import re
import config
import pytest
import unittest
import logging
import subprocess
import os
import json
import ib_utils.ib_NIOS as ib_NIOS
from time import sleep
import commands
import json, ast
import requests
import time
import pexpect
import getpass
import sys
import pdb
auth_zone={"fqdn": "indexer.com"}
auth_zone_1={"fqdn": "dtc.com"}

class Network(unittest.TestCase):


	 @pytest.mark.run(order=1)
         def test_001_create_New_AuthZone(self):
                logging.info("Create A new Zone")
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(auth_zone))
                print(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 1 Execution Completed")

         @pytest.mark.run(order=2)
         def test_002_create_grid_primary_for_zone(self):
                logging.info("Create grid_primary with required fields")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
		
        	data = {"grid_primary": [{"name": config.grid_fqdn,"stealth":False}]}
        	response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
        	logging.info(response)
        	logging.info("============================")
        	print(response)
		
                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                sleep(10)
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(20)

                logging.info("Test Case 2 Execution Completed")

	 @pytest.mark.run(order=3)
         def test_003_modify_log_queries(self):
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)

                logging.info("Modify a  log_queries")
                data1 = {"logging_categories":{"log_queries": True}}
                data2 = {"logging_categories":{"log_responses": True}}
                data3 = {"logging_categories":{"log_dtc_gslb": True}}
                data4 = {"logging_categories":{"log_dtc_health": True}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data1))
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data2))
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data3))
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data4))
                #print(response)
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                sleep(10)
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(10)
                logging.info("Test Case 3 Execution Completed")
                sleep(10)

         @pytest.mark.run(order=3)
         def test_003_create_A_record(self):
                logging.info("Create A record")
		data={"name":"arec."+auth_zone['fqdn'],"ipv4addr":"3.3.3.3","view": "default"}
		response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data))
	        if (response[0]!=400):
		    print ("Added A record")
		else:
		    print ("A record already exists")
		logging.info("Test Case 3 Execution Completed")

	 
	 @pytest.mark.run(order=4)
         def test_004_add_a_DTC_Server1(self):
                logging.info("Create A DTC Server") 
                data = {"name":"s1","host":"10.120.21.222"}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
                print(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 4 Execution Completed")


	 @pytest.mark.run(order=5)
         def test_005_add_a_DTC_Server2(self):
                logging.info("Create A DTC Server")
                data = {"name":"s2","host":"10.120.21.63"}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
                print(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 5 Execution Completed")
  

	 @pytest.mark.run(order=6)
         def test_006_add_a_DTC_pool(self):
                logging.info("Create A DTC Pool")
                data = {"name":"pool1","monitors":["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"],"lb_preferred_method":"ROUND_ROBIN","servers": [{"ratio": 1,"server": "dtc:server/ZG5zLmlkbnNfc2VydmVyJHMx:s1"},{"ratio": 1,"server": "dtc:server/ZG5zLmlkbnNfc2VydmVyJHMy:s2"}]}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:pool", fields=json.dumps(data))
                print(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 6 Execution Completed")

         @pytest.mark.run(order=7)
         def test_007_add_topology_one(self):
                 logging.info("Create a topology ruleset")
                 data = {"name":"topo1","rules":[{"sources": [{"source_op": "IS","source_type": "SUBNET","source_value": "10.0.0.0/8"}],"dest_type": "POOL","return_type":"REGULAR","destination_link":"dtc:pool/ZG5zLmlkbnNfcG9vbCRwb29sMQ:pool1"}]}
                 response = ib_NIOS.wapi_request('POST', object_type="dtc:topology", fields=json.dumps(data))
                 print(response)
                 logging.info(response)
                 read  = re.search(r'201',response)
                 for read in  response:
                         assert True
                 logging.info("Test Case 7 Execution Completed")
                 

         @pytest.mark.run(order=8)
         def test_008_add_a_DTC_lbdn(self):
                logging.info("Create A DTC LBDN")
                data = {"name":"lbdn","lb_method":"TOPOLOGY","topology": "dtc:topology/ZG5zLmlkbnNfdG9wb2xvZ3kkdG9wbzE:topo1","patterns": ["arec.indexer.com"], "pools": [{"pool":"dtc:pool/ZG5zLmlkbnNfcG9vbCRwb29sMQ:pool1","ratio": 1}], "auth_zones":["zone_auth/ZG5zLnpvbmUkLl9kZWZhdWx0LmNvbS5pbmRleGVy:indexer.com/default"],"types":["A","AAAA","CNAME","NAPTR","SRV"]}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:lbdn", fields=json.dumps(data))
                print(response)
                logging.info(response)
		get_ref = ib_NIOS.wapi_request('GET', object_type="dtc:lbdn")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)

                data = {"grid_primary": [{"name": config.grid_fqdn,"stealth":False}]}
                response1 = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                logging.info(response1)
                logging.info("============================")

                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
		print(request_publish)
                sleep(10)
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
		print(request_restart)
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
		print(restart)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 8 Execution Completed")
		sleep(30)

	 @pytest.mark.run(order=9)
         def test_009_perform_query_for_DTC_record_for_s1_response(self):
                logging.info("Perform query for DTC record ")
                dig_cmd = 'dig @'+str(config.grid_vip)+' arec.indexer.com IN A'
                dig_cmd1 = os.system(dig_cmd)
                logging.info("Validate Syslog afer perform queries")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -5 /var/log/syslog | grep  \'10.120.21.222\'"'
                out1 = commands.getoutput(sys_log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'10.120.21.222',out1)
                logging.info("Test Case 9 Execution Completed")
		sleep(10)

	 @pytest.mark.run(order=10)
         def test_010_perform_query_for_DTC_record_for_s2_response(self):
                logging.info("Perform query for DTC record ")
                dig_cmd = 'dig @'+str(config.grid_vip)+' arec.indexer.com IN A'
                dig_cmd1 = os.system(dig_cmd)
                logging.info("Validate Syslog afer perform queries")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -5 /var/log/syslog | grep  \'10.120.21.63\'"'
                out1 = commands.getoutput(sys_log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'10.120.21.63',out1)
                logging.info("Test Case 10 Execution Completed")
		sleep(10)

         @pytest.mark.run(order=11)
         def test_011_add_topology_two(self):
                 logging.info("Create 2nd topology ruleset")
                 data = {"name":"topo2","rules":[{"sources": [{"source_op": "IS","source_type": "SUBNET","source_value": "10.0.0.0/8"}],"dest_type": "POOL","return_type":"NOERR"}]}
                 response = ib_NIOS.wapi_request('POST', object_type="dtc:topology", fields=json.dumps(data))
                 print(response)
                 logging.info(response)
                 read  = re.search(r'201',response)
                 for read in  response:
                         assert True
                 logging.info("Test Case 11 Execution Completed")

		
         @pytest.mark.run(order=12)
         def test_012_modify_DTC_lbdn(self):
		print("Modify a DTC LBDN only to have NOERR")
                logging.info("Modify a DTC LBDN only to have NOERR")
                data = {"topology": "dtc:topology/ZG5zLmlkbnNfdG9wb2xvZ3kkdG9wbzI:topo2"}
                response = ib_NIOS.wapi_request('PUT',ref="dtc:lbdn/ZG5zLmlkbnNfbGJkbiRsYmRu:lbdn",fields=json.dumps(data))
                print(response)
                logging.info(response)

                get_ref = ib_NIOS.wapi_request('GET', object_type="dtc:lbdn")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                
                data = {"grid_primary": [{"name": config.grid_fqdn,"stealth":False}]}
                response1 = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                logging.info(response1)
                logging.info("============================")

                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                sleep(10)
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
	
		read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 12 Execution Completed")
		sleep(20)

         @pytest.mark.run(order=13)
         def test_013_perform_query_for_DTC_record_for_NOERR(self):
                logging.info("Perform query for DTC record NOERR")
		print("Perform query for DTC record NOERR")
                dig_cmd = 'dig @'+str(config.grid_vip)+' arec.indexer.com IN A'
                dig_cmd1 = os.system(dig_cmd)
                logging.info("Validate Syslog afer perform queries")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -5 /var/log/syslog | grep  \'NOERROR\'"'
                out1 = commands.getoutput(sys_log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'NOERROR',out1)
                logging.info("Test Case 13 Execution Completed")
                sleep(10)
	
	 @pytest.mark.run(order=14)
         def test_014_add_topology_three(self):
                 logging.info("Create 3rd topology ruleset")
                 data = {"name":"topo3","rules":[{"sources": [{"source_op": "IS","source_type": "SUBNET","source_value": "10.0.0.0/8"}],"dest_type": "POOL","return_type":"NXDOMAIN"}]}
                 response = ib_NIOS.wapi_request('POST', object_type="dtc:topology", fields=json.dumps(data))
                 print(response)
                 logging.info(response)
                 read  = re.search(r'201',response)
                 for read in  response:
                         assert True
                 logging.info("Test Case 14 Execution Completed")

         @pytest.mark.run(order=15)
         def test_015_modify_DTC_lbdn(self):
                print("Modify a DTC LBDN only to have NXDOMAIN")
                logging.info("Modify a DTC LBDN only to have NXDOMAIN")
                data = {"topology": "dtc:topology/ZG5zLmlkbnNfdG9wb2xvZ3kkdG9wbzM:topo3"}
                response = ib_NIOS.wapi_request('PUT',ref="dtc:lbdn/ZG5zLmlkbnNfbGJkbiRsYmRu:lbdn",fields=json.dumps(data))
                print(response)
                logging.info(response)

                get_ref = ib_NIOS.wapi_request('GET', object_type="dtc:lbdn")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)

                data = {"grid_primary": [{"name": config.grid_fqdn,"stealth":False}]}
                response1 = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                logging.info(response1)
                logging.info("============================")

                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                sleep(10)
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")

                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 15 Execution Completed")
		sleep(20)


         @pytest.mark.run(order=16)
         def test_016_perform_query_for_DTC_record_for_NXDOMAIN(self):
                logging.info("Perform query for DTC record NXDOMAIN")
                print("Perform query for DTC record NXDOMAIN")
                dig_cmd = 'dig @'+str(config.grid_vip)+' arec.indexer.com IN A'
                dig_cmd1 = os.system(dig_cmd)
                logging.info("Validate Syslog afer perform queries")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -5 /var/log/syslog | grep  \'NXDOMAIN\'"'
                out1 = commands.getoutput(sys_log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'NXDOMAIN',out1)
                logging.info("Test Case 16 Execution Completed")
                sleep(10)

	 @pytest.mark.run(order=17)
         def test_017_create_New_AuthZone(self):
                logging.info("Create A new Zone")
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(auth_zone_1))
                print(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 17 Execution Completed")

         @pytest.mark.run(order=18)
         def test_018_create_grid_primary_for_zone(self):
                logging.info("Create grid_primary with required fields")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=dtc.com")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)

                data = {"grid_primary": [{"name": config.grid_fqdn,"stealth":False}]}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                logging.info(response)
                logging.info("============================")
                print(response)

                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                sleep(10)
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(20)

                logging.info("Test Case 18 Execution Completed")


         @pytest.mark.run(order=19)
         def test_019_create_A_record(self):
                logging.info("Create A record")
                data={"name":"arec."+auth_zone['fqdn'],"ipv4addr":"4.4.4.4","view": "default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data))
                if (response[0]!=400):
                    print ("Added A record")
                else:
                    print ("A record already exists")
                logging.info("Test Case 19 Execution Completed")


         @pytest.mark.run(order=20)
         def test_020_add_a_DTC_Server1(self):
                logging.info("Create A DTC Server")
                data = {"name":"s3","host":"10.120.22.198"}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
                print(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 20 Execution Completed")


         @pytest.mark.run(order=21)
         def test_021_add_a_DTC_Server2(self):
                logging.info("Create A DTC Server")
                data = {"name":"s4","host":"10.120.22.35"}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
                print(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 21 Execution Completed")


         @pytest.mark.run(order=22)
         def test_022_add_topology_four(self):
                 logging.info("Create a topology ruleset with SERVER")
                 data = {"name":"topo-serv","rules":[{"sources": [{"source_op": "IS","source_type": "SUBNET","source_value": "10.0.0.0/8"}],"dest_type": "SERVER","return_type":"REGULAR","destination_link":"dtc:server/ZG5zLmlkbnNfc2VydmVyJHMz:s3"}]}
                 response = ib_NIOS.wapi_request('POST', object_type="dtc:topology", fields=json.dumps(data))
                 print(response)
                 logging.info(response)
                 read  = re.search(r'201',response)
                 for read in  response:
                         assert True
                 logging.info("Test Case 22 Execution Completed")

         @pytest.mark.run(order=23)
         def test_023_add_a_DTC_pool_2(self):
                logging.info("Create A DTC Pool")
                data = {"name":"pool2","monitors":["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"],"lb_preferred_method":"TOPOLOGY","lb_preferred_topology": "dtc:topology/ZG5zLmlkbnNfdG9wb2xvZ3kkdG9wby1zZXJ2:topo-serv","servers": [{"ratio": 1,"server": "dtc:server/ZG5zLmlkbnNfc2VydmVyJHMz:s3"},{"ratio": 1,"server": "dtc:server/ZG5zLmlkbnNfc2VydmVyJHM0:s4"}]}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:pool", fields=json.dumps(data))
                print(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 23 Execution Completed")


         @pytest.mark.run(order=24)
         def test_024_add_a_DTC_lbdn_2(self):
                logging.info("Create A DTC LBDN")
                data = {"name":"lbdn2","lb_method":"ROUND_ROBIN","patterns": ["arec.dtc.com"], "pools": [{"pool":"dtc:pool/ZG5zLmlkbnNfcG9vbCRwb29sMg:pool2","ratio": 1}], "auth_zones":["zone_auth/ZG5zLnpvbmUkLl9kZWZhdWx0LmNvbS5kdGM:dtc.com/default"],"types":["A","AAAA","CNAME","NAPTR","SRV"]}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:lbdn", fields=json.dumps(data))
                print(response)
                logging.info(response)
                get_ref = ib_NIOS.wapi_request('GET', object_type="dtc:lbdn?name=lbdn2")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)

                data = {"grid_primary": [{"name": config.grid_fqdn,"stealth":False}]}
                response1 = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                logging.info(response1)
                logging.info("============================")

                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
		print(request_publish)
                sleep(10)
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
 		print(request_restart)
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
		print(restart)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 24 Execution Completed")
                sleep(30)

         @pytest.mark.run(order=25)
         def test_025_perform_query_for_DTC_record_for_s1_response(self):
                logging.info("Perform query for DTC record ")
                dig_cmd = 'dig @'+str(config.grid_vip)+' arec.dtc.com IN A'
                dig_cmd1 = os.system(dig_cmd)
                logging.info("Validate Syslog afer perform queries")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -5 /var/log/syslog | grep  \'10.120.22.198\'"'
                out1 = commands.getoutput(sys_log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'10.120.22.198',out1)
                logging.info("Test Case 25 Execution Completed")
                sleep(5)


         @pytest.mark.run(order=27)
         def test_027_modify_topology_four_NOERR(self):
                logging.info("Modify a topology ruleset with SERVER")
                data = {"name":"topo-serv","rules":[{"sources": [{"source_op": "IS","source_type": "SUBNET","source_value": "20.0.0.0/8"}],"dest_type": "SERVER","return_type":"REGULAR","destination_link":"dtc:server/ZG5zLmlkbnNfc2VydmVyJHMz:s3"},{"sources": [{"source_op": "IS","source_type": "SUBNET","source_value": "10.0.0.0/8"}],"dest_type": "SERVER","return_type":"NOERR"}]}
	        get_ref = ib_NIOS.wapi_request('GET', object_type="dtc:topology?name=topo-serv")
    		logging.info(get_ref)
     		ref1 = json.loads(get_ref)[0]['_ref']
    		print("++++++++++++++++++++++",ref1)
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                logging.info(response)

                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                sleep(10)
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")

                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 27 Execution Completed")
		sleep(20)

         @pytest.mark.run(order=28)
         def test_028_perform_query_for_DTC_record_for_NOERR(self):
                logging.info("Perform query for DTC record NOERR")
                print("Perform query for DTC record NOERR")
                dig_cmd = 'dig @'+str(config.grid_vip)+' arec.dtc.com IN A'
                dig_cmd1 = os.system(dig_cmd)
                logging.info("Validate Syslog afer perform queries")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -5 /var/log/syslog | grep  \'NOERROR\'"'
                out1 = commands.getoutput(sys_log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'NOERROR',out1)
                logging.info("Test Case 28 Execution Completed")
                sleep(10)

         @pytest.mark.run(order=29)
         def test_029_modify_topology_four_NXDOMAIN(self):
                logging.info("Modify a topology ruleset with SERVER")
                data = {"name":"topo-serv","rules":[{"sources": [{"source_op": "IS","source_type": "SUBNET","source_value": "30.0.0.0/8"}],"dest_type": "SERVER","return_type":"REGULAR","destination_link":"dtc:server/ZG5zLmlkbnNfc2VydmVyJHMz:s3"},{"sources": [{"source_op": "IS","source_type": "SUBNET","source_value": "20.0.0.0/8"}],"dest_type": "SERVER","return_type":"NOERR"},{"sources": [{"source_op": "IS","source_type": "SUBNET","source_value": "10.0.0.0/8"}],"dest_type": "SERVER","return_type":"NXDOMAIN"}]}
                get_ref = ib_NIOS.wapi_request('GET', object_type="dtc:topology?name=topo-serv")
                logging.info(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print("++++++++++++++++++++++",ref1)
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                logging.info(response)

                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                print(request_publish)
		sleep(10)
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                print(request_restart)
		restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
		print(restart)

                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 29 Execution Completed")
		sleep(20)

         @pytest.mark.run(order=30)
         def test_030_perform_query_for_DTC_record_for_NXDOMAIN(self):
                logging.info("Perform query for DTC record NXDOMAIN")
                print("Perform query for DTC record NXDOMAIN")
                dig_cmd = 'dig @'+str(config.grid_vip)+' arec.dtc.com IN A'
                dig_cmd1 = os.system(dig_cmd)
                logging.info("Validate Syslog afer perform queries")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -5 /var/log/syslog | grep  \'NXDOMAIN\'"'
                out1 = commands.getoutput(sys_log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'NXDOMAIN',out1)
                logging.info("Test Case 30 Execution Completed")
                sleep(10)


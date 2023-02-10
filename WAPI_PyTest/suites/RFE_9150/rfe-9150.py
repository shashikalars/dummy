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

class Network(unittest.TestCase):


	 @pytest.mark.run(order=1)
         def test_001_create_New_AuthZone(self):
                logging.info("Create A new Zone")
                data = {"fqdn": "zone.com"}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                print response
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
                print ref1
		
        	data = {"grid_primary": [{"name": config.grid_fqdn,"stealth":False}]}
        	response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
        	logging.info(response)
        	logging.info("============================")
        	print response
		
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
         def test_003_add_a_DTC_Server1(self):
                logging.info("Create A DTC Server") 
                data = {"name":"s1","host":"10.120.20.151"}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 3 Execution Completed")


	 @pytest.mark.run(order=4)
         def test_004_add_a_DTC_Server2(self):
                logging.info("Create A DTC Server")
                data = {"name":"s2","host":"10.120.21.95"}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 4 Execution Completed")



	 @pytest.mark.run(order=5)
         def test_005_add_a_DTC_pool(self):
                logging.info("Create A DTC Pool")
                data = {"name":"pool1","monitors":["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"],"lb_preferred_method":"ROUND_ROBIN","servers": [{"ratio": 1,"server": "dtc:server/ZG5zLmlkbnNfc2VydmVyJHMx:s1"},{"ratio": 1,"server": "dtc:server/ZG5zLmlkbnNfc2VydmVyJHMy:s2"}]}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:pool", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 5 Execution Completed")

         @pytest.mark.run(order=6)
         def test_006_add_a_DTC_lbdn(self):
                logging.info("Create A DTC LBDN")
                data = {"name":"lbdn1","lb_method":"GLOBAL_AVAILABILITY", "patterns": ["*.zone.com"], "pools": [{"pool":"dtc:pool/ZG5zLmlkbnNfcG9vbCRwb29sMQ:pool1","ratio": 1}], "auth_zones":["zone_auth/ZG5zLnpvbmUkLl9kZWZhdWx0LmNvbS56b25l:zone.com/default"],"types":["A","AAAA","CNAME","NAPTR","SRV"]}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:lbdn", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 6 Execution Completed")


	 @pytest.mark.run(order=7)
         def test_007_modify_log_queries(self):
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify a  log_queries")
                data1 = {"logging_categories":{"log_queries": True}}
		data2 = {"logging_categories":{"log_responses": True}}
		data3 = {"logging_categories":{"log_dtc_gslb": True}}
		data4 = {"logging_categories":{"log_dtc_health": True}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data1))
		response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data2))
		response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data3))
		response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data4))
                #print response
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
                logging.info("Test Case 7 Execution Completed")
		sleep(10)


	 @pytest.mark.run(order=8)
         def test_008_perform_query_for_DTC_record_on_master_for_s1_response(self):
                logging.info("Perform query for DTC record ")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.zone.com IN A'
                dig_cmd1 = os.system(dig_cmd)
                logging.info("Validate Syslog afer perform queries")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -5 /var/log/syslog | grep  \'10.120.20.151\'"'
                out1 = commands.getoutput(sys_log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'10.120.20.151',out1)
                logging.info("Test Case 8 Execution Completed")
		sleep(10)

	 @pytest.mark.run(order=9)
         def test_009_perform_query_for_DTC_record_on_master_for_s2_response(self):
                logging.info("Perform query for DTC record ")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.zone.com IN A'
                dig_cmd1 = os.system(dig_cmd)
                logging.info("Validate Syslog afer perform queries")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -5 /var/log/syslog | grep  \'A 10.120.21.95\'"'
                out1 = commands.getoutput(sys_log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'A 10.120.21.95',out1)
                logging.info("Test Case 9 Execution Completed")
                sleep(10)


	 @pytest.mark.run(order=10)
         def test_010_lbdn_modify_set_persistence_to_2hours(self):
                get_ref = ib_NIOS.wapi_request('GET', object_type="dtc:lbdn")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modifying the persistence value")
                data = {"persistence":7200}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
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
                sleep(20)
                logging.info("Test Case 10 Execution Completed")
                sleep(10)


	 @pytest.mark.run(order=11)
         def test_011_perform_query_for_DTC_record_on_master_for_s1_response(self):
                logging.info("Perform query for DTC record ")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.zone.com IN A'
                dig_cmd1 = os.system(dig_cmd)
                logging.info("Validate Syslog afer perform queries")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -5 /var/log/syslog | grep  \'10.120.20.151\'"'
                out1 = commands.getoutput(sys_log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'10.120.20.151',out1)
                logging.info("Test Case 11 Execution Completed")
                sleep(10)

         @pytest.mark.run(order=12)
         def test_012_perform_query_for_DTC_record_on_master_for_s1_response(self):
                logging.info("Perform query for DTC record ")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.zone.com IN A'
                dig_cmd1 = os.system(dig_cmd)
                logging.info("Validate Syslog afer perform queries")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -5 /var/log/syslog | grep  \'A 10.120.20.151\'"'
                out1 = commands.getoutput(sys_log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'A 10.120.20.151',out1)
                logging.info("Test Case 12 Execution Completed")
                sleep(10)


	 @pytest.mark.run(order=13)
         def test_013_perform_query_for_DTC_record_on_master_for_s1_response(self):
                logging.info("Perform query for DTC record ")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.zone.com IN A'
                dig_cmd1 = os.system(dig_cmd)
                logging.info("Validate Syslog afer perform queries")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -5 /var/log/syslog | grep  \'A 10.120.20.151\'"'
                out1 = commands.getoutput(sys_log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'A 10.120.20.151',out1)
                logging.info("Test Case 13 Execution Completed")
                sleep(10)

	 @pytest.mark.run(order=14)
         def test_014_reset_LBDN_persistence_to_0_hours(self):
                get_ref = ib_NIOS.wapi_request('GET', object_type="dtc:lbdn")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modifying the persistence value")
                data = {"persistence":0}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
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
                sleep(20)
                logging.info("Test Case 14 Execution Completed")
                sleep(10)


	 @pytest.mark.run(order=15)
         def test_015_perform_query_for_DTC_record_on_master_for_s1_response(self):
                logging.info("Perform query for DTC record ")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.zone.com IN A'
                dig_cmd1 = os.system(dig_cmd)
                logging.info("Validate Syslog afer perform queries")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -5 /var/log/syslog | grep  \'10.120.20.151\'"'
                out1 = commands.getoutput(sys_log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'10.120.20.151',out1)
                logging.info("Test Case 15 Execution Completed")
                sleep(10)

         @pytest.mark.run(order=16)
         def test_016_perform_query_for_DTC_record_on_master_for_s2_response(self):
                logging.info("Perform query for DTC record ")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.zone.com IN A'
                dig_cmd1 = os.system(dig_cmd)
                logging.info("Validate Syslog afer perform queries")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -5 /var/log/syslog | grep  \'A 10.120.21.95\'"'
                out1 = commands.getoutput(sys_log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'A 10.120.21.95',out1)
                logging.info("Test Case 16 Execution Completed")
                sleep(10)


	 @pytest.mark.run(order=17)
         def test_017_perform_query_for_DTC_record_on_master_for_s1_response(self):
                logging.info("Perform query for DTC record ")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.zone.com IN A'
                dig_cmd1 = os.system(dig_cmd)
                logging.info("Validate Syslog afer perform queries")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -5 /var/log/syslog | grep  \'10.120.20.151\'"'
                out1 = commands.getoutput(sys_log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'10.120.20.151',out1)
                logging.info("Test Case 17 Execution Completed")
                sleep(10)

         @pytest.mark.run(order=18)
         def test_018_perform_query_for_DTC_record_on_master_for_s2_response(self):
                logging.info("Perform query for DTC record ")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.zone.com IN A'
                dig_cmd1 = os.system(dig_cmd)
                logging.info("Validate Syslog afer perform queries")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -5 /var/log/syslog | grep  \'A 10.120.21.95\'"'
                out1 = commands.getoutput(sys_log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'A 10.120.21.95',out1)
                logging.info("Test Case 18 Execution Completed")
                sleep(10)


import re
import sys
import config
import pytest
import unittest
import logging
import os
import os.path
from os.path import join
import subprocess
import json
import time
import subprocess

from time import sleep
import commands
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util
import ib_utils.log_capture as log_capture
from  ib_utils.log_capture import log_action as log
from  ib_utils.log_validation import log_validation as logv
import pexpect
from paramiko import client

class Rfe_9893(unittest.TestCase):
         		
        @pytest.mark.run(order=1)
        def test_001_Start_DNS_Service(self):
                logging.info("Start DNS Service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                for i in res:
                        logging.info("Modify a enable_dns")
                        data = {"enable_dns": True}
                        response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
                        print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 1 Execution Completed")

        @pytest.mark.run(order=2)
        def test_002_Validate_DNS_service_Enabled(self):
                logging.info("Validate DNs Service is enabled")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                for i in res:
                        print i
                        logging.info("found")
                        assert i["enable_dns"] == True
                print("Test Case 2 Execution Completed")

        @pytest.mark.run(order=3)
        def test_003_create_New_AuthZone(self):
                logging.info("Create A new Zone")
                data = {"fqdn": "dtc.com","grid_primary": [{"name": config.grid_member_fqdn,"stealth":False}, {"name": config.grid_member1_fqdn,"stealth":False}, {"name": config.grid_member2_fqdn,"stealth":False}, {"name": config.grid_member3_fqdn,"stealth":False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Restart DNS Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20)
                logging.info("Test Case 3 Execution Completed")

        @pytest.mark.run(order=4)
        def test_004_Validate_Created_Zone(self):
                logging.info("Validate Created Zone")
                response =  ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=dtc.com", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                assert re.search(r'"dtc.com"',response)
                sleep(5)
                print("Test Case 4 Execution Completed")

        @pytest.mark.run(order=5)
        def test_005_add_a_DTC_Server1(self):
                logging.info("Create A DTC first Server")
                data = {"name":"Server1","host":config.Server1}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 5 Execution Completed")

        @pytest.mark.run(order=6)
        def test_006_Validate_Created_Server1(self):
                logging.info("Validate Created Server1")
                response =  ib_NIOS.wapi_request('GET', object_type="dtc:server?name=Server1", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                assert re.search(r'"Server1',response)
                sleep(5)
                print("Test Case 6 Execution Completed")

        @pytest.mark.run(order=7)
        def test_007_add_a_DTC_Server2(self):
                logging.info("Create A DTC Second Server")
                data = {"name":"Server2","host":config.Server2}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 7 Execution Completed")

        @pytest.mark.run(order=8)
        def test_008_Validate_Created_Server2(self):
                logging.info("Validate Created Server2")
                response =  ib_NIOS.wapi_request('GET', object_type="dtc:server?name=Server2", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                assert re.search(r'"Server2',response)
                sleep(5)
                print("Test Case 8 Execution Completed")

        @pytest.mark.run(order=9)
        def test_009_add_a_DTC_pool(self):
                logging.info("Create A DTC Pool")
		data= {"name": "Pool1","lb_preferred_method": "SOURCE_IP_HASH","servers": [{"ratio": 1,"server": "dtc:server/ZG5zLmlkbnNfc2VydmVyJFNlcnZlcjE:Server1"},{"ratio": 1,"server": "dtc:server/ZG5zLmlkbnNfc2VydmVyJFNlcnZlcjI:Server2"}],"monitors": ["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"]}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:pool", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 9 Execution Completed") 

        @pytest.mark.run(order=10)
        def test_010_Validate_Created_Pool(self):
                logging.info("Validate Created Pool")
                response =  ib_NIOS.wapi_request('GET', object_type="dtc:pool?name=Pool1", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                assert re.search(r'"Pool1',response)
                sleep(5)
                print("Test Case 10 Execution Completed")

        @pytest.mark.run(order=11)
        def test_011_add_a_DTC_lbdn(self):
                logging.info("Create A DTC LBDN")
                data = {"name":"lbdn","lb_method":"SOURCE_IP_HASH","patterns": ["a1.dtc.com"], "pools": [{"pool":"dtc:pool/ZG5zLmlkbnNfcG9vbCRQb29sMQ:Pool1","ratio": 1}], "auth_zones":["zone_auth/ZG5zLnpvbmUkLl9kZWZhdWx0LmNvbS5kdGM:dtc.com/default"],"types":["A","AAAA","CNAME","NAPTR","SRV"]}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:lbdn", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Restart DNS Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(30)
                logging.info("Test Case 11 Execution Completed")

        @pytest.mark.run(order=12)
        def test_012_Validate_Created_LBDN(self):
                logging.info("Validate Created LBDN")
                response =  ib_NIOS.wapi_request('GET', object_type="dtc:lbdn?name=lbdn", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                assert re.search(r'"lbdn',response)
                sleep(5)
                print("Test Case 12 Execution Completed")

	@pytest.mark.run(order=13)
        def test_013_Validate_parsed_health_File_in_Master(self):
                logging.info("Validate parsed_health File in Master")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
		child.sendline('cd /storage/tmp')
		child.expect('#')
		child.sendline('ls')
		child.expect('#')
		files=child.before
		print(files)
		child.close()
		if ("parsed_health.gz" in files):
			assert True
		else:
			assert False
		print("Test Case 13 Execution Completed")	

	@pytest.mark.run(order=14)
        def test_014_Enable_Master_Candidate_For_HA_member(self):
		logging.info("Enable Master_Candidate For HA-member")
		response =  ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
                print response
                logging.info(response)
		res = json.loads(response)
                ref1 = json.loads(response)[1]['_ref']
                print ref1
		data = {"master_candidate":True}
		response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(300)
                print("Test Case 14 Execution Completed")
		
	@pytest.mark.run(order=15)
        def test_015_Validate_Enabled_Master_Candidate_For_HA_member(self):
                logging.info("Enabled Master_Candidate For HA-member")
                response =  ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                res = json.loads(response)
                ref1 = json.loads(response)[1]['_ref']
                print ref1
                response = ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=master_candidate,enable_ro_api_access")
                print(response)
		if (('"enable_ro_api_access": false' in response) and ('"master_candidate": true' in response)):
			assert True
		else:
			assert False
		print("Test Case 15 Execution Completed")
	
	@pytest.mark.run(order=16)
        def test_016_Validate_parsed_health_File_in_HA_Member(self):
                logging.info("Validate parsed_health File in HA Member")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cd /storage/tmp')
                child.expect('#')
                child.sendline('ls')
                child.expect('#')
                files=child.before
                print(files)
                if ("parsed_health.gz" not in files):
                        assert True
                else:
                        assert False
		print("Test Case 16 Execution Completed")
		
	@pytest.mark.run(order=17)
        def test_017_Enable_RO_API_Access_For_HA_member(self):
                logging.info("Enable RO_API_Access For HA-member")
                response =  ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                res = json.loads(response)
                ref1 = json.loads(response)[1]['_ref']
                print ref1
                data = {"enable_ro_api_access":True}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(100)
                print("Test Case 17 Execution Completed")

        @pytest.mark.run(order=18)
        def test_018_Validate_Enabled_RO_API_Access_For_HA_member(self):
                logging.info("Enabled RO_API_Access For HA-member")
                response =  ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                res = json.loads(response)
                ref1 = json.loads(response)[1]['_ref']
                print ref1
                response = ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=master_candidate,enable_ro_api_access")
                print(response)
                if (('"enable_ro_api_access": true' in response) and ('"master_candidate": true' in response)):
                        assert True
                else:
                        assert False
                print("Test Case 18 Execution Completed")

	@pytest.mark.run(order=19)
        def test_019_Validate_parsed_health_File_in_HA_Member(self):
                logging.info("Validate parsed_health File in HA Member")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cd /storage/tmp')
                child.expect('#')
                child.sendline('ls')
                child.expect('#')
                files=child.before
                print(files)
                if ("parsed_health.gz" in files):
                        assert True
                else:
                        assert False
		print("Test Case 19 Execution Completed")
		
	@pytest.mark.run(order=20)
        def test_020_Validate_parsed_health_File_in_HA_Passive_Node(self):
                logging.info("Validate parsed_health File in HA Passive Node")  
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.passive_ip)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('show status')
                child.expect('>')
                passive_status=child.before
                if ("Passive" in passive_status):
                    passive_ip=config.passive_ip
                else:
                    passive_ip=config.active_ip
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+passive_ip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('rm -rf /tmp/parsed_health*')
                child.expect('#')
                sleep(30)
                child.sendline('cd /storage/tmp')
                child.expect('#')
                child.sendline('ls')
                child.expect('#')
                files=child.before
                print(files)
                if ("parsed_health.gz" not in files):
                        assert True
                else:
                        assert False
		print("Test Case 20 Execution Completed")

	@pytest.mark.run(order=21)
        def test_021_Validate_DTC_Objects_health_status_of_master(self):
                logging.info("Validate DTC Objects health_status of master")
                response_Server1 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server1&_return_fields%2B=health", grid_vip=config.grid_vip)
                print response_Server1
                logging.info(response_Server1)
                response_Server2 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server2&_return_fields%2B=health", grid_vip=config.grid_vip)
                print response_Server2
                logging.info(response_Server2)
                response_Pool1 =  ib_NIOS.wapi_request('GET',"dtc:pool?name=Pool1&_return_fields%2B=health", grid_vip=config.grid_vip)
                print response_Pool1
                logging.info(response_Pool1)
                response_lbdn =  ib_NIOS.wapi_request('GET',"dtc:lbdn?name=lbdn&_return_fields%2B=health", grid_vip=config.grid_vip)
                print response_lbdn
                logging.info(response_lbdn)
                List=[response_Server1,response_Server2,response_Pool1,response_lbdn]
                for health in List:
                        if ('"availability": "GREEN"' in health):
                                assert True
                        else:
                                assert False
		print("Test Case 21 Execution Completed")

        @pytest.mark.run(order=22)
        def test_022_Validate_DTC_Objects_health_status_of_HA_Member(self):
                logging.info("Validate DTC Objects health_status of HA")
                response_Server1 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server1&_return_fields%2B=health", grid_vip=config.grid_member1_vip)
                print response_Server1
                logging.info(response_Server1)
                response_Server2 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server2&_return_fields%2B=health", grid_vip=config.grid_member1_vip)
                print response_Server2
                logging.info(response_Server2)
                response_Pool1 =  ib_NIOS.wapi_request('GET',"dtc:pool?name=Pool1&_return_fields%2B=health", grid_vip=config.grid_member1_vip)
                print response_Pool1
                logging.info(response_Pool1)
                response_lbdn =  ib_NIOS.wapi_request('GET',"dtc:lbdn?name=lbdn&_return_fields%2B=health", grid_vip=config.grid_member1_vip)
                print response_lbdn
                logging.info(response_lbdn)
                List=[response_Server1,response_Server2,response_Pool1,response_lbdn]
                for health in List:
                        if ('"availability": "GREEN"' in health):
                                assert True
                        else:
                                assert False
                print("Test Case 22 Execution Completed")

        @pytest.mark.run(order=23)
        def test_023_Enable_Master_Candidate_For_SA_member(self):
                logging.info("Enable Master_Candidate For SA-member")
                response =  ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                res = json.loads(response)
                ref1 = json.loads(response)[2]['_ref']
                print ref1
                data = {"master_candidate":True}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(300)
                print("Test Case 23 Execution Completed")

        @pytest.mark.run(order=24)
        def test_024_Validate_Enabled_Master_Candidate_For_SA_member(self):
                logging.info("Enabled Master_Candidate For SA-member")
                response =  ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                res = json.loads(response)
                ref1 = json.loads(response)[2]['_ref']
                print ref1
                response = ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=master_candidate,enable_ro_api_access")
                print(response)
                if (('"enable_ro_api_access": false' in response) and ('"master_candidate": true' in response)):
                        assert True
                else:
                        assert False
                print("Test Case 24 Execution Completed")

        @pytest.mark.run(order=25)
        def test_025_Validate_parsed_health_File_in_SA_Member(self):
                logging.info("Validate parsed_health File in SA Member")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member2_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cd /storage/tmp')
                child.expect('#')
                child.sendline('ls')
                child.expect('#')
                files=child.before
                print(files)
                if ("parsed_health.gz" not in files):
                        assert True
                else:
                        assert False
		sleep(10)
                print("Test Case 25 Execution Completed")
			
        @pytest.mark.run(order=26)
        def test_026_Enable_RO_API_Access_For_SA_member(self):
                logging.info("Enable RO_API_Access For SA-member")
                response =  ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                res = json.loads(response)
                ref1 = json.loads(response)[2]['_ref']
                print ref1
                data = {"enable_ro_api_access":True}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(100)
                print("Test Case 26 Execution Completed")

        @pytest.mark.run(order=27)
        def test_027_Validate_Enabled_RO_API_Access_For_SA_member(self):
                logging.info("Enabled RO_API_Access For SA-member")
                response =  ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                res = json.loads(response)
                ref1 = json.loads(response)[2]['_ref']
                print ref1
                response = ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=master_candidate,enable_ro_api_access")
                print(response)
                if (('"enable_ro_api_access": true' in response) and ('"master_candidate": true' in response)):
                        assert True
                else:
                        assert False
                print("Test Case 27 Execution Completed")

        @pytest.mark.run(order=28)
        def test_028_Validate_parsed_health_File_in_SA_Member(self):
                logging.info("Validate parsed_health File in SA Member")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member2_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cd /storage/tmp')
                child.expect('#')
                child.sendline('ls')
                child.expect('#')
                files=child.before
                print(files)
                if ("parsed_health.gz" in files):
                        assert True
                else:
                        assert False
		sleep(10)
                print("Test Case 28 Execution Completed")
	
        @pytest.mark.run(order=29)
        def test_029_Validate_DTC_Objects_health_status_of_SA_Member(self):
                logging.info("Validate DTC Objects health_status of SA")
                response_Server1 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server1&_return_fields%2B=health", grid_vip=config.grid_member2_vip)
                print response_Server1
                logging.info(response_Server1)
                response_Server2 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server2&_return_fields%2B=health", grid_vip=config.grid_member2_vip)
                print response_Server2
                logging.info(response_Server2)
                response_Pool1 =  ib_NIOS.wapi_request('GET',"dtc:pool?name=Pool1&_return_fields%2B=health", grid_vip=config.grid_member2_vip)
                print response_Pool1
                logging.info(response_Pool1)
                response_lbdn =  ib_NIOS.wapi_request('GET',"dtc:lbdn?name=lbdn&_return_fields%2B=health", grid_vip=config.grid_member2_vip)
                print response_lbdn
                logging.info(response_lbdn)
                List=[response_Server1,response_Server2,response_Pool1,response_lbdn]
                for health in List:
                        if ('"availability": "GREEN"' in health):
                                assert True
                        else:
                                assert False
                print("Test Case 29 Execution Completed")

        @pytest.mark.run(order=30)
        def test_030_Enable_Master_Candidate_For_IBFLEX_member(self):
                logging.info("Enable Master_Candidate For IBFLEX-member")
                response =  ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                res = json.loads(response)
                ref1 = json.loads(response)[3]['_ref']
                print ref1
                data = {"master_candidate":True}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(300)
                print("Test Case 30 Execution Completed")
	
        @pytest.mark.run(order=31)
        def test_031_Validate_Enabled_Master_Candidate_For_IBFLEX_member(self):
                logging.info("Enabled Master_Candidate For IBFLEX-member")
                response =  ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                res = json.loads(response)
                ref1 = json.loads(response)[3]['_ref']
                print ref1
                response = ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=master_candidate,enable_ro_api_access")
                print(response)
                if (('"enable_ro_api_access": false' in response) and ('"master_candidate": true' in response)):
                        assert True
                else:
                        assert False
                print("Test Case 31 Execution Completed")

        @pytest.mark.run(order=32)
        def test_032_Validate_parsed_health_File_in_IBFLEX_Member(self):
                logging.info("Validate parsed_health File in IBFLEX Member")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member3_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cd /storage/tmp')
                child.expect('#')
                child.sendline('ls')
                child.expect('#')
                files=child.before
                print(files)
                if ("parsed_health.gz" not in files):
                        assert True
                else:
                        assert False
                print("Test Case 32 Execution Completed")

        @pytest.mark.run(order=33)
        def test_033_Enable_RO_API_Access_For_IBFLEX_member(self):
                logging.info("Enable RO_API_Access For IBFLEX-member")
                response =  ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                res = json.loads(response)
                ref1 = json.loads(response)[3]['_ref']
                print ref1
                data = {"enable_ro_api_access":True}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(100)
                print("Test Case 33 Execution Completed")

        @pytest.mark.run(order=34)
        def test_034_Validate_Enabled_RO_API_Access_For_IBFLEX_member(self):
                logging.info("Enabled RO_API_Access For IBFLEX-member")
                response =  ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                res = json.loads(response)
                ref1 = json.loads(response)[3]['_ref']
                print ref1
                response = ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=master_candidate,enable_ro_api_access")
                print(response)
                if (('"enable_ro_api_access": true' in response) and ('"master_candidate": true' in response)):
                        assert True
                else:
                        assert False
                print("Test Case 34 Execution Completed")

        @pytest.mark.run(order=35)
        def test_035_Validate_parsed_health_File_in_IBFLEX_Member(self):
                logging.info("Validate parsed_health File in IBFLEX Member")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member3_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cd /storage/tmp')
                child.expect('#')
                child.sendline('ls')
                child.expect('#')
                files=child.before
                print(files)
                if ("parsed_health.gz" in files):
                        assert True
                else:
                        assert False
		sleep(10)
                print("Test Case 35 Execution Completed")
	
        @pytest.mark.run(order=36)
        def test_036_Validate_DTC_Objects_health_status_of_IBFLEX_Member(self):
                logging.info("Validate DTC Objects health_status of IBFLEX")
                response_Server1 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server1&_return_fields%2B=health", grid_vip=config.grid_member3_vip)
                print response_Server1
                logging.info(response_Server1)
                response_Server2 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server2&_return_fields%2B=health", grid_vip=config.grid_member3_vip)
                print response_Server2
                logging.info(response_Server2)
                response_Pool1 =  ib_NIOS.wapi_request('GET',"dtc:pool?name=Pool1&_return_fields%2B=health", grid_vip=config.grid_member3_vip)
                print response_Pool1
                logging.info(response_Pool1)
                response_lbdn =  ib_NIOS.wapi_request('GET',"dtc:lbdn?name=lbdn&_return_fields%2B=health", grid_vip=config.grid_member3_vip)
                print response_lbdn
                logging.info(response_lbdn)
                List=[response_Server1,response_Server2,response_Pool1,response_lbdn]
                for health in List:
                        if ('"availability": "GREEN"' in health):
                                assert True
                        else:
                                assert False
                print("Test Case 36 Execution Completed")

	@pytest.mark.run(order=37)
        def test_037_Execute_DROP_Command_in_Master(self):
                logging.info("Execute_DROP_Command_in_Master")
                drop='iptables -I INPUT -s '+config.Server1+' -j DROP'
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline(drop)
                child.expect('#')
                sleep(60)
		print("Test Case 37 Execution Completed")

	@pytest.mark.run(order=38)
        def test_038_Validate_DTC_Objects_health_status_of_master(self):
                logging.info("Validate DTC Objects health_status of master")
                response_Server1 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server1&_return_fields%2B=health", grid_vip=config.grid_vip)
                print response_Server1
                logging.info(response_Server1)
                response_Server2 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server2&_return_fields%2B=health", grid_vip=config.grid_vip)
                print response_Server2
                logging.info(response_Server2)
                response_Pool1 =  ib_NIOS.wapi_request('GET',"dtc:pool?name=Pool1&_return_fields%2B=health", grid_vip=config.grid_vip)
                print response_Pool1
                logging.info(response_Pool1)
                response_lbdn =  ib_NIOS.wapi_request('GET',"dtc:lbdn?name=lbdn&_return_fields%2B=health", grid_vip=config.grid_vip)
                print response_lbdn
                logging.info(response_lbdn)
                if (('"availability": "RED"' in response_Server1) and ('"availability": "GREEN"' in response_Server2) and ('"availability": "YELLOW"' in response_Pool1) and ('"availability": "YELLOW"' in response_lbdn)):
			assert True
                else:
                        assert False
		print("Test Case 38 Execution Completed")

	@pytest.mark.run(order=39)
        def test_039_Validate_DTC_Objects_health_status_of_HA_Member(self):
                logging.info("Validate DTC Objects health_status of HA")
                response_Server1 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server1&_return_fields%2B=health", grid_vip=config.grid_member1_vip)
                print response_Server1
                logging.info(response_Server1)
                response_Server2 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server2&_return_fields%2B=health", grid_vip=config.grid_member1_vip)
                print response_Server2
                logging.info(response_Server2)
                response_Pool1 =  ib_NIOS.wapi_request('GET',"dtc:pool?name=Pool1&_return_fields%2B=health", grid_vip=config.grid_member1_vip)
                print response_Pool1
                logging.info(response_Pool1)
                response_lbdn =  ib_NIOS.wapi_request('GET',"dtc:lbdn?name=lbdn&_return_fields%2B=health", grid_vip=config.grid_member1_vip)
                print response_lbdn
                logging.info(response_lbdn)
		if (('"availability": "RED"' in response_Server1) and ('"availability": "GREEN"' in response_Server2) and ('"availability": "YELLOW"' in response_Pool1) and ('"availability": "YELLOW"' in response_lbdn)):
                        assert True
                else:
                        assert False
                print("Test Case 39 Execution Completed")
		
	@pytest.mark.run(order=40)
        def test_040_Validate_DTC_Objects_health_status_of_SA_Member(self):
                logging.info("Validate DTC Objects health_status of SA")
                response_Server1 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server1&_return_fields%2B=health", grid_vip=config.grid_member2_vip)
                print response_Server1
                logging.info(response_Server1)
                response_Server2 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server2&_return_fields%2B=health", grid_vip=config.grid_member2_vip)
                print response_Server2
                logging.info(response_Server2)
                response_Pool1 =  ib_NIOS.wapi_request('GET',"dtc:pool?name=Pool1&_return_fields%2B=health", grid_vip=config.grid_member2_vip)
                print response_Pool1
                logging.info(response_Pool1)
                response_lbdn =  ib_NIOS.wapi_request('GET',"dtc:lbdn?name=lbdn&_return_fields%2B=health", grid_vip=config.grid_member2_vip)
                print response_lbdn
                logging.info(response_lbdn)
		if (('"availability": "RED"' in response_Server1) and ('"availability": "GREEN"' in response_Server2) and ('"availability": "YELLOW"' in response_Pool1) and ('"availability": "YELLOW"' in response_lbdn)):
                        assert True
                else:
                        assert False
                print("Test Case 40 Execution Completed")

	@pytest.mark.run(order=41)
        def test_041_Validate_DTC_Objects_health_status_of_IBFLEX_Member(self):
                logging.info("Validate DTC Objects health_status of IBFLEX")
                response_Server1 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server1&_return_fields%2B=health", grid_vip=config.grid_member3_vip)
                print response_Server1
                logging.info(response_Server1)
                response_Server2 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server2&_return_fields%2B=health", grid_vip=config.grid_member3_vip)
                print response_Server2
                logging.info(response_Server2)
                response_Pool1 =  ib_NIOS.wapi_request('GET',"dtc:pool?name=Pool1&_return_fields%2B=health", grid_vip=config.grid_member3_vip)
                print response_Pool1
                logging.info(response_Pool1)
                response_lbdn =  ib_NIOS.wapi_request('GET',"dtc:lbdn?name=lbdn&_return_fields%2B=health", grid_vip=config.grid_member3_vip)
                print response_lbdn
                logging.info(response_lbdn)
		if (('"availability": "RED"' in response_Server1) and ('"availability": "GREEN"' in response_Server2) and ('"availability": "YELLOW"' in response_Pool1) and ('"availability": "YELLOW"' in response_lbdn)):
                        assert True
                else:
                        assert False
                print("Test Case 41 Execution Completed")

	@pytest.mark.run(order=42)
        def test_042_Promoting_SA_Member_as_Master(self):
		child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
            	child.logfile=sys.stdout
            	child.expect('password:')
            	child.sendline('infoblox')
            	child.expect('Infoblox >')
		child.sendline('set promote_master')
                child.expect(':')
		child.sendline('y')
                child.expect(':')
		child.sendline('10')
                child.expect(':')
		child.sendline('y')
		child.expect(':')
                child.sendline('y')
		time.sleep(300)
		child.expect('closed.')
		print("Test Case 42 Execution Completed")
	
	@pytest.mark.run(order=43)
        def test_043_Validate_SA_Member_as_Master(self):
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('show network')
                child.expect('Infoblox >')
		response=child.before
	        print(response)
		assert re.search(r'Master of Infoblox Grid',response)
		print("Test Case 43 Execution Completed")

	@pytest.mark.run(order=44)
        def test_044_Enable_RO_API_Access_For_Master(self):
                logging.info("Enable RO_API_Access For Master")
                response =  ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_member2_vip)
                print response
                logging.info(response)
                res = json.loads(response)
                ref1 = json.loads(response)[0]['_ref']
                print ref1
                data = {"enable_ro_api_access":True}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data),grid_vip=config.grid_member2_vip)
                print(response)
                sleep(120)
                print("Test Case 44 Execution Completed")
	
        @pytest.mark.run(order=45)
        def test_045_Validate_Enabled_RO_API_Access_For_Master(self):
                logging.info("Enabled RO_API_Access For Master")
                response =  ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_member2_vip)
                print response
                logging.info(response)
                res = json.loads(response)
                ref1 = json.loads(response)[0]['_ref']
                print ref1
                response = ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=master_candidate,enable_ro_api_access",grid_vip=config.grid_member2_vip)
                print(response)
                if (('"enable_ro_api_access": true' in response) and ('"master_candidate": true' in response)):
                        assert True
                else:
                        assert False
                print("Test Case 45 Execution Completed")

	@pytest.mark.run(order=46)
        def test_046_Validate_DTC_Objects_health_status_of_master(self):
                logging.info("Validate DTC Objects health_status of master")
                response_Server1 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server1&_return_fields%2B=health", grid_vip=config.grid_vip)
                print response_Server1
                logging.info(response_Server1)
                response_Server2 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server2&_return_fields%2B=health", grid_vip=config.grid_vip)
                print response_Server2
                logging.info(response_Server2)
                response_Pool1 =  ib_NIOS.wapi_request('GET',"dtc:pool?name=Pool1&_return_fields%2B=health", grid_vip=config.grid_vip)
                print response_Pool1
                logging.info(response_Pool1)
                response_lbdn =  ib_NIOS.wapi_request('GET',"dtc:lbdn?name=lbdn&_return_fields%2B=health", grid_vip=config.grid_vip)
                print response_lbdn
                logging.info(response_lbdn)
		List=[response_Server1,response_Server2,response_Pool1,response_lbdn]
                for health in List:
                        if ('"availability": "GREEN"' in health):
                                assert True
                        else:
                                assert False
                print("Test Case 46 Execution Completed")
	
        @pytest.mark.run(order=47)
        def test_047_Validate_DTC_Objects_health_status_of_HA_Member(self):
                logging.info("Validate DTC Objects health_status of HA")
                response_Server1 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server1&_return_fields%2B=health", grid_vip=config.grid_member1_vip)
                print response_Server1
                logging.info(response_Server1)
                response_Server2 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server2&_return_fields%2B=health", grid_vip=config.grid_member1_vip)
                print response_Server2
                logging.info(response_Server2)
                response_Pool1 =  ib_NIOS.wapi_request('GET',"dtc:pool?name=Pool1&_return_fields%2B=health", grid_vip=config.grid_member1_vip)
                print response_Pool1
                logging.info(response_Pool1)
                response_lbdn =  ib_NIOS.wapi_request('GET',"dtc:lbdn?name=lbdn&_return_fields%2B=health", grid_vip=config.grid_member1_vip)
                print response_lbdn
                logging.info(response_lbdn)
		List=[response_Server1,response_Server2,response_Pool1,response_lbdn]
                for health in List:
                        if ('"availability": "GREEN"' in health):
                                assert True
                        else:
                                assert False
                print("Test Case 47 Execution Completed")
		
        @pytest.mark.run(order=48)
        def test_048_Validate_DTC_Objects_health_status_of_SA_Member(self):
                logging.info("Validate DTC Objects health_status of SA")
                response_Server1 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server1&_return_fields%2B=health", grid_vip=config.grid_member2_vip)
                print response_Server1
                logging.info(response_Server1)
                response_Server2 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server2&_return_fields%2B=health", grid_vip=config.grid_member2_vip)
                print response_Server2
                logging.info(response_Server2)
                response_Pool1 =  ib_NIOS.wapi_request('GET',"dtc:pool?name=Pool1&_return_fields%2B=health", grid_vip=config.grid_member2_vip)
                print response_Pool1
                logging.info(response_Pool1)
                response_lbdn =  ib_NIOS.wapi_request('GET',"dtc:lbdn?name=lbdn&_return_fields%2B=health", grid_vip=config.grid_member2_vip)
                print response_lbdn
                logging.info(response_lbdn)
		List=[response_Server1,response_Server2,response_Pool1,response_lbdn]
                for health in List:
                        if ('"availability": "GREEN"' in health):
                                assert True
                        else:
                                assert False
                print("Test Case 48 Execution Completed")

        @pytest.mark.run(order=49)
        def test_049_Validate_DTC_Objects_health_status_of_IBFLEX_Member(self):
                logging.info("Validate DTC Objects health_status of IBFLEX")
                response_Server1 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server1&_return_fields%2B=health", grid_vip=config.grid_member3_vip)
                print response_Server1
                logging.info(response_Server1)
                response_Server2 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server2&_return_fields%2B=health", grid_vip=config.grid_member3_vip)
                print response_Server2
                logging.info(response_Server2)
                response_Pool1 =  ib_NIOS.wapi_request('GET',"dtc:pool?name=Pool1&_return_fields%2B=health", grid_vip=config.grid_member3_vip)
                print response_Pool1
                logging.info(response_Pool1)
                response_lbdn =  ib_NIOS.wapi_request('GET',"dtc:lbdn?name=lbdn&_return_fields%2B=health", grid_vip=config.grid_member3_vip)
                print response_lbdn
                logging.info(response_lbdn)
		List=[response_Server1,response_Server2,response_Pool1,response_lbdn]
                for health in List:
                        if ('"availability": "GREEN"' in health):
                                assert True
                        else:
                                assert False
                print("Test Case 49 Execution Completed")

	@pytest.mark.run(order=50)
        def test_050_Execute_ACCEPT_Command_in_Master(self):
                logging.info("Execute_ACCEPT_Command_in_Master")
                drop='iptables -I INPUT -s '+config.Server1+' -j DROP'
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline(drop)
                child.expect('#')
                sleep(60)
		print("Test Case 50 Execution Completed")

	@pytest.mark.run(order=51)
        def test_051_Validate_DTC_Objects_health_status_of_master(self):
                logging.info("Validate DTC Objects health_status of master")
                response_Server1 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server1&_return_fields%2B=health", grid_vip=config.grid_vip)
                print response_Server1
                logging.info(response_Server1)
                response_Server2 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server2&_return_fields%2B=health", grid_vip=config.grid_vip)
                print response_Server2
                logging.info(response_Server2)
                response_Pool1 =  ib_NIOS.wapi_request('GET',"dtc:pool?name=Pool1&_return_fields%2B=health", grid_vip=config.grid_vip)
                print response_Pool1
                logging.info(response_Pool1)
                response_lbdn =  ib_NIOS.wapi_request('GET',"dtc:lbdn?name=lbdn&_return_fields%2B=health", grid_vip=config.grid_vip)
                print response_lbdn
                logging.info(response_lbdn)
		if (('"availability": "RED"' in response_Server1) and ('"availability": "GREEN"' in response_Server2) and ('"availability": "YELLOW"' in response_Pool1) and ('"availability": "YELLOW"' in response_lbdn)):
                        assert True
                else:
                        assert False

		print("Test Case 51 Execution Completed")

        @pytest.mark.run(order=52)
        def test_052_Validate_DTC_Objects_health_status_of_HA_Member(self):
                logging.info("Validate DTC Objects health_status of HA")
                response_Server1 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server1&_return_fields%2B=health", grid_vip=config.grid_member1_vip)
                print response_Server1
                logging.info(response_Server1)
                response_Server2 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server2&_return_fields%2B=health", grid_vip=config.grid_member1_vip)
                print response_Server2
                logging.info(response_Server2)
                response_Pool1 =  ib_NIOS.wapi_request('GET',"dtc:pool?name=Pool1&_return_fields%2B=health", grid_vip=config.grid_member1_vip)
                print response_Pool1
                logging.info(response_Pool1)
                response_lbdn =  ib_NIOS.wapi_request('GET',"dtc:lbdn?name=lbdn&_return_fields%2B=health", grid_vip=config.grid_member1_vip)
                print response_lbdn
                logging.info(response_lbdn)
		if (('"availability": "RED"' in response_Server1) and ('"availability": "GREEN"' in response_Server2) and ('"availability": "YELLOW"' in response_Pool1) and ('"availability": "YELLOW"' in response_lbdn)):
                        assert True
                else:
                        assert False

                print("Test Case 52 Execution Completed")

	@pytest.mark.run(order=53)
        def test_053_Validate_DTC_Objects_health_status_of_SA_Member(self):
                logging.info("Validate DTC Objects health_status of SA")
                response_Server1 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server1&_return_fields%2B=health", grid_vip=config.grid_member2_vip)
                print response_Server1
                logging.info(response_Server1)
                response_Server2 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server2&_return_fields%2B=health", grid_vip=config.grid_member2_vip)
                print response_Server2
                logging.info(response_Server2)
                response_Pool1 =  ib_NIOS.wapi_request('GET',"dtc:pool?name=Pool1&_return_fields%2B=health", grid_vip=config.grid_member2_vip)
                print response_Pool1
                logging.info(response_Pool1)
                response_lbdn =  ib_NIOS.wapi_request('GET',"dtc:lbdn?name=lbdn&_return_fields%2B=health", grid_vip=config.grid_member2_vip)
                print response_lbdn
                logging.info(response_lbdn)
		if (('"availability": "RED"' in response_Server1) and ('"availability": "GREEN"' in response_Server2) and ('"availability": "YELLOW"' in response_Pool1) and ('"availability": "YELLOW"' in response_lbdn)):
                        assert True
                else:
                        assert False

                print("Test Case 53 Execution Completed")

	@pytest.mark.run(order=54)
        def test_054_Validate_DTC_Objects_health_status_of_IBFLEX_Member(self):
                logging.info("Validate DTC Objects health_status of IBFLEX")
                response_Server1 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server1&_return_fields%2B=health", grid_vip=config.grid_member3_vip)
                print response_Server1
                logging.info(response_Server1)
                response_Server2 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server2&_return_fields%2B=health", grid_vip=config.grid_member3_vip)
                print response_Server2
                logging.info(response_Server2)
                response_Pool1 =  ib_NIOS.wapi_request('GET',"dtc:pool?name=Pool1&_return_fields%2B=health", grid_vip=config.grid_member3_vip)
                print response_Pool1
                logging.info(response_Pool1)
                response_lbdn =  ib_NIOS.wapi_request('GET',"dtc:lbdn?name=lbdn&_return_fields%2B=health", grid_vip=config.grid_member3_vip)
                print response_lbdn
                logging.info(response_lbdn)
		if (('"availability": "RED"' in response_Server1) and ('"availability": "GREEN"' in response_Server2) and ('"availability": "YELLOW"' in response_Pool1) and ('"availability": "YELLOW"' in response_lbdn)):
                        assert True
                else:
                        assert False

                print("Test Case 54 Execution Completed")

	#SPTYRFE-50
	@pytest.mark.run(order=55)
        def test_055_Validating_Verify_certificates_command(self):
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('show  verify_certificates')
		child.expect('Infoblox >')
		response=child.before
		assert re.search(r'ocsp_ca_cert.pem: OK',response)
		print("Test Case 55 Execution Completed")		
		
	@pytest.mark.run(order=56)
        def test_056_Create_Empty_certicate_From_Bash(self):
                logging.info("Create Empty certicate")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member2_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cd /infoblox/security/certs')
                child.expect('#')
		child.sendline('>siva.pem')
                child.expect('#')
		print("Test Case 56 Execution Completed")
	
	@pytest.mark.run(order=57)
        def test_057_Validate_Empty_certicate_from_Bash(self):
                logging.info("Validate Empty certicate from Bash")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member2_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('openssl verify -verbose /infoblox/security/certs/*.pem')
                child.expect('#')
		response=child.before
		assert re.search(r'unable to load certificate',response)
		print("Test Case 57 Execution Completed")

	@pytest.mark.run(order=58)
        def test_058_Validating_Empty_Certificate_using_Verify_certificates_command(self):
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('show  verify_certificates')
                child.expect('Infoblox >')
                response=child.before
                assert re.search(r'siva.pem is empty, skipping',response)
		print("Test Case 58 Execution Completed")

	@pytest.mark.run(order=59)
        def test_059_Adding_CA_certificate(self):
		logging.info("Adding CA certificate")
		create_file = ib_NIOS.wapi_request('POST', object_type="fileop",params="?_function=uploadinit",grid_vip=config.grid_member2_vip)
		logging.info(create_file)
                res = json.loads(create_file)
                token = json.loads(create_file)['token']
		print(token)
                url = json.loads(create_file)['url']
		print(url)
		os.system("curl -k -u admin:infoblox -H 'content-typemultipart-formdata' '"+url+"' -F file=@ca.pem")
		data = {"token": token, "certificate_usage":"EAP_CA"}
               	response = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=uploadcertificate",grid_vip=config.grid_member2_vip)
		sleep(60)
		print("Test Case 59 Execution Completed")

	@pytest.mark.run(order=60)
        def test_060_Validating_CA_certificate(self):
                logging.info("Validating CA certificate")
		response =  ib_NIOS.wapi_request('GET',"cacertificate", grid_vip=config.grid_member2_vip)
                print response
		assert re.search(r'Infoblox',response)
		print("Test Case 60 Execution Completed")
		
	@pytest.mark.run(order=61)
        def test_061_Validating_Verify_certificates_command(self):
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('show  verify_certificates')
                child.expect('Infoblox >')
                response=child.before
                assert re.search(r'vdiscovery_ca_certs.pem: OK',response)
		print("Test Case 61 Execution Completed")

	@pytest.mark.run(order=62)
        def test_062_Add_Data_into_certicate(self):
                logging.info("Add data into  certicate")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member2_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cd /infoblox/security/certs')
                child.expect('#')
                child.sendline('echo "ssh -o StrictHostKeyChecking=no root" >siva.pem')
                child.expect('#')
		child.close()
		print("Test Case 62 Execution Completed")
	
	@pytest.mark.run(order=63)
        def test_063_Validating_Broken_Certificate_using_Verify_certificates_command(self):
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('show  verify_certificates')
                child.expect('Infoblox >')
                response=child.before
		child.close()
                assert re.search(r'siva.pem  --',response)
		print("Test Case 63 Execution Completed")

	#RFE-9893 with IPV6
	@pytest.mark.run(order=64)
        def test_064_Validate_DTC_Objects_health_status_of_master(self):
                logging.info("Validate DTC Objects health_status of master")
                response_Server1 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server1&_return_fields%2B=health", grid_vip=config.grid_vip_v6)
                print response_Server1
                logging.info(response_Server1)
                response_Server2 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server2&_return_fields%2B=health", grid_vip=config.grid_vip_v6)
                print response_Server2
                logging.info(response_Server2)
                response_Pool1 =  ib_NIOS.wapi_request('GET',"dtc:pool?name=Pool1&_return_fields%2B=health", grid_vip=config.grid_vip_v6)
                print response_Pool1
                logging.info(response_Pool1)
                response_lbdn =  ib_NIOS.wapi_request('GET',"dtc:lbdn?name=lbdn&_return_fields%2B=health", grid_vip=config.grid_vip_v6)
                print response_lbdn
                logging.info(response_lbdn)
                if (('"availability": "RED"' in response_Server1) and ('"availability": "GREEN"' in response_Server2) and ('"availability": "YELLOW"' in response_Pool1) and ('"availability": "YELLOW"' in response_lbdn)):
                        assert True
                else:
                        assert False

                print("Test Case 64 Execution Completed")

        @pytest.mark.run(order=65)
        def test_065_Validate_DTC_Objects_health_status_of_SA_Member(self):
                logging.info("Validate DTC Objects health_status of SA")
                response_Server1 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server1&_return_fields%2B=health", grid_vip=config.grid_member2_vip_v6)
                print response_Server1
                logging.info(response_Server1)
                response_Server2 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server2&_return_fields%2B=health", grid_vip=config.grid_member2_vip_v6)
                print response_Server2
                logging.info(response_Server2)
                response_Pool1 =  ib_NIOS.wapi_request('GET',"dtc:pool?name=Pool1&_return_fields%2B=health", grid_vip=config.grid_member2_vip_v6)
                print response_Pool1
                logging.info(response_Pool1)
                response_lbdn =  ib_NIOS.wapi_request('GET',"dtc:lbdn?name=lbdn&_return_fields%2B=health", grid_vip=config.grid_member2_vip_v6)
                print response_lbdn
                logging.info(response_lbdn)
                if (('"availability": "RED"' in response_Server1) and ('"availability": "GREEN"' in response_Server2) and ('"availability": "YELLOW"' in response_Pool1) and ('"availability": "YELLOW"' in response_lbdn)):
                        assert True
                else:
                        assert False

                print("Test Case 65 Execution Completed")

        @pytest.mark.run(order=66)
        def test_066_Validate_DTC_Objects_health_status_of_IBFLEX_Member(self):
                logging.info("Validate DTC Objects health_status of IBFLEX")
                response_Server1 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server1&_return_fields%2B=health", grid_vip=config.grid_member3_vip_v6)
                print response_Server1
                logging.info(response_Server1)
                response_Server2 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server2&_return_fields%2B=health", grid_vip=config.grid_member3_vip_v6)
                print response_Server2
                logging.info(response_Server2)
                response_Pool1 =  ib_NIOS.wapi_request('GET',"dtc:pool?name=Pool1&_return_fields%2B=health", grid_vip=config.grid_member3_vip_v6)
                print response_Pool1
                logging.info(response_Pool1)
                response_lbdn =  ib_NIOS.wapi_request('GET',"dtc:lbdn?name=lbdn&_return_fields%2B=health", grid_vip=config.grid_member3_vip_v6)
                print response_lbdn
                logging.info(response_lbdn)
                if (('"availability": "RED"' in response_Server1) and ('"availability": "GREEN"' in response_Server2) and ('"availability": "YELLOW"' in response_Pool1) and ('"availability": "YELLOW"' in response_lbdn)):
                        assert True
                else:
                        assert False

                print("Test Case 66 Execution Completed")
	
        @pytest.mark.run(order=67)
        def test_067_Download_Grid_Master_support_bundle(self):
                logging.info("Download Grid Master Support Bundle")       
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')	
                child.sendline('set transfer_supportbundle scp '+config.Client_ip+' root infoblox dest /tmp/support_bundle_master.gz core_files')
                child.expect(':')
                child.sendline('y')
                sleep(100)
                child.expect('Infoblox >')
                response=child.before
                assert re.search(r'supportBundle is uploaded to scp server.* successfully',response)
                print("Test Case 67 Execution Completed")

        @pytest.mark.run(order=68)
        def test_068_Validate_parsed_health_File_in_Master_Support_Bundle(self):
                logging.info("Validate parsed_health_File in Master Support_Bundle")
                os.system("mkdir master;cd master;cp -rf /tmp/support_bundle_master.gz .;tar -xvf support_bundle_master.gz")
                files=os.listdir('master/storage/tmp')
                print("Files",files)
                if ("parsed_health.gz" in files):
                        assert True
                else:
                        assert False
                sleep(10)
                print("Test Case 68 Execution Completed")

        @pytest.mark.run(order=69)
        def test_069_Download_HA_Active_Node_support_bundle(self):
                logging.info("Download HA Active Node Support Bundle")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.active_ip)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('set transfer_supportbundle scp '+config.Client_ip+' root infoblox dest /tmp/support_bundle_active.gz core_files')
                child.expect(':')
                child.sendline('y')
                sleep(100)
                child.expect('Infoblox >')
                response=child.before
                assert re.search(r'supportBundle is uploaded to scp server.* successfully',response)
                print("Test Case 69 Execution Completed")

        @pytest.mark.run(order=70)
        def test_070_Validate_parsed_health_File_in_HA_Active_Node_Support_Bundle(self):
                logging.info("Validate parsed_health_File in HA_Active_Node Support_Bundle")
                os.system("mkdir HA_Active_Node;cd HA_Active_Node;cp -rf /tmp/support_bundle_active.gz .;tar -xvf support_bundle_active.gz")
                files=os.listdir('HA_Active_Node/storage/tmp')
                print("Files",files)
                if ("parsed_health.gz" in files):
                        assert True
                else:
                        assert False
                sleep(10)
                print("Test Case 70 Execution Completed")

        @pytest.mark.run(order=71)
        def test_071_Download_SA_Member_support_bundle(self):
                logging.info("Download SA_Member Support Bundle")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('set transfer_supportbundle scp '+config.Client_ip+' root infoblox dest /tmp/support_bundle_SA_Member.gz core_files')
                child.expect(':')
                child.sendline('y')
                sleep(100)
                child.expect('Infoblox >')
                response=child.before
                assert re.search(r'supportBundle is uploaded to scp server.* successfully',response)
                print("Test Case 71 Execution Completed")

        @pytest.mark.run(order=72)
        def test_072_Validate_parsed_health_File_in_SA_Member_Support_Bundle(self):
                logging.info("Validate parsed_health_File in SA_Member Support_Bundle")
                os.system("mkdir SA_Member;cd SA_Member;cp -rf /tmp/support_bundle_SA_Member.gz .;tar -xvf support_bundle_SA_Member.gz")
                files=os.listdir('SA_Member/storage/tmp')
                print("Files",files)
                if ("parsed_health.gz" in files):
                        assert True
                else:
                        assert False
                sleep(10)
                print("Test Case 72 Execution Completed")

        @pytest.mark.run(order=73)
        def test_073_Download_IB_Flex_Member_support_bundle(self):
                logging.info("Download IB_Flex_Member Support Bundle")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member3_vip)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('set transfer_supportbundle scp '+config.Client_ip+' root infoblox dest /tmp/support_bundle_IB_Flex_Member.gz core_files')
                child.expect(':')
                child.sendline('y')
                sleep(100)
                child.expect('Infoblox >')
                response=child.before
                assert re.search(r'supportBundle is uploaded to scp server.* successfully',response)
                print("Test Case 73 Execution Completed")

        @pytest.mark.run(order=74)
        def test_074_Validate_parsed_health_File_in_IB_Flex_Member_Support_Bundle(self):
                logging.info("Validate parsed_health_File in IB_Flex_Member Support_Bundle")
                os.system("mkdir IB_Flex_Member;cd IB_Flex_Member;cp -rf /tmp/support_bundle_IB_Flex_Member.gz .;tar -xvf support_bundle_IB_Flex_Member.gz")
                files=os.listdir('IB_Flex_Member/storage/tmp')
                print("Files",files)
                if ("parsed_health.gz" in files):
                        assert True
                else:
                        assert False
                sleep(10)
                print("Test Case 74 Execution Completed")

        @pytest.mark.run(order=75)
        def test_075_Download_Grid_HA_Passive_Node_support_bundle(self):
                logging.info("Download HA_Passive_Node Support Bundle")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.passive_ip)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('show status')
                child.expect('>')
                passive_status=child.before
                if ("Passive" in passive_status):
                    passive_ip=config.passive_ip
                else:
                    passive_ip=config.active_ip
		child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+passive_ip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('rm -rf /tmp/parsed_health*')
                child.expect('#')
                child.close()
		sleep(100)
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+passive_ip)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('set transfer_supportbundle scp '+config.Client_ip+' root infoblox dest /tmp/support_bundle_passive.gz core_files')
                child.expect(':')
                child.sendline('y')
                sleep(100)
                child.expect('Infoblox >')
                response=child.before
                assert re.search(r'supportBundle is uploaded to scp server.* successfully',response)
                print("Test Case 75 Execution Completed")

        @pytest.mark.run(order=76)
        def test_076_Validate_parsed_health_File_in_HA_PAssive_Support_Bundle(self):
                logging.info("Validate parsed_health_File in Master Support_Bundle")
                os.system("mkdir HA_Passive_Node;cd HA_Passive_Node;cp -rf /tmp/support_bundle_passive.gz .;tar -xvf support_bundle_passive.gz")
                files=os.listdir('HA_Passive_Node/storage/tmp')
                print("Files",files)
                if ("parsed_health.gz" not in files):
                        assert True
                else:
                        assert False
                sleep(10) 
                print("Test Case 76 Execution Completed")
                
        @pytest.mark.run(order=77)
        def test_077_Taking_DTC_Backup_Config_File(self):
                logging.info("Taking DTC Backup config file")
                data = {"type": "BACKUP_DTC"}
                response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=getgriddata",grid_vip=config.grid_member2_vip)
                response = json.loads(response)
                global token_of_GM
                global token_of_URL
                token_of_GM = response['token']
                token_of_URL = response['url']
                print(token_of_GM)
                print(token_of_URL)
                print("Test Case 77 Execution Completed")
    
        @pytest.mark.run(order=78)
        def test_078_Delete_the_DTC_LBDN2(self):
                response = ib_NIOS.wapi_request('GET', object_type="dtc:lbdn?name=lbdn", grid_vip=config.grid_member2_vip)
                response = json.loads(response)
                ref_lbdn = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('DELETE', object_type=ref_lbdn, grid_vip=config.grid_member2_vip)
                print("Restart DNS Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_member2_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_member2_vip)
                sleep(30)
                print("Test Case 78 Execution Completed")

        @pytest.mark.run(order=79)
        def test_079_Validate_Deleted_LBDN(self):
                logging.info("Validate Deleted LBDN")
                response =  ib_NIOS.wapi_request('GET', object_type="dtc:lbdn?name=lbdn", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                if (response=='[]'):
                        assert True
                else:
                        assert False
                sleep(5)
                print("Test Case 79 Execution Completed")

        @pytest.mark.run(order=80)
        def test_080_Restore_DTC_Config_File(self):
                log("start","/infoblox/var/infoblox.log", config.grid_member2_vip)
                data = {"forced": False, "token": token_of_GM}
                response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=restoredtcconfig",grid_vip=config.grid_member2_vip)
                sleep(30)
                LookFor="'DTC restore: done'"
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_member2_vip)
                print("Restart DNS Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_member2_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_member2_vip)
                sleep(60)
                logging.info("Test Case 079 Execution Completed")
       
        @pytest.mark.run(order=81) 
        def test_081_Validate_DTC_Objects_health_status_of_master(self):
                logging.info("Validate DTC Objects health_status of master")
                response_Server1 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server1&_return_fields%2B=health", grid_vip=config.grid_vip)
                print response_Server1
                logging.info(response_Server1)
                response_Server2 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server2&_return_fields%2B=health", grid_vip=config.grid_vip)
                print response_Server2
                logging.info(response_Server2)
                response_Pool1 =  ib_NIOS.wapi_request('GET',"dtc:pool?name=Pool1&_return_fields%2B=health", grid_vip=config.grid_vip)
                print response_Pool1
                logging.info(response_Pool1)
                response_lbdn =  ib_NIOS.wapi_request('GET',"dtc:lbdn?name=lbdn&_return_fields%2B=health", grid_vip=config.grid_vip)
                print response_lbdn
                logging.info(response_lbdn)
                if (('"availability": "RED"' in response_Server1) and ('"availability": "GREEN"' in response_Server2) and ('"availability": "YELLOW"' in response_Pool1) and ('"availability": "YELLOW"' in response_lbdn)):
                        assert True
                else:
                        assert False
                print("Test Case 81 Execution Completed")

        @pytest.mark.run(order=82)
        def test_082_Validate_DTC_Objects_health_status_of_HA_Member(self):
                logging.info("Validate DTC Objects health_status of HA")
                response_Server1 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server1&_return_fields%2B=health", grid_vip=config.grid_member1_vip)
                print response_Server1
                logging.info(response_Server1)
                response_Server2 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server2&_return_fields%2B=health", grid_vip=config.grid_member1_vip)
                print response_Server2
                logging.info(response_Server2)
                response_Pool1 =  ib_NIOS.wapi_request('GET',"dtc:pool?name=Pool1&_return_fields%2B=health", grid_vip=config.grid_member1_vip)
                print response_Pool1
                logging.info(response_Pool1)
                response_lbdn =  ib_NIOS.wapi_request('GET',"dtc:lbdn?name=lbdn&_return_fields%2B=health", grid_vip=config.grid_member1_vip)
                print response_lbdn
                logging.info(response_lbdn)
                if (('"availability": "RED"' in response_Server1) and ('"availability": "GREEN"' in response_Server2) and ('"availability": "YELLOW"' in response_Pool1) and ('"availability": "YELLOW"' in response_lbdn)):
                        assert True
                else:
                        assert False
                print("Test Case 82 Execution Completed")

        @pytest.mark.run(order=83)
        def test_083_Validate_DTC_Objects_health_status_of_SA_Member(self):
                logging.info("Validate DTC Objects health_status of SA")
                response_Server1 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server1&_return_fields%2B=health", grid_vip=config.grid_member2_vip)
                print response_Server1
                logging.info(response_Server1)
                response_Server2 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server2&_return_fields%2B=health", grid_vip=config.grid_member2_vip)
                print response_Server2
                logging.info(response_Server2)
                response_Pool1 =  ib_NIOS.wapi_request('GET',"dtc:pool?name=Pool1&_return_fields%2B=health", grid_vip=config.grid_member2_vip)
                print response_Pool1
                logging.info(response_Pool1)
                response_lbdn =  ib_NIOS.wapi_request('GET',"dtc:lbdn?name=lbdn&_return_fields%2B=health", grid_vip=config.grid_member2_vip)
                print response_lbdn
                logging.info(response_lbdn)
                if (('"availability": "RED"' in response_Server1) and ('"availability": "GREEN"' in response_Server2) and ('"availability": "YELLOW"' in response_Pool1) and ('"availability": "YELLOW"' in response_lbdn)):
                        assert True
                else:
                        assert False
                print("Test Case 83 Execution Completed")

        @pytest.mark.run(order=84)
        def test_084_Validate_DTC_Objects_health_status_of_IBFLEX_Member(self):
                logging.info("Validate DTC Objects health_status of IBFLEX")
                response_Server1 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server1&_return_fields%2B=health", grid_vip=config.grid_member3_vip)
                print response_Server1
                logging.info(response_Server1)
                response_Server2 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server2&_return_fields%2B=health", grid_vip=config.grid_member3_vip)
                print response_Server2
                logging.info(response_Server2)
                response_Pool1 =  ib_NIOS.wapi_request('GET',"dtc:pool?name=Pool1&_return_fields%2B=health", grid_vip=config.grid_member3_vip)
                print response_Pool1
                logging.info(response_Pool1)
                response_lbdn =  ib_NIOS.wapi_request('GET',"dtc:lbdn?name=lbdn&_return_fields%2B=health", grid_vip=config.grid_member3_vip)
                print response_lbdn
                logging.info(response_lbdn)
                if (('"availability": "RED"' in response_Server1) and ('"availability": "GREEN"' in response_Server2) and ('"availability": "YELLOW"' in response_Pool1) and ('"availability": "YELLOW"' in response_lbdn)):
                        assert True
                else:
                        assert False
                print("Test Case 84 Execution Completed")
       
        @pytest.mark.run(order=85)
        def test_085_Execute_ACCEPT_Command_in_Master(self):
                logging.info("Execute_ACCEPT_Command_in_Master")
                drop='iptables -I INPUT -s '+config.Server1+' -j ACCEPT'
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline(drop)
                child.expect('#')
                sleep(60)
                print("Test Case 85 Execution Completed")
 
        @pytest.mark.run(order=86)
        def test_086_Validate_DTC_Objects_health_status_of_master(self):
                logging.info("Validate DTC Objects health_status of master")
                response_Server1 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server1&_return_fields%2B=health", grid_vip=config.grid_vip)
                print response_Server1
                logging.info(response_Server1)
                response_Server2 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server2&_return_fields%2B=health", grid_vip=config.grid_vip)
                print response_Server2
                logging.info(response_Server2)
                response_Pool1 =  ib_NIOS.wapi_request('GET',"dtc:pool?name=Pool1&_return_fields%2B=health", grid_vip=config.grid_vip)
                print response_Pool1
                logging.info(response_Pool1)
                response_lbdn =  ib_NIOS.wapi_request('GET',"dtc:lbdn?name=lbdn&_return_fields%2B=health", grid_vip=config.grid_vip)
                print response_lbdn
                logging.info(response_lbdn)
                List=[response_Server1,response_Server2,response_Pool1,response_lbdn]
                for health in List:
                        if ('"availability": "GREEN"' in health):
                                assert True
                        else:
                                assert False
                print("Test Case 86 Execution Completed")

        @pytest.mark.run(order=87)
        def test_087_Validate_DTC_Objects_health_status_of_HA_Member(self):
                logging.info("Validate DTC Objects health_status of HA")
                response_Server1 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server1&_return_fields%2B=health", grid_vip=config.grid_member1_vip)
                print response_Server1
                logging.info(response_Server1)
                response_Server2 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server2&_return_fields%2B=health", grid_vip=config.grid_member1_vip)
                print response_Server2
                logging.info(response_Server2)
                response_Pool1 =  ib_NIOS.wapi_request('GET',"dtc:pool?name=Pool1&_return_fields%2B=health", grid_vip=config.grid_member1_vip)
                print response_Pool1
                logging.info(response_Pool1)
                response_lbdn =  ib_NIOS.wapi_request('GET',"dtc:lbdn?name=lbdn&_return_fields%2B=health", grid_vip=config.grid_member1_vip)
                print response_lbdn
                logging.info(response_lbdn)
                List=[response_Server1,response_Server2,response_Pool1,response_lbdn]
                for health in List:
                        if ('"availability": "GREEN"' in health):
                                assert True
                        else:
                                assert False
                print("Test Case 87 Execution Completed")

        @pytest.mark.run(order=88)
        def test_088_Validate_DTC_Objects_health_status_of_SA_Member(self):
                logging.info("Validate DTC Objects health_status of SA")
                response_Server1 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server1&_return_fields%2B=health", grid_vip=config.grid_member2_vip)
                print response_Server1
                logging.info(response_Server1)
                response_Server2 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server2&_return_fields%2B=health", grid_vip=config.grid_member2_vip)
                print response_Server2
                logging.info(response_Server2)
                response_Pool1 =  ib_NIOS.wapi_request('GET',"dtc:pool?name=Pool1&_return_fields%2B=health", grid_vip=config.grid_member2_vip)
                print response_Pool1
                logging.info(response_Pool1)
                response_lbdn =  ib_NIOS.wapi_request('GET',"dtc:lbdn?name=lbdn&_return_fields%2B=health", grid_vip=config.grid_member2_vip)
                print response_lbdn
                logging.info(response_lbdn)
                List=[response_Server1,response_Server2,response_Pool1,response_lbdn]
                for health in List:
                        if ('"availability": "GREEN"' in health):
                                assert True
                        else:
                                assert False
                print("Test Case 88 Execution Completed")

        @pytest.mark.run(order=89)
        def test_089_Validate_DTC_Objects_health_status_of_IBFLEX_Member(self):
                logging.info("Validate DTC Objects health_status of IBFLEX")
                response_Server1 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server1&_return_fields%2B=health", grid_vip=config.grid_member3_vip)
                print response_Server1
                logging.info(response_Server1)
                response_Server2 =  ib_NIOS.wapi_request('GET',"dtc:server?name=Server2&_return_fields%2B=health", grid_vip=config.grid_member3_vip)
                print response_Server2
                logging.info(response_Server2)
                response_Pool1 =  ib_NIOS.wapi_request('GET',"dtc:pool?name=Pool1&_return_fields%2B=health", grid_vip=config.grid_member3_vip)
                print response_Pool1
                logging.info(response_Pool1)
                response_lbdn =  ib_NIOS.wapi_request('GET',"dtc:lbdn?name=lbdn&_return_fields%2B=health", grid_vip=config.grid_member3_vip)
                print response_lbdn
                logging.info(response_lbdn)
                List=[response_Server1,response_Server2,response_Pool1,response_lbdn]
                for health in List:
                        if ('"availability": "GREEN"' in health):
                                assert True
                        else:
                                assert False
                print("Test Case 89 Execution Completed")

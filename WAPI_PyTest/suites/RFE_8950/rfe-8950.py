import re
import config
import pytest
import unittest
import logging
import subprocess
import os
import json
import sys
#sys.path.append("/home/akulkarni/RFE_8950/WAPI_PyTest/")
import ib_utils.ib_NIOS as ib_NIOS
from time import sleep
import commands
import json, ast
import requests
import time
import pexpect

class Network(unittest.TestCase):



	 @pytest.mark.run(order=1)
         def test_001_Create_New_AuthZone(self):
                logging.info("Create An auth Zone")
                data = {"fqdn": "parent.tld"}
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
         def test_003_Create_a_forward_zone(self):
                logging.info("Create A forward Zone")
                data = {"fqdn":"subdomain.parent.tld","forward_to":[{"name":"ns1.someotherzone.tld","address":"1.2.3.4"}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_forward", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 3 Execution Completed")



	 @pytest.mark.run(order=4)
         def test_004_create_grid_primary_for_forward_zone(self):
                logging.info("Create grid_primary with required fields")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_forward")
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

                logging.info("Test Case 4 Execution Completed")



	 @pytest.mark.run(order=5)
         def test_005_Modify_log_queries(self):
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify a  log_queries")
                data = {"logging_categories":{"log_queries": True,"log_responses": True}}
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
                logging.info("Test Case 5 Execution Completed")


	 @pytest.mark.run(order=6)
         def test_006_perform_query_for_record_on_master(self):
                logging.info("Perform query for DTC record ")
                dig_cmd = 'dig @'+str(config.grid_vip)+' foobar.subdomain.parent.tld IN A'
                dig_cmd1 = os.system(dig_cmd)
                logging.info("Test Case 8 Execution Completed")
                sleep(10)



	 @pytest.mark.run(order=7)
         def test_007_enable_checkbox_disable_ns_generation(self):
                logging.info("Enable check box for disable_ns_generation")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_forward")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                data = {"disable_ns_generation": True}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 7 Execution Completed")
		sleep(10)

	 @pytest.mark.run(order=8)
         def test_008_perform_query_for_record_on_master_for_NXDOMAIN_response(self):
                logging.info("Perform query to get NXDOMAIN response")
                dig_cmd = 'dig @'+str(config.grid_vip)+' foobar.subdomain.parent.tld  IN A'
                dig_cmd1 = os.system(dig_cmd)
                logging.info("Validate Syslog afer perform queries")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -10 /var/log/syslog | grep  \'NXDOMAIN\'"'
                out1 = commands.getoutput(sys_log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'NXDOMAIN',out1)
                logging.info("Test Case 8 Execution Completed")
                sleep(10)


	 @pytest.mark.run(order=9)
         def test_009_disable_checkbox_disable_ns_generation(self):
                logging.info("Disable check box for disable_ns_generation")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_forward")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                data = {"disable_ns_generation": False}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 9 Execution Completed")
                sleep(10)


	 @pytest.mark.run(order=10)
         def test_010_perform_query_for_record_on_master(self):
                logging.info("Perform query for DTC record ")
                dig_cmd = 'dig @'+str(config.grid_vip)+' foobar.subdomain.parent.tld IN A'
                dig_cmd1 = os.system(dig_cmd)
                logging.info("Test Case 10 Execution Completed")
                sleep(10)


	 @pytest.mark.run(order=11)
         def test_011_enable_checkbox_disable_ns_generation(self):
                logging.info("Enable check box for disable_ns_generation")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_forward")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                data = {"disable_ns_generation": True}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 7 Execution Completed")
                sleep(10)

         @pytest.mark.run(order=12)
         def test_012_perform_query_for_record_on_master_for_NXDOMAIN_response(self):
                logging.info("Perform query to get NXDOMAIN response")
                dig_cmd = 'dig @'+str(config.grid_vip)+' foobar.subdomain.parent.tld  IN A'
                dig_cmd1 = os.system(dig_cmd)
                logging.info("Validate Syslog afer perform queries")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -10 /var/log/syslog | grep  \'NXDOMAIN\'"'
                out1 = commands.getoutput(sys_log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'NXDOMAIN',out1)
                logging.info("Test Case 12 Execution Completed")
                sleep(10)


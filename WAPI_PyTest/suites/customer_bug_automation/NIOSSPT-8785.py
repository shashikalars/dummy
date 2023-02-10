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
import time
from time import sleep
import pexpect
from paramiko import client
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as comm_util
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv



class Network(unittest.TestCase):


            @pytest.mark.run(order=0)
            def test_00_Delete_Network(self):
                logging.info("Deleting the 10.0.0.0 NETWORK")
                #res = ib_NIOS.wapi_request('GET',object_type='network?network=10.0.0.0/8')
                res = ib_NIOS.wapi_request('GET',object_type='network')
                print(res)
                if ("10.0.0.0/8" in res):
                     res = json.loads(res)
                     zone_ref=res[0]['_ref']
                     response=ib_NIOS.wapi_request('DELETE', object_type=zone_ref)
                     print(response)
                     grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                     ref = json.loads(grid)[0]['_ref']
                     data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                     request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                     logging.info("Wait for 20 sec.,")
                     sleep(20)
                else:
                    print("No Networks are there to delete")
                print("Test Case Completed")

            @pytest.mark.run(order=1)
            def test_01_start_IPv4_DHCP_service(self):
                logging.info("start the ipv4 DHCP service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print (ref1)
                data = {"enable_dhcp":True}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                print("Test Case 1 Execution Completed")

            @pytest.mark.run(order=2)
            def test_02_start_IPv4_DNS_service(self):
                logging.info("start the ipv4 DNS service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print (ref1)
                data = {"enable_dns": True}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                sleep(20)
                logging.info(response)
                print (response)
                print("Test Case 2 Execution Completed")

            @pytest.mark.run(order=3)
            def test_03_create_IPv4_network(self):
                logging.info("Create an ipv4 network default network view")
                data = {"network": "10.0.0.0/8","network_view": "default","members":[{"_struct": "dhcpmember","ipv4addr":config.grid_vip}]}
                response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                read  = re.search(r'201',response)
                for read in  response:
                         assert True
                print("Created the ipv4network 10.0.0.0/8 in default view")
                logging.info("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 3 Execution Completed")

            @pytest.mark.run(order=4)
            def test_04_create_IPv4_Range(self):
                logging.info("Create an IPv4 range in defaultnetwork view")
                data = {"network":"10.0.0.0/8","start_addr":"10.0.0.10","end_addr":"10.0.0.100","network_view": "default","member":{"_struct":"dhcpmember","ipv4addr":config.grid_vip}}
                response = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(data), grid_vip=config.grid_vip)
                print (response)
                read  = re.search(r'201',response)
                for read in  response: 
                         assert True
                print("Created the ipv4 prefix range with bits 8  in default view")
                logging.info("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 4 Execution Completed")

            @pytest.mark.run(order=5)
            def test_05_Creating_relay_agent_filter(self):
                logging.info("Create an ipv4 network default network view")
                data = {"is_circuit_id": "ANY","is_circuit_id_substring":False,"is_remote_id": "MATCHES_VALUE","is_remote_id_substring": False,"name": "prasad","remote_id_name": "gh"}
                response = ib_NIOS.wapi_request('POST', object_type="filterrelayagent", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                read  = re.search(r'201',response)
                for read in  response:
                         assert True
                print("Test Case 5 Execution Completed") 
            
            @pytest.mark.run(order=6)
            def test_06_assign_filter_for_specific_range(self):
                logging.info("assigning filter for specific range")
                get_ref = ib_NIOS.wapi_request('GET', object_type="range", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print (ref1)
                data = {"relay_agent_filter_rules":[{"filter":"prasad","permission":"Allow"}]}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                read  = re.search(r'201',response)
                for read in  response:
                         assert True
                print("Test Case 6 Execution Completed")
        
            @pytest.mark.run(order=7)
            def test_07_restart_dhcp_services(self):
                logging.info("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 7 Execution Completed")
            
            @pytest.mark.run(order=8)
            def test_08_requesting_ipv4_lease(self):
                logging.info("Perform dras command")
		for i in range(10):
                	dras_cmd = 'sudo /import/tools/qa/tools/dras/dras /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'-h -n 1 -O 82:02026768 -v '
                	dras_cmd1 = os.system(dras_cmd)
                	print (dras_cmd1)
			if dras_cmd1 == 0:
                     		print("got the lease")
                     		assert True
				break
                	else:
                     		assert False
				print("didn't get the lease and continuing for lease")
                sleep(10)
		'''
                grid =  ib_NIOS.wapi_request('GET', object_type="lease",grid_vip=config.grid_vip)
                print(grid)
                grid_json=json.loads(grid)
                ref=grid_json[-1]["_ref"]
                print(ref)
                logging.info("get option for ip")
                response = ib_NIOS.wapi_request('GET',object_type=ref+"?_return_fields=option",grid_vip=config.grid_vip)
                print(response)
                if ("10.0.0.100" in response):
                   assert True
                else:
                   assert False
		'''
                print("Test Case 8 Execution Completed")            

            @pytest.mark.run(order=9)
            def test_09_Negative_scenario_checking_with_02006768_looking_for_SIGSEGV(self):
                logging.info("Perform dras command")
                log("start","/infoblox/var/infoblox",config.grid_vip)
		for i in range(10):
                	dras_cmd = 'sudo /import/tools/qa/tools/dras/dras /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'-h -n 1 -O 82:02006768 -v '
                	dras_cmd1 = os.system(dras_cmd)
                	print (dras_cmd1)
			if dras_cmd1 == 0:
                        	print("got the lease")
                        	break
                    	else:
                        	print("didn't get the lease and continuing for lease")
               	sleep(10)
		LookFor="SIGSEGV"
                log("stop","/infoblox/var/infoblox",config.grid_vip)
                #LookFor='SIGSEGV'
                logs=logv(LookFor,"/infoblox/var/infoblox",config.grid_vip)
                print(logs)
                if logs == None:
                    print("No Error")
                    assert True
                else:
                    assert False
            

            @pytest.mark.run(order=10)
            def test_10_looking_for_segfault(self):
                logging.info("Perform dras command")
                log("start","/infoblox/var/infoblox",config.grid_vip)
                dras_cmd = 'sudo /import/qaddi/API_Automation/WAPI_PyTest/suites/RFE_6874/dras/dras -i'+str(config.grid_vip)+' '+'-h -n 1 -O 82:02026768 -v '
                dras_cmd1 = os.system(dras_cmd)
                print (dras_cmd1)
                sleep(10)
                log("stop","/infoblox/var/infoblox",config.grid_vip)
                LookFor='SIGSEGV'
                logs=logv(LookFor,"/infoblox/var/infoblox",config.grid_vip)
                print(logs)
                if logs == None:
                    print("No Error")
                    assert True
                else:
                    assert False



            @pytest.mark.run(order=11)
            def test_11_deleting_the_IPv4_network(self):
                logging.info("Deleting the 10.0.0.0 NETWORK")
                res = ib_NIOS.wapi_request('GET',object_type='network?network=10.0.0.0/8')
                res = json.loads(res)
                zone_ref=res[0]['_ref']
                response=ib_NIOS.wapi_request('DELETE', object_type=zone_ref)
                print(response)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 20 sec.,")
                sleep(20)
                print("Test Case 11 Execution Completed")

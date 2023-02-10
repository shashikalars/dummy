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

class Network(unittest.TestCase):

            @pytest.mark.run(order=1)
            def test_01_start_IPv4_DHCP_service(self):
                logging.info("start the ipv4 service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print (ref1)
                data = {"enable_dhcp":True,}
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
		logging.info("Enable capture fixed address service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"capture_hostname": True}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                print response
		logging.info("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 20 sec.,")
                sleep(20)
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
                data = {"network":"10.0.0.0/8","start_addr":"10.0.0.5","end_addr":"10.0.0.100","network_view": "default","member":{"_struct":"dhcpmember"}}
                response = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(data), grid_vip=config.grid_vip)
                print (response)
                #read  = re.search(r'201',response)
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
            def test_05_create_IPv4_network(self):
                logging.info("Create an ipv4 network default network view")
                data = {"network": "20.0.0.0/8","network_view": "default","members":[{"_struct": "dhcpmember","ipv4addr":config.grid_vip}]}
                response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                read  = re.search(r'201',response)
                for read in  response:
                       assert True
                print("Created the ipv4network 20.0.0.0/8 in default view")
                logging.info("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 10 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 5 Execution Completed")

            @pytest.mark.run(order=6)
            def test_06_create_IPv4_Range(self):
                logging.info("Create an IPv4 range in defaultnetwork view")
                data = {"network":"20.0.0.0/8","start_addr":"20.0.0.5","end_addr":"20.0.0.75","network_view": "default","member":{"_struct":"dhcpmember"}}
                response = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(data), grid_vip=config.grid_vip)
                print (response)
                print(response)
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
                print("Test Case 6 Execution Completed")

            @pytest.mark.run(order=7)
            def test_07_requesting_ipv4_lease_with_link_selection(self):
                logging.info("Perform dras command")
                dras_cmd = 'sudo /import/qaddi/API_Automation/WAPI_PyTest/suites/RFE_6874/dras/dras -i'+str(config.grid_vip)+' '+'-n 1 -x l=10.0.0.0 '
                dras_cmd1 = os.system(dras_cmd)
                print (dras_cmd1)
                sleep(20)
                grid =  ib_NIOS.wapi_request('GET', object_type="lease",grid_vip=config.grid_vip)
                print(grid)
                grid_json=json.loads(grid)
                ref=grid_json[-1]["_ref"]
                print(ref)
                logging.info("get option for ip")
                response = ib_NIOS.wapi_request('GET',object_type=ref+"?_return_fields=option",grid_vip=config.grid_vip)
                print(response)
                assert re.search(r'agent.link-selection',response)
                print("Test Case 7 Execution Completed")             

            @pytest.mark.run(order=8)
            def test_08_create_fixed_address(self):
                logging.info("Create an ipv4 network default network view")
                data = { "ipv4addr": "10.0.0.2","mac": "aa:bb:cc:dd:ee:ff","network_view": "default"}
                response = ib_NIOS.wapi_request('POST', object_type="fixedaddress", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                read  = re.search(r'201',response)
                for read in  response:
                      assert True
                print("Created the fixed address ")
                logging.info("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 8 Execution Completed")             

            @pytest.mark.run(order=9)
            def test_09_requesting_ipv4_lease_with_Exact_mac_address(self):
                logging.info("Perform dras command")
                dras_cmd = 'sudo /import/qaddi/API_Automation/WAPI_PyTest/suites/RFE_6874/dras/dras -i'+str(config.grid_vip)+' '+'-n 1 -x l=10.0.0.0 -h -a aa:bb:cc:dd:ee:ff'
                dras_cmd1 = os.system(dras_cmd)
                print (dras_cmd1)
                sleep(20)
                print("Test Case 9 Execution Completed")

            @pytest.mark.run(order=10)
            def test_10_validating_ipv4_lease_with_Exact_mac_address(self):
                grid =  ib_NIOS.wapi_request('GET', object_type="lease",grid_vip=config.grid_vip)
                #print(grid)
                grid_json=json.loads(grid)
                ref=grid_json[-1]["_ref"]
                print(ref)
                logging.info("get option for ip")
                response = ib_NIOS.wapi_request('GET',object_type=ref+"?_return_fields=option",grid_vip=config.grid_vip)
                print(response)
                assert re.search(r'agent.link-selection',response)
                print("Test Case 10 Execution Completed")

            @pytest.mark.run(order=11)
            def test_11_delete_IPv4_network(self):
                logging.info("Get Network List")
                grid =  ib_NIOS.wapi_request('GET', object_type="network",grid_vip=config.grid_vip)
                print(grid)
                res = json.loads(grid)
                for i in res:
                    if i["network"]=="10.0.0.0/8":
                        ref=i["_ref"]
                print ref
                request_restart = ib_NIOS.wapi_request('DELETE',object_type = ref,grid_vip=config.grid_vip)
                logging.info("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                logging.info("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 11 Execution Completed")

            @pytest.mark.run(order=12)
            def test_12_requesting_ipv4_lease_with_link_selection(self):
                logging.info("Perform dras command")
                dras_cmd = 'sudo /import/qaddi/API_Automation/WAPI_PyTest/suites/RFE_6874/dras/dras -i'+str(config.grid_vip)+' '+'-n 1 -x l=20.0.0.0 '
                dras_cmd1 = os.system(dras_cmd)
                print (dras_cmd1)
                sleep(20)
                grid =  ib_NIOS.wapi_request('GET', object_type="lease",grid_vip=config.grid_vip)
                #print(grid)
                grid_json=json.loads(grid)
                ref=grid_json[-1]["_ref"]
                print(ref)
                logging.info("get option for ip")
                response = ib_NIOS.wapi_request('GET',object_type=ref+"?_return_fields=option",grid_vip=config.grid_vip)
                print(response)
                assert re.search(r'agent.link-selection',response)
                print("Test Case 12 Execution Completed")

            @pytest.mark.run(order=13)
            def test_13_create_IPv4_network(self):
                logging.info("Create an ipv4 network default network view")
                data = {"network": "10.0.0.0/8","network_view": "default","members":[{"_struct": "dhcpmember","ipv4addr":config.grid_vip}]}
                response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                read  = re.search(r'201',response)
                for read in  response:
                         assert True
                print("Created the ipv4network 10.0.0.0/8 in default view")
                logging.info("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 13 Execution Completed")

            @pytest.mark.run(order=14)
            def test_14_create_IPv4_Range(self):
                logging.info("Create an IPv4 range in defaultnetwork view")
                data = {"network":"10.0.0.0/8","start_addr":"10.0.0.5","end_addr":"10.0.0.100","network_view": "default","member":{"_struct":"dhcpmember"}}
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
                logging.info("Wait for 30 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 14 Execution Completed")
                
            @pytest.mark.run(order=15)
            def test_15_requesting_ipv4_lease_with_link_selection(self):
                logging.info("Perform dras command")
                dras_cmd = 'sudo /import/qaddi/API_Automation/WAPI_PyTest/suites/RFE_6874/dras/dras -i'+str(config.grid_vip)+' '+'-n 1 -x l=10.0.0.0 '
                dras_cmd1 = os.system(dras_cmd)
                print (dras_cmd1)
                sleep(20)
                grid =  ib_NIOS.wapi_request('GET', object_type="lease",grid_vip=config.grid_vip)
	        #print(grid)
                grid_json=json.loads(grid)
                ref=grid_json[-1]["_ref"]
                print(ref)
                logging.info("get option for ip")
                response = ib_NIOS.wapi_request('GET',object_type=ref+"?_return_fields=option",grid_vip=config.grid_vip)
                print(response)
                assert re.search(r'agent.link-selection',response)
                print("Test Case 15 Execution Completed")
                                
            @pytest.mark.run(order=16)
            def test_16_requesting_ipv4_lease_with_server_id(self):
                logging.info("Perform dras command")
                dras_cmd = 'sudo /import/qaddi/API_Automation/WAPI_PyTest/suites/RFE_6874/dras/dras -i'+str(config.grid_vip)+' '+'-n 1 -x  s=10.0.0.1 '
                dras_cmd1 = os.system(dras_cmd)
                print (dras_cmd1)
                sleep(20)
                grid =  ib_NIOS.wapi_request('GET', object_type="lease",grid_vip=config.grid_vip)
                #print(grid)
                grid_json=json.loads(grid)
                ref=grid_json[-1]["_ref"]
                print(ref)
                logging.info("get option for ip")
                response = ib_NIOS.wapi_request('GET',object_type=ref+"?_return_fields=option",grid_vip=config.grid_vip)
                print(response)
                assert re.search(r'agent.server-id-override',response)
                print("Test Case 16 Execution Completed")
               
            @pytest.mark.run(order=17)
            def test_17_create_ipv4_fixed_addree(self):
                logging.info("Create an ipv4 network default network view")
                data = { "ipv4addr": "10.0.0.3","mac": "ff:ee:dd:cc:bb:aa","network_view": "default"}
                response = ib_NIOS.wapi_request('POST', object_type="fixedaddress", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                read  = re.search(r'201',response)
                for read in  response:
                    assert True
                print("Created the fixed address ")
                logging.info("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 17 Execution Completed")
    
            @pytest.mark.run(order=18)
            def test_18_requesting_ipv4_lease_with_Exact_mac_address(self):
                logging.info("Perform dras command")
                dras_cmd = 'sudo /import/qaddi/API_Automation/WAPI_PyTest/suites/RFE_6874/dras/dras -i'+str(config.grid_vip)+' '+'-n 1 -x l=10.0.0.0 -a ff:ee:dd:cc:bb:aa'
                dras_cmd1 = os.system(dras_cmd)
                print (dras_cmd1)
                sleep(20)
                print("Test Case 18 Execution Completed")

            @pytest.mark.run(order=19)
            def test_19_Validating_ipv4_lease_with_Exact_mac_address(self):
                grid =  ib_NIOS.wapi_request('GET', object_type="lease",grid_vip=config.grid_vip)
                #print(grid)
                grid_json=json.loads(grid)
                ref=grid_json[-1]["_ref"]
                print(ref)
                logging.info("get option for ip")
                response = ib_NIOS.wapi_request('GET',object_type=ref+"?_return_fields=option",grid_vip=config.grid_vip)
                print(response)
                assert re.search(r'agent.link-selection',response)
                print("Test Case 19 Execution Completed")
                
                

            @pytest.mark.run(order=20)
            def test_20_create_fixed_address(self):
                logging.info("Create an ipv4 network default network view")
                data = { "ipv4addr": "10.0.0.2","mac": "aa:bb:cc:dd:ee:ff","network_view": "default"}
                response = ib_NIOS.wapi_request('POST', object_type="fixedaddress", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                read  = re.search(r'201',response)
                for read in  response:
                      assert True
                print("Created the fixed address ")
                logging.info("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 20 Execution Completed")  
            
            @pytest.mark.run(order=21)
            def test_21_requesting_ipv4_lease_with_Exact_mac_address(self):
                logging.info("Perform dras command")
                dras_cmd = 'sudo /import/qaddi/API_Automation/WAPI_PyTest/suites/RFE_6874/dras/dras -i'+str(config.grid_vip)+' '+'-n 1 -x s=10.0.0.1 -a aa:bb:cc:dd:ee:ff'
                dras_cmd1 = os.system(dras_cmd)
                print (dras_cmd1)
                sleep(10)
                print("Test Case 21 Execution Completed")

            @pytest.mark.run(order=22)
            def test_22_Validating_ipv4_lease_with_Exact_mac_address(self):
                grid =  ib_NIOS.wapi_request('GET', object_type="lease",grid_vip=config.grid_vip)
                #print(grid)
                grid_json=json.loads(grid)
                ref=grid_json[-1]["_ref"]
                print(ref)
                logging.info("get option for ip")
                response = ib_NIOS.wapi_request('GET',object_type=ref+"?_return_fields=option",grid_vip=config.grid_vip)
                print(response)
                assert re.search(r'agent.server-id-override',response)
                print("Test Case 22 Execution Completed")            
                

            @pytest.mark.run(order=23)
            def test_23_requesting_ipv4_lease_and_overriding_with_Exact_mac_address(self):
                logging.info("Perform dras command")
                dras_cmd = 'sudo /import/qaddi/API_Automation/WAPI_PyTest/suites/RFE_6874/dras/dras -i'+str(config.grid_vip)+' '+'-n 1 -x l=10.0.0.0 -a aa:bb:cc:dd:ee:ff'
                dras_cmd1 = os.system(dras_cmd)
                print (dras_cmd1)
                sleep(10)
                print("Test Case 23 Execution Completed")

            @pytest.mark.run(order=24)
            def test_24_validating_ipv4_overriding_lease_with_Exact_mac_address(self):
                grid =  ib_NIOS.wapi_request('GET', object_type="lease",grid_vip=config.grid_vip)
                #print(grid)
                grid_json=json.loads(grid)
                ref=grid_json[-1]["_ref"]
                print(ref)
                logging.info("get option for ip")
                response = ib_NIOS.wapi_request('GET',object_type=ref+"?_return_fields=option",grid_vip=config.grid_vip)
                print(response)
                assert re.search(r'agent.link-selection',response)
                print("Test Case 24 Execution Completed")
                             
            @pytest.mark.run(order=25)
            def test_25_requesting_ipv4_lease_with_circuit_id(self):
                logging.info("Perform dras command")
                dras_cmd = 'sudo /import/qaddi/API_Automation/WAPI_PyTest/suites/RFE_6874/dras/dras -i'+str(config.grid_vip)+' '+'-n 1 -x  c=infobloxblr '
                dras_cmd1 = os.system(dras_cmd)
                print (dras_cmd1)
                sleep(20)
                grid =  ib_NIOS.wapi_request('GET', object_type="lease",grid_vip=config.grid_vip)
                #print(grid)
                grid_json=json.loads(grid)
                ref=grid_json[-1]["_ref"]
                print(ref)
                logging.info("get option for ip")
                response = ib_NIOS.wapi_request('GET',object_type=ref+"?_return_fields=option",grid_vip=config.grid_vip)
                print(response)
                assert re.search(r'agent.circuit-id',response)
                print("Test Case 25 Execution Completed")
               
            @pytest.mark.run(order=26)
            def test_26_requesting_ipv4_lease_with_Exact_remote_id(self):
                logging.info("Perform dras command")
                dras_cmd = 'sudo /import/qaddi/API_Automation/WAPI_PyTest/suites/RFE_6874/dras/dras -i'+str(config.grid_vip)+' '+'-n 1 -x  r=santaclara '
                dras_cmd1 = os.system(dras_cmd)
                print (dras_cmd1)
                sleep(20)
                grid =  ib_NIOS.wapi_request('GET', object_type="lease",grid_vip=config.grid_vip)
                #print(grid)
                grid_json=json.loads(grid)
                ref=grid_json[-1]["_ref"]
                print(ref)
                logging.info("get option for ip")
                response = ib_NIOS.wapi_request('GET',object_type=ref+"?_return_fields=option",grid_vip=config.grid_vip)
                print(response)
                assert re.search(r'agent.remote-id',response)
                print("Test Case 26 Execution Completed")
                     
            @pytest.mark.run(order=27)
            def test_27_requesting_ipv4_lease_with_Exact_prefix_lenght_two_sub_options(self):
                logging.info("Perform dras command")
                dras_cmd = 'sudo /import/qaddi/API_Automation/WAPI_PyTest/suites/RFE_6874/dras/dras -i'+str(config.grid_vip)+' '+'-n 1 -x c=infobloxblr,r=santaclara '
                dras_cmd1 = os.system(dras_cmd)
                print (dras_cmd1)
                sleep(20)
                grid =  ib_NIOS.wapi_request('GET', object_type="lease",grid_vip=config.grid_vip)
                #print(grid)
                grid_json=json.loads(grid)
                ref=grid_json[-1]["_ref"]
                print(ref)
                logging.info("get option for ip")
                response = ib_NIOS.wapi_request('GET',object_type=ref+"?_return_fields=option",grid_vip=config.grid_vip)
                print(response)
                assert re.search(r'agent.circuit-id',response)
                assert re.search(r'agent.remote-id',response)
                print("Test Case 27 Execution Completed")

            @pytest.mark.run(order=28)
            def test_28_requesting_ipv4_lease_with_Exact_prefix_lenght_two_sub_options(self):
                logging.info("Perform dras command")
                dras_cmd = 'sudo /import/qaddi/API_Automation/WAPI_PyTest/suites/RFE_6874/dras/dras -i'+str(config.grid_vip)+' '+'-n 1 -x c=infobloxblr,l=10.0.0.0 '
                dras_cmd1 = os.system(dras_cmd)
                print (dras_cmd1)
                sleep(20)
                grid =  ib_NIOS.wapi_request('GET', object_type="lease",grid_vip=config.grid_vip)
                #print(grid)
                grid_json=json.loads(grid)
                ref=grid_json[-1]["_ref"]
                print(ref)
                logging.info("get option for ip")
                response = ib_NIOS.wapi_request('GET',object_type=ref+"?_return_fields=option",grid_vip=config.grid_vip)
                print(response)
                assert re.search(r'agent.circuit-id',response)
                assert re.search(r'agent.link-selection',response)
                print("Test Case 28 Execution Completed")

            @pytest.mark.run(order=29)
            def test_29_requesting_ipv4_lease_with_Exact_prefix_lenght_two_sub_options(self):
                logging.info("Perform dras command")
                dras_cmd = 'sudo /import/qaddi/API_Automation/WAPI_PyTest/suites/RFE_6874/dras/dras -i'+str(config.grid_vip)+' '+'-n 1 -x c=infobloxblr,s=10.0.0.1 '
                dras_cmd1 = os.system(dras_cmd)
                print (dras_cmd1)
                sleep(20)
                grid =  ib_NIOS.wapi_request('GET', object_type="lease",grid_vip=config.grid_vip)
                #print(grid)
                grid_json=json.loads(grid)
                ref=grid_json[-1]["_ref"]
                print(ref)
                logging.info("get option for ip")
                response = ib_NIOS.wapi_request('GET',object_type=ref+"?_return_fields=option",grid_vip=config.grid_vip)
                print(response)
                assert re.search(r'agent.circuit-id',response)
                assert re.search(r'agent.server-id-override',response)
                print("Test Case 29 Execution Completed")

            @pytest.mark.run(order=30)
            def test_30_requesting_ipv4_lease_with_Exact_prefix_lenght_two_sub_options(self):
                logging.info("Perform dras command")
                dras_cmd = 'sudo /import/qaddi/API_Automation/WAPI_PyTest/suites/RFE_6874/dras/dras -i'+str(config.grid_vip)+' '+'-n 1 -x r=santaclara,l=10.0.0.0 '
                dras_cmd1 = os.system(dras_cmd)
                print (dras_cmd1)
                sleep(20)
                grid =  ib_NIOS.wapi_request('GET', object_type="lease",grid_vip=config.grid_vip)
                #print(grid)
                grid_json=json.loads(grid)
                ref=grid_json[-1]["_ref"]
                print(ref)
                logging.info("get option for ip")
                response = ib_NIOS.wapi_request('GET',object_type=ref+"?_return_fields=option",grid_vip=config.grid_vip)
                print(response)
                assert re.search(r'agent.remote-id',response)
                assert re.search(r'agent.link-selection',response)
                print("Test Case 30 Execution Completed")

            @pytest.mark.run(order=31)
            def test_31_requesting_ipv4_lease_with_Exact_prefix_lenght_two_sub_options(self):
                logging.info("Perform dras command")
                dras_cmd = 'sudo /import/qaddi/API_Automation/WAPI_PyTest/suites/RFE_6874/dras/dras -i'+str(config.grid_vip)+' '+'-n 1 -x r=santaclara,s=10.0.0.1 '
                dras_cmd1 = os.system(dras_cmd)
                print (dras_cmd1)
                sleep(20)
                grid =  ib_NIOS.wapi_request('GET', object_type="lease",grid_vip=config.grid_vip)
                #print(grid)
                grid_json=json.loads(grid)
                ref=grid_json[-1]["_ref"]
                print(ref)
                logging.info("get option for ip")
                response = ib_NIOS.wapi_request('GET',object_type=ref+"?_return_fields=option",grid_vip=config.grid_vip)
                print(response)
                assert re.search(r'agent.remote-id',response)
                assert re.search(r'agent.server-id-override',response)
                print("Test Case 31 Execution Completed") 

            @pytest.mark.run(order=32)
            def test_32_requesting_ipv4_lease_with_Exact_prefix_lenght_two_sub_options(self):
                logging.info("Perform dras command")
                dras_cmd = 'sudo /import/qaddi/API_Automation/WAPI_PyTest/suites/RFE_6874/dras/dras -i'+str(config.grid_vip)+' '+'-n 1 -x l=10.0.0.0,s=10.0.0.1 '
                dras_cmd1 = os.system(dras_cmd)
                print (dras_cmd1)
                sleep(20)
                grid =  ib_NIOS.wapi_request('GET', object_type="lease",grid_vip=config.grid_vip)
                #print(grid)
                grid_json=json.loads(grid)
                ref=grid_json[-1]["_ref"]
                print(ref)
                logging.info("get option for ip")
                response = ib_NIOS.wapi_request('GET',object_type=ref+"?_return_fields=option",grid_vip=config.grid_vip)
                print(response)
                assert re.search(r'agent.link-selection',response)
                assert re.search(r'agent.server-id-override',response)
                print("Test Case 32 Execution Completed")
               
            @pytest.mark.run(order=33)
            def test_33_requesting_ipv4_lease_with_Exact_prefix_lenght_three_sub_options(self):
                logging.info("Perform dras command")
                dras_cmd = 'sudo /import/qaddi/API_Automation/WAPI_PyTest/suites/RFE_6874/dras/dras -i'+str(config.grid_vip)+' '+'-n 1 -x c=infobloxblr,r=santaclara,l=10.0.0.0'
                dras_cmd1 = os.system(dras_cmd)
                print (dras_cmd1)
                sleep(20)
                grid =  ib_NIOS.wapi_request('GET', object_type="lease",grid_vip=config.grid_vip)
                #print(grid)
                grid_json=json.loads(grid)
                ref=grid_json[-1]["_ref"]
                print(ref)
                logging.info("get option for ip")
                response = ib_NIOS.wapi_request('GET',object_type=ref+"?_return_fields=option",grid_vip=config.grid_vip)
                print(response)
                assert re.search(r'agent.circuit-id',response)
                assert re.search(r'agent.remote-id',response)
                assert re.search(r'agent.link-selection',response)
                print("Test Case 33 Execution Completed")

            @pytest.mark.run(order=34)
            def test_34_requesting_ipv4_lease_with_Exact_prefix_lenght_three_sub_options(self):
                logging.info("Perform dras command")
                dras_cmd = 'sudo /import/qaddi/API_Automation/WAPI_PyTest/suites/RFE_6874/dras/dras -i'+str(config.grid_vip)+' '+'-n 1 -x c=infobloxblr,r=santaclara,s=10.0.0.1'
                dras_cmd1 = os.system(dras_cmd)
                print (dras_cmd1)
                sleep(20)
                grid =  ib_NIOS.wapi_request('GET', object_type="lease",grid_vip=config.grid_vip)
                #print(grid)
                grid_json=json.loads(grid)
                ref=grid_json[-1]["_ref"]
                print(ref)
                logging.info("get option for ip")
                response = ib_NIOS.wapi_request('GET',object_type=ref+"?_return_fields=option",grid_vip=config.grid_vip)
                print(response)
                assert re.search(r'agent.circuit-id',response)
                assert re.search(r'agent.remote-id',response)
                assert re.search(r'agent.server-id-override',response)
                print("Test Case 34 Execution Completed")

            @pytest.mark.run(order=35)
            def test_35_requesting_ipv4_lease_with_Exact_prefix_lenght_three_sub_options(self):
                logging.info("Perform dras command")
                dras_cmd = 'sudo /import/qaddi/API_Automation/WAPI_PyTest/suites/RFE_6874/dras/dras -i'+str(config.grid_vip)+' '+'-n 1 -x c=infobloxblr,l=10.0.0.0,s=10.0.0.1'
                dras_cmd1 = os.system(dras_cmd)
                print (dras_cmd1)
                sleep(20)
                grid =  ib_NIOS.wapi_request('GET', object_type="lease",grid_vip=config.grid_vip)
                #print(grid)
                grid_json=json.loads(grid)
                ref=grid_json[-1]["_ref"]
                print(ref)
                logging.info("get option for ip")
                response = ib_NIOS.wapi_request('GET',object_type=ref+"?_return_fields=option",grid_vip=config.grid_vip)
                print(response)
                assert re.search(r'agent.circuit-id',response)
                assert re.search(r'agent.link-selection',response)
                assert re.search(r'agent.server-id-override',response)
                print("Test Case 35 Execution Completed")

            @pytest.mark.run(order=36)
            def test_36_requesting_ipv4_lease_with_Exact_prefix_lenght_three_sub_options(self):
                logging.info("Perform dras command")
                dras_cmd = 'sudo /import/qaddi/API_Automation/WAPI_PyTest/suites/RFE_6874/dras/dras -i'+str(config.grid_vip)+' '+'-n 1 -x r=santaclara,l=10.0.0.0,s=10.0.0.1'
                dras_cmd1 = os.system(dras_cmd)
                print (dras_cmd1)
                sleep(20)
                grid =  ib_NIOS.wapi_request('GET', object_type="lease",grid_vip=config.grid_vip)
                #print(grid)
                grid_json=json.loads(grid)
                ref=grid_json[-1]["_ref"]
                print(ref)
                logging.info("get option for ip")
                response = ib_NIOS.wapi_request('GET',object_type=ref+"?_return_fields=option",grid_vip=config.grid_vip)
                print(response)
                assert re.search(r'agent.remote-id',response)
                assert re.search(r'agent.link-selection',response)
                assert re.search(r'agent.server-id-override',response)
                print("Test Case 36 Execution Completed")
            
            @pytest.mark.run(order=37)
            def test_37_requesting_ipv4_lease_with_Exact_prefix_lenght_four_sub_options(self):
                logging.info("Perform dras command")
                dras_cmd = 'sudo /import/qaddi/API_Automation/WAPI_PyTest/suites/RFE_6874/dras/dras -i'+str(config.grid_vip)+' '+'-n 1 -x c=infobloxblr,r=santaclara,l=10.0.0.0,s=10.0.0.1'
                dras_cmd1 = os.system(dras_cmd)
                print (dras_cmd1)
                sleep(20)
                grid =  ib_NIOS.wapi_request('GET', object_type="lease",grid_vip=config.grid_vip)
                #print(grid)
                grid_json=json.loads(grid)
                ref=grid_json[-1]["_ref"]
                print(ref)
                logging.info("get option for ip")
                response = ib_NIOS.wapi_request('GET',object_type=ref+"?_return_fields=option",grid_vip=config.grid_vip)
                print(response)
                assert re.search(r'agent.link-selection',response)
                assert re.search(r'agent.server-id-override',response)
                assert re.search(r'agent.remote-id',response)
                assert re.search(r'agent.circuit-id',response)
                print("Test Case 37 Execution Completed")


            @pytest.mark.run(order=38)
            def test_38_requesting_ipv4_lease_with_hexadecimal_two_sub_options(self):
                logging.info("Perform dras command")
                dras_cmd = 'sudo /import/qaddi/API_Automation/WAPI_PyTest/suites/RFE_6874/dras/dras -i'+str(config.grid_vip)+' '+'-n 1 -O 82:010b696e666f626c6f78626c72 -x r=santaclara '
                dras_cmd1 = os.system(dras_cmd)
                print (dras_cmd1)
                sleep(20)
                grid =  ib_NIOS.wapi_request('GET', object_type="lease",grid_vip=config.grid_vip)
                #print(grid)
                grid_json=json.loads(grid)
                ref=grid_json[-1]["_ref"]
                print(ref)
                logging.info("get option for ip")
                response = ib_NIOS.wapi_request('GET',object_type=ref+"?_return_fields=option",grid_vip=config.grid_vip)
                print(response)
                assert re.search(r'agent.circuit-id',response)
                assert re.search(r'agent.remote-id',response)
                print("Test Case 38 Execution Completed")

            @pytest.mark.run(order=39)
            def test_39_requesting_ipv4_lease_with_hexadecimal_two_sub_options(self):
               logging.info("Perform dras command")
               dras_cmd = 'sudo /import/qaddi/API_Automation/WAPI_PyTest/suites/RFE_6874/dras/dras -i'+str(config.grid_vip)+' '+'-n 1 -x c=infobloxblr -O 82:020a73616e7461636c617261'
               dras_cmd1 = os.system(dras_cmd)
               print (dras_cmd1)
               sleep(20)
               grid =  ib_NIOS.wapi_request('GET', object_type="lease",grid_vip=config.grid_vip)
               #print(grid)
               grid_json=json.loads(grid)
               ref=grid_json[-1]["_ref"]
               print(ref)
               logging.info("get option for ip")
               response = ib_NIOS.wapi_request('GET',object_type=ref+"?_return_fields=option",grid_vip=config.grid_vip)
               print(response)
               assert re.search(r'agent.circuit-id',response)
               assert re.search(r'agent.remote-id',response)
               print("Test Case 39 Execution Completed")

            @pytest.mark.run(order=40)
            def test_40_requesting_ipv4_lease_with_hexadecimal_string(self):
               logging.info("Perform dras command")
               dras_cmd = 'sudo /import/qaddi/API_Automation/WAPI_PyTest/suites/RFE_6874/dras/dras -i'+str(config.grid_vip)+' '+'-n 1 -O 82:010b696e666f626c6f78626c72 '
               dras_cmd1 = os.system(dras_cmd)
               print (dras_cmd1)
               sleep(20)
               grid =  ib_NIOS.wapi_request('GET', object_type="lease",grid_vip=config.grid_vip)
               #print(grid)
               grid_json=json.loads(grid)
               ref=grid_json[-1]["_ref"]
               print(ref)
               logging.info("get option for ip")
               response = ib_NIOS.wapi_request('GET',object_type=ref+"?_return_fields=option",grid_vip=config.grid_vip)
               print(response)
               assert re.search(r'agent.circuit-id',response)
               print("Test Case 40 Execution Completed")

            @pytest.mark.run(order=41)
            def test_41_requesting_ipv4_lease_with_hexadecimal_string(self):
               logging.info("Perform dras command")
               dras_cmd = 'sudo /import/qaddi/API_Automation/WAPI_PyTest/suites/RFE_6874/dras/dras -i'+str(config.grid_vip)+' '+'-n 1 -O 82:020a73616e7461636c617261 '
               dras_cmd1 = os.system(dras_cmd)
               print (dras_cmd1)
               sleep(20)
               grid =  ib_NIOS.wapi_request('GET', object_type="lease",grid_vip=config.grid_vip)
               #print(grid)
               grid_json=json.loads(grid)
               ref=grid_json[-1]["_ref"]
               print(ref)
               logging.info("get option for ip")
               response = ib_NIOS.wapi_request('GET',object_type=ref+"?_return_fields=option",grid_vip=config.grid_vip)
               print(response)
               assert re.search(r'agent.remote-id',response)
               print("Test Case 41 Execution Completed")

            @pytest.mark.run(order=42)
            def test_42_requesting_ipv4_lease_with_hexadecimal_strings(self):
               logging.info("Perform dras command")
               dras_cmd = 'sudo /import/qaddi/API_Automation/WAPI_PyTest/suites/RFE_6874/dras/dras -i'+str(config.grid_vip)+' '+'-n 1 -O 82:010b696e666f626c6f78626c72 -O 82:020a73616e7461636c617261 '
               dras_cmd1 = os.system(dras_cmd)
               print (dras_cmd1)
               sleep(20)
               grid =  ib_NIOS.wapi_request('GET', object_type="lease",grid_vip=config.grid_vip)
               #print(grid)
               grid_json=json.loads(grid)
               ref=grid_json[-1]["_ref"]
               print(ref)
               logging.info("get option for ip")
               response = ib_NIOS.wapi_request('GET',object_type=ref+"?_return_fields=option",grid_vip=config.grid_vip)
               print(response)
               assert re.search(r'agent.circuit-id',response)
               assert re.search(r'agent.remote-id',response)
               print("Test Case 42 Execution Completed")
            
                








                

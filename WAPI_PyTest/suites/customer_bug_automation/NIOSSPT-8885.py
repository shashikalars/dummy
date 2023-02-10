__author__ = "Prasad K"
__email__  = "pkondisetty@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master                                                                      #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415)                                      #
########################################################################################

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
#import pexpect
#from log_capture import log_action as log
#from log_validation import log_validation as logv

class Network(unittest.TestCase):
      @pytest.mark.run(order=1)
      def test_01_create_IPv4_network(self):
          logging.info("Create an ipv4 network in default network view")
          data = {"network": "10.0.0.0/8","network_view": "default","members":[{"_struct": "dhcpmember","ipv4addr":config.grid_vip}]}
          response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data), grid_vip=config.grid_vip)
          print(response)
          print("Created the ipv4network 10.0.0.0/8 in default view")
          logging.info("Created the ipv4network 10.0.0.0/8 in default view")
          logging.info("Restart DHCP Services")
          grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
          ref = json.loads(grid)[0]['_ref']
          data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
          request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
          sleep(20) #wait for 20 secs for the member to get started
          response = ib_NIOS.wapi_request('GET', object_type="network",grid_vip=config.grid_vip)
          print(response)
          if ("10.0.0.0/8" in response):
                assert True
          else:
                assert False
          print("Test Case 1 Execution Completed")
                            
                       
      @pytest.mark.run(order=2)
      def test_02_create_IPv4_Range(self):
           logging.info("Create an IPv4 range in network")
           #data = {"network":"10.0.0.0/8","start_addr":"10.0.0.10","end_addr":"10.0.0.100","network_view": "default","member": {"_struct": "dhcpmember","ipv4addr": config.grid_vip,"name": config.grid_fqdn}}
           data = {"network":"10.0.0.0/8","start_addr":"10.0.0.10","end_addr":"10.0.0.100","network_view": "default","member": {"_struct": "dhcpmember","ipv4addr": config.grid_vip}}
           response = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(data), grid_vip=config.grid_vip)
           print (response)
           print("Created the ipv4 prefix range with bits 24  in default view")
           logging.info("Created the ipv4 prefix range with bits 24  in default view")
           logging.info("Restart DHCP Services")
           grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
           ref = json.loads(grid)[0]['_ref']
           data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
           request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
           sleep(20) #wait for 20 secs for the member to get started
           response = ib_NIOS.wapi_request('GET', object_type="range", grid_vip=config.grid_vip)
           response=eval(response)
           print(response)
           if (response[0].get('start_addr') == "10.0.0.10" and response[0].get('end_addr') == "10.0.0.100"):
                   assert True
           else:
                   assert False
           print("Test Case 2 Execution Completed")                    
                   
      @pytest.mark.run(order=3)
      def test_03_create_IPv4_network(self):
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
          print("Test Case 3 Execution Completed")              

      @pytest.mark.run(order=4)
      def test_04_start_IPv4_DHCP_service(self):
          logging.info("start the ipv4 service")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          logging.info(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print (ref1)
          data = {"enable_dhcp":True,}
          response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
          print(response)
          sleep(10)
          print("Test Case 4 Execution Completed")


      @pytest.mark.run(order=5)
      def test_05_Creating_the_auth_zone_in_default_dns_view(self):
          logging.info("validating the inherited values of logic_filter_rules with network")
          data = {"fqdn": "infoblox.com","view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data), grid_vip=config.grid_vip)
          print(response)
          print("Test Case 5 Executuion Completed")

  
      @pytest.mark.run(order=6)        
      def test_06_Create_IPV4_networks(self):
          data ={"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "20.0.0.2","mac": "aa:bb:cc:dd:ee:ff"}], "name": "bug.infoblox.com","view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
          logging.info(response)
          read  = re.search(r'201',response)
          for read in  response:
                 assert True
	  logging.info("Restart DHCP Services")
          grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
          ref = json.loads(grid)[0]['_ref']
          data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
          request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
          sleep(20) #wait for 20 secs for the member to get started
          print("Test Case 6 Execution Completed")
            
      @pytest.mark.run(order=7)
      def test_07_delete_IPv4_network(self):
          logging.info("Get Network List")
          grid =  ib_NIOS.wapi_request('GET', object_type="network",grid_vip=config.grid_vip)
          print(grid)
          res = json.loads(grid)
          for i in res:
             if i["network"]=="20.0.0.0/8":
                 ref=i["_ref"]
          print (ref)
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
          print("Test Case 7 Execution Completed")   
                                            
                 
      @pytest.mark.run(order=8)
      def test_08_enable_immediate_fa_configuration(self):
          logging.info("enabling immediate fa configuration")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          logging.info(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print (ref1)
          data = {"immediate_fa_configuration": True}
          response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
          print(response)
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
          dras_cmd = 'sudo dras/dras -i'+str(config.grid_vip)+' '+'-n 1 -a aa:bb:cc:dd:ee:ff'
          dras_cmd1 = os.system(dras_cmd)
          print (dras_cmd1)
          sleep(10)
          logging.info("Validate Syslog afer perform lease operation")
          sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -40 /var/log/syslog "'
          out1 = commands.getoutput(sys_log_validation)
          logging.info(out1)
          #assert re.search(r'infoblox_find_host_by_haddr',out1)
          if ("infoblox_find_host_by_haddr" in out1):
                   assert False
          else:
                   assert True
          print("Test Case 9 Execution Completed")
      @pytest.mark.run(order=10)
      def test_10_cleanup(self):
          print("cleanup section")
          res = ib_NIOS.wapi_request('GET',object_type='network?network=10.0.0.0/8')
          res = json.loads(res)
          zone_ref=res[0]['_ref']
          response=ib_NIOS.wapi_request('DELETE', object_type=zone_ref)
          print(response)

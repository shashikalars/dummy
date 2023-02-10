__author__ = "Siva Krishna"
__email__  = "krishnas@infoblox.com"

####################################################
#  Grid Set up required:                           #
#  1. Grid Master + 2 Grid Members                 #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415)  #
#  3. Need to perform SGU
####################################################

import re
import config
import pexpect
import pytest
import sys
import unittest
import logging
import subprocess
import os
import json
import ib_utils.ib_NIOS as ib_NIOS
import commands
import json, ast
import requests
import subprocess
import ib_utils.log_capture as log_capture
from  ib_utils.log_capture import log_action as log
from  ib_utils.log_validation import log_validation as logv
import time
from time import sleep
import pexpect
from paramiko import client
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as comm_util
global ref1,ref2,ref3,ref4,ref5,ref6

class Network(unittest.TestCase):
	@pytest.mark.run(order=1)
	def test_01_start_IPv4_DHCP_service_Member1(self):
    	    logging.info("start the ipv4 service")
    	    get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
   	    logging.info(get_ref)
    	    res = json.loads(get_ref)
    	    ref1 = json.loads(get_ref)[1]['_ref']
    	    ref1=ref1+"?_return_fields=enable_dhcp"
   	    print ("==========================",ref1)
    	    member_dhcp_data=ib_NIOS.wapi_request('GET',object_type=ref1)
	    print ("---------------------------",member_dhcp_data)
   	    data = {"enable_dhcp":True}
	    response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
   	    print(response)
	
	@pytest.mark.run(order=2)	
	def test_02_start_IPv4_DHCP_service_Member2(self):
            logging.info("start the ipv4 service")
            get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
            logging.info(get_ref)
            res = json.loads(get_ref)
            ref1 = json.loads(get_ref)[2]['_ref']
            ref1=ref1+"?_return_fields=enable_dhcp"
            print ("==========================",ref1)
            member_dhcp_data=ib_NIOS.wapi_request('GET',object_type=ref1)
            print ("---------------------------",member_dhcp_data)
            data = {"enable_dhcp":True}
            response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
            print(response)

	@pytest.mark.run(order=3)
        def test_03_Create_IPv4_network(self):
	    logging.info("Create an ipv4 network default network view and with out Extensible attributes of Subscriber services")
            network_data = {"network": "10.0.0.0/8","network_view": "default","members":[{"_struct": "dhcpmember","ipv4addr":config.grid_member1_vip}]}
            response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(network_data), grid_vip=config.grid_vip)
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
            logging.info("Wait for 15 sec.,")
            sleep(15)
            new_data =  ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
            new_data=json.loads(new_data)
            print ("result of adding ipv4 network",new_data)
            sleep(20) #wait for 20 secs for the member to get started
            if (new_data[0]['network']==network_data['network']):
                assert True
                print("Test Case 03 Execution Completed")
            else:
                assert False
                print ("Test Case 03 Execution Failed")
	@pytest.mark.run(order=11)
    	def test_04_create_IPv4_Range(self):
            sleep(5)
            logging.info("Create an IPv4 range in defaultnetwork view")
            network_data = {"network":"10.0.0.0/8","start_addr":"10.0.0.10","end_addr":"10.0.0.100","network_view": "default","member":{"_struct":"dhcpmember","ipv4addr":config.grid_member1_vip}}
            response = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(network_data), grid_vip=config.grid_vip)
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
            new_data =  ib_NIOS.wapi_request('GET', object_type="range", grid_vip=config.grid_vip)
            new_data=json.loads(new_data)
            sleep(20) #wait for 20 secs for the member to get started
            if (new_data[0]['network']==network_data['network']):
                assert True
                print("Test Case 04 Execution Completed")
            else:
                assert False
                print ("Test Case 04 Execution Failed")

	@pytest.mark.run(order=5)	
	def test_05_show_upgrade_history(self):
    	   logging.info(" show upgrade_history")
    	   for i in range(10):
       	       hostname = config.grid_vip
               response = os.system("ping -c 1 " + hostname)
               if response == 0:
            	  pingstatus = "Network Active"
                  child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
                  child.logfile=sys.stdout
            	  child.expect('password:')
         	  child.sendline('infoblox')
            	  child.expect('Infoblox >')
            	  child.sendline('show version')
           	  child.expect('Infoblox >')
           	  child.sendline('show upgrade_history')
          	  child.expect('Infoblox >')
                  upgrade=child.before
          	  print(upgrade)
          	  upgrade=upgrade.replace('\n',' ').replace('\r',' ')
          	  upgrade=re.findall(r'Upgraded to: \d\.\d\.\d-\d{6}',upgrade)
          	  print type(upgrade),upgrade
           	  if (upgrade !=[]):
                      assert True
            	  else:
                      assert False
            	  break
           else:
              sleep(300)


	@pytest.mark.run(order=6)
        def test_06_looking_for_apply_struct(self):
            logging.info("Perform dras command")
            log("start","/var/log/syslog",config.grid_vip)
            dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_member1_vip)+' '+'-n 1'
            dras_cmd1 = os.system(dras_cmd)
            print (dras_cmd1)
            sleep(10)
            log("stop","/var/log/syslog",config.grid_vip)
            check=commands.getoutput(" grep -cw \"dbobj_apply_struct_xform_for_object(): invalid argument\" /tmp/"+str(config.grid_vip)+"_infoblox*")
            #print (type(check))
            if (int(check)==0):
                print("segfault not found")
                assert True
            else:
                assert False
            sleep(1)
            print("Test Case 06 Execution Completed")

	@pytest.mark.run(order=7)
	def test_07_cleanup(self):
	   get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
            logging.info(get_ref)
            res = json.loads(get_ref)
            ref1 = json.loads(get_ref)[1]['_ref']
            ref1=ref1+"?_return_fields=enable_dhcp"
            print ("==========================",ref1)
            member_dhcp_data=ib_NIOS.wapi_request('GET',object_type=ref1)
            print ("---------------------------",member_dhcp_data)
            data = {"enable_dhcp":False}
            response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
            print(response)
	    
 	    get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
            logging.info(get_ref)
            res = json.loads(get_ref)
            ref1 = json.loads(get_ref)[2]['_ref']
            ref1=ref1+"?_return_fields=enable_dhcp"
            print ("==========================",ref1)
            member_dhcp_data=ib_NIOS.wapi_request('GET',object_type=ref1)
            print ("---------------------------",member_dhcp_data)
            data = {"enable_dhcp":False}
            response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
            print(response)
	    
            get_ref = ib_NIOS.wapi_request('GET', object_type="dtc:server", grid_vip=config.grid_vip)
            for ref in json.loads(get_ref):
                response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
             
           	print(response)
                    
            	if type(response) == tuple:
                        
                	if response[0]==400 or response[0]==401:
                            
                    		assert False
                	else:
                    		assert True

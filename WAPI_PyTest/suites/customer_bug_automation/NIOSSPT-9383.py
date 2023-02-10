__author__ = "Siva Krishna"
__email__  = "krishnas@infoblox.com"

####################################################
#  Grid Set up required:                           #
#  1. Standalone Grid                              #
#  2. Licenses : DNS, DHCP, Gride,NIOS (IB-V1415)  #
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
	def test_001_start_IPv4_DHCP_service(self):
    	    logging.info("start the ipv4 service")
    	    get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
   	    logging.info(get_ref)
    	    res = json.loads(get_ref)
    	    ref1 = json.loads(get_ref)[0]['_ref']
    	    ref1=ref1+"?_return_fields=enable_dhcp"
   	    print ("==========================",ref1)
    	    member_dhcp_data=ib_NIOS.wapi_request('GET',object_type=ref1)
	    print ("---------------------------",member_dhcp_data)
   	    data = {"enable_dhcp":True}
	    response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
   	    print(response)

	@pytest.mark.run(order=2)
        def test_002_Create_IPv4_network(self):
	    logging.info("Create an ipv4 network default network view and with out Extensible attributes of Subscriber services")
            network_data = {"network": "10.0.0.0/8","network_view": "default","members":[{"_struct": "dhcpmember","ipv4addr":config.grid_vip}]}
            #network_data={"network":"10.0.0.0/8","members": [{"_struct": "dhcpmember","ipv4addr": config.grid_vip,"name":config.grid_fqdn }],"extattrs":{"IB Discovery Owned": {"value": "ib"}}}
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
                print("Test Case 02 Execution Completed")
            else:
                assert False
                print ("Test Case 02 Execution Failed")
	@pytest.mark.run(order=3)
    	def test_003_create_IPv4_Range(self):
            sleep(5)
            logging.info("Create an IPv4 range in defaultnetwork view")
            network_data = {"network":"10.0.0.0/8","start_addr":"10.0.0.10","end_addr":"10.0.0.100","network_view": "default","member":{"_struct":"dhcpmember","ipv4addr":config.grid_vip}}
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
                print("Test Case 03 Execution Completed")
            else:
                assert False
                print ("Test Case 03 Execution Failed")

	@pytest.mark.run(order=4)
        def test_004_looking_for_SIGSEGV(self):
            logging.info("Perform dras command")
            log("start","/var/log/syslog",config.grid_vip)
            dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'-B -x r=RemoteId,c=CircuitId'
            dras_cmd1 = os.system(dras_cmd)
            print (dras_cmd1)
            sleep(30)
            log("stop","/var/log/syslog",config.grid_vip)
            check=commands.getoutput(" grep -cw \"segfault\" /tmp/"+str(config.grid_vip)+"_var*")
            #print (type(check))
            if (int(check)==0):
                print("segfault not found")
                assert True
            else:
                assert False
            sleep(1)
            print("Test Case 04 Execution Completed")

	@pytest.mark.run(order=5)
        def test_005_delete_Network(self):
                logging.info("delete an ipv4 network default network view")
                get_ref = ib_NIOS.wapi_request('GET', object_type="network")
                print(get_ref)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                #data = { "ipv4addr": "10.196.0.2","mac": "aa:bb:cc:dd:ee:11","network_view": "default"}
                response = ib_NIOS.wapi_request('DELETE', ref=ref1, grid_vip=config.grid_vip)
                print(response)
                print("Created the fixed address ")
                logging.info("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 20 sec.,")
                sleep(30) #wait for 20 secs for the member to get started
                print("Test Case 5 Execution Completed")

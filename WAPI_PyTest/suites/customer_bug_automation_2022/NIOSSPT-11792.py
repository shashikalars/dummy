#!/usr/bin/env python

__author__ = "Prasad K"
__email__  = "pkondisetty@infoblox.com"
__NIOSSPT_11792__ = 'WAPI call returning 500 server error when adding multiple zone associations in one call'
########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master with member                                                          #
#  2. Licenses : DNS, DHCP, Grid, NIOS                                                 #
########################################################################################

import re
import sys
import config
import pytest
import unittest
import os
import os.path
from os.path import join
import json
import pexpect
import requests
import urllib3
import commands
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util
import paramiko
import time
from datetime import datetime, timedelta

import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util
import ib_utils.log_capture as log_capture
from  ib_utils.log_capture import log_action as log
from  ib_utils.log_validation import log_validation as logv

class NIOSSPT_11792(unittest.TestCase):


    	@pytest.mark.run(order=1)
	def test_01_Add_Network_10_0_0_0_24(self):
        	print("\n***************************************************")
        	print("* TC 3:Add network 10.0.0.0/24                     *")
	        print("***************************************************")
	        data = {"network": "10.0.0.0/24","network_view": "default","members": [{"_struct": "dhcpmember","ipv4addr": config.grid_vip}]}
        	response = ib_NIOS.wapi_request('POST', object_type='network', fields=json.dumps(data))
        	print(response)
        	if bool(re.match("\"network*.*10.0.0.0/24/default",str(response))):
                	print("Network 10.0.0.0/24 creation successful")
	        else:
        		print("Network 10.0.0.0/24 creation unsuccessful")
                	assert False
		print("Test Case 01 Execution Completed")


    	@pytest.mark.run(order=2)
    	def test_02_Add_150_Authoritative_zones_with_member_assigned(self):
        	print("\n*********************************************************")
	        print("* TC 2: Adding 150 Authoritative zones with member assignement *")
        	print("***************************************************")
		for i in range(1,151):
        		data={"fqdn":"test"+str(i)+".com","view":"default","grid_primary":[{"name": config.grid_fqdn,"stealth": False}]}
		        response=ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data))
        		print(response)
			if bool(re.match("\"zone_auth*.*test"+str(i)+".com",str(response))):
				print("Zone test"+str(i)+".com creation successful")
			else:
				print("Zone test"+str(i)+".com creation unsuccessful")
				assert False
		print("Test Case 02 Execution Completed")


        @pytest.mark.run(order=03)
        def test_03_Associate_150_Authoritative_zones_to_Network(self):
		print("\n******************************************************")
		print("* TC 3: Associating 150 authoritative zones to network *")
		print("\n******************************************************")
		get_ref =ib_NIOS.wapi_request('GET',"network",grid_vip=config.grid_vip)
		print(get_ref)
		print("\n")
		ref = json.loads(get_ref)[0]['_ref']
		data = []		
		for i in range(1,151):
			data1 = {'fqdn': 'test'+str(i)+'.com','is_default': False,'view': 'default'}
			data.append(data1)
		data = {"zone_associations": data}
		print(data)
		response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
		print("\n")
	        print(response)
                if bool(re.match("\"network*.*default",str(response))):
                	print("Zone associations to Network success")
                else:
                        print("Zone associations to Network unsuccess")
                        assert False
		print("Test Case 03 Execution Completed")


        @pytest.mark.run(order=04)
        def test_04_Validate_associated_150_Authoritative_zones_to_Network(self):
                print("\n******************************************************")
                print("* TC 4: Validating associated 150 authoritative zones to network *")
                print("\n******************************************************")
                get_ref =ib_NIOS.wapi_request('GET',"network",grid_vip=config.grid_vip)
                print(get_ref)
		ref = json.loads(get_ref)[0]['_ref']
		response = ib_NIOS.wapi_request('GET',ref=ref+"?_return_fields=zone_associations",grid_vip=config.grid_vip)
		print(response)
		for i in range(1,151):
			data = '"fqdn": '+'"test'+str(i)+'.com"'
			if data in response:
				assert True
				print('"test'+str(i)+'.com" zone is associated to network')
			else:
				assert False
		print("Test Case 04 Execution Completed")

###############
## Clean UP ###
###############

        @pytest.mark.run(order=05)
        def test_05_Delete_added_150_Authoritative_zones(self):
		print("\n**********************************************")
                print("* TC 5: Deleting added 150 authoritative zones *")
                print("\n**********************************************")
		for i in range(1,151):
			get_ref =ib_NIOS.wapi_request('GET',"zone_auth?fqdn=test"+str(i)+".com",grid_vip=config.grid_vip)
	                print(get_ref)
			ref = json.loads(get_ref)[0]['_ref']
			delete_zone = ib_NIOS.wapi_request('DELETE',object_type = ref,grid_vip=config.grid_vip)
			print(delete_zone)
			if bool(re.match("\"zone_auth*.*test"+str(i)+".com",str(delete_zone))):
				print("Zone test"+str(i)+".com deleted successful")
			else:
				print("Zone test"+str(i)+".com deleted unsuccessful")
				assert False
		print("Test Case 05 Execution Completed")

        @pytest.mark.run(order=06)
        def test_06_Validate_associated_authoritative_zones_to_Network_should_be_deleted(self):
                print("\n******************************************************")
                print("* TC 6: Validating deleted associated authoritative zones to network *")
                print("\n******************************************************")
                get_ref =ib_NIOS.wapi_request('GET',"network",grid_vip=config.grid_vip)
                print(get_ref)
		ref = json.loads(get_ref)[0]['_ref']
		response = ib_NIOS.wapi_request('GET',ref=ref+"?_return_fields=zone_associations",grid_vip=config.grid_vip)
	        print(response)
		data = '"zone_associations": []'
		if data in response:
			assert True
		else:
			assert False
		print("Test Case 06 Execution Completed")


        @pytest.mark.run(order=07)
        def test_07_Delete_added_Network(self):
                print("\n***********************************")
                print("* TC 7: Deleting added IPv4 Network *")
                print("\n***********************************")
            	get_ref =ib_NIOS.wapi_request('GET',"network?network=10.0.0.0/24",grid_vip=config.grid_vip)
                print(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
		print(ref)
                delete_network = ib_NIOS.wapi_request('DELETE',ref=ref,grid_vip=config.grid_vip)
                print(delete_network)
		if bool(re.match("\"network*.*10.0.0.0/24/default",str(delete_network))):
			print("Network 10.0.0.0/24 deleted successful")
		else:
			print("Network 10.0.0.0/24 deleted unsuccessful")
			assert False
		print("Test Case 07 Execution Completed")

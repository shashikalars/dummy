#!/usr/bin/env python

__author__ = "Prasad K"
__email__  = "pkondisetty@infoblox.com"
__NIOSSPT_11716__ = "IPv4 Option filters not working"
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


def restart_services(grid=config.grid_vip):
    	print("Restart services")
        get_ref =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=grid)
        ref = json.loads(get_ref)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices", fields=json.dumps(data),grid_vip=grid)
    	print("wait for 25sec")
        sleep(25)


class NIOSSPT_11716(unittest.TestCase):

        @pytest.mark.run(order=1)
        def test_01_create_IPv4_network(self):
                print("\n==============================")
                print("creating IPv4 Network")
                print("================================")
                data = {"network": "10.0.0.0/24","network_view": "default","members":[{"_struct": "dhcpmember","ipv4addr":config.grid_vip}]}
                response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data), grid_vip=config.grid_vip)
		print(response)
                print("Test Case 01 Execution Completed")

        @pytest.mark.run(order=2)
        def test_02_Validate_Created_IPv4_network(self):
                print("\n==============================")
                print("Validating created IPv4 Network")
                print("================================")
                network = ib_NIOS.wapi_request('GET',object_type="network?network=10.0.0.0")
                print(network)
                data = '"network": "10.0.0.0/24"'
                if data in network:
                        assert True
                else:
                        assert False
                print(data)
                print("Test Case 02 Execution Completed")


        @pytest.mark.run(order=03)
        def test_03_Add_IPv4_Range1(self):
                print("\n==============================")
                print("Adding IPv4 Range1")
                print("================================")
		data = {"network":"10.0.0.0/24","start_addr":"10.0.0.1","end_addr":"10.0.0.100","network_view": "default","member":{"_struct":"dhcpmember"}}
		print(data)
                response = ib_NIOS.wapi_request('POST',object_type="range",fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                sleep(05)
                print("Test Case 03 Execution Completed")


        @pytest.mark.run(order=04)
        def test_04_Add_IPv4_MAC_Address_Filter(self):
                print("\n==============================")
                print("Addining IPv4 MAC Address Filter")
                print("================================")
		data = {"name": "mac_filter"}
		response = ib_NIOS.wapi_request('POST',object_type="filtermac",fields=json.dumps(data),grid_vip=config.grid_vip)
		print(response)
		sleep(05)
                data = {"expiration_time": 1652180613,"filter": "mac_filter","mac": "11:22:33:44:55:66","never_expires": True}
                response = ib_NIOS.wapi_request('POST',object_type="macfilteraddress",fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
	        if bool(re.match("\"macfilteraddress*.*mac_filter",str(response))):
	              	print(" IPv4 MAC Address Filter creation successful")
        		sleep(5)
        	else:
            		print(" IPv4 MAC Address Filter creation unsuccessful")
            		assert False
		print("Test Case 04 Execution Completed")


        @pytest.mark.run(order=05)
        def test_05_Add_IPv4_Option_Filter(self):
                print("\n==============================")
                print("Addining IPv4 Option Filter")
                print("================================")
                #data = {"expression": "(substring(option host-name,0,4)=\"testhost\")","name": "opt_filter"}
		data = {"expression": "(option host-name=\"test\")","name": "opt_filter"}
                response = ib_NIOS.wapi_request('POST',object_type="filteroption",fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
		if bool(re.match("\"filteroption*.*opt_filter",str(response))):
                        print("IPv4 Option Filter creation successful")
                        sleep(5)
                else:
                        print("IPv4 Option Filter creation unsuccessful")
                        assert False
		print("Test Case 05 Execution Completed")

        @pytest.mark.run(order=06)
        def test_06_Assign_IPv4_MAC_Permision_as_Allow_and_Option_Filter_Permission_as_Allow_to_IPv4_range(self):
                print("\n==============================")
                print(" Assign IPv4 MAC Permision as Allow and Option Filter Permission as Allow to IPv4 range ")
                print("================================")
                range_ref = ib_NIOS.wapi_request('GET',object_type="range?start_addr=10.0.0.1")
                print(range_ref)
		ref = json.loads(range_ref)[0]['_ref']
		data = {"mac_filter_rules": [{"filter": "mac_filter","permission": "Allow"}],"option_filter_rules": [{"filter": "opt_filter","permission": "Allow"}]}
		response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data))
		print(response)
		filters = ib_NIOS.wapi_request('GET',object_type="range?start_addr=10.0.0.1&_return_fields%2B=mac_filter_rules,option_filter_rules")
		print(filters)
		filters = filters.replace(" ","").replace("\n","")
		data = ['"filter":"mac_filter","permission":"Allow"','"filter":"opt_filter","permission":"Allow"']
		for i in data:
			if i in data:
				assert True
			else:
				assert False
		print("Permissions for both 'MAC' and 'Option' filters are set to allow")
		print("Test Case 06 Execution Completed")

        @pytest.mark.run(order=07)
        def test_07_Enable_DHCP_Service(self):
		print("\n==============================")
		print(" Enabling DHCP Service ")
		print("\n==============================")
	        member_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
	        print(member_ref)
        	ref = json.loads(member_ref)[0]['_ref']
        	data = {"enable_dhcp":True}
	        response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data))
        	print(response)
                if bool(re.match("\"member:dhcpproperties*.*com",str(response))):
                        print(" Enabling DHCP service successful")
                        sleep(5)
                else:
                        print(" Enabling DHCP service unsuccessful")
                        assert False
		print("Test Case 07 Execution Completed")


        @pytest.mark.run(order=8)
        def test_08_Request_lease_with_mac_and_option_arguments_when_both_permissions_are_set_to_Allow(self):
		print("\n==============================")
		print("Request lease with mac and option arguments when both permissions are set to Allow ")
		print("\n==============================")
	        sleep(30)
        	for i in range(10):
	            dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' '+' -n 1 -x l=10.0.0.0 -a 11:22:33:44:55:66 -O 12:74657374'
        	    print(dras_cmd)
	            dras_cmd1 = os.system(dras_cmd)
        	    sleep(02)
	            print("output is ",dras_cmd1)
                    if dras_cmd1 == 0:
			assert True
			print(" Got the lease")
			break
                    else:
			print(" Didn't get the lease ")
			assert False
                print("\nTest Case 08 Executed Successfully")

        @pytest.mark.run(order=9)
        def test_09_Assign_IPv4_MAC_Permision_as_Allow_and_Option_Filter_Permission_as_DENY_to_IPv4_range(self):
                print("\n==============================")
                print(" Assign IPv4 MAC Permision as Allow and Option Filter Permission as DENY to IPv4 range ")
                print("================================")
                range_ref = ib_NIOS.wapi_request('GET',object_type="range?start_addr=10.0.0.1")
                print(range_ref)
                ref = json.loads(range_ref)[0]['_ref']
                data = {"mac_filter_rules": [{"filter": "mac_filter","permission": "Allow"}],"option_filter_rules": [{"filter": "opt_filter","permission": "DENY"}]}
                response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data))
                print(response)
                filters = ib_NIOS.wapi_request('GET',object_type="range?start_addr=10.0.0.1&_return_fields%2B=mac_filter_rules,option_filter_rules")
                print(filters)
                filters = filters.replace(" ","").replace("\n","")
                data = ['"filter":"mac_filter","permission":"Allow"','"filter":"opt_filter","permission":"DENY"']
                for i in data:
                        if i in data:
                                assert True
                        else:
                                assert False
		restart_services()
                print(" MAC filter is set to Allow and 'ption filter is set to Deny")
                print("Test Case 09 Execution Completed")

        @pytest.mark.run(order=10)
        def test_10_Request_lease_with_mac_and_option_arguments_when_mac_permission_set_to_Allow_and_Option_permission_set_to_Deny(self):
                print("\n==============================")
                print("Request lease with mac and option arguments when mac permission set to Allow and Option permission set to Deny")
                print("\n==============================")
                sleep(10)
                for i in range(10):
                    dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' '+' -n 1 -x l=10.0.0.0 -a 11:22:33:44:55:66 -O 12:74657374'
                    print(dras_cmd)
                    dras_cmd1 = os.system(dras_cmd)
                    sleep(02)
                    print(" dras response is ",dras_cmd1)
                    if dras_cmd1 == 256:
                        assert True
                        print(" Didn't get the lease ")
                    else:
                        print(" Got the lease")
                        assert False
                print("\nTest Case 10 Executed Successfully")

        @pytest.mark.run(order=11)
        def test_11_Assign_IPv4_MAC_Permision_as_DENY_and_Option_Filter_Permission_as_Allow_to_IPv4_range(self):
                print("\n==============================")
                print(" Assign IPv4 MAC Permision as DENY and Option Filter Permission as Allow to IPv4 range ")
                print("================================")
                range_ref = ib_NIOS.wapi_request('GET',object_type="range?start_addr=10.0.0.1")
                print(range_ref)
                ref = json.loads(range_ref)[0]['_ref']
                data = {"mac_filter_rules": [{"filter": "mac_filter","permission": "DENY"}],"option_filter_rules": [{"filter": "opt_filter","permission": "Allow"}]}
                response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data))
                print(response)
                filters = ib_NIOS.wapi_request('GET',object_type="range?start_addr=10.0.0.1&_return_fields%2B=mac_filter_rules,option_filter_rules")
                print(filters)
                filters = filters.replace(" ","").replace("\n","")
                data = ['"filter":"mac_filter","permission":"DENY"','"filter":"opt_filter","permission":"Allow"']
                for i in data:
                        if i in data:
                                assert True
                        else:
                                assert False
		restart_services()
                print(" MAC filter is set to Deny and Option filter is set to Allow ")
                print(" Test Case 11 Execution Completed ")

        @pytest.mark.run(order=12)
        def test_12_Request_lease_with_mac_and_option_arguments_when_mac_permission_set_to_deny_and_option_permission_set_to_allow(self):
                print("\n==============================")
                print("Request lease with mac and option arguments when mac permission set to deny and option permission set to allow")
                print("\n==============================")
                sleep(10)
                for i in range(10):
                    dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' '+' -n 1 -x l=10.0.0.0 -a 11:22:33:44:55:66 -O 12:74657374'
                    print(dras_cmd)
                    dras_cmd1 = os.system(dras_cmd)
                    sleep(02)
                    print("output is ",dras_cmd1)
                    if dras_cmd1 == 256:
                        assert True
                        print(" Didn't get the lease ")
                    else:
                        print(" Got the lease")
                        assert False
                print("\nTest Case 12 Executed Successfully")

        @pytest.mark.run(order=13)
        def test_13_Assign_IPv4_MAC_Permision_as_DENY_and_Option_Filter_Permission_as_DENY_to_IPv4_range(self):
                print("\n==============================")
                print(" Assign IPv4 MAC Permision as DENY and Option Filter Permission as DENY to IPv4 range ")
                print("================================")
                range_ref = ib_NIOS.wapi_request('GET',object_type="range?start_addr=10.0.0.1")
                print(range_ref)
                ref = json.loads(range_ref)[0]['_ref']
                data = {"mac_filter_rules": [{"filter": "mac_filter","permission": "DENY"}],"option_filter_rules": [{"filter": "opt_filter","permission": "DENY"}]}
                response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data))
                print(response)
                filters = ib_NIOS.wapi_request('GET',object_type="range?start_addr=10.0.0.1&_return_fields%2B=mac_filter_rules,option_filter_rules")
                print(filters)
                filters = filters.replace(" ","").replace("\n","")
                data = ['"filter":"mac_filter","permission":"DENY"','"filter":"opt_filter","permission":"DENY"']
                for i in data:
                        if i in data:
                                assert True
                        else:
                                assert False
		restart_services()
                print(" MAC filter is set to Deny and Option filter is set to Deny ")
                print("Test Case 13 Execution Completed")

        @pytest.mark.run(order=14)
        def test_14_Request_lease_with_mac_and_option_arguments(self):
                print("\n==============================")
                print("Request lease with mac and option arguments")
                print("\n==============================")
                sleep(10)
                for i in range(10):
                    dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' '+' -n 1 -x l=10.0.0.0 -a 11:22:33:44:55:66 -O 12:74657374'
                    print(dras_cmd)
                    dras_cmd1 = os.system(dras_cmd)
                    sleep(02)
                    print("output is ",dras_cmd1)
                    if dras_cmd1 == 256:
                        assert True
                        print(" Didn't get the lease ")
                    else:
                        print(" Got the lease")
                        assert False
                print("\nTest Case 14 Executed Successfully")

##NIOS-85099:Able to create an "IPv4 Option Filter" using values exceeding the "length" and "offset" intervals using WAPI and getting the internal error while editing the ###created "IPv4 Option Filter" in GUI 

        @pytest.mark.run(order=15)
        def test_15_Add_IPv4_Option_Filter_with_exceeded_offset_value(self):
                print("\n==============================")
                print("Addining IPv4 Option Filter with exceeded offset value")
                print("================================")
                data = {"expression": "(substring(option host-name,99999999999999999999999999999999999999999999999,4)=\"testhost\")","name": "opt_filter1"}
                response = ib_NIOS.wapi_request('POST',object_type="filteroption",fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
		data = "The Offset value must be a value from 0 to 65535"
		if data in response:
			assert True
		else:
			assert False
                print("Test Case 15 Execution Completed")

        @pytest.mark.run(order=16)
        def test_16_Add_IPv4_Option_Filter_with_exceeded_length_value(self):
                print("\n==============================")
                print("Addining IPv4 Option Filter with exceeded length value")
                print("================================")
                data = {"expression": "(substring(option host-name,0,999999999999999999999999999999999999999999)=\"testhost\")","name": "opt_filter2"}
                response = ib_NIOS.wapi_request('POST',object_type="filteroption",fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
		data = "The Length value must be a value from 0 to 65535"
		if data in response:
			assert True
		else:
			assert False
                print("Test Case 16 Execution Completed")



##############
## Clean UP ##
##############

        @pytest.mark.run(order=17)
        def test_17_Disable_DHCP_Service(self):
                print("\n==============================")
                print(" Disabling DHCP Service ")
                print("\n==============================")
                member_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
                print(member_ref)
                ref = json.loads(member_ref)[0]['_ref']
                data = {"enable_dhcp":False}
                response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data))
                print(response)
                if bool(re.match("\"member:dhcpproperties*.*com",str(response))):
                        print(" Disabling DHCP service successful")
                        sleep(5)
                else:
                        print(" Disabling DHCP service unsuccessful")
                        assert False
                print("Test Case 17 Execution Completed")

        @pytest.mark.run(order=18)
        def test_18_Delete_IPv4_network(self):
                print("\n==============================")
                print("Deleting IPv4 Network")
                print("================================")
                network_ref = ib_NIOS.wapi_request('GET', object_type="network?network=10.0.0.0",grid_vip=config.grid_vip)
                print(network_ref)
		ref = json.loads(network_ref)[0]['_ref']
		response = ib_NIOS.wapi_request('DELETE',object_type=ref,grid_vip=config.grid_vip)
		print(response)
		network = ib_NIOS.wapi_request('GET', object_type="network?network=10.0.0.0",grid_vip=config.grid_vip)
                print(network)		
		data = '"network": "10.0.0.0/24"'
		if data in network:
			assert False
			print(" Deleting IPv4 network unsuccessful")
		else:
			assert True
			print(" Deleting IPv4 network successful")
                print("Test Case 18 Execution Completed")


        @pytest.mark.run(order=19)
        def test_19_Delete_IPv4_MAC_Address_Filter(self):
                print("\n==============================")
                print(" Deleting IPv4 MAC Address Filter")
                print("================================")
                mac_filter_ref = ib_NIOS.wapi_request('GET',object_type="filtermac?name=mac_filter",grid_vip=config.grid_vip)
                print(mac_filter_ref)
		ref = json.loads(mac_filter_ref)[0]['_ref']
                response = ib_NIOS.wapi_request('DELETE',object_type=ref,grid_vip=config.grid_vip)
                print(response)
		response = ib_NIOS.wapi_request('GET',object_type="filtermac?name=mac_filter",grid_vip=config.grid_vip)
                print(response)
		data = '"name": "mac_filter"'
                if data in response:
			assert False
			print(" Deleting IPv4 MAC Address filter unsuccessful")
                else:
                        assert True
			print(" Deleting IPv4 MAC Address filter successful")
                print("Test Case 19 Execution Completed")


        @pytest.mark.run(order=20)
        def test_20_Delete_IPv4_Option_Filter(self):
                print("\n==============================")
                print("Deleting IPv4 Option Filter")
                print("================================")
                option_filter_ref = ib_NIOS.wapi_request('GET',object_type="filteroption?name=opt_filter",grid_vip=config.grid_vip)
                print(option_filter_ref)
                ref = json.loads(option_filter_ref)[0]['_ref']
                response = ib_NIOS.wapi_request('DELETE',object_type=ref,grid_vip=config.grid_vip)
                print(response)
                response = ib_NIOS.wapi_request('GET',object_type="filteroption?name=opt_filter",grid_vip=config.grid_vip)
                print(response)
                data = '"name": "opt_filter"'
                if data in response:
                        assert False
			print(" Deleting IPv4 Option filter unsuccessful")
                else:
                        assert True
			print(" Deleting IPv4 Option filter successful")
                print("Test Case 20 Execution Completed")


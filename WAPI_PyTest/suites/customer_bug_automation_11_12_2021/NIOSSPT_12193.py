#!/usr/bin/env python

__author__  = "Prasad K"
__email__   = "pkondisetty@infoblox.com"
__NIOSSPT__ = '12193'
########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master with member                                                                      #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415)                                      #
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

class NIOSSPT_12193(unittest.TestCase):

	
        @pytest.mark.run(order=01)
        def test_01_Create_failover_association_with_two_members(self):
                print("\n==========================================")
                print("Create failover association with two members")
                print("============================================\n")
                data = {"name": "DHCPFO","primary": config.grid_member2_fqdn,"primary_server_type": "GRID","secondary": config.grid_member3_fqdn,"secondary_server_type": "GRID"}
                response = ib_NIOS.wapi_request('POST',object_type="dhcpfailover", fields=json.dumps(data))
                print(response)
		sleep(05)
                print("Test Case 001 Execution Completed")

        @pytest.mark.run(order=02)
        def test_02_Validate_created_failover_association(self):
                print("\n==========================================")
                print("Validating created failover association")
                print("============================================\n")
		grid =  ib_NIOS.wapi_request('GET', object_type="dhcpfailover?name=DHCPFO&_return_fields%2B=primary_state,secondary_state&_return_as_object=1",grid_vip=config.grid_vip)
		print(grid)
		date = ['"name": "DHCPFO"','"primary_state": "UNKNOWN"','"secondary_state": "UNKNOWN"']
		for i in date:
			if i in grid:
				assert True
				print(i)
			else:
				assert False
		print("Test Case 02 Execution Completed")

        @pytest.mark.run(order=03)
        def test_03_create_IPv4_network(self):
                print("\n==============================")
                print("creating IPv4 Network")
                print("================================")
                data = {"members": [{"_struct": "dhcpmember","name": config.grid_member2_fqdn},{"_struct": "dhcpmember","name": config.grid_member3_fqdn}],"network": "10.0.0.0/24","network_view": "default"}
	        response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
		sleep(05)
                print("Test Case 03 Execution Completed")

        @pytest.mark.run(order=04)
        def test_04_Validate_Created_IPv4_network_and_assigned_members(self):
                print("\n==============================")
                print("Validating created IPv4 Network")
                print("================================")
		output =ib_NIOS.wapi_request('GET',"network?network=10.0.0.0/24&_return_fields%2B=members,network&_return_as_object=1",grid_vip=config.grid_vip)
                print(output)
                data = ['"ipv4addr": "'+config.grid_member2_vip+'"','"name": "'+config.grid_member2_fqdn+'"','"ipv4addr": "'+config.grid_member3_vip+'"','"name": "'+config.grid_member3_fqdn+'"','"network": "10.0.0.0/24"']
                for i in data:
                        if i in output:
                                assert True
                                print(i)
                        else:
                                assert False
                print("Test Case 04 Execution Completed")

        @pytest.mark.run(order=05)
        def test_05_Add_IPv4_Range1(self):
                print("\n==============================")
                print("Adding IPv4 Range1")
                print("================================")
                data = {"name": "Range1","start_addr": "10.0.0.11","end_addr": "10.0.0.50"}
                response = ib_NIOS.wapi_request('POST',object_type="range",fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
		sleep(05)
                print("Test Case 05 Execution Completed")

        @pytest.mark.run(order=06)
        def test_06_Add_IPv4_Range2(self):
                print("\n==============================")
                print("Adding IPv4 Range2")
                print("================================")
                data = {"name": "Range2","start_addr": "10.0.0.51","end_addr": "10.0.0.100"}
                response = ib_NIOS.wapi_request('POST',object_type="range",fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
		sleep(05)
                print("Test Case 06 Execution Completed")

        @pytest.mark.run(order=07)
        def test_07_Validated_added_Range1_and_Range2(self):
                print("\n==============================")
                print("Validating added Range1 and Range2")
                print("================================")
		range = ib_NIOS.wapi_request('GET', object_type="range")
		print(range)
		data = ['"start_addr": "10.0.0.11"','"end_addr": "10.0.0.50"','"start_addr": "10.0.0.51"','"end_addr": "10.0.0.100"']	
		for i in data:
			if i in range:
				assert True
				print(i)
			else:
				assert False
		print("Test Case 07 Execution Completed")

        @pytest.mark.run(order=8)
        def test_08_Start_DHCP_Service(self):
                print("\n============================================")
                print("Starting DHCP Service")
                print("============================================\n")
                for i in range(0,3):
                        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties")
                        ref = json.loads(get_ref)[i]['_ref']
                        data = {"enable_dhcp": True}
                        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
                        print(response)
		print("\n")
		print("Sleep for 20Sec..")
                sleep(20)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(40) #wait for 40 secs for the member to get started
                print("Test Case 08 Execution Completed")

        @pytest.mark.run(order=9)
        def test_09_Validate_Enabled_DHCP_services_on_all_members(self):
                print("\n============================================\n")
                print("Validating enabled DHCP services on all members")
                print("\n============================================\n")
                for i in range(0,3):
                        grid =  ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
                        ref = json.loads(grid)[i]['_ref']
                        response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=enable_dhcp",grid_vip=config.grid_vip)
                        print(response)
                        data = '"enable_dhcp": true'
                        if data in response:
                                assert True
				print(data)
				print("\n")
                        else:
                                assert False
                sleep(05)
		print("Test Case 09 Execution Completed")

	@pytest.mark.run(order=10)
        def test_10_Disable_DHCP_services_on_all_members(self):
		print("\n============================================")
                print("Disabling the DHCP Services on all members")
                print("============================================\n")
		for i in range(0,3):
                        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties")
                	ref = json.loads(get_ref)[i]['_ref']
                	data = {"enable_dhcp": False}
	                response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
        	        print(response)
                print("\n")
                print("Sleep for 20Sec..")
                sleep(20)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(40)
                print("Test Case 10 Execution Completed")


        @pytest.mark.run(order=11)
        def test_11_Validate_disabled_DHCP_services_on_all_members(self):
                print("\n============================================\n")
                print("Validating disabled DHCP services on all members")
                print("\n============================================\n")
                for i in range(0,3):
			get_ref =  ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
			ref = json.loads(get_ref)[i]['_ref']
                        response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=enable_dhcp",grid_vip=config.grid_vip)
                        print(response)
                        data = '"enable_dhcp": false'
                        if data in response:
                                assert True
                                print(data)
                                print("\n")
                        else:
                                assert False
                sleep(05)
                print("Test Case 11 Execution Completed")


        @pytest.mark.run(order=12)
        def test_12_Assign_both_ranges_to_the_failover_association(self):
                print("\n============================================\n")
                print("Assigning the both ranges to the failover association")
                print("\n============================================\n")
		grid =  ib_NIOS.wapi_request('GET', object_type="range", grid_vip=config.grid_vip)
		for i in range(0,2):
			ref = json.loads(grid)[i]['_ref']
			data = {"failover_association": "DHCPFO"}
			response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
			print(response)
		print("Test Case 12 Execution Completed")


        @pytest.mark.run(order=13)
        def test_13_Validate_the_failover_association_for_Range1_and_Range2(self):
                print("\n============================================")
                print("Validating the failover association for Range1 and Range2")
                print("============================================\n")
		get_ref = ib_NIOS.wapi_request('GET', object_type="range")
		data = '"failover_association": "DHCPFO"'
                for i in range(0,2):
                        ref = json.loads(get_ref)[i]['_ref']
                        response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=failover_association",grid_vip=config.grid_vip)
                        print(response)
			if data in response:
				assert True
				print(data)
				print("\n")
			else:
				assert False
		print("Test Case 13 Execution Completed")

        @pytest.mark.run(order=14)
        def test_14_Start_DHCP_Service(self):
                print("\n============================================")
                print("Starting DHCP Service")
                print("============================================\n")
                for i in range(0,3):
                        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties")
                        ref = json.loads(get_ref)[i]['_ref']
                        data = {"enable_dhcp": True}
                        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
                        print(response)
                print("\n")
                print("Sleep for 20Sec..")
                sleep(20)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(40) #wait for 40 secs for the member to get started
                print("Test Case 14 Execution Completed")

        @pytest.mark.run(order=15)
        def test_15_Validate_Enabled_DHCP_services_on_all_members(self):
                print("\n============================================\n")
                print("Validating enabled DHCP services on all members")
                print("\n============================================\n")
                for i in range(0,3):
                        grid =  ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
                        ref = json.loads(grid)[i]['_ref']
                        response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=enable_dhcp",grid_vip=config.grid_vip)
                        print(response)
                        data = '"enable_dhcp": true'
                        if data in response:
                                assert True
                                print(data)
                                print("\n")
                        else:
                                assert False
                sleep(05)
                print("Test Case 15 Execution Completed")

        @pytest.mark.run(order=16)
        def test_16_Validate_Primary_and_Secondary_Peers_status(self):
                print("\n============================================\n")
                print("Validating Primary and Secondary peers status")
                print("\n============================================\n")
                grid =  ib_NIOS.wapi_request('GET', object_type="dhcpfailover", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=primary_state,secondary_state",grid_vip=config.grid_vip)
                print(response)
		data = ['"primary_state": "NORMAL"','"secondary_state": "NORMAL"']
		for i in data:
			if i in response:
				assert True
				print(i)
			else:
				assert False
		print("Test Case 16 Execution Completed")

        @pytest.mark.run(order=17)
        def test_17_Stop_DHCP_Service_on_all_members(self):
                print("\n============================================")
                print("Starting DHCP Service on all members")
                print("============================================\n")
                for i in range(0,3):
                        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties")
                        ref = json.loads(get_ref)[i]['_ref']
                        data = {"enable_dhcp": False}
                        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
                        print(response)
                print("\n")
                print("Sleep for 20Sec..")
                sleep(20)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 40 secs for the member to get started
                print("Test Case 17 Execution Completed")

        @pytest.mark.run(order=18)
        def test_18_Validate_Disabled_DHCP_services_on_all_members(self):
                print("\n============================================\n")
                print("Validating disabled DHCP services on all members")
                print("\n============================================\n")
                for i in range(0,3):
                        grid =  ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
                        ref = json.loads(grid)[i]['_ref']
                        response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=enable_dhcp",grid_vip=config.grid_vip)
                        print(response)
                        data = '"enable_dhcp": false'
                        if data in response:
                                assert True
                                print(data)
                                print("\n")
                        else:
                                assert False
                sleep(05)
                print("Test Case 18 Execution Completed")

        @pytest.mark.run(order=19)
        def test_19_Assign_Range2_to_the_failover_primary_member(self):
                print("\n============================================\n")
                print("Assigning Range2 to the failover primary member")
                print("\n============================================\n")
                grid =  ib_NIOS.wapi_request('GET', object_type="range", grid_vip=config.grid_vip)
		ref = json.loads(grid)[-1]['_ref']
		data = {"member": {"_struct": "dhcpmember","ipv4addr": config.grid_member2_vip,"name": config.grid_member2_fqdn}}
                response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
		print(response)
                print("Test Case 19 Execution Completed")

        @pytest.mark.run(order=20)
        def test_20_Validate_assigned_failover_primary_member_to_the_Range2(self):
                print("\n============================================\n")
                print("Validating disabl")
                print("\n============================================\n")
                grid =  ib_NIOS.wapi_request('GET',object_type="range", grid_vip=config.grid_vip)
                ref = json.loads(grid)[-1]['_ref']
		response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=member")
		print(response)
		data = ['"_struct": "dhcpmember"','"ipv4addr": "'+config.grid_member2_vip+'"','"name": "'+config.grid_member2_fqdn+'"']
		for i in data:
			if i in response:
				assert True
				print(i)
			else:
				assert False
		print("Test Case 20 Execution Completed")


        @pytest.mark.run(order=21)
        def test_21_Start_DHCP_Service(self):
                print("\n============================================")
                print("Starting DHCP Service")
                print("============================================\n")
                for i in range(0,3):
                        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties")
                        ref = json.loads(get_ref)[i]['_ref']
                        data = {"enable_dhcp": True}
                        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
                        print(response)
                print("\n")
                print("Sleep for 20Sec..")
                sleep(20)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 40 secs for the member to get started
                print("Test Case 21 Execution Completed")

        @pytest.mark.run(order=22)
        def test_22_Validate_Enabled_DHCP_services_on_all_members(self):
                print("\n============================================\n")
                print("Validating enabled DHCP services on all members")
                print("\n============================================\n")
                for i in range(0,3):
                        grid =  ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
                        ref = json.loads(grid)[i]['_ref']
                        response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=enable_dhcp",grid_vip=config.grid_vip)
                        print(response)
                        data = '"enable_dhcp": true'
                        if data in response:
                                assert True
                                print(data)
                                print("\n")
                        else:
                                assert False
                sleep(30)#Giving sleep to peers come to NORMAL state 
                print("Test Case 22 Execution Completed")

        @pytest.mark.run(order=23)
        def test_23_Validate_Primary_and_Secondary_Peers_status(self):
                print("\n============================================\n")
                print("Validating Primary and Secondary peers status")
                print("\n============================================\n")
                grid =  ib_NIOS.wapi_request('GET', object_type="dhcpfailover", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=primary_state,secondary_state",grid_vip=config.grid_vip)
                print(response)
                data = ['"primary_state": "NORMAL"','"secondary_state": "NORMAL"']
                for i in data:
                        if i in response:
                                assert True
                                print(i)
                        else:
                                assert False
                print("Test Case 23 Execution Completed")

        @pytest.mark.run(order=24)
        def test_24_Stop_DHCP_Service_on_all_members(self):
                print("\n============================================")
                print("Starting DHCP Service on all members")
                print("============================================\n")
                for i in range(0,3):
                        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties")
                        ref = json.loads(get_ref)[i]['_ref']
                        data = {"enable_dhcp": False}
                        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
                        print(response)
                print("\n")
                print("Sleep for 20Sec..")
                sleep(20)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 40 secs for the member to get started
                print("Test Case 24 Execution Completed")

        @pytest.mark.run(order=25)
        def test_25_Validate_Disabled_DHCP_services_on_all_members(self):
                print("\n============================================\n")
                print("Validating disabled DHCP services on all members")
                print("\n============================================\n")
                for i in range(0,3):
                        grid =  ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
                        ref = json.loads(grid)[i]['_ref']
                        response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=enable_dhcp",grid_vip=config.grid_vip)
                        print(response)
                        data = '"enable_dhcp": false'
                        if data in response:
                                assert True
                                print(data)
                                print("\n")
                        else:
                                assert False
                sleep(05)
                print("Test Case 25 Execution Completed")

        @pytest.mark.run(order=26)
        def test_26_Assign_Range2_back_to_the_failover_association(self):
                print("\n============================================\n")
                print("Assigning Range2 back to the failover association")
                print("\n============================================\n")
                grid =  ib_NIOS.wapi_request('GET', object_type="range", grid_vip=config.grid_vip)
                ref = json.loads(grid)[-1]['_ref']
		data = {"failover_association": "DHCPFO"}
                response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
                print(response)
                print("Test Case 26 Execution Completed")

        @pytest.mark.run(order=27)
        def test_27_Validate_assigned_failover_primary_member_to_the_Range2(self):
                print("\n============================================\n")
                print("Validating disabl")
                print("\n============================================\n")
                grid =  ib_NIOS.wapi_request('GET',object_type="range", grid_vip=config.grid_vip)
                ref = json.loads(grid)[-1]['_ref']
                response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=failover_association")
                print(response)
		data = '"failover_association": "DHCPFO"'
                if data in response:
                	assert True
                        print(data)
                        print("\n")
                else:
                        assert False
                print("Test Case 27 Execution Completed")

        @pytest.mark.run(order=28)
        def test_28_Start_DHCP_Service(self):
                print("\n============================================")
                print("Starting DHCP Service")
                print("============================================\n")
		log("start","/var/log/syslog",config.grid_member3_vip)
                for i in range(0,3):
                        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties")
                        ref = json.loads(get_ref)[i]['_ref']
                        data = {"enable_dhcp": True}
                        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
                        print(response)
                print("\n")
                print("Sleep for 20Sec..")
                sleep(40)
		log("stop","/var/log/syslog",config.grid_member3_vip)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 40 secs for the member to get started
                print("Test Case 28 Execution Completed")

        @pytest.mark.run(order=29)
        def test_29_Validate_Enabled_DHCP_services_on_all_members(self):
                print("\n============================================\n")
                print("Validating enabled DHCP services on all members")
                print("\n============================================\n")
                for i in range(0,3):
                        grid =  ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
                        ref = json.loads(grid)[i]['_ref']
                        response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=enable_dhcp",grid_vip=config.grid_vip)
                        print(response)
                        data = '"enable_dhcp": true'
                        if data in response:
                                assert True
                                print(data)
                                print("\n")
                        else:
                                assert False
                print("Test Case 29 Execution Completed")

	@pytest.mark.run(order=30)
        def test_30_validate_Expedited_recover_wait_or_recover_done_or_Both_servers_normal_messages_in_DHCPFO_secondary_failover_member_syslogs(self):
		print("\n============================================\n")
                print("Validating Expedited recover-wait or recover-done or Both servers normal messages in DHCPFO secondary failover member syslogs")
                print("\n============================================\n")
		data=['Expedited recover-wait','I move from recover-wait to recover-done','I move from recover-done to normal','Both servers normal']
		textfile = open('/tmp/'+config.grid_member3_vip+'_var_log_messages.log', 'r')
                log_validation = textfile.read()
                textfile.close()
		if data[0] in log_validation  or data[1] in log_validation  or data[2] in log_validation or data[3] in log_validation:
			assert True
		else:
			assert False
                print("Test Case 30 Execution Completed")



##############################
### Clean UP #################
##############################

        @pytest.mark.run(order=31)
        def test_31_Disable_DHCP_Service_on_all_members(self):
                print("\n============================================")
                print("Disabling DHCP Service on all members")
                print("============================================\n")
		get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties")
		data = {"enable_dhcp": False}
                for i in range(0,3):
                        ref = json.loads(get_ref)[i]['_ref']
                        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
                        print(response)
                print("\n")
                print("Sleep for 20Sec..")
                sleep(20)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 40 secs for the member to get started
                print("Test Case 31 Execution Completed")

        @pytest.mark.run(order=32)
        def test_32_Validate_Disabled_DHCP_services_on_all_members(self):
                print("\n============================================\n")
                print("Validating disabled DHCP services on all members")
                print("\n============================================\n")
                for i in range(0,3):
                        grid =  ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
                        ref = json.loads(grid)[i]['_ref']
                        response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=enable_dhcp",grid_vip=config.grid_vip)
                        print(response)
                        data = '"enable_dhcp": false'
                        if data in response:
                                assert True
                                print(data)
                                print("\n")
                        else:
                                assert False
                sleep(05)
                print("Test Case 32 Execution Completed")

        @pytest.mark.run(order=33)
        def test_33_Delete_Created_IPv4_network(self):
                print("\n==============================")
                print("Deleting created IPv4 Network")
                print("================================")
                network = ib_NIOS.wapi_request('GET',object_type="network?network=10.0.0.0/24")
                print(network)
                ref = json.loads(network)[0]['_ref']
                del_network=ib_NIOS.wapi_request('DELETE',object_type=ref)
                print(del_network)
		print("Test Case 33 Execution Completed")

        @pytest.mark.run(order=34)
        def test_34_Validate_deleted_IPv4_network(self):
                print("\n==============================")
                print("Validating deleted IPv4 Network")
                print("================================")
                output = ib_NIOS.wapi_request('GET',object_type="network?network=10.0.0.0/24",grid_vip=config.grid_vip)
                print(output)
		if '"network": "10.0.0.0/24"' not in output:
			assert True
		else:
			assert False
                print("Test Case 34 Execution Completed")


        @pytest.mark.run(order=35)
        def test_35_Delete_created_DHCPFO_failover_association(self):
                print("\n==========================================")
                print("Deleting created DHCPFO failover association")
                print("============================================\n")
                grid = ib_NIOS.wapi_request('GET', object_type="dhcpfailover?name=DHCPFO",grid_vip=config.grid_vip)
		print(grid)
		ref = json.loads(grid)[0]['_ref']
		del_dhcpfo = ib_NIOS.wapi_request('DELETE',object_type=ref)
		print(del_dhcpfo)
		print("Test Case 35 Execution Completed")

        @pytest.mark.run(order=36)
        def test_36_Validate_Deleted_DHCPFO_failover_association(self):
                print("\n==============================")
                print("Validating deleting DHCP failover association")
                print("================================")
                failover = ib_NIOS.wapi_request('GET',object_type="dhcpfailover?name=DHCPFO")
                print(failover)
		if '"name": "DHCPFO"' not in failover:
			assert True
		else:
			assert False
		print("Test Case 36 Execution Completed")	

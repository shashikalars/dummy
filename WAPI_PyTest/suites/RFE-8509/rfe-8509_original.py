#!/usr/bin/env python

__author__ = "Prasad K"
__email__  = "pkondisetty@infoblox.com"
__RFE__ = 'DNS Scavenging Ability to WhiteList IP\Subnet to Not Trigger "Last Queried" (RFE-7933)'
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
import datetime
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv

#Validating the HOST Record creation time stamp in audit logs 
def epoch(host):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('#')
        sleep(05)
	child.sendline('''grep "'''+host+'''" /infoblox/var/audit.log''')
        child.expect('#')
        output = child.before
        output = output.replace("\n","").replace("\r","")
        auditlogs = re.search('audit.log(.*)Created HostRecord', output)
        auditlogs = auditlogs.group(0)
        print("\n")
        print("\n============================================\n")
        record_host = ib_NIOS.wapi_request('GET',object_type="record:host?name="+host)
        ref = json.loads(record_host)[0]['_ref']
        ref = eval(json.dumps(ref))
        response = ib_NIOS.wapi_request('GET', ref=ref,params="?_inheritance=True&_return_fields=creation_time")
        response = json.loads(response)
        epoch_time = str(response["creation_time"])
        epoch_time = float(epoch_time)
        print("Epoch Time -->> ",epoch_time)
        #epoch_time=datetime.datetime.utcfromtimestamp(epoch_time).strftime('%Y-%m-%d %H:%M:%S')
	epoch_time=datetime.datetime.utcfromtimestamp(epoch_time).strftime('%Y-%m-%d %H:%M')
        print("Epoch Time to UTC -->> ",epoch_time)
        if epoch_time in auditlogs:
                assert True
                print("\n")
                print("Epoch Time of "+host+" Matched with Audit log time stamp")
		print("\n")
        else:
                print("\n")
                print("Epoch Time of "+host+" is Not Matched with Audit log time stamp")
		print("\n")
                assert False
        return host


class PenTest(unittest.TestCase):

	        
        @pytest.mark.run(order=0)
        def test_000_Make_normal_member_as_Grid_Master_Candidate(self):
		print("\n==============================")
                print("Make normal member as Grid Master Candidate")
                print("================================")
                response = ib_NIOS.wapi_request('GET',object_type="member")
                print(response)
                ref = json.loads(response)[-1]['_ref']
                print(ref)
		data = {"master_candidate": True}
                output = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data))
                print(output)
                sleep(30)
		response = ib_NIOS.wapi_request('GET',object_type="member")
                print(response)
                ref = json.loads(response)[-1]['_ref']
                print(ref)
		output = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=master_candidate")
		print(output)
		data = '"master_candidate": true'
		if data in output:
			assert True	
		else:
			assert False
		print("Test Case 000 Execution Completed")

        @pytest.mark.run(order=1)
        def test_001_Add_Authoritative_zone(self):
                print("\n============================================\n")
                print("Create Authoritative Zone")
                print("\n============================================\n")
                data = {"fqdn": "test.com","grid_primary": [{"name":config.grid_fqdn,"stealth":False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                print(response)
                sleep(03)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20sec,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 01 Execution Completed")

        @pytest.mark.run(order=2)
        def test_002_Validate_addition_of_Authoritative_zone(self):
                print("\n============================================\n")
                print("Validating addition of authoritative zone")
                print("\n============================================\n")
                get_temp = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=test.com",grid_vip=config.grid_vip)
                print(get_temp)
                data = '"fqdn": "test.com"'
                if data in get_temp:
                    assert True
                else:
                    assert False
                print(data)
                print("\n")
                print("Test Case 02 Execution Completed")
	
        @pytest.mark.run(order=3)
        def test_003_create_IPv4_network(self):
		print("\n==============================")
                print("creating IPv4 Network")
                print("================================")
                data = {"network": "10.0.0.0/24","network_view": "default","members":[{"_struct": "dhcpmember","ipv4addr":config.grid_vip}]}
                response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data), grid_vip=config.grid_vip)
		print("\n===================")
                print("Restart DHCP Services")
		print("\n===================")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 03 Execution Completed")
		
        @pytest.mark.run(order=4)
        def test_004_Validate_Created_IPv4_network(self):
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
		print("Test Case 04 Execution Completed")
	
        @pytest.mark.run(order=5)
        def test_005_create_IPv6_network_with_members_assignment(self):
        	print("\n==============================")
            	print("Validating created IPv4 Network")
            	print("================================")
		global ipv6_network
                ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
                ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
		print("ipv6_network is",ipv6_network)
            	data = {"network": ipv6_network+"::/64","network_view": "default","members": [{"_struct": "dhcpmember","ipv6addr": config.grid1_ipv6_ip,"name": config.grid_fqdn}]}
            	response = ib_NIOS.wapi_request('POST', object_type="ipv6network", fields=json.dumps(data), grid_vip=config.grid_vip)
            	print(response)
            	sleep(05)
          	print("Test Case 05 Execution Completed")

		
        @pytest.mark.run(order=6)
        def test_006_Validate_Created_IPv6_network_and_assigned_members(self):
		print("\n==============================")
                print("Validating created IPv6 Network")
                print("================================")
                output = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=members,network",grid_vip=config.grid_vip)
                print("output",output)
		result = ['"ipv4addr": "'+config.grid_vip+'"','"name": "'+config.grid_fqdn+'"','"network": "'+ipv6_network+'::/64"']
		print(result)
		for i in result:
			if i in output:
				assert True
				print(i)
			else:
				assert False
                print("Test Case 06 Execution Completed")

        @pytest.mark.run(order=7)
        def test_007_Create_an_HOST_Record_with_dns_and_dhcp_enabled(self):
                print("\n==============================")
                print("creating HOST record with dns and dhcp enabled")
                print("================================")
                data = {"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "10.0.0.1","mac": "11:11:11:11:11:11"}],"name": "host1.test.com","configure_for_dns": True}
                response = ib_NIOS.wapi_request('POST',object_type="record:host", fields=json.dumps(data))
                print(response)
                print("Test Case 07 Execution is Completed")

        @pytest.mark.run(order=8)
        def test_008_Validate_create_HOST_Record_with_dns_and_dhcp_enable(self):
                print("\n==============================")
                print("creating HOST record with dns and dhcp enabled")
                print("================================")
                hostrecord = ib_NIOS.wapi_request('GET',object_type="record:host?name=host1.test.com")
                print(hostrecord)
		data = ['"host": "host1.test.com"','"ipv4addr": "10.0.0.1"','"mac": "11:11:11:11:11:11"']
		for i in data:
			if i in hostrecord:
				assert True
				print(i)
			else:
				assert False
                print("Test Case 08 Execution is Completed")

        @pytest.mark.run(order=9)
        def test_009_Validate_Creation_time_of_HOST_record(self):
                print("\n=====================================")
                print("Validating creation time of HOST Record")
                print("=======================================")
                response=epoch("host1.test.com")
                print("Test Case 09 Execution is Completed")


        @pytest.mark.run(order=10)
        def test_010_Disable_Authoritative_Zone(self):
                print("\n==============================")
                print("Disable Authoritative Zone")
                print("================================")
                data = {"disable": True}
		response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=test.com")
                print(response)
		ref = json.loads(response)[0]['_ref']
		response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
		print(response)
		print("\n===================")
                print("Restart DHCP Services")
                print("\n===================")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
		print("Test Case 10 Execution is Completed")

	@pytest.mark.run(order=11)
	def test_011_Validate_disabled_Authoritative_Zone(self):
		print("\n==============================")
                print("Validating disabled Authoritative Zone")
                print("================================")
		response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=test.com&_return_fields%2B=disable&_return_as_object=1")
		print(response)
		data = ['"disable": true','"fqdn": "test.com"']
		for i in data:
			if i in response:
				assert True
				print(i)
			else:
				assert False
		print("Test Case 11 Execution is Completed")

        @pytest.mark.run(order=12)
        def test_012_Create_an_HOST_Record_with_dns_and_dhcp_enabled(self):
                print("\n==============================")
                print("creating HOST record with dns and dhcp enabled")
                print("================================")
                data = {"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "10.0.0.2","mac": "22:22:22:22:22:22"}],"name": "host2.test.com","configure_for_dns": True}
                response = ib_NIOS.wapi_request('POST',object_type="record:host", fields=json.dumps(data))
                print(response)
		print("\n===================")
                print("Restart DHCP Services")
                print("===================")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 12 Execution is Completed")

        @pytest.mark.run(order=13)
        def test_013_Validate_create_HOST_Record_with_dns_and_dhcp_enable(self):
                print("\n==============================")
                print("creating HOST record with dns and dhcp enabled")
                print("================================")
                hostrecord = ib_NIOS.wapi_request('GET',object_type="record:host?name=host2.test.com")
                print(hostrecord)
                data = ['"host": "host2.test.com"','"ipv4addr": "10.0.0.2"','"mac": "22:22:22:22:22:22"']
                for i in data:
                        if i in hostrecord:
                                assert True
                                print(i)
                        else:
                                assert False
                print("Test Case 13 Execution is Completed")

        @pytest.mark.run(order=14)
        def test_014_Validate_Creation_time_of_HOST_record_when_the_authoritative_zone_is_disabled(self):
                print("\n=====================================")
                print("Validating creation time of HOST Record when the authoritative zone is disabled")
                print("=======================================")
                response=epoch("host2.test.com")
                print("Test Case 14 Execution is Completed")

        @pytest.mark.run(order=15)
        def test_015_Enable_the_disabled_Authoritative_Zone(self):
                print("\n==============================")
                print("Enabling the disabled authoritative Zone")
                print("================================")
                data = {"disable": False}
                response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=test.com")
                print(response)
                ref = json.loads(response)[0]['_ref']
                response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
                print(response)
                print("\n===================")
                print("Restart DHCP Services")
                print("=====================")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 15 Execution is Completed")

        @pytest.mark.run(order=16)
        def test_016_Validate_the_enabled_Authoritative_Zone(self):
                print("\n==============================")
                print("Validating the disabled Authoritative Zone")
                print("================================")
                response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=test.com&_return_fields%2B=disable&_return_as_object=1")
                print(response)
                data = ['"disable": false','"fqdn": "test.com"']
                for i in data:
                        if i in response:
                                assert True
                                print(i)
                        else:
                                assert False
                print("Test Case 16 Execution is Completed")

        @pytest.mark.run(order=17)
        def test_017_Lock_the_Authoritative_Zone(self):
                print("\n==============================")
                print("Lock the Authoritative Zone")
                print("================================")
                data = {"locked": True}
                response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=test.com")
                print(response)
                ref = json.loads(response)[0]['_ref']
                response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
                print(response)
		print("\n===================")
                print("Restart DHCP Services")
                print("=====================")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 17 Execution is Completed")

        @pytest.mark.run(order=18)
        def test_018_Validate_the_Locked_Authoritative_Zone(self):
		print("\n======================================")
                print("Validating the Locked Authoritative Zone")
                print("========================================")
                response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=test.com&_return_fields%2B=locked&_return_as_object=1")
                print(response)
                data = ['"locked": true','"fqdn": "test.com"']
		for i in data:
                	if i in response:
                        	assert True
				print(i)
                	else:
                        	assert False
		print("\n")
                print("Test Case 18 Execution is Completed")

        @pytest.mark.run(order=19)
        def test_019_Create_an_HOST_Record_with_dns_and_dhcp_enabled(self):
                print("\n==============================")
                print("creating HOST record with dns and dhcp enabled")
                print("================================")
                data = {"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "10.0.0.3","mac": "33:33:33:33:33:33"}],"name": "host3.test.com","configure_for_dns": True}
                response = ib_NIOS.wapi_request('POST',object_type="record:host", fields=json.dumps(data))
                print(response)
                print("\n===================")
                print("Restart DHCP Services")
                print("===================")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 19 Execution is Completed")

        @pytest.mark.run(order=20)
        def test_020_Validate_create_HOST_Record_with_dns_and_dhcp_enabled(self):
                print("\n==============================")
                print("creating HOST record with dns and dhcp enabled")
                print("================================")
                hostrecord = ib_NIOS.wapi_request('GET',object_type="record:host?name=host3.test.com")
                print(hostrecord)
                data = ['"host": "host3.test.com"','"ipv4addr": "10.0.0.3"','"mac": "33:33:33:33:33:33"']
                for i in data:
                        if i in hostrecord:
                                assert True
                                print(i)
                        else:
                                assert False
                print("Test Case 20 Execution is Completed")

        @pytest.mark.run(order=21)
        def test_021_Validate_Creation_time_of_HOST_record_when_the_authoritative_zone_is_locked(self):
                print("\n=====================================")
                print("Validating creation time of HOST Record when the authoritative zone is locked")
                print("=======================================")
                response=epoch("host3.test.com")
                print("Test Case 21 Execution is Completed")

        @pytest.mark.run(order=22)
        def test_022_Unlock_the_Authoritative_Zone(self):
                print("\n==============================")
                print("Unlock the Authoritative Zone")
                print("================================")
                data = {"locked": False}
                response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=test.com")
                print(response)
                ref = json.loads(response)[0]['_ref']
                response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
                print(response)
                print("\n===================")
                print("Restart DHCP Services")
                print("=====================")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 22 Execution is Completed")

        @pytest.mark.run(order=23)
        def test_023_Validate_the_Unlocked_Authoritative_Zone(self):
                print("\n======================================")
                print("Validating the Unlocked Authoritative Zone")
                print("========================================")
                response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=test.com&_return_fields%2B=locked&_return_as_object=1")
                print(response)
                data = ['"locked": false','"fqdn": "test.com"']
                for i in data:
                        if i in response:
                                assert True
                                print(i)
                        else:
                                assert False
                print("\n")
                print("Test Case 23 Execution is Completed")


	@pytest.mark.run(order=24)
        def test_024_Create_an_HOST_Record_with_dns_and_dhcp_enabled(self):
                print("\n==============================")
                print("creating HOST record with dns and dhcp enabled")
                print("================================")
                data = {"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "10.0.0.4","mac": "44:44:44:44:44:44"}],"name": "host4.test.com","configure_for_dns": True}
                response = ib_NIOS.wapi_request('POST',object_type="record:host", fields=json.dumps(data))
                print(response)
		print("\n===================")
                print("Restart DHCP Services")
                print("=====================")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 24 Execution is Completed")

        @pytest.mark.run(order=25)
        def test_025_Validate_Created_HOST_Record_with_dns_and_dhcp_enabled(self):
		print("\n==============================")
                print("validating created HOST record with dns and dhcp enabled")
                print("================================")
                response = ib_NIOS.wapi_request('GET', object_type="record:host?name=host4.test.com&_return_fields%2B=configure_for_dns&_return_as_object=1")
                print(response)
                data = ['"configure_for_dhcp": true','"host": "host4.test.com"','"ipv4addr": "10.0.0.4"','"mac": "44:44:44:44:44:44"','"view": "default"','"configure_for_dns": true']
		for i in data:
                	if i in response:
                        	assert True
				print(i)
                	else:
                        	assert False
                print("Test Case 25 Execution is Completed")

        @pytest.mark.run(order=26)
        def test_026_Validate_Creation_time_of_HOST_record_when_the_authoritative_zone_is_locked(self):
                print("\n=====================================")
                print("Validating creation time of HOST Record when the authoritative zone is locked")
                print("=======================================")
                response=epoch("host4.test.com")
                print("Test Case 26 Execution is Completed")

        @pytest.mark.run(order=27)
        def test_027_Create_an_HOST_Record_with_dns_enabled_and_dhcp_disabled(self):
                print("\n==============================")
                print("creating HOST record with dns enabled and dhcp disabled")
                print("================================")
                data = {"ipv4addrs": [{"configure_for_dhcp": False,"ipv4addr": "10.0.0.5","mac": "55:55:55:55:55:55"}],"name": "host5.test.com","configure_for_dns": True}
                response = ib_NIOS.wapi_request('POST',object_type="record:host", fields=json.dumps(data))
                print(response)
		print("\n===================")
                print("Restart DHCP Services")
                print("=====================")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 27 Execution is Completed")
	
        @pytest.mark.run(order=28)
        def test_028_Validate_Created_HOST_Record_with_dns_enabled_and_dhcp_disabled(self):
		print("\n==============================")
                print("validating created HOST record with dns enabled and dhcp disabled")
                print("================================")
                response = ib_NIOS.wapi_request('GET', object_type="record:host?name=host5.test.com&_return_fields%2B=configure_for_dns&_return_as_object=1")
                print(response)
                data = ['"configure_for_dhcp": false','"host": "host5.test.com"','"ipv4addr": "10.0.0.5"','"mac": "55:55:55:55:55:55"','"view": "default"','"configure_for_dns": true']
                for i in data:
                        if i in response:
                                assert True
                                print(i)
                        else:
                                assert False
                print("Test Case 28 Execution is Completed")

        @pytest.mark.run(order=29)
        def test_029_Validate_Creation_time_of_HOST_record_when_the_authoritative_zone_is_locked(self):
                print("\n=====================================")
                print("Validating creation time of HOST Record when the authoritative zone is locked")
                print("=======================================")
                response=epoch("host5.test.com")
                print("Test Case 29 Execution is Completed")


        @pytest.mark.run(order=30)
        def test_030_Create_an_HOST_Record_with_dns_disabled_and_dhcp_enabled(self):
                print("\n==============================")
                print("creating HOST record with dns disabled and dhcp enabled")
                print("================================")
                data = {"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "10.0.0.6","mac": "66:66:66:66:66:66"}],"name": "host6.test.com","configure_for_dns": False}
                response = ib_NIOS.wapi_request('POST',object_type="record:host", fields=json.dumps(data))
                print(response)
		print("\n===================")
                print("Restart DHCP Services")
                print("=====================")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 30 Execution is Completed")

        @pytest.mark.run(order=31)
        def test_031_Validate_Created_HOST_Record_with_dns_disabled_and_dhcp_enabled(self):
		print("\n==============================")
                print("validating created HOST record with dns disabled and dhcp enabled")
                print("================================")
                response = ib_NIOS.wapi_request('GET', object_type="record:host?name=host6.test.com&_return_fields%2B=configure_for_dns&_return_as_object=1")
                print(response)
                data = ['"configure_for_dhcp": true','"host": "host6.test.com"','"ipv4addr": "10.0.0.6"','"mac": "66:66:66:66:66:66"','view": " "','"configure_for_dns": false']
                for i in data:
                        if i in response:
                                assert True
                                print(i)
                        else:
                                assert False
                print("Test Case 31 Execution is Completed")

        @pytest.mark.run(order=32)
        def test_032_Validate_Creation_time_of_HOST_record_when_the_authoritative_zone_is_locked(self):
                print("\n=====================================")
                print("Validating creation time of HOST Record when the authoritative zone is locked")
                print("=======================================")
                response=epoch("host6.test.com")
                print("Test Case 32 Execution is Completed")


        @pytest.mark.run(order=33)
        def test_033_Create_an_HOST_Recordwith_dns_enabled_and_dhcp_disabled(self):
                print("\n==============================")
                print("creating HOST record with dns enabled and dhcp disabled")
                print("================================")
                data = {"ipv4addrs": [{"configure_for_dhcp": False,"ipv4addr": "10.0.0.7","mac": "77:77:77:77:77:77"}],"name": "host7.test.com","configure_for_dns": True}
                response = ib_NIOS.wapi_request('POST',object_type="record:host", fields=json.dumps(data))
                print(response)
		print("\n===================")
                print("Restart DHCP Services")
                print("=====================")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 33 Execution is Completed")

        @pytest.mark.run(order=34)
        def test_034_Validate_Created_HOST_Record_with_dns_enabled_and_dhcp_disabled(self):
		print("\n==============================")
                print("validating created HOST record with dns enabled and dhcp disabled")
                print("================================")
                response = ib_NIOS.wapi_request('GET', object_type="record:host?name=host7.test.com&_return_fields%2B=configure_for_dns&_return_as_object=1")
                print(response)
                data = ['"configure_for_dhcp": false','"host": "host7.test.com"','"ipv4addr": "10.0.0.7"','"mac": "77:77:77:77:77:77"','"view": "default"','"configure_for_dns": true']
                for i in data:
                        if i in response:
                                assert True
                                print(i)
                        else:
                                assert False
                print("Test Case 34 Execution is Completed")

        @pytest.mark.run(order=35)
        def test_035_Validate_Creation_time_of_HOST_record_when_the_authoritative_zone_is_locked(self):
                print("\n=====================================")
                print("Validating creation time of HOST Record when the authoritative zone is locked")
                print("=======================================")
                response=epoch("host7.test.com")
                print("Test Case 35 Execution is Completed")


        @pytest.mark.run(order=36)
        def test_036_Create_an_HOST_Record_with_dns_and_dhcp_disabled(self):
                print("\n==============================")
                print("creating HOST record with dns and dhcp disabled")
                print("================================")
                data = {"ipv4addrs": [{"configure_for_dhcp": False,"ipv4addr": "10.0.0.8","mac": "88:88:88:88:88:88"}],"name": "host8.test.com","configure_for_dns": False}
                response = ib_NIOS.wapi_request('POST',object_type="record:host", fields=json.dumps(data))
                print(response)
		print("\n===================")
                print("Restart DHCP Services")
                print("=====================")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 36 Execution is Completed")

        @pytest.mark.run(order=37)
        def test_037_Validate_Created_HOST_Record_with_dns_and_dhcp_disabled(self):
                print("\n==============================")
                print("validating created HOST record with dns and dhcp disabled")
                print("================================")
                response = ib_NIOS.wapi_request('GET', object_type="record:host?name=host8.test.com&_return_fields%2B=configure_for_dns&_return_as_object=1")
                print(response)
                data = ['"configure_for_dhcp": false','"host": "host8.test.com"','"ipv4addr": "10.0.0.8"','"mac": "88:88:88:88:88:88"','"view": " "','"configure_for_dns": false']
                for i in data:
                        if i in response:
                                assert True
                                print(i)
                        else:
                                assert False
                print("Test Case 37 Execution is Completed")

        @pytest.mark.run(order=38)
        def test_038_Validate_Creation_time_of_HOST_record_when_the_authoritative_zone_is_locked(self):
                print("\n=====================================")
                print("Validating creation time of HOST Record when the authoritative zone is locked")
                print("=======================================")
                response=epoch("host8.test.com")
                print("Test Case 38 Execution is Completed")


        @pytest.mark.run(order=39)
        def test_039_Create_Admin_Users_in_Admin_Group(self):
                print("\n============================================\n")
                print("Create Admin Users in Admin Group")
                print("============================================")
                data = {"admin_groups": ["admin-group"],"name": "admin1","password":"admin1"}
                response = ib_NIOS.wapi_request('POST', object_type="adminuser", fields=json.dumps(data))
                print(response)
                print("\n")
                sleep(10)
                print("Test Case 39 Execution Completed")

        @pytest.mark.run(order=40)
        def test_040_Validate_created_Admin_User(self):
                print("\n============================================\n")
                print(" Validate created Admin Users in Admin Group")
                print("============================================")
                response = ib_NIOS.wapi_request('GET','adminuser?name=admin1',grid_vip=config.grid_vip)
                print(response)
                sleep(05)
                response = response.replace("\n","").replace(" ","")
                data = '''"admin_groups":["admin-group"],"name":"admin1'''
                if data in response:
                        assert True
                else:
                        assert False
                print("\n")
                print(data)
                print("\n")
                print("Test Case 40 Execution Completed")

        @pytest.mark.run(order=41)
        def test_041_Validate_creation_time_of_host_record_with_another_super_user(self):
                print("\n==============================")
                print("Validating creation time of host record with non super user")
                print("================================")
                nonsuperuser=ib_NIOS.wapi_request('GET',object_type="record:host?name=host7.test.com")
                print(nonsuperuser)
                ref = json.loads(nonsuperuser)[0]['_ref']
                print(ref)
                response = ("curl -k1 -u admin1:admin1 -H Content-Type:application/json -X GET https://"+config.grid_vip+"/wapi/v"+config.wapi_version+"/"+ref+"?_return_fields=creation_time")
                print(response)
                cmd = os.popen(response).read()
                cmd = json.loads(cmd)
                cmd = cmd["creation_time"]
                print(cmd)
                if cmd == None or cmd == []:
                        assert False
                else:
                        assert True
                print("Test Case 41 Execution is Completed")

        @pytest.mark.run(order=42)
        def test_042_Create_non_super_user_group_with_only_api_access(self):
                print("\n============================================\n")
                print(" Creating non super user group with only api access ")
                print("\n============================================\n")
                data = {"access_method": ["API"],"name": "infoblox_api"}
                response = ib_NIOS.wapi_request('POST', object_type="admingroup", fields=json.dumps(data))
                print(response)
                print("\n")
                sleep(10)
                print("Test Case 42 Execution Completed")

        @pytest.mark.run(order=43)
        def test_043_Validate_created_non_super_user_group(self):
                print("\n============================================\n")
                print("Validating created non super user group")
                print("\n============================================\n")
                response = ib_NIOS.wapi_request('GET',"admingroup?name=infoblox_api&_return_fields=name,access_method",grid_vip=config.grid_vip)
                print(response)
                response = response.replace("\n","").replace(" ","")
                data = '''"access_method":["API"],"name":"infoblox_api"'''
                if data in response:
                        assert True
                else:
                        assert False
                print("\n")
                print(data)
                print("\n")
                print("Test Case 43 Execution Completed")

        @pytest.mark.run(order=44)
        def test_044_Create_Users_in_created_non_super_User_group(self):
                print("\n============================================\n")
                print("Creating users in created non super User group")
                print("\n============================================\n")
                data = {"admin_groups": ["infoblox_api"],"name": "infoblox_api1","password":"infoblox_api1"}
                response = ib_NIOS.wapi_request('POST', object_type="adminuser", fields=json.dumps(data))
                print(response)
                print("\n")
                sleep(10)
                print("Test Case 44 Execution Completed")

        @pytest.mark.run(order=45)
        def test_045_Validate_created_users_in_non_super_User_group(self):
                print("\n============================================\n")
                print("Validating created users in non super User group")
                print("\n============================================\n")
                response = ib_NIOS.wapi_request('GET','adminuser?name=infoblox_api1',grid_vip=config.grid_vip)
                print(response)
                sleep(05)
                response = response.replace("\n","").replace(" ","")
                data = '''"admin_groups":["infoblox_api"],"name":"infoblox_api1'''
                if data in response:
                        assert True
                else:
                        assert False
                print("\n")
                print(data)
                print("\n")
                print("Test Case 45 Execution Completed")

        @pytest.mark.run(order=46)
        def test_046_Validate_creation_time_of_host_record_with_other_admin_user(self):
                print("\n==============================")
                print("Validating creation time of host record with other admin user")
                print("================================")
		data = {"group": "infoblox_api","permission": "READ","resource_type": "HOST"}
		response = ib_NIOS.wapi_request('POST',object_type="permission",fields=json.dumps(data))
		print(response)
		sleep(10)
                nonsuperuser=ib_NIOS.wapi_request('GET',object_type="record:host?name=host7.test.com")
                print(nonsuperuser)
                ref = json.loads(nonsuperuser)[0]['_ref']
                print(ref)
                response = ("curl -k1 -u infoblox_api1:infoblox_api1 -H Content-Type:application/json -X GET https://"+config.grid_vip+"/wapi/v"+config.wapi_version+"/"+ref+"?_return_fields=creation_time")
                print(response)
                cmd = os.popen(response).read()
                cmd = json.loads(cmd)
                cmd = cmd["creation_time"]
                print(cmd)
                if cmd == None or cmd == []:
                        assert False
                else:
                        assert True
                print("Test Case 46 Execution is Completed")

        @pytest.mark.run(order=47)
        def test_047_SIGN_the_Authoritative_forward_mapping_zone(self):
                print("\n============================================\n")
                print("SIGN the Authoritative forward mapping zone")
                print("\n============================================\n")
                grid =  ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=test.com", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data = {"operation":"SIGN"}
                token_upload = ib_NIOS.wapi_request('POST', ref=ref,object_type="zone_auth",fields=json.dumps(data),params="?_function=dnssec_operation")
                print("\n")
                print(token_upload)
                print("\nTest Case 47 Execution Completed")

        @pytest.mark.run(order=48)
        def test_048_Validate_signed_authoritative_forward_mapping_zone(self):
                print("\n============================================\n")
                print("validating the signed authoritative forward mapping zone")
                print("\n============================================\n")
                signzone=ib_NIOS.wapi_request('GET',object_type="zone_auth?fqdn=test.com&_return_fields%2B=is_dnssec_enabled,is_dnssec_signed&_return_as_object=1", grid_vip=config.grid_vip)
                print(signzone)
                data = ['"fqdn": "test.com"','"is_dnssec_enabled": true','"is_dnssec_signed": true']
                for i in data:
                        if i in signzone:
                                assert True
                                print(i)
                        else:
                                assert False
                print("\nTest Case 48 Execution Completed")

        @pytest.mark.run(order=49)
        def test_049_Create_an_HOST_Record_with_dns_and_dhcp_enabled(self):
                print("\n==============================")
                print("creating HOST record with dns and dhcp enabled")
                print("================================")
                data = {"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "10.0.0.9","mac": "99:99:99:99:99:99"}],"name": "host9.test.com","configure_for_dns": True}
                response = ib_NIOS.wapi_request('POST',object_type="record:host", fields=json.dumps(data))
                print(response)
                print("\n===================")
                print("Restart DHCP Services")
                print("=====================")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 49 Execution is Completed")

        @pytest.mark.run(order=50)
        def test_050_Validate_Created_HOST_Record_with_dns_and_dhcp_enabled(self):
                print("\n==============================")
                print("validating created HOST record with dns and dhcp enabled")
                print("================================")
                response = ib_NIOS.wapi_request('GET', object_type="record:host?name=host9.test.com&_return_fields%2B=configure_for_dns&_return_as_object=1")
                print(response)
                data = ['"configure_for_dhcp": true','"host": "host9.test.com"','"ipv4addr": "10.0.0.9"','"mac": "99:99:99:99:99:99"','"view": "default"','"configure_for_dns": true']
                for i in data:
                        if i in response:
                                assert True
                                print(i)
                        else:
                                assert False
                print("Test Case 50 Execution is Completed")

        @pytest.mark.run(order=51)
        def test_051_Validate_Creation_time_of_HOST_record_when_the_authoritative_zone_is_signed(self):
                print("\n=====================================")
                print("Validating creation time of HOST Record when the authoritative zone is signed")
                print("=======================================")
                response=epoch("host9.test.com")
                print("Test Case 51 Execution is Completed")

        @pytest.mark.run(order=52)
        def test_052_UNSIGN_the_Authoritative_forward_mapping_zone(self):
                print("\n============================================\n")
                print("UNSIGN the Authoritative forward mapping zone")
                print("\n============================================\n")
                grid =  ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=test.com", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data = {"operation":"UNSIGN"}
                unsign = ib_NIOS.wapi_request('POST', ref=ref,object_type="zone_auth",fields=json.dumps(data),params="?_function=dnssec_operation")
                print("\n")
                print(unsign)
                print("\nTest Case 52 Execution Completed")

        @pytest.mark.run(order=53)
        def test_053_Validate_unsigned_authoritative_forward_mapping_zone(self):
                print("\n============================================\n")
                print("validating the unsigned authoritative forward mapping zone")
                print("\n============================================\n")
                unsign=ib_NIOS.wapi_request('GET',object_type="zone_auth?fqdn=test.com&_return_fields%2B=is_dnssec_enabled,is_dnssec_signed&_return_as_object=1", grid_vip=config.grid_vip)
                print(unsign)
                data = ['"fqdn": "test.com"','"is_dnssec_signed": false']
                for i in data:
                        if i in unsign:
                                assert True
                                print(i)
                        else:
                                assert False
                print("\nTest Case 53 Execution Completed")

        @pytest.mark.run(order=54)
        def test_054_Create_an_HOST_Record_with_dns_and_dhcp_enabled(self):
                print("\n==============================")
                print("creating HOST record with dns and dhcp enabled")
                print("================================")
                data = {"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "10.0.0.10","mac": "10:10:10:10:10:10"}],"name": "host10.test.com","configure_for_dns": True}
                response = ib_NIOS.wapi_request('POST',object_type="record:host", fields=json.dumps(data))
                print(response)
                print("\n===================")
                print("Restart DHCP Services")
                print("=====================")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 54 Execution is Completed")

        @pytest.mark.run(order=55)
        def test_055_Validate_Created_HOST_Record_with_dns_and_dhcp_disabled(self):
                print("\n==============================")
                print("validating created HOST record with dns and dhcp disabled")
                print("================================")
                response = ib_NIOS.wapi_request('GET', object_type="record:host?name=host10.test.com&_return_fields%2B=configure_for_dns&_return_as_object=1")
                print(response)
                data = ['"configure_for_dhcp": true','"host": "host10.test.com"','"ipv4addr": "10.0.0.10"','"mac": "10:10:10:10:10:10"','"view": "default"','"configure_for_dns": true']
                for i in data:
                        if i in response:
                                assert True
                                print(i)
                        else:
                                assert False
                print("Test Case 55 Execution is Completed")

        @pytest.mark.run(order=56)
        def test_056_Disable_HOST_Record(self):
                print("\n==============================")
                print("Disable HOST Record")
                print("================================")
                data = {"disable": True}
                response = ib_NIOS.wapi_request('GET', object_type="record:host?name=host10.test.com")
                print(response)
                ref = json.loads(response)[0]['_ref']
                response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
                print(response)
                print("Test Case 56 Execution is Completed")

        @pytest.mark.run(order=57)
        def test_057_Validate_Disabled_HOST_Record(self):
                print("\n============================================\n")
                print("validating the disabled host record")
                print("\n============================================\n")
                disablehostrecord=ib_NIOS.wapi_request('GET',object_type="record:host?name=host10.test.com&_return_fields%2B=disable&_return_as_object=1", grid_vip=config.grid_vip)
                print(disablehostrecord)
                data = ['"host": "host10.test.com"','"disable": true']
                for i in data:
                        if i in disablehostrecord:
                                assert True
                                print(i)
                        else:
                                assert False
                print("\nTest Case 57 Execution Completed")

        @pytest.mark.run(order=58)
        def test_058_Validate_Creation_time_of_HOST_record_when_the_HOST_record_is_disabled(self):
                print("\n=====================================")
                print("Validating creation time of HOST Record when the HOST record is disabled")
                print("=======================================")
                response=epoch("host10.test.com")
                print("Test Case 58 Execution is Completed")

        @pytest.mark.run(order=59)
        def test_059_Add_an_HOST_Record_with_aliases(self):
                print("\n==============================")
                print("Adding HOST record with dns and dhcp enabled")
                print("================================")
                data = {"configure_for_dns": True,"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "10.0.0.11","mac": "11:11:11:11:11:10"}],"name": "host11.test.com"}
                response = ib_NIOS.wapi_request('POST',object_type="record:host", fields=json.dumps(data))
                print(response)
                response = ib_NIOS.wapi_request('GET', object_type="record:host?name=host11.test.com")
                print(response)
                ref = json.loads(response)[0]['_ref']
                data = {"aliases": ["host121.test.com"]}
                response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data))
                print(response)
		print("\n===================")
                print("Restart DHCP Services")
                print("=====================")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 59 Execution is Completed")

        @pytest.mark.run(order=60)
        def test_060_Validate_added_host_record_with_aliases(self):
                print("\n============================================\n")
                print("validating the host record with aliases")
                print("\n============================================\n")
                aliaseshostrecord=ib_NIOS.wapi_request('GET',object_type="record:host?name=host11.test.com&_return_fields%2B=aliases&_return_as_object=1", grid_vip=config.grid_vip)
                print(aliaseshostrecord)
                aliaseshostrecord = aliaseshostrecord.replace(" ","").replace("\n","")
                data = ['"aliases":["host121.test.com"]','"host":"host11.test.com"']
                for i in data:
                        if i in aliaseshostrecord:
                                assert True
                                print(i)
                        else:
                                assert False
                print("\nTest Case 60 Execution Completed")

        @pytest.mark.run(order=61)
        def test_061_Validate_Creation_time_of_HOST_record_when_the_HOST_record_is_added_with_aliases(self):
                print("\n=====================================")
                print("Validating creation time of HOST Record when the HOST record is added with aliases")
                print("=======================================")
                response=epoch("host11.test.com")
                print("Test Case 61 Execution is Completed")

        @pytest.mark.run(order=62)
        def test_062_Add_Bulk_HOST_Record(self):
                print("\n==============================")
                print("Adding Bulk HOST record")
                print("================================")
                data = {"end_addr": "10.0.0.100","prefix": "32","start_addr": "10.0.0.1","zone": "test.com"}
                response = ib_NIOS.wapi_request('POST',object_type="bulkhost", fields=json.dumps(data))
                print(response)
                print("Test Case 62 Execution is Completed")

        @pytest.mark.run(order=63)
        def test_063_Validate_added_bulk_host_record(self):
                print("\n============================================\n")
                print("validating the bulk host record")
                print("\n============================================\n")
                bulkhostrecord=ib_NIOS.wapi_request('GET',object_type="bulkhost?prefix=32&_return_fields%2B=zone,end_addr,start_addr,prefix&_return_as_object=1",grid_vip=config.grid_vip)
                print(bulkhostrecord)
                data = ['"start_addr": "10.0.0.1"','"end_addr": "10.0.0.100"','"zone": "test.com"','"prefix": "32"']
                for i in data:
                        if i in bulkhostrecord:
                                assert True
                                print(i)
                        else:
                                assert False
                print("\nTest Case 63 Execution Completed")

        @pytest.mark.run(order=64)
        def test_064_Creation_time_object_should_not_the_support_bulk_host_record(self):
                print("\n==============================")
                print("creation time object should not support the bulk host record")
                print("================================")
                bulkhostrecord=ib_NIOS.wapi_request('GET',object_type="bulkhost?prefix=32")
                print(bulkhostrecord)
                ref = json.loads(bulkhostrecord)[0]['_ref']
                bulkhostrecord= ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=creation_time")
                print(bulkhostrecord)
                bulkhostrecord = str(bulkhostrecord)
                bulkhostrecord = bulkhostrecord.replace('\r','').replace("\'"," ")
                data = '''"text": "Unknown argument/field: \ creation_time'''
                if data in bulkhostrecord:
                        assert True
                else:
                        assert False
                print("Test Case 64 Execution is Completed")

        @pytest.mark.run(order=65)
        def test_065_Add_Authoritative_forward_mapping_subzone(self):
                print("\n============================================\n")
                print("adding authoritative forward mapping subzone")
                print("\n============================================\n")
                data = {"fqdn": "sub.test.com","view": "default","grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 65 Execution Completed")

        @pytest.mark.run(order=66)
        def test_066_Validate_added_authoritative_forward_mapping_subzone(self):
                print("\n============================================\n")
                print("adding authoritative forward mapping subzone")
                print("\n============================================\n")
                grid =  ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=sub.test.com", grid_vip=config.grid_vip)
                print(grid)
                value = '"fqdn": "sub.test.com"'
                if value in grid:
                    assert True
                else:
                    assert False
                print(value)
                sleep(5)
                print("\nTest Case 66 Execution Completed")

        @pytest.mark.run(order=67)
        def test_067_Create_an_HOST_Record_under_sub_zone_with_dns_and_dhcp_enabled(self):
                print("\n==============================")
                print("creating HOST record under sub zone with dns and dhcp enabled")
                print("================================")
                data = {"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "10.0.0.12","mac": "12:12:12:12:12:12"}],"name": "host12.sub.test.com","configure_for_dns": True}
                response = ib_NIOS.wapi_request('POST',object_type="record:host", fields=json.dumps(data))
                print(response)
                print("\n===================")
                print("Restart DHCP Services")
                print("=====================")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 67 Execution is Completed")

        @pytest.mark.run(order=68)
        def test_068_Validate_Created_HOST_Record_under_sub_zone_with_dns_and_dhcp_disabled(self):
                print("\n==============================")
                print("validating created HOST record under sub zone with dns and dhcp disabled")
                print("================================")
                response = ib_NIOS.wapi_request('GET', object_type="record:host?name=host12.sub.test.com&_return_fields%2B=configure_for_dns&_return_as_object=1")
                print(response)
                data = ['"configure_for_dhcp": true','"host": "host12.sub.test.com"','"ipv4addr": "10.0.0.12"','"mac": "12:12:12:12:12:12"','"view": "default"','"configure_for_dns": true']
                for i in data:
                        if i in response:
                                assert True
                                print(i)
                        else:
                                assert False
                print("Test Case 68 Execution is Completed")

        @pytest.mark.run(order=69)
        def test_069_Validate_Creation_time_of_HOST_record_when_the_HOST_record_is_under_subzone(self):
                print("\n=====================================")
                print("Validating creation time of HOST Record when the HOST record is under subzone")
                print("=======================================")
		response=epoch("host12.sub.test.com")
		"""
	        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
        	child.logfile=sys.stdout
	        child.expect('#')
        	sleep(05)
		child.sendline('''grep "host12.sub.test.com" /infoblox/var/audit.log''')
        	child.expect('#')
	        output = child.before
        	output = output.replace("\n","").replace("\r","")
		print(output)
	        auditlogs = re.search('audit.log(.*)Created HostRecord', output)
        	auditlogs = auditlogs.group(0)
		print(auditlogs)
	        record_host = ib_NIOS.wapi_request('GET',object_type="record:host?name=host12.sub.test.com")
        	ref = json.loads(record_host)[0]['_ref']
	        ref = eval(json.dumps(ref))
        	response = ib_NIOS.wapi_request('GET', ref=ref,params="?_inheritance=True&_return_fields=creation_time")
	        response = json.loads(response)
        	epoch_time = str(response["creation_time"])
	        epoch_time = float(epoch_time)
        	print("Epoch Time -->> ",epoch_time)
	        epoch_time=datetime.datetime.utcfromtimestamp(epoch_time).strftime('%Y-%m-%d %H:%M')
        	print("Epoch Time to UTC -->> ",epoch_time)
	        if epoch_time in auditlogs:
        	        assert True
                	print("\n")
	                print("Epoch Time of host12.sub.test.com Matched with Audit log time stamp")
        	else:
                	print("\n")
	                print("Epoch Time of host12.sub.test.com is Not Matched with Audit log time stamp")
        	        assert False
		"""
	        print("Test Case 69 Execution is Completed")

        @pytest.mark.run(order=70)
        def test_070_Add_stub_forward_mapping_zone(self):
                print("\n============================================\n")
                print("adding stub forward mapping zone")
                print("\n============================================\n")
                data = {"fqdn": "stub.test.com","stub_from": [{"address": config.grid_vip,"name": "grid"}],"view": "default"}
                response = ib_NIOS.wapi_request('POST', object_type="zone_stub",fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
		print("Wait for 20sec,")
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 70 Execution Completed")

        @pytest.mark.run(order=71)
        def test_071_Validate_added_stub_forward_mapping_zone(self):
                print("\n============================================\n")
                print("Validating added stub forward mapping zone")
                print("\n============================================\n")
                grid =  ib_NIOS.wapi_request('GET', object_type="zone_stub?fqdn=stub.test.com", grid_vip=config.grid_vip)
                print(grid)
                data = ['"fqdn": "stub.test.com"','"name": "grid"','"address": "'+config.grid_vip+'"','"view": "default"']
		for i in data:
                	if i in grid:
                    		assert True
				print(i)
                	else:
                    		assert False
                print("\nTest Case 71 Execution Completed")

        @pytest.mark.run(order=72)
        def test_072_Add_Authoritative_zone_under_stub_zone(self):
                print("\n============================================\n")
                print("Create Authoritative Zone under stub zone")
                print("\n============================================\n")
                data = {"fqdn": "auth.stub.test.com","grid_primary": [{"name":config.grid_fqdn,"stealth":False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                print(response)
		sleep(03)
		grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20sec,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 72 Execution Completed")

        @pytest.mark.run(order=73)
        def test_073_Validate_addition_of_Authoritative_zone_under_stub_zone(self):
                print("\n============================================\n")
                print("Validating addition of authoritative zone  under stub zone")
                print("\n============================================\n")
                zone_data = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=auth.stub.test.com&_return_fields%2B=grid_primary,fqdn&_return_as_object=1")
                print(zone_data)
                data = ['"fqdn": "auth.stub.test.com"','"name": "'+config.grid_fqdn+'"','"stealth": false']
		for i in data:
                	if i in zone_data:
                    		assert True
				print(i)
                	else:
                    		assert False
                print("\n")
                print("Test Case 73 Execution Completed")

        @pytest.mark.run(order=74)
        def test_074_Create_an_HOST_Record_with_dns_and_dhcp_enabled(self):
                print("\n==============================")
                print("creating HOST record with dns and dhcp enabled")
                print("================================")
                data = {"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "10.0.0.13","mac": "13:13:13:13:13:13"}],"name": "host13.auth.stub.test.com","configure_for_dns": True}
                response = ib_NIOS.wapi_request('POST',object_type="record:host", fields=json.dumps(data))
                print(response)
                print("\n===================")
                print("Restart DHCP Services")
                print("=====================")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 74 Execution is Completed")

        @pytest.mark.run(order=75)
        def test_075_Validate_Created_HOST_Record_with_dns_and_dhcp_disabled(self):
                print("\n==============================")
                print("validating created HOST record with dns and dhcp disabled")
                print("================================")
                response = ib_NIOS.wapi_request('GET', object_type="record:host?name=host13.auth.stub.test.com&_return_fields%2B=configure_for_dns&_return_as_object=1")
                print(response)
                data = ['"configure_for_dhcp": true','"host": "host13.auth.stub.test.com"','"ipv4addr": "10.0.0.13"','"mac": "13:13:13:13:13:13"','"view": "default"','"configure_for_dns": true']
                for i in data:
                        if i in response:
                                assert True
                                print(i)
                        else:
                                assert False
                print("Test Case 75 Execution is Completed")

        @pytest.mark.run(order=76)
        def test_076_Validate_Creation_time_of_HOST_record_when_the_HOST_record_is_under_stub_authoritative_zone(self):
                print("\n=====================================")
                print("Validating creation time of HOST Record when the HOST record is under stub authoritative zone")
                print("=======================================")
                response=epoch("host13.auth.stub.test.com")
                print("Test Case 76 Execution is Completed")

        @pytest.mark.run(order=77)
        def test_077_Add_Delegation_zone(self):
                print("\n==================\n")
                print("adding delegation zone")
                print("\n==================\n")
                data = {"delegate_to": [{"address": config.grid2,"name": "secondgrid"}],"fqdn": "delegation.test.com"}
                response = ib_NIOS.wapi_request('POST', object_type="zone_delegated",fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20sec,")
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 77 Execution Completed")

        @pytest.mark.run(order=78)
        def test_078_Validate_added_delegation_zone(self):
                print("\n============================================\n")
                print("Validating added delegation zone")
                print("\n============================================\n")
                grid =  ib_NIOS.wapi_request('GET', object_type="zone_delegated?fqdn=delegation.test.com", grid_vip=config.grid_vip)
                print(grid)
                data = ['"fqdn": "delegation.test.com"','"name": "secondgrid"','"address": "'+config.grid2+'"','"view": "default"']
                for i in data:
                        if i in grid:
                                assert True
                                print(i)
                        else:
                                assert False
                print("\nTest Case 78 Execution Completed")

        @pytest.mark.run(order=79)
        def test_079_Add_Authoritative_zone_under_delegation_zone(self):
                print("\n============================================\n")
                print("Create Authoritative Zone under delegation zone")
                print("\n============================================\n")
                data = {"fqdn": "auth.delegation.test.com","grid_primary": [{"name":config.grid_fqdn,"stealth":False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                print(response)
                sleep(03)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20sec,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 79 Execution Completed")

        @pytest.mark.run(order=80)
        def test_080_Validate_addition_of_Authoritative_zone_under_delegation_zone(self):
                print("\n============================================\n")
                print("Validating addition of authoritative zone  under delegation zone")
                print("\n============================================\n")
                zone_data = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=auth.delegation.test.com&_return_fields%2B=grid_primary,fqdn&_return_as_object=1")
                print(zone_data)
                data = ['"fqdn": "auth.delegation.test.com"','"name": "'+config.grid_fqdn+'"','"stealth": false']
                for i in data:
                        if i in zone_data:
                                assert True
                                print(i)
                        else:
                                assert False
                print("\n")
                print("Test Case 80 Execution Completed")

        @pytest.mark.run(order=81)
        def test_081_Create_an_HOST_Record_with_dns_and_dhcp_enabled(self):
                print("\n==============================")
                print("creating HOST record with dns and dhcp enabled")
                print("================================")
                data = {"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "10.0.0.15","mac": "15:15:15:15:15:15"}],"name": "host15.auth.delegation.test.com","configure_for_dns": True}
                response = ib_NIOS.wapi_request('POST',object_type="record:host", fields=json.dumps(data))
                print(response)
                print("\n===================")
                print("Restart DHCP Services")
                print("=====================")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 81 Execution is Completed")

        @pytest.mark.run(order=82)
        def test_082_Validate_Created_HOST_Record_with_dns_and_dhcp_enabled(self):
                print("\n==============================")
                print("validating created HOST record with dns and dhcp disabled")
                print("================================")
                response = ib_NIOS.wapi_request('GET', object_type="record:host?name=host15.auth.delegation.test.com&_return_fields%2B=configure_for_dns&_return_as_object=1")
                print(response)
                data = ['"configure_for_dhcp": true','"host": "host15.auth.delegation.test.com"','"ipv4addr": "10.0.0.15"','"mac": "15:15:15:15:15:15"','"view": "default"','"configure_for_dns": true']
                for i in data:
                        if i in response:
                                assert True
                                print(i)
                        else:
                                assert False
                print("Test Case 82 Execution is Completed")

        @pytest.mark.run(order=83)
        def test_083_Validate_Creation_time_of_HOST_record_when_the_HOST_record_is_under_stub_authoritative_zone(self):
                print("\n=====================================")
                print("Validating creation time of HOST Record when the HOST record is under stub authoritative zone")
                print("=======================================")
                response=epoch("host15.auth.delegation.test.com")
                print("Test Case 83 Execution is Completed")

        @pytest.mark.run(order=84)
        def test_084_Create_custom_dns_view(self):
                print("\n============================================\n")
                print("Create custom dns view")
                print("\n============================================\n")
                data = {"name": "custom"}
                response = ib_NIOS.wapi_request('POST', object_type="view", fields=json.dumps(data))
                print(response)
                print("Test Case 84 Execution Completed")

        @pytest.mark.run(order=85)
        def test_085_Validate_created_custom_dns_view(self):
                print("\n============================================\n")
                print("Validating created custom dns view")
                print("\n============================================\n")
                response = ib_NIOS.wapi_request('GET','view?name=custom',grid_vip=config.grid_vip)
                print(response)
		data = ['"is_default": false','"name": "custom"']
		for i in data:
			if i in response:
				assert True
				print(i)
			else:
				assert False
		print("Test Case 85 Execution Completed")

        @pytest.mark.run(order=86)
        def test_086_Add_Authoritative_zone(self):
                print("\n============================================\n")
                print("Create Authoritative Zone")
                print("\n============================================\n")
                data = {"fqdn": "test1.com","grid_primary": [{"name":config.grid_fqdn,"stealth":False}],"view": "custom"}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                print(response)
                sleep(03)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20sec,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 86 Execution Completed")

        @pytest.mark.run(order=87)
        def test_087_Validate_addition_of_Authoritative_zone_in_custom_dns_view(self):
                print("\n============================================\n")
                print("Validating addition of authoritative zone in custom dns view")
                print("\n============================================\n")
                zonedata = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=test1.com",grid_vip=config.grid_vip)
                print(zonedata)
                data = ['"fqdn": "test1.com"','view": "custom"']
		for i in data:
                	if i in zonedata:
                    		assert True
				print(i)
                	else:
                    		assert False
                print(data)
                print("\n")
                print("Test Case 87 Execution Completed")

        @pytest.mark.run(order=88)
        def test_088_Create_an_HOST_Record_with_dns_and_dhcp_enabled_in_custom_dns_view(self):
                print("\n==============================")
                print("creating HOST record with dns and dhcp enabled in custom dns view")
                print("================================")
                data = {"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "10.0.0.16","mac": "16:16:16:16:16:16"}],"name": "host16.test1.com","configure_for_dns": True,"view": "custom"}
                response = ib_NIOS.wapi_request('POST',object_type="record:host", fields=json.dumps(data))
                print(response)
                print("\n===================")
                print("Restart DHCP Services")
                print("=====================")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 88 Execution is Completed")

        @pytest.mark.run(order=89)
        def test_089_Validate_Created_HOST_Record_with_dns_and_dhcp_enabled_in_custom_dns_view(self):
                print("\n==============================")
                print("validating created HOST record with dns and dhcp enabled in custom dns view")
                print("================================")
                response = ib_NIOS.wapi_request('GET', object_type="record:host?name=host16.test1.com&_return_fields%2B=configure_for_dns&_return_as_object=1")
                print(response)
                data = ['"configure_for_dhcp": true','"host": "host16.test1.com"','"ipv4addr": "10.0.0.16"','"mac": "16:16:16:16:16:16"','"view": "custom"','"configure_for_dns": true']
                for i in data:
                        if i in response:
                                assert True
                                print(i)
                        else:
                                assert False
                print("Test Case 89 Execution is Completed")

        @pytest.mark.run(order=90)
        def test_090_Validate_Creation_time_of_HOST_record_when_the_HOST_record_is_in_custom_dns_view(self):
                print("\n=====================================")
                print("Validating creation time of HOST Record when the HOST record is in custom dns view")
                print("=======================================")
                response=epoch("host16.test1.com")
                print("Test Case 90 Execution is Completed")






###################
## ZONE Transfer ##
###################

        @pytest.mark.run(order=91)
        def test_091_Enable_Updates_nad_zone_transfer_and_recursive_query(self):
                print("\n============================================\n")
                print("Enable updates and zone transfers and recursive query")
                print("\n============================================\n")
		grid =  ib_NIOS.wapi_request('GET', object_type="grid:dns")
		ref = json.loads(grid)[0]['_ref']
                data = {"allow_recursive_query": True,"allow_transfer": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}],"allow_update": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}]}
                response = ib_NIOS.wapi_request('PUT',ref=ref,object_type="grid:dns",fields=json.dumps(data))
                print(response)
		print("\n===================")
                print("Restart DHCP Services")
                print("=====================")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started		
		print("Test Case 91 Execution is Completed")

        @pytest.mark.run(order=92)
        def test_092_Add_Authoritative_zone_in_GRID1(self):
                print("\n=================================\n")
                print("Create Authoritative Zone in GRID1")
                print("\n=================================\n")
                data = {"external_secondaries": [{"address": config.grid2,"name": "grid2","stealth": False,"use_tsig_key_name": False}],"fqdn": "zonetransfer.com","grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                print(response)
                sleep(03)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20sec,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 92 Execution Completed")

        @pytest.mark.run(order=93)
        def test_093_Create_an_HOST_Record_with_dns_and_dhcp_enabled_default_dns_view(self):
                print("\n==============================")
                print("creating HOST record with dns and dhcp enabled in default dns view")
                print("================================")
                data = {"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "10.0.0.17","mac": "17:17:17:17:17:17"}],"name": "host17.zonetransfer.com","configure_for_dns": True,"view": "default"}
                response = ib_NIOS.wapi_request('POST',object_type="record:host", fields=json.dumps(data))
                print(response)
                print("\n===================")
                print("Restart DHCP Services")
                print("=====================")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 93 Execution is Completed")

        @pytest.mark.run(order=94)
        def test_094_Validate_Created_HOST_Record_with_dns_and_dhcp_enabled_in_default_dns_view(self):
                print("\n==============================")
                print("validating created HOST record with dns and dhcp enabled in default dns view")
                print("================================")
                response = ib_NIOS.wapi_request('GET', object_type="record:host?name=host17.zonetransfer.com&_return_fields%2B=configure_for_dns&_return_as_object=1")
                print(response)
                data = ['"configure_for_dhcp": true','"host": "host17.zonetransfer.com"','"ipv4addr": "10.0.0.17"','"mac": "17:17:17:17:17:17"','"view": "default"','"configure_for_dns": true']
                for i in data:
                        if i in response:
                                assert True
                                print(i)
                        else:
                                assert False
                print("Test Case 94 Execution is Completed")

        @pytest.mark.run(order=95)
        def test_095_Validate_Creation_time_of_HOST_record_when_the_HOST_record_is_in_default_dns_view(self):
                print("\n=====================================")
                print("Validating creation time of HOST Record when the HOST record is in default dns view")
                print("=======================================")
                response=epoch("host17.zonetransfer.com")
                print("Test Case 95 Execution is Completed")

        @pytest.mark.run(order=96)
        def test_096_Add_Authoritative_zone_in_GRID2(self):
                print("\n=================================\n")
                print("Create Authoritative Zone in GRID2")
                print("\n=================================\n")
		data = {"grid_secondaries": [{"enable_preferred_primaries": False,"grid_replicate": False,"lead": False,"name": config.grid_fqdn,"preferred_primaries": [],"stealth": False}],"external_primaries": [{"address": config.grid_vip,"name": "grid2","stealth": False,"use_tsig_key_name": False}],"use_external_primary" : True,"fqdn": "zonetransfer.com"}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data),grid_vip=config.grid2)
                print(response)
                sleep(03)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid2)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid2)
                print("Wait for 20sec,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 96 Execution Completed")

        @pytest.mark.run(order=97)
        def test_097_Should_not_GET_the_HOST_Record_synced_through_zone_transfer_in_GRID2(self):
                print("\n===============================================================\n")
                print("Shouldn't GET the HOST Record synced through zone transfer in GRID2")
                print("\n===============================================================\n")
		host_record=ib_NIOS.wapi_request('GET',object_type="record:host?name=host17.zonetransfer.com",grid_vip=config.grid2)
		print(host_record)
		if host_record == '[]':
			assert True
		else:
			assert False
		sleep(100)
		print("Test Case 97 Execution Completed")


##########################
## IMPORT Zone Scenario ##
##########################

        @pytest.mark.run(order=98)
        def test_098_Enable_Add_allowed_IP_addresses_to_also_notify_option_in_Grid1(self):
                print("\n===============================================================\n")
                print("Enable Add allowed IP addresses to also notify option in Grid1")
                print("\n===============================================================\n")
		grid_dns=ib_NIOS.wapi_request('GET',object_type="grid:dns")
		ref = json.loads(grid_dns)[0]['_ref']
		data = {"copy_xfer_to_notify": True}
                dns_update=ib_NIOS.wapi_request('PUT',ref=ref,object_type="grid:dns",fields=json.dumps(data))
		print(dns_update)
		sleep(03)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20sec,")
                sleep(20) #wait for 20 secs for the member to get started
		print("Test Case 98 Execution Completed")

        @pytest.mark.run(order=99)
        def test_099_Allow_Zone_Transfer_and_enable_add_allowed_IP_addresses_to_also_notify_option_in_Grid2(self):
                print("\n===============================================================\n")
                print("Allow Zone Transfer and enable add allowed IP addresses to also notify option in Grid2")
                print("\n===============================================================\n")
                grid_dns=ib_NIOS.wapi_request('GET',object_type="grid:dns",grid_vip=config.grid2)
                ref = json.loads(grid_dns)[0]['_ref']
                data = {"copy_xfer_to_notify": True}
                dns_update=ib_NIOS.wapi_request('PUT',ref=ref,object_type="grid:dns",fields=json.dumps(data),grid_vip=config.grid2)
                print(dns_update)
		data = {"allow_transfer": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}]}
		dns_update=ib_NIOS.wapi_request('PUT',ref=ref,object_type="grid:dns",fields=json.dumps(data),grid_vip=config.grid2)
		print(dns_update)
                sleep(03)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid2)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid2)
                print("Wait for 20sec,")
                sleep(20) #wait for 20 secs for the member to get started
		print("Test Case 99 Execution Completed")

        @pytest.mark.run(order=100)
        def test_100_Add_Authoritative_forward_mapping_zone_in_Grid1(self):
                print("\n============================================\n")
                print("adding authoritative forward mapping zone in Grid1")
                print("\n============================================\n")
                data = {"fqdn": "import.com","view": "default","grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 100 Execution Completed")

        @pytest.mark.run(order=101)
        def test_101_Validate_added_authoritative_forward_mapping_zone_Grid1(self):
                print("\n============================================\n")
                print("adding authoritative forward mapping zone in Grid1")
                print("\n============================================\n")
                grid =  ib_NIOS.wapi_request('GET',"zone_auth?fqdn=import.com&_return_fields%2B=fqdn,grid_primary&_return_as_object=1", grid_vip=config.grid_vip)
                print(grid)
                data = ['"fqdn": "import.com"','"name": "'+config.grid_fqdn+'"','"view": "default"']
		for i in data:
                	if i in grid:
                    		assert True
				print(i)
                	else:
                    		assert False
                print("\nTest Case 101 Execution Completed")

        @pytest.mark.run(order=102)
        def test_102_Add_Authoritative_forward_mapping_zone_in_Grid2(self):
                print("\n============================================\n")
                print("adding authoritative forward mapping zone in Grid2")
                print("\n============================================\n")
                data = {"fqdn": "import.com","view": "default","grid_primary": [{"name": config.grid2_fqdn,"stealth": False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data),grid_vip=config.grid2)
                print(response)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid2)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid2)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 102 Execution Completed")

        @pytest.mark.run(order=103)
        def test_103_Validate_added_authoritative_forward_mapping_zone_Grid2(self):
                print("\n============================================\n")
                print("adding authoritative forward mapping zone in Grid2")
                print("\n============================================\n")
                grid =  ib_NIOS.wapi_request('GET',"zone_auth?fqdn=import.com&_return_fields%2B=fqdn,grid_primary&_return_as_object=1", grid_vip=config.grid2)
                print(grid)
                data = ['"fqdn": "import.com"','"name": "'+config.grid2_fqdn+'"','"view": "default"']
                for i in data:
                        if i in grid:
                                assert True
                                print(i)
                        else:
                                assert False
                print("\nTest Case 103 Execution Completed")

        @pytest.mark.run(order=104)
        def test_104_Create_an_HOST_Record_with_dns_and_dhcp_enabled_in_Grid2_to_import_to_Grid1_through_import_zone(self):
                print("\n==============================")
                print("creating HOST record with dns and dhcp enabled in Grid2 to import to Grid1 through import zone")
                print("================================")
                data = {"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "10.0.0.18","mac": "18:18:18:18:18:18"}],"name": "host18.import.com","configure_for_dns": True,"view": "default"}
                response = ib_NIOS.wapi_request('POST',object_type="record:host", fields=json.dumps(data),grid_vip=config.grid2)
                print(response)
                print("\n===================")
                print("Restart DHCP Services")
                print("=====================")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid2)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid2)
                print("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 104 Execution is Completed")

        @pytest.mark.run(order=105)
        def test_105_Validate_Created_HOST_Record_with_dns_and_dhcp_enabled_in_Grid2(self):
                print("\n==============================")
                print("validating created HOST record with dns and dhcp enabled in Grid2")
                print("================================")
                response = ib_NIOS.wapi_request('GET', object_type="record:host?name=host18.import.com&_return_fields%2B=configure_for_dns&_return_as_object=1",grid_vip=config.grid2)
                print(response)
                data = ['"configure_for_dhcp": true','"host": "host18.import.com"','"ipv4addr": "10.0.0.18"','"mac": "18:18:18:18:18:18"','"view": "default"','"configure_for_dns": true']
                for i in data:
                        if i in response:
                                assert True
                                print(i)
                        else:
                                assert False
                print("Test Case 105 Execution is Completed")

        @pytest.mark.run(order=106)
        def test_106_Import_zone_from_External_Grid2_to_Grid1(self):
                print("\n==============================")
                print("Import zone from External Grid2 to Grid1")
                print("================================")
		response = ib_NIOS.wapi_request('GET',object_type="zone_auth?fqdn=import.com")
		print(response)
		ref = json.loads(response)[0]['_ref']
		data = {"use_import_from":True, "import_from":config.grid2, "do_host_abstraction":True}
		output = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data))
		print(output)
		print("\n===================")
                print("Restart DHCP Services")
                print("=====================")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid2)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid2)
                print("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
		print("Test Case 106 Execution is Completed")

        @pytest.mark.run(order=107)
        def test_107_Validate_imported_HOST_Record_from_onedb_in_Grid1(self):
                print("\n=====================================")
                print("Validating imported HOST Record from onedb in Grid1")
                print("=======================================")
	        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
        	child.logfile=sys.stdout
	        child.expect('#')
        	sleep(05)
        	child.sendline('''grep "Modified AuthZone import.com" /infoblox/var/audit.log''')
	        child.expect('#')
	        auditlogs = child.before
		print(auditlogs)
		child.sendline('''/infoblox/one/bin/db_dump -silvd /tmp/ ''')	
		child.expect('#')
		child.sendline('''grep -B 10 "host18" /tmp/onedb.xml ''')
		child.expect('#')
		onedb = child.before
		onedb = onedb.replace("PROPERTY NAME","").replace("\n","").replace("\r","").replace(">","").replace("<=","").replace(" ","").replace("/","").replace('"','').replace("=","").replace("VALUE","")
		onedb = re.search('creation_timestamp(.*)creator',onedb)
                onedb = onedb.group(0)
		epoch_time = onedb.replace("creation_timestamp","").replace("creator","")
		print("\n")
		print("epoch time -->> ",epoch_time)
		epoch_time = float(epoch_time)
	        epoch_time=datetime.datetime.utcfromtimestamp(epoch_time).strftime('%Y-%m-%d %H:%M')
        	print("Epoch Time to UTC -->> ",epoch_time)
	        if epoch_time in auditlogs:
        	        assert True
                	print("\n")
	                print("Epoch Time of host18 Matched with Audit log time stamp")
        	        print("\n")
	        else:
        	        print("\n")
                	print("Epoch Time of host18 is Not Matched with Audit log time stamp")
	                print("\n")
        	        assert False
		print("Test Case 107 Execution is Completed")


####################
## IPv6 Scenarios ##
####################

        @pytest.mark.run(order=108)
        def test_108_Validate_HOST_Record_Creation_time_through_Grid1_IPv6_IP_when_the_HOST_Record_is_enabled_with_dns_and_dhcp(self):
                print("\n==============================")
                print("Validating HOST Record creation time through Grid1 IPv6 IP when the HOST Record is enabled with dns and dhcp")
                print("================================")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                sleep(05)
                child.sendline('''grep host1.test.com /infoblox/var/audit.log''')
                child.expect('#')
                output = child.before
                output = output.replace("\n","").replace("\r","")
                auditlogs = re.search('audit.log(.*)Created HostRecord',output)
                auditlogs = auditlogs.group(0)
                print("\n")
                record_host = ib_NIOS.wapi_request('GET',object_type="record:host?name=host1.test.com",grid_vip='['+config.grid1_ipv6_ip+']')
                ref = json.loads(record_host)[0]['_ref']
                ref = eval(json.dumps(ref))
                response = ib_NIOS.wapi_request('GET', ref=ref,params="?_inheritance=True&_return_fields=creation_time",grid_vip='['+config.grid1_ipv6_ip+']')
                response = json.loads(response)
                epoch_time = str(response["creation_time"])
                epoch_time = float(epoch_time)
                print("Epoch Time -->> ",epoch_time)
                epoch_time=datetime.datetime.utcfromtimestamp(epoch_time).strftime('%Y-%m-%d %H:%M')
                print("Epoch Time to UTC -->> ",epoch_time)
                if epoch_time in auditlogs:
                        assert True
                        print("\n")
                        print("Epoch Time of host1.test.com record Matched with Audit log time stamp")
                        print("\n")
                else:
                        print("\n")
                        print("Epoch Time of host1.test.com record is Not Matched with Audit log time stamp")
                        print("\n")
                        assert False
                print("Test Case 108 Execution is Completed")

        @pytest.mark.run(order=109)
        def test_109_Validate_HOST_Record_Creation_time_through_Grid1_IPv6_IP_when_the_HOST_Record_is_enabled_with_dhcp_and_disabled_with_dns(self):
                print("\n==============================")
                print("Validating HOST Record creation time through IPv6 IP when the HOST Record is enabled with dhcp and disabled with dns")
                print("================================")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                sleep(05)
                child.sendline('''grep host6.test.com /infoblox/var/audit.log''')
                child.expect('#')
                output = child.before
                output = output.replace("\n","").replace("\r","")
                auditlogs = re.search('audit.log(.*)Created HostRecord',output)
                auditlogs = auditlogs.group(0)
                print("\n")
                record_host = ib_NIOS.wapi_request('GET',object_type="record:host?name=host6.test.com",grid_vip='['+config.grid1_ipv6_ip+']')
                ref = json.loads(record_host)[0]['_ref']
                ref = eval(json.dumps(ref))
                response = ib_NIOS.wapi_request('GET', ref=ref,params="?_inheritance=True&_return_fields=creation_time",grid_vip='['+config.grid1_ipv6_ip+']')
                response = json.loads(response)
                epoch_time = str(response["creation_time"])
                epoch_time = float(epoch_time)
                print("Epoch Time -->> ",epoch_time)
                epoch_time=datetime.datetime.utcfromtimestamp(epoch_time).strftime('%Y-%m-%d %H:%M')
                print("Epoch Time to UTC -->> ",epoch_time)
                if epoch_time in auditlogs:
                        assert True
                        print("\n")
                        print("Epoch Time of host6.test.com record Matched with Audit log time stamp")
                        print("\n")
                else:
                        print("\n")
                        print("Epoch Time of host6.test.com record is Not Matched with Audit log time stamp")
                        print("\n")
                        assert False
                print("Test Case 109 Execution is Completed")

        @pytest.mark.run(order=110)
        def test_110_Validate_HOST_Record_Creation_time_through_Grid1_IPv6_IP_when_the_HOST_Record_is_under_custom_dns_view(self):
                print("\n==============================")
                print("validating HOST Record creation time through Grid1 IPv6 IP when the HOST Record is under custom dns view")
                print("================================")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                sleep(05)
                child.sendline('''grep host16.test1.com /infoblox/var/audit.log''')
                child.expect('#')
                output = child.before
                output = output.replace("\n","").replace("\r","")
                auditlogs = re.search('audit.log(.*)Created HostRecord',output)
                auditlogs = auditlogs.group(0)
                print("\n")
                record_host = ib_NIOS.wapi_request('GET',object_type="record:host?name=host16.test1.com",grid_vip='['+config.grid1_ipv6_ip+']')
                ref = json.loads(record_host)[0]['_ref']
                ref = eval(json.dumps(ref))
                response = ib_NIOS.wapi_request('GET', ref=ref,params="?_inheritance=True&_return_fields=creation_time",grid_vip='['+config.grid1_ipv6_ip+']')
                response = json.loads(response)
                epoch_time = str(response["creation_time"])
                epoch_time = float(epoch_time)
                print("Epoch Time -->> ",epoch_time)
                epoch_time=datetime.datetime.utcfromtimestamp(epoch_time).strftime('%Y-%m-%d %H:%M')
                print("Epoch Time to UTC -->> ",epoch_time)
                if epoch_time in auditlogs:
                        assert True
                        print("\n")
                        print("Epoch Time of host16.test1.com record Matched with Audit log time stamp")
                        print("\n")
                else:
                        print("\n")
                        print("Epoch Time of host16.test1.com record is Not Matched with Audit log time stamp")
                        print("\n")
                        assert False
                print("Test Case 110 Execution is Completed")

        @pytest.mark.run(order=111)
        def test_111_Create_an_HOST_Record_with_IPv6_address(self):
                print("\n====================================")
                print("creating HOST record with IPv6 Address")
                print("======================================")
                data = {"ipv6addrs": [{"configure_for_dhcp": False,"ipv6addr": ipv6_network+"::1"}],"name": "host19.test.com","view": "default","configure_for_dns": True}
                response = ib_NIOS.wapi_request('POST',object_type="record:host", fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                print("\n===================")
                print("Restart DHCP Services")
                print("=====================")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 111 Execution is Completed")

        @pytest.mark.run(order=112)
        def test_112_Validate_Created_HOST_Record(self):
                print("\n==============================")
                print("validating created HOST record ")
                print("================================")
                response = ib_NIOS.wapi_request('GET', object_type="record:host?name=host19.test.com&_return_fields%2B=configure_for_dns&_return_as_object=1",grid_vip=config.grid_vip)
                print(response)
                data = ['"configure_for_dhcp": false','"host": "host19.test.com"','"ipv6addr": "'+ipv6_network+'::1"','"view": "default"','"configure_for_dns": true']
                for i in data:
                        if i in response:
                                assert True
                                print(i)
                        else:
                                assert False
                print("Test Case 112 Execution is Completed")

        @pytest.mark.run(order=113)
        def test_113_Validate_HOST_Record_Creation_time_through_Grid1_IPv6_IP_when_the_HOST_Record_is_added_with_IPv6_address(self):
                print("\n==============================")
                print("validating HOST Record creation time through Grid1 IPv6 IP when the HOST Record is added with IPv6 Address")
                print("================================")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                sleep(05)
                child.sendline('''grep host19.test.com /infoblox/var/audit.log''')
                child.expect('#')
                output = child.before
                output = output.replace("\n","").replace("\r","")
                auditlogs = re.search('audit.log(.*)Created HostRecord',output)
                auditlogs = auditlogs.group(0)
                print("\n")
                record_host = ib_NIOS.wapi_request('GET',object_type="record:host?name=host19.test.com",grid_vip='['+config.grid1_ipv6_ip+']')
                ref = json.loads(record_host)[0]['_ref']
                ref = eval(json.dumps(ref))
                response = ib_NIOS.wapi_request('GET', ref=ref,params="?_inheritance=True&_return_fields=creation_time",grid_vip='['+config.grid1_ipv6_ip+']')
                response = json.loads(response)
                epoch_time = str(response["creation_time"])
                epoch_time = float(epoch_time)
                print("Epoch Time -->> ",epoch_time)
                epoch_time=datetime.datetime.utcfromtimestamp(epoch_time).strftime('%Y-%m-%d %H:%M')
                print("Epoch Time to UTC -->> ",epoch_time)
                if epoch_time in auditlogs:
                        assert True
                        print("\n")
                        print("Epoch Time of host19.test.com record Matched with Audit log time stamp")
                        print("\n")
                else:
                        print("\n")
                        print("Epoch Time of host19.test.com record is Not Matched with Audit log time stamp")
                        print("\n")
                        assert False
                print("Test Case 113 Execution is Completed")

        @pytest.mark.run(order=114)
        def test_114_Create_an_HOST_Record_with_IPv4_and_IPv6_address(self):
                print("\n====================================")
                print("creating HOST record with IPv4 and IPv6 Address")
                print("======================================")
		data = {"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "20.0.0.0","mac": "20:20:20:20:20:20"}],"ipv6addrs": [{"configure_for_dhcp": True,"duid": "12:34","ipv6addr": ipv6_network+"::2"}],"name": "host20.test.com","view": "default"}
                response = ib_NIOS.wapi_request('POST',object_type="record:host", fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                print("\n===================")
                print("Restart DHCP Services")
                print("=====================")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 114 Execution is Completed")

        @pytest.mark.run(order=115)
        def test_115_Validate_Created_HOST_Record(self):
                print("\n==============================")
                print("validating created HOST record ")
                print("================================")
                response = ib_NIOS.wapi_request('GET', object_type="record:host?name=host20.test.com&_return_fields%2B=configure_for_dns&_return_as_object=1",grid_vip=config.grid_vip)
                print(response)
                data = ['"configure_for_dhcp": true','"host": "host20.test.com"','"ipv6addr": "'+ipv6_network+'::2"','"view": "default"','"configure_for_dns": true','"ipv4addr": "20.0.0.0"','"duid": "12:34"']
                for i in data:
                        if i in response:
                                assert True
                                print(i)
                        else:
                                assert False
                print("Test Case 115 Execution is Completed")

        @pytest.mark.run(order=116)
        def test_116_Validate_HOST_Record_Creation_time_through_Grid1_IPv6_IP_when_the_HOST_Record_is_added_with_IPv4_and_IPv6_address(self):
                print("\n==============================")
                print("validating HOST Record creation time through Grid1 IPv6 IP when the HOST Record is added with IPv4 and IPv6 Address")
                print("================================")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                sleep(05)
                child.sendline('''grep host20.test.com /infoblox/var/audit.log''')
                child.expect('#')
                output = child.before
                output = output.replace("\n","").replace("\r","")
                auditlogs = re.search('audit.log(.*)Created HostRecord',output)
                auditlogs = auditlogs.group(0)
                print("\n")
                record_host = ib_NIOS.wapi_request('GET',object_type="record:host?name=host20.test.com",grid_vip='['+config.grid1_ipv6_ip+']')
                ref = json.loads(record_host)[0]['_ref']
                ref = eval(json.dumps(ref))
                response = ib_NIOS.wapi_request('GET', ref=ref,params="?_inheritance=True&_return_fields=creation_time",grid_vip='['+config.grid1_ipv6_ip+']')
                response = json.loads(response)
                epoch_time = str(response["creation_time"])
                epoch_time = float(epoch_time)
                print("Epoch Time -->> ",epoch_time)
                epoch_time=datetime.datetime.utcfromtimestamp(epoch_time).strftime('%Y-%m-%d %H:%M')
                print("Epoch Time to UTC -->> ",epoch_time)
                if epoch_time in auditlogs:
                        assert True
                        print("\n")
                        print("Epoch Time of host20.test.com record Matched with Audit log time stamp")
                        print("\n")
                else:
                        print("\n")
                        print("Epoch Time of host20.test.com record is Not Matched with Audit log time stamp")
                        print("\n")
                        assert False
                print("Test Case 116 Execution is Completed")

        @pytest.mark.run(order=117)
        def test_117_Validate_Creation_time_of_HOST_record_when_the_HOST_record_is_added_with_IPv4_and_IPv6_address(self):
                print("\n=====================================")
                print("Validating creation time of HOST Record when the HOST record is added with IPv4 and IPv6 address")
                print("=======================================")
                response=epoch("host20.test.com")
                print("Test Case 117 Execution is Completed")


#########################
## GMC Scenarios ########
#########################

        @pytest.mark.run(order=118)
        def test_118_Enable_RO_API_Access_for_Grid_Master_Candidate(self):
                print("\n==============================")
                print("Enabling RO API Access for Grid Master Candidate")
                print("================================")
                response = ib_NIOS.wapi_request('GET',object_type="member")
                print(response)
                ref = json.loads(response)[-1]['_ref']
                print(ref)
		data = {"enable_ro_api_access": True}
		output = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data))
		print(output)
		sleep(20)
		print("Test Case 118 Execution is Completed")

        @pytest.mark.run(order=119)
        def test_119_Validate_enabled_RO_API_Access_for_Grid_Master_Candidate(self):
                print("\n==============================")
                print("Validating enabled RO API Access for Grid Master Candidate")
                print("================================")
		response = ib_NIOS.wapi_request('GET',object_type="member")
                print(response)
                ref = json.loads(response)[-1]['_ref']
		output = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=enable_ro_api_access")
		print(output)
		data = '"enable_ro_api_access": true'
		if data in output:
			assert True
		else:
			assert False
		print("Test Case 119 Execution is Completed")

        @pytest.mark.run(order=120)
        def test_120_Validate_HOST_Record_Creation_time_through_GMC_IP(self):
		print("\n==============================")
		print("validating HOST Record Creation time through GMC IP")
		print("================================")
	        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
	        child.logfile=sys.stdout
        	child.expect('#')
	        sleep(05)
        	child.sendline('''grep host11.test.com /infoblox/var/audit.log''')
	        child.expect('#')
        	output = child.before
	        output = output.replace("\n","").replace("\r","")
        	auditlogs = re.search('audit.log(.*)Created HostRecord',output)
	        auditlogs = auditlogs.group(0)
        	print("\n")
        	record_host = ib_NIOS.wapi_request('GET',object_type="record:host?name=host11.test.com",grid_vip=config.GMC_IP)
	        ref = json.loads(record_host)[0]['_ref']
        	ref = eval(json.dumps(ref))
	        response = ib_NIOS.wapi_request('GET', ref=ref,params="?_inheritance=True&_return_fields=creation_time",grid_vip=config.GMC_IP)
        	response = json.loads(response)
	        epoch_time = str(response["creation_time"])
        	epoch_time = float(epoch_time)
	        print("Epoch Time -->> ",epoch_time)
	        epoch_time=datetime.datetime.utcfromtimestamp(epoch_time).strftime('%Y-%m-%d %H:%M')
        	print("Epoch Time to UTC -->> ",epoch_time)
	        if epoch_time in auditlogs:
        	        assert True
                	print("\n")
	                print("Epoch Time of host11.test.com record Matched with Audit log time stamp")
        	        print("\n")
	        else:
        	        print("\n")
                	print("Epoch Time of host11.test.com record is Not Matched with Audit log time stamp")
	                print("\n")
        	        assert False
		print("Test Case 120 Execution is Completed")

################################
### HOST Name Policy Scenario ##
################################

        @pytest.mark.run(order=121)
        def test_121_Update_new_HostName_Policy(self):
                print("\n==============================")
                print("Updating new HostName Policy")
                print("================================")
		grid_dns=ib_NIOS.wapi_request('GET',object_type="grid:dns")
		ref = json.loads(grid_dns)[0]['_ref']
		data = {"protocol_record_name_policies": [{"is_default": False,"name": "Strict Hostname Checking","regex": "^[a-zA-Z0-9]$|^[a-zA-Z0-9][-a-zA-Z0-9.]*[a-zA-Z0-9]$"},{"is_default": False,"name": "Allow Underscore","regex": "^[-a-zA-Z0-9_.]+$"},{"is_default": False,"name": "Allow Any","regex": ".+"},{"is_default": True,"name": "Allow integers","regex": "^[0-9.]+$"}]}
                response = ib_NIOS.wapi_request('PUT',ref=ref,object_type="grid:dns",fields=json.dumps(data))
                print(response)
		print("Test Case 121 Execution is Completed")

        @pytest.mark.run(order=122)
        def test_122_Create_an_HOST_Record_as_per_new_Allow_Integers_RR_policy(self):
                print("\n==============================")
                print("creating HOST record as per new Allow Integers RR policy")
                print("================================")
                data = {"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "10.0.0.19","mac": "19:19:19:19:19:19"}],"name": "19.test.com","configure_for_dns": True,"view": "default"}
                response = ib_NIOS.wapi_request('POST',object_type="record:host", fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                print("\n===================")
                print("Restart DHCP Services")
                print("=====================")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 122 Execution is Completed")

        @pytest.mark.run(order=123)
        def test_123_Validate_Created_HOST_Record(self):
                print("\n==============================")
                print("validating created HOST record ")
                print("================================")
                response = ib_NIOS.wapi_request('GET', object_type="record:host?name=19.test.com&_return_fields%2B=configure_for_dns&_return_as_object=1",grid_vip=config.grid_vip)
                print(response)
                data = ['"configure_for_dhcp": true','"host": "19.test.com"','"ipv4addr": "10.0.0.19"','"mac": "19:19:19:19:19:19"','"view": "default"','"configure_for_dns": true']
                for i in data:
                        if i in response:
                                assert True
                                print(i)
                        else:
                                assert False
                print("Test Case 123 Execution is Completed")

        @pytest.mark.run(order=124)
        def test_124_Validate_Creation_time_of_HOST_record_when_the_HOST_record_is_in_default_dns_view_and_set_back_hostname_policy(self):
                print("\n=====================================")
                print("Validating creation time of HOST Record when the HOST record is in default dns view and set back hostname policy")
                print("=======================================")
                response=epoch("19.test.com")
		grid_dns=ib_NIOS.wapi_request('GET',object_type="grid:dns")
                ref = json.loads(grid_dns)[0]['_ref']
		data = {"protocol_record_name_policies": [{"is_default": False,"name": "Strict Hostname Checking","regex": "^[a-zA-Z0-9]$|^[a-zA-Z0-9][-a-zA-Z0-9.]*[a-zA-Z0-9]$"},{"is_default": True,"name": "Allow Underscore","regex": "^[-a-zA-Z0-9_.]+$"},{"is_default": False,"name": "Allow Any","regex": ".+"},{"is_default": False,"name": "Allow integers","regex": "^[0-9.]+$"}]}	
		response = ib_NIOS.wapi_request('PUT',ref=ref,object_type="grid:dns",fields=json.dumps(data))
		sleep(40)
                print("Test Case 124 Execution is Completed")

        @pytest.mark.run(order=125)
        def test_125_Add_HOST_Record_through_CSV_Import(self):
		print("\n=====================================")
		print("Adding HOST Record through CSV Import")
		print("=======================================")
		data = ib_NIOS.wapi_request('POST', object_type="fileop",params="?_function=uploadinit")
         	print(data)
                data  = json.loads(data)
                data  = eval(json.dumps(data))
                token = data['token']
                url  = data['url']
		url_upload = ('curl -k1 -u admin:infoblox -F name=@Zonechilds_25.csv '+url)
		print(url_upload)
                url_upload  = os.popen(url_upload).read()
                print(url_upload)
		data = {"action":"START","on_error":"CONTINUE","update_method":"MERGE","token":token}
		print(data)
                token_upload = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=csv_import")
                print("\n")
                print(token_upload)
		sleep(10)
		print("Test Case 125 Execution is Completed")

        @pytest.mark.run(order=126)
        def test_126_Validate_Creation_time_of_HOST_record_when_the_HOST_record_is_in_default_dns_view(self):
                print("\n=====================================")
                print("Validating creation time of HOST Record when the HOST record is in default dns view")
                print("=======================================")
                response=epoch("host21.test.com")
                print("Test Case 126 Execution is Completed")

        @pytest.mark.run(order=127)
        def test_127_Copy_HOST_Records_from_test_zone_to_import_zone_in_default_dns_view(self):
                print("\n==============================================")
                print("Copy HOST Records from test.com to import.com zone in default dns view")
                print("==============================================\n")
		source_zone =  ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=test.com", grid_vip=config.grid_vip)
                source_zone = json.loads(source_zone)[0]['_ref']
		print(source_zone)
		destination_zone=ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=import.com",grid_vip=config.grid_vip)
		destination_zone=json.loads(destination_zone)[0]['_ref']
		print(destination_zone)
                data = {"clear_destination_first": False,"destination_zone": destination_zone,"replace_existing_records": True,"select_records":["HOST"]}
                response = ib_NIOS.wapi_request('POST', object_type=source_zone, params='?_function=copyzonerecords', fields=json.dumps(data))
                print("\n")
                print(response)
		print("\n=========================")
                print("HOST Records are copied")
                print("=========================\n")
                sleep(05)
		print("Test Case 127 Execution is Completed")

        @pytest.mark.run(order=128)
        def test_128_Validate_Copied_HOST_Records_from_test_zone_to_import_zone_in_audit_logs(self):
		print("\n==============================================")
                print("Validating copied HOST Records from test.com to import.com zone in audit logs")
                print("==============================================\n")
		child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                sleep(05)
                child.sendline('''grep "destination_zone=Zone:import.com" /infoblox/var/audit.log''')
                child.expect('#')
                output = child.before
		data = ['select_records=["HOST"]','source_zone=Zone:test.com','destination_zone=Zone:import.com']
		print("\n")
		for i in data:
			if i in output:
				assert True
				print(i)
			else:
				assert False
                print("\n=========================")
                print("Validated Copied HOST Records")
                print("=========================\n")
		print("Test Case 128 Execution is Completed")

        @pytest.mark.run(order=129)
        def test_129_Validate_Copied_HOST_Record_Creation_time_in_Audit_logs(self):
                print("\n==============================")
                print("validating copied HOST Records Creation time in Audit logs")
                print("================================")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                sleep(05)
                child.sendline('''grep "destination_zone=Zone:import.com" /infoblox/var/audit.log''')
                child.expect('#')
                auditlogs = child.before
                record_host = ib_NIOS.wapi_request('GET',object_type="record:host?name=host10.import.com",grid_vip=config.grid_vip)
                ref = json.loads(record_host)[0]['_ref']
                ref = eval(json.dumps(ref))
                response = ib_NIOS.wapi_request('GET', ref=ref,params="?_inheritance=True&_return_fields=creation_time",grid_vip=config.grid_vip)
                response = json.loads(response)
                epoch_time = str(response["creation_time"])
                epoch_time = float(epoch_time)
                print("Epoch Time -->> ",epoch_time)
                epoch_time=datetime.datetime.utcfromtimestamp(epoch_time).strftime('%Y-%m-%d %H:%M')
                print("Epoch Time to UTC -->> ",epoch_time)
                if epoch_time in auditlogs:
                        assert True
                        print("\n")
                        print("Epoch Time of host10.import.com record Matched with Audit log time stamp")
                        print("\n")
                else:
                        print("\n")
                        print("Epoch Time of host10.import.com record is Not Matched with Audit log time stamp")
                        print("\n")
                        assert False
                print("Test Case 129 Execution is Completed")


        @pytest.mark.run(order=130)
        def test_130_Copy_HOST_Records_from_test_zone_to_import_zone_in_custom_dns_view(self):
                print("\n==============================================")
                print("Copy and Validate HOST Records from test.com to import.com zone in custom dns view")
                print("==============================================\n")
                source_zone =  ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=test.com", grid_vip=config.grid_vip)
                source_zone = json.loads(source_zone)[0]['_ref']
                print(source_zone)
                destination_zone=ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=test1.com",grid_vip=config.grid_vip)
                destination_zone=json.loads(destination_zone)[0]['_ref']
                print(destination_zone)
                data = {"clear_destination_first": False,"destination_zone": destination_zone,"replace_existing_records": True,"select_records":["HOST"]}
                response = ib_NIOS.wapi_request('POST', object_type=source_zone, params='?_function=copyzonerecords', fields=json.dumps(data))
                print("\n")
                print(response)
                print("\n=========================")
                print("HOST Records are copied")
                print("=========================\n")
                sleep(05)
		print("Test Case 130  Execution is Completed")

        @pytest.mark.run(order=131)
        def test_131_Validate_copied_HOST_Records_from_test_zone_to_test1_zone_in_Audit_logs(self):
		print("\n==============================================")
                print("Validating copied HOST Records from test.com to test1.com zone in Audit logs")
                print("==============================================\n")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                sleep(05)
                child.sendline('''grep "destination_zone=Zone:test1.com" /infoblox/var/audit.log''')
                child.expect('#')
                output = child.before
                data = ['select_records=["HOST"]','source_zone=Zone:test.com','destination_zone=Zone:test1.com']
                print("\n")
                for i in data:
                        if i in output:
                                assert True
                                print(i)
                        else:
                                assert False
                print("\n=========================")
                print("Validated Copied HOST Records")
                print("=========================\n")
                print("Test Case 131 Execution is Completed")

        @pytest.mark.run(order=132)
        def test_132_Validate_Copied_HOST_Records_from_default_dns_view_to_custom_dns_view_creation_time_in_Audit_logs(self):
                print("\n==============================")
                print("validating copied HOST Records from default dns view to custom dns view creation time in Audit logs")
                print("================================")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                sleep(05)
                child.sendline('''grep "destination_zone=Zone:test1.com" /infoblox/var/audit.log''')
                child.expect('#')
                auditlogs = child.before
                record_host = ib_NIOS.wapi_request('GET',object_type="record:host?name=host10.test1.com",grid_vip=config.grid_vip)
                ref = json.loads(record_host)[0]['_ref']
                ref = eval(json.dumps(ref))
                response = ib_NIOS.wapi_request('GET', ref=ref,params="?_inheritance=True&_return_fields=creation_time",grid_vip=config.grid_vip)
                response = json.loads(response)
                epoch_time = str(response["creation_time"])
                epoch_time = float(epoch_time)
                print("Epoch Time -->> ",epoch_time)
                epoch_time=datetime.datetime.utcfromtimestamp(epoch_time).strftime('%Y-%m-%d %H:%M')
                print("Epoch Time to UTC -->> ",epoch_time)
                if epoch_time in auditlogs:
                        assert True
                        print("\n")
                        print("Epoch Time of host10.test1.com record Matched with Audit log time stamp")
                        print("\n")
                else:
                        print("\n")
                        print("Epoch Time of host10.test1.com record is Not Matched with Audit log time stamp")
                        print("\n")
                        assert False
                print("Test Case 132 Execution is Completed")


        @pytest.mark.run(order=133)
        def test_133_Create_A_record(self):
                print("\n==============================")
                print("Creating A record")
                print("================================")
                data={"name": "a.test.com","ipv4addr":"10.0.0.100","view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data))
                print (response)
                sleep(05)
		response = ib_NIOS.wapi_request('GET',object_type="record:a?name=a.test.com")
                print(response)
                ref = json.loads(response)[-1]['_ref']
                print(ref)
                data = {"creator": "DYNAMIC"}
                output = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data))
                print(output)
		print("Test Case 133 Execution Completed")
	
        @pytest.mark.run(order=134)
        def test_134_Validate_created_A_record(self):
                print("\n=========================")
                print("Validating created A record")
                print("===========================")
		response = ib_NIOS.wapi_request('GET',object_type="record:a?name=a.test.com&_return_fields%2B=name,ipv4addr,creator&_return_as_object=1")
                print(response)
		data = ['"creator": "DYNAMIC"','"ipv4addr": "10.0.0.100"','"name": "a.test.com"','"view": "default"']
		for i in data:
			if i in response:
				assert True
				print(i)
			else:
				assert False
		print("Test Case 134 Execution Completed")

        @pytest.mark.run(order=135)
        def test_135_Update_DNS_Scavenging_settings_rule_to_do_record_scavenging_with_creation_time_greater_then_one_hour(self):
		print("\n=========================")
                print("Updating DNS Scavenging settings rules to do record scavenging with creation time greater than one hour")
                print("===========================")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                ref = json.loads(response)[-1]['_ref']
                print(ref)
		data = {"scavenging_settings": {"ea_expression_list": [],"enable_auto_reclamation": False,"enable_recurrent_scavenging": False,"enable_rr_last_queried": False,"enable_scavenging": True,"enable_zone_last_queried": False,"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "GT","op1": "ctime","op1_type": "FIELD","op2": "3600","op2_type": "STRING"},{"op": "ENDLIST"}],"reclaim_associated_records": False}}
		output = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data))
		print(output)
		grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20 sec.,")
                sleep(30) #wait for 20 secs for the member to get started
		print("Test Case 135 Execution Completed")

        @pytest.mark.run(order=136)
        def test_136_Perform_DNS_Scavenging(self):
		print("\n=======================")
		print("Performing DNS Scavenging")
		print("=========================")
		response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
		ref = json.loads(response)[-1]['_ref']
                print(ref)
                data={"action":"ANALYZE_RECLAIM"}
                response = ib_NIOS.wapi_request('POST',object_type=ref,fields=json.dumps(data),params="?_function=run_scavenging")
		print(response)
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(10)
                print("Test Case 136 Execution Completed")

        @pytest.mark.run(order=137)
        def test_137_Validate_Creation_time_of_HOST_record_after_DNS_Scavenging(self):
                print("\n=====================================")
                print("Validating creation time of HOST Record after DNS Scavenging")
                print("=======================================")
                response=epoch("host21.test.com")
                print("Test Case 137 Execution is Completed")








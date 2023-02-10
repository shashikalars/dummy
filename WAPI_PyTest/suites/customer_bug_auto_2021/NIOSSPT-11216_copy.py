#!/usr/bin/env python
__author__ = "Prasad K"
__email__  = "pkondisetty@@infoblox.com"

####################################################################################
#  Grid Set up required:                                                           #
#  1. Grid Master with one threat protection member                                #
#  2. Licenses : DNS, Grid, NIOS(IB_1415),Threat Protection licenses               #
#  3. Enable DNS services                                                          #
#  NIOSSPT JIRA link : https://jira.inca.infoblox.com/browse/NIOSSPT-11216         #
#                                                                                  #
####################################################################################

import re
import pprint
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
import sys
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv

class NIOSSPT_11216(unittest.TestCase):


    @pytest.mark.run(order=1)
    def test_01_Start_DNS_Service_on_both_members(self):
        print("\n============================================\n")
        print("Enable DNS service on both members")
        print("\n============================================\n")
        data = {"enable_dns": True}
        for i in range(0,2):
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
                ref = json.loads(get_ref)[i]['_ref']
                response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
        print("Test case 01 Execution Completed")


    @pytest.mark.run(order=2)
    def test_02_Validate_enabled_dns_service_on_both_members(self):
        print("\n============================================\n")
        print("Validate Enabled DNS service on both members")
        print("\n============================================\n")
        data = '"enable_dns": true'
        for i in range(0,2):
                member_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
                member_ref = json.loads(member_ref)[i]['_ref']
                response = ib_NIOS.wapi_request('GET',ref=member_ref+'?_return_fields=enable_dns',grid_vip=config.grid_vip)
                print(response)
                if data in response:
                        assert True
                else:
                        assert False
        print(data)
        print("Test case 02 Execution Completed")

    @pytest.mark.run(order=3)
    def test_03_Start_Threat_Protection_Service_on_member(self):
        print("\n============================================\n")
        print("Enable Threat Protection Service on member")
        print("\n============================================\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection", grid_vip=config.grid_vip)
        print(get_ref)
        ref = json.loads(get_ref)[0]['_ref']
        data = {"enable_service": True}
        response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30) #wait for 30 secs for the member to get started
        print("Test case 03 Execution Completed")


    @pytest.mark.run(order=4)
    def test_04_Validate_Enabled_Threat_Protection_Service_on_member(self):
        print("\n============================================\n")
        print("Validate Enabled Threat Protection Service on member")
        print("\n============================================\n")
        data = '"enable_service": true'
        member_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection", grid_vip=config.grid_vip)
        member_ref = json.loads(member_ref)[0]['_ref']
        response = ib_NIOS.wapi_request('GET',ref=member_ref+'?_return_fields=enable_service',grid_vip=config.grid_vip)
        print(response)
        if data in response:
                 assert True
        else:
                 assert False
        print(data)
        print("Test case 04 Execution Completed")

    @pytest.mark.run(order=5)
    def test_05_Configure_OSPF_IPv4_configuration_on_both_members(self):
        print("\n============================================\n")
        print("Configure OSFP IPV4 for both members")
        print("\n============================================\n")
	for i in range(0,2):
	        get_ref = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
        	res = json.loads(get_ref)
	        res = eval(json.dumps(res))
        	ref=(res)[i]['_ref']
	        print(ref)
        	data = {"ospf_list": [{"area_id": "0.0.0.12","area_type": "STANDARD","authentication_type": "NONE","auto_calc_cost_enabled": True,"cost": 1,"dead_interval": 40,"enable_bfd": False,"hello_interval": 10,"interface": "LAN_HA","is_ipv4": True,"key_id": 1,"retransmit_interval": 5,"transmit_delay": 1}]}
	        #get_ref1 = ib_NIOS.wapi_request('GET',object_type=ref+'?_return_fields=additional_ip_list',grid_vip=config.grid_vip)
        	response = ib_NIOS.wapi_request('PUT',ref=ref, fields=json.dumps(data),grid_vip=config.grid_vip)
	        print(response)
        print("Test case 05 Execution Completed")

    @pytest.mark.run(order=6)
    def test_06_Validate_Configured_OSPF_IPv4_configuration_on_both_members(self):
        print("\n============================================\n")
        print("Validate OSPF IPV4 configuration on both  members")
        print("\n============================================\n")
	for i in range(0,2):
	      	get_ref = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
        	ref = json.loads(get_ref)[1]['_ref']
	       	ref = eval(json.dumps(ref))
        	response = ib_NIOS.wapi_request('GET',object_type=ref+'?_return_fields=ospf_list',grid_vip=config.grid_vip)
	       	print(response)
		data = ['"area_id": "0.0.0.12"','"area_type": "STANDARD"','"authentication_type": "NONE"','"auto_calc_cost_enabled": true','"cost": 1','"dead_interval": 40','"enable_bfd": false','"hello_interval": 10','"interface": "LAN_HA"','"is_ipv4": true','"key_id": 1','"retransmit_interval": 5','"transmit_delay": 1']
		for j in data:
			if j in response:
				assert True
			else:
				assert False
	print(data)
        print("Test case 06 Execution Completed")


    @pytest.mark.run(order=7)
    def test_07_Configure_BGP_configurations_for_both_members(self):
        print("\n============================================\n")
        print(" Configure BGP configuration on both members ")
        print("\n============================================\n")
	for i in range(0,2):
	        get_ref = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
        	res = json.loads(get_ref)
	        res = eval(json.dumps(res))
        	ref=(res)[i]['_ref']
	        print(ref)
        	data={"bgp_as": [{"as": 12,"holddown": 16,"keepalive": 4,"link_detect": False,"neighbors": [{"authentication_mode": "NONE","enable_bfd": False,"interface": "LAN_HA","multihop": False,"multihop_ttl": 255,"neighbor_ip": config.anycast_client,"remote_as": 12}]}]}
	        #get_ref1 = ib_NIOS.wapi_request('GET',object_type=ref+'?_return_fields=additional_ip_list',grid_vip=config.grid_vip)
        	response = ib_NIOS.wapi_request('PUT',ref=ref, fields=json.dumps(data),grid_vip=config.grid_vip)
        	print(response)
	print(data)
        print("Test case 07 Execution Completed")


    @pytest.mark.run(order=8)
    def test_08_Validate_configured_BGP_configuration_on_both_members(self):
        print("\n============================================\n")
        print("Validate BGP configurations on both members")
        print("\n============================================\n")
	for i in range(0,2):
	        get_ref = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
        	ref = json.loads(get_ref)[1]['_ref']
	        ref = eval(json.dumps(ref))
        	response = ib_NIOS.wapi_request('GET',object_type=ref+'?_return_fields=bgp_as',grid_vip=config.grid_vip)
	        print(response)
        	data=['"as": 12','"holddown": 16','"keepalive": 4','"link_detect": false','"authentication_mode": "NONE"','"enable_bfd": false','"interface": "LAN_HA"','"multihop": false','"multihop_ttl": 255','"neighbor_ip": "'+config.anycast_client+'"','"remote_as": 12']
	        for j in data:
        	        if j in response:
                	        assert True
				print(j)
	                else:
        	                assert False
        print(data)
        print("Test case 08 Execution Completed")




    @pytest.mark.run(order=9)
    def test_09_Enable_OSPF_and_BGP_ANYCAST_services_on_both_members(self):
        print("\n============================================\n")
        print("Enable OSPF and BGP and Anycast serivices on both members")
        print("\n============================================\n")
	for i in range(0,2):
        	get_ref = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
	        ref = json.loads(get_ref)[i]['_ref']
        	ref = eval(json.dumps(ref))
	        print(ref)
        	data={"additional_ip_list": [{"anycast": True,"enable_bgp": True,"enable_ospf": True,"interface": "LOOPBACK","ipv4_network_setting": {"address": "1.1.1.1","dscp": 0,"primary": False,"subnet_mask": "255.255.255.255","use_dscp": False}}]}
	        #get_ref1 = ib_NIOS.wapi_request('GET',object_type=ref+'?_return_fields=additional_ip_list',grid_vip=config.grid_vip)
        	response = ib_NIOS.wapi_request('PUT',ref=ref, fields=json.dumps(data),grid_vip=config.grid_vip)
	        print(response)
	print(data)
	sleep(300)
        print("Test case 09 Execution Completed")


    @pytest.mark.run(order=10)
    def test_10_Validate_enabled_ospf_and_bgp_anycast_services_on_both_members(self):
        print("\n============================================\n")
        print("Validate enabled ospf and bgp and anycast services on both services")
        print("\n============================================\n")
	for i in range(0,2):
        	get_ref = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
	        ref = json.loads(get_ref)[0]['_ref']
        	ref = eval(json.dumps(ref))
	        response = ib_NIOS.wapi_request('GET',object_type=ref+'?_return_fields=additional_ip_list',grid_vip=config.grid_vip)
        	print(response)
	        data = ['"anycast": true','"enable_bgp": true','"enable_ospf": true','"interface": "LOOPBACK"','"address": "1.1.1.1"','"dscp": 0','"primary": false','"subnet_mask": '+'"255.255.255.255"','"use_dscp": false']
        	for j in data:
                	if j in response:
                        	assert True
	                else:
        	                assert False
        print(data)
        print("Test case 10 Execution Completed")


    @pytest.mark.run(order=11)
    def test_11_Associate_configured_IPv4_anycast_IP_for_both_members_at_member_DNS_properties(self):
        print("\n============================================\n")
        print("Associate configured IPV4 anycast IP for both members at member DNS properties")
        print("\n============================================\n")
	for i in range(0,2):
		get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
		print(get_ref)
        	ref1 = json.loads(get_ref)[i]['_ref']
		ref1 = eval(json.dumps(ref1))
		print(ref1)
		data= {"additional_ip_list_struct": [{"ip_address": "1.1.1.1"}]}
		print("my data is",data)
		response1 = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
		print(response1)
	grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30) #wait for 30 secs for the member to get started
        print("Test case 11 Execution Completed")


    @pytest.mark.run(order=12)
    def test_12_Validate_associated_IPv4_anycast_IP_at_both_member_dns_properties(self):
        print("\n============================================\n")
        print("Validate associated IPv4 anycast IP at both member dns properties")
        print("\n============================================\n")
	for i in range(0,2):
	        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        	ref = json.loads(get_ref)[i]['_ref']
	        ref = eval(json.dumps(ref))
        	print(ref)
		response = ib_NIOS.wapi_request('GET',object_type=ref+'?_return_fields=additional_ip_list_struct',grid_vip=config.grid_vip)
        	print(response)
		data='"ip_address": "1.1.1.1"'
		if data in response:
			assert True
		else:
			assert False
	print(data)
        print("Test case 12 Execution Completed")

    @pytest.mark.run(order=13)
    def test_13_Add_Resolver_at_grid_properties(self):
        print("\n============================================\n")
        print("Add resolver at grid properties")
        print("\n============================================\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        print(get_ref)
        ref = json.loads(get_ref)[0]['_ref']
        data = {"dns_resolver_setting": {"resolvers": [config.dns_resolver]}}
        response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)
	grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30) #wait for 30 secs for the member to get started
        print("Test case 13 Execution Completed")
	

    @pytest.mark.run(order=14)
    def test_14_Validate_configured_Resolver_IP(self):
        print("\n============================================\n")
        print("Validate configured resolver ip")
        print("\n============================================\n")
	response = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=dns_resolver_setting')
	print(response)
	data = config.dns_resolver
	if data in response:
		assert True
	else:
		assert False
        print("Test case 14 Execution Completed")


    @pytest.mark.run(order=15)
    def test_15_Add_neighbor_IP_as_Grid_Master_IP_in_bird_conf_file(self):
	print("\n============================================\n")
        print("Add neighbor IP as gird ip in bird.conf file")
        print("\n============================================\n")
	try:
                  child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.client_v4)
                  child.logfile=sys.stdout
                  child.expect('password: ')
                  child.sendline('infoblox')
                  child.expect('#')
                  child.sendline('cp /import/qaddi/API_Automation_27_06/WAPI_PyTest/suites/prasad_k/11216bird.conf /import/qaddi/API_Automation/WAPI_PyTest/suites/customer_bug_auto_2021')
                  child.expect('#')
                  child.sendline('chmod 777 /import/qaddi/API_Automation/WAPI_PyTest/suites/customer_bug_auto_2021/11216bird.conf')
                  child.expect('#')
        except:
                  print("Failed to copy the 11216bird.conf file ")
                  assert False
        finally:
                  child.close()
	with open('/import/qaddi/API_Automation/WAPI_PyTest/suites/customer_bug_auto_2021/11216bird.conf', 'r') as file :
	 	filedata = file.read()
	filedata = filedata.replace('neighbor 10.0.0.2', 'neighbor '+config.grid_vip)
	with open('/import/qaddi/API_Automation/WAPI_PyTest/suites/customer_bug_auto_2021/11216bird.conf', 'w') as file:
	  file.write(filedata)
	print("sleep")
	sleep(10)
	print("Test case 15 Execution Completed")

    @pytest.mark.run(order=16)
    def test_16_Validate_neighbor_IP_in_bird_conf_file(self):
        print("\n============================================\n")
        print("Validate neighbor IP in bird.conf file")
        print("\n============================================\n")
	with open('/import/qaddi/API_Automation/WAPI_PyTest/suites/customer_bug_auto_2021/11216bird.conf', 'r') as file :
                filedata = file.read()
		data = ('neighbor '+config.grid_vip)
            	if data in filedata:
                	assert  True
		else:
			assert False
	print(data)
	print("Test case 16 Execution Completed")

    @pytest.mark.run(order=17)
    def test_17_Add_source_address_as_client_IP_in_bird_conf_file(self):
	print("\n============================================\n")
        print("Add source IP as client IP in bird.conf file ")
        print("\n============================================\n")
        with open('/import/qaddi/API_Automation/WAPI_PyTest/suites/customer_bug_auto_2021/11216bird.conf', 'r') as file :
                filedata = file.read()
        filedata = filedata.replace('source address 10.0.0.2', 'source address '+config.client_v4)
        with open('/import/qaddi/API_Automation/WAPI_PyTest/suites/customer_bug_auto_2021/11216bird.conf', 'w') as file:
          file.write(filedata)
	print("Test case 17 Execution Completed")

    @pytest.mark.run(order=18)
    def test_18_Validate_source_IP_ib_bird_conf_file(self):
        print("\n============================================\n")
        print("Validate  source IP address in bird.conf file")
        print("\n============================================\n")
        with open('/import/qaddi/API_Automation/WAPI_PyTest/suites/customer_bug_auto_2021/11216bird.conf', 'r') as file :
                filedata = file.read()
                data = ('source address '+config.client_v4)
                if data in filedata:
                        assert  True
                else:
                        assert False
        print(data)
        print("Test case 18 Execution Completed")


    @pytest.mark.run(order=19)
    def test_19_Run_bird_conf_file_to_start_the_neighborship_process(self):
	print("\n============================================\n")
        print("Run bird.conf file to start the neighborship process")
        print("\n============================================\n")
	try:
                  child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.client_v4)
                  child.logfile=sys.stdout
                  child.expect('password: ')
                  child.sendline('infoblox')
                  child.expect('#')
                  child.sendline('cp /import/qaddi/API_Automation/WAPI_PyTest/suites/customer_bug_auto_2021/11216bird.conf /usr/local/etc/')
                  #child.expect('password: ')
                  #child.sendline('infoblox')
                  child.expect('#')
        except:
                  print("Failed to copy the bird.conf file ")
                  assert False
        finally:
                  child.close()
	print("sleep ---------")
	sleep(120)
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.client_v4)
        child.logfile=sys.stdout
        child.expect('password:')
	child.sendline('infoblox')
	child.expect('#')
        child.sendline('bird -c /usr/local/etc/11216bird.conf')
        child.expect('#')
        output = child.before
        print(output)
	sleep(300)
	print("Test case 19 Execution Completed")


    @pytest.mark.run(order=20)
    def test_20_Validate_ospf_neighborship_in_member(self):
	print("\n============================================\n")
        print("Validate ospf neighborship in member")
        print("\n============================================\n")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	child.sendline('show ospf neighbor')
	child.expect('command.')
	output1=child.before
        print(output1)
        child.sendline('\r')
	child.expect('command.')
        output2 = child.before
	print(output2)
	child.sendline('\r')
        child.expect('Infoblox >')
	output3 = child.before
	print(output3)
	data = ('Neighbor '+config.grid_master_vip)
	if (data in output1) or (data in output2) or (data in output3):
		assert True
	else:
		assert False
	print(data)
        print("Test case 20 Execution Completed")

    @pytest.mark.run(order=21)
    def test_21_Execute_iptable_command_in_GM_to_drop_from_member(self):
	print("\n============================================\n")
        print("Execute iptable command in GM to drop from member")
        print("\n============================================\n")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
        child.logfile=sys.stdout
       # child.expect('#')
        child.sendline('iptables -I OUTPUT -j DROP -p udp --dport 1194')
        child.expect('#')
        child.sendline('exit')
        sleep(300)
        print("Test case 21 Execution Completed")

    @pytest.mark.run(order=22)
    def test_22_Validate_ospf_neighborship_in_member(self):
	print("\n============================================\n")
        print("Validate ospf neighborship in member")
        print("\n============================================\n")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	child.sendline('show ospf neighbor')
        child.expect('command.')
        output1=child.before
        print(output1)
        child.sendline('\r')
        child.expect('command.')
        output2 = child.before
        print(output2)
        child.sendline('\r')
        child.expect('Infoblox >')
        output3 = child.before
        print(output3)
        data = ['Neighbor '+config.client_v4,'interface address '+config.client_v4,'DR is '+config.client_v4]
	for i in data:
        	if (i in output2) or (i in output3) or (i in output1):
                	assert True
			print(i)
        	else:
                	assert False
        print(data)
        print("Test case 22 Execution Completed")

####################################################
## Removing the configuration to cleanup the grid ##
####################################################


    @pytest.mark.run(order=23)
    def test_23_Execute_iptable_command_in_GM_to_delete_the_dropped_iptable(self):
	print("\n============================================\n")
        print("Execute iptable command in GM to delete the dropped iptable")
        print("\n============================================\n")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('iptables -D OUTPUT -j DROP -p udp --dport 1194')
        child.expect('#')
        child.sendline('exit')
        sleep(120)
        print("Test case 23 Execution Completed")

    @pytest.mark.run(order=24)
    def test_24_Disbale_DNS_Service_on_both_members(self):
        print("\n============================================\n")
        print("Disable DNS service on both members")
        print("\n============================================\n")
        data = {"enable_dns": False}
        for i in range(0,2):
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
                ref = json.loads(get_ref)[i]['_ref']
                response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
        print("Test case 24 Execution Completed")


    @pytest.mark.run(order=25)
    def test_25_Validate_disabled_dns_service_on_both_members(self):
        print("\n============================================\n")
        print("Validate disabled DNS service on both members")
        print("\n============================================\n")
        data = '"enable_dns": false'
        for i in range(0,2):
                member_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
                member_ref = json.loads(member_ref)[i]['_ref']
                response = ib_NIOS.wapi_request('GET',ref=member_ref+'?_return_fields=enable_dns',grid_vip=config.grid_vip)
                print(response)
                if data in response:
                        assert True
                else:
                        assert False
        print(data)
        print("Test case 25 Execution Completed")

    @pytest.mark.run(order=26)
    def test_26_Disable_Threat_Protection_Service_on_member(self):
        print("\n============================================\n")
        print("Disable threat protection service on member")
        print("\n============================================\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection", grid_vip=config.grid_vip)
        print(get_ref)
        ref = json.loads(get_ref)[0]['_ref']
        data = {"enable_service": False}
        response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30) #wait for 30 secs for the member to get started
        print("Test case 26 Execution Completed")


    @pytest.mark.run(order=27)
    def test_27_Validate_Disabled_Threat_Protection_Service_on_member(self):
        print("\n============================================\n")
        print("Validate disabled threat protection service on member")
        print("\n============================================\n")
        data = '"enable_service": false'
        member_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection", grid_vip=config.grid_vip)
        member_ref = json.loads(member_ref)[0]['_ref']
        response = ib_NIOS.wapi_request('GET',ref=member_ref+'?_return_fields=enable_service',grid_vip=config.grid_vip)
        print(response)
        if data in response:
                 assert True
        else:
                 assert False
        print(data)
        print("Test case 27 Execution Completed")


    @pytest.mark.run(order=28)
    def test_28_Remove_IPv4_anycast_IP_from_both_members(self):
        print("\n============================================\n")
        print("Configure IPV4 anycast IP for member DNS")
        print("\n============================================\n")
	for i in range(0,2):
	        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        	print(get_ref)
	        ref1 = json.loads(get_ref)[i]['_ref']
        	ref1 = eval(json.dumps(ref1))
	        print(ref1)
        	data= {"additional_ip_list": [ ]}
	        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
        	print(response)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30) #wait for 30 secs for the member to get started
        print("Test case 28 Execution Completed")


    @pytest.mark.run(order=29)
    def test_29_Validate_removed_anycast_IPv4_IP_from_both_members(self):
        print("\n============================================\n")
        print("Configure IPV4 anycast IP for member DNS")
        print("\n============================================\n")
        for i in range(0,2):
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
                ref = json.loads(get_ref)[i]['_ref']
                ref = eval(json.dumps(ref))
                print(ref)
                response = ib_NIOS.wapi_request('GET',object_type=ref+'?_return_fields=additional_ip_list_struct',grid_vip=config.grid_vip)
                print(response)
                data='"additional_ip_list_struct": []'
                if data in response:
                        assert True
                else:
                        assert False
        print(data)
        print("Test case 29 Execution Completed")


    @pytest.mark.run(order=30)
    def test_30_Disable_OSPF_BGP_Anycast_services_on_both_members(self):
        print("\n============================================\n")
        print("Disable ospf and bgp and anycast services on both members")
        print("\n============================================\n")
	for i in range(0,2):
	        get_ref = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
        	print(get_ref)
	        ref = json.loads(get_ref)[i]['_ref']
        	ref = eval(json.dumps(ref))
	        print(ref)
        	data= {"additional_ip_list": [{"anycast": True,"enable_bgp": False,"enable_ospf": False,"interface": "LOOPBACK","ipv4_network_setting": {"address": "1.1.1.1","dscp": 0,"primary": False,"subnet_mask": "255.255.255.255","use_dscp": False}}]}
	        response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
        	print(response)
	print(data)
        print("Test case 30 Execution Completed")

    @pytest.mark.run(order=31)
    def test_31_Validate_disabled_OSPF_BGP_Anycast_services_on_both_members(self):
        print("\n============================================\n")
        print("Validate disabled ospf and bgp and anycast services on both members")
        print("\n============================================\n")
        for i in range(0,2):
                get_ref = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
                print(get_ref)
                ref = json.loads(get_ref)[i]['_ref']
                ref = eval(json.dumps(ref))
                print(ref)
		response = ib_NIOS.wapi_request('GET',object_type=ref+'?_return_fields=additional_ip_list',grid_vip=config.grid_vip)
                print(response)
		data = ['"enable_bgp": false','"enable_ospf": false']
		for i in data:
			if i in response:
				assert True
			else:
				assert False
		
	print(data)
	print("Test Case 31 Execution Completed")

    @pytest.mark.run(order=32)
    def test_32_Remove_OSPF_and_BGP_configuration_on_both_members(self):
        print("\n============================================\n")
        print("remove ospf and bgp configurations on both members")
        print("\n============================================\n")
        for i in range(0,2):
                get_ref = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                res = eval(json.dumps(res))
                ref=(res)[i]['_ref']
                print(ref)
                data={"bgp_as": [{"as": 12,"holddown": 16,"keepalive": 4,"link_detect": False,"neighbors": []}],"ospf_list": []}
                response = ib_NIOS.wapi_request('PUT',ref=ref, fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
        print(data)
        print("Test case 32 Execution Completed")


    @pytest.mark.run(order=33)
    def test_33_Validate_removed_ospf_and_bgp_configurations_on_both_members(self):
        print("\n============================================\n")
        print("Validate removed ospf and bgp configurations on both members")
        print("\n============================================\n")
        for i in range(0,2):
                get_ref = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                res = eval(json.dumps(res))
                ref=(res)[i]['_ref']
                print(ref)
		response = ib_NIOS.wapi_request('GET',object_type=ref+'?_return_fields=ospf_list,bgp_as',grid_vip=config.grid_vip)
                print(response)
                data={'"bgp_as"','"as": 12','"holddown": 16','"keepalive": 4','"link_detect": false','"neighbors": []','"ospf_list": []'}
		for i in data:
			if i in response:
				assert True
			else:
				assert False
        print(data)
        print("Test case 33 Execution Completed")



    @pytest.mark.run(order=34)
    def test_34_Run_bird_conf_file_to_start_the_neighborship_process(self):
        print("\n============================================\n")
        print("Run bird.conf file to start the neighborship process")
        print("\n============================================\n")
        try:
                  child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.client_v4)
                  child.logfile=sys.stdout
                  child.expect('password: ')
                  child.sendline('infoblox')
                  child.expect('#')
                  child.sendline('rm -rf /usr/local/etc/11216bird.conf')
                  child.expect('#')
                  child.sendline('rm -rf /import/qaddi/API_Automation/WAPI_PyTest/suites/customer_bug_auto_2021/11216bird.conf')
                  child.expect('#')
                  child.sendline('cd /import/qaddi/API_Automation/WAPI_PyTest/suites/customer_bug_auto_2021')
                  child.expect('#')
                  sleep(10)
                  child.sendline('ls')
                  child.expect('#')
                  output = child.before
                  if "11216bird.conf" in output:
                        assert False
                        print("Failed to remove  11216bird.conf file")
                  else:
                        assert True
        finally:
                  child.close()
        print("Test case 34 Execution Completed")

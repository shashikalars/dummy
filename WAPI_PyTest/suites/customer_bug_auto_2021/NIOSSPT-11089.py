#!/usr/bin/env python
__author__ = "Prasad K"
__email__  = "pkondisetty@@infoblox.com"
__NIOSSPT__ = "NIOSSPT-11089"
####################################################################################
#  Grid Set up required:                                                           #
#  1. Grid Master with one threat protection member                                #
#  2. Licenses : DNS, Grid, NIOS(IB_1415)                                          #
#  3. Enable DNS services on IPv6                                                  #
#  NIOSSPT Cloud JIRA link : https://infoblox.atlassian.net/browse/NIOS-76715      #
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

class NIOSSPT_11089(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_01_Enable_IPv6_port_on_master(self):
        print("\n============================================\n")
        print("Enable IPv6 Port on master")
        print("\n============================================\n")
	get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        print(get_ref)
        ref = json.loads(get_ref)[0]['_ref']
        data = {"use_lan_ipv6_port": True}
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
        print(response)
	print("Test case 01 Execution Completed")

    @pytest.mark.run(order=2)
    def test_02_Validate_enabled_ipv6_port_on_master(self):
        print("\n============================================\n")
        print("Validate enabled IPv6 Port on master")
        print("\n============================================\n")
	grid =  ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=use_lan_ipv6_port",grid_vip=config.grid_vip)
        print(response)
        data = '"use_lan_ipv6_port": true'
        if data in response:
              assert True
	      print(data)
        else:
              assert False
	print("Test case 02 Execution Completed")

    @pytest.mark.run(order=3)
    def test_03_Configure_OSPF_IPv6_configuration_on_master(self):
        print("\n============================================\n")
        print("Configure OSFP IPV4 configuration on master")
        print("\n============================================\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
        res = json.loads(get_ref)
        res = eval(json.dumps(res))
        ref=(res)[0]['_ref']
	data = {"ospf_list": [{"area_id": "0.0.0.12","area_type": "STANDARD","authentication_type": "NONE","auto_calc_cost_enabled": False,"cost": 100,"dead_interval": 40,"enable_bfd": False,"hello_interval": 10,"interface": "LAN_HA","is_ipv4": False,"key_id": 1,"retransmit_interval": 5,"transmit_delay": 1}]}
        response = ib_NIOS.wapi_request('PUT',ref=ref, fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)
	sleep(05)
        print("Test case 03 Execution Completed")

    @pytest.mark.run(order=4)
    def test_04_Validate_Configured_OSPF_IPv6_configuration_on_master(self):
        print("\n============================================\n")
        print("Validate Configured OSPF IPv6 configuration on master")
        print("\n============================================\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
        ref = json.loads(get_ref)[0]['_ref']
        ref = eval(json.dumps(ref))
        response = ib_NIOS.wapi_request('GET',object_type=ref+'?_return_fields=ospf_list',grid_vip=config.grid_vip)
        print(response)
        data = ['"area_id": "0.0.0.12"','"area_type": "STANDARD"','"authentication_type": "NONE"','"auto_calc_cost_enabled": false','"cost": 1','"dead_interval": 40','"enable_bfd": false','"hello_interval": 10','"interface": "LAN_HA"','"is_ipv4": false','"key_id": 1','"retransmit_interval": 5','"transmit_delay": 1']
        for i in data:
             if i in response:
                 assert True
		 print(i)
             else:
                 assert False
        print("Test case 04 Execution Completed")

    @pytest.mark.run(order=5)
    def test_05_Configure_Three_IPv6_loopback_interfaces_and_enable_ospf_for_only_two_of_these_IPv6_loopback_interfaces(self):
        print("\n============================================\n")
        print("Configured IPv6 loopback interfaces and enabled ospf for two of these IPv6 loopback interfaces")
        print("\n============================================\n")
        grid =  ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
	print(ref)
	data = {"additional_ip_list": [{"anycast": True,"enable_bgp": False,"enable_ospf": True,"interface": "LOOPBACK","ipv6_network_setting": {"cidr_prefix": 128,"dscp": 0,"enabled": True,"primary": False,"use_dscp": False,"virtual_ip": "11:22:33:44::1"}},{"anycast": True,"enable_bgp": False,"enable_ospf": True,"interface": "LOOPBACK","ipv6_network_setting": {"cidr_prefix": 128,"dscp": 0,"enabled": True,"primary": False,"use_dscp": False,"virtual_ip": "11:22:33:44::2"}},{"anycast": True,"enable_bgp": False,"enable_ospf": False,"interface": "LOOPBACK","ipv6_network_setting": {"cidr_prefix": 128,"dscp": 0,"enabled": True,"primary": False,"use_dscp": False,"virtual_ip": "11:22:33:44::3"}}]}
        response = ib_NIOS.wapi_request('PUT', object_type = ref + "?_return_fields=additional_ip_list",fields=json.dumps(data),grid_vip=config.grid_vip)
	print(response)
	sleep(300)
        print("Test case 05 Execution Completed")


    @pytest.mark.run(order=6)
    def test_06_Validate_Configure_Three_IPv6_loopback_interfaces_and_enabled_ospf_for_two_interfaces(self):
        print("\n============================================\n")
        print("Validate configured three IPv6 loopback interfaces and enbaled ospf for two interfaces")
        print("\n============================================\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
        ref = json.loads(get_ref)[0]['_ref']
        ref = eval(json.dumps(ref))
        response = ib_NIOS.wapi_request('GET',object_type=ref+'?_return_fields=additional_ip_list',grid_vip=config.grid_vip)
        print(response)
	value = response.count('"enable_ospf": true')
	if value == 2 :
		assert True
	else:
		assert False
        data = ['"virtual_ip": "11:22:33:44::1"','"virtual_ip": "11:22:33:44::2"','"virtual_ip": "11:22:33:44::3"','"enable_ospf": false']
        for i in data:
             if i in response:
                    assert True
		    print(i)
             else:
                    assert False
        print("Test case 06 Execution Completed")

    @pytest.mark.run(order=7)
    def test_07_Associate_configured_IPv6_anycast_IP_for_master_at_member_DNS_properties(self):
        print("\n============================================\n")
        print("Associate configured IPv6 anycast IP for master at member DNS properties")
        print("\n============================================\n")
        grid =  ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        print(ref)
	data = {"additional_ip_list_struct": [{"ip_address": "11:22:33:44::1"},{"ip_address": "11:22:33:44::2"},{"ip_address": "11:22:33:44::3"}]}
	response = ib_NIOS.wapi_request('PUT', object_type = ref + "?_return_fields=additional_ip_list_struct",fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)
	sleep(05)
        print("Test case 07 Execution Completed")

    @pytest.mark.run(order=8)
    def test_08_Validate_associated_IPv6_anycast_IP_at__member_dns_properties(self):
        print("\n============================================\n")
        print("Validate associated IPv6 anycast IP at member dns properties")
        print("\n============================================\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        ref = json.loads(get_ref)[0]['_ref']
        ref = eval(json.dumps(ref))
        response = ib_NIOS.wapi_request('GET',object_type=ref+'?_return_fields=additional_ip_list_struct',grid_vip=config.grid_vip)
        print(response)
        data=['"ip_address": "11:22:33:44::1"','"ip_address": "11:22:33:44::2"','"ip_address": "11:22:33:44::3"']
	for i in data:
         	if i in response:
                        assert True
			print(i)
                else:
                        assert False
        print("Test case 08 Execution Completed")

    @pytest.mark.run(order=9)
    def test_09_Enable_DNS_Service_on_master(self):
        print("\n============================================\n")
        print("Enable DNS service on master")
        print("\n============================================\n")
        data = {"enable_dns": True}
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        ref = json.loads(get_ref)[0]['_ref']
        response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)
	sleep(10)
        print("Test case 09 Execution Completed")


    @pytest.mark.run(order=10)
    def test_10_Validate_Enabled_dns_service_on_master_and_kill_the_running_bird_process_in_bird_client(self):
        print("\n============================================\n")
        print("Validate enabled DNS service on master and kill the running bird process in bird client ")
        print("\n============================================\n")
        data = '"enable_dns": true'
        member_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        member_ref = json.loads(member_ref)[0]['_ref']
        response = ib_NIOS.wapi_request('GET',ref=member_ref+'?_return_fields=enable_dns',grid_vip=config.grid_vip)
        print(response)
        if data in response:
             assert True
        else:
             assert False
        print(data)
	try:
                  child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.bird_client)
                  child.logfile=sys.stdout
                  child.expect('password: ')
                  child.sendline('infoblox')
                  child.expect('#')
                  child.sendline('ps -ax | grep bird | grep Ssl')
                  child.expect('#')
                  bird_process = child.before
                  bird_process = bird_process.replace("\n",'').replace("\r",'').replace('ps -ax | grep bird | grep Ssl','').replace(' ','')
                  bird_process = bird_process.split("?",1)
                  bird_process = bird_process[0]
                  print(bird_process)
                  child.sendline('kill '+bird_process)
                  child.expect('#')
                  child.sendline('ps -ax | grep bird')
                  child.expect('#')
                  bird_process_output = child.before
                  if bird_process in bird_process_output:
                        assert False
                  else:
                        assert True
        except:
                  assert False
        finally:
                  child.close()
        print("Test case 10 Execution Completed")

    @pytest.mark.run(order=11)
    def test_11_Copy_bird_conf_to_client(self):
        print("\n============================================\n")
        print("copying bird.conf file to client")
        print("\n============================================\n")
	try:
                  child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.bird_client)
		  child.logfile=sys.stdout
		  child.expect('password: ')
		  child.sendline('infoblox')
                  child.expect('#')
                  child.sendline('scp -pr /import/qaddi/API_Automation_27_06/WAPI_PyTest/suites/prasad_k/bird6_NIOSSPT11089.conf root@'+config.bird_client+':/usr/local/etc')
                  child.expect('password: ')
                  child.sendline('infoblox')
                  child.expect('#')
        except:
                  print("Failed to copy the bird.conf file ")
                  assert False
        finally:
                  child.close()
        print("Test Case 11 Execution Completed")

    @pytest.mark.run(order=12)
    def test_12_Validate_advertised_ipv6_loopback_adress_which_is_not_assigned_to_ospf(self):
        print("\n============================================\n")
        print("validate advertised ipv6 loopback address which is not assigned to ospf")
        print("\n============================================\n")
	sleep(05)
        try:
		  child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.bird_client)
                  child.logfile=sys.stdout
                  child.expect('password: ')
		  child.sendline('infoblox')
		  child.expect('#')
                  child.sendline('bird6 -c /usr/local/etc/bird6_NIOSSPT11089.conf')
                  child.expect('#')
		  child.sendline('birdc6')
		  child.expect('>')
		  sleep(800)
		  child.sendline('show route ')
		  child.expect('>')
		  child.sendline('show route ')
		  child.expect('>')
		  output = child.before
		  print("output is",output)
		  data = {'11:22:33:44::1/128','11:22:33:44::2/128'}
		  for i in data:
			if i in output:
				print("Configured IPv6 Addresses are present in routes")
				assert True
		  	else:
				print("Configured IPv6 Addresses are not present in routes")
				assert False
		  print(data)
		  if '11:22:33:44::3' in output:
			print("Detected IPv6 Loopback Address which is not assigned to OSPF ")
			assert False
		  else:
			print("No IPv6 Loopback Address detected which is not assigned to OSPF ")
			assert True
        except:
                  assert False
        finally:
                  child.close()
        print("Test Case 12 Execution Completed")

###########################
## Starting Grid Cleanup ##
###########################

    @pytest.mark.run(order=13)
    def test_13_Remove_associated_IPv6_anycast_IP_for_master_at_member_dns_properties(self):
        print("\n============================================\n")
        print("Remove associated IPv6 anycast IP for master at member dns properties")
        print("\n============================================\n")
        grid =  ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        print(ref)
        data = {"additional_ip_list_struct": []}
        response = ib_NIOS.wapi_request('PUT', object_type = ref + "?_return_fields=additional_ip_list_struct",fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)
	sleep(05)
        print("Test case 13 Execution Completed")

    @pytest.mark.run(order=14)
    def test_14_Validate_removed_IPv6_anycast_IP_for_master_at_member_dns_properties(self):
        print("\n============================================\n")
        print("Validate removed IPv6 anycast IP for master at member dns properties")
        print("\n============================================\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        ref = json.loads(get_ref)[0]['_ref']
        ref = eval(json.dumps(ref))
        response = ib_NIOS.wapi_request('GET',object_type=ref+'?_return_fields=additional_ip_list_struct',grid_vip=config.grid_vip)
        print(response)
        if '"additional_ip_list_struct": []' in response:
               assert True
        else:
               assert False
        print("Test case 14 Execution Completed")

    @pytest.mark.run(order=15)
    def test_15_Remove_associated_IPv6_anycast_IP_for_master_at_member_DNS_properties(self):
        print("\n============================================\n")
        print("Remove associated IPv6 anycast IP for master at member DNS properties")
        print("\n============================================\n")
        grid =  ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        print(ref)
        data = {"additional_ip_list": []}
        response = ib_NIOS.wapi_request('PUT', object_type = ref + "?_return_fields=additional_ip_list",fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)
	sleep(150)
        print("Test case 15 Execution Completed")


    @pytest.mark.run(order=16)
    def test_16_Validate_removed_IPv6_anycast_IP_for_master_at_member_DNS_properties(self):
        print("\n============================================\n")
        print("Validate removed IPv6 anycast IP for master at member DNS properties")
        print("\n============================================\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
        ref = json.loads(get_ref)[0]['_ref']
        ref = eval(json.dumps(ref))
        response = ib_NIOS.wapi_request('GET',object_type=ref+'?_return_fields=additional_ip_list',grid_vip=config.grid_vip)
        print(response)
        if '"additional_ip_list": []' in response:
              assert True
        else:
              assert False
        print("Test case 16 Execution Completed")


    @pytest.mark.run(order=17)
    def test_17_Remove_OSPF_IPv6_configuration_for_master(self):
        print("\n============================================\n")
        print("Remove OSFP IPv6 configuration for master")
        print("\n============================================\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
        res = json.loads(get_ref)
        res = eval(json.dumps(res))
        ref=(res)[0]['_ref']
        data = {"ospf_list": []}
        response = ib_NIOS.wapi_request('PUT',ref=ref, fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)
        print("Test case 17 Execution Completed")

    @pytest.mark.run(order=18)
    def test_18_Validate_removed_OSPF_IPv6_configuration_for_master(self):
        print("\n============================================\n")
        print("validate removed ospf ipv6 configuration for master")
        print("\n============================================\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
        ref = json.loads(get_ref)[0]['_ref']
        ref = eval(json.dumps(ref))
        response = ib_NIOS.wapi_request('GET',object_type=ref+'?_return_fields=ospf_list',grid_vip=config.grid_vip)
        print(response)
        if '"ospf_list": []' in response:
               assert True
        else:
               assert False
        print("Test case 18 Execution Completed")

    @pytest.mark.run(order=19)
    def test_19_Disbale_DNS_Service_on_master(self):
        print("\n============================================\n")
        print("Disable DNS service on master")
        print("\n============================================\n")
        data = {"enable_dns": False}
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        ref = json.loads(get_ref)[0]['_ref']
        response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)
        print("Test case 19 Execution Completed")

    @pytest.mark.run(order=20)
    def test_20_Validate_disabled_dns_service_on_master(self):
        print("\n============================================\n")
        print("Validate disabled DNS service on master")
        print("\n============================================\n")
        data = '"enable_dns": false'
        member_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        member_ref = json.loads(member_ref)[0]['_ref']
        response = ib_NIOS.wapi_request('GET',ref=member_ref+'?_return_fields=enable_dns',grid_vip=config.grid_vip)
        print(response)
        if data in response:
             assert True
        else:
             assert False
        print(data)
        print("Test case 20 Execution Completed")

    @pytest.mark.run(order=21)
    def test_21_Delete_and_validate_copied_bird_conf_file_from_client(self):
        print("\n============================================\n")
        print("Delete and validate copied bird conf file from client")
        print("\n============================================\n")
        sleep(05)
        try:
                  child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.bird_client)
                  child.logfile=sys.stdout
                  child.expect('password: ')
                  child.sendline('infoblox')
                  child.expect('#')
                  child.sendline('rm -rf /usr/local/etc/bird6_NIOSSPT11089.conf')
                  child.expect('#')
		  child.sendline('cd /usr/local/etc')
		  child.expect('#')
		  child.sendline('ls')
		  child.expect('#')
		  files_list = child.before
		  print(files_list)
		  if 'bird6_NIOSSPT11089.conf' in files_list:
			assert False
		  else:
			assert True
        except:
                  assert False
        finally:
                  child.close()
        print("Test Case 21 Execution Completed")


    @pytest.mark.run(order=22)
    def test_22_Kill_the_bird_process_running_in_bird_client(self):
        print("\n============================================\n")
        print("Kill the bird process running in bird client")
        print("\n============================================\n")
        sleep(05)
        try:
                  child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.bird_client)
                  child.logfile=sys.stdout
                  child.expect('password: ')
                  child.sendline('infoblox')
                  child.expect('#')
                  child.sendline('ps -ax | grep bird | grep Ssl')
                  child.expect('#')
                  bird_process = child.before
                  bird_process = bird_process.replace("\n",'').replace("\r",'').replace('ps -ax | grep bird | grep Ssl','').replace(' ','')
                  bird_process = bird_process.split("?",1)
                  bird_process = bird_process[0]
                  print(bird_process)
                  child.sendline('kill '+bird_process)
                  child.expect('#')
                  child.sendline('ps -ax | grep bird')
                  child.expect('#')
                  bird_process_output = child.before
                  if bird_process in bird_process_output:
                        assert False
                  else:
                        assert True
        except:
                  assert False
        finally:
                  child.close()
        print("Test Case 22 Execution Completed")


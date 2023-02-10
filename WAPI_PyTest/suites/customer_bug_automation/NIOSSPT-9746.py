#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Licenses : DNS(enabled), DHCP, Grid                                   #
#############################################################################
import os
import re
import config
import pytest
import unittest
import logging
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import pexpect
import subprocess
import shlex
import commands

class NIOSSPT_9746(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_000_start_IPv4_DHCP_service(self):
        print("Enable the DPCH service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties?_return_fields=enable_dhcp", grid_vip=config.grid_vip)
        ref = json.loads(get_ref)[0]['_ref']
        data = {"enable_dhcp":True}
        response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==404:
                print("Failure: Create an ipv4 network")
                assert False
            else:
                print("Success: Create an ipv4 network")
                assert True
    
    @pytest.mark.run(order=2)
    def test_001_Create_IPv4_network(self):
        print("Create an ipv4 network default network view and with out Extensible attributes of Subscriber services")
        data = {"network": "10.0.0.0/8","network_view": "default","members":[{"_struct": "dhcpmember","ipv4addr":config.grid_vip}]}
        response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==404:
                print("Failure: Create an ipv4 network")
                assert False
            else:
                print("Success: Create an ipv4 network")
                assert True
                
        print("Restart DHCP Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)
                    
                
    @pytest.mark.run(order=3)
    def test_002_create_IPv4_Range(self):
        sleep(10)
        print("Create an IPv4 range in defaultnetwork view")
        data = {"network":"10.0.0.0/8","start_addr":"10.0.0.1","end_addr":"10.0.0.108","network_view": "default","member":{"_struct":"dhcpmember","ipv4addr":config.grid_vip}}
        response = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(data), grid_vip=config.grid_vip)
        print (response)
            
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==404:
                print("Failure: Create an IPv4 range")
                assert False
            else:
                print("Success: Create an IPv4 range")
                assert True

        print("Restart DHCP Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)
            
    @pytest.mark.run(order=4)
    def test_003_create_MAC_Filter(self):
        print("Create_MAC_Filter")
        data = {"name":"mac_filter"}
        response = ib_NIOS.wapi_request('POST', object_type="filtermac", fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==404:
                print("Failure: Create_MAC_Filter")
                assert False
            else:
                print("Success: Create_MAC_Filter")
                assert True
        
    
    @pytest.mark.run(order=5)
    def test_004_create_MAC_Filter_Address(self):
        print("Create_MAC_Filter_address 00:00:00:00:00:01")
        data = {"filter":"mac_filter","mac":"00:00:00:00:00:01"}

        response = ib_NIOS.wapi_request('POST', object_type="macfilteraddress", fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==404:
                print("Failure: Create_MAC_Filter_address 00:00:00:00:00:01")
                assert False
            else:
                print("Success: Create_MAC_Filter_address 00:00:00:00:00:01")
                assert True
    
    
    @pytest.mark.run(order=6)
    def test_005_create_Fingerprint_Filter(self):
        print("Create_Fingerprint Filter Microsoft Windows Kernel 5.1,5.2")
        #data = {"name":"Fingerprint","fingerprint":["Microsoft Windows Kernel 5.1,5.2"]}
        data = {"name":"Fingerprint","fingerprint":["Microsoft Windows XP (Version 5.1, 5.2)"]}
        response = ib_NIOS.wapi_request('POST', object_type="filterfingerprint", fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==404:
                print("Failure: Create_Fingerprint Filter Microsoft Windows XP (Version 5.1, 5.2)")
                assert False
            else:
                print("Success: Create_Fingerprint Filter Microsoft Windows XP (Version 5.1, 5.2)")
                assert True

    
    @pytest.mark.run(order=7)
    def test_006_range_assign_fingerprint_Filter_Allow(self):
        print("Edit the range and assign fingerprint filter to Allow")
        get_ref = ib_NIOS.wapi_request('GET', object_type='range?_return_fields=fingerprint_filter_rules')
        data = {"fingerprint_filter_rules":[{"filter": "Fingerprint","permission": "Allow"}]}
        stat_range="10.0.0.1"
        
        for ref in json.loads(get_ref):
            if stat_range in  ref['_ref']:
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401 or response[0]==404:
                        print("Failure: Edit the range and assign fingerprint filter to Allow")
                        assert False
                    else:
                        print("Success: Edit the range and assign fingerprint filter to Allow")
                        assert True
        
        
        
    @pytest.mark.run(order=8)
    def test_007_range_assign_mac_Filter_Allow(self):
        print("Edit the range and assign mac filter to Allow")
        get_ref = ib_NIOS.wapi_request('GET', object_type='range?_return_fields=mac_filter_rules')
        data = {"mac_filter_rules":[{"filter": "mac_filter","permission": "Allow"}]}
        stat_range="10.0.0.1"
        
        for ref in json.loads(get_ref):
            if stat_range in  ref['_ref']:
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401 or response[0]==404:
                        print("Failure: Edit the range and assign mac filter to Allow")
                        assert False
                    else:
                        print("Success: Edit the range and assign mac filter to Allow")
                        assert True
        print("Restart DHCP Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(60)
            
    @pytest.mark.run(order=9)
    def test_008_requesting_ipv4_lease_with_Allow_Allow(self):
        print("Allow fingerprint filter Allow Mac filter in range")
        #dras_validation= 'sudo /import/qaddi/API_Automation/niti/tools/dras/dras_opt55/dras -i '+str(config.grid_vip)+' -a 00:00:00:00:00:01 '+'-n 1 -D -O 55:010f03062c2e2f1f21f92b'
	dras_validation= 'sudo /import/tools/qa/tools/dras_opt55/dras -i '+str(config.grid_vip)+' -a 00:00:00:00:00:01 '+'-n 1 -D -O 55:010f03062c2e2f1f21f92b'
        print(dras_validation)
        out1 = commands.getoutput(dras_validation)
        print out1
        assert re.search(r'.*ompleted.*1',out1)

            
            
    @pytest.mark.run(order=10)
    def test_009_range_assign_fingerprint_Filter_Deny(self):
        print("Edit the range and assign fingerprint filter to Deny")
        get_ref = ib_NIOS.wapi_request('GET', object_type='range?_return_fields=fingerprint_filter_rules')
        data = {"fingerprint_filter_rules":[{"filter": "Fingerprint","permission": "Deny"}]}
        stat_range="10.0.0.1"
        
        for ref in json.loads(get_ref):
            if stat_range in  ref['_ref']:
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401 or response[0]==404:
                        print("Failure: Edit the range and assign fingerprint filter to Deny")
                        assert False
                    else:
                        print("Success: Edit the range and assign fingerprint filter to Deny")
                        assert True
        
        
        
        
    @pytest.mark.run(order=11)
    def test_010_edit_range_assign_mac_Filter_Allow(self):
        print("Edit the range and assign mac filter to Allow")
        get_ref = ib_NIOS.wapi_request('GET', object_type='range?_return_fields=mac_filter_rules')
        data = {"mac_filter_rules":[{"filter": "mac_filter","permission": "Allow"}]}
        stat_range="10.0.0.1"
        
        for ref in json.loads(get_ref):
            if stat_range in  ref['_ref']:
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401 or response[0]==404:
                        print("Failure: Edit the range and assign mac filter to Allow")
                        assert False
                    else:
                        print("Success: Edit the range and assign mac filter to Allow")
                        assert True
        
        print("Restart DHCP Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)

        
        
    @pytest.mark.run(order=12)
    def test_011_requesting_ipv4_Deny_Allow(self):
        print("Deny fingerprint filter Allow Macfilter in range")
	#dras_validation= 'sudo /import/qaddi/API_Automation/niti/tools/dras/dras_opt55/dras -i '+str(config.grid_vip)+' -a 00:00:00:00:00:01 '+'-n 1 -D -O 55:010f03062c2e2f1f21f92b'
        dras_validation= 'sudo /import/tools/qa/tools/dras_opt55/dras -i '+str(config.grid_vip)+' -a 00:00:00:00:00:01 '+'-n 1 -D -O 55:010f03062c2e2f1f21f92b'
        print(dras_validation)
	out1 = commands.getoutput(dras_validation)
        print out1
        assert re.search(r'No.*eplies.*eceived',out1)
        
 
    
    
    @pytest.mark.run(order=13)
    def test_012_range_assign_fingerprint_Filter_Allow(self):
        print("Edit the range and assign fingerprint filter to Allow")
        get_ref = ib_NIOS.wapi_request('GET', object_type='range?_return_fields=fingerprint_filter_rules')
        data = {"fingerprint_filter_rules":[{"filter": "Fingerprint","permission": "Allow"}]}
        stat_range="10.0.0.1"
        
        for ref in json.loads(get_ref):
            if stat_range in  ref['_ref']:
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401 or response[0]==404:
                        print("Failure: Edit the range and assign fingerprint filter to Allow")
                        assert False
                    else:
                        print("Success: Edit the range and assign fingerprint filter to Allow")
                        assert True
        
        
        
        
    @pytest.mark.run(order=14)
    def test_013_edit_range_assign_mac_Filter_Deny(self):
        print("Edit the range and assign mac filter to Deny")
        get_ref = ib_NIOS.wapi_request('GET', object_type='range?_return_fields=mac_filter_rules')
        data = {"mac_filter_rules":[{"filter": "mac_filter","permission": "Deny"}]}
        stat_range="10.0.0.1"
        
        for ref in json.loads(get_ref):
            if stat_range in  ref['_ref']:
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                print(response)
                if type(response) == tuple: 
                    if response[0]==400 or response[0]==401 or response[0]==404:
                        print("Failure: Edit the range and assign mac filter to Deny")
                        assert False
                    else:
                        print("Success: Edit the range and assign mac filter to Deny")
                        assert True
        print("Restart DHCP Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)
        
        
        
        
    @pytest.mark.run(order=15)
    def test_014_requesting_ipv4_Allow_Deny(self):
        print("Allow fingerprint filter Deny Macfilter in range")
        dras_validation= 'sudo /import/tools/qa/tools/dras/dras -i '+str(config.grid_vip)+' -a 00:00:00:00:00:01 '+'-n 1 -D -O 55:010f03062c2e2f1f21f92b'
        out1 = commands.getoutput(dras_validation)
        print out1
        assert re.search(r'No.*eplies.*eceived',out1)
       
 
                
                
    @pytest.mark.run(order=16)
    def test_015_range_assign_fingerprint_Filter_Deny(self):
        print("Edit the range and assign fingerprint filter to Deny")
        get_ref = ib_NIOS.wapi_request('GET', object_type='range?_return_fields=fingerprint_filter_rules')
        data = {"fingerprint_filter_rules":[{"filter": "Fingerprint","permission": "Deny"}]}
        stat_range="10.0.0.1"
        
        for ref in json.loads(get_ref):
            if stat_range in  ref['_ref']:
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401 or response[0]==404:
                        print("Failure: Edit the range and assign fingerprint filter to Deny")
                        assert False
                    else:
                        print("Success: Edit the range and assign fingerprint filter to Deny")
                        assert True
        
        
        
        
    @pytest.mark.run(order=17)
    def test_016_edit_range_assign_mac_Filter_Deny(self):
        print("Edit the range and assign mac filter to Deny")
        get_ref = ib_NIOS.wapi_request('GET', object_type='range?_return_fields=mac_filter_rules')
        data = {"mac_filter_rules":[{"filter": "mac_filter","permission": "Deny"}]}
        stat_range="10.0.0.1"
        
        for ref in json.loads(get_ref):
            if stat_range in  ref['_ref']:
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401 or response[0]==404:
                        print("Failure: Edit the range and assign mac filter to Deny")
                        assert False
                    else:
                        print("Success: Edit the range and assign mac filter to Deny")
                        assert True
        print("Restart DHCP Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)
        
        
        
        
    @pytest.mark.run(order=18)
    def test_017_requesting_ipv4_Deny_Deny(self):
        print("Deny fingerprint filter Deny Macfilter in range")
        dras_validation= 'sudo /import/tools/qa/tools/dras/dras -i '+str(config.grid_vip)+' -a 00:00:00:00:00:01 '+'-n 1 -D -O 55:010f03062c2e2f1f21f92b'
        out1 = commands.getoutput(dras_validation)
        print out1
        assert re.search(r'No.*eplies.*eceived',out1)


    @pytest.mark.run(order=19)
    def test_018_cleanup(self):
        print("Clean up all created objects")
        get_ref = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
             
            print(response)
                    
            if type(response) == tuple:
                        
                if response[0]==400 or response[0]==401:
                            
                    assert False
                else:
                    assert True
             
        
        get_ref = ib_NIOS.wapi_request('GET', object_type="range", grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
             
            print(response)
                    
            if type(response) == tuple:
                        
                if response[0]==400 or response[0]==401:
                            
                    assert False
                else:
                    assert True
      
        get_ref = ib_NIOS.wapi_request('GET', object_type="filtermac", grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
             
            print(response)
                    
            if type(response) == tuple:
                        
                if response[0]==400 or response[0]==401:
                            
                    assert False
                else:
                    assert True
                    
        get_ref = ib_NIOS.wapi_request('GET', object_type="filterfingerprint", grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
             
            print(response)
                    
            if type(response) == tuple:
                        
                if response[0]==400 or response[0]==401:
                            
                    assert False
                else:
                    assert True
                
        
        print("Restart DHCP Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)

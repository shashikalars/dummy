#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
# Grid Set up required:                                                     #
#  1. Licenses : Grid                                                       #
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
import shlex
from time import sleep
from subprocess import Popen, PIPE
import pexpect
import paramiko
from scapy import *
from scapy.utils import RawPcapReader
from scapy.all import *
import shutil
# from ib_utils.start_stop_logs import log_action as log
# from ib_utils.file_content_validation import log_validation as logv

class NIOS_71011(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_start_dns_services(self):
       print("Start DNS service")
       get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns')
       print(get_ref)
       for ref in json.loads(get_ref):
           response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps({"enable_dns":True}))
           if type(response) == tuple:
               if response[0]==400 or response[0]==401:
                   assert False
        

    @pytest.mark.run(order=2)
    def test_001_dns_services_zone_transfer_settings(self):
       print("DNS service with zone transfer settings")
       get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns')
       print(get_ref)
       for ref in json.loads(get_ref):
            data={"allow_transfer": [{
                    "_struct": "addressac",
                    "address": "Any",
                    "permission": "ALLOW"
                }]}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)
            print(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    print("Failure: DNS services and zone transfer settings")
                    assert False

    @pytest.mark.run(order=3)
    def test_002_Creating_NSG_group_one(self):
        print("Creating NSG groups")
        data = {"name": "NSG_1",
                "grid_primary": [{"name": config.grid_fqdn,
                "stealth": False}]}
                
        
        response = ib_NIOS.wapi_request('POST', object_type="nsgroup", fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)
        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==404:
                print("Failure: Create A NSG group1")
                assert False
            else:
                print("Success: Create A NSG group1")
                assert True
                   
    @pytest.mark.run(order=4)
    def test_003_Creating_NSG_group_two(self):
        data2={"name": "NSG_2","grid_primary": [{
                "name": config.grid_fqdn,
                "stealth": False }] }
        response = ib_NIOS.wapi_request('POST', object_type="nsgroup", fields=json.dumps(data2),grid_vip=config.grid_vip)
        print(response)
        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==404:
                print("Failure: Create A NSG group2")
                assert False
            else:
                print("Success: Create A NSG group2")
                assert True
                   
    @pytest.mark.run(order=5)
    def test_004_create_Authoritative_Zone1(self): 
        print("Create testing.com auth zone1 and assigned to GM")
        data = {"fqdn": "testing.com",
                "view":"default",
                "ns_group": "NSG_1"}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==404:
                print("Failure: create_Forward_Mapping_Zone1")
                assert False
       
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(10)
        
    @pytest.mark.run(order=6)
    def test_005_create_Authoritative_Zone2(self): 
        print("Create sub.testing.com auth zone2 and assigned to GM")
        data = {"fqdn": "sub.testing.com",
                "view":"default",
                "ns_group": "NSG_1",
                "zone_format": "FORWARD",
                }
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==404:
                print("Failure: create_Forward_Mapping_Zone1")
                assert False
                
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(10)
        
    @pytest.mark.run(order=7)
    def test_006_DNSSEC_signed_parent_zone(self):                  
                
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth')
        for ref in json.loads(get_ref):
            if "testing.com" in ref['_ref']:
                response = ib_NIOS.wapi_request('POST', ref=ref['_ref'], params='?_function=dnssec_operation', fields=json.dumps({"operation":"SIGN"}))
             
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401 or response[0]==404:
                        display_msg("Failure: Sign the parent zone")
                        assert False 
                        
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(10)

    @pytest.mark.run(order=8)
    def test_007_change_the_NSG_Group(self):  
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth')
        for ref in json.loads(get_ref):
            if 'sub.testing.com' in ref['_ref']:
                data={"ns_group": "NSG_2"}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401 or response[0]==404:
                        print("Failure: Change the NSG group ")
                        assert False
    
    
    @pytest.mark.run(order=9)
    def test_08_cleanup(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="nsgroup", grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
             
            print(response)
                    
            if type(response) == tuple:
                        
                if response[0]==400 or response[0]==401 or response[0]==404:
                            
                    assert False
                else:
                    assert True

        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)

        for ref in json.loads(get_ref):
            if 'testing.com' == ref["fqdn"]:
                response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
                 
                print(response)
                        
                if type(response) == tuple:
                            
                    if response[0]==400 or response[0]==401 or response[0]==404:
                                
                        assert False
                    else:
                        assert True
        # for ref in json.loads(get_ref):            
            # if 'testing.com' in ref['_ref']:
                # response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
                 
                # print(response)
                        
                # if type(response) == tuple:
                            
                    # if response[0]==400 or response[0]==401 or response[0]==404:
                                
                        # assert False
                    # else:
                        # assert True
        
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(10)
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

class NIOSSPT_10588(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_admin_group_and_non_superuser(self):
        print("Create group_test")
        group_data = {"name": "group_test","access_method": ["GUI","API"], "roles":[]}
        response = ib_NIOS.wapi_request('POST',object_type="admingroup",fields=json.dumps(group_data))
        print(response)
        #ref=json.loads(response)['_ref']
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create group_test")
                assert False
            else:
                print("Success: Create group_test")
                assert True
                
        print("Create user in group_test")
        user_data = {"name": "user","password": "infoblox","admin_groups": ["group_test"]}
        response = ib_NIOS.wapi_request('POST',object_type="adminuser",fields=json.dumps(user_data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create user in group_test")
                assert False
            else:
                print("Success: Create user in group_test")
                assert True
                
        print("Create Global Permission as 'All Zones' for group_test")
        data = [{"method":"POST","object":"permission","data":{"group":"group_test","resource_type":"ZONE","permission":"WRITE"}},
                {"method":"POST","object":"permission","data":{"group":"group_test","resource_type":"CSV_IMPORT_TASK","permission":"WRITE"}},
                {"method":"POST","object":"permission","data":{"group":"group_test","resource_type":"HOST","permission":"WRITE"}}]
        response = ib_NIOS.wapi_request('POST',object_type="request",fields=json.dumps(data))

        #data = {"group":"group_test","resource_type":"ZONE","permission":"WRITE"}
        #response = ib_NIOS.wapi_request('POST',object_type="permission",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create Global Permission as 'Zones,HOST,CSV_IMPORT_TASK ' for group_test")
                assert False
            else:
                print("Success: Create Global Permission as 'Zones,HOST,CSV_IMPORT_TASK' for group_test")
                assert True
    
        
    @pytest.mark.run(order=2)
    def test_001_create_New_AuthZone(self):
        print("Create A new Zone")
      
        data = {"fqdn": "test.com","grid_primary": [{"name": config.grid_member_fqdn,"stealth":False}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
        print response
        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==401:
                print("Failure: Create A new Zone")
                assert False
            else:
                print("Success: Create A new Zone")
                assert True
     
        print("Restart DHCP Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)
        
    @pytest.mark.run(order=3)
    def test_002_create_host_record(self):
        print("\nCreate IPV6 host record in 2222::/64 network and GET Host Record Object by logging in using user credentials")
        print("\nCreating host record in 2222::/64 network")
        data = {"ipv6addrs":[{"ipv6addr":"2222::11"}],"name":"host_rec.test.com","configure_for_dns":True}
        response = ib_NIOS.wapi_request('POST',object_type="record:host",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Creating host record in 2222::/64 network")
                assert False
            else:
                print("Success: Creating host record in 2222::/64 network")
           
        print("\nCreating host record ipv4 network")
        data = {"ipv4addrs":[{"ipv4addr":"10.0.0.1"}],"name":"host_ipv4_rec.test.com","configure_for_dns":True}
        response = ib_NIOS.wapi_request('POST',object_type="record:host",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Creating host record ipv4 network")
                assert False
            else:
                print("Success: Creating host record ipv4 network")
                
    @pytest.mark.run(order=4)
    def test_003_get_host_record_from_non_user(self):
        
        print("GET Host Record Object by logging in using user credentials")
        data={"_object" : "record:host"}    
        response = ib_NIOS.wapi_request('POST',object_type="fileop?_function=csv_export",fields=json.dumps(data))
        print(response)
        if "token" in response and "url" in response:
            print("Success: validating Token and URL present in the response")
            assert True
        else:
            print("Failure: validating Token and URL present in the response")
            assert False
            
        
    @pytest.mark.run(order=5)
    def test_cleanup_objects(self):
        
        get_ref = ib_NIOS.wapi_request('GET',object_type="adminuser")
        for ref in json.loads(get_ref):
            if 'user' in ref['name']:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])

        get_ref = ib_NIOS.wapi_request('GET',object_type="admingroup")
        for ref in json.loads(get_ref):
            if 'group' in ref['name']:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])
                
        get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth")
        for ref in json.loads(get_ref):
            if 'test.com' in ref['_ref']:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])
                
       

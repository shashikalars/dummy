#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
# Grid Set up required:                                                     #
#  1. Licenses : Grid DNS, DHCP, Grid, NIOS (IB-V1415)                      #
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

class NIOS_73689(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_000_Create_IPv4_network_container(self):
        print("Create an ipv4 network_container default network view and with out Extensible attributes of Subscriber services")
        data = {"network": "10.0.0.0/8","network_view": "default"}
        response = ib_NIOS.wapi_request('POST', object_type="networkcontainer", fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create an ipv4 network_container")
                assert False
            else:
                print("Success: Create an ipv4 network_container")
                assert True

        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)

        get_ref = ib_NIOS.wapi_request('GET',object_type='networkcontainer?_return_fields=extattrs', grid_vip=config.grid_vip)
        
        print(get_ref)
        
        for ref in json.loads(get_ref):
            if '{}' in ref['extattrs']:
                assert True

    @pytest.mark.run(order=2)
    def test_001_Create_extensible_attribute(self):
        print("Create an ipv4 network_container default network view and with Extensible attributes")
        data = {"name": "location_id",
                "type": "INTEGER"}
        response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef", fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create extensible attribute")
                assert False
            else:
                print("Success: Create extensible attribute")
                assert True
                
        data = {
                "name": "location_name",
                "type": "INTEGER"}
        response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef", fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create extensible attribute")
                assert False
            else:
                print("Success: Create extensible attribute")
                assert True
                
    @pytest.mark.run(order=3)
    def test_002_add_extattrs_fields_to_network_container(self):  
        get_ref = ib_NIOS.wapi_request('GET', object_type='networkcontainer')
             
        for ref in json.loads(get_ref):
        
            data = {"extattrs": {"IB Discovery Owned": {"value": "50"},"Site": {"value": "33"},"location_id": {"value": 11},"location_name": {"value": "15"}}}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            print(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    print("Failure: Added extattrs fields for network_container")
                    assert False
                else:
                    print("Success: Added extattrs fields for network_container")
                    assert True
                    
    @pytest.mark.run(order=4)
    def test_003_add_extattrs_fields_to_ranges(self): 
        print("Create an ipv4 network_container default network view and with Extensible attributes")
        net_obj = {"members":[{"_struct": "dhcpmember", "ipv4addr":config.grid_vip ,"name":config.grid_fqdn}], \
                "network": "11.0.0.0/8", "network_view": "default"}
        network1 = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(net_obj))
        print(network1)
        
        range_obj = {"start_addr":"11.0.0.100","end_addr":"11.0.0.110","member":{"_struct": "dhcpmember","ipv4addr":config.grid_vip,"name": config.grid_fqdn}, \
                 "options":[{"_struct": "dhcpoption","name":"dhcp-lease-time","num": 51,"use_option": True,"value": "120","vendor_class": "DHCP"}]}
        response = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(range_obj))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure:Adding range")
                assert False
            else:
                print("Success: Added range")
                assert True

        get_ref = ib_NIOS.wapi_request('GET', object_type='range')
             
        for ref in json.loads(get_ref):
        
            data = {"extattrs": {"IB Discovery Owned": {"value": "50"},"Site": {"value": "33"},"location_id": {"value": 11},"location_name": {"value": "15"}}}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            print(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    print("Failure: Added extattrs fields for range")
                    assert False
                else:
                    print("Success: Added extattrs fields for range")
                    assert True

    @pytest.mark.run(order=5)
    def test_004_add_extattrs_fields_to_authzone(self): 
        print("Create A new Zone")
        data = {"fqdn": "test.com","grid_primary": [{"name": config.grid_fqdn,"stealth":False}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
        print response
        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==404:
                print("Failure: Create A new Zone")
                assert False
            else:
                print("Success: Create A new Zone")
                assert True
       

        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth')
             
        for ref in json.loads(get_ref):
        
            data = {"extattrs": {"IB Discovery Owned": {"value": "50"},"Site": {"value": "33"},"location_id": {"value": 11},"location_name": {"value": "15"}}}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            print(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    print("Failure: Added extattrs fields for zone")
                    assert False
                else:
                    print("Success: Added extattrs fields for zone")
                    assert True
                    
    @pytest.mark.run(order=6)
    def test_005_add_extattrs_fields_to_record(self): 
                       
        print("Add  A records ")
        data = {"name":"a_record.test.com",
                "ipv4addr":"1.1.1.1"
                }
        response = ib_NIOS.wapi_request('POST',object_type='record:a',fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Add additional resource record")
                assert False         
                
        get_ref = ib_NIOS.wapi_request('GET', object_type='record:a')
             
        for ref in json.loads(get_ref):
        
            data = {"extattrs": {"IB Discovery Owned": {"value": "50"},"Site": {"value": "33"},"location_id": {"value": 11},"location_name": {"value": "15"}}}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            print(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    print("Failure: Added extattrs fields for record")
                    assert False
                else:
                    print("Success: Added extattrs fields for record")
                    assert True
                    
    @pytest.mark.run(order=1)
    def test_cleanup_objects(self):
        get_ref = ib_NIOS.wapi_request('GET',object_type='networkcontainer?_return_fields=extattrs', grid_vip=config.grid_vip)  
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])             
            print(response)                  
            if type(response) == tuple:                        
                assert False
                
        get_ref = ib_NIOS.wapi_request('GET',object_type='extensibleattributedef', grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            if 'location_id' in ref['_ref']:
                response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])             
                print(response)                  
                if type(response) == tuple:                        
                    assert False
                    
            if 'location_name' in ref['_ref']:
                response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])             
                print(response)                  
                if type(response) == tuple:                        
                    assert False
  
        get_ref = ib_NIOS.wapi_request('GET',object_type='zone_auth', grid_vip=config.grid_vip)  
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])             
            print(response)                  
            if type(response) == tuple:                        
                assert False

                
        get_ref = ib_NIOS.wapi_request('GET',object_type='networkcontainer', grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
            print(response)
            if type(response) == tuple:
                assert False

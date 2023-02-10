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
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv

class NIOS_79055(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_Create_IPv4_filters(self):

        mac_filter = {"name":"mac_f"}
        response = ib_NIOS.wapi_request('POST', object_type="filtermac", fields=json.dumps(mac_filter))
        print(type(response))
        if type(response) == tuple:
            print("Failure: Creating IPV4 mac filter")
            assert False
        print("Success:  Creating IPV4 mac filter")

        finger_filter = {"name":"finger_f","fingerprint": ["3Com Switches"]}
        response = ib_NIOS.wapi_request('POST', object_type="filterfingerprint", fields=json.dumps(finger_filter))
        print(response)
        if type(response) == tuple:

            print("Failure: Creating IPV4 fingerprint filter")
            assert False
        print("Success:  Creating IPV4  fingerprint filter")

        option_filter = {"name":"option_f"}
        response = ib_NIOS.wapi_request('POST', object_type="filteroption", fields=json.dumps(option_filter))
        if type(response) == tuple:
            print("Failure: Creating IPV4 filter option")
            assert False
        print("Success:  Creating IPV4 filter option")

        relay_filter = {"name":"relay_f","is_circuit_id": "NOT_SET"}
        response = ib_NIOS.wapi_request('POST', object_type="filterrelayagent", fields=json.dumps(relay_filter))
        print(response)
        if type(response) == tuple:
            print("Failure: Creating IPV4 relayagent filter")
            assert False
        print("Success:  Creating IPV4 relayagent filter")

        ipv6option_filter = {"name":"ipv6op_f"}
        response = ib_NIOS.wapi_request('POST', object_type="ipv6filteroption", fields=json.dumps(ipv6option_filter))
        print(response)
        if type(response) == tuple:
            print("Failure: Creating IPV4 IPV6option filter")
            assert False
        print("Success:  Creating IPV4 IPV6option filter")


    @pytest.mark.run(order=2)
    def test_001_Create_IPv4_network(self):
        print("Create an ipv4 network ")
        data = {"network": "10.0.0.0/8","network_view": "default","members":[{"_struct": "dhcpmember","ipv4addr":config.grid_vip}]}
        response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
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
        sleep(20) 

        #Add Range
        range_obj = {"start_addr":"10.0.0.1","end_addr":"10.0.0.10","network_view":"default","member":{"_struct": "dhcpmember", \
        "ipv4addr":config.grid_vip,"name": config.grid_fqdn}}
        response = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(range_obj))

        if type(response) == tuple:
            print("Failure: Creating IPV4 range")
            assert False
        print("Success:  Creating IPV4 range")

    @pytest.mark.run(order=3)
    def test_002_adding_IPv4_network_range_with_class_filter(self):
        data={"fingerprint_filter_rules": [{"filter": "finger_f","permission": "Allow"}],"relay_agent_filter_rules": [{"filter": "relay_f","permission": "Allow"}]}
        #data={"option_filter_rules": [{"filter": "werwerer","permission": "Allow"}]}
        grid =  ib_NIOS.wapi_request('GET', object_type="range", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            print("Failure: Adding IPV4 Network range with class filter")
            assert False
        print("Success:  Adding IPV4 Network range with class filter")


        grid =  ib_NIOS.wapi_request('GET', object_type="range?_return_fields=fingerprint_filter_rules,relay_agent_filter_rules", grid_vip=config.grid_vip)
        
        print(grid)
        if 'finger_f' in grid and 'relay_f' in grid:
            print("Success : Validating ipv4 filters are added to range or not")


    @pytest.mark.run(order=4)
    def test_003_Create_IPv6_network(self):
        data = [{"method":"POST","object":"ipv6network","data":{"network":"2222::/64","members":[{"_struct": "dhcpmember","ipv6addr":config.ipv6add}]}}]
        response = ib_NIOS.wapi_request('POST',object_type="request",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create an ipv6 network")
                assert False
            else:
                print("Success: Create an ipv6 network")
                assert True


        print("Restart DHCP Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)

        print("Create IPV6 Network Range")
        data = [{"method":"POST","object":"ipv6range","data":{"start_addr":"2222::1", "end_addr":"2222::10", "network":"2222::/64","member":{"_struct": "dhcpmember","ipv6addr":config.ipv6add,"name": config.grid_fqdn}}}]
        response = ib_NIOS.wapi_request('POST',object_type="request",fields=json.dumps(data))
        print(response)

        if type(response) == tuple:
            print("Failure: Creating IPV6 range")
            assert False
        print("Success:  Creating IPV6 range")


    @pytest.mark.run(order=5)
    def test_004_adding_IPv6_network_range_with_class_filter(self):

        data={"option_filter_rules": [{"filter": "ipv6op_f","permission": "Allow"}]}
        grid =  ib_NIOS.wapi_request('GET', object_type="ipv6range", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            print("Failure: Adding IPV6 Network range with class filter")
            assert False
        print("Success: Adding IPV4 Network range with class filter")
        
        grid =  ib_NIOS.wapi_request('GET', object_type="ipv6range?_return_fields=option_filter_rules", grid_vip=config.grid_vip)

        print(grid)
        if 'ipv6op_f' in grid:
            print("Success : Validating ipv6 filters are added to range or not")


    @pytest.mark.run(order=6)
    def test_005_clenup(self):
        log("start","/infoblox/var/audit.log",config.grid_vip)

        print("Clean up all created objects")
        get_ref = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
            print(response)
            if type(response) == tuple:
                assert False

        get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6network", grid_vip=config.grid_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
            print(response)
            if type(response) == tuple:
                assert False


        get_ref = ib_NIOS.wapi_request('GET', object_type="filterfingerprint", grid_vip=config.grid_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
            print(response)
            if type(response) == tuple:
                assert False


        get_ref = ib_NIOS.wapi_request('GET', object_type="filtermac", grid_vip=config.grid_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
            print(response)
            if type(response) == tuple:
                assert False

        get_ref = ib_NIOS.wapi_request('GET', object_type="filteroption", grid_vip=config.grid_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
            print(response)
            if type(response) == tuple:
                assert False

        get_ref = ib_NIOS.wapi_request('GET', object_type="filterrelayagent", grid_vip=config.grid_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
            print(response)
            if type(response) == tuple:
                assert False


        get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6filteroption", grid_vip=config.grid_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
            print(response)
            if type(response) == tuple:
                assert False
        
        log("stop","/infoblox/var/audit.log",config.grid_vip)
        lookfor = ["Deleted OptionFilter option_f","Deleted IPv6OptionFilter ipv6op_f"]
        for look in lookfor:

            result = logv(lookfor, '/infoblox/var/audit.log', config.grid_vip)
            if not result:
                print("Failure: Validate audit log message after deleting ipv4 and ipv6 filters")
        print("Success: Validate audit log message after deleting ipv4 and ipv6 filters")


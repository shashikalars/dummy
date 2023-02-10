#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
# Grid Set up required:                                                     #
#  1. SA grid with Licenses :DNS,DHCP                                       #
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

class NIOS_74609(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_Configure_unbound(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=recursive_resolver', grid_vip=config.grid_vip)
        print("\n")
        ref=json.loads(get_ref)[0]
        #for ref in json.loads(get_ref):

        data={"recursive_resolver":"UNBOUND"}
        response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
           
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==404:
                print("Failure: set to recursive resolver")
                assert False
            else:
                print("Success: set to recursive resolver")
                assert True
                    
                    
    @pytest.mark.run(order=2)
    def test_001_forwarder_as_client_ip_and_enable_recursion(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns?_return_fields=forwarders,allow_recursive_query', grid_vip=config.grid_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            data = {"allow_recursive_query": True, "forwarders": ["10.120.22.193"]}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            print(response)
           
            if type(response) == tuple:
                if response[0]==400 or response[0]==401 or response[0]==404:
                    print("Success: forwarder as client ip and enable recursion")
                    assert True
                else:
                    print("Failure: forwarder as client ip and enable recursion")
                    assert False  
                    
    @pytest.mark.run(order=3)
    def test_002_dig_cmd_unbound(self):
    
        args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid_vip
        args=shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
       
        child.stdin.write("dig @"+config.grid_vip+"ptr nic.de\n")
        output = child.communicate()
       
        for i in output:
            print(i)

    @pytest.mark.run(order=4)
    def test_003_cleanup_created_objects(self):
        print("Clean up all created objects")
	get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=recursive_resolver', grid_vip=config.grid_vip)
        print("\n")
        for ref in json.loads(get_ref):
            data={"recursive_resolver":"BIND"}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            print(response)

            if type(response) == tuple:
                if response[0]==400 or response[0]==401 or response[0]==404:
                    print("Success: Do not set to recursive resolver")
                    assert True
                else:
                    print("Failure: DO not set to recursive resolver")
                    assert False
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns?_return_fields=forwarders,allow_recursive_query', grid_vip=config.grid_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            data = {"allow_recursive_query": False, "forwarders": []}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            print(response)

            if type(response) == tuple:
                if response[0]==400 or response[0]==401 or response[0]==404:
                    print("Success: NO forwarder as client ip and disable recursion")
                    assert True
                else:
                    print("Failure: No forwarder as client ip and disable recursion")
                    assert False


#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
# Grid Set up required:                                                     #
#  1. Licenses : Grid DNS, DHCP, Grid, NIOS (IB-V1415) with DFP             #
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

class NIOS_75567(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_000_check_dfp_forward_is_false_by_default(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type='memberdfp', grid_vip=config.grid_vip)
        print("\n")
        for ref in json.loads(get_ref):
            if config.grid_fqdn in ref['_ref']: 
                get_ref_v = ib_NIOS.wapi_request('GET', ref=ref['_ref']+"?_return_fields=dfp_forward_first", grid_vip=config.grid_vip)
                print(str(get_ref_v))
                # Dict = eval(get_ref_v) 
                # print(Dict)
                res=json.loads(get_ref_v)
                print(str(res))
           
                if "'dfp_forward_first': False" in str(res):
                    print("dfp_forward_first is false by default")
                    assert True
                
                else:
                    assert False
                    

    @pytest.mark.run(order=2)
    def test_001_check_able_to_get_dfp(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns', grid_vip=config.grid_vip)
        print("\n")
        for ref in json.loads(get_ref):
            if config.grid_fqdn in ref['_ref']: 
                response = ib_NIOS.wapi_request('GET', ref=ref['_ref']+"?_return_fields=dfp_forward_first", grid_vip=config.grid_vip)
                #print(get_ref_v)
                
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        if 'Unknown argument' in response[1]: 
                            print("Sucess: found Unknown argument/field when the object is member:dns present")
                            assert True
                    else:
                        assert False
                    
    @pytest.mark.run(order=3)
    def test_002_check_dfp_is_true(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type='memberdfp', grid_vip=config.grid_vip)
        print("\n")
        for ref in json.loads(get_ref):
            if config.grid_fqdn in ref['_ref']: 
                data={'dfp_forward_first':True}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401: 
                        assert False
                    else:
                        assert True
                        
                #get object        
                get_ref_v = ib_NIOS.wapi_request('GET', ref=ref['_ref']+"?_return_fields=dfp_forward_first", grid_vip=config.grid_vip)
                print(get_ref_v)
                
                res=json.loads(get_ref_v)
                print(str(res))
           
                if "'dfp_forward_first': True" in str(res):
                    print("dfp_forward_first is false by default")
                    assert True
                
                else:
                    assert False
                        
    @pytest.mark.run(order=4)
    def test_cleanup_created_objects(self): 
        get_ref = ib_NIOS.wapi_request('GET', object_type='memberdfp', grid_vip=config.grid_vip)
        print("\n")
        for ref in json.loads(get_ref):
            if config.grid_fqdn in ref['_ref']: 
                data={'dfp_forward_first':False}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401: 
                        assert False
                    else:
                        assert True
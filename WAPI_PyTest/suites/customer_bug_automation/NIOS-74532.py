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

class NIOS_74532(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_enable_snmp_in_the_grid(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting')
        response = ib_NIOS.wapi_request('GET', object_type="member")
        memref = json.loads(response)[0]['_ref']
        print(get_ref)
        for ref in json.loads(get_ref):
            data={"snmp_setting":{"queries_enable":True,"queries_community_string":"public","trap_receivers":[{"address": "10.120.22.193"}],"traps_community_string":"public","traps_enable":True}}   
            response = ib_NIOS.wapi_request('PUT', ref=memref, fields=json.dumps(data))
            print(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401 or response[0]==404:
                    print("Success: forwarder as client ip and enable recursion")
                    assert True
                else:
                    print("Failure: forwarder as client ip and enable recursion")
                    assert False
                
    @pytest.mark.run(order=2)
    def test_001_execute_snmp_commands(self):   
        print("Executing snmp commands")
        os.system("/import/tools/lab/bin/reset_console -H "+config.vmid)
        sleep(20)
        child=pexpect.spawn("console_connect -H "+config.vmid,  maxread=4000)
        try:
            #child=pexpect.spawn("console_connect -H vm-07-25",  maxread=4000)
            child.expect(".*Escape character is .*",timeout=100)
            child.sendline("\r")
            child.expect(".*login:",timeout=100)
            child.sendline("admin")
            child.expect('password:',timeout=100)
            child.sendline("infoblox")
            child.expect("Infoblox >")

            child.sendline('show snmp variable \n')
            child.expect("\r")
            child.expect("Synopsis:\r")
            child.expect("\r")
            child.expect("show snmp {variable <name of an SNMP variable, in dotted or symbolic format> v3 <snmpuser>}")
            child.expect("\r")
            child.expect("Description:")
            child.expect("\r")
            child.expect("'show snmp variable <name> v3 <User>' shows the content of an SNMP variable, as seen from")
            child.expect("the snmpget command.")
            child.expect(" Examples:")
            child.expect("\r")
            child.expect("show snmp variable sysName.0")
            child.expect("\r")
            child.expect("show snmp variable .1.3.6.1.4.1.2021.11.53.0")
            child.expect("\r")
            child.expect("show snmp variable sysName.0 v3 TestUser")
            child.expect("\r")
            child.expect("show snmp variable .1.3.6.1.4.1.2021.11.53.0 v3 TestUser")
           
            child.expect("Infoblox >")
            child.sendline('show snmp variable sysName.0 v3 TestUser\n')
            child.expect('Please enable SNMPv3 query and set user.')
            child.sendline('show snmp variable .1.3.6.1.4.1.2021.11.53.0 v3 TestUser\n')
            child.expect('Please enable SNMPv3 query and set user.')
            child.sendline("exit")
            child.expect(".*login:")
            child.close()
            print("Success: Validating SNMP commands")
            assert True

        except Exception as e:
            child.close()
            print("Failure: Validating SNMP commands")
            print (e)
            assert False
    
    @pytest.mark.run(order=3)
    def test_002_cleanup(self):
        print("Clean up all created objects")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting')
        for ref in json.loads(get_ref):
            data={"snmp_setting":{"queries_enable":False,"queries_community_string":"public","trap_receivers":[{"address": "10.120.22.193"}],"traps_community_string":"public","traps_enable":False}}   
	    response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
	    print(response)                  
            if type(response) == tuple:                        
                if response[0]==400 or response[0]==401:                            
                    assert False
                else:
                    assert True    
    

    

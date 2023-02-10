#!/usr/bin/env python
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. SA configuration                                                      #
#  2. License : Grid                                                        #
#############################################################################

import re
import config
import pytest
import unittest
import logging
import subprocess
import os
import sys
import json
import commands
import json, ast
import requests
from time import sleep as sleep
import ib_utils.ib_NIOS as ib_NIOS
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv
import paramiko

class NIOS_79089(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_enable_ntp_services(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
        data={ "ntp_setting": {"enable_ntp": True}}
        for ref in json.loads(get_ref):
            
            response = ib_NIOS.wapi_request('PUT',ref=ref['_ref'],fields=json.dumps(data), grid_vip=config.grid_vip)
        
            print(response)
            if type(response) == tuple:
                print("Failure: Enable NTP services")
                assert False
        print("Sucess: Enabled NTP services")

    @pytest.mark.run(order=2)
    def test_001_create_ACL_ipv4_network_(self):
        data={"access_list": [{ "_struct": "addressac","address": "1.1.1.1","permission": "ALLOW"}],"name":"ntp_acl"}
        response = ib_NIOS.wapi_request('POST',object_type="namedacl",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            print("Failure: Creating IPV4 address ACL")
            assert False
        print("Sucess: Creating ACL")

    @pytest.mark.run(order=3)
    def test_002_create_ACL_ipv6_network_(self):
        data={"access_list": [{ "_struct": "addressac","address": "1111::","permission": "ALLOW"}],"name":"ntp_acl_ipv6"}
        response = ib_NIOS.wapi_request('POST',object_type="namedacl",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            print("Failure: Creating IPV6 address ACL")
            assert False
        print("Sucess: Creating ACL")


    @pytest.mark.run(order=4)
    def test_003_create_NTP_ACL(self):
        log("start","/var/log/syslog",config.grid_vip)
        data={"ntp_setting": {
            
            "ntp_acl": {
                "ac_list": [
                    {
                        "address_ac": {
                            "address": "Any",
                            "permission": "ALLOW"
                        },
                        "service": "TIME"
                    }
                ],
                "acl_type": "NAMED_ACL",
                "named_acl": "ntp_acl",
                "service": "TIME_AND_NTPQ"
            }}}
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        
        for ref in json.loads(get_ref):

            response = ib_NIOS.wapi_request('PUT',ref=ref['_ref'],fields=json.dumps(data), grid_vip=config.grid_vip)
        
            print(response)
            if type(response) == tuple:
                print("Failure: Creating NTP ACL")
                assert False
        print("Sucess: Creating NTP ACL")
        log("stop","/var/log/syslog",config.grid_vip)

    @pytest.mark.run(order=5)
    def test_004_create_NTP_ACL(self):
        #log("start","/var/log/syslog",config.grid_vip)
        data={"ntp_setting": {

            "ntp_acl": {
                "ac_list": [
                    {
                        "address_ac": {
                            "address": "Any",
                            "permission": "ALLOW"
                        },
                        "service": "TIME"
                    }
                ],
                "acl_type": "NAMED_ACL",
                "named_acl": "ntp_acl_ipv6",
                "service": "TIME_AND_NTPQ"
            }}}
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)

        for ref in json.loads(get_ref):

            response = ib_NIOS.wapi_request('PUT',ref=ref['_ref'],fields=json.dumps(data), grid_vip=config.grid_vip)

            print(response)
            if type(response) == tuple:
                print("Failure: Creating NTP ACL")
                assert False
        print("Sucess: Creating NTP ACL")
        #log("stop","/var/log/syslog",config.grid_vip)


    @pytest.mark.run(order=6)
    def test_005_validate_logs_messages(self):
        lookfor = "make_ntpd_conf.*segfault at.*"
        result = logv(lookfor, '/var/log/syslog', config.grid_vip)
        if not result:
            print("Success: Could see ntpd_conf in messages")
            assert True

    @pytest.mark.run(order=7)
    def test_006_lookfor_core_files(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data="ls -ltr /storage/cores/\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        if 'SIGSEGV' not in stdout:
            print("Success : Did not created core files")
            client.close()
            assert True

        else:
            print("Failure : core files are created")
            client.close()
            assert False


    @pytest.mark.run(order=8)
    def test_007_cleanup(self):
        print("Clean up all created objects")

        get_ref = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            
            data={"ntp_setting": { 'enable_ntp': False,                
            
                'ntp_acl': { 'ac_list': [], 'acl_type': 'NONE', 'service': 'TIME'},
                'ntp_keys': [],
                'ntp_kod': False,
                'ntp_servers': []}}
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)

        for ref in json.loads(get_ref):

            response = ib_NIOS.wapi_request('PUT',ref=ref['_ref'],fields=json.dumps(data), grid_vip=config.grid_vip)

            print(response)
            if type(response) == tuple:
                print("Failure: Cleanup the objects")
                assert False
        get_ref = ib_NIOS.wapi_request('GET', object_type="namedacl", grid_vip=config.grid_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
            print(response)
            if type(response) == tuple:
                assert True
    


        get_ref = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
        data={ "ntp_setting": {"enable_ntp": False}}
        for ref in json.loads(get_ref):

            response = ib_NIOS.wapi_request('PUT',ref=ref['_ref'],fields=json.dumps(data), grid_vip=config.grid_vip)

            print(response)
            if type(response) == tuple:
                print("Failure: Disable NTP services")
                assert False


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


class NIOS_78804(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_add_ipv6_option_space_wizard(self):
        data={"enterprise_number": 11,"name": "optionS6"}
        #data={"name": "ipv6option","option_definitions": ["optionS"]}
        response = ib_NIOS.wapi_request('POST',object_type="ipv6dhcpoptionspace",fields=json.dumps(data))
        print("/n")
        print(response)
        if type(response) == tuple:
            print("Failure: Creating IPV6 space option wizard")
            assert False
        print("Success:  Creating IPV6 space option wizard")

    @pytest.mark.run(order=2)
    def test_001_add_ipv6_option_space_wizard(self):
        #data={"enterprise_number": 11,"name": "optionS6"}
        data={"name":"fqdn","code":9,"space":"optionS6","type":"string"}
        response = ib_NIOS.wapi_request('POST', object_type="ipv6dhcpoptiondefinition",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                assert False

    @pytest.mark.run(order=3)
    def test_002_add_ipv6_option_space_to_creating_filter(self):
        ipv6option_filter = {"name":"ipv6op_f","option_space":"optionS6"}
        response = ib_NIOS.wapi_request('POST', object_type="ipv6filteroption", fields=json.dumps(ipv6option_filter))
        print(response)
        if type(response) == tuple:
            print("Failure: Adding IPV6 space option to creating IPV6option filter")
            assert False
        print("Success:  Adding IPV6 space option to creating IPV6option filter")


    @pytest.mark.run(order=4)
    def test_003_cleanup(self):
        print("Clean up all created objects")
        get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6dhcpoptionspace", grid_vip=config.grid_vip)
        print(get_ref)
        ref= json.loads(get_ref)[1]['_ref']

        response = ib_NIOS.wapi_request('DELETE',ref=ref)
        print(response)
        if type(response) == tuple and 'cannot be deleted as it has an option referenced' in response[1]:
            print("Sucess: Cannot be deleted as it has an option referenced")
            assert True

        get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6dhcpoptionspace", grid_vip=config.grid_vip)
        print(get_ref)
        ref= json.loads(get_ref)[0]['_ref']

        response = ib_NIOS.wapi_request('DELETE',ref=ref)
        print(response)
        if type(response) == tuple and 'The predefined option space.*cannot be deleted' in response[1]:
            print("Sucess: The predefined option space 'DHCPv6' cannot be deleted.")
            assert False



        log("start","/infoblox/var/audit.log",config.grid_vip)
        get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6filteroption", grid_vip=config.grid_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
            print(response)
            if type(response) == tuple:
                assert False
        get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6dhcpoptionspace", grid_vip=config.grid_vip)
        print(get_ref)
        ref= json.loads(get_ref)[1]['_ref']

        response = ib_NIOS.wapi_request('DELETE',ref=ref)
        print(response)
        if type(response) == tuple:
            assert False


        log("stop","/infoblox/var/audit.log",config.grid_vip)
        lookfor = ["Deleted IPv6OptionFilter ipv6op_f","Deleted IPv6OptionSpace optionS6"]
        for look in lookfor:
            result = logv(look, '/infoblox/var/audit.log', config.grid_vip)
            if not result:
                print("Failure: Validate audit log message after deleting ipv4 and ipv6 filters")
                assert False
        print("Success: Validate audit log message after deleting ipv4 and ipv6 filters")


 

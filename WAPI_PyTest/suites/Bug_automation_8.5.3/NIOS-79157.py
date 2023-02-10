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

class NIOSSPT_79157(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_add_ipv4_option_space_wizard(self):

        data={"name": "ipv4option"}
        response = ib_NIOS.wapi_request('POST',object_type="dhcpoptionspace",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            print("Failure: Creating IPV4 space option wizard")
            assert False
        print("Success:  Creating IPV4 space option wizard")

    @pytest.mark.run(order=2)
    def test_001_add_ipv4_DHCP_option_space_with_option_definition(self):
        print("Add IPv4 DHCP Option space with option definition")
        data={"name":"fqdn","code":1,"space":"ipv4option","type":"32-bit signed integer"}
        response = ib_NIOS.wapi_request('POST', object_type="dhcpoptiondefinition",fields=json.dumps(data))
        print(response)
        res=response
        res = json.loads(res)
        print(res)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                assert False
        


    @pytest.mark.run(order=3)
    def test_002_cleanup(self):
        print("Clean up all created objects")
        get_ref = ib_NIOS.wapi_request('GET', object_type="dhcpoptionspace", grid_vip=config.grid_vip)
        print(get_ref)
        ref= json.loads(get_ref)[1]['_ref']

        response = ib_NIOS.wapi_request('DELETE',ref=ref)
        print(response)
        if type(response) == tuple:
            assert False


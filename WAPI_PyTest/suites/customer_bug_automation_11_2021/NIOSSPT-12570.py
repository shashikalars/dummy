#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Vindya V K"
__email__  = "vvk@infoblox.com"

#############################################################################
# Grid Set up required:                                                     #
#  1. Grid Master + Member - 8.6.1 build    (LAN and LAN2 on member)        #
#  2. Licenses : DNS, DHCP, Grid, NIOS                                      #
#                                                                           #
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
import pexpect
import sys
import subprocess
import time
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util
from logger import logger

#####################################################################################################
# STEPS TO REPRODUCE:                                                                               #
## (GM + M1)                                                                                        #
#                                                                                                   #
#   1. Add LAN2 IP address for the member                                                           #
#   2. Start DNS service                                                                            #
#   3. In Member DNS properties (M1) add LAN2 IP address as ‘Other IP Address’                      #
#   4. Validate the message “The IP address XX.XX.XX.XX already exists. Choose an IP address that   #
#       is different from the LAN2 IP address”                                                      #
#                                                                                                   #
#####################################################################################################

class NIOSSPT_12570(unittest.TestCase):

# Start DNS service on member
    @pytest.mark.run(order=1)
    def test_001_Start_DNS_service(self):
        print("\n========================================================\n")
        print("Starting DNS service on member...")
        print("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        print(get_ref)
        res = json.loads(get_ref)
        for i in res:
            if config.grid_member1_fqdn in i['_ref']:
                data = {"enable_dns": True}
                response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)

                if response[0]==400 or response[0]==401:
                    print("Failure: Start DNS service on member")
                    assert False
                else:
                    print("Success: Start DNS service on member")
                    assert True

        print("\n***************. Test Case 1 Execution Completed .***************\n")


# add LAN2 IP address as ‘Other IP Address’ in member DNS properties
    @pytest.mark.run(order=2)
    def test_002_Adding_LAN2_IP_as_other_IP_addresses(self):
        print("\n========================================================\n")
        print("Adding LAN2 IP as 'other IP address'...")
        print("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns', grid_vip=config.grid_vip)
        get_ref = json.loads(get_ref)[2]['_ref']

        data = {"glue_record_addresses":[{"glue_address_choice": "OTHER","glue_record_address": config.member1_LAN2_ip,"view": "default"}]} # LAN2 IP for glue_record_addresses
        response = ib_NIOS.wapi_request('PUT', ref=get_ref, fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)

        message="Choose an IP address that is different from the LAN2 IP address"


        if message in response[1]:
            print("Failure: Adding LAN2 IP for DNS view")
            assert False
        else:
            print("Success: Adding LAN2 IP for DNS view")
            assert True

        print("\n***************. Test Case 2 Execution Completed .***************\n")

        


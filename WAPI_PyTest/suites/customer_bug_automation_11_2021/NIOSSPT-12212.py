#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Vindya V K"
__email__  = "vvk@infoblox.com"

#############################################################################
# Grid Set up required:                                                     #
#  1. Grid Master - 8.5.3 build                                             #
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
#   1. Create an authoratative zone - test.com                                                      #                                                                          #
#   2. Create a ipv6 network                                                                        #
#   2. Create ipv6 host record using below scenerio -                                               #
#       a. Without using Zone create a Host record and enable DHCP flag under IPv6 Addresses        #
#       b. With using Zone create a Host record and enable DHCP flag under IPv6 Addresses           #
#   4. Check the 'usage field' under the IPAM ipv6 network                                          #
#   5. Notice that in Scenario (a) and Scenario (b) - Usage Flag is not displaying 'DHCP' even      #
#      though it is part of DHCP usage                                                              #
#####################################################################################################


class NIOSSPT_12212(unittest.TestCase):

# Create authoratative zone - test.com
    @pytest.mark.run(order=1)
    def test_001_Create_auth_zone(self):
        print("\n================================================================\n")
        print("Creating an Authoratative zone - test.com")
        print("\n================================================================\n")

        data = {"fqdn":"test.com","view":"default", "grid_primary": [{"name": config.grid_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if response[0]==400 or response[0]==401 or response[0]==404:
            print("FAILURE: Failed to create authoratative zone test.com!")
            assert False
        else:
            print("SUCCESS: Authorataive zone test.com has been successfully created!")
            assert True

        print("\n***************. Test Case 1 Execution Completed .***************\n")



# Create ipv6_network
    @pytest.mark.run(order=2)
    def test_002_Create_ipv6_network(self):
        print("\n================================================================\n")
        print("Creating an ipv6 network - 2001:550:40a:2500::/64")
        print("\n================================================================\n")

        data = {"network": "2001:550:40a:2500::/64","network_view": "default"}
        response = ib_NIOS.wapi_request('POST', object_type="ipv6network", fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if response[0]==400 or response[0]==401 or response[0]==404:
            print("FAILURE: Failed to create ipv6 network!")
            assert False
        else:
            print("SUCCESS: ipv6 network has been created!")
            assert True

        print("\n***************. Test Case 2 Execution Completed .***************\n")


# Validating the ipv6 network
    @pytest.mark.run(order=3)
    def test_003_validate_ipv6_network(self):
        print("\n================================================================\n")
        print("Validating ipv6 network")
        print("\n================================================================\n")

        response = ib_NIOS.wapi_request('GET', object_type="ipv6network", grid_vip=config.grid_vip)
        response=json.loads(response)

        for ref in response:
            if '2001:550:40a:2500::/64' in ref['network']:
                print(ref["network"])
                print("SUCCESS: ipv6 network 2001:550:40a:2500::/64 was created!")
                assert True
                break
            else:
                continue
                print("FAILURE: ipv6 network 2001:550:40a:2500::/64 was not created!")
                assert False
        print("\n***************. Test Case 3 Execution Completed .***************\n")


# Create ipv6 host record without using zone
    @pytest.mark.run(order=4)
    def test_004_Create_host_record_without_using_zone(self):
        print("\n================================================================\n")
        print("Creating a host record - 'record_without_zone'")
        print("\n================================================================\n")

        data = {"name":"record_without_zone","configure_for_dns":False, "ipv6addrs":[{"ipv6addr": "2001:550:40a:2500::1", "configure_for_dhcp": True, "duid": "44:ee:dd:ee:ff:ee"}]}
        response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if response[0]==400 or response[0]==401 or response[0]==404:
            print("FAILURE: Failed to create host record without zone!")
            assert False
        else:
            print("SUCCESS: host record without zone has been successfully created!")
            assert True

        print("\n***************. Test Case 4 Execution Completed .***************\n")



# Validating host record without zone
    @pytest.mark.run(order=5)
    def test_005_validate_host_record_without_zone(self):
        print("\n========================================================\n")
        print("Validating host record without zone")
        print("\n========================================================\n")

        response = ib_NIOS.wapi_request('GET', object_type="record:host?name=record_without_zone", grid_vip=config.grid_vip)
        response=json.loads(response)

        for ref in response:
            if 'record_without_zone' in ref['_ref']:
                print(ref["_ref"])
                print("SUCCESS: Host record without zone was successfully created!")
                assert True
                break
            else:
                continue
                print("FAILURE: Host record without zone was not created!")
                assert False
        print("\n***************. Test Case 5 Execution Completed .***************\n")



# Check the 'usage field' under the IPAM ipv6 network
# This is expected to fail now as the bug is still not fixed

    @pytest.mark.run(order=6)
    def test_006_Check_the_usage_field(self):
        print("\n========================================================\n")
        print("Checking the usage field under IPAM ipv6 network")
        print("\n========================================================\n")

        response = ib_NIOS.wapi_request('GET', object_type="ipv6address?ip_address=2001:550:40a:2500::1", grid_vip=config.grid_vip)
        response=json.loads(response)
        print(response)[0]

        for res in response:
            if 'DHCP' not in res['usage']:
                print("usage field = "+str(res["usage"]))
                print("FAILURE: 'usage' field does not contain DHCP!")
                assert False
                break
            else:
                continue
                print("SUCCESS: 'usage' field contains DHCP!")
                assert True

        print("\n***************. Test Case 6 Execution Completed .***************\n")



# Create ipv6 host record with using zone
    @pytest.mark.run(order=7)
    def test_007_Create_chost_record_with_using_zone(self):
        print("\n========================================================\n")
        print("Creating host record - 'record_with_zone'")
        print("\n========================================================\n")

        data = {"name":"record_with_zone.test.com", "ipv6addrs":[{"ipv6addr": "2001:550:40a:2500::2", "configure_for_dhcp": True, "duid": "44:ee:dd:ee:ff:ff"}]}
        response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if response[0]==400 or response[0]==401 or response[0]==404:
            print("FAILURE: Failed to create host record with zone!")
            assert False
        else:
            print("SUCCESS: host record with zone has been successfully created!")
            assert True

        print("\n***************. Test Case 7 Execution Completed .***************\n")



# Validating host record with zone
    @pytest.mark.run(order=8)
    def test_008_validate_host_record_with_zone(self):
        print("\n========================================================\n")
        print("Validating host record with zone")
        print("\n========================================================\n")

        response = ib_NIOS.wapi_request('GET', object_type="record:host?name=record_with_zone.test.com", grid_vip=config.grid_vip)
        response=json.loads(response)

        for ref in response:
            if 'record_with_zone.test.com' in ref['_ref']:
                print(ref["_ref"])
                print("SUCCESS: Host record with zone was successfully created!")
                assert True
                break
            else:
                continue
                print("FAILURE: Host record with zone was not created!")
                assert False
        print("\n***************. Test Case 8 Execution Completed .***************\n")



# Check the 'usage field' under the IPAM ipv6 network
# This is expected to fail now as the bug is still not fixed

    @pytest.mark.run(order=9)
    def test_009_Check_the_usage_field(self):
        print("\n========================================================\n")
        print("Checking the usage field under IPAM ipv6 network")
        print("\n========================================================\n")

        response = ib_NIOS.wapi_request('GET', object_type="ipv6address?ip_address=2001:550:40a:2500::2", grid_vip=config.grid_vip)
        response=json.loads(response)
        print(response)[0]

        for res in response:
            if 'DHCP' not in res['usage']:
                print("usage field = "+str(res["usage"]))
                print("FAILURE: 'usage' field does not contain DHCP!")
                assert False
                break
            else:
                continue
                print("SUCCESS: 'usage' field contains DHCP!")
                assert True

        print("\n***************. Test Case 9 Execution Completed .***************\n")


### cleanup function

    @pytest.mark.run(order=10)
    def test_010_cleanup_objects(self):
        print("\n============================================\n")
        print("CLEANUP: Reverting back to original setup...")
        print("\n============================================\n")

        get_ref = ib_NIOS.wapi_request('GET',object_type="record:host")
        for ref in json.loads(get_ref):
            if 'record_with_zone.test.com' in ref["_ref"]:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])

        get_ref = ib_NIOS.wapi_request('GET',object_type="record:host")
        for ref in json.loads(get_ref):
            if 'record_without_zone' in ref["_ref"]:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])

        get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth")
        for ref in json.loads(get_ref):
            if 'test.com' in ref["_ref"]:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])

        get_ref = ib_NIOS.wapi_request('GET',object_type="ipv6network")
        for ref in json.loads(get_ref):
            if '2001:550:40a:2500::/64' in ref["network"]:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])

        print("\n***************. Test Case 10 Execution Completed .***************\n")


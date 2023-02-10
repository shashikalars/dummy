#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Vindya V K"
__email__  = "vvk@infoblox.com"

#############################################################################
# Grid Set up required:                                                     #
#  1. Grid Master - 8.5.3 build                                             #
#  2. Licenses : DNS, DHCP, Grid, NIOS                                      #
#
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

################################################################################
# STEPS TO REPRODUCE:                                                          #
#   1. "Enable port redundancy on LAN1/LAN2" - member properties > network     #
#   2. execute cli command -  "set interface_mtu"  on LAN1                     #
#   3. execute cli command -  "set interface_mtu"  on LAN2                     #
################################################################################


class NIOSSPT_10043(unittest.TestCase):

# Enable port redundancy on LAN1 and LAN2
    @pytest.mark.run(order=1)
    def test_001_Enable_port_redundancy_on_LAN1_LAN2(self):
        print("\n========================================================\n")
        print("Enable port redundancy on LAN1/LAN2")
        print("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[0]['_ref']
        print(ref)

        data = {"lan2_port_setting":{"enabled":True,"nic_failover_enable_primary":True,"nic_failover_enabled":True}}
        response = ib_NIOS.wapi_request('PUT', ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)

        if response[0]==400 or response[0]==401 or response[0]==404:
            print("FAILURE: Enabling port redundancy on LAN1/LAN2")
            assert False
        else:
            print("SUCCESS: Enabling port redundancy on LAN1/LAN2")
            assert True
        sleep(150)

        print("\n***************. Test Case 1 Execution Completed .***************\n")


# Validating if the port redundancy is enabled
    @pytest.mark.run(order=2)
    def test_002_validate_port_redundancy(self):
        print("\n========================================================\n")
        print("Validating port redundancy on LAN1/LAN2")
        print("\n========================================================\n")

        response = ib_NIOS.wapi_request('GET', object_type="member?_return_fields=lan2_port_setting", grid_vip=config.grid_vip)
        response=json.loads(response)[0]['lan2_port_setting']
        print(response)

        if response['enabled']==True and response['nic_failover_enable_primary']==True and response['nic_failover_enabled']==True:
            print("Port redundancy is successfully enabled on LAN1/LAN2")
            assert True
        else:
            print("Port redundancy is not enabled on LAN1/LAN2")
            assert False

        print("\n***************. Test Case 2 Execution Completed .***************\n")


# set interface_mtu for LAN1 using cli
    @pytest.mark.run(order=3)
    def test_003_set_interface_mtu_for_LAN1(self):
        print("\n========================================================\n")
        print("Set interface mtu for LAN1 using cli")
        print("\n========================================================\n")

        try:
            child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect("password:")
            child.sendline("infoblox")
            child.expect("Infoblox >")
            child.sendline("set interface_mtu lan 1500")
            child.expect("MTU Value of lan cannot be set when port redundancy is enabled")

            print("SUCCESS: MTU Value of lan cannot be set when port redundancy is enabled")
            assert True

        except Exception as e:
            print(e)
            child.close()
            print("FAILURE: Something went wrong...MTU value was set when port redundancy is enabled!")
            assert False

        finally:
            child.close()

        print("\n***************. Test Case 3 Execution Completed .***************\n")


# set interface_mtu for LAN2 using cli
    @pytest.mark.run(order=4)
    def test_004_set_interface_mtu_for_LAN2(self):
        print("\n========================================================\n")
        print("Set interface mtu for LAN2 using cli")
        print("\n========================================================\n")

        try:
            child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect("password:")
            child.sendline("infoblox")
            child.expect("Infoblox >")
            child.sendline("set interface_mtu lan2 1500")
            child.expect("MTU Value of lan2 cannot be set when port redundancy is enabled")

            print("SUCCESS: MTU Value of lan2 cannot be set when port redundancy is enabled")
            assert True

        except Exception as e:
            print(e)
            child.close()
            print("FAILURE: Something went wrong...MTU value was set when port redundancy is enabled!")
            assert False

        finally:
            child.close()

        print("\n***************. Test Case 4 Execution Completed .***************\n")


### cleanup function

    @pytest.mark.run(order=5)
    def test_005_cleanup_objects(self):
        print("\n============================================\n")
        print("CLEANUP: Reverting back to original setup...")
        print("\n============================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[0]['_ref']
        print(ref)

        data = {"lan2_port_setting":{"enabled":False,"nic_failover_enable_primary":False,"nic_failover_enabled":False}}
        response = ib_NIOS.wapi_request('PUT', ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)

        if response[0]==400 or response[0]==401 or response[0]==404:
            print("FAILURE: Disabling port redundancy on LAN1/LAN2")
            assert False
        else:
            print("SUCCESS: Disabling port redundancy on LAN1/LAN2")
            assert True
        sleep(150)


        print("\n***************. Test Case 5 Execution Completed .***************\n")


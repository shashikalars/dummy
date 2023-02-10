#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Vindya V K"
__email__  = "vvk@infoblox.com"

#############################################################################
# Grid Set up required:
#  1. Grid Master + Reporting member - 8.5.3 build
#  2. Licenses : DNS, DHCP, Grid, NIOS, Cloud Network Automation license (Master)
#                Grid,Reporting (Member)
##
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

class NIOSSPT_12246(unittest.TestCase):
## Splunk-reporting-group
# Disable concurrent login under splunk-reporting-group

    @pytest.mark.run(order=1)
    def test_001_Disable_concurrent_login_for_splunk_reporting_group(self):
        print("\n========================================================\n")
        print("Disabling Concurrent login under splunk-reporting-group")
        print("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[3]['_ref']
        print(ref)

        data = {"name": "splunk-reporting-group", "disable_concurrent_login":True}
        response = ib_NIOS.wapi_request('PUT', ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        message = "Splunk Reporting Group is not allowed to be updated."

        if response[0]==400 or response[0]==401 or response[0]==404:
            if message in response[1]:
                print('\n'+message+'\n')
                print("SUCCESS: Could not disable Concurrent login for splunk-reporting-group as " + message)
                assert True
            else:
                print("FAILURE: Concurrent login disabled for splunk-reporting-group!")
                assert False
        print("\n***************. Test Case 1 Execution Completed .***************\n")



# Validating disable_concurrent_login field value for splunk-reporting-group

    @pytest.mark.run(order=2)
    def test_002_validating_Disable_concurrent_login_for_splunk_reporting_group(self):
        print("\n========================================================\n")
        print("Validating Disable Concurrent login under splunk-reporting-group")
        print("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup?_return_fields=disable_concurrent_login", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[3]['disable_concurrent_login']
        print(ref)


        if ref == False:
            print("SUCCESS: Concurrent login has NOT been disabled for splunk-reporting-group")
            assert True

        else:
            print("FAILURE: Failed Diable Concurrent login for splunk-reporting-group!")
            assert False
        print("\n***************. Test Case 2 Execution Completed .***************\n")

# admin-group
# Disable concurrent login for admin-group

    @pytest.mark.run(order=3)
    def test_003_Disable_concurrent_login_for_admin_group(self):
        print("\n========================================================\n")
        print("Disabling Concurrent login for admin-group")
        print("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[0]['_ref']
        print(ref)

        data = {"name": "admin-group", "disable_concurrent_login":True}
        response = ib_NIOS.wapi_request('PUT', ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)

        if response[0]==400 or response[0]==401 or response[0]==404:
            print("FAILURE: Could not disable Concurrent login for admin-group!")
            assert False

        else:
            print("SUCCESS: Concurrent login disabled for admin-group")
            assert True
        print("\n***************. Test Case 3 Execution Completed .***************\n")


# Validating disable_concurrent_login field value for admin-group

    @pytest.mark.run(order=4)
    def test_004_validating_Disable_concurrent_login_for_admin_group(self):
        print("\n========================================================\n")
        print("Validating Disable Concurrent login for admin-group")
        print("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup?_return_fields=disable_concurrent_login", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[0]['disable_concurrent_login']
        print(ref)


        if ref == True:
            print("SUCCESS: Concurrent login has been disabled for admin-group")
            assert True

        else:
            print("FAILURE: Concurrent login has NOT been disabled for admin-group!")
            assert False
        print("\n***************. Test Case 4 Execution Completed .***************\n")



# Cloud-api-only
# Disable concurrent login for cloud-api-only

    @pytest.mark.run(order=5)
    def test_005_Disable_concurrent_login_for_cloud_api_only_group(self):
        print("\n========================================================\n")
        print("Disabling Concurrent login for cloud-api-only group")
        print("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[1]['_ref']
        print(ref)

        data = {"name": "cloud-api-only", "disable_concurrent_login":True}
        response = ib_NIOS.wapi_request('PUT', ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)

        if response[0]==400 or response[0]==401 or response[0]==404:
            print("FAILURE: Could not disable Concurrent login for cloud-api-only group!")
            assert False

        else:
            print("SUCCESS: Concurrent login disabled for cloud-api-only group")
            assert True
        print("\n***************. Test Case 5 Execution Completed .***************\n")


# Validating disable_concurrent_login field value for cloud-api-only

    @pytest.mark.run(order=6)
    def test_006_validating_Disable_concurrent_login_for_cloud_api_only_group(self):
        print("\n========================================================\n")
        print("Validating Disable Concurrent login for cloud-api-only group")
        print("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup?_return_fields=disable_concurrent_login", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[1]['disable_concurrent_login']
        print(ref)


        if ref == True:
            print("SUCCESS: Concurrent login has been disabled for cloud-api-only group")
            assert True

        else:
            print("FAILURE: Concurrent login has NOT been disabled for cloud-api-only group!")
            assert False
        print("\n***************. Test Case 6 Execution Completed .***************\n")



# saml-group
# Disable concurrent login for saml-group

    @pytest.mark.run(order=7)
    def test_007_Disable_concurrent_login_for_saml_group(self):
        print("\n========================================================\n")
        print("Disabling Concurrent login for saml-group")
        print("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[2]['_ref']
        print(ref)

        data = {"name": "saml-group", "disable_concurrent_login":True}
        response = ib_NIOS.wapi_request('PUT', ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)

        if response[0]==400 or response[0]==401 or response[0]==404:
            print("FAILURE: Could not disable Concurrent login for saml-group!")
            assert False

        else:
            print("SUCCESS: Concurrent login disabled for saml-group")
            assert True
        print("\n***************. Test Case 7 Execution Completed .***************\n")


# Validating disable_concurrent_login field value for saml-group

    @pytest.mark.run(order=8)
    def test_008_validating_Disable_concurrent_login_for_saml_group(self):
        print("\n========================================================\n")
        print("Validating Disable Concurrent login for saml-group")
        print("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup?_return_fields=disable_concurrent_login", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[2]['disable_concurrent_login']
        print(ref)


        if ref == True:
            print("SUCCESS: Concurrent login has been disabled for saml-group")
            assert True

        else:
            print("FAILURE: Concurrent login has NOT been disabled for saml-group!")
            assert False
        print("\n***************. Test Case 8 Execution Completed .***************\n")


# grid
# Disable concurrent login for grid

    @pytest.mark.run(order=9)
    def test_009_Disable_concurrent_login_for_grid(self):
        print("\n========================================================\n")
        print("Disabling Concurrent login under grid security settings")
        print("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="grid?_return_fields=security_setting", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[0]['_ref']
        print(ref)

        data = {"security_setting":{"disable_concurrent_login": True}}
        response = ib_NIOS.wapi_request('PUT', ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if response[0]==400 or response[0]==401 or response[0]==404:
            print("FAILURE: Failed Diable Concurrent login for grid!")
            assert False
        else:
            print("SUCCESS: Concurrent login disabled for grid")
            assert True
        print("\n***************. Test Case 9 Execution Completed .***************\n")



# Validating disable_concurrent_login field value for grid

    @pytest.mark.run(order=10)
    def test_010_validating_Disable_concurrent_login_for_grid(self):
        print("\n========================================================\n")
        print("Validating Disable Concurrent login for grid")
        print("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="grid?_return_fields=security_setting", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[0]['security_setting']
        new_ref=ref['disable_concurrent_login']
        print(new_ref)

        if new_ref == True:
            print("SUCCESS: Concurrent login disabled for grid")
            assert True

        else:
            print("FAILURE: Concurrent login NOT disabled for grid!")
            assert False
        print("\n***************. Test Case 10 Execution Completed .***************\n")



# splunk-reporting-Group
# Enable Account lockout under splunk-reporting-group

    @pytest.mark.run(order=11)
    def test_011_Enable_account_lockout_for_splunk_reporting_group(self):
        print("\n========================================================\n")
        print("Enabling account lockout for splunk-reporting-group")
        print("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup?_return_fields=lockout_setting", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[3]['_ref']
        print(ref)

        data = {"name": "splunk-reporting-group", "lockout_setting":{"enable_sequential_failed_login_attempts_lockout":True}}
        response = ib_NIOS.wapi_request('PUT', ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        message = "Splunk Reporting Group is not allowed to be updated."

        if response[0]==400 or response[0]==401 or response[0]==404:
            if message in response[1]:
                print('\n'+message+'\n')
                print("SUCCESS: Could not Enable account lockout for splunk-reporting-group as " + message)
                assert True
            else:
                print("FAILURE: Enabled account lockout for splunk-reporting-group!")
                assert False
        print("\n***************. Test Case 11 Execution Completed .***************\n")



# Validating Enable_Accoubt_lockout field value for splunk-reporting-group

    @pytest.mark.run(order=12)
    def test_012_validating_Enable_Account_Lockout_for_splunk_reporting_group(self):
        print("\n========================================================\n")
        print("Validating Enable Account lockout for splunk-reporting-group")
        print("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup?_return_fields=lockout_setting", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[3]['lockout_setting']
        print(ref)
        new_ref = ref['enable_sequential_failed_login_attempts_lockout']

        if new_ref == False:
            print("SUCCESS: Account lockout has NOT been Enabled for splunk-reporting-group")
            assert True

        else:
            print("FAILURE: Account lockout has been Enabled for splunk-reporting-group!")
            assert False
        print("\n***************. Test Case 12 Execution Completed .***************\n")



# admin-Group
# Enable Account lockout for admin-group

    @pytest.mark.run(order=13)
    def test_013_Enable_account_lockout_for_admin_group(self):
        print("\n========================================================\n")
        print("Enabling account lockout for admin-group")
        print("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup?_return_fields=lockout_setting", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[0]['_ref']
        print(ref)

        data = {"name": "admin-group", "lockout_setting":{"enable_sequential_failed_login_attempts_lockout":True}}
        response = ib_NIOS.wapi_request('PUT', ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)

        if response[0]==400 or response[0]==401 or response[0]==404:
            print("FAILURE: Could not Enable account lockout for admin-group!")
            assert False

        else:
            print("SUCCESS: Account lockout has been enabled for admin-group!")
            assert True
        print("\n***************. Test Case 13 Execution Completed .***************\n")



# Validating Enable_Accoubt_lockout field value for admin-group

    @pytest.mark.run(order=14)
    def test_014_validating_Enable_Account_Lockout_for_admin_group(self):
        print("\n========================================================\n")
        print("Validating Enable Account lockout for admin-group")
        print("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup?_return_fields=lockout_setting", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[0]['lockout_setting']
        print(ref)
        new_ref = ref['enable_sequential_failed_login_attempts_lockout']

        if new_ref == True:
            print("SUCCESS: Account lockout has been Enabled for admin-group")
            assert True

        else:
            print("FAILURE: Account lockout has NOT been Enabled for admin-group!")
            assert False
        print("\n***************. Test Case 14 Execution Completed .***************\n")



# cloud-api-only
# Enable Account lockout for cloud-api-only group

    @pytest.mark.run(order=15)
    def test_015_Enable_account_lockout_for_cloud_api_only_group(self):
        print("\n========================================================\n")
        print("Enabling account lockout for cloud-api-only group")
        print("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup?_return_fields=lockout_setting", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[1]['_ref']
        print(ref)

        data = {"name": "cloud-api-only", "lockout_setting":{"enable_sequential_failed_login_attempts_lockout":True}}
        response = ib_NIOS.wapi_request('PUT', ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)

        if response[0]==400 or response[0]==401 or response[0]==404:
            print("FAILURE: Could not Enable account lockout for cloud-api-only group!")
            assert False

        else:
            print("SUCCESS: Account lockout has been enabled for cloud-api-only group !")
            assert True
        print("\n***************. Test Case 15 Execution Completed .***************\n")



# Validating Enable_Accoubt_lockout field value for cloud-api-only group

    @pytest.mark.run(order=16)
    def test_016_validating_Enable_Account_Lockout_for_cloud_api_only_group(self):
        print("\n========================================================\n")
        print("Validating Enable Account lockout for cloud-api-only group")
        print("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup?_return_fields=lockout_setting", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[1]['lockout_setting']
        print(ref)
        new_ref = ref['enable_sequential_failed_login_attempts_lockout']

        if new_ref == True:
            print("SUCCESS: Account lockout has been Enabled for cloud-api-only group")
            assert True

        else:
            print("FAILURE: Account lockout has NOT been Enabled for cloud-api-only group!")
            assert False
        print("\n***************. Test Case 16 Execution Completed .***************\n")


# saml-Group
# Enable Account lockout for saml-group

    @pytest.mark.run(order=17)
    def test_017_Enable_account_lockout_for_saml_group(self):
        print("\n========================================================\n")
        print("Enabling account lockout for saml-group")
        print("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup?_return_fields=lockout_setting", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[2]['_ref']
        print(ref)

        data = {"name": "saml-group", "lockout_setting":{"enable_sequential_failed_login_attempts_lockout":True}}
        response = ib_NIOS.wapi_request('PUT', ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)

        if response[0]==400 or response[0]==401 or response[0]==404:
            print("FAILURE: Could not Enable account lockout for saml-groupp!")
            assert False

        else:
            print("SUCCESS: Account lockout has been enabled for saml-group !")
            assert True
        print("\n***************. Test Case 17 Execution Completed .***************\n")



# Validating Enable_Accoubt_lockout field value for saml-group

    @pytest.mark.run(order=18)
    def test_018_validating_Enable_Account_Lockout_for_saml_group(self):
        print("\n========================================================\n")
        print("Validating Enable Account lockout for saml-group")
        print("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup?_return_fields=lockout_setting", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[2]['lockout_setting']
        print(ref)
        new_ref = ref['enable_sequential_failed_login_attempts_lockout']

        if new_ref == True:
            print("SUCCESS: Account lockout has been Enabled for saml-group")
            assert True

        else:
            print("FAILURE: Account lockout has NOT been Enabled for saml-group!")
            assert False
        print("\n***************. Test Case 18 Execution Completed .***************\n")


# grid
# Enable Account lockout for grid

    @pytest.mark.run(order=19)
    def test_019_Enable_account_lockout_for_grid(self):
        print("\n========================================================\n")
        print("Enable account lockout for grid")
        print("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="grid?_return_fields=lockout_setting", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[0]['_ref']
        print(ref)

        data = {"lockout_setting":{"enable_sequential_failed_login_attempts_lockout":True}}
        response = ib_NIOS.wapi_request('PUT', ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if response[0]==400 or response[0]==401 or response[0]==404:
            print("FAILURE: Failed Enable account lockout for grid!")
            assert False
        else:
            print("SUCCESS: Account lockout Enabled for grid")
            assert True
        print("\n***************. Test Case 19 Execution Completed .***************\n")


# Validating Enable account lockout field value for grid

    @pytest.mark.run(order=20)
    def test_020_validating_Enable_account_lockout_for_grid(self):
        print("\n========================================================\n")
        print("Validating Enable account lockout for grid")
        print("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="grid?_return_fields=lockout_setting", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[0]['lockout_setting']
        new_ref = ref['enable_sequential_failed_login_attempts_lockout']
        print(new_ref)

        if new_ref == True:
            print("SUCCESS: Account lockout is Enabled for grid")
            assert True

        else:
            print("FAILURE: Account lockout is NOT enabled for grid!")
            assert False
        print("\n***************. Test Case 20 Execution Completed .***************\n")


### cleanup function

    @pytest.mark.run(order=21)
    def test_021_cleanup_objects(self):
        print("\n============================================\n")
        print("CLEANUP: Reverting back to original setup...")
        print("\n============================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup?_return_fields=disable_concurrent_login,lockout_setting", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[0]['_ref']
        print(ref)
        data = {"disable_concurrent_login": False, "lockout_setting":{"enable_sequential_failed_login_attempts_lockout":False} }
        response = ib_NIOS.wapi_request('PUT', ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)

        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup?_return_fields=disable_concurrent_login,lockout_setting", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[1]['_ref']
        print(ref)
        data = {"disable_concurrent_login": False, "lockout_setting":{"enable_sequential_failed_login_attempts_lockout":False} }
        response = ib_NIOS.wapi_request('PUT', ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)

        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup?_return_fields=disable_concurrent_login,lockout_setting", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[2]['_ref']
        print(ref)
        data = {"disable_concurrent_login": False, "lockout_setting":{"enable_sequential_failed_login_attempts_lockout":False} }
        response = ib_NIOS.wapi_request('PUT', ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)

        get_ref = ib_NIOS.wapi_request('GET', object_type="grid?_return_fields=security_setting", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[0]['_ref']
        print(ref)
        data = {"security_setting":{"disable_concurrent_login": False}, "lockout_setting":{"enable_sequential_failed_login_attempts_lockout":False} }
        response = ib_NIOS.wapi_request('PUT', ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)

        print("\n***************. Test Case 21 Execution Completed .***************\n")


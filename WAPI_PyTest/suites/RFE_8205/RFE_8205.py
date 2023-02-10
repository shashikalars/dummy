import re
import config
import pytest
import unittest
import logging
import subprocess
import os
import json
import ib_utils.ib_NIOS as ib_NIOS
from time import sleep
import commands
import json, ast
import requests
import time
import pexpect
import getpass
import sys

def get_reference_value_grid():
    logging.info("get reference value for GRID")
    get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
    logging.info(get_ref)
    res = json.loads(get_ref)
    ref1 = json.loads(get_ref)[0]['_ref']
    logging.info (ref1)
    return ref1

def get_reference_value_admingroup():
    logging.info("get reference value for ADMIN GROUP")
    get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup")
    logging.info(get_ref)
    return get_ref

def get_grid_inactivity_lockout_settings():
    ref1=get_reference_value_grid()
    logging.info("Get inactivity lockout settings for GRID")
    get_ref = ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=security_setting")
    logging.info(get_ref)
    res = json.loads(get_ref)
    return res

class Network(unittest.TestCase):
    logging.basicConfig(filename='example.log', filemode='w', level=logging.DEBUG)

    @pytest.mark.run(order=1)
    def test_01_grid_inactivity_lockout_default_settings(self):
        logging.info("===================================================================================================================================")
        logging.info("EXECUTING TEST CASE : test_01_grid_inactivity_lockout_default_settings")
        logging.info("This Test Case will verify that the Grid Properties have the expected default settings")
        logging.info("===================================================================================================================================")
        settings = get_grid_inactivity_lockout_settings()
        logging.info(settings)
        data = {'reactivate_via_serial_console_enable': True, 'reminder_days': 15, 'account_inactivity_lockout_enable': False, 'reactivate_via_remote_console_enable': True, 'inactive_days': 30}
        condition = settings['security_setting']['inactivity_lockout_setting']
        logging.info("Verifying if Inactivity Lockout Setting is Diabled by default in GRID Properties")
        if (condition['account_inactivity_lockout_enable'] == data['account_inactivity_lockout_enable'] and condition['inactive_days'] == data['inactive_days'] and \
        condition['reminder_days'] == data['reminder_days'] and condition['reactivate_via_serial_console_enable'] == data['reactivate_via_serial_console_enable'] and \
        condition['reactivate_via_remote_console_enable'] == data['reactivate_via_remote_console_enable']):
            logging.info("Successfully verified that Inactivity Lockout Setting is Disabled by default in GRID Properties")
            assert True
        else:
            logging.error("FAILED to verify that Inacitvity Lockout Setting is Disabled by default in GRID Properties")
            logging.info("Expected Setting")
            logging.info(data)
            logging.info("Actual Setting")
            logging.info(condition)
            assert False

    @pytest.mark.run(order=2)
    def test_02_grid_inactivity_lockout_enable_with_default_values(self):
        logging.info("===================================================================================================================================")
        logging.info("EXECUTING TEST CASE : test_02_grid_inactivity_lockout_enable_with_default_values")
        logging.info("This Test Case will verify that Inactivity Lockout can be enabled with default values in Grid Properties")
        logging.info("===================================================================================================================================")
        input_data = {'security_setting':{'inactivity_lockout_setting':{'account_inactivity_lockout_enable': True,"inactive_days":30, "reminder_days":15, "reactivate_via_remote_console_enable": True, "reactivate_via_serial_console_enable": True}}}
        ref1 = get_reference_value_grid()
        logging.info("Enabling Inactivity Lockout Setting with default values")
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(input_data),grid_vip=config.grid_vip)
        logging.info(response)
        settings = get_grid_inactivity_lockout_settings()
        logging.info(settings)
        data = {'reactivate_via_serial_console_enable': True, 'reminder_days': 15, 'account_inactivity_lockout_enable': True, 'reactivate_via_remote_console_enable': True, 'inactive_days': 30}
        condition = settings['security_setting']['inactivity_lockout_setting']
        logging.info("Verifying if Inactivity Lockout Setting is Enabled with default values in GRID Properties")
        if (condition['account_inactivity_lockout_enable'] == data['account_inactivity_lockout_enable'] and condition['inactive_days'] == data['inactive_days'] and \
        condition['reminder_days'] == data['reminder_days'] and condition['reactivate_via_serial_console_enable'] == data['reactivate_via_serial_console_enable'] and \
        condition['reactivate_via_remote_console_enable'] == data['reactivate_via_remote_console_enable']):
            logging.info("Successfully verified that Inactivity Lockout Setting is Enabled with default values in GRID Properties")
            assert True
        else:
            logging.error("FAILED to verify that Inacitvity Lockout Setting is Enabled with default values in GRID Properties")
            logging.info("Expected Setting")
            logging.info(data)
            logging.info("Actual Setting")
            logging.info(condition)
            assert False
        logging.info("Restoring Settings back to original")
        input_data = {'security_setting':{'inactivity_lockout_setting':{'account_inactivity_lockout_enable': False,"inactive_days":30, "reminder_days":15, "reactivate_via_remote_console_enable": True, "reactivate_via_serial_console_enable": True}}}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(input_data),grid_vip=config.grid_vip)
        logging.info(response)

    @pytest.mark.run(order=3)
    def test_03_grid_inactivity_lockout_enable_with_custom_values(self):
        logging.info("===================================================================================================================================")
        logging.info("EXECUTING TEST CASE : test_03_grid_inactivity_lockout_enable_with_custom_values")
        logging.info("This Test Case will verify that Inactivity Lockout can be enabled with custom values in Grid Properties")
        logging.info("===================================================================================================================================")
        input_data = {'security_setting':{'inactivity_lockout_setting':{'account_inactivity_lockout_enable': True,"inactive_days":7, "reminder_days":3, "reactivate_via_remote_console_enable": False, "reactivate_via_serial_console_enable": True}}}
        ref1 = get_reference_value_grid()
        logging.info("Enabling Inactivity Lockout Setting with custom values")
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(input_data),grid_vip=config.grid_vip)
        logging.info(response)
        settings = get_grid_inactivity_lockout_settings()
        logging.info(settings)
        data = {'reactivate_via_serial_console_enable': True, 'reminder_days': 3, 'account_inactivity_lockout_enable': True, 'reactivate_via_remote_console_enable': False, 'inactive_days': 7}
        condition = settings['security_setting']['inactivity_lockout_setting']
        logging.info("Verifying if Inactivity Lockout Setting is Enabled with custom values in GRID Properties")
        if (condition['account_inactivity_lockout_enable'] == data['account_inactivity_lockout_enable'] and condition['inactive_days'] == data['inactive_days'] and \
        condition['reminder_days'] == data['reminder_days'] and condition['reactivate_via_serial_console_enable'] == data['reactivate_via_serial_console_enable'] and \
        condition['reactivate_via_remote_console_enable'] == data['reactivate_via_remote_console_enable']):
            logging.info("Successfully verified that Inactivity Lockout Setting is Enabled with custom values in GRID Properties")
            assert True
        else:
            logging.error("FAILED to verify that Inacitvity Lockout Setting is Enabled with custom values in GRID Properties")
            logging.info("Expected Setting")
            logging.info(data)
            logging.info("Actual Setting")
            logging.info(condition)
            assert False
        logging.info("Restoring Settings back to original")
        input_data = {'security_setting':{'inactivity_lockout_setting':{'account_inactivity_lockout_enable': False,"inactive_days":30, "reminder_days":15, "reactivate_via_remote_console_enable": True, "reactivate_via_serial_console_enable": True}}}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(input_data),grid_vip=config.grid_vip)
        logging.info(response)

    @pytest.mark.run(order=4)
    def test_04_default_groups_inactivity_lockout_default_settings(self):
        logging.info("===================================================================================================================================")
        logging.info("EXECUTING TEST CASE : test_04_default_groups_inactivity_lockout_default_settings")
        logging.info("This Test Case will verify that the Inactivity Lockout Setting is Overridden and Disabled by default for the default ADMIN GROUPS")
        logging.info("===================================================================================================================================")
        all_ref = get_reference_value_admingroup()
        res = json.loads(all_ref)
        count = len(res)
        for current_group in range(count):
            ref1 = json.loads(all_ref)[current_group]['_ref']
            admin_group = json.loads(all_ref)[current_group]['name']
            if (admin_group == "admin-group" or admin_group == "saml-group" or admin_group == "cloud-api-only" or admin_group == "splunk-reporting-group"):
                logging.info("Testing default group")
                logging.info(admin_group)
                logging.info("Get use flag - use_account_inactivity_lockout_enable for ADMIN GROUP")
                get_use_flag = ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=use_account_inactivity_lockout_enable")
                logging.info(get_use_flag)
                res = json.loads(get_use_flag)
                use_flag_condition = res['use_account_inactivity_lockout_enable']
                use_flag_data = {'use_account_inactivity_lockout_enable': True}
                if (use_flag_condition == use_flag_data['use_account_inactivity_lockout_enable'] ):
                    logging.info("Successfully verified that ADMIN GROUP is Overridden by default as Expected")
                    assert True
                else:
                    logging.error("FAILED to verify that ADMIN GROUP is Overridden by default")
                    assert False
                logging.info("Get inactivity lockout settings for ADMIN GROUP")
                get_lockout_setting = ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=inactivity_lockout_setting")
                logging.info(get_lockout_setting)
                res = json.loads(get_lockout_setting)
                data = {'reactivate_via_serial_console_enable': True, 'reminder_days': 15, 'account_inactivity_lockout_enable': False, 'reactivate_via_remote_console_enable': True, 'inactive_days': 30}
                condition = res['inactivity_lockout_setting']
                logging.info("Verifying if Inactivity Lockout Setting is Diabled by default in Admin Group Properties")
                if (condition['account_inactivity_lockout_enable'] == data['account_inactivity_lockout_enable'] and condition['inactive_days'] == data['inactive_days'] and \
                condition['reminder_days'] == data['reminder_days'] and condition['reactivate_via_serial_console_enable'] == data['reactivate_via_serial_console_enable'] and \
                condition['reactivate_via_remote_console_enable'] == data['reactivate_via_remote_console_enable']):
                    logging.info("Successfully verified that Inactivity Lockout Setting is Disabled by default in ADMIN GROUP Properties")
                    assert True
                else:
                    logging.error("FAILED to verify that Inacitvity Lockout Setting is Disabled by default in ADMIN GROUP Properties")
                    logging.info("Expected Setting")
                    logging.info(data)
                    logging.info("Actual Setting")
                    logging.info(condition)
                    assert False

    @pytest.mark.run(order=5)
    def test_05_default_group_inherit_from_grid(self):
        logging.info("===================================================================================================================================")
        logging.info("EXECUTING TEST CASE : test_05_default_group_inherit_from_grid")
        logging.info("This Test Case will verify that default group can successfully inherit Inactivity Lockout Setting from GRID")
        logging.info("===================================================================================================================================")
        all_ref = get_reference_value_admingroup()
        res = json.loads(all_ref)
        count = len(res)
        for current_group in range(count):
            ref1 = json.loads(all_ref)[current_group]['_ref']
            admin_group = json.loads(all_ref)[current_group]['name']
            if (admin_group == "admin-group"):
                logging.info("Testing if default group admin-group can inherit Inactivity Lockout Setting from GRID")
                input_data = {'use_account_inactivity_lockout_enable': False}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(input_data),grid_vip=config.grid_vip)
                logging.info(response)
                logging.info("Get use flag - use_account_inactivity_lockout_enable for admin-group")
                get_use_flag = ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=use_account_inactivity_lockout_enable")
                logging.info(get_use_flag)
                res = json.loads(get_use_flag)
                use_flag_condition = res['use_account_inactivity_lockout_enable']
                use_flag_data = {'use_account_inactivity_lockout_enable': False}
                if (use_flag_condition == use_flag_data['use_account_inactivity_lockout_enable'] ):
                    logging.info("Successfully verified that default group admin-group can be inherited from GRID")
                    assert True
                else:
                    logging.error("FAILED to verify that default group admin-group can be inherited from GRID")
                    assert False
                logging.info("Restoring settings to original")
                input_data = {'use_account_inactivity_lockout_enable': True}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(input_data),grid_vip=config.grid_vip)
                logging.info(response)

    @pytest.mark.run(order=6)
    def test_06_default_group_override_and_enable(self):
        logging.info("===================================================================================================================================")
        logging.info("EXECUTING TEST CASE : test_06_default_group_override_and_enable")
        logging.info("This Test Case will verify that default group can be successfully overridden and enabled for Account Inactivity Lockout")
        logging.info("===================================================================================================================================")
        all_ref = get_reference_value_admingroup()
        res = json.loads(all_ref)
        count = len(res)
        for current_group in range(count):
            ref1 = json.loads(all_ref)[current_group]['_ref']
            admin_group = json.loads(all_ref)[current_group]['name']
            if (admin_group == "admin-group"):
                logging.info("Testing if default group admin-group can be overridden for Inactivity Lockout Setting")
                input_data = {'use_account_inactivity_lockout_enable': True}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(input_data),grid_vip=config.grid_vip)
                logging.info(response)
                logging.info("Get use flag - use_account_inactivity_lockout_enable for admin-group")
                get_use_flag = ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=use_account_inactivity_lockout_enable")
                logging.info(get_use_flag)
                res = json.loads(get_use_flag)
                use_flag_condition = res['use_account_inactivity_lockout_enable']
                use_flag_data = {'use_account_inactivity_lockout_enable': True}
                if (use_flag_condition == use_flag_data['use_account_inactivity_lockout_enable'] ):
                    logging.info("Successfully verified that default group admin-group can be overridden")
                    assert True
                else:
                    logging.error("FAILED to verify that default group admin-group can be overridden")
                    assert False
                logging.info("Enabling Account Inactivity Lockout with custom values for admin-group")
                input_data = {'inactivity_lockout_setting': {'reactivate_via_serial_console_enable': False, 'reminder_days': 10, 'account_inactivity_lockout_enable': True, 'reactivate_via_remote_console_enable': True, 'inactive_days': 20}}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(input_data),grid_vip=config.grid_vip)
                logging.info(response)
                logging.info("Get inactivity lockout settings for ADMIN GROUP")
                get_lockout_setting = ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=inactivity_lockout_setting")
                logging.info(get_lockout_setting)
                res = json.loads(get_lockout_setting)
                data = {'reactivate_via_serial_console_enable': False, 'reminder_days': 10, 'account_inactivity_lockout_enable': True, 'reactivate_via_remote_console_enable': True, 'inactive_days': 20}
                condition = res['inactivity_lockout_setting']
                logging.info("Verifying if Account Inactivity Lockout can be Enabled with custom values for default group admin-group")
                if (condition['account_inactivity_lockout_enable'] == data['account_inactivity_lockout_enable'] and condition['inactive_days'] == data['inactive_days'] and \
                condition['reminder_days'] == data['reminder_days'] and condition['reactivate_via_serial_console_enable'] == data['reactivate_via_serial_console_enable'] and \
                condition['reactivate_via_remote_console_enable'] == data['reactivate_via_remote_console_enable']):
                    logging.info("Successfully verified that Account Inactivity Lockout can be Enabled with custom values for default group admin-group")
                    assert True
                else:
                    logging.error("FAILED to verify that Account Inacitvity Lockout can be Enabled with custom values for default group admin-group")
                    logging.info("Expected Setting")
                    logging.info(data)
                    logging.info("Actual Setting")
                    logging.info(condition)
                    assert False
                logging.info("Restoring settings to original")
                input_data = {'inactivity_lockout_setting': {'reactivate_via_serial_console_enable': True, 'reminder_days': 15, 'account_inactivity_lockout_enable': False, 'reactivate_via_remote_console_enable': True, 'inactive_days': 30}}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(input_data),grid_vip=config.grid_vip)
                logging.info(response)

    @pytest.mark.run(order=7)
    def test_07_default_group_override_and_disable(self):
        logging.info("===================================================================================================================================")
        logging.info("EXECUTING TEST CASE : test_07_default_group_override_and_disable")
        logging.info("This Test Case will verify that default group can be successfully overridden and disabled for Account Inactivity Lockout")
        logging.info("===================================================================================================================================")
        all_ref = get_reference_value_admingroup()
        res = json.loads(all_ref)
        count = len(res)
        for current_group in range(count):
            ref1 = json.loads(all_ref)[current_group]['_ref']
            admin_group = json.loads(all_ref)[current_group]['name']
            if (admin_group == "admin-group"):
                logging.info("Testing if default group admin-group can be overridden for Inactivity Lockout Setting")
                input_data = {'use_account_inactivity_lockout_enable': True}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(input_data),grid_vip=config.grid_vip)
                logging.info(response)
                logging.info("Get use flag - use_account_inactivity_lockout_enable for admin-group")
                get_use_flag = ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=use_account_inactivity_lockout_enable")
                logging.info(get_use_flag)
                res = json.loads(get_use_flag)
                use_flag_condition = res['use_account_inactivity_lockout_enable']
                use_flag_data = {'use_account_inactivity_lockout_enable': True}
                if (use_flag_condition == use_flag_data['use_account_inactivity_lockout_enable'] ):
                    logging.info("Successfully verified that default group admin-group can be overridden")
                    assert True
                else:
                    logging.error("FAILED to verify that default group admin-group can be overridden")
                    assert False
                logging.info("Disabling Account Inactivity Lockout for admin-group")
                input_data = {'inactivity_lockout_setting': {'reactivate_via_serial_console_enable': True, 'reminder_days': 3, 'account_inactivity_lockout_enable': False, 'reactivate_via_remote_console_enable': True, 'inactive_days': 7}}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(input_data),grid_vip=config.grid_vip)
                logging.info(response)
                logging.info("Get inactivity lockout settings for ADMIN GROUP")
                get_lockout_setting = ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=inactivity_lockout_setting")
                logging.info(get_lockout_setting)
                res = json.loads(get_lockout_setting)
                data = {'reactivate_via_serial_console_enable': True, 'reminder_days': 3, 'account_inactivity_lockout_enable': False, 'reactivate_via_remote_console_enable': True, 'inactive_days': 7}
                condition = res['inactivity_lockout_setting']
                logging.info("Verifying if Account Inactivity Lockout can be Disabled for default group admin-group")
                if (condition['account_inactivity_lockout_enable'] == data['account_inactivity_lockout_enable'] and condition['inactive_days'] == data['inactive_days'] and \
                condition['reminder_days'] == data['reminder_days'] and condition['reactivate_via_serial_console_enable'] == data['reactivate_via_serial_console_enable'] and \
                condition['reactivate_via_remote_console_enable'] == data['reactivate_via_remote_console_enable']):
                    logging.info("Successfully verified that Account Inactivity Lockout can be Disabled for default group admin-group")
                    assert True
                else:
                    logging.error("FAILED to verify that Account Inacitvity Lockout can be Disabled for default group admin-group")
                    logging.info("Expected Setting")
                    logging.info(data)
                    logging.info("Actual Setting")
                    logging.info(condition)
                    assert False
                logging.info("Restoring settings to original")
                input_data = {'inactivity_lockout_setting': {'reactivate_via_serial_console_enable': True, 'reminder_days': 15, 'account_inactivity_lockout_enable': False, 'reactivate_via_remote_console_enable': True, 'inactive_days': 30}}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(input_data),grid_vip=config.grid_vip)
                logging.info(response)

    @pytest.mark.run(order=8)
    def test_08_new_group_inactivity_lockout_default_settings(self):
        logging.info("===================================================================================================================================")
        logging.info("EXECUTING TEST CASE : test_08_new_group_inactivity_lockout_default_settings")
        logging.info("This Test Case will verify that the Inactivity Lockout Setting is Inheritted from GRID for newly created user group by default")
        logging.info("===================================================================================================================================")
        logging.info("Creating a new Admin Group vasu-test-group")
        group={"name":"vasu-test-group","superuser":True}
        get_ref_group = ib_NIOS.wapi_request('POST',object_type="admingroup", fields=json.dumps(group))
        logging.info(get_ref_group)
        all_ref = get_reference_value_admingroup()
        res = json.loads(all_ref)
        count = len(res)
        for current_group in range(count):
            ref1 = json.loads(all_ref)[current_group]['_ref']
            admin_group = json.loads(all_ref)[current_group]['name']
            if (admin_group == "vasu-test-group"):
                logging.info("Get use flag - use_account_inactivity_lockout_enable for vasu-test-group")
                get_use_flag = ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=use_account_inactivity_lockout_enable")
                logging.info(get_use_flag)
                res = json.loads(get_use_flag)
                use_flag_condition = res['use_account_inactivity_lockout_enable']
                use_flag_data = {'use_account_inactivity_lockout_enable': False}
                if (use_flag_condition == use_flag_data['use_account_inactivity_lockout_enable'] ):
                    logging.info("Successfully verified that vasu-test-group has inherited Account Inactivity Lockout Setting from GRID by default as Expected")
                    assert True
                else:
                    logging.error("FAILED to verify that vasu-test-group has inherited Account Inactivity Lockout Setting from GRID by default")
                    logging.info("Expected Setting")
                    logging.info(res)
                    logging.info("Actual Setting")
                    logging.info(use_flag_data)
                    assert False

    @pytest.mark.run(order=9)
    def test_09_new_group_inactivity_lockout_override_and_enable(self):
        logging.info("===================================================================================================================================")
        logging.info("EXECUTING TEST CASE : test_09_new_group_inactivity_lockout_override_and_enable")
        logging.info("This Test Case will verify that the Inactivity Lockout Setting can be overridden and enabled for newly created user group")
        logging.info("===================================================================================================================================")
        all_ref = get_reference_value_admingroup()
        res = json.loads(all_ref)
        count = len(res)
        for current_group in range(count):
            ref1 = json.loads(all_ref)[current_group]['_ref']
            admin_group = json.loads(all_ref)[current_group]['name']
            if (admin_group == "vasu-test-group"):
                logging.info("Modifying Admin Group vasu-test-group to override for Inactivity Lockout Setting")
                input_data = {'use_account_inactivity_lockout_enable': True}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(input_data),grid_vip=config.grid_vip)
                logging.info(response)
                logging.info("Get use flag - use_account_inactivity_lockout_enable for vasu-test-group")
                get_use_flag = ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=use_account_inactivity_lockout_enable")
                logging.info(get_use_flag)
                res = json.loads(get_use_flag)
                use_flag_condition = res['use_account_inactivity_lockout_enable']
                use_flag_data = {'use_account_inactivity_lockout_enable': True}
                if (use_flag_condition == use_flag_data['use_account_inactivity_lockout_enable'] ):
                    logging.info("Successfully verified that vasu-test-group has been overridden for Account Inactivity Lockout as Expected")
                    assert True
                else:
                    logging.error("FAILED to verify that vasu-test-group has been overridden for Account Inactivity Lockout")
                    logging.info("Expected Setting")
                    logging.info(res)
                    logging.info("Actual Setting")
                    logging.info(use_flag_data)
                    assert False
                logging.info("Enabling Account Inactivity Lockout with custom values for Admin Group vasu-test-group")
                input_data = {'inactivity_lockout_setting': {'reactivate_via_serial_console_enable': True, 'reminder_days': 2, 'account_inactivity_lockout_enable': True, 'reactivate_via_remote_console_enable': False, 'inactive_days': 4}}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(input_data),grid_vip=config.grid_vip)
                logging.info(response)
                logging.info("Get inactivity lockout settings for ADMIN GROUP vasu-test-groupo")
                get_lockout_setting = ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=inactivity_lockout_setting")
                logging.info(get_lockout_setting)
                res = json.loads(get_lockout_setting)
                data = {'reactivate_via_serial_console_enable': True, 'reminder_days': 2, 'account_inactivity_lockout_enable': True, 'reactivate_via_remote_console_enable': False, 'inactive_days': 4}
                condition = res['inactivity_lockout_setting']
                logging.info("Verifying if Account Inactivity Lockout can be Enabled with custom values for Admin Group vasu-test-group")
                if (condition['account_inactivity_lockout_enable'] == data['account_inactivity_lockout_enable'] and condition['inactive_days'] == data['inactive_days'] and \
                condition['reminder_days'] == data['reminder_days'] and condition['reactivate_via_serial_console_enable'] == data['reactivate_via_serial_console_enable'] and \
                condition['reactivate_via_remote_console_enable'] == data['reactivate_via_remote_console_enable']):
                    logging.info("Successfully verified that Account Inactivity Lockout can be Enabled with custom values for Admin Group vasu-test-group")
                    assert True
                else:
                    logging.error("FAILED to verify that Account Inacitvity Lockout can be Enabled with custom values for Admin Group vasu-test-group")
                    logging.info("Expected Setting")
                    logging.info(data)
                    logging.info("Actual Setting")
                    logging.info(condition)
                    assert False

    @pytest.mark.run(order=10)
    def test_10_new_group_inactivity_lockout_override_and_disable(self):
        logging.info("===================================================================================================================================")
        logging.info("EXECUTING TEST CASE : test_10_new_group_inactivity_lockout_override_and_disable")
        logging.info("This Test Case will verify that the Inactivity Lockout Setting can be overridden and disabled for newly created user group")
        logging.info("===================================================================================================================================")
        all_ref = get_reference_value_admingroup()
        res = json.loads(all_ref)
        count = len(res)
        for current_group in range(count):
            ref1 = json.loads(all_ref)[current_group]['_ref']
            admin_group = json.loads(all_ref)[current_group]['name']
            if (admin_group == "vasu-test-group"):
                logging.info("Disabling Account Inactivity Lockout for Admin Group vasu-test-group")
                input_data = {'inactivity_lockout_setting': {'reactivate_via_serial_console_enable': True, 'reminder_days': 15, 'account_inactivity_lockout_enable': False, 'reactivate_via_remote_console_enable': True, 'inactive_days': 30}}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(input_data),grid_vip=config.grid_vip)
                logging.info(response)
                logging.info("Get inactivity lockout settings for ADMIN GROUP vasu-test-groupo")
                get_lockout_setting = ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=inactivity_lockout_setting")
                logging.info(get_lockout_setting)
                res = json.loads(get_lockout_setting)
                data = {'reactivate_via_serial_console_enable': True, 'reminder_days': 15, 'account_inactivity_lockout_enable': False, 'reactivate_via_remote_console_enable': True, 'inactive_days': 30}
                condition = res['inactivity_lockout_setting']
                logging.info("Verifying if Account Inactivity Lockout can be Enabled with custom values for Admin Group vasu-test-group")
                if (condition['account_inactivity_lockout_enable'] == data['account_inactivity_lockout_enable'] and condition['inactive_days'] == data['inactive_days'] and \
                condition['reminder_days'] == data['reminder_days'] and condition['reactivate_via_serial_console_enable'] == data['reactivate_via_serial_console_enable'] and \
                condition['reactivate_via_remote_console_enable'] == data['reactivate_via_remote_console_enable']):
                    logging.info("Successfully verified that Account Inactivity Lockout can be Disabled for Admin Group vasu-test-group")
                    assert True
                else:
                    logging.error("FAILED to verify that Account Inacitvity Lockout can be Disabled for Admin Group vasu-test-group")
                    logging.info("Expected Setting")
                    logging.info(data)
                    logging.info("Actual Setting")
                    logging.info(condition)
                    assert False

    @pytest.mark.run(order=11)
    def test_11_new_group_inactivity_lockout_inherit_from_grid(self):
        logging.info("===================================================================================================================================")
        logging.info("EXECUTING TEST CASE : test_11_new_group_inactivity_lockout_inherit_from_grid")
        logging.info("This Test Case will verify that the Inactivity Lockout Setting can be inherited from Grid for newly created user group")
        logging.info("===================================================================================================================================")
        all_ref = get_reference_value_admingroup()
        res = json.loads(all_ref)
        count = len(res)
        for current_group in range(count):
            ref1 = json.loads(all_ref)[current_group]['_ref']
            admin_group = json.loads(all_ref)[current_group]['name']
            if (admin_group == "vasu-test-group"):
                logging.info("Modifying Admin Group vasu-test-group to inherit from Grid for Inactivity Lockout Setting")
                input_data = {'use_account_inactivity_lockout_enable': False}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(input_data),grid_vip=config.grid_vip)
                logging.info(response)
                logging.info("Get use flag - use_account_inactivity_lockout_enable for vasu-test-group")
                get_use_flag = ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=use_account_inactivity_lockout_enable")
                logging.info(get_use_flag)
                res = json.loads(get_use_flag)
                use_flag_condition = res['use_account_inactivity_lockout_enable']
                use_flag_data = {'use_account_inactivity_lockout_enable': False}
                if (use_flag_condition == use_flag_data['use_account_inactivity_lockout_enable'] ):
                    logging.info("Successfully verified that vasu-test-group has been inherited from Grid for Account Inactivity Lockout as Expected")
                    assert True
                else:
                    logging.error("FAILED to verify that vasu-test-group has been inherited from Grid for Account Inactivity Lockout")
                    logging.info("Expected Setting")
                    logging.info(res)
                    logging.info("Actual Setting")
                    logging.info(use_flag_data)
                    assert False

    @pytest.mark.run(order=12)
    def test_12_negative_and_boundary_testing(self):
        logging.info("===================================================================================================================================")
        logging.info("EXECUTING TEST CASE : test_12_negative_and_boundary_testing")
        logging.info("This Test Case will that proper error messages are obtained for negative and out of boundary cases")
        logging.info("===================================================================================================================================")
        ref1 = get_reference_value_grid()
        input_data = {'security_setting':{'inactivity_lockout_setting':{'account_inactivity_lockout_enable': True,"inactive_days":10000, "reminder_days":3, "reactivate_via_remote_console_enable": False, "reactivate_via_serial_console_enable": False}}}
        logging.info("Trying to set out of boundary value 10000 for Inactive Days")
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(input_data),grid_vip=config.grid_vip)
        logging.info(response)
        if (response[0] == 400):
            logging.info("Successfully verified that error is obtained while trying to set out of boundary value 10000 for Inactive Days")
            assert True
        else:
            logging.error("FAILED to verify that error is obtained while trying to set out of boundary value 10000 for Inactive Days")
            assert False
        input_data = {'security_setting':{'inactivity_lockout_setting':{'account_inactivity_lockout_enable': True,"inactive_days":-1, "reminder_days":3, "reactivate_via_remote_console_enable": False, "reactivate_via_serial_console_enable": False}}}
        logging.info("Trying to set value -1 for Inactive Days")
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(input_data),grid_vip=config.grid_vip)
        logging.info(response)
        if (response[0] == 400):
            logging.info("Successfully verified that error is obtained while trying to set value -1 for Inactive Days")
            assert True
        else:
            logging.error("FAILED to verify that error is obtained while trying to set out of boundary value -1 for Inactive Days")
            assert False
        input_data = {'security_setting':{'inactivity_lockout_setting':{'account_inactivity_lockout_enable': True,"inactive_days":7, "reminder_days":0, "reactivate_via_remote_console_enable": False, "reactivate_via_serial_console_enable": False}}}
        logging.info("Trying to set out of boundary value 0 for Reminder Days")
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(input_data),grid_vip=config.grid_vip)
        logging.info(response)
        if (response[0] == 400):
            logging.info("Successfully verified that error is obtained while trying to set out of boundary value 0 for Reminder Days")
            assert True
        else:
            logging.error("FAILED to verify that error is obtained while trying to set out of boundary value 0 for Reminder Days")
            assert False
        input_data = {'security_setting':{'inactivity_lockout_setting':{'account_inactivity_lockout_enable': True,"inactive_days":7, "reminder_days":31, "reactivate_via_remote_console_enable": False, "reactivate_via_serial_console_enable": False}}}
        logging.info("Trying to set out of boundary value 31 for Reminder Days")
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(input_data),grid_vip=config.grid_vip)
        logging.info(response)
        if (response[0] == 400):
            logging.info("Successfully verified that error is obtained while trying to set out of boundary value 31 for Reminder Days")
            assert True
        else:
            logging.error("FAILED to verify that error is obtained while trying to set out of boundary value 31 for Reminder Days")
            assert False
        input_data = {'security_setting':{'inactivity_lockout_setting':{'account_inactivity_lockout_enable': True,"inactive_days":7, "reminder_days":"@", "reactivate_via_remote_console_enable": False, "reactivate_via_serial_console_enable": False}}}
        logging.info("Trying to set special character @ for Reminder Days")
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(input_data),grid_vip=config.grid_vip)
        logging.info(response)
        if (response[0] == 400):
            logging.info("Successfully verified that error is obtained while trying to set special character @ for Reminder Days")
            assert True
        else:
            logging.error("FAILED to verify that error is obtained while trying to set special character @ for Reminder Days")
            assert False
        input_data = {'security_setting':{'inactivity_lockout_setting':{'account_inactivity_lockout_enable': "Traa","inactive_days":7, "reminder_days":3, "reactivate_via_remote_console_enable": False, "reactivate_via_serial_console_enable": False}}}
        logging.info("Trying to set wrong value instead of boolean value True for account_inactivity_lockout_enable")
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(input_data),grid_vip=config.grid_vip)
        logging.info(response)
        if (response[0] == 400):
            logging.info("Successfully verified that error is obtained while trying to wrong value instead of boolean value True for account_inactivity_lockout_enable")
            assert True
        else:
            logging.error("FAILED to verify that error is obtained while trying to set wrong value instead of boolean value True for account_inactivity_lockout_enable")
            assert False

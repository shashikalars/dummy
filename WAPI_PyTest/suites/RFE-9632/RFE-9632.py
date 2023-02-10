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
import getpass
import sys


class Network(unittest.TestCase):
    logging.basicConfig(filename='example.log', filemode='w', level=logging.DEBUG)

    @pytest.mark.run(order=1)
    def test_01_creating_ms_server_all_fields(self):
	logging.info("Create a MS Server with all fields")
	data = {"address":"10.11.10.10","login_name":"hello","login_password":"Infoblox123","synchronization_min_delay":2,"dns_view": "default","log_level":"ADVANCED","log_destination":"MSLOG","use_log_destination":True,"comment":"hello","ad_sites": {"ldap_auth_port": 389,"ldap_encryption": "NONE","login_name": "abcd","managed": True,"read_only": True,"synchronization_min_delay": 2,"use_default_ip_site_link": False,"use_ldap_timeout": False,"use_login": False,"use_synchronization_min_delay": False},"ad_user": {"enable_user_sync": False,"login_name": "abcd","synchronization_interval": 2,"use_enable_ad_user_sync": False,"use_enable_user_sync": False,"use_login": False,"use_synchronization_interval": False,"use_synchronization_min_delay": False},"dhcp_server": {"enable_invalid_mac": True,"enable_monitoring": True,"login_name": "abcd","managed": True,"next_sync_control": "NONE","synchronization_min_delay": 2,"use_enable_invalid_mac": False,"use_enable_monitoring": False,"use_login": False,"use_synchronization_min_delay": False},"dns_server": {"enable_dns_reports_sync": False,"enable_monitoring": True,"login_name": "abcd","managed": True,"next_sync_control": "NONE","synchronization_min_delay": 2,"use_enable_dns_reports_sync": False,"use_enable_monitoring": False,"use_login": False,"use_synchronization_min_delay": False}}
	response = ib_NIOS.wapi_request('POST',object_type="msserver",fields=json.dumps(data))
        print("&&&&&&&&&&&&&&&&&&&&&&&",response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 1 Execution Completed")
	logging.info("Test Case 1 Execution Completed")
        logging.info("============================")


    @pytest.mark.run(order=2)
    def test_02_modifying_ms_server_all_fields(self):
	logging.info("Modify a MS Server from all fields to mandatory fields")
	get_ref = ib_NIOS.wapi_request('GET', object_type="msserver?address=10.11.10.10")
	logging.info(get_ref)
	ref1 = json.loads(get_ref)[0]['_ref']
        print("++++++++++++++++++++++",ref1)
        logging.info (ref1)
	data = {"address":"10.11.10.11","login_name":"www.hello.com","login_password":""}
	response = ib_NIOS.wapi_request('PUT',object_type="msserver",fields=json.dumps(data),ref=ref1)
	print("&&&&&&&&&&&&&&&&&&&&&&&",response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 2 Execution Completed")
        logging.info("Test Case 2 Execution Completed")
        logging.info("============================")
        

    @pytest.mark.run(order=3)
    def test_03_creating_ms_server_mandatory_fields(self):
        logging.info("Creating MS Server with only mandatory fields")
        data={"address": "11.11.10.10","login_name": "add"}
	response = ib_NIOS.wapi_request('POST',object_type="msserver",fields=json.dumps(data))
	print("&&&&&&&&&&&&&&&&&&&&&&&",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 3 Execution Completed")
        logging.info("Test Case 3 Execution Completed")
        logging.info("============================")

    @pytest.mark.run(order=4)
    def test_04_creating_ms_server_mandatory_fields_character_address(self):
        logging.info("Creating MS Server with only mandatory fields/character address")
        data={"address": "hello.com","login_name": "add"}
        response = ib_NIOS.wapi_request('POST',object_type="msserver",fields=json.dumps(data))
        print("&&&&&&&&&&&&&&&&&&&&&&&",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 4 Execution Completed")
        logging.info("Test Case 4 Execution Completed")
        logging.info("============================")


    @pytest.mark.run(order=5)
    def test_05_modifying_ms_server_mandatory_fields_negative(self):
        logging.info("Modify a MS Server from mandatory fields to all fields")
        get_ref = ib_NIOS.wapi_request('GET', object_type="msserver?address=hello.com")
	print("&&&&&&&&&&&&&&&&&&&&&&&",get_ref)
        logging.info(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        print("++++++++++++++++++++++",ref1)
        logging.info (ref1)
	data = {"address":"10.11.10.12","login_name":"hello","login_password":"Infoblox123","synchronization_min_delay":2,"dns_view": "default","log_level":"ADVANCED","log_destination":"MSLOG","use_log_destination":True,"comment":"hello","ad_sites": {"ldap_auth_port": 389,"ldap_encryption": "NONE","login_name": "abcd","managed": True,"read_only": True,"synchronization_min_delay": 2,"use_default_ip_site_link": False,"use_ldap_timeout": False,"use_login": False,"use_synchronization_min_delay": False},"ad_user": {"enable_user_sync": False,"login_name": "abcd","synchronization_interval": 2,"use_enable_ad_user_sync": False,"use_enable_user_sync": False,"use_login": False,"use_synchronization_interval": False,"use_synchronization_min_delay": False},"dhcp_server": {"enable_invalid_mac": True,"enable_monitoring": True,"login_name": "abcd","managed": True,"next_sync_control": "NONE","synchronization_min_delay": 2,"use_enable_invalid_mac": False,"use_enable_monitoring": False,"use_login": False,"use_synchronization_min_delay": False},"dns_server": {"enable_dns_reports_sync": False,"enable_monitoring": True,"login_name": "abcd","managed": True,"next_sync_control": "NONE","synchronization_min_delay": 2,"use_enable_dns_reports_sync": False,"use_enable_monitoring": False,"use_login": False,"use_synchronization_min_delay": False}}
	response = ib_NIOS.wapi_request('PUT',object_type="msserver",fields=json.dumps(data),ref=ref1)
        print("&&&&&&&&&&&&&&&&&&&&&&&",response)
        if (response[0]==400):
            print("The Network Users feature should be enabled")
            assert True
        else:
            print("The Network Users feature is already enabled")
            assert False
        print("Test Case 5 Execution Completed")
        logging.info("Test Case 5 Execution Completed")
        logging.info("============================")

    @pytest.mark.run(order=6)
    def test_06_enable_network_users(self):
	logging.info("Enable Network Users")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid?_return_fields=ms_setting")
        logging.info(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        print("++++++++++++++++++++++",ref1)
	data = {"ms_setting": {"enable_network_users": True}}
	response = ib_NIOS.wapi_request('PUT',ref=ref1,object_type="grid",fields=json.dumps(data))
	print("&&&&&&&&&&&&&&&&&&&&&&&",response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 6 Execution Completed")
        logging.info("Test Case 6 Execution Completed")
        logging.info("============================")

 
    @pytest.mark.run(order=7)
    def test_07_modifying_ms_server_mandatory_fields(self):
        logging.info("Modify a MS Server from all fields to mandatory fields")
        get_ref = ib_NIOS.wapi_request('GET', object_type="msserver?address=hello.com")
        print("&&&&&&&&&&&&&&&&&&&&&&&",get_ref)
        logging.info(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        print("++++++++++++++++++++++",ref1)
        logging.info (ref1)
        data = {"address":"10.11.10.12","login_name":"hello","login_password":"Infoblox123","synchronization_min_delay":2,"dns_view": "default","log_level":"ADVANCED","log_destination":"MSLOG","use_log_destination":True,"comment":"hello","ad_sites": {"ldap_auth_port": 389,"ldap_encryption": "NONE","login_name": "abcd","managed": True,"read_only": True,"synchronization_min_delay": 2,"use_default_ip_site_link": False,"use_ldap_timeout": False,"use_login": False,"use_synchronization_min_delay": False},"ad_user": {"enable_user_sync": False,"login_name": "abcd","synchronization_interval": 2,"use_enable_ad_user_sync": False,"use_enable_user_sync": False,"use_login": False,"use_synchronization_interval": False,"use_synchronization_min_delay": False},"dhcp_server": {"enable_invalid_mac": True,"enable_monitoring": True,"login_name": "abcd","managed": True,"next_sync_control": "NONE","synchronization_min_delay": 2,"use_enable_invalid_mac": False,"use_enable_monitoring": False,"use_login": False,"use_synchronization_min_delay": False},"dns_server": {"enable_dns_reports_sync": False,"enable_monitoring": True,"login_name": "abcd","managed": True,"next_sync_control": "NONE","synchronization_min_delay": 2,"use_enable_dns_reports_sync": False,"use_enable_monitoring": False,"use_login": False,"use_synchronization_min_delay": False}}
        response = ib_NIOS.wapi_request('PUT',object_type="msserver",fields=json.dumps(data),ref=ref1)
        print("&&&&&&&&&&&&&&&&&&&&&&&",response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 7 Execution Completed")
        logging.info("Test Case 7 Execution Completed")
        logging.info("============================")

    @pytest.mark.run(order=8)
    def test_08_disable_network_users(self):
        logging.info("Disable Network Users")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid?_return_fields=ms_setting")
        logging.info(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        print("++++++++++++++++++++++",ref1)
        data = {"ms_setting": {"enable_network_users": False}}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,object_type="grid",fields=json.dumps(data))
        print("&&&&&&&&&&&&&&&&&&&&&&&",response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 8 Execution Completed")
        logging.info("Test Case 8 Execution Completed")
        logging.info("============================")


    @pytest.mark.run(order=9)
    def test_09_creating_ms_server_extensible_attributes(self):
        logging.info("Creating MS Server with EA")
	data={"name": "Custom","type":"INTEGER"}
	response = ib_NIOS.wapi_request('POST',object_type="extensibleattributedef",fields=json.dumps(data))
	print("&&&&&&&&&&&&&&&&&&&&&&&",response)
	data={"address": "11.11.10.11","login_name": "EA","extattrs": {"Custom": {"value": "100"}}}
	response = ib_NIOS.wapi_request('POST',object_type="msserver",fields=json.dumps(data))
        print("&&&&&&&&&&&&&&&&&&&&&&&",response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 9 Execution Completed")
        logging.info("Test Case 9 Execution Completed")
        logging.info("============================")
	
    @pytest.mark.run(order=10)
    def test_10_deleting_ms_server_all_fields(self):
	logging.info("Deleting MS Server")
	get_ref = ib_NIOS.wapi_request('GET', object_type="msserver?address=10.11.10.11")
        print get_ref
        logging.info(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        print ref1
	response = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
        logging.info(response)
        get_ref = ib_NIOS.wapi_request('GET', object_type="msserver?address=10.11.10.12")
        print get_ref
        logging.info(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        print ref1
        response = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
        logging.info(response)
        get_ref = ib_NIOS.wapi_request('GET', object_type="msserver?address=11.11.10.10")
        print get_ref
        logging.info(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        print ref1
        response = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
        logging.info(response)
        get_ref = ib_NIOS.wapi_request('GET', object_type="msserver?address=11.11.10.11")
        print get_ref
        logging.info(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        print ref1
        response = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 10 Execution Completed")
        logging.info("Test Case 10 Execution Completed")
        logging.info("============================")

	
    

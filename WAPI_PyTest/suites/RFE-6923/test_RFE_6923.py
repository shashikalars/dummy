import re
import config
import pytest
import unittest
import logging
import subprocess
import os
import json
import config
import ib_utils.ib_NIOS as ib_NIOS
from time import sleep
from paramiko import client
import commands
import json, ast
import requests
import time
import pexpect
import getpass
import sys
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv


def get_reference_value_grid():
    logging.info("get reference value for GRID")
    get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
    logging.info(get_ref)
    res = json.loads(get_ref)
    ref1 = json.loads(get_ref)[0]['_ref']
    logging.info (ref1)
    return ref1

def get_email_settings():
    ref = get_reference_value_grid()
    logging.info("get EMAIL settings for GRID")
    get_ref = ib_NIOS.wapi_request('GET', object_type=ref+"?_return_fields=email_setting")
    logging.info(get_ref)
    res = json.loads(get_ref)
    return res

def get_security_settings():
    ref1=get_reference_value_grid()
    logging.info("get security settings for GRID")
    get_ref = ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=security_setting")
    logging.info(get_ref)
    res = json.loads(get_ref)
    return res

class Network(unittest.TestCase):
    logging.basicConfig(filename='example.log', filemode='w', level=logging.DEBUG)
    
    @pytest.mark.run(order=1)
    def test_01_create_super_user_group(self):

        logging.info("Creating User Group for testing concurrent login features")
        group={"name":"test1","superuser":True}
        get_ref_group = ib_NIOS.wapi_request('POST',object_type="admingroup", fields=json.dumps(group))
        logging.info(get_ref_group)
        if (get_ref_group[0] == 400):
            print("Duplicate object \'test1\' of type \'admin_group\' already exists in the database")
        else:
            print("User \'test1\' has been created")

	# VALIDATING THE GROUP HAS BEEN CREATED
        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup?name=test1")
        logging.info(get_ref)
        ref1 = json.loads(get_ref)[0]['name']
	if(ref1 == "test1"):
	    assert True
	else:
	    assert False

        user={"name":"testusr1","password":"infoblox","admin_groups":["test1"]}
        get_ref = ib_NIOS.wapi_request('POST',object_type="adminuser", fields=json.dumps(user))
        logging.info (get_ref)
        if (get_ref[0] == 400):
            print("Duplicate object \'testusr1\' of type \'adminuser\' already exists in the database")
        else:
            print("User \'test1usr\' has been created")

        # VALIDATING THE USER HAS BEEN CREATED        
        get_ref = ib_NIOS.wapi_request('GET', object_type="adminuser?name=testusr1")
        logging.info(get_ref)
        ref1 = json.loads(get_ref)[0]['name']
        if(ref1 == "testusr1"):
            assert True
        else:
            assert False


    @pytest.mark.run(order=2)
    def test_02_enable_email_trap_notifications_grid(self):
	grid_ref = get_reference_value_grid()
	logging.info ("Enabling EMAIL notifications and DNS resolver")
	data1 = {"email_setting": {"address": config.email_id,"enabled": True,"port_number": 25}}	
	response = ib_NIOS.wapi_request('PUT',ref=grid_ref,fields=json.dumps(data1),grid_vip=config.grid_vip)	
	print(response)

	#VALIDATING EMAIL SETTING
	email_settings = get_email_settings()
	condition = email_settings['email_setting']['address']
        if(condition==(data1['email_setting']['address'])):
	    assert True
	    print("EMAIL settings are correct")
	else:
	    assert False
	    print("EMAIL setting is incorrect")

        condition = email_settings['email_setting']['enabled']
        if(condition==(data1['email_setting']['enabled'])):
            assert True
            print("EMAIL settings are correct")
        else:
            assert False
            print("EMAIL setting is incorrect")

        condition = email_settings['email_setting']['port_number']
        if(condition==(data1['email_setting']['port_number'])):
            assert True
            print("EMAIL settings are correct")
        else:
            assert False
            print("EMAIL setting is incorrect")

	data2 = {"dns_resolver_setting": {"resolvers": [config.resolver_ip]}}
	response1 = ib_NIOS.wapi_request('PUT',ref=grid_ref,fields=json.dumps(data2),grid_vip=config.grid_vip)
        print(response1)

	data3 = {"trap_notifications": [{"enable_email": True,"enable_trap": True,"trap_type": "Login"},{"enable_email": True,"enable_trap": True,"trap_type": "Clear"},{"enable_email": True,"enable_trap": True,"trap_type": "Reporting"}]} 
	response2 = ib_NIOS.wapi_request('PUT',ref=grid_ref,fields=json.dumps(data3),grid_vip=config.grid_vip)
        print(response2)
	sleep(10)
	print("Test Case 2 Execution Completed")

    @pytest.mark.run(order=3)
    def test_03_start_infoblox_logs(self):
        logging.info("Starting Infoblox Logs")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("test case 2 passed")
        sleep(5)
        print("Test Case 3 Execution Completed")

    @pytest.mark.run(order=4)
    def test_04_disabling_login_grid_level(self):
        ref1=get_reference_value_grid()
        logging.info ("Enabling concurrent login for grid level")
        data={"security_setting":{"disable_concurrent_login" : False}}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
        logging.info(response)
        logging.info("============================")
        settings=get_security_settings()
        logging.info (settings)
        condition=settings['security_setting']['disable_concurrent_login']
        if (condition==(data['security_setting']['disable_concurrent_login'])):
            assert True
            logging.info("Test case 4 Passed for disabling Concurrent Login at grid level")
        else:
            logging.info("Test case 4 Failed for disabling Concurrent Login at grid level")
	    assert False

    @pytest.mark.run(order=5)
    def test_05_stop_infoblox_Logs(self):
        sleep(10)
        logging.info("Stopping Infoblox Logs")
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        print("Test Case 5 Execution Completed")


    @pytest.mark.run(order=6)
    def test_06_validate_SPLUNK_REPORTING_ADMIN_logs(self):
        logging.info("Validating $SPLUNK_REPORTING_ADMIN log for admin")
        LookFor="Concurrent_Login_Denied"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test Case 6 Execution Completed")
            assert True
        else:
            logging.info("Test Case 6 Execution Failed")
            assert False


    @pytest.mark.run(order=7)
    def test_07_start_infoblox_logs(self):
        logging.info("Starting Infoblox Logs")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("test case 7 passed")
        sleep(5)
	print("Test Case 7 Execution Completed")

    @pytest.mark.run(order=8)
    def test_08_enabling_login_grid_level(self):
        ref1 = get_reference_value_grid()
        logging.info ("Disable concurrent login at grid level")
        data = {"security_setting": {"disable_concurrent_login": True}}
        response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data), grid_vip=config.grid_vip)
        logging.info(response)
        logging.info("============================")
        settings = get_security_settings()
        logging.info(settings)
        logging.info ("Status after passing True value ; ", settings)
        condition = settings['security_setting']['disable_concurrent_login']
        logging.info("***********Condition after passing value*************",condition)
        logging.info ("**********condition passsed in data*************",data['security_setting']['disable_concurrent_login'])
        if (condition == (data['security_setting']['disable_concurrent_login'])):
            assert True
            logging.info("Test case 8 Passed for enabling Concurrent Login at grid level ")
        else:
            logging.info("Test case 8 Failed for enabling Concurrent Login at grid level")
	    assert False

    @pytest.mark.run(order=9)
    def test_09_stop_infoblox_Logs(self):
	sleep(120)
        logging.info("Stopping Infoblox Logs")
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        print("Test Case 9 Execution Completed")


    @pytest.mark.run(order=10)
    def test_10_validate_CONCURRENT_LOGIN_SPLUNK_REPORTING_ADMIN_logs(self):
        logging.info("Validating Concurrent_Login_Denied $SPLUNK_REPORTING_ADMIN log for admin")
        LookFor="Concurrent_Login_Denied | $SPLUNK-REPORTING-ADMIN$"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test Case 10 Execution Completed")
            assert True
        else:
            logging.info("Test Case 10 Execution Failed")
            assert False

    @pytest.mark.run(order=11)
    def test_11_validate_snmp_traps_logs(self):
        logging.info("Validating SNMP traps should not be sent for $SPLUNK-REPORTING-ADMIN user")
        LookFor="one_send_snmp_trap"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test Case 11 Execution Completed")
            assert True
        else:
            logging.info("Test Case 11 Execution Failed")
            assert False

    @pytest.mark.run(order=12)
    def test_12_validate_email_notifications_logs(self):
        logging.info("Validating email notifications should not be sent for $SPLUNK-REPORTING-ADMIN user")
        LookFor="one_send_snmp_trap_email_with_ack"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test Case 12 Execution Completed")
            assert True
        else:
            logging.info("Test Case 12 Execution Failed")
            assert False


    @pytest.mark.run(order=13)
    def test_13_start_infoblox_logs(self):
        logging.info("Starting Infoblox Logs")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("test case 13 passed")
        sleep(5)
        print("Test Case 13 Execution Completed")


    @pytest.mark.run(order=14)
    def test_14_incorrect_login_credentials_super_user(self):
	logging.info("get reference value of GRID for super-user")
	command = ('curl -k1 -u testusr1:infoblox1 -H "Content-Type:application/json" -X GET https://'+config.grid_vip+'/wapi/v'+config.wapi_version+'/grid')
        output = os.popen(command).read()
        print(output)
        if "Authorization Required" or "401 Unauthorized" in output:
            assert True
        else:
            assert False
	print("\nTest Case 14 Execution Completed")

    @pytest.mark.run(order=15)
    def test_15_stop_infoblox_Logs(self):
        sleep(60)
        logging.info("Stopping Infoblox Logs")
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        print("Test Case 15 Execution Completed")

    @pytest.mark.run(order=16)
    def test_16_validate_snmp_traps_mail_notification(self):
        logging.info("Validating SNMP traps and notifications for super-user")
        LookFor="one_send_snmp_trap"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test Case 16 Execution Failed")
            assert False
        else:
            logging.info("Test Case 16 Execution Completed")
            assert True

    @pytest.mark.run(order=17)
    def test_17_validate_mail_notification(self):
        logging.info("Validating mail notifications for super-user")
        LookFor="one_send_snmp_trap_email_with_ack"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test Case 17 Execution Failed")
            assert False
        else:
            logging.info("Test Case 17 Execution Completed")
            assert True


    @pytest.mark.run(order=18)
    def test_18_disabling_login_grid_level(self):
        ref1=get_reference_value_grid()
        logging.info ("Enabling concurrent login for grid level")
        data={"security_setting":{"disable_concurrent_login" : False}}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
        logging.info(response)
        logging.info("============================")
        settings=get_security_settings()
        logging.info (settings)
        condition=settings['security_setting']['disable_concurrent_login']
        if (condition==(data['security_setting']['disable_concurrent_login'])):
            assert True
            logging.info("Test case 18 Passed for disabling Concurrent Login at grid level")
        else:
            logging.info("Test case 18 Failed for disabling Concurrent Login at grid level")
	    assert False

    @pytest.mark.run(order=19)
    def test_19_cleanup(self):
        get_ref = ib_NIOS.wapi_request("GET",object_type="adminuser?name=testusr1")
        ref1 = json.loads(get_ref)[0]['_ref']
	response = ib_NIOS.wapi_request("DELETE",ref=ref1,object_type="adminuser")
	logging.info(response)
	print(response)
	get_ref1 = ib_NIOS.wapi_request("GET",object_type="admingroup?name=test1")
	ref2 = json.loads(get_ref1)[0]['_ref']
	response = ib_NIOS.wapi_request("DELETE",ref=ref2,object_type="admingroup")
        logging.info(response)
        print(response)
	
	data1 = {"email_setting": {"enabled": False,"port_number": 25},"dns_resolver_setting": {"resolvers": []},"trap_notifications": [{"enable_email": False,"enable_trap": False,"trap_type": "Login"},{"enable_email": False,"enable_trap": False,"trap_type": "Clear"},{"enable_email": False,"enable_trap": False,"trap_type": "Reporting"}]}

	grid_ref = get_reference_value_grid()
	response = ib_NIOS.wapi_request('PUT',ref=grid_ref,fields=json.dumps(data1),grid_vip=config.grid_vip)
        logging.info(response)
        print(response)
	print("Test case 19 Execution completed")


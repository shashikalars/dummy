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

def get_security_settings():
    ref1=get_reference_value_grid()
    logging.info("get security settings for GRID")
    get_ref = ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=security_setting")
    logging.info(get_ref)
    res = json.loads(get_ref)
    return res

def super_user_check(ref1):
    ref2=ref1
    #logging.info("get reference value for GROUP level")
    #get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup")
    #logging.info(get_ref)
    #res = json.loads(get_ref)
    #ref2=json.loads(get_ref)[0]['_ref']
    logging.info("get value for super user or not")
    get_ref = ib_NIOS.wapi_request('GET', object_type=ref2+"?_return_fields=superuser")
    logging.info(get_ref)
    res = json.loads(get_ref)
    return res


def get_reference_value_admin_group(ref1):
    ref2=ref1
    #logging.info("get reference value for GROUP level")
    #get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup")
    #logging.info(get_ref)
    #res = json.loads(get_ref)
    #ref2=json.loads(get_ref)[0]['_ref']
    #object_type=ref2+"?_return_fields=disable_concurrent_login"
    get_ref = ib_NIOS.wapi_request('GET', object_type=ref2+"?_return_fields=disable_concurrent_login")
    logging.info(get_ref)
    res = json.loads(get_ref)
    ref1 = json.loads(get_ref)['disable_concurrent_login']
    logging.info ("*********************************************************************************",ref1)
    return ref1

class Network(unittest.TestCase):
    #logging.basicConfig(filename='example.log', filemode='w', level=logging.DEBUG)
    @pytest.mark.run(order=1)
    def test_01_create_super_user_group(self):
        logging.info("Creating User Group for testing concurrent login features ")
        group={"name":"test1","superuser":True}
        get_ref_group = ib_NIOS.wapi_request('POST',object_type="admingroup", fields=json.dumps(group))
        logging.info(get_ref_group)
        res_group = json.loads(get_ref_group)
        user={"name":"testusr1","password":"infobox","admin_groups":["test1"]}
        get_ref = ib_NIOS.wapi_request('POST',object_type="adminuser", fields=json.dumps(user))
        logging.info (get_ref)
        logging.info("Creating User Group for testing concurrent login features ")
        group1={"name":"test2","superuser":False}
        get_ref_group1 = ib_NIOS.wapi_request('POST',object_type="admingroup", fields=json.dumps(group1))
        logging.info(get_ref_group1)
        res_group1 = json.loads(get_ref_group1)
        user1={"name":"testusr2","password":"infobox","admin_groups":["test2"]}
        get_ref1 = ib_NIOS.wapi_request('POST',object_type="adminuser", fields=json.dumps(user1))
        logging.info(get_ref1)
        res1 = json.loads(get_ref1)
        logging.info (res1)


    @pytest.mark.run(order=2)
    def test_02_disabling_login_grid_level(self):
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
            logging.info("Test case 1 Passed for disabling Concurrent Login at grid level")
        else:
            logging.info("Test case 1 Failed for disabling Concurrent Login at grid level")

    @pytest.mark.run(order=3)
    def test_03_enabling_login_grid_level(self):
        ref1 = get_reference_value_grid()
        logging.info ("Disabling concurrent login at grid level")
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
            logging.info("Test case 2 Passed for disabling Concurrent Login at group level ")
        else:
            logging.info("Test case 2 Failed for disabling Concurrent Login at group level")

    @pytest.mark.run(order=4)
    def test_04_enabling_login_group_level(self):
        data = []
        logging.info("get reference value for GROUP level")
        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup")
        logging.info(get_ref)
        res = json.loads(get_ref)
        logging.info ("----------------------Groups where conditions will be applied------------------------------------------")
        time.sleep(5)
        for i in res:
            if (i['name'] not in ('splunk-reporting-group', 'cloud-api-only')):  # it gets data /reference other than splunk and clou-api
                data.append(i)
        logging.info (">***********************",data)
        for i in data:
            ref1=i['_ref']
            logging.info ("reference value for group is:",ref1)
            result=super_user_check(ref1)
            logging.info ("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^",result)
            if (result['superuser']!= False):
                data = {"use_disable_concurrent_login":True, "disable_concurrent_login":True}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data), grid_vip=config.grid_vip)
                time.sleep(5)
                logging.info(response)
                logging.info("=========================================================================")
                condition=get_reference_value_admin_group(ref1) #condition is to check what you have passed in data and what has updated after passing put command
                logging.info ("#######################################",condition)
                if (condition == (data['disable_concurrent_login'])):
                    assert True
                    logging.info("Test case 3 Passed for disabling Concurrent Login at group level ")
                else:
                    logging.info("Test case 3 Failed for disabling Concurrent Login at group level")

    @pytest.mark.run(order=5)
    def test_05_enabling_login_group_level1(self):
        data = []
        logging.info("get reference value for GROUP level")
        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup")
        logging.info(get_ref)
        res = json.loads(get_ref)
        logging.info ("----------------------Groups where conditions will be applied------------------------------------------")
        time.sleep(5)
        for i in res:
            if (i['name'] not in ('splunk-reporting-group', 'cloud-api-only')):  # it gets data /reference other than splunk and clou-api
                data.append(i)
        logging.info (">***********************",data)
        for i in data:
            ref1=i['_ref']
            logging.info ("reference value for group is:",ref1)
            result=super_user_check(ref1)
            logging.info ("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^",result)
            if (result['superuser']!= False):
                data = {"use_disable_concurrent_login":True, "disable_concurrent_login":False}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data), grid_vip=config.grid_vip)
                time.sleep(5)
                logging.info(response)
                logging.info("=========================================================================")
                condition=get_reference_value_admin_group(ref1) #condition is to check what you have passed in data and what has updated after passing put command
                logging.info ("#######################################",condition)
                if (condition == (data['disable_concurrent_login'])):
                    assert True
                    logging.info("Test case 4 Passed for disabling Concurrent Login at group level ")
                else:
                    logging.info("Test case 4 Failed for disabling Concurrent Login at group level")

    @pytest.mark.run(order=6)
    def test_06_enabling_login_group_level2(self):
        data = []
        logging.info("get reference value for GROUP level")
        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup")
        logging.info(get_ref)
        res = json.loads(get_ref)
        logging.info ("----------------------Groups where conditions will be applied------------------------------------------")
        time.sleep(5)
        for i in res:
            if (i['name'] not in ('splunk-reporting-group', 'cloud-api-only')):  # it gets data /reference other than splunk and clou-api
                data.append(i)
        logging.info (">***********************",data)
        for i in data:
            ref1=i['_ref']
            logging.info ("reference value for group is:",ref1)
            result=super_user_check(ref1)
            logging.info ("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^",result)
            if (result['superuser']!= False):
                data = {"use_disable_concurrent_login":False, "disable_concurrent_login":True}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data), grid_vip=config.grid_vip)
                time.sleep(5)
                logging.info(response)
                logging.info("=========================================================================")
                condition=get_reference_value_admin_group(ref1) #condition is to check what you have passed in data and what has updated after passing put command
                logging.info ("#######################################",condition)
                if (condition == (data['disable_concurrent_login'])):
                    assert True
                    logging.info("Test case 5 Passed for disabling Concurrent Login at group level ")
                else:
                    logging.info("Test case 5 Failed for disabling Concurrent Login at group level")

    @pytest.mark.run(order=7)
    def test_07_enabling_login_group_level3(self):
        data = []
        logging.info("get reference value for GROUP level")
        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup")
        logging.info(get_ref)
        res = json.loads(get_ref)
        logging.info ("----------------------Groups where conditions will be applied------------------------------------------")
        time.sleep(5)
        for i in res:
            if (i['name'] not in ('splunk-reporting-group', 'cloud-api-only')):  # it gets data /reference other than splunk and clou-api
                data.append(i)
        logging.info (">***********************",data)
        for i in data:
            ref1=i['_ref']
            logging.info ("reference value for group is:",ref1)
            result=super_user_check(ref1)
            logging.info ("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^",result)
            if (result['superuser']!= False):
                data = {"use_disable_concurrent_login":False, "disable_concurrent_login":False}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data), grid_vip=config.grid_vip)
                time.sleep(5)
                logging.info(response)
                logging.info("=========================================================================")
                condition=get_reference_value_admin_group(ref1) #condition is to check what you have passed in data and what has updated after passing put command
                logging.info ("#######################################",condition)
                logging.info ("+++++++++++++++++++++++++++++++",(data['disable_concurrent_login']))
                if (condition == (data['disable_concurrent_login'])):
                    assert True
                    logging.info("Test case 6 Passed for disabling Concurrent Login at group level ")
                else:
                    logging.info("Test case 6 Failed for disabling Concurrent Login at group level")




    @pytest.mark.run(order=8)
    def test_08_non_super_user_enabling(self):
        data = []
        logging.info("get reference value for GROUP level")
        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup")
        logging.info(get_ref)
        res = json.loads(get_ref)
        logging.info ("----------------------Groups where conditions will be applied------------------------------------------")
        time.sleep(5)
        for i in res:
            if (i['name'] not in ('splunk-reporting-group', 'cloud-api-only','admin-group')):  # it gets data /reference other than splunk and clou-api
                data.append(i)
        logging.info (">***********************",data)
        for i in data:
            ref1=i['_ref']
            logging.info ("reference value for group is:",ref1)
            result=super_user_check(ref1)
            logging.info ("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^",result)
            if (result['superuser']== False):
                data = {"use_disable_concurrent_login":True, "disable_concurrent_login":True}
                logging.info (data)
		try:
                	response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data), grid_vip=config.grid_vip,user="testusr2",password="infoblox")
		except Exception as error:
			assert True
			logging.info ("Non Super User have no permissions to execute command")

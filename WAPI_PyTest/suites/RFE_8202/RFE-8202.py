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

def change_date(no_of_days):
    ssh="ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@"+config.grid_vip +" 'date -s \"+%d days\"'"%(no_of_days)
    print ssh
    logging.info(ssh)
    date_change=os.popen(ssh).readline()
    print date_change
    logging.info(date_change)

def get_reference_value_grid():
    logging.info("get reference value for GRID")
    get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
    logging.info(get_ref)
    ref1 = json.loads(get_ref)[0]['_ref']
    print("++++++++++++++++++++++",ref1)
    logging.info (ref1)
    return ref1

def get_reference_value_grid_negative():
    logging.info("get reference value for GRID")
    get_ref = ib_NIOS.wapi_request('GET',object_type="grid",user="admin",password="infoblox1")
    logging.info(get_ref)
    ref1 = json.loads(get_ref)[0]['_ref']
    print("++++++++++++++++++++++",ref1)
    logging.info (ref1)
    return ref1

def get_reference_value_grid_superuser():
    logging.info("get reference value for GRID")
    get_ref = ib_NIOS.wapi_request('GET',object_type="grid",user="new",password="infoblox")
    logging.info(get_ref)
    ref1 = json.loads(get_ref)[0]['_ref']
    print("++++++++++++++++++++++",ref1)
    logging.info (ref1)
    return ref1

def get_password_settings():
    ref1=get_reference_value_grid()
    print("////////////////",ref1)
    logging.info("Get password settings for GRID")
    get_ref = ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=password_setting")
    logging.info(get_ref)
    res = json.loads(get_ref)
    return res

def super_user_check():
    logging.info("get reference value for GROUP level")
    get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup")
    logging.info(get_ref)
    ref2=json.loads(get_ref)[0]['_ref']
    logging.info("get value for super user or not")
    get_ref = ib_NIOS.wapi_request('GET', object_type=ref2+"?_return_fields=superuser")
    logging.info(get_ref)
    res = json.loads(get_ref)

class Network(unittest.TestCase):
    logging.basicConfig(filename='example.log', filemode='w', level=logging.DEBUG)

    @pytest.mark.run(order=1)
    def test_01_disabling_password_history(self):
        ref1=get_reference_value_grid()
        logging.info ("Disabling Password History")
        data={"password_setting":{"history_enable" : False}}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
        print("&&&&&&&&&&&&&&&&&&&&&&&",response)
        logging.info(response)
        logging.info("============================")
        settings=get_password_settings()
        logging.info(settings)
        condition=settings['password_setting']['history_enable']
        if (condition==(data['password_setting']['history_enable'])):
            logging.info("Test case 1 Passed for disabling password history")
            assert True
        else:
            logging.info("Test case 1 Failed for disabling password history")
            assert False


    @pytest.mark.run(order=2)
    def test_02_enabling_password_history(self):
        ref1=get_reference_value_grid()
        logging.info ("Enabling Password History")
        data={"password_setting":{"history_enable" : True}}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
        print("#######################",response)
        logging.info(response)
        logging.info("============================")
        settings=get_password_settings()
        logging.info(settings)
        #print("@!@#$%^$%^&*",settings)
        logging.info ("Status after passing True value : ", settings)
        condition=settings['password_setting']['history_enable']
        #logging.info("***********Condition after passing value*************",condition)
        #logging.info ("**********condition passsed in data*************",data['password_setting']['history_enable'])
        if (condition==(data['password_setting']['history_enable'])):
            logging.info("Test case 1 Passed for enabling password history")
            print("Test case 1 Passed for enabling password history")
            assert True
        else:
            logging.info("Test case 1 Failed for enabling password history")
            print("Test case 1 Failed for enabling password history")
            assert False


    @pytest.mark.run(order=3)
    def test_03_disable_minimum_password_age(self):
        ref1=get_reference_value_grid()
        logging.info ("Disabling Minimum Password Age")
        data={"password_setting":{"min_password_age": 0}}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
        print("@@@@@@@@@@@@@@@@@@@@@@@@",response)
        logging.info(response)
        logging.info("============================")
        settings=get_password_settings()
        logging.info(settings)
        condition=settings['password_setting']['min_password_age']
        if (condition==(data['password_setting']['min_password_age'])):
            logging.info("Test case 1 Passed for disabling Minimum Password Age")
            assert True
        else:
            logging.info("Test case 1 Failed for disabling Minimum Password Age")
            assert False


    @pytest.mark.run(order=4)
    def test_04_enable_minimum_password_age(self):
        ref1=get_reference_value_grid()
        logging.info ("Enabling Minimum Password Age")
        data={"password_setting":{"min_password_age": 3,"expire_enable": True,"expire_days": 7,"reminder_days": 2}}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
        print("@@@@@@@@@@@@@@@@@@@@@@@@",response)
        logging.info(response)
        logging.info("============================")
        settings=get_password_settings()
        logging.info(settings)
        condition=settings['password_setting']['min_password_age']
        if (condition==(data['password_setting']['min_password_age'])):
            logging.info("Test case 1 Passed for enabling Minimum Password Age")
            assert True
        else:
            logging.info("Test case 1 Failed for enabling Minimum Password Age")
            assert False

    @pytest.mark.run(order=5)
    def test_05_enable_minimum_password_age_negative(self):
        ref1=get_reference_value_grid()
        logging.info ("Enabling Minimum Password Age")
        data={"password_setting":{"min_password_age": 5,"expire_days":4}}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
        logging.info("============================")
        if (response[0]==400):
            print("Minimum password age must be less than password expiry interval")
            assert True
        else:
            print("Minimum password age value is entered successfully")
            assert False


    @pytest.mark.run(order=6)
    def test_06_enable_minimum_password_age_negative_two(self):
        ref1=get_reference_value_grid()
        logging.info ("Enabling Minimum Password Age")
        values = [10000,20000]
        for i in values:
             data={"password_setting":{"min_password_age": i}}
             response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
             logging.info("============================")
             if (response[0]==400):
                 print("Minimum password age must be between 0 to 9998")
                 assert True
             else:
                 print("Minimum password age value is entered successfully")
                 assert False


    @pytest.mark.run(order=7)
    def test_07_enable_minimum_password_age_negative_three(self):
        ref1=get_reference_value_grid()
        logging.info ("Enabling Minimum Password Age & check validation")
        values = ["abc"," 123"]
        for i in values:
             data={"password_setting":{"min_password_age": i}}
             response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
             logging.info("============================")
             if (response[0]==400):
                 print("Minimum password age should not have any characters or spaces")
                 assert True
             else:
                 print("Minimum password age value is entered successfully")
		 assert False


    @pytest.mark.run(order=8)
    def test_08_disable_force_password_change(self):
        ref1=get_reference_value_grid()
        logging.info ("Disabling Force Password Change at Next Login")
        data={"password_setting":{"force_reset_enable":False}}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
        print("$$$$$$$$$$$$$$$$$$$$$",response)
        logging.info(response)
        logging.info("============================")
        settings=get_password_settings()
        logging.info(settings)
        condition=settings['password_setting']['force_reset_enable']
        if (condition==(data['password_setting']['force_reset_enable'])):
            logging.info("Test case 1 Passed for disabling Force Password Change at Next Login")
            assert True
        else:
            logging.info("Test case 1 Failed for disabling Force Password Change at Next Login")
            assert False


    @pytest.mark.run(order=9)
    def test_09_create_user_group(self):
        logging.info("Creating User Group for testing password history features")
        group={"name":"non-super-user","superuser":False}
        get_ref_group = ib_NIOS.wapi_request('POST',object_type="admingroup", fields=json.dumps(group))
        if (get_ref_group[0] == 400):
            print("Duplicate object \'non-super-user\' of type \'admin_group\' already exists in the database")
            assert True
        else:
            print("Group \'non-super-user\' has been created")
        #logging.info(get_ref_group)
        #print("@@@@@####!!!!!",get_ref_group)
        #res_group = json.loads(get_ref_group)
        user={"name":"manoj","password":"manoj","admin_groups":["non-super-user"]}
        get_ref = ib_NIOS.wapi_request('POST',object_type="adminuser", fields=json.dumps(user))
        if (get_ref[0] == 400):
            print("Duplicate object \'manoj\' of type \'adminuser\' already exists in the database")
            assert True
        else:
            print("User \'manoj\' has been created")
        #logging.info (get_ref)
        #res = json.loads(get_ref)
        #logging.info (res)
        #print("######@@@@@@@",res)


    @pytest.mark.run(order=10)
    def test_10_login_user_first_time(self):
        logging.info("Create super-user group for testing password history features")
        group = {"name":"super-user","superuser":True}
        get_ref_group = ib_NIOS.wapi_request('POST',object_type="admingroup", fields=json.dumps(group))
        if (get_ref_group[0] == 400):
            print("Duplicate object \'super-user\' of type \'admin_group\' already exists in the database")
            assert True
        else:
            print("Group \'super-user\' has been created")
        logging.info(get_ref_group)
        #print("@@@@@####!!!!!",get_ref_group)
        user = {"name":"new","password":"infoblox","admin_groups":["super-user"]}
        get_ref = ib_NIOS.wapi_request('POST',object_type="adminuser", fields=json.dumps(user))
        if (get_ref[0] == 400):
            print("Duplicate object \'new' of type \'super-user\' already exists in the database")

        else:
            print("User \'new\' has been created")
        logging.info (get_ref)
        res = json.loads(get_ref)
        logging.info (res)
        print("######@@@@@@@",res)
        data = {"password_setting":{"min_password_age":3,"num_passwords_saved":5,"expire_days":4}}
        get_ref = get_reference_value_grid_superuser()
        response = ib_NIOS.wapi_request('PUT',ref=get_ref,fields=json.dumps(data),user="new",password="infoblox",grid_vip=config.grid_vip)
        res=json.loads(response)
        logging.info(res)


    @pytest.mark.run(order=11)
    def test_11_reuse_password_change_superuser(self):
        logging.info("Try re-using older passwords through super-user that should allow when older passwords are expired")
        data = {"password_setting":{"history_enable":True, "min_password_age":0, "num_passwords_saved":3}}
        ref2 = get_reference_value_grid()
        response = ib_NIOS.wapi_request('PUT',ref=ref2,grid_vip=config.grid_vip,fields=json.dumps(data))
        logging.info(response)
        print("&&&&&&&&&&&&&",response)
        get_ref_1 = ib_NIOS.wapi_request("GET",object_type="adminuser",user="new",password="infoblox")
        ref_1=json.loads(get_ref_1)[-1]['_ref']
        print("ref",ref_1)
        user = {"name":"new","password":"infoblox1","admin_groups":["super-user"]}
        password_res = ib_NIOS.wapi_request("PUT",ref=ref_1,fields=json.dumps(user),grid_vip=config.grid_vip,user="new",password="infoblox")
        logging.info(password_res)
        print("First time password change")
        get_ref_2 = ib_NIOS.wapi_request("GET",object_type="adminuser",user="new",password="infoblox1")
        ref_2=json.loads(get_ref_2)[-1]['_ref']
        user = {"name":"new","password":"infoblox2","admin_groups":["super-user"]}
        password_res = ib_NIOS.wapi_request("PUT",ref=ref_2,fields=json.dumps(user),grid_vip=config.grid_vip,user="new",password="infoblox1")
        logging.info(password_res)
        print("Second time password change")
        get_ref_3 = ib_NIOS.wapi_request("GET",object_type="adminuser",user="new",password="infoblox2")
        ref_3=json.loads(get_ref_3)[-1]['_ref']
        user = {"name":"new","password":"infoblox3","admin_groups":["super-user"]}
        password_res = ib_NIOS.wapi_request("PUT",ref=ref_3,fields=json.dumps(user),grid_vip=config.grid_vip,user="new",password="infoblox2")
        logging.info(password_res)
        print("Third time password change",password_res)
        get_ref_4 = ib_NIOS.wapi_request("GET",object_type="adminuser",user="new",password="infoblox3")
        ref_4=json.loads(get_ref_4)[-1]['_ref']
        user = {"name":"new","password":"infoblox4","admin_groups":["super-user"]}
        password_res = ib_NIOS.wapi_request("PUT",ref=ref_4,fields=json.dumps(user),grid_vip=config.grid_vip,user="new",password="infoblox3")
        logging.info(password_res)
        get_ref_5 = ib_NIOS.wapi_request("GET",object_type="adminuser",user="new",password="infoblox4")
        ref_5=json.loads(get_ref_5)[-1]['_ref']
        user = {"name":"new","password":"infoblox1","admin_groups":["super-user"]}
        password_res = ib_NIOS.wapi_request("PUT",ref=ref_5,fields=json.dumps(user),grid_vip=config.grid_vip,user="new",password="infoblox4")
        logging.info(password_res)
        if (password_res[0] != 400):
            print("Password is modified with older password for Super-User")
            assert True
        else:
            print("Cannot reuse older passwords")
            assert False

    @pytest.mark.run(order=12)
    def test_12_change_superuser_password(self):
        data = {"password_setting":{"history_enable":False}}
        get_ref = ib_NIOS.wapi_request('GET',object_type="grid",user="new",password="infoblox1")
        ref = json.loads(get_ref)[0]['_ref']
        #print("++++++++++++++++++++++",ref1)
        logging.info (ref)
        response = ib_NIOS.wapi_request('PUT',ref=ref,grid_vip=config.grid_vip,fields=json.dumps(data),user="new",password="infoblox1")
        logging.info(response)
        print("&&&&&&&&&&&&&",response)
        get_ref_1 = ib_NIOS.wapi_request("GET",object_type="adminuser",user="new",password="infoblox1")
        ref_1 = json.loads(get_ref_1)[-1]['_ref']
        user = {"name":"new","password":"infoblox","admin_groups":["super-user"]}
        password_res = ib_NIOS.wapi_request("PUT", ref=ref_1,fields=json.dumps(user),grid_vip=config.grid_vip,user="new",password="infoblox1")
        logging.info(password_res)
        if (password_res[0] != 400):
            print("Password is modified to older password infoblox")
            assert True
        else:
            print("Cannot modify the password")
            assert False

    @pytest.mark.run(order=13)
    def test_13_reuse_password_change_superuser_negative(self):
        logging.info("Try re-using older passwords through super-user that should not allow when passwords are still in database")
        data = {"password_setting":{"history_enable":True, "min_password_age":0, "num_passwords_saved":3}}
        ref2 = get_reference_value_grid()
        response = ib_NIOS.wapi_request('PUT',ref=ref2,grid_vip=config.grid_vip,fields=json.dumps(data))
        logging.info(response)
        print("&&&&&&&&&&&&&",response)
        get_ref_1 = ib_NIOS.wapi_request("GET",object_type="adminuser",user="new",password="infoblox")
        ref_1=json.loads(get_ref_1)[-1]['_ref']
        user = {"name":"new","password":"infoblox1","admin_groups":["super-user"]}
        password_res = ib_NIOS.wapi_request("PUT", ref=ref_1,fields=json.dumps(user),grid_vip=config.grid_vip,user="new",password="infoblox")
        logging.info(password_res)
        print("$$$$$$$###########",password_res)
        get_ref_2 = ib_NIOS.wapi_request("GET",object_type="adminuser",user="new",password="infoblox1")
        ref_2=json.loads(get_ref_2)[-1]['_ref']
        user = {"name":"new","password":"infoblox2","admin_groups":["super-user"]}
        password_res = ib_NIOS.wapi_request("PUT", ref=ref_2,fields=json.dumps(user),grid_vip=config.grid_vip,user="new",password="infoblox1")
        logging.info(password_res)
        print("$$$$$$$###########",password_res)
        get_ref_3 = ib_NIOS.wapi_request("GET",object_type="adminuser",user="new",password="infoblox2")
        ref_3=json.loads(get_ref_3)[-1]['_ref']
        user = {"name":"new","password":"infoblox3","admin_groups":["super-user"]}
        password_res = ib_NIOS.wapi_request("PUT", ref=ref_3,fields=json.dumps(user),grid_vip=config.grid_vip,user="new",password="infoblox2")
        logging.info(password_res)
        print("$$$$$$$###########",password_res)
        get_ref_4 = ib_NIOS.wapi_request("GET",object_type="adminuser",user="new",password="infoblox3")
        ref_4=json.loads(get_ref_4)[-1]['_ref']
        user = {"name":"new","password":"infoblox2","admin_groups":["super-user"]}
        password_res = ib_NIOS.wapi_request("PUT", ref=ref_4,fields=json.dumps(user),grid_vip=config.grid_vip,user="new",password="infoblox3")
        logging.info(password_res)
        #print("$$$$$$$###########",password_res)
        if (password_res[0] == 400):
            print("Cannot reuse older passwords")
            assert True
        else:
            print("Password is modified")
	    assert False


    @pytest.mark.run(order=14)
    def test_14_login_user_modify_password(self):
        logging.info("Change password through super-user login")
        data = {"password_setting":{"history_enable":False,"min_password_age":0}}
        get_ref=ib_NIOS.wapi_request("GET",object_type="adminuser")
        ref1=json.loads(get_ref)[0]['_ref']
        ref2=get_reference_value_grid()
        response=ib_NIOS.wapi_request('PUT',ref=ref2,grid_vip=config.grid_vip,fields=json.dumps(data))
        logging.info(response)
        print("&&&&&&&&&&&&&",response)
        user = {"name":"admin","password":"infoblox1","admin_groups":["admin-group"]}
        password_res = ib_NIOS.wapi_request("PUT", ref=ref1,fields=json.dumps(user))
        if (password_res[0] == 400):
            print("Can only change the password after 3 days")
            assert False
        else:
            print("Password has been modified")
            assert True
        logging.info(password_res)
        print("$$$$$$$###########",password_res)
        user1 = {"name":"admin","password":"infoblox","admin_groups":["admin-group"]}
        get_ref_1=ib_NIOS.wapi_request("GET",object_type="adminuser",user="admin",password="infoblox1")
        ref3=json.loads(get_ref_1)[0]['_ref']
        password_res_1 = ib_NIOS.wapi_request("PUT", ref=ref3,fields=json.dumps(user1),user="admin",password="infoblox1")
        #if (password_res_1[0] == 400):
        #    print("Can only change the password after 3 days")
        #    assert False
        #else:
        #    print("Password has been modified")
        #    assert True
        print("Password has been modified")
        logging.info(password_res_1)
        print("*************",password_res_1)


    @pytest.mark.run(order=15)
    def test_15_login_user_modify_password_negative(self):
        logging.info("Change password through super-user login")
        data = {"password_setting":{"min_password_age":3}}
        get_ref=ib_NIOS.wapi_request("GET",object_type="adminuser")
        ref1=json.loads(get_ref)[0]['_ref']
        ref2=get_reference_value_grid()
        response=ib_NIOS.wapi_request('PUT',ref=ref2,grid_vip=config.grid_vip,fields=json.dumps(data))
        logging.info(response)
        print("&&&&&&&&&&&&&",response)
        user = {"name":"admin","password":"infoblox1","admin_groups":["admin-group"]}
        password_res = ib_NIOS.wapi_request("PUT", ref=ref1,fields=json.dumps(user))
        if (password_res[0] == 400):
            print("Can only change the password after 3 days")
            assert True
        else:
            print("Password has been modified")
            assert False
        print("$$$$$$$###########",password_res)


    @pytest.mark.run(order=16)
    def test_16_reuse_password_change_admin(self):
        logging.info("Try re-using older passwords through admin that should allow when older passwords are expired")
        data = {"password_setting":{"history_enable":True, "min_password_age":0, "num_passwords_saved":3}}
        ref2 = get_reference_value_grid()
        response = ib_NIOS.wapi_request('PUT',ref=ref2,grid_vip=config.grid_vip,fields=json.dumps(data))
        logging.info(response)
        print("&&&&&&&&&&&&&",response)
        get_ref_1 = ib_NIOS.wapi_request("GET",object_type="adminuser")
        ref_1=json.loads(get_ref_1)[0]['_ref']
        user = {"name":"admin","password":"infoblox1","admin_groups":["admin-group"]}
        password_res = ib_NIOS.wapi_request("PUT", ref=ref_1,fields=json.dumps(user))
        logging.info(password_res)
        print("$$$$$$$###########",password_res)
        get_ref_2 = ib_NIOS.wapi_request("GET",object_type="adminuser",user="admin",password="infoblox1")
        ref_2=json.loads(get_ref_2)[0]['_ref']
        user = {"name":"admin","password":"infoblox2","admin_groups":["admin-group"]}
        password_res = ib_NIOS.wapi_request("PUT", ref=ref_2,fields=json.dumps(user),user="admin",password="infoblox1")
        logging.info(password_res)
        print("$$$$$$$###########",password_res)
        get_ref_3 = ib_NIOS.wapi_request("GET",object_type="adminuser",user="admin",password="infoblox2")
        ref_3=json.loads(get_ref_3)[0]['_ref']
        user = {"name":"admin","password":"infoblox3","admin_groups":["admin-group"]}
        password_res = ib_NIOS.wapi_request("PUT", ref=ref_3,fields=json.dumps(user),user="admin",password="infoblox2")
        logging.info(password_res)
        print("$$$$$$$###########",password_res)
        get_ref_4 = ib_NIOS.wapi_request("GET",object_type="adminuser",user="admin",password="infoblox3")
        ref_4=json.loads(get_ref_4)[0]['_ref']
        user = {"name":"admin","password":"infoblox4","admin_groups":["admin-group"]}
        password_res = ib_NIOS.wapi_request("PUT", ref=ref_4,fields=json.dumps(user),user="admin",password="infoblox3")
        logging.info(password_res)
        get_ref_5 = ib_NIOS.wapi_request("GET",object_type="adminuser",user="admin",password="infoblox4")
        ref_5=json.loads(get_ref_5)[0]['_ref']
        user = {"name":"admin","password":"infoblox1","admin_groups":["admin-group"]}
        password_res = ib_NIOS.wapi_request("PUT", ref=ref_5,fields=json.dumps(user),user="admin",password="infoblox4")
        logging.info(password_res)
        if (password_res[0] != 400):
            print("Password is modified with older password which was already expired when it is cleared out of database")
            assert True
        else:
            print("Cannot reuse older passwords")
            assert False


    @pytest.mark.run(order=17)
    def test_17_change_admin_password(self):
        data = {"password_setting":{"history_enable":False}}
        get_ref = ib_NIOS.wapi_request('GET',object_type="grid",user="admin",password="infoblox1")
        ref = json.loads(get_ref)[0]['_ref']
        #print("++++++++++++++++++++++",ref1)
        logging.info (ref)
        response = ib_NIOS.wapi_request('PUT',ref=ref,grid_vip=config.grid_vip,fields=json.dumps(data),user="admin",password="infoblox1")
        logging.info(response)
        print("&&&&&&&&&&&&&",response)
        get_ref_1 = ib_NIOS.wapi_request("GET",object_type="adminuser",user="admin",password="infoblox1")
        ref_1 = json.loads(get_ref_1)[0]['_ref']
        user = {"name":"admin","password":"infoblox","admin_groups":["admin-group"]}
        password_res = ib_NIOS.wapi_request("PUT", ref=ref_1,fields=json.dumps(user),user="admin",password="infoblox1")
        logging.info(password_res)
        if (password_res[0] != 400):
            print("Password is modified to older password infoblox")
            assert True
        else:
            print("Cannot modify the password")
            assert False

    @pytest.mark.run(order=18)
    def test_18_reuse_password_change_negative_admin(self):
        logging.info("Try re-using older passwords through admin that should not allow when passwords are still in history")
        data = {"password_setting":{"history_enable":True, "min_password_age":0, "num_passwords_saved":3}}
        ref2 = get_reference_value_grid()
        response = ib_NIOS.wapi_request('PUT',ref=ref2,grid_vip=config.grid_vip,fields=json.dumps(data))
        logging.info(response)
        print("&&&&&&&&&&&&&",response)
        get_ref_1 = ib_NIOS.wapi_request("GET",object_type="adminuser")
        ref_1=json.loads(get_ref_1)[0]['_ref']
        user = {"name":"admin","password":"infoblox1","admin_groups":["admin-group"]}
        password_res = ib_NIOS.wapi_request("PUT", ref=ref_1,fields=json.dumps(user))
        logging.info(password_res)
        print("$$$$$$$###########",password_res)
        get_ref_2 = ib_NIOS.wapi_request("GET",object_type="adminuser",user="admin",password="infoblox1")
        ref_2=json.loads(get_ref_2)[0]['_ref']
        user = {"name":"admin","password":"infoblox2","admin_groups":["admin-group"]}
        password_res = ib_NIOS.wapi_request("PUT", ref=ref_2,fields=json.dumps(user),user="admin",password="infoblox1")
        logging.info(password_res)
        print("$$$$$$$###########",password_res)
        get_ref_3 = ib_NIOS.wapi_request("GET",object_type="adminuser",user="admin",password="infoblox2")
        ref_3=json.loads(get_ref_3)[0]['_ref']
        user = {"name":"admin","password":"infoblox3","admin_groups":["admin-group"]}
        password_res = ib_NIOS.wapi_request("PUT", ref=ref_3,fields=json.dumps(user),user="admin",password="infoblox2")
        logging.info(password_res)
        print("$$$$$$$###########",password_res)
        get_ref_4 = ib_NIOS.wapi_request("GET",object_type="adminuser",user="admin",password="infoblox3")
        ref_4=json.loads(get_ref_4)[0]['_ref']
        user = {"name":"admin","password":"infoblox2","admin_groups":["admin-group"]}
        password_res = ib_NIOS.wapi_request("PUT", ref=ref_4,fields=json.dumps(user),user="admin",password="infoblox3")
        logging.info(password_res)
        if (password_res[0] == 400):
            print("Cannot reuse older passwords")
            assert True
        else:
            print("Password is modified")
	    assert False
    
    '''
    @pytest.mark.run(order=19)
    def test_19_change_date_password_admin(self):
        logging.info("Try changing the date for admin when minimum password age is one & it should allow when date is moved forward")
        data = {"password_setting":{"history_enable":False}}
        get_ref = ib_NIOS.wapi_request('GET',object_type="grid",user="admin",password="infoblox3")
        ref = json.loads(get_ref)[0]['_ref']
        logging.info (ref)
        response = ib_NIOS.wapi_request('PUT',ref=ref,grid_vip=config.grid_vip,fields=json.dumps(data),user="admin",password="infoblox3")
        logging.info(response)
        print("&&&&&&&&&&&&&",response)
        get_ref_1 = ib_NIOS.wapi_request("GET",object_type="adminuser",user="admin",password="infoblox3")
        ref_1 = json.loads(get_ref_1)[0]['_ref']
        user = {"name":"admin","password":"infoblox","admin_groups":["admin-group"]}
        password_res = ib_NIOS.wapi_request("PUT", ref=ref_1,fields=json.dumps(user),user="admin",password="infoblox3")
        print("Password reset to infoblox done successfully")
        data_1 = {"password_setting":{"history_enable":True, "min_password_age":1, "num_passwords_saved":3}} 
        ref2 = get_reference_value_grid()
        response = ib_NIOS.wapi_request('PUT',ref=ref2,grid_vip=config.grid_vip,fields=json.dumps(data_1))
        logging.info(response)
        print("&&&&&&&&&&&&&",response)
        change_date(1)
        get_ref_2 = ib_NIOS.wapi_request("GET",object_type="adminuser")
        ref_2 = json.loads(get_ref_2)[0]['_ref']
        user = {"name":"admin","password":"infoblox1","admin_groups":["admin-group"]}
        password = ib_NIOS.wapi_request("PUT", ref=ref_2,fields=json.dumps(user))
        logging.info(password)
        if (password[0] != 400):
            print("Password is successfully modified after 1 day")
            assert True
        else:
            print("Cannot modify the password")
            assert False
        '''



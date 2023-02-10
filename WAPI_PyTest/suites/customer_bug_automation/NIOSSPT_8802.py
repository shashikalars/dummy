##Setup requirement: SA grid with NIOS,Grid license

import re
import config
import pytest
import unittest
import logging
import subprocess
import os
import json
import ib_utils.ib_NIOS as ib_NIOS
import commands
import json, ast
import requests
from time import sleep as sleep
import pexpect
from paramiko import client
#from log_capture import log_action as log
#from log_validation import log_validation as logv
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as comm_util
import ast

global serv_ref

def display_msg(x):
    logging.info(x)
    print("")
    print(x)


class Network(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_101_add__nested_ad_service_group(self):
        global serv_ref
        display_msg("Creating an Authentication Server Group")
        data = {"name": "ad_test","ad_domain": "ad19187.com","nested_group_querying": True,"timeout": 5,"domain_controllers": [{"auth_port": 389,"disabled": False,"encryption": "NONE","fqdn_or_ip": "10.34.98.56","use_mgmt_port": False}]}
        response = ib_NIOS.wapi_request('POST',object_type="ad_auth_service",fields=json.dumps(data))       
        print(response)
        serv_ref = json.loads(response)
        response = str(response)
        if (re.search(r'already exists in the database',response)):
            assert False
        else:
            assert True
        display_msg("Authentication Server Group added")

    @pytest.mark.run(order=2)
    def test_102_add_admin_group(self): 
        data={"name":"group2","superuser":True}
        response = ib_NIOS.wapi_request('POST',object_type="admingroup", fields=json.dumps(data))
        print response
        display_msg("Group2 added successfully")      
        
        
    @pytest.mark.run(order=3)
    def test_103_configure_authentication_policy(self): 
        global serv_ref
        print (type(serv_ref))
	response = ib_NIOS.wapi_request('GET', object_type="authpolicy?_return_fields=admin_groups,auth_services")
        response=json.loads(response)
        auth_policy = response[0]['_ref'].encode('ascii')
        local_user = json.dumps(response[0]['auth_services'])
        local_user.encode('ascii')
        local_user=ast.literal_eval(local_user)
        local_user.append(serv_ref)
        print ("local_user : " ,local_user)
        print ("auth_policy :",auth_policy)
        data = {"admin_groups": ["group2"],"auth_services": local_user}
        print (":????????????????????????????????????",data)
        response = response = ib_NIOS.wapi_request('PUT', ref=auth_policy, fields=json.dumps(data))
        print response


    @pytest.mark.run(order=4)
    def test_104_login_with_parenthesis_user(self):
        display_msg("Try to login with the username: user1()")
        response = ib_NIOS.wapi_request('GET', object_type="member", user="user1()", password="Infoblox@123")
        print response
        response = str(response)
        if (re.search(r'401 Authorization Required',response)):
            assert False
        else:
            assert True

    @pytest.mark.run(order=5)
    def test_105_login_with_comma_user(self):
        display_msg("Try to login with the username: user2,")
        response = ib_NIOS.wapi_request('GET', object_type="member", user="user2_", password="Infoblox@123")
        print response
        response = str(response)
        if (re.search(r'401 Authorization Required',response)):
            assert False
        else:
            assert True


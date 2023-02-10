#!/usr/bin/env python
__author__ = "Manoj Kumar RG"
__email__  = "mgovarthanan@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Stand alone Grid Master                                               #
#  2. Licenses : DHPC, DNS, Grid, NIOS(IB_1415)                             #
#############################################################################

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
import time
import sys
import pexpect

class NIOSSPT_11055(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_001_create_radius_authentication_server_group(self):
	print("Testcase 1 started")
        logging.info("Creating radius service in authentication server group")
        data={
                "name": "radius",
                "servers": [
                    {
                        "acct_port": 1813,
                        "address": "10.120.20.49",
                        "auth_port": 1812,
                        "auth_type": "PAP",
                        "shared_secret": "testing123"
                    }
                ]
            }
        response = ib_NIOS.wapi_request('POST', object_type="radius:authservice",fields=json.dumps(data))
        print(response)
        logging.info(response)
        radiusref=response
        radiusref = json.loads(radiusref)
        print(radiusref)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
               assert False

        print("Test Case 01 Execution Completed")

    @pytest.mark.run(order=2)
    def test_002_create_super_user_group(self):
	print("Testcase 2 started")
        logging.info("Creating User Group for testing password history features")
        group={"name":"superuser","superuser":True}
        get_ref_group = ib_NIOS.wapi_request('POST',object_type="admingroup", fields=json.dumps(group))
        if (get_ref_group[0] == 400):
            print("Duplicate object \'superuser\' of type \'admin_group\' already exists in the database")
            assert True
        else:
            print("Group \'superuser\' has been created")
        user={"name":"shiva","password":"shiva","admin_groups":["superuser"]}
        get_ref = ib_NIOS.wapi_request('POST',object_type="adminuser", fields=json.dumps(user))
        if (get_ref[0] == 400):
            print("Duplicate object \'shiva\' of type \'adminuser\' already exists in the database")
            assert True
        else:
            print("User \'shiva\' has been created")
	print("Test Case 02 Execution Completed")

    @pytest.mark.run(order=3)
    def test_003_create_radius_authentication_policy(self):
	print("Testcase 3 started")	
        logging.info("Create authentication policy group to add remote authentication")
        logging.info("get authentication policy ref")
        res = ib_NIOS.wapi_request('GET',object_type='authpolicy')
        res = json.loads(res)
        print(res)
        auth_policy_ref=res[0][u'_ref']
        print(auth_policy_ref)
        logging.info("adding default group for authpolicy")
        data={"default_group": "superuser"}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=auth_policy_ref)
        print(response)
        logging.info("Get auth_service localuser reference")
        res = ib_NIOS.wapi_request('GET',object_type='authpolicy?_return_fields=auth_services')
        res = json.loads(res)
        print(res)
        localuser_ref=res[0][u'auth_services'][0]
        print(localuser_ref)
        logging.info("Get radius server reference")
        response = ib_NIOS.wapi_request('GET', object_type="radius:authservice")
        print(response)
        response = json.loads(response)
        radiusref=response[0][u'_ref']
        logging.info("Adding localuser and radius reference to auth_services")
        data={"auth_services":[radiusref,localuser_ref]}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=auth_policy_ref)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
               assert False
        print("Test Case 03 Execution Completed")

    @pytest.mark.run(order=4)
    def test_004_verify_radius_sshlogin(self):
        print("Testcase 4 started")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no shiva@'+config.grid_vip)
        child.expect ('password.*:')
        child.sendline ('hello')
        child.expect ('Infoblox >')
        child.sendline ('exit')
        assert True
	print("Test Case 04 Execution Completed")

    @pytest.mark.run(order=5)
    def test_005_verify_radius_gui_login(self):
        print("Testcase 5 started")
    	get_ref = ib_NIOS.wapi_request('GET',object_type="grid",user="shiva",password="hello")
    	logging.info(get_ref)
        print("#######################",get_ref)
        read  = re.search(r'200',get_ref)
        for read in response:
            assert True
        print("Test Case 05 Execution Completed")
	
    @pytest.mark.run(order=6)
    def test_006_change_usage_type(self):
	print("Testcase 6 started")
        res = ib_NIOS.wapi_request('GET',object_type='authpolicy')
        res = json.loads(res)
        ref1=res[0]['_ref']
	data = {"usage_type": "AUTH_ONLY"}
	response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 06 Execution Completed")

    @pytest.mark.run(order=7)
    def test_007_verify_sshlogin_radius_user(self):
        print("Testcase 7 started")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no shiva@'+config.grid_vip)
        child.expect ('password.*:')
        child.sendline ('hello')
        child.expect ('Infoblox >')
        child.sendline ('exit')
	#child.expect ('password.*:')
        #assert True
	print("Test Case 07 Execution Completed")

    @pytest.mark.run(order=8)
    def test_008_verify_gui_login_radius(self):
        print("Testcase 8 started")
        get_ref = ib_NIOS.wapi_request('GET',object_type="grid",user="shiva",password="hello")
        logging.info(get_ref)
        print("#######################",get_ref)
        read  = re.search(r'200',get_ref)
        for read in response:
            assert False
        print("Test Case 08 Execution Completed")
	
    @pytest.mark.run(order=9)
    def test_009_cleanup_data(self):
        logging.info("resetting default group for authpolicy")
        res = ib_NIOS.wapi_request('GET',object_type='authpolicy')
        res = json.loads(res)
        print(res)
        auth_policy_ref=res[0][u'_ref']
        print(auth_policy_ref)
        data={"default_group": "admingroup"}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=auth_policy_ref)
        print(response)
        res = ib_NIOS.wapi_request('GET',object_type='authpolicy')
        res = json.loads(res)
        print(res)
        auth_policy_ref=res[0][u'_ref']
        res = ib_NIOS.wapi_request('GET',object_type='authpolicy?_return_fields=auth_services')
        res = json.loads(res)
        print(res)
        localuser_ref=res[0][u'auth_services'][1]
        print(localuser_ref)
        logging.info("Removing radius server frm auth_services")
        data={"auth_services":[localuser_ref]}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=auth_policy_ref)
        print(response)
        res1 = ib_NIOS.wapi_request('GET', object_type="radius:authservice")
        print(res1)
        res1 = json.loads(res1)
        radiusref=res1[0][u'_ref']
	response = ib_NIOS.wapi_request('DELETE',ref=radiusref)
        print(response)
        res = ib_NIOS.wapi_request('GET',object_type='authpolicy')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data = {"usage_type": "FULL"}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
	res2 = ib_NIOS.wapi_request('GET', object_type="adminuser?name=shiva")
        print(res2)
        res2 = json.loads(res2)
        groupref=res2[0][u'_ref']
        response = ib_NIOS.wapi_request('DELETE',ref=groupref)
        print(response)
        res3 = ib_NIOS.wapi_request('GET', object_type="admingroup?name=superuser")
        print(res3)
        res3 = json.loads(res3)
        groupref=res3[0][u'_ref']
        response = ib_NIOS.wapi_request('DELETE',ref=groupref)
        print(response)
	print("Test Case 09 Execution Completed")




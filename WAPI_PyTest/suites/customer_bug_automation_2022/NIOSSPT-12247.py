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
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv

class Network(unittest.TestCase):
    logging.basicConfig(filename='niosspt_12247.log', filemode='w', level=logging.DEBUG)

    @pytest.mark.run(order=1)
    def test_001_create_ldap_authentication_server_group(self):
        
	logging.info("Creating ldap service in authentication server group")
        data={
                "name": "ldap",
		"ldap_user_attribute": "uid",
		"timeout": 5,
		"retries": 5,
		"recovery_interval": 30,
		"mode": "ORDERED_LIST",
		"search_scope": "SUBTREE",
                "servers": [
                    {
                        "port": 389,
                        "address": "10.197.38.101",
			"authentication_type": "ANONYMOUS",
			"base_dn": "dc=ldapserver,dc=local",
			"encryption": "NONE",
			"use_mgmt_port": False,
			"version": "V3",
			"disable": False
                    }
                ]
            }
        response = ib_NIOS.wapi_request('POST', object_type="ldap_auth_service",fields=json.dumps(data))
        print("%%%%%%%%%%%%%%%",response)
        logging.info(response)
        ldapref=response
        ldapref = json.loads(ldapref)
        print(ldapref)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
               assert False

        print("Test Case 001 Execution Completed")

    @pytest.mark.run(order=2)
    def test_002_create_tacacs_authentication_server_group(self):
        logging.info("Creating tacacs service in authentication server group")
        data={
                "name": "tacacs",
                "servers": [
                    {
                        "address": "10.197.38.101",
                        "shared_secret": "testing123"
                    }
                ]
            }
        response = ib_NIOS.wapi_request('POST', object_type="tacacsplus:authservice",fields=json.dumps(data))
        print(response)
        logging.info(response)
        tacacs_ref=response
        tacacs_ref = json.loads(tacacs_ref)
        print(tacacs_ref)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
               assert False

        print("Test Case 002 Execution Completed")

    @pytest.mark.run(order=3)
    def test_003_create_superuser_group(self):
        logging.info("Create a super-user group")
        data={"name":"infobloxgroup","superuser":True}
        response = ib_NIOS.wapi_request('POST',object_type="admingroup",fields=json.dumps(data))
        print("#######################",response)
        if (response[0] == 400):
            print("Duplicate object \'infobloxgroup\' of type \'admin_group\' already exists in the database")
            assert True
        else:
            print("Group \'infobloxgroup\' has been created")

	print("Test Case 003 Execution Completed")

    @pytest.mark.run(order=4)
    def test_004_configure_authentication_policy(self):
        logging.info("Configure authentication policy group to add remote authentication")
        res = ib_NIOS.wapi_request('GET',object_type='authpolicy?_return_fields=auth_services')
        res = json.loads(res)
        print(res)
        localuser_ref=res[0][u'auth_services'][0]
        print("$$$$$$$$$$$$$$$$$$",localuser_ref)

        logging.info("Get ldap server reference")
        response = ib_NIOS.wapi_request('GET', object_type="ldap_auth_service")
        print(response)
        response = json.loads(response)
        ldapref=response[0][u'_ref']
	print("$$$$$$$$$$$$$$$$$$",ldapref)

        logging.info("Get tacacs server reference")
        response = ib_NIOS.wapi_request('GET', object_type="tacacsplus:authservice")
        print(response)
        response = json.loads(response)
        tacacsref=response[0][u'_ref']
        print("$$$$$$$$$$$$$$$$$$",tacacsref)

        logging.info("Adding localuser ldap and tacacs reference to auth_services")
        logging.info("get authentication policy ref")
        res = ib_NIOS.wapi_request('GET',object_type='authpolicy')
        res = json.loads(res)
        print(res)
        auth_policy_ref=res[0][u'_ref']

        data={"auth_services":[localuser_ref,ldapref,tacacsref]}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=auth_policy_ref)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
               assert False
	print("Test Case 004 Execution Completed")

    @pytest.mark.run(order=5)
    def test_005_add_remote_group_auth_policy(self):
        logging.info("Add remote group under auth policy")

        logging.info("get authentication policy ref")
        res = ib_NIOS.wapi_request('GET',object_type='authpolicy')
        res = json.loads(res)
        print(res)
        auth_policy_ref=res[0][u'_ref']

	data={"admin_groups": ["infobloxgroup"]}
	response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=auth_policy_ref)
	print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
               assert False
        print("Test Case 005 Execution Completed")

    @pytest.mark.run(order=6)
    def test_006_verify_ldap_gui_login(self):
        print("Testcase 6 started")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
	output = os.popen("curl -k -u user1_ldap:infoblox -H 'Content-type: application/json' -X GET https://"+config.grid_vip+"/wapi/"+config.wapi_version+"/grid").read()
        print(output)
        if "401 Authorization Required" in output:
            assert True

        print("Test Case 006 Execution Completed")

    @pytest.mark.run(order=7)
    def test_007_verify_ldap_gui_login_log_validation(self):

	log("stop","/infoblox/var/infoblox.log",config.grid_vip)
	LookFor=[".*user1_ldap.*Login_Denied.*Admin has no enabled groups.*"]
	cnt=0
        for look in LookFor:
            logging.info(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            logging.info(logs)
            if logs:
                cnt=cnt+1
            else:
                cnt=cnt+0

        if cnt==1:
            logging.info(logs)
            logging.info("Success:LDAP login got failed")
            assert True
	    print("Test Case 007 Execution Completed")
        else:
            logging.info("Failed:LDAP login got successful without proper remote group")
            assert False
	    print("Test Case 007 Execution Completed")


    @pytest.mark.run(order=8)
    def test_008_verify_ldap_sshlogin(self):
        print("Testcase 8 started")
	log("start","/infoblox/var/infoblox.log",config.grid_vip)
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+config.ldap_username+'@'+config.grid_vip)
        child.expect ('password.*:')
        child.sendline ('infoblox')
        child.expect ('password.*:')
        child.send(chr(67))
        assert True
    	print("Test Case 008 Execution Completed")

    @pytest.mark.run(order=9)
    def test_009_verify_ldap_sshlogin_log_validation(self):

        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
	LookFor=[".*LDAP Authentication Succeeded for user.*user1_ldap.*Authorization group assignment failed\n\n\n.*"]
        cnt=0
        for look in LookFor:
            logging.info(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            logging.info(logs)
            if logs:
                cnt=cnt+1
            else:
                cnt=cnt+0
	if cnt==1:
            logging.info(logs)
            logging.info("Success:LDAP SSH login got failed")
            assert True
            print("Test Case 007 Execution Completed")
        else:
            logging.info("Failed:LDAP login got successful without proper remote group")
            assert False
            print("Test Case 009 Execution Completed")


    @pytest.mark.run(order=10)
    def test_010_cleanup(self):
	get_ref = ib_NIOS.wapi_request('GET', object_type='authpolicy?_return_fields=admin_groups')
        getref=json.loads(get_ref)[0]['_ref']
        print(getref)
	data={"admin_groups":[]}
        response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
        print(response)
        res = ib_NIOS.wapi_request('GET',object_type='authpolicy?_return_fields=auth_services')
        res = json.loads(res)
        print(res)
        localuser_ref=res[0][u'auth_services'][0]
        print("@@@@@@@@@@@@@@@@@",localuser_ref)
        
        logging.info("get authentication policy ref")
        res = ib_NIOS.wapi_request('GET',object_type='authpolicy')
        res = json.loads(res)
        print(res)
        auth_policy_ref=res[0][u'_ref']

	logging.info("Removing LDAP and Tacacs auth_services")
        data={"auth_services":[localuser_ref]}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=auth_policy_ref)
        print(response)

        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
               assert False

        res1 = ib_NIOS.wapi_request('GET', object_type="ldap_auth_service")
        print(res1)
        res1 = json.loads(res1)
        ldapref=res1[0][u'_ref']
	response = ib_NIOS.wapi_request('DELETE',ref=ldapref)
        print(response)

        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
               assert False

        res2 = ib_NIOS.wapi_request('GET', object_type="tacacsplus:authservice")
        print(res2)
        res2 = json.loads(res2)
        tacacsref=res2[0][u'_ref']
        response = ib_NIOS.wapi_request('DELETE',ref=tacacsref)
        print(response)

        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
               assert False

        res3 = ib_NIOS.wapi_request('GET', object_type="admingroup?name=infobloxgroup")
        print(res3)
        res3 = json.loads(res3)
        groupref=res3[0][u'_ref']
        response = ib_NIOS.wapi_request('DELETE',ref=groupref)
        print(response)

        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
               assert False

	print("Test Case 010 Execution Completed")
	

	

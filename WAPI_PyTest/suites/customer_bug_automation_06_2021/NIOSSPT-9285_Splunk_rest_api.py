#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Shekhar Srivastava"
__email__  = "ssrivastava@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Grid Master,Reporting member                                          #
#  2. Licenses : DNS(enabled),Grid,Reporting(enabled on both)               #
#############################################################################

from subprocess import Popen, PIPE, STDOUT
import re
import config
import pytest
from paramiko import client
import pexpect
import sys
import unittest
import logging
import os
import commands
import os.path
from os.path import join
import subprocess
from subprocess import PIPE
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS

def get_ref_member():
    get_ref = ib_NIOS.wapi_request('GET', object_type="adminuser", grid_vip=config.grid_vip)
    logging.info(get_ref)
    res = json.loads(get_ref)
    ref1 = json.loads(get_ref)[1]['_ref']
    return ref1

class Outbound(unittest.TestCase):

	@pytest.mark.run(order=1)
        def test_001_Create_Superuser_group_and_user(self):
                logging.info("Create super-user group")
                group = {"name":"test","superuser":True}
                get_ref_group = ib_NIOS.wapi_request('POST',object_type="admingroup", fields=json.dumps(group))
                if (get_ref_group[0] == 400):
                        print("Duplicate object \'super-user\' of type \'admin_group\' already exists in the database")
                        assert True
                else:
                        print("Group \'super-user\' has been created")
                        logging.info(get_ref_group)
                        user = {"name":"test","password":"infoblox","admin_groups":["test"]}
                        get_ref = ib_NIOS.wapi_request('POST',object_type="adminuser", fields=json.dumps(user))
                        if (get_ref[0] == 400):
                                print("Duplicate object \'new' of type \'super-user\' already exists in the database")

                        else:
                                print("User \'new\' has been created")




	@pytest.mark.run(order=2)
        def test_002_provide_reporting_user_capability_to_superuser(self):
                logging.info("Login as Admin")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
                print child
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('set reporting_user_capabilities enable test')
                child.expect('  1. Delete reporting indexed data')
                child.sendline('1')
                sleep(10)
                child.expect('Infoblox >')
                output = child.before
                child.sendline('exit')
                sleep(30)
                print("\nTest Case Executed Successfully")





	@pytest.mark.run(order=3)
        def test_003_Splunk_API_call_with_initial_username_and_password(self):
                logging.info("Splunk rest  API call with initial  username and password")
                import xml.etree.ElementTree as ET
                args = 'curl -k -u test:infoblox https://' +config.reporting_member1_ip +':9185/services/search/jobs/ -d search="search sourcetype=ib:dhcp:lease_history index=ib_dhcp_lease_history"'
                result= subprocess.check_output(args,stderr=subprocess.PIPE, shell=True)
                data = ET.fromstring(result)
                status = ''
                for child in data:
                    if child.tag == 'sid':
                        status = child.text
                if status != '':
                    assert True
                else:
                    assert False



	@pytest.mark.run(order=4)
        def test_004_Modify_Superuser_Password(self):
                logging.info("Modify super-user password")
		ref = get_ref_member()
                data = {"name":"test","password":"infoblox123","admin_groups":["test"]}
                response = ib_NIOS.wapi_request('PUT',ref=ref, fields=json.dumps(data))
		res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 4 Execution Completed")



	@pytest.mark.run(order=5)
        def test_005_Splunk_API_call_with_modify_password(self):
                logging.info("Splunk API call with modified password")
                import xml.etree.ElementTree as ET
                args = 'curl -k -u test:infoblox123 https://' +config.reporting_member1_ip +':9185/services/search/jobs/ -d search="search sourcetype=ib:dhcp:lease_history index=ib_dhcp_lease_history"'
                result= subprocess.check_output(args,stderr=subprocess.PIPE, shell=True)
                data = ET.fromstring(result)
                status = ''
                for child in data:
                    if child.tag == 'sid':
                        status = child.text
                if status != '':
                    assert False
                else:
                    assert True
                    print("This is expected as splunk API calls will work only after user login to UI with updated password")


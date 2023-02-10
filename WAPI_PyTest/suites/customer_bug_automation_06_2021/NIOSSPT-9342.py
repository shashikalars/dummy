__author__ = "Manoj Kumar R G"
__email__  = "mgovarthanan@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master + Reporting member                                                   #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415), NIOS (IB-805), Reporting license    #
########################################################################################


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
#from log_capture import log_action as log
#from log_validation import log_validation as logv
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv

class Network(unittest.TestCase):
    logging.basicConfig(filename='example.log', filemode='w', level=logging.DEBUG)

    @pytest.mark.run(order=1)
    def test_01_create_one_super_user(self):
        logging.info("Create super-user group")
        group = {"name":"super-user","superuser":True}
        get_ref_group = ib_NIOS.wapi_request('POST',object_type="admingroup", fields=json.dumps(group))
        if (get_ref_group[0] == 400):
            print("Duplicate object \'super-user\' of type \'admin_group\' already exists in the database")
            assert True
        else:
            print("Group \'super-user\' has been created")
        logging.info(get_ref_group)
        user = {"name":"new_user","password":"infoblox","admin_groups":["super-user"]}
        get_ref = ib_NIOS.wapi_request('POST',object_type="adminuser", fields=json.dumps(user))
        if (get_ref[0] == 400):
            print("Duplicate object \'new' of type \'super-user\' already exists in the database")
        else:
            print("User \'new\' has been created")
        logging.info (get_ref)
	logging.info("Test Case 1 Execution Completed")


    @pytest.mark.run(order=2)
    def test_02_start_infoblox_logs(self):
        logging.info("Starting Infoblox Logs")
        log("start","/infoblox/var/infoblox.log",config.reporting_member1_ip)
        logging.info("test case 2 passed")
	sleep(30)

    @pytest.mark.run(order=3)
    def test_03_execute_CLI_commands(self):
        #log("start","/infoblox/var/infoblox.log",config.grid_vip)
	logging.info("set debug/set reporting_user_capabilities")
	child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >',timeout=60)
        child.sendline('set debug all on')
	child.expect(': all')
	child.sendline('set reporting_user_capabilities enable new_user')
	child.expect('quit:')
	child.sendline('1')
	child.expect('The reporting Delete permission has been enabled for user new.')
	logging.info("Test Case 3 Execution Completed")
	print("Test Case 3 Execution Completed")
	sleep(120)

    @pytest.mark.run(order=4)
    def test_04_stop_infoblox_Logs(self):
        logging.info("Stopping Infoblox Logs")
        log("stop","/infoblox/var/infoblox.log",config.reporting_member1_ip)
        print("Test Case 4 Execution Completed")

    @pytest.mark.run(order=5)
    def test_05_validating_logs(self):
	sleep(30)
        logging.info("Validating Splunk restart on infoblox logs")
        LookFor="Stopping splunkd"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.reporting_member1_ip)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test Case 5 Execution Completed")
            assert True
        else:
            logging.info("Test Case 5 Execution Failed")
            assert False

    @pytest.mark.run(order=6)
    def test_06_clean_up(self):
	get_ref = ib_NIOS.wapi_request('GET', object_type="adminuser?name=new_user")
	ref1 = json.loads(get_ref)[0]['_ref']
	response = ib_NIOS.wapi_request('DELETE',ref=ref1)
	print(response)
	get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup?name=super-user")
        ref1 = json.loads(get_ref)[0]['_ref']
        response = ib_NIOS.wapi_request('DELETE',ref=ref1)
        print(response)
	
	
	


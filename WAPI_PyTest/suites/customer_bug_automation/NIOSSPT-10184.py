#!/usr/bin/env python
__author__ = "Manoj Kumar R G"
__email__  = "mgovarthanan@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Grid Master		                                            #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415)                           #
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
import paramiko
from paramiko import client
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv


class Network(unittest.TestCase):
    logging.basicConfig(filename='example.log', filemode='w', level=logging.DEBUG)

    @pytest.mark.run(order=1)
    def test_01_create_tacacs_authentication_server_group(self):
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

        print("Test Case 01 Execution Completed")

    @pytest.mark.run(order=2)
    def test_02__add_tacacs_plus_in_authentication_policy(self):
        logging.info("Add tacacs in authentication policy group")
        logging.info("get authentication policy ref")
        res = ib_NIOS.wapi_request('GET',object_type='authpolicy')
        res = json.loads(res)
        auth_policy_ref=res[0][u'_ref']
        res = ib_NIOS.wapi_request('GET',object_type='authpolicy?_return_fields=auth_services')
        res = json.loads(res)
        logging.info("get localuser and tacacsplus reference to add in auth_services")
        localuser_ref=res[0][u'auth_services'][0]
        print(localuser_ref)
        logging.info("get tacacs server ref")
        response = ib_NIOS.wapi_request('GET', object_type="tacacsplus:authservice")
        response = json.loads(response)
        tacacsplusref=response[0]['_ref']
        logging.info("adding localuser and tacacsplus authentication to authentication services")
        data={"auth_services":[localuser_ref,tacacsplusref]}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=auth_policy_ref)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
               assert False
        print("Test Case 02 Execution Completed")

    @pytest.mark.run(order=3)
    def test_03_create_super_user(self):
        logging.info("Creating User Group for mapping remote admin group")
        group={"name":"infobloxgroup","superuser": True}
        get_ref_group = ib_NIOS.wapi_request('POST',object_type="admingroup", fields=json.dumps(group))
        if (get_ref_group[0] == 400):
            print("Duplicate object \'infobloxgroup\' of type \'admin_group\' already exists in the database")
            assert True
        else:
            print("Group \'infobloxgroup\' has been created")
	print("Test Case 03 Execution Completed")

    @pytest.mark.run(order=4)
    def test_04_map_remote_admingroup_local_group(self):
        logging.info("Map the remote admin group to the local group in this order")
        get_ref = ib_NIOS.wapi_request("GET",object_type="authpolicy")
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"admin_groups": ["infobloxgroup"]}
	response = ib_NIOS.wapi_request("PUT",ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
	logging.info(response)
	print("Map the remote admin group to the local group in this order")
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
               assert False
        print("Test Case 04 Execution Completed")

    @pytest.mark.run(order=5)
    def test_05_start_infoblox_logs(self):
        logging.info("Starting Infoblox Logs")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("test case 5 passed")


    @pytest.mark.run(order=6)
    def test_06_validate_tacacs_plus_user_sshlogin(self):
        logging.info("validate tacacs server using SSH login")
        try:
	    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no user1@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >',timeout=60)
            child.sendline("exit")
            print(child.before)
            assert True
        except:
            assert False
        finally:
            child.close()
            #os.system("/import/tools/lab/bin/reset_console -H "+config.vmid)

	print("Test Case 06 Execution Completed")

    @pytest.mark.run(order=7)
    def test_07_stop_infoblox_Logs(self):
        logging.info("Stopping Infoblox Logs")
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        print("Test Case 7 Execution Completed")

    @pytest.mark.run(order=8)
    def test_08_validate_admin_group_not_found_database(self):
        logging.info("Validate user1 should be able to login using tacacs+ credentials ")
        LookFor="Admin group for user1 not found in the database"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test Case 8 Execution Completed")
            assert True
        else:
            logging.info("Test Case 8 Execution Failed")
            assert False

        logging.info("Test Case 8 Execution Completed")
        print("Test Case 8 Execution Completed")

    @pytest.mark.run(order=9)
    def test_09_start_infoblox_logs(self):
        logging.info("Starting Infoblox Logs")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("test case 9 passed")

    @pytest.mark.run(order=10)
    def test_10_validate_tacacs_plus_user_clilogin(self):
        logging.info("validating tacacsplus user authentication after adding tacacs in auth_services")
        try:
            child = pexpect.spawn("console_connect -H "+config.vmid,  maxread=100)
            child.expect(".*Escape character is .*")
            child.sendline("\r")
            child.expect(".*login:")
            child.sendline("user1")
            child.expect('password:')
            child.sendline("infoblox")
            child.expect("Infoblox >")
            child.sendline("exit")
            print(child.before)
            assert True
        except:
            assert False
        finally:
            #child = pexpect.spawn("console_connect -H "+config.vmid,  maxread=100)
	    child.sendline("exit")
	    child.close()
            os.system("/import/tools/lab/bin/reset_console -H "+config.vmid)
            sleep(20)
        print("Test Case 10 Execution Completed")

    @pytest.mark.run(order=11)
    def test_11_stop_infoblox_Logs(self):
        logging.info("Stopping Infoblox Logs")
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        print("Test Case 11 Execution Completed")

    @pytest.mark.run(order=12)
    def test_12_validate_admin_group_not_found_database(self):
        logging.info("Validate user1 should be able to login using tacacs+ credentials ")
        LookFor="Admin group for user1 not found in the database"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test Case12 Execution Completed")
            assert True
        else:
            logging.info("Test Case 12 Execution Failed")
            assert False

        logging.info("Test Case 12 Execution Completed")
        print("Test Case 12 Execution Completed")

    @pytest.mark.run(order=13)
    def test_13_check_cores(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(config.grid_vip, username='root')
        stdin, stdout, stderr = ssh.exec_command("ls /storage/cores/ | wc -l")
        response=stdout.readlines()
        print(response[0])
        if int(response[0]) == 0:
            assert True
        else:
            stdin, stdout, stderr = ssh.exec_command("ls -ltr /storage/cores/")
            response=stdout.readlines()
            print(response)
            assert False

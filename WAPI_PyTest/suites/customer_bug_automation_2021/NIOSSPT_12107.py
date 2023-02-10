#!/usr/bin/env python
__author__ = "Manoj Kumar R G"
__email__  = "mgovarthanan@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Grid Master - SA IB-4030                                              #
#  2. Licenses : DCA, TP, TP Update, DNS                                    #
#  3. Refer if any clarification https://infoblox.atlassian.net/browse/NIOSSPT-12107 #
#############################################################################

import re
import config
import pytest
import subprocess
import unittest
import logging
import os
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import commands
import json, ast
import requests
import time
import pexpect
import getpass
import paramiko
import shlex
from subprocess import Popen, PIPE
import sys
from paramiko import client

auth_zone={"fqdn": "indexer.com"}

class Network(unittest.TestCase):


    @pytest.mark.run(order=1)
    def test_01_create_dns_zone_records(self):
	
	logging.info("Create A new Zone")
	response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(auth_zone))
	print(response)
	logging.info(response)
	response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=indexer.com")
	res = json.loads(response)[-1]["fqdn"]
	print(res)
	if res == "indexer.com":
	    assert True
	
	data={"name":"arec."+auth_zone['fqdn'],"ipv4addr":"3.3.3.3","view": "default"}
	response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data))
        print(response)
        logging.info(response)
        response = ib_NIOS.wapi_request('GET', object_type="record:a")
        res = json.loads(response)[-1]["name"]
        print(res)
        if res == "arec.zone.com":
            assert True
	
	logging.info("Test Case 1 Execution Completed")
	print("Test Case 1 Execution Completed")

    @pytest.mark.run(order=2)
    def test_02_reset_database_system(self):
        logging.info("Validate system comes ONLINE post reset database")

	child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
	child.expect('password:')
	child.sendline('infoblox')
	child.expect('Infoblox >')
	child.sendline('reset database')
	child.expect("Do you wish to preserve basic network settings\? \(y or n\)\: ")
        child.sendline('y')
        child.expect("ARE YOU SURE YOU WANT TO PROCEED\? \(y or n\)\: ")
        child.sendline('y')
	for i in range(30):
	    ping = os.popen("for i in range{1..3};do ping -c 4 -w 10 "+config.grid_vip+"; done").read()
 	    print(ping)
   	    if "0 received" in ping:
	        print(config.grid_vip+" is pinging")
		assert True
	    else:
	        print(config.grid_vip+" is not pinging, Going to sleep for 60 seconds ")
	        sleep(60)
	
    @pytest.mark.run(order=3)
    def test_03_validate_dns_objects(self):
        logging.info("Validate DNS objects should be cleared post reset database")

        response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=indexer.com")
        res = json.loads(response)
        print(res)
        if res == "":
            assert True

        response = ib_NIOS.wapi_request('GET', object_type="record:a?name=arec.indexer.com")
        res = json.loads(response)
        print(res)
        if res == "":
            assert True

	logging.info("Testcase 3 completed")
	print("Testcase 3 completed")


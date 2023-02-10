#!/usr/bin/env python

__author__ = "Prasad K"
__email__  = "pkondisetty@infoblox.com"
__NIOSSPT_11812__ = 'WAPI responds with 500 Internal Server Error when logout WAPI call is used with cookie-based authentication'
########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master with member                                                          #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415), Cloud Network Automation            #
########################################################################################


import re
import sys
import config
import pytest
import unittest
import os
import os.path
from os.path import join
import json
import pexpect
import requests
import urllib3
import commands
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util
import time
import datetime

class NIOSSPT_11812(unittest.TestCase):


        @pytest.mark.run(order=01)
        def test_01_GET_the_cookie_details(self):
		print("\n====================")
                print("GET the cookie details")
                print("====================\n")
		global ibaplog
		child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
		child.sendline('curl -k -u admin:infoblox -X GET https://'+config.grid_vip+'/wapi/v'+config.wapi_version+'/grid -v')
		child.expect('#')
		child.sendline('curl -k -u admin:infoblox -X GET https://'+config.grid_vip+'/wapi/v'+config.wapi_version+'/grid -v')
                child.expect('#')
                grid_ref = child.before
		data = [str('ip='+config.grid_vip),'client=API','group=admin-group','auth=LOCAL','user=admin','200 OK']
		print(data)
		for i in data:
			if i in grid_ref:
				assert True
				print(i)
			else:
				assert False
		ibaplog = re.search('ibapauth=(.*)Path=/', grid_ref)
	        ibaplog = ibaplog.group(0)
		data = "ip="+config.grid_vip
		if data in ibaplog:
			assert True
			print(data)
		else:
			assert False
		print("Test Case Execution 01 is Completed")

        @pytest.mark.run(order=02)
        def test_02_GET_the_grid_reference_using_cookie(self):
		print("\n=================================")
                print("GET the grid reference using cookie")
                print("=================================\n")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline("curl -k -b '"+ibaplog+"' -X GET https://"+config.grid_vip+"/wapi/v"+config.wapi_version+"/grid -v")
                child.expect('#')
                child.sendline("curl -k -b '"+ibaplog+"' -X GET https://"+config.grid_vip+"/wapi/v"+config.wapi_version+"/grid -v")
                child.expect('#')
                output = child.before
                data = [str('ip='+config.grid_vip),'client=API','group=admin-group','auth=LOCAL','user=admin','200 OK']
                print(data)
                for i in data:
                        if i in output:
                                assert True
                        else:
                                assert False
                print("Test Case Execution 02 is Completed")

        @pytest.mark.run(order=03)
        def test_03_LOGOUT_using_cookie(self):
		print("\n=================")
                print("Logout using cookie")
                print("=================\n")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline("curl -k -b '"+ibaplog+"' -X POST https://"+config.grid_vip+"/wapi/v"+config.wapi_version+"/logout -v")
                child.expect('#')
                child.sendline("curl -k -b '"+ibaplog+"' -X POST https://"+config.grid_vip+"/wapi/v"+config.wapi_version+"/logout -v")
                child.expect('#')
                output = child.before
		if "500 Internal Server Error" in output:
			print("\n")
			print("500 Internal Server Error Found")
			print("\n")
			assert False
		else:
			assert True
			print("\n")
			print("500 Internal Server Error NOt Found")
			print("\n")
                print("Test Case Execution 03 is Completed")

        @pytest.mark.run(order=04)
        def test_04_After_logout_use_same_cookie_to_GET_the_grid_reference(self):
                print("\n====================================================")
                print("After logout use same cookie to GET the grid reference")
                print("====================================================\n")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline("curl -k -b '"+ibaplog+"' -X GET https://"+config.grid_vip+"/wapi/v"+config.wapi_version+"/grid -v")
                child.expect('#')
                child.sendline("curl -k -b '"+ibaplog+"' -X GET https://"+config.grid_vip+"/wapi/v"+config.wapi_version+"/grid -v")
                child.expect('#')
                grid_ref = child.before
                data = [str('ip='+config.grid_vip),'client=API','group=admin-group','auth=LOCAL','user=admin','200 OK']
                print(data)
                for i in data:
                        if i in grid_ref:
                                assert True
                        else:
                                assert False
                print("Test Case Execution 04 is Completed")


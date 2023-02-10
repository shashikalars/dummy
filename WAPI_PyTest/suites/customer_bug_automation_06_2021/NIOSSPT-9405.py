#!/usr/bin/env python
__author__ = "Manoj Kumar R G"
__email__  = "mgovarthanan@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Grid Master + Grid Member (PT-2200)                                   #
#  2. Licenses : Grid, NIOS (IB-V1415),Threat Protection	            #
#  3. Enable Threat Protection License                                      #
#############################################################################

import re
import config
import pytest
import unittest
import logging
import subprocess,signal
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

def get_reference_value_grid():
    logging.info("get reference value for GRID")
    get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
    logging.info(get_ref)
    res = json.loads(get_ref)
    print("**********************",res)
    ref1 = json.loads(get_ref)[0]['_ref']
    print("++++++++++++++++++++++",ref1)
    logging.info (ref1)
    return ref1


class Network(unittest.TestCase):
    logging.basicConfig(filename='example.log', filemode='w', level=logging.DEBUG)

    @pytest.mark.run(order=1)
    def test_01_setting_values_snmp(self):
        ref1=get_reference_value_grid()
        logging.info ("Setting values for SNMP Setting")
        data={"snmp_setting":{"queries_community_string":"public","queries_enable":True,"trap_receivers":[{"address":str(config.grid_member1_vip)}],"traps_community_string":"public","traps_enable":True}}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
        print("&&&&&&&&&&&&&&&&&&&&&&&",response)
        print("GRID_IP",config.grid_vip)
	print("GRID_MEMBER1_VIP",config.grid_member1_vip)
	logging.info(response)
        logging.info("============================")
        if (response[0]!=400):
            print("Value has been set successfully")
            assert True
        else:
            print("Incorrect values")
            assert False

    @pytest.mark.run(order=2)
    def test_02_check_SOCK_RAW(self):
	logging.info ("Checking whether SOCK_RAW is running under monitor")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
        child.logfile=sys.stdout
	#child.expect('password:')
	#child.sendline('D+mLz1zX')
        child.expect('-bash-5.0#')
	child.sendline('lsof -c monitor | grep SOCK_RAW')	
        child.expect('#')
	result=child.before
	print('\n')
	print(result)
        count = result.count('type=SOCK_RAW')
        print(count)
        if (count<=1):
           assert True
        else:
           assert False

        logging.info("Test Case 2 Execution Completed")
        print("Test Case 2 Execution Completed")

    @pytest.mark.run(order=3)
    def test_03_check_SOCK_RAW(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('-bash-5.0#')
        logging.info ("Checking whether SOCK_RAW process is getting increased")
	sleep(900)
        child.sendline('lsof -c monitor | grep SOCK_RAW')
        child.expect('#')
        result=child.before
        print(result)
        count = result.count('type=SOCK_RAW')
        print(count)
        if (count>1):
           assert False
        else:
           assert True

        logging.info("Test Case 3 Execution Completed")
        print("Test Case 3 Execution Completed")

    @pytest.mark.run(order=4)
    def test_04_cleanup_objects(self):
        ref1=get_reference_value_grid()
        logging.info ("Reset values for SNMP Setting")
        data={"snmp_setting":{"queries_enable": False,"trap_receivers":[],"traps_enable":False}}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
        print("&&&&&&&&&&&&&&&&&&&&&&&",response)
        print("GRID_IP",config.grid_vip)
        print("GRID_MEMBER1_VIP",config.grid_member1_vip)
        logging.info(response)
        logging.info("============================")
        if (response[0]!=400):
            print("Value has been set successfully")
            assert True
        else:
            print("Incorrect values")
            assert False

	

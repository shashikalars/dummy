__author__ = "Manoj Kumar R G"
__email__  = "mgovarthanan@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. Standalone Grid Master                                                          #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V815)                                      #
#  REFER https://jira.inca.infoblox.com/browse/NIOSSPT-11083 IF THIS SCRIPT FAILS     #
########################################################################################

import re
import config
import pytest
import unittest
import logging
import subprocess
import signal
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

def display_msg(x=""):
    """ 
    Additional function.
    """
    logging.info(x)
    print(x)

def restart_services(grid=config.grid_vip):
    """
    Restart Services
    """
    display_msg("Restart services")
    get_ref =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=grid)
    ref = json.loads(get_ref)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices", fields=json.dumps(data),grid_vip=grid)
    sleep(20)


class NIOSSPT_11083(unittest.TestCase):
    logging.basicConfig(filename='example.log', filemode='w', level=logging.DEBUG)

    @pytest.mark.run(order=1)
    def test_000_setup(self):
        """
        setup method: Used for configuring pre-required configs.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case setup Started            |")
        display_msg("------------------------------------------------")
        
        '''"Enable DNS service"'''
        display_msg("Enable DNS service")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns')
        display_msg(get_ref)
        ref = json.loads(get_ref)[0]
        response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps({"enable_dns":True}))
        if type(response) == tuple:
            display_msg("Failure: Enable DNS Service")
            assert False
        restart_services()
        
        '''Validation'''
        display_msg("Start validation")
        response_val = ib_NIOS.wapi_request('GET',object_type="member:dns", params="?_return_fields=enable_dns")
        display_msg(response_val)
        if not json.loads(response_val)[0]["enable_dns"] == True:
            display_msg("Validation failed")
            assert False
        display_msg("Validation passed")
        
        display_msg("---------Test Case setup Execution Completed----------")

    @pytest.mark.run(order=2)
    def test_001_execute_script_for_tcp_client(self):
        '''
        Execute script "CVE-2018-5743.py" along with Grid IP and port 53
        to simulate client tcp connections that violates tcp-clients quota 
	logs
        '''

        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 1 Execution Started           |")
        display_msg("----------------------------------------------------")
        sleep(5) 
        a = subprocess.Popen('python CVE-2018-5743.py '+config.grid_vip+' 53', shell=True)
        sleep(5)
	a.terminate()
	assert True
        display_msg("Script execution passed")
        
        display_msg("-----------Test Case 1 Execution Completed------------")
    
    @pytest.mark.run(order=3)
    def test_002_validate_warning_message(self):
        '''
        Validate TCP quota log messages that WARNING message should be updated in log 
        instead of DEBUG message, along with TCP client quota reached message 
        '''

        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 2 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -20 /var/log/syslog | grep  \'TCP client quota reached: quota reached\'"'
        out1 = commands.getoutput(sys_log_validation)
        display_msg(out1)
        res = re.search(r'.+warning client.+no-peer.+TCP client quota reached: quota reached',out1)
        if res == None:
            display_msg("Validation passed")
            assert True
        else:
            display_msg("Validation got failed")
            assert False
        
        display_msg("-----------Test Case 2 Execution Completed------------")



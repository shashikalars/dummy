#!/usr/bin/env python
__author__ = "Shubhashaya M"
__email__  = "smavinakuli@infoblox.com"

####################################################################################
#  Grid Set up required:                                                           #
#  1. Stand alone Grid Master                                                      #
#  2. Licenses : DNS, Grid, NIOS(IB-FLEX)                                        #
#  3. Enable DNS,TP services                                                          #
#  REFER https://jira.inca.infoblox.com/browse/NIOSSPT-10148 IF THIS SCRIPT FAILS  #
#                                                                                  #
####################################################################################

import re
import config
import pytest
import unittest
import logging
import os
import json
from time import sleep
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
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as comm_util
import ib_utils.log_capture as log_capture
from  ib_utils.log_capture import log_action as log
from  ib_utils.log_validation import log_validation as logv
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="NIOSSPT-10148.log" ,level=logging.DEBUG,filemode='w')

def display_msg(x=""):
    """
    Additional function.
    """
    logging.info(x)
    print(x)


class NIOSSPT_10638(unittest.TestCase):

    @pytest.mark.run(order=01)
    def test_01_enable_threat_protection(self):
        """
        enable threat protection on master
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case 1 Execution Started      |")
        display_msg("------------------------------------------------")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        ref1 = json.loads(get_ref)[0]['_ref']
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps({"enable_service": True}))
        res=json.loads(response)
        logging.info(response)
        display_msg(response)
	read  = re.search(r'201',response)
        for read in  response:
            assert True
        sleep(300)
        grid = ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(15)
        display_msg("-----------Test Case 1 Execution Completed------------")

    @pytest.mark.run(order=02)
    def test_02_test_TP_Service_Restart(self):
          logging.info("Enabling adp monitor-mode in CLI")
          args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid_member1_vip
          args=shlex.split(args)
          child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
          child.stdin.write("set adp monitor-mode on \n")
          child.stdin.write("show adp monitor-mode \n")
          child.stdin.write("exit")
          child.stdin.close()
          str1=child.stdout.read()
          logging.info(str1)
          #Validation for adp enabling
          for i in range(150):
	      sleep(2)
	      if (bool(re.search(r'Threat Protection monitor mode:  Enabled', str1))==True):
	          break
	      
	  '''
	  print((bool(re.search(r'Threat Protection monitor mode:  Enabled', str1))))
          if (bool(re.search(r'Threat Protection monitor mode:  Enabled', str1))==False):   
              assert False
          '''
  
          root_login= 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member1_vip)+''
          args=shlex.split(root_login)
          child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
          child.stdin.write(" while(true); do echo " ">/infoblox/var/fastpath_status; done \n")
          sleep(30)# Need sleep to retrieve particular logs 
          log("start","/infoblox/var/infoblox.log",config.grid_member1_vip) 
          sleep(60)
          log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
	  display_msg("-----------Test Case 2 Execution Completed------------") 
       
    @pytest.mark.run(order=03)
    def test_03_test_log_validation(self):
          check1=commands.getoutput(" grep -cw \".*ATP service status not found*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.log.log")
          check2=commands.getoutput(" grep -cw \".*one_send_snmp_trap()*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.log.log")
	  print(check1,check2)
          if ((int(check1)>0) and (int(check2)==0)):
                    assert True
          else:
                    assert False


    @pytest.mark.run(order=04)
    def test_cleanup_1(self):
        """
        cleanup method: This will Disable adp monitor-mode in CLI.
        """

        logging.info("Disabling adp monitor-mode in CLI")
        args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid_vip
        args=shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        child.stdin.write("set adp monitor-mode off \n")
	child.stdin.write("show adp monitor-mode \n")
        child.stdin.write("exit")
        child.stdin.close()
        str1=child.stdout.read()
        if (bool(re.search(r'Threat Protection monitor mode: Disabled', str1))==False):
              assert True
	
    @pytest.mark.run(order=-1)
    def test_cleanup(self):
        """
        cleanup method: Delete all the objects created from this script.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|          Test Case cleanup Started           |")
        display_msg("------------------------------------------------")
        display_msg("Disable threat protection service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        ref1 = json.loads(get_ref)[0]['_ref']
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps({"enable_service": False}))
        sleep(30)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(5)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(5)



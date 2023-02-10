#!/usr/bin/env python
__author__ = "Shubhashaya M"
__email__  = "smavinakuli@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Grid Master + Grid Member+Grid Member                                 #
#  2. Licenses : IB-V1415                                                   #
#############################################################################

import re
import config
#import config1
import pytest
import subprocess
import unittest
import logging
#import subprocess
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
#from dig_all_records import dig
from paramiko import client
#from log_capture import log_action as log
#from log_validation import log_validation as logv
#import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as comm_util

class Network(unittest.TestCase):          

      @pytest.mark.run(order=1)
      def test_01_generating_permanent_license(self):
          
          logging.info("Function for generating threat analytics license")
          license_gen_workstation_ip="10.120.20.188" #This ip should be harcoded as permanent license can be generated only by logging to 10.120.20.188
          args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid_vip
          args=shlex.split(args)
          child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
          child.stdin.write("show hwid\n")
          child.stdin.write("exit")
          hardware_id=child.communicate()
          str1=hardware_id[0].split(' ')
          str2=str1[-1].strip('\n')

          login1 = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no root@"+license_gen_workstation_ip
          args=shlex.split(login1)
          child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
          child.stdin.write("chroot /local/aslan_chroot \n")
          child.stdin.write("/infoblox/common/bin/generatelic -i " +str2+ " -p nios  -l 1415 \n")
          output=child.communicate()
          license_str=output[1].split('\n')[2]
          args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid_vip
          args=shlex.split(args)
          child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
          child.stdin.write("set license \n")
          child.stdin.write(license_str)
          child.stdin.write("y \n\r")
          child.stdin.write("y \n\r") 
          out=child.communicate()
          error_msg="ERROR:License string is not valid"
          for line in list(out):
              if 'Disconnect NOW if you have' in line:
                 continue
              if error_msg in line:
                 assert False

      @pytest.mark.run(order=2)
      def test_02_changing_time(self):
          sleep(30) 
          login2 = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no root@"+config.grid_vip
          args=shlex.split(login2)
          child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
          child.stdin.write("date --set='+1 day +1 hour' \n")
          out1=child.communicate()
          logging.info("Test Case 2 Execution Completed")
          sleep(30)
          
          
      @pytest.mark.run(order=3)
      def test_03_checking_online_status_member(self):

          member_ip=config.grid_member1_vip
          sleep(300)
          p = subprocess.Popen("grid_info "+member_ip+"",shell=True, stdout=subprocess.PIPE)
          print("Hello**********************************")
          out = p.communicate()
          print(out)
          if "OFFLINE" in out[0]:
              assert False
          infoblox_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str( config.grid_vip) + ' " tail -400 /infoblox/var/infoblox.log "'
          if (re.search(r'evict_all_nodes(): INFO: Put all nodes offline due to my license issues',infoblox_log_validation)==1):
              assert False
          logging.info("Test Case 3 Execution Completed")
          


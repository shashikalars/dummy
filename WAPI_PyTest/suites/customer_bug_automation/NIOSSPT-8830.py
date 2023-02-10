__author__ = "Shubhashaya Mavinakuli"
__email__  = "smavinakuli@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master + Grid Member                                                        #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415), TA  #
########################################################################################

import re
import config
#import config1
import pytest
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
#import pdb

def generating_license_string(self):
          logging.info("Function for generating threat analytics license")
          args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid_vip
          args=shlex.split(args)
          child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
          child.stdin.write("show license_uid \n")
          child.stdin.write("exit")
          child.stdin.close()
          str1=child.stdout.read()
          print(str1)
          l=str1.split()
          match=l[-1]
          print(match)
          cmd2='request_license -W '+ str(match)+' -p threat_anl -g yes'
          out2=os.popen(cmd2).read()
          #l2=out2.split('\n')
          #for i in l2:
          #    if 'LICENSE' in i:
          #        string=i.split('='[-1])
          #        license_string=string[1]
          #        break
          #out2=child.before
          matched = re.match(".*LICENSE=([A-Za-z\d/=]+).*",str(out2.split('\n')))
          if matched:
              license_string=matched.group(1)
              print(license_string)
          return(license_string)

class Network(unittest.TestCase):          

      @pytest.mark.run(order=1)
      def test_01_valid_threat_license(self):
          import pdb;pdb.set_trace()
          license_string1=generating_license_string(self)
          license_string_multiplied=3*license_string1
          args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid_vip
          args=shlex.split(args)
          child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
          child.stdin.write("set license \n")
          child.stdin.write(license_string_multiplied +'\n')
          out=child.communicate()
          error_msg="ERROR: License string is not valid"
          #for line in out:
          #    if error_msg in line:
          for line in list(out):
              if 'Disconnect NOW if you have' in line:
                 continue
              print(line)
              if error_msg not in line:
                 print("Error")
                 assert False      


      @pytest.mark.run(order=2)
      def test_02_valid_threat_license(self):
          #import pdb;pdb.set_trace()
          license_string1=generating_license_string(self)
          args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid_vip
          args=shlex.split(args)
          child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
          child.stdin.write("set license \n")
          print(child.stdin.write(license_string1 +'\n'))
          child.stdin.write("y"+'\n')
          #child.expect('\(y or n\):)
          #child.sendline('y')
          child.stdin.write("exit")
          child.stdin.close()
          str1=child.stdout.read()
          print(str1)


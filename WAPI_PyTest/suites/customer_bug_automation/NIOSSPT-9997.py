#!/usr/bin/env python
__author__ = "Shubhashaya M"
__email__  = "smavinakuli@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Grid Master                                                           #
#  2. Licenses : IB-V2225
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
#from pynput.keyboard import key,Controller
#from dig_all_records import dig
from paramiko import client
#from log_capture import log_action as log
#from log_validation import log_validation as logv
#import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as comm_util

class Network(unittest.TestCase):          

      @pytest.mark.run(order=1)
      def test_01_emergency_prompt_with_no_reset(self):

          logging.info("Not performing reset_storage in Emergency mode")
          child = pexpect.spawn("console_connect -H "+config.vmid,  maxread=4000)
          try:
                #child.sendline("\r")
                child.expect(".*Escape character is .*")
                #child.expect(".*Disconnect NOW if you have not been .*")
                child.sendline("\r")
                child.expect(".*login:",timeout=100)
                child.sendline("admin")
                child.expect('password:',timeout=100)
                child.sendline("infoblox")
                child.expect("Infoblox >")

                child.sendline('reboot')
                #child.expect('\(y or n\): ')
                #child.expect('.*REBOOT THE SYSTEM?.*')
                child.expect("REBOOT THE SYSTEM\? \(y or n\)\: ")
                #child.send('y\n')
                child.send('y')
                child.send('\n')

                Error_msg="Catastrophic recovery failure"
                str1=".*Hit \"Esc\" and \"Enter\" now for Emergency prompt.*"
                child.expect(str1, timeout=800) #Expecting str1 line for 800sec
                child.send(chr(27))             #Press "ESC"
                child.send('\r')                #Press "Enter"

                child.expect('Emergency>')  #Entering Emergency mode
                child.sendline("reset storage")
               # child.sendline("")
                child.expect('.*DO YOU WANT TO PROCEED?.*',timeout=100)
                child.send('n')
                child.send('\n')
                #child.sendline("n")
                child.expect('Emergency>',timeout=100)
                #child.sendline('set')
                #child.expect('Emergency>',timeout=30)
                #child.sendline('version')
                #child.expect('Emergency>',timeout=30)
                #child.sendline('help')
                #child.expect('Emergency>',timeout=30)
                #child.expect('Emergency>',timeout=100)
      
          except Exception as e:
                #child.close()
                print (e)
                child.sendline("exit")
                child.close()
                os.system("/import/tools/lab/bin/reset_console -H "+config.vmid)
                sleep(20)
                assert False


          try:
                child.sendline("exit")
                child.expect(".*login:",timeout=1200)


          except Exception as e:
                #child.expect(Error_msg, timeout=3600)
                #print ("Catastrophic recovery failure found")
                print e
                assert False

          finally:
                child = pexpect.spawn("console_connect -H "+config.vmid,  maxread=100)
                child.expect(".*Escape character is .*")
                #child.expect(".*Disconnect NOW if you have not been .*")
                child.sendline("\r")
                child.expect(".*login:",timeout=100)
                child.sendline("admin")
                child.expect('password:',timeout=100)
                child.sendline("infoblox")
                child.expect("Infoblox >")
                child.sendline("exit")
                child.close()
                os.system("/import/tools/lab/bin/reset_console -H "+config.vmid)
                sleep(20)


      @pytest.mark.run(order=2)
      def test_02_emergency_prompt_reset(self):
          
          logging.info("Performing reset storage in Emergency mode")
          child = pexpect.spawn("console_connect -H "+config.vmid,  maxread=2000)
          try:
                child.expect(".*Escape character is .*")
                child.sendline("\r")
                child.expect(".*login:")
                child.sendline("admin")
                child.expect('password:')
                child.sendline("infoblox")
                child.expect("Infoblox >")

                child.sendline('reboot')
                #child.expect('.*REBOOT THE SYSTEM?.*')
                child.expect("REBOOT THE SYSTEM\? \(y or n\)\: ")
                child.send('y')
                child.send('\n')

                Error_msg="Catastrophic recovery failure"
                str1=".*Hit \"Esc\" and \"Enter\" now for Emergency prompt.*"
                child.expect(str1, timeout=800)#Expecting str1 line for 800sec
                child.send(chr(27))#Press "ESC"
                child.send('\r') #Press "Enter"

                child.expect('Emergency>')
                child.sendline("reset storage")
                child.expect('.*DO YOU WANT TO PROCEED?.*',timeout=100)
                child.send('y')
                child.send('\n')
                child.expect('.*ARE YOU SURE YOU WANT TO PROCEED.*',timeout=50)
                child.send('y')
                child.send('\n')               
                child.expect('.*Remounting root as rw',timeout=300)
                child.expect('.*Stopping ptop',timeout=300)
                child.expect('.*Stopping ib_100_gpio',timeout=300)
                child.expect('.*Stopping syslog-ng',timeout=300)

          except Exception as e:
                #child.close()
                print (e)
                child.sendline("exit")
                child.close()
                os.system("/import/tools/lab/bin/reset_console -H "+config.vmid)
                sleep(20)
                assert False
                

          try:
                child.expect(".*login:",timeout=1200)#Expecting "login" prompt after restore storage
                #child.expect(Error_msg, timeout=1200)
                 

          except Exception as e:
          #      child.expect(Error_msg, timeout=3600)
          #      print ("Catastrophic recovery failure found")
                print e
                assert False
                
          finally:
            
                child = pexpect.spawn("console_connect -H "+config.vmid,  maxread=100)
                child.expect(".*Escape character is .*")
                #child.expect(".*Disconnect NOW if you have not been .*")
                child.sendline("\r")
                child.expect(".*login:",timeout=100)
                child.sendline("admin")
                child.expect('password:',timeout=100)
                child.sendline("infoblox")
                child.expect("Infoblox >")
                child.sendline("exit")
                child.close()
                os.system("/import/tools/lab/bin/reset_console -H "+config.vmid)
                sleep(20)






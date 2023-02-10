__author__ = "Ashwini C M, Chetan Kuamr PG"
__email__  = "cma@infoblox.com, cpg@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master (IB_4030)                                                            #
#  2. Licenses : DNS, DHCP, Grid, NIOS and DCA license                                 #
#  3. Services: DCA service                                                            #
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
#import requests
import time
import pexpect
import paramiko
import sys
from ib_utils.log_capture import log_action as log
from ib_utils.log_validation import log_validation as logv
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="niosspt_9233.log" ,level=logging.DEBUG,filemode='w')

def display_msg(x=""):
    """ 
    Additional function.
    """
    logging.info(x)
    print(x)

def validate_syslog(lookfor, logfile, grid=config.grid_vip):
    """
    Validate captured log
    Using this file because log_validation.py in ib_utils is not correct.
    """
    display_msg("Validate captured log")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(grid, username='root', pkey = mykey)
    file_name='_'.join(logfile.split('/'))
    file = '/root/dump/'+ str(grid)+file_name+'.log'
    display_msg("cat "+file+" | grep -i '"+lookfor+"'")
    stdin, stdout, stderr = client.exec_command("cat "+file+" | grep -i '"+lookfor+"'")
    result=stdout.read()
    display_msg(result)
    client.close()
    if result:
        return True
    return False

class NIOSSPT_9233(unittest.TestCase):

    @pytest.mark.run(order=01)
    def test_001_set_smartnic_on_cmd_and_validate_audit_logs(self):
        """
        Run command 'set smartnic-debug dsr on'
        Validate audit log for correct log message.
        maintenancemode="on from off"
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 1 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Execute command 'set smartnic-debug dsr on'")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        display_msg("Start capturing /infoblox/var/audit.log")
        log("start","/infoblox/var/audit.log",config.grid_vip)
        try:
            child.expect ('password.*:')
            child.sendline ('infoblox')
            child.expect ('Infoblox >',timeout=60)
            child.sendline('set maintenancemode')
            child.expect("Maintenance Mode > ")
            child.sendline ('set smartnic-debug dsr on')
            sleep(10)
        except Exception as e:
            display_msg("Failure: Execute command 'set smartnic-debug dsr on'")
            display_msg(e)
            assert False
        finally:
            child.close()
        
        lookfor = "maintenancemode=\"on from off\""
        result = validate_syslog(lookfor, '/infoblox/var/audit.log', config.grid_vip)
        display_msg("Stop capturing /infoblox/var/audit.log")
        log("stop","/infoblox/var/audit.log",config.grid_vip)
        if not result:
            display_msg("Failure: Validate captured log /infoblox/var/audit.log")
            assert False
        
        display_msg("-----------Test Case 1 Execution Completed------------")

    @pytest.mark.run(order=02)
    def test_002_set_smartnic_off_cmd_and_validate_audit_logs(self):
        """
        Run command 'set smartnic-debug dsr off'
        Validate audit log for correct log message.
        maintenancemode="off from on"
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 2 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Execute command 'set smartnic-debug dsr off'")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        display_msg("Start capturing /infoblox/var/audit.log")
        log("start","/infoblox/var/audit.log",config.grid_vip)
        try:
            child.expect ('password.*:')
            child.sendline ('infoblox')
            child.expect ('Infoblox >',timeout=60)
            child.sendline('set maintenancemode')
            child.expect("Maintenance Mode > ")
            child.sendline ('set smartnic-debug dsr off')
            sleep(10)
        except Exception as e:
            display_msg("Failure: Execute command 'set smartnic-debug dsr off'")
            display_msg(e)
            assert False
        finally:
            child.close()
        
        lookfor = "maintenancemode=\"off from on\""
        result = validate_syslog(lookfor, '/infoblox/var/audit.log', config.grid_vip)
        display_msg("Stop capturing /infoblox/var/audit.log")
        log("stop","/infoblox/var/audit.log",config.grid_vip)
        if not result:
            display_msg("Failure: Validate captured log /infoblox/var/audit.log")
            assert False
        
        display_msg("-----------Test Case 2 Execution Completed------------")


                    

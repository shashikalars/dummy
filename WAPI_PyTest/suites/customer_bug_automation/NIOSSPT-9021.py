__author__ = "Arunkumar CM"
__email__  = "acm@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master                                                                      #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415)                                      #
########################################################################################
import config
import paramiko
import datetime
import re
import pexpect
import pytest
import unittest
import logging
import subprocess
import os
import json
import config
import ib_utils.ib_NIOS as ib_NIOS
from time import sleep
import commands
import json, ast
import requests
import time
import getpass
import sys
import pexpect


def request_license():
    cmd='request_license -H '+config.vm_id+' -p dhcp -l 5d'
    command2=subprocess.check_output(cmd, shell=True)
    command2=command2.split("\n")
    license_key=command2[3][8:]
    invalid_license_key=license_key*2
    #print invalid_license_key
    #print license_key
    return invalid_license_key,license_key

class Network(unittest.TestCase):



    def test_001_invalid_license(self):
        try:
            key=request_license()
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            #child.logfile=sys.stdout
            child.logfile_read = sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set license')
            child.expect('Enter license string:')
            #child.sendline('asdg')
            child.sendline(key[0])
            child.expect('Infoblox >')
            child.sendline('exit')
            print child.before
            assert True
        except:
            assert False

    def test_002_valid_license(self):
        try:
            key=request_license()
            print key
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            #child.logfile_read = sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set license')
            child.expect('license string:')
            #child.sendline('asdg')
            child.sendline(key[1])
            option="y"
            child.expect('\(y or n\):')
            child.delaybeforesend = None
            child.sendline(option)
            child.expect('\(y or n\):')
            child.sendline(option)
            child.expect('\(y or n\):')
            child.sendline(option)
            child.expect('Infoblox >')
            child.sendline('exit')
            print child.before
            assert True
        except:
            assert False

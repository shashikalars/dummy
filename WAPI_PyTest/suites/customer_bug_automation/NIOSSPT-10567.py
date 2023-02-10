#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
# Grid Set up required:                                                     #
#  1. Licenses : Grid                                                       #
#############################################################################
import os
import re
import config
import pytest
import unittest
import logging
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import shlex
from time import sleep
from subprocess import Popen, PIPE
import pexpect
import paramiko
from scapy import *
from scapy.utils import RawPcapReader
from scapy.all import *
import shutil

class NIOSSPT_10567(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_reset_network(self):
        print("Performing reset all")
        os.system("/import/tools/lab/bin/reset_console -H "+config.vmid)
        sleep(20)
        child=pexpect.spawn("console_connect -H "+config.vmid,  maxread=4000)
        try:
            child.expect(".*Escape character is .*",timeout=100)
            child.sendline("\r")
            child.expect(".*login:",timeout=100)
            child.sendline("admin") 
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('reset all')
            child.expect('y or n')
            child.sendline('n')
            sleep(10)
            child.sendline("exit")
            child.expect(".*login:")
            child.close()
            print("\nSuccess: reset all")
            assert True
            
        except Exception as e:
            child.close()
            print (e)
            print("Failure: reset all")
            assert False
           
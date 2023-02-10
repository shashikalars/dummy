#!/usr/bin/env python
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. SA with Grid                                                          #
#  2. License : DNS ,DHCP license                                           #
#############################################################################

import re
import config
import pytest
import unittest
import logging
import subprocess
import os
import json
import commands
import json, ast
import requests
from time import sleep as sleep
import pexpect
import paramiko
from paramiko import client
import ib_utils.common_utilities as comm_util
import ib_utils.ib_NIOS as ib_NIOS
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv

class NIOS_69634(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_check_time_stamp_from_PTOP_log_and_syslog(self):
        ptop=''
        sysl=''
        ptop_ltst=''
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey) 
        data="ls -ltr /var/log/ptop-* \n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.readlines()
        print('\n')
        ptop_ltst=stdout[-1]
        ptop_ltst=(ptop_ltst.split(' ')[-1])
        print("PTOP log: "+ptop_ltst)
        client.close()

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data="grep TIME "+ptop_ltst+"\n"
        stdin, stdout, stderr = client.exec_command(data)
        res=stdout.readline()
     
        hour=res.split(' ')[-1]
        print("PTOP time stamp: "+res+"->"+res.split(' ')[-2]+"T"+hour.split(':')[-3])
        ptop=res.split(' ')[-2]+"T"+hour.split(':')[-3]
        client.close()
        sleep(20)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data="grep TIME /var/log/syslog\n"
        #data="tail -n 4  /var/log/syslog\n"
        stdin, stdout, stderr = client.exec_command(data)
        
        res=stdout.readlines()
        print(res)
        hour=''
        #print(ptop)
        print("----------------------------------------")
        #print(res)
        for i in res:
            #print(i)
            #print("**************************")
            if ptop in i:
                hour=i

        print(hour)
        hours=hour.split(' ')[0]
        sysl=hours.split(':')[-0]
        print("Sys time stamp : "+hour+"->"+sysl)
        client.close()
        if sysl==ptop:
            print("Success : The time stamp from PTOP log and syslog matches")
            assert True
        else:
            print("Failure : The time stamp from PTOP log and syslog matches")
            assert False

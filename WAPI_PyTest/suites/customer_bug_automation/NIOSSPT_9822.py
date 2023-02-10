#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Chetan Kumar PG"
__email__  = "cpg@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Grid Master                                                           #
#  2. Licenses : DNS(enabled), DHCP, Grid                                   #
#############################################################################

import os
import re
import csv
import config
import pytest
import unittest
import logging
import json
import pexpect
import paramiko
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as ib_TOKEN
#from ib_utils.log_capture import log_action as log
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="niosspt_9822.log" ,level=logging.DEBUG,filemode='w')
   
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

def display_msg(x=""):
    """ 
    Additional function.
    """
    logging.info(x)
    print(x)

class NIOSSPT_9822(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_001_set_transfer_supportbundle(self):
        """
        SSH as admin to the device
        Run debug shell
        Run set transfer_supportbundle scp 127.0.0.1 '$(touch /infoblox/var/flags/serial_debug_shell)' infoblox
        Run debug shell
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 1 Execution Started           |")
        display_msg("----------------------------------------------------")

        '''SSH with admin user to the device'''
        
        display_msg("SSH with admin user to the device")
        args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid_vip
        conn = pexpect.spawn(args)
        
        try:
            display_msg("sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid_vip)
            conn.expect("Infoblox >")
            conn.sendline("debug shell")
            conn.expect("Infoblox >")
            display_msg("debug shell")
            conn.sendline("set transfer_supportbundle scp 127.0.0.1 '$(touch /infoblox/var/flags/serial_debug_shell)' infoblox")
            conn.expect(".Synopsis:.*")
        except Exception as E:
            display_msg(E)
            conn.expect(".*y or n.*")
            conn.sendline("y")
            conn.expect("Infoblox >", timeout=200)
            display_msg("y")
            conn.sendline("debug shell")
            conn.expect(".*#")
            display_msg("Failure: Admin to root login is successfull")
            assert False
        finally:
            conn.close()
        
        display_msg("-----------Test Case 1 Execution Completed------------")
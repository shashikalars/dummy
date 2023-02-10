__author__ = "Manoj Kumar R G"
__email__  = "mgovarthanan@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master + Reporting Member                                                   #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415), NIOS (IB-805), Reporting License    #
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
import json, ast
import requests
import time
import pexpect
import getpass
import sys
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="niosspt_8850.log" ,level=logging.DEBUG,filemode='w')

def display_msg(x=""):
    """ 
    Additional function.
    """
    logging.info(x)
    print(x)

class NIOSSPT_8850(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_01_execute_reporting_reset_license(self):
        """
        SSH as admin to grid and execute below commands.
        set reporting_reset_license.
        Validate the SSH connection is not closed.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 1 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Execute set reporting_reset_license command")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        try:
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >',timeout=60)
            child.sendline('set reporting_reset_license')
            child.expect('string:')
            child.sendline('\r\n')
        except Exception as E:
            display_msg("Failure: Failed to execute command 'set reporting_reset_license'")
            display_msg(E)
            assert False
        finally:
            child.close()
        
        display_msg("-----------Test Case 1 Execution Completed------------")


#!/usr/bin/env python
__author__ = "Chetan Kumar PG"
__email__  = "cpg@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Stand alone Grid Master                                               #
#  2. Licenses : DNS, DHCP, Grid                                            #
#############################################################################

import os
import re
import config
import pytest
import unittest
import logging
import json
import shlex
import subprocess
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="niosspt_9356.log" ,level=logging.DEBUG,filemode='w')

def display_msg(x=""):
    """ 
    Additional function.
    """
    logging.info(x)
    print(x)

class NIOSSPT_9356(unittest.TestCase):
    
    @pytest.mark.run(order=1)
    def test_000_setup(self):
        """
        setup method: Used for configuring pre-required configs.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case setup Started            |")
        display_msg("------------------------------------------------")
        pass
    
    @pytest.mark.run(order=2)
    def test_001_check_metaspace_size_and_max_metaspace_size_using_CLI(self):
        """
        SSH into the divice.
        Check metaspace size and max metaspace size using below CLI.
        ps -ef | grep Size
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 1 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Check metaspace size and max metaspace size using CLI")
        cmd=('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@%s' % (config.grid_vip))
        cmd = shlex.split(cmd)
        cmd.append('ps -ef | grep Size')
        display_msg(cmd)
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        output = process.communicate()
        #display_msg(output)
        display_msg()
        for line in list(output):
            if 'Disconnect NOW if you have' in line:
                continue
            display_msg(line)
            if not '-XX:MetaspaceSize=180M' in line.split():
                display_msg("Failure: MetaspaceSize=180M not found in the output")
                assert False
            if not '-XX:MaxMetaspaceSize=260M' in line.split():
                display_msg("Failure: MaxMetaspaceSize=260M not found in the output")
                assert False
        display_msg("-----------Test Case 1 Execution Completed------------")

    @pytest.mark.run(order=3)
    def test_002_check_metaspace_size_and_max_metaspace_size_from_file(self):
        """
        SSH into the divice.
        Check metaspace size and max metaspace size from below file.
        /infoblox/one/bin/webui_control
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 2 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Check metaspace size and max metaspace size from file")
        cmd=('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@%s' % (config.grid_vip))
        cmd = shlex.split(cmd)
        cmd.append('cat /infoblox/one/bin/webui_control')
        display_msg(cmd)
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        output = process.communicate()
        #display_msg(output)
        display_msg()
        for line in list(output):
            if 'Disconnect NOW if you have' in line:
                continue
            display_msg(line)
            if not 'INITIAL_METASPACE_SIZE=180M' in line.split():
                display_msg("Failure: INITIAL_METASPACE_SIZE=180M not found in the output")
                assert False
            if not 'MAX_METASPACE_SIZE=260M' in line.split():
                display_msg("Failure: MAX_METASPACE_SIZE=260M not found in the output")
                assert False
        display_msg("-----------Test Case 2 Execution Completed------------")

    @pytest.mark.run(order=-1)
    def test_cleanup(self):
        """
        cleanup method: Delete all the objects created from this script.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|          Test Case cleanup Started           |")
        display_msg("------------------------------------------------")
        display_msg("-----------Test Case cleanup Completed------------")
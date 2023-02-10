#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Vindya V K"
__email__  = "vvk@infoblox.com"

#############################################################################
# Grid Set up required:                                                     #
#  1. Grid Master (SA)  - 9.0.0-48631                                       #
#  2. Licenses : DNS, DHCP, Grid, NIOS                                      #
#                                                                           #
#############################################################################

#### REQUIRED LIBRARIES ####
import os
import sys
import json
import config
import pytest
import unittest
import logging
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util
import pexpect


#####################################################################################################
# BUGS INCLUDED IN THIS SCRIPT:                                                                     #
#                                                                                                   #
# 1. NIOS-86741     (Automated by Vindya)                                                           #

#####################################################################################################


logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="9.0_CA_bugs.log" ,level=logging.DEBUG,filemode='w')

def display_message(x=""):
    # Additional function used to log and print using a single line
    logging.info(x)
    print(x)

class Bondi_CA_bugs(unittest.TestCase):

# Login as admin and execute CLI command 'rotate log syslog'

    @pytest.mark.run(order=1)
    def test_001_NIOS_86741(self):
        display_message("\n========================================================\n")
        display_message("Executing CLI command 'rotate log syslog'")
        display_message("\n========================================================\n")

        try:
            child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect("password:")
            child.sendline("infoblox")
            child.expect("Infoblox >")
            child.sendline("rotate log syslog")
            child.expect("The selected log file has been rotated to syslog.0.gz")
            child.expect("Infoblox >")
            print("SUCCESS: ")
            assert True

        except Exception as e:
            print(e)
            child.close()
            print("FAILURE: ")
            assert False

        finally:
            child.close()

        display_message("\n***************. Test Case 1 Execution Completed .***************\n")


# Login as root and check if /var/log/syslog is present

    @pytest.mark.run(order=2)
    def test_002_NIOS_86741(self):
        display_message("\n========================================================\n")
        display_message("Logging in as root and checking if syslog folder is peresent ")
        display_message("\n========================================================\n")

        try:
            child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect(".*#")
            child.sendline("ls -ltr /var/log/syslog* > output.txt")
            child.expect(".*#")
            os.system("sshpass -p 'infoblox' scp -pr root@"+config.grid_vip+":output.txt .")
            
            with open('output.txt') as file:
                output=file.readlines()
                print(type(output))
                if '/var/log/syslog\n' in output[-1]:
                    print("SUCCESS: ")
                    assert True
                else:
                    print("FAILURE: ")
                    assert False

        except Exception as e:
            print(e)
            child.close()
            print("FAILURE: ")
            assert False

        finally:
            child.close()

        display_message("\n***************. Test Case 2 Execution Completed .***************\n")


# Clean Up

    @pytest.mark.run(order=3)
    def test_003_NIOS_86741_cleanup(self):
        display_message("\n============================================\n")
        display_message("CLEANUP: Reverting back to original setup...")
        display_message("\n============================================\n")

        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect(".*#")
        child.sendline("rm -rf output.txt")
        child.expect(".*#")
        os.system("rm -rf output.txt")

        print("\n***************. Test Case 3 Execution Completed .***************\n")



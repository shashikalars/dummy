#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Vindya V K"
__email__  = "vvk@infoblox.com"

#############################################################################
# Grid Set up required:
#  1. HA grid + 1 reporting member
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415)
##
#############################################################################

import os
import re
import config
import pytest
import unittest
import logging
import json
import pexpect
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util
# from log_capture import log_action as log
# from log_validation import log_validation as logv
from ib_utils.log_capture import log_action as log
from ib_utils.log_validation import log_validation as logv


class NIOSSPT_10616(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_001_cli_command(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info ("SETTING REPORTING_RESET_LICENSE")

      # logging.info("Not performing reset_storage in Emergency mode")
        child = pexpect.spawn("console_connect -H "+config.vmid,  maxread=4000)
        try:
            child.expect(".*Escape character is .*",timeout=100)
            child.sendline("\r")
            child.expect(".*login:",timeout=100)
            child.sendline("admin")
            child.expect('password:',timeout=100)
            child.sendline("infoblox")
            child.expect("Infoblox >")

            child.sendline('set reporting_reset_license')
            child.expect("Enter reset license string: ")
            sleep(900)
            empty = child.expect(".*login:",timeout=100)
            if empty == ".*login:":
                assert False
            else:
                child.close()
                assert True


        except Exception as e:
            print(e)
            child.close()
            assert False


        finally:
            child.close()


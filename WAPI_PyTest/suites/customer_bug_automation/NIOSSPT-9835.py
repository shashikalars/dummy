#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"
#############################################################################
#  Grid Set up required:                                                    #
#  1. Standalone with RPZ license                                           #
#  2. Licenses : DNS(enabled), DHCP, Grid                                   #
#############################################################################
import os
import re
import config
import pytest
import unittest
import logging
import subprocess
import paramiko
import json
import shlex
from time import sleep
from subprocess import Popen, PIPE
import ib_utils.ib_NIOS as ib_NIOS

class NIOSSPT_9835(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_000_NIOSSPT_9835(self):
        args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid_vip
        args=shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        data="a"*5013
        child.stdin.write("show rpz_recursive_only "+data+" \n")
	sleep(10)
        output = child.communicate()
        msg="Serial Console command size should not exceed 4096 characters"

        for line in list(output):
                if 'Disconnect NOW if you have' in line:
                        continue
                        print(line)
                if msg in line:
                        print("Sucessfully Found the message")
                        assert True
                else:
                        print("Unsucsessful")
                        assert False


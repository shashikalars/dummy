#!/usr/bin/env python

__author__ = "Manoj Kumar R G"
__email__  = "mgovarthanan@infoblox.com"
__RFE__    = "https://infoblox.atlassian.net/browse/NIOSSPT-11611"
############################################################################################################
#  Grid Set up required:                                                                                   #
#  1. SA PT-1405 Grid
#  2. Licenses : DNS, Grid, RPZ, Threat Protection                                                         #
############################################################################################################

import re
import sys
import config
import pytest
import unittest
import os
import os.path
from os.path import join
import json
import pexpect
import requests
import urllib3
import commands
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util
import ib_utils.common_utilities as comm_util
import subprocess
import paramiko
import time
from datetime import datetime, timedelta
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv

class NIOSSPT_11611(unittest.TestCase):

	@pytest.mark.run(order=001)
	def test_001_validate_rabbitmq_status_UP(self):

		rabbitmq = 'ssh -o StrictHostKeyChecking=no root@'+config.grid_vip+' "/infoblox/one/bin/rabbitmq_control" "status"'
		rabbitmq_command = subprocess.check_output(rabbitmq, shell=True)
		assert re.search(r'.*\'enabled\': True*',rabbitmq_command)
		assert re.search(r'.*\'my_vnode_id\': \'0\'',rabbitmq_command)
		
		

        @pytest.mark.run(order=002)
        def test_002_validate_erlang_cookies(self):
                print("Validate through GM LAN IP erlang cookie should have 200bytes")
                print("============================================")
                sleep(03)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''wc -c /var/lib/rabbitmq/.erlang.cookie''')
                        child.expect('#')
                        print("\n")
                        output = child.before
                        output = output.replace("\n","").replace("\r","").replace(" wc -c /var/lib/rabbitmq/.erlang.cookie"," ").replace('-bash-4.0','')
                        print("==============================")
                        print(output)
                        print("==============================")
                        print("\n")
                        result = re.search('200(.*)erlang.cookie', output)
                        result = result.group(0)
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 002 Execution Completed")


	

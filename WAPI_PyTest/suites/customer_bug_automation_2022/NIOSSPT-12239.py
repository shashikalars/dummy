#!/usr/bin/env python

__author__ = "Prasad K"
__email__  = "pkondisetty@infoblox.com"
__NIOSSPT_12239__ = 'Threat Analytics failed - Spark metrics are NOT OK'
########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master with member                                                          #
#  2. Licenses : DNS, DHCP, Grid, NIOS , TA , RPZ                                      #
########################################################################################

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
import logging
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util
import paramiko
import time
from datetime import datetime, timedelta
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util
import ib_utils.log_capture as log_capture
from  ib_utils.log_capture import log_action as log
from  ib_utils.log_validation import log_validation as logv

class NIOSSPT_12239(unittest.TestCase):

            @pytest.mark.run(order=01)
            def test_01_Validate_the_presence_of_the_analytics_folder_under_infoblox_var_on_grid(self):
		print("\n===========================================================================")
                print(" Validating the presence of the analytics folder under /infoblox/var on grid ")
		print("=============================================================================")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('ls /infoblox/var/analytics')
                child.expect('#')
                output=child.before
                print(output)
		data = 'model.xml'
		if data in output:
			assert True
			print(" analytics folder present under /infoblox/var ")
		else:
			assert False
			print(" analytics folder not present under /infoblox/var ")
                print("\nTest Case 01 Executed Successfully")

            @pytest.mark.run(order=02)
            def test_02_Create_rpz_zone(self):
		print("\n=================")
		print(" Creating RPZ zone ")
		print("===================")
		data = {"fqdn": "rpz.com","grid_primary": [{"name": config.grid_fqdn,"stealth": False}],"view": "default"}
		response = ib_NIOS.wapi_request('POST', object_type="zone_rp", fields=json.dumps(data), grid_vip=config.grid_vip)
		print(response)
		sleep(03)
		if bool(re.match("\"zone_rp*.*rpz.com/default",str(response))):
                        print(" Create rpz zone success")
                else:
                        print(" Create rpz zone unsuccess")
                        assert False
		print("\nTest Case 02 Executed Successfully")

            @pytest.mark.run(order=03)
            def test_03_Adding_rpz_zone_to_threat_analytics(self):
		print("\n===================================")
		print(" Adding rpz zone to threat analytics ")
		print("=====================================")
                threat_ref = ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics", grid_vip=config.grid_vip)
		print(threat_ref)
                ref = json.loads(threat_ref)[0]['_ref']
		rpz_ref = ib_NIOS.wapi_request('GET',object_type="zone_rp?fqdn=rpz.com",grid_vip=config.grid_vip)
		print(rpz_ref)
		ref1 = json.loads(rpz_ref)[0]['_ref']
                data = {"dns_tunnel_black_list_rpz_zones": [ref1]}
                output = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(output)
		sleep(03)
		if "grid:threatanalytics" in output:
			assert True
			print(" adding rpz zone to the threat analytics is success ")
		else:
			assert False
			print(" adding rpz zone to the threat analytics is unsuccess ")
		print("\nTest Case 03 Executed Successfully")

            @pytest.mark.run(order=04)
            def test_04_Enable_threat_analytics_service(self):
		print("\n=================================")
		print(" Enabling threat analytics service ")
		print("===================================")
                threat_analytics_ref = ib_NIOS.wapi_request('GET', object_type="member:threatanalytics", grid_vip=config.grid_vip)
		print(threat_analytics_ref)
                ref = json.loads(threat_analytics_ref)[0]['_ref']
                data = {"enable_service": True}
                response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
		sleep(05)
		if bool(re.match("\"member:threatanalytics*.*"+config.grid_fqdn,str(response))):
                        print(" Threat analytics service starting is success ")
                else:
                        print(" Threat analytics service starting is unsuccess ")
                        assert False
		print("\nTest Case 04 Executed Successfully")


##############
## Clean UP ##
##############

            @pytest.mark.run(order=05)
            def test_05_Disable_threat_analytics_service(self):
                print("\n==================================")
                print(" Disabling threat analytics service ")
                print("====================================")
                threat_analytics_ref = ib_NIOS.wapi_request('GET', object_type="member:threatanalytics", grid_vip=config.grid_vip)
                print(threat_analytics_ref)
                ref = json.loads(threat_analytics_ref)[0]['_ref']
                data = {"enable_service": False}
                response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
		sleep(05)
                if bool(re.match("\"member:threatanalytics*.*"+config.grid_fqdn,str(response))):
                        print(" Threat analytics service disabling is success ")
                else:
                        print(" Threat analytics service disabling is unsuccess ")
                        assert False
                print("\nTest Case 05 Executed Successfully")

            @pytest.mark.run(order=06)
            def test_06_Removing_rpz_zone_from_threat_analytics(self):
                print("\n=======================================")
                print(" Removing rpz zone from threat analytics ")
                print("=========================================")
                threat_ref = ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics", grid_vip=config.grid_vip)
                print(threat_ref)
                ref = json.loads(threat_ref)[0]['_ref']
                data = {"dns_tunnel_black_list_rpz_zones": []}
                output = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(output)
		sleep(03)
                if "grid:threatanalytics" in output:
                        assert True
                        print(" removing rpz zone to the threat analytics is success ")
                else:
                        assert False
                        print(" removing rpz zone to the threat analytics is unsuccess ")
                print("\nTest Case 06 Executed Successfully")


            @pytest.mark.run(order=07)
            def test_07_Delete_rpz_zone(self):
                print("\n=================")
                print(" Deleting RPZ zone ")
                print("===================")
		rpz_ref = ib_NIOS.wapi_request('GET', object_type="zone_rp?fqdn=rpz.com", grid_vip=config.grid_vip)
		print(rpz_ref)
		ref = json.loads(rpz_ref)[0]['_ref']
                response = ib_NIOS.wapi_request('DELETE', object_type=ref,grid_vip=config.grid_vip)
                print(response)
		sleep(05)
                if bool(re.match("\"zone_rp*.*rpz.com/default",str(response))):
                        print(" Delete rpz zone is success")
                else:
                        print(" Delete rpz zone is unsuccess")
                        assert False
                print("\nTest Case 07 Executed Successfully")



#!/usr/bin/env python

__author__ = "Prasad K"
__email__  = "pkondisetty@infoblox.com"
__NIOSSPT_11703__ = 'WAPI call returning 500 server error when adding multiple zone associations in one call'
########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master with member                                                          #
#  2. Licenses : DNS, DHCP, Grid, NIOS                                                 #
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

class NIOSSPT_11703(unittest.TestCase):

        @pytest.mark.run(order=1)
        def test_01_Add_Authoritative_zone(self):
                print("\n============================================\n")
                print("Create Authoritative Zone")
                print("\n============================================\n")
                data = {"fqdn": "test.com","grid_primary": [{"name":config.grid_fqdn,"stealth":False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                print(response)
		sleep(05)
                if bool(re.match("\"zone_auth*.*test.com/default",str(response))):
                        print("Authoritative zone addition success")
                else:
                        print("Authoritative zone addition unsuccess")
                        assert False
                print("Test Case 01 Execution Completed")

        @pytest.mark.run(order=2)
        def test_02_Add_DTC_Server(self):
                print("\n============================================\n")
                print("Create Authoritative Zone")
                print("\n============================================\n")
                data = {"host": config.grid_vip,"name": "a.1.test.com"}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
                print(response)
                sleep(05)
                if bool(re.match("\"dtc:server*.*a.1.test.com",str(response))):
                        print("DTC server addition success")
                else:
                        print("DTC server addition unsuccess")
                        assert False
                print("Test Case 02 Execution Completed")

        @pytest.mark.run(order=3)
        def test_03_Add_DTC_Pool(self):
                print("\n=========================\n")
                print(" Adding DTC Pool in the grid ")
                print("\n=========================\n")
		server_ref = ib_NIOS.wapi_request('GET',object_type="dtc:server?name=a.1.test.com")
		print(server_ref)
		dtc_server_ref=json.loads(server_ref)[0]['_ref']
		print(dtc_server_ref)
                data = {"lb_preferred_method": "ROUND_ROBIN","name": "dtc_pool","servers": [{"ratio": 1,"server": dtc_server_ref}]}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:pool", fields=json.dumps(data))
                print(response)
		sleep(05)
                if bool(re.match("\"dtc:pool*.*dtc_pool",str(response))):
                        print("DTC pool addition success")
                else:
                        print("DTC pool addition unsuccess")
                        assert False
		print("Test Case 03 Execution Completed")

        @pytest.mark.run(order=4)
        def test_04_Add_DTC_lbdn(self):
                print("\n=========================\n")
                print(" Adding DTC lbdn in the grid ")
                print("\n=========================\n")
                pool_ref = ib_NIOS.wapi_request('GET',object_type="dtc:pool?name=dtc_pool")
                print(pool_ref)
                pool_ref=json.loads(pool_ref)[0]['_ref']
		print(pool_ref)
		zone_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth?fqdn=test.com")
                print(zone_ref)
                zone_ref=json.loads(zone_ref)[0]['_ref']
                print(zone_ref)
                data = {"auth_zones": [zone_ref],"lb_method": "ROUND_ROBIN","name": "dtc_lbdn","patterns": ["a.1.test.com"],"pools": [{"pool": pool_ref,"ratio": 1}]}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:lbdn", fields=json.dumps(data))
                print(response)
		sleep(05)
                if bool(re.match("\"dtc:lbdn*.*dtc_lbdn",str(response))):
                        print("DTC lbdn addition success")
                else:
                        print("DTC lbdn addition unsuccess")
                        assert False
                print("Test Case 04 Execution Completed")

        @pytest.mark.run(order=5)
        def test_05_Validate_DTC_lbdn(self):
                print("\n============================================\n")
                print("Create Authoritative Zone")
                print("\n============================================\n")
                dtc_lbdn = ib_NIOS.wapi_request('GET',object_type="dtc:lbdn?fqdn=a.1.test.com")
                print(dtc_lbdn)
		sleep(05)
		data = '"name": "dtc_lbdn"'
		if data in dtc_lbdn:
			assert True
			print("Able to retrieve the name of an LBDN from a pattern (a.1.test.com - fqdn) using WAPI")
		else:
			print("Unable to retrieve the name of an LBDN from a pattern (a.1.test.com - fqdn) using WAPI")
			assert False
		print("Test Case 05 Execution Completed")

#################
## Clean UP #####
#################

        @pytest.mark.run(order=6)
        def test_06_DELETE_DTC_lbdn(self):
                print("\n===============\n")
                print(" Deleting DTC lbdn ")
                print("\n===============\n")
                dtc_lbdn = ib_NIOS.wapi_request('GET',object_type="dtc:lbdn")
		print(dtc_lbdn)
		dtc_lbdn_ref =  json.loads(dtc_lbdn)[0]['_ref']
		print(dtc_lbdn_ref)
		delete_dtc_lbdn = ib_NIOS.wapi_request('DELETE',ref=dtc_lbdn_ref)
		print(delete_dtc_lbdn)
		sleep(05)
                if bool(re.match("\"dtc:lbdn*.*dtc_lbdn",str(delete_dtc_lbdn))):
                        print("DTC lbdn removal success")
                else:
                        print("DTC lbdn removal unsuccess")
                        assert False
		print("Test Case 06 Execution Completed")

        @pytest.mark.run(order=7)
        def test_07_DELETE_DTC_Pool(self):
                print("\n===============\n")
                print(" Deleting DTC Pool ")
                print("\n===============\n")
                dtc_pool = ib_NIOS.wapi_request('GET',object_type="dtc:pool")
                print(dtc_pool)
                dtc_pool_ref =  json.loads(dtc_pool)[0]['_ref']
                print(dtc_pool_ref)
                delete_dtc_pool = ib_NIOS.wapi_request('DELETE',ref=dtc_pool_ref)
                print(delete_dtc_pool)
		sleep(05)
                if bool(re.match("\"dtc:pool*.*dtc_pool",str(delete_dtc_pool))):
                        print("DTC pool removal success")
                else:
                        print("DTC pool removal unsuccess")
                        assert False
		print("Test Case 07 Execution Completed")

        @pytest.mark.run(order=8)
        def test_08_DELETE_DTC_Server(self):
                print("\n=================\n")
                print(" Deleting DTC Server ")
                print("\n=================\n")
                dtc_server = ib_NIOS.wapi_request('GET',object_type="dtc:server")
                print(dtc_server)
                dtc_server_ref =  json.loads(dtc_server)[0]['_ref']
                print(dtc_server_ref)
                delete_dtc_server = ib_NIOS.wapi_request('DELETE',ref=dtc_server_ref)
                print(delete_dtc_server)
		sleep(05)
                if bool(re.match("\"dtc:server*.*a.1.test.com",str(delete_dtc_server))):
                        print("DTC server removal success")
                else:
                        print("DTC server removal unsuccess")
                        assert False
		print("Test Case 08 Execution Completed")

        @pytest.mark.run(order=9)
        def test_09_DELETE_Authoritative_Zone(self):
                print("\n=========================\n")
                print(" Deleting Authoritative Zone ")
                print("\n=========================\n")
                zone_auth = ib_NIOS.wapi_request('GET',object_type="zone_auth")
                print(zone_auth)
                zone_auth_ref =  json.loads(zone_auth)[0]['_ref']
                print(zone_auth_ref)
                delete_zone_auth = ib_NIOS.wapi_request('DELETE',ref=zone_auth_ref)
                print(delete_zone_auth)
		sleep(05)
                if bool(re.match("\"zone_auth*.*test.com/default",str(delete_zone_auth))):
                        print("Authoritative zone removal success")
                else:
                        print("Authoritative zone removal unsuccess")
                        assert False
                print("Test Case 09 Execution Completed")


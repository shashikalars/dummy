#!/usr/bin/env python

__author__ = "Prasad K"
__email__  = "pkondisetty@infoblox.com"
__NIOSSPT_11798__ = 'GUI shows incorrect status for LBDN when all servers associated with the pool have a GREEN status'
########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master with member                                                          #
#  2. Licenses : DNS, DHCP, Grid, NIOS, DTC                                            #
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

class NIOSSPT_11798(unittest.TestCase):

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
                data = {"host": config.grid_vip,"name": "dtc_server"}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
                print(response)
                sleep(05)
                if bool(re.match("\"dtc:server*.*dtc_server",str(response))):
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
		dtc_server_ref = ib_NIOS.wapi_request('GET',object_type="dtc:server?name=dtc_server")
		print(dtc_server_ref)
		dtc_server_ref=json.loads(dtc_server_ref)[0]['_ref']
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
			assert True
                        print("DTC lbdn addition success")
                else:
                        print("DTC lbdn addition unsuccess")
                        assert False
		sleep(60)
                print("Test Case 04 Execution Completed")

	@pytest.mark.run(order=5)
    	def test_05_Enable_and_Validate_DNS_service_Enabled(self):	
		print("\n=========================\n")
        	print(" Enabling and Validating DNS service enabled ")
		print("\n=========================\n")
		data = {"enable_dns": True}
		master_ref = ib_NIOS.wapi_request('GET',object_type="member:dns")
		ref = json.loads(master_ref)[0]['_ref']
		response = ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
		print(response)
                print("Restart services")
                get_ref =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(get_ref)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices", fields=json.dumps(data),grid_vip=config.grid_vip)
                print("wait for 25sec")
                sleep(60)
		response = ib_NIOS.wapi_request('GET',"member:dns?host_name="+config.grid_fqdn+"&_return_fields%2B=enable_dns&_return_as_object=1",grid_vip=config.grid_vip)
		print(response)
		data = '"enable_dns": true'
		if data in response:
			assert True
		else:
			assert False
        	print("Test Case 05 Execution Completed")

        @pytest.mark.run(order=6)
        def test_06_Validate_DTC_Server_Health_Status(self):
                print("\n============================================\n")
                print(" Validating DTC Server Health Status ")
                print("\n============================================\n")
		sleep(60)
                dtc_server = ib_NIOS.wapi_request('GET',object_type="dtc:server?name=dtc_server&_return_fields%2B=health&_return_as_object=1")
                print(dtc_server)
		dtc_server = dtc_server.replace("\n","").replace(" ","")
		data = '"health":{"availability":"GREEN"'
		if data in dtc_server:
			assert True
			print("DTC Server health status is GREEN")
		else:
			print("DTC Server health status is Not GREEN")
			assert False
		print("Test Case 06 Execution Completed")

        @pytest.mark.run(order=7)
        def test_07_Validate_DTC_Pool_Health_Status(self):
                print("\n============================================\n")
                print(" Validating DTC Pool Health Status ")
                print("\n============================================\n")
		sleep(60)
                dtc_pool = ib_NIOS.wapi_request('GET',object_type="dtc:pool?name=dtc_pool&_return_fields%2B=health&_return_as_object=1")
                print(dtc_pool)
                dtc_pool = dtc_pool.replace("\n","").replace(" ","")
                data = '"health":{"availability":"GREEN"'
                if data in dtc_pool:
                        assert True
                        print("DTC Pool health status is GREEN")
                else:
                        print("DTC Pool health status is Not GREEN")
			assert False
                print("Test Case 07 Execution Completed")

        @pytest.mark.run(order=8)
        def test_08_Validate_DTC_lbdn_Health_Status(self):
                print("\n============================================\n")
                print(" Validating DTC lbdn Health Status ")
                print("\n============================================\n")
		sleep(60)
                dtc_lbdn = ib_NIOS.wapi_request('GET',object_type="dtc:lbdn?name=dtc_lbdn&_return_fields%2B=health&_return_as_object=1")
                print(dtc_lbdn)
                dtc_lbdn = dtc_lbdn.replace("\n","").replace(" ","")
                data = '"health":{"availability":"GREEN"'
                if data in dtc_lbdn:
                        assert True
                        print("DTC lbdn health status is GREEN")
                else:
                        print("DTC lbdn health status is Not GREEN")
			assert False
                print("Test Case 08 Execution Completed")


#################
## Clean UP #####
#################

        @pytest.mark.run(order=9)
        def test_09_Disable_DNS_service_and_DELETE_DTC_lbdn(self):
                print("\n===============\n")
                print(" Disabling DNS service and deleting DTC lbdn ")
                print("\n===============\n")
                data = {"enable_dns": False}
                master_ref = ib_NIOS.wapi_request('GET',object_type="member:dns")
                ref = json.loads(master_ref)[0]['_ref']
                response = ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
                print(response)
		sleep(10)
                dtc_lbdn = ib_NIOS.wapi_request('GET',object_type="dtc:lbdn")
		print(dtc_lbdn)
		dtc_lbdn_ref =  json.loads(dtc_lbdn)[0]['_ref']
		print(dtc_lbdn_ref)
		delete_dtc_lbdn = ib_NIOS.wapi_request('DELETE',ref=dtc_lbdn_ref)
		print(delete_dtc_lbdn)
		sleep(05)
                if bool(re.match("\"dtc:lbdn*.*dtc_lbdn",str(delete_dtc_lbdn))):
			assert True
                        print("DTC lbdn removal success")
                else:
                        print("DTC lbdn removal unsuccess")
                        assert False
		print("Test Case 09 Execution Completed")

        @pytest.mark.run(order=10)
        def test_10_DELETE_DTC_Pool(self):
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
			assert True
                        print("DTC pool removal success")
                else:
                        print("DTC pool removal unsuccess")
                        assert False
		print("Test Case 10 Execution Completed")

        @pytest.mark.run(order=11)
        def test_11_DELETE_DTC_Server(self):
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
                if bool(re.match("\"dtc:server*.*dtc_server",str(delete_dtc_server))):
			assert True
                        print("DTC server removal success")
                else:
                        print("DTC server removal unsuccess")
                        assert False
		print("Test Case 11 Execution Completed")

        @pytest.mark.run(order=12)
        def test_12_DELETE_Authoritative_Zone(self):
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
			assert True
                        print("Authoritative zone removal success")
                else:
                        print("Authoritative zone removal unsuccess")
                        assert False
                print("Test Case 12 Execution Completed")


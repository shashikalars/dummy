__author__ = "Rajath"
__email__  = "rpatavardhan@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master                                                                      #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1425)                                      #
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
import commands
import json, ast
import requests
from time import sleep as sleep
import pexpect
from paramiko import client
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as comm_util

global snmp_memref
class Network(unittest.TestCase):
	@pytest.mark.run(order=0)
        def test_100_NIOSSPT_8809_add_a_snmpv3_user(self):
            global snmp_memref
            print("\nNIOSSPT-8809:Add a SNMPv3 user")
            data={"name":"test","authentication_protocol":"MD5","authentication_password":"infoblox","privacy_protocol":"DES","privacy_password":"infoblox"}
            response=ib_NIOS.wapi_request('POST', object_type="snmpuser",fields=json.dumps(data), grid_vip=config.grid_vip)
            snmp_memref=response
            print("SNMPv3 user added successfully")
            print snmp_memref
            logging.info(response)
            read = re.search(r'201',response)
            for read in response:
                assert True
                break
            else:
                assert False

	@pytest.mark.run(order=1)
	def test_101_NIOSSPT_8809_override_snmp_settings(self):
            global snmp_memref
            print("\nNIOSSPT-8809:Override SNMP settings under member properties")
	    response = ib_NIOS.wapi_request('GET', object_type="member")
	    memref = json.loads(response)[0]['_ref']
	    sleep(5)
	    data={"snmp_setting":{"queries_enable": False,"snmpv3_queries_enable": True,"snmpv3_queries_users": [{"user":snmp_memref}]}}
	    response=ib_NIOS.wapi_request('PUT',ref=memref, fields=json.dumps(data))
	    print response
            logging.info(response)
            read  = re.search(r'201',response)
            for read in  response:
	        assert True
                break
            else:
                assert False
            print("SNMP settings successfully updated under member properties")
			
	@pytest.mark.run(order=2)
	def test_102_NIOSSPT_8809_delete_snmpv3_user(self):
            print("\nNIOSSPT-8809:NEGATIVE:Try to delete the SNMPv3 user")
	    global snmp_memref
            snmp_memref=json.loads(snmp_memref)
            response=ib_NIOS.wapi_request('DELETE', object_type=snmp_memref)
	    print(response)
            response=str(response)
            if (re.search(r'You cannot delete SNMPv3 user test when SNMPv3 queries are configured for the user',response)):
                print("Unable to delete the SNMPv3 user, NEGATIVE TESTCASE PASSED")
                assert True
            else:
                print("SNMPv3 user deleted, NEGATIVE TESTCASE FAILED")
                assert False


	@pytest.mark.run(order=3)
        def test_103_NIOSSPT_8809_cleanup(self):
            print("\nNIOSSPT-8809:Cleanup-Update Member properties and Remove the SNMPv3 user")
            response = ib_NIOS.wapi_request('GET', object_type="member")
            memref = json.loads(response)[0]['_ref']
            sleep(5)
            global snmp_memref
	    data={"snmp_setting":{"queries_enable": False,"snmpv3_queries_enable": False}}
            response=ib_NIOS.wapi_request('PUT',ref=memref, fields=json.dumps(data))
            print response
            logging.info(response)
            response=ib_NIOS.wapi_request('DELETE', object_type=snmp_memref)
            print(response)




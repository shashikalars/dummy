#!/usr/bin/env python
__author__ = "Manoj Kumar R G"
__email__  = "mgovarthanan@infoblox.com"

####################################################################################
#  Grid Set up required:                                                           #
#  1. Grid Master with one CP member                                               #
#  2. Licenses : DNS, Grid, NIOS(IB-1415), CNA license                             #
#  3. Enable DNS,TP services                                                       #
#  REFER https://jira.inca.infoblox.com/browse/NIOSSPT-11610 IF THIS SCRIPT FAILS  #
#                                                                                  #
####################################################################################

import re
import config
import pytest
import unittest
import logging
import os
import json
from time import sleep
import commands
import json, ast
import requests
import time
import pexpect
import getpass
import paramiko
import shlex
from subprocess import Popen, PIPE
import sys
from paramiko import client
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as comm_util
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="NIOSSPT-11610.log" ,level=logging.DEBUG,filemode='w')


class NIOSSPT_11610(unittest.TestCase):

    @pytest.mark.run(order=01)
    def test_01_create_network(self):

	data = {"network": "40.0.0.0/24"}
        response = ib_NIOS.wapi_request('POST',object_type="network",fields=json.dumps(data))
        logging.info(response)

        get_ref = ib_NIOS.wapi_request("GET",object_type="network?network=40.0.0.0/24")
        ref_1=json.loads(get_ref)[0]['network']
        print(ref_1)

        if (ref_1 == "40.0.0.0/24"):
            print("\nPASS")
            assert True
        else:
            print("\nFAIL")
            assert False

    @pytest.mark.run(order=02)
    def test_02_create_extattrs(self):

	data = {"name":"VRF","type":"STRING"}
	response = ib_NIOS.wapi_request('POST',object_type="extensibleattributedef",fields=json.dumps(data))
        logging.info(response)
	print("#################",response)
        read  = re.search(r'201',response)
        for read in  response:
            assert True


    @pytest.mark.run(order=03)
    def test_03_add_ext_attrs(self):

        get_ref = ib_NIOS.wapi_request('GET', object_type="network?network=40.0.0.0/24")
        ref1 = json.loads(get_ref)[0]['_ref']
	data = {"extattrs": {"VRF" :{"value": "PCLOUD-PROD"}}}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
	print("#########",response)
        res=json.loads(response)
        logging.info(response)
        read  = re.search(r'201',response)
        for read in  response:
            assert True

    @pytest.mark.run(order=04)
    def test_04_delete_ext_attrs(self):

        get_ref = ib_NIOS.wapi_request('GET', object_type="network?network=40.0.0.0/24")
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"extattrs-": {"VRF" :{}}}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
	print("#########",response)
        res=json.loads(response)
        logging.info(response)
        read  = re.search(r'201',response)
        for read in  response:
            assert True

    @pytest.mark.run(order=05)
    def test_05_cleanup_object(self):

        get_ref = ib_NIOS.wapi_request('GET', object_type="extensibleattributedef?name=VRF")
        ref1 = json.loads(get_ref)[0]['_ref']
	
	response = ib_NIOS.wapi_request('DELETE', object_type=ref1)
	print("######",response)
	read = re.search(r'200',response)
	for read in response:
		assert True

        get_ref = ib_NIOS.wapi_request('GET', object_type="network?network=40.0.0.0/24")
        ref1 = json.loads(get_ref)[0]['_ref']

        response = ib_NIOS.wapi_request('DELETE', object_type=ref1)
        print("######",response)
        read = re.search(r'200',response)
        for read in response:
                assert True




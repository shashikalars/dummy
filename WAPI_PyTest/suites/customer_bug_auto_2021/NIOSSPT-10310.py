#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
# Grid Set up required:                                                     #
#  1. Licenses : Grid DNS, DHCP, Grid, NIOS (IB-V1415)                      #
#############################################################################
import os
import re
import config
import pytest
import unittest
import logging
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import shlex
from time import sleep
from subprocess import Popen, PIPE
import pexpect
import paramiko
from scapy import *
from scapy.utils import RawPcapReader
from scapy.all import *
import shutil
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv

logging.basicConfig(filename='niosspt10310.log', filemode='w', level=logging.DEBUG)

class NIOSSPT_10310(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_000_create_a_lom_user_with_password_length_less_than_4(self):
        logging.info("Create a LOM user called 'test' with password length below 4")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        logging.info(get_ref)
        for ref in json.loads(get_ref):
            
            data = {"name": "Infoblox","lom_users":[{"disable": False,"name": "test","role": "OPERATOR","password":"te"}]}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            logging.info(response)
            print(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    if "Password must be 4-20 characters long" in response[1]:
                        logging.info("Success: Did not Create a LOM user called 'test' with password length below 4")
                        assert True
                    
            else:
                logging.info("Failure: Create a LOM user called 'test' with password length below 4:Password must be 4-20 characters long.")
                assert False
                              

    @pytest.mark.run(order=2)
    def test_001_create_a_lom_user_with_password_length_more_than_20(self):
        logging.info("Create a LOM user called 'test' with password length above 20")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        logging.info(get_ref)
        for ref in json.loads(get_ref):
            
            data = {"name": "Infoblox","lom_users":[{"disable": False,"name": "test","role": "OPERATOR","password":"test12345678912924567890"}]}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            logging.info(response)
            print(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    if "Password must be 4-20 characters long" in response[1]:
                        logging.info("Success: Did not Create a LOM user called 'test' with password length above 20")
                        assert True
                    
            else:
                logging.info("Failure: Create a LOM user called 'test' with password length above 20")
                assert False
                
  
    @pytest.mark.run(order=3)
    def test_002_create_a_lom_user_with_password_length_is_zero(self):
        logging.info("Create a LOM user called 'test' with password length is 'zero'")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        logging.info(get_ref)
        for ref in json.loads(get_ref):
            
            data = {"name": "Infoblox","lom_users":[{"disable": False,"name": "test","role": "OPERATOR","password":""}]}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            logging.info(response)
            print(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    if "Password must be 4-20 characters long" in response[1]:
                        logging.info("Success: Did not Create a LOM user called 'test' with password length is 'zero'")
                        assert True
                          
                else:
                    logging.info("Failure: Created a LOM user called 'test' with password length is 'zero'")
                    assert False
                

    @pytest.mark.run(order=4)
    def test_003_create_a_lom_user_without_name_field(self):
        logging.info("Create a LOM user called 'test' without a name field ")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        logging.info(get_ref)
        for ref in json.loads(get_ref):
            
            data = {"name": "Infoblox","lom_users":[{"disable": False,"role": "OPERATOR","password":""}]}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            logging.info(response)
            print(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    if "Required field missing: name" in response[1]:
                        logging.info("Success: Did not Create a LOM user called 'test', because name field is missing")
                        assert True
                          
            else:
                logging.info("Failure: Did not Create a LOM user called 'test', because name field is missing")
                assert False
                
    @pytest.mark.run(order=5)
    def test_004_create_a_lom_user_with_password_length_between_4_to_15(self):
        logging.info("Create a LOM user called 'test' with password length between 4 to 15")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        logging.info(get_ref)
        for ref in json.loads(get_ref):
            
            data = {"name": "Infoblox","lom_users":[{"disable": False,"name": "test","role": "OPERATOR","password":"test"}]}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            logging.info(response)
            print(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    logging.info("Failure: Did not Create a LOM user called 'test' with password length between 4 to 15")
                    assert False      
            else:
                logging.info("Success: Created a LOM user called 'test' with password length between 4 to 15")
                assert True

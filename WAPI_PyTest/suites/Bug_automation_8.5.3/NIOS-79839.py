#!/usr/bin/env python
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. SA configuration                                                      #
#  2. License : Grid                                                        #
#############################################################################

import re
import config
import pytest
import unittest
import logging
import subprocess
import os
import sys
import json
import commands
import json, ast
import requests
from time import sleep as sleep
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util

class NIOS_79839_(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_error_message_as_expected_in_grid_setup_wizard_saml_auth_type_non_superuser(self):
        data={"admin_groups": ["saml-group"],"auth_type": "LOCAL","name": "saml12","password":"1"}
        response = ib_NIOS.wapi_request('POST',object_type="adminuser",fields=json.dumps(data))
        print(response)
        if type(response) == tuple and 'It must contain 4-64 characters' in response:
            print("Success: should get error message as expected in grid setup wizard")
            assert True

    @pytest.mark.run(order=2)
    def test_001_error_message_as_expected_in_grid_setup_wizard_local_auth_type_non_superuser(self):
        data={"admin_groups": ["saml-group"],"auth_type": "SAML_LOCAL","name": "saml12","password":"1"}
        response = ib_NIOS.wapi_request('POST',object_type="adminuser",fields=json.dumps(data))
        print(response)
        if type(response) == tuple and 'It must contain 4-64 characters' in response:
            print("Success: should get error message as expected in grid setup wizard")
            assert True

    @pytest.mark.run(order=3)
    def test_002_error_message_as_expected_in_grid_setup_wizard_saml_auth_type_superuser(self):
        data={"admin_groups": ["admin-group"],"auth_type": "LOCAL","name": "saml12","password":"1"}
        response = ib_NIOS.wapi_request('POST',object_type="adminuser",fields=json.dumps(data))
        print(response)
        if type(response) == tuple and 'It must contain 4-64 characters' in response:
            print("Success: should get error message as expected in grid setup wizard")
            assert True

    @pytest.mark.run(order=4)
    def test_003_error_message_as_expected_in_grid_setup_wizard_local_auth_type_superuser(self):
        data={"admin_groups": ["admin-group"],"auth_type": "SAML_LOCAL","name": "saml12","password":"1"}
        response = ib_NIOS.wapi_request('POST',object_type="adminuser",fields=json.dumps(data))
        print(response)
        if type(response) == tuple and 'It must contain 4-64 characters' in response:
            print("Success: should get error message as expected in grid setup wizard")
            assert True

    @pytest.mark.run(order=5)
    def test_004_error_message_as_expected_in_userprofile_wizard(self):
        
        print("Error message as expected in userprofile wizard")
        data={"old_password":"infoblox","password":"1"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="userprofile", grid_vip=config.grid_vip)
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[0]['_ref']
        print(ref)

        response = ib_NIOS.wapi_request('PUT',ref=ref, object_type="userprofile",fields=json.dumps(data))
        print(response)
        if type(response) == tuple and 'It must contain 4-64 characters' in response:
            if response[0]==400 or response[0]==401:
                print("Success: should get error message as expected in userprofile setup wizard")
                assert True



    @pytest.mark.run(order=6)
    def test_005_error_message_as_expected_in_grid_shared_secret(self):
        print("Error message as expected in grid wizard shared secret")
        data={"name": "Infoblox","secret":"1"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[0]['_ref']
        print(ref)

        response = ib_NIOS.wapi_request('PUT',ref=ref, object_type="grid",fields=json.dumps(data))
        print(response)
        if type(response) == tuple and 'The shared secret is not between 4 and 64 characters' in response[1]:
            if response[0]==400 or response[0]==401:
                print("Success: should get error message as expected in grid wizard shared secret")
                assert True

        else:
            print("Failure: Logged a bug, the bug number is NIOS-80833")
            assert False

    @pytest.mark.run(order=7)
    def test_006_error_message_as_expected_in_radius_shared_secret(self):
        print("Error message as expected in radius authenticationshared secret")
        data={"name":"rad","servers":[{"address": "10.120.23.105","shared_secret":"1"}]}

        response = ib_NIOS.wapi_request('POST', object_type="radius:authservice",fields=json.dumps(data))
        print(response)
        if type(response) == tuple and 'The shared secret is not between 4 and 64 characters' in response[1]:
            if response[0]==400 or response[0]==401:
                print("Success: should get error message as expected in radius shared secret")
                assert True

        else:
            print("Failure: Logged a bug, the bug number is NIOS-80835")
            assert False
    '''
    @pytest.mark.run(order=8)
    def test_007_error_message_as_expected_in_certificate_shared_secret(self):
        
        print("Upload Cisco ISE Server CA Certificate")
        dir_name="."
        base_filename="myCA_cert.pem"
        token = common_util.generate_token_from_file(dir_name,base_filename)
        print (token)
        data = {"token": token, "certificate_usage":"EAP_CA"}
        
        response = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=uploadcertificate")

        data = { "auto_populate_login": "S_DN_CN","name": "cert","ocsp_check": "DISABLED","user_match_type": "AUTO_MATCH","client_cert_subject" : "grid","ca_certificates":["cacertificate/b25lLmVhcF9jYV9jZXJ0JDAuNWJmYmE0NGY2ZjJmZjU1YmI1MzkyYWIzYWMzZTk2NTVkM2ViYmNmMzdkMWFkNTAxMWIzZDFhNTI1N2MzMzdkOWZjZGUyODk0MGI3ZmM3MzA3OTI1NjcyMjAyNWQ4M2U0ODc5OWMwYTBmODMyOTQ4OTBkYzBhNzc3ZTRkNGI5ZDA:CN%3D%22ca.gnidoni-vm.inca.infoblox.com%22"]}
        response = ib_NIOS.wapi_request('POST', object_type="certificate:authservice", fields=json.dumps(data), grid_vip=config.grid_vip)
        print (response)
        sleep(30)
        print(response)
        if type(response) == tuple and 'It must contain 4-64 characters' in response:
            if response[0]==400 or response[0]==401:
                print("Success: should get error message as expected in Certificate authentication")
                assert True

        else:
            assert False
    '''
    '''    
    @pytest.mark.run(order=3)
    def test_002_error_message_as_expected_in_ftpuser_wizard(self):
        print("Error message as expected in ftpuser wizard")
        data={"admin_groups": ["saml-group"],"username": "saml12","password":"1"}
        response = ib_NIOS.wapi_request('POST', object_type="ftpuser",fields=json.dumps(data))
        print(response)
        if type(response) == tuple and 'It must contain 4-64 characters' in response:
            if response[0]==400 or response[0]==401:
                print("Success: should get error message as expected in ftpuser setup wizard")
                assert True
    '''

    @pytest.mark.run(order=9)
    def test_008_clenup_object(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="radius:authservice", grid_vip=config.grid_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
            print(response)
            if type(response) == tuple:
                assert True



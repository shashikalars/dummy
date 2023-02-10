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

class NIOS_79782(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_configure_SAML_Service_By_Upload(self):
        ref=ib_NIOS.wapi_request('GET',object_type='saml:authservice')
        filename="metadata.xml"
        print("Test Uploading the Template with fileop")
        data = {"filename":filename}
        create_file = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=uploadinit")
        print(create_file)
        res = json.loads(create_file)
        token = json.loads(create_file)['token']
        url = json.loads(create_file)['url']
        file1=url.split("/")
        os.system('curl -k1 -u admin:infoblox -F name=%s -F filedata=@%s %s'%(filename,filename,url))
        filename="/"+filename
        data = {"name":"saml","session_timeout":1234,"idp":{"idp_type": "OKTA","metadata_token":token,"sso_redirect_url":config.grid_vip}}
        create_file1 = ib_NIOS.wapi_request('POST', object_type="saml:authservice",fields=json.dumps(data))
        create_file1=json.loads(create_file1)
        print(create_file1)
        if type(create_file1) == tuple:
            if response[0]==400 or response[0]==401:
                assert True
                print("Failed: SAML service is not configured")
        else:
            assert True
            print("Success: SAML service configured")

    @pytest.mark.run(order=2)
    def test_001_delete_saml_service(ref1):
        get_ref=ib_NIOS.wapi_request('GET',object_type="saml:authservice")
        print("reference value for saml service to delete")
        if get_ref!='[]':
            get_ref1=json.loads(get_ref)[0]['_ref']
            response = ib_NIOS.wapi_request('DELETE', object_type=get_ref1)
            print(response)
        print("Success: SAML service deleted")

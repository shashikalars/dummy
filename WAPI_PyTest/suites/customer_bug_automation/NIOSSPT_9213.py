#!/usr/bin/env python
__author__ = "Chetan Kumar PG"
__email__  = "cpg@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Stand alone Grid Master                                               #
#  2. Licenses : DNS, DHCP, Grid                                            #
#  3. Enable DHCP services                                                  #
#############################################################################

import re
import os
import config
import pytest
import unittest
import logging
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="niosspt_9213.log" ,level=logging.DEBUG,filemode='w')

def display_msg(x=""):
    """ 
    Additional function.
    """
    logging.info(x)
    print(x)

class NIOSSPT_9213(unittest.TestCase):
    
    @pytest.mark.run(order=1)
    def test_000_setup(self):
        """
        setup method: Used for configuring pre-required configs.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case setup Started            |")
        display_msg("------------------------------------------------")
        pass
    
    @pytest.mark.run(order=2)
    def test_001_Create_IPV4_Network_Template_with_extattrs(self):
        """
        Create IPV4 Network Template.
        Add an extensible attribute 'Building' with empty value.
        Verify that the template is created with no errors.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 1 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Create an IPV4 Network Template niosspt_9213_template with external attribute 'Building' with no value")
        data = {"name": "niosspt_9213_template",
                "netmask": 8,
                "extattrs": {"Building": {"value":""}}
                }
        response = ib_NIOS.wapi_request('POST',object_type="networktemplate",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                assert False
        display_msg("-----------Test Case 1 Execution Completed------------")
    
    @pytest.mark.run(order=3)
    def test_002_Get_IPV4_Network_Template_(self):
        """
        Check whether you are able to GET the Network Template created using WAPI.
        Expected: Should be able to succesfully get the network template object.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 2 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("GET IPV4 Network Template with extattrs as return fields")
        response = ib_NIOS.wapi_request('GET',object_type="networktemplate?_return_fields=extattrs")
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                assert False
        display_msg("-----------Test Case 2 Execution Completed------------")
    
    @pytest.mark.run(order=4)
    def test_003_Modify_IPV4_Network_Template(self):
        """
        Check whether you are able to modify the Network Template using WAPI.
        Expected: Should be able to succesfully modify the object.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 3 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Modify IPV4 Network Template niosspt_9213_template")
        get_ref = ib_NIOS.wapi_request('GET',object_type="networktemplate?")
        display_msg(get_ref)
        ref1 = json.loads(get_ref)[0]["_ref"]
        data = {"netmask": 22}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                assert False
        display_msg("-----------Test Case 3 Execution Completed------------")
    
    @pytest.mark.run(order=-1)
    def test_cleanup(self):
        """
        cleanup method: Delete all the objects created from this script.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|          Test Case cleanup Started           |")
        display_msg("------------------------------------------------")
        get_ref = ib_NIOS.wapi_request('GET',object_type="networktemplate")
        display_msg(get_ref)
        response = ib_NIOS.wapi_request('DELETE', ref=json.loads(get_ref)[0]["_ref"])
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                assert False
        display_msg("-----------Test Case cleanup Completed------------")

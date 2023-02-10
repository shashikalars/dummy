#!/usr/bin/env python
__author__ = "Chetan Kumar PG"
__email__  = "cpg@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Grid Master + Grid Member                                             #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415)                           #
#  3. Enable DNS services                                                   #
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
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="niosspt_9212.log" ,level=logging.DEBUG,filemode='w')

def display_msg(x=""):
    """ 
    Additional function.
    """
    logging.info(x)
    print(x)

class NIOSSPT_9212(unittest.TestCase):
    
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
    def test_001_Create_Auth_NSG_add_member(self):
        """
        1. Create Authorative Name Server Group.
        2. Add Grid member as Grid primary.
        3. Verify that the NSG is created
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 1 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Create an authorative Name Server Group and add member as grid primary")
        data = {"name": "niosspt_9212_auth",
                "grid_primary": [{"name": config.grid_member1_fqdn,"stealth": False}]}
        response = ib_NIOS.wapi_request('POST',object_type="nsgroup",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                assert False
        display_msg("-----------Test Case 1 Execution Completed------------")
    
    @pytest.mark.run(order=3)
    def test_002_Create_Forwarding_member_NSG_add_member(self):
        """
        1. Create forwarding member Name Server Group.
        2. Add Grid member as forwarding member server.
        3. Verify that the NSG is created
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 2 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Create a forwarding member Name Server Group and add member as forwarding member server")
        data = {"name": "niosspt_9212_forwarding",
                "forwarding_servers": [{"name": config.grid_member1_fqdn}]}
        response = ib_NIOS.wapi_request('POST',object_type="nsgroup:forwardingmember",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                assert False
        display_msg("-----------Test Case 2 Execution Completed------------")
    
    #@pytest.mark.run(order=4)
    @pytest.mark.skip
    def test_003_Modify_DNS_object_through_PAPI(self):
        """
        1. Modify Infoblox::Grid::DNS object using PAPI.
        2. In the script modify_grid_dns_object.pl , it is trying to modify resolver_query_timeout
        3. Verify that the object is modified successfully.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 3 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Modify Grid::DNS object using PAPI")
        cmd = 'perl '+os.getcwd()+'/modify_grid_dns_object_9212.pl '+config.grid_vip+' '+config.grid_fqdn
        output = os.popen(cmd).read()
        display_msg(output)
        if not 'Modified Grid DNS Object successfully' in output:
            assert False
        display_msg("-----------Test Case 3 Execution Completed------------")
    
    @pytest.mark.run(order=5)
    def test_004_Check_for_all_the_NSGs(self):
        """
        1. GET all the Name Server Group using WAPI.
        2. Verify that none of the NSGs are deleted.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 4 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Verify that none of the NSGs are deleted")
        get_ref = ib_NIOS.wapi_request('GET',object_type="nsgroup")
        display_msg(get_ref)
        if get_ref == '[]':
            assert False
        if type(get_ref) == tuple:
            if get_ref[0]==400 or get_ref[0]==401:
                assert False
        
        get_ref = ib_NIOS.wapi_request('GET',object_type="nsgroup:forwardingmember")
        display_msg(get_ref)
        if get_ref == '[]':
            assert False
        if type(get_ref) == tuple:
            if get_ref[0]==400 or get_ref[0]==401:
                assert False
        display_msg("-----------Test Case 4 Execution Completed------------")
    
    @pytest.mark.run(order=-1)
    def test_cleanup(self):
        """
        cleanup method: Delete all the objects created from this script.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|          Test Case cleanup Started           |")
        display_msg("------------------------------------------------")
        get_ref = ib_NIOS.wapi_request('GET',object_type="nsgroup")
        display_msg(get_ref)
        res = json.loads(get_ref)
        for obj in res:
            ref1 = obj['_ref']
            response = ib_NIOS.wapi_request('DELETE', ref=ref1)
            display_msg(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    assert False
        
        get_ref = ib_NIOS.wapi_request('GET',object_type="nsgroup:forwardingmember")
        display_msg(get_ref)
        res = json.loads(get_ref)
        for obj in res:
            ref1 = obj['_ref']
            response = ib_NIOS.wapi_request('DELETE', ref=ref1)
            display_msg(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    assert False
        display_msg("-----------Test Case cleanup Completed------------")

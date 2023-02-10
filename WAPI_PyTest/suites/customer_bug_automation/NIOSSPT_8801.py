#!/usr/bin/env python
__author__ = "Chetan Kumar PG"
__email__  = "cpg@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Grid Master + Grid Member                                             #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415)                           #
#  3. Enable DNS,DHCP services                                              #
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
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="niosspt_8801.log" ,level=logging.DEBUG,filemode='w')

def display_msg(x=""):
    """ 
    Additional function.
    """
    logging.info(x)
    print(x)

class NIOSSPT_8801(unittest.TestCase):
    
    @pytest.mark.run(order=1)
    def test_000_setup(self):
        """
        setup method: Used for configuring pre-required configs.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case setup Started            |")
        display_msg("------------------------------------------------")
        get_ref = ib_NIOS.wapi_request('GET',object_type="member")
        display_msg(get_ref)
        ref = json.loads(get_ref)
        member_ref = ref[1]["_ref"]
        display_msg("Make Grid member as the Grid Master Candidate")
        response = ib_NIOS.wapi_request('PUT', object_type=member_ref, fields=json.dumps({"master_candidate":True}))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Make Grid member as the Grid Master Candidate")
                assert False
        display_msg("Sleeping 120 seconds for the GMC to come up")
        sleep(120)
        pass
    
    @pytest.mark.run(order=2)
    def test_001_ro_api_access_to_GMC(self):
        """
        Set Read Only API access to True for Grid Master Candidate.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 1 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Set Read Only API access to True for GMC")
        get_ref = ib_NIOS.wapi_request('GET',object_type="member")
        display_msg(get_ref)
        ref = json.loads(get_ref)
        member_ref = ref[1]["_ref"]
        response = ib_NIOS.wapi_request('PUT',object_type=member_ref,fields=json.dumps({"enable_ro_api_access":True}))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Set Read Only API access to True for GMC")
                assert False
        display_msg("Sleeping 120 seconds for the GMC to come up")
        sleep(120)
        display_msg("-----------Test Case 1 Execution Completed------------")

    @pytest.mark.run(order=3)
    def test_002_add_IPV4_Filters_through_GMC(self):
        """
        Add IPV4 MAC Address Filter niosspt_8801 through GMC.
        Verify that adding the IPV4 MAC Address Filter is failed,
        since Read-Only API is enbaled on GMC
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 2 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Add IPV4 MAC Address Filter niosspt_8801 through GMC")
        response = ib_NIOS.wapi_request('POST',object_type="filtermac",fields=json.dumps({"name":"niosspt_8801"}),grid_vip=config.grid_member1_vip)
        display_msg(response)
        if type(response) == tuple:
            display_msg("Error Code: "+str(response[0]))
            display_msg("Error message: "+json.loads(response[1])["text"])
            if not json.loads(response[1])["text"] == "Only read-only API access supported":
                display_msg("Failure: Unexpected Error message while adding IPV4 MAC Address Filter through GMC")
                assert False
        else:
            display_msg("Failure: Add IPV4 MAC Address Filter niosspt_8801 through GMC")
            assert False
        display_msg("-----------Test Case 2 Execution Completed------------")

    @pytest.mark.run(order=4)
    def test_003_Add_IPV4_filters_through_grid_master(self):
        """
        Add IPV4 MAC Address Filter niosspt_8801_gm through Grid Master.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 3 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Add IPV4 MAC Address Filter niosspt_8801_gm through Grid Master")
        response = ib_NIOS.wapi_request('POST',object_type="filtermac",fields=json.dumps({"name":"niosspt_8801_gm"}))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Add IPV4 MAC Address Filter niosspt_8801_gm through Grid Master")
            assert False

        display_msg("-----------Test Case 3 Execution Completed------------")

    @pytest.mark.run(order=5)
    def test_004_read_IPV4_filters_through_GMC(self):
        """
        GET IPV4 MAC Address Filter niosspt_8801_gm through GMC using WAPI.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 4 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Get IPV4 MAC Address Filter niosspt_8801_gm through GMC")
        get_ref = ib_NIOS.wapi_request('GET', object_type='filtermac', grid_vip=config.grid_member1_vip)
        display_msg(get_ref)
        if type(get_ref) == tuple:
            display_msg("Failure: Get IPV4 MAC Address Filter through GMC")
            assert False
        flag =False
        for ref in json.loads(get_ref):
            if ref['name'] == 'niosspt_8801_gm':
                flag = True
        if not flag:
            display_msg("Failure: Get IPV4 MAC Address Filter niosspt_8801_gm through GMC")
            assert False
                
        display_msg("-----------Test Case 4 Execution Completed------------")

    @pytest.mark.run(order=6)
    def test_005_disable_ro_api_access_to_GMC(self):
        """
        Set Read Only API access to False for Grid Master Candidate.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 5 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Set Read Only API access to False for GMC")
        get_ref = ib_NIOS.wapi_request('GET',object_type="member")
        display_msg(get_ref)
        ref = json.loads(get_ref)
        member_ref = ref[1]["_ref"]
        response = ib_NIOS.wapi_request('PUT',object_type=member_ref,fields=json.dumps({"enable_ro_api_access":False}))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Set Read Only API access to False for GMC")
                assert False
        display_msg("Sleeping 120 seconds for the GMC to come up")
        sleep(120)
        display_msg("-----------Test Case 5 Execution Completed------------")

    @pytest.mark.run(order=7)
    def test_006_read_IPV4_filters_through_GMC(self):
        """
        GET IPV4 MAC Address Filter niosspt_8801_gm through GMC using WAPI. Should fail
        Read Only API access should be set to False
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 6 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Get IPV4 MAC Address Filter niosspt_8801_gm through GMC")
        get_ref = ib_NIOS.wapi_request('GET', object_type='filtermac', grid_vip=config.grid_member1_vip)
        display_msg(get_ref)
        if 'if page does not refresh in 10 seconds' not in get_ref:
            display_msg("Failure: Get operation successful")
            assert False
                
        display_msg("-----------Test Case 6 Execution Completed------------")

    @pytest.mark.run(order=-1)
    def test_cleanup(self):
        """
        cleanup method: Delete all the objects created from this script.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|          Test Case cleanup Started           |")
        display_msg("------------------------------------------------")
        display_msg("Reverting back the Grid Member Candidate setting")
        get_ref = ib_NIOS.wapi_request('GET',object_type="member")
        display_msg(get_ref)
        ref = json.loads(get_ref)
        member_ref = ref[1]["_ref"]
        response = ib_NIOS.wapi_request('PUT',object_type=member_ref,fields=json.dumps({"enable_ro_api_access":False}))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Set Read Only API access to False for GMC")
                assert False
        response = ib_NIOS.wapi_request('PUT', object_type=member_ref, fields=json.dumps({"master_candidate":False}))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Reverting back the Grid Member Candidate setting")
                assert False
        display_msg("Sleeping 120 seconds for the GMC to come up")
        sleep(120)
        
        display_msg("Deleting the IPV4 MAC Address Filters")
        get_ref = ib_NIOS.wapi_request('GET', object_type='filtermac')
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('DELETE', ref=ref['_ref'])
            display_msg(response)
            if type(response) == tuple:
                display_msg('Failure: Deleting the IPV4 MAC Address Filters')
                assert False
        
        display_msg("-----------Test Case cleanup Completed------------")

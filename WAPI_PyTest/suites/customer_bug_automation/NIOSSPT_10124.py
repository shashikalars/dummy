#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Chetan Kumar PG"
__email__  = "cpg@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Grid Master                                                           #
#  2. Licenses : DNS, DHCP(enabled), Grid                                   #
#############################################################################

import os
import re
import csv
import config
import pytest
import unittest
import logging
import json
import pexpect
import paramiko
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as ib_TOKEN
#from ib_utils.log_capture import log_action as log
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="niosspt_10124.log" ,level=logging.DEBUG,filemode='w')
   
def restart_services(grid=config.grid_vip):
    """
    Restart Services
    """
    display_msg("Restart services")
    get_ref =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=grid)
    ref = json.loads(get_ref)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices", fields=json.dumps(data),grid_vip=grid)
    sleep(20)

def display_msg(x=""):
    """ 
    Additional function.
    """
    logging.info(x)
    print(x)

class NIOSSPT_10124(unittest.TestCase):
    
    @pytest.mark.run(order=1)
    def test_000_setup(self):
        """
        setup method: Used for configuring pre-required configs.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case setup Started            |")
        display_msg("------------------------------------------------")
        
        '''Add extensible attributes'''
        display_msg("Add extensible attributes")
        data1 = {"name":"location_short_name",
                 "type":"STRING",
                 "flags":"I",
                 "descendants_action":{"option_without_ea": "INHERIT","option_with_ea": "INHERIT"}}
        data2 = {"name":"location_status",
                 "type":"STRING",
                 "flags":"I",
                 "descendants_action":{"option_without_ea": "INHERIT","option_with_ea": "INHERIT"}}
        data3 = {"name":"location_type",
                 "type":"STRING",
                 "flags":"I",
                 "descendants_action":{"option_without_ea": "INHERIT","option_with_ea": "INHERIT"}}
        data = [{"method":"POST","object":"extensibleattributedef","data":data1},
                {"method":"POST","object":"extensibleattributedef","data":data2},
                {"method":"POST","object":"extensibleattributedef","data":data3}]
        response = ib_NIOS.wapi_request('POST', object_type='request', fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Add extensible attributes")
            assert False

        display_msg("---------Test Case setup Execution Completed----------")

    @pytest.mark.run(order=2)
    def test_001_create_network_container_1(self):
        """
        Create network container 100.100.100.0/24
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 1 Execution Started           |")
        display_msg("----------------------------------------------------")

        '''Create network container 100.100.100.0/24'''
        display_msg("Create network container 100.100.100.0/24")
        data = {"network":"100.100.100.0/24"}
        response = ib_NIOS.wapi_request('POST', object_type="networkcontainer", fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Create network container")
            assert False
        
        display_msg("-----------Test Case 1 Execution Completed------------")

    @pytest.mark.run(order=3)
    def test_002_create_network_container_2(self):
        """
        Create network container 100.100.0.0/16
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 2 Execution Started           |")
        display_msg("----------------------------------------------------")

        '''Create network container 100.100.0.0/16'''
        display_msg("Create network container 100.100.0.0/16")
        data = {"network":"100.100.0.0/16"}
        response = ib_NIOS.wapi_request('POST', object_type="networkcontainer", fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Create network container")
            assert False
        
        display_msg("-----------Test Case 2 Execution Completed------------")

    @pytest.mark.run(order=4)
    def test_003_create_network_container_3(self):
        """
        Create network container 100.0.0.0/8
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 3 Execution Started           |")
        display_msg("----------------------------------------------------")

        '''Create network container 100.0.0.0/8'''
        display_msg("Create network container 100.0.0.0/8")
        data = {"network":"100.0.0.0/8"}
        response = ib_NIOS.wapi_request('POST', object_type="networkcontainer", fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Create network container")
            assert False
        
        display_msg("-----------Test Case 3 Execution Completed------------")

    @pytest.mark.run(order=5)
    def test_004_add_extensible_attributes_to_network_container_1(self):
        """
        Add extensible attributes to network container 100.0.0.0/8
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 4 Execution Started           |")
        display_msg("----------------------------------------------------")

        '''Add extensible attributes to network container 100.0.0.0/8'''
        display_msg("Add extensible attributes to network container 100.0.0.0/8")
        get_ref = ib_NIOS.wapi_request('GET', object_type='networkcontainer')
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            if ref["network"] == "100.0.0.0/8":
                data = {"extattrs": {"location_short_name": {"value": "testdeinze",
                                                             "descendants_action": {"option_without_ea": "NOT_INHERIT","option_with_ea": "INHERIT"}},
                                     "location_status": {"value": "open",
                                                         "descendants_action": {"option_without_ea": "NOT_INHERIT","option_with_ea": "INHERIT"}},
                                     "location_type": {"value": "shop",
                                                       "descendants_action": {"option_without_ea": "NOT_INHERIT","option_with_ea": "INHERIT"}}}}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                display_msg(response)
                if type(response) == tuple:
                    display_msg("Failure: Add extensible attributes to network container")
                    assert False
        
        display_msg("-----------Test Case 4 Execution Completed------------")

    @pytest.mark.run(order=6)
    def test_005_add_extensible_attributes_to_network_container_2(self):
        """
        Add extensible attributes to network container 100.100.0.0/16
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 5 Execution Started           |")
        display_msg("----------------------------------------------------")

        '''Add extensible attributes to network container 100.100.0.0/16'''
        display_msg("Add extensible attributes to network container 100.100.0.0/16")
        get_ref = ib_NIOS.wapi_request('GET', object_type='networkcontainer')
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            if ref["network"] == "100.100.0.0/16":
                data = {"extattrs": {"location_short_name": {"value": "testdeinze",
                                                             "descendants_action": {"option_without_ea": "INHERIT","option_with_ea": "INHERIT"}},
                                     "location_status": {"value": "open",
                                                         "descendants_action": {"option_without_ea": "NOT_INHERIT","option_with_ea": "INHERIT"}},
                                     "location_type": {"value": "shop1",
                                                       "descendants_action": {"option_without_ea": "INHERIT","option_with_ea": "INHERIT"}}}}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                display_msg(response)
                if type(response) == tuple:
                    display_msg("Failure: Add extensible attributes to network container")
                    assert False
        
        display_msg("-----------Test Case 5 Execution Completed------------")

    @pytest.mark.run(order=7)
    def test_006_add_extensible_attributes_to_network_container_3(self):
        """
        Add extensible attributes to network container 100.100.100.0/24
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 6 Execution Started           |")
        display_msg("----------------------------------------------------")

        '''Add extensible attributes to network container 100.100.100.0/24'''
        display_msg("Add extensible attributes to network container 100.100.100.0/24")
        get_ref = ib_NIOS.wapi_request('GET', object_type='networkcontainer')
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            if ref["network"] == "100.100.100.0/24":
                data = {"extattrs": {"location_short_name": {"value": "testdeinze2",
                                                             "descendants_action": {"option_without_ea": "INHERIT","option_with_ea": "INHERIT"}},
                                     "location_status": {"value": "open2",
                                                         "descendants_action": {"option_without_ea": "INHERIT","option_with_ea": "INHERIT"}},
                                     "location_type": {"value": "shop2",
                                                       "descendants_action": {"option_without_ea": "INHERIT","option_with_ea": "INHERIT"}}}}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                display_msg(response)
                if type(response) == tuple:
                    display_msg("Failure: Add extensible attributes to network container")
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
        
        display_msg("Delete network containers")
        get_ref = ib_NIOS.wapi_request('GET',object_type="networkcontainer")
        display_msg(get_ref)
        for obj in json.loads(get_ref):
            if obj['network'] == '100.0.0.0/8':
                ref1 = obj['_ref']
                response = ib_NIOS.wapi_request('DELETE', ref=ref1)
                display_msg(response)
                if type(response) == tuple:
                    display_msg("Failure: Delete network containers")
                    assert False

        display_msg("Delete extensible attributes")
        get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef")
        display_msg(get_ref)
        for obj in json.loads(get_ref):
            if obj['name'] == 'location_short_name' or obj['name'] == 'location_status' or obj['name'] == 'location_type':
                ref1 = obj['_ref']
                response = ib_NIOS.wapi_request('DELETE', ref=ref1)
                display_msg(response)
                if type(response) == tuple:
                    display_msg("Failure: Delete extensible attributes")
                    assert False
        
        display_msg("-----------Test Case cleanup Completed------------")


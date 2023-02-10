#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Chetan Kumar PG"
__email__  = "cpg@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Grid Master + Discovery member                                        #
#  2. Licenses : DNS, DHCP, Grid - GM, Grid,Discovery - DM                  #
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
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="niosspt_10086.log" ,level=logging.DEBUG,filemode='w')
   
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

class NIOSSPT_10086(unittest.TestCase):
    
    @pytest.mark.run(order=1)
    def test_000_setup(self):
        """
        setup method: Used for configuring pre-required configs.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case setup Started            |")
        display_msg("------------------------------------------------")
        
        '''Add snmpv1v2_credentials as public'''
        display_msg("Edit Grid Discovery Properties")
        get_ref = ib_NIOS.wapi_request('GET', object_type='discovery:gridproperties')
        display_msg(get_ref)
        discovery_grid_properties = {"snmpv1v2_credentials":[{"community_string":"public"}]}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(discovery_grid_properties))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Edit Grid Discovery Properties")
            assert False
        
        '''Enable Discovery service'''
        display_msg("Enable Discovery service")
        get_ref = ib_NIOS.wapi_request('GET', object_type='discovery:memberproperties')
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            if ref["discovery_member"] == config.grid_member1_fqdn:
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps({"enable_service":True}))
                display_msg(response)
                if type(response) == tuple:
                    display_msg("Failure: Enable Discovery Service")
                    assert False
                restart_services()
        
        display_msg("Sleeping 5 minutes for Discovery service to come up")
        sleep(300)

        display_msg("---------Test Case setup Execution Completed----------")

    @pytest.mark.run(order=2)
    def test_001_create_network_and_enable_discovery(self):
        """
        Create network 10.40.16.0/24 and add discovery member.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 1 Execution Started           |")
        display_msg("----------------------------------------------------")

        '''Create network 10.40.16.0/24 and enable immediate discovery'''
        display_msg("Create network 10.40.16.0/24 with discovery member")
        data = {"network":"10.40.16.0/24",
                "use_enable_discovery":True,
                "discovery_member":config.grid_member1_fqdn,
                "enable_discovery":True,
                "enable_immediate_discovery":True}
        response = ib_NIOS.wapi_request('POST', object_type='network', fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Create network 10.40.16.0/24 with discovery member")
            assert False
        
        display_msg("Sleeping 15 minutes for Discovery to complete")
        sleep(1000)
        
        display_msg("-----------Test Case 1 Execution Completed------------")


    @pytest.mark.run(order=3)
    def test_002_verify_paging_result(self):
        """
        curl -k -u admin:infoblox -X GET 
        'https://<ipaddress>/wapi/<wapiversion>/discovery:device?_paging=1&_return_as_object=1&_max_results=1&_return_fields%2B=interfaces.ifaddr_infos'
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 2 Execution Started           |")
        display_msg("----------------------------------------------------")

        '''Perform GET operation on the discovery device with return fields'''
        display_msg("Paging output - part 1")
        paging_data = "?_paging=1&_return_as_object=1&_max_results=1&_return_fields%2B=interfaces.ifaddr_infos"
        curl_cmd = "curl -k -u admin:infoblox -X GET 'https://"+config.grid_vip+"/wapi/v"+config.wapi_version+"/discovery:device"+paging_data+"'"
        display_msg(curl_cmd)
        #response = ib_NIOS.wapi_request('POST', object_type='discovery:device', params=paging_data)
        response = os.popen(curl_cmd).read()
        display_msg(response)
        if "Error" in response:
            display_msg("Failure: Paging output - part 1")
            assert False
        
        output = json.loads(response)
        page_id = output["next_page_id"]
        for address in output["result"]:
            display_msg(address["address"])
            if "interfaces" in address.keys():
                if "ifaddr_infos" in address["interfaces"][0].keys():
                    display_msg("ifaddr_infos is present in the page 1")
                    break
            display_msg("ifaddr_infos is not present in the page 1")
            assert False
        
        '''Page 2'''
        display_msg("Paging output - part 2")
        paging_data = "?_paging=1&_return_as_object=1&_max_results=1&_return_fields%2B=interfaces.ifaddr_infos&_page_id="+page_id
        curl_cmd = "curl -k -u admin:infoblox -X GET 'https://"+config.grid_vip+"/wapi/v"+config.wapi_version+"/discovery:device"+paging_data+"'"
        display_msg(curl_cmd)
        #response2 = ib_NIOS.wapi_request('POST', object_type='discovery:device', params=paging_data)
        response2 = os.popen(curl_cmd).read()
        display_msg(response2)
        if "Error" in response2:
            display_msg("Failure: Paging output - part 2")
            assert False
        
        output2 = json.loads(response2)
        #page_id = output2["next_page_id"]
        for address in output2["result"]:
            display_msg(address["address"])
            if "interfaces" in address.keys():
                if "ifaddr_infos" in address["interfaces"][0].keys():
                    display_msg("ifaddr_infos is present in the page 2")
                    break
            display_msg("ifaddr_infos is not present in the page 2")
            assert False
        
        display_msg("-----------Test Case 2 Execution Completed------------")

    @pytest.mark.run(order=-1)
    def test_cleanup(self):
        """
        cleanup method: Delete all the objects created from this script.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|          Test Case cleanup Started           |")
        display_msg("------------------------------------------------")
        
        display_msg("Delete network")
        get_ref = ib_NIOS.wapi_request('GET',object_type="network")
        display_msg(get_ref)
        for obj in json.loads(get_ref):
            if obj['network'] == '10.40.16.0/24':
                ref1 = obj['_ref']
                response = ib_NIOS.wapi_request('DELETE', ref=ref1)
                display_msg(response)
                if type(response) == tuple:
                    display_msg("Failure: Delete network")
                    assert False
        
        '''Disable Discovery service'''
        display_msg("Disable Discovery service")
        get_ref = ib_NIOS.wapi_request('GET', object_type='discovery:memberproperties')
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            if ref["discovery_member"] == config.grid_member1_fqdn:
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps({"enable_service":False}))
                display_msg(response)
                if type(response) == tuple:
                    display_msg("Failure: Disable Discovery Service")
                    assert False
                restart_services()
        
        display_msg("Sleeping 5 minutes for Discovery service to go down")
        sleep(300)
        
        display_msg("-----------Test Case cleanup Completed------------")

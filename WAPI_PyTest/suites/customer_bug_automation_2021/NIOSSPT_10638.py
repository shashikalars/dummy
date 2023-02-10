#!/usr/bin/env python
__author__ = "Chetan Kumar PG"
__email__  = "cpg@infoblox.com"

####################################################################################
#  Grid Set up required:                                                           #
#  1. Stand alone Grid Master                                                      #
#  2. Licenses : DNS, Grid, NIOS(IB_1415)                                          #
#  3. Enable DNS services                                                          #
#  REFER https://jira.inca.infoblox.com/browse/NIOSSPT-10638 IF THIS SCRIPT FAILS  #
#                                                                                  #
####################################################################################

import os
import re
import config
import pytest
import unittest
import logging
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="niosspt_10638.log" ,level=logging.DEBUG,filemode='w')

def display_msg(x=""):
    """ 
    Additional function.
    """
    logging.info(x)
    print(x)

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

class NIOSSPT_10638(unittest.TestCase):
    
    @pytest.mark.run(order=1)
    def test_000_setup(self):
        """
        setup method: Used for configuring pre-required configs.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case setup Started            |")
        display_msg("------------------------------------------------")
        
        '''"Enable DNS service"'''
        display_msg("Enable DNS service")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns')
        display_msg(get_ref)
        ref = json.loads(get_ref)[0]
        response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps({"enable_dns":True}))
        if type(response) == tuple:
            display_msg("Failure: Enable DNS Service")
            assert False
        restart_services()
        
        '''Validation'''
        display_msg("Start validation")
        response_val = ib_NIOS.wapi_request('GET',object_type="member:dns", params="?_return_fields=enable_dns")
        display_msg(response_val)
        if not json.loads(response_val)[0]["enable_dns"] == True:
            display_msg("Validation failed")
            assert False
        display_msg("Validation passed")
        
        display_msg("---------Test Case setup Execution Completed----------")
    
    @pytest.mark.run(order=2)
    def test_001_add_authoritative_forward_mapping_zone(self):
        """
        Add an Authorative Forward mapping Zone niosspt_10638.com.
        Add Grid master as Grid primary.
        Verify that the Zone is created with no errors.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 1 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Add an authoritative fwd mapping zone niosspt_10638.com")
        data = {"fqdn": "niosspt_10638.com", 
                "view":"default", 
                "grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Add an authoritative fwd mapping zone niosspt_10638.com")
            assert False
        
        restart_services(config.grid_vip)
        
        '''Validation'''
        display_msg("Start validation")
        response_val = ib_NIOS.wapi_request('GET',object_type="zone_auth", params="?fqdn=niosspt_10638.com")
        display_msg(response_val)
        if not json.loads(response_val) or type(response_val) == tuple:
            display_msg("Validation failed")
            assert False
        display_msg("Validation passed")
        
        display_msg("-----------Test Case 1 Execution Completed------------")

    @pytest.mark.run(order=3)
    def test_002_add_a_record_1(self):
        """
        Add A record a.sub.niosspt_10638.com.
        Add IPV4 address (example : 10.1.1.1).
        Verify that the A record is created with no errors.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 2 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Create A record a.sub.niosspt_10638.com")
        data = {"name": "a.sub.niosspt_10638.com",
                "ipv4addr":"10.1.1.1"}
        response = ib_NIOS.wapi_request('POST',object_type="record:a",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Create A record a.sub.niosspt_10638.com")
            assert False
        
        '''Validation'''
        display_msg("Start validation")
        response_val = ib_NIOS.wapi_request('GET',object_type="record:a", params="?name=a.sub.niosspt_10638.com")
        display_msg(response_val)
        if not json.loads(response_val) or type(response_val) == tuple:
            display_msg("Validation failed")
            assert False
        display_msg("Validation passed")
        
        display_msg("-----------Test Case 2 Execution Completed------------")

    @pytest.mark.run(order=4)
    def test_003_dig_a_record_1(self):
        """
        Perform dig operation on A record a.sub.niosspt_10638.com
        dig @config.grid_vip a.sub.niosspt_10638.com
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 3 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Perform dig operation on A record a.sub.niosspt_10638")
        dig_cmd = 'dig @'+config.grid_vip+' a.sub.niosspt_10638.com'
        result = os.popen(dig_cmd).read()
        response = result.split('\n')
        answer = False
        pattern = False 
        match_line = "a.sub.niosspt_10638.com.\s+\d+\s+IN\s+A\s+10.1.1.1"
        for line in response:
            display_msg(line)
            if answer and not pattern:
                match = re.match(match_line, line)
                if match:
                    pattern = True
                    break
            if 'ANSWER SECTION' in line:
                answer = True
        if not answer or not pattern:
            display_msg("Failure: Perform dig query")
            assert False
        
        display_msg("-----------Test Case 3 Execution Completed------------")

    @pytest.mark.run(order=5)
    def test_004_add_forward_zone(self):
        """
        Add a Forward Zone as sub zone sub.niosspt_10638.com.
        Add dummy name server.
        Verify that the Zone is created with no errors.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 4 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Add forward zone sub.niosspt_10638.com")
        data = {"fqdn": "sub.niosspt_10638.com", 
                "view":"default", 
                "forward_to": [{"name": "infoblox.localdomain","address": "1.1.1.1"}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_forward",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Add forward zone sub.niosspt_10638.com")
            assert False
        
        restart_services(config.grid_vip)
        
        '''Validation'''
        display_msg("Start validation")
        response_val = ib_NIOS.wapi_request('GET',object_type="zone_forward", params="?fqdn=sub.niosspt_10638.com")
        display_msg(response_val)
        if not json.loads(response_val) or type(response_val) == tuple:
            display_msg("Validation failed")
            assert False
        display_msg("Validation passed")
        
        display_msg("-----------Test Case 4 Execution Completed------------")

    @pytest.mark.run(order=6)
    def test_005_dig_a_record_1_repeat(self):
        """
        Perform dig operation on A record a.sub.niosspt_10638.com
        dig @config.grid_vip a.sub.niosspt_10638.com
        Refer https://jira.inca.infoblox.com/browse/NIOSSPT-10638 if this case fails
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 5 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Perform dig operation on A record a.sub.niosspt_10638")
        dig_cmd = 'dig @'+config.grid_vip+' a.sub.niosspt_10638.com'
        result = os.popen(dig_cmd).read()
        response = result.split('\n')
        answer = False
        pattern = False 
        match_line = "a.sub.niosspt_10638.com.\s+\d+\s+IN\s+A\s+10.1.1.1"
        for line in response:
            display_msg(line)
            if answer and not pattern:
                match = re.match(match_line, line)
                if match:
                    pattern = True
                    break
            if 'ANSWER SECTION' in line:
                answer = True
        if not answer or not pattern:
            display_msg("Expected Failure: Perform dig query")
            assert True
        else:
            display_msg("Unexpected Pass: Perform dig query")
            display_msg("Refer https://jira.inca.infoblox.com/browse/NIOSSPT-10638 if this case fails")
            assert False
        
        display_msg("-----------Test Case 5 Execution Completed------------")

    @pytest.mark.run(order=7)
    def test_006_validate_a_record_1(self):
        """
        Validate A record a.sub.niosspt_10638.com
        Refer https://jira.inca.infoblox.com/browse/NIOSSPT-10638 if this case fails
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 6 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Validate A record a.sub.niosspt_10638")
        response_val = ib_NIOS.wapi_request('GET',object_type="record:a", params="?name=a.sub.niosspt_10638.com")
        display_msg(response_val)
        if not json.loads(response_val) or type(response_val) == tuple:
            display_msg("Expected Failure: Validation failed")
            assert True
        else:
            display_msg("Unexpected Pass: Validation passed")
            display_msg("Refer https://jira.inca.infoblox.com/browse/NIOSSPT-10638 if this case fails")
            assert False
        
        display_msg("-----------Test Case 6 Execution Completed------------")

    @pytest.mark.run(order=8)
    def test_007_add_a_record_2(self):
        """
        Add A record a.sub2.niosspt_10638.com.
        Add IPV4 address (example : 10.1.1.2).
        Verify that the A record is created with no errors.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 7 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Create A record a.sub2.niosspt_10638.com")
        data = {"name": "a.sub2.niosspt_10638.com",
                "ipv4addr":"10.1.1.2"}
        response = ib_NIOS.wapi_request('POST',object_type="record:a",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Create A record a.sub2.niosspt_10638.com")
            assert False
        
        '''Validation'''
        display_msg("Start validation")
        response_val = ib_NIOS.wapi_request('GET',object_type="record:a", params="?name=a.sub2.niosspt_10638.com")
        display_msg(response_val)
        if not json.loads(response_val) or type(response_val) == tuple:
            display_msg("Validation failed")
            assert False
        display_msg("Validation passed")
        
        display_msg("-----------Test Case 7 Execution Completed------------")

    @pytest.mark.run(order=9)
    def test_008_dig_a_record_2(self):
        """
        Perform dig operation on A record a.sub2.niosspt_10638.com
        dig @config.grid_vip a.sub2.niosspt_10638.com
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 8 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Perform dig operation on A record a.sub2.niosspt_10638")
        dig_cmd = 'dig @'+config.grid_vip+' a.sub2.niosspt_10638.com'
        result = os.popen(dig_cmd).read()
        response = result.split('\n')
        answer = False
        pattern = False 
        match_line = "a.sub2.niosspt_10638.com.\s+\d+\s+IN\s+A\s+10.1.1.2"
        for line in response:
            display_msg(line)
            if answer and not pattern:
                match = re.match(match_line, line)
                if match:
                    pattern = True
                    break
            if 'ANSWER SECTION' in line:
                answer = True
        if not answer or not pattern:
            display_msg("Failure: Perform dig query")
            assert False
        
        display_msg("-----------Test Case 8 Execution Completed------------")

    @pytest.mark.run(order=10)
    def test_009_add_stub_zone(self):
        """
        Add a Stub Zone as sub zone sub2.niosspt_10638.com.
        Add dummy name server.
        Verify that the Zone is created with no errors.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 9 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Add Stub zone sub2.niosspt_10638.com")
        data = {"fqdn": "sub2.niosspt_10638.com", 
                "view":"default", 
                "stub_from": [{"name": "infoblox.localdomain","address": "1.1.1.2"}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_stub",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Add Stub zone sub2.niosspt_10638.com")
            assert False
        
        restart_services(config.grid_vip)
        
        '''Validation'''
        display_msg("Start validation")
        response_val = ib_NIOS.wapi_request('GET',object_type="zone_stub", params="?fqdn=sub2.niosspt_10638.com")
        display_msg(response_val)
        if not json.loads(response_val) or type(response_val) == tuple:
            display_msg("Validation failed")
            assert False
        display_msg("Validation passed")
        
        display_msg("-----------Test Case 9 Execution Completed------------")

    @pytest.mark.run(order=11)
    def test_010_dig_a_record_2_repeat(self):
        """
        Perform dig operation on A record a.sub2.niosspt_10638.com
        dig @config.grid_vip a.sub2.niosspt_10638.com
        Refer https://jira.inca.infoblox.com/browse/NIOSSPT-10638 if this case fails
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 10 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Perform dig operation on A record a.sub2.niosspt_10638")
        dig_cmd = 'dig @'+config.grid_vip+' a.sub2.niosspt_10638.com'
        result = os.popen(dig_cmd).read()
        response = result.split('\n')
        answer = False
        pattern = False 
        match_line = "a.sub2.niosspt_10638.com.\s+\d+\s+IN\s+A\s+10.1.1.2"
        for line in response:
            display_msg(line)
            if answer and not pattern:
                match = re.match(match_line, line)
                if match:
                    pattern = True
                    break
            if 'ANSWER SECTION' in line:
                answer = True
        if not answer or not pattern:
            display_msg("Expected Failure: Perform dig query")
            assert True
        else:
            display_msg("Unexpected Pass: Perform dig query")
            display_msg("Refer https://jira.inca.infoblox.com/browse/NIOSSPT-10638 if this case fails")
            assert False
        
        display_msg("-----------Test Case 10 Execution Completed------------")

    @pytest.mark.run(order=12)
    def test_011_validate_a_record_2(self):
        """
        Validate A record a.sub2.niosspt_10638.com
        Refer https://jira.inca.infoblox.com/browse/NIOSSPT-10638 if this case fails
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 11 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Validate A record a.sub2.niosspt_10638")
        response_val = ib_NIOS.wapi_request('GET',object_type="record:a", params="?name=a.sub2.niosspt_10638.com")
        display_msg(response_val)
        if not json.loads(response_val) or type(response_val) == tuple:
            display_msg("Expected Failure: Validation failed")
            assert True
        else:
            display_msg("Unexpected Pass: Validation passed")
            display_msg("Refer https://jira.inca.infoblox.com/browse/NIOSSPT-10638 if this case fails")
            assert False
        
        display_msg("-----------Test Case 11 Execution Completed------------")

    @pytest.mark.run(order=13)
    def test_012_add_a_record_3(self):
        """
        Add A record a.sub3.niosspt_10638.com.
        Add IPV4 address (example : 10.1.1.3).
        Verify that the A record is created with no errors.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 12 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Create A record a.sub3.niosspt_10638.com")
        data = {"name": "a.sub3.niosspt_10638.com",
                "ipv4addr":"10.1.1.3"}
        response = ib_NIOS.wapi_request('POST',object_type="record:a",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Create A record a.sub3.niosspt_10638.com")
            assert False
        
        '''Validation'''
        display_msg("Start validation")
        response_val = ib_NIOS.wapi_request('GET',object_type="record:a", params="?name=a.sub3.niosspt_10638.com")
        display_msg(response_val)
        if not json.loads(response_val) or type(response_val) == tuple:
            display_msg("Validation failed")
            assert False
        display_msg("Validation passed")
        
        display_msg("-----------Test Case 12 Execution Completed------------")

    @pytest.mark.run(order=14)
    def test_013_dig_a_record_3(self):
        """
        Perform dig operation on A record a.sub3.niosspt_10638.com
        dig @config.grid_vip a.sub3.niosspt_10638.com
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 13 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Perform dig operation on A record a.sub3.niosspt_10638")
        dig_cmd = 'dig @'+config.grid_vip+' a.sub3.niosspt_10638.com'
        result = os.popen(dig_cmd).read()
        response = result.split('\n')
        answer = False
        pattern = False 
        match_line = "a.sub3.niosspt_10638.com.\s+\d+\s+IN\s+A\s+10.1.1.3"
        for line in response:
            display_msg(line)
            if answer and not pattern:
                match = re.match(match_line, line)
                if match:
                    pattern = True
                    break
            if 'ANSWER SECTION' in line:
                answer = True
        if not answer or not pattern:
            display_msg("Failure: Perform dig query")
            assert False
        
        display_msg("-----------Test Case 13 Execution Completed------------")

    @pytest.mark.run(order=15)
    def test_014_add_delegated_zone(self):
        """
        Add a Delegated Zone as sub zone sub3.niosspt_10638.com.
        Add dummy name server.
        Verify that the Zone is created with no errors.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 14 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Add Delegated zone sub3.niosspt_10638.com")
        data = {"fqdn": "sub3.niosspt_10638.com", 
                "view":"default", 
                "delegate_to": [{"name": "infoblox.localdomain","address": "1.1.1.3"}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_delegated",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Add Delegated zone sub3.niosspt_10638.com")
            assert False
        
        restart_services(config.grid_vip)
        
        '''Validation'''
        display_msg("Start validation")
        response_val = ib_NIOS.wapi_request('GET',object_type="zone_delegated", params="?fqdn=sub3.niosspt_10638.com")
        display_msg(response_val)
        if not json.loads(response_val) or type(response_val) == tuple:
            display_msg("Validation failed")
            assert False
        display_msg("Validation passed")
        
        display_msg("-----------Test Case 14 Execution Completed------------")

    @pytest.mark.run(order=16)
    def test_015_dig_a_record_3_repeat(self):
        """
        Perform dig operation on A record a.sub3.niosspt_10638.com
        dig @config.grid_vip a.sub3.niosspt_10638.com
        Refer https://jira.inca.infoblox.com/browse/NIOSSPT-10638 if this case fails
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 15 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Perform dig operation on A record a.sub3.niosspt_10638")
        dig_cmd = 'dig @'+config.grid_vip+' a.sub3.niosspt_10638.com'
        result = os.popen(dig_cmd).read()
        response = result.split('\n')
        answer = False
        pattern = False 
        match_line = "a.sub3.niosspt_10638.com.\s+\d+\s+IN\s+A\s+10.1.1.3"
        for line in response:
            display_msg(line)
            if answer and not pattern:
                match = re.match(match_line, line)
                if match:
                    pattern = True
                    break
            if 'ANSWER SECTION' in line:
                answer = True
        if not answer or not pattern:
            display_msg("Expected Failure: Perform dig query")
            assert True
        else:
            display_msg("Unexpected Pass: Perform dig query")
            display_msg("Refer https://jira.inca.infoblox.com/browse/NIOSSPT-10638 if this case fails")
            assert False
        
        display_msg("-----------Test Case 15 Execution Completed------------")

    @pytest.mark.run(order=17)
    def test_016_validate_a_record_3(self):
        """
        Validate A record a.sub3.niosspt_10638.com
        Refer https://jira.inca.infoblox.com/browse/NIOSSPT-10638 if this case fails
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 16 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Validate A record a.sub3.niosspt_10638")
        response_val = ib_NIOS.wapi_request('GET',object_type="record:a", params="?name=a.sub3.niosspt_10638.com")
        display_msg(response_val)
        if not json.loads(response_val) or type(response_val) == tuple:
            display_msg("Expected Failure: Validation failed")
            assert True
        else:
            display_msg("Unexpected Pass: Validation passed")
            display_msg("Refer https://jira.inca.infoblox.com/browse/NIOSSPT-10638 if this case fails")
            assert False
        
        display_msg("-----------Test Case 16 Execution Completed------------")

    @pytest.mark.run(order=18)
    def test_017_add_a_record_4(self):
        """
        Add A record a.sub4.niosspt_10638.com.
        Add IPV4 address (example : 10.1.1.4).
        Verify that the A record is created with no errors.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 17 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Create A record a.sub4.niosspt_10638.com")
        data = {"name": "a.sub4.niosspt_10638.com",
                "ipv4addr":"10.1.1.4"}
        response = ib_NIOS.wapi_request('POST',object_type="record:a",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Create A record a.sub4.niosspt_10638.com")
            assert False
        
        '''Validation'''
        display_msg("Start validation")
        response_val = ib_NIOS.wapi_request('GET',object_type="record:a", params="?name=a.sub4.niosspt_10638.com")
        display_msg(response_val)
        if not json.loads(response_val) or type(response_val) == tuple:
            display_msg("Validation failed")
            assert False
        display_msg("Validation passed")
        
        display_msg("-----------Test Case 17 Execution Completed------------")

    @pytest.mark.run(order=19)
    def test_018_dig_a_record_4(self):
        """
        Perform dig operation on A record a.sub4.niosspt_10638.com
        dig @config.grid_vip a.sub4.niosspt_10638.com
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 18 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Perform dig operation on A record a.sub4.niosspt_10638")
        dig_cmd = 'dig @'+config.grid_vip+' a.sub4.niosspt_10638.com'
        result = os.popen(dig_cmd).read()
        response = result.split('\n')
        answer = False
        pattern = False 
        match_line = "a.sub4.niosspt_10638.com.\s+\d+\s+IN\s+A\s+10.1.1.4"
        for line in response:
            display_msg(line)
            if answer and not pattern:
                match = re.match(match_line, line)
                if match:
                    pattern = True
                    break
            if 'ANSWER SECTION' in line:
                answer = True
        if not answer or not pattern:
            display_msg("Failure: Perform dig query")
            assert False
        
        display_msg("-----------Test Case 18 Execution Completed------------")

    @pytest.mark.run(order=20)
    def test_019_add_disabled_forward_zone(self):
        """
        Add a Disabled on Creation Forward Zone as sub zone sub4.niosspt_10638.com.
        Add dummy name server.
        Verify that the Zone is created with no errors.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 19 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Add disabled forward zone sub4.niosspt_10638.com")
        data = {"fqdn": "sub4.niosspt_10638.com", 
                "view":"default",
                "disable": True,
                "forward_to": [{"name": "infoblox.localdomain","address": "1.1.1.4"}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_forward",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Add disabled forward zone sub4.niosspt_10638.com")
            assert False
        
        restart_services(config.grid_vip)
        
        '''Validation'''
        display_msg("Start validation")
        response_val = ib_NIOS.wapi_request('GET',object_type="zone_forward", params="?fqdn=sub4.niosspt_10638.com")
        display_msg(response_val)
        if not json.loads(response_val) or type(response_val) == tuple:
            display_msg("Validation failed")
            assert False
        display_msg("Validation passed")
        
        display_msg("-----------Test Case 19 Execution Completed------------")

    @pytest.mark.run(order=21)
    def test_020_dig_a_record_4_repeat(self):
        """
        Perform dig operation on A record a.sub4.niosspt_10638.com
        dig @config.grid_vip a.sub4.niosspt_10638.com
        Refer https://jira.inca.infoblox.com/browse/NIOSSPT-10638 if this case fails
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 20 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Perform dig operation on A record a.sub4.niosspt_10638")
        dig_cmd = 'dig @'+config.grid_vip+' a.sub4.niosspt_10638.com'
        result = os.popen(dig_cmd).read()
        response = result.split('\n')
        answer = False
        pattern = False 
        match_line = "a.sub4.niosspt_10638.com.\s+\d+\s+IN\s+A\s+10.1.1.4"
        for line in response:
            display_msg(line)
            if answer and not pattern:
                match = re.match(match_line, line)
                if match:
                    pattern = True
                    break
            if 'ANSWER SECTION' in line:
                answer = True
        if not answer or not pattern:
            display_msg("Expected Failure: Perform dig query")
            assert True
        else:
            display_msg("Unexpected Pass: Perform dig query")
            display_msg("Refer https://jira.inca.infoblox.com/browse/NIOSSPT-10638 if this case fails")
            assert False
        
        display_msg("-----------Test Case 20 Execution Completed------------")

    @pytest.mark.run(order=22)
    def test_021_validate_a_record_4(self):
        """
        Validate A record a.sub4.niosspt_10638.com
        Refer https://jira.inca.infoblox.com/browse/NIOSSPT-10638 if this case fails
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 21 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Validate A record a.sub4.niosspt_10638")
        response_val = ib_NIOS.wapi_request('GET',object_type="record:a", params="?name=a.sub4.niosspt_10638.com")
        display_msg(response_val)
        if not json.loads(response_val) or type(response_val) == tuple:
            display_msg("Expected Failure: Validation failed")
            assert True
        else:
            display_msg("Unexpected Pass: Validation passed")
            display_msg("Refer https://jira.inca.infoblox.com/browse/NIOSSPT-10638 if this case fails")
            assert False
        
        display_msg("-----------Test Case 21 Execution Completed------------")

    @pytest.mark.run(order=23)
    def test_022_add_a_record_5(self):
        """
        Add A record a.sub5.niosspt_10638.com.
        Add IPV4 address (example : 10.1.1.5).
        Verify that the A record is created with no errors.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 22 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Create A record a.sub5.niosspt_10638.com")
        data = {"name": "a.sub5.niosspt_10638.com",
                "ipv4addr":"10.1.1.5"}
        response = ib_NIOS.wapi_request('POST',object_type="record:a",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Create A record a.sub5.niosspt_10638.com")
            assert False
        
        '''Validation'''
        display_msg("Start validation")
        response_val = ib_NIOS.wapi_request('GET',object_type="record:a", params="?name=a.sub5.niosspt_10638.com")
        display_msg(response_val)
        if not json.loads(response_val) or type(response_val) == tuple:
            display_msg("Validation failed")
            assert False
        display_msg("Validation passed")
        
        display_msg("-----------Test Case 22 Execution Completed------------")

    @pytest.mark.run(order=24)
    def test_023_dig_a_record_5(self):
        """
        Perform dig operation on A record a.sub5.niosspt_10638.com
        dig @config.grid_vip a.sub5.niosspt_10638.com
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 23 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Perform dig operation on A record a.sub5.niosspt_10638")
        dig_cmd = 'dig @'+config.grid_vip+' a.sub5.niosspt_10638.com'
        result = os.popen(dig_cmd).read()
        response = result.split('\n')
        answer = False
        pattern = False 
        match_line = "a.sub5.niosspt_10638.com.\s+\d+\s+IN\s+A\s+10.1.1.5"
        for line in response:
            display_msg(line)
            if answer and not pattern:
                match = re.match(match_line, line)
                if match:
                    pattern = True
                    break
            if 'ANSWER SECTION' in line:
                answer = True
        if not answer or not pattern:
            display_msg("Failure: Perform dig query")
            assert False
        
        display_msg("-----------Test Case 23 Execution Completed------------")

    @pytest.mark.run(order=25)
    def test_024_add_disabled_stub_zone(self):
        """
        Add a Disabled on Creation Stub Zone as sub zone sub5.niosspt_10638.com.
        Add dummy name server.
        Verify that the Zone is created with no errors.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 24 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Add disabled Stub zone sub5.niosspt_10638.com")
        data = {"fqdn": "sub5.niosspt_10638.com", 
                "disable": True,
                "view":"default", 
                "stub_from": [{"name": "infoblox.localdomain","address": "1.1.1.5"}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_stub",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Add disabled Stub zone sub5.niosspt_10638.com")
            assert False
        
        restart_services(config.grid_vip)
        
        '''Validation'''
        display_msg("Start validation")
        response_val = ib_NIOS.wapi_request('GET',object_type="zone_stub", params="?fqdn=sub5.niosspt_10638.com")
        display_msg(response_val)
        if not json.loads(response_val) or type(response_val) == tuple:
            display_msg("Validation failed")
            assert False
        display_msg("Validation passed")
        
        display_msg("-----------Test Case 24 Execution Completed------------")

    @pytest.mark.run(order=26)
    def test_025_dig_a_record_5_repeat(self):
        """
        Perform dig operation on A record a.sub5.niosspt_10638.com
        dig @config.grid_vip a.sub5.niosspt_10638.com
        Refer https://jira.inca.infoblox.com/browse/NIOSSPT-10638 if this case fails
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 25 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Perform dig operation on A record a.sub5.niosspt_10638")
        dig_cmd = 'dig @'+config.grid_vip+' a.sub5.niosspt_10638.com'
        result = os.popen(dig_cmd).read()
        response = result.split('\n')
        answer = False
        pattern = False 
        match_line = "a.sub5.niosspt_10638.com.\s+\d+\s+IN\s+A\s+10.1.1.5"
        for line in response:
            display_msg(line)
            if answer and not pattern:
                match = re.match(match_line, line)
                if match:
                    pattern = True
                    break
            if 'ANSWER SECTION' in line:
                answer = True
        if not answer or not pattern:
            display_msg("Expected Failure: Perform dig query")
            assert True
        else:
            display_msg("Unexpected Pass: Perform dig query")
            display_msg("Refer https://jira.inca.infoblox.com/browse/NIOSSPT-10638 if this case fails")
            assert False
        
        display_msg("-----------Test Case 25 Execution Completed------------")

    @pytest.mark.run(order=27)
    def test_026_validate_a_record_5(self):
        """
        Validate A record a.sub5.niosspt_10638.com
        Refer https://jira.inca.infoblox.com/browse/NIOSSPT-10638 if this case fails
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 26 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Validate A record a.sub5.niosspt_10638")
        response_val = ib_NIOS.wapi_request('GET',object_type="record:a", params="?name=a.sub5.niosspt_10638.com")
        display_msg(response_val)
        if not json.loads(response_val) or type(response_val) == tuple:
            display_msg("Expected Failure: Validation failed")
            assert True
        else:
            display_msg("Unexpected Pass: Validation passed")
            display_msg("Refer https://jira.inca.infoblox.com/browse/NIOSSPT-10638 if this case fails")
            assert False
        
        display_msg("-----------Test Case 26 Execution Completed------------")

    @pytest.mark.run(order=28)
    def test_027_add_a_record_6(self):
        """
        Add A record a.sub6.niosspt_10638.com.
        Add IPV4 address (example : 10.1.1.6).
        Verify that the A record is created with no errors.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 27 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Create A record a.sub6.niosspt_10638.com")
        data = {"name": "a.sub6.niosspt_10638.com",
                "ipv4addr":"10.1.1.6"}
        response = ib_NIOS.wapi_request('POST',object_type="record:a",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Create A record a.sub6.niosspt_10638.com")
            assert False
        
        '''Validation'''
        display_msg("Start validation")
        response_val = ib_NIOS.wapi_request('GET',object_type="record:a", params="?name=a.sub6.niosspt_10638.com")
        display_msg(response_val)
        if not json.loads(response_val) or type(response_val) == tuple:
            display_msg("Validation failed")
            assert False
        display_msg("Validation passed")
        
        display_msg("-----------Test Case 27 Execution Completed------------")

    @pytest.mark.run(order=29)
    def test_028_dig_a_record_6(self):
        """
        Perform dig operation on A record a.sub6.niosspt_10638.com
        dig @config.grid_vip a.sub6.niosspt_10638.com
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 28 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Perform dig operation on A record a.sub6.niosspt_10638")
        dig_cmd = 'dig @'+config.grid_vip+' a.sub6.niosspt_10638.com'
        result = os.popen(dig_cmd).read()
        response = result.split('\n')
        answer = False
        pattern = False 
        match_line = "a.sub6.niosspt_10638.com.\s+\d+\s+IN\s+A\s+10.1.1.6"
        for line in response:
            display_msg(line)
            if answer and not pattern:
                match = re.match(match_line, line)
                if match:
                    pattern = True
                    break
            if 'ANSWER SECTION' in line:
                answer = True
        if not answer or not pattern:
            display_msg("Failure: Perform dig query")
            assert False
        
        display_msg("-----------Test Case 28 Execution Completed------------")

    @pytest.mark.run(order=30)
    def test_029_add_disabled_delegated_zone(self):
        """
        Add a Disabled on Creation Delegated Zone as sub zone sub6.niosspt_10638.com.
        Add dummy name server.
        Verify that the Zone is created with no errors.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 29 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Add disabled Delegated zone sub6.niosspt_10638.com")
        data = {"fqdn": "sub6.niosspt_10638.com", 
                "disable": True,
                "view":"default", 
                "delegate_to": [{"name": "infoblox.localdomain","address": "1.1.1.6"}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_delegated",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Add disabled Delegated zone sub6.niosspt_10638.com")
            assert False
        
        restart_services(config.grid_vip)
        
        '''Validation'''
        display_msg("Start validation")
        response_val = ib_NIOS.wapi_request('GET',object_type="zone_delegated", params="?fqdn=sub6.niosspt_10638.com")
        display_msg(response_val)
        if not json.loads(response_val) or type(response_val) == tuple:
            display_msg("Validation failed")
            assert False
        display_msg("Validation passed")
        
        display_msg("-----------Test Case 29 Execution Completed------------")

    @pytest.mark.run(order=31)
    def test_030_dig_a_record_6_repeat(self):
        """
        Perform dig operation on A record a.sub6.niosspt_10638.com
        dig @config.grid_vip a.sub6.niosspt_10638.com
        Refer https://jira.inca.infoblox.com/browse/NIOSSPT-10638 if this case fails
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 30 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Perform dig operation on A record a.sub6.niosspt_10638")
        dig_cmd = 'dig @'+config.grid_vip+' a.sub6.niosspt_10638.com'
        result = os.popen(dig_cmd).read()
        response = result.split('\n')
        answer = False
        pattern = False 
        match_line = "a.sub6.niosspt_10638.com.\s+\d+\s+IN\s+A\s+10.1.1.6"
        for line in response:
            display_msg(line)
            if answer and not pattern:
                match = re.match(match_line, line)
                if match:
                    pattern = True
                    break
            if 'ANSWER SECTION' in line:
                answer = True
        if not answer or not pattern:
            display_msg("Expected Failure: Perform dig query")
            assert True
        else:
            display_msg("Unexpected Pass: Perform dig query")
            display_msg("Refer https://jira.inca.infoblox.com/browse/NIOSSPT-10638 if this case fails")
            assert False
        
        display_msg("-----------Test Case 30 Execution Completed------------")

    @pytest.mark.run(order=32)
    def test_031_validate_a_record_6(self):
        """
        Validate A record a.sub6.niosspt_10638.com
        Refer https://jira.inca.infoblox.com/browse/NIOSSPT-10638 if this case fails
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 31 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Validate A record a.sub6.niosspt_10638")
        response_val = ib_NIOS.wapi_request('GET',object_type="record:a", params="?name=a.sub6.niosspt_10638.com")
        display_msg(response_val)
        if not json.loads(response_val) or type(response_val) == tuple:
            display_msg("Expected Failure: Validation failed")
            assert True
        else:
            display_msg("Unexpected Pass: Validation passed")
            display_msg("Refer https://jira.inca.infoblox.com/browse/NIOSSPT-10638 if this case fails")
            assert False
        
        display_msg("-----------Test Case 31 Execution Completed------------")

    @pytest.mark.run(order=33)
    def test_032_add_a_record_with_same_logic(self):
        """
        Add A record a.sub6.niosspt_10638.com.
        Add IPV4 address (example : 10.1.1.7).
        Verify that the A record is created with no errors.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 32 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Create A record a.sub6.niosspt_10638.com")
        data = {"name": "a.sub6.niosspt_10638.com",
                "ipv4addr":"10.1.1.7"}
        response = ib_NIOS.wapi_request('POST',object_type="record:a",fields=json.dumps(data))
        display_msg(response)
        if not type(response) == tuple:
            display_msg("Failure: Created A record a.sub6.niosspt_10638.com under Delegated zone")
            assert False
        
        '''Validation'''
        display_msg("Start validation")
        response_val = ib_NIOS.wapi_request('GET',object_type="record:a", params="?name=a.sub6.niosspt_10638.com")
        display_msg(response_val)
        if json.loads(response_val) or type(response_val) == tuple:
            display_msg("Validation failed")
            assert False
        display_msg("Validation passed")
        
        display_msg("-----------Test Case 32 Execution Completed-----------")

    @pytest.mark.run(order=-1)
    def test_cleanup(self):
        """
        cleanup method: Delete all the objects created from this script.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|          Test Case cleanup Started           |")
        display_msg("------------------------------------------------")
        display_msg("Delete the zone niosspt_10638.com")
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", params="?fqdn=niosspt_10638.com")
        display_msg(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        response = ib_NIOS.wapi_request('DELETE', ref=ref1)
        display_msg(response)

        restart_services()

        display_msg("-----------Test Case cleanup Completed------------")
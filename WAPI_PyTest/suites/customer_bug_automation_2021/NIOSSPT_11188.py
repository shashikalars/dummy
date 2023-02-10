#!/usr/bin/env python
__author__ = "Chetan Kumar PG"
__email__  = "cpg@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Stand alone Grid Master                                               #
#  2. Licenses : DNS, Grid, NIOS(IB_1415)                                   #
#  3. Enable DNS services                                                   #
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
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="niosspt_11188.log" ,level=logging.DEBUG,filemode='w')

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

class NIOSSPT_11188(unittest.TestCase):
    
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
        
        '''Enable Zone Transfer'''
        display_msg("Enable DNS Zone Transfer")
        get_ref1 = ib_NIOS.wapi_request('GET', object_type='grid:dns')
        display_msg(get_ref1)
        ref1 = json.loads(get_ref1)[0]
        response = ib_NIOS.wapi_request('PUT', ref=ref1['_ref'], fields=json.dumps({"allow_transfer":[{"_struct": "addressac","address":"Any","permission": "ALLOW"}]}))
        if type(response) == tuple:
            display_msg("Failure: Enable DNS Zone Transfer")
            assert False
        restart_services()
        
        '''Validation'''
        display_msg("Start validation")
        response_val1 = ib_NIOS.wapi_request('GET',object_type="grid:dns", params="?_return_fields=allow_transfer")
        display_msg(response_val1)
        if not json.loads(response_val1)[0]["allow_transfer"] == [{"_struct": "addressac","address":"Any","permission": "ALLOW"}]:
            display_msg("Validation failed")
            assert False
        display_msg("Validation passed")
        
        display_msg("---------Test Case setup Execution Completed----------")
    
    @pytest.mark.run(order=2)
    def test_001_add_authoritative_forward_mapping_zone(self):
        """
        Add an Authorative Forward mapping Zone niosspt_11188.com.
        Add Grid master as Grid primary.
        Verify that the Zone is created with no errors.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 1 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Add an authoritative fwd mapping zone niosspt_11188.com")
        data = {"fqdn": "niosspt_11188.com", 
                "view":"default", 
                "grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Add an authoritative fwd mapping zone niosspt_11188.com")
            assert False
        
        restart_services(config.grid_vip)
        
        '''Validation'''
        display_msg("Start validation")
        response_val = ib_NIOS.wapi_request('GET',object_type="zone_auth", params="?fqdn=niosspt_11188.com")
        display_msg(response_val)
        if not json.loads(response_val) or type(response_val) == tuple:
            display_msg("Validation failed")
            assert False
        display_msg("Validation passed")
        
        display_msg("-----------Test Case 1 Execution Completed------------")

    @pytest.mark.run(order=3)
    def test_002_add_host_record(self):
        """
        Add host record host.niosspt_11188.com.
        Add IPV4 address (example : 10.1.1.1).
        Verify that the host record is created with no errors.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 2 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Create host record host.niosspt_11188.com")
        data = {"name": "host.niosspt_11188.com",
                "ipv4addrs": [{"ipv4addr":"10.1.1.1"}]}
        response = ib_NIOS.wapi_request('POST',object_type="record:host",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Create host record host.niosspt_11188.com")
            assert False
        
        '''Validation'''
        display_msg("Start validation")
        response_val = ib_NIOS.wapi_request('GET',object_type="record:host", params="?name=host.niosspt_11188.com")
        display_msg(response_val)
        if not json.loads(response_val) or type(response_val) == tuple:
            display_msg("Validation failed")
            assert False
        display_msg("Validation passed")
        
        display_msg("-----------Test Case 2 Execution Completed------------")

    @pytest.mark.run(order=4)
    def test_003_dig_host_record(self):
        """
        Perform dig operation on host record host.niosspt_11188.com
        dig @config.grid_vip host.niosspt_11188.com
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 3 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Perform dig operation on host record host.niosspt_11188")
        dig_cmd = 'dig @'+config.grid_vip+' host.niosspt_11188.com'
        result = os.popen(dig_cmd).read()
        response = result.split('\n')
        answer = False
        pattern = False 
        match_line = "host.niosspt_11188.com.\s+\d+\s+IN\s+A\s+10.1.1.1"
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
    def test_004_authoritative_reverse_mapping_zone(self):
        """
        Add an Authorative Reverse mapping Zone 10.1.1.0/24.
        Add Grid master as Grid primary.
        Verify that the Zone is created with no errors.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 4 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Add an authoritative reverse mapping zone 10.1.1.0/24")
        data = {"fqdn": "10.1.1.0/24",
                "zone_format":"IPV4",
                "view":"default", 
                "grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Add an authoritative reverse mapping zone 10.1.1.0/24")
            assert False
        
        restart_services(config.grid_vip)
        
        '''Validation'''
        display_msg("Start validation")
        response_val = ib_NIOS.wapi_request('GET',object_type="zone_auth", params="?fqdn=10.1.1.0/24")
        display_msg(response_val)
        if not json.loads(response_val) or type(response_val) == tuple:
            display_msg("Validation failed")
            assert False
        display_msg("Validation passed")
        
        display_msg("-----------Test Case 4 Execution Completed------------")

    @pytest.mark.run(order=6)
    def test_005_repeat_dig_host_record(self):
        """
        Repeat dig operation on host record host.niosspt_11188.com
        dig @config.grid_vip host.niosspt_11188.com
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 5 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Repeat dig operation on host record host.niosspt_11188")
        dig_cmd = 'dig @'+config.grid_vip+' host.niosspt_11188.com'
        result = os.popen(dig_cmd).read()
        response = result.split('\n')
        answer = False
        pattern = False 
        match_line = "host.niosspt_11188.com.\s+\d+\s+IN\s+A\s+10.1.1.1"
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
        
        display_msg("-----------Test Case 5 Execution Completed------------")

    @pytest.mark.run(order=7)
    def test_006_dig_host_record_reverse_nslookup(self):
        """
        Perform dig operation on host record using reverse nslookup
        dig @config.grid_vip -x 10.1.1.1
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 6 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Perform dig operation on host record using reverse nslookup")
        dig_cmd = 'dig @'+config.grid_vip+' -x 10.1.1.1'
        result = os.popen(dig_cmd).read()
        response = result.split('\n')
        answer = False
        pattern = False 
        match_line = "1.1.1.10.in-addr.arpa.\s+\d+\s+IN\s+PTR\s+host.niosspt_11188.com"
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
        
        display_msg("-----------Test Case 6 Execution Completed------------")

    @pytest.mark.run(order=8)
    def test_007_add_host_record_repeat(self):
        """
        Add host record host2.niosspt_11188.com.
        Add IPV4 address (example : 10.1.1.2).
        Verify that the host record is created with no errors.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 7 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Create host record host2.niosspt_11188.com")
        data = {"name": "host2.niosspt_11188.com",
                "ipv4addrs": [{"ipv4addr":"10.1.1.2"}]}
        response = ib_NIOS.wapi_request('POST',object_type="record:host",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Create host record host2.niosspt_11188.com")
            assert False
        
        '''Validation'''
        display_msg("Start validation")
        response_val = ib_NIOS.wapi_request('GET',object_type="record:host", params="?name=host2.niosspt_11188.com")
        display_msg(response_val)
        if not json.loads(response_val) or type(response_val) == tuple:
            display_msg("Validation failed")
            assert False
        display_msg("Validation passed")
        
        display_msg("-----------Test Case 7 Execution Completed------------")

    @pytest.mark.run(order=9)
    def test_008_dig_host_record_repeat(self):
        """
        Perform dig operation on host record host2.niosspt_11188.com
        dig @config.grid_vip host2.niosspt_11188.com
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 8 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Perform dig operation on host record host2.niosspt_11188.com")
        dig_cmd = 'dig @'+config.grid_vip+' host2.niosspt_11188.com'
        result = os.popen(dig_cmd).read()
        response = result.split('\n')
        answer = False
        pattern = False 
        match_line = "host2.niosspt_11188.com.\s+\d+\s+IN\s+A\s+10.1.1.2"
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
    def test_009_perform_axfr_on_zone(self):
        """
        Perform AXFR operation on Zone niosspt_11188.com
        dig @config.grid_vip niosspt_11188.com axfr
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 9 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Perform AXFR operation on zone niosspt_11188.com")
        dig_cmd = 'dig @'+config.grid_vip+' niosspt_11188.com axfr'
        result = os.popen(dig_cmd).read()
        response = result.split('\n')
        pattern1 = False 
        pattern2 = False 
        match_line1 = "host.niosspt_11188.com.\s+\d+\s+IN\s+A\s+10.1.1.1"
        match_line2 = "host2.niosspt_11188.com.\s+\d+\s+IN\s+A\s+10.1.1.2"
        for line in response:
            display_msg(line)
            match = re.match(match_line1, line)
            match2 = re.match(match_line2, line)
            if match:
                pattern1 = True
            if match2:
                pattern2 = True
        if not pattern1 or not pattern2:
            display_msg("Failure: Perform AXFR on zone niosspt_11188.com")
            assert False
        
        display_msg("-----------Test Case 9 Execution Completed------------")

    @pytest.mark.run(order=11)
    def test_010_disable_dns_service(self):
        """
        Disable DNS Service
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 10 Execution Started          |")
        display_msg("----------------------------------------------------") 
        display_msg("Disable DNS service")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns')
        display_msg(get_ref)
        ref = json.loads(get_ref)[0]
        response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps({"enable_dns":False}))
        if type(response) == tuple:
            display_msg("Failure: Disable DNS Service")
            assert False
        restart_services()
        
        '''Validation'''
        display_msg("Start validation")
        response_val = ib_NIOS.wapi_request('GET',object_type="member:dns", params="?_return_fields=enable_dns")
        display_msg(response_val)
        if not json.loads(response_val)[0]["enable_dns"] == False:
            display_msg("Validation failed")
            assert False
        display_msg("Validation passed")
        
        display_msg("-----------Test Case 10 Execution Completed-----------")

    @pytest.mark.run(order=12)
    def test_011_enable_dns_service(self):
        """
        Enable DNS Service
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 11 Execution Started          |")
        display_msg("----------------------------------------------------") 
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
        
        display_msg("-----------Test Case 11 Execution Completed-----------")

    @pytest.mark.run(order=13)
    def test_012_perform_axfr_on_zone_repeat(self):
        """
        Perform AXFR operation on Zone niosspt_11188.com
        dig @config.grid_vip niosspt_11188.com axfr
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 12 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Perform AXFR operation on zone niosspt_11188.com")
        dig_cmd = 'dig @'+config.grid_vip+' niosspt_11188.com axfr'
        result = os.popen(dig_cmd).read()
        response = result.split('\n')
        pattern1 = False 
        pattern2 = False 
        match_line1 = "host.niosspt_11188.com.\s+\d+\s+IN\s+A\s+10.1.1.1"
        match_line2 = "host2.niosspt_11188.com.\s+\d+\s+IN\s+A\s+10.1.1.2"
        for line in response:
            display_msg(line)
            match = re.match(match_line1, line)
            match2 = re.match(match_line2, line)
            if match:
                pattern1 = True
            if match2:
                pattern2 = True
        if not pattern1 or not pattern2:
            display_msg("Failure: Perform AXFR on zone niosspt_11188.com")
            assert False
        
        display_msg("-----------Test Case 12 Execution Completed-----------")

    @pytest.mark.run(order=-1)
    def test_cleanup(self):
        """
        cleanup method: Delete all the objects created from this script.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|          Test Case cleanup Started           |")
        display_msg("------------------------------------------------")
        display_msg("Delete the zone niosspt_11188.com")
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", params="?fqdn=niosspt_11188.com")
        display_msg(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        response = ib_NIOS.wapi_request('DELETE', ref=ref1)
        display_msg(response)
        
        display_msg("Delete the zone 10.1.1.0/24")
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", params="?fqdn=10.1.1.0/24")
        display_msg(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        response = ib_NIOS.wapi_request('DELETE', ref=ref1)
        display_msg(response)

        restart_services()

        display_msg("-----------Test Case cleanup Completed------------")

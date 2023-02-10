#!/usr/bin/env python
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. SA Grid Master with Grid and DNS license                              #
#  2. SA + member1                                                          #
#############################################################################

import re
import config
import pytest
import unittest
import logging
import subprocess
import os
import json
import commands
import json, ast
import requests
from time import sleep as sleep
import pexpect
import paramiko
from paramiko import client
import ib_utils.common_utilities as comm_util
import ib_utils.ib_NIOS as ib_NIOS
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv
  
class NIOSSPT_10628(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_Create_NSG_group(self):
        print("Creating NSG group")
        data = {"name": "NSG_1"}
        response = ib_NIOS.wapi_request('POST', object_type="nsgroup", fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)
        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==404:
                print("Failure: Create A NSG group")
                assert False
            else:
                print("Success: Create A NSG group")
                assert True
        
        
    @pytest.mark.run(order=2)
    def test_001_update_NSG_services(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type='nsgroup')
        print(get_ref)
        for ref in json.loads(get_ref):
            if 'NSG_1' in ref['name']:
            
                data={"external_secondaries": [{
                "address": "1.1.1.1",
                "name": "external_secondary.com",
                "stealth": False,
                "use_tsig_key_name": False
            }],
        "grid_primary": [{
                "name": config.grid_fqdn,
                "stealth": False
            }],
        "grid_secondaries": [{
                "enable_preferred_primaries": False,
                "grid_replicate": False,
                "lead": False,
                "name": config.grid_member1_fqdn,
                "preferred_primaries": [],
                "stealth": False
            }]}
            
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)
                print response
                
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401 or response[0]==404:
                        print("Failure: Create A NSG group primary and secondaries")
                        assert False
                    else:
                        print("Success: Create A NSG group group primary and secondaries")
                        assert True

    @pytest.mark.run(order=3)
    def test_002_create_Forward_Mapping_Zone1(self): 
        print("Create test FMZ zone1 assigned to GM")
        data = {"fqdn": "test1.com",
                "view":"default",
                "ns_group": "NSG_1",
                "zone_format": "FORWARD"
                }
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: create_Forward_Mapping_Zone1")
                assert False

    @pytest.mark.run(order=4)
    def test_003_Override_Zone_transfer_option(self):    
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth')
        for ref in json.loads(get_ref):
            if 'test1.com' in ref['fqdn']:
                data={"allow_transfer": [{
                        "_struct": "addressac",
                        "address": "Any",
                        "permission": "ALLOW"
                    }]}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: Override Zone transfer option with value any")
                        assert False

    @pytest.mark.run(order=5)
    def test_004_create_Forward_Mapping_Zone2(self): 
        print("Create test FMZ zone2 assigned to GM")
        data = {"fqdn": "test2.com",
                "view":"default",
                "ns_group": "NSG_1",
                "zone_format": "FORWARD"
                }
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: create_Forward_Mapping_Zone2")
                assert False
        
    @pytest.mark.run(order=6)
    def test_005_Update_Zone_transfer_option_in_Grid_DNS(self):  
        print("Update Zone transfer option in Grid DNS")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns')
        for ref in json.loads(get_ref):
            data={"allow_transfer": [{
                    "_struct": "addressac",
                    "address": "Any",
                    "permission": "ALLOW"
                }]}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)
            print(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    print("Failure: Override Zone transfer option in Grid DNS with value any")
                    assert False
                    
        log("start","/infoblox/var/named_conf/named.conf",config.grid_vip)
           
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)
        
        log("stop","/infoblox/var/named_conf/named.conf",config.grid_vip)
        LookFor=["unknown option 'key'","unknown option '1.1.1.1'","unknown option 'any'","SYNTAX ERROR"]
        cnt=0
        for look in LookFor:
            print(look)
            logs=logv(LookFor,"/infoblox/var/named_conf/named.conf",config.grid_vip)
            print(logs)
            if logs:
                cnt=cnt+1
            else:
                cnt=cnt+0
        print(cnt)
        if cnt!=0:
         
            logging.info("Failed")
            assert False
            
        else:
            logging.info("Success")
            assert True

    @pytest.mark.run(order=7)
    def test_006_check_status_of_grid(self): 
        sleep(30)
        get_ref=ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=service_status')
        print(get_ref)
        
        for ref in json.loads(get_ref):
            if "WORKING" in ref['service_status']:
                
                print("----------Status of the grid: "+ref['service_status']+"-----------")
                assert True
            else:
                print("-------Status of the grid: "+ref['service_status']+"--------")
                assert False
               
            
    @pytest.mark.run(order=8)
    def test_007_cleanup_objects(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
             
            print(response)
                    
            if type(response) == tuple:
                        
                if response[0]==400 or response[0]==401:
                            
                    assert False
                else:
                    assert True
        get_ref = ib_NIOS.wapi_request('GET', object_type="nsgroup", grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
             
            print(response)
                    
            if type(response) == tuple:
                        
                if response[0]==400 or response[0]==401:
                            
                    assert False
                else:
                    assert True
 

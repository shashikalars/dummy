#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Licenses : DNS(enabled), DHCP, Grid                                   #
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
import pexpect

logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="rfe_10324.log" ,level=logging.DEBUG,filemode='w')


class NIOSSPT_6623(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_000_start_dns_services(self):
        print("Start DNS service")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns')
        print(get_ref)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps({"enable_dns":True}))
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    assert False
    
    
    
    @pytest.mark.run(order=2)
    def test_001_create_nsg_services(self):
        print("create 'default' NSG using the GM as Grid Primary and set as default NSG")
        data = {"name": "NSG",
               "comment": "Created a new NSG server",
               "grid_primary":[{"name": config.grid_fqdn}]
               }
        response = ib_NIOS.wapi_request('POST',object_type="nsgroup",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create default NSG")
                assert False
                  
                   
    @pytest.mark.run(order=3)
    def test_002_create_zone_default_NSG(self):     
        print("Create auth zone localdomain using the 'default' NSG")
        data = {"fqdn": "nsg_testing.com",
               "view": "default",
               "ns_group":"NSG"}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create auth zone localdomain using the 'default' NSG")
                assert False
                  
        
    @pytest.mark.run(order=4)
    def test_003_enable_ddns_update(self):      
        print("Enable DDNS updates from anywhere")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns')
        data = {"allow_update":[{"_struct": "addressac","address":"Any", "permission":"ALLOW"}]}
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data))
            print(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    print("Failure: Enable DDNS updates from anywhere")
                    assert False
                
        print("Restart DHCP Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)
        
    @pytest.mark.run(order=5)
    def test_004_create_CAA_Record(self):     
        print("Add a CAA record")
        data = {"name": "c_rec.nsg_testing.com",
                "ca_flag": 0,
                "ca_tag": "issue",
                "ca_value": "no",
               "view": "default"}
        response = ib_NIOS.wapi_request('POST',object_type="record:caa",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Add a CAA record")
                assert False
     
    @pytest.mark.run(order=6)
    def test_005_create_CAA_Record_nsupdate(self):     
        print("Add a CAA record through nsupdate")
        child = pexpect.spawn("nsupdate")
        try:
            child.expect('> ')
            child.send('server '+config.grid_vip+'\n')
            print(child.before)
            child.expect('>')
            child.send('update add caa_rec.nsg_testing.com. 100 caa 0 issue "nsg_testing.com"\n')
            print(child.before)
            child.expect('>')
            child.send('send\n')
            print(child.before)
            child.expect('>')
            child.send('quit\n')
        except Exception as e:
            print(e)
            assert False
        finally:
            child.close()
            
    @pytest.mark.run(order=7)
    def test_006_validate_caa_record_updation(self):        
        print("\nValidating caa record got updated or not")     
        get_ref = ib_NIOS.wapi_request('GET', object_type='record:caa?name=caa_rec.nsg_testing.com')
        for ref in json.loads(get_ref):
            if 'caa_rec' in ref['_ref']:
                print("Success: Validating caa record got updated")
                assert True
            else:
                print("Failure: Validating caa record got updated")
                assert False
                        
    @pytest.mark.run(order=8)
    def test_007_sign_zone_notice_message(self):        
        print("Try to sign the zone, and notice the error message received")     
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth')
        for ref in json.loads(get_ref):
            if 'nsg_testing' in ref['_ref']:
                response = ib_NIOS.wapi_request('POST', ref=ref['_ref'], params='?_function=dnssec_operation', fields=json.dumps({"operation":"SIGN"}))
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: Sign Zone signs without error")
                        assert False
                    else:
                        print("Success: Sign Zone ssigns without error")
                        
    
    @pytest.mark.run(order=9)
    def test_008_unsign_zone_(self):        
        print("Try to unsign the zone")     
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth')
        for ref in json.loads(get_ref):
            if 'nsg_testing' in ref['_ref']:
                response = ib_NIOS.wapi_request('POST', ref=ref['_ref'], params='?_function=dnssec_operation', fields=json.dumps({"operation":"UNSIGN"}))
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: Unsign Zone signs without error")
                        assert False
                    else:
                        print("Success: Unsign Zone ssigns without error")

    @pytest.mark.run(order=10)   
    def test_009_change_nsg_to_grid_primary(self):
        print("Edit the zone and move from the 'default' NSG to a manually defined GM as Grid Primary")
    
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth')
        data = {"view":"default","grid_primary":[{"name": config.grid_fqdn}],"comment":"Move from NSG to grid"}
        for ref in json.loads(get_ref):
            if 'nsg_testing' in ref['_ref']:
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: move from NSG to Grid")
                        assert False
        print("Restart DHCP Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)
    
    
    @pytest.mark.run(order=11)   
    def test_010_sign_zone_without_error(self):
        print("Try to sign the zone, and confirm it signs without error")
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth')
        for ref in json.loads(get_ref):
            if 'nsg_testing' in ref['_ref']:
                response = ib_NIOS.wapi_request('POST', ref=ref['_ref'], params='?_function=dnssec_operation', fields=json.dumps({"operation":"SIGN"}),grid_vip=config.grid_vip)
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: Sign Zone signs without error")
                        assert False
                    else:
                        print("Success: Sign Zone ssigns without error")
    
    
        
                   
    @pytest.mark.run(order=12)
    def test_011_cleanup(self):
        print("Clean up all created objects")
        get_ref = ib_NIOS.wapi_request('GET', object_type="nsgroup", grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
             
            print(response)
                    
            if type(response) == tuple:
                        
                if response[0]==400 or response[0]==401:
                            
                    assert False
                else:
                    assert True


        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
             
            print(response)
                    
            if type(response) == tuple:
                        
                if response[0]==400 or response[0]==401:
                            
                    assert False
                else:
                    assert True

        get_ref = ib_NIOS.wapi_request('GET', object_type="record:caa", grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
             
            print(response)
                    
            if type(response) == tuple:
                        
                if response[0]==400 or response[0]==401:
                            
                    assert False
                else:
                    assert True

        print("Restart DHCP Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)

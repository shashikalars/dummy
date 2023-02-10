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
#import ib_utils.common_utilities as ib_TOKEN

def restart_services(grid=config.grid_vip):
    """
    Restart Services
    """
    print("Restart services")
    get_ref =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=grid)
    ref = json.loads(get_ref)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices", fields=json.dumps(data),grid_vip=grid)
    sleep(30)

class NIOSSPT_10056(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_000_Forward_Mapping_Zone(self):
        print("Create test FMZ zone assigned to GM")
        data = {"fqdn": "rfe_niosspt_10056.com",
                "view":"default",
                "grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            print("Failure: Create Authorative FMZ")
            assert False
        restart_services()


    @pytest.mark.run(order=2)
    def test_001_Reverse_Mapping_Zone(self):
        print("Create test RMZ zone assigned to GM")
        data = {"fqdn": "13.0.0.0/8",   
                "view":"default",
                "zone_format":"IPV4",
                "grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            print("Failure: Create Authorative RMZ")
            assert False
        restart_services()


    @pytest.mark.run(order=3)
    def test_002_create_A_record(self):
        print("Creating A RR in test zone")
        data = {"ipv4addr": "13.0.0.1",
                "view":"default",
                "name": "A_rec.rfe_niosspt_10056.com"}
        response = ib_NIOS.wapi_request('POST',object_type="record:a",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            print("Failure: Create A record in test zone")
            assert False

    @pytest.mark.run(order=4)
    def test_003_create_PTR_record(self):
        print("Creating A PTR in test zone")
        data = {"ptrdname": "A_rec.rfe_niosspt_10056.com",
                "view":"default",
                "name": "1.0.0.13.in-addr.arpa"}
        response = ib_NIOS.wapi_request('POST',object_type="record:ptr",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            print("Failure: Create ptr record in test zone")
            assert False


    @pytest.mark.run(order=5)
    def test_004_update_PTR_record(self):
        data={"ptrdname": "a_rec.rfe_niosspt_10056.com"}
        print("Change case of any character of PTR RR hostname in test RMZ")
        get_ref = ib_NIOS.wapi_request('GET', object_type='record:ptr')
        for ref in json.loads(get_ref):
            print(ref)
            if 'rfe_niosspt_10056.com' in ref["ptrdname"]:
                print(ref)
                response = ib_NIOS.wapi_request('PUT',ref=ref['_ref'],fields=json.dumps(data))
                print(response)
                if type(response) == tuple:
                    print("Failure: Update PTR in test zone")
                    assert False
                else:
                    assert True


    @pytest.mark.run(order=6)
    def test_005_start_dns_services(self):
       print("Start DNS service")
       get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns')
       print(get_ref)
       for ref in json.loads(get_ref):
           response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps({"enable_dns":True}))
           if type(response) == tuple:
                assert False
       restart_services()


    @pytest.mark.run(order=7)
    def test_006_dig_output_resolve(self):
        
        sleep(90)
        
        print("Check with dig that test A and PTR RRs are resolved correctly")
        output = os.popen("dig @"+config.grid_vip+" A_rec.rfe_niosspt_10056.com IN A").read()
        output = output.split('\n')
    
        A_found = False
        PTR_found= False
        for index,value in enumerate(output):
            if 'ANSWER SECTION:' in value:
                print(output[index+1])
                match = re.match("A_rec.rfe_niosspt_10056.com.\s+\d+\s+IN\s+A\s+13.0.0.1", output[index+1])
                print(match)
                if match:
                    A_found = True
                    break
              
        if A_found==True:
            print("Success: Perform dig query")
            assert True
        else:
            print("Failed: Perform dig query")
            print(output)
            assert False
            
            
    @pytest.mark.run(order=8)
    def test_007_dig_output_resolve_ptr(self):
        print("Check with dig that test PTR RRs are resolved correctly")
        output = os.popen("dig @"+config.grid_vip+" 1.0.0.13.in-addr.arpa. IN PTR").read()
        output = output.split('\n')
        print()
        PTR_found= False
    
        for index,value in enumerate(output):
            if 'ANSWER SECTION:' in value:
                print(output[index+1])
                match = re.match("1.0.0.13.in-addr.arpa.\s+\d+\s+IN\s+PTR\s+a_rec.rfe_niosspt_10056.com.", output[index+1])
                
                if match:
                    PTR_found = True
                    break
        if PTR_found==True:
            print("Success: Perform dig query")
            assert True
        else:
            print("Failed: Perform dig query")
            print(output)
            assert False
            
    @pytest.mark.run(order=9)
    def test_008_import_zone(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth')
        print(get_ref)
        for ref in json.loads(get_ref):
            if 'rfe_niosspt_10056.com' in ref['_ref']:
                print(ref['_ref'])
                data = {"use_import_from":True, "import_from":"255.255.255.255", "do_host_abstraction":True}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                print(response)
                if type(response) == tuple:
                    print("Failure: Import record from zone of test FMZ")
                    assert False
        restart_services()
                        
    @pytest.mark.run(order=10)
    def test_009_dig_output_resolve_import(self):
        sleep(60)
        print("Check with dig that test A and PTR RRs are resolved correctly")
        output = os.popen("dig @"+config.grid_vip+" A_rec.rfe_niosspt_10056.com IN A").read()
        output = output.split('\n')
        A_found = False
        PTR_found= False
        #print(output)
        for index,value in enumerate(output):
            if 'ANSWER SECTION:' in value:
                print(output[index+1])
                match = re.match("A_rec.rfe_niosspt_10056.com.\s+\d+\s+IN\s+A\s+13.0.0.1", output[index+1])
                print(match)
                if match:
                    A_found = True
                    break
        if A_found==True:
            print("Success: Perform dig query")
            assert True
        else:
            print("Failed: Perform dig query")
            print(output)
            assert False
            
            
    @pytest.mark.run(order=11)
    def test_010_dig_output_resolve_ptr_import(self):
        print("Check with dig that test A and PTR ")
        output = os.popen("dig @"+config.grid_vip+" 1.0.0.13.in-addr.arpa. IN PTR").read()
        output = output.split('\n')
        print()
        PTR_found= False
    
        for index,value in enumerate(output):
            if 'ANSWER SECTION:' in value:
                print(output[index+1])
                match = re.match("1.0.0.13.in-addr.arpa.\s+\d+\s+IN\s+PTR\s+a_rec.rfe_niosspt_10056.com.", output[index+1])
                
                if match:
                    PTR_found = True
                    break
        if PTR_found==True:
            print("Success: Perform dig query")
            assert True
        else:
            print("Failed: Perform dig query")
            print(output)
            assert False
    
    
    @pytest.mark.run(order=12)
    def test_011_cleanup(self):
        print("Clean up all created objects")
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])             
            print(response)                  
            if type(response) == tuple:                        
                assert False


        get_ref = ib_NIOS.wapi_request('GET', object_type="record:a", grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])             
            print(response)
            if type(response) == tuple:
                assert False

        get_ref = ib_NIOS.wapi_request('GET', object_type="record:ptr", grid_vip=config.grid_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            if 'A_rec.rfe_niosspt_10056.com' in ref['_ref']:
                response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])  
                print(response)                  
                if type(response) == tuple:                       
                    assert False

        restart_services()


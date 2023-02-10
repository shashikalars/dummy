#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Grid Master + M1                                                      #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415)                           #
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
    sleep(10)
    
class NIOS_75687(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_000_Create_NSG_groups(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        logging.info(get_ref)
        res = json.loads(get_ref)
        for i in res:
            logging.info("Modify a enable_dns")
            data = {"enable_dns": True}
            response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
            print(response)
        print("Creating NSG group 'rootServers'")
        data = {"name": "rootServers",
                "grid_primary": [{
                "name": config.grid_fqdn,
                "stealth": False}]}
        response = ib_NIOS.wapi_request('POST', object_type="nsgroup", fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)
        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==404:
                print("Failure: Create A rootServers group ")
                assert False
            else:
                print("Success: Create A rootServers group")
                assert True
        
        print("Creating NSG group 'authServers'")
        data = {"name": "authServers",
                "grid_primary": [{
                "name": config.grid_member1_fqdn,
                "stealth": False}]}
        response = ib_NIOS.wapi_request('POST', object_type="nsgroup", fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)
        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==404:
                print("Failure: Create A authServers group ")
                assert False
            else:
                print("Success: Create A authServers group")
                assert True

        restart_services()
        
    @pytest.mark.run(order=2)
    def test_001_create_Forward_Mapping_Zone(self): 
        print("Create test FMZ zone assigned to GM")
        data = {"fqdn": ".",
                "view":"default",
                "ns_group": "rootServers",
                "zone_format": "FORWARD"
                }
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==404:
                print("Failure: create_Forward_Mapping_Zone1")
                assert False
        restart_services()

    @pytest.mark.run(order=3)
    def test_002_create_Reverse_Mapping_Zone(self):
        print(config.grid_fqdn)
        print("Create test RMZ zone and assign to NSgroup 'authServers'")
        data = {"fqdn": "1.1.0.0/16",
                "ns_group": "authServers",
                "zone_format": "IPV4"}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            print("Failure: Create Authorative RMZ")
            assert False
            
        print("Create test RMZ zone and assign to the member ")
        data = {"fqdn": "1.2.0.0/16",
                "zone_format": "IPV4",
                "grid_primary": [{
                "name": config.grid_member1_fqdn,
                "stealth": False}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            print("Failure: Create Authorative RMZ")
            assert False
        
        restart_services()
        
    @pytest.mark.run(order=4)
    def test_003_Override_Zone_transfer_option(self):    
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth')
        for ref in json.loads(get_ref):
            if './default' in ref['_ref']:
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
        restart_services()
        sleep(20)
        
    @pytest.mark.run(order=5)
    def test_004_validate_NS_records_for_both_zones(self):
        print("Validate NS records for both NS zones")
	sleep(5)
        output = os.popen("dig @"+config.grid_vip+" axfr .").read()
        output = output.split('\n')
        print(output)
        found1=False
        found2=False
        print(config.grid_vip)
        for index,value in enumerate(output):

            #print(output[index])
            match = re.match("1.1.in-addr.arpa.\s+\d+\s+IN\s+NS\s+"+config.grid_member1_fqdn+".", output[index])
            
            if match:
                found1 = True
                break
                
        for index,value in enumerate(output):
            match1 = re.match("2.1.in-addr.arpa.\s+\d+\s+IN\s+NS\s+"+config.grid_member1_fqdn+".", output[index])
            
            if match1:
                found2 = True
                break
        print(found1,found2)    
        if found1==True and found2==True:
            print("Success: Perform dig query")
            assert True
        else:
            print("Failed: Perform dig query")
            print(output)
            assert False
        
    @pytest.mark.run(order=6)
    def test_005_create_and_disable_arpa_zone(self): 
        print("Create test RMZ in-addr.arpa zone and assign to the member ")
        data = {"fqdn": "0.0.0.0/0",
                "zone_format": "IPV4",
                "grid_primary": [{
                "name": config.grid_member1_fqdn,
                "stealth": False}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            print("Failure: Create test RMZ in-addr.arpa zone and assign to the member")
            assert False
            
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth')
        #print(get_ref)
        for ref in json.loads(get_ref):
            if '0.0.0.0%2F0' in ref['_ref']:
                data={"disable": True}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: Override Zone disable with true")
                        assert False
                    else:
                        print("Success: Override Zone disable with true")
                        assert True
        restart_services()
        sleep(30)
        
    @pytest.mark.run(order=7)
    def test_006_after_disable_arpa_zone_validate_NS_records_for_both_zones(self):
        print("After disable arpa zone validate NS records for both zones")
        sleep(5)
	output = os.popen("dig @"+config.grid_vip+" axfr .").read()
        output = output.split('\n')
        print(output)
        found1=False
        found2=False
        print(config.grid_vip)
        for index,value in enumerate(output):

            #print(output[index])
            match = re.match("1.1.in-addr.arpa.\s+\d+\s+IN\s+NS\s+"+config.grid_member1_fqdn+".", output[index])
            
            if match:
                found1 = True
                break
                
        for index,value in enumerate(output):
            match1 = re.match("2.1.in-addr.arpa.\s+\d+\s+IN\s+NS\s+"+config.grid_member1_fqdn+".", output[index])
            
            if match1:
                found2 = True
                break
        print(found1,found2)    
        if found1==True and found2==True:
            print("Success: Perform dig query")
            assert True
        else:
            print("Failed: Perform dig query")
            print(output)
            assert False
            
    @pytest.mark.run(order=8)
    def test_007_delete_arpa_zone(self): 
        print("Delete arpa zone")
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth')
        #print(get_ref)
        for ref in json.loads(get_ref):
            if '0.0.0.0%2F0' in ref['_ref']:
                response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
                
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: Deleted the 'in-addr.arpa' zone ")
                        assert False
                    else:
                        print("Success: Deleted the 'in-addr.arpa' zone ")
                        assert False
            
        restart_services()
        sleep(20)
        
        
    @pytest.mark.run(order=9)
    def test_008_after_deleting_zone_validate_NS_records(self):
        print("Check with dig")
	sleep(5)
        output = os.popen("dig @"+config.grid_vip+" axfr .").read()
        output = output.split('\n')
        print(output)
        found1=False
        found2=False
        print(config.grid_vip)
        for index,value in enumerate(output):

            #print(output[index])
            match = re.match("1.1.in-addr.arpa.\s+\d+\s+IN\s+NS\s+"+config.grid_member1_fqdn+".", output[index])
            
            if match:
                found1 = True
                break
                
        for index,value in enumerate(output):
            match1 = re.match("2.1.in-addr.arpa.\s+\d+\s+IN\s+NS\s+"+config.grid_member1_fqdn+".", output[index])
            
            if match1:
                found2 = True
                break
        print(found1,found2)    
        if found1==True and found2==True:
            print("Success: Perform dig query")
            assert True
        else:
            print("Failed: Perform dig query")
            print(output)
            assert False
            
    @pytest.mark.run(order=10)
    def test_009_cleanup_objects(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            if '1.1.0.0%2F16' in ref['_ref']:
                response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
                print(response)  
                if type(response) == tuple:          
                    if response[0]==400 or response[0]==401:      
                        assert False
                    else:
                        assert True
                        
            if '1.2.0.0%2F16' in ref['_ref']:
                response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
                print(response)  
                if type(response) == tuple:          
                    if response[0]==400 or response[0]==401:      
                        assert False
                    else:
                        assert True
            if '.' in ref['fqdn']:
                response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
                print(response)  
                if type(response) == tuple:          
                    if response[0]==400 or response[0]==401:      
                        assert False
                    else:
                        assert True
                        
        get_ref = ib_NIOS.wapi_request('GET', object_type="nsgroup", grid_vip=config.grid_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            if 'authServers' in ref['_ref']:
                response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
                print(response)           
                if type(response) == tuple:          
                    if response[0]==400 or response[0]==401:          
                        assert False
                    else:
                        assert True
            if 'rootServers' in ref['_ref']:
                response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
                print(response)           
                if type(response) == tuple:          
                    if response[0]==400 or response[0]==401:          
                        assert False
                    else:
                        assert True
                    
                    
                    
                    
                    

                    

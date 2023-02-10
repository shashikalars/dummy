#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
# Grid Set up required:                                                     #
#  1. Licenses : Grid DNS, DHCP, Grid, NIOS (IB-V1415)                      #
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
import shlex
from time import sleep
from subprocess import Popen, PIPE
import pexpect
import paramiko
from scapy import *
from scapy.utils import RawPcapReader
from scapy.all import *
import shutil

logging.basicConfig(filename='niosspt11321.log', filemode='w', level=logging.DEBUG)

class NIOSSPT_11321(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_000_create_New_AuthZone1(self):
        logging.info("Create a 'ford1.hrc.com' auth Zone with grid master")
      
        data = {"fqdn": "ford1.hrc.com","grid_primary": [{"name": config.grid_fqdn,"stealth":False}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
        logging.info(response)
        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==402:
                
                assert False
            else:
                
                assert True
                
        get_ref = ib_NIOS.wapi_request('GET',object_type='zone_auth', grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
           
            if 'ford1.hrc.com' in ref['fqdn']:
                logging.info("Success: Create a 'ford1.hrc.com' auth Zone with grid master")
                assert True
            else:
                logging.info("Failure: Create a 'ford1.hrc.com' auth Zone with grid master")
                assert False
           
       
            
    @pytest.mark.run(order=2)
    def test_001_create_New_AuthZone2(self):
        logging.info("Create a 'forestdnszones.dctest.com' auth Zone with grid master")
        data = {"fqdn": "forestdnszones.dctest.com","grid_primary": [{"name": config.grid_fqdn,"stealth":False}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
        logging.info(response)
        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==402:
                
                assert False
            else:
                
                assert True
         
        get_ref = ib_NIOS.wapi_request('GET',object_type='zone_auth', grid_vip=config.grid_vip)
        #print(get_ref)
        for ref in json.loads(get_ref):
           
            if 'forestdnszones.dctest.com' in ref['fqdn']:
                logging.info("Success: Create a 'forestdnszones.dctest.com' auth Zone with grid master")
                assert True
                break
            else:
                logging.info("Failure: Create a 'forestdnszones.dctest.com' auth Zone with grid master")
                continue
                assert False
           
        
    @pytest.mark.run(order=3)
    def test_002_create_New_AuthZone3(self):
        logging.info("Create a 'forestdnszones.test.com' auth Zone with grid master")
        data = {"fqdn": "forestdnszones.test.com","grid_primary": [{"name": config.grid_fqdn,"stealth":False}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
        logging.info(response)
        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==402:
                
                assert False
            else:
                
                assert True
        get_ref = ib_NIOS.wapi_request('GET',object_type='zone_auth', grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
           
            if 'forestdnszones.test.com' in ref['fqdn']:
                logging.info("Success: Create a 'forestdnszones.test.com' auth Zone with grid master")
                assert True
                break
            else:
                logging.info("Failure: Create a 'forestdnszones.test.com' auth Zone with grid master")
                continue
                assert False
    
        
    @pytest.mark.run(order=4)
    def test_003_create_New_AuthZone4(self):
        logging.info("Create a 'hrc.com' auth Zone with grid master")
        data = {"fqdn": "hrc.com","grid_primary": [{"name": config.grid_fqdn,"stealth":False}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
        logging.info(response)
        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==402:
                
                assert False
            else:
                
                assert True
        
        get_ref = ib_NIOS.wapi_request('GET',object_type='zone_auth', grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
           
            if 'hrc.com' in ref['_ref']:
                logging.info("Success: Create a 'hrc.com' auth Zone with grid master")
                assert True
                break
            else:
                logging.info("Failure: Create a 'hrc.com' auth Zone with grid master")
                continue
                assert False
                   
     
        
    @pytest.mark.run(order=5)
    def test_004_create_delegated_Zone1(self):
        logging.info("Create a 'forbes-delegation.hrc.com' delegated Zone")
        
        data = {"delegate_to": [{
                "address": "2.2.2.200", 
                "name": "del3.local"
                }], 
            "fqdn": "forbes-delegation.hrc.com", 
            "view": "default"
            }
        response = ib_NIOS.wapi_request('POST', object_type="zone_delegated", fields=json.dumps(data))
        logging.info(response)        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==402:
                
                assert False
            else:
                
                assert True
                
        get_ref = ib_NIOS.wapi_request('GET',object_type='zone_delegated', grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
           
            if 'forbes-delegation.hrc.com' in ref['fqdn']:
                logging.info("Success: Create a 'forbes-delegation.hrc.com' delegated Zone")
                assert True
                break
            else:
                logging.info("Failure: Create a 'forbes-delegation.hrc.com' delegated Zone")
                continue
                assert False
      
    @pytest.mark.run(order=6)
    def test_005_create_delegated_Zone2(self):
        logging.info("Create a 'ford-delegation.hrc.com' delegated Zone")
        data = {"delegate_to": [{
                "address": "1.1.1.220", 
                "name": "del4.local"
                }], 
            "fqdn": "ford-delegation.hrc.com", 
            "view": "default"
            }
        response = ib_NIOS.wapi_request('POST', object_type="zone_delegated", fields=json.dumps(data))
        logging.info(response)
        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==402:
                logging.info("Failure: Create A new delegated Zone")
                assert False
            else:
                logging.info("Success: Create A new delegated Zone")
                assert True

        get_ref = ib_NIOS.wapi_request('GET',object_type='zone_delegated', grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
           
            if 'ford-delegation.hrc.com' in ref['fqdn']:
                logging.info("Success: Create a 'ford-delegation.hrc.com' delegated Zone")
                assert True
                break
            else:
                logging.info("Failure: Create a 'ford-delegation.hrc.com' delegated Zone")
                continue
                assert False

        logging.info("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)
        
        
 
    @pytest.mark.run(order=7)
    def test_006_create_NS_record1(self):
        logging.info("Create NS record with name 'forestdnszones.dctest.com'")
        
        data = {"name": "forestdnszones.dctest.com", 
                "nameserver": config.grid_fqdn,
                "addresses": [{
                "address": "5.5.5.5",
                "auto_create_ptr": False}],
                "view": "default"}
        response = ib_NIOS.wapi_request('POST', object_type="record:ns", fields=json.dumps(data))
        logging.info(response)
        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==402:
                
                assert False
            else:
                
                assert True
        
        get_ref = ib_NIOS.wapi_request('GET',object_type='record:ns?_return_fields=name', grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
           
            if 'ford-delegation.hrc.com' in ref['name']:
                logging.info("Success: Create NS record with name 'forestdnszones.dctest.com'")
                assert True
                break
            else:
                logging.info("Failure: Create NS record with name 'forestdnszones.dctest.com'")
                continue
                assert False
                 
                
    @pytest.mark.run(order=8)
    def test_007_create_NS_record2(self):
        logging.info("Create NS record with name 'ford1.hrc.com'")
        data = {"name": "ford1.hrc.com", 
                "nameserver": config.grid_fqdn, 
                "addresses": [{
                "address": "6.6.6.6",
                "auto_create_ptr": False}],
                "view": "default"}
        response = ib_NIOS.wapi_request('POST', object_type="record:ns", fields=json.dumps(data))
        logging.info(response)
        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==402:
                
                assert False
            else:
                
                assert True
                
        get_ref = ib_NIOS.wapi_request('GET',object_type='record:ns?_return_fields=name', grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
           
            if 'ford1.hrc.com' in ref['name']:
                logging.info("Success: Create NS record with name 'ford1.hrc.com'")
                assert True
                break
            else:
                logging.info("Failure: Create NS record with name 'ford1.hrc.com'")
                continue
                assert False  
                
        logging.info("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)
        
        
    @pytest.mark.run(order=9)
    def test_008_create_A_record(self):
        logging.info("Create A new record")
        
        data = {"ipv4addr": "1.2.3.4", 
            "name": "ford1.hrc.com", 
            "view": "default"}
        response = ib_NIOS.wapi_request('POST', object_type="record:a", fields=json.dumps(data))
        logging.info(response)
        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==402:
                
                assert False
            else:
                
                assert True
        get_ref = ib_NIOS.wapi_request('GET',object_type='record:a?_return_fields=name', grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
           
            if 'ford1.hrc.com' in ref['name']:
                logging.info("Success: Create NS record with name 'ford1.hrc.com'")
                assert True
                break
            else:
                logging.info("Failure: Create NS record with name 'ford1.hrc.com'")
                continue
                assert False                          
   
        
    @pytest.mark.run(order=10)
    def test_009_validate_regex_search(self):
        logging.info("validate regex search function")
        
        list_val=["ford1_ns.hrc.com","ford1.hrc.com","ford-delegation.hrc.com"]
           
        get_ref = ib_NIOS.wapi_request('GET',object_type='search?fqdn~=^ford|..hrc.com', grid_vip=config.grid_vip)
        
        logging.info(get_ref)
        logging.info("===================================")
        for ref in json.loads(get_ref):
            try:
                if ref['fqdn'] in list_val or ref['name'] in list_val:
                    logging.info(ref)
                    logging.info("\n")
                    assert True
            except:
                pass
                
    @pytest.mark.run(order=11)
    def test_cleanup_objects(self):
        
        get_ref = ib_NIOS.wapi_request('GET',object_type="record:a")
        logging.info(get_ref)
        for ref in json.loads(get_ref):
            if '1.2.3.4' in ref['ipv4addr']:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])

        get_ref = ib_NIOS.wapi_request('GET',object_type="record:ns")
        #logging.info(get_ref)
        for ref in json.loads(get_ref):
            ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])
        
        get_ref = ib_NIOS.wapi_request('GET',object_type="zone_delegated")
        #logging.info(get_ref)
        for ref in json.loads(get_ref):
            ib_NIOS.wapi_request('DELETE',object_type=ref['_ref']) 
            
        get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth")
        #logging.info(get_ref)
        for ref in json.loads(get_ref):
            ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])
            
        logging.info("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)                
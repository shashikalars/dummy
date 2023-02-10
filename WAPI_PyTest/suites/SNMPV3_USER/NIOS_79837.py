#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
# Grid Set up required:                                                     #
#  1. Grid + Member                                                         #
#  2. Licenses : Grid,NIOS                                                  #
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


class NIOS_79837(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_create_an_SNMPv3_User_with_disable(self):
       print("Create an SNMPv3 User and disable it")
       
       data={"name":"snmptest","authentication_protocol":"NONE","privacy_protocol":"NONE","disable":True}
       response = ib_NIOS.wapi_request('POST',object_type="snmpuser",fields=json.dumps(data))
       print(response)
        
       if type(response) == tuple:
           if response[0]==200 :
               print("\n Success: Created SNMPv3 User\n")
               assert True
           else:
               print("\n Failure: Created SNMPv3 User\n")
               assert False
               

    @pytest.mark.run(order=2)
    def test_001_enable_snmp_trap_grid_level(self):
        response = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        userref = json.loads(response)[0]['_ref']
        userref = userref.encode('ascii', 'ignore')
        print(userref)
        
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting')
        getref=json.loads(get_ref)[0]['_ref']
        print(getref)
        data={"snmp_setting":{"snmpv3_traps_enable": True,"trap_receivers": [{"address": "10.36.198.1","user":userref}]}}
        response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400:
                if 'SNMPv3 user snmptest is disabled' in response[1]:
                    print("Success: SNMPv3 user snmptest is disabled")
                    assert True
            else:
                print("Success: SNMPv3 user snmptest is disabled")
                assert False

    @pytest.mark.run(order=3)
    def test_002_check_disable_SNMPv3_after_trap_configuration(self): 
        getref = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmpuser_ref = json.loads(getref)[0]['_ref']
        
        data={"disable":False}
        response = ib_NIOS.wapi_request('PUT',ref=snmpuser_ref,fields=json.dumps(data))
        print(response)
        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==404:

                if 'cannot disable SNMPv3 user snmptest' in response[1]:
                    print("\n Success: Cannot disable SNMPv3 user snmptest when SNMPv3 traps are configured for the user")
                    assert True
            else:
                print("\n Failure: Cannot disable SNMPv3 user snmptest when SNMPv3 traps are configured for the user")
                assert False
 
    @pytest.mark.run(order=4)
    def test_003_enable_snmp_trap_grid_level(self):
        print("\n")
        response = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmp_memref = json.loads(response)[0]['_ref']
        snmp_memref = snmp_memref.encode('ascii', 'ignore')
        print(snmp_memref)
        
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting')
        get_grid_ref=json.loads(get_ref)[0]['_ref']
        sleep(5)
        data={"snmp_setting":{"snmpv3_traps_enable": True,"trap_receivers": [{"address": "10.36.198.1","user":snmp_memref}]}}
        response=ib_NIOS.wapi_request('PUT',ref=get_grid_ref, fields=json.dumps(data))
        print(response)
        if type(response) == tuple:

            if response[0]==400 or response[0]==401 or response[0]==404:
                print("\n Success: Enable snmp trap on grid property (grid-level)")
                assert True
            else:
                print("\n Failure: Enable snmp trap on grid property (grid-level)")
                assert False 
 
    @pytest.mark.run(order=5)
    def test_004_check_disable_SNMPv3_after_trap_configuration_on_grid_level(self): 
        getref = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmpuser_ref = json.loads(getref)[0]['_ref']
        
        data={"disable":True}
        response = ib_NIOS.wapi_request('PUT',ref=snmpuser_ref,fields=json.dumps(data))
        print(response)
        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==404:

                if 'cannot disable SNMPv3 user snmptest' in response[1]:
                    print("\n Success: Cannot disable SNMPv3 user snmptest when SNMPv3 traps are configured on Grid-level")
                    assert True
            else:
                print("\n Failure: Cannot disable SNMPv3 user snmptest when SNMPv3 traps are configured on Grid-level")
                assert False
  
    @pytest.mark.run(order=6)
    def test_005_enable_snmp_trap_grid_master_level(self):
        print("\n")
        response = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmp_memref = json.loads(response)[0]['_ref']
        snmp_memref = snmp_memref.encode('ascii', 'ignore')
        print(snmp_memref)
        
        response = ib_NIOS.wapi_request('GET', object_type="member")
        memref = json.loads(response)[0]['_ref']
        print(memref)
        sleep(5)
        data={"snmp_setting":{"snmpv3_traps_enable": True,"trap_receivers": [{"address": "10.36.198.1","user":snmp_memref}]}}
        
        response=ib_NIOS.wapi_request('PUT',ref=memref, fields=json.dumps(data))
        print(response)
        if type(response) == tuple:

            if response[0]==400 or response[0]==401 or response[0]==404:
                if 'SNMPv3 user snmptest is disabled' in response[1]:
                    print("\n Success: Enable snmp trap on grid master level")
                    assert True
            else:
                print("\n Failure: Enable snmp trap on grid master level")
                assert False

    @pytest.mark.run(order=7)
    def test_006_check_disable_SNMPv3_after_trap_configuration_on_grid_master_level(self): 
        getref = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmpuser_ref = json.loads(getref)[0]['_ref']
        
        data={"disable":True}
        response = ib_NIOS.wapi_request('PUT',ref=snmpuser_ref,fields=json.dumps(data))
        print(response)
        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==404:
                print("Success: Cannot disable SNMPv3 user snmptest when SNMPv3 queries are configured on grid master")
                assert True
            else:
                print("Failure: Cannot disable SNMPv3 user snmptest when SNMPv3 queries are configured on grid master")
                assert False
                
    @pytest.mark.run(order=8)
    def test_007_enable_snmp_trap_member_level(self):
        print("\n")
        response = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmp_memref = json.loads(response)[0]['_ref']
        snmp_memref = snmp_memref.encode('ascii', 'ignore')
        print(snmp_memref)
        response = ib_NIOS.wapi_request('GET', object_type="member")
        memref = json.loads(response)[1]['_ref']
        print(memref)
        sleep(5)
        data={"snmp_setting":{"snmpv3_traps_enable": True,"trap_receivers": [{"address": "10.36.198.1","user":snmp_memref}]}}
        response=ib_NIOS.wapi_request('PUT',ref=memref, fields=json.dumps(data))
        print(response)
        if type(response) == tuple:

            if response[0]==400 or response[0]==401 or response[0]==404:
                if 'SNMPv3 user snmptest is disabled' in response[1]:
                    print("\n Success: Enable snmp trap on grid member level")
                    assert True
            else:
                print("\n Failure: Enable snmp trap on grid member level")
                assert False 
                
    @pytest.mark.run(order=9)
    def test_008_check_disable_SNMPv3_after_trap_configuration_on_member_level(self): 
        print("\n")
        getref = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmpuser_ref = json.loads(getref)[0]['_ref']
        
        data={"disable":True}
        response = ib_NIOS.wapi_request('PUT',ref=snmpuser_ref,fields=json.dumps(data))
        print(response)
        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==404:

                if 'cannot disable SNMPv3 user snmptest' in response[1]:
                    print("\n Success: Cannot disable SNMPv3 user snmptest when SNMPv3 traps are configured on Grid-member")
                    assert True
            else:
                print("\n Failure: Cannot disable SNMPv3 user snmptest when SNMPv3 traps are configured on Grid-member")
                assert False
 
    @pytest.mark.run(order=10)
    def test_009_create_an_SNMPv3_User_without_disable(self):
       print("Create an SNMPv3 User without disable it")
       
       data={"name":"snmptest1","authentication_protocol":"NONE","privacy_protocol":"NONE","disable":False}
       response = ib_NIOS.wapi_request('POST',object_type="snmpuser",fields=json.dumps(data))
       print(response)
        
       if type(response) == tuple:
           if response[0]==200 :
               print("\n Success: Created SNMPv3 User\n")
               assert True
           else:
               print("\n Failure: Created SNMPv3 User\n")
               assert False 
               
    @pytest.mark.run(order=11)
    def test_010_ovveride_snmp_trap_grid_master_level(self):
        print("\n")
        response = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        for ref in json.loads(response):
            if 'snmptest1' in ref['_ref']:
                snmp_memref = ref['_ref']
                print(snmp_memref)
            
        response = ib_NIOS.wapi_request('GET', object_type="member")
        memref = json.loads(response)[1]['_ref']
        print(memref)
        sleep(5)
        data={"snmp_setting":{"snmpv3_traps_enable": True,"trap_receivers": [{"address": "10.36.198.1","user":snmp_memref}]}}
        
        response=ib_NIOS.wapi_request('PUT',ref=memref, fields=json.dumps(data))
        print(response)
        if type(response) == tuple:

            if response[0]==200:
                print("\n Success: Enable snmp trap on grid master level with new SNMP user")
                assert True                 
            else:
                print("\n Failure: Enable snmp trap on grid master level with new SNMP user")
                assert False
                
    @pytest.mark.run(order=12)
    def test_011_cleanup(self):
        print("\n\n Clean up all created object\n\n")
        get_reff = ib_NIOS.wapi_request('GET', object_type="member")
     
        for ref in json.loads(get_reff):
            print(ref['_ref'])
            
            data={"snmp_setting":{"snmpv3_traps_enable": False,"trap_receivers": []}}
            response=ib_NIOS.wapi_request('PUT',ref=ref['_ref'], fields=json.dumps(data))
            print(response)
            if type(response) == tuple:

                if response[0]==400 or response[0]==401 or response[0]==404:
                   
                    print("Sucess: \n Deleting SNMP configuration on members ")
                    assert True
                    
                else:
                    print("Failure: \n Deleting SNMP configuration on members ")
                    assert False 
                    
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting')
        get_grid_ref=json.loads(get_ref)[0]['_ref']
        sleep(5)
        data={"snmp_setting":{"snmpv3_traps_enable": False,"trap_receivers": []}}
        response=ib_NIOS.wapi_request('PUT',ref=get_grid_ref, fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==404:     
                print("Sucess: \n Deleting SNMP configuration on GRID-LEVEL ")
                assert True
            else:
                print("Failure: \n Deleting SNMP configuration on GRID-LEVEL ")
                assert False
                
        get_ref = ib_NIOS.wapi_request('GET', object_type="snmpuser", grid_vip=config.grid_vip)

        for ref in json.loads(get_ref):
            if 'snmptest' in ref["_ref"] or 'snmptest1' in ref["_ref"]:
                response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
                print(response)  
                if type(response) == tuple:           
                    if response[0]==200:     
                        print("Sucess: \n Deleting SNMP user ")
                        assert True
                    else:
                        print("Failure: \n Deleting SNMP user ")
                        assert False
              
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)
       



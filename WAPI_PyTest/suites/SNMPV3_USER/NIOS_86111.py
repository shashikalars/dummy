#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
# Grid Set up required:                                                     #
#  1. Grid                                                                  #
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


class NIOS_86111(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_Start_DNS_Service_on_grid1(self):
        print("Start DNS Service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        print(get_ref)
        res = json.loads(get_ref)
        for i in res:
            ref=i["_ref"]
            print("Enable dns services")
            data = {"enable_dns": True}
            response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
            sleep(5)
            print(response)
            read  = re.search(r'200',response)
            for read in  response:
                assert True
                
    @pytest.mark.run(order=2)
    def test_001_Start_DNS_Service_on_grid2(self):
        print("Start DNS Service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns",grid_vip=config.grid2_vip)
        print(get_ref)
        res = json.loads(get_ref)
        for i in res:
            ref=i["_ref"]
            print("Enable dns services")
            data = {"enable_dns": True}
            response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data),grid_vip=config.grid2_vip)
            sleep(5)
            print(response)
            read  = re.search(r'200',response)
            for read in  response:
                assert True    

                
    @pytest.mark.run(order=3)
    def test_002_Add_the_Authoritative_zone_sprinklr_in_grid_2(self):

        print("Add the Authoritative zone sprinklr.com in grid 2")
        data={"fqdn":"sprinklr.com","grid_primary": [{"name": config.grid2_fqdn,"stealth": False}]}
        get_ref=ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data),grid_vip=config.grid2_vip)
        print(get_ref)
        print get_ref
        if type(get_ref)!=tuple:
            print("Restaring the grid")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid2_vip)
            ref = json.loads(grid)[0]['_ref']
            data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid2_vip)
            sleep(20)
            print("Restrting the grid")
            reference=ib_NIOS.wapi_request('GET', object_type="zone_auth",grid_vip=config.grid2_vip)
            reference=json.loads(reference)
            if "sprinklr.com" in reference[0]["fqdn"]:
                print("Test case execution passed")
                assert True
            else:
                print("Test case execution Failed")
                assert False
        else:
            print(get_ref)
            print("Test case execution failed")
            assert False

    @pytest.mark.run(order=4)
    def test_003_Add_the_Authoritative_zone_mashery_in_grid_2(self):

        print("Add the Authoritative zone mashery.com in grid 2")
        data={"fqdn":"mashery.com","grid_primary": [{"name": config.grid2_fqdn,"stealth": False}]}
        get_ref=ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data),grid_vip=config.grid2_vip)
        print(get_ref)
        print get_ref
        if type(get_ref)!=tuple:
            print("Restaring the grid")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid2_vip)
            ref = json.loads(grid)[0]['_ref']
            data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid2_vip)
            sleep(20)
            print("Restrting the grid")
            reference=ib_NIOS.wapi_request('GET', object_type="zone_auth",grid_vip=config.grid2_vip)
            reference=json.loads(reference)
            if "mashery.com" in reference[1]["fqdn"]:
                print("Test case execution passed")
                assert True
            else:
                print("Test case execution Failed")
                assert False
        else:
            print(get_ref)
            print("Test case execution failed")
            assert False

    @pytest.mark.run(order=5)
    def test_004_create_CNAME_record_sprinklr_zone(self):
        print("Creating CNAME record below sprinklr zone")
        data = {"canonical": "sprinklr.api.mashery.com","name": "api2.sprinklr.com","view": "default","ttl":60}
        cname_record_ref = ib_NIOS.wapi_request('POST',object_type='record:cname',fields=json.dumps(data),grid_vip=config.grid2_vip)
        print(cname_record_ref)
        if type(cname_record_ref) == tuple:
            if cname_record_ref[0]==200:
                print("Success: Creating CNAME record below sprinklr zone")
                assert True
            else:
                print("Failure: Creating CNAME record below sprinklr zone ")
                assert False
           
        print("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid2_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid2_vip)
        sleep(20)
        

    @pytest.mark.run(order=6)
    def test_005_create_CNAME_record_below_mashery_zone(self):
        print("Creating CNAME record below mashery zone")
        data = {"canonical": "sb-sprinklr.mashery.com","name": "sprinklr.api.mashery.com","ttl":300}
        cname_record_ref = ib_NIOS.wapi_request('POST',object_type='record:cname',fields=json.dumps(data),grid_vip=config.grid2_vip)
        print(cname_record_ref)
        if type(cname_record_ref) == tuple:
            if cname_record_ref[0]==200:
                print("Success: Creating CNAME record below mashery zone")
                assert True
            else:
                print("Failure: Creating CNAME record below mashery zone ")
                assert False
                
        print("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid2_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid2_vip)
        sleep(20)
        
    @pytest.mark.run(order=7)
    def test_006_create_First_A_record_below_mashery_zone(self):
        print("Create A record below mashery zone")
        data={"ipv4addr":"54.225.183.184","name":"sb-sprinklr.mashery.com","ttl":30}
        a_record_ref=ib_NIOS.wapi_request('POST',object_type='record:a',fields=json.dumps(data), grid_vip=config.grid2_vip)
        print(a_record_ref)
        if type(a_record_ref) == tuple:
            if a_record_ref[0]==200:
                print("Success: Creating 3sb-sprinklr A record below mashery zone")
                assert True
            else:
                print("Failure: Creating 3sb-sprinklr A record below mashery zone ")
                assert False


    @pytest.mark.run(order=8)
    def test_007_create_second_A_record_below_mashery_zone(self):
        print("\n\nCreate A record below mashery zone")
        data={"ipv4addr":"54.225.182.247","name":"sb-sprinklr.mashery.com","ttl":30}
        a_record_ref=ib_NIOS.wapi_request('POST',object_type='record:a',fields=json.dumps(data), grid_vip=config.grid2_vip)
        print(a_record_ref)
        if type(a_record_ref) == tuple:
            if a_record_ref[0]==200:
                print("Success: Creating 4sb-sprinklr A record below mashery zone")
                assert True
            else:
                print("Failure: Creating 4sb-sprinklr A record below mashery zone ")
                assert False


    @pytest.mark.run(order=9)
    def test_008_create_third_A_record_below_mashery_zone(self):
        print("Create A record below mashery zone")
        data={"ipv4addr":"54.225.183.182","name":"sb-sprinklr.mashery.com","ttl":30}
        a_record_ref=ib_NIOS.wapi_request('POST',object_type='record:a',fields=json.dumps(data), grid_vip=config.grid2_vip)
        print(a_record_ref)
        if type(a_record_ref) == tuple:
            if a_record_ref[0]==200:
                print("Success: Creating 5sb-sprinklr A record below mashery zone")
                assert True
            else:
                print("Failure: Creating 5sb-sprinklr A record below mashery zone ")
                assert False

    @pytest.mark.run(order=10)
    def test_009_add_Forwarders_and_Allow_Recursion_At_Grid_level(self):
        print("Add Forwarders and Allow Recursion At Grid level")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
        print(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        print ref1

        print("Modify Grid DNS Properties")
        data = {"allow_recursive_query": True,"forwarders": [config.grid2_vip],"enable_ftc":True,"ftc_expired_record_ttl":25}
        response = ib_NIOS.wapi_request('PUT',ref= ref1,fields=json.dumps(data))
        print response
        print(response)
        read  = re.search(r'200',response)
        for read in  response:
            assert True
        
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns", grid_vip=config.grid2_vip)
        print(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        print ref1
       
        data = {"allow_recursive_query": True}
        response = ib_NIOS.wapi_request('PUT',ref= ref1,fields=json.dumps(data), grid_vip=config.grid2_vip)
        print response
        print(response)
        read  = re.search(r'200',response)
        for read in  response:
            assert True
            
        print("Restart services on grid1\n\n")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data))
        
        
        print("Restart services on grid2")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid2_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data), grid_vip=config.grid2_vip)
        sleep(20)
        
    @pytest.mark.run(order=11)
    def test_010_Validate_all_the_records_should_have_TTL_greater_25(self):
        
        #dig_cmd = 'dig @'+str(config.grid_vip)+' api2.sprinklr.com'
        print("perform query for should have TTL greater 25")
        #dig_result = subprocess.check_output(dig_cmd, shell=True)
        output = os.popen("dig @"+config.grid_vip+" api2.sprinklr.com").read()
        output = output.split('\n')
        answer = False
        pattern = 0
        for line in output:
            print(line)
        match_line =".*.\s+[3-9][0-9]+\s+IN\s+.*"
        for line in output:
            match = re.match(match_line, line)
            if match:
                pattern = pattern+1
            
            if 'ANSWER SECTION' in line:
                answer = True
        if not answer or pattern!=5:
            print("Failure: Perform dig query")
            assert False
            
    @pytest.mark.run(order=12)
    def test_011_Validate_all_the_records_should_have_TTL_as_25(self):
        print("Sleep for 8 min to get update")
        sleep(430)
        print("perform query for should have TTL 25")

        output = os.popen("dig @"+config.grid_vip+" api2.sprinklr.com").read()
        output = output.split('\n')
        answer = False
        pattern = 0
        for line in output:
            print(line)
        #match_line =".*.\s+25\s+IN\s+.*"
        match_line=".*.\s+[2][5]+\s+IN\s+.*"
        for line in output:
            match = re.match(match_line, line)
            if match:
                pattern = pattern+1
                
            if 'ANSWER SECTION' in line:
                answer = True
        if not answer or pattern!=5:
            print("Failure: Perform dig query")
            assert False

    @pytest.mark.run(order=13)
    def test_012_Validate_all_the_records_should_have_TTL_greater_25(self):
        #print("Sleep for 8 min to get update")
        
        #dig_cmd = 'dig @'+str(config.grid_vip)+' api2.sprinklr.com'
        print("perform query for should have TTL greater 25")
        #dig_result = subprocess.check_output(dig_cmd, shell=True)
        output = os.popen("dig @"+config.grid_vip+" api2.sprinklr.com").read()
        output = output.split('\n')
        answer = False
        pattern = 0
        for line in output:
            print(line)
        match_line =".*.\s+[3-9][0-9]+\s+IN\s+.*"
        for line in output:
            match = re.match(match_line, line)
            if match:
                pattern = pattern+1
            
            if 'ANSWER SECTION' in line:
                answer = True
        if not answer or pattern!=5:
            print("Failure: Perform dig query, Bug-opened: NIOS-86111")
            assert False
            
    @pytest.mark.run(order=14)
    def test_013_cleanup(self):
        get_reff = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid2_vip)
        for ref in json.loads(get_reff):
            print(ref['_ref'])
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'], grid_vip=config.grid2_vip)
            print(response)  
            if type(response) == tuple:           
                if response[0]==200:     
                    assert True
                else:
                    assert False
                    
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
        print(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        print ref1

        data = {"allow_recursive_query": False,"forwarders": []}
        response = ib_NIOS.wapi_request('PUT',ref= ref1,fields=json.dumps(data))
        print response
        print(response)
        read  = re.search(r'200',response)
        for read in  response:
            assert True
               
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid2_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid2_vip)
        sleep(10)
       





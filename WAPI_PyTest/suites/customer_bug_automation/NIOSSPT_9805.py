#!/usr/bin/env python
__author__ = "Ashwini"
__email__  = "cma@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. SA GRID                                                                          #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415), Echo-system  Licenses               #
########################################################################################


import re
import config
import pytest
import unittest
import logging
import subprocess
import os
import json
import ib_utils.ib_NIOS as ib_NIOS
from time import sleep
import commands
import json, ast
import time
import sys
import pexpect
from ib_utils.log_capture import log_action as log
from ib_utils.log_validation import log_validation as logv

    
    
def get_reference_value_grid_superuser():
    logging.info("get reference value for GRID")
    get_ref = ib_NIOS.wapi_request('GET',object_type="grid",user="new",password="infoblox")
    logging.info(get_ref)
    ref1 = json.loads(get_ref)[0]['_ref']
    print("++++++++++++++++++++++",ref1)
    logging.info (ref1)
    return ref1

class Network(unittest.TestCase):
    


    @pytest.mark.run(order=1)
    def test_001_create_super_user_1(self):
        logging.info("Create super-user group for testing password history features")
        group = {"name":"super-user","superuser":True}
        get_ref_group = ib_NIOS.wapi_request('POST',object_type="admingroup", fields=json.dumps(group))
        if (get_ref_group[0] == 400):
            print("Duplicate object \'super-user\' of type \'admin_group\' already exists in the database")
            assert True
        else:
            print("Group \'super-user\' has been created")
        logging.info(get_ref_group)
        user = {"name":"new1","password":"infoblox","admin_groups":["super-user"]}
        get_ref = ib_NIOS.wapi_request('POST',object_type="adminuser", fields=json.dumps(user))
        if (get_ref[0] == 400):
            print("Duplicate object \'new' of type \'super-user\' already exists in the database")
        else:
            print("User \'new1\' has been created")
        logging.info (get_ref)
        res = json.loads(get_ref)
        logging.info (res)
        print("######@@@@@@@",res)


        
    @pytest.mark.run(order=2)
    def test_002_login_super_user_2(self):
        logging.info("Create super-user group for testing password history features")
        group = {"name":"super-user","superuser":True}
        get_ref_group = ib_NIOS.wapi_request('POST',object_type="admingroup", fields=json.dumps(group))
        if (get_ref_group[0] == 400):
            print("Duplicate object \'super-user\' of type \'admin_group\' already exists in the database")
            assert True
        else:
            print("Group \'super-user\' has been created")
        logging.info(get_ref_group)
        user = {"name":"new2","password":"infoblox","admin_groups":["super-user"]}
        get_ref = ib_NIOS.wapi_request('POST',object_type="adminuser", fields=json.dumps(user))
        if (get_ref[0] == 400):
            print("Duplicate object \'new' of type \'super-user\' already exists in the database")
        else:
            print("User \'new2\' has been created")
        logging.info (get_ref)
        res = json.loads(get_ref)
        logging.info (res)
        print("######@@@@@@@",res)
     
        
            
    @pytest.mark.run(order=3)
    def test_003_Create_New_AuthZone(self):
        logging.info("Create zone 'test.com'")
        data = {"fqdn": "test1.com","grid_primary": [{"name": config.grid_fqdn,"stealth":False}], "comment": "Auth zone" }
        response = ib_NIOS.wapi_request('POST', user="new1" , object_type="zone_auth" ,fields=json.dumps(data))
        #response = ib_NIOS.wapi_request('POST', object_type="zone_auth",params="?_function=dnssec_operation", fields=json.dumps(data))
        print response
        logging.info(response)
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        logging.info("zone is created")
        logging.info("Create grid_primary with required fields")
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        print ref1
        if (response[0]!=400):
           assert True
           print ("Locked zone")
        else:
           assert False


        data = {"grid_primary": [{"name": config.grid_fqdn,"stealth":False}]}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
        logging.info(response)
        logging.info("============================")
        print response    

        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("restart service is done successfully")
        sleep(30)

    @pytest.mark.run(order=4)
    def test_004_lock_zone(self):
            logging.info("Create grid_primary with required fields")
            get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth")
            for ref in json.loads(get_ref):
                print ref
                if 'test1.com' in ref['fqdn']:
                    ref1 = ref['_ref']
                    print ref1
                    data = {"locked":True}
                    response = ib_NIOS.wapi_request('PUT', user="new1" ,ref=ref1,fields=json.dumps(data))
                    logging.info(response)
                    print response
                    if (response[0]!=400):
                        assert True
                    else:
                        assert False
                    logging.info("zone is already locked successfully")
                    print response

    @pytest.mark.run(order=5)
    def test_005_add_A_record_in_zone(self):
            logging.info("Create A record")
            data={"name":"arec1.test1.com","ipv4addr":"2.2.2.2","view": "default"}
            response = ib_NIOS.wapi_request('POST', user="new1", object_type="record:a",fields=json.dumps(data))
            if (response[0]!=400):
                assert True
                print ("Added A record")
            else:
               print ("A record already exists")
            logging.info("Test Case 5 Execution Completed")
            
    @pytest.mark.run(order=6)
    def test_006_add_host_record_in_zone(self):
            logging.info("Create host record")
            data ={"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "2.2.4.2","mac": "11:11:11:11:11:15"}], "name": "host2.test1.com","view": "default"}
            response = ib_NIOS.wapi_request('POST', user="new1", object_type="record:host",fields=json.dumps(data))
            print response
            logging.info(response)
            read  = re.search(r'201',response)
            if (response[0]!=400):
                assert True
                print ("Host record created for the zone test1.com")
            else:
                assert False
            logging.info("Host record not created for the zone test1.com")
            logging.info("Test Case 6 Execution Completed")
            
    
            
    @pytest.mark.run(order=7)
    def test_007_delete_a_record_in_zone(self):
        logging.info("delete A record")
        #log("start","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("delete A record in zone")
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:a",user="new1")
        for ref in json.loads(get_ref):
            if 'arec1.test1.com' in ref['name']:
                ref1 = ref['_ref']
                print ref1

        delete_record = ib_NIOS.wapi_request('DELETE', object_type=ref1,user="new2")
        #delete_record=str(delete_record)
        print delete_record[1]
        validate="Cannot add/modify/delete records for zone \'test1.com\' as it is locked by user \'new1\'"
        #print validate
        if validate in delete_record[1]:
            assert True
        else:
            assert False
            
    
    
    @pytest.mark.run(order=8)
    def test_008_delete_host_record_in_zone(self):
        logging.info("delete Host record")
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:host")
        logging.info(get_ref)
        res = json.loads(get_ref)
        for ref in res:
            ref1 = ref['_ref']
            print (ref1)
        #data={"ipv4addr":"2.2.2.2","view": "default"}
        response = ib_NIOS.wapi_request('DELETE', object_type=ref1, user="new2")
        print response
        validate="Cannot add/modify/delete records for zone \'test1.com\' as it is locked by user \'new1\'"
        if validate in response[1]:
            assert True
        else:
            assert False
        logging.info("Test Case 08 Execution Completed")
            
    
            
            
    
        
        
    

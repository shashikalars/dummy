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
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv

logging.basicConfig(filename='niosspt11050.log', filemode='w', level=logging.DEBUG)

class NIOSSPT_11050(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_000_create_ACEs_for_admingroup(self):
        logging.info("Create a admin group called 'test'")
        
        data = {"name": "test",
                "superuser":True,
                "user_access": [{
                "address": "10.36.0.0/16",
                "permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('POST', object_type="admingroup", fields=json.dumps(data))
        logging.info(response)
        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==402:
                logging.info("Failure: Create a admingroup called 'test'")
                assert False
            else:
                logging.info("Success: Create a admingroup called 'test'")
                assert True

    @pytest.mark.run(order=2)
    def test_001_create_admin_user(self):
        logging.info("")
        data = {"admin_groups": ["test"],"auth_type": "LOCAL","name": "user1","password":"infoblox"}
        response = ib_NIOS.wapi_request('POST', object_type="adminuser", fields=json.dumps(data))
        logging.info(response)
        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==402:
                logging.info("Failure: Create A admin user called 'user1'")
                assert False
            else:
                logging.info("Success: Create A admin user called 'user1'")
                assert True                


    @pytest.mark.run(order=3)
    def test_002_try_to_login_appliances_using_authorized(self):
        logging.info("")
        log("start","/infoblox/var/audit.log",config.grid_vip)
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no user1@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >',timeout=30)
            child.sendline("exit")
            logging.info(child.before)
    
        except:
            assert True
        finally:
            child.close()

        log("stop","/infoblox/var/audit.log",config.grid_vip)
        LookFor=[".*user1.*Login_Allowed.*to.*Serial.*Console apparently_via.*Remote ip.*"]
        cnt=0
        for look in LookFor:
            logging.info(look)
            logs=logv(look,"/infoblox/var/audit.log",config.grid_vip)
            logging.info(logs)
            if logs:
                cnt=cnt+1
            else:
                cnt=cnt+0

        if cnt==1:
            logging.info(logs)
            logging.info("Success:Try to login appliances using authorized ")
            assert True
        else:
            logging.info("Failed:Try to login appliances using authorized")
            assert False

    @pytest.mark.run(order=4)
    def test_003_modify_ACEs_for_admingroup_(self):
        logging.info("modify user_access address of the admingroup called 'test' ")
        get_ref = ib_NIOS.wapi_request('GET', object_type='admingroup', grid_vip=config.grid_vip)
       
        for ref in json.loads(get_ref):
           if 'test' in ref['_ref']:
                data = {"user_access": [{
                    "address": "10.120.0.0/16",
                    "permission": "ALLOW"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
                
                logging.info(response)
                
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401 or response[0]==402:
                        logging.info("Failure: changing user_access address of the admingroup called 'test'")
                        assert False
                    else:
                        logging.info("Success: changing user_access address of the admingroup called 'test'")
                        assert True
                
    @pytest.mark.run(order=5)
    def test_004_try_to_login_appliances_using_unauthorized(self):

        log("start","/infoblox/var/audit.log",config.grid_vip)
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no user1@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >',timeout=30)
            child.sendline("exit")
            logging.info(child.before)
    
        except:
            assert True
        finally:
            child.close()


        log("stop","/infoblox/var/audit.log",config.grid_vip)
        LookFor=[".*user1.*Login_Denied.*apparently_via.*Remote ip.*"]
        cnt=0
        for look in LookFor:
            logging.info(look)
            logs=logv(look,"/infoblox/var/audit.log",config.grid_vip)
            logging.info(logs)
            if logs:
                cnt=cnt+1
            else:
                cnt=cnt+0

        if cnt==1:
            logging.info(logs)
            logging.info("Success:Try to login appliances using unauthorized client")
            assert True
        else:
            logging.info("Failed:Try to login appliances using unauthorized client")
            assert False


    @pytest.mark.run(order=6)
    def test_005_create_ACEs_for_admingroup_with_nonsuperuser(self):
        logging.info("Create a admin group called 'test1' with non superuser access")
        
        data = {"name": "test1",
                "superuser":False,
                "access_method": ["GUI",
                    "API",
                    "CLI"],
                "user_access": [{
                "address": "10.36.0.0/16",
                "permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('POST', object_type="admingroup", fields=json.dumps(data))
        logging.info(response)
        print(response)
        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==402:
                logging.info("Failure: Create a admin group called 'test1' with non superuser access")
                assert False
            else:
                logging.info("Success: Create a admin group called 'test1' with non superuser access")
                assert True

    @pytest.mark.run(order=7)
    def test_006_create_admin_user_with_nonsuperuser(self):
        logging.info("Create A admin user called 'user2'")
        data = {"admin_groups": ["test1"],"auth_type": "LOCAL","name": "user2","password":"infoblox"}
        response = ib_NIOS.wapi_request('POST', object_type="adminuser", fields=json.dumps(data))
        logging.info(response)
        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==402:
                logging.info("Failure: Create A admin user called 'user2'")
                assert False
            else:
                logging.info("Success: Create A admin user called 'user2'")
                assert True                


    @pytest.mark.run(order=8)
    def test_007_try_to_login_appliances_using_authorized_with_nonsuperuser(self):
        logging.info("")
        log("start","/infoblox/var/audit.log",config.grid_vip)
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no user2@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >',timeout=30)
            child.sendline("exit")
            logging.info(child.before)
    
        except:
            assert True
        finally:
            child.close()

        log("stop","/infoblox/var/audit.log",config.grid_vip)
        LookFor=[".*user2.*Login_Allowed.*to.*Serial.*Console apparently_via.*Remote ip.*"]
        cnt=0
        for look in LookFor:
            logging.info(look)
            logs=logv(look,"/infoblox/var/audit.log",config.grid_vip)
            logging.info(logs)
            if logs:
                cnt=cnt+1
            else:
                cnt=cnt+0

        if cnt==1:
            logging.info(logs)
            logging.info("Success:Try to login appliances using authorized with non superuser access")
            assert True
        else:
            logging.info("Failed:Try to login appliances using authorized with non superuser access")
            assert False

    @pytest.mark.run(order=9)
    def test_008_modify_ACEs_for_admingroup_with_nonsuperuser(self):
        logging.info("Modify user_access address of the admingroup called 'test1' ")
        get_ref = ib_NIOS.wapi_request('GET', object_type='admingroup', grid_vip=config.grid_vip)
       
        for ref in json.loads(get_ref):
           if 'test1' in ref['_ref']:
                data = {"user_access": [{
                    "address": "10.120.0.0/16",
                    "permission": "ALLOW"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
                
                logging.info(response)
                
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401 or response[0]==402:
                        logging.info("Failure: Modify user_access address of the admingroup called 'test1' ")
                        assert False
                    else:
                        logging.info("Success: Modify user_access address of the admingroup called 'test1' ")
                        assert True
                
    @pytest.mark.run(order=10)
    def test_009_try_to_login_appliances_using_unauthorized_with_nonsuperuser(self):

        log("start","/infoblox/var/audit.log",config.grid_vip)
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no user2@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >',timeout=30)
            child.sendline("exit")
            logging.info(child.before)
    
        except:
            assert True
        finally:
            child.close()


        log("stop","/infoblox/var/audit.log",config.grid_vip)
        LookFor=[".*user2.*Login_Denied.*apparently_via.*Remote ip.*"]
        cnt=0
        for look in LookFor:
            logging.info(look)
            logs=logv(look,"/infoblox/var/audit.log",config.grid_vip)
            logging.info(logs)
            if logs:
                cnt=cnt+1
            else:
                cnt=cnt+0

        if cnt==1:
            logging.info(logs)
            logging.info("Success:Try to login appliances using unauthorized with non superuser access")
            assert True
        else:
            logging.info("Failed:Try to login appliances using unauthorized non superuser access")
            assert False


    @pytest.mark.run(order=11)
    def test_010_modify_ACEs_for_admingroup_with_nonsuperuser(self):
        logging.info("Testing WAPI calls through user and checking able to run based on ACEs")
        get_ref = ib_NIOS.wapi_request('GET', object_type='adminuser?_return_fields=status', grid_vip=config.grid_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            
            if 'user1' in ref['_ref']:
                if "ACTIVE" in ref["status"]:
                    logging.info("Success: Testing WAPI calls through user and checking able to run based on ACEs")
                    assert True
                    break
            else:
                logging.info("Failure: Testing WAPI calls through user and checking able to run based on ACEs")
                continue
                assert False

                        
    @pytest.mark.run(order=12)
    def test_011_cleanup_object(self):
        logging.info("Clean up created object")
        get_ref = ib_NIOS.wapi_request('GET', object_type="adminuser", grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            if 'user1' in ref['_ref']:
                response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
                logging.info(response)   
                if type(response) == tuple:       
                    if response[0]==400 or response[0]==401:        
                        assert False
                    else:
                        assert True
                        
        
        get_ref = ib_NIOS.wapi_request('GET', object_type="adminuser", grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            if 'user2' in ref['_ref']:
                response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
                logging.info(response)   
                if type(response) == tuple:       
                    if response[0]==400 or response[0]==401:        
                        assert False
                    else:
                        assert True
                        
        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup", grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            if 'test' in ref['_ref']:
                response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
                logging.info(response)   
                if type(response) == tuple:       
                    if response[0]==400 or response[0]==401:        
                        assert False
                    else:
                        assert True   
                      
        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup", grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            if 'test1' in ref['_ref']:
                response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
                logging.info(response)   
                if type(response) == tuple:       
                    if response[0]==400 or response[0]==401:        
                        assert False
                    else:
                        assert True  

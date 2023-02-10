#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
# Grid Set up required:                                                     #
#  1. SA GRID with Licenses : DNS,DHCP                                      #
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

class NIOSSPT_10572(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_create_AD_Services(self):
        print("Create AD services")
        data={"ad_domain": "ad19187.com","domain_controllers": [{"auth_port": 389,"comment": "AD services","disabled": False,"encryption": "NONE","fqdn_or_ip": "10.34.98.56","use_mgmt_port": False}],"name": "adserver"}
        response = ib_NIOS.wapi_request('POST',object_type="ad_auth_service",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create AD services")
                assert False
            else:

                print("Success: Create AD services")
                assert True

    @pytest.mark.run(order=2)
    def test_001_create_LDAP_services(self):
        print("Create LDAP services")
        data={"ldap_group_attribute": "memberOf",
            "ldap_group_authentication_type": "GROUP_ATTRIBUTE",
            "ldap_user_attribute": "uid",
            "timeout":5,
            "retries":5,
            "recovery_interval":30,
            "search_scope": "SUBTREE",
            "name": "ldapserver",
            "servers": [
                {
                    "address": "10.197.38.101",
                    "authentication_type": "ANONYMOUS",
                    "base_dn": "dc=ldapserver,dc=local",
                    #"bind_user_dn": "cn=admin,dc=lab,dc=local",
                    #"bind_password":"infoblox",
                    "comment": "LDAP services",
                    "disable": False,
                    "encryption": "NONE",
                    "port": 389,
                    "use_mgmt_port": False,
                    "version": "V3"}
                      ]}
        response = ib_NIOS.wapi_request('POST',object_type="ldap_auth_service",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create LDAP services")
                assert False
            else:

                print("Success: Create LDAP services")
                assert True
    
        
        
    @pytest.mark.run(order=3)
    def test_002_create_TACACS_services(self):
        print("Create TACACS services")
        data={"acct_retries": 0,
        "acct_timeout": 1000,
        "auth_retries": 0,
        "auth_timeout": 5000,
        "name": "user1_tacacs",
        "servers": [
            {
                "address": "10.197.38.101",
                "auth_type": "CHAP",
                "shared_secret":"testing123",
                "comment": "shashi",
                "disable": False,
                "port": 49,
                "use_accounting": False,
                "use_mgmt_port": False
            }
        ]}
        response = ib_NIOS.wapi_request('POST',object_type="tacacsplus:authservice",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create TACACS services")
                assert False
            else:

                print("Success: Create TACACS services")
                assert True
    @pytest.mark.run(order=4)
    def test_003_create_a_groups(self):
        print("Create groups for AD,LDAP,TACACS services")
               
        
        data={"name": "asmgroup","comment":"group for AD services","superuser":True}
        response = ib_NIOS.wapi_request('POST',object_type="admingroup",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create group for AD services")
                assert False
            else:


                print("Success: Create group for AD services")
                assert True

        data={"name": "blox2","comment":"group for LDAP services","superuser":True}
        response = ib_NIOS.wapi_request('POST',object_type="admingroup",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create group for LDAP services")
                assert False
            else:

                print("Success: Create group for LDAP services")
                assert True

        data={"name": "infobloxgroup","comment":"group for TACACS services","superuser":True}
        response = ib_NIOS.wapi_request('POST',object_type="admingroup",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create group for TACACS services")
                assert False
            else:

                print("Success: Create group for TACACS services")
                assert True
                
        # print("Create a non-super users with anabling CLI")       
        # data={"name": "nonsuperone","comment":"group for TACACS services","superuser":False,"access_method":"CLI"}
        # response = ib_NIOS.wapi_request('POST',object_type="admingroup",fields=json.dumps(data))
        # print(response)
        # if type(response) == tuple:
            # if response[0]==400 or response[0]==401:
                # print("Failure: Create a non-super users with anabling CLI")
                # assert False
            # else:

                # print("Success: Create a non-super users with anabling CLI")
                # assert True
                
        # print("Create a non-super users with anabling CLI")       
        # data={"name": "nonsupertwo","comment":"group for TACACS services","superuser":False,"access_method":"CLI"}
        # response = ib_NIOS.wapi_request('POST',object_type="admingroup",fields=json.dumps(data))
        # print(response)
        # if type(response) == tuple:
            # if response[0]==400 or response[0]==401:
                # print("Failure: Create a non-super users with anabling CLI")
                # assert False
            # else:

                # print("Success: Create a non-super users with anabling CLI")
                # assert True
                
    @pytest.mark.run(order=5)
    def test_004_create_a_authpolicy_services(self):
        get_ref_ad = ib_NIOS.wapi_request('GET', object_type='ad_auth_service', grid_vip=config.grid_vip)
        get_ref_ldap = ib_NIOS.wapi_request('GET', object_type='ldap_auth_service', grid_vip=config.grid_vip)
        get_ref_tacacs = ib_NIOS.wapi_request('GET', object_type='tacacsplus:authservice', grid_vip=config.grid_vip)
        ref_ad=''
        ref_ldap=''
        ref_tacacs=''
        #print(get_ref_ad)
        for ref in json.loads(get_ref_ad):
             ref_ad+=ref['_ref']
        for ref in json.loads(get_ref_ldap):
             ref_ldap+=ref['_ref']
        for ref in json.loads(get_ref_tacacs):
             ref_tacacs+=ref['_ref']

        get_ref = ib_NIOS.wapi_request('GET', object_type='authpolicy?_return_fields=auth_services', grid_vip=config.grid_vip)
        print("\n")
  
        print(ref_ad,ref_ldap,ref_tacacs)
        for ref in json.loads(get_ref):
           
            data={"auth_services": [
               ref['auth_services'][0],
               ref_ad,
               ref_ldap,
               ref_tacacs
               ]}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            
            print(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    print("Failure: Add groups to Auth policy group")
                    assert False
                else:

                    print("Success: Add groups to Auth policy group")
                    assert True



    @pytest.mark.run(order=6)
    def test_005_create_a_authpolicy_groups(self):
        get_ref_s1 = ib_NIOS.wapi_request('GET', object_type='admingroup?name=asmgroup', grid_vip=config.grid_vip)
        get_ref_s2 = ib_NIOS.wapi_request('GET', object_type='admingroup?name=cloud-api-only', grid_vip=config.grid_vip)
        get_ref_s3 = ib_NIOS.wapi_request('GET', object_type='admingroup?name=infobloxgroup', grid_vip=config.grid_vip)
        get_ref_s4 = ib_NIOS.wapi_request('GET', object_type='admingroup?name=saml-group', grid_vip=config.grid_vip)
        get_ref_s5 = ib_NIOS.wapi_request('GET', object_type='admingroup?name=blox2', grid_vip=config.grid_vip)
        get_ref_s6 = ib_NIOS.wapi_request('GET', object_type='admingroup?name=splunk-reporting-group', grid_vip=config.grid_vip)
        #print(type(get_ref_s1))
        dat=[]
        dat.append(json.loads(get_ref_s1)[0]['name'])
        dat.append(json.loads(get_ref_s2)[0]['name'])
        dat.append(json.loads(get_ref_s3)[0]['name'])
        dat.append(json.loads(get_ref_s4)[0]['name'])
        dat.append(json.loads(get_ref_s5)[0]['name'])
        dat.append(json.loads(get_ref_s6)[0]['name'])
        print(dat)
        data={"admin_groups": dat}
        
        print("Add groups to Auth policy groups")
        get_ref = ib_NIOS.wapi_request('GET', object_type='authpolicy', grid_vip=config.grid_vip)
        print("\n")
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
           
            print(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    print("Failure: Add groups to Auth policy group")
                    assert False
                else:

                    print("Success: Add groups to Auth policy group")
                    assert True
                    
        data={"default_group": "blox2"}
        get_ref = ib_NIOS.wapi_request('GET', object_type='authpolicy', grid_vip=config.grid_vip)
        print("\n")
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create a LDAP default group")
                assert False
            else:

                print("Success: Create a LDAP default group")
                assert True
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)
        
    @pytest.mark.run(order=7)
    def test_006_validating_AD_services(self):
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no manoj@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('Infoblox@123')
            #child.sendline('shekhar/Infoblox@123')

            child.expect('Infoblox >',timeout=60)
            child.sendline("exit")
            print(child.before)
            assert True
        except:
            assert False
        finally:
            child.close()

        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        LookFor=["Authorization succeeded for user123","Admin group asmgroupn found in remote method reply","AD Authentication Succeeded"]
        cnt=0
        for look in LookFor:
            print(look)
            logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                cnt=cnt+1
            else:
                cnt=cnt+0

        if cnt==3:
            logging.info(logs)
            logging.info("Success")
            assert True
        else:
            logging.info("Failed")
            assert False

    @pytest.mark.run(order=8)
    def test_007_validating_TACACS_services(self):
        sleep(20)
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no user1_tacacs@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >',timeout=60)
            child.sendline("exit")
            print(child.before)
            assert True
        except:
            assert False
        finally:
            child.close()

        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        LookFor=["Authorization succeeded for user1","Admin group infobloxgroup found in remote method reply","TACACS Authentication Succeeded"]
        cnt=0
        for look in LookFor:
            print(look)
            logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                cnt=cnt+1
            else:
                cnt=cnt+0

        if cnt==3:
            logging.info(logs)
            logging.info("Success")
            assert True
        else:
            logging.info("Failed")
            assert False

    @pytest.mark.run(order=9)
    def test_008_validating_LDAP_services(self):
        
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no user1_ldap@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=100)
            child.sendline('infoblox')
            child.expect('Infoblox >',timeout=100)
            child.sendline("exit")
            print(child.before)
            assert True
        except Exception as e:
            print(e)
            assert False
        finally:
            child.close()

        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        LookFor=[".*Authorization succeeded for user1.*",".*User group.*default.*blox2.*",".*Successfully authenticated NIOS superuser.*user1.*"]
        cnt=0
        for look in LookFor:
            print(look)
            logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                cnt=cnt+1
            else:
                cnt=cnt+0

        if cnt==3:
            logging.info(logs)
            logging.info("Success")
            assert True
        else:
            logging.info("Failed")
            assert False

    @pytest.mark.run(order=10)
    def test_009_cleanup_object(self):
        data={"default_group": "admin-group"}
        get_ref = ib_NIOS.wapi_request('GET', object_type='authpolicy', grid_vip=config.grid_vip)
        print("\n")
        for ref in json.loads(get_ref):
            
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
              
                assert False
            else:

                assert True
        
        get_ref = ib_NIOS.wapi_request('GET', object_type='authpolicy', grid_vip=config.grid_vip)
        print("\n")
        data={"admin_groups":[]}
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
           
            print(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    assert False
                else:
                    assert True
                    
        get_ref = ib_NIOS.wapi_request('GET', object_type='authpolicy?_return_fields=auth_services', grid_vip=config.grid_vip)
        print("\n")
  
        
        for ref in json.loads(get_ref):
           
            data={"auth_services": [
               ref['auth_services'][0]]}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            
            print(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                   
                    assert False
                else:

                    assert True
        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup", grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            if 'asmgroup' in ref['_ref'] or 'infobloxgroup' in ref['_ref'] or 'blox2' in ref['_ref']:
                response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
                 
                print(response)
                        
                if type(response) == tuple:
                            
                    if response[0]==400 or response[0]==401:
                                
                        assert False
                    else:
                        assert True  
                    
        get_ref = ib_NIOS.wapi_request('GET', object_type="ad_auth_service", grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
             
            print(response)
                    
            if type(response) == tuple:
                        
                if response[0]==400 or response[0]==401:
                            
                    assert False
                else:
                    assert True     
        get_ref = ib_NIOS.wapi_request('GET', object_type="ldap_auth_service", grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
             
            print(response)
                    
            if type(response) == tuple:
                        
                if response[0]==400 or response[0]==401:
                            
                    assert False
                else:
                    assert True       
        get_ref = ib_NIOS.wapi_request('GET', object_type="tacacsplus:authservice", grid_vip=config.grid_vip)
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



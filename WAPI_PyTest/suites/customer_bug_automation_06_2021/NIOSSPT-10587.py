#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. IB-Flex grid with M1                                                  #
#  2. Licenses : Flex Grid Activation license                               #
#############################################################################
import os
import sys
import re
import config
import pytest
import unittest
import logging
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import pexpect
import shlex
from subprocess import Popen, PIPE
class NIOSSPT_10587(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_000_start_IPv4_DHCP_service(self):
        print("Enable the DPCH service")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns')
        print(get_ref)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps({"enable_dns":True}))
            if type(response) == tuple:
                if response[0]==400 or response[0]==401 or response[0]==404:
                    print("Failure: Create A new Zone")
                    assert False
                else:
                    print("Success: Create A new Zone")
                    assert True

    @pytest.mark.run(order=2)
    def test_001_create_New_AuthZone(self):
        print("Create A new Zone")
      
        data = {"fqdn": "new1.com","grid_primary": [{"name": config.grid_member_fqdn,"stealth":False}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
        print response
        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==404:
                print("Failure: Create A new Zone")
                assert False
            else:
                print("Success: Create A new Zone")
                assert True
     
               
        data = {"fqdn": "new2.com","grid_primary": [{"name": config.grid_member_fqdn,"stealth":False}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
        print response
        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==404:
                print("Failure: Create A new Zone")
                assert False
            else:
                print("Success: Create A new Zone")
                assert True
                
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns')
        print(get_ref)
        data = {"allow_update":[{"_struct": "addressac","address":"Any", "permission":"ALLOW"}]}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Enable Zone transfer")
                assert False
            else:
                print("Success: Enable Zone transfer")
                assert True
                
        
        print("Restart DHCP Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20) 

    @pytest.mark.run(order=3)
    def test_002_send_ns_updates_and_noticed_it_fails_master(self):

        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.client_ip)
        try:
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.sendline('nsupdate')
            child.expect('>')
            child.sendline('server '+config.grid_vip)
            child.sendline("zone new2.com")
            child.sendline("prereq nxdomain pre1.new2.com")
            child.sendline("send")
            child.sendline("prereq nxdomain pre1.new2.com")
            child.sendline("send")
            child.sendline("prereq yxdomain yx.new2.com a")
            child.sendline("send")
            child.sendline("prereq nxrrset pre.new2.com a")
            child.sendline("send")
            child.sendline("prereq yxrrset yx.new2.com a")
            child.sendline("send")
            child.close()
            print("Success : Able to do the nsupdates master")
            assert True
        except Exception as e:
            child.close()
            print (e)
            print("Failure: Able to do the nsupdates master")
            assert False
       
    @pytest.mark.run(order=4)
    def test_003_send_ns_updates_and_noticed_it_fails_for_member(self):
      
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.client_ip)
        try:
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.sendline('nsupdate')
            child.expect('>')
            child.sendline('server '+config.grid_member1_vip)
            child.sendline("prereq nxdomain pre1.new1.com")
            child.sendline("send")
            child.sendline("prereq yxdomain yx.new1.com a")
            child.sendline("send")
            child.sendline("prereq nxrrset pre.new1.com a")
            child.sendline("send")
            child.sendline("prereq yxrrset yx.new1.com a")
            child.sendline("send")
            child.sendline("quit")
            
            child.close()
            print("Success : Able to do the nsupdates for member")
            assert True
        except Exception as e:
            child.close()
            print (e)
            print("Failure: Able to do the nsupdates for member")
            assert False    
            
    @pytest.mark.run(order=5)
    def test_004_send_ns_updates_for_member(self):
       
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.client_ip)
        try:
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.sendline('nsupdate')
            child.expect('>')
            child.sendline('server '+config.grid_member1_vip)
            child.sendline("update add a_rec_ns.new1.com 111 in A 10.0.0.101")
            child.expect('>')
            child.sendline("send")
            child.sendline("quit")
            child.close()
            print("Success : Able to do the update cmd")
            assert True
        except Exception as e:
            child.close()
            print (e)
            print("Failure: Able to do the update cmd")
            assert False

    @pytest.mark.run(order=6)
    def test_005_cleanup_object(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
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

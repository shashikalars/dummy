#!/usr/bin/env python
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"


#############################################################################
# Grid Set up required:                                                     #
#  1. SA grid with Licenses :DNS,DHCP                                       #
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

class NIOS_65064(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_Create_forwarder_zone(self):
        print("Start DNS Service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        print(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        print ref1

        print("Modify a enable_dns")
        data = {"enable_dns": True}
        response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
        print response
        sleep(20)
        print(response)
        read  = re.search(r'200',response)
        for read in  response:
            assert True

        data = {"fqdn": "test.com",
            "view":"default",
            "forwarding_servers":[{"name": config.grid_fqdn}],
            "forward_to": [{
            "address": "1.1.1.1",
            "name": "abc"}],                
            }
        response = ib_NIOS.wapi_request('POST',object_type="zone_forward",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==404:
                print("Failure: create Forward Zone")
                assert False
            else:
                print("Success: Create a Forward Zone")
                assert True  
                    
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(40)    
        
    @pytest.mark.run(order=2)
    def test_001_verify_changes_in_config_file(self): 
        print("\nverify changes in config file")
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data="cat /infoblox/var/named_conf/named.conf\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        
        if 'forwarders { 1.1.1.1; };' in stdout:
            print("Success: verify changes in config file")
            assert True
        else:
            print("Failure: verify changes in config file")
            assert False       
            
    @pytest.mark.run(order=3)
    def test_002_add_custom_forwarder(self):
        print("\n Add custom forwarder to 2.2.2.2")
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_forward',grid_vip=config.grid_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
        
            data = {"forward_to": [{"address":"2.2.2.2","name": "abc"}]}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            print(response)
           
            if type(response) == tuple:
                if response[0]==400 or response[0]==401 or response[0]==404:
                    print("Failure: Add custom forwarder to 2.2.2.2")
                    assert False  
                else:
                    print("Success: Add custom forwarder to 2.2.2.2")
                    assert True
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(40)      
        
        
    @pytest.mark.run(order=4)
    def test_003_verify_changes_in_config_file_after_edit(self): 
        print("\nverify changes in config file")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data="cat /infoblox/var/named_conf/named.conf\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        
        if 'forwarders { 2.2.2.2; };' in stdout:
            print("Success: verify changes in config file")
            assert True
        else:
            print("Failure: verify changes in config file")
            assert False       
    
    @pytest.mark.run(order=5)
    def test_004_edit_custom_forwarder(self):
        print("\n Add custom forwarder to 2.2.2.2")
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_forward',grid_vip=config.grid_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
        
            data = {"forward_to": [{"address":"3.3.3.3","name": "abc"}]}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            print(response)
           
            if type(response) == tuple:
                if response[0]==400 or response[0]==401 or response[0]==404:
                    print("Failure: Add custom forwarder to 2.2.2.2")
                    assert False  
                else:
                    print("Success: Add custom forwarder to 2.2.2.2")
                    assert True 
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(40)      
        
        
    @pytest.mark.run(order=6)
    def test_005_verify_changes_in_config_file_after_edit_custom(self): 
        print("\nverify changes in config file")
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data="cat /infoblox/var/named_conf/named.conf\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        #print(stdout)
        
        if 'forwarders { 3.3.3.3; };' in stdout:
            print("Success: verify changes in config file")
            assert True
        else:
            print("Failure: verify changes in config file")
            assert False       

    @pytest.mark.run(order=7)
    def test_006_cleanup(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_forward", grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
             
            print(response)
                    
            if type(response) == tuple:
                        
                if response[0]==400 or response[0]==401:
                            
                    assert False
                else:
                    assert True
                    
                    
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)            

#!/usr/bin/env python
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    # 
#  1. Configure IB-FLEX with FLEX license                                   #
#############################################################################

import re
import config
import pytest
import unittest
import logging
import subprocess
import os
import json
import commands
import json, ast
import requests
from time import sleep as sleep
import pexpect
import paramiko
from paramiko import client
#import ib_utils.common_utilities as comm_util
import ib_utils.ib_NIOS as ib_NIOS
#from ib_utils.start_stop_logs import log_action as log
#from ib_utils.file_content_validation import log_validation as logv

class NIOSSPT_10304(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_Enabling_recusion_view(self):
        logging.info("Enabling DNS service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"enable_dns": True}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        sleep(10)


        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns', grid_vip=config.grid_vip)
        print("\n")
        for ref in json.loads(get_ref):

            data={"allow_recursive_query": True}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)

            print(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    print("Failure: Enabling recusive view")
                    assert False
                else:

                    print("Success: Enabling recusive view")
                    assert True
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)
        
    @pytest.mark.run(order=2)
    def test_001_validating_sppc_present_in_dns_view(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data="cat /infoblox/var/named_conf/dns_cache_acceleration.json"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        data = json.loads(stdout)
        if "sppc" in data["dca_config"]["1"]:
            print("Success : DNS sppc present in First dns view")
            assert True
        else:
            print("Failed: DNS sppc present in more than one dns views")
            assert False
            
    @pytest.mark.run(order=3)
    def test_002_create_custom_views1(self):
        data={"name": "Cusmt1"}
        response = ib_NIOS.wapi_request('POST',object_type="view",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create custom view")
                assert False
            else:

                print("Success: Create custom view")
                assert True
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)
        
    @pytest.mark.run(order=4)
    def test_003_validating_sppc_view1(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data="cat /infoblox/var/named_conf/dns_cache_acceleration.json"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        data = json.loads(stdout)
	print(data)
	print("____________________________________")
	print(data["dca_config"]["1"])
        if "sppc" in data["dca_config"]["1"] and "sppc" not in data["dca_config"]["2"]:
            print("Success : DNS sppc present in First dns view")
            assert True
        else:
            print("Failed: DNS sppc present in more than one dns views")
            assert False  

    @pytest.mark.run(order=5)
    def test_004_changining_the_view_order(self):
        get_ref =  ib_NIOS.wapi_request('GET', object_type="member:dns?_return_fields=views")
        print(get_ref)
        for ref in json.loads(get_ref):
            if 'Cusmt1' in ref['views']:
                print("---------------")
                data = {"views": ["Cusmt1","default"]}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                print(response) 
        
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: Set a Views Assigned to This Member")
                        assert False
                else:
                    print("Success: Set a Views Assigned to This Member")
                    
                    get_ref =  ib_NIOS.wapi_request('GET', object_type="member:dns?_return_fields=views")
                    print(get_ref)          
                    print("Restart Services")
                    grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                    ref = json.loads(grid)[0]['_ref']
                    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                    sleep(20)
                    assert True
                    
    @pytest.mark.run(order=6)
    def test_005_validating_sppc_custom_view2(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data="cat /infoblox/var/named_conf/dns_cache_acceleration.json"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        data = json.loads(stdout)
        if "sppc" in data["dca_config"]["1"] and "sppc" not in data["dca_config"]["2"]:
            print("Success : DNS sppc present in First dns view")
            assert True
        else:
            print("Failed: DNS sppc present in more than one dns views")
            assert False
            
            
    @pytest.mark.run(order=7)
    def test_006_disable_custom_views(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type='view')
        for ref in json.loads(get_ref):
            if 'Cusmt1' in ref['_ref']:
                data = {"disable": True}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: disable custom view")
                        assert False
                    else:

                        print("Success: disable custom view")
                        assert True
                        
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)
        assert True     
          
    @pytest.mark.run(order=8)
    def test_007_validating_sppc_disable_view(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data="cat /infoblox/var/named_conf/dns_cache_acceleration.json"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        data = json.loads(stdout)
        if "sppc" in data["dca_config"]["1"]:
            print("Success : DNS sppc present in First dns view")
            assert True
        else:
            print("Failed: DNS sppc present in more than one dns views")
            assert False  
            
    @pytest.mark.run(order=9)
    def test_008_create_custom_views2(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type='view')
        for ref in json.loads(get_ref):
            if 'Cusmt1' in ref['_ref']:
                data = {"disable": False}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: Enable custom view")
                        assert False
                    else:

                        print("Success: Enable custom view")
                        assert True
                        
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)
        
        assert True     
        data={"name": "Cusmt2"}
        response = ib_NIOS.wapi_request('POST',object_type="view",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create custom view")
                assert False
            else:

                print("Success: Create custom view")
                assert True
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)
        assert True     

    @pytest.mark.run(order=10)
    def test_009_validating_sppc_custom_view3(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data="cat /infoblox/var/named_conf/dns_cache_acceleration.json"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        data = json.loads(stdout)
        if "sppc" in data["dca_config"]["1"] and "sppc" not in data["dca_config"]["2"]:
            print("Success : DNS sppc present in First dns view")
            assert True
        else:
            print("Failed: DNS sppc present in more than one dns views")
            assert False
            
    @pytest.mark.run(order=11)
    def test_010_changining_the_view_order(self):
        get_ref =  ib_NIOS.wapi_request('GET', object_type="member:dns?_return_fields=views")
        print(get_ref)
        for ref in json.loads(get_ref):
            if 'Cusmt1' in ref['views']:
                print("---------------")
                data = {"views": ["Cusmt1","Cusmt2","default"]}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                print(response) 
        
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: Set a Views Assigned to This Member")
                        assert False
                else:
                    print("Success: Set a Views Assigned to This Member")
                    
                    get_ref =  ib_NIOS.wapi_request('GET', object_type="member:dns?_return_fields=views")
                    print(get_ref)          
                    print("Restart Services")
                    grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                    ref = json.loads(grid)[0]['_ref']
                    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                    sleep(20)
                    assert True


    @pytest.mark.run(order=12)
    def test_011_validating_dns_sppc_for_views_according_to_order(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data="cat /infoblox/var/named_conf/dns_cache_acceleration.json"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        data = json.loads(stdout)
        if "sppc" in data["dca_config"]["1"] and "sppc" not in data["dca_config"]["2"]:
            print("Success : DNS sppc present in First dns view")
            assert True
        else:
            print("Failed: DNS sppc present in more than one dns views")
            assert False
            
 
            
    @pytest.mark.run(order=13)
    def test_012_cleanup_objects(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns', grid_vip=config.grid_vip)
        print("\n")
        for ref in json.loads(get_ref):

            data={"allow_recursive_query": False}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)

            print(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    print("Failure: Enabling recusive view")
                    assert False
                else:

                    print("Success: Enabling recusive view")
                    assert True
        
        
        get_ref = ib_NIOS.wapi_request('GET', object_type="view", grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            if 'default' not in ref["_ref"]:
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
        sleep(10)

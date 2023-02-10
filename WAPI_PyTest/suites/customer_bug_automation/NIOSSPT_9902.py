#!/usr/bin/env python
__author__ = "Rajath Patavardhan"
__email__  = "rpatavardhan@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  SA Grid Master with Grid and DNS license                                 #
#############################################################################



import re
import config
import pytest
import unittest
import logging
import subprocess
import os
import json
import ib_utils.ib_NIOS as ib_NIOS
import commands
import json, ast
import requests
from time import sleep as sleep
import pexpect
import paramiko
from paramiko import client
#from log_capture import log_action as log
#from log_validation import log_validation as logv
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as comm_util
#from ib_utils.start_stop_logs import log_action as log
#from ib_utils.file_content_validation import log_validation as logv

def display_msg(x):
    logging.info(x)
    print("")
    print(x)

class SSH:
    client=None

    def __init__(self,address):
        logging.info ("Log Validation Script")
        logging.info ("connecting to server \n : ", address)
        self.client=client.SSHClient()
        self.client.set_missing_host_key_policy(client.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        self.client.connect(address, username='root', pkey = mykey)

    def send_command(self,command):
        if(self.client):
            stdin, stdout, stderr = self.client.exec_command(command)
            result=stdout.read()
            return result
        else:
            logging.info("Connection not opened.")
      
    
class NIOSSPT_9902(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_101_add_three_acls(self):
        display_msg("Adding three Named ACLs")
        data = {"name": "first", "access_list": [{"_struct": "addressac","address": "127.0.0.1","permission": "ALLOW"}, {"_struct": "addressac","address": "10.1.1.1","permission": "ALLOW"}, {"_struct": "addressac","address": "10.1.1.2","permission": "ALLOW"}]}
        response=ib_NIOS.wapi_request('POST', object_type="namedacl",fields=json.dumps(data), grid_vip=config.grid_vip)
        ref1 = response
        print ref1
        data = {"name": "second", "access_list": [{"_struct": "addressac","address": "40.40.40.1","permission": "ALLOW"},{"_struct": "addressac","address": "50.50.0.0/16","permission": "ALLOW"}]}
        response=ib_NIOS.wapi_request('POST', object_type="namedacl",fields=json.dumps(data), grid_vip=config.grid_vip)
        ref2 = response
        print ref2
        data = {"name": "third", "access_list": [{"_struct": "addressac","address": "10.2.2.2","permission": "ALLOW"}, {"_ref": ref1}, {"_ref": ref2},{"_struct": "addressac","address": "10.3.3.3","permission": "ALLOW"}]}
        response=ib_NIOS.wapi_request('POST', object_type="namedacl",fields=json.dumps(data), grid_vip=config.grid_vip)
        ref3 = response
        print ref3
        display_msg("ACLs added successfully")
        
        
    @pytest.mark.run(order=2)
    def test_102_update_grid_dns_properties(self):
        display_msg("Update Grid DNS Properties and Set allow_transfer to 3rd ACL")
        response = ib_NIOS.wapi_request('GET', object_type="grid:dns")
        dnsref = json.loads(response)[0]['_ref']
        print dnsref
        data = {"allow_update": [{ "_struct": "addressac", "address": "1.2.3.4","permission": "ALLOW"}, {"_struct": "addressac","address": "20.20.0.0/16","permission": "ALLOW"}]}
        response=ib_NIOS.wapi_request('PUT',ref=dnsref,fields=json.dumps(data), grid_vip=config.grid_vip)
        print response
        data = {"allow_recursive_query": True}
        response=ib_NIOS.wapi_request('PUT', ref=dnsref, fields=json.dumps(data))
        print response
        display_msg("Done")
        get_ref = ib_NIOS.wapi_request('GET', object_type='namedacl')
        for ref in json.loads(get_ref):
            if ref['name'] == 'third':
                data = {"allow_transfer": [{"_ref":ref['_ref']}]}
                response=ib_NIOS.wapi_request('PUT', ref=dnsref, fields=json.dumps(data))
                print response
                break


    @pytest.mark.run(order=3)
    def test_103_create_custome_view(self): 
        display_msg("Create custom network view")
        data={"name": "customnetview"}
        response=ib_NIOS.wapi_request('POST', object_type="networkview",fields=json.dumps(data))
        zoneref = response
        print response

    @pytest.mark.run(order=4)
    def test_104_add_records_in_custom_view(self):     
        zoneref = ib_NIOS.wapi_request('GET', object_type='networkview')
        for ref in json.loads(zoneref):
            if ref['name'] == 'customnetview':
                display_msg("Add _abc.com and xyz.custom.com in customnetview")
                data = {"_ref":zoneref, "fqdn":"_abc.com", "view": "default.customnetview","grid_primary": [{ "name": config.grid_fqdn,"stealth": False}]}
                response=ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data))
                print response
                data = {"_ref":zoneref, "fqdn":"xyz_custom.com", "view": "default.customnetview","grid_primary": [{ "name": config.grid_fqdn,"stealth": False}],"allow_transfer": [{"_struct": "addressac","address": "3.3.3.3","permission": "ALLOW"}]}
                response=ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data))
                print response
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        display_msg("Failed to add DNS records")
                        assert False
                break
        
    @pytest.mark.run(order=5)
    def test_105_add_record_in_default_view(self): 
        get_ref = ib_NIOS.wapi_request('GET', object_type='namedacl')
        for ref in json.loads(get_ref):
            if ref['name'] == 'third':
                display_msg("Add xyz_custom.com in dafault view")
                data = {"fqdn":"xyz_custom.com", "view": "default","grid_primary": [{ "name": config.grid_fqdn,"stealth": False}],"allow_transfer": [{"_ref": ref['_ref']}]}
                response=ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data))
                print response
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        display_msg("Failed to add DNS records")
                        assert False
            break
        
    @pytest.mark.run(order=6)
    def test_106_add_records(self):  
        get_ref = ib_NIOS.wapi_request('GET', object_type='namedacl')
        for ref in json.loads(get_ref):
            if ref['name'] == 'third':
                display_msg("Add foo.com with grid primary and dummy external secondary with allow transfer select third named acl")
                data = {"fqdn":"foo.com", "view": "default","grid_primary": [{ "name": config.grid_fqdn,"stealth": False}],"allow_transfer": [{"_ref": ref['_ref']}], "external_secondaries": [{ "name": "dummy.com","address":"1.2.3.4"}]}
                response=ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data))
                print response
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        display_msg("Failed to add DNS records")
                        assert False
            break

    @pytest.mark.run(order=7)
    def test_107_start_DNS_service(self):
        display_msg("start DNS service\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        print (ref1)
        data = {"enable_dns": True}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        sleep(10)
        logging.info(response)
        print (response)
        display_msg("Wait for 10 sec....\n")
        sleep(10)
        print("DNS service started")    
        
    @pytest.mark.run(order=8)
    def test_108_validate_infoblox_logs(self):
        display_msg("Starting Infoblox Logs")
        connection=SSH(str(config.grid_vip))
        result=connection.send_command("cat \/infoblox\/var\/infoblox.log")
        keyword1=len(re.findall(r'SYNTAX ERROR', result))
        keyword2=len(re.findall(r'unknown option', result))
        if ((keyword1 == 0) and (keyword2 == 0)): 
            display_msg("Error not found, Test case passed")
            assert True
        else:
            display_msg("Error found, Test case failed")
            assert False 
  
  
    @pytest.mark.run(order=9)
    def test_109_stop_DNS_service(self):
        display_msg("stop DNS service\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"enable_dns": False}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        sleep(10)
        display_msg("Wait for 10 sec....\n")
        sleep(10)
        print("DNS service stopped")    


    @pytest.mark.run(order=10)
    def test_110_add_aces(self):
        display_msg("Update ACEs under Grid DNS Properties and Set allow_updates to 3rd ACL")
        response = ib_NIOS.wapi_request('GET', object_type="grid:dns")
        dnsref = json.loads(response)[0]['_ref']
        print dnsref
        get_ref = ib_NIOS.wapi_request('GET', object_type='namedacl')
        for ref in json.loads(get_ref):
            if ref['name'] == 'third':
                data = {"allow_recursive_query": True, "allow_transfer": [],"allow_update": [{"_ref":ref['_ref']}] }
                response=ib_NIOS.wapi_request('PUT', ref=dnsref, fields=json.dumps(data))
                print response
            break
        
    @pytest.mark.run(order=11)
    def test_111_start_DNS_service(self):
        display_msg("start DNS service\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        print (ref1)
        data = {"enable_dns": True}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        sleep(10)
        logging.info(response)
        print (response)
        display_msg("Wait for 10 sec....\n")
        sleep(10)
        print("DNS service started")         

    @pytest.mark.run(order=12)
    def test_112_validate_infoblox_logs(self):
        display_msg("Starting Infoblox Logs")
        connection=SSH(str(config.grid_vip))
        result=connection.send_command("cat \/infoblox\/var\/infoblox.log")
        keyword1=len(re.findall(r'SYNTAX ERROR', result))
        keyword2=len(re.findall(r'unknown option', result))
        if ((keyword1 == 0) and (keyword2 == 0)): 
            display_msg("Error not found, Test case passed")
            assert True
        else:
            display_msg("Error found, Test case failed")
            assert False 
   
    @pytest.mark.run(order=13)
    def test_113_stop_DNS_service(self):
        display_msg("stop DNS service\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"enable_dns": False}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        sleep(10)
        display_msg("Wait for 10 sec....\n")
        sleep(10)
        print("DNS service stopped")  


    @pytest.mark.run(order=14)
    def test_114_add_aces(self):
        display_msg("Update ACEs under Grid DNS Properties and Set allow_queries to 3rd ACL")
        response = ib_NIOS.wapi_request('GET', object_type="grid:dns")
        dnsref = json.loads(response)[0]['_ref']
        print dnsref
        get_ref = ib_NIOS.wapi_request('GET', object_type='namedacl')
        for ref in json.loads(get_ref):
            if ref['name'] == 'third':
                data = {"allow_recursive_query": True, "allow_transfer": [],"allow_update": [], "allow_query": [{"_ref":ref['_ref']}]}
                response=ib_NIOS.wapi_request('PUT', ref=dnsref, fields=json.dumps(data))
                print response
            break
        
    @pytest.mark.run(order=15)
    def test_115_start_DNS_service(self):
        display_msg("start DNS service\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        print (ref1)
        data = {"enable_dns": True}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        sleep(10)
        logging.info(response)
        print (response)
        display_msg("Wait for 10 sec....\n")
        sleep(10)
        print("DNS service started")         

    @pytest.mark.run(order=16)
    def test_116_validate_infoblox_logs(self):
        display_msg("Starting Infoblox Logs")
        connection=SSH(str(config.grid_vip))
        result=connection.send_command("cat \/infoblox\/var\/infoblox.log")
        keyword1=len(re.findall(r'SYNTAX ERROR', result))
        keyword2=len(re.findall(r'unknown option', result))
        if ((keyword1 == 0) and (keyword2 == 0)): 
            display_msg("Error not found, Test case passed")
            assert True
        else:
            display_msg("Error found, Test case failed")
            assert False 
   
    @pytest.mark.run(order=17)
    def test_117_stop_DNS_service(self):
        display_msg("stop DNS service\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"enable_dns": False}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        sleep(10)
        display_msg("Wait for 10 sec....\n")
        sleep(10)
        print("DNS service stopped")            

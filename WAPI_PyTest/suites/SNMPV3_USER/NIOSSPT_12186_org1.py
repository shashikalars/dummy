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
from  ib_utils.log_capture import log_action as log
from  ib_utils.log_validation import log_validation as logv


class NIOSSPT_12186(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_create_an_SNMPv3_User(self):
       print("Create an SNMPv3 User")

       data={"name":"snmpUser1","authentication_protocol":"SHA","privacy_protocol":"AES","privacy_password":"infoblox1","authentication_password":"infoblox1"}

       response = ib_NIOS.wapi_request('POST',object_type="snmpuser",fields=json.dumps(data))
       print(response)
        
       if type(response) == tuple:
           if response[0]==200:
               print("\nSuccess: Created SNMPv3 User\n")
               assert True
           else:
               assert False
               

    @pytest.mark.run(order=2)
    def test_001_enable_snmp_query_grid_level(self):
       
        log("start","/var/log/syslog",config.grid_vip)
        response = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmp_memref = json.loads(response)[0]['_ref']
        snmp_memref = snmp_memref.encode('ascii', 'ignore')
        print(snmp_memref)
        
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting')
        getref=json.loads(get_ref)[0]['_ref']
        print(getref)
        
        data={"snmp_setting":{"snmpv3_queries_enable": True,"snmpv3_queries_users": [{"user":snmp_memref}]}}
        response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:
                assert True
            else:
                assert False
        sleep(30)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor=".*NET-SNMP.*AgentX subagent connected.*"
 
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(logs)
        if logs:
            assert True 
        else:
            assert False
            
    @pytest.mark.run(order=3)
    def test_002_Validate_snmpwalk_cmd_working_SHA_AES_Grid_Level(self):  
        
        getref = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        print(getref)
        snmpuser_name = json.loads(getref)[0]["name"]
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data='snmpwalk -v3 -l authPriv -u '+snmpuser_name+' -a SHA -A "infoblox1" -x AES -X "infoblox1" '+config.grid_vip+'| grep master'
        stdin, stdout, stderr = client.exec_command(data)
        sleep(2)
        stdout=stdout.read()
        print(data,stdout)
        if 'openvpn-master' in stdout:
            print("\nSuccess : snmpwalk command SHA->AES  work successfully on GRID-LEVEL\n")
            client.close()
            assert True
        else:
            client.close()
            assert False
                   

    @pytest.mark.run(order=4)
    def test_003_Validate_snmpwalk_cmd_working_SHA_DES_Grid_Level(self):  
        getref = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmpuser_ref = json.loads(getref)[0]['_ref']
        
        data={"authentication_protocol":"SHA","privacy_protocol":"DES","privacy_password":"infoblox1","authentication_password":"infoblox1"}
        response = ib_NIOS.wapi_request('PUT',ref=snmpuser_ref,fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:
                assert False
            else:
                assert True
        sleep(30)
        snmpuser_name = json.loads(getref)[0]["name"]
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data='snmpwalk -v3 -l authPriv -u '+snmpuser_name+' -a SHA -A "infoblox1" -x DES -X "infoblox1" '+config.grid_vip+'| grep master'
        stdin, stdout, stderr = client.exec_command(data)
        sleep(2)
        stdout=stdout.read()
        print(data,stdout)
        if 'openvpn-master' in stdout:
            print("\nSuccess : snmpwalk command SHA->DES  work successfully on GRID-LEVEL\n")
            client.close()
            assert True
        else:
            client.close()
            assert False
               

    @pytest.mark.run(order=5)
    def test_004_Validate_snmpwalk_cmd_working_MD5_AES_Grid_Level(self):   
        getref = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmpuser_ref = json.loads(getref)[0]['_ref']
        
        data={"authentication_protocol":"MD5","privacy_protocol":"AES","privacy_password":"infoblox1","authentication_password":"infoblox1"}
        response = ib_NIOS.wapi_request('PUT',ref=snmpuser_ref,fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:
                assert False
            else:
                assert True
        sleep(30)       
        snmpuser_name = json.loads(getref)[0]["name"]
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data='snmpwalk -v3 -l authPriv -u '+snmpuser_name+' -a MD5 -A "infoblox1" -x AES -X "infoblox1" '+config.grid_vip+'| grep master'
        stdin, stdout, stderr = client.exec_command(data)
        sleep(2)
        stdout=stdout.read()
        print(data,stdout)
        if 'openvpn-master' in stdout:
            print("\nSuccess : snmpwalk command MD5->AES work successfully on GRID-LEVEL\n")
            client.close()
            assert True
        else:
            client.close()
            assert False
            
    @pytest.mark.run(order=6)
    def test_005_Validate_snmpwalk_cmd_working_MD5_DES_Grid_Level(self):   
        getref = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmpuser_ref = json.loads(getref)[0]['_ref']
        
        data={"authentication_protocol":"MD5","privacy_protocol":"DES","privacy_password":"infoblox1","authentication_password":"infoblox1"}
        response = ib_NIOS.wapi_request('PUT',ref=snmpuser_ref,fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:
                assert False
            else:
                assert True
        sleep(30)  
        snmpuser_name = json.loads(getref)[0]["name"]
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data='snmpwalk -v3 -l authPriv -u '+snmpuser_name+' -a MD5 -A "infoblox1" -x DES -X "infoblox1" '+config.grid_vip+'| grep master'
        stdin, stdout, stderr = client.exec_command(data)
        sleep(2)
        stdout=stdout.read()
        print(data,stdout)
        if 'openvpn-master' in stdout:
            print("\nSuccess : snmpwalk command MD5->DES work successfully on GRID-LEVEL\n")
            client.close()
            assert True
        else:
            client.close()
            assert False
        
         
    @pytest.mark.run(order=7)
    def test_006_enable_snmp_query_on_grid_master_level(self):
        print("\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting')
        get_grid_ref=json.loads(get_ref)[0]['_ref']
        
        data={"snmp_setting":{"snmpv3_queries_enable": False,"snmpv3_queries_users": []}}
        response=ib_NIOS.wapi_request('PUT',ref=get_grid_ref, fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:     
                    assert True
            else:
                assert False
                
        response = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmp_memref = json.loads(response)[0]['_ref']
        snmp_memref = snmp_memref.encode('ascii', 'ignore')
        print(snmp_memref)
        
        response = ib_NIOS.wapi_request('GET', object_type="member")
        memref = json.loads(response)[0]['_ref']
        print(memref)
        
        data={"use_snmp_setting":False,"snmp_setting":{"snmpv3_queries_enable": True,"snmpv3_queries_users": [{"user":snmp_memref}]}}
        
        response=ib_NIOS.wapi_request('PUT',ref=memref, fields=json.dumps(data))
        print(response)
        if type(response) == tuple:

            if response[0]==200:
                print("Success: Enable snmp query on grid master level")
                assert False
            else:
                assert True
        
        sleep(30)
        
        
    @pytest.mark.run(order=8)
    def test_007_Validate_snmpwalk_cmd_working_SHA_AES_Grid_Master_Level(self):   
        getref = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmpuser_ref = json.loads(getref)[0]['_ref']
        
        #data={"authentication_protocol":"SHA","privacy_protocol":"AES","privacy_password":"infoblox1","authentication_password":"infoblox1"}
        
        data={"authentication_protocol":"SHA","privacy_protocol":"AES","privacy_password":"infoblox1","authentication_password":"infoblox1"}
        response = ib_NIOS.wapi_request('PUT',ref=snmpuser_ref,fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:
                assert False
            else:
                assert True
        sleep(30) 
        snmpuser_name = json.loads(getref)[0]["name"]
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data='snmpwalk -v3 -l authPriv -u '+snmpuser_name+' -a SHA -A "infoblox1" -x AES -X "infoblox1" '+config.grid_vip+'| grep master'
        stdin, stdout, stderr = client.exec_command(data)
        sleep(2)
        stdout=stdout.read()
        print(data,stdout)
        if 'openvpn-master' in stdout:
            print("\nSuccess : snmpwalk command SHA->AES work successfully on GRID-MASTER-LEVEL\n")
            client.close()
            assert True
        else:
            client.close()
            assert False
       
    @pytest.mark.run(order=9)
    def test_008_Validate_snmpwalk_cmd_working_SHA_DES_Grid_Master_Level(self):  
        getref = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmpuser_ref = json.loads(getref)[0]['_ref']
        
       
        data={"authentication_protocol":"SHA","privacy_protocol":"DES","privacy_password":"infoblox1","authentication_password":"infoblox1"}

        response = ib_NIOS.wapi_request('PUT',ref=snmpuser_ref,fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:
                assert False
            else:
                assert True
        sleep(30)      
        snmpuser_name = json.loads(getref)[0]["name"]
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data='snmpwalk -v3 -l authPriv -u '+snmpuser_name+' -a SHA -A "infoblox1" -x DES -X "infoblox1" '+config.grid_vip+'| grep master'
        stdin, stdout, stderr = client.exec_command(data)
        sleep(2)
        stdout=stdout.read()
        print(data,stdout)
        if 'openvpn-master' in stdout:
            print("\nSuccess : snmpwalk command SHA->DES work successfully on GRID-MASTER-LEVEL\n")
            client.close()
            assert True
        else:
            client.close()
            assert False
        
                 
            
    @pytest.mark.run(order=10)
    def test_009_Validate_snmpwalk_cmd_working_MD5_AES_Grid_Master_Level(self):   
        getref = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmpuser_ref = json.loads(getref)[0]['_ref']
        
        data={"authentication_protocol":"MD5","privacy_protocol":"AES","privacy_password":"infoblox1","authentication_password":"infoblox1"}
        response = ib_NIOS.wapi_request('PUT',ref=snmpuser_ref,fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:
                assert False
            else:
                assert True
        sleep(30)        
        snmpuser_name = json.loads(getref)[0]["name"]
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data='snmpwalk -v3 -l authPriv -u '+snmpuser_name+' -a MD5 -A "infoblox1" -x AES -X "infoblox1" '+config.grid_vip+'| grep master'
        stdin, stdout, stderr = client.exec_command(data)
        sleep(2)
        stdout=stdout.read()
        print(data,stdout)
        if 'openvpn-master' in stdout:
            print("\nSuccess : snmpwalk command MD5->AES work successfully on GRID-MASTER-LEVEL\n")
            client.close()
            assert True
        else:
            client.close()
            assert False
                 
    @pytest.mark.run(order=11)
    def test_010_Validate_snmpwalk_cmd_working_MD5_DES_Grid_Master_Level(self):   
        getref = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmpuser_ref = json.loads(getref)[0]['_ref']
        
        
        data={"authentication_protocol":"MD5","privacy_protocol":"DES","privacy_password":"infoblox1","authentication_password":"infoblox1"}
        response = ib_NIOS.wapi_request('PUT',ref=snmpuser_ref,fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:
                assert False
            else:
                assert True
        sleep(30)       
        snmpuser_name = json.loads(getref)[0]["name"]
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data='snmpwalk -v3 -l authPriv -u '+snmpuser_name+' -a MD5 -A "infoblox1" -x DES -X "infoblox1" '+config.grid_vip+'| grep master'
        stdin, stdout, stderr = client.exec_command(data)
        sleep(2)
        stdout=stdout.read()
        print(data,stdout)
        if 'openvpn-master' in stdout:
            print("\nSuccess : snmpwalk command MD5->DES work successfully on GRID-MASTER-LEVEL\n")
            client.close()
            assert True
        else:
            client.close()
            assert False
           
    @pytest.mark.run(order=12)
    def test_011_enable_snmp_query_on_grid_member_level(self):
        print("\n")
        get_reff = ib_NIOS.wapi_request('GET', object_type="member")
        get_reff = json.loads(response)[0]['_ref']
        
        data={"use_snmp_setting":True,"snmp_setting":{"snmpv3_queries_enable": False,"snmpv3_queries_users": []}}
        response=ib_NIOS.wapi_request('PUT',ref=get_reff, fields=json.dumps(data))
        print(response)
        if type(response) == tuple:

            if response[0]==200:
               
                assert True
            else:
                assert False 
                    
        response = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmp_memref = json.loads(response)[0]['_ref']
        snmp_memref = snmp_memref.encode('ascii', 'ignore')
        print(snmp_memref)
        
        response = ib_NIOS.wapi_request('GET', object_type="member")
        memref = json.loads(response)[1]['_ref']
        print(memref)
        sleep(30)
        data={"use_snmp_setting":False,"snmp_setting":{"snmpv3_queries_enable": True,"snmpv3_queries_users": [{"user":snmp_memref}]}}
        
        response=ib_NIOS.wapi_request('PUT',ref=memref, fields=json.dumps(data))
        print(response)
        if type(response) == tuple:

            if response[0]==200:
                
                assert False
            else:
                print("Success: Enable snmp query on grid member level")
                assert True
        sleep(30)

    @pytest.mark.run(order=13)
    def test_012_Validate_snmpwalk_cmd_working_SHA_AES_Grid_Member_Level(self):   
        getref = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmpuser_ref = json.loads(getref)[0]['_ref']
        
        data={"authentication_protocol":"SHA","privacy_protocol":"AES","privacy_password":"infoblox1","authentication_password":"infoblox1"}
        response = ib_NIOS.wapi_request('PUT',ref=snmpuser_ref,fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:
                assert False
            else:
                assert True
        sleep(30)       
        snmpuser_name = json.loads(getref)[0]["name"]
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data='snmpwalk -v3 -l authPriv -u '+snmpuser_name+' -a SHA -A "infoblox1" -x AES -X "infoblox1" '+config.grid_member1_vip+'| grep member'
        stdin, stdout, stderr = client.exec_command(data)
        sleep(2)
        stdout=stdout.read()
        print(data,stdout)
        print(type(stdout))
        if 'openvpn-member' in stdout:
            print("\nSuccess : snmpwalk command SHA->AES work successfully on GRID-MEMBER-LEVEL\n")
            client.close()
            assert True
        else:
            print("Failure: open bug -> NIOS-87010")
            client.close()
            assert False
        
    @pytest.mark.run(order=14)
    def test_013_Validate_snmpwalk_cmd_working_SHA_DES_Grid_Member_Level(self):  
        getref = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmpuser_ref = json.loads(getref)[0]['_ref']
       
        data={"authentication_protocol":"SHA","privacy_protocol":"DES","privacy_password":"infoblox1","authentication_password":"infoblox1"}
        response = ib_NIOS.wapi_request('PUT',ref=snmpuser_ref,fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:
                assert False
            else:
                assert True
        sleep(30)        
        snmpuser_name = json.loads(getref)[0]["name"]
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data='snmpwalk -v3 -l authPriv -u '+snmpuser_name+' -a SHA -A "infoblox1" -x DES -X "infoblox1" '+config.grid_member1_vip+'| grep member'
        stdin, stdout, stderr = client.exec_command(data)
        sleep(2)
        stdout=stdout.read()
        print(data,stdout)
        print(data)
        if 'openvpn-member' in stdout:
            print("\nSuccess : snmpwalk command SHA->DES work successfully on GRID-MEMBER-LEVEL\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: open bug -> NIOS-87010")
            assert False
        
          
    @pytest.mark.run(order=15)
    def test_014_Validate_snmpwalk_cmd_working_MD5_AES_Grid_Member_Level(self):   
        getref = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmpuser_ref = json.loads(getref)[0]['_ref']
        
        data={"authentication_protocol":"MD5","privacy_protocol":"AES","privacy_password":"infoblox1","authentication_password":"infoblox1"}
        response = ib_NIOS.wapi_request('PUT',ref=snmpuser_ref,fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:
                assert False
            else:
                assert True
        sleep(30)       
        snmpuser_name = json.loads(getref)[0]["name"]
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data='snmpwalk -v3 -l authPriv -u '+snmpuser_name+' -a MD5 -A "infoblox1" -x AES -X "infoblox1" '+config.grid_member1_vip+'| grep member'
        stdin, stdout, stderr = client.exec_command(data)
        sleep(2)
        stdout=stdout.read()
        print(data,stdout)
        if 'openvpn-member' in stdout:
            print("\nSuccess : snmpwalk command MD5->AES work successfully on GRID-MEMBER-LEVEL\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: open bug -> NIOS-87010")
            assert False
            
    @pytest.mark.run(order=16)
    def test_015_Validate_snmpwalk_cmd_working_MD5_DES_Grid_Member_Level(self):   
        getref = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmpuser_ref = json.loads(getref)[0]['_ref']
      
        data={"authentication_protocol":"MD5","privacy_protocol":"DES","privacy_password":"infoblox1","authentication_password":"infoblox1"}
        response = ib_NIOS.wapi_request('PUT',ref=snmpuser_ref,fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:
                assert False
            else:
                assert True
        sleep(30)       
        snmpuser_name = json.loads(getref)[0]["name"]
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data='snmpwalk -v3 -l authPriv -u '+snmpuser_name+' -a MD5 -A "infoblox1" -x AES -X "infoblox1" '+config.grid_member1_vip+'| grep member'
        stdin, stdout, stderr = client.exec_command(data)
        sleep(2)
        stdout=stdout.read()
        print(data,stdout)
        if 'openvpn-member' in stdout:
            print("\nSuccess : snmpwalk command MD5->DES work successfully on GRID-MEMBER-LEVEL\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: open bug -> NIOS-87010")
            assert False
                                 
            
    @pytest.mark.run(order=17)
    def test_016_Validate_snmpwalk_cmd_working_SHA_AES_Grid_Master_Level_after_changing_passwd(self):  
        log("start","/var/log/syslog",config.grid_vip)
        getref = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmpuser_ref = json.loads(getref)[0]['_ref']
        
        data={"authentication_protocol":"SHA","privacy_protocol":"AES","privacy_password":"Infoblox1","authentication_password":"Infoblox1"}
        response = ib_NIOS.wapi_request('PUT',ref=snmpuser_ref,fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:
                assert False
            else:
                assert True
        sleep(30)       
        snmpuser_name = json.loads(getref)[0]["name"]
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data='snmpwalk -v3 -l authPriv -u '+snmpuser_name+' -a SHA -A "Infoblox1" -x AES -X "Infoblox1" '+config.grid_vip+'| grep master'
        stdin, stdout, stderr = client.exec_command(data)
        sleep(2)
        stdout=stdout.read()
        print(data,stdout)
        if 'openvpn-master' in stdout:
            print("\nSuccess : snmpwalk command SHA->AES work successfully on GRID-MASTER-LEVEL\n")
            client.close()
            assert True
        else:
            client.close()
            #print("Failure: open bug -> NIOS-87010")
            assert False
        
        
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor=".*snmpd.*Turning on AgentX master support.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        if logs:
            assert True
        else:
            assert False
            
    @pytest.mark.run(order=18)
    def test_017_Validate_snmpwalk_cmd_working_SHA_AES_Grid_Member_Level(self):   
        getref = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmpuser_ref = json.loads(getref)[0]['_ref']

        data={"authentication_protocol":"SHA","privacy_protocol":"AES","privacy_password":"Infoblox1","authentication_password":"Infoblox1"}
        response = ib_NIOS.wapi_request('PUT',ref=snmpuser_ref,fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:
                assert False
            else:
                assert True
        sleep(30)       
        snmpuser_name = json.loads(getref)[0]["name"]
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data='snmpwalk -v3 -l authPriv -u '+snmpuser_name+' -a SHA -A "infoblox1" -x AES -X "infoblox1" '+config.grid_member1_vip+'| grep member'
        stdin, stdout, stderr = client.exec_command(data)
        sleep(2)
        stdout=stdout.read()
        print(data,stdout)
        if 'openvpn-member' in stdout:
            print("\nSuccess : snmpwalk command SHA->AES work successfully on GRID-MEMBER-LEVEL\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: open bug -> NIOS-87010")
            assert False
 
    @pytest.mark.run(order=19)
    def test_018_Validate_snmpwalk_cmd_working_SHA_AES_Grid_Member_Level_use_old_passwd(self):  
        log("start","/var/log/syslog",config.grid_vip)
        getref = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmpuser_ref = json.loads(getref)[0]['_ref']
        
        data={"authentication_protocol":"SHA","privacy_protocol":"AES","privacy_password":"infoblox1","authentication_password":"infoblox1"}
        response = ib_NIOS.wapi_request('PUT',ref=snmpuser_ref,fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:
                assert False
            else:
                assert True
        sleep(30)       
        snmpuser_name = json.loads(getref)[0]["name"]
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data='snmpwalk -v3 -l authPriv -u '+snmpuser_name+' -a SHA -A "infoblox1" -x AES -X "infoblox1" '+config.grid_vip+'| grep master'
        stdin, stdout, stderr = client.exec_command(data)
        sleep(2)
        stdout=stdout.read()
        print(data,stdout)
        if 'Authentication failure' in stdout:
            print("\nSuccess : snmpwalk: Authentication failure (incorrect password, community or key)\n")
            client.close()
            assert True
        else:
            client.close()
            assert False
        #snmpwalk: Authentication failure (incorrect password, community or key)
        
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor=".*snmpd.*warning Authentication failed .*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        if logs:
            assert True 
        else:
            assert False
            
            
    @pytest.mark.run(order=19)
    def test_018_Validate_snmpwalk_cmd_working_SHA_AES_Grid_Member_Level(self):   
        getref = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmpuser_ref = json.loads(getref)[0]['_ref']

        data={"authentication_protocol":"SHA","privacy_protocol":"AES","privacy_password":"Infoblox1","authentication_password":"Infoblox1"}
        response = ib_NIOS.wapi_request('PUT',ref=snmpuser_ref,fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:
                assert False
            else:
                assert True
        sleep(30)       
        snmpuser_name = json.loads(getref)[0]["name"]
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data='snmpwalk -v3 -l authPriv -u '+snmpuser_name+' -a SHA -A "infoblox1" -x AES -X "infoblox1" '+config.grid_member1_vip+'| grep member'
        stdin, stdout, stderr = client.exec_command(data)
        sleep(2)
        stdout=stdout.read()
        print(data,stdout)
        if 'openvpn-member' in stdout:
            print("\nSuccess : snmpwalk command MD5->DES work successfully on GRID-MEMBER-LEVEL\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: open bug -> NIOS-87010")
            assert False
  
    @pytest.mark.run(order=20)
    def test_019_Validate_logs_after_disable_grid_level_snmpv3_query(self):  
        log("start","/var/log/syslog",config.grid_vip)
        log("start","/var/log/syslog",config.grid_member1_vip)
        response = ib_NIOS.wapi_request('GET', object_type="member")
        memref = json.loads(response)[0]['_ref']
        print(memref)
        sleep(30)
        data={"snmp_setting":{"snmpv3_queries_enable": False,"snmpv3_queries_users": []}}
        
        response=ib_NIOS.wapi_request('PUT',ref=memref, fields=json.dumps(data))
        print(response)
        if type(response) == tuple:

            if response[0]==200:
                
                assert False
            else:
                print("Success: Disable snmp query on grid level")
                assert True
        
        sleep(30)
        
        LookFor=".*snmpd.*Received TERM or STOP signal .*"
        log("stop","/var/log/syslog",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        if logs:
            assert True 
        else:
            assert False    
            
        LookFor=".*snmpd.*Received TERM or STOP signal .*"
        
        logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
        if logs:
            assert True 
        else:
            print("Failure: open bug -> NIOS-87010")
            assert False
 
    @pytest.mark.run(order=21)
    def test_020_Validate_logs_after_enable_grid_level_snmpv3_query(self):
        log("start","/var/log/syslog",config.grid_vip)
        log("start","/var/log/syslog",config.grid_member1_vip)
        print("\n")
        response = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmp_memref = json.loads(response)[0]['_ref']
        snmp_memref = snmp_memref.encode('ascii', 'ignore')
        print(snmp_memref)
        
        response = ib_NIOS.wapi_request('GET', object_type="member")
        memref = json.loads(response)[0]['_ref']
        print(memref)
        sleep(30)
        data={"snmp_setting":{"snmpv3_queries_enable": True,"snmpv3_queries_users": [{"user":snmp_memref}]}}
        
        response=ib_NIOS.wapi_request('PUT',ref=memref, fields=json.dumps(data))
        print(response)
        if type(response) == tuple:

            if response[0]==200:
                
                assert False
            else:
                print("Success: Enable snmp query on grid member level")
                assert True
       
        sleep(30)
              
        LookFor=".*NET-SNMP.*AgentX subagent connected.*"
        log("stop","/var/log/syslog",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        if logs:
            assert True 
        else:
            assert False    
            
        LookFor=".*snmpd.*Received TERM or STOP signal .*"
        
        logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
        if logs:
            assert True 
        else:
            print("Failure: open bug -> NIOS-87010")
            assert False

            
    @pytest.mark.run(order=22)
    def test_021_cleanup(self):
        get_reff = ib_NIOS.wapi_request('GET', object_type="member")
        
        #print(get_reff)
        for ref in json.loads(get_reff):
            print(ref['_ref'])
            
            data={"use_snmp_setting":True,"snmp_setting":{"snmpv3_queries_enable": False,"snmpv3_queries_users": []}}
            response=ib_NIOS.wapi_request('PUT',ref=ref['_ref'], fields=json.dumps(data))
            print(response)
            if type(response) == tuple:

                if response[0]==200:
                   
                    assert True
                else:
                    assert False 
                    
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting')
        get_grid_ref=json.loads(get_ref)[0]['_ref']
        
        data={"snmp_setting":{"snmpv3_queries_enable": False,"snmpv3_queries_users": []}}
        response=ib_NIOS.wapi_request('PUT',ref=get_grid_ref, fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:     
                    assert True
            else:
                assert False
                
        get_ref = ib_NIOS.wapi_request('GET', object_type="snmpuser", grid_vip=config.grid_vip)

        for ref in json.loads(get_ref):
            if 'snmpUser1' in ref["_ref"]:
                response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
                print(response)  
                if type(response) == tuple:           
                    if response[0]==200:     
                        assert True
                    else:
                        assert False
              
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)


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
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv

def perform_snmpwalk_command(IP,auth_protocal,priv_protocal,MAS_or_MEM):
    getref = ib_NIOS.wapi_request('GET',object_type="snmpuser")
    print(getref)
    snmpuser_name = json.loads(getref)[0]["name"]
              
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(config.grid_vip, username='root', pkey = mykey)
    sleep(30)
    data='snmpwalk -v3 -l authPriv -u '+snmpuser_name+' -a '+auth_protocal+' -A "infoblox1" -x '+priv_protocal+' -X "infoblox1" '+IP+'| grep '+MAS_or_MEM
    stdin, stdout, stderr = client.exec_command(data)
    sleep(2)
    stdout=stdout.read()
    stderr=stderr.read()
    print(data,stdout,stderr)

    return client,stdout,stderr

def perform_snmpwalk_command_using_change_passwd(IP,auth_protocal,priv_protocal,MAS_or_MEM):
    getref = ib_NIOS.wapi_request('GET',object_type="snmpuser")
    print(getref)
    snmpuser_name = json.loads(getref)[0]["name"]
              
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(config.grid_vip, username='root', pkey = mykey)
    sleep(30)
    data='snmpwalk -v3 -l authPriv -u '+snmpuser_name+' -a '+auth_protocal+' -A "Infoblox1" -x '+priv_protocal+' -X "Infoblox1" '+IP+'| grep '+MAS_or_MEM
    stdin, stdout, stderr = client.exec_command(data)
    sleep(2)
    stdout=stdout.read()
    stderr=stderr.read()
    print(data,stdout,stderr)

    return client,stdout,stderr
    
    
def log_validation(IP,auth_protocal,priv_protocal):
    log("start","/var/log/messages",IP)
    getref = ib_NIOS.wapi_request('GET',object_type="snmpuser")
    snmpuser_ref = json.loads(getref)[0]['_ref']
    data={"authentication_protocol":auth_protocal,"privacy_protocol":priv_protocal,"privacy_password":"infoblox1","authentication_password":"infoblox1"}
    response = ib_NIOS.wapi_request('PUT',ref=snmpuser_ref,fields=json.dumps(data))
    print(response)
    if type(response) == tuple:
        if response[0]==200:
            print("Success: Changed the authentication and privacy protocal")
            assert True
        else:
            print("Failure: Changed the authentication and privacy protocal")
            assert False
    sleep(120)
    
    log("stop","/var/log/messages",IP)
    LookFor=".*NET-SNMP.*AgentX.*subagent.*connected.*"
    print(LookFor)
    logs=logv(LookFor,"/var/log/messages",IP)
    print(logs)
    return logs 

def log_validation_changing_passwd(IP,auth_protocal,priv_protocal):
    log("start","/var/log/messages",IP)
    getref = ib_NIOS.wapi_request('GET',object_type="snmpuser")
    snmpuser_ref = json.loads(getref)[0]['_ref']
    data={"name":"snmpUser1","authentication_protocol":auth_protocal,"privacy_protocol":priv_protocal,"privacy_password":"Infoblox1","authentication_password":"Infoblox1"}
    response = ib_NIOS.wapi_request('PUT',ref=snmpuser_ref,fields=json.dumps(data))
    print(response)
    if type(response) == tuple:
        if response[0]==200:
            print("Success: Changed the authentication and privacy protocal")
            assert True
        else:
            print("Failure: Changed the authentication and privacy protocal")
            assert False
    sleep(120)
    
    log("stop","/var/log/messages",IP)
    LookFor=".*NET-SNMP.*AgentX.*subagent.*connected.*"
    print(LookFor)
    logs=logv(LookFor,"/var/log/messages",IP)
    print(logs)
    return logs 
    
class NIOSSPT_12186(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_create_an_SNMPv3_User(self):
       print("Create an SNMPv3 User")

       data={"name":"snmpUser1","authentication_protocol":"SHA","privacy_protocol":"AES","privacy_password":"infoblox1","authentication_password":"infoblox1"}

       response = ib_NIOS.wapi_request('POST',object_type="snmpuser",fields=json.dumps(data))
       print(response)
       
       if type(response) == tuple:           
           if response[0]==200:  
               print("\n Success: Created SNMPv3 User\n")
               assert True
           else:
               print("\n Failure: Create SNMPv3 User\n")
               assert False
         
    @pytest.mark.run(order=2)
    def test_001_enable_snmp_query_grid_level(self):
        
        log("start","/var/log/messages",config.grid_vip)
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
                print("Success: Enable SNMP configuration on grid level")
                assert True
            else:
                print("Failure: Enable SNMP configuration on grid level")
                assert False
                
        sleep(120)
        log("stop","/var/log/messages",config.grid_vip)
        
        LookFor=".*NET-SNMP.*AgentX.*subagent.*connected.*"
        print(LookFor)
        logs=logv(LookFor,"/var/log/messages",config.grid_vip)
        print(logs)
        
        if logs:
            print("Success : SNMP restart ")
            assert True 
        else:
            print("Failure: SNMP didn't restart ")
            assert False
            
    @pytest.mark.run(order=3)
    def test_002_Validate_snmpwalk_cmd_working_SHA_AES_Grid_Level(self):  
        print(" SNMP walk against member (GRID-LEVEL)")
        client,stdout,stderr=perform_snmpwalk_command(config.grid_vip,"SHA","AES","master")  
        if 'openvpn-master' in stdout:
            print("\nSuccess : snmpwalk command SHA->DES  work successfully on GRID-LEVEL\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: open bug -> NIOS-87010 ")
            assert False
                   
        
            
    @pytest.mark.run(order=4)
    def test_003_Validate_snmpwalk_cmd_working_SHA_DES_Grid_Level(self): 
        logs=log_validation(config.grid_vip,"SHA","DES")
        if logs:
            client,stdout,stderr=perform_snmpwalk_command(config.grid_vip,"SHA","DES","master")            
            if 'openvpn-master' in stdout:
                print("\nSuccess : snmpwalk command SHA->DES  work successfully on GRID-LEVEL\n")
                client.close()
                assert True
            else:
                client.close()
                print("Failure: open bug -> NIOS-87010 ")
                assert False
        else:
            print("SNMP didn't restart ")
            assert False

    @pytest.mark.run(order=5)
    def test_004_Validate_snmpwalk_cmd_working_MD5_AES_Grid_Level(self): 
        logs=log_validation(config.grid_vip,"MD5","AES")
        if logs:
            
            client,stdout,stderr=perform_snmpwalk_command(config.grid_vip,"MD5","AES","master")    
            if 'openvpn-master' in stdout:
                print("\nSuccess : snmpwalk command MD5->AES work successfully on GRID-LEVEL\n")
                client.close()
                assert True
            else:
                client.close()
                print("Failure: open bug -> NIOS-87010 ")
                assert False
        else:
            print("SNMP didn't restart ")
            assert False
            
    @pytest.mark.run(order=6)
    def test_005_Validate_snmpwalk_cmd_working_MD5_DES_Grid_Level(self):   
        logs=log_validation(config.grid_vip,"MD5","DES")
        if logs:
            client,stdout,stderr=perform_snmpwalk_command(config.grid_vip,"MD5","DES","master")   
            if 'openvpn-master' in stdout:
                print("\nSuccess : snmpwalk command MD5->DES work successfully on GRID-LEVEL\n")
                client.close()
                assert True
            else:
                client.close()
                print("Failure: open bug -> NIOS-87010 ")
                assert False
        else:
            print("SNMP didn't restart ")
            assert False
         
    @pytest.mark.run(order=7)
    def test_006_enable_snmp_query_on_grid_master_level(self):
        log("start","/var/log/messages",config.grid_vip)
        print("\n")
                       
        response = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmp_memref = json.loads(response)[0]['_ref']
        snmp_memref = snmp_memref.encode('ascii', 'ignore')
        print(snmp_memref)
        
        response = ib_NIOS.wapi_request('GET', object_type="member")
        memref = json.loads(response)[0]['_ref']
        print(memref)
        
        data={"use_snmp_setting":True,"snmp_setting":{"snmpv3_queries_enable": True,"snmpv3_queries_users": [{"user":snmp_memref}]}}
        
        response=ib_NIOS.wapi_request('PUT',ref=memref, fields=json.dumps(data))
        print(response)
        if type(response) == tuple:

            if response[0]==200:
                print("\n Success : Configure SNMP on master level") 
                assert True
            else:
                print("Failure: Configure SNMP on master level")
                assert False
       
        sleep(120)
        log("stop","/var/log/messages",config.grid_vip)
        LookFor=".*NET-SNMP.*AgentX.*subagent.*connected.*"
        print(LookFor)
        logs=logv(LookFor,"/var/log/messages",config.grid_vip)
        print(logs)
        if logs:
            print("Success : SNMP restart ")
            assert True 
        else:
            print("Failure: SNMP didn't restart ")
            assert False
            
    @pytest.mark.run(order=8)
    def test_007_Validate_snmpwalk_cmd_working_SHA_AES_Grid_Master_Level(self):  
        logs=log_validation(config.grid_vip,"SHA","AES")
        
        if logs:
            client,stdout,stderr=perform_snmpwalk_command(config.grid_vip,"SHA","AES","master")   
            if 'openvpn-master' in stdout:
                print("\nSuccess : snmpwalk command SHA->AES work successfully on GRID-MASTER-LEVEL\n")
                client.close()
                assert True
            else:
                client.close()
                print("Failure: open bug -> NIOS-87010 ")
                assert False
        else:
            print("SNMP didn't restart ")
            assert False
            
    @pytest.mark.run(order=9)
    def test_008_Validate_snmpwalk_cmd_working_SHA_DES_Grid_Master_Level(self):  
        logs=log_validation(config.grid_vip,"SHA","DES")
        
        if logs:
            client,stdout,stderr=perform_snmpwalk_command(config.grid_vip,"SHA","DES","master")   
            if 'openvpn-master' in stdout:
                print("\nSuccess : snmpwalk command SHA->DES work successfully on GRID-MASTER-LEVEL\n")
                client.close()
                print("Success: open bug -> NIOS-87010 ")
                assert True
            else:
                print("Failure: open bug -> NIOS-87010 ")
                client.close()
                assert False
    
        else:
            print("SNMP didn't restart ")
            assert False
                        
            
    @pytest.mark.run(order=10)
    def test_009_Validate_snmpwalk_cmd_working_MD5_AES_Grid_Master_Level(self):   
        logs=log_validation(config.grid_vip,"MD5","AES")
        
        if logs:
            client,stdout,stderr=perform_snmpwalk_command(config.grid_vip,"MD5","AES","master")   
            if 'openvpn-master' in stdout:
                print("\nSuccess : snmpwalk command MD5->AES work successfully on GRID-MASTER-LEVEL\n")
                client.close()
                assert True
            else:
                client.close()
                print("Failure: open bug -> NIOS-87010 ")
                assert False
        else:
            print("SNMP didn't restart ")
            assert False     
            
    @pytest.mark.run(order=11)
    def test_010_Validate_snmpwalk_cmd_working_MD5_DES_Grid_Master_Level(self):   
        logs=log_validation(config.grid_vip,"MD5","DES")
        
        if logs:
            client,stdout,stderr=perform_snmpwalk_command(config.grid_vip,"MD5","DES","master")   
            if 'openvpn-master' in stdout:
                print("\nSuccess : snmpwalk command MD5->DES work successfully on GRID-MASTER-LEVEL\n")
                client.close()
                assert True
            else:
                client.close()
                print("Failure: open bug -> NIOS-87010 ")
                assert False
        else:
            print("SNMP didn't restart ")
            assert False  
            
    @pytest.mark.run(order=12)
    def test_011_enable_snmp_query_on_grid_member_level(self):
        print("\n")
        log("start","/var/log/messages",config.grid_vip)
        get_reff = ib_NIOS.wapi_request('GET', object_type="member")
        get_reff = json.loads(get_reff)[0]['_ref']
        
        data={"use_snmp_setting":False,"snmp_setting":{"snmpv3_queries_enable": False,"snmpv3_queries_users": []}}
        response=ib_NIOS.wapi_request('PUT',ref=get_reff, fields=json.dumps(data))
        print(response)
        if type(response) == tuple:

            if response[0]==200:
                print("\n Success : Disable SNMP Configuration on master level") 
                assert True
            else:
                print("\n Failure : Disable SNMP Configuration on master level")
                assert False 
                
        response = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmp_memref = json.loads(response)[0]['_ref']
        snmp_memref = snmp_memref.encode('ascii', 'ignore')
        print(snmp_memref)
        
        response = ib_NIOS.wapi_request('GET', object_type="member")
        memref = json.loads(response)[1]['_ref']
        print(memref)
       
        data={"use_snmp_setting":True,"snmp_setting":{"snmpv3_queries_enable": True,"snmpv3_queries_users": [{"user":snmp_memref}]}}
        
        response=ib_NIOS.wapi_request('PUT',ref=memref, fields=json.dumps(data))
        print(response)
        if type(response) == tuple:

            if response[0]==200:
                print("\n Success: Enable SNMP configuration on member")
                assert False
            else:
                print("Failure: Enable SNMP configuration on member")
                assert True

        sleep(120)
        log("stop","/var/log/messages",config.grid_vip)
        LookFor=".*NET-SNMP.*AgentX.*subagent.*connected.*"
        print(LookFor)
        logs=logv(LookFor,"/var/log/messages",config.grid_vip)
        print(logs)
        if logs:
            print("Success : SNMP restart ")
            assert True 
        else:
            print("Failure: SNMP didn't restart ")
            assert False
            
    @pytest.mark.run(order=13)
    def test_012_Validate_snmpwalk_cmd_working_SHA_AES_Grid_Member_Level(self):   
        logs=log_validation(config.grid_member1_vip,"SHA","AES")
        
        if logs:
            client,stdout,stderr=perform_snmpwalk_command(config.grid_member1_vip,"SHA","AES","member")
            if 'openvpn-member' in stdout:
                print("\nSuccess : snmpwalk command SHA->AES work successfully on GRID-MEMBER-LEVEL\n")
                client.close()
                assert True
            else:
                client.close()
                print("Failure: open bug -> NIOS-87010")
                assert False
        else:
            print("SNMP didn't restart, open bug -> NIOS-87010")
            assert False 
            
    @pytest.mark.run(order=14)
    def test_013_Validate_snmpwalk_cmd_working_SHA_DES_Grid_Member_Level(self):  
        logs=log_validation(config.grid_member1_vip,"SHA","DES")
        
        if logs:
            client,stdout,stderr=perform_snmpwalk_command(config.grid_member1_vip,"SHA","DES","member")
            if 'openvpn-member' in stdout:
                print("\nSuccess : snmpwalk command SHA->DES work successfully on GRID-MEMBER-LEVEL\n")
                client.close()
                assert True
            else:
                client.close()
                print("Failure: open bug -> NIOS-87010")
                assert False
        else:
            print("SNMP didn't restart, open bug -> NIOS-87010")
            assert False       
          
    @pytest.mark.run(order=15)
    def test_014_Validate_snmpwalk_cmd_working_MD5_AES_Grid_Member_Level(self):   
        logs=log_validation(config.grid_member1_vip,"MD5","AES")
        
        if logs:
            client,stdout,stderr=perform_snmpwalk_command(config.grid_member1_vip,"MD5","AES","member")
            if 'openvpn-member' in stdout:
                print("\nSuccess : snmpwalk command MD5->AES work successfully on GRID-MEMBER-LEVEL\n")
                client.close()
                assert True
            else:
                client.close()
                print("Failure: open bug -> NIOS-87010 ")
                assert False
        else:
            print("SNMP didn't restart, open bug -> NIOS-87010")
            assert False                    
            
    @pytest.mark.run(order=16)
    def test_015_Validate_snmpwalk_cmd_working_MD5_DES_Grid_Member_Level(self):   
        
        logs=log_validation(config.grid_member1_vip,"MD5","DES")
        
        if logs:
            client,stdout,stderr=perform_snmpwalk_command(config.grid_member1_vip,"MD5","DES","member")
            if 'openvpn-member' in stdout:
                print("\nSuccess : snmpwalk command MD5->DES work successfully on GRID-MEMBER-LEVEL\n")
                client.close()
                assert True
            else:
                client.close()
                print("Failure: open bug -> NIOS-87010")
                assert False
                
        else:
            print("SNMP didn't restart, open bug -> NIOS-87010 ")
            assert False 
            
            
    @pytest.mark.run(order=17)
    def test_016_Validate_snmpwalk_cmd_for_SHA_AES_Grid_Master_after_changing_passwd(self): 
        
        logs=log_validation_changing_passwd(config.grid_vip,"SHA","AES")

        if logs:
            print("\n wait for 3 minutes")
            sleep(180)
            log("start","/var/log/messages",config.grid_vip)
            
            client,stdout,stderr=perform_snmpwalk_command(config.grid_vip,"SHA","AES","master")
            print(stderr)
            log("stop","/var/log/messages",config.grid_vip)
            
            print("=================================================")
            print("Look for log on master")
            print("=================================================")
            LookFor_master='.*snmpd.*warning.*Authentication.*failed.*'
            logss=logv(LookFor_master,"/var/log/messages",config.grid_vip)
            print(logss)
            if logss:
                print("\n Success: warning Authentication failed on master")
            else:
                print("\n Failure: warning Authentication failed on master")
                
            if 'Authentication failure' in stderr:
                print("\nSuccess : Authentication failure (incorrect password, community or key) \n")
                client.close()
                assert True
            else:
                client.close()
                print("Failure: Authentication failure (incorrect password, community or key) ")
                assert False
        else:
            print("SNMP didn't restart ")
            assert False 
          
    @pytest.mark.run(order=18)
    def test_017_Validate_snmpwalk_cmd_working_SHA_AES_Grid_Member_after_changing_passwd(self):  
        #logs=log_validation_changing_passwd(config.grid_member1_vip,"SHA","AES")
        
        #if logs:
        client,stdout,stderr=perform_snmpwalk_command(config.grid_member1_vip,"SHA","AES","member")
        if 'openvpn-member' in stdout:
            print("Failure: open bug -> NIOSSPT-12186 ")
            
            client.close()
            assert False
        else:
            client.close()
            print("\nSuccess : snmpwalk command SHA->AES work successfully on GRID-MEMBER\n")
            assert True
        #else:
            #print("SNMP didn't restart Failure: open bug -> NIOS-87010 ")
            #assert False
            
    @pytest.mark.run(order=19)
    def test_018_Validate_snmpwalk_cmd_working_SHA_AES_Grid_master_using_new_passwd(self):  

        client,stdout,stderr=perform_snmpwalk_command_using_change_passwd(config.grid_vip,"SHA","AES","master")
        if 'openvpn-master' in stdout:
            print("\nSuccess : snmpwalk command SHA->AES work successfully on GRID-MASTER\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: open bug -> NIOS-87010 ")
            assert False
        
    @pytest.mark.run(order=20)
    def test_019_Validate_snmpwalk_cmd_working_SHA_AES_Grid_Member_using_new_passwd(self):  
        log("start","/var/log/messages",config.grid_member1_vip)
        client,stdout,stderr=perform_snmpwalk_command_using_change_passwd(config.grid_member1_vip,"SHA","AES","member")
        print(stderr)
        log("stop","/var/log/messages",config.grid_member1_vip)
        
        print("=================================================")
        print("Look for log on member")
        print("=================================================")
        LookFor_master='.*snmpd.*warning.*Authentication.*failed.*'
        logss=logv(LookFor_master,"/var/log/messages",config.grid_member1_vip)
        print(logss)
        if logss:
            print("\n Failure: warning Authentication failed on member which is a bug NIOSSPT-12186")
            assert False
        else:
            print("\n Success: did not get warning Authentication failed on member using new password")
            assert True

        if 'Authentication failure' in stderr:
            client.close()
            print("Failure: Authentication failure (incorrect password, community or key) which is a bug NIOSSPT-12186")
            assert False
            
        else:
            print("\nSuccess :  snmpwalk command SHA->AES work successfully on GRID-MEMBER\n")
            client.close()
            assert True
       
    @pytest.mark.run(order=21)
    def test_020_Validate_logs_after_disable_grid_level_snmpv3_query(self):  
        
        log("start","/var/log/messages",config.grid_vip)
        log("start","/var/log/messages",config.grid_member1_vip)
        
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting')
        get_grid_ref=json.loads(get_ref)[0]['_ref']
        
        data={"snmp_setting":{"snmpv3_queries_enable": False,"snmpv3_queries_users": []}}
        response=ib_NIOS.wapi_request('PUT',ref=get_grid_ref, fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200: 
                print("Success: Disable snmp configuration on grid level")
                assert True
            else:
                print("Failure: Disable snmp configuration on grid level")
                assert False
           
        sleep(120)
        
        log("stop","/var/log/messages",config.grid_vip)
        log("stop","/var/log/messages",config.grid_member1_vip)
        
        print("\n=================================================\n")
        print("\n\n Check SNMP is stopped on master")
        print("\n=================================================\n")
        LookFor=".*snmpd.*Received TERM or STOP signal.*"
        print(LookFor)
        
        logs=logv(LookFor,"/var/log/messages",config.grid_vip)
        
        print(logs)
        if logs:
            print("Success: SNMP is stopped on master")
            assert True 
        else:
            print("Failure: SNMP is stopped on master")
            assert False     

    @pytest.mark.run(order=22)
    def test_021_Validate_logs_after_add_back_grid_level_snmpv3_query_(self):
        log("start","/var/log/messages",config.grid_vip)
        log("start","/var/log/messages",config.grid_member1_vip)
        print("\n")
        response = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmp_memref = json.loads(response)[0]['_ref']
        snmp_memref = snmp_memref.encode('ascii', 'ignore')
        print(snmp_memref)
        
        response = ib_NIOS.wapi_request('GET', object_type="grid?_return_fields=snmp_setting")
        memref = json.loads(response)[0]['_ref']
        print(memref)
        sleep(120)
        data={"snmp_setting":{"snmpv3_queries_enable": True,"snmpv3_queries_users": [{"user":snmp_memref}]}}
        
        response=ib_NIOS.wapi_request('PUT',ref=memref, fields=json.dumps(data))
        print(response)
        if type(response) == tuple:

            if response[0]==200:
                print("Success: Enable snmp query on grid level") 
                assert False
            else:
                print("Success: Enable snmp query on grid level")
                assert True
       
        sleep(120)
        print("\n=================================================\n")
        print("Check SNMP is Started on master")
        print("\n=================================================\n")
        
        LookFor=".*NET-SNMP.*AgentX.*subagent.*connected.*"
        print(LookFor)
        log("stop","/var/log/messages",config.grid_vip)
        log("stop","/var/log/messages",config.grid_member1_vip)
        logs=logv(LookFor,"/var/log/messages",config.grid_vip)
        print("\n\n Check SNMP is started on master")
        print(logs)
        if logs:
            print("Success: SNMP is Started on master")
            assert True 
        else:
            print("Failure: SNMP is Started on master")
            assert False   

 
    @pytest.mark.run(order=23)
    def test_022_Validate_snmpwalk_cmd_working_SHA_AES_Master_new_password(self):   
        #logs=log_validation_changing_passwd(config.grid_vip,"SHA","AES")
        
        #if logs:
        client,stdout,stderr=perform_snmpwalk_command_using_change_passwd(config.grid_vip,"SHA","AES","master")
        if 'openvpn-master' in stdout:
            print("\nSuccess : snmpwalk command SHA->AES work successfully on GRID-LEVEL\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: open bug -> NIOS-87010")
            assert False
        # else:
            # print("SNMP didn't restart, open bug -> NIOS-87010")
            # assert False 
  
    @pytest.mark.run(order=24)
    def test_023_Validate_snmpwalk_cmd_working_SHA_AES_Grid_Member_Level(self):   
        #logs=log_validation(config.grid_member1_vip,"SHA","AES")
        
        #if logs:
        client,stdout,stderr=perform_snmpwalk_command_using_change_passwd(config.grid_member1_vip,"SHA","AES","member")
        if 'openvpn-member' in stdout:
            print("\nSuccess : snmpwalk command SHA->AES work successfully on MEMBER-LEVEL\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: open bug -> NIOSSPT-12186")
            assert False
        
        # else:
            # print("SNMP didn't restart, open bug -> NIOS-87010")
            # assert False   
            
    @pytest.mark.run(order=25)
    def test_024_cleanup(self):
        print("\n\n Clean up all created object\n\n")
        get_reff = ib_NIOS.wapi_request('GET', object_type="member")
      
        for ref in json.loads(get_reff):
            print(ref['_ref'])
            
            data={"use_snmp_setting":False,"snmp_setting":{"snmpv3_queries_enable": False,"snmpv3_queries_users": []}}
            response=ib_NIOS.wapi_request('PUT',ref=ref['_ref'], fields=json.dumps(data))
            print(response)
            if type(response) == tuple:

                if response[0]==200:
                    print("Sucess: \n Deleting SNMP configuration on members ")
                    assert True
                    
                else:
                    print("Failure: \n Deleting SNMP configuration on members ")
                    assert False 
                    
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting')
        get_grid_ref=json.loads(get_ref)[0]['_ref']
        
        data={"snmp_setting":{"snmpv3_queries_enable": False,"snmpv3_queries_users": []}}
        response=ib_NIOS.wapi_request('PUT',ref=get_grid_ref, fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:
                print("Sucess: \n Deleting SNMP configuration on GRID-LEVEL ")
                assert True
            else:
                print("Failure: \n Deleting SNMP configuration on GRID-LEVEL ")
                assert False
                
        get_ref = ib_NIOS.wapi_request('GET', object_type="snmpuser", grid_vip=config.grid_vip)

        for ref in json.loads(get_ref):
            if 'snmpUser1' in ref["_ref"]:
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







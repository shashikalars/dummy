#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. 2 SA Grids,MGMT,LAN2                                                  #
#  2. Licenses : DNS(enabled), DHCP, Grid                                   #
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

def perform_dig_cmd_tcpdump(dig_cmd):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(config.grid_vip, username='root', pkey = mykey)
    transport = client.get_transport()
    channel_tcpdump = transport.open_session()
    channel_tcpdump.get_pty()
    channel_tcpdump.set_combine_stderr(True)
    data="tcpdump -U -v -i any -A port 53 -w log.pcap"
    channel_tcpdump.exec_command(data)
    sleep(5)
    # data="dig @"+config.grid_vip+" a_rec.rfe_4795.com IN A"
    data=dig_cmd
    stdin, stdout, stderr = client.exec_command(data)
    print(stdout.read())
    sleep(10)
    data="pkill tcpdump"
    stdin, stdout, stderr = client.exec_command(data)
    print(stdout.read())
    channel_tcpdump.close()
    sleep(10)
    client.close()

    
def validate_tcp_or_udp():    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(config.grid_vip, username='root', pkey = mykey)
    data="tcpdump -v -r log.pcap"
    stdin, stdout, stderr = client.exec_command(data)
    stdout=stdout.read()
    print("output ",stdout)
    
    
    
    if 'proto TCP' in stdout and 'proto UDP' in stdout:
        print("This is TCP protocal")
        data="rm log.pcap"
        stdin, stdout, stderr = client.exec_command(data)
        client.close()
        return("TCP")
    elif 'proto TCP' in stdout:
        print("This is TCP protocal")
        data="rm log.pcap"
        stdin, stdout, stderr = client.exec_command(data)
        client.close()
        return("TCP")
    elif 'proto UDP' in stdout:
        print("This is UDP protocal")
        data="rm log.pcap"
        stdin, stdout, stderr = client.exec_command(data)
        client.close()
        return("UDP")
    else:   
        return("Error")

def validate_tcp_or_udp_ipv6():
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(config.grid_vip, username='root', pkey = mykey)
    data="tcpdump -v -r log.pcap"
    stdin, stdout, stderr = client.exec_command(data)
    stdout=stdout.read()
    print("output ",stdout)
      
    if 'TCP' in stdout and 'UDP' in stdout:
        print("This is TCP protocal")
        data="rm log.pcap"
        stdin, stdout, stderr = client.exec_command(data)
        client.close()
        return("TCP")
    elif 'TCP' in stdout:
        print("This is TCP protocal")
        data="rm log.pcap"
        stdin, stdout, stderr = client.exec_command(data)
        client.close()
        return("TCP")
    elif 'UDP' in stdout:
        print("This is UDP protocal")
        data="rm log.pcap"
        stdin, stdout, stderr = client.exec_command(data)
        client.close()
        return("UDP")
    else:   
        return("Error")

def clear_DNS_cache():
    get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns')
    print(get_ref)
    for ref in json.loads(get_ref):
        #print(ref['_ref'])
        response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps({"clear_dns_cache": True}))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Did not clear the dns cache")
                assert False
        else:
            print("Success: Clear the dns cache")
            assert True
    
class RFE_4795(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_start_dns_services(self):
       print("Start DNS service")
       get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns')
       print(get_ref)
       for ref in json.loads(get_ref):
           response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps({"enable_dns":True}))
           if type(response) == tuple:
               if response[0]==400 or response[0]==401:
                   assert False
                   
    
    @pytest.mark.run(order=2)
    def test_001_check_UDP_buffer_size_attribute_and_test_default_value(self):
        
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns?_return_fields=max_udp_size')
        print(get_ref)
        def_value= 1220
        for ref in json.loads(get_ref):
            if def_value==ref['max_udp_size']:          
                if get_ref:
                     print("Success:check_UDP_buffer_size_attribute_present and test default value for UDP buffer size is 1220")
                     assert True
            else:
                  
                print("Failure: Check_UDP_buffer_size_attribute_present and test default value for UDP buffer size is 1220")
                assert False
                    
                    
    @pytest.mark.run(order=3)
    def test_002_create_New_AuthZone(self):
        print("Create A new Zone Authoritative zone")
      
        data = {"fqdn": "rfe_4795.com","grid_primary": [{"name": config.grid_fqdn,"stealth":False}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
        print response
        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==404:
                print("Failure: Create A new Zone Authoritative zone")
                assert False
            else:
                print("Success: Create A new Zone Authoritative zone")
                assert True
                
                
    @pytest.mark.run(order=4)
    def test_003_create_A_record_with_different_size(self): 
        print("Creating a record ")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth')
        print(get_ref)
        for i in range(1,15):
            for ref in json.loads(get_ref):
                if 'rfe_4795.com' in ref['_ref']:
                    data = {
                    "ipv4addr":"13.0.0."+str(i),
                    "view":"default",
                    "name": "a_rec.rfe_4795.com"}
                    response = ib_NIOS.wapi_request('POST',object_type="record:a",fields=json.dumps(data))
                    print(response)
                    if type(response) == tuple:
                        if response[0]==400 or response[0]==401:
                            print("Failure: Create A record in test zone")
                            assert False
        for i in range(1,35):
            for ref in json.loads(get_ref):
                if 'rfe_4795.com' in ref['_ref']:
                    data = {
                    "ipv4addr":"13.0.0."+str(i),
                    "view":"default",
                    "name": "b_rec.rfe_4795.com"}
                    response = ib_NIOS.wapi_request('POST',object_type="record:a",fields=json.dumps(data))
                    print(response)
                    if type(response) == tuple:
                        if response[0]==400 or response[0]==401:
                            print("Failure: Create A record in test zone")
                            assert False
                            
        for i in range(1,85):
            for ref in json.loads(get_ref):
                if 'rfe_4795.com' in ref['_ref']:
                    data = {
                    "ipv4addr":"13.0.0."+str(i),
                    "view":"default",
                    "name": "c_rec.rfe_4795.com"}
                    response = ib_NIOS.wapi_request('POST',object_type="record:a",fields=json.dumps(data))
                    print(response)
                    if type(response) == tuple:
                        if response[0]==400 or response[0]==401:
                            print("Failure: Create A record in test zone")
                            assert False
                            
                            
                            
        for i in range(1,185):
            for ref in json.loads(get_ref):
                if 'rfe_4795.com' in ref['_ref']:
                    data = {
                    "ipv4addr":"13.0.0."+str(i),
                    "view":"default",
                    "name": "d_rec.rfe_4795.com"}
                    response = ib_NIOS.wapi_request('POST',object_type="record:a",fields=json.dumps(data))
                    print(response)
                    if type(response) == tuple:
                        if response[0]==400 or response[0]==401:
                            print("Failure: Create A record in test zone")
                            assert False
                            
                            
        for i in range(1,255):
            for ref in json.loads(get_ref):
                if 'rfe_4795.com' in ref['_ref']:
                    data = {
                    "ipv4addr":"13.0.0."+str(i),
                    "view":"default",
                    "name": "e_rec.rfe_4795.com"}
                    response = ib_NIOS.wapi_request('POST',object_type="record:a",fields=json.dumps(data))
                    print(response)
                    if type(response) == tuple:
                        if response[0]==400 or response[0]==401:
                            print("Failure: Create A record in test zone")
                            assert False
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)
    
    
    @pytest.mark.run(order=5)
    def test_004_check_sizeof_and_test_UDP_1220(self): 
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" a_rec.rfe_4795.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()   
        if res1=="UDP":
            assert True
        else:
            assert False
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" b_rec.rfe_4795.com IN A +bufsize=2000" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="UDP":
            assert True
        else:
            assert False
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" c_rec.rfe_4795.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="TCP":
            assert True
        else:
            assert False
            
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" d_rec.rfe_4795.com IN A +bufsize=512" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="TCP":
            assert True
        else:
            assert False
            
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" e_rec.rfe_4795.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        else:
            assert False
            
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" b_rec.rfe_4795.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
        else:
            assert False  
           
        
    @pytest.mark.run(order=6)
    def test_005_modify_UDP_size_512(self):
    
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns?_return_fields=max_udp_size')
        print(get_ref)
        for ref in json.loads(get_ref):
            data={'max_udp_size':512}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
            print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns?_return_fields=max_udp_size')
        print(get_ref)
        def_value=512
        for ref in json.loads(get_ref):
            if def_value==ref['max_udp_size']:          
                if get_ref:
                     print("Success:check_UDP_buffer_size_attribute_present and test UDP buffer size is 512")
                     print("Restart Services")
                     grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                     ref = json.loads(grid)[0]['_ref']
                     data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                     request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                     sleep(20)
                     assert True
            else:
              
                print("Failure: Check_UDP_buffer_size_attribute_present and test UDP buffer size is 512")
                assert False
        
    @pytest.mark.run(order=7)
    def test_006_check_sizeof_and_test_UDP_512(self): 
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" a_rec.rfe_4795.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="UDP":
            assert True
        else:
            assert False
            
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" b_rec.rfe_4795.com IN A +bufsize=1220" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
        else:
            assert False
            
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" c_rec.rfe_4795.com IN A +bufsize=2000" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="TCP":
            assert True
        else:
            assert False
            
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" d_rec.rfe_4795.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="TCP":
            assert True
        else:
            assert False
            
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" e_rec.rfe_4795.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        else:
            assert False    
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" b_rec.rfe_4795.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True  
        else:
            assert False
            
        
        
    @pytest.mark.run(order=8)
    def test_007_modify_UDP_size_2000(self):
        print("-----Before modify------")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns?_return_fields=max_udp_size')
        print(get_ref)
        for ref in json.loads(get_ref):
            data={'max_udp_size':2000}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
            print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns?_return_fields=max_udp_size')
        print(get_ref)
        def_value=2000
        for ref in json.loads(get_ref):
            if def_value==ref['max_udp_size']:          
                if get_ref:
                     print("Success:check_UDP_buffer_size_attribute_present and test UDP buffer size 2000")
                     print("Restart Services")
                     grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                     ref = json.loads(grid)[0]['_ref']
                     data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                     request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                     sleep(20)
                     assert True
            else:
              
                print("Failure: Check_UDP_buffer_size_attribute_present and test UDP buffer size 2000")
                assert False
        
    @pytest.mark.run(order=9)
    def test_008_check_sizeof_and_test_UDP_2000(self): 
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" a_rec.rfe_4795.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="UDP":
            assert True
        else:
            assert False
            
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" b_rec.rfe_4795.com IN A +bufsize=1220" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="UDP":
            assert True
        else:
            assert False
            
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" c_rec.rfe_4795.com IN A +bufsize=2500" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="UDP":
            assert True
        else:
            assert False
            
            
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" d_rec.rfe_4795.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="TCP":
            assert True
        else:
            assert False
            
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" e_rec.rfe_4795.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        else:
            assert False   
            
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" b_rec.rfe_4795.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
        else:
            assert False    
          
        
        
    @pytest.mark.run(order=10)
    def test_009_modify_UDP_size_4096(self):
        print("-----Before modify------")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns?_return_fields=max_udp_size')
        print(get_ref)
        for ref in json.loads(get_ref):
            data={'max_udp_size':4096}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
            print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns?_return_fields=max_udp_size')
        print(get_ref)
        def_value=4096
        for ref in json.loads(get_ref):
            if def_value==ref['max_udp_size']:          
                if get_ref:
                     print("Success:check_UDP_buffer_size_attribute_present and test UDP buffer size 4096")
                     print("Restart Services")
                     grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                     ref = json.loads(grid)[0]['_ref']
                     data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                     request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                     sleep(20)
                     assert True
            else:
              
                print("Failure: Check_UDP_buffer_size_attribute_present and test UDP buffer size 4096")
                assert False
        
    @pytest.mark.run(order=11)
    def test_010_check_sizeof_and_test_UDP_4096(self): 
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" a_rec.rfe_4795.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="UDP":
            assert True
        else:
            assert False
            
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" b_rec.rfe_4795.com IN A +bufsize=1220" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="UDP":
            assert True
        else:
            assert False
            
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" c_rec.rfe_4795.com IN A +bufsize=512" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="TCP":
            assert True
        else:
            assert False
            
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" d_rec.rfe_4795.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="UDP":
            assert True
        else:
            assert False
            
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" e_rec.rfe_4795.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        else:
            assert False
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" b_rec.rfe_4795.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
        else:
            assert False    
       
        
        
    @pytest.mark.run(order=12)
    def test_011_modify_UDP_size_1220_for_member(self):
          
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=max_udp_size')
        print(get_ref)
        for ref in json.loads(get_ref):
            data={'max_udp_size':1220}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
            print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=max_udp_size')
        print(get_ref)
        def_value=1220
        for ref in json.loads(get_ref):
            if def_value==ref['max_udp_size']:          
                if get_ref:
                     print("Success:check_UDP_buffer_size_attribute_present and test UDP buffer size is 1220")
                     print("Restart Services")
                     grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                     ref = json.loads(grid)[0]['_ref']
                     data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                     request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                     sleep(20)
                     assert True
            else:
              
                print("Failure: Check_UDP_buffer_size_attribute_present and test UDP buffer size is 1220")
                assert False
    
            
                
    @pytest.mark.run(order=13)
    def test_012_check_sizeof_and_test_UDP_1220_for_member(self): 
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" a_rec.rfe_4795.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" b_rec.rfe_4795.com IN A +bufsize=2000" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" c_rec.rfe_4795.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="TCP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" d_rec.rfe_4795.com IN A +bufsize=512" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="TCP":
            assert True
        else:
            assert False    
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" e_rec.rfe_4795.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" b_rec.rfe_4795.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
        else:
            assert False   
        
        
    @pytest.mark.run(order=14)
    def test_013_modify_UDP_size_512_for_member(self):
    
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=max_udp_size')
        print(get_ref)
        for ref in json.loads(get_ref):
            data={'max_udp_size':512}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
            print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=max_udp_size')
        print(get_ref)
        def_value=512
        for ref in json.loads(get_ref):
            if def_value==ref['max_udp_size']:          
                if get_ref:
                     print("Success:check_UDP_buffer_size_attribute_present and test UDP buffer size is 512")
                     print("Restart Services")
                     grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                     ref = json.loads(grid)[0]['_ref']
                     data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                     request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                     sleep(20)
                     assert True
            else:
              
                print("Failure: Check_UDP_buffer_size_attribute_present and test UDP buffer size is 512")
                assert False
    
    @pytest.mark.run(order=15)
    def test_014_check_sizeof_and_test_UDP_512_for_member(self): 
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" a_rec.rfe_4795.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" b_rec.rfe_4795.com IN A +bufsize=1220" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" c_rec.rfe_4795.com IN A +bufsize=2000" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="TCP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" d_rec.rfe_4795.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="TCP":
            assert True
        else:
            assert False   
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" e_rec.rfe_4795.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
            
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" b_rec.rfe_4795.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True  
            
        else:
            assert False
        
    @pytest.mark.run(order=16)
    def test_015_modify_UDP_size_2000_for_member(self):
        print("-----Before modify------")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=max_udp_size')
        print(get_ref)
        for ref in json.loads(get_ref):
            data={'max_udp_size':2000}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
            print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=max_udp_size')
        print(get_ref)
        def_value=2000
        for ref in json.loads(get_ref):
            if def_value==ref['max_udp_size']:          
                if get_ref:
                     print("Success:check_UDP_buffer_size_attribute_present and test UDP buffer size 2000")
                     print("Restart Services")
                     grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                     ref = json.loads(grid)[0]['_ref']
                     data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                     request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                     sleep(20)
                     assert True
            else:
              
                print("Failure: Check_UDP_buffer_size_attribute_present and test UDP buffer size 2000")
                assert False
    
    @pytest.mark.run(order=17)
    def test_016_check_sizeof_and_test_UDP_2000_for_member(self): 
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" a_rec.rfe_4795.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" b_rec.rfe_4795.com IN A +bufsize=1220" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" c_rec.rfe_4795.com IN A +bufsize=2500" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" d_rec.rfe_4795.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="TCP":
            assert True
        else:
            assert False   
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" e_rec.rfe_4795.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        else:
            assert False    
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" b_rec.rfe_4795.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
            
        else:
            assert False
            
    @pytest.mark.run(order=18)
    def test_017_modify_UDP_size_4096_for_member(self):
        print("-----Before modify------")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=max_udp_size')
        print(get_ref)
        for ref in json.loads(get_ref):
            data={'max_udp_size':4096}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
            print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=max_udp_size')
        print(get_ref)
        def_value=4096
        for ref in json.loads(get_ref):
            if def_value==ref['max_udp_size']:          
                if get_ref:
                     print("Success:check_UDP_buffer_size_attribute_present and test UDP buffer size 4096")
                     print("Restart Services")
                     grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                     ref = json.loads(grid)[0]['_ref']
                     data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                     request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                     sleep(20)
                     assert True
            else:
              
                print("Failure: Check_UDP_buffer_size_attribute_present and test UDP buffer size 4096")
                assert False
    
    @pytest.mark.run(order=19)
    def test_018_check_sizeof_and_test_UDP_4096_for_member(self): 
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" a_rec.rfe_4795.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" b_rec.rfe_4795.com IN A +bufsize=1220" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" c_rec.rfe_4795.com IN A +bufsize=512" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="TCP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" d_rec.rfe_4795.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="UDP":
            assert True
        else:
            assert False    
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" e_rec.rfe_4795.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        else:
            assert False
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" b_rec.rfe_4795.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
            
        else:
            assert False
    
    @pytest.mark.run(order=20)
    def test_019_modify_UDP_size_1220_for_view(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=max_udp_size')
        #print(get_ref)
        for ref in json.loads(get_ref):
            if 'default' in ref['_ref']:
                print(ref)
                data={'max_udp_size':1220}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=max_udp_size')
        
        def_value=1220
        for ref in json.loads(get_ref):
            if 'default' in ref['_ref']:
                print(ref)
                if def_value==ref['max_udp_size']:          
                    if get_ref:
                         print("Success:check_UDP_buffer_size_attribute_present and test UDP buffer size 1220")
                         print("Restart Services")
                         grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                         ref = json.loads(grid)[0]['_ref']
                         data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                         request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                         sleep(20)
                         assert True
                else:
                  
                    print("Failure: Check_UDP_buffer_size_attribute_present and test UDP buffer size 1220")
                    assert False      
        
        
    @pytest.mark.run(order=21)
    def test_020_check_sizeof_and_test_UDP_1220_for_view(self): 
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" a_rec.rfe_4795.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" b_rec.rfe_4795.com IN A +bufsize=2000" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" c_rec.rfe_4795.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="TCP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" d_rec.rfe_4795.com IN A +bufsize=512" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="TCP":
            assert True
        else:
            assert False    
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" e_rec.rfe_4795.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        else:
            assert False
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" b_rec.rfe_4795.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
            
        else:
            assert False    
        
    @pytest.mark.run(order=22)
    def test_021_modify_UDP_size_512_for_view(self):
    
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=max_udp_size')
        #print(get_ref)
        for ref in json.loads(get_ref):
            if 'default' in ref['_ref']:
                print(ref)
                data={'max_udp_size':512}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=max_udp_size')
        
        def_value=512
        for ref in json.loads(get_ref):
            if 'default' in ref['_ref']:
                print(ref)
                if def_value==ref['max_udp_size']:          
                    if get_ref:
                         print("Success:check_UDP_buffer_size_attribute_present and test UDP buffer size 512")
                         print("Restart Services")
                         grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                         ref = json.loads(grid)[0]['_ref']
                         data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                         request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                         sleep(20)
                         assert True
                else:
                  
                    print("Failure: Check_UDP_buffer_size_attribute_present and test UDP buffer size 512")
                    assert False
    @pytest.mark.run(order=23)
    def test_022_check_sizeof_and_test_UDP_512_for_view(self): 
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" a_rec.rfe_4795.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="UDP":
            assert True
        else:
            assert False
            
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" b_rec.rfe_4795.com IN A +bufsize=1220" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" c_rec.rfe_4795.com IN A +bufsize=2000" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="TCP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" d_rec.rfe_4795.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="TCP":
            assert True
        else:
            assert False   
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" e_rec.rfe_4795.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        else:
            assert False    
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" b_rec.rfe_4795.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True  
            
        else:
            assert False
        
    @pytest.mark.run(order=24)
    def test_023_modify_UDP_size_2000_for_view(self):
        print("-----Before modify------")
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=max_udp_size')
        #print(get_ref)
        for ref in json.loads(get_ref):
            if 'default' in ref['_ref']:
                print(ref)
                data={'max_udp_size':2000}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=max_udp_size')
        
        def_value=2000
        for ref in json.loads(get_ref):
            if 'default' in ref['_ref']:
                print(ref)
                if def_value==ref['max_udp_size']:          
                    if get_ref:
                         print("Success:check_UDP_buffer_size_attribute_present and test UDP buffer size 2000")
                         print("Restart Services")
                         grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                         ref = json.loads(grid)[0]['_ref']
                         data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                         request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                         sleep(20)
                         assert True
                else:
                  
                    print("Failure: Check_UDP_buffer_size_attribute_present and test UDP buffer size 2000")
                    assert False
    
    @pytest.mark.run(order=25)
    def test_024_check_sizeof_and_test_UDP_2000_for_view(self): 
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" a_rec.rfe_4795.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" b_rec.rfe_4795.com IN A +bufsize=1220" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" c_rec.rfe_4795.com IN A +bufsize=2500" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" d_rec.rfe_4795.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="TCP":
            assert True
        else:
            assert False    
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" e_rec.rfe_4795.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        else:
            assert False    
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" b_rec.rfe_4795.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
            
        else:
            assert False 
    @pytest.mark.run(order=26)
    def test_025_modify_UDP_size_4096_for_view(self):
        print("-----Before modify------")
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=max_udp_size')
        #print(get_ref)
        for ref in json.loads(get_ref):
            if 'default' in ref['_ref']:
                print(ref)
                data={'max_udp_size':4096}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=max_udp_size')
        
        def_value=4096
        for ref in json.loads(get_ref):
            if 'default' in ref['_ref']:
                print(ref)
                if def_value==ref['max_udp_size']:          
                    if get_ref:
                         print("Success:check_UDP_buffer_size_attribute_present and test UDP buffer size 4096")
                         print("Restart Services")
                         grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                         ref = json.loads(grid)[0]['_ref']
                         data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                         request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                         sleep(20)
                         assert True
                else:
                  
                    print("Failure: Check_UDP_buffer_size_attribute_present and test UDP buffer size 4096")
                    assert False
    
    @pytest.mark.run(order=27)
    def test_026_check_sizeof_and_test_UDP_4096_for_view(self): 
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" a_rec.rfe_4795.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" b_rec.rfe_4795.com IN A +bufsize=1220" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" c_rec.rfe_4795.com IN A +bufsize=512" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="TCP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" d_rec.rfe_4795.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="UDP":
            assert True
        else:
            assert False    
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" e_rec.rfe_4795.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        else:
            assert False
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" b_rec.rfe_4795.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
        else:
            assert False  
        
        
    @pytest.mark.run(order=28)
    def test_027_create_non_default_view(self):
        
        data={'name':"rfe_view"}
        response = ib_NIOS.wapi_request('POST', object_type="view", fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create A record in test zone")
                assert False
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)
        
       

    @pytest.mark.run(order=29)
    def test_028_create_New_AuthZone_non_default_view(self):
        print("Create A new Zone Authoritative zone for non default view")
        
        data = {"fqdn": "rfe_4795_view.com" ,"view":"rfe_view", "grid_primary": [{"name": config.grid_fqdn,"stealth":False}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data),grid_vip=config.grid_vip)
        print response
        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==404:
                print("Failure: Create A Authoritative new Zone for non default view")
                assert False
            else:
                print("Success: Create A Authoritative new Zone for non default view")
                
                assert True
                
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)
        get_ref =  ib_NIOS.wapi_request('GET', object_type="member:dns?_return_fields=views")
        print(get_ref)
        for ref in json.loads(get_ref):
            if 'rfe_view' in ref['views']:
                print("---------------")
                data = {"views": ["rfe_view","default"]}
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
                
    @pytest.mark.run(order=30)
    def test_029_create_A_record_with_different_size_non_default_view(self): 
        print("Creating a record ")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth',grid_vip=config.grid_vip)
        print(get_ref)
  
        for i in range(1,15):
            for ref in json.loads(get_ref):
                if 'rfe_4795_view' in ref['_ref']:
                    data = {
                    "ipv4addr":"13.0.0."+str(i),
                    "view":"rfe_view",
                    "name":"v_rec.rfe_4795_view.com"}
                    response = ib_NIOS.wapi_request('POST',object_type="record:a",fields=json.dumps(data))
                    print(response)
                    if type(response) == tuple:
                        if response[0]==400 or response[0]==401:
                            print("Failure: Create A record in test zone")
                            assert False
        for i in range(1,35):
            for ref in json.loads(get_ref):
                if 'rfe_4795_view.com' in ref['_ref']:
                    data = {
                    "ipv4addr":"13.0.0."+str(i),
                    "view":"rfe_view",
                    "name": "w_rec.rfe_4795_view.com"}
                    response = ib_NIOS.wapi_request('POST',object_type="record:a",fields=json.dumps(data))
                    print(response)
                    if type(response) == tuple:
                        if response[0]==400 or response[0]==401:
                            print("Failure: Create A record in test zone")
                            assert False
                            
        for i in range(1,85):
            for ref in json.loads(get_ref):
                if 'rfe_4795_view.com' in ref['_ref']:
                    data = {
                    "ipv4addr":"13.0.0."+str(i),
                    "view":"rfe_view",
                    "name": "x_rec.rfe_4795_view.com"}
                    response = ib_NIOS.wapi_request('POST',object_type="record:a",fields=json.dumps(data))
                    print(response)
                    if type(response) == tuple:
                        if response[0]==400 or response[0]==401:
                            print("Failure: Create A record in test zone")
                            assert False
                            
                            
                            
        for i in range(1,185):
            for ref in json.loads(get_ref):
                if 'rfe_4795_view.com' in ref['_ref']:
                    data = {
                    "ipv4addr":"13.0.0."+str(i),
                    "view":"rfe_view",
                    "name": "y_rec.rfe_4795_view.com"}
                    response = ib_NIOS.wapi_request('POST',object_type="record:a",fields=json.dumps(data))
                    print(response)
                    if type(response) == tuple:
                        if response[0]==400 or response[0]==401:
                            print("Failure: Create A record in test zone")
                            assert False
                            
                            
        for i in range(1,255):
            for ref in json.loads(get_ref):
                if 'rfe_4795_view.com' in ref['_ref']:
                    data = {
                    "ipv4addr":"13.0.0."+str(i),
                    "view":"rfe_view",
                    "name": "z_rec.rfe_4795_view.com"}
                    response = ib_NIOS.wapi_request('POST',object_type="record:a",fields=json.dumps(data))
                    print(response)
                    if type(response) == tuple:
                        if response[0]==400 or response[0]==401:
                            print("Failure: Create A record in test zone")
                            assert False
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)
    
    @pytest.mark.run(order=31)
    def test_030_modify_UDP_size_1220_for_non_default_view(self):
        print("-----Before modify------")
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=max_udp_size')
        print("\n")
        for ref in json.loads(get_ref):
            if 'rfe_view' in ref['_ref']:
                print(ref)
                data={'max_udp_size':1220}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=max_udp_size')
        
        def_value=1220
        for ref in json.loads(get_ref):
            if 'rfe_view' in ref['_ref']:
                print(ref)
                if def_value==ref['max_udp_size']:          
                    if get_ref:
                         print("Success:check_UDP_buffer_size_attribute_present and test UDP buffer size 1220 for non default view ")
                         print("Restart Services")
                         grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                         ref = json.loads(grid)[0]['_ref']
                         data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                         request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                         sleep(30)
                         assert True
                else:
                  
                    print("Failure: Check_UDP_buffer_size_attribute_present and test UDP buffer size 1220 for non default view")
                    assert False     
            
        
    @pytest.mark.run(order=32)
    def test_031_check_sizeof_and_test_UDP_1220_for_non_default_view(self): 
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" v_rec.rfe_4795_view.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" w_rec.rfe_4795_view.com IN A +bufsize=2000" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" x_rec.rfe_4795_view.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="TCP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" y_rec.rfe_4795_view.com IN A +bufsize=512" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="TCP":
            assert True
        else:
            assert False    
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" z_rec.rfe_4795_view.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        else:
            assert False
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" w_rec.rfe_4795_view.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
            
        else:
            assert False    
        
    @pytest.mark.run(order=33)
    def test_032_modify_UDP_size_512_for_non_default_view(self):
    
        print("-----Before modify------")
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=max_udp_size')
        print("\n")
        for ref in json.loads(get_ref):
            if 'rfe_view' in ref['_ref']:
                print(ref)
                data={'max_udp_size':512}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=max_udp_size')
        
        def_value=512
        for ref in json.loads(get_ref):
            if 'rfe_view' in ref['_ref']:
                print(ref)
                if def_value==ref['max_udp_size']:          
                    if get_ref:
                         print("Success:check_UDP_buffer_size_attribute_present and test UDP buffer size 512 for non default view")
                         print("Restart Services")
                         grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                         ref = json.loads(grid)[0]['_ref']
                         data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                         request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                         sleep(20)
                         assert True
                else:
                  
                    print("Failure: Check_UDP_buffer_size_attribute_present and test UDP buffer size 512 for non default view")
                    assert False     

    @pytest.mark.run(order=34)
    def test_033_check_sizeof_and_test_UDP_512_for_non_default_view(self): 
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" v_rec.rfe_4795_view.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" w_rec.rfe_4795_view.com IN A +bufsize=1220" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" x_rec.rfe_4795_view.com IN A +bufsize=2000" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="TCP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" y_rec.rfe_4795_view.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="TCP":
            assert True
        else:
            assert False   
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" z_rec.rfe_4795_view.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        else:
            assert False    
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" w_rec.rfe_4795_view.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True  
            
        else:
            assert False
        
    @pytest.mark.run(order=35)
    def test_034_modify_UDP_size_2000_for_non_default_view(self):
        print("-----Before modify------")
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=max_udp_size')
        print("\n")
        for ref in json.loads(get_ref):
            if 'rfe_view' in ref['_ref']:
                print(ref)
                data={'max_udp_size':2000}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=max_udp_size')
        
        def_value=2000
        for ref in json.loads(get_ref):
            if 'rfe_view' in ref['_ref']:
                print(ref)
                if def_value==ref['max_udp_size']:          
                    if get_ref:
                         print("Success:check_UDP_buffer_size_attribute_present and test UDP buffer size 2000 for non default view ")
                         print("Restart Services")
                         grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                         ref = json.loads(grid)[0]['_ref']
                         data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                         request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                         sleep(20)
                         assert True
                else:
                  
                    print("Failure: Check_UDP_buffer_size_attribute_present and test UDP buffer size 2000 for non default view")
                    assert False     
    
    @pytest.mark.run(order=36)
    def test_035_check_sizeof_and_test_UDP_2000_for_non_default_view(self): 
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" v_rec.rfe_4795_view.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" w_rec.rfe_4795_view.com IN A +bufsize=1220" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" x_rec.rfe_4795_view.com IN A +bufsize=2500" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" y_rec.rfe_4795_view.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="TCP":
            assert True
        else:
            assert False   
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" z_rec.rfe_4795_view.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        else:
            assert False    
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" w_rec.rfe_4795_view.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
            
        else:
            assert False
            
    @pytest.mark.run(order=37)
    def test_036_modify_UDP_size_4096_for_non_default_view(self):
        print("-----Before modify------")
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=max_udp_size')
        print("\n")
        for ref in json.loads(get_ref):
            if 'rfe_view' in ref['_ref']:
                print(ref)
                data={'max_udp_size':4096}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=max_udp_size')
        
        def_value=4096
        for ref in json.loads(get_ref):
            if 'rfe_view' in ref['_ref']:
                print(ref)
                if def_value==ref['max_udp_size']:          
                    if get_ref:
                         print("Success:check_UDP_buffer_size_attribute_present and test UDP buffer size 4096 for non default view ")
                         print("Restart Services")
                         grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                         ref = json.loads(grid)[0]['_ref']
                         data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                         request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                         sleep(20)
                         assert True
                else:
                  
                    print("Failure: Check_UDP_buffer_size_attribute_present and test UDP buffer size 4096 for non default view")
                    assert False     
        
    @pytest.mark.run(order=38)
    def test_037_check_sizeof_and_test_UDP_4096_for_non_default_view(self): 
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" v_rec.rfe_4795_view.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" w_rec.rfe_4795_view.com IN A +bufsize=1220" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" x_rec.rfe_4795_view.com IN A +bufsize=512" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="TCP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" y_rec.rfe_4795_view.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="UDP":
            assert True
        else:
            assert False   
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" z_rec.rfe_4795_view.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        else:
            assert False
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" w_rec.rfe_4795_view.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
            
        else:
            assert False
        
        
    @pytest.mark.run(order=39)
    def test_038_create_forwards_of_second_grid_in_first_grid(self):
       
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns')
        print(get_ref)
        for ref in json.loads(get_ref):
            data={"allow_recursive_query":True,
                  "forward_only":True,
                  "forwarders":[config.grid2_vip]}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
            print(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    print("Failure: Create A record in test zone")
                    assert False
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)
        
        
    @pytest.mark.run(order=40)
    def test_039_create_New_AuthZone_grid2(self):
        print("Create A new Zone Authoritative zone")
      
        data = {"fqdn": "rfe_4795_edns.com","grid_primary": [{"name": config.grid2_fqdn,"stealth":False}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data),grid_vip=config.grid2_vip)
        print response
        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==404:
                print("Failure: Create A Authoritative new Zone for grid2")
                assert False
            else:
                print("Success: Create A Authoritative new Zone for grid2")
                assert True
                
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid2_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid2_vip)
        sleep(30)
                
                
    @pytest.mark.run(order=41)
    def test_040_create_A_record_with_different_size_grid2(self): 
        print("Creating a record ")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth',grid_vip=config.grid2_vip)
        print(get_ref)
  
        for i in range(1,15):
            for ref in json.loads(get_ref):
                if 'rfe_4795_edns.com' in ref['_ref']:
                    data = {
                    "ipv4addr":"13.0.0."+str(i),
                    "view":"default",
                    "name": "m_rec.rfe_4795_edns.com"}
                    response = ib_NIOS.wapi_request('POST',object_type="record:a",fields=json.dumps(data),grid_vip=config.grid2_vip)
                    print(response)
                    if type(response) == tuple:
                        if response[0]==400 or response[0]==401:
                            print("Failure: Create A record in test zone")
                            assert False
        for i in range(1,35):
            for ref in json.loads(get_ref):
                if 'rfe_4795_edns.com' in ref['_ref']:
                    data = {
                    "ipv4addr":"13.0.0."+str(i),
                    "view":"default",
                    "name": "n_rec.rfe_4795_edns.com"}
                    response = ib_NIOS.wapi_request('POST',object_type="record:a",fields=json.dumps(data),grid_vip=config.grid2_vip)
                    print(response)
                    if type(response) == tuple:
                        if response[0]==400 or response[0]==401:
                            print("Failure: Create A record in test zone")
                            assert False
                            
        for i in range(1,85):
            for ref in json.loads(get_ref):
                if 'rfe_4795_edns.com' in ref['_ref']:
                    data = {
                    "ipv4addr":"13.0.0."+str(i),
                    "view":"default",
                    "name": "o_rec.rfe_4795_edns.com"}
                    response = ib_NIOS.wapi_request('POST',object_type="record:a",fields=json.dumps(data),grid_vip=config.grid2_vip)
                    print(response)
                    if type(response) == tuple:
                        if response[0]==400 or response[0]==401:
                            print("Failure: Create A record in test zone")
                            assert False
                            
                            
                            
        for i in range(1,185):
            for ref in json.loads(get_ref):
                if 'rfe_4795_edns.com' in ref['_ref']:
                    data = {
                    "ipv4addr":"13.0.0."+str(i),
                    "view":"default",
                    "name": "p_rec.rfe_4795_edns.com"}
                    response = ib_NIOS.wapi_request('POST',object_type="record:a",fields=json.dumps(data),grid_vip=config.grid2_vip)
                    print(response)
                    if type(response) == tuple:
                        if response[0]==400 or response[0]==401:
                            print("Failure: Create A record in test zone")
                            assert False
                            
                            
        for i in range(1,255):
            for ref in json.loads(get_ref):
                if 'rfe_4795_edns.com' in ref['_ref']:
                    data = {
                    "ipv4addr":"13.0.0."+str(i),
                    "view":"default",
                    "name": "q_rec.rfe_4795_edns.com"}
                    response = ib_NIOS.wapi_request('POST',object_type="record:a",fields=json.dumps(data),grid_vip=config.grid2_vip)
                    print(response)
                    if type(response) == tuple:
                        if response[0]==400 or response[0]==401:
                            print("Failure: Create A record in test zone")
                            assert False
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid2_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid2_vip)
        sleep(30)
    
    
    @pytest.mark.run(order=42)
    def test_041_check_default_edns_size_1220_for_grid1(self):
        print("Restarting DNS member of grid2")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns',grid_vip=config.grid2_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps({"enable_dns":True}),grid_vip=config.grid2_vip)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    assert False
            else:
                assert True
                
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns?_return_fields=max_udp_size',grid_vip=config.grid2_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            data={'max_udp_size':4096}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data),grid_vip=config.grid2_vip)
            print(response)
            print("Restart Services")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid2_vip)
            ref = json.loads(grid)[0]['_ref']
            data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid2_vip)
            sleep(20)
            assert True
        
        
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns?_return_fields=edns_udp_size')
        print(get_ref)
        def_value=1220
        for ref in json.loads(get_ref):
            if def_value==ref['edns_udp_size']:          
                if get_ref:
                     print("Success:check_EDNS_buffer_size_attribute_present and test EDNS buffer size is 1220")
                     
                     assert True
                else:
                  
                    print("Failure: check_EDNS_buffer_size_attribute_present and test EDNS buffer size is 1220")
                    assert False
    
    
    @pytest.mark.run(order=43)
    def test_042_check_default_EDNS_size_1220_for_grid1(self): 
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" m_rec.rfe_4795_edns.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()   
        if res1=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" n_rec.rfe_4795_edns.com IN A +bufsize=2000" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" o_rec.rfe_4795_edns.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="TCP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" p_rec.rfe_4795_edns.com IN A +bufsize=512" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="TCP":
            assert True
        else:
            assert False    
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" q_rec.rfe_4795_edns.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" n_rec.rfe_4795_edns.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
            
        else:
            assert False    
        clear_DNS_cache()
        
    @pytest.mark.run(order=44)
    def test_043_modify_EDNS_size_512_for_grid1(self):
    
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns?_return_fields=edns_udp_size')
        print(get_ref)
        for ref in json.loads(get_ref):
            data={'edns_udp_size':512}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
            print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns?_return_fields=edns_udp_size')
        print(get_ref)
        def_value=512
        for ref in json.loads(get_ref):
            if def_value==ref['edns_udp_size']:          
                if get_ref:
                     print("Success:check_EDNS_buffer_size_attribute_present and test EDNS buffer size is 512")
                     print("Restart Services")
                     grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                     ref = json.loads(grid)[0]['_ref']
                     data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                     request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                     sleep(20)
                     assert True
                else:
                  
                    print("Failure: check_EDNS_buffer_size_attribute_present and test EDNS buffer size is 512")
                    assert False
    
    @pytest.mark.run(order=45)
    def test_044_check_sizeof_and_test_EDNS_512_for_grid1(self): 
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" m_rec.rfe_4795_edns.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" n_rec.rfe_4795_edns.com IN A +bufsize=1220" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" o_rec.rfe_4795_edns.com IN A +bufsize=2000" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="TCP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" p_rec.rfe_4795_edns.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="TCP":
            assert True
        else:
            assert False   
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" q_rec.rfe_4795_edns.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
            
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" n_rec.rfe_4795_edns.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True  
            
        else:
            assert False
        clear_DNS_cache()
        
    @pytest.mark.run(order=46)
    def test_045_modify_EDNS_size_2000_for_grid1(self):
        print("-----Before modify------")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns?_return_fields=edns_udp_size')
        print(get_ref)
        for ref in json.loads(get_ref):
            data={'edns_udp_size':2000}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
            print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns?_return_fields=edns_udp_size')
        print(get_ref)
        def_value=2000
        for ref in json.loads(get_ref):
            if def_value==ref['edns_udp_size']:          
                if get_ref:
                     print("Success:check_EDNS_buffer_size_attribute_present and test EDNS buffer size 2000")
                     print("Restart Services")
                     grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                     ref = json.loads(grid)[0]['_ref']
                     data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                     request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                     sleep(20)
                     assert True
                else:
                  
                    print("Failure: check_EDNS_buffer_size_attribute_present and test EDNS buffer size 2000")
                    assert False
    
    @pytest.mark.run(order=47)
    def test_046_check_sizeof_and_test_EDNS_2000_for_grid1(self): 
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" m_rec.rfe_4795_edns.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" n_rec.rfe_4795_edns.com IN A +bufsize=1220" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" o_rec.rfe_4795_edns.com IN A +bufsize=2500" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" p_rec.rfe_4795_edns.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="TCP":
            assert True
        else:
            assert False    
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" q_rec.rfe_4795_edns.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        else:
            assert False    
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" n_rec.rfe_4795_edns.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
            
        else:
            assert False  
        
        clear_DNS_cache()
        
    @pytest.mark.run(order=48)
    def test_047_modify_EDNS_size_4096_for_grid1(self):
        print("-----Before modify------")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns?_return_fields=edns_udp_size')
        print(get_ref)
        for ref in json.loads(get_ref):
            data={'edns_udp_size':4096}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
            print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns?_return_fields=edns_udp_size')
        print(get_ref)
        def_value=4096
        for ref in json.loads(get_ref):
            if def_value==ref['edns_udp_size']:          
                if get_ref:
                     print("Success:check_EDNS_buffer_size_attribute_present and test EDNS buffer size 4096")
                     print("Restart Services")
                     grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                     ref = json.loads(grid)[0]['_ref']
                     data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                     request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                     sleep(20)
                     assert True
                else:
                  
                    print("Failure: check_EDNS_buffer_size_attribute_present and test EDNS buffer size 4096")
                    assert False
    
    @pytest.mark.run(order=49)
    def test_048_check_sizeof_and_test_EDNS_4096_for_grid1(self): 
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" m_rec.rfe_4795_edns.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" n_rec.rfe_4795_edns.com IN A +bufsize=1220" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" o_rec.rfe_4795_edns.com IN A +bufsize=512" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="TCP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" p_rec.rfe_4795_edns.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="UDP":
            assert True
        else:
            assert False   
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" q_rec.rfe_4795_edns.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" n_rec.rfe_4795_edns.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
            
        else:
            assert False
        clear_DNS_cache()
        
    @pytest.mark.run(order=50)
    def test_049_check_default_edns_size_1220_for_grid1_member(self):
        print("-----Before modify------")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=edns_udp_size')
        print(get_ref)
        for ref in json.loads(get_ref):
            data={'edns_udp_size':1220}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
            print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=edns_udp_size')
        print(get_ref)
        def_value=1220
        for ref in json.loads(get_ref):
            if def_value==ref['edns_udp_size']:          
                if get_ref:
                     print("Success:check_EDNS_buffer_size_attribute_present and test EDNS buffer size is 1220")
                     print("Restart Services")
                     grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                     ref = json.loads(grid)[0]['_ref']
                     data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                     request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                     sleep(20)
                     assert True
                else:
                  
                    print("Failure: check_EDNS_buffer_size_attribute_present and test EDNS buffer size is 1220")
                    assert False
    
    
    @pytest.mark.run(order=51)
    def test_050_check_default_EDNS_size_1220_for_grid1_member(self): 
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" m_rec.rfe_4795_edns.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()   
        if res1=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" n_rec.rfe_4795_edns.com IN A +bufsize=2000" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" o_rec.rfe_4795_edns.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="TCP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" p_rec.rfe_4795_edns.com IN A +bufsize=512" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="TCP":
            assert True
        else:
            assert False   
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" q_rec.rfe_4795_edns.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" n_rec.rfe_4795_edns.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
            
        else:
            assert False
        clear_DNS_cache()
        
    @pytest.mark.run(order=52)
    def test_051_modify_EDNS_size_512_for_grid1_member(self):
    
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=edns_udp_size')
        print(get_ref)
        for ref in json.loads(get_ref):
            data={'edns_udp_size':512}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
            print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=edns_udp_size')
        print(get_ref)
        def_value=512
        for ref in json.loads(get_ref):
            if def_value==ref['edns_udp_size']:          
                if get_ref:
                     print("Success:check_EDNS_buffer_size_attribute_present and test EDNS buffer size is 512")
                     print("Restart Services")
                     grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                     ref = json.loads(grid)[0]['_ref']
                     data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                     request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                     sleep(20)
                     assert True
                else:
                  
                    print("Failure: check_EDNS_buffer_size_attribute_present and test EDNS buffer size is 512")
                    assert False
    
    @pytest.mark.run(order=53)
    def test_052_check_sizeof_and_test_EDNS_512_for_grid1_member(self): 
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" m_rec.rfe_4795_edns.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" n_rec.rfe_4795_edns.com IN A +bufsize=1220" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" o_rec.rfe_4795_edns.com IN A +bufsize=2000" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="TCP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" p_rec.rfe_4795_edns.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="TCP":
            assert True
        else:
            assert False   
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" q_rec.rfe_4795_edns.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
            
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" n_rec.rfe_4795_edns.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True  
            
        else:
            assert False
        clear_DNS_cache()
        
    @pytest.mark.run(order=54)
    def test_053_modify_EDNS_size_2000_for_grid1_member(self):
        print("-----Before modify------")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=edns_udp_size')
        print(get_ref)
        for ref in json.loads(get_ref):
            data={'edns_udp_size':2000}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data),grid_vip=config.grid2_vip)
            print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=edns_udp_size')
        print(get_ref)
        def_value=2000
        for ref in json.loads(get_ref):
            if def_value==ref['edns_udp_size']:          
                if get_ref:
                     print("Success:check_EDNS_buffer_size_attribute_present and test EDNS buffer size 2000")
                     print("Restart Services")
                     grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                     ref = json.loads(grid)[0]['_ref']
                     data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                     request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                     sleep(20)
                     assert True
                else:
                  
                    print("Failure: check_EDNS_buffer_size_attribute_present and test EDNS buffer size 2000")
                    assert False
    
    @pytest.mark.run(order=55)
    def test_054_check_sizeof_and_test_EDNS_2000_for_grid1_member(self): 
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" m_rec.rfe_4795_edns.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" n_rec.rfe_4795_edns.com IN A +bufsize=1220" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" o_rec.rfe_4795_edns.com IN A +bufsize=2500" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" p_rec.rfe_4795_edns.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="UDP":
            assert True
        else:
            assert False    
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" q_rec.rfe_4795_edns.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        else:
            assert False    
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" n_rec.rfe_4795_edns.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
            
        else:
            assert False  
        
        clear_DNS_cache()
    @pytest.mark.run(order=56)
    def test_055_modify_EDNS_size_4096_for_grid1_member(self):
        print("-----Before modify------")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=edns_udp_size')
        print(get_ref)
        for ref in json.loads(get_ref):
            data={'edns_udp_size':4096}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
            print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=edns_udp_size')
        print(get_ref)
        def_value=4096
        for ref in json.loads(get_ref):
            if def_value==ref['edns_udp_size']:          
                if get_ref:
                     print("Success:check_EDNS_buffer_size_attribute_present and test EDNS buffer size 4096")
                     print("Restart Services")
                     grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                     ref = json.loads(grid)[0]['_ref']
                     data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                     request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                     sleep(20)
                     assert True
                else:
                  
                    print("Failure: check_EDNS_buffer_size_attribute_present and test EDNS buffer size 4096")
                    assert False
    
    @pytest.mark.run(order=57)
    def test_056_check_sizeof_and_test_EDNS_4096_for_grid1_member(self): 
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" m_rec.rfe_4795_edns.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" n_rec.rfe_4795_edns.com IN A +bufsize=1220" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" o_rec.rfe_4795_edns.com IN A +bufsize=512" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="TCP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" p_rec.rfe_4795_edns.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="UDP":
            assert True
        else:
            assert False    
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" q_rec.rfe_4795_edns.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" n_rec.rfe_4795_edns.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
            
        else:
            assert False
        clear_DNS_cache()
        
    @pytest.mark.run(order=58)
    def test_057_check_default_EDNS_size_1220_for_grid1_view(self):
        print("-----Before modify------")
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=edns_udp_size')
        print(get_ref)
        for ref in json.loads(get_ref):
            data={'edns_udp_size':1220}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
            print(response)
        print("----After modify----") 
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=edns_udp_size')
        print(get_ref)
        def_value=1220
        for ref in json.loads(get_ref):
            if def_value==ref['edns_udp_size']:          
                if get_ref:
                     print("Success:check_EDNS_buffer_size_attribute_present and test EDNS buffer size 1220")
                     print("Restart Services")
                     grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                     ref = json.loads(grid)[0]['_ref']
                     data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                     request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                     sleep(20)
                     assert True
            else:
              
                print("Failure: Check_EDNS_buffer_size_attribute_present and test EDNS buffer size 1220")
                assert False 
    
    @pytest.mark.run(order=59)
    def test_058_check_default_EDNS_size_1220_for_grid1_view(self): 
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" m_rec.rfe_4795_edns.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" n_rec.rfe_4795_edns.com IN A +bufsize=2000" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" o_rec.rfe_4795_edns.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="TCP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" p_rec.rfe_4795_edns.com IN A +bufsize=512" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="TCP":
            assert True
        else:
            assert False    
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" q_rec.rfe_4795_edns.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        else:
            assert False
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" n_rec.rfe_4795_edns.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
        else:
            assert False  
        clear_DNS_cache()
        
    @pytest.mark.run(order=60)
    def test_059_modify_EDNS_size_512_for_grid1_view(self):
    
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=edns_udp_size')
        print(get_ref)
        for ref in json.loads(get_ref):
            data={'edns_udp_size':512}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
            print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=edns_udp_size')
        print(get_ref)
        def_value=512
        for ref in json.loads(get_ref):
            if def_value==ref['edns_udp_size']:          
                if get_ref:
                     print("Success:check_EDNS_buffer_size_attribute_present and test EDNS buffer size is 512")
                     print("Restart Services")
                     grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                     ref = json.loads(grid)[0]['_ref']
                     data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                     request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                     sleep(20)
                     assert True
                else:
                  
                    print("Failure: check_EDNS_buffer_size_attribute_present and test EDNS buffer size is 512")
                    assert False
    
    @pytest.mark.run(order=61)
    def test_060_check_sizeof_and_test_EDNS_512_for_grid1_view(self): 
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" m_rec.rfe_4795_edns.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" n_rec.rfe_4795_edns.com IN A +bufsize=1220" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" o_rec.rfe_4795_edns.com IN A +bufsize=2000" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="TCP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" p_rec.rfe_4795_edns.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="TCP":
            assert True
        else:
            assert False   
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" q_rec.rfe_4795_edns.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        else:
            assert False    
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" n_rec.rfe_4795_edns.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True  
            
        else:
            assert False
        
        clear_DNS_cache()
        
    @pytest.mark.run(order=62)
    def test_061_modify_EDNS_size_2000_for_grid1_view(self):
        print("-----Before modify------")
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=edns_udp_size')
        print(get_ref)
        for ref in json.loads(get_ref):
            data={'edns_udp_size':2000}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
            print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=edns_udp_size')
        print(get_ref)
        def_value=2000
        for ref in json.loads(get_ref):
            if def_value==ref['edns_udp_size']:          
                if get_ref:
                     print("Success:check_EDNS_buffer_size_attribute_present and test EDNS buffer size 2000")
                     print("Restart Services")
                     grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                     ref = json.loads(grid)[0]['_ref']
                     data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                     request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                     sleep(20)
                     assert True
                else:
                  
                    print("Failure: check_EDNS_buffer_size_attribute_present and test EDNS buffer size 2000")
                    assert False
    
    @pytest.mark.run(order=63)
    def test_062_check_sizeof_and_test_EDNS_2000_for_grid1_view(self): 
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" m_rec.rfe_4795_edns.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" n_rec.rfe_4795_edns.com IN A +bufsize=1220" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" o_rec.rfe_4795_edns.com IN A +bufsize=2500" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" p_rec.rfe_4795_edns.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="TCP":
            assert True
        else:
            assert False   
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" q_rec.rfe_4795_edns.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        else:
            assert False   
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" n_rec.rfe_4795_edns.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
            
        else:
            assert False 
        
        clear_DNS_cache()
        
    @pytest.mark.run(order=64)
    def test_063_modify_EDNS_size_4096_for_grid1_view(self):
        print("-----Before modify------")
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=edns_udp_size')
        print(get_ref)
        for ref in json.loads(get_ref):
            data={'edns_udp_size':4096}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
            print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=edns_udp_size')
        print(get_ref)
        def_value=4096
        for ref in json.loads(get_ref):
            if def_value==ref['edns_udp_size']:          
                if get_ref:
                     print("Success:check_EDNS_buffer_size_attribute_present and test EDNS buffer size 4096")
                     print("Restart Services")
                     grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                     ref = json.loads(grid)[0]['_ref']
                     data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                     request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                     sleep(20)
                     assert True
                else:
                  
                    print("Failure: check_EDNS_buffer_size_attribute_present and test EDNS buffer size 4096")
                    assert False
    
    @pytest.mark.run(order=65)
    def test_064_check_sizeof_and_test_EDNS_4096_for_grid1_view(self): 
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" m_rec.rfe_4795_edns.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" n_rec.rfe_4795_edns.com IN A +bufsize=1220" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" o_rec.rfe_4795_edns.com IN A +bufsize=512" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="TCP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" p_rec.rfe_4795_edns.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="UDP":
            assert True
        else:
            assert False   
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" q_rec.rfe_4795_edns.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" n_rec.rfe_4795_edns.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
            
        else:
            assert False
        
        clear_DNS_cache()
       

    
    @pytest.mark.run(order=66)
    def test_065_check_non_default_view_edns(self):        
        get_ref =  ib_NIOS.wapi_request('GET', object_type="member:dns?_return_fields=views", grid_vip=config.grid_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            if 'rfe_view' in ref['views']:
                print("---------------")
                data = {"views": ["rfe_view","default"]}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response) 
        
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: Set a Views Assigned to This Member")
                        assert False
                else:
                    print("Success: Set a Views Assigned to This Member")
                    get_ref =  ib_NIOS.wapi_request('GET', object_type="member:dns?_return_fields=views" , grid_vip=config.grid_vip)
                    print(get_ref)          
                    print("Restart Services")
                    grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                    ref = json.loads(grid)[0]['_ref']
                    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data), grid_vip=config.grid_vip)
                    sleep(20)
                    assert True
                  
    
    @pytest.mark.run(order=67)
    def test_066_modify_EDNS_size_1220_for_non_default_view_edns(self):
        print("-----Before modify------")
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=edns_udp_size', grid_vip=config.grid_vip)
        print("\n")
        for ref in json.loads(get_ref):
            if 'rfe_view' in ref['_ref']:
                print(ref)
                data={'edns_udp_size':1220}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=edns_udp_size',grid_vip=config.grid_vip)
        
        def_value=1220
        for ref in json.loads(get_ref):
            if 'rfe_view' in ref['_ref']:
                print(ref)
                if def_value==ref['edns_udp_size']:          
                    if get_ref:
                         print("Success:check_EDNS_buffer_size_attribute_present and test EDNS buffer size 1220 for non default view ")
                         print("Restart Services")
                         grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid2_vip)
                         ref = json.loads(grid)[0]['_ref']
                         data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                         request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data), grid_vip=config.grid_vip)
                         sleep(30)
                         assert True
                else:
                  
                    print("Failure: Check_EDNS_buffer_size_attribute_present and test EDNS buffer size 1220 for non default view")
                    assert False     
            
        
    @pytest.mark.run(order=68)
    def test_067_check_sizeof_and_test_EDNS_1220_for_non_default_view_edns(self): 
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" m_rec.rfe_4795_edns.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" n_rec.rfe_4795_edns.com IN A +bufsize=2000" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" o_rec.rfe_4795_edns.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="TCP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" p_rec.rfe_4795_edns.com IN A +bufsize=512" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="TCP":
            assert True
        else:
            assert False    
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" q_rec.rfe_4795_edns.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        else:
            assert False
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" n_rec.rfe_4795_edns.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
            
        else:
            assert False    
       
        clear_DNS_cache() 
       
       
    @pytest.mark.run(order=69)
    def test_068_modify_EDNS_size_512_for_non_default_view_edns(self):
    
        print("-----Before modify------")
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=edns_udp_size', grid_vip=config.grid_vip)
        print("\n")
        for ref in json.loads(get_ref):
            if 'rfe_view' in ref['_ref']:
                print(ref)
                data={'edns_udp_size':512}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=edns_udp_size', grid_vip=config.grid_vip)
        
        def_value=512
        for ref in json.loads(get_ref):
            if 'rfe_view' in ref['_ref']:
                print(ref)
                if def_value==ref['edns_udp_size']:          
                    if get_ref:
                         print("Success:check_EDNS_buffer_size_attribute_present and test EDNS buffer size 512 for non default view")
                         print("Restart Services")
                         grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                         ref = json.loads(grid)[0]['_ref']
                         data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                         request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data), grid_vip=config.grid_vip)
                         sleep(20)
                         assert True
                else:
                  
                    print("Failure: Check_EDNS_buffer_size_attribute_present and test EDNS buffer size 512 for non default view")
                    assert False     

    @pytest.mark.run(order=70)
    def test_069_check_sizeof_and_test_EDNS_512_for_non_default_view_edns(self): 
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" m_rec.rfe_4795_edns.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" n_rec.rfe_4795_edns.com IN A +bufsize=1220" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" o_rec.rfe_4795_edns.com IN A +bufsize=2000" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="TCP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" p_rec.rfe_4795_edns.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="TCP":
            assert True
        else:
            assert False   
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" q_rec.rfe_4795_edns.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        else:
            assert False    
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" n_rec.rfe_4795_edns.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True  
            
        else:
            assert False
        clear_DNS_cache()
        
    @pytest.mark.run(order=71)
    def test_070_modify_EDNS_size_2000_for_non_default_view_edns(self):
        print("-----Before modify------")
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=edns_udp_size', grid_vip=config.grid_vip)
        print("\n")
        for ref in json.loads(get_ref):
            if 'rfe_view' in ref['_ref']:
                print(ref)
                data={'edns_udp_size':2000}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=edns_udp_size', grid_vip=config.grid_vip)
        
        def_value=2000
        for ref in json.loads(get_ref):
            if 'rfe_view' in ref['_ref']:
                print(ref)
                if def_value==ref['edns_udp_size']:          
                    if get_ref:
                         print("Success:check_EDNS_buffer_size_attribute_present and test EDNS buffer size 2000 for non default view ")
                         print("Restart Services")
                         grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                         ref = json.loads(grid)[0]['_ref']
                         data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                         request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data), grid_vip=config.grid_vip)
                         sleep(20)
                         assert True
                else:
                  
                    print("Failure: Check_EDNS_buffer_size_attribute_present and test EDNS buffer size 2000 for non default view")
                    assert False     
    
    @pytest.mark.run(order=72)
    def test_071_check_sizeof_and_test_UDP_2000_for_non_default_view_edns(self): 
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" m_rec.rfe_4795_edns.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" n_rec.rfe_4795_edns.com IN A +bufsize=1220" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" o_rec.rfe_4795_edns.com IN A +bufsize=2500" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" p_rec.rfe_4795_edns.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="TCP":
            assert True
        else:
            assert False   
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" q_rec.rfe_4795_edns.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        else:
            assert False    
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" n_rec.rfe_4795_edns.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
            
        else:
            assert False
        clear_DNS_cache()    
        
    @pytest.mark.run(order=73)
    def test_072_modify_EDNS_size_4096_for_non_default_view_edns(self):
        print("-----Before modify------")
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=edns_udp_size', grid_vip=config.grid_vip)
        print("\n")
        for ref in json.loads(get_ref):
            if 'rfe_view' in ref['_ref']:
                print(ref)
                data={'edns_udp_size':4096}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=edns_udp_size', grid_vip=config.grid_vip)
        
        def_value=4096
        for ref in json.loads(get_ref):
            if 'rfe_view' in ref['_ref']:
                print(ref)
                if def_value==ref['edns_udp_size']:          
                    if get_ref:
                         print("Success:check_EDNS_buffer_size_attribute_present and test EDNS buffer size 4096 for non default view ")
                         print("Restart Services")
                         grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                         ref = json.loads(grid)[0]['_ref']
                         data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                         request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data), grid_vip=config.grid_vip)
                         sleep(20)
                         assert True
                else:
                  
                    print("Failure: Check_EDNS_buffer_size_attribute_present and test EDNS buffer size 4096 for non default view")
                    assert False     
        
    @pytest.mark.run(order=74)
    def test_073_check_sizeof_and_test_EDNS_4096_for_non_default_view_edns(self): 
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" m_rec.rfe_4795_edns.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" n_rec.rfe_4795_edns.com IN A +bufsize=1220" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="UDP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" o_rec.rfe_4795_edns.com IN A +bufsize=512" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="TCP":
            assert True
        else:
            assert False
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" p_rec.rfe_4795_edns.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="UDP":
            assert True
        else:
            assert False   
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" q_rec.rfe_4795_edns.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        else:
            assert False
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" n_rec.rfe_4795_edns.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
            
        else:
            assert False
        clear_DNS_cache()

    @pytest.mark.run(order=75)
    def test_074_Negative_test_UDP(self):
        print("Negative test for UDP Buffer")
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=max_udp_size')
        print("\n")
        for ref in json.loads(get_ref):
            if 'rfe_view' in ref['_ref']:
                print(ref)
                data={'max_udp_size':"abcd"}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401 or response[0]==404:
                        print("Success: Numeric characters for Negative test for UDP Buffer")
                        assert True
                    else:
                        print("Failure: Numeric characters for Negative test for UDP Buffer")
                        assert False
       
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=max_udp_size')
        print("\n")
        for ref in json.loads(get_ref):
            if 'rfe_view' in ref['_ref']:
                print(ref)
                data={'max_udp_size':5000}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401 or response[0]==404:
                        print("Success: 5000 for Negative test for UDP Buffer")
                        assert True
                    else:
                        print("Failure: 5000 for Negative test for UDP Buffer")
                        assert False
        
    @pytest.mark.run(order=76)
    def test_075_Negative_test_EDNS(self):
        print("Negative test for EDNS Buffer")
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=edns_udp_size', grid_vip=config.grid_vip)
        print("\n")
        for ref in json.loads(get_ref):
            if 'rfe_view' in ref['_ref']:
                print(ref)
                data={'edns_udp_size':"abcd"}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
                
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401 or response[0]==404:
                        print("Success: Numeric characters for Negative test for EDNS Buffer")
                        assert True
                    else:
                        print("Failure: Numeric characters for Negative test for EDNS Buffer")
                        assert False
                        
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=edns_udp_size', grid_vip=config.grid_vip)
        print("\n")
        for ref in json.loads(get_ref):
            if 'rfe_view' in ref['_ref']:
                print(ref)
                data={'edns_udp_size':5000}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
               
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401 or response[0]==404:
                        print("Success: 5000 for Negative test for EDNS Buffer")
                        assert True
                    else:
                        print("Failure: 5000 for Negative test for EDNS Buffer")
                        assert False
                        
                        
    @pytest.mark.run(order=77)
    def test_076_check_changes_are_reflecting_in_audit_logs(self):
        
        print("check changes are reflecting in audit logs")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        transport = client.get_transport()
        channel_tcpdump = transport.open_session()
        channel_tcpdump.get_pty()
        channel_tcpdump.set_combine_stderr(True)
        data="cat /infoblox/var/audit.log"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        #print("output ",stdout)
           
        if 'Modified GridDns Infoblox: Changed edns_udp_size:1220->512' in stdout and 'Modified GridDns Infoblox: Changed max_udp_size:1220->512' in stdout:
            print("Changes are reflecting in audit logs")
            client.close()
            assert True
        
    
    @pytest.mark.run(order=78)
    def test_077_enable_all_interfaces(self):
            
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=use_lan2_port,use_mgmt_port,use_lan_port,use_mgmt_ipv6_port,use_lan_ipv6_port,use_lan2_ipv6_port', grid_vip=config.grid_vip)
        print("\n")
        #print(get_ref)
        for ref in json.loads(get_ref):
            data={"use_lan_port": True,"use_lan2_port": True,"use_mgmt_port": True,"use_lan2_ipv6_port": True,"use_lan_ipv6_port": True,"use_mgmt_ipv6_port": True}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            print(response)
               
            if type(response) == tuple:
                if response[0]==400 or response[0]==401 or response[0]==404:
                    print("Failure: All interface are enabled")
                    assert False
                    
            else:
                print("Success: All interface are enabled")
                print("Restart Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data), grid_vip=config.grid_vip)
                sleep(80)
                assert True
        
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=use_lan2_port,use_mgmt_port,use_lan_port,use_mgmt_ipv6_port,use_lan_ipv6_port,use_lan2_ipv6_port', grid_vip=config.grid_vip)
        print(get_ref)
    
    
    @pytest.mark.run(order=79)
    def test_078_performing_dig_query_from_different_interfaces_UDP(self):
        get_ref =  ib_NIOS.wapi_request('GET', object_type="member:dns?_return_fields=views", grid_vip=config.grid_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            data = {"views": ["default","rfe_view"]}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            print(response)

        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=max_udp_size')
        print("\n")
        for ref in json.loads(get_ref):
            if 'default' in ref['_ref']:
                print(ref)
                data={'max_udp_size':1220}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=max_udp_size')
        
        def_value=1220
        for ref in json.loads(get_ref):
            if 'default' in ref['_ref']:
                print(ref)
                if def_value==ref['max_udp_size']:          
                    if get_ref:
                         print("Success:check_UDP_buffer_size_attribute_present and test UDP buffer size 1220 for non default view")
                         print("Restart Services")
                         grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                         ref = json.loads(grid)[0]['_ref']
                         data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                         request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                         sleep(20)
                         assert True
                else:
                  
                    print("Failure: Check_UDP_buffer_size_attribute_present and test UDP buffer size 1220 for non default view")
                    assert False
                
        print('------------Ipv4:LAN2-------------------')
        dig="dig @"+config.grid_master_vip+" c_rec.rfe_4795.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="TCP":
            assert True
        else:
            assert False
        print('-------------Ipv4:MGMT------------------')
        dig="dig @"+config.grid_master_mgmt+" d_rec.rfe_4795.com IN A +bufsize=1220" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
        else:
            assert False
        print('-------------Ipv6:LAN1------------------')
        dig="dig @"+config.grid_master_lan_v6+" a_rec.rfe_4795.com IN A +bufsize=512" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp_ipv6()
        if res3=="UDP":
            assert True
        else:
            assert False
        print('-----------Ipv6:LAN2--------------------')
        dig="dig @"+config.grid_master_lan2_v6+" b_rec.rfe_4795.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp_ipv6()
        if res4=="UDP":
            assert True
        else:
            assert False   
        print('--------------Ipv6:MGMT-----------------')
        dig="dig @"+config.grid_master_mgmt_v6+" e_rec.rfe_4795.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp_ipv6()
        if res5=="TCP":
            assert True
        else:
            assert False
        
        print('--------------Ipv6:LAN1----------------------------')
        dig="dig @"+config.grid_master_lan_v6+" b_rec.rfe_4795.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp_ipv6()
        if res2=="TCP":
            assert True
            
        else:
            assert False

            
        print("-----Before modify------")
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=max_udp_size')
        print("\n")
        for ref in json.loads(get_ref):
            if 'default' in ref['_ref']:
                print(ref)
                data={'max_udp_size':512}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=max_udp_size')
        
        def_value=512
        for ref in json.loads(get_ref):
            if 'default' in ref['_ref']:
                print(ref)
                if def_value==ref['max_udp_size']:          
                    if get_ref:
                         print("Success:check_UDP_buffer_size_attribute_present and test UDP buffer size 512 for non default view")
                         print("Restart Services")
                         grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                         ref = json.loads(grid)[0]['_ref']
                         data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                         request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                         sleep(20)
                         assert True
                else:
                  
                    print("Failure: Check_UDP_buffer_size_attribute_present and test UDP buffer size 512 for non default view")
                    assert False
               
        print('-------------Ipv6:LAN1------------------')
        dig="dig @"+config.grid_master_lan_v6+" a_rec.rfe_4795.com IN A +bufsize=512" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp_ipv6()
        if res3=="UDP":
            assert True
        else:
            assert False
        print('-----------Ipv6:LAN2--------------------')
        dig="dig @"+config.grid_master_lan2_v4+" b_rec.rfe_4795.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp_ipv6()
        if res4=="TCP":
            assert True
        else:
            assert False   
        print('--------------Ipv6:MGMT-----------------')
        dig="dig @"+config.grid_master_mgmt_v6+" e_rec.rfe_4795.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp_ipv6()
        if res5=="TCP":
            assert True
        else:
            assert False
        print('--------------Ipv6:LAN1----------------------------')
        dig="dig @"+config.grid_master_lan_v6+" b_rec.rfe_4795.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp_ipv6()
        if res2=="TCP":
            assert True
            
        else:
            assert False
        
        print("-----Before modify------")
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=max_udp_size')
        print("\n")
        for ref in json.loads(get_ref):
            if 'default' in ref['_ref']:
                print(ref)
                data={'max_udp_size':2000}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=max_udp_size')
        
        def_value=2000
        for ref in json.loads(get_ref):
            if 'default' in ref['_ref']:
                print(ref)
                if def_value==ref['max_udp_size']:          
                    if get_ref:
                         print("Success:check_UDP_buffer_size_attribute_present and test UDP buffer size 2000 for non default view")
                         print("Restart Services")
                         grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                         ref = json.loads(grid)[0]['_ref']
                         data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                         request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                         sleep(20)
                         assert True
                else:
                  
                    print("Failure: Check_UDP_buffer_size_attribute_present and test UDP buffer size 512 for non default view")
                    assert False
                
        print('------------Ipv4:LAN2-------------------')
        dig="dig @"+config.grid_master_lan2_v4+" c_rec.rfe_4795.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="UDP":
            assert True
        else:
            assert False
        print('-------------Ipv4:MGMT------------------')
        dig="dig @"+config.grid_master_mgmt+" d_rec.rfe_4795.com IN A +bufsize=1220" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
        else:
            assert False
        print('-------------Ipv6:LAN1------------------')
        dig="dig @"+config.grid_master_lan_v6+" a_rec.rfe_4795.com IN A +bufsize=512" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp_ipv6()
        if res3=="UDP":
            assert True
        else:
            assert False
            
        print('--------------Ipv6:LAN1----------------------------')
        dig="dig @"+config.grid_master_lan_v6+" b_rec.rfe_4795.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp_ipv6()
        if res2=="TCP":
            assert True
            
        else:
            assert False

    
        
    @pytest.mark.run(order=80)
    def test_079_performing_dig_query_from_different_interfaces_EDNS(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=edns_udp_size', grid_vip=config.grid_vip)
        print("\n")
        for ref in json.loads(get_ref):
            if 'default' in ref['_ref']:
                print(ref)
                data={'edns_udp_size':1220}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=edns_udp_size', grid_vip=config.grid_vip)
        
        def_value=1220
        for ref in json.loads(get_ref):
            if 'default' in ref['_ref']:
                print(ref)
                if def_value==ref['edns_udp_size']:          
                    if get_ref:
                         print("Success:check_EDNS_buffer_size_attribute_present and test EDNS buffer size 512 for non default view")
                         print("Restart Services")
                         grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                         ref = json.loads(grid)[0]['_ref']
                         data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                         request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data), grid_vip=config.grid_vip)
                         sleep(20)
                         assert True
                else:
                  
                    print("Failure: Check_EDNS_buffer_size_attribute_present and test EDNS buffer size 1220 for non default view")
                    assert False
        clear_DNS_cache()        
        print('------------Ipv4:LAN2-------------------')
        dig="dig @"+config.grid_master_lan2_v4+" o_rec.rfe_4795_edns.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="TCP":
            assert True
        else:
            assert False
        print('-------------Ipv4:MGMT------------------')
        dig="dig @"+config.grid_master_mgmt+" p_rec.rfe_4795_edns.com IN A +bufsize=1220" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
        else:
            assert False
        print('-------------Ipv6:LAN1------------------')
        dig="dig @"+config.grid_master_lan_v6+" m_rec.rfe_4795_edns.com IN A +bufsize=512" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp_ipv6()
        if res3=="UDP":
            assert True
        else:
            assert False
        print('-----------Ipv6:LAN2--------------------')
        dig="dig @"+config.grid_master_lan2_v6+" n_rec.rfe_4795_edns.com IN A +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp_ipv6()
        if res4=="UDP":
            assert True
        else:
            assert False   
        print('--------------Ipv6:MGMT-----------------')
        dig="dig @"+config.grid_master_mgmt_v6+" q_rec.rfe_4795_edns.com IN A +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp_ipv6()
        if res5=="TCP":
            assert True
        else:
            assert False
        
        print('--------------Ipv6:LAN1----------------------------')
        dig="dig @"+config.grid_master_lan_v6+" n_rec.rfe_4795_edns.com IN A +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp_ipv6()
        if res2=="TCP":
            assert True
            
        else:
            assert False

        clear_DNS_cache()
        
        print("EDNS buffer size setting to 512")
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=edns_udp_size', grid_vip=config.grid_vip)
        print("\n")
        for ref in json.loads(get_ref):
            if 'default' in ref['_ref']:
                print(ref)
                data={'edns_udp_size':512}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=edns_udp_size', grid_vip=config.grid_vip)
        
        def_value=512
        for ref in json.loads(get_ref):
            if 'default' in ref['_ref']:
                print(ref)
                if def_value==ref['edns_udp_size']:          
                    if get_ref:
                         print("Success:check_EDNS_buffer_size_attribute_present and test EDNS buffer size 512 for non default view")
                         print("Restart Services")
                         grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                         ref = json.loads(grid)[0]['_ref']
                         data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                         request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data), grid_vip=config.grid_vip)
                         sleep(20)
                         assert True
                else:
                  
                    print("Failure: Check_EDNS_buffer_size_attribute_present and test EDNS buffer size 512 for non default view")
                    assert False
                
        print('------------Ipv4:LAN2-------------------')
        dig="dig @"+config.grid_master_lan2_v4+" o_rec.rfe_4795_edns.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="TCP":
            assert True
        else:
            assert False
        print('-------------Ipv4:MGMT------------------')
        dig="dig @"+config.grid_master_mgmt+" p_rec.rfe_4795_edns.com IN A +bufsize=1220" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
        else:
            assert False
            
        clear_DNS_cache() 
        
        print("EDNS buffer size setting to 2000")
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=edns_udp_size', grid_vip=config.grid_vip)
        print("\n")
        for ref in json.loads(get_ref):
            if 'default' in ref['_ref']:
                print(ref)
                data={'edns_udp_size':2000}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=edns_udp_size', grid_vip=config.grid_vip)
        
        def_value=2000
        for ref in json.loads(get_ref):
            if 'default' in ref['_ref']:
                print(ref)
                if def_value==ref['edns_udp_size']:          
                    if get_ref:
                         print("Success:check_EDNS_buffer_size_attribute_present and test EDNS buffer size 512 for non default view")
                         print("Restart Services")
                         grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                         ref = json.loads(grid)[0]['_ref']
                         data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                         request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data), grid_vip=config.grid_vip)
                         sleep(20)
                         assert True
                else:
                  
                    print("Failure: Check_EDNS_buffer_size_attribute_present and test EDNS buffer size 512 for non default view")
                    assert False
                
        print('------------Ipv4:LAN2-------------------')
        dig="dig @"+config.grid_master_lan2_v4+" m_rec.rfe_4795_edns.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="UDP":
            assert True
        else:
            assert False
        print('-------------Ipv4:MGMT------------------')
        dig="dig @"+config.grid_master_mgmt+" p_rec.rfe_4795_edns.com IN A +bufsize=1220" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
        else:
            assert False

            
        clear_DNS_cache()
        
        print("EDNS buffer size setting to 4096")
           
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=edns_udp_size', grid_vip=config.grid_vip)
        print("\n")
        for ref in json.loads(get_ref):
            if 'default' in ref['_ref']:
                print(ref)
                data={'edns_udp_size':4096}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=edns_udp_size', grid_vip=config.grid_vip)
        
        def_value=4096
        for ref in json.loads(get_ref):
            if 'default' in ref['_ref']:
                print(ref)
                if def_value==ref['edns_udp_size']:          
                    if get_ref:
                         print("Success:check_EDNS_buffer_size_attribute_present and test EDNS buffer size 512 for non default view")
                         print("Restart Services")
                         grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                         ref = json.loads(grid)[0]['_ref']
                         data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                         request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data), grid_vip=config.grid_vip)
                         sleep(20)
                         assert True
                else:
                  
                    print("Failure: Check_EDNS_buffer_size_attribute_present and test EDNS buffer size 512 for non default view")
                    assert False
                
        print('------------Ipv4:LAN2-------------------')
        dig="dig @"+config.grid_master_lan2_v4+" m_rec.rfe_4795_edns.com IN A"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()
        if res1=="UDP":
            assert True
        else:
            assert False
        print('-------------Ipv4:MGMT------------------')
        dig="dig @"+config.grid_master_mgmt+" p_rec.rfe_4795_edns.com IN A +bufsize=1220" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
        else:
            assert False
        print('-------------Ipv6:LAN1------------------')
        dig="dig @"+config.grid_master_lan_v6+" m_rec.rfe_4795_edns.com IN A +bufsize=512" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp_ipv6()
        if res3=="UDP":
            assert True
        else:
           assert False

        clear_DNS_cache()
        
        
    @pytest.mark.run(order=81)
    def test_080_check_non_default_view_edns(self):        
        get_ref =  ib_NIOS.wapi_request('GET', object_type="member:dns?_return_fields=views", grid_vip=config.grid_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
                data = {"views": ["default","rfe_view"]}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response) 
        
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: Set a Views Assigned to This Member")
                        assert False
                else:
                    print("Success: Set a Views Assigned to This Member")
                    get_ref =  ib_NIOS.wapi_request('GET', object_type="member:dns?_return_fields=views" , grid_vip=config.grid_vip)
                    print(get_ref)          
                    print("Restart Services")
                    grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                    ref = json.loads(grid)[0]['_ref']
                    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data), grid_vip=config.grid_vip)
                    sleep(20)
                    assert True
                    
    @pytest.mark.run(order=82)
    def test_081_create_New_reverse_mapping_zone_in_grid1(self):
        print("Create test RMZ zone assigned to GM")
        data = {"fqdn": "14.0.0.0/8",   
                "view":"default",
                "zone_format":"IPV4",
                "grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create Authorative RMZ")
                assert False
                
        print("Restart DHCP Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)
                
    @pytest.mark.run(order=83)
    def test_082_create_a_ptr_record_with_different_size(self): 
        print("Creating a record ")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth?fqdn=14.0.0.0/8')
        print(get_ref)
        for i in range(1,15):
            for ref in json.loads(get_ref):
                data = {
                "name":"1.0.0.14.in-addr.arpa",
                "view":"default",
                "ptrdname": "a_ptr_rec"+str(i)}
                response = ib_NIOS.wapi_request('POST',object_type="record:ptr",fields=json.dumps(data))
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: Create A record in test zone")
                        assert False
                        
        for i in range(1,35):
            for ref in json.loads(get_ref):
          
                data = {
                "name":"2.0.0.14.in-addr.arpa",
                "view":"default",
                "ptrdname": "b_ptr_rec"+str(i)}
                response = ib_NIOS.wapi_request('POST',object_type="record:ptr",fields=json.dumps(data))
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: Create A record in test zone")
                        assert False
                            
        for i in range(1,85):
            for ref in json.loads(get_ref):
               
                data = {
                "name":"3.0.0.14.in-addr.arpa",
                "view":"default",
                "ptrdname": "c_ptr_rec"+str(i)}
                response = ib_NIOS.wapi_request('POST',object_type="record:ptr",fields=json.dumps(data))
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: Create A record in test zone")
                        assert False
                            
                            
                            
        for i in range(1,185):
            for ref in json.loads(get_ref):
            
                data = {
                "name":"4.0.0.14.in-addr.arpa",
                "view":"default",
                "ptrdname": "d_ptr_rec"+str(i)}
                response = ib_NIOS.wapi_request('POST',object_type="record:ptr",fields=json.dumps(data))
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: Create A record in test zone")
                        assert False
                        
                            
        for i in range(1,255):
            for ref in json.loads(get_ref):
           
                data = {
                "name":"5.0.0.14.in-addr.arpa",
                "view":"default",
                "ptrdname": "e_ptr_rec"+str(i)}
                response = ib_NIOS.wapi_request('POST',object_type="record:ptr",fields=json.dumps(data))
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: Create A record in test zone")
                        assert False
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)
        
    @pytest.mark.run(order=84)
    def test_083_check_UDP_buffer_size_attribute_and_test_default_value_RMZ(self):
        print("UDP buffer size setting to 1220")
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=max_udp_size')
        print(get_ref)
        for ref in json.loads(get_ref):
            data={'max_udp_size':1220}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
            print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=max_udp_size')
        print(get_ref)
        def_value=1220
        for ref in json.loads(get_ref):
            if def_value==ref['max_udp_size']:          
                if get_ref:
                     print("Success:check_UDP_buffer_size_attribute_present and test UDP buffer size is 1220")
                     print("Restart Services")
                     grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                     ref = json.loads(grid)[0]['_ref']
                     data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                     request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                     sleep(20)
                     assert True
            else:
              
                print("Failure: Check_UDP_buffer_size_attribute_present and test UDP buffer size is 1220")
                assert False
        
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 1.0.0.14.in-addr.arpa. IN PTR"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()   
        if res1=="UDP":
            assert True
        else:
            assert False
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 2.0.0.14.in-addr.arpa. IN PTR +bufsize=2000" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="UDP":
            assert True
        else:
            assert False
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 3.0.0.14.in-addr.arpa. IN PTR +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="TCP":
            assert True
        else:
            assert False
            
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 4.0.0.14.in-addr.arpa. IN PTR +bufsize=512" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="TCP":
            assert True
        else:
            assert False
            
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 5.0.0.14.in-addr.arpa. IN PTR +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        else:
            assert False
            
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 2.0.0.14.in-addr.arpa. IN PTR +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
        else:
            assert False  
           
        
        print("UDP buffer size setting to 512")
        
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=max_udp_size')
        print(get_ref)
        for ref in json.loads(get_ref):
            data={'max_udp_size':512}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
            print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=max_udp_size')
        print(get_ref)
        def_value=512
        for ref in json.loads(get_ref):
            if def_value==ref['max_udp_size']:          
                if get_ref:
                     print("Success:check_UDP_buffer_size_attribute_present and test UDP buffer size is 512")
                     print("Restart Services")
                     grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                     ref = json.loads(grid)[0]['_ref']
                     data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                     request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                     sleep(20)
                     assert True
            else:
              
                print("Failure: Check_UDP_buffer_size_attribute_present and test UDP buffer size is 512")
                assert False
        
     
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 1.0.0.14.in-addr.arpa. IN PTR"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()   
        if res1=="UDP":
            assert True
        else:
            assert False
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 2.0.0.14.in-addr.arpa. IN PTR +bufsize=2000" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
        else:
            assert False
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 3.0.0.14.in-addr.arpa. IN PTR +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="TCP":
            assert True
        else:
            assert False
            
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 4.0.0.14.in-addr.arpa. IN PTR +bufsize=512" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="TCP":
            assert True
        else:
            assert False
            
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 5.0.0.14.in-addr.arpa. IN PTR +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        else:
            assert False
            
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 2.0.0.14.in-addr.arpa. IN PTR +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
        else:
            assert False  
            
        print("UDP buffer size setting to 2000")
        
        print("-----Before modify------")
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=max_udp_size')
        print(get_ref)
        for ref in json.loads(get_ref):
            data={'max_udp_size':2000}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
            print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=max_udp_size')
        print(get_ref)
        def_value=2000
        for ref in json.loads(get_ref):
            if def_value==ref['max_udp_size']:          
                if get_ref:
                     print("Success:check_UDP_buffer_size_attribute_present and test UDP buffer size 2000")
                     print("Restart Services")
                     grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                     ref = json.loads(grid)[0]['_ref']
                     data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                     request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                     sleep(20)
                     assert True
            else:
              
                print("Failure: Check_UDP_buffer_size_attribute_present and test UDP buffer size 2000")
                assert False
        
    
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 1.0.0.14.in-addr.arpa. IN PTR"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()   
        if res1=="UDP":
            assert True
        else:
            assert False
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 2.0.0.14.in-addr.arpa. IN PTR +bufsize=2000" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="UDP":
            assert True
        else:
            assert False
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 3.0.0.14.in-addr.arpa. IN PTR +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="TCP":
            assert True
        else:
            assert False
            
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 4.0.0.14.in-addr.arpa. IN PTR +bufsize=512" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="TCP":
            assert True
        else:
            assert False
            
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 5.0.0.14.in-addr.arpa. IN PTR +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        else:
            assert False
            
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 2.0.0.14.in-addr.arpa. IN PTR +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
        else:
            assert False  
          
        print("UDP buffer size setting to 4096")
    
        print("-----Before modify------")
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=max_udp_size')
        print(get_ref)
        for ref in json.loads(get_ref):
            data={'max_udp_size':4096}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
            print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=max_udp_size')
        print(get_ref)
        def_value=4096
        for ref in json.loads(get_ref):
            if def_value==ref['max_udp_size']:          
                if get_ref:
                     print("Success:check_UDP_buffer_size_attribute_present and test UDP buffer size 4096")
                     print("Restart Services")
                     grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                     ref = json.loads(grid)[0]['_ref']
                     data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                     request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                     sleep(20)
                     assert True
            else:
              
                print("Failure: Check_UDP_buffer_size_attribute_present and test UDP buffer size 4096")
                assert False
        
   
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 1.0.0.14.in-addr.arpa. IN PTR"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()   
        if res1=="UDP":
            assert True
        else:
            assert False
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 2.0.0.14.in-addr.arpa. IN PTR +bufsize=2000" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="UDP":
            assert True
        else:
            assert False
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 3.0.0.14.in-addr.arpa. IN PTR +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="UDP":
            assert True
        else:
            assert False
            
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 4.0.0.14.in-addr.arpa. IN PTR +bufsize=512" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="TCP":
            assert True
        else:
            assert False
            
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 5.0.0.14.in-addr.arpa. IN PTR +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        else:
            assert False
            
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 2.0.0.14.in-addr.arpa. IN PTR +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
        else:
            assert False  
            
            
    @pytest.mark.run(order=85)
    def test_084_create_New_reverse_mapping_zone_in_grid2(self):
        print("Create test RMZ zone assigned to GM2")
        data = {"fqdn": "15.0.0.0/8",   
                "view":"default",
                "zone_format":"IPV4",
                "grid_primary": [{"name": config.grid2_fqdn,"stealth": False}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data), grid_vip=config.grid2_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create Authorative RMZ")
                assert False
                
        print("Restart DHCP Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid2_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid2_vip)
        sleep(20)
                
    @pytest.mark.run(order=86)
    def test_085_create_a_ptr_record_with_different_size_grid2(self): 
        print("Creating a PTR record in grid2")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth?fqdn=15.0.0.0/8', grid_vip=config.grid2_vip)
        print(get_ref)
        for i in range(1,15):
            for ref in json.loads(get_ref):
                data = {
                "name":"1.0.0.15.in-addr.arpa",
                "view":"default",
                "ptrdname": "m_ptr_rec"+str(i)}
                response = ib_NIOS.wapi_request('POST',object_type="record:ptr",fields=json.dumps(data), grid_vip=config.grid2_vip)
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: Create A record in test zone")
                        assert False
                        
        for i in range(1,35):
            for ref in json.loads(get_ref):
          
                data = {
                "name":"2.0.0.15.in-addr.arpa",
                "view":"default",
                "ptrdname": "n_ptr_rec"+str(i)}
                response = ib_NIOS.wapi_request('POST',object_type="record:ptr",fields=json.dumps(data), grid_vip=config.grid2_vip)
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: Create A record in test zone")
                        assert False
                            
        for i in range(1,85):
            for ref in json.loads(get_ref):
               
                data = {
                "name":"3.0.0.15.in-addr.arpa",
                "view":"default",
                "ptrdname": "o_ptr_rec"+str(i)}
                response = ib_NIOS.wapi_request('POST',object_type="record:ptr",fields=json.dumps(data), grid_vip=config.grid2_vip)
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: Create A record in test zone")
                        assert False
                            
                            
                            
        for i in range(1,185):
            for ref in json.loads(get_ref):
            
                data = {
                "name":"4.0.0.15.in-addr.arpa",
                "view":"default",
                "ptrdname": "p_ptr_rec"+str(i)}
                response = ib_NIOS.wapi_request('POST',object_type="record:ptr",fields=json.dumps(data), grid_vip=config.grid2_vip)
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: Create A record in test zone")
                        assert False
                        
                            
        for i in range(1,255):
            for ref in json.loads(get_ref):
           
                data = {
                "name":"5.0.0.15.in-addr.arpa",
                "view":"default",
                "ptrdname": "q_ptr_rec"+str(i)}
                response = ib_NIOS.wapi_request('POST',object_type="record:ptr",fields=json.dumps(data), grid_vip=config.grid2_vip)
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: Create A record in test zone")
                        assert False
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid2_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid2_vip)
        sleep(30)
        
        
        
    @pytest.mark.run(order=87)
    def test_086_check_EDNS_buffer_size_attribute_and_test_RMZ(self):
        print("Restarting DNS member of grid2")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns',grid_vip=config.grid2_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps({"enable_dns":True}),grid_vip=config.grid2_vip)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    assert False
            else:
                assert True
        
        
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns?_return_fields=max_udp_size',grid_vip=config.grid2_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            data={'max_udp_size':4096}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data),grid_vip=config.grid2_vip)
            print(response)
            print("Restart Services")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid2_vip)
            ref = json.loads(grid)[0]['_ref']
            data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid2_vip)
            sleep(20)
            assert True
        
        print("EDNS buffer size setting to 1220")
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=edns_udp_size', grid_vip=config.grid_vip)
        print("\n")
        for ref in json.loads(get_ref):
            if 'default' in ref['_ref']:
                print(ref)
                data={'edns_udp_size':1220}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=edns_udp_size', grid_vip=config.grid_vip)
        
        def_value=1220
        for ref in json.loads(get_ref):
            if 'default' in ref['_ref']:
                print(ref)
                if def_value==ref['edns_udp_size']:          
                    if get_ref:
                         print("Success:check_EDNS_buffer_size_attribute_present and test EDNS buffer size 1220 for default view")
                         print("Restart Services")
                         grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                         ref = json.loads(grid)[0]['_ref']
                         data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                         request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data), grid_vip=config.grid_vip)
                         sleep(20)
                         assert True
                else:
                  
                    print("Failure: Check_EDNS_buffer_size_attribute_present and test EDNS buffer size 1220 for default view")
                    assert False
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 1.0.0.15.in-addr.arpa. IN PTR"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()   
        if res1=="UDP":
            assert True
        else:
            assert False
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 2.0.0.15.in-addr.arpa. IN PTR +bufsize=2000" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="UDP":
            assert True
        else:
            assert False
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 3.0.0.15.in-addr.arpa. IN PTR +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="TCP":
            assert True
        else:
            assert False
            
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 4.0.0.15.in-addr.arpa. IN PTR +bufsize=512" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="TCP":
            assert True
        else:
            assert False
            
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 5.0.0.15.in-addr.arpa. IN PTR +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        else:
            assert False
            
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 2.0.0.15.in-addr.arpa. IN PTR +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
        else:
            assert False  
        clear_DNS_cache()
        
        print("EDNS buffer size setting to 4096")
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=edns_udp_size', grid_vip=config.grid_vip)
        print("\n")
        for ref in json.loads(get_ref):
            if 'default' in ref['_ref']:
                print(ref)
                data={'edns_udp_size':4096}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
        print("----After modify----")    
        get_ref = ib_NIOS.wapi_request('GET', object_type='view?_return_fields=edns_udp_size', grid_vip=config.grid_vip)
        
        def_value=4096
        for ref in json.loads(get_ref):
            if 'default' in ref['_ref']:
                print(ref)
                if def_value==ref['edns_udp_size']:          
                    if get_ref:
                         print("Success:check_EDNS_buffer_size_attribute_present and test EDNS buffer size 4096 for default view")
                         print("Restart Services")
                         grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                         ref = json.loads(grid)[0]['_ref']
                         data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                         request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data), grid_vip=config.grid_vip)
                         sleep(20)
                         assert True
                else:
                  
                    print("Failure: Check_EDNS_buffer_size_attribute_present and test EDNS buffer size 4096 for default view")
                    assert False

        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 1.0.0.15.in-addr.arpa. IN PTR"  
        perform_dig_cmd_tcpdump(dig)
        res1=validate_tcp_or_udp()   
        if res1=="UDP":
            assert True
        else:
            assert False
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 2.0.0.15.in-addr.arpa. IN PTR +bufsize=2000" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="UDP":
            assert True
        else:
            assert False
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 3.0.0.15.in-addr.arpa. IN PTR +bufsize=4096" 
        perform_dig_cmd_tcpdump(dig)        
        res3=validate_tcp_or_udp()
        if res3=="UDP":
            assert True
        else:
            assert False
            
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 4.0.0.15.in-addr.arpa. IN PTR +bufsize=512" 
        perform_dig_cmd_tcpdump(dig)        
        res4=validate_tcp_or_udp()
        if res4=="TCP":
            assert True
        else:
            assert False
            
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 5.0.0.15.in-addr.arpa. IN PTR +bufsize=5000"
        perform_dig_cmd_tcpdump(dig)        
        res5=validate_tcp_or_udp()
        if res5=="TCP":
            assert True
        else:
            assert False
            
        
        print('-------------------------------')
        dig="dig @"+config.grid_master_vip+" 2.0.0.15.in-addr.arpa. IN PTR +noedns" 
        perform_dig_cmd_tcpdump(dig)        
        res2=validate_tcp_or_udp()
        if res2=="TCP":
            assert True
        else:
            assert False  
            
        clear_DNS_cache()
        

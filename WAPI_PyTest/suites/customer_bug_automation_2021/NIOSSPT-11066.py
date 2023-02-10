#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Grid Master + M1                                                      #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415)                           #
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
#from ib_utils.start_stop_logs import log_action as log
#from ib_utils.file_content_validation import log_validation as logv
import subprocess

logging.basicConfig(filename='niosspt11066.log', filemode='w', level=logging.DEBUG)
count=[]

def kill_running_snmp_trap_id_from_client():
    print("\n============================================\n")
    print("Kill the snmp process running in client")
    print("\n============================================\n")
    sleep(05)
    cmd=('sshpass -p "infoblox" ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@%s' % (config.client_ip))
    cmd = shlex.split(cmd)
    cmd.append('pkill snmptrapd')
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    output = process.communicate()
    print("done")
    sleep(3)

def check_able_to_login_appliances(ip,unit):
    
    for i in range(5):
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+ip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.close()
            print("\n************Appliances is Working************\n ")
            sleep(120)
            assert True
            break
            
        except Exception as e:
            child.close()
            print(e)
            sleep(60)
            #continue
            if i == 2:
                os.system("reboot_system -H "+unit)
                
            continue
            print("Failure: Appliances did not comeup(vm didn't comeup)")
            
            assert False

def GMC_promote_member_as_master_candidate():    
    print("DNS Restart Services")
    sleep(30)
    grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
    ref = json.loads(grid)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
    sleep(30)
    get_ref = ib_NIOS.wapi_request('GET', object_type="member?_return_fields=master_candidate", grid_vip=config.grid_vip)
    print(get_ref)
    
    for ref in json.loads(get_ref):
        if config.grid_member1_fqdn in ref['_ref']:
            data = {"master_candidate": True}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            print(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    print("Failure: Can't set master candidate to true for member")
                    assert False
            else:
                print("Success: set master candidate to true for member")
                assert True
        
    check_able_to_login_appliances(config.grid_vip,config.master_vmid)  
    sleep(40) 
    child1 = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
    try:
        child1.logfile=sys.stdout
        child1.expect('password:')
        child1.sendline('infoblox')
        child1.expect('Infoblox >')
        child1.sendline('set promote_master')
        child1.expect('y or n')
        child1.sendline('y')
        child1.expect('Default: 30s')
        child1.sendline('\n')
        child1.expect('y or n')
        
        child1.sendline('y\n')
        
        child1.expect('y or n')
        child1.sendline('y\n')
        
        child1.expect('y or n')
        child1.sendline('y\n')
           
    except Exception as e:
        child1.close()
        print("Failure: Can't promote GMC master as master candidate")
        print("\n================Errorrr====================\n")
        print(e)
        assert False
    for i in range(5):
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.send('show status')
            child.expect('>')
            if 'Grid Member' in child.before:
                child.close()
                print("\n************Grid member is promoted as a Grid master************\n ")
                sleep(60)
                assert True
                break
            else:
                
                raise(Exception)
            
        except Exception as e:
            child.close()
            print(e)
            
            sleep(20)
            continue
            print("Failure")
        
            assert False
  
    return "executed"

def track_snmp_traps():
     
    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.client_ip)
    try:
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('#')
        child.sendline('snmptrapd udp6:162,udp:162 -f -C -c /etc/snmp/snmptrapd.conf -Le &> trap_snmp.txt\n')
        get_ref = ib_NIOS.wapi_request('GET', object_type="member?_return_fields=ntp_setting", grid_vip=config.grid_vip)
        
        for ref in json.loads(get_ref):
            
            data= {"ntp_setting": {
                "enable_external_ntp_servers": False,
                "enable_ntp": True,
                "exclude_grid_master_ntp_server": False,
                "ntp_acl": {
                    "ac_list": [],
                    "acl_type": "NONE",
                    "service": "TIME"
                },
                "ntp_keys": [],
                "ntp_kod": False,
                "ntp_servers": [],
                "use_ntp_acl": False,
                "use_ntp_keys": False,
                "use_ntp_kod": False,
                "use_ntp_servers": False
            }}

            response = ib_NIOS.wapi_request('PUT',ref=ref['_ref'],fields=json.dumps(data), grid_vip=config.grid_vip)
            print(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    print("Failure: Enable NTP services")
                    assert False
                else:
                    print("Success: Enable NTP services")
                    assert True
         
        print("Reboot the Master")
        child1 = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child1.logfile=sys.stdout
        child1.expect('password:')
        child1.sendline('infoblox')
        child1.expect('Infoblox >')
        child1.sendline('reboot')
        child1.expect('y or n')
        child1.sendline('y')
        sleep(60)
        check_able_to_login_appliances(config.grid_vip,config.master_vmid)
        sleep(60)
        child1.close()
        res=GMC_promote_member_as_master_candidate()
        print("Reboot the Master")
        child1 = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child1.logfile=sys.stdout
        child1.expect('password:')
        child1.sendline('infoblox')
        child1.expect('Infoblox >')
        child1.sendline('reboot')
        child1.expect('y or n')
        child1.sendline('y')
        sleep(60)
        child1.close()
        check_able_to_login_appliances(config.grid_member1_vip,config.member_vmid)
        print("Reboot the Member")
        child1 = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child1.logfile=sys.stdout
        child1.expect('password:')
        child1.sendline('infoblox')
        child1.expect('Infoblox >')
        child1.sendline('reboot')
        child1.expect('y or n')
        child1.sendline('y')
        sleep(60)
        check_able_to_login_appliances(config.grid_vip,config.master_vmid)
        child1.close()
        child.sendcontrol('z')
        print("consol z")
        child.expect('#')
        
       
        child.close()
    except Exception as e:
        child.close()
        print("Failure:")
        print(e)
        assert False
    flag=0 
    
    child=pexpect.spawn("ssh root@"+config.grid_member1_vip,  maxread=4000)

    try:
        child.expect("-bash-4.0#",timeout=100)
        child.sendline("scp -pr root@"+config.client_ip+":/root/trap_snmp.txt /root")
        child.expect("Are you sure you want to continue connecting (yes/no)?")
        child.sendline("yes") 
        child.expect('password:',timeout=100)
        child.sendline("infoblox")
        
        child.expect("-bash-4.0#")
        child.sendline("exit")
        print("\nSuccess: Copy the original file into member root directory")
        child.close()
        assert True

    except Exception as e:
        child.close()
        print (e)
        print("Failure: Copy the original file into member root directory")
        assert False

    search_txt=[config.grid_vip+".*grid member is not connected to the grid master",config.grid_vip+".*grid member is connected to the grid master",config.grid_vip+".*NTP Service is working",config.grid_member1_vip+".*grid member is not connected to the grid master",config.grid_member1_vip+".*NTP Service is working"]
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(config.grid_member1_vip, username='root', pkey = mykey)
    
   
    print("--------------copied------------------------------")
    data="ls\n"
    stdin, stdout, stderr = client.exec_command(data)
    
    print(stdout.readlines())
    data="cat /root/trap_snmp.txt\n"
    stdin, stdout, stderr = client.exec_command(data)
    stdout=stdout.readlines()
    print(stdout)
    print("--------============================================-----------")   
    New_list=[]
    '''
    for search_s in search_txt:
        for line in stdout:
            if re.search(search_s, line):
                New_list.append(line)
                print("Match found")
                flag=flag+1
                print(search_s)
                print("****************************************************")
                print(line)

    '''
    for line in stdout:
        for search_s in search_txt:
            
            if re.search(search_s, line):

                New_list.append(line)
                flag=flag+1
                #assert True
            else:
                #print("Match not found")
                flag=flag+0
    if flag==0:
        assert False
    else:
        print("Success: All traps which are looking for is present")
        assert True
        
    client.close()   
    
class NIOSSPT_11066(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_enable_snmp_in_the_grid(self):
        kill_running_snmp_trap_id_from_client()
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting', grid_vip=config.grid_vip)
        
        print(get_ref)
        for ref in json.loads(get_ref):
            data={"snmp_setting":{"queries_enable":True,"queries_community_string":"public","trap_receivers":[{"address": config.client_ip}],"traps_community_string":"public","traps_enable":True}}   
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            print(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401 or response[0]==404:
                    print("Failure: Enable SNMP in the grid")
                    assert False
            else:
                print("Success: Enable SNMP in the grid")
                assert True
                
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting', grid_vip=config.grid_vip)
        print(get_ref)
    @pytest.mark.run(order=2)
    def test_001_start_NTP_service(self):
        print("Enable the NTP service")
        
        track_snmp_traps()
            
    @pytest.mark.run(order=5)
    def test_cleanup(self):
                           
        child1 = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        try:
            child1.logfile=sys.stdout
            child1.expect('password:')
            child1.sendline('infoblox')
            child1.expect('Infoblox >')
            child1.sendline('set promote_master')
            child1.expect('y or n')
            child1.sendline('y')
            child1.expect('Default: 30s')
            child1.sendline('\n')
            child1.expect('y or n')
            
            child1.sendline('y\n')
            
            child1.expect('y or n')
            child1.sendline('y\n')
            
            child1.expect('y or n')
            child1.sendline('y\n')
            check_able_to_login_appliances(config.grid_vip,config.master_vmid)  
            child1.close()
            assert True
            
            
        except Exception as e:
            child1.close()
            print("Failure: Can't promote GMC Master as master candidate")
            print(e)
            assert False
            
        check_able_to_login_appliances(config.grid_vip,config.master_vmid)
        
        print("Disable the SNMP traps")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting', grid_vip=config.grid_vip)
        
        print(get_ref)
        for ref in json.loads(get_ref):
            data={"snmp_setting":{"queries_enable":False,"queries_community_string":"","trap_receivers":[],"traps_community_string":"","traps_enable":False}}   
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            print(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401 or response[0]==404:
                    print("Success: Disable the SNMP traps")
                    assert True
                else:
                    print("Failure: Disable the SNMP traps")
                    assert False
                    
                    
        print("Disable the NTP service")
        #track_snmp_traps()
        get_ref = ib_NIOS.wapi_request('GET', object_type="member?_return_fields=ntp_setting", grid_vip=config.grid_vip)
        
        for ref in json.loads(get_ref):
            
            data= {"ntp_setting": {
                "enable_external_ntp_servers": False,
                "enable_ntp": False,
                "exclude_grid_master_ntp_server": False,
                "ntp_acl": {
                    "ac_list": [],
                    "acl_type": "NONE",
                    "service": "TIME"
                },
                "ntp_keys": [],
                "ntp_kod": False,
                "ntp_servers": [],
                "use_ntp_acl": False,
                "use_ntp_keys": False,
                "use_ntp_kod": False,
                "use_ntp_servers": False
            }}

            response = ib_NIOS.wapi_request('PUT',ref=ref['_ref'],fields=json.dumps(data), grid_vip=config.grid_vip)
            print(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    print("Failure: Disable NTP services")
                    assert False
                else:
                    print("Success: Disable NTP services")
                    assert True 
                    
 

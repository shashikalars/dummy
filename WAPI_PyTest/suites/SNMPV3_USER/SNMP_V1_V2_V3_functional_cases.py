#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
# Grid Set up required:                                                     #
#  1. Flex Grid                                                             #
#  2. Licenses : FLEX LICENSE                                               #
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
import sys
import commands

def restart_services():
    print("Restart DNS Services")
    grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
    ref = json.loads(grid)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","services": "ALL"}
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
    sleep(30)

def perform_snmpwalk_command(IP,grep_variable):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(config.grid_vip, username='root', pkey = mykey)
    sleep(20)
    data='snmpwalk -v 2c -c public -m ALL '+IP+' infoblox |grep "'+grep_variable+'"'
    stdin, stdout, stderr = client.exec_command(data)
    sleep(2)
    stdout=stdout.read()
    stderr=stderr.read()
    print(data,stdout,stderr)
    
    return client,stdout,stderr 
          
def perform_snmp_command_on_v1(snmp_cmd,IP,grep_variable):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(config.grid_vip, username='root', pkey = mykey)
    sleep(20)
    data=snmp_cmd+' -v 1 -c public '+IP+' '+grep_variable
    stdin, stdout, stderr = client.exec_command(data)
    sleep(2)
    stdout=stdout.read()
    stderr=stderr.read()
    print(data,stdout,stderr)
    
    return client,stdout,stderr  
		
def perform_snmp_command_on_v2(snmp_cmd,IP,grep_variable):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(config.grid_vip, username='root', pkey = mykey)
    sleep(20)
    data=snmp_cmd+' -v 2c -c public '+IP+' '+grep_variable
    stdin, stdout, stderr = client.exec_command(data)
    sleep(2)
    stdout=stdout.read()
    stderr=stderr.read()
    print(data,stdout,stderr)
    
    return client,stdout,stderr 
    
def perform_snmp_command_on_v3(snmp_cmd,IP,grep_variable):
    getref = ib_NIOS.wapi_request('GET',object_type="snmpuser")
    snmpuser_name = json.loads(getref)[0]["name"]
        
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(config.grid_vip, username='root', pkey = mykey)
    sleep(20)
    data=snmp_cmd+' -v 3 '+IP+' '+grep_variable+' -l authPriv -a SHA -A infoblox1 -x AES -X infoblox1 -u '+snmpuser_name
    stdin, stdout, stderr = client.exec_command(data)
    sleep(2)
    stdout=stdout.read()
    stderr=stderr.read()
    print(data,stdout,stderr)
    
    return client,stdout,stderr 
 
def validate_snmp_command_on_v1(stdout_v1,string_v,SNMP_cmd,client,GM_M):
    if string_v in stdout_v1:
        print("\nSuccess : "+SNMP_cmd+" command worked on snmpv1 with "+GM_M+"/n")
        client.close()
        assert True
    else:
        client.close()
        print("Failure: "+SNMP_cmd+" command did not worked on snmpv1 with "+GM_M+"\n\n")
        assert False
        
def validate_snmp_command_on_v2(stdout_v2,string_v,SNMP_cmd,client,GM_M):
    if string_v in stdout_v2:
        print("\nSuccess : "+SNMP_cmd+" command  worked on snmpv2 with "+GM_M+"/n")
        client.close()
        assert True
    else:
        client.close()
        print("Failure: "+SNMP_cmd+" command did not worked on snmpv2 with "+GM_M+"\n\n")
        assert False
        
def validate_snmp_command_on_v3(stdout_v3,string_v,SNMP_cmd,client,GM_M):
    if string_v in stdout_v3:
        print("\nSuccess : "+SNMP_cmd+" command worked on snmpv3 with "+GM_M+"/n")
        client.close()
        assert True
    else:
        client.close()
        print("Failure: "+SNMP_cmd+" command did not worked on snmpv3 with "+GM_M+"\n\n")
        assert False
        
def perform_cli_commands_on_snmp(IP,snmp_set_cmd):
    output=''
    child1 = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+IP)
    try:
        child1.logfile=sys.stdout
        child1.expect('password:')
        child1.sendline('infoblox')
        child1.expect('Infoblox >')
        child1.sendline(snmp_set_cmd)
        child1.expect('Infoblox >')
        
        output= child1.before
        child1.close()
    except Exception as e:
        child1.close()
        print("\n Failure: error in executing snmp comand")
        print("\n================Error====================\n")
        print(e)
        assert False        
           
    print(output)
    return output
    
def check_able_to_login_appliances(ip):

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
            sleep(120)
            continue
            
            print("Failure: Appliances did not comeup(vm didn't comeup)")

            assert False

def start_services(obj,service_type,name_ser):
    get_ref = ib_NIOS.wapi_request('GET', object_type=obj)
    print(get_ref)
    for ref in json.loads(get_ref):
        data = {service_type: True}
        response = ib_NIOS.wapi_request('PUT', ref=ref["_ref"], fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:
                print("\n Success: Start "+name_ser+" services")
                assert True
            else:
                print("\n Failure: did not Start "+name_ser+" services")
                assert False
				
def stop_services(obj,service_type,name_ser):
    get_ref = ib_NIOS.wapi_request('GET', object_type=obj)
    print(get_ref)
  
    for ref in json.loads(get_ref):
        data = {service_type: False}
        response = ib_NIOS.wapi_request('PUT', ref=ref["_ref"], fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:
                print("\n Success: Start "+name_ser+" services")
                assert True
            else:
                print("\n Failure: did not Start "+name_ser+" services")
                assert False
 
def Having_No_Authentication_Password_and_No_Privacy_Password(snmp_cmd,IP,grep_variable):
    getref = ib_NIOS.wapi_request('GET',object_type="snmpuser")
    #snmpuser_name = json.loads(getref)[0]["name"]
    snmpuser_name=''
    for ref in json.loads(getref):
        if 'snmpUser1' in ref['name']:
            snmpuser_name=ref['name']
            
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(config.grid_vip, username='root', pkey = mykey)
    sleep(20)
    data=snmp_cmd+' -v 3 -u '+snmpuser_name+' -m all -l noAuthNoPriv '+IP+' '+grep_variable
    stdin, stdout, stderr = client.exec_command(data)
    sleep(2)
    stdout=stdout.read()
    stderr=stderr.read()
    print(data,stdout,stderr)
    
    return client,stdout,stderr 

def Having_Authentication_Password_No_Privacy_Password(snmp_cmd,IP,grep_variable):
    getref = ib_NIOS.wapi_request('GET',object_type="snmpuser")
    #snmpuser_name = json.loads(getref)[0]["name"]
    snmpuser_name=''
    for ref in json.loads(getref):
        if 'snmpUser2' in ref['name']:
            snmpuser_name=ref['name']
            
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(config.grid_vip, username='root', pkey = mykey)
    sleep(20)
    data=snmp_cmd+' -v 3 -u '+snmpuser_name+' -m all -l authNoPriv -a MD5 -A infoblox1 '+IP+' '+grep_variable
    stdin, stdout, stderr = client.exec_command(data)
    sleep(2)
    stdout=stdout.read()
    stderr=stderr.read()
    print(data,stdout,stderr)
    
    return client,stdout,stderr 
    
def Having_Authentication_Password_Privacy_Password(snmp_cmd,IP,grep_variable):
    getref = ib_NIOS.wapi_request('GET',object_type="snmpuser")
    #snmpuser_name = json.loads(getref)[0]["name"]
    snmpuser_name=''
    for ref in json.loads(getref):
        if 'snmpUser3' in ref['name']:
            snmpuser_name=ref['name']
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(config.grid_vip, username='root', pkey = mykey)
    sleep(20)
    data=snmp_cmd+' -v 3 -u '+snmpuser_name+' -m all -l authPriv -a MD5 -A infoblox1 -x DES -X infoblox1 '+IP+' '+grep_variable
    stdin, stdout, stderr = client.exec_command(data)
    sleep(2)
    stdout=stdout.read()
    stderr=stderr.read()
    print(data,stdout,stderr)
    
    return client,stdout,stderr 
    
def track_snmp_traps(trap_server,trapcmd,filename):
    
    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+trap_server)
    print(trap_server)
    try:
        child.expect('password:')
        
        child.sendline('infoblox')
        child.expect('$')

        sleep(2)
        child.logfile=sys.stdout
        
        child.sendline('killall snmptrapd')
 
        child.expect('$')
        child.sendline(trapcmd+' &> '+filename)
        #child.sendline('snmptrapd -f -C -c /etc/snmp/snmptrapd.conf -Le &> trap_snmp1.txt')
        ref= ib_NIOS.wapi_request('GET', object_type="grid",params="?_return_fields=trap_notifications", grid_vip=config.grid_vip)
        ref= json.loads(ref)
        grid_ref=ref[0]['_ref']

        data = {"trap_notifications": [{"enable_email": False,"enable_trap": True,"trap_type": "AnalyticsRPZ"},{"enable_email": False,"enable_trap": True,"trap_type": "AutomatedTrafficCapture"},{"enable_email": False,"enable_trap": True,"trap_type": "BFD"},{"enable_email": False,"enable_trap": True,"trap_type": "BGP"},{"enable_email": False,"enable_trap": True,"trap_type": "Backup"},{"enable_email": False,"enable_trap": True,"trap_type": "CPU"},{"enable_email": False,"enable_trap": True,"trap_type": "CaptivePortal"},{"enable_email": False,"enable_trap": True,"trap_type": "CiscoISEServer"},{"enable_email": False,"enable_trap": True,"trap_type": "Clear"},{"enable_email": False,"enable_trap": True,"trap_type": "CloudAPI"},{"enable_email": False,"enable_trap": True,"trap_type": "Cluster"},{"enable_email": False,"enable_trap": True,"trap_type": "Controld"},{"enable_email": False,"enable_trap": True,"trap_type": "DHCP"},{"enable_email": False,"enable_trap": True,"trap_type": "DNS"},{"enable_email": False,"enable_trap": True,"trap_type": "DNSAttack"},{"enable_email": False,"enable_trap": True,"trap_type": "DNSIntegrityCheck"},{"enable_email": False,"enable_trap": True,"trap_type": "DNSIntegrityCheckConnection"},{"enable_email": False,"enable_trap": True,"trap_type": "Database"},{"enable_email": False,"enable_trap": True,"trap_type": "DisconnectedGrid"},{"enable_email": False,"enable_trap": True,"trap_type": "Discovery"},{"enable_email": False,"enable_trap": True,"trap_type": "DiscoveryConflict"},{"enable_email": False,"enable_trap": True,"trap_type": "DiscoveryUnmanaged"},{"enable_email": False,"enable_trap": True,"trap_type": "Disk"},{"enable_email": False,"enable_trap": True,"trap_type": "DuplicateIP"},{"enable_email": False,"enable_trap": True,"trap_type": "ENAT"},{"enable_email": False,"enable_trap": True,"trap_type": "FDUsage"},{"enable_email": False,"enable_trap": True,"trap_type": "FTP"},{"enable_email": False,"enable_trap": True,"trap_type": "Fan"},{"enable_email": False,"enable_trap": True,"trap_type": "HA"},{"enable_email": False,"enable_trap": True,"trap_type": "HSM"},{"enable_email": False,"enable_trap": True,"trap_type": "HTTP"},{"enable_email": False,"enable_trap": True,"trap_type": "IFMAP"},{"enable_email": False,"enable_trap": True,"trap_type": "IMC"},{"enable_email": False,"enable_trap": True,"trap_type": "IPAMUtilization"},{"enable_email": False,"enable_trap": True,"trap_type": "IPMIDevice"},{"enable_email": False,"enable_trap": True,"trap_type": "LCD"},{"enable_email": False,"enable_trap": True,"trap_type": "LDAPServers"},{"enable_email": False,"enable_trap": True,"trap_type": "License"},{"enable_email": False,"enable_trap": True,"trap_type": "Login"},{"enable_email": False,"enable_trap": True,"trap_type": "MGM"},{"enable_email": False,"enable_trap": True,"trap_type": "MSServer"},{"enable_email": False,"enable_trap": True,"trap_type": "Memory"},{"enable_email": False,"enable_trap": True,"trap_type": "NTP"},{"enable_email": False,"enable_trap": True,"trap_type": "Network"},{"enable_email": False,"enable_trap": True,"trap_type": "OCSPResponders"},{"enable_email": False,"enable_trap": True,"trap_type": "OSPF"},{"enable_email": False,"enable_trap": True,"trap_type": "OSPF6"},{"enable_email": False,"enable_trap": True,"trap_type": "Outbound"},{"enable_email": False,"enable_trap": True,"trap_type": "PowerSupply"},{"enable_email": False,"enable_trap": True,"trap_type": "RAID"},{"enable_email": False,"enable_trap": True,"trap_type": "RIRSWIP"},{"enable_email": False,"enable_trap": True,"trap_type": "RPZHitRate"},{"enable_email": False,"enable_trap": True,"trap_type": "RecursiveClients"},{"enable_email": False,"enable_trap": True,"trap_type": "Reporting"},{"enable_email": False,"enable_trap": True,"trap_type": "RootFS"},{"enable_email": False,"enable_trap": True,"trap_type": "SNMP"},{"enable_email": False,"enable_trap": True,"trap_type": "SSH"},{"enable_email": False,"enable_trap": True,"trap_type": "SerialConsole"},{"enable_email": False,"enable_trap": True,"trap_type": "SwapUsage"},{"enable_email": False,"enable_trap": True,"trap_type": "Syslog"},{"enable_email": False,"enable_trap": True,"trap_type": "System"},{"enable_email": False,"enable_trap": True,"trap_type": "TFTP"},{"enable_email": False,"enable_trap": True,"trap_type": "Taxii"},{"enable_email": False,"enable_trap": True,"trap_type": "ThreatAnalytics"},{"enable_email": False,"enable_trap": True,"trap_type": "ThreatProtection"}]}
        response= ib_NIOS.wapi_request('PUT', ref=grid_ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==200:
                print("\n Success: Configure snmp notification")
                assert True
            else:
                print("\n Failure: can't Configure snmp notification")
                assert False
				
        print("\n============================================\n")
        print("Start DNS services")
        print("\n============================================\n")
        start_services("member:dns","enable_dns","DNS")
        sleep(30)
        print("\n============================================\n")
        print("Stop DNS services")
        print("\n============================================\n")
        stop_services("member:dns","enable_dns","DNS")
        sleep(30)
        print("\n============================================\n")
        print("Start DHCP services")
        print("\n============================================\n")
        start_services("member:dhcpproperties","enable_dhcp","DHCP")
        
        sleep(30)
        print("\n============================================\n")
        print("Stop DHCP services")
        print("\n============================================\n")
        stop_services("member:dhcpproperties","enable_dhcp","DHCP")
      
        sleep(60)
        print("\n============================================\n")
        print("Start FTP services")
        print("\n============================================\n")
        start_services("member:filedistribution","enable_ftp","FTP")
        
        sleep(60)
        print("\n============================================\n")
        print("Start TFTP services")
        print("\n============================================\n")
        start_services("member:filedistribution","enable_tftp","TFTP")
        
        sleep(30)
        print("\n============================================\n")
        print("Start HTTP services")
        print("\n============================================\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:filedistribution")
        start_services("member:filedistribution","enable_http","HTTP")
        
        sleep(30)
        print("\n============================================\n")
        print("Stop FTP services")
        print("\n============================================\n")
        stop_services("member:filedistribution","enable_ftp","FTP")
        
        sleep(30)
        
        print("\n============================================\n")
        print("Stop TFTP services")
        print("\n============================================\n")
        stop_services("member:filedistribution","enable_tftp","TFTP")
        
        sleep(30)
        print("\n============================================\n")
        print("Stop HTTP services")
        print("\n============================================\n")
        stop_services("member:filedistribution","enable_http","HTTP")
        
        sleep(60)
        print("\n============================================\n")
        print("Reboot the system")
        print("\n============================================\n")
        child1 = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child1.logfile=sys.stdout
        child1.expect('password:')
        child1.sendline('infoblox')
        child1.expect('Infoblox >')
        child1.sendline('reboot')
        child1.expect('y or n')
        child1.sendline('y')
        sleep(120)
        check_able_to_login_appliances(config.grid_vip)
        sleep(60)
        child1.close()

        
        child.sendcontrol('z')
        print("consol z")
        child.expect('$')
        child.close()
    except Exception as e:
        child.close()
        print("Failure: to Fetch the traps")
        print(e)
        assert False
    sleep(60)
    child=pexpect.spawn("ssh root@"+config.grid_vip,  maxread=4000)
    try:
        child.expect("#",timeout=100)
        child.sendline("scp -o StrictHostKeyChecking=no -pr root@"+config.trap_receiver_ip+":/root/"+filename+" /root")
        child.expect('password:',timeout=200)
        child.sendline("infoblox")
        child.expect("#")
        print(config.grid_vip)
        child.sendline("exit")
        print("\nSuccess: Copy the original file into master root directory")
        child.close()
        assert True

    except Exception as e:
        child.close()
        print (e)
        print("Failure: can't Copy the original file into master root directory")
        assert False
    sleep(20)
    flag=0
    
    search_txt=[trap_server,config.grid_vip,config.grid_member1_vip,"DNS Service is working","DHCP Service is working","DHCP Service is inactive","FTP Service is working","FTP Service is inactive","TFTP Service is working","TFTP Service is inactive","HTTP Service is working","HTTP Service is inactive","The system is rebooting","NTP Service is inactive","LDAP service is inactive","DoT/DoH is Inactive"]

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(config.grid_vip, username='root', pkey = mykey)
    print("--------------copied------------------------------")
    
    data="cat /root/"+filename+"\n"
    stdin, stdout, stderr = client.exec_command(data)
    stdout=stdout.readlines()
    print(stdout)
    print("--------============================================-----------")
    New_list=[]
    New_list_not_p=[]
    for line in stdout:
        for search_s in search_txt:
            if re.search(search_s, line):
                New_list.append(search_s)
                flag=flag+1 
            else:
                New_list_not_p.append(search_s)
                flag=flag+0
                
    print("\n Trap which is present below:\n")
    print(set(New_list))
            
    if flag==0:
        print("Failure: All traps which are looking for is not present")
        assert False       
    else:
       print("Success: All traps which are looking for is present\n")
       assert True

    client.close()

def enable_SNMPV3_trap(node_memref):
    response = ib_NIOS.wapi_request('GET',object_type="snmpuser")
    snmp_memref = json.loads(response)[0]['_ref']
    snmp_memref = snmp_memref.encode('ascii', 'ignore')
    print(snmp_memref)
    
    data={"use_snmp_setting":True,"snmp_setting":{"snmpv3_traps_enable": True,"trap_receivers":[{"address": config.client_ip,"user":snmp_memref}]}}
    
    response=ib_NIOS.wapi_request('PUT',ref=node_memref, fields=json.dumps(data))
    print(response)
    if type(response) == tuple:

        if response[0]==200:
            print("\n Success: Enable SNMP configuration on member level")
            assert False
        else:
            print("Failure: Enable SNMP configuration on member level")
            assert True

def disable_SNMPV3_trap(node_memref):
    response = ib_NIOS.wapi_request('GET',object_type="snmpuser")
    snmp_memref = json.loads(response)[0]['_ref']
    snmp_memref = snmp_memref.encode('ascii', 'ignore')
    print(snmp_memref)
    
    data={"use_snmp_setting":True,"snmp_setting":{"snmpv3_traps_enable": False,"trap_receivers":[{"address": config.client_ip,"user":snmp_memref}]}}
    
    response=ib_NIOS.wapi_request('PUT',ref=node_memref, fields=json.dumps(data))
    print(response)
    if type(response) == tuple:

        if response[0]==200:
            print("\n Success: Enable SNMP configuration on member level")
            assert False
        else:
            print("Failure: Enable SNMP configuration on member level")
            assert True
            
            
def get_engineboot_value(IP):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(IP, username='root', pkey = mykey)
    sleep(2)
    data="tail -5 /var/lib/net-snmp/snmpd.conf"
    stdin, stdout, stderr = client.exec_command(data)
    sleep(2)
    stdout=stdout.readlines()
    stderr=stderr.read()
    print(data,stdout,stderr)
    eng_value=stdout[3].split()[1]
    print(eng_value)
    eng_ID=stdout[4].split()[1]
    print (eng_ID)
    client.close()
    return eng_value
    
    
def engineboot_increment_by_1(IP,e_VLU):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(IP, username='root', pkey = mykey)
    sleep(2)
    data="tail -5 /var/lib/net-snmp/snmpd.conf"
    stdin, stdout, stderr = client.exec_command(data)
    sleep(2)
    stdout=stdout.readlines()
    stderr=stderr.read()
    print(data,stdout,stderr)
    eng_value=stdout[3].split()[1]
    eng_value = eng_value.encode('ascii', 'ignore')
    e_VLU = e_VLU.encode('ascii', 'ignore')
    print(eng_value)
    
    res=int(eng_value)-int(e_VLU)
    print(res)
    client.close()
    if res==1:
        print("\n Success: The engine boots incremented by 1")
        assert True
    else:
        print("Failure: The engine boots did not incremented by 1")
        assert False

def engineboot_increment_by_2(IP,e_VLU):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(IP, username='root', pkey = mykey)
    sleep(2)
    data="tail -5 /var/lib/net-snmp/snmpd.conf"
    stdin, stdout, stderr = client.exec_command(data)
    sleep(2)
    stdout=stdout.readlines()
    stderr=stderr.read()
    print(data,stdout,stderr)
    eng_value=stdout[3].split()[1]

    eng_value = eng_value.encode('ascii', 'ignore')
    e_VLU = e_VLU.encode('ascii', 'ignore')
    
    print(eng_value)
    res=int(eng_value)-int(e_VLU)
    print(res)
    client.close()
    if res==2:
        print("\n Success: The engine boots incremented by 2")
        assert True
    else:
        print("Failure: The engine boots value is not 2.")
        assert False
  
def check_engineboot_has_been_incremented(IP,e_VLU):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(IP, username='root', pkey = mykey)
    sleep(2)
    data="tail -5 /var/lib/net-snmp/snmpd.conf"
    stdin, stdout, stderr = client.exec_command(data)
    sleep(2)
    stdout=stdout.readlines()
    stderr=stderr.read()
    print(data,stdout,stderr)
    eng_value=stdout[3].split()[1]

    eng_value = eng_value.encode('ascii', 'ignore')
    e_VLU = e_VLU.encode('ascii', 'ignore')
    client.close()
    print(eng_value)
    # res=int(eng_value)-int(e_VLU)
    # print(res)
    if eng_value==e_VLU:
        print("Failure: The engine boots value is not incremented")
        assert False
    else:
        print("\n Success: The engine boots value is incremented")
        assert True
        

def reboot_node(IP):
    print("start rebooting "+str(IP))
    try:
        child1 = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+IP)
        child1.logfile=sys.stdout
        child1.expect('password:')
        child1.sendline('infoblox')
        child1.expect('Infoblox >')
        child1.sendline('reboot')
        child1.expect('y or n')
        child1.sendline('y')
        sleep(60)
        check_able_to_login_appliances(IP)
        sleep(30)
        child1.close()
    except Exception as e:
        child1.close()
        print("\n Failure: error in rebooting")
        print("\n================Error====================\n")
        print(e)
        assert False        
    
    
class NIOS_87171(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_create_RPZ_zone(self):
        print("\n============================================\n")
        print("Creating RPZ zone")
        print("\n============================================\n")
        
        data={"fqdn": "rpz_zone.com","view": "default","grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
        rpz_zone_ref=ib_NIOS.wapi_request('POST',fields=json.dumps(data),object_type="zone_rp")
        print(rpz_zone_ref)
        if type(rpz_zone_ref) == tuple:
            if rpz_zone_ref[0]==200:
                print("Success: Zone created successfully")
                restart_services()
                assert True
            else:
                print("Failure: Zone not created successfully")
                assert False
        elif 'rpz_zone.com' in rpz_zone_ref:
            print("Success: Zone created successfully")
            assert True        
        else:
                print("Failure: Zone not created successfully")
                assert False
                
    @pytest.mark.run(order=2)
    def test_001_validate_RPZ_zone_creation(self):        
        zone =  ib_NIOS.wapi_request('GET', object_type="zone_rp", grid_vip=config.grid_vip)
        zone=json.loads(zone)[0]['_ref']
        print(zone)
        if 'rpz_zone.com' in zone:
            print("Success: Validate RPZ zone created successfully")
            assert True
        else:
            print("Failure: Validate not create RPZ Zone")
            assert False
            
    @pytest.mark.run(order=3)
    def test_002_Assign_RPZ_Zone_to_analytics_blaclist(self):
       
        print("\n============================================\n")
        print("Add the zone to add blaclisted domains in threat analytics")
        print("\n============================================\n")
        zone =  ib_NIOS.wapi_request('GET', object_type="zone_rp", grid_vip=config.grid_vip)
        zone=json.loads(zone)[0]['_ref']
        print(zone)
        response1 = ib_NIOS.wapi_request('GET',object_type="grid:threatanalytics")
        response1=json.loads(response1)
        print(response1)
        ref_obj = response1[0]['_ref']
        response = ib_NIOS.wapi_request('PUT',object_type=ref_obj ,fields=json.dumps({"dns_tunnel_black_list_rpz_zones":[zone]}))
        print(response)
        
        if type(response) == tuple:
            if response[0]==200:
                print("Success: Add the zone to add blaclisted domains in threat analytics")
                
                assert True
            else:
                print("Failure: not Added the zone to blaclisted domains in threat analytics")
                assert False
        elif 'grid:threatanalytics' in response:
                print("Success: Add the zone to add blaclisted domains in threat analytics")
                
                assert True
                
    @pytest.mark.run(order=4)
    def test_003_validate_RPZ_Zone_to_analytics_whishlist(self):        
        response1 = ib_NIOS.wapi_request('GET',object_type="grid:threatanalytics?_return_fields=dns_tunnel_black_list_rpz_zones")
        response1=json.loads(response1)
        print(response1)
        ref_obj = response1[0]['dns_tunnel_black_list_rpz_zones']
        print(ref_obj)
        if 'rpz_zone.com' in ref_obj[0]:
            print("Success: Validate RPZ zone added to blaclisted domains in threat analytics")
            assert True
        else:
            print("Failure: To Validate RPZ zone not added to blaclisted domains in threat analytics")
            assert False
            
    @pytest.mark.run(order=5)
    def test_004_start_Threat_analytics_service(self):
        print("\n============================================\n")
        print("Start Threat analytics Service")
        print("\n============================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatanalytics", grid_vip=config.grid_vip)
        print(get_ref)
        res = json.loads(get_ref)
       
        for i in res:
            data = {"enable_service": True}
            response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            print(response)
            if type(response) == tuple:
                if response[0]==200:
                    print("Success: Start Threat analytics Service")
                    assert True
                else:
                    print("Failure: Start Threat analytics Service")
                    assert False
            
            elif "member:threatanalytics" in response:
                print("Success: Start Threat analytics Service")
                assert True
                
        sleep(300)
        check_able_to_login_appliances(config.grid_vip)
        restart_services()
                
    @pytest.mark.run(order=6)
    def test_005_validate_Threat_analytics_service_working(self):
        print("\n============================================\n")
        print("Validate Threat analytics Service working")
        print("\n============================================\n")
      
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatanalytics", grid_vip=config.grid_vip)
        print(get_ref)
        response1=json.loads(get_ref)
        print(response1)
        ref_obj = response1[0]['status']
        if 'WORKING' in ref_obj:
            print("Validating threat analytics service running")
            assert True
        else:
            print("Failure: Validating threat analytics service is working or not")
            assert False
            
            
    @pytest.mark.run(order=7)
    def test_006_enable_the_threat_protection_service_on_the_grid(self):
        print("\n============================================\n")
        print("Start Threat protection Service")
        print("\n============================================\n")
       
        data = {"enable_service": True}
        response = ib_NIOS.wapi_request('GET',object_type="member:threatprotection")
        response = json.loads(response)
        ref = response[1]['_ref']
        print(ref)
        response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
        print(response1)
        
        print(response1)
        if type(response1) == tuple:
            if response1[0]==200:
                print("Success: Start Threat protection Service")
                assert True
            else:
                print("Failure: Start Threat protection Service")
                assert False
                
        elif "member:threatprotection" in response:
            print("Success: Start Threat protection Service")
            assert True
            
        sleep(300)
        check_able_to_login_appliances(config.grid_vip)
        restart_services()
            
    @pytest.mark.run(order=8)
    def test_007_validate_Threat_protection_service_working(self):
        print("\n============================================\n")
        print("Validate Threat protection Service working")
        print("\n============================================\n")
       
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection?_return_fields=enable_service", grid_vip=config.grid_vip)
        print(get_ref)
        response1=json.loads(get_ref)
        print(response1)
        ref_obj = response1[1]['enable_service']
        if ref_obj==True:
            print("Validating threat protection service running on both master and member")
            assert True
        else:
            print("Failure: Validating threat protection service is working ot not on both master and member")
            assert False   
            
    @pytest.mark.run(order=9)
    def test_008_start_DNS_DCA_service(self):
        print("\n============================================\n")
        print("Start DCA Service")
        print("\n============================================\n")
        
        data = {"enable_dns": True,"enable_dns_cache_acceleration": True}
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            print(ref)
            if config.grid_member2_fqdn in ref['_ref']:
                pass
            else:
                response = ib_NIOS.wapi_request('PUT', object_type=ref['_ref'], fields=json.dumps(data))
                print(response)
                if type(response) == tuple:
                    if response[0]==200:
                        print("Success: Start DCA Service")
                        assert True
                    else:
                        print("Failure: Start DCA Service")
                        assert False
                        
                elif "member:dns" in response:
                    print("Success: Start DCA Service")
                    assert True
                
                    sleep(300)
                    check_able_to_login_appliances(config.grid_vip)
        
                
    @pytest.mark.run(order=10)
    def test_009_validate_DCA_service_working(self):
        print("\n============================================\n")
        print("Validate DCA Service working")
        print("\n============================================\n")
       
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns?_return_fields=enable_dns_cache_acceleration,enable_dns", grid_vip=config.grid_vip)
        print(get_ref)
        response1=json.loads(get_ref)
        print(response1)
        ref_obj = response1[0]['enable_dns_cache_acceleration']
        ref_obj1 = response1[0]['enable_dns']
        
        if ref_obj==True and ref_obj1==True:
            print("Validating DCA and DNS service running on both master and member")
            assert True
        else:
            print("Failure: Validate DCA and DNS Service not running on both master and member")
            assert False   
            
            
    @pytest.mark.run(order=11)
    def test_010_enable_snmp_trap_on_grid_level(self):
        print("\n============================================\n")
        print("Enable SNMP TRAPs on grid")
        print("\n============================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting', grid_vip=config.grid_vip)

        print(get_ref)
        for ref in json.loads(get_ref):
            data={"snmp_setting":{"queries_enable":True,"queries_community_string":config.community_string,"trap_receivers":[{"address": config.trap_receiver_ip}],"traps_community_string":config.community_string,"traps_enable":True}}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            print(response)
            if type(response) == tuple:
                if response[0]==200:
                    print("Success: Enable SNMP trap in the grid")
                    assert True
                else:
                    print("Failure: can not Enable SNMP trap in the grid")
                    assert False
            if 'grid' in response:
                print("Success: Enable SNMP trap in the grid")
                assert True
            else:
                print("Failure: can not Enable SNMP trap in the grid")
                assert False
                
    @pytest.mark.run(order=12)
    def test_011_validate_enable_snmp_trap_on_grid_level(self):
        print("\n============================================\n")
        print("Validate SNMP TRAPs on grid")
        print("\n============================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting', grid_vip=config.grid_vip)
        get_ref = json.loads(get_ref)
        print(get_ref)
        queries_en = get_ref[0]['snmp_setting']['queries_enable']
        traps_en = get_ref[0]['snmp_setting']['traps_enable']
        trap_add = get_ref[0]['snmp_setting']['trap_receivers'][0]['address']
        
        if queries_en==True and traps_en==True and trap_add==config.trap_receiver_ip:
            print("Validating snmpv1 and v2 Trap enabled")
            assert True
        else:
            print("Failure: Validate snmpv1 and v2 Trap not enabled")
            assert False                            
         
    @pytest.mark.run(order=13)
    def test_012_perform_snmpwalk_cmd(self):
        sleep(30)
        print("\n============================================\n")
        print("SNMP walk command on Threat Analytic Service description")
        print("\n============================================\n")
        
        client,stdout,stderr=perform_snmpwalk_command(config.grid_vip,"ibNodeServiceDesc.threat-analytics")
        
        if 'ibNodeServiceDesc.threat-analytics = STRING: Threat Analytics Service is working' in stdout:
            print("\nSuccess : Threat Analytics Service is working\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: Threat Analytics Service is not working ")
            assert False
        print("\n============================================\n")
        print("SNMP walk command on Threat Protection Service description")
        print("\n============================================\n")  

        client,stdout,stderr=perform_snmpwalk_command(config.grid_vip,"ibNodeServiceDesc.threat-protection")
        
        if 'ibNodeServiceDesc.threat-protection = STRING: Threat Protection Service is inactive' in stdout:
            print("\nSuccess : Threat Protection Service is inactive\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: Threat Protection Service is not working ")
            assert False
        print("\n============================================\n")
        print("SNMP walk command on DNS cache acceleration Service description")
        print("\n============================================\n")
        
        client,stdout,stderr=perform_snmpwalk_command(config.grid_vip,"ibNodeServiceDesc.dns-cache-acceleration")
        
        if 'ibNodeServiceDesc.dns-cache-acceleration = STRING: The DNS cache acceleration service is OK' in stdout:
            print("\nSuccess : The DNS cache acceleration service is OK\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: The DNS cache acceleration service is not OK ")
            assert False
        print("\n============================================\n")
        print("SNMP walk command on Power supply service status")
        print("\n============================================\n")
        
        client,stdout,stderr=perform_snmpwalk_command(config.grid_vip,"ibNodeServiceStatus.power")
        
        if 'ibNodeServiceStatus.power-supply1 = INTEGER: unknown' in stdout:
            print("\nSuccess : The DNS cache Power supply\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: The DNS cache Power supply not ok ")
            assert False
        
        
        print("\n============================================\n")
        print("SNMP walk command on DHCP service status")
        print("\n============================================\n")
        
        client,stdout,stderr=perform_snmpwalk_command(config.grid_vip,"ibServiceStatus.dhcp")
        
        if 'ibServiceStatus.dhcp = INTEGER: inactive' in stdout:
            print("\nSuccess : The DHCP service inactive\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: The DHCP service not inactive ")
            assert False
        
        print("\n============================================\n")
        print("SNMP walk command on DNS service status")
        print("\n============================================\n")
        
        client,stdout,stderr=perform_snmpwalk_command(config.grid_vip,"ibServiceStatus.dns")
        
        if 'ibServiceStatus.dns = INTEGER: working' in stdout:
            print("\nSuccess : The DNS service status active\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: The DNS service status not active")
            assert False
            
        print("\n============================================\n")
        print("SNMP walk command on NTP service status")
        print("\n============================================\n")
        
        client,stdout,stderr=perform_snmpwalk_command(config.grid_vip,"ibServiceStatus.ntp")
        
        if 'ibServiceStatus.ntp = INTEGER: inactive' in stdout:
            print("\nSuccess : The NTP service inactive\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: The NTP service not inactive ")
            assert False
            
        print("\n============================================\n")
        print("SNMP walk command on TFTP service status")
        print("\n============================================\n")
        
        client,stdout,stderr=perform_snmpwalk_command(config.grid_vip,"ibServiceStatus.tftp")
        
        if 'ibServiceStatus.tftp = INTEGER: inactive' in stdout:
            print("\nSuccess : The TFTP service inactive\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: The TFTP service not inactive ")
            assert False
        
        print("\n============================================\n")
        print("SNMP walk command on HTTP service status")
        print("\n============================================\n")

        client,stdout,stderr=perform_snmpwalk_command(config.grid_vip,"ibServiceStatus.http-file-dist")
        
        if 'ibServiceStatus.http-file-dist = INTEGER: inactive' in stdout:
            print("\nSuccess : The HTTP service inactive\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: The HTTP service not inactive")
            assert False
            
            
        print("\n============================================\n")
        print("SNMP walk command on FTP service status")
        print("\n============================================\n")

        client,stdout,stderr=perform_snmpwalk_command(config.grid_vip,"ibServiceStatus.ftp")
        
        if 'ibServiceStatus.ftp = INTEGER: inactive' in stdout:
            print("\nSuccess : The FTP service inactive\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: The FTP service not inactive")
            assert False

                  
        print("\n============================================\n")
        print("SNMP walk command on TAXII service status")
        print("\n============================================\n")
        
        client,stdout,stderr=perform_snmpwalk_command(config.grid_vip,"ibNodeServiceStatus.taxii")
        
        if 'ibNodeServiceStatus.taxii = INTEGER: inactive' in stdout:
            print("\nSuccess : The TAXII service inactive\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: The TAXII service not inactive")
            assert False
        
        
        print("\n============================================\n")
        print("SNMP walk command on DHCP service description")
        print("\n============================================\n")
        
        client,stdout,stderr=perform_snmpwalk_command(config.grid_vip,"ibServiceDesc.dhcp")
        
        if 'ibServiceDesc.dhcp = STRING: DHCP Service is inactive' in stdout:
            print("\nSuccess : STRING: DHCP Service is inactive\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: STRING: DHCP Service is not inactive")
            assert False
        print("\n============================================\n")
        print("SNMP walk command on DNS service description")
        print("\n============================================\n")
        
        client,stdout,stderr=perform_snmpwalk_command(config.grid_vip,"ibServiceDesc.dns")
        
        if 'ibServiceDesc.dns = STRING: DNS Service is working' in stdout:
            print("\nSuccess : STRING: DNS Service is working\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: STRING: DNS Service is not working")
            assert False


        print("\n============================================\n")
        print("SNMP walk command on NTP service description")
        print("\n============================================\n")
       
        client,stdout,stderr=perform_snmpwalk_command(config.grid_vip,"ibServiceDesc.ntp")
        
        if 'ibServiceDesc.ntp = STRING: NTP Service is inactive' in stdout:
            print("\nSuccess : STRING: NTP Service is inactive\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: STRING: NTP Service is not inactive")
            assert False
            
            
        print("\n============================================\n")
        print("SNMP walk command on TFTP service description")
        print("\n============================================\n")
        
        client,stdout,stderr=perform_snmpwalk_command(config.grid_vip,"ibServiceDesc.tftp")
        
        if 'ibServiceDesc.tftp = STRING: Hard Disk: 0% - TFTP Service is inactive' in stdout:
            print("\nSuccess : Hard Disk: 0% - TFTP Service is inactive\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: Hard Disk: 0% - TFTP Service is not inactive")
            assert False

        print("\n============================================\n")
        print("SNMP walk command on HTTP service description")
        print("\n============================================\n")

        client,stdout,stderr=perform_snmpwalk_command(config.grid_vip,"ibServiceDesc.http-file-dist")
        
        if 'ibServiceDesc.http-file-dist = STRING: Hard Disk: 0% - HTTP File Dist Service is inactive' in stdout:
            print("\nSuccess : Hard Disk: 0% - HTTP File Dist Service is inactive\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: Hard Disk: 0% - HTTP File Dist Service is not inactive")
            assert False
            
        print("\n============================================\n")
        print("SNMP walk command on FTP service description")
        print("\n============================================\n")
        
        client,stdout,stderr=perform_snmpwalk_command(config.grid_vip,"ibServiceDesc.ftp")
        
        if 'ibServiceDesc.ftp = STRING: Hard Disk: 0% - FTP Service is inactive' in stdout:
            print("\nSuccess : Hard Disk: 0% - FTP Service is inactive\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: Hard Disk: 0% - FTP Service is not inactive")
            assert False    
            
                   
        print("\n============================================\n")
        print("SNMP walk command on TAXII service description")
        print("\n============================================\n")
        
        client,stdout,stderr=perform_snmpwalk_command(config.grid_vip,"ibNodeServiceDesc.taxii")
        
        if 'ibNodeServiceDesc.taxii = STRING: TAXII Service is inactive' in stdout:
            print("\nSuccess : STRING: TAXII Service is inactive \n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: STRING: TAXII Service is not inactive ")
            assert False
            
    @pytest.mark.run(order=14)
    def test_013_perform_snmpwalk_cmd_with_member(self):
        sleep(30)
        print("\n============================================\n")
        print("SNMP walk command on Threat Analytic Service description with member")
        print("\n============================================\n")
        
        client,stdout,stderr=perform_snmpwalk_command(config.grid_member1_vip,"ibNodeServiceDesc.threat-analytics")
        
        if 'ibNodeServiceDesc.threat-analytics = STRING: Threat Analytics Service is working' in stdout:
            print("\nSuccess : Threat Analytics Service is working with member\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: Threat Analytics Service is not working with member")
            assert False
        print("\n============================================\n")
        print("SNMP walk command on Threat Protection Service description with member")
        print("\n============================================\n")  

        client,stdout,stderr=perform_snmpwalk_command(config.grid_member1_vip,"ibNodeServiceDesc.threat-protection")
        
        if 'ibNodeServiceDesc.threat-protection = STRING: Threat Protection Service is working' in stdout:
            print("\nSuccess : Threat Protection Service is working with member\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: Threat Protection Service is not working with member")
            assert False
        print("\n============================================\n")
        print("SNMP walk command on DNS cache acceleration Service description with member")
        print("\n============================================\n")
        
        client,stdout,stderr=perform_snmpwalk_command(config.grid_member1_vip,"ibNodeServiceDesc.dns-cache-acceleration")
        
        if 'ibNodeServiceDesc.dns-cache-acceleration = STRING: The DNS cache acceleration service is OK' in stdout:
            print("\nSuccess : The DNS cache acceleration service is OK with member\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: The DNS cache acceleration service is not OK with member ")
            assert False
        print("\n============================================\n")
        print("SNMP walk command on Power supply service status with member")
        print("\n============================================\n")
        
        client,stdout,stderr=perform_snmpwalk_command(config.grid_member1_vip,"ibNodeServiceStatus.power")
        
        if 'ibNodeServiceStatus.power-supply1 = INTEGER: unknown' in stdout:
            print("\nSuccess : The DNS cache Power supply with member\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: The DNS cache Power supply not ok with member")
            assert False
        
        
        print("\n============================================\n")
        print("SNMP walk command on DHCP service status with member")
        print("\n============================================\n")
        
        client,stdout,stderr=perform_snmpwalk_command(config.grid_member1_vip,"ibServiceStatus.dhcp")
        
        if 'ibServiceStatus.dhcp = INTEGER: inactive' in stdout:
            print("\nSuccess : The DHCP service inactive with member\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: The DHCP service not inactive with member")
            assert False
        
        print("\n============================================\n")
        print("SNMP walk command on DNS service status")
        print("\n============================================\n")
        
        client,stdout,stderr=perform_snmpwalk_command(config.grid_member1_vip,"ibServiceStatus.dns")
        
        if 'ibServiceStatus.dns = INTEGER: working' in stdout:
            print("\nSuccess : The DNS service status active with member\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: The DNS service status not active with member")
            assert False
            
        print("\n============================================\n")
        print("SNMP walk command on NTP service status with member")
        print("\n============================================\n")
        
        client,stdout,stderr=perform_snmpwalk_command(config.grid_member1_vip,"ibServiceStatus.ntp")
        
        if 'ibServiceStatus.ntp = INTEGER: inactive' in stdout:
            print("\nSuccess : The NTP service inactive with member\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: The NTP service not inactive with member")
            assert False
            
        print("\n============================================\n")
        print("SNMP walk command on TFTP service status with member")
        print("\n============================================\n")
        
        client,stdout,stderr=perform_snmpwalk_command(config.grid_member1_vip,"ibServiceStatus.tftp")
            
        if 'ibServiceStatus.tftp = INTEGER: inactive' in stdout:
            print("\nSuccess : The TFTP service inactive with member\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: The TFTP service not inactive with member")
            assert False
        
        print("\n============================================\n")
        print("SNMP walk command on HTTP service status with member")
        print("\n============================================\n")

        client,stdout,stderr=perform_snmpwalk_command(config.grid_member1_vip,"ibServiceStatus.http-file-dist")
        
        if 'ibServiceStatus.http-file-dist = INTEGER: inactive' in stdout:
            print("\nSuccess : The HTTP service inactive with member\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: The HTTP service not inactive with member")
            assert False
            
            
        print("\n============================================\n")
        print("SNMP walk command on FTP service status with member")
        print("\n============================================\n")

        client,stdout,stderr=perform_snmpwalk_command(config.grid_member1_vip,"ibServiceStatus.ftp")
        
        if 'ibServiceStatus.ftp = INTEGER: inactive' in stdout:
            print("\nSuccess : The FTP service inactive with member\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: The FTP service not inactive with member")
            assert False
        
        print("\n============================================\n")
        print("SNMP walk command on TAXII service status with member")
        print("\n============================================\n")
        
        client,stdout,stderr=perform_snmpwalk_command(config.grid_member1_vip,"ibNodeServiceStatus.taxii")
        
        if 'ibNodeServiceStatus.taxii = INTEGER: inactive' in stdout:
            print("\nSuccess : The TAXII service inactive with member\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: The TAXII service not inactive with member")
            assert False
        
        
        print("\n============================================\n")
        print("SNMP walk command on DHCP service description with member")
        print("\n============================================\n")
        
        client,stdout,stderr=perform_snmpwalk_command(config.grid_member1_vip,"ibServiceDesc.dhcp")
        
        if 'ibServiceDesc.dhcp = STRING: DHCP Service is inactive' in stdout:
            print("\nSuccess : STRING: DHCP Service is inactive with member\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: STRING: DHCP Service is not inactive with member")
            assert False
        print("\n============================================\n")
        print("SNMP walk command on DNS service description with member")
        print("\n============================================\n")
        
        client,stdout,stderr=perform_snmpwalk_command(config.grid_member1_vip,"ibServiceDesc.dns")
        
        if 'ibServiceDesc.dns = STRING: DNS Service is working' in stdout:
            print("\nSuccess : STRING: DNS Service is working with member\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: STRING: DNS Service is not working with member")
            assert False


        print("\n============================================\n")
        print("SNMP walk command on NTP service description with member")
        print("\n============================================\n")
       
        client,stdout,stderr=perform_snmpwalk_command(config.grid_member1_vip,"ibServiceDesc.ntp")
        
        if 'ibServiceDesc.ntp = STRING: NTP Service is inactive' in stdout:
            print("\nSuccess : STRING: NTP Service is inactive with member\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: STRING: NTP Service is not inactive with member")
            assert False
            
            
        print("\n============================================\n")
        print("SNMP walk command on TFTP service description with member")
        print("\n============================================\n")
        
        client,stdout,stderr=perform_snmpwalk_command(config.grid_member1_vip,"ibServiceDesc.tftp")
            
        if 'ibServiceDesc.tftp = STRING: Hard Disk: 0% - TFTP Service is inactive' in stdout:
            print("\nSuccess : Hard Disk: 0% - TFTP Service is inactive with member\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: Hard Disk: 0% - TFTP Service is not inactive with member")
            assert False

        print("\n============================================\n")
        print("SNMP walk command on HTTP service description with member")
        print("\n============================================\n")

        client,stdout,stderr=perform_snmpwalk_command(config.grid_member1_vip,"ibServiceDesc.http-file-dist")
        
        if 'ibServiceDesc.http-file-dist = STRING: Hard Disk: 0% - HTTP File Dist Service is inactive' in stdout:
            print("\nSuccess : Hard Disk: 0% - HTTP File Dist Service is inactive with member\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: Hard Disk: 0% - HTTP File Dist Service is not inactive with member")
            assert False
            
        print("\n============================================\n")
        print("SNMP walk command on FTP service description with member")
        print("\n============================================\n")
        
        client,stdout,stderr=perform_snmpwalk_command(config.grid_member1_vip,"ibServiceDesc.ftp")
        
        if 'ibServiceDesc.ftp = STRING: Hard Disk: 0% - FTP Service is inactive' in stdout:
            print("\nSuccess : Hard Disk: 0% - FTP Service is inactive with member\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: Hard Disk: 0% - FTP Service is not inactive with member")
            assert False    
        
        print("\n============================================\n")
        print("SNMP walk command on TAXII service description with member")
        print("\n============================================\n")
        
        client,stdout,stderr=perform_snmpwalk_command(config.grid_member1_vip,"ibNodeServiceDesc.taxii")
        
        if 'ibNodeServiceDesc.taxii = STRING: TAXII Service is inactive' in stdout:
            print("\nSuccess : STRING: TAXII Service is inactive with member \n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: STRING: TAXII Service is not inactive with member")
            assert False
            
                  
    @pytest.mark.run(order=15)
    def test_014_create_an_SNMPv3_User(self):
       print("Create an SNMPv3 User")
       
       data={"name":"snmptest","authentication_protocol":"SHA","privacy_protocol":"AES","privacy_password":"infoblox1","authentication_password":"infoblox1"}

       response = ib_NIOS.wapi_request('POST',object_type="snmpuser",fields=json.dumps(data))
       print(response)
       
       if type(response) == tuple:           
           if response[0]==200:  
               print("\n Success: Created SNMPv3 User\n")
               assert True
           else:
               print("\n Failure: Did not Create SNMPv3 User\n")
               assert False
               
    @pytest.mark.run(order=16)
    def test_015_validate_created_an_SNMPv3_User(self):
        print("\n============================================\n")
        print("Validate SNMPV3 user created")
        print("\n============================================\n")

        getref = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        
        snmpuser_name = json.loads(getref)[0]["name"]
        
        if 'snmptest' in snmpuser_name:
            print("Validating SNMPV3 user created")
            assert True
        else:
            print("Failure: Validate SNMPV3 user not created")
            assert False      
            
    @pytest.mark.run(order=17)
    def test_016_assign_SNMPV3_user_with_grid(self):      
       response = ib_NIOS.wapi_request('GET',object_type="snmpuser")
       snmp_memref = json.loads(response)[0]['_ref']
       snmp_memref = snmp_memref.encode('ascii', 'ignore')
       print(snmp_memref)
  
        
       get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting')
       getref=json.loads(get_ref)[0]['_ref']
       print(getref)
       data={"snmp_setting":{"snmpv3_traps_enable": True,"snmpv3_queries_enable": True,"snmpv3_queries_users": [{"user":snmp_memref}],"queries_enable":True,"queries_community_string":config.community_string,"trap_receivers":[{"address": config.trap_receiver_ip},{"address": config.client_ip,"user":snmp_memref}],"traps_community_string":config.community_string,"traps_enable":True}}
       
       response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
       print(response)
       if type(response) == tuple:
           if response[0]==200:
               print("Success: Enable SNMP configuration on grid level")
               assert True
           else:
               print("Failure: did not Enable SNMP configuration on grid level")
               assert False  

       if 'grid' in response:
           print("Success: Enable SNMP trap in the grid")
           assert True
       else:
           print("Failure: can not Enable SNMP trap in the grid")
           assert False    
            
    @pytest.mark.run(order=18)
    def test_017_validate_snmpv3_trap_enabled_on_grid_level(self):
        print("\n============================================\n")
        print("Validate SNMPV3 TRAPs on grid")
        print("\n============================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting', grid_vip=config.grid_vip)
        get_ref = json.loads(get_ref)
        print(get_ref)
       
        trap_add1 = get_ref[0]['snmp_setting']['trap_receivers'][0]['address']
        v3trap_en = get_ref[0]['snmp_setting']['snmpv3_traps_enable']
        v3q_user = get_ref[0]['snmp_setting']['snmpv3_queries_users'][0]['user']['name']
        trap_add = get_ref[0]['snmp_setting']['trap_receivers'][1]['address']
        print(trap_add)
        if v3trap_en==True and 'snmptest' == v3q_user and trap_add==config.client_ip and trap_add1==config.trap_receiver_ip:
            print("Validating snmpv3 Trap enabled")
            assert True
        else:
            print("Failure: Validate snmpv3 Trap not enabled")
            assert False                            
         
         
    @pytest.mark.run(order=19)
    def test_018_Perform_SNMPGET_commands_on_all_three_vesion(self):   
        '''Add sys data'''
        response = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmp_memref = json.loads(response)[0]['_ref']
        snmp_memref = snmp_memref.encode('ascii', 'ignore')
        print(snmp_memref)
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting')
        getref=json.loads(get_ref)[0]['_ref']
        print(getref)
        data={"snmp_setting":{"syscontact": ["sys_Contact"],"sysdescr": ["sys_Descr"],"syslocation": ["sys_Location"],"sysname": ["sys_Name"],"snmpv3_traps_enable": True,"snmpv3_queries_enable": True,"snmpv3_queries_users": [{"user":snmp_memref}],"queries_enable":True,"queries_community_string":config.community_string,"trap_receivers":[{"address": config.trap_receiver_ip},{"address": config.client_ip,"user":snmp_memref}],"traps_community_string":config.community_string,"traps_enable":True}}
        response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
        print(response)
        print(response)
        if type(response) == tuple:
            if response[0]==200:
                print("Success: added sys data")
                assert True
            else:
                print("Failure: did not added sys data")
                assert False
        elif 'grid' in response:
            print("Success: added sys data")
            assert True
        sleep(30)
        print("\n============================================\n")
        print("SNMPGET command on v1, v2, v3")
        print("\n============================================\n")
        
        ''' sysDescr '''
        
        client,stdout_v1,stderr=perform_snmp_command_on_v1("snmpget",config.grid_vip,"sysDescr.0")
       
        client,stdout_v2,stderr=perform_snmp_command_on_v2("snmpget",config.grid_vip,"sysDescr.0")
        
        client,stdout_v3,stderr=perform_snmp_command_on_v3("snmpget",config.grid_vip,"sysDescr.0")
        
        validate_snmp_command_on_v1(stdout_v1,'STRING: sys_Descr',"SNMPGET",client,"master")
        validate_snmp_command_on_v2(stdout_v2,'STRING: sys_Descr',"SNMPGET",client,"master")
        validate_snmp_command_on_v3(stdout_v3,'STRING: sys_Descr',"SNMPGET",client,"master")
        

        ''' sysContact ''' 
       
        client,stdout_v1,stderr=perform_snmp_command_on_v1("snmpget",config.grid_vip,"sysContact.0")
        
        client,stdout_v2,stderr=perform_snmp_command_on_v2("snmpget",config.grid_vip,"sysContact.0")

        client,stdout_v3,stderr=perform_snmp_command_on_v3("snmpget",config.grid_vip,"sysContact.0")
        
        validate_snmp_command_on_v1(stdout_v1,'STRING: sys_Contact',"SNMPGET",client,"master")
        validate_snmp_command_on_v2(stdout_v2,'STRING: sys_Contact',"SNMPGET",client,"master")
        validate_snmp_command_on_v3(stdout_v3,'STRING: sys_Contact',"SNMPGET",client,"master")
            
        ''' sysName ''' 
        
        client,stdout_v1,stderr=perform_snmp_command_on_v1("snmpget",config.grid_vip,"sysName.0")
        
        client,stdout_v2,stderr=perform_snmp_command_on_v2("snmpget",config.grid_vip,"sysName.0")
       
        client,stdout_v3,stderr=perform_snmp_command_on_v3("snmpget",config.grid_vip,"sysName.0")
        
        validate_snmp_command_on_v1(stdout_v1,'STRING: sys_Name',"SNMPGET",client,"master")
        validate_snmp_command_on_v2(stdout_v2,'STRING: sys_Name',"SNMPGET",client,"master")
        validate_snmp_command_on_v3(stdout_v3,'STRING: sys_Name',"SNMPGET",client,"master")
        
                   
        ''' sysLocation ''' 
        client,stdout_v1,stderr=perform_snmp_command_on_v1("snmpget",config.grid_vip,"sysLocation.0")
        
        client,stdout_v2,stderr=perform_snmp_command_on_v2("snmpget",config.grid_vip,"sysLocation.0")
        
        client,stdout_v3,stderr=perform_snmp_command_on_v3("snmpget",config.grid_vip,"sysLocation.0")
        
        validate_snmp_command_on_v1(stdout_v1,'STRING: sys_Location',"SNMPGET",client,"master")
        validate_snmp_command_on_v2(stdout_v2,'STRING: sys_Location',"SNMPGET",client,"master")
        validate_snmp_command_on_v3(stdout_v3,'STRING: sys_Location',"SNMPGET",client,"master")
       
        child1 = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        try:
            child1.logfile=sys.stdout
            child1.expect('password:')
            child1.sendline('infoblox')
            child1.expect('Infoblox >')
            child1.sendline('show version')
            child1.expect('Infoblox >')
            
            output= child1.before
            child1.close()
        except Exception as e:
            child1.close()
            print("\n Failure: error in executing snmp comand")
            print("\n================Error====================\n")
            print(e)
            assert False        
               
        print(output)
        version=output.split('-')[0].split(':')[1].strip()
        ''' ibNiosVersion ''' 
        client,stdout_v1,stderr=perform_snmp_command_on_v1("snmpget",config.grid_vip,"-m all ibNiosVersion.0")
        
        client,stdout_v2,stderr=perform_snmp_command_on_v2("snmpget",config.grid_vip,"-m all ibNiosVersion.0")
        
        client,stdout_v3,stderr=perform_snmp_command_on_v3("snmpget",config.grid_vip,"-m all ibNiosVersion.0")
        
        validate_snmp_command_on_v1(stdout_v1,version,"SNMPGET",client,"master")
        validate_snmp_command_on_v2(stdout_v2,version,"SNMPGET",client,"master")
        validate_snmp_command_on_v3(stdout_v3,version,"SNMPGET",client,"master")
       
    @pytest.mark.run(order=20)
    def test_019_Perform_SNMPGET_commands_on_all_three_vesion_with_member(self):   
        
        print("\n============================================\n")
        print("SNMPGET command on v1, v2, v3 with member")
        print("\n============================================\n")
        
        ''' sysDescr '''
        
        client,stdout_v1,stderr=perform_snmp_command_on_v1("snmpget",config.grid_member1_vip,"sysDescr.0")
       
        client,stdout_v2,stderr=perform_snmp_command_on_v2("snmpget",config.grid_member1_vip,"sysDescr.0")
        
        client,stdout_v3,stderr=perform_snmp_command_on_v3("snmpget",config.grid_member1_vip,"sysDescr.0")
        
        validate_snmp_command_on_v1(stdout_v1,'STRING: sys_Descr',"SNMPGET",client,"member")
        validate_snmp_command_on_v2(stdout_v2,'STRING: sys_Descr',"SNMPGET",client,"member")
        validate_snmp_command_on_v3(stdout_v3,'STRING: sys_Descr',"SNMPGET",client,"member")

               
        ''' sysContact ''' 
       
        client,stdout_v1,stderr=perform_snmp_command_on_v1("snmpget",config.grid_member1_vip,"sysContact.0")
        
        client,stdout_v2,stderr=perform_snmp_command_on_v2("snmpget",config.grid_member1_vip,"sysContact.0")

        client,stdout_v3,stderr=perform_snmp_command_on_v3("snmpget",config.grid_member1_vip,"sysContact.0")
        
        validate_snmp_command_on_v1(stdout_v1,'STRING: sys_Contact',"SNMPGET",client,"member")
        validate_snmp_command_on_v2(stdout_v2,'STRING: sys_Contact',"SNMPGET",client,"member")
        validate_snmp_command_on_v3(stdout_v3,'STRING: sys_Contact',"SNMPGET",client,"member")
       
       
        ''' sysName ''' 
        
        client,stdout_v1,stderr=perform_snmp_command_on_v1("snmpget",config.grid_member1_vip,"sysName.0")
        
        client,stdout_v2,stderr=perform_snmp_command_on_v2("snmpget",config.grid_member1_vip,"sysName.0")
       
        client,stdout_v3,stderr=perform_snmp_command_on_v3("snmpget",config.grid_member1_vip,"sysName.0")
        
        validate_snmp_command_on_v1(stdout_v1,'STRING: sys_Name',"SNMPGET",client,"member")
        validate_snmp_command_on_v2(stdout_v2,'STRING: sys_Name',"SNMPGET",client,"member")
        validate_snmp_command_on_v3(stdout_v3,'STRING: sys_Name',"SNMPGET",client,"member")

            
        ''' sysLocation ''' 
        client,stdout_v1,stderr=perform_snmp_command_on_v1("snmpget",config.grid_member1_vip,"sysLocation.0")
        
        client,stdout_v2,stderr=perform_snmp_command_on_v2("snmpget",config.grid_member1_vip,"sysLocation.0")
        
        client,stdout_v3,stderr=perform_snmp_command_on_v3("snmpget",config.grid_member1_vip,"sysLocation.0")
        
        validate_snmp_command_on_v1(stdout_v1,'STRING: sys_Location',"SNMPGET",client,"member")
        validate_snmp_command_on_v2(stdout_v2,'STRING: sys_Location',"SNMPGET",client,"member")
        validate_snmp_command_on_v3(stdout_v3,'STRING: sys_Location',"SNMPGET",client,"member")
        
        ''' ibNiosVersion ''' 
        child1 = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        try:
            child1.logfile=sys.stdout
            child1.expect('password:')
            child1.sendline('infoblox')
            child1.expect('Infoblox >')
            child1.sendline('show version')
            child1.expect('Infoblox >')
            
            output= child1.before
            child1.close()
        except Exception as e:
            child1.close()
            print("\n Failure: error in executing snmp comand")
            print("\n================Error====================\n")
            print(e)
            assert False        
               
        print(output)
        version=output.split('-')[0].split(':')[1].strip()
        
        client,stdout_v1,stderr=perform_snmp_command_on_v1("snmpget",config.grid_member1_vip,"-m all ibNiosVersion.0")
        
        client,stdout_v2,stderr=perform_snmp_command_on_v2("snmpget",config.grid_member1_vip,"-m all ibNiosVersion.0")
        
        client,stdout_v3,stderr=perform_snmp_command_on_v3("snmpget",config.grid_member1_vip,"-m all ibNiosVersion.0")
        
        validate_snmp_command_on_v1(stdout_v1,version,"SNMPGET",client,"member")
        validate_snmp_command_on_v2(stdout_v2,version,"SNMPGET",client,"member")
        validate_snmp_command_on_v3(stdout_v3,version,"SNMPGET",client,"member")
        
       
    @pytest.mark.run(order=21)
    def test_020_Perform_SNMPGETNEXT_commands_on_all_three_vesion(self):   
               
        print("\n============================================\n")
        print("SNMPGETNEXT command on v1, v2, v3 with Master")
        print("\n============================================\n")
        
        client,stdout_v1,stderr=perform_snmp_command_on_v1("snmpgetnext",config.grid_vip,"-m all ibNiosVersion.0")
        
        client,stdout_v2,stderr=perform_snmp_command_on_v2("snmpgetnext",config.grid_vip,"-m all ibNiosVersion.0")
        
        client,stdout_v3,stderr=perform_snmp_command_on_v3("snmpgetnext",config.grid_vip,"-m all ibNiosVersion.0")
        
        validate_snmp_command_on_v1(stdout_v1,'ibSystemMonitorCpuUsage.0 = INTEGER:',"SNMPGETNEXT",client,"master")
        validate_snmp_command_on_v2(stdout_v2,'ibSystemMonitorCpuUsage.0 = INTEGER:',"SNMPGETNEXT",client,"master")
        validate_snmp_command_on_v3(stdout_v3,'ibSystemMonitorCpuUsage.0 = INTEGER:',"SNMPGETNEXT",client,"master")
        

    @pytest.mark.run(order=22)
    def test_021_Perform_SNMPGETNEXT_commands_on_all_three_vesion_with_member(self):   
               
        print("\n============================================\n")
        print("SNMPGETNEXT command on v1, v2, v3 with member")
        print("\n============================================\n")
        
        client,stdout_v1,stderr=perform_snmp_command_on_v1("snmpgetnext",config.grid_member1_vip,"-m all ibNiosVersion.0")
        
        client,stdout_v2,stderr=perform_snmp_command_on_v2("snmpgetnext",config.grid_member1_vip,"-m all ibNiosVersion.0")
        
        client,stdout_v3,stderr=perform_snmp_command_on_v3("snmpgetnext",config.grid_member1_vip,"-m all ibNiosVersion.0")
        
        validate_snmp_command_on_v1(stdout_v1,'ibSystemMonitorCpuUsage.0 = INTEGER:',"SNMPGETNEXT",client,"member")
        validate_snmp_command_on_v2(stdout_v2,'ibSystemMonitorCpuUsage.0 = INTEGER:',"SNMPGETNEXT",client,"member")
        validate_snmp_command_on_v3(stdout_v3,'ibSystemMonitorCpuUsage.0 = INTEGER:',"SNMPGETNEXT",client,"member")
        
                
            
    @pytest.mark.run(order=23)
    def test_022_Perform_SNMPBULKGET_commands_v2_v3_vesion(self):   
                   
        print("\n============================================\n")
        print("SNMPBULKGET command on v1-not supported v2,v3 supported")
        print("\n============================================\n")

        client,stdout_v2,stderr=perform_snmp_command_on_v2("snmpbulkget",config.grid_vip,"-t 5 "+config.OID)
        
        client,stdout_v3,stderr=perform_snmp_command_on_v3("snmpbulkget",config.grid_vip,"-t 5 "+config.OID)
        
        validate_snmp_command_on_v2(stdout_v2,'hrSWRunPerfCPU',"SNMPBULKGET",client,"master")
        validate_snmp_command_on_v3(stdout_v3,'hrSWRunPerfCPU',"SNMPBULKGET",client,"master")
        

    @pytest.mark.run(order=24)
    def test_023_Perform_SNMPBULKGET_commands_v2_v3_vesion_with_member(self):   
                   
        print("\n============================================\n")
        print("SNMPBULKGET command on v1-not supported v2,v3 supported with member")
        print("\n============================================\n")

        client,stdout_v2,stderr=perform_snmp_command_on_v2("snmpbulkget",config.grid_member1_vip,"-t 5 "+config.OID)
        
        client,stdout_v3,stderr=perform_snmp_command_on_v3("snmpbulkget",config.grid_member1_vip,"-t 5 "+config.OID)
        
        validate_snmp_command_on_v2(stdout_v2,'hrSWRunPerfCPU',"SNMPBULKGET",client,"member")
        validate_snmp_command_on_v3(stdout_v3,'hrSWRunPerfCPU',"SNMPBULKGET",client,"member")
        

            
    @pytest.mark.run(order=25)
    def test_024_Perform_SNMPTABLE_commands_on_all_three_vesion(self):   
          
        print("\n============================================\n")
        print("SNMPTABLE command on snmpv1, v2, v3")
        print("\n============================================\n")
        
        client,stdout_v1,stderr=perform_snmp_command_on_v1("snmptable",config.grid_vip," -m ALL -M+/usr/share/snmp/mibs/ IB-PLATFORMONE-MIB::ibMemberServiceStatusTable")
        
        client,stdout_v2,stderr=perform_snmp_command_on_v2("snmptable",config.grid_vip," -m ALL -M+/usr/share/snmp/mibs/ IB-PLATFORMONE-MIB::ibMemberServiceStatusTable")
        
        client,stdout_v3,stderr=perform_snmp_command_on_v3("snmptable",config.grid_vip," -m ALL -M+/usr/share/snmp/mibs/ IB-PLATFORMONE-MIB::ibMemberServiceStatusTable")
        
        validate_snmp_command_on_v1(stdout_v1,'DNS Service is working',"SNMPTABLE",client,"master")
        validate_snmp_command_on_v2(stdout_v2,'DNS Service is working',"SNMPTABLE",client,"master")
        validate_snmp_command_on_v3(stdout_v3,'DNS Service is working',"SNMPTABLE",client,"master")
 
    @pytest.mark.run(order=26)
    def test_025_Perform_SNMPTABLE_commands_on_all_three_vesion_with_member(self):   
           
                
        print("\n============================================\n")
        print("SNMPTABLE command on snmpv1, v2, v3 with member")
        print("\n============================================\n")
        
        client,stdout_v1,stderr=perform_snmp_command_on_v1("snmptable",config.grid_member1_vip," -m ALL -M+/usr/share/snmp/mibs/ IB-PLATFORMONE-MIB::ibMemberServiceStatusTable")
        
        client,stdout_v2,stderr=perform_snmp_command_on_v2("snmptable",config.grid_member1_vip," -m ALL -M+/usr/share/snmp/mibs/ IB-PLATFORMONE-MIB::ibMemberServiceStatusTable")
        
        client,stdout_v3,stderr=perform_snmp_command_on_v3("snmptable",config.grid_member1_vip," -m ALL -M+/usr/share/snmp/mibs/ IB-PLATFORMONE-MIB::ibMemberServiceStatusTable")
        
        validate_snmp_command_on_v1(stdout_v1,'DNS Service is working',"SNMPTABLE",client,"member")
        validate_snmp_command_on_v2(stdout_v2,'DNS Service is working',"SNMPTABLE",client,"member")
        validate_snmp_command_on_v3(stdout_v3,'DNS Service is working',"SNMPTABLE",client,"member")
            
    @pytest.mark.run(order=27)
    def test_026_reboot_appliances_observe_netsnmp_assert(self):
        log("start","/var/log/messages",config.grid_vip)
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
        check_able_to_login_appliances(config.grid_vip)
        sleep(60)
        child1.close()

        log("stop","/var/log/messages",config.grid_vip)
        LookFor=".*err.*netsnmp_assert.*"
        print(LookFor)
        logs=logv(LookFor,"/var/log/messages",config.grid_vip)
        print(logs)
        if logs:
            print("Failure: Found netsnmp_assert which is a bug")
            assert False
            
        else:
            print("Failure: Found netsnmp_assert which is a bug")
            assert True  

    @pytest.mark.run(order=28)
    def test_027_disable_SNMP_configuration(self):
        '''Disable SNMP configuration '''
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid')
        get_grid_ref=json.loads(get_ref)[0]['_ref']
        
        data={"snmp_setting":{"snmpv3_traps_enable": False,"snmpv3_queries_enable": False,"snmpv3_queries_users": [],"queries_enable":False,"queries_community_string":"","trap_receivers":[],"traps_community_string":"","traps_enable":False}}
       
        response=ib_NIOS.wapi_request('PUT',ref=get_grid_ref, fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:
                print("Sucess: \n Deleting SNMP configuration on GRID-LEVEL ")
                assert True
                
            else:
                print("Failure: \n can not Delete SNMP configuration on GRID-LEVEL ")
                assert False
        if 'grid' in response:
                print("Success: Enable SNMP trap in the grid")
                assert True
        else:
            print("Failure: can not Enable SNMP trap in the grid")
            assert False  
        sleep(20)   

    @pytest.mark.run(order=29)
    def test_028_validate_snmp_configuration_is_disable(self):
        print("\n============================================\n")
        print("Validate SNMP configuration is disable")
        print("\n============================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting', grid_vip=config.grid_vip)
        get_ref = json.loads(get_ref)
        print(get_ref)
        v3trap_en = get_ref[0]['snmp_setting']['snmpv3_traps_enable']
        queries_en = get_ref[0]['snmp_setting']['queries_enable']
        traps_en = get_ref[0]['snmp_setting']['traps_enable']
        
        if queries_en==False and traps_en==False and v3trap_en==False:
            print("Validating snmpv1, v2 and v3 Trap and queries disabled")
            assert True
        else:
            print("Failure: Validate snmpv1, v2 and v3 Trap and queries not disabled")
            assert False                            
         
    @pytest.mark.run(order=30)
    def test_029_perform_cli_command_on_snmp_before_snmp_configure(self):
        
        print("\n============================================\n")
        print("Perform CLI commands on SNMP before SNMP configure")
        print("\n============================================\n")
        
        output=perform_cli_commands_on_snmp(config.grid_vip,'set snmptrap variable 1.3.6.1.4.1.7779.3.1.1.1.1.1 address '+config.grid_vip+' ibTrapDesc '"The system"'')
        
        if 'Please enable SNMPv1/v2 traps and set community' in output:
            print("\n Success: Please enable SNMPv1/v2 traps and set community")
            assert True
        else:
            print("\n Failure: Perform CLI set snmptrap command")
            assert False
            
        output=perform_cli_commands_on_snmp(config.grid_vip,'show snmp variable sysName.0')
         
        if 'Please enable SNMP query and set community' in output:
            print("\n Success: Please enable SNMP query and set community.")
            assert True
        else:
            print("\n Failure: Perform CLI show snmp command")
            assert False

    @pytest.mark.run(order=31)
    def test_030_perform_cli_command_on_snmp_before_snmp_configure_wth_member(self):
        
        print("\n============================================\n")
        print("Perform CLI commands on SNMP before SNMP configure with member")
        print("\n============================================\n")
        
        output=perform_cli_commands_on_snmp(config.grid_member1_vip,'set snmptrap variable 1.3.6.1.4.1.7779.3.1.1.1.1.1 address '+config.grid_member1_vip+' ibTrapDesc '"The system"'')
        
        if 'Please enable SNMPv1/v2 traps and set community' in output:
            print("\n Success: Please enable SNMPv1/v2 traps and set community with member IP")
            assert True
        else:
            print("\n Failure: Perform CLI set snmptrap command with member")
            assert False
            
        output=perform_cli_commands_on_snmp(config.grid_member1_vip,'show snmp variable sysName.0')
         
        if 'Please enable SNMP query and set community' in output:
            print("\n Success: Please enable SNMP query and set community. with member IP")
            assert True
        else:
            print("\n Failure: Perform CLI show snmp command with member")
            assert False
            
    @pytest.mark.run(order=32)
    def test_031_enable_SNMP_configuration_back(self):           
        response = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmp_memref = json.loads(response)[0]['_ref']
        snmp_memref = snmp_memref.encode('ascii', 'ignore')
        print(snmp_memref)
  
        
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting')
        getref=json.loads(get_ref)[0]['_ref']
        print(getref)
        data={"snmp_setting":{"snmpv3_traps_enable": True,"snmpv3_queries_enable": True,"snmpv3_queries_users": [{"user":snmp_memref}],"queries_enable":True,"queries_community_string":config.community_string,"trap_receivers":[{"address": config.trap_receiver_ip},{"address": config.client_ip,"user":snmp_memref}],"traps_community_string":config.community_string,"traps_enable":True}}
       
        response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:
                print("Sucess: \n Enable SNMP configuration on GRID-LEVEL ")
                assert True
            else:
                print("Failure: \n Did not Enable SNMP configuration on GRID-LEVEL ")
                assert False
        if 'grid' in response:
                print("Success: Enable SNMP trap in the grid")
                assert True
        else:
            print("Failure: can not Enable SNMP trap in the grid")
            assert False    
        sleep(30)
        
    @pytest.mark.run(order=33)
    def test_032_validate_snmp_configuration_is_enabled(self):
        print("\n============================================\n")
        print("Validate SNMP configuration is enabled")
        print("\n============================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting', grid_vip=config.grid_vip)
        get_ref = json.loads(get_ref)
        print(get_ref)
        v3trap_en = get_ref[0]['snmp_setting']['snmpv3_traps_enable']
        queries_en = get_ref[0]['snmp_setting']['queries_enable']
        traps_en = get_ref[0]['snmp_setting']['traps_enable']
        
        if queries_en==True and traps_en==True and v3trap_en==True:
            print("Validating snmpv1, v2 and v3 Trap and queries enabled")
            assert True
        else:
            print("Failure: Validate snmpv1, v2 and v3 Trap and queries not enabled")
            assert False 
            
    @pytest.mark.run(order=34)
    def test_033_perform_cli_command_on_snmp_after_configure_snmp(self):
        output=perform_cli_commands_on_snmp(config.grid_vip,'show snmp variable sysName.0')

        if 'STRING: "sys_Name"' in output:
            print("\n Success: show snmp variable sysName.0")
            assert True
        else:
            print("\n Failure: Perform CLI show snmp variable command")
            assert False
            
        output=perform_cli_commands_on_snmp(config.grid_vip,'show snmp variable .1.3.6.1.4.1.2021.11.53.0')

        if 'UCD-SNMP-MIB::ssCpuRawIdle' in output:
            print("\n Success: show snmp variable .1.3.6.1.4.1.2021.11.53.0")
            assert True
        else:
            print("\n Failure: Perform CLI show snmp variable command")
            assert False
            
        output=perform_cli_commands_on_snmp(config.grid_vip,'show snmp variable sysName.0 v3 snmptest')
   
        if 'STRING: "sys_Name"' in output:
            print("\n Success: show snmp variable sysName.0 v3 snmptest")
            assert True
        else:
            print("\n Failure: Perform CLI show snmp variable command")
            assert False
            
        output=perform_cli_commands_on_snmp(config.grid_vip,'show snmp variable .1.3.6.1.4.1.2021.11.53.0 v3 snmptest')
       
        if 'UCD-SNMP-MIB::ssCpuRawIdle' in output:
            print("\n Success: show snmp variable .1.3.6.1.4.1.2021.11.53.0 v3 snmptest")
            assert True
        else:
            print("\n Failure: Perform CLI show snmp variable command")
            assert False
 
    @pytest.mark.run(order=35)
    def test_034_perform_cli_command_on_snmp_after_configure_snmp_with_member(self):
        output=perform_cli_commands_on_snmp(config.grid_member1_vip,'show snmp variable sysName.0')

        if 'STRING: "sys_Name"' in output:
            print("\n Success: show snmp variable sysName.0 with member")
            assert True
        else:
            print("\n Failure: Perform CLI show snmp variable command with member")
            assert False
            
        output=perform_cli_commands_on_snmp(config.grid_member1_vip,'show snmp variable .1.3.6.1.4.1.2021.11.53.0')

        if 'UCD-SNMP-MIB::ssCpuRawIdle' in output:
            print("\n Success: show snmp variable .1.3.6.1.4.1.2021.11.53.0 with member")
            assert True
        else:
            print("\n Failure: Perform CLI show snmp variable command with member")
            assert False
            
        output=perform_cli_commands_on_snmp(config.grid_member1_vip,'show snmp variable sysName.0 v3 snmptest')
   
        if 'STRING: "sys_Name"' in output:
            print("\n Success: show snmp variable sysName.0 v3 snmptest with member")
            assert True
        else:
            print("\n Failure: Perform CLI show snmp variable command with member")
            assert False
            
        output=perform_cli_commands_on_snmp(config.grid_member1_vip,'show snmp variable .1.3.6.1.4.1.2021.11.53.0 v3 snmptest')
       
        if 'UCD-SNMP-MIB::ssCpuRawIdle' in output:
            print("\n Success: show snmp variable .1.3.6.1.4.1.2021.11.53.0 v3 snmptest with member")
            assert True
        else:
            print("\n Failure: Perform CLI show snmp variable command with member")
            assert False
              
               
    @pytest.mark.run(order=36)
    def test_035_disabling_DCA_service_before_enabling_DHCP(self):
        print("\n============================================\n")
        print("Disabling DNS cache acceleration services before start DHCP service ")
        print("\n============================================\n")
        data = {"enable_dns": False,"enable_dns_cache_acceleration": False}
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns?_return_fields=enable_dns_cache_acceleration", grid_vip=config.grid_vip)
        
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('PUT', object_type=ref['_ref'], fields=json.dumps(data))
            print(response)
            if type(response) == tuple:
                if response[0]==200:
                    print("Success: Stop DCA Service")
                    assert True
                else:
                    print("Failure: did not Stop DCA Service")
                    assert False
            if 'member:dns' in response:
                print("Success: Enable SNMP trap in the grid")
                assert True
            else:
                print("Failure: can not Enable SNMP trap in the grid")
                assert False  
                
        sleep(300)
        check_able_to_login_appliances(config.grid_vip)

    @pytest.mark.run(order=37)
    def test_036_validate_DCA_service_stop_working(self):
        print("\n============================================\n")
        print("Validate DCA Service stop working")
        print("\n============================================\n")
       
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns?_return_fields=enable_dns_cache_acceleration", grid_vip=config.grid_vip)
        print(get_ref)
        response1=json.loads(get_ref)
        print(response1)
        ref_obj = response1[0]['enable_dns_cache_acceleration']
        ref_obj1 = response1[1]['enable_dns_cache_acceleration']
        if ref_obj==False and ref_obj1==False:
            print("Validating DCA service stop running")
            assert True
        else:
            print("Failure: Validate DCA Service did not stop")
            assert False   
        
    @pytest.mark.run(order=38)
    def test_037_validate_snmpd_config_file(self):        
        print("\n============================================\n")
        print("Check the snmpd.conf file")
        print("\n============================================\n")
        getref = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        print(getref)
        snmpuser_name = json.loads(getref)[0]["name"]
                
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data="cat /etc/snmp/snmpd.conf"
        sleep(5)
        stdin, stdout, stderr = client.exec_command(data)
        sleep(2)
        stdout=stdout.read()
        stderr=stderr.read()
        print(data,stdout,stderr)
        if 'public' in stdout and config.grid_vip in stdout and snmpuser_name in stdout and config.client_ip in stdout:
            print("\nSuccess : Checking the snmpd.conf file\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: did not found required info in the snmpd.conf file\n\n")
            assert False
            
    @pytest.mark.run(order=39)
    def test_038_perform_snmpwalk_and_check_bad_operator_message_any(self):
        
        print("\n============================================\n")
        print("SNMP walk command on Threat Analytic Service description")
        print("\n============================================\n")
        
        client,stdout,stderr=perform_snmpwalk_command(config.grid_vip,"ibNodeServiceDesc.threat-analytics")
        
        if 'Bad operator (INTEGER):' in stderr:
            client.close()
            print("Failure: Got Bad operator (INTEGER) which is a bug :NIOS-87281")
            assert False        
        else:
            print("\nSuccess : did not get Bad operator (INTEGER)\n")
            client.close()
            assert True
  
    @pytest.mark.run(order=40)
    def test_039_enable_only_SNMPv1_v2_trap(self): 
        print("Enable only SNMPv1/v2 trap")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting')
        getref=json.loads(get_ref)[0]['_ref']
        print(getref)
        data={"snmp_setting":{"queries_enable":True,"queries_community_string":config.community_string,"trap_receivers":[{"address": config.trap_receiver_ip}],"traps_community_string":config.community_string,"traps_enable":True}}
        
        response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:
                print("Failure: Did not Enable SNMPV1/V2 trap on GRID-LEVEL ")
                assert False
            else:
                print("Sucess:Enable SNMPV1/V2 trap on GRID-LEVEL ")
        if 'grid' in response:
                print("Success: Enable SNMP trap in the grid")
                assert True
        else:
            print("Failure: can not Enable SNMP trap in the grid")
            assert False    
        sleep(20)  

    @pytest.mark.run(order=41)
    def test_040_validate_enable_only_SNMPv1_v2_trap(self):
        print("\n============================================\n")
        print("Validate SNMPv1/v2 trap enabled")
        print("\n============================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting', grid_vip=config.grid_vip)
        get_ref = json.loads(get_ref)
        print(get_ref)
        queries_en = get_ref[0]['snmp_setting']['queries_enable']
        traps_en = get_ref[0]['snmp_setting']['traps_enable']
        trap_add = get_ref[0]['snmp_setting']['trap_receivers'][0]['address']
        
        if queries_en==True and traps_en==True and trap_add==config.trap_receiver_ip:
            print("Validating snmpv1 and v2 Trap enabled")
            assert True
        else:
            print("Failure: Validate snmpv1 and v2 Trap not enabled")
            assert False 
            
    @pytest.mark.run(order=42)
    def test_041_disable_the_TP_service_before_FTP_service_start(self):
        print("\n============================================\n")
        print("Disable Threat protection Service before FTP service start")
        print("\n============================================\n")
       
        data = {"enable_service": False}
        response = ib_NIOS.wapi_request('GET',object_type="member:threatprotection")
        for ref in json.loads(response):
            print(ref['_ref'])
            response1 = ib_NIOS.wapi_request('PUT',object_type=ref['_ref'], fields=json.dumps(data))
            print(response1)
            
            print(response1)
            if type(response1) == tuple:
                if response1[0]==200:
                    print("Success: Start Threat protection Service")
                    assert True
                else:
                    print("Failure: Start Threat protection Service")
                    assert False
                    
            elif "member:threatprotection" in response:
                print("Success: Start Threat protection Service")
                assert True
                
        sleep(300)
        check_able_to_login_appliances(config.grid_vip)      

    @pytest.mark.run(order=43)
    def test_042_validate_the_TP_service_inactive(self):
        print("\n============================================\n")
        print("Validate Threat protection Service inactive")
        print("\n============================================\n")
       
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection?_return_fields=enable_service", grid_vip=config.grid_vip)
        print(get_ref)
        response1=json.loads(get_ref)
        print(response1)
        ref_obj = response1[1]['enable_service']
        if ref_obj==False:
            print("Validating threat protection service is not running ")
            assert True
        else:
            print("Failure: Validating threat protection inactive is working ot not")
            assert False
        
    @pytest.mark.run(order=44)
    def test_043_perform_SNMP_trap_reciever_on_V1_v2(self):
        print("\n============================================\n")
        print("SNMPV1/V2 Trap reciever on IPV4")
        print("\n============================================\n")
        track_snmp_traps(config.trap_receiver_ip,'snmptrapd -f -C -c /etc/snmp/snmptrapd.conf -Le','snmptrapv2.txt')
        
        print("\n============================================\n")
        print("SNMPV1/V2 Trap reciever on IPV6")
        print("\n============================================\n")
        track_snmp_traps(config.trap_receiver_ip,'snmptrapd udp6:162,udp:162 -f -C -c /etc/snmp/snmptrapd.conf -Le','snmptrapv2.txt')

    @pytest.mark.run(order=45)
    def test_044_enable_only_SNMPV3_trap(self): 
        print("\n\nEnable only SNMPv3 trap")
        response = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmp_memref = json.loads(response)[0]['_ref']
        snmp_memref = snmp_memref.encode('ascii', 'ignore')
        print(snmp_memref)
        
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting')
        getref=json.loads(get_ref)[0]['_ref']
        print(getref)
        data={"snmp_setting":{"snmpv3_traps_enable": True,"snmpv3_queries_enable": True,"snmpv3_queries_users": [{"user":snmp_memref}],"trap_receivers":[{"address": config.trap_receiver_ip,"user":snmp_memref}]}}

        response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:
                print("Failure: \n Did not Enable SNMPV3 trap on GRID-LEVEL ")
                assert False
        else:
            print("Sucess: \n Enable SNMPV3 trap on GRID-LEVEL ")
            
        sleep(20)  

    @pytest.mark.run(order=46)
    def test_045_validate_enable_only_SNMPv3_trap(self):
        print("\n============================================\n")
        print("Validate SNMPv3 trap enabled")
        print("\n============================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting', grid_vip=config.grid_vip)
        get_ref = json.loads(get_ref)
        print(get_ref)
        v3trap_en = get_ref[0]['snmp_setting']['snmpv3_traps_enable']
        v3q_user = get_ref[0]['snmp_setting']['snmpv3_queries_users'][0]['user']['name']
        trap_add = get_ref[0]['snmp_setting']['trap_receivers'][0]['address']
        print(trap_add)
        if v3trap_en==True and 'snmptest' == v3q_user and trap_add==config.trap_receiver_ip:
            print("Validating snmpv3 Trap enabled")
            assert True
        else:
            print("Failure: Validate snmpv3 Trap not enabled")
            assert False     
     
    @pytest.mark.run(order=47)
    def test_046_change_snmptrapd_config_file_for_snmpv3(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting', grid_vip=config.grid_vip)
        get_ref = json.loads(get_ref)
        
        engine_id = get_ref[0]['snmp_setting']['engine_id']
        engine_id=str(engine_id[0])
        print(engine_id)
        new_en_id = engine_id.replace(":", "" )
        new_en_id = '0x'+new_en_id
        print(new_en_id)
        string_up1='createUser -e '+new_en_id+' snmptest SHA infoblox1 AES infoblox1'
        string_up2='authUser log,execute,net snmp3'
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.trap_receiver_ip)
        print(config.trap_receiver_ip)
        try:
            child.expect('password:')
            
            child.sendline('infoblox')
            child.expect('$')

            sleep(2)
            child.logfile=sys.stdout
            
            child.sendline('echo "'+string_up1+'" | tee -a /etc/snmp/snmptrapd.conf')
            child.expect('$')
            child.sendline('echo "'+string_up2+'" | tee -a /etc/snmp/snmptrapd.conf')
            child.expect('$')
    
        except Exception as e:
            child.close()
            print("Failure: to change config file ")
            print(e)
            assert False
        
    @pytest.mark.run(order=48)
    def test_047_perform_SNMP_trap_reciever_on_V3(self):
        print("\n============================================\n")
        print("SNMPV3 Trap reciever on IPV4")
        print("\n============================================\n")
        track_snmp_traps(config.trap_receiver_ip,'snmptrapd -f -C -c /etc/snmp/snmptrapd.conf -Le','snmptrapv3.txt')
        
        print("\n============================================\n")
        print("SNMPV3 Trap reciever on IPV6")
        print("\n============================================\n")
        track_snmp_traps(config.trap_receiver_ip,'snmptrapd udp6:162,udp:162 -f -C -c /etc/snmp/snmptrapd.conf -Le','snmptrapv3.txt')

    
    @pytest.mark.run(order=49)
    def test_048_validate_snmp_config_file(self):        
        print("\n============================================\n")
        print("Check the snmpd.conf file")
        print("\n============================================\n")
        getref = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        print(getref)
        snmpuser_name = json.loads(getref)[0]["name"]
                
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data="cat /etc/snmp/snmp.conf"
        sleep(5)
        stdin, stdout, stderr = client.exec_command(data)
        sleep(2)
        stdout=stdout.read()
        stderr=stderr.read()
        print(data,stdout,stderr)
        if config.grid_vip in stdout:
            print("\nSuccess : Checking the snmpd.conf file\n")
            client.close()
            assert True
        else:
            client.close()
            print("Failure: did not found required info in the snmpd.conf file\n\n")
            assert False
     

    @pytest.mark.run(order=50)
    def test_049_after_override_SNMP_settings_at_member_level(self):   
        response = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmp_memref = json.loads(response)[0]['_ref']
        snmp_memref = snmp_memref.encode('ascii', 'ignore')
        print(snmp_memref)
        
        response = ib_NIOS.wapi_request('GET', object_type="member?host_name="+config.grid_member1_fqdn)
        memref = json.loads(response)[0]['_ref']
        print(memref)
       
        data={"use_snmp_setting":True,"snmp_setting":{"syscontact": ["sys_Contact"],"sysdescr": ["sys_Descr"],"syslocation": ["sys_Location"],"sysname": ["sys_Name"],"snmpv3_traps_enable": True,"snmpv3_queries_enable": True,"snmpv3_queries_users": [{"user":snmp_memref}],"queries_enable":True,"queries_community_string":config.community_string,"trap_receivers":[{"address": config.trap_receiver_ip},{"address": config.client_ip,"user":snmp_memref}],"traps_community_string":config.community_string,"traps_enable":True}}
        
        response=ib_NIOS.wapi_request('PUT',ref=memref, fields=json.dumps(data))
        print(response)
        if type(response) == tuple:

            if response[0]==200:
                print("\n Success: Enable SNMP configuration on member level")
                assert False
            else:
                print("Failure: Enable SNMP configuration on member level")
                assert True

    @pytest.mark.run(order=51)
    def test_050_validate_snmpv1_2_3_trap_enabled_on_grid_level(self):
        print("\n============================================\n")
        print("Validate SNMPV3 TRAPs on member")
        print("\n============================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=snmp_setting', grid_vip=config.grid_vip)
        print(get_ref)
        get_ref = json.loads(get_ref)
        
       
        trap_add1 = get_ref[2]['snmp_setting']['trap_receivers'][0]['address']
        v3trap_en = get_ref[2]['snmp_setting']['snmpv3_traps_enable']
        v3q_user = get_ref[2]['snmp_setting']['snmpv3_queries_users'][0]['user']['name']
        trap_add = get_ref[2]['snmp_setting']['trap_receivers'][1]['address']
        print(trap_add)
        if v3trap_en==True and 'snmptest' == v3q_user and trap_add==config.client_ip and trap_add1==config.trap_receiver_ip:
            print("Validating snmpv1, v2, v3 Trap enabled at member level")
            assert True
        else:
            print("Failure: Validate snmpv1, v2, v3 Trap not enabled at member level")
            assert False
            
    @pytest.mark.run(order=52)
    def test_051_perform_snmp_command_at_member_level(self):
        print("\n============================================\n")
        print("SNMPGET command on v1, v2, v3 with member after override SNMP settings at member level ")
        print("\n============================================\n")
        
        ''' sysDescr '''
        
        client,stdout_v1,stderr=perform_snmp_command_on_v1("snmpget",config.grid_member1_vip,"sysDescr.0")
       
        client,stdout_v2,stderr=perform_snmp_command_on_v2("snmpget",config.grid_member1_vip,"sysDescr.0")
        
        client,stdout_v3,stderr=perform_snmp_command_on_v3("snmpget",config.grid_member1_vip,"sysDescr.0")
        
        validate_snmp_command_on_v1(stdout_v1,'STRING: sys_Descr',"SNMPGET",client,"member")
        validate_snmp_command_on_v2(stdout_v2,'STRING: sys_Descr',"SNMPGET",client,"member")
        validate_snmp_command_on_v3(stdout_v3,'STRING: sys_Descr',"SNMPGET",client,"member")
		
		
        print("\n============================================\n")
        print("SNMPGETNEXT command on v1, v2, v3 with member")
        print("\n============================================\n")
        
        client,stdout_v1,stderr=perform_snmp_command_on_v1("snmpgetnext",config.grid_member1_vip,"-m all ibNiosVersion.0")
        
        client,stdout_v2,stderr=perform_snmp_command_on_v2("snmpgetnext",config.grid_member1_vip,"-m all ibNiosVersion.0")
        
        client,stdout_v3,stderr=perform_snmp_command_on_v3("snmpgetnext",config.grid_member1_vip,"-m all ibNiosVersion.0")
        
        validate_snmp_command_on_v1(stdout_v1,'ibSystemMonitorCpuUsage.0 = INTEGER:',"SNMPGETNEXT",client,"member")
        validate_snmp_command_on_v2(stdout_v2,'ibSystemMonitorCpuUsage.0 = INTEGER:',"SNMPGETNEXT",client,"member")
        validate_snmp_command_on_v3(stdout_v3,'ibSystemMonitorCpuUsage.0 = INTEGER:',"SNMPGETNEXT",client,"member")
        
		
        print("\n============================================\n")
        print("SNMPBULKGET command on v1-not supported v2,v3 supported with member")
        print("\n============================================\n")

        client,stdout_v2,stderr=perform_snmp_command_on_v2("snmpbulkget",config.grid_member1_vip,"-t 5 "+config.OID)
        
        client,stdout_v3,stderr=perform_snmp_command_on_v3("snmpbulkget",config.grid_member1_vip,"-t 5 "+config.OID)
        
        validate_snmp_command_on_v2(stdout_v2,'hrSWRunPerfCPU',"SNMPBULKGET",client,"member")
        validate_snmp_command_on_v3(stdout_v3,'hrSWRunPerfCPU',"SNMPBULKGET",client,"member")
		
		
        print("\n============================================\n")
        print("SNMPTABLE command on snmpv1, v2, v3 with member")
        print("\n============================================\n")
        
        client,stdout_v1,stderr=perform_snmp_command_on_v1("snmptable",config.grid_member1_vip," -m ALL -M+/usr/share/snmp/mibs/ IB-PLATFORMONE-MIB::ibMemberServiceStatusTable")
        
        client,stdout_v2,stderr=perform_snmp_command_on_v2("snmptable",config.grid_member1_vip," -m ALL -M+/usr/share/snmp/mibs/ IB-PLATFORMONE-MIB::ibMemberServiceStatusTable")
        
        client,stdout_v3,stderr=perform_snmp_command_on_v3("snmptable",config.grid_member1_vip," -m ALL -M+/usr/share/snmp/mibs/ IB-PLATFORMONE-MIB::ibMemberServiceStatusTable")
        
        validate_snmp_command_on_v1(stdout_v1,'FTP Service is inactive',"SNMPTABLE",client,"member")
        validate_snmp_command_on_v2(stdout_v2,'FTP Service is inactive',"SNMPTABLE",client,"member")
        validate_snmp_command_on_v3(stdout_v3,'FTP Service is inactive',"SNMPTABLE",client,"member")

    
    @pytest.mark.run(order=53)
    def test_052_create_an_different_SNMPv3_Users(self):
       print("Create an SNMPv3 User1")
       
       data={"name":"snmpUser1","authentication_protocol":"NONE","privacy_protocol":"NONE"}

       response = ib_NIOS.wapi_request('POST',object_type="snmpuser",fields=json.dumps(data))
       print(response)
       
       if type(response) == tuple:           
           if response[0]==200:  
               print("\n Success: Created SNMPv3 User1\n")
               assert True
           else:
               print("\n Failure: Create SNMPv3 User1\n")
               assert False 
       
       print("Create an SNMPv3 User2")

       data={"name":"snmpUser2","authentication_protocol":"MD5","privacy_protocol":"NONE","authentication_password":"infoblox1"}

       response = ib_NIOS.wapi_request('POST',object_type="snmpuser",fields=json.dumps(data))
       print(response)
       
       if type(response) == tuple:           
           if response[0]==200:  
               print("\n Success: Created SNMPv3 User2\n")
               assert True
           else:
               print("\n Failure: Create SNMPv3 User2\n")
               assert False
               
       print("Create an SNMPv3 User3")

       data={"name":"snmpUser3","authentication_protocol":"MD5","privacy_protocol":"DES","privacy_password":"infoblox1","authentication_password":"infoblox1"}

       response = ib_NIOS.wapi_request('POST',object_type="snmpuser",fields=json.dumps(data))
       print(response)
       
       if type(response) == tuple:           
           if response[0]==200:  
               print("\n Success: Created SNMPv3 User3\n")
               assert True
           else:
               print("\n Failure: Create SNMPv3 User3\n")
               assert False

    @pytest.mark.run(order=54)
    def test_053_validate_created_an_SNMPv3_User(self):
        print("\n============================================\n")
        print("Validate SNMPV3 user created")
        print("\n============================================\n")

        getref = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        for ref in json.loads(getref):
            print(ref['name'])

            if 'snmpUser1' in ref['name']:
                print("Sucess: Validating SNMPV3 user 'snmpUser1' created")
                assert True
            elif 'snmpUser2' in ref['name']:
                print("Sucess: Validating SNMPV3 user 'snmpUser2' created")
                assert True
            elif 'snmpUser3' in ref['name']:
                print("Sucess: Validating SNMPV3 user 'snmpUser3' created")
                assert True
            elif 'snmptest' in ref['name']:
                print("Sucess: Validating SNMPV3 user 'snmptest' created")
                assert True
            else:
                print("Failure: Validate SNMPV3 user "+ref['name']+" not created")
                assert False     
            
    @pytest.mark.run(order=55)
    def test_054_add_SNMPv3_Users_to_the_grid(self):
        response = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmp_memref = json.loads(response)[0]['_ref']
        snmp_memref = snmp_memref.encode('ascii', 'ignore')
        print(snmp_memref)
        snmp_memref1=''
        snmp_memref2=''
        snmp_memref3=''
        snmp_memref4=''
        for ref in json.loads(response):
            #print(ref['_ref'])
            if 'snmpUser1' in ref['_ref']:
                snmp_memref1=ref['_ref']
                snmp_memref1 = snmp_memref1.encode('ascii', 'ignore')
            elif 'snmpUser2' in ref['_ref']:
                snmp_memref2=ref['_ref']
                snmp_memref2 = snmp_memref2.encode('ascii', 'ignore')
            elif 'snmpUser3' in ref['_ref']:
                snmp_memref3=ref['_ref']
                snmp_memref3 = snmp_memref3.encode('ascii', 'ignore')
            elif 'snmptest' in ref['_ref']:
                snmp_memref4=ref['_ref']
                snmp_memref4 = snmp_memref4.encode('ascii', 'ignore')
        
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid?_return_fields=snmp_setting")

        for ref in json.loads(get_ref):
            print(ref['_ref'])
            data={"snmp_setting":{"syscontact": ["sys_Contact"],"sysdescr": ["sys_Descr"],"syslocation": ["sys_Location"],"sysname": ["sys_Name"],"snmpv3_traps_enable": True,"snmpv3_queries_enable": True,"snmpv3_queries_users": [{"user":snmp_memref4},{"user":snmp_memref1},{"user":snmp_memref2},{"user":snmp_memref3}],"queries_enable":True,"queries_community_string":config.community_string,"trap_receivers":[{"address": config.trap_receiver_ip},{"address": config.client_ip,"user":snmp_memref}],"traps_community_string":config.community_string,"traps_enable":True}}
            print(data)
            response = ib_NIOS.wapi_request('PUT',ref=ref['_ref'], fields=json.dumps(data))
            print(response)
            
            if type(response) == tuple:

                if response[0]==200:
                    print("\n Success: add all SNMP user to SNMP configuration on grid")
                    assert True
                else:
                    print("Failure: did not add all SNMP user to SNMP configuration on grid")
                    assert False
            else:
                print("\n Success: add all SNMP user to SNMP configuration on grid")
                assert True
    
    @pytest.mark.run(order=56)
    def test_055_perform_snmp_V3_commands_on_4_scenarios(self): 
        print("\n============================================\n")
        print("SNMPWALK command on SNMP v3")
        print("\n============================================\n")
        
        client,stdout_v3,stderr=Having_No_Authentication_Password_and_No_Privacy_Password("snmpwalk",config.grid_vip,'|grep "Threat Analytics"') 
        
        if 'STRING: "Threat Analytics"' in stdout_v3:
            print("Success: Validating SNMPV3 Having No Authentication Password & No Privacy Password")
            assert True
        else:
            print("Failure: Validate SNMPV3 usernot  Having No Authentication Password & No Privacy Password")
            assert False
        
        client,stdout_v3,stderr=Having_Authentication_Password_No_Privacy_Password("snmpwalk",config.grid_vip,'|grep "Threat Analytics"')
        
        if 'STRING: "Threat Analytics"' in stdout_v3:
            print("Success: Validating SNMPV3 user not Having Authentication Password & No Privacy Password")
            assert True
        else:
            print("Failure: "+stderr)
            
            assert False
            
        client,stdout_v3,stderr=Having_Authentication_Password_Privacy_Password("snmpwalk",config.grid_vip,'|grep "Threat Analytics"')
        
        if 'STRING: "Threat Analytics"' in stdout_v3:
            print("Success: Validating SNMPV3 user Having Authentication Password & Privacy Password")
            assert True
        else:
            print("Failure: Validate SNMPV3 user not Having Authentication Password & Privacy Password")
            assert False
        
        print("\n============================================\n")
        print("SNMPGET command on SNMP v3")
        print("\n============================================\n")
        child1 = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        try:
            child1.logfile=sys.stdout
            child1.expect('password:')
            child1.sendline('infoblox')
            child1.expect('Infoblox >')
            child1.sendline('show version')
            child1.expect('Infoblox >')
            
            output= child1.before
            child1.close()
        except Exception as e:
            child1.close()
            print("\n Failure: error in executing snmp comand")
            print("\n================Error====================\n")
            print(e)
            assert False        
               
        
        version=output.split('-')[0].split(':')[1].strip()
        print(version)
        client,stdout_v3,stderr=Having_No_Authentication_Password_and_No_Privacy_Password("snmpget",config.grid_vip,config.OID_v3) 
        
        if 'ibNiosVersion.0 = STRING: '+version in stdout_v3:
            print("Validating SNMPV3 Having No Authentication Password & No Privacy Password")
            assert True
        else:
            print("Failure: Validate SNMPV3 user not Having No Authentication Password & No Privacy Password")
            assert False
        
        client,stdout_v3,stderr=Having_Authentication_Password_No_Privacy_Password("snmpget",config.grid_vip,config.OID_v3)
        
        if 'ibNiosVersion.0 = STRING: '+version in stdout_v3:
            print("Validating SNMPV3 user Having Authentication Password & No Privacy Password")
            assert True
        else:
            print("Failure: Validate SNMPV3 user not Having Authentication Password & No Privacy Password")
            assert False
        client,stdout_v3,stderr=Having_Authentication_Password_Privacy_Password("snmpget",config.grid_vip,config.OID_v3)
        
        if 'ibNiosVersion.0 = STRING: '+version in stdout_v3:
            print("Validating SNMPV3 user Having Authentication Password & Privacy Password")
            assert True
        else:
            print("Failure: Validate SNMPV3 user not Having Authentication Password & Privacy Password")
            assert False
        
        print("\n============================================\n")
        print("SNMPGETNEXT command on SNMP v3")
        print("\n============================================\n")
        
        client,stdout_v3,stderr=Having_No_Authentication_Password_and_No_Privacy_Password("snmpgetnext",config.grid_vip,config.OID_v3) 
        
        if 'ibSystemMonitorCpuUsage.0 = INTEGER:' in stdout_v3:
            print("Validating SNMPV3 Having No Authentication Password & No Privacy Password")
            assert True
        else:
            print("Failure: Validate SNMPV3 user not Having No Authentication Password & No Privacy Password")
            assert False
        
        client,stdout_v3,stderr=Having_Authentication_Password_No_Privacy_Password("snmpgetnext",config.grid_vip,config.OID_v3)
        
        if 'ibSystemMonitorCpuUsage.0 = INTEGER:' in stdout_v3:
            print("Validating SNMPV3 user Having Authentication Password & No Privacy Password")
            assert True
        else:
            print("Failure: Validate SNMPV3 user not Having Authentication Password & No Privacy Password")
            assert False
        client,stdout_v3,stderr=Having_Authentication_Password_Privacy_Password("snmpgetnext",config.grid_vip,config.OID_v3)
        
        if 'ibSystemMonitorCpuUsage.0 = INTEGER:' in stdout_v3:
            print("Validating SNMPV3 user Having Authentication Password & Privacy Password")
            assert True
        else:
            print("Failure: Validate SNMPV3 user not Having Authentication Password & Privacy Password")
            assert False
        
        print("\n============================================\n")
        print("SNMPBULKGET command on SNMP v3")
        print("\n============================================\n")
        
        client,stdout_v3,stderr=Having_No_Authentication_Password_and_No_Privacy_Password("snmpbulkget",config.grid_vip,config.OID_v3) 
        
        if 'ibSystemMonitorCpuUsage.0 = INTEGER' in stdout_v3:
            print("Validating SNMPV3 Having No Authentication Password & No Privacy Password")
            assert True
        else:
            print("Failure: Validate SNMPV3 user not Having No Authentication Password & No Privacy Password")
            assert False
        
        client,stdout_v3,stderr=Having_Authentication_Password_No_Privacy_Password("snmpbulkget",config.grid_vip,config.OID_v3)
        
        if 'ibSystemMonitorCpuUsage.0 = INTEGER' in stdout_v3:
            print("Validating SNMPV3 user Having Authentication Password & No Privacy Password")
            assert True
        else:
            print("Failure: Validate SNMPV3 user not Having Authentication Password & No Privacy Password")
            assert False
        client,stdout_v3,stderr=Having_Authentication_Password_Privacy_Password("snmpbulkget",config.grid_vip,config.OID_v3)
        
        if 'ibSystemMonitorCpuUsage.0 = INTEGER' in stdout_v3:
            print("Validating SNMPV3 user Having Authentication Password & Privacy Password")
            assert True
        else:
            print("Failure: Validate SNMPV3 user not Having Authentication Password & Privacy Password")
            assert False
        
        print("\n============================================\n")
        print("SNMPTABLE command on SNMP v3")
        print("\n============================================\n")
        
        
        client,stdout_v3,stderr=Having_No_Authentication_Password_and_No_Privacy_Password("snmptable",config.grid_vip,'-M+/usr/share/snmp/mibs/ .1.3.6.1.4.1.7779.3.1.1.2.1.10') 
        
        if 'Threat Analytics Service is working' in stdout_v3:
            print("Validating SNMPV3 Having No Authentication Password & No Privacy Password")
            assert True
        else:
            print("Failure: Validate SNMPV3 user not Having No Authentication Password & No Privacy Password")
            assert False
        
        client,stdout_v3,stderr=Having_Authentication_Password_No_Privacy_Password("snmptable",config.grid_vip,'-M+/usr/share/snmp/mibs/ .1.3.6.1.4.1.7779.3.1.1.2.1.10')
        
        if 'Threat Analytics Service is working' in stdout_v3:
            print("Validating SNMPV3 user Having Authentication Password & No Privacy Password")
            assert True
        else:
            print("Failure: Validate SNMPV3 user not Having Authentication Password & No Privacy Password")
            assert False
        client,stdout_v3,stderr=Having_Authentication_Password_Privacy_Password("snmptable",config.grid_vip,'-M+/usr/share/snmp/mibs/ .1.3.6.1.4.1.7779.3.1.1.2.1.10')
        
        if 'Threat Analytics Service is working' in stdout_v3:
            print("Validating SNMPV3 user Having Authentication Password & Privacy Password")
            assert True
        else:
            print("Failure: Validate SNMPV3 user not Having Authentication Password & Privacy Password")
            assert False
            
                 
    @pytest.mark.run(order=57)
    def test_056_check_SNMPV3_engineboot_values_on_HA_member(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="member?host_name="+config.grid_member2_fqdn)
        get_ref=json.loads(get_ref)
        memref = get_ref[0]['_ref']
        print(memref)
        print("\n============================================\n")
        print("Get Engine value to check it before changes")
        print("\n============================================\n")
        print(config.grid_member2_vip)
        eng_value = get_engineboot_value(config.grid_member2_vip)
        
        print("\nEnbale SNMPV3 trap and check enginee boot value")
        print("\n============================================\n")
        
        enable_SNMPV3_trap(memref)
        sleep(60)
        check_engineboot_has_been_incremented(config.grid_member2_vip,eng_value)
        
        print("\n============================================\n")
        print("Get Engine value to check it before changes")
        print("\n============================================\n")
        
        eng_value = get_engineboot_value(config.grid_member2_vip)
        
        print("\n============================================\n")
        print("Disable SNMPV3 trap and check enginee boot value")
        print("\n============================================\n")
        
        disable_SNMPV3_trap(memref)
        sleep(30)
        check_engineboot_has_been_incremented(config.grid_member2_vip,eng_value)
        
        print("\n============================================\n")
        print("Get Engine value to check it before changes")
        print("\n============================================\n")
        eng_value = get_engineboot_value(config.grid_member2_vip)
        
        print("\n============================================\n")
        
        print("Enbale SNMPV3 trap and check enginee boot value")
        print("\n============================================\n")
        
        enable_SNMPV3_trap(memref)
        sleep(60)
        check_engineboot_has_been_incremented(config.grid_member2_vip,eng_value)
        
        print("\n============================================\n")
        print("Get Engine value to check it before changes")
        print("\n============================================\n")
        
        eng_value = get_engineboot_value(config.grid_member2_vip)
        
        print("\n============================================\n")
        print("Disable SNMPV3 trap and check enginee boot value")
        print("\n============================================\n")
        
        disable_SNMPV3_trap(memref)
        sleep(30)
        check_engineboot_has_been_incremented(config.grid_member2_vip,eng_value)
        
        
    @pytest.mark.run(order=58)
    def test_057_reboot_SA_and_HA_member_check_engine_value_disable_snmpv3_trap(self):
        print("\n============================================\n")
        print("Reboot active and passive node check Engineboot values, on HA member ")
        print("\n============================================\n")
                
        print("Get Engine value to check it before changes")
        print("\n============================================\n")
        
        eng_value = get_engineboot_value(config.grid_member1_vip)
        
        print("\n============================================\n")
        print("reboot SA member, check engineeboot value")
        print("\n============================================\n")
        
        reboot_node(config.grid_member1_vip)
        check_engineboot_has_been_incremented(config.grid_member1_vip,eng_value)
        
        print("\n============================================\n")
        print("Get Engine value to check it before changes")
        print("\n============================================\n")
        
        eng_value = get_engineboot_value(config.grid_member3_vip)
        
        print("\n============================================\n")
        print("reboot active node, check engineeboot value")
        print("\n============================================\n")
        
        reboot_node(config.grid_member3_vip)
        
        check_engineboot_has_been_incremented(config.grid_member3_vip,eng_value)
        
        print("\n============================================\n")
        print("Get Engine value to check it before changes")
        print("\n============================================\n")
        
        eng_value = get_engineboot_value(config.grid_member4_vip)
        
        print("\n============================================\n")
        print("reboot passive node, check engineeboot value ")
        print("\n============================================\n")
        
        reboot_node(config.grid_member4_vip)
        
        check_engineboot_has_been_incremented(config.grid_member4_vip,eng_value)

    @pytest.mark.run(order=59)
    def test_058_reboot_SA_and_HA_member_check_engine_value_enable_snmpv3_trap(self):
        print("\n============================================\n")
        print("Reboot active and passive node check Engineboot values, on HA member ")
        print("\n============================================\n")
        
        get_ref = ib_NIOS.wapi_request('GET', object_type="member?host_name="+config.grid_member2_fqdn)
        get_ref=json.loads(get_ref)
        memref = get_ref[0]['_ref']
        print(memref)
        enable_SNMPV3_trap(memref)
        
        print("Get Engine value to check it before changes")
        print("\n============================================\n")
        
        eng_value = get_engineboot_value(config.grid_member1_vip)
        
        print("\n============================================\n")
        print("reboot SA member, check engineeboot value")
        print("\n============================================\n")
        
        reboot_node(config.grid_member1_vip)
        check_engineboot_has_been_incremented(config.grid_member1_vip,eng_value)
        
        print("\n============================================\n")
        print("Get Engine value to check it before changes")
        print("\n============================================\n")
        
        eng_value = get_engineboot_value(config.grid_member3_vip)
        
        print("\n============================================\n")
        print("reboot active node, check engineeboot value")
        print("\n============================================\n")
        
        reboot_node(config.grid_member3_vip)
        
        check_engineboot_has_been_incremented(config.grid_member3_vip,eng_value)
        
        print("\n============================================\n")
        print("Get Engine value to check it before changes")
        print("\n============================================\n")
        
        eng_value = get_engineboot_value(config.grid_member4_vip)
        
        print("\n============================================\n")
        print("reboot passive node, check engineeboot value ")
        print("\n============================================\n")
        
        reboot_node(config.grid_member4_vip)
        
        check_engineboot_has_been_incremented(config.grid_member4_vip,eng_value)
                
    @pytest.mark.run(order=60)
    def test_059_check_Test_SNMP_WAPI_support_available(self):
        print("\n============================================\n")
        print("Check Test SNMP WAPI support available or not ")
        print("\n============================================\n")
        try:
            get_ref = ib_NIOS.wapi_request('GET', object_type='test_snmp', grid_vip=config.grid_vip)
            print(get_ref)
            get_ref = json.loads(get_ref)
            print("Success: Test SNMP WAPI support available")
            assert True
        
        except Exception as e:
            print(e)
            print("Failure: Test SNMP WAPI support not available, Open bug: NIOS-69552")
            assert False
            
    @pytest.mark.run(order=61)
    def test_060_enable_only_SNMPv1_v2_trap(self): 
        print("Enable only SNMPv1/v2 trap")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member?host_name="+config.grid_member1_fqdn)
        getref=json.loads(get_ref)[0]['_ref']
        print(getref)
        data={"snmp_setting":{"queries_enable":True,"queries_community_string":config.community_string,"trap_receivers":[{"address": config.trap_receiver_ip},{"address": config.trap_receiver_ipv6}],"traps_community_string":config.community_string,"traps_enable":True}}
        
        response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:
                print("Failure: Did not Enable SNMPV1/V2 trap on GRID-LEVEL ")
                assert False
            else:
                print("Sucess:Enable SNMPV1/V2 trap on GRID-LEVEL ")
        if 'member' in response:
                print("Success: Enable SNMP trap in the grid")
                assert True
        else:
            print("Failure: can not Enable SNMP trap in the grid")
            assert False    
        sleep(20)  

    @pytest.mark.run(order=62)
    def test_061_validate_enable_only_SNMPv1_v2_trap(self):
        print("\n============================================\n")
        print("Validate SNMPv1/v2 trap enabled")
        print("\n============================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=snmp_setting', grid_vip=config.grid_vip)
        get_ref = json.loads(get_ref)
        print(get_ref)
        queries_en = get_ref[2]['snmp_setting']['queries_enable']
        traps_en = get_ref[2]['snmp_setting']['traps_enable']
        trap_add = get_ref[2]['snmp_setting']['trap_receivers'][0]['address']
        trap_add_ipv6 = get_ref[2]['snmp_setting']['trap_receivers'][1]['address']
        if queries_en==True and traps_en==True and trap_add==config.trap_receiver_ip and trap_add_ipv6==config.trap_receiver_ipv6:
            print("Validating snmpv1 and v2 Trap enabled")
            assert True
        else:
            print("Failure: Validate snmpv1 and v2 Trap not enabled")
            assert False 
			
    @pytest.mark.run(order=63)
    def test_062_perform_SNMP_trap_ipv6_reciever_only_with_SNMPV1_V2(self):
        
        print("\n============================================\n")
        print("SNMPV1/V2 Trap reciever on IPV6")
        print("\n============================================\n")
        
        track_snmp_traps(config.trap_receiver_ipv6,'snmptrapd udp6:162,udp:162 -f -C -c /etc/snmp/snmptrapd.conf -Le','snmptrapv2.txt')

    @pytest.mark.run(order=64)
    def test_063_enable_only_SNMPV3_trap(self): 
        print("\n\nEnable only SNMPv3 trap")
        response = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        snmp_memref = json.loads(response)[0]['_ref']
        snmp_memref = snmp_memref.encode('ascii', 'ignore')
        print(snmp_memref)
        
        get_ref = ib_NIOS.wapi_request('GET', object_type="member?host_name="+config.grid_member1_fqdn)
        getref=json.loads(get_ref)[0]['_ref']
        print(getref)
        data={"snmp_setting":{"snmpv3_traps_enable": True,"snmpv3_queries_enable": True,"snmpv3_queries_users": [{"user":snmp_memref}],"trap_receivers":[{"address": config.trap_receiver_ipv6,"user":snmp_memref}]}}

        response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:
                print("Failure: \n Did not Enable SNMPV3 trap on GRID-LEVEL ")
                assert False
        else:
            print("Sucess: \n Enable SNMPV3 trap on GRID-LEVEL ")
            
        sleep(20)  

    @pytest.mark.run(order=65)
    def test_064_validate_enable_only_SNMPv3_trap(self):
        print("\n============================================\n")
        print("Validate SNMPv3 trap enabled")
        print("\n============================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=snmp_setting', grid_vip=config.grid_vip)
        get_ref = json.loads(get_ref)
        print(get_ref)
        v3trap_en = get_ref[2]['snmp_setting']['snmpv3_traps_enable']
        v3q_user = get_ref[2]['snmp_setting']['snmpv3_queries_users'][0]['user']['name']
        
        trap_add_ipv6 = get_ref[2]['snmp_setting']['trap_receivers'][0]['address']
        print(trap_add_ipv6)
        if v3trap_en==True and 'snmptest' == v3q_user and trap_add_ipv6==config.trap_receiver_ipv6:
            print("Validating snmpv3 Trap enabled")
            assert True
        else:
            print("Failure: Validate snmpv3 Trap not enabled")
            assert False     

    @pytest.mark.run(order=66)
    def test_065_perform_SNMP_ipv6_trap_reciever_on_V3(self):
        
        print("\n============================================\n")
        print("SNMPV3 Trap reciever on IPV6")
        print("\n============================================\n")
        track_snmp_traps(config.trap_receiver_ipv6,'snmptrapd udp6:162,udp:162 -f -C -c /etc/snmp/snmptrapd.conf -Le','snmptrapv3.txt')

    @pytest.mark.run(order=67)
    def test_066_Taking_Grid_Backup_File(self):
        print("Taking Grid Backup file")
        data = {"type": "BACKUP"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=getgriddata",grid_vip=config.grid_vip)
        response = json.loads(response)
        token_of_GM = response['token']
        token_of_URL = response['url']
        curl_download='curl -k -u admin:infoblox -H  "content-type: application/force-download" '+token_of_URL+' -o "database.bak"'
        os.system(curl_download)
        print(token_of_GM)
        print(token_of_URL)
        x = os.listdir(".")
        print(x)
        if 'database.bak' in x:
            print("Success: File dowloaded successfully")
            assert True
        else:
            print("Failure: File did not dowloaded")
            assert False
            
    @pytest.mark.run(order=68)
    def test_067_Restore_Grid_Backup_File(self):
        print("Restore_Grid_Backup_File")
        log("start","/infoblox/var/infoblox.log", config.grid_vip)
        response = ib_NIOS.wapi_request('POST', object_type="fileop",params="?_function=uploadinit",grid_vip=config.grid_vip)
        response = json.loads(response)
        print(response)
        token_of_GM = response['token']
        token_of_URL = response['url']
        curl_upload='curl -k -u admin:infoblox -H "content-typemultipart-formdata" '+token_of_URL+' -F file=@database.bak'
        os.system(curl_upload)
        print(curl_upload)
        data = {"mode": "FORCED", "token": token_of_GM}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=restoredatabase",grid_vip=config.grid_vip)
        sleep(240)
        check_able_to_login_appliances(config.grid_vip)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        sleep(120)
        check_master=commands.getoutput(" grep -cw \".*restore_node complete.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
        if (int(check_master)!=0):
            assert True
        else:
            assert False
        sleep(60)
        

    @pytest.mark.run(order=69)
    def test_068_validate_snmpv_configuration_after_grid_restore(self):
        print("\n============================================\n")
        print("Validate SNMPV configurations after grid restore")
        print("\n============================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=snmp_setting', grid_vip=config.grid_vip)
        print(get_ref)
        get_ref = json.loads(get_ref)
        v3trap_en = get_ref[2]['snmp_setting']['snmpv3_traps_enable']
        v3q_user = get_ref[2]['snmp_setting']['snmpv3_queries_users'][0]['user']['name']
        
        trap_add_ipv6 = get_ref[2]['snmp_setting']['trap_receivers'][0]['address']
        print(trap_add_ipv6)
        if v3trap_en==True and 'snmptest' == v3q_user and trap_add_ipv6==config.trap_receiver_ipv6:
            print("Success to Validate SNMPV configurations after grid restore")
            assert True
        else:
            print("Failure: falied to validate SNMPV configurations after grid restore")
            assert False

    @pytest.mark.run(order=70)
    def test_069_cleanup(self): 
        
        print("\n\n Clean up all created object\n\n")
        
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatanalytics", grid_vip=config.grid_vip)
        print(get_ref)
        res = json.loads(get_ref)
        for i in res:
            data = {"enable_service": False}
            response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            print(response)
            if type(response) == tuple:
                if response[0]==200:
                    print("Success: Stop Threat analytics Service")
                    assert True
                else:
                    print("Failure: Stop Threat analytics Service")
                    assert False
        
        sleep(300)
        check_able_to_login_appliances(config.grid_vip)
        restart_services()
        
        response1 = ib_NIOS.wapi_request('GET',object_type="grid:threatanalytics")
        response1=json.loads(response1)
        print(response1)
        ref_obj = response1[0]['_ref']
        response = ib_NIOS.wapi_request('PUT',object_type=ref_obj ,fields=json.dumps({"dns_tunnel_black_list_rpz_zones":[]}))
        print(response)
        
        if type(response) == tuple:
            if response[0]==200:
                print("Success: Add the zone to add blaclisted domains in threat analytics")
                restart_services()
                assert True
            else:
                print("Failure: Add the zone to add blaclisted domains in threat analytics")
                assert False
               
        get_reff = ib_NIOS.wapi_request('GET', object_type="zone_rp")
      
        for ref in json.loads(get_reff):
            print(ref['_ref'])
            
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
            print(response)  
            if type(response) == tuple:           
                if response[0]==200: 
                    print("Sucess: \n Deleting RPZ zone  ")
                    assert True
                else:
                    print("Failure: \n Deleting RPZ zone  ")
                    assert False       
        
        data = {"enable_dns": False,"enable_dns_cache_acceleration": False}
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns?_return_fields=enable_dns_cache_acceleration", grid_vip=config.grid_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            print(ref)
        
            response = ib_NIOS.wapi_request('PUT', object_type=ref['_ref'], fields=json.dumps(data))
            print(response)
            if type(response) == tuple:
                if response[0]==200:
                    print("Success: stop DCA Service")
                    assert True
                else:
                    print("Failure: did nt stop DCA Service")
                    assert False
                    
            elif "member:dns" in response:
                print("Success: Stop DCA Service ")
                assert True
                
        sleep(300)
        check_able_to_login_appliances(config.grid_vip)
        '''
        Cleanup SNMP setting on grid level
        '''
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting')
        get_grid_ref=json.loads(get_ref)[0]['_ref']
        
        data={"snmp_setting":{"syscontact": [""],"sysdescr": [""],"syslocation": [""],"sysname": [""],"snmpv3_traps_enable": False,"snmpv3_queries_enable": False,"snmpv3_queries_users": [],"queries_enable":False,"queries_community_string":"","trap_receivers":[],"traps_community_string":"","traps_enable":False}}
       
        response=ib_NIOS.wapi_request('PUT',ref=get_grid_ref, fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:
                print("Sucess: \n Deleting SNMP configuration on GRID-LEVEL ")
                assert True
            else:
                print("Failure: \n Deleting SNMP configuration on GRID-LEVEL ")
                assert False
        '''
        Cleanup SNMP setting on members level
        '''
             
        get_reff = ib_NIOS.wapi_request('GET', object_type="member")
      
        for ref in json.loads(get_reff):
            print(ref['_ref'])
            
            data={"use_snmp_setting":False,"snmp_setting":{"syscontact": [""],"sysdescr": [""],"syslocation": [""],"sysname": [""],"snmpv3_traps_enable": False,"snmpv3_queries_enable": False,"snmpv3_queries_users": [],"queries_enable":False,"queries_community_string":"","trap_receivers":[],"traps_community_string":"","traps_enable":False}}
            response=ib_NIOS.wapi_request('PUT',ref=ref['_ref'], fields=json.dumps(data))
            print(response)
            if type(response) == tuple:

                if response[0]==200:
                    print("Sucess: \n Deleting SNMP configuration on members ")
                    assert True
                    
                else:
                    print("Failure: \n Deleting SNMP configuration on members ")
                    assert False 
                    
                   
        get_ref = ib_NIOS.wapi_request('GET', object_type="snmpuser", grid_vip=config.grid_vip)

        for ref in json.loads(get_ref):
            
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
            print(response)  
            if type(response) == tuple:           
                if response[0]==200: 
                    print("Sucess: \n Deleting SNMP user ")
                    assert True
                else:
                    print("Failure: \n Deleting SNMP user ")
                    assert False

        restart_services()
        
    @pytest.mark.run(order=71)
    def test_070_validate_all_enabled_services_inactive(self):
        print("\n============================================\n")
        print("Validate Threat analytics Service inactive")
        print("\n============================================\n")
      
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatanalytics", grid_vip=config.grid_vip)
        print(get_ref)
        response1=json.loads(get_ref)
        print(response1)
        ref_obj = response1[0]['status']
        if "INACTIVE" in ref_obj:
            print("Validating threat analytics service inactive")
            assert True
        else:
            print("Failure: Validating threat analytics service is inactive or not")
            assert False
      
        print("\n============================================\n")
        print("Validate DCA Service inactive")
        print("\n============================================\n")
       
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns?_return_fields=enable_dns_cache_acceleration", grid_vip=config.grid_vip)
        print(get_ref)
        response1=json.loads(get_ref)
        print(response1)
        ref_obj = response1[0]['enable_dns_cache_acceleration']
        ref_obj1 = response1[1]['enable_dns_cache_acceleration']
        if ref_obj==False and ref_obj1==False:
            print("Validating DCA service inactive on both master and member")
            assert True
        else:
            print("Failure: Validate DCA Service not inactive on both master and member")
            assert False 


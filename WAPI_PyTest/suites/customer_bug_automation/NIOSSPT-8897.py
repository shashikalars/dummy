__author__ = "Arunkumar CM"
__email__  = "acm@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. stand alone grid
#  3. Licenses : Grid,DNS,DHCP and IPV4 with lan ip only                               #
########################################################################################

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
import time
import sys
import socket
from paramiko import client
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv
from ib_utils.start_bird import Start_bird_process as bird
#import start_bird
global host_ip
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
#host_ip="10.36.198.9"
def show_OSPF_data():
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show ospf neighbor')
        #child.expect('>')
        if child.expect('.'):
            child.sendline('\n')
        child.expect('>')
        output= child.before
        child.sendline('exit')
        return output


class Network(unittest.TestCase):
    
    @pytest.mark.run(order=1)
    def test_001_change_lan_settings(self):
        os.system("netctl_system -i lan -S 10.36.0.0 -a vlanset -H "+config.vm_id)
        #child = pexpect.spawn('reset_console -H '+config.vm_id)
        #child = pexpect.spawn('reset_console -H '+config.vm_id)
        child = pexpect.spawn('console_connect -H '+config.vm_id)
        #child = pexpect.spawn('console_connect -H '+config.vm_id)
        child.logfile=sys.stdout
        child.expect('Escape chara.*')
        child.sendline('\n')
        child.sendline('\n')
        child.sendline('\n')
        sleep(10)
        child.expect('login:')
        child.sendline('admin')
        sleep(10)
        child.expect('password:')
        sleep(5)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set network')
        #child.expect('\[Default: '+config.grid_vip+'\]:')
        child.expect('Enter IP address:')
        child.sendline(config.grid_mgmt_ip)
        child.expect('\[Default: 255.255.0.0\]:')
        child.sendline("255.255.0.0")
        child.expect('\[Default: 10.36.0.1\]:')
        child.sendline("10.36.0.1")
        child.expect('\[Default: Untagged\]:')
        child.sendline("Untagged")
        child.expect('\[Default: .*\]:')
        child.sendline(config.grid_ip6)
        child.expect('\[Default: 64\]:')
        child.sendline("64")
        child.expect('\[Default.*::1\]:')
        child.sendline("2001:550:40a:2400::1")
        child.expect('\[Default: Untagged\]:')
        child.sendline("Untagged")
        child.expect("Become grid member\? \(y or n\):",timeout=30)
        child.sendline("n")
        child.expect("Is this correct\? \(y or n\):",timeout=30)
        child.sendline("y")
        child.expect("Are you sure\? \(y or n\):",timeout=30)
        child.sendline("y")
        sleep(150)
        child.expect('login:')
        child.sendline('admin')
        sleep(10)
        child.expect('password:')
        sleep(5)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline("exit")
        return 1
    
    
    @pytest.mark.run(order=2)
    def test_002_add_ospf_config(self):
        directory=os.getcwd()
        bird("bird",["ospf"],directory+"/arun.json")     
        logging.info("Add OSPF config")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member",grid_vip=config.grid_mgmt_ip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        print (ref1)
        data = {"ospf_list": [{"area_id": "0.0.0.12","area_type": "STANDARD","authentication_type": "NONE","auto_calc_cost_enabled": True,"cost": 1,"dead_interval": 40,"enable_bfd": False,"hello_interval": 10,"interface": "LAN_HA","is_ipv4": True,"key_id": 1,"retransmit_interval": 5,"transmit_delay": 1}]}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_mgmt_ip)
        sleep(20)
        logging.info(response)
        print (response)
        sleep(20)
        print("OSPF enabled on the member")



    @pytest.mark.run(order=3)
    def test_003_add_Anycast_configuration(self):
        logging.info("getting member properties")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_mgmt_ip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"additional_ip_list":[{"anycast": True,"enable_bgp": False ,"enable_ospf": True,"interface": "LOOPBACK","ipv4_network_setting": {"address": "1.1.1.2","dscp": 0,"primary": False,"subnet_mask": "255.255.255.255","use_dscp": False}}]}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_mgmt_ip)
        sleep(10)
        sleep(300)
        print("Anycast is enabled on the Grid member")

    @pytest.mark.run(order=4)
    def test_004_add_Anycast_ip_in_member(self):
        logging.info("getting member properties")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_mgmt_ip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        #data={"additional_ip_list_struct":[{"ip_address":"2:2:2::3"}],"use_mgmt_port":True,"use_mgmt_ipv6_port":True,"use_lan_ipv6_port":True}
        #data={"additional_ip_list_struct":[{"ip_address":"1.1.1.2"}],"use_mgmt_port":True}
        data={"additional_ip_list_struct":[{"ip_address":"1.1.1.2"}]}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_mgmt_ip)
        if type(response)!=tuple:
            grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_mgmt_ip)
            ref = json.loads(grid)[0]['_ref']
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus",grid_vip=config.grid_mgmt_ip)
            #data={"restart_option":"FORCE_RESTART","service_option":"DNS"}
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",grid_vip=config.grid_mgmt_ip)
            time.sleep(60)
            print ("Restarting the grid forcefully ")
            print("Anycast ip is added on the Grid member")
            assert True
            sleep(50)
        else:
            assert False

    @pytest.mark.run(order=5)
    def test_005_Start_DNS_Service(self):
        logging.info("Start DNS Service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns",grid_vip=config.grid_mgmt_ip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        for ref in res:
            ref1 = ref["_ref"]
            logging.info("Modify a enable_dns")
            data = {"enable_dns": True}
            response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data),grid_vip=config.grid_mgmt_ip)
            sleep(20)
            logging.info(response)
            read  = re.search(r'200',response)
            for read in  response:
                assert True
        logging.info("Test Case 1 Execution Completed")

    @pytest.mark.run(order=6)
    def test_006_Validate_DNS_service_Enabled(self):
        logging.info("Validate DNs Service is enabled")
        get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns",grid_vip=config.grid_mgmt_ip)
        logging.info(get_tacacsplus)
        res = json.loads(get_tacacsplus)
        for i in res:
            logging.info("found")
            assert i["enable_dns"] == True
        logging.info("Test Case 2 Execution Completed")
        logging.info("============================")


    @pytest.mark.run(order=7)
    def test_007_validate_OSPF_data(self):
        time.sleep(20)
        data=show_OSPF_data()
        result=re.search("Neighbor .*, interface address.*",data)
        result1=re.search("In the area 0.0.0.12 via interface eth1",data)
        if (result != None and result1!=None):
            assert True
            print ("Test case 74 passed")
        else:
            assert False
            print ("Test case 74 failed")

    @pytest.mark.run(order=8)
    def test_008_Remove_Anycast_ip_in_member(self):
        logging.info("Cleaning up the added Anycast IP")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns",grid_vip=config.grid_mgmt_ip)
        logging.info(get_ref)
        print get_ref
        res = json.loads(get_ref)
        print res
        ref1 = json.loads(get_ref)[0]['_ref']
        data={"additional_ip_list_struct":[]}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_mgmt_ip)
        print response
        print("Anycast ip is removed on the Grid member")

    @pytest.mark.run(order=9)
    def test_009_Remove_Anycast_configuration(self):
        logging.info("Remove Anycast configuratpn")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member",grid_vip=config.grid_mgmt_ip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"additional_ip_list":[]}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_mgmt_ip)
        print response
        sleep(150)
        print("Anycast is enabled on the Grid member")

    @pytest.mark.run(order=1)
    def test_010_change_lan_settings(self):
        os.system("netctl_system -i lan -S 10.35.0.0 -a vlanset -H "+config.vm_id)
        #child = pexpect.spawn('reset_console -H '+config.vm_id)
        #child = pexpect.spawn('reset_console -H '+config.vm_id)
        child = pexpect.spawn('console_connect -H '+config.vm_id)
        #child = pexpect.spawn('console_connect -H '+config.vm_id)
        child.logfile=sys.stdout
        child.expect('Escape chara.*')
        child.sendline('\n')
        child.sendline('\n')
        child.sendline('\n')
        sleep(10)
        child.expect('login:')
        child.sendline('admin')
        sleep(10)
        child.expect('password:')
        sleep(5)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set network')
        #child.expect('\[Default: '+config.grid_vip+'\]:')
        child.expect('Enter IP address:')
        child.sendline(config.grid_vip)
        child.expect('\[Default: 255.255.0.0\]:')
        child.sendline("255.255.0.0")
        child.expect('\[Default: 10.35.0.1\]:')
        child.sendline("10.35.0.1")
        child.expect('\[Default: Untagged\]:')
        child.sendline("Untagged")
        child.expect('\[Default: .*\]:')
        child.sendline(config.grid_ip6)
        child.expect('\[Default: 64\]:')
        child.sendline("64")
        child.expect('\[Default.*::1\]:')
        child.sendline("2001:550:40a:2400::1")
        child.expect('\[Default: Untagged\]:')
        child.sendline("Untagged")
        child.expect("Become grid member\? \(y or n\):",timeout=30)
        child.sendline("n")
        child.expect("Is this correct\? \(y or n\):",timeout=30)
        child.sendline("y")
        child.expect("Are you sure\? \(y or n\):",timeout=30)
        child.sendline("y")
        sleep(150)
        child.expect('login:')
        child.sendline('admin')
        sleep(10)
        child.expect('password:')
        sleep(5)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline("exit")
        return 1


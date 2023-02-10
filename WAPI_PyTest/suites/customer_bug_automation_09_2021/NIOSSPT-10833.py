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

class NIOSSPT_10833(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_000_start_IPv4_DHCP_service(self):
        print("Enable the DPCH service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties?_return_fields=enable_dhcp", grid_vip=config.grid_vip)
        print(get_ref)
        ref = json.loads(get_ref)[0]['_ref']
        data = {"enable_dhcp":True}
        response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)

    @pytest.mark.run(order=2)
    def test_001_create_DDNS_domain_name(self):
        print("DDNS domain name in Grid DNS properties")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
        ref = json.loads(get_ref)[0]['_ref']
        data = {"ddns_domainname": "ddns.warwick.ac.uk",
            "enable_ddns": True,
            "ddns_use_option81":True}
        response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: DDNS domain name")
                assert False
            else:
                print("Success: DDNS domain name")
                assert True      
                
    @pytest.mark.run(order=3)
    def test_002_Create_IPv4_network(self):
        print("Create an ipv4 network ")
        data = {"network": "137.205.102.0/24","network_view": "default","members":[{"_struct": "dhcpmember","ipv4addr":config.grid_master_vip}]}
        response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create an ipv4 network")
                assert False
            else:
                print("Success: Create an ipv4 network")
                assert True
                
        print("Restart DHCP Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)

    @pytest.mark.run(order=4)
    def test_003_verify_changes_in_config_file(self):
        print("\nverify changes in config file")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_master_vip, username='root', pkey = mykey)
        data="cat /infoblox/var/dhcpd_conf/dhcpd.conf\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.readlines()
        #print(stdout)
        count=0
        for res in stdout:
            print(res)
            if 'ddns-domainname = pick ( option fqdn.domainname, "ddns.warwick.ac.uk" );' in res:
                
                count=count+1

        client.close()
        print(count)
        if count<=1:
            print("Success : verify changes in config file")
            assert True
        else:
            print("Failure : verify changes in config file")
            assert False

    @pytest.mark.run(order=5)
    def test_004_cleanup_created_objects(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
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

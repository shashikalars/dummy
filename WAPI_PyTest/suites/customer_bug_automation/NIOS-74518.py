#!/usr/bin/env python
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Licenses : DTC license  to GM and all members                         #
#  2. SA + member1 (HA) + member2                                           #
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
import ib_utils.common_utilities as comm_util
import ib_utils.ib_NIOS as ib_NIOS
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv
  
class NIOS_74518(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_Create_a_zone(self):
        print("Creating a test_s.com zone")
        data={"fqdn": "test_s.com",
                "view":"default"}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==404:
                print("Failure: Creating a test_s.com zone")
                assert False
            else:
                print("Success: Creating a test_s.com zone")
                assert True 
                
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth')
        for ref in json.loads(get_ref):
            if 'test_s.com' in ref['fqdn']:
                data={
                   "grid_primary": [
                        {
                            "name": config.grid_member1_fqdn,
                            "stealth": False
                        },
                        {
                            "name": config.grid_member2_fqdn,
                            "stealth": False
                        }
                    ]}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401 or response[0]==404:
                        print("Failure: adding member1 and memeber2 as grid primaries")
                        assert False
                

                
        
    @pytest.mark.run(order=2)
    def test_001_add_a_DTC_Server(self):
        print("Create A DTC first Server")
        data = {"name":"s1","host":"1.1.1.1"}
        response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
        print response
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create A DTC first Server")
                assert False
            else:
                print("Success: Create A DTC first Server")
                assert True
        
    @pytest.mark.run(order=3)
    def test_002_create_Pool_add_server_init(self): 
    
        get_ref = ib_NIOS.wapi_request('GET', object_type="dtc:server", grid_vip=config.grid_vip)
        serv=[]
        for ref in json.loads(get_ref):
            if 's1' in ref['_ref']:   
                serv.append({"ratio":1 ,"server": ref['_ref']})
        
        get_ref = ib_NIOS.wapi_request('GET', object_type="dtc:monitor:icmp", grid_vip=config.grid_vip)
        monitor=[]
        for ref in json.loads(get_ref):
            if not'https' in ref['_ref']:
                monitor.append(ref['_ref'])
        print(monitor)
        
        data = {"name":"p1","lb_preferred_method":"ROUND_ROBIN","servers": serv,"monitors":monitor}
        response = ib_NIOS.wapi_request('POST', object_type="dtc:pool", fields=json.dumps(data))
        print(response)
        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create A DTC Pool and adding servers in it")
                assert False
            else:
                print("Success: Create A DTC Pool and adding servers in it")
                assert True

    @pytest.mark.run(order=4)
    def test_003_add_a_DTC_lbdn(self):
        print("Create A DTC LBDN")
      
        get_ref_pool = ib_NIOS.wapi_request('GET', object_type="dtc:pool", grid_vip=config.grid_vip)
        pool_lst=[]
        ind=1
        for ref in json.loads(get_ref_pool):
            print(ref['_ref'])
            if 'p1' in ref['_ref']:
                pool_lst.append({"pool":ref['_ref'],"ratio":ind})
                ind=ind+1
                
        get_ref_zones = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
        zone_lst=[]
        for ref in json.loads(get_ref_zones):
            print(ref['_ref'])
            if 'test_s.com' in ref['_ref']:
                zone_lst.append(ref['_ref'])
                       
        print(pool_lst,zone_lst)   
        data = {"name":"one","lb_method":"ROUND_ROBIN","patterns": ["arec.test_s.com"], "pools": pool_lst, "auth_zones":zone_lst,"types":["A","AAAA","CNAME","NAPTR"]}
        response = ib_NIOS.wapi_request('POST', object_type="dtc:lbdn", fields=json.dumps(data))
        print response
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create A DTC LBDN")
                assert False
            else:
                print("Success: Create A DTC LBDN")
                assert True
        
        print("Restart DHCP Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)
        
    @pytest.mark.run(order=5)
    def test_004_consolidated_monitor_on_DTC_pool(self):
        print("consolidated monitor on DTC pool")   
        get_ref = ib_NIOS.wapi_request('GET', object_type="dtc:monitor:icmp", grid_vip=config.grid_vip)
        monitor=""
        for ref in json.loads(get_ref):
            if 'icmp' in ref['_ref']:
                monitor=ref['_ref']
            
        get_ref_mem = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)

        memb=[]
        ind=1
        for ref in json.loads(get_ref_mem):
            # if config.grid_member1_fqdn in ref['_ref']:  
                # memb.append(config.grid_member1_fqdn)
            if config.grid_member2_fqdn in ref['_ref']:
                memb.append(config.grid_member2_fqdn)
                
        get_ref_pool = ib_NIOS.wapi_request('GET', object_type="dtc:pool", grid_vip=config.grid_vip)
        print(get_ref_pool)
        print(memb)
        for ref in json.loads(get_ref_pool):
            if 'p1' in ref['_ref']:
                get_ref = ib_NIOS.wapi_request('GET', object_type=ref['_ref']+"?_return_fields=consolidated_monitors")
                data = {"consolidated_monitors": [{"availability": "ALL","members": memb,"monitor": monitor}]}
                response = ib_NIOS.wapi_request('PUT',ref=ref['_ref'], fields=json.dumps(data))
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: Assign_servers_to_pool_monitor")
                        assert False
                    else:
                        print("Success: Assign_servers_to_pool_monitor")
                        assert True
                        

    @pytest.mark.run(order=6)
    def test_005_start_dns_services_for_member(self):
       print("Start DNS service")
       get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns')
       print(get_ref)
       for ref in json.loads(get_ref):
           response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps({"enable_dns":True}))
           print(response)
           if type(response) == tuple:
               if response[0]==400 or response[0]==401:
                   assert False

    
    @pytest.mark.run(order=7)
    def test_006_validation(self):
        ip_list=[]

        ip_list.append(config.grid_vip) 
        ip_list.append(config.grid_member1_vip) 
        ip_list.append(config.grid_member2_vip) 
 
        print(ip_list)
        for i in ip_list:
            print(i)
            print("====================")
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
            mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
            client.connect(i, username='root', pkey = mykey)
            data="grep -icw 'DTC*initialization' /var/log/syslog"
            stdin, stdout, stderr = client.exec_command(data)
            stdout=stdout.read()
            print("output ",stdout)

            if '0' in stdout:
                print("Success")
                client.close()
                #continue
                assert True

            else:
                print("Failed")
                client.close()
		continue
                assert False

    @pytest.mark.run(order=8)
    def test_007_cleanup_object(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="dtc:lbdn", grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
             
            print(response)
                    
            if type(response) == tuple:
                        
                if response[0]==400 or response[0]==401:
                            
                    assert False
                else:
                    assert True
   
        get_ref = ib_NIOS.wapi_request('GET', object_type="dtc:pool", grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
             
            print(response)
                    
            if type(response) == tuple:
                        
                if response[0]==400 or response[0]==401:
                            
                    assert False
                else:
                    assert True
        get_ref = ib_NIOS.wapi_request('GET', object_type="dtc:server", grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
             
            print(response)
                    
            if type(response) == tuple:
                        
                if response[0]==400 or response[0]==401:
                            
                    assert False
                else:
                    assert True
   
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
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
        

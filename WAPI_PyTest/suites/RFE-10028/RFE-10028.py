#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Shivasai"
__email__  = "sbandaru@infoblox.com"

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
import sys
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import shlex
from time import sleep
import subprocess
import pexpect
import paramiko
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv


def display_msg(x=""):
    """ 
    Additional function.
    """
    logging.info(x)
    print(x)

def dras_requests():
    """
    Perform dras command
    """
    print("sending dras")
    dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i '+str(config.grid_vip)+' '+ ' -x l=10.0.0.0 ' + '-n 1 -a aa:bb:cc:dd:ee:ff'
    print(dras_cmd)
    dras_cmd1 = os.system(dras_cmd)
    print (dras_cmd1)
    
       
def start_radius():
    """
    start radius service
    """
    print("starting radius")
    cmd=('sshpass -p "infoblox" ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@%s' % (config.client_radius))
    cmd = shlex.split(cmd)
    cmd.append('radiusd start')
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    output = process.communicate()
    print(output)
    sleep(30)

def stop_radius():
    """
    stop radius service
    """
    cmd=('sshpass -p "infoblox" ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@%s' % (config.client_radius))
    cmd = shlex.split(cmd)
    cmd.append('killall radiusd')
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    output = process.communicate()
    sleep(30)

class RFE_10028(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_001_radius_auth_server(self):
        display_msg("----------------------------------------------------")
        display_msg("|     Testcase 1 Execution Started                 |")
        display_msg("----------------------------------------------------")

        display_msg("Creating radius service in authentication server group")
        data={
                "name": "radius",
                "servers": [
                    {
                        "acct_port": 1812,
                        "address": "10.36.201.7",
                        "auth_port": 1812,
                        "auth_type": "PAP",
                        "shared_secret": "testing123"
                        }
                    ]
                }
        radiusref = ib_NIOS.wapi_request('POST', object_type="radius:authservice",fields=json.dumps(data))
        print(radiusref)
        display_msg(radiusref)
        radiusref = json.loads(radiusref)
        if type(radiusref) == tuple:
            if response[0]==400 or response[0]==401:
                assert False
            else:
                assert True
        print("Test Case 1 Execution Completed")
                
    @pytest.mark.run(order=2)
    def test_002_add_radius_server_in_authentication_servers(self):
        display_msg("----------------------------------------------------")
        display_msg("|     Testcase 2 Execution Started                 |")
        display_msg("----------------------------------------------------")
        
        display_msg("Get radius server reference")
        radius_ref = ib_NIOS.wapi_request('GET', object_type="radius:authservice")
        radius_ref = json.loads(radius_ref)
        radiusref=radius_ref[0]['_ref']
        local_ref = ib_NIOS.wapi_request('GET', object_type="localuser:authservice")
        local_ref = json.loads(local_ref)
        localuser_ref = local_ref[0]['_ref']
        display_msg("Adding localuser and radius reference to auth_services")
        data={
            "auth_services":[localuser_ref,radiusref],
            "default_group": "admin-group"
            }
        auth_policy_ref = ib_NIOS.wapi_request('GET',object_type='authpolicy')
        auth_policy_ref = json.loads(auth_policy_ref)
        auth_policy_ref=auth_policy_ref[0]['_ref']
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=auth_policy_ref)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                assert False
            else:
                assert True
        print("Test Case 2 Execution Completed")
        
    @pytest.mark.run(order=3)
    def test_003_add_ipv4_NAC_filters(self):
        display_msg("----------------------------------------------------")
        display_msg("|     Testcase 3 Execution Started                 |")
        display_msg("----------------------------------------------------")
        display_msg("adding ipv4 DHCP NAC filters ")
        data={
                "name": "good guys",
                "expression": "(Sophos.ComplianceState=\"Compliant\" OR Sophos.ComplianceState=\"PartialCompliant\" OR Radius.ServerError=\"false\" OR Radius.ServerState=\"success\")"        
            }
        data1={
               "name": "bad guys", 
                "expression": "(Sophos.UserClass=\"NACDeny\" OR Sophos.ComplianceState=\"Unknown\" OR Sophos.ComplianceState=\"NonCompliant\")"
        }
        data2={
            "name": "Server Error",
            "expression": "(Radius.ServerError=\"true\")"
        }
        data3={
            "name": "Server Fail",
            "expression": "(Radius.ServerState=\"fail\")"
        }
        Nacref1 = ib_NIOS.wapi_request('POST', object_type="filternac",fields=json.dumps(data))
        if type(Nacref1) == tuple:
            if Nacref1[0]==400 or Nacref1[0]==401:
                assert False
        
        Nacref2 = ib_NIOS.wapi_request('POST', object_type="filternac",fields=json.dumps(data1))
        if type(Nacref2) == tuple:
            if Nacref2[0]==400 or Nacref2[0]==401:
                assert False
        
        Nacref3 = ib_NIOS.wapi_request('POST', object_type="filternac",fields=json.dumps(data2))
        if type(Nacref3) == tuple:
            if Nacref3[0]==400 or Nacref3[0]==401:
                assert False
        
        Nacref4 = ib_NIOS.wapi_request('POST', object_type="filternac",fields=json.dumps(data3))     
        if type(Nacref4) == tuple:
            if Nacref4[0]==400 or Nacref4[0]==401:
                assert False
            else:
                assert True
        print("Test Case 3 Execution Completed")
        
    @pytest.mark.run(order=4)
    def test_004_enable_dhcp_create_network_range(self):
        display_msg("----------------------------------------------------")
        display_msg("|     Testcase 4 Execution Started                 |")
        display_msg("----------------------------------------------------")
        display_msg("Enable Dhcp,create network and range")
        data = {"network": "10.0.0.0/8","network_view": "default","members":[{"_struct": "dhcpmember","ipv4addr":config.grid_vip}]}
        response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data))
        print(response)
        if type(response)  == tuple:
            if response[0] == 400 or response[0] -- 401:
                assert False
        print("Created the ipv4network 10.0.0.0/8 in default view")
        data = {"network":"10.0.0.0/8","start_addr":"10.0.0.10","end_addr":"10.0.0.100","network_view": "default","member": {"_struct": "dhcpmember","ipv4addr": config.grid_vip}}
        response = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(data))
        print (response)
        if type(response)  == tuple:
            if response[0] == 400 or response[0] -- 401:
                assert False
        display_msg("Enable Dhcp service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties")
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"enable_dhcp":True,}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                assert False
            else:
                assert True
        print("Test Case 4 Execution Completed")
    
    @pytest.mark.run(order=5)
    def test_005_add_radius_server_in_dhcp_auth_server_group(self):
        display_msg("----------------------------------------------------")
        display_msg("|     Testcase 5 Execution Started                 |")
        display_msg("----------------------------------------------------")
        
        display_msg("Get radius server reference")
        radius_ref = ib_NIOS.wapi_request('GET', object_type="radius:authservice")
        radius_ref = json.loads(radius_ref)
        radiusref=radius_ref[0]['_ref']
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties")
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"authn_server_group_enabled": True,"auth_server_group":"radius",}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
        print(response)
        if type(response)  == tuple:
            if response[0] == 400 or response[0] -- 401:
                assert False
        grid =  ib_NIOS.wapi_request('GET', object_type="grid",)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        response = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),)
        sleep(20) #wait for 20 secs for the service to get started
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                assert False
            else:
                assert True
               
        print("Test Case 5 Execution Completed")

    @pytest.mark.run(order=6)
    def test_006_add_nac_filters_to_range(self):
        display_msg("----------------------------------------------------")
        display_msg("|     Testcase 6 Execution Started                 |")
        display_msg("----------------------------------------------------")
        get_ref = ib_NIOS.wapi_request('GET', object_type="range")
        ref1 = json.loads(get_ref)[0]['_ref']
        data={"logic_filter_rules": [{"filter": "Server Error", "type": "NAC"}, {"filter": "Server Fail", "type": "NAC"},{"filter": "bad guys","type": "NAC"},{"filter": "good guys","type": "NAC"}],"nac_filter_rules": [{"filter": "Server Fail","permission": "Allow"},{"filter": "good guys","permission": "Allow"},{"filter": "bad guys","permission": "Allow"},{"filter": "Server Error","permission": "Allow"}]}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
        print(response)
        if type(response)  == tuple:
            if response[0] == 400 or response[0] -- 401:
                assert False
        grid =  ib_NIOS.wapi_request('GET', object_type="grid",)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        response = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),)
        sleep(20) #wait for 20 secs for the service to get started
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                assert False
            else:
                assert True
        
        print("Test Case 6 Execution Completed")
        
    
    @pytest.mark.run(order=7)
    def test_007_enable_snmp(self):
        display_msg("----------------------------------------------------")
        display_msg("|     Testcase 7 Execution Started                 |")
        display_msg("----------------------------------------------------")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting')
        print(get_ref)
        get_ref = json.loads(get_ref)[0]['_ref']
        data={"snmp_setting":{"queries_enable":True,"queries_community_string":"public","trap_receivers":[{"address": config.client_ip}],"traps_community_string":"public","traps_enable":True}}
        response = ib_NIOS.wapi_request('PUT', ref=get_ref, fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            assert False
        else:
            assert True
        print("Test Case 7 Execution Completed")    
    
    @pytest.mark.run(order=8)
    def test_008_collect_snmp_traps(self):
        display_msg("----------------------------------------------------")
        display_msg("|     Testcase 8 Execution Started                 |")
        display_msg("----------------------------------------------------")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.client_ip)
        try:
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('#')
            child.sendline('snmptrapd udp6:162,udp:162 -f -C -c /etc/snmp/snmptrapd.conf -Le &> snmp_traps.txt\n')
            sleep(10)
            #child.sendcontrol('z')
            #child.expect('snmptrapd.conf')
            child.close()
            assert True
            
        except Exception as e:
            child.close()
            print("Failure:")
            print (e)
            assert False
        print("Test Case 8 Execution Completed")
        
    def test_009_send_dras_request_check_log(self):
        display_msg("----------------------------------------------------")
        display_msg("|     Testcase 9 Execution Started                 |")
        display_msg("----------------------------------------------------")
        start_radius()
        sleep(60)
        stop_radius()
        log("start","/var/log/syslog",config.grid_vip)
        dras_requests()
        dras_requests()
        sleep(10)
        LookFor="NAC authentication group is down"
        print("looking for logs ")
        sleep(50)
        log("stop","/var/log/syslog",config.grid_vip)
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(logs)
        if logs == None:
            print("Error")
            assert False
        else:
            assert True
            print("found logs")
        print("Test Case 09 Execution Completed")
        
    @pytest.mark.run(order=10)
    def test_010_send_dras_request_check_log(self):
        display_msg("----------------------------------------------------")
        display_msg("|     Testcase 10 Execution Started                 |")
        display_msg("----------------------------------------------------")
        start_radius()
        log("start","/var/log/syslog",config.grid_vip)
        dras_requests()
        dras_requests()
        sleep(10)
        LookFor="NAC authentication group is up"
        print("looking for logs ")
        sleep(50)
        log("stop","/var/log/syslog",config.grid_vip)
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(logs)
        if logs == None:
            print("Error")
            assert False
        else:
            assert True
            print("found logs")
        print("Test Case 10 Execution Completed")

    @pytest.mark.run(order=11)
    def test_011_check_snmp_traps(self):
        display_msg("----------------------------------------------------")
        display_msg("|     Testcase 11 Execution Started                 |")
        display_msg("----------------------------------------------------")
        cmd=('sshpass -p "infoblox" ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@%s' % (config.client_ip))
        cmd = shlex.split(cmd)
        cmd.append('grep -i -c "NAC authentication group is up" snmp_traps.txt')
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        output = process.communicate()
        print(output[0])
        if int(output[0]) > 0 :
            assert True
        else:
            assert False 
        print("Test Case 11 Execution Completed")
           
    @pytest.mark.run(order=12)
    def test_012_check_snmp_traps(self):
        display_msg("----------------------------------------------------")
        display_msg("|     Testcase 12 Execution Started                 |")
        display_msg("----------------------------------------------------")
        
        cmd=('sshpass -p "infoblox" ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@%s' % (config.client_ip))
        cmd = shlex.split(cmd)
        cmd.append('grep -i -c "NAC authentication group is down" snmp_traps.txt')
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        output = process.communicate()
        print(output[0])
        if int(output[0]) > 0 :
            assert True
        else:
            assert False
        print("Test Case 12 Execution Completed")

    @pytest.mark.run(order=13)
    def test_013_disable_radius_validate_logs(self):
        display_msg("----------------------------------------------------")
        display_msg("|     Testcase 13 Execution Started                 |")
        display_msg("----------------------------------------------------")
        LookFor="Cannot read Radius Server Group properties. Authentication Service is not available"
        log("start","/var/log/syslog",config.grid_vip)
        data={"disable": True,}
        radiusref = ib_NIOS.wapi_request('GET',object_type='radius:authservice')
        radiusref = json.loads(radiusref)
        radiusref=radiusref[0]['_ref']
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=radiusref)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                assert False
        sleep(45)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid",)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        response = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),)
        sleep(40) #wait for 20 secs for the service to get started 
        log("stop","/var/log/syslog",config.grid_vip)
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(logs)
        if logs == None:
            print("Error")
            assert False
        else:
            assert True
            print("found logs")
        print("Test Case 13 Execution Completed")

    @pytest.mark.run(order=14)
    def test_014_disable_radius_validate_logs(self):
        display_msg("----------------------------------------------------")
        display_msg("|     Testcase 14 Execution Started                 |")
        display_msg("----------------------------------------------------")
	
        data={"disable": False,}
        radiusref = ib_NIOS.wapi_request('GET',object_type='radius:authservice')
        radiusref = json.loads(radiusref)
        radiusref=radiusref[0]['_ref']
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=radiusref)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                assert False
        sleep(45)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid",)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        response = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),)
        sleep(40)
	LookFor="Attempted to run Sophos connector without initialization"
        log("start","/var/log/syslog",config.grid_vip)
        data={"disable": True,}
        radiusref = ib_NIOS.wapi_request('GET',object_type='radius:authservice')
        radiusref = json.loads(radiusref)
        radiusref=radiusref[0]['_ref']
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=radiusref)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                assert False
        sleep(45)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid",)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        response = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),)
        sleep(40)
        print("sending dras")
	dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i '+str(config.grid_vip)+' '+ ' -x l=10.0.0.0 ' + '-n 1 -a aa:bb:cc:dd:ee:ff'
   	print(dras_cmd)
   	dras_cmd1 = os.system(dras_cmd)
    	print (dras_cmd1)
	log("stop","/var/log/syslog",config.grid_vip)
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(logs)
        if logs == None:
            print("Error")
            assert False
        else:
            assert True
            print("found logs")
        print("Test Case 14 Execution Completed")    

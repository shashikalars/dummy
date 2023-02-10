#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Chetan Kumar PG"
__email__  = "cpg@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Grid Master + Grid Member and SA Grid Master                          #
#  2. Licenses : DNS(enabled), DHCP, Grid                                   #
#############################################################################

import os
import re
import csv
import config
import pytest
import unittest
import logging
import json
import shlex
import pexpect
import paramiko
from time import sleep
from subprocess import Popen,PIPE
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as  ib_TOKEN
from ib_utils.log_capture import log_action as log
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="rfe_7507.log" ,level=logging.DEBUG,filemode='w')
   
def restart_services(grid=config.grid_vip):
    """
    Restart Services
    """
    display_msg("Restart services")
    get_ref =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=grid)
    ref = json.loads(get_ref)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices", fields=json.dumps(data),grid_vip=grid)
    sleep(20)

def display_msg(x=""):
    """ 
    Additional function.
    """
    logging.info(x)
    print(x)

def perform_dig_query(zone, record, rr_type, grid=config.grid_vip):
    """
    Performs dig query and validates output
    """
    #output = os.popen("dig @"+grid+" "+zone+ " axfr").read()
    #display_msg(output)

    display_msg("Perform dig query for the added "+rr_type+" record")
    display_msg("dig @"+grid+" "+record+" IN "+rr_type)
    output = os.popen("dig @"+grid+" "+record+" IN "+rr_type).read()
    output = output.split('\n')
    answer = False
    pattern = False
    for line in output:
        display_msg(line)
    match_line = record+".\s+\d+\s+IN\s+"+rr_type
    for line in output:
        if answer and not pattern:
            match = re.match(match_line, line)
            if match:
                pattern = True
                break
        if 'ANSWER SECTION' in line:
            answer = True
    if not answer or not pattern:
        display_msg("Failure: Perform dig query")
        assert False

def start_syslog(logfile, grid=config.grid_vip):
    """
    Start log capture
    """
    display_msg("Start capturing "+logfile)
    log("start",logfile,grid)

def stop_syslog(logfile, grid=config.grid_vip):
    """
    Stop log capture
    """
    display_msg("Stop capturing "+logfile)
    log("stop",logfile,grid)

def validate_syslog(logfile, lookfor, grid=config.grid_vip):
    """
    Validate captured log
    """
    display_msg("Validate captured log")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(grid, username='root', pkey = mykey)
    file_name='_'.join(logfile.split('/'))
    file = '/root/dump/'+ str(grid)+file_name+'.log'
    display_msg("cat "+file+" | grep -i '"+lookfor+"'")
    stdin, stdout, stderr = client.exec_command("cat "+file+" | grep -i '"+lookfor+"'")
    result=stdout.read()
    display_msg(result)
    client.close()
    if result:
        return True
    return False


class RFE_7507(unittest.TestCase):
    
    @pytest.mark.run(order=1)
    def test_000_setup(self):
        """
        setup method: Used for configuring pre-required configs.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case setup Started            |")
        display_msg("------------------------------------------------")
        
        '''Enable debug log'''
        display_msg("Enable debug log")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        stdin, stdout, stderr = client.exec_command("touch /infoblox/var/debug")
        if stderr.read():
            display_msg(stderr.read())
            assert False
        stdin, stdout, stderr = client.exec_command("touch /infoblox/var/debug_nice")
        if stderr.read():
            display_msg(stderr.read())
            assert False
        stdin, stdout, stderr = client.exec_command("touch /infoblox/rc restart")
        if stderr.read():
            display_msg(stderr.read())
        sleep(30)
        client.close()
        
        '''Enable debug log grid master 2'''
        display_msg("Enable debug log grid master 2")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid2_vip, username='root', pkey = mykey)
        stdin, stdout, stderr = client.exec_command("touch /infoblox/var/debug")
        if stderr.read():
            display_msg(stderr.read())
            assert False
        stdin, stdout, stderr = client.exec_command("touch /infoblox/var/debug_nice")
        if stderr.read():
            display_msg(stderr.read())
            assert False
        stdin, stdout, stderr = client.exec_command("touch /infoblox/rc restart")
        if stderr.read():
            display_msg(stderr.read())
        sleep(30)
        client.close()
        
        '''Enable extra validation feature'''
        display_msg("Check wether extra validation feature is disbaled by default")
        args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid_vip
        args=shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        child.stdin.write("show extra_dns_name_validations\n")
        child.stdin.write("exit")
        result = child.communicate()
        flag = False
        for line in result:
            display_msg(line)
            if 'extra_dns_name_validations option is turned off' in line:
                flag = True
        if not flag:
            display_msg("Failure: extra validation feature is not disabled by default")
            assert False

        
        display_msg("Enable extra validation feature")
        os.system("set extra_dns_name_validations on")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        try:
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set extra_dns_name_validations on')
            child.expect('.*Do you want to continue?.*')
            child.sendline('y')
            child.expect('Infoblox >')
            child.sendline('exit')
        except Exception as error:
            display_msg(error)
            assert False
        finally:
            child.close()

        '''Enable extra validation feature grid master 2'''
        display_msg("Check wether extra validation feature is disbaled by default on grid master 2")
        args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid2_vip
        args=shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        child.stdin.write("show extra_dns_name_validations\n")
        child.stdin.write("exit")
        result = child.communicate()
        flag = False
        for line in result:
            display_msg(line)
            if 'extra_dns_name_validations option is turned off' in line:
                flag = True
        if not flag:
            display_msg("Failure: extra validation feature is not disabled by default")
            assert False

        
        display_msg("Enable extra validation feature on grid master 2")
        os.system("set extra_dns_name_validations on")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid2_vip)
        try:
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set extra_dns_name_validations on')
            child.expect('.*Do you want to continue?.*')
            child.sendline('y')
            child.expect('Infoblox >')
            child.sendline('exit')
        except Exception as error:
            display_msg(error)
            assert False
        finally:
            child.close()
        
        sleep(60)

        display_msg("---------Test Case setup Execution Completed----------")

    @pytest.mark.run(order=2)
    def test_001_enable_dns_service(self):
        """
        Enable DNS service in both the grids
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 1 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        '''Enable DNS service'''
        display_msg("Enable DNS service")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns')
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps({"enable_dns":True}))
            if type(response) == tuple:
                display_msg("Failure: ENable DNS Service")
                assert False
            restart_services()

        '''Enable DNS service in second grid master'''
        display_msg("Enable DNS service in the second grid master")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns', grid_vip=config.grid2_vip)
        display_msg(get_ref)
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps({"enable_dns":True}), grid_vip=config.grid2_vip)
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: ENable DNS Service")
            assert False
        restart_services(config.grid2_vip)
        
        display_msg("-----------Test Case 1 Execution Completed------------")

    @pytest.mark.run(order=3)
    def test_002_modify_host_name_policy_to_allow_any(self):
        """
        Modify host name policy to allow any in both the grids
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 2 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        '''Modify host name policy to allow any'''
        display_msg("Modify hostname policy to allow any")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns')
        display_msg(get_ref)
        data = {"protocol_record_name_policies":[{"regex": "^[a-zA-Z0-9]$|^[a-zA-Z0-9][-a-zA-Z0-9.]*[a-zA-Z0-9]$",
                                                  "is_default": False, 
                                                  "name": "Strict Hostname Checking"}, 
                                                 {"regex": "^[-a-zA-Z0-9_.]+$", 
                                                  "is_default": False, 
                                                  "name": "Allow Underscore"}, 
                                                 {"regex": ".+", 
                                                  "is_default": True, 
                                                  "name": "Allow Any"}]}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Set host name policy to allow any")
            assert False
        restart_services()
        
        display_msg("Modify hostname policy to allow any in the second grid master")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns', grid_vip=config.grid2_vip)
        display_msg(get_ref)
        data = {"protocol_record_name_policies":[{"regex": "^[a-zA-Z0-9]$|^[a-zA-Z0-9][-a-zA-Z0-9.]*[a-zA-Z0-9]$",
                                                  "is_default": False, 
                                                  "name": "Strict Hostname Checking"}, 
                                                 {"regex": "^[-a-zA-Z0-9_.]+$", 
                                                  "is_default": False, 
                                                  "name": "Allow Underscore"}, 
                                                 {"regex": ".+", 
                                                  "is_default": True, 
                                                  "name": "Allow Any"}]}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data), grid_vip=config.grid2_vip)
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Set host name policy to allow any in remote server")
            assert False
        restart_services()
        
        display_msg("-----------Test Case 2 Execution Completed------------")

    @pytest.mark.run(order=4)
    def test_003_enable_zone_transfer(self):
        """
        Enable zone transfer with allow any in both the grids
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 3 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        '''Enable zone transfer'''
        display_msg("Enable Zone transfer")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns')
        display_msg(get_ref)
        data = {"allow_transfer":[{"_struct": "addressac","address":"Any", "permission":"ALLOW"}]}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Enable Zone transfer")
            assert False
        restart_services()
        
        display_msg("Enable Zone transfer on the second grid master")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns', grid_vip=config.grid2_vip)
        display_msg(get_ref)
        data = {"allow_transfer":[{"_struct": "addressac","address":"Any", "permission":"ALLOW"}]}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data), grid_vip=config.grid2_vip)
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Enable Zone transfer")
            assert False
        restart_services(config.grid2_vip)
        
        display_msg("-----------Test Case 3 Execution Completed------------")

    @pytest.mark.run(order=5)
    def test_004_enable_updates(self):
        """
        Enable updates with allow any in both the grids
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 4 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        '''Enable updates'''
        display_msg("Enable Updates")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns')
        display_msg(get_ref)
        data = {"allow_update":[{"_struct": "addressac","address":"Any", "permission":"ALLOW"}]}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Enable update")
            assert False
        restart_services()
        
        display_msg("Enable updates on the second grid master")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns', grid_vip=config.grid2_vip)
        display_msg(get_ref)
        data = {"allow_update":[{"_struct": "addressac","address":"Any", "permission":"ALLOW"}]}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data), grid_vip=config.grid2_vip)
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Enable update")
            assert False
        restart_services(config.grid2_vip)
        
        display_msg("-----------Test Case 4 Execution Completed------------")

    @pytest.mark.run(order=6)
    def test_005_create_auth_forward_mapping_zone(self):
        """
        Create an auth zone with name rfe_7507.com in both the grids
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 5 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        '''Create an auth zone'''
        display_msg("Create a DNS auth zone rfe_7507.com")
        data = {"fqdn": "rfe_7507.com",
                "view":"default",
                "grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
        start_syslog('/infoblox/var/infoblox.log', config.grid_vip)
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Create a DNS auth zone rfe_7507.com")
            assert False
        restart_services()
        result = validate_syslog('/infoblox/var/infoblox.log', 'extra_zone_validations', config.grid_vip)
        stop_syslog('/infoblox/var/infoblox.log', config.grid_vip)
        if not result:
            display_msg("Failure: Log validation")
            assert False
        
        '''Create an auth zone in grid master 2'''
        display_msg("Create a DNS auth zone rfe_7507.com in grid master 2")
        data = {"fqdn": "rfe_7507.com",
                "view":"default",
                "grid_primary": [{"name": config.grid2_fqdn,"stealth": False}]}
        start_syslog('/infoblox/var/infoblox.log', config.grid2_vip)
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data),grid_vip=config.grid2_vip)
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Create a DNS auth zone rfe_7507.com remote server")
            assert False
        restart_services(config.grid2_vip)
        result = validate_syslog('/infoblox/var/infoblox.log', 'extra_zone_validations', config.grid2_vip)
        stop_syslog('/infoblox/var/infoblox.log', config.grid2_vip)
        if not result:
            display_msg("Failure: Log validation")
            assert False
        
        display_msg("-----------Test Case 5 Execution Completed------------")

    @pytest.mark.run(order=7)
    def test_006_add_network(self):
        """
        Add network 1.0.0.0/8 in both the grids
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 6 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        '''Add network'''
        display_msg("Add network 1.0.0.0/8 address")
        data = {"network":"1.0.0.0/8"}
        response = ib_NIOS.wapi_request('POST', object_type='network', fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Add network 1.0.0.0/8 address")
            assert False
        restart_services()
        
        display_msg("Add network 1.0.0.0/8 address in the second grid master")
        data = {"network":"1.0.0.0/8"}
        response = ib_NIOS.wapi_request('POST', object_type='network', fields=json.dumps(data),grid_vip=config.grid2_vip)
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Add network 1.0.0.0/8 address in the remote server")
            assert False
        restart_services(config.grid2_vip)
        
        display_msg("-----------Test Case 6 Execution Completed------------")

    @pytest.mark.run(order=8)
    def test_007_add_host_record_with_valid_host_name(self):
        """
        Verify that host gets created in DNS zone with valid hostname.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 7 Execution Started           |")
        display_msg("----------------------------------------------------")
        ## record names not validated + '' -
        
        display_msg("Add host record with valid host name into rfe_7507.com zone")
        hostnames = ["*","?","_","!","#","(","&","^",";","+","@","''","-"]
        for name in hostnames:
            display_msg("Hostname= "+name)
            start_syslog('/infoblox/var/infoblox.log', config.grid_vip)
            hostname = name+".rfe_7507.com"
            data = {"name":hostname, "ipv4addrs":[{"ipv4addr":"1.1.1.1"}]}
            response = ib_NIOS.wapi_request('POST',object_type="record:host",fields=json.dumps(data))
            display_msg(response)
            if type(response) == tuple:
                display_msg("Failure: Add valid host record")
                assert False
            result = validate_syslog('/infoblox/var/infoblox.log', 'extra_validations', config.grid_vip)
            stop_syslog('/infoblox/var/infoblox.log', config.grid_vip)
            if not result:
                display_msg("Failure: Log validation")
                assert False
        
        hostnames = ["*","?","_","!","#","\\\(","&","^","\@","\\\;"]
        for name in hostnames:
            display_msg("Hostname= "+name)
            hostname = name+".rfe_7507.com"
            perform_dig_query("rfe_7507.com", "\\"+hostname, "A")
        
        display_msg("-----------Test Case 7 Execution Completed------------")

    @pytest.mark.skip
    def test_008_add_host_record_with_invalid_host_name(self):
        """
        Verify that host DOES NOT get created in DNS zone with INVALID hostname.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 8 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add host record with invalid host name into this zone")
        data = {"name":"[.rfe_7507.com", "ipv4addrs":[{"ipv4addr":"1.1.1.2"}]}
        start_syslog('/infoblox/var/infoblox.log', config.grid_vip)
        response = ib_NIOS.wapi_request('POST',object_type="record:host",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if "RR was rejected by DNS server" in response[-1]:
                result = validate_syslog('/infoblox/var/infoblox.log', 'extra_validations', config.grid_vip)
                stop_syslog('/infoblox/var/infoblox.log', config.grid_vip)
                if not result:
                    display_msg("Failure: Log validation")
                    assert False
            else:
                display_msg("Failure: Add invalid host record")
                assert False
        else:
            display_msg("Failure: Add invalid host record")
            assert False
        
        display_msg("-----------Test Case 8 Execution Completed------------")

    @pytest.mark.run(order=10)
    def test_009_add_modify_a_record_with_valid_host_name(self):
        """
        Verify that A record gets created and modified in DNS zone with valid hostname.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 9 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add A record with valid host name into this zone")
        data = {"name":"a_rec.rfe_7507.com", "ipv4addr":"1.1.1.3"}
        start_syslog('/infoblox/var/infoblox.log', config.grid_vip)
        response = ib_NIOS.wapi_request('POST',object_type="record:a",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Add valid A record")
            assert False
        result = validate_syslog('/infoblox/var/infoblox.log', 'extra_validations', config.grid_vip)
        stop_syslog('/infoblox/var/infoblox.log', config.grid_vip)
        if not result:
            display_msg("Failure: Log validation")
            assert False
        
        perform_dig_query("rfe_7507.com", "a_rec.rfe_7507.com", "A")
        
        '''Modify a record'''
        display_msg("Modify A record")
        get_ref = ib_NIOS.wapi_request('GET', object_type='record:a')
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            if ref['name'] == 'a_rec.rfe_7507.com':
                record_ref = ref['_ref']
                break
        data = {"name":"a_rec2.rfe_7507.com"}
        start_syslog('/infoblox/var/infoblox.log', config.grid_vip)
        response = ib_NIOS.wapi_request('PUT',ref=record_ref,fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Modify valid A record")
            assert False
        result = validate_syslog('/infoblox/var/infoblox.log', 'extra_validations', config.grid_vip)
        stop_syslog('/infoblox/var/infoblox.log', config.grid_vip)
        if not result:
            display_msg("Failure: Log validation")
            assert False
        
        display_msg("-----------Test Case 3 Execution Completed------------")

    @pytest.mark.skip
    def test_010_add_a_record_with_invalid_host_name(self):
        """
        Verify that A record DOES NOT get created in DNS zone with INVALID hostname.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 10 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add A record with invalid host name into this zone")
        data = {"name":"[2.rfe_7507.com", "ipv4addr":"1.1.1.4"}
        start_syslog('/infoblox/var/infoblox.log', config.grid_vip)
        response = ib_NIOS.wapi_request('POST',object_type="record:a",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if "RR was rejected by DNS server" in response[-1]:
                result = validate_syslog('/infoblox/var/infoblox.log', 'extra_validations', config.grid_vip)
                stop_syslog('/infoblox/var/infoblox.log', config.grid_vip)
                if not result:
                    display_msg("Failure: Log validation")
                    assert False
            else:
                display_msg("Failure: Add invalid A record")
                assert False
        else:
            display_msg("Failure: Add invalid A record")
            assert False
        
        display_msg("-----------Test Case 10 Execution Completed-----------")

    @pytest.mark.run(order=12)
    def test_011_add_host_record_with_enable_dns_enable_dhcp(self):
        """
        Verify that host gets created in DHCP with valid hostname when "Enable in DNS" is selected.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 11 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add host record with enable in DNS and enable in DHCP")
        data = {"name":"host2.rfe_7507.com", 
                "ipv4addrs":[{"ipv4addr":"1.1.1.5"}],
                "configure_for_dns":True}
        start_syslog('/infoblox/var/infoblox.log', config.grid_vip)
        response = ib_NIOS.wapi_request('POST',object_type="record:host",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Add valid host record")
            assert False
        result = validate_syslog('/infoblox/var/infoblox.log', 'extra_validations', config.grid_vip)
        stop_syslog('/infoblox/var/infoblox.log', config.grid_vip)
        if not result:
            display_msg("Failure: Log validation")
            assert False
        
        perform_dig_query("rfe_7507.com", "host2.rfe_7507.com", "A")
        
        display_msg("-----------Test Case 11 Execution Completed-----------")

    @pytest.mark.skip
    def test_012_add_invalid_host_record_with_enable_dns_enable_dhcp(self):
        """
        Verify that host doesn't gets created in DHCP with invalid hostname when "Enable in DNS" is selected.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 12 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add invalid host record with enable in DNS and enable in DHCP")
        data = {"name":"[3.rfe_7507.com", 
                "ipv4addrs":[{"ipv4addr":"1.1.1.6"}],
                "configure_for_dns":True}
        start_syslog('/infoblox/var/infoblox.log', config.grid_vip)
        response = ib_NIOS.wapi_request('POST',object_type="record:host",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if "RR was rejected by DNS server" in response[-1]:
                result = validate_syslog('/infoblox/var/infoblox.log', 'extra_validations', config.grid_vip)
                stop_syslog('/infoblox/var/infoblox.log', config.grid_vip)
                if not result:
                    display_msg("Failure: Log validation")
                    assert False
            else:
                display_msg("Failure: Add invalid host record")
                assert False
        else:
            display_msg("Failure: Add invalid host record")
            assert False
        
        display_msg("-----------Test Case 12 Execution Completed-----------")

    @pytest.mark.run(order=14)
    def test_013_add_host_record_with_disable_dns_enable_dhcp(self):
        """
        Verify that host gets created in DHCP with valid hostname when "Not Enable in DNS" is selected.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 13 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add host record with disable in DNS and enable in DHCP")
        data = {"name":"host3.rfe_7507.com", 
                "ipv4addrs":[{"ipv4addr":"1.1.1.7"}],
                "configure_for_dns":False}
                #"configure_for_dhcp":True,
                #"mac":"10:10:10:10:10:10"}
        start_syslog('/infoblox/var/infoblox.log', config.grid_vip)
        response = ib_NIOS.wapi_request('POST',object_type="record:host",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Add valid host record")
            assert False
        result = validate_syslog('/infoblox/var/infoblox.log', 'extra_validations', config.grid_vip)
        stop_syslog('/infoblox/var/infoblox.log', config.grid_vip)
        if not result:
            display_msg("Failure: Log validation")
            assert False
        
        perform_dig_query("rfe_7507.com", "host3.rfe_7507.com", "A")
        
        display_msg("-----------Test Case 13 Execution Completed-----------")

    @pytest.mark.skip
    def test_014_add_invalid_host_record_with_disable_dns_enable_dhcp(self):
        """
        Verify that host doesn't gets created in DHCP with invalid hostname when "Not Enable in DNS" is selected.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 14 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add host record with disable in DNS and enable in DHCP")
        data = {"name":"[4.rfe_7507.com", 
                "ipv4addrs":[{"ipv4addr":"1.1.1.8"}],
                "configure_for_dns":False}
        start_syslog('/infoblox/var/infoblox.log', config.grid_vip)
        response = ib_NIOS.wapi_request('POST',object_type="record:host",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if "RR was rejected by DNS server" in response[-1]:
                result = validate_syslog('/infoblox/var/infoblox.log', 'extra_validations', config.grid_vip)
                stop_syslog('/infoblox/var/infoblox.log', config.grid_vip)
                if not result:
                    display_msg("Failure: Log validation")
                    assert False
            else:
                display_msg("Failure: Add invalid host record")
                assert False
        else:
            display_msg("Failure: Add invalid host record")
            assert False
        
        display_msg("-----------Test Case 14 Execution Completed-----------")

    @pytest.mark.run(order=16)
    def test_015_create_bulk_host_record(self):
        """
        Create bulk host record
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 15 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Ceate bulk host record")
        data = {"start_addr":"1.1.1.10", "end_addr":"1.1.1.15", "prefix":"bulk_host", "zone":"rfe_7507.com"}
        start_syslog('/infoblox/var/infoblox.log', config.grid_vip)
        response = ib_NIOS.wapi_request('POST', object_type='bulkhost', fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Create bulk host record")
            assert False
        result = validate_syslog('/infoblox/var/infoblox.log', 'extra_validations', config.grid_vip)
        stop_syslog('/infoblox/var/infoblox.log', config.grid_vip)
        if result:
            display_msg("Failure: extra_validation called for bulk host creation")
            assert False
        
        display_msg("-----------Test Case 15 Execution Completed----------")

    @pytest.mark.run(order=17)
    def test_016_create_subzone_with_valid_name(self):
        """
        Verify that valid sub-zone gets created in the zone. 
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 16 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Create subzones with valid name")
        zonenames = ["?.rfe_7507.com","_.rfe_7507.com","!.rfe_7507.com","#.rfe_7507.com",";.rfe_7507.com",
                     "(.rfe_7507.com","&.rfe_7507.com","^.rfe_7507.com","[.rfe_7507.com"]
        for name in zonenames:
            display_msg("Zone : "+name)
            data = {"fqdn": name,
                    "view":"default",
                    "grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
            start_syslog('/infoblox/var/infoblox.log', config.grid_vip)
            response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
            display_msg(response)
            if type(response) == tuple:
                display_msg("Failure: Create subzone with valid name")
                assert False
            restart_services()
            result = validate_syslog('/infoblox/var/infoblox.log', 'extra_zone_validations', config.grid_vip)
            stop_syslog('/infoblox/var/infoblox.log', config.grid_vip)
            if not result:
                display_msg("Failure: Log validation")
                assert False
        
        display_msg("-----------Test Case 16 Execution Completed-----------")

    @pytest.mark.run(order=18)
    def test_017_create_subzone_with_invalid_name(self):
        """
        Verify that invalid sub-zone Does not create.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 17 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Create subzone with valid name")
        data = {"fqdn": "*.rfe_7507.com",
                "view":"default",
                "grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        if type(response) == tuple:
            display_msg(response[1])
            if "Cannot create a wildcard subzone" in response[-1]:
                assert True
            else:
                display_msg("Failure: Create subzone with valid name")
                assert False
        else:
            display_msg(response)
            display_msg("Failure: Create subzone with valid name")
            assert False
        
        display_msg("-----------Test Case 17 Execution Completed-----------")

    @pytest.mark.run(order=19)
    def test_018_import_csv_file_with_valid_zone_names(self):
        """
        Import zone file having valid zone names.
        """
        display_msg()
        display_msg("---------------------------------------------------")
        display_msg("|          Test Case 18 Execution Started          |")
        display_msg("---------------------------------------------------")

        '''Modifying the grid primary value in the csv file'''
        with open('valid_zones.csv', 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')

            lines = list(csv_reader)
            for line in lines:
                if 'header' in line[0]:
                    continue
                line[23] = config.grid_fqdn+'/False/False/False'

        with open('valid_zones_new.csv', 'w') as new_file:
            csv_writer = csv.writer(new_file)
            csv_writer.writerows(lines)
        
        display_msg("Uploading csv file containing valid zone names")
        start_syslog('/infoblox/var/infoblox.log', config.grid_vip)
        dir_name=os.getcwd()
        base_filename = "valid_zones_new.csv"
        token =ib_TOKEN.generate_token_from_file(dir_name, base_filename)
        data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"OVERRIDE","operation":"INSERT"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_import")
        response=json.loads(response)
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: CSV file upload")
            assert False
        
        sleep(30)
        get_ref=ib_NIOS.wapi_request('GET', object_type="csvimporttask")
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            if response["csv_import_task"]["import_id"]==ref["import_id"]:
                if ref["lines_failed"]==0:
                    display_msg("CSV import successful")
                else:
                    raise Exception("CSV import unsuccessful")
        
        restart_services()
        result = validate_syslog('/infoblox/var/infoblox.log', 'extra_zone_validations', config.grid_vip)
        stop_syslog('/infoblox/var/infoblox.log', config.grid_vip)
        if not result:
            display_msg("Failure: Log validation")
            assert False
        
        display_msg("-----------Test Case 18 Execution Completed-----------")

    @pytest.mark.run(order=20)
    def test_019_import_csv_file_with_invalid_zone_names(self):
        """
        Import zone file having a invalid zone names.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 19 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        '''Modifying the grid primary value in the csv file'''
        with open('invalid_zones.csv', 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')

            lines = list(csv_reader)
            for line in lines:
                if 'header' in line[0]:
                    continue
                line[23] = config.grid_fqdn+'/False/False/False'

        with open('invalid_zones_new.csv', 'w') as new_file:
            csv_writer = csv.writer(new_file)
            csv_writer.writerows(lines)
        
        display_msg("Uploading csv file containing invalid zone names")
        dir_name=os.getcwd()
        base_filename = "invalid_zones_new.csv"
        token =ib_TOKEN.generate_token_from_file(dir_name, base_filename)
        data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"OVERRIDE","operation":"INSERT"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_import")
        response=json.loads(response)
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: CSV file upload")
            assert False
        
        sleep(30)
        get_ref=ib_NIOS.wapi_request('GET', object_type="csvimporttask")
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            if response["csv_import_task"]["import_id"]==ref["import_id"]:
                if ref["lines_failed"] >= 1:
                    display_msg("CSV import unsuccessful")
                else:
                    raise Exception("Failure: CSV import successful")
        
        restart_services()
        
        display_msg("-----------Test Case 19 Execution Completed-----------")

    @pytest.mark.run(order=21)
    def test_020_import_csv_file_with_valid_host_records(self):
        """
        Import zone file having valid host records.
        """
        display_msg()
        display_msg("---------------------------------------------------")
        display_msg("|          Test Case 20 Execution Started         |")
        display_msg("---------------------------------------------------")
        
        display_msg("Uploading csv file containing valid host record")
        start_syslog('/infoblox/var/infoblox.log', config.grid_vip)
        dir_name=os.getcwd()
        base_filename = "valid_hosts.csv"
        token =ib_TOKEN.generate_token_from_file(dir_name, base_filename)
        data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"OVERRIDE","operation":"INSERT"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_import")
        response=json.loads(response)
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: CSV file upload")
            assert False
        
        sleep(30)
        get_ref=ib_NIOS.wapi_request('GET', object_type="csvimporttask")
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            if response["csv_import_task"]["import_id"]==ref["import_id"]:
                if ref["lines_failed"]==0:
                    display_msg("CSV import successful")
                else:
                    raise Exception("CSV import unsuccessful")
        
        result = validate_syslog('/infoblox/var/infoblox.log', 'extra_validations', config.grid_vip)
        stop_syslog('/infoblox/var/infoblox.log', config.grid_vip)
        if not result:
            display_msg("Failure: Log validation")
            assert False
        
        output = os.popen("dig @"+config.grid_vip+" rfe_7507.com axfr").read()
        display_msg(output)
        
        display_msg("-----------Test Case 20 Execution Completed-----------")

    @pytest.mark.skip
    def test_021_import_csv_file_with_invalid_host_records(self):
        """
        Import zone file having a invalid hostnames for hosts and host records.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 21 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Uploading csv file containing invalid host record")
        start_syslog('/infoblox/var/infoblox.log', config.grid_vip)
        dir_name=os.getcwd()
        base_filename = "invalid_hosts.csv"
        token =ib_TOKEN.generate_token_from_file(dir_name, base_filename)
        data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"OVERRIDE","operation":"INSERT"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_import")
        response=json.loads(response)
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: CSV file upload")
            assert False
        
        data={"action":"START","file_name":"invalid_hosts.csv","on_error":"CONTINUE","operation":"CREATE","separator":"COMMA"}
        sleep(30)
        get_ref=ib_NIOS.wapi_request('GET', object_type="csvimporttask")
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            if response["csv_import_task"]["import_id"]==ref["import_id"]:
                if ref["lines_failed"] >= 1:
                    display_msg("CSV import unsuccessful")
                else:
                    raise Exception("Failure: CSV import successful")
        
        result = validate_syslog('/infoblox/var/infoblox.log', 'extra_validations', config.grid_vip)
        stop_syslog('/infoblox/var/infoblox.log', config.grid_vip)
        if not result:
            display_msg("Failure: Log validation")
            assert False
        
        output = os.popen("dig @"+config.grid_vip+" rfe_7507.com axfr").read()
        display_msg(output)
        
        display_msg("-----------Test Case 21 Execution Completed-----------")

    @pytest.mark.run(order=23)
    def test_022_import_records_to_remote_server(self):
        """
        Perform import zone operation to import records to remote server.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 22 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        '''Perform import zone in the remote server'''
        display_msg("Perform import zone in the remote server")
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth',grid_vip=config.grid2_vip)
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            if 'rfe_7507.com' in ref['_ref'] and 'sub' not in ref['_ref']:
                start_syslog('/infoblox/var/infoblox.log', config.grid2_vip)
                data = {"use_import_from":True, "import_from":config.grid_vip, "do_host_abstraction":True}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data),grid_vip=config.grid2_vip)
                display_msg(response)
                if type(response) == tuple:
                    display_msg("Failure: Import zone in the remote server")
                    assert False
                restart_services()
                result = validate_syslog('/infoblox/var/infoblox.log', 'extra_validations', config.grid2_vip)
                stop_syslog('/infoblox/var/infoblox.log', config.grid2_vip)
                if result:
                    display_msg("Failure: Log validation called for import zone operation")
                    assert False
        
        output = os.popen("dig @"+config.grid2_vip+" rfe_7507.com axfr").read()
        display_msg(output)
        
        display_msg("-----------Test Case 22 Execution Completed-----------")

    @pytest.mark.run(order=24)
    def test_023_zonetransfer_from_local_to_remote_server(self):
        """
        Perform zone transfer operation from local grid to remote server.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 23 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        '''Add FM zone with external secodary'''
        display_msg("Create an Authorative FMZ rfe_7507_zone_transfer.com with grid primary and external secondary")
        data = {"fqdn": "rfe_7507_zone_transfer.com",
                "view":"default",
                "grid_primary": [{"name": config.grid_fqdn,"stealth": False}],
                "external_secondaries": [{"name":config.grid2_fqdn,"address":config.grid2_vip}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Create Authorative FMZ in rfe_7507_zone_transfer.com with grid primary and external secondary")
            assert False
        restart_services()
        
        '''Add zone with external primary and grid secondary in remote server'''
        display_msg("Create an Authorative FMZ rfe_7507_zone_transfer.com with grid secondary and external primary")
        data = {"fqdn": "rfe_7507_zone_transfer.com",
                "view":"default",
                "use_external_primary": True,
                "grid_secondaries": [{"name": config.grid2_fqdn,"stealth": False}],
                "external_primaries": [{"name":config.grid_fqdn,"address":config.grid_vip}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data), grid_vip=config.grid2_vip)
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Create Authorative FMZ in rfe_7507_zone_transfer.com with grid primary and external secondary")
            assert False
        restart_services(config.grid2_vip)
        
        '''Add host record in primary zone'''
        display_msg("Add host record with valid host name into this zone")
        hostnames = ["*","?","_","!","#","(","&","^",";","+","@","''","-"]
        start_syslog('/infoblox/var/infoblox.log', config.grid2_vip)
        for name in hostnames:
            display_msg("Hostname= "+name)
            hostname = name+".rfe_7507_zone_transfer.com"
            data = {"name":hostname, "ipv4addrs":[{"ipv4addr":"1.1.1.17"}]}
            response = ib_NIOS.wapi_request('POST',object_type="record:host",fields=json.dumps(data))
            display_msg(response)
            if type(response) == tuple:
                display_msg("Failure: Add valid host record")
                assert False
            sleep(30)
            
        result = validate_syslog('/infoblox/var/infoblox.log', 'extra_zone_validations', config.grid2_vip)
        result2 = validate_syslog('/infoblox/var/infoblox.log', 'extra_validations', config.grid2_vip)
        stop_syslog('/infoblox/var/infoblox.log', config.grid2_vip)
        if result2 and not result:
            display_msg("Failure: Log validation called for zone transfer operation")
            assert False
        
        '''Perform dig query on the external server'''
        hostnames = ["*","?","_","!","#","\\\(","&","^","\@","\\\;"]
        for name in hostnames:
            display_msg("Hostname= "+name)
            hostname = name+".rfe_7507_zone_transfer.com"
            perform_dig_query("rfe_7507_zone_transfer.com", "\\"+hostname, "A", grid=config.grid2_vip)

        display_msg("-----------Test Case 23 Execution Completed-----------")

    @pytest.mark.run(order=25)
    def test_024_add_resource_records_through_nsupdate(self):
        """
        Through nsupdate add resource record with valid hostname.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 24 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add resource records using nsupdate")
        
        hostnames = [("MX 3 rfe_7507.com","*"),("AAAA ab::18","?"),("CAA 64 issue \"rfe_7507.com\"","!"),("A 1.0.0.18","#"),
                     ("MX 10 rfe_7507.com","("),("AAAA ac::18","&"),("CAA 128 issuewild \"rfe_7507.com\"",";"),
                     ("A 1.0.1.18","+"),("MX 100 rfe_7507.com","@"),("CAA 32 iodef \"rfe_7507.com\"","''"),("A 1.0.2.18","-")]
        start_syslog('/infoblox/var/infoblox.log', config.grid_vip)
        for data,record in hostnames:
            record = record+'.rfe_7507.com'
            display_msg("RR name : "+record)
            child = pexpect.spawn("nsupdate")
            try:
                child.expect('>')
                child.sendline('server '+config.grid_vip)
                display_msg(child.before)
                child.expect('>')
                child.sendline('check-names no')
                child.expect('>')
                child.sendline('update add '+record+' 3600 IN '+data)
                display_msg(child.before)
                child.expect('>')
                child.sendline('send')
                display_msg(child.before)
                child.expect('>')
                child.sendline('quit')
            except Exception as e:
                display_msg(e)
                assert False
            finally:
                child.close()
        result = validate_syslog('/infoblox/var/infoblox.log', 'extra_validations', config.grid_vip)
        stop_syslog('/infoblox/var/infoblox.log', config.grid_vip)
        if result:
            display_msg("Failure: Log validation called for ns update")
            assert False

        hostnames = [("MX","*"),("AAAA","?"),("CAA","!"),("A","#"),("MX","\\\("),("AAAA","&"),
                     ("CAA","\\\;"),("MX","\@")]
        for rr_type,name in hostnames:
            display_msg("Hostname= "+name)
            hostname = name+".rfe_7507.com"
            perform_dig_query("rfe_7507.com", "\\"+hostname, rr_type)
        
        display_msg("-----------Test Case 24 Execution Completed-----------")

    @pytest.mark.run(order=26)
    def test_025_delete_resource_records_through_nsupdate(self):
        """
        Through nsupdate delete resource record with valid hostname.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 25 Execution Started          |")
        display_msg("----------------------------------------------------")
        display_msg("Delete resource records using nsupdate")
        
        hostnames = [("MX 3 rfe_7507.com","*"),("AAAA ab::18","?"),("CAA 64 issue \"rfe_7507.com\"","!"),("A 1.0.0.18","#"),
                     ("MX 10 rfe_7507.com","("),("AAAA ac::18","&"),("CAA 128 issuewild \"rfe_7507.com\"",";"),
                     ("A 1.0.1.18","+"),("MX 100 rfe_7507.com","@"),("CAA 32 iodef \"rfe_7507.com\"","''"),("A 1.0.2.18","-")]
        for data,record in hostnames:
            record = record+'.rfe_7507.com'
            display_msg("RR name : "+record)
            child = pexpect.spawn("nsupdate")
            try:
                child.expect('>')
                child.sendline('server '+config.grid_vip+'\n')
                display_msg(child.before)
                child.expect('>')
                child.sendline('update delete '+record+' 3600 IN '+data)
                display_msg(child.before)
                child.expect('>')
                child.sendline('send\n')
                display_msg(child.before)
                child.expect('>')
                child.sendline('quit\n')
            except Exception as e:
                display_msg(e)
                assert False
            finally:
                child.close()
        
        display_msg("-----------Test Case 25 Execution Completed-----------")

    @pytest.mark.skip
    def test_026_add_invalid_a_record_through_nsupdate(self):
        """
        Through nsupdate add a record with invalid hostname.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 26 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add invalid a record using nsupdate")
        child = pexpect.spawn("nsupdate")
        try:
            child.expect('>')
            child.send('server '+config.grid_vip+'\n')
            display_msg(child.before)
            child.expect('>')
            child.send('update add a_rec.rfe_7507.com. 3600 IN A 1.0.0.18\n')
            display_msg(child.before)
            child.expect('check-names failed: bad owner.*')
            display_msg(child.before)
            child.send('quit\n')
        except Exception as e:
            display_msg(e)
            assert False
        finally:
            child.close()
        
        display_msg("-----------Test Case 26 Execution Completed-----------")

    @pytest.mark.skip
    def test_027_disbale_extra_validation_and_verify(self):
        """
        Diable extra validation feature from CLI and verify.
        set extra_dns_name_validations <on|off>
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 27 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        try:
            display_msg("Disable extra validation feature")
            args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid_vip
            args=shlex.split(args)
            child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            child.stdin.write("set extra_dns_name_validations off\n")
            child.stdin.write("exit")
            result = child.communicate()
            flag = False
            for line in result:
                display_msg(line)
                if 'Extra DNS name validations is turned off' in line:
                    flag = True
            if not flag:
                display_msg("Failure: extra validation feature is not disabled")
                assert False
            
            display_msg("Add host record with valid host name")
            data = {"name":"[20.rfe_7507.com", "ipv4addrs":[{"ipv4addr":"1.1.1.20"}]}
            start_syslog('/infoblox/var/infoblox.log', config.grid_vip)
            response = ib_NIOS.wapi_request('POST',object_type="record:host",fields=json.dumps(data))
            display_msg(response)
            if type(response) == tuple:
                display_msg("Failure: Add valid A record")
                assert False
            result = validate_syslog('/infoblox/var/infoblox.log', 'extra_validations', config.grid_vip)
            stop_syslog('/infoblox/var/infoblox.log', config.grid_vip)
            if result:
                display_msg("Failure: Log validation called for ns update")
                assert False
            
            perform_dig_query("rfe_7507.com", "\\[20.rfe_7507.com", "A")
        
        finally:
            display_msg("Enable extra validation feature")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@10.35.133.4')
            try:
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('set extra_dns_name_validations on')
                child.expect('.*Do you want to continue?.*')
                child.sendline('y')
                child.expect('Infoblox >')
                child.sendline('exit')
            except Exception as error:
                display_msg(error)
                assert False
            finally:
                child.close()
            
        
        display_msg("-----------Test Case 27 Execution Completed-----------")

    @pytest.mark.run(order=29)
    def test_028_add_resource_records_with_valid_host_name(self):
        """
        Add other resource records and validate their creation
        A, AAAA, MX, CAA, Alias
        
        # & ( ? ^ _ 
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 28 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add resource records with valid host name")
        hostnames = [("A","*"),("MX","?"),("AAAA","_"),("Alias","!alias"),("CAA","#"),("A","("),("MX","&"),
                     ("AAAA","^"),("Alias",";alias"),("CAA","+"),("A","@"),("MX","''"),("CAA","-")]
        for rr_type,name in hostnames:
            display_msg("Hostname= "+name)
            hostname = name+".rfe_7507.com"
            if rr_type == "A":
                data = {"name":hostname,"ipv4addr":"1.1.1.1"}
            elif rr_type == "MX":
                data = {"name":hostname,"mail_exchanger":";()[]{}@","preference":10}
            elif rr_type == "AAAA":
                data = {"name":hostname,"ipv6addr":"ab::1"}
            elif rr_type == "Alias":
                data = {"name":hostname,"target_name":"*.rfe_7507.com","target_type":"A"}
            elif rr_type == "CAA":
                data = {"name":hostname,"ca_flag":128,"ca_tag":"issue","ca_value":"(\\)[]{}@"}
            obj_type = "record:"+rr_type.lower()
            start_syslog('/infoblox/var/infoblox.log', config.grid_vip)
            response = ib_NIOS.wapi_request('POST',object_type=obj_type,fields=json.dumps(data))
            display_msg(response)
            if type(response) == tuple:
                display_msg("Failure: Add valid resource record")
                assert False
            result = validate_syslog('/infoblox/var/infoblox.log', 'extra_validations', config.grid_vip)
            stop_syslog('/infoblox/var/infoblox.log', config.grid_vip)
            if not result:
                display_msg("Failure: Log validation")
                assert False
        
        hostnames = [("A","*"),("MX","?"),("AAAA","_"),("A","!alias"),("CAA","#"),("A","\\\("),("MX","&"),
                     ("AAAA","^"),("A","\\\;alias"),("A","\@")]
        for rr_type,name in hostnames:
            display_msg("Hostname= "+name)
            hostname = name+".rfe_7507.com"
            perform_dig_query("rfe_7507.com", "\\"+hostname, rr_type)
        
        display_msg("-----------Test Case 28 Execution Completed-----------")

    @pytest.mark.run(order=30)
    def test_029_Add_host_record_with_valid_host_name_strict_hostname_checking(self):
        """
        Verify that host gets created in DNS zone with valid hostname when strict host name checking policy is enabled.
        """
        display_msg()
        display_msg("-----------------------------------------------------")
        display_msg("|          Test Case 29 Execution Started           |")
        display_msg("-----------------------------------------------------")

        '''Modify host name policy to strict host name checking'''
        display_msg("Modify hostname policy to strict host name checking")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns')
        display_msg(get_ref)
        data = {"protocol_record_name_policies":[{"regex": "^[a-zA-Z0-9]$|^[a-zA-Z0-9][-a-zA-Z0-9.]*[a-zA-Z0-9]$",
                                                  "is_default": True, 
                                                  "name": "Strict Hostname Checking"}, 
                                                 {"regex": "^[-a-zA-Z0-9_.]+$", 
                                                  "is_default": False, 
                                                  "name": "Allow Underscore"}, 
                                                 {"regex": ".+", 
                                                  "is_default": False, 
                                                  "name": "Allow Any"}]}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Set host name policy to strict host name checking")
            assert False
        restart_services()

        display_msg("Add host record with valid host name into this zone")
        data = {"name":"rfe7507host.rfe_7507.com", "ipv4addrs":[{"ipv4addr":"1.1.1.19"}]}
        start_syslog('/infoblox/var/infoblox.log', config.grid_vip)
        response = ib_NIOS.wapi_request('POST',object_type="record:host",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Add valid host record")
            assert False
        result = validate_syslog('/infoblox/var/infoblox.log', 'extra_validations', config.grid_vip)
        stop_syslog('/infoblox/var/infoblox.log', config.grid_vip)
        if not result:
            display_msg("Failure: Log validation")
            assert False
        
        perform_dig_query("rfe_7507.com", "rfe7507host.rfe_7507.com", "A")
        
        display_msg("-----------Test Case 29 Execution Completed------------")

    @pytest.mark.run(order=31)
    def test_030_Add_host_record_with_invalid_host_name_strict_hostname_checking(self):
        """
        Verify that host doesn't gets created in DNS zone with invalid hostname when strict host name checking policy is enabled.
        """
        display_msg()
        display_msg("-----------------------------------------------------")
        display_msg("|          Test Case 30 Execution Started           |")
        display_msg("-----------------------------------------------------")

        '''Modify host name policy to strict host name checking'''
        display_msg("Modify hostname policy to strict host name checking")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns')
        display_msg(get_ref)
        data = {"protocol_record_name_policies":[{"regex": "^[a-zA-Z0-9]$|^[a-zA-Z0-9][-a-zA-Z0-9.]*[a-zA-Z0-9]$",
                                                  "is_default": True, 
                                                  "name": "Strict Hostname Checking"}, 
                                                 {"regex": "^[-a-zA-Z0-9_.]+$", 
                                                  "is_default": False, 
                                                  "name": "Allow Underscore"}, 
                                                 {"regex": ".+", 
                                                  "is_default": False, 
                                                  "name": "Allow Any"}]}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Set host name policy to strict host name checking")
            assert False
        restart_services()

        display_msg("Add host record with valid host name into this zone")
        data = {"name":"rfe7507_host.rfe_7507.com", "ipv4addrs":[{"ipv4addr":"1.1.1.20"}]}
        response = ib_NIOS.wapi_request('POST',object_type="record:host",fields=json.dumps(data))
        if type(response) == tuple:
            display_msg(response[1])
            if "RR name 'rfe7507_host' does not comply with policy 'Strict Hostname Checking'" in response[-1]:
                assert True
            else:
                display_msg("Failure: Add invalid host record")
                assert False
        else:
            display_msg(response)
            display_msg("Failure: Add invalid host record")
            assert False
        
        display_msg("-----------Test Case 30 Execution Completed------------")

    @pytest.mark.run(order=32)
    def test_031_Add_host_record_with_valid_host_name_allow_underscore(self):
        """
        Verify that host gets created in DNS zone with valid hostname when allow underscore policy is enabled.
        """
        display_msg()
        display_msg("-----------------------------------------------------")
        display_msg("|          Test Case 31 Execution Started           |")
        display_msg("-----------------------------------------------------")

        '''Modify host name policy to allow underscore'''
        display_msg("Modify hostname policy to allow underscore")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns')
        display_msg(get_ref)
        data = {"protocol_record_name_policies":[{"regex": "^[a-zA-Z0-9]$|^[a-zA-Z0-9][-a-zA-Z0-9.]*[a-zA-Z0-9]$",
                                                  "is_default": False, 
                                                  "name": "Strict Hostname Checking"}, 
                                                 {"regex": "^[-a-zA-Z0-9_.]+$", 
                                                  "is_default": True, 
                                                  "name": "Allow Underscore"}, 
                                                 {"regex": ".+", 
                                                  "is_default": False, 
                                                  "name": "Allow Any"}]}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Set host name policy to allow underscore")
            assert False
        restart_services()

        display_msg("Add host record with valid host name into this zone")
        data = {"name":"rfe_7507_host.rfe_7507.com", "ipv4addrs":[{"ipv4addr":"1.1.1.21"}]}
        start_syslog('/infoblox/var/infoblox.log', config.grid_vip)
        response = ib_NIOS.wapi_request('POST',object_type="record:host",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Add valid host record")
            assert False
        result = validate_syslog('/infoblox/var/infoblox.log', 'extra_validations', config.grid_vip)
        stop_syslog('/infoblox/var/infoblox.log', config.grid_vip)
        if not result:
            display_msg("Failure: Log validation")
            assert False
        
        perform_dig_query("rfe_7507.com", "rfe_7507_host.rfe_7507.com", "A")
        
        display_msg("-----------Test Case 31 Execution Completed------------")

    @pytest.mark.run(order=33)
    def test_032_Add_host_record_with_invalid_host_name_allow_underscore(self):
        """
        Verify that host doesn't gets created in DNS zone with invalid hostname when strict host name checking policy is enabled.
        """
        display_msg()
        display_msg("-----------------------------------------------------")
        display_msg("|          Test Case 32 Execution Started           |")
        display_msg("-----------------------------------------------------")

        '''Modify host name policy to allow underscore'''
        display_msg("Modify hostname policy to allow underscore")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns')
        display_msg(get_ref)
        data = {"protocol_record_name_policies":[{"regex": "^[a-zA-Z0-9]$|^[a-zA-Z0-9][-a-zA-Z0-9.]*[a-zA-Z0-9]$",
                                                  "is_default": False, 
                                                  "name": "Strict Hostname Checking"}, 
                                                 {"regex": "^[-a-zA-Z0-9_.]+$", 
                                                  "is_default": True, 
                                                  "name": "Allow Underscore"}, 
                                                 {"regex": ".+", 
                                                  "is_default": False, 
                                                  "name": "Allow Any"}]}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Set host name policy to allow underscore")
            assert False
        restart_services()

        display_msg("Add host record with valid host name into this zone")
        data = {"name":"rfe_?7507_*host.rfe_7507.com", "ipv4addrs":[{"ipv4addr":"1.1.1.22"}]}
        response = ib_NIOS.wapi_request('POST',object_type="record:host",fields=json.dumps(data))
        if type(response) == tuple:
            display_msg(response[1])
            if "RR name 'rfe_?7507_*host' does not comply with policy 'Allow Underscore'" in response[-1]:
                assert True
            else:
                display_msg("Failure: Add invalid host record")
                assert False
        else:
            display_msg(response)
            display_msg("Failure: Add invalid host record")
            assert False
        
        display_msg("-----------Test Case 32 Execution Completed------------")


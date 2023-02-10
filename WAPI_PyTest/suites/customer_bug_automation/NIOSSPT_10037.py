#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Chetan Kumar PG"
__email__  = "cpg@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Grid Master                                                           #
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
import pexpect
import paramiko
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as ib_TOKEN
#from ib_utils.log_capture import log_action as log
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="niosspt_10037.log" ,level=logging.DEBUG,filemode='w')
   
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

class NIOSSPT_10037(unittest.TestCase):
    
    @pytest.mark.run(order=1)
    def test_000_setup(self):
        """
        setup method: Used for configuring pre-required configs.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case setup Started            |")
        display_msg("------------------------------------------------")
        
        '''"Enable DNS service"'''
        display_msg("Enable DNS service")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns')
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps({"enable_dns":True}))
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    display_msg("Failure: ENable DNS Service")
                    assert False
            restart_services()

        display_msg("---------Test Case setup Execution Completed----------")

    @pytest.mark.run(order=2)
    def test_001_Enable_zone_tranfer_with_TSIG_key(self):
        """
        Enable Zone Transfer with TSIG key - UPPERCASE
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 1 Execution Started           |")
        display_msg("----------------------------------------------------")

        '''"Enable zone transfer"'''
        display_msg("Enable Zone transfer")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns')
        display_msg(get_ref)
        data = {"allow_transfer":[{"_struct": "tsigac",
                                   "tsig_key_alg":"HMAC-SHA256", 
                                   "tsig_key_name":"NIOSSPT_10037", 
                                   "tsig_key":"ZI+vIhci6umhgSLyqsxxHw==",
                                   "use_tsig_key_name":True}]}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Enable Zone transfer")
                assert False
        restart_services()
        
        display_msg("-----------Test Case 1 Execution Completed------------")

    @pytest.mark.run(order=3)
    def test_002_Enable_queries_with_TSIG_key(self):
        """
        Enable Queries with TSIG key - lowercase
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 2 Execution Started           |")
        display_msg("----------------------------------------------------")

        '''"Enable queries"'''
        display_msg("Enable Queries")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns')
        display_msg(get_ref)
        data = {"allow_query":[{"_struct": "tsigac",
                                "tsig_key_alg":"HMAC-SHA256", 
                                "tsig_key_name":"niosspt_10037", 
                                "tsig_key":"ZI+vIhci6umhgSLyqsxxHw==",
                                "use_tsig_key_name":True}]}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Enable Queries")
                assert False
        restart_services()
        
        display_msg("-----------Test Case 2 Execution Completed------------")

    @pytest.mark.run(order=4)
    def test_003_generate_BIND_configuration_files(self):
        """
        Generate BIND configuration files using the below command.
        /infoblox/dns/bin/make_bind_conf -d /tmp
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 3 Execution Started           |")
        display_msg("----------------------------------------------------")

        display_msg("Generate BIND configuration files")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        display_msg("/infoblox/dns/bin/make_bind_conf -d /tmp")
        stdin, stdout, stderr = client.exec_command("/infoblox/dns/bin/make_bind_conf -d /tmp")
        error=stderr.read()
        display_msg(error)
        client.close()
        if error:
            return False
        
        display_msg("-----------Test Case 3 Execution Completed------------")

    @pytest.mark.run(order=5)
    def test_004_Validate_generated_BIND_config_file(self):
        """
        Validate that there is only one key in /tmp/tsig.key file
        
        cat /tmp/tsig.key
        key "niosspt_10037" {
            algorithm HMAC-SHA256;
            secret "FafcISqThX0T7cZ34gp2wA==";
        };
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 4 Execution Started           |")
        display_msg("----------------------------------------------------")

        display_msg("Validate /tmp/tsig.key file for only one key")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        display_msg("cat /tmp/tsig.key")
        stdin, stdout, stderr = client.exec_command("cat /tmp/tsig.key")
        output=stdout.read()
        display_msg(output)
        client.close()
        if output.count("key") >= 2: 
            if output.lower().count("niosspt_10037") == 2:
                display_msg("Failure: Found more than one key with the same name in the file tsig.key")
                assert False

        display_msg("-----------Test Case 4 Execution Completed------------")

    @pytest.mark.run(order=6)
    def test_005_Create_Auth_Zone(self):
        """
        Create an Auth zone
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 5 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Creating auth zone")
        data = {"fqdn":"niosspt_10037.com","grid_primary":[{"name": config.grid_fqdn}]}
        response = ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Create auth zone")
            assert False
        restart_services()
        
        display_msg("-----------Test Case 5 Execution Completed------------")

    @pytest.mark.run(order=7)
    def test_006_Create_A_Record(self):
        """
        Create A record in niosspt_10037.com
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 6 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Creating A record")
        data = {"name": "a_rec.niosspt_10037.com", "ipv4addr": "10.0.0.1"}
        response = ib_NIOS.wapi_request('POST',object_type='record:a',fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Create A record")
            assert False
        
        display_msg("-----------Test Case 6 Execution Completed------------")


    @pytest.mark.run(order=8)
    def test_007_Dig_A_record_Using_TSIG_Key(self):
        """
        Dig A record using TSIG key
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 7 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Dig A record using TSIG key")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        dig_cmd = "dig a_rec.niosspt_10037.com -y HMAC-SHA256:NIOSSPT_10037:ZI+vIhci6umhgSLyqsxxHw=="
        stdin, stdout, stderr = client.exec_command(dig_cmd)
        if stderr.read():
            display_msg(stderr.read())
        response = stdout.read()
        client.close()
        response = response.split('\n')
        answer = False
        pattern = False
        for line in response:
            display_msg(line)
        match_line = "a_rec.niosspt_10037.com.\s+\d+\s+IN\s+A\s+10.0.0.1"
        for line in response:
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
        
        display_msg("-----------Test Case 7 Execution Completed------------")

    @pytest.mark.run(order=-1)
    def test_cleanup(self):
        """
        cleanup method: Delete all the objects created from this script.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|          Test Case cleanup Started           |")
        display_msg("------------------------------------------------")
        
        display_msg("Revert back changes made to DNS properties")
        
        '''"Disable zone transfer"'''
        display_msg("Disable Zone transfer")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns')
        display_msg(get_ref)
        data = {"allow_transfer":[]}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Disable Zone transfer")
            assert False
        restart_services()
        
        '''"Disable queries"'''
        display_msg("Disable Queries")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns')
        display_msg(get_ref)
        data = {"allow_query":[]}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Disable Queries")
            assert False
        restart_services()
        
        '''Delete auth zone'''
        display_msg("Delete auth zone")
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth')
        for ref in json.loads(get_ref):
            if ref['fqdn'] == 'niosspt_10037.com':
                response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
                display_msg(response)
                if type(response) == tuple:
                    display_msg("Failure: Delete auth zone")
                    assert False
                break
        restart_services()

        display_msg("-----------Test Case cleanup Completed------------")

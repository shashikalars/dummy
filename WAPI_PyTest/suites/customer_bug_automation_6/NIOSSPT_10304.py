#!/usr/bin/env python
__author__ = "Rajath Patavardhan"
__email__  = "rpatavardhan@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. IB-FLEX Grid Master + IB-FLEX Grid Member                             #
#############################################################################
### Followed steps in NIOS-71177 as the fix for NIOSSPT-10304 is a hotfix ###


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
import sys
from paramiko import client
#from log_capture import log_action as log
#from log_validation import log_validation as logv
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as comm_util



def display_msg(x):
    logging.info(x)
    print("")
    print(x)
    
class SSH:
    client=None

    def __init__(self,address):
        logging.info ("Log Validation Script")
        logging.info ("connecting to server \n : ", address)
        self.client=client.SSHClient()
        self.client.set_missing_host_key_policy(client.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        self.client.connect(address, username='root', pkey = mykey)

    def send_command(self,command):
        if(self.client):
            stdin, stdout, stderr = self.client.exec_command(command)
            result=stdout.read()
            return result
        else:
            logging.info("Connection not opened.")
                

class Network(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_101_start_DCA_service(self):
        display_msg("starting DCA service in the Grid member...\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[1]['_ref']
        data = {"enable_dhcp": False}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        sleep(10)
        print (response)
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[1]['_ref']
        data = {"enable_dns": True,"enable_dns_cache_acceleration": True}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        sleep(10)
        print (response)
        sleep(30)
        print("DCA service started in the Grid member")



    @pytest.mark.run(order=2)
    def test_102_enable_recusrion_in_grid_member(self):
        display_msg("Enabling DNS recursion in Grid member...")
        grid_dns_ref = ib_NIOS.wapi_request('GET', object_type='member:dns')
        logging.info(grid_dns_ref)
        res = json.loads(grid_dns_ref)
        print res
        ref1 = json.loads(grid_dns_ref)[1]['_ref']
        print ref1
        data =  {"recursive_query_list": [{"address": "Any", "permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps({"allow_recursive_query": True}), grid_vip=config.grid_vip)
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Allow recursive query")
                assert False
        display_msg("Updating recursive query list...")
        response2 = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data), grid_vip=config.grid_vip)
        display_msg(response2)
        if type(response2) == tuple:
            if response2[0]==400 or response2[0]==401:
                display_msg("Failure: Add recursive query list")
                assert False


    @pytest.mark.run(order=3)
    def test_103_add_dns_forwarder_to_grid_member(self):
        display_msg("Adding DNS forwarder : 10.0.2.35 to the Grid Member...")
        grid_dns_ref = ib_NIOS.wapi_request('GET', object_type='member:dns')
        data = {"forwarders":["10.0.2.35"]}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(grid_dns_ref)[1]['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Adding DNS Forwarder")
                assert False
            else:
                assert True
    
    @pytest.mark.run(order=4)
    def test_104_stop_and_start_DCA_service_in_member(self):
        display_msg("Restarting DCA service in the Grid Member...\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[1]['_ref']
        data = {"enable_dns_cache_acceleration": False}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        sleep(10)
        logging.info(response)
        print (response)
        sleep(20)
        print("DCA service stopped")
        print("Starting DCA service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[1]['_ref']
        print ref1
        data = {"enable_dns": True,"enable_dns_cache_acceleration": True}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        sleep(10)
        logging.info(response)
        print (response)
        sleep(60)
        print("DCA service started in the Grid member.")

    @pytest.mark.run(order=5)
    def test_105_validate_infoblox_logs(self):
        display_msg("Validating infoblox logs in the Grid Member...")
        connection=SSH(str(config.grid_member1_vip))
        result=connection.send_command("cat \/infoblox\/var\/infoblox.log")
        keyword1=len(re.findall(r'DNS cache acceleration is now started', result))
        keyword2=len(re.findall(r'missing sppc configuration in view', result))
        keyword3=len(re.findall(r'notice DNS cache acceleration configuration error', result))
        if ((keyword1 >= 1) and (keyword2 == 0) and (keyword3 == 0)): 
            display_msg("Error not found, DCA service is running. Log validation successful")
            assert True
        else:
            assert False                

    @pytest.mark.run(order=6)
    def test_106_start_DCA_service(self):
        display_msg("starting DCA service in the Grid Master...\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"enable_dhcp": False}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        sleep(10)
        print (response)
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"enable_dns": True,"enable_dns_cache_acceleration": True}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        sleep(10)
        logging.info(response)
        print (response)
        sleep(300)
        print("DCA service started")



    @pytest.mark.run(order=7)
    def test_107_enable_recusrion_in_gm(self):
        display_msg("Enabling DNS recursion in the Grid Master...")
        grid_dns_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns')
        data =  {"recursive_query_list": [{"address": "Any", "permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(grid_dns_ref)[0]['_ref'], fields=json.dumps({"allow_recursive_query": True}))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Allow recursive query")
                assert False
        display_msg("Updating recursive query list...")
        response2 = ib_NIOS.wapi_request('PUT', ref=json.loads(grid_dns_ref)[0]['_ref'], fields=json.dumps(data))
        display_msg(response2)
        if type(response2) == tuple:
            if response2[0]==400 or response2[0]==401:
                display_msg("Failure: Add recursive query list")
                assert False


    @pytest.mark.run(order=8)
    def test_108_add_dns_forwarder(self):
        display_msg("Adding DNS forwarder : 10.0.2.35 to the Grid Master...")
        grid_dns_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns')
        data = {"forwarders":["10.0.2.35"]}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(grid_dns_ref)[0]['_ref'], fields=json.dumps(data))
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Adding DNS Forwarder")
                assert False
            else:
                assert True
    
    @pytest.mark.run(order=9)
    def test_109_stop_and_start_DCA_service(self):
        display_msg("Restarting DCA service in the Grid Master...\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"enable_dns_cache_acceleration": False}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        sleep(10)
        logging.info(response)
        print (response)
        sleep(20)
        print("DCA service stopped")
        print("Starting DCA service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        print ref1
        data = {"enable_dns": True,"enable_dns_cache_acceleration": True}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        sleep(10)
        logging.info(response)
        print (response)
        sleep(60)
        print("DCA service restarted in the Grid Master.")

    @pytest.mark.run(order=10)
    def test_110_validate_infoblox_logs(self):
        connection=SSH(str(config.grid_member1_vip))
        result=connection.send_command("cat \/infoblox\/var\/infoblox.log")
        keyword1=len(re.findall(r'DNS cache acceleration is now started', result))
        keyword2=len(re.findall(r'missing sppc configuration in view', result))
        keyword3=len(re.findall(r'notice DNS cache acceleration configuration error', result))
        if ((keyword1 >= 1) and (keyword2 == 0) and (keyword3 == 0)): 
            display_msg("Error not found, DCA service is running. Log validation successful")
            assert True
        else:
            assert False 

    @pytest.mark.run(order=11)
    def test_111_stop_DCA_service(self):
        display_msg("Stopping DCA service...\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"enable_dns_cache_acceleration": False}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        sleep(10)
        logging.info(response)
        print (response)
        sleep(20)
        print("DCA service stopped in master")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[1]['_ref']
        data = {"enable_dns_cache_acceleration": False}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        sleep(10)
        logging.info(response)
        print (response)
        sleep(20)
        print("DCA service stopped in member")
        


    @pytest.mark.run(order=12)
    def test_112_cleanup(self):
        display_msg("Cleanup: Starting DHCP swervices in GM and member\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[1]['_ref']
        data = {"enable_dhcp": True}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        sleep(10)
        print (response)
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"enable_dhcp": True}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        sleep(10)
        print (response)
        


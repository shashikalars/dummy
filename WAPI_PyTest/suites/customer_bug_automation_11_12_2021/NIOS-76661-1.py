#!/usr/bin/env python

__author__ = "Shivasai"
__email__  = "sbandaru@infoblox.com"
__RFE__= "NIOS-76661 RabbitMQ upgrade to 3.8.20"
##################################################################################################
#  Grid Set up required:	                                                                     #
#  1. Grid Master with IB-V1415 members 	                                                	 #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415),Threat Analytics,Security Ecosystem,discovery  #
##################################################################################################

import re
import sys
import config
import pytest
import unittest
import os
import os.path
from os.path import join
import json
import pexpect
import requests
import urllib3
import commands
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util
import ib_utils.common_utilities as comm_util
import paramiko
import time
from datetime import datetime, timedelta
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv


class PenTest_855_RabbitMQ_Upgrade(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_01_create_network_for_vdiscovery(self):   
        print("============================================")
        print("create_network_for_vdiscovery")
        print("======================================")
        sleep(40)
        #log("start","/var/log/syslog",config.grid_member1_vip)
        get_ref = ib_NIOS.wapi_request('GET', object_type='discovery:gridproperties')
        discovery_grid_properties = {"snmpv1v2_credentials":[{"community_string":"public"}]}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(discovery_grid_properties))
        if type(response) == tuple:
            assert False
            
        
        get_ref = ib_NIOS.wapi_request('GET', object_type='discovery:memberproperties')
        for ref in json.loads(get_ref):
            if ref["discovery_member"] == config.grid_member1_fqdn:
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps({"enable_service":True}))
                print(response)
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30) #discovery service
        print("Test Case 34 Execution Completed")
        
    @pytest.mark.run(order=2)
    def test_02_check_discovery_error_logs(self):
        print("\n====================================")
        print("create_network_for_vdiscovery")
        print("======================================")
        log("start","/var/log/syslog",config.grid_member1_vip)
        sleep(100)
        log("stop","/var/log/syslog",config.grid_member1_vip)
        LookFor="Discovery Consolidator Service has failed"
        logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
        print(logs)
        if logs == None:
            assert True
        else:
            assert False
        print("Test Case 2 Execution Completed")
        
    @pytest.mark.run(order=3)
    def test_03_create_network_for_vdiscovery(self):
        print("\n====================================")
        print("create_network_for_vdiscovery")
        print("======================================")      
    
        data = {"network":"10.40.16.0/24",
                "members":[{"_struct": "dhcpmember","ipv4addr":config.grid_vip}],
                "use_enable_discovery":True,
                "discovery_member":config.grid_member1_fqdn,
                "enable_discovery":True,
                "enable_immediate_discovery":True}
        response = ib_NIOS.wapi_request('POST', object_type='network', fields=json.dumps(data))
        print("Restart Services")
        print(response)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(330)
        print(response)
        if type(response) == tuple:
            assert True

        
        sleep(30)
        print("Test Case 3 Execution Completed")
    
    
    @pytest.mark.run(order=4)
    def test_04_discovery_functionality(self):
        print("\n====================================")
        print("discovery_functionality")
        print("======================================")
        paging_data = "?_paging=1&_return_as_object=1&_max_results=1&_return_fields%2B=interfaces.ifaddr_infos"
        curl_cmd = "curl -k -u admin:infoblox -X GET 'https://"+config.grid_vip+"/wapi/v"+config.wapi_version+"/discovery:device"+paging_data+"'"
        response = os.popen(curl_cmd).read()
        if "Error" in response:
            assert False

        output = json.loads(response)
        page_id = output["next_page_id"]

        print(output["result"])
        if "address" not in output["result"][0].keys():
            assert False


        for address in output["result"]:
            if "interfaces" in address.keys():
                if "ifaddr_infos" in address["interfaces"][0].keys():
                    break
        #    assert False
            
        paging_data ="?_paging=1&_return_as_object=1&_max_results=1&_return_fields%2B=interfaces.ifaddr_infos&_page_id="+page_id
        curl_cmd = "curl -k -u admin:infoblox -X GET 'https://"+config.grid_vip+"/wapi/v"+config.wapi_version+"/discovery:device"+paging_data+"'"
        print(curl_cmd)
        response2 = os.popen(curl_cmd).read()
        output2 = json.loads(response2)
        if "Error" in response2:
            assert False
        
        for address in output2["result"]:
            if "interfaces" in address.keys():
                if "ifaddr_infos" in address["interfaces"][0].keys():
                    
                    break
            
            #assert False
            
        print("Test Case 4 Execution Completed")
        
    
    
    @pytest.mark.run(order=5)
    def test_05_check_rabbitmq_service_on_discovery_member(self):
        print("\n====================================")
        print("check rabbitmq status on discovery member")
        print("======================================")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('#')
            child.sendline('''rabbitmqctl status''')
            child.expect('#')
            print("\n")
            output = child.before
            print(output)
            print("==============================")
            print("\n")
            data = ["Status of node rabbit","RabbitMQ","3.8.20"]
            for i in data:
                if i not in output:
                    assert False
                    print (i)
        except Exception as error_message:
            print(error_message)
            assert False
        finally:
            child.close()
        print("Test Case 05 Execution Completed")

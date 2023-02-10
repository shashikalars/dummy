#!/usr/bin/env python
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. IB-FLEX + SA configuration (M1 + MGMT)                                #
#  2. M1 License : TP                                                       #
#############################################################################

import re
import config
import pytest
import unittest
import logging
import subprocess
import os
import sys
import json
import commands
import json, ast
import requests
from time import sleep as sleep
import ib_utils.ib_NIOS as ib_NIOS
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv
import ib_utils.ib_papi as papi
'''
Need to add MGMT for mrmber + config.py chnage 10.35 to 10.36
'''
class NIOSSPT_10161(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_Upload_TP_ruleset(self):
        print("Start DNS Service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        print(get_ref)
        for ref in json.loads(get_ref):

            data = {"enable_dns": True}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
            print response
            sleep(20)
            print(response)
            read  = re.search(r'200',response)
            for read in  response:
                assert True

        print("Enable automatic download")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:threatprotection",grid_vip=config.grid_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            if ref["grid_name"]== 'Infoblox':
                ref1 = ref['_ref']
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps({"enable_auto_download": True}),grid_vip=config.grid_vip)
                print(response)
                if type(response) == tuple:
                    print("Failure: Enable automatic download in threat protection service")
                    assert False
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("sleep 30 seconds for threat protection rules to download")
                sleep(30)
        print("-"*6+"Enabling Threat protection service"+"-"*6)
        print("Enable the threat protection service on member")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        print(get_ref)
        for ref in json.loads(get_ref):
            ref1 = json.loads(get_ref)[0]['_ref']
            response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps({"enable_service": True}),grid_vip=config.grid_vip)
            print(response)
            if type(response) == tuple:
                print("Failure: Enable threat protection service")
                assert False
        sleep(300)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)

    @pytest.mark.run(order=2)
    def test_001_create_zone(self):
        print("Add Authoritative zone in grid")
        data = {"fqdn" : "test.com","grid_primary": [{"name": config.grid_member1_fqdn,"stealth": False}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
        print(response)
        res=json.loads(response)
        
        if type(response) == tuple:
            assert False
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)
        
    @pytest.mark.run(order=3)
    def test_002_enable_query_response_in_grid_logging(self):
        data={"logging_categories": {
            "log_client": True,
            "log_config": True,
            "log_database": True,
            "log_dnssec": True,
            "log_dtc_gslb": False,
            "log_dtc_health": False,
            "log_general": True,
            "log_lame_servers": True,
            "log_network": True,
            "log_notify": True,
            "log_queries": True,
            "log_query_rewrite": False,
            "log_rate_limit": True,
            "log_resolver": True,
            "log_responses": True,
            "log_rpz": False,
            "log_security": True,
            "log_update": True,
            "log_update_security": True,
            "log_xfer_in": True,
            "log_xfer_out": True
        }}
        
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
        print(get_ref)
        print(json.loads(get_ref)[0]['_ref'])
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
            print response
            if type(response) == tuple:
                assert False
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)

    @pytest.mark.run(order=4)
    def test_003_enable_mgmt_port_for_dns(self):
        ref=ib_NIOS.wapi_request('GET', object_type="member:dns")
        ref=json.loads(ref)[0]['_ref']
        data={"enable_dns":True,"use_mgmt_port":True}
        ref1=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
        logging.info (ref1)
        sleep(60)
            

        
    @pytest.mark.run(order=5)
    def test_004_validate_logs_after_sending_dig_query(self):
        print("validating var logs after sending dig query")
        log("start","/var/log/syslog",config.grid_member1_vip)
        sleep(10)
        #dig_cmd = 'dig @'+config.grid_member1_vip+' test.com +noedns +norec +noad +zflag'
        #dig_cmd = 'dig @'+config.grid_member1_vip+' test.com +noedns +norec +noad'
        dig_cmd = '/import/tools/qa/bin/dnsq -ns='+config.grid_member1_vip+' -qname=test.com -z=1'
        print(dig_cmd)
        dig_cmd1 = os.system(dig_cmd)
        sleep(10)
        log("stop","/var/log/syslog",config.grid_member1_vip)
        lookfor = [".*test.com.*query.*test.com IN A .*"+config.grid_member1_vip,"UDP: query: test.com IN A response: NOERROR -A"]
        for look in lookfor:
            result = logv(look, '/var/log/syslog', config.grid_member1_vip)
            print(result)
            if not result:
                print("Failure: Validate messages test.com zone with zbit flag enable")
                assert False
        print("Success: Validate messages test.com zone with zbit flag enable")

        
    @pytest.mark.run(order=6)
    def test_005_cleanup(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth')
        print(get_ref)
        for ref in json.loads(get_ref):
            if ref['fqdn'] == 'test.com':
                response = ib_NIOS.wapi_request('DELETE', ref = ref['_ref'])
                print(response)
                if type(response) == tuple:
                    print("Failure: Delete auth zone test.com")
                    assert False
                    
        ref=ib_NIOS.wapi_request('GET', object_type="member:dns")
        ref=json.loads(ref)[0]['_ref']
        data={"enable_dns":False,"use_mgmt_port":False}
        ref1=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
        logging.info (ref1)
        sleep(30)
        print("Disable the threat protection service on member")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        print(get_ref)
        for ref in json.loads(get_ref):
            ref1 = json.loads(get_ref)[0]['_ref']
            response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps({"enable_service": False}),grid_vip=config.grid_vip)
            print(response)
            if type(response) == tuple:
                print("Failure: disable threat protection service")
                assert False
        sleep(30)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)

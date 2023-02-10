"""
 Copyright (c) Infoblox Inc., 2016

 ReportName          : User_Login_History
 ReportCategory      : Network User
 Number of Test cases: 1
 Execution time      : 93.58
 Execution Group     : Minute Group (MG)
 Description         : User Login History report will update every 1 min

 Author   : Raghavendra MN
 History  : 06/01/2016 (Created)
 Reviewer : Raghavendra MN
"""
import config
import json
import os
import pytest
import pexpect
import re
import sys
import subprocess
import time 
import unittest

import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from logger import logger
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results

"""
TEST Steps:
      1.  Input/Preparaiton      : Adding Network View say 'network_user_view'.
                                   Adding network say 170.0.0.0/24 & 180.0.0.0/24
                                   Adding network users say 'first', 'Second' with differet address, domainname and guid. 
      2.  Search                 : Performing Search operaiton. 
      3.  Validation             : Validation against input data.
"""


class UserLoginHistory(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        logger.info('-'*15+"START:User Login History"+'-'*15)

        logger.info("Enabling Network User")     
        grid_ref = ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid_ref)[0]['_ref']
        enable_network_user = {"ms_setting" : {"enable_network_users":True,"enable_ad_user_sync": True}}
        response = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(enable_network_user))
       
        logger.info("Adding Network View 'network_user_view'")
        network_view = {"name":"network_user_view"}
        response = ib_NIOS.wapi_request('POST', object_type="networkview", fields=json.dumps(network_view))

        logger.info("Add network 170.0.0.0/24 & 180.0.0.0/24 under 'network_user_view'")
        network_data = {"network":"170.0.0.0/24","network_view":"network_user_view"}
        response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(network_data))

        network_data = {"network":"180.0.0.0/24","network_view":"default"}
        response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(network_data))

        logger.info("Add network user:first, address:170.0.0.1, doamin:ad-domain20,guid:100")
        first_seen_time=ib_get.indexer_epoch_time(config.indexer_ip)
        network_user = {"name":"first","address":"170.0.0.1","domainname":"ad-domain20","first_seen_time":first_seen_time,"guid":"100", \
        "network_view":"network_user_view","logon_id":"user1"}
        response = ib_NIOS.wapi_request('POST', object_type="networkuser", fields=json.dumps(network_user))


        logger.info("Add network user:second,address:170.0.0.2, doamin:ad-domain21,guid:101")
        network_user = {"name":"second","address":"170.0.0.2","domainname":"ad-domain21","first_seen_time":first_seen_time,"guid":"101", \
        "network_view":"network_user_view","logon_id":"user2"}
        response = ib_NIOS.wapi_request('POST', object_type="networkuser", fields=json.dumps(network_user))


        logger.info("Add network user:third,address:180.0.0.1, doamin:ad-domain22,guid:102")
        network_user = {"name":"third","address":"180.0.0.1","domainname":"ad-domain22","first_seen_time":first_seen_time,"guid":"102", \
        "network_view":"default","logon_id":"user3"}
        response = ib_NIOS.wapi_request('POST', object_type="networkuser", fields=json.dumps(network_user))

        logger.info("Add network user:fourth,address:180.0.0.2, doamin:ad-domain23,guid:103")
        network_user = {"name":"fourth","address":"180.0.0.2","domainname":"ad-domain23","first_seen_time":first_seen_time,"guid":"103", \
        "network_view":"default","logon_id":"user4"}
        response = ib_NIOS.wapi_request('POST', object_type="networkuser", fields=json.dumps(network_user))

        logger.info("Performing restart service")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        logger.info("Waiting for 30 sec.,")
        time.sleep(30) #wait for 30 sec, for Member Restar

        #Preparation for Test Case#1
        logger.info("Preparation for test case#1")
        first_last_seen= time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(float(first_seen_time)))
        cls.test1=   [ \
        { "User Name":"fourth", "Domain":"ad-domain23", "IP Address":"180.0.0.2", "First Seen":first_last_seen,"Last Seen":first_last_seen, \
        "User Status":"ACTIVE" }, \
        { "User Name":"third", "Domain":"ad-domain22", "IP Address":"180.0.0.1",  "First Seen":first_last_seen,"Last Seen":first_last_seen, \
        "User Status":"ACTIVE" }, \
        { "User Name":"second", "Domain":"ad-domain21", "IP Address":"170.0.0.2", "First Seen":first_last_seen, "Last Seen":first_last_seen, \
        "User Status":"ACTIVE" }, \
        { "User Name":"first", "Domain":"ad-domain20", "IP Address":"170.0.0.1", "First Seen":first_last_seen, "Last Seen":first_last_seen, \
        "User Status":"ACTIVE" } ]
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))
        logger.info("Wait for 60 sec., to update reports")
        time.sleep(60) #wait for report update

    def test_1_user_login_history_validate_domain_ipaddress_first_and_last_seen(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
        search_str=r"search sourcetype=ib:reserved1 source=ib:user:user_login index=ib_security | eval TIMEOUT_KEY=\"ad_user_default_timeout\" | lookup users_timeout_value_lookup TIMEOUT_KEY output TIMEOUT_VAL | eval TIMEOUT_VALUE=if(isnull(TIMEOUT_VAL),18000,TIMEOUT_VAL*60) | eval last_activeEpoch=if(isnum(last_active), last_active, strptime(last_active, \"%Y-%m-%d %H:%M:%S\")) | eventstats latest(last_activeEpoch) as l_last_active by user_name, ip_address, login_time | eval status=if((last_activeEpoch=l_last_active) AND (status==\"ACTIVE\") AND ((last_activeEpoch+TIMEOUT_VALUE)<now()),\"TIMEOUT\",status) | sort -_time | eval last_active=if(isnum(last_active), strftime(last_active, \"%Y-%m-%d %H:%M:%S\"), last_active) | eval last_updated=if(isnum(last_updated), strftime(last_updated, \"%Y-%m-%d %H:%M:%S\"), last_updated) | eval logout_time=if(isnum(logout_time), strftime(logout_time, \"%Y-%m-%d %H:%M:%S\"), logout_time) | eval login_time=if(isnum(login_time), strftime(login_time, \"%Y-%m-%d %H:%M:%S\"), login_time) | rename timestamp as Time, user_name as \"User Name\", login_time as \"First Seen\", logout_time as \"Logout Time\", last_active as \"Last Seen\", last_updated as \"Last Updated\", ip_address as \"IP Address\", domain as \"Domain\", status as \"User Status\",  | table \"Last Updated\" \"User Name\" \"Domain\" \"IP Address\" \"First Seen\" \"Logout Time\" \"Last Seen\" \"User Status\""
        cmd = config.search_py + " \"" + search_str + "\" --output_mode=json"
        os.system(cmd)
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        results_dist= results_list[-240::1]
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test1,results_dist)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        result = compare_results(self.test1,results_list)
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg

    @classmethod
    def teardown_class(cls):
        logger.info("Cleanup, deleting added network") 
        network_data = ib_NIOS.wapi_request('GET', object_type="network?network~=180.0.0.0/24")
        ref = json.loads(network_data)[0]['_ref']
        del_status = ib_NIOS.wapi_request('DELETE', object_type = ref)
   
	network_view = ib_NIOS.wapi_request('GET', object_type="networkview?name~=network_user_view")
        ref = json.loads(network_view)[0]['_ref']
        del_status = ib_NIOS.wapi_request('DELETE', object_type = ref)
        logger.info('-'*15+"STOP:User Login History"+'-'*15)

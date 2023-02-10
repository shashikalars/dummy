"""
 Copyright (c) Infoblox Inc., 2016

 Report Name          	: 	1) DNS Top Tunneling by Category(Detailed)
				
					   
 Report Category      	: 	DNS Top Tunneling 
 Number of Test cases	: 	1
 Execution time     	: 	2.99 seconds
 Execution Group     	: 	Minute Group (MG)
 Description         	: 	Validating Resource Availability Trend by Server health status, this Report will update immediately after 10 minutes. 
				Validating Pool Availability Trend by Pool health status, this Report will update immediately after 10 minutes.
					   
 Author			:	Shashikala R S
 History		:	03/09/2021 (Created)
"""
import config
import json
import os
import pytest
import pexpect
import re
import sys
import subprocess
import unittest
import time
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from logger import logger
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results

"""
TEST Steps:
	1.  Input/Preparation  : 
            
						
	2.  Search     : Performing Search operation with default/custom filter
	3.  Validation : comparing Search results with Retrieved 'DNS Top Tunneling by Category'
    """

class dns_top_tunneling_by_Category(unittest.TestCase):
    @classmethod
    def setup_class(cls):   
        logger.info('-'*15+"START : DNS Top Tunneling by Category"+'-'*15)
               
        cls.test1=[]
        temp={}
        temp["Description (DNS View)"]="This rule detects a Base32-encoded SSH 2.0 payload over TCP (which could be OzymanDNS/SplitBrain DNS Tunneling traffic). (N/A)"
        temp["Category"]="Known Tunneling Encoding"
        temp["Category%"]="25.00"
        #temp["Events"]="1"
        cls.test1.append(temp)
        
        
    def test_1_dns_tunneling_by_Category(self):
        logger.info("Test:"+sys._getframe().f_code.co_name)       
        search_str=r"search source=ib:ddos:ip_rule_stats index=ib_security | lookup atp_rule_sid_lookup RULE_SID output RULE_DESCRIPTION, DNST_CATEGORY | append [ search source=* index=ib_dns | lookup dns_viewkey_displayname_lookup VIEW output display_name | rename display_name as DNS_VIEW | join DNS_VIEW [ | inputlookup analytics_rpz_lookup | stats values(ANALYTICS_RPZ) as ANALYTICS_RPZ by DNS_VIEW ] | makemv ANALYTICS_RPZ | mvexpand ANALYTICS_RPZ | where like(RPZ_QNAME, \"%\" + ANALYTICS_RPZ) | table TOTAL_COUNT, CLIENT, MITIGATION_ACTION, ANALYTICS_RPZ, DNS_VIEW, _time | where MITIGATION_ACTION != \"ER\" | eval DNST_CATEGORY=\"Detected by Analytics Engine\" | eval RULE_DESCRIPTION=ANALYTICS_RPZ | stats sum(TOTAL_COUNT) as ACTIVE_COUNT by CLIENT, DNST_CATEGORY, RULE_DESCRIPTION, ANALYTICS_RPZ, DNS_VIEW, _time | eval SOURCE_IP=CLIENT ] | eval DNS_VIEW = if(isnull(DNS_VIEW),\"N/A\",DNS_VIEW) | eval RULE_DESCRIPTION = RULE_DESCRIPTION + \" (\" + DNS_VIEW + \")\" | stats sum(ACTIVE_COUNT) as ACTIVE_COUNT_SUM by RULE_DESCRIPTION, DNST_CATEGORY, DNS_VIEW | sort -ACTIVE_COUNT_SUM | head 10 | eventstats sum(ACTIVE_COUNT_SUM) as EVENTS_TOTAL | eval Percentage=round(ACTIVE_COUNT_SUM*100/EVENTS_TOTAL, 2) | rename DNST_CATEGORY as Category, Percentage as \"Category%\", RULE_DESCRIPTION as \"Description (DNS View)\", ACTIVE_COUNT_SUM as Events | table \"Description (DNS View)\", Category, Events, \"Category%\""
    
        cmd = config.search_py + " \"" + search_str + "\" --output_mode=json"
        logger.info (cmd)
        print(os.system(cmd))
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operation failed, Please check Grid Configuration")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        results_dist= results_list[-240::1]
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        print(results_dist)
        first=results_dist[0]
        print(first)
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

        if first['Category'] == "Known Tunneling Encoding" and first['Category%'] >= 0 and first['Events'] >= 0:
            print("-----------------------------------------")
            print("--------------***********----------------")
            print("PASSED")
            logger.info("Search validation result: %s(PASS)",first)
            assert True

        else:
            logger.error("Search validation result: %s(FAIL)",first)

            msg = 'Count does not match - %s', first
            assert False

	'''        
	search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test1,results_dist)
        logger.info("compare_resutls with 'delta'=.5")
        result = compare_results(self.test1,results_list,.5)
        logger.info("-----------------------------------------------------")
        logger.info(self.test1)
        logger.info(len(self.test1))
        logger.info("--------------Adding Debugging line ------------------")
        logger.info(results_list)
        logger.info(len(results_list))
        logger.info("-----------------------------------------------------")
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg
	'''

    @classmethod
    def teardown_class(cls):
	
        logger.info("Cleanup: Delete all DTC Objects and Zone Associated with it")
        	
        logger.info('-'*15+"END:DNS Top Tunneling by Category"+'-'*15)

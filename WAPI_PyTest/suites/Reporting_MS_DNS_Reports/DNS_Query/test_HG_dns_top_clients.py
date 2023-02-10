"""
 Copyright (c) Infoblox Inc., 2016
 ReportName          : DNS Top Clients
 ReportCategory      : DNS Query 
 Number of Test cases: 1
 Execution time      : 302.61 seconds
 Execution Group     : Hour Group (HG)
 Description         : DNS Top Clients, This report will be udpated every one hour

 Author : Raghavendra MN
 History: 05/26/2016 (Created)
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
from time import sleep

import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from logger import logger
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results

"""
TEST Steps:
      1.  Input/Preparation  : Prparation will be called by separte script as reports will be updated every one hour 
          a.Adding zones say 'dns_top_clients.com' and RR's.
          b.Next performing Query from differnt Clients
            Client#1: 10000
	    Client#2: 11000
	    Client#3: 12000
	    Client#4: 13000
	    Client#5  14000
      2.  Search     : Performing Search operaion with default/custom filter
      3.  Validation : comparing Search results with Reterived 'DNS Top Clients per Domain' report without delta.
"""

class DNSTopClients(unittest.TestCase):
    @classmethod
    #Preparation
    def setup_class(cls):
        logger.info('-'*15+"START:DNS Top Clients"+'-'*15)
        logger.info ("Preparation has executed 1 hour before as this report will take 1 hour to update")

    def test_1_Default_Filter_validate_DNS_Top_Clients(self):
        
	logger.info("TestCase:test_1_Default_Filter_validate_DNS_Top_Clients_per_Domain")
        
	search_str="search index=ib_dns_summary report=si_dns_top_clients(orig_host=\"*\")* | eval resolved_names_or_ips=coalesce(ms_resolved_names,ms_resolved_ips)| eval resolved_names_or_ips=if(isnull(resolved_names_or_ips),MS_SERVER,resolved_names_or_ips)| stats sum(COUNT) as CLIENT_QUERIES by CLIENT| sort -CLIENT_QUERIES| head 10| eventstats sum(CLIENT_QUERIES) as TOTAL| eval PERCENT=round(CLIENT_QUERIES*100/TOTAL,1)| eval PCLIENT=CLIENT | rename PCLIENT as Client, CLIENT_QUERIES as Queries| fields Client, Queries | noop"

        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        print("EXECUTION OF SEARCH STRING COMMAND",cmd)

        print(os.system(cmd))
        print("*****************%%%%%*********************")

        try:
            retrived_data=open(config.json_file).read()
            print(retrived_data)

        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']

        results_dist= results_list[-240::1]

        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        print(results_dist)
        first=results_dist[0]
        print(first)
	second=results_dist[1]
        print(second)

        if first['Queries'] >= 0 and second['Queries'] >= 0:
            print("--------------***********----------------")
            print("Successfully PASSED")
            logger.info("Search validation result: %s (PASS)",first)

        else:
            logger.error("Search validation result: %s (FAIL)",first)

            msg = 'Count does not match - %s', first
            assert first == 0, first


    #Clean up
    @classmethod
    def teardown_class(cls):
        #deleting zones
        logger.info("Cleanup: Removing zones which was added in preparation step.")
        #del_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn~=dns_top_clients.com")
        #ref = json.loads(del_zone)[0]['_ref']
        #del_status = ib_NIOS.wapi_request('DELETE', object_type = ref)
        logger.info('-'*15+"END:DNS Top Clients"+'-'*15)

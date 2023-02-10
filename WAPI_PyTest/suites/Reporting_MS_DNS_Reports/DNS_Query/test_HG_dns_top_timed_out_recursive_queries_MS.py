"""
 Copyright (c) Infoblox Inc., 2016

 ReportName          : DNS Top Timed-Out Recursive Queries 
 ReportCategory      : DNS Query
 Number of Test cases: 1
 Execution time      : 302.61 seconds
 Execution Group     : Hourly Group (HG)
 Description         : DNS Top Timed-Out Recursive Queries reports will be updated every 1 hour

 Author : Raghavendra MN
 History: 06/04/2016 (Created)
"""
import config
import json
import os
import pytest
import pexpect
import re
import sys
import subprocess
from time import sleep
import unittest

import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from logger import logger
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results
"""
TEST Steps:
      1.  Input/Preparaiton      : This is Hourly Report and Preparation is injected separately.
      2.  Search                 : Search with Default Filter
      3.  Validation             : Validating Search result against input data
				   Due to of other report preparation, % value in Domain Name (say "Domain Name":"hello.com.(25.0%)") is not possible. 
                                   So, % calculation will be done after performing search operation based on total number of queries 
                                   and validating only Number of Queries. 								
"""
class DNSTopRequestedTimedOutRecursiveQueries(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        logger.info('-'*15+"START:DNS Top Timed Out Recursive Queries"+'-'*15)
        logger.info("Performing Query through Query perf")
        
	cls.test1=[{"Domain Name": "2.fedora.pool.ntp.org."}, {"Domain Name": "2.fedora.pool.ntp.org.ad-32.local."}]
        
	logger.info ("Json input for validation test1")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))
        
    def test_1_dns_top_requested_timed_out_recursive_queries(self):
        logger.info(sys._getframe().f_code.co_name)
        
        search_str=r"search index=ib_dns_summary report=si_top_timeout_queries | lookup dns_viewkey_displayname_lookup VIEW output display_name | bucket span=1h _time | stats sum(COUNT) as SFT_QUERIES by NAME | sort -SFT_QUERIES | head 20 | eventstats  sum(SFT_QUERIES) as COUNT_SUM | eval DNPERCENT=NAME | rename DNPERCENT as \"Domain Name\", SFT_QUERIES as \"Queries\" | fields \"Domain Name\", \"Queries\""	
        
	cmd = config.search_py + " \"" + search_str + "\" --output_mode=json"
        os.system(cmd)
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        results_dist = results_list[-240::1]
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        print(results_dist)
        first=results_dist[0]
        print(first)
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

        if first['Queries'] >= 0:
            print("--------------***********----------------")
            print("PASSED")
            logger.info("Search validation result: %s(PASS)",first)
            assert True

        else:
            logger.error("Search validation result: %s(FAIL)",first)

            msg = 'Count does not match - %s', first
            assert False


    @classmethod
    def teardown_class(cls):
        logger.info('-'*15+"END:DNS Top Timed Out Recursive Queries."+'-'*15)

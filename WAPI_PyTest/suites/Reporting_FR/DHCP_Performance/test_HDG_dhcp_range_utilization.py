"""
 Copyright (c) Infoblox Inc., 2016
 ReportName          : DHCP Range Utilization
 ReportCategory      : DHCP Performance.
 Number of Test cases: 1
 Execution time      : 302.61 seconds
 Execution Group     : Hour Group (HG)
 Description         : DHCP Performance'.

 Author   : Manimaran
 History  : 06/01/2016 (Created)
 Reviewer : Raghavendra MN
"""
import pytest
import unittest
import logging
import subprocess
import json
import os
import ib_utils.ib_validaiton as ib_validation
import ib_utils.ib_system as ib_system
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
import config
import pexpect
import sys
import random

import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from logger import logger
from time import sleep
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results
"""
TEST Steps:
      1.  Input/Preparation  : Prparation will be called by separte script as reports will be updated every one hour
                               a. Create a custom network view custom_view_1, create 2 MAC Filters and add below networks.
                                  10.0.0.0/8
                                  30.0.0.0/24 with range 30.0.0.1 to 30.0.0.50 and fixed address as 30.0.0.32.
                                  32.0.0.0/24 with range 32.0.0.1 to 32.0.0.25 and fixed address as 32.0.0.32.
                                  Request 1 lease for both 30.0.0.0/24 and 32.0.0.0/24
      2.  Search     : Performing Search operaion with default/custom filter
      3.  Validation : comparing Search results with Reterived 'DHCPv4 Range Utilization Trend' report without delta.
"""

class DHCPRangeUtilization(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        logger.info('-'*15+"START:DHCP Range Utilization Report"+'-'*15)
        logger.info ("Preparation has executed 1 hour before as this report will take 1 hour to update")

        cls.test1=[]
        temp={}
        temp["30.0.0.1-30.0.0.50"]="4.0"
        cls.test1.append(temp)
        
        logger.info ("Input Json for validation")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))

    def test_1_dhcp_range_utilization(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
        search_str=r"search index=ib_dhcp_summary report=si_dhcp_range_utilization_trend  DHCP_RANGE=\"30.0.0.1-30.0.0.50\" | noop  | eval members=if(isnull(members), \"\", members) | where like(members, \"%\") | eval ms_servers=if(isnull(ms_servers), \"\", ms_servers) | stats avg(dhcp_utilization) as ADU by _time view members ms_servers start_address end_address DHCP_RANGE dhcp_utilization_status | noop  | timechart bins=1000 eval(avg(ADU)/10) by DHCP_RANGE where max in top5 useother=f |  rename _time as Time | eval Time=strftime(Time, \"%Y-%m-%d %H:%M:%S %Z\")"
        cmd = config.search_py + " \"" + search_str + "\" --output_mode=json"
        logger.info (cmd) 
        os.system(cmd)
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operation failed, Please check Grid Configuration")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test1,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_results")
        result = compare_results(self.test1,results_list)
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg

    @classmethod
    def teardown_class(cls):
        logger.info('-'*15+"END:DHCP Range Utilization report"+'-'*15)
 

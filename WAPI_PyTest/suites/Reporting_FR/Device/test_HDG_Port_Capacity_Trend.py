"""
 Copyright (c) Infoblox Inc., 2016
 ReportName          : Port Capacity Trend
 ReportCategory      : Devices.
 Number of Test cases: 1
 Execution time      : 302.61 seconds
 Execution Group     : Hour Group (HG)
 Description         : Devices'.

 Author   : Manimaran
 History  : 05/24/2016 (Created)
 Reviewer : Raghavendra MN
"""
import pytest
import unittest
import logging
import subprocess
import json
import ConfigParser
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
				     a. Added 10.40.16.0/24 network and Edit Grid Discovery Properties
				        SNMPv1/v2  - public, devsnmp
				        CLI        - protocol as SSH, Telnet and Name as 'Admin' and 'Password' as 'infoblox'
				                     protocol as SSH, Telnet and 'Password' as 'infoblox'
					Enable all the checkbox in Polling -> Basic Tab.
				     b. Edit 10.40.16.0/24 network and start discovery in Discovery tab.
      2.  Search     : Performing Search operaion with default/custom filter
      3.  Validation : comparing Search results with Reterived 'Port Capacity Trend' report without delta.
"""

class PortCapacityTrend(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        logger.info('-'*15+"START:Port Capacity Trend"+'-'*15)
        cls.test1=[]
        temp={}
        temp["Admin-Down/Operation-Down"]="20"
        temp["Admin-Up/Operation-Down"]="286"
        temp["Admin-Up/Operation-Up"]="46"
        temp["Total Available"]="352"
        cls.test1.append(temp)
        
        logger.info ("Creating input in json format for Port Capacity Trend")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))

    def test_1_port_capacity_trend(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
        search_str=r"search source=ib:discovery:port_capacity index=ib_discovery | timechart span=1d dc(EVTIME) as DAILY_SNAPSHOT_COUNT sum(TOTAL_AVAIL_COUNT)  as SUM_TOTAL_AVAIL_COUNT sum(ADM_UP_OP_UP_COUNT) as SUM_ADM_UP_OP_UP_COUNT sum(ADM_UP_OP_DN_COUNT) as SUM_ADM_UP_OP_DN_COUNT | eval DAILY_TOTAL_AVAIL_COUNT = round(SUM_TOTAL_AVAIL_COUNT / DAILY_SNAPSHOT_COUNT) | eval DAILY_ADM_UP_OP_UP_COUNT = round(SUM_ADM_UP_OP_UP_COUNT / DAILY_SNAPSHOT_COUNT) | eval DAILY_ADM_UP_OP_DN_COUNT = round(SUM_ADM_UP_OP_DN_COUNT / DAILY_SNAPSHOT_COUNT) | eval \"Admin-Down/Operation-Down\" = DAILY_TOTAL_AVAIL_COUNT - DAILY_ADM_UP_OP_UP_COUNT - DAILY_ADM_UP_OP_DN_COUNT  | rename DAILY_TOTAL_AVAIL_COUNT  as \"Total Available\" DAILY_ADM_UP_OP_UP_COUNT as \"Admin-Up/Operation-Up\" DAILY_ADM_UP_OP_DN_COUNT as \"Admin-Up/Operation-Down\" | fields - DAILY_SNAPSHOT_COUNT SUM_TOTAL_AVAIL_COUNT SUM_ADM_UP_OP_UP_COUNT SUM_ADM_UP_OP_DN_COUNT"
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
        logger.info('-'*15+"END:Port Capacity Trend"+'-'*15)

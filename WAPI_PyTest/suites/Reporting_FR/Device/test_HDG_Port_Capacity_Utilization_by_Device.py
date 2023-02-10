"""
 Copyright (c) Infoblox Inc., 2016
 ReportName          : Port Capacity Utilization
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
      3.  Validation : comparing Search results with Reterived 'Device Class Trend' report without delta.
"""

class PortCapacityUtilization(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        logger.info('-'*15+"START:Port Capacity Utilization"+'-'*15)

        cls.test1=[]
        temp={}
        temp["Device Name"]="AugustaLab-Arista-DCS-7048T.inca.infoblox.com"
        temp["Admin-Up/Operation-Down"]="50"
        temp["Admin-Up/Operation-Up"]="3"
        temp["Admin-Down/Operation-Down"]="0"
        temp["Network View"]="discovery_view"
        temp["Total Available"]="53" 
        cls.test1.append(temp)
        
        temp={}
        temp["Device Name"]="DELL-PC8024F"
        temp["Admin-Up/Operation-Down"]="22"
        temp["Admin-Up/Operation-Up"]="2"
        temp["Admin-Down/Operation-Down"]="0"
        temp["Total Available"]="24"
        temp["Network View"]="discovery_view"
        cls.test1.append(temp)

        logger.info ("Creating input in json format for Port Capacity Utilization")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))

    def test_1_port_capacity_utilization(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
        search_str=r"search source=ib:discovery:port_capacity index=ib_discovery | stats avg(TOTAL_AVAIL_COUNT)  as AVG_TOTAL_AVAIL_COUNT avg(ADM_UP_OP_UP_COUNT) as AVG_ADM_UP_OP_UP_COUNT avg(ADM_UP_OP_DN_COUNT) as AVG_ADM_UP_OP_DN_COUNT by NETWORK_VIEW DEVICE_NAME | eval DAILY_TOTAL_AVAIL_COUNT = round(AVG_TOTAL_AVAIL_COUNT) | eval DAILY_ADM_UP_OP_UP_COUNT = round(AVG_ADM_UP_OP_UP_COUNT) | eval DAILY_ADM_UP_OP_DN_COUNT = round(AVG_ADM_UP_OP_DN_COUNT) | eval \"Admin-Down/Operation-Down\" = DAILY_TOTAL_AVAIL_COUNT - DAILY_ADM_UP_OP_UP_COUNT - DAILY_ADM_UP_OP_DN_COUNT  | rename DEVICE_NAME as \"Device Name\" NETWORK_VIEW as \"Network View\" DAILY_TOTAL_AVAIL_COUNT  as \"Total Available\" DAILY_ADM_UP_OP_UP_COUNT as \"Admin-Up/Operation-Up\" DAILY_ADM_UP_OP_DN_COUNT as \"Admin-Up/Operation-Down\"          | table \"Device Name\" \"Admin-Up/Operation-Up\" \"Admin-Down/Operation-Down\" \"Admin-Up/Operation-Down\" \"Total Available\" \"Network View\" | sort +str(\"Device Name\") +str(\"Network View\")"
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
        logger.info('-'*15+"END:Port Capacity Utilization"+'-'*15)

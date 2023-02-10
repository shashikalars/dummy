"""
 Copyright (c) Infoblox Inc., 2016
 ReportName          : Port Capacity Delta by Device
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
from time import sleep
from logger import logger 
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

class PortCapacityDeltaByDevice(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        logger.info('-'*15+"START:Port Capacity Delta By Device"+'-'*15)

        cls.test1=[]
        temp={}
        temp["Device Name"]="AugustaLab-Arista-DCS-7048T.inca.infoblox.com"
        temp["Admin-Up/Operation-Up Start"]="3"
        temp["Admin-Down/Operation-Down Start"]="0"
        temp["Admin-Up/Operation-Down Start"]="50"
        temp["Total Available"]="53"
        temp["Network View"]="discovery_view"
        temp["Admin-Down/Operation-Down Start"]="0" 
        cls.test1.append(temp)
        
        temp={}
        temp["Device Name"]="DELL-PC8024F"
        temp["Admin-Up/Operation-Up Start"]="2"
        temp["Admin-Down/Operation-Down Start"]="0"
        temp["Admin-Up/Operation-Down Start"]="22"
        temp["Total Available"]="24"
        temp["Network View"]="discovery_view"
        temp["Admin-Down/Operation-Down Start"]="0"
        cls.test1.append(temp)

        logger.info ("Input Json for validation for Port Capacity Delta by Device")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))

    def test_1_port_capacity_delta_by_device(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
        search_str=r"search source=ib:discovery:port_capacity index=ib_discovery                                       | stats avg(TOTAL_AVAIL_COUNT)  as AVG_TOTAL_AVAIL_COUNT avg(ADM_UP_OP_UP_COUNT) as AVG_ADM_UP_OP_UP_COUNT avg(ADM_UP_OP_DN_COUNT) as AVG_ADM_UP_OP_DN_COUNT by NETWORK_VIEW DEVICE_NAME             | eval DAILY_TOTAL_AVAIL_COUNT = round(AVG_TOTAL_AVAIL_COUNT)             | eval DAILY_ADM_UP_OP_UP_COUNT = round(AVG_ADM_UP_OP_UP_COUNT)             | eval DAILY_ADM_UP_OP_DN_COUNT = round(AVG_ADM_UP_OP_DN_COUNT)             | eval \"Admin-Down/Operation-Down Start\" = DAILY_TOTAL_AVAIL_COUNT - DAILY_ADM_UP_OP_UP_COUNT - DAILY_ADM_UP_OP_DN_COUNT             | rename DAILY_TOTAL_AVAIL_COUNT  as \"Total Available\" DAILY_ADM_UP_OP_UP_COUNT as \"Admin-Up/Operation-Up Start\" DAILY_ADM_UP_OP_DN_COUNT as \"Admin-Up/Operation-Down Start\"             | append [ search source=ib:discovery:port_capacity index=ib_discovery             -1d@d             -1d@d+1d                                                   | stats avg(TOTAL_AVAIL_COUNT)  as AVG_TOTAL_AVAIL_COUNT avg(ADM_UP_OP_UP_COUNT) as AVG_ADM_UP_OP_UP_COUNT avg(ADM_UP_OP_DN_COUNT) as AVG_ADM_UP_OP_DN_COUNT by NETWORK_VIEW DEVICE_NAME             | eval DAILY_TOTAL_AVAIL_COUNT = round(AVG_TOTAL_AVAIL_COUNT)             | eval DAILY_ADM_UP_OP_UP_COUNT = round(AVG_ADM_UP_OP_UP_COUNT)             | eval DAILY_ADM_UP_OP_DN_COUNT = round(AVG_ADM_UP_OP_DN_COUNT)             | eval \"Admin-Down/Operation-Down End\" = DAILY_TOTAL_AVAIL_COUNT - DAILY_ADM_UP_OP_UP_COUNT - DAILY_ADM_UP_OP_DN_COUNT             | rename DAILY_TOTAL_AVAIL_COUNT  as \"Total Available\" DAILY_ADM_UP_OP_UP_COUNT as \"Admin-Up/Operation-Up End\" DAILY_ADM_UP_OP_DN_COUNT as \"Admin-Up/Operation-Down End\" ]             | selfjoin keepsingle=true NETWORK_VIEW DEVICE_NAME             | rename DEVICE_NAME as \"Device Name\" NETWORK_VIEW as \"Network View\"              | table \"Device Name\" \"Admin-Up/Operation-Up Start\" \"Admin-Up/Operation-Up End\" \"Admin-Down/Operation-Down Start\" \"Admin-Down/Operation-Down End\" \"Admin-Up/Operation-Down Start\" \"Admin-Up/Operation-Down End\" \"Total Available\" \"Network View\"             | sort +str(\"Device Name\") +str(\"Network View\")"
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
        logger.info('-'*15+"END:Port Capacity Delta by Device"+'-'*15) 

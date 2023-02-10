"""
 Copyright (c) Infoblox Inc., 2016
 Report Name          : Top Devices Denied an IP Address
 Report Category      : DHCP Fingerprint.
 Number of Test cases : 1
 Execution time       : 302.61 seconds
 Execution Group      : Hour Group (HG)
 Description          : DHCP Fingerprint Requested Leases.

 Author   : Manimaran Avudayappan
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
      1.  Input/Preparation  : Preparation called by separate script as reports will be updated every one hour
                                     a. Create a custom network view network_view_dhcp,
                                        10.0.0.0/8
                                        51.0.0.0/24 with range 51.0.0.1 to 51.0.0.100.
                                        Add 1 fingerprint assigned with range with Deny Permission.
                                        Request 1 Leases for Alps Electric
      2.  Search     : Performing Search operation with default/custom filter
      3.  Validation : comparing Search results with Retrieved 'Top Devices Denied an IP Address' report without delta.
"""

class TopDeviceDeniedIPAddress(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        logger.info('-'*15+"START:Top Devices Denied an IP Address"+'-'*15)

        cls.test1=[]
        temp={}
        temp["Device Type"]="Alps Electric"
        temp["Device Class"]="Misc"
        temp["Network"]="51.0.0.0"
        temp["Attempts"]="1"
        cls.test1.append(temp)
        
        logger.info("Creating input in json format for Top Devices Denied an IP Address report validation ")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))

    def test_1_brg_top_device_denied_an_ip_address(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
        search_str=r"search index=ib_dhcp_summary report=si_devices_denied_an_ip_address             (orig_host=\"*\")             *             *             (CIDR>=1)             | eval FINGER_PRINT=if(isnull(OS_NUMBER) OR OS_NUMBER==0,FP,SFP)             | noop             | eval DEVICE_CLASS=if(isnull(DEVICE_CLASS), \"Modified or Deleted\", DEVICE_CLASS)             | noop             | stats count as COUNT, max(_time) as LAST_ATTEMPT by MAC_DUID, FINGER_PRINT, DEVICE_CLASS, NW             | sort -COUNT              | head 10              | eval last_attempt=strftime(LAST_ATTEMPT, \"%Y-%m-%d %H:%M:%S %Z\")             | rename MAC_DUID as \"MAC/DUID\", FINGER_PRINT as \"Device Type\", DEVICE_CLASS as \"Device Class\", NW as Network, COUNT as Attempts, last_attempt as \"Last Attempt\"             | table \"MAC/DUID\", \"Device Type\", \"Device Class\", Network, Attempts, \"Last Attempt\"" 
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
        logger.info('-'*15+"END:Top Devices Denied an IP Address report"+'-'*15)
 

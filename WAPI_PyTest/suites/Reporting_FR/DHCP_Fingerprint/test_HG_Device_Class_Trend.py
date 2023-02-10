"""
 Copyright (c) Infoblox Inc., 2016
 Report Name          : Device Class Trend
 Report Category      : DHCP Fingerprint.
 Number of Test cases : 1
 Execution time       : 302.61 seconds
 Execution Group      : Hour Group (HG)
 Description          : DHCP Fingerprint Requested Leases'.

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
      1.  Input/Preparation  : Preparation called by separate script as reports will be updated every one hour
                                    a. Create a custom network view network_view_dhcp, 
                                        10.0.0.0/8
                                        51.0.0.0/24 with range 51.0.0.1 to 51.0.0.100.
                                        Request 10 Leases for Voip Phones/Adapters, Switches and 1 lease for Apple Airport , AP Meraki and Alps Electric  
                                        sudo /import/tools/qa/tools/dras_opt55/dras -i "+config.grid_member1_vip+" -n 10 -w -D -O 55:0103060c0f2a424378

      2.  Search     : Performing Search operation with default/custom filter
      3.  Validation : comparing Search results with Retrieved 'Device Class Trend' report without delta.
"""

class DeviceClassTrend(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        logger.info('-'*15+"START:Device Class Trend report"+'-'*15)
        cls.test1=[]
        temp={}
        temp["Switches"]="10"
        temp["VoIP Phones/Adapters"]="10"
        cls.test1.append(temp)
        

        logger.info("Creating input in json format for Device Class Trend report validation ")   
	logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))

    def test_1_device_class_trend(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
        '''
	search_str=r"search index=ib_dhcp_summary report=si_dhcp_top_os_by_network | bucket span=4h _time | dedup _time MAC_DUID | lookup os_number_fingerprint_lookup OS_NUMBER output SFP | eval FINGER_PRINT=if(isnull(OS_NUMBER) OR OS_NUMBER==0,FP,SFP) | lookup fingerprint_device_class_lookup FINGER_PRINT output DEVICE_CLASS | eval DEVICE_CLASS=if(isnull(DEVICE_CLASS), \"Modified or Deleted\", DEVICE_CLASS) | timechart span=4h count as Count by DEVICE_CLASS where max in top5 useother=f"
        '''
        search_str=r"search index=ib_dhcp_summary report=si_dhcp_top_os_by_network  * (orig_host=\"*\")  (CIDR>=1) * * | bucket span=4h _time | rename _time as time_for_dedup | dedup time_for_dedup MAC_DUID  | eval _time=time_for_dedup  | lookup os_number_fingerprint_lookup OS_NUMBER output SFP | eval FINGER_PRINT=if(isnull(OS_NUMBER) OR OS_NUMBER==0,FP,SFP) | noop | lookup fingerprint_device_class_lookup FINGER_PRINT output DEVICE_CLASS | noop | eval DEVICE_CLASS=if(isnull(DEVICE_CLASS), \"Modified or Deleted\", DEVICE_CLASS) | timechart span=4h count as Count by DEVICE_CLASS where max in top5 useother=f | rename _time as Time | eval Time=strftime(Time, \"%Y-%m-%d %H:%M:%S %Z\")"
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
        logger.info("compare_resutls")
        result = compare_results(self.test1,results_list)
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg 

    @classmethod
    def teardown_class(cls):
        logger.info('-'*15+"END:Device Class Trend report"+'-'*15)


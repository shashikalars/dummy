"""
 Copyright (c) Infoblox Inc., 2016
 Report Name          : Device Fingerprint Change Detected
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
                                     Request 1 lease for Apple Airport , AP Meraki with same MAC Address
                                     sudo /import/tools/qa/tools/dras_opt55/dras -i "+config.grid_member1_vip+" -n 10 -w -D -O 55:0103060c0f2a424378
      2.  Search     : Performing Search operation with default/custom filter
      3.  Validation : comparing Search results with Retrieved 'Device Fingerprint Change Detected' report without delta.
"""

class DeviceFingerprintChangeDetected(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        logger.info('-'*15+"START:Device Fingerprint Change Detected report"+'-'*15)
        cls.test1=[]
        temp={}
        temp["MAC/DUID"]="aa:11:bb:22:cc:33"
        temp["Current Device Type"]="BeOS"
        temp["Current Device Class"]="Dead OSes"
        temp["Previous Device Type"]="Apple Airport"
        temp["Previous Device Class"]="Routers and APs"
        temp["Lease IP"]="51.0.0.80"
        temp["Action"]="Renewed" 
        cls.test1.append(temp)
        logger.info("Creating input in json format for Device Fingerprint Change Detected report validation")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))

    def test_1_device_fingerprint_change_detected(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
	search_str=r"search sourcetype=ib:dhcp:lease_history index=ib_dhcp_lease_history dhcpd OR dhcpdv6 r-l-e ACTION = \"Issued\" OR ACTION = \"Renewed\"  | where isnotnull(FP_VIEW) and isnotnull(FP_NW) and isnotnull(FP_CIDR) and isnotnull(FP_RANGE) | lookup os_number_fingerprint_lookup OS_NUMBER output SFP | eval FINGER_PRINT=if(isnull(OS_NUMBER) OR OS_NUMBER==0,FP,SFP) | lookup fingerprint_device_class_lookup FINGER_PRINT output DEVICE_CLASS | eval DEVICE_CLASS=if(isnull(DEVICE_CLASS), \"Modified or Deleted\", DEVICE_CLASS) | streamstats current=false last(FINGER_PRINT) as LAST_FINGER_PRINT last(LEASE_IP) as LAST_LEASE_IP last(ACTION) as LAST_ACTION last(_time) as LAST_TIME last(DEVICE_CLASS) as LAST_DEVICE_CLASS last(FP_NW) as LAST_NW by MAC_DUID  | where  LAST_DEVICE_CLASS != DEVICE_CLASS  | rename LAST_FINGER_PRINT as \"Current Device Type\" FINGER_PRINT as \"Previous Device Type\" MAC_DUID as \"MAC/DUID\" LAST_LEASE_IP as \"Lease IP\" LAST_ACTION as \"Action\" LAST_DEVICE_CLASS as \"Current Device Class\" DEVICE_CLASS as \"Previous Device Class\"  | convert ctime(LAST_TIME) as Time | sort -Time | table Time, \"MAC/DUID\",  \"Current Device Type\" \"Current Device Class\" \"Previous Device Type\" \"Previous Device Class\" \"Lease IP\" \"Action\""
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
        logger.info('-'*15+"END:Device Fingerprint Change Detected report"+'-'*15)
 

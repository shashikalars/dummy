"""
 Copyright (c) Infoblox Inc., 2016
 ReportName          : DHCP Top Lease Clients
 ReportCategory      : DHCP Lease History.
 Number of Test cases: 1
 Execution time      : 302.61 seconds
 Execution Group     : Hour Group (HG)
 Description         : DHCP Lease'.

 Author   : Manimaran
 History  : 05/31/2016 (Created)
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
                               a. Requested 1 lease with same MAC Address for 2 times 
                                   ./dras -i 10.35.111.6 -n 1 -a 77:22:33:44:55:99
      2.  Search     : Performing Search operaion with default/custom filter
      3.  Validation : comparing Search results with Reterived  'DHCP Top Lease Clients' report without delta.
"""

class DHCPTopClients(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        logger.info('-'*15+"START:DHCP Top Lease Clients"+'-'*15)
        logger.info ("Preparation has executed 1 hour before as this report will take 1 hour to update")

        '''
        cls.test1=[]
        temp={}
        temp["MAC/DUID"]="77:22:33:44:55:99"
        temp["Issued"]="1"
        temp["Renewed"]="1"
        temp["Freed"]="0"
        temp["MAC/DUID Total"]="2"  
        cls.test1.append(temp)
        '''
        cls.test1=[]
        temp={}
        temp["MAC/DUID"]="aa:11:bb:22:cc:33"
        temp["Issued"]="1"
        temp["Renewed"]="1"
        temp["Freed"]="1"
        temp["MAC/DUID Total"]="3"
        cls.test1.append(temp)
  

        logger.info ("Input Json for validation")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))

    def test_1_dhcp_top_clients(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
        search_str=r"search index=ib_dhcp_summary report=si_dhcp_top_lease_client (orig_host=\"*\") * * | eval FINGER_PRINT=if(isnull(OS_NUMBER) OR OS_NUMBER==0,FP,SFP) | noop | stats count as COUNT by orig_host Protocol MAC_DUID ACTION, FINGER_PRINT | where (ACTION=\"Issued\" or ACTION=\"Renewed\" or ACTION=\"Freed\") | eval DEVICE_CLASS=if(isnull(DEVICE_CLASS), \"Modified or Deleted\", DEVICE_CLASS) | stats sum(eval(if(ACTION=\"Issued\",COUNT,0))) as Issued ,                  sum(eval(if(ACTION=\"Renewed\",COUNT,0))) as Renewed, sum(eval(if(ACTION=\"Freed\",COUNT,0))) as Freed, sum(COUNT) as MacDuidTotal by MAC_DUID | sort 0 -num(MacDuidTotal) | head 50 | rename MAC_DUID as \"MAC/DUID\", MacDuidTotal as \"MAC/DUID Total\""
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
        logger.info('-'*15+"END:DHCP Top Lease Clients"+'-'*15) 

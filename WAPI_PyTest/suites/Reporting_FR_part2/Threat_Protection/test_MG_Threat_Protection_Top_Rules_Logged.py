"""
 Copyright (c) Infoblox Inc., 2016
 ReportName          : Threat Protection Top Rules Logged
 ReportCategory      : Threat Protection.
 Number of Test cases: 1
 Execution time      : 
 Execution Group     : Minute Group (HG)
 Description         : Top Rules Logged.

 Author   : shashikala R S
 History  : 02/26/2021 (Created)
 Reviewer : 
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
      1.  Input/Preparation  : Prparation will be called by separte script as reports will be updated every minute
                               
      2.  Search     : Performing Search operaion with default/custom filter
      3.  Validation : comparing Search results with Reterived  'Threat Protection Top Rules Logged' report without delta.
"""

class Threat_Protection_Top_Rules_Logged(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        logger.info('-'*15+"START:Threat Protection Top Rules Logged"+'-'*15)
        #logger.info ("Preparation has executed 1 hour before as this report will take 1 hour to update")


        cls.test1=[]
        temp={}
        temp["RULE"]="OzymanDNS/SplitBrain Base32 SSH-2.0 payload over UDP (anti tunneling)"
	#temp["RULE"]="Rate limited:rudp.com"
        temp["Logged Event Count"]="1"
       
        cls.test1.append(temp)
  

        logger.info ("Input Json for validation")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))

    def test_1_TP_Top_Rules_Logged(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
        search_str="search source=ib:ddos:ip_rule_stats index=ib_security (host=\"*\") * * (SOURCE_PORT>=0) * | lookup atp_rule_sid_lookup RULE_SID output RULE_NAME,RULE_DESCRIPTION | eval SOURCE_IP = if (NAT_STATUS==\"Yes\",SOURCE_IP+\":[\"+BLOCK_START+\"-\"+BLOCK_END+\"]\", SOURCE_IP) | stats sum(ACTIVE_COUNT) as SID_COUNT_BY_SOURCE latest(_time) as LATEST_TIME by RULE_SID RULE_NAME SOURCE_IP RULE_DESCRIPTION | eventstats sum(SID_COUNT_BY_SOURCE) as SUM_SID_COUNT max(LATEST_TIME) as MAX_LATEST_TIME by RULE_SID | where (SUM_SID_COUNT >=0) | sort -SID_COUNT_BY_SOURCE | dedup 3 RULE_SID | eventstats values(SOURCE_IP) as \"Top Sources\" by RULE_SID | dedup RULE_SID | sort -SUM_SID_COUNT | convert ctime(MAX_LATEST_TIME) as \"Last Active\" | head 10  | eval RULE = RULE_NAME | makemv delim=\"#\" \"Rule\" | rename SUM_SID_COUNT as \"Logged Event Count\" | table \"Rule\" \"Logged Event Count\" \"Top Sources\" \"Last Active\" \"RULE\" | fields \"RULE\" \"Logged Event Count\""
        
        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
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
        print('-----------------------------------------------')
        print(self.test1)
        print(len(self.test1))
        print('---------------Adding Debugging line--------------------------------')
        print(results_list)
        print(len(results_list))
        print('-----------------------------------------------')
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg



    @classmethod
    def teardown_class(cls):
        logger.info('-'*15+"END:Threat Protection Top Rules Logged"+'-'*15) 


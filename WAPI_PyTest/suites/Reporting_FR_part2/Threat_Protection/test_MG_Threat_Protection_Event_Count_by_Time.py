"""
 Copyright (c) Infoblox Inc., 2016
 ReportName          : Threat Protection Event Count By Time
 ReportCategory      : Threat Protection.
 Number of Test cases: 1
 Execution time      : 
 Execution Group     : Minute Group (HG)
 Description         : Event Count Dashboard.

 Author   : shashikala R S
 History  : 03/02/2021 (Created)
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
      3.  Validation : comparing Search results with Reterived  'Threat Protection Event Count by Time' report without delta.
"""

class Threat_Protection_Event_Count_by_Time(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        logger.info('-'*15+"START:Threat Protection Event Count by Time"+'-'*15)
       
        cls.test1=[]
        temp={}
        temp["Member"]=config.grid_member1_fqdn
        #temp["Category"]="DNS Tunneling"
	#temp["Category"]="DHCP"
        #temp["Log Severity"]="MAJOR"
	#temp["Log Severity"]="INFORMATIONAL"
        #temp["Event Name"]="OzymanDNS/SplitBrain Base32 SSH-2.0 payload over UDP (anti tunneling)"
        #temp["Alert Count"]="0"
        #temp["Drop Count"]="1"
        #temp["Total Event Count"]="1"
        cls.test1.append(temp)
  

        logger.info ("Input Json for validation")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))

    def test_1_TP_Event_Count_by_Time(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
        search_str="search source=ib:ddos:events index=ib_security (host=\"*\") * * * | bucket span=5m _time | stats sum(ACOUNT) as SUM_ACOUNT, sum(DCOUNT) as SUM_DCOUNT by _time, host, SID, CATEGORY, SEVERITY, MESSAGE | eval SUM_TOTAL=SUM_ACOUNT+SUM_DCOUNT | sort -_time | head 5 | convert ctime(_time) as Time | rename host as \"Member\", CATEGORY as \"Category\", SEVERITY as \"Log Severity\", MESSAGE as \"Event Name\", SUM_ACOUNT as \"Alert Count\", SUM_DCOUNT as \"Drop Count\", SUM_TOTAL as \"Total Event Count\" | lookup atp_rule_sid_lookup RULE_SID AS SID OUTPUT RULE_DESCRIPTION | makemv delim=\"#\" \"Event Name\"  | table \"Time\", \"SID\", \"Member\", \"Category\", \"Log Severity\", \"Event Name\", \"Alert Count\", \"Drop Count\", \"Total Event Count\""
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
        logger.info('-'*15+"END:Threat Protection Event Count by Time"+'-'*15) 


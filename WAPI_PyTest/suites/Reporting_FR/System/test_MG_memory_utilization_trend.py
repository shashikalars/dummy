"""
 Copyright (c) Infoblox Inc., 2016                                   

 ReportName          : Memory Utilization (Detailed)    
 ReportCategory      : System
 Number of Test cases: 1
 Execution time      : 302.61 seconds
 Execution Group     : Minute Group (MG)
 Description         : Memory utilization (Detailed) report will be udpated every 1 min  

 Author   : Raghavendra MN
 History  : 05/23/2016 (Created)                                                                   
 Reviewer : Raghavendra MN
"""
import config
import json
import os
import pytest
import pexpect
import re
import sys
import subprocess
import unittest
from time import sleep

import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from logger import logger
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results

""" 
TEST Steps:
      1.  Input/Preparation      : Retriving Member Memory usage using WAPI
      2.  Search    		 : Performing Search operaion with default/custom filter 
      3.  Validation		 : comparing Search results with Reterived Memory utilization (with delta 10). 
"""


class SystemMemory(unittest.TestCase):
    #Preparation
    @classmethod
    def setup_class(cls):
        cls.test1=[] #Variable which is used for comparision.
        logger.info('-'*15+"START:Memory Utilization"+'-'*15)
        logger.info('SystemMemory:setup_class')
        logger.info ("Preparation for Memory Utilization")
        logger.info ("Retriving Member Memory Usage from WAPI call")
        members_memory={}
        #Retriving Memory usage using WAPI Call
    	response = ib_NIOS.wapi_request("GET", object_type="member?_return_fields%2b=node_info,vip_setting")
  	val = json.loads(response)
	for i in val:
    	    member_ip = i["vip_setting"]["address"]
    	    for j in i["node_info"]:
                for x in j["service_status"]:
                    if x["service"] == "MEMORY" and x["status"] == "WORKING" :
                        memory_utilization = re.findall('\d+',x["description"])[0]
                        members_memory[i["host_name"]] = memory_utilization
        members_memory["_time"] = ib_get.indexer_date(config.indexer_ip) 
        
        cls.test1.append(members_memory)
        logger.info ("Input Json for validation")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))
        logger.info ("Waiting for 7 min., for updating reports")
        sleep(420) #wait for report update some times reports will not update properly. 

    #Test case Execution
    def test_1_Memory_Utilization_default_filter(self):
        logger.info ("TestCase:"+sys._getframe().f_code.co_name)
        search_str=r"search sourcetype=ib:system index=ib_system 2 | bucket span=1m _time | timechart bins=1000 avg(MEMORY_PERCENT) by host where max in top10 useother=f"
        cmd = config.search_py + " \"" + search_str + "\" --output_mode=json"
        logger.info (cmd)
        os.system(cmd)
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        results_dist= results_list[-240::1]
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test1,results_dist)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 10")
        result = compare_results(self.test1,results_list,10)
        if result == 0: 
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg

    #Clean up
    @classmethod
    def teardown_class(cls):
        logger.info('-'*15+"END:Memory Utilization"+'-'*15)

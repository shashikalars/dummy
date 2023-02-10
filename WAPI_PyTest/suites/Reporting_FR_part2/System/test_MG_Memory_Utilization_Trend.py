"""
 Copyright (c) Infoblox Inc., 2016                                   

 ReportName          : Memory Utilization (Detailed)    
 ReportCategory      : System
 Number of Test cases: 1
 Execution time      :  seconds
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
from time import sleep
import unittest
import time
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from logger import logger
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results

""" 
TEST Steps:
      1.  Input/Preparaiton      : Retriving Member Memory usage using WAPI
      2.  Search                 : Performing Search operaion with default/custom filter 
      3.  Validation             : comparing Search results with Reterived Memory utilization (with delta 10). 
"""


class SystemMemory(unittest.TestCase):
    #Preparation
    @classmethod
    def setup_class(cls):
        cls.test1=[] #Variable which is used for comparision.
        logger.info('-'*15+"START:Memory Utilization"+'-'*15)
        logger.info ("Preparation for Memory Utilization")
        logger.info ("Retriving Member Memory Usage from WAPI call")
        members_cpu={}
        #Retriving Memory usage using WAPI Call
    	response = ib_NIOS.wapi_request("GET", object_type="member?_return_fields%2b=node_info,vip_setting")
        val = json.loads(response)
        for i in val:
    	    member_ip = i["vip_setting"]["address"]
    	    for j in i["node_info"]:
                for x in j["service_status"]:
                    print(x)
                    if x["service"] == "MEMORY" and x["status"] == "WORKING" :
                        memory_tilization = re.findall('\d+',x["description"])[0]
                        print(re.findall('\d+',x["description"]))
                        members_cpu[i["host_name"]] = memory_tilization
        #members_cpu["_time"] = ib_get.indexer_date(config.indexer_ip) 
        
        cls.test1.append(members_cpu)
        logger.info ("Input Json for validation")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))
        logger.info ("Waiting for 7 min., for updating reports")
        #sleep(420) #wait for report update some times reports will not update properly. 
        sleep(60)
    #Test case Execution
    def test_1_Memory_utilization_default_filter(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
        search_str="search sourcetype=ib:system index=ib_system 2 earliest=-60m | bucket span=1m _time | timechart bins=1000 avg(MEMORY_PERCENT) by host where max in top10 useother=f"
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
        logger.info("-----------------------------------------------------")
        logger.info(self.test1)
        logger.info(len(self.test1))
        logger.info("--------------Adding Debugging line ------------------")
        logger.info(results_list)
        logger.info(len(results_list))
        logger.info("-----------------------------------------------------")
	#Adding New validation code
        """
        flag=0
        leng=0
        for k in self.test1:
            leng=len(k.values())
            for i in k.values():
                if i>1:
                    flag=flag+1
                    #assert True
                    #print("************************************************")
        print(flag,leng)
        if flag==leng:
            print("Passed")
        """

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

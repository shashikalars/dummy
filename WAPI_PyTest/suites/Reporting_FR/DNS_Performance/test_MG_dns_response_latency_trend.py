"""
 Copyright (c) Infoblox Inc., 2016
 ReportName          : DNS Response Latency Trend
 ReportCategory      : DNS Performance
 Number of Test cases: 1
 Execution time      : 603.24 seconds
 Execution Group     : Minute Group (MG)
 Description         : DNS Response Latency Trend report will be updated every 1 min. 

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
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from logger import logger
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results

"""
TEST Steps:
      1.  Input/Preparaiton      : Retriving Member information from WAPI
      2.  Search                 : Performing Search operaion with default/custom filter
      3.  Validation             : comparing Search results with input data (with delta 10).
"""

class DNSPerformance(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        logger.info('-'*15+"START:DNS Response Latency Trend"+'-'*15)
        cls.test1=[]
        logger.info("Preparation, fetching member informaion")
        response = ib_NIOS.wapi_request("GET", object_type="member?_return_fields%2b=vip_setting,service_status")
        val = json.loads(response)
        members_dns_info={}
        for i in val:
            for x in i["service_status"]:
                if x["service"] == "DNS" and x["status"] == "WORKING" :
                   member_ip = i["vip_setting"]["address"]
                   members_dns_info[i["host_name"]] = '10'
            members_dns_info["_time"] = ib_get.indexer_date(config.indexer_ip) 
        cls.test1.append(members_dns_info)
        logger.info ("Input Json for validation")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))
        logger.info ("Waiting for 10 min., for updating reports")
        sleep(600) 

    def test_1_dns_response_latency_trend_default_filter(self):
        logger.info("TestCase:",sys._getframe().f_code.co_name)
        search_str=r"search sourcetype=ib:dns:perf index=ib_dns | bucket span=1m _time | timechart bins=1000 avg(LATENCY) by host where max in top10 useother=f" 
        cmd = config.search_py + " \"" + search_str + "\" --output_mode=json"
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

    @classmethod
    def teardown_class(cls):
        logger.info('-'*15+"END:DNS Response Latency Trend"+'-'*15)

"""
 Copyright (c) Infoblox Inc., 2016

 ReportName          : DNS Daily Peak Hour Query Rate by Member
 ReportCategory      : DNS 
 Number of Test cases: 1
 Execution time      : 3.50 seconds
 Execution Group     : Daily Group (DG)
 Description         : DNS Daily Peak Hour Query Rate by Member report will be updated once a day

 Author : Raghavendra MN
 History: 06/06/2016 (Created)
"""
import config
import json
import os
import pytest
import pexpect
import re
import sys
import subprocess
import time
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
      3.  Validation             : Comparing Search results with input data (with delta 10).
"""

class DNSQuery(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        logger.info('-'*15+"START:DNS Daily Peak Hour Query Rate by Member "+'-'*15)
        cls.test1=[]
        logger.info("Preparation, fetching member informaion")
        response = ib_NIOS.wapi_request("GET", object_type="member?_return_fields%2b=vip_setting,service_status")
        val = json.loads(response)
        members_dns_info={}
        epoc=ib_get.indexer_epoch_time(config.indexer_ip)
        ts = time.strftime('%Y-%m-%d', time.gmtime(int(epoc)))
        ts1 = ts+"T00:00:00.000+00:00"
        for i in val:
            for x in i["service_status"]:
                if x["service"] == "DNS" and x["status"] == "WORKING" :
                   member_ip = i["vip_setting"]["address"]
                   members_dns_info[i["host_name"]] = '10'
            members_dns_info["_time"] = ts1
        cls.test1.append(members_dns_info)
        logger.info ("Input Json for validation")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))

    def test_1_dns_daily_peak_hour_query_rate_by_member(self):
        logger.info("Test Case:",sys._getframe().f_code.co_name)
        search_str=r"search index=ib_dns_summary report=si_dns_member_qps_trend_per_hour | lookup dns_viewkey_displayname_lookup VIEW output display_name | rename orig_host as host | stats avg(QCOUNT) as avg_COUNT, max(QCOUNT) as max_COUNT by _time host VIEW | bucket span=1d _time | streamstats max(avg_COUNT) as MAX_AVG_COUNT by _time, host, VIEW | eval avg_COUNT = if (avg_COUNT == MAX_AVG_COUNT, avg_COUNT, 0) | eval max_COUNT = if (avg_COUNT == MAX_AVG_COUNT, max_COUNT, 0) | stats max(avg_COUNT) as avg_COUNT, max(max_COUNT) as max_COUNT by _time, host, VIEW | timechart span=1d eval(max(max_COUNT)/600) by host where max in top5 useother=f"
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
        logger.info('-'*15+"END:DNS Daily Peak Hour Query Rate by Member "+'-'*15)

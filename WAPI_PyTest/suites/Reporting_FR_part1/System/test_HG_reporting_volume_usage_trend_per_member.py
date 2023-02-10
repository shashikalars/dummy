"""
 Copyright (c) Infoblox Inc., 2016                                   

 ReportName          : Reporting Volume Usage Trend per Member (Detailed)    
 ReportCategory      : System
 Number of Test cases: 1
 Execution time      : 4.52 sec.,
 Execution Group     : Hourly Group(HG)
 Description         : Reporting Volume Usage Tredn per Member reports will be updated every 30 min. 

 Author   : Raghavendra MN
 History  : 06/03/2016 (Created)                                                                   
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
import time
import unittest
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from logger import logger
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results

""" 
TEST Steps:
      1.  Input/Preparaiton      : Retriving Member informion from WAPI Call, with approximate 'Volume' usage say 75
      2.  Search                 : Performing Search operaion with default/custom filter 
      3.  Validation             : Comparing Search results with inputdata (with delta 70). 
				   This test will validate reports are updated or not (report will be considered as PASS if volume value inbetween 5 to 145)
"""


class SystemReportVolumeUsageTrendPerMember(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        cls.test1=[]
        logger.info('-'*15+"START:Reporting Volume Usage Trend per Member"+'-'*15)
        logger.info ("Preparation for Reporting Volume Usage Trend per Member")
        logger.info ("Retriving Member information from WAPI Call")
        member_volume={}
        
        epoc=ib_get.indexer_epoch_time(config.grid_vip)
        minute=time.strftime('%M',time.gmtime(int(epoc)))
        sm = '30' if int(minute) >= 45 else '00'
        tm = time.strftime('%Y-%m-%dT%H', time.gmtime(int(epoc)))

    	response = ib_NIOS.wapi_request("GET", object_type="member?_return_fields%2b=node_info,vip_setting")
  	val = json.loads(response)
	for i in val:
            member_volume[i["host_name"]] = '75'
        #member_volume["_time"] = tm+":"+sm+":00.000+00:00"
        
        cls.test1.append(member_volume)
        logger.info ("Input Json for validation")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))

    def test_1_reporting_volume_usage_trend_per_member(self):
        logger.info ("TestCase:"+sys._getframe().f_code.co_name)
        search_str="search source=* index=_internal group=per_host_thruput | bucket span=1m _time | stats sum(kb) as kb by _time, series | timechart avg(kb) by series where max in top10 useother=f"
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

        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        print(results_dist)
        first=results_dist[0]
        print(first)
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

        if first[config.grid_member_fqdn] > 20 or first[config.grid_member1_fqdn] > 20 or first[config.grid_member2_fqdn] > 20:
            print("-----------------------------------------")
            print("--------------***********----------------")
            print("PASSED")
            logger.info("Search validation result: %s(PASS)",first)
            assert True

        else:
            logger.error("Search validation result: %s(FAIL)",first)

            msg = 'Count does not match - %s', first
            assert False



        '''
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test1,results_dist)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 70")
        result = compare_results(self.test1,results_list,70)
        if result == 0: 
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg
        '''

    @classmethod
    def teardown_class(cls):
        logger.info('-'*15+"END:Reporting Volume Usage Trend per Member"+'-'*15)

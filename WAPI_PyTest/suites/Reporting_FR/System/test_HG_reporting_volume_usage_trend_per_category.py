"""
 Copyright (c) Infoblox Inc., 2016                                   

 ReportName          : Reporting Volume Usage Trend per Category (Detailed)    
 ReportCategory      : System
 Number of Test cases: 1
 Execution time      : 4.52 sec.,
 Execution Group     : Hourly Group(HG)
 Description         : Reporting Volume Usage Tredn per Category reports will be updated every 30 min. 

 Author : Raghavendra MN
 History: 06/03/2016 (Created)                                                                   
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
      1.  Input/Preparaiton      : Currently creating preparation for 'DHCP Performance', 'DNS Performance' , 'DNS Query' & 'System Utilization'
      2.  Search                 : Performing Search operaion with default/custom filter 
      3.  Validation             : Comparing Search results with inputdata (with delta 3.9). 
				   This test will validate reports are updated or not (report will be considered as PASS if volume value inbetween 0.1 to 7.9)
"""
class ReportingVolumeUsageTrendPerCategory(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        cls.test1=[]
        logger.info('-'*15+"START:Reporting Volume Usage Trend per Category"+'-'*15)
        logger.info ("Preparation for Reporting Volume Usage Trend per Category")
        logger.info ("Retriving Member information from WAPI Call")
        member_volume={}
        
        epoc=ib_get.indexer_epoch_time(config.grid_vip)
        minute=time.strftime('%M',time.gmtime(int(epoc)))
        sm = '30' if int(minute) >= 45 else '00'
        tm = time.strftime('%Y-%m-%dT%H', time.gmtime(int(epoc)))

        member_volume["DHCP Performance"] = '4'
        member_volume["DNS Performance"] = '4'
        member_volume["DNS Query"] = '4'
        member_volume["System Utilization"] = '4'
        member_volume["_time"] = tm+":"+sm+":00.000+00:00"
        cls.test1.append(member_volume)
        logger.info ("Input Json for validation")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))

    def test_1_reporting_volume_usage_trend_per_category(self):
        logger.info ("TestCase:"+sys._getframe().f_code.co_name)
        search_str=r"search source=* index=_internal (group=per_source_thruput OR group=per_sourcetype_thruput) series=ib:* series!=\"ib:dns:reserved\" series!=\"ib:reserved1\" | bucket span=1m _time |  eval CATEGORY=case(((series=\"ib:dns:query:top_requested_domain_names\" OR series=\"ib:dns:query:cache_hit_rate\" OR series=\"ib:dns:query:by_member\" OR series=\"ib:dns:query:qps\" OR series=\"ib:dns:query:top_clients\" OR series=\"ib:dns:stats\") AND group=\"per_sourcetype_thruput\") OR ((series=\"ib:dns:query:top_clients_per_zone\" OR series=\"ib:dns:query:top_clients_per_domain\" OR series=\"ib:dns:query:top_nxdomain_query\" OR series=\"ib:dns:query:top_failed\" OR series=\"ib:dns:query:top_received\" OR series=\"ib:dns:query:top_timeout\" OR series=\"ib:dns:query:ip_block_group\") AND group=\"per_source_thruput\"), \"DNS Query\", series=\"ib:dns:perf\" AND group=\"per_sourcetype_thruput\", \"DNS Performance\", series=\"ib:ddns\" AND group=\"per_sourcetype_thruput\", \"DDNS\", series=\"ib:dhcp:lease_history\" AND group=\"per_sourcetype_thruput\", \"DHCP Lease History/Fingerprint\", (series=\"ib:dhcp:message\" OR series=\"ib:dhcp:network\" OR series=\"ib:dhcp:range\") AND group=\"per_sourcetype_thruput\", \"DHCP Performance\", series=\"ib:system\" AND group=\"per_sourcetype_thruput\", \"System Utilization\", (series=\"ib:ipam:network\" OR series=\"ib:dns:view\" OR series=\"ib:dns:zone\") AND group=\"per_sourcetype_thruput\", \"DDI Utilization\", (series=\"ib:dns:query:top_rpz_hit\" OR series=\"ib:dns:fireeye\" OR series=\"ib:ddos:events\") AND group=\"per_source_thruput\", \"Security\") | where isnotnull(CATEGORY) | stats sum(kb) as kb by _time, CATEGORY | timechart avg(kb) by CATEGORY"
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
        logger.info("compare_resutls with 'delta' value as 3.9")
        result = compare_results(self.test1,results_list,3.95)
        if result == 0: 
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg

    @classmethod
    def teardown_class(cls):
        logger.info('-'*15+"END:Reporting Volume Usage Trend per Category"+'-'*15)

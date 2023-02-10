import config
import json
import os
import pytest
import pexpect
import re
import sys
import subprocess
import unittest
import time
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from logger import logger
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results

class MSPreports(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        logger.info('-'*15+"Managed_DDI_Usage_Trend"+'-'*15)
	cls.ddi_address_usage = [{"IPv4 Count":"1000","IPv6 Count":"1000","Total Count":"2000","5-Day Avg IPv4 Count":"1000","5-Day Avg IPv6 Count":"1000","5-Day Avg Total Count":"2000"}]
	cls.dns_usage_trend = [{"Peak_QPM":"1.4144444444444446","5-Day Average Peak QPS":"0.024"}]

    def test_001_managed_ddi_peak_ip_usage_trend(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
        logger.info("Managed DDI Peak IP Usage Trend")

	search_str="search index=ib_ipam_summary report=si_ipam_address_usage_trend_per_5days | eval Peak_IPV4=IPV4_COUNT, Peak_IPV6=IPV6_COUNT, Peak_Total=TOTAL_COUNT | sort _time | streamstats window=5 avg(Peak_IPV4) as Avg_IPv4_Count, avg(Peak_IPV6) as Avg_IPv6_Count, avg(Peak_Total) as Avg_Total_Count | eval \"Time\"=strftime(_time, \"%m/%d/%Y:%H:%M:%S\"), \"5-Day Avg IPv4 Count\"=round(Avg_IPv4_Count,0), \"5-Day Avg IPv6 Count\"=round(Avg_IPv6_Count,0), \"5-Day Avg Total Count\"=round(Avg_Total_Count,0) | rename IPV4_COUNT as \"IPv4 Count\", IPV6_COUNT as \"IPv6 Count\", TOTAL_COUNT as \"Total Count\" | table \"Time\", \"IPv4 Count\", \"IPv6 Count\", \"Total Count\", \"5-Day Avg IPv4 Count\", \"5-Day Avg IPv6 Count\", \"5-Day Avg Total Count\""

        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        print("##########################",cmd)
        print(os.system(cmd))
        print("*****************%%%%%*********************")

        try:
            retrived_data=open(config.json_file).read()
            print(retrived_data)

        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.ddi_address_usage,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        result = compare_results(self.ddi_address_usage,results_list)
        logger.info("-----------------------------------------------------")
        logger.info(self.ddi_address_usage)
        logger.info(len(self.ddi_address_usage))
        logger.info("--------------------shashhhhhhhh-------------------")
        logger.info(results_list)
        logger.info(len(results_list))
        logger.info("-----------------------------------------------------")
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg

    def test_002_managed_dns_peak_usage_trend(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
        logger.info("Managed DNS Peak Usage Trend")

	search_str="search index=ib_dns_summary report=si_dns_member_qps_trend_per_5days | stats max(QCOUNT) as stats_COUNT by _time | sort _time | streamstats window=5 avg(stats_COUNT) as Peak_QPM | eval Date=strftime(_time, \"%a %b %e\"),\"5-Day Average Peak QPS\"=round((Peak_QPM/60),3) | table Date, \"Peak_QPM\" \"5-Day Average Peak QPS\""
	
        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        print("##########################",cmd)
        print(os.system(cmd))
        print("*****************%%%%%*********************")

        try:
            retrived_data=open(config.json_file).read()
            print(retrived_data)

        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.dns_usage_trend,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        result = compare_results(self.dns_usage_tren,results_list)
        logger.info("-----------------------------------------------------")
        logger.info(self.dns_usage_trend)
        logger.info(len(self.dns_usage_trend))
        logger.info("--------------------shashhhhhhhh-------------------")
        logger.info(results_list)
        logger.info(len(results_list))
        logger.info("-----------------------------------------------------")
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg


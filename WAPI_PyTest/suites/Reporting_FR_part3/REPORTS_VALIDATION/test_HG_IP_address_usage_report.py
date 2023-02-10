import config
import json
import os
import pytest
import pexpect
import re
import sys
import subprocess
from time import sleep
import time
import unittest
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from logger import logger
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results


class  IP_address_usage_report(unittest.TestCase):

# IP Address Usage Report

    @pytest.mark.run(order=1)
    def test_1_IP_address_usage(self):
        
        logger.info ("Input Json Data for IP Address Usage Report validation")

        
        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search index=ib_usage_count report=si_ipam_usage_count_address_usage_trend_per_5days| eval Peak_IPV4=IPV4_COUNT, Peak_IPV6=IPV6_COUNT, Peak_Total=TOTAL_COUNT| sort _time   | streamstats window=5 avg(Peak_IPV4) as Avg_IPv4_Count, avg(Peak_IPV6) as Avg_IPv6_Count, avg(Peak_Total) as Avg_Total_Count| eval \"Time\"=strftime(_time, \"%m/%d/%Y\"), \"5-Day Avg IPv4 Count\"=round(Avg_IPv4_Count,0), \"5-Day Avg IPv6 Count\"=round(Avg_IPv6_Count,0), \"5-Day Avg Total Count\"=round(Avg_Total_Count,0)| dedup the_date| rename IPV4_COUNT as \"IPv4 Count\", IPV6_COUNT as \"IPv6 Count\", TOTAL_COUNT as \"Total Count\"| table \"Time\", \"IPv4 Count\", \"IPv6 Count\", \"Total Count\", \"5-Day Avg IPv4 Count\", \"5-Day Avg IPv6 Count\", \"5-Day Avg Total Count\""

        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        logger.info (cmd)

        print(os.system(cmd))
        print("-------------%%%----------")
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operation failed, Please check Grid Configuration")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        results_dist= results_list[-240::1]
        
        print(results_dist)
        first=results_dist[0]
        print(first)


        if first['IPv4 Count'] >= 1000 and first['IPv6 Count'] >= 1 and first['Total Count'] >= 1000:
            print("-----------------------------------------")
            print("IPv4 Count=",first['IPv4 Count'])
            print("IPv6 Count=",first['IPv6 Count'])
            print("Total Count=",first['Total Count'])
            print("5-Day Avg IPv4 Count=",first['5-Day Avg IPv4 Count'])
            print("5-Day Avg IPv6 Count=",first['5-Day Avg IPv6 Count'])
            print("5-Day Avg Total Count=",first['5-Day Avg Total Count'])
            print("--------------***********----------------")
            print("PASSED")
            logger.info("Search validation result: %s (PASS)",first)

            
        else:
            logger.error("Search validation result: %s (FAIL)",first)

            msg = 'Count does not match - %s', first
            assert first == 0, first
        

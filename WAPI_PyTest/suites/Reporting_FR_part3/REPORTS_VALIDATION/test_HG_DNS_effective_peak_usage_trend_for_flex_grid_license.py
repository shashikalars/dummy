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


class DNS_effective_peak_usage_trend_Flex_member(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_1_DNS_effective_peak_usage_trend_flex_member(self):
    
    
        ## DNS Effective Peak Usage Trend for Flex Grid License

        logger.info ("Input Json Data for DNS Effective Peak Usage Trend for Flex Grid License report validation")

        
        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search index=ib_dns_summary report=si_dns_member_qps_trend_per_5days | stats max(QCOUNT) as stats_COUNT by _time | streamstats window=5 avg(stats_COUNT) as Peak_QPM | eval \"5-Day Average Peak QPS\"=round((Peak_QPM/60),3) |  sort -_time | rename _time as Time | eval Time=strftime(Time, \"%Y-%m-%d %H:%M:%S %Z\") | table Time,\"5-Day Average Peak QPS\""
        print(search_str)
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
        print("-----------------------------------------")
        count=first['5-Day Average Peak QPS']
        print(count)
        print("--------------***********----------------")

        if count >= 0.018:
            print("PASSED")
            logger.info("Search validation result: %s (PASS)",count)
        else:
            logger.error("Search validation result: %s (FAIL)",count)

            msg = '5-day average is less than 0.018 - %s', count
            assert count == 0, msg
        


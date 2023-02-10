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


class  Managed_DDI_peak_usage_trend(unittest.TestCase):

# IP Address Usage Report

    @pytest.mark.run(order=1)
    def test_1_Managed_DNS_peak_usage_trend(self):
        
        logger.info ("Input Json Data for Managed DNS Peak usage trend Report validation")


        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search index=ib_dns_summary report=si_dns_member_qps_trend_per_5days | stats max(QCOUNT) as stats_COUNT by _time | sort _time | streamstats window=5 avg(stats_COUNT) as Peak_QPM | eval Date=strftime(_time, \"%Y-%m-%d\"),\"Peak QPS\"=round((stats_COUNT/60),3),\"5-Day Average Peak QPS\"=round((Peak_QPM/60),3) | table Date,\"Peak QPS\",\"5-Day Average Peak QPS\""

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


        if first['Peak QPS'] >= 30 and first['5-Day Average Peak QPS'] >= 30:
            print("-----------------------------------------")
            print("Peak QPS=",first['Peak QPS'])
            print("5-Day Average Peak QPS=",first['5-Day Average Peak QPS'])
            print("--------------***********----------------")
            print("PASSED")
            logger.info("Search validation result: %s (PASS)",first)

            
        else:
            logger.error("Search validation result: %s (FAIL)",first)

            msg = 'Count does not match - %s', first
            assert first == 0, first
        




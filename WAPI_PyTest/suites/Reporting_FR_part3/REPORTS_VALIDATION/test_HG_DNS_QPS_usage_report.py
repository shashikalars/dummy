

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



class DNS_qps_usage(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_1_DNS_QPS_usage(self):

    # EXPECTED VALUES

        logger.info ("Input Json Data for DNS QPS Usage report validation")


        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search index=ib_usage_count report=si_usage_count_member_qps_trend_per_5days | stats max(QCOUNT) as stats_COUNT by _time |eval stats_COUNT = stats_COUNT/1000 | sort _time | streamstats window=5 avg(stats_COUNT) as Peak_QPM | eval Date=strftime(_time, \"%Y-%m-%d\"),\"Peak kQPS\"=round((stats_COUNT/60),3),\"5-Day Average Peak kQPS\"=round((Peak_QPM/60),3) | table Date,\"Peak kQPS\",\"5-Day Average Peak kQPS\""

        
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


        if first['Peak kQPS'] >=0.072 and first['5-Day Average Peak kQPS'] >= 0.063:
            print("-----------------------------------------")
            print("Peak kQPS=",first['Peak kQPS'])
            print("5-Day Average Peak kQPS=",first['5-Day Average Peak kQPS'])
            print("--------------***********----------------")
            print("PASSED")
            logger.info("Search validation result: %s (PASS)",first)

            
        else:
            logger.error("Search validation result: %s (FAIL)",first)

            msg = 'Count does not match - %s', first
            assert first == 0, first
        
        
        



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


class  DHCP_LPS_usage_report(unittest.TestCase):
# DHCP LPS Usage Report


    @pytest.mark.run(order=1)
    def test_1_DHCP_LPS_usage_report(self):

        test1 = [{"Peak LPS":"4.000","5-Day Average Peak LPS":"4.000"}]
        logger.info ("Input Json Data for DHCP LPS Usage Report validation")
        logger.info(json.dumps(test1, sort_keys=True, indent=4, separators=(',', ': ')))

        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search index=ib_usage_count report=si_usage_count_member_dhcp_lps_trend_per_5days| stats max(LCOUNT) as stats_COUNT by _time| sort _time| streamstats window=5 avg(stats_COUNT) as Peak_LPM| eval Date=strftime(_time, \"%Y-%m-%d\"),\"Peak LPS\"=round((stats_COUNT/60),3),\"5-Day Average Peak LPS\"=round((Peak_LPM/60),3)| table Date,\"Peak LPS\",\"5-Day Average Peak LPS\""
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
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",test1,results_dist)
        logger.info("compare_results with 'delta=1'")
        result = compare_results(test1,results_list,1)
        print(result)
        logger.info("-----------------------------------------------------")
        logger.info(test1)
        logger.info(len(test1))
        logger.info("--------------------**************-------------------")
        logger.info(results_list)
        logger.info(len(results_list))
        logger.info("-----------------------------------------------------")

        if result == 0:
            print("PASSED")
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg
        


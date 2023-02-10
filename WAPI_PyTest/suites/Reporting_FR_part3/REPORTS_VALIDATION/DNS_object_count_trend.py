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


class DNS_object_count_trend_for_Flex_member(unittest.TestCase):
   
    @pytest.mark.run(order=1)
    def test_1(self):

        ## DNS Object Count Trend for FLEX Grid License

        test1 = [{"DNS Object Count":"6"}]
        logger.info ("Input Json Data for DNS Object Count Trend for FLEX Grid License report validation")
        logger.info(json.dumps(test1, sort_keys=True, indent=4, separators=(',', ': ')))

        # import pdb;pdb.set_trace()

        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search index=ib_ipam sourcetype=\"ib:dns:ibflex_zone_counts\" | bucket span=1d _time | stats sum(rr_total) as MAX_PER_DAY by _time | streamstats window=5 avg(MAX_PER_DAY) as MAX_COUNT | eval \"DNS Object Count\"=round(MAX_COUNT, 0) |  sort -_time | rename _time as Time | eval Time=strftime(Time, \"%Y-%m-%d %H:%M:%S %Z\") | table Time,\"DNS Object Count\""
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
    #        print(output_data)
        results_list = output_data['results']
        results_dist= results_list[-240::1]
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",test1,results_dist)
        logger.info("compare_results with 'delta=1'")
        result = compare_results(test1,results_list,1)
        print(result)
        logger.info("-----------------------------------------------------")
        logger.info(test1)
        logger.info(len(test1))
        logger.info("--------------------shashhhhhhhh-------------------")
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
        



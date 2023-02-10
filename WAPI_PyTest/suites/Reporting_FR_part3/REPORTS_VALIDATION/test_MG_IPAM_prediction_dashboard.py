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


class  IPAM_prediction_dashboard(unittest.TestCase):

    

    # 2. Subnet Utilization Prediction

    @pytest.mark.run(order=1)
    def test_1_IPAM_prediction_dashboard(self):

        test1=[{"Actual":"0.0","Threshold":"80"}]
        logger.info ("Input Json Data for IPAM Prediction dashboard: Subnet Utilization Prediction report validation")
        logger.info(json.dumps(test1, sort_keys=True, indent=4, separators=(',', ': ')))


        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search sourcetype=ib:dhcp:network index=ib_dhcp | eval view_network=view.\"/\".address.\"/\".cidr  | where (view_network==\"default/10.0.0.0/8\") | sort 0 -num(dhcp_utilization)  | convert ctime(_time) as Time  | timechart bins=200 max(dhcp_utilization) as percent_used_addresses | streamstats current=false window=1 avg(Prediction) as prev_prediction | eval threshold_str=\"80\" | eval threshold=tonumber(threshold_str) |  eval Hits=if(isnotnull(threshold) and ((prev_prediction < threshold and threshold <= Prediction) or (Prediction < threshold and threshold <= prev_prediction)),threshold,NULL)| rename percent_used_addresses  as Actual, threshold as Threshold| fields _time, Actual ,Prediction, Hits, Threshold"
        
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



import config
import json
import os
import pytest
import pexpect
import re
import sys
import subprocess
import logging
from time import sleep
import time
import unittest
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from logger import logger

from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results



class query_count_details_by_Subscriber_ID(unittest.TestCase):


    # Query Count Details by Subscriber ID

    @pytest.mark.run(order=1)
    def test_001_Comparing_and_Validating_new_values_with_expected_values(self):


        # Expected Values
        test1 = [{"Subscriber ID Value":"110361288","Event type":"STOP","Query Count":"1"}]
        logging.info ("Input Json Data for Query Count Details by Subscriber ID Report validation")
        logging.info(json.dumps(test1, sort_keys=True, indent=4, separators=(',', ': ')))


        logging.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search source=ib:dns:query:dca_query_count index=ib_dns | eval SUB_TYPE=if(isnull(SUB_TYPE),\"N/A\",SUB_TYPE) | eval SUB_VAL=if(isnull(SUB_VAL),\"N/A\",SUB_VAL) | eval IPS_VAL=if(isnull(IPS_VAL),\"N/A\",IPS_VAL) | eval EVENT_TYPE=if(isnull(EVENT_TYPE),\"N/A\",EVENT_TYPE) | eval QUERY_COUNT=if(isnull(QUERY_COUNT),\"0\",QUERY_COUNT) | sort -QUERY_COUNT | dedup 1  SUB_TYPE, SUB_VAL, IPS_VAL, CLIENT | head 10 | rename SUB_TYPE as \"Subscriber ID Type\", SUB_VAL as \"Subscriber ID Value\", IPS_VAL as \"IP Space Discriminator\", CLIENT as \"Client ID\", EVENT_TYPE as \"Event type\", QUERY_COUNT as \"Query Count\"  | table \"Subscriber ID Value\", \"Subscriber ID Type\", \"Client ID\", \"IP Space Discriminator\" ,\"Event type\" ,\"Query Count\""
        print(search_str)
        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        logging.info (cmd)

        print(os.system(cmd))
        print("-------------%%%----------")
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logging.error('search operation failed due to %s',e)
            raise Exception("Search operation failed, Please check Grid Configuration")
        output_data = json.loads(retrived_data)
        print(output_data)
        results_list = output_data['results']
        results_dist= results_list[-240::1]
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",test1,results_dist)
        logging.info("compare_results with 'delta=1'")
        result = compare_results(test1,results_list,1)
        print(result)
        logging.info("-----------------------------------------------------")
        logging.info(test1)
        logging.info(len(test1))
        logging.info("--------------------shashhhhhhhh-------------------")
        logging.info(results_list)
        logging.info(len(results_list))
        logging.info("-----------------------------------------------------")

        if result == 0:
            print("PASSED")
            logging.info("Search validation result: %s (PASS)",result)
        else:
            logging.error("Search validation result: %s (FAIL)",result)
            msg = 'Validation is not matching for object which is retrieved from DB %s', result
            assert result == 0, msg




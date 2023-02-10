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


class Flex_grid_licensing_features_enabled(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_1_flex_grid_licencing_features_enabled(self):
    
        # Expected values

        test1 = [{"Feature":"Active Trust Plus","Enabled":"No"},{"Feature":"Active Trust Standard","Enabled":"No"},{"Feature":"Authoritative DNS","Enabled":"No"},{"Feature":"Captive Portal","Enabled":"No"},{"Feature":"Cloud Network Automation","Enabled":"No"},{"Feature":"DHCP","Enabled":"Yes"},{"Feature":"DNS Cache Acceleration","Enabled":"Yes"},{"Feature":"DNS Traffic Control","Enabled":"No"},{"Feature":"Microsoft Management","Enabled":"No"},{"Feature":"Recursive DNS","Enabled":"Yes"},{"Feature":"Security Ecosystem","Enabled":"No"},{"Feature":"Subscriber Services","Enabled":"No"},{"Feature":"Threat Analytics","Enabled":"No"},{"Feature":"Threat Protection","Enabled":"Yes"}]
        logger.info ("Input Json Data for Flex Grid Features enabled report validation")
        logger.info(json.dumps(test1, sort_keys=True, indent=4, separators=(',', ': ')))

        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search index=ib_system source=\"ib:system:ibflex:feature_status\" (host_name=\"*\") | bucket span=1d _time | stats count by _time, service, status | sort -_time | dedup service sortby -status | eval status=case(status == \"0\", \"No\", status == \"1\", \"Yes\") | eval service=case(service == \"ATP\", \"Threat Protection\", service == \"DCA\", \"DNS Cache Acceleration\", service == \"ECO\", \"Security Ecosystem\", service == \"ADNS\", \"Authoritative DNS\", service == \"RDNS\", \"Recursive DNS\", service == \"RPZP\", \"Active Trust Plus\", service == \"RPZS\", \"Active Trust Standard\", service == \"IDNS\", \"DNS Traffic Control\", service == \"FREYE\", \"Fireeye\", service == \"TAN\", \"Threat Analytics\", service == \"SCS\", \"Subscriber Services\", service == \"DHCP\", \"DHCP\", service == \"CP\", \"Captive Portal\", service == \"MSMGM\", \"Microsoft Management\", service == \"CNA\", \"Cloud Network Automation\") | rename service as Feature, status as Enabled | table Feature, Enabled |  sort Feature"
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



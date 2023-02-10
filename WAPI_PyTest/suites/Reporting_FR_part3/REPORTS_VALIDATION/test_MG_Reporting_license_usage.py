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



class Reporting_license_usage(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_1_reporting_license_usage(self):

        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search index=_internal source=*license_usage.log* type=Usage LicenseUsage | eval v=(b/1024/1024) | timechart span=1d sum(v) as lu"


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
        lu=first['lu']
        print(lu)
        print("--------------***********----------------")

        if lu >= 1.0:
            print("PASSED")
            logger.info("Search validation result: %s (PASS)",lu)
        else:
            logger.error("Search validation result: %s (FAIL)",lu)

            msg = 'Validation value is Less than 1 MB - %s', lu
            assert lu == 0, msg


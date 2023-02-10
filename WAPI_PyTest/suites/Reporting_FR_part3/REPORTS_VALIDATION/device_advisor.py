
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

class device_advisor(unittest.TestCase):
    # Validation for Device Advisor

    @pytest.mark.run(order=1)
    def test_1_device_advisor(self):


        test1 = [{"Device Type":"Router","Asset Type":"Physical Device","Device Vendor":"Cisco","OS Version":"15.0(2)SE8","Device Name":"ni-mri-core.inca.infoblox.com","Device IP":"10.40.16.1","Network View":"discovery_view"},{"Device Type":"Switch","Asset Type":"Physical Device","Device Name":"unknown","Device IP":"10.40.16.8","Network View":"discovery_view"},{"Device Type":"Switch-Router","Asset Type":"Physical Device","Device Vendor":"Juniper","OS Version":"13.2X51-D20.2","Device Name":"EX2200-48T-4G","Device IP":"10.40.16.7","Network View":"discovery_view"}]
        logger.info ("Input Json Data for Device components report validation")
        logger.info(json.dumps(test1, sort_keys=True, indent=4, separators=(',', ': ')))

        # import pdb;pdb.set_trace()

        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search source=ib:discovery:device_advisor index=ib_discovery | dedup ip_address | rename device_type as \"Device Type\" asset_type as \"Asset Type\" device_vendor as \"Device Vendor\" device_os_version as \"OS Version\" serial_number as \"Chassis S/N\" chassis_part_number as \"Chassis P/N\" ip_address as \"Device IP\" device_name as \"Device Name\" network_view as \"Network View\" eoxstatus as \"EOL Status\" eosdate as \"End of Sale Date\" eoldate as \"End of Support Date\" url as \"EOL Bulletin URL\" cvecount as \"CVE Bulletin Count\" cvelist as \"CVE Bulletin List\" | table \"Device Type\" \"Asset Type\" \"Device Vendor\" \"OS Version\" \"Device Name\" \"Chassis S/N\" \"Chassis P/N\" \"Device IP\" \"Network View\" \"EOL Status\" \"End of Sale Date\" \"End of Support Date\" \"EOL Bulletin URL\" \"CVE Bulletin Count\" \"CVE Bulletin List\" | sort -_time +str(\"Device Type\")"
    #        print(search_str)
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


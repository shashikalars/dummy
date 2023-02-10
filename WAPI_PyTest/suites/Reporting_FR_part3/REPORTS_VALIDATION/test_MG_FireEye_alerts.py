

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



class FireEye_alerts(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_1_Fireeye_alerts(self):

    # EXPECTED VALUES

        test1 = [{"Log Severity":"Minor","Alert Type":"Domain Match","FireEye Appliance":"FireEye alert simulator_Gridmember1","Mitigation Action":"Passthru"},{"Log Severity":"Minor","Alert Type":"Malware Object","FireEye Appliance":"FireEye alert simulator_Gridmember1","Mitigation Action":"Passthru"}]
        logger.info ("Input Json Data for Fire-eye alerts report validation")
        logger.info(json.dumps(test1, sort_keys=True, indent=4, separators=(',', ': ')))


        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search sourcetype=ib:dns:reserved index=ib_dns info fireeye-rpt | eval TYPE=case(ALERT_TYPE == \"web-infection\", \"Web Infection\", ALERT_TYPE == \"malware-object\", \"Malware Object\", ALERT_TYPE == \"domain-match\", \"Domain Match\", ALERT_TYPE == \"malware-callback\", \"Callback Events\", ALERT_TYPE == \"infection-match\", \"Infection Events\") | eval SEVERITY=case(LOG_SEVERITY == \"majr\", \"Major\", LOG_SEVERITY == \"crit\", \"Critical\", LOG_SEVERITY == \"minr\", \"Minor\") | eval ALERT_TYPE=if(isnull(TYPE), ALERT_TYPE,TYPE) | eval LOG_SEVERITY=if(isnull(SEVERITY), LOG_SEVERITY,SEVERITY) | eval RPZ_RULE = if(isnull(RPZ_RULE), \"None\",RPZ_RULE) | eval ACTION = if(isnull(ACTION), \"None\",ACTION)  | eval MITIGATION_ACTION=case(ACTION == \"Passthru\", \"PT\", ACTION == \"Block (No Such Domain)\", \"NX\", ACTION == \"Block (No Data)\", \"ND\", ACTION == \"Substitute (Domain Name)\", \"DN\", ACTION == \"None\", \"None\") | rename ALERT_ID as \"Alert ID\", LOG_SEVERITY as \"Log Severity\", ALERT_TYPE as \"Alert Type\", RPZ_RULE as \"RPZ Entry\", ACTION as \"Mitigation Action\", APP_ID as \"FireEye Appliance\" | convert ctime(_time) as Time | table Time, \"Alert ID\", \"Log Severity\", \"Alert Type\", \"FireEye Appliance\", \"RPZ Entry\", \"Mitigation Action\""

        
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
        logger.info("----------------------**********---------------------")
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


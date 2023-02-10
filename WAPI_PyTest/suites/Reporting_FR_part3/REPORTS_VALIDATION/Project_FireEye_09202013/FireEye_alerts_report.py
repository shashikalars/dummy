"""
 Copyright (c) Infoblox Inc., 2016

 ReportName          : DNS Query Rate By Query Type
 ReportCategory      : DNS Query
 Number of Test cases: 1
 Execution time      : 361.09 seconds
 Execution Group     : Minute Group (MG)
 Description         : DNS 'Query Rate by Query Type' report update every 1 min.

 Author   : Vindya V K
 History  : 02/24/2021 (Created)
 Reviewer : Shekhar, Manoj
"""

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

"""
TEST Steps:
      1.  Input/Preparaiton      : Creating a superuser under fire-eye group and Adding zone_rp
      2.  Search                 : Search with Default Filter
      3.  Validation             : Validating Search result against input data
"""


class  FireEye_alerts(unittest.TestCase):
    @classmethod

    def setup_class(cls):

        logger.info("Creating a super User for fire-eye Group")
        get_ref = ib_NIOS.wapi_request('GET',object_type="admingroup")
        logger.info(get_ref)
        ref1 = json.loads(get_ref)[5]['_ref']
        print(ref1)

        data={"superuser":True}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)



        user={"name":"user","password":"user@123","admin_groups":["fireeye-group"]}
        get_ref = ib_NIOS.wapi_request('POST',object_type="adminuser", fields=json.dumps(user))
        if (get_ref[0] == 400):
            print("Duplicate object \'user\' of type \'adminuser\' already exists in the database")
            assert True
        else:
            print("User \'user\' has been created")


# Creating DNS response policy zone

        logger.info("Add zone_rp 'test.com'")
        rpz = {"fqdn": "test.com","grid_primary": [{"name": "infoblox.localdomain"}], "rpz_type": "FIREEYE"}
        rpz_response = ib_NIOS.wapi_request('POST', object_type="zone_rp", fields=json.dumps(rpz),grid_vip=config.grid_vip)
        rpz_get = ib_NIOS.wapi_request('GET', object_type="zone_rp")
        rpz_ref = json.loads(rpz_get)[0]['_ref']
        print(rpz_ref)

        # Restart Services

        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(30)


# Editing Grid DNS properties - adding forwarder and enabling recurssion

        logger.info("Adding Forwarder and enabling recursion")
        grid_get = ib_NIOS.wapi_request('GET',object_type="grid:dns")
        logger.info(get_ref)
        grid_ref = json.loads(grid_get)[0]['_ref']
        print(grid_ref)

        grid={"allow_recursive_query": True,"forwarders": ["10.39.16.160"]}
        grid_response = ib_NIOS.wapi_request('PUT',ref=grid_ref,fields=json.dumps(grid),grid_vip=config.grid_vip)
        print(grid_response)


        # Restart Services

        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(30)

# Execute ./run_alert_tests.sh

        cmd = os.system("./run_alert_tests.sh").read()
        print(cmd)


        logger.info ("Wait 5 minutes for reports to get update")
        sleep(150)



# EXPECTED VALUES

        cls.test1 = [{"Alert ID":"infection-match_1615541827013887895","Alert Type":"Infection Events", "RPZ Entry":"asm.com.test.com"},{"Alert ID":"malware-object_161554182660357684202","Alert Type":"Malware Object","RPZ Entry":"us.com.test.com"},{"Alert ID":"domain-match_1615541827138977689","Alert Type":"Domain Match","RPZ Entry":"domain.com.test.com"},{"Alert ID":"web-infection_1615541826883390913","Alert Type":"Web Infection","RPZ Entry":"infoblox.com.test.com"},{"Alert ID":"malware-callback_1615541826443421838","Alert Type":"Callback Events","RPZ Entry":"banglore.com.test.com"}]
        logger.info ("Input Json Data for Fire-eye alerts report validation")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))




    @pytest.mark.run(order=1)
    def test_1(self):
        # import pdb;pdb.set_trace()

        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search sourcetype=ib:dns:reserved index=ib_dns info fireeye-rpt | eval TYPE=case(ALERT_TYPE == \"web-infection\", \"Web Infection\", ALERT_TYPE == \"malware-object\", \"Malware Object\", ALERT_TYPE == \"domain-match\", \"Domain Match\", ALERT_TYPE == \"malware-callback\", \"Callback Events\", ALERT_TYPE == \"infection-match\", \"Infection Events\") | eval SEVERITY=case(LOG_SEVERITY == \"majr\", \"Major\", LOG_SEVERITY == \"crit\", \"Critical\", LOG_SEVERITY == \"minr\", \"Minor\") | eval ALERT_TYPE=if(isnull(TYPE), ALERT_TYPE,TYPE) | eval LOG_SEVERITY=if(isnull(SEVERITY), LOG_SEVERITY,SEVERITY) | eval RPZ_RULE = if(isnull(RPZ_RULE), \"None\",RPZ_RULE) | eval ACTION = if(isnull(ACTION), \"None\",ACTION)  | eval MITIGATION_ACTION=case(ACTION == \"Passthru\", \"PT\", ACTION == \"Block (No Such Domain)\", \"NX\", ACTION == \"Block (No Data)\", \"ND\", ACTION == \"Substitute (Domain Name)\", \"DN\", ACTION == \"None\", \"None\") | rename ALERT_ID as \"Alert ID\", LOG_SEVERITY as \"Log Severity\", ALERT_TYPE as \"Alert Type\", RPZ_RULE as \"RPZ Entry\", ACTION as \"Mitigation Action\", APP_ID as \"FireEye Appliance\" | convert ctime(_time) as Time | table Time, \"Alert ID\", \"Log Severity\", \"Alert Type\", \"FireEye Appliance\", \"RPZ Entry\", \"Mitigation Action\""
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
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test1,results_dist)
        logger.info("compare_results with 'delta=1'")
        result = compare_results(self.test1,results_list,1)
        print(result)
        logger.info("-----------------------------------------------------")
        logger.info(self.test1)
        logger.info(len(self.test1))
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

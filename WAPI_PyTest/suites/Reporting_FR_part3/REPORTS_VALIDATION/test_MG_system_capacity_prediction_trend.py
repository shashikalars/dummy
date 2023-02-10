import re
import config
import pytest
import unittest
import logging
import subprocess
import os
import json
import ib_utils.ib_NIOS as ib_NIOS
import commands
import json, ast
import requests
from time import sleep as sleep
import pexpect
import paramiko
import time
import sys
from paramiko import client
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results


class  System_Capacity_Prediction_trend(unittest.TestCase):


# Max CPU Utilization

    @pytest.mark.run(order=001)
    def test_001_Max_CPU_Utilization(self):

        # Expected Values
        test1 = [{"threshold":"80"}]
        logging.info ("Input Json Data for Max CPU Utilization Report validation")
        logging.info(json.dumps(test1, sort_keys=True, indent=4, separators=(',', ': ')))


        logging.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search index=ib_system_summary report=si_cpu_usage orig_host="+config.grid_fqdn+" | head 1 | eval threshold_str=\"80\" | eval threshold=if(isnull(tonumber(threshold_str)), \"not set\", tonumber(threshold_str)) | table threshold"
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


# CPU Prediction Trend

    @pytest.mark.run(order=002)
    def test_002_CPU_Prediction_trend(self):

        # Expected Values
        test2 = [{"Threshold":"80"}]
        logging.info ("Input Json CPU Prediction trend Report validation")
        logging.info(json.dumps(test2, sort_keys=True, indent=4, separators=(',', ': ')))


        logging.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search index=ib_system_summary report=si_cpu_usage orig_host="+config.grid_fqdn+" | timechart bins=200 avg(CPU_PERCENT) by orig_host | streamstats current=false window=1 avg(Prediction) as prev_prediction | eval threshold_str=\"80\" | eval threshold=tonumber(threshold_str) |  eval Hits=if(isnotnull(threshold) and ((prev_prediction < threshold and threshold <= Prediction) or (Prediction < threshold and threshold <= prev_prediction)),threshold,NULL) | rename _time as Time, infoblox.localdomain as Actual, threshold as Threshold | eval Time=strftime(Time, \"%Y-%m-%d %H:%M:%S %Z\") | fields Time, Actual, Prediction, Hits, Threshold"
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
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",test2,results_dist)
        logging.info("compare_results with 'delta=1'")
        result = compare_results(test2,results_list,1)
        print(result)
        logging.info("-----------------------------------------------------")
        logging.info(test2)
        logging.info(len(test2))
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


# Max DB Object Utilization

    @pytest.mark.run(order=003)
    def test_003_Max_DB_Object_Utilization(self):

        # Expected Values
        test3 = [{"info":"IB-V1415:440,000"}]
        logging.info ("Input Json Data for Max DB Object Utilization Report validation")
        logging.info(json.dumps(test3, sort_keys=True, indent=4, separators=(',', ': ')))


        logging.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search index=\"ib_system_capacity\" source=\"ib:system_capacity:objects\" host="+config.grid_fqdn+" | head 1 | eval threshold_str=\"440000\" | eval threshold=if(isnull(tonumber(threshold_str)), \"not set\", tonumber(threshold_str)) | eval hhm = \"IB-V1415\" | eval info = tostring(floor(440000), \"commas\") | eval info = hhm.\":\".info | table info"
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
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",test3,results_dist)
        logging.info("compare_results with 'delta=1'")
        result = compare_results(test3,results_list,1)
        print(result)
        logging.info("-----------------------------------------------------")
        logging.info(test3)
        logging.info(len(test3))
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



#!/usr/bin/env python
__author__ = "Chetan Kumar PG"
__email__  = "cpg@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Stand alone Grid Master                                               #
#  2. Licenses : DNS, Grid, NIOS(IB_1415)                                   #
#############################################################################

import config
import pytest
import unittest
import logging
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',level=logging.INFO, filename='niosspt_11365.log', filemode='w')

def display_msg(x=""):
    """
    Additional function.
    """
    logging.info(x)
    print(x)

class NIOSSPT_11365(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_01_start_log(self):
        """
        Start log capture on infoblox.log
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case 1 Started                |")
        display_msg("------------------------------------------------")

        display_msg("Starting log capture on infoblox.log")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        
        display_msg("---------Test Case 1 Execution Completed----------")

    @pytest.mark.run(order=2)
    def test_02_modify_hostname(self):
        """
        Modify the hostname of the Master Grid Member
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case 2 Started                |")
        display_msg("------------------------------------------------")

        '''Modifying Host name'''
        display_msg("Modify hostname of the Master Grid Member")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member', params='?_return_fields=host_name')
        display_msg(get_ref)
        ref = json.loads(get_ref)[0]
        global old_hostname
        old_hostname = ref["host_name"]
        new_hostname = "modified.com"
        response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps({"host_name":new_hostname}))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failed: Modifying hostname of the Master Grid Member")
            assert False

        sleep(180)

        '''Validation'''
        display_msg("Validation: Started")
        response_val = ib_NIOS.wapi_request('GET', object_type='member', params='?_return_fields=host_name')
        display_msg(response_val)
        display_msg("Validation: Stopped")
        if not json.loads(response_val)[0]["host_name"] == new_hostname:
            display_msg("Validation: Failed")
            assert False
        display_msg("Validation: passed")
        display_msg("Passed: Modifying hostname of the Master Grid Member")

        display_msg("---------Test Case 2 Execution Completed----------")

    @pytest.mark.run(order=3)
    def test_03_stop_and_validate_captured_logs(self):
        """
        Stop and Validate capture infoblox.log
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case 3 Started                |")
        display_msg("------------------------------------------------")

        display_msg("Stopping log capture on infoblox.log")
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        
        LookFor=[".*Certificate regeneration request found", ".*does NOT match certificate, regenerating", 
                 ".*Regenerated default cert/key pair", ".*Apache is running.  Stopping and restarting", 
                 ".*httpd.*The process stopped normally", ".*Restarting Apache", ".*httpd.*The process started normally.*"]
        flag = False
        for string in LookFor:
            display_msg("LookFor: "+string)
            display_msg("Starting Log validation")
            logs=logv(string,"/infoblox/var/infoblox.log",config.grid_vip)
            display_msg(logs)
            if logs:
                display_msg("Passed: String found\n")
            else:
                display_msg("Failed: String not found\n")
                flag = True
        if flag:
            display_msg("Failed: Log validation")
            assert False
        display_msg("Passed: Log validation")
        
        display_msg("---------Test Case 3 Execution Completed----------")

    @pytest.mark.run(order=4)
    def test_04_cleanup(self):
        """
        Revert to original hostname of the Master Grid Member
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case 4 Started                |")
        display_msg("------------------------------------------------")

        '''Revert to original Host name'''
        global old_hostname
        display_msg("Revert to original hostname of the Master Grid Member")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member', params='?_return_fields=host_name')
        display_msg(get_ref)
        ref = json.loads(get_ref)[0]
        response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps({"host_name":old_hostname}))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failed: Reverting to original hostname of the Master Grid Member")
            assert False

        sleep(180)

        '''Validation'''
        display_msg("Validation: Started")
        response_val = ib_NIOS.wapi_request('GET', object_type='member', params='?_return_fields=host_name')
        display_msg(response_val)
        display_msg("Validation: Stopped")
        if not json.loads(response_val)[0]["host_name"] == old_hostname:
            display_msg("Validation: Failed")
            assert False
        display_msg("Validation: passed")
        display_msg("Passed: Reverting to original hostname of the Master Grid Member")

        display_msg("---------Test Case 4 Execution Completed----------")

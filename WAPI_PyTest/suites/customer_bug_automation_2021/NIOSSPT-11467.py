__author__ = "Aditya G"
__email__  = "adityag@infoblox.com"

#####################################################################################################
#  Grid Set up required:                                                                            #
#  1. Standalone GM                                                                                 #
#  2. Licenses : DNS, DHCP, Grid                                                                    #
#####################################################################################################

import re
import config
import pytest
import unittest
import logging
import subprocess
import os
import json
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.dig_utility
from time import sleep
import commands
import json, ast
import time
import getpass
import sys
import pexpect
import paramiko
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv


logging.basicConfig(filename='niosspt11467.log', filemode='w', level=logging.DEBUG)

class NIOSSPT11467(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test001_Start_log_capture_on_the_grid(self):
        '''Start capture of infoblox.log on master'''
        log("start","/infoblox/var/infoblox.log",config.grid_vip)

    @pytest.mark.run(order=2)
    def test002_Create_Smart_Folder_with_Conflict_and_IP_filters(self):
        ''' Create a smart folder with the filters "Conflict" and "IP" '''
        logging.info(" Create a smart folder with the filters \"Conflict\" and \"IP\" ")
        data = { "name": "NIOSSPT11467","query_items": [{"field_type": "NORMAL","name": "was_conflict","op_match": True,"operator": "EQ","value": {"value_boolean": True},"value_type": "BOOLEAN"},{"field_type": "NORMAL","name": "address","op_match": True,"operator": "BEGINS_WITH","value": {"value_string": "10.65.128.0/21"},"value_type": "STRING"}]}
        smart_folder_reference = ib_NIOS.wapi_request('POST',object_type='smartfolder:personal',fields=json.dumps(data))
        logging.info(smart_folder_reference)
        if bool(re.match("\"smartfolder:personal*.",str(smart_folder_reference))):
            logging.info("Smart folder created successfully")
            sleep(5)
            assert True
        else:
            logging.info("Smart folder creation unsuccessful")

    @pytest.mark.run(order=3)
    def test003_Verify_if_Smart_Folders_have_been_created(self):
        ''' Verify if the smart folder in testcase 1 has been created by doing WAPI GET operation'''
        logging.info("Verifying if the smartfolder \"NIOSSPT11467\" has been created")
        count=0
        smart_folder_info = ib_NIOS.wapi_request('GET',object_type='smartfolder:personal')
        logging.info(smart_folder_info)
        for ref in json.loads(smart_folder_info):
            if ref['name'] == 'NIOSSPT11467':
                logging.info("Smart folder NIOSSPT11467 found")
                count +=1
                assert True
        if count!=1:
            logging.info("Smart folder NIOSSPT11467 not found")
            assert False

    @pytest.mark.run(order=4)
    def test004_Stop_log_capture_and_verify_if_any_error_messages_are_present_in_the_logs(self):
        '''Stopping the capture of infoblox.log and verify if the error logs are present in the captured logs'''
        logging.info('Stopping log capture')
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)

        '''Check the captured logs for any error messages'''
        error_logs=['ERROR com.infoblox.data.json.AbstractJsonTarget.*Error during JSON response','/infoblox/one/bin/forced_restore_save_data) forced_restore_save_data.c:395 save_data_before_restore(): invalid argument','/infoblox/one/bin/forced_restore_save_data) forced_restore_save_data.c:1833 main(): invalid argument','/infoblox/one/bin/reset_node_storage) : ERROR: missing saved_node_data','/infoblox/one/bin/reset_node_storage) : mount /config as rw','/infoblox/one/bin/reset_node_storage) : ./vpn_addrs/v15 updated']

        logging.info("Checking captured logs for error messages")
        count=0
        for error_msg in error_logs:
            logs=logv(error_msg,"/infoblox/var/infoblox.log",config.grid_vip)
            if(logs):
                count +=1

        if count!=0:
            logging.info("Error message encountered in logs, creation of Smart folder failed")
            assert False
        else:
            logging.info("Error message not encountered in logs, creation of Smart folder successful")
            assert True


    @pytest.mark.run(order=5)
    def test005_Test_Cleanup(self):
        logging.info("Perform test cleanup")
        smart_folder_info = ib_NIOS.wapi_request('GET',object_type='smartfolder:personal')
        logging.info(smart_folder_info)
        for ref in json.loads(smart_folder_info):
            if ref['name'] == 'NIOSSPT11467':
                smart_folder_del = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
                logging.info(smart_folder_del)
                if bool(re.match("\"smartfolder:personal*.",str(smart_folder_del))):
                    logging.info("Smart folder deleted successfully")
                    sleep(5)
                    assert True
                else:
                    logging.info("Smart folder deletion unsuccessful")
                    assert False










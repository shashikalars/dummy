__author__ = "Siva Krishna"
__email__  = "krishnas@infoblox.com"

####################################################
#  Grid Set up required:                           #
#  1. Standalone Grid                           #
#  2. Licenses : DNS, DHCP, Gride,NIOS (IB-V1415)  #
####################################################
import re
import config
import pytest
import unittest
import logging
import os
import os.path
from os.path import join
import subprocess
import json
import time
from time import sleep
import commands
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util
import ib_utils.log_capture as log_capture
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv

import pexpect
import paramiko
from paramiko import client

class Crafted_DNS_packet_with_invalid_TSIG_RR(unittest.TestCase):
	@pytest.mark.run(order=1)
        def test_001_Start_DNS_Service(self):
                logging.info("Start DNS Service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                for i in res:
                        logging.info("Modify a enable_dns")
                        data = {"enable_dns": True}
                        response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
                        print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 1 Execution Completed")

        @pytest.mark.run(order=2)
        def test_002_Validate_DNS_service_Enabled(self):
                logging.info("Validate DNs Service is enabled")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                for i in res:
                        print i
                        logging.info("found")
                        assert i["enable_dns"] == True
                print("Test Case 2 Execution Completed")

	@pytest.mark.run(order=3)
        def test_003_Starting_Logs(self):
                logging.info("Logs Validation")
                log("start","/var/log/syslog",config.grid_vip)
                sleep(5)

	@pytest.mark.run(order=4)
	def test_004_Executing_Python_script(self):	
		script_cmd='python 1703_poc.py ' + config.grid_vip +' 53'
		output=os.system(script_cmd)
		print(output)			
		sleep(30)	
                script_cmd='python 1703_poc.py ' + config.grid_vip +' 53'
                output=os.system(script_cmd)
                print(output)
                sleep(30)
	
	@pytest.mark.run(order=5)
        def test_005_Stopping_Logs(self):
                logging.info("Logs Validation")
                log("stop","/var/log/syslog",config.grid_vip)
                sleep(5)
	
	@pytest.mark.run(order=6)
        def test_006_Validate_Core_Files(self):
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                print('running remote command for')
                ssh.connect(config.grid_vip, username='root')
                stdin, stdout, stderr = ssh.exec_command("find /storage/cores/ -name  core.*")
		response=stdout.readlines()
		print(response)
		if (response==[]):
			assert True
		else:
			assert False

	@pytest.mark.run(order=7)
        def test_007_Validate_DNS_service_Enabled(self):
                logging.info("Validate DNs Service is enabled")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                for i in res:
                        print i
                        logging.info("found")
                        assert i["enable_dns"] == True
                print("Test Case 7 Execution Completed")
		
        @pytest.mark.run(order=8)
        def test_008_looking_for_assertion_failure_Negative(self):
                LookFor="crit exiting (due to assertion failure)"
                logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
                #check=commands.getoutput(" grep -cw \".*crit exiting (due to assertion failure).*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
		print(logs)
                if logs == None:
                    assert True
                else:
                    assert False


                sleep(5)

	@pytest.mark.run(order=9)
        def test_009_Stop_DNS_Service(self):
                logging.info("Stop DNS Service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                for i in res:
                        logging.info("Modify a enable_dns")
                        data = {"enable_dns": False}
                        response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
                        print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 09 Execution Completed")

        @pytest.mark.run(order=10)
        def test_010_Validate_DNS_service_Disabled(self):
                logging.info("Validate disable DNS Service ")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                for i in res:
                        print i
                        logging.info("found")
                        assert i["enable_dns"] == False
                print("Test Case 10 Execution Completed")

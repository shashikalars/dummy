import re
import sys
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
import subprocess
from time import sleep
import commands
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util
import ib_utils.log_capture as log_capture
from  ib_utils.log_capture import log_action as log
from  ib_utils.log_validation import log_validation as logv
import pexpect
import paramiko
from paramiko import client
class Rfe_LRT(unittest.TestCase):

	#Validating the transaction logs before enabling Debug
	@pytest.mark.run(order=1)
        def test_001_Starting_Logs_To_Capture_Transaction_Logs(self):
                logging.info("Start Logs")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
		ref =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                print(ref)
                sleep(10)
                print("Test Case 1 Execution Completed")
	
	@pytest.mark.run(order=2)
        def test_002_Stopping_Logs_after_Transaction_Logs_capture(self):
                logging.info("Stop Logs")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                sleep(2)
                print("Test Case 2 Execution Completed")

        @pytest.mark.run(order=3)
        def test_003_Validate_Default_Login_Transaction_in_Infoblox_Log(self):
                logging.info("Validate_Default_Login_Transaction_in_Infoblox_Log")
		check=commands.getoutput(" grep -cw \".*Read Only txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                check_1=commands.getoutput(" grep -cw \".*Read Write txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
		print(check,check_1,type(check),type(check_1))
                if ((int(check)==0) and (int(check_1)==0)):
                    assert True
                else:
                    assert False
		print("Test Case 3 Execution Completed")

	@pytest.mark.run(order=4)
        def test_004_Enabling_Disable_Concurrent_Login_Security_feature(self):
                logging.info("Enabling Disable Concurrent Login Security feature")
                ref =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
		data = {"security_setting": {"disable_concurrent_login": True}}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(5)
		print("Test Case 4 Execution Completed")
	
	@pytest.mark.run(order=5)
        def test_005_Validate_Enabled_Disable_Concurrent_Login_Security_feature(self):
                logging.info("Validate Enabled Disable Concurrent Login Security feature")
                response =  ib_NIOS.wapi_request('GET', object_type="grid?_return_fields=security_setting", grid_vip=config.grid_vip)
                print response
                logging.info(response)
		assert re.search(r'"disable_concurrent_login": true',response)
		sleep(5)
		print("Test Case 5 Execution Completed")

	@pytest.mark.run(order=6)
        def test_006_Validate_Login_Transaction_in_Infoblox_Log(self):
                logging.info("Validate Login Transaction in Infoblox_Log")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                ref =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                print(ref)
                sleep(10)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                check=commands.getoutput(" grep -cw \".*Read Only txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                check_1=commands.getoutput(" grep -cw \".*Read Write txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(check,check_1,type(check),type(check_1))
                if ((int(check)==0) and (int(check_1)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 6 Execution Completed")

	@pytest.mark.run(order=7)
        def test_007_Enabling_Enable_Account_Lockout_Security_feature(self):
                logging.info("Enabling Enable Account Lockout Security feature")
                ref =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"lockout_setting": {"enable_sequential_failed_login_attempts_lockout": True,"failed_lockout_duration": 5,"never_unlock_user": False,"sequential_attempts": 5}} 
		response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(5)
		print("Test Case 7 Execution Completed")

	@pytest.mark.run(order=8)
        def test_008_Validate_Enabled_Enable_Account_Lockout_Security_feature(self):
                logging.info("Validate Enabled Enable Account Lockout Security feature")
                response =  ib_NIOS.wapi_request('GET', object_type="grid?_return_fields=lockout_setting", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                assert re.search(r'"enable_sequential_failed_login_attempts_lockout": true',response)
                sleep(5)
                print("Test Case 8 Execution Completed")

        @pytest.mark.run(order=9)
        def test_009_Validate_Login_Transactions_in_Infoblox_Log(self):
                logging.info("Validate Login Transaction in Infoblox_Log")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                ref =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                print(ref)
                sleep(10)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                check=commands.getoutput(" grep -cw \".*Read Only txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                check_1=commands.getoutput(" grep -cw \".*Read Write txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
		if ((int(check)==0) and (int(check_1)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 9 Execution Completed")

	@pytest.mark.run(order=10)
        def test_010_Disabling_Disable_Concurrent_Login_Security_feature(self):
                logging.info("Disabling Disable Concurrent Login Security feature")
                ref =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
		data = {"security_setting": {"disable_concurrent_login": False}}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(5)
		print("Test Case 10 Execution Completed")	

	@pytest.mark.run(order=11)
        def test_011_Validate_Disabled_Disable_Concurrent_Login_Security_feature(self):
                logging.info("Validate Disabled Disable Concurrent Login Security feature")
		response =  ib_NIOS.wapi_request('GET', object_type="grid?_return_fields=security_setting", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                assert re.search(r'"disable_concurrent_login": false',response)
                sleep(5)
                print("Test Case 11 Execution Completed")

        @pytest.mark.run(order=12)
        def test_012_Validate_Login_Transaction_in_Infoblox_Log(self):
                logging.info("Validate Login Transaction in Infoblox_Log")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                ref =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                print(ref)
                sleep(10)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                check=commands.getoutput(" grep -cw \".*Read Only txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                check_1=commands.getoutput(" grep -cw \".*Read Write txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
		if ((int(check)==0) and (int(check_1)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 12 Execution Completed")

	@pytest.mark.run(order=13)
        def test_013_Disabling_Disable_Account_Lockout_Security_feature(self):
                logging.info("Disabling Disable Account Lockout Security feature")
                ref =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"lockout_setting": {"enable_sequential_failed_login_attempts_lockout": False,"failed_lockout_duration": 5,"never_unlock_user": False,"sequential_attempts": 5}}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(5)
		print("Test Case 13 Execution Completed")
	
	@pytest.mark.run(order=14)
        def test_014_Validate_Disabled_Disable_Account_Lockout_Security_feature(self):
                logging.info("Validate Disabled Disable Account Lockout Security feature")
		response =  ib_NIOS.wapi_request('GET', object_type="grid?_return_fields=lockout_setting", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                assert re.search(r'"enable_sequential_failed_login_attempts_lockout": false',response)
                sleep(5)
                print("Test Case 14 Execution Completed")

        @pytest.mark.run(order=15)
        def test_015_Validate_Login_Transactions_in_Infoblox_Log(self):
                logging.info("Validate Login Transaction in Infoblox_Log")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                ref =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                print(ref)
                sleep(10)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
		check=commands.getoutput(" grep -cw \".*Read Only txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                check_1=commands.getoutput(" grep -cw \".*Read Write txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                if ((int(check)==0) and (int(check_1)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 15 Execution Completed")

	@pytest.mark.run(order=16)
        def test_016_Enabling_Disable_Concurrent_Login_Security_feature_Group_Level(self):
                logging.info("Enabling Disable Concurrent Login Security feature at group level")
                ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=admin-group", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
		print(config.grid_vip)
                data = {"use_disable_concurrent_login": True,"disable_concurrent_login": True}
		response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(5)
		print("Test Case 16 Execution Completed")

	@pytest.mark.run(order=17)
        def test_017_Validate_Enabled_Disable_Concurrent_Login_Security_feature_Group_Level(self):
                logging.info("Validate Enabled Disable Concurrent Login Security feature at group level")
		ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=admin-group", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=disable_concurrent_login", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                assert re.search(r'"disable_concurrent_login": true',response)
                sleep(5)
                print("Test Case 17 Execution Completed")

        @pytest.mark.run(order=18)
        def test_018_Validate_Login_Transaction_in_Infoblox_Log(self):
                logging.info("Validate Login_Transaction_in_Infoblox_Log")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                ref =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                print(ref)
                sleep(10)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
		check=commands.getoutput(" grep -cw \".*Read Only txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                check_1=commands.getoutput(" grep -cw \".*Read Write txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
		print(check,type(check),check_1,type(check_1))
                if ((int(check)==0) and (int(check_1)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 18 Execution Completed")

	@pytest.mark.run(order=19)
        def test_019_Enabling_Enable_Account_Lockout_Security_feature_Group_Level(self):
                logging.info("Enabling Enable Account Lockout Security feature at group level")
                ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=admin-group", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"use_lockout_setting": True,"lockout_setting": {"enable_sequential_failed_login_attempts_lockout": True,"failed_lockout_duration": 5,"never_unlock_user": False,"sequential_attempts": 5}}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(5)
		print("Test Case 19 Execution Completed")

	@pytest.mark.run(order=20)
        def test_020_Validate_Enabled_Enable_Account_Lockout_Security_feature_Group_Level(self):
                logging.info("Validate Enabled Enable Account Lockout Security feature at group level")
		ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=admin-group", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=lockout_setting", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                assert re.search(r'"enable_sequential_failed_login_attempts_lockout": true',response)
                sleep(5)
                print("Test Case 20 Execution Completed")

        @pytest.mark.run(order=21)
        def test_021_Validate_Login_Transaction_in_Infoblox_Log(self):
                logging.info("Validate Login Transaction in Infoblox_Log")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                ref =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                print(ref)
                sleep(10)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                check=commands.getoutput(" grep -cw \".*Read Only txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox*")
                check_1=commands.getoutput(" grep -cw \".*Read Write txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox*")
                print(check,type(check),check_1,type(check_1))
                if ((int(check)==0) and (int(check_1)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 21 Execution Completed")

	@pytest.mark.run(order=22)
        def test_022_Disabling_Disable_Concurrent_Login_Security_feature_Group_Level(self):
                logging.info("Disabling Disable Concurrent Login Security feature at group level")
                ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=admin-group", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"use_disable_concurrent_login": False,"disable_concurrent_login": False}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(5)
		print("Test Case 22 Execution Completed")

	@pytest.mark.run(order=23)
        def test_023_Validate_Disabled_Disable_Concurrent_Login_Security_feature_Group_Level(self):
                logging.info("Validate Disabled Disable Concurrent Login Security feature at group level")
                ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=admin-group", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=disable_concurrent_login", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                assert re.search(r'"disable_concurrent_login": false',response)
                sleep(5)
                print("Test Case 23 Execution Completed")
	
        @pytest.mark.run(order=24)
        def test_024_Validate_Login_Transaction_in_Infoblox_Log(self):
                logging.info("Validate Login Transaction in Infoblox_Log")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                ref =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                print(ref)
                sleep(10)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                check=commands.getoutput(" grep -cw \".*Read Only txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                check_1=commands.getoutput(" grep -cw \".*Read Write txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(check,type(check),check_1,type(check_1))
                if ((int(check)==0) and (int(check_1)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 24 Execution Completed")

	@pytest.mark.run(order=25)
        def test_025_Disabling_Enable_Account_Lockout_Security_feature_Group_Level(self):
                logging.info("Disabling Enable Account Lockout Security feature at group level")
                ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=admin-group", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"use_lockout_setting": False,"lockout_setting": {"enable_sequential_failed_login_attempts_lockout": False,"failed_lockout_duration": 5,"never_unlock_user": False,"sequential_attempts": 5}}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(5)
		print("Test Case 25 Execution Completed")

	@pytest.mark.run(order=26)
        def test_026_Validate_Disabled_Enable_Account_Lockout_Security_feature_Group_Level(self):
                logging.info("Validate Disabled Enable Account Lockout Security feature at group level")
                ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=admin-group", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=lockout_setting", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                assert re.search(r'"enable_sequential_failed_login_attempts_lockout": false',response)
                sleep(5)
                print("Test Case 26 Execution Completed")

        @pytest.mark.run(order=27)
        def test_027_Validate_Login_Transaction_in_Infoblox_Log(self):
                logging.info("Validate Login Transaction in Infoblox_Log")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                ref =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                print(ref)
                sleep(10)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                check=commands.getoutput(" grep -cw \".*Read Only txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox*")
                check_1=commands.getoutput(" grep -cw \".*Read Write txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox*")
                print(check,type(check),check_1,type(check_1))
                if ((int(check)==0) and (int(check_1)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 27 Execution Completed")

	@pytest.mark.run(order=28)
        def test_028_Disabling_Super_User_Access_for_Admin_Group_Negative(self):
                logging.info("Disabling Super_User Access for Admin_Group")
	        ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=admin-group", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"superuser": False}
		response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
		response=str(response)
		assert re.search(r'"text": "You cannot demote your own group: admin-group"',response)
                sleep(5)
		print("Test Case 28 Execution Completed")		

	@pytest.mark.run(order=29)
        def test_029_Creating_Non_Super_User_Group(self):
                logging.info("Creating Non Super User Group")
                data = {"name": "test1","use_disable_concurrent_login": True,"disable_concurrent_login": True}
		response = ib_NIOS.wapi_request('POST', object_type="admingroup", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
		assert re.search(r'test1',response)
		sleep(5)
		print("Test Case 29 Execution Completed")

	@pytest.mark.run(order=30)
        def test_030_Validating_Non_Super_User_Group(self):
                logging.info("Validating Non Super User Group")
	 	ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=test1", grid_vip=config.grid_vip)
		logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
		response = ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=superuser,disable_concurrent_login", grid_vip=config.grid_vip)
		print(response)
		if ('"disable_concurrent_login": true' in response) and ('"superuser": false' in response):
			assert True
		else:
			assert False	
		sleep(2)
		print("Test Case 30 Execution Completed")

	@pytest.mark.run(order=31)
        def test_031_Creating_Non_Super_User(self):
                logging.info("Creating Non Super User")
                data = {"admin_groups": ["test1"],"name": "test1","password":"infoblox"}
                response = ib_NIOS.wapi_request('POST', object_type="adminuser", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                assert re.search(r'test1',response)
                sleep(5)
		print("Test Case 31 Execution Completed")

	@pytest.mark.run(order=32)
        def test_032_Validate_Login_Transaction_of_Non_Super_User_in_Infoblox_Log(self):
                logging.info("Validate Login Transaction of non super user in Infoblox_Log")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                Curl_cmd="curl -k1 -u test1:infoblox -H Content-Type: application/json -X GET https://"+config.grid_vip+"/wapi/"+config.wapi_version+"/grid"
		print(Curl_cmd)
		child = pexpect.spawn(Curl_cmd)
		sleep(10)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                check=commands.getoutput(" grep -cw \".*Read Only txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox*")
                check_1=commands.getoutput(" grep -cw \".*Read Write txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox*")
                print(check,type(check),check_1,type(check_1))
                if ((int(check)==0) and (int(check_1)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 32 Execution Completed")

	@pytest.mark.run(order=33)
        def test_033_Enabling_Enable_Account_Lockout_Security_feature_Non_Super_User_Group(self):
                logging.info("Enabling Enable Account Lockout Security feature at group level")
                ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=test1", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"use_lockout_setting": True,"lockout_setting": {"enable_sequential_failed_login_attempts_lockout": True,"failed_lockout_duration": 5,"never_unlock_user": False,"sequential_attempts": 5}}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(5)
		print("Test Case 33 Execution Completed")

        @pytest.mark.run(order=34)
        def test_034_Validate_Enabled_Enable_Account_Lockout_Security_feature_Non_Super_User_Group(self):
                logging.info("Validate Enabled Enable Account Lockout Security feature at group level")
                ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=test1", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=lockout_setting", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                assert re.search(r'"enable_sequential_failed_login_attempts_lockout": true',response)
                sleep(5)
                print("Test Case 34 Execution Completed")

	@pytest.mark.run(order=35)
        def test_035_Validate_Login_Transaction_of_Non_Super_User_in_Infoblox_Log(self):
                logging.info("Validate Login Transaction of non super user in Infoblox_Log")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                Curl_cmd="curl -k1 -u test1:infoblox -H Content-Type: application/json -X GET https://"+config.grid_vip+"/wapi/"+config.wapi_version+"/grid"
                print(Curl_cmd)
                child = pexpect.spawn(Curl_cmd)
                sleep(10)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                check=commands.getoutput(" grep -cw \".*Read Only txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox*")
                check_1=commands.getoutput(" grep -cw \".*Read Write txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox*")
                print(check,type(check),check_1,type(check_1))
                if ((int(check)==0) and (int(check_1)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 35 Execution Completed")

	@pytest.mark.run(order=36)
        def test_036_Disabling_Disable_Concurrent_Login_Security_feature_Non_Super_User_Group(self):
                logging.info("Disabling Disable Concurrent Login Security feature at Non Super User group")
                ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=test1", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"use_disable_concurrent_login": True,"disable_concurrent_login": True}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(5)
		print("Test Case 36 Execution Completed")

        @pytest.mark.run(order=37)
        def test_037_Validate_Disabled_Disable_Concurrent_Login_Security_feature_Non_Super_User_Group(self):
                logging.info("Validate Disabled Disable Concurrent Login Security feature at Non Super user group")
                ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=test1", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=disable_concurrent_login", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                assert re.search(r'"disable_concurrent_login": false',response)
                sleep(5)
                print("Test Case 37 Execution Completed")

	@pytest.mark.run(order=38)
        def test_038_Validate_Login_Transaction_of_Non_Super_User_in_Infoblox_Log(self):
                logging.info("Validate Login Transaction of non super user in Infoblox_Log")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                Curl_cmd="curl -k1 -u test1:infoblox -H Content-Type: application/json -X GET https://"+config.grid_vip+"/wapi/"+config.wapi_version+"/grid"
                print(Curl_cmd)
                child = pexpect.spawn(Curl_cmd)
                sleep(10)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                check=commands.getoutput(" grep -cw \".*Read Only txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox*")
                check_1=commands.getoutput(" grep -cw \".*Read Write txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox*")
                print(check,type(check),check_1,type(check_1))
                if ((int(check)==0) and (int(check_1)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 38 Execution Completed")

	@pytest.mark.run(order=39)
        def test_039_Disabling_Enable_Account_Lockout_Security_feature_Non_Super_User_Group(self):
                logging.info("Disabling Enable Account Lockout Security feature at group level")
                ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=test1", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"use_lockout_setting": True,"lockout_setting": {"enable_sequential_failed_login_attempts_lockout": False,"failed_lockout_duration": 5,"never_unlock_user": False,"sequential_attempts": 5}}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(5)
		print("Test Case 39 Execution Completed")

        @pytest.mark.run(order=40)
        def test_040_Validate_Disabled_Enable_Account_Lockout_Security_feature_Non_Super_User_Group(self):
                logging.info("Validate Disabled Enable Account Lockout Security feature at group level")
                ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=test1", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=lockout_setting", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                assert re.search(r'"enable_sequential_failed_login_attempts_lockout": false',response)
                sleep(5)
                print("Test Case 40 Execution Completed")

	@pytest.mark.run(order=41)
        def test_041_Validate_Login_Transaction_of_Non_Super_User_in_Infoblox_Log(self):
                logging.info("Validate Login Transaction of non super user in Infoblox_Log")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                Curl_cmd="curl -k1 -u test1:infoblox -H Content-Type: application/json -X GET https://"+config.grid_vip+"/wapi/"+config.wapi_version+"/grid"
                print(Curl_cmd)
                child = pexpect.spawn(Curl_cmd)
                sleep(10)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                check=commands.getoutput(" grep -cw \".*Read Only txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox*")
                check_1=commands.getoutput(" grep -cw \".*Read Write txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox*")
                print(check,type(check),check_1,type(check_1))
                if ((int(check)==0) and (int(check_1)==0)):
                    assert True
                else:
                    assert False
		sleep(15)
                print("Test Case 41 Execution Completed")
	
	#Validating the transaction logs after enabling Debug
	@pytest.mark.run(order=42)
        def test_042_Enabling_Debug_Logs_To_Capture_Transaction_Logs(self):
                logging.info("Enabling Debug Logs to Capture Transaction Logs")
		child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
            	child.logfile=sys.stdout
		sleep(10)
		child.expect('#')
            	child.sendline('touch /infoblox/var/debug')
		child.expect('#')
                child.sendline('touch /infoblox/var/debug_nice')
		child.expect('#')
                child.sendline('/infoblox/rc restart')
		sleep(200)
		child.expect('#')
		child.close()
		print("Test Case 42 Execution Completed")
	
        @pytest.mark.run(order=43)
        def test_043_Validate_Default_Login_Transaction_in_Infoblox_Log(self):
                logging.info("Validate_Default_Login_Transaction_in_Infoblox_Log")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                ref =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                print(ref)
                sleep(10)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                check=commands.getoutput(" grep -cw \".*Read Only txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                check_1=commands.getoutput(" grep -cw \".*Read Write txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(check,check_1,type(check),type(check_1))
                if ((int(check)!=0) and (int(check_1)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 43 Execution Completed")

        @pytest.mark.run(order=44)
        def test_044_Enabling_Disable_Concurrent_Login_Security_feature(self):
                logging.info("Enabling Disable Concurrent Login Security feature")
                ref =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
		data = {"security_setting": {"disable_concurrent_login": True}}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(5)
		print("Test Case 44 Execution Completed")

        @pytest.mark.run(order=45)
        def test_045_Validate_Enabled_Disable_Concurrent_Login_Security_feature(self):
                logging.info("Validate Enabled Disable Concurrent Login Security feature")
                response =  ib_NIOS.wapi_request('GET', object_type="grid?_return_fields=security_setting", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                assert re.search(r'"disable_concurrent_login": true',response)
                sleep(5)
                print("Test Case 45 Execution Completed")

        @pytest.mark.run(order=46)
        def test_046_Validate_Login_Transaction_in_Infoblox_Log(self):
                logging.info("Validate Login Transaction in Infoblox_Log")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                ref =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                print(ref)
                sleep(10)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                check=commands.getoutput(" grep -cw \".*Read Only txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                check_1=commands.getoutput(" grep -cw \".*Read Write txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(check,check_1,type(check),type(check_1))
                if ((int(check)==0) and (int(check_1)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 46 Execution Completed")

        @pytest.mark.run(order=47)
        def test_047_Enabling_Enable_Account_Lockout_Security_feature(self):
                logging.info("Enabling Enable Account Lockout Security feature")
                ref =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"lockout_setting": {"enable_sequential_failed_login_attempts_lockout": True,"failed_lockout_duration": 5,"never_unlock_user": False,"sequential_attempts": 5}}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(5)
		print("Test Case 47 Execution Completed")
	
        @pytest.mark.run(order=48)
        def test_048_Validate_Enabled_Enable_Account_Lockout_Security_feature(self):
                logging.info("Validate Enabled Enable Account Lockout Security feature")
                response =  ib_NIOS.wapi_request('GET', object_type="grid?_return_fields=lockout_setting", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                assert re.search(r'"enable_sequential_failed_login_attempts_lockout": true',response)
                sleep(5)
                print("Test Case 48 Execution Completed")

        @pytest.mark.run(order=49)
        def test_049_Validate_Login_Transactions_in_Infoblox_Log(self):
                logging.info("Validate Login Transaction in Infoblox_Log")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                ref =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                print(ref)
                sleep(10)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                check=commands.getoutput(" grep -cw \".*Read Only txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                check_1=commands.getoutput(" grep -cw \".*Read Write txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                if ((int(check)==0) and (int(check_1)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 49 Execution Completed")

        @pytest.mark.run(order=50)
        def test_050_Disabling_Disable_Concurrent_Login_Security_feature(self):
                logging.info("Disabling Disable Concurrent Login Security feature")
                ref =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
		data = {"security_setting": {"disable_concurrent_login": False}}
		response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(5)
		print("Test Case 50 Execution Completed")

        @pytest.mark.run(order=51)
        def test_051_Validate_Disabled_Disable_Concurrent_Login_Security_feature(self):
                logging.info("Validate Disabled Disable Concurrent Login Security feature")
                response =  ib_NIOS.wapi_request('GET', object_type="grid?_return_fields=security_setting", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                assert re.search(r'"disable_concurrent_login": false',response)
                sleep(5)
                print("Test Case 51 Execution Completed")

        @pytest.mark.run(order=52)
        def test_052_Validate_Login_Transaction_in_Infoblox_Log(self):
                logging.info("Validate Login Transaction in Infoblox_Log")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                ref =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                print(ref)
                sleep(10)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                check=commands.getoutput(" grep -cw \".*Read Only txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                check_1=commands.getoutput(" grep -cw \".*Read Write txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                if ((int(check)!=0) and (int(check_1)!=1)):
                    assert True
                else:
                    assert False
                print("Test Case 52 Execution Completed")

        @pytest.mark.run(order=53)
        def test_053_Disabling_Disable_Account_Lockout_Security_feature(self):
                logging.info("Disabling Disable Account Lockout Security feature")
                ref =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"lockout_setting": {"enable_sequential_failed_login_attempts_lockout": False,"failed_lockout_duration": 5,"never_unlock_user": False,"sequential_attempts": 5}}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(5)
		print("Test Case 53 Execution Completed")

        @pytest.mark.run(order=54)
        def test_054_Validate_Disabled_Disable_Account_Lockout_Security_feature(self):
                logging.info("Validate Disabled Disable Account Lockout Security feature")
                response =  ib_NIOS.wapi_request('GET', object_type="grid?_return_fields=lockout_setting", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                assert re.search(r'"enable_sequential_failed_login_attempts_lockout": false',response)
                sleep(5)
                print("Test Case 54 Execution Completed")

        @pytest.mark.run(order=55)
        def test_055_Validate_Login_Transactions_in_Infoblox_Log(self):
                logging.info("Validate Login Transaction in Infoblox_Log")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                ref =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                print(ref)
                sleep(10)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                check=commands.getoutput(" grep -cw \".*Read Only txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                check_1=commands.getoutput(" grep -cw \".*Read Write txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                if ((int(check)!=1) and (int(check_1)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 55 Execution Completed")
	
        @pytest.mark.run(order=56)
        def test_056_Enabling_Disable_Concurrent_Login_Security_feature_Group_Level(self):
                logging.info("Enabling Disable Concurrent Login Security feature at group level")
                ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=admin-group", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"use_disable_concurrent_login": True,"disable_concurrent_login": True}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(5)
		print("Test Case 56 Execution Completed")

        @pytest.mark.run(order=57)
        def test_057_Validate_Enabled_Disable_Concurrent_Login_Security_feature_Group_Level(self):
                logging.info("Validate Enabled Disable Concurrent Login Security feature at group level")
                ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=admin-group", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=disable_concurrent_login", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                assert re.search(r'"disable_concurrent_login": true',response)
                sleep(5)
                print("Test Case 57 Execution Completed")
	
        @pytest.mark.run(order=58)
        def test_058_Validate_Login_Transaction_in_Infoblox_Log(self):
                logging.info("Validate Login_Transaction_in_Infoblox_Log")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                ref =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                print(ref)
                sleep(10)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                check=commands.getoutput(" grep -cw \".*Read Only txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                check_1=commands.getoutput(" grep -cw \".*Read Write txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(check,type(check),check_1,type(check_1))
                if ((int(check)==0) and (int(check_1)!=1)):
                    assert True
                else:
                    assert False
                print("Test Case 58 Execution Completed")

        @pytest.mark.run(order=59)
        def test_059_Enabling_Enable_Account_Lockout_Security_feature_Group_Level(self):
                logging.info("Enabling Enable Account Lockout Security feature at group level")
                ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=admin-group", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"use_lockout_setting": True,"lockout_setting": {"enable_sequential_failed_login_attempts_lockout": True,"failed_lockout_duration": 5,"never_unlock_user": False,"sequential_attempts": 5}}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(5)
		print("Test Case 59 Execution Completed")

        @pytest.mark.run(order=60)
        def test_060_Validate_Enabled_Enable_Account_Lockout_Security_feature_Group_Level(self):
                logging.info("Validate Enabled Enable Account Lockout Security feature at group level")
                ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=admin-group", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=lockout_setting", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                assert re.search(r'"enable_sequential_failed_login_attempts_lockout": true',response)
                sleep(5)
                print("Test Case 60 Execution Completed")

        @pytest.mark.run(order=61)
        def test_061_Validate_Login_Transaction_in_Infoblox_Log(self):
                logging.info("Validate Login Transaction in Infoblox_Log")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                ref =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                print(ref)
                sleep(10)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                check=commands.getoutput(" grep -cw \".*Read Only txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox*")
                check_1=commands.getoutput(" grep -cw \".*Read Write txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox*")
                print(check,type(check),check_1,type(check_1))
                if ((int(check)==0) and (int(check_1)!=1)):
                    assert True
                else:
                    assert False
                print("Test Case 61 Execution Completed")

        @pytest.mark.run(order=62)
        def test_062_Disabling_Disable_Concurrent_Login_Security_feature_Group_Level(self):
                logging.info("Disabling Disable Concurrent Login Security feature at group level")
                ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=admin-group", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"use_disable_concurrent_login": True,"disable_concurrent_login": True}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(5)
		print("Test Case 62 Execution Completed")

        @pytest.mark.run(order=63)
        def test_063_Validate_Disabled_Disable_Concurrent_Login_Security_feature_Group_Level(self):
                logging.info("Validate Disabled Disable Concurrent Login Security feature at group level")
                ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=admin-group", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=disable_concurrent_login", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                assert re.search(r'"disable_concurrent_login": false',response)
                sleep(5)
                print("Test Case 63 Execution Completed")

        @pytest.mark.run(order=64)
        def test_064_Validate_Login_Transaction_in_Infoblox_Log(self):
                logging.info("Validate Login Transaction in Infoblox_Log")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                ref =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                print(ref)
                sleep(10)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                check=commands.getoutput(" grep -cw \".*Read Only txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                check_1=commands.getoutput(" grep -cw \".*Read Write txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(check,type(check),check_1,type(check_1))
                if ((int(check)==0) and (int(check_1)!=1)):
                    assert True
                else:
                    assert False
                print("Test Case 64 Execution Completed")

        @pytest.mark.run(order=65)
        def test_065_Disabling_Enable_Account_Lockout_Security_feature_Group_Level(self):
                logging.info("Disabling Enable Account Lockout Security feature at group level")
                ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=admin-group", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"use_lockout_setting": False,"lockout_setting": {"enable_sequential_failed_login_attempts_lockout": False,"failed_lockout_duration": 5,"never_unlock_user": False,"sequential_attempts": 5}}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(5)
		print("Test Case 65 Execution Completed")

        @pytest.mark.run(order=66)
        def test_066_Validate_Disabled_Enable_Account_Lockout_Security_feature_Group_Level(self):
                logging.info("Validate Disabled Enable Account Lockout Security feature at group level")
                ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=admin-group", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=lockout_setting", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                assert re.search(r'"enable_sequential_failed_login_attempts_lockout": false',response)
                sleep(5)
                print("Test Case 66 Execution Completed")

        @pytest.mark.run(order=67)
        def test_067_Validate_Login_Transaction_in_Infoblox_Log(self):
                logging.info("Validate Login Transaction in Infoblox_Log")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                ref =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                print(ref)
                sleep(10)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                check=commands.getoutput(" grep -cw \".*Read Only txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox*")
                check_1=commands.getoutput(" grep -cw \".*Read Write txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox*")
                print(check,type(check),check_1,type(check_1))
                if ((int(check)!=1) and (int(check_1)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 67 Execution Completed")

        @pytest.mark.run(order=68)
        def test_068_Disabling_Super_User_Access_for_Admin_Group_Negative(self):
                logging.info("Disabling Super_User Access for Admin_Group")
                ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=admin-group", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"superuser": False}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                response=str(response)
                assert re.search(r'"text": "You cannot demote your own group: admin-group"',response)
                sleep(5)
		print("Test Case 68 Execution Completed")

        @pytest.mark.run(order=69)
        def test_069_Enabling_Disable_Concurrent_Login_in_Non_Super_User_Group(self):
                logging.info("Creating Non Super User Group")
		ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=test1", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"use_disable_concurrent_login": True,"disable_concurrent_login": True}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1, fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                assert re.search(r'test1',response)
                sleep(5)
		print("Test Case 69 Execution Completed")

        @pytest.mark.run(order=70)
        def test_070_Validating_Non_Super_User_Group(self):
                logging.info("Validating Non Super User Group")
                ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=test1", grid_vip=config.grid_vip)
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response = ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=superuser,disable_concurrent_login", grid_vip=config.grid_vip)
                print(response)
                if ('"disable_concurrent_login": true' in response) and ('"superuser": false' in response):
                        assert True
                else:
                        assert False
                sleep(2)
		print("Test Case 70 Execution Completed")

        @pytest.mark.run(order=71)
        def test_071_Validate_Login_Transaction_of_Non_Super_User_in_Infoblox_Log(self):
                logging.info("Validate Login Transaction of non super user in Infoblox_Log")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                Curl_cmd="curl -k1 -u test1:infoblox -H Content-Type: application/json -X GET https://"+config.grid_vip+"/wapi/"+config.wapi_version+"/grid"
                print(Curl_cmd)
                child = pexpect.spawn(Curl_cmd)
                sleep(10)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                check=commands.getoutput(" grep -cw \".*Read Only txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox*")
                check_1=commands.getoutput(" grep -cw \".*Read Write txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox*")
                print(check,type(check),check_1,type(check_1))
                if ((int(check)==0) and (int(check_1)!=1)):
                    assert True
                else:
                    assert False
                print("Test Case 71 Execution Completed")

        @pytest.mark.run(order=72)
        def test_072_Enabling_Enable_Account_Lockout_Security_feature_Non_Super_User_Group(self):
                logging.info("Enabling Enable Account Lockout Security feature at group level")
                ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=test1", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"use_lockout_setting": True,"lockout_setting": {"enable_sequential_failed_login_attempts_lockout": True,"failed_lockout_duration": 5,"never_unlock_user": False,"sequential_attempts": 5}}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(5)
		print("Test Case 72 Execution Completed")

        @pytest.mark.run(order=73)
        def test_073_Validate_Enabled_Enable_Account_Lockout_Security_feature_Non_Super_User_Group(self):
                logging.info("Validate Enabled Enable Account Lockout Security feature at group level")
                ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=test1", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=lockout_setting", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                assert re.search(r'"enable_sequential_failed_login_attempts_lockout": true',response)
                sleep(5)
                print("Test Case 73 Execution Completed")

        @pytest.mark.run(order=74)
        def test_074_Validate_Login_Transaction_of_Non_Super_User_in_Infoblox_Log(self):
                logging.info("Validate Login Transaction of non super user in Infoblox_Log")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                Curl_cmd="curl -k1 -u test1:infoblox -H Content-Type: application/json -X GET https://"+config.grid_vip+"/wapi/"+config.wapi_version+"/grid"
                print(Curl_cmd)
                child = pexpect.spawn(Curl_cmd)
                sleep(10)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                check=commands.getoutput(" grep -cw \".*Read Only txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox*")
                check_1=commands.getoutput(" grep -cw \".*Read Write txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox*")
                print(check,type(check),check_1,type(check_1))
                if ((int(check)==0) and (int(check_1)!=1)):
                    assert True
                else:
                    assert False
                print("Test Case 74 Execution Completed")

        @pytest.mark.run(order=75)
        def test_075_Disabling_Disable_Concurrent_Login_Security_feature_Non_Super_User_Group(self):
                logging.info("Disabling Disable Concurrent Login Security feature at Non Super User group")
                ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=test1", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"use_disable_concurrent_login": False,"disable_concurrent_login": False}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(5)
		print("Test Case 75 Execution Completed")

        @pytest.mark.run(order=76)
        def test_076_Validate_Disabled_Disable_Concurrent_Login_Security_feature_Non_Super_User_Group(self):
                logging.info("Validate Disabled Disable Concurrent Login Security feature at Non Super user group")
                ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=test1", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=disable_concurrent_login", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                assert re.search(r'"disable_concurrent_login": false',response)
                sleep(5)
                print("Test Case 76 Execution Completed")

        @pytest.mark.run(order=77)
        def test_077_Validate_Login_Transaction_of_Non_Super_User_in_Infoblox_Log(self):
                logging.info("Validate Login Transaction of non super user in Infoblox_Log")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                Curl_cmd="curl -k1 -u test1:infoblox -H Content-Type: application/json -X GET https://"+config.grid_vip+"/wapi/"+config.wapi_version+"/grid"
                print(Curl_cmd)
                child = pexpect.spawn(Curl_cmd)
                sleep(10)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                check=commands.getoutput(" grep -cw \".*Read Only txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox*")
                check_1=commands.getoutput(" grep -cw \".*Read Write txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox*")
                print(check,type(check),check_1,type(check_1))
                if ((int(check)==0) and (int(check_1)!=1)):
                    assert True
                else:
                    assert False
                print("Test Case 77 Execution Completed")

        @pytest.mark.run(order=78)
        def test_078_Disabling_Enable_Account_Lockout_Security_feature_Non_Super_User_Group(self):
                logging.info("Disabling Enable Account Lockout Security feature at group level")
                ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=test1", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"use_lockout_setting": False,"lockout_setting": {"enable_sequential_failed_login_attempts_lockout": False,"failed_lockout_duration": 5,"never_unlock_user": False,"sequential_attempts": 5}}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(5)
		print("Test Case 78 Execution Completed")

        @pytest.mark.run(order=79)
        def test_079_Validate_Disabled_Enable_Account_Lockout_Security_feature_Non_Super_User_Group(self):
                logging.info("Validate Disabled Enable Account Lockout Security feature at group level")
                ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=test1", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=lockout_setting", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                assert re.search(r'"enable_sequential_failed_login_attempts_lockout": false',response)
                sleep(5)
                print("Test Case 79 Execution Completed")

        @pytest.mark.run(order=80)
        def test_080_Validate_Login_Transaction_of_Non_Super_User_in_Infoblox_Log(self):
                logging.info("Validate Login Transaction of non super user in Infoblox_Log")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                Curl_cmd="curl -k1 -u test1:infoblox -H Content-Type: application/json -X GET https://"+config.grid_vip+"/wapi/"+config.wapi_version+"/grid"
                print(Curl_cmd)
                child = pexpect.spawn(Curl_cmd)
                sleep(10)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                check=commands.getoutput(" grep -cw \".*Read Only txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox*")
                check_1=commands.getoutput(" grep -cw \".*Read Write txns\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox*")
                print(check,type(check),check_1,type(check_1))
                if ((int(check)!=1) and (int(check_1)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 80 Execution Completed")



        @pytest.mark.run(order=81)       
	def test_081_Disabling_Disable_Concurrent_Login_Security_feature(self):
                logging.info("Disabling Disable Concurrent Login Security feature")
                ref =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"security_setting": {"disable_concurrent_login": False}}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(5)
                print("Test Case 81 Execution Completed")


        @pytest.mark.run(order=82)
        def test_082_Disabling_Disable_Concurrent_Login_Security_feature_Group_Level(self):
                logging.info("Disabling Disable Concurrent Login Security feature at group level")
                ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=admin-group", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"use_disable_concurrent_login": False,"disable_concurrent_login": False}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(5)
                print("Test Case 82 Execution Completed")



        @pytest.mark.run(order=83)
        def test_083_Disabling_Disable_Concurrent_Login_Security_feature_Group_Level(self):
                logging.info("Disabling Disable Concurrent Login Security feature at group level")
                ref =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=admin-group", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"use_disable_concurrent_login": False,"disable_concurrent_login": False}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(5)
                print("Test Case 62 Execution Completed")


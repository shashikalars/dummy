__author__ = "Arun J R"
__email__  = "aramaiah@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Stan alone Grid Master with Grid Member                               #
#  2. Stand alone Grid Master                                               #
#  3. Licenses : DNS, Grid, NIOS(IB_1415)                                   #
#############################################################################


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
import shlex
import json
import time
from time import sleep
import commands
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util
import ib_utils.log_capture as log_capture
from  ib_utils.log_capture import log_action as log
from  ib_utils.log_validation import log_validation as logv
import pexpect
import paramiko
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="rfe_11096.log" ,level=logging.INFO,filemode='w')




def print_and_log(arg=""):
	print(arg)
	logging.info(arg)


class Rfe_11096(unittest.TestCase):



	@pytest.mark.run(order=1)
	def test_001_enable_ntp_on_grid_master_2(self):
		print_and_log("Enabling ntp on grid master 2")
		request = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid2_vip)
		request = json.loads(request)
		print_and_log(request)
		request_ref = request[0]['_ref']
		print_and_log(request_ref)
		data = {"ntp_setting": {"enable_ntp": True}}
		res = ib_NIOS.wapi_request('PUT', object_type=request_ref, fields=json.dumps(data), grid_vip=config.grid2_vip)
		print_and_log(res)
		assert re.search(r'member', res)
		print_and_log("TestCase 1 executed successfully")


	@pytest.mark.run(order=2)
	def test_002_validate_if_ntp_enabled_on_grid_master_2(self):
		print_and_log("Validating if NTP ENABLED on grid master 2")
		request = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid2_vip)
		request = json.loads(request)
		print_and_log(request)
		request_ref = request[0]['_ref']
		print_and_log(request_ref)
		res = ib_NIOS.wapi_request('GET', object_type=request_ref, params='?_return_fields=ntp_setting', grid_vip=config.grid2_vip)
		res = json.loads(res)
		res_enable = res['ntp_setting']['enable_ntp']
		print_and_log(res_enable)
		if res_enable == True:
			print_and_log("NTP is enabled")
			assert True
		else:
			print_and_log("NTP is not enabled")
			assert False
		sleep(120)
		print_and_log("TestCase 2 executed successfully")



	@pytest.mark.run(order=3)
	def test_003_Exeute_the_cli_command_show_ntp_on_grid_master_2(self):
		print_and_log("Exeute the cli command show ntp on grid master 2")
		args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+str(config.grid2_vip)
		args=shlex.split(args)
		child = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		child.stdin.write("show ntp\n")
		result = child.communicate()
		print_and_log(result)
		result = str(result)
		if "*127.127.1.1" in result or "127.127.1.1" in result:
			print_and_log(" Grid is synced with local NTP server")
			assert True
		else:
			print_and_log(" Grid is not synced with local NTP server")
			assert False
		print_and_log("TestCase 3 Exeuted successfully")



	@pytest.mark.run(order=4)
	def test_004_Add_the_External_ntp_server_to_grid_master_2(self):
		print_and_log("Add the External ntp server to grid master 2")
		request = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid2_vip)
		request = json.loads(request)
		res_ref = request[0]['_ref']
		print_and_log(res_ref)
		data = {"ntp_setting": {"enable_ntp": True, "ntp_servers": [{"address": config.ntp_server, "burst": True, "enable_authentication": False, "iburst": True, "preferred": False}]}}
		request1 = ib_NIOS.wapi_request('PUT', object_type=res_ref, fields=json.dumps(data), grid_vip=config.grid2_vip)
		print_and_log(request1)
		logging.info("******** Restart the NTP service *********")
                response = ib_NIOS.wapi_request('GET',object_type='grid', grid_vip=config.grid2_vip)
                reference = json.loads(response)
                ref = reference[0]['_ref']
                data = {"member_order" : "SIMULTANEOUSLY", "restart_option": "FORCE_RESTART", "service_option": "ALL"}
                response1 = ib_NIOS.wapi_request('POST', object_type=ref + '?_function=restartservices',fields=json.dumps(data))
                if type(response1) == tuple:
                    if response1 == 400 or response1 == 401 or response1 == 402:
                        print("Error while restarting the NTP service")
                        assert False
                else:
                    print("NTP restarted successfully")
                    assert True
                #sleep(30)
                sleep(90)
		print_and_log("TestCase 4 executed successfully")



	@pytest.mark.run(order=5)
	def test_005_Exeute_the_cli_command_show_ntp_and_verify_if_grid_master_2_is_synced_with_external_server(self):
		print_and_log("Exeute the cli command show ntp and verify if grid master 2 is synced with external server")
		args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+str(config.grid2_vip)
		args=shlex.split(args)
		child = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		child.stdin.write("show ntp\n")
		result = child.communicate()
		print_and_log(result)
		result = str(result)
		if "*"+config.ntp_server in result:
			print_and_log(" Grid is synced with local NTP server")
			assert True
		else:
			print_and_log(" Grid is not synced with local NTP server")
			assert False
		print_and_log("TestCase 5 Exeuted successfully")




	@pytest.mark.run(order=6)
	def test_006_Remove_the_External_ntp_server_from_grid_master_2(self):
		print_and_log("Remove the External ntp server to grid master 2")
		request = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid2_vip)
		request = json.loads(request)
		res_ref = request[0]['_ref']
		print_and_log(res_ref)
		data = {"ntp_setting": {"enable_ntp": False, "ntp_servers": []}}
		request1 = ib_NIOS.wapi_request('PUT', object_type=res_ref, fields=json.dumps(data), grid_vip=config.grid2_vip)
		print_and_log(request1)
		print_and_log("TestCase 6 Exeuted successfully")





	@pytest.mark.run(order=7)
	def test_007_enable_ntp_on_master_and_members(self):
		print_and_log("Enabling NTP on master and members")
		request = ib_NIOS.wapi_request('GET', object_type="member")
		request = json.loads(request)
		print_and_log(request)
		for i in request:
			request_ref = i['_ref']
			print_and_log(request_ref)
			data = {"ntp_setting": {"enable_ntp": True}}
			res = ib_NIOS.wapi_request('PUT', object_type=request_ref, fields=json.dumps(data))
			print_and_log(res)
			assert re.search(r'member', res)
		print_and_log("TestCase 7 executed successfully")


	@pytest.mark.run(order=8)
	def test_008_validate_if_ntp_enabled_on_master_and_members(self):
		print_and_log("Validating if NTP ENABLED on master and members")
		request = ib_NIOS.wapi_request('GET', object_type="member")
		request = json.loads(request)
		print_and_log(request)
		for i in request:
			request_ref = i['_ref']
			print_and_log(request_ref)
			res = ib_NIOS.wapi_request('GET', object_type=request_ref, params='?_return_fields=ntp_setting')
			res = json.loads(res)
			res_enable = res['ntp_setting']['enable_ntp']
			print_and_log(res_enable)
			if res_enable == True:
				print_and_log("NTP is enabled")
				assert True
			else:
				print_and_log("NTP is not enabled")
				assert False
		print_and_log("TestCase 8 executed successfully")


	@pytest.mark.run(order=9)
	def test_009_validate_the_default_stratum_option_is_enabled_in_orphan_mode_of_grid_master(self):
		print_and_log("Validate the default stratum option is enabled in orphan mode of grid master")
		request = ib_NIOS.wapi_request('GET', object_type="grid")
		request = json.loads(request)
		res_ref = request[0]['_ref']
		print_and_log(res_ref)
		request1 = ib_NIOS.wapi_request('GET', object_type=res_ref, params='?_return_fields=ntp_setting')
		request1 = json.loads(request1)
		print_and_log(request1)
		gm_use_default_stratum = request1['ntp_setting']['use_default_stratum']
		gm_local_ntp_stratum = request1['ntp_setting']['gm_local_ntp_stratum']
		print_and_log(gm_use_default_stratum)
		if gm_use_default_stratum == True and int(gm_local_ntp_stratum) == 13:
			print_and_log("Default stratum option is enabled")
			assert True
		else:
			print_and_log("Default stratum option is not enabled")
			assert False
		print_and_log("TestCase 9 executed successfully")


	@pytest.mark.run(order=10)
	def test_010_validate_the_default_stratum_option_is_enabled_in_orphan_mode_of_grid_member(self):
		print_and_log("Validate the default stratum option is enabled in orphan mode of grid member")
		request = ib_NIOS.wapi_request('GET', object_type="member")
		request = json.loads(request)
		res_ref = request[1]['_ref']
		print_and_log(res_ref)
		request1 = ib_NIOS.wapi_request('GET', object_type=res_ref, params='?_return_fields=ntp_setting')
		request1 = json.loads(request1)
		print_and_log(request1)
		gm_use_default_stratum = request1['ntp_setting']['use_default_stratum']
		local_ntp_stratum = request1['ntp_setting']['local_ntp_stratum']
		print_and_log(gm_use_default_stratum)
		if gm_use_default_stratum == True and int(local_ntp_stratum) == 15:
			print_and_log("Default stratum option is enabled in Grid member")
			assert True
		else:
			print_and_log("Default stratum option is not enabled in Grid member")
			assert False
		print_and_log("TestCase 10 executed successfully")


	@pytest.mark.run(order=11)
	def test_011_Configure_other_values_to_orphan_mode_other_than_default_values(self):
		print_and_log("Configure other values to orphan mode other than default values")
		print_and_log("\nChecking for NTPD restart")
		log("start", "/infoblox/var/infoblox.log", config.grid_vip)
		log("start", "/infoblox/var/infoblox.log", config.grid_member1_vip)
		request = ib_NIOS.wapi_request('GET', object_type="grid")
		request = json.loads(request)
		res_ref = request[0]['_ref']
		print_and_log(res_ref)
		data = {"ntp_setting": {"gm_local_ntp_stratum": 8, "local_ntp_stratum": 9, "use_default_stratum": False}}
		request1 = ib_NIOS.wapi_request('PUT', object_type=res_ref, fields=json.dumps(data))
		print_and_log(request1)
		assert re.search(r'grid', request1)
		sleep(120)
		print_and_log("TestCase 11 executed successfully")


	@pytest.mark.run(order=12)
	def test_012_Check_if_ntpd_process_is_restarted_in_grid_master(self):
		print_and_log("Check if ntpd process is restarted in grid master")
		LookFor="'Restarting ntpd due to conf file differences below'"
		log("stop","/infoblox/var/infoblox.log", config.grid_vip)
		logs=logv(LookFor,"/infoblox/var/infoblox.log", config.grid_vip)
		print_and_log("NTPD process is restarted successfully")
		print_and_log("TestCase 12 executed successfully")


	@pytest.mark.run(order=13)
	def test_013_Check_if_ntpd_process_is_restarted_in_grid_member(self):
		print_and_log("Check if ntpd process is restarted in grid member")
		LookFor="'Restarting ntpd due to conf file differences below'"
		log("stop","/infoblox/var/infoblox.log", config.grid_member1_vip)
		logs=logv(LookFor,"/infoblox/var/infoblox.log", config.grid_member1_vip)
		print_and_log("NTPD process is restarted successfully")
		print_and_log("TestCase 13 executed successfully")


	@pytest.mark.run(order=14)
	def test_014_validate_the_custom_values_present_in_orphan_mode(self):
		print_and_log("Validate the custom values present in orphan mode")
		global gm_local_ntp_value
		global local_ntp_value
		request = ib_NIOS.wapi_request('GET', object_type="grid")
		request = json.loads(request)
		res_ref = request[0]['_ref']
		print_and_log(res_ref)
		request1 = ib_NIOS.wapi_request('GET', object_type=res_ref, params='?_return_fields=ntp_setting')
		request1 = json.loads(request1)
		print_and_log(request1)
		gm_local_ntp_value = request1['ntp_setting']['gm_local_ntp_stratum']
		print_and_log(gm_local_ntp_value)
		local_ntp_value = request1['ntp_setting']['local_ntp_stratum']
		print_and_log(local_ntp_value)
		if int(gm_local_ntp_value) == 8 and int(local_ntp_value) == 9:
			print_and_log("Custom values are updated ")
			assert True
		else:
			print_and_log("Custom values are not updated")
			assert False
		print_and_log("TestCase 14 executed successfully")



	@pytest.mark.run(order=15)
	def test_015_validate_the_custom_value_present_in_master_ntp_conf_file(self):
		print_and_log("Validate the custom values present in master ntp.conf file")
		#ip = [config.grid_master_vip, config.grid_member1_vip]
		global gm_local_ntp_value
		print("Logging in to device "+config.grid_master_vip)
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
		mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
		client.connect(config.grid_master_vip, username='root', pkey = mykey)
		stdin, stdout, stderr = client.exec_command('cat /tmpfs/ntp.conf')
		output = stdout.read()
		output = output.split("\n")
		print_and_log(output)
		match_line = "tos orphan "+str(gm_local_ntp_value)
		match_line2 = "fudge 127.127.1.1 stratum "+str(gm_local_ntp_value-1)
		print_and_log(match_line)
		if match_line in output and match_line2 in output:
			print_and_log("The custom value that is updated is seen in ntpd.conf file")
			assert True
		else:
			print_and_log("The custom value that is not updated in ntpd.conf file")
			assert False
		client.close()
		print_and_log("TestCase 15 executed successfully")


	@pytest.mark.run(order=16)
	def test_016_validate_the_custom_value_present_in_member_ntp_conf_file(self):
		print_and_log("Validate the custom values present in member ntp.conf file")
		#ip = [config.grid_master_vip, config.grid_member1_vip]
		global local_ntp_value
		print("Logging in to device "+config.grid_member1_vip)
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
		mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
		client.connect(config.grid_member1_vip, username='root', pkey = mykey)
		stdin, stdout, stderr = client.exec_command('cat /tmpfs/ntp.conf')
		output = stdout.read()
		output = output.split("\n")
		print_and_log(output)
		match_line = "tos orphan "+str(local_ntp_value)
		match_line2 = "fudge 127.127.1.1 stratum "+str(local_ntp_value-1)
		print_and_log(match_line)
		if match_line in output and match_line2 in output:
			print_and_log("The custom value that is updated is seen in ntpd.conf file")
			assert True
		else:
			print_and_log("The custom value that is not updated in ntpd.conf file")
			assert False
		client.close()
		print_and_log("TestCase 16 executed successfully")


	@pytest.mark.run(order=17)
	def test_017_Configure_invalid_values_to_orphan_mode(self):
		print_and_log("Configure invalid values to orphan mode")
		request = ib_NIOS.wapi_request('GET', object_type="grid")
		request = json.loads(request)
		res_ref = request[0]['_ref']
		print_and_log(res_ref)
		data = {"ntp_setting": {"gm_local_ntp_stratum": 18, "local_ntp_stratum": 18}}
		request1 = ib_NIOS.wapi_request('PUT', object_type=res_ref, fields=json.dumps(data))
		if type(request1) == tuple:
			out = request1[1]
			out = json.loads(out)
			print_and_log(out)
			error_message = out['text']
			expected_error_message = "' The NTP local source stratum value must be between 2 and 15. The specified Grid Manager stratum value is 18, member value is 18.'"
			if error_message in expected_error_message:
				print_and_log("Expected Error message is seen")
				assert True
			else:
				print_and_log("Expected Error message is not seen")
				assert False
		else:
			print_and_log(request1)
			print_and_log(" The Invalid values configured successfully")
			assert False
		print_and_log("TestCase 17 executed successfully")




	@pytest.mark.run(order=18)
	def test_018_Configure_higher_stratum_value_for_grid_master_and_expect_error(self):
		print_and_log("Configure higher stratum value for grid master and expect_error")
		request = ib_NIOS.wapi_request('GET', object_type="grid")
		request = json.loads(request)
		res_ref = request[0]['_ref']
		print_and_log(res_ref)
		data = {"ntp_setting": {"gm_local_ntp_stratum": 10, "local_ntp_stratum": 9}}
		request1 = ib_NIOS.wapi_request('PUT', object_type=res_ref, fields=json.dumps(data))
		if type(request1) == tuple:
			out = request1[1]
			out = json.loads(out)
			print_and_log(out)
			error_message = out['text']
			expected_error_message = "' NTP cluster local source stratum restriction: The Grid Manager stratum value must be less than the stratum value of any member. Specified Grid Manager stratum value is 10 and the member stratum value is 9.'"
			if error_message in expected_error_message:
				print_and_log("Expected Error message is seen")
				assert True
			else:
				print_and_log("Expected Error message is not seen")
				assert False
		else:
			print_and_log(request1)
			print_and_log(" The Invalid values configured successfully")
			assert False
		print_and_log("TestCase 18 executed successfully")



	@pytest.mark.run(order=19)
	def test_019_Configure_negative_stratum_value_for_grid_master_and_expect_error(self):
		print_and_log("Configure negative stratum value for grid master and expect_error")
		request = ib_NIOS.wapi_request('GET', object_type="grid")
		request = json.loads(request)
		res_ref = request[0]['_ref']
		print_and_log(res_ref)
		data = {"ntp_setting": {"gm_local_ntp_stratum": -3, "local_ntp_stratum": -5}}
		request1 = ib_NIOS.wapi_request('PUT', object_type=res_ref, fields=json.dumps(data))
		if type(request1) == tuple:
			out = request1[1]
			out = json.loads(out)
			print_and_log(out)
			error_message = out['text']
			expected_error_message = "' Invalid value for gm_local_ntp_stratum: -3: Invalid value, must be between 0 and 4294967295'"
			if error_message in expected_error_message:
				print_and_log("Expected Error message is seen")
				assert True
			else:
				print_and_log("Expected Error message is not seen")
				assert False
		else:
			print_and_log(request1)
			print_and_log(" The Invalid values configured successfully")
			assert False
		print_and_log("TestCase 19 executed successfully")	




	@pytest.mark.run(order=20)
	def test_020_Overide_the_member_stratum_values_from_grid_master(self):
		print_and_log("Overide the member stratum values from grid master")
		print_and_log("\nChecking for NTPD restart")
		log("start", "/infoblox/var/infoblox.log", config.grid_member1_vip)
		request = ib_NIOS.wapi_request('GET', object_type="member")
		request = json.loads(request)
		res_ref = request[1]['_ref']
		print_and_log(res_ref)
		#data = {"ntp_setting": {"local_ntp_stratum": 11, "use_local_ntp_stratum": True}}
		data = {"ntp_setting": {"local_ntp_stratum": 11, "use_local_ntp_stratum": True, "use_default_stratum": False}}
		request1 = ib_NIOS.wapi_request('PUT', object_type=res_ref, fields=json.dumps(data))
		request1 = json.loads(request1)
		print_and_log(request1)
		assert re.search(r'member', request1)
		sleep(60)
		print_and_log("TestCase 20 executed successfully")



	@pytest.mark.run(order=21)
	def test_021_Check_if_ntpd_process_is_restarted(self):
		print_and_log("Check if ntpd process is restarted")
		LookFor="'Restarting ntpd due to conf file differences below'"
		log("stop","/infoblox/var/infoblox.log", config.grid_member1_vip)
		logs=logv(LookFor,"/infoblox/var/infoblox.log", config.grid_member1_vip)
		print_and_log("NTPD process is restarted successfully")
		print_and_log("TestCase 21 executed successfully")


	@pytest.mark.run(order=22)
	def test_022_Validate_the_overided_local_ntp_stratum_value_in_grid_member(self):
		print_and_log("Validate the overided local ntp stratum value in grid member")
		global gm_local_ntp_stratum
		request = ib_NIOS.wapi_request('GET', object_type="member")
		request = json.loads(request)
		res_ref = request[1]['_ref']
		print_and_log(res_ref)
		request1 = ib_NIOS.wapi_request('GET', object_type=res_ref, params='?_return_fields=ntp_setting')
		request1 = json.loads(request1)
		print_and_log(request1)
		gm_local_ntp_stratum = request1['ntp_setting']['local_ntp_stratum']
		print_and_log(gm_local_ntp_stratum)
		use_local_ntp_stratum = request1['ntp_setting']['use_local_ntp_stratum']
		print_and_log(use_local_ntp_stratum)
		if int(gm_local_ntp_stratum) == 11 and use_local_ntp_stratum == True:
			print_and_log("Local ntp stratum values are overided successfully")
			assert True
		else:
			print_and_log("Local ntp stratum values are not overided")
			assert False
		print_and_log("TestCase 22 executed successfully")



	@pytest.mark.run(order=23)
	def test_023_validate_the_custom_value_present_in_member_ntp_conf_file(self):
		print_and_log("Validate the custom values present in member ntp.conf file")
		#ip = [config.grid_master_vip, config.grid_member1_vip]
		global gm_local_ntp_stratum
		print("Logging in to device "+ config.grid_member1_vip)
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
		mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
		client.connect(config.grid_member1_vip, username='root', pkey = mykey)
		stdin, stdout, stderr = client.exec_command('cat /tmpfs/ntp.conf')
		output = stdout.read()
		output = output.split("\n")
		print_and_log(output)
		match_line = "tos orphan "+str(gm_local_ntp_stratum)
		match_line2 = "fudge 127.127.1.1 stratum "+str(gm_local_ntp_stratum-1)
		print_and_log(match_line)
		print_and_log(match_line2)
		if match_line in output and match_line2 in output:
			print_and_log("The overided value "+str(gm_local_ntp_stratum) +" is seen in ntpd.conf file")
			assert True
		else:
			print_and_log("The overided value "+str(gm_local_ntp_stratum) +" is not seen in ntpd.conf file")
			assert False
		client.close()
		print_and_log("TestCase 23 executed successfully")




	@pytest.mark.run(order=24)
	def test_024_Revert_the_Grid_master_and_Grid_member_stratum_values_to_default_value_16_on_Grid_master_and_expect_error(self):
		print_and_log("Revert the Grid master and Grid member stratum values to default value 16 on Grid master and expect error")
		request = ib_NIOS.wapi_request('GET', object_type="grid")
		request = json.loads(request)
		res_ref = request[0]['_ref']
		print_and_log(res_ref)
		#data = {"ntp_setting": {"gm_local_ntp_stratum": 16, "local_ntp_stratum": 16}}
		data = {"ntp_setting": {"use_default_stratum": True}}
		request1 = ib_NIOS.wapi_request('PUT', object_type=res_ref, fields=json.dumps(data))
		if type(request1) == tuple:
			out = request1[1]
			out = json.loads(out)
			print_and_log(out)
			error_message = out['text']
			#expected_error_message = "'NTP cluster local source stratum restriction: The Grid Manager stratum value must be less than the value of any of its members. Specified Grid Manager stratum value is 12 and the lowest stratum value of a configured member is 11.'"
			expected_error_message = "'NTP cluster local source stratum restriction: The Grid Manager stratum value must be less than the value of any of its members. Specified Grid Manager stratum value is 13 and the lowest stratum value of a configured member is 11.'"
			if error_message in expected_error_message:
				print_and_log("Expected Error message is seen")
				assert True
			else:
				print_and_log("Expected Error message is not seen")
				assert False
		else:
			print_and_log(request1)
			print_and_log(" The Invalid values configured successfully")
			assert False
		print_and_log("TestCase 24 executed successfully")



	@pytest.mark.run(order=25)
	def test_025_Add_the_External_ntp_server_to_grid_member_synchronization_by_overiding_the_grid(self):
		print_and_log("Add the External ntp server to grid member synchronization by overiding the grid")
		request = ib_NIOS.wapi_request('GET', object_type="member")
		request = json.loads(request)
		res_ref = request[1]['_ref']
		print_and_log(res_ref)
		data = {"ntp_setting": { "enable_external_ntp_servers": True, "enable_ntp": True, "exclude_grid_master_ntp_server": True, "ntp_servers": [{"address": config.ntp_server, "burst": True, "enable_authentication": False, "iburst": True, "preferred": False}]}}
		request1 = ib_NIOS.wapi_request('PUT', object_type=res_ref, fields=json.dumps(data))
		print_and_log(request1)
		logging.info("******** Restart the NTP service *********")
                response = ib_NIOS.wapi_request('GET',object_type='grid')
                reference = json.loads(response)
                ref = reference[0]['_ref']
                data = {"member_order" : "SIMULTANEOUSLY", "restart_option": "FORCE_RESTART", "service_option": "ALL"}
                response1 = ib_NIOS.wapi_request('POST', object_type=ref + '?_function=restartservices',fields=json.dumps(data))
                if type(response1) == tuple:
                    if response1 == 400 or response1 == 401 or response1 == 402:
                        print("Error while restarting the NTP service")
                        assert False
                else:
                    print("NTP restarted successfully")
                    assert True
                sleep(60)
		print_and_log("TestCase 25 executed successfully")



	@pytest.mark.run(order=26)
	def test_026_Validate_the_external_ntp_server_added_in_the_grid_member_and_excluding_grid_master_ntp_server(self):
		print_and_log("Validate the external ntp server added in the grid member and excluding grid master ntp server")
		print_and_log("Ping the Member ip and check if it is reachable")
		for i in range(300):
			output = os.system("ping -c 2 " + config.grid_member1_vip)
			if output == 0:
				print_and_log(" Member restart is successfull after adding external NTP server")
				break
			else:
				print_and_log(" Ping failed, checking Ping again ")
				sleep(1)
				continue
		print_and_log("Validate the external ntp server added in the grid member and excluding grid master ntp server")
		request = ib_NIOS.wapi_request('GET', object_type="member")
		request = json.loads(request)
		res_ref = request[1]['_ref']
		print_and_log(res_ref)
		request1 = ib_NIOS.wapi_request('GET', object_type=res_ref, params="?_return_fields=ntp_setting")
		output1 = json.loads(request1)
		print_and_log(output1)
		enable_external_ntp = output1['ntp_setting']['enable_external_ntp_servers']
		exclude_grid_master_ntp = output1['ntp_setting']['exclude_grid_master_ntp_server']
		external_ntp_server = output1['ntp_setting']['ntp_servers'][0]['address']
		print_and_log(enable_external_ntp)
		print_and_log(exclude_grid_master_ntp)
		print_and_log(external_ntp_server)
		if enable_external_ntp == True and exclude_grid_master_ntp == True and external_ntp_server == config.ntp_server:
			print_and_log("Modified changes are reflecting")
			assert True
		else:
			print_and_log("Modified changes are not reflecting")
			assert False
		print_and_log("TestCase 26 executed successfully")





	@pytest.mark.run(order=27)
	def test_027_Configure_lower_stratum_value_for_the_member_than_master_grid_and_no_error_should_be_seen(self):
		print_and_log("Configure lower stratum value for the member than master grid and no error should be seen")
		request = ib_NIOS.wapi_request('GET', object_type="member")
		request = json.loads(request)
		res_ref = request[1]['_ref']
		print_and_log(res_ref)
		data = {"ntp_setting": {"local_ntp_stratum": 3, "use_default_stratum": False, "use_local_ntp_stratum": True, "ntp_servers": [{"address": config.ntp_server, "burst": True, "enable_authentication": False, "iburst": True, "preferred": False}]}}
		request1 = ib_NIOS.wapi_request('PUT', object_type=res_ref, fields=json.dumps(data))
		request1 = json.loads(request1)
		print_and_log(request1)
		assert re.search(r'member', request1)
		sleep(80)
		print_and_log("TestCase 27 executed successfully")




	@pytest.mark.run(order=28)
	def test_028_Validate_the_overided_local_ntp_stratum_value_in_grid_member(self):
		print_and_log("Validate the overided local ntp stratum value in grid member")
		global gm_local_ntp_stratum
		request = ib_NIOS.wapi_request('GET', object_type="member")
		request = json.loads(request)
		res_ref = request[1]['_ref']
		print_and_log(res_ref)
		request1 = ib_NIOS.wapi_request('GET', object_type=res_ref, params='?_return_fields=ntp_setting')
		request1 = json.loads(request1)
		print_and_log(request1)
		gm_local_ntp_stratum = request1['ntp_setting']['local_ntp_stratum']
		print_and_log(gm_local_ntp_stratum)
		if int(gm_local_ntp_stratum) == 3:
			print_and_log("Local ntp stratum values are overided successfully")
			assert True
		else:
			print_and_log("Local ntp stratum values are not overided")
			assert False
		print_and_log("TestCase 28 executed successfully")



	@pytest.mark.run(order=29)
	def test_029_validate_the_custom_value_present_in_member_ntp_conf_file(self):
		print_and_log("Validate the custom values present in member ntp.conf file")
		#ip = [config.grid_master_vip, config.grid_member1_vip]
		global gm_local_ntp_stratum
		print("Logging in to device "+ config.grid_member1_vip)
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
		mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
		client.connect(config.grid_member1_vip, username='root', pkey = mykey)
		stdin, stdout, stderr = client.exec_command('cat /tmpfs/ntp.conf')
		output = stdout.read()
		output = output.split("\n")
		print_and_log(output)
		match_line = "tos orphan "+str(gm_local_ntp_stratum)
		match_line2 = "fudge 127.127.1.1 stratum "+str(gm_local_ntp_stratum-1)
		print_and_log(match_line)
		print_and_log(match_line2)
		if match_line in output and match_line2 in output:
			print_and_log("The overided value "+str(gm_local_ntp_stratum) +" is seen in ntpd.conf file")
			assert True
		else:
			print_and_log("The overided value "+str(gm_local_ntp_stratum) +" is not seen in ntpd.conf file")
			assert False
		client.close()
		print_and_log("TestCase 29 executed successfully")





	@pytest.mark.run(order=30)
	def test_030_Change_the_ntp_member_config_to_synchronize_with_grid_master_and_expect_error(self):
		print_and_log("Change the ntp member config to synchronize with grid master and expect error")
		request = ib_NIOS.wapi_request('GET', object_type="member")
		request = json.loads(request)
		res_ref = request[1]['_ref']
		print_and_log(res_ref)
		data = {"ntp_setting": {"enable_external_ntp_servers": False, "exclude_grid_master_ntp_server": False}}
		request1 = ib_NIOS.wapi_request('PUT', object_type=res_ref, fields=json.dumps(data))
		if type(request1) == tuple:
			out = request1[1]
			out = json.loads(out)
			print_and_log(out)
			error_message = out['text']
			expected_error_message = "' NTP member local source stratum restriction: The stratum value of the members must be greater than the Grid Manager. Specified stratum value of the member node is 3,  stratum value of the configured Grid Manager is 8 at the Grid level.'"
			if error_message in expected_error_message:
				print_and_log("Expected Error message is seen")
				assert True
			else:
				print_and_log("Expected Error message is not seen")
				assert False
		else:
			print_and_log(request1)
			print_and_log(" The Invalid values configured successfully")
			assert False
		print_and_log("TestCase 30 executed successfully")






	@pytest.mark.run(order=31)
	def test_031_Configure_the_higher_value_for_the_member_stratum_value_than_grid_master_stratum_value(self):
		print_and_log("Configure the higher value for the member stratum value than grid master stratum value")
		request = ib_NIOS.wapi_request('GET', object_type="member")
		request = json.loads(request)
		res_ref = request[1]['_ref']
		print_and_log(res_ref)
		data = {"ntp_setting": {"local_ntp_stratum": 11, "use_local_ntp_stratum": True, "ntp_servers": [{"address": config.ntp_server, "burst": True, "enable_authentication": False, "iburst": True, "preferred": False}]}}
		request1 = ib_NIOS.wapi_request('PUT', object_type=res_ref, fields=json.dumps(data))
		request1 = json.loads(request1)
		print_and_log(request1)
		assert re.search(r'member', request1)
		sleep(70)
		print_and_log("TestCase 31 executed successfully")



	@pytest.mark.run(order=32)
	def test_032_Validate_the_overided_local_ntp_stratum_value_in_grid_member(self):
		print_and_log("Validate the overided local ntp stratum value in grid member")
		global gm_local_ntp_stratum
		request = ib_NIOS.wapi_request('GET', object_type="member")
		request = json.loads(request)
		res_ref = request[1]['_ref']
		print_and_log(res_ref)
		request1 = ib_NIOS.wapi_request('GET', object_type=res_ref, params='?_return_fields=ntp_setting')
		request1 = json.loads(request1)
		print_and_log(request1)
		gm_local_ntp_stratum = request1['ntp_setting']['local_ntp_stratum']
		print_and_log(gm_local_ntp_stratum)
		if int(gm_local_ntp_stratum) == 11:
			print_and_log("Local ntp stratum values are overided successfully")
			assert True
		else:
			print_and_log("Local ntp stratum values are not overided")
			assert False
		print_and_log("TestCase 32 executed successfully")



	@pytest.mark.run(order=33)
	def test_033_validate_the_custom_value_present_in_member_ntp_conf_file(self):
		print_and_log("Validate the custom values present in member ntp.conf file")
		#ip = [config.grid_master_vip, config.grid_member1_vip]
		global gm_local_ntp_stratum
		print("Logging in to device "+ config.grid_member1_vip)
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
		mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
		client.connect(config.grid_member1_vip, username='root', pkey = mykey)
		stdin, stdout, stderr = client.exec_command('cat /tmpfs/ntp.conf')
		output = stdout.read()
		output = output.split("\n")
		print_and_log(output)
		match_line = "tos orphan "+str(gm_local_ntp_stratum)
		match_line2 = "fudge 127.127.1.1 stratum "+str(gm_local_ntp_stratum-1)
		print_and_log(match_line)
		print_and_log(match_line2)
		if match_line in output and match_line2 in output:
			print_and_log("The overided value "+str(gm_local_ntp_stratum) +" is seen in ntpd.conf file")
			assert True
		else:
			print_and_log("The overided value "+str(gm_local_ntp_stratum) +" is not seen in ntpd.conf file")
			assert False
		client.close()
		print_and_log("TestCase 33 executed successfully")




	@pytest.mark.run(order=34)
	def test_034_Overide_the_member_stratum_values_from_grid_master_when_external_ntp_server_is_synced(self):
		print_and_log("Overide the member stratum values from grid master when external ntp server is synced")
		request = ib_NIOS.wapi_request('GET', object_type="member")
		request = json.loads(request)
		res_ref = request[1]['_ref']
		print_and_log(res_ref)
		data = {"ntp_setting": {"use_local_ntp_stratum": False, "ntp_servers": [{"address": config.ntp_server, "burst": True, "enable_authentication": False, "iburst": True, "preferred": False}]}}
		request1 = ib_NIOS.wapi_request('PUT', object_type=res_ref, fields=json.dumps(data))
		request1 = json.loads(request1)
		print_and_log(request1)
		assert re.search(r'member', request1)
		sleep(60)
		print_and_log("TestCase 34 executed successfully")




	@pytest.mark.run(order=35)
	def test_035_Change_the_ntp_member_config_to_synchronize_with_grid_master_and_expect_no_error(self):
		print_and_log("Change the ntp member config to synchronize with grid master and expect no error")
		request = ib_NIOS.wapi_request('GET', object_type="member")
		request = json.loads(request)
		res_ref = request[1]['_ref']
		print_and_log(res_ref)
		data = {"ntp_setting": {"enable_external_ntp_servers": False, "exclude_grid_master_ntp_server": False}}
		request1 = ib_NIOS.wapi_request('PUT', object_type=res_ref, fields=json.dumps(data))
		print_and_log(request1)
		assert re.search(r'member', request1)
		print_and_log("TestCase 35 executed successfully")




	@pytest.mark.run(order=36)
	def test_036_Exeute_the_cli_command_show_ntp_stratum(self):
		print_and_log("Exeute the cli command show ntp stratum")
		args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+str(config.grid_master_vip)
		args=shlex.split(args)
		child = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		child.stdin.write("set maintenancemode\n")
		child.stdin.write("show ntp_stratum\n")
		child.stdin.write("exit")
		result = child.communicate()
		print_and_log(result)
		result = str(result)
		if "GM NTP Orphan Mode stratum" in result and "Member NTP Orphan Mode stratum" in result:
		    print_and_log("Show ntp startum command worked successfully")
		    assert True
		else:
		    print_and_log("Show ntp startum command worked successfully")
		    assert False
		print_and_log("TestCase 36 executed successfully")


        
        @pytest.mark.run(order=37)
        def test_037_Configure_the_stratum_values_using_cli_command_set_ntp_stratum(self):
            print_and_log("Exeute the cli command show ntp stratum")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            try:
               child.expect ('password.*:')
               child.sendline ('infoblox')
               child.expect ('Infoblox >',timeout=60)
               child.sendline('set maintenancemode')
               child.expect("Maintenance Mode > ")
               child.sendline ('set ntp_stratum')
               child.expect ('y or n')
               child.sendline ('n')
               #print(child.before)
               child.expect (':')
               child.sendline ('6')
               child.expect (':')
               child.sendline ('8')
               child.expect ('y or n')
               child.sendline ('y')
               child.expect ('y or n')
               child.sendline ('y')
               sleep(10)
               child.sendline ('show ntp_stratum')
               child.expect('Maintenance Mode >')
               result = child.before
               print_and_log(result)
               if "GM NTP Orphan Mode stratum" in result and "Member NTP Orphan Mode stratum" in result:
                    print_and_log(" ntp stratum values are configured successfully ")
                    assert True
            except Exception as e:
               print_and_log("ntp stratum values are not configured successfully")
               print_and_log(e)
               assert False
            finally:
               child.close()
            print_and_log("TestCase 37 executed successfully")


	@pytest.mark.run(order=38)
	def test_038_Verify_the_cli_command_show_ntp_stratum_and_validate_newly_configured_values(self):
		print_and_log("Exeute the cli command show ntp stratum")
		args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+str(config.grid_master_vip)
		args=shlex.split(args)
		child = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		child.stdin.write("set maintenancemode\n")
		child.stdin.write("show ntp_stratum\n")
		child.stdin.write("exit")
		result = child.communicate()
		print_and_log(result)
		result = str(result)
		match_line1=".*GM\sNTP\sOrphan\sMode\sstratum:(\s+)(\d+).*"
		match_line2=".*Member\sNTP\sOrphan\sMode\sstratum:(\s+)(\d+).*"
		output1 = re.match(match_line1, result)
		cli_output1 = output1.group(2)
		print_and_log(output1)
		output2 = re.match(match_line2, result)
		cli_output2 = output2.group(2)
		print_and_log(output2)
		if cli_output1 == "6" and cli_output2 == "8":
			print_and_log(" Configured values are reflecting in CLI")
			assert True
		else:
			print_and_log(" Configured values are not reflecting in CLI")
			assert False
		sleep(60)
		print_and_log("TestCase 38 executed successfully")



	@pytest.mark.run(order=39)
	def test_039_validate_the_custom_value_present_in_master_ntp_conf_file(self):
		print_and_log("Validate the custom values present in master ntp.conf file")
		print("Logging in to device "+config.grid_master_vip)
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
		mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
		client.connect(config.grid_master_vip, username='root', pkey = mykey)
		stdin, stdout, stderr = client.exec_command('cat /tmpfs/ntp.conf')
		output = stdout.read()
		output = output.split("\n")
		print_and_log(output)
		match_line = "tos orphan 6"
		match_line2 = "fudge 127.127.1.1 stratum 5"
		print_and_log(match_line)
		if match_line in output and match_line2 in output:
			print_and_log("The custom value that is updated is seen in ntpd.conf file")
			assert True
		else:
			print_and_log("The custom value that is not updated in ntpd.conf file")
			assert False
		client.close()
		print_and_log("TestCase 39 executed successfully")


	@pytest.mark.run(order=40)
	def test_040_validate_the_custom_value_present_in_member_ntp_conf_file(self):
		print_and_log("Validate the custom values present in member ntp.conf file")
		print("Logging in to device "+config.grid_member1_vip)
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
		mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
		client.connect(config.grid_member1_vip, username='root', pkey = mykey)
		stdin, stdout, stderr = client.exec_command('cat /tmpfs/ntp.conf')
		output = stdout.read()
		output = output.split("\n")
		print_and_log(output)
		match_line = "tos orphan 8"
		match_line2 = "fudge 127.127.1.1 stratum 7"
		print_and_log(match_line)
		if match_line in output and match_line2 in output:
			print_and_log("The custom value that is updated is seen in ntpd.conf file")
			assert True
		else:
			print_and_log("The custom value that is not updated in ntpd.conf file")
			assert False
		client.close()
		print_and_log("TestCase 40 executed successfully")



	@pytest.mark.run(order=41)
	def test_041_verify_if_grid_master_2_is_acting_as_local_ntp_server_since_external_server_is_not_present(self):
		print_and_log("Verify if grid master 2 is acting as local ntp server since external server is not present")
		args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+str(config.grid2_vip)
		args=shlex.split(args)
		flag = False
		for i in range(0, 10):
			child = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			child.stdin.write("show ntp\n")
			result = child.communicate()
			print_and_log(result)
			result = str(result)
			if "*127.127.1.1" in result:
				print_and_log(" Grid is synced with local NTP server")
				flag = True
				break
			else:
				print_and_log(" Grid is not synced with local NTP server continuing the loop again")
				sleep(60)
				continue
		if flag == False:
			print_and_log(" Grid is not synced with local NTP server ")
			assert False
		print_and_log("TestCase 41 Exeuted successfully")

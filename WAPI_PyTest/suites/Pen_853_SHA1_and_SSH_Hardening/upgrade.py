#!/usr/bin/env python

__author__ 	= "Prasad K"
__email__  	= "pkondisetty@infoblox.com"
__Project__    	= "UPGRADE"

import re
import sys
import config
import pytest
import unittest
import os
import os.path
import json
import pexpect
import requests
import commands
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util
import ib_utils.common_utilities as comm_util
import sys

class UPGRADE(unittest.TestCase):

        @pytest.mark.run(order=01)
        def test_01_Initiate_Upgrade_file_upload(self):
                print("\n============================")
                print("Initiate Upgrade file upload")
                print("============================\n")
		global token
		global url
		global steps_total
		steps_total = "grid_info "+config.grid_vip
		steps_total = os.popen(steps_total).read()
		online = steps_total.count("ONLINE")
		synchronizing = steps_total.count("SYNCHRONIZING")
		steps_total = online + synchronizing
		IP = (str(config.grid_vip))
                for i in range(30):
                        ping = os.popen("for i in range{1..3} ; do ping -c 4 -w 10 "+IP+" ; done").read()
                        print(ping)
                        if "0 received" not in ping:
                                print(IP+" is pinging ")
                                print("\n")
                                try:
					data = ib_NIOS.wapi_request('POST', object_type="fileop",params="?_function=uploadinit")
					print(data)
					data  = json.loads(data)
					data  = eval(json.dumps(data))
					token = data['token']
					url   = data['url']
					break
                                except:
                                        print("Not able Initiate Upgrade file upload, Going to sleep for 60 seconds")
                                        sleep(60)
                        else:
                                print(IP+" is not pinging, Going to sleep for 60 seconds ")
                                print("\n")
                                sleep(60)
		sleep(10)
		print("\n=========================================")
		print("Upgrade file upload initiate is completed")
		print("=========================================\n")

        @pytest.mark.run(order=02)
        def test_02_Upload_the_Upgrade_file(self):
                print("\n=====================")
                print("Upload the Upgrade file")
                print("=====================\n")
                url_upload = ('curl -k -u admin:infoblox -F name='+config.image+' -F filedata=@'+config.image+' '+'"'+url+'"')
                url_upload  = os.popen(url_upload).read()
		print(url_upload)
		sleep(20)
		print("\n==============================")
		print("Upgrade file upload is completed")
		print("==============================\n")
	
        @pytest.mark.run(order=03)
        def test_03_Set_it_as_the_Upgrade_file(self):
                print("\n==============================================")
                print("Set it as the Upgrade file")
                print("==============================================\n")
		data = {"token":token}
	        token_upload = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=set_upgrade_file")
		print("\n")
	 	print(token_upload)	
		sleep(05)
		print("\n=========================")
		print("Token uploaded is completed")
		print("=========================\n")

        @pytest.mark.run(order=04)
        def test_04_Call_the_upgrade_function_to_UPLOAD_the_file(self):
                print("\n==========================================")
                print("Call the upgrade function to UPLOAD the file")
                print("==========================================\n")
		data = {"action": "UPLOAD"}
		upload_file = ib_NIOS.wapi_request('POST', object_type="grid",fields=json.dumps(data),params="?_function=upgrade")
		print(upload_file)
		sleep(20)
		print("\n==============")
		print("Uplod is Started")
		print("==============\n")
		
        @pytest.mark.run(order=05)
        def test_05_Call_the_upgrade_function_to_start_the_distribution_process(self):
                print("\n=========================================================")
                print("Call the upgrade function to start the distribution process")
                print("=========================================================\n")
		data = {"action": "DISTRIBUTION_START"}
		for i in range(20):
			upgrade_status = ib_NIOS.wapi_request('GET', object_type="upgradestatus?type=GRID", grid_vip=config.grid_vip)
	                print(upgrade_status) 
			if '''"grid_state": "UPLOADED"''' in upgrade_status:
				distribute=ib_NIOS.wapi_request('POST',object_type="grid",fields=json.dumps(data),params="?_function=upgrade")
				print(distribute)
				break
			else:
				print("Going to sleep for 60 seconds")
				sleep(60)
				continue
		upgrade_status = ib_NIOS.wapi_request('GET', object_type="upgradestatus?type=GRID", grid_vip=config.grid_vip)
                print(upgrade_status)
		if '''"grid_state": "UPLOADED"''' in upgrade_status:
			assert False
			print("UPGRADE Failed at Distribution")
		else:
			assert True
		print("\n==========================================")
		print("Upload is completed, Distribution is started")	
		print("==========================================\n")

        @pytest.mark.run(order=06)
        def test_06_Call_the_upgrade_function_to_start_the_Upgrade_test_process(self):
                print("\n=========================================================")
                print("Call the upgrade function to start the Upgrade test process")
                print("=========================================================\n")
		data = {"action": "UPGRADE_TEST_START"}
		for i in range(72):
			upgrade_status = ib_NIOS.wapi_request('GET', object_type="upgradestatus?type=GRID", grid_vip=config.grid_vip)
	                print(upgrade_status)
                        if '''"grid_state": "DISTRIBUTING_COMPLETE"''' in upgrade_status:
                                UPGRADE_TEST=ib_NIOS.wapi_request('POST',object_type="grid",fields=json.dumps(data),params="?_function=upgrade")
                                print(UPGRADE_TEST)
                                break
                        else:
				print("Going to sleep for 100 seconds")
                                sleep(100)
                                continue
		sleep(10)
		upgrade_status = ib_NIOS.wapi_request('GET', object_type="upgradestatus?type=GRID", grid_vip=config.grid_vip)
                print(upgrade_status)
		if '''"grid_state": "DISTRIBUTING"''' in upgrade_status:
			assert False
			print("UPGRADE Failed at UPGRADE TEST")
		else:
			assert True
		print("\n===============================================")
                print("Distribution is completed, UPGRAE Test is started")
		print("===============================================\n")
			
        @pytest.mark.run(order=07)
        def test_07_Call_the_upgrade_function_to_start_the_UPGRADE(self):
                print("\n============================================")
                print("Call the upgrade function to start the UPGRADE")
                print("============================================\n")
                data = {"action": "UPGRADE"}
                for i in range(20):
			upgrade_status = ib_NIOS.wapi_request('GET', object_type="upgradestatus?type=GRID", grid_vip=config.grid_vip)
                        print(upgrade_status)
                        if '''"upgrade_test_status": "COMPLETED"''' in upgrade_status:
                                UPGRADE_TEST=ib_NIOS.wapi_request('POST',object_type="grid",fields=json.dumps(data),params="?_function=upgrade")
                                print(UPGRADE_TEST)
                                break
                        else:
				print("Going to sleep for 30 seconds")
                                sleep(30)
                                continue
		sleep(10)
		upgrade_status = ib_NIOS.wapi_request('GET', object_type="upgradestatus?type=GRID", grid_vip=config.grid_vip)
		print(upgrade_status)
		if '''"upgrade_test_status": "COMPLETED"''' in upgrade_status:
			assert False
			print("Failed at UPGRADE")
		else:
			assert True
		print("\n===========================================")
                print("UPGRADE Test is completed, UPGRADE is started")
		print("===========================================\n")
	
        @pytest.mark.run(order=18)
        def test_08_Check_the_Upgrade_status(self):
                print("\n=========================")
                print("Checking the upgrade status")
                print("=========================\n")
		sleep(600)
		IP = (str(config.grid_vip))
		for i in range(72):
                        ping = os.popen("for i in range{1..3} ; do ping -c 4 -w 10 "+IP+" ; done").read()
                        print(ping)
                        if "0 received" not in ping:
                               	print(IP+" is pinging ")
                               	print("\n")
				try:
	                        	upgrade_status = ib_NIOS.wapi_request('GET', object_type="upgradestatus?type=GRID", grid_vip=config.grid_vip)
				        print(upgrade_status)
					upgrade_status = upgrade_status.replace("[","").replace("]","")
					upgrade_status = json.loads(upgrade_status)
					#steps_total = upgrade_status["steps_total"]
					steps_completed  = upgrade_status["steps_completed"]
	                	        if steps_total == steps_completed:
						print("UPGRADE is Completd")	
						break
					else:
						print("Going to sleep for 100 seconds")
						sleep(100)
				except:
					print(" Going to sleep for 100 seconds")
					sleep(100)
	                else:
                             	print(IP+" is not pinging, Going to sleep for 100 seconds ")
	                        print("\n")
                	        sleep(100)
		print("\n==========================")
		print("UPGRADE Process is Completed")
		print("==========================\n")

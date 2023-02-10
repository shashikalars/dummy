import re
import sys
import config
import pytest
import unittest
import logging
import ast
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
from ib_utils.common_utilities import generate_token_from_file

#Variables
group_ref_Default = "gmcgroup/b25lLmdtY19ncm91cCREZWZhdWx0:Default"; global group_ref_Default
group_ref_gp1 = "gmcgroup/b25lLmdtY19ncm91cCRncDE:gp1"; global group_ref_gp1
group_schedule_ref = "b25lLmdtY19zY2hlZHVsZV9ncm91cCQw"; global group_schedule_ref

#supporting Functions
def print_and_log(arg=""):
        print(arg)
        logging.info(arg)

def print_and_log_header(arg=""):
	arg = "\n" + "*"*10 + " " + "Beginning of Test Case : " + arg +  " " + "*"*10
	print_and_log(arg)

def print_and_log_footer(arg=""):
        arg = "*"*10 + " " + "End of Test Case: " + arg +  " " + "*"*10
        print_and_log(arg)


#GMC group WAPI Requests functions
def Get_GMC_Groups(objectname):
        print_and_log("Get GMC groups in the grid")
	get_data = ib_NIOS.wapi_request('GET', object_type="gmcgroup")
	gmc_groups = json.loads(get_data)
	return gmc_groups
	print_and_log("GMC Groups in the grid are : " + gmc_groups)

def Count_GMC_Groups(objectname, local_gmc_groups):
	print_and_log("Count GMC groups in the grid")
        count = len(local_gmc_groups)
	return count	

def Get_GMC_Group_Name_and_Ref_using_index(objectname, local_gmc_groups, index):
	print_and_log("Print GMC group Names and Ref in the grid of given index : " + str(index))
	gmc_group = local_gmc_groups[index]
	group_name, group_ref = (gmc_group["name"], gmc_group["_ref"])
	print_and_log("GMC group Name is " +  group_name)
	print_and_log("GMC group Ref is " +  group_ref)
        return group_name, group_ref

def Get_GMC_Group_Name_and_Ref_using_Group_Name(objectname, local_gmc_groups, search_group_name):
        print_and_log("Print GMC group name and ref in the grid using given group name : " + str(index))
	for group_group in local_gmc_groups:
		group_name, group_ref = (gmc_group["name"], gmc_group["_ref"])
		if (group_name ==  search_group_name):
			return group_ref
		else:
			return "GroupNOTFound"

def Get_GroupRef_DefaultGroup(object_name):
        print_and_log("Get GroupRef of Default Group")
        get_data = ib_NIOS.wapi_request('GET', object_type="gmcgroup")
        res = json.loads(get_data)
	group_ref = res[0]["_ref"]
        global group_ref


#system level functions 
def validate_sigsegv_sigquit_and_sigabrt_core_files(grid_vip):
        print("************ Validate Sigsegv Sigquit and Sigabrt Core files ************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(grid_vip, username='root', pkey = mykey)
        stdin, stdout, stderr = client.exec_command('ls -lrt /storage/cores')
        count_sigsegv=0
        count_sigabrt=0
        count_sigquit=0
        for i in stdout.readlines():
            print(i)
            if re.search(r'core.isc-worker0000.SIGSEGV', i):
                count_sigsegv=count_sigsegv+1
            elif re.search(r'core.idns_healthd.SIGABRT', i):
                count_sigabrt=count_sigabrt+1
            elif re.search(r'core.named.SIGQUIT', i):
                count_sigquit=count_sigquit+1
        print(str(count_sigsegv)+" core.isc-worker0000.SIGSEGV files are seen")
        print(str(count_sigabrt)+" core.idns_healthd.SIGABRT files are seen")
        print(str(count_sigquit)+" core.named.SIGQUIT files are seen")
        if count_sigsegv == 0 and count_sigabrt == 0 and count_sigquit == 0:
            print("No core files are seen")
            assert True
        else:
            print("Core files are seen")
            assert False





#Test Cases
class RFE_4753_Scheduled_Group_GMC_Promotion(unittest.TestCase):

        @pytest.mark.run(order=1)
        def test_001_Validate_Default_GMC_Group(self):
                print_and_log("\n********** Validate whether only Default Group is available **********")
                get_data = ib_NIOS.wapi_request('GET', object_type="gmcgroup")
                print_and_log(get_data)
                res = json.loads(get_data)
                print_and_log(res)
		count = len(res)
                print_and_log("Number of groups : " + str(count))
                groupname = res[0]["name"]
                print_and_log("Name of group : " + groupname)
                groupref = res[0]["_ref"]
                print_and_log("Id of group : " + groupref)
		assert count == 1 and groupname == "Default" and groupref == "gmcgroup/b25lLmdtY19ncm91cCREZWZhdWx0:Default"
                print_and_log("*********** Test Case Execution Completed **********")


        @pytest.mark.run(order=9)
        def test_009_Validate_Default_GMC_Group(self):
		test_case_title = "Test 009 Validate whether only Default Group is available"
                print_and_log_header(test_case_title)
                res = Get_GMC_Groups(self); print_and_log(res)
                count = Count_GMC_Groups(self, res); print_and_log("Number of groups : " + str(count))
		group_name, group_ref = Get_GMC_Group_Name_and_Ref_using_index(self, res, index=0)
                print_and_log("Name of group : " + group_name); print_and_log("Ref of group : " + group_ref)
                assert count == 1 and group_name == "Default" and group_ref == group_ref_Default
                print_and_log_footer(test_case_title)




        @pytest.mark.run(order=2)
        def test_002_Validate_Default_GMC_Group_Details(self):
                print_and_log("\n********** Validate Default Group Details **********")
                Get_GroupRef_DefaultGroup(self)
		print_and_log("group_ref : " + group_ref)
                get_data = ib_NIOS.wapi_request('GET', object_type=""+group_ref+"?_return_fields=name,comment,gmc_promotion_policy,scheduled_time,members,time_zone")
                print_and_log(get_data)
		res = json.loads(get_data)
		print_and_log(res)
                count = len(res["members"])
                #ToDo: Validate list of members
		print_and_log("Number of groups : " + str(count))
                assert count == 5
                print_and_log("*********** Test Case Execution Completed **********")

        @pytest.mark.run(order=3)
        def test_003_Validate_Creation_of_GMC_Group(self):
                print_and_log("\n********** Validate Creation of Group **********")
                data = {"name":"gp1"}
                get_data = ib_NIOS.wapi_request('POST', object_type="gmcgroup", fields=json.dumps(data))
		print_and_log(get_data)
                res = json.loads(get_data)
                print_and_log(res)
		assert res == "gmcgroup/b25lLmdtY19ncm91cCRncDE:gp1"
                #ToDo: Validate whether list of groups has 2 groups
                print_and_log("*********** Test Case Execution Completed **********")

        @pytest.mark.run(order=4)
        def test_004_Validate_Adding_Members_to_GMC_Group(self):
                print_and_log("\n********** Validate Addition of Members to GMC Group **********")
		data = {"members":[{"member":"vm-sa1.infoblox.com"}]}
		get_data = ib_NIOS.wapi_request('PUT', object_type=""+group_ref_gp1, fields=json.dumps(data))
		print_and_log(get_data)
                res = json.loads(get_data)
                print_and_log(res)
                assert res == "gmcgroup/b25lLmdtY19ncm91cCRncDE:gp1"
		# Validate member is added to gp1 group
                get_data = ib_NIOS.wapi_request('GET', object_type=""+group_ref_gp1+"?_return_fields=name,comment,gmc_promotion_policy,scheduled_time,members,time_zone")
                print_and_log(get_data)
                res = json.loads(get_data)
                print_and_log(res)
                count = len(res["members"])
                #ToDo: Validate list of members
                print_and_log("Number of groups : " + str(count))
                assert count == 1
                #ToDo: Validate member is moved out of default group as it is moved to new group
                print_and_log("*********** Test Case Execution Completed **********")

        @pytest.mark.run(order=5)
        def test_005_Validate_Updating_SCHEDULED_TIME_and_GMC_PROMOTION_POLICY_to_GMC_Group(self):
                print_and_log("\n********** Validate Updation of Scheduled Time and GMC Promotion Policy to GMC Group **********")
                data = {"scheduled_time": 1675772044,"gmc_promotion_policy":"SEQUENTIALLY"}
                get_data = ib_NIOS.wapi_request('PUT', object_type=""+group_ref_gp1, fields=json.dumps(data))
                print_and_log(get_data)
                res = json.loads(get_data)
                print_and_log(res)
                assert res == "gmcgroup/b25lLmdtY19ncm91cCRncDE:gp1"
		# Validate gmcpromotion and Scheduled Time is added to gp1 group [EXPECTED to FAIL as we have a bug]
                get_data = ib_NIOS.wapi_request('GET', object_type=""+group_ref_gp1+"?_return_fields=name,comment,gmc_promotion_policy,scheduled_time,members,time_zone")
                print_and_log(get_data)
                res = json.loads(get_data)
                print_and_log(res)
                gmc_promotion_policy = res["gmc_promotion_policy"]
                scheduled_time = res["scheduled_time"]
                assert gmc_promotion_policy == "SEQUENTIALLY" and scheduled_time == data["scheduled_time"]
                print_and_log("*********** Test Case Execution Completed **********")

        @pytest.mark.run(order=6)
        def test_006_Validate_Deletion_of_GMC_Group(self):
                print_and_log("\n********** Validate Deletion of GMC Group **********")
                get_data = ib_NIOS.wapi_request('DELETE', object_type=""+group_ref_gp1)
                print_and_log(get_data)
                res = json.loads(get_data)
                print_and_log(res)
                assert res == "gmcgroup/b25lLmdtY19ncm91cCRncDE:gp1"
		# Validate only Default Group exists and gp1 is deleted
                get_data = ib_NIOS.wapi_request('GET', object_type="gmcgroup")
                print_and_log(get_data)
                res = json.loads(get_data)
                print_and_log(res)
                count = len(res)
                print_and_log("Number of groups : " + str(count))
                groupname = res[0]["name"]
                print_and_log("Name of group : " + groupname)
                groupref = res[0]["_ref"]
                print_and_log("Id of group : " + groupref)
                assert count == 1 and groupname == "Default" and groupref == "gmcgroup/b25lLmdtY19ncm91cCREZWZhdWx0:Default"
                print_and_log("*********** Test Case Execution Completed **********")


	# GMC Schedule Object Testing
        @pytest.mark.run(order=7)
        def test_007_Getting_GMC_Schedule_Object(self):
                print_and_log("\n********** Validating GMC Schedule Object **********")
                get_data = ib_NIOS.wapi_request('GET', object_type="gmcschedule/"+group_schedule_ref+"?_return_fields=activate_gmc_group_schedule,gmc_groups")
                print_and_log(get_data)
                res = json.loads(get_data)
                print_and_log(res)
		gmcschedule_ref = res["_ref"]
                assert gmcschedule_ref == "gmcschedule/"+group_schedule_ref
                #ToDo: Validations for schedule
                print_and_log("*********** Test Case Execution Completed **********")


        @pytest.mark.run(order=8)
        def test_008_Activating_GMC_Schedule(self):
                print_and_log("\n********** Activating GMC Schedule **********")
		data = {"activate_gmc_group_schedule": True}
                get_data = ib_NIOS.wapi_request('PUT', object_type="gmcschedule/"+group_schedule_ref, fields=json.dumps(data))
                print_and_log(get_data)
                res = json.loads(get_data)
                print_and_log(res)
		assert res == "gmcschedule/"+group_schedule_ref
		# Validate GMC schedule is active
                get_data = ib_NIOS.wapi_request('GET', object_type="gmcschedule/"+group_schedule_ref+"?_return_fields=activate_gmc_group_schedule,gmc_groups")
                print_and_log(get_data)
                res = json.loads(get_data)
                print_and_log(res)
                activate_status_gmcschedule = res["activate_gmc_group_schedule"]
                assert activate_status_gmcschedule == True
                #Deactivate schedule to bring back to base state
                data = {"activate_gmc_group_schedule": False}
                get_data = ib_NIOS.wapi_request('PUT', object_type="gmcschedule/"+group_schedule_ref, fields=json.dumps(data))
                print_and_log(get_data)
                res = json.loads(get_data)
                print_and_log(res)
                assert res == "gmcschedule/"+group_schedule_ref
                print_and_log("*********** Test Case Execution Completed **********")



        @pytest.mark.run(order=10)
    	def test_010_Making_normal_member_as_GMC(self):
        	logging.info("making normal member as GMC ")
        	get_ref = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
        	#ref1 = json.loads(get_ref)[0]['_ref']
        	res = json.loads(get_ref)
        	res = eval(json.dumps(res))
        	print(res)
        	ref1=(res)[1]['_ref']
        	print(ref1)
		"""
		data1 = {"master_candidate": True}
        	output1 = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data1),grid_vip=config.grid_vip)
        	print(output1)
        	ref2=(res)[4]['_ref']
        	print(ref2)
        	data2 = {"master_candidate": True}
        	output2 = ib_NIOS.wapi_request('PUT',ref=ref2,fields=json.dumps(data2),grid_vip=config.grid_vip)
        	print(output2)
        	sleep(600)
        	print("-----------Test Case 10 Execution Completed------------")

		"""

      


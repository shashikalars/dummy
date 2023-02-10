#!/usr/bin/env python
__author__ = "Prasad K"
__email__  = "pkondisetty@@infoblox.com"

####################################################################################
#  Grid Set up required:                                                           #
#  1. Grid Master with two members                                                 #
#  2. Licenses : DNS, Grid, NIOS(IB_1415),RPZ,Threat Analytics                     #
#  3. Enable DNS services                                                          #
#  NIOSSPT JIRA link : https://jira.inca.infoblox.com/browse/NIOSSPT-11156         #
#                                                                                  #
####################################################################################
import re
import pprint
import config
import pytest
import unittest
import logging
import subprocess
import os
import json
import ib_utils.ib_NIOS as ib_NIOS
from time import sleep
import commands
import json, ast
import requests
import time
import pexpect
import sys
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv

class NIOSSPT_11156(unittest.TestCase):


        @pytest.mark.run(order=01)
        def test_01_Start_DNS_Service_on_all_members(self):
            logging.info("Start DNS Service")
            data = {"enable_dns": True}
            for i in range(0,3):
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                member = json.loads(get_ref)[i]['_ref']
                response = ib_NIOS.wapi_request('PUT', ref=member, fields=json.dumps(data))
                print(response)
            print("Test Case 01 Execution Completed")


        @pytest.mark.run(order=2)
        def test_02_Validate_Enabled_DNS_service_on_all_members(self):
            logging.info("Validate enabled DNS Service on all members")
	    data = '"enable_dns": true'
	    for i in range(0,3):
		grid =  ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
		member_ref = json.loads(grid)[i]['_ref']
		response = ib_NIOS.wapi_request('GET',ref=member_ref,params="?_inheritance=True&_return_fields=enable_dns",grid_vip=config.grid_vip)
		if '"enable_dns": true' in response:
			assert True
		else:
			assert False
	        print(response)
	    print("Test Case 02 Execution Completed")


        @pytest.mark.run(order=3)
        def test_03_Add_Authoritative_zone(self):
            logging.info("Create Authoritative Zone")
            data = {"fqdn": "test.com","grid_primary": [{"name": config.grid_fqdn,"stealth": False},{"name": config.grid_member1_fqdn,"stealth": False},{"name": config.grid_member2_fqdn,"stealth": False}]}
            response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
            print(response)
            logging.info("restarting the grid services")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
            ref = json.loads(grid)[0]['_ref']
            data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
            sleep(20) #wait for 20 secs for the member to get started
            print("Test Case 03 Execution Completed")

        @pytest.mark.run(order=4)
        def test_04_Validate_addedition_of_Authoritative_zone(self):
	    logging.info("Validate added authoritative zone")
	    response = ib_NIOS.wapi_request('GET',object_type="zone_auth?fqdn=test.com&_return_fields=fqdn,grid_primary&_return_as_object=1",grid_vip=config.grid_vip)
	    print(response)
	    data = ('"fqdn": "test.com"','"name": "'+config.grid_fqdn+'"','"name": "'+config.grid_member1_fqdn+'"','"name": "'+config.grid_member2_fqdn+'"')
	    for i in data:
	    	if i in response:
        	    assert True
	    	else:
        	    assert False
	    print(data)
	    print("\n")
	    print("Test Case 04 Execution Completed")


        @pytest.mark.run(order=5)
        def test_05_Add_RPZ_zone(self):
            logging.info("Create RPZ Zone")
            data = {"fqdn": "threatinsight","grid_primary": [{"name": config.grid_fqdn,"stealth": False},{"name": config.grid_member1_fqdn,"stealth": False}]}
            response = ib_NIOS.wapi_request('POST', object_type="zone_rp", fields=json.dumps(data))
            print(response)
            logging.info("restarting the grid services")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
            ref = json.loads(grid)[0]['_ref']
            data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
            sleep(30) #wait for 30 secs for the member to get started
            print("Test Case 05 Execution Completed")

        @pytest.mark.run(order=6)
        def test_06_Validate_addition_of_RPZ_zone(self):
            logging.info("Validate added authoritative zone")
            response = ib_NIOS.wapi_request('GET',object_type="zone_rp?fqdn=threatinsight&_return_fields=fqdn,grid_primary&_return_as_object=1",grid_vip=config.grid_vip)
            print(response)
            data = ('"fqdn": "threatinsight"','"name": "'+config.grid_fqdn+'"','"name": "'+config.grid_member1_fqdn+'"')
            for i in data:
                if i in response:
                    assert True
                else:
                    assert False
            print(data)
            print("\n")
            print("Test Case 06 Execution Completed")

        @pytest.mark.run(order=7)
        def test_07_Associate_created_RPZ_Zone_at_threat_analytics_properties(self):
            logging.info("Associate RPZ zone at threat analytics properties")
	    get_ref = ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics", grid_vip=config.grid_vip)
	    ref = json.loads(get_ref)[0]['_ref']
            response = ib_NIOS.wapi_request('GET',object_type="zone_rp?fqdn=threatinsight",grid_vip=config.grid_vip)
            print(response)
	    ref1 = json.loads(response)[0]['_ref']
	    print(ref1)	
	    data = {"dns_tunnel_black_list_rpz_zones": [ref1]}
            output = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
            print(output)
	    print("Test Case 07 Execution Completed")

        @pytest.mark.run(order=8)
        def test_08_Validate_association_of_RPZ_zone_at_Threat_Analytics(self):
            logging.info("Validate association of RPZ Zone at threat analytics properties")
            response = ib_NIOS.wapi_request('GET',object_type="grid:threatanalytics",params="?_inheritance=True&_return_fields=dns_tunnel_black_list_rpz_zones",grid_vip=config.grid_vip)
            print(response)
	    get_ref = ib_NIOS.wapi_request('GET',object_type="zone_rp?fqdn=threatinsight",grid_vip=config.grid_vip)
            ref = json.loads(get_ref)[0]['_ref']
	    if ref in response:
		assert True
	    else:
		assert False
	    print(ref)
	    print("Test Case 08 Execution Completed")


        @pytest.mark.run(order=9)
        def test_09_Start_Threat_Analytics_Service_on_master_and_member1(self):
            logging.info("Start Threat Analytics Service on master and member1")
	    data = {"enable_service": True}
	    for i in range(0,2):
		get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatanalytics", grid_vip=config.grid_vip)
		ref = json.loads(get_ref)[i]['_ref']
		output = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
		print(output)
	    grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
            ref = json.loads(grid)[0]['_ref']
            data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
            sleep(30) #wait for 30 secs for the member to get started
	    print("Test Case 09 Execution Completed")


        @pytest.mark.run(order=10)
        def test_10_Validate_Enabled_Threat_Analytics_service_on_master_and_member(self):
            logging.info("Validate enabled threat analytic service on master and member1")
	    data = '"enable_service": true'
	    for i in range(0,2):
            	grid =  ib_NIOS.wapi_request('GET', object_type="member:threatanalytics", grid_vip=config.grid_vip)
            	member = json.loads(grid)[i]['_ref']
            	response = ib_NIOS.wapi_request('GET',ref=member,params="?_inheritance=True&_return_fields=enable_service",grid_vip=config.grid_vip)
		print(response)
		if data in response:
                	assert True
            	else:
                	assert False
            print("Test Case 10 Execution Completed")


        @pytest.mark.run(order=11)
        def test_11_Start_infoblox_logs(self):
            logging.info("Starte infoblox logs to check the error message logs")
            log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
            print("Test Case 11 Execution Completed")


        @pytest.mark.run(order=12)
        def test_12_Remove_Name_server_from_RPZ_zone(self):
            logging.info("Remove name server from rpz zone")
	    response =  ib_NIOS.wapi_request('GET', object_type="zone_rp?fqdn=threatinsight", grid_vip=config.grid_vip)
	    print(response)
	    ref = json.loads(response)[0]['_ref']
	    print(ref)
	    data = {"grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
	    output1 = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
            print(output1)
            logging.info("restarting the grid services")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
            ref = json.loads(grid)[0]['_ref']
            data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
            sleep(30) #wait for 30 secs for the member to get started
            print("Test Case 12 Execution Completed")


        @pytest.mark.run(order=13)
        def test_13_Validate_removed_name_server_for_RPZ_zone(self):
            logging.info("Validate removed name server on RPZ zone")
            response = ib_NIOS.wapi_request('GET',object_type="zone_rp?fqdn=threatinsight&_return_fields=grid_primary&_return_as_object=1",grid_vip=config.grid_vip)
            print(response)
            data = '"name": "'+config.grid_member1_fqdn+'"'
            if data in response:
                    assert False
            else:
                    assert True
            print(data)
            print("\n")
            print("Test Case 13 Execution Completed")

        @pytest.mark.run(order=14)
        def test_14_Stop_Threat_Analytics_Service(self):
            logging.info("Stop Threat Analytics Service")
            get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatanalytics", grid_vip=config.grid_vip)
            ref1 = json.loads(get_ref)[1]['_ref']
            data = {"enable_service": False}
            output1 = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
            print(output1)
            grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
            ref = json.loads(grid)[0]['_ref']
            data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
            sleep(30) #wait for 30 secs for the member to get started
            print("Test Case 14 Execution Completed")

        @pytest.mark.run(order=15)
        def test_15_Validate_Disabled_Threat_Analytics_service_on_member1(self):
            logging.info("Validate disabled Threat Analytics Service on member1")
            grid =  ib_NIOS.wapi_request('GET', object_type="member:threatanalytics", grid_vip=config.grid_vip)
            member1 = json.loads(grid)[1]['_ref']
            response = ib_NIOS.wapi_request('GET',ref=member1,params="?_inheritance=True&_return_fields=enable_service",grid_vip=config.grid_vip)
            print(response)
            output = '"enable_service": false'
            if output in response:
                  assert True
            else:
                  assert False
            print("Test Case 15 Execution Completed")


        @pytest.mark.run(order=16)
        def test_16_Start_again_Threat_Analytics_Service_on_member1(self):
            logging.info("Start again Threat Analytics Service on member1 ")
            get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatanalytics", grid_vip=config.grid_vip)
            ref1 = json.loads(get_ref)[1]['_ref']
            data = {"enable_service": True}
            output1 = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
            print(output1)
            grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
            ref = json.loads(grid)[0]['_ref']
            data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
            sleep(30) #wait for 30 secs for the member to get started
            print("Test Case 16 Execution Completed")

        @pytest.mark.run(order=17)
        def test_17_Validate_Enabled_Threat_Analytics_service_on_member1(self):
            logging.info("Validate enabled Threat Analytics Service on member1")
            grid =  ib_NIOS.wapi_request('GET', object_type="member:threatanalytics", grid_vip=config.grid_vip)
            member1 = json.loads(grid)[1]['_ref']
            response = ib_NIOS.wapi_request('GET',ref=member1,params="?_inheritance=True&_return_fields=enable_service",grid_vip=config.grid_vip)
            print(response)
            output = '"enable_service": true'
            if output in response:
                  assert True
            else:
                  assert False
            print("Test Case 17 Execution Completed")

        @pytest.mark.run(order=18)
        def test_18_Assign_back_member1_name_server_to_the_RPZ_zone(self):
            logging.info("assigning back member1 name server to the RPZ zone")
	    response =  ib_NIOS.wapi_request('GET', object_type="zone_rp?fqdn=threatinsight", grid_vip=config.grid_vip)
            print(response)
            ref = json.loads(response)[0]['_ref']
            print(ref)
            data = {"grid_primary": [{"name": config.grid_fqdn,"stealth": False},{"name": config.grid_member1_fqdn,"stealth": False}]}
	    output1 = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
            print(output1)
            logging.info("restarting the grid services")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
            ref = json.loads(grid)[0]['_ref']
            data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
            sleep(30) #wait for 30 secs for the member to get started
            print("Test Case 18 Execution Completed")

        @pytest.mark.run(order=19)
        def test_19_Validate_assigned_name_servers_on_RPZ_zone(self):
            logging.info("Validate assigned name servers for RPZ zone")
            response = ib_NIOS.wapi_request('GET',object_type="zone_rp?fqdn=threatinsight&_return_fields=fqdn,grid_primary&_return_as_object=1",grid_vip=config.grid_vip)
            print(response)
            data = ('"name": "'+config.grid_fqdn+'"','"name": "'+config.grid_member1_fqdn+'"')
            for i in data:
                if i in response:
                    assert True
                else:
                    assert False
            print(data)
            print("\n")
            print("Test Case 19 Execution Completed")


        @pytest.mark.run(order=20)
        def test_20_Stop_infoblox_Logs_to_check_the_error_logs(self):
            logging.info("Stop infoblox logs to check the error logs")
            log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
            print("Test Case 20 Execution Completed")


        @pytest.mark.run(order=21)
        def test_21_Validate_the_error_logs_in_member2_infoblox_logs(self):
            logging.info("validating the error logs in member2 infoblox logs")
            out1 = str(config.grid_member2_vip+'_infoblox_var_infoblox.log')
            print(out1)
            textfile = open('/tmp/'+out1, 'r')
            log_validation = textfile.read()
            textfile.close()
	    error_logs = 'Member reference does not point to valid object'
	    if error_logs in log_validation:
		assert True
	    else:
		assert False
	    print(error_logs)
	    print("Test Case 21 Execution Completed")


#########################################################
## Removing all the configuration to clean up the grid ##
#########################################################


        @pytest.mark.run(order=22)
        def test_22_Disable_Threat_Analytic_Service_on_master_and_member1(self):
            logging.info("Disable Threat Analytics Service on master and member1")
	    data = {"enable_service": False}
	    for i in range(0,2):
            	get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatanalytics", grid_vip=config.grid_vip)
            	ref = json.loads(get_ref)[i]['_ref']
            	output = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
            	print(output)
            grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
            ref = json.loads(grid)[0]['_ref']
            data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
            sleep(30) #wait for 30 secs for the member to get started
            print("Test Case 22 Execution Completed")


        @pytest.mark.run(order=23)
        def test_23_Validate_disabled_Threat_Analytics_service_on_master_and_member1(self):
            logging.info("Validate disabled Threat Analytics Service on master and member1")
	    data = '"enable_service": false'
	    for i in range(0,2):
            	grid =  ib_NIOS.wapi_request('GET', object_type="member:threatanalytics", grid_vip=config.grid_vip)
            	members = json.loads(grid)[i]['_ref']
            	response = ib_NIOS.wapi_request('GET',ref=members,params="?_inheritance=True&_return_fields=enable_service",grid_vip=config.grid_vip)
            	if data in response:
            	      assert True
            	else:
                      assert False
		print(response)
            print("Test Case 23 Execution Completed")


        @pytest.mark.run(order=24)
        def test_24_Remove_RPZ_Zone_at_threat_analytic_properties(self):
            logging.info("Remove RPZ zone at threat analytic properties")
            get_ref = ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics", grid_vip=config.grid_vip)
            ref = json.loads(get_ref)[0]['_ref']
            response = ib_NIOS.wapi_request('GET',object_type="zone_rp?fqdn=threatinsight",grid_vip=config.grid_vip)
            print(response)
            ref1 = json.loads(response)[0]['_ref']
            print(ref1)
            data = {"dns_tunnel_black_list_rpz_zones": []}
            output = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
            print(output)
            print("Test Case 24 Execution Completed")

        @pytest.mark.run(order=25)
        def test_25_Validate_removed_RPZ_zone_at_Threat_Analytics(self):
            logging.info("Validate removed RPZ zone at threat analytics properties")
            get_ref = ib_NIOS.wapi_request('GET',object_type="zone_rp?fqdn=threatinsight",grid_vip=config.grid_vip)
	    print(get_ref)
            ref = json.loads(get_ref)[0]['_ref']
	    response = ib_NIOS.wapi_request('GET',object_type="grid:threatanalytics",params="?_inheritance=True&_return_fields=dns_tunnel_black_list_rpz_zones",grid_vip=config.grid_vip)
            print(response)
            if ref in response:
                assert False
            else:
                assert True
            print("Test Case 25 Execution Completed")


        @pytest.mark.run(order=26)
        def test_26_Delete_created_RPZ_zone(self):
            logging.info("Delete created RPZ zone")
            get_ref = ib_NIOS.wapi_request('GET', object_type="zone_rp?fqdn=threatinsight", grid_vip=config.grid_vip)
	    ref = json.loads(get_ref)[0]['_ref']
            print(get_ref)
            request_restart = ib_NIOS.wapi_request('DELETE',object_type = ref,grid_vip=config.grid_vip)
            logging.info("restarting the grid services")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
            ref = json.loads(grid)[0]['_ref']
            data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
            sleep(30) #wait for 30 secs for the member to get started
            print("Test Case 26 Execution Completed")

        @pytest.mark.run(order=27)
        def test_27_Validate_deleted_RPZ_zone(self):
            logging.info("Valide deleted RPZ zone")
            response = ib_NIOS.wapi_request('GET',object_type="zone_rp?fqdn=threatinsight&_return_fields=fqdn,grid_primary&_return_as_object=1",grid_vip=config.grid_vip)
            print(response)
            if '"result": []' in response:
                    assert True
            else:
                    assert False
            print("\n")
            print("Test Case 27 Execution Completed")

        @pytest.mark.run(order=28)
        def test_28_Delete_Authoritative_zone(self):
            logging.info("Delete Authoritative Zone")
            get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=test.com", grid_vip=config.grid_vip)
	    print(get_ref)
	    ref = json.loads(get_ref)[0]['_ref']
	    response = ib_NIOS.wapi_request('DELETE',object_type = ref,grid_vip=config.grid_vip)
	    print(response)
            logging.info("restarting the grid services")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
            ref = json.loads(grid)[0]['_ref']
            data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
            sleep(30) #wait for 20 secs for the member to get started
            print("Test Case 28 Execution Completed")

        @pytest.mark.run(order=29)
        def test_29_Validate_deleted_Authoritative_zone(self):
            logging.info("Validate deleted authoritative zone")
            response = ib_NIOS.wapi_request('GET',object_type="zone_auth?fqdn=test.com",grid_vip=config.grid_vip)
            print(response)
            if 'test.com' in response:
                    assert False
            else:
                    assert True
            print("\n")
            print("Test Case 29 Execution Completed")

        @pytest.mark.run(order=30)
        def test_30_Stop_DNS_Service_on_all_the_members(self):
            logging.info("Stop DNS Service on all the members")
            data = {"enable_dns": False}
            for i in range(0,3):
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                member = json.loads(get_ref)[i]['_ref']
                response = ib_NIOS.wapi_request('PUT', ref=member, fields=json.dumps(data))
                print(response)
            print("Test Case 30 Execution Completed")


        @pytest.mark.run(order=31)
        def test_31_Validate_Disabled_DNS_service_on_all_the_members(self):
            logging.info("Validate disabled DNS Service on all the members")
            data = '"enable_dns": false'
            for i in range(0,3):
                grid =  ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
                member_ref = json.loads(grid)[i]['_ref']
                response = ib_NIOS.wapi_request('GET',ref=member_ref,params="?_inheritance=True&_return_fields=enable_dns",grid_vip=config.grid_vip)
                if data in response:
                        assert True
                else:
                        assert False
                print(response)
            print("Test Case 31 Execution Completed")


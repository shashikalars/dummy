#!/usr/bin/env python
__author__ = "Siva Krishna K"
__email__  = "krishnas@infoblox.com"
__NIOSSPT__ = "NIOSSPT-11225"
####################################################################################
#  Grid Set up required:                                                           #
#  1. Stand Alone Grid Matser                                                      #
#  2. Licenses : DNS, Grid, NIOS(IB_1415),Security Ecosystem licenses              #
#  3. Enable DNS services                                                          #
#  NIOSSPT JIRA link : https://infoblox.atlassian.net/browse/NIOSSPT-11225         #
#                                                                                  #
####################################################################################

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
from  ib_utils.log_capture import log_action as log
from  ib_utils.log_validation import log_validation as logv
import pexpect
from paramiko import client

class NIOSSPT_11225(unittest.TestCase):
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
        def test_003_Add_REST_API_endpoint(self):
                logging.info("Create_REST_API_Endpoint")
                data={"name": "Endpoint","outbound_member_type": "GM","uri": "https://"+config.grid_vip+"/","server_cert_validation": "NO_VALIDATION","log_level": "DEBUG"}
                response = ib_NIOS.wapi_request('POST', object_type="notification:rest:endpoint", fields=json.dumps(data))
                print response
                logging.info(response)
                assert re.search(r'notification:rest:endpoint',response)    
                print("Test Case 3 Execution Completed")

        @pytest.mark.run(order=4)
        def test_004_Validate_REST_API_endpoint_Test_Connection(self):
                logging.info("REST_API Endpoint Test Connection Validation")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rest:endpoint?name=Endpoint")
                print(get_ref)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                response = ib_NIOS.wapi_request('POST', object_type=ref1+"?_function=test_connection")
                print response
                logging.info(response)
                sleep(20)
                assert re.search(r'"overall_status": "SUCCESS"',response)
                print("Test Case 4 Execution Completed")

	@pytest.mark.run(order=05)
        def test_005_Verify_REST_API_Endpoint(self):
                logging.info("Verify REST API Endpoint")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rest:endpoint?_return_fields=name",grid_vip=config.grid_vip)
                print("response    : ",response)
                if('"name": "Endpoint"'in response):
                         assert True
                else:
                         assert False
                sleep(2)
                logging.info("Test Case 5 Execution Completed")

        @pytest.mark.run(order=6)
        def test_006_Upload_REST_API_Endpoint_Event_Template(self):
                logging.info("Upload REST API Event Template")
                dir_name="./templates/"
                base_filename="Version5_DNS_Zone_and_Records_Action_Template.json"
                token = common_util.generate_token_from_file(dir_name,base_filename)
                data = {"token": token,"overwrite": True}
                response = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=restapi_template_import")
                logging.info(response)
                print response
                logging.info(response)
                res = json.loads(response)
                string = {"overall_status": "SUCCESS","error_message": ""}
                if res == string:
                        assert True
                else:
                        assert False
                print("Test Case 6 Execution Completed")   
	
	@pytest.mark.run(order=07)
        def test_007_Validating_Event_Template(self):
                logging.info("Validating Event Template")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rest:template?name=Version5_DNS_Zone_and_Records_Action_Template") 
		print("response    : ",response)
                if('"name": "Version5_DNS_Zone_and_Records_Action_Template"'in response):
                         assert True
                else:
                         assert False
                sleep(10)
                logging.info("Test Case 7 Execution Completed")	

	
        @pytest.mark.run(order=8)
        def test_008_Create_REST_API_Endpoint_Host_Notification_Rule(self):
                logging.info("Create REST API Endpoint Host Notification Rule")
                get_ref = ib_NIOS.wapi_request('GET',object_type="notification:rest:endpoint?name=Endpoint")
                print(get_ref)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"name":"Test","notification_target":ref1,"event_type":"DB_CHANGE_DNS_HOST_ADDRESS_IPV4","template_instance": {"template": "Version5_DNS_Zone_and_Records_Action_Template"},"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "REGEX","op1": "HOST","op1_type": "FIELD","op2": "~a","op2_type": "STRING"},{"op": "ENDLIST"}],"notification_action": "RESTAPI_TEMPLATE_INSTANCE"}
                print ("data provided :",data)
                response = ib_NIOS.wapi_request('POST', object_type="notification:rule",fields=json.dumps(data))
                print(response)
                global notification_ref
                notification_ref=response
                sleep(10)
                logging.info("Test Case 8 Execution Completed")

        @pytest.mark.run(order=9)
        def test_009_Verify_REST_API_Endpoint_Notification_Rule(self):
                logging.info("Verify_REST_API_Endpoint Notification Rule")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule?_return_fields=template_instance,event_type,name",grid_vip=config.grid_vip)
                print("response    : ",response)
                if('"name": "Test"'in response) and ('"template": "Version5_DNS_Zone_and_Records_Action_Template"' in response) and ('"event_type": "DB_CHANGE_DNS_HOST_ADDRESS_IPV4"' in response):
                         assert True
                else:
                         assert False
                sleep(2)
                logging.info("Test Case 9 Execution Completed")

        @pytest.mark.run(order=10)
        def test_010_create_AuthZone(self):
                logging.info("Create Auth Zone")
                data = {"fqdn": "outbound.com","grid_primary": [{"name": config.grid_member_fqdn,"stealth":False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Restart DNS Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20)
                logging.info("Test Case 10 Execution Completed")

        @pytest.mark.run(order=11)
        def test_011_Verify_Created_Auth_Zone(self):
                logging.info("Verify Created Auth Zone")
                response = ib_NIOS.wapi_request('GET',object_type="zone_auth?fqdn=outbound.com",grid_vip=config.grid_vip)
                print("response    : ",response)
                if('"fqdn": "outbound.com"'in response):
                         assert True
                else:
                         assert False
                sleep(10)
                logging.info("Test Case 11 Execution Completed")

        @pytest.mark.run(order=12)
        def test_012_Capture_Template_execution_logs_While_Creating_Host_Record(self):
                logging.info("Capture_Template_execution_logs_While_Creating_Host Record")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(5)
                data={"ipv4addrs": [{"configure_for_dhcp": False,"ipv4addr": "10.1.1.1","mac": "22:22:22:22:22:22"}],"name": "a.outbound.com","view": "default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data))
                print response
                logging.info(response)
                assert re.search(r'a.outbound.com',response)
                sleep(10)
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(5)
                logging.info("Test Case 12 Execution Completed")

        @pytest.mark.run(order=13)
        def test_013_looking_for_Template_execution_Status(self):
                logging.info("looking_for_Templated_Execution_Status")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("template was executed successfully")
                    assert True
                else:
                    print("template was not executed")
                    assert False
                sleep(5)
                print("Test Case 13 Execution Completed")
        
	#This test case is the exact issue of the bug
        @pytest.mark.run(order=14)
        def test_014_Capture_Template_execution_logs_While_Updating_Host_Record_With_NULL_Parameters_Negative(self):
                logging.info("Capture_Template_execution_logs_While Updating_Host Record With_NULL_Parameters_Negative")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(5)
                get_ref = ib_NIOS.wapi_request('GET',object_type="record:host?name=a.outbound.com")
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                data={}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert re.search(r'a.outbound.com',response)
                sleep(10)
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(5)
                logging.info("Test Case 14 Execution Completed")

        @pytest.mark.run(order=15)
        def test_015_looking_for_Template_execution_Status_Negative(self):
                logging.info("looking_for_Templated_Execution_Status Negative")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)==0):
                    print("template was Not executed which is expected")
                    assert True
                else:
                    print("template was executed which is not expected")
                    assert False
                sleep(5)
                print("Test Case 15 Execution Completed")

        @pytest.mark.run(order=16)
        def test_016_Capture_Template_execution_logs_While_Updating_Host_mac_Address(self):
                logging.info("Capture_Template_execution_logs_While Updating_Host mac address")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(5)
                get_ref = ib_NIOS.wapi_request('GET',object_type="record:host?name=a.outbound.com")
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)    
                data={"ipv4addrs": [{"configure_for_dhcp": False,"ipv4addr": "10.1.1.1","mac": "22:22:22:22:22:11"}]}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert re.search(r'a.outbound.com',response)
                sleep(5)
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(5)
                logging.info("Test Case 16 Execution Completed")

        @pytest.mark.run(order=17)
        def test_017_looking_for_Template_execution_Status(self):
                logging.info("looking_for_Templated_Execution_Status")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("template was executed successfully")
                    assert True
                else:
                    print("template was not executed")
                    assert False
                sleep(5)
                print("Test Case 17 Execution Completed")
    
        @pytest.mark.run(order=18)
        def test_018_Capture_Template_execution_logs_while_doing_GET_Operation(self):
                logging.info("Capture_Template_execution_logs while doing GET_Host")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(5)
                response = ib_NIOS.wapi_request('GET', object_type="record:host?name=a.outbound.com")
                print response
                logging.info(response)
                assert re.search(r'a.outbound.com',response)
                sleep(10)
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(5)
                logging.info("Test Case 18 Execution Completed")

        @pytest.mark.run(order=19)
        def test_019_looking_for_Template_execution_Status(self):
                logging.info("looking for Templated Execution Status")
		check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
		if (int(check)==0):
                    print("template was Not executed which is expected")
                    assert True
                else:
                    print("template was executed which is not expected")
                    assert False
                print("Test Case 19 Execution Completed")

        @pytest.mark.run(order=20)
        def test_020_Capture_Template_execution_logs_While_Deleting_Host_Record(self):
                logging.info("Capture Template execution logs while Deleting Host Record")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(5)
                get_ref = ib_NIOS.wapi_request('GET',object_type="record:host?name=a.outbound.com")
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                response = ib_NIOS.wapi_request('DELETE', object_type=ref1)
                print response
                logging.info(response)
                assert re.search(r'a.outbound.com',response)
                sleep(10)
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(5)
                logging.info("Test Case 20 Execution Completed")

        @pytest.mark.run(order=21)
        def test_021_looking_for_Template_execution_Status(self):
                logging.info("looking_for_Templated_Execution_Status")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("template was executed successfully")
                    assert True
                else:
                    print("template was not executed")
                    assert False
                sleep(5)
                print("Test Case 21 Execution Completed")
	
	@pytest.mark.run(order=22)
        def test_022_Upload_REST_API_Endpoint_Session_Template(self):
                logging.info("Upload REST API Endpoint Session Template")
                dir_name="./templates/"
                base_filename="Version5_REST_API_Session_Template.json"
                token = common_util.generate_token_from_file(dir_name,base_filename)
                data = {"token": token,"overwrite": True}
                response = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=restapi_template_import")
                logging.info(response)
                print response
                logging.info(response)
                res = json.loads(response)
                string = {"overall_status": "SUCCESS","error_message": ""}
                if res == string:
                        assert True
                else:
                        assert False
                print("Test Case 22 Execution Completed")

	@pytest.mark.run(order=23)
        def test_023_Validating_Session_Template(self):
                logging.info("Validating Session Template")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rest:template?name=Version5_REST_API_Session_Template")
                print("response    : ",response)
                if('"name": "Version5_REST_API_Session_Template"'in response):
                         assert True
                else:
                         assert False
                sleep(10)
                logging.info("Test Case 23 Execution Completed")

	@pytest.mark.run(order=24)
        def test_024_Update_REST_API_Endpoint_with_Session_Template(self):
                logging.info("Update_REST API_Endpoint with Session_Template")
                get_ref = ib_NIOS.wapi_request('GET',object_type="notification:rest:endpoint?name=Endpoint")
                print(get_ref)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
		data={"template_instance": {"parameters": [],"template": "Version5_REST_API_Session_Template"}}
		response = ib_NIOS.wapi_request('PUT', object_type=ref1, fields=json.dumps(data))
		print response
                logging.info(response)
                assert re.search(r'notification:rest:endpoint',response)
                print("Test Case 24 Execution Completed")

        @pytest.mark.run(order=25)
        def test_025_REST_API_endpoint_Test_Connection_Validation(self):
                logging.info("REST_API Endpoint Test Connection Validation")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rest:endpoint?name=Endpoint")
                print(get_ref)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                response = ib_NIOS.wapi_request('POST', object_type=ref1+"?_function=test_connection")
                print response
                logging.info(response)
                sleep(20)
                assert re.search(r'"overall_status": "SUCCESS"',response)
                print("Test Case 25 Execution Completed")

	@pytest.mark.run(order=26)
        def test_026_Verify_Session_Template_in_REST_API_Endpoint(self):
                logging.info("Verify Session template in REST API Endpoint")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rest:endpoint?_return_fields=name,template_instance",grid_vip=config.grid_vip)
                print("response    : ",response)
                if('"name": "Endpoint"'in response) and ('"template": "Version5_REST_API_Session_Template"' in response):
                         assert True
                else:
                         assert False
                sleep(2)
                logging.info("Test Case 26 Execution Completed")
	
	@pytest.mark.run(order=27)
        def test_027_Capture_Template_execution_logs_While_Creating_Host_Record(self):
                logging.info("Capture Template execution logs While Creating_Host Record")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(5)
                data={"ipv4addrs": [{"configure_for_dhcp": False,"ipv4addr": "10.1.1.1","mac": "22:22:22:22:22:22"}],"name": "a.outbound.com","view": "default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data))
                print response
                logging.info(response)
                assert re.search(r'a.outbound.com',response)
                sleep(10)
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(5)
                logging.info("Test Case 27 Execution Completed")

        @pytest.mark.run(order=28)
        def test_028_looking_for_Template_execution_Status(self):
                logging.info("looking_for_Templated_Execution_Status")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("template was executed successfully")
                    assert True
                else:
                    print("template was not executed")
                    assert False
                sleep(5)
                print("Test Case 28 Execution Completed")

	#This test case is the exact issue of the bug
	@pytest.mark.run(order=29)
        def test_029_Capture_Template_execution_logs_While_updating_Host_Record_With_NULL_Parameters(self):
                logging.info("Capture_Template_execution_logs_While Updating_Host Record With_NULL_Parameters")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(5)
                get_ref = ib_NIOS.wapi_request('GET',object_type="record:host?name=a.outbound.com")
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                data={}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert re.search(r'a.outbound.com',response)
                sleep(10)
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(5)
                logging.info("Test Case 29 Execution Completed")

        @pytest.mark.run(order=30)
        def test_030_looking_for_Template_execution_Status_Negative(self):
                logging.info("looking for Templated_Execution_Status Negative")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)==0):
                    print("template was Not executed which is expected")
                    assert True
                else:
                    print("template was executed which is not expected")
                    assert False
		sleep(5)
                print("Test Case 30 Execution Completed")	
	
	@pytest.mark.run(order=31)
        def test_031_Capture_Template_execution_logs_While_updating_Host_mac_Address(self):
                logging.info("Capture_Template_execution_logs_While Updating_Host mac address")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(5)
                get_ref = ib_NIOS.wapi_request('GET',object_type="record:host?name=a.outbound.com")
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                data={"ipv4addrs": [{"configure_for_dhcp": False,"ipv4addr": "10.1.1.1","mac": "22:22:22:22:22:11"}]}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert re.search(r'a.outbound.com',response)
                sleep(5)
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(5)
                logging.info("Test Case 31 Execution Completed")

        @pytest.mark.run(order=32)
        def test_032_looking_for_Template_execution_Status(self):
                logging.info("looking_for_Templated_Execution_Status")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("template was executed successfully")
                    assert True
                else:
                    print("template was not executed")
                    assert False
                sleep(5)
                print("Test Case 32 Execution Completed")
	
	@pytest.mark.run(order=33)
        def test_033_Capture_Template_execution_logs_While_doing_GET_Operation(self):
                logging.info("Capture_Template_execution_logs_While_doing_GET_Host")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(5)
                response = ib_NIOS.wapi_request('GET', object_type="record:host?name=a.outbound.com")
                print response
                logging.info(response)
                assert re.search(r'a.outbound.com',response)
                sleep(10)
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(5)
                logging.info("Test Case 33 Execution Completed")

        @pytest.mark.run(order=34)
        def test_034_looking_for_Template_execution_Status_Negative(self):
                logging.info("looking_for_Templated_Execution_Status Negative")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)==0):
                    print("template was Not executed which is expected")
                    assert True
                else:
                    print("template was executed which is not expected")
                    assert False
		sleep(5)
                print("Test Case 34 Execution Completed")

	@pytest.mark.run(order=35)
        def test_035_Capture_Template_execution_logs_While_Deleting_Host_address(self):
                logging.info("Capture_Template_execution_logs_While_Deleting_Host address")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(5)
                get_ref = ib_NIOS.wapi_request('GET',object_type="record:host?name=a.outbound.com")
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                response = ib_NIOS.wapi_request('DELETE', object_type=ref1)
                print response
                logging.info(response)
                assert re.search(r'a.outbound.com',response)
                sleep(10)
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(5)
                logging.info("Test Case 35 Execution Completed")

        @pytest.mark.run(order=36)
        def test_036_looking_for_Template_execution_Status(self):
                logging.info("looking_for_Templated_Execution_Status")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("template was executed successfully")
                    assert True
                else:
                    print("template was not executed")
                    assert False
                sleep(5)
                print("Test Case 36 Execution Completed")

	
        @pytest.mark.run(order=37)
        def test_037_Deleting_Auth_Zone(self):
                logging.info("Deleting Auth zone outbound")
                get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth?fqdn=outbound.com")
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                response = ib_NIOS.wapi_request('DELETE', object_type=ref1)
                print response
                logging.info(response)
                assert re.search(r'outbound.com',response)
                sleep(5)
                print("Restart DNS Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20)
                logging.info("Test Case 37 Execution Completed")

        @pytest.mark.run(order=38)
        def test_038_Deleting_Notification_Rule(self):
                logging.info("Deleting Notification Rule")
                get_ref = ib_NIOS.wapi_request('GET',object_type="notification:rule?name=Test")
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                response = ib_NIOS.wapi_request('DELETE', object_type=ref1)
                print response
                logging.info(response)
                assert re.search(r'Test',response)
                sleep(5)
                logging.info("Test Case 38 Execution Completed")
        
        @pytest.mark.run(order=39)
        def test_039_Deleting_Endpoint(self):
                logging.info("Deleting Endpoint")
                get_ref = ib_NIOS.wapi_request('GET',object_type="notification:rest:endpoint?name=Endpoint")
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                response = ib_NIOS.wapi_request('DELETE', object_type=ref1)
                print response
                logging.info(response)
                assert re.search(r'Endpoint',response)
                sleep(5)
                logging.info("Test Case 39 Execution Completed")

        @pytest.mark.run(order=40)
        def test_040_Deleting_Event_Template(self):
                logging.info("Deleting_Template")
                get_ref = ib_NIOS.wapi_request('GET',object_type="notification:rest:template?name=Version5_DNS_Zone_and_Records_Action_Template")
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                response = ib_NIOS.wapi_request('DELETE', object_type=ref1)
                print response
                logging.info(response)
                assert re.search(r'Version5_DNS_Zone_and_Records_Action_Template',response)
                sleep(5)
                logging.info("Test Case 40 Execution Completed")

	@pytest.mark.run(order=41)
        def test_041_Deleting_Session_Template(self):
                logging.info("Deleting Session Template")
                get_ref = ib_NIOS.wapi_request('GET',object_type="notification:rest:template?name=Version5_REST_API_Session_Template")
                res = json.loads(get_ref)
		print(res)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                response = ib_NIOS.wapi_request('DELETE', object_type=ref1)
                print response
                logging.info(response)
                assert re.search(r'Version5_REST_API_Session_Template',response)
                sleep(5)
                logging.info("Test Case 41 Execution Completed")

        @pytest.mark.run(order=42)
        def test_042_Stop_DNS_Service(self):
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
                print("Test Case 42 Execution Completed")

        @pytest.mark.run(order=43)
        def test_043_Validate_DNS_service_Disabled(self):
                logging.info("Validate disable DNS Service ")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                for i in res:
                        print i
                        logging.info("found")
                        assert i["enable_dns"] == False
                print("Test Case 43 Execution Completed")
                

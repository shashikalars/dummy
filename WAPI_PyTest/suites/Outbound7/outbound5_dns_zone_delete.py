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
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv

class Outbound(unittest.TestCase):

#Starting DNS service

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

#Adding Forwarder

	@pytest.mark.run(order=3)
	def test_003_Configure_Global_Forwarders_Logging_Categories_Allow_Recursion_At_Grid_level(self):
		logging.info("Configure Global Forwarders Logging Categories Allow Recursion at Grid level")
		get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
		logging.info(get_ref)
		res = json.loads(get_ref)
		ref1 = json.loads(get_ref)[0]['_ref']
		print ref1

		logging.info("Modify Grid DNS Properties")
		data = {"allow_recursive_query": True,"forwarders": [config.dns_forwarder],"logging_categories": {"log_queries": True,"log_responses": True,"log_rpz": True}}
		response = ib_NIOS.wapi_request('PUT',ref= ref1,fields=json.dumps(data))
		print response
		logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 3 Execution Completed")

	@pytest.mark.run(order=4)
        def test_004_Validate_Global_Forwarders_Logging_Categories_Allow_Recursion_At_Grid_level(self):
                logging.info("Validate Configured Global Forwarders Logging Categories Allow Recursion at Grid level")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="grid:dns",params="?_return_fields=allow_recursive_query,forwarders")
                res = json.loads(get_tacacsplus)
                res = eval(json.dumps(get_tacacsplus))
                print(res)
                output=res.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                print(output)
                result = ['allow_recursive_query:true','forwarders:['+config.dns_forwarder+']']
                for i in result:
                  if i in output:
                        assert True
                  else:
                        assert False
                print(result)
		logging.info("Test Case 4 Execution Completed")
                logging.info("============================")


#Upload Templates

	@pytest.mark.run(order=5)
        def test_005_Upload_REST_API_Session_Template(self):
                logging.info("Upload REST API Version5 Session Template")
                #dir_name="/import/qaddi/API_Automation_26_09/WAPI_PyTest/suites/Outbound7/Outbound5_templates"
                base_filename="Version5_REST_API_Session_Template.json"
		dir_name = os.getcwd()
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
                print("Test Case 5 Execution Completed")

	@pytest.mark.run(order=6)
        def test_006_Validate_Adding_REST_API_Session_Template(self):
                logging.info("Validating Adding REST API Session Template")
                data = {"name": "Version5_REST_API_Session_Template"}
                get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rest:template",params="?_inheritance=True&_return_fields=name,template_type")
                logging.info(get_temp)
                res=json.loads(get_temp)
		res = eval(json.dumps(res))
                print(res)
		res = ''.join(map(str, res))
		output = ["'name': 'Version5_REST_API_Session_Template'","'template_type': 'REST_ENDPOINT'"]
		for values in output:
                	if values in res:
                        	assert True
                	else:
                        	assert False
		print(output)
                print("Test Case 6 Execution Completed")
                sleep(5)

	
        @pytest.mark.run(order=7)
        def test_007_Upload_DNS_Records_Event_Template(self):
                logging.info("Upload DNS RECORDS Version5 Event Template")
                #dir_name="/import/qaddi/API_Automation_26_09/WAPI_PyTest/suites/Outbound7/Outbound5_templates"
                base_filename="Version5_DNS_Zone_and_Records_Action_Template.json"
		dir_name = os.getcwd()
                token = common_util.generate_token_from_file(dir_name,base_filename)
                data = {"token": token,"overwrite":True}
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
                print("Test Case 7 Execution Completed")

	@pytest.mark.run(order=8)
        def test_008_Validate_Adding_DNS_Record_Event_Template(self):
                logging.info("Validate adding DNS record event template")
		data = {"name": "Version5_DNS_Zone_and_Records_Action_Template"}
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rest:template",params="?_inheritance=True&_return_fields=name,template_type")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = ["'name': 'Version5_DNS_Zone_and_Records_Action_Template'","'template_type': 'REST_EVENT'"]
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 8 Execution Completed")
                sleep(5)


#Add REST API endpoint
		
	@pytest.mark.run(order=9)
        def test_009_Add_REST_API_endpoint(self):
                logging.info("Add REST API endpoint")
                data = {"name": "rest_api_endpoint1", "uri": "https://"+config.grid_master_vip,"outbound_member_type": "GM","username": "admin","password": "infoblox","wapi_user_name": "admin", "wapi_user_password": "infoblox","template_instance": {"template": "Version5_REST_API_Session_Template"},"server_cert_validation": "NO_VALIDATION","log_level": "DEBUG"}
                response = ib_NIOS.wapi_request('POST', object_type="notification:rest:endpoint", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                sleep(10)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 9 Execution Completed")

	@pytest.mark.run(order=10)
        def test_010_Validating_REST_API_endpoint(self):
                logging.info("Validating REST API endpoint")
		data = {"name": "rest_api_endpoint1", "uri": "https://"+config.grid_master_vip,"outbound_member_type": "GM","username": "admin","password": "infoblox","wapi_user_name": "admin", "wapi_user_password": "infoblox","template_instance": {"template": "Version5_REST_API_Session_Template"},"server_cert_validation": "NO_VALIDATION","log_level": "DEBUG"}
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rest:endpoint",params="?_inheritance=True&_return_fields=name,outbound_member_type,username,wapi_user_name,template_instance,server_cert_validation,log_level")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
		res = ''.join(map(str, res))
                output = ["'name': 'rest_api_endpoint1'","'username': 'admin'", "'wapi_user_name': 'admin'", "'log_level': 'DEBUG'", "'name': 'rest_api_endpoint1'","'outbound_member_type': 'GM'", "'server_cert_validation': 'NO_VALIDATION'", "'template_instance': {'parameters': [], 'template': 'Version5_REST_API_Session_Template'"]
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 10 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=11)
        def test_011_Add_DNS_Zone_Notification_Rule_with_Zone_Type_As_Authoritative(self):
		logging.info("Adding Notification rule with zone type as Authoritative")
                object_type="notification:rest:endpoint"
                data={"name":"rest_api_endpoint1"}
                get_ref = common_util.get_object_reference(object_type,data)
                print "========================="
                print get_ref
                data = {"name": "dns_notify1","notification_action": "RESTAPI_TEMPLATE_INSTANCE", "notification_target": get_ref,"template_instance": {"template": "Version5_DNS_Zone_and_Records_Action_Template"},"event_type": "DB_CHANGE_DNS_ZONE","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_AUTHORITATIVE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('POST', object_type="notification:rule", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
		sleep(5)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 11 Execution Completed")

	@pytest.mark.run(order=12)
        def test_012_Validate_Adding_Notification_Rule_with_zone_type_as_Authoritative(self):
                logging.info("Validating Addition of Notification rule with zone type as Authoritative")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=name,expression_list,notification_action,notification_target,template_instance")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = ["'template_instance': {'parameters': [], 'template': 'Version5_DNS_Zone_and_Records_Action_Template'}", "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_AUTHORITATIVE', 'op1': 'ZONE_TYPE'}, {'op': 'ENDLIST'}]","'notification_action': 'RESTAPI_TEMPLATE_INSTANCE'", "'name': 'dns_notify1'"]
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 12 Execution Completed")
                sleep(5)

#Add and validate all types of Authoritative Zones

	@pytest.mark.run(order=13)
        def test_013_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 13 Execution Completed")
	

	@pytest.mark.run(order=14)
	def test_014_Add_Authoritative_zone(self):
                logging.info("Create Auth Zone")
                grid_member=config.grid_fqdn
                data = {"fqdn": "outbound_zone2.com","grid_primary": [{"name":config.grid_fqdn,"stealth":False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 14 Execution Completed")

		logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
		print("System Restart is done successfully")
		sleep(5)

	@pytest.mark.run(order=15)
        def test_015_Stopping_Logs_for_Template_Execution(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 15 Execution Completed")


	@pytest.mark.run(order=16)
        def test_016_validate_Worker_logs_to_check_Template_for_Auth_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution for Auth Zone in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print (result)
                print("Test Case 16 Execution Completed")

	@pytest.mark.run(order=17)
        def test_017_Update_Notification_rule_for_Authoritative_zone_with_match_rule_as_Modify(self):
                logging.info("Update notification rule for Authoritative zone with match rule as Modify")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_AUTHORITATIVE","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "MODIFY","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 17 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=18)
        def test_018_Validate_Notification_rule_for_Authoritative_zone_with_match_rule_as_Modify(self):
                logging.info("Validating notification rule for Authoritative zone with match rule as Modify")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
		output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}","{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_AUTHORITATIVE', 'op1': 'ZONE_TYPE'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'MODIFY', 'op1': 'OPERATION_TYPE'}","{'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
		sleep(5)
                print("Test Case 18 Execution Completed")

	@pytest.mark.run(order=19)
        def test_019_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 19 Execution Completed")
	
	@pytest.mark.run(order=20)
        def test_020_Update_Authoritative_zone(self):
                logging.info("Update Auth Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify Auth Zone")
                data = {"comment": "test"}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 20 Execution Completed")
		sleep(5)

	@pytest.mark.run(order=21)
        def test_021_Stopping_Logs_for_Template_Execution(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 21 Execution Completed")


        @pytest.mark.run(order=22)
        def test_022_validate_Worker_logs_to_check_Template_for_Auth_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution for Auth Zone in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print (result)
                print("Test Case 22 Execution Completed")

	@pytest.mark.run(order=23)
        def test_023_Update_Notification_rule_for_Authoritative_zone_with_match_rule_as_DELETE(self):
                logging.info("Update notification rule for Authoritative zone with match rule as DELETE")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_AUTHORITATIVE","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 23 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=24)
        def test_024_Validate_Notification_rule_for_Authoritative_zone_with_match_rule_as_delete(self):
                logging.info("Validating notification rule for Authoritative zone with match rule as delete")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}","{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_AUTHORITATIVE', 'op1': 'ZONE_TYPE'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}","{'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 24 Execution Completed")
                sleep(5)


	@pytest.mark.run(order=25)
        def test_025_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 25 Execution Completed")

	@pytest.mark.run(order=26)
        def test_026_Delete_Authzone_After_executing_Template(self):
                logging.info("Deleting Authzone after executing template")
                data= {"fqdn": "outbound_zone2.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
                sleep(5)
		print("Test Case 26 Execution Completed")

	@pytest.mark.run(order=27)
        def test_027_Stopping_Logs_for_Template_Execution(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 27 Execution Completed")

	@pytest.mark.run(order=28)
        def test_028_validate_Worker_logs_to_check_Template_for_Auth_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution for Auth Zone in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print (result)
                print("Test Case 28 Execution Completed")

	@pytest.mark.run(order=29)
        def test_029_Update_Notification_rule_for_IPV4_Authoritative_zone_with_match_rule_as_INSERT(self):
                logging.info("Update notification rule for IPv4 Authoritative zone with match rule as INSERT")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_AUTHORITATIVE","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "INSERT","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 29 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=30)
        def test_030_validate_Notification_rule_for_IPV4_Authoritative_zone_with_match_rule_as_INSERT(self):
                logging.info("Validating notification rule for IPv4 Authoritative zone with match rule as insert")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}","{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_AUTHORITATIVE', 'op1': 'ZONE_TYPE'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'INSERT', 'op1': 'OPERATION_TYPE'}","{'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 30 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=31)
	def test_031_start_Worker_logs_to_check_IPv4_Auth_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 31 Execution Completed")


	@pytest.mark.run(order=32)
        def test_032_Add_IPv4_Authoritative_zone(self):
                logging.info("Create IPv4 Auth Zone")
                grid_member=config.grid_fqdn
                data = {"fqdn": "10.35.103.0/24","zone_format": "IPV4","grid_primary": [{"name":config.grid_fqdn,"stealth":False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 32 Execution Completed")

		logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")
		sleep(10)

	@pytest.mark.run(order=33)
        def test_033_stop_Worker_logs_to_check_IPv4_Auth_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 33 Execution Completed")

	@pytest.mark.run(order=34)
        def test_034_validate_Worker_logs_to_check_Template_for_IPv4_Auth_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution for Auth Zone in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 34 Execution Completed")
	
	@pytest.mark.run(order=35)
        def test_035_Update_Notification_rule_for_IPv4_Authoritative_zone_with_match_rule_as_Modify(self):
                logging.info("Update Auth Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_AUTHORITATIVE","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "MODIFY","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 35 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=36)
        def test_036_validate_Notification_rule_for_IPV4_Authoritative_zone_with_match_rule_as_modify(self):
                logging.info("Validating notification rule for IPv4 Authoritative zone with match rule as modify")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}","{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_AUTHORITATIVE', 'op1': 'ZONE_TYPE'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'MODIFY', 'op1': 'OPERATION_TYPE'}","{'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 36 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=37)
        def test_037_start_Worker_logs_to_check_IPv4_Auth_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 37 Execution Completed")


	@pytest.mark.run(order=38)
        def test_038_Update_IPv4_Authoritative_zone(self):
                logging.info("Update IPv4 Auth Zone")
		data= {"fqdn": "10.35.103.0/24"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify Auth Zone")
                data = {"comment": "test"}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 38 Execution Completed")
		sleep(5)

	@pytest.mark.run(order=39)
        def test_039_stop_Worker_logs_to_check_IPv4_Auth_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 39 Execution Completed")

	@pytest.mark.run(order=40)
        def test_040_validate_Worker_logs_to_check_Template_for_IPv4_Auth_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution for Auth Zone in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 40 Execution Completed")

	@pytest.mark.run(order=41)
        def test_041_Update_Notification_rule_for_IPv4_Authoritative_zone_with_match_rule_as_DELETE(self):
                logging.info("Update notification rule for IPv4 Authzone with match rule as DELETE")
		get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_AUTHORITATIVE","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 41 Execution Completed")
                sleep(5)


	@pytest.mark.run(order=42)
        def test_042_validate_Notification_rule_for_IPV4_Authoritative_zone_with_match_rule_as_delete(self):
                logging.info("Validating notification rule for IPv4 Authoritative zone with match rule as delete")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}","{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_AUTHORITATIVE', 'op1': 'ZONE_TYPE'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}","{'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 42 Execution Completed")
                sleep(5)


	@pytest.mark.run(order=43)
        def test_043_start_Worker_logs_to_check_IPv4_Auth_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 43 Execution Completed")

	@pytest.mark.run(order=44)
        def test_044_Delete_Authzone_After_executing_Template(self):
                logging.info("Deleting Authzone after executing template")
                data= {"fqdn": "10.35.103.0/24"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
		print("Test Case 44 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=45)
        def test_045_stop_Worker_logs_to_check_IPv4_Auth_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 45 Execution Completed")

	@pytest.mark.run(order=46)
        def test_046_validate_Worker_logs_to_check_Template_for_IPv4_Auth_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution for Auth Zone in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 46 Execution Completed")

	@pytest.mark.run(order=47)
        def test_047_Update_Notification_rule_for_IPv6_Authoritative_zone_with_match_rule_as_INSERT(self):
                logging.info("Update notification rule for IPv6 Authzone with match rule as INSERT")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_AUTHORITATIVE","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "INSERT","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 47 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=48)
        def test_048_validate_Notification_rule_for_IPv6_Authoritative_zone_with_match_rule_as_insert(self):
                logging.info("Validating notification rule for IPv6 Authoritative zone with match rule as insert")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}","{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_AUTHORITATIVE', 'op1': 'ZONE_TYPE'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'INSERT', 'op1': 'OPERATION_TYPE'}","{'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 48 Execution Completed")
                sleep(5)


	@pytest.mark.run(order=49)
        def test_049_start_Worker_logs_to_check_IPv6_Auth_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 49 Execution Completed")

	@pytest.mark.run(order=50)
        def test_050_Add_IPv6_Authoritative_zone(self):
                logging.info("Create IPv6 Auth Zone")
                grid_member=config.grid_fqdn
                data = {"fqdn": "2620:10a:6000:7814::5b/128","zone_format": "IPV6","grid_primary": [{"name":config.grid_fqdn,"stealth":False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 50 Execution Completed")

		logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")
                sleep(10)

	@pytest.mark.run(order=51)
        def test_051_stop_Worker_logs_to_check_IPv6_Auth_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 51 Execution Completed")

	@pytest.mark.run(order=52)
        def test_052_validate_Worker_logs_to_check_Template_for_IPv6_Auth_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution for Auth Zone in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 52 Execution Completed")

	@pytest.mark.run(order=53)
        def test_053_Update_Notification_rule_for_IPv6_Authoritative_zone_with_match_rule_as_Modify(self):
		logging.info("Update notification for IPv6 Authzone with match rule as Modify")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_AUTHORITATIVE","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "MODIFY","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 53 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=54)
        def test_054_validate_Notification_rule_for_IPv6_Authoritative_zone_with_match_rule_as_modify(self):
                logging.info("Validating notification rule for IPv6 Authoritative zone with match rule as modify")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}","{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_AUTHORITATIVE', 'op1': 'ZONE_TYPE'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'MODIFY', 'op1': 'OPERATION_TYPE'}","{'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 54 Execution Completed")
                sleep(5)


	@pytest.mark.run(order=55)
        def test_055_start_Worker_logs_to_check_IPv6_Auth_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 55 Execution Completed")

	@pytest.mark.run(order=56)
        def test_056_Update_IPv6_Authoritative_zone(self):
                logging.info("Update Auth Zone")
		data= {"fqdn": "2620:10a:6000:7814::5b/128"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"comment": "test"}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 56 Execution Completed")
		sleep(10)

	@pytest.mark.run(order=57)
        def test_057_stop_Worker_logs_to_check_IPv6_Auth_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 57 Execution Completed")

	@pytest.mark.run(order=58)
        def test_058_validate_Worker_logs_to_check_Template_for_Auth_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution for Auth Zone in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 58 Execution Completed")

	@pytest.mark.run(order=59)
        def test_059_Update_Notification_rule_for_IPv6_Authoritative_zone_with_match_rule_as_DELETE(self):
                logging.info("Update notification rule for IPv6 Authzone with match rule as DELETE")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_AUTHORITATIVE","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 59 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=60)
        def test_060_validate_Notification_rule_for_IPv6_Authoritative_zone_with_match_rule_as_delete(self):
                logging.info("Validating notification rule for IPv6 Authoritative zone with match rule as delete")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}","{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_AUTHORITATIVE', 'op1': 'ZONE_TYPE'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}","{'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
		print(output)
		print("Test Case 60 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=61)
        def test_061_start_Worker_logs_to_check_IPv6_Auth_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 61 Execution Completed")

	@pytest.mark.run(order=62)
        def test_062_Delete_Authzone_After_executing_Template(self):
                logging.info("Deleting IPv6 Authzone after executing template")
                data= {"fqdn": "2620:10a:6000:7814::5b/128"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
		print("Test Case 62 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=63)
        def test_063_stop_Worker_logs_to_check_IPv6_Auth_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 63 Execution Completed")

	@pytest.mark.run(order=64)
        def test_064_validate_Worker_logs_to_check_Template_for_IPv6_Auth_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution for Auth Zone in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 64 Execution Completed")


	@pytest.mark.run(order=65)
        def test_065_Update_DNS_Zone_Notification_Rule_with_Zone_Type_As_Stub_and_match_rule_as_INSERT(self):
                logging.info("Notification rule for Stub Zone and match rule as INSERT")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_STUB","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "INSERT","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 65 Execution Completed")
		sleep(5)

	@pytest.mark.run(order=66)
        def test_066_Validate_updating_Notification_Rule_for_stub_zone_with_match_rule_as_INSERT(self):
                logging.info("Validating update Notification rule with zone type as stub and match rule as INSERT")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}","{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_STUB', 'op1': 'ZONE_TYPE'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'INSERT', 'op1': 'OPERATION_TYPE'}","{'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                sleep(5)

##Add and validate all types of stub Zones

	@pytest.mark.run(order=67)
        def test_067_start_Worker_logs_to_check_stub_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 67 Execution Completed")

	@pytest.mark.run(order=68)
	def test_068_Add_stub_zone(self):
                logging.info("Create stub Zone")
                grid_member=config.grid_fqdn
                data = {"fqdn": "stub.outbound_zone2.com","stub_from": [{"address":config.grid_vip,"name":config.grid_fqdn}],"stub_members":[{"name":config.grid_member1_fqdn}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_stub", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 68 Execution Completed")
		
		logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")
                sleep(10)

	@pytest.mark.run(order=69)
        def test_069_stop_Worker_logs_to_check_stub_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 69 Execution Completed")

	@pytest.mark.run(order=70)
        def test_070_validate_Worker_logs_to_check_Template_for_stub_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution for Auth Zone in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 70 Execution Completed")

	@pytest.mark.run(order=71)
        def test_071_Update_Notification_rule_for_IPv4_stub_zone_with_match_rule_as_Modify(self):
                logging.info("Update notification rule for IPv4 stub zone with match rule as MODIFY")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_STUB","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "MODIFY","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 71 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=72)
        def test_072_Validate_updating_Notification_Rule_for_stub_zone_with_match_rule_as_modify(self):
                logging.info("Validating update Notification rule with zone type as stub and match rule as modify")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}","{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_STUB', 'op1': 'ZONE_TYPE'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'MODIFY', 'op1': 'OPERATION_TYPE'}","{'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 72 Execution Completed")
                sleep(5)


	@pytest.mark.run(order=73)
        def test_073_start_Worker_logs_to_check_stub_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 73 Execution Completed")

	@pytest.mark.run(order=74)
        def test_074_Update_stub_zone(self):
                logging.info("Update Stub Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_stub")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify stub Zone")
                data = {"comment": "test"}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 74 Execution Completed")
		sleep(5)

	@pytest.mark.run(order=75)
        def test_075_stop_Worker_logs_to_check_stub_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 75 Execution Completed")

	@pytest.mark.run(order=76)
        def test_076_validate_Worker_logs_to_check_Template_for_stub_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution for stub Zone in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 76 Execution Completed")

	@pytest.mark.run(order=77)
        def test_077_Update_Notification_rule_for_STUB_zone_with_match_rule_as_DELETE(self):
                logging.info("Update notification rule for stub zone with match rule as DELETE")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_STUB","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 77 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=78)
        def test_078_Validate_updating_Notification_Rule_for_stub_zone_with_match_rule_as_delete(self):
                logging.info("Validating update Notification rule with zone type as stub and match rule as delete")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}","{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_STUB', 'op1': 'ZONE_TYPE'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}","{'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 78 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=79)
        def test_079_start_Worker_logs_to_check_stub_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 79 Execution Completed")

	@pytest.mark.run(order=80)
        def test_080_Delete_stubzone_After_executing_Template(self):
                logging.info("Deleting stub zone after executing template")
                data= {"fqdn": "stub.outbound_zone2.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_stub",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
		print("Test Case 80 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=81)
        def test_081_stop_Worker_logs_to_check_stub_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 81 Execution Completed")

	@pytest.mark.run(order=82)
        def test_082_validate_Worker_logs_to_check_Template_for_stub_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution for Auth Zone in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 82 Execution Completed")

	
	@pytest.mark.run(order=83)
        def test_083_Update_Notification_rule_for_IPv4_stubzone_with_match_rule_as_modify(self):
                logging.info("Update notification rule for IPv4 stub zone with match rule as modify")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_STUB","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "INSERT","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 83 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=84)
        def test_084_Validate_updating_Notification_Rule_for_IPv4_stub_zone_with_match_rule_as_insert(self):
                logging.info("Validating update Notification rule with zone type as IPv4 stub and match rule as insert")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}","{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_STUB', 'op1': 'ZONE_TYPE'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'INSERT', 'op1': 'OPERATION_TYPE'}","{'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 84 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=85)
        def test_085_start_Worker_logs_to_check_IPv4_stub_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 85 Execution Completed")

	@pytest.mark.run(order=86)
        def test_086_Add_IPv4_stub_zone(self):
                logging.info("Create IPv4 stub Zone")
                grid_member=config.grid_fqdn
                data = {"fqdn": "10.35.34.0/24","zone_format": "IPV4","stub_from": [{"address":config.grid_vip,"name":config.grid_fqdn}],"stub_members":[{"name":config.grid_member1_fqdn}],"view": "default"}
                response = ib_NIOS.wapi_request('POST', object_type="zone_stub", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 86 Execution Completed")

		logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")
                sleep(10)

	@pytest.mark.run(order=87)
        def test_087_stop_Worker_logs_to_check_IPv4_stub_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 87 Execution Completed")


	@pytest.mark.run(order=88)
        def test_088_validate_Worker_logs_to_check_Template_for_IPv4_stub_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution for Auth Zone in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 88 Execution Completed")

	@pytest.mark.run(order=89)
        def test_089_Update_Notification_rule_for_IPv4_stub_zone_with_match_rule_as_Modify(self):
                logging.info("Update notification rule for IPv4 stub zone with match rule as MODIFY")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_STUB","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "MODIFY","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 89 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=90)
        def test_090_Validate_updating_Notification_Rule_for_IPv4_stub_zone_with_match_rule_as_modify(self):
                logging.info("Validating update Notification rule with zone type as IPv4 stub and match rule as modify")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}","{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_STUB', 'op1': 'ZONE_TYPE'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'MODIFY', 'op1': 'OPERATION_TYPE'}","{'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 90 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=91)
        def test_091_start_Worker_logs_to_check_IPv4_stub_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 91 Execution Completed")

	@pytest.mark.run(order=92)
	def test_092_Update_IPv4_stub_zone(self):
                logging.info("Update IPv4 Stub Zone")
		data={"fqdn": "10.35.34.0/24"}
                get_ref = ib_NIOS.wapi_request('GET',object_type="zone_stub",fields=json.dumps(data))
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify stub Zone")
                data = {"comment": "test"}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 92 Execution Completed")

	@pytest.mark.run(order=93)
        def test_093_stop_Worker_logs_to_check_IPv4_stub_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 93 Execution Completed")

	@pytest.mark.run(order=94)
        def test_094_validate_Worker_logs_to_check_Template_for_IPv4_stub_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution for Auth Zone in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 94 Execution Completed")

	@pytest.mark.run(order=95)
        def test_095_Update_Notification_rule_for_IPv4_stub_zone_with_match_rule_as_DELETE(self):
                logging.info("Update Auth Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_STUB","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 95 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=96)
        def test_096_Validate_updating_Notification_Rule_for_IPv4_stub_zone_with_match_rule_as_delete(self):
                logging.info("Validating update Notification rule with zone type as IPv4 stub and match rule as delete")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}","{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_STUB', 'op1': 'ZONE_TYPE'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}","{'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 96 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=97)
        def test_097_start_Worker_logs_to_check_IPv4_stub_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 97 Execution Completed")

	@pytest.mark.run(order=98)
        def test_098_Delete_IPv4_stubzone_After_executing_Template(self):
                logging.info("Deleting IPv4 stub zone after executing template")
                data= {"fqdn": "10.35.34.0/24"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_stub",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
		print("Test Case 98 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=99)
        def test_099_stop_Worker_logs_to_check_IPv4_stub_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 99 Execution Completed")

	@pytest.mark.run(order=100)
        def test_100_validate_Worker_logs_to_check_Template_for_Auth_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution for Auth Zone in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 100 Execution Completed")

	@pytest.mark.run(order=101)
        def test_101_Update_Notification_rule_for_IPv6_stub_zone_with_match_rule_as_INSERT(self):
                logging.info("Update notification rule for IPv6 stub zone with match rule as Insert")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_STUB","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "INSERT","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 101 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=102)
        def test_102_Validate_updating_Notification_Rule_for_IPv4_stub_zone_with_match_rule_as_delete(self):
                logging.info("Validating update Notification rule with zone type as IPv4 stub and match rule as delete")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}","{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_STUB', 'op1': 'ZONE_TYPE'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'INSERT', 'op1': 'OPERATION_TYPE'}","{'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 102 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=103)
        def test_103_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 103 Execution Completed")

        @pytest.mark.run(order=104)
        def test_104_Add_IPv6_stub_zone(self):
                logging.info("Create IPv6 stub Zone")
		grid_member=config.grid_fqdn
                data = {"fqdn": "2620:10a:6000:7814::2e/128","zone_format": "IPV6","stub_from": [{"address":config.grid_vip,"name":config.grid_fqdn}],"stub_members":[{"name":config.grid_member1_fqdn}],"view": "default"}
                response = ib_NIOS.wapi_request('POST', object_type="zone_stub", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 104 Execution Completed")

		logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")
                sleep(10)

	@pytest.mark.run(order=105)
        def test_105_stop_Worker_logs_to_check_IPv6_stub_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 105 Execution Completed")

	@pytest.mark.run(order=106)
        def test_106_validate_Worker_logs_to_check_Template_for_IPv6_stub_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution for Auth Zone in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 106 Execution Completed")

	@pytest.mark.run(order=107)
        def test_107_Update_Notification_rule_for_IPv6_stub_zone_with_match_rule_as_Modify(self):
                logging.info("Update Auth Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_STUB","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "MODIFY","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 107 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=108)
        def test_108_Validate_updating_Notification_Rule_for_IPv6_stub_zone_with_match_rule_as_modify(self):
                logging.info("Validating update Notification rule with zone type as IPv4 stub and match rule as modify")
                print("Test Case 108 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=109)
        def test_109_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 109 Execution Completed")

	@pytest.mark.run(order=110)
        def test_110_Update_IPv6_Stub_zone(self):
                logging.info("Update IPv6 Stub Zone")
		data = {"fqdn": "2620:10a:6000:7814::2e/128"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_stub",fields=json.dumps(data))
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify stub Zone")
                data = {"comment": "test"}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 110 Execution Completed")
		sleep(20)

	@pytest.mark.run(order=111)
        def test_111_stop_Worker_logs_to_check_IPv6_stub_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 111 Execution Completed")

	@pytest.mark.run(order=112)
        def test_112_validate_Worker_logs_to_check_Template_for_IPv6_stub_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution for Auth Zone in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 112 Execution Completed")

	@pytest.mark.run(order=113)
        def test_113_Update_Notification_rule_for_IPv6_stub_zone_with_match_rule_as_DELETE(self):
                logging.info("Update notification rule for IPv6 stub zone with match rule as DELETE")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_STUB","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 113 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=114)
        def test_114_Validate_updating_Notification_Rule_for_IPv6_stub_zone_with_match_rule_as_delete(self):
                logging.info("Validating update Notification rule with zone type as IPv4 stub and match rule as delete")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}","{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_STUB', 'op1': 'ZONE_TYPE'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}","{'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 114 Execution Completed")


	@pytest.mark.run(order=115)
        def test_115_start_Worker_logs_to_check_IPv6_stub_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 115 Execution Completed")

	@pytest.mark.run(order=116)
        def test_116_Delete_IPv6_stub_zone_After_executing_Template(self):
                logging.info("Deleting IPv6 stub zone after executing template")
                data= {"fqdn": "2620:10a:6000:7814::2e/128"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_stub",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
		print("Test Case 116 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=117)
        def test_117_stop_Worker_logs_to_check_IPv6_stub_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 117 Execution Completed")

	@pytest.mark.run(order=118)
        def test_118_validate_Worker_logs_to_check_Template_for_IPv6_stub_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution for Auth Zone in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 118 Execution Completed")
        
	@pytest.mark.run(order=119)
	def test_119_Update_DNS_Zone_Notification_Rule_with_Zone_Type_As_RPZ(self):
                logging.info("Updating Notification rule for RPZ")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_RPZ","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "INSERT","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 119 Execution Completed")
		sleep(5)

	@pytest.mark.run(order=120)
        def test_120_Validate_updating_Notification_Rule(self):
                logging.info("Validating update Notification rule with zone type as RPZ")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}","{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_RPZ', 'op1': 'ZONE_TYPE'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'INSERT', 'op1': 'OPERATION_TYPE'}","{'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 120 Execution Completed")
                sleep(5)

#Add and validate all types of RPZ Zones

	@pytest.mark.run(order=121)
        def test_121_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 121 Execution Completed")

	@pytest.mark.run(order=122)
	def test_122_Add_Local_RPZ_zone(self):
		logging.info("Create Local RPZ Zone")
                grid_member=config.grid_fqdn
                data = {"fqdn":"rpz.com","rpz_type": "LOCAL","grid_primary": [{"name":config.grid_fqdn}],"rpz_severity": "MAJOR","rpz_type": "LOCAL"}
                response = ib_NIOS.wapi_request('POST', object_type="zone_rp", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 122 Execution Completed")

		logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")
                sleep(5)

	@pytest.mark.run(order=123)
        def test_123_stop_Worker_logs_to_check_Local_RPZ_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 123 Execution Completed")

	@pytest.mark.run(order=124)
        def test_124_validate_Worker_logs_to_check_Template_for_Local_RPZ_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 124 Execution Completed")

	@pytest.mark.run(order=125)
        def test_125_Update_Notification_rule_for_Local_RPZ_zone_with_match_rule_as_Modify(self):
                logging.info("Update notification rule for local RPZ zone with match rule as MODIFY")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_RPZ","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "MODIFY","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 125 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=126)
        def test_126_Validate_Notification_rule_for_Local_RPZ_zone_with_match_rule_as_Modify(self):
                logging.info("Validating notification rule for local RPZ zone with match rule as MODIFY")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}","{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_RPZ', 'op1': 'ZONE_TYPE'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'MODIFY', 'op1': 'OPERATION_TYPE'}","{'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 126 Execution Completed")


	@pytest.mark.run(order=127)
        def test_127_start_Worker_logs_to_check_Local_RPZ_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 127 Execution Completed")

	@pytest.mark.run(order=128)
        def test_128_Update_RPZ_Local_zone(self):
                logging.info("Update RPZ Local Zone")
		data = {"fqdn":"rpz.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_rp",fields=json.dumps(data))
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify RPZ Local Zone")
                data = {"comment": "test"}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 128 Execution Completed")
		sleep(5)

	@pytest.mark.run(order=129)
        def test_129_stop_Worker_logs_to_check_Local_RPZ_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 129 Execution Completed")

	@pytest.mark.run(order=130)
        def test_130_validate_Worker_logs_to_check_Template_for_Local_RPZ_zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution for Auth Zone in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 130 Execution Completed")

	@pytest.mark.run(order=131)
        def test_131_Update_Notification_rule_for_Local_RPZ_zone_with_match_rule_as_DELETE(self):
                logging.info("Update notification rule for local RPZ zone with match rule as DELETE")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_RPZ","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 131 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=132)
        def test_132_Validate_Notification_rule_for_Local_RPZ_zone_with_match_rule_as_delete(self):
                logging.info("Validating notification rule for local RPZ zone with match rule as delete")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}","{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_RPZ', 'op1': 'ZONE_TYPE'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}","{'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 132 Execution Completed")


	@pytest.mark.run(order=133)
        def test_133_start_Worker_logs_to_check_Local_RPZ_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 133 Execution Completed")

	@pytest.mark.run(order=134)
        def test_134_Delete_Local_RPZ_Zone_After_executing_Template(self):
                logging.info("Deleting Local RPZ after executing Template")
                data= {"fqdn":"rpz.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_rp",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
		print("Test Case 134 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=135)
        def test_135_stop_Worker_logs_to_check_Local_RPZ_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 135 Execution Completed")

	@pytest.mark.run(order=136)
        def test_136_validate_Worker_logs_to_check_Template_for_Local_RPZ_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 136 Execution Completed")

	@pytest.mark.run(order=137)
        def test_137_Update_Notification_rule_for_RPZ_FireEye_Integrated_zone_with_match_rule_as_INSERT(self):
                logging.info("Update notification rule for RPZ FireEye Integrated zone with match rule as INSERT")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_RPZ","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "INSERT","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 137 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=138)
        def test_138_Validate_Notification_rule_for_RPZ_FireEye_Integrated_zone_with_match_rule_as_INSERT(self):
                logging.info("Validating notification rule for RPZ FireEye Integrated zone with match rule as INSERT")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}","{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_RPZ', 'op1': 'ZONE_TYPE'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'INSERT', 'op1': 'OPERATION_TYPE'}","{'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 138 Execution Completed")

	@pytest.mark.run(order=139)
        def test_139_start_Worker_logs_to_check_RPZ_FireEye_Integrated_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 139 Execution Completed")
	
	@pytest.mark.run(order=140)
	def test_140_Add_RPZ_FireEye_Integrated_zone(self):
		logging.info("Create RPZ FireEye-Integrated Zone")
                grid_member=config.grid_fqdn
                data = {"fqdn":"rpz-fire.com","rpz_type": "FIREEYE","grid_primary": [{"name":config.grid_fqdn}],"rpz_severity": "MAJOR","rpz_type": "FIREEYE","fireeye_rule_mapping": {"apt_override": "NOOVERRIDE","fireeye_alert_mapping": [{"alert_type": "DOMAIN_MATCH","lifetime": 604800,"rpz_rule": "PASSTHRU"},{"alert_type": "INFECTION_MATCH","rpz_rule": "PASSTHRU","lifetime": 86400},{"alert_type": "MALWARE_CALLBACK","rpz_rule": "PASSTHRU","lifetime": 86400},{"alert_type": "MALWARE_OBJECT","rpz_rule": "PASSTHRU","lifetime": 86400},{"alert_type": "WEB_INFECTION","rpz_rule": "PASSTHRU","lifetime": 86400}]}}
                response = ib_NIOS.wapi_request('POST', object_type="zone_rp", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 140 Execution Completed")

		logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")
                sleep(5)

	@pytest.mark.run(order=141)
        def test_141_stop_Worker_logs_to_check_RPZ_FireEye_Integrated_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 141 Execution Completed")

	@pytest.mark.run(order=142)
        def test_142_validate_Worker_logs_to_check_Template_for_RPZ_FireEye_Integrated_zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 142 Execution Completed")

	
	@pytest.mark.run(order=143)
        def test_143_Update_Notification_rule_for_RPZ_FireEye_Integrated_zone_with_match_rule_as_Modify(self):
                logging.info("Update notification rule for RPZ FireEye Integrated zone with match rule as MODIFY")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_RPZ","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "MODIFY","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 143 Execution Completed")
                sleep(2)

	@pytest.mark.run(order=144)
        def test_144_Validate_Notification_rule_for_RPZ_FireEye_Integrated_zone_with_match_rule_as_modify(self):
                logging.info("Validating notification rule for RPZ FireEye Integrated zone with match rule as modify")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}","{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_RPZ', 'op1': 'ZONE_TYPE'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'MODIFY', 'op1': 'OPERATION_TYPE'}","{'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 144 Execution Completed")

	@pytest.mark.run(order=145)
        def test_145_start_Worker_logs_to_check_RPZ_FireEye_Integrated_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 145 Execution Completed")

	@pytest.mark.run(order=146)
        def test_146_Update_RPZ_FireEye_zone(self):
                logging.info("Update RPZFireEye Zone")
		data = {"fqdn":"rpz-fire.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_rp",fields=json.dumps(data))
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify RPZ FireEye Zone")
                data = {"comment": "test"}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 146 Execution Completed")

	@pytest.mark.run(order=147)
        def test_147_stop_Worker_logs_to_check_RPZ_FireEye_Integrated_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 147 Execution Completed")

	@pytest.mark.run(order=148)
        def test_148_validate_Worker_logs_to_check_Template_for_RPZ_FireEye_Integrated_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 148 Execution Completed")

	@pytest.mark.run(order=149)
        def test_149_Update_Notification_rule_for_RPZ_FireEye_Integrated_zone_with_match_rule_as_DELETE(self):
                logging.info("Update notification rule for RPZ FireEye Integrated zone with match rule as Delete")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_RPZ","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 149 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=150)
        def test_150_Validate_Notification_rule_for_RPZ_FireEye_Integrated_zone_with_match_rule_as_delete(self):
                logging.info("Validating notification rule for RPZ FireEye Integrated zone with match rule as delete")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}","{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_RPZ', 'op1': 'ZONE_TYPE'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}","{'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 150 Execution Completed")


	@pytest.mark.run(order=151)
        def test_151_start_Worker_logs_to_check_RPZ_FireEye_Integrated_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 151 Execution Completed")

	@pytest.mark.run(order=152)
        def test_152_Delete_RPZ_FireEye_Integrated_zone_After_executing_Template(self):
                logging.info("Deleting A record created by template")
                data= {"fqdn":"rpz-fire.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_rp",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
		print("Test Case 152 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=153)
        def test_153_stop_Worker_logs_to_check_RPZ_FireEye_Integrated_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 153 Execution Completed")

	@pytest.mark.run(order=154)
        def test_154_validate_Worker_logs_to_check_Template_for_RPZ_FireEye_Integrated_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 154 Execution Completed")


	@pytest.mark.run(order=155)
        def test_155_Update_Notification_rule_for_RPZ_Feed_zone_with_match_rule_as_INSERT(self):
                logging.info("Update notification rule for RPZ Feed Zone with match rule as INSERT")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_RPZ","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "INSERT","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 155 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=156)
        def test_156_Validate_Notification_rule_for_RPZ_Feed_zone_with_match_rule_as_insert(self):
                logging.info("Validating notification rule for RPZ FireEye Integrated zone with match rule as insert")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_RPZ', 'op1': 'ZONE_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'INSERT', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 156 Execution Completed")


	@pytest.mark.run(order=157)
        def test_157_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 157 Execution Completed")

	@pytest.mark.run(order=158)
        def test_158_Add_RPZ_Feed_zone(self):
		logging.info("Create RPZ Feed Zone")
		grid_member=config.grid_fqdn
		data = {"fqdn":"rpz-feed.com","rpz_type": "FEED","external_primaries": [{"address": "10.35.169.2","name": "external.com","stealth": False}],"grid_secondaries": [{"enable_preferred_primaries": False,"grid_replicate": False,"lead": False,"name":config.grid_fqdn}],"rpz_type": "FEED","use_external_primary": True}
		response = ib_NIOS.wapi_request('POST', object_type="zone_rp", fields=json.dumps(data))
		res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 158 Execution Completed")

		logging.info("Restart services")
		grid =  ib_NIOS.wapi_request('GET', object_type="grid")
		ref = json.loads(grid)[0]['_ref']
		publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("DNS service restarted")
		sleep(5)
	
	@pytest.mark.run(order=159)
        def test_159_stop_Worker_logs_to_check_RPZ_Feed_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 159 Execution Completed")

	@pytest.mark.run(order=160)
        def test_160_validate_Worker_logs_to_check_Template_for_RPZ_Feed_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 160 Execution Completed")

	@pytest.mark.run(order=161)
        def test_161_Update_Notification_rule_for_RPZ_Feed_zone_with_match_rule_as_Modify(self):
                logging.info("Update notification rule for RPZ feed zone with match rule as MODIFY")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_RPZ","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "MODIFY","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 161 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=162)
        def test_162_Validate_Notification_rule_for_RPZ_Feed_zone_with_match_rule_as_modify(self):
                logging.info("Validating Notification_rule_for_RPZ_Feed_zone_with_match_rule_as_modify")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_RPZ', 'op1': 'ZONE_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'MODIFY', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 162 Execution Completed")


	@pytest.mark.run(order=163)
        def test_163_start_Worker_logs_to_check_RPZ_Feed_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 163 Execution Completed")

	@pytest.mark.run(order=164)
        def test_164_Update_RPZ_Feed_zone(self):
                logging.info("Update RPZFeed Zone")
                data = {"fqdn":"rpz-feed.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_rp",fields=json.dumps(data))
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify RPZ Feed Zone")
                data = {"comment": "test"}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 164 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=165)
        def test_165_stop_Worker_logs_to_check_RPZ_feed_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 165 Execution Completed")

	@pytest.mark.run(order=166)
        def test_166_validate_Worker_logs_to_check_Template_for_RPZ_Feed_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
		LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 166 Execution Completed")

	@pytest.mark.run(order=167)
        def test_167_Update_Notification_rule_for_RPZ_Feed_zone_with_match_rule_as_DELETE_and_ends_with(self):
                logging.info("Update notification rule for RPZ Feed Zone with match rule as DELETE and ends with")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_RPZ","op2_type": "STRING"},{"op": "REGEX","op1": "ZONE_NAME","op1_type": "FIELD","op2": "m$","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 167 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=168)
        def test_168_Validate_Notification_rule_for_RPZ_Feed_zone_with_match_rule_as_DELETE_and_ends_with(self):
                logging.info("Validating Notification rule for RPZ Feed zone with match rule as delete and ends with")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_RPZ', 'op1': 'ZONE_TYPE'}", "{'op2_type': 'STRING', 'op': 'REGEX', 'op1_type': 'FIELD', 'op2': 'm$', 'op1': 'ZONE_NAME'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 168 Execution Completed")


	@pytest.mark.run(order=169)
        def test_169_start_Worker_logs_to_check_RPZ_Feed_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 169 Execution Completed")


	@pytest.mark.run(order=170)
        def test_170_Delete_RPZ_Fedd_zone_After_executing_Template(self):
                logging.info("Deleting RPZ Feed zone after executing template")
                data= {"fqdn":"rpz-feed.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_rp",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
                print("Test Case 170 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=171)
        def test_171_stop_Worker_logs_to_check_RPZ_Feed_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 171 Execution Completed")


	@pytest.mark.run(order=172)
        def test_172_validate_Worker_logs_to_check_Template_for_RPZ_Feed_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution for Auth Zone in Outbound_user")
		LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)	
                print("Test Case 172 Execution Completed")

	@pytest.mark.run(order=173)
	def test_173_Update_DNS_Zone_Notification_Rule_with_Zone_Type_As_Forward_with_match_rule_as_INSERT(self):
                logging.info("Notification rule for Forward zone with match rule as INSERT")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify Notification rule")
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_FORWARD","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "INSERT","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 173 Execution Completed")
		sleep(5)

	@pytest.mark.run(order=174)
        def test_174_Validate_DNS_Zone_Notification_Rule_with_Zone_Type_As_Forward_with_match_rule_as_INSERT(self):
                logging.info("Validating update Notification rule with zone type as forward with match rule as INSERT")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_FORWARD', 'op1': 'ZONE_TYPE'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'INSERT', 'op1': 'OPERATION_TYPE'}, {'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 174 Execution Completed")
                sleep(5)

#Add and validate all types of Forward Zones

	@pytest.mark.run(order=175)
        def test_175_start_Worker_logs_to_check_Forward_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 175 Execution Completed")

	@pytest.mark.run(order=176)
        def test_176_Add_Forward_zone(self):
                logging.info("Create Forward Zone")
		grid_member=config.grid_fqdn
		data = {"forward_to": [{"address": "10.35.169.2","name": "forwarder.com"}],"fqdn": "forward.outbound_zone2.com"}
		response = ib_NIOS.wapi_request('POST', object_type= "zone_forward", fields=json.dumps(data))
		res=json.loads(response)
		logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 176 Execution Completed")

                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type= "grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("DNS service restarted")
		sleep(5)

	@pytest.mark.run(order=177)
        def test_177_stop_Worker_logs_to_check_Forward_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 177 Execution Completed")

	@pytest.mark.run(order=178)
        def test_178_validate_Worker_logs_to_check_Template_for_Forward_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution for Auth Zone in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 178 Execution Completed")

	@pytest.mark.run(order=179)
        def test_179_Update_Notification_rule_for_Forward_zone_with_match_rule_as_Modify(self):
                logging.info("Update notification rule for forward zone with match rule as MODIFY")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_FORWARD","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "MODIFY","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 179 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=180)
        def test_180_Validate_Notification_rule_for_Forward_zone_with_match_rule_as_Modify(self):
                logging.info("Validating notification rule for forward zone with match rule as MODIFY")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_FORWARD', 'op1': 'ZONE_TYPE'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'MODIFY', 'op1': 'OPERATION_TYPE'}, {'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 180 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=181)
        def test_181_start_Worker_logs_to_check_Forward_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 181 Execution Completed")

	@pytest.mark.run(order=182)
	def test_182_Update_Forward_zone(self):
		logging.info("Update Forward Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_forward")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify Forward Feed Zone")
                data = {"comment": "test"}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 182 Execution Completed")
		sleep(5)

	@pytest.mark.run(order=183)
        def test_183_stop_Worker_logs_to_check_Forward_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 183 Execution Completed")

	@pytest.mark.run(order=184)
        def test_184_validate_Worker_logs_to_check_Template_for_Forward_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
		LookFor="The template was executed successfully"
                result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 184 Execution Completed")

	@pytest.mark.run(order=185)
        def test_185_Update_Notification_rule_for_Forward_zone_with_match_rule_as_Delete_and_begins_with(self):
                logging.info("Update notification rule for Forward zone with match rule as DELETE and begins with")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_FORWARD","op2_type": "STRING"},{"op": "REGEX","op1": "ZONE_NAME","op1_type": "FIELD","op2": "^f","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 185 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=186)
        def test_186_Validate_Notification_rule_for_Forward_zone_with_match_rule_as_Modify(self):
                logging.info("Validating notification rule for forward zone with match rule as MODIFY")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_FORWARD', 'op1': 'ZONE_TYPE'}", "{'op2_type': 'STRING', 'op': 'REGEX', 'op1_type': 'FIELD', 'op2': '^f', 'op1': 'ZONE_NAME'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 186 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=187)
        def test_187_start_Worker_logs_to_check_Forward_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 187 Execution Completed")
				
	@pytest.mark.run(order=188)
        def test_188_Delete_Forward_zone_After_executing_Template(self):
                logging.info("Deleting Forward zone after executing template")
                data= {"fqdn": "forward.outbound_zone2.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_forward",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
		print("Test Case 188 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=189)
        def test_189_stop_Worker_logs_to_check_Forward_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 189 Execution Completed")

	@pytest.mark.run(order=190)
        def test_190_validate_Worker_logs_to_check_Template_for_Forward_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
                result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 190 Execution Completed")

	@pytest.mark.run(order=191)
        def test_191_Update_Notification_rule_for_IPv4_Forward_zone_with_match_rule_as_Insert(self):
                logging.info("Update notification rule for IPv4 Forward zone with match rule as Insert")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_FORWARD","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "INSERT","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 191 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=192)
        def test_192_Validate_Notification_rule_for_IPv4_Forward_zone_with_match_rule_as_Insert(self):
                logging.info("Validating notification rule for IPv4 Forward zone with match rule as Insert")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_FORWARD', 'op1': 'ZONE_TYPE'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'INSERT', 'op1': 'OPERATION_TYPE'}, {'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 192 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=193)
        def test_193_start_Worker_logs_to_check_IPv4_Forward_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 193 Execution Completed")
	
	@pytest.mark.run(order=194)
        def test_194_Add_IPv4_Forward_zone(self):
                logging.info("Create IPv4 Forward Zone")
                grid_member=config.grid_fqdn
		data = {"forward_to": [{"address": "10.39.16.160","name": "forwarder.com"}],"zone_format": "IPV4","fqdn": "10.2.9.0/24"}
                response = ib_NIOS.wapi_request('POST', object_type= "zone_forward", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in response:
                        assert True
                logging.info("Test Case 194 Execution Completed")

                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type= "grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("DNS service restarted")
		sleep(5)

	@pytest.mark.run(order=195)
        def test_195_stop_Worker_logs_to_check_IPv4_Forward_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 195 Execution Completed")

	@pytest.mark.run(order=196)
        def test_196_validate_Worker_logs_to_check_Template_for_IPv4_Forward_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
                result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 196 Execution Completed")

	@pytest.mark.run(order=197)
        def test_197_Update_Notification_rule_for_IPv4_Forward_zone_with_match_rule_as_Modify(self):
                logging.info("Update Notification rule for IPv4 Forward zone with match_rule as Modify")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_FORWARD","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "MODIFY","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 197 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=198)
        def test_198_Validate_Notification_rule_for_IPv4_Forward_zone_with_match_rule_as_modify(self):
                logging.info("Validating notification rule for IPv4 forward zone with match rule as modify")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_FORWARD', 'op1': 'ZONE_TYPE'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'MODIFY', 'op1': 'OPERATION_TYPE'}, {'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 198 Execution Completed")


	@pytest.mark.run(order=199)
        def test_199_start_Worker_logs_to_check_IPv4_Forward_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 199 Execution Completed")		

	@pytest.mark.run(order=200)
        def test_200_Update_IPv4_Forward_zone(self):
                logging.info("Update IPv4 Forward Zone")
		data= {"fqdn": "10.2.9.0/24"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_forward",fields=json.dumps(data))
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify IPv4 Forward Zone")
                data = {"comment": "test"}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 200 Execution Completed")
		sleep(5)

	@pytest.mark.run(order=201)
        def test_201_stop_Worker_logs_to_check_IPv4_Forward_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		logging.info("Test Case 201 Execution Completed")

	@pytest.mark.run(order=202)
        def test_202_validate_Worker_logs_to_check_Template_for_IPv4_Forward_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
                result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 202 Execution Completed")
		
	@pytest.mark.run(order=203)
        def test_203_Update_Notification_rule_for_IPv4_Forward_zone_with_match_rule_as_Delete(self):
                logging.info("Update notification rule for IPv4 forward zone with match rule as DELETE")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_FORWARD","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 203 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=204)
        def test_204_Validate_Notification_rule_for_IPv4_Forward_zone_with_match_rule_as_delete(self):
                logging.info("Validating notification rule for IPv4 forward zone with match rule as delete")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_FORWARD', 'op1': 'ZONE_TYPE'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}, {'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 204 Execution Completed")


	@pytest.mark.run(order=205)
        def test_205_start_Worker_logs_to_check_IPv4_Forward_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 205 Execution Completed")
	
	@pytest.mark.run(order=206)
        def test_206_Delete_IPv4_Forward_zone_After_executing_Template(self):
                logging.info("Delete IPv4 Forward zone After executing Template")
                data= {"fqdn": "10.2.9.0/24"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_forward",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
		print("Test Case 206 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=207)
        def test_207_stop_Worker_logs_to_check_IPv4_Forward_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 207 Execution Completed")

	@pytest.mark.run(order=208)
        def test_208_validate_Worker_logs_to_check_Template_for_IPv4_Forward_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 208 Execution Completed")

	@pytest.mark.run(order=209)
        def test_209_Update_Notification_rule_for_IPv6_Forward_zone_with_match_rule_as_Insert(self):
                logging.info("Update Auth Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_FORWARD","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "INSERT","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 209 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=210)
        def test_210_Validate_Notification_rule_for_IPv6_Forward_zone_with_match_rule_as_insert(self):
                logging.info("Validating notification rule for IPv6 forward zone with match rule as insert")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_FORWARD', 'op1': 'ZONE_TYPE'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'INSERT', 'op1': 'OPERATION_TYPE'}, {'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 210 Execution Completed")

	@pytest.mark.run(order=211)
        def test_211_start_Worker_logs_to_check_IPv6_Forward_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 211 Execution Completed")

	@pytest.mark.run(order=212)
        def test_212_Add_IPv6_Forward_zone(self):
                logging.info("Create IPv6 Forward Zone")
                grid_member=config.grid_fqdn
		data = {"forward_to": [{"address": "10.39.16.160","name": "forwarder.com"}],"zone_format": "IPV6","fqdn": "2620:10a:6000:7814::2a/128"}
		response = ib_NIOS.wapi_request('POST', object_type= "zone_forward", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 212 Execution Completed")

                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type= "grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("DNS service restarted")
		sleep(5)

	@pytest.mark.run(order=213)
        def test_213_stop_Worker_logs_to_check_IPv6_Forward_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 213 Execution Completed")

	@pytest.mark.run(order=214)
        def test_214_validate_Worker_logs_to_check_Template_for_IPv6_Forward_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 214 Execution Completed")

	@pytest.mark.run(order=215)
        def test_215_Update_Notification_rule_for_IPv6_Forward_zone_with_match_rule_as_Modify(self):
                logging.info("Update notification rule for IPv6 Forward zone with match rule as Modify")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_FORWARD","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "MODIFY","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 215 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=216)
        def test_216_Validate_Notification_rule_for_IPv6_Forward_zone_with_match_rule_as_modify(self):
                logging.info("Validating notification rule for IPv6 forward zone with match rule as modify")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_FORWARD', 'op1': 'ZONE_TYPE'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'MODIFY', 'op1': 'OPERATION_TYPE'}, {'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 216 Execution Completed")


	@pytest.mark.run(order=217)
        def test_217_start_Worker_logs_to_check_IPv6_Forward_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 217 Execution Completed")

	@pytest.mark.run(order=218)
        def test_218_Update_IPv6_Forward_zone(self):
                logging.info("Update IPv6 Forward Zone")
		data= {"fqdn": "2620:10a:6000:7814::2a/128"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_forward",fields=json.dumps(data))
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify IPv6 Forward Zone")
                data = {"comment": "test"}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 218 Execution Completed")
		sleep(5)

	@pytest.mark.run(order=219)
        def test_219_stop_Worker_logs_to_check_IPv6_Forward_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 219 Execution Completed")

	@pytest.mark.run(order=220)
        def test_220_validate_Worker_logs_to_check_Template_for_IPv6_Forward_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 220 Execution Completed")

	@pytest.mark.run(order=221)
        def test_221_Update_Notification_rule_for_IPv6_Forward_zone_with_match_rule_as_Delete(self):
                logging.info("Update notification rule for IPv6 Forward Zone with match rule as Delete")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_FORWARD","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 221 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=222)
        def test_222_Validate_Notification_rule_for_IPv6_Forward_zone_with_match_rule_as_delete(self):
		logging.info("Update notification rule for IPv6 Forward Zone with match rule as Delete")
                get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_FORWARD', 'op1': 'ZONE_TYPE'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}, {'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
		print("Test Case 222 Execution Completed")


	@pytest.mark.run(order=223)
        def test_223_start_Worker_logs_to_check_IPv6_Forward_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 223 Execution Completed")

	@pytest.mark.run(order=224)
        def test_224_Delete_IPv6_Forwardzone_After_executing_Template(self):
                logging.info("Deleting IPv6 Forward zone after executing template")
                data= {"fqdn": "2620:10a:6000:7814::2a/128"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_forward",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
		print("Test Case 224 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=225)
        def test_225_stop_Worker_logs_to_check_IPv6_Forward_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 225 Execution Completed")

	@pytest.mark.run(order=226)
        def test_226_validate_Worker_logs_to_check_Template_for_IPv6_Forward_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 226 Execution Completed")

	@pytest.mark.run(order=227)
        def test_227_Add_Authoritative_zone_Globally(self):
                logging.info("Create Auth Zone")
                grid_member=config.grid_fqdn
                data = {"fqdn": "outbound_zone2.com","grid_primary": [{"name":config.grid_fqdn,"stealth":False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 227 Execution Completed")

                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")

	@pytest.mark.run(order=228)
        def test_228_Validate_addition_of_Authoritative_zone(self):
                logging.info("Validating addition of authoritative zone with match rule as delete")
		get_temp = ib_NIOS.wapi_request('GET', object_type="zone_auth",params="?_inheritance=True&_return_fields=fqdn")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
		res = ''.join(map(str, res))
		print(res)
		data= "'fqdn': 'outbound_zone2.com'"
		if data in res:
			assert True
		else:
                       	assert False
                print("Test Case 228 Execution Completed")
                sleep(5)


	@pytest.mark.run(order=229)
        def test_229_Update_DNS_Zone_Notification_Rule_with_Zone_Type_As_Delegate(self):
                logging.info("Notification rule for Delegated Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify Notification rule")
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_DELEGATED","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 229 Execution Completed")
		sleep(5)

	@pytest.mark.run(order=230)
        def test_230_Validate_Notification_rule_for_delegate_zone_with_match_rule_as_insert(self):
                logging.info("Validating notification rule for delegate zone with match rule as insert")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_DELEGATED', 'op1': 'ZONE_TYPE'}", "{'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 230 Execution Completed")


#Add and validate Delegated Zone


	@pytest.mark.run(order=231)
        def test_231_start_Worker_logs_to_check_Delegated_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 231 Execution Completed")

	@pytest.mark.run(order=232)
        def test_232_Add_Delegated_zone(self):
                logging.info("Create Delegated Zone")
                grid_member=config.grid_fqdn
                data = {"fqdn": "dddd.outbound_zone2.com","delegate_to": [{"address": "10.35.169.2","name": "secondary.com"}]}
                response = ib_NIOS.wapi_request('POST', object_type= "zone_delegated", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 232 Execution Completed")
		sleep(5)

	@pytest.mark.run(order=233)
        def test_233_stop_Worker_logs_to_check_Delegated_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 233 Execution Completed")

	@pytest.mark.run(order=234)
        def test_234_validate_Worker_logs_to_check_Template_for_Delegated_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 234 Execution Completed")

	@pytest.mark.run(order=235)
        def test_235_Update_Notification_rule_for_Delegated_zone_with_match_rule_as_Modify(self):
                logging.info("Update Notification rule for Delegated Zone with match rule as Modify")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_DELEGATED","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "MODIFY","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 235 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=236)
        def test_236_Validate_Notification_rule_for_delegate_zone_with_match_rule_as_modify(self):
                logging.info("Validating notification rule for delegate zone with match rule as modify")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_DELEGATED', 'op1': 'ZONE_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'MODIFY', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 236 Execution Completed")


	@pytest.mark.run(order=237)
        def test_237_start_Worker_logs_to_check_Delegated_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 237 Execution Completed")

	@pytest.mark.run(order=238)
        def test_238_Update_Delegated_zone(self):
                logging.info("Update Delegated Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_delegated")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify Delegated Zone")
                data = {"comment": "test"}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 238 Execution Completed")
		sleep(5)

	@pytest.mark.run(order=239)
        def test_239_stop_Worker_logs_to_check_Delegated_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 239 Execution Completed")

	@pytest.mark.run(order=240)
        def test_240_validate_Worker_logs_to_check_Template_for_Delegated_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 240 Execution Completed")

	@pytest.mark.run(order=241)
        def test_241_Update_Notification_rule_for_Delegated_zone_with_match_rule_as_Delete(self):
                logging.info("Update Notification rule for Delegated Zone with match rule as delete")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_DELEGATED","op2_type": "STRING"},{"op": "EQ","op1":"OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "REGEX","op1": "ZONE_NAME","op1_type": "FIELD","op2": "^d","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 241 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=242)
        def test_242_Validate_Notification_rule_for_delegate_zone_with_match_rule_as_delete(self):
                logging.info("Validating notification rule for delegate zone with match rule as delete")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_DELEGATED', 'op1': 'ZONE_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}"
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 242 Execution Completed")


	@pytest.mark.run(order=243)
        def test_243_start_Worker_logs_to_check_Delegated_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 243 Execution Completed")

	@pytest.mark.run(order=244)
        def test_244_Delete_Delegated_zone_After_executing_Template(self):
                logging.info("Deleting Delegated one after executing template")
                data= {"fqdn": "dddd.outbound_zone2.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_delegated",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
		print("Test Case 244 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=245)
        def test_245_stop_Worker_logs_to_check_Delegated_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 245 Execution Completed")

	@pytest.mark.run(order=246)
        def test_246_validate_Worker_logs_to_check_Template_for_Delegated_Zone_outbound_user(self):
		logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 246 Execution Completed")

#Notification rule for records


	@pytest.mark.run(order=247)
        def test_247_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_A_with_match_rule_as_Insert(self):
                logging.info("Update Notification rule with record type as A with match rule as Insert")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify Notification rule")
                data = {"event_type": "DB_CHANGE_DNS_RECORD","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_A","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "INSERT","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 247 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=248)
        def test_248_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_A_with_match_rule_as_Insert(self):
                logging.info("Validating Notification rule with record type as A with match rule as Insert")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_A', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'INSERT', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 248 Execution Completed")


	@pytest.mark.run(order=249)
        def test_249_start_Worker_logs_to_check_A_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 249 Execution Completed")

	@pytest.mark.run(order=250)
        def test_250_Create_A_record(self):
                logging.info ("Creating A Record for added Zone")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "arec.outbound_zone2.com","ipv4addr":"1.2.3.4","_ref":endpoint,"comment":"Adding arec","view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                #import pdb;pdb.set_trace()
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                print("Test Case 250 Execution Completed")
		sleep(5)

	@pytest.mark.run(order=251)
        def test_251_stop_Worker_logs_to_check_A_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 251 Execution Completed")

	@pytest.mark.run(order=252)
        def test_252_validate_Worker_logs_to_check_Template_for_A_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution for A record in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 252 Execution Completed")

	@pytest.mark.run(order=253)
        def test_253_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_A_with_match_rule_as_Modify(self):
                logging.info("Update Notification rule with record type as A with match rule as Modify")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_A","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "MODIFY","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 253 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=254)
        def test_254_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_A_with_match_rule_as_Modify(self):
                logging.info("Validating Notification rule with record type as A with match rule as modify")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_A', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'MODIFY', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 254 Execution Completed")


	@pytest.mark.run(order=255)
        def test_255_start_Worker_logs_to_check_A_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 255 Execution Completed")

	@pytest.mark.run(order=256)
        def test_256_Update_A_record(self):
                logging.info ("Updating A Record for added Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:a")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"comment":"Updating A Record"}

                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
		print("Test Case 256 Execution Completed")
                sleep(10)

	@pytest.mark.run(order=257)
        def test_257_stop_Worker_logs_to_check_A_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 257 Execution Completed")

	@pytest.mark.run(order=258)
        def test_258_validate_Worker_logs_to_check_Template_for_A_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution for A record in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 258 Execution Completed")

	@pytest.mark.run(order=259)
        def test_259_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_A_with_match_rule_as_delete(self):
                logging.info("Update Notification rule with record type as A with match rule as delete")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_A","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
		print("Test Case 259 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=260)
        def test_260_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_A_with_match_rule_as_Delete(self):
                logging.info("Validating Notification rule with record type as A with match rule as delete")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_A', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 260 Execution Completed")


	@pytest.mark.run(order=261)
        def test_261_start_Worker_logs_to_check_A_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 261 Execution Completed")

	@pytest.mark.run(order=262)
        def test_262_Delete_A_Record(self):
                logging.info("Deleting A record created by template")
                data= {"name": "arec.outbound_zone2.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:a",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
		print("Test Case 262 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=263)
        def test_263_stop_Worker_logs_to_check_A_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 263 Execution Completed")
	
	@pytest.mark.run(order=264)
        def test_264_validate_Worker_logs_to_check_Template_for_A_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 264 Execution Completed")


	@pytest.mark.run(order=265)
        def test_265_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_AAAA_with_match_rule_as_Insert(self):
                logging.info("Update Notification rule with record type as AAAA with match rule as Insert")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_AAAA","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "INSERT","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 265 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=266)
        def test_266_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_AAAA_with_match_rule_as_Insert(self):
                logging.info("Validating Notification rule with record type as AAAA with match rule as insert")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_AAAA', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'INSERT', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 266 Execution Completed")


	@pytest.mark.run(order=267)
        def test_267_start_Worker_logs_to_check_AAAA_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 267 Execution Completed")

	@pytest.mark.run(order=268)
        def test_268_Create_AAAA_record(self):
                logging.info ("Creating AAAA Record for added Zone")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"ipv6addr": "fd60:e45:e31b::","name":"aaaarec.outbound_zone2.com","_ref":endpoint,"view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:aaaa",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                print("Test Case 268 Execution Completed")
		sleep(10)


	@pytest.mark.run(order=269)
        def test_269_stop_Worker_logs_to_check_AAAA_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 269 Execution Completed")

	@pytest.mark.run(order=270)
        def test_270_validate_Worker_logs_to_check_Template_for_AAAA_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 270 Execution Completed")

	@pytest.mark.run(order=271)
        def test_271_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_AAAA_with_match_rule_as_Modify(self):
                logging.info("Update Notification rule with record type as AAAA with match rule as Modify")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_AAAA","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "MODIFY","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 271 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=272)
        def test_272_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_AAAA_with_match_rule_as_Insert(self):
                logging.info("Validating Notification rule with record type as AAAA with match rule as insert")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_AAAA', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'MODIFY', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 272 Execution Completed")

	@pytest.mark.run(order=273)
        def test_273_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_AAAA_with_match_rule_as_Insert(self):
                logging.info("Validating Notification rule with record type as AAAA with match rule as insert")
                get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_AAAA', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'MODIFY', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 273 Execution Completed")

	@pytest.mark.run(order=274)
        def test_274_start_Worker_logs_to_check_AAAA_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 274 Execution Completed")

	@pytest.mark.run(order=275)
        def test_275_Update_AAAA_record(self):
                logging.info ("Updating A Record for added Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:aaaa")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"comment":"Updating AAAA Record"}

                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
		print("Test Case 275 Execution Completed")

	@pytest.mark.run(order=276)
        def test_276_stop_Worker_logs_to_check_AAAA_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 276 Execution Completed")

	@pytest.mark.run(order=277)
        def test_277_validate_Worker_logs_to_check_Template_for_AAAA_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 277 Execution Completed")

	
	@pytest.mark.run(order=278)
        def test_278_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_AAAA_with_match_rule_as_delete(self):
                logging.info("Update Notification rule with record type as AAAA with match rule as delete")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_AAAA","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 278 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=279)
        def test_279_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_AAAA_with_match_rule_as_delete(self):
                logging.info("Validating Notification rule with record type as AAAA with match rule as delete")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_AAAA', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 279 Execution Completed")

	@pytest.mark.run(order=280)
        def test_280_start_Worker_logs_to_check_AAAA_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 280 Execution Completed")


	@pytest.mark.run(order=281)
        def test_281_Delete_AAAA_Record(self):
                logging.info("Deleting AAAA record created by template")
                data= {"name":"aaaarec.outbound_zone2.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:aaaa",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
		print("Test Case 281 Execution Completed")

	@pytest.mark.run(order=282)
        def test_282_stop_Worker_logs_to_check_AAAA_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 282 Execution Completed")

	@pytest.mark.run(order=283)
        def test_283_validate_Worker_logs_to_check_Template_for_AAAA_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 283 Execution Completed")

	@pytest.mark.run(order=284)
        def test_284_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_CNAME_with_match_rule_as_INSERT(self):
                logging.info("Update Notification rule with record type as CNAME with match rule as INSERT")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_CNAME","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "INSERT","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 284 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=285)
        def test_285_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_CNAME_with_match_rule_as_insert(self):
                logging.info("Validating Notification rule with record type as CNMAE with match rule as insert")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_CNAME', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'INSERT', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 285 Execution Completed")

	@pytest.mark.run(order=286)
        def test_286_start_Worker_logs_to_check_CNAME_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 286 Execution Completed")

	@pytest.mark.run(order=287)
        def test_287_Create_CNAME_record(self):
                logging.info ("Creating CNAME Record for added Zone")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "cname.outbound_zone2.com","canonical": "cnametest.com","_ref":endpoint,"view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:cname",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("CNAME Record is created Successfully")
		print("Test Case 287 Execution Completed")

	@pytest.mark.run(order=288)
        def test_288_stop_Worker_logs_to_check_CNAME_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 288 Execution Completed")

	@pytest.mark.run(order=289)
        def test_289_validate_Worker_logs_to_check_Template_for_CNAME_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 289 Execution Completed")

	@pytest.mark.run(order=290)
        def test_290_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_CNAME_with_match_rule_as_MODIFY(self):
                logging.info("Update Notification rule with record type as CNAME with match rule as MODIFY")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_CNAME","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "MODIFY","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 290 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=291)
        def test_291_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_CNAME_with_match_rule_as_insert(self):
                logging.info("Validating Notification rule with record type as CNMAE with match rule as insert")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_CNAME', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'MODIFY', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 291 Execution Completed")


	@pytest.mark.run(order=292)
        def test_292_start_Worker_logs_to_check_CNAME_recordin_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 292 Execution Completed")

	@pytest.mark.run(order=293)
	def test_293_Update_CNAME_record(self):
                logging.info ("Updating A Record for added Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:cname")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"comment":"Updating CNAME Record"}

                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("A Record is updated Successfully")
		print("Test Case 293 Execution Completed")


	@pytest.mark.run(order=294)
        def test_294_stop_Worker_logs_to_check_CNAME_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 294 Execution Completed")

	@pytest.mark.run(order=295)
        def test_295_validate_Worker_logs_to_check_Template_for_CNAME_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 295 Execution Completed")

	@pytest.mark.run(order=296)
        def test_296_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_CNAME_with_match_rule_as_DELETE(self):
                logging.info("Update Notification rule with record type as CNAME with match rule as DELETE")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_CNAME","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 296 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=297)
        def test_297_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_CNAME_with_match_rule_as_delete(self):
                logging.info("Validating Notification rule with record type as CNMAE with match rule as delete")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_CNAME', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 297 Execution Completed")


	@pytest.mark.run(order=298)
        def test_298_start_Worker_logs_to_check_CNAME_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 298 Execution Completed")

	@pytest.mark.run(order=299)
        def test_299_Delete_CNAME_Record(self):
                logging.info("Deleting CNAME record created by template")
                data= {"name":"cname.outbound_zone2.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:cname",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
		print("Test Case 299 Execution Completed")

	@pytest.mark.run(order=300)
        def test_300_stop_Worker_logs_to_check_CNAME_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 300 Execution Completed")

	@pytest.mark.run(order=301)
        def test_301_validate_Worker_logs_to_check_Template_for_CNAME_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 301 Execution Completed")


	@pytest.mark.run(order=302)
        def test_302_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_ALIAS_with_match_rule_as_insert(self):
                logging.info("Update Notification rule with record type as ALIAS with match rule as insert")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_ALIAS","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "INSERT","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 302 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=303)
        def test_303_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_ALIAS_with_match_rule_as_insert(self):
                logging.info("Validating Notification rule with record type as ALIAS with match rule as insert")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_ALIAS', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'INSERT', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 303 Execution Completed")
		
	@pytest.mark.run(order=304)
        def test_304_start_Worker_logs_to_check_ALIAS_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 304 Execution Completed")

	@pytest.mark.run(order=305)
        def test_305_Create_ALIAS_record(self):
                logging.info ("Creating ALIAS Record for added Zone")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "alias.outbound_zone2.com","target_name": "arec.outbound_zone2.com","_ref":endpoint,"target_type": "A","view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:alias",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("ALIAS Record is created Successfully")
		print("Test Case 305 Execution Completed") 
                sleep(5)

	@pytest.mark.run(order=306)
        def test_306_stop_Worker_logs_to_check_ALAIAS_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 306 Execution Completed")

        @pytest.mark.run(order=307)
        def test_307_validate_Worker_logs_to_check_Template_for_ALIAS_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 307 Execution Completed")

	@pytest.mark.run(order=308)
        def test_308_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_ALIAS_with_match_rule_as_modify(self):
                logging.info("Update Notification rule with record type as ALIAS with match rule as modify")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_ALIAS","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "MODIFY","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 308 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=309)
        def test_309_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_ALIAS_with_match_rule_as_modify(self):
                logging.info("Validating Notification rule with record type as ALIAS with match rule as modify")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_ALIAS', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'MODIFY', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 309 Execution Completed")

	@pytest.mark.run(order=310)
        def test_310_start_Worker_logs_to_check_ALIAS_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)	
		print("Test Case 310 Execution Completed")

	@pytest.mark.run(order=311)
        def test_311_Update_ALIAS_record(self):
                logging.info ("Updating ALIAS Record for added Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:alias")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"name": "aliasupdated.outbound_zone2.com"}

                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("ALIAS Record is updated Successfully")
		print("Test Case 311 Execution Completed")
                sleep(5)


	@pytest.mark.run(order=312)
        def test_312_stop_Worker_logs_to_check_ALIAS_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 312 Execution Completed")

        @pytest.mark.run(order=313)
        def test_313_validate_Worker_logs_to_check_Template_for_ALIAS_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 313 Execution Completed")


	@pytest.mark.run(order=314)
        def test_314_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_ALIAS_with_match_rule_as_Delete(self):
                logging.info("Update Notification rule with record type as ALIAS with match rule as delete")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_ALIAS","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 314 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=315)
        def test_315_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_ALIAS_with_match_rule_as_delete(self):
                logging.info("Validating Notification rule with record type as ALIAS with match rule as delete")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_ALIAS', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 315 Execution Completed")

	@pytest.mark.run(order=316)
        def test_316_start_Worker_logs_to_check_ALIAS_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 316 Execution Completed")


	@pytest.mark.run(order=317)
        def test_317_Delete_ALIAS_Record(self):
                logging.info("Deleting CNAME record created by template")
                data= {"name": "aliasupdated.outbound_zone2.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:alias",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
		print("Test Case 317 Execution Completed")

	@pytest.mark.run(order=318)
        def test_318_stop_Worker_logs_to_check_ALIAS_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 318 Execution Completed")

        @pytest.mark.run(order=319)
        def test_319_validate_Worker_logs_to_check_Template_for_ALIAS_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 319 Execution Completed")


	@pytest.mark.run(order=320)
        def test_320_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_CAA_with_match_rule_as_insert(self):
                logging.info("Update Notification rule with record type as CAA with match rule as insert")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_CAA","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "INSERT","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 320 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=321)
        def test_321_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_CAA_with_match_rule_as_insert(self):
                logging.info("Validating Notification rule with record type as CAA with match rule as insert")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_CAA', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'INSERT', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 321 Execution Completed")

	@pytest.mark.run(order=322)
        def test_322_start_Worker_logs_to_check_CAA_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 322 Execution Completed")

	@pytest.mark.run(order=323)
        def test_323_Create_CAA_record(self):
                logging.info ("Creating CAA Record for added Zone")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"ca_value": "CAA_Authority.com","ca_tag": "issue","name": "caa.outbound_zone2.com","ca_flag":0}
                response = ib_NIOS.wapi_request('POST', object_type="record:caa",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("CAA Record is created Successfully")
		print("Test Case 323 Execution Completed")

	@pytest.mark.run(order=324)
        def test_324_stop_Worker_logs_to_check_CAA_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 324 Execution Completed")

        @pytest.mark.run(order=325)
        def test_325_validate_Worker_logs_to_check_Template_for_CAA_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 325 Execution Completed")

	@pytest.mark.run(order=326)
        def test_326_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_CAA_with_match_rule_as_modify(self):
                logging.info("Update Notification rule with record type as CAA with match rule as modify")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_CAA","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "MODIFY","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 326 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=327)
        def test_327_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_CAA_with_match_rule_as_modify(self):
                logging.info("Validating Notification rule with record type as CAA with match rule as modify")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_CAA', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'MODIFY', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 327 Execution Completed")

	@pytest.mark.run(order=328)
        def test_328_start_Worker_logs_to_check_CAA_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 328 Execution Completed")

	@pytest.mark.run(order=329)
        def test_329_Update_CAA_record(self):
                logging.info ("Updating CAA Record for added Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:caa")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"name": "caaUPDATED.outbound_zone2.com"}

                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("CAA Record is updated Successfully")
		print("Test Case 329 Execution Completed")

	@pytest.mark.run(order=330)
        def test_330_stop_Worker_logs_to_check_CAA_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 330 Execution Completed")

        @pytest.mark.run(order=331)
        def test_331_validate_Worker_logs_to_check_Template_for_CAA_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 331 Execution Completed")

	@pytest.mark.run(order=332)
        def test_332_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_CAA_with_match_rule_as_delete(self):
                logging.info("Update Notification rule with record type as CAA with match rule as delete")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_CAA","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 332 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=333)
        def test_333_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_CAA_with_match_rule_as_delete(self):
                logging.info("Validating Notification rule with record type as CAA with match rule as delete")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_CAA', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 333 Execution Completed")

	@pytest.mark.run(order=334)
	def test_334_start_Worker_logs_to_check_CAA_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 334 Execution Completed")

	@pytest.mark.run(order=335)
	def test_335_Delete_CAA_Record(self):
                logging.info("Deleting CAA record created by template")
                data= {"name": "caaupdated.outbound_zone2.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:caa",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
		print("Test Case 335 Execution Completed")

	@pytest.mark.run(order=336)
        def test_336_stop_Worker_logs_to_check_CAA_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 336 Execution Completed")

        @pytest.mark.run(order=337)
        def test_337_validate_Worker_logs_to_check_Template_for_CAA_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 337 Execution Completed")


	@pytest.mark.run(order=338)
        def test_338_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_DNAME_with_match_rule_as_Insert(self):
                logging.info("Update Notification rule with record type as DNAME with match rule as insert")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_DNAME","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "INSERT","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 338 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=339)
        def test_339_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_DNAME_with_match_rule_as_Insert(self):
                logging.info("Validating Notification rule with record type as DNAME with match rule as Insert")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_DNAME', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'INSERT', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 339 Execution Completed")

	@pytest.mark.run(order=340)
        def test_340_start_Worker_logs_to_check_DNAME_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 340 Execution Completed")

	@pytest.mark.run(order=341)
        def test_341_Create_DNAME_record(self):
                logging.info ("Creating DMANE Record for added Zone")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "dname.outbound_zone2.com","target": "arec.com","_ref":endpoint,"comment":"Adding dname rec","view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:dname",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("DNAME Record is created Successfully")
		print("Test Case 341 Execution Completed")

	@pytest.mark.run(order=342)
        def test_342_stop_Worker_logs_to_check_DNAME_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 342 Execution Completed")

        @pytest.mark.run(order=343)
        def test_343_validate_Worker_logs_to_check_Template_for_DNAME_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 343 Execution Completed")

	
	@pytest.mark.run(order=344)
        def test_344_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_DNAME_with_match_rule_as_modify(self):
                logging.info("Update Notification rule with record type as DNAME with match rule as modify")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_DNAME","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "MODIFY","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 344 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=345)
        def test_345_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_DNAME_with_match_rule_as_modify(self):
                logging.info("Validating Notification rule with record type as DNAME with match rule as modify")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_DNAME', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'MODIFY', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 345 Execution Completed")

	@pytest.mark.run(order=346)
        def test_346_start_Worker_logs_to_check_DNAME_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 346 Execution Completed")

	@pytest.mark.run(order=347)
        def test_347_Update_DNAME_record(self):
                logging.info ("Updating DNAME Record for added Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:dname")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"comment":"Adding UPDATED dname rec"}

                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("DNAME Record is updated Successfully")
		print("Test Case 347 Execution Completed")

	@pytest.mark.run(order=348)
        def test_348_stop_Worker_logs_to_check_DNAME_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 348 Execution Completed")

        @pytest.mark.run(order=349)
        def test_349_validate_Worker_logs_to_check_Template_for_DNAME_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 349 Execution Completed")


	@pytest.mark.run(order=350)
        def test_350_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_DNAME_with_match_rule_as_delete(self):
                logging.info("Update Notification rule with record type as DNAME with match rule as delete")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_DNAME","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 350 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=351)
        def test_351_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_DNAME_with_match_rule_as_delete(self):
                logging.info("Validating Notification rule with record type as DNAME with match rule as delete")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_DNAME', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
		logging.info("Test Case 351 Execution Completed")

	@pytest.mark.run(order=352)
        def test_352_start_Worker_logs_to_check_DNAME_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 352 Execution Completed")

	@pytest.mark.run(order=353)
	def test_353_Delete_DNAME_Record(self):
                logging.info("Deleting DNAME record created by template")
                data= {"name": "dname.outbound_zone2.com","target": "arec.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:dname",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
		print("Test Case 353 Execution Completed")

	@pytest.mark.run(order=354)
        def test_354_stop_Worker_logs_to_check_DNAME_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 354 Execution Completed")

        @pytest.mark.run(order=355)
        def test_355_validate_Worker_logs_to_check_Template_for_DNAME_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 355 Execution Completed")


	@pytest.mark.run(order=356)
        def test_356_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_MX_with_match_rule_as_insert(self):
                logging.info("Update Notification rule with record type as MX with match rule as insert")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_MX","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "INSERT","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 356 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=357)
        def test_357_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_MX_with_match_rule_as_insert(self):
                logging.info("Validating Notification rule with record type as DNAME with match rule as insert")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_MX', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'INSERT', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 357 Execution Completed")


	@pytest.mark.run(order=358)
        def test_358_start_Worker_logs_to_check_MX_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 358 Execution Completed")

	@pytest.mark.run(order=359)
        def test_359_Create_MX_record(self):
                logging.info ("Creating MX Record for added Zone")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"mail_exchanger": "host1.outbound_zone2.com","name": "mail.outbound_zone2.com","_ref":endpoint,"preference": 1,"view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:mx",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("MX Record is created Successfully")
		print("Test Case 359 Execution Completed")
                sleep(10)


	@pytest.mark.run(order=360)
        def test_360_stop_Worker_logs_to_check_DNAME_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 360 Execution Completed")

        @pytest.mark.run(order=361)
        def test_361_validate_Worker_logs_to_check_Template_for_DNAME_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 361 Execution Completed")

	@pytest.mark.run(order=362)
        def test_362_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_MX_with_match_rule_as_modify(self):
                logging.info("Update Notification rule with record type as MX with match rule as modify")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_MX","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "MODIFY","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 362 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=363)
        def test_363_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_MX_with_match_rule_as_modify(self):
                logging.info("Validating Notification rule with record type as DNAME with match rule as modify")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_MX', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'MODIFY', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 363 Execution Completed")

	@pytest.mark.run(order=364)
        def test_364_start_Worker_logs_to_check_MX_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 364 Execution Completed")

	@pytest.mark.run(order=365)
        def test_365_Update_MX_record(self):
                logging.info ("Updating MX Record for added Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:mx")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"mail_exchanger": "host111.outbound_zone2.com"}

                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("MX Record is updated Successfully")
		print("Test Case 365 Execution Completed")

	@pytest.mark.run(order=366)
        def test_366_stop_Worker_logs_to_check_DNAME_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 366 Execution Completed")

        @pytest.mark.run(order=367)
        def test_367_validate_Worker_logs_to_check_Template_for_DNAME_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 367 Execution Completed")


	@pytest.mark.run(order=368)
        def test_368_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_MX_with_match_rule_as_delete(self):
                logging.info("Update Notification rule with record type as MX with match rule as delete")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_MX","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 368 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=369)
        def test_369_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_MX_with_match_rule_as_delete(self):
                logging.info("Validating Notification rule with record type as DNAME with match rule as delete")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_MX', 'op1': 'RECORD_TYPE'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}, {'op': 'ENDLIST'}"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 369 Execution Completed")

        @pytest.mark.run(order=370)
        def test_370_start_Worker_logs_to_check_MX_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 370 Execution Completed")

	@pytest.mark.run(order=371)
        def test_371_Delete_MX_Record(self):
                logging.info("Deleting MX record created by template")
                data= {"name": "mail.outbound_zone2.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:mx",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
		print("Test Case 371 Execution Completed")

	@pytest.mark.run(order=372)
        def test_372_stop_Worker_logs_to_check_MX_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 372 Execution Completed")

        @pytest.mark.run(order=373)
        def test_373_validate_Worker_logs_to_check_Template_for_MX_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 373 Execution Completed")


	@pytest.mark.run(order=374)
        def test_374_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_NAPTR_with_match_rule_as_insert(self):
                logging.info("Update Notification rule with record type as NAPTR with match rule as insert")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_NAPTR","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "INSERT","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 374 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=375)
        def test_375_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_NAPTR_with_match_rule_as_insert(self):
                logging.info("Validating Notification rule with record type as NAPTR with match rule as insert")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_NAPTR', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'INSERT', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 375 Execution Completed")


        @pytest.mark.run(order=376)
        def test_376_start_Worker_logs_to_check_NAPTR_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 376 Execution Completed")

	@pytest.mark.run(order=377)
        def test_377_Create_NAPTR_record(self):
                logging.info ("Creating NAPTR Record for added Zone")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "naptr.outbound_zone2.com","order": 10,"_ref":endpoint,"preference": 10,"view":"default","replacement": "arec.outbound_zone2.com","services": "http+E2U"}
                response = ib_NIOS.wapi_request('POST', object_type="record:naptr",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("NAPTR Record is created Successfully")
		print("Test Case 377 Execution Completed")

	@pytest.mark.run(order=378)
        def test_378_stop_Worker_logs_to_check_NAPTR_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 378 Execution Completed")

        @pytest.mark.run(order=379)
        def test_379_validate_Worker_logs_to_check_Template_for_NAPTR_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 379 Execution Completed")


	@pytest.mark.run(order=380)
        def test_380_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_NAPTR_with_match_rule_as_modify(self):
                logging.info("Update Notification rule with record type as NAPTR with match rule as modify")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_NAPTR","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "MODIFY","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 380 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=381)
        def test_381_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_NAPTR_with_match_rule_as_modify(self):
                logging.info("Validating Notification rule with record type as NAPTR with match rule as modify")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_NAPTR', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'MODIFY', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 381 Execution Completed")


        @pytest.mark.run(order=382)
        def test_382_start_Worker_logs_to_check_NAPTR_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 382 Execution Completed")

	@pytest.mark.run(order=383)
        def test_383_Update_NAPTR_record(self):
                logging.info ("Updating NAPTR Record for added Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:naptr")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"name": "naptrUPDATED.outbound_zone2.com"}

                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("NAPTR Record is updated Successfully")
		print("Test Case 383 Execution Completed")

	@pytest.mark.run(order=384)
        def test_384_stop_Worker_logs_to_check_NAPTR_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 384 Execution Completed")

        @pytest.mark.run(order=385)
        def test_385_validate_Worker_logs_to_check_Template_for_NAPTR_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 385 Execution Completed")

	@pytest.mark.run(order=386)
        def test_386_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_NAPTR_with_match_rule_as_delete(self):
                logging.info("Update Notification rule with record type as NAPTR with match rule as delete")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_NAPTR","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 386 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=387)
        def test_387_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_NAPTR_with_match_rule_as_delete(self):
                logging.info("Validating Notification rule with record type as NAPTR with match rule as delete")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_NAPTR', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 387 Execution Completed")

        @pytest.mark.run(order=388)
        def test_388_start_Worker_logs_to_check_NAPTR_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 388 Execution Completed")

	@pytest.mark.run(order=389)
	def test_389_Delete_NAPTR_Record(self):
                logging.info("Deleting NAPTR record created by template")
                data= {"name": "naptrupdated.outbound_zone2.com","order": 10,"preference": 10,"replacement": "arec.outbound_zone2.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:naptr",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
		ref = json.loads(get_ref)[0]['_ref']
		request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
		print("Test Case 389 Execution Completed")

        @pytest.mark.run(order=390)
        def test_390_stop_Worker_logs_to_check_MX_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 390 Execution Completed")

        @pytest.mark.run(order=391)
        def test_391_validate_Worker_logs_to_check_Template_for_MX_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 391 Execution Completed")

	@pytest.mark.run(order=392)
        def test_392_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_NS_with_match_rule_as_insert(self):
                logging.info("Update Notification rule with record type as NS with match rule as insert")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_NS","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "INSERT","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 392 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=393)
        def test_393_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_NS_with_match_rule_as_insert(self):
                logging.info("Validating Notification rule with record type as NS with match rule as insert")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_NS', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'INSERT', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 393 Execution Completed")


	@pytest.mark.run(order=394)
        def test_394_start_Worker_logs_to_check_NS_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 394 Execution Completed")

	@pytest.mark.run(order=395)
        def test_395_Create_NS_record(self):
                logging.info ("Creating NS Record for added Zone")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name":"outbound_zone2.com","nameserver": "aa.outbound_zone2.com","addresses":[{"address":"4.3.2.1","auto_create_ptr": False}]}
                response = ib_NIOS.wapi_request('POST', object_type="record:ns",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("NS Record is created Successfully")
		print("Test Case 395 Execution Completed")

	@pytest.mark.run(order=396)
        def test_396_stop_Worker_logs_to_check_NS_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 396 Execution Completed")

        @pytest.mark.run(order=397)
        def test_397_validate_Worker_logs_to_check_Template_for_NS_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 397 Execution Completed")

	@pytest.mark.run(order=398)
        def test_398_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_NS_with_match_rule_as_delete(self):
                logging.info("Update Notification rule with record type as NS with match rule as delete")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_NS","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 398 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=399)
        def test_399_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_NS_with_match_rule_as_delete(self):
                logging.info("Validating Notification rule with record type as NS with match rule as delete")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_NS', 'op1': 'RECORD_TYPE'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}, {'op': 'ENDLIST'}]"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 399 Execution Completed")

 
        @pytest.mark.run(order=400)
        def test_400_start_Worker_logs_to_check_NAPTR_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 400 Execution Completed")

	@pytest.mark.run(order=401)
        def test_401_Delete_NS_Record(self):
                logging.info("Deleting NS record created by template")
                data= {"name":"outbound_zone2.com","nameserver": "aa.outbound_zone2.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:ns",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
		print("Test Case 401 Execution Completed")

        @pytest.mark.run(order=402)
        def test_402_stop_Worker_logs_to_check_NS_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 402 Execution Completed")

        @pytest.mark.run(order=403)
        def test_403_validate_Worker_logs_to_check_Template_for_NS_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 403 Execution Completed")

	@pytest.mark.run(order=404)
        def test_404_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_PTR_with_match_rule_as_insert(self):
                logging.info("Update Notification rule with record type as PTR with match rule as insert")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_PTR","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "INSERT","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 404 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=405)
        def test_405_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_PTR_with_match_rule_as_insert(self):
                logging.info("Validating Notification rule with record type as PTR with match rule as insert")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_PTR', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'INSERT', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 405 Execution Completed")


        @pytest.mark.run(order=406)
        def test_406_start_Worker_logs_to_check_PTR_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 406 Execution Completed")

	@pytest.mark.run(order=407)
        def test_407_Create_PTR_record(self):
                logging.info ("Creating PTR Record for added Zone")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "ptrrec.outbound_zone2.com","ipv4addr":"1.2.3.4","_ref":endpoint,"ptrdname": "server1.outbound_zone.com","view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:ptr",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("PTR Record is created Successfully")
		print("Test Case 407 Execution Completed")

	@pytest.mark.run(order=408)
        def test_408_stop_Worker_logs_to_check_PTR_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 408 Execution Completed")

        @pytest.mark.run(order=409)
        def test_409_validate_Worker_logs_to_check_Template_for_PTR_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
		print("Test Case 409 Execution Completed")

	@pytest.mark.run(order=410)
        def test_410_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_PTR_with_match_rule_as_modify(self):
                logging.info("Update Notification rule with record type as PTR with match rule as modify")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_PTR","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "MODIFY","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 410 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=411)
        def test_411_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_PTR_with_match_rule_as_modify(self):
                logging.info("Validating Notification rule with record type as PTR with match rule as modify")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_PTR', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'MODIFY', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 411 Execution Completed")

	@pytest.mark.run(order=412)
        def test_412_start_Worker_logs_to_check_PTR_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 412 Execution Completed")

	@pytest.mark.run(order=413)
	def test_413_Update_PTR_record(self):
                logging.info ("Updating PTR Record for added Zone")
		get_ref = ib_NIOS.wapi_request('GET', object_type="record:ptr")
		logging.info(get_ref)
		res = json.loads(get_ref)
		ref1 = json.loads(get_ref)[-1]['_ref']
		print ref1
		data = {"comment": "outbound"}
		response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
		print ("---------------------------------------------------",json.loads(response))
		read  = re.search(r'201',response)
		for read in response:
			assert True
		print("Test Case 413 Execution Completed")

	@pytest.mark.run(order=414)
        def test_414_stop_Worker_logs_to_check_PTR_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 414 Execution Completed")

        @pytest.mark.run(order=415)
        def test_415_validate_Worker_logs_to_check_Template_for_PTR_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
		print("Test Case 415 Execution Completed")

	@pytest.mark.run(order=416)
        def test_416_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_PTR_with_match_rule_as_delete(self):
                logging.info("Update Notification rule with record type as PTR with match rule as delete")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_PTR","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 416 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=417)
        def test_417_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_PTR_with_match_rule_as_delete(self):
                logging.info("Validating Notification rule with record type as PTR with match rule as delete")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_PTR', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 417 Execution Completed")

        @pytest.mark.run(order=418)
        def test_418_start_Worker_logs_to_check_PTR_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 418 Execution Completed")

	@pytest.mark.run(order=419)
        def test_419_Delete_PTR_Record(self):
                logging.info("Deleting PTR record created by template")
                data= {"ptrdname": "server1.outbound_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:ptr",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
		print("Test Case 419 Execution Completed")

        @pytest.mark.run(order=420)
        def test_420_stop_Worker_logs_to_check_PTR_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 420 Execution Completed")

        @pytest.mark.run(order=421)
        def test_421_validate_Worker_logs_to_check_Template_for_PTR_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 421 Execution Completed")

	@pytest.mark.run(order=422)
        def test_422_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_SOA_with_match_rule_as_MODIFY(self):
                logging.info("Update Notification rule with record type as SOA with match rule as MODIFY")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_SOA","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "MODIFY","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 422 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=423)
        def test_423_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_SOA_with_match_rule_as_MODIFY(self):
                logging.info("Validating Notification rule with record type as PTR with match rule as MODIFY")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_SOA', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'MODIFY', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 423 Execution Completed")

        @pytest.mark.run(order=424)
        def test_424_start_Worker_logs_to_check_SOA_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 424 Execution Completed")


	@pytest.mark.run(order=425)
        def test_425_Update_soa_record(self):
                logging.info ("Updating Serial Number for SOA Record for added Zone")
                data={"fqdn":"outbound_zone2.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"soa_serial_number":6}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("Serial Number for SOA Record is updated Successfully")
		print("Test Case 425 Execution Completed")

	@pytest.mark.run(order=426)
        def test_426_stop_Worker_logs_to_check_SOA_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 426 Execution Completed")

        @pytest.mark.run(order=427)
        def test_427_validate_Worker_logs_to_check_Template_for_SOA_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 427 Execution Completed")

	@pytest.mark.run(order=428)
        def test_428_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_SRV_with_match_rule_as_insert(self):
                logging.info("Update Notification rule with record type as SRV with match rule as INSERT")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_SRV","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "INSERT","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 428 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=429)
        def test_429_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_SOA_with_match_rule_as_INSERT(self):
                logging.info("Validating Notification rule with record type as PTR with match rule as INSERT")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_SRV', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'INSERT', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 429 Execution Completed")

        @pytest.mark.run(order=430)
        def test_430_start_Worker_logs_to_check_SOA_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 430 Execution Completed")

	@pytest.mark.run(order=431)
        def test_431_Create_SRV_record(self):
                logging.info ("Creating SRV Record for added Zone")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "outbound_zone2.com","port":22,"_ref":endpoint,"target":"outbound_zone2.com","view":"default","weight":10,"priority":1}
                response = ib_NIOS.wapi_request('POST', object_type="record:srv",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("SRV Record is created Successfully")
		print("Test Case 431 Execution Completed")

	@pytest.mark.run(order=432)
        def test_432_stop_Worker_logs_to_check_SOA_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 432 Execution Completed")

        @pytest.mark.run(order=433)
        def test_433_validate_Worker_logs_to_check_Template_for_SOA_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 433 Execution Completed")

	@pytest.mark.run(order=434)
        def test_434_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_SRV_with_match_rule_as_MODIFY(self):
                logging.info("Update Notification rule with record type as SRV with match rule as MODIFY")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_SRV","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "MODIFY","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 434 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=435)
        def test_435_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_SOA_with_match_rule_as_MODIFY(self):
                logging.info("Validating Notification rule with record type as PTR with match rule as MODIFY")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_SRV', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'MODIFY', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 435 Execution Completed")

        @pytest.mark.run(order=436)
        def test_436_start_Worker_logs_to_check_SOA_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 436 Execution Completed")

	@pytest.mark.run(order=437)
        def test_437_Update_SRV_record(self):
                logging.info ("Updating SRV Record for added Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:srv")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"port":443}

                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("SRV Record is updated Successfully")
		print("Test Case 437 Execution Completed")


	@pytest.mark.run(order=438)
        def test_438_stop_Worker_logs_to_check_SRV_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 438 Execution Completed")

        @pytest.mark.run(order=439)
        def test_439_validate_Worker_logs_to_check_Template_for_SRV_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 439 Execution Completed")

	@pytest.mark.run(order=440)
        def test_440_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_SRV_with_match_rule_as_DELETE(self):
                logging.info("Update Notification rule with record type as SRV with match rule as delete")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_SRV","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
		print("Test Case 440 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=441)
        def test_441_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_SRV_with_match_rule_as_delete(self):
                logging.info("Validating Notification rule with record type as PTR with match rule as Delete")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_SRV', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 441 Execution Completed")

        @pytest.mark.run(order=442)
        def test_442_start_Worker_logs_to_check_SOA_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 442 Execution Completed")

	@pytest.mark.run(order=443)
	def test_443_Delete_SRV_Record(self):
                logging.info("Deleting SRV record created by template")
                data={"name": "outbound_zone2.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:srv",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
		print("Test Case 443 Execution Completed")

        @pytest.mark.run(order=444)
        def test_444_stop_Worker_logs_to_check_SRV_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 444 Execution Completed")

        @pytest.mark.run(order=445)
        def test_445_validate_Worker_logs_to_check_Template_for_SRV_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 445 Execution Completed")

	@pytest.mark.run(order=446)
        def test_446_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_TLSA_with_match_rule_as_INSERT(self):
                logging.info("Update Notification rule with record type as TLSA with match rule as insert")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_TLSA","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "INSERT","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 446 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=447)
        def test_447_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_TLSA_with_match_rule_as_INSERT(self):
                logging.info("Validating Notification rule with record type as TLSA with match rule as INSERT")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_TLSA', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'INSERT', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 447 Execution Completed")


	@pytest.mark.run(order=448)
        def test_448_Sign_Dnssec_Zone(self):
                logging.info("Sign zone for adding TLSA Record")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                ref=endpoint
                print ("###########",ref)
                data={"buffer":"KSK","operation":"SIGN"}
                response = ib_NIOS.wapi_request('POST', object_type=ref,fields=json.dumps(data),params="?_function=dnssec_operation")
                print (response)
                for read in response:
                        assert True
                logging.info("The selected zone is signed successfully")
                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")
		print("Test Case 448 Execution Completed")

	@pytest.mark.run(order=449)
        def test_449_Validate_Dnssec_Zone_isSigned(self):
                logging.info("Validate if the zone is signed")
                data = {"fqdn":"outbound_zone2.com"}
                response=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",response)
                logging.info(response)
                ref=response
                #response1=common_util.get_object_reference(object_type=ref,params= "?_return_fields=is_dnssec_signed")
                response1 = ib_NIOS.wapi_request('GET', object_type= ref + "?_return_fields=is_dnssec_signed",fields=json.dumps(data))
                print response1
                res=json.loads(response1)
                print ("The value of the dnssec sign zone is ",res['is_dnssec_signed'])
                if (res['is_dnssec_signed']==True):
                        assert True
                logging.info("Selected Zone is signed successfully")
		print("Test Case 449 Execution Completed")

	@pytest.mark.run(order=450)
        def test_450_start_Worker_logs_to_check_TLSA_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 450 Execution Completed")

	@pytest.mark.run(order=451)
        def test_451_Create_TLSA_record(self):
                logging.info ("Creating TLSA Record for added Zone")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "_443._tcp.tlsa.outbound_zone2.com","matched_type": 0,"selector":0,"certificate_usage": 0,"certificate_data":"abcd","_ref":endpoint,"view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:tlsa",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("TLSA Record is created Successfully")
		print("Test Case 451 Execution Completed")

	@pytest.mark.run(order=452)
        def test_452_stop_Worker_logs_to_check_SRV_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 452 Execution Completed")

        @pytest.mark.run(order=453)
        def test_453_validate_Worker_logs_to_check_Template_for_SRV_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 453 Execution Completed")


	@pytest.mark.run(order=454)
        def test_454_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_TLSA_with_match_rule_as_modify(self):
                logging.info("Update Notification rule with record type as TLSA with match rule as modify")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_TLSA","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "MODIFY","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 454 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=455)
        def test_455_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_TLSA_with_match_rule_as_MODIFY(self):
                logging.info("Validating Notification rule with record type as TLSA with match rule as MODIFY")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_TLSA', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'MODIFY', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 455 Execution Completed")
	
	@pytest.mark.run(order=456)
        def test_456_start_Worker_logs_to_check_SOA_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 456 Execution Completed")

	@pytest.mark.run(order=457)
        def test_457_Update_TLSA_record(self):
                logging.info ("Updating cert for TLSA Record for added Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:tlsa")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"certificate_data":"abcdef"}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("Certificate details is updated for TLSA Record")
		print("Test Case 457 Execution Completed")

	@pytest.mark.run(order=458)
        def test_458_stop_Worker_logs_to_check_SRV_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 458 Execution Completed")

        @pytest.mark.run(order=459)
        def test_459_validate_Worker_logs_to_check_Template_for_SRV_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 459 Execution Completed")

	@pytest.mark.run(order=460)
        def test_460_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_TLSA_with_match_rule_as_delete(self):
                logging.info("Update Notification rule with record type as TLSA with match rule as delete")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_TLSA","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 460 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=461)
        def test_461_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_TLSA_with_match_rule_as_delete(self):
                logging.info("Validating Notification rule with record type as TLSA with match rule as delete")
                get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_TLSA', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
		print("Test Case 461 Execution Completed")

        @pytest.mark.run(order=462)
        def test_462_start_Worker_logs_to_check_SOA_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 462 Execution Completed")

	@pytest.mark.run(order=463)
        def test_463_Delete_TLSA_Record(self):
                logging.info("Deleting TLSA record created by template")
                data= {"name": "_443._tcp.tlsa.outbound_zone2.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:tlsa",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
		print("Test Case 463 Execution Completed")

        @pytest.mark.run(order=464)
        def test_464_stop_Worker_logs_to_check_TLSA_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 464 Execution Completed")

        @pytest.mark.run(order=465)
        def test_465_validate_Worker_logs_to_check_Template_for_TLSA_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 465 Execution Completed")


	@pytest.mark.run(order=466)
        def test_466_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_TXT_with_match_rule_as_insert(self):
                logging.info("Update Notification rule with record type as TXT with match rule as insert")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_TXT","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "INSERT","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 466 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=467)
        def test_467_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_TXT_with_match_rule_as_insert(self):
                logging.info("Validating Notification rule with record type as TXT with match rule as insert")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_TXT', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'INSERT', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 467 Execution Completed")

        @pytest.mark.run(order=468)
        def test_468_start_Worker_logs_to_check_TXT_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 468 Execution Completed")

	@pytest.mark.run(order=469)
        def test_469_Create_TXT_record(self):
                logging.info ("Creating TXT Record for added Zone")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "text.outbound_zone2.com","text": "This a host server","_ref":endpoint,"view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:txt",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("TXT Record is created Successfully")
		print("Test Case 469 Execution Completed")

	@pytest.mark.run(order=470)
        def test_470_stop_Worker_logs_to_check_TXT_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 470 Execution Completed")

        @pytest.mark.run(order=471)
        def test_471_validate_Worker_logs_to_check_Template_for_TXT_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 471 Execution Completed")

	@pytest.mark.run(order=472)
        def test_472_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_TXT_with_match_rule_as_modify(self):
                logging.info("Update Notification rule with record type as TXT with match rule as modify")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_TXT","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "MODIFY","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 472 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=473)
        def test_473_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_TXT_with_match_rule_as_modify(self):
                logging.info("Validating Notification rule with record type as TXT with match rule as modify")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_TXT', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'MODIFY', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 473 Execution Completed")

        @pytest.mark.run(order=474)
        def test_474_start_Worker_logs_to_check_TXT_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 474 Execution Completed")

	@pytest.mark.run(order=475)
        def test_475_Update_TXT_record(self):
                logging.info ("Updating TXT Record for added Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:txt")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"comment":"Updating CNAME Record"}

                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("TXT Record is updated Successfully")
		print("Test Case 475 Execution Completed")

	@pytest.mark.run(order=476)
        def test_476_stop_Worker_logs_to_check_CNAME_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 476 Execution Completed")

        @pytest.mark.run(order=477)
        def test_477_validate_Worker_logs_to_check_Template_for_CNAME_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 477 Execution Completed")

	@pytest.mark.run(order=478)
        def test_478_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_TXT_with_match_rule_as_delete(self):
                logging.info("Update Notification rule with record type as TXT with match rule as delete")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_TXT","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 478 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=479)
        def test_479_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_TXT_with_match_rule_as_delete(self):
                logging.info("Validating Notification rule with record type as TXT with match rule as delete")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_TXT', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 479 Execution Completed")

        @pytest.mark.run(order=480)
        def test_480_start_Worker_logs_to_check_TXT_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 480 Execution Completed")

	@pytest.mark.run(order=481)
        def test_481_Delete_TXT_Record(self):
                logging.info("Deleting TXT record created by template")
                data= {"name": "text.outbound_zone2.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:txt",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
		print("Test Case 481 Execution Completed")

        @pytest.mark.run(order=482)
        def test_482_stop_Worker_logs_to_check_TXT_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 482 Execution Completed")
		
        @pytest.mark.run(order=483)
        def test_483_validate_Worker_logs_to_check_Template_for_TXT_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 483 Execution Completed")

	@pytest.mark.run(order=484)
        def test_484_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_Unknown_with_match_rule_as_insert(self):
                logging.info("Update Notification rule with record type as Unknown with match rule as insert")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_UNKNOWN","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "INSERT","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 484 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=485)
        def test_485_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_Unknown_with_match_rule_as_insert(self):
                logging.info("Validating Notification rule with record type as  with match rule as insert")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_UNKNOWN', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'INSERT', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 485 Execution Completed")

        @pytest.mark.run(order=486)
        def test_486_start_Worker_logs_to_check_Unknown_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 486 Execution Completed")

	@pytest.mark.run(order=487)
        def test_487_Create_Unknown_record(self):
                logging.info ("Creating Unknown Record for added Zone")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name":"spf.outbound_zone2.com","record_type": "SPF","subfield_values": [{"field_value": "v=spf","field_type": "T","include_length": "8_BIT"}]}
                response = ib_NIOS.wapi_request('POST', object_type="record:unknown",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("Unknown Record is created Successfully")
		print("Test Case 487 Execution Completed")

	@pytest.mark.run(order=488)
        def test_488_stop_Worker_logs_to_check_Unknown_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 488 Execution Completed")

        @pytest.mark.run(order=489)
        def test_489_validate_Worker_logs_to_check_Template_for_Unknown_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 489 Execution Completed")
	
	@pytest.mark.run(order=490)
        def test_490_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_Unknown_with_match_rule_as_modify(self):
                logging.info("Update Notification rule with record type as Unknown with match rule as modify")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_UNKNOWN","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "MODIFY","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 490 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=491)
        def test_491_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_Unknown_with_match_rule_as_modify(self):
                logging.info("Validating Notification rule with record type as  with match rule as modify")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'RECORD_TYPE_UNKNOWN', 'op1': 'RECORD_TYPE'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'MODIFY', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_RECORD'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 491 Execution Completed")

        @pytest.mark.run(order=492)
        def test_492_start_Worker_logs_to_check_Unknown_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 492 Execution Completed")

	@pytest.mark.run(order=493)
        def test_493_Update_Unknown_record(self):
                logging.info ("Updating Unknown Record for added Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:unknown")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"comment":"Updating unknown  Record"}

                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("Unknown Record is updated Successfully")
		print("Test Case 493 Execution Completed")

        @pytest.mark.run(order=494)
        def test_494_stop_Worker_logs_to_check_unknown_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 494 Execution Completed")

        @pytest.mark.run(order=495)
        def test_495_validate_Worker_logs_to_check_Template_for_unknown_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 495 Execution Completed")

	@pytest.mark.run(order=496)
        def test_496_Update_DNS_Zone_Notification_Rule_with_Record_Type_As_Unknown_with_match_rule_as_delete(self):
                logging.info("Update Notification rule with record type as Unknown with match rule as delete")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_UNKNOWN","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 496 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=497)
        def test_497_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_Unknown_with_match_rule_as_delete(self):
                logging.info("Validating Notification rule with record type as  with match rule as delete")
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_UNKNOWN","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_temp)
                res=json.loads(get_temp)
                print res
                print("Test Case 497 Execution Completed")

        @pytest.mark.run(order=498)
        def test_498_start_Worker_logs_to_check_Unknown_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 498 Execution Completed")

	@pytest.mark.run(order=499)
        def test_499_Delete_Unknown_Record(self):
                logging.info("Deleting Unknown record created by template")
                data= {"name":"spf.outbound_zone2.com","record_type": "SPF","subfield_values": [{"field_value": "v=spf","field_type": "T","include_length": "8_BIT"}]}
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:unknown",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
		print("Test Case 499 Execution Completed")

        @pytest.mark.run(order=500)
        def test_500_stop_Worker_logs_to_check_Unknown_record_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
		print("Test Case 500 Execution Completed")

        @pytest.mark.run(order=501)
        def test_501_validate_Worker_logs_to_check_Template_for_Unknown_record_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 501 Execution Completed")


	@pytest.mark.run(order=502)
	def test_502_Update_DNS_Zone_Notification_Rule_with_Record_Name_contains_with_match_rule_as_delete(self):
		logging.info("Update DNS_Zone Notification Rule with Record Name contains with match rule_as delete")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "REGEX","op1": "RECORD_NAME","op1_type": "FIELD","op2": "~f","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 502 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=503)
        def test_503_Validate_DNS_Zone_Notification_Rule_with_Record_Name_contains_with_match_rule_as_delete(self):
                logging.info("Validating DNS_Zone Notification Rule with Record Name contains with match rule_as delete")
                get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}, {'op2_type': 'STRING', 'op': 'REGEX', 'op1_type': 'FIELD', 'op2': '~f', 'op1': 'RECORD_NAME'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}, {'op': 'ENDLIST'}"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
		print("Test Case 503 Execution Completed")

	@pytest.mark.run(order=504)
        def test_504_Create_A_record(self):
                logging.info ("Creating A Record for added Zone")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "yfgh.outbound_zone2.com","ipv4addr":"1.2.3.4","_ref":endpoint,"comment":"Adding arec","view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                #import pdb;pdb.set_trace()
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                print("Test Case 504 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=505)
        def test_505_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print("Test Case 505 Execution Completed")

	@pytest.mark.run(order=506)
        def test_506_Delete_A_Record(self):
                logging.info("Deleting A record created by template")
                data= {"name": "yfgh.outbound_zone2.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:a",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
                print("Test Case 506 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=507)
        def test_507_stop_Worker_logs_to_check_Unknown_record_in_outbound_user(self):
                logging.info("Stop Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print("Test Case 507 Execution Completed")

        @pytest.mark.run(order=508)
        def test_508_validate_Worker_logs_to_check_Template_in_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 508 Execution Completed")

	@pytest.mark.run(order=509)
        def test_509_Update_DNS_Zone_Notification_Rule_with_Record_Name_BeginsWith_with_match_rule_as_delete(self):
                logging.info("Update DNS_Zone Notification Rule with Record Name beginswith with match rule_as delete")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "REGEX","op1": "RECORD_NAME","op1_type": "FIELD","op2": "^f","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 509 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=510)
        def test_510_Validate_DNS_Zone_Notification_Rule_with_Record_Name_BeginsWith_with_match_rule_as_delete(self):
                logging.info("Validating DNS_Zone Notification Rule with Record Name BeginsWith with match rule_as delete")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'REGEX', 'op1_type': 'FIELD', 'op2': '^f', 'op1': 'RECORD_NAME'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 510 Execution Completed")

	@pytest.mark.run(order=511)
        def test_511_Create_A_record(self):
                logging.info ("Creating A Record for added Zone")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "fygh.outbound_zone2.com","ipv4addr":"1.2.3.4","_ref":endpoint,"comment":"Adding arec","view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                #import pdb;pdb.set_trace()
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                print("Test Case 511 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=512)
        def test_512_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print("Test Case 512 Execution Completed")

	@pytest.mark.run(order=513)
        def test_513_Delete_A_Record(self):
                logging.info("Deleting A record created by template")
                data= {"name": "fygh.outbound_zone2.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:a",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
                print("Test Case 513 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=514)
        def test_514_stop_Worker_logs_to_check_Unknown_record_in_outbound_user(self):
                logging.info("Stop Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print("Test Case 514 Execution Completed")

        @pytest.mark.run(order=515)
        def test_515_validate_Worker_logs_to_check_Template_in_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 515 Execution Completed")

	@pytest.mark.run(order=516)
        def test_516_Update_DNS_Zone_Notification_Rule_with_Record_Name_EndsWith_with_match_rule_as_delete(self):
                logging.info("Update DNS_Zone Notification Rule with Record Name endswith with match rule_as delete")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "REGEX","op1": "RECORD_NAME","op1_type": "FIELD","op2": "f$","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 516 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=517)
        def test_517_Validate_DNS_Zone_Notification_Rule_with_Record_Name_endswith_with_match_rule_as_delete(self):
                logging.info("Validating DNS_Zone Notification Rule with Record Name endsWith with match rule_as delete")
                get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'REGEX', 'op1_type': 'FIELD', 'op2': 'f$', 'op1': 'RECORD_NAME'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
		print("Test Case 517 Execution Completed")

        @pytest.mark.run(order=518)
        def test_518_Create_A_record(self):
                logging.info ("Creating A Record for added Zone")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "yghf.outbound_zone2.com","ipv4addr":"1.2.3.4","_ref":endpoint,"comment":"Adding arec","view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                #import pdb;pdb.set_trace()
                read  = re.search(r'201',response)
		for read in response:
                    assert True
                print("Test Case 518 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=519)
        def test_519_Delete_A_Record(self):
                logging.info("Deleting A record created by template")
                data= {"name": "yghf.outbound_zone2.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:a",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
                print("Test Case 519 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=520)
        def test_520_stop_Worker_logs_to_check_Unknown_record_in_outbound_user(self):
                logging.info("Stop Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print("Test Case 520 Execution Completed")

        @pytest.mark.run(order=521)
        def test_521_validate_Worker_logs_to_check_Template_in_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 521 Execution Completed")

	@pytest.mark.run(order=522)
        def test_522_Start_DHCP_Service(self):
                logging.info("Start DHCP Service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties")
                logging.info(get_ref)
                res = json.loads(get_ref)
                for i in res:
                        logging.info("Modify a enable_dhcp")
                        data = {"enable_dhcp": True}
                        response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
                        print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
		
		logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")
                print("Test Case 522 Execution Completed")

        @pytest.mark.run(order=523)
        def test_523_Validate_DHCP_service_Enabled(self):
                logging.info("Validate DHCP Service is enabled")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties",params="?_return_fields=enable_dhcp")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                for i in res:
                        print i
                        logging.info("found")
                        assert i["enable_dhcp"] == True
                print("Test Case 523 Execution Completed")

	@pytest.mark.run(order=524)
        def test_524_Start_Discovery_Service(self):
                logging.info("Start Discovery Service")
		get_ref = ib_NIOS.wapi_request('GET', object_type="discovery:memberproperties")
                logging.info(get_ref)
                res = json.loads(get_ref)
                res = eval(json.dumps(res)) 
                print(res[1]['_ref'])
                #print(type(res[1]))
                refer=res[1]['_ref']
                print(refer)
                logging.info("start a enable_service")
                data = {"enable_service": True}
                response = ib_NIOS.wapi_request('PUT', ref=refer,fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
		logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")
                print("Test Case 524 Execution Completed")

        @pytest.mark.run(order=525)
        def test_525_Validate_Discovery_service_Enabled(self):
                logging.info("Validate Discovery Service is enabled")
		get_ref = ib_NIOS.wapi_request('GET', object_type="discovery:memberproperties")
                print(get_ref)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print(ref1)
                get_temp = ib_NIOS.wapi_request('GET',ref=ref1,object_type="discovery:memberproperties",params="?_return_fields=enable_service")
                print(get_temp)
                result='"enable_service": true'
                if result in get_temp:
                        assert True
                else:
                        assert False
                print(result)
                print("Test Case 525 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=526)
	def test_526_create_IPv4_network(self):
                logging.info("Create an ipv4 network default network view")
                data = {"network": "10.40.16.0/24","network_view": "default","members":[{"_struct": "dhcpmember","ipv4addr":config.grid_vip}]}
                response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                read  = re.search(r'201',response)
                for read in  response:
                         assert True
                print("Created the ipv4network 10.40.16.0/24 in default view")
                logging.info("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Test Case 526 Execution Completed")

	@pytest.mark.run(order=527)
        def test_527_Validate_adding_ipv4_DHCP_network(self):
                logging.info("Validate adding ipv4 DHCP network")
                data = {"network": "10.40.16.0/24","network_view": "default"}
		get_temp = ib_NIOS.wapi_request('GET', object_type="network",params="?_inheritance=True&_return_fields=network,network_view")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                res = ''.join(map(str, res))
                print(res)
                data= "'network': '10.40.16.0/24'"
                if data in res:
                        assert True
                else:
                        assert False
		print(data)
                sleep(5)

	@pytest.mark.run(order=528)
        def test_528_Enable_Discovery_Service(self):
		logging.info ("Enable discovery service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="network")
                logging.info(get_ref)
                res = json.loads(get_ref)
                for i in res:
                        logging.info("start a enable_service")
                        data = {"network":"10.40.16.0/24","use_enable_discovery":True,"discovery_member": config.grid_member1_fqdn,"enable_discovery":True,"enable_immediate_discovery": True}
                        response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
                        print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True

		print("Test Case 528 Execution Completed")

	@pytest.mark.run(order=529)
        def test_529_Update_DNS_Zone_Notification_Rule_for_DNS_Discovery_Data_as_match_rule_Discoverer_Beginswith_and_Delete(self):
                logging.info("Update DNS_Zone Notification Rule for discovery data as match rule discoverer Beginswith and delete")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"event_type": "DB_CHANGE_DNS_DISCOVERY_DATA","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "REGEX","op1": "DISCOVERER","op1_type": "FIELD","op2": "^N","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 529 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=530)
        def test_530_Validate_DNS_Zone_Notification_Rule_DNS_Discovery_Data_as_match_rule_Discoverer_Beginswith_and_Delete(self):
                logging.info("Validating DNS Zone Notification Rule for discovery data as match rule discoverer Beginswith and delete")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'REGEX', 'op1_type': 'FIELD', 'op2': '^N', 'op1': 'DISCOVERER'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 530 Execution Completed")


	@pytest.mark.run(order=531)
        def test_531_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print("Test Case 531 Execution Completed")

	@pytest.mark.run(order=532)
        def test_532_Clear_Unmanaged_IP(self):
		network =  ib_NIOS.wapi_request('GET', object_type="network")
                ref = json.loads(network)[0]['_ref']
                data= {"ip_address" : "10.40.16.1","usage":"UNMANAGED","scope": "NETWORK","network":"10.40.16.0/24"}
                response = ib_NIOS.wapi_request('POST', object_type = "network_discovery" + "?_function=clear_discovery_data",fields=json.dumps(data))
		logging.info(response)
                res=json.loads(response)
                print res
                print("Test Case 532 Execution Completed")


	@pytest.mark.run(order=533)
        def test_533_stop_Worker_logs_to_check_Unknown_record_in_outbound_user(self):
                logging.info("Stop Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print("Test Case 533 Execution Completed")

        @pytest.mark.run(order=534)
        def test_534_validate_Worker_logs_to_check_Template_in_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 534 Execution Completed")


	@pytest.mark.run(order=535)
        def test_535_Update_DNS_Zone_Notification_Rule_for_DNS_Discovery_Data_as_match_rule_Discoverer_contains_and_Delete(self):
                logging.info("Update DNS_Zone Notification Rule for discovery data as match rule discoverer contains and delete")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"event_type": "DB_CHANGE_DNS_DISCOVERY_DATA","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "REGEX","op1": "DISCOVERER","op1_type": "FIELD","op2": "~Insight","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 535 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=536)
        def test_536_Validate_DNS_Zone_Notification_Rule_DNS_Discovery_Data_as_match_rule_Discoverer_contains_and_Delete(self):
                logging.info("Validating DNS Zone Notification Rule for discovery data as match rule discoverer contains and delete")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'REGEX', 'op1_type': 'FIELD', 'op2': '~Insight', 'op1': 'DISCOVERER'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
		print("Test Case 536 Execution Completed")

	@pytest.mark.run(order=537)
        def test_537_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print("Test Case 537 Execution Completed")

        @pytest.mark.run(order=538)
        def test_538_Clear_Unmanaged_IP(self):
                network =  ib_NIOS.wapi_request('GET', object_type="network")
                ref = json.loads(network)[0]['_ref']
                data= {"ip_address" : "10.40.16.1","usage":"UNMANAGED","scope": "NETWORK","network":"10.40.16.0/24"}
                response = ib_NIOS.wapi_request('POST', object_type = "network_discovery" + "?_function=clear_discovery_data",fields=json.dumps(data))
                logging.info(response)
                res=json.loads(response)
                print res
                print("Test Case 538 Execution Completed")


        @pytest.mark.run(order=539)
        def test_539_stop_Worker_logs_to_check_Unknown_record_in_outbound_user(self):
                logging.info("Stop Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print("Test Case 539 Execution Completed")

        @pytest.mark.run(order=540)
        def test_540_validate_Worker_logs_to_check_Template_in_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 540 Execution Completed")
	
	@pytest.mark.run(order=541)
        def test_541_Update_DNS_Zone_Notification_Rule_for_DNS_Discovery_Data_as_match_rule_Discoverer_Equals_and_Delete(self):
                logging.info("Update DNS_Zone Notification Rule for discovery data as match rule discoverer equals and delete")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"event_type": "DB_CHANGE_DNS_DISCOVERY_DATA","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "DISCOVERER","op1_type": "FIELD","op2": "Network Insight","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 541 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=542)
        def test_542_Validate_DNS_Zone_Notification_Rule_DNS_Discovery_Data_as_match_rule_Discoverer_Equal_and_Delete(self):
                logging.info("Validating DNS Zone Notification Rule for discovery data as match rule discoverer equal and delete")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'Network Insight', 'op1': 'DISCOVERER'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 542 Execution Completed")

        @pytest.mark.run(order=543)
        def test_543_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print("Test Case 543 Execution Completed")


	@pytest.mark.run(order=544)
        def test_544_Clear_Unmanaged_IP(self):
                network =  ib_NIOS.wapi_request('GET', object_type="network")
                ref = json.loads(network)[0]['_ref']
                data= {"ip_address" : "10.40.16.1","usage":"UNMANAGED","scope": "NETWORK","network":"10.40.16.0/24"}
                response = ib_NIOS.wapi_request('POST', object_type = "network_discovery" + "?_function=clear_discovery_data",fields=json.dumps(data))
                logging.info(response)
                res=json.loads(response)
                print res
                print("Test Case 544 Execution Completed")


        @pytest.mark.run(order=545)
        def test_545_stop_Worker_logs_to_check_Unknown_record_in_outbound_user(self):
                logging.info("Stop Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print("Test Case 545 Execution Completed")

        @pytest.mark.run(order=546)
        def test_546_validate_Worker_logs_to_check_Template_in_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 546 Execution Completed")

	@pytest.mark.run(order=547)
        def test_547_Update_DNS_Zone_Notification_Rule_for_DNS_Discovery_Data_as_match_rule_Discoverer_Endswith_and_Delete(self):
                logging.info("Update DNS_Zone Notification Rule for discovery data as match rule discoverer Endswith and delete")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"event_type": "DB_CHANGE_DNS_DISCOVERY_DATA","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "REGEX","op1": "DISCOVERER","op1_type": "FIELD","op2": "t$","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 547 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=548)
        def test_548_Validate_DNS_Zone_Notification_Rule_DNS_Discovery_Data_as_match_rule_Discoverer_Endswith_and_Delete(self):
                logging.info("Validating DNS Zone Notification Rule for discovery data as match rule discoverer endswith and delete")
                get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'REGEX', 'op1_type': 'FIELD', 'op2': 't$', 'op1': 'DISCOVERER'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
		print("Test Case 548 Execution Completed")

        @pytest.mark.run(order=549)
        def test_549_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print("Test Case 549 Execution Completed")

	@pytest.mark.run(order=550)
        def test_550_Clear_Unmanaged_IP(self):
                network =  ib_NIOS.wapi_request('GET', object_type="network")
                ref = json.loads(network)[0]['_ref']
                data= {"ip_address" : "10.40.16.1","usage":"UNMANAGED","scope": "NETWORK","network":"10.40.16.0/24"}
                response = ib_NIOS.wapi_request('POST', object_type = "network_discovery" + "?_function=clear_discovery_data",fields=json.dumps(data))
                logging.info(response)
                res=json.loads(response)
                print res
                print("Test Case 550 Execution Completed")


        @pytest.mark.run(order=551)
        def test_551_stop_Worker_logs_to_check_Unknown_record_in_outbound_user(self):
                logging.info("Stop Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print("Test Case 541 Execution Completed")

        @pytest.mark.run(order=552)
        def test_552_validate_Worker_logs_to_check_Template_in_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 552 Execution Completed")


	@pytest.mark.run(order=553)
        def test_553_Update_DNS_Zone_Notification_Rule_for_DNS_Discovery_Data_as_match_rule_IP_ADDRESS_Equals_and_Delete(self):
                logging.info("Update DNS_Zone Notification Rule for discovery data as match rule IP_ADDRESS equals and delete")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"event_type": "DB_CHANGE_DNS_DISCOVERY_DATA","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "IP_ADDRESS","op1_type": "FIELD","op2": "10.40.16.30","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 553 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=554)
        def test_554_Validate_DNS_Zone_Notification_Rule_DNS_Discovery_Data_as_match_rule_IP_ADDRESS_Equals_and_Delete(self):
                logging.info("Validating DNS Zone Notification Rule for discovery data as match rule IP_ADDRESS equals and delete")
                get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': '10.40.16.30', 'op1': 'IP_ADDRESS'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
		print("Test Case 554 Execution Completed")

        @pytest.mark.run(order=555)
        def test_555_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print("Test Case 555 Execution Completed")

	@pytest.mark.run(order=556)
        def test_556_Clear_Unmanaged_IP(self):
                network =  ib_NIOS.wapi_request('GET', object_type="network")
                ref = json.loads(network)[0]['_ref']
                data= {"ip_address" : "10.40.16.30","usage":"UNMANAGED","scope": "NETWORK","network":"10.40.16.0/24"}
                response = ib_NIOS.wapi_request('POST', object_type = "network_discovery" + "?_function=clear_discovery_data",fields=json.dumps(data))
                logging.info(response)
                res=json.loads(response)
                print res
                print("Test Case 556 Execution Completed")


        @pytest.mark.run(order=557)
        def test_557_stop_Worker_logs_to_check_Unknown_record_in_outbound_user(self):
                logging.info("Stop Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print("Test Case 557 Execution Completed")

        @pytest.mark.run(order=558)
        def test_558_validate_Worker_logs_to_check_Template_in_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 558 Execution Completed")

	@pytest.mark.run(order=559)
        def test_559_Update_DNS_Zone_Notification_Rule_for_DNS_Discovery_Data_as_match_rule_IP_ADDRESS_MATCH_RANGE_and_Delete(self):
                logging.info("Update DNS_Zone Notification Rule for discovery data as match rule IP_ADDRESS MATCH_RANGE and delete")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"event_type": "DB_CHANGE_DNS_DISCOVERY_DATA","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "MATCH_RANGE","op1": "IP_ADDRESS","op1_type": "FIELD","op2": "10.40.16.0-10.40.16.10","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 559 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=560)
        def test_560_Validate_DNS_Zone_Notification_Rule_DNS_Discovery_Data_as_match_rule_IP_ADDRESS_MATCH_RANGE_and_Delete(self):
                logging.info("Validating DNS Zone Notification Rule for discovery data as match rule IP_ADDRESS MATCH_RANGE and delete")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "{'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'MATCH_RANGE', 'op1_type': 'FIELD', 'op2': '10.40.16.0-10.40.16.10', 'op1': 'IP_ADDRESS'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}","'event_type': 'DB_CHANGE_DNS_DISCOVERY_DATA'"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
		logging.info("Test Case 560 Execution Completed")

        @pytest.mark.run(order=561)
        def test_561_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print("Test Case 561 Execution Completed")

	@pytest.mark.run(order=562)
        def test_562_Clear_Unmanaged_IP(self):
                network =  ib_NIOS.wapi_request('GET', object_type="network")
                ref = json.loads(network)[0]['_ref']
                data= {"ip_address" : "10.40.16.9","usage":"UNMANAGED","scope": "NETWORK","network":"10.40.16.0/24"}
                response = ib_NIOS.wapi_request('POST', object_type = "network_discovery" + "?_function=clear_discovery_data",fields=json.dumps(data))
                logging.info(response)
                res=json.loads(response)
                print res
                print("Test Case 562 Execution Completed")


        @pytest.mark.run(order=563)
        def test_563_stop_Worker_logs_to_check_Unknown_record_in_outbound_user(self):
                logging.info("Stop Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print("Test Case 563 Execution Completed")

        @pytest.mark.run(order=564)
        def test_564_validate_Worker_logs_to_check_Template_in_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 564 Execution Completed")

	@pytest.mark.run(order=565)
        def test_565_Update_DNS_Zone_Notification_Rule_for_DNS_Discovery_Data_as_match_rule_IS_IPV4_and_Delete(self):
                logging.info("Update DNS_Zone Notification Rule for discovery data as match rule IS_IPV4 and delete")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"event_type": "DB_CHANGE_DNS_DISCOVERY_DATA","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "IS_IPV4","op1_type": "FIELD","op2": "TRUE","op2_type": "STRING"},{"op": "EQ","op1": "OPERATION_TYPE","op1_type": "FIELD","op2": "DELETE","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 565 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=566)
        def test_566_Validate_DNS_Zone_Notification_Rule_DNS_Discovery_Data_as_match_rule_IS_IPV4_and_Delete(self):
                logging.info("Validating DNS Zone Notification Rule for discovery data as match rule IS_IPV4 and delete")
		get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=event_type,expression_list")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                print(res)
                res = ''.join(map(str, res))
                output = "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'TRUE', 'op1': 'IS_IPV4'}", "{'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'DELETE', 'op1': 'OPERATION_TYPE'}", "{'op': 'ENDLIST'}"
                for values in output:
                       if values in res:
                                assert True
                       else:
                                assert False
                print(output)
                print("Test Case 566 Execution Completed")

        @pytest.mark.run(order=567)
        def test_567_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print("Test Case 567 Execution Completed")

	@pytest.mark.run(order=568)
        def test_568_Clear_Unmanaged_IP(self):
                network =  ib_NIOS.wapi_request('GET', object_type="network")
                ref = json.loads(network)[0]['_ref']
                data= {"ip_address" : "10.40.16.9","usage":"UNMANAGED","scope": "NETWORK","network":"10.40.16.0/24"}
                response = ib_NIOS.wapi_request('POST', object_type = "network_discovery" + "?_function=clear_discovery_data",fields=json.dumps(data))
                logging.info(response)
                res=json.loads(response)
                print res
                print("Test Case 568 Execution Completed")


        @pytest.mark.run(order=569)
        def test_569_stop_Worker_logs_to_check_Unknown_record_in_outbound_user(self):
                logging.info("Stop Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print("Test Case 569 Execution Completed")

        @pytest.mark.run(order=570)
        def test_570_validate_Worker_logs_to_check_Template_in_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution in Outbound_user")
                LookFor="The template was executed successfully"
		result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 570 Execution Completed")


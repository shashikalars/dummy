import re
import config
import pytest
import unittest
import logging
import os
import pexpect
import sys
import os.path
from os.path import join
import subprocess
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util


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
                logging.info("Configured Global Forwarders Logging Categories Allow Recursion At Grid level")
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
        def test_004_Validate_Configured_Global_Forwarders_Logging_Categories_Allow_Recursion_At_Grid_level(self):
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
 
	@pytest.mark.run(order=5)
        def test_005_Start_Discovery_Service_at_grid_level(self):
                logging.info("Start Discovery Service at grid level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="discovery:memberproperties")
                print(get_ref)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[-1]['_ref']
                print(ref1)
                logging.info("start a enable_service")
                data = {"enable_service": True}
                response = ib_NIOS.wapi_request('PUT', ref=ref1,fields=json.dumps(data))
                print response
                logging.info(response)
                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
		sleep(100)
                logging.info("System Restart is done successfully")
                print("Test Case 5 Execution Completed")

	@pytest.mark.run(order=6)
        def test_006_Validate_Discovery_service_Enabled_at_grid_level(self):
                logging.info("Validate Discovery Service is enabled at grid level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="discovery:memberproperties")
                print(get_ref)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[-1]['_ref']
                print(ref1)
                get_temp = ib_NIOS.wapi_request('GET',ref=ref1,object_type="discovery:memberproperties",params="?_return_fields=enable_service")
                print(get_temp)
          	result='"enable_service": true' 
		if result in get_temp:
                        assert True
                else:
                        assert False
 		print(result)
                print("Test Case 6 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=7)
        def test_007_Test_Hidden_CLI_command_to_check_RabbitMQ_queues_when_no_services_are_running(self):
               logging.info("Hidden CLI command to check RabbitMQ queues when no services are running")
               child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
               child.logfile=sys.stdout
               child.expect('password:')
               child.sendline('infoblox')
               child.expect('Infoblox >')
               child.sendline('show rabbitmq_queues')
	       child.expect('Infoblox >')
               output = child.before
               print(output)
               result = 'Listing queues'
	       if result in output:
	       		assert True
	       else:
			assert False
               print(result)
               print("\nTest Case 7 Executed Successfully")

	@pytest.mark.run(order=8)
        def test_008_Test_Hidden_CLI_command_to_check_RabbitMQ_queues_to_get_grid_info(self):
               logging.info("Hidden CLI command to check RabbitMQ queues to get grid info")
               child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
               child.logfile=sys.stdout
               child.expect('password:')
               child.sendline('infoblox')
               child.expect('Infoblox >')
               child.sendline('show rabbitmq_queues')
               child.expect('Infoblox >')
               sleep(10)
	       output = child.before
	       result = [config.grid_member_fqdn,config.grid_member2_fqdn,config.grid_member1_fqdn]
               for values in result:
                if values in output:
                        assert True
                else:
                        assert False
		print(result)

               print("\nTest Case 8 Executed Successfully")


	@pytest.mark.run(order=9)
        def test_009_Test_Hidden_CLI_command_to_check_RabbitMQ_queues_checking_negative_scenario(self):
               logging.info("Hidden CLI command to check RabbitMQ queues checking negative scenario")
               child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
               child.logfile=sys.stdout
               child.expect('password:')
               child.sendline('infoblox')
               child.expect('Infoblox >')
               child.sendline('show rabbitmq_queues')
	       child.expect('Infoblox >')
               output = child.before
               print(output)
	       result = 'analytics_dnst_blacklist_queue'
               if result in output:
                        assert False
               else:
                        assert True
               print("\nTest Case 9 Executed Successfully")

	@pytest.mark.run(order=10)
    	def test_010_add_rpz_zone_added_in_the_grid(self):
                logging.info("Create Local RPZ Zone")
                grid_member=config.grid_member_fqdn
                data = {"fqdn":"rpz.com","rpz_type": "LOCAL","grid_primary": [{"name":config.grid_member_fqdn}],"rpz_severity": "MAJOR","rpz_type": "LOCAL"}
                response = ib_NIOS.wapi_request('POST', object_type="zone_rp", fields=json.dumps(data))
		print(response)
                res=json.loads(response)
                logging.info(response)
                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")
		print("Test Case 10 Execution Completed")
                sleep(5)
       
	@pytest.mark.run(order=11)
        def test_011_Validate_RPZ_zone_added_in_the_grid(self):
                logging.info("Validate RPZ zone added in the grid")
		get_ref = ib_NIOS.wapi_request('GET',object_type="zone_rp",grid_vip=config.grid_vip)
		print(get_ref)
		result = ['"fqdn": "rpz.com"','"view": "default"']
		for i in result:
			if i in get_ref:
				assert True
			else:
				assert False
		print(result)
                logging.info("Test Case 11 Execution Completed")
                logging.info("============================")

	@pytest.mark.run(order=12)
        def test_012_add_RPZ_zone_to_threat_analytics(self):
		logging.info("Validate RPZ zone added in the grid")
        	get_ref=ib_NIOS.wapi_request('GET', object_type="zone_rp")
        	getref1=json.loads(get_ref)
        	data={"dns_tunnel_black_list_rpz_zones":[getref1[0]['_ref']]}
        	get_ref=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics")
        	logging.info(get_ref)
        	get_ref1=json.loads(get_ref)[0]['_ref']
        	get_ref_of_TA=ib_NIOS.wapi_request('PUT', object_type=get_ref1,fields=json.dumps(data))
		print(get_ref_of_TA)
        	logging.info(get_ref_of_TA)
        	if type(get_ref_of_TA)!=tuple:
            		logging.info(get_ref_of_TA)
            		logging.info("Test case 12 passed")
            		assert True
        	else:
            		logging.info("Test case 12 failed")
            		assert False

	@pytest.mark.run(order=13)
        def test_013_starting_and_validating_threat_analytics_in_the_grid(self):
		logging.info("Starting and validating threat analytics in the grid")
        	members=[]
        	get_ref=ib_NIOS.wapi_request('GET', object_type="member:threatanalytics")
        	get_ref=json.loads(get_ref)
        	for i in get_ref:
            		members.append(i["_ref"])
        	for ref in members:
            		data={"enable_service":True}
            		get_ref_of_TA=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
			print(get_ref_of_TA)
            		sleep(10)
        		grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        		ref = json.loads(grid)[0]['_ref']
        		publish={"member_order":"SIMULTANEOUSLY"}
        		request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        		sleep(20)
        		request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        		restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        		sleep(30)
        		logging.info("Restarting the grid ")
        	for i in members:
            		get_ref=ib_NIOS.wapi_request('GET', object_type=i)
            		get_ref1=json.loads(get_ref)
            	if get_ref1["status"]=="WORKING":
                	assert True
                	logging.info("Test case 13 passed as threat analytics is running")
            	else:
                	assert False
                	logging.info("Test case 13 failed as threat analytics is not running")

	@pytest.mark.run(order=14)
        def test_014_Test_Hidden_CLI_command_to_check_RabbitMQ_queues_when_Threat_Analytics_started(self):
	       logging.info("Hidden CLI command to check RabbitMQ queues when threat analytics started")
               child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
               child.logfile=sys.stdout
               child.expect('password:')
               child.sendline('infoblox')
               child.expect('Infoblox >')
               child.sendline('show rabbitmq_queues')
	       child.expect('Infoblox >')
               output = child.before
               print(output)
	       result='analytics_dnst_blacklist_queue'
               if result in output:
                        assert True
               else:
                        assert False
	       print(result)
               print("\nTest Case 14 Executed Successfully")

	@pytest.mark.run(order=15)
	def test_015_Test_Hidden_CLI_command_to_check_RabbitMQ_queues_to_get_grid_info_in_the_member(self):
               logging.info("Hidden CLI command to check RabbitMQ queues in the member")
               child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
               child.logfile=sys.stdout
               child.expect('password:')
               child.sendline('infoblox')
               child.expect('Infoblox >')
               child.sendline('show rabbitmq_queues')
               child.expect('Infoblox >')
               sleep(10)
               output = child.before
               #print(output)
	       result = [config.grid_member_fqdn,config.grid_member2_fqdn,config.grid_member1_fqdn]
	       for values in result: 
               	if values in output:
                        assert True
               	else:
                        assert False
	       print(result)
               print("\nTest Case 15 Executed Successfully")

#Upload Templates

        @pytest.mark.run(order=16)
        def test_016_Upload_REST_API_Session_Template(self):
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
                print("Test Case 16 Execution Completed")

        @pytest.mark.run(order=17)
        def test_017_Validate_Adding_REST_API_Session_Template(self):
                logging.info("Validating Addition of REST API session Template")
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
                logging.info("Test Case 17 Execution Completed")
                logging.info("============================")

                sleep(5)

	@pytest.mark.run(order=18)
        def test_018_Upload_DNS_Records_Event_Template(self):
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
                print("Test Case 18 Execution Completed")

        @pytest.mark.run(order=19)
        def test_019_Validate_Adding_DNS_Records_Event_Template(self):
                logging.info("Validating addition of DNS RECORDS Version5 Event Template")
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
                logging.info("Test Case 19 Execution Completed")
                logging.info("============================")

                sleep(5)

#Add REST API endpoint

        @pytest.mark.run(order=20)
        def test_020_Add_REST_API_endpoint(self):
                logging.info("Add REST API endpoint")
                data = {"name": "rest_api_endpoint1", "uri": "https://"+config.grid_vip,"outbound_member_type": "GM","username": "admin","password": "infoblox","wapi_user_name": "admin", "wapi_user_password": "infoblox","template_instance": {"template": "Version5_REST_API_Session_Template"},"server_cert_validation": "NO_VALIDATION","log_level": "DEBUG"}
                response = ib_NIOS.wapi_request('POST', object_type="notification:rest:endpoint", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                sleep(10)
                print("Test Case 20 Execution Completed")

        @pytest.mark.run(order=21)
        def test_021_Validating_REST_API_endpoint(self):
                logging.info("Validating REST API endpoint")
		data = {"name": "rest_api_endpoint1", "uri": "https://"+config.grid_vip,"outbound_member_type": "GM","username": "admin","password": "infoblox","wapi_user_name": "admin", "wapi_user_password": "infoblox","template_instance": {"template": "Version5_REST_API_Session_Template"},"server_cert_validation": "NO_VALIDATION","log_level": "DEBUG"}
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
                print("Test Case 21 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=22)
        def test_022_Add_DNS_Zone_Notification_Rule_with_Zone_Type_As_Authoritative(self):
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
                print("Test Case 22 Execution Completed")

        @pytest.mark.run(order=23)
        def test_023_Validate_Adding_Notification_Rule(self):
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
                print("Test Case 23 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=24)
        def test_024_Test_Hidden_CLI_command_to_validate_RabbitMQ_queues_when_outbound_service_started(self):
               logging.info("Hidden CLI command to validate RabbitMQ queues when outbound service started")
               child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
               child.logfile=sys.stdout
               child.expect('password:')
               child.sendline('infoblox')
               child.expect('Infoblox >')
               child.sendline('show rabbitmq_queues')
               #output = child.before
               #print(output)
               child.expect('Infoblox >')
               sleep(5)
               output = child.before
               #print(output)
               result = 'outbound.rest_api'
               if result in output:
                        assert True
               else:
                        assert False
               print("\n")
               print(result)
               print("\nTest Case 24 Executed Successfully")
	

	@pytest.mark.run(order=25)
        def test_025_reboot_gridmaster_to_validate_queuesize(self):
               logging.info("reboot grid master tovalidate queue size")
               child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
               child.logfile=sys.stdout
               child.expect('password:')
               child.sendline('infoblox')
               child.expect('Infoblox >')
               child.sendline('reboot')
               child.expect('\(y or n\):')
	       child.sendline('y')
               print("\nTest Case 25 Executed Successfully")
	       sleep(20)

	@pytest.mark.run(order=26)
        def test_026_Test_Hidden_CLI_command_in_gridmember_to_validate_RabbitMQ_queuesize_in_Gridmember_chaging_for_GM(self):
               logging.info("Hidden CLI command in grid member to validate RabbitMQ queuesize in Grid member changing for GM")
               child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
               child.logfile=sys.stdout
               child.expect('password:')
               child.sendline('infoblox')
               child.expect('Infoblox >')
               child.sendline('show rabbitmq_queues')
               child.expect('Infoblox >')
               sleep(10)
               output = child.before
               #print(output)
	       result='to_gm'
               if result in output:
                        assert True
               else:
                        assert False
	       print("\n")
	       print(result)
	       print("\nTest Case 26 Executed Successfully")


	@pytest.mark.run(order=27)
        def test_027_reboot_gridmemeber_to_validate_RabbitMQ_queuesize_of_gridmember(self):
               logging.info("reboot grid member to validate RabbitMQ queuesize of grid member")
               child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
               child.logfile=sys.stdout
               child.expect('password:')
               child.sendline('infoblox')
               child.expect('Infoblox >')
               child.sendline('reboot')
               child.expect('\(y or n\):')
               child.sendline('y')
               output = child.before
               print("\nTest Case 27 Executed Successfully")
               sleep(500)


	@pytest.mark.run(order=28)
        def test_028_Test_Hidden_CLI_command_to_check_RabbitMQ_queuesize_for_rebooting_member_in_GM(self):
               logging.info("Hidden CLI command to check RabbitMQ queues for rebooting member in GM")
	       child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
	       child.logfile=sys.stdout
               child.expect('password:')
               child.sendline('infoblox')
               child.expect('Infoblox >')
               child.sendline('show rabbitmq_queues')
	       child.expect('Enter <return> for next page or q<return> to cancel the command')
	       output = child.before
               child.sendline('\r')
               child.expect('Infoblox >')
               sleep(10)
               #output = child.before
	       print("output is",output)
               result = "to_member1"
               if result in output:
                        assert True
               else:
                        assert False
               print("\n")
               print(result)
	       sleep(10)
               print("\nTest Case 28 Executed Successfully")

	@pytest.mark.run(order=29)
        def test_029_Make_Member_as_GMC_in_Admin_Local(self):
                logging.info("Making Member as GMC in Admin Local")
                grid_member=config.grid_member1_fqdn
                grid =  ib_NIOS.wapi_request('GET', object_type="member")
                ref = json.loads(grid)[1]['_ref']
                print("The reference of member is ",ref)
                data={"master_candidate": True}
                gmc = ib_NIOS.wapi_request('PUT',ref=ref,object_type ="member",fields=json.dumps(data))
		print(gmc)
                print("The Member is made as GMC Successfully")
		get_temp = ib_NIOS.wapi_request('GET', object_type="member",ref=ref,params="?_return_fields=master_candidate")
                print(get_temp)
                result = '"master_candidate": true'
                if result in get_temp:
                      assert True
                else:
                      assert False
                print(result)
   		print("\nTest Case 29 Executed Successfully")
		sleep(500)

      	@pytest.mark.run(order=30)
        def test_030_promote_member_as_master(self):
               logging.info("promote member as master")
               child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
               child.logfile=sys.stdout
               child.expect('password:')
               child.sendline('infoblox')
               child.expect('Infoblox >')
               child.sendline('set promote_master')
	       child.expect('Do you want a delay between notification to grid members\? \(y or n\): ')
	       child.sendline('y')
               child.expect(': ')
               child.sendline('30')
	       #child.expect('Are you sure you want to do this\? \(y or n\): ')
               child.expect(': ')
               child.sendline('y')
	       child.expect(': ')
	       child.sendline('y')
               child.expect('Master promotion beginning on this member')
               #print(output)
               print("\nTest Case 30 Executed Successfully")
               sleep(700)

	@pytest.mark.run(order=31)
        def test_031_Test_Hidden_CLI_command_to_check_RabbitMQ_queues_to_get_queuesize_of_current_Gridmember(self):
               logging.info("Hidden CLI command to check RabbitMQ queues to get queuesize of current Gridmember")
               child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
               child.logfile=sys.stdout
               child.expect('password:')
               child.sendline('infoblox')
               child.expect('Infoblox >')
               child.sendline('show rabbitmq_queues')
               #child.expect('Enter <return> for next page or q<return> to cancel the command')
               #child.sendline('\r')
	       child.expect('Infoblox >')
               sleep(10)
               output = child.before
               print("output is",output)
               result='to_member0'
               if result in output:
                        assert True
               else:
                        assert False
               print("\n")
               print(result)
	       print("\nTest Case 31 Executed Successfully")

	@pytest.mark.run(order=32)
        def test_032_Test_Rabbitmq_queues_command_in_Expertmode(self):
               logging.info("Test RabbitMQ queue command in Expertmode")
               child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
               child.logfile=sys.stdout
               child.expect('password:')
               child.sendline('infoblox')
               child.expect('Infoblox >')
               child.sendline('set expertmode')
               child.expect('"Disclaimer: The expert mode CLI commands are designed for advanced users.')
	       sleep(5)
               child.expect('Expert Mode >')
	       child.sendline('show rabbitmq_queues')
               #print(output)
               #child.expect('Enter <return> for next page or q<return> to cancel the command')
               #child.sendline('\r')
               #sleep(10)
	       child.expect('Expert Mode >')
	       output = child.before
	       result = [config.grid_member_fqdn,config.grid_member2_fqdn,config.grid_member1_fqdn]
               for values in result:
                if values in output:
                        assert True
                else:
                        assert False
               print(result)
               print("\nTest Case 32 Executed Successfully")
               sleep(20)

	@pytest.mark.run(order=33)
        def test_033_Test_Rabbitmq_queues_command_in_Maintenancemode(self):
               logging.info("Test RabbitMQ queues command in Maintenance Mode")
               child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
               child.logfile=sys.stdout
               child.expect('password:')
               child.sendline('infoblox')
               child.expect('Infoblox >')
               child.sendline('set maintenancemode')
               child.expect('Maintenance Mode >')
	       child.sendline('show rabbitmq_queues')
               #print(output)
               #child.expect('Enter <return> for next page or q<return> to cancel the command')
               #child.sendline('\r')
               child.expect('Maintenance Mode >')
	       output = child.before
               #sleep(10)
	       result = [config.grid_member_fqdn,config.grid_member2_fqdn,config.grid_member1_fqdn]
               for values in result:
                if values in output:
                        assert True
                else:
                        assert False
               print(result)
               print("\nTest Case 33 Executed Successfully")
	       

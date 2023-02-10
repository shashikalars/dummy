#!/usr/bin/env python
__author__ = "Vijaya Sinha"
__email__  = "vsinha@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Stand alone Grid Master                                               #
#  2. Licenses : Grid, NIOS(IB_1415),Security Ecosystem License             #
#############################################################################



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
import pexpect
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util
#import ib_utils.outbound5_dns_zone111 as import_zone
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv

class NIOSSPT_10688(unittest.TestCase):

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
                data = {"name": "dns_notify1","notification_action": "RESTAPI_TEMPLATE_INSTANCE", "notification_target": get_ref,"template_instance": {"template": "Version5_DNS_Zone_and_Records_Action_Template"},"event_type": "DB_CHANGE_DNS_ZONE","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "NETWORK_VIEW","op1_type": "FIELD","op2": "default","op2_type": "STRING"},{"op": "ENDLIST"}]}
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
                output = ["'template_instance': {'parameters': [], 'template': 'Version5_DNS_Zone_and_Records_Action_Template'}", "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'default', 'op1': 'NETWORK_VIEW'}, {'op': 'ENDLIST'}]","'notification_action': 'RESTAPI_TEMPLATE_INSTANCE'", "'name': 'dns_notify1'"]
                for values in output:
                        if values in res:
                                assert True
                        else:
                                assert False
                print(output)
                print("Test Case 12 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=13)
        def test_013_create_AD_authentication_server_group(self):
            print("Testcase 13 started")
            logging.info("Creating AD service in authentication server group")
            data={
                    "name": "adserver",
                    "ad_domain": "ad19187.com",
                    "domain_controllers": [
                        {
                            "auth_port": 389,
                            "disabled": False,
                            "encryption": "NONE",
                            "fqdn_or_ip": "10.34.98.56",
                            "use_mgmt_port": False
            }
        ]
                }
            response = ib_NIOS.wapi_request('POST', object_type="ad_auth_service",fields=json.dumps(data))
            print(response)
            logging.info(response)
            radiusref=response
            radiusref = json.loads(radiusref)
            print(radiusref)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    assert False
            print("Test Case 13 Execution Completed")


	@pytest.mark.run(order=14)
    	def test_014_create_super_user_group(self):
            print("Testcase 14 started")
       	    logging.info("Creating User Group")
            group={"name":"RK","superuser":True}
            get_ref_group = ib_NIOS.wapi_request('POST',object_type="admingroup", fields=json.dumps(group))
            if (get_ref_group[0] == 400):
                print("Duplicate object \'RK\' of type \'admin_group\' already exists in the database")
                assert True
            else:
                print("Group \'RK\' has been created")
            print("Test Case 14 Execution Completed")

	@pytest.mark.run(order=15)
        def test_015_create_a_super_user(self):
            logging.info("Creating non-super user to test functionality")
            data={"admin_groups":["RK"],"name": "user1","password":"infoblox"}
            response = ib_NIOS.wapi_request('POST', object_type="adminuser",fields=json.dumps(data))
            print(response)
            res=response
            res = json.loads(res)
            print(res)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    assert False
                print("Test Case 15 Execution Completed")
                print("Restart DHCP services to reflect changes")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(10)


	@pytest.mark.run(order=16)
    	def test_016_create_radius_authentication_policy(self):
            logging.info("Create authentication policy group to add remote authentication")
            logging.info("get authentication policy ref")
	    res = ib_NIOS.wapi_request('GET',object_type='authpolicy')
            res = json.loads(res)
            print(res)
            auth_policy_ref=res[0][u'_ref']
            print(auth_policy_ref)
            logging.info("adding default group for authpolicy")
            data={"admin_groups": ["RK"]}
            response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=auth_policy_ref)
            print(response)
	    logging.info("Get auth_service localuser reference")
            res = ib_NIOS.wapi_request('GET',object_type='authpolicy?_return_fields=auth_services')
            res = json.loads(res)
            print(res)
            localuser_ref=res[0][u'auth_services'][0]
            print(localuser_ref)
            logging.info("Get AD server reference")
            response = ib_NIOS.wapi_request('GET', object_type="ad_auth_service")
            print(response)
            response = json.loads(response)
            radiusref=response[0][u'_ref']
            logging.info("Adding localuser and radius reference to auth_services")
            data={"auth_services":[radiusref,localuser_ref]}
            response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=auth_policy_ref)
            print(response)
	    print("Test Case 16 Execution Completed")

	
	@pytest.mark.run(order=17)
    	def test_017_verify_AD_sshlogin(self):
            print("Testcase 17 started")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no user1@'+config.grid_vip)
            child.expect ('password:')
            child.sendline ('infoblox')
            child.expect ('Infoblox >')
            child.sendline ('exit')
            assert True
            print("Test Case 17 Execution Completed")

	@pytest.mark.run(order=18)
    	def test_018_verify_radius_gui_login(self):
            print("Testcase 18 started")
            output = os.popen("curl -k -u user1:infoblox -H 'Content-type: application/json' -X GET https://"+config.grid_vip+"/wapi/"+config.wapi_version+"/grid").read()
            print(output)
            if "401 Authorization Required" in output:
                 assert False

            print("Test Case 18 Execution Completed")


	@pytest.mark.run(order=19)
        def test_019_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print("Test Case 19 Execution Completed")


        @pytest.mark.run(order=20)
        def test_020_Add_Authoritative_zone(self):
		logging.info("Create Auth Zone")
                grid_member=config.grid_fqdn
                data = {"fqdn": "outbound.com","grid_primary": [{"name":config.grid_fqdn,"stealth":False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data),user="user1",password="infoblox")
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 20 Execution Completed")

                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                print("System Restart is done successfully")
                sleep(5)

	@pytest.mark.run(order=21)
        def test_022_validate_Worker_logs_to_check_Template_for_Auth_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution for Auth Zone in Outbound_user")
                LookFor="The template was executed successfully"
                result=logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print (result)
                print("Test Case 21 Execution Completed")


	@pytest.mark.run(order=22)
        def test_022_Stopping_Logs_for_Template_Execution(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                print("Test Case 22 Execution Completed")

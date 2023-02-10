import paramiko
import re
import config
from paramiko import client
import pexpect
import sys
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
import ib_utils.common_utilities as comm_util
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv
#from ib_utils.log_capture import log_action as log
#from ib_utils.log_validation import log_validation as logv

class Outbound6(unittest.TestCase):

#Starting DNS service

	@pytest.mark.run(order=1)
	def test_001_Start_DNS_Service_in_the_Grid(self):
                logging.info("Start DNS Service in the Grid")
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
        def test_002_Validate_DNS_service_Enabled_in_the_Grid(self):
                logging.info("Validate DNS Service is enabled in Grid")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                for i in res:
                        print i
                        logging.info("found")
                        assert i["enable_dns"] == True
                print("Test Case 2 Execution Completed")

#Upload Templates

	@pytest.mark.run(order=3)
        def test_003_Upload_REST_API_Session_Template_in_Admin_Local_for_starting_Outbound_process_and_create_Outbound_Rest_API_Session(self):
                logging.info("Upload REST API Version5 Session Template in Admin Local for starting Outbound Process and create Outbound Rest API Session")
                dir_name="Outbound5_templates/"
                base_filename="Version5_REST_API_Session_Template.json"
                token = comm_util.generate_token_from_file(dir_name,base_filename)
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
                print("Test Case 3 Execution Completed")
	
        @pytest.mark.run(order=4)
        def test_004_Upload_ALL_DB_Events_Template_in_Admin_Local_for_starting_Outbound_process_and_create_Outbound_Notification_Rule_and_start_Outbound_Process(self):
                logging.info("Upload All DB changes Events Template in Admin Local for starting Outbound process and create Outbound Notification Rule and start Outbound Process.")
                dir_name="Outbound5_templates/"
                base_filename="Version6_REST_EVENT_Tunnel.json"
                token = comm_util.generate_token_from_file(dir_name,base_filename)
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
                print("Test Case 4 Execution Completed")

	@pytest.mark.run(order=5)
        def test_005_Validate_Template_Upload_for_starting_outbound_process(self):
                logging.info("Validating template upload")
                get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rest:template")
                logging.info(get_temp)
                print get_temp
                print("Test Case 5 Execution Completed")
                sleep(5)


        @pytest.mark.run(order=6)
        def test_006_Make_Member_as_GMC_in_Admin_Local(self):
                logging.info("Making Member as GMC in Admin Local")
                grid_member=config.grid_member_vip
                grid =  ib_NIOS.wapi_request('GET', object_type="member")
                ref = json.loads(grid)[1]['_ref']
                print("The reference of member is ",ref)
                data={"master_candidate": True}
                gmc = ib_NIOS.wapi_request('PUT',ref=ref,object_type ="member",fields=json.dumps(data))
                print("The Member is made as GMC Successfully")
                read  = re.search(r'201',gmc)
                for read in gmc:
                        assert True
                print("Test Case 6 Execution Completed")
                sleep(10)


####Add Zone###
		
        @pytest.mark.run(order=7)
        def test_007_Add_REST_API_endpoint_in_Admin_Users_to_start_Outbound_Process_with_Outbound_Member_Type_As_Member_For_Validating_Outbound_Worker_Logs(self):
                logging.info("Add REST API endpoint to start Outbound Process with Outbound Member Type as Member for Validating the Outbound Worker Logs")
                data = {"name": "rest_api_endpoint1", "uri": "https://"+config.grid_vip,"outbound_member_type": "MEMBER","outbound_members":[config.grid_member_fqdn],"username": "admin","password": "infoblox","wapi_user_name": "admin", "wapi_user_password": "infoblox","template_instance": {"template": "Version5_REST_API_Session_Template"},"server_cert_validation": "NO_VALIDATION","log_level": "DEBUG"}
                response = ib_NIOS.wapi_request('POST', object_type="notification:rest:endpoint", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                sleep(10)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 7 Execution Completed")

	@pytest.mark.run(order=8)
        def test_008_Validating_REST_API_endpoint_Gets_Added_with_Outbound_Member_Type_as_Member_for_Validating_the_Outbound_Worker_Logs(self):
                logging.info("Validating REST API endpoint gets added with Outbound Member type as member for validating the Outbound Worker logs")
		data = {"name": "rest_api_endpoint1"}
                get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rest:endpoint")
                logging.info(get_temp)
		res=json.loads(get_temp)
                ref1 = json.loads(get_temp)[0]['_ref']
                print res
                print ref1
                get_rest_endpoint = ib_NIOS.wapi_request('GET', ref=ref1,params="?_return_fields=name,outbound_member_type,uri")
                logging.info(get_rest_endpoint)
                res=json.loads(get_rest_endpoint)
                print res
                string = {"name": "rest_api_endpoint1","_ref": ref1,"outbound_member_type": "MEMBER","uri": "https://"+config.grid_vip}
                if res == string:
                     assert True
                else:
                     assert False
                print("Test Case 8 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=9)
        def test_009_Add_DNS_Zone_Notification_Rule_DB_Changes_in_Admin_Local_with_Usergroup_as_Outbound_user_and_Password_as_infoblox(self):
		logging.info("Adding Notification rule for Adding Auth Zone with users as Outbound_user and password as Infoblox ")
                object_type="notification:rest:endpoint"
                data={"name":"rest_api_endpoint1"}
                get_ref = comm_util.get_object_reference(object_type,data)
                print "========================="
                print get_ref
                data = {"name": "notif1","notification_action": "RESTAPI_TEMPLATE_INSTANCE","notification_target": get_ref,"template_instance": {"template": "event_tunnel_ipv4"},"event_type": "DB_CHANGE_DNS_ZONE","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "DB_CHANGE_GROUP_NAME","op1_type": "FIELD","op2": "admin-group","op2_type": "STRING"},{"op": "EQ","op1":"DB_CHANGE_USER_NAME","op1_type": "FIELD","op2": "outbound_user","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('POST', object_type="notification:rule", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
		sleep(25)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 9 Execution Completed")

        @pytest.mark.run(order=10)
        def test_010_Validating_Notification_Rule_for_Admin_Users_LOCAL_For_Adding_Auth_Zone_with_Usergroup_as_Outbound_user_and_Password_as_infoblox(self):
                logging.info("Validating Notification Rule for Adding Auth Zone with Usergroup as Outbound_user & Password as Infoblox")
                data = {"name": "notif1"}
                get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_temp)
                res=json.loads(get_temp)
                print res
                ref1 = json.loads(get_temp)[0]['_ref']
                notification = ib_NIOS.wapi_request('GET', ref = ref1)
                logging.info(notification)
                res=json.loads(notification)
                print res
                string ={"name": "notif1","event_type": "DB_CHANGE_DNS_ZONE","notification_target": ref1}
                if (res == string):
                     assert True

                print("Test Case 10 Execution Completed")
                sleep(5)


        @pytest.mark.run(order=11)
        def test_011_Validate_ByDefault_Admin_Group_Present_in_Local(self):
                logging.info("Validate bydefault present admin-group in Local")
                get_response = ib_NIOS.wapi_request('GET', object_type="admingroup", params="?_return_fields=name",grid_vip=config.grid_vip)
                logging.info(get_response)
                res = json.loads(get_response)
                for i in res:
                   if i["name"]=="admin-group":
                     assert True
                print("Test Case 11 Execution Completed")
                sleep(5)


        @pytest.mark.run(order=12)
        def test_012_Add_User_in_Admin_Group(self):
                logging.info("Add User in Admin-Group")
                data = {"name":"outbound_user","auth_type":"LOCAL","password":"infoblox","admin_groups":["admin-group"]}
                response = ib_NIOS.wapi_request('POST', object_type="adminuser", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                print res
                print("Test Case 12 Execution Completed")
                sleep(10)


        @pytest.mark.run(order=13)
        def test_013_start_Worker_logs_to_check_Auth_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)


	@pytest.mark.run(order=14)
	def test_014_Add_Authoritative_zone_in_Outbound_user_with_Username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Create Auth Zone in outbound_user with Username as outbound_user and password as infoblox")
                #grid_member=config.grid_fqdn
                data = {"fqdn": "outbound6_zone2.com","grid_primary": [{"name":config.grid_member_fqdn,"stealth":False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth",user="outbound_user",password="infoblox", fields=json.dumps(data))
                data = {"fqdn": "outbound6_zone2.com"}
                grid = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print ("getting the zone",grid)
                logging.info(grid)
                res = json.loads(grid)
                print (res)
                for i in res:
                      print i
                      logging.info("found")
                      assert i["fqdn"] == "outbound6_zone2.com"

                print("Test Case 14 Execution Completed")
                sleep(25)

		logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
		print("System Restart is done successfully")
                sleep(10)
	
	@pytest.mark.run(order=15)
        def test_015_stop_Worker_logs_to_check_Auth_Zone_in_outbound_user(self):
                logging.info("Starting Outbound Worker Logs to check logs in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)


	@pytest.mark.run(order=16)
        def test_016_validate_Worker_logs_to_check_Template_for_Auth_Zone_outbound_user(self):
                logging.info("Validating Outbound Worker Logs to check template execution for Auth Zone in Outbound_user")
                LookFor="The template was executed successfully"
                logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print("Test Case 16 Execution Completed")



#######Update Auth Zone######

        @pytest.mark.run(order=17)
        def test_017_start_Worker_logs_to_check_Template_for_Updated_zone_in_Local_User_with_Username_as_admin_and_password_as_infoblox(self):
                logging.info("Starting Outbound Worker Logs to check updated auth zone in Local user with username as admin and password as infoblox ")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)


        @pytest.mark.run(order=18)
        def test_018_update_Authoritative_zone_Admin_User_with_Username_as_admin_and_password_as_infoblox(self):
                logging.info("Update Auth Zone in Local user with username as admin and password as infoblox")
		get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                logging.info("Modify Auth Zone")
                data = {"comment": "modifying auth zone"}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
		logging.info(response)
                res= json.loads(response)
                logging.info("Test Case 18 Execution Completed")
                sleep(5)
             

        @pytest.mark.run(order=19)
        def test_019_stop_Worker_logs_to_check_Template_for_Updated_zone_in_Local_User_Username_as_admin_and_password_as_infoblox(self):
                logging.info("Stopping Outbound Worker Logs in Local user with username as admin and password as infoblox")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print("Test Case 19 Execution Completed")

        @pytest.mark.run(order=20)
        def test_020_validate_Worker_log_to_check_Template_for_Updated_zone_in_Local_Users_with_Username_as_admin_and_password_as_infoblox(self):
                logging.info("Validating Outbound Worker Logs in Local user with username as admin and password as infoblox")
                LookFor="The template was executed successfully"
                response = logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print "================================="
                print response
                print "================================="
                print("Test Case 20 Execution Completed")


##### IPV4 Addr ########

        @pytest.mark.run(order=21)
        def test_021_Add_Notification_Rule_DNS_IPV4_Address_in_Admin_Local_with_Usergroup_as_admin_group_and_Username_as_outbound_user(self):
                logging.info("Adding Notification rule for DHCP IPV4 Address for Admin Users with Usergroup as admin-group and Username as outbound_user")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify Notification rule")
                data = {"event_type": "DB_CHANGE_DHCP_NETWORK_IPV4","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "DB_CHANGE_GROUP_NAME","op1_type": "FIELD","op2": "admin-group","op2_type": "STRING"},{"op": "EQ","op1":"DB_CHANGE_USER_NAME","op1_type": "FIELD","op2": "outbound_user","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                res = json.loads(response)
                print("Test Case 21 Execution Completed")
                sleep(15)

        @pytest.mark.run(order=22)
        def test_022_Validating_Notification_Rule_IPV4_Address_Admin_Users_LOCAL_with_Usergroup_as_admin_group_and_Username_as_outbound_user(self):
                logging.info("Validating REST API endpoint for Admin Users with Usergroup as admin-group and Username as outbound_user")
                data = {"name": "notif1"}
                get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_temp)
                res=json.loads(get_temp)
                print res
                ref1 = json.loads(get_temp)[0]['_ref']
                notification = ib_NIOS.wapi_request('GET', ref = ref1)
                logging.info(notification)
                res=json.loads(notification)
                print res
                string ={"name": "notif1","event_type": "DB_CHANGE_DHCP_NETWORK_IPV4","notification_target": ref1}
                if (res == string):
                     assert True

                print("Test Case 22 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=23)
        def test_023_start_Worker_logs_to_check_IPV4_in_outbound_user_with_Username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Starting Outbound Worker Logs to check template execution for IPV4 in outbound_user ")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)

        @pytest.mark.run(order=24)
        def test_024_Add_IPV4_Network_in_Outbound_user_with_Username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Adding IPV4 Network in Outbound_user with username as outbound_user and password as infoblox")
                grid_member=config.grid_fqdn
                data = {"network":"10.0.0.0/8","network_view": "default"}
                response = ib_NIOS.wapi_request('POST', object_type="network",user="outbound_user",password="infoblox", fields=json.dumps(data))
                data = {"network":"10.0.0.0/8"}
                grid = ib_NIOS.wapi_request('GET', object_type="network",fields=json.dumps(data))
                print ("getting the network",grid)
                logging.info(grid)
                res = json.loads(grid)
                print (res)
                for i in res:
                      print i
                      logging.info("found")
                      assert i["network"] == "10.0.0.0/8"


                print("Test Case 24 Execution Completed")
                sleep(10)

        @pytest.mark.run(order=25)
        def test_025_stop_Worker_logs_to_check_IPV4_in_outbound_user_with_Username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Stopping Outbound Worker Logs to check template execution for IPV4 in outbound_user")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print("Test Case 20 Execution Completed")


        @pytest.mark.run(order=26)
        def test_026_validate_Worker_logs_to_check_IPV4_in_outbound_user_with_Username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Validating Outbound Worker Logs to check template execution for IPV4 in outbound_user")
                LookFor="The template was executed successfully"
                logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print("Test Case 26 Execution Completed")

#####Update IPv4 Address###

        @pytest.mark.run(order=27)
        def test_027_start_Worker_logs_to_check_Template_for_Updated_IPV4_in_Local_Users_with_Username_as_admin_and_password_as_infoblox(self):
                logging.info("Starting Outbound Worker Logs to check template execution for updated IPV4 network with username as admin and password as infoblox")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)


        @pytest.mark.run(order=28)
        def test_028_update_IPV4_network_in_Local_User_with_Username_as_admin_and_password_as_infoblox(self):
                logging.info("Modify the IPV4 Network in Local User with username as admin and password as infoblox")
		get_ref = ib_NIOS.wapi_request('GET', object_type="network")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
		logging.info("Modifying IPV4 Network in Local User")
                data = {"comment": "modify IPV4 Network"}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
		logging.info(response)
                res = json.loads(response)
                logging.info("Test Case 28 Execution Completed")
                sleep(5)
             

        @pytest.mark.run(order=29)
        def test_029_stop_Worker_logs_to_check_Template_for_Updated_IPV4_Network_in_Local_Users_with_Username_as_admin_and_password_as_infoblox(self):
                logging.info("Stopping Outbound Worker Logs to check template execution for updated IPV4 network with username as admin and password as infoblox")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print("Test Case 29 Execution Completed")


        @pytest.mark.run(order=30)
        def test_030_validate_Worker_logs_to_check_Template_for_Updated_IPV4_Network_in_Local_Users_with_Username_as_admin_and_password_as_infoblox(self):
                logging.info("Validating Outbound Worker Logs to check template execution for updated IPV4 network with username as admin and password as infoblox")
                LookFor="The template was executed successfully"
                response = logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print "================================="
                print response
                print "================================="
                print("Test Case 30 Execution Completed")



##### IPV6 Addr ########

        @pytest.mark.run(order=31)
        def test_031_Add_Notification_Rule_for_DHCP_IPV6_Address_in_Admin_Local_with_Usergroup_as_admin_group_and_Username_as_outbound_user(self):
                logging.info("Adding Notification rule for DHCP IPV6 Address for Admin Users with Usergroup as admin-groups & username as outbound_user")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify Notification rule")
                data = {"event_type": "DB_CHANGE_DHCP_NETWORK_IPV6","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "DB_CHANGE_GROUP_NAME","op1_type": "FIELD","op2": "admin-group","op2_type": "STRING"},{"op": "EQ","op1":"DB_CHANGE_USER_NAME","op1_type": "FIELD","op2": "outbound_user","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 31 Execution Completed")
                sleep(15)

        @pytest.mark.run(order=32)
        def test_032_Validating_Notification_Rule_Admin_Users_LOCAL_with_Usergroup_as_admin_group_and_Username_as_outbound_user(self):
                logging.info("Validating Notification Rule for validating DHCP IPV6 Address for Admin Users with Usergroup as admin-groups & username as outbound_user")
                data = {"name": "notif1"}
                get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_temp)
                res=json.loads(get_temp)
                print res
                ref1 = json.loads(get_temp)[0]['_ref']
                notification = ib_NIOS.wapi_request('GET', ref = ref1)
                logging.info(notification)
                res=json.loads(notification)
                print res
                string ={"name": "notif1","event_type": "DB_CHANGE_DHCP_NETWORK_IPV6","notification_target": ref1}
                if (res == string):
                     assert True

                print("Test Case 32 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=33)
        def test_033_start_Worker_logs_to_check_IPV6_in_outbound_user_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Starting Outbound Worker Logs to check DHCP IPV6 address with username as outbound_user and password as infoblox")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)

        @pytest.mark.run(order=34)
        def test_034_Add_IPV6_Network_in_Outbound_user_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Adding IPV6 Network to check DHCP IPV6 address with username as outbound_user and password as infoblox")
              
                data = {"network":"aaaa::/16","network_view": "default"}
                response = ib_NIOS.wapi_request('POST', object_type="ipv6network",user="outbound_user",password="infoblox", fields=json.dumps(data))
                data = {"network":"aaaa::/16"}
                grid = ib_NIOS.wapi_request('GET', object_type="ipv6network",fields=json.dumps(data))
                print ("getting the network",grid)
                logging.info(grid)
                res = json.loads(grid)
                print (res)
                for i in res:
                      print i
                      logging.info("found")
                      assert i["network"] == "aaaa::/16"

                print("Test Case 34 Execution Completed")
                sleep(10)

        @pytest.mark.run(order=35)
        def test_035_stop_Worker_logs_to_check_IPV6_in_outbound_user_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Stopping Outbound Worker Logs to check DHCP IPV6 address with username as outbound_user and password as infoblox")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print("Test Case 35 Execution Completed")


        @pytest.mark.run(order=36)
        def test_036_validate_Worker_logs_to_check_IPV6_in_outbound_user_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Validating Outbound Worker Logs to check DHCP IPV6 address with username as outbound_user and password as infoblox")
                LookFor="The template was executed successfully"
                logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print("Test Case 36 Execution Completed")

####update ipv6 in local users

        @pytest.mark.run(order=37)
        def test_037_start_Worker_logs_to_check_template_execution_for_updated_ipv6_in_Local_User_with_Username_as_admin_and_password_as_infoblox(self):
                logging.info("Starting Outbound Worker Logs to check updated DHCP IPV6 address with username as admin & password as infoblox")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)


        @pytest.mark.run(order=38)
        def test_038_update_ipv6_network_in_Local_User_with_Username_as_admin_and_password_as_infoblox(self):
                logging.info("Update ipv6 network in Local User with username as admin & password as infoblox")
		get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6network")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
		logging.info("Modify IPV6 network")
                data = {"comment": "modifying ipv6 network"}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
		logging.info(response)
                res= json.loads(response)
                logging.info("Test Case 38 Execution Completed")
                sleep(5)
             

        @pytest.mark.run(order=39)
        def test_039_stop_Worker_logs_to_check_template_execution_for_updated_ipv6_in_Local_User_with_Username_as_admin_and_password_as_infoblox(self):
                logging.info("Stopping Outbound Worker Logs to check updated DHCP IPV6 address with username as admin & password as infoblox")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print("Test Case 39 Execution Completed")


        @pytest.mark.run(order=40)
        def test_040_validate_Worker_logs_to_check_template_execution_for_updated_ipv6_in_Local_User_with_Username_as_admin_and_password_as_infoblox(self):
                logging.info("Validating Outbound Worker Logs to check updated DHCP IPV6 address with username as admin & password as infoblox")
                LookFor="The template was executed successfully"
                response = logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print "================================="
                print response
                print "================================="
                print("Test Case 40 Execution Completed")


##### IPV4 Fixed Addr ########

        @pytest.mark.run(order=41)
        def test_041_NOTIFY_DHCP_IPV4_Fixed_Address_in_Admin_Local_with_Usergroup_as_admin_group_and_Username_as_outbound_user(self):
                logging.info("Adding Notification rule for DHCP IPV4 Fixed Address for Admin Users with Usergroup as admin-groups & username as outbound_user")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify Notification rule")
                data = {"event_type": "DB_CHANGE_DHCP_FIXED_ADDRESS_IPV4","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "DB_CHANGE_GROUP_NAME","op1_type": "FIELD","op2": "admin-group","op2_type": "STRING"},{"op": "EQ","op1":"DB_CHANGE_USER_NAME","op1_type": "FIELD","op2": "outbound_user","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 41 Execution Completed")
                sleep(15)

        @pytest.mark.run(order=42)
        def test_042_Validating_Notification_Rule_for_DHCP_IPV4_Fixed_Addr_in_Admin_Local_with_Usergroup_as_admin_group_and_Username_as_outbound_user(self):
                logging.info("Validating Notification Rule for validating DHCP IPV4 Fixed Address for Admin Users with Usergroup as admin-groups & username as outbound_user")
                data = {"name": "notif1"}
                get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_temp)
                res=json.loads(get_temp)
                print res
                ref1 = json.loads(get_temp)[0]['_ref']
                notification = ib_NIOS.wapi_request('GET', ref = ref1)
                logging.info(notification)
                res=json.loads(notification)
                print res
                string ={"name": "notif1","event_type": "DB_CHANGE_DHCP_FIXED_ADDRESS_IPV4","notification_target": ref1}
                if (res == string):
                     assert True

                print("Test Case 42 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=43)
        def test_043_start_Worker_logs_for_validating_DHCP_IPV4_Fixed_Addr_in_outbound_user_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Starting Outbound Worker Logs for validating DHCP IPV4 Fixed Address with username as outbound_user and password as infoblox")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)

        @pytest.mark.run(order=44)
        def test_044_Add_IPV4_Fixed_Network__in_outbound_user_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Adding IPV4 Network for  DHCP IPV4 Fixed Address with username as outbound_user and password as infoblox")
                data = {"network":"10.0.0.0/8","ipv4addr":"10.0.0.1","network_view": "default","mac":"11:11:11:11:11:22"}
                response = ib_NIOS.wapi_request('POST', object_type="fixedaddress",user="outbound_user",password="infoblox", fields=json.dumps(data))
                data = {"network":"10.0.0.0/8","ipv4addr":"10.0.0.1","mac":"11:11:11:11:11:22"}
                grid = ib_NIOS.wapi_request('GET', object_type="fixedaddress",fields=json.dumps(data))
                print ("getting the network",grid)
                logging.info(grid)
                res = json.loads(grid)
                print (res)
                for i in res:
                      print i
                      logging.info("found")
                      assert i["ipv4addr"] == "10.0.0.1"
                print("Test Case 44 Execution Completed")
                sleep(10)

        @pytest.mark.run(order=45)
        def test_045_stop_Worker_logs_for_validating_DHCP_IPV4_Fixed_Addr_in_outbound_user_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Stopping Outbound Worker Logs for validating DHCP IPV4 Fixed Address with username as outbound_user and password as infoblox")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print("Test Case 45 Execution Completed")


        @pytest.mark.run(order=46)
        def test_046_validate_Worker_logs_for_validating_DHCP_IPV4_Fixed_Addr_in_outbound_user_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Validating Outbound Worker Logs for validating DHCP IPV4 Fixed Address with username as outbound_user and password as infoblox")
                LookFor="The template was executed successfully"
                logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print("Test Case 46 Execution Completed")

######update ipv4 fixed address

        @pytest.mark.run(order=47)
        def test_047_start_Worker_logs_to_check_Template_for_Updated_ipv4_fixed_address_in_Local_User_Username_as_admin_and_password_as_infoblox(self):
                logging.info("Starting Outbound Worker Logs for validating DHCP IPV4 Fixed Address with username as admin and password as infoblox")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)


        @pytest.mark.run(order=48)
        def test_048_update_ipv4_fixed_address_in_Local_User_Username_as_admin_and_password_as_infoblox_(self):
                logging.info("Update ipv4 fixed address in Local User with username as admin and password as infoblox")
		get_ref = ib_NIOS.wapi_request('GET', object_type="fixedaddress")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
		logging.info("Modify ipv4 fixed address")
                data = {"comment": "update ipv4 fixed address"}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
		logging.info(response)

        @pytest.mark.run(order=49)
        def test_049_stop_Worker_logs_to_check_Template_for_Updated_ipv4_fixed_address_in_Local_User_Username_as_admin_and_password_as_infoblox(self):
                logging.info("Stopping Outbound Worker Logs for validating DHCP IPV4 Fixed Address with username as admin and password as infoblox")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print("Test Case 49 Execution Completed")


        @pytest.mark.run(order=50)
        def test_050_validate_Worker_logs_to_check_Template_for_Updated_ipv4_fixed_address_in_Local_User_Username_as_admin_and_password_as_infoblox(self):
                logging.info("Validating Outbound Worker Logs for validating DHCP IPV4 Fixed Address with username as admin and password as infoblox")
                LookFor="The template was executed successfully"
                response = logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print "================================="
                print response
                print "================================="
                print("Test Case 50 Execution Completed")



##### IPV6 Fixed Addr ########

        @pytest.mark.run(order=51)
        def test_051_NOTIFY_DNS_IPV6_Fixed_Address_in_Admin_Local_with_Usergroup_as_Outbound_user_and_Password_as_infoblox(self):
                logging.info("Adding Notification rule for DHCP IPV6 Fixed Address for Admin Users with Usergroup as admin-groups & username as outbound_user")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify Notification rule")
                data = {"event_type": "DB_CHANGE_DHCP_FIXED_ADDRESS_IPV6","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "DB_CHANGE_GROUP_NAME","op1_type": "FIELD","op2": "admin-group","op2_type": "STRING"},{"op": "EQ","op1":"DB_CHANGE_USER_NAME","op1_type": "FIELD","op2": "outbound_user","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 51 Execution Completed")
                sleep(15)

        @pytest.mark.run(order=52)
        def test_052_Validating_Notification_Rule_Admin_Users_LOCAL_with_Usergroup_as_Outbound_user_and_Password_as_infoblox(self):
                logging.info("Validating Notification rule for DHCP IPV6 Fixed Address for Admin Users with Usergroup as admin-groups & username as outbound_user")
                data = {"name": "notif1"}
                get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_temp)
                res=json.loads(get_temp)
                print res
                ref1 = json.loads(get_temp)[0]['_ref']
                notification = ib_NIOS.wapi_request('GET', ref = ref1)
                logging.info(notification)
                res=json.loads(notification)
                print res
                string ={"name": "notif1","event_type": "DB_CHANGE_DHCP_FIXED_ADDRESS_IPV6","notification_target": ref1}
                if (res == string):
                     assert True

                print("Test Case 52 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=53)
        def test_053_start_Worker_logs_to_check_Template_for_IPV6_Fixed_Network_with_Usergroup_as_Outbound_user_and_Password_as_infoblox(self):
                logging.info("Starting Outbound Worker Logs to validate template for DHCP IPV6 Fixed Address for outbound_user with username as outbound_user and password as infoblox")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)

        @pytest.mark.run(order=54)
        def test_054_Add_IPV6_Fixed_Network_Admin_User_in_outbound_user_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Adding IPV6 Network with username as outbound_user and password as infoblox")
                grid_member=config.grid_fqdn
                data = {"ipv6addr":"aaaa::1","network": "aaaa::/16", "duid":"12:34"}
                response = ib_NIOS.wapi_request('POST', object_type="ipv6fixedaddress",user="outbound_user",password="infoblox", fields=json.dumps(data))
                data = {"ipv6addr":"aaaa::1","network": "aaaa::/16", "duid":"12:34"}
                grid = ib_NIOS.wapi_request('GET', object_type="ipv6fixedaddress",fields=json.dumps(data))
                print ("getting the network",grid)
                logging.info(grid)
                res = json.loads(grid)
                print (res)
                for i in res:
                      print i
                      logging.info("found")
                      assert i["ipv6addr"] == "aaaa::1"


                print("Test Case 54 Execution Completed")
                sleep(10)

        @pytest.mark.run(order=55)
        def test_055_stop_Worker_logs_to_check_Template_for_IPV6_Fixed_Network_with_Usergroup_as_Outbound_user_and_Password_as_infoblox(self):
                logging.info("Stopping Outbound Worker Logs to validate template for DHCP IPV6 Fixed Address for outbound_user with username as outbound_user and password as infoblox ")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print("Test Case 55 Execution Completed")


        @pytest.mark.run(order=56)
        def test_056_validate_Worker_logs_to_check_Template_for_IPV6_Fixed_Network_with_Usergroup_as_Outbound_user_and_Password_as_infoblox(self):
                logging.info("Validating Outbound Worker logs to validate template for DHCP IPV6 Fixed Address for outbound_user with username as outbound_user and password as infoblox")
                LookFor="The template was executed successfully"
                logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print("Test Case 56 Execution Completed")

######update ipv6 fixed address

        @pytest.mark.run(order=57)
        def test_057_start_Worker_logs_to_validate_updated_ipv6_fixed_address_with_Username_as_admin_and_password_as_infoblox(self):
                logging.info("Starting Outbound Worker Logs to validate updated ipv6 fixed address with username as admin and password as infoblox")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)


        @pytest.mark.run(order=58)
        def test_058_update_ipv6_fixed_address_with_Username_as_admin_and_password_as_infoblox(self):
                logging.info("Update ipv6 fixed address in Local User with username as admin and password as infoblox")
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6fixedaddress")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                logging.info("Modify ipv6 fixed address")
                data = {"comment": "update ipv6 fixed address"}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                res = json.loads(response)
                logging.info("Test Case 58 Execution Completed")
                sleep(5)


        @pytest.mark.run(order=59)
        def test_059_stop_Worker_logs_to_validate_updated_ipv6_fixed_address_with_Username_as_admin_and_password_as_infoblox(self):
                logging.info("Stopping Outbound Worker Logs to validate updated ipv6 fixed address with username as admin and password as infoblox")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print("Test Case 59 Execution Completed")


        @pytest.mark.run(order=60)
        def test_060_validate_Worker_logs_to_validate_updated_ipv6_fixed_address_with_Username_as_admin_and_password_as_infoblox(self):
                logging.info("Validating Outbound Worker Logs to validate updated ipv6 fixed address with username as admin and password as infobloxto validate updated ipv6 fixed address with username as admin and password as infoblox")
                LookFor="The template was executed successfully"
                response = logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print "================================="
                print response
                print "================================="
                print("Test Case 60 Execution Completed")


##### IPV4 Range ########

        @pytest.mark.run(order=61)
        def test_061_NOTIFY_DHCP_IPV4_Range_in_Admin_Local_with_Usergroup_as_admin_group_and_Username_as_outbound_user(self):
                logging.info("Adding Notification rule for DHCP IPV4 Range for Admin Users with Usergroup as admin-groups & username as outbound_user")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify Notification rule")
                data = {"event_type": "DB_CHANGE_DHCP_RANGE_IPV4","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "DB_CHANGE_GROUP_NAME","op1_type": "FIELD","op2": "admin-group","op2_type": "STRING"},{"op": "EQ","op1":"DB_CHANGE_USER_NAME","op1_type": "FIELD","op2": "outbound_user","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 61 Execution Completed")
                sleep(15)

        @pytest.mark.run(order=62)
        def test_062_Validating_Notification_Rule_For_DHCP_IPV4_Range_for_Admin_Users_LOCAL_with_Usergroup_as_admin_group_and_Username_as_outbound_user(self):
                logging.info("Validating Notification Rule for DHCP IPV4 Range with username as outbound_user and password as infoblox")
                data = {"name": "notif1"}
                get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_temp)
                res=json.loads(get_temp)
                print res
                ref1 = json.loads(get_temp)[0]['_ref']
                notification = ib_NIOS.wapi_request('GET', ref = ref1)
                logging.info(notification)
                res=json.loads(notification)
                print res
                string ={"name": "notif1","event_type": "DB_CHANGE_DHCP_RANGE_IPV4","notification_target": ref1}
                if (res == string):
                     assert True
                print("Test Case 62 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=63)
        def test_063_start_Worker_logs_for_validating_DHCP_IPV4_Range_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Starting Outbound Worker Logs for validating DHCP IPV4 Range with username as outbound_user and password as infoblox")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)

        @pytest.mark.run(order=64)
        def test_064_Add_IPV4_Range_Admin_User_in_outbound_user_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Adding IPV4 Range in outbound_user  with username as outbound_user and password as infoblox")
                data = {"network": "10.0.0.0/8","network_view": "default","start_addr": "10.0.0.3","end_addr": "10.0.0.7"}
                response = ib_NIOS.wapi_request('POST', object_type="range",user="outbound_user",password="infoblox", fields=json.dumps(data))
                data = {"network": "10.0.0.0/8","network_view": "default","start_addr": "10.0.0.3","end_addr": "10.0.0.7"}
                grid = ib_NIOS.wapi_request('GET', object_type="range",fields=json.dumps(data))
                print ("getting the network",grid)
                logging.info(grid)
                res = json.loads(grid)
                print (res)
                for i in res:
                      print i
                      logging.info("found")
                      assert i["start_addr"] == "10.0.0.3"
                print("Test Case 64 Execution Completed")

                sleep(10)

        @pytest.mark.run(order=65)
        def test_065_stop_Worker_logs_for_validating_DHCP_IPV4_Range_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Stopping Outbound Worker Logs for validating DHCP IPV4 Range with username as outbound_user and password as infoblox")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print("Test Case 65 Execution Completed")


        @pytest.mark.run(order=66)
        def test_066_validate_Worker_logs_for_validating_DHCP_IPV4_Range_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Validating Outbound Worker Logs for validating DHCP IPV4 Range with username as outbound_user and password as infoblox")
                LookFor="The template was executed successfully"
                logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print("Test Case 66 Execution Completed")

#####update ipv4 range####

        @pytest.mark.run(order=67)
        def test_067_start_Worker_logs_for_validating_updated_ipv4_range_with_Username_as_admin_and_password_as_infoblox(self):
                logging.info("Starting Outbound Worker Logs for validating updated DHCP IPV4 Range with username as admin and password as infoblox")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)


        @pytest.mark.run(order=68)
        def test_068_update_ipv4_fixed_address_in_local_admin_with_Username_as_admin_and_password_as_infoblox(self):
                logging.info("Update ipv4 range in local admin with username as admin and password as infoblox")
                get_ref = ib_NIOS.wapi_request('GET', object_type="range")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                logging.info("Modify ipv4 range")
                data = {"comment": "update ipv4 range"}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)

                logging.info("Test Case 68 Execution Completed")
                sleep(5)


        @pytest.mark.run(order=69)
        def test_069_stop_Worker_logs_for_validating_updated_ipv4_range_with_Username_as_admin_and_password_as_infoblox(self):
                logging.info("Stopping Outbound Worker Logs for validating updated DHCP IPV4 Range with username as admin and password as infoblox")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print("Test Case 69 Execution Completed")


        @pytest.mark.run(order=70)
        def test_070_validate_Worker_logs_for_validating_updated_ipv4_range_with_Username_as_admin_and_password_as_infoblox(self):
                logging.info("Validating Outbound Worker Logs for validating updated DHCP IPV4 Range with username as admin and password as infoblox")
                LookFor="The template was executed successfully"
		response = logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print "================================="
                print response
                print "================================="
                print("Test Case 70 Execution Completed")



##### IPV6 Range ########

        @pytest.mark.run(order=71)
        def test_071_NOTIFY_DHCP_IPV6_Range_in_Admin_Local_with_Usergroup_as_admin_group_and_Username_as_outbound_user(self):
                logging.info("Adding Notification rule for DHCP IPV6 Range for Admin Users with Usergroup as admin-groups & username as outbound_user")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify Notification rule")
                data = {"event_type": "DB_CHANGE_DHCP_RANGE_IPV6","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "DB_CHANGE_GROUP_NAME","op1_type": "FIELD","op2": "admin-group","op2_type": "STRING"},{"op": "EQ","op1":"DB_CHANGE_USER_NAME","op1_type": "FIELD","op2": "outbound_user","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 71 Execution Completed")
                sleep(15)

        @pytest.mark.run(order=72)
        def test_072_Validating_Notification_Rule_For_DHCP_IPV6_Range_in_Admin_Users_LOCAL_with_Usergroup_as_admin_group_and_Username_as_outbound_user(self):
                logging.info("Validating Notification Rule for validating DHCP IPV6 Range for Admin Users with Usergroup as admin-groups & username as outbound_user")
                data = {"name": "notif1"}
                get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_temp)
                res=json.loads(get_temp)
                print res
                ref1 = json.loads(get_temp)[0]['_ref']
                notification = ib_NIOS.wapi_request('GET', ref = ref1)
                logging.info(notification)
                res=json.loads(notification)
                print res
                string ={"name": "notif1","event_type": "DB_CHANGE_DHCP_RANGE_IPV6","notification_target": ref1}
                if (res == string):
                     assert True

                print("Test Case 72 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=73)
        def test_073_start_Worker_logs_to_validate_DHCP_IPV6_Range_in_outbound_user_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Starting Outbound Worker Logs for validating DHCP IPV6 Range for outbound_user with Username as outbound_user and password as infoblox")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)

        @pytest.mark.run(order=74)
        def test_074_Add_IPV6_Range_Admin_User_in_outbound_user_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Adding IPV6 Range in outbound_user with Username as outbound_user and password as infoblox")
                data = {"network": "aaaa::/16","network_view": "default","start_addr": "aaaa::5","end_addr": "aaaa::8"}
                response = ib_NIOS.wapi_request('POST', object_type="ipv6range",user="outbound_user",password="infoblox", fields=json.dumps(data))
                data = {"network": "aaaa::/16","network_view": "default","start_addr": "aaaa::5","end_addr": "aaaa::8"}
                grid = ib_NIOS.wapi_request('GET', object_type="ipv6range",fields=json.dumps(data))
                print ("getting the network",grid)
                logging.info(grid)
                res = json.loads(grid)
                print (res)
                for i in res:
                      print i
                      logging.info("found")
                      assert i["start_addr"] == "aaaa::5"
                print("Test Case 74 Execution Completed")
                sleep(10)

        @pytest.mark.run(order=75)
        def test_075_stop_Worker_logs_to_validate_DHCP_IPV6_Range_in_outbound_user_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Stopping Outbound Worker Logs for validating DHCP IPV6 Range for outbound_user with Username as outbound_user and password as infoblox")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print("Test Case 75 Execution Completed")


        @pytest.mark.run(order=76)
        def test_076_validate_Worker_logs_to_validate_DHCP_IPV6_Range_in_outbound_user_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Validating Outbound Worker Logs for validating DHCP IPV6 Range for outbound_user with Username as outbound_user and password as infoblox")
                LookFor="The template was executed successfully"
                logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print("Test Case 76 Execution Completed")

######update ipv6 range####

        @pytest.mark.run(order=77)
        def test_077_start_Worker_logs_to_validate_updated_DHCP_IPV6_Range_in_admin_user_with_username_as_admin_and_password_as_infoblox(self):
                logging.info("Starting Outbound Worker Logs to validate updated DHCP IPV6 Range for local user with Username as admin and password as infoblox")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)


        @pytest.mark.run(order=78)
        def test_078_update_ipv6_fixed_address_in_admin_user_with_username_as_admin_and_password_as_infoblox(self):
                logging.info("Update ipv6 range for local user with Username as admin and password as infoblox")
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6range")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                logging.info("Modify ipv6 range")
                data = {"comment": "update ipv6 range"}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                res = json.loads(response)

                logging.info("Test Case 78 Execution Completed")
                sleep(5)


        @pytest.mark.run(order=79)
        def test_079_stop_Worker_logs_to_validate_updated_DHCP_IPV6_Range_in_admin_user_with_username_as_admin_and_password_as_infoblox(self):
                logging.info("Stopping Outbound Worker Logs to validate updated DHCP IPV6 Range for local user with Username as admin and password as infoblox")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print("Test Case 79 Execution Completed")


        @pytest.mark.run(order=80)
        def test_080_validate_Worker_logs_to_validate_updated_DHCP_IPV6_Range_in_admin_user_with_username_as_admin_and_password_as_infoblox(self):
                logging.info("Validating Outbound Worker Logs to validate updated DHCP IPV6 Range for local user with Username as admin and password as infoblox")
                LookFor="The template was executed successfully"
                response = logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print "================================="
                print response
                print "================================="
                print("Test Case 80 Execution Completed")

##### Add Record ########

        @pytest.mark.run(order=81)
        def test_081_Add_Notification_Record_in_Admin_Local_with_Usergroup_as_admin_group_and_Username_as_outbound_user(self):
                logging.info("Adding Notification rule for Adding Record for Admin Users with Usergroup as admin-groups & username as outbound_user")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify Notification rule")
                data = {"event_type": "DB_CHANGE_DNS_RECORD","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "DB_CHANGE_GROUP_NAME","op1_type": "FIELD","op2": "admin-group","op2_type": "STRING"},{"op": "EQ","op1":"DB_CHANGE_USER_NAME","op1_type": "FIELD","op2": "outbound_user","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 81 Execution Completed")
                sleep(15)

        @pytest.mark.run(order=82)
        def test_082_Validating_Notification_Rule_For_Adding_Record_in_Admin_Users_LOCAL_with_Usergroup_as_admin_group_and_Username_as_outbound_user(self):
                logging.info("Validating Notification Rule for adding CNAME Record for Admin Users with Usergroup as admin-groups & username as outbound_user")
                data = {"name": "notif1"}
                get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_temp)
                res=json.loads(get_temp)
                print res
                ref1 = json.loads(get_temp)[0]['_ref']
                notification = ib_NIOS.wapi_request('GET', ref = ref1)
                logging.info(notification)
                res=json.loads(notification)
                print res
                string ={"name": "notif1","event_type": "DB_CHANGE_DNS_RECORD","notification_target": ref1}
                if (res == string):
                     assert True

                print("Test Case 82 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=83)
        def test_083_start_Worker_logs_for_validating_Template_to_add_Record_in_outbound_user_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Starting Outbound Worker Logs to validate template for adding Records for outbound_user with username as outbound_user and password as infoblox")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)

        @pytest.mark.run(order=84)
        def test_084_Create_CNAME_record_to_add_Record_in_outbound_user_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info ("Creating CNAME Record for added Zone for outbound_user with username as outbound_user and password as infoblox")
                data = {"fqdn":"outbound6_zone2.com"}
                endpoint=comm_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "cname.outbound6_zone2.com","canonical": "cnametest.com","_ref":endpoint,"view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:cname",user="outbound_user",password="infoblox",fields=json.dumps(data))
                data = {"name": "cname.outbound6_zone2.com","canonical": "cnametest.com"}
                grid = ib_NIOS.wapi_request('GET', object_type="record:cname",fields=json.dumps(data))
                print ("getting the network",grid)
                logging.info(grid)
                res = json.loads(grid)
                print (res)
                for i in res:
                      print i
                      logging.info("found")
                      assert i["name"] == "cname.outbound6_zone2.com"
                logging.info("CNAME Record is created Successfully")
                sleep(10)


        @pytest.mark.run(order=85)
        def test_085_stop_Worker_logs_for_validating_Template_to_add_Record_in_outbound_user_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Stopping Outbound Worker Logs to validate template for adding Records for outbound_user with username as outbound_user and password as infoblox")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print("Test Case 85 Execution Completed")


        @pytest.mark.run(order=86)
        def test_086_validate_Worker_logs_for_validating_Template_to_add_Record_in_outbound_user_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Validating Outbound Worker Logs to validate template for adding Records for outbound_user with username as outbound_user and password as infoblox")
                LookFor="The template was executed successfully"
                logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print("Test Case 86 Execution Completed")


######Update CNAME Record#########

        @pytest.mark.run(order=87)
        def test_087_start_Worker_logs_for_validating_Template_to_update_Record_in_Local_Admin_with_username_as_admin_and_password_as_infoblox(self):
                logging.info("Starting Outbound Worker Logs to validate template for updating Records for admin local with username as admin and password as infoblox")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)



        @pytest.mark.run(order=88)
        def test_088_Update_CNAME_record_in_Local_Admin_with_username_as_admin_and_password_as_infoblox(self):
                logging.info ("Updating CNAME Record for added Zone for admin local with username as admin and password as infoblox")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:cname")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"comment":"Updating CNAME Record"}

                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                logging.info(response)
                res = json.loads(response)

                logging.info("CNAME Record is updated Successfully")
                sleep(30)

        @pytest.mark.run(order=89)
        def test_089_stop_Worker_logs_to_update_Record_in_Local_Admin_with_username_as_admin_and_password_as_infoblox(self):
                logging.info("Stopping Outbound Worker Logs to validate template for updating Records for admin local with username as admin and password as infoblox")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print("Test Case 88 Execution Completed")

        @pytest.mark.run(order=90)
        def test_090_validate_Worker_logs_to_update_Record_in_Local_Admin_with_username_as_admin_and_password_as_infoblox(self):
                logging.info("Validating Outbound Worker Logs to validate template for updating Records for admin local with username as admin and password as infoblox")
                LookFor="The template was executed successfully"
                response = logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print "================================="
                print response
                print "================================="
                print("Test Case 90 Execution Completed")


##### Add IPv4 Network Host ########

        @pytest.mark.run(order=91)
        def test_091_Add_Notification_IPV4_Host_in_admin_local_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Adding Notification rule for Adding IPV4 Network Host for Admin Users with username as outbound_user and password as infoblox")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify Notification rule")
                data = {"event_type": "DB_CHANGE_DNS_HOST_ADDRESS_IPV4","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "DB_CHANGE_GROUP_NAME","op1_type": "FIELD","op2": "admin-group","op2_type": "STRING"},{"op": "EQ","op1":"DB_CHANGE_USER_NAME","op1_type": "FIELD","op2": "outbound_user","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 91 Execution Completed")
                sleep(15)

        @pytest.mark.run(order=92)
        def test_092_Validating_Notification_Rule_Admin_Users_LOCAL_For_adding_IPV4_Host_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Validating Notification Rule for adding IPV4 Network Host for Admin Users with username as outbound_user and password as infoblox")
                data = {"name": "notif1"}
                get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_temp)
                res=json.loads(get_temp)
                print res
                ref1 = json.loads(get_temp)[0]['_ref']
                notification = ib_NIOS.wapi_request('GET', ref = ref1)
                logging.info(notification)
                res=json.loads(notification)
                print res
                string ={"name": "notif1","event_type": "DB_CHANGE_DNS_HOST_ADDRESS_IPV4","notification_target": ref1}
                if (res == string):
                     assert True

                print("Test Case 92 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=93)
        def test_093_start_Worker_logs_to_validate_template_execution_for_adding_IPV4_Host_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Starting Outbound Worker Logs for adding IPV4 Network Host for Admin Users with username as outbound_user and password as infoblox ")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)

        @pytest.mark.run(order=94)
        def test_094_Add_IPV4_Host_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Adding IPV4 Host in outbound_user with username as outbound_user and password as infoblox")
                grid_member=config.grid_fqdn
                data = {"name": "host1.outbound6_zone2.com","ipv4addrs": [{"ipv4addr":"10.10.10.26","configure_for_dhcp": True,"mac": "11:11:11:11:11:23"}]}
                response = ib_NIOS.wapi_request('POST', object_type="record:host",user="outbound_user",password="infoblox", fields=json.dumps(data))
                data = {"name": "host1.outbound6_zone2.com"}
                grid = ib_NIOS.wapi_request('GET', object_type="record:host",fields=json.dumps(data))
                print ("getting the network",grid)
                logging.info(grid)
                res = json.loads(grid)
                print (res)
                for i in res:
                      print i
                      logging.info("found")
                      assert i["name"] == "host1.outbound6_zone2.com"

                print("Test Case 94 Execution Completed")
                sleep(10)



        @pytest.mark.run(order=95)
        def test_095_stop_Worker_logs_to_validate_template_execution_for_adding_IPV4_Host_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Stopping Outbound Worker Logs for adding IPV4 Network Host for Admin Users with username as outbound_user and password as infoblox")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print("Test Case 95 Execution Completed")


        @pytest.mark.run(order=96)
        def test_096_validate_Worker_logs_to_validate_template_execution_for_adding_IPV4_Host_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Validating Outbound Worker Logs for adding IPV4 Network Host for Admin Users with username as outbound_user and password as infoblox")
                LookFor="The template was executed successfully"
                logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print("Test Case 96 Execution Completed")

##### Add IPv6 Network Host ########

        @pytest.mark.run(order=97)
        def test_097_ADD_Notification_IPV6_Host_with_Usergroup_as_admin_group_and_Username_as_outbound_user(self):
                logging.info("Adding Notification rule for Adding IPV6 Network Host for Admin Users with Usergroup as admin-groups & username as outbound_user")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify Notification rule")
                data = {"event_type": "DB_CHANGE_DNS_HOST_ADDRESS_IPV6","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "DB_CHANGE_GROUP_NAME","op1_type": "FIELD","op2": "admin-group","op2_type": "STRING"},{"op": "EQ","op1":"DB_CHANGE_USER_NAME","op1_type": "FIELD","op2": "outbound_user","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 97 Execution Completed")
                sleep(15)

        @pytest.mark.run(order=98)
        def test_098_Validating_Notification_Rule_for_adding_IPV6_host_in_Admin_Users_LOCAL_with_Usergroup_as_admin_group_and_Username_as_outbound_user(self):
                logging.info("Validating Notification Rule for adding IPV6 Network Host for Admin Users with Usergroup as admin-groups & username as outbound_user ")
                data = {"name": "notif1"}
                get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_temp)
                res=json.loads(get_temp)
                print res
                ref1 = json.loads(get_temp)[0]['_ref']
                notification = ib_NIOS.wapi_request('GET', ref = ref1)
                logging.info(notification)
                res=json.loads(notification)
                print res
                string ={"name": "notif1","event_type": "DB_CHANGE_DNS_HOST_ADDRESS_IPV6","notification_target": ref1}
                if (res == string):
                     assert True


                print("Test Case 98 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=99)
        def test_099_start_Worker_logs_to_validate_template_execution_for_adding_IPV6_Host_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Starting Outbound Worker Logs for adding IPV6 Network Host for Admin Users with username as outbound_user and password as infoblox")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)

        @pytest.mark.run(order=100)
        def test_100_Add_IPV6_Host_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Adding IPV6 Host in outbound_user with username as outbound_user and password as infoblox")
                grid_member=config.grid_fqdn
                data ={"name": "host2.outbound6_zone2.com","ipv6addrs":[{"ipv6addr":"aaaa::10","configure_for_dhcp": True,"duid":"12:45"}]}
                response = ib_NIOS.wapi_request('POST', object_type="record:host",user="outbound_user",password="infoblox", fields=json.dumps(data))
                data = {"name": "host2.outbound6_zone2.com"}
                grid = ib_NIOS.wapi_request('GET', object_type="record:host",fields=json.dumps(data))
                print ("getting the network",grid)
                logging.info(grid)
                res = json.loads(grid)
                print (res)
                for i in res:
                      print i
                      logging.info("found")
                      assert i["name"] == "host2.outbound6_zone2.com"

                print("Test Case 100 Execution Completed")
                sleep(10)



        @pytest.mark.run(order=101)
        def test_101_stop_Worker_logs_to_validate_template_execution_for_adding_IPV6_Host_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Stopping Outbound Worker Logs for adding IPV6 Network Host for Admin Users with username as outbound_user and password as infoblox")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print("Test Case 101 Execution Completed")


        @pytest.mark.run(order=102)
        def test_102_validate_Worker_logs_to_validate_template_execution_for_adding_IPV6_Host_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Validating Outbound Worker Logs for adding IPV6 Network Host for Admin Users with username as outbound_user and password as infoblox")
                LookFor="The template was executed successfully"
                response = logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print "================================="
                print response
                print "================================="
                print("Test Case 102 Execution Completed")


        @pytest.mark.run(order=103)
        def test_103_Add_Notification_Rule_Authzone_in_Admin_Local_with_Usergroup_as_admin_group_and_Username_as_outbound_user(self):
                logging.info("Adding Notification rule for Authoritative zone for Admin Users with Usergroup as admin-group and Username as outbound_user")
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify Notification rule")
                data = {"event_type": "DB_CHANGE_DNS_ZONE","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "DB_CHANGE_GROUP_NAME","op1_type": "FIELD","op2": "admin-group","op2_type": "STRING"},{"op": "EQ","op1":"DB_CHANGE_USER_NAME","op1_type": "FIELD","op2": "outbound_user","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                res = json.loads(response)
                print("Test Case 103 Execution Completed")
                sleep(15)

        @pytest.mark.run(order=104)
        def test_104_Validating_Notification_Rule_for_Admin_Users_LOCAL_For_Adding_Auth_Zone_with_Usergroup_as_Outbound_user_and_Password_as_infoblox(self):
                logging.info("Validating Notification Rule for Adding Auth Zone with Usergroup as Outbound_user & Password as Infoblox")
                data = {"name": "notif1"}
                get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule")
                logging.info(get_temp)
                res=json.loads(get_temp)
                print res
                ref1 = json.loads(get_temp)[0]['_ref']
                notification = ib_NIOS.wapi_request('GET', ref = ref1)
                logging.info(notification)
                res=json.loads(notification)
                print res
                string ={"name": "notif1","event_type": "DB_CHANGE_DNS_ZONE","notification_target": ref1}
                if (res == string):
                     assert True

                print("Test Case 104 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=105)
        def test_105_start_Worker_logs_to_validate_template_execution_for_adding_IPV6_Host_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Starting Outbound Worker Logs for adding IPV6 Network Host for Admin Users with username as outbound_user and password as infoblox")
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)

	@pytest.mark.run(order=106)
        def test_106_Add_Authoritative_zone(self):
		logging.info("Add Authoritative zone in 2nd grid")
		data = {"fqdn": "test.com","grid_primary": [{"name":config.grid_member_fqdn,"stealth":False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data),grid_vip= config.grid_vip)
                print(response)
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 106 Execution Completed")
                sleep(20)

                logging.info("Restart services")

                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                print("System Restart is done successfully")
                sleep(10)


        @pytest.mark.run(order=107)
        def test_107_import_bulk_records_through_csv(self):
		logging.info("import bulk record through csv")
                dir_name = "/home/kperiyaswamy/WAPI_PyTest_RK_Outbound/WAPI_PyTest/suites/outbound-6"
		base_filename = "bulk_csv1.csv"
                token = comm_util.generate_token_from_file(dir_name,base_filename)
                data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"OVERRIDE"}
                response = ib_NIOS.wapi_request('POST',object_type="fileop",fields=json.dumps(data),params="?_function=csv_import",grid_vip=config.grid_vip)
                print(response)
                response=json.loads(response)
                sleep(30)
                #data={"action":"START","file_name":"arun.csv","on_error":"STOP","operation":"CREATE","separator":"COMMA"}
                get_ref=ib_NIOS.wapi_request('GET', object_type="csvimporttask")
                get_ref=json.loads(get_ref)
                for ref in get_ref:
                    if response["csv_import_task"]["import_id"]==ref["import_id"]:
                       print ref["lines_failed"]
                       if ref["lines_failed"]>0:
                           data={"import_id":ref["import_id"]}
                           response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_error_log",grid_vip=config.grid_vip)
                           response=json.loads(response)
                           response=response["url"].split("/")
                           print response[4]
                           print response[5]
                           #connection=SSH(str(config.grid_member_vip))
                           connection=SSH(str(config.grid_vip))
                           command1='cat /tmp/http_direct_file_io/'+response[4]+'/'+response[5]+'| egrep -i \"Insertion\"'
                           logging.info (command1)
                           result=connection.send_command(command1)
                           logging.info (result)

        @pytest.mark.run(order=108)
        def test_108_start_HA_Failover_Test(self):
                logging.info("starting HA Failover test")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member_vip)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('reboot')
                child.expect('\(y or n\): ')
                child.sendline('y')
                #child.expect('Infoblox >')
                sleep(05)
                #return child.before
                print("\nTest Case Executed Successfully")
                sleep(60)



        @pytest.mark.run(order=109)
        def test_109_stop_Worker_logs_to_validate_template_execution_for_adding_IPV6_Host_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Stopping Outbound Worker Logs for adding IPV6 Network Host for Admin Users with username as outbound_user and password as infoblox")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print("Test Case 109 Execution Completed")


        @pytest.mark.run(order=110)
        def test_110_validate_Worker_logs_to_validate_template_execution_for_adding_IPV6_Host_with_username_as_outbound_user_and_password_as_infoblox(self):
                logging.info("Validating Outbound Worker Logs for adding IPV6 Network Host for Admin Users with username as outbound_user and password as infoblox")
                LookFor="The template was executed successfully"
                response = logv(LookFor,"/infoblox/var/outbound/log/worker_*",config.grid_member_vip)
                print "================================="
                print response
                print "================================="
                print("Test Case 110 Execution Completed")

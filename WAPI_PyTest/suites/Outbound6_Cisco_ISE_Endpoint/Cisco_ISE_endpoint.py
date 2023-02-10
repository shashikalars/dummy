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

global ref1
global notification_ref
global ipam_range
class Outbound_Cisco_ISE_Endpoint(unittest.TestCase):

#Starting DHCP service
 
        @pytest.mark.run(order=1)
        def test_001_start_IPv4_DHCP_service(self):
            	logging.info("start the ipv4 DHCP service")
            	get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
            	logging.info(get_ref)
            	res = json.loads(get_ref)
            	ref1 = json.loads(get_ref)[0]['_ref']
            	ref1=ref1+"?_return_fields=enable_dhcp"
            	print ("==========================",ref1)
            	member_dhcp_data=ib_NIOS.wapi_request('GET',object_type=ref1)
            	print ("---------------------------",member_dhcp_data)
            	data = {"enable_dhcp":True}
            	response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
            	print(response)
                print("Test Case 1 Execution Completed")

        @pytest.mark.run(order=2)
        def test_002_Validate_DHCP_service_Enabled(self):
                logging.info("Validate DHCP Service is enabled")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties",params="?_return_fields=enable_dhcp")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                for i in res:
                        print i
                        assert i["enable_dhcp"] == True
                print("Test Case 2 Execution Completed")

#Adding Forwarder

	@pytest.mark.run(order=3)
	def test_003_Configure_Global_Forwarders_Logging_Categories_Allow_Recursion_At_Grid_level(self):
		logging.info("Configure Global Forwarders Logging Categories Allow Recursion At Grid level")
		get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
		logging.info(get_ref)
		res = json.loads(get_ref)
		ref1 = json.loads(get_ref)[0]['_ref']
		print ref1
		data = {"allow_recursive_query": True,"forwarders": [config.dns_forwarder],"logging_categories": {"log_queries": True,"log_responses": True,"log_rpz": True}}
		response = ib_NIOS.wapi_request('PUT',ref= ref1,fields=json.dumps(data))
		print response
                print("Test Case 3 Execution Completed")

        @pytest.mark.run(order=4)
        def test_004_Validate_Configured_Global_Forwarders_Logging_Categories_Allow_Recursion_At_Grid_level(self):
                logging.info("Validate Configured Global Forwarders Logging Categories Allow Recursion at Grid level")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="grid:dns",params="?_return_fields=forwarders")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
		res = eval(json.dumps(res))
                print(res[0])
		print(type(res))
		if res[0]['forwarders'] == [config.dns_forwarder]:
                        assert True
                else:
			assert False
                logging.info("============================")
		print("Test Case 4 Execution Completed")

#Upload Templates

	@pytest.mark.run(order=5)
        def test_005_Upload_Cisco_ISE_Endpoint_Session_Template(self):
                logging.info("Upload Cisco ISE Endpoint Version6 Session Template")
                dir_name="./Cisco_ISE_templates/"
                base_filename="PxgrdiSessionTemplate.json"
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
        def test_006_Validate_CISCO_ISE_Endpoint_Session_Template_Uploaded(self):
                logging.info("Validating Cisco ISE Endpoint Session template get uploaded")
                data = {"name": "PxgrdiSessionTemplate"}
                get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rest:template",fields=json.dumps(data))
                logging.info(get_temp)
                print get_temp
                res = json.loads(get_temp)
                print res
                for i in res:
                        print i
                        assert i["name"] == "PxgrdiSessionTemplate"
                print("Test Case 6 Execution Completed")
	
        @pytest.mark.run(order=7)
        def test_007_Upload_Cisco_ISE_Endpoint_IPAM_Event_Template(self):
                logging.info("Upload Version6 Cisco ISE endpoint IPAM Event Template")
                dir_name="./Cisco_ISE_templates/"
                base_filename="IPAM_PxgridEvent.json"
                token = common_util.generate_token_from_file(dir_name,base_filename)
                data = {"token": token,"overwrite":True}
                response = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=restapi_template_import")
                logging.info(response)
                print response
                res = json.loads(response)
                string = {"overall_status": "SUCCESS","error_message": ""}
                if res == string:
                        assert True
                else:
                        assert False
                print("Test Case 7 Execution Completed")

	@pytest.mark.run(order=8)
        def test_008_Validate_IPAM_Event_Template_Uploaded(self):
                logging.info("Validating Cisco ISE Endpoint IPAM Event template get uploaded")
                data = {"name": "IPAM_PxgridEvent"}
                get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rest:template",fields=json.dumps(data))
                logging.info(get_temp)
                print get_temp
                res = json.loads(get_temp)
                print res
                for i in res:
                        print i
                        assert i["name"] == "IPAM_PxgridEvent"
                print("Test Case 8 Execution Completed")

        @pytest.mark.run(order=9)
        def test_009_Try_to_Upload_Cisco_ISE_Endpoint_Session_Template_with_version5(self):
                logging.info("Try to Upload Cisco ISE Endpoint Session Template with version5")
                dir_name="./Cisco_ISE_templates/"
                base_filename="PxgrdiSessionTemplate_version5.json"
                token = common_util.generate_token_from_file(dir_name,base_filename)
                data = {"token": token,"overwrite": True}
                response = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=restapi_template_import")
                logging.info(response)
                print response
                logging.info(response)
                res = json.loads(response)
                string = { "error_message": "The template is not validated correctly with the schema. u'PXGRID_ENDPOINT' is not one of [u'REST_ENDPOINT', u'DXL_ENDPOINT', u'SYSLOG_ENDPOINT'].","overall_status": "FAILED"}
                if res == string:
                        assert True
                else:
                        assert False
                print("Test Case 9 Execution Completed")


        @pytest.mark.run(order=10)
        def test_010_Try_to_Upload_Cisco_ISE_Endpoint_IPAM_Event_Template_with_version5(self):
                logging.info("Try to Upload Cisco ISE endpoint IPAM Event Template with version5")
                dir_name="./Cisco_ISE_templates/"
                base_filename="IPAM_PxgridEvent_version5.json"
                token = common_util.generate_token_from_file(dir_name,base_filename)
                data = {"token": token,"overwrite":True}
                response = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=restapi_template_import")
                print response
                logging.info(response)
                res = json.loads(response)
                string = {"error_message": "The template is not validated correctly with the schema. u'IPAM' is not one of [u'RPZ', u'LEASE', u'TUNNEL', u'ADP', u'DXL', u'NETWORK_IPV4', u'NETWORK_IPV6', u'RANGE_IPV4', u'RANGE_IPV6', u'FIXED_ADDRESS_IPV4', u'FIXED_ADDRESS_IPV6', u'HOST_ADDRESS_IPV4', u'HOST_ADDRESS_IPV6', u'DISCOVERY_DATA', u'SCHEDULE', u'DNS_RECORD', u'DNS_ZONE', u'SESSION'].","overall_status": "FAILED"}
                if res == string:
                        assert True
                else:
                        assert False
                print("Test Case 10 Execution Completed")


        @pytest.mark.run(order=11)
        def test_011_Try_to_Upload_Cisco_ISE_Endpoint_DHCP_lease_Event_Template_version5_with_PX_SEND_DHCP_LEASES_Operation(self):
                logging.info("Try to Upload Cisco ISE endpoint DHCP Lease Event Template with version5 with PX_SEND_DHCP_LEASES Operation")
                dir_name="./Cisco_ISE_templates/"
                base_filename="DHCPLease_Event_version5.json"
                token = common_util.generate_token_from_file(dir_name,base_filename)
                data = {"token": token,"overwrite":True}
                response = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=restapi_template_import")
                print response
                logging.info(response)
                res = json.loads(response)
                string = {"error_message": "The template is not validated correctly with the schema. {u'operation': u'PX_SEND_DHCP_LEASES', u'name': u'DHCP_event'} is not valid under any of the given schemas.", "overall_status": "FAILED"}
                if res == string:
                        assert True
                else:
                        assert False
                print("Test Case 11 Execution Completed")

        @pytest.mark.run(order=12)
        def test_012_Try_to_Upload_Cisco_ISE_Endpoint_RPZ_Event_Template_with_version5_with_PX_SEND_QUARANTINE_Operation(self):
                logging.info("Try to Upload Cisco ISE endpoint RPZ OR ADP Event Template with version5 with PX_SEND_QUARANTINE Operation")
                dir_name="./Cisco_ISE_templates/"
                base_filename="PXGRID_action_RPZ_ADP_version5.json"
                token = common_util.generate_token_from_file(dir_name,base_filename)
                data = {"token": token,"overwrite":True}
                response = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=restapi_template_import")
                print response
                logging.info(response)
                res = json.loads(response)
                string = {"error_message": "The template is not validated correctly with the schema. {u'operation': u'PX_SEND_QUARANTINE', u'name': u'IPAM event'} is not valid under any of the given schemas.","overall_status": "FAILED"}
                if res == string:
                        assert True
                else:
                        assert False
                print("Test Case 12 Execution Completed")

#Adding Cisco ISE Outbound endpoint with Negative Scenarios
	
        @pytest.mark.run(order=13)
        def test_013_Add_Cisco_ISE_endpoint_with_Invalid_certificate_token(self):
                logging.info("Add Cisco ISE endpoint with Invalid certificate token")
                data = {"address": config.cisco_ise_server_ip,"comment": "Add cisco ISE endpoint","log_level": "DEBUG","name": "cisco_ise_endpoint1","network_view": "default","outbound_member_type": "GM","outbound_members": [],"publish_settings": {"enabled_attributes":["IPADDRESS"]}, "subscribe_settings": {"enabled_attributes": ["DOMAINNAME"],"mapped_ea_attributes": []},"template_instance": {"parameters": [],"template": "PxgrdiSessionTemplate"},"timeout": 30,"vendor_identifier": "pxgrid","wapi_user_name": "admin","wapi_user_password":"infoblox","client_certificate_token": ""}
                response = ib_NIOS.wapi_request('POST', object_type="pxgrid:endpoint", fields=json.dumps(data))
                print response
                logging.info(response)
                assert re.search(r'"text": "client_certificate_token is not provided."',response[-1])
                print("Test Case 13 Execution Completed")                

        @pytest.mark.run(order=14)
        def test_014_Upload_Cisco_ISE_Server_CA_Certificate(self):
                logging.info("Upload Cisco ISE Server CA Certificate")
                dir_name="./Cisco_ISE_templates/"
                base_filename="brokercerts.crt"
                token = common_util.generate_token_from_file(dir_name,base_filename)
                print token
                data = {"token": token, "certificate_usage":"EAP_CA"}
                response = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=uploadcertificate")
                print("Test Case 14 Execution Completed")
                sleep(60)

        @pytest.mark.run(order=15)
        def test_015_Try_to_Add_Cisco_ISE_endpoint_without_client_certificate_token_Attribute(self):
                logging.info("Try to Add Cisco ISE endpoint without client_certificate_token Attribute")
                data = {"address": config.cisco_ise_server_ip,"comment": "Add cisco ISE endpoint","log_level": "DEBUG","name": "cisco_ise_endpoint1","network_view": "default","outbound_member_type": "GM","outbound_members": [],"publish_settings": {"enabled_attributes":["IPADDRESS"]}, "subscribe_settings": {"enabled_attributes": ["DOMAINNAME"],"mapped_ea_attributes": []},"template_instance": {"parameters": [],"template": "PxgrdiSessionTemplate"},"timeout": 30,"vendor_identifier": "pxgrid","wapi_user_name": "admin","wapi_user_password":"infoblox"}
                response = ib_NIOS.wapi_request('POST', object_type="pxgrid:endpoint", fields=json.dumps(data))
                print response
                logging.info(response)
		sleep(20)
                assert re.search(r'"text": "field for create missing: client_certificate_token"',response[-1])
                print("Test Case 15 Execution Completed")

        @pytest.mark.run(order=16)
        def test_016_Try_to_Add_Cisco_ISE_endpoint_with_empty_client_certificate_token_value(self):
                logging.info("Try to Add Cisco ISE endpoint with Empty client_certificate_token Value")
                data = {"address": config.cisco_ise_server_ip,"comment": "Add cisco ISE endpoint","log_level": "DEBUG","name": "cisco_ise_endpoint2","network_view": "default","outbound_member_type": "GM","outbound_members": [],"publish_settings": {"enabled_attributes":["IPADDRESS"]}, "subscribe_settings": {"enabled_attributes": ["DOMAINNAME"],"mapped_ea_attributes": []},"template_instance": {"parameters": [],"template": "PxgrdiSessionTemplate"},"timeout": 30,"vendor_identifier": "pxgrid","wapi_user_name": "admin","wapi_user_password":"infoblox","client_certificate_token": " "}
                response = ib_NIOS.wapi_request('POST', object_type="pxgrid:endpoint", fields=json.dumps(data))
                print response
                logging.info(response)
		sleep(20)
                assert re.search(r'"text": "Invalid token value"',response[-1])
                print("Test Case 16 Execution Completed")
       
	@pytest.mark.run(order=17)
        def test_017_Try_to_Add_Cisco_ISE_endpoint_without_subscribe_settings_Attribute(self):
                logging.info("Try_to_Add_Cisco_ISE_endpoint_without subscribe settings Attribute")
                dir_name="./Cisco_ISE_templates/"
                base_filename="client.cer"
                token = common_util.generate_token_from_file(dir_name,base_filename)
                print ("Token details :",token)
                data = {"address":config.cisco_ise_server_ip ,"comment": "Add cisco ISE endpoint","log_level": "DEBUG","name": "cisco_ise_endpoint1","outbound_member_type": "GM","outbound_members": [],"publish_settings": {"enabled_attributes":["IPADDRESS"]},"wapi_user_name": "admin","wapi_user_password":"infoblox","client_certificate_token": str(token)} 
		response = ib_NIOS.wapi_request('POST', object_type="pxgrid:endpoint", fields=json.dumps(data))
                print response
                logging.info(response)
		sleep(10)
                assert re.search(r'"text": "field for create missing: subscribe_settings"',response[-1])
                print("Test Case 17 Execution Completed")
				
	@pytest.mark.run(order=18)
        def test_018_Try_to_Add_Cisco_ISE_endpoint_with_wrong_subscribe_settings_Attribute(self):
                logging.info("Try_to_Add_Cisco_ISE_endpoint_with wrong subscribe settings Attribute")
                dir_name="./Cisco_ISE_templates/"
                base_filename="client.cer"
                token = common_util.generate_token_from_file(dir_name,base_filename)
                print ("Token details :",token)
                data = {"address":config.cisco_ise_server_ip ,"comment": "Add cisco ISE endpoint","log_level": "DEBUG","name": "cisco_ise_endpoint1","outbound_member_type": "GM","outbound_members": [],"publish_settings": {"enabled_attributes":["IPADDRESS"]}, "subscribe_settings": {"enabled_attributes": ["DOMAINNAM"],"mapped_ea_attributes": []},"wapi_user_name": "admin","wapi_user_password":"infoblox","client_certificate_token": str(token)}
		response = ib_NIOS.wapi_request('POST', object_type="pxgrid:endpoint", fields=json.dumps(data))
                print response
                logging.info(response)
		sleep(10)
                assert re.search(r'"text": "Invalid value for enabled_attributes: \\"DOMAINNAM\\": Valid values are DOMAINNAME, ENDPOINT_PROFILE, SECURITY_GROUP, SESSION_STATE, SSID, USERNAME, VLAN"',response[-1])
                print("Test Case 18 Execution Completed")
        
        @pytest.mark.run(order=19)
        def test_019_Update_Grid_Master_Host_Name_To_Connect_Endpoint(self):
                logging.info("Update Grid Master Host Name To_Connect_Endpoint")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                print(get_ref)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
		data = {"host_name": config.host_name}
		response = ib_NIOS.wapi_request('PUT', object_type=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
		sleep(10)
                print("Test Case 19 Execution Completed")

        @pytest.mark.run(order=20)
        def test_020_Validating_Grid_Master_Host_Name_To_Connect_Endpoint(self):
                logging.info("Validating Grid Master Host Name To_Connect_Endpoint")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                print(get_ref)
		host='"host_name": "'+config.host_name+'"'
		if(host in get_ref):
                        assert True
                else:
                        assert False	
		print("Test Case 20 Execution Completed")

	@pytest.mark.run(order=21)
        def test_021_Try_to_Add_Cisco_ISE_endpoint_with_wrong_Manage_Certificate(self):
                logging.info("Create_Cisco_ISE_Endpoint with wrong Manage Certificate")
                dir_name="./Cisco_ISE_templates/"
                base_filename="client.cer"
                token = common_util.generate_token_from_file(dir_name,base_filename)
                print ("Token details :",token)
                data= {"address": config.cisco_ise_server_ip,"comment": "Add cisco ISE endpoint","log_level": "DEBUG","name": "cisco_ise_endpoint2","network_view": "default","outbound_member_type": "GM","outbound_members": [],"publish_settings": {"enabled_attributes":["IPADDRESS"]}, "subscribe_settings": {"enabled_attributes": ["DOMAINNAME"],"mapped_ea_attributes": []},"template_instance": {"parameters": [],"template": "PxgrdiSessionTemplate"},"timeout": 30,"vendor_identifier": "pxgrid","wapi_user_name": "admin","wapi_user_password":"infoblox","client_certificate_token":str(token)}
                response = ib_NIOS.wapi_request('POST', object_type="pxgrid:endpoint", fields=json.dumps(data))
                print response
                logging.info(response)
		sleep(20)
                assert re.search(r'cisco_ise_endpoint2',response)
                print("Test Case 21 Execution Completed")

        @pytest.mark.run(order=22)
        def test_022_Configure_Global_Resolver_Logging_Categories_Allow_Recursion_At_Grid_level(self):
                logging.info("Configure Global Resolver Logging Categories Allow Recursion At Grid level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
		print(get_ref)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"dns_resolver_setting":{"resolvers":[config.dns_resolver],"search_domains":[]}}
                response = ib_NIOS.wapi_request('PUT',ref= ref1,fields=json.dumps(data))
                print response
                logging.info(response)
		sleep(10)
                print("Test Case 22 Execution Completed")

	@pytest.mark.run(order=23)
        def test_023_Validate_Configured_DNS_Resolver_Logging_Grid_level(self):
                logging.info("Validate Configured DNS Resolver Logging Grid level")
                string = {"dns_resolver_setting":{"resolvers":[config.dns_resolver]}}
                print string
                get_resolver = ib_NIOS.wapi_request('GET', object_type="grid",params="?_return_fields=dns_resolver_setting")
                logging.info(get_resolver)
                res = json.loads(get_resolver)
                res = eval(json.dumps(res))
                print res[0]
                print(type(res))
                if ((res[0]["dns_resolver_setting"]["resolvers"] == string["dns_resolver_setting"]["resolvers"]) and ("['"+config.dns_resolver+"']" in str(res[0]))):
                        assert True
                else:
                        assert False
                sleep(10)
                print("Test Case 23 Execution Completed")
                logging.info("============================")
			
	@pytest.mark.run(order=24)
        def test_024_CiscoISE_Endpoint_Test_Connection_Validation_of_wrong_Manage_Certificate(self):
                logging.info("CiscoISE Endpoint Test Connection Validation with wrong_Manage_Certificate")
                get_ref = ib_NIOS.wapi_request('GET', object_type="pxgrid:endpoint")
                print(get_ref)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                response = ib_NIOS.wapi_request('POST', object_type=ref1+"?_function=test_connection")
                sleep(30)
                print response
                logging.info(response)
		sleep(20)
                assert re.search(r'"text": "Test connection failed: Certificate verify failed."',response[-1])
                print("Test Case 24 Execution Completed")
			
	@pytest.mark.run(order=25)
        def test_025_Delete_Endpoint_after_Test_Connection_Validation_of_wrong_Manage_Certificate(self):
                logging.info("Delete_Endpoint after_Test_Connection_Validation_of_wrong_Manage_Certificate")
                get_ref = ib_NIOS.wapi_request('GET', object_type="pxgrid:endpoint")
                print(get_ref)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
		response = ib_NIOS.wapi_request('DELETE', object_type=ref1)
		sleep(10)
		print("Test Case 25 Execution Completed")
		
        @pytest.mark.run(order=26)
        def test_026_Configure_Empty_Global_Resolver_Logging_Categories_Allow_Recursion_At_Grid_level(self):
                logging.info("Configure Empty Global Resolver Logging Categories Allow Recursion At Grid level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
		print(get_ref)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"dns_resolver_setting":{"resolvers":[ ],"search_domains":[]}}
                response = ib_NIOS.wapi_request('PUT',ref= ref1,fields=json.dumps(data))
                print response
                logging.info(response)
		sleep(10)
                print("Test Case 26 Execution Completed")
  
	@pytest.mark.run(order=27)
        def test_027_Upload_Cisco_ISE_Server_CA_Certificate(self):
                logging.info("Upload Cisco ISE Server CA Certificate")
                dir_name="./Cisco_ISE_templates/"
                base_filename="rootCA1.cer"
                token = common_util.generate_token_from_file(dir_name,base_filename)
                print token
                data = {"token": token, "certificate_usage":"EAP_CA"}
                response = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=uploadcertificate")
                print("Test Case 27 Execution Completed")
                sleep(30)
                
        @pytest.mark.run(order=28)
        def test_028_Try_to_Add_Cisco_ISE_endpoint_with_out_DNS_Resolver(self):
                logging.info("Create_Cisco_ISE_Endpoint with out DNS Resolver")
                dir_name="./Cisco_ISE_templates/"
                base_filename="ramesh1.cer"
                token = common_util.generate_token_from_file(dir_name,base_filename)
                print ("Token details :",token)
                data= {"address": config.cisco_ise_server_ip,"comment": "Add cisco ISE endpoint","log_level": "DEBUG","name": "cisco_ise_endpoint2","network_view": "default","outbound_member_type": "GM","outbound_members": [],"publish_settings": {"enabled_attributes":["IPADDRESS"]}, "subscribe_settings": {"enabled_attributes": ["DOMAINNAME"],"mapped_ea_attributes": []},"template_instance": {"parameters": [],"template": "PxgrdiSessionTemplate"},"timeout": 30,"vendor_identifier": "pxgrid","wapi_user_name": "admin","wapi_user_password":"infoblox","client_certificate_token":str(token)}
                response = ib_NIOS.wapi_request('POST', object_type="pxgrid:endpoint", fields=json.dumps(data))
                sleep(30)
                print response
                logging.info(response)
                assert re.search(r'cisco_ise_endpoint2',response)
                print("Test Case 28 Execution Completed")

        @pytest.mark.run(order=29)
        def test_029_CiscoISE_Endpoint_Test_Connection_Validation_with_out_DNS_Resolver(self):
                logging.info("CiscoISE Endpoint Test Connection Validation with_out_DNS_Resolver")
                get_ref = ib_NIOS.wapi_request('GET', object_type="pxgrid:endpoint")
                print(get_ref)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                response = ib_NIOS.wapi_request('POST', object_type=ref1+"?_function=test_connection")
                sleep(30)
                print response
                logging.info(response)
		response=str(response)
		response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
		print(response)
		sleep(20)
		if(('"text":"Testconnectionfailed:Unabletorequestdata,failedtoestablishconnection."' in response) or ('"text":"Testconnectionfailed:Couldnotsendmessagetomember."' in response)):
			assert True
                else:
                        assert False	
                print("Test Case 29 Execution Completed")

        @pytest.mark.run(order=30)
        def test_030_Delete_Endpoint_after_Test_Connection_Validation_with_out_DNS_Resolver(self):
                logging.info("Delete_Endpoint after_Test_Connection_Validation_with_out_DNS_Resolver")
                get_ref = ib_NIOS.wapi_request('GET', object_type="pxgrid:endpoint")
                print(get_ref)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
		response = ib_NIOS.wapi_request('DELETE', object_type=ref1)
		sleep(15)
		print("Test Case 30 Execution Completed")

        @pytest.mark.run(order=31)
        def test_031_Configure_Global_Resolver_Logging_Categories_Allow_Recursion_At_Grid_level(self):
                logging.info("Configure Global Resolver At Grid level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
		print(get_ref)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"dns_resolver_setting":{"resolvers":[config.dns_resolver],"search_domains":[]}}
                response = ib_NIOS.wapi_request('PUT',ref= ref1,fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
		sleep(15)
                print("Test Case 31 Execution Completed")

	@pytest.mark.run(order=32)
        def test_032_Validate_Configured_DNS_Resolver_At_Grid_level(self):
                logging.info("Validate Configured DNS Resolver At Grid level")
                string = {"dns_resolver_setting":{"resolvers":[config.dns_resolver]}}
                print string
                get_resolver = ib_NIOS.wapi_request('GET', object_type="grid",params="?_return_fields=dns_resolver_setting")
                logging.info(get_resolver)
                res = json.loads(get_resolver)
                res = eval(json.dumps(res))
                print res
                if ((res[0]["dns_resolver_setting"]["resolvers"] == string["dns_resolver_setting"]["resolvers"]) and ("['"+config.dns_resolver+"']" in str(res[0]))):
                	assert True
                else:
                        assert False
		sleep(10)
                print("Test Case 32 Execution Completed")
        

        @pytest.mark.run(order=33)
        def test_033_Try_to_Add_Cisco_ISE_endpoint_with_wrong_Client_Certificate(self):
                logging.info("Create_Cisco_ISE_Endpoint with wrong Client Certificate")
                dir_name="./Cisco_ISE_templates/"
                base_filename="nios_client.cer"
                token = common_util.generate_token_from_file(dir_name,base_filename)
                print ("Token details :",token)
                data= {"address": config.cisco_ise_server_ip,"comment": "Add cisco ISE endpoint","log_level": "DEBUG","name": "cisco_ise_endpoint2","network_view": "default","outbound_member_type": "GM","outbound_members": [],"publish_settings": {"enabled_attributes":["IPADDRESS"]}, "subscribe_settings": {"enabled_attributes": ["DOMAINNAME"],"mapped_ea_attributes": []},"template_instance": {"parameters": [],"template": "PxgrdiSessionTemplate"},"timeout": 30,"vendor_identifier": "pxgrid","wapi_user_name": "admin","wapi_user_password":"infoblox","client_certificate_token":str(token)}
                response = ib_NIOS.wapi_request('POST', object_type="pxgrid:endpoint", fields=json.dumps(data))
                print response
                logging.info(response)
		sleep(20)
                assert re.search(r'cisco_ise_endpoint2',response)
                print("Test Case 33 Execution Completed")
		
        @pytest.mark.run(order=34)
        def test_034_CiscoISE_Endpoint_Test_Connection_Validation_with_wrong_Client_Certificate(self):
                logging.info("CiscoISE Endpoint Test Connection Validation with_wrong_Client_Certificate")
                get_ref = ib_NIOS.wapi_request('GET', object_type="pxgrid:endpoint")
                print(get_ref)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                response = ib_NIOS.wapi_request('POST', object_type=ref1+"?_function=test_connection")
                sleep(30)
                print response
                logging.info(response)
		sleep(25)
                assert re.search(r'"text": "Test connection failed: Invalid certificate."',response[-1])
                print("Test Case 34 Execution Completed")
		
        @pytest.mark.run(order=35)
        def test_035_Delete_Endpoint_after_Test_Connection_Validation_with_wrong_Client_Certificate(self):
                logging.info("Delete_Endpoint after_Test_Connection_Validation_with_wrong_Client_Certificate")
                get_ref = ib_NIOS.wapi_request('GET', object_type="pxgrid:endpoint")
                print(get_ref)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
		response = ib_NIOS.wapi_request('DELETE', object_type=ref1)
		sleep(15)
     		print("Test Case 35 Execution Completed")
                        		
	@pytest.mark.run(order=36)
        def test_036_Create_IPv4_network_reverse_mapping_zone(self):
                logging.info("Create an ipv4 network default network view")
                network_data = {"network": config.network+".0/24","network_view": "default","members":[{"_struct": "dhcpmember","ipv4addr":config.grid_vip}]}
                response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(network_data), grid_vip=config.grid_vip)
                print(response)
                print("Created the ipv4network  in default view")
                logging.info("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 15 sec.,")
                sleep(15)
                print("Test Case 36 Execution Completed")

        @pytest.mark.run(order=37)
        def test_037_Verify_IPv4_network_reverse_mapping_zone(self):
                logging.info("Verify an ipv4 network default network view")
                new_data =  ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
                new_data=json.loads(new_data)
                print ("result of adding ipv4 network",new_data)
                sleep(20) #wait for 20 secs for the member to get started
                if (new_data[0]['network']==config.network+".0/24"):
                        assert True
                        print("Test Case 37 Execution Completed")
                else:
                        assert False
                        print("Test Case 37 Execution Failed")
        		
	@pytest.mark.run(order=38)
        def test_038_Starting_Logs(self):
                logging.info("Start Logs")
                log("start","/var/log/syslog  /infoblox/var/infoblox.log",config.grid_vip)
                sleep(20)
		print("Test Case 38 Execution Completed")

#Creating END Point with ALL coorect Inputs 
 
	@pytest.mark.run(order=39)
        def test_039_Try_to_Add_Cisco_ISE_endpoint_with_ALL_Correct_Inputs(self):
                logging.info("Create_Cisco_ISE_Endpoint with ALL_Correct_Inputs")
                dir_name="./Cisco_ISE_templates/"
                base_filename="ramesh1.cer"
                token = common_util.generate_token_from_file(dir_name,base_filename)
                print ("Token details :",token)
                data= {"address": config.cisco_ise_server_ip,"comment": "Add cisco ISE endpoint","log_level": "DEBUG","name": "cisco_ise_endpoint2","network_view": "default","outbound_member_type": "GM","outbound_members": [],"publish_settings": {"enabled_attributes":["IPADDRESS"]}, "subscribe_settings": {"enabled_attributes": ["DOMAINNAME","ENDPOINT_PROFILE","SESSION_STATE"],"mapped_ea_attributes": []},"template_instance": {"parameters": [],"template": "PxgrdiSessionTemplate"},"timeout": 30,"vendor_identifier": "pxgrid","wapi_user_name": "admin","wapi_user_password":"infoblox","client_certificate_token":str(token)}

                response = ib_NIOS.wapi_request('POST', object_type="pxgrid:endpoint", fields=json.dumps(data))
                print response
                logging.info(response)
		sleep(50)
                assert re.search(r'cisco_ise_endpoint2',response)
                print("Test Case 39 Execution Completed")

	@pytest.mark.run(order=40)
        def test_040_CiscoISE_Endpoint_Test_Connection_Validation(self):
                logging.info("CiscoISE Endpoint Test Connection Validation")
                get_ref = ib_NIOS.wapi_request('GET', object_type="pxgrid:endpoint")
                print(get_ref)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
		response = ib_NIOS.wapi_request('POST', object_type=ref1+"?_function=test_connection")
                print response
                logging.info(response)
		sleep(20)
                assert re.search(r'"result": "SUCCESS"',response)
                print("Test Case 40 Execution Completed")

	@pytest.mark.run(order=41)
        def test_041_CiscoISE_Endpoint_Validation(self):
                logging.info("CiscoISE Endpoint Validation")
                response = ib_NIOS.wapi_request('GET', object_type="pxgrid:endpoint?_return_fields=name,address,publish_settings,subscribe_settings")
                print response
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                print response
                print(type(response))
                logging.info(response)
		if(config.cisco_ise_server_ip in response) and ('"name":"cisco_ise_endpoint2"' in response) and ('"publish_settings":"enabled_attributes":"IPADDRESS"' in response) and ('"subscribe_settings":"enabled_attributes":"DOMAINNAME","ENDPOINT_PROFILE","SESSION_STATE"' in response):
                        assert True
                else:
                        assert False
                print("Test case 41 Execution Completed")
                sleep(20)

        @pytest.mark.run(order=42)
        def test_042_Stopping_Logs(self):
                logging.info("Stop Logs")
                log("stop","/var/log/syslog  /infoblox/var/infoblox.log",config.grid_vip)
                sleep(20)
		print("Test Case 42 Execution Completed")

        @pytest.mark.run(order=43)
        def test_043_looking_for_CiscoISEEvent_session_seen(self):
		logging.info("CiscoISEEvent_session_seen")
                check=commands.getoutput(" grep -cw \".*CiscoISEEvent:session_seen.* 10.* user.* has been created\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                if (int(check)!=0):
                    print("CiscoISEEvent:session_seen")
                    assert True
                else:
                    assert False
                sleep(20)	
		print("Test case 43 Execution Completed")
			
	@pytest.mark.run(order=44)
        def test_044_Enable_Network_users_Grid_level(self):
                logging.info("Enable Network users Grid level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
                print(get_ref)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
		data={"ms_setting":{"enable_network_users": True}}
		response = ib_NIOS.wapi_request('PUT',ref= ref1,fields=json.dumps(data))
                print("Test Case 44 Execution Completed")
                print response
                logging.info(response)
                sleep(20)

	@pytest.mark.run(order=45)
        def test_045_Verify_Enabled_Network_users_Grid_level(self):
                logging.info("Verify Enabled Network users Grid level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
                print(get_ref)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1	
		response = ib_NIOS.wapi_request('GET',ref= ref1,params="?_return_fields=ms_setting")
                print response
                logging.info(response)
		assert re.search(r'"enable_network_users": true',response)
                print("Test Case 45 Execution Completed")	
                sleep(20)
        
# Creating END Point Notification and Tepmlate Execution Starts from here
        @pytest.mark.run(order=46)
        def test_046_Create_Cisco_ISE_Endpoint_IPAM_Notification(self):
                logging.info("Create_Cisco_ISE_Endpoint_IPAM_Notification")
                response = ib_NIOS.wapi_request('GET',object_type="pxgrid:endpoint?_return_fields=address")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                notification=response[3]
                print("notification",notification)
		data = {"name":"Test","notification_target":notification,"event_type":"IPAM","template_instance": {"template": "IPAM_PxgridEvent"},"expression_list": [],"notification_action": "RESTAPI_TEMPLATE_INSTANCE"}
                print ("data provided :",data)
                response = ib_NIOS.wapi_request('POST', object_type="notification:rule",fields=json.dumps(data))
                print(response)
                global notification_ref
                notification_ref=response
                sleep(60)
		logging.info("Test Case 46 Execution Completed")
	
	@pytest.mark.run(order=47)
        def test_047_Verify_Cisco_ISE_Endpoint_IPAM_Notification(self):
                logging.info("Verify_Cisco_ISE_Endpoint_IPAM_Notification")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule?_return_fields=template_instance,event_type,name",grid_vip=config.grid_vip)
                print("response    : ",response)
		if('"name": "Test"'in response) and ('"template": "IPAM_PxgridEvent"' in response) and ('"event_type": "IPAM"' in response):
			 assert True
            	else:
                    	 assert False
	        sleep(10)
		logging.info("Test Case 47 Execution Completed")
        
	@pytest.mark.run(order=48)
        def test_048_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
		sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		print("Test Case 48 Execution Completed")
        	
	@pytest.mark.run(order=49)
        def test_049_create_fixed_address(self):
                logging.info("Create an ipv4 fixed address with default network view")
                data = {"ipv4addr": config.network+".2","mac": "aa:bb:cc:dd:ee:ff","network_view": "default"}
                response = ib_NIOS.wapi_request('POST', object_type="fixedaddress", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                fixed_address_ref=response
                global ref1
                ref1=response
                print("reff",ref1)
                print("Created the fixed address ")
                logging.info("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 20 sec.,")
                sleep(30) 
                print("Test Case 49 Execution Completed")
	
	@pytest.mark.run(order=50)
        def test_050_Verify_Fixed_Address(self):
                logging.info("Verify Fixed Address")
                response = ib_NIOS.wapi_request('GET',object_type="fixedaddress?_return_fields=mac,ipv4addr",grid_vip=config.grid_vip)
                print("response    : ",response)
		Addr=config.network+".2"
		print(Addr)
		if('"ipv4addr": "'+Addr+'"'in response) and ('"mac": "aa:bb:cc:dd:ee:ff"' in response):
                         assert True
                else:
                         assert False
                sleep(20)
		print("Test Case 50 Execution Completed")

	@pytest.mark.run(order=51)
        def test_051_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		print("Test Case 51 Execution Completed")

	@pytest.mark.run(order=52)
        def test_052_looking_for_Template_execution_Status(self):
		logging.info("looking_for_Templated_Execution_Status")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("template was executed successfully")
                    assert True
                else:
		    print("template was not executed")
                    assert False
                sleep(20)
		print("Test Case 52 Execution Completed")

	@pytest.mark.run(order=53)
        def test_053_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		print("Test Case 53 Execution Completed")
	
	@pytest.mark.run(order=54)
        def test_054_modify_fixed_address(self):
                logging.info("modify an ipv4 fixed address with default network view")
		ref2=ref1.replace('"','')
                print("reff",ref2,type(ref2))
		Addr=config.network+'.2'
		print(Addr)
                data = { "ipv4addr": Addr,"mac": "aa:bb:cc:dd:ee:11","network_view": "default"}
                response = ib_NIOS.wapi_request('PUT', ref=ref2, fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                print("Created the fixed address ")
                logging.info("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 20 sec.,")
                sleep(30) 
                print("Test Case 54 Execution Completed")

        @pytest.mark.run(order=55)
        def test_055_Verify_Modified_Fixed_Address(self):
                logging.info("Verify Modified Fixed Address")
		ref2=ref1.replace('"','')
                print("reff",ref2,type(ref2))
                response = ib_NIOS.wapi_request('GET',object_type=ref2+"?_return_fields=mac,ipv4addr",grid_vip=config.grid_vip)
                print("response    : ",response)
		Addr=config.network+'.2'
		if('"ipv4addr": "'+Addr+'"'in response) and ('"mac": "aa:bb:cc:dd:ee:11"' in response):
                         assert True
                else:
                         assert False
                sleep(20)
		print("Test Case 55 Execution Completed")

        @pytest.mark.run(order=56)
        def test_056_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		print("Test Case 56 Execution Completed")

        @pytest.mark.run(order=57)
        def test_057_looking_for_Template_execution_Status(self):
		logging.info("looking_for_Templated_Execution_Status")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("template was executed successfully")
                    assert True
                else:
		    print("template was not executed")
                    assert False
                sleep(20)
		print("Test Case 57 Execution Completed")

	@pytest.mark.run(order=58)
        def test_058_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
		sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		print("Test Case 58 Execution Completed")

        @pytest.mark.run(order=59)
        def test_059_delete_fixed_address(self):
                logging.info("delete an ipv4 network default network view")
                ref2=ref1.replace('"','')
                print("reff",ref2,type(ref2))
                response = ib_NIOS.wapi_request('DELETE', ref=ref2, grid_vip=config.grid_vip)
                print(response)
                print("Created the fixed address ")
                logging.info("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 20 sec.,")
                sleep(30) 
                print("Test Case 59 Execution Completed")

        @pytest.mark.run(order=60)
        def test_060_Verify_Deleted_Fixed_Address(self):
                logging.info("Verify Deleted Fixed Address")
                ref2=ref1.replace('"','')
                print("reff",ref2,type(ref2))
                response = ib_NIOS.wapi_request('GET',object_type=ref2+"?_return_fields=mac,ipv4addr",grid_vip=config.grid_vip)
                print(response)
                response=str(response)
                if("Reference "+ref2+" not found" in response):
			assert True
		else:
			assert False
                sleep(10)
		print("Test Case 60 Execution Completed")
	
	@pytest.mark.run(order=61)
        def test_061_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		print("Test Case 61 Execution Completed")

	@pytest.mark.run(order=62)
        def test_062_looking_for_Template_execution_Status(self):
		logging.info("looking_for_Templated_Execution_Status")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("template was executed successfully")
                    assert True
                else:
		    print("template was not executed")
                    assert False
                sleep(20)	
		print("Test Case 62 Execution Completed")

	@pytest.mark.run(order=63)
        def test_063_Modify_Cisco_ISE_Endpoint_Notification_with_publish_settings(self):
                logging.info("Modify_Cisco_ISE_Endpoint_Notification with publish_settings")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                notification=response[3]
                print("notification",notification)
                data = {"event_type":"IPAM","publish_settings":{"enabled_attributes":["CLIENT_ID","IPADDRESS"]},"template_instance": {"template": "IPAM_PxgridEvent"},"expression_list": [],"notification_action": "RESTAPI_TEMPLATE_INSTANCE"}
                print ("data provided :",data)
                response = ib_NIOS.wapi_request('PUT', object_type=notification,fields=json.dumps(data))
                print(response)
                print("Test Case 63 Execution Completed")
                sleep(40)

	@pytest.mark.run(order=64)
        def test_064_Verify_Modified_Cisco_ISE_Endpoint_Notification(self):
                logging.info("Verify Modified Cisco ISE Endpoint Notification")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule?_return_fields=publish_settings",grid_vip=config.grid_vip)
                print("response    : ",response)
		response=response.replace('\n','').replace(' ','').replace('{','').replace('}','')
		print("###",response)
		if('"CLIENT_ID"'in response) and ('"IPADDRESS"' in response):
                         assert True
                else:
                         assert False
                sleep(20)
		print("Test Case 64 Execution Completed")
        
	@pytest.mark.run(order=65)
        def test_065_Delete_Cisco_ISE_Endpoint_Notification(self):
		logging.info("Delete_Cisco_ISE_Endpoint_Notification")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                notification=response[3]
                print("notification",notification)
                noti_ref=notification_ref.replace('"','')
                response = ib_NIOS.wapi_request('DELETE', object_type=noti_ref)
                print(response)
                print("Test Case 65 Execution Completed")
                sleep(60)
                
	@pytest.mark.run(order=66)
        def test_066_Verify_Deleted_Cisco_ISE_Endpoint_Notification(self):
                logging.info("Verify Deleted_Cisco_ISE_Endpoint_Notification")
                noti_ref=notification_ref.replace('"','')
                response = ib_NIOS.wapi_request('GET',object_type=noti_ref)
                print("response    : ",response)
                print(type(response))
                response=str(response)
		if("Reference "+noti_ref+" not found" in response):
			assert True
                else:
                        assert False			
		print("Test Case 66 Execution Completed")
	
	@pytest.mark.run(order=67)
        def test_067_Upload_Cisco_ISE_Endpoint_DHCPLEASE_Event_Template(self):
                logging.info("Upload Version Cisco ISE endpoint IPAM Event Template")
                dir_name="./Cisco_ISE_templates/"
                base_filename="DHCPLease_Event.json"
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
                print("Test Case 67 Execution Completed")
                sleep(20)

        @pytest.mark.run(order=68)
        def test_068_Validate_DHCPLEASE_Event_Template_Uploaded(self):
                logging.info("Validating DHCPLEASE Event template get uploaded")
                data = {"name": "DHCPLease_Event"}
                get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rest:template",fields=json.dumps(data))
                logging.info(get_temp)
                print get_temp
                res = json.loads(get_temp)
                print res
                for i in res:
                        print i
                        logging.info("found")
                        assert i["name"] == "DHCPLease_Event"
                print("Test Case 68 Execution Completed")
                sleep(20)

	@pytest.mark.run(order=69)
        def test_069_Create_Cisco_ISE_Endpoint_DHCP_Notification(self):
                logging.info("Create_Cisco_ISE_Endpoint DHCP Notification")
                response = ib_NIOS.wapi_request('GET',object_type="pxgrid:endpoint?_return_fields=address")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                notification=response[3]
                print("notification",notification)
                data = {"name":"Test_DHCP","notification_target":notification,"event_type":"DHCP_LEASES","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "DHCP_LEASE_STATE","op1_type": "FIELD","op2": "DHCP_LEASE_STATE_ABANDONED","op2_type": "STRING"},{"op": "ENDLIST"}],"template_instance": {"template": "DHCPLease_Event"},"notification_action": "RESTAPI_TEMPLATE_INSTANCE"}
                print ("data provided :",data)
                response = ib_NIOS.wapi_request('POST', object_type="notification:rule",fields=json.dumps(data))
                print(response)
                print("Test Case 69 Execution Completed")
                sleep(60)

        @pytest.mark.run(order=70)
        def test_070_Verify_Cisco_ISE_Endpoint_DHCP_Notification(self):
                logging.info("Verify_Cisco_ISE_Endpoint_DHCP_Notification")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule?_return_fields=template_instance,event_type,name,expression_list",grid_vip=config.grid_vip)
                print("response    : ",response)
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                print("response    : ",response)
		if('"name":"Test_DHCP"'in response) and ('"template":"DHCPLease_Event"' in response) and ('"event_type":"DHCP_LEASES"'in response) and ('"expression_list":"op":"AND","op1_type":"LIST","op":"EQ","op1":"DHCP_LEASE_STATE","op1_type":"FIELD","op2":"DHCP_LEASE_STATE_ABANDONED","op2_type":"STRING","op":"ENDLIST"' in response):
                         assert True
                else:
                         assert False
                sleep(20)
		print("Test Case 70 Execution Completed")
        
        @pytest.mark.run(order=71)
        def test_071_Create_IPv4_range_in_defaultnetwork_view(self):
            	logging.info("Create an IPv4 range in defaultnetwork view")
            	network_data = {"network":config.network+".0/24","start_addr":config.network+".1","end_addr":config.network+".1","member":{"_struct":"dhcpmember","ipv4addr":config.grid_vip}}
         	response = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(network_data), grid_vip=config.grid_vip)
		sleep(10)
            	print (response)
                global ipam_range
                ipam_range=response
            	print("Created the ipv4 prefix range with bits 16  in default view")
            	logging.info("Restart DHCP Services")
            	grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
            	ref = json.loads(grid)[0]['_ref']
            	data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
            	request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
		sleep(30)
            	logging.info("Wait for 20 sec.,")
		print("Test Case 71 Execution Completed")
		
        @pytest.mark.run(order=72)
        def test_072_Verify_IPv4_range(self):
            	logging.info("Verify an ipv4 range default network view")
                ipam_range1=ipam_range.replace('"','')
            	new_data =  ib_NIOS.wapi_request('GET', object_type=ipam_range1, grid_vip=config.grid_vip)
            	new_data=json.loads(new_data)
            	sleep(10)
            	new_data = eval(json.dumps(new_data))
            	print(new_data,type(new_data))
                new_data=str(new_data)
                if("'start_addr': '"+config.network+".1'" in new_data) and ("'end_addr': '"+config.network+".1'" in new_data):
                	assert True
            	else:
                	assert False
                	print ("Test Case 72 Execution Completed")
			
        @pytest.mark.run(order=73)
        def test_073_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
		sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)	
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		print("Test Case 73 Execution Completed")

        @pytest.mark.run(order=74)
        def test_074_Executing_dras_command(self):
            	logging.info("Executing dras command")
		#for i in range(10):
		dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1 -x l='+config.network+'.0'
            	dras_cmd1 = os.system(dras_cmd)
		print(dras_cmd)
		sleep(5)
                #sleep(30)
            	print (dras_cmd1)
		print("Test Case 74 Execution Completed")

        @pytest.mark.run(order=75)
        def test_075_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		print("Test Case 75 Execution Completed")

        @pytest.mark.run(order=76)
        def test_076_looking_for_Template_execution_Status(self):
		logging.info("looking_for_Templated_Execution_Status")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("template was executed successfully")
                    assert True
                else:
		    print("template was not executed")
                    assert False
                sleep(20)
		print("Test Case 76 Execution Completed")
         	
        @pytest.mark.run(order=77)
        def test_077_Delete_IPV4_Network(self):
                logging.info("Delete IPV4 Network")
                response = ib_NIOS.wapi_request('GET',object_type="network")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                notification=response[3]
                print("notification",notification)
                response = ib_NIOS.wapi_request('DELETE', object_type=notification)
                print(response)
		logging.info("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(30)
                logging.info("Wait for 30 sec.,")
             	print("Test Case 77 Execution Completed")
        
        @pytest.mark.run(order=78)
        def test_078_Modify_Cisco_ISE_Endpoint_Notification_with_DHCP_LEASE_STATE_ACTIVE(self):
                logging.info("Modify_Cisco_ISE_Endpoint_Notification with DHCP_LEASE_STATE_ACTIVE")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                ref1=response[3]
                print("ref1",ref1)
                data = {"event_type":"DHCP_LEASES","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "DHCP_LEASE_STATE","op1_type": "FIELD","op2": "DHCP_LEASE_STATE_ACTIVE","op2_type": "STRING"},{"op": "ENDLIST"}],"template_instance": {"template": "DHCPLease_Event"},"notification_action": "RESTAPI_TEMPLATE_INSTANCE"}
                print ("data provided :",data)
                response = ib_NIOS.wapi_request('PUT', ref= ref1,fields=json.dumps(data))
                print(response)
                logging.info("Test Case 80 Execution Completed")
                sleep(10)
		print("Test Case 78 Execution Completed")

        @pytest.mark.run(order=79)
        def test_079_Verify_Modified_Cisco_ISE_Endpoint_Notification_with_DHCP_LEASE_STATE_ACTIVE(self):
                logging.info("Verify Modified_Cisco_ISE_Endpoint_Notification with DHCP_LEASE_STATE_ACTIVE")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule?_return_fields=template_instance,event_type,name,expression_list",grid_vip=config.grid_vip)
                print("response    : ",type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                print("response    : ",response)
		if('"name":"Test_DHCP"'in response) and ('"template":"DHCPLease_Event"' in response) and ('"event_type":"DHCP_LEASES"'in response) and ('"expression_list":"op":"AND","op1_type":"LIST","op":"EQ","op1":"DHCP_LEASE_STATE","op1_type":"FIELD","op2":"DHCP_LEASE_STATE_ACTIVE","op2_type":"STRING","op":"ENDLIST"' in response):
                         assert True
                else:
                         assert False	
                sleep(10)
		print("Test Case 79 Execution Completed")

        @pytest.mark.run(order=80)
        def test_080_Create_IPv4_network_in_defaultnetwork_view(self):
            	logging.info("Create an IPv4 network in defaultnetwork view")
            	network_data = {"network":"10.36.0.0/16","members": [{"_struct": "dhcpmember","ipv4addr": config.grid_vip}]}
            	response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(network_data), grid_vip=config.grid_vip)
            	print (response)
            	print("Created the ipv4 prefix range with bits 16  in default view")
            	logging.info("Restart DHCP Services")
            	grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
            	ref = json.loads(grid)[0]['_ref']
            	data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
            	request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
            	sleep(20)
		logging.info("Wait for 20 sec.,")
           	print("Test Case 80 Execution Completed") 

        @pytest.mark.run(order=81)
        def test_081_Verify_IPv4_network_range(self):
            	logging.info("Verify an ipv4 network default network view")
            	new_data =  ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
            	new_data=json.loads(new_data)
            	sleep(20)
            	print(new_data[0])
            	if (new_data[0]['network']=="10.36.0.0/16"):
                	assert True
                	print("Test Case 81 Execution Completed")
            	else:
                	assert False
                	print("Test Case 81 Execution Failed")

        @pytest.mark.run(order=82)
        def test_082_Create_IPv4_range_reverse_mapping_zone(self):
            	logging.info("Create an IPv4 range in defaultnetwork view")
            	network_data = {"network":"10.36.0.0/16","start_addr":"10.36.0.1","end_addr":"10.36.0.100","member":{"_struct":"dhcpmember","ipv4addr":config.grid_vip}}
            	response = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(network_data), grid_vip=config.grid_vip)
            	print (response)
                print("Created the ipv4 prefix range with bits 16  in default view")
            	logging.info("Restart DHCP Services")
            	grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
            	ref = json.loads(grid)[0]['_ref']
            	data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
            	request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
		sleep(20) 
           	logging.info("Wait for 20 sec.,")
            	print("Test Case 82 Execution Completed")
            
        @pytest.mark.run(order=83)
        def test_083_Verify_IPv4_network_range(self):
            	logging.info("Verify an ipv4 range default network view")
            	new_data =  ib_NIOS.wapi_request('GET', object_type="range", grid_vip=config.grid_vip)
            	new_data=json.loads(new_data)
            	sleep(20)
            	print(new_data)
            	if ((new_data[0]['start_addr']=="10.36.0.1") and (new_data[0]['end_addr']=="10.36.0.100")):
                	assert True
                	print("Test Case 83 Execution Completed")
            	else:
                	assert False
                	print ("Test Case 83 Execution Failed")

        @pytest.mark.run(order=84)
        def test_084_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
		sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		print("Test Case 84 Execution Completed")

        @pytest.mark.run(order=85)
        def test_085_Executing_dras_command(self):
            	logging.info("Executing dras command")
            	dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
            	dras_cmd1 = os.system(dras_cmd)
                sleep(10)
                print (dras_cmd1)
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(10)
            	print (dras_cmd1)
		print ("Test Case 85 Execution Completed")

        @pytest.mark.run(order=86)
        def test_086_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		print ("Test Case 86 Execution Completed")

        @pytest.mark.run(order=87)
        def test_087_looking_for_Template_execution_Status(self):
		logging.info("looking_for_Templated_Execution_Status")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("template was executed successfully")
                    assert True
                else:
                    assert False
                sleep(20)
		print ("Test Case 87 Execution Completed")

	@pytest.mark.run(order=88)
        def test_088_Changing_DHCP_Lease_time(self):
                logging.info("Changing DHCP Lease time")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dhcpproperties")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                ref1=response[3]
                print("ref1",ref1)
                data = {"options": [{"value": "30","name": "dhcp-lease-time"}]}
                print ("data provided :",data)
                response = ib_NIOS.wapi_request('PUT', ref= ref1,fields=json.dumps(data))
                print(response)
                logging.info("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 20 sec.,")
                sleep(20) 
                logging.info("Test Case 88 Execution Completed")

        @pytest.mark.run(order=89)
        def test_089_Modify_Cisco_ISE_Endpoint_Notification_with_DHCP_LEASE_STATE_FREE(self):
                logging.info("Modify_Cisco_ISE_Endpoint_Notification with DHCP_LEASE_STATE_FREE")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                ref1=response[3]
                print("ref1",ref1)
                data = {"event_type":"DHCP_LEASES","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "DHCP_LEASE_STATE","op1_type": "FIELD","op2": "DHCP_LEASE_STATE_FREE","op2_type": "STRING"},{"op": "ENDLIST"}],"template_instance": {"template": "DHCPLease_Event"},"notification_action": "RESTAPI_TEMPLATE_INSTANCE"}
                print ("data provided :",data)
                response = ib_NIOS.wapi_request('PUT', ref= ref1,fields=json.dumps(data))
                print(response)
                logging.info("Test Case 89 Execution Completed")
        
        @pytest.mark.run(order=90)
        def test_090_Verify_Modified_Cisco_ISE_Endpoint_Notification_with_DHCP_LEASE_STATE_FREE(self):
                logging.info("Verify Modified_Cisco_ISE_Endpoint_Notification with DHCP_LEASE_STATE_FREE")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule?_return_fields=template_instance,event_type,name,expression_list",grid_vip=config.grid_vip)
                print("response    : ",response)
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                print("response    : ",response)
		if('"name":"Test_DHCP"'in response) and ('"template":"DHCPLease_Event"' in response) and ('"event_type":"DHCP_LEASES"'in response) and ('"expression_list":"op":"AND","op1_type":"LIST","op":"EQ","op1":"DHCP_LEASE_STATE","op1_type":"FIELD","op2":"DHCP_LEASE_STATE_FREE","op2_type":"STRING","op":"ENDLIST"' in response):
                         assert True
                else:
                         assert False
                sleep(20)
        	print ("Test Case 90 Execution Completed")

        @pytest.mark.run(order=91)
        def test_091_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
		sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                logging.info("Test Case 07 Execution Completed")
                sleep(20)
		print ("Test Case 91 Execution Completed")
	
        @pytest.mark.run(order=92)
        def test_092_Executing_dras_command(self):
            	logging.info("Executing dras command")
            	dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
            	dras_cmd1 = os.system(dras_cmd)
		sleep(50)
                print (dras_cmd1)
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(50)
            	print (dras_cmd1)
		print("Test Case 92 Execution Completed")

        @pytest.mark.run(order=93)
        def test_093_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		print ("Test Case 93 Execution Completed")

        @pytest.mark.run(order=94)
        def test_094_looking_for_Template_execution_Status(self):
		logging.info("looking_for_Templated_Execution_Status")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("template was executed successfully")
                    assert True
                else:
		    print("template not executed")
                    assert False
                sleep(20)
		print ("Test Case 94 Execution Completed")
                
        @pytest.mark.run(order=95)
        def test_095_Modify_Cisco_ISE_Endpoint_Notification_with_DHCP_LEASE_STATE_OFFERED(self):
                logging.info("Modify_Cisco_ISE_Endpoint_Notification with DHCP_LEASE_STATE_OFFERED")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                ref1=response[3]
                print("ref1",ref1)
                data = {"event_type":"DHCP_LEASES","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "DHCP_LEASE_STATE","op1_type": "FIELD","op2": "DHCP_LEASE_STATE_OFFERED","op2_type": "STRING"},{"op": "ENDLIST"}],"template_instance": {"template": "DHCPLease_Event"},"notification_action": "RESTAPI_TEMPLATE_INSTANCE"}
                print ("data provided :",data)
                response = ib_NIOS.wapi_request('PUT', ref= ref1,fields=json.dumps(data))
                print(response)
		print("Test Case 95 Execution Completed")
		
        @pytest.mark.run(order=96)
        def test_096_Verify_Modified_Cisco_ISE_Endpoint_Notification_with_DHCP_LEASE_STATE_OFFERED(self):
                logging.info("Verify Modified_Cisco_ISE_Endpoint_Notification with DHCP_LEASE_STATE_OFFERED")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule?_return_fields=template_instance,event_type,name,expression_list",grid_vip=config.grid_vip)
                print("response    : ",response)
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                print("response    : ",response)
		if('"name":"Test_DHCP"'in response) and ('"template":"DHCPLease_Event"' in response) and ('"event_type":"DHCP_LEASES"'in response) and ('"expression_list":"op":"AND","op1_type":"LIST","op":"EQ","op1":"DHCP_LEASE_STATE","op1_type":"FIELD","op2":"DHCP_LEASE_STATE_OFFERED","op2_type":"STRING","op":"ENDLIST"' in response):
                         assert True
                else:
                         assert False
                sleep(20)
		print ("Test Case 96 Execution Completed")
                
        @pytest.mark.run(order=97)
        def test_097_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
		sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		print ("Test Case 97 Execution Completed")

        @pytest.mark.run(order=98)
        def test_098_Executing_dras_command(self):
            	logging.info("Executing dras command")
            	dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
            	dras_cmd1 = os.system(dras_cmd)
                sleep(15)
                print (dras_cmd1)
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(15)
            	print (dras_cmd1)
		dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(15)
                print (dras_cmd1)
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(15)
                print (dras_cmd1)
		print ("Test Case 98 Execution Completed")

        @pytest.mark.run(order=99)
        def test_099_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		print ("Test Case 99 Execution Completed")

	@pytest.mark.run(order=100)
        def test_100_looking_for_Template_execution_Status(self):
		logging.info("looking_for_Templated_Execution_Status")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("template was executed successfully")
                    assert True
                else:
		    print("template was not Executed")
                    assert False
                sleep(20)
		print ("Test Case 100 Execution Completed")                

        @pytest.mark.run(order=101)
        def test_101_Modify_Cisco_ISE_Endpoint_Notification_DHCP_LEASE_STATE_STATIC_Negative(self):
                logging.info("Modify_Cisco_ISE_Endpoint_Notification DHCP_LEASE_STATE_STATIC Negative")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                ref1=response[3]
                print("ref1",ref1)
                data = {"event_type":"DHCP_LEASES","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "DHCP_LEASE_STATE","op1_type": "FIELD","op2": "DHCP_LEASE_STATE_STATIC","op2_type": "STRING"},{"op": "ENDLIST"}],"template_instance": {"template": "DHCPLease_Event"},"notification_action": "RESTAPI_TEMPLATE_INSTANCE"}
                print ("data provided :",data)
                response = ib_NIOS.wapi_request('PUT', ref= ref1,fields=json.dumps(data))
                print(response)
                print("Test Case 101 Execution Completed")
               
        @pytest.mark.run(order=102)
        def test_102_Verify_Modified_Cisco_ISE_Endpoint_Notification_DHCP_LEASE_STATE_STATIC_Negative(self):
                logging.info("Verify Modified_Cisco_ISE_Endpoint_Notification DHCP_LEASE_STATE_STATIC Negative")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule?_return_fields=template_instance,event_type,name,expression_list",grid_vip=config.grid_vip)
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                print("response    : ",response)
		if('"name":"Test_DHCP"'in response) and ('"template":"DHCPLease_Event"' in response) and ('"event_type":"DHCP_LEASES"'in response) and ('"expression_list":"op":"AND","op1_type":"LIST","op":"EQ","op1":"DHCP_LEASE_STATE","op1_type":"FIELD","op2":"DHCP_LEASE_STATE_STATIC","op2_type":"STRING","op":"ENDLIST"' in response):
                         assert True
                else:
                         assert False
                sleep(20)
		print("Test Case 102 Execution Completed")
 
        @pytest.mark.run(order=103)
        def test_103_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
		sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
		logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		print("Test Case 103 Execution Completed")

        @pytest.mark.run(order=104)
        def test_104_Executing_dras_command(self):
            	logging.info("Executing dras command")
            	dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
            	dras_cmd1 = os.system(dras_cmd)
                sleep(30)
                print (dras_cmd1)
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(30)
		print("Test Case 104 Execution Completed")

        @pytest.mark.run(order=105)
        def test_105_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		print("Test Case 105 Execution Completed")	

        @pytest.mark.run(order=106)
        def test_106_looking_for_Template_execution_Status_Negative(self):
		logging.info("looking_for_Templated_Execution_Status_Negative")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)==0):
                    print("template was executed successfully")
                    assert True
                else:
		     print("template was not executed")
                     assert False
                sleep(20)
		print("Test Case 106 Execution Completed")

        @pytest.mark.run(order=107)
        def test_107_create_fixed_address_To_request_Lease(self):
                logging.info("Create an fixed address To_request_Lease")
                data = { "ipv4addr": "10.36.0.13","mac": "aa:bb:cc:dd:ee:ff","network_view": "default"}
                response = ib_NIOS.wapi_request('POST', object_type="fixedaddress", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                print("Created the fixed address ")
                logging.info("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 20 sec.,")
                sleep(30) 
                print("Test Case 107 Execution Completed")

        @pytest.mark.run(order=108)
        def test_108_Verify_Fixed_Address_To_request_Lease(self):
                logging.info("Verify Fixed Address To_request_Lease")
                response = ib_NIOS.wapi_request('GET',object_type="fixedaddress?_return_fields=mac,ipv4addr",grid_vip=config.grid_vip)
                print("response    : ",response)
		if('"ipv4addr": "10.36.0.13"'in response) and ('"mac": "aa:bb:cc:dd:ee:ff"' in response):
                         assert True
                else:
                         assert False
                sleep(20)
		print("Test Case 108 Execution Completed")

        @pytest.mark.run(order=109)
        def test_109_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
		sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		print("Test Case 109 Execution Completed")

        @pytest.mark.run(order=110)
        def test_110_Executing_dras_command(self):
            	logging.info("Executing dras command")
            	dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'-a aa:bb:cc:dd:ee:ff'
            	dras_cmd1 = os.system(dras_cmd)
                sleep(15)
            	print (dras_cmd1)
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'-a aa:bb:cc:dd:ee:ff'
                dras_cmd1 = os.system(dras_cmd)
                sleep(15)
                print(dras_cmd1)
		print("Test Case 110 Execution Completed")

        @pytest.mark.run(order=111)
        def test_111_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		print("Test Case 111 Execution Completed")

        @pytest.mark.run(order=112)
        def test_112_looking_for_Template_execution_Status(self):
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("template was executed successfully")
                    assert True
                else:
		    print("template was not Executed")
                    assert False
                sleep(20) 
		print("Test Case 112 Execution Completed")

        @pytest.mark.run(order=113)
        def test_113_Modify_Cisco_ISE_Endpoint_Notification_With_NetwotkView_CONTAINS(self):
                logging.info("Modify_Cisco_ISE_Endpoint_Notification with Networkview_CONTAINS")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                ref1=response[3]
                print("ref1",ref1)
                data = {"event_type":"DHCP_LEASES","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "REGEX","op1": "NETWORK_VIEW","op1_type": "FIELD","op2": "~def","op2_type": "STRING"},{"op": "ENDLIST"}],"template_instance": {"template": "DHCPLease_Event"},"notification_action": "RESTAPI_TEMPLATE_INSTANCE"}
                print ("data provided :",data)                                                                                                                                                                              
                response = ib_NIOS.wapi_request('PUT', ref= ref1,fields=json.dumps(data))
                print(response)
                print("Test Case 113 Execution Completed")
                
        @pytest.mark.run(order=114)
        def test_114_Verify_Modified_Cisco_ISE_Endpoint_Notification_CONTAINS(self):
                logging.info("Verify Modified_Cisco_ISE_Endpoint_Notification CONTAINS")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule?_return_fields=template_instance,event_type,name,expression_list",grid_vip=config.grid_vip)
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                print("response    : ",response)
		if('"name":"Test_DHCP"'in response) and ('"template":"DHCPLease_Event"' in response) and ('"op1":"NETWORK_VIEW"'in response) and ('"expression_list":"op":"AND","op1_type":"LIST","op":"REGEX","op1":"NETWORK_VIEW","op1_type":"FIELD","op2":"~def","op2_type":"STRING","op":"ENDLIST"' in response):
                         assert True
                else:
                         assert False
                sleep(20) 
		print("Test Case 114 Execution Completed")

        @pytest.mark.run(order=115)
        def test_115_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
		sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		print("Test Case 115 Execution Completed")

        @pytest.mark.run(order=116)
        def test_116_Executing_dras_command(self):
            	logging.info("Executing dras command")
            	dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
            	dras_cmd1 = os.system(dras_cmd)
                sleep(15)
            	print (dras_cmd1)
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(15)
                print (dras_cmd1)
		print("Test Case 116 Execution Completed")

        @pytest.mark.run(order=117)
        def test_117_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		print("Test Case 117 Execution Completed")

        @pytest.mark.run(order=118)
        def test_118_looking_for_Template_execution_Status(self):
		logging.info("looking_for_Templated_Execution_Status")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("template was executed successfully")
                    assert True
                else:
		    print("template was not Executed")
                    assert False
                sleep(20)
		print("Test Case 118 Execution Completed")
	
        @pytest.mark.run(order=119)
        def test_119_Modify_Cisco_ISE_Endpoint_Notification_With_NetwotkView_CONTAINS_Negative(self):
                logging.info("Modify_Cisco_ISE_Endpoint_Notification with Networkview CONTAINS_Negative")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                ref1=response[3]
                print("ref1",ref1)
                data = {"event_type":"DHCP_LEASES","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "REGEX","op1": "NETWORK_VIEW","op1_type": "FIELD","op2": "~aef","op2_type": "STRING"},{"op": "ENDLIST"}],"template_instance": {"template": "DHCPLease_Event"},"notification_action": "RESTAPI_TEMPLATE_INSTANCE"}
                print ("data provided :",data)                                                                                                               
                response = ib_NIOS.wapi_request('PUT', ref= ref1,fields=json.dumps(data))
                print(response)
                print("Test Case 119 Execution Completed")
	
        @pytest.mark.run(order=120)
        def test_120_Verify_Modified_Cisco_ISE_Endpoint_Notification_CONTAINS_Negative(self):
                logging.info("Verify Modified_Cisco_ISE_Endpoint_Notification CONTAINS_Negative")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule?_return_fields=template_instance,event_type,name,expression_list",grid_vip=config.grid_vip)
                print("response    : ",response)
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                print("response    : ",response)
		if('"name":"Test_DHCP"' in response) and ('"template":"DHCPLease_Event"' in response) and ('"op1":"NETWORK_VIEW"'in response) and ('"expression_list":"op":"AND","op1_type":"LIST","op":"REGEX","op1":"NETWORK_VIEW","op1_type":"FIELD","op2":"~aef","op2_type":"STRING","op":"ENDLIST"' in response):
                         assert True
                else:
                         assert False
                sleep(20)
		print("Test Case 120 Execution Completed")

        @pytest.mark.run(order=121)
        def test_121_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
		sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		print("Test Case 121 Execution Completed")

	@pytest.mark.run(order=122)
        def test_122_Executing_dras_command(self):
            	logging.info("Executing dras command")
            	dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
            	dras_cmd1 = os.system(dras_cmd)
            	print (dras_cmd1)
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(15)
                print(dras_cmd1)
		print("Test Case 122 Execution Completed")
        
        @pytest.mark.run(order=123)
        def test_123_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		print("Test Case 123 Execution Completed")

        @pytest.mark.run(order=124)
        def test_124_looking_for_Template_execution_Status_Negative(self):
		logging.info("looking_for_Templated_Execution_Status Negative")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)==0):
                    print("template was executed successfully")
                    assert True
                else:
		    print("template was not Executed")    
                    assert False
                sleep(20)
		print("Test Case 124 Execution Completed")
	
        @pytest.mark.run(order=125)
        def test_125_Modify_Cisco_ISE_Endpoint_Notification_With_NetwotkView_Equals(self):
                logging.info("Modify_Cisco_ISE_Endpoint_Notification with Networkview Equals")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                ref1=response[3]
                print("ref1",ref1)
                data = {"event_type":"DHCP_LEASES","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "NETWORK_VIEW","op1_type": "FIELD","op2": "default","op2_type": "STRING"},{"op": "ENDLIST"}],"template_instance": {"template": "DHCPLease_Event"},"notification_action": "RESTAPI_TEMPLATE_INSTANCE"}
                print ("data provided :",data)                                                                                                               
                response = ib_NIOS.wapi_request('PUT', ref= ref1,fields=json.dumps(data))
                print(response)
                print("Test Case 125 Execution Completed")
    
        @pytest.mark.run(order=126)
        def test_126_Verify_Modified_Cisco_ISE_Endpoint_Notification_Equals(self):
                logging.info("Verify Modified_Cisco_ISE_Endpoint_Notification Equals")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule?_return_fields=template_instance,event_type,name,expression_list",grid_vip=config.grid_vip)
                print("response    : ",response)
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                print("response    : ",response)
		if('"name":"Test_DHCP"' in response) and ('"template":"DHCPLease_Event"' in response) and ('"op1":"NETWORK_VIEW"'in response) and ('"expression_list":"op":"AND","op1_type":"LIST","op":"EQ","op1":"NETWORK_VIEW","op1_type":"FIELD","op2":"default","op2_type":"STRING","op":"ENDLIST"' in response):
                         assert True
                else:
                         assert False
                sleep(20)
		print("Test Case 126 Execution Completed")

        @pytest.mark.run(order=127)
        def test_127_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
		sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 127 Execution Completed")

        @pytest.mark.run(order=128)
        def test_128_Executing_dras_command(self):
            	logging.info("Executing dras command")
            	dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
            	dras_cmd1 = os.system(dras_cmd)
                sleep(15)
                print (dras_cmd1)
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(15)
            	print(dras_cmd1)
		logging.info("Test Case 128 Execution Completed")

        @pytest.mark.run(order=129)
        def test_129_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 129 Execution Completed")

        @pytest.mark.run(order=130)
        def test_130_looking_for_Template_execution_Status(self):
		logging.info("looking_for_Templated_Execution_Status")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("template was executed successfully")
                    assert True
                else:
		    print("template was not Executed")
                    assert False
                sleep(20)
		logging.info("Test Case 130 Execution Completed")

        @pytest.mark.run(order=131)
        def test_131_Modify_Cisco_ISE_Endpoint_Notification_With_NetwotkView_Equals_Negative(self):
                logging.info("Modify_Cisco_ISE_Endpoint_Notification with Networkview_Equals_Negative")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                ref1=response[3]
                print("ref1",ref1)
                data = {"event_type":"DHCP_LEASES","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "NETWORK_VIEW","op1_type": "FIELD","op2": "aefault","op2_type": "STRING"},{"op": "ENDLIST"}],"template_instance": {"template": "DHCPLease_Event"},"notification_action": "RESTAPI_TEMPLATE_INSTANCE"}
                print ("data provided :",data)
                response = ib_NIOS.wapi_request('PUT', ref= ref1,fields=json.dumps(data))
                print(response)
                logging.info("Test Case 131 Execution Completed")

        @pytest.mark.run(order=132)
        def test_132_Verify_Modified_Cisco_ISE_Endpoint_Notification_Equals_Negative(self):
                logging.info("Verify Modified_Cisco_ISE_Endpoint_Notification Equals_Negative")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule?_return_fields=template_instance,event_type,name,expression_list",grid_vip=config.grid_vip)
                print("response    : ",response)
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                print("response    : ",response)
		if('"name":"Test_DHCP"' in response) and ('"template":"DHCPLease_Event"' in response) and ('"op1":"NETWORK_VIEW"'in response) and ('"expression_list":"op":"AND","op1_type":"LIST","op":"EQ","op1":"NETWORK_VIEW","op1_type":"FIELD","op2":"aefault","op2_type":"STRING","op":"ENDLIST"' in response):
                         assert True
                else:
                         assert False
                sleep(20)
		logging.info("Test Case 132 Execution Completed")
	
        @pytest.mark.run(order=133)
        def test_133_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
		sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 133 Execution Completed")

        @pytest.mark.run(order=134)
        def test_134_Executing_dras_command(self):
            	logging.info("Executing dras command")
            	dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
            	dras_cmd1 = os.system(dras_cmd)
                sleep(15)
            	print (dras_cmd1)
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(15)
                print(dras_cmd1)
		logging.info("Test Case 134 Execution Completed")
        
        @pytest.mark.run(order=135)
        def test_135_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 135 Execution Completed")

        @pytest.mark.run(order=136)
        def test_136_looking_for_Template_execution_Status_Negative(self):
		logging.info("looking_for_Templated_Execution_Status Negative")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)==0):
                    print("template was executed successfully")
                    assert True
                else:
		    print("template was not Executed")
                    assert False
                sleep(20)
		logging.info("Test Case 136 Execution Completed")

        @pytest.mark.run(order=137)
        def test_137_Modify_Cisco_ISE_Endpoint_Notification_With_NetwotkView_STARTS_WITH(self):
                logging.info("Modify_Cisco_ISE_Endpoint_Notification with Networkview STARTS_WITH")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                ref1=response[3]
                print("ref1",ref1)
                data = {"event_type":"DHCP_LEASES","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "REGEX","op1": "NETWORK_VIEW","op1_type": "FIELD","op2": "^def","op2_type": "STRING"},{"op": "ENDLIST"}],"template_instance": {"template": "DHCPLease_Event"},"notification_action": "RESTAPI_TEMPLATE_INSTANCE"}
                print ("data provided :",data)
                response = ib_NIOS.wapi_request('PUT', ref= ref1,fields=json.dumps(data))
                print(response)
                logging.info("Test Case 137 Execution Completed")

        @pytest.mark.run(order=138)
        def test_138_Verify_Modified_Cisco_ISE_Endpoint_Notification_STARTS_WITH(self):
                logging.info("Verify Modified_Cisco_ISE_Endpoint_Notification STARTS_WITH")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule?_return_fields=template_instance,event_type,name,expression_list",grid_vip=config.grid_vip)
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                print("response    : ",response)
		if('"name":"Test_DHCP"' in response) and ('"template":"DHCPLease_Event"' in response) and ('"op1":"NETWORK_VIEW"'in response) and ('"expression_list":"op":"AND","op1_type":"LIST","op":"REGEX","op1":"NETWORK_VIEW","op1_type":"FIELD","op2":"^def","op2_type":"STRING","op":"ENDLIST"' in response):
                         assert True
                else:
                         assert False
                sleep(20)
		logging.info("Test Case 138 Execution Completed")

        @pytest.mark.run(order=139)
        def test_139_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
		sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 139 Execution Completed")

        @pytest.mark.run(order=140)
        def test_140_Executing_dras_command(self):
            	logging.info("Executing dras command")
            	dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
            	dras_cmd1 = os.system(dras_cmd)
                sleep(15)
            	print (dras_cmd1)
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(15)
                print(dras_cmd1)
		logging.info("Test Case 140 Execution Completed")

        @pytest.mark.run(order=141)
        def test_141_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 141 Execution Completed")

        @pytest.mark.run(order=142)
        def test_142_looking_for_Template_execution_Status(self):
		logging.info("looking_for_Templated_Execution_Status")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("The template was executed successfully")
                    assert True
                else:
		    print("template was not Executed")    
                    assert False
                sleep(20)
		logging.info("Test Case 142 Execution Completed")

        @pytest.mark.run(order=143)
        def test_143_Modify_Cisco_ISE_Endpoint_Notification_With_NetwotkView_STARTS_WITH_Negative(self):
                logging.info("Verify_Cisco_ISE_Endpoint_Notification with Networkview STARTS_WITH_Negative")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                ref1=response[3]
                print("ref1",ref1)
                data = {"event_type":"DHCP_LEASES","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "REGEX","op1": "NETWORK_VIEW","op1_type": "FIELD","op2": "^aef","op2_type": "STRING"},{"op": "ENDLIST"}],"template_instance": {"template": "DHCPLease_Event"},"notification_action": "RESTAPI_TEMPLATE_INSTANCE"}
                print ("data provided :",data)
                response = ib_NIOS.wapi_request('PUT', ref= ref1,fields=json.dumps(data))
                print(response)
                logging.info("Test Case 143 Execution Completed")

        @pytest.mark.run(order=144)
        def test_144_Verify_Modified_Cisco_ISE_Endpoint_Notification_STARTS_WITH_Negative(self):
                logging.info("Verify Modified_Cisco_ISE_Endpoint_Notification STARTS_WITH_Negative")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule?_return_fields=template_instance,event_type,name,expression_list",grid_vip=config.grid_vip)
                print("response    : ",response)
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                print("response    : ",response)
		if('"name":"Test_DHCP"' in response) and ('"template":"DHCPLease_Event"' in response) and ('"op1":"NETWORK_VIEW"'in response) and ('"expression_list":"op":"AND","op1_type":"LIST","op":"REGEX","op1":"NETWORK_VIEW","op1_type":"FIELD","op2":"^aef","op2_type":"STRING","op":"ENDLIST"' in response):
                         assert True
                else:
                         assert False
                sleep(20)
		logging.info("Test Case 144 Execution Completed")

        @pytest.mark.run(order=145)
        def test_145_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
		sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 145 Execution Completed")

        @pytest.mark.run(order=146)
        def test_146_Executing_dras_command(self):
            	logging.info("Executing dras command")
            	dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
            	dras_cmd1 = os.system(dras_cmd)
                sleep(15)
                print (dras_cmd1)
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(15)
            	print(dras_cmd1)
		logging.info("Test Case 146 Execution Completed")

        @pytest.mark.run(order=147)
        def test_147_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 147 Execution Completed")

        @pytest.mark.run(order=148)
        def test_148_looking_for_Template_execution_Status_Negative(self):
		logging.info("looking_for_Templated_Execution_Status Negative")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)==0):
                    print("The template was executed successfully")
                    assert True
                else:
		    print("template was not Executed")
                    assert False
                sleep(20)
		logging.info("Test Case 148 Execution Completed")

        @pytest.mark.run(order=149)
        def test_149_Modify_Cisco_ISE_Endpoint_Notification_With_NetwotkView_ENDS_WITH(self):
                logging.info("Verify_Cisco_ISE_Endpoint_Notification with Networkview ENDS_WITH")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                ref1=response[3]
                print("ref1",ref1)
                data = {"event_type":"DHCP_LEASES","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "REGEX","op1": "NETWORK_VIEW","op1_type": "FIELD","op2": "ult$","op2_type": "STRING"},{"op": "ENDLIST"}],"template_instance": {"template": "DHCPLease_Event"},"notification_action": "RESTAPI_TEMPLATE_INSTANCE"}
                print ("data provided :",data)
                response = ib_NIOS.wapi_request('PUT', ref= ref1,fields=json.dumps(data))
                print(response)
                logging.info("Test Case 149 Execution Completed")

        @pytest.mark.run(order=150)
        def test_150_Verify_Modified_Cisco_ISE_Endpoint_Notification_ENDS_WITH(self):
                logging.info("Verify Modified_Cisco_ISE_Endpoint_Notification ENDS_WITH")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule?_return_fields=template_instance,event_type,name,expression_list",grid_vip=config.grid_vip)
                print("response    : ",response)
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                print("response    : ",response)
		if('"name":"Test_DHCP"' in response) and ('"template":"DHCPLease_Event"' in response) and ('"op1":"NETWORK_VIEW"'in response) and ('"expression_list":"op":"AND","op1_type":"LIST","op":"REGEX","op1":"NETWORK_VIEW","op1_type":"FIELD","op2":"ult$","op2_type":"STRING","op":"ENDLIST"' in response):
                         assert True
                else:
                         assert False
                sleep(20)
		logging.info("Test Case 150 Execution Completed")

        @pytest.mark.run(order=151)
        def test_151_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
		sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 151 Execution Completed")

        @pytest.mark.run(order=152)
        def test_152_Executing_dras_command(self):
            	logging.info("Executing dras command")
            	dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
            	dras_cmd1 = os.system(dras_cmd)
                sleep(15)
                print (dras_cmd1)
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(15)
            	print(dras_cmd1)
		logging.info("Test Case 152 Execution Completed")

        @pytest.mark.run(order=153)
        def test_153_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 153 Execution Completed")		

        @pytest.mark.run(order=154)
        def test_154_looking_for_Template_execution_Status(self):
		logging.info("looking_for_Templated_Execution_Status")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("The template was executed successfully")
                    assert True
                else:
		    print("template was not Executed")
                    assert False
                sleep(20)
		logging.info("Test Case 154 Execution Completed")
        
        @pytest.mark.run(order=155)
        def test_155_Modify_Cisco_ISE_Endpoint_Notification_With_NetwotkView_ENDS_WITH_Negative(self):
                logging.info("Modify_Cisco_ISE_Endpoint_Notification with Networkview ENDS_WITH_Negative")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                ref1=response[3]
                print("ref1",ref1)
                data = {"event_type":"DHCP_LEASES","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "REGEX","op1": "NETWORK_VIEW","op1_type": "FIELD","op2": "alt$","op2_type": "STRING"},{"op": "ENDLIST"}],"template_instance": {"template": "DHCPLease_Event"},"notification_action": "RESTAPI_TEMPLATE_INSTANCE"}
                print ("data provided :",data)
                response = ib_NIOS.wapi_request('PUT', ref= ref1,fields=json.dumps(data))
                print(response)
                logging.info("Test Case 155 Execution Completed")

        @pytest.mark.run(order=156)
        def test_156_Verify_Modified_Cisco_ISE_Endpoint_Notification_ENDS_WITH_Negative(self):
                logging.info("Verify Modified_Cisco_ISE_Endpoint_Notification ENDS_WITH_Negative")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule?_return_fields=template_instance,event_type,name,expression_list",grid_vip=config.grid_vip)
                print("response    : ",response)
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                print("response    : ",response)
		if('"name":"Test_DHCP"' in response) and ('"template":"DHCPLease_Event"' in response) and ('"op1":"NETWORK_VIEW"'in response) and ('"expression_list":"op":"AND","op1_type":"LIST","op":"REGEX","op1":"NETWORK_VIEW","op1_type":"FIELD","op2":"alt$","op2_type":"STRING","op":"ENDLIST"' in response):
                         assert True
                else:
                         assert False
                sleep(20)
		logging.info("Test Case 156 Execution Completed")

        @pytest.mark.run(order=157)
        def test_157_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
		sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 157 Execution Completed")

        @pytest.mark.run(order=158)
        def test_158_Executing_dras_command(self):
            	logging.info("Executing dras command")
            	dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
            	dras_cmd1 = os.system(dras_cmd)
                sleep(15)
                print(dras_cmd1)
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(15)
            	print(dras_cmd1)
		logging.info("Test Case 158 Execution Completed")

	@pytest.mark.run(order=159)
        def test_159_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 159 Execution Completed")

        @pytest.mark.run(order=160)
        def test_160_looking_for_Template_execution_Status_Negative(self):
		logging.info("looking_for_Templated_Execution_Status Negative")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)==0):
                    print("The template was executed successfully")
                    assert True
                else:
		    print("template was not Executed")
                    assert False
                sleep(20)
		logging.info("Test Case 160 Execution Completed")

        @pytest.mark.run(order=161)
        def test_161_Modify_Cisco_ISE_Endpoint_Notification_With_NetwotkView_EQUALS_Fixed_Address(self):
                logging.info("Modify_Cisco_ISE_Endpoint_Notification with Networkview EQUALS_Fixed_Address")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                ref1=response[3]
                print("ref1",ref1)
                data = {"event_type":"DHCP_LEASES","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "DHCP_IP_ADDRESS","op1_type": "FIELD","op2": "10.36.0.13","op2_type": "STRING"},{"op": "ENDLIST"}],"template_instance": {"template": "DHCPLease_Event"},"notification_action": "RESTAPI_TEMPLATE_INSTANCE"}
                print ("data provided :",data)
                response = ib_NIOS.wapi_request('PUT', ref= ref1,fields=json.dumps(data))
                print(response)
                logging.info("Test Case 161 Execution Completed")

        @pytest.mark.run(order=162)
        def test_162_Verify_Modified_Cisco_ISE_Endpoint_Notification_EQUALS_Fixed_Address(self):
                logging.info("Verify Modified_Cisco_ISE_Endpoint_Notification EQUALS_Fixed_Address")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule?_return_fields=template_instance,event_type,name,expression_list",grid_vip=config.grid_vip)
                print("response    : ",response)
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                print("response    : ",response)
		if('"name":"Test_DHCP"' in response) and ('"template":"DHCPLease_Event"' in response) and ('"expression_list":"op":"AND","op1_type":"LIST","op":"EQ","op1":"DHCP_IP_ADDRESS","op1_type":"FIELD","op2":"10.36.0.13","op2_type":"STRING","op":"ENDLIST"'in response):
                         assert True
                else:
                         assert False
                sleep(10)
		logging.info("Test Case 162 Execution Completed")

        @pytest.mark.run(order=163)
        def test_163_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
		sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 163 Execution Completed")

        @pytest.mark.run(order=164)
        def test_164_Executing_dras_command(self):
            	logging.info("Executing dras command")
            	dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1 -a aa:bb:cc:dd:ee:ff'
           	dras_cmd1 = os.system(dras_cmd)
                sleep(15)
                print (dras_cmd1)
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1 -a aa:bb:cc:dd:ee:ff'
                dras_cmd1 = os.system(dras_cmd)
                sleep(15)
            	print(dras_cmd1)
		logging.info("Test Case 164 Execution Completed")

        @pytest.mark.run(order=165)
        def test_165_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 165 Execution Completed")

        @pytest.mark.run(order=166)
        def test_166_looking_for_Template_execution_Status(self):
		logging.info("looking_for_Templated_Execution_Status")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("The template was executed successfully")
                    assert True
                else:
                    print("template was not Executed")
		    assert False
                sleep(20)
		logging.info("Test Case 166 Execution Completed")

        @pytest.mark.run(order=167)
        def test_167_Modify_Cisco_ISE_Endpoint_Notification_With_NetwotkView_EQUALS_Fixed_Address_Negative(self):
                logging.info("Modify_Cisco_ISE_Endpoint_Notification with Networkview Fixed_Address_Negative")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                ref1=response[3]
                print("ref1",ref1)
                data = {"event_type":"DHCP_LEASES","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "DHCP_IP_ADDRESS","op1_type": "FIELD","op2": "10.36.0.13","op2_type": "STRING"},{"op": "ENDLIST"}],"template_instance": {"template": "DHCPLease_Event"},"notification_action": "RESTAPI_TEMPLATE_INSTANCE"}
                print ("data provided :",data)
                response = ib_NIOS.wapi_request('PUT', ref= ref1,fields=json.dumps(data))
                print(response)
                logging.info("Test Case 167 Execution Completed")

        @pytest.mark.run(order=168)
        def test_168_Verify_Modified_Cisco_ISE_Endpoint_Notification_Fixed_Address_Negative(self):
                logging.info("Verify Modified_Cisco_ISE_Endpoint_Notification Fixed_Address_Negative")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule?_return_fields=template_instance,event_type,name,expression_list",grid_vip=config.grid_vip)
                print("response    : ",response)
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                print("response    : ",response)
		if('"name":"Test_DHCP"' in response) and ('"template":"DHCPLease_Event"' in response) and ('"op1":"DHCP_IP_ADDRESS"'in response) and ('"expression_list":"op":"AND","op1_type":"LIST","op":"EQ","op1":"DHCP_IP_ADDRESS","op1_type":"FIELD","op2":"10.36.0.13","op2_type":"STRING","op":"ENDLIST"' in response):
                         assert True
                else:
                         assert False
                sleep(10)
		logging.info("Test Case 168 Execution Completed")

        @pytest.mark.run(order=169)
        def test_169_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
		sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(10)
		logging.info("Test Case 169 Execution Completed")

        @pytest.mark.run(order=170)
        def test_170_Executing_dras_command(self):
            	logging.info("Executing dras command")
            	dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
            	dras_cmd1 = os.system(dras_cmd)
                sleep(10)
                print (dras_cmd1)
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(10)
            	print(dras_cmd1)
		logging.info("Test Case 170 Execution Completed")

        @pytest.mark.run(order=171)
        def test_171_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 171 Execution Completed")

        @pytest.mark.run(order=172)
        def test_172_looking_for_Template_execution_Status_Negative(self):
		logging.info("looking_for_Templated_Execution_Status Negative")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)==0):
                    print("The template was executed successfully")
                    assert True
                else:
		    print("template was not Executed")
                    assert False
                sleep(20)
		logging.info("Test Case 172 Execution Completed")

        @pytest.mark.run(order=173)
        def test_173_Modify_Cisco_ISE_Endpoint_Notification_With_NetwotkView_Range(self):
                logging.info("Modify_Cisco_ISE_Endpoint_Notification with Networkview Range")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                ref1=response[3]
                print("ref1",ref1)
                data = {"event_type":"DHCP_LEASES","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "MATCH_RANGE","op1": "DHCP_IP_ADDRESS","op1_type": "FIELD","op2": "10.36.0.1-10.36.0.100","op2_type": "STRING"},{"op": "ENDLIST"}],"template_instance": {"template": "DHCPLease_Event"},"notification_action": "RESTAPI_TEMPLATE_INSTANCE"}
                print ("data provided :",data)
                response = ib_NIOS.wapi_request('PUT', ref= ref1,fields=json.dumps(data))
                print(response)
                logging.info("Test Case 173 Execution Completed")

        @pytest.mark.run(order=174)
        def test_174_Verify_Modified_Cisco_ISE_Endpoint_Notification_Range(self):
                logging.info("Verify Modified_Cisco_ISE_Endpoint_Notification_Range")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule?_return_fields=template_instance,event_type,name,expression_list",grid_vip=config.grid_vip)
                print("response    : ",response)
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                print("response    : ",response)
		if('"name":"Test_DHCP"' in response) and ('"template":"DHCPLease_Event"' in response) and ('"op":"MATCH_RANGE"'in response) and ('"expression_list":"op":"AND","op1_type":"LIST","op":"MATCH_RANGE","op1":"DHCP_IP_ADDRESS","op1_type":"FIELD","op2":"10.36.0.1-10.36.0.100","op2_type":"STRING","op":"ENDLIST"' in response):
                         assert True
                else:
                         assert False
                sleep(20)
		logging.info("Test Case 174 Execution Completed")
		
        @pytest.mark.run(order=175)
        def test_175_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
		sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 175 Execution Completed")

        @pytest.mark.run(order=176)
        def test_176_Executing_dras_command(self):
                logging.info("Executing dras command")
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(15)
                print (dras_cmd1)
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(15)
                print(dras_cmd1)
		logging.info("Test Case 176 Execution Completed")

        @pytest.mark.run(order=177)
        def test_177_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 177 Execution Completed")

        @pytest.mark.run(order=178)
        def test_178_looking_for_Template_execution_Status(self):
		logging.info("looking_for_Templated_Execution_Status")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("The template was executed successfully")
                    assert True
                else:
		    print("template was not Executed")
                    assert False
                sleep(20)
		logging.info("Test Case 178 Execution Completed")

        @pytest.mark.run(order=179)
        def test_179_Modify_Cisco_ISE_Endpoint_Notification_With_NetwotkView_Range_Negative(self):
                logging.info("Modify_Cisco_ISE_Endpoint_Notification with Networkview Range_Negative")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                ref1=response[3]
                print("ref1",ref1)
                data = {"event_type":"DHCP_LEASES","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "MATCH_RANGE","op1": "DHCP_IP_ADDRESS","op1_type": "FIELD","op2": "10.36.0.200-10.36.0.255","op2_type": "STRING"},{"op": "ENDLIST"}],"template_instance": {"template": "DHCPLease_Event"},"notification_action": "RESTAPI_TEMPLATE_INSTANCE"}
                print ("data provided :",data)
                response = ib_NIOS.wapi_request('PUT', ref= ref1,fields=json.dumps(data))
                print(response)
                logging.info("Test Case 179 Execution Completed")

        @pytest.mark.run(order=180)
        def test_180_Verify_Modified_Cisco_ISE_Endpoint_Notification_Range_Negative(self):
                logging.info("Verify Modified_Cisco_ISE_Endpoint_Notification Range_Negative")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule?_return_fields=template_instance,event_type,name,expression_list",grid_vip=config.grid_vip)
                print("response    : ",response)
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                print("response    : ",response)
		if('"name":"Test_DHCP"' in response) and ('"template":"DHCPLease_Event"' in response) and ('"op":"MATCH_RANGE"'in response) and ('"expression_list":"op":"AND","op1_type":"LIST","op":"MATCH_RANGE","op1":"DHCP_IP_ADDRESS","op1_type":"FIELD","op2":"10.36.0.200-10.36.0.255","op2_type":"STRING","op":"ENDLIST"' in response):
                         assert True
                else:
                         assert False
                sleep(20)
		logging.info("Test Case 180 Execution Completed")

        @pytest.mark.run(order=181)
        def test_181_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
		sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 181 Execution Completed")

        @pytest.mark.run(order=182)
        def test_182_Executing_dras_command(self):
            	logging.info("Executing dras command")
            	dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
          	dras_cmd1 = os.system(dras_cmd)
                sleep(15)
                print (dras_cmd1)
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(15)
            	print(dras_cmd1)    
		logging.info("Test Case 182 Execution Completed")

        @pytest.mark.run(order=183)
        def test_183_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 183 Execution Completed")

        @pytest.mark.run(order=184)
        def test_184_looking_for_Template_execution_Status_Negative(self):
		logging.info("looking_for_Templated_Execution_Status Negative")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)==0):
                    print("The template was executed successfully")
                    assert True
                else:
                    assert False
                sleep(20)
		logging.info("Test Case 184 Execution Completed")

        @pytest.mark.run(order=185)
        def test_185_Modify_Cisco_ISE_Endpoint_Notification_With_NetwotkView_MATCH_CIDR(self):
                logging.info("Modify_Cisco_ISE_Endpoint_Notification with Networkview MATCH_CIDR")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                ref1=response[3]
                print("ref1",ref1)
                data = {"event_type":"DHCP_LEASES","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "MATCH_CIDR","op1": "DHCP_IP_ADDRESS","op1_type": "FIELD","op2": "10.36.0.0/16","op2_type": "STRING"},{"op": "ENDLIST"}],"template_instance": {"template": "DHCPLease_Event"},"notification_action": "RESTAPI_TEMPLATE_INSTANCE"}
                print ("data provided :",data)
                response = ib_NIOS.wapi_request('PUT', ref= ref1,fields=json.dumps(data))
                print(response)
                logging.info("Test Case 185 Execution Completed")
		
        @pytest.mark.run(order=186)
        def test_186_Verify_Modified_Cisco_ISE_Endpoint_Notification_MATCH_CIDR(self):
                logging.info("Verify Modified_Cisco_ISE_Endpoint_Notification MATCH_CIDR")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule?_return_fields=template_instance,event_type,name,expression_list",grid_vip=config.grid_vip)
                print("response    : ",response)
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                print("response    : ",response)
		if('"name":"Test_DHCP"' in response) and ('"template":"DHCPLease_Event"' in response) and ('"op":"MATCH_CIDR"'in response) and ('"expression_list":"op":"AND","op1_type":"LIST","op":"MATCH_CIDR","op1":"DHCP_IP_ADDRESS","op1_type":"FIELD","op2":"10.36.0.0/16","op2_type":"STRING","op":"ENDLIST"' in response):
                         assert True
                else:
                         assert False
                sleep(20)
		logging.info("Test Case 186 Execution Completed")

        @pytest.mark.run(order=187)
        def test_187_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
		sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 187 Execution Completed")

        @pytest.mark.run(order=188)
        def test_188_Executing_dras_command(self):
            	logging.info("Executing dras command")
            	dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
            	dras_cmd1 = os.system(dras_cmd)
                sleep(15)
                print (dras_cmd1)
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(15)
            	print(dras_cmd1)
		logging.info("Test Case 188 Execution Completed")

        @pytest.mark.run(order=189)
        def test_189_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 189 Execution Completed")

        @pytest.mark.run(order=190)
        def test_190_looking_for_Template_execution_Status(self):
		logging.info("looking_for_Templated_Execution_Status")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("The template was executed successfully")
                    assert True
                else:
		    print("template was not Executed")
                    assert False
                sleep(20)
		logging.info("Test Case 190 Execution Completed")

        @pytest.mark.run(order=191)
        def test_191_Modify_Cisco_ISE_Endpoint_Notification_With_NetwotkView_MATCH_CIDR_Negative(self):
                logging.info("Modify_Cisco_ISE_Endpoint_Notification with Networkview MATCH_CIDR_Negative")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                ref1=response[3]
                print("ref1",ref1)
                data = {"event_type":"DHCP_LEASES","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "MATCH_CIDR","op1": "DHCP_IP_ADDRESS","op1_type": "FIELD","op2": "10.32.0.0/16","op2_type": "STRING"},{"op": "ENDLIST"}],"template_instance": {"template": "DHCPLease_Event"},"notification_action": "RESTAPI_TEMPLATE_INSTANCE"}
                print ("data provided :",data)
                response = ib_NIOS.wapi_request('PUT', ref= ref1,fields=json.dumps(data))
                print(response)
                logging.info("Test Case 191 Execution Completed")

        @pytest.mark.run(order=192)
        def test_192_Verify_Modified_Cisco_ISE_Endpoint_Notification_MATCH_CIDR_Negative(self):
                logging.info("Verify Modified_Cisco_ISE_Endpoint_Notification MATCH_CIDR_Negative")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule?_return_fields=template_instance,event_type,name,expression_list",grid_vip=config.grid_vip)
                print("response    : ",response)
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                print("response    : ",response)
		if('"name":"Test_DHCP"' in response) and ('"template":"DHCPLease_Event"' in response) and ('"op":"MATCH_CIDR"'in response) and ('"expression_list":"op":"AND","op1_type":"LIST","op":"MATCH_CIDR","op1":"DHCP_IP_ADDRESS","op1_type":"FIELD","op2":"10.32.0.0/16","op2_type":"STRING","op":"ENDLIST"' in response):
                         assert True
                else:
                         assert False
                sleep(20)
		logging.info("Test Case 192 Execution Completed")

        @pytest.mark.run(order=193)
        def test_193_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
		sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 193 Execution Completed")

        @pytest.mark.run(order=194)
        def test_194_Executing_dras_command(self):
            	logging.info("Executing dras command")
            	dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
            	dras_cmd1 = os.system(dras_cmd)
                sleep(15)
                print(dras_cmd1)
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(15)
            	print(dras_cmd1)
		logging.info("Test Case 194 Execution Completed")

        @pytest.mark.run(order=195)
        def test_195_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 195 Execution Completed")

        @pytest.mark.run(order=196)
        def test_196_looking_for_Template_execution_Status_Negative(self):
		logging.info("looking_for_Templated_Execution_Status Negative")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)==0):
                    print("The template was executed successfully")
                    assert True
                else:
        	    print("template was not Executed")
	            assert False
                sleep(20)
		logging.info("Test Case 196 Execution Completed")

	@pytest.mark.run(order=197)
        def test_197_Update_Subscribe_and_Publish_Settings_for_Cisco_ISE_endpoint(self):
                logging.info("Update_Subscribe_and_Publish_Settings_for_Cisco_ISE_endpoint")
                response = ib_NIOS.wapi_request('GET', object_type="pxgrid:endpoint")
                print response
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                ref1=response[3]
                print("ref1",ref1)
                logging.info(response)
                data= {"address":config.cisco_ise_server_ip ,"comment": "Add cisco ISE endpoint","log_level": "DEBUG","name": "cisco_ise_endpoint2","network_view": "default","outbound_member_type": "GM","outbound_members": [],"publish_settings": {"enabled_attributes":["IPADDRESS","CLIENT_ID"]}, "subscribe_settings": {"enabled_attributes": ["DOMAINNAME","VLAN"],"mapped_ea_attributes": []},"template_instance": {"parameters": [],"template": "PxgrdiSessionTemplate"},"timeout": 30,"vendor_identifier": "pxgrid","wapi_user_name": "admin","wapi_user_password":"infoblox"}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1, fields=json.dumps(data))
                print response
		sleep(30)
                assert re.search(r'cisco_ise_endpoint2',response)
                print("Test Case 197 Execution Completed")

	@pytest.mark.run(order=198)
        def test_198_Verify_Updated_CiscoISE_Endpoint_Validation(self):
                logging.info("Verify Updated CiscoISE Endpoint Validation")
                response = ib_NIOS.wapi_request('GET', object_type="pxgrid:endpoint?_return_fields=subscribe_settings,publish_settings")
                print response
		print("respose",type(response))
		response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
		print response
                print("respose",type(response))
                logging.info(response)
		if('"publish_settings":"enabled_attributes":"CLIENT_ID","IPADDRESS"' in response) and ('"subscribe_settings":"enabled_attributes":"DOMAINNAME"' in response):
                         assert True
                else:
                         assert False
                print("Test case 198 Execution Completed")
                sleep(20)

	@pytest.mark.run(order=199)
        def test_199_Modify_Cisco_ISE_Endpoint_DHCP_Notification_with_Override(self):
                logging.info("Modify_Cisco_ISE_Endpoint_Notification_with_Override")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                ref1=response[3]
                print("ref1",ref1)
                data = {"event_type":"DHCP_LEASES","use_publish_settings":True,"publish_settings":{"enabled_attributes":["CLIENT_ID","IPADDRESS","LEASE_END_TIME","LEASE_STATE","LEASE_START_TIME"]},"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "DHCP_LEASE_STATE","op1_type": "FIELD","op2": "DHCP_LEASE_STATE_ACTIVE","op2_type": "STRING"},{"op": "ENDLIST"}],"template_instance": {"template": "DHCPLease_Event"},"notification_action": "RESTAPI_TEMPLATE_INSTANCE"}
                print ("data provided :",data)
                response = ib_NIOS.wapi_request('PUT', ref= ref1,fields=json.dumps(data))
		sleep(10)
                print(response)
                logging.info("Test Case 199 Execution Completed")

        @pytest.mark.run(order=200)
        def test_200_Verify__Updated_Cisco_ISE_Endpoint_DHCP_Notification_with_Override(self):
                logging.info("Verify_updated_Cisco_ISE_Endpoint_DHCP_Notification with Override")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule?_return_fields=template_instance,event_type,name,publish_settings",grid_vip=config.grid_vip)
                print("response    : ",response)
		if('"name": "Test_DHCP"' in response) and ('"template": "DHCPLease_Event"' in response) and ('"event_type": "DHCP_LEASES"'in response) and ('"CLIENT_ID"' in response) and ('"IPADDRESS"' in response) and ('"LEASE_END_TIME"' in response) and ('"LEASE_STATE"' in response) and ('"LEASE_START_TIME"' in response):
                         assert True
                else:
                         assert False		
                sleep(10)
                logging.info("Test Case 200 Execution Completed")
		
        @pytest.mark.run(order=201)
        def test_201_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
		sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 201 Execution Completed")

	@pytest.mark.run(order=202)
        def test_202_Executing_dras_command(self):
                logging.info("Executing dras command")
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(15)
                print(dras_cmd1)
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(15)
                print(dras_cmd1)
		dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(15)
                print(dras_cmd1)
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(15)
                print(dras_cmd1)
		logging.info("Test Case 202 Execution Completed")

        @pytest.mark.run(order=203)
        def test_203_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 203 Execution Completed")

        @pytest.mark.run(order=204)
        def test_204_looking_for_Template_execution_Status(self):
		logging.info("looking_for_Templated_Execution_Status")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("The template was executed successfully")
                    assert True
                else:
		    print("template was not Executed")
                    assert False
                sleep(20)
		logging.info("Test Case 204 Execution Completed")	

	@pytest.mark.run(order=205)
        def test_205_Modify_Cisco_ISE_Endpoint_DHCP_Notification_with_Inherit(self):
                logging.info("Modify_Cisco_ISE_Endpoint_Notification with Inherit")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                ref1=response[3]
                print("ref1",ref1)
                data = {"event_type":"DHCP_LEASES","use_publish_settings":False,"publish_settings":{"enabled_attributes":["CLIENT_ID","IPADDRESS","LEASE_END_TIME","LEASE_STATE","LEASE_START_TIME"]},"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "DHCP_LEASE_STATE","op1_type": "FIELD","op2": "DHCP_LEASE_STATE_ACTIVE","op2_type": "STRING"},{"op": "ENDLIST"}],"template_instance": {"template": "DHCPLease_Event"},"notification_action": "RESTAPI_TEMPLATE_INSTANCE"}
                print ("data provided :",data)
                response = ib_NIOS.wapi_request('PUT', ref= ref1,fields=json.dumps(data))
                sleep(10)
		print(response)
                logging.info("Test Case 205 Execution Completed")

        @pytest.mark.run(order=206)
        def test_206_Verify_Cisco_ISE_Endpoint_DHCP_Notification_with_Inherit(self):
                logging.info("Verify_Cisco_ISE_Endpoint_DHCP_Notification with Inherit")
		response = ib_NIOS.wapi_request('GET',object_type="notification:rule?_return_fields=template_instance,event_type,name,expression_list",grid_vip=config.grid_vip)
                print("response    : ",response)
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                print("response    : ",response)
		if('"name":"Test_DHCP"' in response) and ('"template":"DHCPLease_Event"' in response) and ('"event_type":"DHCP_LEASES"'in response) and ('"expression_list":"op":"AND","op1_type":"LIST","op":"EQ","op1":"DHCP_LEASE_STATE","op1_type":"FIELD","op2":"DHCP_LEASE_STATE_ACTIVE","op2_type":"STRING","op":"ENDLIST"' in response):
                         assert True
                else:
                         assert False
                sleep(10)
                logging.info("Test Case 206 Execution Completed")
		
        @pytest.mark.run(order=207)
        def test_207_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
		sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 207 Execution Completed")

	@pytest.mark.run(order=208)
        def test_208_Executing_dras_command(self):
                logging.info("Executing dras command")
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(15)
                print (dras_cmd1)
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(15)
                print(dras_cmd1)
		logging.info("Test Case 208 Execution Completed")

        @pytest.mark.run(order=209)
        def test_209_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 209 Execution Completed")

        @pytest.mark.run(order=210)
        def test_210_looking_for_Template_execution_Status(self):
		logging.info("looking_for_Templated_Execution_Status")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("The template was executed successfully")
                    assert True
                else:
		    print("template was not Executed")
                    assert False
                sleep(20)
		logging.info("Test Case 210 Execution Completed")

	@pytest.mark.run(order=211)
        def test_211_Modify_Cisco_ISE_Endpoint_IPAM_Notification_with_Override(self):
                logging.info("Modify_Cisco_ISE_Endpoint_Notification with Override")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                ref1=response[3]
                print("ref1",ref1)
                data = {"event_type":"IPAM","use_publish_settings":True,"publish_settings":{"enabled_attributes":["CLIENT_ID","IPADDRESS","LEASE_END_TIME","LEASE_STATE","LEASE_START_TIME"]},"template_instance": {"template": "IPAM_PxgridEvent"},"expression_list": [],"notification_action": "RESTAPI_TEMPLATE_INSTANCE"}
                print ("data provided :",data)
                response = ib_NIOS.wapi_request('PUT', ref= ref1,fields=json.dumps(data))
		sleep(10)
                print(response)
		logging.info("Test Case 211 Execution Completed")        
      
        @pytest.mark.run(order=212)
        def test_212_Verify_Cisco_ISE_Endpoint_IPAM_Notification_with_Override(self):
                logging.info("Verify_Cisco_ISE_Endpoint_IPAM_Notification with_Override")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule?_return_fields=template_instance,event_type,name,publish_settings",grid_vip=config.grid_vip)
                print("response    : ",response)
		if('"name": "Test_DHCP"' in response) and ('"template": "IPAM_PxgridEvent"' in response) and ('"event_type": "IPAM"'in response) and ('"CLIENT_ID"' in response) and ('"IPADDRESS"' in response) and ('"LEASE_END_TIME"' in response) and ('"LEASE_STATE"' in response) and ('"LEASE_START_TIME"' in response):
                         assert True
                else:
                         assert False
                sleep(20)
                logging.info("Test Case 212 Execution Completed")
		
	@pytest.mark.run(order=213)
        def test_213_Create_IPv4_network_default_network_view(self):
                logging.info("Create an ipv4 network default network view")
                network_data = {"network": config.network+".0/24","network_view": "default","members":[{"_struct": "dhcpmember","ipv4addr":config.grid_vip}]}
                response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(network_data), grid_vip=config.grid_vip)
                print(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Created the ipv4network in default view")
                logging.info("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 15 sec.,")
                sleep(15)
		logging.info("Test Case 213 Execution Completed")		
				
        @pytest.mark.run(order=214)
        def test_214_Verify_IPv4_network_default_network_view(self):
                logging.info("Verify an ipv4 network default network view")
                new_data =  ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
                new_data=json.loads(new_data)
		new_data = eval(json.dumps(new_data))
                print ("result of adding ipv4 network",new_data)
		print(new_data[1])
                sleep(20) #wait for 20 secs for the member to get started
                if (new_data[1]['network']==config.network+".0/24"):
                        assert True
                        print("Test Case 214 Execution Completed")
                else:
                        assert False
                        print ("Test Case 214 Execution Failed")

  	@pytest.mark.run(order=215)
        def test_215_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
		sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 215 Execution Completed")

	@pytest.mark.run(order=216)
        def test_216_create_fixed_address(self):
                logging.info("Create an ipv4 fixed Address")
                data = { "ipv4addr": config.network+".2","mac": "aa:bb:cc:dd:ee:ff","network_view": "default"}
                response = ib_NIOS.wapi_request('POST', object_type="fixedaddress", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                print("Created the fixed address ")
                logging.info("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 20 sec.,")
                sleep(30) 
                print("Test Case 216 Execution Completed")
	
        @pytest.mark.run(order=217)
        def test_217_Verify_Fixed_Address(self):
                logging.info("Verify Fixed Address")
                response = ib_NIOS.wapi_request('GET',object_type="fixedaddress?_return_fields=mac,ipv4addr",grid_vip=config.grid_vip)
                print("response    : ",response)
		if('"ipv4addr": "'+config.network+'.2"'in response) and ('"mac": "aa:bb:cc:dd:ee:ff"' in response):
                         assert True
                else:
                         assert False
                sleep(20)
		logging.info("Test Case 217 Execution Completed")

        @pytest.mark.run(order=218)
        def test_218_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 218 Execution Completed")

        @pytest.mark.run(order=219)
        def test_219_looking_for_Template_execution_Status(self):
                logging.info("looking_for_Templated_Execution_Status")
		check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("The template was executed successfully")
                    assert True
                else:
                    print("template was not Executed")
		    assert False
                sleep(20)
		logging.info("Test Case 219 Execution Completed")	

	@pytest.mark.run(order=220)
        def test_220_Modify_Cisco_ISE_Endpoint_IPAM_Notification_With_Inherit(self):
                logging.info("Modify_Cisco_ISE_Endpoint_Notification with Inherit")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                ref1=response[3]
                print("ref1",ref1)
		data = {"event_type":"IPAM","use_publish_settings":False,"publish_settings":{"enabled_attributes":["CLIENT_ID","IPADDRESS","LEASE_END_TIME","LEASE_STATE","LEASE_START_TIME"]},"template_instance": {"template": "IPAM_PxgridEvent"},"expression_list": [],"notification_action": "RESTAPI_TEMPLATE_INSTANCE"}
                print ("data provided :",data)
                response = ib_NIOS.wapi_request('PUT', ref= ref1,fields=json.dumps(data))
                print(response)
                sleep(10)
                logging.info("Test Case 220 Execution Completed")

	@pytest.mark.run(order=221)
	def test_221_Verify_Cisco_ISE_Endpoint_IPAM_Notification_with_Inherit(self):
                logging.info("Verify_Cisco_ISE_Endpoint_IPAM_Notification with Inherit")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule?_return_fields=template_instance,event_type,name,publish_settings",grid_vip=config.grid_vip)
                print("response    : ",response)
		if('"name": "Test_DHCP"'in response) and ('"template": "IPAM_PxgridEvent"' in response) and ('"event_type": "IPAM"' in response):
                         assert True
                else:
                         assert False
                sleep(20)
                logging.info("Test Case 221 Execution Completed")

	@pytest.mark.run(order=222)
        def test_222_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
		sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 222 Execution Completed")

	@pytest.mark.run(order=223)
        def test_223_delete_fixed_address(self):
                logging.info("delete an fixed Address")
                get_ref = ib_NIOS.wapi_request('GET', object_type="fixedaddress")
                print(get_ref)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1
                response = ib_NIOS.wapi_request('DELETE', ref=ref1, grid_vip=config.grid_vip)
                print(response)
                print("Created the fixed address ")
                logging.info("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 20 sec.,")
                sleep(30)
                print("Test Case 223 Execution Completed")

	@pytest.mark.run(order=224)
        def test_224_Verify_Deleted_Fixed_Address(self):
                logging.info("Verify Deleted Fixed Address")
                response = ib_NIOS.wapi_request('GET',object_type="fixedaddress?_return_fields=mac,ipv4addr",grid_vip=config.grid_vip)
                print(response)
		if (config.network+".2" not in response):
                        assert True
                else:
                        assert False
                sleep(10)
		logging.info("Test Case 224 Execution Completed")

        @pytest.mark.run(order=225)
        def test_225_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 225 Execution Completed")

        @pytest.mark.run(order=226)
        def test_226_looking_for_Template_execution_Status(self):
		logging.info("looking_for_Templated_Execution_Status")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("The template was executed successfully")
                    assert True
                else:
		    print("template was not Executed")
                    assert False
                sleep(20)
		logging.info("Test Case 226 Execution Completed")	

	@pytest.mark.run(order=227)
        def test_227_Delete_Endpoint(self):
                logging.info("Delete_Endpoint")
                get_ref = ib_NIOS.wapi_request('GET', object_type="pxgrid:endpoint")
                print(get_ref)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                response = ib_NIOS.wapi_request('DELETE', object_type=ref1)
                sleep(15)
                print("Test Case 227 Execution Completed")

	@pytest.mark.run(order=228)
        def test_228_Verify_Deleted_Endpoint(self):
                logging.info("Verify Deleted_Endpoint")
                response = ib_NIOS.wapi_request('GET',object_type="pxgrid:endpoint",grid_vip=config.grid_vip)
                print(response)
                if (response=="[]"):
                        assert True
                else:
                        assert False
                sleep(10)
		logging.info("Test Case 228 Execution Completed")		

	@pytest.mark.run(order=229)
        def test_229_Verify_Cisco_ISE_Endpoint_in_Network(self):
                logging.info("Verify_Cisco_ISE_Endpoint_in_Network")
                response = ib_NIOS.wapi_request('GET',object_type="network?_return_fields=endpoint_sources",grid_vip=config.grid_vip)
                print(response)
                if ("cisco_ise_endpoint2" not in response):
                        assert True
                else:
                        assert False
                sleep(10)
		logging.info("Test Case 229 Execution Completed")	

#Test cases related to discovery Member starts from here
	@pytest.mark.run(order=230)
        def test_230_create_IPADDRESS_EA(self):
                logging.info("create_IPADDRESS_EA")
                data = {"name": "IP_ADDRESS_EXT","type": "STRING"}
                response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                print("Created the IPADDRESS_EA ")
		logging.info("Test Case 230 Execution Completed")	

	@pytest.mark.run(order=231)
        def test_231_validate_IPADDRESS_EA(self):
                logging.info("validate_IPADDRESS_EA")
                response = ib_NIOS.wapi_request('GET', object_type="extensibleattributedef?_return_fields=name",  grid_vip=config.grid_vip)
                print(response)
		if ('"name": "IP_ADDRESS_EXT"' in response):
			assert True
		else:
			assert False
                print("Validated the IPADDRESS_EA ")
		logging.info("Test Case 231 Execution Completed")

	@pytest.mark.run(order=232)
        def test_232_create_MAC_EA(self):
                logging.info("create_MAC_EA")
                data = {"name": "MAC_EXT","type": "STRING"}
                response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                print("Created the MAC_EA ")
		logging.info("Test Case 232 Execution Completed")

        @pytest.mark.run(order=233)
        def test_233_validate_MAC_EA(self):
                logging.info("validate_MAC_EA")
                response = ib_NIOS.wapi_request('GET', object_type="extensibleattributedef?_return_fields=name",  grid_vip=config.grid_vip)
                print(response)
                if ('"name": "MAC_EXT"' in response):
                        assert True
                else:
                        assert False
                print("Validated the MAC_EA ")
		logging.info("Test Case 233 Execution Completed")

	@pytest.mark.run(order=234)
        def test_234_create_ACCOUNT_SESSION_ID_EA(self):
                logging.info("create_IPADDRESS_EA")
                data = {"name": "ACCOUNT_SESSION_ID_EXTN","type": "STRING"}
                response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                print("Created the ACCOUNT_SESSION_ID_EA ")
		logging.info("Test Case 234 Execution Completed")

        @pytest.mark.run(order=235)
        def test_235_validate_ACCOUNT_SESSION_ID_EA(self):
                logging.info("validate_ACCOUNT_SESSION_ID_EA")
                response = ib_NIOS.wapi_request('GET', object_type="extensibleattributedef?_return_fields=name",  grid_vip=config.grid_vip)
                print(response)
                if ('"name": "ACCOUNT_SESSION_ID_EXTN"' in response):
                        assert True
                else:
                        assert False
                print("Validated the ACCOUNT_SESSION_ID_EA ")
		logging.info("Test Case 235 Execution Completed")

	@pytest.mark.run(order=236)
        def test_236_create_NAS_IP_ADDRESS_EA(self):
                logging.info("create_NAS_IP_ADDRESS_EA")
                data = {"name": "NAS_IP_ADDRESS_EXT","type": "STRING"}
                response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                print("Created the NAS_IP_ADDRESS_EA ")
		logging.info("Test Case 236 Execution Completed")

        @pytest.mark.run(order=237)
        def test_237_validate_NAS_IP_ADDRESS_EA(self):
                logging.info("validate_NAS_IP_ADDRESS_EA")
                response = ib_NIOS.wapi_request('GET', object_type="extensibleattributedef?_return_fields=name",  grid_vip=config.grid_vip)
                print(response)
                if ('"name": "NAS_IP_ADDRESS_EXT"' in response):
                        assert True
                else:
                        assert False
                print("Validated the NAS_IP_ADDRESS_EA ")
		logging.info("Test Case 237 Execution Completed")

	@pytest.mark.run(order=238)
        def test_238_Try_to_Add_Cisco_ISE_endpoint_with_ALL_Correct_Inputs(self):
                logging.info("Create_Cisco_ISE_Endpoint with All correct Inputs")
                dir_name="./Cisco_ISE_templates/"
                base_filename="ramesh1.cer"
                token = common_util.generate_token_from_file(dir_name,base_filename)
                print ("Token details :",token)
                data= {"address": config.cisco_ise_server_ip,"comment": "Add cisco ISE endpoint","log_level": "DEBUG","name": "cisco_ise_endpoint2","network_view": "default","outbound_member_type": "GM","outbound_members": [],"publish_settings": {"enabled_attributes":["IPADDRESS"]}, "subscribe_settings": {"enabled_attributes": ["DOMAINNAME","ENDPOINT_PROFILE","SESSION_STATE"],"mapped_ea_attributes": [{"mapped_ea": "IP_ADDRESS_EXT","name": "IP_ADDRESS"},{"mapped_ea": "MAC_EXT","name": "MAC"}]},"template_instance": {"parameters": [],"template": "PxgrdiSessionTemplate"},"timeout": 30,"vendor_identifier": "pxgrid","wapi_user_name": "admin","wapi_user_password":"infoblox","client_certificate_token":str(token)}

                response = ib_NIOS.wapi_request('POST', object_type="pxgrid:endpoint", fields=json.dumps(data))
                print response
                logging.info(response)
                sleep(50)
                assert re.search(r'cisco_ise_endpoint2',response)
                print("Test Case 238 Execution Completed")

        @pytest.mark.run(order=239)
        def test_239_CiscoISE_Endpoint_Test_Connection_Validation(self):
                logging.info("CiscoISE Endpoint Test Connection Validation")
                get_ref = ib_NIOS.wapi_request('GET', object_type="pxgrid:endpoint")
                print(get_ref)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                response = ib_NIOS.wapi_request('POST', object_type=ref1+"?_function=test_connection")
                print response
                logging.info(response)
                sleep(20)
                assert re.search(r'"result": "SUCCESS"',response)
                print("Test Case 239 Execution Completed")

	@pytest.mark.run(order=240)
        def test_240_CiscoISE_Endpoint_Validation(self):
                logging.info("CiscoISE Endpoint Validation")
                response = ib_NIOS.wapi_request('GET', object_type="pxgrid:endpoint?_return_fields=subscribe_settings,name,address")
                print response
                logging.info(response)
		if(config.cisco_ise_server_ip in response) and ('"name": "cisco_ise_endpoint2"' in response) and ('"DOMAINNAME"'in response) and ('"ENDPOINT_PROFILE"' in response) and ('"SESSION_STATE"'in response) and ('"name": "IP_ADDRESS"' in response) and ('"name": "MAC"'in response):
                        assert True
                else:
                        assert False
                print("Test case 240 Execution Completed")
                sleep(20)

	@pytest.mark.run(order=241)
        def test_241_Create_Cisco_ISE_Endpoint_DHCP_Notification(self):
                logging.info("Create_Cisco_ISE_Endpoint DHCP Notification")
                response = ib_NIOS.wapi_request('GET',object_type="pxgrid:endpoint?_return_fields=address")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                notification=response[3]
                print("notification",notification)
                data = {"name":"Test_DHCP","notification_target":notification,"event_type":"DHCP_LEASES","use_publish_settings":True,"publish_settings":{"enabled_attributes":["CLIENT_ID","FINGERPRINT","LEASE_END_TIME","LEASE_START_TIME","LEASE_STATE","IPADDRESS"]},"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "DHCP_LEASE_STATE","op1_type": "FIELD","op2": "DHCP_LEASE_STATE_ACTIVE","op2_type": "STRING"},{"op": "ENDLIST"}],"template_instance": {"template": "DHCPLease_Event"},"notification_action": "RESTAPI_TEMPLATE_INSTANCE"}
                print ("data provided :",data)
                response = ib_NIOS.wapi_request('POST', object_type="notification:rule",fields=json.dumps(data))
                print(response)
                logging.info("Restart  Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 20 sec.,")
                sleep(20)
                logging.info("Test Case 241 Execution Completed")

	@pytest.mark.run(order=242)
        def test_242_Verify_Cisco_ISE_Endpoint_DHCP_Notification(self):
                logging.info("Verify_Cisco_ISE_Endpoint_DHCP_Notification")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule?_return_fields=template_instance,event_type,name,publish_settings",grid_vip=config.grid_vip)
                print("response    : ",response)
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                print("response    : ",response)
                if('"name":"Test_DHCP"' in response) and ('"template":"DHCPLease_Event"' in response) and ('"event_type":"DHCP_LEASES"'in response) and ('"CLIENT_ID"' in response) and ('"IPADDRESS"' in response) and ('"LEASE_END_TIME"' in response) and ('"LEASE_STATE"' in response) and ('"LEASE_START_TIME"' in response):
                         assert True
                else:
                         assert False
                sleep(10)
                logging.info("Test Case 242 Execution Completed")

        @pytest.mark.run(order=243)
        def test_243_Create_IPv4_Container_with_OVERRIDE_in_defaultnetwork_view(self):
                logging.info("Create an IPv4 Container in defaultnetwork view")
                network_data = {"network":"10.0.0.0/8","use_subscribe_settings": True,"subscribe_settings": {"enabled_attributes": ["DOMAINNAME","ENDPOINT_PROFILE","SESSION_STATE","SECURITY_GROUP","SSID","USERNAME","VLAN"],"mapped_ea_attributes": [ {"mapped_ea": "MAC_EXT","name": "MAC"},{"mapped_ea": "IP_ADDRESS_EXT","name": "IP_ADDRESS"},{"mapped_ea": "NAS_IP_ADDRESS_EXT","name": "NAS_IP_ADDRESS"}]}}
                response = ib_NIOS.wapi_request('POST', object_type="networkcontainer", fields=json.dumps(network_data), grid_vip=config.grid_vip)
                print (response)
                print("Created the ipv4 container in default view")
                logging.info("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                sleep(20)
                logging.info("Wait for 20 sec.,")
		logging.info("Test Case 243 Execution Completed")

	@pytest.mark.run(order=244)
        def test_244_Verify_IPv4_Container(self):
                logging.info("Verify an ipv4 container")
                new_data =  ib_NIOS.wapi_request('GET', object_type="networkcontainer?_return_fields=subscribe_settings,network", grid_vip=config.grid_vip)
                response = eval(json.dumps(new_data))
                sleep(10)
                print(response)
                if('"network": "10.0.0.0/8"'in response) and ('"DOMAINNAME"'in response) and ('"ENDPOINT_PROFILE"' in response) and ('"SESSION_STATE"'in response) and ('"SECURITY_GROUP"'in response) and ('"SSID"' in response) and ('"USERNAME"'in response) and ('"VLAN"' in response) and ('"name": "IP_ADDRESS"' in response) and ('"name": "MAC"'in response) and ('"name": "NAS_IP_ADDRESS"'in response):
                        assert True
                        print("Test Case 244 Execution Completed")
                else:
                        assert False
                        print("Test Case 244 Execution Failed")

	@pytest.mark.run(order=245)
        def test_245_Verify_Cisco_ISE_Endpoint_in_Network(self):
                logging.info("Verify_Cisco_ISE_Endpoint_in_Network")
                response = ib_NIOS.wapi_request('GET',object_type="networkcontainer?_return_fields=endpoint_sources",grid_vip=config.grid_vip)
		print(response)
                if ("cisco_ise_endpoint2" in response):
                        assert True
                else:
                        assert False
                sleep(10)
		logging.info("Test Case 245 Execution Completed")

        @pytest.mark.run(order=246)
        def test_246_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
		sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 246 Execution Completed")

        @pytest.mark.run(order=247)
        def test_247_Executing_dras_command(self):
                logging.info("Executing dras command")
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(10)
                print (dras_cmd1)
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(10)
                print (dras_cmd1)
		logging.info("Test Case 247 Execution Completed")

	@pytest.mark.run(order=248)
        def test_248_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 248 Execution Completed")

        @pytest.mark.run(order=249)
        def test_249_looking_for_Templated_Execution_Status(self):
		logging.info("Templated Execution Status")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("The template was executed successfully")
                    assert True
                else:
		    print("template was not Executed")
                    assert False
                sleep(20)
		logging.info("Test Case 249 Execution Completed")
	
	@pytest.mark.run(order=250)
        def test_250_Modify_IPv4_Container_with_INHERIT_in_defaultnetwork_view(self):
                logging.info("Modify an IPv4 Container_with_INHERIT defaultnetwork view")
                response = ib_NIOS.wapi_request('GET',object_type="networkcontainer")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                ref1=response[3]
                print("ref1",ref1)
                network_data = {"use_subscribe_settings": False,"subscribe_settings": {"enabled_attributes": ["DOMAINNAME","ENDPOINT_PROFILE","SESSION_STATE","SECURITY_GROUP","SSID","USERNAME","VLAN"],"mapped_ea_attributes": [ {"mapped_ea": "MAC_EXT","name": "MAC"},{"mapped_ea": "IP_ADDRESS_EXT","name": "IP_ADDRESS"},{"mapped_ea": "NAS_IP_ADDRESS_EXT","name": "NAS_IP_ADDRESS"}]}}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1, fields=json.dumps(network_data), grid_vip=config.grid_vip)
                print (response)
                print("Created the ipv4 container in default view")
                logging.info("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20)
                logging.info("Wait for 20 sec.,")
		logging.info("Test Case 250 Execution Completed")        

	@pytest.mark.run(order=251)
        def test_251_Verify_Modified_IPv4_Container(self):
                logging.info("Verify Modified an ipv4 container")
                new_data =  ib_NIOS.wapi_request('GET', object_type="networkcontainer?_return_fields=subscribe_settings,network", grid_vip=config.grid_vip)
                response = eval(json.dumps(new_data))
                sleep(10)
                print(response)
                if('"network": "10.0.0.0/8"'in response) and ('"DOMAINNAME"'in response) and ('"ENDPOINT_PROFILE"' in response) and ('"SESSION_STATE"'in response) and ('"SECURITY_GROUP"'not in response) and ('"SSID"' not in response) and ('"name": "IP_ADDRESS"' in response) and ('"name": "MAC"'in response) and ('"name": "NAS_IP_ADDRESS"'not in response):
                        assert True
                        print("Test Case 251 Execution Completed")
                else:
                        assert False
                        print("Test Case 251 Execution Failed")

	@pytest.mark.run(order=252)
        def test_252_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
		sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 252 Execution Completed")

        @pytest.mark.run(order=253)
        def test_253_Executing_dras_command(self):
                logging.info("Executing dras command")
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(10)
                print(dras_cmd1)
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(10)
                print(dras_cmd1)
		logging.info("Test Case 253 Execution Completed")

        @pytest.mark.run(order=254)
        def test_254_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 254 Execution Completed")

	@pytest.mark.run(order=255)
        def test_255_looking_For_Template_Execution_Status(self):
                logging.info("looking_for_Templated_Execution_Status")
		check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("The template was executed successfully")
                    assert True
                else:
		    print("template was not Executed")
                    assert False
                sleep(20)
		logging.info("Test Case 255 Execution Completed")	

	@pytest.mark.run(order=256)
        def test_256_Modify_IPv4network_with_OVERRIDE_in_defaultnetwork_view(self):
                logging.info("Modify IPV4 network with_OVERRIDE_with_OVERRIDE in defaultnetwork view")
                response = ib_NIOS.wapi_request('GET',object_type="network")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[3])
                response=str(response[3])
                response=response.split('\"')
                print(response)
                ref1=response[3]
                print("ref1",ref1)
                network_data = {"use_subscribe_settings": True,"subscribe_settings": {"enabled_attributes": ["DOMAINNAME","ENDPOINT_PROFILE","SESSION_STATE","SECURITY_GROUP","SSID","USERNAME","VLAN"],"mapped_ea_attributes": [ {"mapped_ea": "MAC_EXT","name": "MAC"},{"mapped_ea": "IP_ADDRESS_EXT","name": "IP_ADDRESS"},{"mapped_ea": "NAS_IP_ADDRESS_EXT","name": "NAS_IP_ADDRESS"}]}}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1, fields=json.dumps(network_data), grid_vip=config.grid_vip)
                print (response)
                logging.info("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20)
                logging.info("Wait for 20 sec.,")
		logging.info("Test Case 256 Execution Completed")

        @pytest.mark.run(order=257)
        def test_257_Verify_IPv4_Network(self):
                logging.info("Verify an ipv4 Network")
                new_data =  ib_NIOS.wapi_request('GET', object_type="network?_return_fields=subscribe_settings,network", grid_vip=config.grid_vip)
                response = eval(json.dumps(new_data))
                sleep(10)
                print(response)
                if('"network": "10.36.0.0/16"'in response) and ('"DOMAINNAME"'in response) and ('"ENDPOINT_PROFILE"' in response) and ('"SESSION_STATE"'in response) and ('"SECURITY_GROUP"'in response) and ('"SSID"' in response) and ('"USERNAME"'in response) and ('"VLAN"' in response) and ('"name": "IP_ADDRESS"' in response) and ('"name": "MAC"'in response) and ('"name": "NAS_IP_ADDRESS"'in response):
                        assert True
                        print("Test Case 257 Execution Completed")
                else:
                        assert False
                        print("Test Case 257 Execution Failed")

	@pytest.mark.run(order=258)
        def test_258_Verify_Cisco_ISE_Endpoint_in_Network(self):
                logging.info("Verify_Cisco_ISE_Endpoint_in_Network")
                response = ib_NIOS.wapi_request('GET',object_type="network?_return_fields=endpoint_sources",grid_vip=config.grid_vip)
                print(response)
                if ("cisco_ise_endpoint2" in response):
                        assert True
                else:
                        assert False
                sleep(10)
		logging.info("Test Case 258 Execution Completed")

	@pytest.mark.run(order=259)
        def test_259_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
		sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 259 Execution Completed")

        @pytest.mark.run(order=260)
        def test_260_Executing_dras_command(self):
                logging.info("Executing dras command")
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(10)
                print (dras_cmd1)
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(10)
                print (dras_cmd1)
		logging.info("Test Case 260 Execution Completed")

        @pytest.mark.run(order=261)
        def test_261_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 261 Execution Completed")

	@pytest.mark.run(order=262)
        def test_262_looking_for_Template_Execution_Status(self):
                logging.info("looking_for_Templated_Execution_Status")
		check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("The template was executed successfully")
                    assert True
                else:
		    print("template was not Executed")
                    assert False
                sleep(20)
		logging.info("Test Case 262 Execution Completed")
	
	@pytest.mark.run(order=263)
        def test_263_Modify_IPv4_Network_with_INHERIT_in_defaultnetwork_view(self):
                logging.info("Modify an IPv4 Network_with_INHERIT in defaultnetwork view")
                response = ib_NIOS.wapi_request('GET',object_type="network")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[3])
                response=str(response[3])
                response=response.split('\"')
                print(response)
                ref1=response[3]
                print("ref1",ref1)
                network_data = {"use_subscribe_settings": False,"subscribe_settings": {"enabled_attributes": ["DOMAINNAME","ENDPOINT_PROFILE","SESSION_STATE","SECURITY_GROUP","SSID","USERNAME","VLAN"],"mapped_ea_attributes": [ {"mapped_ea": "MAC_EXT","name": "MAC"},{"mapped_ea": "IP_ADDRESS_EXT","name": "IP_ADDRESS"},{"mapped_ea": "NAS_IP_ADDRESS_EXT","name": "NAS_IP_ADDRESS"}]}}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1, fields=json.dumps(network_data), grid_vip=config.grid_vip)
                print (response)
                print("Created the ipv4 container in default view")
                logging.info("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20)
                logging.info("Wait for 20 sec.,")
		logging.info("Test Case 263 Execution Completed")

        @pytest.mark.run(order=264)
        def test_264_Verify_IPv4_Network(self):
                logging.info("Verify an ipv4 Network")
                new_data =  ib_NIOS.wapi_request('GET', object_type="network?_return_fields=subscribe_settings,network", grid_vip=config.grid_vip)
                response = eval(json.dumps(new_data))
                sleep(10)
                print(response)
                if('"network": "10.36.0.0/16"'in response) and ('"DOMAINNAME"'in response) and ('"ENDPOINT_PROFILE"' in response) and ('"SESSION_STATE"'in response) and ('"USERNAME"' not in response) and ('"VLAN"' not in response) and ('"name": "IP_ADDRESS"' in response) and ('"name": "MAC"'in response) and ('"name": "NAS_IP_ADDRESS"' not in response):
                        assert True
                        print("Test Case 264 Execution Completed")
                else:
                        assert False
                        print("Test Case 264 Execution Failed")

	@pytest.mark.run(order=265)
        def test_265_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
		sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 265 Execution Completed")

        @pytest.mark.run(order=266)
        def test_266_Executing_dras_command(self):
                logging.info("Executing dras command")
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(10)
                print (dras_cmd1)
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(10)
                print(dras_cmd1)
		logging.info("Test Case 266 Execution Completed")

        @pytest.mark.run(order=267)
        def test_267_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 267 Execution Completed")

	@pytest.mark.run(order=268)
        def test_268_looking_for_Template_Execution_Status(self):
                logging.info("looking_for_Templated_Execution_Status")
		check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("The template was executed successfully")
                    assert True
                else:
		    print("template was not Executed")
                    assert False
                sleep(20)
		logging.info("Test Case 268 Execution Completed")
	
	@pytest.mark.run(order=269)
        def test_269_Modify_IPv4_Range_with_OVERRIDE_in_defaultnetwork_view(self):
                logging.info("Modify an IPv4 Range in defaultnetwork view")
                response = ib_NIOS.wapi_request('GET',object_type="range")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                ref1=response[3]
                print("ref1",ref1)
                network_data = {"use_subscribe_settings": True,"subscribe_settings": {"enabled_attributes": ["DOMAINNAME","ENDPOINT_PROFILE","SESSION_STATE","SECURITY_GROUP","SSID","USERNAME","VLAN"],"mapped_ea_attributes": [ {"mapped_ea": "MAC_EXT","name": "MAC"},{"mapped_ea": "IP_ADDRESS_EXT","name": "IP_ADDRESS"},{"mapped_ea": "NAS_IP_ADDRESS_EXT","name": "NAS_IP_ADDRESS"}]}}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1, fields=json.dumps(network_data), grid_vip=config.grid_vip)
                print (response)
                print("Created the ipv4 container in default view")
                logging.info("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20)
                logging.info("Wait for 20 sec.,")
		logging.info("Test Case 269 Execution Completed")

	@pytest.mark.run(order=270)
        def test_270_Verify_IPv4_Range(self):
                logging.info("Verify an ipv4 Range")
                new_data =  ib_NIOS.wapi_request('GET', object_type="range?_return_fields=subscribe_settings,end_addr,start_addr", grid_vip=config.grid_vip)
                response = eval(json.dumps(new_data))
                sleep(10)
                print(response)
                if('"start_addr": "10.36.0.1"'in response) and ('"end_addr": "10.36.0.100"'in response) and ('"DOMAINNAME"'in response) and ('"ENDPOINT_PROFILE"' in response) and ('"SESSION_STATE"'in response) and ('"SECURITY_GROUP"'in response) and ('"SSID"' in response) and ('"USERNAME"'in response) and ('"VLAN"' in response) and ('"name": "IP_ADDRESS"' in response) and ('"name": "MAC"'in response) and ('"name": "NAS_IP_ADDRESS"'in response):
                        assert True
                        print("Test Case 270 Execution Completed")
                else:
                        assert False
                        print("Test Case 270 Execution Failed")

	@pytest.mark.run(order=271)
        def test_271_Verify_Cisco_ISE_Endpoint_in_Range(self):
                logging.info("Verify_Cisco_ISE_Endpoint_in_Range")
                response = ib_NIOS.wapi_request('GET',object_type="range?_return_fields=endpoint_sources",grid_vip=config.grid_vip)
                print(response)
                if ("cisco_ise_endpoint2" in response):
                        assert True
                else:
                        assert False
                sleep(10)
		logging.info("Test Case 271 Execution Completed")

        @pytest.mark.run(order=272)
        def test_272_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
		sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 272 Execution Completed")

        @pytest.mark.run(order=273)
        def test_273_Executing_dras_command(self):
                logging.info("Executing dras command")
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(10)
                print (dras_cmd1)
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(10)
                print(dras_cmd1)
		logging.info("Test Case 273 Execution Completed")

        @pytest.mark.run(order=274)
        def test_274_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 274 Execution Completed")

	@pytest.mark.run(order=275)
        def test_275_looking_for_Template_Execution_Status(self):
	        logging.info("looking_for_Templated_Execution_Status")
        	check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("The template was executed successfully")
                    assert True
                else:
		    print("template was not Executed")
                    assert False
                sleep(20)
		logging.info("Test Case 275 Execution Completed")

        @pytest.mark.run(order=276)
        def test_276_Modify_IPv4_Range_with_INHERIT_in_defaultnetwork_view(self):
                logging.info("Modify an IPv4 Range_with_INHERIT defaultnetwork view")
                response = ib_NIOS.wapi_request('GET',object_type="range")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                ref1=response[3]
                print("ref1",ref1)
                network_data = {"use_subscribe_settings": False,"subscribe_settings": {"enabled_attributes": ["DOMAINNAME","ENDPOINT_PROFILE","SESSION_STATE","SECURITY_GROUP","SSID","USERNAME","VLAN"],"mapped_ea_attributes": [ {"mapped_ea": "MAC_EXT","name": "MAC"},{"mapped_ea": "IP_ADDRESS_EXT","name": "IP_ADDRESS"},{"mapped_ea": "NAS_IP_ADDRESS_EXT","name": "NAS_IP_ADDRESS"}]}}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1, fields=json.dumps(network_data), grid_vip=config.grid_vip)
                print (response)
                print("Created the ipv4 container in default view")
                logging.info("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20)
                logging.info("Wait for 20 sec.,")
		logging.info("Test Case 276 Execution Completed")

	@pytest.mark.run(order=277)
        def test_277_Verify_IPv4_Network_Range(self):
                logging.info("Verify an ipv4 Range")
                new_data =  ib_NIOS.wapi_request('GET', object_type="range?_return_fields=subscribe_settings,start_addr,end_addr", grid_vip=config.grid_vip)
                response = eval(json.dumps(new_data))
                sleep(10)
                print(response)
                if('"start_addr": "10.36.0.1"'in response) and ('"end_addr": "10.36.0.100"'in response) and ('"DOMAINNAME"'in response) and ('"ENDPOINT_PROFILE"' in response) and ('"SESSION_STATE"'in response) and ('"USERNAME"'not in response) and ('"VLAN"'not in response) and ('"name": "IP_ADDRESS"' in response) and ('"name": "MAC"'in response) and ('"name": "NAS_IP_ADDRESS"'not in response):
                        assert True
                        print("Test Case 277 Execution Completed")
                else:
                        assert False
                        print("Test Case 277 Execution Failed")

        @pytest.mark.run(order=278)
        def test_278_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
		sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 278 Execution Completed")

        @pytest.mark.run(order=279)
        def test_279_Executing_dras_command(self):
                logging.info("Executing dras command")
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(10)
                print (dras_cmd1)
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(10)
                print(dras_cmd1)
		logging.info("Test Case 279 Execution Completed")

	@pytest.mark.run(order=280)
        def test_280_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
		logging.info("Test Case 280 Execution Completed")

        @pytest.mark.run(order=281)
        def test_281_looking_for_Template_Execution_Status(self):
                logging.info("looking_for_Templated_Execution_Status")
		check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("The template was executed successfully")
                    assert True
                else:
		    print("template was not Executed")
                    assert False
                sleep(20)
		logging.info("Test Case 281 Execution Completed")
	
        @pytest.mark.run(order=282)
        def test_282_Delete_Endpoint(self):
                logging.info("Delete_Endpoint")
                get_ref = ib_NIOS.wapi_request('GET', object_type="pxgrid:endpoint")
                print(get_ref)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                response = ib_NIOS.wapi_request('DELETE', object_type=ref1)
                sleep(15)
                print("Test Case 282 Execution Completed")
	
        @pytest.mark.run(order=283)
        def test_283_Try_to_Add_Cisco_ISE_endpoint_with_ALL_Correct_Inputs(self):
                logging.info("Create_Cisco_ISE_Endpoint with All correct Inputs")
                dir_name="./Cisco_ISE_templates/"
                base_filename="ramesh1.cer"
                token = common_util.generate_token_from_file(dir_name,base_filename)
                print ("Token details :",token)
                data= {"address": config.cisco_ise_server_ip,"comment": "Add cisco ISE endpoint","log_level": "DEBUG","name": "cisco_ise_endpoint2","network_view": "default","outbound_member_type": "GM","outbound_members": [],"publish_settings": {"enabled_attributes":["IPADDRESS"]}, "subscribe_settings": {"enabled_attributes": ["DOMAINNAME","ENDPOINT_PROFILE","SESSION_STATE"],"mapped_ea_attributes": [{"mapped_ea": "IP_ADDRESS_EXT","name": "IP_ADDRESS"},{"mapped_ea": "MAC_EXT","name": "MAC"}]},"template_instance": {"parameters": [],"template": "PxgrdiSessionTemplate"},"timeout": 30,"vendor_identifier": "pxgrid","wapi_user_name": "admin","wapi_user_password":"infoblox","client_certificate_token":str(token)}

                response = ib_NIOS.wapi_request('POST', object_type="pxgrid:endpoint", fields=json.dumps(data))
                print response
                logging.info(response)
                sleep(50)
                assert re.search(r'cisco_ise_endpoint2',response)
                print("Test Case 283 Execution Completed")

        @pytest.mark.run(order=284)
        def test_284_CiscoISE_Endpoint_Test_Connection_Validation(self):
                logging.info("CiscoISE Endpoint Test Connection Validation")
                get_ref = ib_NIOS.wapi_request('GET', object_type="pxgrid:endpoint")
                print(get_ref)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                response = ib_NIOS.wapi_request('POST', object_type=ref1+"?_function=test_connection")
                print response
                logging.info(response)
                sleep(20)
                assert re.search(r'"result": "SUCCESS"',response)
                print("Test Case 284 Execution Completed")
	
        @pytest.mark.run(order=285)
        def test_285_Create_Cisco_ISE_Endpoint_DHCP_Notification(self):
                logging.info("Create_Cisco_ISE_Endpoint DHCP Notification")
                response = ib_NIOS.wapi_request('GET',object_type="pxgrid:endpoint?_return_fields=address")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                notification=response[3]
                print("notification",notification)
                data = {"name":"Test_DHCP","notification_target":notification,"event_type":"DHCP_LEASES","use_publish_settings":True,"publish_settings":{"enabled_attributes":["CLIENT_ID","FINGERPRINT","LEASE_END_TIME","LEASE_START_TIME","LEASE_STATE","IPADDRESS"]},"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "DHCP_LEASE_STATE","op1_type": "FIELD","op2": "DHCP_LEASE_STATE_ACTIVE","op2_type": "STRING"},{"op": "ENDLIST"}],"template_instance": {"template": "DHCPLease_Event"},"notification_action": "RESTAPI_TEMPLATE_INSTANCE"}
                print ("data provided :",data)
                response = ib_NIOS.wapi_request('POST', object_type="notification:rule",fields=json.dumps(data))
                print(response)
                logging.info("Restart  Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 20 sec.,")
                sleep(20)
                logging.info("Test Case 285 Execution Completed")

        @pytest.mark.run(order=286)
        def test_286_Verify_Cisco_ISE_Endpoint_DHCP_Notification(self):
                logging.info("Verify_Cisco_ISE_Endpoint_DHCP_Notification")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule?_return_fields=template_instance,event_type,name,publish_settings",grid_vip=config.grid_vip)
                print("response    : ",response)
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                print("response    : ",response)
                if('"name":"Test_DHCP"' in response) and ('"template":"DHCPLease_Event"' in response) and ('"event_type":"DHCP_LEASES"'in response) and ('"CLIENT_ID"' in response) and ('"IPADDRESS"' in response) and ('"LEASE_END_TIME"' in response) and ('"LEASE_STATE"' in response) and ('"LEASE_START_TIME"' in response):
                         assert True
                else:
                         assert False
                sleep(10)
                logging.info("Test Case 286 Execution Completed")

        @pytest.mark.run(order=287)
        def test_287_Verify_IPv4_Container(self):
                logging.info("Verify an ipv4 container")
                new_data =  ib_NIOS.wapi_request('GET', object_type="networkcontainer?_return_fields=subscribe_settings,network", grid_vip=config.grid_vip)
                response = eval(json.dumps(new_data))
                sleep(10)
                print(response)
                if('"network": "10.0.0.0/8"'in response) and ('"DOMAINNAME"'in response) and ('"ENDPOINT_PROFILE"' in response) and ('"SESSION_STATE"'in response) and ('"name": "IP_ADDRESS"' in response) and ('"name": "MAC"'in response):
                        assert True
                        print("Test Case 287 Execution Completed")
                else:
                        assert False
                        print("Test Case 287 Execution Failed")

        @pytest.mark.run(order=288)
        def test_288_Verify_Cisco_ISE_Endpoint_in_Network(self):
                logging.info("Verify_Cisco_ISE_Endpoint_in_Network")
                response = ib_NIOS.wapi_request('GET',object_type="networkcontainer?_return_fields=endpoint_sources",grid_vip=config.grid_vip)
                print(response)
                if ("cisco_ise_endpoint2" in response):
                        assert True
                else:
                        assert False
                sleep(10)
                logging.info("Test Case 288 Execution Completed")

        @pytest.mark.run(order=289)
        def test_289_Verify_IPv4_Network(self):
                logging.info("Verify an ipv4 Network")
                new_data =  ib_NIOS.wapi_request('GET', object_type="network?_return_fields=subscribe_settings,network", grid_vip=config.grid_vip)
                response = eval(json.dumps(new_data))
                sleep(10)
                print(response)
                if('"network": "10.36.0.0/16"'in response) and ('"DOMAINNAME"'in response) and ('"ENDPOINT_PROFILE"' in response) and ('"SESSION_STATE"'in response) and ('"name": "IP_ADDRESS"' in response) and ('"name": "MAC"'in response):
                        assert True
                        print("Test Case 289 Execution Completed")
                else:
                        assert False
                        print("Test Case 289 Execution Failed")

        @pytest.mark.run(order=290)
        def test_290_Verify_Cisco_ISE_Endpoint_in_Network(self):
                logging.info("Verify_Cisco_ISE_Endpoint_in_Network")
                response = ib_NIOS.wapi_request('GET',object_type="network?_return_fields=endpoint_sources",grid_vip=config.grid_vip)
                print(response)
                if ("cisco_ise_endpoint2" in response):
                        assert True
                else:
                        assert False
                sleep(10)
                logging.info("Test Case 290 Execution Completed")

        @pytest.mark.run(order=291)
        def test_291_Verify_IPv4_Range(self):
                logging.info("Verify an ipv4 Range")
                new_data =  ib_NIOS.wapi_request('GET', object_type="range?_return_fields=subscribe_settings,end_addr,start_addr", grid_vip=config.grid_vip)
                response = eval(json.dumps(new_data))
                sleep(10)
                print(response)
                if('"start_addr": "10.36.0.1"'in response) and ('"end_addr": "10.36.0.100"'in response) and ('"DOMAINNAME"'in response) and ('"ENDPOINT_PROFILE"' in response) and ('"SESSION_STATE"'in response) and ('"name": "IP_ADDRESS"' in response) and ('"name": "MAC"'in response):
                        assert True
                        print("Test Case 291 Execution Completed")
                else:
                        assert False
                        print("Test Case 291 Execution Failed")

        @pytest.mark.run(order=292)
        def test_292_Verify_Cisco_ISE_Endpoint_in_Range(self):
                logging.info("Verify_Cisco_ISE_Endpoint_in_Range")
                response = ib_NIOS.wapi_request('GET',object_type="range?_return_fields=endpoint_sources",grid_vip=config.grid_vip)
                print(response)
                if ("cisco_ise_endpoint2" in response):
                        assert True
                else:
                        assert False
                sleep(10)
                logging.info("Test Case 292 Execution Completed")
    
        @pytest.mark.run(order=293)
        def test_293_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
                logging.info("Test Case 293 Execution Completed")

        @pytest.mark.run(order=294)
        def test_294_Executing_dras_command(self):
                logging.info("Executing dras command")
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(10)
                print (dras_cmd1)
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(10)
                print(dras_cmd1)
                logging.info("Test Case 294 Execution Completed")

        @pytest.mark.run(order=295)
        def test_295_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
                logging.info("Test Case 295 Execution Completed")

        @pytest.mark.run(order=296)
        def test_296_looking_for_Template_Execution_Status(self):
                logging.info("looking_for_Templated_Execution_Status")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("The template was executed successfully")
                    assert True
                else:
                    print("template was not Executed")
                    assert False
                sleep(20)
                logging.info("Test Case 296 Execution Completed")
	
	@pytest.mark.run(order=297)
        def test_297_Modify_IPv4network_with_OVERRIDE_in_defaultnetwork_view(self):
                logging.info("Modify IPV4 network with_OVERRIDE_with_OVERRIDE in defaultnetwork view")
                response = ib_NIOS.wapi_request('GET',object_type="network")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[3])
                response=str(response[3])
                response=response.split('\"')
                print(response)
                ref1=response[3]
                print("ref1",ref1)
                network_data = {"use_subscribe_settings": True,"subscribe_settings": {"enabled_attributes": ["DOMAINNAME","ENDPOINT_PROFILE","SESSION_STATE","SECURITY_GROUP","SSID","USERNAME","VLAN"],"mapped_ea_attributes": [ {"mapped_ea": "MAC_EXT","name": "MAC"},{"mapped_ea": "IP_ADDRESS_EXT","name": "IP_ADDRESS"},{"mapped_ea": "NAS_IP_ADDRESS_EXT","name": "NAS_IP_ADDRESS"}]}}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1, fields=json.dumps(network_data), grid_vip=config.grid_vip)
                print (response)
                logging.info("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20)
                logging.info("Wait for 20 sec.,")
                logging.info("Test Case 297 Execution Completed")

	@pytest.mark.run(order=298)
        def test_298_Verify_IPv4_Network(self):
                logging.info("Verify an ipv4 Network")
                new_data =  ib_NIOS.wapi_request('GET', object_type="network?_return_fields=subscribe_settings,network", grid_vip=config.grid_vip)
                response = eval(json.dumps(new_data))
                sleep(10)
                print(response)
                if('"network": "10.36.0.0/16"'in response) and ('"DOMAINNAME"'in response) and ('"ENDPOINT_PROFILE"' in response) and ('"SESSION_STATE"'in response) and ('"SECURITY_GROUP"'in response) and ('"SSID"' in response) and ('"USERNAME"'in response) and ('"VLAN"' in response) and ('"name": "IP_ADDRESS"' in response) and ('"name": "MAC"'in response) and ('"name": "NAS_IP_ADDRESS"'in response):
                        assert True
                        print("Test Case 257 Execution Completed")
                else:
                        assert False
                        print("Test Case 298 Execution Failed")

        @pytest.mark.run(order=299)
        def test_299_Verify_Cisco_ISE_Endpoint_in_Network(self):
                logging.info("Verify_Cisco_ISE_Endpoint_in_Network")
                response = ib_NIOS.wapi_request('GET',object_type="network?_return_fields=endpoint_sources",grid_vip=config.grid_vip)
                print(response)
                if ("cisco_ise_endpoint2" in response):
                        assert True
                else:
                        assert False
                sleep(10)
                logging.info("Test Case 299 Execution Completed")

        @pytest.mark.run(order=300)
        def test_300_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
                logging.info("Test Case 300 Execution Completed")

	@pytest.mark.run(order=301)
        def test_301_Executing_dras_command(self):
                logging.info("Executing dras command")
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(10)
                print (dras_cmd1)
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(10)
                print (dras_cmd1)
                logging.info("Test Case 301 Execution Completed")

        @pytest.mark.run(order=302)
        def test_302_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
                logging.info("Test Case 261 Execution Completed")

        @pytest.mark.run(order=303)
        def test_303_looking_for_Template_Execution_Status(self):
                logging.info("looking_for_Templated_Execution_Status")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("The template was executed successfully")
                    assert True
                else:
                    print("template was not Executed")
                    assert False
                sleep(20)
                logging.info("Test Case 303 Execution Completed")

	@pytest.mark.run(order=304)
        def test_304_Modify_IPv4_Range_with_OVERRIDE_in_defaultnetwork_view(self):
                logging.info("Modify an IPv4 Range in defaultnetwork view")
                response = ib_NIOS.wapi_request('GET',object_type="range")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[0])
                response=str(response[0])
                response=response.split('\"')
                print(response)
                ref1=response[3]
                print("ref1",ref1)
                network_data = {"use_subscribe_settings": True,"subscribe_settings": {"enabled_attributes": ["DOMAINNAME","ENDPOINT_PROFILE","SESSION_STATE","SECURITY_GROUP","SSID","USERNAME","VLAN"],"mapped_ea_attributes": [ {"mapped_ea": "MAC_EXT","name": "MAC"},{"mapped_ea": "IP_ADDRESS_EXT","name": "IP_ADDRESS"},{"mapped_ea": "NAS_IP_ADDRESS_EXT","name": "NAS_IP_ADDRESS"}]}}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1, fields=json.dumps(network_data), grid_vip=config.grid_vip)
                print (response)
                print("Created the ipv4 container in default view")
                logging.info("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20)
                logging.info("Wait for 20 sec.,")
                logging.info("Test Case 304 Execution Completed")

	@pytest.mark.run(order=305)
        def test_305_Verify_IPv4_Range(self):
                logging.info("Verify an ipv4 Range")
                new_data =  ib_NIOS.wapi_request('GET', object_type="range?_return_fields=subscribe_settings,end_addr,start_addr", grid_vip=config.grid_vip)
                response = eval(json.dumps(new_data))
                sleep(10)
                print(response)
                if('"start_addr": "10.36.0.1"'in response) and ('"end_addr": "10.36.0.100"'in response) and ('"DOMAINNAME"'in response) and ('"ENDPOINT_PROFILE"' in response) and ('"SESSION_STATE"'in response) and ('"SECURITY_GROUP"'in response) and ('"SSID"' in response) and ('"USERNAME"'in response) and ('"VLAN"' in response) and ('"name": "IP_ADDRESS"' in response) and ('"name": "MAC"'in response) and ('"name": "NAS_IP_ADDRESS"'in response):
                        assert True
                        print("Test Case 305 Execution Completed")
                else:
                        assert False
                        print("Test Case 305 Execution Failed")

	@pytest.mark.run(order=306)
        def test_306_Verify_Cisco_ISE_Endpoint_in_Range(self):
                logging.info("Verify_Cisco_ISE_Endpoint_in_Range")
                response = ib_NIOS.wapi_request('GET',object_type="range?_return_fields=endpoint_sources",grid_vip=config.grid_vip)
                print(response)
                if ("cisco_ise_endpoint2" in response):
                        assert True
                else:
                        assert False
                sleep(10)
                logging.info("Test Case 306 Execution Completed")

        @pytest.mark.run(order=307)
        def test_307_Starting_Logs_for_Template_Execution(self):
                logging.info("Starting Logs for Template Execution")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' "> /infoblox/var/outbound/log/worker_*"'
                logs = commands.getoutput(sys_log_validation)
                log("start","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
                logging.info("Test Case 307 Execution Completed")

        @pytest.mark.run(order=308)
        def test_308_Executing_dras_command(self):
                logging.info("Executing dras command")
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(10)
                print (dras_cmd1)
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'n 1'
                dras_cmd1 = os.system(dras_cmd)
                sleep(10)
                print(dras_cmd1)
                logging.info("Test Case 308 Execution Completed")

	@pytest.mark.run(order=309)
        def test_309_Stopping_Logs_for_Template_Execution(self):
                logging.info("Stopping Logs for Template Execution")
                log("stop","/infoblox/var/outbound/log/worker_*",config.grid_vip)
                sleep(20)
                logging.info("Test Case 309 Execution Completed")

        @pytest.mark.run(order=310)
        def test_310_looking_for_Template_Execution_Status(self):
                logging.info("looking_for_Templated_Execution_Status")
                check=commands.getoutput(" grep -cw \".*The template was executed successfully\" /tmp/"+str(config.grid_vip)+"_infoblox_var_outbound_log_worker*")
                if (int(check)!=0):
                    print("The template was executed successfully")
                    assert True
                else:
                    print("template was not Executed")
                    assert False
                sleep(20)
                logging.info("Test Case 310 Execution Completed")
		

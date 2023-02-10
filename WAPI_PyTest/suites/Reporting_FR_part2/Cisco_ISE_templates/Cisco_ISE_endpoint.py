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

class Outbound_Cisco_ISE_Endpoint(unittest.TestCase):

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
		logging.info("Update Grid DNS Properties and Configure Global Forwarders Logging Categories Allow Recursion At Grid level")
		get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
		logging.info(get_ref)
		res = json.loads(get_ref)
		ref1 = json.loads(get_ref)[0]['_ref']
		print ref1

		logging.info("Modify Grid DNS Properties and Configure Global Forwarders Logging Categories Allow Recursion At Grid level")
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
                string = {"allow_recursive_query": True,"forwarders": [config.dns_forwarder]}
                print string
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="grid:dns",params="?_return_fields=allow_recursive_query,forwarders")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                if res == string:
                        assert True
                #else:
		#	assert False

                logging.info("Test Case 4 Execution Completed")
                logging.info("============================")



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
                        logging.info("found")
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
                logging.info(response)
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
                        logging.info("found")
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
                logging.info(response)
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
                logging.info(response)
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
                logging.info(response)
                print response
                logging.info(response)
                res = json.loads(response)
                string = {"error_message": "The template is not validated correctly with the schema. {u'operation': u'PX_SEND_QUARANTINE', u'name': u'IPAM event'} is not valid under any of the given schemas.","overall_status": "FAILED"}
                if res == string:
                        assert True
                else:
                        assert False
                print("Test Case 12 Execution Completed")



#Add Cisco ISE Outbound endpoint
	
        @pytest.mark.run(order=13)
        def test_013_Add_Cisco_ISE_endpoint(self):
                logging.info("Add Cisco ISE endpoint")
                data = {"address": config.cisco_ise_server_ip,"comment": "Add cisco ISE endpoint","log_level": "DEBUG","name": "cisco_ise_endpoint1","network_view": "default","outbound_member_type": "GM","outbound_members": [],"publish_settings": {"enabled_attributes":["IPADDRESS"]}, "subscribe_settings": {"enabled_attributes": ["DOMAINNAME"],"mapped_ea_attributes": []},"template_instance": {"parameters": [],"template": "PxgrdiSessionTemplate"},"timeout": 30,"vendor_identifier": "pxgrid","wapi_user_name": "admin","wapi_user_password":"infoblox","client_certificate_token": ""}
                status,response = ib_NIOS.wapi_request('POST', object_type="pxgrid:endpoint", fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "CA Certificate is required"',response)
                print("Test Case 13 Execution Completed")

	@pytest.mark.run(order=22)
        def test_022_Delete_Endpoint(self):
                logging.info("Delete_Endpoint")
                get_ref = ib_NIOS.wapi_request('GET', object_type="pxgrid:endpoint")
                print(get_ref)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                response = ib_NIOS.wapi_request('DELETE', object_type=ref1)

        @pytest.mark.run(order=14)
        def test_014_Upload_Cisco_ISE_Server_CA_Certificate(self):
                logging.info("Upload Cisco ISE Server CA Certificate")
                dir_name="./Cisco_ISE_templates/"
                base_filename="cisco_ise_server.cer"
                token = common_util.generate_token_from_file(dir_name,base_filename)
                print token
                data = {"token": token, "certificate_usage":"EAP_CA"}
                response = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=uploadcertificate")
                logging.info("Test Case 14 Execution Completed")
                sleep(60)

        @pytest.mark.run(order=15)
        def test_015_Try_to_Add_Cisco_ISE_endpoint_without_client_certificate_token_Attribute(self):
                logging.info("Try to Add Cisco ISE endpoint without client_certificate_token Attribute")
                data = {"address": config.cisco_ise_server_ip,"comment": "Add cisco ISE endpoint","log_level": "DEBUG","name": "cisco_ise_endpoint1","network_view": "default","outbound_member_type": "GM","outbound_members": [],"publish_settings": {"enabled_attributes":["IPADDRESS"]}, "subscribe_settings": {"enabled_attributes": ["DOMAINNAME"],"mapped_ea_attributes": []},"template_instance": {"parameters": [],"template": "PxgrdiSessionTemplate"},"timeout": 30,"vendor_identifier": "pxgrid","wapi_user_name": "admin","wapi_user_password":"infoblox"}
                status,response = ib_NIOS.wapi_request('POST', object_type="pxgrid:endpoint", fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "field for create missing: client_certificate_token"',response)
                print("Test Case 15 Execution Completed")

	

        @pytest.mark.run(order=16)
        def test_016_Try_to_Add_Cisco_ISE_endpoint_with_empty_client_certificate_token_value(self):
                logging.info("Try to Add Cisco ISE endpoint with Empty client_certificate_token Value")
                data = {"address": config.cisco_ise_server_ip,"comment": "Add cisco ISE endpoint","log_level": "DEBUG","name": "cisco_ise_endpoint2","network_view": "default","outbound_member_type": "GM","outbound_members": [],"publish_settings": {"enabled_attributes":["IPADDRESS"]}, "subscribe_settings": {"enabled_attributes": ["DOMAINNAME"],"mapped_ea_attributes": []},"template_instance": {"parameters": [],"template": "PxgrdiSessionTemplate"},"timeout": 30,"vendor_identifier": "pxgrid","wapi_user_name": "admin","wapi_user_password":"infoblox","client_certificate_token": " "}
                status,response = ib_NIOS.wapi_request('POST', object_type="pxgrid:endpoint", fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "Invalid token value"',response)
                print("Test Case 16 Execution Completed")


	@pytest.mark.run(order=17)
        def test_017_Configure_Global_Forwarders_Logging_Categories_Allow_Recursion_At_Grid_level(self):
                logging.info("Update Grid DNS Properties and Configure Global Forwarders Logging Categories Allow Recursion At Grid level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
		print(get_ref)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
				
		logging.info("Modify Grid Properties and Configure DNS Resolver Allow Recursion At Grid level")
                data = {"dns_resolver_setting":{"resolvers":[config.dns_resolver],"search_domains":[]}}
                response = ib_NIOS.wapi_request('PUT',ref= ref1,fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 17 Execution Completed")

	@pytest.mark.run(order=18)
        def test_018_Validate_Configured_DNS_Resolver_Logging_Grid_level(self):
                logging.info("Validate Configured DNS Resolver Logging Grid level")
                string = {"dns_resolver_setting":{"resolvers":["10.196.6.50"]}}
                print string
                get_resolver = ib_NIOS.wapi_request('GET', object_type="grid",params="?_return_fields=dns_resolver_setting")
                logging.info(get_resolver)
                res = json.loads(get_resolver)
                print res
                if res == string:
                        assert True
                #else:
                #       assert False

                logging.info("Test Case 18 Execution Completed")
                logging.info("============================")

	@pytest.mark.run(order=19)
        def test_019_Try_to_Add_Cisco_ISE_endpoint_without_subscribe_settings_Attribute(self):
                logging.info("Try_to_Add_Cisco_ISE_endpoint_without subscribe settings Attribute")
                data = {"address":config.cisco_ise_server_ip ,"comment": "Add cisco ISE endpoint","log_level": "DEBUG","name": "cisco_ise_endpoint1","outbound_member_type": "GM","outbound_members": [],"publish_settings": {"enabled_attributes":["IPADDRESS"]},"wapi_user_name": "admin","wapi_user_password":"infoblox","client_certificate_token": ""} 
		status,response = ib_NIOS.wapi_request('POST', object_type="pxgrid:endpoint", fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "field for create missing: subscribe_settings"',response)
                print("Test Case 19 Execution Completed")
				
	@pytest.mark.run(order=20)
        def test_020_Try_to_Add_Cisco_ISE_endpoint_with_wrong_subscribe_settings_Attribute(self):
                logging.info("Try_to_Add_Cisco_ISE_endpoint_with wrong subscribe settings Attribute")
                data = {"address":config.cisco_ise_server_ip ,"comment": "Add cisco ISE endpoint","log_level": "DEBUG","name": "cisco_ise_endpoint1","outbound_member_type": "GM","outbound_members": [],"publish_settings": {"enabled_attributes":["IPADDRESS"]}, "subscribe_settings": {"enabled_attributes": ["DOMAINNAM"],"mapped_ea_attributes": []},"wapi_user_name": "admin","wapi_user_password":"infoblox","client_certificate_token": ""}
		status,response = ib_NIOS.wapi_request('POST', object_type="pxgrid:endpoint", fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "Invalid value for enabled_attributes: \\"DOMAINNAM\\": Valid values are DOMAINNAME, ENDPOINT_PROFILE, SECURITY_GROUP, SESSION_STATE, SSID, USERNAME, VLAN"',response)
                print("Test Case 20 Execution Completed")

	@pytest.mark.run(order=21)
        def test_021_Try_to_Add_Cisco_ISE_endpoint_With_Wrong_Certificate(self):
                logging.info("Create_Cisco_ISE_Endpoint With Wrong Certificate")
                dir_name="./Cisco_ISE_templates/"
                base_filename="nios_client.cer"
                token = common_util.generate_token_from_file(dir_name,base_filename)
                print ("Token details :",token)
   		data= {"address": config.cisco_ise_server_ip,"comment": "Add cisco ISE endpoint","log_level": "DEBUG","name": "cisco_ise_endpoint2","network_view": "default","outbound_member_type": "GM","outbound_members": [],"publish_settings": {"enabled_attributes":["IPADDRESS"]}, "subscribe_settings": {"enabled_attributes": ["DOMAINNAME"],"mapped_ea_attributes": []},"template_instance": {"parameters": [],"template": "PxgrdiSessionTemplate"},"timeout": 30,"vendor_identifier": "pxgrid","wapi_user_name": "admin","wapi_user_password":"infoblox","client_certificate_token":str(token)}
             
                status,response = ib_NIOS.wapi_request('POST', object_type="pxgrid:endpoint", fields=json.dumps(data))
                print response
                logging.info(response)
                #assert status ==400 and re.search(r'"text": "Invalid token value"',response)
                print("Test Case 20 Execution Completed")

	@pytest.mark.run(order=22)
        def test_022_Delete_Endpoint(self):
                logging.info("Delete_Endpoint")
                get_ref = ib_NIOS.wapi_request('GET', object_type="pxgrid:endpoint")
                print(get_ref)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
		response = ib_NIOS.wapi_request('DELETE', object_type=ref1)

	@pytest.mark.run(order=23)
        def test_023_Upload_Cisco_ISE_Server_CA_Certificate(self):
                logging.info("Upload Cisco ISE Server CA Certificate")
                dir_name="./Cisco_ISE_templates/"
                base_filename="server.cer"
                token = common_util.generate_token_from_file(dir_name,base_filename)
                print token
                data = {"token": token, "certificate_usage":"EAP_CA"}
                response = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=uploadcertificate")
                logging.info("Test Case 14 Execution Completed")
                sleep(60)

	@pytest.mark.run(order=24)
        def test_024_Try_to_Add_Cisco_ISE_endpoint(self):
                logging.info("Create_Cisco_ISE_Endpoint")
                dir_name="./Cisco_ISE_templates/"
                base_filename="client.cer"
                token = common_util.generate_token_from_file(dir_name,base_filename)
                print ("Token details :",token)
                data= {"address": config.cisco_ise_server_ip,"comment": "Add cisco ISE endpoint","log_level": "DEBUG","name": "cisco_ise_endpoint2","network_view": "default","outbound_member_type": "GM","outbound_members": [],"publish_settings": {"enabled_attributes":["IPADDRESS"]}, "subscribe_settings": {"enabled_attributes": ["DOMAINNAME"],"mapped_ea_attributes": []},"template_instance": {"parameters": [],"template": "PxgrdiSessionTemplate"},"timeout": 30,"vendor_identifier": "pxgrid","wapi_user_name": "admin","wapi_user_password":"infoblox","client_certificate_token":str(token)}

                status,response = ib_NIOS.wapi_request('POST', object_type="pxgrid:endpoint", fields=json.dumps(data))
                print response
                logging.info(response)
                #assert status ==400 and re.search(r'"text": "Invalid token value"',response)
                print("Test Case 20 Execution Completed")

	@pytest.mark.run(order=25)
        def test_025_CiscoISE_Endpoint_Test_Connection_Validation(self):
                logging.info("CiscoISE Endpoint Test Connection Validation")
                get_ref = ib_NIOS.wapi_request('GET', object_type="pxgrid:endpoint")
                print(get_ref)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
				status,response = ib_NIOS.wapi_request('POST', object_type=ref1)
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"result": "SUCCESS"',response)
                print("Test Case 25 Execution Completed")	

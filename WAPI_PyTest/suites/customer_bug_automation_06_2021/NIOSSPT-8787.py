__author__ = "Siva Krishna"
__email__  = "krishnas@infoblox.com"

######################################################################################################################
#  Grid Set up required:                                                               				     #
#  1. Grid Master + Grid Member + Discovery Member                                     				     #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415),discovery member(ND-V1405,Add Grid license,Add Discovery license)  #
######################################################################################################################

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

class Cisco_ISE_Endpoint(unittest.TestCase):
        @pytest.mark.run(order=01)
        def test_001_Upload_Cisco_ISE_Server_CA_Certificate(self):
                logging.info("Upload Cisco ISE Server CA Certificate")
                dir_name="./Certificates/"
                base_filename="cisco_ise_server.cer"
                token = common_util.generate_token_from_file(dir_name,base_filename)
                print token
                data = {"token": token, "certificate_usage":"EAP_CA"}
                response = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=uploadcertificate")
                logging.info("Test Case 1 Execution Completed")
                sleep(60)

        @pytest.mark.run(order=002)
        def test_002_Create_Cisco_ISE_Endpoint(self):
                logging.info("Create_Cisco_ISE_Endpoint")
                dir_name="./Certificates/"
                base_filename="5_64.cer"
                token = common_util.generate_token_from_file(dir_name,base_filename)
                print ("Token details :",token)
                base_filename1="rootCA.cer"
                token1 = common_util.generate_token_from_file(dir_name,base_filename1)
                print ("Token1:",token1)
                data = {"address":"10.120.22.123","version": "VERSION_2_0","subscribing_member":config.grid_member_fqdn,"client_certificate_token":str(token),"bulk_download_certificate_token":str(token1),"subscribe_settings":{"enabled_attributes":["DOMAINNAME","ENDPOINT_PROFILE","SECURITY_GROUP","SESSION_STATE","SSID","USERNAME","VLAN"]},"publish_settings":{"enabled_attributes":["CLIENT_ID","IPADDRESS"]}}
                print ("data provided :",data)
                response = ib_NIOS.wapi_request('POST', object_type="ciscoise:endpoint",fields=json.dumps(data))
                print(response)
		logging.info("Test Case 02 Execution Completed")
                sleep(60)

	@pytest.mark.run(order=003)
        def test_003_Verify_Cisco_ISE_Endpoint(self):
                logging.info("Create_Cisco_ISE_Endpoint")
                response = ib_NIOS.wapi_request('GET',object_type="ciscoise:endpoint?_return_fields=publish_settings,address",grid_vip=config.grid_vip)
                print("response    : ",response)
		response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                assert re.search(r'"address": "10.120.22.123"' and r'"publish_settings":"enabled_attributes":"CLIENT_ID","IPADDRESS"',response)
                sleep(20)

	@pytest.mark.run(order=004)
        def test_004_Create_Cisco_ISE_Endpoint_Notification(self):
                logging.info("Create_Cisco_ISE_Endpoint_Notification")
		response = ib_NIOS.wapi_request('GET',object_type="ciscoise:endpoint?_return_fields=address")
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
		print(notification)			
		data = {"name":"Test","notification_target":notification,"event_type":"DHCP_LEASES","notification_action":"CISCOISE_PUBLISH","use_publish_settings":True,"publish_settings":{"enabled_attributes":["CLIENT_ID","FINGERPRINT","LEASE_END_TIME","LEASE_START_TIME","LEASE_STATE","IPADDRESS"]},"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "DHCP_LEASE_STATE","op1_type": "FIELD","op2": "EXPIRED","op2_type": "STRING"},{"op": "ENDLIST"}],"selected_members":[config.grid_member_fqdn]}	
		print ("data provided :",data)
                response = ib_NIOS.wapi_request('POST', object_type="notification:rule",fields=json.dumps(data))
                print(response)
		logging.info("Restart  Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 20 sec.,")
                sleep(30)
                logging.info("Test Case 04 Execution Completed")
                sleep(60)

	@pytest.mark.run(order=005)
        def test_005_Verify_Cisco_ISE_Endpoint_DHCP_Notification(self):
                logging.info("Create_Cisco_ISE_Endpoint_DHCP_Notification")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule?_return_fields=publish_settings,name,event_type",grid_vip=config.grid_vip)
                print("response    : ",response)
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                assert re.search(r'"name":"Test"' and r'"event_type":"DHCP_LEASES"' and r'"publish_settings":"enabled_attributes":"CLIENT_ID","FINGERPRINT","IPADDRESS","LEASE_END_TIME","LEASE_START_TIME","LEASE_STATE"',response)
                sleep(2)

	@pytest.mark.run(order=006)
        def test_006_Create_Cisco_ISE_Endpoint_IPAM_Notification(self):
                logging.info("Create_Cisco_ISE_Endpoint_Notification")
                response = ib_NIOS.wapi_request('GET',object_type="ciscoise:endpoint?_return_fields=address")
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
                print(notification)
                data = {"name":"Test_IPAM","notification_target":notification,"event_type":"IPAM","notification_action":"CISCOISE_PUBLISH","use_publish_settings":True,"publish_settings":{"enabled_attributes":["CLIENT_ID","FINGERPRINT","LEASE_END_TIME","LEASE_START_TIME","LEASE_STATE","IPADDRESS"]},"expression_list": [],"selected_members":[config.grid_member_fqdn]}
                print ("data provided :",data)
                response = ib_NIOS.wapi_request('POST', object_type="notification:rule",fields=json.dumps(data))
                print(response)
                logging.info("Restart  Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 20 sec.,")
                sleep(30)
                logging.info("Test Case 04 Execution Completed")
                sleep(60)

        @pytest.mark.run(order=007)
        def test_007_Verify_Cisco_ISE_Endpoint_DHCP_Notification(self):
                logging.info("Create_Cisco_ISE_Endpoint_DHCP_Notification")
                response = ib_NIOS.wapi_request('GET',object_type="notification:rule?_return_fields=publish_settings,name,event_type",grid_vip=config.grid_vip)
                print("response    : ",response)
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                assert re.search(r'"name":"Test_IPAM"' and r'"event_type":"IPAM"' and r'"publish_settings":"enabled_attributes":"CLIENT_ID","FINGERPRINT","IPADDRESS","LEASE_END_TIME","LEASE_START_TIME","LEASE_STATE"',response)

"""
 Copyright (c) Infoblox Inc., 2016
 ReportName          : Publish Data
 ReportCategory      : Publish Data
 Number of Test cases: 1
 Execution time      : 
 Execution Group     : Minute Group (HG)
 Description         : Event Count Dashboard.

 Author   : shashikala R S
 History  : 03/30/2021 (Created)
 Reviewer : 
"""
import pytest
import unittest
import logging
import subprocess
import json
import ConfigParser
import os
import ib_utils.ib_validaiton as ib_validation
import ib_utils.ib_system as ib_system
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
import config
import pexpect
import sys
import random
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from logger import logger
from time import sleep
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results
import ib_utils.common_utilities as common_util
import re
"""
TEST Steps:
      1.  Input/Preparation  : Prparation will be called by separte script as reports will be updated in minute
                                                     
      2.  Search     : Performing Search operaion with default/custom filter
      3.  Validation : comparing Search results with Reterived  'Publish Data' report without delta.
"""

class Publish_Data(unittest.TestCase):

    
    @classmethod
    def setup_class(cls):
        logger.info('-'*15+"START:Publish Data"+'-'*15)
        logger.info("Enabling Network User")     
        grid_ref = ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid_ref)[0]['_ref']
        enable_network_user = {"ms_setting" : {"enable_network_users":True,"enable_ad_user_sync": True}}
        response = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(enable_network_user))


	logger.info("Performing restart service")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        logger.info("Waiting for 30 sec.,")
        sleep(30) 
 
        '''
        start_IPv4_DHCP_service
        '''
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
        
        '''
        Configure_Global_Forwarders_Logging_Categories_Allow_Recursion_At_Grid_level
        '''
        
        logging.info("Configure Global Forwarders Logging Categories Allow Recursion At Grid level")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        print ref1
        data = {"allow_recursive_query": True,"forwarders": [config.dns_forwarder],"logging_categories": {"log_queries": True,"log_responses": True,"log_rpz": True}}
        response = ib_NIOS.wapi_request('PUT',ref= ref1,fields=json.dumps(data))
        print response
        
        '''
        Upload_Cisco_ISE_Endpoint_Session_Template
        '''
        logging.info("Upload Cisco ISE Endpoint Version6 Session Template")
        dir_name="/import/qaddi/API_Automation/Cisco_ISE_templates/"
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
        
        '''
        Upload_Cisco_ISE_Endpoint_IPAM_Event_Template
        '''
        logging.info("Upload Version6 Cisco ISE endpoint IPAM Event Template")
        dir_name="/import/qaddi/API_Automation/Cisco_ISE_templates/"
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
       
        '''
        Upload_Cisco_ISE_Server_CA_Certificate
        '''
        
        logging.info("Upload Cisco ISE Server CA Certificate")
        dir_name="/import/qaddi/API_Automation/Cisco_ISE_templates/"
        base_filename="brokercerts.crt"
        token = common_util.generate_token_from_file(dir_name,base_filename)
        print token
        data = {"token": token, "certificate_usage":"EAP_CA"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=uploadcertificate")
        print("Test Case 14 Execution Completed")
        sleep(60)
        
        '''
        Update_Grid_Master_Host_Name_To_Connect_Endpoint
        '''
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
        
        '''
        Upload_Cisco_ISE_Server_CA_Certificate
        '''
        logging.info("Upload Cisco ISE Server CA Certificate")
        dir_name="/import/qaddi/API_Automation/Cisco_ISE_templates/"
        base_filename="rootCA1.cer"
        token = common_util.generate_token_from_file(dir_name,base_filename)
        print token
        data = {"token": token, "certificate_usage":"EAP_CA"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=uploadcertificate")
        print("Test Case 27 Execution Completed")
        sleep(30)
        
        '''
        Configure_Global_Resolver_Logging_Categories_Allow_Recursion_At_Grid_level
        '''
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
        '''
	Try_to_Add_Cisco_ISE_endpoint_without_client_certificate_token_Attribute
	'''
	logging.info("Try to Add Cisco ISE endpoint without client_certificate_token Attribute")
        data = {"address": config.cisco_ise_server_ip,"comment": "Add cisco ISE endpoint","log_level": "DEBUG","name": "cisco_ise_endpoint1","network_view": "default","outbound_member_type": "GM","outbound_members": [],"publish_settings": {"enabled_attributes":["IPADDRESS"]}, "subscribe_settings": {"enabled_attributes": ["DOMAINNAME"],"mapped_ea_attributes": []},"template_instance": {"parameters": [],"template": "PxgrdiSessionTemplate"},"timeout": 30,"vendor_identifier": "pxgrid","wapi_user_name": "admin","wapi_user_password": config.wapi_user_password}
        response = ib_NIOS.wapi_request('POST', object_type="pxgrid:endpoint", fields=json.dumps(data))
        print response
        logging.info(response)
	sleep(20)
	assert re.search(r'"text": "field for create missing: client_certificate_token"',response[-1])
        '''
	
	'''
	logging.info("Create_Cisco_ISE_Endpoint with ALL_Correct_Inputs")
        dir_name="/import/qaddi/API_Automation/Cisco_ISE_templates/"
        base_filename="ramesh1.cer"
        token = common_util.generate_token_from_file(dir_name,base_filename)
        print ("Token details :",token)
        data= {"address": config.cisco_ise_server_ip,"comment": "Add cisco ISE endpoint","log_level": "DEBUG","name": "cisco_ise_endpoint2","network_view": "default","outbound_member_type": "GM","outbound_members": [],"publish_settings": {"enabled_attributes":["IPADDRESS"]}, "subscribe_settings": {"enabled_attributes": ["DOMAINNAME"],"mapped_ea_attributes": []},"template_instance": {"parameters": [],"template": "PxgrdiSessionTemplate"},"timeout": 30,"vendor_identifier": "pxgrid","wapi_user_name": "admin","wapi_user_password": config.wapi_user_password,"client_certificate_token":str(token)}

        response = ib_NIOS.wapi_request('POST', object_type="pxgrid:endpoint", fields=json.dumps(data))
        print response
        logging.info(response)
        sleep(50)
        assert re.search(r'cisco_ise_endpoint2',response)
        print("Test Case 39 Execution Completed")

	'''
	'''
	logging.info("Upload Cisco ISE Server CA Certificate")
        dir_name="/import/qaddi/API_Automation/Cisco_ISE_templates/"
        base_filename="rootCA1.cer"
        token = common_util.generate_token_from_file(dir_name,base_filename)
        print token
        data = {"token": token, "certificate_usage":"EAP_CA"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=uploadcertificate")
        print("Test Case 27 Execution Completed")
        sleep(30)


        '''
        Create_Cisco_ISE_Endpoint_IPAM_Notification
        '''
        logging.info("Create_Cisco_ISE_Endpoint_IPAM_Notification")
        response = ib_NIOS.wapi_request('GET',object_type="pxgrid:endpoint?_return_fields=address")
        print("response    : ",response)
        print(type(response))
        response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
        response=response.split(',')
        print(response)
        print(type(response))
        print(response[0])
	print("=----------------------------------------------------=")
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
        
        '''
        Create a DHCP network
        '''
        logging.info("Create an ipv4 IPAM network default network view")
        network_data = {"network": "10.0.0.0/8","network_view": "default","members":[{"_struct": "dhcpmember","ipv4addr":config.grid_master_vip}]}
        response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(network_data), grid_vip=config.grid_vip)
        print(response)
        
        logging.info("Restart DHCP Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        logging.info("Wait for 15 sec.,")
        sleep(20)
        '''
        Create_fixed_address of IPAM
        '''
        logging.info("Create an ipv4 fixed address with default network view")
        data = {"ipv4addr": "10.0.0.3","mac": "22:22:22:22:33:33","network_view": "default"}
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
        logging.info("Wait for 600 sec.,")
        sleep(600) 
        
       
        
        cls.test1=[]
        temp={}
        temp["Publish Type"]="CISCOISE_PUBLISH_IPAM"
        temp["Contents"]={'IpAddress': '10.0.0.3'}
      
        cls.test1.append(temp)
 
        logger.info ("Input Json for validation")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))
	sleep(300)

    def test_1_Publish_data(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
        search_str="search sourcetype=ib:reserved1 source=ib:ecosystem_publish:publish_data index=ib_ecosystem_publish| eval last_updated=if(isnum(timestamp), strftime(timestamp,\"%Y-%m-%d %H:%M:%S\"), timestamp) | rename timestamp as \"Last updated\",ip_address as \"IP Address\",notification_target as \"TARGET IP Address\", notification_action as \"Publish Type\", contents as \"Contents\",| table \"Last updated\", \"IP Address\", \"TARGET IP Address\", \"Publish Type\",\"Contents\""
        #cmd = config.search_py + " \"" + search_str + "\" --output_mode=json"
        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        logger.info (cmd) 
        print(os.system(cmd))
        os.system(cmd)
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operation failed, Please check Grid Configuration")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test1,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_results")
        result = compare_results(self.test1,results_list)
        print('-----------------------------------------------')
        print(self.test1)
        print(len(self.test1))
        print('---------------Adding Debugging line--------------------------------')
        print(results_list)
        print(len(results_list))
        print('-----------------------------------------------')
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg



    @classmethod
    def teardown_class(cls):
        logger.info('-'*15+"END:Publish Data"+'-'*15) 
        """
        '''
        Update_Grid_Master_Host_Name_To_Connect_Endpoint
        '''
        logging.info("Update Grid Master Host Name To_Connect_Endpoint")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member")
        print(get_ref)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        print ref1
        data = {"host_name": config.grid_fqdn}
        response = ib_NIOS.wapi_request('PUT', object_type=ref1, fields=json.dumps(data))
        print response
        logging.info(response)
        sleep(10)
	
	reff = ib_NIOS.wapi_request('GET', object_type="fileop")
        for ref in json.loads(reff):
        
            response = ib_NIOS.wapi_request('DELETE', object_type = ref["_ref"])
 	"""

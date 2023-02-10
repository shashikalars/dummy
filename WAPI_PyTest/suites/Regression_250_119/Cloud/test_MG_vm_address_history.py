"""
 Copyright (c) Infoblox Inc., 2016

 ReportName          : VM Address History
 ReportCategory      : Cloud
 Number of Test cases: 1
 Execution time      : 302.61 seconds
 Execution Group     : Minute Group (MG)
 Description         : This report will be updated every one minute. 
 Author : Raghavendra MN & Manimaran
 History: 05/23/2016 (Created)
 Reviewer : Raghavendra MN
"""
import config
import json
import os
import pytest
import pexpect
import re
import sys
import subprocess
from time import sleep
import unittest
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from logger import logger
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results


"""
TEST Steps:
      1.  Input/Preparaiton      : Configure CP HW's and cloud user , network and zones.
      2.  Search                 : Perform Dearult/Custom Search. 
      3.  Validation             : Compare Search result against inputdata. 
"""


class VMAddressHistory(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        logger.info('-'*15+"START:VM Address History"+'-'*15)

        logger.info("Preparation for VM Address History") 
        logger.info("Adding Cloud Group") 
        get_cloud_group = ib_NIOS.wapi_request('GET', object_type="admingroup?name~=cloud-api-only")
        ref_cloud_group = json.loads(get_cloud_group)[0]['_ref']
        data_modify = {"roles":["DHCP Admin", "DNS Admin"]}
        response = ib_NIOS.wapi_request('PUT', object_type=ref_cloud_group, fields=json.dumps(data_modify))

        logger.info("Adding Cloud User") 
        data = {"admin_groups":["cloud-api-only"],"name":"cloud","password":"infoblox"}
        response = ib_NIOS.wapi_request('POST', object_type="adminuser", fields=json.dumps(data))

        logger.info("Adding Cloud Network") 
        data_cloud_network = {"network":"224.0.0.0/8","network_view":"default","extattrs": {"Tenant ID":{"value": "1223"} , \
           "CMP Type":{"value":"vm600ctest"} ,"Cloud API Owned":{"value":"True"}}}
        response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data_cloud_network),user='cloud',password='infoblox')

        logger.info("Adding Fixed Address") 
        data_fixed_address = {"ipv4addr":"224.0.0.3","network_view":"default","mac":"11:11:11:22:33:44", \
           "extattrs": {"Tenant ID": {"value": "15487"},"VM ID": {"value": "5789"},"CMP Type": {"value":"vm-test123"}, \
           "Cloud API Owned": {"value":"True"}}}
        response = ib_NIOS.wapi_request('POST', object_type="fixedaddress", fields=json.dumps(data_fixed_address),user='cloud',password='infoblox')

        logger.info("Adding Cloud Zone") 
        data_zone = {"fqdn":"cloud.com","view":"default","grid_primary":[{"name":config.grid_fqdn,"stealth": False}], \
         "extattrs": {"Tenant ID":{"value":"56"} , "CMP Type":{"value":"vm105ctest"},"Cloud API Owned": {"value":"True"}}}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data_zone),user='cloud',password='infoblox')

        logger.info("Adding A Record") 
        data_a_record = {"name": "arec.cloud.com", "ipv4addr":"20.0.0.2","view": "default", \
          "extattrs": {"Tenant ID":{"value": "1011"},"CMP Type":{"value":"vm130ctest"}, \
          "Cloud API Owned": {"value":"True"},"VM ID":{"value":"12"}}}
        response = ib_NIOS.wapi_request('POST', object_type="record:a", fields=json.dumps(data_a_record),user='cloud',password='infoblox')

        logger.info("Adding AAAA Record") 
        data_aaaa_record = {"ipv6addr": "2620:40a:5000:2800::4","name":"aaaa.cloud.com","view":"default", \
           "extattrs": {"Tenant ID":{"value": "114"} , "Cloud API Owned":{"value":"True"}, \
           "CMP Type":{"value":"vm1012ctest"}, "VM ID":{"value":"415"}}}
        response = ib_NIOS.wapi_request('POST', object_type="record:aaaa", fields=json.dumps(data_aaaa_record),user='cloud',password='infoblox')


        logger.info("Performing Restart operation") 
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        logger.info("Waiting for 30 sec.,") 
        sleep(30)

        cls.test1= [ \
   	{  "IP Address":"2620:40a:5000:2800::4", "Action":"Allocated",  "Address Type":"Fixed",  "FQDN":"aaaa.cloud.com", \
	"Network View":"default", "Is Primary Interface":"No",  "Management Platform":"vm1012ctest" }, \
   	{  "IP Address":"20.0.0.2","Action":"Allocated", "Address Type":"Fixed", "FQDN":"arec.cloud.com", \
     	"Network View":"default", "Is Primary Interface":"No",  "Management Platform":"vm130ctest" }, \
   	{  "IP Address":"224.0.0.3", "Action":"Allocated", "Address Type":"Fixed", "MAC Address":"11:11:11:22:33:44", \
        "Network":"224.0.0.0/8", "Network View":"default", "Is Primary Interface":"No", "Management Platform":"vm-test123" } ]
        
        cls.test2= [ \
        {  "IP Address":"20.0.0.2","Action":"Allocated", "Address Type":"Fixed", "FQDN":"arec.cloud.com", \
        "Network View":"default", "Is Primary Interface":"No",  "Management Platform":"vm130ctest" } ]

        logger.info ("Input Json for validation")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))
        logger.info("Waiting for 3 min for report update")
        sleep(180)


    def test_1_vm_address_history_default_filter(self):
        logger.info("Test"+sys._getframe().f_code.co_name)
        search_str=r"search sourcetype=ib:reserved2 source=ib:cloud:vm_address_history index=ib_cloud | eval IS_PRIMARY_IFC=case(is_primary_ifc==1, \"Yes\", is_primary_ifc==0, \"No\") | eval TYPE=case(address_type==0, \"Floating\", address_type==1, \"Fixed\", address_type==2, \"Private\", address_type==3, \"Public\", address_type==4, \"Elastic\", 1==1, address_type) | convert ctime(_time) as Time  | sort -Time address network_view | rename address as \"IP Address\", TYPE as \"Address Type\", ACTION as \"Action\", IS_PRIMARY_IFC as \"Is Primary Interface\", mac_address as \"MAC Address\", port_id as \"Port ID\", cnames as \"CNAME(s)\", fqdn as \"FQDN\", vm_name as \"VM Name/Instance Name\", network as \"Network\", network_view as \"Network View\", tenant_id as \"Tenant ID\", TENANT_NAME as \"Tenant Name\", location as \"Location\", vlan_id as \"VLAN ID\", application_type as \"Application Type\", private_hostname as \"Private Hostname\", public_hostname as \"Public Hostname\", private_address as \"Private Address\", public_address as \"Public Address\", elastic_address as \"Elastic Address\", interface_name as \"Interface Name\", mgmt_platform as \"Management Platform\", vm_vpc_id as \"VPC ID\", vm_vpc_name as \"VPC Name\", vpc_addr as \"VPC Network\", vm_hostname as \"VM Hostname\" | table Time \"IP Address\" \"Action\" \"Address Type\" \"MAC Address\" \"CNAME(s)\" \"Port ID\" \"FQDN\" \"VM Name/Instance Name\" \"Network\" \"Network View\" \"Tenant ID\" \"Tenant Name\" \"Location\" \"VLAN ID\" \"Application Type\" \"Private Hostname\" \"Public Hostname\" \"Private Address\" \"Public Address\" \"Elastic Address\" \"Interface Name\" \"Is Primary Interface\" \"Management Platform\" \"VPC ID\" \"VPC Name\" \"VPC Network\" \"VM Hostname\""

        cmd = config.search_py + " \"" + search_str + "\" --output_mode=json"
        os.system(cmd)
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test1,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 10")
        result = compare_results(self.test1,results_list,10)
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg
    
    def test_2_vm_address_history_default_filter_tenant(self):
        logger.info("Test"+sys._getframe().f_code.co_name)
        search_str=r"search sourcetype=ib:reserved2 source=ib:cloud:vm_address_history index=ib_cloud (host=\"*\") tenant_id=\"1011\" | eval IS_PRIMARY_IFC=case(is_primary_ifc==1, \"Yes\", is_primary_ifc==0, \"No\") | eval TYPE=case(address_type==0, \"Floating\", address_type==1, \"Fixed\", address_type==2, \"Private\", address_type==3, \"Public\", address_type==4, \"Elastic\", 1==1, address_type) | convert ctime(_time) as Time | sort -Time address network_view                   | rename address as \"IP Address\", TYPE as \"Address Type\", ACTION as \"Action\", IS_PRIMARY_IFC as \"Is Primary Interface\", mac_address as \"MAC Address\", port_id as \"Port ID\", cnames as \"CNAME(s)\", fqdn as \"FQDN\", vm_name as \"VM Name/Instance Name\", network as \"Network\", network_view as \"Network View\", tenant_id as \"Tenant ID\", TENANT_NAME as \"Tenant Name\", location as \"Location\", vlan_id as \"VLAN ID\", application_type as \"Application Type\", private_hostname as \"Private Hostname\", public_hostname as \"Public Hostname\", private_address as \"Private Address\", public_address as \"Public Address\", elastic_address as \"Elastic Address\", interface_name as \"Interface Name\", mgmt_platform as \"Management Platform\", vm_vpc_id as \"VPC ID\", vm_vpc_name as \"VPC Name\", vpc_addr as \"VPC Network\", vm_hostname as \"VM Hostname\"  | table Time \"IP Address\" \"Action\" \"Address Type\" \"MAC Address\" \"CNAME(s)\" \"Port ID\" \"FQDN\" \"VM Name/Instance Name\" \"Network\" \"Network View\" \"Tenant ID\" \"Tenant Name\" \"Location\" \"VLAN ID\" \"Application Type\" \"Private Hostname\" \"Public Hostname\" \"Private Address\" \"Public Address\" \"Elastic Address\" \"Interface Name\" \"Is Primary Interface\" \"Management Platform\" \"VPC ID\" \"VPC Name\" \"VPC Network\" \"VM Hostname\""
        cmd = config.search_py + " \"" + search_str + "\" --output_mode=json"
        os.system(cmd)
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test2,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 10")
        result = compare_results(self.test2,results_list,10)
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg
 
    @classmethod
    def teardown_class(cls):
        logger.info("Cleanup, Deleting added Network, Zoens and Cloud User Groups")
        cloud_network = ib_NIOS.wapi_request('GET', object_type="network?network~=224.0.0.0/8")
        ref = json.loads(cloud_network)[0]['_ref']
        del_status = ib_NIOS.wapi_request('DELETE', object_type = ref,user='cloud',password='infoblox')

        cloud_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn~=cloud.com")
        ref = json.loads(cloud_zone)[0]['_ref']
        del_status = ib_NIOS.wapi_request('DELETE', object_type = ref)

        cloud_user = ib_NIOS.wapi_request('GET', object_type="adminuser?name~=cloud")
        ref = json.loads(cloud_user)[0]['_ref']
        del_status = ib_NIOS.wapi_request('DELETE', object_type = ref)

        logger.info("Performing Restart operation") 
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        logger.info('-'*15+"END:VM Address History"+'-'*15)

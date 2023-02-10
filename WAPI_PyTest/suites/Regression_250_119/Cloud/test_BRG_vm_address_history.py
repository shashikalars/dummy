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


    def test_1_brg_vm_address_history_default_filter(self):
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
    
    def test_2_brg_vm_address_history_default_filter_tenant(self):
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
        logger.info('-'*15+"END:Cloud VM Address History report"+'-'*15)

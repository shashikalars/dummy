"""
 Copyright (c) Infoblox Inc., 2016
 ReportName          : Subscription Data
 ReportCategory      : Subscription Data
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
      3.  Validation : comparing Search results with Reterived  'Subscription Data' report without delta.
"""

class Subscription_Data(unittest.TestCase):

    
    @classmethod
    def setup_class(cls):
        logger.info('-'*15+"START:Subscription Data"+'-'*15)
        
        child1 = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+config.MS_user+'@'+config.dns_resolver)
        try:
            child1.logfile=sys.stdout
            child1.expect('password:')
            child1.sendline('Infoblox123')
            #child1.expect('$ >')
	    sleep(5)
            child1.sendline('exit')
            
            child1.close()
            assert True    
        except Exception as e:
            child1.close()
            print("Failure: Failed to login MS server")
            print(e)
            assert False
        
        cls.test1=[]
        temp={}
        temp["Domain"]="ad-36.local"
        temp["IP Address"]="10.34.98.36"
        temp["GUID"]="test1"

        cls.test1.append(temp)
 
        logger.info ("Input Json for validation")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))
	sleep(100)

    def test_1_Subscription_data(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
        search_str="search source=ib:ecosystem_subscription:subscription_data index=ib_ecosystem_subscription | eval last_discovered_timestamp=if(isnum(last_discovered_timestamp), strftime(last_discovered_timestamp,\"%Y-%m-%d %H:%M:%S\"), last_discovered_timestamp) | rename username as \"User Name\",domainname as \"Domain\",cisco_ise_ssid as \"Cisco ISE SSID\", port_vlan_name as \"VLAN Name\", port_vlan_number as \"VLAN ID\", cisco_ise_session_state as \"Cisco ISE Session State\", cisco_ise_endpoint_profile as \"Cisco ISE Endpoint profile\", cisco_ise_security_group as \"Cisco ISE Security Group\", last_discovered_timestamp as \"Discovered At\", ea_eps_status as \"Cisco ISE EPS Status\", ip_address as \"IP Address\", guid as \"GUID\",| table \"User Name\", \"Domain\", \"Cisco ISE SSID\", \"VLAN Name\", \"VLAN ID\", \"Cisco ISE Session State\", \"Cisco ISE Endpoint profile\",\"Cisco ISE Security Group\", \"Discovered At\", \"Cisco ISE EPS Status\", \"IP Address\", \"GUID\""
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
        logger.info('-'*15+"END:Subscription Data"+'-'*15) 
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

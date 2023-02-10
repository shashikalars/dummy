"""
 Copyright (c) Infoblox Inc., 2016
 Report Name          : DNS Top SERVFAIL
 Report Category      : DNS
 Number of Test cases: 1
 Execution time      :  seconds
 Execution Group     : Hour Group (HG)
 Description         : DNS Top SERVFAIL Errors Received. 

 Author   : Shashikala R S
 History  : 03/03/2021 (Created)
 Reviewer : 
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
      1.  Input/Preparaiton      : Adding Zones, A records, etc.,
      2.  Search                 : Performing Search operaion with default/custom filter
      3.  Validation             : Comparing Search results against Audit log events. 
     
"""

class DNS_Top_SERVFAIL_Errors_Received(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        logger.info('-'*15+"START:DNS Top SERVFAIL Errors Received"+'-'*15)
        logger.info("Preparation for DNS Top SERVFAIL Errors Received Report")
        logger.info("Add forward zone 'fwd1.com'")
        
        
        cls.test1=[]
        temp={}
        temp["Domain Name"]="arec.fwd.com."
        #temp["Queries"]="24"
        
        cls.test1.append(temp)
  

        logger.info ("Input Json for validation")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))
        
        
    def test_1_DNS_Top_SERVFAIL_Errors_Received(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
        # search_str="search index=ib_dns_summary report=si_top_servfail_received_queries | lookup dns_viewkey_displayname_lookup VIEW output display_name | bucket span=1h _time | stats sum(COUNT) as SF_QUERIES by NAME | sort -SF_QUERIES | head 10 | eventstats sum(SF_QUERIES) as COUNT_SUM | eval FAIL_PERCENT=round(SF_QUERIES*100/COUNT_SUM, 1) | eval DNPERCENT=NAME + \"(\"+ FAIL_PERCENT + \"%)\" | rename DNPERCENT as \"Domain Name\", SF_QUERIES as \"Queries\" | fields \"Domain Name\", \"Queries\""
        
        search_str="search index=ib_dns_summary report=si_top_servfail_received_queries | lookup dns_viewkey_displayname_lookup VIEW output display_name | bucket span=1h _time | stats sum(COUNT) as SFR_QUERIES by NAME | sort -SFR_QUERIES | head 10 | eventstats sum(SFR_QUERIES) as COUNT_SUM | eval DNPERCENT=NAME | rename DNPERCENT as \"Domain Name\" | fields \"Domain Name\""
                       
        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        print(os.system(cmd))
        
        
        try:
            retrived_data=open(config.json_file).read()
            print(retrived_data)
           
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']



        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test1,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        result = compare_results(self.test1,results_list)
        logger.info("-----------------------------------------------------")
        logger.info(self.test1)
        logger.info(len(self.test1))
        logger.info("--------------Adding Debugging line ------------------")
        logger.info(results_list)
        logger.info(len(results_list))
        logger.info("-----------------------------------------------------")
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg

    @classmethod
    def teardown_class(cls):
        logger.info('-'*15+"END:DNS Top SERVFAIL Errors Received"+'-'*15)
        print("DELETE")
        grid1_zone_get = ib_NIOS.wapi_request('GET', object_type="zone_auth")
        #print(grid1_zone_get)
        for ref in json.loads(grid1_zone_get):
            if 'fwd1.com' in ref['_ref']:
            
                res = ib_NIOS.wapi_request('DELETE', object_type = ref['_ref'])
                print(res)
            
        grid2_zone_get = ib_NIOS.wapi_request('GET', object_type="zone_auth",grid_vip=config.grid_member2_vip)
        #print(grid2_zone_get)
        for ref in json.loads(grid2_zone_get):
            if 'fwd1.com' in ref['_ref']:
            
                res = ib_NIOS.wapi_request('DELETE', object_type = ref['_ref'])
            
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        logger.info('Grid restart services after cleanup')
        #sleep(30)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_member2_vip)
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",grid_vip=config.grid_member2_vip)
        logger.info('Grid restart services after cleanup')
        sleep(30)

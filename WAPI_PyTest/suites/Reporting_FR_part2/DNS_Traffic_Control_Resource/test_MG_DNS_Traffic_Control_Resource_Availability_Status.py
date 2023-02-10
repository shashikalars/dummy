"""
 Copyright (c) Infoblox Inc., 2016

 Report Name          	: 1) DNS Traffic Control Resource Availability Status (Detailed)
			   
 Report Category      	: DNS Traffic Control
 Number of Test cases 	: 2 
 Execution time      	: 932.97 seconds
 Execution Group     	: Minute Group (MG)
 Description         	: Validating Availability status with Available and Unavailable count, this Report will update immediately after 10 minutes. 
		      	  Validating Resource Availability Status with Available and Unavailable count, this Report will update immediately after 10 minutes.
 
 Author 		: Shashikala R S
 History		: 03/09/2021 (Created)
"""
import config
import json
import os
import pytest
import pexpect
import re
import sys
import subprocess
import unittest
import time

import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from logger import logger
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results

"""
TEST Steps:
	1. Input/Preparation  : 
          a) Add Zone dtc.com with Master as Grid Primary. 
	  b) Add DTC servers as, 
		1) server1 - 10.120.21.249 	(Status : Running)
		
          c) Add DTC Pool as,
		1) pool1 - server1		(Status : Running)
  		
          d) Add DTC LBDN as, 
		1) lbdn1 - a1.dtc.com, pool1 	(Status : Running)
		
	  e) Reports :
 		1) DNS Traffic Control Resource Availability Status (Detailed) 
			
      		
	2. Search     : Performing Search operation with default/custom filter
	3. Validation : comparing Search results with Retrieved 'DNS Traffic Control Resource Resource Availability Status' report without delta.
"""

class dnstrafficcontrolresourceavailabilitystatus(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        logger.info('-'*15+"START:DNS Traffic Control Resource Availability Status"+'-'*15)
        
	#cls.test1=[{"Availability":"Available","count":"3"}]
        cls.test1=[{"Availability":"Available"}]
        
        logger.info ("Input Json for validation of DNS Traffic Control Pool Availability Status")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))
	
    	
        logger.info ("Wait 10 minutes for reports to get update")
        #time.sleep(330)

    def test_1_dns_traffic_control_resource_availability_status(self):
        logger.info("Test:"+sys._getframe().f_code.co_name)         
	search_str=r"search sourcetype=ib:dns:reserved source=/infoblox/var/reporting/idns_res_avail.csv index=ib_dtc | eval Availability=case(available==0, \"Unavailable\", unavailable==0, \"Available\", unavailable>0,  \"Partially Available\") | chart count by Availability"
        cmd = config.search_py + " \"" + search_str + "\" --output_mode=json"
        logger.info (cmd)
        os.system(cmd)
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operation failed, Please check Grid Configuration")        	
	output_data = json.loads(retrived_data)
        results_list = output_data['results']
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test1,results_list)  
	logger.info("compare_results without 'delta'")
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
        logger.info("Cleanup: Delete all DTC Objects and Zone Associated with it")
	
        lbdn1_get = ib_NIOS.wapi_request('GET', object_type="dtc:lbdn?name=lbdn1")
        lbdn1_ref = json.loads(lbdn1_get)[0]['_ref']
        lbdn1del_status = ib_NIOS.wapi_request('DELETE', object_type = lbdn1_ref)
            
            
        pool1_get = ib_NIOS.wapi_request('GET', object_type="dtc:pool?name=pool1")
        pool1_ref = json.loads(pool1_get)[0]['_ref']
        pool1del_status = ib_NIOS.wapi_request('DELETE', object_type = pool1_ref)


        server1_get = ib_NIOS.wapi_request('GET', object_type="dtc:server?name=server1")
        server1_ref = json.loads(server1_get)[0]['_ref']
        server1del_status = ib_NIOS.wapi_request('DELETE', object_type = server1_ref)
            

        del_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=dtc1.com")
        ref = json.loads(del_zone)[0]['_ref']
        del_status = ib_NIOS.wapi_request('DELETE', object_type = ref)

        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        logger.info('Grid restart services after cleanup')
        time.sleep(30)

        logger.info('-'*15+"END:DNS Traffic Control Resource Availability Status"+'-'*15)

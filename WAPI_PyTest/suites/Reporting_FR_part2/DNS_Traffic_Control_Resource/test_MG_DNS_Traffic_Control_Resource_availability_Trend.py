"""
 Copyright (c) Infoblox Inc., 2016

 Report Name          	: 	1) DNS Traffic Control Resource Availibility Trend (Detailed)
				
					   
 Report Category      	: 	DNS Traffic Control
 Number of Test cases	: 	1
 Execution time     	: 	 seconds
 Execution Group     	: 	Minute Group (MG)
 Description         	: 	Validating Resource Availability Trend by Server health status, this Report will update immediately after 10 minutes. 
				Validating Availability Trend by health status, this Report will update immediately after 10 minutes.
					   
 Author			:	Shashikala R S
 History		:	03/09/2021 (Created)
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
	1.  Input/Preparation  : 
            a) Add Zone dtc.com with Master as Grid Primary. 
	    b) Add DTC servers as, 
		1) server1 - 10.120.21.249 	(Status : Error,  2 out of 3 monitors in error status, 33.34%)
		
	    c) Add DTC Pool as,
		1) pool1 - server1				, Monitors : ICMP, SIP, PDP			(Status : Warning)
						(Status : Warning)
	    d) Add DTC LBDN as, 
		1) lbdn1 - a1.dtc.com, pool1 	(Status : Running)
		
	    e) Reports :
		1) DNS Traffic Control Resource SNMP Trend (Detailed).
		      Report will show Server Availability based on health status of DTC servers, 
			a)Resource = server1,oid":".1.3.6.1.2.1.2.2.1.1.10","value":'10'	
		
				
	2.  Search     : Performing Search operation with default/custom filter
	3.  Validation : comparing Search results with Retrieved 'DNS Traffic Control Resource Availibility Trend' with delta .5
"""

class dns_traffic_control_resource_snmp_trend(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        logger.info('-'*15+"START : DNS Traffic Control Resource Availibility Trend"+'-'*15)
        cls.test1=[]
	temp={}
        temp["server1"]="100"
        
	cls.test1.append(temp)
        logger.info ("Input Json data for validation of DNS Traffic Control Resource Availability trend report")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))
        #logger.info ("Wait 15 minutes for reports to get update")
        #time.sleep(1200)
        #time.sleep(120)
    def test_1_dns_traffic_control_resource_availability_trend(self):
        logger.info("Test:"+sys._getframe().f_code.co_name)       
   	search_str=r"search sourcetype=ib:dns:reserved source=/infoblox/var/reporting/idns_res_avail.csv index=ib_dtc | bucket span=10m _time | stats sum(available) as available, sum(unavailable) as unavailable by _time, resource | eval percent = 100*available/(available + unavailable) | timechart bins=1000 avg(percent) by resource" 
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
        results_dist= results_list[-240::1]
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test1,results_dist)
        logger.info("compare_resutls with 'delta'=.5")
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
	
        logger.info('-'*15+"END:DNS Traffic Control Resource Availability Trend"+'-'*15)

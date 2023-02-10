"""
 Copyright (c) Infoblox Inc., 2016

 ReportName          : Traffic Rate (Detailed)
 ReportCategory      : System
 Number of Test cases: 1
 Execution time      : 302.61 seconds
 Execution Group     : Minute Group (MG)
 Description         : Traffic Rate report will be updated every 1 min.

 Author   : Raghavendra MN
 History  : 05/23/2016 (Created)
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
from unicodedata import numeric
import unittest
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from logger import logger
from ib_utils.ib_system import search_dump 
from ib_utils.ib_validaiton import compare_results 

"""
TEST Steps:
      1.  Input/Preparaiton      : No
      2.  Search                 : Performing Search operaion with default/custom filter
      3.  Validation             : Validating Inbound & Outbound Traffic is greater than 0 [We cannot validate exact inbound or outbound traffic]
"""


class SystemTrafficRate(unittest.TestCase):
     @classmethod
     def setup_class(cls):
        #Test Preparation to Fetch Member Information. 
        cls.test1=[]
        traffic_rate={}
        logger.info('-'*15+"START:Traffic Rate"+'-'*15)
    	response = ib_NIOS.wapi_request("GET", object_type="member?_return_fields%2b=node_info,vip_setting")
        val = json.loads(response)
        for i in val:
            member_ip = i["vip_setting"]["address"]
            traffic_rate[i["host_name"]+": inbound"] =  '20000'
            traffic_rate[i["host_name"]+": outbound"] = '20000'
            #traffic_rate["_time"] = ib_get.indexer_date(config.indexer_ip)  #ib_get.indexer_date(config.indexer_ip,-600,10) 
         
        cls.test1.append(traffic_rate)
        logger.info ("Input Json for validation")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))
        logger.info ("Waiting for 300 sec., reports to gets updated")
        #sleep(300) #wait for report update
        #sleep(60)

     def test_001_traffic_rate_default_filter(self):
        logger.info ("TestCase:"+sys._getframe().f_code.co_name)
        search_str=r"search sourcetype=ib:system index=ib_system bps | eval MEMBER=host+\": \"+if(sys_report_id=3,\"inbound\",\"outbound\") | bucket span=1m _time | timechart bins=1000 avg(TRAF_VALUE) by MEMBER where max in top26 useother=f"
        cmd = config.search_py + " \"" + search_str + "\" --output_mode=json"
        
        logger.info('-'*15)
        print(os.system(cmd))
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e )
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        results_dist= results_list[-10::1]

        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        print(results_dist)
        first=results_dist[0]
	print("/////////////////////////////////////////////////////////////////////")
        print("FIRST OF DICTIONARY",first)
	print("/////////////////////////////////////////////////////////////////////")

	'''
	for k,v in first.items():
	    print("KEY",k)
	    if str(config.grid_member_fqdn)+": inbound" in k:
	        print("VALUE",v,type(v))
		print("##############",float(v),type(float(v)))
	'''
	second=results_dist[1]
	print("SECOND OF DICTIONARY",second)
	print("/////////////////////////////////////////////////////////////////////")


	if str(config.grid_member_fqdn)+": inbound" in results_dist[0]:
	    print("***********INPUT************")

	    if ((first[str(config.grid_member1_fqdn)+": inbound"] >= 0) and (first[str(config.grid_member1_fqdn)+": outbound"] >= 0) and (first[str(config.grid_member_fqdn)+": inbound"] >= 0) and (first[str(config.grid_member_fqdn)+": outbound"] >= 0) and (first[str(config.grid_member2_fqdn)+": inbound"] >= 0) and (first[str(config.grid_member2_fqdn)+": outbound"] >= 0) and (first[str(config.grid_member3_fqdn)+": inbound"] >= 0) and (first[str(config.grid_member3_fqdn)+": outbound"] >= 0) and (first[str(config.grid_member4_fqdn)+": inbound"] >= 0) and (first[str(config.grid_member4_fqdn)+": outbound"] >= 0) and (first[str(config.grid_member5_fqdn)+": inbound"] >= 0) and (first[str(config.grid_member5_fqdn)+": outbound"] >= 0) and (first[str(config.reporting_member1_fqdn)+": inbound"] >= 0) and (first[str(config.reporting_member1_fqdn)+": outbound"] >= 0)):
	    
                print("--------------***********----------------")
                print("PASSED IN FIRST ELEMENT")
		assert True

            else:
            	logger.error("Search validation result: %s(FAIL)",first)
            	msg = 'Count does not match - %s', first
            	assert False

	elif str(config.grid_member_fqdn)+": inbound" in results_dist[1]:
	    
 	    if (second[str(config.grid_member1_fqdn)+": inbound"] >= 0 and second[str(config.grid_member1_fqdn)+": outbound"] >= 0 and second[str(config.grid_member_fqdn)+": inbound"] >= 0 and second[str(config.grid_member_fqdn)+": outbound"] >= 0 and second[str(config.grid_member2_fqdn)+": inbound"] >= 0 and second[str(config.grid_member2_fqdn)+": outbound"] >= 0 and second[str(config.grid_member3_fqdn)+": inbound"] >= 0 and second[str(config.grid_member3_fqdn)+": outbound"] >= 0 and second[str(config.grid_member4_fqdn)+": inbound"] >= 0 and second[str(config.grid_member4_fqdn)+": outbound"] >= 0 and second[str(config.grid_member5_fqdn)+": inbound"] >= 0 and second[str(config.grid_member5_fqdn)+": outbound"] >= 0 and second[str(config.reporting_member1_fqdn)+": inbound"] >= 0 and second[str(config.reporting_member1_fqdn)+": outbound"] >= 0):

                print("--------------***********----------------")
                print("PASSED IN SECOND ELEMENT")
		assert True

            else:
                logger.error("Search validation result: %s(FAIL)",first)
                msg = 'Count does not match - %s', first
                assert False		    

	else:
	    print("NO DATA PRESENT")
	    assert False

	'''

        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test1,results_dist)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 20000")
        result = compare_results(self.test1,results_list,20000)
        logger.info("-----------------------------------------------------")
        logger.info(self.test1)
        logger.info(len(self.test1))
        logger.info("--------------------Adding debug line-------------------")
        logger.info(results_list)
        logger.info(len(results_list))
        logger.info("-----------------------------------------------------")
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg

	'''

     @classmethod
     def teardown_class(cls):
        logger.info('-'*15+"END:Traffic Rate"+'-'*15)


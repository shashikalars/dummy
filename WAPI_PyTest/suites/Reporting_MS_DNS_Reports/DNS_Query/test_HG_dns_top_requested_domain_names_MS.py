"""
 Copyright (c) Infoblox Inc., 2016

 ReportName          : DNS Top Requested Domain Names
 ReportCategory      : DNS Query
 Number of Test cases: 1
 Execution time      : 302.61 seconds
 Execution Group     : Hourly Group (HG)
 Description         : DNS 'DNS Top Requested Domain Nmaes' reports will update hourly.

 Author : Raghavendra MN
 History: 05/30/2016 (Created)
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
      1.  Input/Preparaiton      : This is Hourly Report and Preparation is injected separately.
      2.  Search                 : Search with Default Filter
      3.  Validation             : Validating Search result against input data
"""
class DNSTopRequestedDomainNames(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        logger.info('-'*15+"START:DNS Top Requested Domain Names"+'-'*15)
        
	#cls.test1=[{"Domain Name": "admin-api.pingone.com"}]
     
	cls.test1=[{"Domain Name": "domain2.abc.com"},{"Domain Name": "domain1.abc.com"}]
	
        #cls.test1=[{"Domain Name": "32.98.34.10.in-addr.arpa"}]

	logger.info ("Json input for validation test1")
        
	logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))
        

    def test_1_dns_top_requested_domain_names(self):

        logger.info(sys._getframe().f_code.co_name)
        search_str=r"search index=ib_dns_summary report=si_dns_requested_domain | lookup dns_viewkey_displayname_lookup VIEW output display_name | stats sum(COUNT) as FQDN_TOTAL by FQDN | sort -FQDN_TOTAL | head 10 | eventstats sum(FQDN_TOTAL) as TOTAL | eval PERCENT=round(FQDN_TOTAL*100/TOTAL, 1) | eval PHOST=FQDN | rename FQDN_TOTAL as Count, PHOST as \"Domain Name\" | fields \"Domain Name\""

	#search_str=r"search index=ib_dns_summary report=si_dns_requested_domain (orig_host=\"*\") | lookup dns_viewkey_displayname_lookup VIEW output display_name | stats sum(COUNT) as FQDN_TOTAL by FQDN | sort -FQDN_TOTAL | head 20 | eventstats sum(FQDN_TOTAL) as TOTAL | eval PERCENT=round(FQDN_TOTAL*100/TOTAL, 1) | eval PHOST=FQDN+\" (\"+PERCENT+\"%%)\" | rename FQDN_TOTAL as Count, PHOST as \"Domain Name\" | fields \"Domain Name\", Count"
        cmd = config.search_py + " \"" + search_str + "\" --output_mode=json"
        os.system(cmd)
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
	results_dist = results_list[-240::1]

	'''
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        print(results_dist)
        first=results_dist[0]
        print(first)


        if first['1.0.0.127.in-addr.arpa'] >= 10 and first['32.98.34.10.in-addr.arpa'] >= 10:
            print("-----------------------------------------")
            print("Count of 32.98.34.10.in-addr.arpa:",first['32.98.34.10.in-addr.arpa'])
            print("Count of 1.0.0.127.in-addr.arpa :",first['1.0.0.127.in-addr.arpa'])
            print("--------------***********----------------")
            print("Successfully PASSED")
            logger.info("Search validation result: %s (PASS)",first)

        else:
            logger.error("Search validation result: %s (FAIL)",first)

            msg = 'Count does not match - %s', first
            assert first == 0, first
	
	logger.info("Appending % value in Domain name")
        M=self.test1
        L=results_list
        tot=0
        for H in L:
            tot+= int(H["Queries"])
        temp_test1=[]
        for N in M:
            comp_dict={}
            per="{0:.1f}".format((float(N["Queries"])/tot)*100)
            comp_dict["Domain Name"]=N["Domain Name"]+". ("+per+"%)"
            comp_dict["Queries"]=N["Queries"]
            temp_test1.append(comp_dict)
	'''

        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test1,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        result = compare_results(self.test1,results_list)

        print("######EXPECTED OUTPUT########",self.test1)
        logger.info("-----------------------------------------------------")
        logger.info(self.test1)
	logger.info("-----------------------------------------------------")
        print("#######ACTUAL OUTPUT#########",results_list)
        logger.info("-----------------------------------------------------")
        logger.info(results_list)
        logger.info("-----------------------------------------------------")
        print("#########COMPARISON##########",result)
	logger.info("-----------------------------------------------------")
	logger.info(result)

        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg

    def teardown_class(cls):
        logger.info('-'*15+"END:DNS Top Requested Domain Names."+'-'*15)

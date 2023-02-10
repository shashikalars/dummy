"""
 Copyright (c) Infoblox Inc., 2016
 Report Name          : DNS Top RPZ Hits 
 Report Category      : DNS Security
 Number of Test cases : 1
 Execution time       : 302.61 seconds
 Execution Group      : Minute Group (MG)
 Description          :

 Author  : Harish
 History : 06/02/2016 (Created)
 Reviewer: Raghavendra MN
"""
import pytest
import unittest
import logging
import subprocess
import json
import os
#import ib_utils.ib_validaiton as ib_validation
#import ib_utils.ib_system as ib_system
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
import config
import pexpect
import sys
import random
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from time import sleep
from logger import logger
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results

"""
TEST Steps:
      1.  Input/Preparation  : Add RPZ zones with different types of rules 
                               Perform query opration on added zones to hit the rules with different clients
      2.  Search     : Performing Search operaion with default/custom filter
      3.  Validation : comparing Search results with Reterived 'DNS Top RPZ Hits' report without delta.
"""

class DNSTopRPZHits(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        logger.info('-'*15+"START:DNS Top RPZ Hits"+'-'*15)
        logger.info ("Preparation has executed 1 hour before as this report will take 1 hour to update")
        cls.test1=[]
        temp={}
        temp["Client ID"]=config.client_ip
        temp["Total Client Hits"]="145"
        temp["Domain Name"]="asm"
        temp["RPZ Entry"]="asm.rpz_feed.com"
        temp["RPZ Severity"]="MAJOR"
        temp["Total Rule Hits"]="50"
        temp["Mitigation Action"]="Substitute (A)"
        temp["Substitute Addresses"]="A=12.12.12.12;"
        cls.test1.append(temp)
         
        temp={}
        temp["Client ID"]=config.client_ip
        temp["Total Client Hits"]="145"
        temp["Domain Name"]="asm1"
        temp["RPZ Entry"]="asm1.rpz_feed.com"
        temp["RPZ Severity"]="MAJOR"
        temp["Total Rule Hits"]="40"
        temp["Mitigation Action"]="Substitute (A)"
        temp["Substitute Addresses"]="A=22.22.22.22;"
        cls.test1.append(temp)
      
             
        temp={}
        temp["Client ID"]=config.client_ip
        temp["Total Client Hits"]="145"
        temp["Domain Name"]="blockdn.com"
        temp["RPZ Entry"]="blockdn.com.rpz_feed.com"
        temp["RPZ Severity"]="MAJOR"
        temp["Total Rule Hits"]="15"
        temp["Mitigation Action"]="Block (No Data)"
        cls.test1.append(temp)

 
         
        temp={}
        temp["Client ID"]=config.client_ip
        temp["Total Client Hits"]="145"
        temp["Domain Name"]="g.com"
        temp["RPZ Entry"]="g.com.rpz_feed.com"
        temp["RPZ Severity"]="MAJOR"
        temp["Total Rule Hits"]="40"
        temp["Mitigation Action"]="Substitute"
        cls.test1.append(temp)
          
         
        
        logger.info ("Input Json for validation")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))

        cls.test3=[]
        temp={}
        temp["Client ID"]=config.client_ip
        temp["Total Client Hits"]="50"
        temp["Domain Name"]="asm"
        temp["RPZ Entry"]="asm.rpz_feed.com"
        temp["RPZ Severity"]="MAJOR"
        temp["Total Rule Hits"]="50"
        temp["Mitigation Action"]="Substitute (A)"
        temp["Substitute Addresses"]="A=12.12.12.12;"
        cls.test3.append(temp)

        
        logger.info ("Input Json for validation")
        logger.info(json.dumps(cls.test3, sort_keys=True, indent=4, separators=(',', ': ')))    
       
        cls.test2=[]
        temp={}
        temp["Client ID"]=config.client_ip
        temp["Total Client Hits"]="40"
        temp["Domain Name"]="g.com"
        temp["RPZ Entry"]="g.com.rpz_feed.com"
        temp["RPZ Severity"]="MAJOR"
        temp["Total Rule Hits"]="40"
        temp["Mitigation Action"]="Substitute"
        cls.test2.append(temp)
          
        logger.info ("Input Json for validation")
        logger.info(json.dumps(cls.test2, sort_keys=True, indent=4, separators=(',', ': ')))


 
          
    def test_1_dns_top_rpz_hits_classes(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
	search_str=r"search index=ib_dns_summary report=si_dns_rpz_hits | lookup dns_viewkey_displayname_lookup VIEW output display_name | eval DNS_VIEW =if(isnull(display_name), \"NULL\",display_name) | eval RECORD_DATA=if(isnull(RECORD_DATA),\"\",RECORD_DATA) | eval RPZ_QNAME=if(isnull(RPZ_QNAME),\"\",RPZ_QNAME) | eval RPZ_SEVERITY=if(isnull(RPZ_SEVERITY),\"\",RPZ_SEVERITY) | where MITIGATION_ACTION != \"ER\" | stats sum(COUNT) as QCOUNT by _time, CLIENT, DOMAIN_NAME, DNS_VIEW, orig_host, TOTAL_COUNT, MITIGATION_ACTION, RPZ_SEVERITY, RECORD_DATA RPZ_QNAME | stats sum(TOTAL_COUNT) as TOTAL_COUNT, sum(QCOUNT) as QCOUNT by _time, CLIENT, DOMAIN_NAME, DNS_VIEW, MITIGATION_ACTION, RPZ_SEVERITY, RECORD_DATA RPZ_QNAME | convert ctime(_time) as Time | sort -QCOUNT | head 10 | eval MITIGATION_ACTION=case(MITIGATION_ACTION == \"PT\", \"Passthru\", MITIGATION_ACTION == \"NX\", \"Block (No Such Domain)\", MITIGATION_ACTION == \"ND\", \"Block (No Data)\", MITIGATION_ACTION == \"SB\", \"Substitute\", MITIGATION_ACTION == \"A1\", \"Substitute (A)\", MITIGATION_ACTION == \"A4\", \"Substitute (AAAA)\", MITIGATION_ACTION == \"AA\", \"Substitute (A/AAAA)\", MITIGATION_ACTION == \"DN\", \"Substitute (Domain Name)\", MITIGATION_ACTION == \"ER\", \"Error\") | eval RPZ_SEVERITY=case(RPZ_SEVERITY == \"4\", \"INFORMATIONAL\", RPZ_SEVERITY == \"6\", \"WARNING\", RPZ_SEVERITY == \"7\", \"MAJOR\", RPZ_SEVERITY == \"8\", \"CRITICAL\", RPZ_SEVERITY == \"\", \"\") | rename CLIENT as \"Client ID\", QCOUNT as \"Total Client Hits\", DOMAIN_NAME as \"Domain Name\", TOTAL_COUNT as \"Total Rule Hits\", RPZ_QNAME as \"RPZ Entry\", RPZ_SEVERITY as \"RPZ Severity\", MITIGATION_ACTION as \"Mitigation Action\", RECORD_DATA as \"Substitute Addresses\" | table \"Client ID\", \"Total Client Hits\", \"Domain Name\", \"RPZ Entry\", \"RPZ Severity\", \"Total Rule Hits\", \"Mitigation Action\", \"Substitute Addresses\", Time"
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
	logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test1,results_list)
        logger.info("compare_results")
        result = compare_results(self.test1,results_list)
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg 

    def test_2_dns_top_rpz_hits_classes_filter(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
        search_str=r"search index=ib_dns_summary report=si_dns_rpz_hits * * * (orig_host=\"*\") *  RPZ_QNAME=\"*g.com.rpz_feed.com\" * * | eval DNS_VIEW =if(isnull(display_name), \"NULL\",display_name) | eval RECORD_DATA=if(isnull(RECORD_DATA),\"\",RECORD_DATA) | eval RPZ_QNAME=if(isnull(RPZ_QNAME),\"\",RPZ_QNAME) | eval RPZ_SEVERITY=if(isnull(RPZ_SEVERITY),\"\",RPZ_SEVERITY) | where MITIGATION_ACTION != \"ER\" | stats sum(COUNT) as QCOUNT by _time, CLIENT, DOMAIN_NAME, DNS_VIEW, orig_host, TOTAL_COUNT, MITIGATION_ACTION, RPZ_SEVERITY, RECORD_DATA RPZ_QNAME | stats sum(TOTAL_COUNT) as TOTAL_COUNT, sum(QCOUNT) as QCOUNT by _time, CLIENT, DOMAIN_NAME, DNS_VIEW, MITIGATION_ACTION, RPZ_SEVERITY, RECORD_DATA RPZ_QNAME | convert ctime(_time) as Time | eventstats earliest(Time) as \"MinTimeHit\", latest(Time) as \"MaxTimeHit\" BY CLIENT RPZ_QNAME DOMAIN_NAME RPZ_SEVERITY MITIGATION_ACTION RECORD_DATA | stats sum(TOTAL_COUNT) as TOTAL_COUNT,sum(QCOUNT) as QCOUNT  BY CLIENT RPZ_QNAME DOMAIN_NAME RPZ_SEVERITY MITIGATION_ACTION RECORD_DATA MinTimeHit MaxTimeHit |eventstats sum(TOTAL_COUNT) as \"Total Hits\" by CLIENT   | sort -QCOUNT  | head 10 | eval MITIGATION_ACTION=case(MITIGATION_ACTION == \"PT\", \"Passthru\", MITIGATION_ACTION == \"NX\", \"Block (No Such Domain)\", MITIGATION_ACTION == \"ND\", \"Block (No Data)\", MITIGATION_ACTION == \"SB\", \"Substitute\", MITIGATION_ACTION == \"A1\", \"Substitute (A)\", MITIGATION_ACTION == \"A4\", \"Substitute (AAAA)\", MITIGATION_ACTION == \"AA\", \"Substitute (A/AAAA)\", MITIGATION_ACTION == \"DN\", \"Substitute (Domain Name)\", MITIGATION_ACTION == \"ER\", \"Error\") | eval RPZ_SEVERITY=case(RPZ_SEVERITY == \"4\", \"INFORMATIONAL\", RPZ_SEVERITY == \"6\", \"WARNING\", RPZ_SEVERITY == \"7\", \"MAJOR\", RPZ_SEVERITY == \"8\",  \"CRITICAL\", RPZ_SEVERITY == \"\", \"\") | eval FEED_ZONE = substr(RPZ_QNAME, len(DOMAIN_NAME) + 2, len(RPZ_QNAME)) | lookup rpz_feed_tsig_key_lookup RPZ_FEED_ZONE AS FEED_ZONE OUTPUT TSIG_KEY | eval TSIG_KEY=if(isnull(TSIG_KEY),\"None\",TSIG_KEY) | rename CLIENT as \"Client ID\", QCOUNT as \"Total Client Hits\", DOMAIN_NAME as \"Domain Name\", TOTAL_COUNT as \"Total Rule Hits\", RPZ_QNAME as \"RPZ Entry\", RPZ_SEVERITY as \"RPZ Severity\", MITIGATION_ACTION as \"Mitigation Action\", RECORD_DATA as \"Substitute Addresses\" | table \"Client ID\", \"Total Hits\", \"Domain Name\", \"RPZ Entry\", \"RPZ Severity\", \"Total Rule Hits\", \"Mitigation Action\", \"Substitute Addresses\",\"MinTimeHit\",\"MaxTimeHit\", \"TSIG_KEY\" | rename \"Total Hits\" as \"Total Client Hits\""
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
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test2,results_list)
        logger.info("compare_results")
        result = compare_results(self.test2,results_list)
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg
    def test_3_dns_top_rpz_hits_classes_filter(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
        search_str=r"search index=ib_dns_summary report=si_dns_rpz_hits * DOMAIN_NAME=\"asm\" * (orig_host=\"*\")  *  *  *  * | eval DNS_VIEW =if(isnull(display_name), \"NULL\",display_name)      | eval RECORD_DATA=if(isnull(RECORD_DATA),\"\",RECORD_DATA) | eval RPZ_QNAME=if(isnull(RPZ_QNAME),\"\",RPZ_QNAME) | eval RPZ_SEVERITY=if(isnull(RPZ_SEVERITY),\"\",RPZ_SEVERITY) | where MITIGATION_ACTION != \"ER\" | stats sum(COUNT) as QCOUNT by _time, CLIENT, DOMAIN_NAME, DNS_VIEW, orig_host, TOTAL_COUNT, MITIGATION_ACTION, RPZ_SEVERITY, RECORD_DATA RPZ_QNAME | stats sum(TOTAL_COUNT) as TOTAL_COUNT, sum(QCOUNT) as QCOUNT by _time, CLIENT, DOMAIN_NAME, DNS_VIEW, MITIGATION_ACTION, RPZ_SEVERITY, RECORD_DATA RPZ_QNAME  | convert ctime(_time) as Time  | eventstats earliest(Time) as \"MinTimeHit\", latest(Time) as \"MaxTimeHit\"  BY CLIENT RPZ_QNAME DOMAIN_NAME RPZ_SEVERITY MITIGATION_ACTION RECORD_DATA | stats sum(TOTAL_COUNT) as TOTAL_COUNT,sum(QCOUNT) as QCOUNT BY CLIENT RPZ_QNAME DOMAIN_NAME RPZ_SEVERITY MITIGATION_ACTION RECORD_DATA MinTimeHit MaxTimeHit |eventstats sum(TOTAL_COUNT) as \"Total Hits\" by CLIENT    | sort -QCOUNT | head 10 | eval MITIGATION_ACTION=case(MITIGATION_ACTION == \"PT\", \"Passthru\", MITIGATION_ACTION == \"NX\", \"Block (No Such Domain)\", MITIGATION_ACTION == \"ND\", \"Block (No Data)\", MITIGATION_ACTION == \"SB\", \"Substitute\", MITIGATION_ACTION == \"A1\", \"Substitute (A)\", MITIGATION_ACTION == \"A4\", \"Substitute (AAAA)\", MITIGATION_ACTION == \"AA\", \"Substitute (A/AAAA)\", MITIGATION_ACTION == \"DN\", \"Substitute (Domain Name)\", MITIGATION_ACTION == \"ER\", \"Error\") | eval RPZ_SEVERITY=case(RPZ_SEVERITY == \"4\", \"INFORMATIONAL\", RPZ_SEVERITY == \"6\", \"WARNING\", RPZ_SEVERITY == \"7\", \"MAJOR\", RPZ_SEVERITY == \"8\",  \"CRITICAL\", RPZ_SEVERITY == \"\", \"\")  | eval FEED_ZONE = substr(RPZ_QNAME, len(DOMAIN_NAME) + 2, len(RPZ_QNAME))             | lookup rpz_feed_tsig_key_lookup RPZ_FEED_ZONE AS FEED_ZONE OUTPUT TSIG_KEY | eval TSIG_KEY=if(isnull(TSIG_KEY),\"None\",TSIG_KEY) | rename CLIENT as \"Client ID\", QCOUNT as \"Total Client Hits\", DOMAIN_NAME as \"Domain Name\", TOTAL_COUNT as \"Total Rule Hits\", RPZ_QNAME as \"RPZ Entry\", RPZ_SEVERITY as \"RPZ Severity\", MITIGATION_ACTION as \"Mitigation Action\", RECORD_DATA as \"Substitute Addresses\" | table \"Client ID\", \"Total Hits\", \"Domain Name\", \"RPZ Entry\", \"RPZ Severity\", \"Total Rule Hits\", \"Mitigation Action\",\"Substitute Addresses\",\"MinTimeHit\",\"MaxTimeHit\", \"TSIG_KEY\" | rename \"Total Hits\" as \"Total Client Hits\""
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
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test3,results_list)
        logger.info("compare_results")
        result = compare_results(self.test3,results_list)
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg


    @classmethod
    def teardown_class(cls):
       logger.info('-'*15+"END::DNS Top RPZ Hits"+'-'*15)


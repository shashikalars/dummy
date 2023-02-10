"""
 Copyright (c) Infoblox Inc., 2016
 ReportName          : DNS Top Clients
 ReportCategory      : DNS Query 
 Number of Test cases: 1
 Execution time      : 302.61 seconds
 Execution Group     : Hour Group (HG)
 Description         : DNS Top Clients, This report will be udpated every one hour

 Author : Raghavendra MN
 History: 05/26/2016 (Created)
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
from time import sleep

import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from logger import logger
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results

"""
TEST Steps:
      1.  Input/Preparation  : Prparation will be called by separte script as reports will be updated every one hour 
          a.Adding zones say 'dns_top_clients.com' and RR's.
          b.Next performing Query from differnt Clients
            Client#1: 10000
	    Client#2: 11000
	    Client#3: 12000
	    Client#4: 13000
	    Client#5  14000
      2.  Search     : Performing Search operaion with default/custom filter
      3.  Validation : comparing Search results with Reterived 'DNS Top Clients per Domain' report without delta.
"""

class DNSTopClients(unittest.TestCase):
    @classmethod
    #Preparation
    def setup_class(cls):
        logger.info('-'*15+"START:DNS Top Clients"+'-'*15)
        logger.info ("Preparation has executed 1 hour before as this report will take 1 hour to update")
        cls.test1=[]
        temp={}
        temp["Queries"]="10000"
        temp["CLIENT"]=config.client_eth1_ip1
        cls.test1.append(temp)

        temp={}
        temp["Queries"]="11000"
        temp["CLIENT"]=config.client_eth1_ip2
        cls.test1.append(temp)

        temp={}
        temp["Queries"]="12000"
        temp["CLIENT"]=config.client_eth1_ip3
        cls.test1.append(temp)

        temp={}
        temp["Queries"]="13000"
        temp["CLIENT"]=config.client_eth1_ip4
        cls.test1.append(temp)

      # temp={}
      # temp["Queries"]="14000"
      # temp["CLIENT"]=config.client_eth1_ip5
      # cls.test1.append(temp)

        logger.info ("Input Json for validation")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))

    def test_1_Default_Filter_validate_DNS_Top_Clients(self):
        logger.info("TestCase:test_1_Default_Filter_validate_DNS_Top_Clients_per_Domain")
        search_str=r"search index=ib_dns_summary report=si_dns_top_clients | stats sum(COUNT) as CLIENT_QUERIES by CLIENT | sort -CLIENT_QUERIES | head 10 | eventstats sum(CLIENT_QUERIES) as TOTAL | eval PERCENT=round(CLIENT_QUERIES*100/TOTAL,1) | eval PCLIENT=CLIENT+\" (\"+PERCENT+\"%)\" | rename PCLIENT as Client, CLIENT_QUERIES as Queries"
        cmd = config.search_py + " \"" + search_str + "\" --output_mode=json"
        logger.info (cmd)
        os.system(cmd)
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Looks like reporting service not started please check the GRID")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        logger.info("Appending % value in Client name")
        M=self.test1
        L=results_list
        tot=0
        for H in L:
            tot+= int(H["Queries"])
        temp_test1=[]
        for N in M:
            comp_dict={}
            per="{0:.1f}".format((float(N["Queries"])/tot)*100)
            comp_dict["Client"]=N["CLIENT"]+" ("+per+"%)"
            comp_dict["CLIENT"]=N["CLIENT"]
            comp_dict["Queries"]=N["Queries"]
            temp_test1.append(comp_dict)
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",temp_test1,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        result = compare_results(temp_test1,results_list)
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg


    #Clean up
    @classmethod
    def teardown_class(cls):
        #deleting zones
        logger.info("Cleanup: Removing zones which was added in preparation step.")
        #del_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn~=dns_top_clients.com")
        #ref = json.loads(del_zone)[0]['_ref']
        #del_status = ib_NIOS.wapi_request('DELETE', object_type = ref)
        logger.info('-'*15+"END:DNS Top Clients"+'-'*15)

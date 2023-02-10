"""
 Copyright (c) Infoblox Inc., 2016

 ReportName          : DNS Scavenge Object Count Trend
 ReportCategory      : DNS Scavenge
 Number of Test cases: 1
 Execution time      : 556.90 seconds
 Execution Group     : Minute Group (MG)
 Description         : 'DNS Scavenge Object Count Trend' report will updated every one min. 

 Authora  : Raghavendra MN
 History  : 06/07/2016 (Created)
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
import time
import unittest
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
import ib_utils.ib_papi as papi
from logger import logger
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results

"""
TEST Steps:
      1.  Input/Preparaiton      : Adding zones, RR's in different view through CSV and next performing 'DNS Scavenge' operaiton. 
      2.  Search                 : Performing Search operaion with default/custom filter
      3.  Validation             : validating Search Results against scavenge data.
"""

class DNSScavengeObjectCountTrend(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        logger.info('-'*15+"START:DNS Scavenge Object Count Trend"+'-'*15)
        logger.info("Preparation: DNS Scavenge")

        logger.info("Add NSG 'nsg_scavenging'")
        data = {"name":"nsg_scavenging","grid_primary":[{"name": config.grid_fqdn,"stealth": False}], \
        "grid_secondaries":[{"name": config.grid_member1_fqdn,"stealth": False}]}
        response = ib_NIOS.wapi_request('POST', object_type="nsgroup", fields=json.dumps(data))

        logger.info("Add Views, Zones & RR's through CSV")
        papi.import_csv('ib_data/DNS_Scavenge/dns_scavenging_view_1_nsg.csv')     
        papi.import_csv('ib_data/DNS_Scavenge/dns_scavenging_view_2_nsg.csv')     
     
        logger.info("Wait 120 sec., for CSV import operation.")
        time.sleep(120)

        epoc=ib_get.indexer_epoch_time(config.indexer_ip)
        minute=int(time.strftime('%M',time.gmtime(int(epoc))))
        t=minute%10
        wait_time = 0 if t<=1 else (11-t)*60

        logger.info("Enable DNS Scavenge in View level")
        cw=os.getcwd()
        os.chdir('ib_data/DNS_Scavenge/')
        os.system("perl enable_scavening_view.pl "+config.grid_vip)
        logger.info("Run Reclamation, after %d sec",wait_time)
        time.sleep(wait_time)
        os.system("perl run_reclamation.pl "+config.grid_vip)
        os.chdir(cw)
 
        logger.info("Input file for test#1")
        cls.test1=[{ \
        "0.0.0.0.0.0.0.0.0.0.0.0.2.2.1.1.ip6.arpa (view1)":"20.000000", \
        "0.0.0.0.0.0.0.0.0.0.0.0.2.2.2.2.ip6.arpa (view2)":"20.000000", \
        "23.in-addr.arpa (view1)":"40.000000", \
        "24.in-addr.arpa (view2)":"40.000000", \
        "dnsscavenging.com (view1)":"79.000000", \
        "dnsscavenging1.com (view2)":"79.000000"}]
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))


        logger.info("Input file for test#2")
        cls.test2=[{ \
        "0.0.0.0.0.0.0.0.0.0.0.0.2.2.1.1.ip6.arpa (view1)":"20.000000", \
        "23.in-addr.arpa (view1)":"40.000000", \
        "dnsscavenging.com (view1)":"79.000000"}]
        logger.info(json.dumps(cls.test2, sort_keys=True, indent=4, separators=(',', ': ')))

        logger.info("Input file for test#3")
        cls.test3=[{ "23.in-addr.arpa (view1)":"40.000000" }]
        logger.info(json.dumps(cls.test3, sort_keys=True, indent=4, separators=(',', ': ')))
        

        logger.info("Waiting for 180 sec.,")
        time.sleep(180) #wait for report update

    def test_1_dns_scavenge_object_count_trend_default_filter(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
        search_str=r"search source=ib:dns:reclamation index=ib_dns | bucket span=10m _time  | eval ZONE=zone_name+\" (\"+view+\")\" | stats sum(rr_reclaimed) as RRR by _time ZONE | timechart bins=1000 avg(RRR) by ZONE where max in top10 useother=f"

        cmd = config.search_py + " \"" + search_str + "\" --output_mode=json"
        os.system(cmd)
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Looks like reporting service not started please check the GRID")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test1,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        result = compare_results(self.test1,results_list)
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg



    def test_2_dns_scavenge_object_count_trend_view_filter(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
        search_str=r"search source=ib:dns:reclamation index=ib_dns (view=\"view1\") | bucket span=10m _time  | eval ZONE=zone_name+\" (\"+view+\")\" | stats sum(rr_reclaimed) as RRR by _time ZONE | timechart bins=1000 avg(RRR) by ZONE where max in top10 useother=f"

        cmd = config.search_py + " \"" + search_str + "\" --output_mode=json"
        os.system(cmd)
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Looks like reporting service not started please check the GRID")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test2,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        result = compare_results(self.test2,results_list)
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg



    def test_3_dns_scavenge_object_count_trend_zone_filter(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
        search_str=r"search source=ib:dns:reclamation index=ib_dns (zone_name=\"23.in-addr.arpa\") | bucket span=10m _time  | eval ZONE=zone_name+\" (\"+view+\")\" | stats sum(rr_reclaimed) as RRR by _time ZONE | timechart bins=1000 avg(RRR) by ZONE where max in top5 useother=f"

        cmd = config.search_py + " \"" + search_str + "\" --output_mode=json"
        os.system(cmd)
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Looks like reporting service not started please check the GRID")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test3,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        result = compare_results(self.test3,results_list)
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg


    @classmethod
    def teardown_class(cls):

        logger.info("Cleanup, Removing added DNS View & NSG") 
        del_view = ib_NIOS.wapi_request('GET', object_type="view?name~=view1")
        ref = json.loads(del_view)[0]['_ref']
        del_status = ib_NIOS.wapi_request('DELETE', object_type = ref)

        del_view = ib_NIOS.wapi_request('GET', object_type="view?name~=view2")
        ref = json.loads(del_view)[0]['_ref']
        del_status = ib_NIOS.wapi_request('DELETE', object_type = ref)

        del_nsg = ib_NIOS.wapi_request('GET', object_type="nsgroup?name~=nsg_scavenging")
        ref = json.loads(del_nsg)[0]['_ref']
        del_status = ib_NIOS.wapi_request('DELETE', object_type = ref)
        logger.info('-'*15+"END:DNS Scavenge Object Count Trend"+'-'*15)

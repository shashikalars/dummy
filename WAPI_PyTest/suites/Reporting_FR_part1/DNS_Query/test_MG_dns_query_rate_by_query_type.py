"""
 Copyright (c) Infoblox Inc., 2016

 ReportName          : DNS Query Rate By Query Type
 ReportCategory      : DNS Query
 Number of Test cases: 1
 Execution time      : 361.09 seconds
 Execution Group     : Minute Group (MG)
 Description         : DNS 'Query Rate by Query Type' report update every 1 min. 

 Author   : Raghavendra MN
 History  : 05/30/2016 (Created)
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
from logger import logger
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results
import ib_data
"""
TEST Steps:
      1.  Input/Preparaiton      : Adding Zones and RR's and Performing Query
      2.  Search                 : Search with Default Filter 
      3.  Validation             : Validating Search result against input data
"""
path=os.getcwd()
class DNSQueryRateByQueryType(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        logger.info('-'*15+"START:DNS Query Rate By Query Type"+'-'*15)
        logger.info("Adding Zoens and RR's through CSV")
        cw=os.getcwd()
        print(cw)
        #os.chdir('/ib_data/DNS_Query/DNS_QRQT')
        os.chdir(path+'/ib_data/DNS_Query/DNS_QRQT')
        os.system("perl generate_csv.pl  "+config.grid_fqdn+" zones.csv")
        os.system("perl import_CSV.pl "+config.grid_vip+" zones.csv")
        logger.info("Wait for 120 sec., CSV import operation")
        time.sleep(120)

        logger.info("Performing service restart operation")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        logger.info("Wait for 60 sec., for restart operation")
        time.sleep(60) 

        epoch=int(ib_get.indexer_epoch_time(config.indexer_ip))
        sleep_sec = 60-int(time.strftime('%S', time.gmtime(epoch)))
        logger.info("Waiting for %d sec., to for QueryPerf execution",sleep_sec)
        time.sleep(sleep_sec)


        logger.info("Performing Query through Query perf")
        os.system("perl generate_query.pl");
        #fp=os.popen("~/dduq/dduq -i "+config.grid_vip+" -f input.txt")
	fp=os.popen("~/API_Automation/WAPI_PyTest/suites/Reporting_FR_part1/dduq/dduq -i "+config.grid_vip+" -f input.txt")
        logger.info("%s",''.join(fp.readlines()))
        os.chdir(cw)
        """ 
        cls.test1=[]
        temp={}
        new_time = time.strftime('%Y-%m-%dT%H:%M', time.gmtime(epoch+sleep_sec))
        #temp["_time"]= new_time+":00.000+00:00"  #ib_get.indexer_date(config.indexer_ip)
  #     temp["A"]="10.0666667"
        temp["A"]="8"  
        temp["AAAA"]="8.00000000"
        temp["CNAME"]= "6.00000000"
        temp["DNAME"]= "4.00000000"
        temp["MX"]="6.00000000"
        temp["NAPTR"]="4.00000000"
        temp["SRV"]= "4.00000000"
        temp["TXT"]= "6.00000000"
        cls.test1.append(temp)
        logger.info ("Input Json for validation")
        """
        cls.test1=[]
        temp={}
        #new_time = time.strftime('%Y-%m-%dT%H:%M', time.gmtime(epoch+sleep_sec))
        #temp["_time"]= new_time+":00.000+00:00"  #ib_get.indexer_date(config.indexer_ip)
       
        temp["A"]="8"
        temp["AAAA"]="8"
        temp["CNAME"]= "6"
        temp["DNAME"]= "4"
        temp["MX"]="6"
        #temp["NAPTR"]="4"
        #temp["SRV"]= "4"
        #temp["TXT"]= "6"
        cls.test1.append(temp)
        logger.info ("Input Json for validation")

        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))
        print(cls)
        logger.info ("Waiting for 5  min., for updating reports")
        time.sleep(600) #wait till reports gets udpated
        #time.sleep(60)
        #print("------------jjj")
    def test_1_dns_query_rate_by_query_tye_validate_query_rate_for_a_aaaa_cname_dname_mx_naptr_srv_txt_records(self):
        
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
        
        #search_str="search sourcetype=ib:dns:query:qps index=ib_dns | lookup dns_viewkey_displayname_lookup VIEW output display_name | bucket span=1m _time | stats sum(COUNT) as QPM by _time TYPE | timechart limit=18 bins=1000 eval(avg(QPM)/60) by TYPE useother=f"
        search_str="search sourcetype=ib:dns:query:qps index=ib_dns | lookup dns_viewkey_displayname_lookup VIEW output display_name | bucket span=5m _time | stats sum(COUNT) as QPM by _time TYPE | timechart limit=18 bins=1000 eval(avg(QPM)/60) by TYPE useother=f | fields A,AAAA,CNAME,DNAME,MX"

        #cmd = config.search_py + " \"" + search_str + "\" --output_mode=json"
        print(config)
        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        
        print("---------------------------------hhh")
        print(cmd)
        print(os.system("date"))
        print(os.system(cmd))
        print("%%%%%%%%%%%%%%%%%")
        try:
            retrived_data=open(config.json_file).read()
            #print(retrived_data)
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']

        '''
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        print(results_dist)
        first=results_dist[0]
        print(first)
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

        if first['A'] >= 0 and first['AAAA'] >= 0:
            print("--------------***********----------------")
            print("PASSED")
            logger.info("Search validation result: %s(PASS)",first)
            assert True

        else:
            logger.error("Search validation result: %s(FAIL)",first)

            msg = 'Count does not match - %s', first
            assert False

	'''

        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test1,results_dist)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 2")
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
        logger.info("Cleanup, Deleting Added zones")
        del_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn~=qrqt1.com")
        ref = json.loads(del_zone)[0]['_ref']
        del_status = ib_NIOS.wapi_request('DELETE', object_type = ref)

        del_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn~=qrqt2.com")
        ref = json.loads(del_zone)[0]['_ref']
        del_status = ib_NIOS.wapi_request('DELETE', object_type = ref)
        logger.info('-'*15+"END:DNS Query Rate By Query Type"+'-'*15)


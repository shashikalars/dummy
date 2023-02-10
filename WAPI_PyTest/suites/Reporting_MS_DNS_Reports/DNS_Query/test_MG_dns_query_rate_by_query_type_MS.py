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
        '''
	logger.info("Adding Zoens and RR's through CSV")
        cw=os.getcwd()
        print("----------Current Directory-------")
	print(cw)
        os.chdir(path+'/ib_data/DNS_Query/DNS_QRQT')
        f = os.system("perl generate_csv.pl  "+config.grid_ms_fqdn+" zones.csv")
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$",f)
	os.system("perl import_CSV.pl "+config.grid_ms_ip+" zones.csv")
        logger.info("Wait for 120 sec., CSV import operation")
        #time.sleep(120)

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

	'''

        logger.info("Performing Query through Query perf")
        
	fp=os.popen("dig @"+config.grid_ms_ip+" -f /import/qaddi/API_Automation_08_12_20/WAPI_PyTest/suites/Reporting_MS_DNS_Reports/ib_data/DNS_Query/DNS_Top_Requested_Domain_Names/top_requested_domains.txt")
	print(fp)
	logger.info("%s",''.join(fp.readlines()))
        
	cls.test1=[]
      	temp={} 
        #temp["A"]="0.13333333333333333"
        #temp["AAAA"]="0.21666666666666667"
        #temp["HINFO"]= "0.3333333333333333"
        temp["HINFO"]= "0.16666666666666666"
	cls.test1.append(temp)
        logger.info ("Input Json for validation")

        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))
        print(cls)
        logger.info ("Waiting for 10  min., for updating reports")
        time.sleep(600) #wait till reports gets udpated
    
    def test_1_dns_query_rate_by_query_type(self):
        
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
        
        #search_str="search sourcetype=ib:dns:query:qps index=ib_dns | lookup dns_viewkey_displayname_lookup VIEW output display_name | bucket span=5m _time | stats sum(COUNT) as QPM by _time TYPE | timechart limit=18 bins=1000 eval(avg(QPM)/60) by TYPE useother=f | fields \"A\",\"AAAA\", \"HINFO\""

	search_str="search sourcetype=ib:dns:query:qps index=ib_dns | lookup dns_viewkey_displayname_lookup VIEW output display_name | bucket span=5m _time | stats sum(COUNT) as QPM by _time TYPE | timechart limit=18 bins=1000 eval(avg(QPM)/60) by TYPE useother=f | table A, AAAA | where AAAA > 1"       
 
        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        print("EXECUTION OF SEARCH STRING COMMAND",cmd)
 
        print(os.system(cmd))
        print("%%%%%%%%%%%%%%%%%")

        try:
            retrived_data=open(config.json_file).read()
            print(retrived_data)

        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']

        results_dist= results_list[-240::1]
	print('#####################',results_dist)
        '''
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test1,results_dist)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 2")
        result = compare_results(self.test1,results_list,2)
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
	

    '''
    @classmethod
    def teardown_class(cls):
        logger.info("Cleanup, Deleting Added zones")

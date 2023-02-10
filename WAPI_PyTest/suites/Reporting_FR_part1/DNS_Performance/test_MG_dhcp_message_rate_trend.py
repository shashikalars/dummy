"""
 Copyright (c) Infoblox Inc., 2016

 ReportName          : DHCP Message Rate Trend
 ReportCategory      : DHCP Performance
 Number of Test cases: 4
 Execution time      : 302.61 seconds
 Execution Group     : Minute Group (MG)
 Description         : DHCP Message Rate Trend report will be updated every one min

 Author   : Raghavendra MN
 History  : 05/31/2016 (Created)
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
import unittest
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from logger import logger
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results
"""
TEST Steps:
      1.  Input/Preparaiton      : Add Network 10.0.0.0/8 and Range 10.0.0.200-10.0.0.201
				   Next using dras command request 100 leases
      2.  Search                 : Performing Search operaion with default/custom filter
      3.  Validation             : comparing Search results with Reterived CPU utilization (with delta 10).
"""



class DHCPMessageRateTrend(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        logger.info('-'*15+"START:DHCP Message Rate Trend"+'-'*15)
        cls.test1=[]
        cls.test2=[]
        cls.test3=[]
        cls.test4=[]
        print(config.grid_vip)
        logger.info("Adding 10.0.0.0/8 Network")
        net_obj = {"members":[{"_struct": "dhcpmember", "ipv4addr":config.grid_vip ,"name":config.grid_fqdn}], \
                "network": "10.0.0.0/8", "network_view": "default"}
        network1 = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(net_obj))
        print(network1)
        logger.info("Adding Range 10.0.0.101-10.0.0.110")
        range_obj = {"start_addr":"10.0.0.101","end_addr":"10.0.0.110","member":{"_struct": "dhcpmember","ipv4addr":config.grid_vip,"name": config.grid_fqdn}, \
                 "options":[{"_struct": "dhcpoption","name":"dhcp-lease-time","num": 51,"use_option": True,"value": "120","vendor_class": "DHCP"}]}
                 #value=43200
        range = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(range_obj)) 
        print(range)
        logger.info("Performing Restart operation")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref'] 
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        logger.info("Waiting 30 sec., for Member Restart")
        sleep(120) #wait for 30 sec, for Member Restart

        #Preparation for Test1  
        logger.info("Requesting 20 leases using dras command")
        fp=os.popen("sudo /import/tools/qa/tools/dras/dras -i "+config.grid_vip+" -n 20 -x l=10.0.0.0")
        #fp=os.popen("sudo /import/tools/qa/tools/dras/dras -i "+config.grid_vip+" -n 20")
        logger.info(''.join(fp.readlines()))
        print(fp.read())
        print("---using dras command------")
        temp={}
        #temp["DHCPDISCOVER"]='20.000000'
        #temp["DHCPDISCOVER"]='10.000000'
        temp["DHCPOFFER"]='10.000000'
        temp["DHCPREQUEST"]='10.000000'
        temp["DHCPACK"]='10.000000'
        cls.test1.append(temp)
        logger.info("Creating json input for test1")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))
        logger.info("Wait for 120 sec.,")
        sleep(120) #wait for Report update
        #Preparation for Test2
        temp={}
        temp["DHCPDISCOVER"]='20.000000'
        #temp["DHCPDISCOVER"]='10.000000'
        cls.test2.append(temp)
        logger.info("Creating json input for test2")
        logger.info(json.dumps(cls.test2, sort_keys=True, indent=4, separators=(',', ': ')))
        #Preparation for Test3
        temp={}
        temp["DHCPOFFER"]='10.000000'
        cls.test3.append(temp)
        logger.info("Creating json input for test3")
        logger.info(json.dumps(cls.test3, sort_keys=True, indent=4, separators=(',', ': ')))
        
        temp={}
        temp["DHCPACK"]='10.000000'
        cls.test4.append(temp)
        logger.info("Creating json input for test4")
        logger.info(json.dumps(cls.test4, sort_keys=True, indent=4, separators=(',', ': ')))
	sleep(100)
    def test_1_dhcp_message_rate_trend_default_filter(self):
        logger.info("Test case:"+sys._getframe().f_code.co_name)
        #search_str="search sourcetype=ib:dhcp:message index=ib_dhcp | rex \"^[^,]*,(?<PROTO>[46])(,(?<COUNT1>\d+))?(,(?<COUNT2>\d+))?(,(?<COUNT3>\d+))?(,(?<COUNT4>\d+))?(,(?<COUNT5>\d+))?(,(?<COUNT6>\d+))?(,(?<COUNT7>\d+))?(,(?<COUNT8>\d+))?(,(?<COUNT9>\d+))?(,(?<COUNT10>\d+))?(,(?<COUNT11>\d+))?(,(?<COUNT12>\d+))?(,(?<COUNT13>\d+))?(,(?<COUNT14>\d+))?(,(?<COUNT15>\d+))?\" | eval Protocol=if(PROTO==\"6\",\"IPV6\",\"IPV4\") | bucket span=1m _time | stats sum(eval(if(PROTO==\"4\",COUNT1,0))) as v4discover, sum(eval(if(PROTO==\"4\",COUNT2,0))) as v4offer, sum(eval(if(PROTO==\"4\",COUNT3,0))) as v4request, sum(eval(if(PROTO==\"4\",COUNT5,0))) as v4ack by _time | timechart bins=1000 avg(v4discover) as DHCPDISCOVER, avg(v4offer) as DHCPOFFER, avg(v4request) as DHCPREQUEST, avg(v4ack) as DHCPACK"
        
        search_str="search sourcetype=ib:dhcp:message index=ib_dhcp | rex \"^[^,]*,(?<PROTO>[46])(,(?<COUNT1>\d+))?(,(?<COUNT2>\d+))?(,(?<COUNT3>\d+))?(,(?<COUNT4>\d+))?(,(?<COUNT5>\d+))?(,(?<COUNT6>\d+))?(,(?<COUNT7>\d+))?(,(?<COUNT8>\d+))?(,(?<COUNT9>\d+))?(,(?<COUNT10>\d+))?(,(?<COUNT11>\d+))?(,(?<COUNT12>\d+))?(,(?<COUNT13>\d+))?(,(?<COUNT14>\d+))?(,(?<COUNT15>\d+))?\" | eval Protocol=if(PROTO==\"6\",\"IPV6\",\"IPV4\") | bucket span=1m _time | stats sum(eval(if(PROTO==\"4\",COUNT1,0))) as v4discover, sum(eval(if(PROTO==\"4\",COUNT2,0))) as v4offer, sum(eval(if(PROTO==\"4\",COUNT3,0))) as v4request, sum(eval(if(PROTO==\"4\",COUNT5,0))) as v4ack by _time | timechart bins=1000 avg(v4discover) as DHCPDISCOVER, avg(v4offer) as DHCPOFFER, avg(v4request) as DHCPREQUEST, avg(v4ack) as DHCPACK"
        
        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        print(os.system(cmd))
        print("*****************%%%%%*********************")
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        logger.info("-----------------------------------------------------")
        logger.info(self.test1)
        logger.info(len(self.test1))
        logger.info("--------------Adding Debugging line ------------------")
        logger.info(results_list)
        logger.info(len(results_list))
        logger.info("-----------------------------------------------------")
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

    def test_2_dhcp_message_rate_trend_filter_eq_DHCP_DISCOVER(self):
        logger.info("Test case:"+sys._getframe().f_code.co_name)
        search_str="search sourcetype=ib:dhcp:message index=ib_dhcp | rex \"^[^,]*,(?<PROTO>[46])(,(?<COUNT1>\d+))?(,(?<COUNT2>\d+))?(,(?<COUNT3>\d+))?(,(?<COUNT4>\d+))?(,(?<COUNT5>\d+))?(,(?<COUNT6>\d+))?(,(?<COUNT7>\d+))?(,(?<COUNT8>\d+))?(,(?<COUNT9>\d+))?(,(?<COUNT10>\d+))?(,(?<COUNT11>\d+))?(,(?<COUNT12>\d+))?(,(?<COUNT13>\d+))?(,(?<COUNT14>\d+))?(,(?<COUNT15>\d+))?\" | eval Protocol=if(PROTO==\"6\",\"IPV6\",\"IPV4\") | bucket span=1m _time | stats sum(eval(if(PROTO==\"4\",COUNT1,0))) as v4discover, sum(eval(if(PROTO==\"4\",COUNT2,0))) as v4offer, sum(eval(if(PROTO==\"4\",COUNT3,0))) as v4request, sum(eval(if(PROTO==\"4\",COUNT5,0))) as v4ack by _time | timechart bins=1000 avg(v4discover) as DHCPDISCOVER"
        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        print(os.system(cmd))
        print("*****************%%%%%*********************")
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test2,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        result = compare_results(self.test2,results_list)
        logger.info("-----------------------------------------------------")
        logger.info(self.test2)
        logger.info(len(self.test2))
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

    def test_3_dhcp_message_rate_trend_filter_DHCP_OFFER(self):
        logger.info("Test case:"+sys._getframe().f_code.co_name)
        search_str="search sourcetype=ib:dhcp:message index=ib_dhcp | rex \"^[^,]*,(?<PROTO>[46])(,(?<COUNT1>\d+))?(,(?<COUNT2>\d+))?(,(?<COUNT3>\d+))?(,(?<COUNT4>\d+))?(,(?<COUNT5>\d+))?(,(?<COUNT6>\d+))?(,(?<COUNT7>\d+))?(,(?<COUNT8>\d+))?(,(?<COUNT9>\d+))?(,(?<COUNT10>\d+))?(,(?<COUNT11>\d+))?(,(?<COUNT12>\d+))?(,(?<COUNT13>\d+))?(,(?<COUNT14>\d+))?(,(?<COUNT15>\d+))?\" | eval Protocol=if(PROTO==\"6\",\"IPV6\",\"IPV4\") | bucket span=1m _time | stats sum(eval(if(PROTO==\"4\",COUNT1,0))) as v4discover, sum(eval(if(PROTO==\"4\",COUNT2,0))) as v4offer, sum(eval(if(PROTO==\"4\",COUNT3,0))) as v4request, sum(eval(if(PROTO==\"4\",COUNT5,0))) as v4ack by _time | timechart bins=1000 avg(v4offer) as DHCPOFFER"
        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        print(os.system(cmd))
        print("*****************%%%%%*********************")
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test3,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        result = compare_results(self.test3,results_list)
        logger.info("-----------------------------------------------------")
        logger.info(self.test3)
        logger.info(len(self.test3))
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

    def test_4_dhcp_message_rate_trend_default_filter_DHCP_ACK(self):
        logger.info("Test case:"+sys._getframe().f_code.co_name)
        search_str="search sourcetype=ib:dhcp:message index=ib_dhcp | rex \"^[^,]*,(?<PROTO>[46])(,(?<COUNT1>\d+))?(,(?<COUNT2>\d+))?(,(?<COUNT3>\d+))?(,(?<COUNT4>\d+))?(,(?<COUNT5>\d+))?(,(?<COUNT6>\d+))?(,(?<COUNT7>\d+))?(,(?<COUNT8>\d+))?(,(?<COUNT9>\d+))?(,(?<COUNT10>\d+))?(,(?<COUNT11>\d+))?(,(?<COUNT12>\d+))?(,(?<COUNT13>\d+))?(,(?<COUNT14>\d+))?(,(?<COUNT15>\d+))?\" | eval Protocol=if(PROTO==\"6\",\"IPV6\",\"IPV4\") | bucket span=1m _time | stats sum(eval(if(PROTO==\"4\",COUNT1,0))) as v4discover, sum(eval(if(PROTO==\"4\",COUNT2,0))) as v4offer, sum(eval(if(PROTO==\"4\",COUNT3,0))) as v4request, sum(eval(if(PROTO==\"4\",COUNT5,0))) as v4ack by _time | timechart bins=1000 avg(v4ack) as DHCPACK"
        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        print(os.system(cmd))
        print("*****************%%%%%*********************")
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test4,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        result = compare_results(self.test4,results_list)
        logger.info("-----------------------------------------------------")
        logger.info(self.test4)
        logger.info(len(self.test4))
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
        logger.info("Cleanup,deleting added network")
    	delnetwork = ib_NIOS.wapi_request('GET', object_type="network?network=10.0.0.0/8")
        ref = json.loads(delnetwork)[0]['_ref']
        del_status = ib_NIOS.wapi_request('DELETE', object_type = ref)
        logger.info('-'*15+"END:DHCP Message Rate Trend"+'-'*15)
        logger.info("Performing Restart operation")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref'] 
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        logger.info("Waiting 30 sec., for Member Restart")
        sleep(20)

import config
import json
import os
import pytest
import pexpect
import re
import sys
import subprocess
#import time
from time import sleep
import unittest
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from logger import logger
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results

class MS_Server(unittest.TestCase):
    @classmethod
    def setup_class(cls):

	logger.info("Validation of MS Server reports")


	cls.dhcp_usage_statistics = [{"Network view":"default","Network":"10.0.0.0","CIDR":"8","Ranges":"1","Provisioned":"200","Static":"0"},{"Network view":"default","Network":"20.0.0.0","CIDR":"24","Ranges":"1","Provisioned":"191","Static":"0"}]


    @pytest.mark.run(order=1)
    def test_001_dhcp_range_utilization(self):
        #SLEEPING FOR 14400 SECONDS TO VALIDATE THIS REPORT DUE TO DATA GENERATES 24 MINUTES PAST THE HOUR FOR EVERY 8 HOURS
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
	search_str="search index=ib_dhcp_summary report=si_dhcp_range_utilization_trend  | eval members=if(isnull(members), \"\", members) | eval ms_servers=if(isnull(ms_servers), \"\", ms_servers) | stats avg(dhcp_utilization) as ADU by _time view members ms_servers start_address end_address DHCP_RANGE dhcp_utilization_status | timechart bins=1000 eval(avg(ADU)/10) by DHCP_RANGE where max in top5 useother=f"

        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
	print("EXECUTION OF SEARCH STRING COMMAND",cmd)

        print(os.system(cmd))
        print("*****************%%%%%*********************")

        try:
            retrived_data=open(config.json_file).read()
            print(retrived_data)

        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
	
	results_dist= results_list[-540::1]

        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        print(results_dist)
        first=results_dist[0]
        print(first)

        if first['20.0.0.10-20.0.0.200'] >= 0 and first['10.0.0.1-10.0.0.200'] >=0:
            print("-----------------------------------------")
	    print("10.0.0.0 range utilization %:",first['10.0.0.1-10.0.0.200'])
            print("20.0.0.0 range utilization %:",first['20.0.0.10-20.0.0.200'])
            print("--------------***********----------------")
            print("Successfully PASSED")
            logger.info("Search validation result: %s (PASS)",first)

        else:
            logger.error("Search validation result: %s (FAIL)",first)

            msg = 'Count does not match - %s', first
            assert first == 0, first

	'''
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.dhcp_range_utilization,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%",self.dhcp_range_utilization)
        print("-------------------------------------")
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$",results_list)
        result = compare_results(self.dhcp_range_utilization,results_list)
        print("#####################################",result)

        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg
	
	'''

    @pytest.mark.run(order=2)
    def test_002_dhcp_usage_trend(self):
        #SLEEPING FOR 14400 SECONDS TO VALIDATE THIS REPORT DUE TO DATA GENERATES 24 MINUTES PAST THE HOUR FOR EVERY 8 HOURS
        logger.info("TestCase:"+sys._getframe().f_code.co_name)

	search_str = "search index=ib_dhcp_summary report=si_dhcp_usage_trend | eval members=if(isnull(members), \"\", members) | eval ms_servers=if(isnull(ms_servers), \"\", ms_servers) | stats avg(dynamic_hosts) as dynamic_hosts, avg(static_hosts) as static_hosts, avg(FREE_ADDRESSES) as FREE_ADDRESSES by _time view start_address end_address members ms_servers DHCP_RANGE | stats sum(dynamic_hosts) as dynamic_hosts, sum(static_hosts) as static_hosts, sum(FREE_ADDRESSES) as FREE_ADDRESSES by _time | timechart bins=1000 avg(dynamic_hosts) as Dynamic, avg(static_hosts) as Static, avg(FREE_ADDRESSES) as Free" 

        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
	print("EXECUTION OF SEARCH STRING COMMAND",cmd)

        print(os.system(cmd))
        print("*****************%%%%%*********************")

        try:
            retrived_data=open(config.json_file).read()
            print(retrived_data)

        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        results_dist= results_list[-540::1]

        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        print(results_dist)
        first=results_dist[0]
        print(first)
	print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
	sleep(5)

        if first['Dynamic'] >= 1 and first['Free'] >= 1 :
            print("-----------------------------------------")
            print("Dynamic IP count",first['Dynamic'])
	    print("Free IP count",first['Free'])
            print("--------------***********----------------")
            print("Successfully PASSED")
            logger.info("Search validation result: %s (PASS)",first)
            assert True

        else:
	
            logger.error("Search validation result: %s (FAIL)",first)
            msg = 'Count does not match - %s ', first
	    print("#################################",msg)
            assert False
	'''
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.dhcp_usage_trend,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%",self.dhcp_usage_trend)
        print("-------------------------------------")
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$",results_list)
        result = compare_results(self.dhcp_usage_trend,results_list)
        print("#####################################",result)

        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg
	'''

    @pytest.mark.run(order=3)
    def test_003_dhcp_usage_statistics(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)

	search_str = "search sourcetype=ib:dhcp:network index=ib_dhcp earliest=-8h | eval dedup_key=view.\"/\".address.\"/\".tostring(cidr) | dedup dedup_key | eval NETWORK=address.\"/\".cidr | lookup network_ea_lookup_csv NETWORK, NETWORK_VIEW as view output EA | spath input=EA output=MSSITE path=BUILTIN-MSSite | eval MSSITE = if(isnull(MSSITE), \"(no_value)\", MSSITE) | mvexpand MSSITE | mvcombine MSSITE | sort 0 -num(dhcp_utilization) | eval Free=address_total-dhcp_hosts | rename timestamp as Timestamp, view as \"Network view\", address as Network, cidr as CIDR, MSSITE as \"AD Site\", dhcp_utilization as \"DHCPv4 Utilization %\", ranges as Ranges, address_total as Provisioned, dhcp_hosts as Used, static_hosts as Static, dynamic_hosts as Dynamic | table Timestamp, \"Network view\", Network, CIDR, \"AD Site\", \"DHCPv4 Utilization %\", Ranges, Provisioned, Used, Static, Dynamic" 

        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
	print("EXECUTION OF SEARCH STRING COMMAND",cmd)

        print(os.system(cmd))
        print("*****************%%%%%*********************")


        try:
            retrived_data=open(config.json_file).read()
            print(retrived_data)

        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
	
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.dhcp_usage_statistics,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%",self.dhcp_usage_statistics)
        print("-------------------------------------")
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$",results_list)
        result = compare_results(self.dhcp_usage_statistics,results_list)
        print("#####################################",result)

        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg

    @pytest.mark.run(order=4)
    def test_004_top_lease_clients(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)

	search_str = "search index=ib_dhcp_summary report=si_dhcp_top_lease_client earliest=-8h | lookup os_number_fingerprint_lookup OS_NUMBER output SFP | eval FINGER_PRINT=if(isnull(OS_NUMBER) OR OS_NUMBER==0,FP,SFP) | stats count as COUNT by orig_host Protocol MAC_DUID ACTION, FINGER_PRINT | where ACTION=\"Issued\" or ACTION=\"Renewed\" or ACTION=\"Freed\" | lookup fingerprint_device_class_lookup FINGER_PRINT output DEVICE_CLASS | eval DEVICE_CLASS=if(isnull(DEVICE_CLASS), \"Modified or Deleted\", DEVICE_CLASS) | stats sum(eval(if(ACTION=\"Issued\",COUNT,0))) as Issued, sum(eval(if(ACTION=\"Renewed\",COUNT,0))) as Renewed, sum(eval(if(ACTION=\"Freed\",COUNT,0))) as Freed, sum(COUNT) as MacDuidTotal by MAC_DUID | sort 0 -num(MacDuidTotal) | head 10 | rename MAC_DUID as \"MAC/DUID\", MacDuidTotal as \"MAC/DUID Total\""

        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
	print("EXECUTION OF SEARCH STRING COMMAND",cmd)

        print(os.system(cmd))
        print("*****************%%%%%*********************")

        try:
            retrived_data=open(config.json_file).read()
            print(retrived_data)

        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        results_dist= results_list[-240::1]

	print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        print(results_dist)
        first=results_dist[0]
        print(first)
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

        if first['Issued'] >= 1 and first['Renewed'] >= 0 and first['MAC/DUID Total'] >= 1 and first['Freed'] >= 0:
            print("-----------------------------------------")
            print("Issued",first['Issued'])
            print("Renewed",first['Renewed'])
	    print("MAC/DUID Total",first['MAC/DUID Total'])
            print("Freed",first['Freed'])
            print("--------------***********----------------")
            print("Successfully PASSED")
            logger.info("Search validation result: %s (PASS)",first)
            assert True

        else:
            logger.error("Search validation result: %s (FAIL)",first)

            msg = 'Count does not match - %s', first
            assert False


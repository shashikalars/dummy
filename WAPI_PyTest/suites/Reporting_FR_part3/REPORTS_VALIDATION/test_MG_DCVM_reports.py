import config
import json
import os
import pytest
import pexpect
import re
import sys
import subprocess
from time import sleep
import time
import unittest
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from logger import logger
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results



class DCVM_reports(unittest.TestCase):

# DNS Domain Query Trend report

    @pytest.mark.run(order=1)
    def test_1_DNS_domain_query_trend(self):
    
        # Expected values

        logger.info ("Input Json Data for DNS Domain Query Trend report validation")
        

        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search sourcetype=ib:dns:capture index=ib_dns_capture | timechart minspan=5m count"
        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        logger.info (cmd)

        print(os.system(cmd))
        print("-------------%%%----------")
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operation failed, Please check Grid Configuration")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        results_dist= results_list[-240::1]
        
        print(results_dist)
        first=results_dist[0]
        print(first)
        print("-----------------------------------------")
        count=first['count']
        print(count)
        print("--------------***********----------------")

        if count >= 20:
            print("PASSED")
            logger.info("Search validation result: %s (PASS)",count)
        else:
            logger.error("Search validation result: %s (FAIL)",count)

            msg = 'Count is less than 20 - %s', count
            assert count == 0, msg
        


# DNS Domains Queried by Client report

    @pytest.mark.run(order=2)
    def test_2_DNS_domains_queried_by_client_report(self):
    
        # Expected values
        
        test2 = [{"Domain Name":"mx_record.flex.com","Query Type":"MX","Member":config.grid_member1_fqdn},{"Domain Name":"mx_record.source.com","Query Type":"MX","Member":config.grid_fqdn}]
        logger.info ("Input Json Data for DNS Domains Queried by Client report validation")
        logger.info(json.dumps(test2, sort_keys=True, indent=4, separators=(',', ': ')))

        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search sourcetype=ib:dns:capture index=ib_dns_capture | eval resolved_names_or_ips=coalesce(ms_resolved_names,ms_resolved_ips) | eval MS_SERVER = if (resolved_names_or_ips != \"\", resolved_names_or_ips, \"\" )  | eval host = if (MS_SERVER == \"\", host, \"\") | eval timestamp=strftime(_time,\"%Y-%m-%d %H:%M:%S\").\".\".time_msec | eval view=if(view==0,\"_default\",view) | lookup dns_viewkey_displayname_lookup VIEW as view output display_name as viewname | rename timestamp as \"Timestamp\", src_ip as \"Source IP Address\", query as \"Domain Name\", query_type as \"Query Type\", host as \"Member\", MS_SERVER as MSSERVER, viewname as \"View\" | table \"Timestamp\" \"Source IP Address\" \"Domain Name\" \"Query Type\" \"Member\" \"MSSERVER\" \"View\""

        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        logger.info (cmd)

        print(os.system(cmd))
        print("-------------%%%----------")
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operation failed, Please check Grid Configuration")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        results_dist= results_list[-240::1]
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",test2,results_dist)
        logger.info("compare_results with 'delta=1'")
        result = compare_results(test2,results_list,1)
        print(result)
        logger.info("-----------------------------------------------------")
        logger.info(test2)
        logger.info(len(test2))
        logger.info("--------------------**************-------------------")
        logger.info(results_list)
        logger.info(len(results_list))
        logger.info("-----------------------------------------------------")

        if result == 0:
            print("PASSED")
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg


# DNS Query Rate by Member report

    @pytest.mark.run(order=3)
    def test_3_DNS_query_rate_by_member(self):
        # Expected values
    
        test3 = [{config.grid_fqdn:"0.02"}]
        logger.info ("Input Json Data for DNS Query Rate by Member report validation")
        logger.info(json.dumps(test3, sort_keys=True, indent=4, separators=(',', ': ')))

        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search index=ib_dns_summary report=si_dns_member_qps_trend | lookup dns_viewkey_displayname_lookup VIEW output display_name | rename orig_host as host | eval source_host=if(MS_SERVER !=\"\", coalesce(ms_resolved_names,ms_resolved_ips),host) | stats sum(QCOUNT) as QCOUNT by _time source_host | timechart bins=1000 eval(avg(QCOUNT)/600) by source_host where max in top5 useother=f"

        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        logger.info (cmd)

        print(os.system(cmd))
        print("-------------%%%----------")
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operation failed, Please check Grid Configuration")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        results_dist= results_list[-240::1]
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",test3,results_dist)
        logger.info("compare_results with 'delta=1'")
        result = compare_results(test3,results_list,1)
        print(result)
        logger.info("-----------------------------------------------------")
        logger.info(test3)
        logger.info(len(test3))
        logger.info("--------------------**************-------------------")
        logger.info(results_list)
        logger.info(len(results_list))
        logger.info("-----------------------------------------------------")

        if result == 0:
            print("PASSED")
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg


# DNS Top Clients by Query Type report

    @pytest.mark.run(order=4)
    def test_4_DNS_top_clients_by_query_type(self):
    
        # Expected values
    
        logger.info ("Input Json Data for DNS Top Clients by Query Type report validation")

        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search sourcetype=ib:dns:capture index=ib_dns_capture (query_type=\"A\") query_source=I | stats count by src_ip | sort -count | head 10 | rename src_ip as \"Source IP Address\", count as \"Query Count\" | table \"Source IP Address\", \"Query Count\""
        
        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        logger.info (cmd)

        print(os.system(cmd))
        print("-------------%%%----------")
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operation failed, Please check Grid Configuration")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        results_dist= results_list[-240::1]
        
        print(results_dist)
        first=results_dist[0]
        print(first)
        print("-----------------------------------------")
        count=first['Query Count']
        print(count)
        print("--------------***********----------------")

        if count >= 20000:
            print("PASSED")
            logger.info("Search validation result: %s (PASS)",count)
        else:
            logger.error("Search validation result: %s (FAIL)",count)

            msg = 'Count is less than 20k - %s', count
            assert count == 0, msg


# DNS Top Clients Querying MX Records report
    '''
    @pytest.mark.run(order=5)
    def test_5_DNS_top_clients_querying_MX_record(self):
    
        # Expected values
    
        test5 = [{"Query Count":"22"}]
        logger.info ("Input Json Data for DNS Top Clients Querying MX Records report validation")
        logger.info(json.dumps(test5, sort_keys=True, indent=4, separators=(',', ': ')))


        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search sourcetype=ib:dns:capture index=ib_dns_capture (query_type=\"MX\") query_source=I | stats count by src_ip | sort -count | head 10 | rename src_ip as \"Source IP Address\", count as \"Query Count\" | table \"Source IP Address\", \"Query Count\""


        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        logger.info (cmd)

        print(os.system(cmd))
        print("-------------%%%----------")
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operation failed, Please check Grid Configuration")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        results_dist= results_list[-240::1]
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",test5,results_dist)
        logger.info("compare_results with 'delta=1'")
        result = compare_results(test5,results_list,1)
        print(result)
        logger.info("-----------------------------------------------------")
        logger.info(test5)
        logger.info(len(test5))
        logger.info("--------------------**************-------------------")
        logger.info(results_list)
        logger.info(len(results_list))
        logger.info("-----------------------------------------------------")

        if result == 0:
            print("PASSED")
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg
        '''
        
# DNS Top Clients Querying MX Records report

    @pytest.mark.run(order=5)
    def test_5_DNS_top_clients_querying_MX_record(self):

        # Expected values

        logger.info ("Input Json Data for DNS Top Clients Querying MX Records report validation")

        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search sourcetype=ib:dns:capture index=ib_dns_capture (query_type=\"MX\") query_source=I | stats count by src_ip | sort -count | head 10 | rename src_ip as \"Source IP Address\", count as \"Query Count\" | table \"Source IP Address\", \"Query Count\""

        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        logger.info (cmd)

        print(os.system(cmd))
        print("-------------%%%----------")
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operation failed, Please check Grid Configuration")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        results_dist= results_list[-240::1]

        print(results_dist)
        first=results_dist[0]
        print(first)
        print("-----------------------------------------")
        count=first['Query Count']
        print(count)
        print("--------------***********----------------")

        if count >= 22:
            print("PASSED")
            logger.info("Search validation result: %s (PASS)",count)
        else:
            logger.error("Search validation result: %s (FAIL)",count)

            msg = 'Count is less than 22 - %s', count
            assert count == 0, msg


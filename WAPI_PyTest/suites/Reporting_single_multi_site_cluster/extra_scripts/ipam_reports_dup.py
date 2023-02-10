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


class IPAM_reports(unittest.TestCase):
    """
    # IPAMv4 DEVICE NETWORKS
    
    @pytest.mark.run(order=1)
    def test_1_IPAMv4_device_networks(self):
    
        test1 = [{"IPAM Network":"167.1.1.0/24","Utilization %":"64.9"},{"IPAM Network":"166.10.0.0/16","Utilization %":"2.3"},{"IPAM Network":"165.0.0.0/8","Utilization %":"3.9"}]
        logger.info ("Input Json Data for IPAMv4 Device Networks report validation")
        logger.info(json.dumps(test1, sort_keys=True, indent=4, separators=(',', ': ')))

        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search source=ib:discovery:switch_port_capacity index=ib_discovery"

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
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",test1,results_dist)
        logger.info("compare_results with 'delta=1'")
        result = compare_results(test1,results_list,1)
        print(result)
        logger.info("-----------------------------------------------------")
        logger.info(test1)
        logger.info(len(test1))
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
        """

    # IPAMv4 NETWORK USAGE STATISTICS

    @pytest.mark.run(order=2)
    def test_2_IPAMv4_network_usage_statistics(self):
    
        test2=[{"Network":"167.1.1.0","CIDR":"24","Total":"256","Allocated":"165","Reserved":"2","Protocol":"IPV4"},{"Network":"166.10.0.0","CIDR":"16","Total":"65536","Allocated":"1549","Reserved":"2","Protocol":"IPV4"},{"Network":"165.0.0.0","CIDR":"8","Total":"16777216","Allocated":"658175","Reserved":"2","Protocol":"IPV4"}]
        logger.info ("Input Json Data for IPAMv4 Network Usage Statistics report validation")
        logger.info(json.dumps(test2, sort_keys=True, indent=4, separators=(',', ': ')))
    

        logger.info("Test:"+sys._getframe().f_code.co_name)
#        search_str="search sourcetype=ib:ipam:network index=ib_ipam | eval dedup_key=view.\"/\".address.\"/\".cidr | dedup dedup_key | eval NETWORK=address.\"/\".cidr | lookup network_ea_lookup_csv NETWORK, NETWORK_VIEW as view output EA | spath input=EA output=MSSITE path=BUILTIN-MSSite | eval MSSITE = if(isnull(MSSITE), \"(no_value)\", MSSITE) | mvexpand MSSITE | eval utilization=round(utilization/10, 1) | mvcombine MSSITE | sort -utilization | rename timestamp as Timestamp, view as \"Network view\", address as Network, cidr as CIDR, MSSITE as \"AD Site\", utilization as \"DHCPv4 Utilization %\", address_total as Total, address_alloc as Allocated, address_reserved as Reserved, address_assigned as Assigned, protocol as Protocol, allocation as \"Utilization %\", address_unmanaged as Unmanaged | table Timestamp, \"Network view\", Network, CIDR, \"AD Site\", \"DHCPv4 Utilization %\", Total, Allocated, Reserved, Assigned, Protocol, \"Utilization %\", Unmanaged"

        search_str="search sourcetype=ib:ipam:network index=ib_ipam"

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


    # IPAMv4 NETWORK USAGE TREND

    @pytest.mark.run(order=3)
    def test_3_IPAMv4_network_usage(self):
    
        test3=[{"165.0.0.0/8":"3.9","166.10.0.0/16":"2.3","167.1.1.0/24":"64.9"}]
        logger.info ("Input Json Data for IPAMv4 Network Usage Trend report validation")
        logger.info(json.dumps(test3, sort_keys=True, indent=4, separators=(',', ': ')))

        logger.info("Test:"+sys._getframe().f_code.co_name)
#        search_str="search sourcetype=ib:ipam:network index=ib_ipam | eval NETWORK=address.\"/\".cidr | lookup network_ea_lookup_csv NETWORK, NETWORK_VIEW as view output EA | spath input=EA output=MSSITE path=BUILTIN-MSSite | eval MSSITE = if(isnull(MSSITE), \"(no_value)\", MSSITE) | mvexpand MSSITE | sort -allocation | timechart bins=1000 avg(allocation) as \"Usage %\" by NETWORK useother=f"

        search_str="search sourcetype=ib:ipam:network index=ib_ipam"

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


    # IPAMv4 TOP UTILISED NETWORKS

    @pytest.mark.run(order=4)
    def test_4_IPAMv4_top_utilised_networks(self):
    
        test4=[{"Network":"167.1.1.0","CIDR":"24","Utilization %":"64.9","Total":"256","Reserved":"2"},{"Network":"165.0.0.0","CIDR":"8","Utilization %":"3.9","Total":"16777216","Reserved":"2"},{"Network":"166.10.0.0","CIDR":"16","Utilization %":"2.3","Total":"65536","Reserved":"2"}]
        logger.info ("Input Json Data for IPAMv4 Top Utilised Networks report validation")
        logger.info(json.dumps(test4, sort_keys=True, indent=4, separators=(',', ': ')))


        logger.info("Test:"+sys._getframe().f_code.co_name)
#        search_str="search sourcetype=ib:ipam:network index=ib_ipam | eval dedup_key=view.\"/\".address.\"/\".cidr | dedup dedup_key | eval NETWORK=address.\"/\".cidr | lookup network_ea_lookup_csv NETWORK, NETWORK_VIEW as view output EA | spath input=EA output=MSSITE path=BUILTIN-MSSite | eval MSSITE = if(isnull(MSSITE), \"(no_value)\", MSSITE) | sort -allocation | head 10 | rename timestamp as Timestamp, view as \"Network view\", address as Network, cidr as CIDR, MSSITE as \"AD Site\", allocation as \"Utilization %\", address_total as Total, address_assigned as Assigned, address_reserved as Reserved, address_unmanaged as Unmanaged | table Timestamp, \"Network view\", Network, CIDR, \"AD Site\", \"Utilization %\", Total, Assigned, Reserved, Unmanaged"

        search_str="search sourcetype=ib:ipam:network index=ib_ipam"

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
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",test4,results_dist)
        logger.info("compare_results with 'delta=1'")
        result = compare_results(test4,results_list,1)
        print(result)
        logger.info("-----------------------------------------------------")
        logger.info(test4)
        logger.info(len(test4))
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


    # DHCPv4 TOP UTILISED NETWORKS

    @pytest.mark.run(order=5)
    def test_5_DHCPv4_top_utilised_networks(self):
    
        test5=[{"Network":"167.1.1.0","CIDR":"24","Ranges":"1","Provisioned":"165","Static":"10"},{"Network":"166.10.0.0","CIDR":"16","Ranges":"1","Provisioned":"1549","Static":"14"},{"Network":"165.0.0.0","CIDR":"8","Ranges":"1","Provisioned":"658175","Static":"20"}]
        logger.info ("Input Json Data for DHCPv4 Top Utilized networks report validation")
        logger.info(json.dumps(test5, sort_keys=True, indent=4, separators=(',', ': ')))


        logger.info("Test:"+sys._getframe().f_code.co_name)
#        search_str="search sourcetype=ib:dhcp:network index=ib_dhcp | eval dedup_key=view.\"/\".address.\"/\".cidr | dedup dedup_key | sort 0 -num(dhcp_utilization) | head 10 | eval Free=address_total-dhcp_hosts | rename timestamp as Timestamp, view as \"Network View\", address as Network, cidr as CIDR, dhcp_utilization as \"DHCPv4 Utilization %\", ranges as Ranges, address_total as Provisioned, dhcp_hosts as Used, static_hosts as Static, dynamic_hosts as Dynamic | table Timestamp, \"Network View\", Network, CIDR, \"DHCPv4 Utilization %\", Ranges, Provisioned, Dynamic, Static, Free, Used"

        search_str="search sourcetype=ib:dhcp:network index=ib_dhcp"

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


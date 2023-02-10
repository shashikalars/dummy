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


class Network_VLAN_inventory_reports(unittest.TestCase):

    # NETWORK INVENTORY REPORT
        
    @pytest.mark.run(order=1)
    def test_1_Network_inventory(self):

        test1=[{"Address":"10.0.0.0","Netmask":"8","Network View":"default","Managed":"True","Management Platform":"","Assigned Vlan Name":"","Assigned Vlan ID":""}]
        
        
        logger.info ("Input Json Data for Network Inventory report validation")
        logger.info(json.dumps(test1, sort_keys=True, indent=4, separators=(',', ': ')))
        
        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search sourcetype=ib:ipam:network index=ib_ipam | sort 0 -_time, +ip(address) | fillnull value=\"\" | dedup view address cidr | eval last_discovered_timestamp=strftime(last_discovered_timestamp,\"%Y-%m-%d %H:%M:%S\") | eval first_discovered_timestamp=strftime(first_discovered_timestamp,\"%Y-%m-%d %H:%M:%S\") | eval allocation=round(allocation, 1) | rename view as \"Network View\" address as \"Address\" cidr as \"Netmask\" allocation as \"Utilization %\" port_vlan_name as \"Discovered Vlan Name\" assigned_port_vlan_name as \"Assigned Vlan Name\" port_vlan_number as \"Discovered Vlan ID\" assigned_port_vlan_number as \"Assigned Vlan ID\" vrf_name as \"VRF Name\" vrf_description as \"VRF Description\" vrf_rd as \"VRF RD\" bgp_as as \"BGP AS\" from_sdn as \"SDN\" first_discovered_timestamp as \"First Seen\" last_discovered_timestamp as \"Last Seen\" managed as \"Managed\" management_platform as \"Management Platform\" source_device as \"Source Device\"| table \"Address\" \"Netmask\" \"First Seen\" \"Last Seen\" \"Network View\" \"Utilization %\" \"Managed\" \"Management Platform\" \"Discovered Vlan Name\" \"Assigned Vlan Name\" \"Discovered Vlan ID\" \"Assigned Vlan ID\" \"VRF Name\" \"VRF Description\" \"VRF RD\" \"BGP AS\" \"SDN\" \"Source Device\""

        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        logger.info (cmd)

        print(os.system(cmd))
        print("-------------%%%----------")
        try:
            retrived_data=open(config.json_file).read()
            print(retrived_data)
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
        


    # VLAN INVENTORY REPORT

    @pytest.mark.run(order=2)
    def test_2_VLAN_inventory(self):
    
        test2=[{"VLAN ID":"154","VLAN Name":"VLAN_id2","VLAN View":"VLAN_view","VLAN Range":"VLAN_range1","Status":"ASSIGNED","Assigned To":"62.0.0.0/24"},{"VLAN ID":"159","VLAN Name":"VLAN_id1","VLAN View":"VLAN_view","VLAN Range":"","Status":"ASSIGNED","Assigned To":"Multiple"}]
        logger.info ("Input Json Data for VLAN Inventory report validation")
        logger.info(json.dumps(test2, sort_keys=True, indent=4, separators=(',', ': ')))

        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search sourcetype=ib:ipam:vlan_inventory index=ib_ipam | sort 0 -_time +num(vlan_id) | fillnull value=\"\" | rename timestamp as \"Time\" vlan_id as \"VLAN ID\" vlan_name as \"VLAN Name\" vlan_view as \"VLAN View\" vlan_range as \"VLAN Range\" status as \"Status\" assigned_to as \"Assigned To\" comment as \"Comment\" description as \"Description\" contact as \"Contact\" department as \"Department\" | table \"Time\" \"VLAN ID\" \"VLAN Name\" \"VLAN View\" \"VLAN Range\" \"Status\" \"Assigned To\" \"Comment\" \"Description\" \"Contact\" \"Department\""
        
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
        
        
        
    # VLAN CONFLICT REPORT
        
    @pytest.mark.run(order=3)
    def test_3_VLAN_conflict(self):
    
        test3=[{"Network":"61.0.0.0","Netmask":"24","Protocol":"IPV4","Assigned VLAN Name":"VLAN_id1","Assigned VLAN ID":"159"},{"Network":"62.0.0.0","Netmask":"24","Protocol":"IPV4","Assigned VLAN Name":"VLAN_id2","Assigned VLAN ID":"154"},{"Network":"2620:10a:6000:2500::","Netmask":"64","Protocol":"IPV6","Assigned VLAN Name":"VLAN_id1","Assigned VLAN ID":"159"}]
        logger.info ("Input Json Data for VLAN Conflict report validation")
        logger.info(json.dumps(test3, sort_keys=True, indent=4, separators=(',', ': ')))

        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search sourcetype=ib:ipam:vlan_conflict index=ib_ipam | sort 0 -_time +ip(address) | fillnull value=\"\" | rename timestamp as \"Time\" view as \"Network View\" address as \"Network\" cidr as \"Netmask\" protocol as \"Protocol\" discovered_vlan_name as \"Discovered VLAN Name\" discovered_vlan_id as \"Discovered VLAN ID\" assigned_vlan_name as \"Assigned VLAN Name\" assigned_vlan_id as \"Assigned VLAN ID\" reason as \"Conflict Reason\" discovered_for_ip as \"Discovered IP\" | table \"Time\" \"Network View\" \"Network\" \"Netmask\" \"Protocol\" \"Discovered VLAN Name\" \"Discovered VLAN ID\" \"Assigned VLAN Name\" \"Assigned VLAN ID\" \"Conflict Reason\" \"Discovered IP\""

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


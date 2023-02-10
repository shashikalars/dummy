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


class  Discovery_member_reports(unittest.TestCase):

    # DEVICE COMPONENTS

    @pytest.mark.run(order=1)
    def test_1_Device_components(self):
    

        test1 = [{"Device IP":"10.40.16.10","Network View":"discovery_view","Device Name":"DELL-PC8024F","Device Model":"Powerconnect 8024F","Device Vendor":"Dell","OS Version":"5.1.2.3","Name":"Te1/0/24","Description":"Unit: 1 Slot: 0 Port: 24 10G - Level","Class":"port"},{"Device IP":"10.40.16.10","Network View":"discovery_view","Device Name":"DELL-PC8024F","Device Model":"Powerconnect 8024F","Device Vendor":"Dell","OS Version":"5.1.2.3","Name":"Te1/0/21","Description":"Unit: 1 Slot: 0 Port: 21 10G - Level","Class":"port"},{"Device IP":"10.40.16.10","Network View":"discovery_view","Device Name":"DELL-PC8024F","Device Model":"Powerconnect 8024F","Device Vendor":"Dell","OS Version":"5.1.2.3","Name":"Te1/0/20","Description":"Unit: 1 Slot: 0 Port: 20 10G - Level","Class":"port"},{"Device IP":"10.40.16.10","Network View":"discovery_view","Device Name":"DELL-PC8024F","Device Model":"Powerconnect 8024F","Device Vendor":"Dell","OS Version":"5.1.2.3","Name":"Te1/0/19","Description":"Unit: 1 Slot: 0 Port: 19 10G - Level","Class":"port"},{"Device IP":"10.40.16.10","Network View":"discovery_view","Device Name":"DELL-PC8024F","Device Model":"Powerconnect 8024F","Device Vendor":"Dell","OS Version":"5.1.2.3","Name":"Te1/0/18","Description":"Unit: 1 Slot: 0 Port: 18 10G - Level","Class":"port"}]
        logger.info ("Input Json Data for Device components report validation")
        logger.info(json.dumps(test1, sort_keys=True, indent=4, separators=(',', ': ')))
    

        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search source=ib:discovery:device_components index=ib_discovery | fillnull value=\"\" | dedup network_view ip_address component_name description class serial_number sortby +_time| rename ip_address as \"Device IP\" network_view as \"Network View\" device_name as \"Device Name\" device_model as \"Device Model\" device_vendor as \"Device Vendor\" device_os_version as \"OS Version\" component_name as \"Name\" description as \"Description\" class as \"Class\" serial_number as \"S/N\" model as \"Model\" hardware_rev as \"Hardware Rev\" firmware_rev as \"Firmware Rev\" software_rev as \"Software Rev\" | table \"Device IP\" \"Network View\" \"Device Name\" \"Device Model\" \"Device Vendor\" \"OS Version\" \"Name\" \"Description\" \"Class\" \"S/N\" \"Model\" \"Hardware Rev\" \"Firmware Rev\" \"Software Rev\" | sort -_time"

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



    # DEVICE INTERFACE INVENTORY

    @pytest.mark.run(order=2)
    def test_2_Device_interface_inventory(self):
    

        test2=[{"Network View":"discovery_view","Device IP":"10.40.16.10","Device Name":"DELL-PC8024F","Device Type":"Switch-Router","Device Vendor":"Dell","Device Model":"Powerconnect 8024F","Device OS Version":"5.1.2.3","Interface Name":"Po81","Interface Description":"Link Aggregate 81","Admin Status":"up","Operation Status":"down"},{"Network View":"discovery_view","Device IP":"10.40.16.10","Device Name":"DELL-PC8024F","Device Type":"Switch-Router","Device Vendor":"Dell","Device Model":"Powerconnect 8024F","Device OS Version":"5.1.2.3","Interface Name":"Te1/0/19","Interface Description":"Unit: 1 Slot: 0 Port: 19 10G - Level","Admin Status":"up","Operation Status":"down"},{"Network View":"discovery_view","Device IP":"10.40.16.10","Device Name":"DELL-PC8024F","Device Type":"Switch-Router","Device Vendor":"Dell","Device Model":"Powerconnect 8024F","Device OS Version":"5.1.2.3","Interface Name":"Te1/0/15","Interface Description":"Unit: 1 Slot: 0 Port: 15 10G - Level","Admin Status":"up","Operation Status":"down"},{"Network View":"discovery_view","Device IP":"10.40.16.10","Device Name":"DELL-PC8024F","Device Type":"Switch-Router","Device Vendor":"Dell","Device Model":"Powerconnect 8024F","Device OS Version":"5.1.2.3","Interface Name":"Po63","Interface Description":"Link Aggregate 63","Admin Status":"up","Operation Status":"down"},{"Network View":"discovery_view","Device IP":"10.40.16.10","Device Name":"DELL-PC8024F","Device Type":"Switch-Router","Device Vendor":"Dell","Device Model":"Powerconnect 8024F","Device OS Version":"5.1.2.3","Interface Name":"Po106","Interface Description":"Link Aggregate 106","Admin Status":"up","Operation Status":"down"}]
        logger.info ("Input Json Data for Device interface inventory report validation")
        logger.info(json.dumps(test2, sort_keys=True, indent=4, separators=(',', ': ')))

    

        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search source=ib:discovery:switch_port_capacity index=ib_discovery | fillnull value=\"N/A\" | dedup network_view, device_id, interface_ip_address, interface_name | rename network_view as \"Network View\" InterfaceSubnet as \"Network\" device_ip_address as \"Device IP\" interface_ip_address as \"Interface IP\" interface_name as \"Interface Name\" interface_description as \"Interface Description\" device_model as \"Device Model\" device_vendor as \"Device Vendor\" device_version as \"Device OS Version\" device_type as \"Device Type\" device_name as \"Device Name\" is_trunk_port as \"Trunk Port\" interface_type as \"Type\" interface_speed as \"Speed\" interface_vlan as \"Vlan ID\" interface_vlan_name as \"Vlan Name\" interface_admin_status as \"Admin Status\" interface_port_status as \"Operation Status\" port_last_changed_at as \"Last port Changed\" aggregated_interface as \"Aggregated Interface\" | table \"Network View\" \"Device IP\" \"Device Name\" \"Device Type\" \"Device Vendor\" \"Device Model\" \"Device OS Version\" \"Interface Name\" \"Interface IP\" \"Interface Description\" \"Admin Status\" \"Operation Status\" \"Last port Changed\" \"Trunk Port\" \"Type\" \"Speed\" \"Vlan ID\" \"Vlan Name\" \"Network\" \"Aggregated Interface\""

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



    # DEVICE INVENTORY
    
    @pytest.mark.run(order=3)
    def test_3_Device_inventory(self):
    

        test3=[{"Asset Type":"Physical Device","Device Vendor":"Alcatel","Device Name":"unknown","Device IP":"10.40.16.12","Network View":"discovery_view"},{"Asset Type":"Physical Device","Device Vendor":"Cisco","OS Version":"15.0(2)SE8","Device Name":"ni-mri-core.inca.infoblox.com","Chassis S/N":"FDO1523R1Q7","Device IP":"10.40.16.1","Network View":"discovery_view"}]
        logger.info ("Input Json Data for Device inventory report validation")
        logger.info(json.dumps(test3, sort_keys=True, indent=4, separators=(',', ': ')))


        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search source=ib:discovery:device_inventory index=ib_discovery | dedup ip_address | eval last_seen=strftime(last_seen,\"%Y-%m-%d %H:%M:%S\") | eval first_seen=strftime(first_seen,\"%Y-%m-%d %H:%M:%S\") | rename device_type as \"Device Type\" asset_type as \"Asset Type\" device_vendor as \"Device Vendor\" device_model as \"Device Model\" device_os_version as \"OS Version\" serial_number as \"Chassis S/N\" ip_address as \"Device IP\" device_name as \"Device Name\" network_view as \"Network View\" first_seen as \"First Seen\" last_seen as \"Last Seen\" | table \"Device Type\" \"Asset Type\" \"Device Vendor\" \"Device Model\" \"OS Version\" \"Device Name\" \"Chassis S/N\" \"Device IP\" \"Network View\" \"First Seen\" \"Last Seen\" | sort -_time +str(\"Device Type\")"

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



    # IPAMv4 DEVICE NETWORKS
            
    @pytest.mark.run(order=4)
    def test_4_IPAMv4_device_networks(self):
    

        test4=[{"IPAM Network":"167.1.1.0/24","Utilization %":"64.9"},{"IPAM Network":"166.10.0.0/16","Utilization %":"2.3"},{"IPAM Network":"165.0.0.0/8","Utilization %":"3.9"}]
        logger.info ("Input Json Data for IPAMv4 Device Networks report validation")
        logger.info(json.dumps(test4, sort_keys=True, indent=4, separators=(',', ': ')))

        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search source=ib:discovery:switch_port_capacity index=ib_discovery | fillnull value=\"N/A\" | dedup network_view device_ip_address interface_ip_address | join type=inner InterfaceSubnet, network_view [search sourcetype=ib:ipam:network index=ib_ipam | dedup NETWORK, view | rename NETWORK as InterfaceSubnet view as network_view | fields InterfaceSubnet, network_view, allocation] | APPEND [search sourcetype=ib:ipam:network index=ib_ipam | dedup NETWORK, view | rename NETWORK as InterfaceSubnet view as network_view | join type=left InterfaceSubnet, network_view [search source=ib:discovery:switch_port_capacity index=ib_discovery | fields InterfaceSubnet, device_ip_address, network_view] | where isnull(device_ip_address)] | rename InterfaceSubnet as \"IPAM Network\" allocation as \"Utilization %\" device_ip_address as \"Device IP\" interface_ip_address as \"Interface IP\" device_model as \"Device Model\" device_vendor as \"Device Vendor\" device_version as \"Device OS Version\" device_name as \"Device Name\" network_view as \"Network View\" | table \"IPAM Network\", \"Utilization %\", \"Network View\", \"Device IP\", \"Device Name\", \"Interface IP\", \"Device Model\", \"Device Vendor\", \"Device OS Version\""

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



    # IP ADDRESS INVENTORY

    @pytest.mark.run(order=5)
    def test_5_IP_address_inventory(self):


        test5=[{"IP Address":"10.40.16.1","Discovered Name":"ni-mri-core.inca.infoblox.com","Network View":"discovery_view","Managed":"False","Management Platform":"Network Insight"},{"IP Address":"10.40.16.7","Discovered Name":"EX2200-48T-4G","Network View":"discovery_view","Managed":"False","Management Platform":"Network Insight"}]
        logger.info ("Input Json Data for IP address inventory report validation")
        logger.info(json.dumps(test5, sort_keys=True, indent=4, separators=(',', ': ')))



        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search source=ib:ipam:ip_address_inventory index=ib_ipam | sort 0 -_time, +ip(ip_address) | fillnull value=\"\" | dedup network_view ip_address | eval last_discovered_timestamp=strftime(last_discovered_timestamp,\"%Y-%m-%d %H:%M:%S\") | eval first_discovered_timestamp=strftime(first_discovered_timestamp,\"%Y-%m-%d %H:%M:%S\") | rename network_view as \"Network View\" ip_address as \"IP Address\" discovered_name as \"Discovered Name\" port_vlan_name as \"Vlan Name\" port_vlan_number as \"Vlan ID\" vrf_name as \"VRF Name\" vrf_description as \"VRF Description\" vrf_rd as \"VRF RD\" bgp_as as \"BGP AS\" first_discovered_timestamp as \"First Seen\" last_discovered_timestamp as \"Last Seen\" managed as \"Managed\" management_platform as \"Management Platform\" | table \"IP Address\" \"Discovered Name\" \"First Seen\" \"Last Seen\" \"Network View\" \"Managed\" \"Management Platform\" \"Vlan Name\" \"Vlan ID\" \"VRF Name\" \"VRF Description\" \"VRF RD\" \"BGP AS\""


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


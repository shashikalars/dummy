"""
 Copyright (c) Infoblox Inc., 2016

 ReportName          : DNS Query Rate By Query Type
 ReportCategory      : DNS Query
 Number of Test cases: 1
 Execution time      : 361.09 seconds
 Execution Group     : Minute Group (MG)
 Description         : DNS 'Query Rate by Query Type' report update every 1 min.

 Author   : Vindya V K
 History  : 02/24/2021 (Created)
 Reviewer : Shekhar, Manoj
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
import time
import unittest
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from logger import logger
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results

"""
TEST Steps:
      1.  Input/Preparaiton      : logging into discovery member as root and perform few commands
      2.  Search                 : Search with Default Filter
      3.  Validation             : Validating Search result against input data
"""


class  Discovery_member_reports(unittest.TestCase):
    @classmethod

    def setup_class(cls):

        logger.info("Logging into discovery member as 'root'")
	child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
	child.logfile=sys.stdout
	child.expect('#')

        child.sendline("cd /infoblox/netmri/bin")
        child.expect('-bash-5.0#',timeout=100)

        child.sendline("./discovery_network_device_inventory")
        child.expect('-bash-5.0#',timeout=100)

        child.sendline("./discovery_switch_port_capacity")
        child.expect('-bash-5.0#',timeout=100)
 
        child.sendline("./discovery_vpn_info")
        child.expect('-bash-5.0#',timeout=100)
 
        child.sendline("./discovery_device_components")
        child.expect('-bash-5.0#',timeout=100)

        child.sendline("exit")


        #Wait for some time for the reports to be generated
        print("sleeping for 600 seconds")
        sleep(600)
	
	'''
	try:
	    child.expect('(yes/no)?',timeout=100)
            child.sendline("yes")

            child.expect('-bash-5.0#',timeout=100)
            child.sendline("cd /infoblox/netmri/bin")

            child.expect('-bash-5.0#',timeout=100)
            child.sendline("./discovery_network_device_inventory")

            child.expect('-bash-5.0#',timeout=100)
            child.sendline("./discovery_switch_port_capacity")

            child.expect('-bash-5.0#',timeout=100)
            child.sendline("./discovery_vpn_info")

            child.expect('-bash-5.0#',timeout=100)
            child.sendline("./discovery_device_components")

            child.expect('-bash-5.0#',timeout=100)
            child.sendline("exit")

            #Wait for some time for the reports to be generated
            print("sleeping for 600 seconds")
	    #sleep(600)

        except Exception as e:
            print(e)
            child.close()
            assert False


        finally:
            child.close()

	'''

# Expected Values

        # DEVICE COMPONENTS

	cls.test1 = [{u'Device Name': u'ni-mri-core.inca.infoblox.com', u'Network View': u'discovery_view', u'Device Vendor': u'Cisco', u'Device IP': u'10.40.16.1'}]

        logger.info ("Input Json Data for Device components report validation")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))


        # DEVICE INTERFACE INVENTORY

	cls.test2 = [{u'Device Name': u'ni-mri-core.inca.infoblox.com', u'Network View': u'discovery_view', u'Device Vendor': u'Cisco', u'Device IP': u'10.40.16.1'}]	

        logger.info ("Input Json Data for Device interface inventory report validation")
        logger.info(json.dumps(cls.test2, sort_keys=True, indent=4, separators=(',', ': ')))


        # DEVICE INVENTORY

	cls.test3 = [{u'Asset Type': u'Physical Device', u'Device Name': u'ni-mri-core.inca.infoblox.com', u'Device Vendor': u'Cisco', u'Network View': u'discovery_view'}]

        logger.info ("Input Json Data for Device inventory report validation")
        logger.info(json.dumps(cls.test3, sort_keys=True, indent=4, separators=(',', ': ')))


        # IPAMv4 DEVICE NETWORKS

        cls.test4 = [{u'Device Name': u'ni-mri-core.inca.infoblox.com', u'Network View': u'discovery_view', u'Device Vendor': u'Cisco', u'Device IP': u'10.40.16.1'}]
	logger.info ("Input Json Data for IPAMv4 Device Networks report validation")
        logger.info(json.dumps(cls.test4, sort_keys=True, indent=4, separators=(',', ': ')))

        # IP ADDRESS INVENTORY

	cls.test5 = [{u'Discovered Name': u'ni-mri-core.inca.infoblox.com', u'Network View': u'discovery_view'}]	

        logger.info ("Input Json Data for IP address inventory report validation")
        logger.info(json.dumps(cls.test5, sort_keys=True, indent=4, separators=(',', ': ')))


    # DEVICE COMPONENTS
    @pytest.mark.run(order=1)
    def test_001_device_components(self):

	print("################################DEVICE COMPONENTS#################################")
        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search source=ib:discovery:device_components index=ib_discovery | fillnull value=\"\" | dedup network_view ip_address component_name description class serial_number sortby +_time| rename ip_address as \"Device IP\" network_view as \"Network View\" device_name as \"Device Name\" device_model as \"Device Model\" device_vendor as \"Device Vendor\" device_os_version as \"OS Version\" component_name as \"Name\" description as \"Description\" class as \"Class\" serial_number as \"S/N\" model as \"Model\" hardware_rev as \"Hardware Rev\" firmware_rev as \"Firmware Rev\" software_rev as \"Software Rev\" | table \"Device IP\" \"Network View\" \"Device Name\" \"Device Model\" \"Device Vendor\" \"OS Version\" \"Name\" \"Description\" \"Class\" \"S/N\" \"Model\" \"Hardware Rev\" \"Firmware Rev\" \"Software Rev\" | sort -_time"
        print(search_str)
        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        print("##########################",cmd)
        logger.info (cmd)

        print(os.system(cmd))
        print("-------------%%%----------")
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operation failed, Please check Grid Configuration")
        output_data = json.loads(retrived_data)
#        print(output_data)
        results_list = output_data['results']
        results_dist= results_list[-240::1]
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test1,results_dist)
        logger.info("compare_results with 'delta=1'")
        result = compare_results(self.test1,results_list,1)
	print("*********************EXPECTED OUTPUT********************")
        print(self.test1)
	print("*********************ACTUAL OUTPUT**********************")
	print(results_list)
	print("********************MISSED OUTPUT***********************")
	print(result)
	print("########################################################")
        logger.info("-----------------------------------------------------")
        logger.info(self.test1)
        logger.info(len(self.test1))
        logger.info("--------------------shashhhhhhhh-------------------")
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
    def test_002_device_interface_inventory(self):

	print("#########################DEVICE INTERFACE INVENTORY############################")
        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search source=ib:discovery:switch_port_capacity index=ib_discovery | fillnull value=\"N/A\" | dedup network_view, device_id, interface_ip_address, interface_name | rename network_view as \"Network View\" InterfaceSubnet as \"Network\" device_ip_address as \"Device IP\" interface_ip_address as \"Interface IP\" interface_name as \"Interface Name\" interface_description as \"Interface Description\" device_model as \"Device Model\" device_vendor as \"Device Vendor\" device_version as \"Device OS Version\" device_type as \"Device Type\" device_name as \"Device Name\" is_trunk_port as \"Trunk Port\" interface_type as \"Type\" interface_speed as \"Speed\" interface_vlan as \"Vlan ID\" interface_vlan_name as \"Vlan Name\" interface_admin_status as \"Admin Status\" interface_port_status as \"Operation Status\" port_last_changed_at as \"Last port Changed\" aggregated_interface as \"Aggregated Interface\" | table \"Network View\" \"Device IP\" \"Device Name\" \"Device Type\" \"Device Vendor\" \"Device Model\" \"Device OS Version\" \"Interface Name\" \"Interface IP\" \"Interface Description\" \"Admin Status\" \"Operation Status\" \"Last port Changed\" \"Trunk Port\" \"Type\" \"Speed\" \"Vlan ID\" \"Vlan Name\" \"Network\" \"Aggregated Interface\""
        print(search_str)
        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        logger.info (cmd)
        print("##########################",cmd)
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
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test2,results_dist)
        logger.info("compare_results with 'delta=1'")
        result = compare_results(self.test2,results_list,1)
        print("*********************EXPECTED OUTPUT********************")
        print(self.test1)
        print("*********************ACTUAL OUTPUT**********************")
        print(results_list)
        print("********************MISSED OUTPUT***********************")
        print(result)
        print("########################################################")
	logger.info("-----------------------------------------------------")
        logger.info(self.test2)
        logger.info(len(self.test2))
        logger.info("--------------------shashhhhhhhh-------------------")
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
    def test_003_device_inventory(self):

	print("######################DEVICE INVENTORY#######################")
        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search source=ib:discovery:device_inventory index=ib_discovery | dedup ip_address | eval last_seen=strftime(last_seen,\"%Y-%m-%d %H:%M:%S\") | eval first_seen=strftime(first_seen,\"%Y-%m-%d %H:%M:%S\") | rename device_type as \"Device Type\" asset_type as \"Asset Type\" device_vendor as \"Device Vendor\" device_model as \"Device Model\" device_os_version as \"OS Version\" serial_number as \"Chassis S/N\" ip_address as \"Device IP\" device_name as \"Device Name\" network_view as \"Network View\" first_seen as \"First Seen\" last_seen as \"Last Seen\" | table \"Device Type\" \"Asset Type\" \"Device Vendor\" \"Device Model\" \"OS Version\" \"Device Name\" \"Chassis S/N\" \"Device IP\" \"Network View\" \"First Seen\" \"Last Seen\" | sort -_time +str(\"Device Type\")"
        print(search_str)
        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        logger.info (cmd)
        print("##########################",cmd)
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
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test3,results_dist)
        logger.info("compare_results with 'delta=1'")
        result = compare_results(self.test3,results_list,1)
        print("*********************EXPECTED OUTPUT********************")
        print(self.test1)
        print("*********************ACTUAL OUTPUT**********************")
        print(results_list)
        print("********************MISSED OUTPUT***********************")
        print(result)
        print("########################################################")
	logger.info(self.test3)
        logger.info(len(self.test3))
        logger.info("--------------------shashhhhhhhh-------------------")
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
    def test_004_ipamv4_device_networks(self):

	print("#####################IPAMv4 DEVICE NETWORKS##########################")
        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search source=ib:discovery:switch_port_capacity index=ib_discovery | fillnull value=\"N/A\" | dedup network_view device_ip_address interface_ip_address | join type=inner InterfaceSubnet, network_view [search sourcetype=ib:ipam:network index=ib_ipam | dedup NETWORK, view | rename NETWORK as InterfaceSubnet view as network_view | fields InterfaceSubnet, network_view, allocation] | APPEND [search sourcetype=ib:ipam:network index=ib_ipam | dedup NETWORK, view | rename NETWORK as InterfaceSubnet view as network_view | join type=left InterfaceSubnet, network_view [search source=ib:discovery:switch_port_capacity index=ib_discovery | fields InterfaceSubnet, device_ip_address, network_view] | where isnull(device_ip_address)] | rename InterfaceSubnet as \"IPAM Network\" allocation as \"Utilization %\" device_ip_address as \"Device IP\" interface_ip_address as \"Interface IP\" device_model as \"Device Model\" device_vendor as \"Device Vendor\" device_version as \"Device OS Version\" device_name as \"Device Name\" network_view as \"Network View\" | table \"IPAM Network\", \"Utilization %\", \"Network View\", \"Device IP\", \"Device Name\", \"Interface IP\", \"Device Model\", \"Device Vendor\", \"Device OS Version\""
        print(search_str)
        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        logger.info (cmd)
        print("##########################",cmd)

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
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test4,results_dist)
        logger.info("compare_results with 'delta=1'")
        result = compare_results(self.test4,results_list,1)
        print("*********************EXPECTED OUTPUT********************")
        print(self.test1)
        print("*********************ACTUAL OUTPUT**********************")
        print(results_list)
        print("********************MISSED OUTPUT***********************")
        print(result)
	print("########################################################")
	logger.info("-----------------------------------------------------")
        logger.info(self.test4)
        logger.info(len(self.test4))
        logger.info("--------------------shashhhhhhhh-------------------")
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
    def test_005_ip_address_inventory(self):

	print("#######################IP ADDRESS INVENTORY##########################")
        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search source=ib:ipam:ip_address_inventory index=ib_ipam | sort 0 -_time, +ip(ip_address) | fillnull value=\"\" | dedup network_view ip_address | eval last_discovered_timestamp=strftime(last_discovered_timestamp,\"%Y-%m-%d %H:%M:%S\") | eval first_discovered_timestamp=strftime(first_discovered_timestamp,\"%Y-%m-%d %H:%M:%S\") | rename network_view as \"Network View\" ip_address as \"IP Address\" discovered_name as \"Discovered Name\" port_vlan_name as \"Vlan Name\" port_vlan_number as \"Vlan ID\" vrf_name as \"VRF Name\" vrf_description as \"VRF Description\" vrf_rd as \"VRF RD\" bgp_as as \"BGP AS\" first_discovered_timestamp as \"First Seen\" last_discovered_timestamp as \"Last Seen\" managed as \"Managed\" management_platform as \"Management Platform\" | table \"IP Address\" \"Discovered Name\" \"First Seen\" \"Last Seen\" \"Network View\" \"Managed\" \"Management Platform\" \"Vlan Name\" \"Vlan ID\" \"VRF Name\" \"VRF Description\" \"VRF RD\" \"BGP AS\""

        print(search_str)
        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        logger.info (cmd)
        print("##########################",cmd)

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
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test5,results_dist)
        logger.info("compare_results with 'delta=1'")
        result = compare_results(self.test5,results_list,1)
        print("*********************EXPECTED OUTPUT********************")
        print(self.test1)
        print("*********************ACTUAL OUTPUT**********************")
        print(results_list)
        print("********************MISSED OUTPUT***********************")
        print(result)
	print("########################################################")
        logger.info("-----------------------------------------------------")
        logger.info(self.test5)
        logger.info(len(self.test5))
        logger.info("--------------------shashhhhhhhh-------------------")
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


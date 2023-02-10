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
        child = pexpect.spawn("ssh root@"+config.grid_member1_vip,  maxread=4000)
	#child = pexpect.spawn("ssh root@10.35.192.4",  maxread=4000)
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
	    sleep(600)

        except Exception as e:
            print(e)
            child.close()
            assert False


        finally:
            child.close()


# Expected Values

        # DEVICE COMPONENTS

	cls.test1 = [{u'Firmware Rev': u'', u'Device Name': u'EX2200-48T-4G', u'Network View': u'default', u'Device Vendor': u'Juniper', u'Hardware Rev': u'', u'Device IP': u'10.40.16.7', u'Software Rev': u'', u'S/N': u'', u'Device Model': u'EX2200-48T-4G', u'Description': u'', u'Model': u'', u'OS Version': u'13.2X51-D20.2', u'Class': u'routingEngine', u'Name': u'Routing Engine 2'}, {u'Firmware Rev': u'', u'Device Name': u'EX2200-48T-4G', u'Network View': u'default', u'Device Vendor': u'Juniper', u'Hardware Rev': u'', u'Device IP': u'10.40.16.7', u'Software Rev': u'', u'S/N': u'', u'Device Model': u'EX2200-48T-4G', u'Description': u'', u'Model': u'', u'OS Version': u'13.2X51-D20.2', u'Class': u'routingEngine', u'Name': u'Routing Engine'}]

        logger.info ("Input Json Data for Device components report validation")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))


        # DEVICE INTERFACE INVENTORY

	cls.test2 = [{u'Vlan ID': u'N/A', u'Interface IP': u'N/A', u'Device Name': u'EX2200-48T-4G', u'Network View': u'default', u'Interface Name': u'ge-0/0/38', u'Device Vendor': u'Juniper', u'Interface Description': u'ge-0/0/38', u'Device IP': u'10.40.16.7', u'Speed': u'0', u'Vlan Name': u'N/A', u'Network': u'N/A', u'Device Type': u'Switch-Router', u'Trunk Port': u'no', u'Device Model': u'EX2200-48T-4G', u'Aggregated Interface': u'N/A', u'Admin Status': u'up', u'Last port Changed': u'2021-03-23 14:55:08', u'Operation Status': u'down', u'Type': u'ethernet-csmacd', u'Device OS Version': u'13.2X51-D20.2'}, {u'Vlan ID': u'N/A', u'Interface IP': u'N/A', u'Device Name': u'EX2200-48T-4G', u'Network View': u'default', u'Interface Name': u'ge-0/0/19', u'Device Vendor': u'Juniper', u'Interface Description': u'ge-0/0/19', u'Device IP': u'10.40.16.7', u'Speed': u'0', u'Vlan Name': u'N/A', u'Network': u'N/A', u'Device Type': u'Switch-Router', u'Trunk Port': u'no', u'Device Model': u'EX2200-48T-4G', u'Aggregated Interface': u'N/A', u'Admin Status': u'up', u'Last port Changed': u'2021-03-23 14:55:06', u'Operation Status': u'down', u'Type': u'ethernet-csmacd', u'Device OS Version': u'13.2X51-D20.2'}, {u'Vlan ID': u'0', u'Interface IP': u'N/A', u'Device Name': u'EX2200-48T-4G', u'Network View': u'default', u'Interface Name': u'ge-0/0/4.0', u'Device Vendor': u'Juniper', u'Interface Description': u'ge-0/0/4.0', u'Device IP': u'10.40.16.7', u'Speed': u'0', u'Vlan Name': u'default', u'Network': u'N/A', u'Device Type': u'Switch-Router', u'Trunk Port': u'no', u'Device Model': u'EX2200-48T-4G', u'Aggregated Interface': u'N/A', u'Admin Status': u'up', u'Last port Changed': u'2021-03-23 14:55:05', u'Operation Status': u'lowerLayerDown', u'Type': u'propVirtual', u'Device OS Version': u'13.2X51-D20.2'}, {u'Vlan ID': u'N/A', u'Interface IP': u'N/A', u'Device Name': u'EX2200-48T-4G', u'Network View': u'default', u'Interface Name': u'ge-0/0/44', u'Device Vendor': u'Juniper', u'Interface Description': u'ge-0/0/44', u'Device IP': u'10.40.16.7', u'Speed': u'0', u'Vlan Name': u'N/A', u'Network': u'N/A', u'Device Type': u'Switch-Router', u'Trunk Port': u'no', u'Device Model': u'EX2200-48T-4G', u'Aggregated Interface': u'N/A', u'Admin Status': u'up', u'Last port Changed': u'2021-03-23 14:55:08', u'Operation Status': u'down', u'Type': u'ethernet-csmacd', u'Device OS Version': u'13.2X51-D20.2'}]	

        #cls.test2 = [{'Device Name': 'EX4200-24P', 'Network View': 'discovery_view', 'Admin Status': 'down', 'Interface Description': 'ge-0/0/3', 'Device IP': '10.40.16.6', 'Device Type': 'Switch-Router', 'Device Model': 'EX4200-24P', 'Type': 'ethernet-csmacd', 'Trunk Port': 'no', 'Interface Name': 'ge-0/0/3', 'Device Vendor': 'Juniper', 'Interface IP': 'N/A', 'Device OS Version': '13.2X50-D15.3', 'Speed': '0', 'Operation Status': 'down'}, {'Device Name': 'EX4200-24P', 'Network View': 'discovery_view', 'Admin Status': 'up', 'Interface Description': 'vcp-1.32768', 'Device IP': '10.40.16.6', 'Device Type': 'Switch-Router', 'Device Model': 'EX4200-24P', 'Type': 'propVirtual', 'Trunk Port': 'no', 'Interface Name': 'vcp-1.32768', 'Device Vendor': 'Juniper', 'Interface IP': 'N/A', 'Device OS Version': '13.2X50-D15.3', 'Speed': '32000000000', 'Operation Status': 'lowerLayerDown'}, {'Device Name': 'EX4200-24P', 'Network View': 'discovery_view', 'Admin Status': 'down', 'Interface Description': 'ge-0/0/9', 'Device IP': '10.40.16.6', 'Device Type': 'Switch-Router', 'Device Model': 'EX4200-24P', 'Type': 'ethernet-csmacd', 'Trunk Port': 'no', 'Interface Name': 'ge-0/0/9', 'Device Vendor': 'Juniper', 'Interface IP': 'N/A', 'Device OS Version': '13.2X50-D15.3', 'Speed': '0', 'Operation Status': 'down'}, {'Device Name': 'EX4200-24P', 'Network View': 'discovery_view', 'Admin Status': 'up', 'Interface Description': 'ge-0/0/14.0', 'Device IP': '10.40.16.6', 'Device Type': 'Switch-Router', 'Device Model': 'EX4200-24P', 'Type': 'propVirtual', 'Trunk Port': 'no', 'Interface Name': 'ge-0/0/14.0', 'Device Vendor': 'Juniper', 'Interface IP': 'N/A', 'Device OS Version': '13.2X50-D15.3', 'Speed': '0', 'Operation Status': 'lowerLayerDown'}, {'Device Name': 'EX4200-24P', 'Network View': 'discovery_view', 'Admin Status': 'up', 'Interface Description': 'me0.0', 'Device IP': '10.40.16.6', 'Device Type': 'Switch-Router', 'Device Model': 'EX4200-24P', 'Type': 'propVirtual', 'Trunk Port': 'no', 'Interface Name': 'me0.0', 'Device Vendor': 'Juniper', 'Interface IP': 'N/A', 'Device OS Version': '13.2X50-D15.3', 'Speed': '0', 'Operation Status': 'lowerLayerDown'}]

	#cls.test2=[{"Network View":"discovery_view","Device IP":"10.40.16.6","Device Name":"EX4200-24P","Device Type":"Switch-Router","Device Vendor":"Juniper","Device Model":"EX4200-24P","Device OS Version":"13.2X50-D15.3","Interface Name":"ge-0/0/3","Interface IP":"N/A","Interface Description":"ge-0/0/3","Admin Status":"down","Operation Status":"down","Trunk Port":"no","Type":"ethernet-csmacd","Speed":"0"},{"Network View":"discovery_view","Device IP":"10.40.16.6","Device Name":"EX4200-24P","Device Type":"Switch-Router","Device Vendor":"Juniper","Device Model":"EX4200-24P","Device OS Version":"13.2X50-D15.3","Interface Name":"vcp-1.32768","Interface IP":"N/A","Interface Description":"vcp-1.32768","Admin Status":"up","Operation Status":"lowerLayerDown", "Trunk Port":"no","Type":"propVirtual","Speed":"32000000000"},{"Network View":"discovery_view","Device IP":"10.40.16.6","Device Name":"EX4200-24P","Device Type":"Switch-Router","Device Vendor":"Juniper","Device Model":"EX4200-24P","Device OS Version":"13.2X50-D15.3","Interface Name":"ge-0/0/9","Interface IP":"N/A","Interface Description":"ge-0/0/9","Admin Status":"down","Operation Status":"down","Trunk Port":"no","Type":"ethernet-csmacd","Speed":"0"},{"Network View":"discovery_view","Device IP":"10.40.16.6","Device Name":"EX4200-24P","Device Type":"Switch-Router","Device Vendor":"Juniper","Device Model":"EX4200-24P","Device OS Version":"13.2X50-D15.3","Interface Name":"ge-0/0/14.0","Interface IP":"N/A","Interface Description":"ge-0/0/14.0","Admin Status":"up","Operation Status":"lowerLayerDown","Trunk Port":"no","Type":"propVirtual","Speed":"0"},{"Network View":"discovery_view","Device IP":"10.40.16.6","Device Name":"EX4200-24P","Device Type":"Switch-Router","Device Vendor":"Juniper","Device Model":"EX4200-24P","Device OS Version":"13.2X50-D15.3","Interface Name":"me0.0","Interface IP":"N/A","Interface Description":"me0.0","Admin Status":"up","Operation Status":"lowerLayerDown","Trunk Port":"no","Type":"propVirtual","Speed":"0"}]
        logger.info ("Input Json Data for Device interface inventory report validation")
        logger.info(json.dumps(cls.test2, sort_keys=True, indent=4, separators=(',', ': ')))


        # DEVICE INVENTORY

	cls.test3 = [{u'Asset Type': u'Physical Device', u'Device Name': u'unknown', u'Network View': u'default', u'Device Vendor': u'Cisco', u'Device IP': u'10.40.16.100', u'Device Type': u'End Host'}, {u'Asset Type': u'Physical Device', u'Device Name': u'unknown', u'Network View': u'default', u'Device Vendor': u'Alcatel', u'Device IP': u'10.40.16.12', u'Device Type': u'End Host'}, {u'Asset Type': u'Physical Device', u'Device Name': u'unknown', u'Network View': u'default', u'Device Vendor': u'Alcatel', u'Device IP': u'10.40.16.11', u'Device Type': u'End Host'}, {u'OS Version': u'15.0(2)SE8', u'Device Type': u'Router', u'Asset Type': u'Physical Device', u'Device Name': u'ni-mri-core.inca.infoblox.com', u'Network View': u'default', u'Device Vendor': u'Cisco', u'Chassis S/N': u'FDO1523R1Q7', u'Device IP': u'10.40.16.1', u'Device Model': u'WS-C3560X-48T-S'}, {u'OS Version': u'13.2X51-D20.2', u'Device Type': u'Switch-Router', u'Asset Type': u'Physical Device', u'Device Name': u'EX2200-48T-4G', u'Network View': u'default', u'Device Vendor': u'Juniper', u'Chassis S/N': u'CU0212399302', u'Device IP': u'10.40.16.7', u'Device Model': u'EX2200-48T-4G'}]

        #cls.test3=[{"Device Type":"End Host","Asset Type":"Physical Device","Device Name":"unknown","Device IP":"10.40.16.13","Network View":"discovery_view"},{"Device Type":"End Host","Asset Type":"Physical Device","Device Vendor":"Alcatel","Device Name":"unknown","Device IP":"10.40.16.12","Network View":"discovery_view"},{"Device Type":"End Host","Asset Type":"Physical Device","Device Vendor":"Alcatel","Device Name":"unknown","Device IP":"10.40.16.11","Network View":"discovery_view"},{"Device Type":"Router","Asset Type":"Physical Device","Device Vendor":"Cisco","Device Model":"WS-C3560X-48T-S","OS Version":"15.0(2)SE8","Device Name":"ni-mri-core.inca.infoblox.com","Chassis S/N":"FDO1523R1Q7","Device IP":"10.40.16.1","Network View":"discovery_view"},{"Device Type":"Switch","Asset Type":"Physical Device","Device Name":"unknown","Device IP":"10.40.16.8","Network View":"discovery_view"}]
        logger.info ("Input Json Data for Device inventory report validation")
        logger.info(json.dumps(cls.test3, sort_keys=True, indent=4, separators=(',', ': ')))


        # IPAMv4 DEVICE NETWORKS

	cls.test4 = [{u'Device Name': u'DELL-PC8024F', u'Network View': u'default', u'Interface IP': u'2620:10a:6000:2810::10', u'Device IP': u'10.40.16.10', u'Device Model': u'Powerconnect 8024F', u'Device Vendor': u'Dell', u'Utilization %': u'0.0', u'IPAM Network': u'2620:10a:6000:2810::/64', u'Device OS Version': u'5.1.2.3'}, {u'Device Name': u'ni-mri-core.inca.infoblox.com', u'Network View': u'default', u'Interface IP': u'10.40.255.1', u'Device IP': u'10.40.16.1', u'Device Model': u'WS-C3560X-48T-S', u'Device Vendor': u'Cisco', u'Utilization %': u'0.3', u'IPAM Network': u'10.40.255.0/24', u'Device OS Version': u'15.0(2)SE8'}, {u'Device Name': u'ni-mri-core.inca.infoblox.com', u'Network View': u'default', u'Interface IP': u'10.40.25.1', u'Device IP': u'10.40.16.1', u'Device Model': u'WS-C3560X-48T-S', u'Device Vendor': u'Cisco', u'Utilization %': u'0.3', u'IPAM Network': u'10.40.25.0/24', u'Device OS Version': u'15.0(2)SE8'}, {u'Device Name': u'ni-mri-core.inca.infoblox.com', u'Network View': u'default', u'Interface IP': u'10.40.36.1', u'Device IP': u'10.40.16.1', u'Device Model': u'WS-C3560X-48T-S', u'Device Vendor': u'Cisco', u'Utilization %': u'0.7', u'IPAM Network': u'10.40.36.0/24', u'Device OS Version': u'15.0(2)SE8'}, {u'Device Name': u'ni-mri-core.inca.infoblox.com', u'Network View': u'default', u'Interface IP': u'10.40.240.1', u'Device IP': u'10.40.16.1', u'Device Model': u'WS-C3560X-48T-S', u'Device Vendor': u'Cisco', u'Utilization %': u'0.3', u'IPAM Network': u'10.40.240.0/24', u'Device OS Version': u'15.0(2)SE8'}, {u'IPAM Network': u'10.255.40.0/24', u'Utilization %': u'0.3', u'Network View': u'default'}, {u'IPAM Network': u'10.40.18.0/24', u'Utilization %': u'0.3', u'Network View': u'default'}, {u'IPAM Network': u'10.40.17.0/24', u'Utilization %': u'0.3', u'Network View': u'default'}, {u'IPAM Network': u'10.40.16.0/24', u'Utilization %': u'2.7', u'Network View': u'default'}]

        #cls.test4=[{"IPAM Network":"219.117.34.140/30","Utilization %":"50.0","Network View":"discovery_view","Device IP":"10.40.16.6","Device Name":"EX4200-24P","Interface IP":"219.117.34.142","Device Model":"EX4200-24P","Device Vendor":"Juniper","Device OS Version":"13.2X50-D15.3"},{"IPAM Network":"219.117.34.128/30","Utilization %":"50.0","Network View":"discovery_view","Device IP":"10.40.16.6","Device Name":"EX4200-24P","Interface IP":"219.117.34.130","Device Model":"EX4200-24P","Device Vendor":"Juniper","Device OS Version":"13.2X50-D15.3"},{"IPAM Network":"10.40.16.0/24","Utilization %":"2.7","Network View":"discovery_view","Device IP":"10.40.16.6","Device Name":"EX4200-24P","Interface IP":"10.40.16.6","Device Model":"EX4200-24P","Device Vendor":"Juniper","Device OS Version":"13.2X50-D15.3"},{"IPAM Network":"10.40.16.0/24","Utilization %":"2.7","Network View":"discovery_view","Device IP":"10.40.16.7","Device Name":"EX2200-48T-4G","Interface IP":"10.40.16.7","Device Model":"EX2200-48T-4G","Device Vendor":"Juniper","Device OS Version":"13.2X51-D20.2"},{"IPAM Network":"10.40.240.0/24","Utilization %":"0.3","Network View":"discovery_view","Device IP":"10.40.16.1","Device Name":"ni-mri-core.inca.infoblox.com","Interface IP":"10.40.240.1","Device Model":"WS-C3560X-48T-S","Device Vendor":"Cisco","Device OS Version":"15.0(2)SE8"}]
        logger.info ("Input Json Data for IPAMv4 Device Networks report validation")
        logger.info(json.dumps(cls.test4, sort_keys=True, indent=4, separators=(',', ': ')))


        # IP ADDRESS INVENTORY

	cls.test5 = [{u'Management Platform': u'Network Insight', u'Managed': u'False', u'Network View': u'default', u'VRF Description': u'', u'IP Address': u'10.40.0.1', u'Vlan ID': u'4040', u'Discovered Name': u'ni-mri-core.inca.infoblox.com', u'VRF Name': u'', u'VRF RD': u'', u'Vlan Name': u'v10-40-0-0'}, {u'Management Platform': u'Network Insight', u'Managed': u'False', u'Network View': u'default', u'VRF Description': u'', u'IP Address': u'10.40.0.103', u'Vlan ID': u'4040', u'Discovered Name': u'', u'VRF Name': u'', u'VRF RD': u'', u'Vlan Name': u'v10-40-0-0'}, {u'Management Platform': u'Network Insight', u'Managed': u'False', u'Network View': u'default', u'VRF Description': u'', u'IP Address': u'10.40.16.1', u'Vlan ID': u'16', u'Discovered Name': u'ni-mri-core.inca.infoblox.com', u'VRF Name': u'', u'VRF RD': u'', u'Vlan Name': u'v10-40-16-0'}]	

        #cls.test5=[{"IP Address":"10.40.0.1","Discovered Name":"ni-mri-core.inca.infoblox.com","Network View":"discovery_view","Managed":"False","Management Platform":"Network Insight","Vlan Name":"v10-40-0-0","Vlan ID":"4040"},{"IP Address":"10.40.0.103","Discovered Name":"","Network View":"discovery_view","Managed":"False","Management Platform":"Network Insight","Vlan Name":"v10-40-0-0","Vlan ID":"4040"},{"IP Address":"10.40.16.1","Discovered Name":"ni-mri-core.inca.infoblox.com","Network View":"discovery_view","Managed":"False","Management Platform":"Network Insight","Vlan Name":"v10-40-16-0","Vlan ID":"16"},{"IP Address":"10.40.16.6","Discovered Name":"EX4200-24P","Network View":"discovery_view","Managed":"False","Management Platform":"Network Insight","Vlan Name":"","Vlan ID":""},{"IP Address":"10.40.16.7","Discovered Name":"EX2200-48T-4G","Network View":"discovery_view","Managed":"False","Management Platform":"Network Insight","Vlan Name":"","Vlan ID":""}]
        logger.info ("Input Json Data for IP address inventory report validation")
        logger.info(json.dumps(cls.test5, sort_keys=True, indent=4, separators=(',', ': ')))



    # DEVICE COMPONENTS
    @pytest.mark.run(order=1)
    def test_1(self):
        # import pdb;pdb.set_trace()

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
	print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print(self.test1)
	print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
	print(results_list)
	print("########################################################")
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
    def test_2(self):
#        import pdb;pdb.set_trace()

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
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print(self.test2)
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print(results_list)
        print("########################################################")
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
    def test_3(self):
#        import pdb;pdb.set_trace()

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
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print(self.test3)
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print(results_list)
	print("########################################################")
        print(result)
	print("########################################################")
        logger.info("-----------------------------------------------------")
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
    def test_4(self):
#        import pdb;pdb.set_trace()

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
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print(self.test4)
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print(results_list)
        print("########################################################")
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
    def test_5(self):
#        import pdb;pdb.set_trace()

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
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print(self.test5)
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print(results_list)
	print("########################################################")
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


#!/usr/bin/env python
__author__ = "Shivasai"
__email__  = "sbandaru@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master + Grid Member                                                        #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415), Threat Analytics, RPZ ,Echo-system  #
########################################################################################

import os
import re
import config
import pytest
import unittest
import logging
import subprocess
import json
from time import sleep
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv
import ib_utils.ib_NIOS as ib_NIOS
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="niosspt_9130.log" ,level=logging.DEBUG,filemode='w')

# Global variables

def display_msg(x=""):
    """ 
    Additional function.
    """
    logging.info(x)
    print(x)

class NIOSSPT_8982(unittest.TestCase):
    
    @pytest.mark.run(order=1)
    def test_000_setup(self):
        """
        Enable DHCP service 
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case setup Started            |")
        display_msg("------------------------------------------------")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties?_return_fields=enable_dhcp", grid_vip=config.grid_vip)
        ref = json.loads(get_ref)[0]['_ref']
        data = {"enable_dhcp":True}
        response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create an ipv4 network")
                assert False
            else:
                print("Success: Create an ipv4 network")
                assert True
        

    @pytest.mark.run(order=2)
    def test_001_Create_Network_Container(self):
        """
        Create network container 
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 1 Execution Started           |")
        display_msg("----------------------------------------------------")
        

        data = {"network": "20.0.0.0/8","network_view": "default","members":[{"_struct": "dhcpmember","ipv4addr":config.grid_vip}]}
        response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create an ipv4 network")
                assert False
            else:
                print("Success: Create an ipv4 network")
                assert True

        print("Restart DHCP Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)

        
    @pytest.mark.run(order=3)
    def test_002_Create_Network_Inside_Container(self):
        """
         Create network under network container
         
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 2 Execution Started           |")
        display_msg("----------------------------------------------------")
        data = {"network": "20.2.0.0/24","network_view": "default","members":[{"_struct": "dhcpmember","ipv4addr":config.grid_vip}]}
        response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create an ipv4 network")
                assert False
            else:
                print("Success: Create an ipv4 network")
                assert True

        print("Restart DHCP Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)

    @pytest.mark.run(order=4)
    def test_003_Create_Another_2_Networks(self):
        """
        Create another network inside the network container
        """
        data = {"network": "20.5.0.0/16","network_view": "default","members":[{"_struct": "dhcpmember","ipv4addr":config.grid_vip}]}
        response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create an ipv4 network")
                assert False
            else:
                print("Success: Create an ipv4 network")
                assert True
        
        data = {"network": "30.0.0.0/8","network_view": "default","members":[{"_struct": "dhcpmember","ipv4addr":config.grid_vip}]}
        response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create an ipv4 network")
                assert False
            else:
                print("Success: Create an ipv4 network")
                assert True
        
        
        print("Restart DHCP Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)

    @pytest.mark.run(order=5)
    def test_004_Create_Auth_Zone(self):
        """
         Create Auth Zone
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 3 Execution Started           |")
        display_msg("----------------------------------------------------")
        data={"fqdn":"niosspt_12002.com",
             "grid_primary": [{"name": config.grid_fqdn, "stealth": False}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data))
        logging.info(response)
        zoneref=response
        zoneref = json.loads(zoneref)
        print(zoneref)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create an ipv4 network")
                assert False
            else:
                print("Success: Create an ipv4 network")
                assert True
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(5)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")


    @pytest.mark.run(order=6)
    def test_005_Create_3Host_Records(self):
        """
         Create tunneling and check if the domain is blacklisted in rpz
         
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 5 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        host_info={"name": "newhost1.niosspt_12002.com","network_view": "default","configure_for_dns": False,"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "20.2.0.7","mac": "a:b:c:d:e:f"}]}
        host_ref=ib_NIOS.wapi_request('POST',object_type='record:host',fields=json.dumps(host_info))
        logging.info(host_ref)
        print (host_ref)
        if type(host_ref) == tuple:
            if host_ref[0]==400 or host_ref[0]==401:
                print("Failure: Create an ipv4 network")
                assert False
            else:
                print("Success: Create an ipv4 network")
                assert True
                
        host_info={"name": "newhost2.niosspt_12002.com","network_view": "default","configure_for_dns": False,"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "20.2.0.16","mac": "a:b:c:d:e:5"}]}
        host_ref=ib_NIOS.wapi_request('POST',object_type='record:host',fields=json.dumps(host_info))
        logging.info(host_ref)
        print (host_ref)
        if type(host_ref) == tuple:
            if host_ref[0]==400 or host_ref[0]==401:
                print("Failure: Create an ipv4 network")
                assert False
            else:
                print("Success: Create an ipv4 network")
                assert True
                
        host_info={"name": "newhost3.niosspt_12002.com","network_view": "default","configure_for_dns": False,"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "20.5.0.11","mac": "a:b:c:d:e:4"}]}
        host_ref=ib_NIOS.wapi_request('POST',object_type='record:host',fields=json.dumps(host_info))
        logging.info(host_ref)
        print (host_ref)
        if type(host_ref) == tuple:
            if host_ref[0]==400 or host_ref[0]==401:
                print("Failure: Create an ipv4 network")
                assert False
            else:
                print("Success: Create an ipv4 network")
                assert True
                
                
    @pytest.mark.run(order=7)
    def test_006_Query_For_Hostrecords_Under_Network(self):
        """
         Query for host records for network under 20.2.0.0
         
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 5 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        host_ref=ib_NIOS.wapi_request('GET',object_type='record:host?network=20.2.0.0/24')
        print(host_ref)
        if "20.5.0.11" in host_ref:
            assert False
        else:
            assert True

    @pytest.mark.run(order=8)
    def test_007_Associate_Another_Network_IPaddress_To_Newhost3(self):
        """
        Associate another network IP address to the existing host record, 'newhost3' associated with '20.5.0.11' and '30.38.1.5'
        """
        
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 5 Execution Started           |")
        display_msg("----------------------------------------------------")
        host_record=ib_NIOS.wapi_request('GET',object_type='record:host?ipv4addr=20.5.0.11')
        host_record_ref = json.loads(host_record)[0]['_ref']
        print(host_record_ref)
        host_info={"name": "newhost3.niosspt_12002.com","configure_for_dns": False,"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "20.5.0.11","mac": "a:b:c:d:e:4"},{"configure_for_dhcp": True,"ipv4addr": "30.38.1.5","mac": "a:b:c:d:e:5"}]}
        host_ref=ib_NIOS.wapi_request('PUT',ref=host_record_ref, fields=json.dumps(host_info))
        logging.info(host_ref)
        print (host_ref)
        if type(host_ref) == tuple:
            if host_ref[0]==400 or host_ref[0]==401:
                print("Failure: Create an ipv4 network")
                assert False
            else:
                print("Success: Create an ipv4 network")
                assert True
                

    @pytest.mark.run(order=9)
    def test_008_Query_For_Hostrecords_Under_Network(self):
        """
         Query for host records for network under 20.2.0.0
         
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 8 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        host_ref=ib_NIOS.wapi_request('GET',object_type='record:host?network=20.2.0.0/24')
        print(host_ref)
        if "20.5.0.11" in host_ref or "30.38.1.5" in host_ref:
            assert False
        else:
            assert True


    @pytest.mark.run(order=10)
    def test_009_clean_up(self):
        """
        Delete Auth zone and networks
         
        """
        
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case clean up Started              |")
        display_msg("----------------------------------------------------")
        
        zone_ref=ib_NIOS.wapi_request('GET',object_type='zone_auth?fqdn=niosspt_12002.com')
        print(zone_ref)
        zone_ref = json.loads(zone_ref)[0]['_ref']
        response = ib_NIOS.wapi_request('DELETE',ref=zone_ref)
        
        network = ib_NIOS.wapi_request('GET',object_type='networkcontainer?network=20.0.0.0/8')
        network_ref = json.loads(network)[0]['_ref']
        response = ib_NIOS.wapi_request('DELETE',ref=network_ref)
        
        print(response)
        network = ib_NIOS.wapi_request('GET',object_type='network?network=30.0.0.0/8')
        network_ref = json.loads(network)[0]['_ref']
        response = ib_NIOS.wapi_request('DELETE',ref=network_ref)
        print(response)
        
        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure")
                assert False
            else:
                print("Success")
                assert True
        
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(5)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(30)

#!/usr/bin/env python
__author__ = "Shivasai"
__email__  = "sbandaru@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master + Discovery Member                                      #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415)  #
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

class NIOSSPT_12067(unittest.TestCase):
    
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

        
    @pytest.mark.run(order=3)
    def test_002_Create_Network_Inside_Container(self):
        """
         Create network under network container
         
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 2 Execution Started           |")
        display_msg("----------------------------------------------------")
        data = {"network": "30.30.30.0/24","network_view": "default","members":[{"_struct": "dhcpmember","ipv4addr":config.grid_vip}]}
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
    def test_003_Create_Auth_Zone(self):
        """
         Create Auth Zone
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 3 Execution Started           |")
        display_msg("----------------------------------------------------")
        data={"fqdn":"niosspt_12067.com",
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


    @pytest.mark.run(order=5)
    def test_004_Create_Host_Records(self):
        """
        Create host record with cli credentials 
         
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 4 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        host_info={"name": "newhost.niosspt_12067.com","network_view": "default","configure_for_dns": True,"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "30.30.30.30","mac": "3a:3b:3c:3d:3e:3f"}],"use_cli_credentials":True,"cli_credentials": [{"credential_group": "default","credential_type": "ENABLE_SSH","user": "shiva","password":"shivasaipassword"},{"credential_group": "default","credential_type": "SSH","user": "shiva","password":"shivasaipassword"}]}
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
                
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(5)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(30)

                

    @pytest.mark.run(order=6)
    def test_005_Export_Host_Records_CSV(self):
        """
        Export Host records data in csv format
         
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 5 Execution Started           |")
        display_msg("----------------------------------------------------") 
        logging.info("Starting csv export")
        data = {"_object":"allrecords",
                "zone":"niosspt_12067.com",
                "view":"default"}
        
        create_file = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=csv_export")
        display_msg(create_file)
        result = json.loads(create_file)
        token = result['token']
        url = result['url']
        display_msg("Token : "+token)
        display_msg("URL : "+url)
        display_msg("Create the fileop function to dowload the csv file to the specified url")
        sleep(5)
        os.system('curl -k -u admin:infoblox -H "Content-type:application/force-download" -O %s'%(url))
        display_msg("CSV export successful")
        sleep(5)
        
        filename = os.system("ls -ltr Zonechilds.csv")
        print(filename)
        if filename !=0:
            assert False
        else:
            assert True
            
    

    @pytest.mark.run(order=7)
    def test_006_Check_Pssword_IN_CSV(self):
        """
        check if host record password is visible in csv file
         
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 6 Execution Started           |")
        display_msg("----------------------------------------------------")   

        file = open("Zonechilds.csv","r")
        content = file.readlines()
        print(content)
        if "shivasaipassword" in content:
            assert False
        else:
            assert True
            
    @pytest.mark.run(order=8)
    def test_007_Clean_up(self):
        """
        Clean up, remove network container and zones
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case clean up           |")
        display_msg("----------------------------------------------------")
        
        zone_ref=ib_NIOS.wapi_request('GET',object_type='zone_auth?fqdn=niosspt_12067.com')
        print(zone_ref)
        zone_ref = json.loads(zone_ref)[0]['_ref']
        response = ib_NIOS.wapi_request('DELETE',ref=zone_ref)
        
        network = ib_NIOS.wapi_request('GET',object_type='networkcontainer?network=30.0.0.0/8')
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
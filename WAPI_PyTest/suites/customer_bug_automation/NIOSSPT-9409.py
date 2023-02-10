__author__ = "Shekhar Srivastava"
__email__  = "ssrivastava@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master                                                                      #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V815)                                      #
########################################################################################

import re
import config
import pytest
import unittest
import logging
import subprocess
import os
import json
import ib_utils.ib_NIOS as ib_NIOS
from time import sleep
import commands
import json, ast
import requests
import time
import pexpect
import getpass
import sys
import csv
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="niosspt_9409.log" ,level=logging.DEBUG,filemode='w')

def display_msg(x=""):
    """ 
    Additional function.
    """
    logging.info(x)
    print(x)

def restart_services(grid=config.grid_vip):
    """
    Restart Services
    """
    display_msg("Restart services")
    get_ref =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=grid)
    ref = json.loads(get_ref)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices", fields=json.dumps(data),grid_vip=grid)
    sleep(20)

class NIOSSPT_9409(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_001_Create_New_AuthZone(self):
        """
        Create authoritative forward mapping zone niosspt_9409.com
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 1 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Create an authoritative FM zone niosspt_9409.com")
        data = {"fqdn": "niosspt_9409.com",
                "view":"default",
                "grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Create an authoritative FM zone rfe_7507.com")
            assert False
        restart_services()
        
        display_msg("-----------Test Case 1 Execution Completed------------")


    @pytest.mark.run(order=2)
    def test_002_Create_host_record_with_multiple_ip_address(self):
        """
        Create host address host.niosspt_9409.com with more than 1 ip addresses
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 2 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Create host record with multiple ip addresses")
        data = {"ipv4addrs": [{"configure_for_dhcp": True,
                               "ipv4addr": "10.0.0.1",
                               "mac": "11:11:11:11:11:15"},
                              {"configure_for_dhcp": True,
                               "ipv4addr": "10.0.0.2",
                               "mac": "21:11:11:11:11:15"}], 
                "name": "host.niosspt_9409.com",
                "view": "default"}
        response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Create an authoritative FM zone rfe_7507.com")
            assert False
        restart_services()
        
        display_msg("-----------Test Case 2 Execution Completed------------")

    @pytest.mark.run(order=3)
    def test_003_perform_csv_export(self):
        """
        Perform CSV Export for all records
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 3 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Create the fileop function to download csv_export object with host record")
        data = {"_object":"allrecords",
                "zone":"niosspt_9409.com",
                "view":"default"}
        create_file = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=csv_export")
        display_msg(create_file)
        result = json.loads(create_file)
        token = result['token']
        url = result['url']
        display_msg("Token : "+token)
        display_msg("URL : "+url)
        display_msg("Create the fileop function to dowload the csv file to the specified url")
        os.system('curl -k -u admin:infoblox -H "Content-type:application/force-download" -O %s'%(url))
        display_msg("CSV export successful")

        display_msg("-----------Test Case 3 Execution Completed------------")

    @pytest.mark.run(order=4)
    def test_004_count_host_name_occurance_in_exported_csv(self):
        """
        Count the number of rows exported in CSV exported file.
        Since one host record is created, there should be no more than 3 rows.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 4 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Validate the csv file downloaded")
        with open("Zonechilds.csv") as f:
            data = f.read()
            count=(data.count("host.niosspt_9409.com"))
            display_msg("Number of rows exported = "+str(count))
            if int(count) >  3:
                display_msg("Failure: Multiple entries for the same hostaddress found on CSV file")
                assert False
        os.system('rm -rf Zonechilds.csv')
        
        display_msg("-----------Test Case 4 Execution Completed------------")
            
    @pytest.mark.run(order=-1)
    def test_cleanup(self):
        """
        cleanup method: Delete all the objects created from this script.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|          Test Case cleanup Started           |")
        display_msg("------------------------------------------------")
        
        display_msg("Delete auth zone niosspt_9409.com")
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth')
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            if ref['fqdn'] == 'niosspt_9409.com':
                response = ib_NIOS.wapi_request('DELETE', ref = ref['_ref'])
                display_msg(response)
                if type(response) == tuple:
                    display_msg("Failure: Delete auth zone niosspt_9409.com")
                    assert False
                break

        display_msg("-----------Test Case cleanup Completed------------")
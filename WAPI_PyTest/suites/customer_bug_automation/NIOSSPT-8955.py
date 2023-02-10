#!/usr/bin/env python
__author__ = "Shiva Sai"
__email__  = "sbandaru@infoblox.com"

import os
import re
import config
import pytest
import unittest
import logging
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="niosspt-8955.log" ,level=logging.DEBUG,filemode='w')

def display_msg(x=""):
    """ 
    Additional function.
    """
    logging.info(x)
    print(x)

class NIOSSPT_8955(unittest.TestCase):


    @pytest.mark.run(order=1)
    def test_001_create_zone(self):
        """
        Add an Authorative Zone niosspt_8955.com.
        Verify that the Zone is created with no errors.
        """
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 1 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Create a zone niosspt_8955.com")
        data = {"fqdn": "niosspt_8955.com", 
                "view":"default", 
                "grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                assert False
        display_msg("-----------Test Case 1 Execution Completed------------")
        
    @pytest.mark.run(order=2)
    def test_002_create_host_record(self):
        """
        Add a Host record test in the zone
        Verify that the record is added with no errors.
        """
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 2 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Create a Host record in the Zone")
        data = {
                    "ipv4addrs": [
                        {
                            "configure_for_dhcp": False,
                        "ipv4addr": "10.0.0.2"
                        }   ],
                    "name": "test.niosspt_8955.com",
                    "view": "default"
                }
        response = ib_NIOS.wapi_request('POST',object_type="record:host",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                assert False
        display_msg("-----------Test Case 2 Execution Completed------------")
        
        
    @pytest.mark.run(order=3)
    def test_003_create_alias_record(self):
        """
        Add an A Alias record test in the zone
        Verify that the record should not added.
        """
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 3 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Create an A Alias record in the Zone")
        data = {
                    "name": "test.niosspt_8955.com",
                    "target_name": "q.ss.com",
                    "target_type": "A",
                    "view": "default"
                }
        response = ib_NIOS.wapi_request('POST',object_type="record:alias",fields=json.dumps(data))
        display_msg(response)
        expected = "Alias record as there is already Host record with the same name in the zone"
        if type(response) == tuple:
            if expected in str(response):
                assert True    
        else :
            assert False
        display_msg("-----------Test Case 3 Execution Completed------------")


    @pytest.mark.run(order=4)
    def test_004_remove_host_record(self):
        display_msg("Get host record ref and delete it")
        res = ib_NIOS.wapi_request('GET',object_type='record:host')
        print res
        res = json.loads(res)
        zone_ref=res[0]['_ref']
        response=ib_NIOS.wapi_request('DELETE', object_type=zone_ref)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                assert False
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(35)
        display_msg("-----------Test Case 4 Execution Completed------------")

    @pytest.mark.run(order=5)
    def test_005_create_alias_record(self):
        """
        Add an A Alias record test in the zone
        Verify that the record should added.
        """
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 5 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Create an A Alias record in the Zone")
        data = {
                    "name": "test.niosspt_8955.com",
                    "target_name": "q.ss.com",
                    "target_type": "A",
                    "view": "default"
                }
        response = ib_NIOS.wapi_request('POST',object_type="record:alias",fields=json.dumps(data))
        display_msg(response)
        if type(response) != tuple:
            assert True
        else :
            assert False
        display_msg("-----------Test Case 5 Execution Completed------------")

    @pytest.mark.run(order=6)     
    def test_006_create_host_record(self):
        """
        Add a Host record test in the zone
        Verify that the host record is should not add.
        """
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 6 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Create a Host record in the Zone")
        data = {
                    "ipv4addrs": [
                        {
                            "configure_for_dhcp": False,
                        "ipv4addr": "10.0.0.2"
                        }   ],
                    "name": "test.niosspt_8955.com",
                    "view": "default"
                }
        response = ib_NIOS.wapi_request('POST',object_type="record:host",fields=json.dumps(data))
        display_msg(response)
        expected = "HOST record as there is already Alias record with the same name in the zone"
        if type(response) == tuple:
            if expected in str(response):
                assert True
        else :
            assert False
        display_msg("-----------Test Case 6 Execution Completed------------")


        
    @pytest.mark.run(order=7)
    def test_007_cleanup(self):
        """ clean up section,
            removing zone created in testcase1
            """

        display_msg("----------------------------------------------------")
        display_msg("|          Test Cleanup          |")
        display_msg("----------------------------------------------------")
        display_msg("Get zone ref and delete it")
        res = ib_NIOS.wapi_request('GET',object_type='zone_auth?fqdn=niosspt_8955.com')
        res = json.loads(res)
        zone_ref=res[0]['_ref']
        response=ib_NIOS.wapi_request('DELETE', object_type=zone_ref)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                assert False
        display_msg("-----------Test Case 7 Execution Completed------------")

    

#!/usr/bin/env python
__author__ = "Shivasai"
__email__  = "sbandaru@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. SA GRID                                                                          #
#  2. Licenses : DNS, DHCP, Grid                                                       #
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
import commands
import json, ast
import requests
from time import sleep as sleep
import ib_utils.ib_NIOS as ib_NIOS


def display_msg(x):
    """ 
    Additional function.
    """
    logging.info(x)
    print(x)

class Network(unittest.TestCase):
    @pytest.mark.run(order=1)
    def  test_01_NIOSSPT_8776_disable_default_dns_view(self):
        display_msg("\n----------------------------------------------------")
        display_msg("|          Test Case 1 Execution Started           |")
        display_msg("----------------------------------------------------")

        print("\nNIOSSPT-8776 Disable Default DNS view\n")
        print("\nGet ref for view\n")
        """
            Disabling default dns view using viewref
        """
            
        response=ib_NIOS.wapi_request('GET', object_type="view")
        viewref = json.loads(response)[0]['_ref']
        print(viewref)
        print("\nDisable default view\n")
        data={"disable":True}
        response=ib_NIOS.wapi_request('PUT', object_type="view",fields=json.dumps(data),ref=viewref)
        print(response)
        print("Successfully Disabled DNS Default view\n")
        print (response)
        logging.info(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                assert False
                    
        display_msg("-----------Test Case 1 Execution Completed------------")


    @pytest.mark.run(order=2)
    def test_02_NIOSSPT_8776_create_zone(self):
        display_msg("\n----------------------------------------------------")
        display_msg("|          Test Case 2 Execution Started           |")
        display_msg("----------------------------------------------------")
        print("\nCreating Authorative Zone")
            
        """
                Add an Authorative Zone niosspt_8776.com.
                Add Grid master as Grid primary.
                Verify that the Zone is created with no errors.
        """

        data={"fqdn":"4niosspt_8776.com",
              "grid_primary": [{"name": config.grid_fqdn, "stealth": False}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data))
        print(response)
        logging.info(response)
        zoneref=response
        zoneref = json.loads(zoneref)
        print(zoneref)            
            
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
               assert False

        print("Successfully Created zone after disabling default dns view")
        display_msg("-----------Test Case 2 Execution Completed------------")

        """ Testcase cleanup """
            
	response1 = ib_NIOS.wapi_request('DELETE',ref=zoneref)
        print(response1)
        if type(response1) == tuple:
            if response1[0]==400 or response1[0]==401:
                assert False
        print("deleted zone and enable dns view as part of cleanup")
        response=ib_NIOS.wapi_request('GET', object_type="view")
        viewref = json.loads(response)[0]['_ref']
        print(viewref)
        print("\nEnable default view\n")
        data={"disable":False}
        response=ib_NIOS.wapi_request('PUT', object_type="view",fields=json.dumps(data),ref=viewref)
        print(response)

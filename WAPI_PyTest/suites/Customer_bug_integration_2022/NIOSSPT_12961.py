#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Vindya V K"
__email__  = "vvk@infoblox.com"

#############################################################################
# Grid Set up required:                                                     #
#  1. Grid Master (SA)  - 8.6.2 build                                       #
#  2. Licenses : DNS, DHCP, Grid, NIOS                                      #
#                                                                           #
#############################################################################

#### REQUIRED LIBRARIES ####
import os
import config
import pytest
import unittest
import logging
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import sys
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util


#####################################################################################################
# STEPS TO REPRODUCE:                                                                               #
# 1. Create an authoritative zone 'ksk.com' and assign it to Grid Master.                          #
# 2. Edit the DNS properties of the zone 'ksk.com' and override DNSSEC properties.                 #
# 3. Change the 'Key-signing Key Rollover Interval' to 17 Years and try to save it.                 #
# 4. Validate the expected error message as below -                                                 #
#    'The KSK rollover interval must be between one day and the number of days to January 19, 2038' #
#                                                                                                   #
#####################################################################################################


logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="niosspt_12961.log" ,level=logging.DEBUG,filemode='w')

def display_message(x=""):
    # Additional function used to log and print with a single line
    logging.info(x)
    print(x)

class NIOSSPT_12961(unittest.TestCase):

# Create an authoratative zone - ksk.com
# Assign Master as grid primary
# Validate if ksk.com is created or not

    @pytest.mark.run(order=1)
    def test_001_Create_auth_zone(self):
        display_message("\n========================================================\n")
        display_message("Creating an Authoratative zone - ksk.com")
        display_message("\n========================================================\n")

        data = {"fqdn":"ksk.com","view":"default","grid_primary":[{"name":config.grid_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_message(response)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_message("FAILURE: Create authoratative zone.")
            assert False
        else:
            display_message()
            display_message("\n--------------------------------------------------------\n")
            display_message("Validating Authoratative zone - ksk.com")
            display_message("\n--------------------------------------------------------\n")

            response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=ksk.com", grid_vip=config.grid_vip)
            response=json.loads(response)[0]
            display_message(response)

            if 'ksk.com' in response['_ref']:
                display_message(response["_ref"])
                display_message("SUCCESS: Authoratative Zone 'ksk.com' was created!")
                assert True
            else:
                display_message("FAILURE: Authoratative Zone 'ksk.com' was NOT created!")
                assert False

        display_message("\n***************. Test Case 1 Execution Completed .***************\n") # requires restart


# Under grid:dns properties of the zone set 'Key-signing Key Rollover Interval' as 17
# Validate the error message 'The KSK rollover interval must be between one day and the number of days to January 19, 2038'

    @pytest.mark.run(order=2)
    def test_002_Updating_DNSSEC_properties(self):
        display_message("\n========================================================\n")
        display_message("Updating DNSSEC properties - setting KSK rollover as 17 years")
        display_message("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[0]['_ref']
        print(ref)

        data = {"dnssec_key_params":{"ksk_rollover": 536467742}}
        response = ib_NIOS.wapi_request('PUT', ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)

        message = "The KSK rollover interval must be between one day and the number of days to January 19, 2038"

        if message in response[1]:
            display_message("SUCCESS: KSK was not set to 17 years as the KSK rollover interval must be between one day and the number of days to January 19, 2038")
            assert True
        else:
            display_message("FAILURE: Something went wrong.. looks like KSK rollover was set to 17 years.")
            assert False

        display_message("\n***************. Test Case 2 Execution Completed .***************\n") # requires restart



### cleanup function

    @pytest.mark.run(order=3)
    def test_003_cleanup_objects(self):
        print("\n============================================\n")
        print("CLEANUP: Reverting back to original setup...")
        print("\n============================================\n")

        get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth")
        for ref in json.loads(get_ref):
            if 'ksk.com' in ref["_ref"]:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])

        print("\n***************. Test Case 3 Execution Completed .***************\n")


# Restart services
    @pytest.mark.run(order=4)
    def test_004_Restart_services(self):

        display_message("\n========================================================\n")
        display_message("Restarting Services")
        display_message("\n========================================================\n")

        grid = ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(35)

        display_message("\n***************. Test Case 4 Execution Completed .***************\n")


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
# 1. Create an authoratative zone 'test.com' and under grid properties > DNSSEC > assign the record #
#    type as - NSEC.                                                                                #
# 2. Sign the zone 'test.com'                                                                       #
# 3. Create a CNAME record '"abc.test.com' [double quote before abc.test.com is on purpose]         #
# 4. Try to edit the name of the CNAME record by removing the double quotes.                        #
# 5. Validate if the name of the CNAME record is updated.                                           #
#                                                                                                   #
##### NOTE #####                                                                                    #
#               Since this bug is still open at the time of automation, you will notice the         #
#               following error - "The record 'abc.test.com' already exist"                         #
#                                                                                    ##### NOTE #####
#                                                                                                   #
# 6. Create another CNAME record 'xyz.com' [This time DONOT add the double quote]                   #
# 7. Try to edit the name of the new CNAME record by removing 'x' and making it 'yz.com'            #
# 8. Validate if the name of the CNAME record is updated                                            #
#                                                                                                   #
#####################################################################################################


logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="niosspt_12909.log" ,level=logging.DEBUG,filemode='w')

def display_message(x=""):
    # Additional function used to log and print with a single line
    logging.info(x)
    print(x)


class NIOSSPT_12909(unittest.TestCase):

# Create an authoratative zone - test.com
# Assign Master as grid primary
# Validate if test.com is created or not

    @pytest.mark.run(order=1)
    def test_001_Create_auth_zone(self):
        display_message("\n========================================================\n")
        display_message("Creating an Authoratative zone - test.com")
        display_message("\n========================================================\n")

        data = {"fqdn":"test.com","view":"default","grid_primary":[{"name":config.grid_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_message(response)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_message("FAILURE: Create authoratative zone.")
            assert False
        else:
            display_message()
            display_message("\n--------------------------------------------------------\n")
            display_message("Validating Authoratative zone - test.com")
            display_message("\n--------------------------------------------------------\n")

            response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=test.com", grid_vip=config.grid_vip)
            response=json.loads(response)[0]
            display_message(response)

            if 'test.com' in response['_ref']:
                display_message(response["_ref"])
                display_message("SUCCESS: Authoratative Zone 'test.com' was created!")
                assert True
            else:
                display_message("FAILURE: Authoratative Zone 'test.com' was NOT created!")
                assert False

        display_message("\n***************. Test Case 1 Execution Completed .***************\n") # requires restart


# Under grid:dns properties assign next_secure_type as NSEC
# Validate if its assigned

    @pytest.mark.run(order=2)
    def test_002_Updating_grid_dns_properties(self):
        display_message("\n========================================================\n")
        display_message("Assigning next_secure_type as NSEC")
        display_message("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[0]['_ref']
        print(ref)

        data = {"dnssec_key_params":{"next_secure_type": "NSEC"}}
        response = ib_NIOS.wapi_request('PUT', ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)

        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_message("FAILURE: Update next_secure_type to NSEC.")
            assert False
        else:
            display_message()
            display_message("\n--------------------------------------------------------\n")
            display_message("Validating if next_secure_typeis updated to NSEC")
            display_message("\n--------------------------------------------------------\n")

            response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=test.com", grid_vip=config.grid_vip)
            response=json.loads(response)[0]
            display_message(response)

            if 'test.com' in response['_ref']:
                display_message(response["_ref"])
                display_message("SUCCESS: grid:dns was successfully updated with next_secure_type as NSEC!")
                assert True
            else:
                display_message("FAILURE: grid:dns was NOT updated with next_secure_type as NSEC!")
                assert False

        display_message("\n***************. Test Case 2 Execution Completed .***************\n") # requires restart



# Restart services
    @pytest.mark.run(order=3)
    def test_003_Restart_services(self):

        display_message("\n========================================================\n")
        display_message("Restarting Services")
        display_message("\n========================================================\n")

        grid = ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(35)

        display_message("\n***************. Test Case 3 Execution Completed .***************\n")


# Sign the zone 'test.com'
# Validate if 'test.com' was signed successfully

    @pytest.mark.run(order=4)
    def test_004_Sign_auth_zone(self):

        display_message("\n========================================================\n")
        display_message("Signing authoratative zone 'test.com'")
        display_message("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth?fqdn=test.com', grid_vip=config.grid_vip)
        get_ref = json.loads(get_ref)[0]['_ref']

        data = {"operation":"SIGN"}
        response = ib_NIOS.wapi_request('POST', object_type=get_ref + "?_function=dnssec_operation", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_message(response)

        display_message("\n--------------------------------------------------------\n")
        display_message("Validating signing of Authoratative zone 'test.com'")
        display_message("\n--------------------------------------------------------\n")

        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_message("FAILURE: Signig zone 'test.com'")
            assert False

        else:
            display_message("SUCCESS: Signing zone 'test.com'")
            assert True

        display_message("\n***************. Test Case 4 Execution Completed .***************\n")


# Create a CNAME record '"abc.test.com' [double quote before abc.test.com is on purpose]
# Validate if the CNAME record is created

    @pytest.mark.run(order=5)
    def test_005_Create_CNAME_record(self):
        display_message("\n========================================================\n")
        display_message('Creating CNAME record - "abc.test.com')
        display_message("\n========================================================\n")

        data = {"name":"\"abc.test.com","canonical": "com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:cname", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_message(response)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_message("FAILURE: Create CNAME record.")
            assert False
        else:
            display_message()
            display_message("\n--------------------------------------------------------\n")
            display_message("Validating CNAME record - \"abc.test.com")
            display_message("\n--------------------------------------------------------\n")

            response = ib_NIOS.wapi_request('GET', object_type="record:cname?name=\"abc.test.com", grid_vip=config.grid_vip)
            response=json.loads(response)[0]
            display_message(response)

            if '\"abc.test.com' in response['name']:
                display_message("SUCCESS: CNAME record \"abc.test.com was successfully created!")
                assert True
            else:
                display_message("FAILURE: CNAME record \"abc.test.com was NOT created!")
                assert False

        display_message("\n***************. Test Case 5 Execution Completed .***************\n") # requires restart


# Try to edit the name of the CNAME "abc.test.com record by removing the double quotes
# Validate if it was updated successfully without errors
#### This case will fail now was this bug is still open ####

    @pytest.mark.run(order=6)
    def test_006_Update_CNAME_record(self):

        display_message("\n========================================================\n")
        display_message("Updating CNAME record by removing the double quotes in the name of CNAME record")
        display_message("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="record:cname?name=\"abc.test.com", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[0]['_ref']
        display_message(ref)

        data = {"name":"abc.test.com","canonical": "com"}
        response = ib_NIOS.wapi_request('PUT', ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        display_message(response[1])

        message="The record 'test.com' already exist"

        if message in response[1]:
            display_message("FAILURE: Bug is still open. CNAME record is not Updated!")
            assert False
        else:
            display_message("SUCCESS: CNAME record was successfully Updated")
            assert True

        display_message("\n***************. Test Case 6 Execution Completed .***************\n")


# Validating if the name of CNAME record is updated to abc.test.com
#### This case will fail now was this bug is still open ####

    @pytest.mark.run(order=7)
    def test_007_Validate_CNAME_record(self):

        display_message("\n========================================================\n")
        display_message("Validating if the name of CNAME record is updated")
        display_message("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="record:cname?name=abc.test.com", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[0]['_ref']
        display_message(ref)

        if 'abc.test.com' in response['_ref']:
            display_message(response["_ref"])
            display_message("SUCCESS: CNAME record 'abc.test.com' was successfully updated!")
            assert True
        else:
            display_message("FAILURE: CNAME record 'abc.test.com' was NOT updated!")
            assert False

        display_message("\n***************. Test Case 7 Execution Completed .***************\n")


# Create another CNAME record xyz.test.com
# Validate if CNAME record xyz.test.com was successfully created

    @pytest.mark.run(order=8)
    def test_008_Create_CNAME_record(self):
        display_message("\n========================================================\n")
        display_message('Creating CNAME record - xyz.test.com')
        display_message("\n========================================================\n")

        data = {"name":"xyz.test.com","canonical": "vvk"}
        response = ib_NIOS.wapi_request('POST', object_type="record:cname", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_message(response)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_message("FAILURE: Create CNAME record.")
            assert False
        else:
            display_message()
            display_message("\n--------------------------------------------------------\n")
            display_message("Validating CNAME record - xyz.test.com")
            display_message("\n--------------------------------------------------------\n")

            response = ib_NIOS.wapi_request('GET', object_type="record:cname?name=xyz.test.com", grid_vip=config.grid_vip)
            response=json.loads(response)[0]
            display_message(response)

            if 'xyz.test.com' in response['_ref']:
                display_message(response["_ref"])
                display_message("SUCCESS: CNAME record xyz.test.com was successfully created!")
                assert True
            else:
                display_message("FAILURE: CNAME record xyz.test.com was NOT created!")
                assert False

        display_message("\n***************. Test Case 8 Execution Completed .***************\n") # requires restart


# Try to update the name of CNAME record from 'xyz.test.com' to 'yz.test.com'
# Validate if it got updated successfully

    @pytest.mark.run(order=9)
    def test_009_Update_CNAME_record(self):

        display_message("\n========================================================\n")
        display_message("Updating CNAME record by removing the 'x' in 'xyz.test.com'")
        display_message("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="record:cname?name=xyz.test.com", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[0]['_ref']
        display_message(ref)

        data = {"name":"yz.test.com","canonical": "vvk"}
        response = ib_NIOS.wapi_request('PUT', ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        display_message(response[1])

        message="The record 'test.com' already exist"

        if message in response[1]:
            display_message("FAILURE: Bug is still open. CNAME record is not Updated!")
            assert False
        else:
            display_message("SUCCESS: CNAME record was successfully Updated")
            assert True

        display_message("\n***************. Test Case 9 Execution Completed .***************\n")


# Validating if the name of CNAME record is updated to yz.test.com

    @pytest.mark.run(order=10)
    def test_010_Validate_CNAME_record(self):

        display_message("\n========================================================\n")
        display_message("Validating if the name of CNAME record is updated")
        display_message("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="record:cname?name=yz.test.com", grid_vip=config.grid_vip)
        response=json.loads(get_ref)[0]['_ref']
        display_message(response)

        if 'yz.test.com' in response:
            display_message("SUCCESS: CNAME record 'yz.test.com' was successfully updated!")
            assert True
        else:
            display_message("FAILURE: CNAME record 'yz.test.com' was NOT updated!")
            assert False

        display_message("\n***************. Test Case 10 Execution Completed .***************\n")


### cleanup function

    @pytest.mark.run(order=11)
    def test_011_cleanup_objects(self):
        print("\n============================================\n")
        print("CLEANUP: Reverting back to original setup...")
        print("\n============================================\n")

        get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth")
        for ref in json.loads(get_ref):
            if 'test.com' in ref["_ref"]:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])

        print("\n***************. Test Case 11 Execution Completed .***************\n")


# Restart services
    @pytest.mark.run(order=12)
    def test_012_Restart_services(self):

        display_message("\n========================================================\n")
        display_message("Restarting Services")
        display_message("\n========================================================\n")

        grid = ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(35)

        display_message("\n***************. Test Case 12 Execution Completed .***************\n")


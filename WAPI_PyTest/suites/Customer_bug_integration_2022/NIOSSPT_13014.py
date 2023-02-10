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
# 1. Create a middle authoritative zone 'test.com' and assign it to Grid Master.                    #
# 2. Create a deligated sub zone 'dlg.test.com' assigned to delegated name server with FQDN from    #
#    parent zone of the middle zone and assign any IP to it. - 'srv.com' : 1.2.3.4.                 #
# 3. Create a Authoratative parent zone 'com' for middle zone 'test.com'.                           #
# 4. Validate if 'srv' record of type-A is created under parent zone 'com'.                         #
# 5. Create a Foward zone - 'redhat.com' and forward it to a dummy IP -11.12.13.14.                              #
# 6. Create Authoratative sub zones 'ord.redhat.com' and 'dfw.redhat.com' under 'redhat.com'.       #
# 7. Delete the forward zone 'redhat.com'.                                                          #
# 8. Create another Authoratative zone with same name 'redhat.com' and validate if it got created   #
#    without any errors.                                                                            #
#                                                                                                   #
#####################################################################################################

logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="niosspt_12975.log" ,level=logging.DEBUG,filemode='w')

def display_message(x=""):
    # Additional function used to log and print with a single line
    logging.info(x)
    print(x)


class NIOSSPT_12975(unittest.TestCase):

# Create a middle authoratative zone - test.com
# Assign Master as grid primary
# Validate if test.com is created or not

    @pytest.mark.run(order=1)
    def test_001_Create_middle_auth_zone(self):
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


# Create a deligated sub zone - dlg.test.com
# Deligate it to srv.com with ip 1.2.3.4
# Validate if deligated zone dlg.test.com is created

    @pytest.mark.run(order=2)
    def test_002_Create_deligated_sub_zone(self):
        display_message("\n========================================================\n")
        display_message("Creating an deligated sub zone - dlg.test.com")
        display_message("\n========================================================\n")

        data = {"fqdn":"dlg.test.com","view":"default","delegate_to":[{"name":'srv.com',"address":"1.2.3.4"}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_delegated", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_message(response)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_message("FAILURE: Create deligated sub zone.")
            assert False
        else:
            display_message()
            display_message("\n--------------------------------------------------------\n")
            display_message("Validating Deligated zone - dlg.test.com")
            display_message("\n--------------------------------------------------------\n")

            response = ib_NIOS.wapi_request('GET', object_type="zone_delegated?fqdn=dlg.test.com", grid_vip=config.grid_vip)
            response=json.loads(response)[0]
            display_message(response)

            if 'test.com' in response['_ref']:
                display_message(response["_ref"])
                display_message("SUCCESS: Deligated Sub Zone 'dlg.test.com' was created!")
                assert True
            else:
                display_message("FAILURE: Deligated Sub Zone 'dlg.test.com' was NOT created!")
                assert False

        display_message("\n***************. Test Case 2 Execution Completed .***************\n") # requires restart



# Create a Authoratative parent zone - 'com'
# Assign grid master as grid primary
# Validate if auth zone com is created

    @pytest.mark.run(order=3)
    def test_003_Create_auth_parent_zone(self):
        display_message("\n========================================================\n")
        display_message("Creating parent authoratative zone - com")
        display_message("\n========================================================\n")

        data = {"fqdn":"com","view":"default","grid_primary":[{"name":config.grid_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_message(response)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_message("FAILURE: Create parent authoratative zone.")
            assert False
        else:
            display_message()
            display_message("\n--------------------------------------------------------\n")
            display_message("Validating parent authoratative zone - com")
            display_message("\n--------------------------------------------------------\n")

            response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=test.com", grid_vip=config.grid_vip)
            response=json.loads(response)[0]
            display_message(response)

            if 'test.com' in response['_ref']:
                display_message(response["_ref"])
                display_message("SUCCESS: parent authoratative Zone 'com' was created!")
                assert True
            else:
                display_message("FAILURE: parent authoratative Zone 'com' was NOT created!")
                assert False

        display_message("\n***************. Test Case 3 Execution Completed .***************\n") # requires restart


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


# perform GET operation for A record
# Validate if a record 'srv' of type A is created under parent zone 'com'

    @pytest.mark.run(order=5)
    def test_005_validating_A_record_created_in_parent_zone(self):
        display_message("\n========================================================\n")
        display_message("Validating A record 'srv' created in parent zone 'com'")
        display_message("\n========================================================\n")

        response = ib_NIOS.wapi_request('GET', object_type="record:a?name=srv.com", grid_vip=config.grid_vip)
        response=json.loads(response)[0]
        display_message(response)

        if 'srv.com' in response['_ref']:
            display_message(response["_ref"])
            display_message("SUCCESS: A record 'srv' was successfully created under parent zone 'com'!")
            assert True
        else:
            display_message("FAILURE: A record 'srv' was NOT created under parent zone 'com'!")
            assert False

        display_message("\n***************. Test Case 5 Execution Completed .***************\n")



# Create a Forward zone 'redhat.com'
# Forward it to a dummy IP 11.12.13.14
# Verify if the zone is created successfully


    @pytest.mark.run(order=6)
    def test_006_Create_forward_zone(self):
        display_message("\n========================================================\n")
        display_message("Creating forward mapping zone - redhat.com")
        display_message("\n========================================================\n")

        data = {"fqdn":"redhat.com","view":"default","forward_to":[{"address": "11.12.13.14", "name": "dummy"}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_forward", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_message(response)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_message("FAILURE: Create forward zone.")
            assert False
        else:
            display_message()
            display_message("\n--------------------------------------------------------\n")
            display_message("Validating forward zone - redhat.com")
            display_message("\n--------------------------------------------------------\n")

            response = ib_NIOS.wapi_request('GET', object_type="zone_forward?fqdn=redhat.com", grid_vip=config.grid_vip)
            response=json.loads(response)[0]
            display_message(response)

            if 'redhat.com' in response['_ref']:
                display_message(response["_ref"])
                display_message("SUCCESS: Forward Zone 'redhat.com' was created!")
                assert True
            else:
                display_message("FAILURE: Forward Zone 'redhat.com' was NOT created!")
                assert False

        display_message("\n***************. Test Case 6 Execution Completed .***************\n") # requires restart



# Create authoratative sub zone 'ord.redhat.com'
# Assign grid primary as grid Master
# Verify if the zone is created successfully

    @pytest.mark.run(order=7)
    def test_007_Create_auth_sub_zone(self):
        display_message("\n========================================================\n")
        display_message("Creating an Authoratative sub zone - ord.redhat.com")
        display_message("\n========================================================\n")

        data = {"fqdn":"ord.redhat.com","view":"default","grid_primary":[{"name":config.grid_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_message(response)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_message("FAILURE: Create authoratative sub zone.")
            assert False
        else:
            display_message()
            display_message("\n--------------------------------------------------------\n")
            display_message("Validating Authoratative sub zone - ord.redhat.com")
            display_message("\n--------------------------------------------------------\n")

            response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=ord.redhat.com", grid_vip=config.grid_vip)
            response=json.loads(response)[0]
            display_message(response)

            if 'ord.redhat.com' in response['_ref']:
                display_message(response["_ref"])
                display_message("SUCCESS: Authoratative sub Zone 'ord.redhat.com' was created!")
                assert True
            else:
                display_message("FAILURE: Authoratative sub Zone 'ord.redhat.com' was NOT created!")
                assert False

        display_message("\n***************. Test Case 7 Execution Completed .***************\n") # requires restart



# Create authoratative sub zone 'dfw.redhat.com'
# Assign grid primary as grid Master
# Verify if the zone is created successfully

    @pytest.mark.run(order=8)
    def test_008_Create_auth_sub_zone(self):
        display_message("\n========================================================\n")
        display_message("Creating an Authoratative sub zone - dfw.redhat.com")
        display_message("\n========================================================\n")

        data = {"fqdn":"dfw.redhat.com","view":"default","grid_primary":[{"name":config.grid_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_message(response)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_message("FAILURE: Create authoratative sub zone.")
            assert False
        else:
            display_message()
            display_message("\n--------------------------------------------------------\n")
            display_message("Validating Authoratative sub zone - dfw.redhat.com")
            display_message("\n--------------------------------------------------------\n")

            response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=dfw.redhat.com", grid_vip=config.grid_vip)
            response=json.loads(response)[0]
            display_message(response)

            if 'dfw.redhat.com' in response['_ref']:
                display_message(response["_ref"])
                display_message("SUCCESS: Authoratative sub Zone 'dfw.redhat.com' was created!")
                assert True
            else:
                display_message("FAILURE: Authoratative sub Zone 'dfw.redhat.com' was NOT created!")
                assert False

        display_message("\n***************. Test Case 8 Execution Completed .***************\n") # requires restart



# Restart services
    @pytest.mark.run(order=9)
    def test_009_Restart_services(self):

        display_message("\n========================================================\n")
        display_message("Restarting Services")
        display_message("\n========================================================\n")

        grid = ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(35)

        display_message("\n***************. Test Case 9 Execution Completed .***************\n")



# Delete forward zone 'redhat.com'
# Validate if the zone got deleted successfully.

    @pytest.mark.run(order=10)
    def test_010_Delete_forward_zone(self):
        display_message("\n========================================================\n")
        display_message("Deleting Forward zone - redhat.com")
        display_message("\n========================================================\n")

        response = ib_NIOS.wapi_request('GET', object_type="zone_forward?fqdn=redhat.com", grid_vip=config.grid_vip)
        response=json.loads(response)[0]
        ref=response['_ref']
        display_message(ref)
        delete=ib_NIOS.wapi_request('DELETE', object_type=ref, grid_vip=config.grid_vip)

        if delete[0]==400 or delete[0]==401 or delete[0]==404 or delete[0]==500:
            display_message("FAILURE: Delete forward zone redhat.com.")
            assert False
        else:
            display_message()
            display_message("\n--------------------------------------------------------\n")
            display_message("Validating deletion of forward zone - redhat.com")
            display_message("\n--------------------------------------------------------\n")

            response = ib_NIOS.wapi_request('GET', object_type="zone_forward", grid_vip=config.grid_vip)
            response=json.loads(response)
            display_message(response)

            if response==[]:
                display_message("SUCCESS: Authoratative sub Zone 'dfw.redhat.com' was created!")
                assert True
            else:
                display_message("FAILURE: Authoratative sub Zone 'dfw.redhat.com' was NOT created!")
                assert False

        display_message("\n***************. Test Case 10 Execution Completed .***************\n") # requires restart


# Create Authoratative zone 'redhat.com'
# Validate if the auth zone got created without any errors

    @pytest.mark.run(order=11)
    def test_011_Create_auth_zone(self):
        display_message("\n========================================================\n")
        display_message("Creating an Authoratative zone - redhat.com")
        display_message("\n========================================================\n")

        data = {"fqdn":"redhat.com","view":"default","grid_primary":[{"name":config.grid_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_message(response)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_message("FAILURE: Create authoratative zone.")
            assert False
        else:
            display_message()
            display_message("\n--------------------------------------------------------\n")
            display_message("Validating Authoratative zone - redhat.com")
            display_message("\n--------------------------------------------------------\n")

            response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=redhat.com", grid_vip=config.grid_vip)
            response=json.loads(response)[0]
            display_message(response)

            if 'redhat.com' in response['_ref']:
                display_message(response["_ref"])
                display_message("SUCCESS: Authoratative Zone 'redhat.com' was created!")
                assert True
            else:
                display_message("FAILURE: Authoratative Zone 'redhat.com' was NOT created!")
                assert False

        display_message("\n***************. Test Case 11 Execution Completed .***************\n") # requires restart


### cleanup function

    @pytest.mark.run(order=12)
    def test_012_cleanup_objects(self):
        print("\n============================================\n")
        print("CLEANUP: Reverting back to original setup...")
        print("\n============================================\n")

        get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth")
        for ref in json.loads(get_ref):
            if 'com' in ref["_ref"]:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])

        print("\n***************. Test Case 12 Execution Completed .***************\n")


# Restart services
    @pytest.mark.run(order=13)
    def test_013_Restart_services(self):

        display_message("\n========================================================\n")
        display_message("Restarting Services")
        display_message("\n========================================================\n")

        grid = ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(35)

        display_message("\n***************. Test Case 13 Execution Completed .***************\n")


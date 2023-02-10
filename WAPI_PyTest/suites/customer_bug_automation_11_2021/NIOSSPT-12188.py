#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Vindya V K"
__email__  = "vvk@infoblox.com"

#############################################################################
# Grid Set up required:
#  1. Grid Master - 8.5.3
#  2. Licenses : DNS, DHCP, Grid, NIOS
##
#############################################################################

import os
import re
import config
import pytest
import unittest
import logging
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import pexpect
import sys
import subprocess
import time
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util
from logger import logger

class NIOSSPT_12188(unittest.TestCase):

# Add an authoratative zone

    @pytest.mark.run(order=1)
    def test_001_Add_auth_zone(self):
        print("\n============================================\n")
        print("Adding Authoratative zone")
        print("\n============================================\n")

        data = {"fqdn":"test.com","view":"default"}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
        print(response)
        if response[0]==400 or response[0]==401 or response[0]==404:
            print("FAILURE: Failed to create authoratative zone test.com!")
            assert False
        else:
            print("SUCCESS: Authorataive zone test.com has been created!")
            assert True
        print("\n***************. Test Case 1 Execution Completed .***************\n")


# Validating the zone

    @pytest.mark.run(order=2)
    def test_002_validate_auth_zone(self):
        print("\n============================================\n")
        print("Validating Authoratative zone")
        print("\n============================================\n")

        response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=test.com", grid_vip=config.grid_vip)
        response=json.loads(response)

        for ref in response:
            if 'test.com' in ref['_ref']:
                print(ref["_ref"])
                print("SUCCESS: Authoratative Zone 'test.com' was created!")
                assert True
                break
            else:
                continue
                print("FAILURE: Authoratative Zone 'test.com' was NOT created!")
                assert False
        print("\n***************. Test Case 2 Execution Completed .***************\n")


# Creating shared record group srg1

    @pytest.mark.run(order=3)
    def test_003_create_shared_record_group(self):
        print("\n============================================\n")
        print("Creating Shared Record Group 'srg1' ")
        print("\n============================================\n")

        data = {"name":"srg1"}
        response = ib_NIOS.wapi_request('POST', object_type="sharedrecordgroup", fields=json.dumps(data))
        print(response)
        if response[0]==400 or response[0]==401 or response[0]==404:
            print("FAILURE: Failed to create shared record group 'srg1'!")
            assert False
        else:
            print("SUCCESS: Shared record Group 'srg1' has been created!")
            assert True
        print("\n***************. Test Case 3 Execution Completed .***************\n")


# Validating the shared group srg1

    @pytest.mark.run(order=4)
    def test_004_validate_shared_record_group(self):
        print("\n============================================\n")
        print("Validating Shared Record Group")
        print("\n============================================\n")

        response = ib_NIOS.wapi_request('GET', object_type="sharedrecordgroup?name=srg1", grid_vip=config.grid_vip)
        response=json.loads(response)

        for ref in response:
            if 'srg1' in ref['_ref']:
                print(ref["_ref"])
                print("SUCCESS: Shared record group 'srg1' was created!")
                assert True
                break
            else:
                continue
                print("FAILURE: Shared record group 'srg1' was NOT created!")
                assert False
        print("\n***************. Test Case 4 Execution Completed .***************\n")


# Creating shared A record under srg1

    @pytest.mark.run(order=5)
    def test_005_create_shared_A_record(self):
        print("\n============================================\n")
        print("Creating Shared A record under 'srg1' ")
        print("\n============================================\n")

        data = {"ipv4addr": "1.2.3.4", "name": "a", "shared_record_group": "srg1"}
        response = ib_NIOS.wapi_request('POST', object_type="sharedrecord:a", fields=json.dumps(data))
        print(response)
        if response[0]==400 or response[0]==401 or response[0]==404:
            print("FAILURE: Failed to create shared A record!")
            assert False
        else:
            print("SUCCESS: Shared A record has been created!")
            assert True
        print("\n***************. Test Case 5 Execution Completed .***************\n")



# Validating the shared A record

    @pytest.mark.run(order=6)
    def test_006_validate_shared_A_record(self):
        print("\n============================================\n")
        print("Validating Shared A record")
        print("\n============================================\n")

        response = ib_NIOS.wapi_request('GET', object_type="sharedrecord:a?name=a", grid_vip=config.grid_vip)
        response=json.loads(response)

        for ref in response:
            if 'a/srg1' in ref['_ref']:
                print(ref["_ref"])
                print("SUCCESS: Shared A record was created!")
                assert True
                break
            else:
                continue
                print("FAILURE: Shared A record was NOT created!")
                assert False
        print("\n***************. Test Case 6 Execution Completed .***************\n")



# Creating shared record group srg2

    @pytest.mark.run(order=7)
    def test_007_create_shared_record_group(self):
        print("\n============================================\n")
        print("Creating Shared Record Group 'srg2' ")
        print("\n============================================\n")

        data = {"name":"srg2"}
        response = ib_NIOS.wapi_request('POST', object_type="sharedrecordgroup", fields=json.dumps(data))
        print(response)
        if response[0]==400 or response[0]==401 or response[0]==404:
            print("FAILURE: Failed to create shared record group 'srg2'!")
            assert False
        else:
            print("SUCCESS: Shared record Group 'srg2' has been created!")
            assert True
        print("\n***************. Test Case 7 Execution Completed .***************\n")


# Validating the shared group srg2

    @pytest.mark.run(order=8)
    def test_008_validate_shared_record_group(self):
        print("\n============================================\n")
        print("Validating Shared Record Group")
        print("\n============================================\n")

        response = ib_NIOS.wapi_request('GET', object_type="sharedrecordgroup?name=srg2", grid_vip=config.grid_vip)
        response=json.loads(response)

        for ref in response:
            if 'srg2' in ref['_ref']:
                print(ref["_ref"])
                print("SUCCESS: Shared record group 'srg2' was created!")
                assert True
                break
            else:
                continue
                print("FAILURE: Shared record group 'srg2' was NOT created!")
                assert False
        print("\n***************. Test Case 8 Execution Completed .***************\n")


# Creating shared A record under srg2

    @pytest.mark.run(order=9)
    def test_009_create_shared_A_record(self):
        print("\n============================================\n")
        print("Creating Shared A record under 'srg2' ")
        print("\n============================================\n")

        data = {"ipv4addr": "1.2.3.4", "name": "a", "shared_record_group": "srg2"}
        response = ib_NIOS.wapi_request('POST', object_type="sharedrecord:a", fields=json.dumps(data))
        print(response)
        if response[0]==400 or response[0]==401 or response[0]==404:
            print("FAILURE: Failed to create shared A record!")
            assert False
        else:
            print("SUCCESS: Shared A record has been created!")
            assert True
        print("\n***************. Test Case 9 Execution Completed .***************\n")



# Validating the shared A record

    @pytest.mark.run(order=10)
    def test_010_validate_shared_A_record(self):
        print("\n============================================\n")
        print("Validating Shared A record")
        print("\n============================================\n")

        response = ib_NIOS.wapi_request('GET', object_type="sharedrecord:a?name=a", grid_vip=config.grid_vip)
        response=json.loads(response)

        for ref in response:
            if 'a/srg2' in ref['_ref']:
                print(ref["_ref"])
                print("SUCCESS: Shared A record was created!")
                assert True
                break
            else:
                continue
                print("FAILURE: Shared A record was NOT created!")
                assert False
        print("\n***************. Test Case 10 Execution Completed .***************\n")


# Assigning shared record group srg1 to authoratative zone test.com

    @pytest.mark.run(order=11)
    def test_011_assigning_srg1_to_authzone(self):
        print("\n============================================\n")
        print("Assigning shared record srg1 to authoratative zone test.com")
        print("\n============================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="sharedrecordgroup?name=srg1", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[0]['_ref']
        print(ref)

        data = {"name":"srg1", "zone_associations":["test.com"]}
        response = ib_NIOS.wapi_request('PUT', ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if response[0]==400 or response[0]==401 or response[0]==404:
            print("FAILURE: Failed to assign shared record group to the auth zone!")
            assert False
        else:
            print("SUCCESS: shared record group has been assigned to auth zone!")
            assert True
        print("\n***************. Test Case 11 Execution Completed .***************\n")


# Validating zone association

    @pytest.mark.run(order=12)
    def test_012_validate_zone_association(self):
        print("\n============================================\n")
        print("Validating zone association")
        print("\n============================================\n")

        response = ib_NIOS.wapi_request('GET', object_type="sharedrecordgroup?_return_fields=name,zone_associations", grid_vip=config.grid_vip)
        response=json.loads(response)
        shared_record_group=response[0]
        print(shared_record_group)

        values=list(shared_record_group.values())

        if 'test.com' in values[1]:
            print(values[1])
            print("SUCCESS: zone was associated to srg1!")
            assert True
        else:
            print("FAILURE: zone was not associated to srg1!")
            assert False
        print("\n***************. Test Case 12 Execution Completed .***************\n")


# Assigning shared record group srg2 to authoratative zone test.com
# This is expected to fail now as the bug is still not fixed

    @pytest.mark.run(order=13)
    def test_013_assigning_srg2_to_authzone(self):
        print("\n============================================\n")
        print("Assigning shared record srg2 to authoratative zone test.com")
        print("\n============================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="sharedrecordgroup?name=srg2", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[0]['_ref']
        print(ref)

        data = {"name":"srg2", "zone_associations":["test.com"]}
        response = ib_NIOS.wapi_request('PUT', ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if response[0]==400 or response[0]==401 or response[0]==404:
            print("FAILURE: Failed to assign shared record group to the auth zone!")
            assert False
        else:
            print("SUCCESS: shared record group has been assigned to auth zone!")
            assert True
        print("\n***************. Test Case 13 Execution Completed .***************\n")


# Validating zone association
# This is expected to fail now as the bug is still not fixed

    @pytest.mark.run(order=14)
    def test_014_validate_zone_association(self):
        print("\n============================================\n")
        print("Validating zone association")
        print("\n============================================\n")

        response = ib_NIOS.wapi_request('GET', object_type="sharedrecordgroup?_return_fields=name,zone_associations", grid_vip=config.grid_vip)
        response=json.loads(response)
        shared_record_group=response[1]
        print(shared_record_group)

        values=list(shared_record_group.values())

        if 'test.com' in values[1]:
            print(values[1])
            print("SUCCESS: zone was associated to srg2!")
            assert True
        else:
            print("FAILURE: zone was not associated to srg2!")
            assert False
        print("\n***************. Test Case 14 Execution Completed .***************\n")


### cleanup function

    @pytest.mark.run(order=15)
    def test_015_cleanup_objects(self):
        print("\n============================================\n")
        print("CLEANUP: Reverting back to original setup...")
        print("\n============================================\n")


        get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth")
        for ref in json.loads(get_ref):
            if 'test.com' in ref["_ref"]:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])

        get_ref = ib_NIOS.wapi_request('GET',object_type="sharedrecordgroup")
        for ref in json.loads(get_ref):
            if 'srg1' in ref["_ref"]:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])

        get_ref = ib_NIOS.wapi_request('GET',object_type="sharedrecordgroup")
        for ref in json.loads(get_ref):
            if 'srg2' in ref["_ref"]:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])

        print("\n***************. Test Case 15 Execution Completed .***************\n")


#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Vindya V K"
__email__  = "vvk@infoblox.com"

#############################################################################
# Grid Set up required:
#  1. Grid Master
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415)
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

class NIOSSPT_10399(unittest.TestCase):

# Start DNS services on Grid Master

    @pytest.mark.run(order=1)
    def test_001_start_DNS_services(self):
        print("\n============================================\n")
        print("DNS Start Services")
        print("\n============================================\n")


        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        print(get_ref)
        res = json.loads(get_ref)
        for i in res:
            if config.grid_fqdn in i['_ref']:
                data = {"enable_dns": True}
                response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: DNS Start Services on Master")
                        assert False
                else:
                    print("Success: DNS Start Services on Master")
                    assert True



# Create one authoritative Name server group.

    @pytest.mark.run(order=2)
    def test_002_create_auth_name_server(self):
        print("Create an authoritative name server group")

        data = {"name": "nsgroup1",
        "grid_primary": [{"name": config.grid_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="nsgroup", fields=json.dumps(data))
        print response

        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==402:
                print("Failure: Create Authoritative name server group")
                assert False
        else:
            print("Success: Create Authoritative name server group")
            assert True

        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)


# Validating the created Name server group

    @pytest.mark.run(order=3)
    def test_003_Validating_nsgroup1(self):
        print("Validating if the Name server created or not...")

        response = ib_NIOS.wapi_request('GET', object_type="nsgroup", grid_vip=config.grid_vip)
        response=json.loads(response)

        for ref in response:
            if 'nsgroup1' in ref['_ref']:
                # print(ref["_ref"])
                print("SUCCESS: nsgroup1 was created!")
                assert True
            else:
                print("FAILURE: nsgroup1 was NOT created!")
                assert False




# Create one Forward Name server group.

    @pytest.mark.run(order=4)
    def test_004_create_forward_name_server(self):
        print("Create a forward name server group")

        data = {"name": "nsgroup2", "external_servers": [{"name":"nsgroup2", "address": "192.0.0.8"}]}
        response = ib_NIOS.wapi_request('POST', object_type="nsgroup:forwardstubserver", fields=json.dumps(data))
        print response

        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==402:
                print("Failure: Create a forward name server group")
                assert False
        else:
            print("Success: Create a forward name server group")
            assert True

        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)


# Validating the created Name server group

    @pytest.mark.run(order=5)
    def test_005_Validating_nsgroup2(self):
        print("Validating if the Name server created or not...")

        response = ib_NIOS.wapi_request('GET', object_type="nsgroup:forwardstubserver", grid_vip=config.grid_vip)
        response=json.loads(response)

        for ref in response:
            if 'nsgroup2' in ref['_ref']:
                # print(ref["_ref"])
                print("SUCCESS: nsgroup2 was created!")
                assert True
            else:
                print("FAILURE: nsgroup2 was NOT created!")
                assert False



# Create an authoritative zone “lab” and assign the authoritative NS group (nsgroup1)

    @pytest.mark.run(order=6)
    def test_006_create_zone_auth(self):
        print("Create an authoritative zone")

        data = {"fqdn": "lab.com", "view": "default", "ns_group": "nsgroup1"}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
        print response

        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==402:
                print("Failure: Create an authoritative zone")
                assert False
        else:
            print("Success: Create an authoritative zone")
            assert True

        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)

# Validating the created Authoritative zone

    @pytest.mark.run(order=7)
    def test_007_Validating_zone(self):
        print("Validating if the zone is created or not...")

        response = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
        response=json.loads(response)

        for ref in response:
            if 'lab.com' in ref['_ref']:
                # print(ref["_ref"])
                print("SUCCESS: Authoritative Zone was created!")
                assert True
            else:
                print("FAILURE: Authoritative Zone was NOT created!")
                assert False


# Create a subzone “fwd.lab” as forward zone and assign the forward NS group (nsgroup2)

    @pytest.mark.run(order=8)
    def test_008_create_forward_subzone(self):
        print("Create a forward subzone")

        data = {"forward_to": [], "fqdn": "fwd.lab.com", "external_ns_group": "nsgroup2"}
        response = ib_NIOS.wapi_request('POST', object_type="zone_forward", fields=json.dumps(data))
        print response

        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==402 or response[0]==404:
                print("Failure: Create a forward subzone")
                assert False
        else:
            print("Success: Create a forward subzone")
            assert True

        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)

# Validating the created Forward zone

    @pytest.mark.run(order=9)
    def test_009_Validating_zone(self):
        print("Validating if the zone is created or not...")

        response = ib_NIOS.wapi_request('GET', object_type="zone_forward?_return_fields=fqdn", grid_vip=config.grid_vip)
        response=json.loads(response)
        print(response)

        for ref in response:
            if 'fwd.lab.com' in ref['fqdn']:
                # print(ref["_ref"])
                print("SUCCESS: Forward Zone was created!")
                assert True
            else:
                print("FAILURE: Forward Zone was NOT created!")
                assert False



# Create another subzone “sub.fwd.lab” as forward zone and assign the same forward NS group (nsgroup2)

    @pytest.mark.run(order=10)
    def test_010_create_forward_subzone(self):
        print("Create a forward subzone")

        data = {"forward_to": [], "fqdn": "sub.fwd.lab.com", "external_ns_group": "nsgroup2"}
        response = ib_NIOS.wapi_request('POST', object_type="zone_forward", fields=json.dumps(data))
        print response

        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==402:
                print("Failure: Create a forward subzone")
                assert False
        else:
            print("Success: Create a forward subzone")
            assert True

        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)



# Validating the created Forward zone

    @pytest.mark.run(order=11)
    def test_011_Validating_zone(self):
        print("Validating if the zone is created or not...")

        response = ib_NIOS.wapi_request('GET', object_type="zone_forward?_return_fields=fqdn", grid_vip=config.grid_vip)
        response=json.loads(response)
        print(response)

        for ref in response:
            if 'sub.fwd.lab.com' in ref['_ref']:
                # print(ref["_ref"])
                print("SUCCESS: Forward Zone was created!")
                assert True
                break
            else:
                continue
                print("FAILURE: Forward Zone was NOT created!")
                assert False



# Delete the subzone “fwd.zone”, the NS records in the parent zone will be replaced as per the remaining subzone.


    @pytest.mark.run(order=12)
    def test_012_delete_parent_zone(self):
        print("Deleting parent zone...")
        get_ref = ib_NIOS.wapi_request('GET',object_type="zone_forward?_return_fields=fqdn")
        print(get_ref)
        for ref in json.loads(get_ref):
            if ref['fqdn'] == 'fwd.lab.com':
                response =ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])
                print(response)

                if type(response) == tuple:

                    if response[0]==400 or response[0]==401:
                        print("Failure: Deleting parent zone")
                        assert False
                else:
                    print("Success: Deleting parent zone")
                    assert True

# Validate delete for "fwd.lab"

    @pytest.mark.run(order=13)
    def test_013_validate_delete_parent_zone(self):

        output = os.popen("dig @" + config.grid_vip + " fwd.lab.com ns").read()
        output = output.split('\n')
        for i in range(len(output)):
            if output[i] == ";; AUTHORITY SECTION:":

            # fetching the line where the ns group is present, into an array

                ns = output[i + 1]
                ns = ns.split('\t')

                # validation

                if ns[4] == 'SOA':
                    print("Parent zone fwd.lab.com is deleted!")
                    assert True
                else:
                    print("parent zone fwd.lab.com is NOT deleted!")
                    assert False


# Delete the remaining subzone “sub.fwd.lab”

    @pytest.mark.run(order=14)
    def test_014_delete_sub_zone(self):
        print("Deleting sub zone...")
        get_ref = ib_NIOS.wapi_request('GET',object_type="zone_forward?_return_fields=fqdn")
        print(get_ref)
        for ref in json.loads(get_ref):
            if 'sub.fwd.lab.com' in ref['fqdn']:
                response =ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])
                print(response)

                if type(response) == tuple:

                    if response[0]==400 or response[0]==401:
                        print("Failure: Deleting sub zone")
                        assert False
                else:
                    print("Success: Deleting sub zone")
                    assert True

# Validate delete for "sub.fwd.lab"

    @pytest.mark.run(order=15)
    def test_015_validate_delete_sub_zone(self):

        output = os.popen("dig @" + config.grid_vip + " sub.fwd.lab.com ns").read()
        output = output.split('\n')
        for i in range(len(output)):
            if output[i] == ";; AUTHORITY SECTION:":

            # fetching the line where the ns group is present, into an array

                ns = output[i + 1]
                ns = ns.split('\t')
                print(ns[0])
                # validation

                if ns[4] == 'SOA':
                    print("sub zone sub.fwd.lab.com is deleted!")
                    assert True
                else:
                    print("sub zone sub.fwd.lab.com is NOT deleted!")
                    assert False


 #Deleting all the objects that was created

    @pytest.mark.run(order=16)
    def test_cleanup_objects(self):

        get_ref = ib_NIOS.wapi_request('GET',object_type="nsgroup:forwardstubserver")
        for ref in json.loads(get_ref):
            if 'nsgroup2' in ref["_ref"]:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])

        get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth")
        for ref in json.loads(get_ref):
            if 'lab.com' in ref["_ref"]:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])

        get_ref = ib_NIOS.wapi_request('GET',object_type="nsgroup")
        for ref in json.loads(get_ref):
            if 'nsgroup1' in ref["_ref"]:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])

        get_ref = ib_NIOS.wapi_request('GET',object_type="zone_forward")
        for ref in json.loads(get_ref):
            if 'fwd.lab.com' in ref["_ref"]:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])

        get_ref = ib_NIOS.wapi_request('GET',object_type="zone_forward")
        for ref in json.loads(get_ref):
            if 'sub.fwd.lab.com' in ref["_ref"]:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])


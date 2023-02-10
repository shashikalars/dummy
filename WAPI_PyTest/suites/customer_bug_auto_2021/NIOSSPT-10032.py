#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Vindya V K"
__email__  = "vvk@infoblox.com"

#############################################################################
# Grid Set up required:
#  1. Grid Master + 1 member
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

class NIOSSPT_10032(unittest.TestCase):

### Create Forward Mapping zone (test.com) and assign it to Grid Master as primary name server and member as secondary.

    @pytest.mark.run(order=1)
    def test_001_create_FMZ(self):
        print("Create an Forward mapping zone")

        data = {"fqdn": "test.com",
        "grid_primary": [{"name": config.grid_fqdn}],
         "grid_secondaries": [{"name": config.grid_member1_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth?_return_fields=fqdn", fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)
#        print(type(response))
        if type(response) == tuple:
            if response[0] == 400 or response[0] == 401:
                print("Failure: Create an Forward mapping zone")
                assert False
        else:
            print("Success: Create an Forward mapping zone")
            assert True

        print("Restart DNS Services")
        grid = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data = {"member_order":"SIMULTANEOUSLY", "restart_option":"FORCE_RESTART","service_option":"ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)


# Validating the created Forward mapping zone

    @pytest.mark.run(order=2)
    def test_002_Validating_FMZ(self):
        print("Validating if the zone is created or not...")

        response = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
        response=json.loads(response)

        for ref in response:
            if 'test.com' in ref['_ref']:
                # print(ref["_ref"])
                print("SUCCESS: Forward mapping Zone was created!")
                assert True
                break
            else:
                continue
                print("FAILURE: Forward mapping Zone was NOT created!")
                assert False




### Create test Reverse Mapping Zone with CIDR greater than 24 with any RFC 2317 prefix and assign it to Grid Master as primary name server.

    @pytest.mark.run(order=3)
    def test_003_create_RMZ(self):
        print("Create an Reverse mapping zone")

        data = {"fqdn": "10.0.0.0/25",
        "grid_primary": [{"name": config.grid_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
        print(response)
#        print(type(response))

        if type(response) == tuple:
            if response[0] == 400 or response[0] == 401 or response[0] == 402:
                print("Failure: Create an Reverse mapping zone")
                assert False
        else:
            print("Success: Create an Reverse mapping zone")
            assert True

        print("Restart DNS Services")
        grid = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data = {"member_order":"SIMULTANEOUSLY", "restart_option":"FORCE_RESTART","service_option":"ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)


# Validating the created Reverse mapping zone

    @pytest.mark.run(order=4)
    def test_004_Validating_RMZ(self):
        print("Validating if the zone is created or not...")

        response = ib_NIOS.wapi_request('GET', object_type="zone_auth?_return_fields=fqdn", grid_vip=config.grid_vip)
        response=json.loads(response)

        for ref in response:
            if '10.0.0.0/25' in ref['fqdn']:
                # print(ref["_ref"])
                print("SUCCESS: Reverse mapping Zone was created!")
                assert True
                break
            else:
                continue
                print("FAILURE: Reverse mapping Zone was NOT created!")
                assert False




### Create Host record in Forward Mapping zone (test.com) with any name and IP address from Reverse Mapping Zone (10.0.0.0/25)

    @pytest.mark.run(order=5)
    def test_005_create_host_record_in_FMZ(self):
        print("Create a host record in Forward mapping zone")

        data = {"ipv4addrs":[{"ipv4addr": "10.48.2.0"}], "name": "host1.test.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data))
        print(response)
#        print(type(response))

        if type(response) == tuple:
            if response[0] == 400 or response[0] == 401 or response[0] == 402:
                print("Failure: Create a host record in Forward mapping zone")
                assert False
        else:
            print("Success: Create a host record in Forward mapping zone")
            assert True

        print("Restart DNS Services")
        grid = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data = {"member_order":"SIMULTANEOUSLY", "restart_option":"FORCE_RESTART","service_option":"ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)


# Validating the created Host record

    @pytest.mark.run(order=6)
    def test_006_Validating_host_record(self):
        print("Validating if the Host record was created or not...")

        response = ib_NIOS.wapi_request('GET', object_type="record:host", grid_vip=config.grid_vip)
        response=json.loads(response)

        for ref in response:
            if 'host1.test.com' in ref['_ref']:
                # print(ref["_ref"])
                print("SUCCESS: Host record was created!")
                assert True
            else:
                print("FAILURE: Host record was NOT created!")
                assert False



### Start DNS service on Grid Master and member

    @pytest.mark.run(order=7)
    def test_007_start_DNS_services(self):
        print("\n============================================\n")
        print("Start DNS Services")
        print("\n============================================\n")

        # Starting DNS service on Master

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


        # Starting DNS service on Member

        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns?_return_fields=enable_dns", grid_vip=config.grid_vip)
        print(get_ref)
        res = json.loads(get_ref)
        for i in res:
            if config.grid_member1_fqdn in i['_ref']:
                data = {"enable_dns": True}
                response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: DNS Start Services on Member")
                        assert False
                else:
                    print("Success: DNS Start Services on Member")
                    assert True



### Check with "dig" command that SOA serial of the test Forward mapping zone (test.com) are equal on both name servers

    @pytest.mark.run(order=8)
    def test_008_Perform_dig_query_for_SOA_serial(self):

    # performing dig on master

        output = os.popen("dig @"+config.grid_vip+" test.com IN SOA").read()
        print(output)
        output = output.split('\n')
        for i in range(len(output)):
            if output[i] == ";; ANSWER SECTION:":

        # fetching the line where the SOA serial is present into an array

                SOA_serial = output[i+1]
                SOA_serial = SOA_serial.split(' ')


        # storing the serial number to compare after change

                serial_1 = SOA_serial[2]

    # performing dig on member

        output = os.popen("dig @"+config.grid_member1_vip+" test.com IN SOA").read()
        print(output)
        output = output.split('\n')
        for i in range(len(output)):
            if output[i] == ";; ANSWER SECTION:":

        # fetching the line where the SOA serial is present into an array

                SOA_serial = output[i+1]
                SOA_serial = SOA_serial.split(' ')


        # storing the serial number to compare after change

                serial_2 = SOA_serial[2]

        # validating if SOA serials match

        if serial_1 == serial_2 :
            print("SOA SERIALS EQUAL ON BOTH NAME SERVERS!!!")
            assert True
        else:
            print("SOA SERIALS NOT EQUAL!!!")
            assert False


### Make any changes to the RFC 2317 prefix of Reverse mapping zone (10.0.0.0/25)

    @pytest.mark.run(order=9)
    def test_009_Update_RMZ(self):
        print("Update the Reverse mapping zone")

        zone = ib_NIOS.wapi_request('GET',object_type="zone_auth")
        ref_path = json.loads(zone)[0]['_ref']

        data = {"prefix":"rmzPrefix"}
        response = ib_NIOS.wapi_request('PUT', ref_path, fields=json.dumps(data), grid_vip=config.grid_vip)

        print(response)

        if type(response) == tuple:
            if response[0] == 400 or response[0] == 401 or response[0] == 402:
                print("Failure: Update the Reverse mapping zone")
                assert False
        else:
            print("Success: Update the Reverse mapping zone")
            assert True

        print("Restart DNS Services")
        grid = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data = {"member_order":"SIMULTANEOUSLY", "restart_option":"FORCE_RESTART","service_option":"ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)


### Check with dig that SOA serial of the test.com are equal on both name servers (comapre the serial number in test_005 and test_006)

    @pytest.mark.run(order=10)
    def test_010_Perform_dig_query_for_SOA_serial(self):

    # peforming dig on master

        output = os.popen("dig @"+config.grid_vip+" test.com IN SOA").read()
        print(output)
        output = output.split('\n')
        for i in range(len(output)):
            if output[i] == ";; ANSWER SECTION:":

        # fetching the line where the SOA serial is present into an array

                SOA_serial = output[i+1]
                SOA_serial = SOA_serial.split(' ')

        # storing the serial number to compare

                serial_1 = SOA_serial[2]

    # performing dig on member

        output = os.popen("dig @"+config.grid_member1_vip+" test.com IN SOA").read()
        print(output)
        output = output.split('\n')
        for i in range(len(output)):
            if output[i] == ";; ANSWER SECTION:":

        # fetching the line where the SOA serial is present into an array

                SOA_serial = output[i+1]
                SOA_serial = SOA_serial.split(' ')


        # storing the serial number to compare after change

                serial_2 = SOA_serial[2]

        # validating if SOA serials match

        if serial_1 == serial_2 :
            print("SOA SERIALS EQUAL ON BOTH NAME SERVERS!!!")
            assert True
        else:
            print("SOA SERIALS NOT EQUAL!!!")
            assert False


### cleanup function

    @pytest.mark.run(order=11)
    def test_cleanup_objects(self):

        get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth")
        for ref in json.loads(get_ref):
            if 'test.com' in ref["_ref"]:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])

        get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth")
        for ref in json.loads(get_ref):
            if '10.0.0.0' in ref["_ref"]:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])

        get_ref = ib_NIOS.wapi_request('GET',object_type="record:host")
        for ref in json.loads(get_ref):
            if 'host1.test.com' in ref["_ref"]:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])


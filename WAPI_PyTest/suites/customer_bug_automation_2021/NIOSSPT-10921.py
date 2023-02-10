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
import ib_utils.common_utilities as common_util

class NIOSSPT_10921(unittest.TestCase):

## Create a CSV with below headers
## header-network address* netmask* auto_create_reversezone
## NETWORK 10.19.8.0 255.255.255.0 TRUE

    @pytest.mark.run(order=1)
    def test_001_create_CSV_file(self):
        print("Creating test.csv...")

        create= open('test.csv','w')
        create.write("header-network ,address*,netmask*,auto_create_reversezone\nNETWORK,10.19.8.0,255.255.255.0,TRUE")
        print("test.csv is created!")


# start DNS services
    @pytest.mark.run(order=2)
    def test_002_start_DNS_services(self):
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
                    if response[0]==400 or response[0]==401 or response[0]==402:
                        print("Failure: DNS Start Services on Master")
                        assert False
                else:
                    print("Success: DNS Start Services on Master")
                    assert True

# import test.csv file

    @pytest.mark.run(order=3)
    def test_003_import_CSV_file(self):
        print("Importing test.csv file...")

        dir_name = "/mnt/home/vvk"
        base_filename = "test.csv"
        token = common_util.generate_token_from_file(dir_name,base_filename)
        data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"OVERRIDE"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_import")
        response=json.loads(response)
        sleep(30)

        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==402:
                print("Failure: Import test.csv file")
                assert False
        else:
            print("Success: Import test.csv file")
            assert True


        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)


# Validating the created Network

    @pytest.mark.run(order=4)
    def test_004_Validating_network(self):
        print("Validating if the Network 10.19.8.0/24 is created or not...")

        response = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
        response=json.loads(response)

        for ref in response:
            if '10.19.8.0/24' in ref['_ref']:
                # print(ref["_ref"])
                print("SUCCESS: Network 10.19.8.0/24 was created!")
                assert True
            else:
                print("FAILURE: Network 10.19.8.0/24 was NOT created!")
                assert False


# Validating the created Reverse mapping zone

    @pytest.mark.run(order=5)
    def test_005_Validating_zone(self):
        print("Validating if the zone is created or not...")

        response = ib_NIOS.wapi_request('GET', object_type="zone_auth?_return_fields=fqdn", grid_vip=config.grid_vip)
        response=json.loads(response)

        for ref in response:
            if '10.19.8.0/24' in ref['fqdn']:
                # print(ref["_ref"])
                print("SUCCESS: Reverse mapping Zone was created!")
                assert True
            else:
                print("FAILURE: Reverse mapping Zone was NOT created!")
                assert False


# Creating an IPv4 reverse mapping zone 100.0.0.0/16 assigned to Grid Master

    @pytest.mark.run(order=6)
    def test_006_create_RMZ_zone(self):
        print("Create first reverse mapping zone")

        data = {"fqdn": "100.0.0.0/16"}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
        print response

        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==402:
                print("Failure: Create first reverse mapping zone")
                assert False
        else:
            print("Success: Create first reverse mapping zone")
            assert True

        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)


# Validating the created Reverse mapping zone (1)

    @pytest.mark.run(order=7)
    def test_007_Validating_zone(self):
        print("Validating if the zone is created or not...")

        response = ib_NIOS.wapi_request('GET', object_type="zone_auth?_return_fields=fqdn", grid_vip=config.grid_vip)
        response=json.loads(response)

        for ref in response:
            if '100.0.0.0/16' in ref['fqdn']:
                print("SUCCESS: Reverse mapping Zone was created!")
                assert True
                break
            else:
                continue
                print("FAILURE: Reverse mapping Zone was NOT created!")
                assert False


# Creating an IPv4 reverse mapping zone 100.0.0.0/8 assigned to Grid Master

    @pytest.mark.run(order=8)
    def test_008_create_RMZ_zone(self):
        print("Create Second reverse mapping zone")

        data = {"fqdn": "100.0.0.0/8"}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
        print response

        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==402:
                print("Failure: Create Second reverse mapping zone")
                assert False
        else:
            print("Success: Create Second reverse mapping zone")
            assert True

        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)


# Validating the created Reverse mapping zone (2)

    @pytest.mark.run(order=9)
    def test_009_Validating_zone(self):
        print("Validating if the zone is created or not...")

        response = ib_NIOS.wapi_request('GET', object_type="zone_auth?_return_fields=fqdn", grid_vip=config.grid_vip)
        response=json.loads(response)

        for ref in response:
            if '100.0.0.0/8' in ref['fqdn']:
                print("SUCCESS: Reverse mapping Zone was created!")
                assert True
                break
            else:
                continue
                print("FAILURE: Reverse mapping Zone was NOT created!")
                assert False


# Create another CSV file test2.csv with 100.0.0.0 network and netmask 255.255.0.0

    @pytest.mark.run(order=10)
    def test_010_create_CSV_file(self):
        print("Creating test2.csv...")

        create= open('test2.csv','w')
        create.write("header-network ,address*,netmask*,auto_create_reversezone\nNETWORK,100.0.0.0,255.255.0.0,TRUE")
        print("test2.csv created!")


# import test2.csv file

    @pytest.mark.run(order=11)
    def test_011_import_CSV_file(self):
        print("Importing test2.csv file...")

        dir_name = "/mnt/home/vvk"
        base_filename = "test2.csv"
        token = common_util.generate_token_from_file(dir_name,base_filename)
        data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"OVERRIDE"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_import")
        response=json.loads(response)
        sleep(300)

        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==402:
                print("Failure: Import test2.csv file")
                assert False
        else:
            print("Success: Import test2.csv file")
            assert True


        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)


# Validating the created Network

    @pytest.mark.run(order=12)
    def test_012_Validating_zone(self):
        print("Validating if the Network 100.0.0.0/16 is created or not...")

        response = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
        response=json.loads(response)

        for ref in response:
            if '100.0.0.0/16' in ref['_ref']:
                # print(ref["_ref"])
                print("SUCCESS: Network 100.0.0.0/16 was created!")
                assert True
                break
            else:
                continue
                print("FAILURE: Network 100.0.0.0/16 was NOT created!")
                assert False


# Validating the created Reverse mapping zone

    @pytest.mark.run(order=13)
    def test_013_Validating_zone(self):
        print("Validating if the zone is created or not...")

        response = ib_NIOS.wapi_request('GET', object_type="zone_auth?_return_fields=fqdn", grid_vip=config.grid_vip)
        response=json.loads(response)

        for ref in response:
            if '100.0.0.0/16' in ref['fqdn']:
                # print(ref["_ref"])
                print("SUCCESS: Reverse mapping Zone was created!")
                assert True
                break
            else:
                continue
                print("FAILURE: Reverse mapping Zone was NOT created!")
                assert False



# Delete reverse mapping zone 100.0.0.0/16

    @pytest.mark.run(order=14)
    def test_014_delete_RMZ(self):
        print("Deleting Reverse mapping zone 100.0.0.0/16...")

        get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth?_return_fields=fqdn")
        print(get_ref)
        for ref in json.loads(get_ref):
            if '100.0.0.0/16' in ref['fqdn']:
                response =ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])
                print(response)
                print("Reverse Mapping zone 100.0.0.0/16 deleted!")
                assert True
                break
            else:
                continue
                print("Reverse Mapping zone 100.0.0.0/16 NOT deleted!")
                assert False

                # if type(response) == tuple:
                #
                #     if response[0]==400 or response[0]==401 or response[0]==402:
                #         print("Reverse Mapping zone 100.0.0.0/16 NOT deleted!")
                #         assert False
                #     else:
                #         print("Reverse Mapping zone 100.0.0.0/16 deleted!")
                #         assert True


# Delete Network 100.0.0.0/16

    @pytest.mark.run(order=15)
    def test_015_delete_network(self):
        print("Deleting IPv4 network 100.0.0.0/16...")

        get_ref = ib_NIOS.wapi_request('GET',object_type="network")
        print(get_ref)
        for ref in json.loads(get_ref):
            if '100.0.0.0/16' in ref['_ref']:
                response =ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])
                print(response)
                print("Network 100.0.0.0/16 deleted!")
                assert True
                break
            else:
                continue
                print("Network 100.0.0.0/16 NOT deleted!")
                assert False

                # if type(response) == tuple:
                #
                #     if response[0]==400 or response[0]==401 or response[0]==402:
                #         print("Network 100.0.0.0/16 NOT deleted!")
                #         assert False
                #     else:
                #         print("Network 100.0.0.0/16 deleted!")
                #         assert True


# import test2.csv again

    @pytest.mark.run(order=16)
    def test_016_import_CSV_file(self):
        print("Importing test2.csv file again...")

        dir_name = "/mnt/home/vvk"
        base_filename = "test2.csv"
        token = common_util.generate_token_from_file(dir_name,base_filename)
        data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"OVERRIDE"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_import")
        response=json.loads(response)
        sleep(30)

        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==402:
                print("Failure: Import test2.csv file")
                assert False
        else:
            print("Success: Import test2.csv file")
            assert True


        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)


# Validating the created Network

    @pytest.mark.run(order=17)
    def test_017_Validating_network(self):
        print("Validating if the Network 100.0.0.0/16 is created or not...")

        response = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
        response=json.loads(response)

        for ref in response:
            if '100.0.0.0/16' in ref['_ref']:
                # print(ref["_ref"])
                print("SUCCESS: Network 100.0.0.0/16 was created!")
                assert True
                break
            else:
                continue
                print("FAILURE: Network 100.0.0.0/16 was NOT created!")
                assert False


# Validating the created Reverse mapping zone

    @pytest.mark.run(order=18)
    def test_018_Validating_zone(self):
        print("Validating if the zone is created or not...")

        response = ib_NIOS.wapi_request('GET', object_type="zone_auth?_return_fields=fqdn", grid_vip=config.grid_vip)
        response=json.loads(response)

        for ref in response:
            if '100.0.0.0/16' in ref['fqdn']:
                # print(ref["_ref"])
                print("SUCCESS: Reverse mapping Zone was created!")
                assert True
                break
            else:
                continue
                print("FAILURE: Reverse mapping Zone was NOT created!")
                assert False



    @pytest.mark.run(order=19)
    def test_cleanup_objects(self):

        get_ref = ib_NIOS.wapi_request('GET',object_type="network")
        for ref in json.loads(get_ref):
            if 'network' in ref["_ref"]:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])

        get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth")
        for ref in json.loads(get_ref):
            if 'zone_auth' in ref["_ref"]:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])


#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Vindya V K"
__email__  = "vvk@infoblox.com"

#############################################################################
# Grid Set up required:
#  1. Grid Master - 8.6.0
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



class NIOSSPT_10384(unittest.TestCase):

# Configure a IPv6 Network Template and associate 2 IPv6 Fixed Address Templates within the properties of the configured IPv6 Network Template

    @pytest.mark.run(order=1)
    def test_001_Configure_IPv6_Network_Template(self):
        print("Create IPv6 Network template")

        data = {"cidr": 80, "name": "ipv6_network"}
        response = ib_NIOS.wapi_request('POST', object_type="ipv6networktemplate", fields=json.dumps(data))
        print(response)

        if type(response) == tuple:
            if response[0] == 400 or response[0] == 401 or response[0] == 402:
                print("Failure: Create IPv6 Network template")
                assert False
        else:
            print("Success: Create IPv6 Network template")
            assert True

        print("Restart DNS Services")
        grid = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data = {"member_order":"SIMULTANEOUSLY", "restart_option":"FORCE_RESTART","service_option":"ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)



# Validating the created IPv6 Network template

    @pytest.mark.run(order=2)
    def test_002_Validate_IPv6_Network_Template(self):
        fixed_address = ib_NIOS.wapi_request('GET',object_type="ipv6networktemplate", grid_vip=config.grid_vip)
        print(fixed_address)
        for ref in json.loads(fixed_address):
            if 'ipv6_network' in ref['_ref']:
                print("ipv6_network template was created!!")
                assert True
            else:
                print("ipv6_network template was NOT created!!")
                assert False


# IPv6 fixed address template-1

    @pytest.mark.run(order=3)
    def test_003_Configure_IPv6_fixed_address_Template_1(self):
        print("Create IPv6 Fixed address template-1")

        data = {"name": "ipv6_fixed1", "offset": 1, "number_of_addresses": 1}
        response = ib_NIOS.wapi_request('POST', object_type="ipv6fixedaddresstemplate", fields=json.dumps(data))
        print(response)

        if type(response) == tuple:
            if response[0] == 400 or response[0] == 401 or response[0] == 402:
                print("Failure: Create IPv6 Fixed address template-1")
                assert False
        else:
            print("Success: Create IPv6 Fixed address template-1")
            assert True

        print("Restart DNS Services")
        grid = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data = {"member_order":"SIMULTANEOUSLY", "restart_option":"FORCE_RESTART","service_option":"ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)


# Validating the created IPv6 Fixed address template (1)

    @pytest.mark.run(order=4)
    def test_004_Validate_IPv6_fixed_address_Template_1(self):
        fixed_address = ib_NIOS.wapi_request('GET',object_type="ipv6fixedaddresstemplate", grid_vip=config.grid_vip)
        print(fixed_address)
        for ref in json.loads(fixed_address):
            if 'ipv6_fixed1' in ref['_ref']:
                print("ipv6_fixed1 template was created!!")
                assert True
            else:
                print("ipv6_fixed1 template was NOt created!!")
                assert False




# IPv6 fixed address template-2

    @pytest.mark.run(order=5)
    def test_005_Configure_IPv6_fixed_address_Template_2(self):
        print("Create IPv6 Fixed address template-2")

        data = {"name": "ipv6_fixed2", "offset": 2, "number_of_addresses": 1}
        response = ib_NIOS.wapi_request('POST', object_type="ipv6fixedaddresstemplate", fields=json.dumps(data))
        print(response)

        if type(response) == tuple:
            if response[0] == 400 or response[0] == 401 or response[0] == 402:
                print("Failure: Create IPv6 Fixed address template-2")
                assert False
        else:
            print("Success: Create IPv6 Fixed address template-2")
            assert True

        print("Restart DNS Services")
        grid = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data = {"member_order":"SIMULTANEOUSLY", "restart_option":"FORCE_RESTART","service_option":"ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)


# Validating the created IPv6 Fixed address template (2)

    @pytest.mark.run(order=6)
    def test_006_Validate_IPv6_fixed_address_Template_2(self):
        fixed_address = ib_NIOS.wapi_request('GET',object_type="ipv6fixedaddresstemplate", grid_vip=config.grid_vip)
        print(fixed_address)
        for ref in json.loads(fixed_address):
            if 'ipv6_fixed2' in ref['_ref']:
                print("ipv6_fixed2 template was created!!")
                assert True
                break
            else:
                continue
                print("ipv6_fixed2 template was NOT created!!")
                assert False


# associating only one ipv6 fixed address (ipv6_fixed1) template with ipv6 network template

    @pytest.mark.run(order=7)
    def test_007_Update_IPv6_Network_Template(self):
        print("Assign one IPv6 fixed address template to IPv6 Network template")

        net_temp = ib_NIOS.wapi_request('GET',object_type="ipv6networktemplate")
        ref_path = json.loads(net_temp)[0]['_ref']

        data = {"fixed_address_templates": ["ipv6_fixed1"]}
        response = ib_NIOS.wapi_request('PUT', ref_path , fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)

        if type(response) == tuple:
            if response[0] == 400 or response[0] == 401 or response[0] == 402:
                print("Failure: Assign one IPv6 fixed address template to IPv6 Network template")
                assert False
        else:
            print("Success: Assign one IPv6 fixed address template to IPv6 Network template")
            assert True

        print("Restart DNS Services")
        grid = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data = {"member_order":"SIMULTANEOUSLY", "restart_option":"FORCE_RESTART","service_option":"ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)

# Validating output

    @pytest.mark.run(order=8)
    def test_008_Validate_IPv6_Network_Template(self):
        fixed_address = ib_NIOS.wapi_request('GET',object_type="ipv6networktemplate?_return_fields=fixed_address_templates", grid_vip=config.grid_vip)
        print(fixed_address)
        for ref in json.loads(fixed_address):
            if 'ipv6_fixed1' in ref['fixed_address_templates']:
                print(ref['fixed_address_templates'])
                print("ipv6_fixed1 is added to ipv6_network!")
                assert True
            else:
                print("ipv6_fixed1 is NOT added to ipv6_network!")
                assert False




# associating two ipv6 fixed address (ipv6_fixed1, ipv6_fixed2) templates with ipv6 network template

    @pytest.mark.run(order=9)
    def test_009_Update_IPv6_Network_Template(self):
        print("Assign two IPv6 fixed address templates to IPv6 Network template")

        net_temp = ib_NIOS.wapi_request('GET',object_type="ipv6networktemplate")
        ref_path = json.loads(net_temp)[0]['_ref']

        data = {"fixed_address_templates": ["ipv6_fixed1", "ipv6_fixed2"]}
        response = ib_NIOS.wapi_request('PUT', ref_path , fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)


        if type(response) == tuple:
            if response[0] == 400 or response[0] == 401 or response[0] == 402:
                print("Failure: Assign two IPv6 fixed address templates to IPv6 Network template")
                assert True
        else:
            print("Success: Assign two IPv6 fixed address templates to IPv6 Network template")
            assert False

        print("Restart DNS Services")
        grid = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data = {"member_order":"SIMULTANEOUSLY", "restart_option":"FORCE_RESTART","service_option":"ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)


# Validating output

    @pytest.mark.run(order=10)
    def test_010_Validate_IPv6_Network_Template(self):
        fixed_address = ib_NIOS.wapi_request('GET',object_type="ipv6networktemplate?_return_fields=fixed_address_templates")
        for ref in json.loads(fixed_address):
            if 'ipv6_fixed1' in ref['fixed_address_templates']:
                if 'ipv6_fixed2' in ref['fixed_address_templates']:
                    print(ref["fixed_address_templates"])
                    print("ipv6_fixed1 and ipv6_fixed2 added to ipv6_network!")
                    assert False
                else:
                    print("ipv6_fixed2 NOT added to ipv6_network!")
                    assert True


# adding a ipv6 network using the network template

    @pytest.mark.run(order=11)
    def test_011_Adding_ipv6_network_using_template(self):
        print("Adding IPv6 network using network template")

        data = {"network": "fe80::1:0:0:0/80", "template": "ipv6_network"}
        response = ib_NIOS.wapi_request('POST', object_type="ipv6network", fields=json.dumps(data))
        print(response)

        if type(response) == tuple:
            if response[0] == 400 or response[0] == 401 or response[0] == 402:
                print("Failure: Adding IPv6 network using network template")
                assert False
        else:
            print("Success: Adding IPv6 network using network template")
            assert True

        print("Restart DNS Services")
        grid = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data = {"member_order":"SIMULTANEOUSLY", "restart_option":"FORCE_RESTART","service_option":"ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)

# Validating output

    @pytest.mark.run(order=12)
    def test_012_Validating_IPv6_Network_Template(self):
        network = ib_NIOS.wapi_request('GET',object_type="ipv6network")
        for ref in json.loads(network):
            if '80' in ref['_ref']:
                # print(ref["_ref"])
                print("Network is created using Template!")
                assert True
            else:
                print("Network is created WITHOUT using the Template!")
                assert False


# Cleanup Objects

    @pytest.mark.run(order=13)
    def test_cleanup_objects(self):

        get_ref = ib_NIOS.wapi_request('GET',object_type="ipv6networktemplate")
        for ref in json.loads(get_ref):
            if 'ipv6_network' in ref["_ref"]:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])

        get_ref = ib_NIOS.wapi_request('GET',object_type="ipv6fixedaddresstemplate")
        for ref in json.loads(get_ref):
            if 'ipv6_fixed1' in ref["_ref"]:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])

        get_ref = ib_NIOS.wapi_request('GET',object_type="ipv6fixedaddresstemplate")
        for ref in json.loads(get_ref):
            if 'ipv6_fixed2' in ref["_ref"]:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])

        get_ref = ib_NIOS.wapi_request('GET',object_type="ipv6network")
        for ref in json.loads(get_ref):
            if 'fe80::1:0:0:0/80' in ref["network"]:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])


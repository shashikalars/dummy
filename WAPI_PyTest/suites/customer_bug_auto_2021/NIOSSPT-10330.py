#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Vindya V K"
__email__  = "vvk@infoblox.com"

#############################################################################
# Grid Set up required:
#  1. Grid with one GM and one GMC member
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
import sys
import pexpect
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util



def convert_member_to_Master_candidate():
    print("Make the member as Master candidate")

    get_ref = ib_NIOS.wapi_request('GET', object_type='member', grid_vip=config.grid_vip)
    get_ref = json.loads(get_ref)[1]['_ref']


    data = {"master_candidate":True}
    response = ib_NIOS.wapi_request('PUT', ref=get_ref, fields=json.dumps(data),grid_vip=config.grid_vip)
    print(response)

    if type(response) == tuple:
        if response[0] == 400 or response[0] == 401:
            print("Failure: Make the member as Master candidate")
            assert False
        else:
            print("Success: Make the member as Master candidate")
            assert True

class NIOSSPT_10330(unittest.TestCase):

### Configure Grid NTP Properties with External NTP Servers and enable the option “Synchronize the Grid with these External NTP Servers”

    @pytest.mark.run(order=1)
    def test_001_configure_GM_NTP_properties(self):
    
        convert_member_to_Master_candidate()
    
        print("Start NTP service and add external NTP servers")

        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=ntp_setting', grid_vip=config.grid_vip)
        get_ref = json.loads(get_ref)[0]['_ref']


        data = {"ntp_setting":{"enable_ntp": True,"ntp_servers": [{"address": "10.35.114.14", "burst": True, "iburst":True, "preferred": True}]}}
        response = ib_NIOS.wapi_request('PUT', ref=get_ref, fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)

        if type(response) == tuple:
            if response[0] == 400 or response[0] == 401:
                print("Failure: Start NTP service and add external NTP servers")
                assert False
        else:
            print("Success: Start NTP service and add external NTP servers")
            assert True


        print("Restart DNS Services")
        grid = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data = {"member_order":"SIMULTANEOUSLY", "restart_option":"FORCE_RESTART","service_option":"ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)


# Validating the Grid ntp properties

    @pytest.mark.run(order=2)
    def test_002_Validating_grid_ntp_properties(self):
        print("Validate Grid ntp properties for 'enable_ntp': true...")

        get_ref =ib_NIOS.wapi_request('GET',object_type="grid",grid_vip=config.grid_vip)
        ref = json.loads(get_ref)[0]['_ref']
        print(ref)

        response = ib_NIOS.wapi_request('GET',ref=ref,params="grid?_return_fields=ntp_setting",grid_vip=config.grid_vip)
        print(response)
        data = ('"enable_ntp": true')
        for i in data:
                if i in response:
                    print("SUCCESS: Validate Grid ntp properties for 'enable_ntp': true")
                    assert True
                    break
                else:
                    continue
                    print("FAILURE: Validate Grid ntp properties for 'enable_ntp': true")
                    assert False
        print(data)

# Updating member NTP properties - synchronising the member with other ntp servers

    @pytest.mark.run(order=3)
    def test_003_updating_member_NTP_properties(self):
        print("Synchronizing the member with other ntp servers...")


        get_ref = ib_NIOS.wapi_request('GET', object_type="member?_return_fields=ntp_setting", grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            data={"ntp_setting":{"enable_external_ntp_servers": True,
                                "enable_ntp": True,
                                "ntp_servers": [{"address": "10.35.114.14",
                                                "burst": True,
                                                "iburst":True,
                                                "preferred": True}]}}

            response = ib_NIOS.wapi_request('PUT',ref=ref['_ref'],fields=json.dumps(data), grid_vip=config.grid_vip)

        if type(response) == tuple:
            if response[0] == 400 or response[0] == 401:
                print("Failure: Synchronize the member with other ntp servers")
                assert False
        else:
            print("Success: Synchronize the member with other ntp servers")
            assert True


        print("Restart DNS Services")
        grid = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data = {"member_order":"SIMULTANEOUSLY", "restart_option":"FORCE_RESTART","service_option":"ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)


# Validating the Grid Master ntp properties

    @pytest.mark.run(order=4)
    def test_004_Validating_GM_ntp_properties(self):
        print("Validating Grid Master ntp properties for 'enable_external_ntp_servers': false...")

        get_ref =ib_NIOS.wapi_request('GET',object_type="member",grid_vip=config.grid_vip)
        ref = json.loads(get_ref)[0]['_ref']
        print(ref)
        response = ib_NIOS.wapi_request('GET',ref=ref,params="member?_return_fields=ntp_setting",grid_vip=config.grid_vip)
        print(response)
        data = ('"enable_external_ntp_servers": false','"enable_ntp": true')
        for i in data:
                if i in response:
                    print("SUCCESS: Validate Grid Master ntp properties for 'enable_external_ntp_servers': false")
                    assert True
                    break
                else:
                    continue
                    print("FAILURE: Validate Grid Master ntp properties for 'enable_external_ntp_servers': false")
                    assert False
        print(data)


# Validating the Grid MAster Candidate ntp properties

    @pytest.mark.run(order=5)
    def test_005_Validating_GMC_ntp_properties(self):
        print("Validating Grid Master Candidate ntp properties for 'enable_external_ntp_servers': true...")

        get_ref =ib_NIOS.wapi_request('GET',object_type="member",grid_vip=config.grid_vip)
        ref = json.loads(get_ref)[1]['_ref']
        print(ref)
        response = ib_NIOS.wapi_request('GET',ref=ref,params="member?_return_fields=ntp_setting",grid_vip=config.grid_vip)
        print(response)
        data = ('"enable_external_ntp_servers": true','"enable_ntp": true')
        for i in data:
                if i in response:
                    print("SUCCESS: Validate Grid Master Candidate ntp properties for 'enable_external_ntp_servers': true")
                    assert True
                    break
                else:
                    continue
                    print("FAILURE: Validate Grid Master Candidate ntp properties for 'enable_external_ntp_servers': true")
                    assert False
        print(data)

        print("Restart DNS Services")
        grid = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data = {"member_order":"SIMULTANEOUSLY", "restart_option":"FORCE_RESTART","service_option":"ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(120)



# Promote Grid master candidate

    @pytest.mark.run(order=6)
    def test_006_Promote_GMC(self):
        print("Promoting Grid Master Candidate...")

        try:

            child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect("password:")
            child.sendline("infoblox")
            child.expect("Infoblox >")

            child.sendline("set promote_master")
            child.expect(":")
            child.sendline("n")
            child.expect(":")
            child.sendline("y")
            child.expect(":")
            child.sendline("y")
            print("System restart...")
            sleep(300)
            print("SUCCESS: Grid Master Candidate promoted!")
            assert True


        except Exception as e:
            print(e)
            child.close()
            print("FAILURE: Grid Master Candidate not promoted!")
            assert False


        finally:
            child.close()



# Validating the promoted Grid Master Candidate

    @pytest.mark.run(order=7)
    def test_007_Validate_Promoted_GMC(self):
        print("Validating promoted Grid Master Candidate...")

        try:

            child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect("password:")
            child.sendline("infoblox")
            child.expect("Infoblox >")

            child.sendline("show status")
            prom = child.expect("Infoblox > ")
            val = child.before
            print(val)
            # print(type(val))
            child.sendline("exit")

            status = "Grid Status: ID Grid Master"
            if status in val:
                assert True
            else:
                assert False

        except Exception as e:
            print(e)
            child.close()
            print("Exception...")
            print("FAILURE: Grid Master Candidate not promoted as master!")
            assert False


        finally:
            child.close()


# changing the configuration (host_name) of newly promoted gird

    @pytest.mark.run(order=8)
    def test_008_update_new_GM_config(self):
        print("Updating the host name of the newly promoted grid...")

        get_ref = ib_NIOS.wapi_request('GET', object_type='member', grid_vip=config.grid_member1_vip)
        get_ref = json.loads(get_ref)[1]['_ref']


        data = {"host_name":"gmcandidate.com"}
        response = ib_NIOS.wapi_request('PUT', ref=get_ref, fields=json.dumps(data),grid_vip=config.grid_member1_vip)
        print(response)

        if type(response) == tuple:
            if response[0] == 400 or response[0] == 401:
                print("Failure: Update the host name of the newly promoted grid")
                assert False
        else:
            print("Success: Update the host name of the newly promoted grid")
            assert True


        print("Restart DHCP Services")
        grid = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_member1_vip)
        ref = json.loads(grid)[0]['_ref']
        data = {"member_order":"SIMULTANEOUSLY", "restart_option":"FORCE_RESTART","service_option":"ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_member1_vip)
        sleep(20)


    @pytest.mark.run(order=9)
    def test_009_Validating_host_name(self):
        print("Validating the host_name of newly promoted grid...")

        get_ref =ib_NIOS.wapi_request('GET',object_type="member",grid_vip=config.grid_member1_vip)
        ref = json.loads(get_ref)[1]['host_name']
        print(ref)
        if ref == "gmcandidate.com":
            print("SUCCESS: Validate the host_name of newly promoted grid")
            assert True
        else:
            print("FAILURE: Validate the host_name of newly promoted grid")
            assert False


# Clean up code

    @pytest.mark.run(order=10)
    def test_010_Promote_GMC(self):
        print("Resetting the Grid configuration...")

        try:

            child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect("password:")
            child.sendline("infoblox")
            child.expect("Infoblox >")

            child.sendline("set promote_master")
            child.expect("y or n")
            child.sendline("n")
            child.expect("y or n")
            child.sendline("y")
            child.expect("y or n")
            child.sendline("y")
            print("System restart...")
            sleep(300)
            print("SUCCESS: Reset Grid Configuration!")
            assert True


        except Exception as e:
            print(e)
            child.close()
            print("FAILURE: Reset Configuration!")
            assert False


        finally:
            child.close()

# Stop ntp service on Grid Master

    @pytest.mark.run(order=11)
    def test_011_configure_GM_NTP_properties(self):
        print("Stop NTP service and remove external NTP servers")

        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=ntp_setting', grid_vip=config.grid_vip)
        get_ref = json.loads(get_ref)[0]['_ref']


        data = {"ntp_setting":{"enable_ntp": False}}
        response = ib_NIOS.wapi_request('PUT', ref=get_ref, fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)

        if type(response) == tuple:
            if response[0] == 400 or response[0] == 401:
                print("Failure: Stop NTP service and remove external NTP servers")
                assert False
        else:
            print("Success: Stop NTP service and remove external NTP servers")
            assert True


        print("Restart DNS Services")
        grid = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data = {"member_order":"SIMULTANEOUSLY", "restart_option":"FORCE_RESTART","service_option":"ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)




# Disable external_ntp_servers on member

    @pytest.mark.run(order=12)
    def test_012_updating_member_NTP_properties(self):
        print("Disabling external ntp servers on member...")


        get_ref = ib_NIOS.wapi_request('GET', object_type="member?_return_fields=ntp_setting", grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            data={"ntp_setting":{"enable_external_ntp_servers": False,
                                "enable_ntp": False}}

            response = ib_NIOS.wapi_request('PUT',ref=ref['_ref'],fields=json.dumps(data), grid_vip=config.grid_vip)

        if type(response) == tuple:
            if response[0] == 400 or response[0] == 401:
                print("Failure: Disabling external ntp servers on member")
                assert False
        else:
            print("Success: Disabling external ntp servers on member")
            assert True


        print("Restart DNS Services")
        grid = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data = {"member_order":"SIMULTANEOUSLY", "restart_option":"FORCE_RESTART","service_option":"ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)

# changing the hostname to original name

    @pytest.mark.run(order=13)
    def test_013_update_hostname_of_member(self):
        print("Updating the host name of the member...")

        get_ref = ib_NIOS.wapi_request('GET', object_type='member', grid_vip=config.grid_vip)
        get_ref = json.loads(get_ref)[1]['_ref']


        data = {"host_name":config.grid_member1_fqdn}
        response = ib_NIOS.wapi_request('PUT', ref=get_ref, fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)

        if type(response) == tuple:
            if response[0] == 400 or response[0] == 401:
                print("Failure: Renaming the host name of the member to original name")
                assert False
        else:
            print("Success: Renaming the host name of the member to original name")
            assert True


        print("Restart DHCP Services")
        grid = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data = {"member_order":"SIMULTANEOUSLY", "restart_option":"FORCE_RESTART","service_option":"ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)

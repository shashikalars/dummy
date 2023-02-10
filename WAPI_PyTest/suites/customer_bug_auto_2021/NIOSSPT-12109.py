#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Vindya V K"
__email__  = "vvk@infoblox.com"

#############################################################################
# Grid Set up required:
#  1. Grid Master - 8.6.0_412613
#  2. Licenses : DNS, DHCP, Grid, NIOS, RPZ, Threat analytics
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
from logger import logger


def restart_services():

# Restart Services
    grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    sleep(60)


class NIOSSPT_12109(unittest.TestCase):

# Start DNS services on Grid Master

    @pytest.mark.run(order=1)
    def test_001_start_DNS_services(self):
    
        restart_services()
    
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



# add an RPZ zone

    @pytest.mark.run(order=2)
    def test_002_add_an_RPZ_zone(self):
        print("Adding an RPZ zone - rpz.com")

        data = {"fqdn": "rpz.com", "view":"default", "grid_primary": [{"name": config.grid_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_rp", fields=json.dumps(data))
        print(response)

        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==402:
                print("Failure: Adding an RPZ zone - rpz.com")
                assert False
        else:
            print("Success: Adding an RPZ zone - rpz.com")
            assert True

        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)


# Validating the created RPZ zone

    @pytest.mark.run(order=3)
    def test_003_Validating_RPZ_zone(self):
        print("Validating if the RPZ zone is created...")

        response = ib_NIOS.wapi_request('GET', object_type="zone_rp?fqdn=rpz.com", grid_vip=config.grid_vip)
        response=json.loads(response)

        for ref in response:
            if 'rpz.com' in ref['_ref']:
                print(ref["_ref"])
                print("SUCCESS: RPZ Zone was created!")
                assert True
                break
            else:
                continue
                print("FAILURE: RPZ Zone was NOT created!")
                assert False


# Adding RPZ zone to Threat analytics

    @pytest.mark.run(order=4)
    def test_004_Adding_RPZ_zone_to_threat_analytics(self):

        logging.info("adding rpz.com to threat_analytics")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics", grid_vip=config.grid_vip)
        ref1 = json.loads(get_ref)[0]['_ref']

        response = ib_NIOS.wapi_request('GET', object_type="zone_rp?fqdn=rpz.com", grid_vip=config.grid_vip)
        response=json.loads(response)
        for ref in response:
            if 'rpz.com' in ref['_ref']:
                rpz=ref["_ref"]
                print(rpz)

        data = {"dns_tunnel_black_list_rpz_zones": [rpz]}
        output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
        print(output)
        print("Successfully added rpz.com at threat_analytics")


##### Validating RPZ zone in threat analytics

    @pytest.mark.run(order=5)
    def test_005_Validating_RPZ_zone_in_threat_analytics(self):

        logging.info("Validating rpz.com in threat_analytics")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=dns_tunnel_black_list_rpz_zones", grid_vip=config.grid_vip)
        response = json.loads(get_ref)
        # ref1 = json.loads(get_ref)[0]['dns_tunnel_black_list_rpz_zones']

        for ref in response:
            if 'rpz.com' in ref['dns_tunnel_black_list_rpz_zones'][0]:
                print(ref["dns_tunnel_black_list_rpz_zones"])
                print("SUCCESS: RPZ Zone is present in Threat analytics")
                assert True
                break
            else:
                continue
                print("FAILURE: RPZ Zone is not present in Threat analytics")
                assert False




# Adding DNS Resolver

    @pytest.mark.run(order=6)
    def test_006_Adding_DNS_resolver(self):

        logging.info("adding DNS resolver")


        get_ref = ib_NIOS.wapi_request('GET', object_type="grid?_return_fields=dns_resolver_setting", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[0]['_ref']

        print(ref)

        data = {"dns_resolver_setting":{"resolvers":[config.dns_resolver]}}
        response = ib_NIOS.wapi_request('PUT', ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)

        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==402:
                print("Failure: DNS resolver added")
                assert False
        else:
            print("Success: DNS resolver not added")
            assert True


##### Validating addition of DNS resolver

    @pytest.mark.run(order=7)
    def test_007_Validating_DNS_resolver(self):

        logging.info("Validating addition of DNS resolver")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid?_return_fields=dns_resolver_setting", grid_vip=config.grid_vip)
        response = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['dns_resolver_setting']

        for ref in ref1:
            if "10.195.3.10" in ref[0]:
                print(ref["resolvers"])
                print("SUCCESS: DNS resolver is successfully added")
                assert True
                break
            else:
                continue
                print("FAILURE: DNS resolver is not added")
                assert False

# Start TA services on Grid Master

    @pytest.mark.run(order=8)
    def test_008_start_TA_service(self):
        print("\n============================================\n")
        print("Start Threat analytics Service")
        print("\n============================================\n")


        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatanalytics", grid_vip=config.grid_vip)
        print(get_ref)
        res = json.loads(get_ref)
        for i in res:
            if config.grid_fqdn in i['_ref']:
                data = {"enable_service": True}
                response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: Start Threat analytics Service on Master")
                        assert False
                else:
                    print("Success: Start Threat analytics Service on Master")
                    assert True

        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)

##### Validating if TA service is enabled

    @pytest.mark.run(order=9)
    def test_009_Validating_if_TA_service_is_enabled(self):

        logging.info("Validating if TA service is enabled")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatanalytics?_return_fields=status", grid_vip=config.grid_vip)
        response = json.loads(get_ref)
        #ref1 = json.loads(get_ref)[0]['dns_resolver_setting']

        for ref in response:
            if 'WORKING' in ref['status'][0]:
                print(ref["status"])
                print("SUCCESS: TA service is WORKING")
                assert True
                break
            else:
                continue
                print("FAILURE: TA service is not WORKING")
                assert False


# Downloading whitelist
# We are downloading the whitelist twice to verify that the whitelest is in the latest version by verifying the message.
# Validation is a part of this case

    @pytest.mark.run(order=10)
    def test_010_Downloading_whitelist(self):

        logging.info("Enabling autodownload of whitelist")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=enable_whitelist_auto_download", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[0]['_ref']
        print(ref)
        data = {"enable_whitelist_auto_download":True}
        response = ib_NIOS.wapi_request('PUT', ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)


        print("Downloading latest Whitelist")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=last_whitelist_update_version", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        version=json.loads(grid)[0]['last_whitelist_update_version']
        print("CURRENT WHITELIST VERSION IS "+ version)
        data= {"is_whitelist":True}
        request_download = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=download_threat_analytics_whitelist_update",fields=json.dumps(data),grid_vip=config.grid_vip)
        print(request_download)
        grid1 =  ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=last_whitelist_update_version", grid_vip=config.grid_vip)
        version=json.loads(grid1)[0]['last_whitelist_update_version']
        print("UPDATED WHITELIST VERSION IS "+ version)


        print("Downloading latest Whitelist again...")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=last_whitelist_update_version", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"is_whitelist":True}
        request_download = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=download_threat_analytics_whitelist_update",fields=json.dumps(data),grid_vip=config.grid_vip)
        print(request_download)

        new_version=json.loads(grid)[0]['last_whitelist_update_version']

        message="Grid Master already has the latest Threat Analytics whitelist versions. No new files downloaded."
        if (new_version==version) and (message in request_download[1]):
            print("ALREADY UPDATED!\n"+message)
            print("Success: Downloading latest Whitelist")
            assert True
        else:
            print("Failure: Downloading latest Whitelist")
            assert False


# Stop TA services on Grid Master

    @pytest.mark.run(order=11)
    def test_011_stop_TA_service(self):
        print("\n============================================\n")
        print("Stop Threat analytics Service")
        print("\n============================================\n")


        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatanalytics", grid_vip=config.grid_vip)
        print(get_ref)
        res = json.loads(get_ref)
        for i in res:
            if config.grid_fqdn in i['_ref']:
                data = {"enable_service": False}
                response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: Stop Threat analytics Service on Master")
                        assert False
                    else:
                        print("Success: Stop Threat analytics Service on Master")
                        assert True

        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)


##### Validating if TA service is disabled

    @pytest.mark.run(order=12)
    def test_012_Validating_if_TA_service_is_diasbled(self):

        logging.info("Validating if TA service is disabled")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatanalytics?_return_fields=status", grid_vip=config.grid_vip)
        response = json.loads(get_ref)
        #ref1 = json.loads(get_ref)[0]['dns_resolver_setting']

        for ref in response:
            if 'INACTIVE' in ref['status']:
                print(ref["status"])
                print("SUCCESS: TA service is INACTIVE")
                assert True
                break
            else:
                continue
                print("FAILURE: TA service is not INACTIVE")
                assert False



# Deleting RPZ zone in Threat analytics

    @pytest.mark.run(order=13)
    def test_013_Deleting_RPZ_zone_in_threat_analytics(self):

        logging.info("deleting rpz.com in threat_analytics")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics", grid_vip=config.grid_vip)
        ref1 = json.loads(get_ref)[0]['_ref']

        data = {"dns_tunnel_black_list_rpz_zones": []}
        output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
        print(output)



##### Validating if RPZ zone is deleted from threat analytics

    @pytest.mark.run(order=14)
    def test_014_Validating_RPZ_zone_delete_from_threat_analytics(self):

        logging.info("Validating rpz.com in threat_analytics")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=dns_tunnel_black_list_rpz_zones", grid_vip=config.grid_vip)
        response = json.loads(get_ref)
        # ref1 = json.loads(get_ref)[0]['dns_tunnel_black_list_rpz_zones']

        for ref in response:
            if 'dns_tunnel_black_list_rpz_zones' in ref:
                print("FAILURE: RPZ Zone is not deleted from Threat analytics")
                assert False
            else:
                print("SUCCESS: RPZ Zone is deleted from Threat analytics")
                assert True

# cleanup function

    @pytest.mark.run(order=15)
    def test_015_cleanup_objects(self):

        get_ref = ib_NIOS.wapi_request('GET',object_type="zone_rp")
        for ref in json.loads(get_ref):
            if 'zone_rp' in ref["_ref"]:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])


# Validating the if the RPZ zone is deleted

    @pytest.mark.run(order=16)
    def test_016_Validating_deleted_RPZ_zone(self):
        print("Validating if the RPZ zone is deleted...")

        response = ib_NIOS.wapi_request('GET', object_type="zone_rp?_return_fields=fqdn", grid_vip=config.grid_vip)
        response=json.loads(response)

        for ref in response:
            if 'rpz.com' in ref['_ref']:
                print(ref["_ref"])
                print("FAILURE: RPZ Zone is not deleted!")
                assert False
            else:
                print("SUCCESS: RPZ Zone is deleted!")
                assert True

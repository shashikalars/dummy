#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Vindya V K"
__email__  = "vvk@infoblox.com"

#############################################################################
# Grid Set up required:
#  1. Grid Master - 8.5.3
#  2. Licenses : DNS, DHCP, Grid, NIOS, Security ecosystem
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

class NIOSSPT_12032(unittest.TestCase):

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
                if response[0]==400 or response[0]==401:
                    print("Failure: DNS Start Services on Master")
                    assert False
                else:
                    print("Success: DNS Start Services on Master")
                    assert True
        print("Test Case 1 Execution Completed")

# Uploading Version5_Syslog_Session_Template

    @pytest.mark.run(order=2)
    def test_002_upload_Version5_Syslog_Session_Template(self):

        logging.info("Upload Version5_Syslog_Session_Template")
        dir_name="./Syslog_templates/"
        base_filename="Version5_Syslog_Session_Template.json"
        token = common_util.generate_token_from_file(dir_name,base_filename)
        data = {"token": token,"overwrite": True}
        response = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=restapi_template_import", grid_vip=config.grid_vip)
        logging.info(response)
        print response
        logging.info(response)
        res = json.loads(response)
        string = {"overall_status": "SUCCESS","error_message": ""}
        if res == string:
                assert True
        else:
                assert False
        print("Test Case 2 Execution Completed")


# Uploading Version5_Syslog_Action_Template.json

    @pytest.mark.run(order=3)
    def test_003_upload_Version5_Syslog_Action_Template(self):

        logging.info("Upload Version5_Syslog_Action_Template")
        dir_name="./Syslog_templates/"
        base_filename="Version5_Syslog_Action_Template.json"
        token = common_util.generate_token_from_file(dir_name,base_filename)
        data = {"token": token,"overwrite": True}
        response = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=restapi_template_import", grid_vip=config.grid_vip)
        logging.info(response)
        print response
        logging.info(response)
        res = json.loads(response)
        string = {"overall_status": "SUCCESS","error_message": ""}
        if res == string:
                assert True
        else:
                assert False
        print("Test Case 3 Execution Completed")


# Adding Syslog endpoint name with space

    @pytest.mark.run(order=4)
    def test_004_adding_syslog_endpoint_name_with_space(self):

        logging.info("Add syslog endpoint name with space")

        data = {"name":"Sample Endpoint",
        "outbound_member_type":"GM",
        "syslog_servers":[{"address":config.grid_vip, "connection_type": "tcp", "facility": "local0", "format": "formatted", "hostname": "HOSTNAME", "port": 514, "severity": "debug"}],
        "vendor_identifier":"syslog",
        "wapi_user_name":"admin",
        "wapi_user_password":"infoblox",
        "log_level":"DEBUG",
        "template_instance": {"template": "Version5_Syslog_Session_Template"}}

        response = ib_NIOS.wapi_request('POST', object_type="syslog:endpoint?_return_fields=name,syslog_servers", fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)

        get_ref = ib_NIOS.wapi_request('GET', object_type="syslog:endpoint?_return_fields=name,syslog_servers", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[0]['_ref']
        print(ref)

        if response[0]==400 or response[0]==401 or response[0]==402:
            print("Failure: Syslog endpoint name with spaces is not created!")
            assert False
        else:
            print("Success: Syslog endpoint name with spaces has been created!")
            assert True
        print("Test Case 4 Execution Completed")



# Validating if the endpoint is created or not

    @pytest.mark.run(order=5)
    def test_005_Validating_syslog_endpoint(self):
        print("Validating if the syslog Endpoint is created...")

        response = ib_NIOS.wapi_request('GET', object_type="syslog:endpoint", grid_vip=config.grid_vip)
        response=json.loads(response)

        for ref in response:
            if 'Sample%20Endpoint' in ref['_ref']:
                print(ref["_ref"])
                print("SUCCESS: Endpoint was created!")
                assert True
                break
            else:
                continue
                print("FAILURE: Endpoint was NOT created!")
                assert False
            print("Test Case 5 Execution Completed")



# Restart services

    @pytest.mark.run(order=6)
    def test_006_Restart_services(self):
        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)
        print("Test Case 6 Execution Completed")


# Adding Notification to the endpoint

    @pytest.mark.run(order=7)
    def test_007_creating_Notification_in_endpoint(self):

        logging.info("Create Notification in endpoint")

        target= ib_NIOS.wapi_request('GET', object_type="syslog:endpoint?_return_fields=name,syslog_servers", grid_vip=config.grid_vip)
        target_ref=json.loads(target)[0]['_ref']
        print(target_ref)

        data = {"name":"new_notifiaction",
        "notification_target":target_ref,
        "event_type":"DB_CHANGE_DNS_ZONE",
        "notification_action": "RESTAPI_TEMPLATE_INSTANCE",
        "expression_list": [
            {
                "op": "AND",
                "op1_type": "LIST"
            },
            {
                "op": "EQ",
                "op1": "ZONE_TYPE",
                "op1_type": "FIELD",
                "op2": "ZONE_TYPE_AUTHORITATIVE",
                "op2_type": "STRING"
            },
            {
                "op": "ENDLIST"
            }],
        "template_instance": {
            "template": "Version5_Syslog_Action_Template"
        }}

        response = ib_NIOS.wapi_request('POST', object_type="notification:rule", fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule?_return_fields=template_instance,event_type,notification_target,name,expression_list", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[0]['_ref']
        print(ref)
        if response[0]==400 or response[0]==401 or response[0]==402:
            print("Failure: Creating Notification in endpoint Failed!")
            assert False
        else:
            print("Success: Notification successfully created in endpoint!")
            assert True
        print("Test Case 7 Execution Completed")



# Validating if the Notification is created or not

    @pytest.mark.run(order=8)
    def test_008_Validating_Notification(self):
        print("Validating if the Notification is created...")

        response = ib_NIOS.wapi_request('GET', object_type="notification:rule", grid_vip=config.grid_vip)
        response=json.loads(response)

        for ref in response:
            if 'new_notifiaction' in ref['_ref']:
                print(ref["_ref"])
                print("SUCCESS: Notification was created!")
                assert True
                break
            else:
                continue
                print("FAILURE: Notification was NOT created!")
                assert False
            print("Test Case 8 Execution Completed")


# Create an Authoratative zone

    @pytest.mark.run(order=9)
    def test_009_create_authoratative_zone(self):
        print("Create an authoritative zone")

        data = {"fqdn":"zone1.com","view":"default","grid_primary": [{"name": config.grid_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
        print(response)
        if response[0]==400 or response[0]==401 or response[0]==404:
            print("Failure: Create an authoritative zone")
            assert False
        else:
            print("Success: Create an authoritative zone")
            assert True
        print("Test Case 9 Execution Completed")

# Validating if the zone is Created

    @pytest.mark.run(order=10)
    def test_010_Validating_auth_zone(self):
        print("Validating if the Authoratative zone is created...")

        response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=zone1.com", grid_vip=config.grid_vip)
        response=json.loads(response)

        for ref in response:
            if 'zone1.com' in ref['_ref']:
                print(ref["_ref"])
                print("SUCCESS: Authoratative Zone was created!")
                assert True
                break
            else:
                continue
                print("FAILURE: Authoratative Zone was NOT created!")
                assert False
            print("Test Case 10 Execution Completed")

# validating syslog to check if created auth_zone zone1.com is present

    @pytest.mark.run(order=11)
    def test_011_checking_for_presence_of_authzone_in_syslog(self):

        logger.info("checking for zone1.com in syslog")

        os.system("scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@"+config.grid_vip+":/var/log/syslog"+" "+config.run_path)
        cmd="grep -Rc 'zone1.com' messages"

        messages = os.system(cmd)
        print(messages)

        if messages != 0:
            print("SUCCESS: zone1.com is not logged in syslog file")
            assert True
        else:
            print("FAILURE: zone1.com has been logged in syslog file")
            assert False
        print("Test Case 11 Execution Completed")



# editing the Syslog endpoint name without space

    @pytest.mark.run(order=12)
    def test_012_editing_syslog_endpoint_name_without_space(self):

        logging.info("Editing syslog endpoint name without space")

        get_ref = ib_NIOS.wapi_request('GET', object_type="syslog:endpoint?_return_fields=name,syslog_servers", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[0]['_ref']
        print(ref)

        data = {"name":"SampleEndpoint",
        "outbound_member_type":"GM",
        "syslog_servers":[{"address":config.grid_vip, "connection_type": "tcp", "facility": "local0", "format": "formatted", "hostname": "HOSTNAME", "port": 514, "severity": "debug"}],
        "vendor_identifier":"syslog",
        "wapi_user_name":"admin",
        "wapi_user_password":"infoblox",
        "log_level":"DEBUG",
        "template_instance": {"template": "Version5_Syslog_Session_Template"}}

        response = ib_NIOS.wapi_request('PUT', ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)

        if response[0]==400 or response[0]==401 or response[0]==402:
            print("Failure: Syslog name is not updated without space")
            assert False
        else:
            print("Success: Syslog name is updated without space")
            assert True
        print("Test Case 12 Execution Completed")


# Create another Authoratative zone

    @pytest.mark.run(order=13)
    def test_013_create_another_authoratative_zone(self):
        print("Create another authoritative zone")

        data = {"fqdn":"zone2.com","view":"default","grid_primary": [{"name": config.grid_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
        print(response)
        if response[0]==400 or response[0]==401 or response[0]==404:
            print("Failure: Create another authoritative zone")
            assert False
        else:
            print("Success: Create another authoritative zone")
            assert True
        print("Test Case 13 Execution Completed")


# Validating if the second zone is Created

    @pytest.mark.run(order=14)
    def test_014_Validating_second_auth_zone(self):
        print("Validating if the second Authoratative zone is created...")

        response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=zone1.com", grid_vip=config.grid_vip)
        response=json.loads(response)

        for ref in response:
            if 'zone2.com' in ref['_ref']:
                print(ref["_ref"])
                print("SUCCESS: Second Authoratative Zone was created!")
                assert True
                break
            else:
                continue
                print("FAILURE: Second Authoratative Zone was NOT created!")
                assert False
            print("Test Case 14 Execution Completed")


# validating syslog to check if newly created auth_zone zone2.com is present

    @pytest.mark.run(order=15)
    def test_015_checking_for_presence_of_new_authzone_in_syslog(self):

        logger.info("checking for zone2.com in syslog")

        os.system("scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@"+config.grid_vip+":/var/log/syslog"+" "+config.run_path)
        cmd="grep -Rc 'zone2.com' messages"

        messages = os.system(cmd)
        print(messages)

        if messages != 0:
            print("SUCCESS: zone2.com is not logged in syslog file")
            assert True
        else:
            print("FAILURE: zone2.com has been logged in syslog file")
            assert False
        print("Test Case 15 Execution Completed")


### cleanup function

    @pytest.mark.run(order=16)
    def test_016_cleanup_objects(self):

        os.system("rm messages")

        get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth")
        for ref in json.loads(get_ref):
            if 'zone1.com' in ref["_ref"]:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])

        get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth")
        for ref in json.loads(get_ref):
            if 'zone2.com' in ref["_ref"]:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])

        get_ref = ib_NIOS.wapi_request('GET',object_type="syslog:endpoint")
        for ref in json.loads(get_ref):
            if 'SampleEndpoint' in ref["_ref"]:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])

        print("Test Case 16 Execution Completed")


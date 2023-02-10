__author__ = "Aditya G"
__email__  = "adityag@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. Standalone GM                                                                    #
#  2. Licenses : DNS, DHCP, Grid, NIOS                                                 #
########################################################################################

import re
import config
import pytest
import unittest
import logging
import subprocess
import os
import json
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.dig_utility
from time import sleep
import commands
import json, ast
import time
import getpass
import sys
import pexpect



logging.basicConfig(filename='niosspt11390.log', filemode='w', level=logging.DEBUG)



class NIOSSPT_11390(unittest.TestCase):

    @pytest.mark.order(order=1)
    def test001_Stop_DNS_service(self):
        logging.info("Stop DNS Service")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns')
        logging.info(get_ref)
        for ref in json.loads(get_ref):
            if config.grid_fqdn in ref['_ref']:
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps({"enable_dns":False}))
                logging.info(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        assert False
                else:
                    sleep(30)
                    assert True


    @pytest.mark.order(order=2)
    def test002_create_zone_test_com(self):
        logging.info("Creating zone test.com")
        data={"fqdn":"test.com","view":"default","grid_primary":[{"name": config.grid_fqdn,"stealth": False}]}
        zone_ref=ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data))
        logging.info(zone_ref)
        if bool(re.match("\"zone_auth*.",str(zone_ref))):
            logging.info("test.com created succesfully")
            assert True
        else:
            logging.info("test.com zone creation failed")
            assert False

    @pytest.mark.order(order=3)
    def test003_create_A_alias_record_in_zone_test_com(self):
        logging.info("Creating A alias record in zone test.com")
        data={"name":"a.test.com","target_name":"abc.test.com","target_type":"A","view":"default"}
        a_alias_ref=ib_NIOS.wapi_request('POST',object_type='record:alias',fields=json.dumps(data))
        logging.info(a_alias_ref)
        if bool(re.match("\"record:alias*.",str(a_alias_ref))):
            logging.info("A Alias record  created successfully")
            assert True
        else:
            logging.info("A alias record creation failed")
            assert False

    @pytest.mark.order(order=4)
    def test004_create_shared_record_group(self):
        logging.info("Create shared record group")
        data={"name":"shared1","zone_associations":["test.com"]}
        shared_record_group_ref=ib_NIOS.wapi_request('POST',object_type='sharedrecordgroup',fields=json.dumps(data))
        logging.info(shared_record_group_ref)
        if bool(re.match("\"sharedrecordgroup*.",str(shared_record_group_ref))):
            logging.info("Shared record group created successfully")
            assert True
        else:
            logging.info("Shared record group creation failed")
            assert False

    @pytest.mark.order(order=5)
    def test005_create_shared_A_record(self):
        logging.info("Create shared A record")
        data={"name":"a","ipv4addr":"10.0.0.1","shared_record_group":"shared1"}
        shared_a_record_ref=ib_NIOS.wapi_request('POST',object_type='sharedrecord:a',fields=json.dumps(data))
        logging.info(shared_a_record_ref)
        if bool(re.match("\"sharedrecord:a*.",str(shared_a_record_ref))):
            logging.info("Shared A record created, which shouldnt happen and is a bug")
            assert False
        else:
            logging.info("Shared A record creation failed")
            assert True

    @pytest.mark.order(order=6)
    def test006_Start_DNS_service(self):
        logging.info("Start DNS Service")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns')
        logging.info(get_ref)
        for ref in json.loads(get_ref):
            if config.grid_fqdn in ref['_ref']:
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps({"enable_dns":True}))
                logging.info(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        assert False
                else:
                    sleep(30)
                    assert True

    @pytest.mark.order(order=7)
    def test007_Perform_dig_query_on_zone_test_com_and_verify_no_SERVFAIL_message_is_seen(self):
        logging.info("Performing dig query on zone test.com")
        sleep(30)
        ip='@'+config.grid_vip
        dig_output=subprocess.check_output(['dig',ip,'test.com','in','a'])
        logging.info(dig_output)
        if 'SERVFAIL' in dig_output:
            logging.info("SERVFAIL encountered while doing dig on test.com")
            assert False
        else:
            logging.info("SERVFAIL not encountered while doing dig on test.com")
            assert True

    @pytest.mark.order(order=8)
    def test008_Test_cleanup(self):
        logging.info("Performing test cleanup")

        logging.info("Removing shared A record if present")
        get_ref = ib_NIOS.wapi_request('GET', object_type='sharedrecord:a')
        json_get_ref=json.loads(get_ref)
        if len(json_get_ref)==0:
            logging.info("Shared A record is not present, hence skipping")
        else:
            for ref in json_get_ref:
                if ref["name"]=="a":
                    shared_a_record_ref=ref['_ref']
                    del_shared_A_record=ib_NIOS.wapi_request('DELETE',ref=shared_a_record_ref)
                    logging.info(del_shared_A_record)
                    if bool(re.match("\"sharedrecord:a*.",str(del_shared_A_record))):
                        logging.info("Shared A record deleted")
                        assert True
                    else:
                        logging.info("Shared A record deletion failed")
                        assert False


        logging.info("Remove zone test.com")
        get_ref=ib_NIOS.wapi_request('GET',object_type='zone_auth')
        json_get_ref=json.loads(get_ref)
        for ref in json_get_ref:
            if ref["fqdn"]=="test.com":
                zone_ref=ref['_ref']
                del_zone=ib_NIOS.wapi_request('DELETE',ref=zone_ref)
                if bool(re.match("\"zone_auth*.",str(del_zone))):
                    logging.info("test.com deleted succesfully")
                    assert True
                else:
                    logging.info("test.com zone deletion failed")
                    assert False

        
        logging.info("Removing shared record group")
        get_ref = ib_NIOS.wapi_request('GET', object_type='sharedrecordgroup')
        json_get_ref=json.loads(get_ref)
        for ref in json_get_ref:
            if ref["name"]=="shared1":
                shared_record_group_ref=ref['_ref']
                del_shared_record_group=ib_NIOS.wapi_request('DELETE',ref=shared_record_group_ref)
                if bool(re.match("\"sharedrecordgroup*.",str(del_shared_record_group))):
                    logging.info("Shared record group deleted successfully")
                    assert True
                else:
                    logging.info("Shared record group deletion failed")
                    assert False


        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(5)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(5)





















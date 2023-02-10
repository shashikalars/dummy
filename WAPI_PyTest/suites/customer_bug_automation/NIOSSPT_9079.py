__author__ = "Aditya G"
__email__  = "adityag@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master                                                                      #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415)                                      #
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


logging.basicConfig(filename='niosspt9079.log', filemode='w', level=logging.DEBUG)


class NIOSSPT9079(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test001_create_zone1(self):
        logging.info("Creating zone test1.com")
        data={"fqdn":"test1.com","view":"default","grid_primary":[{"name": config.grid_fqdn,"stealth": False}]}
        self.zone1_ref=ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data))
        logging.info(self.zone1_ref)
        if bool(re.match("\"zone_auth*.",str(self.zone1_ref))):
            logging.info("test1.com created succesfully")
            logging.info("Restart services")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            sleep(5)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            sleep(5)
        else:
            raise Exception("test1.com creation unsuccessful")
    
    @pytest.mark.run(order=2)
    def test002_create_zone2(self):
        logging.info("Creating zone test2.com")
        data={"fqdn":"test2.com","view":"default","grid_primary":[{"name": config.grid_fqdn,"stealth": False}]}
        self.zone2_ref=ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data))
        logging.info(self.zone2_ref)
        if bool(re.match("\"zone_auth*.",str(self.zone2_ref))):
            logging.info("test2.com created succesfully")
            logging.info("Restart services")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            sleep(5)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            sleep(5)
        else:
            raise Exception("test2.com creation unsuccessful")

    @pytest.mark.run(order=3)
    def test003_create_srg(self):
        logging.info("Creating shared resource group:group1")
        data={"name":"group1","zone_associations":["test1.com","test2.com"]}
        self.srg_ref=ib_NIOS.wapi_request('POST',object_type='sharedrecordgroup',fields=json.dumps(data))
        logging.info(self.srg_ref)
        if bool(re.match("\"sharedrecordgroup*.",str(self.srg_ref))):
            logging.info("SRG creation succesfull")
            logging.info("Restart services")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            sleep(5)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            sleep(5)
        else:
            raise Exception("SRG creation unsuccessful")

    @pytest.mark.run(order=4)
    def test004_create_nsg(self):
        logging.info("Creating name server group:group1")
        data={"name": "group1","grid_primary":[{"name": config.grid_fqdn,"stealth": False}]}
        self.nsg_ref=ib_NIOS.wapi_request('POST',object_type='nsgroup',fields=json.dumps(data))
        logging.info(self.nsg_ref)
        if bool(re.match("\"nsgroup*.",str(self.nsg_ref))):
            logging.info("NSG creation successful")
            logging.info("Restart services")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            sleep(5)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            sleep(5)
        else:
            raise Exception("NSG creation unsuccessful")

    @pytest.mark.run(order=5)
    def test005_create_A_record(self):
        logging.info("Sending WAPI request to create A record in srg")
        data={"ipv4addr":"2.2.2.2","name":"abc","shared_record_group":"group1"}
        a_record_ref=ib_NIOS.wapi_request('POST',object_type='sharedrecord:a',fields=json.dumps(data))
        logging.info(a_record_ref)
        if bool(re.match("\"sharedrecord:a*.",str(a_record_ref))):
            logging.info("A Record Creation succesfull")
        else:
            raise Exception("A Record creation unsuccessful")

    @pytest.mark.run(order=6)
    def test006_create_AAAA_record(self):
        logging.info("Sending WAPI request to create AAAA record in srg")
        data = {"ipv6addr": "2400:cb00:2049:1::a29f:1804","name": "ipv6","shared_record_group": "group1"}
        aaaa_record_ref = ib_NIOS.wapi_request('POST',object_type='sharedrecord:aaaa',fields=json.dumps(data))
        logging.info(aaaa_record_ref)
        if bool(re.match("\"sharedrecord:aaaa*.",str(aaaa_record_ref))):
            logging.info("AAAA Record Creation succesfull")
        else:
            raise Exception("AAAA Record creation unsuccessful")

    @pytest.mark.run(order=7)
    def test007_create_CNAME_record(self):
        logging.info("Sending WAPI request to create CNAME record in srg")
        data = {"canonical": "ipv6.test1.com","name": "ipv66","shared_record_group": "group1"}
        cname_record_ref = ib_NIOS.wapi_request('POST',object_type='sharedrecord:cname',fields=json.dumps(data))
        logging.info(cname_record_ref)
        if bool(re.match("\"sharedrecord:cname*.",str(cname_record_ref))):
            logging.info("CNAME Record Creation succesfull")
            logging.info("Restart services")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            sleep(5)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            sleep(10)
        else:
            raise Exception("CNAME Record creation unsuccessful")

    @pytest.mark.run(order=8)
    def test008_dig_A_record_from_both_zones(self):
        logging.info("Querying A record from both the zones")
        logging.info("Starting query from test1.com")
        validation = '2.2.2.2'
        ip = '@'+config.grid_vip
        output=subprocess.check_output(['dig',ip,'abc.test1.com','in','a'])
        logging.info(output)
        if validation in output:
            logging.info("Query for abc.test1.com successfull")
            sleep(5)
        else:
            raise Exception("Query for abc.test1.com failed")
        output=subprocess.check_output(['dig',ip,'abc.test2.com','in','a'])
        logging.info(output)
        if validation in output:
            logging.info("Query for abc.test2.com successfull")
            sleep(5)
        else:
            raise Exception("Query for abc.test2.com failed")


    @pytest.mark.run(order=9)
    def test009_dig_AAAA_record_from_both_zones(self):
        logging.info("Querying AAAA record from both the zones")
        logging.info("Starting query from test1.com")
        validation = "2400:cb00:2049:1::a29f:1804"
        ip = '@'+config.grid_vip
        output=subprocess.check_output(['dig',ip,'ipv6.test1.com','in','aaaa'])
        logging.info(output)
        if validation in output:
            logging.info("Query for ipv6.test1.com successfull")
            sleep(5)
        else:
            raise Exception("Query for ipv6.test1.com failed")
        output=subprocess.check_output(['dig',ip,'ipv6.test2.com','in','aaaa'])
        logging.info(output)
        if validation in output:
            logging.info("Query for ipv6.test2.com successfull")
            sleep(5)
        else:
            raise Exception("Query for ipv6.test2.com failed")

    @pytest.mark.run(order=10)
    def test010_dig_CNAME_record_from_both_zones(self):
        logging.info("Querying CNAME record from both the zones")
        logging.info("Starting query from test1.com")
        validation = "2400:cb00:2049:1::a29f:1804"
        ip = '@'+config.grid_vip
        output=subprocess.check_output(['dig',ip,'ipv66.test1.com','in','aaaa'])
        logging.info(output)
        if validation in output:
            logging.info("Query for ipv66.test1.com successfull")
            sleep(5)
        else:
            raise Exception("Query for ipv66.test1.com failed")
        output=subprocess.check_output(['dig',ip,'ipv66.test2.com','in','aaaa'])
        logging.info(output)
        if validation in output:
            logging.info("Query for ipv66.test2.com successfull")
            sleep(5)
        else:
            raise Exception("Query for ipv66.test2.com failed")


    @pytest.mark.run(order=11)
    def test011_test_cleanup(self):
        logging.info("Starting cleanup")
        get_ref = ib_NIOS.wapi_request('GET',object_type='zone_auth')
        self.zone1_ref = json.loads(get_ref)[0]['_ref']
        del_zone1_ref=ib_NIOS.wapi_request('DELETE',ref=self.zone1_ref.strip('\"'))
        if bool(re.match("\"zone_auth*.",str(del_zone1_ref))):
            logging.info("test1.com deleted succesfully")
        else:
            raise Exception("test1.com deletion unsuccessful")

        res = ib_NIOS.wapi_request('GET',object_type='zone_auth?fqdn=test2.com')
        res = json.loads(res)
        zone_ref=res[0]['_ref']
        response=ib_NIOS.wapi_request('DELETE', object_type=zone_ref)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(65)


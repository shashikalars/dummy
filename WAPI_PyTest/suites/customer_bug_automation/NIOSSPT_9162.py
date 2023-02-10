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
import ib_utils.common_utilities as ib_TOKEN
from time import sleep
import commands
import json, ast
import time
import getpass
import sys
import pexpect


logging.basicConfig(filename='niosspt9162.log', filemode='w', level=logging.DEBUG)


class NIOSSPT_9162(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_001_change_hostname_of_grid_master(self):
        logging.info("Fetching grid master reference")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member")
        master_ref=''
        for ref in json.loads(get_ref):
            if ref['host_name'] == config.grid_fqdn:
                master_ref = ref['_ref']
                logging.info(master_ref)
                break
        if master_ref == '':
            logging.info("Reference of master grid not found")
            assert False
        logging.info("Changing the hostname of master grid to infoblox.localdomain")
        data = {"host_name": "infoblox.localdomain"}
        response = ib_NIOS.wapi_request('PUT', ref=master_ref, fields=json.dumps(data))
        if bool(re.match("\"member*.",str(response))):
            logging.info("Hostname of master changed successfully")
            sleep(180)
            assert True
        else:
            logging.info("Changing hostname of the master failed")
            assert False

    @pytest.mark.run(order=2)
    def test_002_Check_if_forwarder_ip_is_present_and_remove_if_present(self):
        logging.info("Checking if forwarder ip is present and removing it if present")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns?_return_fields=forwarders,host_name")
        print(get_ref)
        for ref in json.loads(get_ref):
            if ref['host_name'] == 'infoblox.localdomain':
                if len(ref['forwarders']) != 0:
                        data = {"forwarders": []}
                        response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                        if bool(re.match("\"member:dns*.",str(response))):
                            logging.info("Forwarders removed successfully")
                            logging.info("Restart services")
                            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                            ref = json.loads(grid)[0]['_ref']
                            publish={"member_order":"SIMULTANEOUSLY"}
                            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                            sleep(5)
                            assert True
                        else:
                            logging.info("Forwarders removal failed")
                            assert False
                else:
                    logging.info("No forwarder ip present, proceeding with further cases")
                    assert True
                            


    @pytest.mark.run(order=3)
    def test_003_import_modified_csv_with_updated_allow_forwarder(self):
        logging.info("Uploading csv file containing member dns properties and also have updated the allow_forwarder with an forwarder IP address")
        logging.info("Starting csv import")
        dir_name = os.getcwd()
        base_filename = "niosspt_9162.csv"
        token =ib_TOKEN.generate_token_from_file(dir_name, base_filename)
        data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"OVERRIDE","operation":"UPDATE"}
        response1 = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_import")
        print(response1)
        response = json.loads(response1)
        logging.info("logging response")
        logging.info(response)
        sleep(10)
        data={"action":"START","file_name":"niosspt_9162.csv","on_error":"CONTINUE","operation":"CREATE","separator":"COMMA"}
        get_ref=ib_NIOS.wapi_request('GET', object_type="csvimporttask")
        logging.info("get_ref")
        logging.info(get_ref)
        get_ref=json.loads(get_ref)
        for ref in get_ref:
            if response["csv_import_task"]["import_id"]==ref["import_id"]:
                if ref["lines_failed"]==0:
                    logging.info("CSV import successful")
                else:
                    raise Exception("CSV import unsuccessful")
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(5)

    @pytest.mark.run(order=4)
    def test_004_test_cleanup(self):
        logging.info("Cleaning forwarder ip")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns?_return_fields=forwarders,host_name")
        print(get_ref)
        for ref in json.loads(get_ref):
            if ref['host_name'] == 'infoblox.localdomain':
                data = {"forwarders": []}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                if bool(re.match("\"member:dns*.",str(response))):
                        logging.info("Forwarders removed successfully")
                        logging.info("Restart services")
                        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                        ref = json.loads(grid)[0]['_ref']
                        publish={"member_order":"SIMULTANEOUSLY"}
                        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                        sleep(5)
                        assert True
                else:
                        logging.info("Forwarders removal failed")
                        assert False

        logging.info("Fetching grid master reference")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member")
        master_ref=''
        for ref in json.loads(get_ref):
            if ref['host_name'] == "infoblox.localdomain":
                master_ref = ref['_ref']
                logging.info(master_ref)
                break
        if master_ref == '':
            logging.info("Reference of master grid not found")
            assert False
        logging.info("Changing the hostname of master grid to "+config.grid_fqdn)
        data = {"host_name": config.grid_fqdn}
        response = ib_NIOS.wapi_request('PUT', ref=master_ref, fields=json.dumps(data))
        if bool(re.match("\"member*.",str(response))):
            logging.info("Hostname of master changed successfully")
            sleep(180)
            assert True
        else:
            logging.info("Changing hostname of the master failed")
            assert False





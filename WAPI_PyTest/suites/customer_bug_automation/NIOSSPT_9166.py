#!/usr/bin/env python
__author__ = "Chetan Kumar PG"
__email__  = "cpg@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Stand alone Grid Master                                               #
#  2. Licenses : DNS, DHCP, Grid                                            #
#  3. Enable DNS services                                                   #
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
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="niosspt_9166.log" ,level=logging.DEBUG,filemode='w')

def display_msg(x=""):
    """ 
    Additional function.
    """
    logging.info(x)
    print(x)

class NIOSSPT_9166(unittest.TestCase):
    
    @pytest.mark.run(order=1)
    def test_000_setup(self):
        """
        setup method: Used for configuring pre-required configs.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case setup Started            |")
        display_msg("------------------------------------------------")
        pass
    
    @pytest.mark.run(order=2)
    def test_001_add_zone(self):
        """
        Add an Authorative Zone niosspt_9166.com.
        Add Grid master as Grid primary.
        Verify that the Zone is created with no errors.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 1 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Create a zone niosspt_9166.com")
        data = {"fqdn": "niosspt_9166.com", 
                "view":"default", 
                "grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                assert False
        display_msg("-----------Test Case 1 Execution Completed------------")
    
    @pytest.mark.run(order=3)
    def test_002_add_subzone(self):
        """
        Add an Authorative SubZone sub.niosspt_9166.com.
        Add Grid master as Grid primary.
        Verify that the SubZone is created with no errors.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 2 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Add subzone sub.niosspt_9166.com")
        data = {"fqdn": "sub.niosspt_9166.com", 
                "view":"default",
                "grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                assert False
        display_msg("-----------Test Case 2 Execution Completed------------")
    
    @pytest.mark.run(order=4)
    def test_003_modify_subzone_to_sign(self):
        """
        DNSSEC Sign the SubZone sub.niosspt_9166.com.
        Verify that the SubZone is Signed with no errors.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 3 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Modify the zone sub.niosspt_9166.com to sign the zone")
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", params="?fqdn=sub.niosspt_9166.com")
        display_msg(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"operation":"SIGN"}
        response = ib_NIOS.wapi_request('POST', ref=ref1, fields=json.dumps(data), params="?_function=dnssec_operation")
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                assert False
        display_msg("-----------Test Case 3 Execution Completed------------")
    
    
    @pytest.mark.run(order=5)
    def test_004_export_ds_records_from_subzone(self):
        """
        Export DS records from SubZone sub.niosspt_9166.com.
        Download the exported file to current working directory as ds_record.txt.
        Verify that the file is downloaded with no errors.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 4 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Export DS records created by signing the subzone sub.niosspt_9166.com")
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", params="?fqdn=sub.niosspt_9166.com")
        display_msg(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"operation":"EXPORT_DS"}
        response = ib_NIOS.wapi_request('POST', ref=ref1, fields=json.dumps(data), params="?_function=dnssec_export")
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                assert False
        
        ## Download DS record
        url = json.loads(response)['url']
        cmd = "curl -k -u admin:infoblox -H 'content-type: application/force-download' "+ str(url) + " -o 'ds_record.txt'"
        display_msg(cmd)
        if os.system(cmd):
            assert False
        display_msg("-----------Test Case 4 Execution Completed------------")
    
    @pytest.mark.run(order=6)
    def test_005_delete_subzone(self):
        """
        Delete the SubZone sub.niosspt_9166.com.
        Verify that the SubZone is deleted with no errors.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 5 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Delete the zone sub.niosspt_9166.com")
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", params="?fqdn=sub.niosspt_9166.com")
        display_msg(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        response = ib_NIOS.wapi_request('DELETE', ref=ref1)
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                assert False
        display_msg("-----------Test Case 5 Execution Completed------------")
    
    @pytest.mark.run(order=7)
    def test_006_add_subzone_again(self):
        """
        Add an Authorative SubZone sub.niosspt_9166.com.
        Add Grid master as Grid primary.
        Verify that the SubZone is created with no errors.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 6 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Add subzone sub.niosspt_9166.com again")
        data = {"fqdn": "sub.niosspt_9166.com", 
                "view":"default",
                "grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                assert False
        display_msg("-----------Test Case 6 Execution Completed------------")
    
    @pytest.mark.run(order=8)
    def test_007_import_ds_records_to_subzone(self):
        """
        Import DS Records from the downloaded file ds_record.txt.
        Verify that the DS records are imported with no errors.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 7 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Import DS records to the subzone sub.niosspt_9166.com")
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", params="?fqdn=niosspt_9166.com")
        display_msg(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        file = os.getcwd()+'//ds_record.txt'
        with open(file,'r') as f:
            ds_record = f.read()
        ds_record = ds_record.strip().strip('\n')
        display_msg(ds_record)
        data = {"operation":"IMPORT_DS", "buffer": ds_record}
        response = ib_NIOS.wapi_request('POST', ref=ref1, fields=json.dumps(data), params="?_function=dnssec_operation")
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                assert False
        display_msg("-----------Test Case 7 Execution Completed------------")
    
    @pytest.mark.run(order=9)
    def test_008_delete_imported_ds_records(self):
        """
        Delete the imported DS Records using WAPI.
        Verify that the imported DS Records are deleted with no errors.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 8 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Delete all the imported DS records from the zone sub.niosspt_9166.com")
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:ds", params="?name=sub.niosspt_9166.com")
        display_msg(get_ref)
        get_ref=json.loads(get_ref)
        for obj in get_ref:
            ref1 = obj['_ref']
            response = ib_NIOS.wapi_request('DELETE', ref=ref1)
            display_msg(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    assert False
        check_ref = ib_NIOS.wapi_request('GET', object_type="record:ds", params="?name=sub.niosspt_9166.com")
        if not check_ref=='[]':
            assert False
        display_msg("-----------Test Case 8 Execution Completed------------")
    
    @pytest.mark.run(order=-1)
    def test_cleanup(self):
        """
        cleanup method: Delete all the objects created from this script.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|          Test Case cleanup Started           |")
        display_msg("------------------------------------------------")
        display_msg("Delete the zone niosspt_9166.com")
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", params="?fqdn=niosspt_9166.com")
        display_msg(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        response = ib_NIOS.wapi_request('DELETE', ref=ref1)
        display_msg(response)
        os.system('rm -rf ds_record.txt')
        display_msg("-----------Test Case cleanup Completed------------")
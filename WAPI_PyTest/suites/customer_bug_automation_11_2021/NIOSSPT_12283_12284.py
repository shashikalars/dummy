#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Vindya V K"
__email__  = "vvk@infoblox.com"

#############################################################################
# Grid Set up required:                                                     #
#  1. Grid Master - 8.5.3 build                                             #
#  2. Licenses : DNS, DHCP, Grid, NIOS                                      #
#                                                                           #
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

################################################################################
# STEPS TO REPRODUCE:                                                          #
#                                                                              #
##  NIOSSPT-12284   ##
#   1. Create an authoratative zone - test.com                                 #
#   2. Create CNAME record - cname2.test.com                                   #
#   3. Create a csv file - cname1.csv with the field 'canonical_name' as empty #
#                        - add CNAME record cname1.test.com                    #
#   4. Import the newly created csv file - cname1.csv (update_method=MERGE)    #
#   5. Create a csv file - cname2.csv with the field 'canonical_name' as empty #
#                        - add CNAME record cname2.test.com                    #
#   6. Import the newly created csv file - cname2.csv (update_method=OVERRIDE) #
#   7. Check the log for import error under '/storage/infoblox.var/csv_import' #
#                                                                              #
##  NIOSSPT-12283   ##
#   8. Create a CNAME record - record.test.com                                 #
#   9. Perform Global CSV Export for CNAME records                             #
#  10. Check the headers and verify the required fields as per the admin guide #
################################################################################


class NIOSSPT_12284(unittest.TestCase):

# Create authoratative zone - test.com
    @pytest.mark.run(order=1)
    def test_001_Create_auth_zone(self):
        print("\n========================================================\n")
        print("Creating an Authoratative zone - test.com")
        print("\n========================================================\n")

        data = {"fqdn":"test.com","view":"default"}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if response[0]==400 or response[0]==401 or response[0]==404:
            print("FAILURE: Failed to create authoratative zone test.com!")
            assert False
        else:
            print("SUCCESS: Authorataive zone test.com has been successfully created!")
            assert True

        print("\n***************. Test Case 1 Execution Completed .***************\n")


# Validating the zone
    @pytest.mark.run(order=2)
    def test_002_validate_auth_zone(self):
        print("\n========================================================\n")
        print("Validating Authoratative zone")
        print("\n========================================================\n")

        response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=test.com", grid_vip=config.grid_vip)
        response=json.loads(response)

        for ref in response:
            if 'test.com' in ref['_ref']:
                print(ref["_ref"])
                print("SUCCESS: Authoratative Zone 'test.com' was created!")
                assert True
                break
            else:
                continue
                print("FAILURE: Authoratative Zone 'test.com' was NOT created!")
                assert False
        print("\n***************. Test Case 2 Execution Completed .***************\n")


# Create a CNAME record - cname2.test.com
    @pytest.mark.run(order=3)
    def test_003_Create_CNAME_record(self):
        print("\n========================================================\n")
        print("Creating a CNAME record - cname2.test.com")
        print("\n========================================================\n")

        data = {"name":"cname2.test.com", "canonical":"cnamerecord"}
        response = ib_NIOS.wapi_request('POST', object_type="record:cname", fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if response[0]==400 or response[0]==401 or response[0]==404:
            print("FAILURE: Failed to create cname record!")
            assert False
        else:
            print("SUCCESS: cname record has been successfully created!")
            assert True

        print("\n***************. Test Case 3 Execution Completed .***************\n")


# Validating CNAME record
    @pytest.mark.run(order=4)
    def test_004_validate_cname_record(self):
        print("\n========================================================\n")
        print("Validating CNAME record")
        print("\n========================================================\n")

        response = ib_NIOS.wapi_request('GET', object_type="record:cname?name=cname2.test.com", grid_vip=config.grid_vip)
        response=json.loads(response)

        for ref in response:
            if 'cname2.test.com' in ref['_ref']:
                print(ref["_ref"])
                print("SUCCESS: cname record 'cname2.test.com' was created!")
                assert True
                break
            else:
                continue
                print("FAILURE: cname record 'cname2.test.com' was NOT created!")
                assert False
        print("\n***************. Test Case 4 Execution Completed .***************\n")


# Create a csv file without marking canonical field as required
    @pytest.mark.run(order=5)
    def test_005_Create_csv_file(self):
        print("\n========================================================\n")
        print("Creating a csv file - cname1.csv")
        print("\n========================================================\n")

        create= open('cname1.csv','w')
        create.write("header-cnamerecord,fqdn*,_new_fqdn,canonical_name,comment,creator,ddns_principal,ddns_protected,disabled,ttl,view\ncnamerecord,cname1.test.com,,,,STATIC,,False,False,,default\n")
        print("cname1.csv is created!")

        print("\n***************. Test Case 5 Execution Completed .***************\n")


# import csv file
# This import is expexted to fail

    @pytest.mark.run(order=6)
    def test_006_import_csv_file(self):
        print("\n========================================================\n")
        print("import CSV file from the system using 'MERGE'")
        print("\n========================================================\n")

        # dir_name = "/mnt/home/vvk"
        dir_name=os.getcwd()
        base_filename = "cname1.csv"
        token = common_util.generate_token_from_file(dir_name,base_filename)
        data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"MERGE"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_import")
        response=json.loads(response)
        sleep(30)

        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==402:
                print("Failure: Import cname1.csv file")
                assert False
        else:
            print("Success: Import cname1.csv file")
            assert True


        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)

        print("\n***************. Test Case 6 Execution Completed .***************\n")


# Create a csv file without marking canonical field as required
    @pytest.mark.run(order=7)
    def test_007_Create_csv_file(self):
        print("\n========================================================\n")
        print("Creating a csv file - cname2.csv")
        print("\n========================================================\n")

        create= open('cname2.csv','w')
        create.write("header-cnamerecord,fqdn*,_new_fqdn,canonical_name,comment,creator,ddns_principal,ddns_protected,disabled,ttl,view\ncnamerecord,cname2.test.com,,,,STATIC,,False,False,,default\n")
        print("cname2.csv is created!")

        print("\n***************. Test Case 7 Execution Completed .***************\n")


# import csv file
    @pytest.mark.run(order=8)
    def test_008_import_csv_file(self):
        print("\n========================================================\n")
        print("import CSV file from the system using 'OVERRIDE'")
        print("\n========================================================\n")

        # dir_name = "/mnt/home/vvk"
        dir_name=os.getcwd()
        base_filename = "cname2.csv"
        token = common_util.generate_token_from_file(dir_name,base_filename)
        data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"OVERRIDE"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_import")
        response=json.loads(response)
        sleep(30)

        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==402:
                print("Failure: Import cname2.csv file")
                assert False
        else:
            print("Success: Import cname2.csv file")
            assert True


        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)

        print("\n***************. Test Case 8 Execution Completed .***************\n")



# Check for error

### This case will fail now as the bug is not yet fixed ###
    @pytest.mark.run(order=9)
    def test_009_check_for_errors(self):
        print("\n========================================================\n")
        print("Checking for errors under /storage/infoblox.var/csv_import")
        print("\n========================================================\n")

        current_dir=os.getcwd()
        os.system("scp -pr -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@"+config.grid_vip+":/storage/infoblox.var/csv_import"+" "+current_dir)
        cmd="grep -Rc 'Insertion aborted due to The CNAME property \"\"dns_canonical_name\"\" is read-only and cannot be changed' csv_import/csv-error*"
        data = os.system(cmd)
        print(data)

        message="Insertion aborted due to The CNAME property ""dns_canonical_name"" is read-only and cannot be changed."

        if data != 0:
            print("SUCCESS: csv import was successful")
            assert True
        else:
            print("FAILURE: csv import was unsuccessful due to '"+message+"'")
            assert False

        os.system("rm -rf "+current_dir+"/csv_import")
        print("\n***************. Test Case 9 Execution Completed .***************\n")


# Create a CNAME record - record.test.com
    @pytest.mark.run(order=10)
    def test_010_Create_CNAME_record(self):
        print("\n========================================================\n")
        print("Creating a CNAME record - record.test.com")
        print("\n========================================================\n")

        data = {"name":"record.test.com", "canonical":"cnamerecord"}
        response = ib_NIOS.wapi_request('POST', object_type="record:cname", fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if response[0]==400 or response[0]==401 or response[0]==404:
            print("FAILURE: Failed to create cname record!")
            assert False
        else:
            print("SUCCESS: cname record has been successfully created!")
            assert True

        print("\n***************. Test Case 10 Execution Completed .***************\n")



# Validating CNAME record
    @pytest.mark.run(order=11)
    def test_011_validate_cname_record(self):
        print("\n========================================================\n")
        print("Validating CNAME record")
        print("\n========================================================\n")

        response = ib_NIOS.wapi_request('GET', object_type="record:cname?name=record.test.com", grid_vip=config.grid_vip)
        response=json.loads(response)

        for ref in response:
            if 'record.test.com' in ref['_ref']:
                print(ref["_ref"])
                print("SUCCESS: cname record 'record.test.com' was created!")
                assert True
                break
            else:
                continue
                print("FAILURE: cname record 'record.test.com' was NOT created!")
                assert False
        print("\n***************. Test Case 11 Execution Completed .***************\n")



# Export csv file
    @pytest.mark.run(order=12)
    def test_012_Export_csv_file(self):
        print("\n========================================================\n")
        print("Export CSV file from the system")
        print("\n========================================================\n")

        print("Create the fileop function to download csv_export object with cname record")
        data = {"_object":"record:cname"}
        create_file = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=csv_export")
        print(create_file)
        result = json.loads(create_file)
        token = result['token']
        url = result['url']
        print("Token : "+token)
        print("URL : "+url)
        print("Create the fileop function to download the csv file to the specified url")
        output=os.system('curl -k -u admin:infoblox -H "Content-type:application/force-download" -O %s'%(url))
        print(output)

        if output==0:
            print("CSV export successful")
            assert True
        else:
            print("csv export failed")
            assert False

        print("\n***************. Test Case 12 Execution Completed .***************\n")



# Checking is the headers have *

### This case will fail now as the bug is not yet fixed ###

    @pytest.mark.run(order=13)
    def test_013_verifying_the_required_fields(self):
        print("\n========================================================\n")
        print("verifying if the required fields have * or not...")
        print("\n========================================================\n")

        with open('Cnamerecords.csv') as file:
            contents = file.read()
# According to the admin guide, 3 fileds must be marked as mantatory fields with a * - header-cnamerecord, fqdn and canonical_name
            search_word1 = "header-cnamerecord*"
            search_word2 = "fqdn*"
            search_word3 = "canonical_name*"
            if search_word1 and search_word2 and search_word3 in contents:
                print ("All mandatory fields are marked with a '*'")
                assert True
            else:
                print ("Some Mandatory fields are not marked with a '*'")
                assert False

        print("\n***************. Test Case 13 Execution Completed .***************\n")


### cleanup function

    @pytest.mark.run(order=14)
    def test_014_cleanup_objects(self):
        print("\n============================================\n")
        print("CLEANUP: Reverting back to original setup...")
        print("\n============================================\n")


        get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth")
        for ref in json.loads(get_ref):
            if 'test.com' in ref["_ref"]:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])

        print("\n***************. Test Case 14 Execution Completed .***************\n")



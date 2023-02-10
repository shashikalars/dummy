#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Vindya V K"
__email__  = "vvk@infoblox.com"

################################################################################
# Configuration - Grid master + Member
# Here we are automating all the Alias records present in Forward mapping zone #
################################################################################

import sys
import os
import json
import config
import pytest
import subprocess
import unittest
import logging
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util


logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="ib_alias.log" ,level=logging.DEBUG,filemode='w')

def display_message(x=""):
    # Additional function used to log and print with a single line
    logging.info(x)
    print(x)


def perform_dig_query(ip,record,record_type,lookFor1,lookFor2):
    query ="dig @" + ip +" "+ record +" in "+ record_type
    display_message(query)
    query = subprocess.check_output(query,shell=True)
    display_message(query)

    display_message("\n--------------------------------------------------------\n")
    display_message("Validating dig response...")
    display_message("\n--------------------------------------------------------\n")

    if lookFor1 in query and lookFor2 in query:
        display_message(lookFor1 + " response found!")
        assert True

    else:
        display_message(lookFor1 +" response NOT found!")
        assert False


def create_alias_record(name,target_name,target_type):

    data = {"name": name, "target_name": target_name, "target_type": target_type}
    response = ib_NIOS.wapi_request('POST', object_type="record:alias", fields=json.dumps(data), grid_vip=config.grid_vip)
    display_message(response)
    if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
        display_message("FAILURE: Create "+target_type+" alias record.")
        assert False
    else:
        display_message("\n--------------------------------------------------------\n")
        display_message("Validating alias record "+name)
        display_message("\n--------------------------------------------------------\n")

        response = ib_NIOS.wapi_request('GET', object_type="record:alias?name="+name, grid_vip=config.grid_vip)
        response=json.loads(response)[0]
        display_message(response)

        if name in response['_ref']:
            display_message(response["_ref"])
            display_message("SUCCESS: Alias record "+name+" was created!")
            assert True
        else:
            display_message("FAILURE: Alias record "+name+" was NOT created!")
            assert False

def create_record_in_sub_zone(data,name,type):

    response = ib_NIOS.wapi_request('POST', object_type="record:"+type, fields=json.dumps(data), grid_vip=config.grid_vip)
    display_message(response)
    if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
        display_message("FAILURE: Create "+type+" record.")
        assert False
    else:
        display_message("\n--------------------------------------------------------\n")
        display_message("Validating "+type+" record - "+name)
        display_message("\n--------------------------------------------------------\n")

        response = ib_NIOS.wapi_request('GET', object_type="record:"+type+"?name="+name, grid_vip=config.grid_vip)
        response=json.loads(response)[0]
        display_message(response)

        if name in response['_ref']:
            display_message(response["_ref"])
            display_message("SUCCESS: Alias record "+name+" was created!")
            assert True
        else:
            display_message("FAILURE: Alias record "+name+" was NOT created!")
            assert False

## CNAME record fucntions

def create_cname_record(name,canonical):
    data = {"name": name, "canonical": canonical}
    response = ib_NIOS.wapi_request('POST', object_type="record:cname", fields=json.dumps(data), grid_vip=config.grid_vip)
    display_message(response)
    if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
        display_message("FAILURE: Create "+name+" cname record.")
        assert False
    else:
        display_message("\n--------------------------------------------------------\n")
        display_message("Validating CNAME record "+name)
        display_message("\n--------------------------------------------------------\n")

        response = ib_NIOS.wapi_request('GET', object_type="record:cname?name="+name, grid_vip=config.grid_vip)
        response=json.loads(response)[0]
        display_message(response)

        if name in response['_ref']:
            display_message(response["_ref"])
            display_message("SUCCESS: CNAME record "+name+" was created!")
            assert True
        else:
            display_message("FAILURE: CNAME record "+name+" was NOT created!")
            assert False

def create_record_in_zone(data,name,type):

    response = ib_NIOS.wapi_request('POST', object_type="record:"+type, fields=json.dumps(data), grid_vip=config.grid_vip)
    display_message(response)
    if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
        display_message("FAILURE: Create "+type+" record.")
        assert False
    else:
        display_message("\n--------------------------------------------------------\n")
        display_message("Validating "+type+" record - "+name)
        display_message("\n--------------------------------------------------------\n")

        response = ib_NIOS.wapi_request('GET', object_type="record:"+type+"?name="+name, grid_vip=config.grid_vip)
        response=json.loads(response)[0]
        display_message(response)

        if name in response['_ref']:
            display_message(response["_ref"])
            display_message("SUCCESS: "+type+" record "+name+" was created!")
            assert True
        else:
            display_message("FAILURE: "+type+" record "+name+" was NOT created!")
            assert False


def perform_dig_query_cname(ip,record,record_type,lookFor1,lookFor2,lookFor3):
    sleep(5)
    query ="dig @" + ip +" "+ record +" in "+ record_type
    display_message(query)
    query = subprocess.check_output(query,shell=True)
    display_message(query)

    display_message("\n--------------------------------------------------------\n")
    display_message("Validating dig response...")
    display_message("\n--------------------------------------------------------\n")

    if lookFor3=='':
        if lookFor1 in query and lookFor2 in query:
            display_message(lookFor1 + " response found!")
            assert True
        else:
            display_message(lookFor1 +" response NOT found!")
            assert False
    else:
        if lookFor1 in query and lookFor2 in query and lookFor3 not in query:
            display_message(lookFor1 + " response found!")
            display_message("AND cname not found in response!")
            assert True
        else:
            display_message(lookFor1 +" response NOT found!")
            display_message("OR cname found in response!")
            assert False


def create_dname_record(name,target):
    data = {"name": name, "target": target}
    response = ib_NIOS.wapi_request('POST', object_type="record:dname", fields=json.dumps(data), grid_vip=config.grid_vip)
    display_message(response)
    if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
        display_message("FAILURE: Create "+name+" dname record.")
        assert False
    else:
        display_message("\n--------------------------------------------------------\n")
        display_message("Validating DNAME record "+name)
        display_message("\n--------------------------------------------------------\n")

        response = ib_NIOS.wapi_request('GET', object_type="record:dname?name="+name, grid_vip=config.grid_vip)
        response=json.loads(response)[0]
        display_message(response)

        if name in response['_ref']:
            display_message(response["_ref"])
            display_message("SUCCESS: DNAME record "+name+" was created!")
            assert True
        else:
            display_message("FAILURE: DNAME record "+name+" was NOT created!")
            assert False


class IB_Alias_Automation(unittest.TestCase):

# Create authoratative zone - infoblox.com
# Assign grid master as grid primary
# Validate if infoblox.com has been created.
    @pytest.mark.run(order=1)
    def test_001_Create_auth_zone(self):

        display_message("\n========================================================\n")
        display_message("Creating an Authoratative zone - infoblox.com")
        display_message("\n========================================================\n")

        data = {"fqdn":"infoblox.com","view":"default","grid_primary":[{"name":config.grid_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_message(response)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_message("FAILURE: Create authoratative zone.")
            assert False
        else:
            display_message()
            display_message("\n--------------------------------------------------------\n")
            display_message("Validating Authoratative zone - infoblox.com")
            display_message("\n--------------------------------------------------------\n")

            response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=infoblox.com", grid_vip=config.grid_vip)
            response=json.loads(response)[0]
            display_message(response)

            if 'infoblox.com' in response['_ref']:
                display_message(response["_ref"])
                display_message("SUCCESS: Authoratative Zone 'infoblox.com' was created!")
                assert True
            else:
                display_message("FAILURE: Authoratative Zone 'infoblox.com' was NOT created!")
                assert False

        display_message("\n***************. Test Case 1 Execution Completed .***************\n") # requires restart


# Create authoratative subzone zone - sub.infoblox.com
# Assign grid master as grid primary
# Validate if sub.infoblox.com has been created.
    @pytest.mark.run(order=2)
    def test_002_Create_auth_sub_zone(self):

        display_message("\n========================================================\n")
        display_message("Creating an Authoratative sub zone - sub.infoblox.com")
        display_message("\n========================================================\n")

        data = {"fqdn":"sub.infoblox.com","view":"default","grid_primary":[{"name":config.grid_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_message(response)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_message("FAILURE: Create authoratative sub zone.")
            assert False
        else:
            display_message()
            display_message("\n--------------------------------------------------------\n")
            display_message("Validating Authoratative sub zone - sub.infoblox.com")
            display_message("\n--------------------------------------------------------\n")

            response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=sub.infoblox.com", grid_vip=config.grid_vip)
            response=json.loads(response)[0]
            display_message(response)

            if 'sub.infoblox.com' in response['_ref']:
                display_message(response["_ref"])
                display_message("SUCCESS: Authoratative Sub Zone 'sub.infoblox.com' was created!")
                assert True
            else:
                display_message("FAILURE: Authoratative Sub Zone 'sub.infoblox.com' was NOT created!")
                assert False

        display_message("\n***************. Test Case 2 Execution Completed .***************\n") # requires restart


# Restart services
    @pytest.mark.run(order=3)
    def test_003_Restart_services(self):

        display_message("\n========================================================\n")
        display_message("Restarting Services")
        display_message("\n========================================================\n")

        grid = ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(60)

        display_message("\n***************. Test Case 3 Execution Completed .***************\n")


############################################################################################################################################
# Performing dig queries and validating for NXDOMAIN and SOA response
############################################################################################################################################


# Perform dig query for alias with type A
# Validate for NXDOMAIN response and SOA
    @pytest.mark.run(order=4)
    def test_004_dig_alias_with_type_A(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type A")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"a_alias.infoblox.com","a","NXDOMAIN","SOA")

        display_message("\n***************. Test Case 4 Execution Completed .***************\n")



# Perform dig query for alias with type AAAA
# Validate for NXDOMAIN response and SOA
    @pytest.mark.run(order=5)
    def test_005_dig_alias_with_type_AAAA(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type AAAA")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"aaaa_alias.infoblox.com","aaaa","NXDOMAIN","SOA")

        display_message("\n***************. Test Case 5 Execution Completed .***************\n")


# Perform dig query for alias with type MX
# Validate for NXDOMAIN response and SOA
    @pytest.mark.run(order=6)
    def test_006_dig_alias_with_type_MX(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type MX")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"mx_alias.infoblox.com","mx","NXDOMAIN","SOA")

        display_message("\n***************. Test Case 6 Execution Completed .***************\n")


# Perform dig query for alias with type NAPTR
# Validate for NXDOMAIN response and SOA
    @pytest.mark.run(order=7)
    def test_007_dig_alias_with_type_NAPTR(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type NAPTR")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"naptr_alias.infoblox.com","naptr","NXDOMAIN","SOA")

        display_message("\n***************. Test Case 7 Execution Completed .***************\n")


# Perform dig query for alias with type PTR
# Validate for NXDOMAIN response and SOA
    @pytest.mark.run(order=8)
    def test_008_dig_alias_with_type_PTR(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type PTR")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"ptr_alias.infoblox.com","ptr","NXDOMAIN","SOA")

        display_message("\n***************. Test Case 8 Execution Completed .***************\n")


# Perform dig query for alias with type SPF
# Validate for NXDOMAIN response and SOA
    @pytest.mark.run(order=9)
    def test_009_dig_alias_with_type_SPF(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type SPF")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"spf_alias.infoblox.com","spf","NXDOMAIN","SOA")

        display_message("\n***************. Test Case 9 Execution Completed .***************\n")


# Perform dig query for alias with type SRV
# Validate for NXDOMAIN response and SOA
    @pytest.mark.run(order=10)
    def test_010_dig_alias_with_type_SRV(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type SRV")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"srv_alias.infoblox.com","srv","NXDOMAIN","SOA")

        display_message("\n***************. Test Case 10 Execution Completed .***************\n")


# Perform dig query for alias with type TXT
# Validate for NXDOMAIN response and SOA
    @pytest.mark.run(order=11)
    def test_011_dig_alias_with_type_TXT(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type TXT")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"txt_alias.infoblox.com","txt","NXDOMAIN","SOA")

        display_message("\n***************. Test Case 11 Execution Completed .***************\n")


# Perform dig query for alias with type ANY
# Validate for NXDOMAIN response and SOA
    @pytest.mark.run(order=12)
    def test_012_dig_alias_with_type_ANY(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type ANY")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"a_alias.infoblox.com","any","NXDOMAIN","SOA")
        perform_dig_query(config.grid_vip,"aaaa_alias.infoblox.com","any","NXDOMAIN","SOA")
        perform_dig_query(config.grid_vip,"mx_alias.infoblox.com","any","NXDOMAIN","SOA")
        perform_dig_query(config.grid_vip,"naptr_alias.infoblox.com","any","NXDOMAIN","SOA")
        perform_dig_query(config.grid_vip,"ptr_alias.infoblox.com","any","NXDOMAIN","SOA")
        perform_dig_query(config.grid_vip,"spf_alias.infoblox.com","any","NXDOMAIN","SOA")
        perform_dig_query(config.grid_vip,"srv_alias.infoblox.com","any","NXDOMAIN","SOA")
        perform_dig_query(config.grid_vip,"txt_alias.infoblox.com","any","NXDOMAIN","SOA")

        display_message("\n***************. Test Case 12 Execution Completed .***************\n")



############################################################################################################################################
# Creating alias records
############################################################################################################################################


# Create type A alias record a_alias inside infoblox.com
# set the target as a.sub.infoblox.com
# Validate if a_alias.infoblox.com has been created
    @pytest.mark.run(order=13)
    def test_013_Create_a_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - a_alias.infoblox.com")
        display_message("\n========================================================\n")

        create_alias_record("a_alias.infoblox.com","a.sub.infoblox.com","A")

        display_message("\n***************. Test Case 13 Execution Completed .***************\n")



# Create type AAAA alias record aaaa_alias inside infoblox.com
# set the target as a.sub.infoblox.com
# Validate if aaaa_alias.infoblox.com has been created
    @pytest.mark.run(order=14)
    def test_014_Create_aaaa_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - aaaa_alias.infoblox.com")
        display_message("\n========================================================\n")

        create_alias_record("aaaa_alias.infoblox.com","aaaa.sub.infoblox.com","AAAA")

        display_message("\n***************. Test Case 14 Execution Completed .***************\n")



# Create type MX alias record mx_alias inside infoblox.com
# set the target as a.sub.infoblox.com
# Validate if mx_alias.infoblox.com has been created
    @pytest.mark.run(order=15)
    def test_015_Create_mx_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - mx_alias.infoblox.com")
        display_message("\n========================================================\n")

        create_alias_record("mx_alias.infoblox.com","mx.sub.infoblox.com","MX")

        display_message("\n***************. Test Case 15 Execution Completed .***************\n")



# Create type NAPTR alias record naptr_alias inside infoblox.com
# set the target as a.sub.infoblox.com
# Validate if naptr_alias.infoblox.com has been created
    @pytest.mark.run(order=16)
    def test_016_Create_naptr_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - naptr_alias.infoblox.com")
        display_message("\n========================================================\n")

        create_alias_record("naptr_alias.infoblox.com","naptr.sub.infoblox.com","NAPTR")

        display_message("\n***************. Test Case 16 Execution Completed .***************\n")



# Create type PTR alias record ptr_alias inside infoblox.com
# set the target as a.sub.infoblox.com
# Validate if ptr_alias.infoblox.com has been created
    @pytest.mark.run(order=17)
    def test_017_Create_ptr_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - ptr_alias.infoblox.com")
        display_message("\n========================================================\n")

        create_alias_record("ptr_alias.infoblox.com","ptr.sub.infoblox.com","PTR")

        display_message("\n***************. Test Case 17 Execution Completed .***************\n")



# Create type SPF alias record spf_alias inside infoblox.com
# set the target as a.sub.infoblox.com
# Validate if spf_alias.infoblox.com has been created
    @pytest.mark.run(order=18)
    def test_018_Create_spf_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - spf_alias.infoblox.com")
        display_message("\n========================================================\n")

        create_alias_record("spf_alias.infoblox.com","spf.sub.infoblox.com","SPF")

        display_message("\n***************. Test Case 18 Execution Completed .***************\n")



# Create type SRV alias record srv_alias inside infoblox.com
# set the target as a.sub.infoblox.com
# Validate if srv_alias.infoblox.com has been created
    @pytest.mark.run(order=19)
    def test_019_Create_srv_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - srv_alias.infoblox.com")
        display_message("\n========================================================\n")

        create_alias_record("srv_alias.infoblox.com","srv.sub.infoblox.com","SRV")

        display_message("\n***************. Test Case 19 Execution Completed .***************\n")



# Create type TXT alias record txt_alias inside infoblox.com
# set the target as a.sub.infoblox.com
# Validate if txt_alias.infoblox.com has been created
    @pytest.mark.run(order=20)
    def test_020_Create_txt_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - txt_alias.infoblox.com")
        display_message("\n========================================================\n")

        create_alias_record("txt_alias.infoblox.com","txt.sub.infoblox.com","TXT")

        display_message("\n***************. Test Case 20 Execution Completed .***************\n")


############################################################################################################################################
# Performing dig query and validating for NOERROR and SOA response
############################################################################################################################################


# Perform dig query for alias with type A
# Validate for NOERROR response and SOA
    @pytest.mark.run(order=21)
    def test_021_dig_alias_with_type_A(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type A")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"a_alias.infoblox.com","a","NOERROR","SOA")

        display_message("\n***************. Test Case 21 Execution Completed .***************\n")



# Perform dig query for alias with type AAAA
# Validate for NOERROR response and SOA
    @pytest.mark.run(order=22)
    def test_022_dig_alias_with_type_AAAA(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type AAAA")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"aaaa_alias.infoblox.com","aaaa","NOERROR","SOA")

        display_message("\n***************. Test Case 22 Execution Completed .***************\n")


# Perform dig query for alias with type MX
# Validate for NOERROR response and SOA
    @pytest.mark.run(order=23)
    def test_023_dig_alias_with_type_MX(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type MX")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"mx_alias.infoblox.com","mx","NOERROR","SOA")

        display_message("\n***************. Test Case 23 Execution Completed .***************\n")


# Perform dig query for alias with type NAPTR
# Validate for NOERROR response and SOA
    @pytest.mark.run(order=24)
    def test_024_dig_alias_with_type_NAPTR(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type NAPTR")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"naptr_alias.infoblox.com","naptr","NOERROR","SOA")

        display_message("\n***************. Test Case 24 Execution Completed .***************\n")


# Perform dig query for alias with type PTR
# Validate for NOERROR response and SOA
    @pytest.mark.run(order=25)
    def test_025_dig_alias_with_type_PTR(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type PTR")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"ptr_alias.infoblox.com","ptr","NOERROR","SOA")

        display_message("\n***************. Test Case 25 Execution Completed .***************\n")


# Perform dig query for alias with type SPF
# Validate for NOERROR response and SOA
    @pytest.mark.run(order=26)
    def test_026_dig_alias_with_type_SPF(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type SPF")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"spf_alias.infoblox.com","spf","NOERROR","SOA")

        display_message("\n***************. Test Case 26 Execution Completed .***************\n")


# Perform dig query for alias with type SRV
# Validate for NOERROR response and SOA
    @pytest.mark.run(order=27)
    def test_027_dig_alias_with_type_SRV(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type SRV")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"srv_alias.infoblox.com","srv","NOERROR","SOA")

        display_message("\n***************. Test Case 27 Execution Completed .***************\n")


# Perform dig query for alias with type TXT
# Validate for NOERROR response and SOA
    @pytest.mark.run(order=28)
    def test_028_dig_alias_with_type_TXT(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type TXT")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"txt_alias.infoblox.com","txt","NOERROR","SOA")

        display_message("\n***************. Test Case 28 Execution Completed .***************\n")


# Perform dig query for alias with type ANY
# Validate for NOERROR response and SOA
    @pytest.mark.run(order=29)
    def test_029_dig_alias_with_type_ANY(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type ANY")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"a_alias.infoblox.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_vip,"aaaa_alias.infoblox.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_vip,"mx_alias.infoblox.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_vip,"naptr_alias.infoblox.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_vip,"ptr_alias.infoblox.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_vip,"spf_alias.infoblox.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_vip,"srv_alias.infoblox.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_vip,"txt_alias.infoblox.com","any","NOERROR","SOA")

        display_message("\n***************. Test Case 29 Execution Completed .***************\n")


############################################################################################################################################
# Creating records under sub zone
############################################################################################################################################


# Create type A record inside sub.infoblox.com - a.sub.infoblox.com
# Validate if a.sub.infoblox.com has been created
    @pytest.mark.run(order=30)
    def test_030_Create_a_record(self):

        display_message("\n========================================================\n")
        display_message("Creating A record - a.sub.infoblox.com")
        display_message("\n========================================================\n")

        data = {"ipv4addr": "1.2.3.4", "name": "a.sub.infoblox.com"}
        create_record_in_sub_zone(data,"a.sub.infoblox.com","a")

        display_message("\n***************. Test Case 30 Execution Completed .***************\n")


# Create type AAAA record inside sub.infoblox.com - aaaa.sub.infoblox.com
# Validate if aaaa.sub.infoblox.com has been created
    @pytest.mark.run(order=31)
    def test_031_Create_aaaa_record(self):

        display_message("\n========================================================\n")
        display_message("Creating AAAA record - aaaa.sub.infoblox.com")
        display_message("\n========================================================\n")

        data = {"ipv6addr": "1111:2222::34", "name": "aaaa.sub.infoblox.com"}
        create_record_in_sub_zone(data,"aaaa.sub.infoblox.com","aaaa")

        display_message("\n***************. Test Case 31 Execution Completed .***************\n")


# Create type MX record inside sub.infoblox.com - mx.sub.infoblox.com
# Validate if mx.sub.infoblox.com has been created
    @pytest.mark.run(order=32)
    def test_032_Create_mx_record(self):

        display_message("\n========================================================\n")
        display_message("Creating MX record - mx.sub.infoblox.com")
        display_message("\n========================================================\n")

        data = {"mail_exchanger": "sub.infoblox.com","name": "mx.sub.infoblox.com","preference": 10}
        create_record_in_sub_zone(data,"mx.sub.infoblox.com","mx")

        display_message("\n***************. Test Case 32 Execution Completed .***************\n")


# Create type NAPTR record inside sub.infoblox.com - naptr.sub.infoblox.com
# Validate if naptr.sub.infoblox.com has been created
    @pytest.mark.run(order=33)
    def test_033_Create_naptr_record(self):

        display_message("\n========================================================\n")
        display_message("Creating NAPTR record - naptr.sub.infoblox.com")
        display_message("\n========================================================\n")

        data = {"name": "naptr.sub.infoblox.com","order": 10,"preference": 10,"replacement": "zone.com"}
        create_record_in_sub_zone(data,"naptr.sub.infoblox.com","naptr")

        display_message("\n***************. Test Case 33 Execution Completed .***************\n")


# Create type PTR record inside sub.infoblox.com - ptr.sub.infoblox.com
# Validate if ptr.sub.infoblox.com has been created
    @pytest.mark.run(order=34)
    def test_034_Create_ptr_record(self):

        display_message("\n========================================================\n")
        display_message("Creating PTR record - ptr.sub.infoblox.com")
        display_message("\n========================================================\n")

        data = {"name": "ptr.sub.infoblox.com","ptrdname": "xyz.com"}
        create_record_in_sub_zone(data,"ptr.sub.infoblox.com","ptr")

        display_message("\n***************. Test Case 34 Execution Completed .***************\n")


# Create Unknown record of type SPF inside sub.infoblox.com - spf.sub.infoblox.com
# Validate if spf.sub.infoblox.com has been created
    @pytest.mark.run(order=35)
    def test_035_Create_spf_record(self):

        display_message("\n========================================================\n")
        display_message("Creating SPF record - spf.sub.infoblox.com")
        display_message("\n========================================================\n")

        data = {"name": "spf.sub.infoblox.com", "record_type": "SPF", "subfield_values": [{"field_type": "P", "field_value": "\"v=spf1\" \"+mx\" \"a:colo.example.com/28\" \"-all\"", "include_length": "NONE"}]}
        create_record_in_sub_zone(data,"spf.sub.infoblox.com","unknown")

        display_message("\n***************. Test Case 35 Execution Completed .***************\n")



# Create type SRV record inside sub.infoblox.com - srv.sub.infoblox.com
# Validate if srv.sub.infoblox.com has been created
    @pytest.mark.run(order=36)
    def test_036_Create_srv_record(self):

        display_message("\n========================================================\n")
        display_message("Creating SRV record - srv.sub.infoblox.com")
        display_message("\n========================================================\n")

        data = {"name": "srv.sub.infoblox.com","port": 22,"priority": 0,"target": "sub.infoblox.com","weight": 0}
        create_record_in_sub_zone(data,"srv.sub.infoblox.com","srv")

        display_message("\n***************. Test Case 36 Execution Completed .***************\n")



# Create type TXT record inside sub.infoblox.com - txt.sub.infoblox.com
# Validate if txt.sub.infoblox.com has been created
    @pytest.mark.run(order=37)
    def test_037_Create_txt_record(self):

        display_message("\n========================================================\n")
        display_message("Creating TXT record - txt.sub.infoblox.com")
        display_message("\n========================================================\n")

        data = {"name": "txt.sub.infoblox.com","text": "HELLO"}
        create_record_in_sub_zone(data,"txt.sub.infoblox.com","txt")

        display_message("\n***************. Test Case 37 Execution Completed .***************\n")



############################################################################################################################################
# Performing dig query and validating for NOERROR response for all record types. Validating for NOERROR and SOA for record type - any
############################################################################################################################################


# Perform dig query for alias with type A
# Validate for NOERROR response and 1.2.3.4
    @pytest.mark.run(order=38)
    def test_038_dig_alias_with_type_A(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type A")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"a_alias.infoblox.com","a","NOERROR","1.2.3.4")

        display_message("\n***************. Test Case 38 Execution Completed .***************\n")



# Perform dig query for alias with type AAAA
# Validate for NOERROR response and 1111:2222::34
    @pytest.mark.run(order=39)
    def test_039_dig_alias_with_type_AAAA(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type AAAA")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"aaaa_alias.infoblox.com","aaaa","NOERROR","1111:2222::34")

        display_message("\n***************. Test Case 39 Execution Completed .***************\n")


# Perform dig query for alias with type MX
# Validate for NOERROR response and sub.infoblox.com
    @pytest.mark.run(order=40)
    def test_040_dig_alias_with_type_MX(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type MX")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"mx_alias.infoblox.com","mx","NOERROR","sub.infoblox.com")

        display_message("\n***************. Test Case 40 Execution Completed .***************\n")


# Perform dig query for alias with type NAPTR
# Validate for NOERROR response and zone.com
    @pytest.mark.run(order=41)
    def test_041_dig_alias_with_type_NAPTR(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type NAPTR")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"naptr_alias.infoblox.com","naptr","NOERROR","zone.com")

        display_message("\n***************. Test Case 41 Execution Completed .***************\n")


# Perform dig query for alias with type PTR
# Validate for NOERROR response and xyz.com
    @pytest.mark.run(order=42)
    def test_042_dig_alias_with_type_PTR(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type PTR")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"ptr_alias.infoblox.com","ptr","NOERROR","xyz.com")

        display_message("\n***************. Test Case 42 Execution Completed .***************\n")


# Perform dig query for alias with type SPF
# Validate for NOERROR response and a:colo.example.com/28
    @pytest.mark.run(order=43)
    def test_043_dig_alias_with_type_SPF(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type SPF")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"spf_alias.infoblox.com","spf","NOERROR","a:colo.example.com/28")

        display_message("\n***************. Test Case 43 Execution Completed .***************\n")


# Perform dig query for alias with type SRV
# Validate for NOERROR response and sub.infoblox.com
    @pytest.mark.run(order=44)
    def test_044_dig_alias_with_type_SRV(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type SRV")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"srv_alias.infoblox.com","srv","NOERROR","sub.infoblox.com")

        display_message("\n***************. Test Case 44 Execution Completed .***************\n")


# Perform dig query for alias with type TXT
# Validate for NOERROR response and "HELLO"
    @pytest.mark.run(order=45)
    def test_045_dig_alias_with_type_TXT(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type TXT")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"txt_alias.infoblox.com","txt","NOERROR","HELLO")

        display_message("\n***************. Test Case 45 Execution Completed .***************\n")


# Perform dig query for alias with type ANY
# Validate for NOERROR response and SOA
    @pytest.mark.run(order=46)
    def test_046_dig_alias_with_type_ANY(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type ANY")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"a_alias.infoblox.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_vip,"aaaa_alias.infoblox.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_vip,"mx_alias.infoblox.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_vip,"naptr_alias.infoblox.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_vip,"ptr_alias.infoblox.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_vip,"spf_alias.infoblox.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_vip,"srv_alias.infoblox.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_vip,"txt_alias.infoblox.com","any","NOERROR","SOA")

        display_message("\n***************. Test Case 46 Execution Completed .***************\n")



############################################################################################################################################
# Performing Negative validations for grid secondary addition with zone transfers and zone sigining for an auth zone containing Alias records
############################################################################################################################################


# Try to Update authoratative zone - infoblox.com
# Assign grid master as grid Secondary and grid member as grid primary with DNS Zone trnasfers
# Perform Negative Validation - ALIAS record is not supported for a zone having secondaries. Therefore, validate the error.
    @pytest.mark.run(order=47)
    def test_047_add_secondaries_to_auth_zone(self):

        display_message("\n========================================================\n")
        display_message("Adding secondaries with dns_zone_transfer to infoblox.com")
        display_message("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth?fqdn=infoblox.com', grid_vip=config.grid_vip)
        get_ref = json.loads(get_ref)[0]['_ref']

        data = {"grid_primary":[{"name": config.grid_member1_fqdn}], "grid_secondaries": [{"name": config.grid_fqdn,"grid_replicate": False}]}
        response = ib_NIOS.wapi_request('PUT', ref=get_ref, fields=json.dumps(data),grid_vip=config.grid_vip)
        display_message(response)

        message="Zone Transfer cannot be used to update grid secondaries if there are Aliases in the zone infoblox.com."

        display_message()
        display_message("\n--------------------------------------------------------\n")
        display_message("Validating addition of secondaries to infoblox.com")
        display_message("\n--------------------------------------------------------\n")

        display_message(response[1])

        if message in response[1]:
            display_message("SUCCESS: Zone Transfer did not update grid secondaries due to presence of Alias records in infoblox.com")
            assert True
        else:
            display_message("FAILURE: Zone transfer has been used to update grid secondaries. It was meant to fail due to presence of Alias records in the zone.")
            assert False

        display_message("\n***************. Test Case 47 Execution Completed .***************\n")



# Try to Update authoratative zone - infoblox.com
# Sign the zone using dnssec_operation function
# Perform Negative Validation - ALIAS record is not supported for a zone having secondaries. Therefore, validate the error.
    @pytest.mark.run(order=48)
    def test_048_Sign_auth_zone(self):

        display_message("\n========================================================\n")
        display_message("Adding secondaries with dns_zone_transfer to infoblox.com")
        display_message("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth?fqdn=infoblox.com', grid_vip=config.grid_vip)
        get_ref = json.loads(get_ref)[0]['_ref']

        data = {"operation":"SIGN"}
        response = ib_NIOS.wapi_request('POST', object_type=get_ref + "?_function=dnssec_operation", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_message(response)

        message="This zone cannot be signed because it contains the Alias record"

        display_message()
        display_message("\n--------------------------------------------------------\n")
        display_message("Validating signing of zone containing Alias record")
        display_message("\n--------------------------------------------------------\n")

        display_message(response[1])

        if message in response[1]:
            display_message("SUCCESS: This zone cannot be signed because it contains the Alias records.")
            assert True
        else:
            display_message("FAILURE: Signing of zone has been successful. It was meant to fail due to presence of Alias records in the zone.")
            assert False

        display_message("\n***************. Test Case 48 Execution Completed .***************\n")



# Create an nsgroup - MMDNS_alias
# Add grid master anf grid member both as grid primaries
# Validate if nsgroup MMDNS_alias has been created or not
    @pytest.mark.run(order=49)
    def test_049_Create_nsgroup(self):

        display_message("\n========================================================\n")
        display_message("Creating name server group - MMDNS_alias")
        display_message("\n========================================================\n")

        data = {"name": "MMDNS_alias", "grid_primary": [{"name": config.grid_fqdn},{"name": config.grid_member1_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="nsgroup", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_message(response)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_message("FAILURE: Couldnot create nsgroup.")
            assert False
        else:
            display_message()
            display_message("\n--------------------------------------------------------\n")
            display_message("Validating name server group - MMDNS_alias")
            display_message("\n--------------------------------------------------------\n")

            response = ib_NIOS.wapi_request('GET', object_type="nsgroup?name=MMDNS_alias", grid_vip=config.grid_vip)
            response=json.loads(response)[0]
            display_message(response)

            if 'MMDNS_alias' in response['_ref']:
                display_message(response["_ref"])
                display_message("SUCCESS: Name server group 'MMDNS_alias' was created!")
                assert True
            else:
                display_message("FAILURE: Name server group 'MMDNS_alias' was NOT created!")
                assert False

        display_message("\n***************. Test Case 49 Execution Completed .***************\n")


# Update authoratative zone - infoblox.com
# Assign ns_group as MMDNS_alias
# Validate if MMDNS_alias has been added.
    @pytest.mark.run(order=50)
    def test_050_add_nsgroup_to_auth_zone(self):

        display_message("\n========================================================\n")
        display_message("Adding ns_group MMDNS_alias to Authoratative zone - infoblox.com")
        display_message("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth?fqdn=infoblox.com', grid_vip=config.grid_vip)
        get_ref = json.loads(get_ref)[0]['_ref']

        data = {"ns_group": "MMDNS_alias"}
        response = ib_NIOS.wapi_request('PUT', ref=get_ref, fields=json.dumps(data),grid_vip=config.grid_vip)
        display_message(response)

        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_message("FAILURE: Adding ns_group to authoratative zone.")
            assert False
        else:
            display_message()
            display_message("\n--------------------------------------------------------\n")
            display_message("Validating addition of ns_group to infoblox.com ")
            display_message("\n--------------------------------------------------------\n")

            response = ib_NIOS.wapi_request('GET', object_type="zone_auth?_return_fields=ns_group", grid_vip=config.grid_vip)
            response=json.loads(response)[0]
            display_message(response)

            if 'MMDNS_alias' in response['ns_group']:
                display_message(response["_ref"])
                display_message("SUCCESS: ns_group has been added to infoblox.com.")
                assert True
            else:
                display_message("FAILURE: Couldnt add ns_group to infoblox.com")
                assert False

        display_message("\n***************. Test Case 50 Execution Completed .***************\n") # requires restart


# Restart services
    @pytest.mark.run(order=51)
    def test_051_Restart_services(self):

        display_message("\n========================================================\n")
        display_message("Restarting Services")
        display_message("\n========================================================\n")

        grid = ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(60)

        display_message("\n***************. Test Case 51 Execution Completed .***************\n")


############################################################################################################################################
# Performing dig query from both master and member and validating NOERROR response for all record types.
# Validating for NOERROR and SOA for record type - any
############################################################################################################################################


# Perform dig query for alias with type A
# Validate for NOERROR response and 1.2.3.4
    @pytest.mark.run(order=52)
    def test_052_dig_alias_with_type_A(self):

        display_message("\n========================================================\n")
        display_message("Master query - Performing dig query for alias record with type A from Master")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"a_alias.infoblox.com","a","NOERROR","1.2.3.4")

        display_message("\n========================================================\n")
        display_message("Member query - Performing dig query for alias record with type A from Member")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_member1_vip,"a_alias.infoblox.com","a","NOERROR","1.2.3.4")


        display_message("\n***************. Test Case 52 Execution Completed .***************\n")



# Perform dig query for alias with type AAAA
# Validate for NOERROR response and 1111:2222::34
    @pytest.mark.run(order=53)
    def test_053_dig_alias_with_type_AAAA(self):

        display_message("\n========================================================\n")
        display_message("Master query - Performing dig query for alias record with type AAAA from Master")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"aaaa_alias.infoblox.com","aaaa","NOERROR","1111:2222::34")

        display_message("\n========================================================\n")
        display_message("Member query - Performing dig query for alias record with type AAAA from Member")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_member1_vip,"aaaa_alias.infoblox.com","aaaa","NOERROR","1111:2222::34")


        display_message("\n***************. Test Case 53 Execution Completed .***************\n")


# Perform dig query for alias with type MX
# Validate for NOERROR response and sub.infoblox.com
    @pytest.mark.run(order=54)
    def test_054_dig_alias_with_type_MX(self):

        display_message("\n========================================================\n")
        display_message("Master query - Performing dig query for alias record with type MX from Master")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"mx_alias.infoblox.com","mx","NOERROR","sub.infoblox.com")

        display_message("\n========================================================\n")
        display_message("Member query - Performing dig query for alias record with type MX from Member")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_member1_vip,"mx_alias.infoblox.com","mx","NOERROR","sub.infoblox.com")


        display_message("\n***************. Test Case 54 Execution Completed .***************\n")


# Perform dig query for alias with type NAPTR
# Validate for NOERROR response and zone.com
    @pytest.mark.run(order=55)
    def test_055_dig_alias_with_type_NAPTR(self):

        display_message("\n========================================================\n")
        display_message("Master query - Performing dig query for alias record with type NAPTR from Master")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"naptr_alias.infoblox.com","naptr","NOERROR","zone.com")

        display_message("\n========================================================\n")
        display_message("Member query - Performing dig query for alias record with type NAPTR from Member")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_member1_vip,"naptr_alias.infoblox.com","naptr","NOERROR","zone.com")


        display_message("\n***************. Test Case 55 Execution Completed .***************\n")


# Perform dig query for alias with type PTR
# Validate for NOERROR response and xyz.com
    @pytest.mark.run(order=56)
    def test_056_dig_alias_with_type_PTR(self):

        display_message("\n========================================================\n")
        display_message("Master query - Performing dig query for alias record with type PTR from Master")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"ptr_alias.infoblox.com","ptr","NOERROR","xyz.com")

        display_message("\n========================================================\n")
        display_message("Member query - Performing dig query for alias record with type PTR from Member")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_member1_vip,"ptr_alias.infoblox.com","ptr","NOERROR","xyz.com")


        display_message("\n***************. Test Case 56 Execution Completed .***************\n")


# Perform dig query for alias with type SPF
# Validate for NOERROR response and a:colo.example.com/28
    @pytest.mark.run(order=57)
    def test_057_dig_alias_with_type_SPF(self):

        display_message("\n========================================================\n")
        display_message("Master query - Performing dig query for alias record with type SPF from Master")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"spf_alias.infoblox.com","spf","NOERROR","a:colo.example.com/28")

        display_message("\n========================================================\n")
        display_message("Member query - Performing dig query for alias record with type SPF from Member")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_member1_vip,"spf_alias.infoblox.com","spf","NOERROR","a:colo.example.com/28")


        display_message("\n***************. Test Case 57 Execution Completed .***************\n")


# Perform dig query for alias with type SRV
# Validate for NOERROR response and sub.infoblox.com
    @pytest.mark.run(order=58)
    def test_058_dig_alias_with_type_SRV(self):

        display_message("\n========================================================\n")
        display_message("Master query - Performing dig query for alias record with type SRV from Master")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"srv_alias.infoblox.com","srv","NOERROR","sub.infoblox.com")

        display_message("\n========================================================\n")
        display_message("Member query - Performing dig query for alias record with type SRV from Member")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_member1_vip,"srv_alias.infoblox.com","srv","NOERROR","sub.infoblox.com")


        display_message("\n***************. Test Case 58 Execution Completed .***************\n")


# Perform dig query for alias with type TXT
# Validate for NOERROR response and "HELLO"
    @pytest.mark.run(order=59)
    def test_059_dig_alias_with_type_TXT(self):

        display_message("\n========================================================\n")
        display_message("Master query - Performing dig query for alias record with type TXT from Master")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"txt_alias.infoblox.com","txt","NOERROR","HELLO")

        display_message("\n========================================================\n")
        display_message("Member query - Performing dig query for alias record with type TXT from Member")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_member1_vip,"txt_alias.infoblox.com","txt","NOERROR","HELLO")


        display_message("\n***************. Test Case 59 Execution Completed .***************\n")


# Perform dig query for alias with type ANY
# Validate for NOERROR response and SOA
    @pytest.mark.run(order=60)
    def test_060_dig_alias_with_type_ANY(self):

        display_message("\n========================================================\n")
        display_message("Master query - Performing dig query for alias record with type ANY from Master")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_vip,"a_alias.infoblox.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_vip,"aaaa_alias.infoblox.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_vip,"mx_alias.infoblox.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_vip,"naptr_alias.infoblox.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_vip,"ptr_alias.infoblox.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_vip,"spf_alias.infoblox.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_vip,"srv_alias.infoblox.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_vip,"txt_alias.infoblox.com","any","NOERROR","SOA")

        display_message("\n========================================================\n")
        display_message("Member query - Performing dig query for alias record with type ANY from Member")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_member1_vip,"a_alias.infoblox.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_member1_vip,"aaaa_alias.infoblox.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_member1_vip,"mx_alias.infoblox.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_member1_vip,"naptr_alias.infoblox.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_member1_vip,"ptr_alias.infoblox.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_member1_vip,"spf_alias.infoblox.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_member1_vip,"srv_alias.infoblox.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_member1_vip,"txt_alias.infoblox.com","any","NOERROR","SOA")


        display_message("\n***************. Test Case 60 Execution Completed .***************\n")



# Create authoratative zone - test.com
# Assign grid member as grid primary
# Validate if test.com has been created.
    @pytest.mark.run(order=61)
    def test_061_Create_auth_zone(self):

        display_message("\n========================================================\n")
        display_message("Creating an Authoratative zone - test.com")
        display_message("\n========================================================\n")

        data = {"fqdn":"test.com","view":"default","grid_primary":[{"name":config.grid_member1_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_message(response)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_message("FAILURE: Create authoratative zone.")
            assert False
        else:
            display_message()
            display_message("\n--------------------------------------------------------\n")
            display_message("Validating Authoratative zone - test.com")
            display_message("\n--------------------------------------------------------\n")

            response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=test.com", grid_vip=config.grid_vip)
            response=json.loads(response)[0]
            display_message(response)

            if 'test.com' in response['_ref']:
                display_message(response["_ref"])
                display_message("SUCCESS: Authoratative Zone 'test.com' was created!")
                assert True
            else:
                display_message("FAILURE: Authoratative Zone 'test.com' was NOT created!")
                assert False

        display_message("\n***************. Test Case 61 Execution Completed .***************\n") # requires restart


# Restart services
    @pytest.mark.run(order=62)
    def test_062_Restart_services(self):

        display_message("\n========================================================\n")
        display_message("Restarting Services")
        display_message("\n========================================================\n")

        grid = ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(60)

        display_message("\n***************. Test Case 62 Execution Completed .***************\n")


# Copy all the records from infoblox.com to test.com
# Use copyzonerecords function for copying
# Validate if the records are copied or not.
    @pytest.mark.run(order=63)
    def test_063_Copy_records_from_old_zone(self):

        display_message("\n========================================================\n")
        display_message("Copying records from infoblox.com to test.com.")
        display_message("\n========================================================\n")

        get_ref1 = ib_NIOS.wapi_request('GET', object_type='zone_auth?fqdn=infoblox.com', grid_vip=config.grid_vip)
        get_ref1 = json.loads(get_ref1)[0]['_ref']

        get_ref2 = ib_NIOS.wapi_request('GET', object_type='zone_auth?fqdn=test.com', grid_vip=config.grid_vip)
        get_ref2 = json.loads(get_ref2)[0]['_ref']

        data = {"destination_zone":get_ref2}
        response = ib_NIOS.wapi_request('POST', object_type=get_ref1 + "?_function=copyzonerecords", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_message(response)

        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_message("FAILURE: Couldnt copy records from infoblox.com to test.com.")
            assert False
        else:
            display_message()
            display_message("\n--------------------------------------------------------\n")
            display_message("Validating Copied records in test.com")
            display_message("\n--------------------------------------------------------\n")

            response = ib_NIOS.wapi_request('GET', object_type="record:alias", grid_vip=config.grid_vip)
            response=json.loads(response)

            alias=0
            for ref in response:
                if 'test.com' in ref['_ref']:
                    display_message(ref)
                    alias=alias+1
                    continue

            if alias==8:
                display_message("SUCCESS: All the records have been successfully copied to test.com.")
                assert True
            else:
                display_message("FAILURE: Something went wrong.. records were not copied to test.com.")
                assert False


        display_message("\n***************. Test Case 63 Execution Completed .***************\n")


############################################################################################################################################
# Performing dig query from member and validating NOERROR response for all record types. Validating NOERROR and SOA for record type - any
############################################################################################################################################


# Perform dig query for alias with type A
# Validate for NOERROR response and 1.2.3.4
    @pytest.mark.run(order=64)
    def test_064_dig_alias_with_type_A(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type A")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_member1_vip,"a_alias.test.com","a","NOERROR","1.2.3.4")

        display_message("\n***************. Test Case 64 Execution Completed .***************\n")



# Perform dig query for alias with type AAAA
# Validate for NOERROR response and 1111:2222::34
    @pytest.mark.run(order=65)
    def test_065_dig_alias_with_type_AAAA(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type AAAA")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_member1_vip,"aaaa_alias.test.com","aaaa","NOERROR","1111:2222::34")

        display_message("\n***************. Test Case 65 Execution Completed .***************\n")


# Perform dig query for alias with type MX
# Validate for NOERROR response and sub.infoblox.com
    @pytest.mark.run(order=66)
    def test_066_dig_alias_with_type_MX(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type MX")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_member1_vip,"mx_alias.test.com","mx","NOERROR","sub.infoblox.com")

        display_message("\n***************. Test Case 66 Execution Completed .***************\n")


# Perform dig query for alias with type NAPTR
# Validate for NOERROR response and zone.com
    @pytest.mark.run(order=67)
    def test_067_dig_alias_with_type_NAPTR(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type NAPTR")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_member1_vip,"naptr_alias.test.com","naptr","NOERROR","zone.com")

        display_message("\n***************. Test Case 67 Execution Completed .***************\n")


# Perform dig query for alias with type PTR
# Validate for NOERROR response and xyz.com
    @pytest.mark.run(order=68)
    def test_068_dig_alias_with_type_PTR(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type PTR")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_member1_vip,"ptr_alias.test.com","ptr","NOERROR","xyz.com")

        display_message("\n***************. Test Case 68 Execution Completed .***************\n")


# Perform dig query for alias with type SPF
# Validate for NOERROR response and a:colo.example.com/28
    @pytest.mark.run(order=69)
    def test_069_dig_alias_with_type_SPF(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type SPF")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_member1_vip,"spf_alias.test.com","spf","NOERROR","a:colo.example.com/28")

        display_message("\n***************. Test Case 69 Execution Completed .***************\n")


# Perform dig query for alias with type SRV
# Validate for NOERROR response and sub.infoblox.com
    @pytest.mark.run(order=70)
    def test_070_dig_alias_with_type_SRV(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type SRV")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_member1_vip,"srv_alias.test.com","srv","NOERROR","sub.infoblox.com")

        display_message("\n***************. Test Case 70 Execution Completed .***************\n")


# Perform dig query for alias with type TXT
# Validate for NOERROR response and "HELLO"
    @pytest.mark.run(order=71)
    def test_071_dig_alias_with_type_TXT(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type TXT")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_member1_vip,"txt_alias.test.com","txt","NOERROR","HELLO")

        display_message("\n***************. Test Case 71 Execution Completed .***************\n")


# Perform dig query for alias with type ANY
# Validate for NOERROR response and SOA
    @pytest.mark.run(order=72)
    def test_072_dig_alias_with_type_ANY(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type ANY")
        display_message("\n========================================================\n")

        perform_dig_query(config.grid_member1_vip,"a_alias.test.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_member1_vip,"aaaa_alias.test.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_member1_vip,"mx_alias.test.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_member1_vip,"naptr_alias.test.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_member1_vip,"ptr_alias.test.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_member1_vip,"spf_alias.test.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_member1_vip,"srv_alias.test.com","any","NOERROR","SOA")
        perform_dig_query(config.grid_member1_vip,"txt_alias.test.com","any","NOERROR","SOA")

        sleep(70)

        display_message("\n***************. Test Case 72 Execution Completed .***************\n")


############################################################################################################################################
# CNAME Record cases
############################################################################################################################################



# Create authoratative zone - zone.com
# Assign grid master as grid primary
# Validate if zone.com has been created.
    @pytest.mark.run(order=73)
    def test_073_Create_auth_zone(self):

        display_message("\n========================================================\n")
        display_message("Creating an Authoratative zone - zone.com")
        display_message("\n========================================================\n")

        data = {"fqdn":"zone.com","view":"default","grid_primary":[{"name":config.grid_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_message(response)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_message("FAILURE: Create authoratative zone.")
            assert False
        else:
            display_message()
            display_message("\n--------------------------------------------------------\n")
            display_message("Validating Authoratative zone - zone.com")
            display_message("\n--------------------------------------------------------\n")

            response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=zone.com", grid_vip=config.grid_vip)
            response=json.loads(response)[0]
            display_message(response)

            if 'zone.com' in response['_ref']:
                display_message(response["_ref"])
                display_message("SUCCESS: Authoratative Zone 'zone.com' was created!")
                assert True
            else:
                display_message("FAILURE: Authoratative Zone 'zone.com' was NOT created!")
                assert False

        display_message("\n***************. Test Case 73 Execution Completed .***************\n") # requires restart


# Restart services
    @pytest.mark.run(order=74)
    def test_074_Restart_services(self):

        display_message("\n========================================================\n")
        display_message("Restarting Services")
        display_message("\n========================================================\n")

        grid = ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(60)

        display_message("\n***************. Test Case 74 Execution Completed .***************\n")


########################################################################
########################################################################
# Creating A record under zone.com and validating cname record cases
########################################################################
########################################################################

############################################################################################################################################
# IBAlias (A)-> CNAME -> A record   ;   A record answered correctly. CNAME not included in answer.
# a_alias -> a_cname -> a
############################################################################################################################################

# Create type A record inside zone.com - a.zone.com
# Validate if a.zone.com has been created
    @pytest.mark.run(order=75)
    def test_075_Create_a_record(self):

        display_message("\n========================================================\n")
        display_message("Creating A record - a.zone.com")
        display_message("\n========================================================\n")

        data = {"ipv4addr": "1.2.3.4", "name": "a.zone.com"}
        create_record_in_zone(data,"a.zone.com","a")

        display_message("\n***************. Test Case 75 Execution Completed .***************\n")


# Create type A cname record a_cname inside zone.com
# set the target as a.zone.com
# Validate if a_cname.zone.com has been created
    @pytest.mark.run(order=76)
    def test_076_Create_a_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - a_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("a_cname.zone.com","a.zone.com")

        display_message("\n***************. Test Case 76 Execution Completed .***************\n")


# Create type A alias record a_alias inside zone.com
# set the target as a_cname.zone.com
# Validate if a_alias.zone.com has been created
    @pytest.mark.run(order=77)
    def test_077_Create_a_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - a_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("a_alias.zone.com","a_cname.zone.com","A")

        display_message("\n***************. Test Case 77 Execution Completed .***************\n")


# Perform dig query for alias with type A
# Validate for NOERROR response and 1.2.3.4
    @pytest.mark.run(order=78)
    def test_078_dig_alias_with_type_A(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type A from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"a_alias.zone.com","a","NOERROR","1.2.3.4","cname")

        display_message("\n***************. Test Case 78 Execution Completed .***************\n")


############################################################################################################################################
# IBAlias (A) -> IBAlias (A) -> CNAME  -> CNAME -> A record   ;   A record answered correctly.
# a1_alias -> a2_alias -> a1_cname -> a_cname -> a
############################################################################################################################################


# Create type A cname record a1_cname inside zone.com
# set the target as a_cname.zone.com
# Validate if a1_cname.zone.com has been created
    @pytest.mark.run(order=79)
    def test_079_Create_a_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - a1_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("a1_cname.zone.com","a_cname.zone.com")

        display_message("\n***************. Test Case 79 Execution Completed .***************\n")


# Create type A alias record a2_alias inside zone.com
# set the target as a1_cname.zone.com
# Validate if a2_alias.zone.com has been created
    @pytest.mark.run(order=80)
    def test_080_Create_a_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - a2_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("a2_alias.zone.com","a1_cname.zone.com","A")

        display_message("\n***************. Test Case 80 Execution Completed .***************\n")


# Create type A alias record a1_alias inside zone.com
# set the target as a2_alias.zone.com
# Validate if a1_alias.zone.com has been created
    @pytest.mark.run(order=81)
    def test_081_Create_a_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - a1_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("a1_alias.zone.com","a2_alias.zone.com","A")

        display_message("\n***************. Test Case 81 Execution Completed .***************\n")


# Perform dig query for alias with type A
# Validate for NOERROR response and 1.2.3.4
    @pytest.mark.run(order=82)
    def test_082_dig_alias_with_type_A(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type A from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"a1_alias.zone.com","a","NOERROR","1.2.3.4","cname")

        display_message("\n***************. Test Case 82 Execution Completed .***************\n")


############################################################################################################################################
# IBAlias (A) -> CNAME -> NOTHING   ;   No answer is returned.
# a3_alias -> a2_cname -> dummy record
############################################################################################################################################

# Create type A cname record a2_cname inside zone.com
# set the target as NOTHING (a dummy record)
# Validate if a2_cname.zone.com has been created
    @pytest.mark.run(order=83)
    def test_083_Create_a_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - a2_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("a2_cname.zone.com","dummy.zone.com")

        display_message("\n***************. Test Case 83 Execution Completed .***************\n")


# Create type A alias record a3_alias inside zone.com
# set the target as a2_cname.zone.com
# Validate if a3_alias.zone.com has been created
    @pytest.mark.run(order=84)
    def test_084_Create_a_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - a3_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("a3_alias.zone.com","a2_cname.zone.com","A")

        display_message("\n***************. Test Case 84 Execution Completed .***************\n")


# Perform dig query for alias with type A
# Validate for NOERROR response and SOA
    @pytest.mark.run(order=85)
    def test_085_dig_alias_with_type_A(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type A from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"a3_alias.zone.com","a","NOERROR","SOA","cname")

        display_message("\n***************. Test Case 85 Execution Completed .***************\n")


############################################################################################################################################
# IBAlias (A) -> IBAlias (A) -> CNAME  -> CNAME -> NOTHING   ;   No answer is returned.
# a4_alias -> a5_alias -> a3_cname -> a2_cname -> dummy record
############################################################################################################################################


# Create type A cname record a3_cname inside zone.com
# set the target to a2_cname.zone.com
# Validate if a3_cname.zone.com has been created
    @pytest.mark.run(order=86)
    def test_086_Create_a_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - a3_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("a3_cname.zone.com","a2_cname.zone.com")

        display_message("\n***************. Test Case 86 Execution Completed .***************\n")


# Create type A alias record a5_alias inside zone.com
# set the target as a3_cname.zone.com
# Validate if a5_alias.zone.com has been created
    @pytest.mark.run(order=87)
    def test_087_Create_a_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - a5_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("a5_alias.zone.com","a3_cname.zone.com","A")

        display_message("\n***************. Test Case 87 Execution Completed .***************\n")


# Create type A alias record a4_alias inside zone.com
# set the target as a5_alias.zone.com
# Validate if a4_alias.zone.com has been created
    @pytest.mark.run(order=88)
    def test_088_Create_a_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - a4_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("a4_alias.zone.com","a5_alias.zone.com","A")

        display_message("\n***************. Test Case 88 Execution Completed .***************\n")


# Perform dig query for alias with type A
# Validate for NOERROR response and SOA
    @pytest.mark.run(order=89)
    def test_089_dig_alias_with_type_A(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type A from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"a4_alias.zone.com","a","NOERROR","SOA","cname")

        display_message("\n***************. Test Case 89 Execution Completed .***************\n")


############################################################################################################################################
# IBAlias (A)-> CNAME-> AAAA record   ;   No answer is returned because Alias is for AAAA record.
# a6_alias -> a4_cname -> aaaa
############################################################################################################################################

# Create type AAAA record inside zone.com - aaaa.zone.com
# Validate if aaaa.zone.com has been created
    @pytest.mark.run(order=90)
    def test_090_Create_aaaa_record(self):

        display_message("\n========================================================\n")
        display_message("Creating AAAA record - aaaa.zone.com")
        display_message("\n========================================================\n")

        data = {"ipv6addr": "1111:2222::34", "name": "aaaa.zone.com"}
        create_record_in_zone(data,"aaaa.zone.com","aaaa")

        display_message("\n***************. Test Case 90 Execution Completed .***************\n")


# Create type A cname record a4_cname inside zone.com
# set the target to aaaa.zone.com
# Validate if a4_cname.zone.com has been created
    @pytest.mark.run(order=91)
    def test_091_Create_a_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - a4_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("a4_cname.zone.com","aaaa.zone.com")

        display_message("\n***************. Test Case 91 Execution Completed .***************\n")


# Create type A alias record a6_alias inside zone.com
# set the target as a4_cname.zone.com
# Validate if a6_alias.zone.com has been created
    @pytest.mark.run(order=92)
    def test_092_Create_a_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - a6_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("a6_alias.zone.com","a4_cname.zone.com","A")

        display_message("\n***************. Test Case 92 Execution Completed .***************\n")


# Perform dig query for alias with type A
# Validate for NOERROR response and SOA
    @pytest.mark.run(order=93)
    def test_093_dig_alias_with_type_A(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type A from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"a6_alias.zone.com","a","NOERROR","SOA","cname")

        display_message("\n***************. Test Case 93 Execution Completed .***************\n")


############################################################################################################################################
# IBAlias (A)-> CNAME -> AAAA record AND A record with same name   ;   A record is returned but the AAAA record is not.
# a7_alias -> a5_cname -> a_and_aaaa        (create 2 records - A and AAAA with name a_and_aaaa)
############################################################################################################################################

# Create type A record inside zone.com - a_and_aaaa.zone.com
# Validate if a_and_aaaa.zone.com has been created
    @pytest.mark.run(order=94)
    def test_094_Create_a_record(self):

        display_message("\n========================================================\n")
        display_message("Creating A record - a_and_aaaa.zone.com")
        display_message("\n========================================================\n")

        data = {"ipv4addr": "1.2.3.4", "name": "a_and_aaaa.zone.com"}
        create_record_in_zone(data,"a_and_aaaa.zone.com","a")

        display_message("\n***************. Test Case 94 Execution Completed .***************\n")


# Create type AAAA record inside zone.com - a_and_aaaa.zone.com
# Validate if a_and_aaaa.zone.com has been created
    @pytest.mark.run(order=95)
    def test_095_Create_aaaa_record(self):

        display_message("\n========================================================\n")
        display_message("Creating AAAA record - a_and_aaaa.zone.com")
        display_message("\n========================================================\n")

        data = {"ipv6addr": "1111:2222::34", "name": "a_and_aaaa.zone.com"}
        create_record_in_zone(data,"a_and_aaaa.zone.com","aaaa")

        display_message("\n***************. Test Case 95 Execution Completed .***************\n")


# Create type A cname record a5_cname inside zone.com
# set the target to a_and_aaaa.zone.com
# Validate if a5_cname.zone.com has been created
    @pytest.mark.run(order=96)
    def test_096_Create_a_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - a5_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("a5_cname.zone.com","a_and_aaaa.zone.com")

        display_message("\n***************. Test Case 96 Execution Completed .***************\n")


# Create type A alias record a7_alias inside zone.com
# set the target as a5_cname.zone.com
# Validate if a7_alias.zone.com has been created
    @pytest.mark.run(order=97)
    def test_097_Create_a_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - a7_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("a7_alias.zone.com","a5_cname.zone.com","A")

        display_message("\n***************. Test Case 97 Execution Completed .***************\n")


# Perform dig query for alias with type A
# Validate for NOERROR response and 1.2.3.4
    @pytest.mark.run(order=98)
    def test_098_dig_alias_with_type_A(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type A from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"a7_alias.zone.com","a","NOERROR","1.2.3.4","1111:2222::34")

        display_message("\n***************. Test Case 98 Execution Completed .***************\n")


############################################################################################################################################
# IBAlias (A)-> CNAME  -> CNAME -> A record AND another A record with same  ;   Both A records are returned.
# a8_alias -> a6_cname -> a7_cname -> a2        (create 2 records - A and A with name a2)
############################################################################################################################################

# Create type A record inside zone.com - a2.zone.com
# Validate if a2.zone.com has been created
    @pytest.mark.run(order=99)
    def test_099_Create_a_record(self):

        display_message("\n========================================================\n")
        display_message("Creating A record - a2.zone.com")
        display_message("\n========================================================\n")

        data = {"ipv4addr": "1.2.3.4", "name": "a2.zone.com"}
        create_record_in_zone(data,"a2.zone.com","a")

        display_message("\n***************. Test Case 99 Execution Completed .***************\n")


# Create type A record inside zone.com - a2.zone.com
# Validate if a2.zone.com has been created
    @pytest.mark.run(order=100)
    def test_100_Create_a_record(self):

        display_message("\n========================================================\n")
        display_message("Creating A record - a2.zone.com")
        display_message("\n========================================================\n")

        data = {"ipv4addr": "5.6.7.8", "name": "a2.zone.com"}
        create_record_in_zone(data,"a2.zone.com","a")

        display_message("\n***************. Test Case 100 Execution Completed .***************\n")


# Create type A cname record a7_cname inside zone.com
# set the target to a2.zone.com
# Validate if a7_cname.zone.com has been created
    @pytest.mark.run(order=101)
    def test_101_Create_a_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - a7_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("a7_cname.zone.com","a2.zone.com")

        display_message("\n***************. Test Case 101 Execution Completed .***************\n")


# Create type A cname record a6_cname inside zone.com
# set the target to a7_cname.zone.com
# Validate if a6_cname.zone.com has been created
    @pytest.mark.run(order=102)
    def test_102_Create_a_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - a6_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("a6_cname.zone.com","a7_cname.zone.com")

        display_message("\n***************. Test Case 102 Execution Completed .***************\n")


# Create type A alias record a8_alias inside zone.com
# set the target as a6_cname.zone.com
# Validate if a8_alias.zone.com has been created
    @pytest.mark.run(order=103)
    def test_103_Create_a_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - a8_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("a8_alias.zone.com","a6_cname.zone.com","A")

        display_message("\n***************. Test Case 103 Execution Completed .***************\n")


# Perform dig query for alias with type A
# Validate for NOERROR response and 1.2.3.4
    @pytest.mark.run(order=104)
    def test_104_dig_alias_with_type_A(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type A from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"a8_alias.zone.com","a","NOERROR","1.2.3.4","cname")
        perform_dig_query_cname(config.grid_vip,"a8_alias.zone.com","a","NOERROR","5.6.7.8","cname")

        display_message("\n***************. Test Case 104 Execution Completed .***************\n")


############################################################################################################################################
# IBAlias (A)  TTL of 15 -> IBAlias (A) -> CNAME  -> CNAME -> A record  ;   TTL in the answer is 15 which is for the IBAlias record, not the A record
# a9_alias -> a10_alias -> a8_cname -> a_cname -> a
############################################################################################################################################

# Create type A cname record a8_cname inside zone.com
# set the target to a_cname.zone.com
# Validate if a8_cname.zone.com has been created
    @pytest.mark.run(order=105)
    def test_105_Create_a_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - a8_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("a8_cname.zone.com","a_cname.zone.com")

        display_message("\n***************. Test Case 105 Execution Completed .***************\n")


# Create type A alias record a10_alias inside zone.com
# set the target as a8_cname.zone.com
# Validate if a10_alias.zone.com has been created
    @pytest.mark.run(order=106)
    def test_106_Create_a_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - a10_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("a10_alias.zone.com","a8_cname.zone.com","A")

        display_message("\n***************. Test Case 106 Execution Completed .***************\n")


# Create type A alias record a9_alias inside zone.com
# Set ttl to 15 seconds
# set the target as a10_alias.zone.com
# Validate if a9_alias.zone.com has been created
    @pytest.mark.run(order=107)
    def test_107_Create_a_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - a9_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("a9_alias.zone.com","a10_alias.zone.com","A")

        display_message("\n========================================================\n")
        display_message("Updating alias record a9_alias.zone.com - setting ttl to 15")
        display_message("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="record:alias?name=a9_alias.zone.com", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[0]['_ref']
        display_message(ref)

        data = {"name":"a9_alias.zone.com", "target_name": "a10_alias.zone.com", "target_type":"A","use_ttl":True, "ttl":15}
        response = ib_NIOS.wapi_request('PUT', ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        display_message(response)

        if response[0]==400 or response[0]==401 or response[0]==404:
            display_message("FAILURE: Update alias record with ttl=15")
            assert False
        else:
            display_message("SUCCESS: Update alias record with ttl=15")
            assert True

        display_message("\n***************. Test Case 107 Execution Completed .***************\n")


# Perform dig query for alias with type A
# Validate for NOERROR response and 1.2.3.4
    @pytest.mark.run(order=108)
    def test_108_dig_alias_with_type_A(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type A from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"a9_alias.zone.com","a","NOERROR","1.2.3.4","cname")

        display_message("\n***************. Test Case 108 Execution Completed .***************\n")



########################################################################
########################################################################
# Creating AAAA record under zone.com and validating cname record cases
########################################################################
########################################################################

############################################################################################################################################
# IBAlias (AAAA)-> CNAME -> AAAA record   ;   AAAA record answered correctly. CNAME not included in answer.
# aaaa_alias -> aaaa_cname -> aaaa (previously created)
############################################################################################################################################


# Create type AAAA cname record aaaa_cname inside zone.com
# set the target as aaaa.zone.com
# Validate if aaaa_cname.zone.com has been created
    @pytest.mark.run(order=109)
    def test_109_Create_aaaa_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - aaaa_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("aaaa_cname.zone.com","aaaa.zone.com")

        display_message("\n***************. Test Case 109 Execution Completed .***************\n")


# Create type AAAA alias record aaaa_alias inside zone.com
# set the target as aaaa_cname.zone.com
# Validate if aaaa_alias.zone.com has been created
    @pytest.mark.run(order=110)
    def test_110_Create_aaaa_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - aaaa_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("aaaa_alias.zone.com","aaaa_cname.zone.com","AAAA")

        display_message("\n***************. Test Case 110 Execution Completed .***************\n")


# Perform dig query for alias with type AAAA
# Validate for NOERROR response and 1111:2222::34
    @pytest.mark.run(order=111)
    def test_111_dig_alias_with_type_AAAA(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type AAAA from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"aaaa_alias.zone.com","aaaa","NOERROR","1111:2222::34","cname")

        display_message("\n***************. Test Case 111 Execution Completed .***************\n")


############################################################################################################################################
# IBAlias (AAAA) -> IBAlias (AAAA) -> CNAME  -> CNAME -> AAAA record   ;   AAAA record answered correctly. CNAME not included in answer.
# aaaa1_alias -> aaaa2_alias -> aaaa1_cname -> aaaa_cname -> aaaa
############################################################################################################################################


# Create type AAAA cname record aaaa1_cname inside zone.com
# set the target as aaaa_cname.zone.com
# Validate if aaaa1_cname.zone.com has been created
    @pytest.mark.run(order=112)
    def test_112_Create_aaaa_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - aaaa1_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("aaaa1_cname.zone.com","aaaa_cname.zone.com")

        display_message("\n***************. Test Case 112 Execution Completed .***************\n")


# Create type AAAA alias record aaaa2_alias inside zone.com
# set the target as aaaa1_cname.zone.com
# Validate if aaaa2_alias.zone.com has been created
    @pytest.mark.run(order=113)
    def test_113_Create_aaaa_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - aaaa2_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("aaaa2_alias.zone.com","aaaa1_cname.zone.com","AAAA")

        display_message("\n***************. Test Case 113 Execution Completed .***************\n")


# Create type AAAA alias record aaaa1_alias inside zone.com
# set the target as aaaa2_alias.zone.com
# Validate if aaaa1_alias.zone.com has been created
    @pytest.mark.run(order=114)
    def test_114_Create_aaaa_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - aaaa1_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("aaaa1_alias.zone.com","aaaa2_alias.zone.com","AAAA")

        display_message("\n***************. Test Case 114 Execution Completed .***************\n")


# Perform dig query for alias with type AAAA
# Validate for NOERROR response and 1111:2222::34
    @pytest.mark.run(order=115)
    def test_115_dig_alias_with_type_AAAA(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type AAAA from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"aaaa1_alias.zone.com","aaaa","NOERROR","1111:2222::34","cname")

        display_message("\n***************. Test Case 115 Execution Completed .***************\n")


############################################################################################################################################
# IBAlias (AAAA) -> CNAME -> NOTHING   ;   No answer is returned.
# aaaa3_alias -> aaaa2_cname -> dummy record
############################################################################################################################################

# Create type AAAA cname record aaaa2_cname inside zone.com
# set the target to a dummy record (dummy.zone.com)
# Validate if aaaa2_cname.zone.com has been created
    @pytest.mark.run(order=116)
    def test_116_Create_aaaa_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - aaaa2_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("aaaa2_cname.zone.com","dummy.zone.com")

        display_message("\n***************. Test Case 116 Execution Completed .***************\n")


# Create type AAAA alias record aaaa3_alias inside zone.com
# set the target as aaaa2_cname.zone.com
# Validate if aaaa3_alias.zone.com has been created
    @pytest.mark.run(order=117)
    def test_117_Create_aaaa_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - aaaa3_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("aaaa3_alias.zone.com","aaaa2_cname.zone.com","AAAA")

        display_message("\n***************. Test Case 117 Execution Completed .***************\n")


# Perform dig query for alias with type AAAA
# Validate for NOERROR response and SOA
    @pytest.mark.run(order=118)
    def test_118_dig_alias_with_type_AAAA(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type AAAA from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"aaaa3_alias.zone.com","aaaa","NOERROR","SOA","cname")

        display_message("\n***************. Test Case 118 Execution Completed .***************\n")


############################################################################################################################################
# IBAlias (AAAA) -> IBAlias (AAAA) -> CNAME  -> CNAME -> NOTHING   ;   No answer is returned.
# aaaa4_alias -> aaaa5_alias -> aaaa3_cname -> aaaa4_cname -> dummy record
############################################################################################################################################

# Create type AAAA cname record aaaa4_cname inside zone.com
# set the target to a dummy record (dummy.zone.com)
# Validate if aaaa4_cname.zone.com has been created
    @pytest.mark.run(order=119)
    def test_119_Create_aaaa_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - aaaa4_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("aaaa4_cname.zone.com","dummy.zone.com")

        display_message("\n***************. Test Case 119 Execution Completed .***************\n")


# Create type AAAA cname record aaaa3_cname inside zone.com
# set the target as aaaa4_cname.zone.com
# Validate if aaaa3_cname.zone.com has been created
    @pytest.mark.run(order=120)
    def test_120_Create_aaaa_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - aaaa3_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("aaaa3_cname.zone.com","aaaa4_cname.zone.com")

        display_message("\n***************. Test Case 120 Execution Completed .***************\n")


# Create type AAAA alias record aaaa5_alias inside zone.com
# set the target as aaaa3_cname.zone.com
# Validate if aaaa5_alias.zone.com has been created
    @pytest.mark.run(order=121)
    def test_121_Create_aaaa_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - aaaa5_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("aaaa5_alias.zone.com","aaaa3_cname.zone.com","AAAA")

        display_message("\n***************. Test Case 121 Execution Completed .***************\n")


# Create type AAAA alias record aaaa4_alias inside zone.com
# set the target as aaaa5_alias.zone.com
# Validate if aaaa4_alias.zone.com has been created
    @pytest.mark.run(order=122)
    def test_122_Create_aaaa_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - aaaa4_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("aaaa4_alias.zone.com","aaaa5_alias.zone.com","AAAA")

        display_message("\n***************. Test Case 122 Execution Completed .***************\n")


# Perform dig query for alias with type AAAA
# Validate for NOERROR response and SOA
    @pytest.mark.run(order=123)
    def test_123_dig_alias_with_type_AAAA(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type AAAA from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"aaaa4_alias.zone.com","aaaa","NOERROR","SOA","cname")

        display_message("\n***************. Test Case 123 Execution Completed .***************\n")


############################################################################################################################################
# IBAlias (AAAA)-> CNAME-> A record   ;   No answer is returned because Alias is for A record.
# aaaa6_alias -> aaaa5_cname -> a
############################################################################################################################################

# Create type AAAA cname record aaaa5_cname inside zone.com
# set the target as a.zone.com
# Validate if aaaa5_cname.zone.com has been created
    @pytest.mark.run(order=124)
    def test_124_Create_aaaa_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - aaaa5_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("aaaa5_cname.zone.com","a.zone.com")

        display_message("\n***************. Test Case 124 Execution Completed .***************\n")


# Create type AAAA alias record aaaa6_alias inside zone.com
# set the target as aaaa5_cname.zone.com
# Validate if aaaa6_alias.zone.com has been created
    @pytest.mark.run(order=125)
    def test_125_Create_aaaa_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - aaaa6_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("aaaa6_alias.zone.com","aaaa5_cname.zone.com","AAAA")

        display_message("\n***************. Test Case 125 Execution Completed .***************\n")


# Perform dig query for alias with type AAAA
# Validate for NOERROR response and SOA
    @pytest.mark.run(order=126)
    def test_126_dig_alias_with_type_AAAA(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type AAAA from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"aaaa6_alias.zone.com","aaaa","NOERROR","SOA","cname")

        display_message("\n***************. Test Case 126 Execution Completed .***************\n")


############################################################################################################################################
# IBAlias (AAAA)-> CNAME -> AAAA record AND A record with same name   ;   AAAA record is returned but A record is not.
# aaaa7_alias -> aaaa6_cname -> a_and_aaaa  (previously created)
############################################################################################################################################

# Create type AAAA cname record aaaa6_cname inside zone.com
# set the target as a_and_aaaa.zone.com
# Validate if aaaa6_cname.zone.com has been created
    @pytest.mark.run(order=127)
    def test_127_Create_aaaa_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - aaaa6_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("aaaa6_cname.zone.com","a_and_aaaa.zone.com")

        display_message("\n***************. Test Case 127 Execution Completed .***************\n")


# Create type AAAA alias record aaaa7_alias inside zone.com
# set the target as aaaa6_cname.zone.com
# Validate if aaaa7_alias.zone.com has been created
    @pytest.mark.run(order=128)
    def test_128_Create_aaaa_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - aaaa7_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("aaaa7_alias.zone.com","aaaa6_cname.zone.com","AAAA")

        display_message("\n***************. Test Case 128 Execution Completed .***************\n")


# Perform dig query for alias with type AAAA
# Validate for NOERROR response and 1111:2222::34
    @pytest.mark.run(order=129)
    def test_129_dig_alias_with_type_AAAA(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type AAAA from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"aaaa7_alias.zone.com","aaaa","NOERROR","1111:2222::34","1.2.3.4")

        display_message("\n***************. Test Case 129 Execution Completed .***************\n")


############################################################################################################################################
# IBAlias (AAAA)-> CNAME -> CNAME -> AAAA record AND another AAAA record with same name   ;  both AAAA records are returned
# aaaa8_alias -> aaaa7_cname -> aaaa8_cname -> aaaa2.zone.com  (2 AAAA reocrds with name aaaa2.zone.com)
# Open bug - NIOS-84042
############################################################################################################################################

# Create type AAAA record inside zone.com - aaaa2.zone.com
# Validate if aaaa2.zone.com has been created
    @pytest.mark.run(order=130)
    def test_130_Create_aaaa_record(self):

        display_message("\n========================================================\n")
        display_message("Creating AAAA record - aaaa2.zone.com")
        display_message("\n========================================================\n")

        data = {"ipv6addr": "1111:2222::34", "name": "aaaa2.zone.com"}
        create_record_in_zone(data,"aaaa2.zone.com","aaaa")

        display_message("\n***************. Test Case 130 Execution Completed .***************\n")


# Create type AAAA record inside zone.com - aaaa2.zone.com
# Validate if aaaa2.zone.com has been created
    @pytest.mark.run(order=131)
    def test_131_Create_aaaa_record(self):

        display_message("\n========================================================\n")
        display_message("Creating AAAA record - aaaa2.zone.com")
        display_message("\n========================================================\n")

        data = {"ipv6addr": "3333:4444::56", "name": "aaaa2.zone.com"}
        create_record_in_zone(data,"aaaa2.zone.com","aaaa")

        display_message("\n***************. Test Case 1301Execution Completed .***************\n")


# Create type AAAA cname record aaaa8_cname inside zone.com
# set the target as aaaa2.zone.com
# Validate if aaaa8_cname.zone.com has been created
    @pytest.mark.run(order=132)
    def test_132_Create_aaaa_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - aaaa8_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("aaaa8_cname.zone.com","aaaa2.zone.com")

        display_message("\n***************. Test Case 132 Execution Completed .***************\n")


# Create type AAAA cname record aaaa7_cname inside zone.com
# set the target as aaaa8_cname.zone.com
# Validate if aaaa7_cname.zone.com has been created
    @pytest.mark.run(order=133)
    def test_133_Create_aaaa_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - aaaa7_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("aaaa7_cname.zone.com","aaaa8_cname.zone.com")

        display_message("\n***************. Test Case 133 Execution Completed .***************\n")


# Create type AAAA alias record aaaa8_alias inside zone.com
# set the target as aaaa7_cname.zone.com
# Validate if aaaa8_alias.zone.com has been created
    @pytest.mark.run(order=134)
    def test_134_Create_aaaa_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - aaaa8_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("aaaa8_alias.zone.com","aaaa7_cname.zone.com","AAAA")

        display_message("\n***************. Test Case 134 Execution Completed .***************\n")


# Perform dig query for alias with type AAAA
# Validate for NOERROR response and 1111:2222::34 and 3333:4444::56
    @pytest.mark.run(order=135)
    def test_135_dig_alias_with_type_AAAA(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type AAAA from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"aaaa8_alias.zone.com","aaaa","NOERROR","1111:2222::34","cname")
        perform_dig_query_cname(config.grid_vip,"aaaa8_alias.zone.com","aaaa","NOERROR","3333:4444::56","cname")

        display_message("\n***************. Test Case 135 Execution Completed .***************\n")


############################################################################################################################################
# IBAlias (AAAA)  TTL of 15 -> IBAlias (AAAA) -> CNAME  -> CNAME -> AAAA record   ;  TTL in the answer is 15 for the IBAlias record, not the AAAA record
# aaaa9_alias -> aaaa10_alias -> aaaa9_cname -> aaaa_cname -> aaaa
############################################################################################################################################

# Create type AAAA cname record aaaa9_cname inside zone.com
# set the target as aaaa_cname.zone.com
# Validate if aaaa9_cname.zone.com has been created
    @pytest.mark.run(order=136)
    def test_136_Create_aaaa_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - aaaa9_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("aaaa9_cname.zone.com","aaaa_cname.zone.com")

        display_message("\n***************. Test Case 136 Execution Completed .***************\n")


# Create type AAAA alias record aaaa10_alias inside zone.com
# set the target as aaaa9_cname.zone.com
# Validate if aaaa10_alias.zone.com has been created
    @pytest.mark.run(order=137)
    def test_137_Create_aaaa_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - aaaa10_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("aaaa10_alias.zone.com","aaaa9_cname.zone.com","AAAA")

        display_message("\n***************. Test Case 137 Execution Completed .***************\n")


# Create type AAAA alias record aaaa9_alias inside zone.com
# set the target as aaaa10_alias.zone.com
# Validate if aaaa9_alias.zone.com has been created
    @pytest.mark.run(order=138)
    def test_138_Create_aaaa_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - aaaa9_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("aaaa9_alias.zone.com","aaaa10_alias.zone.com","AAAA")

        display_message("\n========================================================\n")
        display_message("Updating alias record aaaa9_alias.zone.com - setting ttl to 15")
        display_message("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="record:alias?name=aaaa9_alias.zone.com", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[0]['_ref']
        display_message(ref)

        data = {"name":"aaaa9_alias.zone.com", "target_name": "aaaa10_alias.zone.com", "target_type":"AAAA","use_ttl":True, "ttl":15}
        response = ib_NIOS.wapi_request('PUT', ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        display_message(response)

        if response[0]==400 or response[0]==401 or response[0]==404:
            display_message("FAILURE: Update alias record with ttl=15")
            assert False
        else:
            display_message("SUCCESS: Update alias record with ttl=15")
            assert True

        display_message("\n***************. Test Case 138 Execution Completed .***************\n")


# Perform dig query for alias with type AAAA
# Validate for NOERROR response and 1111:2222::34
    @pytest.mark.run(order=139)
    def test_139_dig_alias_with_type_AAAA(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type AAAA from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"aaaa9_alias.zone.com","aaaa","NOERROR","1111:2222::34","cname")

        display_message("\n***************. Test Case 139 Execution Completed .***************\n")


############################################################################################################################################
# IBAlias (A) -> DNAME -> A record   ;
# a11_alias -> a_dname -> a
############################################################################################################################################




############################################################################################################################################
# IBAlias (AAAA) -> DNAME -> AAAA record   ;
# aaaa11_alias -> aaaa_dname -> aaaa
############################################################################################################################################




############################################################################################################################################
# IBAlias (MX) -> CNAME -> MX record   ;
# mx_alias -> mx_cname -> mx
############################################################################################################################################

# Create type MX record inside zone.com - mx.zone.com
# Validate if mx.zone.com has been created
    @pytest.mark.run(order=140)
    def test_140_Create_mx_record(self):

        display_message("\n========================================================\n")
        display_message("Creating MX record - mx.zone.com")
        display_message("\n========================================================\n")

        data = {"mail_exchanger": "myzone.com","name": "mx.zone.com","preference": 10}
        create_record_in_zone(data,"mx.zone.com","mx")

        display_message("\n***************. Test Case 140 Execution Completed .***************\n")


# Create type MX cname record mx_cname inside zone.com
# set the target as mx.zone.com
# Validate if mx_cname.zone.com has been created
    @pytest.mark.run(order=141)
    def test_141_Create_mx_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - mx_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("mx_cname.zone.com","mx.zone.com")

        display_message("\n***************. Test Case 141 Execution Completed .***************\n")


# Create type MX alias record mx_alias inside zone.com
# set the target as mx_cname.zone.com
# Validate if mx_alias.zone.com has been created
    @pytest.mark.run(order=142)
    def test_142_Create_mx_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - mx_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("mx_alias.zone.com","mx_cname.zone.com","MX")

        display_message("\n***************. Test Case 142 Execution Completed .***************\n")


# Perform dig query for alias with type MX
# Validate for NOERROR response and 'myzone.com'
    @pytest.mark.run(order=143)
    def test_143_dig_alias_with_type_MX(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type MX from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"mx_alias.zone.com","mx","NOERROR","myzone.com","cname")

        display_message("\n***************. Test Case 143 Execution Completed .***************\n")



############################################################################################################################################
# import zone not supported, perform negative validation
# Update zone.com - import from ip 10.35.173.12
############################################################################################################################################

    @pytest.mark.run(order=144)
    def test_144_Performing_import_zone(self):

        display_message("\n========================================================\n")
        display_message("Performing import zone for zone.com")
        display_message("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=zone.com", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[0]['_ref']
        display_message(ref)

        data = {"use_import_from":True, "import_from":config.grid_member1_vip}
        response = ib_NIOS.wapi_request('PUT', ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        display_message(response[1])

        message="Zone is disabled due to a failed zone import from the remote server. Make sure that the zone information is correct"

        if message in response[1]:
            display_message("SUCCESS: Zone is disabled due to a failed zone import from the remote server. Make sure that the zone information is correct")
            assert True
        else:
            display_message("FAILURE: Something went wrong..zone was updated! Please check the grid..")
            assert False

        display_message("\n***************. Test Case 144 Execution Completed .***************\n")


############################################################################################################################################
# run dig query axfr and make sure the ALIAS records are not in the list
# dig @<master.ip> zone.com axfr
############################################################################################################################################

# Perform dig query for zone.com with axfr
# Validate for NOERROR response and ALIAS records not present in the list
    @pytest.mark.run(order=145)
    def test_145_dig_zone_with_axfr(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for zone.com with axfr from Master")
        display_message("\n========================================================\n")

        query ="dig @" + config.grid_vip +" zone.com" +" in axfr"
        display_message(query)
        query = subprocess.check_output(query,shell=True)
        display_message(query)

        if 'alias' not in query:
            display_message("SUCCESS: Alias records not found in AXFR list!")
            assert True
        else:
            display_message("FAILURE: Something went wrong! one or more Alias records were found in AXFR list!")
            assert False

        display_message("\n***************. Test Case 145 Execution Completed .***************\n")


############################################################################################################################################
# perform copy operation to a zone in another view
# Create a new view - vvk view
# Create a new auth zone - vvk.com
# Copy all the records from zone.com to vvk.com
############################################################################################################################################


    @pytest.mark.run(order=146)
    def test_146_Create_dns_view(self):

        display_message("\n========================================================\n")
        display_message("Creating a DNS view - vvk")
        display_message("\n========================================================\n")

        data = {"name":"vvk"}
        response = ib_NIOS.wapi_request('POST', object_type="view", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_message(response)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_message("FAILURE: Create DNS view.")
            assert False
        else:
            display_message()
            display_message("\n--------------------------------------------------------\n")
            display_message("Validating DNS view - vvk")
            display_message("\n--------------------------------------------------------\n")

            response = ib_NIOS.wapi_request('GET', object_type="view?name=vvk", grid_vip=config.grid_vip)
            response=json.loads(response)[0]
            display_message(response)

            if 'vvk' in response['_ref']:
                display_message(response["_ref"])
                display_message("SUCCESS: DNS view 'vvk' was created!")
                assert True
            else:
                display_message("FAILURE: DNS view 'vvk' was NOT created!")
                assert False

        display_message("\n***************. Test Case 146 Execution Completed .***************\n") # requires restart


    @pytest.mark.run(order=147)
    def test_147_Create_auth_zone(self):

        display_message("\n========================================================\n")
        display_message("Creating an Authoratative zone - vvk.com")
        display_message("\n========================================================\n")

        data = {"fqdn":"vvk.com","view":"vvk","grid_primary":[{"name":config.grid_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_message(response)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_message("FAILURE: Create authoratative zone.")
            assert False
        else:
            display_message()
            display_message("\n--------------------------------------------------------\n")
            display_message("Validating Authoratative zone - vvk.com")
            display_message("\n--------------------------------------------------------\n")

            response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=vvk.com", grid_vip=config.grid_vip)
            response=json.loads(response)[0]
            display_message(response)

            if 'vvk.com' in response['_ref']:
                display_message(response["_ref"])
                display_message("SUCCESS: Authoratative Zone 'vvk.com' was created!")
                assert True
            else:
                display_message("FAILURE: Authoratative Zone 'vvk.com' was NOT created!")
                assert False

        display_message("\n***************. Test Case 147 Execution Completed .***************\n") # requires restart


# Restart services
    @pytest.mark.run(order=148)
    def test_148_Restart_services(self):

        display_message("\n========================================================\n")
        display_message("Restarting Services")
        display_message("\n========================================================\n")

        grid = ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(60)

        display_message("\n***************. Test Case 148 Execution Completed .***************\n")



    @pytest.mark.run(order=149)
    def test_149_Copy_records_from_old_zone(self):

        display_message("\n========================================================\n")
        display_message("Copying records from zone.com.com to vvk.com.")
        display_message("\n========================================================\n")

        get_ref1 = ib_NIOS.wapi_request('GET', object_type='zone_auth?fqdn=zone.com', grid_vip=config.grid_vip)
        get_ref1 = json.loads(get_ref1)[0]['_ref']

        get_ref2 = ib_NIOS.wapi_request('GET', object_type='zone_auth?fqdn=vvk.com', grid_vip=config.grid_vip)
        get_ref2 = json.loads(get_ref2)[0]['_ref']

        data = {"destination_zone":get_ref2}
        response = ib_NIOS.wapi_request('POST', object_type=get_ref1 + "?_function=copyzonerecords", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_message(response)

        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_message("FAILURE: Couldnt copy records from zone.com to vvk.com.")
            assert False
        else:
            display_message()
            display_message("\n--------------------------------------------------------\n")
            display_message("Validating Copied records in vvk.com")
            display_message("\n--------------------------------------------------------\n")

            response = ib_NIOS.wapi_request('GET', object_type="record:alias", grid_vip=config.grid_vip)
            response=json.loads(response)

            alias=0
            for ref in response:
                if 'vvk.com' in ref['_ref']:
                    display_message(ref)
                    alias=alias+1
                    continue

            if alias>=10:
                display_message("SUCCESS: All the records have been successfully copied to vvk.com.")
                assert True
            else:
                display_message("FAILURE: Something went wrong.. records were not copied to vvk.com.")
                assert False


        display_message("\n***************. Test Case 149 Execution Completed .***************\n")


############################################################################################################################################
# IBAlias (A) -> DNAME -> A record   ;
# a11_alias -> a_dname -> a
############################################################################################################################################

# Create dname record a_dname inside zone.com
# set the target to a.zone.com
# Validate if a_dname.zone.com has been created
    @pytest.mark.run(order=150)
    def test_150_Create_a_dname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating dname record - a_dname.zone.com")
        display_message("\n========================================================\n")

        create_dname_record("a_dname.zone.com","a.zone.com")

        display_message("\n***************. Test Case 150 Execution Completed .***************\n")

# Create type A alias record a11_alias inside zone.com
# set the target as a_dname.zone.com
# Validate if a11_alias.zone.com has been created
    @pytest.mark.run(order=151)
    def test_151_Create_a_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - a11_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("a11_alias.zone.com","a_dname.zone.com","A")

        display_message("\n***************. Test Case 151 Execution Completed .***************\n")


# Perform dig query for alias with type A
# Validate for NOERROR response and 1.2.3.4
    @pytest.mark.run(order=152)
    def test_152_dig_alias_with_type_A(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type A from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"a11_alias.zone.com","a","NOERROR","1.2.3.4","dname")

        display_message("\n***************. Test Case 152 Execution Completed .***************\n")



############################################################################################################################################
# IBAlias (AAAA) -> DNAME -> AAAA record   ;
# aaaa11_alias -> aaaa_dname -> aaaa
############################################################################################################################################


# Create dname record aaaa_dname inside zone.com
# set the target to aaaa.zone.com
# Validate if aaaa_dname.zone.com has been created
    @pytest.mark.run(order=153)
    def test_153_Create_a_dname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating dname record - aaaa_dname.zone.com")
        display_message("\n========================================================\n")

        create_dname_record("aaaa_dname.zone.com","aaaa.zone.com")

        display_message("\n***************. Test Case 153 Execution Completed .***************\n")

# Create type AAAA alias record aaaa11_alias inside zone.com
# set the target as aaaa_dname.zone.com
# Validate if aaaa11_alias.zone.com has been created
    @pytest.mark.run(order=154)
    def test_154_Create_a_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - aaaa11_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("aaaa11_alias.zone.com","aaaa_dname.zone.com","AAAA")

        display_message("\n***************. Test Case 154 Execution Completed .***************\n")


# Perform dig query for alias with type AAAA
# Validate for NOERROR response and 1111:2222::34
    @pytest.mark.run(order=155)
    def test_155_dig_alias_with_type_AAAA(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type AAAA from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"aaaa11_alias.zone.com","aaaa","NOERROR","1111:2222::34","dname")

        display_message("\n***************. Test Case 155 Execution Completed .***************\n")


############################################################################################################################################
# IBAlias (MX) -> DNAME -> MX record   ;
# mx2_alias -> mx_dname -> mx  (previously created)
############################################################################################################################################


# Create type MX dname record mx_dname inside zone.com
# set the target as mx.zone.com
# Validate if mx_dname.zone.com has been created
    @pytest.mark.run(order=156)
    def test_156_Create_mx_dname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating dname record - mx_dname.zone.com")
        display_message("\n========================================================\n")

        create_dname_record("mx_dname.zone.com","mx.zone.com")

        display_message("\n***************. Test Case 156 Execution Completed .***************\n")


# Create type MX alias record mx2_alias inside zone.com
# set the target as mx_dname.zone.com
# Validate if mx2_alias.zone.com has been created
    @pytest.mark.run(order=157)
    def test_157_Create_mx_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - mx2_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("mx2_alias.zone.com","mx_dname.zone.com","MX")

        display_message("\n***************. Test Case 157 Execution Completed .***************\n")


# Perform dig query for alias with type MX
# Validate for NOERROR response and 'myzone.com'
    @pytest.mark.run(order=158)
    def test_158_dig_alias_with_type_MX(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type MX from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"mx2_alias.zone.com","mx","NOERROR","myzone.com","dname")

        display_message("\n***************. Test Case 158 Execution Completed .***************\n")


# Enabeling the authoratative zone - zone.com

    @pytest.mark.run(order=159)
    def test_159_Enabel_zone(self):

        display_message("\n========================================================\n")
        display_message("Enabling the Authoratative zone - zone.com")
        display_message("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=zone.com", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[0]['_ref']
        print(ref)

        data = {"disable":False}
        response = ib_NIOS.wapi_request('PUT', ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)

        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            print("FAILURE: Enabling zone - zone.com")
            assert False
        else:
            print("SUCCESS: Enabling zone - zone.com")
            assert True

        display_message("\n***************. Test Case 159 Execution Completed .***************\n") # requires restart


# Create a delegation nsgroup - delegation_NS in grid 2
# Add grid 1 as name server in grid 2
# Validate if nsgroup delegation_NS has been created or not
    @pytest.mark.run(order=160)
    def test_160_Create_nsgroup(self):

        display_message("\n========================================================\n")
        display_message("Creating name server group - delegation_NS")
        display_message("\n========================================================\n")

        data = {"name": "delegation_NS", "delegate_to":[{"address": config.grid_vip,"name": config.grid_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="nsgroup:delegation", fields=json.dumps(data), grid_vip=config.grid2_vip)
        display_message(response)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_message("FAILURE: Couldnot create nsgroup.")
            assert False
        else:
            display_message()
            display_message("\n--------------------------------------------------------\n")
            display_message("Validating name server group - delegation_NS")
            display_message("\n--------------------------------------------------------\n")

            response = ib_NIOS.wapi_request('GET', object_type="nsgroup:delegation?name=delegation_NS", grid_vip=config.grid2_vip)
            response=json.loads(response)[0]
            display_message(response)

            if 'delegation_NS' in response['_ref']:
                display_message(response["_ref"])
                display_message("SUCCESS: Name server group 'delegation_NS' was created!")
                assert True
            else:
                display_message("FAILURE: Name server group 'delegation_NS' was NOT created!")
                assert False

        display_message("\n***************. Test Case 160 Execution Completed .***************\n")



# Create authoratative zone - com
# Assign grid master as grid primary
# Validate if com has been created.
    @pytest.mark.run(order=161)
    def test_161_Create_auth_zone(self):

        display_message("\n========================================================\n")
        display_message("Creating an Authoratative zone - com")
        display_message("\n========================================================\n")

        data = {"fqdn":"com","view":"default","grid_primary":[{"name":config.grid2_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data), grid_vip=config.grid2_vip)
        display_message(response)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_message("FAILURE: Create authoratative zone.")
            assert False
        else:
            display_message()
            display_message("\n--------------------------------------------------------\n")
            display_message("Validating Authoratative zone - com")
            display_message("\n--------------------------------------------------------\n")

            response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=com", grid_vip=config.grid2_vip)
            response=json.loads(response)[0]
            display_message(response)

            if 'com' in response['_ref']:
                display_message(response["_ref"])
                display_message("SUCCESS: Authoratative Zone 'com' was created!")
                assert True
            else:
                display_message("FAILURE: Authoratative Zone 'com' was NOT created!")
                assert False

        display_message("\n***************. Test Case 161 Execution Completed .***************\n") # requires restart



# Restart services
    @pytest.mark.run(order=162)
    def test_162_Restart_services(self):

        display_message("\n========================================================\n")
        display_message("Restarting Services")
        display_message("\n========================================================\n")

        grid = ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(35)

        display_message("\n***************. Test Case 162 Execution Completed .***************\n")


# Create delegation zone - zone.com
# Assign grid master as grid primary
# Validate if zone.com has been created.
    @pytest.mark.run(order=163)
    def test_163_Create_delegation_zone(self):

        display_message("\n========================================================\n")
        display_message("Creating an Delegation zone - zone.com")
        display_message("\n========================================================\n")

        data = {"fqdn":"zone.com","view":"default","ns_group":"delegation_NS","delegate_to":[]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_delegated", fields=json.dumps(data), grid_vip=config.grid2_vip)
        display_message(response)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_message("FAILURE: Create delegation zone.")
            assert False
        else:
            display_message()
            display_message("\n--------------------------------------------------------\n")
            display_message("Validating Delegation zone - zone.com")
            display_message("\n--------------------------------------------------------\n")

            response = ib_NIOS.wapi_request('GET', object_type="zone_delegated?fqdn=zone.com", grid_vip=config.grid2_vip)
            response=json.loads(response)[0]
            display_message(response)

            if 'zone.com' in response['_ref']:
                display_message(response["_ref"])
                display_message("SUCCESS: Delegation Zone 'zone.com' was created!")
                assert True
            else:
                display_message("FAILURE: Delegation Zone 'zone.com' was NOT created!")
                assert False

        display_message("\n***************. Test Case 163 Execution Completed .***************\n") # requires restart


# Restart services
    @pytest.mark.run(order=164)
    def test_164_Restart_services(self):

        display_message("\n========================================================\n")
        display_message("Restarting Services")
        display_message("\n========================================================\n")

        grid = ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(35)

        display_message("\n***************. Test Case 164 Execution Completed .***************\n")


    @pytest.mark.run(order=165)
    def test_165_Enable_recurssion(self):

        display_message("\n========================================================\n")
        display_message("Enabeling recurssion in Grid:2")
        display_message("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns", grid_vip=config.grid2_vip)
        ref=json.loads(get_ref)[0]['_ref']
        print(ref)

        data = {"allow_recursive_query": True}
        response = ib_NIOS.wapi_request('PUT', ref, fields=json.dumps(data), grid_vip=config.grid2_vip)
        print(response)

        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            print("FAILURE: Enabling recursion in Grid:2")
            assert False
        else:
            print("SUCCESS: Enabling recursion in Grid:2")
            assert True

        display_message("\n***************. Test Case 165 Execution Completed .***************\n") # requires restart





# Restart services
    @pytest.mark.run(order=166)
    def test_166_Restart_services(self):

        display_message("\n========================================================\n")
        display_message("Restarting Services")
        display_message("\n========================================================\n")

        grid = ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus",grid_vip=config.grid_vip)
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")

        grid = ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus",grid_vip=config.grid2_vip)
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",grid_vip=config.grid2_vip)

        sleep(40)

        display_message("\n***************. Test Case 166 Execution Completed .***************\n")



##########################################################################################################
# IBAlias (A)-> Delegated A record
# a_alias -> a                      [inside infoblox.com]
##########################################################################################################

    @pytest.mark.run(order=167)
    def test_167_dig_alias_with_type_A(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type A from Grid:2")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid2_vip,"a_alias.zone.com","a","NOERROR","1.2.3.4","cname")

        display_message("\n***************. Test Case 167 Execution Completed .***************\n")


##########################################################################################################
# IBAlias (A)-> Delegated CNAME -> A record
# a_alias -> a_cname -> a                   [inside zone.com]
##########################################################################################################

    @pytest.mark.run(order=168)
    def test_168_dig_alias_with_type_A(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type A from Grid:2")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid2_vip,"a_alias.zone.com","a","NOERROR","1.2.3.4","cname")

        display_message("\n***************. Test Case 168 Execution Completed .***************\n")


##########################################################################################################
# IBAlias (A) -> Delegated CNAME -> NOTHING
# a3_alias -> a2_cname -> dummy record
##########################################################################################################

    @pytest.mark.run(order=169)
    def test_169_dig_alias_with_type_A(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type A from Grid:2")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid2_vip,"a3_alias.zone.com","a","NOERROR","SOA","cname")

        display_message("\n***************. Test Case 169 Execution Completed .***************\n")


##########################################################################################################
# IBAlias (A)-> Delegated CNAME-> AAAA record
# a6_alias -> a4_cname -> aaaa
##########################################################################################################

    @pytest.mark.run(order=170)
    def test_170_dig_alias_with_type_A(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type A from Grid:2")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid2_vip,"a6_alias.zone.com","a","NOERROR","SOA","cname")

        display_message("\n***************. Test Case 170 Execution Completed .***************\n")


##########################################################################################################
# IBAlias (A)-> Delegated CNAME -> AAAA record AND A record with same name
# a7_alias -> a5_cname -> a_and_aaaa
##########################################################################################################

    @pytest.mark.run(order=171)
    def test_171_dig_alias_with_type_A(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type A from Grid:2")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid2_vip,"a7_alias.zone.com","a","NOERROR","1.2.3.4","1111:2222::34")

        display_message("\n***************. Test Case 171 Execution Completed .***************\n")



##########################################################################################################
# IBAlias (A)-> Delegated CNAME  A record AND another A record with same name
# a8_alias -> a6_cname -> a7_cname -> a2
##########################################################################################################

    @pytest.mark.run(order=172)
    def test_172_dig_alias_with_type_A(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type A from Grid:2")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid2_vip,"a8_alias.zone.com","a","NOERROR","1.2.3.4","cname")
        perform_dig_query_cname(config.grid2_vip,"a8_alias.zone.com","a","NOERROR","5.6.7.8","cname")

        display_message("\n***************. Test Case 172 Execution Completed .***************\n")



##########################################################################################################
# IBAlias (A)  TTL of 15 -> Delegated CNAME -> A record TTL 22
# a9_alias -> a10_alias -> a8_cname -> a_cname -> a
##########################################################################################################

    @pytest.mark.run(order=173)
    def test_173_Update_TTL_for_a_record(self):

        display_message("\n========================================================\n")
        display_message("Updating a record a.zone.com - setting ttl to 22")
        display_message("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="record:a?name=a.zone.com", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[0]['_ref']
        display_message(ref)

        data = {"name":"a.zone.com","ipv4addr":"1.2.3.4","ttl":22}
        response = ib_NIOS.wapi_request('PUT', ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        display_message(response)

        if response[0]==400 or response[0]==401 or response[0]==404:
            display_message("FAILURE: Update a record with ttl=22")
            assert False
        else:
            display_message("SUCCESS: Update a record with ttl=22")
            assert True

        display_message("\n***************. Test Case 173 Execution Completed .***************\n")



    @pytest.mark.run(order=174)
    def test_174_dig_alias_with_type_A(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type A from Grid:2")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid2_vip,"a9_alias.zone.com","a","NOERROR","a9_alias.zone.com.	15	IN	A	1.2.3.4","cname")

        display_message("\n***************. Test Case 174 Execution Completed .***************\n")


##########################################################################################################
# IBAlias (AAAA)-> Delegated AAAA record
# aaaa_alias.infoblox.com -> aaaa           [infoblox.com]
##########################################################################################################

    @pytest.mark.run(order=175)
    def test_175_dig_alias_with_type_AAAA(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type AAAA from Grid:2")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid2_vip,"aaaa_alias.zone.com","aaaa","NOERROR","1111:2222::34","cname")

        display_message("\n***************. Test Case 175 Execution Completed .***************\n")



##########################################################################################################
# IBAlias (AAAA)-> Delegated CNAME -> AAAA record
# aaaa_alias -> aaaa_cname -> aaaa         [zone.com]
##########################################################################################################

    @pytest.mark.run(order=176)
    def test_176_dig_alias_with_type_AAAA(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type AAAA from Grid:2")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid2_vip,"aaaa_alias.zone.com","aaaa","NOERROR","1111:2222::34","cname")

        display_message("\n***************. Test Case 176 Execution Completed .***************\n")


##########################################################################################################
# IBAlias (AAAA) -> Delegate CNAME -> NOTHING
# aaaa3_alias -> aaaa2_cname -> dummy record
##########################################################################################################

    @pytest.mark.run(order=177)
    def test_177_dig_alias_with_type_AAAA(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type AAAA from Grid:2")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid2_vip,"aaaa3_alias.zone.com","aaaa","NOERROR","SOA","cname")

        display_message("\n***************. Test Case 177 Execution Completed .***************\n")



##########################################################################################################
# IBAlias (AAAA)-> Delegated CNAME-> A record
# aaaa6_alias -> aaaa5_cname -> a
##########################################################################################################

    @pytest.mark.run(order=178)
    def test_178_dig_alias_with_type_AAAA(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type AAAA from Grid:2")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid2_vip,"aaaa6_alias.zone.com","aaaa","NOERROR","SOA","cname")

        display_message("\n***************. Test Case 178 Execution Completed .***************\n")


##########################################################################################################
# IBAlias (AAAA)-> Delegated CNAME -> AAAA record AND A record with same name
# aaaa7_alias -> aaaa6_cname -> a_and_aaaa
##########################################################################################################

    @pytest.mark.run(order=179)
    def test_179_dig_alias_with_type_AAAA(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type AAAA from Grid:2")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid2_vip,"aaaa6_alias.zone.com","aaaa","NOERROR","SOA","cname")

        display_message("\n***************. Test Case 179 Execution Completed .***************\n")


##########################################################################################################
# IBAlias (AAAA)-> Delegated CNAME  -> AAAA record AND another AAAA record with same name
# aaaa8_alias -> aaaa7_cname -> aaaa8_cname -> aaaa2.zone.com
##########################################################################################################

    @pytest.mark.run(order=180)
    def test_180_dig_alias_with_type_AAAA(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type AAAA from Grid:2")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid2_vip,"aaaa8_alias.zone.com","aaaa","NOERROR","1111:2222::34","cname")
        perform_dig_query_cname(config.grid2_vip,"aaaa8_alias.zone.com","aaaa","NOERROR","3333:4444::56","cname")

        display_message("\n***************. Test Case 180 Execution Completed .***************\n")


##########################################################################################################
# IBAlias (AAAA)-> Delegated CNAME  -> AAAA record AND another AAAA record with same name
# aaaa8_alias -> aaaa7_cname -> aaaa8_cname -> aaaa2.zone.com
##########################################################################################################

    @pytest.mark.run(order=181)
    def test_181_dig_alias_with_type_AAAA(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type AAAA from Grid:2")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid2_vip,"aaaa8_alias.zone.com","aaaa","NOERROR","1111:2222::34","cname")
        perform_dig_query_cname(config.grid2_vip,"aaaa8_alias.zone.com","aaaa","NOERROR","3333:4444::56","cname")

        display_message("\n***************. Test Case 181 Execution Completed .***************\n")


##########################################################################################################
# IBAlias (AAAA)  TTL of 15 Delegated CNAME   AAAA record TTL 22
# aaaa9_alias -> aaaa10_alias -> aaaa9_cname -> aaaa_cname -> aaaa
##########################################################################################################

    @pytest.mark.run(order=182)
    def test_182_Update_TTL_for_aaaa_record(self):

        display_message("\n========================================================\n")
        display_message("Updating aaaa record aaaa.zone.com - setting ttl to 22")
        display_message("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="record:aaaa?name=aaaa.zone.com", grid_vip=config.grid_vip)
        ref=json.loads(get_ref)[0]['_ref']
        display_message(ref)

        data = {"name":"aaaa.zone.com","ipv6addr":"1111:2222::34","ttl":22}
        response = ib_NIOS.wapi_request('PUT', ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        display_message(response)

        if response[0]==400 or response[0]==401 or response[0]==404:
            display_message("FAILURE: Update aaaa record with ttl=22")
            assert False
        else:
            display_message("SUCCESS: Update aaaa record with ttl=22")
            assert True

        display_message("\n***************. Test Case 182 Execution Completed .***************\n")



    @pytest.mark.run(order=183)
    def test_183_dig_alias_with_type_AAAA(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type AAAA from Grid:2")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid2_vip,"aaaa9_alias.zone.com","aaaa","NOERROR","aaaa9_alias.zone.com.	15	IN	AAAA	1111:2222::34","cname")


        display_message("\n***************. Test Case 183 Execution Completed .***************\n")


############################################################################################################################################
# IBAlias (A) -> Delegated DNAME -> A record
# a11_alias -> a_dname -> a
############################################################################################################################################

    @pytest.mark.run(order=184)
    def test_184_dig_alias_with_type_A(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type A from Grid:2")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid2_vip,"a11_alias.zone.com","a","NOERROR","1.2.3.4","dname")

        display_message("\n***************. Test Case 184 Execution Completed .***************\n")


############################################################################################################################################
# IBAlias (AAAA) -> Delegated DNAME -> AAAA record
# aaaa11_alias -> aaaa_dname -> aaaa
############################################################################################################################################

    @pytest.mark.run(order=185)
    def test_185_dig_alias_with_type_AAAA(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type AAAA from Grid:2")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid2_vip,"aaaa11_alias.zone.com","aaaa","NOERROR","1111:2222::34","dname")

        display_message("\n***************. Test Case 185 Execution Completed .***************\n")


############################################################################################################################################
# IBAlias (MX) -> Delegated DNAME -> MX record
# mx2_alias -> mx_dname -> mx
############################################################################################################################################

    @pytest.mark.run(order=186)
    def test_186_dig_alias_with_type_MX(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type MX from Grid:2")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid2_vip,"mx2_alias.zone.com","mx","NOERROR","myzone.com","dname")

        display_message("\n***************. Test Case 186 Execution Completed .***************\n")

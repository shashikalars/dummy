#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Vindya V K"
__email__  = "vvk@infoblox.com"

################################################################################
# Configuration - Grid master + Member
# Here we are automating all the Alias records and quering using CNAME records #
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
############################################################################################
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



class IB_Alias_Automation(unittest.TestCase):

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
        sleep(35)

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
    @pytest.mark.run(order=87)
    def test_087_Create_a_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - a4_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("a4_alias.zone.com","a5_alias.zone.com","A")

        display_message("\n***************. Test Case 87 Execution Completed .***************\n")


# Perform dig query for alias with type A
# Validate for NOERROR response and SOA
    @pytest.mark.run(order=88)
    def test_088_dig_alias_with_type_A(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type A from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"a4_alias.zone.com","a","NOERROR","SOA","cname")

        display_message("\n***************. Test Case 88 Execution Completed .***************\n")


############################################################################################################################################
# IBAlias (A)-> CNAME-> AAAA record   ;   No answer is returned because Alias is for AAAA record.
# a6_alias -> a4_cname -> aaaa
############################################################################################################################################

# Create type AAAA record inside zone.com - aaaa.zone.com
# Validate if aaaa.zone.com has been created
    @pytest.mark.run(order=89)
    def test_089_Create_aaaa_record(self):

        display_message("\n========================================================\n")
        display_message("Creating AAAA record - aaaa.zone.com")
        display_message("\n========================================================\n")

        data = {"ipv6addr": "1111:2222::34", "name": "aaaa.zone.com"}
        create_record_in_zone(data,"aaaa.zone.com","aaaa")

        display_message("\n***************. Test Case 89 Execution Completed .***************\n")


# Create type A cname record a4_cname inside zone.com
# set the target to aaaa.zone.com
# Validate if a4_cname.zone.com has been created
    @pytest.mark.run(order=90)
    def test_090_Create_a_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - a4_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("a4_cname.zone.com","aaaa.zone.com")

        display_message("\n***************. Test Case 90 Execution Completed .***************\n")


# Create type A alias record a6_alias inside zone.com
# set the target as a4_cname.zone.com
# Validate if a6_alias.zone.com has been created
    @pytest.mark.run(order=91)
    def test_091_Create_a_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - a6_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("a6_alias.zone.com","a4_cname.zone.com","A")

        display_message("\n***************. Test Case 91 Execution Completed .***************\n")


# Perform dig query for alias with type A
# Validate for NOERROR response and SOA
    @pytest.mark.run(order=92)
    def test_092_dig_alias_with_type_A(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type A from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"a6_alias.zone.com","a","NOERROR","SOA","cname")

        display_message("\n***************. Test Case 92 Execution Completed .***************\n")


############################################################################################################################################
# IBAlias (A)-> CNAME -> AAAA record AND A record with same name   ;   A record is returned but the AAAA record is not.
# a7_alias -> a5_cname -> a_and_aaaa        (create 2 records - A and AAAA with name a_and_aaaa)
############################################################################################################################################

# Create type A record inside zone.com - a_and_aaaa.zone.com
# Validate if a_and_aaaa.zone.com has been created
    @pytest.mark.run(order=93)
    def test_093_Create_a_record(self):

        display_message("\n========================================================\n")
        display_message("Creating A record - a_and_aaaa.zone.com")
        display_message("\n========================================================\n")

        data = {"ipv4addr": "1.2.3.4", "name": "a_and_aaaa.zone.com"}
        create_record_in_zone(data,"a_and_aaaa.zone.com","a")

        display_message("\n***************. Test Case 93 Execution Completed .***************\n")


# Create type AAAA record inside zone.com - a_and_aaaa.zone.com
# Validate if a_and_aaaa.zone.com has been created
    @pytest.mark.run(order=94)
    def test_094_Create_aaaa_record(self):

        display_message("\n========================================================\n")
        display_message("Creating AAAA record - a_and_aaaa.zone.com")
        display_message("\n========================================================\n")

        data = {"ipv6addr": "1111:2222::34", "name": "a_and_aaaa.zone.com"}
        create_record_in_zone(data,"a_and_aaaa.zone.com","aaaa")

        display_message("\n***************. Test Case 94 Execution Completed .***************\n")


# Create type A cname record a5_cname inside zone.com
# set the target to a_and_aaaa.zone.com
# Validate if a5_cname.zone.com has been created
    @pytest.mark.run(order=95)
    def test_095_Create_a_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - a5_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("a5_cname.zone.com","a_and_aaaa.zone.com")

        display_message("\n***************. Test Case 95 Execution Completed .***************\n")


# Create type A alias record a7_alias inside zone.com
# set the target as a5_cname.zone.com
# Validate if a7_alias.zone.com has been created
    @pytest.mark.run(order=96)
    def test_096_Create_a_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - a7_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("a7_alias.zone.com","a5_cname.zone.com","A")

        display_message("\n***************. Test Case 96 Execution Completed .***************\n")


# Perform dig query for alias with type A
# Validate for NOERROR response and 1.2.3.4
    @pytest.mark.run(order=97)
    def test_097_dig_alias_with_type_A(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type A from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"a7_alias.zone.com","a","NOERROR","1.2.3.4","1111:2222::34")

        display_message("\n***************. Test Case 97 Execution Completed .***************\n")


############################################################################################################################################
# IBAlias (A)-> CNAME  -> CNAME -> A record AND another A record with same  ;   Both A records are returned.
# a8_alias -> a6_cname -> a7_cname -> a2        (create 2 records - A and A with name a2)
############################################################################################################################################

# Create type A record inside zone.com - a2.zone.com
# Validate if a2.zone.com has been created
    @pytest.mark.run(order=98)
    def test_098_Create_a_record(self):

        display_message("\n========================================================\n")
        display_message("Creating A record - a2.zone.com")
        display_message("\n========================================================\n")

        data = {"ipv4addr": "1.2.3.4", "name": "a2.zone.com"}
        create_record_in_zone(data,"a2.zone.com","a")

        display_message("\n***************. Test Case 98 Execution Completed .***************\n")


# Create type A record inside zone.com - a2.zone.com
# Validate if a2.zone.com has been created
    @pytest.mark.run(order=99)
    def test_099_Create_a_record(self):

        display_message("\n========================================================\n")
        display_message("Creating A record - a2.zone.com")
        display_message("\n========================================================\n")

        data = {"ipv4addr": "5.6.7.8", "name": "a2.zone.com"}
        create_record_in_zone(data,"a2.zone.com","a")

        display_message("\n***************. Test Case 99 Execution Completed .***************\n")


# Create type A cname record a7_cname inside zone.com
# set the target to a2.zone.com
# Validate if a7_cname.zone.com has been created
    @pytest.mark.run(order=100)
    def test_100_Create_a_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - a7_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("a7_cname.zone.com","a2.zone.com")

        display_message("\n***************. Test Case 100 Execution Completed .***************\n")


# Create type A cname record a6_cname inside zone.com
# set the target to a7_cname.zone.com
# Validate if a6_cname.zone.com has been created
    @pytest.mark.run(order=101)
    def test_101_Create_a_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - a6_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("a6_cname.zone.com","a7_cname.zone.com")

        display_message("\n***************. Test Case 101 Execution Completed .***************\n")


# Create type A alias record a8_alias inside zone.com
# set the target as a6_cname.zone.com
# Validate if a8_alias.zone.com has been created
    @pytest.mark.run(order=102)
    def test_102_Create_a_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - a8_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("a8_alias.zone.com","a6_cname.zone.com","A")

        display_message("\n***************. Test Case 102 Execution Completed .***************\n")


# Perform dig query for alias with type A
# Validate for NOERROR response and 1.2.3.4
    @pytest.mark.run(order=103)
    def test_103_dig_alias_with_type_A(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type A from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"a8_alias.zone.com","a","NOERROR","1.2.3.4","cname")
        perform_dig_query_cname(config.grid_vip,"a8_alias.zone.com","a","NOERROR","5.6.7.8","cname")

        display_message("\n***************. Test Case 103 Execution Completed .***************\n")


############################################################################################################################################
# IBAlias (A)  TTL of 15 -> IBAlias (A) -> CNAME  -> CNAME -> A record  ;   TTL in the answer is 15 which is for the IBAlias record, not the A record
# a9_alias -> a10_alias -> a8_cname -> a_cname -> a
############################################################################################################################################

# Create type A cname record a8_cname inside zone.com
# set the target to a_cname.zone.com
# Validate if a8_cname.zone.com has been created
    @pytest.mark.run(order=104)
    def test_104_Create_a_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - a8_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("a8_cname.zone.com","a_cname.zone.com")

        display_message("\n***************. Test Case 104 Execution Completed .***************\n")


# Create type A alias record a10_alias inside zone.com
# set the target as a8_cname.zone.com
# Validate if a10_alias.zone.com has been created
    @pytest.mark.run(order=105)
    def test_105_Create_a_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - a10_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("a10_alias.zone.com","a8_cname.zone.com","A")

        display_message("\n***************. Test Case 105 Execution Completed .***************\n")


# Create type A alias record a9_alias inside zone.com
# Set ttl to 15 seconds
# set the target as a10_alias.zone.com
# Validate if a9_alias.zone.com has been created
    @pytest.mark.run(order=106)
    def test_106_Create_a_alias_record(self):

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

        display_message("\n***************. Test Case 106 Execution Completed .***************\n")


# Perform dig query for alias with type A
# Validate for NOERROR response and 1.2.3.4
    @pytest.mark.run(order=107)
    def test_107_dig_alias_with_type_A(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type A from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"a9_alias.zone.com","a","NOERROR","1.2.3.4","cname")

        display_message("\n***************. Test Case 107 Execution Completed .***************\n")



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
    @pytest.mark.run(order=108)
    def test_108_Create_aaaa_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - aaaa_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("aaaa_cname.zone.com","aaaa.zone.com")

        display_message("\n***************. Test Case 108 Execution Completed .***************\n")


# Create type AAAA alias record aaaa_alias inside zone.com
# set the target as aaaa_cname.zone.com
# Validate if aaaa_alias.zone.com has been created
    @pytest.mark.run(order=109)
    def test_109_Create_aaaa_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - aaaa_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("aaaa_alias.zone.com","aaaa_cname.zone.com","AAAA")

        display_message("\n***************. Test Case 109 Execution Completed .***************\n")


# Perform dig query for alias with type AAAA
# Validate for NOERROR response and 1111:2222::34
    @pytest.mark.run(order=110)
    def test_110_dig_alias_with_type_AAAA(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type AAAA from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"aaaa_alias.zone.com","aaaa","NOERROR","1111:2222::34","cname")

        display_message("\n***************. Test Case 110 Execution Completed .***************\n")


############################################################################################################################################
# IBAlias (AAAA) -> IBAlias (AAAA) -> CNAME  -> CNAME -> AAAA record   ;   AAAA record answered correctly. CNAME not included in answer.
# aaaa1_alias -> aaaa2_alias -> aaaa1_cname -> aaaa_cname -> aaaa
############################################################################################################################################


# Create type AAAA cname record aaaa1_cname inside zone.com
# set the target as aaaa_cname.zone.com
# Validate if aaaa1_cname.zone.com has been created
    @pytest.mark.run(order=111)
    def test_111_Create_aaaa_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - aaaa1_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("aaaa1_cname.zone.com","aaaa_cname.zone.com")

        display_message("\n***************. Test Case 111 Execution Completed .***************\n")


# Create type AAAA alias record aaaa2_alias inside zone.com
# set the target as aaaa1_cname.zone.com
# Validate if aaaa2_alias.zone.com has been created
    @pytest.mark.run(order=112)
    def test_112_Create_aaaa_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - aaaa2_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("aaaa2_alias.zone.com","aaaa1_cname.zone.com","AAAA")

        display_message("\n***************. Test Case 112 Execution Completed .***************\n")


# Create type AAAA alias record aaaa1_alias inside zone.com
# set the target as aaaa2_alias.zone.com
# Validate if aaaa1_alias.zone.com has been created
    @pytest.mark.run(order=113)
    def test_113_Create_aaaa_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - aaaa1_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("aaaa1_alias.zone.com","aaaa2_alias.zone.com","AAAA")

        display_message("\n***************. Test Case 113 Execution Completed .***************\n")


# Perform dig query for alias with type AAAA
# Validate for NOERROR response and 1111:2222::34
    @pytest.mark.run(order=114)
    def test_114_dig_alias_with_type_AAAA(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type AAAA from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"aaaa1_alias.zone.com","aaaa","NOERROR","1111:2222::34","cname")

        display_message("\n***************. Test Case 114 Execution Completed .***************\n")


############################################################################################################################################
# IBAlias (AAAA) -> CNAME -> NOTHING   ;   No answer is returned.
# aaaa3_alias -> aaaa2_cname -> dummy record
############################################################################################################################################

# Create type AAAA cname record aaaa2_cname inside zone.com
# set the target to a dummy record (dummy.zone.com)
# Validate if aaaa2_cname.zone.com has been created
    @pytest.mark.run(order=115)
    def test_115_Create_aaaa_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - aaaa2_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("aaaa2_cname.zone.com","dummy.zone.com")

        display_message("\n***************. Test Case 115 Execution Completed .***************\n")


# Create type AAAA alias record aaaa3_alias inside zone.com
# set the target as aaaa2_cname.zone.com
# Validate if aaaa3_alias.zone.com has been created
    @pytest.mark.run(order=116)
    def test_116_Create_aaaa_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - aaaa3_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("aaaa3_alias.zone.com","aaaa2_cname.zone.com","AAAA")

        display_message("\n***************. Test Case 116 Execution Completed .***************\n")


# Perform dig query for alias with type AAAA
# Validate for NOERROR response and SOA
    @pytest.mark.run(order=117)
    def test_117_dig_alias_with_type_AAAA(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type AAAA from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"aaaa3_alias.zone.com","aaaa","NOERROR","SOA","cname")

        display_message("\n***************. Test Case 117 Execution Completed .***************\n")


############################################################################################################################################
# IBAlias (AAAA) -> IBAlias (AAAA) -> CNAME  -> CNAME -> NOTHING   ;   No answer is returned.
# aaaa4_alias -> aaaa5_alias -> aaaa3_cname -> aaaa4_cname -> dummy record
############################################################################################################################################

# Create type AAAA cname record aaaa4_cname inside zone.com
# set the target to a dummy record (dummy.zone.com)
# Validate if aaaa4_cname.zone.com has been created
    @pytest.mark.run(order=118)
    def test_118_Create_aaaa_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - aaaa4_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("aaaa4_cname.zone.com","dummy.zone.com")

        display_message("\n***************. Test Case 118 Execution Completed .***************\n")


# Create type AAAA cname record aaaa3_cname inside zone.com
# set the target as aaaa4_cname.zone.com
# Validate if aaaa3_cname.zone.com has been created
    @pytest.mark.run(order=119)
    def test_119_Create_aaaa_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - aaaa3_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("aaaa3_cname.zone.com","aaaa4_cname.zone.com")

        display_message("\n***************. Test Case 119 Execution Completed .***************\n")


# Create type AAAA alias record aaaa5_alias inside zone.com
# set the target as aaaa3_cname.zone.com
# Validate if aaaa5_alias.zone.com has been created
    @pytest.mark.run(order=120)
    def test_120_Create_aaaa_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - aaaa5_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("aaaa5_alias.zone.com","aaaa3_cname.zone.com","AAAA")

        display_message("\n***************. Test Case 120 Execution Completed .***************\n")


# Create type AAAA alias record aaaa4_alias inside zone.com
# set the target as aaaa5_alias.zone.com
# Validate if aaaa4_alias.zone.com has been created
    @pytest.mark.run(order=121)
    def test_121_Create_aaaa_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - aaaa4_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("aaaa4_alias.zone.com","aaaa5_alias.zone.com","AAAA")

        display_message("\n***************. Test Case 121 Execution Completed .***************\n")


# Perform dig query for alias with type AAAA
# Validate for NOERROR response and SOA
    @pytest.mark.run(order=122)
    def test_122_dig_alias_with_type_AAAA(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type AAAA from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"aaaa4_alias.zone.com","aaaa","NOERROR","SOA","cname")

        display_message("\n***************. Test Case 122 Execution Completed .***************\n")


############################################################################################################################################
# IBAlias (AAAA)-> CNAME-> A record   ;   No answer is returned because Alias is for A record.
# aaaa6_alias -> aaaa5_cname -> a
############################################################################################################################################

# Create type AAAA cname record aaaa5_cname inside zone.com
# set the target as a.zone.com
# Validate if aaaa5_cname.zone.com has been created
    @pytest.mark.run(order=123)
    def test_123_Create_aaaa_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - aaaa5_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("aaaa5_cname.zone.com","a.zone.com")

        display_message("\n***************. Test Case 123 Execution Completed .***************\n")


# Create type AAAA alias record aaaa6_alias inside zone.com
# set the target as aaaa5_cname.zone.com
# Validate if aaaa6_alias.zone.com has been created
    @pytest.mark.run(order=124)
    def test_124_Create_aaaa_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - aaaa6_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("aaaa6_alias.zone.com","aaaa5_cname.zone.com","AAAA")

        display_message("\n***************. Test Case 124 Execution Completed .***************\n")


# Perform dig query for alias with type AAAA
# Validate for NOERROR response and SOA
    @pytest.mark.run(order=125)
    def test_125_dig_alias_with_type_AAAA(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type AAAA from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"aaaa6_alias.zone.com","aaaa","NOERROR","SOA","cname")

        display_message("\n***************. Test Case 125 Execution Completed .***************\n")


############################################################################################################################################
# IBAlias (AAAA)-> CNAME -> AAAA record AND A record with same name   ;   AAAA record is returned but A record is not.
# aaaa7_alias -> aaaa6_cname -> a_and_aaaa  (previously created)
############################################################################################################################################

# Create type AAAA cname record aaaa6_cname inside zone.com
# set the target as a_and_aaaa.zone.com
# Validate if aaaa6_cname.zone.com has been created
    @pytest.mark.run(order=126)
    def test_126_Create_aaaa_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - aaaa6_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("aaaa6_cname.zone.com","a_and_aaaa.zone.com")

        display_message("\n***************. Test Case 126 Execution Completed .***************\n")


# Create type AAAA alias record aaaa7_alias inside zone.com
# set the target as aaaa6_cname.zone.com
# Validate if aaaa7_alias.zone.com has been created
    @pytest.mark.run(order=127)
    def test_127_Create_aaaa_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - aaaa7_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("aaaa7_alias.zone.com","aaaa6_cname.zone.com","AAAA")

        display_message("\n***************. Test Case 127 Execution Completed .***************\n")


# Perform dig query for alias with type AAAA
# Validate for NOERROR response and 1111:2222::34
    @pytest.mark.run(order=128)
    def test_128_dig_alias_with_type_AAAA(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type AAAA from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"aaaa7_alias.zone.com","aaaa","NOERROR","1111:2222::34","1.2.3.4")

        display_message("\n***************. Test Case 128 Execution Completed .***************\n")


############################################################################################################################################
# IBAlias (AAAA)-> CNAME -> CNAME -> AAAA record AND another AAAA record with same name   ;  both AAAA records are returned
# aaaa8_alias -> aaaa7_cname -> aaaa8_cname -> aaaa2.zone.com  (2 AAAA reocrds with name aaaa2.zone.com)
# Open bug - NIOS-84042
############################################################################################################################################

# Create type AAAA record inside zone.com - aaaa2.zone.com
# Validate if aaaa2.zone.com has been created
    @pytest.mark.run(order=129)
    def test_129_Create_aaaa_record(self):

        display_message("\n========================================================\n")
        display_message("Creating AAAA record - aaaa2.zone.com")
        display_message("\n========================================================\n")

        data = {"ipv6addr": "1111:2222::34", "name": "aaaa2.zone.com"}
        create_record_in_zone(data,"aaaa2.zone.com","aaaa")

        display_message("\n***************. Test Case 129 Execution Completed .***************\n")


# Create type AAAA record inside zone.com - aaaa2.zone.com
# Validate if aaaa2.zone.com has been created
    @pytest.mark.run(order=130)
    def test_130_Create_aaaa_record(self):

        display_message("\n========================================================\n")
        display_message("Creating AAAA record - aaaa2.zone.com")
        display_message("\n========================================================\n")

        data = {"ipv6addr": "3333:4444::56", "name": "aaaa2.zone.com"}
        create_record_in_zone(data,"aaaa2.zone.com","aaaa")

        display_message("\n***************. Test Case 130 Execution Completed .***************\n")


# Create type AAAA cname record aaaa8_cname inside zone.com
# set the target as aaaa2.zone.com
# Validate if aaaa8_cname.zone.com has been created
    @pytest.mark.run(order=131)
    def test_131_Create_aaaa_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - aaaa8_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("aaaa8_cname.zone.com","aaaa2.zone.com")

        display_message("\n***************. Test Case 131 Execution Completed .***************\n")


# Create type AAAA cname record aaaa7_cname inside zone.com
# set the target as aaaa8_cname.zone.com
# Validate if aaaa7_cname.zone.com has been created
    @pytest.mark.run(order=132)
    def test_132_Create_aaaa_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - aaaa7_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("aaaa7_cname.zone.com","aaaa8_cname.zone.com")

        display_message("\n***************. Test Case 132 Execution Completed .***************\n")


# Create type AAAA alias record aaaa8_alias inside zone.com
# set the target as aaaa7_cname.zone.com
# Validate if aaaa8_alias.zone.com has been created
    @pytest.mark.run(order=133)
    def test_133_Create_aaaa_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - aaaa8_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("aaaa8_alias.zone.com","aaaa7_cname.zone.com","AAAA")

        display_message("\n***************. Test Case 133 Execution Completed .***************\n")


# Perform dig query for alias with type AAAA
# Validate for NOERROR response and 1111:2222::34 and 3333:4444::56
    @pytest.mark.run(order=134)
    def test_134_dig_alias_with_type_AAAA(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type AAAA from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"aaaa8_alias.zone.com","aaaa","NOERROR","1111:2222::34","cname")
        perform_dig_query_cname(config.grid_vip,"aaaa8_alias.zone.com","aaaa","NOERROR","3333:4444::56","cname")

        display_message("\n***************. Test Case 134 Execution Completed .***************\n")


############################################################################################################################################
# IBAlias (AAAA)  TTL of 15 -> IBAlias (AAAA) -> CNAME  -> CNAME -> AAAA record   ;  TTL in the answer is 15 for the IBAlias record, not the AAAA record
# aaaa9_alias -> aaaa10_alias -> aaaa9_cname -> aaaa_cname -> aaaa
############################################################################################################################################

# Create type AAAA cname record aaaa9_cname inside zone.com
# set the target as aaaa_cname.zone.com
# Validate if aaaa9_cname.zone.com has been created
    @pytest.mark.run(order=135)
    def test_135_Create_aaaa_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - aaaa9_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("aaaa9_cname.zone.com","aaaa_cname.zone.com")

        display_message("\n***************. Test Case 135 Execution Completed .***************\n")


# Create type AAAA alias record aaaa10_alias inside zone.com
# set the target as aaaa9_cname.zone.com
# Validate if aaaa10_alias.zone.com has been created
    @pytest.mark.run(order=136)
    def test_136_Create_aaaa_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - aaaa10_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("aaaa10_alias.zone.com","aaaa9_cname.zone.com","AAAA")

        display_message("\n***************. Test Case 136 Execution Completed .***************\n")


# Create type AAAA alias record aaaa9_alias inside zone.com
# set the target as aaaa10_alias.zone.com
# Validate if aaaa9_alias.zone.com has been created
    @pytest.mark.run(order=137)
    def test_137_Create_aaaa_alias_record(self):

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

        display_message("\n***************. Test Case 137 Execution Completed .***************\n")


# Perform dig query for alias with type AAAA
# Validate for NOERROR response and 1111:2222::34
    @pytest.mark.run(order=138)
    def test_138_dig_alias_with_type_AAAA(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type AAAA from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"aaaa9_alias.zone.com","aaaa","NOERROR","1111:2222::34","cname")

        display_message("\n***************. Test Case 138 Execution Completed .***************\n")


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
    @pytest.mark.run(order=139)
    def test_139_Create_mx_record(self):

        display_message("\n========================================================\n")
        display_message("Creating MX record - mx.zone.com")
        display_message("\n========================================================\n")

        data = {"mail_exchanger": "myzone.com","name": "mx.zone.com","preference": 10}
        create_record_in_zone(data,"mx.zone.com","mx")

        display_message("\n***************. Test Case 139 Execution Completed .***************\n")


# Create type MX cname record mx_cname inside zone.com
# set the target as mx.zone.com
# Validate if mx_cname.zone.com has been created
    @pytest.mark.run(order=140)
    def test_140_Create_mx_cname_record(self):

        display_message("\n========================================================\n")
        display_message("Creating cname record - mx_cname.zone.com")
        display_message("\n========================================================\n")

        create_cname_record("mx_cname.zone.com","mx.zone.com")

        display_message("\n***************. Test Case 140 Execution Completed .***************\n")


# Create type MX alias record mx_alias inside zone.com
# set the target as mx_cname.zone.com
# Validate if mx_alias.zone.com has been created
    @pytest.mark.run(order=141)
    def test_141_Create_mx_alias_record(self):

        display_message("\n========================================================\n")
        display_message("Creating alias record - mx_alias.zone.com")
        display_message("\n========================================================\n")

        create_alias_record("mx_alias.zone.com","mx_cname.zone.com","MX")

        display_message("\n***************. Test Case 141 Execution Completed .***************\n")


# Perform dig query for alias with type MX
# Validate for NOERROR response and 'myzone.com'
    @pytest.mark.run(order=142)
    def test_142_dig_alias_with_type_MX(self):

        display_message("\n========================================================\n")
        display_message("Performing dig query for alias record with type MX from Master")
        display_message("\n========================================================\n")

        perform_dig_query_cname(config.grid_vip,"mx_alias.zone.com","mx","NOERROR","myzone.com","cname")

        display_message("\n***************. Test Case 142 Execution Completed .***************\n")



############################################################################################################################################
# import zone not supported, perform negative validation
# Update zone.com - import from ip 10.35.173.12
############################################################################################################################################

    @pytest.mark.run(order=143)
    def test_143_Performing_import_zone(self):

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

        display_message("\n***************. Test Case 143 Execution Completed .***************\n")


############################################################################################################################################
# run dig query axfr and make sure the ALIAS records are not in the list
# dig @<master.ip> zone.com axfr
############################################################################################################################################

# Perform dig query for zone.com with axfr
# Validate for NOERROR response and ALIAS records not present in the list
    @pytest.mark.run(order=144)
    def test_144_dig_zone_with_axfr(self):

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

        display_message("\n***************. Test Case 144 Execution Completed .***************\n")


############################################################################################################################################
# perform copy operation to a zone in another view
# Create a new view - vvk view
# Create a new auth zone - vvk.com
# Copy all the records from zone.com to vvk.com
############################################################################################################################################


    @pytest.mark.run(order=145)
    def test_145_Create_dns_view(self):

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

        display_message("\n***************. Test Case 145 Execution Completed .***************\n") # requires restart


    @pytest.mark.run(order=146)
    def test_146_Create_auth_zone(self):

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

        display_message("\n***************. Test Case 146 Execution Completed .***************\n") # requires restart


# Restart services
    @pytest.mark.run(order=147)
    def test_147_Restart_services(self):

        display_message("\n========================================================\n")
        display_message("Restarting Services")
        display_message("\n========================================================\n")

        grid = ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(35)

        display_message("\n***************. Test Case 147 Execution Completed .***************\n")



    @pytest.mark.run(order=148)
    def test_148_Copy_records_from_old_zone(self):

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


        display_message("\n***************. Test Case 148 Execution Completed .***************\n")


#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Chetan Kumar PG"
__email__  = "cpg@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. SA Grid Master                                                        #
#  2. Licenses : DNS(enabled), DHCP, Grid                                   #
#############################################################################

import os
import re
import config
import pytest
import unittest
import logging
import json
import pexpect
import paramiko
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as ib_TOKEN
#from ib_utils.log_capture import log_action as log
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="rfe_10324.log" ,level=logging.DEBUG,filemode='w')

### Global variable
global grid2_fqdn
grid2_fqdn = "ib-"+'-'.join(config.grid2_vip.split('.'))+".infoblox.com"
   
def restart_services(grid=config.grid_vip):
    """
    Restart Services
    """
    display_msg("Restart services")
    get_ref =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=grid)
    ref = json.loads(get_ref)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices", fields=json.dumps(data),grid_vip=grid)
    sleep(30)

def add_TLSA(name, certificate_usage, certificate_data, grid = config.grid_vip):
    """
    name               : Name of the TLSA record.
    certificate_usage  : Valid integer values = 0-PKIX-TA, 1-PKIX-EE, 2-DANE-TA, 3-DANE-EE.
    certificate_data   : Certificate data that must be matched for authentication.
    """
    data = {"name":name,
            "certificate_usage":certificate_usage,
            "certificate_data":certificate_data,
            "matched_type":0,
            "selector":0
            }
    response = ib_NIOS.wapi_request('POST',object_type='record:tlsa',fields=json.dumps(data),grid_vip=grid)
    display_msg(response)
    if type(response) == tuple:
        if response[0]==400 or response[0]==401:
            display_msg("Failure: Add TLSA record")
            assert False
    restart_services()

def sign_zone(zone, sign=True, grid=config.grid_vip):
    """
    zone : Name of the zone
    sign : Bool [True, False]
    Signs or Unsigns a zone based on the input.
    """
    operation = "SIGN"
    if not sign:
        operation = "UNSIGN"
    display_msg(operation+" Zone")
    get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth')
    for ref in json.loads(get_ref):
        if zone in ref['_ref']:
            response = ib_NIOS.wapi_request('POST', ref=ref['_ref'], params='?_function=dnssec_operation', fields=json.dumps({"operation":operation}),grid_vip=grid)
            #display_msg(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    display_msg("Failure: Sign/Unsign Zone")
                    assert False
            restart_services()
            return
    display_msg("Failure: Zone not found")
            
def delete_all_records_TLSA(grid=config.grid_vip):
    """
    Deletes TLSA records froms all the zones
    """
    display_msg("Delete TLSA records")
    get_ref = ib_NIOS.wapi_request('GET', object_type='record:tlsa',grid_vip=grid)
    for ref in json.loads(get_ref):
        response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'],grid_vip=grid)
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Delete TLSA record")
                assert False
        restart_services()

def validate_log(logfile, lookfor):
    """
    Validate captured log
    """
    display_msg("Validate captured log")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(config.grid_vip, username='root', pkey = mykey)
    display_msg("cat "+logfile+" | grep -i '"+lookfor+"'")
    stdin, stdout, stderr = client.exec_command("cat "+logfile+" | grep -i '"+lookfor+"'")
    result=stdout.read()
    display_msg(result)
    client.close()
    if result:
        return True
    return False

def display_msg(x=""):
    """ 
    Additional function.
    """
    logging.info(x)
    print(x)

class RFE_10324(unittest.TestCase):
    
    @pytest.mark.run(order=1)
    def test_000_setup(self):
        """
        setup method: Used for configuring pre-required configs.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case setup Started            |")
        display_msg("------------------------------------------------")
        
        '''Enable DNS service'''
        display_msg("Enable DNS service")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns')
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps({"enable_dns":True}))
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    display_msg("Failure: ENable DNS Service")
                    assert False
            restart_services()
        
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns', grid_vip=config.grid2_vip)
        display_msg(get_ref)
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps({"enable_dns":True}), grid_vip=config.grid2_vip)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: ENable DNS Service")
                assert False
        restart_services(config.grid2_vip)
        
        '''Create Authoritative FMZ'''
        display_msg("Create an Authoritative FMZ unsigned")
        data = {"fqdn": "rfe_10324.com",
                "view":"default",
                "grid_primary": [{"name": config.grid_fqdn,"stealth": False}],
                "grid_secondaries": [{"name":config.grid_member1_fqdn}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Create Authorative FMZ")
                assert False
        restart_services()
        
        display_msg("Create second Authorative FMZ unsigned")
        data = {"fqdn": "rfe_10324_second.com",
                "view":"default",
                "grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Create Authorative FMZ")
                assert False
        restart_services()
        
        display_msg("Create an Authorative sub zone unsigned")
        data = {"fqdn": "sub.rfe_10324.com",
                "view":"default",
                "grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Create Authorative FMZ")
                assert False    
        restart_services()
        
        display_msg("Create an Authorative FMZ signed")
        data = {"fqdn": "rfe_10324_signed.com",
                "view":"default",
                "grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Create Authorative FMZ")
                assert False
        restart_services()
        
        sign_zone(zone="rfe_10324_signed.com")
        
        display_msg("Create second Authorative FMZ signed")
        data = {"fqdn": "rfe_10324_signed_second.com",
                "view":"default",
                "grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Create Authorative FMZ")
                assert False
        restart_services()
        
        sign_zone(zone="rfe_10324_signed_second.com")
        
        '''Enable zone transfer'''
        display_msg("Enable Zone transfer")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns')
        display_msg(get_ref)
        data = {"allow_transfer":[{"_struct": "addressac","address":"Any", "permission":"ALLOW"}]}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Enable Zone transfer")
                assert False
        restart_services()
        
        display_msg("Enable Zone transfer on the remote server")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns', grid_vip=config.grid2_vip)
        display_msg(get_ref)
        data = {"allow_transfer":[{"_struct": "addressac","address":"Any", "permission":"ALLOW"}]}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data), grid_vip=config.grid2_vip)
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Enable Zone transfer")
                assert False
        restart_services(config.grid2_vip)
        
        '''Enable updates'''
        display_msg("Enable Updates")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns')
        display_msg(get_ref)
        data = {"allow_update":[{"_struct": "addressac","address":"Any", "permission":"ALLOW"}]}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Enable Zone transfer")
                assert False
        restart_services()
        
        display_msg("Enable updates on the remote server")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns', grid_vip=config.grid2_vip)
        display_msg(get_ref)
        data = {"allow_update":[{"_struct": "addressac","address":"Any", "permission":"ALLOW"}]}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data), grid_vip=config.grid2_vip)
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Enable Zone transfer")
                assert False
        restart_services(config.grid2_vip)
        
        '''Create two zones in remote server'''
        global grid2_fqdn
        display_msg("Create an Authorative FMZ rfe_10324.com in remote server")
        data = {"fqdn": "rfe_10324.com",
                "view":"default",
                "grid_primary": [{"name": grid2_fqdn,"stealth": False}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data),grid_vip=config.grid2_vip)
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Create Authorative FMZ rfe_10324.com in remote server")
                assert False
        restart_services(config.grid2_vip)
        
        display_msg("Create an Authorative FMZ rfe_10324_signed.com in remote server")
        data = {"fqdn": "rfe_10324_signed.com",
                "view":"default",
                "grid_primary": [{"name": grid2_fqdn,"stealth": False}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data),grid_vip=config.grid2_vip)
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Create Authorative FMZ in rfe_10324_signed.com remote server")
                assert False
        restart_services(config.grid2_vip)
        
        display_msg("---------Test Case setup Execution Completed----------")
    
    @pytest.mark.run(order=2)
    def test_001_Add_modify_delete_TLSA_record_PKIX_TA(self):
        """
        Add/Modify/Delete TLSA record in the unsigned zone.
        Certificate Usage : PKIX-TA
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 1 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add TLSA record in the unsigned zone")
        add_TLSA("_443._tcp.tlsa_1.rfe_10324.com", 0, "AA")
        
        display_msg("Modify TLSA record in the unsigned zone")
        get_ref = ib_NIOS.wapi_request('GET', object_type='record:tlsa')
        display_msg(get_ref)
        data = {"name":"_443._tcp.tlsa_1_1.rfe_10324.com"}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Modify TLSA record name")
                assert False
        
        delete_all_records_TLSA()
        
        display_msg("-----------Test Case 1 Execution Completed------------")

    @pytest.mark.run(order=3)
    def test_002_Add_modify_delete_TLSA_record_PKIX_EE(self):
        """
        Add/Modify/Delete TLSA record in the unsigned zone.
        Certificate Usage : PKIX-EE
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 2 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add TLSA record in the unsigned zone")
        add_TLSA("_443._tcp.tlsa_2.rfe_10324.com", 1, "AA")
        
        display_msg("Modify TLSA record in the unsigned zone")
        get_ref = ib_NIOS.wapi_request('GET', object_type='record:tlsa')
        display_msg(get_ref)
        data = {"name":"_443._tcp.tlsa_2_2.rfe_10324.com"}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Modify TLSA record name")
                assert False
        
        delete_all_records_TLSA()
        
        display_msg("-----------Test Case 2 Execution Completed------------")

    @pytest.mark.run(order=4)
    def test_003_Add_modify_delete_TLSA_record_DANE_TA(self):
        """
        Add/Modify/Delete TLSA record in the unsigned zone.
        Certificate Usage : DANE-TA
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 3 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add TLSA record in the unsigned zone")
        add_TLSA("_443._tcp.tlsa_3.rfe_10324.com", 2, "AA")
        
        display_msg("Modify TLSA record in the unsigned zone")
        get_ref = ib_NIOS.wapi_request('GET', object_type='record:tlsa')
        display_msg(get_ref)
        data = {"name":"_443._tcp.tlsa_3_3.rfe_10324.com"}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Modify TLSA record name")
                assert False
        
        delete_all_records_TLSA()
        
        display_msg("-----------Test Case 3 Execution Completed------------")

    @pytest.mark.run(order=5)
    def test_004_Add_modify_delete_TLSA_record_DANE_EE(self):
        """
        Add/Modify/Delete TLSA record in the unsigned zone.
        Certificate Usage : DANE-EE
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 4 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add TLSA record in the unsigned zone")
        add_TLSA("_443._tcp.tlsa_4.rfe_10324.com", 3, "AA")
        
        display_msg("Modify TLSA record in the unsigned zone")
        get_ref = ib_NIOS.wapi_request('GET', object_type='record:tlsa')
        display_msg(get_ref)
        data = {"name":"_443._tcp.tlsa_4_4.rfe_10324.com"}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Modify TLSA record name")
                assert False
        
        delete_all_records_TLSA()
        
        display_msg("-----------Test Case 4 Execution Completed------------")

    @pytest.mark.run(order=6)
    def test_005_Perform_dig_query_for_TLSA_record(self):
        """
        Perform dig query for TLSA record in the unsigned zone.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 5 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add TLSA record in the unsigned zone")
        add_TLSA("_443._tcp.tlsa_dig.rfe_10324.com", 0, "AA")
        
        output = os.popen("dig @"+config.grid_vip+" rfe_10324.com axfr").read()
        display_msg(output)
        
        display_msg("Perform dig query for the added TLSA record")
        output = os.popen("dig @"+config.grid_vip+" _443._tcp.tlsa_dig.rfe_10324.com IN TLSA").read()
        output = output.split('\n')
        answer = False
        pattern = False
        for line in output:
            display_msg(line)
        for line in output:
            if answer:
                match = re.match("_443._tcp.tlsa_dig.rfe_10324.com.\s+\d+\s+IN TLSA", line)
                if match:
                    pattern = True
                    break
            display_msg(line)
            if 'ANSWER SECTION' in line:
                answer = True
        if not answer or not pattern:
            display_msg("Failure: Perform dig query")
            assert False
        
        delete_all_records_TLSA()
        
        display_msg("-----------Test Case 5 Execution Completed------------")

    @pytest.mark.run(order=7)
    def test_006_Perform_dig_query_for_TLSA_record_member(self):
        """
        Perform dig query for TLSA record in the unsigned zone from grid secondary.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 6 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add TLSA record in the unsigned zone")
        add_TLSA("_443._tcp.tlsa_dig.rfe_10324.com", 0, "AA")
        
        output = os.popen("dig @"+config.grid_vip+" rfe_10324.com axfr").read()
        display_msg(output)
        
        display_msg("Perform dig query for the added TLSA record")
        output = os.popen("dig @"+config.grid_member1_vip+" _443._tcp.tlsa_dig.rfe_10324.com IN TLSA").read()
        output = output.split('\n')
        answer = False
        pattern = False
        for line in output:
            display_msg(line)
        for line in output:
            if answer:
                match = re.match("_443._tcp.tlsa_dig.rfe_10324.com.\s+\d+\s+IN TLSA", line)
                if match:
                    pattern = True
                    break
            display_msg(line)
            if 'ANSWER SECTION' in line:
                answer = True
        if not answer or not pattern:
            display_msg("Failure: Perform dig query")
            assert False
        
        delete_all_records_TLSA()
        
        display_msg("-----------Test Case 6 Execution Completed------------")

    @pytest.mark.run(order=8)
    def test_007_Add_modify_delete_TLSA_record_PKIX_TA_sub_zone(self):
        """
        Add/Modify/Delete TLSA record in the unsigned sub zone.
        Certificate Usage : PKIX-TA
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 7 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add TLSA record in the unsigned sub zone")
        add_TLSA("_443._tcp.tlsa_1.sub.rfe_10324.com", 0, "AA")
        
        display_msg("Modify TLSA record in the unsigned sub zone")
        get_ref = ib_NIOS.wapi_request('GET', object_type='record:tlsa')
        display_msg(get_ref)
        data = {"name":"_443._tcp.tlsa_1_1.sub.rfe_10324.com"}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Modify TLSA record name")
                assert False
        
        delete_all_records_TLSA()
        
        display_msg("-----------Test Case 7 Execution Completed------------")

    @pytest.mark.run(order=9)
    def test_008_Add_modify_delete_TLSA_record_PKIX_EE_sub_zone(self):
        """
        Add/Modify/Delete TLSA record in the unsigned sub zone.
        Certificate Usage : PKIX-EE
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 8 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add TLSA record in the unsigned sub zone")
        add_TLSA("_443._tcp.tlsa_2.sub.rfe_10324.com", 1, "AA")
        
        display_msg("Modify TLSA record in the unsigned sub zone")
        get_ref = ib_NIOS.wapi_request('GET', object_type='record:tlsa')
        display_msg(get_ref)
        data = {"name":"_443._tcp.tlsa_2_2.sub.rfe_10324.com"}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Modify TLSA record name")
                assert False
        
        delete_all_records_TLSA()
        
        display_msg("-----------Test Case 8 Execution Completed------------")

    @pytest.mark.run(order=10)
    def test_009_Add_modify_delete_TLSA_record_DANE_TA_sub_zone(self):
        """
        Add/Modify/Delete TLSA record in the unsigned sub zone.
        Certificate Usage : DANE-TA
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 9 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add TLSA record in the unsigned sub zone")
        add_TLSA("_443._tcp.tlsa_3.sub.rfe_10324.com", 2, "AA")
        
        display_msg("Modify TLSA record in the unsigned sub zone")
        get_ref = ib_NIOS.wapi_request('GET', object_type='record:tlsa')
        display_msg(get_ref)
        data = {"name":"_443._tcp.tlsa_3_3.sub.rfe_10324.com"}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Modify TLSA record name")
                assert False
        
        delete_all_records_TLSA()
        
        display_msg("-----------Test Case 9 Execution Completed------------")

    @pytest.mark.run(order=11)
    def test_010_Add_modify_delete_TLSA_record_DANE_EE_sub_zone(self):
        """
        Add/Modify/Delete TLSA record in the unsigned sub zone.
        Certificate Usage : DANE-EE
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 10 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add TLSA record in the unsigned sub zone")
        add_TLSA("_443._tcp.tlsa_4.sub.rfe_10324.com", 3, "AA")
        
        display_msg("Modify TLSA record in the unsigned sub zone")
        get_ref = ib_NIOS.wapi_request('GET', object_type='record:tlsa')
        display_msg(get_ref)
        data = {"name":"_443._tcp.tlsa_4_4.sub.rfe_10324.com"}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Modify TLSA record name")
                assert False
        
        delete_all_records_TLSA()
        
        display_msg("-----------Test Case 10 Execution Completed------------")

    @pytest.mark.run(order=12)
    def test_011_Perform_dig_query_for_TLSA_record(self):
        """
        Perform dig query for TLSA record in the unsigned zone.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 11 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add TLSA record in the unsigned zone")
        add_TLSA("_443._tcp.tlsa_dig.sub.rfe_10324.com", 0, "AA")
        
        output = os.popen("dig @"+config.grid_vip+" sub.rfe_10324.com axfr").read()
        display_msg(output)
        
        display_msg("Perform dig query for the added TLSA record")
        output = os.popen("dig @"+config.grid_vip+" _443._tcp.tlsa_dig.sub.rfe_10324.com IN TLSA").read()
        output = output.split('\n')
        answer = False
        pattern = False
        for line in output:
            display_msg(line)
        for line in output:
            if answer:
                match = re.match("_443._tcp.tlsa_dig.sub.rfe_10324.com.\s+\d+\s+IN TLSA", line)
                if match:
                    pattern = True
                    break
            if 'ANSWER SECTION' in line:
                answer = True
        if not answer or not pattern:
            display_msg("Failure: Perform dig query")
            assert False
        
        delete_all_records_TLSA()
        
        display_msg("-----------Test Case 11 Execution Completed-----------")

    @pytest.mark.run(order=13)
    def test_012_Schedule_add_modify_delete_TLSA_record_DANE_EE(self):
        """
        Add/Modify/Delete TLSA record in the unsigned zone.
        Certificate Usage : DANE-EE
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 12 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Schedule add TLSA record in the unsigned zone")
        add_TLSA("_443._tcp.tlsa_5.rfe_10324.com", 3, "AA")
        
        display_msg("Schedule modify TLSA record in the unsigned zone")
        get_ref = ib_NIOS.wapi_request('GET', object_type='record:tlsa')
        display_msg(get_ref)
        data = {"name":"_443._tcp.tlsa_5_5.sub.rfe_10324.com"}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Modify TLSA record name")
                assert False
        
        display_msg("Schedule delete TLSA record in the unsigned zone")
        get_ref = ib_NIOS.wapi_request('GET', object_type='record:tlsa')
        display_msg(get_ref)
        response = ib_NIOS.wapi_request('DELETE',ref=json.loads(get_ref)[0]['_ref'])
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Delete TLSA record")
                assert False
        
        display_msg("-----------Test Case 12 Execution Completed-----------")

    @pytest.mark.run(order=14)
    def test_013_Perform_dig_query_for_TLSA_record_with_punycode(self):
        """
        Perform dig query for TLSA record with punycode in the unsigned zone.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 13 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add TLSA record in the unsigned zone")
        add_TLSA("_443._tcp.ಚೇತನ್.rfe_10324.com", 0, "AA")
        
        output = os.popen("dig @"+config.grid_vip+" rfe_10324.com axfr").read()
        display_msg(output)
        
        display_msg("Perform dig query for the added TLSA record")
        output = os.popen("dig @"+config.grid_vip+" _443._tcp.xn--sscum6j6a.rfe_10324.com IN TLSA").read()
        output = output.split('\n')
        answer = False
        pattern = False
        for line in output:
            display_msg(line)
        for line in output:
            if answer:
                match = re.match("_443._tcp.ಚೇತನ್.rfe_10324.com.\s+\d+\s+IN TLSA", line)
                if match:
                    pattern = True
                    break
            if 'ANSWER SECTION' in line:
                answer = True
        if not answer or not pattern:
            display_msg("Failure: Perform dig query")
            assert False

        delete_all_records_TLSA()
        
        display_msg("-----------Test Case 13 Execution Completed-----------")

    @pytest.mark.run(order=15)
    def test_014_Add_TLSA_record_through_unknown_record(self):
        """
        Add TLSA record through unknown record in the unsigned zone.
        Should not be able to add.
        
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 14 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add TLSA record through unknown record in the unsigned zone")
        data = {"name": "tlsa_unknown.rfe_10324.com",
                "record_type": "TLSA",
                "subfield_values": [{"field_type": "T",
                                    "field_value": "unknown record",
                                    "include_length": "NONE"}]}
        response = ib_NIOS.wapi_request('POST', object_type='record:unknown', fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                if "Record type already supported by NIOS cannot be created" in response[1]:
                    pass
                else:
                    assert False
            else:
                assert False
        else:
            display_msg("Failure: Able to add TLSA record through unknown record")
            assert False
        
        display_msg("-----------Test Case 14 Execution Completed-----------")

    @pytest.mark.run(order=16)
    def test_015_Copy_TLSA_record_signed_to_unsigned(self):
        """
        Copy TLSA record from signed zone to unsigned zone.
        
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 15 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Copy TLSA record from signed zone to unsigned zone")
        add_TLSA("_443._tcp.tlsa_signed.rfe_10324_signed.com", 0, "AA")
        source_zone_ref = ''
        destination_zone_ref = ''
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth')
        for ref in json.loads(get_ref):
            if  "rfe_10324_signed.com" in ref['_ref']:
                source_zone_ref = ref['_ref']
            if "rfe_10324.com" in ref['_ref']:
                destination_zone_ref = ref['_ref']
        data = {"clear_destination_first":False, 
                "destination_zone":destination_zone_ref, 
                "replace_existing_records":False, 
                "select_records":["TLSA"]}
        response = ib_NIOS.wapi_request('POST', object_type=source_zone_ref, params='?_function=copyzonerecords', fields=json.dumps(data))
        display_msg(response)
        delete_all_records_TLSA()
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Copy TLSA record from signed zone to unsigned zone")
                assert False
        
        display_msg("-----------Test Case 15 Execution Completed-----------")

    @pytest.mark.run(order=17)
    def test_016_Copy_TLSA_record_unsigned_to_signed(self):
        """
        Copy TLSA record from unsigned zone to signed zone.
        
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 16 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Copy TLSA record from unsigned zone to signed zone")
        add_TLSA("_443._tcp.tlsa_unsigned.rfe_10324.com", 0, "AA")
        source_zone_ref = ''
        destination_zone_ref = ''
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth')
        for ref in json.loads(get_ref):
            if  "rfe_10324.com" in ref['_ref']:
                source_zone_ref = ref['_ref']
            if "rfe_10324_signed.com" in ref['_ref']:
                destination_zone_ref = ref['_ref']
        data = {"clear_destination_first":False, 
                "destination_zone":destination_zone_ref, 
                "replace_existing_records":False, 
                "select_records":["TLSA"]}
        response = ib_NIOS.wapi_request('POST', object_type=source_zone_ref, params='?_function=copyzonerecords', fields=json.dumps(data))
        display_msg(response)
        delete_all_records_TLSA()
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Copy TLSA record from unsigned zone to signed zone")
                assert False
        
        display_msg("-----------Test Case 16 Execution Completed-----------")

    @pytest.mark.run(order=18)
    def test_017_Copy_TLSA_record_signed_to_signed(self):
        """
        Copy TLSA record from signed zone to signed zone.
        
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 17 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Copy TLSA record from signed zone to signed zone")
        add_TLSA("_443._tcp.tlsa_signed.rfe_10324.com", 0, "AA")
        source_zone_ref = ''
        destination_zone_ref = ''
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth')
        for ref in json.loads(get_ref):
            if  "rfe_10324.com" in ref['_ref']:
                source_zone_ref = ref['_ref']
            if "rfe_10324_signed.com" in ref['_ref']:
                destination_zone_ref = ref['_ref']
        data = {"clear_destination_first":False, 
                "destination_zone":destination_zone_ref, 
                "replace_existing_records":False, 
                "select_records":["TLSA"]}
        response = ib_NIOS.wapi_request('POST', object_type=source_zone_ref, params='?_function=copyzonerecords', fields=json.dumps(data))
        display_msg(response)
        delete_all_records_TLSA()
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Copy TLSA record from signed zone to signed zone")
                assert False
        
        display_msg("-----------Test Case 17 Execution Completed-----------")

    @pytest.mark.run(order=19)
    def test_018_Copy_TLSA_record_unsigned_to_unsigned(self):
        """
        Copy TLSA record from unsigned zone to unsigned zone.
        
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 18 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Copy TLSA record from unsigned zone to unsigned zone")
        add_TLSA("_443._tcp.tlsa_unsigned.rfe_10324_second.com", 0, "AA")
        source_zone_ref = ''
        destination_zone_ref = ''
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth')
        for ref in json.loads(get_ref):
            if  "rfe_10324.com" in ref['_ref']:
                source_zone_ref = ref['_ref']
            if "rfe_10324_second.com" in ref['_ref']:
                destination_zone_ref = ref['_ref']
        data = {"clear_destination_first":False, 
                "destination_zone":destination_zone_ref, 
                "replace_existing_records":False, 
                "select_records":["TLSA"]}
        response = ib_NIOS.wapi_request('POST', object_type=source_zone_ref, params='?_function=copyzonerecords', fields=json.dumps(data))
        display_msg(response)
        delete_all_records_TLSA()
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Copy TLSA record from unsigned zone to unsigned zone")
                assert False
        
        display_msg("-----------Test Case 18 Execution Completed-----------")

    @pytest.mark.run(order=20)
    def test_019_Import_TLSA_record_signed_to_unsigned(self):
        """
        Import TLSA record from signed zone to unsigned zone.
        
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 19 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Import TLSA record from signed zone to unsigned zone")
        
        '''Sign the zone rfe_10324.com in the remote server'''
        sign_zone(zone="rfe_10324.com", grid=config.grid2_vip)
        
        '''Add TLSA record and import this record'''
        add_TLSA("_443._tcp.tlsa_signed.rfe_10324.com", 0, "AA", grid=config.grid2_vip)
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth')
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            if 'rfe_10324.com' in ref['_ref'] and 'sub' not in ref['_ref']:
                data = {"use_import_from":True, "import_from":config.grid2_vip}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                display_msg(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        display_msg("Failure: Import TLSA record from signed zone to unsigned zone")
                        assert False
        
        '''Delete records and unsign the zone'''
        delete_all_records_TLSA(config.grid2_vip)
        delete_all_records_TLSA()
        sign_zone(zone="rfe_10324.com", sign=False, grid=config.grid2_vip)
        
        display_msg("-----------Test Case 19 Execution Completed-----------")

    @pytest.mark.run(order=21)
    def test_020_Import_TLSA_record_unsigned_to_signed(self):
        """
        Import TLSA record from unsigned zone to signed zone.
        
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 20 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Import TLSA record from unsigned zone to signed zone")
        
        '''Add TLSA record and import this record'''
        add_TLSA("_443._tcp.tlsa_unsigned.rfe_10324_signed.com", 0, "AA", grid=config.grid2_vip)
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth')
        for ref in json.loads(get_ref):
            if 'rfe_10324_signed.com' in ref['_ref']:
                data = {"use_import_from":True, "import_from":config.grid2_vip}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                display_msg(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        display_msg("Failure: Import TLSA record from unsigned zone to signed zone")
                        assert False
        delete_all_records_TLSA(config.grid2_vip)
        delete_all_records_TLSA()
        
        display_msg("-----------Test Case 20 Execution Completed-----------")

    @pytest.mark.run(order=22)
    def test_021_Import_TLSA_record_signed_to_signed(self):
        """
        Import TLSA record from signed zone to signed zone.
        
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 21 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Import TLSA record from signed zone to signed zone")
        
        '''Sign the zone rfe_10324.com in the remote server'''
        sign_zone(zone="rfe_10324_signed.com", grid=config.grid2_vip)
        
        '''Add TLSA record and import this record'''
        add_TLSA("_443._tcp.tlsa_signed.rfe_10324_signed.com", 0, "AA", grid=config.grid2_vip)
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth')
        for ref in json.loads(get_ref):
            if 'rfe_10324_signed.com' in ref['_ref']:
                data = {"use_import_from":True, "import_from":config.grid2_vip}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                display_msg(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        display_msg("Failure: Import TLSA record from signed zone to signed zone")
                        assert False
        
        '''Delete records and unsign the zone'''
        delete_all_records_TLSA(config.grid2_vip)
        delete_all_records_TLSA()
        sign_zone(zone="rfe_10324_signed.com", sign=False, grid=config.grid2_vip)
        
        display_msg("-----------Test Case 21 Execution Completed-----------")

    @pytest.mark.run(order=23)
    def test_022_Import_TLSA_record_unsigned_to_unsigned(self):
        """
        Import TLSA record from unsigned zone to unsigned zone.
        
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 22 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Import TLSA record from unsigned zone to unsigned zone")
        
        '''Add TLSA record and import this record'''
        add_TLSA("_443._tcp.tlsa_unsigned.rfe_10324.com", 0, "AA", grid=config.grid2_vip)
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth')
        for ref in json.loads(get_ref):
            if 'rfe_10324.com' in ref['_ref'] and 'sub' not in ref['_ref']:
                data = {"use_import_from":True, "import_from":config.grid2_vip}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                display_msg(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        display_msg("Failure: Import TLSA record from signed zone to signed zone")
                        assert False
        delete_all_records_TLSA(config.grid2_vip)
        delete_all_records_TLSA()
        
        display_msg("-----------Test Case 22 Execution Completed-----------")

    @pytest.mark.run(order=24)
    def test_023_Zone_transfer_primary_signed_secondary(self):
        """
        Perform zone transfer with TLSA record between primary signed zone and secondary servers
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 23 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Zone transfer between primary signed zone and secondary server")
        
        '''Add primary signed zone with external secodary'''
        global grid2_fqdn
        display_msg("Create an Authorative FMZ rfe_10324_zone_transfer.com with grid primary and external secondary")
        data = {"fqdn": "rfe_10324_zone_transfer.com",
                "view":"default",
                "grid_primary": [{"name": config.grid_fqdn,"stealth": False}],
                "external_secondaries": [{"name":grid2_fqdn,"address":config.grid2_vip}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Create Authorative FMZ in rfe_10324_zone_transfer.com with grid primary and external secondary")
                assert False
        restart_services()
        
        '''Sign the zone rfe_10324_zone_transfer.com in the remote server'''
        sign_zone(zone="rfe_10324_zone_transfer.com")
        
        '''Add zone with external primary and grid secondary in remote server'''
        display_msg("Create an Authorative FMZ rfe_10324_zone_transfer.com with grid secondary and external primary")
        data = {"fqdn": "rfe_10324_zone_transfer.com",
                "view":"default",
                "use_external_primary": True,
                "grid_secondaries": [{"name": grid2_fqdn,"stealth": False}],
                "external_primaries": [{"name":config.grid_fqdn,"address":config.grid_vip}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data), grid_vip=config.grid2_vip)
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Create Authorative FMZ in rfe_10324_zone_transfer.com with grid primary and external secondary")
                assert False
        restart_services(config.grid2_vip)
        
        '''Add TLSA record in primary    zone'''
        add_TLSA("_443._tcp.tlsa_signed.rfe_10324_zone_transfer.com", 0, "AA")
        sleep(60)
        
        '''Perform dig query on the external server'''
        output = os.popen("dig @"+config.grid2_vip+" rfe_10324_zone_transfer.com axfr").read()
        display_msg(output)
        
        display_msg("Perform dig query for the added TLSA record")
        output = os.popen("dig @"+config.grid2_vip+" _443._tcp.tlsa_signed.rfe_10324_zone_transfer.com IN TLSA").read()
        output = output.split('\n')
        answer = False
        pattern = False
        for line in output:
            display_msg(line)
        for line in output:
            if answer:
                match = re.match("_443._tcp.tlsa_signed.rfe_10324_zone_transfer.com.\s+\d+\s+IN TLSA", line)
                if match:
                    pattern = True
                    break
            if 'ANSWER SECTION' in line:
                answer = True
        if not answer or not pattern:
            display_msg("Failure: Perform dig query")
            assert False
        
        '''Delete the created zones'''
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth')
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            if 'rfe_10324_zone_transfer' in ref['_ref']:
                response=ib_NIOS.wapi_request('DELETE', ref=ref['_ref'])
                display_msg(response)
        restart_services()
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth', grid_vip=config.grid2_vip)
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            if 'rfe_10324_zone_transfer' in ref['_ref']:
                response=ib_NIOS.wapi_request('DELETE', ref=ref['_ref'],grid_vip=config.grid2_vip)
                display_msg(response)
        restart_services(config.grid2_vip)
        
        display_msg("-----------Test Case 23 Execution Completed-----------")

    @pytest.mark.run(order=25)
    def test_024_Zone_transfer_primary_unsigned_secondary(self):
        """
        Perform zone transfer with TLSA record between primary unsigned zone and secondary servers
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 24 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Zone transfer between primary unsigned zone and secondary server")
        
        '''Add primary zone with external secodary'''
        global grid2_fqdn
        display_msg("Create an Authorative FMZ rfe_10324_zone_transfer.com with grid primary and external secondary")
        data = {"fqdn": "rfe_10324_zone_transfer.com",
                "view":"default",
                "grid_primary": [{"name": config.grid_fqdn,"stealth": False}],
                "external_secondaries": [{"name":grid2_fqdn,"address":config.grid2_vip}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Create Authorative FMZ in rfe_10324_zone_transfer.com with grid primary and external secondary")
                assert False
        restart_services()
        
        '''Add zone with external primary and grid secondary in remote server'''
        display_msg("Create an Authorative FMZ rfe_10324_zone_transfer.com with grid secondary and external primary")
        data = {"fqdn": "rfe_10324_zone_transfer.com",
                "view":"default",
                "use_external_primary": True,
                "grid_secondaries": [{"name": grid2_fqdn,"stealth": False}],
                "external_primaries": [{"name":config.grid_fqdn,"address":config.grid_vip}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data),grid_vip=config.grid2_vip)
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Create Authorative FMZ in rfe_10324_zone_transfer.com with grid primary and external secondary")
                assert False
        restart_services(config.grid2_vip)
        
        '''Add TLSA record in primary unsigned zone'''
        add_TLSA("_443._tcp.tlsa_signed.rfe_10324_zone_transfer.com", 0, "AA")
        sleep(60)
        
        '''Perform dig query on the external server'''
        output = os.popen("dig @"+config.grid2_vip+" rfe_10324_zone_transfer.com axfr").read()
        display_msg(output)
        
        display_msg("Perform dig query for the added TLSA record")
        output = os.popen("dig @"+config.grid2_vip+" _443._tcp.tlsa_signed.rfe_10324_zone_transfer.com IN TLSA").read()
        output = output.split('\n')
        answer = False
        pattern = False
        for line in output:
            display_msg(line)
        for line in output:
            if answer:
                match = re.match("_443._tcp.tlsa_signed.rfe_10324_zone_transfer.com.\s+\d+\s+IN TLSA", line)
                if match:
                    pattern = True
                    break
            if 'ANSWER SECTION' in line:
                answer = True
        if not answer or not pattern:
            display_msg("Failure: Perform dig query")
            assert False
        
        '''Delete the created zones'''
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth')
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            if 'rfe_10324_zone_transfer' in ref['_ref']:
                response=ib_NIOS.wapi_request('DELETE', ref=ref['_ref'])
                display_msg(response)
        restart_services()
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth', grid_vip=config.grid2_vip)
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            if 'rfe_10324_zone_transfer' in ref['_ref']:
                response=ib_NIOS.wapi_request('DELETE', ref=ref['_ref'],grid_vip=config.grid2_vip)
                display_msg(response)
        restart_services(config.grid2_vip)
        
        display_msg("-----------Test Case 24 Execution Completed-----------")

    @pytest.mark.run(order=26)
    def test_025_Add_TLSA_record_and_query_member(self):
        """
        Add TLSA record in the member and query the record.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 25 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        '''Create Authoritative FMZ'''
        display_msg("Create an Authoritative FMZ unsigned")
        data = {"fqdn": "rfe_10324_member.com",
                "view":"default",
                "grid_primary": [{"name": config.grid_member1_fqdn,"stealth": False}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Create Authorative FMZ")
                assert False
        restart_services()
        
        '''Add TLSA record and import this record'''
        add_TLSA('_443._tcp.tlsa_member.rfe_10324_member.com', 0, 'AA')
        
        '''Perform dig query on the external server'''
        output = os.popen("dig @"+config.grid_member1_vip+" rfe_10324_member.com axfr").read()
        display_msg(output)
        
        display_msg("Perform dig query for the added TLSA record")
        output = os.popen("dig @"+config.grid_member1_vip+" _443._tcp.tlsa_member.rfe_10324_member.com IN TLSA").read()
        output = output.split('\n')
        answer = False
        pattern = False
        for line in output:
            display_msg(line)
        for line in output:
            if answer:
                match = re.match("_443._tcp.tlsa_member.rfe_10324_member.com.\s+\d+\s+IN TLSA", line)
                if match:
                    pattern = True
                    break
            display_msg(line)
            if 'ANSWER SECTION' in line:
                answer = True
        if not answer or not pattern:
            display_msg("Failure: Perform dig query")
            assert False
        
        display_msg("-----------Test Case 25 Execution Completed-----------")

    @pytest.mark.run(order=27)
    def test_026_DNSSEC_validation_with_TLSA_record(self):
        """
        Add "TLSA" record into signed zone.
        Add "TLSA" record into the zone and sign the zone
        Modify the "TLSA" record after signing the zone
        Delete the added "TLSA" record after zone signing
        Add aditional resource records after signing the zone
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 26 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add TLSA record into signed zone")
        add_TLSA("tlsa_signed_dnssec.rfe_10324_signed.com", 0, "AA")
        
        display_msg("Add TLSA record into the zone and sign the zone")
        add_TLSA("tlsa_signed_dnssec.rfe_10324.com", 0, "AA")
        sign_zone('rfe_10324.com')
        
        display_msg("Modify the TLSA record after signing the zone")
        get_ref = ib_NIOS.wapi_request('GET', object_type='record:tlsa')
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            if 'rfe_10324.com' in ref['_ref']:
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps({"name":"tlsa_modified.rfe_10324.com"}))
                display_msg(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        display_msg("Failure: Modify TLSA record after signing the zone")
                        assert False
                restart_services()
        
        display_msg("Add aditional resource records after signing the zone")
        data = {"name":"a_record.rfe_10324.com",
                "ipv4addr":"1.1.1.1"
                }
        response = ib_NIOS.wapi_request('POST',object_type='record:a',fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Add additional resource record")
                assert False
        restart_services()
        
        sign_zone(zone='rfe_10324.com',sign=False)
        
        display_msg("Delete the added TLSA record after zone signing")
        delete_all_records_TLSA()
        
        display_msg("-----------Test Case 26 Execution Completed-----------")

    @pytest.mark.run(order=28)
    def test_027_Add_Modify_Delete_TLSA_record_nsupdate_PKIX_TA(self):
        """
        Through nsupdate Add/Modify/Delete TLSA  record  in the unsigned zone
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 27 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add TLSA record using nsupdate in the unsigned zone")
        child = pexpect.spawn("nsupdate")
        try:
            child.expect('>')
            child.send('server '+config.grid_vip+'\n')
            display_msg(child.before)
            child.expect('>')
            child.send('update add _443._tcp.tlsa_nsupdate.rfe_10324.com. 28800 TLSA 0 0 0 AA\n')
            display_msg(child.before)
            child.expect('>')
            child.send('send\n')
            display_msg(child.before)
            child.expect('>')
            child.send('quit\n')
        except Exception as e:
            display_msg(e)
            assert False
        finally:
            child.close()
        
        '''display_msg("Update TLSA record using nsupdate in the unsigned zone")
        child = pexpect.spawn("nsupdate")
        try:
            child.expect('>')
            child.send('server '+config.grid_vip+'\n')
            display_msg(child.before)
            child.expect('>')
            child.send('update add _443._tcp.tlsa_nsupdate.rfe_10324.com. 28800 TLSA 1 0 0 AA\n')
            display_msg(child.before)
            child.expect('>')
            child.send('send\n')
            display_msg(child.before)
            child.expect('>')
            child.send('quit\n')
        except Exception as e:
            display_msg(e)
            assert False
        finally:
            child.close()'''
        
        display_msg("Delete TLSA record using nsupdate in the unsigned zone")
        child = pexpect.spawn("nsupdate")
        try:
            child.expect('>')
            child.send('server '+config.grid_vip+'\n')
            display_msg(child.before)
            child.expect('>')
            child.send('update delete _443._tcp.tlsa_nsupdate.rfe_10324.com. 28800 TLSA 1 0 0 AA\n')
            display_msg(child.before)
            child.expect('>')
            child.send('send\n')
            display_msg(child.before)
            child.expect('>')
            child.send('quit\n')
        except Exception as e:
            display_msg(e)
            assert False
        finally:
            child.close()
        
        display_msg("-----------Test Case 27 Execution Completed-----------")

    @pytest.mark.run(order=29)
    def test_028_Add_Modify_Delete_TLSA_record_nsupdate_PKIX_EE(self):
        """
        Through nsupdate Add/Modify/Delete TLSA  record  in the unsigned zone
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 28 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add TLSA record using nsupdate in the unsigned zone")
        child = pexpect.spawn("nsupdate")
        try:
            child.expect('>')
            child.send('server '+config.grid_vip+'\n')
            display_msg(child.before)
            child.expect('>')
            child.send('update add _443._tcp.tlsa_nsupdate.rfe_10324.com. 28800 TLSA 1 0 0 AA\n')
            display_msg(child.before)
            child.expect('>')
            child.send('send\n')
            display_msg(child.before)
            child.expect('>')
            child.send('quit\n')
        except Exception as e:
            display_msg(e)
            assert False
        finally:
            child.close()
        
        '''display_msg("Update TLSA record using nsupdate in the unsigned zone")
        child = pexpect.spawn("nsupdate")
        try:
            child.expect('>')
            child.send('server '+config.grid_vip+'\n')
            display_msg(child.before)
            child.expect('>')
            child.send('update add _443._tcp.tlsa_nsupdate.rfe_10324.com. 28800 TLSA 2 0 0 AA\n')
            display_msg(child.before)
            child.expect('>')
            child.send('send\n')
            display_msg(child.before)
            child.expect('>')
            child.send('quit\n')
        except Exception as e:
            display_msg(e)
            assert False
        finally:
            child.close()'''
        
        display_msg("Delete TLSA record using nsupdate in the unsigned zone")
        child = pexpect.spawn("nsupdate")
        try:
            child.expect('>')
            child.send('server '+config.grid_vip+'\n')
            display_msg(child.before)
            child.expect('>')
            child.send('update delete _443._tcp.tlsa_nsupdate.rfe_10324.com. 28800 TLSA 2 0 0 AA\n')
            display_msg(child.before)
            child.expect('>')
            child.send('send\n')
            display_msg(child.before)
            child.expect('>')
            child.send('quit\n')
        except Exception as e:
            display_msg(e)
            assert False
        finally:
            child.close()
        
        display_msg("-----------Test Case 28 Execution Completed-----------")

    @pytest.mark.run(order=30)
    def test_029_Add_Modify_Delete_TLSA_record_nsupdate_DANE_TA(self):
        """
        Through nsupdate Add/Modify/Delete TLSA  record  in the unsigned zone
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 29 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add TLSA record using nsupdate in the unsigned zone")
        child = pexpect.spawn("nsupdate")
        try:
            child.expect('>')
            child.send('server '+config.grid_vip+'\n')
            display_msg(child.before)
            child.expect('>')
            child.send('update add _443._tcp.tlsa_nsupdate.rfe_10324.com. 28800 TLSA 2 0 0 AA\n')
            display_msg(child.before)
            child.expect('>')
            child.send('send\n')
            display_msg(child.before)
            child.expect('>')
            child.send('quit\n')
        except Exception as e:
            display_msg(e)
            assert False
        finally:
            child.close()
        
        '''display_msg("Update TLSA record using nsupdate in the unsigned zone")
        child = pexpect.spawn("nsupdate")
        try:
            child.expect('>')
            child.send('server '+config.grid_vip+'\n')
            display_msg(child.before)
            child.expect('>')
            child.send('update add _443._tcp.tlsa_nsupdate.rfe_10324.com. 28800 TLSA 3 0 0 AA\n')
            display_msg(child.before)
            child.expect('>')
            child.send('send\n')
            display_msg(child.before)
            child.expect('>')
            child.send('quit\n')
        except Exception as e:
            display_msg(e)
            assert False
        finally:
            child.close()'''
        
        display_msg("Delete TLSA record using nsupdate in the unsigned zone")
        child = pexpect.spawn("nsupdate")
        try:
            child.expect('>')
            child.send('server '+config.grid_vip+'\n')
            display_msg(child.before)
            child.expect('>')
            child.send('update delete _443._tcp.tlsa_nsupdate.rfe_10324.com. 28800 TLSA 3 0 0 AA\n')
            display_msg(child.before)
            child.expect('>')
            child.send('send\n')
            display_msg(child.before)
            child.expect('>')
            child.send('quit\n')
        except Exception as e:
            display_msg(e)
            assert False
        finally:
            child.close()
        
        display_msg("-----------Test Case 29 Execution Completed-----------")

    @pytest.mark.run(order=31)
    def test_030_Add_Modify_Delete_TLSA_record_nsupdate_DANE_EE(self):
        """
        Through nsupdate Add/Modify/Delete TLSA  record  in the unsigned zone
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 30 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add TLSA record using nsupdate in the unsigned zone")
        child = pexpect.spawn("nsupdate")
        try:
            child.expect('>')
            child.send('server '+config.grid_vip+'\n')
            display_msg(child.before)
            child.expect('>')
            child.send('update add _443._tcp.tlsa_nsupdate.rfe_10324.com. 28800 TLSA 3 0 0 AA\n')
            display_msg(child.before)
            child.expect('>')
            child.send('send\n')
            display_msg(child.before)
            child.expect('>')
            child.send('quit\n')
        except Exception as e:
            display_msg(e)
            assert False
        finally:
            child.close()
        
        '''display_msg("Update TLSA record using nsupdate in the unsigned zone")
        child = pexpect.spawn("nsupdate")
        try:
            child.expect('>')
            child.send('server '+config.grid_vip+'\n')
            display_msg(child.before)
            child.expect('>')
            child.send('update add _443._tcp.tlsa_nsupdate.rfe_10324.com. 28800 TLSA 3 0 0 BB\n')
            display_msg(child.before)
            child.expect('>')
            child.send('send\n')
            display_msg(child.before)
            child.expect('>')
            child.send('quit\n')
        except Exception as e:
            display_msg(e)
            assert False
        finally:
            child.close()'''
        
        display_msg("Delete TLSA record using nsupdate in the unsigned zone")
        child = pexpect.spawn("nsupdate")
        try:
            child.expect('>')
            child.send('server '+config.grid_vip+'\n')
            display_msg(child.before)
            child.expect('>')
            child.send('update delete _443._tcp.tlsa_nsupdate.rfe_10324.com. 28800 TLSA 4 0 0 BB\n')
            display_msg(child.before)
            child.expect('>')
            child.send('send\n')
            display_msg(child.before)
            child.expect('>')
            child.send('quit\n')
        except Exception as e:
            display_msg(e)
            assert False
        finally:
            child.close()
        
        display_msg("-----------Test Case 30 Execution Completed-----------")

    @pytest.mark.run(order=32)
    def test_031_Add_Modify_Delete_default_EAs_TLSA_record_unsigned(self):
        """
        Add/modify/delete the default EAs to TLSA record in the unsigned zone
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 31 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add/modify/delete the default EAs to TLSA record in the unsigned zone")
        add_TLSA("tlsa_ea.rfe_10324.com", 1, "AA")
        
        display_msg("Add default EAs to the created record")
        get_ref = ib_NIOS.wapi_request('GET',object_type='record:tlsa')
        for ref in json.loads(get_ref):
            if 'tlsa_ea' in ref['_ref']:
                data = {"extattrs":{"IB Discovery Owned":{"value":"100"},"Site":{"value":"200"}}}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                display_msg(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        display_msg("Failure: Add default EAs to TLSA record in the unsigned zone")
                        assert False
        
        display_msg("Modify default EAs to the created record")
        get_ref = ib_NIOS.wapi_request('GET',object_type='record:tlsa')
        for ref in json.loads(get_ref):
            if 'tlsa_ea' in ref['_ref']:
                data = {"extattrs":{"IB Discovery Owned":{"value":"200"},"Site":{"value":"300"}}}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                display_msg(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        display_msg("Failure: Modify default EAs to TLSA record in the unsigned zone")
                        assert False
        
        display_msg("Delete default EAs to the created record")
        get_ref = ib_NIOS.wapi_request('GET',object_type='record:tlsa')
        for ref in json.loads(get_ref):
            if 'tlsa_ea' in ref['_ref']:
                data = {"extattrs":{}}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                display_msg(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        display_msg("Failure: Delete default EAs to TLSA record in the unsigned zone")
                        assert False
        
        delete_all_records_TLSA()
        display_msg("-----------Test Case 31 Execution Completed-----------")

    @pytest.mark.run(order=33)
    def test_032_Add_Modify_Delete_custom_EAs_TLSA_record_unsigned(self):
        """
        Add/modify/delete the custom EAs to TLSA record in the unsigned zone
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 32 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add/modify/delete the custom EAs to TLSA record in the unsigned zone")
        add_TLSA("tlsa_ea_custom.rfe_10324.com", 0, "AA")
        
        display_msg("Add custom extensible attribute")
        data = {"name":"custom_ea","type":"STRING"}
        response = ib_NIOS.wapi_request('POST', object_type='extensibleattributedef', fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Add custom extensible attribute")
                assert False
        
        display_msg("Add custom EA to the created record")
        get_ref = ib_NIOS.wapi_request('GET',object_type='record:tlsa')
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            if 'tlsa_ea_custom' in ref['_ref']:
                data = {"extattrs":{"custom_ea":{"value":"add"}}}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                display_msg(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        display_msg("Failure: Add custom EAs to TLSA record in the unsigned zone")
                        assert False
        
        display_msg("Modify custom EAs to the created record")
        get_ref = ib_NIOS.wapi_request('GET',object_type='record:tlsa')
        for ref in json.loads(get_ref):
            if 'tlsa_ea_custom' in ref['_ref']:
                data = {"extattrs":{"custom_ea":{"value":"modify"}}}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                display_msg(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        display_msg("Failure: Modify custom EAs to TLSA record in the unsigned zone")
                        assert False
        
        display_msg("Delete custom EAs to the created record")
        get_ref = ib_NIOS.wapi_request('GET',object_type='record:tlsa')
        for ref in json.loads(get_ref):
            if 'tlsa_ea_custom' in ref['_ref']:
                data = {"extattrs":{}}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                display_msg(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        display_msg("Failure: Delete custom EAs to TLSA record in the unsigned zone")
                        assert False
        
        delete_all_records_TLSA()
        
        display_msg("-----------Test Case 32 Execution Completed-----------")

    @pytest.mark.run(order=34)
    def test_033_import_tlsa_record_csv(self):
        """
        Add TLSA record to the unsigned zone through CSV
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 33 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Uploading csv file containing tlsa record")
        dir_name=os.getcwd()
        base_filename = "add_tlsa.csv"
        token =ib_TOKEN.generate_token_from_file(dir_name, base_filename)
        data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"OVERRIDE","operation":"INSERT"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_import")
        response=json.loads(response)
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: CSV file upload")
                assert False
        
        data={"action":"START","file_name":"add_tlsa.csv","on_error":"CONTINUE","operation":"CREATE","separator":"COMMA"}
        get_ref=ib_NIOS.wapi_request('GET', object_type="csvimporttask")
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            if response["csv_import_task"]["import_id"]==ref["import_id"]:
                if ref["lines_failed"]==0:
                    display_msg("CSV import successful")
                else:
                    raise Exception("CSV import unsuccessful")
        
        restart_services()
        
        display_msg("-----------Test Case 33 Execution Completed-----------")

    @pytest.mark.run(order=35)
    def test_034_modify_tlsa_record_csv(self):
        """
        Modify TLSA record in the unsigned zone through CSV
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 34 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Uploading csv file containing modified tlsa record")
        dir_name=os.getcwd()
        base_filename = "modify_tlsa.csv"
        token =ib_TOKEN.generate_token_from_file(dir_name, base_filename)
        data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"OVERRIDE","operation":"UPDATE"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_import")
        response=json.loads(response)
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: CSV file upload")
                assert False
        
        data={"action":"START","file_name":"modify_tlsa.csv","on_error":"CONTINUE","operation":"CREATE","separator":"COMMA"}
        get_ref=ib_NIOS.wapi_request('GET', object_type="csvimporttask")
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            if response["csv_import_task"]["import_id"]==ref["import_id"]:
                if ref["lines_failed"]==0:
                    display_msg("CSV import successful")
                else:
                    raise Exception("CSV import unsuccessful")
        
        restart_services()
        
        display_msg("-----------Test Case 34 Execution Completed-----------")

    @pytest.mark.run(order=36)
    def test_035_delete_tlsa_record_csv(self):
        """
        Delete TLSA record in the unsigned zone through CSV
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 35 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Uploading csv file containing tlsa record for delete")
        dir_name=os.getcwd()
        base_filename = "modify_tlsa.csv"
        token =ib_TOKEN.generate_token_from_file(dir_name, base_filename)
        data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"OVERRIDE","operation":"DELETE"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_import")
        response=json.loads(response)
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: CSV file upload")
                assert False
        
        data={"action":"START","file_name":"modify_tlsa.csv","on_error":"CONTINUE","operation":"CREATE","separator":"COMMA"}
        get_ref=ib_NIOS.wapi_request('GET', object_type="csvimporttask")
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            if response["csv_import_task"]["import_id"]==ref["import_id"]:
                if ref["lines_failed"]==0:
                    display_msg("CSV import successful")
                else:
                    raise Exception("CSV import unsuccessful")
        
        restart_services()
        
        display_msg("-----------Test Case 35 Execution Completed-----------")

    @pytest.mark.run(order=37)
    def test_036_create_submitter_approver_group_user(self):
        """
        Create submitter group and submitter user.
        Create approver group and approver user.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 36 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        '''Submitter group'''
        display_msg("Create submitter group")
        data = {"name":"submitter","access_method":["GUI","API"],"roles":["DNS Admin"]}
        response = ib_NIOS.wapi_request('POST', object_type='admingroup', fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Create group submitter")
                assert False
        
        '''Submitter user'''
        display_msg("Create submitter user")
        data = {"name":"submitter","password":"infoblox","admin_groups":["submitter"]}
        response = ib_NIOS.wapi_request('POST', object_type='adminuser', fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Create user submitter")
                assert False
        
        '''Approver group'''
        display_msg("Create approver group")
        data = {"name":"approver","access_method":["GUI","API"],"roles":["DNS Admin"]}
        response = ib_NIOS.wapi_request('POST', object_type='admingroup', fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Create group approver")
                assert False
        
        '''Approver user'''
        display_msg("Create approver user")
        data = {"name":"approver","password":"infoblox","admin_groups":["approver"]}
        response = ib_NIOS.wapi_request('POST', object_type='adminuser', fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Create user approver")
        
        display_msg("-----------Test Case 36 Execution Completed-----------")

    @pytest.mark.run(order=38)
    def test_037_create_approval_workflow(self):
        """
        Create approval workflow with submitter and approver groups
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 37 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Create approver workflow")
        data = {"approval_group":"approver","submitter_group":"submitter"}
        response = ib_NIOS.wapi_request('POST', object_type='approvalworkflow', fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Create approval workflow")
                assert False
        
        display_msg("-----------Test Case 37 Execution Completed-----------")

    @pytest.mark.run(order=39)
    def test_038_create_TLSA_record_from_submitter_user(self):
        """
        Create TLSA record from submitter user.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 38 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Create TLSA record from submitter user")
        data = {"name":"tlsa_submitter.rfe_10324.com","certificate_usage":1,"certificate_data":"AA","matched_type":0,"selector":0}
        response = ib_NIOS.wapi_request('POST', object_type='record:tlsa', fields=json.dumps(data), user='submitter', password='infoblox')
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Create approval workflow")
                assert False
        
        display_msg("-----------Test Case 38 Execution Completed-----------")

    @pytest.mark.run(order=40)
    def test_039_approve_TLSA_creation_from_approval_user(self):
        """
        Approve TLSA record creation from approver user.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 39 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        display_msg("Approve TLSA record creation from approver user")
        get_ref = ib_NIOS.wapi_request('GET', object_type='scheduledtask')
        data = {"approval_status":"APPROVED"}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data), user='approver', password='infoblox')
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Approve TLSA record creation from approver user")
                assert False
        delete_all_records_TLSA()
        display_msg("-----------Test Case 39 Execution Completed-----------")

    @pytest.mark.run(order=41)
    def test_040_verify_auditlog_for_insert_update_delete_TLSA_record(self):
        """
        Audit log entries will be provided for "TLSA" record insert, update and delete in the unsigned zone
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 40 Execution Started          |")
        display_msg("----------------------------------------------------")
        
        '''Insert TLSA record and verify auditlog'''
        display_msg("Validate auditlog for inster TLSA record")
        add_TLSA("_443._tcp.tlsa_audit_log.rfe_10324.com", 0, "AA")
        if not validate_log('/infoblox/var/audit.log','Created TlsaRecord _443._tcp.tlsa_audit_log.rfe_10324.com'):
            display_msg("Failure: Verify auditlog for insert TLSA record")
            assert False
        
        '''Update TLSA record and verify auditlog'''
        display_msg("Validate auditlog for update TLSA record")
        get_ref = ib_NIOS.wapi_request('GET', object_type='record:tlsa')
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            if 'tlsa_audit_log' in ref['_ref']:
                data = {"name":"_443._tcp.tlsa_audit_log_updated.rfe_10324.com"}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                display_msg(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        display_msg("Failure: Modify TLSA record name")
                        assert False
                if not validate_log('/infoblox/var/audit.log','Modified TlsaRecord _443._tcp.tlsa_audit_log_updated.rfe_10324.com'):
                    display_msg("Failure: Verify auditlog for update TLSA record")
                    assert False
        
        '''Delete TLSA record and verify auditlog'''
        delete_all_records_TLSA()
        if not validate_log('/infoblox/var/audit.log','Deleted TlsaRecord _443._tcp.tlsa_audit_log_updated.rfe_10324.com'):
            display_msg("Failure: Verify auditlog for delete TLSA record")
            assert False
        
        display_msg("-----------Test Case 40 Execution Completed-----------")

    @pytest.mark.run(order=-1)
    def test_cleanup(self):
        """
        cleanup method: Delete all the objects created from this script.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|          Test Case cleanup Started           |")
        display_msg("------------------------------------------------")
        display_msg("Delete Authorative FMZ")
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth')
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            if 'rfe_10324' in ref['_ref']:
                response=ib_NIOS.wapi_request('DELETE', ref=ref['_ref'])
                display_msg(response)
        restart_services()
        
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth', grid_vip=config.grid2_vip)
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            if 'rfe_10324' in ref['_ref']:
                response=ib_NIOS.wapi_request('DELETE', ref=ref['_ref'],grid_vip=config.grid2_vip)
                display_msg(response)
        restart_services(config.grid2_vip)
        display_msg("-----------Test Case cleanup Completed------------")

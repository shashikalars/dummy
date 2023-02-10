#!/usr/bin/env python
__author__ = "Chetan Kumar PG"
__email__  = "cpg@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Grid Master + Grid Member                                             #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415)                           #
#############################################################################

import os
import re
import config
import pytest
import unittest
import logging
import json
import paramiko
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="niosspt_8996.log" ,level=logging.DEBUG,filemode='w')

def display_msg(x=""):
    """ 
    Additional function.
    """
    logging.info(x)
    print(x)

class NIOSSPT_8996(unittest.TestCase):
    
    @pytest.mark.run(order=1)
    def test_000_setup(self):
        """
        setup method: Used for configuring pre-required configs.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case setup Started            |")
        display_msg("------------------------------------------------")
        
        display_msg("Verify that member SNMP properties are inherited from the grid master")
        response = ib_NIOS.wapi_request('GET', object_type='member', params="?_return_fields=use_snmp_setting")
        display_msg(response)
        res = json.loads(response)[1]
        if not res["use_snmp_setting"] == False:
            display_msg("Inherit SNMP properties from grid master")
            response = ib_NIOS.wapi_request('PUT', object_type=res['_ref'], fields=json.dumps({"use_snmp_setting":False}))
            display_msg(response)
            if type(response) == tuple:
                display_msg("Failure: Inherit SNMP properties from grid master")
                assert False
            display_msg("sleep 60 seconds for SNMP properties changes to take effect")
            sleep(60)
        
        display_msg("-----------Test Case setup Execution Completed------------")
    
    @pytest.mark.run(order=2)
    def test_001_Check_SNMP_engine_ID_with_inherit(self):
        """
        Check SNMP Engine ID of both master and member.
        Verify that the both the Engine IDs are different.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 1 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Check SNMP Engine ID of both master and member when SNMP properties are inherited")
        response = ib_NIOS.wapi_request('GET', object_type="member", params="?_return_fields=snmp_setting")
        display_msg(response)
        res = json.loads(response)
        master_engine_id = res[0]["snmp_setting"]["engine_id"][0]
        member_engine_id = res[1]["snmp_setting"]["engine_id"][0]
        display_msg("Master Engine ID: "+master_engine_id)
        display_msg("Member Engine ID: "+member_engine_id)
        if master_engine_id==member_engine_id:
            display_msg("Failure: Master Engine ID and Member Engine ID are same when inherit is True")
            assert False
            
        display_msg("-----------Test Case 1 Execution Completed------------")

    @pytest.mark.run(order=3)
    def test_002_Check_SNMP_engine_ID_with_inherit_file_validation(self):
        """
        When SNMP properties are inherited.
        Check SNMP Engine ID of both master and member in the file /var/lib/net-snmp/snmpd.conf.
        Verify that the both the Engine IDs are not same.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 2 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Validate in the file that the inherited SNMP Engine ID of the memebr is not same as in the master")
        
        '''Master Engine ID'''
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        stdin, stdout, stderr = client.exec_command("cat /var/lib/net-snmp/snmpd.conf | grep oldEngineID")
        master_engine_id=stdout.read().split()[-1]
        display_msg("Master Engine ID: "+master_engine_id)
        client.close()
        
        '''Member Engine ID'''
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_member1_vip, username='root', pkey = mykey)
        stdin, stdout, stderr = client.exec_command("cat /var/lib/net-snmp/snmpd.conf | grep oldEngineID")
        member_engine_id=stdout.read().split()[-1]
        display_msg("Member Engine ID: "+member_engine_id)
        client.close()
        
        if master_engine_id==member_engine_id:
            display_msg("Failure: Master Engine ID and Member Engine ID are same when inherit is True")
            assert False
        
        display_msg("-----------Test Case 2 Execution Completed------------")


    @pytest.mark.run(order=4)
    def test_003_Check_SNMP_engine_ID_with_override(self):
        """
        Override the snmp settings in Grid member.
        Check SNMP Engine ID of both master and member.
        Verify that the both the Engine IDs are different.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 3 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Check that the SNMP Engine ID of the memebr is different from the master when snmp settings are overridden")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member", params="?_return_fields=snmp_setting")
        member_ref = json.loads(get_ref)[1]
        display_msg(get_ref)
        response = ib_NIOS.wapi_request('PUT', object_type=member_ref['_ref'], fields=json.dumps({"use_snmp_setting":True}))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: SNMP properties override")
            assert False
        display_msg("sleep 60 seconds for SNMP properties changes to take effect")
        sleep(60)
        
        response = ib_NIOS.wapi_request('GET', object_type="member", params="?_return_fields=snmp_setting")
        display_msg(response)
        res = json.loads(response)
        master_engine_id = res[0]["snmp_setting"]["engine_id"][0]
        member_engine_id = res[1]["snmp_setting"]["engine_id"][0]
        display_msg("Master Engine ID: "+master_engine_id)
        display_msg("Member Engine ID: "+member_engine_id)
        if master_engine_id==member_engine_id:
            display_msg("Failure: Master Engine ID and Member Engine ID are same when inherit is selected")
            assert False
        display_msg("-----------Test Case 3 Execution Completed------------")

    @pytest.mark.run(order=5)
    def test_004_Check_SNMP_engine_ID_with_override_file_validation(self):
        """
        When SNMP properties are overriden
        Check SNMP Engine ID of both master and member in the file /var/lib/net-snmp/snmpd.conf.
        Verify that the both the Engine IDs are not same.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 4 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Validate in the file that the SNMP Engine ID of the memebr and master are different")
        
        '''Master Engine ID'''
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        stdin, stdout, stderr = client.exec_command("cat /var/lib/net-snmp/snmpd.conf | grep oldEngineID")
        master_engine_id=stdout.read().split()[-1]
        display_msg("Master Engine ID: "+master_engine_id)
        client.close()
        
        '''Member Engine ID'''
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_member1_vip, username='root', pkey = mykey)
        stdin, stdout, stderr = client.exec_command("cat /var/lib/net-snmp/snmpd.conf | grep oldEngineID")
        member_engine_id=stdout.read().split()[-1]
        display_msg("Member Engine ID: "+member_engine_id)
        client.close()
        
        if master_engine_id==member_engine_id:
            display_msg("Failure: Master Engine ID and Member Engine ID are same when override is selected")
            assert False
        
        display_msg("-----------Test Case 4 Execution Completed------------")

    @pytest.mark.run(order=-1)
    def test_cleanup(self):
        """
        cleanup method: Delete all the objects created from this script.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|          Test Case cleanup Started           |")
        display_msg("------------------------------------------------")
        
        display_msg("Reverting back the member SNMP Setting")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member", params="?_return_fields=snmp_setting")
        member_ref = json.loads(get_ref)[1]
        display_msg(get_ref)
        response = ib_NIOS.wapi_request('PUT', object_type=member_ref['_ref'], fields=json.dumps({"use_snmp_setting":False}))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Reverting back the member SNMP Setting")
            assert False
        display_msg("sleep 60 seconds for SNMP properties changes to take effect")
        sleep(60)
        display_msg("-----------Test Case cleanup Completed------------")

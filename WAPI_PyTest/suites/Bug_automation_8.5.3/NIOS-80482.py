#!/usr/bin/env python
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. SA configuration                                                      #
#  2. License : Grid                                                        #
#############################################################################

import re
import config
import pytest
import unittest
import logging
import subprocess
import os
import sys
import json
import commands
import json, ast
import requests
import paramiko
from time import sleep as sleep
import ib_utils.ib_NIOS as ib_NIOS
from ib_utils.log_capture import log_action as log

from ib_utils.log_validation import log_validation as logv
import pexpect

class NIOS_80482(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_enable_ntp_on_grid_member(self):
        print("Enabling ntp on grid member ")
        request = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
        request = json.loads(request)
        print(request)

        for request_ref in request:
            print(request_ref)
            data = {"ntp_setting": {"enable_ntp": True}}
            res = ib_NIOS.wapi_request('PUT', object_type=request_ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            print(res)
            assert re.search(r'member', res)
    
    @pytest.mark.run(order=2)
    def test_001_validate_the_default_values_present_in_orphan_mode_of_grid_master(self):
        print("Validate the default values present in orphan mode of grid master")
        request = ib_NIOS.wapi_request('GET', object_type="grid")
        request = json.loads(request)
        res_ref = request[0]['_ref']
        print(res_ref)
        request1 = ib_NIOS.wapi_request('GET', object_type=res_ref, params='?_return_fields=ntp_setting')
        request1 = json.loads(request1)
        print(request1)
        default_local_ntp_value = request1['ntp_setting']['use_default_stratum']
        print(default_local_ntp_value)
        if default_local_ntp_value == True:
            print("Validate Default values of grid master")
            assert True
        else:
            print("Validate Default values of grid master")
            assert False
        '''
        print("Disabling ntp orphan")
        request = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
        request = json.loads(request)
        print(request)
        request_ref = request[0]['_ref']
        print(request_ref)
        data = {"ntp_setting": {"default": "use_default_stratum"}}
        res = ib_NIOS.wapi_request('PUT', object_type=request_ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        print(res)
        '''

    @pytest.mark.run(order=3)
    def test_002_validate_the_default_value_present_in_orphan_mode_of_grid_member(self):
        '''
        print("Disabling ntp orphan")
        request = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
        request = json.loads(request)
        print(request)
        request_ref = request[0]['_ref']
        print(request_ref)
        data = {"ntp_setting": {"default": "use_default_stratum"}}
        res = ib_NIOS.wapi_request('PUT', object_type=request_ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        print(res)
        '''

        print("Validate the default values present in orphan mode of grid member")
        request = ib_NIOS.wapi_request('GET', object_type="member")
        request = json.loads(request)
        res_ref = request[1]['_ref']
        print(res_ref)
        request1 = ib_NIOS.wapi_request('GET', object_type=res_ref, params='?_return_fields=ntp_setting')
        request1 = json.loads(request1)
        print(request1)
        gm_local_ntp_stratum = request1['ntp_setting']['local_ntp_stratum']
        print(gm_local_ntp_stratum)
        if int(gm_local_ntp_stratum) == 15:
            print("Default value in grid member is"+str(gm_local_ntp_stratum))
            assert True
        else:
            print("Default value in grid member is not"+str(gm_local_ntp_stratum))
            assert False



    @pytest.mark.run(order=4)
    def test_003_Configure_other_values_to_orphan_mode_other_than_default_values(self):
        print("Configure other values to orphan mode other than default values")
        print("\nChecking for NTPD restart")
        log("start", "/infoblox/var/infoblox.log", config.grid_vip)
        log("start", "/infoblox/var/infoblox.log", config.grid_member1_vip)
        request = ib_NIOS.wapi_request('GET', object_type="grid")
        request = json.loads(request)
        res_ref = request[0]['_ref']
        print(res_ref)
        data = {"ntp_setting": {"gm_local_ntp_stratum": 8, "local_ntp_stratum": 9,'use_default_stratum':False}}
        request1 = ib_NIOS.wapi_request('PUT', object_type=res_ref, fields=json.dumps(data))
        print(request1)
        assert re.search(r'grid', request1)
        sleep(60)


    @pytest.mark.run(order=5)
    def test_004_Check_if_ntpd_process_is_restarted_in_grid_master(self):
        print("Check if ntpd process is restarted in grid master")
        LookFor="'Restarting ntpd due to conf file differences below'"
        log("stop","/infoblox/var/infoblox.log", config.grid_vip)
        logs=logv(LookFor,"/infoblox/var/infoblox.log", config.grid_vip)
        print("NTPD process is restarted successfully")

    @pytest.mark.run(order=6)
    def test_005_Check_if_ntpd_process_is_restarted_in_grid_member(self):
        print("Check if ntpd process is restarted in grid member")
        LookFor="'Restarting ntpd due to conf file differences below'"
        log("stop","/infoblox/var/infoblox.log", config.grid_member1_vip)
        logs=logv(LookFor,"/infoblox/var/infoblox.log", config.grid_member1_vip)
        print("NTPD process is restarted successfully")

    @pytest.mark.run(order=7)
    def test_006_validate_the_custom_value_present_in_master_ntp_conf_file(self):
        print("Validate the custom values present in master ntp.conf file")
        #ip = [config.grid_master_vip, config.grid_member1_vip]
        global gm_local_ntp_value
        print("Logging in to device "+config.grid_master_vip)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_master_vip, username='root', pkey = mykey)
        stdin, stdout, stderr = client.exec_command('cat /tmpfs/ntp.conf')
        output = stdout.read()
        output = output.split("\n")
        print(output)
        match_line = "tos orphan 8"
        match_line2 = "fudge 127.127.1.1 stratum 7"
        print(match_line)
        if match_line in output and match_line2 in output:
            print("The custom value that is updated is seen in ntpd.conf file")
            assert True
        else:
            print("The custom value that is not updated in ntpd.conf file")
            assert False
        client.close()

    @pytest.mark.run(order=8)
    def test_007_validate_the_custom_value_present_in_member_ntp_conf_file(self):
        print("Validate the custom values present in member ntp.conf file")
        #ip = [config.grid_master_vip, config.grid_member1_vip]
        global local_ntp_value
        print("Logging in to device "+config.grid_member1_vip)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_member1_vip, username='root', pkey = mykey)
        stdin, stdout, stderr = client.exec_command('cat /tmpfs/ntp.conf')
        output = stdout.read()
        output = output.split("\n")
        print(output)
        match_line = "tos orphan 9"
        match_line2 = "fudge 127.127.1.1 stratum 8"
        print(match_line)
        if match_line in output and match_line2 in output:
            print("The custom value that is updated is seen in ntpd.conf file")
            assert True
        else:
            print("The custom value that is not updated in ntpd.conf file")
            assert False
        client.close()


    @pytest.mark.run(order=9)
    def test_008_Configure_invalid_values_to_orphan_mode(self):
        print("Configure invalid values to orphan mode")
        request = ib_NIOS.wapi_request('GET', object_type="grid")
        request = json.loads(request)
        res_ref = request[0]['_ref']
        print(res_ref)
        data = {"ntp_setting": {"gm_local_ntp_stratum": 18, "local_ntp_stratum": 18}}
        request1 = ib_NIOS.wapi_request('PUT', object_type=res_ref, fields=json.dumps(data))
        if type(request1) == tuple:
            out = request1[1]
            out = json.loads(out)
            print(out)
            error_message = out['text']
            expected_error_message = "' The NTP local source stratum value must be between 2 and 15. The specified Grid Manager stratum value is 18, member value is 18.'"
            if error_message in expected_error_message:
                print("Expected Error message is seen")
                assert True
            else:
                print("Expected Error message is not seen")
                assert False
        else:
            print(request1)
            print(" The Invalid values configured successfully")
            assert False


    @pytest.mark.run(order=10)
    def test_009_Configure_higher_stratum_value_for_grid_master_and_expect_error(self):
        print("Configure higher stratum value for grid master and expect_error")
        request = ib_NIOS.wapi_request('GET', object_type="grid")
        request = json.loads(request)
        res_ref = request[0]['_ref']
        print(res_ref)
        data = {"ntp_setting": {"gm_local_ntp_stratum": 10, "local_ntp_stratum": 9}}
        request1 = ib_NIOS.wapi_request('PUT', object_type=res_ref, fields=json.dumps(data))
        if type(request1) == tuple:
            out = request1[1]
            out = json.loads(out)
            print(out)
            error_message = out['text']
            expected_error_message = "' NTP cluster local source stratum restriction: The Grid Manager stratum value must be less than the stratum value of any member. Specified Grid Manager stratum value is 10 and the member stratum value is 9.'"
            if error_message in expected_error_message:
                print("Expected Error message is seen")
                assert True
            else:
                print("Expected Error message is not seen")
                assert False
        else:
            print(request1)
            print(" The Invalid values configured successfully")
            assert False



    @pytest.mark.run(order=11)
    def test_010_Configure_negative_stratum_value_for_grid_master_and_expect_error(self):
        print("Configure negative stratum value for grid master and expect_error")
        request = ib_NIOS.wapi_request('GET', object_type="grid")
        request = json.loads(request)
        res_ref = request[0]['_ref']
        print(res_ref)
        data = {"ntp_setting": {"gm_local_ntp_stratum": -3, "local_ntp_stratum": -5}}
        request1 = ib_NIOS.wapi_request('PUT', object_type=res_ref, fields=json.dumps(data))
        if type(request1) == tuple:
            out = request1[1]
            out = json.loads(out)
            print(out)
            error_message = out['text']
            expected_error_message = "' Invalid value for gm_local_ntp_stratum: -3: Invalid value, must be between 0 and 4294967295'"
            if error_message in expected_error_message:
                print("Expected Error message is seen")
                assert True
            else:
                print("Expected Error message is not seen")
                assert False
        else:
            print(request1)
            print(" The Invalid values configured successfully")
            assert False


    @pytest.mark.run(order=12)
    def test_011_set_default_true(self):
        print("Enabling ntp orphan set to true")
        #print("Validate the default values present in orphan mode of grid master")
        request = ib_NIOS.wapi_request('GET', object_type="grid")
        request = json.loads(request)
        res_ref = request[0]['_ref']
        print(res_ref)
        data = {"ntp_setting": {'use_default_stratum':True}}
        request1 = ib_NIOS.wapi_request('PUT', object_type=res_ref, fields=json.dumps(data))
        print(request1)
        request1 = ib_NIOS.wapi_request('GET', object_type=res_ref, params='?_return_fields=ntp_setting')
        request1=json.loads(request1)

        default_local_ntp_value = request1['ntp_setting']['use_default_stratum']
        print(default_local_ntp_value)
        if default_local_ntp_value == True:
            print("set default value as True")
            assert True
        else:
            print("set default value as True")
            assert False

    @pytest.mark.run(order=13)
    def test_012_validate_orphan_values_16_and_16(self):

        request1 = ib_NIOS.wapi_request('GET', object_type="grid", params='?_return_fields=ntp_setting')
        print(request1)
        for row in json.loads(request1):
            if row['ntp_setting']["gm_local_ntp_stratum"]==13 and row['ntp_setting']["local_ntp_stratum"]==15:
                print("Sucess:Validating default value of grid")
                assert True

    @pytest.mark.run(order=14)
    def test_013_validate_last_orphan_values_through_cli(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        try:
            child.expect ('password.*:')
            child.sendline ('infoblox')
            child.expect ('Infoblox >',timeout=60)
            child.sendline('set maintenancemode')
            child.expect("Maintenance Mode > ")
            child.sendline ('show ntp_stratum')
            child.expect('Maintenance Mode >')
            #print(child.before)
            if 'GM NTP Orphan Mode stratum:    8' in child.before and 'Member NTP Orphan Mode stratum:    9' in child.before:
                print('Configured grid level NTP stratum values is 8 and 9')
            child.sendline('exit')
        except Exception as e:
            print("Failure: Execute command show ntp_stratum")
            print(e)
            assert False
        finally:
            child.close()




    @pytest.mark.run(order=15)
    def test_014_validate_orphan_values_16_and_16_through_cli(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        try:
            child.expect ('password.*:')
            child.sendline ('infoblox')
            child.expect ('Infoblox >',timeout=60)
            child.sendline('set maintenancemode')
            child.expect("Maintenance Mode > ")
            child.sendline ('set ntp_stratum')
            print("Use default NTP stratum settings?")
            child.expect ('y or n')
            child.sendline ('y\n')
            #print(child.before)
            print("The configured member NTP stratum value will be cleared")
            child.expect ('y or n')
            child.sendline ('y\n')
            print("The NTP service will restart now, Do you want to continue?")
            child.expect ('y or n')
            child.sendline ('y')
            print("--------------------------------")
            
            #print(child.before)
            child.expect('Maintenance Mode >')
            print(child.after)
            child.sendline ('show ntp_stratum')
            child.expect('Maintenance Mode >')
            print(child.before)
            if 'The lowest stratum value of a configured member is 15, the member id is 2' in child.before:
                print('Set NTP stratum default values through cli')
            child.sendline('exit')
        except Exception as e:
            print("Failure: Execute command set ntp_stratum")
            print(e)
            assert False
        finally:
            child.close()


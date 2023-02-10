import re
import config
import pytest
import unittest
import logging
import subprocess,signal
import os
import json
import ib_utils.ib_NIOS as ib_NIOS
from time import sleep
import commands
import json, ast
import requests
import time
import pexpect
import getpass
import sys

def get_reference_value_grid():
    logging.info("get reference value for GRID")
    get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
    logging.info(get_ref)
    res = json.loads(get_ref)
    print("**********************",res)
    ref1 = json.loads(get_ref)[0]['_ref']
    print("++++++++++++++++++++++",ref1)
    logging.info (ref1)
    return ref1

def get_snmp_settings():
    ref1=get_reference_value_grid()
    print("////////////////",ref1)
    logging.info("Get SNMP settings for GRID")
    get_ref = ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=snmp_setting")
    logging.info(get_ref)
    res = json.loads(get_ref)
    return res

def get_interface_value_snmp():
    ref1=get_reference_value_grid()
    print("////////////////",ref1)
    logging.info("Get interface settings for SNMP")
    get_ref = ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=updates_download_member_config")
    logging.info(get_ref)
    res = json.loads(get_ref)
    return res

class Network(unittest.TestCase):
    logging.basicConfig(filename='example.log', filemode='w', level=logging.DEBUG)

    @pytest.mark.run(order=1)
    def test_01_setting_values_snmp(self):
        ref1=get_reference_value_grid()
        logging.info ("Setting values for SNMP Setting")
        data={"snmp_setting":{"queries_community_string":"public","queries_enable":True,"trap_receivers":[{"address":config.grid_snmp_vip}],"traps_community_string":"public","traps_enable":True}}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
        print("&&&&&&&&&&&&&&&&&&&&&&&",response)
        logging.info(response)
        logging.info("============================")
        if (response[0]!=400):
            print("Value has been set successfully")
            assert True
        else:
            print("Incorrect values")
            assert False

    @pytest.mark.run(order=2)
    def test_02_setting_interface_snmp_lan1(self):
        ref1=get_reference_value_grid()
        logging.info ("Setting interface LAN1 for SNMP traces to source")
        data={"updates_download_member_config":[{"interface": "LAN1"}]}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
        print("&&&&&&&&&&&&&&&&&&&&&&&",response)
        logging.info(response)
        logging.info("============================")
        if (response[0]!=400):
            print("Interface LAN1 has been set successfully")
            assert True
        else:
            print("Incorrect values")
            assert False


    @pytest.mark.run(order=3)
    def test_03_collecting_mibs_lan1(self):
        #child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_snmp_vip)
        #child.logfile=sys.stdout
        #child.expect('password:')
        #child.sendline('infoblox')
        #child.expect('#')
        #child.sendline('cd /import/qaddi/QA/API/WAPI_PyTest/suites/RFE-8576')
        #child.expect('#')
        child = pexpect.spawn('perl snmp_trap.pl -i ' +str(config.grid_lan_vip)+ ' -t mibs -e positive')
        child.logfile=sys.stdout
	result = child.expect(['(Fail)','(Passed)'])
        if (result == '(Fail)'):
            child.expect('(Fail)')
            child.expect(pexpect.EOF)
        if (result == '(Passed)'):
            child.expect('(Passed)')
            child.expect(pexpect.EOF)
        child = pexpect.spawn('pkill -f snmptrapd')
       	child.logfile=sys.stdout
	child = pexpect.spawn('perl snmp_trap.pl -t start -e positive')
	child.logfile=sys.stdout
        result = child.expect(['(Fail)','(Passed)'])
        if (result == '(Passed)'):
            child.expect(pexpect.EOF)
        if (result == '(Fail)'):
            child.expect(pexpect.EOF)

    '''
    @pytest.mark.run(order=4)
    def test_04_collecting_snmpdtrapd_lan1(self):
        logging.info("Collecting SNMP Traps from LAN1 Port")
        logging.info("Starting SNMP Trap")
        snmp=config.grid_snmp_vip
        infoblox_log_validation = '"sshpass -p infoblox ssh -o StrictHostKeyChecking=no root@"'+snmp+'" "'+'"tail -20 /import/qaddi/QA/API/WAPI_PyTest/suites/RFE-8576/dump/snmptrapd.log"'
        out2 = commands.getoutput(infoblox_log_validation)
        print out2
        vip=(config.grid_vip)
        if re.search(vip,out2):
            print("Trap found")
            assert True
        else:
            print("Trap not found")
            assert False
    '''

    @pytest.mark.run(order=5)
    def test_05_setting_interface_snmp_mgmt(self):
        ref1=get_reference_value_grid()
        logging.info ("Setting interface MGMT for SNMP traces to source")
        data={"updates_download_member_config":[{"interface": "MGMT"}]}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
        print("&&&&&&&&&&&&&&&&&&&&&&&",response)
        logging.info(response)
        logging.info("============================")
        if (response[0]!=400):
            print("Interface MGMT has been set successfully")
            assert True
        else:
            print("Incorrect values")
            assert False


    @pytest.mark.run(order=6)
    def test_06_collecting_mibs_lan1(self):
        #child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@10.36.201.15')
        #child.logfile=sys.stdout
        #child.expect('password:')
        #child.sendline('infoblox')
        #child.expect('#')
        #child.sendline('cd /import/qaddi/QA/API/WAPI_PyTest/suites/RFE-8576')
        #child.expect('#')
        child = pexpect.spawn('perl snmp_trap.pl -i ' +str(config.grid_mgmt_vip)+ ' -t mibs -e positive')
        child.logfile=sys.stdout
	result = child.expect(['(Fail)','(Passed)'])
        if (result == '(Fail)'):
            child.expect('(Fail)')
            child.expect(pexpect.EOF)
        if (result == '(Passed)'):
            child.expect('(Passed)')
            child.expect(pexpect.EOF)
        child = pexpect.spawn('pkill -f snmptrapd')
	child.logfile=sys.stdout
        child = pexpect.spawn('perl snmp_trap.pl -t start -e positive')
	child.logfile=sys.stdout
        result = child.expect(['(Fail)','(Passed)'])
        if (result == '(Passed)'):
            child.expect(pexpect.EOF)
        if (result == '(Fail)'):
            child.expect(pexpect.EOF)


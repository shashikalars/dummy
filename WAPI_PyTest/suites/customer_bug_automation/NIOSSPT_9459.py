__author__ = "Ashwini C M"
__email__  = "cma@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master                                                                      #
#  2. Licenses : DNS, DHCP, Grid, NIOS(IB-V1415)                                                 
########################################################################################


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
#import requests
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
            sleep (10)


    @pytest.mark.run(order=3)
    def test_03_collecting_mibs_lan1(self):
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
            sleep (100)

    @pytest.mark.run(order=4)
    def test_004_start_IPv4_DNS_service(self):
            logging.info("start the ipv4 DNS service")
            get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
            logging.info(get_ref)
            res = json.loads(get_ref)
            for ref in res:
                ref1 = ref['_ref']
                print (ref1)
                data = {"enable_dns": True}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                sleep(10)
                logging.info(response)
                print (response)
            logging.info("Wait for 10 sec.,")
            sleep(100)
            print("Test Case 4 Execution Completed")
         
         
         
    @pytest.mark.run(order=5)
    def test_005_Add_Authoritative_zone(self):
            logging.info("Create Auth Zone")
            grid_member=config.grid_fqdn
            response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(auth_zone))
            print response
            read  = re.search(r'201',response)
            for read in  response:
                assert True
            logging.info("zone is created")
            logging.info("Create grid_primary with required fields")
            get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth")
            logging.info(get_ref)
            res = json.loads(get_ref)
            ref1 = json.loads(get_ref)[0]['_ref']
            print ref1

            data = {"grid_primary": [{"name": config.grid_fqdn,"stealth":False}]}
            response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
            logging.info(response)
            logging.info("============================")
            print response    

            logging.info("Restart services")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            print("System Restart is done successfully")
            sleep(300)
    
    @pytest.mark.run(order=06)
    def test_06_check_snmp_walk_swap_usage(self):
        logging.info("check snmpwalk output")
        try:
          child = pexpect.spawn ('ssh -o StrictHostKeyChecking=no '+config.client_user1+'@'+config.client_ip1)
          child.expect ('.*password:')
          child.sendline ('infoblox')
          child.logfile=sys.stdout
          child.expect ('.*$')
          child.sendline ('snmpwalk -v2c -c public -m ALL '+config.grid_vip+' infoblox >/tmp/snmp_walk_res')
          child.sendline ('cd /tmp')
          snmp_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+config.grid_vip+ "cat /tmp/snmp_walk_res | grep 'ibSystemMonitorSwapUsage'"
          out1 = commands.getoutput(snmp_cmd)
          print out1
          m = re.search(r'(.*)SwapUsage(.*)INTEGER\:(.*)',out1)
          res = m.group(3)
          print res
          if (int(res)==0):
             assert False
             print ("ibSystemMonitorSwapUsage cannot be Zero")
          else:
             print ("ibSystemMonitorSwapUsage is as expected")
        except:
             assert False
             logging.info("Testcase 6 is completed") 

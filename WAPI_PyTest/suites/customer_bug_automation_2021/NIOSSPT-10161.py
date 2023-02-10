#!/usr/bin/env python
__author__ = "Chanchal Sutradhar"
__email__  = "csutradhar@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Stand alone Grid Master                                               #
#  2. Licenses : IB-FLEX                                                    #
#############################################################################

#config_grid -g fr_automation -P ${POOL_DIR} -T ${GRID1_TAG_NAME} -F ${Build_Path_ddi} -Z -A B -M mgmt " -l IB-FLEX"

#Need to set the CPU as 8 and Memory as 22

#reboot_system -H $Master1_ID -a poweroff
#vm_specs -C 8 -M 22 -H $Master1_ID
#reboot_system -H $Master1_ID -a poweron

#Master1_IP=`sak.pl -P ${POOL_DIR} -T ${GRID1_TAG_NAME} -V master 'echo $MASTER_VIP'`
#Master1_ID=`sak.pl -P ${POOL_DIR} -T ${GRID1_TAG_NAME} -V master 'echo $UNIT_1_ID'`
#Master1_mgmt_IP=`sak.pl -P ${POOL_DIR} -T ${GRID1_TAG_NAME} -V master 'echo $UNIT_1_MGMT_IPADDR'`

#python run.py -m $Master1_mgmt_IP -v ${wapi_version}

#echo -e "master_lan1=\"$Master1_IP\"" >> config.py

import re
import commands
import config
import pytest
import unittest
import logging
import os
import json
import ib_utils.ib_NIOS as ib_NIOS
from time import sleep
import json
import time
import sys
import pexpect

#Wrapper to find the member reference string

def mem_ref(hostname):
    response = ib_NIOS.wapi_request('GET', object_type="member")
    logging.info(response)
    print(response)
    if type(response)!=tuple:
        ref1 = json.loads(response)
        for key in ref1:
            if key.get('host_name') == hostname:
                mem_ref = key.get('_ref')
                break
    else:
        print("Failed to get member DNS ref string")
        mem_ref = "NIL"

    return mem_ref

#wrepper to restart DNS service

def dns_restart(hostname):
    ref = mem_ref(hostname)
    data= {"restart_option":"FORCE_RESTART","service_option": "DNS"}
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
    sleep(60)
    print("DNS Restart Successfull")

#wrapper to perform product reboot

def prod_reboot(ip):
    child = pexpect.spawn('ssh admin@'+ip)
    child.logfile=sys.stdout
    child.expect('password:')
    child.sendline('infoblox')
    child.expect('Infoblox >')
    child.sendline('reboot')
    child.expect('REBOOT THE SYSTEM?')
    child.sendline('y')
    child.expect(pexpect.EOF)
    for i in range(1,20):
        sleep(60)
        status = os.system("ping -c1 -w2 "+ip)
        print(status)
        if status == 0:
            print("System is up")
            break
        else:
            print("System is still down..!!")
    sleep(10)
    print("Product Reboot successfull ..!!!")


class NIOSSPT_10161(unittest.TestCase):

        # Enable ADP on the standalone master
        @pytest.mark.run(order=1)
        def test_001_enable_ADP_on_standalone_master(self):
                logging.info("Enable ADP on the standalone master")
                data = {"enable_service": True}
                response = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
                logging.info(response)
                print(response)
                if type(response)!=tuple:
                    ref1 = json.loads(response)
                    for key in ref1:
                        if config.grid_member_fqdn in key.get('_ref'):
                            mem_ref = key.get('_ref')
                            print(mem_ref)
                            break
                response = ib_NIOS.wapi_request('PUT', object_type=mem_ref, fields=json.dumps(data))
                print(response)
                for i in range(1,20):
                    sleep(60)
                    status = os.system("ping -c1 -w2 "+config.grid_vip)
                    print(status)
                    if status == 0:
                        print("System is up")
                        break
                    else:
                        print("System is still down..!!")
                sleep(10)
                print("Product Reboot successfull ..!!!")
                if type(response)!=tuple:
                    print("ADP Enabled successfully")
                    logging.info("ADP Enabled successfully")
                    assert True
                else:
                    print("Failed to enable ADP on the Master")
                    logging.info("Failed to enable ADP")
                    assert False
        
        # Debug log verification for the above test case:

        @pytest.mark.run(order=2)
        def test_002_validate_debug_for_adp_configuration(self):
                logging.info("Validating debug logs for ADP configuration")
                sleep(30)
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -2000 /infoblox/var/infoblox.log"'
                out1 = commands.getoutput(sys_log_validation)
                logging.info (out1)
                res = re.search(r'Enabled Threat Protection service',out1)
                if res == None:
                    logging.info("Test Case Execution Completed and it failed")
                    assert False
                else:
                    logging.info("Test Case Execution Completed and it passed")
                    assert True

        # Create a zone test.com in default view
        @pytest.mark.run(order=3)
        def test_003_create_auth_zone(self):
                logging.info("Creating zone test.com")
                data={"fqdn": "test.com","grid_primary":[{"name":config.grid_fqdn}]}
                zone_ref=ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data))
                sleep(10)
                dns_restart(config.grid_fqdn)
                sleep(20)
                logging.info(zone_ref)
                if bool(re.match("\"zone_auth*.",str(zone_ref))):
                    logging.info("test.com created succesfully")
                    assert True
                else:
                    logging.info("test.com zone creation failed")
                    assert False

        # Validate the zone test.com in default view
        @pytest.mark.run(order=4)
        def test_004_validate_auth_zone(self):
                logging.info("Creating zone test.com")
                response=ib_NIOS.wapi_request('GET',object_type='zone_auth')
                logging.info(response)
                if type(response)!=tuple:
                    ref1 = json.loads(response)
                    for key in ref1:
                        if "test.com" in key.get('fqdn'):
                            logging.info("test.com created and validated")
                            assert True
                else:
                    logging.info("test.com zone creation failed")
                    assert False
                
        #perform a dig query with zflag set
        @pytest.mark.order(order=4)
        def test_004_validate_dns_response_with_zflag_set(self):
                message = "kdig @"+config.master_lan1+" test.com SOA +zflag"
                try:
                    op = os.popen(message)
                    h = op.read()
                    if "status: NOERROR" in h:
                        print("Successfully executed the test case !!")
                        logging.info("Got a succesful response with zflag set")
                        assert True
                    else:
                        print("Got a failed response with zflag set")
                        logging.info("Got a failed response with zflag set")
                        assert False
                except:
                    print("Got a failed response with zflag set")
                    logging.info("Got a failed response with zflag set")
                    assert False

        #Reverting all the changes
        @pytest.mark.order(order=5)
        def test_005_cleanup_all_changes(self):
                logging.info("Performing test cleanup")
                logging.info("Remove zone test.com")
                get_ref=ib_NIOS.wapi_request('GET',object_type='zone_auth')
                json_get_ref=json.loads(get_ref)
                for ref in json_get_ref:
                    if ref["fqdn"]=="test.com":
                        zone_ref=ref['_ref']
                        del_zone=ib_NIOS.wapi_request('DELETE',ref=zone_ref)
                        if bool(re.match("\"zone_auth*.",str(del_zone))):
                            logging.info("test.com deleted succesfully")
                            assert True
                        else:
                            logging.info("test.com zone deletion failed")
                            assert False
                
                logging.info("Disable ADP on the Standalone Master")
                data = {"enable_service": False}
                response = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
                logging.info(response)
                print(response)
                if type(response)!=tuple:
                    ref1 = json.loads(response)
                    for key in ref1:
                        if config.grid_member_fqdn in key.get('_ref'):
                            mem_ref = key.get('_ref')
                            print(mem_ref)
                            break
                response = ib_NIOS.wapi_request('PUT', object_type=mem_ref, fields=json.dumps(data))
                print(response)
                for i in range(1,20):
                    sleep(60)
                    status = os.system("ping -c1 -w2 "+config.grid_vip)
                    print(status)
                    if status == 0:
                        print("System is up")
                        break
                    else:
                        print("System is still down..!!")
                sleep(10)
                if type(response)!=tuple:
                    print("ADP Disabled successfully")
                    logging.info("ADP disable successfully")
                    assert True
                else:
                    print("Failed to disable ADP on the Master")
                    logging.info("Failed disable enable ADP")
                    assert False
                prod_reboot(config.grid_vip)





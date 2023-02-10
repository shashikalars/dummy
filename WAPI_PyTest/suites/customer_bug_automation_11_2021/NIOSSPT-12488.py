#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Vindya V K"
__email__  = "vvk@infoblox.com"

#############################################################################
# Grid Set up required:                                                     #
#  1. Grid Master + GMC + Member - 8.6.1 build    (LAN and MGMT)            #
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

#####################################################################################################
# STEPS TO REPRODUCE:                                                                               #
## (GM + M1 + M2)                                                                                   #
#                                                                                                   #
#   1. Make M1 as GMC                                                                               #
#   2. Start tcpdump on member eth1 and save it in a file - before_VPN_enabled.txt                  #
#   3. Perform GMC promotion test                                                                   #
#   4. Check for promotion status, once it is completed stop tcpdump on eth1                        #
#   5. Validate that the communication between GMC and M2 is through LAN interface only             #
#   6. Enable VPN on MGMT for member (M2) - give 5min sleep for reboot                              #
#   7. Start tcpdump on member eth0 and save it in a file - after_VPN_enabled.txt                   #
#   8. Perform GMC promotion test                                                                   #
#   9. Check for promotion status, once it is completed stop tcpdump on eth0                        #
#  10. Validate that the communication between GMC and M2 is through MGMT interface only            #
#                                                                                                   #
#####################################################################################################


class NIOSSPT_12488(unittest.TestCase):

# Make M1 as GMC
    @pytest.mark.run(order=1)
    def test_001_Make_member_as_GMC(self):
        print("\n========================================================\n")
        print("Make Member1 as Master candidate")
        print("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type='member', grid_vip=config.grid_vip)
        get_ref = json.loads(get_ref)[1]['_ref']

        data = {"master_candidate":True}
        response = ib_NIOS.wapi_request('PUT', ref=get_ref, fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)

        if type(response) == tuple:
            if response[0] == 400 or response[0] == 401:
                print("Failure: Make the member as Master candidate")
                assert False
            else:
                print("Success: Make the member as Master candidate")
                assert True

        print("\n***************. Test Case 1 Execution Completed .***************\n")


# Validating if the member is GMC or not
    @pytest.mark.run(order=2)
    def test_002_validate_member_as_GMC(self):
        print("\n========================================================\n")
        print("Validating if the member is Grid Master Candidate")
        print("\n========================================================\n")

        try:
            child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect("password:")
            child.sendline("infoblox")
            child.expect("Infoblox >")
            child.sendline('show status')
            child.expect("Infoblox >")
            output = child.before
            print(output)
            if "Master Candidate: true" in output:
                assert True
            else:
                assert False

        except Exception as e:
            print(e)
            child.close()
            assert False

        finally:
            child.close()

        print("\n***************. Test Case 2 Execution Completed .***************\n")


# Start tcpdump on member eth1 and save it in a file - before_VPN_enabled.txt
    @pytest.mark.run(order=3)
    def test_003_Start_tcpdump_on_member_eth1(self):
        print("\n============================================\n")
        print("Starting tcpdump on member eth1...")
        print("\n============================================\n")

        try:
            child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@'+config.grid_member2_vip)
            child.logfile=sys.stdout
            child.expect("-bash-5.0#")
            #child.sendline("tcpdump -i eth1 port 1194 or port 2114 -nn")
            #child.sendline("timeout 10 tcpdump -i eth1 port 1194 or port 2114 -nn --> a.txt ")
            child.sendline("nohup tcpdump -n -i eth1 port 1194 or port 2114 -nn > before.txt &")
            child.sendline("\r")
            child.expect("-bash-5.0#")
            assert True

        except Exception as e:
            print(e)
            #child.close()
            assert False

        finally:
            #child.close()
            print("Done")

        print("\n***************. Test Case 3 Execution Completed .***************\n")


# Perform GMC promotion test and validating
    @pytest.mark.run(order=4)
    def test_004_Perform_GMC_promotion_test(self):
        print("\n========================================================\n")
        print("Performing GMC promotion test")
        print("\n========================================================\n")

        logging.info("Validating the test connected status ")
        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        for i in range(1,10):
            child.sendline('set test_promote_master '+config.grid_member1_vip)
            child.expect('Enter Timeout \(>10 secs\) for test messages\(default 120 sec\): ')
            child.sendline('40')
            child.expect('\(y or n\): ')
            child.sendline('y')
            child.expect('Infoblox >')
            sleep(30)
            child.sendline('show test_promote_master status')
            child.expect('Infoblox >')
            output = child.before
            child.sendline('set test_promote_master stop')
            child.expect('\(y or n\): ')
            child.sendline('y')
            child.expect('Infoblox >')
            output=output.replace('\n','').replace(' ','').replace('[','').replace(']','').replace('\r','').replace('\t','')
            print("\n")
            print(output)
            if ('Connected' in output):
                print("Validated the Connected Status")
                assert True
                break
            else:
                continue
            print("Trying again to get Connected Status")
            assert False
        print("\n***************. Test Case 4 Execution Completed .***************\n")


# Stopping/killing the tcpdump process
    @pytest.mark.run(order=5)
    def test_005_stop_tcp_dump(self):
        print("\n========================================================\n")
        print("Stopping tcp dump")
        print("\n========================================================\n")

        try:
            child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@'+config.grid_member2_vip)
            child.logfile=sys.stdout
            child.expect("-bash-5.0#")
            child.sendline("ps -ax | grep 'tcpdump'")
            child.expect("-bash-5.0#")
            output = child.before
            output=output.split('\n')
            process_id=output[2].split(' ')[0]
            print(process_id)
            child.sendline("kill -9 "+str(process_id))
            child.expect("-bash-5.0#")
            assert True

        except Exception as e:
            print(e)
            child.close()
            assert False

        finally:
            child.close()

        print("\n***************. Test Case 5 Execution Completed .***************\n")


# Validate that the communication between GMC and M2 is through LAN interface only
    @pytest.mark.run(order=6)
    def test_006_Validate_comm_through_LAN(self):
        print("\n========================================================\n")
        print("Validating communication between GMC and M2")
        print("\n========================================================\n")

        try:
            child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@'+config.grid_member2_vip)
            child.logfile=sys.stdout
            child.expect("-bash-5.0#")
            child.sendline("grep -c '"+config.grid_member1_vip+"' before.txt")
            child.expect("-bash-5.0#")
            output = child.before
            output=output.split('\n')[1].strip("\r")
            print(output)
            if int(output)>0:
                print("Communication between GMC and M2 is taking place through LAN interface only")
                assert True
            else:
                print("Something went wrong...communication is no taking place through LAN interface!")
                assert False

        except Exception as e:
            print(e)
            child.close()
            assert False

        finally:
            child.close()

        print("\n***************. Test Case 6 Execution Completed .***************\n")


# Enable VPN on MGMT for member (M2) - give 5min sleep for reboot
    @pytest.mark.run(order=7)
    def test_007_Enable_VPN_on_MGMT(self):
        print("\n========================================================\n")
        print("Enabling VPN on MGMT for member")
        print("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type='member', grid_vip=config.grid_vip)
        get_ref = json.loads(get_ref)[2]['_ref']

        data = {"host_name":config.grid_member2_fqdn, "mgmt_port_setting":{"vpn_enabled":True}}
        response = ib_NIOS.wapi_request('PUT', ref=get_ref, fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)

        if type(response) == tuple:
            if response[0] == 400 or response[0] == 401:
                print("Failure: VPN on MGMT is NOT enabled")
                assert False
            else:
                print("Success: VPN on MGMT is enabled")
                assert True
        sleep(180)

        print("\n***************. Test Case 7 Execution Completed .***************\n")


# Validating if VPN on MGMT is enabled
    @pytest.mark.run(order=8)
    def test_008_Validate_VPN_on_MGMT(self):
        print("\n========================================================\n")
        print("Validating VPN on MGMT")
        print("\n========================================================\n")

        response = ib_NIOS.wapi_request('GET', object_type="member?_return_fields=mgmt_port_setting", grid_vip=config.grid_vip)
        response=json.loads(response)[2]
        print(response)

        for ref in response['mgmt_port_setting']:
            if ref==True:

                print("SUCCESS: Validated VPN on MGMT enabled")
                assert True
                break
            else:
                continue
                print("FAILURE: VPN on MGMT is not enabled")
                assert False

        print("\n***************. Test Case 8 Execution Completed .***************\n")


# Start tcpdump on member eth0 and save it in a file - after_VPN_enabled.txt
    @pytest.mark.run(order=9)
    def test_009_Start_tcpdump_on_member_eth0(self):
        print("\n============================================\n")
        print("Starting tcpdump on member eth0...")
        print("\n============================================\n")

        try:
            child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@'+config.grid_member2_vip)
            child.logfile=sys.stdout
            child.expect("-bash-5.0#")
            #child.sendline("tcpdump -i eth0 port 1194 or port 2114 -nn --> after_VPN_enabled.txt",timeout=10)
            child.sendline("nohup tcpdump -n -i eth0 port 1194 or port 2114 -nn > after.txt &")
            child.expect("-bash-5.0#") 

        except Exception as e:
            print(e)
            child.close()
            assert False

        finally:
            child.close()

        print("\n***************. Test Case 9 Execution Completed .***************\n")


# Perform GMC promotion test and validating
    @pytest.mark.run(order=10)
    def test_010_Perform_GMC_promotion_test(self):
        print("\n========================================================\n")
        print("Performing GMC promotion test")
        print("\n========================================================\n")

        logging.info("Validating the test connected status ")
        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        for i in range(1,10):
            child.sendline('set test_promote_master '+config.grid_member1_vip)
            child.expect('Enter Timeout \(>10 secs\) for test messages\(default 120 sec\): ')
            child.sendline('40')
            child.expect('\(y or n\): ')
            child.sendline('y')
            child.expect('Infoblox >')
            sleep(30)
            child.sendline('show test_promote_master status')
            child.expect('Infoblox >')
            output = child.before
            child.sendline('set test_promote_master stop')
            child.expect('\(y or n\): ')
            child.sendline('y')
            child.expect('Infoblox >')
            output=output.replace('\n','').replace(' ','').replace('[','').replace(']','').replace('\r','').replace('\t','')
            print("\n")
            print(output)
            if ('Connected' in output):
                print("Validated the Connected Status")
                break
            else:
                continue
            print("Trying again to get Connected Status")

        print("\n***************. Test Case 10 Execution Completed .***************\n")


# Stopping/killing the tcpdump process
    @pytest.mark.run(order=11)
    def test_011_stop_tcp_dump(self):
        print("\n========================================================\n")
        print("Stopping tcp dump")
        print("\n========================================================\n")

        try:
            child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@'+config.grid_member2_vip)
            child.logfile=sys.stdout
            child.expect("-bash-5.0#")
            child.sendline("ps -ax | grep 'tcpdump'")
            child.expect("-bash-5.0#")
            output = child.before
            output=output.split('\n')
            process_id=output[2].split(' ')[0]
            print(process_id)
            child.sendline("kill -9 "+str(process_id))
            child.expect("-bash-5.0#")

        except Exception as e:
            print(e)
            child.close()
            assert False

        finally:
            child.close()

        print("\n***************. Test Case 11 Execution Completed .***************\n")


# Validate that the communication between GMC and M2 is through MGMT interface only
    @pytest.mark.run(order=12)
    def test_012_Validate_comm_through_MGMT(self):
        print("\n========================================================\n")
        print("Validating communication between GMC and M2")
        print("\n========================================================\n")

        try:
            child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@'+config.grid_member2_vip)
            child.logfile=sys.stdout
            child.expect("-bash-5.0#")
            child.sendline("grep -c '"+config.grid_member1_vip+"' after.txt")
            child.expect("-bash-5.0#")
            output = child.before
            output=output.split('\n')[1].strip("\r")
            print(output)
            if int(output) > 0:
                print("Communication between GMC and M2 is taking place through MGMT interface only")
                assert True
            else:
                print("Something went wrong...communication is no taking place through MGMT interface!")
                assert False

        except Exception as e:
            print(e)
            child.close()
            assert False

        finally:
            child.close()

        print("\n***************. Test Case 12 Execution Completed .***************\n")


### cleanup function

    @pytest.mark.run(order=13)
    def test_013_cleanup_objects(self):
        print("\n============================================\n")
        print("CLEANUP: Reverting back to original setup...")
        print("\n============================================\n")

        print("Disabling VPN on MGMT...")

        get_ref = ib_NIOS.wapi_request('GET', object_type='member', grid_vip=config.grid_vip)
        get_ref = json.loads(get_ref)[2]['_ref']

        data = {"host_name":config.grid_member2_fqdn, "mgmt_port_setting":{"vpn_enabled":False}}
        response = ib_NIOS.wapi_request('PUT', ref=get_ref, fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)

        sleep(120)

        print("\n***************. Test Case 13 Execution Completed .***************\n")


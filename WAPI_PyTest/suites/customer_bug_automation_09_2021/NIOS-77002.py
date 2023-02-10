#!/usr/bin/env python
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. SA configuration                                                      #
#  2. M1 License : DNS,DHCP,NIOS                                            #
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
from time import sleep as sleep
import ib_utils.ib_NIOS as ib_NIOS
import pexpect
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv


class NIOS_77002(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_perform_traffic_capture_on(self):
        child=pexpect.spawn("ssh root@"+config.client_ip,  maxread=4000)
        child.expect('password:',timeout=80)
        child.sendline("infoblox\n")
        try:

            child.expect("#",timeout=100)
            child.sendline("useradd testing \n")
            child.expect('#',timeout=100)
            child.sendline("passwd testing")
            child.expect("New password:")
            #child.sendline("Test@.-_/!$#")
            child.sendline("Test@.-_/!$(),&:@#~*[]={}`^+?%")
            child.expect("Retype new password:")
            #child.sendline("Test@.-_/!#")
            child.sendline("Test@.-_/!$(),&:@#~*[]={}`^+?%")
            child.expect('#',timeout=100)
            if 'passwd: all authentication tokens updated successfully' in child.before:
                print("\nSuccess: created user")
            child.close()
            assert True

        except Exception as e:
            child.close()
            print (e)
            print("Failure: not able to create user")
            assert False

        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        print("perform traffic_capture ON through cli ")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        try:
            child.expect ('password.*:')
            child.sendline ('infoblox')
            child.expect ('Infoblox >',timeout=60)
            child.sendline('set traffic_capture on')
            child.expect("Infoblox >")
            first_va=child.before
            #print(child.after)
            print(first_va)
            print('------------------')
           
            child.sendline ('set traffic_capture transfer scp '+config.client_ip+' testing - /tmp/mycapture.tar.gz')
            #child.expect('Infoblox >')
            child.expect('Enter password:')
            
            child.sendline('Test@.-_/!$(),&:@#~*[]={}`^+?%')
            
            child.expect('Infoblox >')            
             
            if 'Traffic capture started successfully' in first_va and 'traffic capture is currently running' in child.before:
                print('Traffic capture started successfully')
                child.sendline('exit')
                assert True
            else:
                assert False
        except Exception as e:
            print("Failure: Traffic capture could not start")
            print(e)
            assert False
        finally:
            child.close()

    @pytest.mark.run(order=2)
    def test_001_perform_traffic_capture_off(self):
        print("perform traffic_capture oFF through cli")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        try:
            child.expect ('password.*:')
            child.sendline ('infoblox')
            child.expect ('Infoblox >',timeout=60)
            child.sendline('set traffic_capture off')
            child.expect("Infoblox >")
            first_va=child.before
            print(first_va)
            print('------------------')
            
            child.sendline ('set traffic_capture transfer scp '+config.client_ip+' testing - /tmp/mycapture.tar.gz')
            child.expect('Enter password:')
            
            child.sendline('Test@.-_/!$(),&:@#~*[]={}`^+?%')
            
            child.expect ('y or n')
            child.sendline ('y')
            sleep(20)
            print("___________________")

            child.expect('Infoblox >')
            print(child.before)
            if 'Traffic capture stopped successfully' in first_va and 'is uploaded to scp server '+config.client_ip+' successfully' in child.before:
                print('Traffic capture stopped successfully')
                child.sendline('exit')
                assert True
            else:
                assert False
        except Exception as e:
            print("Failure: Traffic capture could not sto, bug opned: NIOS-80990")
            print(e)
            assert False
        finally:
            child.close()



    @pytest.mark.run(order=3)
    def test_002_perform_transfer_supportbundle(self):
        print("perform transfer_supportbundle through cli ")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        try:
            child.expect ('password:')
            child.sendline ('infoblox')
            child.expect ('Infoblox >',timeout=60)
            print('------------------')
            
            child.sendline ('set transfer_supportbundle scp '+config.client_ip+' testing - dest /tmp/mycapture.tar.gz')
            child.expect('Enter password:')
            
            child.sendline('Test@.-_/!$(),&:@#~*[]={}`^+?%')
            child.expect ('y or n')
            child.sendline ('y')
            sleep(30)
            
            child.expect('Infoblox >')
            print(child.before)
            print("^^^^^^^^^^^^^^^^^^^^^^^")
            if 'supportBundle is uploaded to scp server '+config.client_ip+' successfully' in child.before:
                print('Success: supportBundle is uploaded successfully')
                assert True
            else:
                assert False
            child.sendline('exit')
        except Exception as e:
            print("Failure: supportBundle is not uploaded ,bug opned: NIOS-80990")
            print(e)
            assert False
        finally:
            child.close()

    @pytest.mark.run(order=4)
    def test_003_check_password_is_not_shown_in_logs(self):

        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        logs=logv(".*testing.*password suppressed.*","/infoblox/var/infoblox.log",config.grid_vip)
        print(logs)
        if logs:
            assert True
        else:
            assert False
          


    @pytest.mark.run(order=5)
    def test_004_perform_set_hotfix(self):
        print("perform set hotfix cmd")
        print(config.grid_vip)
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        try:
            child.expect ('password.*:')
            child.sendline ('infoblox')
            child.expect ('Infoblox >',timeout=60)
            child.sendline('set maintenancemode')
            child.expect("Maintenance Mode > ")
            
            child.sendline ('set hotfix '+config.client_ip+' /import/qaddi/santhosh/Dummy-hotfix/Hotfix-DEBUG-ON.bin scp testing -')
            child.expect('Enter password:')
            
            child.sendline('Test@.-_/!$(),&:@#~*[]={}`^+?%')
            child.expect ('y or n')
            child.sendline ('y')
            sleep(20)
            
            child.expect('Maintenance Mode >')

            if 'Successfully downloaded hotfix image' in child.before:
                print('Success: Successfully downloaded hotfix image')
                assert True
            else:
                assert False
            child.sendline('exit')
           
        except Exception as e:
            print("Failure: Could not Successfully download hotfix image, bug opned: NIOS-80990")
            print(e)
            assert False
        finally:
            child.close()
        
            child=pexpect.spawn("ssh root@"+config.client_ip,  maxread=4000)
            child.expect('password:',timeout=80)
            child.sendline("infoblox\n")
            try:

                child.expect("#",timeout=100)
                child.sendline("userdel -r testing \n")
                child.expect('#',timeout=100)
                print("\nSuccess: deleted user")
                child.close()
                assert True

            except Exception as e:
                child.close()
                print (e)
                print("Failure: not able to delete user")
                assert False






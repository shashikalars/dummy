#!/usr/bin/env python
__author__ = "Manoj Kumar R G"
__email__  = "mgovarthanan@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Grid Master                                                           #
#  2. Licenses : IB-V1415
#############################################################################

import re
import config
#import config1
import pytest
import subprocess
import unittest
import logging
#import subprocess
import os
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import commands
import json, ast
import requests
import time
import pexpect
import getpass
import paramiko
import shlex
from subprocess import Popen, PIPE
import sys
from paramiko import client
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv

auth_zone={"fqdn": "test123.com"}

class ConnectionError:
    print("Check for SSH connection")

class SSH:
    client = None

    def __init__(self, address):
        print("connecting to server \n : ", address)
        self.client = client.SSHClient()
        self.client.set_missing_host_key_policy(client.AutoAddPolicy())
        self.client.load_system_host_keys()
        self.client.connect(address, username='root', port=22)

    def send_command(self, command):
        if (self.client):
            stdin, stdout, stderr = self.client.exec_command(command)
            result = stdout.read()
            print(result)
            error = stderr.read()
            print(error)
            return result
        else:
            print("Connection not opened.")


def log_validation(grid_vip,lookfor_list,file_path="/infoblox/var/infoblox.log"):
    try:
    	conf_details = []
        connection = SSH(config.grid_vip)
        for look in lookfor_list:
            command1="tail -50 " +str(file_path) + "| grep -i "+'"' + str(look)+'"'
            print (command1)
            result = connection.send_command(command1)
            #print (conf_details)
	    conf_details.append(result)
        return conf_details
    except ConnectionError:
        print ("Connection failed ")


class Network(unittest.TestCase):          

      @pytest.mark.run(order=1)
      def test_01_emergency_prompt_commands(self):

          logging.info("Not performing reset_storage in Emergency mode")
	  os.system("/import/tools/lab/bin/reset_console -H "+config.vm_id+" -c "+config.user)
          child = pexpect.spawn("console_connect -H "+config.vm_id,  maxread=4000)
          try:
                #child.sendline("\r")
                child.expect(".*Escape character is .*",timeout=100)
                #child.expect(".*Disconnect NOW if you have not been .*",timeout=100)
                child.sendline("\r")
                child.expect(".*login:",timeout=100)
                child.sendline("admin")
                child.expect('password:',timeout=100)
                child.sendline("infoblox")
                child.expect("Infoblox >")

                child.sendline('reboot')
                #child.expect('\(y or n\): ')
                child.expect("REBOOT THE SYSTEM\? \(y or n\)\: ")
                #child.expect('.*REBOOT THE SYSTEM?.*')
                #child.send('y\n')
                child.sendline('y')
                #child.send('\n')

                str1=".*Hit \"Esc\" and \"Enter\" now for Emergency prompt.*"
                child.expect(str1, timeout=800) #Expecting str1 line for 800sec
                child.send(chr(27))             #Press "ESC"
                child.send('\r')                #Press "Enter"

                child.expect('Emergency>')  #Entering Emergency mode
                child.sendline("reset")
                child.expect('.*reset all .*licenses.*.*reset database.*reset ssh_keys.*reset reporting_data.*Emergency>',timeout=100)

                child.sendline("reset all licenses")
                #child.sendline("")
                child.expect('.*WARNING: THIS WILL ERASE ALL DATA AND LOG FILES THAT HAVE.*BEEN CREATED ON THIS SYSTEM.*ARE YOU SURE YOU WANT TO PROCEED\? \(y or n\)\:',timeout=100)
                #child.sendline("\n")
                child.sendline("n")
                child.send('\n')
                child.expect('Emergency>',timeout=100)
                child.sendline('reset database')
                child.expect('.*WARNING: THIS WILL ERASE THE DATABASE ON THIS SYSTEM.*ARE YOU SURE YOU WANT TO PROCEED\? \(y or n\)\:',timeout=100)
                child.sendline("n")
                child.send('\n')
                child.expect('Emergency>',timeout=30)
                child.sendline('reset ssh_keys')
                child.expect('.*WARNING: THIS WILL RESET THE SYSTEM.*SSH KEYS.*ARE YOU SURE YOU WANT TO PROCEED\? \(y or n\)\:',timeout=100)
                child.sendline("n")
                child.send('\n')
                child.expect('Emergency>',timeout=30)
                child.sendline('reset reporting_data')
                child.expect('.*WARNING: THIS WILL RESET ALL REPORTING DATA.*DO YOU WANT TO PROCEED\? \(y or n\)\:',timeout=100)
                child.sendline("n")
                child.send('\n')
                child.expect('Emergency>',timeout=30)
                child.sendline('version')
                child.expect('.*Version.*SN.*Hotfix.*Emergency>',timeout=30)
                child.sendline('help')
                child.expect('.*help.*reset.*version.*exit.*set.*For more detailed help about a given command, type.*help \<command\>.*Emergency>',timeout=100)
	 	child.sendline('set weak')
		child.expect("Weak enforcement\? \(y or n\)\: ")
		child.sendline("n")
		child.send('\n')
		child.expect('Emergency>',timeout=30)
                child.sendline('set fsck')
                child.expect("\? \(y or n\)\: ")
                child.sendline("n")
		child.expect("\(y or n\)\: ")
		child.sendline("n")
                child.send('\n')
                child.expect('Emergency>',timeout=30)
                child.sendline('set watchdog')
                child.expect("Enable Watchdog \? \(y or n\)\: ")
                child.sendline("n")
                child.expect("\(y or n\)\: ")
                child.sendline("n")
                child.send('\n')
                child.expect('Emergency>',timeout=30)
                child.sendline('set repsafe_mode')
                child.expect('.*set repsafe_mode \[ on \| off \].*Emergency>',timeout=100)
		child.sendline('set safemode')
		child.expect('Emergency>',timeout=30)
		str2 = ".*Continuing with system startup.*"	
                child.sendline('exit')
		child.expect(str2,timeout=30)
		child.expect(".*login:",timeout=120)
		assert True	
      
          except Exception as e:
                #child.close()
                print (e)
                #child.sendline("exit")
                child.expect(".*login:",timeout=1200)
		child.close()
                os.system("/import/tools/lab/bin/reset_console -H "+config.vm_id+" -c "+config.user)
                sleep(20)
                assert False


          finally:
                child.close()
                os.system("/import/tools/lab/bin/reset_console -H "+config.vm_id+" -c "+config.user)
                sleep(20)


      @pytest.mark.run(order=2)
      def test_02_validate_safemode(self):

          logging.info("Validating safemode functionality")

          lookfor_list=["No DHCP service running - IN SAFE MODE","No DNS service running - IN SAFE MODE"]
          log_validation_result=log_validation(config.grid_vip,lookfor_list)
          print("log_validation_result data check here :", log_validation_result)
          if (log_validation_result == ''):
              assert False
              print ("log validation failed ")
          else:
              assert True
              print ("Log validation passed")


      @pytest.mark.run(order=3)
      def test_03_create_New_AuthZone(self):
          sleep(30)
	  logging.info("Create A new Zone")
          response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(auth_zone))
          print response
          logging.info(response)
          read  = re.search(r'201',response)
          for read in response:
              assert True
              logging.info("Test Case 3 Execution Completed")

      @pytest.mark.run(order=4)
      def test_04_create_grid_primary_for_zone(self):
          logging.info("Create grid_primary with required fields")
          get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=test123.com")
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
          sleep(10)
          request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
          restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
          sleep(20)
          logging.info("Test Case 4 Execution Completed")

      @pytest.mark.run(order=5)
      def test_05_create_A_record(self):
          logging.info("Create A record")
          data={"name":"arec."+auth_zone['fqdn'],"ipv4addr":"3.3.3.3","view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data))
          if (response[0]!=400):
              print ("Added A record")
          else:
              print ("A record already exists")
          logging.info("Test Case 5 Execution Completed")


      @pytest.mark.run(order=5)
      def test_05_modify_log_queries(self):
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
          logging.info(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print ref1

          logging.info("Modify a  log_queries")
          data1 = {"logging_categories":{"log_queries": True}}
          data2 = {"logging_categories":{"log_responses": True}}
          data3 = {"logging_categories":{"log_dtc_gslb": True}}
          data4 = {"logging_categories":{"log_dtc_health": True}}
          response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data1))
          response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data2))
          response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data3))
          response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data4))
          #print response
          logging.info(response)
          read  = re.search(r'200',response)
          for read in response:
              assert True
          logging.info("Restart services")
          grid =  ib_NIOS.wapi_request('GET', object_type="grid")
          ref = json.loads(grid)[0]['_ref']
          publish={"member_order":"SIMULTANEOUSLY"}
          request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
          sleep(10)
          request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
          restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
          sleep(10)
          logging.info("Test Case 5 Execution Completed")
          sleep(10)

      @pytest.mark.run(order=6)
      def test_06_validate_dig_safemode(self):
          logging.info("Perform query for A record while safemode is ON")
          dig_cmd = 'dig @'+str(config.grid_vip)+' arec.test123.com IN A'
          dig_cmd1 = os.system(dig_cmd)
          logging.info("Validate Syslog after perform queries")
          sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -5 /var/log/syslog | grep  \'arec.test123.com. 28800 IN A 3.3.3.3\'"'
          out1 = commands.getoutput(sys_log_validation)
          print out1
          logging.info(out1)
          final = re.search(r'arec.test123.com. 28800 IN A 3.3.3.3',out1)
	  if final is None:
	      logging.info("Test case 6 passed")
	      assert True
	  else:
	      logging.info("Test case 6 Failed")
	      assert False
          sleep(20)


      @pytest.mark.run(order=7)
      def test_07_validate_nosafemode(self):

	  logging.info("Validating nosafemode functionality")
          os.system("/import/tools/lab/bin/reset_console -H "+config.vm_id+" -c "+config.user)
	  child = pexpect.spawn("console_connect -H "+config.vm_id,  maxread=4000)
          child.expect(".*Escape character is .*",timeout=100)
          child.sendline("\r")
          child.expect(".*login:",timeout=100)
          child.sendline("admin")
          child.expect('password:',timeout=100)
          child.sendline("infoblox")
          child.expect("Infoblox >")
          child.sendline('reboot')
          child.expect("REBOOT THE SYSTEM\? \(y or n\)\: ")
          child.sendline('y')
          str1=".*Hit \"Esc\" and \"Enter\" now for Emergency prompt.*"
          child.expect(str1, timeout=800) #Expecting str1 line for 800sec
          child.send(chr(27))             #Press "ESC"
          child.send('\r')                #Press "Enter"

          child.expect('Emergency>')  #Entering Emergency mode

          child.sendline('set nosafemode')
          child.expect('Emergency>',timeout=30)
          child.sendline('exit')
          child.expect(".*login:",timeout=120)
          child.close()
	  sleep(20)
          lookfor_list=["DNS Service is working","DHCP Service is working"]
          log_validation_result=log_validation(config.grid_vip,lookfor_list)
          print("log_validation_result data check here :",log_validation_result)
          if (log_validation_result == ''):
              assert False
              print ("log validation failed")
          else:
              assert True
              print ("Log validation passed")

      @pytest.mark.run(order=8)
      def test_08_validate_dig_no_safemode(self):
	  sleep(30)
          logging.info("Perform query for A record while nosafemode is ON")
          dig_cmd = 'dig @'+str(config.grid_vip)+' arec.test123.com IN A'
          dig_cmd1 = os.system(dig_cmd)
          logging.info("Validate Syslog after perform queries")
          sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -10 /var/log/syslog | grep  \'arec.test123.com. 28800 IN A 3.3.3.3\'"'
          out1 = commands.getoutput(sys_log_validation)
          print out1
          logging.info(out1)
          final = re.search(r'arec.test123.com. 28800 IN A 3.3.3.3',out1)
          if final is not None:
              logging.info("Test case 8 passed")
              assert True
          else:
              logging.info("Test case 8 Failed")
              assert False
          sleep(20)


      @pytest.mark.run(order=9)
      def test_09_validate_cleanup(self):
          logging.info("Perform cleanup by deleting zone and record")
          ref_record = ib_NIOS.wapi_request('GET',object_type="record:a?name=arec.test123.com")
          logging.info(ref_record)
          ref_rec=json.loads(ref_record)[0]['_ref']
          logging.info("Deleting A record")
          ref_del= ib_NIOS.wapi_request('DELETE',ref=ref_rec)
          print("**********DELETED A REC***********",ref_del)
          ref_zone = ib_NIOS.wapi_request('GET',object_type="zone_auth?fqdn=test123.com")
          logging.info(ref_zone)
          ref_zzz=json.loads(ref_zone)[0]['_ref']
          logging.info("Deleting zone")
          ref_del1= ib_NIOS.wapi_request('DELETE',ref=ref_zzz)
          print("**********DELETED A ZONE***********",ref_del1)

          logging.info("Restart services")
          grid =  ib_NIOS.wapi_request('GET', object_type="grid")
          ref = json.loads(grid)[0]['_ref']
          publish={"member_order":"SIMULTANEOUSLY"}
          request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
          sleep(10)
          request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
          restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
          sleep(20)
          print("Cleanup is processed")
 

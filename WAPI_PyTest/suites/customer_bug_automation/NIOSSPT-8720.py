__author__ = "Prasad K"
__email__  = "pkondisetty@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master                                                                      #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415)                                      #
########################################################################################

import re
import pexpect
import sys
import config
import pytest
import unittest
import logging
import os
import os.path
from os.path import join
import subprocess
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util
#import pexpect
#from log_capture import log_action as log
#from log_validation import log_validation as logv

class Network(unittest.TestCase):

      @pytest.mark.run(order=01)
      def test_001_Upload_Cisco_ISE_Server_CA_Certificate(self):
          logging.info("Upload Cisco ISE Server CA Certificate")
          dir_name="certificate/"
          base_filename="myCA_cert.pem"
          token = common_util.generate_token_from_file(dir_name,base_filename)
          print (token)
          data = {"token": token, "certificate_usage":"EAP_CA"}
          response = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=uploadcertificate")
          logging.info("Test Case 1 Execution Completed")
          sleep(30)


      @pytest.mark.run(order=2)
      def test_002_adding_Cisco_ISE_Server_CA_Certificate(self):
           logging.info("adding Cisco ISE server CA certificate")
           data = { "auto_populate_login": "S_DN_CN","name": "test","ocsp_check": "DISABLED","user_match_type": "DIRECT_MATCH","client_cert_subject" : "grid","ca_certificates":["cacertificate/b25lLmVhcF9jYV9jZXJ0JDAuNWJmYmE0NGY2ZjJmZjU1YmI1MzkyYWIzYWMzZTk2NTVkM2ViYmNmMzdkMWFkNTAxMWIzZDFhNTI1N2MzMzdkOWZjZGUyODk0MGI3ZmM3MzA3OTI1NjcyMjAyNWQ4M2U0ODc5OWMwYTBmODMyOTQ4OTBkYzBhNzc3ZTRkNGI5ZDA:CN%3D%22ca.gnidoni-vm.inca.infoblox.com%22"]}
           response = ib_NIOS.wapi_request('POST', object_type="certificate:authservice", fields=json.dumps(data), grid_vip=config.grid_vip)
           print (response)
           sleep(30)
           print("Test Case 2 Execution Completed")



      @pytest.mark.run(order=3)
      def test_003_adding_Authentication_Policy(self):
          logging.info("Adding Authentication Policy")
          get_ref = ib_NIOS.wapi_request('GET', object_type="authpolicy", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref = json.loads(get_ref)[0]['_ref']
          print("authpolicy reference",ref)
          data = {"auth_services":["localuser:authservice/Li5sb2NhbF91c2VyX2F1dGhfc2VydmljZSQy:Local%20Admin","certificate:authservice/b25lLm9jc3BfYXV0aF9zZXJ2aWNlJHRlc3Q:test"]}
          output = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(30)
          print("Test Case 3 Execution Completed")



      @pytest.mark.run(order=4)
      def test_004_checking_the_ssl_reneg_buffer_size(self):
          logging.info("checking the ssl_reneg_buffer_size")
          child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
          child.logfile=sys.stdout
          child.expect('password:')
          child.sendline('infoblox')
          child.expect('Infoblox >')
          child.sendline('show ssl_reneg_buffer_size')
          child.expect('Infoblox >')
          output = child.before
          print(output)
          assert re.search(r'size = 131072 bytes',output)
          sleep(30)
          print("\nTest Case 04 Executed Successfully")

      @pytest.mark.run(order=5)
      def test_005_increasing_the_ssl_reneg_buffer_size(self):
          logging.info("increasing the ssl_reneg_buffer_size")
          child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
          child.logfile=sys.stdout
          child.expect('password:')
          child.sendline('infoblox')
          child.expect('Infoblox >')
          child.sendline('set ssl_reneg_buffer_size 2048000000')
          child.expect('Infoblox >')
          child.sendline('show ssl_reneg_buffer_size')
          child.expect('Infoblox >')
          output = child.before
          print(output)
          assert re.search(r'size = 2048000000 bytes',output)
          sleep(30)
          print("\nTest Case 05 Executed Successfully")



      @pytest.mark.run(order=6)
      def test_006_rebooting_the_grid(self):
          logging.info("rebooting the grid")
          child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
          child.logfile=sys.stdout
          child.expect('password:')
          child.sendline('infoblox')
          child.expect('Infoblox >')
          child.sendline('reboot')
          child.expect('\(y or n\): ')
          child.sendline('y')
          #child.expect('Infoblox >')
          #output = child.before
          sleep(300)
          #return child.before
          print("\nTest Case 06 Executed Successfully")
       
      @pytest.mark.run(order=7)
      def test_007_Add_Authoritative_zone(self):
           logging.info("Add Authoritative zone")
           #data = {"fqdn": "test.com","view": "default","grid_primary":[{"name":"ib-10-35-196-6.infoblox.com"}]}
           data = {"fqdn": "test.com","view": "default","grid_primary":[{"name":config.grid_fqdn}]}
           response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data),grid_vip=config.grid_vip)
           print(response)
           res = json.loads(response)
           read  = re.search(r'201',response)
           for read in  response:
                   assert True
           sleep(30)
           logging.info("Restart services")
           grid =  ib_NIOS.wapi_request('GET', object_type="grid")
           ref = json.loads(grid)[0]['_ref']
           publish={"member_order":"SIMULTANEOUSLY"}
           request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
           request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
           restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
           print("System Restart is done successfully")
           sleep(30)
           print("Test Case 07 Execution Completed")


      @pytest.mark.run(order=8)
      def test_008_import_bulk_records_through_csv(self):
          logging.info("import bulk record through csv")
          dir_name = "/import/qaddi/API_Automation/WAPI_PyTest/suites/customer_bug_automation"
          base_filename = "Only_bulk_records.csv"
          token = common_util.generate_token_from_file(dir_name,base_filename)
          data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"OVERRIDE"}
          response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_import")
          response=json.loads(response)
          sleep(300)
          print("File Uploaded Successfully")
          status,record=ib_NIOS.wapi_request('GET', object_type="record:a")
          print(record)
          assert re.search(r'Result set too large',record)
          print("Test Case 08 Execution Completed")



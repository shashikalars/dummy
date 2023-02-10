import json
import ib_utils.ib_NIOS as ib_NIOS
from time import sleep
import commands
import json, ast
import requests
import time
import pexpect
import ast
import unittest
import pytest
import logging
import config
import os
import glob
import sys
from os import path
#from pathlib import Path
from paramiko import client
import paramiko
import re
import pdb
import subprocess
#from subprocess import PIPE, run


#os.chdir( "/infoblox/var/named_conf/" )

class Network(unittest.TestCase):

      @pytest.mark.run(order=1)
      def test_001_enabling_dns_service(self):
          logging.info("starting DNS service")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_master_vip)
          logging.info(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print (ref1)
          data = {"enable_dns": True}
          response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_master_vip)
          sleep(5)
          logging.info(response)
          print (response)
          print("Successfully started DNS service")
          logging.info("Restart Services")
          grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_master_vip)
          ref = json.loads(grid)[0]['_ref']
          data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
          request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_master_vip)
          logging.info("Wait for 20 sec.,")
          sleep(30)
          print("successfully enabled the dns service")
          print("Test Case 1 Execution Completed")


      @pytest.mark.run(order=2)
      def test_002_create_New_AuthZone(self):
          logging.info("Creating auth zone")
          data = {"fqdn": "test.com","grid_primary": [{"name": config.grid_member_fqdn,"stealth": False}]}
          response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data),grid_vip=config.grid_master_vip)
          print(response)
          logging.info(response)
          logging.info("Restart Services")
          grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_master_vip)
          ref = json.loads(grid)[0]['_ref']
          data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
          request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_master_vip)
          logging.info("Wait for 20 sec.,")
          sleep(60)
          print("successfully enabled the dns service")
          print("Test Case 2 Execution Completed")

      @pytest.mark.run(order=3)
      def test_003_creating_A_record(self):
          logging.info("Create A record")
          data= {"ipv4addr": "2.2.2.2","name": "a.test.com","view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data),grid_vip=config.grid_master_vip)
          print(response)
          if (response[0]!=400):
              print ("Added A record")
          else:
              print ("A record already exists")
          logging.info("Test Case 3 Execution Completed")
          print("Test Case 3 Execution Completed")

      @pytest.mark.run(order=4)
      def test_004_enabling_dns_service(self):
          logging.info("starting DNS service")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid2_master_vip)
          logging.info(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print (ref1)
          data = {"enable_dns": True}
          response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid2_master_vip)
          sleep(5)
          logging.info(response)
          print (response)
          print("Successfully started DNS service")
          logging.info("Restart Services")
          grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid2_master_vip)
          ref = json.loads(grid)[0]['_ref']
          data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
          request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid2_master_vip)
          logging.info("Wait for 20 sec.,")
          sleep(30)
          print("successfully enabled the dns service")
          print("Test Case 4 Execution Completed")


      @pytest.mark.run(order=5)
      def test_005_enabling_allow_recursion(self):
	  get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns", grid_vip=config.grid2_master_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"allow_recursive_query": True}
          output1 = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid2_master_vip)
          print(output1)
          sleep(5)
  	  logging.info("Restart Services")
          grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid2_master_vip)
          ref = json.loads(grid)[0]['_ref']
          data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
          request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid2_master_vip)
          logging.info("Wait for 20 sec.,")
          sleep(20)
          print("Successfully enabled allow_recursive_query at  grid dns properties")
          print("Test Case 5 Execution Completed")

      @pytest.mark.run(order=6)
      def test_006_Adding_custome_root_name_server_at_member_level(self):
          logging.info("adding custom root name server")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid2_master_vip)
          res = json.loads(get_ref)
          ref = json.loads(get_ref)[0]['_ref']
          print(ref)
          #data = {"custom_root_name_servers": [{"address": "10.0.0.10","name": "member"}],"root_name_server_type": "CUSTOM"}
          data = {"custom_root_name_servers": [{"address": config.grid_master_vip,"name": "member"}],"root_name_server_type": "CUSTOM"}
          output = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid2_master_vip)
          print(output)
          sleep(5)
          logging.info("Restart services")
          grid =  ib_NIOS.wapi_request('GET', object_type="grid")
          ref = json.loads(grid)[0]['_ref']
          publish={"member_order":"SIMULTANEOUSLY"}
          request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish),grid_vip=config.grid2_master_vip)
          request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus",grid_vip=config.grid2_master_vip)
          restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",grid_vip=config.grid2_master_vip)
          print("System Restart is done successfully")
          sleep(300)
          print("Test Case 6 Execution Completed")


      @pytest.mark.run(order=7)
      def test_007_checking_custom_ip_in_named_cache_default_file(self):
          ssh = paramiko.SSHClient()
          ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
          print('running remote command for')
          ssh.connect(config.grid2_master_vip, username='root')
          stdin, stdout, stderr = ssh.exec_command("grep member /infoblox/var/named_conf/named.cache._default")
          response = stdout.readlines()[1]
          print("Content of named.cache._default file")
          print(response)
          #if "10.0.0.10" in response:
          if config.grid_master_vip in response:
              assert True
          else:
              assert False
          print("named.cache._default file updated with RNS ip") 
          print("Test Case 7 Execution Completed")

      @pytest.mark.run(order=8)
      def test_008_checking_the_use_root_server_for_all_views_object(self):
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid2_master_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref = json.loads(get_ref)[0]['_ref']
          print(ref)
          response = ib_NIOS.wapi_request('GET',object_type=ref+"?_return_fields=use_root_server_for_all_views",grid_vip=config.grid2_master_vip)
          print(response)
          output = json.loads(response)
          output = json.loads(response)['use_root_server_for_all_views']
          print(output)
          if output == False:
              assert True
          else:
              assert False
          print("Test Case 8 Execution Completed")
                                        
                                                                                 
      @pytest.mark.run(order=9)
      def test_009_creating_dns_view(self):
          data = {"name": "custom"}                     
          response = ib_NIOS.wapi_request('POST', object_type="view",fields=json.dumps(data),grid_vip=config.grid2_master_vip)
          print(response)
          logging.info("Restart services")
          grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid2_master_vip)
          ref = json.loads(grid)[0]['_ref']
          publish={"member_order":"SIMULTANEOUSLY"}
          request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish),grid_vip=config.grid2_master_vip)
          request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus",grid_vip=config.grid2_master_vip)
          restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",grid_vip=config.grid2_master_vip)
          print("System Restart is done successfully")
          sleep(10)
          print("Test Case 9 Execution Completed")                          
                           
      @pytest.mark.run(order=10)
      def test_010_chaning_the_dns_view_order(self):
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid2_master_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"views": ["custom","default"]}
          output1 = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid2_master_vip)
          print(output1)
          sleep(5)                          
          logging.info("Restart services")
          grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid2_master_vip)
          ref = json.loads(grid)[0]['_ref']
          publish={"member_order":"SIMULTANEOUSLY"}
          request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish),grid_vip=config.grid2_master_vip)
          request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus",grid_vip=config.grid2_master_vip)
          restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",grid_vip=config.grid2_master_vip)
          print("System Restart is done successfully")
          sleep(300)    
          print("Test Case 10 Execution Completed")

      @pytest.mark.run(order=11)
      def test_011_performing_the_dig_query_after_changing_the_dns_view_order_and_it_should_not_give_response(self):
          #dig_cmd = 'dig @'+str(config.grid2_master_vip)+' a.test.com IN A'
          #print(dig_cmd)
          proc = subprocess.Popen(['dig @'+str(config.grid2_master_vip)+' a.test.com IN A'], stdout=subprocess.PIPE, shell=True)
          (out, err) = proc.communicate()
          print "program output:", out
          if "2.2.2.2" in out:
                  assert False
          else:
                  assert True
          print("Test Case 11 Execution Completed")


      @pytest.mark.run(order=12)
      def test_012_changing_to_use_root_server_for_all_views(self):
          logging.info("changing to use_root_server_for_all_views")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid2_master_vip)
          res = json.loads(get_ref)
          ref = json.loads(get_ref)[0]['_ref']
          data = {"use_root_server_for_all_views": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid2_master_vip)
          print(output)
          sleep(10)
          logging.info("Restart services")
          grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid2_master_vip)
          ref = json.loads(grid)[0]['_ref']
          publish={"member_order":"SIMULTANEOUSLY"}
          request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish),grid_vip=config.grid2_master_vip)
          request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus",grid_vip=config.grid2_master_vip)
          restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",grid_vip=config.grid2_master_vip)
          print("System Restart is done successfully")
          sleep(300)
          print("Test Case 12 Execution Completed")

      @pytest.mark.run(order=13)
      def test_013_validating_the_root_server_for_all_views(self):
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid2_master_vip)
          res = json.loads(get_ref)
          ref = json.loads(get_ref)[0]['_ref']
          print(ref)
          response = ib_NIOS.wapi_request('GET',object_type=ref+"?_return_fields=use_root_server_for_all_views",grid_vip=config.grid2_master_vip)
          print(response)
          output = json.loads(response)
          output = json.loads(response)['use_root_server_for_all_views']
          print(output)
          if output == True:
              assert True
          else:
              assert False
          sleep(300)
          print("Test Case 13 Execution Completed")

      @pytest.mark.run(order=14)
      def test_014_checking_custom_ip_in_named_cache_default_1_file(self):
          ssh = paramiko.SSHClient()
          ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
          print('running remote command for')
          ssh.connect(config.grid2_master_vip, username='root')
          stdin, stdout, stderr = ssh.exec_command("grep member /infoblox/var/named_conf/named.cache.1")
          #stdin, stdout, stderr = ssh.exec_command("grep member /infoblox/var/named_conf/named.cache.1")
          response = stdout.readlines()[1]
          print("Content of named.cache.1 file")
          print(response)
          if config.grid_master_vip in response:
              assert True
          else:
              assert False
          print("named.cache.1 file updated with RNS ip")
          print("Test Case 14 Execution Completed")

      @pytest.mark.run(order=15)
      def test_015_performing_the_dig_query_after_changing_to_rns_to_all_dns_views_and_it_should_give_response(self):
          logging.info("Perform query for a record ")
          dig_cmd = 'dig @'+str(config.grid2_master_vip)+' a.test.com IN A'
          #print(result.returncode, result.stdout, result.stderr)
          output = subprocess.check_output(dig_cmd, shell=True)
          #print(output)
          print("@@@@@@@@@@@@@@@@@@output")
          print(output)
          sleep(05)
          print("@@@@@@@@@@@@@@@@@@@@@@@@status")
          if "2.2.2.2" in output:
                  assert True
          else:
                  assert False
          print("Test Case 15 Execution Completed")


      @pytest.mark.run(order=16)
      def test_016_chaning_the_dns_view_order(self):
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid2_master_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"views": ["default","custom"]}
          output1 = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid2_master_vip)
          print(output1)
          sleep(20)
          logging.info("Restart services")
          grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid2_master_vip)
          ref = json.loads(grid)[0]['_ref']
          publish={"member_order":"SIMULTANEOUSLY"}
          request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish),grid_vip=config.grid2_master_vip)
          request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus",grid_vip=config.grid2_master_vip)
          restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",grid_vip=config.grid2_master_vip)
          print("System Restart is done successfully")
          sleep(300)
          print("Test Case 16 Execution Completed")


      @pytest.mark.run(order=17)
      def test_017_performing_the_dig_query_after_changing_dns_view_order_and_it_should_give_response(self):
          logging.info("Perform query for a record ")
          dig_cmd = 'dig @'+str(config.grid2_master_vip)+' a.test.com IN A'
          #print(result.returncode, result.stdout, result.stderr)
          output = subprocess.check_output(dig_cmd, shell=True)
          #print(output)
          print("@@@@@@@@@@@@@@@@@@output")
          print(output)
          print("@@@@@@@@@@@@@@@@@@@@@@@@status")
          if "2.2.2.2" in output:
                  assert True
          else:
                  assert False
          print("Test Case 17 Execution Completed")



      @pytest.mark.run(order=18)
      def test_018_deleting_the_custom_dns_view(self):
          logging.info("deleting custom root name server")
          get_ref = ib_NIOS.wapi_request('GET', object_type="view", grid_vip=config.grid2_master_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref = json.loads(get_ref)[1]['_ref']
          print(ref)
          response = ib_NIOS.wapi_request('DELETE',ref=ref,grid_vip=config.grid2_master_vip)
          print(response)
          logging.info("Restart services")
          grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid2_master_vip)
          ref = json.loads(grid)[0]['_ref']
          publish={"member_order":"SIMULTANEOUSLY"}
          request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish),grid_vip=config.grid2_master_vip)
          request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus",grid_vip=config.grid2_master_vip)
          restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",grid_vip=config.grid2_master_vip)
          sleep(10)
          get_ref = ib_NIOS.wapi_request('GET', object_type="view", grid_vip=config.grid2_master_vip)
          print(get_ref)
          print("System Restart is done successfully")
          sleep(300)
          print("Test Case 18 Execution Completed")


      @pytest.mark.run(order=19)
      def test_019_Checking_for_the_named.cache.1_file_and_it_sould_not_present(self):
          logging.info("Checking the GMC status with dummy offline GMC and validating the error message")
          child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid2_master_vip)
          child.logfile=sys.stdout
          child.expect('#')
          #child.sendline('infoblox')
          #child.expect('#')
          child.sendline('cd /infoblox/var/named_conf')
          child.expect('#')
          child.sendline('ls')
          child.expect('#')
          output = child.before
          print(output)
          if "named.cache.1" in output:
              assert False
          else:
             assert True
          print("Test Case 19 Executed Successfully")             

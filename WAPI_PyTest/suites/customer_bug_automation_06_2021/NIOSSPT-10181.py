__author__ = "Siva Krishna"
__email__  = "krishnas@infoblox.com"

####################################################
#  Grid Set up required:                           #
#  1. Grid with 2 members                          #
#  2. Licenses : DNS, DHCP, Gride,NIOS (IB-V1415)  #
####################################################
import re
import config
import pytest
import unittest
import logging
import os
import os.path
from os.path import join
import subprocess
import json
import time
from time import sleep
import commands
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util
import ib_utils.log_capture as log_capture
from  ib_utils.log_capture import log_action as log
from  ib_utils.log_validation import log_validation as logv
import pexpect
from paramiko import client

class Enabling_External_Syslog_Servers(unittest.TestCase):


        @pytest.mark.run(order=1)
        def test_001_Configure_External_Syslog_Server_For_Member1(self):
                logging.info("Configure_External_Syslog_Server_For_Member1")
		response = ib_NIOS.wapi_request('GET',object_type="member")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[5])
                response=str(response[5])
                response=response.split('\"')
                print(response)
                notification=response[3]
                print("notification",notification)
                dir_name="./Certificates/"
                base_filename="ca_cert.pem"
                token = common_util.generate_token_from_file(dir_name,base_filename)
                print ("Token details :",token)
              	data = {"external_syslog_server_enable": True,"syslog_servers": [{"address": config.stcp_syslog_server,"connection_type": "STCP","category_list": [],"certificate_token": str(token)}]}
		response = ib_NIOS.wapi_request('PUT', object_type=notification, fields=json.dumps(data))
                print response
		sleep(10)
		print("Restart Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(30)
                logging.info(response)

	@pytest.mark.run(order=2)
        def test_002_Verify_Syslog_Server(self):
                logging.info("Verify_Syslog_Server")
                response = ib_NIOS.wapi_request('GET',object_type="member")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[5])
                response=str(response[5])
                response=response.split('\"')
                print(response)
                notification=response[3]
                print("notification",notification)
                print("response    : ",response)
		response = ib_NIOS.wapi_request('GET',object_type=notification+"?_return_fields=syslog_servers",grid_vip=config.grid_vip)
		print(response)
		response=response.replace('"','')
		print("address: " +config.stcp_syslog_server)
		if ("address: " +config.stcp_syslog_server in response) and re.search(r'connection_type: STCP',response):
			assert True
		else:
			assert False
                sleep(5)
                logging.info("Test Case 02 Execution Completed")
	
	@pytest.mark.run(order=3)
        def test_003_Starting_Logs(self):
                logging.info("Logs Validation")
                log("start","/var/log/syslog  /infoblox/var/infoblox.log",config.grid_member1_vip)
                sleep(20)

	@pytest.mark.run(order=4)
        def test_004_Configure_External_Syslog_Server_For_Member2(self):
                logging.info("Configure_External_Syslog_Server_For_Member2")
                response = ib_NIOS.wapi_request('GET',object_type="member")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[10])
                response=str(response[10])
                response=response.split('\"')
                print(response)
                notification=response[3]
                print("notification",notification)
                dir_name="./Certificates/"
                base_filename="ca_cert.pem"
                token = common_util.generate_token_from_file(dir_name,base_filename)
                print ("Token details :",token)
                data = {"external_syslog_server_enable": True,"syslog_servers": [{"address": config.stcp_syslog_server,"connection_type": "STCP","category_list": [],"certificate_token": str(token)}]}
                response = ib_NIOS.wapi_request('PUT', object_type=notification, fields=json.dumps(data))
                print response
		sleep(10)
		print("Restart Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(30)
                logging.info(response)

	@pytest.mark.run(order=5)
        def test_005_Verify_Syslog_Server(self):
                logging.info("Verify_Syslog_Server")
                response = ib_NIOS.wapi_request('GET',object_type="member")
                print("response    : ",response)
                print(type(response))
                response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
                response=response.split(',')
                print(response)
                print(type(response))
                print(response[10])
                response=str(response[10])
                response=response.split('\"')
                print(response)
                notification=response[3]
                print("notification",notification)
                print("response    : ",response)
                response = ib_NIOS.wapi_request('GET',object_type=notification+"?_return_fields=syslog_servers",grid_vip=config.grid_vip)
                print(response)
                response=response.replace('"','')
                print("address: " +config.stcp_syslog_server)
                if ("address: " +config.stcp_syslog_server in response) and re.search(r'connection_type: STCP',response):
                        assert True
                else:
                        assert False
                sleep(2)
                logging.info("Test Case 05 Execution Completed")

	@pytest.mark.run(order=6)
        def test_006_Stopping_Logs(self):
                logging.info("Logs Validation")
                log("stop","/var/log/syslog  /infoblox/var/infoblox.log",config.grid_member1_vip)
                sleep(20)

        @pytest.mark.run(order=7)
        def test_007_looking_for_vnode_monitor(self):
                check=commands.getoutput(" grep -cw \".*Ref.* from member vnode_monitor of type.* doesn't point to valid object of type .*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_syslog*")
                #print("check",check)
                if (int(check)==0):
                    print("CiscoISEEvent:session_seen")
                    assert True
                else:
                    assert False
                sleep(20)
                print("Test case 5 Execution Completed")

        @pytest.mark.run(order=8)
        def test_008_test_for_member1_status(self):
            response = ib_NIOS.wapi_request('GET',object_type="member")
            response=json.loads(response)
            response=response[1]["_ref"]
            response1 = ib_NIOS.wapi_request('GET',object_type=response+"?_return_fields=service_status")
            response1=json.loads(response1)
            
            print response1
            print response1["service_status"]
            print response1["service_status"][1]["status"]
            print response1["service_status"][1]["service"]
            if response1["service_status"][1]["service"]!="UNKNOWN":
                assert True
            else:
                assert False




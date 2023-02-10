#!/usr/bin/env python

__author__ = "Prasad K"
__email__  = "pkondisetty@infoblox.com"
__RFE__    = "PenTest 853 RabbitMQ and Erlang Cookies"
############################################################################################################
#  Grid Set up required:                                                               			   #
#  1. Grid Master with reporting,discovery,HA,IB-V1415 members                         			   #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415),Threat Analytics,Security Ecosystem,reporting,discovery  #
############################################################################################################


import re
import sys
from subprocess import Popen, PIPE
import config
import pytest
import unittest
import os
import os.path
from os.path import join
import json
import pexpect
import requests
import urllib3
import commands
from time import sleep
from subprocess import check_output
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util
import ib_utils.common_utilities as comm_util
import paramiko
import time
import subprocess
from datetime import datetime, timedelta
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv


class PenTest_853_RabbitMQ_and_Erlan_cookies(unittest.TestCase):


        @pytest.mark.run(order=01)
        def test_001_Make_normal_member_as_GMC_member_and_validate_the_GMC_member(self):
                print("\n============================\n")
                print("Make normal member as GMC member")
                print("================================")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
                ref = json.loads(get_ref)[-1]['_ref']
                print(ref)
                data = {"master_candidate": True}
                output = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(output)
	 	get_ref = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
                ref = json.loads(get_ref)[-1]['_ref']
                print(ref)	
		gmc_output = ib_NIOS.wapi_request('GET',ref=ref,params="?_return_fields=master_candidate")
		print(gmc_output)
		if '"master_candidate": true' in gmc_output:
			assert True
		else:
			assert False
		sleep(600)
                print("Test Case 01 Execution Completed")


        @pytest.mark.run(order=02)
        def test_002_Validate_erlang_cookie_should_have_200bytes_in_GM(self):
                print("\n============================================\n")
                print("validate erlang cookie should have 200bytes in GM")
                print("============================================")
		try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''wc -c /var/lib/rabbitmq/.erlang.cookie''')
                        child.expect('#')
                        print("\n")
                        output = child.before
                        output = output.replace("\n","").replace("\r","").replace(" wc -c /var/lib/rabbitmq/.erlang.cookie"," ").replace('-bash-4.0','')
                        print("==============================")
                        print(output)
                        print("==============================")
                        print("\n")
                        result = re.search('200(.*)erlang.cookie', output)
                        if result==None:
                                assert False
                        else:
                                result = result.group(0)
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                sleep(03)
                print("Test Case 02 Execution Completed")

        @pytest.mark.run(order=03)
        def test_003_Validate_grid_discovery_member_erlang_cookie_should_have_200bytes(self):
                print("\n============================================\n")
                print("Validate HA VIP erlang cookie should have 200bytes")
                print("============================================")
		sleep(03)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_discovery_member)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''wc -c /var/lib/rabbitmq/.erlang.cookie''')
                        child.expect('#')
                        print("\n")
                        output = child.before
                        output = output.replace("\n","").replace("\r","").replace(" wc -c /var/lib/rabbitmq/.erlang.cookie"," ").replace('-bash-4.0','')
                        print("==============================")
                        print(output)
                        print("==============================")
                        print("\n")
                        result = re.search('200(.*)erlang.cookie', output)
                        if result==None:
                                assert False
                        else:
                                result = result.group(0)
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 03 Execution Completed")


        @pytest.mark.run(order=04)
        def test_004_Validate_HA_ACTIVE_erlang_cookie_should_have_200bytes(self):
                print("\n============================================\n")
                print("Validate HA ACTIVE erlang cookie should have 200bytes")
                print("============================================")
		sleep(03)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_HA_ACTIVE)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''wc -c /var/lib/rabbitmq/.erlang.cookie''')
                        child.expect('#')
                        print("\n")
                        output = child.before
                        output = output.replace("\n","").replace("\r","").replace(" wc -c /var/lib/rabbitmq/.erlang.cookie"," ").replace('-bash-4.0','')
                        print("==============================")
                        print(output)
                        print("==============================")
                        print("\n")
                        result = re.search('200(.*)erlang.cookie', output)
                        if result==None:
                                assert False
                        else:
                                result = result.group(0)
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 04 Execution Completed")


        @pytest.mark.run(order=05)
        def test_005_Validate_HA_PASSIVE_erlang_cookie_should_have_200bytes(self):
                print("\n============================================\n")
                print("Validate HA PASSIVE erlang cookie should have 200bytes")
                print("============================================")
		sleep(03)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_HA_PASSIVE)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''wc -c /var/lib/rabbitmq/.erlang.cookie''')
                        child.expect('#')
                        print("\n")
                        output = child.before
                        output = output.replace("\n","").replace("\r","").replace(" wc -c /var/lib/rabbitmq/.erlang.cookie"," ").replace('-bash-4.0','')
                        print("==============================")
                        print(output)
                        print("==============================")
                        print("\n")
                        result = re.search('200(.*)erlang.cookie', output)
                        if result==None:
                                assert False
                        else:
                                result = result.group(0)
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 05 Execution Completed")

        @pytest.mark.run(order=06)
        def test_006_Validate_reporting_member_erlang_cookie_should_have_200bytes(self):
                print("\n============================================\n")
                print("Validate reporting member erlang cookie should have 200bytes")
                print("============================================")
		sleep(03)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.reporting_member)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''wc -c /var/lib/rabbitmq/.erlang.cookie''')
                        child.expect('#')
                        print("\n")
                        output = child.before
                        output = output.replace("\n","").replace("\r","").replace(" wc -c /var/lib/rabbitmq/.erlang.cookie"," ").replace('-bash-4.0','')
                        print("==============================")
                        print(output)
                        print("==============================")
                        print("\n")
                        result = re.search('200(.*)erlang.cookie', output)
                        if result==None:
                                assert False
                        else:
                                result = result.group(0)
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 06 Execution Completed")

        @pytest.mark.run(order=07)
        def test_007_Validate_erlang_cookie_file_should_have_read_only_access(self):
                print("\n============================================\n")
                print("Validate erlang cookie file should have read only access")
                print("============================================")
		sleep(03)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''ls -ltr /var/lib/rabbitmq/.erlang.cookie''')
                        child.expect('#')
                        print("\n")
                        output = child.before
                        print("==============================")
                        print(output)
                        print("==============================")
                        print("\n")
                        result = re.search('-r--------(.*)erlang.cookie', output)
                        if result==None:
                                assert False
                        else:
                                result = result.group(0)
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 07 Execution Completed")


##NIOS-76662

        @pytest.mark.run(order=108)
        def test_008_Validate_generate_rabbitmq_password_file_under_infoblox_one_bin_directory(self):
                print("\n============================================\n")
                print("Validating generate rabbitmq password file under infoblox one bin directory")
                print("============================================")
		sleep(03)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''ls -ltr /infoblox/one/bin/generate_rabbitmq_password''')
                        child.expect('#')
                        print("\n")
                        output = child.before
                        print("==============================")
                        print(output)
                        print("==============================")
                        print("\n")
                        result = re.search('root(.*)generate_rabbitmq_password', output)
                        if result==None:
                                assert False
                        else:
                                result = result.group(0)
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 08 Execution Completed")

        @pytest.mark.run(order=109)
        def test_009_Validate_RabbitMQ_password_not_set_logs_in_infoblox_logs(self):
                print("\n============================================\n")
                print("Validating RabbitMQ password not set logs in infoblox logs")
                print("============================================")
		sleep(03)
                try:
                        #child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_HA_VIP)
			child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''grep -a "RabbitMQ password not set" /infoblox/var/infoblox.log''')
                        child.expect('#')
                        print("\n")
                        output = child.before
                        print("==============================")
                        print(output)
                        print("==============================")
                        print("\n")
                        result = re.search('/infoblox/one/bin/generate_rabbitmq_password(.*)generating', output)
                        if result==None:
                                assert False
                        else:
                                result = result.group(0)
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 09 Execution Completed")

        @pytest.mark.run(order=10)
        def test_010_Validate_RabbitMQ_password_already_set_logs_in_infoblox_logs(self):
                print("\n============================================\n")
                print("Validating RabbitMQ password already set logs in infoblox logs")
                print("============================================")
		sleep(03)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_HA_ACTIVE)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''grep "RabbitMQ password already set" /infoblox/var/infoblox.log''')
                        child.expect('#')
                        print("\n")
                        output = child.before
                        print("==============================")
                        print(output)
                        print("==============================")
                        print("\n")
                        result = re.search('generate_rabbitmq_password(.*)set', output)
                        if result==None:
                                assert False
                        else:
                                result = result.group(0)
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 10 Execution Completed")


        @pytest.mark.run(order=11)
        def test_011_Validate_new_rabbitmq_password_should_store_in_rabbitmq_data_file(self):
                print("\n============================================")
                print("Validating new rabbitmq password should store in rabbitmq data file")
                print("============================================")
		sleep(03)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''wc -c /infoblox/var/rabbitmq_data''')
                        child.expect('#')
                        print("\n")
                        output = child.before
                        print("==============================")
                        print(output)
                        print("==============================")
                        print("\n")
                        result = re.search('20(.*)rabbitmq_data', output)
                        if result==None:
                                assert False
                        else:
                                result = result.group(0)
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 11 Execution Completed")


        @pytest.mark.run(order=12)
        def test_012_Validate_rabbitmq_password_in_onedb_xml_file(self):
                print("\n============================================\n")
                print("Validate rabbitmq password in onedb xml file")
                print("============================================")
		sleep(03)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''/infoblox/one/bin/db_dump -silvd /tmp/''')
                        child.expect('#')
                        sleep(05)
                        child.sendline('''grep -C 3 'rabbitmq_nios_password' /tmp/onedb.xml''')
                        child.expect('#')
                        output = child.before
                        result = re.search('EAA(.*)=', output)
                        if result==None:
                                assert False
                        else:
                                result = result.group(0)
                        bit_length = len(result)
                        if bit_length == 28:
                                assert True
                        else:
                                assert False
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 12 Execution Completed")

        @pytest.mark.run(order=13)
        def test_013_Get_the_Rabbitmq_Password(self):
                print("\n============================================\n")
                print("Get_the_Rabbitmq_Password")
                print("============================================")
		sleep(03)
                global rabbitmq_passwd1
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('python')
                        child.expect('>>>')
                        sleep(03)
                        child.sendline('import infoblox.common.util as cu')
                        child.expect('>>>')
                        child.sendline('rmq_passw = cu.get_rmq_password()')
                        child.expect('>>>')
                        child.sendline('rmq_passw')
                        child.expect('>>>')
                        rabbitmq_passwd1 = child.before
                        rabbitmq_passwd1 = rabbitmq_passwd1.replace('rmq_passw','').replace('\r','').replace('\n','').replace('"','').replace("'","").replace(' ','')
                        print('\n')
                        print(rabbitmq_passwd1)
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 13 Execution Completed")


        @pytest.mark.run(order=14)
        def test_014_Validate_rabbitmq_password_in_member_rabbitmq_config_file(self):
                print("\n============================================")
                print("Validate rabbitmq password in rabbitmq config file")
                print("============================================")
		sleep(60)
                #global rabbitmq_passwd
                #rabbitmq_passwd = 'nios374652'
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_HA_VIP)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('grep -C 2 "nios:" /etc/rabbitmq/rabbitmq.config')
                        child.expect('#')
                        output = child.before
                        data = 'amqp://nios:'+rabbitmq_passwd1
                        if data in output:
                                assert True
                        else:
                                assert False
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("\n")
                print(data)
                print("\n")
                print("Test Case 14 Execution Completed")


        @pytest.mark.run(order=15)
        def test_015_Validate_rabbitmqctl_status_should_be_running_in_GM(self):
                print("\n============================================\n")
                print("Validate rabbitmqctl status should be running in GM")
                print("============================================")
		sleep(03)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''rabbitmqctl status''')
                        child.expect('#')
                        print("\n")
                        output = child.before
                        print("==============================")
                        print(output)
                        print("==============================")
                        print("\n")
                        data = ['Status of node rabbit@localhost','"RabbitMQ","3.5.7"']
                        for i in data:
                                if i in output:
                                        assert True
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 15 Execution Completed")



#########################

        @pytest.mark.run(order=16)
        def test_016_Start_infoblox_logs_and_execute_rabbitmq_control_stop_command_to_stop_the_RabbitMQ_process(self):
		print("\n=================================================================================================")
		print("Start infoblox logs and execute rabbitmq_control stop command to stop the RabbitMQ process")
		print("===================================================================================================")
		sleep(03)
		log("start","/infoblox/var/infoblox.log",config.grid_vip)
		child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('''/infoblox/one/bin/rabbitmq_control stop''')
                child.expect('#')
		sleep(60)
		print("Test Case 16 Execution Completed")

        @pytest.mark.run(order=17)
        def test_017_Stop_infoblox_logs_to_validate_RabbitMQ_process_stopped_logs(self):
		print("\n=================================================================================================")
                print("Stop infoblox logs to validate RabbitMQ process stopped logs")
                print("===================================================================================================")
		log("stop","/infoblox/var/infoblox.log",config.grid_vip)
		print("\nTest Case 17 Executed Successfully")

        @pytest.mark.run(order=18)
        def test_018_Validate_RabbitMQ_process_stopped_logs_in_infoblox_logs(self):
		print("\n=====================================================")	
		print("Validate RabbitMQ process stopped logs in infoblox logs")
		print("=======================================================")
		sleep(03)
                out1 = str(config.grid_vip+'_infoblox_var_infoblox.log')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                data = ['"stop" command completed successfully','RabbitMQ: error opening TCP consumer socket']
		for i in data:
			if i in log_validation:
				assert True
			else:
				assert False
                print(data)
		print(log_validation)
		print("\nTest Case 18 Executed Successfully")

        @pytest.mark.run(order=19)
        def test_019_Start_infoblox_logs_and_execute_rabbitmq_control_start_command_to_start_the_RabbitMQ_process(self):
		print("\n===================================================================================================")
		print("Start infoblox logs and execute rabbitmq control start command to start the RabbitMQ process")
		print("=====================================================================================================")
		sleep(03)
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('''/infoblox/one/bin/rabbitmq_control start''')
                child.expect('#')
                sleep(180)
		print("\nTest Case 19 Executed Successfully")

        @pytest.mark.run(order=20)
        def test_020_Stop_infoblox_logs_to_validate_RabbitMQ_process_started_logs_in_infoblox_logs(self):
		print("\n===================================================================================================")
                print("Stop infoblox logs to validate RabbitMQ process started logs in infoblox logs")
                print("=====================================================================================================")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                print("\nTest Case 20 Executed Successfully")

        @pytest.mark.run(order=21)
        def test_021_Validate_RabbitMQ_process_started_logs_in_infoblox_logs(self):		
		print("\n=====================================================")
		print("Validate RabbitMQ process started logs in infoblox logs")
		print("=======================================================")
		sleep(03)
                out1 = str(config.grid_vip+'_infoblox_var_infoblox.log')
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
		print(log_validation)
                if 'RabbitMQ password already set' in log_validation:
                      assert True
                else:
                      assert False
                print(log_validation)
		print("\nTest Case 21 Executed Successfully")

        @pytest.mark.run(order=22)
        def test_022_Validate_new_rabbitmq_password_should_store_in_rabbitmq_data_file(self):
                print("\n============================================")
                print("Validating new rabbitmq password should store in rabbitmq data file")
                print("============================================")
		sleep(03)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''wc -c /infoblox/var/rabbitmq_data''')
                        child.expect('#')
                        print("\n")
                        output = child.before
                        print("==============================")
                        print(output)
                        print("==============================")
                        print("\n")
                        result = re.search('20(.*)rabbitmq_data', output)
                        if result==None:
                                assert False
                        else:
                                result = result.group(0)
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 22 Execution Completed")


        @pytest.mark.run(order=23)
        def test_023_Validate_rabbitmq_password_in_onedb_xml_file(self):
                print("\n============================================\n")
                print("Validate rabbitmq password in onedb xml file")
                print("============================================")
		sleep(03)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''/infoblox/one/bin/db_dump -silvd /tmp/''')
                        child.expect('#')
                        sleep(05)
                        child.sendline('''grep -C 3 'rabbitmq_nios_password' /tmp/onedb.xml''')
                        child.expect('#')
                        output = child.before
                        result = re.search('EAA(.*)=', output)
                        if result==None:
                                assert False
                        else:
                                result = result.group(0)
                        bit_length = len(result)
                        if bit_length == 28:
                                assert True
                        else:
                                assert False
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 23 Execution Completed")



        @pytest.mark.run(order=24)
        def test_024_Get_the_Rabbitmq_Password(self):
                print("\n============================================\n")
                print("Get_the_Rabbitmq_Password")
                print("============================================")
                global rabbitmq_passwd2
		sleep(60)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('python')
                        child.expect('>>>')
                        sleep(03)
                        child.sendline('import infoblox.common.util as cu')
                        child.expect('>>>')
                        child.sendline('rmq_passw = cu.get_rmq_password()')
                        child.expect('>>>')
                        child.sendline('rmq_passw')
                        child.expect('>>>')
                        rabbitmq_passwd2 = child.before
                        rabbitmq_passwd2 = rabbitmq_passwd2.replace('rmq_passw','').replace('\r','').replace('\n','').replace('"','').replace("'","").replace(' ','')
                        print('\n')
                        print(rabbitmq_passwd2)
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 24 Execution Completed")

        @pytest.mark.run(order=25)
        def test_025_Validate_rabbitmq_password_in_member_rabbitmq_config_file(self):
                print("\n============================================")
                print("Validate rabbitmq password in rabbitmq config file")
                print("============================================")
		sleep(03)
                #global rabbitmq_passwd
                #rabbitmq_passwd = 'nios374652'
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_HA_VIP)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('grep -C 2 "nios:" /etc/rabbitmq/rabbitmq.config')
                        child.expect('#')
                        output = child.before
                        data = 'amqp://nios:'+rabbitmq_passwd2
                        if data in output:
                                assert True
                        else:
                                assert False
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("\n")
                print(data)
                print("\n")
                print("Test Case 25 Execution Completed")



        @pytest.mark.run(order=26)
        def test_026_Validate_running_rabbitmq_process_through_rabbitmqctl_status_command_in_discovery_member(self):
                print("\n======================================================================================")
                print("Validate running rabbitmq process through rabbitmqctl status command in discovery member")
                print("========================================================================================")
		sleep(10)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_discovery_member)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''rabbitmqctl status''')
                        child.expect('#')
                        print("\n")
                        output = child.before
                        print("==============================")
                        print(output)
                        print("==============================")
                        print("\n")
			data = ['Status of node rabbit@localhost','"RabbitMQ","3.5.7"']
			for i in data:
				if i in output:
					assert True
				else:
					assert False
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 26 Execution Completed")



##############
## OUTBOUND ##
##############


        @pytest.mark.run(order=27)
        def test_027_Validate_running_Rabbitmq_process_in_GM_through_rabbitmqctl_status_command(self):
                print("\n========================================================================")
                print("Validate running Rabbitmq process in GM through rabbitmqctl status command")
                print("==========================================================================")
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''rabbitmqctl status''')
                        child.expect('#')
                        print("\n")
                        output = child.before
                        print("==============================")
                        print(output)
                        print("==============================")
                        print("\n")
                        data = ['Status of node rabbit@localhost','"RabbitMQ","3.5.7"']
                        for i in data:
                                if i in output:
                                        assert True
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 27 Execution Completed")

        @pytest.mark.run(order=28)
        def test_028_Start_DNS_Service_in_all_members(self):
		print("\n==============================")
                print("Start DNS Service in all members")
		print("================================")
		sleep(03)
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                #print(get_ref)
		get_ref = json.loads(get_ref)
		for i in get_ref:
			data={"enable_dns": True}
			response = ib_NIOS.wapi_request('PUT', ref=i["_ref"],fields=json.dumps(data))
			print(response)
		sleep(30)
                print("Test Case 28 Execution Completed")

        @pytest.mark.run(order=29)
        def test_029_Validate_enabled_DNS_service_in_all_members(self):
		print("\n=========================================")
                print("Validate enabled DNS Service in all members")
		print("===========================================")
		sleep(03)
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns")
                res = json.loads(get_tacacsplus)
                for i in res:
                        print(i)
                        assert i["enable_dns"] == True
                print("Test Case 29 Execution Completed")

        @pytest.mark.run(order=30)
        def test_030_Upload_Rest_Endpoint_Session_Template(self):
		print("\n===================================")
                print("Upload Rest Endpoint Session Template")
		print("=====================================")
		sleep(10)
                dir_name="./Outbound5_templates/"
                base_filename="Version5_REST_API_Session_Template.json"
                token = comm_util.generate_token_from_file(dir_name,base_filename)
                data = {"token": token,"overwrite": True}
                response = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=restapi_template_import")
                print(response)
		sleep(05)
                res = json.loads(response)
                string = {"overall_status": "SUCCESS","error_message": ""}
                if res == string:
                        assert True
                else:
                        assert False
                print("Test Case 30 Execution Completed")

        @pytest.mark.run(order=31)
        def test_031_Upload_Rest_Endpoint_DNS_ACTION_Template(self):
		print("\n=============================================")
                print("Upload Rest Endpoint DNS ACTION Template")
		print("===============================================")
		sleep(10)
                dir_name="./Outbound5_templates/"
                base_filename="Version5_DNS_Zone_and_Records_Action_Template.json"
                token = comm_util.generate_token_from_file(dir_name,base_filename)
                data = {"token": token,"overwrite": True}
                response = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=restapi_template_import")
                print(response)
                res = json.loads(response)
		sleep(05)
                string = {"overall_status": "SUCCESS","error_message": ""}
                if res == string:
                        assert True
                else:
                        assert False
                print("Test Case 31 Execution Completed")

        @pytest.mark.run(order=32)
        def test_032_Add_and_Validate_REST_API_endpoint(self):
		print("\n===================")
                print("Add and Validate REST API endpoint")
		print("=====================")
		sleep(60)
                data = {"name": "test", "uri": "https://"+config.grid_vip,"outbound_member_type": "GM","username": "admin","password": "infoblox","wapi_user_name": "admin", "wapi_user_password": "infoblox","log_level":"DEBUG","template_instance": {"template": "Version5_REST_API_Session_Template"},"server_cert_validation": "NO_VALIDATION"}
                response = ib_NIOS.wapi_request('POST', object_type="notification:rest:endpoint", fields=json.dumps(data))
                res=json.loads(response)
                print(response)
                end_point = ib_NIOS.wapi_request('GET',object_type="notification:rest:endpoint")
		print(end_point)
		data = ['"name": "test"','"uri": "https://'+config.grid_vip+'"']
		for i in data:
			if i in end_point:
				print(i)
				assert True
			else:
				assert False
                print("Test Case 32 Execution Completed")

        @pytest.mark.run(order=33)
        def test_033_Add_DNS_Zone_Notification_Rule_with_Record_Type_As_A_Record(self):
		print("\n=========================================================")
                print("Add DNS Zone Notification Rule with Record Type As A Record")
		print("===========================================================")
		sleep(15)
                object_type="notification:rest:endpoint"
                data={"name":"test"}
                get_ref = common_util.get_object_reference(object_type,data)
		get_ref = eval(json.dumps(get_ref))  
		data = {"event_type": "DB_CHANGE_DNS_RECORD","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_A","op2_type": "STRING"},{"op": "ENDLIST"}],"name": "test","notification_action": "RESTAPI_TEMPLATE_INSTANCE","notification_target": get_ref,"template_instance": {"parameters": [],"template": "Version5_DNS_Zone_and_Records_Action_Template"}}
                response = ib_NIOS.wapi_request('POST', object_type="notification:rule", fields=json.dumps(data))
		print(response)
                sleep(10)
                print("Test Case 33 Execution Completed")

        @pytest.mark.run(order=34)
        def test_034_Validate_DNS_Zone_Notification_Rule_with_Record_Type_As_A_with_match_rule_as_Insert(self):
		print("\n=================================================================================")
                print("Validate DNS Zone Notification Rule with Record Type As A with match rule as Insert")
		print("===================================================================================")
		sleep(10)
		response = ib_NIOS.wapi_request('GET',object_type="notification:rule?_return_fields=event_type,expression_list,name,notification_action,notification_target,template_instance")
                print(response)
                data = ['"name": "test"','"op2": "RECORD_TYPE_A"','"event_type": "DB_CHANGE_DNS_RECORD"','"notification_action": "RESTAPI_TEMPLATE_INSTANCE"','"template": "Version5_DNS_Zone_and_Records_Action_Template"','"template": "Version5_DNS_Zone_and_Records_Action_Template"']
                for i in data:
                        if i in response:
                                print(i)
                                assert True
                        else:
                                assert False		
                print("Test Case 34 Execution Completed")

        @pytest.mark.run(order=35)
        def test_035_Add_and_Validate_Authoritative_zone(self):
		print("\n=======================")
                print("Create and Validate Authoritative Zone")
		print("=========================")
		sleep(10)
                data = {"fqdn": "test.com","grid_primary": [{"name":config.grid_fqdn,"stealth":False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                res=json.loads(response)
                print(response)
                print("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
		print("\n=================================")
		print("Validate Created Authoritative Zone")
		print("===================================")
		sleep(10)
		response = ib_NIOS.wapi_request('GET',object_type="zone_auth?fqdn=test.com&_return_fields%2B=grid_primary,fqdn&_return_as_object=1")
		print(response)
		data = ['"fqdn": "test.com"','"name": "'+config.grid_fqdn+'"','"view": "default"']
		for i in data:
			if i in response:
				print(i)
				assert True
			else:
				assert False
                print("Test Case 35 Execution Completed")

        @pytest.mark.run(order=36)
        def test_036_Start_and_Stop_worker_log_and_create_and_validate_A_record(self):
		print("\n==============================")
                print("Creating A Record for added Zone")
		print("================================")
		sleep(03)
		log("start","/infoblox/var/outbound/log/worker_0.log",config.grid_vip)
		data = {"ipv4addr": "10.0.0.2","name": "a.test.com","view": "default"}
	        response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data),grid_vip=config.grid_vip)
          	print(response)
		sleep(180)
		log("stop","/infoblox/var/outbound/log/worker_0.log",config.grid_vip)
		print("\n=======================")
                print("Validate Created A record")
                print("=========================")
                response = ib_NIOS.wapi_request('GET',object_type="record:a?name=a.test.com&_return_fields=name,ipv4addr")
		print(response)
		data = ['"ipv4addr": "10.0.0.2"','"name": "a.test.com"']
		for i in data:
			if i in response:
				print(i)
				assert True
			else:
				assert False
                print("Test Case 36 Execution Completed")

        @pytest.mark.run(order=37)
        def test_037_Validate_template_execution_log_in_worker_log(self):
		print("\n===========================================")
		print("Validate template execution log in worker log")
		print("=============================================")
		sleep(03)
                out1 = str(config.grid_vip+'_infoblox_var_outbound_log_worker_0.log')
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
		data = ['Executing the template Version5_DNS_Zone_and_Records_Action_Template',"'event_type': 'DNS_RECORD'","'dns_name': u'a.test.com'","'ipv4addr': u'10.0.0.2'","'operation_type': u'INSERT'","The template was executed successfully"]
		for i in data:
	                if i in log_validation:
				print("\n")
				print(i)
	                      	assert True
        	        else:
                	      assert False
		print("Test Case 37 Execution Completed")

	@pytest.mark.run(order=38)
        def test_038_Validate_running_Rabbitmq_status_in_GM(self):
                print("\n====================================")
                print("Validate running Rabbitmq status in GM")
                print("======================================")
		sleep(03)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''rabbitmqctl status''')
                        child.expect('#')
                        print("\n")
                        output = child.before
                        print("==============================")
                        print(output)
                        print("==============================")
                        print("\n")
                        data = ['Status of node rabbit@localhost','"RabbitMQ","3.5.7"']
                        for i in data:
                                if i in output:
                                        assert True
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 38 Execution Completed")



######################
## Threat Analytics ##
######################


    	@pytest.mark.run(order=39)
    	def test_039_Add_an_RPZ_zone(self):
		print("\n=============")
        	print("Add an RPZ zone")
		print("===============")
		sleep(15)
        	data = {"fqdn": "rpz.com", "view":"default", "grid_primary": [{"name": config.grid_fqdn}]}
	        response = ib_NIOS.wapi_request('POST', object_type="zone_rp", fields=json.dumps(data))
        	print(response)
        	print("Restart DNS Services")
	        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        	ref = json.loads(grid)[0]['_ref']
	        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        	request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
	        sleep(30)
		print("Test Case 39 Execution Completed")


	@pytest.mark.run(order=40)
	def test_040_Validate_added_RPZ_zone(self):
		print("\n=========================")
        	print("Validating created RPZ zone")
		print("===========================")
		sleep(10)
        	response = ib_NIOS.wapi_request('GET', object_type="zone_rp?fqdn=rpz.com", grid_vip=config.grid_vip)
		print(response)
		if '"fqdn": "rpz.com"' in response:
			assert True
		else:
			assert False
		print("Test Case 40 Execution Completed")


    	@pytest.mark.run(order=41)
	def test_041_Associate_created_RPZ_zone_to_threat_analytics(self):
		print("\n==============================================")
        	print("associating created RPZ zone to threat analytics")
		print("================================================")
		sleep(05)
        	get_ref = ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics", grid_vip=config.grid_vip)
		print(get_ref)
        	ref = json.loads(get_ref)[0]['_ref']
		ref = eval(json.dumps(ref))
        	response = ib_NIOS.wapi_request('GET', object_type="zone_rp?fqdn=rpz.com", grid_vip=config.grid_vip)
		print(response)
		rpz_ref = json.loads(response)[0]['_ref']
        	data = {"dns_tunnel_black_list_rpz_zones": [rpz_ref]}
	        output = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
	        print(output)
		print("\n")
        	print("Successfully added rpz.com at threat_analytics")
		print("\n")
		print("Test Case 41 Execution Completed")


        @pytest.mark.run(order=42)
        def test_042_Add_DNS_forwarders_at_grid_dns_properties(self):
		print("\n==========================================")
		print("adding DNS forwarders at grid dns properties")
		print("============================================")
		sleep(05)
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns", grid_vip=config.grid_vip)
                ref1 = json.loads(get_ref)[0]['_ref']
                data = {"forwarders": [config.dns_forwarder_1,config.dns_forwarder_2]}
                print(data)
                output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(output)
                print("Successfully added forwarders at grid dns properties")
                print("Test Case 42 Execution Completed")


        @pytest.mark.run(order=43)
        def test_043_Validate_added_forwarders_at_grid_dns_properties(self):
		print("\n================================================")
                print("Validating added forwarders at grid dns properties")
		print("==================================================")
		sleep(05)
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns?_return_fields=forwarders", grid_vip=config.grid_vip)
                print(get_ref)
		data = [config.dns_forwarder_1,config.dns_forwarder_2]
		for forwarder in data:
			if forwarder in get_ref:
				print(forwarder)
				assert True
			else:
				assert False
                print("Test Case 43 Execution Completed")


	@pytest.mark.run(order=44)
        def test_044_Enabling_allow_recursive_query_and_logging_categories_log_queries_log_responses_at_grid_dns_properties(self):
		print("\n====================================================================================================")
		print("Enabling allow recursive query and logging categories log queries log responses at grid dns properties")
		print("======================================================================================================")
		sleep(60)
		get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns", grid_vip=config.grid_vip)
                ref1 = json.loads(get_ref)[0]['_ref']
		data = {"allow_recursive_query": True}
                output1 = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(output1)
                print("Successfully enabled allow_recursive_query at  grid dns properties")
                print("enabling log_queries and log_responses and log_rpz at grid dns properties")
                data = {"logging_categories": {"log_queries": True,"log_responses": True,"log_rpz": True}}
                output2 = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(output2)
                print("Successfully enabled log_queries and log_responses and log_rpz at grid dns properties")
                print("Restarting the  Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(30)
                print("Successfully restarted the services")
		print("Test Case 44 Execution Completed")


        @pytest.mark.run(order=45)
        def test_045_Validate_Enabled_allow_recursive_query_and_logging_categories_log_queries_log_responses_at_grid_dns_properties(self):
		print("\n============================================================================================================")
                print("Validate_Enabled_allow_recursive_query_and_logging_categories_log_queries_log_responses_at_grid_dns_properties")
		print("==============================================================================================================")
		sleep(03)
                grid_dns_data = ib_NIOS.wapi_request('GET', object_type="grid:dns?_return_fields=allow_recursive_query,logging_categories", grid_vip=config.grid_vip)
		print(grid_dns_data)
		data = ['"allow_recursive_query": true','"log_queries": true','"log_responses": true','"log_rpz": true']
		for i in data:
			if i in grid_dns_data:
				print(i)
				assert True
			else:
				assert False
		print("\n")
                print("Test Case 45 Execution Completed")
		
        @pytest.mark.run(order=46)
        def test_046_Enable_Threat_Analytics_Service_in_GM(self):
		print("\n===================================")
		print("Enable Threat Analytics Service in GM")
		print("=====================================")
		get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatanalytics", grid_vip=config.grid_vip)
		print(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
		print(ref)
                data = {"enable_service": True}
                output = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data))
                print(output)
                print("Successfully started threat analytics service")
		sleep(60)
		print("Restarting the  Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(30)
                print("Successfully restarted the services")
		print("Test Case 46 Execution Completed")

        @pytest.mark.run(order=47)
        def test_047_Validate_enabled_Threat_Analytics_Service_in_GM(self):
		print("\n=============================================")
		print("Validate enabled threat analytics service in GM")
		print("===============================================")
		sleep(10)
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatanalytics?_return_fields=enable_service", grid_vip=config.grid_vip)
                ref = json.loads(get_ref)[0]['_ref']
		output = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=enable_service")
		print(output)
		if '"enable_service": true' in output:
			assert True
		else:
			assert False
		response = 'dig @'+str(config.grid_vip)+' '+'226L01TTL-0.'+str("infoblox.com")+'.'+str(' IN ')+str("TXT")
		print(response)
                print("Test Case 47 Execution Completed")

        @pytest.mark.run(order=48)
        def test_048_Dig_threatrabbitmqtest_domain_to_detect_the_DNS_tunneling_activity(self):
		print("\n====================================================================")
		print("Dig threatrabbitmqtest domain to detect the DNS tunneling activity")
		print("======================================================================")
		sleep(03)
		ping = ('for i in {1..100}; do dig @'+config.grid_lan1+' 226L01TTL-0.threatrabbitmqtest26.com IN TXT ;done')
                data = os.popen(ping).read()
                print(data)
		sleep(180)
		print("Test Case 48 Execution Completed")


        @pytest.mark.run(order=49)
        def test_049_Validate_DNS_Tunneling_detected_log_in_var_log_messages(self):
		print("\n=====================================================")
		print("Validate DNS Tunneling detected log in var log messages")
		print("=======================================================")
		sleep(100)
		try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline("grep -a 'DNS Tunneling detected' /var/log/syslog")
                        child.expect('#')
                        print("\n")
                        output = child.before
                        data = "threatrabbitmqtest26.com has been detected with tunneling activity"
                        if data in output:
                                assert True
                        else:
                                assert False
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
		print("\n")
		print("===========================")
		print(data)
		print("===========================")
		print("Test Case 49 Execution Completed")
		
        @pytest.mark.run(order=50)
        def test_050_Validate_domain_added_into_blacklist_log_in_infoblox_logs(self):
		print("\n=======================================================")
		print("Validate domain added into blacklist log in infoblox logs")
		print("=========================================================")
		sleep(60)
		try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline("grep -a 'successfully added into BlackList' /infoblox/var/infoblox.log")
                        child.expect('#')
                        print("\n")
                        output = child.before
                        print("\n")
			data = "threatrabbitmqtest26.com' is successfully added into BlackList RPZ zone"
                        if data in output:
				assert True
			else:
				assert False
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("===========================")
                print(data)
                print("===========================")
                print("Test Case 50 Execution Completed")


        @pytest.mark.run(order=51)
        def test_051_Validate_running_Rabbitmq_status_in_GM(self):
                print("\n====================================")
                print("Validate running Rabbitmq status in GM")
                print("======================================")
		sleep(03)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
			sleep(30)
                        child.sendline('''rabbitmqctl status''')
                        child.expect('#')
                        print("\n")
                        output = child.before
                        print("==============================")
                        print(output)
                        print("==============================")
                        print("\n")
                        data = ['Status of node rabbit@localhost','"RabbitMQ","3.5.7"']
                        for i in data:
                                if i in output:
                                        assert True
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 51 Execution Completed")



######################
#### DNS load ########
######################

        @pytest.mark.run(order=52)
        def test_052_Add_authoritative_forward_mapping_zone(self):
		print("\n===========================")
                print("adding authoritative forward-mapping zone")
		print("===========================")
		sleep(03)
                data = {"fqdn": "test1.com","view": "default","grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                sleep(05)
                print("\nTest Case 52 Execution Completed")

        @pytest.mark.run(order=53)
        def test_053_Validate_added_authoritative_forward_mapping_zone(self):
		print("\n===================================================")
                print("validating created authoritative forward mapping zone")
		print("=====================================================")
		sleep(03)
                zone_data = ib_NIOS.wapi_request('GET',object_type="zone_auth?fqdn=test1.com&_return_fields%2B=grid_primary,fqdn,view&_return_as_object=1")
                print(zone_data)
		data = ['"fqdn": "test1.com"','"name": "'+config.grid_fqdn+'"','"stealth": false','"view": "default"']
		for i in data:
			if i in zone_data:
				print(i)
				assert True
			else:
				assert False		
                print("Test Case 53 Executuion Completed")


        @pytest.mark.run(order=54)
        def test_054_Add_A_record(self):
                print("\n=============")
                print("Adding A record")
                print("===============")
                data = {"ipv4addr": "10.0.0.26","name": "z.test1.com","view": "default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                sleep(05)
                print("Test Case 54 Executuion Completed")

        @pytest.mark.run(order=55)
        def test_055_Validate_addition_of_A_record(self):
                print("\n=========================")
                print("validating created A record")
                print("===========================")
		sleep(03)
                output = ib_NIOS.wapi_request('GET',object_type="record:a?name=z.test1.com",grid_vip=config.grid_vip)
                print(output)
                result = ['"name": "z.test1.com"','"ipv4addr": "10.0.0.26"']
                for i in result:
                    if i in output:
                        assert True
                    else:
                        assert False
                print(result)
                print("Test Case 55 Executuion Completed")

        @pytest.mark.run(order=56)
        def test_056_Dig_created_A_record(self):
		print("\n==================")
		print("Dig created A record")
		print("====================")
		sleep(60)
                ping = ('for i in {1..1000}; do dig @'+config.grid_lan1+' z.test1.com IN A ;done')
                data = os.popen(ping).read()
		print(data)
                #if "10.0.0.26" in data:
		#	assert True
		#else:
		#	assert False
                sleep(05)
                print("Test Case 56 Execution Completed")



        @pytest.mark.run(order=57)
        def test_057_Validate_running_Rabbitmq_status_in_GM(self):
                print("\n====================================")
                print("Validate running Rabbitmq status in GM")
                print("======================================")
		sleep(03)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''rabbitmqctl status''')
                        child.expect('#')
                        print("\n")
                        output = child.before
                        print("==============================")
                        print(output)
                        print("==============================")
                        print("\n")
                        data = ['Status of node rabbit@localhost','"RabbitMQ","3.5.7"']
                        for i in data:
                                if i in output:
                                        assert True
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 57 Execution Completed")



###################
##### DHCP Load ###
###################

        @pytest.mark.run(order=58)
        def test_058_Start_IPv4_DHCP_service_in_all_the_members(self):
		print("\n===================================")
                print("start ipv4 service in all the members")
		print("=====================================")
		get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties")
		get_ref = json.loads(get_ref)
		for i in get_ref:
                        data={"enable_dhcp": True}
                        response = ib_NIOS.wapi_request('PUT', ref=i["_ref"],fields=json.dumps(data))
                        print(response)
		sleep(10)
                print("Test Case 58 Execution Completed")


        @pytest.mark.run(order=59)
        def test_059_Validate_Enabled_DHCP_services_in_all_the_members(self):
                print("\n===============================================")
                print("Validate Enabled DHCP services in all the members")
                print("=================================================")
		#sleep(60)
		get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties",params="?_return_fields=enable_dhcp")
                res = json.loads(get_tacacsplus)
                for i in res:
                        print(i)
                        assert i["enable_dhcp"] == True
		print("Test Case 59 Execution Completed")


        @pytest.mark.run(order=60)
        def test_060_Create_IPv4_network_with_member_assignment_in_default_network_view(self):
		print("\n================================================================")
                print("create IPv4 network with member assignment in default network view")
		print("==================================================================")
                data = {"network": "10.0.0.0/8","network_view": "default","members":[{"_struct": "dhcpmember","ipv4addr":config.grid_lan1}]}
                response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                print("Created the ipv4network 10.0.0.0/8 in default view")
                print("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 60 Execution Completed")


        @pytest.mark.run(order=61)
        def test_061_Validate_created_IPv4_network(self):
		print("\n===================================================")
                print("Validate created IPv4 network in default network view")
		print("=====================================================")
                network =  ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
		ref = json.loads(network)[0]['_ref']
		response =  ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=network,network_view,members")
		print(response)
		data = ['"network": "10.0.0.0/8"','"network_view": "default"','"ipv4addr": "'+config.grid_lan1+'"','"name": "'+config.grid_fqdn+'"']
		for i in data:
			if i in response:
				print(i)
				assert True
			else:
				assert False
                print("Test Case 61 Execution Completed")

        @pytest.mark.run(order=62)
        def test_062_Create_IPv4_Range_in_created_network(self):
		print("\n==================================")
                print("Create IPv4 range in created network")
		print("=====================================")
                data = {"network":"10.0.0.0/8","start_addr":"10.0.0.5","end_addr":"10.0.0.220","network_view": "default","member": {"_struct": "dhcpmember","ipv4addr": config.grid_lan1,"name": config.grid_fqdn}}
                response = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(data), grid_vip=config.grid_vip)
                print (response)
                for read in  response:
                        assert True
                print("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 62 Execution Completed")


        @pytest.mark.run(order=63)
        def test_063_Validate_created_IPv4_Range(self):
		print("\n=========================")
                print("Validate created IPv4 range")
		print("===========================")
		sleep(05)
                data = ['"network": "10.0.0.0/8"','"start_addr": "10.0.0.5"','"end_addr": "10.0.0.220"','"network_view": "default"','"name": "'+config.grid_fqdn+'"']
                ipv4_range = ib_NIOS.wapi_request('GET', object_type="range")
		ref = json.loads(ipv4_range)[0]['_ref']
		ipv4_range = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=network,start_addr,end_addr,network_view,member")
		print(ipv4_range)
                for i in data:
			print(i)
			if i in ipv4_range:
	                        assert True
			else:
				assert False
                print("Test Case 63 Execution Completed")


        @pytest.mark.run(order=64)
        def test_064_requesting_ipv4_lease_with_link_selection_option(self):
		print("\n==============================================")
                print("requesting ipv4 lease with link selection option")
		print("================================================")
		sleep(05)
		for i in range(1,51):
                	dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i'+str(config.grid_lan1)+' '+'-n 1 -x l=10.0.0.0 '
                	dras_cmd1 = os.system(dras_cmd)
                	print (dras_cmd1)
                	sleep(02)
                IP_Lease =  ib_NIOS.wapi_request('GET', object_type="lease",grid_vip=config.grid_vip)
                print(IP_Lease)
		if '"address": "10.0.0.219"' in IP_Lease:
			assert True
		else:
			assert False
                print("Test Case 64 Execution Completed")



        @pytest.mark.run(order=65)
        def test_065_Validate_running_Rabbitmq_status_in_GM(self):
                print("\n============================================\n")
                print("Validate running Rabbitmq status in GM")
                print("============================================")
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''rabbitmqctl status''')
                        child.expect('#')
                        print("\n")
                        output = child.before
                        print("==============================")
                        print(output)
                        print("==============================")
                        print("\n")
                        data = ['Status of node rabbit@localhost','"RabbitMQ","3.5.7"']
                        for i in data:
                                if i in output:
                                        assert True
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 65 Execution Completed")




########################
## Adding DTC license ##
########################


        @pytest.mark.run(order=66)
        def test_066_Install_and_Validate_DTC_license_in_GM(self):
                print("\n====================================")
                print("Install and Validate DTC license in GM")
                print("======================================")
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('password:')
                        child.sendline('infoblox')
                        child.expect('Infoblox >')
                        child.sendline('set temp_license')
			child.expect('quit:')
			child.sendline('13')
			child.expect(':')
			child.sendline('y')
			child.expect(':')
			child.sendline('y')
			child.expect(':')
			child.sendline('y')
			child.expect('Infoblox >')
			child.sendline('show license ')
			child.expect('Infoblox >')
			output = child.before
			if 'DNS Traffic Control' in output:
				assert True
			else:
				assert False
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("\nTest Case 66 Execution Completed")



        @pytest.mark.run(order=67)
        def test_067_Validate_running_Rabbitmq_status_in_GM(self):
                print("\n===================================n")
                print("Validate running Rabbitmq status in GM")
                print("======================================")
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''rabbitmqctl status''')
                        child.expect('#')
                        print("\n")
                        output = child.before
                        print("==============================")
                        print(output)
                        print("==============================")
                        print("\n")
                        data = ['Status of node rabbit@localhost','"RabbitMQ","3.5.7"']
                        for i in data:
                                if i in output:
                                        assert True
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 67 Execution Completed")



##########################
## deleting DTC license ##
##########################

        @pytest.mark.run(order=68)
        def test_068_Delete_DTC_license_in_GM(self):
                print("\n============================================\n")
                print("Delete DTC license in GM")
                print("============================================")
		sleep(60)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('/infoblox/one/bin/processlic -d dtc -p 0')
                        child.expect('#')
                        print("\n")
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 68 Execution Completed")

        @pytest.mark.run(order=69)
        def test_069_Validate_removed_DTC_license_in_GM(self):
                print("\n================================")
                print("Validate removed DTC license in GM")
                print("==================================")
		sleep(03)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('password:')
                        child.sendline('infoblox')
                        child.expect('Infoblox >')
                        child.sendline('show license ')
                        child.expect('Infoblox >')
                        output = child.before
                        if 'DNS Traffic Control' in output:
                                assert False
                        else:
                                assert True
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("\nTest Case 69 Execution Completed")


        @pytest.mark.run(order=70)
        def test_070_Validate_running_Rabbitmq_status_in_GM(self):
                print("\n============================================\n")
                print("Validate running Rabbitmq status in GM")
                print("============================================")
		sleep(03)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''rabbitmqctl status''')
                        child.expect('#')
                        print("\n")
                        output = child.before
                        print("==============================")
                        print(output)
                        print("==============================")
                        print("\n")
                        data = ['Status of node rabbit@localhost','"RabbitMQ","3.5.7"']
                        for i in data:
                                if i in output:
                                        assert True
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 70 Execution Completed")



###################
### HA Failover ###
###################

        @pytest.mark.run(order=71)
        def test_071_Validate_running_Rabbitmq_status_in_GM(self):
                print("\n====================================\n")
                print("Validate running Rabbitmq status in GM")
                print("============================================")
		sleep(100)
                try:
                        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@'+config.grid_HA_ACTIVE)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''rabbitmqctl status''')
                        child.expect('#')
                        print("\n")
                        output = child.before
                        print("==============================")
                        print(output)
                        print("==============================")
                        print("\n")
                        data = ['Status of node rabbit@localhost','"RabbitMQ","3.5.7"']
                        for i in data:
                                if i in output:
                                        assert True
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 71 Execution Completed")

        @pytest.mark.run(order=72)
        def test_072_ssh_to_the_HA_Active_and_perform_reboot_to_make_HA_failover(self):
                print("\n=========================================================")
                print("ssh to the HA Active and perform reboot to make HA failover")
                print("===========================================================")
		sleep(60)
		sleep(05)
                vm_reboot=os.popen("reboot_system -H "+config.Active_VM_ID).read()
                print(vm_reboot)
		sleep(500)
                print("Test Case 72 Execution Completed")


        @pytest.mark.run(order=73)
        def test_073_Validate_running_Rabbitmq_status_in_HA_Passive_member(self):
                print("\n==================================================")
                print("Validate_running_Rabbitmq_status_in_HA_Active_member")
                print("====================================================")
		sleep(120)
                try:
                        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@'+config.grid_HA_PASSIVE)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''rabbitmqctl status''')
                        child.expect('#')
                        print("\n")
                        output = child.before
                        print("==============================")
                        print(output)
                        print("==============================")
                        print("\n")
                        data = ['Status of node rabbit@localhost','"RabbitMQ","3.5.7"']
                        for i in data:
                                if i in output:
                                        assert True
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
		sleep(600)
                print("Test Case 73 Execution Completed")




        @pytest.mark.run(order=74)
        def test_074_After_HA_Failover_test_rabbitmqctl_status_in_HA_Passive_member(self):
                print("\n============================================")
                print("After HA Failover test rabbitmqctl status in becomed HA Passive member")
                print("============================================")
		sleep(03)
                try:
                        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@'+config.grid_HA_ACTIVE)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''rabbitmqctl status''')
                        child.expect('#')
                        print("\n")
                        output = child.before
                        print("==============================")
                        print(output)
                        print("==============================")
                        print("\n")
                        data = ['Status of node rabbit@localhost','"RabbitMQ","3.5.7"']
                        for i in data:
                                if i in output:
                                        assert True
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 74 Execution Completed")



###################
## GMC Promotion ##
###################

        @pytest.mark.run(order=75)
        def test_075_Perform_GMC_Promotion_in_GMC_member(self):
                print("\n============================================\n")
                print("Perform GMC Promotion in  GMC member")
                print("============================================")
		sleep(03)
                try:
                        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@'+config.grid_GMC)
                        child.logfile=sys.stdout
                        child.expect('password:')
                        child.sendline('infoblox')
                        child.expect('Infoblox >')
                        child.sendline('set promote_master')
                        child.expect('Do you want a delay between notification to grid members\? \(y or n\): ')
			child.sendline('n')
			child.expect(': ')
			child.sendline('y')
			child.expect(':')
			child.sendline('y')
			output = child.before
			print(output)
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 75 Execution Completed")


        @pytest.mark.run(order=76)
        def test_076_Validate_running_Rabbitmq_status_in_new_GM_after_GMC_promotion(self):
                print("\n===================================================")
                print("Validate Master status in new GM, after GMC Promotion")
                print("=====================================================")
		sleep(2000)
		try:
                        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@'+config.grid_GMC)
                        child.logfile=sys.stdout
                        child.expect('password:')
			child.sendline('infoblox')
			child.expect('Infoblox >')
                        child.sendline('show network')
                        child.expect('Infoblox >')
                        print("\n")
                        output = child.before
                        print("==============================")
                        print(output)
                        print("==============================")
                        print("\n")
			data = 'Master of Infoblox Grid'
			if data in output:
				assert True
			else:
				assert False
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()		
		print(data)
		#########################################
		##### Validating rabbitmqctl status #####
		#########################################
		print("\n============================================\n")
                print("Validate running Rabbitmq status in new GM after GMC promotion")
                print("============================================")
		sleep(300)
                try:
                        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@'+config.grid_GMC)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''rabbitmqctl status''')
                        child.expect('#')
                        print("\n")
                        output = child.before
                        print("==============================")
                        print(output)
                        print("==============================")
                        print("\n")
                        data = ['Status of node rabbit@localhost','"RabbitMQ","3.5.7"']
                        for i in data:
                                if i in output:
                                        assert True
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 76 Execution Completed")



        @pytest.mark.run(order=77)
        def test_077_Validate_running_Rabbitmq_status_in_previous_master_aftre_GMC_promotion(self):
                print("\n============================================\n")
                print("Validate running Rabbitmq status in previous master aftre GMC promotion")
                print("============================================")
		sleep(100)
                try:
                        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''rabbitmqctl status''')
                        child.expect('#')
                        print("\n")
                        output = child.before
                        print("==============================")
                        print(output)
                        print("==============================")
                        print("\n")
                        data = ['Status of node rabbit@localhost','"RabbitMQ","3.5.7"']
                        for i in data:
                                if i in output:
                                        assert True
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 77 Execution Completed")

#############END#################

import re
import pprint
import config
import pytest
import unittest
import logging
import subprocess
import os
import json
import ib_utils.ib_NIOS as ib_NIOS
from time import sleep
import commands
import json, ast
import requests
import time
import pexpect
import sys
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv




class Network(unittest.TestCase):


    @pytest.mark.run(order=1)
    def test_01_Add_offline_member(self):
        print("----------------------------------------------------")
        print("|          Test Case 1 Execution Started           |")
        print("----------------------------------------------------")
        print("Add offline member")
        data = {"config_addr_type": "BOTH",
                "host_name": "ib-10-35-0-2.infoblox.com",
                "platform": "VNIOS",
                "service_type_configuration": "ALL_V6",
                "vip_setting": {"address": "10.35.0.2",
                                "gateway": "10.35.0.1",
                                "primary": True,
                                "subnet_mask": "255.255.0.0"},
                "ipv6_setting": {"cidr_prefix": int(64),
                                 "enabled": True,
                                 "gateway": "2620:10a:6000:2400::1",
                                 "primary": True,
                                 "virtual_ip": "2620:10a:6000:2400::2" }}
        response = ib_NIOS.wapi_request('POST',object_type="member",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            print("Failure: Add offline member")
            assert False
        print("-----------Test Case 1 Execution Completed------------")

    @pytest.mark.run(order=2)
    def test_02_Add_offline_member(self):
        print("----------------------------------------------------")
        print("|          Test Case 2 Execution Started           |")
        print("----------------------------------------------------")
        print("Add offline member")
        data = {"config_addr_type": "BOTH",
                "host_name": "ib-10-35-0-3.infoblox.com",
                "platform": "VNIOS",
                "service_type_configuration": "ALL_V6",
                "vip_setting": {"address": "10.35.0.3",
                                "gateway": "10.35.0.1",
                                "primary": True,
                                "subnet_mask": "255.255.0.0"},
                "ipv6_setting": {"cidr_prefix": int(64),
                                 "enabled": True,
                                 "gateway": "2620:10a:6000:2400::1",
                                 "primary": True,
                                 "virtual_ip": "2620:10a:6000:2400::3" }}
        response = ib_NIOS.wapi_request('POST',object_type="member",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            print("Failure: Add offline member")
            assert False
        print("-----------Test Case 2 Execution Completed------------")

    @pytest.mark.run(order=3)
    def test_03_Making_normal_member_as_GMC(self):
          logging.info("making normal member as GMC ")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
          #ref1 = json.loads(get_ref)[0]['_ref']
          res = json.loads(get_ref)
          res = eval(json.dumps(res))
          #print(res)
          ref1=(res)[1]['_ref']
          print(ref1)
          data1 = {"master_candidate": True}
          output1 = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data1),grid_vip=config.grid_vip)
          print(output1)
          ref2=(res)[4]['_ref']
          print(ref2)
          data2 = {"master_candidate": True}
          output2 = ib_NIOS.wapi_request('PUT',ref=ref2,fields=json.dumps(data2),grid_vip=config.grid_vip)
          print(output2)
          sleep(600)
          print("-----------Test Case 3 Execution Completed------------")

    @pytest.mark.run(order=4)
    def test_04_Validating_the_Message_sent_status_from_GMC(self):
        logging.info("Validating the message sent status from GMC")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        for i in range(1,10):
	        child.sendline('set test_promote_master '+config.grid_member1_vip)
	       	child.expect('Enter Timeout \(>10 secs\) for test messages\(default 120 sec\): ')
        	child.sendline('10')
	        child.expect('\(y or n\): ')
        	child.sendline('y')
	        child.expect('Infoblox >')
        	sleep(10)
	        child.sendline('show test_promote_master status')
        	child.expect('Infoblox >')
	        output = child.before
        	output =output.replace('\n','').replace(' ','').replace('[','').replace(']','').replace('\r','').replace('\t','')
	        print(output)
       		if ('MessageissentfromGMC' in output):
                        #result =re.findall(r'MessageissentfromGMC',output)
                        print("Validated the Connected Status")
                        break
                else:
                        child.sendline('set test_promote_master '+config.grid_member1_vip)
	                child.expect('Enter Timeout \(>10 secs\) for test messages\(default 120 sec\): ')
        	        child.sendline('10')
        	        child.expect('\(y or n\): ')
               		child.sendline('y')
	                child.expect('Infoblox >')
        	        sleep(10)
                	child.sendline('show test_promote_master status')
	                child.expect('Infoblox >')
        	        output = child.before
                        print(output)
               		output =output.replace('\n','').replace(' ','').replace('[','').replace(']','').replace('\r','').replace('\t','')
                        print("\n")
                        if ('MessageissentfromGMC' in output):
                               print("Validated the Connected Status")
                               break
                        else:
                               print("Trying again to get the Connected Status")
                        sleep(10)
        print("\nTest Case 04 Executed Successfully")

    @pytest.mark.run(order=5)
    def test_05_Validating_the_Message_was_not_received_by_GMC_status(self):
        logging.info("Validating the message not received status by GMC ")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        sleep(30)
        for i in range(1,10):
	        child.sendline('set test_promote_master '+config.grid_member1_vip)
        	child.expect('Enter Timeout \(>10 secs\) for test messages\(default 120 sec\): ')
	        child.sendline('60')
	        child.expect('\(y or n\): ')
       		child.sendline('y')
	        child.expect('Infoblox >')
	        sleep(65)
	        child.sendline('show test_promote_master status')
	        child.expect('Infoblox >')
	        output = child.before
	        pp = pprint.PrettyPrinter(depth=1)
        	output=output.replace('\n','').replace(' ','').replace('[','').replace(']','').replace('\r','').replace('\t','')
	        print("\n")
       		sleep(10)
	        if ('MessagewasnotreceivedbyGMC' in output):
        	      print("alidated the MessagewasnotreceivedbyGMC Status")
                      break
	        else:
            	      child.sendline('set test_promote_master '+config.grid_member1_vip)
	              child.expect('Enter Timeout \(>10 secs\) for test messages\(default 120 sec\): ')
        	      child.sendline('60')
	              child.expect('\(y or n\): ')
        	      child.sendline('y')
	              child.expect('Infoblox >')
        	      child.sendline('show test_promote_master status')
	              child.expect('Infoblox >')
        	      sleep(65)
	              output = child.before
        	      pp = pprint.PrettyPrinter(depth=1)
	              output=output.replace('\n','').replace(' ','').replace('[','').replace(']','').replace('\r','').replace('\t','')
        	      print("\n")
	              sleep(40)
                      print(output)
                      if ('MessagewasnotreceivedbyGMC' in output):
                            print("Validated the MessagewasnotreceivedbyGMC Status")
                            break
                      else:
                            print("Trying again to get the MessagewasnotreceivedbyGMC Status")
                            sleep(10)
        print("Test Case 05 Executed Successfully")



    @pytest.mark.run(order=6)
    def test_06_Starting_GMC_Promotion_Test_and_Validating_Connected_status(self):
        logging.info("Validating the test connected status ")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        for i in range(1,10):
        	child.sendline('set test_promote_master '+config.grid_member1_vip)
	        child.expect('Enter Timeout \(>10 secs\) for test messages\(default 120 sec\): ')
	        child.sendline('60')
	        child.expect('\(y or n\): ')
       		child.sendline('y')
	        child.expect('Infoblox >')
	        sleep(65)
       	        child.sendline('show test_promote_master status')
	        child.expect('Infoblox >')
       		output = child.before
	        output=output.replace('\n','').replace(' ','').replace('[','').replace(']','').replace('\r','').replace('\t','')
        	print("\n")
	        print(output) 
        	if ('Connected' in output):
           	      print("Validated the Connected Status")
                      break 
        	else:
            	    child.sendline('set test_promote_master '+config.grid_member1_vip)
	            child.expect('Enter Timeout \(>10 secs\) for test messages\(default 120 sec\): ')
	            child.sendline('60')
	            child.expect('\(y or n\): ')
	            child.sendline('y')
       		    child.expect('Infoblox >')
	            sleep(65)
        	    child.sendline('show test_promote_master status')
	            child.expect('Infoblox >')
       		    output = child.before
	            output=output.replace('\n','').replace(' ','').replace('[','').replace(']','').replace('\r','').replace('\t','')
        	    print("\n")
	            print(output)
	            sleep(05)
                    if ('Connected' in output):
                         print("Validated the Connected Status")
                         break
                    else:
                        print("Trying again to get Connected Status")
        	    #result = re.findall(r''+config.grid_member2_fqdn+'IRDPport\(\:2114\)\:Connected[a-zA-Z]{6}[0-9]{4}\:[0-9]{2}\:[0-9]{6}VPNport\(\:1194\)\:Connected',output)
	            #print(result)
        print("Test Case 06 Executed Successfully")


    @pytest.mark.run(order=7)
    def test_07_Validating_Test_Finished_status(self):
        logging.info("Validating the test finished status")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        sleep(30)
        child.sendline('show test_promote_master status')
        child.expect('Infoblox >')
        output = child.before
        result = re.findall(r'Test state is FINISHED',output)
        print("\n")
        print(result)
        if (result==[]):
           assert False
        else:
           assert True
        print("\nTest Case 07 Executed Successfully")
 
                                    
    @pytest.mark.run(order=8)
    def test_08_Validating_the_Another_test_is_currently_running_status(self):
        logging.info("validating the Another test is currently running status")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set test_promote_master '+config.grid_member1_vip)
        child.expect('Enter Timeout \(>10 secs\) for test messages\(default 120 sec\): ')
        child.sendline('15')
        child.expect('\(y or n\): ')
        child.sendline('y')
        child.expect('Infoblox >')
        child.sendline('set test_promote_master '+config.grid_member1_vip)
        child.expect('Infoblox >')
        output=child.before
        result=re.findall(r'Another test is currently running. There could be only one test at a time.',output)
        print("\n")
        print(result)
        sleep(30)
        if (result==[]):
           assert False
        else:
           assert True
        print("\nTest Case 08 Executed Successfully")
                            
                      
    @pytest.mark.run(order=9)
    def test_09_Testing_the_GMC_Promotion_Test_STOP_command(self):                
        logging.info("Testing the GMC STOP command")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set test_promote_master '+config.grid_member1_vip)
        child.expect('Enter Timeout \(>10 secs\) for test messages\(default 120 sec\): ')
        child.sendline('10')
        child.expect('\(y or n\): ')
        child.sendline('y')
        child.expect('Infoblox >')
        child.sendline('set test_promote_master stop')
        child.expect('\(y or n\): ')
        child.sendline('y')
        child.expect('Infoblox >')
        child.sendline('set test_promote_master stop')
        child.expect('\(y or n\): ')
        child.sendline('y')
        child.expect('Infoblox >')
        output = child.before
        print("\n")
        output = re.findall(r'Test was stopped already.',output)
        print(output)
        if (output==[]):
           assert False
        else:
           assert True
        sleep(10)
        print("\nTest Case 09 Executed Successfully")        
               

    @pytest.mark.run(order=10)
    def test_10_Checking_the_GMC_Promotion_Test_status_with_GMC_IP(self):
        logging.info("Checking the GMC Promotion Test status with GMC IP")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        for i in range(1,10):
        	child.sendline('set test_promote_master '+config.grid_member1_vip)
	        child.expect('Enter Timeout \(>10 secs\) for test messages\(default 120 sec\): ')
        	child.sendline('10')
	        child.expect('\(y or n\): ')
        	child.sendline('y')
	        child.expect('Infoblox >')
	        child.sendline('show test_promote_master '+config.grid_member1_vip)
        	child.expect('Infoblox >')
	        output = child.before
                if ('Test state is STARTED' in output):
                     print("Validated the Test STARTED Status")
                     break
                else:
                     child.sendline('set test_promote_master '+config.grid_member1_vip)
                     child.expect('Enter Timeout \(>10 secs\) for test messages\(default 120 sec\): ')
                     child.sendline('10')
                     child.expect('\(y or n\): ')
                     child.sendline('y')
	             child.expect('Infoblox >')
         	     child.sendline('show test_promote_master '+config.grid_member1_vip)
	             child.expect('Infoblox >')
                     output = child.before
                     print(output)
                     if ('Test state is STARTED' in output):
                            print("Validated the Test STARTED Status")
                            break
                     else:
                            print("Trying again to get the Validated the Test STARTED Status")
                     print("\n")
        sleep(15)
        print("\nTest Case 10 Executed Successfully")



    @pytest.mark.run(order=11)
    def test_11_Checking_the_GMC_Test_Timeout_intervals(self):
        logging.info("Checking the GMC test timeout intervals")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set test_promote_master '+config.grid_member1_vip)
        child.expect('Enter Timeout \(>10 secs\) for test messages\(default 120 sec\): ')
        child.sendline('1')
        child.expect('Infoblox >')
        output = child.before
        print('\n')
        result = re.findall(r'Invalid timeout value',output)
        print(result)
        if (result==[]):
           assert False
        else:
           assert True
        sleep(10)
        print("\nTest Case 11 Executed Successfully")


    @pytest.mark.run(order=12)
    def test_12_Checking_the_GMC_Test_Timeout_intervals(self):
        logging.info("Checking the GMC test timeout intervals")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set test_promote_master '+config.grid_member1_vip)
        child.expect('Enter Timeout \(>10 secs\) for test messages\(default 120 sec\): ')
        child.sendline('121')
        child.expect('Infoblox >')
        output = child.before
        print('\n')
        result = re.findall(r'Invalid timeout value',output)
        print(result)
        if (result==[]):
           assert False
        else:
           assert True
        sleep(10)
        print("\nTest Case 12 Executed Successfully")

    @pytest.mark.run(order=13)
    def test_13_Try_to_start_GMC_test_with_the_IP_which_is_not_present_in_the_grid_and_validating_the_error_message(self):
        logging.info("Try to start GMC test with the IP which is not present in the grid")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set test_promote_master 10.0.0.1')
        child.expect('Infoblox >')
        output= child.before
        print('\n')
        result = re.findall(r'IP: 10.0.0.1 is not present in the Grid',output)
        print(result)
        if (result==[]):
           assert False
        else:
           assert True
        sleep(10)
        print("\nTest Case 13 Executed Successfully")


    @pytest.mark.run(order=14)
    def test_14_Try_to_start_with_ipv6_ip_which_is_not_present_in_the_grid_and_validating_the_error_message(self):
        logging.info("Try to start GMC test with ipv6 ip which is not present in the grid and validating the error message")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set test_promote_master 2001:0db8:85a3:0000:0000:8a2e:0370:7334')
        child.expect('Infoblox >')
        output = child.before
        print('\n')
        result = re.findall(r'IP: 2001:0db8:85a3:0000:0000:8a2e:0370:7334 is not present in the Grid',output)
        print(result)
        if (result==[]):
           assert False
        else:
           assert True
        sleep(60)
        print("\nTest Case 14 Executed Successfully")


    @pytest.mark.run(order=15)
    def test_15_Try_to_start_GMC_test_with_member_and_validating_the_error_message(self):
        logging.info("Try to start the GMC test with member IP and validating the error message")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        sleep(10)
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set test_promote_master '+config.grid_member2_vip)
        child.expect('Infoblox >')
        output = child.before
        print('\n')
        result = re.findall(r''+config.grid_member2_vip+' is not an IP of Grid Master Candidate',output)
        print(result)
        if (result==[]):
           assert False
        else:
           assert True
        sleep(30)
        print("\nTest Case 15 Executed Successfully")

    @pytest.mark.run(order=16)
    def test_16_Try_to_start_GMC_test_with_ipv6_member_and_validating_the_error_message(self):
        logging.info("Try to start the GMC test with ipv6 member IP and validating the error message")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        sleep(10)
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set test_promote_master '+config.grid1_member2_vipv6)
        child.expect('Infoblox >')
        output = child.before
        print('\n')
        result = re.findall(r''+config.grid1_member2_vipv6+' is not an IP of Grid Master Candidate',output)
        print(result)
        if (result==[]):
           assert False
        else:
           assert True
        sleep(20)
        print("\nTest Case 16 Executed Successfully")


    @pytest.mark.run(order=17)
    def test_17_Try_to_start_GMC_test_with_grid_master_ip_and_validating_the_error_message(self):
        logging.info("Try to start the GMC test with grid master ip")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        sleep(10)
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set test_promote_master '+config.grid_vip)
        child.expect('Infoblox >')
        output = child.before
        print('\n')
        result = re.findall(r''+config.grid_vip+' is an IP of Grid Master. Test cannot be run for it',output)
        print(result)
        if (result==[]):
           assert False
        else:
           assert True
        sleep(20)
        print("\nTest Case 17 Executed Successfully")


    @pytest.mark.run(order=18)
    def test_18_Try_to_start_GMC_test_with_ipv6_grid_master_ip_and_validating_the_error_message(self):
        logging.info("Try to start the GMC test with ipv6 grid master ip")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set test_promote_master '+config.grid1_master_vipv6)
        child.expect('Infoblox >')
        output = child.before
        print('\n')
        result = re.findall(r''+config.grid1_master_vipv6+' is an IP of Grid Master. Test cannot be run for it',output)
        print(result)
        if (result==[]):
           assert False
        else:
           assert True
        sleep(20)
        print("\nTest Case 18 Executed Successfully")

    @pytest.mark.run(order=19)
    def test_19_Checking_the_another_GMC_is_running_message_with_ipv6(self):
        logging.info("validating the GMC test is already running message with ipv6")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set test_promote_master '+config.grid1_member1_vipv6)
        child.expect('Enter Timeout \(>10 secs\) for test messages\(default 120 sec\): ')
        child.sendline('15')
        child.expect('\(y or n\): ')
        child.sendline('y')
        child.expect('Infoblox >')
        sleep(5)
        child.sendline('set test_promote_master '+config.grid1_member1_vipv6)
        child.expect('Infoblox >')
        output =child.before
        result =re.findall(r'Another test is currently running. There could be only one test at a time.',output)
        print("\n")
        print(result)
        if (result==[]):
           assert False
        else:
           assert True
        sleep(30)
        print("\nTest Case 19 Executed Successfully")

    @pytest.mark.run(order=20)
    def test_20_Validating_the_GMC_Test_STOPPED_status(self):
        logging.info("validating the GMC test stopped status")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set test_promote_master '+config.grid_member1_vip)
        child.expect('Enter Timeout \(>10 secs\) for test messages\(default 120 sec\): ')
        child.sendline('10')
        child.expect('\(y or n\): ')
        child.sendline('y')
        child.expect('Infoblox >')
        child.sendline('set test_promote_master stop')
        child.expect('\(y or n\): ')
        child.sendline('y')
        child.expect('Infoblox >')
        child.sendline('show test_promote_master status')
        child.expect('Infoblox >')
        output = child.before
        output=output.replace('\n','').replace(' ','').replace('[','').replace(']','').replace('\r','').replace('\t','')
        print(output)
        result = re.findall(r''+config.grid_member2_fqdn+'IRDPport\(\:2114\)\:MessageissentfromGMC[a-zA-Z]{6}[0-9]{4}\:[0-9]{2}\:[0-9]{6}StoppedVPNport\(\:1194\)\:MessageissentfromGMC[a-zA-Z]{6}[0-9]{4}\:[0-9]{2}\:[0-9]{6}Stopped',output)
        print(result)
        if (result==[]):
           assert False
        else:
           assert True
        sleep(30)
        print("\nTest Case 20 Executed Successfully")


    @pytest.mark.run(order=21)
    def test_21_Validating_the_GMC_test_started_state_with_ipv6(self):
        logging.info("Validating the GMC test started state")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        for i in range(1,10):
        	child.sendline('set test_promote_master '+config.grid1_member1_vipv6)
	        child.expect('Enter Timeout \(>10 secs\) for test messages\(default 120 sec\): ')
        	child.sendline('10')
	        child.expect('\(y or n\): ')
        	child.sendline('y')
	        child.expect('Infoblox >')
        	child.sendline('show test_promote_master status')
	        child.expect('Infoblox >')
        	output = child.before
                if ('Test state is STARTED' in output):
                      print("Validated the Test STARTED Status")
                      break
                else:
                      child.sendline('set test_promote_master '+config.grid1_member1_vipv6)
                      child.expect('Enter Timeout \(>10 secs\) for test messages\(default 120 sec\): ')
                      child.sendline('10')
                      child.expect('\(y or n\): ')
                      child.sendline('y')
	              child.expect('Infoblox >')
                      child.sendline('show test_promote_master status')
                      child.expect('Infoblox >')
                      output = child.before
                      print(output)
                      if ('Test state is STARTED' in output):
                             print("Validated the Test STARTED Status")
                             break
                      else:
                             print("Trying again to get the Test state is STARTED Status")
	              print("\n")
	              sleep(10)
        print("\nTest Case 21 Executed Successfully")


    @pytest.mark.run(order=22)
    def test_22_Validating_the_message_sent_from_GMC_status_with_ipv6(self):
        logging.info("Validating the message sent from GMC status with IPv6")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        sleep(30)
        for i in range(1,10):
        	child.sendline('set test_promote_master '+config.grid1_member1_vipv6)
	        child.expect('Enter Timeout \(>10 secs\) for test messages\(default 120 sec\): ')
        	child.sendline('20')
	        child.expect('\(y or n\): ')
        	child.sendline('y')
	        child.expect('Infoblox >')
        	sleep(5)
	        child.sendline('show test_promote_master status')
        	child.expect('Infoblox >')
                output = child.before
                output=output.replace('\n','').replace(' ','').replace('[','').replace(']','').replace('\r','').replace('\t','')
                if ('MessageissentfromGMC' in output):
                        print("\n")
                        print("Validated the MessageissentfromGMC Status")
                        sleep(40)
                        break
                else:
                        child.sendline('set test_promote_master '+config.grid1_member1_vipv6)
               		child.expect('Enter Timeout \(>10 secs\) for test messages\(default 120 sec\): ')
	                child.sendline('20')
        	        child.expect('\(y or n\): ')
                	child.sendline('y')
	                child.expect('Infoblox >')
        	        sleep(5)
                	child.sendline('show test_promote_master status')
	                child.expect('Infoblox >')
        	        output = child.before
		        output=output.replace('\n','').replace(' ','').replace('[','').replace(']','').replace('\r','').replace('\t','')
                        print(output)
                        if ('MessageissentfromGMC' in output):
                             print("Validated the MessageissentfromGMC Status")
                             break
                        else:
                             print("Trying again to get the MessageissentfromGMC Status")
		        print('\n')
        		sleep(40)
        print("\nTest Case 22 Executed Successfully")


    @pytest.mark.run(order=23)
    def test_23_Validating_the_message_was_not_received_by_GMC_status_with_ipv6(self):
        logging.info("Validating the message was not received by GMC status with ipv6")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        for i in range(1,10):
                child.sendline('set test_promote_master '+config.grid1_member1_vipv6)
                child.expect('Enter Timeout \(>10 secs\) for test messages\(default 120 sec\): ')
                child.sendline('20')
                child.expect('\(y or n\): ')
                child.sendline('y')
                child.expect('Infoblox >')
                sleep(30)
        	child.sendline('show test_promote_master status')
	        child.expect('Infoblox >')
	        output = child.before
        	output=output.replace('\n','').replace(' ','').replace('[','').replace(']','').replace('\r','').replace('\t','')
	        print('\n')
                print(output)
        #result = re.findall(r''+config.grid_member3_fqdn+'IRDPport\(\:2114\)\:MessagewasnotreceivedbyGMC[a-zA-Z]{6}[0-9]{4}\:[0-9]{2}\:[0-9]{6}VPNport\(\:1194\)\:MessagewasnotreceivedbyGMC',output)
                if ('MessagewasnotreceivedbyGMC' in output):
                      print('\n')
                      print("Validated the MessagewasnotreceivedbyGMC Status")
                      break
                else:
                      child.sendline('set test_promote_master '+config.grid1_member1_vipv6)
                      child.expect('Enter Timeout \(>10 secs\) for test messages\(default 120 sec\): ')
                      child.sendline('20')
                      child.expect('\(y or n\): ')
                      child.sendline('y')
                      child.expect('Infoblox >')
                      sleep(30)
                      child.sendline('show test_promote_master status')
                      child.expect('Infoblox >')
                      output = child.before
                      output=output.replace('\n','').replace(' ','').replace('[','').replace(']','').replace('\r','').replace('\t','')
                      print('\n')
                      print(output)
                      if ('MessagewasnotreceivedbyGMC' in output):
                             print("Validated the MessagewasnotreceivedbyGMC Status")
                             break
                      else:
                             print("Trying again to get the MessagewasnotreceivedbyGMC Status")
                      print('\n')
                      sleep(10)
        print("\nTest Case 23 Executed Successfully")
    
    @pytest.mark.run(order=24)
    def test_24_Validating_the_GMC_Promotion_Test_Connected_status_with_ipv6(self):
        logging.info("Validating the GMC Promotion Test Connected status with IPv6")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        for i in range(1,10):
		child.sendline('set test_promote_master '+config.grid1_member1_vipv6)
                child.expect('Enter Timeout \(>10 secs\) for test messages\(default 120 sec\): ')
                child.sendline('120')
                child.expect('\(y or n\): ')
                child.sendline('y')
                child.expect('Infoblox >')
                sleep(125)
	        child.sendline('show test_promote_master status')
        	child.expect('Infoblox >')
	        output = child.before
                pp = pprint.PrettyPrinter(depth=1)
        	output=output.replace('\n','').replace(' ','').replace('[','').replace(']','').replace('\r','').replace('\t','')
	        print('\n')
                sleep(10)
                if ('Connected' in output):
                      print('\n')
                      print("Validated the Connected Status")
                      break
		else:
                      child.sendline('set test_promote_master '+config.grid1_member1_vipv6)
                      child.expect('Enter Timeout \(>10 secs\) for test messages\(default 120 sec\): ')
                      child.sendline('120')
          	      child.expect('\(y or n\): ')
                      child.sendline('y')
                      child.expect('Infoblox >')
                      child.sendline('show test_promote_master status')
                      child.expect('Infoblox >')
                      sleep(125)
                      output = child.before
                      pp = pprint.PrettyPrinter(depth=1)
                      output=output.replace('\n','').replace(' ','').replace('[','').replace(']','').replace('\r','').replace('\t','')	
                      print('\n')
                      sleep(10)
                      print(output)
                      if ('Connected' in output):
                            print("alidated the Connected Status")
                            break
                      else:
                            print("Trying again to get the Connected Status")
                      print('\n')
                      sleep(10)
        print("\nTest Case 24 Executed Successfully")
        

    @pytest.mark.run(order=25)
    def test_25_Validating_the_GMC_test_Finished_status(self):
        logging.info("Validating the GMC test Finished status")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show test_promote_master status')
        child.expect('Infoblox >')
        output = child.before
        result = re.findall(r'Test state is FINISHED',output)
        print("\n",result)
        if (result==[]):
           assert False
        else:
           assert True
        sleep(20)
        print("\nTest Case 25 Executed Successfully")


    @pytest.mark.run(order=26)
    def test_26_Validating_the_GMC_test_Finished_status_with_GMC_IP(self):
        logging.info("Validating the GMC test Finished status with GMC IP")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show test_promote_master '+config.grid1_member1_vipv6)
        child.expect('Infoblox >')
        output = child.before
        result = re.findall(r'Test state is FINISHED',output)
        print("\n",result)
        if (result ==[]):
           assert False
        else:
           assert True
        sleep(20)
        print("\nTest Case 26 Executed Successfully")


    @pytest.mark.run(order=27)
    def test_27_starting_the_GMC_test_to_check_Promotion_Test(self):
        logging.info("starting the GMC promotion test to check GMC Promotion")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set test_promote_master '+config.grid1_member1_vipv6)
        child.expect('Enter Timeout \(>10 secs\) for test messages\(default 120 sec\): ')
        child.sendline('120')
        child.expect('\(y or n\): ')
        child.sendline('y')
        child.expect('Infoblox >')
        print("\nTest Case 27 Executed Successfully")


    @pytest.mark.run(order=28)
    def test_28_Checking_GMC_Promotion_while_GMC_test_running(self):
        logging.info("Checking the GMC promotion While running the GMC Promotion Test")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set promote_master ')
        child.expect('Do you want a delay between notification to grid members\? \(y or n\): ')
        child.sendline('y')
        child.expect(': ')
        child.sendline('30')
        child.expect(': ')
        child.sendline('y')
        child.expect('Infoblox >')
        output = child.before
        result = re.findall(r"Cannot promote because GMC test promotion is in progress.",output)
        print("\n",result)
        if (result == []):
           assert False
        else:
           assert True
        sleep(180)
        print("\nTest Case 28 Executed Successfully")


    @pytest.mark.run(order=29)
    def test_29_checking_the_GMC_set_command_in_Grid_Master_Candidate(self):
        logging.info("Checking the GMC set command in Grid Master Candidate and validating the error message")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set test_promote_master '+config.grid_member1_vip)
        child.expect('Infoblox >')
        output = child.before
        result = re.findall(r"ERROR: This setting may only be changed on the active MASTER.",output)
        print(result)
        if (result == []):
           assert False
        else:
           assert True
        sleep(20)
        print("\nTest Case 29 Executed Successfully")


    @pytest.mark.run(order=30)
    def test_30_checking_the_GMC_show_command_in_Grid_Master_Candidate(self):
        logging.info("Checking the GMC show command in Grid Master Candidate and validating the error message")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show test_promote_master status')
        child.expect('Infoblox >')
        output = child.before
        result = re.findall(r"ERROR: This setting may only be changed on the active MASTER.",output)
        print(result)
        if (result == []):
           assert False
        else:
           assert True
        sleep(20)
        print("\nTest Case 30 Executed Successfully")

    @pytest.mark.run(order=31)
    def test_31_checking_GMC_show_command_in_Grid_Master_Candidate_with_IP(self):
        logging.info("Checking the GMC set command in Grid Master Candidate with IP and validating the error message")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show test_promote_master '+config.grid_member1_vip)
        child.expect('Infoblox >')
        output = child.before
        result = re.findall(r"ERROR: This setting may only be changed on the active MASTER.",output)
        print(result)
        if (result == []):
           assert False
        else:
           assert True
        sleep(20)
        print("\nTest Case 31 Executed Successfully")

    @pytest.mark.run(order=32)
    def test_32_checking_GMC_stop_command_in_Grid_Master_Candidate(self):
        logging.info("Checking the GMC stop command in Grid Master Candidate and validating the error message")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set test_promote_master stop')
        child.expect('Infoblox >')
        output = child.before
        result = re.findall(r"ERROR: This setting may only be changed on the active MASTER.",output)
        print(result)
        if (result == []):
           assert False
        else:
           assert True
        sleep(20)
        print("\nTest Case 32 Executed Successfully")



    @pytest.mark.run(order=33)
    def test_33_checking_GMC_set_command_in_Member(self):
        logging.info("Checking the GMC set command in Member and validating the error message")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set test_promote_master '+config.grid_member1_vip)
        child.expect('Infoblox >')
        output = child.before
        result = re.findall(r"ERROR: This setting may only be changed on the active MASTER.",output)
        print(result)
        if (result == []):
           assert False
        else:
           assert True
        sleep(20)
        print("\nTest Case 33 Executed Successfully")


    @pytest.mark.run(order=34)
    def test_34_checking_GMC_show_status_command_in_Member(self):
        logging.info("Checking the GMC show command in Member and validating the error message")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show test_promote_master status')
        child.expect('Infoblox >')
        output = child.before
        result = re.findall(r"ERROR: This setting may only be changed on the active MASTER.",output)
        print(result)
        if (result == []):
           assert False
        else:
           assert True
        sleep(20)
        print("\nTest Case 34 Executed Successfully")

    @pytest.mark.run(order=35)
    def test_35_checking_GMC_stop_command_in_Member(self):
        logging.info("Checking the GMC stop command in Member and validating the error message")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set test_promote_master stop')
        child.expect('Infoblox >')
        output = child.before
        result = re.findall(r"ERROR: This setting may only be changed on the active MASTER.",output)
        print(result)
        if (result == []):
           assert False
        else:
           assert True
        sleep(20)
        print("\nTest Case 35 Executed Successfully")

    @pytest.mark.run(order=36)
    def test_36_checking_GMC_ipv6_set_command_in_Grid_Master_Canditate(self):
        logging.info("Checking the GMC set command with ipv6 in Grid Master Candidate and validating the error message")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set test_promote_master '+config.grid1_member1_vipv6)
        child.expect('Infoblox >')
        output = child.before
        result = re.findall(r"ERROR: This setting may only be changed on the active MASTER.",output)
        print(result)
        if (result == []):
           assert False
        else:
           assert True
        sleep(20)
        print("\nTest Case 36 Executed Successfully")

    @pytest.mark.run(order=37)
    def test_37_checking_GMC_ipv6_show_command_in_Grid_Master_Canditate_with_ipv6_ip(self):
        logging.info("Checking the GMC show command with ipv6 in Grid Master Candidate and validating the error message")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show test_promote_master '+config.grid1_member1_vipv6)
        child.expect('Infoblox >')
        output = child.before
        result = re.findall(r"ERROR: This setting may only be changed on the active MASTER.",output)
        print(result)
        if (result == []):
           assert False
        else:
           assert True
        sleep(20)
        print("\nTest Case 37 Executed Successfully")


    @pytest.mark.run(order=38)
    def test_38_checking_GMC_ipv6_set_command_in_Member(self):
        logging.info("Checking the GMC set command with ipv6 in Member and validating the error message")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set test_promote_master '+config.grid1_member1_vipv6)
        child.expect('Infoblox >')
        output = child.before
        result = re.findall(r"ERROR: This setting may only be changed on the active MASTER.",output)
        print(result)
        if (result == []):
           assert False
        else:
           assert True
        sleep(20)
        print("\nTest Case 38 Executed Successfully")


    @pytest.mark.run(order=39)
    def test_39_checking_GMC_ipv6_show_command_in_Member(self):
        logging.info("Checking the GMC show command with ipv6 in Member and validating the error message")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show test_promote_master '+config.grid1_member1_vipv6)
        child.expect('Infoblox >')
        output = child.before
        result = re.findall(r"ERROR: This setting may only be changed on the active MASTER.",output)
        print(result)
        if (result == []):
           assert False
        else:
           assert True
        sleep(20)
        print("\nTest Case 39 Executed Successfully")



    @pytest.mark.run(order=40)
    def test_40_Giving_the_special_characters_in_Timeout_field(self):
        logging.info("Giving special characters in Timeout field and validating the error message")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set test_promote_master '+config.grid1_member1_vipv6)
        child.expect('Enter Timeout \(>10 secs\) for test messages\(default 120 sec\): ')
        child.sendline('@a#3d')
        child.expect('Infoblox >')
        output = child.before
        print('\n')
        result = re.findall(r'Invalid timeout value',output)
        print(result)
        if (result==[]):
           assert False
        else:
           assert True
        sleep(20)
        print("\nTest Case 40 Executed Successfully")


    @pytest.mark.run(order=41)
    def test_41_Checking_the_description_in_CLI(self):
        logging.info("Validating the description in CLI")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set test_promote_master ')
        child.expect('Infoblox >')
        output = child.before
        result = re.findall(r'Use "set test_promote_master < GMC Ip Address | stop>" To test communication of GMC with provided IP Address with other members in case it will be promoted to Grid Master. Or to stop currently running test.',output)
        print(result)
        if (result==[]):
           assert False
        else:
           assert True
        sleep(20)
        print("\nTest Case 41 Executed Successfully")


    @pytest.mark.run(order=42)
    def test_42_Try_to_start_GMC_test_with_offline_GMC_and_validating_the_error_message(self):
        logging.info("strting the GMC test with offline member and validating the error message")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set test_promote_master '+config.grid_member4_vip)
        child.expect('Enter Timeout \(>10 secs\) for test messages\(default 120 sec\): ')
        child.sendline('10')
        child.expect('\(y or n\): ')
        child.sendline('y')
        child.expect('Infoblox >')
        output = child.before
        result = re.findall(r'Message was not sent to GMC. Exiting the command.',output)
        print(result)
        if (result==[]):
           assert False
        else:
           assert True
        sleep(20)
        print("\nTest Case 42 Executed Successfully")


    @pytest.mark.run(order=43)
    def test_43_Checking_the_GMC_results_with_dummy_offline_GMC(self):
        logging.info("Checking the GMC status with dummy offline GMC and validating the error message")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show test_promote_master '+config.grid_member4_vip)
        child.expect('Infoblox >')
        output = child.before
        result = re.findall(r'No test results found.',output)
        print(result)
        if (result==[]):
           assert False
        else:
           assert True
        sleep(20)
        print("\nTest Case 43 Executed Successfully")

    @pytest.mark.run(order=44)
    def test_44_start_infoblox_logs_and_GMC_test(self):
        logging.info("Starting Infoblox Logs and GMC test")
        log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " > /var/log/syslog "'
        out1 = commands.getoutput(sys_log_validation)
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set test_promote_master '+config.grid_member1_vip)
        child.expect('Enter Timeout \(>10 secs\) for test messages\(default 120 sec\): ')
        child.sendline('10')
        child.expect('\(y or n\): ')
        child.sendline('y')
        child.expect('Infoblox >')
        child.sendline("exit")
        sleep(20)
        print("Test Case 44 Execution Completed")

    @pytest.mark.run(order=45)
    def test_45_stop_infoblox_Logs(self):
        logging.info("Stopping Infoblox Logs")
        log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
        print("Test Case 45 Execution Completed")

    @pytest.mark.run(order=46)
    def test_46(self):
        logging.info("Validating Starting GMC communication test on infoblox logs")
        LookFor="Starting GMC communication test"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_member1_vip)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test Case 46 Execution Failed")
            assert False
        else:
            logging.info("Test Case 46 Execution Completed")
            assert True

        logging.info("Test Case 46 Execution Completed")
        print("Test Case 46 Execution Completed")


    @pytest.mark.run(order=47)
    def test_47_start_infoblox_logs_and_GMC_communication_test(self):
        logging.info("Starting Infoblox Logs and GMC communication test")
        log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " > /var/log/syslog "'
        out1 = commands.getoutput(sys_log_validation)
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set test_promote_master '+config.grid1_member1_vipv6)
        child.expect('Enter Timeout \(>10 secs\) for test messages\(default 120 sec\): ')
        child.sendline('10')
        child.expect('\(y or n\): ')
        child.sendline('y')
        child.expect('Infoblox >')
        child.sendline("exit")
        sleep(20)
        print("Test Case 47 Execution Completed")

    @pytest.mark.run(order=48)
    def test_48_stop_infoblox_Logs(self):
        logging.info("Stopping Infoblox Logs")
        log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
        print("Test Case 48 Execution Completed")

    @pytest.mark.run(order=49)
    def test_49_validating_GMC_communication_test_on_infoblox_logs(self):
        logging.info("Validating Ending GMC communication test on infoblox logs")
        LookFor="Ending GMC communication test"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_member1_vip)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test Case 49 Execution Failed")
            assert False
        else:
            logging.info("Test Case 49 Execution Completed")
            assert True

        logging.info("Test Case 49 Execution Completed")
        print("Test Case 49 Execution Completed")

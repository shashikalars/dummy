#!/usr/bin/env python

__author__ = "Shivasai"
__email__  = "sbandaru@infoblox.com"
__RFE__= "NIOS-76661 RabbitMQ upgrade to 3.8.2"
##################################################################################################
#  Grid Set up required:	                                                                     #
#  1. Grid Master with IB-V1415 members 	                                                	 #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415),Threat Analytics,Security Ecosystem,discovery  #
##################################################################################################

import re
import sys
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
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util
import ib_utils.common_utilities as comm_util
import paramiko
import time
from datetime import datetime, timedelta
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv

def prod_status(ip):
    ping_cmd= 'ping -c 3 '+str(ip)
    print ping_cmd
    for i in range(3):
        result_ping= os.system(ping_cmd)
        if result_ping == 0:
            print("product restarted successfully")
            return True
        else:
            sleep(120)
    else:
        print("product is still restarting")
        return False


class PenTest_855_RabbitMQ_Upgrade(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_001_Validate_rabbitmqctl_status_should_be_running_in_GM(self):   
        print("============================================")
        print("  Validate rabbitmqctl version in 3.8.2    ")
        print("============================================")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('#')
            child.sendline('''rabbitmqctl status''')
            child.expect('#')
            print("\n")
            output = child.before
            print(output)
            print("==============================")
            print("\n")
            data = ["Status of node rabbit","RabbitMQ","3.8.2"]
            for i in data:
                if i not in output:
                    assert False
                    print (i)
        except Exception as error_message:
            print(error_message)
            assert False
        finally:
            child.close()
        print("Test Case 001 Execution Completed")
    
    
    @pytest.mark.run(order=2)
    def test_002_Get_the_Rabbitmq_Password(self):
        print("\n============================================\n")
        print("Get_the_Rabbitmq_Password")
        print("============================================")
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
            print(rabbitmq_passwd1)
        except Exception as error_message:
            (error_message)
            assert False
        finally:
            child.close()
        print("Test Case 02 Execution Completed")
        
    

    @pytest.mark.run(order=3)
    def test_003_Validate_new_rabbitmq_password_should_store_in_rabbitmq_data_file(self):
        print("\n============================================\n")
        print("Validate_new_rabbitmq_password_should_store_in_rabbitmq_data_file")
        print("============================================")
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
            result = result.group(0)
        except Exception as error_message:
            print(error_message)
            assert False
        finally:
            child.close()
        print("Test Case 3 Execution Completed") 
        
        
    @pytest.mark.run(order=4)
    def test_004_Validate_rabbitmq_config_file_is_encrypted(self):
        print("\n============================================\n")
        print("Validate rabbitmq password in rabbitmq config is encrypted")
        print("============================================")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member2_vip)
            child.logfile=sys.stdout
            child.expect('#')
            child.sendline('grep -C 2 "encrypted" /etc/rabbitmq/rabbitmq.config')
            child.expect('#')
            output = child.before
            result = re.search('to_members_shovel', output)
            result = result.group(0)
            if result == "":
                assert False
            else:
                assert True
            print("Rabbitmq config file is encrypted")
        except Exception as error_message:
            print(error_message)
            assert False
        finally:
            child.close()
        print("Test Case 4 Execution Completed")  

    
    @pytest.mark.run(order=5)
    def test_005_execute_show_rabbitmq_state_command(self):
        print("\n====================================")
        print("execute_show_rabbitmq_state_command")
        print("======================================")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('show rabbitmq_state')
            child.expect('Infoblox >')
            output = child.before
            if 'RabbitMQ is not blocked.' in output:
                assert True
            else:
                assert False
        
        except Exception as error_message:
            print(error_message)
            assert False
        finally:
            child.close()
            
        print("Test Case 5 Execution Completed")
            

    @pytest.mark.run(order=6)
    def test_006_execute_set_unblock_rabbitmq_command(self):
        print("\n====================================")
        print("execute_set_unblock_rabbitmq_command")
        print("======================================")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set unblock_rabbitmq')
            child.expect('Infoblox >')
            output = child.before
            if 'RabbitMQ is not blocked.' in output:
                assert True
            else:
                assert False
        
        except Exception as error_message:
            print(error_message)
            assert False
        finally:
            child.close()
            
        print("Test Case 6 Execution Completed")
        
        
        
    @pytest.mark.run(order=7)
    def test_007_verify_set_unblock_rabbitmq_command_is_hidden(self):
        print("\n====================================")
        print("verify_set_unblock_rabbitmq_command_is_hidden")
        print("======================================")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set')
            child.expect('Infoblox >')
            output = child.before
            if 'set unblock_rabbitmq' in output:
                assert False
            else:
                assert True
        
        except Exception as error_message:
            print(error_message)
            assert False
        finally:
            child.close()
            
        print("Test Case 7 Execution Completed")
        
    @pytest.mark.run(order=8)
    def test_008_verify_show_rabbitmq_state_command_is_hidden(self):
        print("\n====================================")
        print("verify_show_rabbitmq_state_command_is_hidden")
        print("======================================")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set')
            child.expect('Infoblox >')
            output = child.before
            if 'show rabbitmq_state' in output:
                assert False
            else:
                assert True
        
        except Exception as error_message:
            print(error_message)
            assert False
        finally:
            child.close()
            
        print("Test Case 8 Execution Completed")
        

    @pytest.mark.run(order=9)
    def test_009_verify_show_rabbitmq_state_command_is_hidden(self):
        print("\n====================================")
        print("verify_show_rabbitmq_state_command_is_hidden")
        print("======================================")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set')
            child.expect('Infoblox >')
            output = child.before
            if 'show rabbitmq_state' in output:
                assert False
            else:
                assert True
        
        except Exception as error_message:
            print(error_message)
            assert False
        finally:
            child.close()
            
        print("Test Case 9 Execution Completed")

    @pytest.mark.run(order=10)
    def test_010_verify_set_update_rabbitmq_password_command_is_available(self):
        print("\n====================================")
        print("verify_set_update_rabbitmq_password_command_is_available")
        print("======================================")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set')
            child.expect('Infoblox >')
            output = child.before
            if 'set update_rabbitmq_password' in output:
                assert True
            else:
                assert False
        
        except Exception as error_message:
            print(error_message)
            assert False
        finally:
            child.close()
        sleep(120)    
        print("Test Case 10 Execution Completed")

    @pytest.mark.run(order=11)
    def test_011_execute_set_update_rabbitmq_password_command(self):
        print("\n====================================")
        print("execute_set_update_rabbitmq_password_command")
        print("======================================")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set update_rabbitmq_password')
            child.expect('Infoblox >')
            output = child.before
            if 'RabbitMQ password is already in secure mode' in output:
                assert True
            else:
                assert False
        
        except Exception as error_message:
            print(error_message)
            assert False
        finally:
            child.close()
            
        print("Test Case 11 Execution Completed")
        
        
    @pytest.mark.run(order=12)
    def test_012_create_nonsuperuser_group(self):
        print("\n====================================")
        print("create_nonsuperuser_group")
        print("======================================")
        data={"name":"test1","access_method": ["API","CLI"]}
        response = ib_NIOS.wapi_request('POST',object_type="admingroup",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: group not created")
                assert False
        else:
            print("Success: created non super user group")
            assert True

        print("Test Case 12 Execution Completed")
        
    @pytest.mark.run(order=13)
    def test_013_create_nonsuperuser_user(self):
        print("\n====================================")
        print("create_nonsuperuser_user")
        print("======================================")
        data = {"name":"test","password":"password","admin_groups": ["test1"]}
        response = ib_NIOS.wapi_request('POST',object_type="adminuser",fields=json.dumps(data))
        print(response)
        sleep(30)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: user not created")
                assert False
        else:
            print("Success: created non super user ")
            assert True

        print("Test Case 13 Execution Completed")
        
    

    @pytest.mark.run(order=14)
    def test_014_verify_set_update_rabbitmq_password_command_for_nonsuper_user(self):
        print("\n====================================")
        print("verify__disabled_set_update_rabbitmq_password_command_for_nonsuper_user")
        print("======================================")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no test@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('password')
            child.expect('Infoblox >')
            child.sendline('set update_rabbitmq_password')
            child.expect('Infoblox >')
            output = child.before
            if 'The user does not have sufficient privileges to run this command' in output:
                assert True
            else:
                assert False
        
        except Exception as error_message:
            print(error_message)
            assert False
        finally:
            child.close()
        sleep(20)    
        print("Test Case 14 Execution Completed")

    @pytest.mark.run(order=15)
    def test_015_verify_show_rabbitmq_state_command_for_nonsuper_user(self):
        print("\n====================================")
        print("verify_show_rabbitmq_state_command_for_nonsuper_user")
        print("======================================")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no test@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('password')
            child.expect('Infoblox >')
            child.sendline('show rabbitmq_state')
            child.expect('Infoblox >')
            output = child.before
            if 'The user does not have sufficient privileges to run this command' in output:
                assert True
            else:
                assert False
        
        except Exception as error_message:
            print(error_message)
            assert False
        finally:
            child.close()
            
        print("Test Case 15 Execution Completed")
        
    @pytest.mark.run(order=16)
    def test_016_verify_set_unblock_rabbitmq_command_for_nonsuper_user(self):
        print("\n====================================")
        print("verify_set_unblock_rabbitmq_command_for_nonsuper_user")
        print("======================================")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no test@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('password')
            child.expect('Infoblox >')
            child.sendline('set unblock_rabbitmq')
            child.expect('Infoblox >')
            output = child.before
            if 'The user does not have sufficient privileges to run this command' in output:
                assert True
            else:
                assert False
        
        except Exception as error_message:
            print(error_message)
            assert False
        finally:
            child.close()
        sleep(20)    
        print("Test Case 16 Execution Completed")
        
    @pytest.mark.run(order=17)
    def test_017_Enable_set_update_rabbitmq_password_command_for_nonsuper_user(self):
        print("\n====================================")
        print("Enable_set_update_rabbitmq_password_command_for_nonsuper_user")
        print("======================================")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"admin_set_commands":{"set_update_rabbitmq_password":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: command is not present in list of avaialble commands for non super users/not able to give access")
                assert False
        else:
            print("Success: enabled access for set update_rabbitmq_password command ")
            assert True
            
        print("Test Case 17 Execution Completed")
        


    @pytest.mark.run(order=18)
    def test_018_execute_set_update_rabbitmq_password_command_for_non_super_user(self):
        print("\n====================================")
        print("execute_set_update_rabbitmq_password_command")
        print("======================================")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no test@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('password')
            child.expect('Infoblox >')
            child.sendline('set update_rabbitmq_password')
            child.expect('Infoblox >')
            output = child.before
            if 'RabbitMQ password is already in secure mode' in output:
                assert True
            else:
                assert False
        
        except Exception as error_message:
            print(error_message)
            assert False
        finally:
            child.close()
            
        print("Test Case 18 Execution Completed")
        
    @pytest.mark.run(order=19)
    def test_019_validate_use_old_rabbitmq_password_field(self):
        print("\n====================================")
        print("validate_use_old_rabbitmq_password_field")
        print("======================================")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('#')
            child.sendline('''/infoblox/one/bin/db_dump -silvd /tmp/''')
            child.expect('#')
            sleep(05)
            child.sendline('''grep 'use_old_rabbitmq_password' /tmp/onedb.xml''')
            child.expect('#')
            output = child.before
            if '"use_old_rabbitmq_password" VALUE=' in output:
                assert True
            else:
                assert False
        
        except Exception as error_message:
            print(error_message)
            assert False
        finally:
            child.close()
        sleep(20)    
        print("Test Case 19 Execution Completed")   
    
        
    @pytest.mark.run(order=20)
    def test_020_execute_set_update_rabbitmq_password_command_on_member(self):
        print("\n====================================")
        print("execute_set_update_rabbitmq_password_command")
        print("======================================")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set update_rabbitmq_password')
            child.expect('Infoblox >')
            output = child.before
            if 'ERROR: This setting may only be changed on the active MASTER' in output:
                assert True
            else:
                assert False
        
        except Exception as error_message:
            print(error_message)
            assert False
        finally:
            child.close()
            
        print("Test Case 20 Execution Completed")   
        
    @pytest.mark.run(order=21)
    def test_021_check_if_rabbitmq_block_present(self):
        print("\n====================================")
        print("check if  /infoblox/var/rabbitmq_block file exists, else create it")
        print("======================================")
        sleep(450)
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('#')
            child.sendline('ls /infoblox/var/rabbitmq_block')
            sleep(05)
            child.expect('#')
            output = child.before
            print(output)
            if 'No such file or directory' in output:
                child.sendline('touch  /infoblox/var/rabbitmq_block')
                assert True
        
        except Exception as error_message:
            print(error_message)
            assert False
        finally:
            child.sendline('exit')
            
        print("Test Case 21 Execution Completed")
        

    @pytest.mark.run(order=22)
    def test_022_check_logs_if_rabbitmq_is_blocked(self):
        print("\n====================================")
        print("check_logs_if_rabbitmq_is_blocked")
        print("======================================")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        sleep(40)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        LookFor="Checks are disabled because RabbitMQ is blocked"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        print(logs)
        if logs == None:
            print("Error")
            assert False
        else:
            assert True
            print("found logs")
        print("Test Case 022 Execution Completed")
        
        
    @pytest.mark.run(order=23)
    def test_023_check_show_rabbitmq_state_after_rabbitmq_blocked(self):
        print("\n====================================")
        print("check_show_rabbitmq_state_after_rabbitmq_blocked")
        print("======================================")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('show rabbitmq_state')
            child.expect('Infoblox >')
            output = child.before
            if "RabbitMQ is blocked and will not start. Check the log for suspicious connections and unblock with 'set unblock_rabbitmq' command" in output:
                assert True
            else:
                assert False
        
        except Exception as error_message:
            print(error_message)
            assert False
        finally:
            child.close()
        sleep(20)    
        print("Test Case 23 Execution Completed")
        
        
    @pytest.mark.run(order=24)
    def test_024_unblock_rabbitmq_using_command(self):
        print("\n====================================")
        print("unblock_rabbitmq_using  set unblock_rabbitmq command")
        print("======================================")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set unblock_rabbitmq')
            child.expect(':')
            child.sendline('y')
            child.expect('Infoblox >')
            output = child.before
            if "RabbitMQ has been unblocked" in output:
                assert True
            else:
                assert False
        
        except Exception as error_message:
            print(error_message)
            assert False
        finally:
            child.close()
            
        print("Test Case 24 Execution Completed")
        
        
    @pytest.mark.run(order=25)
    def test_025_check_logs_after_rabbitmq_unblocked(self):
        print("\n====================================")
        print("check_logs_after_rabbitmq_unblocked")
        print("======================================")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        sleep(40)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        LookFor="Checks are disabled because RabbitMQ is blocked"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        print(logs)
        if logs == None:
            assert True
        else:
            assert False
            print("still rabbitmq is blocked")
        print("Test Case 025 Execution Completed")
        
    
    @pytest.mark.run(order=26)
    def test_026_check_if_rabbitmq_block_present_after_unblock(self):
        print("\n====================================")
        print("check if  /infoblox/var/rabbitmq_block file exists, after rabbitmq unblock")
        print("======================================")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('#')
            child.sendline('ls /infoblox/var/rabbitmq_block')
            sleep(05)
            child.expect('#')
            output = child.before
            print(output)
            if 'No such file or directory' in output:
                assert True
            else:
                assert False
        
        except Exception as error_message:
            print(error_message)
            assert False
        finally:
            child.sendline('exit')
        sleep(20)    
        print("Test Case 26 Execution Completed")
        
    
    @pytest.mark.run(order=27)
    def test_027_Create_RPZ_Zone(self):
        print("\n====================================")
        print("configure global forwarder,allow recursion, rpz logging and rpz zone")
        print("======================================")
        response = ib_NIOS.wapi_request('GET', object_type="grid:dns")
        response=json.loads(response)
        print(response)
        dns_ref = response[0]['_ref']
        response = ib_NIOS.wapi_request('PUT',object_type=dns_ref ,fields=json.dumps({"forwarders": ["10.39.16.160"],"allow_recursive_query": True,"logging_categories":{"log_queries": True,"log_resolver": True,"log_responses": True}}))
        print(response)
        data = {"fqdn": "NIOS_76661.com", "view":"default","grid_primary": [{"name": config.grid_fqdn,"stealth": False},{"name": config.grid_member2_fqdn,"stealth": False}]}
        zone = ib_NIOS.wapi_request('POST',object_type="zone_rp",fields=json.dumps(data))
        zone=json.loads(zone)
        print(zone)
        response1 = ib_NIOS.wapi_request('GET',object_type="grid:threatanalytics")
        response1=json.loads(response1)
        TA = response1[0]['_ref']
        response = ib_NIOS.wapi_request('PUT',object_type=TA ,fields=json.dumps({"dns_tunnel_black_list_rpz_zones":[zone]}))
        print(response)
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                assert False
            else:
                assert True

        print("Test Case 27 Execution Completed")
    
    @pytest.mark.run(order=28)
    def test_028_start_TA_service(self):
        print("\n====================================")
        print("start Threat Analytics service")
        print("======================================")
        log("start","/var/log/syslog",config.grid_vip)
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatanalytics", grid_vip=config.grid_vip)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        ref2 = json.loads(get_ref)[1]['_ref']
        ref3 = json.loads(get_ref)[2]['_ref']
        data = {"enable_service": True}
        output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
        print(output)
        output = ib_NIOS.wapi_request('PUT',ref=ref2,fields=json.dumps(data),grid_vip=config.grid_vip)
        print(output)
        output = ib_NIOS.wapi_request('PUT',ref=ref3,fields=json.dumps(data),grid_vip=config.grid_vip)
        print(output)
        print("Successfully started threat analytics service")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(90)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor="Threat Analytics service is running"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        if logs == None:
            assert False
        else:
            assert True
    print("Test Case 28 Execution Completed")
    
    @pytest.mark.run(order=29)
    def test_029_Check_Tunneling_and_if_rpz_got_added_to_bloacklist(self):
        print("\n====================================")
        print("start Threat Analytics service")
        print("======================================")
        log("start","/var/log/syslog",config.grid_member2_vip)
        sleep(10)
        record = "bugsszz.com"
        a=1
        for i in range(1,7):
            dig_cmd = 'dig @'+config.grid_member2_vip+' '+'226L01TTL-0.'+str(a)+'.'+"bug.com"+str(' IN ')+str(' TXT')
            os.system(dig_cmd)
        sleep(45)
        response1 = ib_NIOS.wapi_request('GET',object_type="record:rpz:cname")
        if "bug.com" not in response1:
            assert False            
        response1=json.loads(response1)
        print(response1)
        LookFor="DNS Tunneling detected"
        sleep(15)
        log("stop","/var/log/syslog",config.grid_member2_vip)
        logs=logv(LookFor,"/var/log/syslog",config.grid_member2_vip)
        sleep(10)
        print(logs)
        if logs == None:
            assert False
        else:
            assert True


    print("Test Case 29 Execution Completed")
    
    
    
    @pytest.mark.run(order=30)
    def test_030_create_rabbitmq_block_file(self):
        print("\n====================================")
        print("touch  /infoblox/var/rabbitmq_block file")
        print("======================================")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('#')
            child.sendline('ls /infoblox/var/rabbitmq_block')
            sleep(05)
            child.expect('#')
            output = child.before
            print(output)
            if 'No such file or directory' in output:
                child.sendline('touch  /infoblox/var/rabbitmq_block')
                assert True
        
        except Exception as error_message:
            print(error_message)
            assert False
        finally:
            child.sendline('exit')
            
        print("Test Case 30 Execution Completed")   

    
    @pytest.mark.run(order=31)
    def test_031_perform_grid_master_restart(self):
        print("\n====================================")
        print("perform_grid_master_restart")
        print("======================================")
        log("start","/var/log/syslog",config.grid_member2_vip)
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('#')
            child.sendline('/infoblox/rc restart')
            sleep(360)
        
        except Exception as error_message:
            print(error_message)
            assert False
        finally:
            child.sendline('exit')
        sleep(20)    
        print("Test Case 31 Execution Completed")

    
    @pytest.mark.run(order=32)
    def test_032_check_if_TA_restarts_after_grid_master_restarts(self):
        print("\n====================================")
        print("check if TA is getting restarted when grid master restarts")
        print("======================================")
        sleep(175)
        log("stop","/var/log/syslog",config.grid_member2_vip)
        LookFor="Restarting Threat Analytics Service because it was not running or not running correctly"
        logs=logv(LookFor,"/var/log/syslog",config.grid_member2_vip)
        if logs == None:
            assert True
        else:
            assert False
        print("Test Case 32 Execution Completed")
    
    @pytest.mark.run(order=33)
    def test_033_check_if_rabbitmq_block_got_deleted_after_master_restarts(self):
        print("\n====================================")
        print("check if rabbitmq_block flag got deleted after restart")
        print("======================================")    
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('#')
            child.sendline('ls /infoblox/var/rabbitmq_block')
            sleep(05)
            child.expect('#')
            output = child.before
            print(output)
            if 'No such file or directory' in output:
                assert True
        
        except Exception as error_message:
            print(error_message)
            assert False
        finally:
            child.sendline('exit')
            
        print("Test Case 33 Execution Completed")

    @pytest.mark.run(order=39)
    def test_039_check_rabbitmq_service_on_ha_active(self):
        print("\n====================================")
        print("heck_rabbitmq_service_on_ha_active")
        print("======================================")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_HA_ACTIVE)
            child.logfile=sys.stdout
            child.expect('#')
            child.sendline('''rabbitmqctl status''')
            child.expect('#')
            print("\n")
            output = child.before
            print(output)
            print("==============================")
            print("\n")
            data = ["Status of node rabbit","RabbitMQ","3.8.2"]
            for i in data:
                if i not in output:
                    assert False
                    print (i)
        except Exception as error_message:
            print(error_message)
            assert False
        finally:
            child.close()
        print("Test Case 039 Execution Completed")
        
    
    
    @pytest.mark.run(order=40)
    def test_040_check_rabbitmq_service_on_ha_passive(self):
        print("\n====================================")
        print("check_rabbitmq_service_on_ha_passive")
        print("======================================")
        
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_HA_PASSIVE)
            child.logfile=sys.stdout
            child.expect('#')
            child.sendline('''rabbitmqctl status''')
            child.expect('#')
            print("\n")
            output = child.before
            print(output)
            print("==============================")
            print("\n")
            data = ["Status of node rabbit","RabbitMQ","3.8.2"]
            for i in data:
                if i not in output:
                    assert False
                    print (i)
        except Exception as error_message:
            print(error_message)
            assert False
        finally:
            child.close()
        sleep(20)    
        print("Test Case 040 Execution Completed")
        
    @pytest.mark.run(order=41)
    def test_041_ssh_to_the_HA_Active_and_perform_reboot_to_make_HA_failover(self):
        
        print("\n====================================")
        print("ssh_to_the_HA_Active_and_perform_reboot_to_make_HA_failover")
        print("======================================")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_HA_ACTIVE)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('reboot')
            child.expect(':')
            child.sendline('y')
            output = child.before
            sleep(500)
            print(output)
            if prod_status(config.grid_vip):
                print("system is avaiable for testing")
                assert True
            else:
                print("system is still taking restart")
                assert False
                sleep(100)
        #sleep(120)

        except Exception as error_message:
            print(error_message)
            assert False
        finally:
            child.close()
        print("Test Case 41 Execution Completed")
        sleep(200)
    
    @pytest.mark.run(order=42)
    def test_042_Validate_status_in_HA_Passive_member_After_Failover(self):
        print("\n==================================================")
        print("Validate_running_Rabbitmq_status_in_HA_Passive_member")
        print("====================================================")
        sleep(45)
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_HA_PASSIVE)#new active
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('show status')
            child.expect('Infoblox >')
            output = child.before
            if 'Active' in output:
                assert True
            else:
                assert False
        except Exception as error_message:
            print(error_message)
            assert False
        finally:
            child.close()
        sleep(20)
        print("Test Case 042 Execution Completed")
    
    
    @pytest.mark.run(order=43)
    def test_043_Validate_running_Rabbitmq_status_in_HA_Active_member(self):
        print("\n==================================================")
        print("Validate_running_Rabbitmq_status_in_HA_Active_member")
        print("====================================================")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_HA_PASSIVE)#new active
            child.logfile=sys.stdout
            child.expect('#')
            child.sendline('''rabbitmqctl status''')
            child.expect('#')
            output = child.before
            data = ["Status of node rabbit","RabbitMQ","3.8.2"]
            for i in data:
                if i not in output:
                    assert False
                    print (i)
        except Exception as error_message:
            print(error_message)
            assert False
        finally:
            child.close()
        print("Test Case 043 Execution Completed")
        
        
    @pytest.mark.run(order=44)
    def test_044_Validate_running_Rabbitmq_status_in_HA_Passive_member(self):
        print("\n==================================================")
        print("Validate_running_Rabbitmq_status_in_HA_passive_member")
        print("====================================================")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_HA_ACTIVE)#Now passive
            child.logfile=sys.stdout
            child.expect('#')
            child.sendline('''rabbitmqctl status''')
            child.expect('#')
            output = child.before
            data = ["Status of node rabbit","RabbitMQ","3.8.2"]
            for i in data:
                if i not in output:
                    assert False
                    print (i)
        except Exception as error_message:
            print(error_message)
            assert False
        finally:
            child.close()
        sleep(20)
        print("Test Case 044 Execution Completed")
        
        
        
    @pytest.mark.run(order=45)
    def test_045_Validate_running_Rabbitmq_status_in_HA_VIP(self):
        print("\n==================================================")
        print("Validate_running_Rabbitmq_status_in_HA_passive_member")
        print("====================================================")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)#Now passive
            child.logfile=sys.stdout
            child.expect('#')
            child.sendline('''rabbitmqctl status''')
            child.expect('#')
            output = child.before
            data = ["Status of node rabbit","RabbitMQ","3.8.2"]
            for i in data:
                if i not in output:
                    assert False
                    print (i)
        except Exception as error_message:
            print(error_message)
            assert False
        finally:
            child.close()
        print("Test Case 045 Execution Completed")

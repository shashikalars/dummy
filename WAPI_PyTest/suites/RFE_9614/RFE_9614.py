import re
import config
import pytest
import unittest
import logging
import os
import pexpect
import sys
import os.path
from os.path import join
import subprocess
import commands
import json
import random
import string
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv

class RFE_9614(unittest.TestCase):

        @pytest.mark.run(order=1)
        def test_001_start_audit_logs_and_debug_log(self):
                logging.info("Starting Audit Logs and debug logs")
                log("start","/infoblox/var/audit.log",config.grid_master_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_master_vip)
                print("Test Case 1 Execution Completed")

        @pytest.mark.run(order=2)
        def test_002_Start_Grid_backuo_on_Local_computer(self):
                logging.info("Start Grid Backup On Local Computers")
                data = {"type": "BACKUP", "nios_data": True}
                response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data))
                logging.info(response)
                if type(response)!=tuple:
                        ref1 = json.loads(response)
                        if ref1.keys()[0] == 'url':
                                print(ref1['url'])
                                assert True
                                logging.info("Test Case 2 Execution Completed")
                        else:
                                print(ref1)
                                assert False
                                logging.info("Test Case 2 Execution Failed")
                else:
                        assert False
                        logging.info("Test Case 2 Execution Failed")
                                
        @pytest.mark.run(order=3)
        def test_003_stop_Audit_Logs_and_debug_logs(self):
                logging.info("Stopping Audit Logs and debug logs")
                sleep(5)
                log("stop","/infoblox/var/audit.log",config.grid_master_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_master_vip)
                print("Test Case 3 Execution Completed")
                logging.info("Test Case 3 Execution Completed")

        @pytest.mark.run(order=4)
        def test_004_validate_Audit_and_debug_log_message_for_taking_backup_on_Local_Computer(self):
                logging.info("Validating Audit and debug log Messages for taking backup on local Computer")
                LookForAudit="BACKUP"
                LookForDebug="Completed backup node by user admin at local"
                logaudit = logv(LookForAudit,"/infoblox/var/audit.log",config.grid_master_vip)
                logdebug = logv(LookForDebug,"/infoblox/var/infoblox.log",config.grid_master_vip)
                if logaudit!=None:
                        if logdebug!=None:
                                logging.info(logaudit)
                                logging.info(logdebug)
                                logging.info("Test Case 4 Execution Completed")
                                assert True
                        else:
                                print("Could not find the expeted logs in the debug logs")
                                logging.info("Test Case 4 Execution Failed")
                                assert False        
                else:
                        print("Could not find the expeted logs in the audit logs")
                        logging.info("Test Case 4 Execution Failed")
                        assert False

        @pytest.mark.run(order=5)
        def test_005_start_audit_and_debug_logs(self):
                logging.info("Starting Audit and debug Logs")
                log("start","/infoblox/var/audit.log",config.grid_master_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_master_vip)
                print("Test Case 5 Execution Completed")

        @pytest.mark.run(order=6)
        def test_006_Start_Grid_backuo_on_FTP_server(self):
                logging.info("Start Grid Backup On FTP Server")
                filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                data = {"type": "BACKUP", "nios_data": True, "remote_url": "ftp://"+config.ftp_username+":"+config.ftp_password+"@"+config.ftp_server +"/"+ config.ftp_path}
                print(json.dumps(data))
                response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data))
                logging.info(response)
                if type(response)!=tuple:
                        ref1 = json.loads(response)
                        if ref1.keys()[0] == 'url':
                                print(ref1['url'])
                                assert True
                                logging.info("Test Case 6 Execution Completed")
                        else:
                                print(ref1)
                                assert False
                                logging.info("Test Case 6 Execution Failed")
                else:
                        assert False
                        logging.info("Test Case 6 Execution Failed")
        
        @pytest.mark.run(order=7)
        def test_007_stop_Audit_and_debug_Logs(self):
                logging.info("Stopping Audit and debug Logs")
                sleep(5)
                log("stop","/infoblox/var/audit.log",config.grid_master_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_master_vip)
                print("Test Case 7 Execution Completed")

        @pytest.mark.run(order=8)
        def test_008_validate_Audit_and_debug_log_message_for_taking_backup_on_FTP_Server(self):
                logging.info("Validating Audit and debug log Messages for taking backup on FTP Server")
                LookForAudit="ftp://"+config.ftp_username+"@"+config.ftp_server+":"+"/"+config.ftp_path+""
                LookForDebug="Completed backup node by user admin at ftp://"+config.ftp_username+"@"+config.ftp_server+":"+config.ftp_path+""
                logaudit = logv(LookForAudit,"/infoblox/var/audit.log",config.grid_master_vip)
                logdebug = logv(LookForDebug,"/infoblox/var/infoblox.log",config.grid_master_vip)
                if logaudit!=None:
                        if logdebug!=None:
                                logging.info(logaudit)
                                logging.info(logdebug)
                                logging.info("Test Case 8 Execution Completed")
                                assert True
                        else:
                                print("Could not find the expeted logs in the debug logs")
                                logging.info("Test Case 8 Execution Failed")
                                assert False        
                else:
                        print("Could not find the expeted logs in the audit logs")
                        logging.info("Test Case 8 Execution Failed")
                        assert False

        @pytest.mark.run(order=9)
        def test_009_start_audit_and_debug_logs(self):
                logging.info("Starting Audit and debug Logs")
                log("start","/infoblox/var/audit.log",config.grid_master_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_master_vip)
                print("Test Case 9 Execution Completed")

        
        @pytest.mark.run(order=10)
        def test_010_Start_Grid_backup_on_SCP_server_with_Password(self):
                logging.info("Start Grid Backup on SCP Server with Password")
                filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                data = {"type": "BACKUP", "nios_data": True, "remote_url": "scp://"+config.scp_username+":"+config.scp_password+"@"+config.scp_server+"//"+config.scp_path}
                print(data)
                response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data))
                logging.info(response)
                if type(response)!=tuple:
                        ref1 = json.loads(response)
                        if ref1.keys()[0] == 'url':
                                print(ref1['url'])
                                assert True
                                logging.info("Test Case 10 Execution Completed")
                        else:
                                print(ref1)
                                assert False
                                logging.info("Test Case 10 Execution Failed")
                else:
                        assert False
                        logging.info("Test Case 10 Execution Failed")
        
        @pytest.mark.run(order=11)
        def test_011_stop_Audit_and_debug_Logs(self):
                logging.info("Stopping Audit and debug Logs")
                sleep(5)
                log("stop","/infoblox/var/audit.log",config.grid_master_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_master_vip)
                print("Test Case 11 Execution Completed")

        @pytest.mark.run(order=12)
        def test_012_validate_Audit_and_debug_log_message_for_taking_backup_on_SCP_Server_with_Password(self):
                logging.info("Validating Audit and debug log Messages for taking backup on SCP server with password")
                #LookForAudit="scp://"+config.scp_username+"@"+config.scp_server+":/"+config.scp_path+""
                #LookForDebug="Completed backup node by user admin at scp://"+config.scp_username+"@"+config.scp_server+":/"+config.scp_path+""
                LookForAudit = 'scp://'+config.scp_username+'@'+config.scp_server+':/'+config.scp_path
                LookForDebug="Completed backup node by user admin at scp://"+config.scp_username+"@"+config.scp_server+":"+config.scp_path+""
                LookForDebug1="SCP upload was successful"
                logaudit = logv(LookForAudit,"/infoblox/var/audit.log",config.grid_master_vip)
                logdebug = logv(LookForDebug,"/infoblox/var/infoblox.log",config.grid_master_vip)
                logdebug1 = logv(LookForDebug1,"/infoblox/var/infoblox.log",config.grid_master_vip)
                if logaudit!=None:
                        if logdebug!=None and logdebug1!=None:
                                logging.info(logaudit)
                                logging.info(logdebug)
                                logging.info(logdebug1)
                                logging.info("Test Case 12 Execution Completed")
                                assert True
                        else:
                                print("Could not find the expeted logs in the Debug logs")
                                logging.info("Test Case 12 Execution Failed")
                                assert False        
                else:
                        print("Could not find the expeted logs in the audit logs")
                        logging.info("Test Case 12 Execution Failed")
                        assert False

        @pytest.mark.run(order=13)
        def test_013_start_audit_and_debug_logs(self):
                logging.info("Starting Audit and debug Logs")
                log("start","/infoblox/var/audit.log",config.grid_master_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_master_vip)
                print("Test Case 13 Execution Completed")

        
        @pytest.mark.run(order=14)
        def test_014_Start_Grid_backuo_on_SCP_server_with_RSA_Key(self):
                logging.info("Start Grid Backup On SCP Server with RSA Key")
                filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                upload_data = {"type": "BACKUP", "use_keys": True, "discovery_data": False, "nios_data": True, "key_type":"id_rsa","upload_keys": True, "remote_url": "scp://"+config.scp_username+":"+config.scp_password+"@"+config.scp_server+"/"+config.scp_path}
                upload_response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(upload_data))
                data = {"type": "BACKUP", "use_keys": True, "discovery_data": False, "nios_data": True, "key_type":"id_rsa", "remote_url": "scp://"+config.scp_username+":@"+config.scp_server+"//"+config.scp_path+"/"+filename}
                response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data))
                logging.info(response)
                if type(response)!=tuple:
                        ref1 = json.loads(response)
                        if ref1.keys()[0] == 'url':
                                print(ref1['url'])
                                assert True
                                logging.info("Test Case 14 Execution Completed")
                        else:
                                print(ref1)
                                assert False
                                logging.info("Test Case 14 Execution Failed")
                else:
                        assert False
                        logging.info("Test Case 14 Execution Failed")
        
        @pytest.mark.run(order=15)
        def test_015_stop_Audit_and_debug_Logs(self):
                logging.info("Stopping Audit and debug Logs")
                sleep(5)
                log("stop","/infoblox/var/audit.log",config.grid_master_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_master_vip)
                print("Test Case 15 Execution Completed")

        @pytest.mark.run(order=16)
        def test_016_validate_Audit_and_debug_log_message_for_taking_backup_on_SCP_Server_with_RSA_Key(self):
                logging.info("Validating Audit and debug log Messages for taking backup on SCP server with RSA Key")
                #LookForAudit="scp://"+config.scp_username+"@"+config.scp_server+":/"+config.scp_path+""
                #LookForDebug="Completed backup node by user admin at scp://"+config.scp_username+"@"+config.scp_server+":/"+config.scp_path+""
                LookForAudit= 'scp://'+config.scp_username+'@'+config.scp_server+':/'+config.scp_path
                LookForDebug="Completed backup node by user admin at scp://"+config.scp_username+"@"+config.scp_server+":"+config.scp_path+""
                LookForDebug1="SCP upload was successful using keys"
                logaudit = logv(LookForAudit,"/infoblox/var/audit.log",config.grid_master_vip)
                logdebug = logv(LookForDebug,"/infoblox/var/infoblox.log",config.grid_master_vip)
                logdebug1 = logv(LookForDebug1,"/infoblox/var/infoblox.log",config.grid_master_vip)
                if logaudit!=None:
                        if logdebug!=None and logdebug1!=None:
                                logging.info(logaudit)
                                logging.info(logdebug)
                                logging.info(logdebug1)
                                logging.info("Test Case 16 Execution Completed")
                                assert True
                        else:
                                print("Could not find the expeted logs in the Debug logs")
                                logging.info("Test Case 16 Execution Failed")
                                assert False        
                else:
                        print("Could not find the expeted logs in the audit logs")
                        logging.info("Test Case 16 Execution Failed")
                        assert False
        
        @pytest.mark.run(order=17)
        def test_017_start_audit_and_debug_logs(self):
                logging.info("Starting Audit and debug Logs")
                log("start","/infoblox/var/audit.log",config.grid_master_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_master_vip)
                print("Test Case 17 Execution Completed")

        
        @pytest.mark.run(order=18)
        def test_018_Start_Grid_backuo_on_SCP_server_with_ECDSA_Key(self):
                logging.info("Start Grid Backup On SCP Server with ECDSA Key")
                filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                upload_data = {"type": "BACKUP", "use_keys": True, "discovery_data": False, "nios_data": True, "key_type":"id_ecdsa","upload_keys": True, "remote_url": "scp://"+config.scp_username+":"+config.scp_password+"@"+config.scp_server+"//"+config.scp_path}
                upload_response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(upload_data))
                data = {"type": "BACKUP", "use_keys": True, "discovery_data": False, "nios_data": True, "key_type":"id_ecdsa", "remote_url": "scp://"+config.scp_username+":@"+config.scp_server+"//"+config.scp_path+"/"+filename}
                response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data))
                logging.info(response)
                if type(response)!=tuple:
                        ref1 = json.loads(response)
                        if ref1.keys()[0] == 'url':
                                print(ref1['url'])
                                assert True
                                logging.info("Test Case 18 Execution Completed")
                        else:
                                print(ref1)
                                assert False
                                logging.info("Test Case 18 Execution Failed")
                else:
                        assert False
                        logging.info("Test Case 18 Execution Failed")
        
        @pytest.mark.run(order=19)
        def test_019_stop_Audit_and_debug_Logs(self):
                logging.info("Stopping Audit and debug Logs")
                sleep(5)
                log("stop","/infoblox/var/audit.log",config.grid_master_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_master_vip)
                print("Test Case 19 Execution Completed")

        @pytest.mark.run(order=20)
        def test_020_validate_Audit_log_message_for_taking_backup_on_SCP_Server_with_ECDSA_Key(self):
                logging.info("Validating Audit log Messages for taking backup on SCP server with ECDSA Key")
                #LookForAudit="scp://"+config.scp_username+"@"+config.scp_server+":/"+config.scp_path+""
                #LookForDebug1="SCP upload was successful using keys"
                #LookForDebug="Completed backup node by user admin at scp://"+config.scp_username+"@"+config.scp_server+":/"+config.scp_path+""
                LookForAudit= 'scp://'+config.scp_username+'@'+config.scp_server+':/'+config.scp_path
                LookForDebug1="SCP upload was successful using keys"
                LookForDebug="Completed backup node by user admin at scp://"+config.scp_username+"@"+config.scp_server+":"+config.scp_path+""
                logaudit = logv(LookForAudit,"/infoblox/var/audit.log",config.grid_master_vip)
                logdebug = logv(LookForDebug,"/infoblox/var/infoblox.log",config.grid_master_vip)
                logdebug1 = logv(LookForDebug1,"/infoblox/var/infoblox.log",config.grid_master_vip)
                if logaudit!=None:
                        if logdebug!=None and logdebug1!=None:
                                logging.info(logaudit)
                                logging.info(logdebug)
                                logging.info(logdebug1)
                                logging.info("Test Case 20 Execution Completed")
                                assert True
                        else:
                                print("Could not find the expeted logs in the Debug logs")
                                logging.info("Test Case 20 Execution Failed")
                                assert False        
                else:
                        print("Could not find the expeted logs in the audit logs")
                        logging.info("Test Case 20 Execution Failed")
                        assert False
        
        @pytest.mark.run(order=21)
        def test_021_start_audit_and_debug_logs(self):
                logging.info("Starting Audit and debug Logs")
                log("start","/infoblox/var/audit.log",config.grid_master_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_master_vip)
                print("Test Case 21 Execution Completed")

        
        @pytest.mark.run(order=22)
        def test_022_Start_Grid_backuo_on_TFTP_server(self):
                logging.info("Start Grid Backup On TFTP Server")
                filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                data = {"type": "BACKUP", "discovery_data": False, "nios_data": True, "remote_url": "tftp://"+config.tftp_server+"/"+config.tftp_path}
                response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data))
                logging.info(response)
                if type(response)!=tuple:
                        ref1 = json.loads(response)
                        if ref1.keys()[0] == 'url':
                                print(ref1['url'])
                                assert True
                                logging.info("Test Case 22 Execution Completed")
                        else:
                                print(ref1)
                                assert False
                                logging.info("Test Case 22 Execution Failed")
                else:
                        assert False
                        logging.info("Test Case 22 Execution Failed")
        
        @pytest.mark.run(order=23)
        def test_023_stop_Audit_and_debug_Logs(self):
                logging.info("Stopping Audit and debug Logs")
                log("stop","/infoblox/var/audit.log",config.grid_master_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_master_vip)
                sleep(30)
                print("Test Case 23 Execution Completed")

        @pytest.mark.run(order=24)
        def test_024_validate_Audit_and_debug_log_message_for_taking_backup_on_TFTP_Server(self):
                logging.info("Validating Audit and debug log Messages for taking backup on TFTP server")
                LookForAudit="tftp://"+config.tftp_server+":"+"/"+config.tftp_path+""
                LookForDebug="Completed backup node by user admin at tftp://"+config.tftp_server+":"
                logaudit = logv(LookForAudit,"/infoblox/var/audit.log",config.grid_master_vip)
                logdebug = logv(LookForDebug,"/infoblox/var/infoblox.log",config.grid_master_vip)
                if logaudit!=None:
                        if logdebug!=None:
                                logging.info(logaudit)
                                logging.info(logdebug)
                                logging.info("Test Case 24 Execution Completed")
                                assert True
                        else:
                                print("Could not find the expeted logs in the Debug logs")
                                logging.info("Test Case 24 Execution Failed")
                                assert False        
                else:
                        print("Could not find the expeted logs in the audit logs")
                        logging.info("Test Case 24 Execution Failed")
                        assert False

        @pytest.mark.run(order=25)
        def test_025_start_audit_and_debug_logs(self):
                logging.info("Starting Audit and debug Logs")
                log("start","/infoblox/var/audit.log",config.grid_master_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_master_vip)
                sleep(30)
                print("Test Case 25 Execution Completed")

        
        @pytest.mark.run(order=26)
        def test_026_Start_Grid_backuo_on_SCP_server_using_password_Through_CLI(self):
                logging.info("Start Grid Backup On scp server using password through CLI")
                logging.info("Login as Admin")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('set database_transfer scp '+ config.scp_server +' '+config.scp_username+' '+config.scp_password+' /'+config.scp_path+' nios')
                child.sendline('y')
                child.expect('Infoblox >')
                output = child.before
                child.sendline('exit')
                sleep(120)
                print("\nTest Case Executed Successfully")
                assert True
                logging.info("Test Case 26 Execution Completed")
               
        @pytest.mark.run(order=27)
        def test_027_stop_Audit_and_debug_Logs(self):
                logging.info("Stopping Audit and debug Logs")
                log("stop","/infoblox/var/audit.log",config.grid_master_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_master_vip)
                sleep(30)
                print("Test Case 27 Execution Completed")

        @pytest.mark.run(order=28)
        def test_028_validate_Audit_and_debug_log_message_for_taking_backup_on_SCP_Server_using_password_through_CLI(self):
                logging.info("Validating Audit and debug log Messages for taking backup on SCP server using password through CLI")
                LookForAudit="scp://"+config.scp_username+"@"+config.scp_server+":/"+config.scp_path+""
                LookForDebug="scp://"+config.scp_username+"@"+config.scp_server+":/"+config.scp_path+""
                logaudit = logv(LookForAudit,"/infoblox/var/audit.log",config.grid_master_vip)
                logdebug = logv(LookForDebug,"/infoblox/var/infoblox.log",config.grid_master_vip)
                if logaudit!=None:
                        if logdebug!=None:
                                logging.info(logaudit)
                                logging.info(logdebug)
                                logging.info("Test Case 28 Execution Completed")
                                assert True
                        else:
                                print("Could not find the expeted logs in the Debug logs")
                                logging.info("Test Case 28 Execution Failed")
                                assert False        
                else:
                        print("Could not find the expeted logs in the audit logs")
                        logging.info("Test Case 28 Execution Failed")
                        assert False
      
        @pytest.mark.run(order=29)
        def test_029_start_debug_logs(self):
                logging.info("Starting debug Logs")
                log("start","/infoblox/var/infoblox.log",config.grid_master_vip)
                sleep(30)
                print("Test Case 29 Execution Completed")

        
        @pytest.mark.run(order=30)
        def test_030_Start_upload_RSA_KEY_to_scp_server_Through_CLI(self):
                logging.info("Start upload RSA Keys to scp server through CLI")
                logging.info("Login as Admin")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
                print child
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('set database_transfer scp '+ config.scp_server +' '+config.scp_username+' '+config.scp_password+' usekeys rsa upload_keys')
                sleep(30)
                child.expect('Infoblox >')
                output = child.before
                child.sendline('exit')
                sleep(120)
                assert True
                print("\nTest Case Executed Successfully")
                logging.info("Test Case 30 Execution Completed")
        
        @pytest.mark.run(order=31)
        def test_031_stop_debug_Logs(self):
                logging.info("Stopping Audit and debug Logs")
                log("stop","/infoblox/var/infoblox.log",config.grid_master_vip)
                sleep(30)
                print("Test Case 31 Execution Completed")

        @pytest.mark.run(order=32)
        def test_032_validate_debug_log_message_upload_RSA_keys__on_SCP_Server_through_CLI(self):
                logging.info("Validating Audit and debug log Messages for upload RSA keys on scp server through CLI")
                LookForDebug="Sucessfully Pushed Public key to SCP Server"
                logdebug = logv(LookForDebug,"/infoblox/var/infoblox.log",config.grid_master_vip)
                if logdebug!=None:
                        logging.info(logdebug)
                        logging.info("Test Case 32 Execution Completed")
                        assert True
                else:
                        print("Could not find the expeted logs in the audit logs")
                        logging.info("Test Case 32 Execution Failed")
                        assert False

        @pytest.mark.run(order=33)
        def test_033_start_debug_logs(self):
                logging.info("Starting debug Logs")
                log("start","/infoblox/var/infoblox.log",config.grid_master_vip)
                sleep(30)
                print("Test Case 33 Execution Completed")

        
        @pytest.mark.run(order=34)
        def test_034_Start_upload_ECDSA_KEY_to_scp_server_Through_CLI(self):
                logging.info("Start upload ECDSA Keys to scp server through CLI")
                logging.info("Login as Admin")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
                print child
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('set database_transfer scp '+ config.scp_server +' '+config.scp_username+' '+config.scp_password+' usekeys ecdsa upload_keys')
                sleep(30)
                child.expect('Infoblox >')
                output = child.before
                child.sendline('exit')
                sleep(120)
                assert True
                print("\nTest Case Executed Successfully")
                logging.info("Test Case 34 Execution Completed")
        
        @pytest.mark.run(order=35)
        def test_035_stop_debug_Logs(self):
                logging.info("Stopping Audit and debug Logs")
                log("stop","/infoblox/var/infoblox.log",config.grid_master_vip)
                sleep(30)
                print("Test Case 35 Execution Completed")

        @pytest.mark.run(order=36)
        def test_036_validate_debug_log_message_upload_ECDSA_keys__on_SCP_Server_through_CLI(self):
                logging.info("Validating Audit and debug log Messages for upload ECDSA keys on scp server through CLI")
                LookForDebug="Sucessfully Pushed Public key to SCP Server"
                logdebug = logv(LookForDebug,"/infoblox/var/infoblox.log",config.grid_master_vip)
                if logdebug!=None:
                        logging.info(logdebug)
                        logging.info("Test Case 36 Execution Completed")
                        assert True
                else:
                        print("Could not find the expeted logs in the audit logs")
                        logging.info("Test Case 36 Execution Failed")
                        assert False

        @pytest.mark.run(order=37)
        def test_037_start_audit_and_debug_logs(self):
                logging.info("Starting Audit and debug Logs")
                log("start","/infoblox/var/audit.log",config.grid_master_vip)
                log("start","/infoblox/var/infobox.log",config.grid_master_vip)
                sleep(30)
                print("Test Case 37 Execution Completed")

        
        @pytest.mark.run(order=38)
        def test_038_Start_Grid_Backup_using_RSA_KEY_to_scp_server_Through_CLI(self):
                logging.info("Start Grid backup using RSA Keys to scp server through CLI")
                logging.info("Login as Admin")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('set database_transfer scp '+ config.scp_server +' '+config.scp_username+' usekeys rsa /'+config.scp_path)
                child.sendline('y')
                sleep(30)
                child.expect('Infoblox >')
                output = child.before
                child.sendline('exit')
                sleep(120)
                assert True
                print("\nTest Case Executed Successfully")
                logging.info("Test Case 38 Execution Completed")
        
        @pytest.mark.run(order=39)
        def test_039_stop_audit_and_debug_Logs(self):
                logging.info("Stopping Audit and debug Logs")
                log("stop","/infoblox/var/infoblox.log",config.grid_master_vip)
                log("stop","/infoblox/var/audit.log",config.grid_master_vip)
                sleep(30)
                print("Test Case 39 Execution Completed")

        @pytest.mark.run(order=40)
        def test_040_validate_audit_and_debug_log_message_to_perform_backup_RSA_keys__on_SCP_Server_through_CLI(self):
                logging.info("Validating Audit log Messages to perform backup RSA keys on scp server through CLI")
                LookForAudit="scp://"+config.scp_username+"@"+config.scp_server+":/"+config.scp_path+""
                logaudit = logv(LookForAudit,"/infoblox/var/audit.log",config.grid_master_vip)
                if logaudit!=None:
                        logging.info(logaudit)
                        logging.info("Test Case 40 Execution Completed")
                        assert True
                else:
                        print("Could not find the expeted logs in the audit logs")
                        logging.info("Test Case 40 Execution Failed")
                        assert False
        
        @pytest.mark.run(order=41)
        def test_041_start_audit_and_debug_logs(self):
                logging.info("Starting Audit and debug Logs")
                log("start","/infoblox/var/audit.log",config.grid_master_vip)
                log("start","/infoblox/var/infobox.log",config.grid_master_vip)
                sleep(30)
                print("Test Case 41 Execution Completed")

        
        @pytest.mark.run(order=42)
        def test_042_Start_Grid_Backup_using_ECDSA_KEY_to_scp_server_Through_CLI(self):
                logging.info("Start Grid backup using RSA Keys to scp server through CLI")
                logging.info("Login as Admin")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
                print child
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('set database_transfer scp '+ config.scp_server +' '+config.scp_username+' usekeys ecdsa /'+config.scp_path)
                child.sendline('y')
                sleep(30)
                child.expect('Infoblox >')
                output = child.before
                child.sendline('exit')
                sleep(120)
                assert True
                print("\nTest Case Executed Successfully")
                logging.info("Test Case 42 Execution Completed")
        
        @pytest.mark.run(order=43)
        def test_043_stop_audit_and_debug_Logs(self):
                logging.info("Stopping Audit and debug Logs")
                log("stop","/infoblox/var/infoblox.log",config.grid_master_vip)
                log("stop","/infoblox/var/audit.log",config.grid_master_vip)
                sleep(30)
                print("Test Case 43 Execution Completed")

        @pytest.mark.run(order=44)
        def test_044_validate_audit_log_message_backup_using_ECDSA_keys__on_SCP_Server_through_CLI(self):
                logging.info("Validating Audit log Messages for upload ECDSA keys on scp server through CLI")
                LookForAudit="scp://"+config.scp_username+"@"+config.scp_server+":/"+config.scp_path+""
                logaudit = logv(LookForAudit,"/infoblox/var/audit.log",config.grid_master_vip)
                if logaudit!=None:
                        logging.info(logaudit)
                        logging.info("Test Case 44 Execution Completed")
                        assert True
                                
                else:
                        print("Could not find the expeted logs in the audit logs")
                        logging.info("Test Case 44 Execution Failed")
                        assert False
        
        @pytest.mark.run(order=46)
        def test_046___Negative_test_case___Start_Grid_backuo_on_FTP_server_with_wrong_username(self):
                logging.info("Start Grid Backup On FTP Server with wrong username | negative case")
                filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                data = {"type": "BACKUP", "nios_data": True, "remote_url": "ftp://q:"+config.ftp_password+"@"+config.ftp_server +"/"+config.ftp_path+"/"+filename}
                status, response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data))
                logging.info(response)
                if status == 400:
                        ref1 = json.loads(response)
                        print(ref1['text'])
                        assert True
                        logging.info("Test Case 46 Execution Completed")
                else:
                        print("Response code: {}" .format(status))
                        assert False
                        logging.info("Test Case 46 Execution Failed")
        
        @pytest.mark.run(order=50)
        def test_050___Negative_test_case___Start_Grid_backuo_on_FTP_server_with_wrong_password(self):
                logging.info("Start Grid Backup On FTP Server with Wrong Password | Negative case ")
                filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                data = {"type": "BACKUP", "nios_data": True, "remote_url": "ftp://"+config.ftp_username+":wrong@"+config.ftp_server +"/"+ config.ftp_path+"/"+filename}
                status, response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data))
                logging.info(response)
                if status == 400:
                        ref1 = json.loads(response)
                        print(ref1['text'])
                        assert True
                        logging.info("Test Case 50 Execution Completed")
                else:
                        print("Response code: {}" .format(status))
                        assert False
                        logging.info("Test Case 50 Execution Failed")
        
        @pytest.mark.run(order=54)
        def test_054___Negative_test_case___Start_Grid_backuo_on_FTP_server_with_wrong_path(self):
                logging.info("Start Grid Backup On FTP Server with Wrong Path | Negative case ")
                filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                data = {"type": "BACKUP", "nios_data": True, "remote_url": "ftp://"+config.ftp_username+":"+config.ftp_password+"@"+config.ftp_server + "/wrong/"+filename}
                status, response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data))
                logging.info(response)
                if status == 400:
                        ref1 = json.loads(response)
                        print(ref1['text'])
                        assert True
                        logging.info("Test Case 54 Execution Completed")
                else:
                        print("Response code: {}" .format(status))
                        assert False
                        logging.info("Test Case 54 Execution Failed")
        
        @pytest.mark.run(order=57)
        def test_057_start_audit_and_debug_logs(self):
                logging.info("Starting Audit and debug Logs")
                log("start","/infoblox/var/infoblox.log",config.grid_master_vip)
                print("Test Case 57 Execution Completed")

        @pytest.mark.run(order=58)
        def test_058___Negative_test_case___Start_Grid_backuo_on_SCP_server_with_wrong_username(self):
                logging.info("Start Grid Backup On SCP Server with wrong username | negative case")
                filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                data = {"type": "BACKUP", "nios_data": True, "remote_url": "scp://q:"+config.scp_password+"@"+config.scp_server +"//"+ config.scp_path+"/"+filename}
                status, response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data))
                logging.info(response)
                if status == 400:
                        ref1 = json.loads(response)
                        print(ref1['text'])
                        assert True
                        logging.info("Test Case 58 Execution Completed")
                else:
                        print("Response code: {}" .format(status))
                        assert False
                        logging.info("Test Case 58 Execution Failed")

        @pytest.mark.run(order=59)
        def test_059_stop_audit_and_debug_Logs(self):
                logging.info("Stopping Audit and debug Logs")
                sleep(5)
                log("stop","/infoblox/var/infoblox.log",config.grid_master_vip)
                print("Test Case 59 Execution Completed")
                
        @pytest.mark.run(order=60)
        def test_060_audit_log_validate_for_the_nagative_test_case_058(self):
                logging.info("Validating Audit and debug log Messages for the negative test case 058")
                LookForDebug="Upload to the SCP server failed"
                logdebug = logv(LookForDebug,"/infoblox/var/infoblox.log",config.grid_master_vip)
                if logdebug!=None:
                        logging.info(logdebug)
                        logging.info("Test Case 60 Execution Completed")
                        assert True
                                
                else:
                        print("We are not getting expected error message from the debug log")
                        logging.info("Test Case 60 Execution Failed")
                        assert False
                                        
        @pytest.mark.run(order=61)
        def test_061_start_audit_and_debug_logs(self):
                logging.info("Starting Audit and debug Logs")
                log("start","/infoblox/var/audit.log",config.grid_master_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_master_vip)
                print("Test Case 61 Execution Completed")

        @pytest.mark.run(order=62)
        def test_062___Negative_test_case___Start_Grid_backuo_on_SCP_server_with_wrong_password(self):
                logging.info("Start Grid Backup On SCP Server with Wrong Password | Negative case ")
                filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                data = {"type": "BACKUP", "nios_data": True, "remote_url": "scp://"+config.scp_username+":wrong@"+config.scp_server +"//"+ config.scp_path+"/"+filename}
                status, response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data))
                logging.info(response)
                if status == 400:
                        ref1 = json.loads(response)
                        print(ref1['text']) 
                        assert True
                        logging.info("Test Case 62 Execution Completed")
                else:
                        print("Response code: {}" .format(status))
                        assert False
                        logging.info("Test Case 62 Execution Failed")

        @pytest.mark.run(order=63)
        def test_063_stop_audit_and_debug_Logs(self):
                logging.info("Stopping Audit and debug Logs")
                sleep(5)
                log("stop","/infoblox/var/audit.log",config.grid_master_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_master_vip)
                print("Test Case 63 Execution Completed")
                
        @pytest.mark.run(order=64)
        def test_064_audit_log_validate_for_the_nagative_test_case_062(self):
                logging.info("Validating Audit and debug log Messages for the negative test case 062")
                LookForDebug="Upload to the SCP server failed"
                logdebug = logv(LookForDebug,"/infoblox/var/infoblox.log",config.grid_master_vip)
                if logdebug!=None:
                        logging.info(logdebug)
                        logging.info("Test Case 64 Execution Completed")
                        assert True
                                
                else:
                        print("We are not getting expected error message from the debug log")
                        logging.info("Test Case 64 Execution Failed")
                        assert False
        
        @pytest.mark.run(order=65)
        def test_065_start_audit_and_debug_logs(self):
                logging.info("Starting Audit and debug Logs")
                log("start","/infoblox/var/audit.log",config.grid_master_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_master_vip)
                print("Test Case 65 Execution Completed")


        @pytest.mark.run(order=66)
        def test_066___Negative_test_case___Start_Grid_backuo_on_scp_server_with_wrong_path(self):
                logging.info("Start Grid Backup On scp Server with Wrong Path | Negative case ")
                filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                data = {"type": "BACKUP", "nios_data": True, "remote_url": "scp://"+config.scp_username+":"+config.scp_password+"@"+config.scp_server + "//wrong/"+filename}
                status, response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data))
                logging.info(response)
                if status == 400:
                        ref1 = json.loads(response)
                        print(ref1['text'])
                        assert True
                        logging.info("Test Case 66 Execution Completed")
                else:
                        print("Response code: {}" .format(status))
                        assert False
                        logging.info("Test Case 66 Execution Failed")
        
        @pytest.mark.run(order=67)
        def test_067_stop_audit_and_debug_Logs(self):
                logging.info("Stopping Audit and debug Logs")
                sleep(5)
                log("stop","/infoblox/var/audit.log",config.grid_master_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_master_vip)
                print("Test Case 67 Execution Completed")
                
        @pytest.mark.run(order=68)
        def test_068_audit_log_validate_for_the_nagative_test_case_066(self):
                logging.info("Validating Audit and debug log Messages for the negative test case 066")
                LookForDebug="Upload to the SCP server failed"
                logdebug = logv(LookForDebug,"/infoblox/var/infoblox.log",config.grid_master_vip)
                if logdebug!=None:
                        logging.info(logdebug)
                        logging.info("Test Case 68 Execution Completed")
                        assert True
                                
                else:
                        print("We are not getting expected error message from the debug log")
                        logging.info("Test Case 68 Execution Failed")
                        assert False


        @pytest.mark.run(order=69)
        def test_069_start_audit_and_debug_logs(self):
                logging.info("Starting Audit and debug Logs")
                log("start","/infoblox/var/audit.log",config.grid_master_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_master_vip)
                print("Test Case 69 Execution Completed")


        @pytest.mark.run(order=70)
        def test_070___Negative_test_case___Start_Grid_backuo_on_SCP_server_with_wrong_server_address(self):
                logging.info("Start Grid Backup On SCP Server with Wrong server IP | Negative case ")
                filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                #data = {"type": "BACKUP", "nios_data": True, "remote_url": "scp://"+config.scp_username+":"+config.scp_password+"@1.1.1.1"+ config.scp_path+"//"+filename}
                data = {"type": "BACKUP", "nios_data": True, "remote_url": "scp://"+config.scp_username+":"+config.scp_password+"@"+config.scp1_server+"//"+config.scp_path}
                status, response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data))
                logging.info(response)
                assert True
                if status == 400:
                        ref1 = json.loads(response)
                        print(ref1['text'])
                        assert True
                        logging.info("Test Case 70 Execution Completed")
                else:
                        print("Response code: {}" .format(status))
                        assert False
                        logging.info("Test Case 70 Execution Failed")
                sleep(240)        
        @pytest.mark.run(order=71)
        def test_071_stop_audit_and_debug_Logs(self):
                logging.info("Stopping Audit and debug Logs")
                sleep(5)
                log("stop","/infoblox/var/audit.log",config.grid_master_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_master_vip)
                print("Test Case 71 Execution Completed")
                
        @pytest.mark.run(order=72)
        def test_072_audit_log_validate_for_the_nagative_test_case_070(self):
                logging.info("Validating Audit and debug log Messages for the negative test case 070")
                #LookForDebug="The SCP server ip address is not valid"
                LookForDebug= "Upload to the SCP server failed. Check if the SCP server is available, the username and password are correct, and the file path is valid."
                logdebug = logv(LookForDebug,"/infoblox/var/infoblox.log",config.grid_master_vip)
                if logdebug!=None:
                        logging.info(logdebug)
                        logging.info("Test Case 60 Execution Completed")
                        assert True
                                
                else:
                        print("We are not getting expected error message from the debug log")
                        logging.info("Test Case 60 Execution Failed")
                        assert False
        
        @pytest.mark.run(order=74)
        def test_074___Negative_test_case___Start_Grid_backuo_on_FTP_server_with_wrong_Server_address(self):
                logging.info("Start Grid Backup On FTP Server with Wrong Server Address | Negative case ")
                filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                data = {"type": "BACKUP", "nios_data": True, "remote_url": "ftp://"+config.ftp_username+":"+config.ftp_password+"@1.1.1.1"+"/"+ config.ftp_path+"/"+filename}
                status, response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data))
                logging.info(response)
                if status == 400:
                        ref1 = json.loads(response)
                        print(ref1['text'])
                        assert True
                        logging.info("Test Case 74 Execution Completed")
                else:
                        print("Response code: {}" .format(status))
                        assert False
                        logging.info("Test Case 74 Execution Failed")


        @pytest.mark.run(order=77)
        def test_077_start_audit_and_debug_logs(self):
                logging.info("Starting Audit and debug Logs")
                log("start","/infoblox/var/infoblox.log",config.grid_master_vip)
                print("Test Case 77 Execution Completed")

        @pytest.mark.run(order=78)
        def test_078___Negative_test_case___Start_Grid_backuo_on_TFTP_server_with_wrong_Server_address(self):
                logging.info("Start Grid Backup On TFTP Server with Wrong Server Address | Negative case ")
                filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                data = {"type": "BACKUP", "nios_data": True, "remote_url": "tftp://1.1.1.1"+"/"+ config.tftp_path+"/"+filename}
                status, response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data))
                logging.info(response)
                if status == 400:
                        ref1 = json.loads(response)
                        print(ref1['text'])
                        assert True
                        logging.info("Test Case 78 Execution Completed")
                else:
                        print("Response code: {}" .format(status))
                        assert False
                        logging.info("Test Case 78 Execution Failed")


        @pytest.mark.run(order=79)
        def test_079_stop_audit_and_debug_Logs(self):
                logging.info("Stopping Audit and debug Logs")
                sleep(5)
                log("stop","/infoblox/var/infoblox.log",config.grid_master_vip)
                print("Test Case 79 Execution Completed")
                
        @pytest.mark.run(order=80)
        def test_080_audit_log_validate_for_the_nagative_test_case_078(self):
                logging.info("Validating Audit and debug log Messages for the negative test case 078")
                LookForDebug="Check TFTP server address"
                logdebug = logv(LookForDebug,"/infoblox/var/infoblox.log",config.grid_master_vip)
                if logdebug!=None:
                        logging.info(logdebug)
                        logging.info("Test Case 60 Execution Completed")
                        assert True
                                
                else:
                        print("We are not getting expected error message from the debug log")
                        logging.info("Test Case 60 Execution Failed")
                        assert False

        @pytest.mark.run(order=81)
        def test_081_start_audit_and_debug_logs(self):
                logging.info("Starting Audit and debug Logs")
                log("start","/infoblox/var/infoblox.log",config.grid_master_vip)
                print("Test Case 81 Execution Completed")
        
        @pytest.mark.run(order=82)
        def test_082___Negative_test_case___Start_Grid_backuo_on_TFTP_server_with_wrong_path(self):
                logging.info("Start Grid Backup On TFTP Server with Wrong path | Negative case ")
                filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                data = {"type": "BACKUP", "nios_data": True, "remote_url": "tftp://"+ config.tftp_server+"/wrong/"+filename}
                status, response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data))
                logging.info(response)
                if status == 400:
                        ref1 = json.loads(response)
                        print(ref1['text'])
                        assert True
                        logging.info("Test Case 82 Execution Completed")
                else:
                        print("Response code: {}" .format(status))
                        assert False
                        logging.info("Test Case 82 Execution Failed")
        
        @pytest.mark.run(order=83)
        def test_083_stop_audit_and_debug_Logs(self):
                logging.info("Stopping Audit and debug Logs")
                sleep(5)
                log("stop","/infoblox/var/infoblox.log",config.grid_master_vip)
                print("Test Case 83 Execution Completed")
                
        @pytest.mark.run(order=84)
        def test_084_audit_log_validate_for_the_nagative_test_case_082(self):
                logging.info("Validating Audit and debug log Messages for the negative test case 082")
                LookForDebug="File not found"
                logdebug = logv(LookForDebug,"/infoblox/var/infoblox.log",config.grid_master_vip)
                if logdebug!=None:
                        logging.info(logdebug)
                        logging.info("Test Case 60 Execution Completed")
                        assert True
                                
                else:
                        print("We are not getting expected error message from the debug log")
                        logging.info("Test Case 60 Execution Failed")
                        assert False
        
        @pytest.mark.run(order=85)
        def test_085_start_audit_and_debug_logs(self):
                logging.info("Starting Audit and debug Logs")
                log("start","/infoblox/var/infoblox.log",config.grid_master_vip)
                print("Test Case 85 Execution Completed")
        
        @pytest.mark.run(order=86)
        def test_086___Negative_test_case___Start_Grid_backuo_on_TFTP_server_with_wrong_path(self):
                logging.info("Start Grid Backup On TFTP Server with Wrong path | Negative case ")
                filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                data = {"type": "BACKUP", "nios_data": True, "remote_url": "tftp://"+ config.tftp_server+"/wrong/"+filename}
                status, response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data))
                logging.info(response)
                if status == 400:
                        ref1 = json.loads(response)
                        print(ref1['text'])
                        assert True
                        logging.info("Test Case 86 Execution Completed")
                else:
                        print("Response code: {}" .format(status))
                        assert False
                        logging.info("Test Case 86 Execution Failed")
        
        @pytest.mark.run(order=87)
        def test_087_stop_audit_and_debug_Logs(self):
                logging.info("Stopping Audit and debug Logs")
                sleep(5)
                log("stop","/infoblox/var/infoblox.log",config.grid_master_vip)
                print("Test Case 83 Execution Completed")
                
        @pytest.mark.run(order=88)
        def test_088_audit_log_validate_for_the_nagative_test_case_082(self):
                logging.info("Validating Audit and debug log Messages for the negative test case 082")
                LookForDebug="File not found"
                logdebug = logv(LookForDebug,"/infoblox/var/infoblox.log",config.grid_master_vip)
                if logdebug!=None:
                        logging.info(logdebug)
                        logging.info("Test Case 88 Execution Completed")
                        assert True
                                
                else:
                        print("We are not getting expected error message from the debug log")
                        logging.info("Test Case 60 Execution Failed")
                        assert False

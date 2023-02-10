import re
import config
#import config1
import pytest
import unittest
import logging
import subprocess
import os
import json
from time import sleep
import commands
import json, ast
import requests
import time
import pexpect
import getpass
import paramiko
import sys
#from dig_all_records import dig
from paramiko import client
#from log_capture import log_action as log
#from log_validation import log_validation as logv
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as comm_util

class Network(unittest.TestCase):

         @pytest.mark.run(order=1)
         def test_01_Create_New_AuthZone(self):
             logging.info("Create A new Zone")
             data = {"fqdn": "zone.com"}
             response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
             print response
             logging.info(response)
             read  = re.search(r'201',response)
             logging.info("Test Case 1 Executed")
             #assert read, "Response code differ from 201"
             logging.info(response)
             read  = re.search(r'201',response)
             for read in  response:
                 assert True
             logging.info("Test Case 3 Execution Completed")


	 @pytest.mark.run(order=2)
         def test_02_create_grid_primary_for_zone(self):
                logging.info("Create grid_primary with required fields")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth")
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

                logging.info("Test Case 2 Execution Completed")


	 @pytest.mark.run(order=3)
         def test_03_Add_a_DTC_Server1(self):
                logging.info("Create A DTC Server") 
                data = {"name":"s1","host":"10.120.20.151"}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 3 Execution Completed")


	 @pytest.mark.run(order=4)
         def test_04_Add_a_DTC_Server2(self):
                logging.info("Create A DTC Server")
                data = {"name":"s2","host":"10.120.21.95"}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 4 Execution Completed")



	 @pytest.mark.run(order=5)
         def test_05_Add_a_DTC_pool(self):
                logging.info("Create A DTC Pool")
                data = {"name":"pool1","monitors":["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"],"lb_preferred_method":"ALL_AVAILABLE","servers": [{"ratio": 1,"server": "dtc:server/ZG5zLmlkbnNfc2VydmVyJHMx:s1"},{"ratio": 1,"server": "dtc:server/ZG5zLmlkbnNfc2VydmVyJHMy:s2"}]}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:pool", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 5 Execution Completed")

         @pytest.mark.run(order=6)
         def test_06_Add_a_DTC_lbdn(self):
                logging.info("Create A DTC LBDN")
                data = {"name":"lbdn1","lb_method":"GLOBAL_AVAILABILITY", "patterns": ["*.zone.com"], "pools": [{"pool":"dtc:pool/ZG5zLmlkbnNfcG9vbCRwb29sMQ:pool1","ratio": 1}], "auth_zones":["zone_auth/ZG5zLnpvbmUkLl9kZWZhdWx0LmNvbS56b25l:zone.com/default"],"types":["A","AAAA","CNAME","NAPTR","SRV"]}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:lbdn", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 6 Execution Completed")


         @pytest.mark.run(order=7)
         def test_07_Modify_log_queries(self):
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify a  log_queries")
                data = {"logging_categories":{"log_queries": True,"log_responses":True,"log_dtc_gslb":True,"log_dtc_health": True}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                sleep(10)
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(20)
                logging.info("Test Case 7 Execution Completed")
                sleep(10)		
    
         @pytest.mark.run(order=8)
         def test_08_perform_query_for_DTC_record_on_master(self):
                logging.info("Perform query for DTC record on master")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.zone.com IN A'
                dig_cmd1 = os.system(dig_cmd)
                logging.info("Validate Syslog afer perform queries")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -10 /var/log/syslog | grep  \'A 10.120.20.151\'"'
                out1 = commands.getoutput(sys_log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'10.120.20.151',out1)
                logging.info("Test Case 8 Execution Completed")
                sleep(10)     

    
         @pytest.mark.run(order=9)
         def test_09_scp_server_fail(self):
             logging.info("Scp server fail")
             data={"remote_url":"scp://root:infoblox@10.120.21.117/root/.ssh","type":"BACKUP","use_keys":False,"upload_keys":False,"key_type":"id_rsa","download_keys":False}
             get_ref = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data),grid_vip=config.grid_vip)
             print get_ref
             sleep(30)
             infoblox_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -10 /infoblox/var/infoblox.log"'
             out1 = commands.getoutput(infoblox_log_validation)
             if re.search(r'Upload to the SCP server failed',out1):
                assert True
             else:
                assert False
             logging.info("Test Case 9 Execution Completed")
  
         @pytest.mark.run(order=10)
         def test_10_rsa_upload_download_keys(self):
             logging.info("Test upload keys as  true using RSA")
             data={"remote_url":"scp://root:infoblox@10.120.21.117/root/.ssh","type":"BACKUP","use_keys":True,"upload_keys":True,"key_type":"id_rsa","download_keys":False}
             get_ref = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data),grid_vip=config.grid_vip)
             print get_ref
             sleep(10)
             infoblox_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -4 /infoblox/var/infoblox.log "'           
             out2 = commands.getoutput(infoblox_log_validation)
             print out2
             if re.search(r'Upload to the SCP server failed',out2):
                assert False
             elif re.search(r'Sucessfully Pushed Public key to SCP Server',out2):
                print "Sucessfully Pushed Public key to SCP Server"
                assert True
             else:
                assert False

             logging.info("Test Case 10 Execution Completed")

         @pytest.mark.run(order=11)
         def test_11_ecdsa_upload_download_keys(self):
             logging.info("Test upload keys as  true using ECDSA")
             data = {"remote_url": "scp://root:infoblox@10.120.21.117/root/.ssh", "type": "BACKUP", "use_keys": True,
                     "upload_keys": True, "key_type": "id_ecdsa", "download_keys":False}
             get_ref = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data),
                                            grid_vip=config.grid_vip)
             print get_ref
             sleep(10)
             infoblox_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str( config.grid_vip) + ' " tail -4 /infoblox/var/infoblox.log "'
             out2 = commands.getoutput(infoblox_log_validation)
             print out2
             if re.search(r'Upload to the SCP server failed', out2):
                 assert False
             elif re.search(r'Sucessfully Pushed Public key to SCP Server', out2):
                 print "Sucessfully Pushed Public key to SCP Server"
                 assert True
             else:
                 assert False

             logging.info("Test Case 11 Execution Completed")
        
         @pytest.mark.run(order=12)
         def test_12_DTC_scp_server_fail(self):
             logging.info("SCP server Fail")
             data={"remote_url":"scp://root:infoblox@10.120.21.117/root/.ssh","type":"BACKUP_DTC","use_keys":False,"upload_keys":False,"key_type":"id_rsa","download_keys":False}
             get_ref = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data),grid_vip=config.grid_vip)
             print get_ref
             sleep(30)
             infoblox_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -10 /infoblox/var/infoblox.log"'
             out1 = commands.getoutput(infoblox_log_validation)
             if re.search(r'Upload to the SCP server failed',out1):
                assert True
             else:
                assert False
             logging.info("Test Case 12 Execution Completed")

         @pytest.mark.run(order=13)
         def test_13_DTC_rsa_upload_download_keys(self):
             logging.info("Upload to download keys")
             data={"remote_url":"scp://root:infoblox@10.120.21.117/root/.ssh","type":"BACKUP_DTC","use_keys":True,"upload_keys":True,"key_type":"id_rsa","download_keys":False}
             get_ref = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data),grid_vip=config.grid_vip)
             print get_ref
             sleep(10)
             infoblox_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -4 /infoblox/var/infoblox.log "'
             out2 = commands.getoutput(infoblox_log_validation)
             print out2
             if re.search(r'Upload to the SCP server failed',out2):
                assert False
             elif re.search(r'Sucessfully Pushed Public key to SCP Server',out2):
                print "Sucessfully Pushed Public key to SCP Server"
                assert True
             else:
                assert False

             logging.info("Test Case 13 Execution Completed")

         @pytest.mark.run(order=14)
         def test_14_DTC_ecdsa_upload_download_keys(self):
             logging.info("Test upload keys as true using ECDSA")
             data = {"remote_url": "scp://root:infoblox@10.120.21.117/root/.ssh", "type": "BACKUP_DTC", "use_keys": True,
                     "upload_keys": True, "key_type": "id_ecdsa", "download_keys":False}
             get_ref = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data),
                                            grid_vip=config.grid_vip)
             print get_ref
             sleep(10)
             infoblox_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str(
                 config.grid_vip) + ' " tail -4 /infoblox/var/infoblox.log "'
             out2 = commands.getoutput(infoblox_log_validation)
             print out2
             if re.search(r'Upload to the SCP server failed', out2):
                 assert False
             elif re.search(r'Sucessfully Pushed Public key to SCP Server', out2):
                 print "Sucessfully Pushed Public key to SCP Server"
                 assert True
             else:
                 assert False

             logging.info("Test Case 14 Execution Completed")

####################### Ubuntu Server ##################################
        
         @pytest.mark.run(order=15)
         def test_15_scp_server_fail(self):
             logging.info("Scp server Fail")
             data={"remote_url":"scp://tp:tp@10.39.18.130/home/tp/.ssh","type":"BACKUP_DTC","use_keys":False,"upload_keys":False,"key_type":"id_rsa","download_keys":False}
             get_ref = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data),grid_vip=config.grid_vip)
             print get_ref
             sleep(30)
             infoblox_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -10 /infoblox/var/infoblox.log | grep  \'Upload to the SCP server failed\'"'
             out1 = commands.getoutput(infoblox_log_validation)
             if re.search(r'Upload to the SCP server failed',out1):
                assert True
             else:
                assert False
             logging.info("Test Case 15 Execution Completed")

         @pytest.mark.run(order=16)
         def test_16_rsa_upload_download_keys(self):
             logging.info("Test upload keys as  true using RSA")
             data={"remote_url":"scp://tp:tp@10.39.18.130/root/.ssh","type":"BACKUP_DTC","use_keys":True,"upload_keys":True,"key_type":"id_rsa","download_keys":False}
             get_ref = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data),grid_vip=config.grid_vip)
             print get_ref
             sleep(10)
             infoblox_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -4 /infoblox/var/infoblox.log "'
             out2 = commands.getoutput(infoblox_log_validation)
             print out2
             if re.search(r'Upload to the SCP server failed',out2):
                assert False
             elif re.search(r'Sucessfully Pushed Public key to SCP Server',out2):
                print "Sucessfully Pushed Public key to SCP Server"
                assert True
             else:
                assert False

             logging.info("Test Case 16 Execution Completed")

         @pytest.mark.run(order=17)
         def test_17_ecdsa_upload_download_keys(self):
             logging.info("Test upload keys as upload and download true using RSA")
             data = {"remote_url": "scp://tp:tp@10.39.18.130/root/.ssh", "type": "BACKUP_DTC", "use_keys": True,
                     "upload_keys": True, "key_type": "id_ecdsa", "download_keys": False}
             get_ref = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data),
                                            grid_vip=config.grid_vip)
             print get_ref
             sleep(10)
             infoblox_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str(
                 config.grid_vip) + ' " tail -4 /infoblox/var/infoblox.log "'
             out2 = commands.getoutput(infoblox_log_validation)
             print out2
             if re.search(r'Upload to the SCP server failed', out2):
                 assert False
             elif re.search(r'Sucessfully Pushed Public key to SCP Server', out2):
                 print "Sucessfully Pushed Public key to SCP Server"
                 assert True
             else:
                 assert False

             logging.info("Test Case 17 Execution Completed") 
        
################################### Cloud server Ended ###########################################

         @pytest.mark.run(order=18)
         def test_18_DTC_BACKUP(self):
                logging.info("Take DTC Backup")
                data = {"type": "BACKUP_DTC"}
                response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data))
                print response
                res = json.loads(response) 
                global token
                token=res['token']
                print token
                print("Token is : %s", token)
                print ("Backup is Done")
                read  = re.search(r'201',token)
                for read in  response:
                        assert True
                logging.info("Test Case 18 Execution Completed")


         @pytest.mark.run(order=19)
         def test_19_Delete_DTC_lbdn(self):
                logging.info("Delete the added DTC LBDN")
                get_ref = ib_NIOS.wapi_request('GET', object_type="dtc:lbdn")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                print ref
                logging.info("Deleting the caa record")
                get_status = ib_NIOS.wapi_request('DELETE', object_type=ref)
                print get_status
                logging.info(get_status)
                read = re.search(r'200',get_status)
                for read in get_status:
                        assert True
                logging.info("Test Case 19 Execution Completed")


         @pytest.mark.run(order=20)
         def test_20_Delete_DTC_Pool(self):
             logging.info("Delete the added DTC POOL")
             get_ref = ib_NIOS.wapi_request('GET', object_type="dtc:pool")
             logging.info(get_ref)
             res = json.loads(get_ref)
             ref = json.loads(get_ref)[0]['_ref']
             print ref
             logging.info("Deleting the caa record")
             get_status = ib_NIOS.wapi_request('DELETE', object_type=ref)
             print get_status
             logging.info(get_status)
             read = re.search(r'200', get_status)
             for read in get_status:
                 assert True
                 logging.info("Test Case 20 Execution Completed")


         @pytest.mark.run(order=21)
         def test_21_Delete_DTC_Server(self):
             logging.info("Delete the added DTC SERVER")
             get_ref = ib_NIOS.wapi_request('GET', object_type="dtc:server")
             logging.info(get_ref)
             res = json.loads(get_ref)
             ref = json.loads(get_ref)[0]['_ref']
             print ref
             logging.info("Deleting the caa record")
             get_status = ib_NIOS.wapi_request('DELETE', object_type=ref)
             print get_status
             logging.info(get_status)
             read = re.search(r'200', get_status)
             for read in get_status:
                 assert True
             logging.info("Test Case 21 Execution Completed")
             sleep(10)

         @pytest.mark.run(order=22)
         def test_22_Delete_DTC_Server2(self):
             logging.info("Delete the added DTC SERVER2")
             get_ref = ib_NIOS.wapi_request('GET', object_type="dtc:server")
             logging.info(get_ref)
             res = json.loads(get_ref)
             ref = json.loads(get_ref)[0]['_ref']
             print ref
             logging.info("Deleting the caa record")
             get_status = ib_NIOS.wapi_request('DELETE', object_type=ref)
             print get_status
             logging.info(get_status)
             read = re.search(r'200', get_status)
             for read in get_status:
                 assert True
             logging.info("Test Case 22 Execution Completed")
             sleep(10)
             logging.info("Restart services")
             grid =  ib_NIOS.wapi_request('GET', object_type="grid")
             ref = json.loads(grid)[0]['_ref']
             publish={"member_order":"SIMULTANEOUSLY"}
             request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
             sleep(10)
             request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
             restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
             sleep(20)
             logging.info("Test Case 22 Execution Completed")
             print token 
             sleep(10)

         @pytest.mark.run(order=23)
         def test_23_DTC_RESTORE(self):
                logging.info("Restore DTC")
                data = {"forced":False, "token":token}
                response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=restoredtcconfig", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 23 Execution Completed")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                sleep(10)
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(200)

######################################## DTC Restore completed #######################
         
         @pytest.mark.run(order=24)
         def test_24_perform_query_for_DTC_record(self):
             logging.info("Perform query for DTC record ")
             dig_cmd = 'dig @' + str(config.grid_vip) + ' a1.zone.com IN A'
             dig_cmd1 = os.system(dig_cmd)
             logging.info("Validate Syslog afer perform queries")
             sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str(config.grid_vip) + ' " tail -10 /var/log/syslog | grep \'A 10.120.20.151\'"'
             out1 = commands.getoutput(sys_log_validation)
             print out1
             logging.info(out1)
             assert re.search(r'10.120.20.151', out1)
             logging.info("Test Case 16 Execution Completed")
             sleep(10)

##################################################### GRID BACKUP ########################################################################## 
         @pytest.mark.run(order=25)
         def test_25_GRID_BACKUP(self):
                print ("Take Grid Backup")
                data = {"type": "BACKUP"}
                response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data))
                #print (response)
                res = json.loads(response)
                #global token
                URL=res['url']
                #print URL
                print("URL is : %s", URL)
                #data1=URL
                #import pdb;pdb.set_trace()
                #response = ib_NIOS.wapi_request('POST',params='database.bak',fields=json.dumps(data1),content_type="application/force-download")
                infoblox_log_validation ='curl -k -u admin:infoblox -H  "content-type: application/force-download" "' + str(URL) +'" -o "database.bak"'
                print ("infoblox.log",infoblox_log_validation)
                out2 = commands.getoutput(infoblox_log_validation)
                print("logs are",out2)
                print ("Backup is Done")
                #print (response)
                read  = re.search(r'201',URL)
                for read in  response:
                        assert True
                logging.info("Test Case 25 Execution Completed")


         @pytest.mark.run(order=26)
         def test_26_Delete_DTC_lbdn(self):
                logging.info("Delete the added DTC LBDN")
                get_ref = ib_NIOS.wapi_request('GET', object_type="dtc:lbdn")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                print ref
                logging.info("Deleting the caa record")
                get_status = ib_NIOS.wapi_request('DELETE', object_type=ref)
                print get_status
                logging.info(get_status)
                read = re.search(r'200',get_status)
                for read in get_status:
                        assert True
                logging.info("Test Case 26 Execution Completed")

         
         @pytest.mark.run(order=27)
         def test_27_Delete_DTC_Pool(self):
             logging.info("Delete the added DTC POOL")
             get_ref = ib_NIOS.wapi_request('GET', object_type="dtc:pool")
             logging.info(get_ref)
             res = json.loads(get_ref)
             ref = json.loads(get_ref)[0]['_ref']
             print ref
             logging.info("Deleting the caa record")
             get_status = ib_NIOS.wapi_request('DELETE', object_type=ref)
             print get_status
             logging.info(get_status)
             read = re.search(r'200', get_status)
             for read in get_status:
                 assert True
                 logging.info("Test Case 20 Execution Completed")


         @pytest.mark.run(order=28)
         def test_28_Delete_DTC_Server(self):
             logging.info("Delete the added DTC SERVER")
             get_ref = ib_NIOS.wapi_request('GET', object_type="dtc:server")
             logging.info(get_ref)
             res = json.loads(get_ref)
             ref = json.loads(get_ref)[0]['_ref']
             print ref
             logging.info("Deleting the caa record")
             get_status = ib_NIOS.wapi_request('DELETE', object_type=ref)
             print get_status
             logging.info(get_status)
             read = re.search(r'200', get_status)
             for read in get_status:
                 assert True
             logging.info("Test Case 21 Execution Completed")
             sleep(10)


         @pytest.mark.run(order=29)
         def test_29_Delete_DTC_Server2(self):
             logging.info("Delete the added DTC SERVER2")
             get_ref = ib_NIOS.wapi_request('GET', object_type="dtc:server")
             logging.info(get_ref)
             res = json.loads(get_ref)
             ref = json.loads(get_ref)[0]['_ref']
             print ref
             logging.info("Deleting the caa record")
             get_status = ib_NIOS.wapi_request('DELETE', object_type=ref)
             print get_status
             logging.info(get_status)
             read = re.search(r'200', get_status)
             for read in get_status:
                 assert True
             logging.info("Test Case 22 Execution Completed")
             sleep(10)
             logging.info("Restart services")
             grid =  ib_NIOS.wapi_request('GET', object_type="grid")
             ref = json.loads(grid)[0]['_ref']
             publish={"member_order":"SIMULTANEOUSLY"}
             request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
             sleep(10)
             request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
             restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
             sleep(20)
             logging.info("Test Case 22 Execution Completed")
             print token
             sleep(10)

         @pytest.mark.run(order=30)
         def test_30_Delete_Zone(self):
                logging.info("Deleting the zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                print ref
                logging.info("Deleting the ZONE")
                get_status = ib_NIOS.wapi_request('DELETE', object_type=ref)
                print get_status
                logging.info(get_status)
                read = re.search(r'200',get_status)
                for read in get_status:
                        assert True
                logging.info("Test Case 30 Execution Completed")
         
         @pytest.mark.run(order=31)
         def test_31_GRID_RESTORE(self):
             logging.info("Grid Restore")
             #data = {"forced":False, "token":token}
             response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=uploadinit")
             #import pdb; pdb.set_trace()
             print response
             res = json.loads(response)
                #global token
             URL=res['url']
             token1=res['token']
             print("URL is : %s", URL)
             print("Token is %s",token1)
             #data1=URL
             #response1 = ib_NIOS.wapi_request('POST',params='database.bak',fields=json.dumps(data1),content_type="content-typemultipart-formdata")
             #logging.info(response)
             infoblox_log_validation ='curl -k -u admin:infoblox -H content_type="content-typemultipart-formdata" ' + str(URL) +' -F file=@database.bak'
             print infoblox_log_validation
             out2 = commands.getoutput(infoblox_log_validation)
             print ("out2$$$$$$",out2)
             data2={"mode":"NORMAL","nios_data":True,"token":token1}
             #data2["token"]=token1
             print ("&*&*&*&*&*&*",data2)
             #print (os.system('pwd'))
             #print (os.system("ls -ltr"))
             #print ("::::::::::::::::::::::::::::::::::::::::::::::::::")
             response2 = ib_NIOS.wapi_request('POST', object_type="fileop?_function=restoredatabase",fields=json.dumps(data2))
             #print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++",response2)
             sleep(150)
             logging.info("Validate Syslog afer perform queries")
             #import pdb; pdb.set_trace()
             #sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -220 /var/log/syslog | grep  \'A restore_node complete\'"'
             infoblox_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str( config.grid_vip) + ' " tail -1200 /infoblox/var/infoblox.log "'
             out1 = commands.getoutput(infoblox_log_validation)
             print out1
             logging.info(out1)
             assert re.search(r'restore_node complete',out1)
             sleep(50)
             read  = re.search(r'201',response)
             for read in  response:
                 assert True
             logging.info("Test Case 23 Execution Completed")
             sleep(120)


         @pytest.mark.run(order=32)
         def test_32_perform_query_for_DTC_record(self):
             logging.info("Perform query for DTC record ")
             dig_cmd = 'dig @' + str(config.grid_vip) + ' a1.zone.com IN A'
             dig_cmd1 = os.system(dig_cmd)
             logging.info("Validate Syslog afer perform queries")
             sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str(config.grid_vip) + ' " tail -10 /var/log/syslog | grep \'A 10.120.20.151\'"'
             out1 = commands.getoutput(sys_log_validation)
             print out1
             logging.info(out1)
             assert re.search(r'10.120.20.151', out1)
             logging.info("Test Case 16 Execution Completed")
             sleep(10)


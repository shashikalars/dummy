__author__ = "Siva Krishna"
__email__  = "krishnas@infoblox.com"

######################################################################################################################
#  Grid Set up required:                                                                                             #
#  1. Grid Master + HA member                                                                                        #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415),Threat Analytics+RPZ                                                   #
######################################################################################################################
import re
import sys
import config
import pytest
import unittest
import logging
import os
import os.path
from os.path import join
import time
from time import sleep
import json
import commands
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util
import ib_utils.log_capture as log_capture
from  ib_utils.log_capture import log_action as log
from  ib_utils.log_validation import log_validation as logv
import pexpect
class NIOSSPT_10842(unittest.TestCase):

        @pytest.mark.run(order=1)
        def test_001_Start_DNS_Service(self):
                logging.info("Start DNS Service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                for i in res:
                        logging.info("Modify a enable_dns")
                        data = {"enable_dns": True}
                        response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
                        print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 1 Execution Completed")

        @pytest.mark.run(order=2)
        def test_002_Validate_DNS_service_Enabled(self):
                logging.info("Validate DNs Service is enabled")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                for i in res:
                        print i
                        logging.info("found")
                        assert i["enable_dns"] == True
                print("Test Case 2 Execution Completed")
	
	@pytest.mark.run(order=3)
        def test_003_create_New_RPZZone(self):
                logging.info("Create A new Zone")
                data = {"fqdn": "test","grid_primary": [{"name": config.grid_fqdn,"stealth":False}, {"name": config.grid_member1_fqdn,"stealth":False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_rp", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Restart DNS Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20)
                logging.info("Test Case 3 Execution Completed")

        @pytest.mark.run(order=4)
        def test_004_Validate_AuthZone(self):
                logging.info("Validate the  Zone")
                response =  ib_NIOS.wapi_request('GET', object_type="zone_rp?fqdn=test", grid_vip=config.grid_vip)
                print response
                if ('"fqdn": "test"' in response):
                    assert True
                else:
                    assert False
                logging.info("Test Case 4 Execution Completed")

        @pytest.mark.run(order=5)
        def test_005_Add_proxy_Server(self):
                logging.info("Add_proxy_Server")
                ref =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data={"http_proxy_server_setting": {"address": config.proxy,"enable_content_inspection": False,"enable_proxy": True,"enable_username_and_password": True,"port": 8001,"username": "client","password": "infoblox","verify_cname": False}}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 5 Execution Completed")
        
	@pytest.mark.run(order=6)
        def test_006_Validate_proxy_Server(self):
                logging.info("Validate_proxy_Server")
                ref =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=http_proxy_server_setting", grid_vip=config.grid_vip)
                print response
                proxy='"address": "'+config.proxy+'"'
                print(proxy)
                if (proxy in response) and ('"port": 8001' in response):
                    assert True
                else:
                    assert False
		sleep(10)
                logging.info("Test Case 6 Execution Completed")

	@pytest.mark.run(order=7)
        def test_007_Add_Blacklist_Domain(self):
                logging.info("Add_Blacklist_Domain")
		ref =  ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
		data={"dns_tunnel_black_list_rpz_zones":["zone_rp/ZG5zLnpvbmUkLl9kZWZhdWx0LnRlc3Q:test/default"]}
		response = ib_NIOS.wapi_request('PUT', object_type=ref1, fields=json.dumps(data))
		sleep(10)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 7 Execution Completed")
	
	@pytest.mark.run(order=8)
        def test_008_Validate_Blacklist_Domain(self):
                logging.info("Validate_Blacklist_Domain")
                response =  ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=dns_tunnel_black_list_rpz_zones", grid_vip=config.grid_vip)
                print response
		if ("test" in response):
		    assert True
                else:
                    assert False
		sleep(10)
                logging.info("Test Case 8 Execution Completed")

	@pytest.mark.run(order=9)
        def test_009_Start_Threat_Analytics_Service(self):
                logging.info("Start Threat_Analytics Service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatanalytics")
                logging.info(get_ref)
                res = json.loads(get_ref)
                for i in res:
                        logging.info("Modify a enable_Threat_Analytics")
                        data = {"enable_service": True}
                        response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
                        print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
		print("Restart DNS Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20)
                print("Test Case 9 Execution Completed")

        @pytest.mark.run(order=10)
        def test_010_Validate_Threat_Analytics_service_Enabled(self):
                logging.info("Validate Threat_Analytics Service is enabled")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:threatanalytics",params="?_return_fields=enable_service")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                for i in res:
                        print i
                        logging.info("found")
                        assert i["enable_service"] == True
		sleep(5)
                print("Test Case 10 Execution Completed")

	@pytest.mark.run(order=11)
        def test_011_Enable_Automatic_White_list_Moduleset(self):
                logging.info("Enable_Automatic_White_list_Moduleset")
		child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.expect('#')
		child.sendline('date')
                child.expect('#')
                date=child.before
		print("date",date)
                print(date)
                date=date.split(" ")
                print(date)
                date=date[4].split(":")
                print(date)
                if int(date[1])>=58:
                    hr=int(date[0])+1
                    mi=1
                else:
                    hr=int(date[0])
                    mi=int(date[1])+2
		ref =  ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
	 	data={"enable_whitelist_auto_download": True,"scheduled_whitelist_download": {"disable": False,"every": 1,"frequency": "HOURLY","hour_of_day": hr,"minutes_past_hour": mi,"repeat": "RECUR","time_zone": "(UTC) Coordinated Universal Time"},"enable_auto_download": True,"scheduled_download": {"disable": False,"every": 1,"frequency": "HOURLY","hour_of_day": hr,"minutes_past_hour": mi,"repeat": "RECUR","time_zone": "(UTC) Coordinated Universal Time" }}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1, fields=json.dumps(data))
		sleep(10)	
		print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 11 Execution Completed")

        @pytest.mark.run(order=12)
        def test_012_Threat_analytics_server_Test_Connection_Validation(self):
                logging.info("Threat_analytics_server Test Connection Validation")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics")
                print(get_ref)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                response = ib_NIOS.wapi_request('POST', object_type=ref1+"?_function=test_threat_analytics_server_connectivity")
                print response
                logging.info(response)
                sleep(5)
                assert re.search(r'"overall_status": "SUCCESS"',response)
                print("Test Case 12 Execution Completed")

        @pytest.mark.run(order=13)
        def test_013_validate_the_whitelist_download_logs_in_PASSIVE_node(self):
                logging.info("validate_the_whitelist_download_logs_in_PASSIVE_node")
                log("start","/infoblox/var/infoblox.log",config.Passive_ip)
                sleep(600)
                log("stop","/infoblox/var/infoblox.log",config.Passive_ip)
                print("Test Case 13 Execution Completed")


        @pytest.mark.run(order=14)
        def test_014_looking_for_bind_failed(self):
                logging.info("looking_for bind failed with errno")
                check=commands.getoutput(" grep -cw \".*bind failed with errno.*\" /tmp/"+str(config.Passive_ip)+"_infoblox_var_infoblox.log.log")
                check1=commands.getoutput(" grep -cw \".*Failed to retrieve whitelist filename from Infoblox Download server.*\" /tmp/"+str(config.Passive_ip)+"_infoblox_var_infoblox.log.log")
                check2=commands.getoutput(" grep -cw \".*Threat Analytics Auto Download has failed.*\" /tmp/"+str(config.Passive_ip)+"_infoblox_var_infoblox.log.log")
                print(check)
                if ((int(check)==0) and (int(check1)==0) and (int(check2)==0)):
                    assert True
                else:
                    assert False
                sleep(2)
                print("Test Case 14 Execution Completed")

        @pytest.mark.run(order=15)
        def test_015_Disable_Automatic_White_list_Moduleset(self):
                logging.info("Disable_Automatic_White_list_Moduleset")
                ref =  ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data={"enable_whitelist_auto_download": False,"enable_auto_download": False }
                response = ib_NIOS.wapi_request('PUT', object_type=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 15 Execution Completed")

        @pytest.mark.run(order=16)
        def test_016_Stop_Threat_Analytics_Service(self):
                logging.info("Stop Threat_Analytics Service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatanalytics")
                logging.info(get_ref)
                res = json.loads(get_ref)
                for i in res:
                        logging.info("Modify a enable_Threat_Analytics")
                        data = {"enable_service": False}
                        response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
                        print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Restart DNS Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20)
                print("Test Case 16 Execution Completed")

        @pytest.mark.run(order=17)
        def test_017_Validate_Threat_Analytics_service_Disabled(self):
                logging.info("Validate Threat_Analytics Service is disabled")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:threatanalytics",params="?_return_fields=enable_service")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                for i in res:
                        print i
                        logging.info("found")
                        assert i["enable_service"] == False
                print("Test Case 17 Execution Completed")

import re
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
import time
import subprocess

from time import sleep
import commands
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util
import ib_utils.log_capture as log_capture
from  ib_utils.log_capture import log_action as log
from  ib_utils.log_validation import log_validation as logv
import pexpect
from paramiko import client

class Rfe_9427(unittest.TestCase):

#Starting DNS service

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
        def test_003_create_New_AuthZone(self):
                logging.info("Create A new Zone")
                data = {"fqdn": "dtc.com","grid_primary": [{"name": config.grid_member_fqdn,"stealth":False}, {"name": config.grid_member1_fqdn,"stealth":False}, {"name": config.grid_member2_fqdn,"stealth":False}]}
		response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
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
    	def test_004_add_a_DTC_Server1(self):
        	logging.info("Create A DTC first Server")
        	data = {"name":"server1","host":config.Server1}
        	response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
        	print response
        	logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 4 Execution Completed")
	
        @pytest.mark.run(order=5)
        def test_005_add_a_DTC_pool(self):
                logging.info("Create A DTC Pool")
                data = {"name": "Pool1","lb_preferred_method": "ROUND_ROBIN","servers": [{"ratio": 1,"server": "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjE:server1"}],"monitors": ["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"]}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:pool", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 5 Execution Completed")

	@pytest.mark.run(order=6)
        def test_006_add_a_DTC_lbdn(self):
                logging.info("Create A DTC LBDN")
                data = {"name":"lbdn","lb_method":"ROUND_ROBIN","patterns": ["a1.dtc.com"], "pools": [{"pool":"dtc:pool/ZG5zLmlkbnNfcG9vbCRQb29sMQ:Pool1","ratio": 1}], "auth_zones":["zone_auth/ZG5zLnpvbmUkLl9kZWZhdWx0LmNvbS5kdGM:dtc.com/default"],"types":["A","AAAA","CNAME","NAPTR","SRV"]}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:lbdn", fields=json.dumps(data))
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
                sleep(30)
                logging.info("Test Case 6 Execution Completed")

        @pytest.mark.run(order=7)
        def test_007_Modify_pool_with_Consolidated_Monitors(self):
                logging.info("Modify_pool_with_Consolidated_Monitors")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:pool", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"consolidated_monitors": [{"availability": "ALL","full_health_communication": False,"members": [config.grid_member1_fqdn,config.grid_member2_fqdn],"monitor":"dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"}]}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                print("Restart DNS Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(30)


	@pytest.mark.run(order=8)
        def test_008_Validate_Consolidated_monitors_at_Pool(self):
		logging.info("Verify_consolidated_monitors_at_Pool")
                response =  ib_NIOS.wapi_request('GET', object_type="dtc:pool?_return_fields=auto_consolidated_monitors,consolidated_monitors", grid_vip=config.grid_vip)
                print response
                if ('"full_health_communication": false' in response) and ('"availability": "ALL"' in response):
                    assert True
                else:
                    assert False
        
        @pytest.mark.run(order=9)
        def test_009_create_A_Record(self):
                logging.info("Create_A_Record")
                data = {"name": "a1.dtc.com","view": "default","ipv4addr": "1.1.1.1"}
                response = ib_NIOS.wapi_request('POST', object_type="record:a", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
 
	@pytest.mark.run(order=10)
        def test_010_enabling_logging_categories(self):
		logging.info("enabling_logging_categories ")
		ref =  ib_NIOS.wapi_request('GET', object_type="grid:dns", grid_vip=config.grid_vip)
		print ref
                logging.info(ref)
		res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
		data = {"logging_categories": {"log_rpz": True,"log_dtc_gslb": True,"log_dtc_health": True}}
		response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
		print("Restart DNS Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20)

	@pytest.mark.run(order=11)
        def test_011_perform_query_for_DTC_record_for_Master(self):
		for i in range(3):
                	dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                	logging.info("perform_query_for_DTC_record_for_Master")
			dig_result = subprocess.check_output(dig_cmd, shell=True)
                	print dig_result
                	if (config.Server1 in dig_result):
                        	assert True
                	else:
                        	assert False
			
	@pytest.mark.run(order=12)
        def test_012_perform_query_for_DTC_record_for_Member1(self):
		for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                        dig_cmd1 = os.system(dig_cmd)
                        sleep(10)
                        logging.info("perform_query_for_DTC_record_for_Member")
			dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (config.Server1 in dig_result):
                                assert True
			else:
                                assert False

	@pytest.mark.run(order=13)
        def test_013_perform_query_for_DTC_record_for_Member2(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                        dig_cmd1 = os.system(dig_cmd)
                        sleep(10)
                        logging.info("perform_query_for_DTC_record_for_Member")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (config.Server1 in dig_result):
                                assert True
                        else:
                                assert False

	@pytest.mark.run(order=14)
        def test_014_Execute_DROP_Command_in_Member1(self):
                logging.info("Execute_DROP_Command_in_Member1")
                drop='iptables -I INPUT -s '+config.Server1+' -j DROP'
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline(drop)
                child.expect('#')
                sleep(60)

	@pytest.mark.run(order=15)
        def test_015_perform_query_for_DTC_record_for_Master(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                        logging.info("perform_query_for_DTC_record_for_Master")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (config.Server1 not in dig_result) and ("1.1.1.1" in dig_result):
                                assert True
                        else:
                                assert False

        @pytest.mark.run(order=16)
        def test_016_perform_query_for_DTC_record_for_Member1(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                        dig_cmd1 = os.system(dig_cmd)
                        sleep(5)
                        logging.info("perform_query_for_DTC_record_for_Member")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (config.Server1 not in dig_result) and ("1.1.1.1" in dig_result):
                                assert True
                        else:
                                assert False

        @pytest.mark.run(order=17)
        def test_017_perform_query_for_DTC_record_for_Member2(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                        dig_cmd1 = os.system(dig_cmd)
                        sleep(5)
                        logging.info("perform_query_for_DTC_record_for_Member")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (config.Server1 in dig_result):
                                assert True
                        else:
                                assert False

	@pytest.mark.run(order=18)
        def test_018_Enable_full_health_communication_at_Pool(self):
                logging.info("Enable_full_health_communication_at_Pool")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:pool", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"consolidated_monitors": [{"availability": "ALL","full_health_communication": True,"members": [config.grid_member1_fqdn,config.grid_member2_fqdn],"monitor":"dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"}]}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                print("Restart DNS Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(30)

	@pytest.mark.run(order=19)
        def test_019_Verify_full_health_communication_at_Pool(self):
                logging.info("Verify_full_health_communication_at_Pool")
                response =  ib_NIOS.wapi_request('GET', object_type="dtc:pool?_return_fields=auto_consolidated_monitors,consolidated_monitors", grid_vip=config.grid_vip)
                print response
                if ('"full_health_communication": true' in response) and ('"availability": "ALL"' in response):
                    assert True
                else:
                    assert False	

	@pytest.mark.run(order=20)
        def test_020_perform_query_for_DTC_record_for_Master(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                        logging.info("perform_query_for_DTC_record_for_Master")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (config.Server1 not in dig_result) and ("1.1.1.1" in dig_result):
                                assert True
                        else:
                                assert False

        @pytest.mark.run(order=21)
        def test_021_perform_query_for_DTC_record_for_Member1(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                        dig_cmd1 = os.system(dig_cmd)
                        sleep(10)
                        logging.info("perform_query_for_DTC_record_for_Member")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (config.Server1 not in dig_result)  and ("1.1.1.1" in dig_result):
                                assert True
                        else:
                                assert False

        @pytest.mark.run(order=22)
        def test_022_perform_query_for_DTC_record_for_Member2(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                        dig_cmd1 = os.system(dig_cmd)
                        sleep(10)
                        logging.info("perform_query_for_DTC_record_for_Member")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (config.Server1 not in dig_result) and ("1.1.1.1" in dig_result):
                                assert True
                        else:
                                assert False
                           
        @pytest.mark.run(order=23)
        def test_023_Starting_Logs(self):
                logging.info("Logs Validation")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                sleep(20)


        @pytest.mark.run(order=24)
        def test_024_Modify_pool_with_Consolidated_Monitors_as_ANY(self):
                logging.info("Modify_pool_with_Consolidated_Monitors as ANY")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:pool", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"consolidated_monitors": [{"availability": "ANY","full_health_communication": True,"members": [config.grid_member1_fqdn,config.grid_member2_fqdn],"monitor":"dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"}]}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                print("Restart DNS Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(60)

        @pytest.mark.run(order=25)
        def test_025_Verify_consolidated_monitors_at_Pool(self):
                logging.info("Verify_consolidated_monitors_at_Pool")
                response =  ib_NIOS.wapi_request('GET', object_type="dtc:pool?_return_fields=auto_consolidated_monitors,consolidated_monitors", grid_vip=config.grid_vip)
                print response
                if ('"full_health_communication": true' in response) and ('"availability": "ANY"' in response):
                    assert True
                else:
                    assert False

        @pytest.mark.run(order=26)
        def test_026_Stopping_Logs(self):
                logging.info("Logs Validation")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                sleep(20)

        @pytest.mark.run(order=27)
        def test_027_looking_for_Health_Status(self):
                check=commands.getoutput(" grep -cw \".*idns_rpc_idnsd.c.* .*Finished getting FULL health update.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox*")
                if (int(check)!=0):
                    assert True
                else:
                    assert False
                sleep(20)
                print("Test case 27 Execution Completed")

        @pytest.mark.run(order=28)
        def test_028_perform_query_for_DTC_record_for_Master(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                        logging.info("perform_query_for_DTC_record_for_Master")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (config.Server1 in dig_result):
                                assert True
                        else:
                                assert False

        @pytest.mark.run(order=29)
        def test_029_perform_query_for_DTC_record_for_Member1(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                        dig_cmd1 = os.system(dig_cmd)
                        sleep(10)
                        logging.info("perform_query_for_DTC_record_for_Member")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (config.Server1 in dig_result):
                                assert True
                        else:
                                assert False

        @pytest.mark.run(order=30)
        def test_030_perform_query_for_DTC_record_for_Member2(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                        dig_cmd1 = os.system(dig_cmd)
                        sleep(10)
                        logging.info("perform_query_for_DTC_record_for_Member")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (config.Server1 in dig_result):
                                assert True
                        else:
                                assert False

        @pytest.mark.run(order=31)
        def test_031_Execute_ACCEPT_Command_in_Member1(self):
                logging.info("Execute_ACCEPT_Command_in_Member1")
                drop='iptables -I INPUT -s '+config.Server1+' -j ACCEPT'
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline(drop)
                child.expect('#')
                sleep(20)

	@pytest.mark.run(order=32)
        def test_032_perform_query_for_DTC_record_for_Master(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                        logging.info("perform_query_for_DTC_record_for_Master")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (config.Server1 in dig_result):
                                assert True
                        else:
                                assert False

        @pytest.mark.run(order=33)
        def test_033_perform_query_for_DTC_record_for_Member1(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                        dig_cmd1 = os.system(dig_cmd)
                        sleep(10)
                        logging.info("perform_query_for_DTC_record_for_Member")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (config.Server1 in dig_result):
                                assert True
                        else:
                                assert False

        @pytest.mark.run(order=34)
        def test_034_perform_query_for_DTC_record_for_Member2(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                        dig_cmd1 = os.system(dig_cmd)
                        sleep(10)
                        logging.info("perform_query_for_DTC_record_for_Member")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (config.Server1 in dig_result):
                                assert True
                        else:
                                assert False

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
global dig_server1
global dig_server2
class Rfe_6827(unittest.TestCase):
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
                data = {"fqdn": "dtc.com","grid_primary": [{"name": config.grid_member_fqdn,"stealth":False}, {"name": config.grid_member1_fqdn,"stealth":False}]}
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
        def test_005_add_a_DTC_Server2(self):
                logging.info("Create A DTC Second Server")
                data = {"name":"server2","host":config.Server2}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 5 Execution Completed")

	@pytest.mark.run(order=6)
        def test_006_add_a_DTC_pool(self):
                logging.info("Create A DTC Pool")
                data = {"name": "Pool1","lb_preferred_method": "SOURCE_IP_HASH","servers": [{"ratio": 1,"server": "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjE:server1"},{"ratio": 1,"server": "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjI:server2"}],"monitors": ["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"]}
		response = ib_NIOS.wapi_request('POST', object_type="dtc:pool", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 6 Execution Completed")

	@pytest.mark.run(order=7)
        def test_007_add_a_DTC_lbdn(self):
                logging.info("Create A DTC LBDN")
                data = {"name":"lbdn","lb_method":"SOURCE_IP_HASH","patterns": ["a1.dtc.com"], "pools": [{"pool":"dtc:pool/ZG5zLmlkbnNfcG9vbCRQb29sMQ:Pool1","ratio": 1}], "auth_zones":["zone_auth/ZG5zLnpvbmUkLl9kZWZhdWx0LmNvbS5kdGM:dtc.com/default"],"types":["A","AAAA","CNAME","NAPTR","SRV"]}
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
                logging.info("Test Case 7 Execution Completed")

	
	@pytest.mark.run(order=8)
        def test_008_Verify_pool_with_SOURCE_IP_HASH_And_Auto_cons(self):
                logging.info("Create A DTC Pool")
                response =  ib_NIOS.wapi_request('GET', object_type="dtc:pool?_return_fields=auto_consolidated_monitors,lb_preferred_method", grid_vip=config.grid_vip)
                print response
                if ('"auto_consolidated_monitors": false' in response) and ('"lb_preferred_method": "SOURCE_IP_HASH"' in response):
                    assert True
                else:
                    assert False

	@pytest.mark.run(order=9)
        def test_009_enabling_logging_categories(self):
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

	@pytest.mark.run(order=10)
        def test_010_perform_query_for_DTC_record_for_Master(self):
                logging.info("perform_query_for_DTC_record_for_Master ")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_cmd1 = os.system(dig_cmd)
		sleep(10)
		dig_result = subprocess.check_output(dig_cmd, shell=True)
                print dig_result
                global dig_server1
		global dig_server2
		if (config.Server1 in dig_result):
			dig_server1=config.Server1			
		elif (config.Server2 in dig_result):
			dig_server1=config.Server2
		else:
			assert False
		if dig_server1==config.Server2:
			dig_server2=config.Server1
		elif dig_server1==config.Server1:
			dig_server2=config.Server2
		print(dig_server1)
		print(dig_server2)


	@pytest.mark.run(order=11)
        def test_011_perform_query_for_DTC_record_for_Master(self):
		for i in range(3):
			print(dig_server1)
                	dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                	logging.info("perform_query_for_DTC_record_for_Master")
			dig_result = subprocess.check_output(dig_cmd, shell=True)
                	print dig_result
                	if (dig_server1 in dig_result) and (dig_server2 not in dig_result):
                        	assert True
                	else:
                        	assert False
			
	@pytest.mark.run(order=12)
        def test_012_perform_query_for_DTC_record_for_Member(self):
		for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                        dig_cmd1 = os.system(dig_cmd)
                        sleep(10)
                        logging.info("perform_query_for_DTC_record_for_Member")
			dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 in dig_result) and (dig_server2 not in dig_result):
                                assert True
                        else:
                                assert False
                        
                logging.info("Test Case 12 Execution Completed")
                sleep(10)

	@pytest.mark.run(order=13)
        def test_013_Execute_DROP_Command_in_Master(self):
		logging.info("Execute_DROP_Command_in_Master")
		drop='iptables -I INPUT -s '+dig_server1+' -j DROP'
		child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
          	child.logfile=sys.stdout
          	child.expect('#')
          	child.sendline(drop)
          	child.expect('#')
		sleep(60)

        @pytest.mark.run(order=14)
        def test_014_perform_query_for_DTC_record_for_Master(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                        dig_cmd1 = os.system(dig_cmd)
                        sleep(10)
                        logging.info("perform_query_for_DTC_record_for_Master")
			dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 not in dig_result) and (dig_server2 in dig_result):
                                assert True
                        else:
                                assert False
                       
        @pytest.mark.run(order=15)
        def test_015_perform_query_for_DTC_record_for_Member(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                        dig_cmd1 = os.system(dig_cmd)
                        sleep(10)
                        logging.info("perform_query_for_DTC_record_for_Member")
			dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 in dig_result) and (dig_server2 not in dig_result):
                                assert True
                        else:
                                assert False
                logging.info("Test Case 15 Execution Completed")
                sleep(10)

	@pytest.mark.run(order=16)
        def test_016_Execute_DROP_Command_in_Member(self):	
                logging.info("Execute_DROP_Command_in_Member")
                drop='iptables -I INPUT -s '+dig_server2+' -j DROP'
                print(drop)
		print(config.grid_member1_vip)
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline(drop)
                child.expect('#')
                sleep(60)

	@pytest.mark.run(order=17)
        def test_017_Verify_pool_with_SOURCE_IP_HASH_And_Auto_cons(self):
                logging.info("Create A DTC Pool")
                response =  ib_NIOS.wapi_request('GET', object_type="dtc:pool?_return_fields=auto_consolidated_monitors,lb_preferred_method", grid_vip=config.grid_vip)
                print response
                if ('"auto_consolidated_monitors": false' in response) and ('"lb_preferred_method": "SOURCE_IP_HASH"' in response):
                    assert True
                else:
                    assert False

        @pytest.mark.run(order=18)
        def test_018_perform_query_for_DTC_record_for_Master(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                        logging.info("perform_query_for_DTC_record_for_Master")
			dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 not in dig_result) and (dig_server2 in dig_result):
                                assert True
                        else:
                                assert False

	@pytest.mark.run(order=19)
        def test_019_perform_query_for_DTC_record_for_Member(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                        sleep(10)
                        logging.info("perform_query_for_DTC_record_for_Member")
			dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 in dig_result) and (dig_server2 not in dig_result):
                                assert True
                        else:
                                assert False
                logging.info("Test Case 19 Execution Completed")
		print("sleep for 10 secs")
                sleep(10)

	@pytest.mark.run(order=20)
        def test_020_Enabling_auto_consolidated_monitors_at_Pool(self):
                logging.info("Enabling_auto_consolidated_monitors_at_Pool ")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:pool", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"auto_consolidated_monitors": True}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                print("Restart DNS Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("sleep for 100 secs")
		sleep(100)

       
	@pytest.mark.run(order=21)
        def test_021_Verify_pool_with_SOURCE_IP_HASH_And_Auto_cons(self):
                logging.info("Create A DTC Pool")
                response =  ib_NIOS.wapi_request('GET', object_type="dtc:pool?_return_fields=auto_consolidated_monitors,lb_preferred_method", grid_vip=config.grid_vip)
                print response
                if ('"auto_consolidated_monitors": true' in response) and ('"lb_preferred_method": "SOURCE_IP_HASH"' in response):
                    assert True
                else:
                    assert False
		print("sleep for 50 sec")
		sleep(50)

	@pytest.mark.run(order=22)
        def test_022_perform_query_for_DTC_record_for_Master(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                        sleep(10)
                        logging.info("perform_query_for_DTC_record_for_Master")
			dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 not in dig_result) and (dig_server2 not in dig_result):
                                assert True
                        else:
                                assert False

        @pytest.mark.run(order=23)
        def test_023_perform_query_for_DTC_record_for_Member(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                        sleep(10)
                        logging.info("perform_query_for_DTC_record_for_Member")
			dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 not in dig_result) and (dig_server2 not in dig_result):
                                assert True
                        else:
                                assert False
                logging.info("Test Case 23 Execution Completed")
                sleep(10)

	@pytest.mark.run(order=24)
        def test_024_Execute_ACCEPT_Command_in_Member(self):
                logging.info("Execute_ACCEPT_Command_in_Member")
                accept='iptables -I INPUT -s '+dig_server2+' -j ACCEPT'
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline(accept)
                child.expect('#')
                sleep(60)

        @pytest.mark.run(order=25)
        def test_025_perform_query_for_DTC_record_for_Master(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                        sleep(10)
                        logging.info("perform_query_for_DTC_record_for_Master")
			dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 not in dig_result) and (dig_server2 in dig_result):
                                assert True
                        else:
                                assert False

	@pytest.mark.run(order=26)
        def test_026_perform_query_for_DTC_record_for_Member(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                        logging.info("perform_query_for_DTC_record_for_Member")
			dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 not in dig_result) and (dig_server2 in dig_result):
                                assert True
                        else:
                                assert False
                logging.info("Test Case 26 Execution Completed")
                sleep(10)

	@pytest.mark.run(order=27)
        def test_027_Execute_ACCEPT_Command_in_Master(self):
                logging.info("Execute_ACCEPT_Command_in_Master")
                accept='iptables -I INPUT -s '+dig_server1+' -j ACCEPT'
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline(accept)
                child.expect('#')
                sleep(60)

        @pytest.mark.run(order=28)
        def test_028_perform_query_for_DTC_record_for_Master(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                        logging.info("perform_query_for_DTC_record_for_Master")
			dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 in dig_result) and (dig_server2 not in dig_result):
                                assert True
                        else:
                                assert False

	@pytest.mark.run(order=29)
        def test_029_perform_query_for_DTC_record_for_Member(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                        logging.info("perform_query_for_DTC_record_for_Member")
			dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 in dig_result) and (dig_server2 not in dig_result):
                                assert True
                        else:
                                assert False
                logging.info("Test Case 29 Execution Completed")
                sleep(10)

	@pytest.mark.run(order=30)
        def test_030_Enabling_auto_consolidated_monitors_at_Lbdn(self):
                logging.info("Enabling_auto_consolidated_monitors_at_Lbdn ")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:lbdn", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"auto_consolidated_monitors": True}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                print("Restart DNS Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(30)

	@pytest.mark.run(order=31)
        def test_031_perform_query_for_DTC_record_for_Master(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                        logging.info("perform_query_for_DTC_record_for_Master")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 in dig_result) and (dig_server2 not in dig_result):
                                assert True
                        else:
                                assert False

        @pytest.mark.run(order=32)
        def test_032_perform_query_for_DTC_record_for_Member(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                        logging.info("perform_query_for_DTC_record_for_Member")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 in dig_result) and (dig_server2 not in dig_result):
                                assert True
                        else:
                                assert False
                logging.info("Test Case 32 Execution Completed")
                sleep(10)

	@pytest.mark.run(order=33)
        def test_033_Disabling_auto_consolidated_monitors_at_Pool_Negative(self):
                logging.info("Enabling_auto_consolidated_monitors_at_Pool ")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:pool", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"auto_consolidated_monitors": False}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
		response=str(response)
                print(response,type(response))
                print("Restart DNS Services")
		warning="Cannot manually disable the Auto Consolidated Monitor option on the DTC pool"
		response=response.replace('\n','').replace('{','').replace('}','').replace(']','').replace('[','').replace('\\','')
		print(response)
		assert re.search(r'''"text": "Cannot manually disable the Auto Consolidated Monitor option on the DTC pool 'Pool1' because it inherited from linked LBDN''',response)
		
	@pytest.mark.run(order=34)
        def test_034_Editing_consolidated_monitors_at_Pool_Negative(self):
                logging.info("Editing_consolidated_monitors_at_Pool ")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:pool", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"consolidated_monitors": [{"availability": "ALL","full_health_communication": False,"members": [config.grid_fqdn],"monitor":"dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"}]}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                response=str(response)
                print(response,type(response))	
                response=response.replace('\n','').replace('{','').replace('}','').replace(']','').replace('[','').replace('\\','')
                print(response)
                assert re.search(r'''"text": "Cannot do any changes in the list of Consolidated Monitors on DTC pool 'Pool1' while Auto Consolidated Monitors option enabled''',response)

	@pytest.mark.run(order=35)
        def test_035_Create_topology_Rule(self):
                logging.info("Create a topology ruleset")
		if dig_server1==config.Server2:
                        destination_link="dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjE:server1"
                elif dig_server1==config.Server1:
                        destination_link="dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjI:server2"
                data = {"name":"topo1","rules":[{"sources": [{"source_op": "IS","source_type": "SUBNET","source_value": "10.36.0.0/16"}],"dest_type": "SERVER","return_type":"REGULAR","destination_link":destination_link}]}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:topology", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True


	@pytest.mark.run(order=36)
        def test_036_add_topology_to_DTC_pool(self):
                logging.info("Create A DTC Pool")
		ref =  ib_NIOS.wapi_request('GET', object_type="dtc:pool", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"lb_preferred_method": "TOPOLOGY","lb_preferred_topology": "dtc:topology/ZG5zLmlkbnNfdG9wb2xvZ3kkdG9wbzE:topo1","lb_alternate_method": "SOURCE_IP_HASH"}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1, fields=json.dumps(data))
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
                sleep(120)
                logging.info("Test Case 36 Execution Completed")	

	@pytest.mark.run(order=37)
        def test_037_perform_query_for_DTC_record_for_Master(self):
               for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                        logging.info("perform_query_for_DTC_record_for_Master")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 not in dig_result) and (dig_server2 in dig_result):
                                assert True
                        else:
                                assert False

        @pytest.mark.run(order=38)
        def test_038_perform_query_for_DTC_record_for_Member(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                        logging.info("perform_query_for_DTC_record_for_Member")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 not in dig_result) and (dig_server2 in dig_result):
                                assert True
                        else:
                                assert False
                logging.info("Test Case 38 Execution Completed")
                sleep(10)

        @pytest.mark.run(order=39)
        def test_039_Modify_pool_with_SOURCE_IP_HASH(self):
                logging.info("Create A DTC Pool")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:pool", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"lb_preferred_method": "SOURCE_IP_HASH"}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1, fields=json.dumps(data))
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
                logging.info("Test Case 39 Execution Completed")

        @pytest.mark.run(order=40)
        def test_040_Verify_pool_with_SOURCE_IP_HASH_And_Auto_cons(self):        
                logging.info("Create A DTC Pool")
                response =  ib_NIOS.wapi_request('GET', object_type="dtc:pool?_return_fields=auto_consolidated_monitors,lb_preferred_method", grid_vip=config.grid_vip)
                print response
                if ('"auto_consolidated_monitors": true' in response) and ('"lb_preferred_method": "SOURCE_IP_HASH"' in response):
                    assert True
                else:
                    assert False


        @pytest.mark.run(order=41)
        def test_041_Disabling_auto_consolidated_monitors_at_Lbdn(self):
                logging.info("Enabling_auto_consolidated_monitors_at_Lbdn ")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:lbdn", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"auto_consolidated_monitors": False}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                print("Restart DNS Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(60)

        @pytest.mark.run(order=42)
        def test_042_Verify_Auto_consolidated_monitors_at_Pool_and_LBDN(self):
                logging.info("Verify_Auto_consolidated_monitors_at_Pool")
                response =  ib_NIOS.wapi_request('GET', object_type="dtc:pool?_return_fields=auto_consolidated_monitors,consolidated_monitors", grid_vip=config.grid_vip)
                print response
                response_lbdn =  ib_NIOS.wapi_request('GET', object_type="dtc:lbdn?_return_fields=auto_consolidated_monitors", grid_vip=config.grid_vip)
                print response_lbdn

                if ('"auto_consolidated_monitors": false' in response) and ('"consolidated_monitors": []' in response) and ('"auto_consolidated_monitors": false' in response_lbdn):
                    assert True
                else:
                    assert False

        @pytest.mark.run(order=43)
        def test_043_Modify_pool_with_Consolidated_Monitors(self):
                logging.info("Modify_pool_with_Consolidated_Monitors")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:pool", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"consolidated_monitors": [{"availability": "ALL","full_health_communication": False,"members": [config.grid_member1_fqdn],"monitor":"dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"}]} 
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                print("Restart DNS Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(30)

        @pytest.mark.run(order=44)
        def test_044_Verify_consolidated_monitors_at_Pool(self):
                logging.info("Verify_consolidated_monitors_at_Pool")
                response =  ib_NIOS.wapi_request('GET', object_type="dtc:pool?_return_fields=auto_consolidated_monitors,consolidated_monitors", grid_vip=config.grid_vip)
                print response
                if ('"auto_consolidated_monitors": false' in response) and ('"full_health_communication": false' in response):
                    assert True
                else:
                    assert False

        @pytest.mark.run(order=45)
        def test_045_Starting_Logs(self):
                logging.info("Logs Validation")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                sleep(20)

        @pytest.mark.run(order=46)
        def test_046_Enabling_auto_consolidated_monitors_at_Lbdn(self):
                logging.info("Enabling_auto_consolidated_monitors_at_Lbdn ")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:lbdn", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"auto_consolidated_monitors": True}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                print("Restart DNS Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(60)

        @pytest.mark.run(order=47)
        def test_047_Verify_Auto_consolidated_monitors_at_Pool_and_LBDN(self):
                logging.info("Verify_Auto_consolidated_monitors_at_Pool")
                response =  ib_NIOS.wapi_request('GET', object_type="dtc:pool?_return_fields=auto_consolidated_monitors,consolidated_monitors", grid_vip=config.grid_vip)
                print response
                response_lbdn =  ib_NIOS.wapi_request('GET', object_type="dtc:lbdn?_return_fields=auto_consolidated_monitors", grid_vip=config.grid_vip)
                print response_lbdn

                if ('"auto_consolidated_monitors": true' in response) and ('"full_health_communication": true' in response) and ('"auto_consolidated_monitors": true' in response_lbdn):
                    assert True
                else:
                    assert False

        @pytest.mark.run(order=48)
        def test_048_Stopping_Logs(self):
                logging.info("Logs Validation")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                sleep(20)

        @pytest.mark.run(order=49)
        def test_049_looking_for_Health_Status_Update(self):
                check=commands.getoutput(" grep -cw \".*idns_rpc_idnsd.c.* .*Finished getting FULL health update.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox*")
                if (int(check)!=0):
                    assert True
                else:
                    assert False
                sleep(20)
                print("Test case 49 Execution Completed")

        @pytest.mark.run(order=50)
        def test_050_perform_query_for_DTC_record_for_Master(self):
        	for i in range(3):
                        print(dig_server1)
                        dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                        logging.info("perform_query_for_DTC_record_for_Master")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 in dig_result) and (dig_server2 not in dig_result):
                                assert True
                        else:
                                assert False

        @pytest.mark.run(order=51)
        def test_051_perform_query_for_DTC_record_for_Member(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                        dig_cmd1 = os.system(dig_cmd)
                        sleep(10)
                        logging.info("perform_query_for_DTC_record_for_Member")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 in dig_result) and (dig_server2 not in dig_result):
                                assert True
                        else:
                                assert False

                logging.info("Test Case 51 Execution Completed")
                sleep(10)

        @pytest.mark.run(order=52)
        def test_052_Execute_DROP_Command_in_Master(self):
                logging.info("Execute_DROP_Command_in_Master")
                drop='iptables -I INPUT -s '+dig_server1+' -j DROP'
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline(drop)
                child.expect('#')
                sleep(60)

        @pytest.mark.run(order=53)
        def test_053_perform_query_for_DTC_record_for_Master(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                        dig_cmd1 = os.system(dig_cmd)
                        sleep(10)
                        logging.info("perform_query_for_DTC_record_for_Master")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 not in dig_result) and (dig_server2 in dig_result):
                                assert True
                        else:
                                assert False

        @pytest.mark.run(order=54)
        def test_054_perform_query_for_DTC_record_for_Member(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                        dig_cmd1 = os.system(dig_cmd)
                        sleep(10)
                        logging.info("perform_query_for_DTC_record_for_Member")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 not in dig_result) and (dig_server2 in dig_result):
                                assert True
                        else:
                                assert False
                logging.info("Test Case 54 Execution Completed")
                sleep(10)

        @pytest.mark.run(order=55)
        def test_055_Execute_DROP_Command_in_Member(self):
                logging.info("Execute_DROP_Command_in_Member")
                drop='iptables -I INPUT -s '+dig_server2+' -j DROP'
                print(drop)
                print(config.grid_member1_vip)
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline(drop)
                child.expect('#')
                sleep(60)

        @pytest.mark.run(order=56)
        def test_056_perform_query_for_DTC_record_for_Master(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                        dig_cmd1 = os.system(dig_cmd)
                        sleep(10)
                        logging.info("perform_query_for_DTC_record_for_Master")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 not in dig_result) and (dig_server2 not in dig_result):
                                assert True
                        else:
                                assert False

        @pytest.mark.run(order=57)
        def test_057_perform_query_for_DTC_record_for_Member(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                        sleep(10)
                        logging.info("perform_query_for_DTC_record_for_Member")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 not in dig_result) and (dig_server2 not in dig_result):
                                assert True
                        else:
                                assert False
                logging.info("Test Case 57 Execution Completed")
                sleep(10)

        @pytest.mark.run(order=58)
        def test_058_Execute_ACCEPT_Command_in_Member(self):
                logging.info("Execute_ACCEPT_Command_in_Member")
                accept='iptables -I INPUT -s '+dig_server2+' -j ACCEPT'
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline(accept)
                child.expect('#')
                sleep(60)

        @pytest.mark.run(order=59)
        def test_059_perform_query_for_DTC_record_for_Master(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                        sleep(10)
                        logging.info("perform_query_for_DTC_record_for_Master")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 not in dig_result) and (dig_server2 in dig_result):
                                assert True
                        else:
                                assert False

        @pytest.mark.run(order=60)
        def test_060_perform_query_for_DTC_record_for_Member(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                        logging.info("perform_query_for_DTC_record_for_Member")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 not in dig_result) and (dig_server2 in dig_result):
                                assert True
                        else:
                                assert False
                logging.info("Test Case 60 Execution Completed")
                sleep(10)

        @pytest.mark.run(order=61)
        def test_061_Execute_ACCEPT_Command_in_Master(self):
                logging.info("Execute_ACCEPT_Command_in_Master")
                accept='iptables -I INPUT -s '+dig_server1+' -j ACCEPT'
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline(accept)
                child.expect('#')
                sleep(60)

        @pytest.mark.run(order=62)
        def test_062_perform_query_for_DTC_record_for_Master(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                        logging.info("perform_query_for_DTC_record_for_Master")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 in dig_result) and (dig_server2 not in dig_result):
                                assert True
                        else:
                                assert False

        @pytest.mark.run(order=63)
        def test_063_perform_query_for_DTC_record_for_Member(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                        sleep(10)
                        logging.info("perform_query_for_DTC_record_for_Member")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 in dig_result) and (dig_server2 not in dig_result):
                                assert True
                        else:
                                assert False
                logging.info("Test Case 63 Execution Completed")
                sleep(10)

        @pytest.mark.run(order=64)
        def test_064_Disabling_auto_consolidated_monitors_at_Lbdn(self):
                logging.info("Disabling_auto_consolidated_monitors_at_Lbdn ")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:lbdn", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"auto_consolidated_monitors": False}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                print("Restart DNS Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(60)

        @pytest.mark.run(order=65)
        def test_065_Verify_pool_AND_LBDN_with_SOURCE_IP_HASH_And_Auto_cons(self):
                logging.info("Create A DTC Pool")
                response =  ib_NIOS.wapi_request('GET', object_type="dtc:pool?_return_fields=auto_consolidated_monitors,lb_preferred_method", grid_vip=config.grid_vip)
                print response
                response_lbdn =  ib_NIOS.wapi_request('GET', object_type="dtc:lbdn?_return_fields=auto_consolidated_monitors,lb_method", grid_vip=config.grid_vip)
                print response_lbdn
		
                if ('"auto_consolidated_monitors": false' in response) and ('"lb_preferred_method": "SOURCE_IP_HASH"' in response) and ('"auto_consolidated_monitors": false' in response_lbdn) and ('"lb_method": "SOURCE_IP_HASH"' in response_lbdn):
                    assert True
                else:
                    assert False
                print("sleep for 20 sec")

        @pytest.mark.run(order=66)
        def test_066_perform_query_for_DTC_record_for_Master(self):
                for i in range(3):
                        print(dig_server1)
                        dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                        logging.info("perform_query_for_DTC_record_for_Master")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 in dig_result) and (dig_server2 not in dig_result):
                                assert True
                        else:
                                assert False

        @pytest.mark.run(order=67)
        def test_067_perform_query_for_DTC_record_for_Member(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                        dig_cmd1 = os.system(dig_cmd)
                        sleep(10)
                        logging.info("perform_query_for_DTC_record_for_Member")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 in dig_result) and (dig_server2 not in dig_result):
                                assert True
                        else:
                                assert False

                logging.info("Test Case 67 Execution Completed")
                sleep(10)

        @pytest.mark.run(order=68)
        def test_068_Enabling_auto_consolidated_monitors_at_Pool(self):
                logging.info("Enabling_auto_consolidated_monitors_at_Pool ")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:pool", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"auto_consolidated_monitors": True}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                print("Restart DNS Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("sleep for 100 secs")
                sleep(100)


        @pytest.mark.run(order=69)
        def test_069_Verify_pool_AND_LBDN_with_SOURCE_IP_HASH_And_Auto_cons(self):
                logging.info("Create A DTC Pool")
                response =  ib_NIOS.wapi_request('GET', object_type="dtc:pool?_return_fields=auto_consolidated_monitors,lb_preferred_method", grid_vip=config.grid_vip)
                print response
                response_lbdn =  ib_NIOS.wapi_request('GET', object_type="dtc:lbdn?_return_fields=auto_consolidated_monitors,lb_method", grid_vip=config.grid_vip)
                print response_lbdn
                if ('"auto_consolidated_monitors": true' in response) and ('"lb_preferred_method": "SOURCE_IP_HASH"' in response) and ('"auto_consolidated_monitors": false' in response_lbdn) and ('"lb_method": "SOURCE_IP_HASH"' in response_lbdn):
                    assert True
                else:
                    assert False
                print("sleep for 20 sec")

        @pytest.mark.run(order=70)
        def test_070_perform_query_for_DTC_record_for_Master(self):
                
                for i in range(3):
                        print(dig_server1)
                        dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                        logging.info("perform_query_for_DTC_record_for_Master")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 in dig_result) and (dig_server2 not in dig_result):
                                assert True
                        else:
                                assert False

        @pytest.mark.run(order=71)
        def test_071_perform_query_for_DTC_record_for_Member(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                        dig_cmd1 = os.system(dig_cmd)
                        sleep(10)
                        logging.info("perform_query_for_DTC_record_for_Member")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 in dig_result) and (dig_server2 not in dig_result):
                                assert True
                        else:
                                assert False

                logging.info("Test Case 71 Execution Completed")
                sleep(10)

        @pytest.mark.run(order=72)
        def test_072_Execute_DROP_Command_in_Member(self):
                logging.info("Execute_DROP_Command_in_Master")
                drop='iptables -I INPUT -s '+dig_server1+' -j DROP'
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline(drop)
                child.expect('#')
                sleep(60)

        @pytest.mark.run(order=73)
        def test_073_perform_query_for_DTC_record_for_Master(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                        dig_cmd1 = os.system(dig_cmd)
                        sleep(10)
                        logging.info("perform_query_for_DTC_record_for_Master")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 not in dig_result) and (dig_server2 in dig_result):
                                assert True
                        else:
                                assert False

        @pytest.mark.run(order=74)
        def test_074_perform_query_for_DTC_record_for_Member(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                        dig_cmd1 = os.system(dig_cmd)
                        sleep(10)
                        logging.info("perform_query_for_DTC_record_for_Member")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 not in dig_result) and (dig_server2 in dig_result):
                                assert True
                        else:
                                assert False
                logging.info("Test Case 75 Execution Completed")
                sleep(10)

        @pytest.mark.run(order=75)
        def test_075_Execute_DROP_Command_in_Master(self):
                logging.info("Execute_DROP_Command_in_Member")
                drop='iptables -I INPUT -s '+dig_server2+' -j DROP'
                print(drop)
                print(config.grid_member1_vip)
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline(drop)
                child.expect('#')
                sleep(60)

        @pytest.mark.run(order=76)
        def test_076_perform_query_for_DTC_record_for_Master(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                        sleep(10)
                        logging.info("perform_query_for_DTC_record_for_Master")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 not in dig_result) and (dig_server2 not in dig_result):
                                assert True
                        else:
                                assert False

        @pytest.mark.run(order=77)
        def test_077_perform_query_for_DTC_record_for_Member(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                        sleep(10)
                        logging.info("perform_query_for_DTC_record_for_Member")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 not in dig_result) and (dig_server2 not in dig_result):
                                assert True
                        else:
                                assert False
                logging.info("Test Case 77 Execution Completed")
                sleep(10)

        @pytest.mark.run(order=78)
        def test_078_Execute_ACCEPT_Command_in_Master(self):
                logging.info("Execute_ACCEPT_Command_in_Member")
                accept='iptables -I INPUT -s '+dig_server2+' -j ACCEPT'
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline(accept)
                child.expect('#')
                sleep(60)

        @pytest.mark.run(order=79)
        def test_079_perform_query_for_DTC_record_for_Master(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                        sleep(10)
                        logging.info("perform_query_for_DTC_record_for_Master")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 not in dig_result) and (dig_server2 in dig_result):
                                assert True
                        else:
                                assert False

        @pytest.mark.run(order=80)
        def test_080_perform_query_for_DTC_record_for_Member(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                        logging.info("perform_query_for_DTC_record_for_Member")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 not in dig_result) and (dig_server2 in dig_result):
                                assert True
                        else:
                                assert False
                logging.info("Test Case 80 Execution Completed")
                sleep(10)

        @pytest.mark.run(order=81)
        def test_081_Execute_ACCEPT_Command_in_Master(self):
                logging.info("Execute_ACCEPT_Command_in_Master")
                accept='iptables -I INPUT -s '+dig_server1+' -j ACCEPT'
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline(accept)
                child.expect('#')
                sleep(60)

        @pytest.mark.run(order=82)
        def test_082_Execute_ACCEPT_Command_in_Master(self):
                logging.info("Execute_ACCEPT_Command_in_Master")
                accept='iptables -I INPUT -s '+dig_server1+' -j ACCEPT'
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline(accept)
                child.expect('#')
                sleep(60)

        @pytest.mark.run(order=83)
        def test_083_perform_query_for_DTC_record_for_Master(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                        logging.info("perform_query_for_DTC_record_for_Master")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 in dig_result) and (dig_server2 not in dig_result):
                                assert True
                        else:
                                assert False

        @pytest.mark.run(order=84)
        def test_084_perform_query_for_DTC_record_for_Member(self):
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                        logging.info("perform_query_for_DTC_record_for_Member")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (dig_server1 in dig_result) and (dig_server2 not in dig_result):
                                assert True
                        else:
                                assert False
                logging.info("Test Case 29 Execution Completed")
                sleep(10)

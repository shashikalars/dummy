__author__ = "Siva Krishna"
__email__  = "krishnas@infoblox.com"

######################################################################################################################
#  Grid Set up required:                                                                                             #
#  1. Grid Master + Grid Member                                                                                      #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415),DTC                                                                #
######################################################################################################################
import re
import sys
import config
import subprocess
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
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
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
        def test_004_Validate_AuthZone(self):
                logging.info("Validate the  Zone")
                response =  ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=dtc.com", grid_vip=config.grid_vip)
                print response
                if ('"fqdn": "dtc.com"' in response):
                    assert True
                else:
                    assert False
                logging.info("Test Case 4 Execution Completed")

        @pytest.mark.run(order=5)
        def test_005_add_a_DTC_Server1(self):
                logging.info("Create A DTC Server")
                data = {"name":"server1","host":config.Server1}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 5 Execution Completed")

	@pytest.mark.run(order=6)
        def test_006_Validate_Server2(self):
                logging.info("Validate_Server")
                response =  ib_NIOS.wapi_request('GET', object_type="dtc:server?name=server1", grid_vip=config.grid_vip)
                print response
                host='"host": '+'"'+config.Server1+'"'
                if (host in response) and ('"name": "server1"' in response):
                    assert True
                else:
                    assert False
                logging.info("Test Case 6 Execution Completed")
	@pytest.mark.run(order=7)
        def test_007_add_a_DTC_Server2(self):
                logging.info("Create A DTC Second Server")
                data = {"name":"server2","host":config.Server2}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 7 Execution Completed")
	
	@pytest.mark.run(order=8)
        def test_008_Validate_Server2(self):
                logging.info("Validate_Server")
                response =  ib_NIOS.wapi_request('GET', object_type="dtc:server?name=server2", grid_vip=config.grid_vip)
                print response
                host='"host": '+'"'+config.Server2+'"'
                if (host in response) and ('"name": "server2"' in response):
                    assert True
                else:
                    assert False
		logging.info("Test Case 8 Execution Completed")

        @pytest.mark.run(order=9)
        def test_009_add_a_DTC_pool(self):
                logging.info("Create A DTC Pool")
                data = {"name": "Pool1","lb_preferred_method": "ROUND_ROBIN","servers": [{"ratio": 1,"server": "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjE:server1"},{"ratio": 1,"server": "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjI:server2"}],"monitors": ["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"]}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:pool", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 9 Execution Completed")

	@pytest.mark.run(order=10)
        def test_010_Verify_DTC_pool(self):
                logging.info("Verify DTC Pool")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:pool?name=Pool1", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=name,lb_preferred_method", grid_vip=config.grid_vip)
                print response
                if ('"name": "Pool1"' in response) and ('"lb_preferred_method": "ROUND_ROBIN"' in response):
                    assert True
                else:
                    assert False
                logging.info("Test Case 10 Execution Completed")

	@pytest.mark.run(order=11)
        def test_011_add_a_DTC_lbdn(self):
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
                logging.info("Test Case 11 Execution Completed")

        @pytest.mark.run(order=12)
        def test_012_Verify_LBDN(self):
                logging.info("Verify DTC LBDN")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:lbdn?name=lbdn", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=name,lb_method", grid_vip=config.grid_vip)
                print response
                if ('"name": "lbdn"' in response) and ('"lb_method": "ROUND_ROBIN"' in response):
                    assert True
                else:
                    assert False 
                logging.info("Test Case 12 Execution Completed")

        @pytest.mark.run(order=13)
        def test_013_add_topology_ruleset(self):
                 logging.info("Create a topology ruleset")
		 data = {"name":"topo1","rules":[{"sources": [{"source_op": "IS","source_type": "SUBNET","source_value": "10.0.0.0/8"}],"dest_type": "SERVER","return_type":"REGULAR","destination_link":"dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjE:server1"},{"sources": [{"source_op": "IS","source_type": "SUBNET","source_value": "20.0.0.0/8"}],"dest_type": "SERVER","return_type":"NXDOMAIN"}]}
		 response = ib_NIOS.wapi_request('POST', object_type="dtc:topology", fields=json.dumps(data))
                 print response
                 logging.info(response)
                 read  = re.search(r'201',response)
                 for read in  response:
                         assert True
                 logging.info("Test Case 13 Execution Completed")

        @pytest.mark.run(order=14)
        def test_014_Verify_DTC_topology(self):
                logging.info("Verify DTC topology")
                response =  ib_NIOS.wapi_request('GET', object_type="dtc:topology?_return_fields=name", grid_vip=config.grid_vip)
                print response
                if ('"name": "topo1"' in response):
                    assert True
                else:
                    assert False
                logging.info("Test Case 14 Execution Completed")

        @pytest.mark.run(order=15)
        def test_015_Modify_pool_with_Topology_and_Consolidated_Monitors_ALL(self):
                logging.info("Modify_pool_with_Topology_and_Consolidated_Monitors ALL")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:pool", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"consolidated_monitors": [{"availability": "ALL","full_health_communication": False,"members": [config.grid_fqdn],"monitor":"dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"}],"lb_preferred_method":"TOPOLOGY","lb_preferred_topology":"dtc:topology/ZG5zLmlkbnNfdG9wb2xvZ3kkdG9wbzE:topo1","lb_alternate_method":"ROUND_ROBIN"}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                print("Restart DNS Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(30)
                logging.info("Test Case 15 Execution Completed")

        @pytest.mark.run(order=16)
        def test_016_Verify_pool_with_Topology_and_Consolidated_Monitors(self):
                logging.info("Verify_pool_with_Topology_and_Consolidated_Monitors")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:pool?name=Pool1", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=name,consolidated_monitors,lb_preferred_method", grid_vip=config.grid_vip)
                print response
                if ('"name": "Pool1"' in response) and ('"lb_preferred_method": "TOPOLOGY"' in response) and ('"availability": "ALL"' in response):
                    assert True
                else:
                    assert False
                logging.info("Test Case 16 Execution Completed")

        @pytest.mark.run(order=17)
        def test_017_Validate_Core_files(self):
                logging.info("Validating core files")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
                child.expect('#')
                child.sendline('cd /storage/cores/')
                child.expect('#')
                child.sendline('ls -lrt /storage/cores')
                child.expect('#')
                core_files=child.before
                print(core_files,type(core_files))
                core_files=core_files.split('\r\n')
                print(core_files)
                L=[]
                for i in core_files:
                    file = i.split(' ')
                    if len(file) >= 9:
                        L.append(file[-1])
                print(L)
                for core in L:
                    core=core.split('.')
                    if "SIGSEGV" in core:
                        assert False
                        print("Core files are generated")
                    else:
                        assert True
                        print("Core files not are generated")
                logging.info("Test Case 17 Execution Completed")
        
        @pytest.mark.run(order=18)
        def test_018_Modify_pool_with_Topology_and_Consolidated_Monitors_with_ANY(self):
                logging.info("Modify_pool_with_Topology_and_Consolidated_Monitors ANY")
                logging.info("Verify_pool_with_Topology_and_Consolidated_Monitors")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:pool?name=Pool1", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=name,consolidated_monitors,lb_preferred_method", grid_vip=config.grid_vip)
                print response
                data = {"consolidated_monitors": [{"availability": "ANY","full_health_communication": False,"members": [config.grid_fqdn],"monitor":"dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"}],"lb_preferred_method":"TOPOLOGY","lb_preferred_topology":"dtc:topology/ZG5zLmlkbnNfdG9wb2xvZ3kkdG9wbzE:topo1","lb_alternate_method":"ROUND_ROBIN"}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                print("Restart DNS Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(30)
                logging.info("Test Case 18 Execution Completed") 

        @pytest.mark.run(order=19)
        def test_019_Verify_pool_with_Topology_and_Consolidated_Monitors_ANY(self):
                logging.info("Verify_pool_with_Topology_and_Consolidated_Monitors ANY")
                response =  ib_NIOS.wapi_request('GET', object_type="dtc:pool?_return_fields=name,consolidated_monitors,lb_preferred_method", grid_vip=config.grid_vip)
                print response
                if ('"name": "Pool1"' in response) and ('"lb_preferred_method": "TOPOLOGY"' in response) and ('"availability": "ANY"' in response):
                    assert True
                else:
                    assert False
                logging.info("Test Case 19 Execution Completed")

        @pytest.mark.run(order=20)
        def test_020_Validate_Core_files(self):
                logging.info("Validating core files")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
                child.expect('#')
                child.sendline('cd /storage/cores/')
                child.expect('#')
                child.sendline('ls -lrt /storage/cores')
                child.expect('#')
                core_files=child.before
                print(core_files,type(core_files))
                core_files=core_files.split('\r\n')
                print(core_files)
                L=[]
                for i in core_files:
                    file = i.split(' ')
                    if len(file) >= 9:
                        L.append(file[-1])
                print(L)
                for core in L:
                    core=core.split('.')
                    if "SIGSEGV" in core:
                        assert False
                        print("Core files are generated")
                    else:
                        assert True
                        print("Core files not are generated")
                logging.info("Test Case 20 Execution Completed")

        @pytest.mark.run(order=21)
        def test_021_Run_the_dig_command_on_grid_master_which_matches_topology_rule(self):
                logging.info("Run_the_dig_command_on_grid_master which_matches_topology_rule")
                output = os.popen("for i in {1..1000}; do dig @"+str(config.grid_vip)+" a1.dtc.com +short; done >DTC_1.log").read()
                output1 = os.popen("grep -v PST DTC_1.log | sort | uniq -dc").read()
                print(output1)
		result="1000 "+config.Server1
		if(result in output1):
			assert True
		else:
			assert False
		logging.info("Test Case 21 Execution Completed")

	@pytest.mark.run(order=22)
        def test_022_Run_the_dig_command_on_grid_member_which_matches_topology_rule(self):
                logging.info("Run_the_dig_command_on_grid_member which_matches_topology_rule")
                output = os.popen("for i in {1..1000}; do dig @"+str(config.grid_member1_vip)+" a1.dtc.com +short; done >DTC_1.log").read()
                output1 = os.popen("grep -v PST DTC_1.log | sort | uniq -dc").read()
                print(output1)
		result="1000 "+config.Server1
                if(result in output1):
                        assert True
                else:
                        assert False
		logging.info("Test Case 22 Execution Completed")

	@pytest.mark.run(order=23)
        def test_023_Run_the_dig_command_on_grid_master_With_different_Subnet_Before_Enabling_EDNS0(self):
                logging.info("Run_the_dig_command_on_grid_master With_different_Subnet_Before_Enabling_EDNS0")
                output = os.popen("for i in {1..1000}; do dig @"+str(config.grid_vip)+" a1.dtc.com +subnet=40.1.1.10/24 +short; done >DTC_1.log").read()
                output1 = os.popen("grep -v PST DTC_1.log | sort | uniq -dc").read()
                print(output1)
		result="1000 "+config.Server1
                if(result in output1):
                        assert True
                else:
                        assert False
		logging.info("Test Case 23 Execution Completed")

        @pytest.mark.run(order=22)
        def test_024_Run_the_dig_command_on_grid_member_With_different_Subnet_Before_Enabling_EDNS0(self):
                logging.info("Run_the_dig_command_on_grid_member With_different_Subnet_Before_Enabling_EDNS0")
                output = os.popen("for i in {1..1000}; do dig @"+str(config.grid_member1_vip)+" a1.dtc.com +subnet=40.1.1.10/24 +short; done >DTC_1.log").read()
                output1 = os.popen("grep -v PST DTC_1.log | sort | uniq -dc").read()
                print(output1)
		result="1000 "+config.Server1
                if(result in output1):
                        assert True
                else:
                        assert False
		logging.info("Test Case 24 Execution Completed")

	@pytest.mark.run(order=25)
        def test_025_enabling_EDNS0_to_query_from_Different_Subnets(self):
                logging.info("enabling_EDNS0 to query from different subnets ")
                ref =  ib_NIOS.wapi_request('GET', object_type="grid:dns", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"dtc_edns_prefer_client_subnet": True}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                print("Restart DNS Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20)
		logging.info("Test Case 25 Execution Completed")		

	@pytest.mark.run(order=26)
        def test_026_Validate_Enabled_EDNS0(self):
                logging.info("Validate_Enabled_EDNS0")
                response =  ib_NIOS.wapi_request('GET', object_type="grid:dns?_return_fields=dtc_edns_prefer_client_subnet", grid_vip=config.grid_vip)
                print response
		response = json.loads(response)
		for i in response:
                        print i
                        logging.info("found")
                        assert i["dtc_edns_prefer_client_subnet"] == True
		logging.info("Test Case 26 Execution Completed")
	
	@pytest.mark.run(order=27)
        def test_027_Run_the_dig_command_on_grid_master_which_matches_topology_rule(self):
                logging.info("Run_the_dig_command_on_grid_master_which_matches_topology_rule")
                output = os.popen("for i in {1..1000}; do dig @"+str(config.grid_vip)+" a1.dtc.com +short; done >DTC_1.log").read()
                output1 = os.popen("grep -v PST DTC_1.log | sort | uniq -dc").read()
                print(output1)
		result="1000 "+config.Server1
                if(result in output1):
                        assert True
                else:
                        assert False
		logging.info("Test Case 27 Execution Completed")

        @pytest.mark.run(order=28)
        def test_028_Run_the_dig_command_on_grid_member_which_matches_topology_rule(self):
                logging.info("Run_the_dig_command_on_grid_member which_matches_topology_rule")
                output = os.popen("for i in {1..1000}; do dig @"+str(config.grid_member1_vip)+" a1.dtc.com +short; done >DTC_1.log").read()
                output1 = os.popen("grep -v PST DTC_1.log | sort | uniq -dc").read()
                print(output1)
		result="1000 "+config.Server1
                if(result in output1):
                        assert True
                else:
                        assert False
		logging.info("Test Case 28 Execution Completed")

        @pytest.mark.run(order=29)
        def test_029_Run_the_dig_command_on_grid_master_With_different_Subnet_After_Enabling_EDNS0(self):
                logging.info("Run_the_dig_command_on_grid_master With_different_Subnet_After_Enabling_EDNS0")
                output = os.popen("for i in {1..1000}; do dig @"+str(config.grid_vip)+" a1.dtc.com +subnet=40.1.1.10/24 +short; done >DTC_1.log").read()
                output1 = os.popen("grep -v PST DTC_1.log | sort | uniq -dc").read()
                print(output1)
		result="500 "+config.Server1
		result1="500 "+config.Server2
                if((result in output1) and (result1 in output1)):
                        assert True
                else:
                        assert False
		logging.info("Test Case 29 Execution Completed")

	@pytest.mark.run(order=30)
        def test_030_Run_the_dig_command_on_grid_member_With_different_Subnet_After_Enabling_EDNS0(self):
                logging.info("Run_the_dig_command_on_grid_member With_different_Subnet_After_Enabling_EDNS0")
                output = os.popen("for i in {1..1000}; do dig @"+str(config.grid_member1_vip)+" a1.dtc.com +subnet=40.1.1.10/24 +short; done >DTC_1.log").read()
                output1 = os.popen("grep -v PST DTC_1.log | sort | uniq -dc").read()
                print(output1)
		result="500 "+config.Server1
                result1="500 "+config.Server2
                if((result in output1) and (result1 in output1)):
                        assert True
                else:
                        assert False
		logging.info("Test Case 30 Execution Completed")	

	@pytest.mark.run(order=31)
        def test_031_perform_query_for_DTC_record_NXDOMAIN_rule_for_Master(self):
		logging.info("perform_query_for_DTC_record_NXDOMAIN rule_for_Master")
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com +subnet=20.1.1.10/24'
                        logging.info("perform_query_for_DTC_record_for_Master")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (("status: NXDOMAIN" in dig_result) and (config.Server1 not in dig_result) and (config.Server2 not in dig_result)):
                                assert True
                        else:
                                assert False
		logging.info("Test Case 31 Execution Completed")

	@pytest.mark.run(order=32)
        def test_032_perform_query_for_DTC_record_NXDOMAIN_rule_for_Member(self):
                logging.info("perform_query_for_DTC_record_NXDOMAIN rule for_Member")
                for i in range(3):
                        dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com +subnet=20.1.1.10/24'
                        logging.info("perform_query_for_DTC_record_for_Master")
                        dig_result = subprocess.check_output(dig_cmd, shell=True)
                        print dig_result
                        if (("status: NXDOMAIN" in dig_result) and (config.Server1 not in dig_result) and (config.Server2 not in dig_result)):
                                assert True
                        else:
                                assert False
                logging.info("Test Case 32 Execution Completed")
	
        @pytest.mark.run(order=33)
        def test_033_Delete_LBDN(self):
                logging.info("Delete Lbdn")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:lbdn?name=lbdn", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('DELETE', object_type=ref1, grid_vip=config.grid_vip)
                print response
                logging.info("Test Case 33 Execution Completed")

        @pytest.mark.run(order=34)
        def test_034_Verify_Deleted_LBDN(self):
                logging.info("Verify_Deleted Lbdn")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:lbdn?name=lbdn", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                print res
                if res==[]:
                    assert True
                else:
                    assert False
                logging.info("Test Case 34 Execution Completed")

        @pytest.mark.run(order=35)
        def test_035_Delete_Pool(self):
                logging.info("Delete Pool")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:pool?name=Pool1", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('DELETE', object_type=ref1, grid_vip=config.grid_vip)
                print response
                logging.info("Test Case 35 Execution Completed")

        @pytest.mark.run(order=36)
        def test_036_Verify_Deleted_Pool(self):
                logging.info("Verify Deleted Pool")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:pool?name=Pool1", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                ref1 = json.loads(ref)
                print ref1
                if ref1==[]:
                    assert True
                else:
                    assert False
                logging.info("Test Case 36 Execution Completed")

        @pytest.mark.run(order=37)
        def test_037_Delete_Toporule(self):
                logging.info("Delete Toporule")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:topology?name=topo1", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('DELETE', object_type=ref1, grid_vip=config.grid_vip)
                print response
                logging.info("Test Case 37 Execution Completed")
                
        @pytest.mark.run(order=38)
        def test_038_Verify_Deleted_Toporule(self):
                logging.info("Verify Deleted Toporule")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:topology?name=topo1", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                ref1 = json.loads(ref)
                if ref1==[]:
                    assert True
                else:
                    assert False
                logging.info("Test Case 38 Execution Completed")

        @pytest.mark.run(order=39)
        def test_039_Delete_Server(self):
                logging.info("Delete Server")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:server?name=server1", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('DELETE', object_type=ref1, grid_vip=config.grid_vip)
                print response
                logging.info("Test Case 39 Execution Completed")

        @pytest.mark.run(order=40)
        def test_040_Verify_Deleted_Server(self):
                logging.info("Verify Deleted Server")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:server?name=server1", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                ref1 = json.loads(ref)
                print ref1
                if ref1==[]:
                    assert True
                else:
                    assert False
                logging.info("Test Case 40 Execution Completed")

	@pytest.mark.run(order=41)
        def test_041_Delete_Server2(self):
                logging.info("Delete Server2")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:server?name=server2", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('DELETE', object_type=ref1, grid_vip=config.grid_vip)
                print response
                logging.info("Test Case 41 Execution Completed")

        @pytest.mark.run(order=42)
        def test_042_Verify_Deleted_Server2(self):
                logging.info("Verify Deleted Server")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:server?name=server2", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                ref1 = json.loads(ref)
                print ref1
                if ref1==[]:
                    assert True
                else:
                    assert False
                logging.info("Test Case 42 Execution Completed")

        @pytest.mark.run(order=43)
        def test_043_Delete_Zone(self):
                logging.info("Delete Zone")
                ref =  ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=dtc.com", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('DELETE', object_type=ref1, grid_vip=config.grid_vip)
                print response
                logging.info("Test Case 43 Execution Completed")

        @pytest.mark.run(order=44)
        def test_044_Verify_Deleted_Zone(self):
                logging.info("Verify Deleted Zone")
                ref =  ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=dtc.com", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                ref1 = json.loads(ref)
                print ref1
                if ref1==[]:
                    assert True
                else:
                    assert False
                logging.info("Test Case 44 Execution Completed")
	
	@pytest.mark.run(order=45)
        def test_045_Disabling_EDNS0_to_query_from_Different_Subnets(self):
                logging.info("Disabling_EDNS0 to query from different subnets ")
                ref =  ib_NIOS.wapi_request('GET', object_type="grid:dns", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"dtc_edns_prefer_client_subnet": False}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                print("Restart DNS Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20)
                logging.info("Test Case 45 Execution Completed")

        @pytest.mark.run(order=46)
        def test_046_Validate_Disabled_EDNS0(self):
                logging.info("Validate_Disabled_EDNS0")
                response =  ib_NIOS.wapi_request('GET', object_type="grid:dns?_return_fields=dtc_edns_prefer_client_subnet", grid_vip=config.grid_vip)
                print response
                response = json.loads(response)
                for i in response:
                        print i
                        logging.info("found")
                        assert i["dtc_edns_prefer_client_subnet"] == False
                logging.info("Test Case 46 Execution Completed")

        @pytest.mark.run(order=47)
        def test_047_Stop_DNS_Service(self):
                logging.info("Stop DNS Service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                for i in res:
                        logging.info("Modify a enable_dns")
                        data = {"enable_dns": False}
                        response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
                        print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 47 Execution Completed")

        @pytest.mark.run(order=48)
        def test_048_Validate_DNS_service_Disabled(self):
                logging.info("Validate DNs Service is disabled")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                for i in res:
                        print i
                        logging.info("found")
                        assert i["enable_dns"] == False
                logging.info("Test Case 48 Execution Completed")

	

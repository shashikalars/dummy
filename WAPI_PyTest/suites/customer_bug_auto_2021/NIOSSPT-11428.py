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
import pytest
import unittest
import logging
import os
import subprocess
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
        def test_003_create_New_AuthZone(self):
                logging.info("Create A new Zone")
                data = {"fqdn": "intranet","grid_primary": [{"name": config.grid_fqdn,"stealth":False}, {"name": config.grid_member1_fqdn,"stealth":False}]}
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
                response =  ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=intranet", grid_vip=config.grid_vip)
                print response
                if ('"fqdn": "intranet"' in response):
                    assert True
                else:
                    assert False
                logging.info("Test Case 4 Execution Completed")

        @pytest.mark.run(order=5)
        def test_005_add_a_DTC_Server(self):
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
        def test_006_Validate_Server(self):
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
        def test_007_add_a_DTC_pool(self):
                logging.info("Create A DTC Pool")
                data = {"name": "Pool1","lb_preferred_method": "ROUND_ROBIN","servers": [{"ratio": 1,"server": "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjE:server1"}],"monitors": ["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"]}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:pool", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 7 Execution Completed")

        @pytest.mark.run(order=8)
        def test_008_Verify_DTC_pool(self):
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
                logging.info("Test Case 8 Execution Completed")

        @pytest.mark.run(order=9)
        def test_009_add_a_DTC_lbdn(self):
                logging.info("Create A DTC LBDN")
                data = {"name":"lbdn_gateway_customer","lb_method":"ROUND_ROBIN","patterns": ["gateway.customer-service.intranet"], "pools": [{"pool":"dtc:pool/ZG5zLmlkbnNfcG9vbCRQb29sMQ:Pool1","ratio": 1}], "auth_zones":["zone_auth/ZG5zLnpvbmUkLl9kZWZhdWx0LmludHJhbmV0:intranet/default"],"types":["A","AAAA","CNAME","NAPTR","SRV"]}
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
                logging.info("Test Case 9 Execution Completed")

        @pytest.mark.run(order=10)
        def test_010_Verify_LBDN(self):
                logging.info("Verify DTC LBDN")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:lbdn?name=lbdn_gateway_customer", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=name,lb_method,patterns", grid_vip=config.grid_vip)
                print response
                if ('"name": "lbdn_gateway_customer"' in response) and ('"lb_method": "ROUND_ROBIN"' in response) and ('"gateway.customer-service.intranet"' in response):
                    assert True
                else:
                    assert False
                logging.info("Test Case 10 Execution Completed")

        @pytest.mark.run(order=11)
        def test_011_add_a_DTC_lbdn2(self):
                logging.info("Create A DTC LBDN2")
                data = {"name":"lbdn_atendimento-gateway","lb_method":"ROUND_ROBIN","patterns": ["gateway.customer-service.intranet"],"priority": 2, "pools": [{"pool":"dtc:pool/ZG5zLmlkbnNfcG9vbCRQb29sMQ:Pool1","ratio": 1}], "auth_zones":["zone_auth/ZG5zLnpvbmUkLl9kZWZhdWx0LmludHJhbmV0:intranet/default"],"types":["A","AAAA","CNAME","NAPTR","SRV"]}
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
        def test_012_Verify_LBDN2(self):
                logging.info("Verify DTC LBDN2")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:lbdn?name=lbdn_atendimento-gateway", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=name,lb_method,patterns,auth_zones", grid_vip=config.grid_vip)
                print response
                if ('"name": "lbdn_atendimento-gateway"' in response) and ('"lb_method": "ROUND_ROBIN"' in response) and ('"gateway.customer-service.intranet"' in response):
                    assert True
                else:
                    assert False
                logging.info("Test Case 12 Execution Completed")

        @pytest.mark.run(order=13)
        def test_013_Disassociate_zone_From_DTC_lbdn1(self):
                logging.info("Disassociate_zone_From_DTC_lbdn1")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:lbdn?name=lbdn_gateway_customer", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                data = {"lb_method":"ROUND_ROBIN","patterns": ["gateway.customer-service.intranet"], "pools": [{"pool":"dtc:pool/ZG5zLmlkbnNfcG9vbCRQb29sMQ:Pool1","ratio": 1}], "auth_zones":[],"types":["A","AAAA","CNAME","NAPTR","SRV"]}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                print("Restart DNS Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(30)
                logging.info("Test Case 13 Execution Completed")

        @pytest.mark.run(order=14)
        def test_014_Verify_Disassociate_zone_From_DTC_lbdn1(self):
                logging.info("Verify Disassociate_zone_From_DTC_lbdn1")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:lbdn?name=lbdn_gateway_customer", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=name,lb_method,patterns,auth_zones", grid_vip=config.grid_vip)
                print response
                if ('"name": "lbdn_gateway_customer"' in response) and ('"lb_method": "ROUND_ROBIN"' in response) and ('"auth_zones"' not in response):
                    assert True
                else:
                    assert False
                logging.info("Test Case 14 Execution Completed")

        @pytest.mark.run(order=15)
        def test_015_create_Cname_record(self):
                logging.info("Create Cname record")
                data={"canonical": "a.intranet","name": "gateway.customer-service.intranet","view": "default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:cname", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 15 Execution Completed")

        @pytest.mark.run(order=16)
        def test_016_Verify_Cname_record(self):
                logging.info("Verify Cname_record")
                response =  ib_NIOS.wapi_request('GET', object_type="record:cname", grid_vip=config.grid_vip)
                print response
                if ('"name": "gateway.customer-service.intranet"' in response) and ('"canonical": "a.intranet"' in response):
                    assert True
                else:
                    assert False
                logging.info("Test Case 16 Execution Completed")
 
        @pytest.mark.run(order=17)
        def test_017_create_A_record(self):
                logging.info("Create A record")
		log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                data={"ipv4addr": "10.1.1.1","name": "gateway.customer-service.intranet","view": "default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:a", fields=json.dumps(data))
                print response
		response=str(response)
		response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','').replace('\\','').replace("'",'')
                logging.info(response)
		print(response)
		if ('"text":"Therecordgateway.customer-service.intranetalreadyexists."' in response):
		    assert True
                else:
                    assert False
                sleep(30)
		log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 17 Execution Completed")

        @pytest.mark.run(order=18)
        def test_018_Verify_A_record(self):
                logging.info("Verify A record")
                response =  ib_NIOS.wapi_request('GET', object_type="record:a", grid_vip=config.grid_vip)
                print response
                if response=='[]':
                    assert True
                else:
                    assert False
                logging.info("Test Case 18 Execution Completed")


        @pytest.mark.run(order=19)
        def test_019_looking_for_Uniqueness_violation(self):
                logging.info("looking_for_Uniqueness violation")
                check=commands.getoutput(" grep -cw \".*Lost connection to grid master.\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.log.log")
                check1=commands.getoutput(" grep -cw \".*Uniqueness violation while inserting object.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.log.log")
                print(check,check1)
		if ((int(check)==0) and (int(check1)!=0)):
                    assert True
                else:
                    assert False
                sleep(2)
                print("Test Case 19 Execution Completed")

        @pytest.mark.run(order=20)
        def test_020_Verify_Member_status(self):
                logging.info("Verify Member Status")
                ref =  ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[1]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=node_info", grid_vip=config.grid_vip)
                print response
                if ('"description": "Running"' in response):
                    assert True
                else:
                    assert False
                logging.info("Test Case 20 Execution Completed")

	@pytest.mark.run(order=21)
        def test_021_perform_query_for_Master(self):
                logging.info("perform_query_for_DTC_record_for_Master ")
                dig_cmd = 'dig @'+str(config.grid_vip)+' gateway.customer-service.intranet'
                dig_cmd1 = os.system(dig_cmd)
		dig_result = subprocess.check_output(dig_cmd, shell=True)
                print dig_result
		if (config.Server1 in dig_result):
			assert True
		else:
                        assert False
                sleep(10)

	@pytest.mark.run(order=22)
        def test_022_perform_query_for_Member(self):
                logging.info("perform_query_for_DTC_record_for_Member ")
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' gateway.customer-service.intranet'
                dig_cmd1 = os.system(dig_cmd)
                dig_result = subprocess.check_output(dig_cmd, shell=True)
                print dig_result
                if (config.Server1 in dig_result):
                        assert True
                else:
                        assert False
                sleep(10)

        @pytest.mark.run(order=23)
        def test_023_Delete_LBDN2(self):
                logging.info("Delete Lbdn2")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:lbdn?name=lbdn_atendimento-gateway", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('DELETE', object_type=ref1, grid_vip=config.grid_vip)
                print response
                logging.info("Test Case 23 Execution Completed")

        pytest.mark.run(order=24)
        def test_024_Verify_Deleted_LBDN2(self):
                logging.info("Verify_Deleted Lbdn2")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:lbdn?name=lbdn_atendimento-gateway", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                print res
                if res==[]:
                    assert True
                else:
                    assert False
                logging.info("Test Case 24 Execution Completed")

        @pytest.mark.run(order=25)
        def test_025_Delete_LBDN1(self):
                logging.info("Delete Lbdn1")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:lbdn?name=lbdn_gateway_customer", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('DELETE', object_type=ref1, grid_vip=config.grid_vip)
                print response
                logging.info("Test Case 25 Execution Completed")

        @pytest.mark.run(order=26)
        def test_026_Verify_Deleted_LBDN(self):
                logging.info("Verify_Deleted Lbdn")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:lbdn?name=lbdn_gateway_customer", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                print res
                if res==[]:
                    assert True
                else:
                    assert False
                logging.info("Test Case 26 Execution Completed")

        @pytest.mark.run(order=27)
        def test_027_Delete_Pool(self):
                logging.info("Delete Pool")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:pool?name=Pool1", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('DELETE', object_type=ref1, grid_vip=config.grid_vip)
                print response
                logging.info("Test Case 27 Execution Completed")

        @pytest.mark.run(order=28)
        def test_028_Verify_Deleted_Pool(self):
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
                logging.info("Test Case 28 Execution Completed")


        @pytest.mark.run(order=29)
        def test_029_Delete_Server(self):
                logging.info("Delete Server")
                ref =  ib_NIOS.wapi_request('GET', object_type="dtc:server?name=server1", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('DELETE', object_type=ref1, grid_vip=config.grid_vip)
                print response
                logging.info("Test Case 29 Execution Completed")

        @pytest.mark.run(order=30)
        def test_030_Verify_Deleted_Server(self):
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
                logging.info("Test Case 30 Execution Completed")

        @pytest.mark.run(order=31)
        def test_031_Delete_Zone(self):
                logging.info("Delete Zone")
                ref =  ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=intranet", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                res = json.loads(ref)
                ref1 = json.loads(ref)[0]['_ref']
                print ref1
                response =  ib_NIOS.wapi_request('DELETE', object_type=ref1, grid_vip=config.grid_vip)
                print response
                logging.info("Test Case 31 Execution Completed")

        @pytest.mark.run(order=32)
        def test_032_Verify_Deleted_Zone(self):
                logging.info("Verify Deleted Zone")
                ref =  ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=intranet", grid_vip=config.grid_vip)
                print ref
                logging.info(ref)
                ref1 = json.loads(ref)
                print ref1
                if ref1==[]:
                    assert True
                else:
                    assert False
                logging.info("Test Case 32 Execution Completed")

	@pytest.mark.run(order=33)
        def test_033_Stop_DNS_Service(self):
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
                logging.info("Test Case 33 Execution Completed")

        @pytest.mark.run(order=34)
        def test_034_Validate_DNS_service_Disabled(self):
                logging.info("Validate DNs Service is Disabled")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                for i in res:
                        print i
                        logging.info("found")
                        assert i["enable_dns"] == False
                logging.info("Test Case 34 Execution Completed")
	

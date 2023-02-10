import re
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

class Network(unittest.TestCase):

        @pytest.mark.run(order=1)
        def test_01_Set_WAPI_Detailed(self):
                logging.info("Set_audit_logging_to_WAPI_DETAILED")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"audit_log_format":"WAPI_DETAILED"}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read = re.search(r'200',response)
                for read in response:
                        assert True
                logging.info("Test Case 1 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=2)
        def test_02_Validate_WAPI_detailed_set(self):
                logging.info("Validate audit log for WAPI Detailed")
                audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -4 /infoblox/var/audit.log | grep  \'audit_log_format\'"'
                out1 = commands.getoutput(audit_log_validation)
                print out1
                logging.info(out1)
                if re.search(r'Modified',out1) and re.search(r'WAPI_DETAILED',out1):
                        assert True
                else:
                        assert False
                logging.info("Test Case 2 Execution Completed")

        @pytest.mark.run(order=3)
        def test_03_Add_Authoritative_Zone(self):
                logging.info("Add Authoritative zone zone.com")
                data = {"fqdn": "zone.com"}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 3 Execution Completed")


        @pytest.mark.run(order=4)
        def test_04_Validate_audit_log_for_added_zone(self):
                logging.info("Validate WAPI Detailed audit log for zone added")
                audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -10 /infoblox/var/audit.log | grep  \'zone\.com\'"'
                out1 = commands.getoutput(audit_log_validation)
                print out1
                logging.info(out1)
                if re.search(r'Created\(POST\)',out1):
                        assert True
                else:
                        assert False
                logging.info("Test Case 4 Execution Completed")

        @pytest.mark.run(order=5)
        def test_05_modify_authoritative_zone(self):
                logging.info("Modify auth zone zone.com")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
                #import pdb; pdb.set_trace()
                res = json.loads(get_ref)
                #logging.info("RESPONSE")
                #logging.info(res)
                print res
                print get_ref
                for i in res:
                        if i["fqdn"]=="zone.com":
                                ref1=i['_ref']
                               # logging.info("reference of {} is {}".format(i["fqdn"], ref1))
                               # logging.info(ref1)

                data = {"comment":"Modified zone comment"}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read = re.search(r'200',response)
                for read in response:
                        assert True
                logging.info("Test Case 5 Execution Completed")

        @pytest.mark.run(order=6)
        def test_06_validate_audit_log_for_modified_zone(self):
                logging.info("Validate WAPI Detailed audit log for zone modified")
                audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -10 /infoblox/var/audit.log | grep  \'zone\.com\'"'
                out1 = commands.getoutput(audit_log_validation)
                print out1
                logging.info(out1)
                if re.search(r'Modified\(PUT\)',out1) and re.search(r'zone\.com',out1):
                        assert True
                else:
                        assert False
                logging.info("Test Case 6 Execution Completed")
				
				
        @pytest.mark.run(order=7)
        def test_07_Addauthoritative_IPv4_reverse_mapping_zone(self):
                logging.info("Add IPv4 reverse mapping zone")
                data = {"fqdn":"10.0.0.0/8","zone_format":"IPV4", "grid_primary": [{"name": config.grid_fqdn ,"stealth": False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 7 Execution Completed")


        @pytest.mark.run(order=8)
        def test_08_validate_audit_log_for_reverse_mapping_zone(self):
                logging.info("Validate WAPI Detailed audit log for reverse mapping zone added")
                audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -10 /infoblox/var/audit.log | grep  \'10\.in\-addr\.arpa\'"'
                out1 = commands.getoutput(audit_log_validation)
                print out1
                logging.info(out1)
                if re.search(r'Created\(POST\)',out1) and re.search(r'10\.in\-addr\.arpa',out1):
                        assert True
                else:
                        assert False
                logging.info("Test Case 8 Execution Completed")
				
        @pytest.mark.run(order=9)
        def test_09_modify_authoritative_reverse_mapping_zone(self):
                logging.info("Modify authoritative reverse mapping zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                print res
                print get_ref
                for i in res:
                        if i["fqdn"]=="10.0.0.0/8":
                                ref1=i['_ref']
                                #logging.info("reference of {} is {}".format(i["fqdn"], ref1))
                                #logging.info(ref1)

                data = {"comment":"Reverse mapping zone modified"}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read = re.search(r'200',response)
                for read in response:
                        assert True
                logging.info("Test Case 9 Execution Completed")


        @pytest.mark.run(order=10)
        def test_10_validate_audit_log_for_modified_reverse_mapping_zone(self):
                logging.info("Validate WAPI Detailed audit log for zone added")
                audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -10 /infoblox/var/audit.log | grep  \'10\.in\-addr\.arpa\'"'
                out1 = commands.getoutput(audit_log_validation)
                print out1
                logging.info(out1)
                if re.search(r'Modified\(PUT\)',out1) and re.search(r'10\.in\-addr\.arpa',out1):
                        assert True
                else:
                        assert False
                logging.info("Test Case 10 Execution Completed")
				
        @pytest.mark.run(order=11)
        def test_11_Add_a_Network(self):
                logging.info("Add a network")
                data = {"network": "10.0.0.0/8"}
                response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 11 Execution Completed")

        @pytest.mark.run(order=12)
        def test_12_validate_WAPI_detailed_audit_log_for_added_network(self):
                logging.info("Validate Audit log for Network WAPI Detailed log")
                audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -10 /infoblox/var/audit.log | grep  \'10\.0\.0\.0\/8\'"'
                out1 = commands.getoutput(audit_log_validation)
                print out1
                logging.info(out1)
                if re.search(r'Created\(POST\)',out1) and re.search(r'Network',out1):
                        assert True
                else:
                        assert False
                logging.info("Test Case 12 Execution Completed")
	    
		
	@pytest.mark.run(order=13)
        def test_13_modify_added_network(self):
                logging.info("validate WAPI_DETAILED log for modified network")
                get_ref = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
                #import pdb; pdb.set_trace()
                res = json.loads(get_ref)
                logging.info("RESPONSE")
                logging.info(res)
                print res
                print get_ref
                for i in res:
                        if i["network"]=="10.0.0.0/8":
                                ref1=i['_ref']
                                logging.info("reference of {} is {}".format(i["network"], ref1))
                                #logging.info(ref1)

                data = {"comment":"Network modified via WAPI"}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read = re.search(r'200',response)
                for read in response:
                        assert True
                logging.info("Test Case 13 Execution completed")

        @pytest.mark.run(order=14)
        def test_14_validate_audit_log_for_modified_network(self):
                logging.info("Validate WAPI Detailed audit log for network modified")
                audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -10 /infoblox/var/audit.log | grep  \'10\.0\.0\.0\/8\'"'
                out1 = commands.getoutput(audit_log_validation)
                print out1
                logging.info(out1)
                if re.search(r'Modified\(PUT\)',out1) and re.search(r'Network',out1):
                        assert True
                else:
                        assert False
                logging.info("Test Case 14 Execution Completed")

        @pytest.mark.run(order=15)
        def test_15_Add_Network_Range(self):
                logging.info("Add range inside Network")
                data = {"name":"range1","start_addr":"10.0.0.20","end_addr": "10.0.0.40","ddns_domainname":"anjan.com","disable": False,"comment":"DHCP range comment"}
                response = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 15 Execution Completed")

        @pytest.mark.run(order=16)
        def test_16_validate_WAPI_detailed_log_for_added_range(self):
                logging.info("Validate WAPI Detailed log for added range")
                audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -3 /infoblox/var/audit.log | grep  \'ReservedRange\'"'
                out1 = commands.getoutput(audit_log_validation)
                print out1
                logging.info(out1)
                if re.search(r'Created\(POST\)',out1) and re.search(r'10\.0\.0\.20\-10\.0\.0\.40',out1):
                        assert True
                else:
                        assert False
                logging.info("Test Case 16 Execution Completed")


        @pytest.mark.run(order=17)
        def test_17_modify_added_range(self):
                logging.info("Modify Added range")
                get_ref = ib_NIOS.wapi_request('GET', object_type="range")
                #import pdb; pdb.set_trace()
                res = json.loads(get_ref)
                #logging.info("RESPONSE")
                #logging.info(res)
                print res
                print get_ref
                for i in res:
                        if i["start_addr"]=="10.0.0.20":
                                ref1=i['_ref']
                                #logging.info("reference of {} is {}".format(i["network"], ref1))
                                #logging.info(ref1)

                data = {"comment":"Range comment modified via WAPI"}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                logging.info(response)
                read = re.search(r'200',response)
                for read in response:
                        assert True
                logging.info("Test Case 17 Execution completed")

	@pytest.mark.run(order=18)
        def test_18_validate_WAPI_detailed_log_for_modified_range(self):
                logging.info("Validate WAPI Detailed log for Modified range")
                audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -3 /infoblox/var/audit.log | grep  \'ReservedRange\'"'
                out1 = commands.getoutput(audit_log_validation)
                print out1
                logging.info(out1)
                if re.search(r'Modified\(PUT\)',out1) and re.search(r'Changed\ comment', out1):
                        assert True
                else:
                        assert False
                logging.info("Test Case 18 Execution Completed")

        @pytest.mark.run(order=19)
        def test_19_Add_A_record(self):
                logging.info("Add A record")
                data = {"name":"arec.zone.com","ipv4addr":"10.0.0.50","comment":"A record added"}
                response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 19 Execution Completed")



        @pytest.mark.run(order=20)
        def test_20_validate_added_A_record(self):
                logging.info("Validate WAPI Detailed audit log for added A record")
                audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -2 /infoblox/var/audit.log | grep  \'ARecord\'"'
                out1 = commands.getoutput(audit_log_validation)
                print out1
                logging.info(out1)
                if re.search(r'Created\(POST\)',out1) and re.search(r'arec\.zone\.com',out1):
                        assert True
                else:
                        assert False
                logging.info("Test Case 20 Execution Completed")

				
        @pytest.mark.run(order=21)
        def test_21_modify_A_record(self):
                logging.info("Modify A record")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:a")
                res = json.loads(get_ref)
                print res
                print get_ref
                for i in res:
                        if i["name"]=="arec.zone.com":
                                ref1=i['_ref']
                                #logging.info("reference of {} is {}".format(i["fqdn"], ref1))
                                #logging.info(ref1)

                data = {"comment":"A record comment modified"}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                logging.info(response)
                read = re.search(r'200',response)
                for read in response:
                        assert True
                logging.info("Test Case 21 Execution Completed")

        @pytest.mark.run(order=22)
        def test_22_validate_A_record_modified(self):
                logging.info("Validate WAPI Detailed audit log for AD server modified")
                audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -2 /infoblox/var/audit.log | grep  \'ARecord\'"'
                out1 = commands.getoutput(audit_log_validation)
                print out1
                logging.info(out1)
                if re.search(r'Modified\(PUT\)',out1) and re.search(r'Changed\ comment', out1):
                        assert True
                else:
                        assert False
                logging.info("Test Case 22 Execution Completed")


        @pytest.mark.run(order=23)
        def test_23_delete_A_record(self):
                logging.info("Delete A record")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:a")
                #import pdb; pdb.set_trace()
                res = json.loads(get_ref)
                logging.info(res)
                print res
                print get_ref
                for i in res:
                        if i["name"]=="arec.zone.com":
                                ref1=i['_ref']
                                #logging.info("reference of {} is {}".format(i["fqdn"], ref1))
                                #logging.info(ref1)

                response = ib_NIOS.wapi_request('DELETE',ref=ref1)
                logging.info(response)
                read = re.search(r'200',response)
                for read in response:
                        assert True
                logging.info("Test Case 23 Execution completed")

        @pytest.mark.run(order=24)
        def test_24_validate_audit_log_for_deleted_A_record(self):
                logging.info("Validate WAPI Detailed audit log for deleted AD server")
                audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -2 /infoblox/var/audit.log | grep  \'ARecord\'"'
                out1 = commands.getoutput(audit_log_validation)
                print out1
                logging.info(out1)
                if re.search(r'Deleted\(DELETE\)',out1):
                        assert True
                else:
                        assert False
                logging.info("Test Case 24 Execution Completed")

        @pytest.mark.run(order=25)
        def test_25_Add_New_Host_record(self):
                logging.info("Create A new Host record")
                data = { "ipv4addrs":[ {"ipv4addr" : "10.0.0.10","configure_for_dhcp" : False, "mac" : "aa:0:0:0:1:cc" }], "comment":"this is my one.perfusera comment","view":"default","name":"perfusera.zone.com"}
                response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info(" Test Case 25 Execution Completed")


        @pytest.mark.run(order=26)
        def test_26_validate_audit_log_for_added_Host(self):
                logging.info("Validate WAPI Detailed audit log for Host record")
                audit_log_validation1 = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -10 /infoblox/var/audit.log | grep  \'HostAddress\'"'
                out1 = commands.getoutput(audit_log_validation1)
                print out1
                logging.info(out1)
                if re.search(r'Created\(POST\)',out1):
                        assert True
                else:
                        assert False

                audit_log_validation2 = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -10 /infoblox/var/audit.log | grep  \'HostRecord\'"'
                out1 = commands.getoutput(audit_log_validation1)
                print out1
                logging.info(out1)
                if re.search(r'Created\(POST\)',out1):
                        assert True
                else:
                        assert False

                logging.info("Test Case 26 Execution Completed")
			
        @pytest.mark.run(order=27)
        def test_27_delete_range(self):
                logging.info("Delete range")
                get_ref = ib_NIOS.wapi_request('GET', object_type="range")
                #import pdb; pdb.set_trace()
                res = json.loads(get_ref)
                logging.info("RESPONSE")
                logging.info(res)
                print res
                print get_ref
                for i in res:
                        if i["start_addr"]=="10.0.0.20":
                                ref1=i['_ref']
                                #logging.info("reference of {} is {}".format(i["network"], ref1))
                                #logging.info(ref1)

                response = ib_NIOS.wapi_request('DELETE',ref=ref1, grid_vip=config.grid_vip)
                logging.info(response)
                read = re.search(r'200',response)
                for read in response:
                        assert True
                logging.info("Test Case 27 Execution Completed")

        @pytest.mark.run(order=28)
        def test_28_validate_audit_log_for_deleted_range(self):
                logging.info("Validate WAPI Detailed audit log for deleted range")
                audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -3 /infoblox/var/audit.log | grep  \'ReservedRange\'"'
                out1 = commands.getoutput(audit_log_validation)
                print out1
                logging.info(out1)
                if re.search(r'Deleted\(DELETE\)',out1):
                        assert True
                else:
                        assert False
                logging.info("Test Case 28 Execution Complete")


        @pytest.mark.run(order=29)
        def test_29_delete_authoritative_fwd_mapping_zone(self):
                logging.info("Delete Authoritative Forward mapping zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth")
                #import pdb; pdb.set_trace()
                res = json.loads(get_ref)
                logging.info("RESPONSE")
                logging.info(res)
                print res
                print get_ref
                for i in res:
                        if i["fqdn"]=="zone.com":
                                ref1=i['_ref']
                                #logging.info("reference of {} is {}".format(i["fqdn"], ref1))
                                #logging.info(ref1)

                response = ib_NIOS.wapi_request('DELETE',ref=ref1, grid_vip=config.grid_vip)
                logging.info(response)
                read = re.search(r'200',response)
                for read in response:
                        assert True
                logging.info("Test Case 29 Execution Completed")


        @pytest.mark.run(order=30)
        def test_30_validate_audit_log_for_deleted_zone(self):
                logging.info("Validate WAPI Detailed audit log for deleted zone")
                audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -10 /infoblox/var/audit.log | grep  \'zone\.com\'"'
                out1 = commands.getoutput(audit_log_validation)
                print out1
                logging.info(out1)
                if re.search(r'Deleted\(DELETE\)',out1):
                        assert True
                else:
                        assert False
                logging.info("Test Case 30 Execution Completed")


        @pytest.mark.run(order=31)
        def test_31_delete_network(self):
                logging.info("Delete added Network")
                get_ref = ib_NIOS.wapi_request('GET', object_type="network")
                #import pdb; pdb.set_trace()
                res = json.loads(get_ref)
                logging.info("RESPONSE")
                logging.info(res)
                print res
                print get_ref
                for i in res:
                        if i["network"]=="10.0.0.0/8":
                                ref1=i['_ref']
                                #logging.info("reference of {} is {}".format(i["network"], ref1))
                                #logging.info(ref1)

                response = ib_NIOS.wapi_request('DELETE',ref=ref1)
                logging.info(response)
                read = re.search(r'200',response)
                for read in response:
                        assert True
                logging.info("Test Case 31 Execution Completed")

        @pytest.mark.run(order=32)
        def test_32_validate_audit_log_for_deleted_network(self):
                logging.info("Validate WAPI Detailed audit log for deleted network")
                audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -10 /infoblox/var/audit.log | grep  \'10\.0\.0\.0\/8\'"'
                out1 = commands.getoutput(audit_log_validation)
                print out1
                logging.info(out1)
                if re.search(r'Deleted\(DELETE\)',out1):
                        assert True
                else:
                        assert False
                logging.info("Test Case 32 Execution Completed")


        @pytest.mark.run(order=33)
        def test_33_Start_traffic_capture(self):
                logging.info("Get member reference to start traffic capture")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Start Traffic Capture")
                data = {"action":"START","interface":"LAN1","seconds_to_run":60}
                response = ib_NIOS.wapi_request('POST', object_type = ref1 + "?_function=capture_traffic_control", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 33 Execution Completed")


        @pytest.mark.run(order=34)
        def test_34_validate_audit_log_for_Traffic_capture(self):
                logging.info("Validate WAPI Detailed audit log for Traffic capture started")
                audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -10 /infoblox/var/audit.log | grep  \'CaptureTrafficControl\'"'
                out1 = commands.getoutput(audit_log_validation)
                print out1
                logging.info(out1)
                if re.search(r'Called\(POST\)',out1) and re.search(r'CaptureTrafficControl',out1):
                        assert True
                else:
                        assert False
                logging.info("Test Case 34 Execution Completed")


        @pytest.mark.run(order=35)
        def test_35_stop_traffic_capture(self):
                logging.info("Get member reference to stop traffic capture")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Stop Traffic Capture")
                data = {"action":"STOP","interface":"LAN1","seconds_to_run":60}
                response = ib_NIOS.wapi_request('POST', object_type = ref1 + "?_function=capture_traffic_control", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 35 Execution Completed")

        @pytest.mark.run(order=36)
        def test_36_validate_audit_log_for_Traffic_capture(self):
                logging.info("Validate WAPI Detailed audit log for Traffic capture added")
                audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -10 /infoblox/var/audit.log | grep  \'CaptureTrafficControl\'"'
                out1 = commands.getoutput(audit_log_validation)
                print out1
                logging.info(out1)
                if re.search(r'Called\(POST\)',out1) and re.search(r'CaptureTrafficControl',out1):
                        assert True
                else:
                        assert False
                logging.info("Test Case 36 Execution Completed")

        @pytest.mark.run(order=37)
        def test_37_Add_AD_server(self):
                logging.info("Add an AD server")
                data = {"name":"AD_server","ad_domain":"anjan.localdomain","domain_controllers": [{"auth_port": 389,"disabled": False,"encryption": "NONE","fqdn_or_ip": "5.5.5.5","use_mgmt_port": False}]}
                response = ib_NIOS.wapi_request('POST', object_type="ad_auth_service", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 37 Execution Completed")



        @pytest.mark.run(order=38)
        def test_38_validate_AD_server_added(self):
                logging.info("Validate WAPI Detailed audit log for AD server added")
                audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -2 /infoblox/var/audit.log | grep  \'AdAuthService\'"'
                out1 = commands.getoutput(audit_log_validation)
                print out1
                logging.info(out1)
                if re.search(r'Created\(POST\)',out1):
                        assert True
                else:
                        assert False
                logging.info("Test Case 38 Execution Completed")



        @pytest.mark.run(order=39)
        def test_39_modify_AD_server(self):
                logging.info("Modify AD server")
                get_ref = ib_NIOS.wapi_request('GET', object_type="ad_auth_service", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                print res
                print get_ref
                for i in res:
                        if i["name"]=="AD_server":
                                ref1=i['_ref']
								#logging.info("reference of {} is {}".format(i["fqdn"], ref1))
                                #logging.info(ref1)

                data = {"comment":"AD server comment modified"}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                logging.info(response)
                read = re.search(r'200',response)
                for read in response:
                        assert True
                logging.info("Test Case 39 Execution Completed")

        @pytest.mark.run(order=40)
        def test_40_validate_AD_server_modified(self):
                logging.info("Validate WAPI Detailed audit log for AD server modified")
                audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -6 /infoblox/var/audit.log | grep  \'AdAuthService\'"'
                out1 = commands.getoutput(audit_log_validation)
                print out1
                logging.info(out1)
                if re.search(r'Modified\(PUT\)',out1) and re.search(r'Changed\ comment',out1):
                        assert True
                else:
                        assert False
                logging.info("Test Case 40 Execution Completed")

        @pytest.mark.run(order=41)
        def test_41_delete_AD_server(self):
                logging.info("Delete AD server")
                get_ref = ib_NIOS.wapi_request('GET', object_type="ad_auth_service")
                #import pdb; pdb.set_trace()
                res = json.loads(get_ref)
                logging.info(res)
                print res
                print get_ref
                for i in res:
                        if i["name"]=="AD_server":
                                ref1=i['_ref']
                                #logging.info("reference of {} is {}".format(i["fqdn"], ref1))
                                #logging.info(ref1)

                response = ib_NIOS.wapi_request('DELETE',ref=ref1)
                logging.info(response)
                read = re.search(r'200',response)
                for read in response:
                        assert True
                logging.info("Test Case 41 Execution Completed")

        @pytest.mark.run(order=42)
        def test_42_validate_audit_log_for_deleted_AD_server(self):
                logging.info("Validate WAPI Detailed audit log for deleted AD server")
                audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -10 /infoblox/var/audit.log | grep  \'AdAuthService\'"'
                out1 = commands.getoutput(audit_log_validation)
                print out1
                logging.info(out1)
                if re.search(r'Deleted\(DELETE\)',out1):
                        assert True
                else:
                        assert False
                logging.info("Test Case 42 Execution Completed")



        @pytest.mark.run(order=43)
        def test_43_Add_Admin_group(self):
                logging.info("Add Admin group")
                data = {"name":"group1","comment":"Added admin group via wapi","superuser":True,"email_addresses":["anjank@mail.com"]}
                response = ib_NIOS.wapi_request('POST', object_type="admingroup", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 43 Execution Completed")



        @pytest.mark.run(order=44)
        def test_44_validate_added_Admin_group(self):
                logging.info("Validate WAPI Detailed audit log for added Admin group")
                audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -2 /infoblox/var/audit.log | grep  \'AdminGroup\'"'
                out1 = commands.getoutput(audit_log_validation)
                print out1
                logging.info(out1)
                if re.search(r'Created\(POST\)',out1) and re.search(r'group1',out1):
                        assert True
                else:
                        assert False
                logging.info("Test Case 44 Execution Completed")

        @pytest.mark.run(order=45)
        def test_45_modify_Admin_group(self):
                logging.info("Modify Admin group")
                get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup")
                res = json.loads(get_ref)
                print res
                print get_ref
                for i in res:
                        if i["name"]=="group1":
                                ref1=i['_ref']
                                #logging.info("reference of {} is {}".format(i["fqdn"], ref1))
                                #logging.info(ref1)

                data = {"comment":"Admin group comment modified"}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                logging.info(response)
                read = re.search(r'200',response)
                for read in response:
                        assert True
                logging.info("Test Case 45 Execution Completed")

        @pytest.mark.run(order=46)
        def test_46_validate_modified_admin_group(self):
                logging.info("Validate WAPI Detailed audit log for modfied Admin group")
                audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -2 /infoblox/var/audit.log | grep  \'AdminGroup\'"'
                out1 = commands.getoutput(audit_log_validation)
                print out1
                logging.info(out1)
                if re.search(r'Modified\(PUT\)',out1) and re.search(r'Changed\ comment', out1):
                        assert True
                else:
                        assert False
                logging.info("Test Case 46 Execution Completed")

        @pytest.mark.run(order=47)
        def test_47_Add_Admin_user_with_group(self):
                logging.info("Add Admin group with newly added admin group")
                data = {"admin_groups":["group1"],"name":"user1","password":"infoblox", "auth_type":"LOCAL","comment":"Added admin user via WAPI"}
                response = ib_NIOS.wapi_request('POST', object_type="adminuser", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 47 Execution Completed")



        @pytest.mark.run(order=48)
        def test_48_validate_added_Admin_User(self):
                logging.info("Validate WAPI Detailed audit log for added Admin user")
                audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -2 /infoblox/var/audit.log | grep  \'AdminMember\'"'
                out1 = commands.getoutput(audit_log_validation)
                print out1
                logging.info(out1)
                if re.search(r'Created\(POST\)',out1) and re.search(r'user1',out1):
                        assert True
                else:
                        assert False
                logging.info("Test Case 48 Execution Completed")

				
        @pytest.mark.run(order=49)
        def test_49_modify_Admin_user(self):
                logging.info("Modified Admin User comment")
                get_ref = ib_NIOS.wapi_request('GET', object_type="adminuser")
                res = json.loads(get_ref)
                print res
                print get_ref
                for i in res:
                        if i["name"]=="user1":
                                ref1=i['_ref']
                                #logging.info("reference of {} is {}".format(i["fqdn"], ref1))
                                #logging.info(ref1)

                data = {"comment":"Admin user comment modified"}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                logging.info(response)
                read = re.search(r'200',response)
                for read in response:
                        assert True
                logging.info("Test Case 49 Execution Completed")

        @pytest.mark.run(order=50)
        def test_50_validate_modified_admin_user(self):
                logging.info("Validate WAPI Detailed audit log for modfied Admin user")
                audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -2 /infoblox/var/audit.log | grep  \'AdminMember\'"'
                out1 = commands.getoutput(audit_log_validation)
                print out1
                logging.info(out1)
                if re.search(r'Modified\(PUT\)',out1) and re.search(r'Changed\ comment', out1):
                        assert True
                else:
                        assert False
                logging.info("Test Case 50 Execution Completed")

        @pytest.mark.run(order=51)
        def test_51_delete_Admin_user(self):
                logging.info("Delete Admin user")
                get_ref = ib_NIOS.wapi_request('GET', object_type="adminuser")
                #import pdb; pdb.set_trace()
                res = json.loads(get_ref)
                logging.info(res)
                print res
                print get_ref
                for i in res:
                        if i["name"]=="user1":
                                ref1=i['_ref']
                                #logging.info("reference of {} is {}".format(i["fqdn"], ref1))
                                #logging.info(ref1)

                response = ib_NIOS.wapi_request('DELETE',ref=ref1)
                logging.info(response)
                read = re.search(r'200',response)
                for read in response:
                        assert True
                logging.info("Test Case 51 Execution Completed")

        @pytest.mark.run(order=52)
        def test_52_validate_audit_log_for_deleted_Admin_user(self):
                logging.info("Validate WAPI Detailed audit log for deleted Admin user")
                audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -2 /infoblox/var/audit.log | grep  \'AdminMember\'"'
                out1 = commands.getoutput(audit_log_validation)
                print out1
                logging.info(out1)
                if re.search(r'Deleted\(DELETE\)',out1):
                        assert True
                else:
                        assert False
                logging.info("Test Case 52 Execution Completed")

        @pytest.mark.run(order=53)
        def test_53_delete_Admin_group(self):
                logging.info("Delete Admin group")
                get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup")
                #import pdb; pdb.set_trace()
                res = json.loads(get_ref)
                logging.info(res)
                print res
                print get_ref
                for i in res:
                        if i["name"]=="group1":
                                ref1=i['_ref']
                                #logging.info("reference of {} is {}".format(i["fqdn"], ref1))
                                #logging.info(ref1)

                response = ib_NIOS.wapi_request('DELETE',ref=ref1)
                logging.info(response)
                read = re.search(r'200',response)
                for read in response:
                        assert True
                logging.info("Test Case 53 Execution Completed")

        @pytest.mark.run(order=54)
        def test_54_validate_audit_log_for_deleted_Admin_group(self):
                logging.info("Validate WAPI Detailed audit log for deleted Admin group")
                audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -2 /infoblox/var/audit.log | grep  \'AdminGroup\'"'
                out1 = commands.getoutput(audit_log_validation)
                print out1
                logging.info(out1)
                if re.search(r'Deleted\(DELETE\)',out1):
                        assert True
                else:
                        assert False
                logging.info("Test Case 54 Execution Completed")


        @pytest.mark.run(order=55)
        def test_55_Add_a_DTC_Server1(self):
                logging.info("Create A DTC Server")
                data = {"name":"s1","host":"10.120.20.151"}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 3 Execution Completed")
                sleep (10)


        @pytest.mark.run(order=56)
        def test_56_Validate_audit_log_for_added_DTC_srver1(self):
                logging.info("Validate WAPI Detailed audit log for added DTC server")
                audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -10 /infoblox/var/audit.log | grep  \'s1\'"'
                out1 = commands.getoutput(audit_log_validation)
                print out1
                logging.info(out1)
                if re.search(r'Created\(POST\)',out1) and re.search(r'IdnsServer',out1):
                        assert True
                else:
                        assert False
                logging.info("Test Case 4 Execution Completed")

        @pytest.mark.run(order=57)
        def test_57_modify_added_DTC_server(self):
                logging.info("Modify DTC server s1")
                get_ref = ib_NIOS.wapi_request('GET', object_type="dtc:server")
                res = json.loads(get_ref)
                for i in res:
                        if i["name"]=="s1":
                                ref1=i['_ref']

                data = {"comment":"Modified DTC server comment"}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                logging.info(response)
                read = re.search(r'200',response)
                for read in response:
                        assert True
                logging.info("Test Case 5 Execution Completed")
        @pytest.mark.run(order=58)
        def test_58_validate_modified_DTC_server_in_audit_log(self):
                logging.info("Validate WAPI Detailed audit log for DTC server modified")
                audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -10 /infoblox/var/audit.log | grep  \'s1\'"'
                out1 = commands.getoutput(audit_log_validation)
                print out1
                logging.info(out1)
                if re.search(r'Modified\(PUT\)',out1) and re.search(r's1',out1):
                        assert True
                else:
                        assert False
                logging.info("Test Case 6 Execution Completed")




        @pytest.mark.run(order=59)
        def test_59_delete_added_DTC_server(self):
                logging.info("Delete DTC server")
                get_ref = ib_NIOS.wapi_request('GET', object_type="dtc:server")
                res = json.loads(get_ref)
                logging.info(res)
                for i in res:
                        if i["name"]=="s1":
                                ref1=i['_ref']

                response = ib_NIOS.wapi_request('DELETE',ref=ref1)
                logging.info(response)
                read = re.search(r'200',response)
                for read in response:
                        assert True
                logging.info("Test Case 29 Execution Completed")

        @pytest.mark.run(order=60)
        def test_60_validate_audit_log_for_deleted_DTC_server(self):
                logging.info("Validate WAPI Detailed audit log for deleted DTC server")
                audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -4 /infoblox/var/audit.log | grep  \'s1\'"'
                out1 = commands.getoutput(audit_log_validation)
                print out1
                logging.info(out1)
                if re.search(r'Deleted\(DELETE\)',out1):
                        assert True
                else:
                        assert False
                logging.info("Test Case 30 Execution Completed")



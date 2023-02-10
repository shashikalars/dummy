__author__ = "Shekhar Srivastava"
__email__  = "ssrivastava@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Grid Master + 2 Grid Member                                           #
#  2. Licenses : Grid, NIOS (IB-815),DNS,RPZ                                #
#  3. GM + 2 Members should have MGMT IPv4 and IPv6 config                  #                     #
#############################################################################



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
import getpass
import sys
import csv

def get_ref_member():
    get_ref = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
    logging.info(get_ref)
    res = json.loads(get_ref)
    ref1 = json.loads(get_ref)[2]['_ref']
    return ref1

def get_dnsref_member2():
    get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
    logging.info(get_ref)
    res = json.loads(get_ref)
    ref1 = json.loads(get_ref)[2]['_ref']
    return ref1


def get_dnsref_member1():
    get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
    logging.info(get_ref)
    res = json.loads(get_ref)
    ref1 = json.loads(get_ref)[1]['_ref']
    return ref1

def get_dnsref_master():
    get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
    logging.info(get_ref)
    res = json.loads(get_ref)
    ref1 = json.loads(get_ref)[0]['_ref']
    return ref1




class Network(unittest.TestCase):


	@pytest.mark.run(order=1)
        def test_1_enable_recursion(self):
                logging.info("allow recursive query")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                logging.info("Modify Grid DNS Properties")
                data = {"allow_recursive_query": True}
                response = ib_NIOS.wapi_request('PUT',ref= ref1,fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 1 Execution Completed")

        @pytest.mark.run(order=2)
        def test_2_Create_Auth_zone(self):
                logging.info("Creating Auth Zone")
                data={"fqdn":"abc.com","view":"default","grid_primary":[{"name": config.grid_fqdn,"stealth": False}],"grid_secondaries": [{"name": config.grid_member1_fqdn,"stealth": False,"grid_replicate": True,"enable_preferred_primaries": False,"preferred_primaries": []}]}
                zone_ref=ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data))
                logging.info(zone_ref)
                if bool(re.match("\"zone_auth*.",str(zone_ref))):
                    logging.info("abc.com created succesfully")
                    logging.info("Restart services")
                    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                    ref = json.loads(grid)[0]['_ref']
                    publish={"member_order":"SIMULTANEOUSLY"}
                    request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                    sleep(5)
                    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                    sleep(5)

                else:
                    raise Exception("abc.com creation unsuccessful")



        @pytest.mark.run(order=3)
        def test_3_Create_RPZ_Zone(self):
		logging.info("Create Local RPZ Zone")
                grid_member=config.grid_fqdn
                data = {"fqdn":"rpz.com","rpz_type": "LOCAL","grid_primary": [{"name":config.grid_fqdn}],"rpz_severity": "MAJOR","rpz_type": "LOCAL","grid_secondaries": [{"enable_preferred_primaries": False,"grid_replicate": False,"lead": False,"name":config.grid_member_fqdn},{"enable_preferred_primaries": False,"grid_replicate": False,"lead": False,"name":config.grid_member1_fqdn}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_rp", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 3 Execution Completed")

                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
		restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")
                sleep(30)
	

	@pytest.mark.run(order=4)
        def test_4_delete_mgmt_IPv4_network_conf_from_one_member(self):
                logging.info("Delete mgmt IPv4 conf from one member")
		ref = get_ref_member()
		data = {"node_info":[{"v6_mgmt_network_setting":{"auto_router_config_enabled": False,"cidr_prefix": 64,"enabled": True,"gateway": "2620:10a:6000:2500::1","virtual_ip":config.grid_member2_vip6 }}]}
		response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data),grid_vip=config.grid_vip)
		res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 4 Execution Completed")

		

	@pytest.mark.run(order=5)
        def test_5_enable_mgmt_IPv6_DNS_service(self):
                logging.info("Enable mgmt IPv6")
                ref = get_dnsref_member2()
                data = {"use_mgmt_ipv6_port": True,"enable_dns": True}
                response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data),grid_vip=config.grid_vip)
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 5 Execution Completed")



	@pytest.mark.run(order=6)
        def test_6_enable_mgmt_IPv4_and_IPv6_DNS_service(self):
                logging.info("Enable dns on IPv4 and IPv6  mgmt ")
                ref = get_dnsref_member1()
                data = {"use_mgmt_ipv6_port": True,"use_mgmt_port": True,"enable_dns": True}
                response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data),grid_vip=config.grid_vip)
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 6 Execution Completed")


	@pytest.mark.run(order=7)
        def test_7_enable_mgmt_IPv4_and_IPv6_DNS_service_on_Master(self):
                logging.info("Enable dns on IPv4 and IPv6  mgmt ")
                ref = get_dnsref_master()
                data = {"use_mgmt_ipv6_port": True,"use_mgmt_port": True,"enable_dns": True}
                response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data),grid_vip=config.grid_vip)
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 7 Execution Completed")



	
	@pytest.mark.run(order=8)
        def test_8_change_DNS_notify_to_MGMT_interface_to_member1(self):
                logging.info("Enable send notifies from the mgmt interface")
                ref = get_dnsref_member2()
                data = {"dns_notify_transfer_source":"MGMT"}
                response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data),grid_vip=config.grid_vip)
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 8 Execution Completed")



        @pytest.mark.run(order=9)
        def test_9_change_DNS_notify_to_MGMT_interface_to_member2(self):
                logging.info("Enable send notifies from the mgmt interface ")
                ref = get_dnsref_member1()
                data = {"dns_notify_transfer_source":"MGMT"}
                response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data),grid_vip=config.grid_vip)
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 9 Execution Completed")

		logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")
                sleep(30)


	@pytest.mark.run(order=010)
        def test_010_named_conf_Grid_Master_for_notify_IPv6_IP(self):
                logging.info("Validate named conf on Grid Master")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " cat /infoblox/var/named_conf/named.conf | grep  \'also-notify.*10.36.*2620:10a:6000:2500\'"'
                out1 = commands.getoutput(sys_log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'also-notify.*10.36.*2620:10a:6000:2500',out1)
                logging.info("Test Case 10 Execution Completed")


	@pytest.mark.run(order=011)
        def test_011_named_conf_Grid_Master_for_allow_transfer_IPv6_IP(self):
                logging.info("Validate named conf on Grid Master")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " cat /infoblox/var/named_conf/named.conf | grep  \'allow-transfer.*10.36.*2620:10a:6000:2500\'"'
                out1 = commands.getoutput(sys_log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'allow-transfer.*10.36.*2620:10a:6000:2500',out1)
                logging.info("Test Case 11 Execution Completed")


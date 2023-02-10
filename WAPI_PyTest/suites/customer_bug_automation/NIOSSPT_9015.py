__author__ = "Ashwini C M"
__email__  = "cma@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master                                                                      #
#  2. Licenses : DNS, DHCP, Grid, NIOS(IB-V1415)                                                 
########################################################################################
import re
import config
import paramiko
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
#import requests
import time
import pexpect
import sys
#import ipaddress

class Network(unittest.TestCase):

            @pytest.mark.run(order=1)
            def test_01_start_IPv4_DHCP_service(self):
                logging.info("start the ipv4 service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"enable_dhcp":True,}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                read  = re.search(r'201',response)
                for read in  response:
                    assert True
                    print("DHCP service is enabled")
                    print("Test Case 1 Execution Completed")
                    break
                else:
                    assert False

            @pytest.mark.run(order=2)
            def test_02_start_IPv4_DNS_service(self):
                logging.info("start the ipv4 DNS service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print (ref1)
                data = {"enable_dns": True}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                sleep(20)
                logging.info(response)
                print (response)
                read  = re.search(r'201',response)
                for read in  response:
                    assert True
                    print("DNS service is enabled")
                    print("Test Case 2 Execution Completed")
                    break
                else:
                    assert False
            
            @pytest.mark.run(order=3)
            def test_03_restart_service(self):
            	logging.info("Restart services")
            	grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            	ref = json.loads(grid)[0]['_ref']
            	publish={"member_order":"SIMULTANEOUSLY"}
            	request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            	request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            	restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                read  = re.search(r'201',restart)
                for read in restart:
                    assert True
                    print("System Restart is done successfully")
                    sleep(30)
                    break
                else:
                    assert False

            @pytest.mark.run(order=4)
            def test_04_create_IPv4_network(self):
                logging.info("Create an ipv4 network default network view")
                data = {"network": "10.0.0.0/8","network_view": "default","members":[{"_struct": "dhcpmember","ipv4addr":config.grid_vip}]}
                response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        assert False
                print("Created the ipv4network 10.0.0.0/8 in default view")
                logging.info("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 4 Execution Completed")

            @pytest.mark.run(order=5)
            def test_05_create_IPv4_Range(self):
                logging.info("Create an IPv4 range in defaultnetwork view")
                client_ip=config.client_ip
                print client_ip
		end_ip=client_ip.split('.')
		end_ip[3]=str(int(end_ip[3])+10)
		end_ip='.'.join(end_ip)
                data = {"network":"10.0.0.0/8","start_addr":config.client_ip,"end_addr":end_ip,"network_view": "default","member":{"_struct":"dhcpmember"}}
                response = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(data), grid_vip=config.grid_vip)
                print (response)
                #read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Created the ipv4 prefix range with bits 8  in default view")
                logging.info("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 20 sec.,")
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 5 Execution Completed")
                
            @pytest.mark.run(order=6)
            def test_06_requesting_ipv4_lease_using_dras(self):
                logging.info("Perform dras command")
                dras_cmd = 'sudo /import/tools/qa/tools/dras/dras -i '+str(config.grid_vip)+' '+' -x l=10.0.0.0 -n 10'
                dras_cmd1 = os.system(dras_cmd)
                print (dras_cmd1)
                sleep(10)
                grid =  ib_NIOS.wapi_request('GET', object_type="lease",grid_vip=config.grid_vip)
                print(grid)
                grid_json=json.loads(grid)
                ref=grid_json[-1]["_ref"]
                print(ref)
                logging.info("get option for ip")
                response = ib_NIOS.wapi_request('GET',object_type=ref+"?_return_fields=option",grid_vip=config.grid_vip)
                print(response)
                lease_ip=config.client_ip
		print(lease_ip)
           #     print lease_ip
		read  = re.search(r'201',response)
                for read in  response:
                    assert True
                    print("DHCP service is enabled")
                    print("Test Case 6 Execution Completed")
                    break
                else:
                    assert False

                sleep(20)
                print("Test Case 6 Execution Completed")
            
            
            @pytest.mark.run(order=7)
            def test_07_issue_cli_commands(self):
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect ('password.*:')
                child.sendline ('infoblox')
                child.expect ('Infoblox >')
                child.sendline ('delete leases state ABANDONED')
                child.expect ('.*Are you.*')
                child.sendline ('y')
                child.expect ('Infoblox >')
                child.sendline ('exit')
                lease1 = child.before
                print lease1
                deleted_lease1 = re.search('(\d+)',lease1)
                print deleted_lease1
                if int(deleted_lease1.group()) == 0:
                    assert False
                else:
                    assert True
                print ("The abandoned leases have been deleted successfully")
                child.close

            @pytest.mark.run(order=7)
            def test_08_validate_audit_logs(self):
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
		mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
		client.connect(config.grid_vip, username='root', pkey = mykey)
		data='grep -0 "Called - delete leases. Args: state ABANDONED" /infoblox/var/audit.log | wc -l'
		stdin, stdout, stderr = client.exec_command(data)
		stdout=stdout.read()
		print("output ",stdout)
		if int(stdout) == 0:
			assert False
		else:
			assert True
		print ("Log validation done")
		client.close()
		    

            
                
            
                
         

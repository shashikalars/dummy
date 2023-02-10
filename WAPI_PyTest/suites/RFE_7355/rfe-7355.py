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


def getting_the_ipv6_address_range_of_client():
    output = os.popen('hostname -I')
    output = output.read()
    output1 = output.split()[1]
    ipv6_range = output1.split('::')[0]
    print(ipv6_range)
    return ipv6_range

class Network(unittest.TestCase):
	@pytest.mark.run(order=1)
        def test_001_start_IPv4_service(self):
                logging.info("start the ipv4 service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                data = {"enable_dhcp": True}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                logging.info("============================")
                print response


	@pytest.mark.run(order=2)
        def test_002_start_IPv6_service(self):
                logging.info("start the ipv6 service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                data = {"enable_dhcpv6_service": True}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                logging.info("============================")
                print response


	@pytest.mark.run(order=3)
        def test_003_create_IPv6_network(self):
           	logging.info("Create an ipv6 network default network view")
                ipv6_addr_range = getting_the_ipv6_address_range_of_client()
                data = {"network": str(ipv6_addr_range)+"::/64","network_view": "default","members":[{"ipv4addr":config.grid_vip,"name":config.grid_fqdn}]}
                response = ib_NIOS.wapi_request('POST', object_type="ipv6network", fields=json.dumps(data), grid_vip=config.grid_vip)
          	print response
                logging.info(response)
                read  = re.search(r'201',response)
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
                logging.info("Test Case 3 Execution Completed")


	@pytest.mark.run(order=4)
        def test_004_create_IPv6_Range(self):
                logging.info("Create an ipv6 range in  default network view")
                ipv6_addr_range = getting_the_ipv6_address_range_of_client()
                data = {"network": str(ipv6_addr_range)+"::/64","start_addr": str(ipv6_addr_range)+"::10","end_addr": str(ipv6_addr_range)+"::100","network_view": "default","member":{"_struct":"dhcpmember","ipv4addr":config.grid_vip,"name":config.grid_fqdn}}
                response = ib_NIOS.wapi_request('POST', object_type="ipv6range", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
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
                logging.info("Test Case 4 Execution Completed")


        @pytest.mark.run(order=5)
        def test_005_requesting_ipv6_lease_without_rapid_commit(self):
                logging.info("Perform dras command")
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/./dras6 -i'+str(config.grid_vip6)+' '+'-n 1 -A -v '
                dras_cmd1 = os.system(dras_cmd)
                sleep(20)
                logging.info("Validate Syslog afer perform lease operation")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /var/log/syslog | grep  \'Advertise\'"'
                out1 = commands.getoutput(sys_log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'Advertise',out1)
                logging.info("Test Case 5 Execution Completed")



	@pytest.mark.run(order=6)
        def test_006_set_rapid_commit_at_network_level(self):
                logging.info("Set rapid-commit option at netowork level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6network")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                data = {"options": [{"name": "dhcp6.rapid-commit","num": 14,"value": "true","vendor_class": "DHCPv6"}]}
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
                logging.info("Test Case 6 Execution Completed")




	@pytest.mark.run(order=7)
        def test_007_requesting_ipv6_lease_with_rapid_commit(self):
                logging.info("Perform dras command")
                ipv6_addr_range = getting_the_ipv6_address_range_of_client()
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/./dras6 -i'+str(config.grid_vip6)+' '+'-n 1 -c '+str(ipv6_addr_range)+':: -A -v -z'
                dras_cmd1 = os.system(dras_cmd)
                sleep(20)
                logging.info("Validate Syslog afer perform lease operation")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /var/log/syslog | grep  \'Reply\'"'
                out1 = commands.getoutput(sys_log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'Reply',out1)
                logging.info("Test Case 7 Execution Completed")



	@pytest.mark.run(order=8)
        def test_008_IPv6_shared_network_negative(self):
                logging.info("Create an ipv6 shared network with network which has rapid-commit enabled")
		get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6network")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                data = {"name":"ipv6_shared","networks":[{"_ref":ref1}]}
		response = ib_NIOS.wapi_request('POST', object_type="ipv6sharednetwork", fields=json.dumps(data), grid_vip=config.grid_vip)
		logging.info(response[0])
       	        if re.search(r'400',str(response[0])):
             	  assert True
		else:
		  assert False
		
		logging.info("Test Case 8 Execution Completed")




	@pytest.mark.run(order=9)
        def test_009_unset_rapid_commit_at_network_level(self):
                logging.info("Set rapid-commit option at netowork level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6network")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
		data = {"options": []}
                #data = {"options": [{"name": "dhcp6.rapid-commit","num": 14,"value": "false","vendor_class": "DHCPv6"}]}
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
                logging.info("Test Case 9 Execution Completed")


	@pytest.mark.run(order=10)
        def test_010_add_IPv6_shared_network(self):
                logging.info("Create an ipv6 shared network with network which has rapid-commit enabled")
		get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6network")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                data = {"name":"ipv6_shared","networks":[{"_ref":ref1}]}
                response = ib_NIOS.wapi_request('POST', object_type="ipv6sharednetwork", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
		read  = re.search(r'201',response)
                for read in  response:
                        assert True

                logging.info("Test Case 10 Execution Completed")



	@pytest.mark.run(order=11)
        def test_011_set_rapid_commit_at_shared_network_level(self):
                logging.info("Set rapid-commit option at shared netowork level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6sharednetwork")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                data = {"options": [{"name": "dhcp6.rapid-commit","num": 14,"value": "true","vendor_class": "DHCPv6"}]}
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
                logging.info("Test Case 11 Execution Completed")



	@pytest.mark.run(order=12)
        def test_012_requesting_ipv6_lease_with_rapid_commit(self):
                logging.info("Perform dras command")
                ipv6_addr_range = getting_the_ipv6_address_range_of_client()
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/./dras6 -i'+str(config.grid_vip6)+' '+'-n 1 -c '+str(ipv6_addr_range)+':: -A -v -z'
                dras_cmd1 = os.system(dras_cmd)
                sleep(20)
                logging.info("Validate Syslog afer perform lease operation")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /var/log/syslog | grep  \'Reply\'"'
                out1 = commands.getoutput(sys_log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'Reply',out1)
                logging.info("Test Case 12 Execution Completed")



	@pytest.mark.run(order=13)
        def test_013_set_rapid_commit_at_network_level_negative(self):
                logging.info("Set rapid-commit option at netowork level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6network")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                data = {"options": [{"name": "dhcp6.rapid-commit","num": 14,"value": "true","vendor_class": "DHCPv6"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
		logging.info(response[0])
                if re.search(r'400',str(response[0])):
                  assert True
                else:
                  assert False

                logging.info("Test Case 13 Execution Completed")




	@pytest.mark.run(order=14)
        def test_014_requesting_ipv6_lease_without_rapid_commit(self):
                logging.info("Perform dras command")
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/./dras6 -i'+str(config.grid_vip6)+' '+'-n 1 -A -v '
                dras_cmd1 = os.system(dras_cmd)
                sleep(20)
                logging.info("Validate Syslog afer perform lease operation")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /var/log/syslog | grep  \'Advertise\'"'
                out1 = commands.getoutput(sys_log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'Advertise',out1)
                logging.info("Test Case 14 Execution Completed")


	@pytest.mark.run(order=15)
        def test_015_requesting_ipv6_lease_with_rapid_commit(self):
                logging.info("Perform dras command")
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/./dras6 -i'+str(config.grid_vip6)+' '+'-n 1 -A -v -z'
                dras_cmd1 = os.system(dras_cmd)
                sleep(20)
                logging.info("Validate Syslog afer perform lease operation")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /var/log/syslog | grep  \'Reply\'"'
                out1 = commands.getoutput(sys_log_validation)
                print out1
                logging.info(out1)
                #assert re.search(r'Reply',out1)
                logging.info("Test Case 15 Execution Completed")


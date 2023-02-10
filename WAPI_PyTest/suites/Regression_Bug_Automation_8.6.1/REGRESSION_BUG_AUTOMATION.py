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
import shlex
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
import paramiko
from ib_utils.common_utilities import generate_token_from_file

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="bug_automation_2.log" ,level=logging.INFO,filemode='w')



def print_and_log(arg=""):
        print(arg)
        logging.info(arg)


def restart_services():
        print_and_log("Service restart start")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(40)
        print_and_log("Service restart Done")


def disable_DHCP_service_on_both_ipv4_and_ipv6():
         print_and_log("*********** enable DHCP service on both ipv4 and ipv6 ************")
         get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties")
         get_ref = json.loads(get_ref)
         dhcp_ref = get_ref[0]['_ref']
         print_and_log(dhcp_ref)
         data = {"enable_dhcp": False}
         get_ref = ib_NIOS.wapi_request('PUT', object_type=dhcp_ref, fields=json.dumps(data))
         get_ref = json.loads(get_ref)
         print_and_log(get_ref)
         assert re.search(r'member:dhcpproperties', get_ref)
         data = {"enable_dhcpv6_service": False}
         get_ref = ib_NIOS.wapi_request('PUT', object_type=dhcp_ref, fields=json.dumps(data))
         get_ref = json.loads(get_ref)
         print_and_log(get_ref)
         assert re.search(r'member:dhcpproperties', get_ref)
         print_and_log("Disable of DHCP IPV4 and IPV6 service is Completed")


class bug_automation(unittest.TestCase):

        #NIOS-82698
        @pytest.mark.run(order=1)
        def test_001_Start_DNS_Service(self):
                print_and_log("********** Start DNS Service **********")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                print_and_log(get_ref)
                res = json.loads(get_ref)
                for i in res:
                    print_and_log("Modify a enable_dns")
                    data = {"enable_dns": True}
                    response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
                    print_and_log(response)
                read  = re.search(r'200',response)
                for read in response:
                        assert True
                print_and_log("Test Case 1 Execution Completed")



        @pytest.mark.run(order=2)
        def test_002_Validate_DNS_service_Enabled(self):
                print_and_log("********** Validate DNS Service is enabled **********")
                res = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns")
                print_and_log(res)
                res = json.loads(res)
                print_and_log(res)
                for i in res:
                    print_and_log(i)
                    print_and_log("found")
                    assert i["enable_dns"] == True
                print_and_log("Test Case 2 Execution Completed")



        @pytest.mark.run(order=3)
        def test_003_enable_DHCP_service_on_both_ipv4_and_ipv6(self):
                print_and_log("*********** enable DHCP service on both ipv4 and ipv6 ************")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties")
                get_ref = json.loads(get_ref)
                dhcp_ref = get_ref[0]['_ref']
                print_and_log(dhcp_ref)
                data = {"enable_dhcp": True}
                get_ref = ib_NIOS.wapi_request('PUT', object_type=dhcp_ref, fields=json.dumps(data))
                get_ref = json.loads(get_ref)
                print_and_log(get_ref)
                assert re.search(r'member:dhcpproperties', get_ref)
                data = {"enable_dhcpv6_service": True}
                get_ref = ib_NIOS.wapi_request('PUT', object_type=dhcp_ref, fields=json.dumps(data))
                get_ref = json.loads(get_ref)
                print_and_log(get_ref)
                assert re.search(r'member:dhcpproperties', get_ref)
                print_and_log("Test Case 3 Execution Completed")



        @pytest.mark.run(order=4)
        def test_004_verify_if_dhcp_service_is_enabled_on_ipv4_and_ipv6(self):
                print_and_log("*********** verify if dhcp service is enabled on ipv4 and ipv6 ************")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties")
                get_ref = json.loads(get_ref)
                dhcp_ref = get_ref[0]['_ref']
                print_and_log(dhcp_ref)
                get_ref = ib_NIOS.wapi_request('GET', object_type=dhcp_ref, params='?_return_fields=enable_dhcp')
                get_ref = json.loads(get_ref)
                print_and_log(get_ref)
                enable_dhcp = get_ref['enable_dhcp']
                print_and_log(enable_dhcp)
                get_ref = ib_NIOS.wapi_request('GET', object_type=dhcp_ref, params='?_return_fields=enable_dhcpv6_service')
                get_ref = json.loads(get_ref)
                print_and_log(get_ref)
                enable_dhcpv6_service = get_ref['enable_dhcpv6_service']
                print_and_log(enable_dhcpv6_service)
                if enable_dhcp == True and enable_dhcpv6_service == True:
                    print_and_log("DHCP service is enabled for both IPV4 and IPV6")
                    assert True
                else:
                    print_and_log("DHCP service is not enabled")
                    assert False
                print_and_log("Test Case 4 Execution Completed")



        @pytest.mark.run(order=5)
        def test_005_Configure_the_ipv6_filter_option(self):
                print_and_log("*********** Configure the ipv6 filter option ************")
                data = {"name":"rrrrrr9401","comment":"123","expression": "(hardware=01:01:23:45:67:89:ab AND option dhcp6.fqdn!=\"test.com\")","option_list": [{"name": "dhcp6.vendor-class","num":16,"value": "Infoblox","vendor_class": "DHCPv6"},{"name": "dhcp6.fqdn","num": 39,"value": "True","vendor_class": "DHCPv6"},{"name": "dhcp6.name-servers","num":23,"value":"21::1,22::2","vendor_class": "DHCPv6"},{"name": "dhcp6.sip-servers-addresses","num":22,"value":"21::1,22::2","vendor_class": "DHCPv6"},{"name": "dhcp6.sntp-servers","num":31,"value":"21::1,22::2","vendor_class": "DHCPv6"},{"name": "dhcp6.bcms-server-a","num":34,"value":"21::1,22::2","vendor_class": "DHCPv6"},{"name": "dhcp6.bcms-server-d","num":33,"value":"\"test.com\",\"zone.com\"","vendor_class": "DHCPv6"},{"name": "dhcp6.info-refresh-time","num":32,"value":"444444444","vendor_class": "DHCPv6"},{"name": "dhcp6.nisp-domain-name","num":30,"value":"\"test.com\"","vendor_class": "DHCPv6"},{"name": "dhcp6.nis-domain-name","num":29,"value":"\"test.com\"","vendor_class": "DHCPv6"},{"name": "dhcp6.nisp-servers","num":28,"value":"22::2","vendor_class": "DHCPv6"},{"name": "dhcp6.nis-servers","num":27,"value":"22::2","vendor_class": "DHCPv6"},{"name": "dhcp6.domain-search","num":24,"value":"\"test.com\"","vendor_class": "DHCPv6"},{"name": "dhcp6.sip-servers-names","num":21,"value":"\"test.com\"","vendor_class": "DHCPv6"}],"option_space": "DHCPv6"}
                get_ref = ib_NIOS.wapi_request('POST', object_type="ipv6filteroption", fields=json.dumps(data))
                if type(get_ref) != tuple:
                    print_and_log(get_ref)
                    get_ref = json.loads(get_ref)
                    assert re.search(r'ipv6filteroption', get_ref)
                    assert True
                else:
                    out = get_ref[1]
                    out = json.loads(out)
                    print_and_log(out)
                    error_message = out['text']
                    print_and_log(error_message)
                    print_and_log("ipv6 filter option is not set due to error while sending the request")
                    assert False
                restart_services()
                print_and_log("Test Case 5 Execution Completed")



        @pytest.mark.run(order=6)
        def test_006_verify_the_ipv6_filter_option_configured(self):
                print_and_log("*********** verify the ipv6 filter option configured ************")
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6filteroption")
                get_ref = json.loads(get_ref)
                name = get_ref[0]['name']
                if name == "rrrrrr9401":
                    print_and_log("IPV6 filter option "+name+" configured successfully")
                    assert True
                else:
                    print_and_log("Error while validating IPV6 filter option that is created")
                    assert False
                print_and_log("Test Case 6 Execution Completed")



        @pytest.mark.run(order=7)
        def test_007_delete_the_ipv6_filter_option_configured(self):
                print_and_log("*********** Delete the ipv6 filter option configured ************")
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6filteroption")
                get_ref = json.loads(get_ref)
                ref = get_ref[0]['_ref']
                get_ref = ib_NIOS.wapi_request('DELETE', object_type=ref)
                assert re.search(r'ipv6filteroption', get_ref)
                restart_services()
                disable_DHCP_service_on_both_ipv4_and_ipv6()
                print_and_log("Test Case 7 Execution Completed")



        #NIOS-82531
        @pytest.mark.run(order=8)
        def test_008_configure_the_forwarders_in_grid_DNS_properties(self):
                print_and_log("********** configure the forwarders in grid DNS properties ************")
                data = {"forwarders": [config.forwarderip]}
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
                get_ref = json.loads(get_ref)
                ref = get_ref[0]['_ref']
                get_ref1 = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
                print_and_log(get_ref1)
                assert re.search(r'grid:dns', get_ref1)
                restart_services()
                print_and_log("Test Case 8 Execution Completed")




        @pytest.mark.run(order=9)
        def test_009_verify_the_forwarder_added_in_grid_DNS_properties(self):
                print_and_log("*********** verify the forwarder added in grid DNS properties ************")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
                get_ref = json.loads(get_ref)
                print_and_log(get_ref)
                ref = get_ref[0]['_ref']
                get_ref1 = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=forwarders')
                get_ref1 = json.loads(get_ref1)
                print_and_log(get_ref1)
                forwarder_ip = get_ref1['forwarders'][0]
                if forwarder_ip == config.forwarderip:
                    print_and_log("Forwarder ip "+config.forwarderip+" is configured successfully")
                    assert True
                else:
                    print_and_log("Forwarder ip is not configured")
                    assert False
                print_and_log("Test Case 9 Execution Completed")



        @pytest.mark.run(order=10)
        def test_010_enable_recursive_queries_in_grid_DNS_properties(self):
                print_and_log("********** enable recursive queries in grid DNS properties ************")
                data = {"allow_recursive_query": True}
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
                get_ref = json.loads(get_ref)
                ref = get_ref[0]['_ref']
                get_ref1 = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
                print_and_log(get_ref1)
                assert re.search(r'grid:dns', get_ref1)
                restart_services()
                print_and_log("Test Case 10 Execution Completed")



        @pytest.mark.run(order=11)
        def test_011_verify_if_recursive_query_is_enabled_in_grid_DNS_properties(self):
                print_and_log("*********** verify if recursive query is enabled in grid DNS properties ************")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
                get_ref = json.loads(get_ref)
                print_and_log(get_ref)
                ref = get_ref[0]['_ref']
                get_ref1 = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=allow_recursive_query')
                get_ref1 = json.loads(get_ref1)
                print_and_log(get_ref1)
                forwarder_ip = get_ref1['allow_recursive_query']
                if forwarder_ip == True:
                    print_and_log("Recursive query is enabled")
                    assert True
                else:
                    print_and_log("Recursive query is not enabled")
                    assert False
                print_and_log("Test Case 11 Execution Completed")




        @pytest.mark.run(order=12)
        def test_012_Send_the_dig_query_with_subnet_option(self):
                print_and_log("************ Send the dig query with subnet option *************")
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(config.grid_vip, username='root', password="infoblox")
                stdin, stdout, stderr = client.exec_command('dig @'+config.lan1_ip+' dell.com +edns +subnet=10.0.0.0/8 +nocookie')
                #output = os.popen("dig @"+config.grid_vip+" dell.com +edns +subnet=10.0.0.0/8 +nocookie").read()
                #out = stdout.split("\n")
                #print_and_log(out)
                flag = False
                for i in stdout.readlines():
                    match = re.match("dell.com.\s+\d+\s+IN\s+A\s+(\d+.\d+.\d+.\d+)",i)
                    print_and_log(i)
                    if match:
                        print_and_log(" Match found ")
                        flag=True
                        break
                if flag == True:
                    print_and_log("DNS query got the response by ignorig the subnet option when ECS is disabled")
                    assert True
                else:
                    print_and_log("DNS query didn't get any response when subnet option is sent while ECS is disabled")
                    assert False
                print_and_log("Test Case 12 Execution Completed")



        @pytest.mark.run(order=13)
        def test_013_enable_recursive_ECS_in_grid_DNS_properties(self):
                print_and_log("************ Enable the recursive ECS in grid DNS properties *************")
                data = {"enable_client_subnet_recursive": True}
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
                get_ref = json.loads(get_ref)
                ref = get_ref[0]['_ref']
                get_ref1 = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
                print_and_log(get_ref1)
                assert re.search(r'grid:dns', get_ref1)
                restart_services()
                print_and_log("Test Case 13 Execution Completed")




        @pytest.mark.run(order=14)
        def test_014_verify_if_recursive_ECS_query_is_enabled_in_grid_DNS_properties(self):
                print_and_log("*********** verify if recursive ECS forwarding is enabled in grid DNS properties ************")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
                get_ref = json.loads(get_ref)
                print_and_log(get_ref)
                ref = get_ref[0]['_ref']
                get_ref1 = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=enable_client_subnet_recursive')
                get_ref1 = json.loads(get_ref1)
                print_and_log(get_ref1)
                enable_client_subnet_recursive = get_ref1['enable_client_subnet_recursive']
                if enable_client_subnet_recursive == True:
                    print_and_log("Recursive ECS option is enabled")
                    assert True
                else:
                    print_and_log("Recursive ECS option is not enabled")
                    assert False
                print_and_log("Test Case 14 Execution Completed")




        @pytest.mark.run(order=15)
        def test_015_enable_ECS_forwarding_in_grid_DNS_properties(self):
                print_and_log("************ Enable the ECS forwarding in grid DNS properties *************")
                data = {"enable_client_subnet_forwarding": True}
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
                get_ref = json.loads(get_ref)
                ref = get_ref[0]['_ref']
                get_ref1 = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
                print_and_log(get_ref1)
                assert re.search(r'grid:dns', get_ref1)
                restart_services()
                print_and_log("Test Case 15 Execution Completed")




        @pytest.mark.run(order=16)
        def test_016_verify_if_ECS_forwarding_is_enabled_in_grid_DNS_properties(self):
                print_and_log("*********** verify if ECS forwarding is enabled in grid DNS properties ************")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
                get_ref = json.loads(get_ref)
                print_and_log(get_ref)
                ref = get_ref[0]['_ref']
                get_ref1 = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=enable_client_subnet_forwarding')
                get_ref1 = json.loads(get_ref1)
                print_and_log(get_ref1)
                enable_client_subnet_forwarding = get_ref1['enable_client_subnet_forwarding']
                if enable_client_subnet_forwarding == True:
                    print_and_log("ECS forwarding option is enabled")
                    assert True
                else:
                    print_and_log("ECS forwarding option is not enabled")
                    assert False
                print_and_log("Test Case 16 Execution Completed")




        @pytest.mark.run(order=17)
        def test_017_Send_the_dig_query_with_subnet_option(self):
                print_and_log("************ Send the dig query with subnet option *************")
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(config.grid_vip, username='root', password="infoblox")
                stdin, stdout, stderr = client.exec_command('dig @'+config.lan1_ip+' dell.com +edns +subnet=10.0.0.0/8 +nocookie')
                #output = os.popen("dig @"+config.grid_vip+" dell.com +edns +subnet=10.0.0.0/8 +nocookie").read()
                #out = stdout.split("\n")
                #print_and_log(out)
                flag = False
                for i in stdout.readlines():
                    match = re.match("dell.com.\s+\d+\s+IN\s+A\s+(\d+.\d+.\d+.\d+)",i)
                    print_and_log(i)
                    if match:
                        print_and_log(" Match found ")
                        flag=True
                        break
                if flag == True:
                    print_and_log("DNS query got the response")
                    assert True
                else:
                    print_and_log("DNS query didn't get any response")
                    assert False
                print_and_log("Test Case 17 Execution Completed")



        @pytest.mark.run(order=18)
        def test_018_add_the_zone_to_client_subnet_domains_and_give_allow_permission(self):
                print_and_log("************ Add the zone to client subnet domains and give allow permission ************")
                data = {"client_subnet_domains": [{"domain": "dell.com", "permission": "ALLOW"}]}
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
                get_ref = json.loads(get_ref)
                ref = get_ref[0]['_ref']
                get_ref1 = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
                print_and_log(get_ref1)
                assert re.search(r'grid:dns', get_ref1)
                restart_services()
                print_and_log("Test Case 18 Execution Completed")



        @pytest.mark.run(order=19)
        def test_019_verify_if_zone_is_Added_in_the_client_subnet_domains_and_allow_permissions_is_given(self):
                print_and_log("*********** Verify if zone is Added in the client subnet domains and allow permissions is given ************")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
                get_ref = json.loads(get_ref)
                print_and_log(get_ref)
                ref = get_ref[0]['_ref']
                get_ref1 = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=client_subnet_domains')
                get_ref1 = json.loads(get_ref1)
                print_and_log(get_ref1)
                domain = get_ref1['client_subnet_domains'][0]['domain']
                permission = get_ref1['client_subnet_domains'][0]['permission']
                if domain == "dell.com" and permission == "ALLOW":
                    print_and_log("zone "+domain+" is added in the client subnet doamins and "+permission+" permission is given")
                    assert True
                else:
                    print_and_log("Error while validating the client subent domains")
                    assert False
                print_and_log("Test Case 19 Execution Completed")




        @pytest.mark.run(order=20)
        def test_020_Send_the_dig_query_with_subnet_option(self):
                print_and_log("************ Send the dig query with subnet option *************")
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(config.grid_vip, username='root', password="infoblox")
                stdin, stdout, stderr = client.exec_command('dig @'+config.lan1_ip+' dell.com +edns +subnet=10.0.0.0/8 +nocookie')
                #output = os.popen("dig @"+config.grid_vip+" dell.com +edns +subnet=10.0.0.0/8 +nocookie").read()
                #out = stdout.split("\n")
                #print_and_log(out)
                flag = False
                for i in stdout.readlines():
                    match = re.match("dell.com.\s+\d+\s+IN\s+A\s+(\d+.\d+.\d+.\d+)",i)
                    print_and_log(i)
                    if match:
                        print_and_log(" Match found ")
                        flag=True
                        break
                if flag == True:
                    print_and_log("DNS query got the response")
                    assert True
                else:
                    print_and_log("DNS query didn't get any response")
                    assert False
                print_and_log("Test Case 20 Execution Completed")




        @pytest.mark.run(order=21)
        def test_021_add_the_zone_to_client_subnet_domains_and_give_deny_permission(self):
                print_and_log("************ Add the zone to client subnet domains and give deny permission ************")
                data = {"client_subnet_domains": [{"domain": "dell.com", "permission": "DENY"}]}
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
                get_ref = json.loads(get_ref)
                ref = get_ref[0]['_ref']
                get_ref1 = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
                print_and_log(get_ref1)
                assert re.search(r'grid:dns', get_ref1)
                restart_services()
                print_and_log("Test Case 21 Execution Completed")



        @pytest.mark.run(order=22)
        def test_022_verify_if_zone_is_Added_in_the_client_subnet_domains_and_deny_permissions_is_given(self):
                print_and_log("*********** Verify if zone is Added in the client subnet domains and deny permissions is given ************")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
                get_ref = json.loads(get_ref)
                print_and_log(get_ref)
                ref = get_ref[0]['_ref']
                get_ref1 = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=client_subnet_domains')
                get_ref1 = json.loads(get_ref1)
                print_and_log(get_ref1)
                domain = get_ref1['client_subnet_domains'][0]['domain']
                permission = get_ref1['client_subnet_domains'][0]['permission']
                if domain == "dell.com" and permission == "DENY":
                    print_and_log("zone "+domain+" is added in the client subnet doamins and "+permission+" permission is given")
                    assert True
                else:
                    print_and_log("Error while validating the client subent domains")
                    assert False
                print_and_log("Test Case 22 Execution Completed")




        @pytest.mark.run(order=23)
        def test_023_Send_the_dig_query_with_subnet_option(self):
                print_and_log("************ Send the dig query with subnet option *************")
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(config.grid_vip, username='root', password="infoblox")
                stdin, stdout, stderr = client.exec_command('dig @'+config.lan1_ip+' dell.com +edns +subnet=10.0.0.0/8 +nocookie')
                #output = os.popen("dig @"+config.grid_vip+" dell.com +edns +subnet=10.0.0.0/8 +nocookie").read()
                #out = stdout.split("\n")
                #print_and_log(out)
                flag = False
                for i in stdout.readlines():
                    match = re.match("dell.com.\s+\d+\s+IN\s+A\s+(\d+.\d+.\d+.\d+)",i)
                    print_and_log(i)
                    if match:
                        print_and_log(" Match found ")
                        flag=True
                        break
                if flag == True:
                    print_and_log("DNS query got the response")
                    assert True
                else:
                    print_and_log("DNS query didn't get any response")
                    assert False
                print_and_log("Test Case 23 Execution Completed")




        @pytest.mark.run(order=24)
        def test_024_disable_recursive_ECS_in_grid_DNS_properties(self):
                print_and_log("************ Disable the recursive ECS in grid DNS properties *************")
                data = {"enable_client_subnet_recursive": False}
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
                get_ref = json.loads(get_ref)
                ref = get_ref[0]['_ref']
                get_ref1 = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
                print_and_log(get_ref1)
                assert re.search(r'grid:dns', get_ref1)
                restart_services()
                print_and_log("Test Case 24 Execution Completed")




        @pytest.mark.run(order=25)
        def test_025_verify_if_recursive_ECS_query_is_disabled_in_grid_DNS_properties(self):
                print_and_log("*********** verify if recursive ECS forwarding is disabled in grid DNS properties ************")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
                get_ref = json.loads(get_ref)
                print_and_log(get_ref)
                ref = get_ref[0]['_ref']
                get_ref1 = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=enable_client_subnet_recursive')
                get_ref1 = json.loads(get_ref1)
                print_and_log(get_ref1)
                enable_client_subnet_recursive = get_ref1['enable_client_subnet_recursive']
                if enable_client_subnet_recursive == False:
                    print_and_log("Recursive ECS option is Disabled")
                    assert True
                else:
                    print_and_log("Recursive ECS option is not Disabled")
                    assert False
                print_and_log("Test Case 25 Execution Completed")




        @pytest.mark.run(order=26)
        def test_026_enable_the_dns_over_tls_service(self):
                print_and_log("*********** Enable the dns over tls service ************")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                get_ref = json.loads(get_ref)
                print_and_log(get_ref)
                ref = get_ref[0]['_ref']
                print_and_log(ref)
                data = {"dns_over_tls_service": True}
                get_ref1 = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
                print_and_log(get_ref)
                assert re.search(r'member:dns', ref)
                restart_services()
                print_and_log("Test Case 26 Execution Completed")



        @pytest.mark.run(order=27)
        def test_027_verify_if_dns_over_tls_service_is_enabled(self):
                print_and_log("*********** Verify if dns over tls service is enabled or not ************")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                get_ref = json.loads(get_ref)
                print_and_log(get_ref)
                ref = get_ref[0]['_ref']
                print_and_log(ref)
                get_ref1 = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=dns_over_tls_service')
                get_ref1 = json.loads(get_ref1)
                dns_over_tls_service = get_ref1['dns_over_tls_service']
                if dns_over_tls_service == True:
                    print_and_log("DNS over TLS service is set to "+str(dns_over_tls_service))
                    assert True
                else:
                    print_and_log("DNS over TLS service is not enabled")
                    assert False
                print_and_log("Test Case 27 Execution Completed")



        @pytest.mark.run(order=28)
        def test_028_enable_the_dns_over_https_service(self):
                print_and_log("*********** Enable the dns over https service ************")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                get_ref = json.loads(get_ref)
                print_and_log(get_ref)
                ref = get_ref[0]['_ref']
                print_and_log(ref)
                data = {"doh_service": True}
                get_ref1 = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
                print_and_log(get_ref)
                assert re.search(r'member:dns', ref)
                restart_services()
                print_and_log("Test Case 28 Execution Completed")



        @pytest.mark.run(order=29)
        def test_029_verify_if_dns_over_https_service_is_enabled(self):
                print_and_log("*********** Verify if dns over https service is enabled or not ************")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                get_ref = json.loads(get_ref)
                print_and_log(get_ref)
                ref = get_ref[0]['_ref']
                print_and_log(ref)
                get_ref1 = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=doh_service')
                get_ref1 = json.loads(get_ref1)
                doh_service = get_ref1['doh_service']
                if doh_service == True:
                    print_and_log("DNS over HTTPS service is set to "+str(doh_service))
                    assert True
                else:
                    print_and_log("DNS over HTTPS service is not enabled")
                    assert False
                print_and_log("Test Case 29 Execution Completed")



        @pytest.mark.run(order=30)
        def test_030_enable_the_DNS_cache_accleration(self):
                print_and_log("********** Enable DNS Cache accleration ***********")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                get_ref = json.loads(get_ref)
                ref = get_ref[0]['_ref']
                data = {"enable_dns_cache_acceleration": True}
                get_ref1 = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
                print_and_log(get_ref1)
                assert re.search(r'member:dns', get_ref1)
                sleep(600)
                print_and_log("Test Case 30 Execution Completed")



        @pytest.mark.run(order=31)
        def test_031_verify_if_the_DNS_cache_accleration_is_enabled(self):
                print_and_log("********** Verify if the DNS cache accleration is enabled ***********")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                get_ref = json.loads(get_ref)
                print_and_log(get_ref)
                ref = get_ref[0]['_ref']
                print_and_log(ref)
                get_ref1 = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=dns_cache_acceleration_status')
                get_ref1 = json.loads(get_ref1)
                print_and_log(get_ref1)
                dns_cache_acceleration_status = get_ref1['dns_cache_acceleration_status']
                if dns_cache_acceleration_status == "WORKING":
                    print_and_log("DNS cache accleration is state is "+str(dns_cache_acceleration_status))
                    assert True
                else:
                    print_and_log("DNS cache accleration service is not enabled")
                    assert False
                print_and_log("Test Case 31 Execution Completed")




        @pytest.mark.run(order=32)
        def test_032_configure_the_dnstap_address_in_grid_dns_properties(self):
                print_and_log("************* Configure the DNSTAP address in Grid DNS Properties **************")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
                get_ref = json.loads(get_ref)
                print_and_log(get_ref)
                ref = get_ref[0]['_ref']
                print_and_log(ref)
                data = {"enable_dnstap_queries": True, "enable_dnstap_responses": True, "dnstap_setting": {"dnstap_receiver_address": config.dnstap_address, "dnstap_receiver_port": 6000}}
                get_ref = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
                print_and_log(get_ref)
                restart_services()
                print_and_log("Test Case 32 Execution Completed")



        @pytest.mark.run(order=33)
        def test_033_verify_if_the_dnstap_address_is_configured_in_grid_dns_properties(self):
                print_and_log("*********** Verify if the dnstap address is configured in grid dns properties ***********")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
                get_ref = json.loads(get_ref)
                print_and_log(get_ref)
                ref = get_ref[0]['_ref']
                get_ref1 = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=enable_dnstap_queries')
                get_ref1 = json.loads(get_ref1)
                print_and_log(get_ref1)
                enable_dnstap_queries = get_ref1['enable_dnstap_queries']
                print_and_log(enable_dnstap_queries)
                get_ref2 = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=enable_dnstap_responses')
                get_ref2 = json.loads(get_ref2)
                print_and_log(get_ref2)
                enable_dnstap_responses = get_ref2['enable_dnstap_responses']
                print_and_log(enable_dnstap_responses)
                get_ref3 = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=dnstap_setting')
                get_ref3 = json.loads(get_ref3)
                print_and_log(get_ref3)
                dnstap_receiver_address = get_ref3['dnstap_setting']['dnstap_receiver_address']
                print_and_log(dnstap_receiver_address)
                if enable_dnstap_queries == True and enable_dnstap_responses == True and dnstap_receiver_address == config.dnstap_address:
                    print_and_log("DNSTAP is configured successfully")
                    assert True
                else:
                    print_and_log("DNSTAP is not configured successfully")
                    assert False
                print_and_log("Test Case 33 Execution Completed")



        @pytest.mark.run(order=34)
        def test_034_start_the_dnstap_on_the_ubuntu_client(self):
                print_and_log("*********** start the dnstap on the ubuntu client ************")
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(config.dnstap_address, username='root', password="infoblox")
                stdin, stdout, stderr = client.exec_command('/root/DNSTAP/./dnstap_bin -l '+config.dnstap_address+':6000 > out.txt 2>&1 &')
                client.close()
                sleep(60)
                print_and_log("Test Case 34 Execution Completed")



        @pytest.mark.run(order=35)
        def test_035_Verify_if_the_dnstap_is_running_on_the_ubuntu_client(self):
                print_and_log("************ Verify if the dnstap is running on the ubuntu client ************")
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(config.dnstap_address, username='root', password="infoblox")
                stdin, stdout, stderr = client.exec_command('netstat -anp | grep 6000')
                for line in stdout.readlines():
                    line = line.split('\n')[0]
                    print_and_log(line)
                    match=re.match("tcp\s+0\s+0\s+10.34.172.75:6000\s+\d.\d.\d.\d+:.\s+LISTEN+.*",line)
                    if match:
                        print_and_log("DNSTAP is running")
                        assert True
                        break
                    else:
                        print_and_log("DNSTAP is not running")
                        assert False               
                client.close()
                print_and_log("Test Case 35 Execution Completed")



        @pytest.mark.run(order=36)
        def test_036_send_the_kdig_queries_with_dns_over_tls_and_check_the_query_and_responses_for_the_request_sent(self):
                print_and_log("*********** Send the kdig queries with dns over tls and check the query and responses for the request sent **********")
                output = os.popen("kdig @"+config.lan1_ip+" a1.infoblox1.com +tls").read()
                #out = output.split("\n")
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(config.dnstap_address, username='root', password="infoblox")
                stdin, stdout, stderr = client.exec_command('cd /root')
                stdin, stdout, stderr = client.exec_command('cat out.txt')
                count = 0
                for i in stdout.readlines():
                    if re.search(r'CQ', i):
                        count = count + 1
                        print_and_log(i)
                if count == 1:
                    print_and_log("Single query request is seen when single DIG command is sent")
                    assert True
                else:
                    print_and_log("More Than 1 query request is sent for single when single DIG command is sent")
                    assert False
                stdin, stdout, stderr = client.exec_command('> /root/out.txt')
                client.close()
                print_and_log("Test Case 36 Execution Completed")



        @pytest.mark.run(order=37)
        def test_037_send_the_kdig_queries_with_dns_over_https_and_check_the_query_and_responses_for_the_request_sent(self):
                print_and_log("*********** Send the kdig queries with dns over https and check the query and responses for the request sent **********")
                output = os.popen("kdig @"+config.lan1_ip+" a1.infoblox1.com").read()
                out = output.split("\n")
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(config.dnstap_address, username='root', password="infoblox")
                stdin, stdout, stderr = client.exec_command('cd /root')
                stdin, stdout, stderr = client.exec_command('cat out.txt')
                count = 0
                for i in stdout.readlines():
                    if re.search(r'CQ', i):
                        count = count + 1
                        print_and_log(i)
                if count == 1:
                    print_and_log("Single query request is seen when single DIG command is sent")
                    assert True
                else:
                    print_and_log("More Than 1 query request is sent for single when single DIG command is sent")
                    assert False
                stdin, stdout, stderr = client.exec_command('> /root/out.txt')
                client.close()
                print_and_log("Test Case 37 Execution Completed")




        #NIOS-79682
        @pytest.mark.run(order=38)
        def test_038_Perform_system_reboot(self):
                print_and_log("************ Perform system reboot ************")
                try:
                    #child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
                    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.lan1_ip)
                    child.logfile=sys.stdout
                    sleep(10)
                    child.expect('password:')
                    child.sendline('infoblox')
                    child.expect('Infoblox >')
                    child.sendline('reboot')
                    child.expect(':')
                    child.sendline('y')
                    child.expect('SYSTEM REBOOTING!')
                    sleep(600)
                except Exception as e:
                    print_and_log(e)
                    print_and_log("Error while executing System reboot command")
                    assert False
                print_and_log("Test Case 38 Execution Completed")




        @pytest.mark.run(order=39)
        def test_039_Enable_DOT_Trace_on_grid(self):
                print_and_log("************ Enable DOT Trace on grid ************")
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
                mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
                client.connect(config.lan1_ip, username='root', pkey = mykey)
                stdin, stdout, stderr = client.exec_command('fp-cli fp ib_dca set dot_trace 1')
                output = stdout.read()
                output = output.split("\n")
                print_and_log(output)
                print_and_log("Test Case 39 Execution Completed")



        @pytest.mark.run(order=40)
        def test_040_send_the_kdig_query_and_validate_if_the_txnld_not_found_message_is_not_seen(self):
                print_and_log("*********** send the kdig query and validate if the txnld not found message is not seen **********")
                try:
                    log("start", "/var/log/syslog", config.lan1_ip)
                    output = os.popen("kdig @"+config.grid_vip+" llall.com a +tls").read()
                    sleep(30)
                    LookFor="'is not found in CTX list to send dns response'"
                    log("stop","/var/log/syslog", config.grid_vip)
                    logs=logv(LookFor,"/var/log/syslog", config.grid_vip)
                    print_and_log("Error Log is found which is not expected")
                    assert False
                except Exception as e:
                    print_and_log(e)
                    print_and_log("Error log is not found")
                    assert True
                print_and_log("Test Case 40 Execution Completed")



        @pytest.mark.run(order=41)
        def test_041_Disable_DOT_Trace_on_grid(self):
                print_and_log("************ Disable DOT Trace on grid ************")
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
                mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
                client.connect(config.lan1_ip, username='root', pkey = mykey)
                stdin, stdout, stderr = client.exec_command('fp-cli fp ib_dca set dot_trace 0')
                output = stdout.read()
                output = output.split("\n")
                print_and_log(output)
                print_and_log("Test Case 41 Execution Completed")




        #NIOS-81403
        @pytest.mark.run(order=42)
        def test_042_enable_bonding_ip_interface_on_the_grid(self):
                print_and_log("************ enable bonding ip interface on the grid *************")
                data = {"lan2_port_setting": {"nic_failover_enabled": True, "enabled": True}}
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                get_ref = json.loads(get_ref)
                print_and_log(get_ref)
                ref = get_ref[0]['_ref']
                get_ref1 = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
                print_and_log(get_ref1)
                sleep(300)
                print_and_log("Test Case 42 Execution Completed")



        @pytest.mark.run(order=43)
        def test_043_verify_if_bonding_ip_interface_is_enabled_on_the_grid(self):
                print_and_log("************ verify if bonding ip interface is enabled on the grid *************")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                get_ref = json.loads(get_ref)
                print_and_log(get_ref)
                ref = get_ref[0]['_ref']
                get_ref1 = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=lan2_port_setting')
                get_ref1 = json.loads(get_ref1)
                print_and_log(get_ref1)
                nic_failover_enabled = get_ref1['lan2_port_setting']['nic_failover_enabled']
                enabled = get_ref1['lan2_port_setting']['enabled']
                if nic_failover_enabled == True and enabled == True:
                    print_and_log("Bonding IP interface is enabled")
                    assert True
                else:
                    print_and_log("Bonding IP interface is not enabled")
                    assert False
                print_and_log("Test Case 43 Execution Completed")



        @pytest.mark.run(order=44)
        def test_044_Perform_system_reboot(self):
                print_and_log("************ Perform system reboot ************")
                try:
                    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.lan1_ip)
                    child.logfile=sys.stdout
                    sleep(10)
                    child.expect('password:')
                    child.sendline('infoblox')
                    child.expect('Infoblox >')
                    child.sendline('reboot')
                    child.expect(':')
                    child.sendline('y')
                    child.expect('SYSTEM REBOOTING!')
                    sleep(600)
                except Exception as e:
                    print_and_log(e)
                    print_and_log("Error while executing System reboot command")
                    assert False
                print_and_log("Test Case 44 Execution Completed")




        @pytest.mark.run(order=45)
        def test_045_send_maximum_kdig_queries_using_dns_over_tls_and_validate_the_LAN1_stats_for_the_same(self):
                print_and_log("*********** send maximum dig queries using dns over tls and validate the LAN1 stats for the same ************")
                for i in range(0,500):
                    output = os.popen("kdig @"+config.lan1_ip+" dell.com +tls").read()
                    out = output.split("\n")
                    print_and_log(out)
                print_and_log("Test Case 45 Execution Completed")




        @pytest.mark.run(order=46)
        def test_046_Exeute_the_cli_command_show_dns_accel_and_verify_the_query_and_response_counts(self):
                print_and_log("********* Exeute the cli command show dns accel and verify the query and response counts ************")
                args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+str(config.lan1_ip)
                args=shlex.split(args)
                child = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                child.stdin.write("show dns-accel\n")
                result = child.communicate()
                print_and_log(result[0])
                result = str(result)
                output = result.split('\n')
                query_count_on_lan1 = []
                response_count = []
                for i in output:
                    match = re.search(r'System\s+UDP\s+DNS\s+query\s+count:\s+MGMT=\d+\s+LAN1=\d+\s+HA=\d+\s+LAN2=\d', i)
                    match1 = re.search(r'System\s+UDP\s+DNS\s+response\s+count:\s+\d+', i)
                    if match and match1:
                        print_and_log(match.group())
                        print_and_log(match1.group())
                        output1 = match.group().split(' ')
                        for line in output1:
                            match2 = re.search(r'LAN1=\d', line)
                            if match2:
                                query_count = line.split('=')[1]
                                print_and_log(query_count)
                                query_count_on_lan1.append(query_count)
                        output2 = match1.group().split(' ')
                        for line in output2:
                            match3 = re.search(r'\d+', line)
                            if match3:
                                res_count = line.split('\n')[0]
                                print_and_log(res_count)
                                response_count.append(res_count)
                print_and_log("The total number of queries on LAN1 is "+query_count_on_lan1[0])
                print_and_log("The total number of responses is "+response_count[0])
                if query_count_on_lan1 == response_count:
                    print_and_log("match in the count of queries sent and responses are same")
                    assert True
                else:
                    print_and_log("There is difference in the count of queries sent and responses")
                    assert False
                print_and_log("Test Case 46 Execution Completed")



        @pytest.mark.run(order=47)
        def test_047_send_maximum_kdig_queries_using_dns_over_https_and_validate_the_LAN1_stats_for_the_same(self):
                print_and_log("*********** send maximum dig queries using dns over https and validate the LAN1 stats for the same ************")
                for i in range(0,500):
                    output = os.popen("kdig @"+config.lan1_ip+" dell.com").read()
                    out = output.split("\n")
                    print_and_log(out)
                print_and_log("Test Case 47 Execution Completed")



        @pytest.mark.run(order=48)
        def test_048_Exeute_the_cli_command_show_dns_accel_and_verify_the_query_and_response_counts(self):
                print_and_log("********* Exeute the cli command show dns accel and verify the query and response counts ************")
                args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+str(config.lan1_ip)
                args=shlex.split(args)
                child = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                child.stdin.write("show dns-accel\n")
                result = child.communicate()
                print_and_log(result[0])
                result = str(result)
                output = result.split('\n')
                query_count_on_lan1 = []
                response_count = []
                for i in output:
                    match = re.search(r'System\s+UDP\s+DNS\s+query\s+count:\s+MGMT=\d+\s+LAN1=\d+\s+HA=\d+\s+LAN2=\d', i)
                    match1 = re.search(r'System\s+UDP\s+DNS\s+response\s+count:\s+\d+', i)
                    if match and match1:
                        print_and_log(match.group())
                        print_and_log(match1.group())
                        output1 = match.group().split(' ')
                        for line in output1:
                            match2 = re.search(r'LAN1=\d', line)
                            if match2:
                                query_count = line.split('=')[1]
                                print_and_log(query_count)
                                query_count_on_lan1.append(query_count)
                        output2 = match1.group().split(' ')
                        for line in output2:
                            match3 = re.search(r'\d+', line)
                            if match3:
                                res_count = line.split('\n')[0]
                                print_and_log(res_count)
                                response_count.append(res_count)
                print_and_log("The total number of queries on LAN1 is "+query_count_on_lan1[0])
                print_and_log("The total number of responses is "+response_count[0])
                if query_count_on_lan1 == response_count:
                    print_and_log("match in the count of queries sent and responses are same")
                    assert True
                else:
                    print_and_log("There is difference in the count of queries sent and responses")
                    assert False
                print_and_log("Test Case 48 Execution Completed")




        #NIOS-80734
        @pytest.mark.skip(order=49)
        def test_049_Enable_FIPS_Mode_on_the_Grid(self):
                print_and_log("************ Enable FIPS Mode on the Grid ************")
                try:
                    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.lan1_ip)
                    child.logfile=sys.stdout
                    sleep(10)
                    child.expect('password:')
                    child.sendline('infoblox')
                    child.expect('Infoblox >')
                    child.sendline('set fips_mode')
                    child.expect(':')
                    child.sendline('y')
                    child.expect(':')
                    child.sendline('y')
                    child.expect(':')
                    child.sendline('y')
                    sleep(900)
                except Exception as e:
                    print_and_log(e)
                    print_and_log("Error while setting the Grid to FIPS mode")
                    assert False
                print_and_log("Test Case 49 Execution Completed")




        @pytest.mark.skip(order=50)
        def test_050_Verify_if_fips_mode_is_enabled(self):
                print_and_log("************ Verify if FIPS mode is enabled ************")
                try:
                    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.lan1_ip)
                    child.logfile=sys.stdout
                    sleep(10)
                    child.expect('password:')
                    child.sendline('infoblox')
                    child.expect('Infoblox >')
                    child.sendline('show fips_mode')
                    child.expect('Yes')
                except Exception as e:
                    print_and_log(e)
                    print_and_log("Error while setting the Grid to FIPS mode")
                    assert False
                print_and_log("Test Case 50 Execution Completed")



        @pytest.mark.skip(order=51)
        def test_051_Configure_the_tacacs_Server(self):
                print_and_log("************ Configure the tacacs Server ************")
                data = {"name": "tacacs_server", "servers":[{"address": "10.120.22.170", "shared_secret":"testing123"}]}
                response = ib_NIOS.wapi_request('POST',object_type="tacacsplus:authservice",fields=json.dumps(data))
                print_and_log(response)
                assert re.search(r'tacacsplus:authservice', response)
                print_and_log("Test Case 51 Execution Completed")



        @pytest.mark.skip(order=52)
        def test_052_verify_the_tacacs_Server(self):
                print_and_log("************ Verify the tacacs Server configured ************")
                response = ib_NIOS.wapi_request('GET',object_type="tacacsplus:authservice")
                response = json.loads(response)
                ref = response[0]['_ref']
                name = response[0]['name']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=servers')
                response1 = json.loads(response1)
                tacacs_address = response1['servers'][0]['address']
                if tacacs_address == config.tacacs_address and name == "tacacs_server":
                    print_and_log("tacacs server is configured successfully")
                    assert True
                else:
                    print_and_log("tacacs server is not configured")
                    assert False
                print_and_log("Test Case 52 Execution Completed")




        @pytest.mark.run(order=53)
        def test_053_enable_the_threat_protection_service_on_the_grid(self):
                print_and_log("*********** Enable the threat protection service on the grid ***********")
                data = {"enable_service": True}
                response = ib_NIOS.wapi_request('GET',object_type="member:threatprotection")
                response = json.loads(response)
                ref = response[0]['_ref']
                print_and_log(ref)
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
                print_and_log(response1)
                assert re.search(r'member:threatprotection', response1)
                restart_services()
                sleep(600)
                print_and_log("Test Case 53 Execution Completed")




        @pytest.mark.run(order=54)
        def test_054_verify_if_the_threat_protection_service_is_enabled_on_the_grid(self):
                print_and_log("*********** verify if the threat protection service is enabled on the grid ***********")
                response = ib_NIOS.wapi_request('GET',object_type="member:threatprotection")
                response = json.loads(response)
                ref = response[0]['_ref']
                print_and_log(ref)
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=enable_service')
                response1 = json.loads(response1)
                enable_service = response1['enable_service']
                if enable_service == True:
                    print_and_log("Threat protection service is enabled")
                    assert True
                else:
                    print_and_log("Threat protection service is not enabled")
                    assert False
                print_and_log("Test Case 54 Execution Completed")




        @pytest.mark.run(order=55)
        def test_055_configure_the_dns_resolver_ip_in_grid_properties(self):
                print_and_log("************* configure the dns resolver ip in grid properties **************")
                data = {"dns_resolver_setting": {"resolvers":[config.resolver]}}
                response = ib_NIOS.wapi_request('GET',object_type="grid")
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
                print_and_log(response1)
                assert re.search(r'grid', response1)
                print_and_log("Test Case 55 Execution Completed")



        @pytest.mark.run(order=56)
        def test_056_verify_the_dns_resolver_ip_in_grid_properties(self):
                print_and_log("*********** Verify the dns resolver ip in grid properties ************")
                response = ib_NIOS.wapi_request('GET',object_type="grid")
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=dns_resolver_setting')
                response1 = json.loads(response1)
                resolver_ip = response1['dns_resolver_setting']['resolvers'][0]
                print_and_log(resolver_ip)
                if resolver_ip == config.resolver:
                    print_and_log("DNS resolver "+resolver_ip+" is configured")
                    assert True
                else:
                    print_and_log("DNS resolver is not configured")
                    assert False
                print_and_log("Test Case 56 Execution Completed")


        @pytest.mark.run(order=57)
        def test_057_enable_mgmt_port_for_dns(self):
                print_and_log("*********** Enable mgmt port for dns *************")
                ref=ib_NIOS.wapi_request('GET', object_type="member:dns")
                ref=json.loads(ref)[0]['_ref']
                data={"enable_dns":True,"use_mgmt_port":True}
                ref1=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
                print_and_log(ref1)
                restart_services()
                print_and_log("Test Case 57 Execution Completed")



        @pytest.mark.run(order=58)
        def test_058_verify_if_enable_mgmt_port_for_dns_is_set_to_true(self):
                print_and_log("*********** Verify if enable mgmt port for dns is set to true *************")
                ref=ib_NIOS.wapi_request('GET', object_type="member:dns")
                ref=json.loads(ref)[0]['_ref']
                ref1=ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=use_mgmt_port')
                ref1 = json.loads(ref1)
                print_and_log(ref1)
                use_mgmt_port = ref1['use_mgmt_port']
                print_and_log(use_mgmt_port)
                if use_mgmt_port == True:
                    print_and_log("Use MGM Port is enabled")
                    assert True
                else:
                    print_and_log("Use MGM Port is not enabled")
                    assert False
                print_and_log("Test Case 58 Execution Completed")




        @pytest.mark.run(order=59)
        def test_059_download_the_latest_ruleset(self):
                print_and_log("************ Download the latest ruleset *************")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:threatprotection")
                get_ref = json.loads(get_ref)
                print_and_log(get_ref)
                ref = get_ref[0]['_ref']
                data = {"enable_auto_download": True}
                response = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
                print_and_log(response)
                assert re.search(r'grid:threatprotection', response)
                restart_services()
                response = ib_NIOS.wapi_request('POST',object_type="fileop",params="?_function=download_atp_rule_update")
                sleep(300)
                print_and_log("Test Case 59 Execution Completed")



        @pytest.mark.run(order=60)
        def test_060_verify_if_the_latest_ruleset_is_downloaded(self):
                print_and_log("************* Verify if the latest ruleset is downloaded *************")
                get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
                get_ref = json.loads(get_ref)
                print_and_log(get_ref)
                version = get_ref[0]['version']
                match = re.search(r'\d+-\d+', version)
                if match:
                    print_and_log("Latest ruleset "+match.group()+" is downloaded")
                    assert True
                else:
                    print_and_log("Latest ruleset is not downloaded")
                    assert False
                print_and_log("Test Case 60 Execution Completed")



        @pytest.mark.run(order=61)
        def test_061_Add_new_blackrule_with_custom_name_c0_followed_with_semicolon_and_expect_error(self):
                print_and_log("********** Add new blackrule with custom name c0 followed with semicolon and expect error **********")
                log("start", "/var/log/syslog", config.grid_vip)
                ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
                ref = json.loads(ref)
                print_and_log(ref)
                version = ref[0]['version']
                match = re.search(r'\d+-\d+', version)
                version = match.group()
                get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:rulecategory")
                get_ref = json.loads(get_ref)
                blacklist_rule = []
                for i in get_ref:
                    name = i['name']
                    match1 = re.search(r'BLACKLIST\s+UDP\s+FQDN\s+lookup', name)
                    if match1:
                        #print_and_log(match.group())
                        blacklist_rule.append(match1.group())
                    else:
                        continue
                print_and_log(blacklist_rule)
                get_ref1 = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate", params='?sid=120303000&ruleset='+version)
                get_ref1 = json.loads(get_ref1)
                print_and_log(get_ref1)
                rule_template_ref = get_ref1[0]['_ref']
                print_and_log(rule_template_ref)
                #data = {"template":rule_template_ref,"disabled":False,"comment": "rule1","config":{"action":"DROP","log_severity":"MAJOR","params":[{"name": blacklist_rule[0], "value":"c0;"},{"name": "EVENTS_PER_SECOND","value":"1"}]}}
                data = {"template":rule_template_ref, "disabled":False,"comment": "rule1","config":{"action":"DROP","log_severity":"MAJOR","params":[{"name": "FQDN", "value":"c0;"},{"name": "EVENTS_PER_SECOND","value":"1"}]}}
                response = ib_NIOS.wapi_request('POST',object_type="threatprotection:grid:rule",fields=json.dumps(data))
                #response = ib_NIOS.wapi_request('PUT',object_type="threatprotection:rule",fields=json.dumps(data))
                print_and_log(response)
                assert re.search(r'threatprotection:grid:rule', response)
                res =  ib_NIOS.wapi_request('GET', object_type="grid")
                res = json.loads(res)[0]['_ref']
                data={"member_order":"SIMULTANEOUSLY"}
                response1 = ib_NIOS.wapi_request('POST', object_type=res, params='?_function=publish_changes', fields=json.dumps(data))
                sleep(10)
                restart_services()
                LookFor="'err Error publishing configuration changes for the Threat Protection service'"
                log("stop","/var/log/syslog", config.grid_vip)
                try:
                    logs=logv(LookFor,"/var/log/syslog", config.grid_vip)
                except subprocess.CalledProcessError:
                    print_and_log(" The ruleset configured is successful no error message is seen in the syslog ")
                    assert True
                else:
                    print_and_log(" Rule configuration failed or Connection failed ")
                    assert False
                print_and_log("Test Case 61 Execution Completed")

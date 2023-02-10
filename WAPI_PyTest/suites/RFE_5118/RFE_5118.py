import re
import pexpect
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
import commands
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util
from paramiko import client
import paramiko
import re
import time
import pdb
import ipaddress
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv

def test_grid_vip_validation_add_to_configuration_file():
        grid_ipv6 = config.grid_vip
        grid_ipv6 = grid_ipv6.replace('[','').replace(']','')
        grid_ipv6 = ipaddress.ip_address(unicode(grid_ipv6))
        grid_ipv6 = (str(grid_ipv6))
        print(grid_ipv6)
	os.system("echo -e 'grid_ipv6=\""+grid_ipv6+"\"' >> config.py")
	reload(config)
	sleep(60)

def test_member_ip_validation_add_to_configuration_file():
        member_ipv6 = config.member_ip
        member_ipv6 = member_ipv6.replace('[','').replace(']','')
        member_ipv6 = ipaddress.ip_address(unicode(member_ipv6))
        member_ipv6 = (str(member_ipv6))
        print(member_ipv6)
	os.system("echo -e 'member_ipv6=\""+member_ipv6+"\"' >> config.py")
	reload(config)
	sleep(60)

def test_member1_ip_validation_add_to_configuration_file():
        member1_ipv6 = config.member1_ip
        member1_ipv6 = member1_ipv6.replace('[','').replace(']','')
        member1_ipv6 = ipaddress.ip_address(unicode(member1_ipv6))
        member1_ipv6 = (str(member1_ipv6))
        print(member1_ipv6)
	os.system("echo -e 'member1_ipv6=\""+member1_ipv6+"\"' >> config.py")
	reload(config)
	sleep(60)

def test_external_ipv6_validation_add_to_configuration_file():
        external_ipv6 = config.external_ipv6
        external_ipv6 = external_ipv6.replace('[','').replace(']','')
        external_ipv6 = ipaddress.ip_address(unicode(external_ipv6))
        external_ipv6 = (str(external_ipv6))
        print(external_ipv6)
	os.system("echo -e 'external_ipv6=\""+external_ipv6+"\"' >> config.py")
	reload(config)
	sleep(60)


class Network(unittest.TestCase):
	    
            @pytest.mark.run(order=1)
            def test_001_create_IPv6_network_with_members_assignment(self):
           	logging.info("Creatiing an ipv6 network with members assignment")
		global ipv6_network
		ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
	 	ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
		data = {"network": ipv6_network+"::/64","network_view": "default","members": [{"_struct": "dhcpmember","ipv6addr": config.member_ipv6,"name": config.grid_member2_fqdn},{"_struct": "dhcpmember","ipv6addr": config.member1_ipv6,"name": config.grid_member1_fqdn}]}
                response = ib_NIOS.wapi_request('POST', object_type="ipv6network", fields=json.dumps(data), grid_vip=config.grid_vip)
          	print(response)
                sleep(05)
                print("Test Case 1 Execution Completed")

	    
            @pytest.mark.run(order=2)
            def test_002_validate_IPv6_network_and_assigned_members(self):
                logging.info("creating ipv6 network")
                output = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=members,network",grid_vip=config.grid_vip)
                print("output",output)
		result = ['"ipv4addr": null','"ipv6addr": "'+config.member_ipv6+'"','"name": "'+config.grid_member2_fqdn+'"','"network": "'+ipv6_network+'::/64"','"ipv6addr": "'+config.member1_ipv6+'"','"name": "'+config.grid_member1_fqdn+'"']
		print(result)
                for values in result:
                    if values in output:
                        assert True
			print(values)
                    else:
                        assert False
                print(result)
                sleep(05)
                print("Test Case 2 Execution Completed")
	    
            @pytest.mark.run(order=3)
            def test_003_create_IPv6_address_Range(self):
                logging.info("Creating ipv6 address range")
		member_ip = config.member_ip
                member_ip = member_ip.replace('[','').replace(']','')
		member_ip = (str(member_ip))
                data ={"end_addr": ipv6_network+"::100","network": ipv6_network+"::/64","network_view": "default","start_addr": ipv6_network+"::10","member": {"_struct": "dhcpmember","ipv6addr": config.member_ipv6,"name": config.grid_member2_fqdn}}
		print(data)
                response = ib_NIOS.wapi_request('POST', object_type="ipv6range", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                sleep(05)
                print("\nTest Case 3 Execution Completed")
	    
            @pytest.mark.run(order=4)
            def test_004_Validate_created_range(self):
                logging.info("validating the created range")
                get_ref =  ib_NIOS.wapi_request('GET', object_type="ipv6range", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[-1]['_ref']
                ref = eval(json.dumps(ref))
                response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=member,end_addr,start_addr",grid_vip=config.grid_vip)
                print(response)
                output = ['"ipv6addr": "'+config.member_ipv6+'"','"name": "'+config.grid_member2_fqdn+'"','"end_addr": "'+ipv6_network+"::100",'"start_addr": "'+ipv6_network+"::10"]
		print(output)
                for values in output:
                    if values in response:
                        assert True
			print(values)
                    else:
                        assert False
                print(output)
                sleep(05)
                print("\nTest Case 4 Execution Completed")

            @pytest.mark.run(order=5)
            def test_005_Add_authoritative_forward_mapping_zone(self):
                logging.info("adding authoritative forward-mapping zone")
		get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                ref2 = json.loads(get_ref)[1]['_ref']
                ref3 = json.loads(get_ref)[2]['_ref']
                data = {"use_lan_ipv6_port": True}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                response = ib_NIOS.wapi_request('PUT',ref=ref2,fields=json.dumps(data), grid_vip=config.grid_vip)
                response = ib_NIOS.wapi_request('PUT',ref=ref3,fields=json.dumps(data), grid_vip=config.grid_vip)
                data = {"fqdn": "test.com","view": "default","grid_primary": [{"name": config.grid_member2_fqdn,"stealth": False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                sleep(05)
                print("\nTest Case 5 Execution Completed")
	    
            @pytest.mark.run(order=6)
            def test_006_Validate_added_authoritative_forward_mapping_zone(self):
                logging.info("validating created authoritative forward mapping zone")
                get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth?fqdn=test.com",grid_vip=config.grid_vip)
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=grid_primary,fqdn" , grid_vip=config.grid_vip)
                output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','').replace('[','').replace(']','')
                result = ['fqdn:test.com','grid_primary:name:'+config.grid_member2_fqdn,'stealth:false']
		print(result)
                for string in result:
                    if string in output:
                        assert True
                    else:
                        assert False
                print(result)
                sleep(05)
                print("Test Case 6 Executuion Completed")
	    
            @pytest.mark.run(order=7)
            def test_007_Add_authoritative_reverse_mapping_zone(self):
                logging.info("adding authoritative reverse mapping zone")
                data = {"fqdn": ipv6_network+"::/64","zone_format": "IPV6","grid_primary": [{"name": config.grid_member2_fqdn,"stealth": False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                sleep(05)
                print("\nTest Case 7 Execution Completed")
	    
            @pytest.mark.run(order=8)
            def test_008_Validate_added_reverse_mapping_zone(self):
                get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[-1]['_ref']
                output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=grid_primary,fqdn,zone_format",grid_vip=config.grid_vip)
                print(output)
                output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','').replace('[','').replace(']','')
                result = ['fqdn:'+ipv6_network+'::/64','grid_primary:name:'+config.grid_member2_fqdn,'zone_format:IPV6']
		print(result)
                for values in result:
                    if values in output:
                        assert True
			print(values)
                    else:
                        assert False
                print(result)
                sleep(05)
                print("\nTest Case 8 Executuion Completed")
		   
            @pytest.mark.run(order=9)
            def test_009_Enable_IPv6_DDNS_Updates(self):
                logging.info("enabling ipv6 ddns updates")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                data = {"ipv6_enable_ddns": True}
                response1 = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response1)
                sleep(05)
                print("Test Case 9 Execution Completed")

            @pytest.mark.run(order=10)
            def test_010_Validate_enabled_ipv6_ddns_updates(self):
                logging.info("Validating IPv6 ddns updates")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=ipv6_enable_ddns",grid_vip=config.grid_vip)
                print(response)
                output = '"ipv6_enable_ddns": true'
                if output in response:
                    assert True
                else:
                    assert False
                print(output)
                sleep(05)
                print("\nTest Case 10 Execution Completed")

            @pytest.mark.run(order=11)
            def test_011_Add_ipv6_ddns_domainname_and_ipv6_domain_name_and_ipv6_domain_name_servers_at_grid_level(self):
                logging.info("adding ipv6 ddns domain name and ipv6 domain name and ipv6 domain name servers at grid level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                data = {"ipv6_ddns_domainname": "test.com","ipv6_domain_name": "test.com","ipv6_domain_name_servers": [config.member_ipv6]  }
                response1 = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response1)
                sleep(05)
                print("\nTest Case 11 Execution Completed")


            @pytest.mark.run(order=12)
            def test_012_Validate_added_ipv6_ddns_domainname_and_ipv6_domain_name_and_ipv6_domain_name_servers_at_grid_level(self):
                logging.info("validating added ipv6 ddns domain name and ipv6 domain name and ipv6 domain name servers at grid level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                print(ref)
                response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=ipv6_ddns_domainname,ipv6_domain_name,ipv6_domain_name_servers",grid_vip=config.grid_vip)
                print(response)
                response=response.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','').replace('[','').replace(']','')
                output = ['ipv6_domain_name_servers:'+config.member_ipv6,'ipv6_ddns_domainname:test.com','ipv6_domain_name:test.com']
                for values in output:
                    if values in response:
                        assert True
                    else:
                        assert False
                print(output)
                sleep(10)
                print("Test CAse 12 Execution Completed")

            @pytest.mark.run(order=13)
            def test_013_Enable_ipv6_ddns_enable_option_fqdn(self):
                logging.info("enabling ipv6 ddns enable option fqdn")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                data = {"ipv6_ddns_enable_option_fqdn": True}
                response1 = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response1)
                sleep(05)
                print("Test Case 13 Execution Completed")

            @pytest.mark.run(order=14)
            def test_014_Validate_enabled_ipv6_ddns_enable_option_fqdn(self):
                logging.info("validating enabled ipv6 ddns enable option fqdn")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=ipv6_ddns_enable_option_fqdn",grid_vip=config.grid_vip)
                print(response)
                output = '"ipv6_ddns_enable_option_fqdn": true'
                if output in response:
                    assert True
                else:
                    assert False
                print(output)
                sleep(05)
                print("\nTest Case 14 Execution Completed")

            @pytest.mark.run(order=15)
            def test_015_Enable_DHCP_server_authoritative(self):
                logging.info("enabling DHCP server authoritative")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                data = {"authority": True}
                response1 = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response1)
                sleep(05)
                print("Test Case 15 Execution Completed")

            @pytest.mark.run(order=16)
            def test_016_Validate_enabled_DHCP_server_authoritative(self):
                logging.info("Validating enabled DHCP server authoritative")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=authority",grid_vip=config.grid_vip)
                print(response)
                output = '"authority": true'
                if output in response:
                    assert True
                else:
                    assert False
                print(output)
                sleep(05)
                print("\nTest Case 16 Execution Completed")


            @pytest.mark.run(order=17)
            def test_017_start_IPv6_DHCP_service_on_all_members(self):
                logging.info("starting the ipv6 dhcp service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
                print(get_ref)
                res = json.loads(get_ref)
                data = {"enable_dhcpv6_service":True}
                ref1 = json.loads(get_ref)[0]['_ref']
                response1 = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response1)
                sleep(20)
                ref2 = json.loads(get_ref)[1]['_ref']
                response2 = ib_NIOS.wapi_request('PUT',ref=ref2,fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response2)
                sleep(20)
                ref3 = json.loads(get_ref)[2]['_ref']
                response3 = ib_NIOS.wapi_request('PUT',ref=ref3,fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response3)
                sleep(20)
                print("Test Case 17 Execution Completed")

            @pytest.mark.run(order=18)
            def test_018_Validate_IPv6_DHCP_service_on_all_members(self):
                logging.info("validating enabled tpv6 dhcp service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=enable_dhcpv6_service",grid_vip=config.grid_vip)
                print(response1)
                ref2 = json.loads(get_ref)[1]['_ref']
                response2 = ib_NIOS.wapi_request('GET',ref=ref2,params="?_inheritance=True&_return_fields=enable_dhcpv6_service",grid_vip=config.grid_vip)
                print(response2)
                ref3 = json.loads(get_ref)[2]['_ref']
                response3 = ib_NIOS.wapi_request('GET',ref=ref3, params="?_inheritance=True&_return_fields=enable_dhcpv6_service",grid_vip=config.grid_vip)
                print(response3)
                response = [response1,response2,response3]
                output = '"enable_dhcpv6_service": true'
                for values in response:
                    if output in values:
                        assert True
                    else:
                        assert False
                print(output)
                sleep(05)
                print("\nTest Case 18 Execution Completed")  

            @pytest.mark.run(order=19)
            def test_019_Restart_grid_service(self):
                logging.info("restarting the grid services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 19 Execution Completed")

            @pytest.mark.run(order=20)
            def test_020_start_IPv6_DNS_service_on_all_members(self):
                logging.info("starting the ipv6 DNS service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
                print(get_ref)
                res = json.loads(get_ref)
		ref1 = json.loads(get_ref)[0]['_ref']
		ref2 = json.loads(get_ref)[1]['_ref']
		ref3 = json.loads(get_ref)[2]['_ref']
                data = {"enable_dns": True}
                response1 = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response1)
                sleep(20)
                ref2 = json.loads(get_ref)[1]['_ref']
                response2 = ib_NIOS.wapi_request('PUT',ref=ref2,fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response2)
                sleep(20)
                ref3 = json.loads(get_ref)[2]['_ref']
                response3 = ib_NIOS.wapi_request('PUT',ref=ref3,fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response3)
                sleep(20)
                print("Test Case 20 Execution Completed")

            @pytest.mark.run(order=21)
            def test_021_validate_IPv6_DNS_service_on_all_members(self):
                logging.info("starting ipv6 DNS service on master")
                grid =  ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
                print(grid)
                ref1 = json.loads(grid)[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=enable_dns",grid_vip=config.grid_vip)
                print(response1)
                ref2 = json.loads(grid)[1]['_ref']
                response2 = ib_NIOS.wapi_request('GET',ref=ref2,params="?_inheritance=True&_return_fields=enable_dns",grid_vip=config.grid_vip)
                print(response2)
                ref3 = json.loads(grid)[2]['_ref']
                response3 = ib_NIOS.wapi_request('GET',ref=ref3, params="?_inheritance=True&_return_fields=enable_dns",grid_vip=config.grid_vip)
                print(response3)
                response = [response1,response2,response3]
                result = '"enable_dns": true'
                for values in response:
                    if result in values:
                        assert True
                    else:
                        assert False
                print(result)
		sleep(60)
                print("\nTest Case 21 Execution Completed")

	     
            @pytest.mark.run(order=22)
            def test_022_start_the_logs_and_request_ipv6_lease_with_hostand_and_mac_address_and_stop_the_logs(self):
                logging.info("Perform dras command")
                log("start","/var/log/syslog",config.member_ipv6)
		sleep(10)
		for i in range(10):
                    #dras_cmd = 'sudo /root/dras6/dras6 -i '+str(config.member_ipv6)+' '+'-A -n 1 -h test.com -a 12:12:12:12:12:12'
		    dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.member_ipv6)+' '+'-A -n 1 -h test.com -a 12:12:12:12:12:12'
		    print(dras_cmd)
		    dras_cmd1 = os.system(dras_cmd)
		    sleep(02)
		    print("output is ",dras_cmd1)
                    if dras_cmd1 == 0:
                        print("got the lease")
                        break
                    else:
                        print("didn't get the lease and continuing for lease")
		ping = ('for i in range{1..2} ; do ping6 -i 1 -c 5 '+config.member_ipv6+' ; done')
                data = os.popen(ping).read()
                print(data)
		sleep(300)
                log("stop","/var/log/syslog",config.member_ipv6)
                print("\nTest Case 22 Executed Successfully")

	    
            @pytest.mark.run(order=23)
            def test_023_validating_ipv6_lease_and_status_of_the_lease(self):
                logging.info("validating the lease and status of the lease")
                out1 = str(config.member_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                #print(log_validation)
                output1 = re.search('debug Lease on(.*)preferred for 27000s', log_validation)
                output1 = output1.group(0)
                print(output1)
                def Convert(string):
                    li = list(string.split(" "))
                    return li
                str1 = Convert(output1)
                Lease_IPv6 = str1[4]
                print(Lease_IPv6)
                get_ref = ib_NIOS.wapi_request('GET', object_type="lease", grid_vip=config.grid_vip)
                #print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[-1]['_ref']
                #print(ref1)
                response = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=binding_state,address",grid_vip=config.grid_vip)
                print(response)
                #output = ['"address": "'+Lease_IPv6+'"','"binding_state": "ACTIVE"']
                #print(output) 
                #for values in output:
                #    if values in response:
                #        assert True
                #    else:
                #        assert False
                sleep(05)
                print("\ntest Case 23 Executed Successfully")
	    
            @pytest.mark.run(order=24)
            def test_024_validate_the_ipv6_lease_and_hostname_in_var_log_messages(self):
                logging.info("validating the ipv6 lease and hostname in var log messages")
                out1 = str(config.member_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                output1 = re.search('debug Lease on(.*)preferred for 27000s',log_validation)
                output1 = output1.group(0)
                print(output1)
		output2 = re.search('Added new forward map from(.*)::',log_validation)
                output2 = output2.group(0)
                print(output2)
                output3 = re.search('Added reverse map from(.*)test.com',log_validation)
                output3 = output3.group(0)
                print(output3)
                host_name = 'h121212121212.test.com'
                output = (output1,output2,output3)
                for values in output:
                    if host_name in values:
                        assert True
                    else:
                        assert False
                print(host_name)
                sleep(05)
                print("\nTest Case 24 Executed Successfully")           


            @pytest.mark.run(order=25)
            def test_025_validate_ddns_update_records_in_authoritative_forward_mapping_zone(self):
                logging.info("validating ddns update records in authoritative forward mapping zone")
                out1 = str(config.member_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                output1 = re.search('debug Lease on(.*)preferred for 27000s', log_validation)
                output1 = output1.group(0)
                print(output1)
                def Convert(string):
                    li = list(string.split(" "))
                    return li
                str1 = Convert(output1)
                Lease_IPv6 = str1[4]
                values = ('ipv6addr:'+Lease_IPv6)
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:aaaa", grid_vip=config.grid_vip)
                print(get_ref)
                get_ref=get_ref.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                if values in get_ref:
                        assert True
                else:
                        assert False
                print(values,"added in forward map zone")
                sleep(05)
                print("\nTest Case 25 Execution Completed")



            @pytest.mark.run(order=26)
            def test_026_validate_ddns_update_records_in_authoritative_reverse_mapping_zone(self):
                logging.info("validating ddns update records in authoritative reverse mapping zone")
                out1 = str(config.member_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                output1 = re.search('debug Lease on(.*)preferred for 27000s', log_validation)
                output1 = output1.group(0)
                print(output1)
                def Convert(string):
                    li = list(string.split(" "))
                    return li
                str1 = Convert(output1)
                Name = str1[5]
                Name = Name.replace('(','').replace(')','')
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:ptr", grid_vip=config.grid_vip)
                print(get_ref)
                get_ref=get_ref.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                result = ('ptrdname:'+Name)
                if result in get_ref:
                    assert True
                else:
                    assert False
                print(result,"added in reverse map zone")
                sleep(05)
                print("\nTest Case 26 Execution Completed")



            @pytest.mark.run(order=27)
            def test_027_delete_the_lease(self):
                logging.info("deleting the ipv6 lease")
                out1 = str(config.member_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                output1 = re.search('debug Lease on(.*)preferred for 27000s',log_validation)
                output1 = output1.group(0)
                print(output1)
                def Convert(string):
                    li = list(string.split(" "))
                    return li
                str1 = Convert(output1)
                Lease_IPv6 = str1[4]
                get_ref = ib_NIOS.wapi_request('GET', object_type="lease", grid_vip=config.grid_vip)
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[-1]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
                print(output)
                sleep(05)
                print("\nTest Case 27 Execution Completed")


            @pytest.mark.run(order=28)
            def test_028_validate_the_deleted_lease_and_state(self):
                logging.info("validating the deleted lease state")
                get_ref = ib_NIOS.wapi_request('GET', object_type="lease", grid_vip=config.grid_vip)
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[-1]['_ref']
                #print(ref1)
                response = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=binding_state",grid_vip=config.grid_vip)
                print(response)
                #value = '"binding_state": "FREE"'
                #if value in response:
                #    assert True
                #else:
                #    assert False
                #print(value)
                sleep(05)
                print("\nTest Case 28 Execution Completed")
           

####################################################
#### DDNS Updates testing with other member ########
####################################################


            @pytest.mark.run(order=29)
            def test_029_Add_authoritative_forward_mapping_zone_and_restart_the_grid_services(self):
                logging.info("adding authoritative forward-mapping zone and_restarting the grid services")
                data = {"fqdn": "test1.com","view": "default","grid_primary": [{"name": config.grid_member1_fqdn,"stealth": False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 29 Execution Completed")
	    
            @pytest.mark.run(order=30)
            def test_030_Validate_authoritative_forward_mapping_zone(self):
                logging.info("validating authoritative forward-mapping zone")
                #get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
		get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth?fqdn=test1.com",grid_vip=config.grid_vip)
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[-1]['_ref']
                #print(ref1)
                output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=grid_primary,fqdn" , grid_vip=config.grid_vip)
                output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','').replace('[','').replace(']','')
                #print(output)
                result = ['fqdn:test1.com','grid_primary:name:'+config.grid_member1_fqdn,'stealth:false']
                for string in result:
                    if string in output:
                        assert True
                    else:
                        assert False
                print(result)
                print("Test Case 30 Executuion Completed")
	    
            @pytest.mark.run(order=31)
            def test_031_Add_Authoritative_reverse_mapping_zone(self):
                logging.info("adding authoritative reverse mapping zone")
		global v6_network
		v6_network = ipv6_network.replace((ipv6_network[-3]),str(int(ipv6_network[-3])-1))
		print(v6_network)
                data = {"fqdn": v6_network+"::/64","zone_format": "IPV6","grid_primary": [{"name": config.grid_member1_fqdn,"stealth": False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 31 Execution Completed")

            @pytest.mark.run(order=32)
            def test_032_Validate_authoritative_reverse_mapping_zone(self):
                logging.info("validating authoritative reverse mapping zone")
                get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[-1]['_ref']
                output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=grid_primary,fqdn,zone_format",grid_vip=config.grid_vip)
                print(output)
                output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','').replace('[','').replace(']','')
                result = ['fqdn:'+v6_network+'::/64','grid_primary:name:'+config.grid_member1_fqdn,'zone_format:IPV6']
                for string in result:
                    if string in output:
                        assert True
                    else:
                        assert False
                print(result)
                print("\nTest Case 32 Executuion Completed")

	    
            @pytest.mark.run(order=33)
            def test_033_create_IPv6_address_Range(self):
                logging.info("Creating ipv6 address range")
                data ={"end_addr": ipv6_network+"::200","network": ipv6_network+"::/64","network_view": "default","start_addr": ipv6_network+"::101","member": {"_struct": "dhcpmember","ipv6addr": config.member1_ipv6,"name": config.grid_member1_fqdn,"_struct": "dhcpmember","ipv6addr": config.member1_ipv6,"name": config.grid_member1_fqdn}}
                response = ib_NIOS.wapi_request('POST', object_type="ipv6range", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 33 Execution Completed")

	    
            @pytest.mark.run(order=34)
            def test_034_Validate_created_range(self):
                logging.info("validating the created range")
                get_ref =  ib_NIOS.wapi_request('GET', object_type="ipv6range", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[-1]['_ref']
                ref = eval(json.dumps(ref))
                response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=member,end_addr,start_addr",grid_vip=config.grid_vip)
                print(response)
                output = ['"ipv6addr": "'+config.member1_ipv6+'"','"name": "'+config.grid_member1_fqdn+'"','"end_addr": "'+ipv6_network+"::200",'"start_addr": "'+ipv6_network+"::101"]
		print(output)
                for values in output:
                    if values in response:
                        assert True
			print(values)
                    else:
                        assert False
                print(output)
                print("\nTest Case 34 Execution Completed")



############################################
## will do dras requests on other member  ##
############################################


            @pytest.mark.run(order=35)
            def test_035_Add_second_member_assigned_zone_at_ipv6_ddns_domainname_and_ipv6_domain_name_and_ipv6_domain_name_servers(self):
                logging.info("adding second member assigned zone at ipv6_ddns_domainname ipv6_domain_name ipv6_domain_name_servers")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                data = {"ipv6_ddns_domainname": "test1.com","ipv6_domain_name": "test1.com","ipv6_domain_name_servers": [config.member1_ipv6]  }
                response1 = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response1)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 35 Execution Completed")


            @pytest.mark.run(order=36)
            def test_036_validate_second_member_assigned_zone_at_ipv6_ddns_domainname_and_ipv6_domain_name_and_ipv6_domain_name_servers(self):
                logging.info("validating second member assigned zone at ipv6_ddns_domainname ipv6_domain_name ipv6_domain_name_servers")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                print(ref)
                response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=ipv6_ddns_domainname,ipv6_domain_name,ipv6_domain_name_servers",grid_vip=config.grid_vip)
                print(response)
                response=response.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','').replace('[','').replace(']','')
                output = ['ipv6_domain_name_servers:'+config.member1_ipv6,'ipv6_ddns_domainname:test1.com','ipv6_domain_name:test1.com']
                for values in output:
                    if values in response:
                        assert True
                    else:
                        assert False
                print(output)
                sleep(120)  #Giving sleep time to work fastly in log validation cases 
                print("Test CAse 36 Execution Completed")
	    

            @pytest.mark.run(order=37)
            def test_037_start_the_logs_and_request_ipv6_lease_with_hostand_and_mac_address_and_stop_the_logs(self):
                logging.info("Performing dras command")
                log("start","/var/log/syslog",config.member1_ipv6)
                sleep(30)
                for i in range(10):
                    dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.member1_ipv6)+' '+'-A -n 1 -h test1.com -a 77:77:77:77:77:82'
                    dras_cmd1 = os.system(dras_cmd)
                    print("output is ",dras_cmd1)
                    if dras_cmd1 == 0:
                        print("got the lease")
                        break
                    else:
                        print("didn't get the lease and continuing for lease")
                ping = ('for i in range{1..2} ; do ping6 -i 1 -c 5 '+config.member1_ipv6+' ; done')
                data = os.popen(ping).read()
                print(data)
                sleep(300)
                log("stop","/var/log/syslog",config.member1_ipv6)
                print("\nTest Case 37 Executed Successfully")



            @pytest.mark.run(order=38)
            def test_038_validate_ipv6_lease_in_leases(self):
                logging.info("validating the ipv6 lease in leases")
                out1 = str(config.member1_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                #print(log_validation)
                output1 = re.search('debug Lease on(.*)preferred for 27000s', log_validation)
                output1 = output1.group(0)
                print(output1)
                def Convert(string):
                    li = list(string.split(" "))
                    return li
                str1 = Convert(output1)
                Lease_IPv6 = str1[4]
                print(Lease_IPv6)
                get_ref = ib_NIOS.wapi_request('GET', object_type="lease", grid_vip=config.grid_vip)
                print(get_ref)
                response = get_ref
                print(response)
                values = '"address": "'+Lease_IPv6+'"'
                if values in response:
                        assert True
                else:
                        assert False
                print(values)
                print("\ntest Case 38 Executed Successfully")

            @pytest.mark.run(order=39)
            def test_039_validate_the_ipv6_lease_and_hostname_in_var_log_messages(self):
                logging.info("validating the ipv6 lease and hostname in var log messages")
                out1 = str(config.member1_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
		print(log_validation)
                output1 = re.search('debug Lease on(.*)preferred for 27000s',log_validation)
                output1 = output1.group(0)
                print(output1)
                host_name = 'h777777777782.test1.com'
                if 'h777777777782.test1.com' in output1:
                        assert True
                else:
                        assert False
                print("\nTest Case 39 Executed Successfully")


            @pytest.mark.run(order=40)
            def test_040_validate_ddns_update_records_in_authoritative_forward_mapping_zone_and_authoritative_reverse_mapping_zone(self):
                logging.info("validating ddns update records in authoritative forward mapping zone and authoritative reverse mapping zone")
                out1 = str(config.member1_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                output1 = re.search('debug Lease on(.*)preferred for 27000s', log_validation)
                output1 = output1.group(0)
                print(output1)
                def Convert(string):
                    li = list(string.split(" "))
                    return li
                str1 = Convert(output1)
                Lease_IPv6 = str1[4]
                Name = str1[5]
                Name = Name.replace('(','').replace(')','')
                values = ['ipv6addr:'+Lease_IPv6,'name:'+Name]
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:aaaa", grid_vip=config.grid_vip)
                print(get_ref)
                get_ref=get_ref.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                for output in values:
                    if output in get_ref:
                        assert True
                    else:
                        assert False
                print(values,"added in forward map zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:ptr", grid_vip=config.grid_vip)
                print(get_ref)
                get_ref=get_ref.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                result = ('ptrdname:'+Name)
                if result in (get_ref):
                    assert True
                else:
                    assert False
                print(result,"added in reverse map zone")
                print("\nTest Case 40 Execution Completed")


##############################################################################
##### Override scenarios at member and ipv6 network level ####################
##############################################################################

            @pytest.mark.run(order=41)
            def test_041_Add_ipv6_ddns_domainname_and_ipv6_domain_name_and_ipv6_domain_name_servers_at_member_level(self):
                logging.info(" adding ipv6 ddns domain name and ipv6 domain name and ipv6 domain name servers at grid level ")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[-1]['_ref']
                print(ref)
                data = {"ipv6_enable_ddns": True}
                response1 = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response1)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 41 Execution Comleted")

            @pytest.mark.run(order=42)
            def test_042_Add_ipv6_ddns_domainname_and_ipv6_domain_name_and_ipv6_domain_name_servers_at_member_level(self):
                logging.info(" adding ipv6 ddns domain name and ipv6 domain name and ipv6 domain name servers at grid level ")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[-1]['_ref']
                print(ref)
                response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=ipv6_enable_ddns",grid_vip=config.grid_vip)
                print(response)
                value = '"ipv6_enable_ddns": true'
                if value in response:
                    assert True
                else:
                    assert False
                print(value)
                print("\nTest Case 42 Execution Completed")
 

 
            @pytest.mark.run(order=43)
            def test_043_Add_ipv6_ddns_domainname_and_ipv6_domain_name_and_ipv6_domain_name_servers_at_member_level(self):
                logging.info(" adding ipv6 ddns domain name and ipv6 domain name and ipv6 domain name servers at grid level ")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[-1]['_ref']
                print(ref)
                data = {"ipv6_ddns_domainname": "test.com","ipv6_domain_name": "test.com","ipv6_domain_name_servers": [config.member_ipv6] }
                response1 = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response1)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 43 Execution Completed")


            @pytest.mark.run(order=44)
            def test_044_Validate_added_ipv6_ddns_domainname_and_ipv6_domain_name_and_ipv6_domain_name_servers_at_member_level(self):
                logging.info("validating added ipv6 ddns domain name and ipv6 domain name and ipv6 domain name servers at member level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[-1]['_ref']
                #print(ref)
                response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=ipv6_ddns_domainname,ipv6_domain_name,ipv6_domain_name_servers",grid_vip=config.grid_vip)
                print(response)
                response=response.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','').replace('[','').replace(']','')
                output = ['ipv6_domain_name_servers:'+config.member_ipv6,'ipv6_ddns_domainname:test.com','ipv6_domain_name:test.com']
                for values in output:
                    if values in response:
                        assert True
                    else:
                        assert False
                print(output)
                sleep(80)
                print("Test CAse 44 Execution Completed")

            @pytest.mark.run(order=45)
            def test_045_start_the_logs_and_request_ipv6_lease_with_hostand_and_mac_address_and_stop_the_logs(self):
                logging.info("Perform dras command")
                log("start","/var/log/syslog",config.member_ipv6)
		sleep(60)
		for i in range(10):
		    #dras_cmd = 'sudo /root/dras6/./dras6 -i'+str(config.member_ipv6)+' '+'-A -n 1 -h test.com -a 77:77:77:77:77:80'
		    dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.member_ipv6)+' '+'-A -n 1 -h test.com -a 77:77:77:77:77:80'
		    dras_cmd1 = os.system(dras_cmd)
		    print("output is ",dras_cmd1)
                    if dras_cmd1 == 0:
                        print("got the lease")
                        break
                    else:
                        print("didn't get the lease and continuing for lease")
		sleep(300)
                log("stop","/var/log/syslog",config.member_ipv6)
                print("\nTest Case 45 Executed Successfully")


            @pytest.mark.run(order=46)
            def test_046_validating_ipv6_lease_and_status_of_the_lease(self):
                logging.info("validating the lease and status of the lease")
                out1 = str(config.member_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                #print(log_validation)
                output1 = re.search('debug Lease on(.*)preferred for 27000s', log_validation)
                output1 = output1.group(0)
                print(output1)
                def Convert(string):
                    li = list(string.split(" "))
                    return li
                str1 = Convert(output1)
                Lease_IPv6 = str1[4]
                print(Lease_IPv6)
                get_ref = ib_NIOS.wapi_request('GET', object_type="lease", grid_vip=config.grid_vip)
                print(get_ref)
                response = get_ref
                print(response)
                values = '"address": "'+Lease_IPv6+'"'
                if values in response:
                        assert True
                else:
                        assert False
                print(values)
                sleep(5)
                print("\ntest Case 46 Executed Successfully")

            @pytest.mark.run(order=47)
            def test_047_validate_the_ipv6_lease_and_hostname_in_var_log_messages(self):
                logging.info("validating the ipv6 lease and hostname in var log messages")
                out1 = str(config.member_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                output = re.search('debug Lease on(.*)preferred for 27000s',log_validation)
                output = output.group(0)
                print(output)
                host_name = 'h777777777780.test.com'
                if 'h777777777780.test.com' in output:
                        assert True
                else:
                        assert False
                sleep(5)
                print("\nTest Case 47 Executed Successfully")


            @pytest.mark.run(order=48)
            def test_048_validate_ddns_update_records_in_authoritative_forward_mapping_zone_and_authoritative_reverse_mapping_zone(self):
                logging.info("Checking the GMC status with dummy offline GMC and validating the error message")
                out1 = str(config.member_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                output1 = re.search('debug Lease on(.*)preferred for 27000s', log_validation)
                output1 = output1.group(0)
                print(output1)
                def Convert(string):
                    li = list(string.split(" "))
                    return li
                str1 = Convert(output1)
                Lease_IPv6 = str1[4]
                Name = str1[5]
                Name = Name.replace('(','').replace(')','')
                values = ['ipv6addr:'+Lease_IPv6,'name:'+Name]
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:aaaa", grid_vip=config.grid_vip)
                print(get_ref)
                get_ref=get_ref.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                for output in values:
                    if output in get_ref:
                        assert True
                    else:
                        assert False
                sleep(5)
                print(values,"added in forward map zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:ptr", grid_vip=config.grid_vip)
                print(get_ref)
                get_ref=get_ref.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                result = ('ptrdname:'+Name)
                if result in (get_ref):
                    assert True
                else:
                    assert False
                print(result,"added in reverse map zone")
                sleep(5)
                print("\nTest Case 48 Execution Completed")

################################################
###  Override ddns scenarios at ipv6network ####
################################################

            @pytest.mark.run(order=49)
            def test_049_Add_ddns_domainname_and_domain_name_and_domain_name_servers_at_ipv6network(self):
                logging.info("adding ipv6 ddns domainname and ipv6 domain name and ipv6 domain name servers at ipv6network")
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6network", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                print(ref)
                data = {"ddns_domainname": "test1.com","domain_name": "test1.com","domain_name_servers": [config.member1_ipv6]}
                response1 = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response1)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 49 Execution Completed")


            @pytest.mark.run(order=50)
            def test_050_Validate_domain_name_and_domain_name_servers_at_ipv6networke(self):
                logging.info("validating domainname and domain name servers at ipv6network")
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6network", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[-1]['_ref']
                response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=domain_name,domain_name_servers",grid_vip=config.grid_vip)
                print(response)
                response=response.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','').replace('[','').replace(']','')
                output = ['value:'+config.member1_ipv6,'value:test1.com']
                print(output)
                for values in output:
                    if values in response:
                        assert True
                    else:
                        assert False
                print(output)
                sleep(5)
                print("\nTest Case 50 Execution Completed")


            @pytest.mark.run(order=51)
            def test_051_Validate_ddns_domainname_at_ipv6network(self):
                logging.info(" ")
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6network", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[-1]['_ref']
                response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=ddns_domainname",grid_vip=config.grid_vip)
                print(response)
                output = ['"value": "test1.com"','"inherited": true']
                for values in output:
                    if values in response:
                        assert True
                    else:
                        assert False
                print(output)
                sleep(5)
                print("Test CAse 51 Execution Completed")

            @pytest.mark.run(order=52)
            def test_052_start_the_logs_and_request_ipv6_lease_with_hostand_and_mac_address_and_stop_the_logs(self):
                logging.info("Performing dras command")
                log("start","/var/log/syslog",config.member1_ipv6)
		sleep(10)
		for i in range(10):
		    #dras_cmd = 'sudo /root/dras6/./dras6 -i '+str(config.member1_ipv6)+' '+'-A -n 1 -h test1.com -a 77:77:77:77:77:86'
		    dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.member1_ipv6)+' '+'-A -n 1 -h test1.com -a 77:77:77:77:77:86'
		    dras_cmd1 = os.system(dras_cmd)
		    print("output is ",dras_cmd1)
		    if dras_cmd1 == 0:
			print("got the lease")
			break
		    else:
		        print("didn't get the lease and continuing for lease")
		sleep(200)
                log("stop","/var/log/syslog",config.member1_ipv6)
                print("\nTest Case 52 Executed Successfully")


            @pytest.mark.run(order=53)
            def test_053_validate_ipv6_lease_in_leases(self):
                logging.info("validating the ipv6 lease in leases")
                out1 = str(config.member1_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                #print(log_validation)
                output1 = re.search('debug Lease on(.*)preferred for 27000s', log_validation)
                output1 = output1.group(0)
                print(output1)
                def Convert(string):
                    li = list(string.split(" "))
                    return li
                str1 = Convert(output1)
                Lease_IPv6 = str1[4]
                print(Lease_IPv6)
                get_ref = ib_NIOS.wapi_request('GET', object_type="lease", grid_vip=config.grid_vip)
                print(get_ref)
                response = get_ref
                print(response)
                values = '"address": "'+Lease_IPv6+'"'
                if values in response:
                        assert True
                else:
                        assert False
                print(values)
                sleep(5)
                print("\ntest Case 53 Executed Successfully")


            @pytest.mark.run(order=54)
            def test_054_validate_the_ipv6_lease_and_hostname_in_var_log_messages(self):
                logging.info("validating the ipv6 lease and hostname in var log messages")
                out1 = str(config.member1_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                output1 = re.search('debug Lease on(.*)preferred for 27000s',log_validation)
                output1 = output1.group(0)
                print(output1)
                #output2 = re.search('Added new forward map from(.*)2620:10a:6000:2500',log_validation)
		output2 = re.search('Added new forward map from(.*)::',log_validation)
                output2 = output2.group(0)
                print(output2)
                output3 = re.search('Added reverse map from(.*)test1.com',log_validation)
                output3 = output3.group(0)
                print(output3)
                host_name = 'h777777777786.test1.com'
                output = (output1,output2,output3)
                for values in output:
                    if host_name in values:
                        assert True
                    else:
                        assert False
                print(host_name)
                sleep(5)
                print("\nTest Case 54 Executed Successfully")


            @pytest.mark.run(order=55)
            def test_055_validate_ddns_update_records_in_authoritative_forward_mapping_zone_and_authoritative_reverse_mapping_zone(self):
                logging.info("validating ddns update records in authoritative forward mapping zone and authoritative reverse mapping zone")
                out1 = str(config.member1_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                output1 = re.search('debug Lease on(.*)preferred for 27000s', log_validation)
                output1 = output1.group(0)
                print(output1)
                def Convert(string):
                    li = list(string.split(" "))
                    return li
                str1 = Convert(output1)
                Lease_IPv6 = str1[4]
                Name = str1[5]
                Name = Name.replace('(','').replace(')','')
                values = ['ipv6addr:'+Lease_IPv6,'name:'+Name]
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:aaaa", grid_vip=config.grid_vip)
                print(get_ref)
                get_ref=get_ref.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                for output in values:
                    if output in get_ref:
                        assert True
                    else:
                        assert False
                print(values,"added in forward map zone")
                sleep(5)
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:ptr", grid_vip=config.grid_vip)
                print(get_ref)
                get_ref=get_ref.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                result = ('ptrdname:'+Name)
                if result in (get_ref):
                    assert True
                else:
                    assert False
                print(result,"added in reverse map zone")
                sleep(5)
                print("\nTest Case 55 Execution Completed")



            @pytest.mark.run(order=56)
            def test_056_Change_the_preferred_lifetime_and_valid_lifetime(self):
                logging.info("changing the preferred lifetime and valid lifetime")
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6network", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                print(ref)
                data = {"preferred_lifetime": 50,"valid_lifetime": 60}
                response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 56 Execution Completed")
      

            @pytest.mark.run(order=57)
            def test_057_Validate_preferred_lifetime_and_valid_lifetime(self):
                logging.info("validating preferred lifetime an valid lifetime")
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6network", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                #print(ref)
                response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=preferred_lifetime,valid_lifetime",grid_vip=config.grid_vip)
                print(response)
                output = ['"value": 50','"value": 60']
                for values in output:
                    if values in response:
                        assert True
                    else:
                        assert False
                print(output)
                print("\nTest Case 57 Execution Completed")

            @pytest.mark.run(order=58)
            def test_058_start_the_logs_and_request_ipv6_lease_with_hostand_and_mac_address_and_stop_the_logs(self):
                logging.info("Performing dras command")
                log("start","/var/log/syslog",config.member1_ipv6)
		sleep(10)
                for i in range(10):
		    #dras_cmd = 'sudo /root/dras6/./dras6 -i '+str(config.member1_ipv6)+' '+'-A -n 1 -h test1.com -a 77:77:77:77:77:17'
		    dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.member1_ipv6)+' '+'-A -n 1 -h test1.com -a 77:77:77:77:77:17'
	            dras_cmd1 = os.system(dras_cmd)
		    print("output is ",dras_cmd1)
		    if dras_cmd1 == 0:
			print("got the lease")
			break
		    else:
			print("didn't get the lease and continuing for lease")
                sleep(100)
                log("stop","/var/log/syslog",config.member1_ipv6)
                print("\nTest Case 58 Executed Successfully")

            @pytest.mark.run(order=59)
            def test_059_validate_the_ipv6_lease_and_hostname_in_var_log_messages(self):
                logging.info("validating the ipv6 lease and hostname in var log messages")
                out1 = str(config.member1_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                output1 = re.search('debug Lease on(.*)preferred for 50s',log_validation)
                output1 = output1.group(0)
                print(output1)
                #output2 = re.search('Added new forward map from(.*)2620:10a:6000:2500',log_validation)
		output2 = re.search('Added new forward map from(.*)::',log_validation)
                output2 = output2.group(0)
                print(output2)
                output3 = re.search('Added reverse map from(.*)test1.com',log_validation)
                output3 = output3.group(0)
                print(output3)
                host_name = 'h777777777717.test1.com'
                output = (output1,output2,output3)
                for values in output:
                    if host_name in values:
                        assert True
                    else:
                        assert False
                print(host_name)
                print("\nTest Case 59 Executed Successfully")


            @pytest.mark.run(order=60)
            def test_060_Validate_records_deleted_message_in_var_log_messages_after_lease_expired(self):
                logging.info(" validating ddns update records deleted message in var log messages after lease expired")
                out1 = str(config.member1_ipv6+'_var_log_messages')
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                sleep(05)
                output = ['Removed forward map','Removed reverse map']
                for values in output:
                    if values in log_validation:
                        assert True
                    else:
                        assert False
                print(output)
                print('Test Case 60 Executed Successfully')
       

            @pytest.mark.run(order=61)
            def test_061_Validate_lease_state_after_lease_expires(self):
                logging.info("validating lease state after lease expires")
                out1 = str(config.member1_ipv6+'_var_log_messages')
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                #sleep(30)
                output1 = re.search('debug Lease on(.*)preferred for 50s', log_validation)
                output1 = output1.group(0)
                print('\n')
                print(output1)
                def Convert(string):
                    li = list(string.split(" "))
                    return li
                str1 = Convert(output1)
                Lease_IPv6 = str1[4]
                get_ref = ib_NIOS.wapi_request('GET', object_type="lease", grid_vip=config.grid_vip)
                ref = json.loads(get_ref)[-1]['_ref']
                response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=binding_state,address",grid_vip=config.grid_vip)
                print(response)
                #output = ['"address": "'+Lease_IPv6+'"','"binding_state": "EXPIRED"']
                #for values in output:
                #    if values in response:
                #        assert True
                #    else:
                #        assert False
                #print(output)
                print("\nTest Case 61 Executed Successfully")

            @pytest.mark.run(order=62)
            def test_062_validate_ddns_update_records_in_authoritative_forward_mapping_zone_and_authoritative_reverse_mapping_zone(self):
                logging.info("validating ddns update records in authoritative forward mapping zone and authoritative reverse mapping zone")
                out1 = str(config.member1_ipv6+'_var_log_messages')
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                output1 = re.search('debug Lease on(.*)preferred for 50s', log_validation)
                output1 = output1.group(0)
                print(output1)
                def Convert(string):
                    li = list(string.split(" "))
                    return li
                str1 = Convert(output1)
                Lease_IPv6 = str1[4]
                print(Lease_IPv6)
                Name = str1[5]
                Name = Name.replace('(','').replace(')','')
                print(Name)
                values = ['"ipv6addr": "'+Lease_IPv6+'"','"name": "'+Name+'"']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:aaaa", grid_vip=config.grid_vip)
                print(get_ref)
                for output in values:
                    if output in get_ref:
                        assert False
                    else:
                        assert True
                print(values,"Expired records got deleted from forward map zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:ptr", grid_vip=config.grid_vip)
                print(get_ref)
                result = ('"ptrdname": "'+Name+'"')
                if result in (get_ref):
                    assert False
                else:
                    assert True
                print(result,"Expired records got deleted from reverse map zone")
                print("\nTest Case 62 Execution Completed")



#######################################################################
##### Setting options to Inherit Values from GRID #####################
#######################################################################

            @pytest.mark.run(order=63)
            def test_063_Changing_the_use_ddns_domainname_and_use_domain_name_and_use_domain_name_servers_and_use_valid_lifetime_to_get_values_from_grid_level(self):
                logging.info("changing the use_ddns_domainname and use_domain_name and use_domain_name_servers and use_valid_lifetime at grid level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6network", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                print(ref)
                data = {"use_ddns_domainname": False,"use_domain_name": False,"use_domain_name_servers": False,"use_preferred_lifetime": False,"use_valid_lifetime": False}
                response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data), grid_vip=config.grid_vip) 
                print(response)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 63 Execution Completed")

            @pytest.mark.run(order=64)
            def test_064_Validating_use_ddns_domainname_and_use_domain_name_and_use_domain_name_servers_and_use_valid_lifetime_at_ipv6network_level(self):
                logging.info("validating use_ddns_domainname and use_domain_name and use_domain_name_servers and use_valid_lifetime at ipv6network level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6network", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                print(ref)
                response1 = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=use_ddns_domainname,use_domain_name,use_domain_name_servers,use_preferred_lifetime,use_valid_lifetime",grid_vip=config.grid_vip)
                print(response1)
                output = ['"use_ddns_domainname": false','"use_domain_name": false','"use_domain_name_servers": false','"use_preferred_lifetime": false','"use_valid_lifetime": false']
                for values in output:
                    if values in response1:
                        assert True
                    else:
                        assert False
                print(output)
                sleep(5)
                print("\nTest Case 64 Execution Completed")

            @pytest.mark.run(order=65)
            def test_065_Changing_the_use_ipv6_ddns_domainname_and_use_ipv6_domain_name_and_use_ipv6_domain_name_servers_to_get_values_from_grid_level(self):
                logging.info("changing the use_ipv6_ddns_domainname and use_ipv6_domain_name and use_ipv6_domain_name_servers at member level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[1]['_ref']
                print(ref)
                data = {"use_ipv6_ddns_domainname": False,"use_ipv6_domain_name": False,"use_ipv6_domain_name_servers": False}
                response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 65 Execution Completed") 

            @pytest.mark.run(order=66)
            def test_066_Validating_the_use_ipv6_ddns_domainname_and_use_ipv6_domain_name_and_use_ipv6_domain_name_servers_at_member_level(self):
                logging.info("adding authority zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[1]['_ref']
                print(ref)
                response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=use_ipv6_ddns_domainname,use_ipv6_domain_name,use_ipv6_domain_name_servers",grid_vip=config.grid_vip)
                print(response)
                output = ['"use_ipv6_ddns_domainname": false','"use_ipv6_domain_name": false','"use_ipv6_domain_name_servers": false']
                for values in output:
                    if values in response:
                        assert True
                    else:
                        assert False
                print(output)
                sleep(5)
                print("\nTest Case 66 Execution Completed")



#####################################################
## Testing with different CIDR scenario #############
#####################################################

            @pytest.mark.run(order=67)
            def test_067_Delete_IPv6_network(self):
                logging.info("deleting ipv6 network")
                get_ref = ib_NIOS.wapi_request('GET',object_type="ipv6network",grid_vip=config.grid_vip)
                print(get_ref)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                response = ib_NIOS.wapi_request('DELETE',ref=ref,grid_vip=config.grid_vip)
                print(response)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 67 Execution Completed")

            @pytest.mark.run(order=68)
            def test_068_Add_IPv6_network_with_members_assignment(self):
                logging.info("Create an ipv6 network default network view")
                data = {"network": ipv6_network+"::/63","network_view": "default","members": [{"_struct": "dhcpmember","ipv6addr": config.member_ipv6,"name": config.grid_member2_fqdn},{"_struct": "dhcpmember","ipv6addr": config.member1_ipv6,"name": config.grid_member1_fqdn}]}
                print(data)
                response = ib_NIOS.wapi_request('POST', object_type="ipv6network", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20)
                print("Test Case 68 Execution Completed")
	    
            @pytest.mark.run(order=69)
            def test_069_validate__IPv6_network(self):
                logging.info("validating created ipv6 network")
                output = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=members,network",grid_vip=config.grid_vip)
                print(output)
		ref = json.loads(output)[0]['_ref']
		print(ref)
                result = ['"ipv4addr": null','"ipv6addr": "'+config.member_ipv6+'"','"name": "'+config.grid_member2_fqdn+'"','"ipv6addr": "'+config.member1_ipv6+'"','"name": "'+config.grid_member1_fqdn+'"','"network": "'+ipv6_network+"::/63"]
		print(result)
                for values in result:
                    if values in output:
                        assert True
                    else:
                        assert False
                print(result)
		data = {"name": "shared_network","network_view": "default","networks": [{"_ref": ref}]}
		response = ib_NIOS.wapi_request('POST',object_type="ipv6sharednetwork", fields=json.dumps(data), grid_vip=config.grid_vip)
		print(response)
                sleep(5)
                print("Test Case 69 Execution Completed")

            @pytest.mark.run(order=70)
            def test_070_create_IPv6_address_Range(self):
                logging.info("Creating ipv6 address range")
                data ={"end_addr": ipv6_network+"::200","network": ipv6_network+"::/63","network_view": "default","start_addr": ipv6_network+"::101","member": {"_struct": "dhcpmember","ipv6addr": config.member1_ipv6,"name": config.grid_member1_fqdn}}
                response = ib_NIOS.wapi_request('POST', object_type="ipv6range", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 70 Execution Completed")
	    
            @pytest.mark.run(order=71)
            def test_071_Validate_created_range(self):
                logging.info("validating the created range")
                get_ref =  ib_NIOS.wapi_request('GET', object_type="ipv6range", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[-1]['_ref']
                ref = eval(json.dumps(ref))
                response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=member,end_addr,start_addr",grid_vip=config.grid_vip)
                print(response)
                output = ['"ipv6addr": "'+config.member1_ipv6+'"','"name": "'+config.grid_member1_fqdn+'"','"end_addr": "'+ipv6_network+"::200",'"start_addr": "'+ipv6_network+"::101"]
                for values in output:
                    if values in response:
                        assert True
			print(values)
                    else:
                        assert False
                print(output)
                sleep(5)
                print("\nTest Case 71 Execution Completed")

            @pytest.mark.run(order=72)
            def test_072_start_the_logs_and_request_ipv6_lease_with_hostand_and_mac_address_and_stop_the_logs(self):
                logging.info("Performing dras command")
                log("start","/var/log/syslog",config.member1_ipv6)
		sleep(10)
		for i in range(10):
		    #dras_cmd = 'sudo /root/dras6/./dras6 -i '+str(config.member1_ipv6)+' '+'-A -n 1 -h test.com -a 77:77:77:77:12:12'
	            dras_cmd = 'sudo  /import/tools/qa/tools/dras6/dras6 -i '+str(config.member1_ipv6)+' '+'-A -n 1 -h test.com -a 77:77:77:77:12:12'
		    dras_cmd1 = os.system(dras_cmd)
		    print("output is ",dras_cmd1)
		    if dras_cmd1 == 0:
		        print("got the lease")
			break
		    else:
			print("didn't get the lease and continuing for lease")
                sleep(200)
                log("stop","/var/log/syslog",config.member1_ipv6)
                print("\nTest Case 72 Executed Successfully")

            @pytest.mark.run(order=73)
            def test_073_Validate_lease_in_leases(self):
                logging.info("validating the ipv6 lease in leases")
                out1 = str(config.member1_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                output1 = re.search('debug Lease on(.*)preferred for 27000s', log_validation)
                output1 = output1.group(0)
                print(output1)
                def Convert(string):
                    li = list(string.split(" "))
                    return li
                str1 = Convert(output1)
                Lease_IPv6 = str1[4]
                print(Lease_IPv6)
                get_ref = ib_NIOS.wapi_request('GET', object_type="lease", grid_vip=config.grid_vip)
                print(get_ref)
                response = get_ref
                print(response)
                values = '"address": "'+Lease_IPv6+'"'
                if values in response:
                        assert True
                else:
                        assert False
                print(values)
                sleep(5)
                print("\ntest Case 73 Executed Successfully")

            @pytest.mark.run(order=74)
            def test_074_validate_the_ipv6_lease_and_hostname_in_var_log_messages(self):
                logging.info("validating the ipv6 lease and hostname in var log messages")
                out1 = str(config.member1_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                output1 = re.search('debug Lease on(.*)preferred for 27000s',log_validation)
                output1 = output1.group(0)
                print(output1)
                #output2 = re.search('Added new forward map from(.*)2620:10a:6000:2500',log_validation)
		output2 = re.search('Added new forward map from(.*)::',log_validation)
                output2 = output2.group(0)
                print(output2)
                output3 = re.search('Added reverse map from(.*)test1.com',log_validation)
                output3 = output3.group(0)
                print(output3)
                host_name = 'h777777771212.test1.com'
                output = (output1,output2,output3)
                for values in output:
                    if host_name in values:
                        assert True
                    else:
                        assert False
                print(host_name)
                print("\nTest Case 74 Executed Successfully")

            @pytest.mark.run(order=75)
            def test_075_validate_ddns_update_records_in_authoritative_forward_mapping_zone_and_authoritative_reverse_mapping_zone(self):
                logging.info("validating ddns update records in authoritative forward mapping zone and authoritative reverse mapping zone")
                out1 = str(config.member1_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                output1 = re.search('debug Lease on(.*)preferred for 27000s', log_validation)
                output1 = output1.group(0)
                print(output1)
                def Convert(string):
                    li = list(string.split(" "))
                    return li
                str1 = Convert(output1)
                Lease_IPv6 = str1[4]
                Name = str1[5]
                Name = Name.replace('(','').replace(')','')
                values = ['ipv6addr:'+Lease_IPv6,'name:'+Name]
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:aaaa", grid_vip=config.grid_vip)
                print(get_ref)
                get_ref=get_ref.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                for output in values:
                    if output in get_ref:
                        assert True
                    else:
                        assert False
                print(values,"added in forward map zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:ptr", grid_vip=config.grid_vip)
                print(get_ref)
                get_ref=get_ref.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                result = ('ptrdname:'+Name)
                if result in (get_ref):
                    assert True
                else:
                    assert False
                print(result,"added in reverse map zone")
                print("\nTest Case 75 Execution Completed")



################################################
####### Testing DDNS Updates in Sub Zone #######
################################################

            @pytest.mark.run(order=76)
            def test_076_Add_Authoritative_forward_mapping_subzone(self):
                logging.info("adding authoritative forward mapping subzone")
                data = {"fqdn": "sub.test1.com","view": "default","grid_primary": [{"name": config.grid_member1_fqdn,"stealth": False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response) 
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 76 Execution Completed")

            @pytest.mark.run(order=77)
            def test_077_Add_Authoritative_forward_mapping_subzone(self):
                logging.info("adding authoritative forward mapping subzone")
                grid =  ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
                print(grid)
                value = '"fqdn": "sub.test1.com"'
                if value in grid:
                    assert True
                else:
                    assert False
                print(value)
                sleep(5)
                print("\nTest Case 77 Execution Completed")

            @pytest.mark.run(order=78)
            def test_078_Add_ipv6_ddns_domainname_and_ipv6_domain_name_and_ipv6_domain_name_servers_at_grid_level(self):
                logging.info("adding ipv6 ddns domain name and ipv6 domain name and ipv6 domain name servers at grid level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                data = {"ipv6_ddns_domainname": "sub.test1.com","ipv6_domain_name": "sub.test1.com","ipv6_domain_name_servers": [config.member1_ipv6]  }
                response1 = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response1)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 78 Execution Completed")

            @pytest.mark.run(order=79)
            def test_079_Validate_added_ipv6_ddns_domainname_and_ipv6_domain_name_and_ipv6_domain_name_servers_at_grid_level(self):
                logging.info("validating added ipv6 ddns domain name and ipv6 domain name and ipv6 domain name servers at grid level")
                get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[-1]['_ref']
                #print(ref1)
                output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=grid_primary,fqdn" , grid_vip=config.grid_vip)
                output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','').replace('[','').replace(']','')
                result = ['fqdn:sub.test1.com','grid_primary:name:'+config.grid_member1_fqdn,'stealth:false']
                for string in result:
                    if string in output:
                        assert True
                    else:
                        assert False
                print(result)
                print("Test Case 79 Executuion Completed")

            @pytest.mark.run(order=80)
            def test_080_start_the_logs_and_request_ipv6_lease_with_hostand_and_mac_address_and_stop_the_logs(self):
                logging.info("Performing dras command")
                log("start","/var/log/syslog",config.member1_ipv6)
		sleep(10)
		for i in range(10):
		    #dras_cmd = 'sudo /root/dras6/./dras6 -i '+str(config.member1_ipv6)+' '+'-A -n 1 -h sub.test1.com -a 77:77:77:77:77:21'
		    dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.member1_ipv6)+' '+'-A -n 1 -h sub.test1.com -a 77:77:77:77:77:21'
		    dras_cmd1 = os.system(dras_cmd)
		    print("output is ",dras_cmd1)
		    if dras_cmd1 == 0:
			print("got the lease")
			break
		    else:
			print("didn't get the lease and continuing for lease")
		ping = ('for i in range{1..2} ; do ping6 -i 1 -c 5 '+config.member1_ipv6+' ; done')
                data = os.popen(ping).read()
                print(data)
                sleep(300)
                log("stop","/var/log/syslog",config.member1_ipv6)
                print("\nTest Case 80 Executed Successfully")

            @pytest.mark.run(order=81)
            def test_081_Validate_ipv6_lease_in_leases(self):
                logging.info("Checking the GMC status with dummy offline GMC and validating the error message")
                out1 = str(config.member1_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                output1 = re.search('debug Lease on(.*)preferred for 27000s', log_validation)
                output1 = output1.group(0)
                print(output1)
                def Convert(string):
                    li = list(string.split(" "))
                    return li
                str1 = Convert(output1)
                Lease_IPv6 = str1[4]
                print(Lease_IPv6)
                get_ref = ib_NIOS.wapi_request('GET', object_type="lease", grid_vip=config.grid_vip)
                print(get_ref)
                response = get_ref
                print(response)
                values = '"address": "'+Lease_IPv6+'"'
                if values in response:
                        assert True
                else:
                        assert False
                print(values)
                print("\ntest Case 81 Executed Successfully")

            @pytest.mark.run(order=82)
            def test_082_validate_the_ipv6_lease_and_hostname_in_var_log_messages(self):
                logging.info("validating the ipv6 lease and hostname in var log messages")
                out1 = str(config.member1_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                output1 = re.search('debug Lease on(.*)preferred for 27000s',log_validation)
                output1 = output1.group(0)
                print(output1)
                #output2 = re.search('Added new forward map from(.*)2620:10a:6000:2500',log_validation)
		output2 = re.search('Added new forward map from(.*)::',log_validation)
                output2 = output2.group(0)
                print(output2)
                output3 = re.search('Added reverse map from(.*)sub.test1.com',log_validation)
                output3 = output3.group(0)
                print(output3)
                host_name = 'h777777777721.sub.test1.com'
                output = (output1,output2,output3)
                for values in output:
                    if host_name in values:
                        assert True
                    else:
                        assert False
                print(host_name)
                print("\nTest Case 82 Executed Successfully")

            @pytest.mark.run(order=83)
            def test_083_validate_ddns_update_records_in_authoritative_forward_mapping_zone_and_authoritative_reverse_mapping_zone(self):
                logging.info("validating ddns update records in authoritative forward mapping zone and authoritative reverse mapping zone")
                out1 = str(config.member1_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                output1 = re.search('debug Lease on(.*)preferred for 27000s', log_validation)
                output1 = output1.group(0)
                print(output1)
                def Convert(string):
                    li = list(string.split(" "))
                    return li
                str1 = Convert(output1)
                Lease_IPv6 = str1[4]
                Name = str1[5]
                Name = Name.replace('(','').replace(')','')
                values = ['ipv6addr:'+Lease_IPv6,'name:'+Name]
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:aaaa", grid_vip=config.grid_vip)
                print(get_ref)
                get_ref=get_ref.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                for output in values:
                    if output in get_ref:
                        assert True
                    else:
                        assert False
                print(values,"added in forward map zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:ptr", grid_vip=config.grid_vip)
                print(get_ref)
                get_ref=get_ref.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                result = ('ptrdname:'+Name)
                if result in (get_ref):
                    assert True
                else:
                    assert False
                print(result,"added in reverse map zone")
                print("\nTest Case 83 Execution Completed")



###################################################################################################
####### Scenario : After ipv6 lease expire ddns update records should be deleted from subzone #####
###################################################################################################

            @pytest.mark.run(order=84)
            def test_084_Change_the_preferred_lifetime_and_valid_lifetime_at_grid_level(self):
                logging.info("changing the preferred lifetime and valid lifetime at grid level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                print(ref)
                data = {"preferred_lifetime": 5,"valid_lifetime": 10}
                response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 84 Execution Completed")

            @pytest.mark.run(order=85)
            def test_085_Validate_changed_preferred_lifetime_and_valid_lifetime_at_grid_level(self):
                logging.info("validating changed preferred lifetime and valid lifetime at grid level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=preferred_lifetime,valid_lifetime",grid_vip=config.grid_vip)
                print(response)
                output = ['"preferred_lifetime": 5','"valid_lifetime": 10']
                for values in output:
                    if values in response:
                        assert True
                    else:
                        assert False
                print(output)
                print("\nTest Case 85 Execution Completed")

            @pytest.mark.run(order=86)
            def test_086_start_the_logs_and_request_ipv6_lease_with_hostand_and_mac_address_and_stop_the_logs(self):
                logging.info("Performing dras command")
                log("start","/var/log/syslog",config.member1_ipv6)
		sleep(10)
                for i in range(10):
        		#dras_cmd = 'sudo /root/dras6/./dras6 -i '+str(config.member1_ipv6)+' '+'-A -n 1 -h sub.test1.com -a 77:77:77:77:77:12'
		        dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.member1_ipv6)+' '+'-A -n 1 -h sub.test1.com -a 77:77:77:77:77:12'
			dras_cmd1 = os.system(dras_cmd)
			print("output is ",dras_cmd1)
			if dras_cmd1 == 0:
				print("got the lease")
				break
			else:
				print("didn't get the lease and continuing for lease")
		ping = ('for i in range{1..2} ; do ping6 -i 1 -c 5 '+config.member1_ipv6+' ; done')
                data = os.popen(ping).read()
                print(data)
                sleep(300)
                log("stop","/var/log/syslog",config.member1_ipv6)
                print("\nTest Case 86 Executed Successfully")

            @pytest.mark.run(order=87)
            def test_087_validate_the_ipv6_lease_and_hostname_in_var_log_messages(self):
                logging.info("validating the ipv6 lease and hostname in var log messages")
                out1 = str(config.member1_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                output1 = re.search('debug Lease on(.*)preferred for 5s',log_validation)
                output1 = output1.group(0)
                print(output1)
                #output2 = re.search('Added new forward map from(.*)2620:10a:6000:2500',log_validation)
		output2 = re.search('Added new forward map from(.*)::',log_validation)
                output2 = output2.group(0)
                print(output2)
                output3 = re.search('Added reverse map from(.*)test1.com',log_validation)
                output3 = output3.group(0)
                print(output3)
                host_name = 'h777777777712.sub.test1.com'
                output = (output1,output2,output3)
                for values in output:
                    if host_name in values:
                        assert True
                    else:
                        assert False
                print(host_name)
                print("\nTest Case 87 Executed Successfully")

            @pytest.mark.run(order=88)
            def test_088_Validate_records_deleted_message_in_var_log_messages_after_lease_expired(self):
                logging.info(" validating ddns update records deleted message in var log messages after lease expired")
                out1 = str(config.member1_ipv6+'_var_log_messages')
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                sleep(05)
                output = ['Removed forward map','Removed reverse map']
                for values in output:
                    if values in log_validation:
                        assert True
                    else:
                        assert False
                print(output)
                print('Test Case 88 Executed Successfully')

            @pytest.mark.run(order=89)
            def test_089_validating_lease_status_after_lease_expired(self):
                logging.info("validating lease status after lease expired")
                out1 = str(config.member1_ipv6+'_var_log_messages')
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                #sleep(30)
                output1 = re.search('debug Lease on(.*)preferred for 5s', log_validation)
                output1 = output1.group(0)
                print('\n')
                print(output1)
                def Convert(string):
                    li = list(string.split(" "))
                    return li
                str1 = Convert(output1)
                Lease_IPv6 = str1[4]
                get_ref = ib_NIOS.wapi_request('GET', object_type="lease", grid_vip=config.grid_vip)
                ref = json.loads(get_ref)[-1]['_ref']
                response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=binding_state,address",grid_vip=config.grid_vip)
                print(response)
                #output = ['"address": "'+Lease_IPv6+'"','"binding_state": "EXPIRED"']
                #for values in output:
                #    if values in response:
                #        assert True
                #    else:
                #        assert False
                #print(output)
                print("\nTest Case 89 Executed Successfully")

            @pytest.mark.run(order=90)
            def test_090_validate_ddns_update_records_in_authoritative_forward_mapping_zone_and_authoritative_reverse_mapping_zone(self):
                logging.info("validating ddns update records in authoritative forward mapping zone and authoritative reverse mapping zone")
                out1 = str(config.member1_ipv6+'_var_log_messages')
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                output1 = re.search('debug Lease on(.*)preferred for 5s', log_validation)
                output1 = output1.group(0)
                print(output1)
                def Convert(string):
                    li = list(string.split(" "))
                    return li
                str1 = Convert(output1)
                Lease_IPv6 = str1[4]
                print(Lease_IPv6)
                Name = str1[5]
                Name = Name.replace('(','').replace(')','')
                print(Name)
                values = ['"ipv6addr": "'+Lease_IPv6+'"','"name": "'+Name+'"']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:aaaa", grid_vip=config.grid_vip)
                print(get_ref)
                for output in values:
                    if output in get_ref:
                        assert False
                    else:
                        assert True
                print(values,"Expired records got deleted from forward map zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:ptr", grid_vip=config.grid_vip)
                print(get_ref)
                result = ('"ptrdname": "'+Name+'"')
                if result in (get_ref):
                    assert False
                else:
                    assert True
                print(result,"Expired records got deleted from reverse map zone")
                print("\nTest Case 90 Execution Completed")


                                                                                           
################################################################################################################
##### Creating 64 IPv6 network and changing ddns update zone from subzone to authoritative forwad mappingzone ##
################################################################################################################

            @pytest.mark.run(order=91)
            def test_091_Delet_IPv6_network(self):
		grid =  ib_NIOS.wapi_request('GET', object_type="ipv6sharednetwork",grid_vip=config.grid_vip)
                print(grid)
                grid=json.loads(grid)
                ref=grid[0]["_ref"]
                print(ref)
                request_restart = ib_NIOS.wapi_request('DELETE',object_type = ref,grid_vip=config.grid_vip)
                print(request_restart)
                logging.info("deleting ipv6 network")
                get_ref = ib_NIOS.wapi_request('GET',object_type="ipv6network",grid_vip=config.grid_vip)
                print(get_ref)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                response = ib_NIOS.wapi_request('DELETE',ref=ref,grid_vip=config.grid_vip)
                print(response)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 91 Execution Completed")
	    
            @pytest.mark.run(order=92)
            def test_092_Add_IPv6_network(self):
                logging.info("adding ipv6 network in default network view")
                #data = {"netwoork": ipv6_network+"::/64","network_view": "default","members": [{"_struct": "dhcpmember","ipv6addr": config.member_ipv6,"name": config.grid_member2_fqdn},{"_struct": "dhcpmember","ipv6addr": config.member1_ipv6,"name": config.grid_member1_fqdn}]}
		data = {"network": ipv6_network+"::/64","network_view": "default","members": [{"_struct": "dhcpmember","ipv6addr": config.member_ipv6,"name": config.grid_member2_fqdn},{"_struct": "dhcpmember","ipv6addr": config.member1_ipv6,"name": config.grid_member1_fqdn}]}
                print(data)
                response = ib_NIOS.wapi_request('POST', object_type="ipv6network", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                sleep(5)
		grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("Test Case 92 Execution Completed")
	    
            @pytest.mark.run(order=93)
            def test_093_Validate_added_IPv6_network(self):
                logging.info("creating ipv6 network")
                output = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=members,network",grid_vip=config.grid_vip)
                print(output)
                result = ['"ipv4addr": null','"ipv6addr": "'+config.member_ipv6+'"','"name": "'+config.grid_member2_fqdn+'"','"network": "'+ipv6_network+"::/64"]
                for values in result:
                    if values in output:
                        assert True
			print(values)
                    else:
                        assert False
                print(result)
                sleep(5)
                print("Test Case 93 Execution Completed")
	    
            @pytest.mark.run(order=94)
            def test_094_Add_IPv6_address_range_1(self):
                logging.info("adding ipv6 address range")
                data ={"end_addr": ipv6_network+"::100","network": ipv6_network+"::/64","network_view": "default","start_addr": ipv6_network+"::10","member": {"_struct": "dhcpmember","ipv6addr": config.member_ipv6,"name": config.grid_member2_fqdn,"_struct": "dhcpmember","ipv6addr": config.member_ipv6,"name": config.grid_member2_fqdn}}
                response = ib_NIOS.wapi_request('POST', object_type="ipv6range", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 94 Execution Completed")

            @pytest.mark.run(order=95)
            def test_095_Validate_added_IPv6_address_range_1(self):
                logging.info("validating added ipv6 address range")
                get_ref =  ib_NIOS.wapi_request('GET', object_type="ipv6range", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                ref = eval(json.dumps(ref))
                response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=member,end_addr,start_addr",grid_vip=config.grid_vip)
                print(response)
                output = ['"ipv6addr": "'+config.member_ipv6+'"','"name": "'+config.grid_member2_fqdn+'"','"end_addr": "'+ipv6_network+"::100",'"start_addr": "'+ipv6_network+"::10"]
                for values in output:
                    if values in response:
                        assert True
                    else:
                        assert False
                print(output)
                sleep(5)
                print("\nTest Case 95 Execution Completed")

            @pytest.mark.run(order=96)
            def test_096_Add_IPv6_address_Range_2(self):
                logging.info("adding ipv6 address range2")
                data ={"end_addr": ipv6_network+"::200","network": ipv6_network+"::/64","network_view": "default","start_addr": ipv6_network+"::101","member": {"_struct": "dhcpmember","ipv6addr": config.member1_ipv6,"name": config.grid_member1_fqdn,"_struct": "dhcpmember","ipv6addr": config.member1_ipv6,"name": config.grid_member1_fqdn}}
                response = ib_NIOS.wapi_request('POST', object_type="ipv6range", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 96 Execution Completed")

            @pytest.mark.run(order=97)
            def test_097_Validate_added_IPv6_address_range_2(self):
                logging.info("validating added ipv6 address range2")
                get_ref =  ib_NIOS.wapi_request('GET', object_type="ipv6range", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[-1]['_ref']
                ref = eval(json.dumps(ref))
                response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=member,end_addr,start_addr",grid_vip=config.grid_vip)
                print(response)
                output = ['"ipv6addr": "'+config.member1_ipv6+'"','"name": "'+config.grid_member1_fqdn+'"','"end_addr": "'+ipv6_network+"::200",'"start_addr": "'+ipv6_network+"::101"]
                for values in output:
                    if values in response:
                        assert True
                    else:
                        assert False
                print(output)
                sleep(5)
                print("\nTest Case 97 Execution Completed")

            @pytest.mark.run(order=98)
            def test_098_Add_ipv6_ddns_domainname_and_ipv6_domain_name_and_ipv6_domain_name_servers_at_grid_level(self):
                logging.info("adding ipv6 ddns domain name and ipv6 domain name and ipv6 domain name servers at grid level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                data = {"ipv6_ddns_domainname": "test1.com","ipv6_domain_name": "test1.com","ipv6_domain_name_servers": [config.member1_ipv6]  }
                response1 = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response1)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 98 Execution Completed")

            @pytest.mark.run(order=99)
            def test_099_Validate_added_ipv6_ddns_domainname_and_ipv6_domain_name_and_ipv6_domain_name_servers_at_grid_level(self):
		logging.info("validating added ipv6 ddns domain name and ipv6 domain name and ipv6 domain name servers at grid level")
                output = ib_NIOS.wapi_request('GET',object_type="grid:dhcpproperties",params="?_inheritance=True&_return_fields=ipv6_ddns_domainname,ipv6_domain_name,ipv6_domain_name_servers",grid_vip=config.grid_vip)
                print(output)
                output = output.replace('\n','').replace(' ','')
                result = ['"ipv6_ddns_domainname":"test1.com"','"ipv6_domain_name":"test1.com"','"ipv6_domain_name_servers":["'+config.member1_ipv6+'"]']
                for values in result:
                    if values in output:
                        assert True
                    else:
                        assert False
                print(result)
                sleep(5)
                print("Test Case 99 Executuion Completed")

            @pytest.mark.run(order=100)
            def test_100_Change_the_preferred_lifetime_and_valid_lifetime_at_grid_level(self):
                logging.info("changing the preferred lifetime and valid lifetime at grid level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                print(ref)
                data = {"preferred_lifetime": 27000,"valid_lifetime": 43200}
                response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 100 Execution Completed")

            @pytest.mark.run(order=101)
            def test_101_Validate_changed_preferred_lifetime_and_valid_lifetime_at_grid_level(self):
                logging.info("validating changed preferred lifetime and valid lifetime at grid level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=preferred_lifetime,valid_lifetime",grid_vip=config.grid_vip)
                print(response)
                output = ['"preferred_lifetime": 27000','"valid_lifetime": 43200']
                for values in output:
                    if values in response:
                        assert True
                    else:
                        assert False
                print(output)
                print("\nTest Case 101 Execution Completed")



########################################################################
# Scenario : Disabling zone and DDNS Updates should be deffered ########
########################################################################
	    
            @pytest.mark.run(order=102)
            def test_102_Disable_authoritative_forward_mapping_zone(self):
                logging.info("disabling authoritative forward mapping zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
                #print(get_ref)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[2]['_ref']
                print(ref)
		get_ref1 = ib_NIOS.wapi_request('GET', "zone_auth?fqdn=test1.com", grid_vip=config.grid_vip)
		ref1 = json.loads(get_ref1)[0]['_ref']
		ref1 = eval(json.dumps(ref1))  
		print(ref1)
                data = {"disable": True}
                response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
		response1 = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response1)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 102 Execution Completed")

            @pytest.mark.run(order=103)
            def test_103_Validating_disabled_authoritative_forward_mapping_zone(self):
                logging.info("validating disabled authoritative forward mapping zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
                print(get_ref)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[2]['_ref']
                print(ref)
                grid =  ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=disable",grid_vip=config.grid_vip)
                print(grid)
                value = '"disable": true' 
                if value in grid:
                    assert True
                else:
                    assert False
                print(value)
                print("\nTest Case 103 Execution Completed")
             
            @pytest.mark.run(order=104)
            def test_104_start_the_logs_and_request_ipv6_lease_with_hostand_and_mac_address_and_stop_the_logs(self):
                logging.info("Performing dras command")
                log("start","/var/log/syslog",config.member1_ipv6)
		sleep(10)
		for i in range(10):
		    #dras_cmd = 'sudo /root/dras6/./dras6 -i '+str(config.member1_ipv6)+' '+'-A -n 1 -h test1.com -a 77:77:77:66:66:16'
		    dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.member1_ipv6)+' '+'-A -n 1 -h test1.com -a 77:77:77:66:66:16'
		    dras_cmd1 = os.system(dras_cmd)
		    print("output is ",dras_cmd1)
                    if dras_cmd1 == 0:
                        print("got the lease")
                        break
                    else:
                        print("didn't get the lease and continuing for lease")
		ping = ('for i in range{1..2} ; do ping6 -i 1 -c 5 '+config.member1_ipv6+' ; done')
                data = os.popen(ping).read()
                print(data)
                sleep(300)
                log("stop","/var/log/syslog",config.member1_ipv6)
                print("\nTest Case 104 Executed Successfully")

            @pytest.mark.run(order=105)
            def test_105_Validate_deffered_message_in_var_log_messages(self):
                logging.info("validating deffered message in var log messages ")
                out1 = str(config.member1_ipv6+'_var_log_messages')
                #print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                print("\n")
                print(log_validation)
                output1 = re.search('debug Lease on(.*)preferred for 27000s', log_validation)
                output1 = output1.group(0)
                print(output1)
                def Convert(string):
                    li = list(string.split(" "))
                    return li
                str1 = Convert(output1)
                Lease_IPv6 = str1[4]
                output = ['Addition of forward map for '+Lease_IPv6+' deferred','Addition of reverse map for '+Lease_IPv6+' deferred']
		#output = 'Addition of reverse map for '+Lease_IPv6+' deferred'
                for values in output:
                    if values in log_validation:
		#if output in log_validation:
                        assert True
                    else:
                        assert False
                print("\n")
                print(output)
                print("\nTest Case 105 Executed Successfully")
	    
            @pytest.mark.run(order=106)
            def test_106_validate_ddns_update_records_in_authoritative_forward_mapping_zone_and_authoritative_reverse_mapping_zone(self):
                logging.info("validating ddns update records in authoritative forward mapping zone and authoritative reverse mapping zone")
                out1 = str(config.member1_ipv6+'_var_log_messages')
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                output1 = re.search('debug Lease on(.*)preferred for 27000s', log_validation)
                output1 = output1.group(0)
                print(output1)
                def Convert(string):
                    li = list(string.split(" "))
                    return li
                str1 = Convert(output1)
                Lease_IPv6 = str1[4]
                print(Lease_IPv6)
                Name = str1[5]
                Name = Name.replace('(','').replace(')','')
                print(Name)
                values = ['"ipv6addr": "'+Lease_IPv6+'"','"name": "'+Name+'"']
		print(values)
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:aaaa", grid_vip=config.grid_vip)
                print(get_ref)
                for output in values:
                    if output in get_ref:
                        assert False
			print(output)
                    else:
                        assert True
                print(values,"Since zone is disabled forward and reverse map updates are deffered")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:ptr", grid_vip=config.grid_vip)
                print(get_ref)
                result = ('"ptrdname": "'+Name+'"')
                if result in (get_ref):
                    assert False
                else:
                    assert True
                #print(result,"Expired records got deleted from reverse map zone")
                sleep(5)
		############################
		## Enabling the auth zone ##
		############################
		get_ref = ib_NIOS.wapi_request('GET', "zone_auth?fqdn=test1.com", grid_vip=config.grid_vip)
                ref = json.loads(get_ref)[0]['_ref']
                ref = eval(json.dumps(ref))
                print(ref)
                data = {"disable": False}
                response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
		grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 106 Execution Completed")


###############################################################################################
#Scenario : After Signed an zone also DDNS Updates should work properly #######################
###############################################################################################
 	    
            @pytest.mark.run(order=107)
            def test_107_Signing_the_authoritative_forward_mapping_zone_and_enabling_the_authoritative_forward_mapping_zone(self):
                logging.info("adding authority zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=test.com", grid_vip=config.grid_vip)
                print(get_ref)
                #res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                print(ref)
		operation = "SIGN"
		response = ib_NIOS.wapi_request('POST', ref=ref, params='?_function=dnssec_operation', fields=json.dumps({"operation":operation}),grid_vip=config.grid_vip)
                print(response)
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
                print(get_ref)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[2]['_ref']
                print(ref)
                data = {"disable": False}
                response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
		grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 107 Execution Completed")	
            
            @pytest.mark.run(order=108)
            def test_108_Validating_the_signed_authoritative_forward_mapping_zone(self):
                logging.info("adding authority zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=test.com", grid_vip=config.grid_vip)
                print(get_ref)
                #res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                print(ref)
                get_ref = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=is_dnssec_signed",grid_vip=config.grid_vip)
                print(get_ref)
                value = '"is_dnssec_signed": true'
                if value in get_ref:
                    assert True
                else:
                    assert False
                print(value)
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
                print(get_ref)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[2]['_ref']
                print(ref)
                grid =  ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=disable",grid_vip=config.grid_vip)
                print(grid)
                value = '"disable": false'
                if value in grid:
                    assert True
                else:
                    assert False
                print(value)
                sleep(5)
                print("\nTest Case 108 Execution Completed")
	    
            @pytest.mark.run(order=109)
            def test_109_start_the_logs_and_request_ipv6_lease_with_hostand_and_mac_address_and_stop_the_logs(self):
                logging.info("Performing dras command")
                log("start","/var/log/syslog",config.member1_ipv6)
		sleep(10)
		for i in range(10):
		    #dras_cmd = 'sudo /root/dras6/./dras6 -i '+str(config.member1_ipv6)+' '+'-A -n 1 -h test1.com -a 77:77:77:76:65:68'
		    dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.member1_ipv6)+' '+'-A -n 1 -h test1.com -a 77:77:77:76:65:68'
		    dras_cmd1 = os.system(dras_cmd)
		    print("output is ",dras_cmd1)
                    if dras_cmd1 == 0:
                        print("got the lease")
                        break
                    else:
                        print("didn't get the lease and continuing for lease")
		ping = ('for i in range{1..2} ; do ping6 -i 1 -c 5 '+config.member1_ipv6+' ; done')
                data = os.popen(ping).read()
                print(data)
                sleep(300)
                log("stop","/var/log/syslog",config.member1_ipv6)
                print("\nTest Case 109 Executed Successfully")

            @pytest.mark.run(order=110)
            def test_110_validating_lease_in_leases(self):
                logging.info("validating the lease in leases")
                out1 = str(config.member1_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                #print(log_validation)
                output1 = re.search('debug Lease on(.*)preferred for 27000s', log_validation)
                output1 = output1.group(0)
                print(output1)
                def Convert(string):
                    li = list(string.split(" "))
                    return li
                str1 = Convert(output1)
                Lease_IPv6 = str1[4]
                print(Lease_IPv6)
                get_ref = ib_NIOS.wapi_request('GET', object_type="lease", grid_vip=config.grid_vip)
                print(get_ref)
                response = get_ref
                print(response)
                values = '"address": "'+Lease_IPv6+'"'
                if values in response:
                        assert True
                else:
                        assert False
                print(values)
                print("\ntest Case 110 Executed Successfully")

            @pytest.mark.run(order=111)
            def test_111_validate_the_ipv6_lease_and_hostname_in_var_log_messages(self):
                logging.info("validating the ipv6 lease and hostname in var log messages")
                out1 = str(config.member1_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                output1 = re.search('debug Lease on(.*)preferred for 27000s',log_validation)
                output1 = output1.group(0)
                print(output1)
                #output2 = re.search('Added new forward map from(.*)2620:10a:6000:2500',log_validation)
		output2 = re.search('Added new forward map from(.*)::',log_validation)
                output2 = output2.group(0)
                print(output2)
                output3 = re.search('Added reverse map from(.*)test1.com',log_validation)
                output3 = output3.group(0)
                print(output3)
                host_name = 'h777777766568.test1.com'
                output = (output1,output2,output3)
                for values in output:
                    if host_name in values:
                        assert True
                    else:
                        assert False
                print(host_name)
                print("\nTest Case 111 Executed Successfully")

            @pytest.mark.run(order=112)
            def test_112_validate_ddns_update_records_in_authoritative_forward_mapping_zone_and_authoritative_reverse_mapping_zone(self):
                logging.info("validating ddns update records in authoritative forward mapping zone and authoritative reverse mapping zone")
                out1 = str(config.member1_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                output1 = re.search('debug Lease on(.*)preferred for 27000s', log_validation)
                output1 = output1.group(0)
                print(output1)
                def Convert(string):
                    li = list(string.split(" "))
                    return li
                str1 = Convert(output1)
                Lease_IPv6 = str1[4]
                Name = str1[5]
                Name = Name.replace('(','').replace(')','')
                values = ['ipv6addr:'+Lease_IPv6,'name:'+Name]
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:aaaa", grid_vip=config.grid_vip)
                print(get_ref)
                get_ref=get_ref.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                for output in values:
                    if output in get_ref:
                        assert True
                    else:
                        assert False
                print(values,"added in forward map zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:ptr", grid_vip=config.grid_vip)
                print(get_ref)
                get_ref=get_ref.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                result = ('ptrdname:'+Name)
                if result in (get_ref):
                    assert True
                else:
                    assert False
                print(result,"added in reverse map zone")
                print("\nTest Case 112 Execution Completed")
	   
            @pytest.mark.run(order=113)
            def test_113_Unsign_auth_zone(self):
                logging.info("UNSIGN auth zone ")
		########################################
		######## Unsiging the auth zone ########
		########################################
		get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=test.com", grid_vip=config.grid_vip)
                print(get_ref)
                #res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                print(ref)
                operation = "UNSIGN"
                response = ib_NIOS.wapi_request('POST', ref=ref, params='?_function=dnssec_operation', fields=json.dumps({"operation":operation}),grid_vip=config.grid_vip)
                print(response)
		grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get startedgrid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 113 Execution Completed")


#########################################################################################
#Scenario : DDNS Updates should work when DNS server is an External server ##############
#########################################################################################
	    
            @pytest.mark.run(order=114)
            def test_114_Change_the_preferred_lifetime_and_valid_lifetime_at_grid_level(self):
                logging.info("changing the preferred lifetime and valid lifetime at grid level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                print(ref)
                data = {"preferred_lifetime": 5,"valid_lifetime": 10}
                response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 114 Execution Completed")

            @pytest.mark.run(order=115)
            def test_115_Validate_changed_preferred_lifetime_and_valid_lifetime_at_grid_level(self):
                logging.info("validating changed preferred lifetime and valid lifetime at grid level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6network", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                #print(ref)
                response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=preferred_lifetime,valid_lifetime",grid_vip=config.grid_vip)
                print(response)
                output = ['"value": 5','"value": 10']
                for values in output:
                    if values in response:
                        assert True
                    else:
                        assert False
                print(output)
                print("\nTest Case 115 Execution Completed")
	    
            @pytest.mark.run(order=116)
            def test_116_Add_ipv6_ddns_domainname_and_ipv6_domain_name_and_ipv6_domain_name_servers_at_grid_level(self):
                logging.info("adding ipv6 ddns domain name and ipv6 domain name and ipv6 domain name servers at grid level")
		############################################################################################
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.external_ip)
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                data = {"use_lan_ipv6_port": True}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.external_ip)
                print(response)
                data = {"use_lan_port": True}
                response1 = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.external_ip)
                print(response1)
                ################################################################################################
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                data = {"ipv6_ddns_domainname": "test2.com","ipv6_domain_name": "test2.com","ipv6_domain_name_servers": [config.external_ipv6]  }
                response1 = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response1)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 116 Execution Completed")

            @pytest.mark.run(order=117)
            def test_117_Validate_added_ipv6_ddns_domainname_and_ipv6_domain_name_and_ipv6_domain_name_servers_at_grid_level(self):
                logging.info("validating added ipv6 ddns domain name and ipv6 domain name and ipv6 domain name servers at grid level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                print(ref)
                response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=ipv6_ddns_domainname,ipv6_domain_name,ipv6_domain_name_servers",grid_vip=config.grid_vip)
                print(response)
                response=response.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','').replace('[','').replace(']','')
                output = ['ipv6_domain_name_servers:'+config.external_ipv6,'ipv6_ddns_domainname:test2.com','ipv6_domain_name:test2.com']
                for values in output:
                    if values in response:
                        assert True
                    else:
                        assert False
                print(output)
                sleep(15)
                print("Test CAse 117 Execution Completed")



###########################################################
###### Configuring External DNS server(ddns properties)####
###########################################################

            @pytest.mark.run(order=118)
            def test_118_Add_External_DNS_server_and_authoritative_forward_mapping_zone(self):
                logging.info("adding external dns server and zone ")
                get_ref = ib_NIOS.wapi_request('GET', object_type="networkview", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                print(ref)
		data = {"remote_forward_zones": [{"fqdn": "test2.com","key_type": "NONE","server_address": config.external_ipv6}]}
                response1 = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response1)
		grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 118 Execution Completed") 

            @pytest.mark.run(order=119)
            def test_119_Validate_added_external_DNS_server_and_authoritative_forward_mapping_zone(self):
                logging.info("adding authority zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="networkview", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                #print(ref)
                response = ib_NIOS.wapi_request('GET',object_type="networkview",params="?_inheritance=True&_return_fields=remote_forward_zones",grid_vip=config.grid_vip)
		print(response)
		output = ['"fqdn": "test2.com"','"key_type": "NONE"','"server_address": "'+config.external_ipv6+'"']
		for values in output:
                    if values in response:
			assert True
                    else:
			assert False
		print(output)
		print("\nTest Case 119 Execution Completed")



###########################################################################
######Adding authoritative forrward mapping zone on external dns server ###
###########################################################################


	     
            @pytest.mark.run(order=120)
            def test_120_Add_authoritative_forward_mapping_zone_on_external_dns_server(self):
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.external_ip)
		print(get_ref)
                logging.info(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print (ref1)
		data = {"use_lan_port":True}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.external_ip)
                print(response)
                sleep(10)
		data = {"use_lan_ipv6_port":True}
		response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.external_ip)
                print(response)
		sleep(10)
		data = {"enable_dns":True}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.external_ip)
                print(response)
                logging.info("adding authority zone")
                data = {"fqdn": "test2.com","view": "default","grid_primary": [{"name": config.external_fqdn,"stealth": False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data),grid_vip=config.external_ip)
                print(response)
                grid =  ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.external_ip)
                print(grid)
                ref = json.loads(grid)[0]['_ref']
                print(ref)
                data = {"allow_update": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}]}
                response1 = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.external_ip)
                print(response1)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.external_ip)
                print(grid)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.external_ip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 120 Execution Completed")
 	    
            @pytest.mark.run(order=121)
            def test_121_Validate_added_authoritative_forward_mapping_zone_on_external_dns_server(self):
                output = ib_NIOS.wapi_request('GET',object_type='zone_auth',params="?_inheritance=True&_return_fields=grid_primary,fqdn" , grid_vip=config.external_ip)
		print(output)
                result = ['"fqdn": "test2.com"','"name": "'+config.external_fqdn+'"','"stealth": false']
                for string in result:
                    if string in output:
                        assert True
                    else:
                        assert False
                print(result)
                print("Test Case 121 Executuion Completed")



#############################################################
## Dras request to test ddns updates on external servel #####
#############################################################
	    
            @pytest.mark.run(order=122)
            def test_122_start_the_logs_and_request_ipv6_lease_with_hostand_and_mac_address_and_stop_the_logs(self):
                logging.info("Performing dras command")
                log("start","/var/log/syslog",config.external_ip)
                log("start","/var/log/syslog",config.member1_ipv6)
		sleep(10)
		for i in range(10):
		    #dras_cmd = 'sudo /root/dras6/./dras6 -i '+str(config.member1_ipv6)+' '+'-A -n 1 -h test2.com -a 77:77:77:77:71:43'
		    dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.member1_ipv6)+' '+'-A -n 1 -h test2.com -a 77:77:77:77:71:43'
		    print("output is ",dras_cmd)
		    dras_cmd1 = os.system(dras_cmd)
		    print("output is ",dras_cmd1)
                    if dras_cmd1 == 0:
                        print("got the lease")
                        break
                    else:
                        print("didn't get the lease and continuing for lease")
                sleep(200)
                log("stop","/var/log/syslog",config.external_ip)
                log("stop","/var/log/syslog",config.member1_ipv6)
                print("\nTest Case 122 Executed Successfully")

            @pytest.mark.run(order=123)
            def test_123_validate_the_ipv6_lease_and_hostname_in_var_log_messages_and_records_added_messages_in_dns_server_logs(self):
                logging.info("validating the ipv6 lease and hostname in var log messages")
                out1 = str(config.member1_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                output1 = re.search('debug Lease on(.*)preferred for 5s',log_validation)
                output1 = output1.group(0)
                print(output1)
                #output2 = re.search('Added new forward map from(.*)2620:10a:6000:2500',log_validation)
		output2 = re.search('Added new forward map from(.*)::',log_validation)
                output2 = output2.group(0)
                print(output2)
                output3 = re.search('Added reverse map from(.*)test2.com',log_validation)
                output3 = output3.group(0)
                print(output3)
                host_name = 'h777777777143.test2.com'
                output = (output1,output2,output3)
                for values in output:
                    if host_name in values:
                        assert True
                    else:
                        assert False
                print(host_name)
                sleep(10)
                print("##################################################")
                out1 = str(config.external_ip+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                server_log_validation = textfile.read()
                textfile.close()
                output1 = re.search('debug Lease on(.*)preferred for 5s', log_validation)
                output1 = output1.group(0)
                print(output1)
                def Convert(string):
                    li = list(string.split(" "))
                    return li
                str1 = Convert(output1)
                Lease_IPv6 = str1[4]
                print(Lease_IPv6)
                result = ["adding an RR at 'h777777777143.test2.com' AAAA "+Lease_IPv6,"adding an RR at 'h777777777143.test2.com' TXT"]
                print(result)
                for values in result:
                    if values in server_log_validation:
                        assert True
                    else:
                        assert False
                print(result) 
                print("\nTest Case 123 Executed Successfully")

            @pytest.mark.run(order=124)
            def test_124_Validate_external_ddns_update_records_deleted_message_in_var_log_messages_after_lease_expired(self):
                logging.info(" validating ddns update records deleted message in var log messages after lease expired")
                out1 = str(config.member1_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                output = ['Removed forward map from h777777777143.test2.com','Removed reverse map']
                for values in output:
                    if values in log_validation:
                        assert True
                    else:
                        assert False
                print(output)
                print("\nTest Case 124 Executed Successfully")

            @pytest.mark.run(order=125)
            def test_125_validate_ddns_update_records_in_authoritative_forward_mapping_zone_and_authoritative_reverse_mapping_zone(self):
                logging.info("validating ddns update records in authoritative forward mapping zone and authoritative reverse mapping zone")
                out1 = str(config.member1_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                output1 = re.search('debug Lease on(.*)preferred for 5s', log_validation)
                output1 = output1.group(0)
                print(output1)
                def Convert(string):
                    li = list(string.split(" "))
                    return li
                str1 = Convert(output1)
                Lease_IPv6 = str1[4]
                Name = str1[5]
                Name = Name.replace('(','').replace(')','')
                values = ['ipv6addr:'+Lease_IPv6,'name:'+Name]
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:aaaa", grid_vip=config.external_ip)
                print(get_ref)
                get_ref=get_ref.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                for output in values:
                    if output in get_ref:
                        assert False
                    else:
                        assert True
                print(values,"removed from forward map zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:ptr", grid_vip=config.external_ip)
                print(get_ref)
                get_ref=get_ref.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                result = ('ptrdname:'+Name)
                if result in (get_ref):
                    assert False
                else:
                    assert True
                print(result,"removed from reverse map zone")
                print("\nTest Case 125 Execution Completed")



###################################
#Scenario : Validating primary6 ###
###################################

            @pytest.mark.run(order=126)
            def test_126_Validating_the_Another_test_is_currently_running_status(self):
                logging.info("validating the Another test is currently running status")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.member1_ipv6)
                child.logfile=sys.stdout
                #child.expect('password:')
                #child.sendline('infoblox')
                child.expect('#')
                child.sendline('cd /infoblox/var/dhcpdv6_conf')
                child.expect('#')
                child.sendline('cat dhcpdv6.conf')
                sleep(03)
                child.expect('#')
                child.sendline('exit')
                output=child.read()
                output=output.replace('\n','').replace(' ','').replace('[','').replace(']','').replace('\r','').replace('\t','')
                #print(output)
                value = 'primary6::1'
                if value in output:
                   assert True
                else:
                   assert False
                print("\n")
                print(value)
                print("\nTest Case 126 Executed Successfully")



##########################################################################################
#####Scenario : Create range with IPv6 Range Template and ddns should work properly ######
##########################################################################################

            @pytest.mark.run(order=127)
            def test_127_delete_IPv6_network(self):
                logging.info("deleting ipv6 network")
                get_ref = ib_NIOS.wapi_request('GET',object_type="ipv6network",grid_vip=config.grid_vip)
                print(get_ref)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                response = ib_NIOS.wapi_request('DELETE',ref=ref,grid_vip=config.grid_vip)
                print(response)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 127 Execution Completed")
	    
            @pytest.mark.run(order=128)
            def test_128_Add_IPv6_network(self):
                logging.info("adding ipv6 network")
                data = {"network": ipv6_network+"::/64","network_view": "default","members": [{"_struct": "dhcpmember","ipv6addr": config.member_ipv6,"name": config.grid_member2_fqdn},{"_struct": "dhcpmember","ipv6addr": config.member1_ipv6,"name": config.grid_member1_fqdn}]}
                print(data)
                response = ib_NIOS.wapi_request('POST', object_type="ipv6network", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20)
                print("Test Case 128 Execution Completed")

            @pytest.mark.run(order=129)
            def test_129_Validate_added_IPv6_network(self):
                logging.info("validating created ipv6 network")
                output = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=members,network",grid_vip=config.grid_vip)
                print(output)
                result = ['"ipv4addr": null','"ipv6addr": "'+config.member_ipv6+'"','"name": "'+config.grid_member2_fqdn+'"','"ipv6addr": "'+config.member1_ipv6+'"','"name": "'+config.grid_member1_fqdn+'"','"network": "'+ipv6_network+'::/64"']
                for values in result:
                    if values in output:
                        assert True
                    else:
                        assert False
                print(result)
                print("Test Case 129 Execution Completed")
	    
            @pytest.mark.run(order=130)
            def test_130_Adding_IPv6_Range_Template(self):
                logging.info("adding authority zone")
                data = {"member": {"_struct": "dhcpmember","ipv6addr": config.member1_ipv6,"name": config.grid_member1_fqdn},"name": "test","number_of_addresses": 20,"offset": 100}
                response1 = ib_NIOS.wapi_request('POST',object_type="ipv6rangetemplate",fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response1)
                print("Test Case 130 Execution Completed")
 
            @pytest.mark.run(order=131)
            def test_131_Validating_IPv6_Range_Template(self):
                logging.info("validating ipv6 range template")
                response = ib_NIOS.wapi_request('GET',object_type="ipv6rangetemplate",params="?_inheritance=True&_return_fields=name,number_of_addresses,offset,member",grid_vip=config.grid_vip)
                print(response)
                output = ['"name": "test"','"number_of_addresses": 20','"offset": 100','"ipv6addr": "'+config.member1_ipv6+'"','"name": "'+config.grid_member1_fqdn+'"']
                for values in output:
                    if values in response:
                        assert True
                    else:
                        assert False
                print(output)
                print("\nTest Case 131 Execution Completed")

            @pytest.mark.run(order=132)
            def test_132_Add_IPv6_Range_using_IPv6_range_Template(self):
                logging.info("adding ipv6 range using ipv6 range template")
                data = {"network": ipv6_network+"::/64","template" : "test","end_addr": ipv6_network+"::77","start_addr": ipv6_network+"::64"}
                response1 = ib_NIOS.wapi_request('POST',object_type="ipv6range",fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response1)
                response = ib_NIOS.wapi_request('GET',object_type="ipv6range",grid_vip=config.grid_vip)
                res = json.loads(response)
                ref = json.loads(response)[0]['_ref']
                print(ref)
                data = {"member": {"_struct": "dhcpmember","ipv6addr": config.member1_ipv6}}
                response1 = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response1)               
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) 
                print("\nTest Case 132 Execution Completed")
								
            @pytest.mark.run(order=133)
            def test_133_Validate_added_IPv6_range(self):
                logging.info("validating added ipv6 range")
                grid =  ib_NIOS.wapi_request('GET', object_type="ipv6range",params="?_inheritance=True&_return_fields=member,end_addr,start_addr,network_view",grid_vip=config.grid_vip)
                print(grid)
                output = ['"end_addr": "'+ipv6_network+"::77",'"start_addr": "'+ipv6_network+"::64",'"network_view": "default"','"name": "'+config.grid_member1_fqdn+'"','"ipv6addr": "'+config.member1_ipv6+'"']
                for values in output:
                    if values in grid:
                        assert True
                    else:
                        assert False
                print(output)
                print("\nTest Case 133 Execution Completed")


            @pytest.mark.run(order=134)
            def test_134_Changing_the_DNS_server(self):
                logging.info("adding authority zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                data = {"ipv6_ddns_domainname": "test.com","ipv6_domain_name": "test.com","ipv6_domain_name_servers": [config.member1_ipv6]  }
                response1 = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response1)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(10) #wait for 20 secs for the member to get started
                print("\nTest Case 134 Execution Completed")

            @pytest.mark.run(order=135)
            def test_135_start_the_logs_and_request_ipv6_lease_with_host_and_and_mac_address_and_stop_the_logs(self):
                logging.info("Performing dras command")
                log("start","/var/log/syslog",config.member1_ipv6)
		sleep(10)
		for i in range(10):
		    #dras_cmd = 'sudo /root/dras6/./dras6 -i '+str(config.member1_ipv6)+' '+'-A -n 1 -h test.com -a 77:77:77:77:61:43'
		    dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.member1_ipv6)+' '+'-A -n 1 -h test.com -a 77:77:77:77:61:43'
		    dras_cmd1 = os.system(dras_cmd)
		    print("output is ",dras_cmd1)
                    if dras_cmd1 == 0:
                        print("got the lease")
                        break
                    else:
                        print("didn't get the lease and continuing for lease")
                sleep(200)
                log("stop","/var/log/syslog",config.member1_ipv6)
                print("\nTest Case 135 Executed Successfully")

            @pytest.mark.run(order=136)
            def test_136_validate_the_ipv6_lease_and_hostname_in_var_log_messages(self):
                logging.info("validating the ipv6 lease and hostname in var log messages")
                out1 = str(config.member1_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                output1 = re.search('debug Lease on(.*)preferred for 5s',log_validation)
                output1 = output1.group(0)
                print(output1)
                #output2 = re.search('Added new forward map from(.*)2620:10a:6000:2500',log_validation)
		output2 = re.search('Added new forward map from(.*)::',log_validation)
                output2 = output2.group(0)
                print(output2)
                output3 = re.search('Added reverse map from(.*)test.com',log_validation)
                output3 = output3.group(0)
                print(output3)
                host_name = 'h777777776143.test.com'
                output = (output1,output2,output3)
                for values in output:
                    if host_name in values:
                        assert True
                    else:
                        assert False
                print(host_name)
                print("\nTest Case 136 Executed Successfully")

            @pytest.mark.run(order=137)
            def test_137_Validate_records_deleted_message_in_var_log_messages_after_lease_expired(self):
                logging.info(" validating ddns update records deleted message in var log messages after lease expired")
                out1 = str(config.member1_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                output = ['Removed forward map from h777777776143.test.com','Removed reverse map']
                for values in output:
                    if values in log_validation:
                        assert True
                    else:
                        assert False
                print(output)
                print("\nTest Case 137 Executed Successfully")

            @pytest.mark.run(order=138)
            def test_138_validate_ddns_update_records_in_authoritative_forward_mapping_zone_and_authoritative_reverse_mapping_zone(self):
                logging.info("validating ddns update records in authoritative forward mapping zone and authoritative reverse mapping zone")
                out1 = str(config.member1_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                output1 = re.search('debug Lease on(.*)preferred for 5s', log_validation)
                output1 = output1.group(0)
                print(output1)
                def Convert(string):
                    li = list(string.split(" "))
                    return li
                str1 = Convert(output1)
                Lease_IPv6 = str1[4]
                Name = str1[5]
                Name = Name.replace('(','').replace(')','')
                values = ['ipv6addr:'+Lease_IPv6,'name:'+Name]
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:aaaa", grid_vip=config.external_ip)
                print(get_ref)
                get_ref=get_ref.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                for output in values:
                    if output in get_ref:
                        assert False
                    else:
                        assert True
                print(values,"added in forward map zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:ptr", grid_vip=config.external_ip)
                print(get_ref)
                get_ref=get_ref.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                result = ('ptrdname:'+Name)
                if result in (get_ref):
                    assert False
                else:
                    assert True
                print(result,"added in reverse map zone")
                print("\nTest Case 138 Execution Completed")

            @pytest.mark.run(order=139)
            def test_139_delete_IPv6_network(self):
                logging.info("deleting ipv6 network")
                get_ref = ib_NIOS.wapi_request('GET',object_type="ipv6network",grid_vip=config.grid_vip)
                print(get_ref)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                response = ib_NIOS.wapi_request('DELETE',ref=ref,grid_vip=config.grid_vip)
                print(response)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 139 Execution Completed")



################################################################################
###Scenario : In Custome Network View also ddns updates should work properly ###
################################################################################

            @pytest.mark.run(order=140)
            def test_140_Add_and_Validate_network_view(self):
                logging.info("adding and validating network view")
                data = {"name": "custom"}
                response = ib_NIOS.wapi_request('POST', object_type="networkview",fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                sleep(05)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(10) #wait for 20 secs for the member to get started
                print("\nTest Case 140 Execution Completed")

            @pytest.mark.run(order=141)
            def test_141_Add_and_Validate_network_view(self):
                logging.info("adding and validating network view")
                output = ib_NIOS.wapi_request('GET',object_type="networkview",grid_vip=config.grid_vip)
                print(output)
                output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                print(output)
                result = 'is_default:false,name:custom'
                if result in output:
                    assert True
                else:
                    assert False
                print(result)
                print("Test Case 141 Executuion Completed")

            @pytest.mark.run(order=142)
            def test_142_create_IPv6_network(self):
                logging.info("Create an ipv6 network default network view")
                #data = {"network": "2620:10A:6000:2500::/64","network_view": "default","members": [{"_struct": "dhcpmember","ipv6addr": config.member_ip,"name": config.grid_member2_fqdn}]}
                data = {"network": ipv6_network+"::/64","network_view": "custom","members": [{"_struct": "dhcpmember","ipv6addr": config.member_ipv6,"name": config.grid_member2_fqdn},{"_struct": "dhcpmember","ipv6addr": config.member1_ipv6,"name": config.grid_member1_fqdn}]}
                print(data)
                response = ib_NIOS.wapi_request('POST', object_type="ipv6network", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 142 Execution Completed")

            @pytest.mark.run(order=143)
            def test_143_validate_IPv6_network(self):
                logging.info("validating ipv6 network")
                output = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=members,network,network_view",grid_vip=config.grid_vip)
                print(output)
                result = ['"ipv4addr": null','"ipv6addr": "'+config.member_ipv6+'"','"name": "'+config.grid_member2_fqdn+'"','"network": "'+ipv6_network+'::/64"','"network_view": "custom"','"name": "'+config.grid_member1_fqdn+'"']
		print(result)
                for values in result:
                    if values in output:
                        assert True
                    else:
                        assert False
                print(result)
                print("\nTest Case 143 Execution Completed")

            @pytest.mark.run(order=144)
            def test_144_create_IPv6_Prefix_address_Range_1(self):
                logging.info("Create an ipv6 range in  default network view")
                data ={"end_addr": ipv6_network+"::100","network": ipv6_network+"::/64","network_view": "custom","start_addr": ipv6_network+"::10","member": {"_struct": "dhcpmember","ipv6addr": config.member_ipv6,"name": config.grid_member2_fqdn}} 
                response = ib_NIOS.wapi_request('POST', object_type="ipv6range", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 144 Execution Completed")

            @pytest.mark.run(order=145)
            def test_145_create_IPv6_Prefix_address_Range_1(self):
                logging.info("Create an ipv6 range in  default network view")
                grid =  ib_NIOS.wapi_request('GET', object_type="ipv6range",params="?_inheritance=True&_return_fields=member,end_addr,start_addr,network_view",grid_vip=config.grid_vip)
                print(grid)
                output = ['"end_addr": "'+ipv6_network+'::100"','"start_addr": "'+ipv6_network+'::10"','"network_view": "custom"','"name": "'+config.grid_member2_fqdn+'"','"ipv6addr": "'+config.member_ipv6+'"']
                for values in output:
                    if values in grid:
                        assert True
                    else:
                        assert False
                print(output)
                print("\nTest Case 145 Execution Completed")

            @pytest.mark.run(order=146)
            def test_146_Add_Authority_zone(self):
                logging.info("adding authority zone")
                data = {"fqdn": "custom.com","view": "default.custom","grid_primary": [{"name": config.grid_member2_fqdn,"stealth": False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 146 Execution Completed")

            @pytest.mark.run(order=147)
            def test_147_Validate_Authority_zone(self):
                get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
                #print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[-1]['_ref']
                output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=grid_primary,fqdn,view" , grid_vip=config.grid_vip)
                print(output)
                #output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','').replace('[','').replace(']','')
                result = ['"fqdn": "custom.com"','"view": "default.custom"','"name": "'+config.grid_member2_fqdn+'"','"stealth": false']
                for values in result:
                    if values in output:
                        assert True
                    else:
                        assert False
                print(result)
                print("Test Case 147 Executuion Completed")

            @pytest.mark.run(order=148)
            def test_148_Add_Authoritative_reverse_mapping_zone(self):
                logging.info("adding authority zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                data = {"ipv6_ddns_domainname": "custom.com","ipv6_domain_name": "custom.com","ipv6_domain_name_servers": [config.member_ipv6]  }
                response1 = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response1)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(10) #wait for 20 secs for the member to get started
                print("\nTest Case 148 Execution Completed")

            @pytest.mark.run(order=149)
            def test_149_Add_Authoritative_reverse_mapping_zone(self):
                logging.info("adding authority zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                print(ref)
                response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=ipv6_ddns_domainname,ipv6_domain_name,ipv6_domain_name_servers",grid_vip=config.grid_vip)
                print(response)
                response=response.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','').replace('[','').replace(']','')
                output = ['ipv6_domain_name_servers:'+config.member_ipv6,'ipv6_ddns_domainname:custom.com','ipv6_domain_name:custom.com']
                for values in output:
                    if values in response:
                        assert True
                    else:
                        assert False
                print(output)
                print("Test CAse 149 Execution Completed")

            @pytest.mark.run(order=150)
            def test_150_Add_Authoritative_reverse_mapping_zone(self):
                logging.info("adding authority zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="networkview", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                print(ref)
                data = {"remote_forward_zones": []}
                response1 = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response1)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(10) #wait for 20 secs for the member to get started
                print("\nTest Case 150 Execution Completed")

            @pytest.mark.run(order=151)
            def test_151_Add_Authoritative_reverse_mapping_zone(self):
                logging.info("adding authority zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="networkview", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                #print(ref)
                response = ib_NIOS.wapi_request('GET',object_type="networkview",params="?_inheritance=True&_return_fields=remote_forward_zones",grid_vip=config.grid_vip)
                print(response)
                output = '"remote_forward_zones": []'
                if output in response:
                       assert True
                else:
                       assert False
                print(output)
                print("\nTest Case 151 Execution Completed")

            @pytest.mark.run(order=152)
            def test_152_Add_Authoritative_reverse_mapping_zone_in_custom_dns_view(self):
                logging.info("adding authoritative reverse mapping zone in custom dns view")
                data = {"fqdn": ipv6_network+"::/64","grid_primary": [{"name": config.grid_member2_fqdn,"stealth": False}],"view": "default.custom","zone_format": "IPV6"}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(10) #wait for 20 secs for the member to get started
                print("\nTest Case 152 Execution Completed")

            @pytest.mark.run(order=153)
            def test_153_Validate_reverse_mapping_zone_in_custom_dns_view(self):
		logging.info("validating authoritative reverse mapping zone in custom dns view")
                get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[-1]['_ref']
                output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=grid_primary,fqdn,zone_format",grid_vip=config.grid_vip)
                print(output)
                output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','').replace('[','').replace(']','')
                result = ['fqdn:'+ipv6_network+'::/64','grid_primary:name:'+config.grid_member2_fqdn,'zone_format:IPV6']
                for string in result:
                    if string in output:
                        assert True
                    else:
                        assert False
                print(result)
                print("\nTest Case 153 Executuion Completed")

            @pytest.mark.run(order=154)
            def test_154_Change_the_preferred_lifetime_and_valid_lifetime_at_grid_level(self):
                logging.info("changing the preferred lifetime and valid lifetime at grid level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                print(ref)
                data = {"preferred_lifetime": 20,"valid_lifetime": 30}
                response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("\nTest Case 154 Execution Completed")

            @pytest.mark.run(order=155)
            def test_155_Validate_changed_preferred_lifetime_and_valid_lifetime_at_grid_level(self):
                logging.info("validating changed preferred lifetime and valid lifetime at grid level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=True&_return_fields=preferred_lifetime,valid_lifetime",grid_vip=config.grid_vip)
                print(response)
                output = ['"preferred_lifetime": 20','"valid_lifetime": 30']
                for values in output:
                    if values in response:
                        assert True
                    else:
                        assert False
                print(output)
                print("\nTest Case 155 Execution Completed")

            @pytest.mark.run(order=156)
            def test_156_Changing_the_use_ipv6_ddns_domainname_and_use_ipv6_domain_name_and_use_ipv6_domain_name_servers_to_get_values_from_grid_level(self):
                logging.info("changing the use_ipv6_ddns_domainname and use_ipv6_domain_name and use_ipv6_domain_name_servers at member level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[-1]['_ref']
                print(ref)
                data = {"use_ipv6_ddns_domainname": False,"use_ipv6_domain_name": False,"use_ipv6_domain_name_servers": False,"use_ipv6_enable_ddns": False}
                response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20) #wait for 20 secs for the member to get started
                print("\nTest Case 156 Execution Completed")




            @pytest.mark.run(order=157)
            def test_157_start_the_logs_and_request_ipv6_lease_with_hostand_and_mac_address_and_stop_the_logs(self):
                logging.info("Performing dras command")
                log("start","/var/log/syslog",config.member_ipv6)
		sleep(10)
		for i in range(10):
		    #dras_cmd = 'sudo /root/dras6/./dras6 -i '+str(config.member_ipv6)+' '+'-A -n 1 -h custom.com -a 11:77:77:77:77:85'
		    dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.member_ipv6)+' '+'-A -n 1 -h custom.com -a 11:77:77:77:77:85'
		    dras_cmd1 = os.system(dras_cmd)
		    print("output is ",dras_cmd1)
                    if dras_cmd1 == 0:
                        print("got the lease")
                        break
                    else:
                        print("didn't get the lease and continuing for lease")
                sleep(10)
                log("stop","/var/log/syslog",config.member_ipv6)
                print("\nTest Case 157 Executed Successfully")

            @pytest.mark.run(order=158)
            def test_158_validating_lease_in_leases(self):
                logging.info("validating the lease in leases")
                out1 = str(config.member_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                output1 = re.search('debug Lease on(.*)preferred for 20s', log_validation)
                output1 = output1.group(0)
                print(output1)
                def Convert(string):
                    li = list(string.split(" "))
                    return li
                str1 = Convert(output1)
                Lease_IPv6 = str1[4]
                print(Lease_IPv6)
                get_ref = ib_NIOS.wapi_request('GET', object_type="lease", grid_vip=config.grid_vip)
                print(get_ref)
                response = get_ref
                print(response)
                values = '"address": "'+Lease_IPv6+'"'
                if values in response:
                        assert True
                else:
                        assert False
                print(values)
                print("\ntest Case 158 Executed Successfully")

            @pytest.mark.run(order=159)
            def test_159_validate_ddns_update_records_in_authoritative_forward_mapping_zone_and_authoritative_reverse_mapping_zone(self):
                logging.info("validating ddns update records in authoritative forward mapping zone and authoritative reverse mapping zone")
                out1 = str(config.member_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                output1 = re.search('debug Lease on(.*)preferred for 20s', log_validation)
                output1 = output1.group(0)
                print(output1)
                def Convert(string):
                    li = list(string.split(" "))
                    return li
                str1 = Convert(output1)
                Lease_IPv6 = str1[4]
                Name = str1[5]
                Name = Name.replace('(','').replace(')','')
                values = ['ipv6addr:'+Lease_IPv6,'name:'+Name]
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:aaaa", grid_vip=config.grid_vip)
                print(get_ref)
                get_ref=get_ref.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                for output in values:
                    if output in get_ref:
                        assert True
                    else:
                        assert False
                print(values,"added in forward map zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:ptr", grid_vip=config.grid_vip)
                print(get_ref)
                get_ref=get_ref.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                result = ('ptrdname:'+Name)
                if result in (get_ref):
                    assert True
                else:
                    assert False
                print(result,"added in reverse map zone")
                print("\nTest Case 159 Execution Completed")

            @pytest.mark.run(order=160)
            def test_160_validate_the_ipv6_lease_and_hostname_in_var_log_messages(self):
                logging.info("validating the ipv6 lease and hostname in var log messages")
                out1 = str(config.member_ipv6+'_var_log_messages')
                print(out1)
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                output1 = re.search('debug Lease on(.*)preferred for 20s',log_validation)
                output1 = output1.group(0)
                print(output1)
                #output2 = re.search('Added new forward map from(.*)2620:10a:6000:2500',log_validation)
		output2 = re.search('Added new forward map from(.*)::',log_validation)
                output2 = output2.group(0)
                print(output2)
                output3 = re.search('Added reverse map from(.*)custom.com',log_validation)
                output3 = output3.group(0)
                print(output3)
                host_name = 'h117777777785.custom.com'
                output = (output1,output2,output3)
                for values in output:
                    if host_name in values:
                        assert True
                    else:
                        assert False
                print(host_name)
                print("\nTest Case 160 Executed Successfully")

            @pytest.mark.run(order=161)
            def test_161_start_the_logs_and_request_ipv6_lease_with_hostand_and_mac_address_and_stop_the_logs(self):
                logging.info("Performing dras command")
                log("start","/var/log/syslog",config.member_ipv6)
		sleep(10)
		for i in range(10):
		    #dras_cmd = 'sudo /root/dras6/./dras6 -i '+str(config.member_ipv6)+' '+'-A -n 1 -h custom.com -a 11:77:77:77:77:86'
		    dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.member_ipv6)+' '+'-A -n 1 -h custom.com -a 11:77:77:77:77:86'
		    dras_cmd1 = os.system(dras_cmd)
		    print("output is ",dras_cmd1)
                    if dras_cmd1 == 0:
                        print("got the lease")
                        break
                    else:
                        print("didn't get the lease and continuing for lease")
                sleep(35)
                log("stop","/var/log/syslog",config.member_ipv6)
                print("\nTest Case 161 Executed Successfully")

            @pytest.mark.run(order=162)
            def test_162_Validate_records_deleted_message_in_var_log_messages_after_lease_expired(self):
                logging.info(" validating ddns update records deleted message in var log messages after lease expired")
                out1 = str(config.member_ipv6+'_var_log_messages')
                textfile = open('/tmp/'+out1, 'r')
                log_validation = textfile.read()
                textfile.close()
                sleep(05)
                output = ['Removed forward map','Removed reverse map']
                for values in output:
                    if values in log_validation:
                        assert True
                    else:
                        assert False
                print(output)
                print('Test Case 162 Executed Successfully')

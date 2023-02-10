__author__ = "Prasad K"
__email__  = "pkondisetty@infoblox.com"

#############################################################################
# RFE : 5514 (Multi-Master DNS Fail-over for DDNS updates)                  #
# Grid Set up required:                                                     #
#  1. Grid with 4 Members                                                   #
#  2. Licenses : Grid,DNS,DHCP,NIOS                                         #
#############################################################################
import re
import re as regex
import config
import pytest
import unittest
import logging
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import pexpect
import paramiko
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv
import os
import glob

logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="RFE_5514.log" ,level=logging.DEBUG,filemode='w')

global log_validation

def log_print(x=''):
    	print(x)
    	logging.info(x)

def restart_services(grid=config.grid_vip):
	log_print("Restart services")
    	get_ref =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=grid)
    	ref = json.loads(get_ref)[0]['_ref']
    	data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    	restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices", fields=json.dumps(data),grid_vip=grid)
	log_print("wait for 25sec")
    	sleep(25)

def IPv4_records_validation(grid=config.grid_vip):
	log_print("***** Record validation is started *****")
	record_name = re.search('Added new forward map from(.*)by server ',log_validation)
	record_name = record_name.group(0)
	def Convert(string):
		li = list(string.split(" "))
		return li
	str1 = Convert(record_name)
	record_name = str1[5]
	log_print(record_name)
	sleep(10)
        A_record = ib_NIOS.wapi_request('GET', object_type="record:a?name="+record_name, grid_vip=config.grid_vip)
        print(A_record)
    	TXT_record = ib_NIOS.wapi_request('GET', object_type="record:txt?name="+record_name,grid_vip=config.grid_vip)
    	print(TXT_record)
    	PTR_record = ib_NIOS.wapi_request('GET', object_type="record:ptr?ptrdname="+record_name,grid_vip=config.grid_vip)
    	print(PTR_record)
    	if record_name in A_record and record_name in TXT_record and record_name in PTR_record:
        	assert True
        	print(record_name+" added in A and TXT and PTR records ")
    	else:
        	print(record_name+" not added in A and TXT and PTR records ")
        	assert False	
	print("***** Record validation is completed *****")

def IPv6_records_validation(grid=config.grid_vip):
        print("***** Record validation is started *****")
        record_name = re.search('Added new forward map from(.*)by server ',log_validation)
        record_name = record_name.group(0)
        def Convert(string):
                li = list(string.split(" "))
                return li
        str1 = Convert(record_name)
        record_name = str1[5]
        print(record_name)
        sleep(10)
        A_record = ib_NIOS.wapi_request('GET', object_type="record:aaaa?name="+record_name, grid_vip=config.grid_vip)
        print(A_record)
        TXT_record = ib_NIOS.wapi_request('GET', object_type="record:txt?name="+record_name,grid_vip=config.grid_vip)
        print(TXT_record)
        PTR_record = ib_NIOS.wapi_request('GET', object_type="record:ptr?ptrdname="+record_name,grid_vip=config.grid_vip)
        print(PTR_record)
        if record_name in A_record and record_name in TXT_record and record_name in PTR_record:
                assert True
                print(record_name+" added in AAAA and TXT and PTR records ")
        else:
                print(record_name+" not added in AAAA and TXT and PTR records ")
                assert False
        print("***** IPv6 Record validation is completed *****")

def enable_ipv4_and_ipv6_dns_interface_on_all_members(grid=config.grid_vip):
        log_print("Fetch member dns reference")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        log_print(get_ref)
        for ref in json.loads(get_ref):
            member_ref = ref['_ref']
            data = {"enable_dns":True,"use_lan_ipv6_port":True}
            response = ib_NIOS.wapi_request('PUT',ref=member_ref,fields=json.dumps(data), grid_vip=config.grid_vip)
            log_print(response)
            if bool(re.match("\"member:dns*.",str(response))):
                log_print("IPv4 DNS interface set for member "+ref['host_name'])
                sleep(5)
            else:
                log_print("Unable to set IPv4 DNS interface for member "+ref['host_name'])
                assert False
	sleep(20)
        log_print("Successfully enabled IPv4 interface on all the members")

def enable_ipv4_and_ipv6_dns_on_member(i):
        log_print("Fetch member dns reference")
        member_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        print(member_ref)
        ref = json.loads(member_ref)[i]['_ref']
        print(ref)
        data = {"enable_dns":True,"use_lan_ipv6_port":True}
        response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data))
        log_print(response)
        if i == 1 :
                i = "first"
        elif i == 2:
                i = "second"
        elif i == 3:
                i = "third"
        elif i == 4:
                i = "fourth"
        if bool(re.match("\"member:dns*.",str(response))):
                assert True
                sleep(05)
        else:
                log_print("Failed to disable DNS service on "+i+" member")
                assert False
        sleep(15)
        log_print("\nEnabled DNS service on "+i+" member")


def disable_ipv4_and_ipv6_dns_on_member(i):
	log_print("Fetch member dns reference")
        member_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        print(member_ref)
        ref = json.loads(member_ref)[i]['_ref']
        print(ref)
        data = {"enable_dns":False,"use_lan_ipv6_port":False}
        response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data))
        print(response)
        if i == 1 :
                i = "first"
        elif i == 2:
                i = "second"
        elif i == 3:
                i = "third"
        elif i == 4:
                i = "fourth"
        if bool(re.match("\"member:dns*.",str(response))):
		assert True
                sleep(05)
        else:
                log_print("Failed to disable DNS service on "+i+" member")
                assert False
	sleep(15)
	log_print("\nDisabled DNS service on "+i+" member")



class RFE_5514(unittest.TestCase):


    @pytest.mark.run(order=1)
    def test_001_Enable_NTP_Service_on_all_the_grid_members(self):
        log_print("\n***************************************************")
        log_print("* TC 1 : Enable NTP service on all the grid members *")
        log_print("*****************************************************")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member?_return_fields=ntp_setting", grid_vip=config.grid_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            data={"ntp_setting":{"enable_ntp": True}}
            response = ib_NIOS.wapi_request('PUT',ref=ref['_ref'],fields=json.dumps(data), grid_vip=config.grid_vip)
            log_print(response)
            if bool(re.match("\"member*.",str(response))):
                log_print("NTP enabled on member "+ref['_ref'].split(':')[1])
            else:
                log_print("NTP service failed to start on member "+ref['_ref'].split(':')[1])
                assert False
            sleep(2)
	print("Test Case 001 Execution Completed")

    @pytest.mark.run(order=2)
    def test_002_Add_MultiMaster_Auth_Zones_in_default_Network_view(self):
        log_print("\n*********************************************************")
        log_print("* TC 2: Add Multi-master Auth zones in default Network view *")
        log_print("***************************************************")
        log_print("Creating zone test1.com")
        data={"fqdn":"test1.com","view":"default","grid_primary":[{"name": config.grid_member1_fqdn,"stealth": False},{"name": config.grid_member2_fqdn,"stealth": False},{"name": config.grid_member3_fqdn,"stealth": False}]}
        test1_ref=ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data))
        log_print(test1_ref)
        if bool(re.match("\"zone_auth*.*test1.com",str(test1_ref))):
		log_print("Zone test1.com creation successful")
		print("\n")
        	sleep(5)
        else:
	        log_print("Zone test1.com creation unsuccessful")
	    	print("\n")
            	assert False

        log_print("Creating zone test2.com")
        data={"fqdn":"test2.com","view":"default","grid_primary":[{"name": config.grid_member3_fqdn,"stealth": False},{"name": config.grid_member2_fqdn,"stealth": False},{"name": config.grid_member1_fqdn,"stealth": False}]}
        test2_ref=ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data))
        log_print(test2_ref)
        if bool(re.match("\"zone_auth*.*test2.com",str(test2_ref))):
            	log_print("Zone test2.com creation successful")
	    	print("\n")
            	sleep(5)
        else:
            	log_print("Zone test2.com creation unsuccessful")
	    	print("\n")
            	assert False
        log_print("Creating sub zone sub.test1.com")
        data={"fqdn":"sub.test1.com","view":"default","grid_primary":[{"name": config.grid_member1_fqdn,"stealth": False},{"name": config.grid_member2_fqdn,"stealth": False},{"name": config.grid_member3_fqdn,"stealth": False}]}
        test3_ref=ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data))
        log_print(test3_ref)
        if bool(re.match("\"zone_auth*.*sub.test1.com",str(test3_ref))):
            	log_print("Zone sub.test1.com creation successful")
		print("\n")
            	sleep(5)
        else:
            	log_print("Zone sub.test1.com creation unsuccessful")
		print("\n")
            	assert False

	log_print("Creating sub zone sub.test2.com")
        data={"fqdn":"sub.test2.com","view":"default","grid_primary":[{"name": config.grid_member1_fqdn,"stealth": False},{"name": config.grid_member3_fqdn,"stealth": False},{"name": config.grid_member2_fqdn,"stealth": False}]}
        test4_ref=ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data))
        log_print(test4_ref)
        if bool(re.match("\"zone_auth*.*sub.test2.com",str(test4_ref))):
            	log_print("Zone sub.test2.com creation successful")
		print("\n")
            	sleep(5)
        else:
            	log_print("Zone sub.test2.com creation unsuccessful")
		print("\n")
            	assert False

        log_print("Creating zone test3.com")
        data={"fqdn":"test3.com","view":"default","grid_primary":[{"name": config.grid_member1_fqdn,"stealth": False},{"name": config.grid_member2_fqdn,"stealth": False},{"name": config.grid_member3_fqdn,"stealth": False}]}
        test4_ref=ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data))
        log_print(test4_ref)
        if bool(re.match("\"zone_auth*.*test3.com",str(test4_ref))):
                log_print("Zone test3.com creation successful")
                print("\n")
                sleep(5)
        else:
                log_print("Zone test3.com creation unsuccessful")
                print("\n")
                assert False

        log_print("Creating zone test4.com")
        data={"fqdn":"test4.com","view":"default","grid_primary":[{"name": config.grid_member1_fqdn,"stealth": False},{"name": config.grid_member2_fqdn,"stealth": False},{"name": config.grid_member3_fqdn,"stealth": False}]}
        test4_ref=ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data))
        log_print(test4_ref)
        if bool(re.match("\"zone_auth*.*test4.com",str(test4_ref))):
                log_print("Zone test4.com creation successful")
                print("\n")
                sleep(5)
        else:
                log_print("Zone test4.com creation unsuccessful")
                print("\n")
                assert False
	print("Test Case 002 Execution Completed")

    @pytest.mark.run(order=3)
    def test_003_Add_authoritative_reverse_mapping_zone_in_default_dns_view(self):
        log_print("\n*****************************************************")
        log_print(" TC : 3 Add authoritative reverse mapping zone in default dns view")
        log_print("******************************************************")
	data = {"fqdn": "0.0.10.in-addr.arpa","zone_format":"IPV4","grid_primary": [{"name": config.grid_member_fqdn,"stealth": False},{"name": config.grid_member1_fqdn,"stealth": False},{"name": config.grid_member2_fqdn,"stealth": False},{"name": config.grid_member3_fqdn,"stealth": False}],"view": "default"}
        response=ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data))
        print(response)
        if bool(re.match("\"zone_auth*.*0.0.10.in-addr.arpa",str(response))):
                log_print("10.0.0.0/24 RPMZ creation successful")
                sleep(5)
        else:
                log_print("10.0.0.0/24 RMZ creation unsuccessful")
                assert False
	print("Test Case 003 Execution Completed")

    @pytest.mark.run(order=4)
    def test_004_Add_IPv6_Authoritative_reverse_mapping_zone_in_default_dns_view(self):
        log_print("\n*****************************************************")
        log_print(" TC : 4 Add Authoritative reverse mapping zone in default dns view")
        log_print("******************************************************")
        ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
        ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
        data = {"fqdn": ipv6_network+"::/64","zone_format":"IPV6","grid_primary": [{"name": config.grid_member_fqdn,"stealth": False},{"name": config.grid_member1_fqdn,"stealth": False},{"name": config.grid_member2_fqdn,"stealth": False},{"name": config.grid_member3_fqdn,"stealth": False}],"view": "default"}
        ref=ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data))
        print(ref)
        print("Test Case 004 Execution Completed")

    @pytest.mark.run(order=5)
    def test_005_Add_Network_10_0_0_0_24_with_members_assignment_in_default_network_view(self):
        log_print("\n***************************************************")
        log_print("* TC : 5 - Add network 10.0.0.0/24 with members assignment in default network view *")
        log_print("*****************************************************")
        #data = {"network": "10.0.0.0/24","network_view": "default","members":[{"_struct": "dhcpmember","ipv4addr":config.grid_vip}]}
	data = {"network": "10.0.0.0/24","network_view": "default","members": [{"_struct": "dhcpmember","ipv4addr": config.grid_master_vip},{"_struct": "dhcpmember","ipv4addr": config.grid_member1_vip},{"_struct": "dhcpmember","ipv4addr": config.grid_member2_vip},{"_struct": "dhcpmember","ipv4addr": config.grid_member3_vip}]}
        response = ib_NIOS.wapi_request('POST', object_type='network', fields=json.dumps(data))
        log_print(response)
        if bool(re.match("\"network*.*10.0.0.0",str(response))):
            	log_print("Network 10.0.0.0/24 creation successful")
		sleep(5)	
        else:
		log_print("Network 10.0.0.0/24 creation unsuccessful")
            	assert False
	print("Test Case 005 Execution Completed")

    @pytest.mark.run(order=6)
    def test_006_Add_range_to_network_10_0_0_0_24_and_assign_GM(self):
        log_print("\n***************************************************")
        log_print("* TC : 6 - Add range to network 10.0.0.0/24 and assign GM *")
        log_print("***************************************************")
        data = {"network":"10.0.0.0/24","start_addr":"10.0.0.1","end_addr":"10.0.0.50","network_view": "default","member": {"_struct": "dhcpmember","ipv4addr": config.grid_vip},"name": "Range1"}
        response = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(data), grid_vip=config.grid_vip)
        log_print(response)
        if bool(re.match("\"range*.",str(response))):
            	log_print("Network range creation successful")
		sleep(5)
        else:
            log_print("Network range creation unsuccessful")
            assert False
	print("Test Case 006 Execution Completed")

    @pytest.mark.run(order=7)
    def test_007_create_IPv6_network_with_members_assignment_in_default_network_view(self):
        log_print("\n************************************************************")
        log_print("* TC : 7 - Create an ipv6 network with members assignment in default network view *")
        log_print("**************************************************************")
        #global ipv6_network
        ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
        ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
        data = {"network": ipv6_network+"::/64","network_view": "default","members": [{"_struct": "dhcpmember","ipv6addr": config.master1_ipv6_ip,"name": config.grid_member_fqdn},{"_struct": "dhcpmember","ipv6addr": config.member1_ipv6_ip,"name": config.grid_member1_fqdn},{"_struct": "dhcpmember","ipv6addr": config.member2_ipv6_ip,"name": config.grid_member2_fqdn},{"_struct": "dhcpmember","ipv6addr": config.member3_ipv6_ip,"name": config.grid_member3_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="ipv6network", fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if bool(re.match("\"ipv6network*.*64",str(response))):
                log_print(ipv6_network+" Network creation successful")
                sleep(5)
        else:
                log_print(ipv6_network+" Network creation unsuccessful")
                assert False
        print("Test Case 007 Execution Completed")

    @pytest.mark.run(order=8)
    def test_008_create_IPv6_address_Range_and_assign_GM(self):
        log_print("\n************************************************************")
        log_print("* TC : 8 - Create ipv6 address range and assign GM *")
        log_print("**************************************************************")
        ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
        ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
        data ={"end_addr": ipv6_network+"::100","network": ipv6_network+"::/64","network_view": "default","start_addr": ipv6_network+"::10","member": {"_struct": "dhcpmember","ipv6addr": config.master1_ipv6_ip,"name": config.grid_member_fqdn}}
        print(data)
        response = ib_NIOS.wapi_request('POST', object_type="ipv6range", fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if bool(re.match("\"ipv6range*.",str(response))):
                log_print(ipv6_network+" Network range creation successful")
                sleep(5)
        else:
            log_print(ipv6_network+" Network range creation unsuccessful")
            assert False
        print("\nTest Case 008 Execution Completed")


    @pytest.mark.run(order=9)
    def test_009_Enable_IPv4_DDNS_Updates_in_grid_DHCP_properties(self):
        log_print("\n***************************************************")
        log_print("* TC : 9 - Enable IPv4 DDNS updates in Grid DHCP Properties                 *")
        log_print("*****************************************************")
        log_print("Fetch grid dhcp properties reference")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
        log_print(get_ref)
        grid_dhcp_ref = json.loads(get_ref)[0]['_ref']
        data = {"options":[{"name":"domain-name","value":"test1.com"}],"enable_ddns":True,"ddns_domainname":"test1.com","ddns_generate_hostname": True,"ddns_update_fixed_addresses": True,"ddns_use_option81": True}
        response = ib_NIOS.wapi_request('PUT',ref=grid_dhcp_ref,fields=json.dumps(data), grid_vip=config.grid_vip)
        if bool(re.match("\"grid:dhcpproperties*.",str(response))):
            log_print("DDNS update enabled successfully")
            sleep(5)
        else:
            log_print("Enabling DDNS update unsuccessful")
            assert False
	print("Test Case 009 Execution Completed")

    @pytest.mark.run(order=10)
    def test_010_Enable_IPv6_DDNS_Updates_in_grid_DHCP_properties(self):
        log_print("\n***************************************************")
        log_print("* TC : 10 - IPv6 Enable DDNS updates in Grid DHCP Properties *")
        log_print("*****************************************************")
        log_print("Fetch grid dhcp properties reference")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
        log_print(get_ref)
        grid_dhcp_ref = json.loads(get_ref)[0]['_ref']
        print(grid_dhcp_ref)
        data = {"ipv6_ddns_domainname": "test1.com","ipv6_ddns_enable_option_fqdn": True,"ipv6_domain_name": "test1.com","ipv6_enable_ddns": True,"ipv6_generate_hostname": True}
        response = ib_NIOS.wapi_request('PUT',ref=grid_dhcp_ref,fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if bool(re.match("\"grid:dhcpproperties*.",str(response))):
                log_print("DDNS update enabled successfully")
                sleep(5)
        else:
            log_print("Enabling DDNS update unsuccessful")
            assert False
        print("Test Case 10 Execution Completed")


    @pytest.mark.run(order=11)
    def test_011_Enable_Allow_Updates_in_grid_DNS_properties(self):
        log_print("\n***************************************************")
        log_print("* TC : 11 - Enable Allow updates in Grid DNS Properties *")
        log_print("***************************************************")
        log_print("Fetch grid dns properties reference")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns", grid_vip=config.grid_vip)
        log_print(get_ref)
        grid_dns_ref = json.loads(get_ref)[0]['_ref']
        data = {"allow_update":[{"_struct":"addressac","address":"Any","permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('PUT',ref=grid_dns_ref,fields=json.dumps(data), grid_vip=config.grid_vip)
        log_print("Printing response")
        log_print(response)
        if bool(re.match("\"grid:dns*.",str(response))):
            log_print("Allow update enabled successfully")
            sleep(5)
        else:
            log_print("Enabling Allow update unsuccessful")
            assert False
	print("Test Case 011 Execution Completed")

    @pytest.mark.run(order=12)
    def test_012_Enable_IPv4_and_IPv6_DHCP_interface_on_all_members(self):
        log_print("\n*****************************************************")
        log_print("* TC : 12 - Enable IPv4 & IPv6 DHCP interface on all members*")
        log_print("******************************************************")
        log_print("Fetch member dhcp properties  reference")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
        log_print("Member DHCP properties reference")
        log_print(get_ref)
        for ref in json.loads(get_ref):
            member_ref = ref['_ref']
            data = {"enable_dhcp":True,"enable_dhcpv6_service":True}
            response = ib_NIOS.wapi_request('PUT',ref=member_ref,fields=json.dumps(data), grid_vip=config.grid_vip)
            log_print(response)
            if bool(re.match("\"member:dhcpproperties*.",str(response))):
                log_print("IPv4 DHCP interface set for member "+ref['host_name'])
                sleep(5)
            else:
                log_print("Unable to set IPv4 DHCP interface for member "+ref['host_name'])
                assert False
	sleep(20)
        print("Test Case 012 Execution Completed")

    @pytest.mark.run(order=13)
    def test_013_Enable_IPv4_and_IPv6_DNS_interface_on_all_members(self):
        log_print("\n************************************************************")
        log_print("* TC : 13 - Enable IPv4 & IPv6 DNS interface on all members******")
        log_print("**************************************************************")
	enable_ipv4_and_ipv6_dns_interface_on_all_members()
        print("Test Case 013 Execution Completed")


    @pytest.mark.run(order=14)
    def test_014_Add_MultiMaster_Zones_For_DDNS_Updates_under_the_configure_DDNS_properties(self):
        log_print("\n***************************************************")
        log_print("* TC : 14 - Add MultiMaster Zones For DDNS Updates under the configure DDNS properties *")
        log_print("***************************************************")
        log_print("Fetch test1.com reference")
        ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
        ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
        zone_ref = ''
        for ref in json.loads(get_ref):
            if ref['fqdn'] == 'test1.com':
                zone_ref = ref['_ref']
        log_print(zone_ref)
        reverse_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=10.0.0.0/24",grid_vip=config.grid_vip)
        reverse_ref = json.loads(reverse_ref)[0]['_ref']
        print(reverse_ref)
        ipv6_reverse_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn="+ipv6_network+"::/64",grid_vip=config.grid_vip)
        ipv6_reverse_ref = json.loads(ipv6_reverse_ref)[0]['_ref']
        print(ipv6_reverse_ref)
        networkview_ref = ib_NIOS.wapi_request('GET', object_type="networkview", grid_vip=config.grid_vip)
        networkview_ref = json.loads(networkview_ref)[0]['_ref']
        data = {"ddns_dns_view": "default","ddns_zone_primaries": [{"dns_grid_primary":config.grid_member1_fqdn,"dns_grid_zone": {"_ref": reverse_ref},"zone_match": "GRID"},{"dns_grid_primary": config.grid_member2_fqdn,"dns_grid_zone": {"_ref": reverse_ref},"zone_match": "GRID"},{"dns_grid_primary": config.grid_member3_fqdn,"dns_grid_zone": {"_ref": reverse_ref},"zone_match": "GRID"},{"dns_grid_primary": config.grid_member1_fqdn,"dns_grid_zone": {"_ref": zone_ref},"zone_match": "GRID"},{"dns_grid_primary": config.grid_member2_fqdn,"dns_grid_zone": {"_ref": zone_ref},"zone_match": "GRID"},{"dns_grid_primary": config.grid_member3_fqdn,"dns_grid_zone": {"_ref": zone_ref},"zone_match": "GRID"},{"dns_grid_primary":config.grid_member1_fqdn,"dns_grid_zone": {"_ref": ipv6_reverse_ref},"zone_match": "GRID"},{"dns_grid_primary":config.grid_member2_fqdn,"dns_grid_zone": {"_ref": ipv6_reverse_ref},"zone_match": "GRID"},{"dns_grid_primary":config.grid_member3_fqdn,"dns_grid_zone": {"_ref": ipv6_reverse_ref},"zone_match": "GRID"}]}
        response = ib_NIOS.wapi_request('PUT',ref=networkview_ref,fields=json.dumps(data), grid_vip=config.grid_vip)
        log_print(response)
        if bool(re.match("\"networkview*.",str(response))):
            log_print("MMDNS zones are added to the preferred multi domain ddns list at configure ddns properties ")
	    sleep(30)
            restart_services()
        else:
            log_print("Failed to add multimaster zones to the preferred multi domain ddns list at configure ddns properties")
            assert False
	print("Test Case 014 Execution Completed")


    @pytest.mark.run(order=15)
    def test_015_Check_if_dhcpd_conf_file_contains_3_DNS_nameservers_configured_as_part_of_the_preferred_multi_domain_ddns_list(self):
        log_print("\n************************************************************************************")
        log_print("* TC : 15 - Check if dhcpd.conf file contains 3 nameservers as part of preferred multi domain ddns list *")
        log_print("************************************************************************************")
	sleep(30)
        try:
            os.system('scp root@'+config.grid_vip+':/infoblox/var/dhcpd_conf/dhcpd.conf .')
        except OSError as e:
            log_print("Scp failed")
            log_print(e)
            assert False

        try:
            file = open("dhcpd.conf",'r')
            file_content = file.read()
            file.close()
            log_print("\n\n")
            log_print(file_content)
            data1 = 'zone "test1.com." {\n\tprimary '+config.grid_member1_vip+', '+config.grid_member2_vip+', '+config.grid_member3_vip+';'
	    data2 = 'zone "0.0.10.in-addr.arpa." {\n\tprimary '+config.grid_member1_vip+', '+config.grid_member2_vip+', '+config.grid_member3_vip+';'
            if data1 in file_content and data2 in file_content:
                log_print("The dhcpd.conf file contains 3 nameservers as part of the preferred multi domain ddns list")
		print(data1)
		print(data2)
                assert True
            else:
                log_print("The dhcpd.conf file does not contain 3 nameservers as part of the preferred multi domain ddns list")
                assert False
        except IOError as e:
            log_print("Unable to open dhcpd.conf file")
            log_print(e)
            assert False
	print("Test Case 015 Execution Completed")

    @pytest.mark.run(order=16)
    def test_016_Check_if_dhcpdv6_conf_file_contains_3_DNS_nameservers_configured_as_part_of_preferred_multi_domain_ddns_list(self):
        log_print("\n************************************************************************************")
        log_print("* TC : 16 - Check if dhcpd.conf file contains 3 nameservers as part of preferred multi domain ddns list *")
        log_print("************************************************************************************")
	sleep(30)
        try:
            os.system('scp root@'+config.grid_vip+':/infoblox/var/dhcpdv6_conf/dhcpdv6.conf .')
        except OSError as e:
            log_print("Scp failed")
            log_print(e)
            assert False

        try:
            file = open("dhcpdv6.conf",'r')
            file_content = file.read()
            file.close()
            log_print("\n\n")
            log_print(file_content)
            data = 'zone "test1.com." {\n\tprimary '+config.grid_member1_vip+', '+config.grid_member2_vip+', '+config.grid_member3_vip+';'
            if data in file_content:
                log_print("The dhcpdv6.conf file contains 3 nameservers as part of preferred multi domain ddns list")
                print(data)
                assert True
            else:
                log_print("The dhcpdv6.conf file does not contain 3 nameservers as part of preferred multi domain ddns list")
                assert False
        except IOError as e:
            log_print("Unable to open dhcpdv6.conf file")
            log_print(e)
            assert False
        print("Test Case 016 Execution Completed")

    @pytest.mark.run(order=17)
    def test_017_Add_4_nameservers_to_the_preferred_multi_domain_ddns_list_for_configuring_DDNS_properties_and_verify_the_error_message(self):
        log_print("\n***************************************************")
        log_print("* TC : 17 - Add 4 nameservers to the preferred multi-domain ddns list for configuring DDNS properties and verify the error message  *")
        log_print("***************************************************")
        log_print("Fetch test1.com reference")
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
        zone_ref = ''
        for ref in json.loads(get_ref):
            if ref['fqdn'] == 'test1.com':
                zone_ref = ref['_ref']
        log_print(zone_ref)
        data = {"ddns_zone_primaries":[{"dns_grid_primary":config.grid_member1_fqdn,"dns_grid_zone":{"_ref":zone_ref},"zone_match": "GRID"},{"dns_grid_primary":config.grid_member2_fqdn,"dns_grid_zone":{"_ref":zone_ref},"zone_match": "GRID"},{"dns_grid_primary":config.grid_member3_fqdn,"dns_grid_zone":{"_ref":zone_ref},"zone_match": "GRID"},{"dns_grid_primary":config.grid_member4_fqdn,"dns_grid_zone":{"_ref":zone_ref},"zone_match": "GRID"}]}
        get_ref = ib_NIOS.wapi_request('GET', object_type="networkview", grid_vip=config.grid_vip)
        networkview_ref = json.loads(get_ref)[0]['_ref']
        log_print(networkview_ref)
	status,response = ib_NIOS.wapi_request('PUT',ref=networkview_ref,fields=json.dumps(data),grid_vip=config.grid_vip)
	print(response)
	data = "For each zone, a maximum of three primary DNS servers can be configured for a DNS failover"
        if data in response:
		assert True
		print("Validated **"+data+"**")
        else:
		assert False
        print("Test Case 017 Execution Completed")

    @pytest.mark.run(order=18)
    def test_018_Request_IPv4_lease_capture_syslogs_validate_DNS_NS1_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 18 - Request lease and capture syslogs and validate the first dns name server used for ddns updates in syslogs and added A, TXT and PTR records *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
	global log_validation
        for i in range(10):
		dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F test1.com'
            	print(dras_cmd)
            	dras_cmd = os.system(dras_cmd)
            	sleep(02)
            	print("output is ",dras_cmd)
               	if dras_cmd == 0:
                      	print("Got the lease")
                       	break
               	else:
                       	print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
	LookFor = 'by server'
	log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
	print(log_validation)
	data = ['Added new forward map from.*by server '+config.grid_member1_vip+'#53','Added reverse map from.*by server '+config.grid_member1_vip+'#53']
	for i in data:
		result = re.search(i,log_validation)
		if result == None:
			assert False
		else:
			assert True
	IPv4_records_validation()
        print("\nTest Case 018 Executed Successfully")

    @pytest.mark.run(order=19)
    def test_019_Request_IPv6_lease_capture_syslogs_validate_DNS_NS1_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 19 - Request ipv6 lease and capture syslogs and validate the dns name server used for ddns updates in syslogs and added AAAA, TXT and PTR records *")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.master1_ipv6_ip)+' -A -n 1 -h test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member1_vip+'#53','Added reverse map from.*by server '+config.grid_member1_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv6_records_validation()
        print("\nTest Case 019 Executed Successfully")


    @pytest.mark.run(order=20)
    def test_020_Disable_IPv4_and_IPv6_DNS_interface_on_DNS_NS1_from_the_preferred_Multi_Domaine_DDNS_list(self):
        log_print("\n****************************************************************************************************************")
        log_print("******** Disable IPv4 and IPv6 DNS interface on first DNS server from the preferred Multi Domaine DDNS list ******")
        log_print("******************************************************************************************************************")
	disable_ipv4_and_ipv6_dns_on_member(1)
        print("Test Case 020 Execution Completed")

    @pytest.mark.run(order=21)
    def test_021_Request_IPv4_lease_capture_syslogs_validate_DNS_NS2_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 21 - Request lease and capture syslogs and validate the second dns name server used for ddns updates in syslogs and added A, TXT and PTR records *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
	global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member2_vip+'#53','Added reverse map from.*by server '+config.grid_member2_vip+'#53']
        for i in data:
                result = re.search(i,log_validation)
                if result == None:
                        assert False
                else:
                        assert True
	IPv4_records_validation()
        print("\nTest Case 021 Executed Successfully")

    @pytest.mark.run(order=22)
    def test_022_Request_IPv6_lease_capture_syslogs_validate_DNS_NS2_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 22 - Request ipv6 lease and capture syslogs and validate the dns name server used for ddns updates in syslogs and added AAAA, TXT and PTR records *")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.master1_ipv6_ip)+' -A -n 1 -h test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member2_vip+'#53','Added reverse map from.*by server '+config.grid_member2_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv6_records_validation()
        print("\nTest Case 022 Executed Successfully")


    @pytest.mark.run(order=23)
    def test_023_Disable_IPv4_and_IPv6_DNS_interface_on_DNS_NS2_from_the_preferred_Multi_Domaine_DDNS_list(self):
        log_print("\n******************************************************")
        log_print("** TC :23 -  Disable IPv4 and IPv6 DNS interface on second DNS server from the preferred Multi Domaine DDNS list ******")
        log_print("********************************************************")
        disable_ipv4_and_ipv6_dns_on_member(2)
        print("Test Case 023 Execution Completed")

    @pytest.mark.run(order=24)
    def test_024_Request_IPv4_lease_capture_syslogs_validate_DNS_NS3_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 24 - Request lease and capture syslogs and validate the third dns name server used for ddns updates in syslogs and added A, TXT and PTR records  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
	global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member3_vip+'#53','Added reverse map from.*by server '+config.grid_member3_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
	IPv4_records_validation()
        print("\nTest Case 024 Executed Successfully")

    @pytest.mark.run(order=25)
    def test_025_Request_IPv6_lease_capture_syslogs_validate_DNS_NS3_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 25 - Request ipv6 lease and capture syslogs and validate the dns name server used for ddns updates in syslogs and added AAAA, TXT and PTR records")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.master1_ipv6_ip)+' -A -n 1 -h test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member3_vip+'#53','Added reverse map from.*by server '+config.grid_member3_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv6_records_validation()
        print("\nTest Case 025 Executed Successfully")


    @pytest.mark.run(order=26)
    def test_026_Disable_IPv4_and_IPv6_DNS_interface_on_DNS_NS3_from_the_preferred_Multi_Domaine_DDNS_list(self):
        log_print("\n***************************************************************")
        log_print("* TC : 26 - Disable IPv4 and IPv6 DNS interface on third DNS server from the preferred Multi Domaine DDNS list*")
        log_print("*****************************************************************")
        disable_ipv4_and_ipv6_dns_on_member(3)      
        print("Test Case 026 Execution Completed")


    @pytest.mark.run(order=27)
    def test_027_Request_IPv4_lease_capture_syslogs_and_validate_deferred_ddns_updates_in_syslogs(self):
        log_print("\n************************************************************")
        log_print("* TC : 27 - Request lease and capture syslogs and validate deferred ddns updates in syslogs *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
	global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'deferred'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Addition of forward map for.*deferred','Addition of reverse map for.*deferred']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        print("\nTest Case 027 Executed Successfully")

    @pytest.mark.run(order=28)
    def test_028_Request_IPv6_lease_capture_syslogs_and_validate_deferred_ddns_updates_in_syslogs(self):
        log_print("\n************************************************************")
        log_print("TC : 28 - Request ipv6 lease and capture syslogs and validate deferred ddns updates in syslogs")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.master1_ipv6_ip)+' -A -n 1 -h test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'deferred'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Addition of forward map for.*deferred','Addition of reverse map for.*deferred']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        print("\nTest Case 028 Executed Successfully")

    @pytest.mark.run(order=29)
    def test_029_Enable_IPv4_and_IPv6_DNS_interface_on_all_members(self):
        log_print("\n************************************************************")
        log_print("**TC : 29 - Enable IPv4 & IPv6 DNS interface on all members******")
        log_print("**************************************************************")
        enable_ipv4_and_ipv6_dns_interface_on_all_members()
        print("Test Case 029 Execution Completed")


########################################################
## Sub Zone Scenarios at Grid level (configure ddns)  ##
########################################################

    @pytest.mark.run(order=30)
    def test_030_Update_sub_zone_name_as_ddns_domain_name_in_grid_dhcp_properties(self):
        log_print("\n************************************************************")
        log_print("* TC : 30 - Update sub zone name as ddns domain name in grid dhcp properties *")
        log_print("**************************************************************")
        log_print("Fetch grid dhcp properties reference")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
        log_print(get_ref)
        grid_dhcp_ref = json.loads(get_ref)[0]['_ref']
        print(grid_dhcp_ref)
        data={"ipv6_ddns_domainname": "sub.test1.com","ipv6_domain_name": "sub.test1.com","options":[{"name":"domain-name","value":"sub.test1.com"}],"ddns_domainname":"sub.test1.com"}
        response = ib_NIOS.wapi_request('PUT',ref=grid_dhcp_ref,fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if bool(re.match("\"grid:dhcpproperties*.",str(response))):
                log_print("sub domain name updated successfully for DDNS domain name in grid dhcp properties")
                sleep(15)
                restart_services()
        else:
            log_print("Enabling DDNS update unsuccessful")
            assert False
        print("Test Case 030 Execution Completed")


    @pytest.mark.run(order=31)
    def test_031_Add_MultiMaster_Zones_For_DDNS_Updates_under_the_configure_DDNS_properties(self):
        log_print("\n***************************************************")
        log_print("* TC : 31 - Add Multimaster Zones for DDNS updates    *")
        log_print("***************************************************")
        log_print("Fetch sub.test1.com reference")
        sub_zone_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=sub.test1.com", grid_vip=config.grid_vip)
        sub_zone_ref = json.loads(sub_zone_ref)[0]['_ref']
        log_print(sub_zone_ref)
        reverse_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=10.0.0.0/24",grid_vip=config.grid_vip)
        reverse_ref = json.loads(reverse_ref)[0]['_ref']
        print(reverse_ref)
        ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
        ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
        ipv6_reverse_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn="+ipv6_network+"::/64",grid_vip=config.grid_vip)
        ipv6_reverse_ref = json.loads(ipv6_reverse_ref)[0]['_ref']
        print(ipv6_reverse_ref)
        networkview_ref = ib_NIOS.wapi_request('GET', object_type="networkview?name=default", grid_vip=config.grid_vip)
        networkview_ref = json.loads(networkview_ref)[0]['_ref']
        data = {"ddns_dns_view": "default","ddns_zone_primaries": [{"dns_grid_primary":config.grid_member1_fqdn,"dns_grid_zone": {"_ref": reverse_ref},"zone_match": "GRID"},{"dns_grid_primary": config.grid_member2_fqdn,"dns_grid_zone": {"_ref": reverse_ref},"zone_match": "GRID"},{"dns_grid_primary": config.grid_member3_fqdn,"dns_grid_zone": {"_ref": reverse_ref},"zone_match": "GRID"},{"dns_grid_primary":config.grid_member1_fqdn,"dns_grid_zone": {"_ref": ipv6_reverse_ref},"zone_match": "GRID"},{"dns_grid_primary":config.grid_member2_fqdn,"dns_grid_zone": {"_ref": ipv6_reverse_ref},"zone_match": "GRID"},{"dns_grid_primary":config.grid_member3_fqdn,"dns_grid_zone": {"_ref": ipv6_reverse_ref},"zone_match": "GRID"},{"dns_grid_primary": config.grid_member1_fqdn,"dns_grid_zone": {"_ref": sub_zone_ref},"zone_match": "GRID"},{"dns_grid_primary": config.grid_member2_fqdn,"dns_grid_zone": {"_ref": sub_zone_ref},"zone_match": "GRID"},{"dns_grid_primary": config.grid_member3_fqdn,"dns_grid_zone": {"_ref": sub_zone_ref},"zone_match": "GRID"}]}
        response = ib_NIOS.wapi_request('PUT',ref=networkview_ref,fields=json.dumps(data), grid_vip=config.grid_vip)
        log_print(response)
        if bool(re.match("\"networkview*.",str(response))):
            log_print("Multimaster zones added to the list of zones in DDNS updates")
	    sleep(30)
            restart_services()
        else:
            log_print("Failed to add multimaster zones to list of zones in DDNS updates")
            assert False
        print("Test Case 031 Execution Completed")

    @pytest.mark.run(order=32)
    def test_032_Check_if_dhcpd_conf_file_contains_3_DNS_nameservers_configured_as_part_of_the_preferred_multi_domain_ddns_list(self):
        log_print("\n************************************************************************************")
        log_print("* TC : 32 - Check if dhcpd.conf file contains 3 nameservers as part of preferred multi domain ddns list *")
        log_print("************************************************************************************")
        sleep(30)
        try:
            os.system('scp root@'+config.grid_vip+':/infoblox/var/dhcpd_conf/dhcpd.conf .')
        except OSError as e:
            log_print("Scp failed")
            log_print(e)
            assert False

        try:
            file = open("dhcpd.conf",'r')
            file_content = file.read()
            file.close()
            log_print("\n\n")
            log_print(file_content)
            data1 = 'zone "sub.test1.com." {\n\tprimary '+config.grid_member1_vip+', '+config.grid_member2_vip+', '+config.grid_member3_vip+';'
            data2 = 'zone "0.0.10.in-addr.arpa." {\n\tprimary '+config.grid_member1_vip+', '+config.grid_member2_vip+', '+config.grid_member3_vip+';'
            if data1 in file_content and data2 in file_content:
                log_print("The dhcpd.conf file contains 3 nameservers as part of multimaster zone")
                print(data1)
                print(data2)
                assert True
            else:
                log_print("The dhcpd.conf file does not contain 3 nameservers as part of multimaster zone")
                assert False
        except IOError as e:
            log_print("Unable to open dhcpd.conf file")
            log_print(e)
            assert False
        print("Test Case 032 Execution Completed")

    @pytest.mark.run(order=33)
    def test_033_Check_if_dhcpdv6_conf_file_contains_3_DNS_nameservers_configured_as_part_of_preferred_multi_domain_ddns_list(self):
        log_print("\n************************************************************************************")
        log_print("* TC : 33 - Check if dhcpd.conf file contains 3 nameservers as part of preferred multi domain ddns list *")
        log_print("************************************************************************************")
        sleep(30)
        try:
            os.system('scp root@'+config.grid_vip+':/infoblox/var/dhcpdv6_conf/dhcpdv6.conf .')
        except OSError as e:
            log_print("Scp failed")
            log_print(e)
            assert False

        try:
            file = open("dhcpdv6.conf",'r')
            file_content = file.read()
            file.close()
            log_print("\n\n")
            log_print(file_content)
            data1 = 'zone "sub.test1.com." {\n\tprimary '+config.grid_member1_vip+', '+config.grid_member2_vip+', '+config.grid_member3_vip+';'
	    data2 = 'ip6.arpa." {\n\tprimary '+config.grid_member1_vip+', '+config.grid_member2_vip+', '+config.grid_member3_vip+';'
            if data1 in file_content and data2 in file_content:
                log_print("The dhcpdv6.conf file contains 3 nameservers as part of multimaster zone")
                print(data1)
		print(data2)
                assert True
            else:
                log_print("The dhcpdv6.conf file does not contain 3 nameservers as part of multimaster zone")
                assert False
        except IOError as e:
            log_print("Unable to open dhcpdv6.conf file")
            log_print(e)
            assert False
        print("Test Case 033 Execution Completed")

    @pytest.mark.run(order=34)
    def test_034_Request_IPv4_lease_capture_syslogs_validate_DNS_NS1_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 34 - Request lease and capture syslogs and validate the first dns name server used for ddns updates in syslogs and added A, TXT and PTR records  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(20)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F sub.test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member1_vip+'#53','Added reverse map from.*by server '+config.grid_member1_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv4_records_validation()
        print("\nTest Case 034 Executed Successfully")

    @pytest.mark.run(order=35)
    def test_035_Request_IPv6_lease_capture_syslogs_validate_DNS_NS_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 35 - Request ipv6 lease and capture syslogs and validate the dns name server used for ddns updates in syslogs and added AAAA, TXT and PTR records *")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.master1_ipv6_ip)+' -A -n 1 -h sub.test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member1_vip+'#53','Added reverse map from.*by server '+config.grid_member1_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv6_records_validation()
        print("\nTest Case 035 Executed Successfully")

    @pytest.mark.run(order=36)
    def test_036_Disable_IPv4_and_IPv6_DNS_interface_on_DNS_NS1_from_the_preferred_Multi_Domaine_DDNS_list(self):
        log_print("\n***************************************************************")
        log_print("* TC : 36 - Disable IPv4 and IPv6 DNS interface on first DNS server from the preferred Multi Domaine DDNS list ******")
        log_print("*****************************************************************")
        disable_ipv4_and_ipv6_dns_on_member(1)
	print("\nTest Case 036 Executed Successfully")

    @pytest.mark.run(order=37)
    def test_037_Request_IPv4_lease_capture_syslogs_validate_DNS_NS2_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 37 - Request lease and capture syslogs and validate the second dns name server used for ddns updates in syslogs and added A, TXT and PTR records  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(20)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F sub.test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member2_vip+'#53','Added reverse map from.*by server '+config.grid_member2_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv4_records_validation()
        print("\nTest Case 037 Executed Successfully")

    @pytest.mark.run(order=38)
    def test_038_Request_IPv6_lease_capture_syslogs_validate_DNS_NS_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 38 - Request ipv6 lease and capture syslogs and validate the dns name server used for ddns updates in syslogs and added AAAA, TXT and PTR records *")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.master1_ipv6_ip)+' -A -n 1 -h sub.test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member2_vip+'#53','Added reverse map from.*by server '+config.grid_member2_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv6_records_validation()
        print("\nTest Case 038 Executed Successfully")

    @pytest.mark.run(order=39)
    def test_039_Disable_IPv4_and_IPv6_DNS_interface_on_DNS_NS2_from_the_preferred_Multi_Domaine_DDNS_list(self):
        log_print("\n***************************************************************")
        log_print("*** TC : 39 - Disable IPv4 and IPv6 DNS interface on second DNS server from the preferred Multi Domaine DDNS list ******")
        log_print("*****************************************************************")
        disable_ipv4_and_ipv6_dns_on_member(2)
        print("\nTest Case 39 Executed Successfully")

    @pytest.mark.run(order=40)
    def test_040_Request_IPv4_lease_capture_syslogs_validate_DNS_NS3_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 40 - Request lease and capture syslogs and validate the third dns name server used for ddns updates in syslogs and added A, TXT and PTR records  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(20)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F sub.test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member3_vip+'#53','Added reverse map from.*by server '+config.grid_member3_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv4_records_validation()
        print("\nTest Case 040 Executed Successfully")

    @pytest.mark.run(order=41)
    def test_041_Request_IPv6_lease_capture_syslogs_validate_DNS_NS_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 41 - Request ipv6 lease and capture syslogs and validate the dns name server used for ddns updates in syslogs and added AAAA, TXT and PTR records *")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.master1_ipv6_ip)+' -A -n 1 -h sub.test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member3_vip+'#53','Added reverse map from.*by server '+config.grid_member3_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv6_records_validation()
        print("\nTest Case 041 Executed Successfully")

    @pytest.mark.run(order=42)
    def test_042_Disable_IPv4_and_IPv6_DNS_interface_on_DNS_NS3_from_the_preferred_Multi_Domaine_DDNS_list(self):
        log_print("\n***************************************************************")
        log_print("* TC : 42 - Disable IPv4 and IPv6 DNS interface on third DNS server from the preferred Multi Domaine DDNS list ******")
        log_print("*****************************************************************")
        disable_ipv4_and_ipv6_dns_on_member(3)
        print("Test Case 042 Execution Completed")


    @pytest.mark.run(order=43)
    def test_043_Request_IPv4_lease_capture_syslogs_validate_deferred_ddns_updates_in_syslogs(self):
        log_print("\n************************************************************")
        log_print("* TC : 43 - Request lease and capture syslogs and validate deferred ddns updates in syslogs  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F sub.test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'deferred'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Addition of forward map for.*deferred','Addition of reverse map for.*deferred']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        print("\nTest Case 043 Executed Successfully")


    @pytest.mark.run(order=44)
    def test_044_Request_IPv6_lease_capture_syslogs_validate_deferred_ddns_updates_in_syslogs(self):
        log_print("\n************************************************************")
        log_print("* TC : 44 - Request ipv6 lease and capture syslogs and validate deferred ddns updates in syslogs *")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.master1_ipv6_ip)+' -A -n 1 -h sub.test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'deferred'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Addition of forward map for.*deferred','Addition of reverse map for.*deferred']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        print("\nTest Case 044 Executed Successfully")

    @pytest.mark.run(order=45)
    def test_045_Enable_IPv4_and_IPv6_DNS_interface_on_DNS_NS2_from_the_preferred_Multi_Domaine_DDNS_list(self):
        log_print("\n*****************************************************")
        log_print("* TC : 45 - Enable IPv4 and IPv6 DNS interface on second DNS server from the preferred Multi Domaine DDNS list *")
        log_print("******************************************************")
	enable_ipv4_and_ipv6_dns_on_member(2)
        print("Test Case 045 Execution Completed")


    @pytest.mark.run(order=46)
    def test_046_Request_IPv4_lease_capture_syslogs_validate_DNS_NS2_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 46 - Request lease and capture syslogs and validate the second dns name server used for ddns updates in syslogs and added A, TXT and PTR records  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(20)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F sub.test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member2_vip+'#53','Added reverse map from.*by server '+config.grid_member2_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv4_records_validation()
        print("\nTest Case 046 Executed Successfully")

    @pytest.mark.run(order=47)
    def test_047_Request_IPv6_lease_capture_syslogs_validate_DNS_NS2_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 47 - Request ipv6 lease and capture syslogs and validate the second dns name server used for ddns updates in syslogs and added AAAA, TXT and PTR records *")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.master1_ipv6_ip)+' -A -n 1 -h sub.test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member2_vip+'#53','Added reverse map from.*by server '+config.grid_member2_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv6_records_validation()
        print("\nTest Case 047 Executed Successfully")

#################Sub Zone cases ended ###################################################################################################################


    @pytest.mark.run(order=48)
    def test_048_Add_list_of_nameservers_for_DDNS_updates_under_the_configure_DDNS_properties_with_one_nameserver_not_part_of_zone(self):
        log_print("\n***************************************************************************************************************************")
        log_print("* TC : 48 - Add list of nameservers for DDNS updates under the configure DDNS properties with one nameserver not part of zone *")
        log_print("***************************************************************************************************************************")
	log_print("** Enable IPv4 and IPv6 DNS interface on all members **")
	enable_ipv4_and_ipv6_dns_interface_on_all_members()
	log_print("*******************************************************")
        log_print("Fetch test1.com reference")
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
        zone_ref = ''
        for ref in json.loads(get_ref):
            if ref['fqdn'] == 'test1.com':
                zone_ref = ref['_ref']
        log_print(zone_ref)
        data = {"ddns_zone_primaries":[{"dns_grid_primary":config.grid_member_fqdn,"dns_grid_zone":{"_ref":zone_ref},"zone_match": "GRID"}]}
        get_ref = ib_NIOS.wapi_request('GET', object_type="networkview", grid_vip=config.grid_vip)
        networkview_ref = json.loads(get_ref)[0]['_ref']
        log_print(networkview_ref)
        status,response = ib_NIOS.wapi_request('PUT',ref=networkview_ref,fields=json.dumps(data), grid_vip=config.grid_vip)
        log_print(response)
        data = config.grid_member_fqdn+"\' is not a DNS primary for zone \'test1.com\' in DNS view \'default\', so it cannot be used with that zone in DDNS update master preferences"
        if data in response:
                assert True
                print("\n")
                print("validated ***"+data+"***")
        else:
                assert False
        sleep(05)
        print("Test Case 048 Execution Completed")

###########################################################################################
################# Default Primary scenarions at default network view ######################
###########################################################################################

    @pytest.mark.run(order=49)
    def test_049_Add_3_Default_Primary_DNS_Nameservers_For_DDNS_Updates_under_the_configure_DDNS_properties(self):
        log_print("\n***************************************************")
        log_print("* TC : 49 - Add Multimaster Zones for DDNS updates    *")
        log_print("***************************************************")
        log_print("Fetch test1.com reference")
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
        zone_ref = ''
        for ref in json.loads(get_ref):
            if ref['fqdn'] == 'test1.com':
                zone_ref = ref['_ref']
        log_print(zone_ref)
        data = {"ddns_dns_view": "default","ddns_zone_primaries": [{"dns_grid_primary": config.grid_member3_fqdn,"zone_match": "ANY_GRID"},{"dns_grid_primary": config.grid_member2_fqdn,"zone_match": "ANY_GRID"},{"dns_grid_primary": config.grid_member1_fqdn,"zone_match": "ANY_GRID"}]}
        get_ref = ib_NIOS.wapi_request('GET', object_type="networkview", grid_vip=config.grid_vip)
        networkview_ref = json.loads(get_ref)[0]['_ref']
        log_print(networkview_ref)
        response = ib_NIOS.wapi_request('PUT',ref=networkview_ref,fields=json.dumps(data), grid_vip=config.grid_vip)
        log_print(response)
        if bool(re.match("\"networkview*.",str(response))):
            log_print("Multimaster zones added to the list of zones in DDNS updates")
	    sleep(15)
            restart_services()
        else:
            log_print("Failed to add multimaster zones to list of zones in DDNS updates")
            assert False
        print("Test Case 049Execution Completed")

    @pytest.mark.run(order=50)
    def test_050_Check_if_dhcpd_conf_file_contains_3_Default_Primary_DNS_NS_configured_as_part_of_preferred_multi_domain_ddns_list(self):
        log_print("\n************************************************************************************")
        log_print("* TC : 50 - Check if dhcpd.conf file contains 3 nameservers as part of preferred multi domain ddns list *")
        log_print("************************************************************************************")
	sleep(30)
        try:
            os.system('scp root@'+config.grid_vip+':/infoblox/var/dhcpd_conf/dhcpd.conf .')
        except OSError as e:
            log_print("Scp failed")
            log_print(e)
            assert False

        try:
            file = open("dhcpd.conf",'r')
            file_content = file.read()
            file.close()
            log_print("\n\n")
            log_print(file_content)
            #data1 = 'zone "test1.com." {\n\tprimary '+config.grid_member3_vip+', '+config.grid_member2_vip+', '+config.grid_member1_vip+';'
	    data1 = 'zone "sub.test1.com." {\n\tprimary '+config.grid_member3_vip+', '+config.grid_member2_vip+', '+config.grid_member1_vip+';'
	    data2 = 'zone "0.0.10.in-addr.arpa." {\n\tprimary '+config.grid_member3_vip+', '+config.grid_member2_vip+', '+config.grid_member1_vip+';'
            if data1 in file_content and data2 in file_content:
                log_print("The dhcpd.conf file contains 3 nameservers as part of multimaster zone")
                print(data1)
		print(data2)
                assert True
       	    else:
                log_print("The dhcpd.conf file does not contain 3 nameservers as part of multimaster zone")
                assert False
        except IOError as e:
            log_print("Unable to open dhcpd.conf file")
            log_print(e)
            assert False
        print("Test Case 050 Execution Completed")


    @pytest.mark.run(order=51)
    def test_051_Check_if_dhcpdv6_conf_file_contains_3_Default_Primary_DNS_NS_configured_is_not_part_of_preferred_multi_domain_ddns_list(self):
        log_print("\n************************************************************************************")
        log_print("* TC : 51 - Check if dhcpd.conf file contains default primary dns nameserver which is not part of preferred multi domain ddns list *")
        log_print("************************************************************************************")
	sleep(30)
        try:
            os.system('scp root@'+config.grid_vip+':/infoblox/var/dhcpdv6_conf/dhcpdv6.conf .')
        except OSError as e:
            log_print("Scp failed")
            log_print(e)
            assert False

        try:
            file = open("dhcpdv6.conf",'r')
            file_content = file.read()
            file.close()
            log_print("\n\n")
            log_print(file_content)
	    #data1 = 'zone "test1.com." {\n\tprimary '+config.grid_member3_vip+', '+config.grid_member2_vip+', '+config.grid_member1_vip+';'
	    data1 = 'zone "sub.test1.com." {\n\tprimary '+config.grid_member3_vip+', '+config.grid_member2_vip+', '+config.grid_member1_vip+';'
            data2 = 'ip6.arpa." {\n\tprimary '+config.grid_member3_vip+', '+config.grid_member2_vip+', '+config.grid_member1_vip+';'
            if data1 in file_content and data2 in file_content:
                log_print("default primary dns nameserver is present in dhcpdv6.conf")
                print(data1)
		print(data2)
		#print(data3)
                assert True
            else:
                log_print("default primary dns nameserver not resent in dhcpdv6.conf")
                assert False
        except IOError as e:
            log_print("Unable to open dhcpdv6.conf file")
            log_print(e)
            assert False
        print("Test Case 051 Execution Completed")


    @pytest.mark.run(order=52)
    def test_052_Request_IPv4_lease_capture_syslogs_validate_DNS_NS1_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 52 - Request lease and capture syslogs and validate the first dns name server used for ddns updates in syslogs and added A, TXT and PTR records  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
	sleep(30)
        log("start","/var/log/syslog",config.grid_vip)
	global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F sub.test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member3_vip+'#53','Added reverse map from.*by server '+config.grid_member3_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
	IPv4_records_validation()
        print("\nTest Case 052 Executed Successfully")

    @pytest.mark.run(order=53)
    def test_053_Request_IPv6_lease_capture_syslogs_validate_DNS_NS1_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 53 - Request ipv6 lease and capture syslogs and validate the first dns name server used for ddns updates in syslogs and added AAAA, TXT and PTR records *")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.master1_ipv6_ip)+' -A -n 1 -h sub.test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member3_vip+'#53','Added reverse map from.*by server '+config.grid_member3_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv6_records_validation()
        print("\nTest Case 53 Executed Successfully")


    @pytest.mark.run(order=54)
    def test_054_Disable_IPv4_and_IPv6_DNS_interface_on_DNS_NS1_from_the_preferred_Multi_Domaine_DDNS_list(self):
        log_print("\n*****************************************************")
        log_print("* TC : 54 - Disable IPv4 and IPv6 DNS interface on third DNS server from the preferred Multi Domaine DDNS list *")
        log_print("******************************************************")
        disable_ipv4_and_ipv6_dns_on_member(3)
        print("Test Case 054 Execution Completed")

    @pytest.mark.run(order=55)
    def test_055_Request_IPv4_lease_capture_syslogs_validate_DNS_NS2_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 55 - Request lease and capture syslogs and validate the second dns name server used for ddns updates in syslogs and added A, TXT and PTR records  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
	global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F sub.test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member2_vip+'#53','Added reverse map from.*by server '+config.grid_member2_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
	IPv4_records_validation()
        print("\nTest Case 055 Executed Successfully")

    @pytest.mark.run(order=56)
    def test_056_Request_IPv6_lease_capture_syslogs_validate_DNS_NS2_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 56 - Request ipv6 lease and capture syslogs and validate the second dns name server used for ddns updates in syslogs and added AAAA, TXT and PTR records *")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.master1_ipv6_ip)+' -A -n 1 -h sub.test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member2_vip+'#53','Added reverse map from.*by server '+config.grid_member2_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv6_records_validation()
        print("\nTest Case 056 Executed Successfully")


    @pytest.mark.run(order=57)
    def test_057_Disable_IPv4_and_IPv6_DNS_interface_on_DNS_NS2_from_the_preferred_Multi_Domaine_DDNS_list(self):
        log_print("\n*****************************************************")
        log_print("* TC : 57 - Disable IPv4 and IPv6 DNS interface on first DNS server from the preferred Multi Domaine DDNS list *")
        log_print("******************************************************")
	disable_ipv4_and_ipv6_dns_on_member(2)
        print("Test Case 057 Execution Completed")


    @pytest.mark.run(order=58)
    def test_058_Request_IPv4_lease_capture_syslogs_validate_DNS_NS3_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 58 - Request lease and capture syslogs and validate the third dns name server used for ddns updates in syslogs and added A, TXT and PTR records  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
	global log_validation
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
	global log_validation 
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F sub.test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member1_vip+'#53','Added reverse map from.*by server '+config.grid_member1_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv4_records_validation()
        print("\nTest Case 058 Executed Successfully")

    @pytest.mark.run(order=59)
    def test_059_Request_IPv6_lease_capture_syslogs_validate_DNS_NS3_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 59 - Request ipv6 lease and capture syslogs and validate the third dns name server used for ddns updates in syslogs and added AAAA, TXT and PTR records *")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.master1_ipv6_ip)+' -A -n 1 -h sub.test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member1_vip+'#53','Added reverse map from.*by server '+config.grid_member1_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv6_records_validation()
        print("\nTest Case 059 Executed Successfully")


    @pytest.mark.run(order=60)
    def test_060_Disable_IPv4_and_IPv6_DNS_interface_on_DNS_NS3_from_the_preferred_Multi_Domaine_DDNS_list(self):
        log_print("\n*****************************************************")
        log_print("* TC : 60 - Disable IPv4 and IPv6 DNS interface on first DNS server from the preferred Multi Domaine DDNS list *")
        log_print("******************************************************")
	disable_ipv4_and_ipv6_dns_on_member(1)
        print("Test Case 060 Execution Completed")

    @pytest.mark.run(order=61)
    def test_061_Request_IPv4_lease_capture_syslogs_validate_deferred_ddns_updates_in_syslogs(self):
        log_print("\n************************************************************")
        log_print("* TC : 61 - Request lease and capture syslogs and validate deferred ddns updates in syslogs  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F sub.test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'deferred'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Addition of forward map for.*deferred','Addition of reverse map for.*deferred']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        print("\nTest Case 061 Executed Successfully")

    @pytest.mark.run(order=62)
    def test_062_Request_IPv6_lease_capture_syslogs_validate_deferred_ddns_updates_in_syslogs(self):
        log_print("\n************************************************************")
        log_print("* TC : 62 - Request ipv6 lease and capture syslogs and validate deferred ddns updates in syslogs *")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.master1_ipv6_ip)+' -A -n 1 -h sub.test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'deferred'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Addition of forward map for.*deferred','Addition of reverse map for.*deferred']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        print("\nTest Case 062 Executed Successfully")


    @pytest.mark.run(order=63)
    def test_063_Add_Default_Primary_DNS_nameserver_which_is_not_part_multi_master_zone_for_DDNS_updates_under_the_configure_DDNS_properties(self):
        log_print("\n***************************************************************************************************************************")
        log_print("* TC : 63 - Add default primary dns nameserver which is not part of multi master zone for DDNS updates under the configure DDNS properties*")
        log_print("***************************************************************************************************************************")
        log_print("Fetch test1.com reference")
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
        zone_ref = ''
        for ref in json.loads(get_ref):
            if ref['fqdn'] == 'test1.com':
                zone_ref = ref['_ref']
        log_print(zone_ref)
        data = {"ddns_zone_primaries":[{"dns_grid_primary":config.grid_member_fqdn,"zone_match": "ANY_GRID"}]}
        get_ref = ib_NIOS.wapi_request('GET', object_type="networkview", grid_vip=config.grid_vip)
        networkview_ref = json.loads(get_ref)[0]['_ref']
        log_print(networkview_ref)
        response = ib_NIOS.wapi_request('PUT',ref=networkview_ref,fields=json.dumps(data), grid_vip=config.grid_vip)
        log_print(response)
	if bool(re.match("\"networkview*.",str(response))):
            log_print("Multimaster zones added to the list of zones in DDNS updates")
	    sleep(15)
            restart_services()
        else:
            log_print("Failed to add multimaster zones to list of zones in DDNS updates")
            assert False
        print("Test Case 063 Execution Completed")

    @pytest.mark.run(order=64)
    def test_064_Check_if_dhcpd_conf_file_contains_configured_Default_Primary_DNS_NS_which_is_not_part_of_test1_com_multimaster_zone(self):
        log_print("\n************************************************************************************")
        log_print("* TC : 64 - Check if dhcpd.conf file contains configured Default Primary DNS NS which is not part of test1 com multimaster zone *")
        log_print("************************************************************************************")
	sleep(30)
        try:
            os.system('scp root@'+config.grid_vip+':/infoblox/var/dhcpd_conf/dhcpd.conf .')
        except OSError as e:
            log_print("Scp failed")
            log_print(e)
            assert False

        try:
            file = open("dhcpd.conf",'r')
            file_content = file.read()
            file.close()
            log_print("\n\n")
            log_print(file_content)
	    data = 'zone "0.0.10.in-addr.arpa." {\n\tprimary 127.0.0.1;'
            if data in file_content:
                log_print("default primary dns nameserver is present in dhcpd.conf")
                print(data)
                assert True
            else:
                log_print("default primary dns nameserver not resent in dhcpd.conf")
                assert False
        except IOError as e:
            log_print("Unable to open dhcpd.conf file")
            log_print(e)
            assert False
        print("Test Case 064 Execution Completed")

    @pytest.mark.run(order=65)
    def test_065_Check_if_dhcpdv6_conf_file_contains_configured_Default_Primary_DNS_NS_which_is_not_part_of_test1_com_multimaster_zone(self):
        log_print("\n************************************************************************************")
        log_print("* TC : 65 - Check if dhcpdv6.conf file contains configured Default Primary DNS NS which is not part of test1 com multimaster zone *")
        log_print("************************************************************************************")
	sleep(30)
        try:
            os.system('scp root@'+config.grid_vip+':/infoblox/var/dhcpdv6_conf/dhcpdv6.conf .')
        except OSError as e:
            log_print("Scp failed")
            log_print(e)
            assert False

        try:
            file = open("dhcpdv6.conf",'r')
            file_content = file.read()
            file.close()
            log_print("\n\n")
            log_print(file_content)
            data = 'ip6.arpa." {\n\tprimary 127.0.0.1;'
            if data in file_content:
                log_print("default primary dns nameserver is present in dhcpdv6.conf")
                print(data)
                assert True
            else:
                log_print("default primary dns nameserver not resent in dhcpdv6.conf")
                assert False
        except IOError as e:
            log_print("Unable to open dhcpdv6.conf file")
            log_print(e)
            assert False
        print("Test Case 065 Execution Completed")


#################### Default primary scenarios at default networkview (Configure DDNS)  end here ############


#####################################################
## Custom network view scenarios ##############
#################################################


    @pytest.mark.run(order=66)
    def test_066_Add_and_Validate_custom_network_view(self):
        log_print("\n************************************************************")
        log_print("* TC : 66 - Add and Validate custom network view *")
        log_print("**************************************************************")
        logging.info("adding and validating network view")
        data = {"name": "custom"}
        response = ib_NIOS.wapi_request('POST', object_type="networkview",fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)
        if bool(re.match("\"networkview*.*custom/false",str(response))):
                log_print("Network view custom creation successful")
                sleep(15)
                restart_services()
        else:
                log_print("Network view custom creation unsuccessful")
                print("\n")
                assert False
        print("\nTest Case 066 Execution Completed")
   
    @pytest.mark.run(order=67)
    def test_067_Add_Network_10_0_0_0_24_with_members_assignment_in_custom_network_view(self):
        log_print("\n***************************************************")
        log_print("* TC : 67 - Add Network 10.0.0.0/24 in custom network view *")
        log_print("*****************************************************")
        data = {"network": "10.0.0.0/24","network_view": "custom","members":[{"_struct": "dhcpmember","ipv4addr":config.grid_member4_vip}]}
        response = ib_NIOS.wapi_request('POST', object_type='network', fields=json.dumps(data))
        log_print(response)
        if bool(re.match("\"network*.*10.0.0.0",str(response))):
                log_print("Network 10.0.0.0/24 creation successful")
                sleep(15)
		restart_services()
        else:
                log_print("Network 10.0.0.0/24 creation unsuccessful")
                assert False
        print("Test Case 067 Execution Completed")

    @pytest.mark.run(order=68)
    def test_068_Add_range_to_network_10_0_0_0_24(self):
        log_print("\n***************************************************")
        log_print("* TC : 68 - Add range to network 10.0.0.0/24            *")
        log_print("***************************************************")
	data = {"network":"10.0.0.0/24","start_addr":"10.0.0.1","end_addr":"10.0.0.50","network_view": "custom","member": {"_struct": "dhcpmember","ipv4addr": config.grid_member4_vip},"name": "Range1"}
        response = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(data), grid_vip=config.grid_vip)
        log_print(response)
        if bool(re.match("\"range*.",str(response))):
                log_print("Network range creation successful")
                sleep(15)
		restart_services()
        else:
            log_print("Network range creation unsuccessful")
            assert False
        print("Test Case 068 Execution Completed")

    @pytest.mark.run(order=69)
    def test_069_Create_IPv6_network_with_members_assignment_in_custom_network_view(self):
        log_print("\n************************************************************")
        log_print("* TC : 69 - Create IPv6 network with members assignment in custom network view *")
        log_print("**************************************************************")
        #global ipv6_network
        ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
        ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
        data = {"network": ipv6_network+"::/64","network_view": "custom","members": [{"_struct": "dhcpmember","ipv6addr": config.member4_ipv6_ip,"name": config.grid_member4_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="ipv6network", fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if bool(re.match("\"ipv6network*.*64",str(response))):
                log_print(ipv6_network+" IPv6 Network creation successful")
                sleep(15)
                restart_services()
        else:
                log_print(ipv6_network+" IPv6 Network creation unsuccessful")
                assert False
        print("Test Case 069 Execution Completed")

    @pytest.mark.run(order=70)
    def test_070_create_IPv6_address_Range(self):
        log_print("\n************************************************************")
        log_print("* TC : 70 - Add range to IPv6 network *")
        log_print("**************************************************************")
        logging.info("Creating ipv6 address range")
        ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
        ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
        data ={"end_addr": ipv6_network+"::100","network": ipv6_network+"::/64","network_view": "custom","start_addr": ipv6_network+"::10","member": {"_struct": "dhcpmember","ipv6addr": config.member4_ipv6_ip,"name": config.grid_member4_fqdn}}
        print(data)
        response = ib_NIOS.wapi_request('POST', object_type="ipv6range", fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if bool(re.match("\"ipv6range*.",str(response))):
                log_print(ipv6_network+" IPv6 Network range creation successful")
                sleep(15)
                restart_services()
        else:
            log_print(ipv6_network+" IPv6 Network range creation unsuccessful")
            assert False
        print("\nTest Case 070 Execution Completed")

    @pytest.mark.run(order=71)
    def test_071_Create_custom_dns_view_in_custom_network_view(self):
        log_print("\n************************************************************")
        log_print("* TC : 71 - Create custom dns view in custom network view *")
        log_print("**************************************************************")
        data = {"name": "custom_dns_view","network_view": "custom"}
        print(data)
        response = ib_NIOS.wapi_request('POST', object_type="view", fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if bool(re.match("\"view*.*custom_dns_view/false",str(response))):
            log_print("Multimaster zones added to the list of zones in DDNS updates")
	    sleep(15)
            restart_services()
        else:
            log_print("Failed to add multimaster zones to list of zones in DDNS updates")
            assert False
        print("Test Case 071 Execution Completed")

    @pytest.mark.run(order=72)
    def test_072_Add_MultiMaster_Auth_Zones_in_custom_dns_view(self):
        log_print("\n*****************************************************")
        log_print("* TC : 72 - Add Multi-master Auth zone custom_test1.com in custom dns view **")
        log_print("*******************************************************")
        #data={"fqdn":"custom_test1.com","view":"custom_dns_view","grid_primary":[{"name": config.grid_member4_fqdn,"stealth": False}]}
	data={"fqdn":"custom_test1.com","view":"custom_dns_view","grid_primary":[{"name": config.grid_member1_fqdn,"stealth": False},{"name": config.grid_member2_fqdn,"stealth": False},{"name": config.grid_member3_fqdn,"stealth": False},{"name": config.grid_member4_fqdn,"stealth": False}]}
        test1_ref=ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data))
        log_print(test1_ref)
        if bool(re.match("\"zone_auth*.*custom_test1.com",str(test1_ref))):
                log_print("Zone custom_test1.com creation successful")
                sleep(15)
                restart_services()
        else:
                log_print("Zone custom_test1.com creation unsuccessful")
                print("\n")
                assert False
        print("Test Case 072 Execution Completed")


    @pytest.mark.run(order=73)
    def test_073_Add_authoritative_reverse_mapping_zone_in_custom_dns_view(self):
        log_print("\n**********************************************************")
        log_print(" TC : 73 - adding authoritative reverse mapping zone in custom dns view")
        log_print("************************************************************")
        #data = {"fqdn": "0.0.10.in-addr.arpa","zone_format":"IPV4","grid_primary": [{"name": config.grid_member4_fqdn,"stealth": False}],"view": "custom_dns_view"}
	data = {"fqdn": "0.0.10.in-addr.arpa","zone_format":"IPV4","grid_primary": [{"name": config.grid_member1_fqdn,"stealth": False},{"name": config.grid_member2_fqdn,"stealth": False},{"name": config.grid_member3_fqdn,"stealth": False},{"name": config.grid_member4_fqdn,"stealth": False}],"view": "custom_dns_view"}
        response=ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data))
        print(response)
        if bool(re.match("\"zone_auth*.*custom_dns_view",str(response))):
                log_print("10.0.0.0/24 reverse mapping zone creation successful")
                sleep(15)
                restart_services()
        else:
                log_print("10.0.0.0/24 reverse mapping zone creation unsuccessful")
                print("\n")
                assert False
        print("Test Case 073 Execution Completed")

    @pytest.mark.run(order=74)
    def test_074_Add_IPv6_authoritative_reverse_mapping_zone_in_custom_dns_view(self):
        log_print("\n*****************************************************")
        log_print(" TC : 74 - adding IPv6 authoritative reverse mapping zone in custom dns view")
        log_print("******************************************************")
        ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
        ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
        #data = {"fqdn": ipv6_network+"::/64","zone_format":"IPV6","grid_primary": [{"name": config.grid_member4_fqdn,"stealth": False}],"view": "custom_dns_view"}
	data = {"fqdn": ipv6_network+"::/64","zone_format":"IPV6","grid_primary": [{"name": config.grid_member1_fqdn,"stealth": False},{"name": config.grid_member2_fqdn,"stealth": False},{"name": config.grid_member3_fqdn,"stealth": False},{"name": config.grid_member4_fqdn,"stealth": False}],"view": "custom_dns_view"}
        response=ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data))
        print(response)
        if bool(re.match("\"zone_auth*.*custom_dns_view",str(response))):
                log_print("IPv6 Network reverse mapping zone creation successful")
                sleep(15)
                restart_services()
        else:
                log_print("IPv6 Network reverse mapping zone creation unsuccessful")
                print("\n")
                assert False
        print("Test Case 074 Execution Completed")

    @pytest.mark.run(order=75)
    def test_075_Enable_IPv4_and_IPv6_DNS_interface_on_all_members(self):
        log_print("\n**************************************************************")
        log_print("* TC : 75 - Enable IPv4 and IPv6 DNS interface on all members******")
        log_print("****************************************************************")
        enable_ipv4_and_ipv6_dns_interface_on_all_members()
	print("Test Case 075  Execution Completed")
	
    @pytest.mark.run(order=76)
    def test_076_Update_custom_dns_view_domain_as_ddns_domain_name_in_grid_dhcp_properties(self):
        log_print("\n***************************************************")
        log_print("* TC : 76 - Update custom dns view domain custom_test1.com as ddns domain name in grid dhcp properties *")
        log_print("*****************************************************")
        log_print("Fetch grid dhcp properties reference")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
        log_print(get_ref)
        grid_dhcp_ref = json.loads(get_ref)[0]['_ref']
        print(grid_dhcp_ref)
        data={"ipv6_ddns_domainname": "custom_test1.com","ipv6_domain_name": "custom_test1.com","options":[{"name":"domain-name","value":"custom_test1.com"}],"ddns_domainname":"custom_test1.com"}
        response = ib_NIOS.wapi_request('PUT',ref=grid_dhcp_ref,fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if bool(re.match("\"grid:dhcpproperties*.",str(response))):
                log_print("updated DDNS domain name at grid dhcp properties successfully")
                sleep(15)
                restart_services()
        else:
            log_print("failed updating DDNS domain name at grid dhcp properties")
            assert False
        print("Test Case 76 Execution Completed")

    @pytest.mark.run(order=77)
    def test_077_Add_MultiMaster_Zones_For_DDNS_Updates_under_the_configure_DDNS_properties(self):
        log_print("\n***************************************************")
        log_print("* TC : 77 - Add Multimaster Zone custom_test1.com for DDNS updates under the configure DDNS properties *")
        log_print("***************************************************")
        log_print("Fetch test1.com reference")
        ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
        ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=custom_test1.com", grid_vip=config.grid_vip)
	zone_ref = json.loads(get_ref)[0]['_ref']
        log_print(zone_ref)
        reverse_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=10.0.0.0/24",grid_vip=config.grid_vip)
        reverse_ref = json.loads(reverse_ref)[0]['_ref']
        log_print(reverse_ref)
        ipv6_reverse_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn="+ipv6_network+"::/64",grid_vip=config.grid_vip)
        ipv6_reverse_ref = json.loads(ipv6_reverse_ref)[0]['_ref']
        log_print(ipv6_reverse_ref)
        networkview_ref = ib_NIOS.wapi_request('GET', object_type="networkview?name=custom", grid_vip=config.grid_vip)
        networkview_ref = json.loads(networkview_ref)[0]['_ref']
	data = {"ddns_dns_view": "custom_dns_view","ddns_zone_primaries": [{"dns_grid_primary":config.grid_member1_fqdn,"dns_grid_zone": {"_ref": reverse_ref},"zone_match": "GRID"},{"dns_grid_primary": config.grid_member2_fqdn,"dns_grid_zone": {"_ref": reverse_ref},"zone_match": "GRID"},{"dns_grid_primary": config.grid_member3_fqdn,"dns_grid_zone": {"_ref": reverse_ref},"zone_match": "GRID"},{"dns_grid_primary": config.grid_member1_fqdn,"dns_grid_zone": {"_ref": zone_ref},"zone_match": "GRID"},{"dns_grid_primary": config.grid_member2_fqdn,"dns_grid_zone": {"_ref": zone_ref},"zone_match": "GRID"},{"dns_grid_primary": config.grid_member3_fqdn,"dns_grid_zone": {"_ref": zone_ref},"zone_match": "GRID"},{"dns_grid_primary":config.grid_member1_fqdn,"dns_grid_zone": {"_ref": ipv6_reverse_ref},"zone_match": "GRID"},{"dns_grid_primary":config.grid_member2_fqdn,"dns_grid_zone": {"_ref": ipv6_reverse_ref},"zone_match": "GRID"},{"dns_grid_primary":config.grid_member3_fqdn,"dns_grid_zone": {"_ref": ipv6_reverse_ref},"zone_match": "GRID"}]}
	response = ib_NIOS.wapi_request('PUT',ref=networkview_ref,fields=json.dumps(data), grid_vip=config.grid_vip)
        log_print(response)
        if bool(re.match("\"networkview*.",str(response))):
            log_print("Multimaster zones added to the list of zones in DDNS updates")
	    sleep(15)
            restart_services()
        else:
            log_print("Failed to add multimaster zones to list of zones in DDNS updates")
            assert False	
        print("Test Case 077 Execution Completed")


    @pytest.mark.run(order=78)
    def test_078_Check_if_the_dhcpd_conf_file_contains_3_DNS_NS_configured_as_part_of_the_preferred_multi_domain_ddns_list(self):
        log_print("\n************************************************************************************")
        log_print("* TC : 78 - Check if the dhcpd conf file contains 3 DNS NS configured as part of the preferred multi domain ddns list *")
        log_print("************************************************************************************")
	sleep(30)
        try:
            os.system('scp -o StrictHostKeyChecking=no root@'+config.grid_member4_vip+':/infoblox/var/dhcpd_conf/dhcpd.conf .')
        except OSError as e:
            log_print("Scp failed")
            log_print(e)
            assert False

        try:
            file = open("dhcpd.conf",'r')
            file_content = file.read()
            file.close()
            log_print("\n\n")
            log_print(file_content)
            data1 = 'zone "custom_test1.com." {\n\tprimary '+config.grid_member1_vip+', '+config.grid_member2_vip+', '+config.grid_member3_vip+';'
            data2 = 'zone "0.0.10.in-addr.arpa." {\n\tprimary '+config.grid_member1_vip+', '+config.grid_member2_vip+', '+config.grid_member3_vip+';'
            if data1 in file_content and data2 in file_content:
                log_print("The dhcpd.conf file contains 3 nameservers as part of preferred multi domain ddns list ")
                print(data1)
                print(data2)
                assert True
            else:
                log_print("The dhcpd.conf file does not contain 3 nameservers as part of preferred multi domain ddns list ")
                assert False
        except IOError as e:
            log_print("Unable to open dhcpd.conf file")
            log_print(e)
            assert False
        print("Test Case 078 Execution Completed")

    @pytest.mark.run(order=79)
    def test_079_Check_if_the_dhcpdv6_conf_file_contains_3_DNS_NS_configured_as_part_of_the_preferred_multi_domain_ddns_list(self):
        log_print("\n************************************************************************************")
        log_print("* TC : 79 - Check if dhcpd.conf file contains 3 nameservers as part of preferred multi domain ddns list *")
        log_print("************************************************************************************")
	sleep(30)
        try:
            os.system('scp -o StrictHostKeyChecking=no root@'+config.grid_member4_vip+':/infoblox/var/dhcpdv6_conf/dhcpdv6.conf .')
        except OSError as e:
            log_print("Scp failed")
            log_print(e)
            assert False

        try:
            file = open("dhcpdv6.conf",'r')
            file_content = file.read()
            file.close()
            log_print("\n\n")
            log_print(file_content)
	    data1 = 'zone "custom_test1.com." {\n\tprimary '+config.grid_member1_vip+', '+config.grid_member2_vip+', '+config.grid_member3_vip+';'
            data2 = 'ip6.arpa." {\n\tprimary '+config.grid_member1_vip+', '+config.grid_member2_vip+', '+config.grid_member3_vip+';'
            if data1 in file_content and data2 in file_content:
                log_print("The dhcpdv6.conf file contains 3 nameservers as part of preferred multi domain ddns list")
                print(data1)
		print(data2)
                assert True
            else:
                log_print("The dhcpdv6.conf file does not contain 3 nameservers as part of preferred multi domain ddns list")
                assert False
        except IOError as e:
            log_print("Unable to open dhcpdv6.conf file")
            log_print(e)
            assert False
        print("Test Case 079 Execution Completed")

    @pytest.mark.run(order=80)
    def test_080_Add_4_Multimaster_zones_For_DDNS_Updates_and_validate_error_message_under_custom_networkview_configure_DDNS_properties(self):
        log_print("\n***************************************************")
        log_print("* TC : 80 - Add 4 Multimaster Zones for DDNS updates and validate error message under custom networkview configure DDNS properties *")
        log_print("***************************************************")
        log_print("Fetch custom_test1.com reference")
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=custom_test1.com", grid_vip=config.grid_vip)
	zone_ref = json.loads(get_ref)[0]['_ref']
        log_print(zone_ref)
        data = {"ddns_dns_view": "custom_dns_view","ddns_zone_primaries":[{"dns_grid_primary":config.grid_member1_fqdn,"dns_grid_zone":{"_ref":zone_ref},"zone_match": "GRID"},{"dns_grid_primary":config.grid_member2_fqdn,"dns_grid_zone":{"_ref":zone_ref},"zone_match": "GRID"},{"dns_grid_primary":config.grid_member3_fqdn,"dns_grid_zone":{"_ref":zone_ref},"zone_match": "GRID"},{"dns_grid_primary":config.grid_member4_fqdn,"dns_grid_zone":{"_ref":zone_ref},"zone_match": "GRID"}]}
        get_ref = ib_NIOS.wapi_request('GET', object_type="networkview?name=custom", grid_vip=config.grid_vip)
        networkview_ref = json.loads(get_ref)[0]['_ref']
        log_print(networkview_ref)
        status,response = ib_NIOS.wapi_request('PUT',ref=networkview_ref,fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)
        data = "For each zone, a maximum of three primary DNS servers can be configured for a DNS failover"
        if data in response:
                assert True
                print("Validated ** "+data+" **")
        else:
                assert False
        print("Test Case 080 Execution Completed")


    @pytest.mark.run(order=81)
    def test_081_Request_IPv4_lease_capture_syslogs_validate_DNS_NS1_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 81 - Request lease and capture syslogs and validate the first dns name server used for ddns updates in syslogs and added A, TXT and PTR records  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_member4_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_member4_vip)+' -n 1 -x l=10.0.0.0 -h -F custom_test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_member4_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_member4_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member1_vip+'#53','Added reverse map from.*by server '+config.grid_member1_vip+'#53']
        for i in data:
                result = re.search(i,log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv4_records_validation()
        print("\nTest Case 081 Executed Successfully")

    @pytest.mark.run(order=82)
    def test_082_Request_IPv6_lease_capture_syslogs_validate_DNS_NS1_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 82 - Request ipv6 lease and capture syslogs and validate the first dns name server used for ddns updates in syslogs and added AAAA, TXT and PTR records *")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_member4_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.member4_ipv6_ip)+' -A -n 1 -h custom_test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_member4_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_member4_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member1_vip+'#53','Added reverse map from.*by server '+config.grid_member1_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv6_records_validation()
        print("\nTest Case 082 Executed Successfully")

    @pytest.mark.run(order=83)
    def test_083_Disable_IPv4_and_IPv6_DNS_interface_on_DNS_NS1_from_the_preferred_Multi_Domaine_DDNS_list(self):
        log_print("\n*****************************************************")
        log_print("* TC: 83 - Disable IPv4 and IPv6 DNS interface on first DNS server from the preferred Multi Domaine DDNS list *")
        log_print("******************************************************")
	disable_ipv4_and_ipv6_dns_on_member(1)
        print("Test Case 083 Execution Completed")

    @pytest.mark.run(order=84)
    def test_084_Request_IPv4_lease_capture_syslogs_validate_DNS_NS2_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 84 - Request lease and capture syslogs and validate the second dns name server used for ddns updates in syslogs and added A, TXT and PTR records  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_member4_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_member4_vip)+' -n 1 -x l=10.0.0.0 -h -F custom_test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_member4_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_member4_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member2_vip+'#53','Added reverse map from.*by server '+config.grid_member2_vip+'#53']
        for i in data:
                result = re.search(i,log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv4_records_validation()
        print("\nTest Case 084 Executed Successfully")

    @pytest.mark.run(order=85)
    def test_085_Request_IPv6_lease_capture_syslogs_validate_DNS_NS2_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 85 - Request ipv6 lease and capture syslogs and validate the second dns name server used for ddns updates in syslogs and added AAAA, TXT and PTR records *")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_member4_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.member4_ipv6_ip)+' -A -n 1 -h custom_test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_member4_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_member4_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member2_vip+'#53','Added reverse map from.*by server '+config.grid_member2_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv6_records_validation()
        print("\nTest Case 085 Executed Successfully")


    @pytest.mark.run(order=86)
    def test_086_Enable_IPv4_and_IPv6_DNS_interface_on_DNS_NS1_from_the_preferred_Multi_Domaine_DDNS_list(self):
        log_print("\n*****************************************************")
        log_print("* TC : 86 - Enable IPv4 and IPv6 DNS interface on first DNS server from the preferred Multi Domaine DDNS list *")
        log_print("******************************************************")
	enable_ipv4_and_ipv6_dns_on_member(1)
        print("Test Case 086 Execution Completed")

    @pytest.mark.run(order=87)
    def test_087_Request_IPv4_lease_capture_syslogs_validate_DNS_NS1_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 87 - Request lease and capture syslogs and validate the first dns name server used for ddns updates in syslogs and added A, TXT and PTR records  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_member4_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_member4_vip)+' -n 1 -x l=10.0.0.0 -h -F custom_test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_member4_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_member4_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member1_vip+'#53','Added reverse map from.*by server '+config.grid_member1_vip+'#53']
        for i in data:
                result = re.search(i,log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv4_records_validation()
        print("\nTest Case 087 Executed Successfully")


    @pytest.mark.run(order=88)
    def test_088_Request_IPv6_lease_capture_syslogs_validate_DNS_NS1_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 88 - Request ipv6 lease and capture syslogs and validate the first dns name server used for ddns updates in syslogs and added AAAA, TXT and PTR records *")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_member4_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.member4_ipv6_ip)+' -A -n 1 -h custom_test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_member4_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_member4_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member1_vip+'#53','Added reverse map from.*by server '+config.grid_member1_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv6_records_validation()
        print("\nTest Case 088 Executed Successfully")


###########################################################################################
######### Default Primary Name Servers scenarios at in custom Network view (Grid Level) ###
###########################################################################################

    @pytest.mark.run(order=89)
    def test_089_Add_3_Default_Primary_DNS_NS_For_DDNS_Updates_under_custom_networkview_configure_DDNS_properties(self):
        log_print("\n***************************************************")
        log_print("* TC : 89 - Add 3 Default Primary DNS NS For DDNS Updates under custom networkview configure DDNS properties at grid level  *")
        log_print("***************************************************")
        data = {"ddns_dns_view": "custom_dns_view","ddns_zone_primaries": [{"dns_grid_primary": config.grid_member3_fqdn,"zone_match": "ANY_GRID"},{"dns_grid_primary": config.grid_member2_fqdn,"zone_match": "ANY_GRID"},{"dns_grid_primary": config.grid_member1_fqdn,"zone_match": "ANY_GRID"}]}
        get_ref = ib_NIOS.wapi_request('GET', object_type="networkview?name=custom", grid_vip=config.grid_vip)
        networkview_ref = json.loads(get_ref)[0]['_ref']
        log_print(networkview_ref)
        response = ib_NIOS.wapi_request('PUT',ref=networkview_ref,fields=json.dumps(data), grid_vip=config.grid_vip)
        log_print(response)
        if bool(re.match("\"networkview*.",str(response))):
            log_print("Multimaster zones added to preferred Multi-Domaine DDNS list")
	    sleep(15)
            restart_services()
        else:
            log_print("Failed to add multimaster zones to preferred Multi-Domaine DDNS list ")
            assert False
        print("Test Case 089 Execution Completed")

    @pytest.mark.run(order=90)
    def test_090_Check_if_dhcpd_conf_file_contains_3_Default_DNS_NS_as_part_of_preferred_multi_domain_ddns_list(self):
        log_print("\n************************************************************************************")
        log_print("* TC : 90 - Check if dhcpd.conf file contains 3 Default DNS NS as part of preferred multi domain ddns list *")
        log_print("************************************************************************************")
	sleep(30)
        try:
            os.system('scp root@'+config.grid_member4_vip+':/infoblox/var/dhcpd_conf/dhcpd.conf .')
        except OSError as e:
            log_print("scp failed")
            log_print(e)
            assert False

        try:
            file = open("dhcpd.conf",'r')
            file_content = file.read()
            file.close()
            log_print("\n\n")
            log_print(file_content)
            data = 'zone "custom_test1.com." {\n\tprimary '+config.grid_member3_vip+', '+config.grid_member2_vip+', '+config.grid_member1_vip+';'
            if data in file_content:
                log_print("The dhcpd.conf file contains 3 nameservers as part of preferred multi domain ddns list")
                print(data)
                assert True
            else:
                log_print("The dhcpd.conf file does not contain 3 nameservers as part of preferred multi domain ddns list")
                assert False
        except IOError as e:
            log_print("Unable to open dhcpd.conf file")
            log_print(e)
            assert False
        print("Test Case 090 Execution Completed")


    @pytest.mark.run(order=91)
    def test_091_Request_IPv4_lease_capture_syslogs_validate_DNS_NS1_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 91 - Request lease and capture syslogs and validate the first dns name server used for ddns updates in syslogs and added A, TXT and PTR records  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_member4_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_member4_vip)+' -n 1 -x l=10.0.0.0 -h -F custom_test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_member4_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_member4_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member3_vip+'#53','Added reverse map from.*by server '+config.grid_member3_vip+'#53']
        for i in data:
                result = re.search(i,log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv4_records_validation()
        print("\nTest Case 091 Executed Successfully")


    @pytest.mark.run(order=92)
    def test_092_Request_IPv6_lease_capture_syslogs_validate_DNS_NS1_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 92 - Request ipv6 lease and capture syslogs and validate the first dns name server used for ddns updates in syslogs and added AAAA, TXT and PTR records *")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_member4_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.member4_ipv6_ip)+' -A -n 1 -h custom_test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_member4_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_member4_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member3_vip+'#53','Added reverse map from.*by server '+config.grid_member3_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv6_records_validation()
        print("\nTest Case 092 Executed Successfully")

    @pytest.mark.run(order=93)
    def test_093_Disable_IPv4_and_IPv6_DNS_interface_on_DNS_NS1_from_the_preferred_Multi_Domaine_DDNS_list(self):
        log_print("\n*****************************************************")
        log_print("* TC : 93 - Disable IPv4 and IPv6 DNS interface on first DNS server from the preferred Multi Domaine DDNS list *")
        log_print("******************************************************")
        disable_ipv4_and_ipv6_dns_on_member(3)
        print("Test Case 093 Execution Completed")

    @pytest.mark.run(order=94)
    def test_094_Request_IPv4_lease_capture_syslogs_validate_DNS_NS2_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 94 - Request lease and capture syslogs and validate the second dns name server used for ddns updates in syslogs and added A, TXT and PTR records  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_member4_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_member4_vip)+' -n 1 -x l=10.0.0.0 -h -F custom_test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_member4_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_member4_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member2_vip+'#53','Added reverse map from.*by server '+config.grid_member2_vip+'#53']
        for i in data:
                result = re.search(i,log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv4_records_validation()
        print("\nTest Case 094 Executed Successfully")

    @pytest.mark.run(order=95)
    def test_095_Request_IPv6_lease_capture_syslogs_validate_DNS_NS2_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 95 - Request ipv6 lease and capture syslogs and validate the second dns name server used for ddns updates in syslogs and added AAAA, TXT and PTR records *")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_member4_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.member4_ipv6_ip)+' -A -n 1 -h custom_test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_member4_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_member4_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member2_vip+'#53','Added reverse map from.*by server '+config.grid_member2_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv6_records_validation()
        print("\nTest Case 095 Executed Successfully")

#################################################################
#########  Multi-master DDNS at Member DHCP Level ###############
#################################################################

    @pytest.mark.run(order=96)
    def test_096_Enable_IPv4_DDNS_Updates_at_member_DHCP_properties(self):
        log_print("\n***************************************************")
        log_print("* TC : 96 - Enable IPv4 DDNS updates at member DHCP properties *")
        log_print("*****************************************************")
        log_print("Fetch member dhcp properties reference")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
        log_print(get_ref)
        grid_dhcp_ref = json.loads(get_ref)[0]['_ref']
	print(grid_dhcp_ref)
        data = {"use_ddns_generate_hostname": True,"use_ddns_update_fixed_addresses": True,"use_ddns_use_option81": True,"use_enable_ddns": True,"use_options": True,"use_ddns_domainname": True,"options":[{"name":"domain-name","value":"test2.com"}],"enable_ddns":True,"ddns_domainname":"test2.com","ddns_generate_hostname": True,"ddns_update_fixed_addresses": True,"ddns_use_option81": True}
        response = ib_NIOS.wapi_request('PUT',ref=grid_dhcp_ref,fields=json.dumps(data), grid_vip=config.grid_vip)
	print(response)
        if bool(re.match("\"member:dhcpproperties*.",str(response))):
            log_print("DDNS updates enabled successfully")
            sleep(15)
            restart_services()
        else:
            log_print("Enabling DDNS update unsuccessful")
            assert False
        print("Test Case 096 Execution Completed")


    @pytest.mark.run(order=97)
    def test_097_Enable_IPv6_DDNS_Updates_at_member_DHCP_properties(self):
        log_print("\n***************************************************")
        log_print("* TC : 97 - IPv6 Enable DDNS updates at member DHCP properties *")
        log_print("*****************************************************")
        log_print("Fetch grid dhcp properties reference")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
        log_print(get_ref)
        member_dhcp_ref = json.loads(get_ref)[0]['_ref']
        print(member_dhcp_ref)
        data = {"use_ipv6_ddns_domainname": True,"use_ipv6_ddns_enable_option_fqdn": True,"use_ipv6_domain_name": True,"use_ipv6_enable_ddns": True,"use_ipv6_generate_hostname": True,"ipv6_ddns_domainname": "test2.com","ipv6_ddns_enable_option_fqdn": True,"ipv6_domain_name": "test2.com","ipv6_enable_ddns": True,"ipv6_generate_hostname": True}
        response = ib_NIOS.wapi_request('PUT',ref=member_dhcp_ref,fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if bool(re.match("\"member:dhcpproperties*.",str(response))):
                log_print("IPv6 DDNS updates enabled successfully")
                sleep(15)
                restart_services()
        else:
            log_print("Enabling IPv6 DDNS updates unsuccessful")
            assert False
        print("Test Case 097 Execution Completed")

    @pytest.mark.run(order=98)
    def test_098_Enable_IPv4_and_IPv6_DNS_interface_on_all_members(self):
        log_print("\n************************************************************")
        log_print("* TC : 98 - Enable IPv4 & IPv6 DNS interface on all members******")
        log_print("**************************************************************")
        enable_ipv4_and_ipv6_dns_interface_on_all_members()        
        print("Test Case 098 Execution Completed")


    @pytest.mark.run(order=99)
    def test_099_Add_MultiMaster_Zones_For_DDNS_Updates_under_Multi_Master_DDNS_at_Member_DHCP_Properties(self):
        log_print("\n***************************************************")
        log_print("* TC : 99 - Add Multimaster Zones for DDNS updates under Multi-master DDNS list at Member DHCP Properties  *")
        log_print("***************************************************")
        log_print("Fetch test2.com reference")
        ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
        ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=test2.com", grid_vip=config.grid_vip)
	zone_ref = ''
	for ref in json.loads(get_ref):
            if ref['view'] == 'default':
                zone_ref = ref['_ref']
        log_print(zone_ref)
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=10.0.0.0/24",grid_vip=config.grid_vip)
        reverse_ref = ''
        for ref in json.loads(get_ref):
            if ref['view'] == 'default':
                reverse_ref = ref['_ref']	
        print(reverse_ref)
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn="+ipv6_network+"::/64",grid_vip=config.grid_vip)
        ipv6_reverse_ref = ''
        for ref in json.loads(get_ref):
            if ref['view'] == 'default':
                ipv6_reverse_ref = ref['_ref']
        print(ipv6_reverse_ref)
        networkview_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
        networkview_ref = json.loads(networkview_ref)[0]['_ref']
	print(networkview_ref)
        data = {"ddns_zone_primaries": [{"dns_grid_primary":config.grid_member3_fqdn,"dns_grid_zone": {"_ref": reverse_ref},"zone_match": "GRID"},{"dns_grid_primary": config.grid_member2_fqdn,"dns_grid_zone": {"_ref": reverse_ref},"zone_match": "GRID"},{"dns_grid_primary": config.grid_member1_fqdn,"dns_grid_zone": {"_ref": reverse_ref},"zone_match": "GRID"},{"dns_grid_primary": config.grid_member1_fqdn,"dns_grid_zone": {"_ref": zone_ref},"zone_match": "GRID"},{"dns_grid_primary": config.grid_member2_fqdn,"dns_grid_zone": {"_ref": zone_ref},"zone_match": "GRID"},{"dns_grid_primary": config.grid_member3_fqdn,"dns_grid_zone": {"_ref": zone_ref},"zone_match": "GRID"},{"dns_grid_primary":config.grid_member3_fqdn,"dns_grid_zone": {"_ref": ipv6_reverse_ref},"zone_match": "GRID"},{"dns_grid_primary":config.grid_member1_fqdn,"dns_grid_zone": {"_ref": ipv6_reverse_ref},"zone_match": "GRID"},{"dns_grid_primary":config.grid_member2_fqdn,"dns_grid_zone": {"_ref": ipv6_reverse_ref},"zone_match": "GRID"}]}
        response = ib_NIOS.wapi_request('PUT',ref=networkview_ref,fields=json.dumps(data), grid_vip=config.grid_vip)
        log_print(response)
        if bool(re.match("\"member:dhcpproperties*.",str(response))):
            log_print("Multimaster zones added to the Multi-master DDNS list at Member DHCP Properties ")
	    sleep(15)
            restart_services()
        else:
            log_print("Failed to add multimaster zones to Multi-master DDNS list at Member DHCP Properties")
            assert False
        print("Test Case 099 Execution Completed")

    @pytest.mark.run(order=100)
    def test_100_Check_if_the_dhcpd_conf_file_contains_3_DNS_NS_configured_as_part_of_the_preferred_multi_domain_ddns_list(self):
        log_print("\n************************************************************************************")
        log_print("* TC : 100 - Check if the dhcpd.conf file contains 3 DNS NS configured as part of the preferred multi domain ddns list *")
        log_print("************************************************************************************")
	sleep(30)
        try:
            os.system('scp -o StrictHostKeyChecking=no root@'+config.grid_vip+':/infoblox/var/dhcpd_conf/dhcpd.conf .')
        except OSError as e:
            log_print("Scp failed")
            log_print(e)
            assert False

        try:
            file = open("dhcpd.conf",'r')
            file_content = file.read()
            file.close()
            log_print("\n\n")
            log_print(file_content)
            data1 = 'zone "test2.com." {\n\tprimary '+config.grid_member1_vip+', '+config.grid_member2_vip+', '+config.grid_member3_vip+';'
            data2 = 'zone "0.0.10.in-addr.arpa." {\n\tprimary '+config.grid_member3_vip+', '+config.grid_member2_vip+', '+config.grid_member1_vip+';'
            if data1 in file_content and data2 in file_content:
                log_print("The dhcpd.conf file contains 3 nameservers as part of preferred multi domain ddns list")
                print(data1)
                print(data2)
                assert True
            else:
                log_print("The dhcpd.conf file does not contain 3 nameservers as part of preferred multi domain ddns list")
                assert False
        except IOError as e:
            log_print("Unable to open dhcpd.conf file")
            log_print(e)
            assert False
        print("Test Case 100 Execution Completed")

    @pytest.mark.run(order=101)
    def test_101_Check_if_the_dhcpdv6_conf_file_contains_3_DNS_NS_configured_as_part_of_the_preferred_multi_domain_ddns_list(self):
        log_print("\n************************************************************************************")
        log_print("* TC : 101 - Check if the dhcpdv6.conf file contains 3 DNS NS configured as part of the preferred multi domain ddns list *")
        log_print("************************************************************************************")
	sleep(30)
        try:
            os.system('scp -o StrictHostKeyChecking=no root@'+config.grid_vip+':/infoblox/var/dhcpdv6_conf/dhcpdv6.conf .')
        except OSError as e:
            log_print("Scp failed")
            log_print(e)
            assert False

        try:
            file = open("dhcpdv6.conf",'r')
            file_content = file.read()
            file.close()
            log_print("\n\n")
            log_print(file_content)
            data1 = 'zone "test2.com." {\n\tprimary '+config.grid_member1_vip+', '+config.grid_member2_vip+', '+config.grid_member3_vip+';'
            data2 = 'ip6.arpa." {\n\tprimary '+config.grid_member3_vip+', '+config.grid_member1_vip+', '+config.grid_member2_vip+';'
            if data1 in file_content and data2 in file_content:
                log_print("The dhcpdv6.conf file contains 3 nameservers as part of multimaster zone")
                print(data1)
                print(data2)
                assert True
            else:
                log_print("The dhcpdv6.conf file does not contain 3 nameservers as part of multimaster zone")
                assert False
        except IOError as e:
            log_print("Unable to open dhcpdv6.conf file")
            log_print(e)
            assert False
        print("Test Case 101 Execution Completed")


    @pytest.mark.run(order=102)
    def test_102_Request_IPv4_lease_capture_syslogs_validate_DNS_NS1_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 102 - Request lease and capture syslogs and validate the first dns name server used for ddns updates in syslogs and added A, TXT and PTR records  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F test2.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member1_vip+'#53','Added reverse map from.*by server '+config.grid_member3_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv4_records_validation()
        print("\nTest Case 102 Executed Successfully")

    @pytest.mark.run(order=103)
    def test_103_Request_IPv6_lease_capture_syslogs_validate_DNS_NS1_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 103 - Request ipv6 lease and capture syslogs and validate the first dns name server used for ddns updates in syslogs and added AAAA, TXT and PTR records *")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.master1_ipv6_ip)+' -A -n 1 -h test2.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member1_vip+'#53','Added reverse map from.*by server '+config.grid_member3_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv6_records_validation()
        print("\nTest Case 103 Executed Successfully")

    @pytest.mark.run(order=104)
    def test_104_Disable_IPv4_and_IPv6_DNS_interface_on_DNS_NS1_and_NS3_from_the_preferred_Multi_Domaine_DDNS_list(self):
        log_print("\n*****************************************************")
        log_print("* TC: 104 - Disable IPv4 and IPv6 DNS interface on first and third DNS servers from the preferred Multi Domaine DDNS list *")
        log_print("******************************************************")
	disable_ipv4_and_ipv6_dns_on_member(1)	
	disable_ipv4_and_ipv6_dns_on_member(3)
        print("Test Case 104 Execution Completed")


    @pytest.mark.run(order=105)
    def test_105_Request_IPv4_lease_capture_syslogs_validate_DNS_NS2_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 105 - Request lease and capture syslogs and validate the second dns name server used for ddns updates in syslogs and added A, TXT and PTR records  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F test2.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member2_vip+'#53','Added reverse map from.*by server '+config.grid_member2_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv4_records_validation()
        print("\nTest Case 105 Executed Successfully")

    @pytest.mark.run(order=106)
    def test_106_Request_IPv6_lease_capture_syslogs_validate_DNS_NS2_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 106 - Request ipv6 lease and capture syslogs and validate the second dns name server used for ddns updates in syslogs and added AAAA, TXT and PTR records *")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.master1_ipv6_ip)+' -A -n 1 -h test2.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member2_vip+'#53','Added reverse map from.*by server '+config.grid_member2_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv6_records_validation()
        print("\nTest Case 106 Executed Successfully")

    @pytest.mark.run(order=107)
    def test_107_Enable_IPv4_and_IPv6_DNS_interface_on_DNS_NS1_and_NS3_from_the_preferred_Multi_Domaine_DDNS_list(self):
        log_print("\n*****************************************************")
        log_print("* TC : 107 - Enable IPv4 and IPv6 DNS interface on first and third DNS server from the preferred Multi Domaine DDNS list *")
        log_print("******************************************************")
	enable_ipv4_and_ipv6_dns_on_member(1)
	enable_ipv4_and_ipv6_dns_on_member(3)
        print("Test Case 107 Execution Completed")


    @pytest.mark.run(order=108)
    def test_108_Request_IPv4_lease_capture_syslogs_validate_DNS_NS1_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 108 - Request lease and capture syslogs and validate the first dns name server used for ddns updates in syslogs and added A, TXT and PTR records  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F test2.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member1_vip+'#53','Added reverse map from.*by server '+config.grid_member3_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv4_records_validation()
        print("\nTest Case 108 Executed Successfully")

    @pytest.mark.run(order=109)
    def test_109_Request_IPv6_lease_capture_syslogs_validate_DNS_NS1_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 109 - Request ipv6 lease and capture syslogs and validate the first dns name server used for ddns updates in syslogs and added AAAA, TXT and PTR records *")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.master1_ipv6_ip)+' -A -n 1 -h test2.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member1_vip+'#53','Added reverse map from.*by server '+config.grid_member3_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv6_records_validation()
        print("\nTest Case 109 Executed Successfully")

    @pytest.mark.run(order=110)
    def test_110_Add_4_Multimaster_zones_For_DDNS_Updates_and_validate_error_message_at_Member_DHCP_Properties(self):
        log_print("\n***************************************************")
        log_print("* TC : 110 - Add 4 Multimaster zones For DDNS Updates and validate error message at Member DHCP Properties   *")
        log_print("***************************************************")
        log_print("Fetch test1.com reference")
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
        zone_ref = ''
        for ref in json.loads(get_ref):
            if ref['fqdn'] == 'test1.com':
                zone_ref = ref['_ref']
        log_print(zone_ref)
        data = {"ddns_zone_primaries":[{"dns_grid_primary":config.grid_member1_fqdn,"dns_grid_zone":{"_ref":zone_ref},"zone_match": "GRID"},{"dns_grid_primary":config.grid_member2_fqdn,"dns_grid_zone":{"_ref":zone_ref},"zone_match": "GRID"},{"dns_grid_primary":config.grid_member3_fqdn,"dns_grid_zone":{"_ref":zone_ref},"zone_match": "GRID"},{"dns_grid_primary":config.grid_member4_fqdn,"dns_grid_zone":{"_ref":zone_ref},"zone_match": "GRID"}]}
        master_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
        master_ref = json.loads(master_ref)[0]['_ref']
        print(master_ref)
        status,response = ib_NIOS.wapi_request('PUT',ref=master_ref,fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)
        data = "For each zone, a maximum of three primary DNS servers can be configured for a DNS failover"
        if data in response:
                assert True
                print("Validated ** "+data+" **")
        else:
                assert False
        print("Test Case 110 Execution Completed")

##################################################################
########  Default Primary DNS NS scenarios at member level #######
##################################################################

    @pytest.mark.run(order=111)
    def test_111_Add_3_Default_Primary_DNS_NS_For_DDNS_Updates_at_Member_DHCP_Properties(self):
        log_print("\n***************************************************")
        log_print("* TC: 111 - Add Multimaster Zones for DDNS updates at Member DHCP Properties *")
        log_print("***************************************************")
        data = {"ddns_zone_primaries": [{"dns_grid_primary": config.grid_member3_fqdn,"zone_match": "ANY_GRID"},{"dns_grid_primary": config.grid_member2_fqdn,"zone_match": "ANY_GRID"},{"dns_grid_primary": config.grid_member1_fqdn,"zone_match": "ANY_GRID"}]}
        member_dhcp_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
        member_dhcp_ref = json.loads(member_dhcp_ref)[0]['_ref']
        print(member_dhcp_ref)
        response = ib_NIOS.wapi_request('PUT',ref=member_dhcp_ref,fields=json.dumps(data), grid_vip=config.grid_vip)
        log_print(response)
        if bool(re.match("\"member:dhcpproperties*.",str(response))):
            log_print("Multimaster zones added to the list of zones in DDNS updates")
	    sleep(15)
            restart_services()
        else:
            log_print("Failed to add multimaster zones to list of zones in DDNS updates")
            assert False
        print("Test Case 111 Execution Completed")


    @pytest.mark.run(order=112)
    def test_112_Check_if_dhcpd_conf_file_contains_3_Default_DNS_NS_configured_as_part_of_preferred_multi_domain_ddns_list(self):
        log_print("\n************************************************************************************")
        log_print("* TC : 112 - Check if dhcpd.conf file contains 3 Default DNS NS as part of preferred multi domain ddns list *")
        log_print("************************************************************************************")
	sleep(30)
        try:
            os.system('scp -o StrictHostKeyChecking=no root@'+config.grid_vip+':/infoblox/var/dhcpd_conf/dhcpd.conf .')
        except OSError as e:
            log_print("Scp failed")
            log_print(e)
            assert False

        try:
            file = open("dhcpd.conf",'r')
            file_content = file.read()
            file.close()
            log_print("\n\n")
            log_print(file_content)
            data1 = 'zone "test2.com." {\n\tprimary '+config.grid_member3_vip+', '+config.grid_member2_vip+', '+config.grid_member1_vip+';'
            data2 = 'zone "0.0.10.in-addr.arpa." {\n\tprimary '+config.grid_member3_vip+', '+config.grid_member2_vip+', '+config.grid_member1_vip+';'
            if data1 in file_content and data2 in file_content:
                log_print("The dhcpd.conf file contains 3 nameservers as part of preferred multi domain ddns list")
                print(data1)
                print(data2)
                assert True
            else:
                log_print("The dhcpd.conf file does not contain 3 nameservers as part of preferred multi domain ddns list")
                assert False
        except IOError as e:
            log_print("Unable to open dhcpd.conf file")
            log_print(e)
            assert False
        print("Test Case 112 Execution Completed")

    @pytest.mark.run(order=113)
    def test_113_Check_if_the_dhcpdv6_conf_file_contains_3_DNS_NS_configured_as_part_of_the_preferred_multi_domain_ddns_list(self):
        log_print("\n************************************************************************************")
        log_print("* TC : 113 - Check if the dhcpdv6.conf file contains 3 DNS NS configured as part of the preferred multi domain ddns list *")
        log_print("************************************************************************************")
	sleep(30)
        try:
            os.system('scp -o StrictHostKeyChecking=no root@'+config.grid_vip+':/infoblox/var/dhcpdv6_conf/dhcpdv6.conf .')
        except OSError as e:
            log_print("Scp failed")
            log_print(e)
            assert False

        try:
            file = open("dhcpdv6.conf",'r')
            file_content = file.read()
            file.close()
            log_print("\n\n")
            log_print(file_content)
            data1 = 'zone "test2.com." {\n\tprimary '+config.grid_member3_vip+', '+config.grid_member2_vip+', '+config.grid_member1_vip+';'
            data2 = 'ip6.arpa." {\n\tprimary '+config.grid_member3_vip+', '+config.grid_member2_vip+', '+config.grid_member1_vip+';'
            if data1 in file_content and data2 in file_content:
                log_print("The dhcpdv6.conf file contains 3 nameservers as part of preferred multi domain ddns list")
                print(data1)
                print(data2)
                assert True
            else:
                log_print("The dhcpdv6.conf file does not contain 3 nameservers as part of preferred multi domain ddns list")
                assert False
        except IOError as e:
            log_print("Unable to open dhcpdv6.conf file")
            log_print(e)
            assert False
        print("Test Case 113 Execution Completed")

    @pytest.mark.run(order=114)
    def test_114_Disable_IPv4_and_IPv6_DNS_interface_on_DNS_NS1_from_the_preferred_Multi_Domaine_DDNS_list(self):
        log_print("\n*****************************************************")
        log_print("* TC : 114 - Disable IPv4 and IPv6 DNS interface on first DNS server from the preferred Multi Domaine DDNS list *")
        log_print("******************************************************")
	disable_ipv4_and_ipv6_dns_on_member(3)
        print("Test Case 114 Execution Completed")

    @pytest.mark.run(order=115)
    def test_115_Request_IPv4_lease_capture_syslogs_validate_DNS_NS2_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 115 - Request lease and capture syslogs and validate the second dns name server used for ddns updates in syslogs and added A, TXT and PTR records  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F test2.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member2_vip+'#53','Added reverse map from.*by server '+config.grid_member2_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv4_records_validation()
        print("\nTest Case 115 Executed Successfully")

    @pytest.mark.run(order=116)
    def test_116_Request_IPv6_lease_capture_syslogs_validate_DNS_NS2_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 116 - Request ipv6 lease and capture syslogs and validate second the dns name server used for ddns updates in syslogs and added AAAA, TXT and PTR records *")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.master1_ipv6_ip)+' -A -n 1 -h test2.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member2_vip+'#53','Added reverse map from.*by server '+config.grid_member2_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv6_records_validation()
        print("\nTest Case 116 Executed Successfully")


    @pytest.mark.run(order=117)
    def test_117_Disable_IPv4_and_IPv6_DNS_interface_on_DNS_NS2_from_the_preferred_Multi_Domaine_DDNS_list(self):
        log_print("\n*****************************************************")
        log_print("* TC : 117 - Disable IPv4 and IPv6 DNS interface on second DNS server from the preferred Multi Domaine DDNS list *")
        log_print("******************************************************")
	disable_ipv4_and_ipv6_dns_on_member(2)
        print("Test Case 117 Execution Completed")

    @pytest.mark.run(order=118)
    def test_118_Request_IPv4_lease_capture_syslogs_validate_DNS_NS3_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 118 - Request lease and capture syslogs and validate the third dns name server used for ddns updates in syslogs and added A, TXT and PTR records  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F test2.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member1_vip+'#53','Added reverse map from.*by server '+config.grid_member1_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv4_records_validation()
        print("\nTest Case 118 Executed Successfully")

    @pytest.mark.run(order=119)
    def test_119_Request_IPv6_lease_capture_syslogs_validate_DNS_NS3_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 119 - Request ipv6 lease and capture syslogs and validate the third dns name server used for ddns updates in syslogs and added AAAA, TXT and PTR records *")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.master1_ipv6_ip)+' -A -n 1 -h test2.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member1_vip+'#53','Added reverse map from.*by server '+config.grid_member1_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv6_records_validation()
        print("\nTest Case 119 Executed Successfully")

    @pytest.mark.run(order=120)
    def test_120_Disable_IPv4_and_IPv6_DNS_interface_on_DNS_NS3_from_the_preferred_Multi_Domaine_DDNS_list(self):
        log_print("\n*****************************************************")
        log_print("* TC : 120 - Disable IPv4 and IPv6 DNS interface on third DNS server from the preferred Multi Domaine DDNS list *")
        log_print("******************************************************")
	disable_ipv4_and_ipv6_dns_on_member(1)
        print("Test Case 120 Execution Completed")


    @pytest.mark.run(order=121)
    def test_121_Request_IPv4_lease_capture_syslogs_validate_deferred_ddns_updates_in_syslogs(self):
        log_print("\n************************************************************")
        log_print("* TC : 121 - Request lease and capture syslogs and validate deferred ddns updates in syslogs  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F test2.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'deferred'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Addition of forward map for.*deferred','Addition of reverse map for.*deferred']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        print("\nTest Case 121 Executed Successfully")

    @pytest.mark.run(order=122)
    def test_122_Request_IPv6_lease_capture_syslogs_validate_deferred_ddns_updates_in_syslogs(self):
        log_print("\n************************************************************")
        log_print("* TC : 122 - Request ipv6 lease and capture syslogs and validate deferred ddns updates in syslogs *")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.master1_ipv6_ip)+' -A -n 1 -h test2.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'deferred'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Addition of forward map for.*deferred','Addition of reverse map for.*deferred']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        print("\nTest Case 122 Executed Successfully")

    @pytest.mark.run(order=123)
    def test_123_Enable_IPv4_and_IPv6_DNS_interface_on_DNS_NS2_from_the_preferred_Multi_Domaine_DDNS_list(self):
        log_print("\n*****************************************************")
        log_print("* TC : 123 - Enable IPv4 and IPv6 DNS interface on second DNS server from the preferred Multi Domaine DDNS list *")
        log_print("******************************************************")
        enable_ipv4_and_ipv6_dns_on_member(2)
        print("Test Case 123 Execution Completed")

    @pytest.mark.run(order=124)
    def test_124_Request_IPv4_lease_capture_syslogs_validate_DNS_NS2_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 124 - Request lease and capture syslogs and validate the second dns name server used for ddns updates in syslogs and added A, TXT and PTR records  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F test2.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member2_vip+'#53','Added reverse map from.*by server '+config.grid_member2_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv4_records_validation()
        print("\nTest Case 124 Executed Successfully")

    @pytest.mark.run(order=125)
    def test_125_Request_IPv6_lease_capture_syslogs_validate_DNS_NS2_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 125 - Request ipv6 lease and capture syslogs and validate the second dns name server used for ddns updates in syslogs and added AAAA, TXT and PTR records *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.master1_ipv6_ip)+' -A -n 1 -h test2.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member2_vip+'#53','Added reverse map from.*by server '+config.grid_member2_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv6_records_validation()
        print("\nTest Case 125 Executed Successfully")


########### Default Primary Sceanrios at member level end here #############


    @pytest.mark.run(order=126)
    def test_126_Add_an_unassigned_DNS_nameserver_to_the_list_of_multimaster_ddns_at_the_member_level_to_validate_the_proper_error_message(self):
        log_print("\n***********************************************************************************************************************************")
        log_print("* TC : 126 - Add an unassigned dns name server to the list of multimaster ddns at the member level to validate the proper error message  *")
        log_print("*************************************************************************************************************************************")
        log_print("Fetch test2.com reference")
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
        zone_ref = ''
        for ref in json.loads(get_ref):
            if ref['fqdn'] == 'test2.com':
                zone_ref = ref['_ref']
        log_print(zone_ref)
        data = {"ddns_zone_primaries":[{"dns_grid_primary":config.grid_member4_fqdn,"dns_grid_zone":{"_ref":zone_ref},"zone_match": "GRID"}]}
        master_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
        master_ref = json.loads(master_ref)[0]['_ref']
        print(master_ref)
        status,response = ib_NIOS.wapi_request('PUT',ref=master_ref,fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)
        data = "Grid member '"+config.grid_member4_fqdn+"' is not a DNS primary for zone 'test2.com' in DNS view 'default', so it cannot be used with that zone in DDNS update master preferences"
        if data in response:
                assert True
                print("Validated ** "+data+" **")
        else:
                assert False
        print("Test Case 126 Execution Completed")



################################################################
################# sub zone scenarios at member level ###########
################################################################

    @pytest.mark.run(order=127)
    def test_127_Enable_IPv4_and_IPv6_DNS_interface_on_all_members(self):
        log_print("\n************************************************************")
        log_print("* TC : 127 -  Enable IPv4 & IPv6 DNS interface on all members******")
        log_print("**************************************************************")
        enable_ipv4_and_ipv6_dns_interface_on_all_members()
        print("Test Case 127 Execution Completed")

    @pytest.mark.run(order=128)
    def test_128_Update_sub_domain_as_ddns_domain_name_in_member_dhcp_properties(self):
        print("*********************************************************")
        log_print("\n***************************************************")
        log_print("* TC : 128 - IPv6 Enable DDNS updates                    *")
        log_print("*****************************************************")
        log_print("Fetch member dhcp properties reference")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
        log_print(get_ref)
        member_dhcp_ref = json.loads(get_ref)[0]['_ref']
        print(member_dhcp_ref)
        data={"ipv6_ddns_domainname": "sub.test2.com","ipv6_domain_name": "sub.test2.com","options":[{"name":"domain-name","value":"sub.test2.com"}],"ddns_domainname":"sub.test2.com"}
        response = ib_NIOS.wapi_request('PUT',ref=member_dhcp_ref,fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if bool(re.match("\"member:dhcpproperties*.",str(response))):
                log_print("updated DDNS domain name at member dhcp properties successfully")
                sleep(15)
                restart_services()
        else:
            log_print("failed updating DDNS domain name at member dhcp properties")
            assert False
        print("Test Case 128 Execution Completed")

    @pytest.mark.run(order=129)
    def test_129_Add_MultiMaster_Sub_Zone_For_DDNS_Updates_at_Member_DHCP_Properties(self):
        log_print("\n***************************************************")
        log_print("* TC : 129 - Add Multimaster Sub Zone sub.test2.com for DDNS updates at Member DHCP Properties*")
        log_print("***************************************************")
        log_print("Fetch sub.test2.com reference")
        ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
        ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=sub.test2.com", grid_vip=config.grid_vip)
        zone_ref = ''
        for ref in json.loads(get_ref):
            if ref['view'] == 'default':
                zone_ref = ref['_ref']
        log_print(zone_ref)
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=10.0.0.0/24",grid_vip=config.grid_vip)
        reverse_ref = ''
        for ref in json.loads(get_ref):
            if ref['view'] == 'default':
                reverse_ref = ref['_ref']
        print(reverse_ref)
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn="+ipv6_network+"::/64",grid_vip=config.grid_vip)
        ipv6_reverse_ref = ''
        for ref in json.loads(get_ref):
            if ref['view'] == 'default':
                ipv6_reverse_ref = ref['_ref']
        print(ipv6_reverse_ref)
        networkview_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
        networkview_ref = json.loads(networkview_ref)[0]['_ref']
        print(networkview_ref)
        data = {"ddns_zone_primaries": [{"dns_grid_primary":config.grid_member1_fqdn,"dns_grid_zone": {"_ref": reverse_ref},"zone_match": "GRID"},{"dns_grid_primary": config.grid_member2_fqdn,"dns_grid_zone": {"_ref": reverse_ref},"zone_match": "GRID"},{"dns_grid_primary": config.grid_member3_fqdn,"dns_grid_zone": {"_ref": reverse_ref},"zone_match": "GRID"},{"dns_grid_primary": config.grid_member1_fqdn,"dns_grid_zone": {"_ref": zone_ref},"zone_match": "GRID"},{"dns_grid_primary": config.grid_member2_fqdn,"dns_grid_zone": {"_ref": zone_ref},"zone_match": "GRID"},{"dns_grid_primary": config.grid_member3_fqdn,"dns_grid_zone": {"_ref": zone_ref},"zone_match": "GRID"},{"dns_grid_primary":config.grid_member1_fqdn,"dns_grid_zone": {"_ref": ipv6_reverse_ref},"zone_match": "GRID"},{"dns_grid_primary":config.grid_member2_fqdn,"dns_grid_zone": {"_ref": ipv6_reverse_ref},"zone_match": "GRID"},{"dns_grid_primary":config.grid_member3_fqdn,"dns_grid_zone": {"_ref": ipv6_reverse_ref},"zone_match": "GRID"}]}
        response = ib_NIOS.wapi_request('PUT',ref=networkview_ref,fields=json.dumps(data), grid_vip=config.grid_vip)
        log_print(response)
        if bool(re.match("\"member:dhcpproperties*.",str(response))):
            log_print("Multimaster sub zone added for DDNS updates at Member DHCP Properties")
	    sleep(15)
            restart_services()
        else:
            log_print("Failed to add multimaster sub zone for DDNS updates at Member DHCP Properties")
            assert False
        print("Test Case 129 Execution Completed")

    @pytest.mark.run(order=130)
    def test_130_Check_if_the_dhcpd_conf_file_contains_3_DNS_NS_configured_as_part_of_the_preferred_multi_domain_ddns_list(self):
        log_print("\n************************************************************************************")
        log_print("* TC : 130 - Check if the dhcpd.conf file contains 3 DNS NS configured as part of the preferred multi domain ddns list *")
        log_print("************************************************************************************")
	sleep(30)
        try:
            os.system('scp -o StrictHostKeyChecking=no root@'+config.grid_vip+':/infoblox/var/dhcpd_conf/dhcpd.conf .')
        except OSError as e:
            log_print("Scp failed")
            log_print(e)
            assert False

        try:
            file = open("dhcpd.conf",'r')
            file_content = file.read()
            file.close()
            log_print("\n\n")
            log_print(file_content)
            data1 = 'zone "sub.test2.com." {\n\tprimary '+config.grid_member1_vip+', '+config.grid_member2_vip+', '+config.grid_member3_vip+';'
            data2 = 'zone "0.0.10.in-addr.arpa." {\n\tprimary '+config.grid_member1_vip+', '+config.grid_member2_vip+', '+config.grid_member3_vip+';'
            if data1 in file_content and data2 in file_content:
                log_print("The dhcpd.conf file contains 3 nameservers as part of preferred multi domain ddns list")
                print(data1)
                print(data2)
                assert True
            else:
                log_print("The dhcpd.conf file does not contain 3 nameservers as part of preferred multi domain ddns list")
                assert False
        except IOError as e:
            log_print("Unable to open dhcpd.conf file")
            log_print(e)
            assert False
        print("Test Case 130 Execution Completed")

    @pytest.mark.run(order=131)
    def test_131_Check_if_the_dhcpdv6_conf_file_contains_3_DNS_NS_configured_as_part_of_the_preferred_multi_domain_ddns_list(self):
        log_print("\n************************************************************************************")
        log_print("* TC : 131 - Check if the dhcpdv6.conf file contains 3 DNS NS configured as part of the preferred multi domain ddns list *")
        log_print("************************************************************************************")
	sleep(30)
        try:
            os.system('scp -o StrictHostKeyChecking=no root@'+config.grid_vip+':/infoblox/var/dhcpdv6_conf/dhcpdv6.conf .')
        except OSError as e:
            log_print("Scp failed")
            log_print(e)
            assert False

        try:
            file = open("dhcpdv6.conf",'r')
            file_content = file.read()
            file.close()
            log_print("\n\n")
            log_print(file_content)
            data1 = 'zone "sub.test2.com." {\n\tprimary '+config.grid_member1_vip+', '+config.grid_member2_vip+', '+config.grid_member3_vip+';'
            data2 = 'ip6.arpa." {\n\tprimary '+config.grid_member1_vip+', '+config.grid_member2_vip+', '+config.grid_member3_vip+';'
            if data1 in file_content and data2 in file_content:
                log_print("The dhcpdv6.conf file contains 3 nameservers as part of multimaster zone")
                print(data1)
                print(data2)
                assert True
            else:
                log_print("The dhcpdv6.conf file does not contain 3 nameservers as part of multimaster zone")
                assert False
        except IOError as e:
            log_print("Unable to open dhcpdv6.conf file")
            log_print(e)
            assert False
        print("Test Case 131 Execution Completed")

    @pytest.mark.run(order=132)
    def test_132_Request_IPv4_lease_capture_syslogs_validate_DNS_NS1_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 132 - Request lease and capture syslogs and validate the first dns name server used for ddns updates in syslogs and added A, TXT and PTR records  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F sub.test2.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member1_vip+'#53','Added reverse map from.*by server '+config.grid_member1_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv4_records_validation()
        print("\nTest Case 132 Executed Successfully")

    @pytest.mark.run(order=133)
    def test_133_Request_IPv6_lease_capture_syslogs_validate_DNS_NS1_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 133 - Request ipv6 lease and capture syslogs and validate the first dns name server used for ddns updates in syslogs and added AAAA, TXT and PTR records *")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.master1_ipv6_ip)+' -A -n 1 -h sub.test2.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member1_vip+'#53','Added reverse map from.*by server '+config.grid_member1_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv6_records_validation()
        print("\nTest Case 133 Executed Successfully")

    @pytest.mark.run(order=134)
    def test_134_Disable_IPv4_and_IPv6_DNS_interface_on_DNS_NS1_and_NS2_from_the_preferred_Multi_Domaine_DDNS_list(self):
        log_print("\n****************************************************************************************************************")
        log_print("* TC : 134 - Disable IPv4 and IPv6 DNS interface on first and second DNS server from the preferred Multi Domaine DDNS list ******")
        log_print("******************************************************************************************************************")
        disable_ipv4_and_ipv6_dns_on_member(1)
	disable_ipv4_and_ipv6_dns_on_member(2)
        print("Test Case 134 Execution Completed")

    @pytest.mark.run(order=135)
    def test_135_Request_IPv4_lease_capture_syslogs_validate_DNS_NS3_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 135 - Request lease and capture syslogs and validate the third dns name server used for ddns updates in syslogs and added A, TXT and PTR records  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F sub.test2.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member3_vip+'#53','Added reverse map from.*by server '+config.grid_member3_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv4_records_validation()
        print("\nTest Case 135 Executed Successfully")

    @pytest.mark.run(order=136)
    def test_136_Request_IPv6_lease_capture_syslogs_validate_DNS_NS3_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 136 - Request ipv6 lease and capture syslogs and validate the third dns name server used for ddns updates in syslogs and added AAAA, TXT and PTR records *")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.master1_ipv6_ip)+' -A -n 1 -h sub.test2.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member3_vip+'#53','Added reverse map from.*by server '+config.grid_member3_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv6_records_validation()
        print("\nTest Case 136 Executed Successfully")

    @pytest.mark.run(order=137)
    def test_137_Enable_IPv4_and_IPv6_DNS_interface_on_DNS_NS2_from_the_preferred_Multi_Domaine_DDNS_list(self):
        log_print("\n*****************************************************")
        log_print("* TC : 137 - Enable IPv4 and IPv6 DNS interface on second DNS server from the preferred Multi Domaine DDNS list *")
        log_print("******************************************************")
        enable_ipv4_and_ipv6_dns_on_member(2)
        print("Test Case 137 Execution Completed")

    @pytest.mark.run(order=138)
    def test_138_Request_IPv4_lease_capture_syslogs_validate_DNS_NS2_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 138 - Request lease and capture syslogs and validate the second dns name server used for ddns updates in syslogs and added A, TXT and PTR records  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F sub.test2.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member2_vip+'#53','Added reverse map from.*by server '+config.grid_member2_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv4_records_validation()
        print("\nTest Case 138 Executed Successfully")


    @pytest.mark.run(order=139)
    def test_139_Request_IPv6_lease_capture_syslogs_validate_DNS_NS2_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 139 - Request ipv6 lease and capture syslogs and validate the second dns name server used for ddns updates in syslogs and added AAAA, TXT and PTR records *")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.master1_ipv6_ip)+' -A -n 1 -h sub.test2.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member2_vip+'#53','Added reverse map from.*by server '+config.grid_member2_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv6_records_validation()
        print("\nTest Case 139 Executed Successfully")

################# Multi Master Sub Zone Scenarions at Member level end here ############### 



####################################################################
####### Custom Network View Multi Master Zones at Member Level #####
####################################################################




    @pytest.mark.run(order=140)
    def test_140_Create_custom_dns_view_in_default_network_view(self):
        log_print("\n************************************************************")
        log_print("* TC : 140 - Create custom dns view in default network view *")
        log_print("**************************************************************")
        data = {"name": "default_dns_view","network_view": "default"}
        print(data)
        response = ib_NIOS.wapi_request('POST', object_type="view", fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if bool(re.match("\"view*.*default_dns_view/false",str(response))):
            log_print("Multimaster zones added to the list of zones in DDNS updates")
            sleep(5)
        else:
            log_print("Failed to add multimaster zones to list of zones in DDNS updates")
            assert False

        log_print("\n*******************************************************************")
        log_print("* Add Multi-master Auth zone default_test1.com in default dns view **")
        log_print("*********************************************************************")
        #data={"fqdn":"custom_test1.com","view":"custom_dns_view","grid_primary":[{"name": config.grid_member4_fqdn,"stealth": False}]}
        data={"fqdn":"default_test1.com","view":"default_dns_view","grid_primary":[{"name": config.grid_member1_fqdn,"stealth": False},{"name": config.grid_member2_fqdn,"stealth": False},{"name": config.grid_member3_fqdn,"stealth": False},{"name": config.grid_member4_fqdn,"stealth": False}]}
        test1_ref=ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data))
        log_print(test1_ref)
        if bool(re.match("\"zone_auth*.*default_test1.com",str(test1_ref))):
                log_print("Zone default_test1.com creation successful")
                sleep(5)
        else:
                log_print("Zone default_test1.com creation unsuccessful")
                print("\n")
                assert False

        log_print("\n***************************************************")
        log_print("* Change DDNS DNS View as custom dns view at Configure DDNS at Grid DHCP Level *")
        log_print("***************************************************")
        log_print("\n************************************************************")
        log_print("******** Enable IPv4 & IPv6 DNS interface on all members******")
        log_print("**************************************************************")
        enable_ipv4_and_ipv6_dns_interface_on_all_members()
	log_print("***************************************************")
        get_ref = ib_NIOS.wapi_request('GET', object_type="networkview", grid_vip=config.grid_vip)
        networkview_ref = ''
        for ref in json.loads(get_ref):
		if ref['name'] == 'default':
             	#if ref['name'] == 'custom':
                	networkview_ref = ref['_ref']
        log_print(networkview_ref)
	data = {"ddns_dns_view": "default_dns_view"}
        response = ib_NIOS.wapi_request('PUT',ref=networkview_ref,fields=json.dumps(data), grid_vip=config.grid_vip)
        log_print(response)
        if bool(re.match("\"networkview*.",str(response))):
            log_print("Changed ddns dns view at configure ddns success")
            sleep(15)
        else:
            log_print("Failed to change ddns dns view at configure ddns")
            assert False

        log_print("\n***********************************************************")
        log_print(" * Add authoritative reverse mapping zone in default dns view")
        log_print("*************************************************************")
        data = {"fqdn": "0.0.10.in-addr.arpa","zone_format":"IPV4","grid_primary": [{"name": config.grid_member_fqdn,"stealth": False},{"name": config.grid_member1_fqdn,"stealth": False},{"name": config.grid_member2_fqdn,"stealth": False},{"name": config.grid_member3_fqdn,"stealth": False}],"view": "default_dns_view"}
        response=ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data))
        print(response)
        if bool(re.match("\"zone_auth*.*0.0.10.in-addr.arpa",str(response))):
                log_print("10.0.0.0/24 RPMZ creation successful")
                sleep(5)
        else:
                log_print("10.0.0.0/24 RMZ creation unsuccessful")
                assert False

        log_print("\n*****************************************************")
        log_print(" Add Authoritative reverse mapping zone in default dns view")
        log_print("******************************************************")
        ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
        ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
        data = {"fqdn": ipv6_network+"::/64","zone_format":"IPV6","grid_primary": [{"name": config.grid_member_fqdn,"stealth": False},{"name": config.grid_member1_fqdn,"stealth": False},{"name": config.grid_member2_fqdn,"stealth": False},{"name": config.grid_member3_fqdn,"stealth": False}],"view": "default_dns_view"}
        ref=ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data))
        print(ref)
	sleep(20)
	restart_services()
        print("Test Case 140 Execution Completed")

    @pytest.mark.run(order=141)
    def test_141_Update_custom_DNS_view_domain_as_ddns_domain_name_in_member_dhcp_properties(self):
        log_print("\n************************************************************")
        log_print("* TC : 141 - Update custom DNS view domain as ddns domain name in member dhcp properties *")
        log_print("**************************************************************")
        log_print("Fetch member dhcp properties reference")
        member_dhcp_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
        log_print(member_dhcp_ref)
        member_dhcp_ref = json.loads(member_dhcp_ref)[0]['_ref']
        print(member_dhcp_ref)
        data={"ipv6_ddns_domainname": "default_test1.com","ipv6_domain_name": "default_test1.com","options":[{"name":"domain-name","value":"default_test1.com"}],"ddns_domainname":"default_test1.com"}
        response = ib_NIOS.wapi_request('PUT',ref=member_dhcp_ref,fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if bool(re.match("\"member:dhcpproperties*.",str(response))):
                log_print("Custom DNS view domain name updated successfully for DDNS domain name in grid dhcp properties")
                sleep(15)
                restart_services()
        else:
            log_print("Enabling DDNS update unsuccessful")
            assert False
        print("Test Case 141 Execution Completed")



    @pytest.mark.run(order=142)
    def test_142_Add_Custom_Network_View_MultiMaster_Zones_at_Member_DHCP_Properties_for_DDNS_updates(self):
        log_print("\n***************************************************")
        log_print("* TC : 142 - Add Custom Network View MultiMaster Zones at Member DHCP Properties for DDNS updates *")
        log_print("***************************************************")
        log_print("Fetch custom_.test1.com reference")
        ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
        ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=default_test1.com", grid_vip=config.grid_vip)
        zone_ref = ''
        for ref in json.loads(get_ref):
            if ref['view'] == 'default_dns_view':
                zone_ref = ref['_ref']
        print(zone_ref)
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=10.0.0.0/24",grid_vip=config.grid_vip)
        reverse_ref = ''
        for ref in json.loads(get_ref):
            if ref['view'] == 'default_dns_view':
                reverse_ref = ref['_ref']
        print(reverse_ref)
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn="+ipv6_network+"::/64",grid_vip=config.grid_vip)
        ipv6_reverse_ref = ''
        for ref in json.loads(get_ref):
            if ref['view'] == 'default_dns_view':
                ipv6_reverse_ref = ref['_ref']
        print(ipv6_reverse_ref)
        member_dhcp_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
        member_dhcp_ref = json.loads(member_dhcp_ref)[0]['_ref']
        print(member_dhcp_ref)
        data = {"ddns_zone_primaries": [{"dns_grid_primary":config.grid_member1_fqdn,"dns_grid_zone": {"_ref": reverse_ref},"zone_match": "GRID"},{"dns_grid_primary": config.grid_member2_fqdn,"dns_grid_zone": {"_ref": reverse_ref},"zone_match": "GRID"},{"dns_grid_primary": config.grid_member3_fqdn,"dns_grid_zone": {"_ref": reverse_ref},"zone_match": "GRID"},{"dns_grid_primary": config.grid_member1_fqdn,"dns_grid_zone": {"_ref": zone_ref},"zone_match": "GRID"},{"dns_grid_primary": config.grid_member2_fqdn,"dns_grid_zone": {"_ref": zone_ref},"zone_match": "GRID"},{"dns_grid_primary": config.grid_member3_fqdn,"dns_grid_zone": {"_ref": zone_ref},"zone_match": "GRID"},{"dns_grid_primary":config.grid_member1_fqdn,"dns_grid_zone": {"_ref": ipv6_reverse_ref},"zone_match": "GRID"},{"dns_grid_primary":config.grid_member2_fqdn,"dns_grid_zone": {"_ref": ipv6_reverse_ref},"zone_match": "GRID"},{"dns_grid_primary":config.grid_member3_fqdn,"dns_grid_zone": {"_ref": ipv6_reverse_ref},"zone_match": "GRID"}]}
        response = ib_NIOS.wapi_request('PUT',ref=member_dhcp_ref,fields=json.dumps(data), grid_vip=config.grid_vip)
        log_print(response)
        if bool(re.match("\"member:dhcpproperties*.",str(response))):
            log_print("Multimaster zones added to the list of zones in DDNS updates")
	    sleep(15)
            restart_services()
        else:
            log_print("Failed to add multimaster zones to list of zones in DDNS updates")
            assert False
        print("Test Case 142 Execution Completed")

    @pytest.mark.run(order=143)
    def test_143_Check_if_the_dhcpd_conf_file_contains_3_DNS_NS_configured_as_part_of_the_preferred_multi_domain_ddns_list(self):
        log_print("\n************************************************************************************")
        log_print("* TC : 143 - Check if the dhcpd.conf file contains 3 DNS NS configured as part of the preferred multi domain ddns list *")
        log_print("************************************************************************************")
	sleep(30)
        try:
            os.system('scp -o StrictHostKeyChecking=no root@'+config.grid_vip+':/infoblox/var/dhcpd_conf/dhcpd.conf .')
        except OSError as e:
            log_print("Scp failed")
            log_print(e)
            assert False

        try:
            file = open("dhcpd.conf",'r')
            file_content = file.read()
            file.close()
            log_print("\n\n")
            log_print(file_content)
            data1 = 'zone "default_test1.com." {\n\tprimary '+config.grid_member1_vip+', '+config.grid_member2_vip+', '+config.grid_member3_vip+';'
            data2 = 'zone "0.0.10.in-addr.arpa." {\n\tprimary '+config.grid_member1_vip+', '+config.grid_member2_vip+', '+config.grid_member3_vip+';'
            if data1 in file_content and data2 in file_content:
                log_print("The dhcpd.conf file contains 3 nameservers as part of preferred multi domain ddns list")
                print(data1)
                print(data2)
                assert True
            else:
                log_print("The dhcpd.conf file does not contain 3 nameservers as part of preferred multi domain ddns list")
                assert False
        except IOError as e:
            log_print("Unable to open dhcpd.conf file")
            log_print(e)
            assert False
        print("Test Case 143 Execution Completed")

    @pytest.mark.run(order=144)
    def test_144_Check_if_the_dhcpdv6_conf_file_contains_3_DNS_NS_configured_as_part_of_the_preferred_multi_domain_ddns_list(self):
        log_print("\n************************************************************************************")
        log_print("* TC : 144 - Check if the dhcpdv6.conf file contains 3 DNS NS configured as part of the preferred multi domain ddns list *")
        log_print("************************************************************************************")
	sleep(30)
        try:
            os.system('scp -o StrictHostKeyChecking=no root@'+config.grid_vip+':/infoblox/var/dhcpdv6_conf/dhcpdv6.conf .')
        except OSError as e:
            log_print("Scp failed")
            log_print(e)
            assert False

        try:
            file = open("dhcpdv6.conf",'r')
            file_content = file.read()
            file.close()
            log_print("\n\n")
            log_print(file_content)
            data1 = 'zone "default_test1.com." {\n\tprimary '+config.grid_member1_vip+', '+config.grid_member2_vip+', '+config.grid_member3_vip+';'
            data2 = 'ip6.arpa." {\n\tprimary '+config.grid_member1_vip+', '+config.grid_member2_vip+', '+config.grid_member3_vip+';'
            if data1 in file_content and data2 in file_content:
                log_print("The dhcpdv6.conf file contains 3 nameservers as part of preferred multi domain ddns list")
                print(data1)
                print(data2)
                assert True
            else:
                log_print("The dhcpdv6.conf file does not contain 3 nameservers as part of preferred multi domain ddns list")
                assert False
        except IOError as e:
            log_print("Unable to open dhcpdv6.conf file")
            log_print(e)
            assert False
        print("Test Case 144 Execution Completed")

    @pytest.mark.run(order=145)
    def test_145_Request_IPv4_lease_capture_syslogs_validate_DNS_NS1_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 145 - Request lease and capture syslogs and validate the first dns name server used for ddns updates in syslogs and added A, TXT and PTR records  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F default_test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member1_vip+'#53','Added reverse map from.*by server '+config.grid_member1_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv4_records_validation()
        print("\nTest Case 145 Executed Successfully")

    @pytest.mark.run(order=146)
    def test_146_Request_IPv6_lease_capture_syslogs_validate_DNS_NS1_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 146 - Request ipv6 lease and capture syslogs and validate the first dns name server used for ddns updates in syslogs and added AAAA, TXT and PTR records *")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.master1_ipv6_ip)+' -A -n 1 -h default_test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member1_vip+'#53','Added reverse map from.*by server '+config.grid_member1_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv6_records_validation()
        print("\nTest Case 146 Executed Successfully")

    @pytest.mark.run(order=147)
    def test_147_Disable_IPv4_and_IPv6_DNS_interface_on_DNS_NS1_and_NS2_from_the_preferred_Multi_Domaine_DDNS_list(self):
        log_print("\n****************************************************************************************************************")
        log_print("* TC : 147 - Disable IPv4 and IPv6 DNS interface on first and second DNS server from the preferred Multi Domaine DDNS list ******")
        log_print("******************************************************************************************************************")
        disable_ipv4_and_ipv6_dns_on_member(1)
        disable_ipv4_and_ipv6_dns_on_member(2)
        print("Test Case 147 Execution Completed")

    @pytest.mark.run(order=148)
    def test_148_Request_IPv4_lease_capture_syslogs_validate_DNS_NS3_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 148 - Request lease and capture syslogs and validate the third dns name server used for ddns updates in syslogs and added A, TXT and PTR records  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F default_test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member3_vip+'#53','Added reverse map from.*by server '+config.grid_member3_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv4_records_validation()
        print("\nTest Case 148 Executed Successfully")


    @pytest.mark.run(order=149)
    def test_149_Request_IPv6_lease_capture_syslogs_validate_DNS_NS3_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 149 - Request ipv6 lease and capture syslogs and validate the third dns name server used for ddns updates in syslogs and added AAAA, TXT and PTR records *")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.master1_ipv6_ip)+' -A -n 1 -h default_test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member3_vip+'#53','Added reverse map from.*by server '+config.grid_member3_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv6_records_validation()
        print("\nTest Case 149 Executed Successfully")

    @pytest.mark.run(order=150)
    def test_150_Disable_IPv4_and_IPv6_DNS_interface_on_DNS_NS3_from_the_preferred_Multi_Domaine_DDNS_list(self):
        log_print("\n****************************************************************************************************************")
        log_print("* TC : 150 - Disable IPv4 and IPv6 DNS interface on third DNS server from the preferred Multi Domaine DDNS list ******")
        log_print("******************************************************************************************************************")
        disable_ipv4_and_ipv6_dns_on_member(3)
        print("Test Case 150 Execution Completed")

    @pytest.mark.run(order=151)
    def test_151_Request_IPv6_lease_capture_syslogs_validate_deferred_ddns_updates_in_syslogs(self):
        log_print("\n************************************************************")
        log_print("* TC : 151 - Request ipv6 lease and capture syslogs and validate deferred ddns updates in syslogs *")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.master1_ipv6_ip)+' -A -n 1 -h default_test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'deferred'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Addition of forward map for.*deferred','Addition of reverse map for.*deferred']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        print("\nTest Case 151 Executed Successfully")

    @pytest.mark.run(order=152)
    def test_152_Enable_IPv4_and_IPv6_DNS_interface_on_DNS_NS2_from_the_preferred_Multi_Domaine_DDNS_list(self):
        log_print("\n*****************************************************")
        log_print("* Enable IPv4 and IPv6 DNS interface on second DNS server from the preferred Multi Domaine DDNS list *")
        log_print("******************************************************")
        enable_ipv4_and_ipv6_dns_on_member(2)
        print("Test Case 152 Execution Completed")

    @pytest.mark.run(order=153)
    def test_153_Request_IPv4_lease_capture_syslogs_validate_DNS_NS2_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 153 - Request lease and capture syslogs and validate the second dns name server used for ddns updates in syslogs and added A, TXT and PTR records  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F default_test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member2_vip+'#53','Added reverse map from.*by server '+config.grid_member2_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv4_records_validation()
        print("\nTest Case 153 Executed Successfully")

    @pytest.mark.run(order=154)
    def test_154_Request_IPv6_lease_capture_syslogs_validate_DNS_NS2_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 154 - Request ipv6 lease and capture syslogs and validate the second dns name server used for ddns updates in syslogs and added AAAA, TXT and PTR records *")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.master1_ipv6_ip)+' -A -n 1 -h default_test1.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member2_vip+'#53','Added reverse map from.*by server '+config.grid_member2_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv6_records_validation()
        print("\nTest Case 154 Executed Successfully")


    @pytest.mark.run(order=155)
    def test_155_Add_4_Default_Primary_DNS_NS_For_DDNS_Updates_at_Member_DHCP_Properties(self):
        log_print("\n***************************************************")
        log_print("* TC : 155 - Add 4 Default Primary DNS NS For DDNS Updates at Member DHCP Properties   *")
        log_print("***************************************************")
        data = {"ddns_zone_primaries": [{"dns_grid_primary": config.grid_member3_fqdn,"zone_match": "ANY_GRID"},{"dns_grid_primary": config.grid_member2_fqdn,"zone_match": "ANY_GRID"},{"dns_grid_primary": config.grid_member1_fqdn,"zone_match": "ANY_GRID"},{"dns_grid_primary": config.grid_member_fqdn,"zone_match": "ANY_GRID"}]}
        member_dhcp_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
        member_dhcp_ref = json.loads(member_dhcp_ref)[0]['_ref']
        print(member_dhcp_ref)
        response = ib_NIOS.wapi_request('PUT',ref=member_dhcp_ref,fields=json.dumps(data), grid_vip=config.grid_vip)
        log_print(response)
        if bool(re.match("\"member:dhcpproperties*.",str(response))):
            log_print("Multimaster zones added to the list of zones in DDNS updates at member dhcp properties ")
	    sleep(15)
            restart_services()
        else:
            log_print("Failed to add multimaster zones to list of zones in DDNS updates at member dhcp properties")
            assert False
        print("Test Case 155 Execution Completed")

    @pytest.mark.run(order=156)
    def test_156_Check_if_dhcpd_conf_file_contains_3_Default_DNS_NS_configured_as_part_of_preferred_multi_domain_ddns_list(self):
        log_print("\n************************************************************************************")
        log_print("* TC : 156 - Check if dhcpd.conf file contains 3 Default DNS NS as part of preferred multi domain ddns list *")
        log_print("************************************************************************************")
	sleep(30)
        try:
            os.system('scp -o StrictHostKeyChecking=no root@'+config.grid_vip+':/infoblox/var/dhcpd_conf/dhcpd.conf .')
        except OSError as e:
            log_print("Scp failed")
            log_print(e)
            assert False

        try:
            file = open("dhcpd.conf",'r')
            file_content = file.read()
            file.close()
            log_print("\n\n")
            log_print(file_content)
            data1 = 'zone "default_test1.com." {\n\tprimary '+config.grid_member3_vip+', '+config.grid_member2_vip+', '+config.grid_member1_vip+';'
            data2 = 'zone "0.0.10.in-addr.arpa." {\n\tprimary '+config.grid_member3_vip+', '+config.grid_member2_vip+', '+config.grid_member1_vip+';'
            if data1 in file_content and data2 in file_content:
                log_print("The dhcpd.conf file contains 3 nameservers as part of preferred multi domain ddns list")
                print(data1)
                print(data2)
                assert True
            else:
                log_print("The dhcpd.conf file does not contain 3 nameservers as part of preferred multi domain ddns list")
                assert False
        except IOError as e:
            log_print("Unable to open dhcpd.conf file")
            log_print(e)
            assert False
        print("Test Case 156 Execution Completed")

    @pytest.mark.run(order=157)
    def test_157_Check_if_dhcpdv6_conf_file_contains_3_Default_DNS_NS_configured_as_part_of_preferred_multi_domain_ddns_list(self):
        log_print("\n************************************************************************************")
        log_print("* TC : 157 - Check if dhcpdv6.conf file contains 3 Default DNS NS as part of preferred multi domain ddns list *")
        log_print("************************************************************************************")
	sleep(30)
        try:
            os.system('scp -o StrictHostKeyChecking=no root@'+config.grid_vip+':/infoblox/var/dhcpdv6_conf/dhcpdv6.conf .')
        except OSError as e:
            log_print("Scp failed")
            log_print(e)
            assert False

        try:
            file = open("dhcpdv6.conf",'r')
            file_content = file.read()
            file.close()
            log_print("\n\n")
            log_print(file_content)
            data1 = 'zone "default_test1.com." {\n\tprimary '+config.grid_member3_vip+', '+config.grid_member2_vip+', '+config.grid_member1_vip+';'
            data2 = 'ip6.arpa." {\n\tprimary '+config.grid_member3_vip+', '+config.grid_member2_vip+', '+config.grid_member1_vip+';'
            if data1 in file_content and data2 in file_content:
                log_print("The dhcpdv6.conf file contains 3 nameservers as part of preferred multi domain ddns list")
                print(data1)
                print(data2)
                assert True
            else:
                log_print("The dhcpdv6.conf file does not contain 3 nameservers as part of preferred multi domain ddns list")
                assert False
        except IOError as e:
            log_print("Unable to open dhcpdv6.conf file")
            log_print(e)
            assert False
        print("Test Case 157 Execution Completed")

####### Custom DNS View Multi Master Zone scenarios at Member DHCP Properties end here ##



######################################################
###### Multi Master at IPv4 and IPv6 Network #########
######################################################

    @pytest.mark.run(order=158)
    def test_158_Change_DDNS_DNS_view_as_default_at_Config_DDNS_at_Grid_DHCP_level(self):
        log_print("\n********************************")
        log_print("* TC : 158 - Change DDNS DNS view as default at Config DDNS at Grid DHCP level *")
        log_print("**********************************")
        log_print("******** Enable IPv4 & IPv6 DNS interface on all members******")
        log_print("**************************************************************")
        enable_ipv4_and_ipv6_dns_interface_on_all_members()
	log_print("**************************************************************")
        get_ref = ib_NIOS.wapi_request('GET', object_type="networkview", grid_vip=config.grid_vip)
        networkview_ref = ''
        for ref in json.loads(get_ref):
            if ref['name'] == 'default':
                networkview_ref = ref['_ref']
        log_print(networkview_ref)
        data = {"ddns_dns_view": "default"}
        response = ib_NIOS.wapi_request('PUT',ref=networkview_ref,fields=json.dumps(data), grid_vip=config.grid_vip)
        log_print(response)
        if bool(re.match("\"networkview*.",str(response))):
            log_print("Multimaster zones added to the list of zones in DDNS updates")
	    sleep(15)
            restart_services()
        else:
            log_print("Failed to add multimaster zones to list of zones in DDNS updates")
            assert False
        print("Test Case 158 Execution Completed")

    @pytest.mark.run(order=159)
    def test_159_Update_DDNS_Domain_Name_at_IPv4_Network_Level(self):
        log_print("\n******************************************")
        log_print("* TC : 159 - Update DDNS Domain Name as test3.com at Network Level *")
        log_print("********************************************")
        get_ref = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
        network_ref = ''
        for ref in json.loads(get_ref):
            if ref['network_view'] == 'default':
                network_ref = ref['_ref']
        log_print(network_ref)
        data = {"ddns_domainname": "test3.com","options": [{"name": "domain-name","num": 15,"use_option": True,"value": "test3.com","vendor_class": "DHCP"}]}
        response = ib_NIOS.wapi_request('PUT',ref=network_ref,fields=json.dumps(data), grid_vip=config.grid_vip)
        log_print(response)
        if bool(re.match("\"network*.*default",str(response))):
            log_print("Multimaster zone added to the list of zones in DDNS updates at IPv4 Network level")
	    sleep(15)
            restart_services()
        else:
            log_print("Failed to add multimaster zones to list of zones in DDNS updates at IPv4 Network level")
            assert False
        print("Test Case 159 Execution Completed")

    @pytest.mark.run(order=160)
    def test_160_Update_DDNS_Domain_Name_at_IPv6_Network_Level(self):
        log_print("\n******************************************")
        log_print("* TC : 160 - Update DDNS Domain as test3.com at Network level *")
        log_print("********************************************")
        get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6network", grid_vip=config.grid_vip)
        network_ref = ''
        for ref in json.loads(get_ref):
            if ref['network_view'] == 'default':
                network_ref = ref['_ref']
        log_print(network_ref)
        data = {"ddns_domainname": "test3.com","options": [{"name": "domain-name","num": 15,"use_option": True,"value": "test3.com","vendor_class": "DHCP"}]}
        response = ib_NIOS.wapi_request('PUT',ref=network_ref,fields=json.dumps(data), grid_vip=config.grid_vip)
        log_print(response)
        if bool(re.match("\"ipv6network*.*default",str(response))):
            log_print("Multimaster zones added to the list of zones in DDNS updates at IPv6 Network level ")
	    sleep(15)
            restart_services()
        else:
            log_print("Failed to add multimaster zones to list of zones in DDNS updates at IPv6 Network level")
            assert False
        print("Test Case 160 Execution Completed")

    @pytest.mark.run(order=161)
    def test_161_Check_if_dhcpd_conf_file_contains_3_Default_DNS_NS_configured_as_part_of_preferred_multi_domain_ddns_list(self):
        log_print("\n************************************************************************************")
        log_print("* TC : 161 - Check if dhcpd.conf file contains 3 Default DNS NS as part of preferred multi domain ddns list *")
        log_print("************************************************************************************")
	sleep(30)
        try:
            os.system('scp -o StrictHostKeyChecking=no root@'+config.grid_vip+':/infoblox/var/dhcpd_conf/dhcpd.conf .')
        except OSError as e:
            log_print("Scp failed")
            log_print(e)
            assert False

        try:
            file = open("dhcpd.conf",'r')
            file_content = file.read()
            file.close()
            log_print("\n\n")
            log_print(file_content)
            data1 = 'zone "test3.com." {\n\tprimary '+config.grid_member3_vip+', '+config.grid_member2_vip+', '+config.grid_member1_vip+';'
            data2 = 'zone "0.0.10.in-addr.arpa." {\n\tprimary '+config.grid_member3_vip+', '+config.grid_member2_vip+', '+config.grid_member1_vip+';'
            if data1 in file_content and data2 in file_content:
                log_print("The dhcpd.conf file contains 3 nameservers as part of preferred multi domain ddns list")
                print(data1)
                print(data2)
                assert True
            else:
                log_print("The dhcpd.conf file does not contain 3 nameservers as part of preferred multi domain ddns list")
                assert False
        except IOError as e:
            log_print("Unable to open dhcpd.conf file")
            log_print(e)
            assert False
        print("Test Case 161 Execution Completed")

    @pytest.mark.run(order=162)
    def test_162_Check_if_dhcpdv6_conf_file_contains_3_Default_DNS_NS_configured_as_part_of_preferred_multi_domain_ddns_list(self):
        log_print("\n************************************************************************************")
        log_print("* TC : 162 - Check if dhcpdv6.conf file contains 3 Default DNS NS as part of preferred multi domain ddns list *")
        log_print("************************************************************************************")
	sleep(30)
        try:
            os.system('scp -o StrictHostKeyChecking=no root@'+config.grid_vip+':/infoblox/var/dhcpdv6_conf/dhcpdv6.conf .')
        except OSError as e:
            log_print("Scp failed")
            log_print(e)
            assert False

        try:
            file = open("dhcpdv6.conf",'r')
            file_content = file.read()
            file.close()
            log_print("\n\n")
            log_print(file_content)
            data1 = 'zone "test3.com." {\n\tprimary '+config.grid_member3_vip+', '+config.grid_member2_vip+', '+config.grid_member1_vip+';'
            data2 = 'ip6.arpa." {\n\tprimary '+config.grid_member3_vip+', '+config.grid_member2_vip+', '+config.grid_member1_vip+';'
            if data1 in file_content and data2 in file_content:
                log_print("The dhcpdv6.conf file contains 3 nameservers as part of preferred multi domain ddns list")
                print(data1)
                print(data2)
                assert True
            else:
                log_print("The dhcpdv6.conf file does not contain 3 nameservers as part of preferred multi domain ddns list")
                assert False
        except IOError as e:
            log_print("Unable to open dhcpdv6.conf file")
            log_print(e)
            assert False
        print("Test Case 162 Execution Completed")

    @pytest.mark.run(order=163)
    def test_163_Request_IPv4_lease_capture_syslogs_validate_DNS_NS1_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 163 - Request lease and capture syslogs and validate the first dns name server used for ddns updates in syslogs and added A, TXT and PTR records  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F test3.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member3_vip+'#53','Added reverse map from.*by server '+config.grid_member3_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv4_records_validation()
        print("\nTest Case 163 Executed Successfully")

    @pytest.mark.run(order=164)
    def test_164_Request_IPv6_lease_capture_syslogs_validate_DNS_NS1_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 164 - Request ipv6 lease and capture syslogs and validate the first dns name server used for ddns updates in syslogs and added AAAA, TXT and PTR records *")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.master1_ipv6_ip)+' -A -n 1 -h test3.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member3_vip+'#53','Added reverse map from.*by server '+config.grid_member3_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv6_records_validation()
        print("\nTest Case 164 Executed Successfully")


    @pytest.mark.run(order=165)
    def test_165_Disable_IPv4_and_IPv6_DNS_interface_on_DNS_NS1_and_NS2_from_the_preferred_Multi_Domaine_DDNS_list(self):
        log_print("\n****************************************************************************************************************")
        log_print("* TC : 165 - Disable IPv4 and IPv6 DNS interface on first and second DNS server from the preferred Multi Domaine DDNS list ******")
        log_print("******************************************************************************************************************")
        disable_ipv4_and_ipv6_dns_on_member(3)
	disable_ipv4_and_ipv6_dns_on_member(2)
        print("Test Case 165 Execution Completed")

    @pytest.mark.run(order=166)
    def test_166_Request_IPv4_lease_capture_syslogs_validate_DNS_NS3_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 166 - Request lease and capture syslogs and validate the third dns name server used for ddns updates in syslogs and added A, TXT and PTR records  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F test3.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member1_vip+'#53','Added reverse map from.*by server '+config.grid_member1_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv4_records_validation()
        print("\nTest Case 166 Executed Successfully")

    @pytest.mark.run(order=167)
    def test_167_Request_IPv6_lease_capture_syslogs_validate_DNS_NS3_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 167 - Request ipv6 lease and capture syslogs and validate the third dns name server used for ddns updates in syslogs and added AAAA, TXT and PTR records *")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.master1_ipv6_ip)+' -A -n 1 -h test3.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member1_vip+'#53','Added reverse map from.*by server '+config.grid_member1_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv6_records_validation()
        print("\nTest Case 167 Executed Successfully")

    @pytest.mark.run(order=168)
    def test_168_Enable_IPv4_and_IPv6_DNS_interface_on_DNS_NS2_from_the_preferred_Multi_Domaine_DDNS_list(self):
        log_print("\n*****************************************************")
        log_print("* TC : 168 - Enable IPv4 and IPv6 DNS interface on second DNS server from the preferred Multi Domaine DDNS list *")
        log_print("******************************************************")
        enable_ipv4_and_ipv6_dns_on_member(2)
        print("Test Case 168 Execution Completed")

    @pytest.mark.run(order=169)
    def test_169_Request_IPv4_lease_capture_syslogs_validate_DNS_NS2_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 169 - Request lease and capture syslogs and validate the second dns name server used for ddns updates in syslogs and added A, TXT and PTR records  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F test3.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member2_vip+'#53','Added reverse map from.*by server '+config.grid_member2_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv4_records_validation()
        print("\nTest Case 169 Executed Successfully")


    @pytest.mark.run(order=170)
    def test_170_Request_IPv6_lease_capture_syslogs_validate_DNS_NS2_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 170 - Request ipv6 lease and capture syslogs and validate the second dns name server used for ddns updates in syslogs and added AAAA, TXT and PTR records *")
        log_print("**************************************************************")
        log_print("Request IPv6 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i '+str(config.master1_ipv6_ip)+' -A -n 1 -h test3.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member2_vip+'#53','Added reverse map from.*by server '+config.grid_member2_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv6_records_validation()
        print("\nTest Case 170 Executed Successfully")

################## IPv4&v6 Network Cases end here #########

##################################
###### IPv4 Range Scenarios ######
##################################

    @pytest.mark.run(order=171)
    def test_171_Enable_IPv4_and_IPv6_DNS_interface_on_all_members(self):
	log_print("**************************************************************")
        log_print("* TC : 171 - Enable IPv4 & IPv6 DNS interface on all members******")
        log_print("**************************************************************")
        enable_ipv4_and_ipv6_dns_interface_on_all_members()
        print("Test Case 171 Execution Completed")

    @pytest.mark.run(order=172)
    def test_172_Update_DDNS_Domain_Name_at_IPv4_Range_level(self):
        log_print("\n******************************************")
        log_print("* TC : 172 - Update DDNS Domain Name as test4.com at IPv6 Range level *")
        log_print("********************************************")
        get_ref = ib_NIOS.wapi_request('GET', object_type="range", grid_vip=config.grid_vip)
        network_ref = ''
        for ref in json.loads(get_ref):
            if ref['network_view'] == 'default':
                network_ref = ref['_ref']
        log_print(network_ref)
        data = {"ddns_domainname": "test4.com","options": [{"name": "domain-name","num": 15,"use_option": True,"value": "test4.com","vendor_class": "DHCP"}]}
        response = ib_NIOS.wapi_request('PUT',ref=network_ref,fields=json.dumps(data), grid_vip=config.grid_vip)
        log_print(response)
        if bool(re.match("\"range*.*default",str(response))):
            log_print("Multimaster zones added to the list of zones in DDNS updates")
	    sleep(15)
            restart_services()
        else:
            log_print("Failed to add multimaster zones to list of zones in DDNS updates")
            assert False
        print("Test Case 172 Execution Completed")


## For IPv6 Range DDNS_Domainname and options won't support ##

    @pytest.mark.run(order=173)
    def test_173_Check_if_dhcpd_conf_file_contains_3_Default_DNS_NS_configured_as_part_of_preferred_multi_domain_ddns_list(self):
        log_print("\n************************************************************************************")
        log_print("* TC : 173 - Check if dhcpd.conf file contains 3 Default DNS NS as part of preferred multi domain ddns list *")
        log_print("************************************************************************************")
	sleep(30)
        try:
            os.system('scp -o StrictHostKeyChecking=no root@'+config.grid_vip+':/infoblox/var/dhcpd_conf/dhcpd.conf .')
        except OSError as e:
            log_print("Scp failed")
            log_print(e)
            assert False

        try:
            file = open("dhcpd.conf",'r')
            file_content = file.read()
            file.close()
            log_print("\n\n")
            log_print(file_content)
            data1 = 'zone "test4.com." {\n\tprimary '+config.grid_member3_vip+', '+config.grid_member2_vip+', '+config.grid_member1_vip+';'
            data2 = 'zone "0.0.10.in-addr.arpa." {\n\tprimary '+config.grid_member3_vip+', '+config.grid_member2_vip+', '+config.grid_member1_vip+';'
            if data1 in file_content and data2 in file_content:
                log_print("The dhcpd.conf file contains 3 nameservers as part of preferred multi domain ddns list")
                print(data1)
                print(data2)
                assert True
            else:
                log_print("The dhcpd.conf file does not contain 3 nameservers as part of preferred multi domain ddns list")
                assert False
        except IOError as e:
            log_print("Unable to open dhcpd.conf file")
            log_print(e)
            assert False
        print("Test Case 173 Execution Completed")

    @pytest.mark.run(order=174)
    def test_174_Request_IPv4_lease_capture_syslogs_validate_DNS_NS1_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 174 - Request lease and capture syslogs and validate the first dns name server used for ddns updates in syslogs and added A, TXT and PTR records  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F test4.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member3_vip+'#53','Added reverse map from.*by server '+config.grid_member3_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv4_records_validation()
        print("\nTest Case 174 Executed Successfully")

    @pytest.mark.run(order=175)
    def test_175_Disable_IPv4_and_IPv6_DNS_interface_on_DNS_NS1_and_NS2_from_the_preferred_Multi_Domaine_DDNS_list(self):
        log_print("\n****************************************************************************************************************")
        log_print("* TC : 175 - Disable IPv4 and IPv6 DNS interface on first and second DNS server from the preferred Multi Domaine DDNS list ******")
        log_print("******************************************************************************************************************")
        disable_ipv4_and_ipv6_dns_on_member(3)
        disable_ipv4_and_ipv6_dns_on_member(2)
        print("Test Case 175 Execution Completed")

    @pytest.mark.run(order=176)
    def test_176_Request_IPv4_lease_capture_syslogs_validate_DNS_NS3_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 176 - Request lease and capture syslogs and validate the third dns name server used for ddns updates in syslogs and added A, TXT and PTR records  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F test4.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member1_vip+'#53','Added reverse map from.*by server '+config.grid_member1_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv4_records_validation()
        print("\nTest Case 176 Executed Successfully")


    @pytest.mark.run(order=177)
    def test_177_Enable_IPv4_and_IPv6_DNS_interface_on_DNS_NS2_from_the_preferred_Multi_Domaine_DDNS_list(self):
        log_print("\n*****************************************************")
        log_print("* TC : 177 - Enable IPv4 and IPv6 DNS interface on second DNS server from the preferred Multi Domaine DDNS list *")
        log_print("******************************************************")
        enable_ipv4_and_ipv6_dns_on_member(2)
        print("Test Case 177 Execution Completed")

    @pytest.mark.run(order=178)
    def test_178_Request_IPv4_lease_capture_syslogs_validate_DNS_NS2_used_for_ddns_updates_in_syslogs_and_added_records(self):
        log_print("\n************************************************************")
        log_print("* TC : 178 - Request lease and capture syslogs and validate the second dns name server used for ddns updates in syslogs and added A, TXT and PTR records  *")
        log_print("**************************************************************")
        log_print("Request IPv4 IP lease using dras")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F test4.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server '+config.grid_member2_vip+'#53','Added reverse map from.*by server '+config.grid_member2_vip+'#53']
        for i in data:
                result = re.search(i, log_validation)
                if result == None:
                        assert False
                else:
                        assert True
        IPv4_records_validation()
        print("\nTest Case 178 Executed Successfully")



#### DDNS and DIG operation ####

    @pytest.mark.run(order=179)
    def test_179_Perform_DDNS_updates_and_validate_DIG_working_for_dynamic_record(self):
        log_print("\n******************************************************************")
        log_print("* TC : 179 - Perform DDNS updates and validate DIG working for the dynamic records *")
        log_print("********************************************************************")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(05)
        global log_validation
        for i in range(10):
                dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid_vip)+' -n 1 -x l=10.0.0.0 -h -F test4.com'
                print(dras_cmd)
                dras_cmd = os.system(dras_cmd)
                sleep(02)
                print("output is ",dras_cmd)
                if dras_cmd == 0:
                        print("Got the lease")
                        break
                else:
                        print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid_vip)
        log_print(log_validation)
        record_name = re.search('Added new forward map from(.*)by server ',log_validation)
        record_name = record_name.group(0)
        def Convert(string):
                li = list(string.split(" "))
                return li
        str1 = Convert(record_name)
	record_name = str1[5]
        log_print(record_name)
	ip_address = str1[7]
	log_print(ip_address)	
	dig=os.popen("dig @"+config.grid_member1_vip+" "+record_name).read()	
	print(dig)
	if ip_address in dig and "ANSWER: 1" in dig:
		assert True
		log_print(ip_address+" present in the dig response")
	else:
		assert False
	log_print("\nTest Case 179 Executed Successfully")


    @pytest.mark.run(order=180)
    def test_180_Negative_scenario_SIGN_MMDNS_zone_and_validate_error_message(self):
        log_print("\n******************************************")
        log_print("* TC : 180 - Negative scenario : SIGN MMDNS zone and validate error message *")
        log_print("********************************************")
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=test1.com", grid_vip=config.grid_vip)
        zone_ref = ''
        for ref in json.loads(get_ref):
            if ref['view'] == 'default':
                zone_ref = ref['_ref']
        log_print(zone_ref)
        operation = "SIGN"
	status,response = ib_NIOS.wapi_request('POST', ref= zone_ref, params='?_function=dnssec_operation', fields=json.dumps({"operation":operation}),grid_vip=config.grid_vip)
	log_print(response)
	data = "Cannot sign a multi-master zone"
	if data in response:
		assert True
	else:
		assert False
	log_print(" ** validated ** "+data)
	log_print("\nTest Case 180 Executed Successfully")
	

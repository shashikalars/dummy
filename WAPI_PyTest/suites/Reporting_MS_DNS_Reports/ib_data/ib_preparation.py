"""
 Copyright (c) Infoblox Inc., 2016

 Modle Name  : ib_preparation
 Description : This module is used for Prepration 

 Author : Raghavendra MN
 History: 05/26/2016(Created)
"""
import config
import json
import os
import pytest
import pexpect
import re
import sys
import subprocess
import unittest
from time import sleep

import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from logger import logger
import ib_utils.ib_papi as papi
from ib_utils.ib_system import search_dump 
from ib_utils.ib_validaiton import compare_results 
import ib_utils.ib_system as ib_system
path=os.getcwd()
"""
Report Name: "DNS Top Clients per Domain" (DNS Query)
Configuring Domain names in "Monitor queries made to the following domains"(Grid Reporting Properties)
Adding Zones & RR's and Querying zones from different clients by adding different ipaddress..
Author: Raghavendra MN
"""
def dns_top_clients_per_domain():
    logger.info("Preparation:%s",logger.info(sys._getframe().f_code.co_name))
    #Configuring  domain names in Grid Reporting Properteis. 
    rc=subprocess.call(['perl','ib_data/DNS_Query/DNS_Top_Clients_per_Domain/DNS_Top_Clients_Per_Domain.pl',config.grid_vip,'domain1.top_clients_per_domain.com,domain2.top_clients_per_domain.com,domain3.top_clients_per_domain.com'])
    print(rc)
    print(config.grid_vip)
    #sleep(600)
    print("---------------***********-----")
    #adding Zone
    zone1 = {"fqdn":"top_clients_per_domain.com","view":"default","grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
    response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(zone1))
    print(response)
    print("-------------------------------------****************---------------------------")
    #Restarting 
    """
    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    print(grid)
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    sleep(60)
    """
    sleep(20)
    grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
    print(grid)
    ref = json.loads(grid)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
    logger.info("Wait for 20 sec.,")
    sleep(30) 

    #Adding RR's
    a_record1 = {"name":"domain1.top_clients_per_domain.com","ipv4addr":"10.10.10.10"}
    ref_admin_a = ib_NIOS.wapi_request('POST', object_type="record:a", fields=json.dumps(a_record1))
    print(ref_admin_a)
    a_record2 = {"name":"domain2.top_clients_per_domain.com","ipv4addr":"20.20.20.20"}
    ref_admin_a = ib_NIOS.wapi_request('POST', object_type="record:a", fields=json.dumps(a_record2))
    print(ref_admin_a)
    a_record3 = {"name":"domain3.top_clients_per_domain.com","ipv4addr":"30.30.30.30"}
    ref_admin_a = ib_NIOS.wapi_request('POST', object_type="record:a", fields=json.dumps(a_record3))
    print(ref_admin_a)
    #VLAN SET
    ib_system.vlanset(config.client_vm,"10.35.0.0")
    #Configure Client#6
    #os.system("sudo ifconfig eth1 inet "+config.client_eth1_ip6+" netmask "+config.client_netmask+" up")
    sleep(60)
    os.system("dig @"+config.grid_vip+" -f ib_data/DNS_Query/DNS_Top_Clients_per_Domain/client1.input -b "+config.client_eth1_ip6 +" > /dev/null 2>&1")
    sleep(5)
    # os.system("sudo ifconfig eth1 inet "+config.client_eth1_ip6+" netmask "+config.client_netmask+" down")
    sleep(60)   
    #Configure Client#7
    #os.system("sudo ifconfig eth1 inet "+config.client_eth1_ip7+" netmask "+config.client_netmask+" up")
    sleep(60)   
    os.system("dig @"+config.grid_vip+" -f ib_data/DNS_Query/DNS_Top_Clients_per_Domain/client2.input -b "+config.client_eth1_ip7 +" > /dev/null 2>&1" )
    sleep(5)
    #os.system("sudo ifconfig eth1 inet "+config.client_eth1_ip7+" netmask "+config.client_netmask+" down")
    sleep(60)    
    #Configure Client#8
    #os.system("sudo ifconfig eth1 inet "+config.client_eth1_ip8+" netmask "+config.client_netmask+" up")
    sleep(60)
    os.system("dig @"+config.grid_vip+" -f ib_data/DNS_Query/DNS_Top_Clients_per_Domain/client3.input -b "+config.client_eth1_ip8 +" > /dev/null 2>&1")
    sleep(5)
    #os.system("sudo ifconfig eth1 inet "+config.client_eth1_ip8+" netmask "+config.client_netmask+" down")
    sleep(60)
    return rc 


"""
Report:DNS Top Clients
Adding Zones and RR's and performing Dig operaiton from differnet Clients.
Auther: Raghavendra MN
"""
def dns_top_clients():
    
    logger.info("Preparation:%s",logger.info(sys._getframe().f_code.co_name))
    #TEST Preparation, Adding zone 'dns_top_clients.com',  GM as Primary , Member1 & Member2 as secondary for resolving members
    #zone1 = {"fqdn":"dns_top_clients.com","view":"default","grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
    #response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(zone1))

    '''

    #Restarting 
    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    sleep(60)

    #adding RR's with default TTL
    a_record1 = {"name":"arec1.dns_top_clients.com","ipv4addr":"2.2.2.2"}
    ref_admin_a = ib_NIOS.wapi_request('POST', object_type="record:a", fields=json.dumps(a_record1))

    #adding RR's with default TTL
    a_record1 = {"name":"brec1.dns_top_clients.com","ipv4addr":"2.2.2.2","ttl":2}
    ref_admin_a = ib_NIOS.wapi_request('POST', object_type="record:a", fields=json.dumps(a_record1))

    '''    

    #client1
    os.system("dig @"+config.grid_ms_ip+" -f ib_data/DNS_Query/DNS_Top_Clients/10q.txt -b "+config.client_ip1+" > /dev/null 2>&1")
    sleep(5)
    
    #client2
    os.system("dig @"+config.grid_ms_ip+" -f ib_data/DNS_Query/DNS_Top_Clients/20q.txt -b "+config.client_ip2+" > /dev/null 2>&1")
    sleep(5)
    
    #client3
    #os.system("dig @"+config.grid_ms_ip+" -f ib_data/DNS_Query/DNS_Top_Clients/20q.txt -b "+config.client_ip3+" > /dev/null 2>&1")
    #sleep(5)

"""
Report:DNS Top Requested Domain Names
Auther: Raghavendra MN
"""
def dns_top_requested_domain_names():
    
    logger.info("Preparation:%s",logger.info(sys._getframe().f_code.co_name))
    fp=os.popen("dig @"+config.grid_ms_ip+" -f "+path+"/ib_data/DNS_Query/DNS_Top_Requested_Domain_Names/top_requested_domains.txt")

    '''
    fp=os.popen(path+"/ib_data/DNS_Query/DNS_Top_Requested_Domain_Names/QueryPerf_input_TopRequestedDomain.txt")
    falg=0
    for i in fp.readlines():
        print(i)
	
        flag=flag+1
        if flag==10000:
            break
        else:
            output = os.popen("dig @"+config.grid_vip+" "+i).read()
            print(output)
    '''

"""
Report: DNS Top Timed-Out Recursive Queries
Auther: Raghavendra MN
"""
def dns_top_timed_out_recursive_queries():
    
    logger.info("Preparation:%s",logger.info(sys._getframe().f_code.co_name))

    logger.info("Enabling Recursion")
    member_dns =  ib_NIOS.wapi_request('GET', object_type="member:dns?host_name~="+config.grid_fqdn)
    print(member_dns)
    ref = json.loads(member_dns)[0]['_ref']
    enable_recursion_forwarder={"allow_recursive_query":True}
    response = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(enable_recursion_forwarder))

    #Restarting 
    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    sleep(60)
    
    fp=os.popen("~/API_Automation/WAPI_PyTest/suites/Reporting_FR_part1/dduq/dduq -i "+config.grid_member1_vip+" -f "+path+"/ib_data/DNS_Query/DNS_Top_Timed_Out_Recursive_Queries/queryperf.txt -t 1")
    
    logger.info("Cleanup,disabling recursion")
    member_dns =  ib_NIOS.wapi_request('GET', object_type="member:dns?host_name~="+config.grid_member1_fqdn)
    ref = json.loads(member_dns)[0]['_ref']
    disable_recursion_forwarder={"allow_recursive_query":False,"use_recursive_query_setting":False,"use_forwarders":False}
    response = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(disable_recursion_forwarder))

    #Restarting 
    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    sleep(60)


def dns_top_nxdomain_noerror():
    logger.info("Preparation:%s",logger.info(sys._getframe().f_code.co_name))
    logger.info("Adding zone 57.in-addr.arpa, dns_top_nxdomain_or_noerror.com & 7.7.7.7.ip6.arpa") 
    #TEST Preparation, Adding zone 'dns_top_clients.com',  GM as Primary , Member1 & Member2 as secondary for resolving members
    zone1 = {"fqdn":"dns_top_nxdomain_or_noerror.com","view":"default","grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
    response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(zone1))

    zone2 = {"fqdn":"57.0.0.0/8","view":"default","zone_format":"IPV4","grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
    response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(zone2))

    zone3 = {"fqdn":"7777::/64","view":"default","zone_format":"IPV6","grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
    response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(zone3))

    #Restarting 
    logger.info("Restaring DNS Service")
    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    sleep(60)
    
    logger.info("Performing Dig query")
    #fp=os.popen("~/API_Automation/WAPI_PyTest/suites/Reporting_FR_part1/dduq/dduq -i "+config.grid_vip+" -f "+path+"/ib_data/DNS_Query/Top_DNS_NXDOMAIN_NOERROR/queryperf.txt")
    
    fp=os.popen("dig @"+config.grid_ms_ip+" -f "+path+"ib_data/DNS_Query/Top_DNS_NXDOMAIN_NOERROR/queryperf.txt")
    
    logger.info("%s",''.join(fp.readlines()))
    
    '''
    fp=os.popen(path+"/ib_data/DNS_Query/Top_DNS_NXDOMAIN_NOERROR/queryperf.txt")
    falg=0
    for i in fp.readlines():
        #print(i)
        flag=flag+1
        if flag==10000:
            break
        else:
            output = os.popen("dig @"+config.grid_vip+" "+i).read()
            print(output)
    '''
    
    #Cleanup 
    logger.info("Cleanup deleting added zones")
    del_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn~=dns_top_nxdomain_or_noerror.com")
    ref = json.loads(del_zone)[0]['_ref']
    del_status = ib_NIOS.wapi_request('DELETE', object_type = ref)

    del_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn~=57.0.0.0/8")
    ref = json.loads(del_zone)[0]['_ref']
    del_status = ib_NIOS.wapi_request('DELETE', object_type = ref)

    del_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn~=7777::/64")
    ref = json.loads(del_zone)[0]['_ref']
    del_status = ib_NIOS.wapi_request('DELETE', object_type = ref)

    #Restarting
    logger.info("Restaring DNS Service")
    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    sleep(60)

"""
   Preparation for Security Repor  .
   
"""

def threat_protection_reports():
    logger.info("Disabling Security Cateogry to avoid auto rule update")
    papi.disable_security_category(config.grid_vip)
    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    logger.info("Performing restart service")
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    logger.info("Wait for 60 Sec.,")
    sleep(60)
    logger.info("Enable MGMT on TP member")
    #papi.enable_mgmt(config.grid_vip,config.grid_member5_vip)
    papi.enable_mgmt(config.grid_vip,config.grid_member1_vip)
    logger.info("Wait for 60 Sec.,")
    sleep(240)
    logger.info("Upload Threat Protection Rulesets")
    papi.upload_ruleset(config.grid_vip,config.olympic_ruleset)
    logger.info("Wait for 10 Sec.,")
    sleep(10)
    logger.info("Disable Auto Rules")
    #papi.disable_auto_rules(config.grid_member5_vip)
    papi.disable_auto_rules(config.grid_member1_vip)
    logger.info("Wait for 10 Sec.,")
    sleep(10)
    logger.info("Publish Changes")
    papi.publish_changes(config.grid_vip)
    logger.info("Wait for 30 Sec.,")
    sleep(30)
    logger.info("Disable System Rules")
    papi.disable_tp_system_rules(config.grid_vip)
    logger.info("Publish Changes")
    papi.publish_changes(config.grid_vip)
    logger.info("Wait for 60 Sec.,")
    sleep(90)
    logger.info("Add TCP Rules")
    papi.add_tcp_rules(config.grid_vip)
    logger.info("Add UDP Rules")
    papi.add_udp_rules(config.grid_vip)
    logger.info("Add Rate Limit Rules")
    papi.add_rate_limit_rules(config.grid_vip)
    papi.enable_security_category(config.grid_vip)

    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    logger.info("Wait for 30 Sec.,")
    sleep(30)
    logger.info("Enable Threat Protection Service")
    papi.enable_tp_service(config.grid_vip)
    logger.info("Wait for 60 Sec.,")
    sleep(60)
    logger.info("Restart Service")
    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    logger.info("Wait for 30 Sec.,")
    sleep(30)
    logger.info("Generate Threat Protection related Data")
    #papi.add_threate_protection_data(config.grid_member5_vip)
    papi.add_threate_protection_data(config.grid_member1_vip)
    logger.info("Publish Changes")
    papi.publish_changes(config.grid_vip)
    logger.info("Wait for 60 Sec.,")
    sleep(60)

def security_rpz_reports():
    logger.info("Enable recursion")
    papi.enable_forwarder_and_recusion(config.grid_vip)
    papi.restart_dns_dhcp_service(config.grid_vip)
    sleep(30)
    logger.info("Add Analytics Zone")
    papi.add_analytics_zone(config.grid_vip,config.grid_member5_vip)
    logger.info("Add RPZ Zone")
    papi.add_rpz_zone(config.grid_vip,config.grid_member5_vip)
    logger.info("Add RPZ Rules")
    papi.add_rpz_data()
    logger.info("Modify Analityics Properties")
    papi.modify_analityics_properties(config.grid_vip)
    sleep(30)
    logger.info("Enable Analityics service")
    papi.enable_analytics_service(config.grid_vip)
    logger.info("Wait for 90 Sec.,")
    sleep(90);
    logger.info("Restart Service")
    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    logger.info("Wait for 120 Sec.,")
    sleep(120)
    logger.info("Generate RPZ and Analityics Data")
    papi.add_analityics_data(config.grid_member5_vip)
    logger.info("Wait for 60 Sec.,")
    sleep(60)
    logger.info("Disable Recursion")
    papi.disable_forwarder_and_recusion(config.grid_vip)
    logger.info("Restart Service")
    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    logger.info("Wait for 60 Sec.,")
    sleep(60)

def rpz_security():
    logger.info ("Enable Recursion, zone transfer and Update in Grid 1 and Grid 2.")
    papi.enable_forwarders_recursion(config.grid_vip)
    papi.enable_forwarders_update(config.grid2_vip)
    logger.info("Restart Service")
    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    logger.info("Wait for 120 Sec.,")
    sleep(60)
    data = {"fqdn": "rpz_feed.com","grid_secondaries": [{"name": config.grid_fqdn,"stealth": False,"grid_replicate": False}],\
    "external_primaries":[{"address": config.grid2_vip,"name": config.grid2_fqdn,"stealth":False}],"rpz_type":"FEED",\
    "rpz_policy": "GIVEN","use_external_primary":True}
    response = ib_NIOS.wapi_request('POST', object_type="zone_rp", fields=json.dumps(data))
    sleep(60)
    data1 = {"fqdn":"rpz_feed.com","grid_primary": [{"name": config.grid2_fqdn,"stealth": False}]}
    response = ib_NIOS.wapi_request_2('POST', object_type="zone_rp", fields=json.dumps(data1))
    papi.add_rpz_records(config.grid2_vip)
    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    logger.info("Wait for 120 Sec.,")
    sleep(120)

    logger.info("Restart Service")
    grid =  ib_NIOS.wapi_request_2('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request_2('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request_2('POST', object_type = ref + "?_function=restartservices")
    logger.info("Wait for 120 Sec.,")
    sleep(120)

    logger.info("Restart Service")
    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    logger.info("Wait for 120 Sec.,")
    sleep(600)
    papi.queries_rpz_records(config.grid_vip)
    
        

"""
Report:DHCP Fingerprint Reports
Adding Networks, Range and requesting leases
"""

def dhcp_fingerprint():
    #Network View
    network_view = {"name":"network_view_dhcp"}
    response = ib_NIOS.wapi_request('POST', object_type="networkview", fields=json.dumps(network_view))
    logger.info(response)
    # Add Network
    data = {"members":[{"_struct": "dhcpmember", "ipv4addr":config.grid_member1_vip,"name":config.grid_member1_fqdn}], \
     "network": "10.0.0.0/8", "network_view": "network_view_dhcp"}
    response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data))
    logger.info(response)
    data = {"members":[{"_struct": "dhcpmember", "ipv4addr":config.grid_member1_vip,"name":config.grid_member1_fqdn}], \
     "network": "51.0.0.0/24", "network_view": "network_view_dhcp"}
    response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data))
    logger.info(response)
    #Add Range
    range_obj = {"start_addr":"51.0.0.1","end_addr":"51.0.0.100","member":{"_struct": "dhcpmember","ipv4addr":config.grid_member1_vip, \
     "name":config.grid_member1_fqdn},"network_view":"network_view_dhcp", \
     "options":[{"_struct": "dhcpoption","name":"dhcp-lease-time","num": 51,"use_option": True,"value": "300","vendor_class": "DHCP"}]}
    range = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(range_obj))
    logger.info(range)
    logger.info("--------------------Added range----------------")
    
    range_obj = {"start_addr":"10.0.0.1","end_addr":"10.0.0.100","member":{"_struct": "dhcpmember","ipv4addr":config.grid_member1_vip, \
     "name":config.grid_member1_fqdn},"network_view":"network_view_dhcp", \
     "options":[{"_struct": "dhcpoption","name":"dhcp-lease-time","num": 51,"use_option": True,"value": "300","vendor_class": "DHCP"}]}
    range = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(range_obj))
    logger.info(range)
    
    
    # Add Shared network
    network_ref_list=[]
    network_10 = ib_NIOS.wapi_request('GET', object_type="network?network=10.0.0.0/8")
    print(network_10)
    ref_10 = json.loads(network_10)[0]['_ref']
    network_ref_list.append({"_ref":ref_10})
    network_51 = ib_NIOS.wapi_request('GET', object_type="network?network=51.0.0.0/24")
    print(network_10)
    ref_51 = json.loads(network_51)[0]['_ref']
    network_ref_list.append({"_ref":ref_51})
    shared_obj={"name":"sharednetworks","networks":network_ref_list,"network_view":"network_view_dhcp"}
    shared1 = ib_NIOS.wapi_request('POST',object_type="sharednetwork",fields=json.dumps(shared_obj))
    logger.info(shared1)
    logger.info("----------------Added shared network----------------------")
    #Restarting
    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    sleep(160)

    # Generate Requested leases for Device Trend, Device Class Trend, Top Device Class Identified, Fingerprint Name Change Detected and (Voip Phones/Adapters)
    #cmd=os.popen("sudo /import/tools/qa/tools/dras_opt55/dras -i "+config.grid_member1_vip+" -n 10 -w -D -O 55:0103060c0f2a424378")
    cmd=os.popen("sudo /import/tools/qa/tools/dras_opt55/dras -i "+config.grid_member1_vip+" -n 10 -w -D -O 55:0103060c0f2a424378")
    #fp=os.popen("sudo /import/tools/qa/tools/dras/dras -i "+config.grid_vip+" -n 20 -x l=20.0.0.0")
    logger.info("%s", ''.join( cmd.readlines()))
    sleep(10)
    logger.info("Generate Requested leases for Device Trend, Device Class Trend, Top Device Class Identified, Fingerprint Name Change Detected and (Voip Phones/Adapters)")
    # Switches
    cmd1=os.popen("sudo /import/tools/qa/tools/dras_opt55/dras -i "+config.grid_member1_vip+" -n 10 -w -D -O 55:0103060f1B")
    logger.info("%s", ''.join( cmd1.readlines()))
    sleep(30)
    # Apple Airport  ( Device Fingerprint Name Change Detected Report )
    cmd2=os.popen("sudo /import/tools/qa/tools/dras_opt55/dras -i "+config.grid_member1_vip+" -n 1 -w -D -O 55:1c03060f -a  aa:11:bb:22:cc:33")
    logger.info("%s", ''.join( cmd2.readlines()))
    sleep(180)
    logger.info("Apple Airport  ( Device Fingerprint Name Change Detected Report )")
    # AP Meraki
    #cmd3=os.popen("sudo /import/tools/qa/tools/dras_opt55/dras -i "+config.grid_member1_vip+" -n 1 -w -D -O 55:0103060c0f1a1c28292a -a aa:11:bb:22:cc:33")
    cmd3=os.popen("sudo /import/tools/qa/tools/dras_opt55/dras -i "+config.grid_member1_vip+" -n 1 -w -D -O  55:0103060f0c13 -a aa:11:bb:22:cc:33")
    logger.info("%s", ''.join( cmd3.readlines()))

    # Add Fingerprint Filter to Generate lease for DHCP TOP DEVICE Denied IP Address
    fingerprint_data = {"name":"fingerprint_filter","fingerprint":["Alps Electric"]}
    shared = ib_NIOS.wapi_request('POST', object_type="filterfingerprint", fields=json.dumps(fingerprint_data))
    logger.info("Add Fingerprint Filter to Generate lease for DHCP TOP DEVICE Denied IP Address")

    # Modify DHCP Range 51.0.0.1 to 51.0.0.100 Fingerprint Filter in Range.
    get_range = ib_NIOS.wapi_request('GET', object_type="range?start_addr=51.0.0.1")
    ref_range = json.loads(get_range)[0]['_ref']
    modify_range={"fingerprint_filter_rules":[{"filter": "fingerprint_filter","permission": "Deny"}]}
    modify_filter = ib_NIOS.wapi_request('PUT',object_type=ref_range,fields=json.dumps(modify_range))
    logger.info("Modify DHCP Range 51.0.0.1 to 51.0.0.100 Fingerprint Filter in Range.")
    
   # Modify DHCP Range 10.0.0.1 to 11.0.0.100 Fingerprint Filter in Range.
    get_range = ib_NIOS.wapi_request('GET', object_type="range?start_addr=10.0.0.1")
    ref_range = json.loads(get_range)[0]['_ref']
    modify_range={"fingerprint_filter_rules":[{"filter": "fingerprint_filter","permission": "Deny"}]}
    modify_filter = ib_NIOS.wapi_request('PUT',object_type=ref_range,fields=json.dumps(modify_range))
    logger.info("Modify DHCP Range 10.0.0.1 to 10.0.0.100 Fingerprint Filter in Range.")
 
    #Restarting
    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    sleep(160)


    # Alps Electric For DHCP TOP DEVICE Denied IP Address
    logger.info("Alps Electric For DHCP TOP DEVICE Denied IP Address")
    cmd4=os.popen("sudo /import/tools/qa/tools/dras_opt55/dras -i "+config.grid_member1_vip+" -n 1 -w -D -O 55:010304060f")
    logger.info("%s", ''.join( cmd4.readlines()))
    sleep(30)
    #Restarting
    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    sleep(450)

    # Delete Shared Network
    delshared = ib_NIOS.wapi_request('GET', object_type="sharednetwork?name=sharednetworks")
    ref = json.loads(delshared)[0]['_ref']
    del_status = ib_NIOS.wapi_request('DELETE', object_type = ref)

    # Delete and Disable Networks
    delnetwork = ib_NIOS.wapi_request('GET', object_type="network?network=10.0.0.0/8")
    ref = json.loads(delnetwork)[0]['_ref']
    del_status = ib_NIOS.wapi_request('DELETE', object_type = ref)
    delnetwork = ib_NIOS.wapi_request('GET', object_type="network?network=51.0.0.0/24")
    ref_51 = json.loads(delnetwork)[0]['_ref']
    data = {"disable":True}
    del_status = ib_NIOS.wapi_request('PUT',object_type=ref_51,fields=json.dumps(data))

"""
Report:DHCP Top Lease Clients
Adding Networks, Range and requesting leases
Author : Manimaran
"""

def dhcp_top_lease_clients():
    #Network View
    net_obj = {"members":[{"_struct": "dhcpmember", "ipv4addr":config.grid_member1_vip ,"name":config.grid_member1_fqdn}], \
               "network": "10.0.0.0/8", "network_view": "network_view_dhcp"}
    network1 = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(net_obj))
    print(network1)
    print("-----Network1----")
    data = {"members":[{"_struct": "dhcpmember", "ipv4addr":config.grid_member1_vip,"name":config.grid_member1_fqdn}], \
    "network": "42.0.0.0/24", "network_view": "network_view_dhcp"}
    response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data))
    print(response)
    print("-----response----")
    
    range_obj = {"start_addr":"10.0.0.1","end_addr":"10.0.0.100","member":{"_struct": "dhcpmember","ipv4addr":config.grid_member1_vip, \
    "name":config.grid_member1_fqdn},"network_view":"network_view_dhcp", \
    "options":[{"_struct": "dhcpoption","name":"dhcp-lease-time","num": 51,"use_option": True,"value": "900","vendor_class": "DHCP"}]}
    range_v = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(range_obj))
    print(range_v)
    
    range_obj = {"start_addr":"42.0.0.1","end_addr":"42.0.0.100","member":{"_struct": "dhcpmember","ipv4addr":config.grid_member1_vip, \
    "name":config.grid_member1_fqdn},"network_view":"network_view_dhcp", \
    "options":[{"_struct": "dhcpoption","name":"dhcp-lease-time","num": 51,"use_option": True,"value": "900","vendor_class": "DHCP"}]}
    range_v = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(range_obj))
    print(range_v)
    sleep(60)   

    #Restarting
    print("Restart Services")
    grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
    ref = json.loads(grid)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
    sleep(80)
    # Shared Network
    
    network_ref_list_1=[]
    network_10 = ib_NIOS.wapi_request('GET', object_type="network?network=10.0.0.0/8")
    ref_10 = json.loads(network_10)[0]['_ref']
    network_ref_list_1.append({"_ref":ref_10})
    network_41 = ib_NIOS.wapi_request('GET', object_type="network?network=42.0.0.0/24")
    
    ref_41 = json.loads(network_41)[0]['_ref']
    print(network_41)
    network_ref_list_1.append({"_ref":ref_41})
    shared_obj = {"name":"test_shared","networks":network_ref_list_1,"network_view":"network_view_dhcp"}
    print(network_ref_list_1)
    shared1 = ib_NIOS.wapi_request('POST',object_type="sharednetwork",fields=json.dumps(shared_obj))
    sleep(20)
    print("Restart Services")
    grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
    ref = json.loads(grid)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
    sleep(800)
   
    # Request Leases
    cmd6=os.popen("sudo /import/tools/qa/tools/dras/dras -i "+config.grid_member1_vip+" -n 1 -a 77:22:33:44:55:99")
    logger.info("%s", ''.join( cmd6.readlines()))
    sleep(120)

    cmd7=os.popen("sudo /import/tools/qa/tools/dras/dras -i "+config.grid_member1_vip+" -n 1 -a 77:22:33:44:55:99")
    logger.info("%s", ''.join( cmd7.readlines()))
    sleep(180)
    # Delete Shared Network
    del_shared = ib_NIOS.wapi_request('GET', object_type="sharednetwork?name~=test_shared")
    ref = json.loads(del_shared)[0]['_ref']
    del_status = ib_NIOS.wapi_request('DELETE', object_type = ref)

    # Delete and Disable Networks
    del_network_10 = ib_NIOS.wapi_request('GET', object_type="network?network~=10.0.0.0/8")
    ref = json.loads(del_network_10)[0]['_ref']
    del_status = ib_NIOS.wapi_request('DELETE', object_type = ref)

    disable_network_41 = ib_NIOS.wapi_request('GET', object_type="network?network=42.0.0.0/24")
    ref_41 = json.loads(disable_network_41)[0]['_ref']
    print(ref_41)
    data = {"disable":True}
    del_status = ib_NIOS.wapi_request('PUT',object_type=ref_41,fields=json.dumps(data))
    print(del_status)
    print("Restart Services")
    grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
    ref = json.loads(grid)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
    sleep(20)

"""
Report:DHCPv4 Usage Statistics
Adding Networks, Range and requesting leases
Author : Manimaran
"""
def dhcpv4_usage_statistics():
    #MAC Filter
    mac_filter = {"name":"mac1"}
    response = ib_NIOS.wapi_request('POST', object_type="filtermac", fields=json.dumps(mac_filter))

    mac_filter_2 = {"name":"mac2"}
    response = ib_NIOS.wapi_request('POST', object_type="filtermac", fields=json.dumps(mac_filter_2))

    # MAC Filter Address
    mac_filter_address_1 = {"filter":"mac1","mac":"11:22:33:44:55:66"}
    response = ib_NIOS.wapi_request('POST', object_type="macfilteraddress", fields=json.dumps(mac_filter_address_1))

    mac_filter_address_2 = {"filter":"mac2","mac":"99:66:33:88:55:22"}
    response = ib_NIOS.wapi_request('POST', object_type="macfilteraddress", fields=json.dumps(mac_filter_address_2))

    #Network View
    network_view = {"name":"custom_view_1"}
    response = ib_NIOS.wapi_request('POST', object_type="networkview", fields=json.dumps(network_view))

    #Add Network
    network_data = {"members":[{"_struct": "dhcpmember", "ipv4addr": config.grid_member2_vip,"name":config.grid_member2_fqdn}], \
                    "network":"10.0.0.0/8","network_view":"custom_view_1"}
    response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(network_data))

    network_data_30 = {"members":[{"_struct": "dhcpmember", "ipv4addr": config.grid_member2_vip,"name":config.grid_member2_fqdn}], \
                       "network":"30.0.0.0/24","network_view":"custom_view_1"}
    response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(network_data_30))

    network_data_32 = {"members":[{"_struct": "dhcpmember", "ipv4addr": config.grid_member2_vip,"name":config.grid_member2_fqdn}],\
                        "network":"32.0.0.0/24","network_view":"custom_view_1"}
    response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(network_data_32))
    #Add Range
    
    range_obj = {"start_addr":"10.0.0.1","end_addr":"10.0.0.50","network_view":"custom_view_1","member":{"_struct": "dhcpmember", \
    "ipv4addr":config.grid_member2_vip,"name": config.grid_member2_fqdn},"mac_filter_rules":[{"filter": "mac1","permission": "Allow"}]}
    range = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(range_obj))
    
    
    range_obj = {"start_addr":"30.0.0.1","end_addr":"30.0.0.50","network_view":"custom_view_1","member":{"_struct": "dhcpmember", \
    "ipv4addr":config.grid_member2_vip,"name": config.grid_member2_fqdn},"mac_filter_rules":[{"filter": "mac1","permission": "Allow"}]}
    range = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(range_obj))

    range_obj_25 = {"start_addr":"32.0.0.1","end_addr":"32.0.0.100","network_view":"custom_view_1","member":{"_struct": "dhcpmember", \
    "ipv4addr":config.grid_member2_vip,"name": config.grid_member2_fqdn},"mac_filter_rules":[{"filter": "mac2","permission": "Allow"}]}
    range = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(range_obj_25))

    #Add Fixed Address
    fixed_address = {"ipv4addr":"30.0.0.32","mac":"88:55:22:99:66:33","network_view":"custom_view_1"}
    response = ib_NIOS.wapi_request('POST', object_type="fixedaddress", fields=json.dumps(fixed_address))

    fixed_address_2 = {"ipv4addr":"32.0.0.32","mac":"55:22:66:33:99:55","network_view":"custom_view_1"}
    response = ib_NIOS.wapi_request('POST', object_type="fixedaddress", fields=json.dumps(fixed_address_2))

    # Add Shared Network
    network_ref_list = []
    network_10 = ib_NIOS.wapi_request('GET', object_type="network?network=10.0.0.0/8")
    print(network_10)
    ref10 = json.loads(network_10)[0]['_ref']
    network_ref_list.append({"_ref":ref10})
    network_30 = ib_NIOS.wapi_request('GET', object_type="network?network=30.0.0.0/24")
    ref30 = json.loads(network_30)[0]['_ref']
    network_ref_list.append({"_ref":ref30})
    network_32 = ib_NIOS.wapi_request('GET', object_type="network?network=32.0.0.0/24")
    ref32 = json.loads(network_32)[0]['_ref']
    network_ref_list.append({"_ref":ref32})

    range_obj = {"name":"shareddhcp","networks":network_ref_list,"network_view": "custom_view_1"}
    shared = ib_NIOS.wapi_request('POST', object_type="sharednetwork", fields=json.dumps(range_obj))

    #Restarting
    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")

    sleep(120)

    cmd9=os.popen("sudo /import/tools/qa/tools/dras/dras -i "+config.grid_member2_vip+" -n 1 -a 11:22:33:44:55:66")
    logger.info("%s", ''.join( cmd9.readlines()))
    sleep(30)

    cmd10=os.popen("sudo /import/tools/qa/tools/dras/dras -i "+config.grid_member2_vip+" -n 1 -x l=32.0.0.0 -a 99:66:33:88:55:22")
    logger.info("%s", ''.join( cmd10.readlines()))
    sleep(10)


    #Restarting
    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")

    sleep(180)
    # Delete Network

    # Delete and Disable Networks
    del_network_10 = ib_NIOS.wapi_request('GET', object_type="network?network=10.0.0.0/8")
    ref = json.loads(del_network_10)[0]['_ref']
    del_status = ib_NIOS.wapi_request('DELETE', object_type = ref)

    disable_network = ib_NIOS.wapi_request('GET', object_type="network?network=30.0.0.0/24")
    ref_30 = json.loads(disable_network)[0]['_ref']
    data = {"disable":True}
    del_status = ib_NIOS.wapi_request('PUT',object_type=ref_30,fields=json.dumps(data))

    disable_network_32 = ib_NIOS.wapi_request('GET', object_type="network?network=32.0.0.0/24")
    ref_32 = json.loads(disable_network_32)[0]['_ref']
    data = {"disable":True}
    del_status = ib_NIOS.wapi_request('PUT',object_type=ref_32,fields=json.dumps(data))

"""
Report: Discovery
Author: Manimaran
"""

def discovery():
    #Network View
    network_view = {"name":"discovery_view"}
    response = ib_NIOS.wapi_request('POST', object_type="networkview", fields=json.dumps(network_view))

    papi.enable_discovery_service(config.grid_vip,config.grid_member4_fqdn)
    sleep(180)
    # Add Network
    network_data = {"members":[{"_struct": "dhcpmember", "ipv4addr": config.grid_member3_vip,"name":config.grid_member3_fqdn}], \
                    "network":"10.40.16.0/24","network_view":"discovery_view"}
    response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(network_data))
    print(response)
    print("discovery network created")
    # Get Network for Enabling Discovery
    grid =  ib_NIOS.wapi_request('GET', object_type="network?network~=10.40.16.0/24")
    ref = json.loads(grid)[0]['_ref']

    # Enable Grid Discovery Properties using following script
    rc=subprocess.call(['perl','ib_data/Discovery/discovery_preparation.pl',config.grid_vip,config.grid_member4_fqdn])

    # Enable Discovery in Network 10.40.16.0/24
    data = {"enable_discovery":True,"discovery_member":config.grid_member4_fqdn}
    enable_network_discovery = ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))



"""
Report: DNS Statistics per Zone,  DNS Statistics per DNS View
Author: Sunil Kumar
"""

def dns_statistics_per_view_zone():
    logger.info("Import Data through CSV for DNS Statistics per view/zone reports")

    logger.info("Add Name server Group with Grid master as Grid primary")
    nsg1 = {"name":"nsg1","grid_primary":[{"name":config.grid_fqdn}]}
    nsg1_response = ib_NIOS.wapi_request('POST', object_type="nsgroup", fields=json.dumps(nsg1))
    logger.info("Adding Authoritative Zones and RR's through CSV import")
    papi.import_csv("ib_data/DDI_Utilization/DNS_statistics_per_zone_view/FMP_DDI_Utilization.csv")
    logger.info("Adding IPV4 Authoritative Zones and RR's through CSV import")
    papi.import_csv("ib_data/DDI_Utilization/DNS_statistics_per_zone_view/IPv4_DDI_Stats.csv")
    logger.info("Adding IPv6 Authoritative Zones and RR's through CSV import")
    papi.import_csv("ib_data/DDI_Utilization/DNS_statistics_per_zone_view/IPv6_DDI_stats.csv")

    logger.info("Grid Restart services after adding the Zones and RR's")
    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    sleep(60)


"""
Report: IPAMv4 Network Usage Statistics, IPAMv4 Network Usage Trend, IPAMv4 Top Utilized networks and DHCP Top Utilized networks
Author: Sunil Kumar
"""
def ipam_network_usage_statistics_trend():

    logger.info("Add Network '10.0.0.0/8' with Grid master as Member assignment")
    network1 = {"network":"10.0.0.0/8","network_view":"default","members":[{"name":config.grid_fqdn,"_struct": "dhcpmember"}],"options":[{"name": "dhcp-lease-time","value": "74390400"}]}
    network1_response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(network1))

    network1_get = ib_NIOS.wapi_request('GET', object_type="network?network=10.0.0.0/8")
    network1_ref = json.loads(network1_get)[0]['_ref']

    logger.info("Add Network '165.0.0.0/8' with Grid master as Member assignment")
    network2 = {"network":"165.0.0.0/8","network_view":"default","members":[{"name":config.grid_fqdn,"_struct": "dhcpmember"}],"options":[{"name": "dhcp-lease-time","value": "74390400"}],}
    network2_response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(network2))
    network2_get = ib_NIOS.wapi_request('GET', object_type="network?network=165.0.0.0/8")
    network2_ref = json.loads(network2_get)[0]['_ref']


    logger.info("Add Range '165.0.0.1-165.10.10.255' in '165.0.0.0/8' with Grid master as Member assignment")
    range1 = {"network":"165.0.0.0/8","network_view":"default","member":{"_struct": "dhcpmember","name":config.grid_fqdn},"start_addr":"165.0.0.1","end_addr":"165.10.10.255"}
    range1_response = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(range1))


    logger.info("Add 10 fixed address in '165.0.0.0/8'")
    for i in range(10):
        fix_addr = {"network":"165.0.0.0/8","network_view":"default","ipv4addr":"165.0.30."+str(i),"mac":"00:00:00:00:00:"+str(i)}
        fix_response = ib_NIOS.wapi_request('POST', object_type="fixedaddress", fields=json.dumps(fix_addr))

    logger.info("Add 10 Reservation in '165.0.0.0/8'")
    for i in range(10):
        reserve = {"network":"165.0.0.0/8","network_view":"default","ipv4addr":"165.0.30.1"+str(i),"match_client":"RESERVED"}
        reserve_response = ib_NIOS.wapi_request('POST', object_type="fixedaddress", fields=json.dumps(reserve))

    logger.info("Add shared Network '165.0.0.0/8', 10.0.0.0/8 ")
    shared_network = {"name":"shared_ipv4","networks":[{"_ref":str(network1_ref)},{"_ref":str(network2_ref)}]}
    shared_network_response = ib_NIOS.wapi_request('POST', object_type="sharednetwork", fields=json.dumps(shared_network))

    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    sleep(60)

    for i in range(10):
        fin=os.popen("sudo /import/tools/qa/tools/dras/dras  -n 200 -i"+config.grid_vip)
        logger.info(''.join(fin.readlines()))
        sleep(10)

    logger.info("Add Network '166.10.0.0/16' with Grid master as Member assignment")
    network3 = {"network":"166.10.0.0/16","network_view":"default","members":[{"name":config.grid_fqdn,"_struct": "dhcpmember"}],"options":[{"name": "dhcp-lease-time","value": "74390400"}]}
    network3_response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(network3))
    network3_get = ib_NIOS.wapi_request('GET', object_type="network?network=166.10.0.0/16")
    network3_ref = json.loads(network3_get)[0]['_ref']


    logger.info("Add Range '166.10.0.1-166.10.5.255' in '166.10.0.0/16' with Grid master as Member assignment")
    range1 = {"network":"166.10.0.0/16","network_view":"default","member":{"_struct": "dhcpmember","name":config.grid_fqdn},"start_addr":"166.10.0.1","end_addr":"166.10.5.255"}
    range1_response = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(range1))

    logger.info("Add 10 fixed address in '166.10.0.0/16'")
    for i in range(7):
        fix_addr = {"network":"166.10.0.0/16","network_view":"default","ipv4addr":"166.10.20."+str(i),"mac":"00:00:00:00:10:"+str(i)}
        fix_response = ib_NIOS.wapi_request('POST', object_type="fixedaddress", fields=json.dumps(fix_addr))

    logger.info("Add 10 Reservation in '166.10.0.0/16'")
    for i in range(7):
        reserve = {"network":"166.10.0.0/16","network_view":"default","ipv4addr":"166.10.20.1"+str(i),"match_client":"RESERVED"}
        reserve_response = ib_NIOS.wapi_request('POST', object_type="fixedaddress", fields=json.dumps(reserve))

    logger.info("Modifiy shared Network '166.10.0.0/16', 10.0.0.0/8 ")
    shared_network_get = ib_NIOS.wapi_request('GET', object_type="sharednetwork?name=shared_ipv4")
    shared_network_ref = json.loads(shared_network_get)[0]['_ref']
    shared_network = {"networks":[{"_ref":str(network1_ref)},{"_ref":str(network3_ref)}]}
    shared_network_response = ib_NIOS.wapi_request('PUT', object_type=shared_network_ref, fields=json.dumps(shared_network))

    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    sleep(60)

    for i in range(5):
        fin=os.popen("sudo /import/tools/qa/tools/dras/dras  -n 200 -i"+config.grid_vip)
        logger.info(''.join(fin.readlines()))
        sleep(10)


    logger.info("Add Network '167.1.1.0/24' with Grid master as Member assignment")
    network4 = {"network":"167.1.1.0/24","network_view":"default","members":[{"name":config.grid_fqdn,"_struct": "dhcpmember"}],"options":[{"name": "dhcp-lease-time","value": "74390400"}]}
    network4_response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(network4))
    network4_get = ib_NIOS.wapi_request('GET', object_type="network?network=167.1.1.0/24")
    network4_ref = json.loads(network4_get)[0]['_ref']

    logger.info("Add Range '167.1.1.100-167.1.1.254' in '167.1.1.0/24' with Grid master as Member assignment")
    range3 = {"network":"167.1.1.0/24","network_view":"default","member":{"_struct": "dhcpmember","name":config.grid_fqdn},"start_addr":"167.1.1.100","end_addr":"167.1.1.254"}
    range3_response = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(range3))

    logger.info("Add 10 fixed address in '167.1.1.0/24'")
    for i in range(5):
        fix_addr = {"network":"167.1.1.0/24","network_view":"default","ipv4addr":"167.1.1."+str(i+1),"mac":"00:00:00:00:20:"+str(i)}
        fix_response = ib_NIOS.wapi_request('POST', object_type="fixedaddress", fields=json.dumps(fix_addr))

    logger.info("Add 10 Reservation in '167.1.1.0/24'")
    for i in range(5):
        reserve = {"network":"167.1.1.0/24","network_view":"default","ipv4addr":"167.1.1.2"+str(i),"match_client":"RESERVED"}
        reserve_response = ib_NIOS.wapi_request('POST', object_type="fixedaddress", fields=json.dumps(reserve))

    logger.info("Modifiy shared Network '167.1.1.0/24', 10.0.0.0/8 ")
    shared_network_get = ib_NIOS.wapi_request('GET', object_type="sharednetwork?name=shared_ipv4")
    shared_network_ref = json.loads(shared_network_get)[0]['_ref']
    shared_network = {"networks":[{"_ref":str(network1_ref)},{"_ref":str(network4_ref)}]}
    shared_network_response = ib_NIOS.wapi_request('PUT', object_type=shared_network_ref, fields=json.dumps(shared_network))

    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    sleep(60)


    for i in range(1):
        fin=os.popen("sudo /import/tools/qa/tools/dras/dras  -n 128 -i"+config.grid_vip)
        logger.info(''.join(fin.readlines()))
        sleep(10)

    logger.info("Removed shared Network")
    shared_network_get = ib_NIOS.wapi_request('GET', object_type="sharednetwork?name=shared_ipv4")
    shared_network_ref = json.loads(shared_network_get)[0]['_ref']
    shared_network_del_status = ib_NIOS.wapi_request('DELETE', object_type = shared_network_ref)

    logger.info("Remove 10.0.0.0/8 network")
    network_get = ib_NIOS.wapi_request('GET', object_type="network?network=10.0.0.0/8")
    network_ref = json.loads(network_get)[0]['_ref']
    network_del_status = ib_NIOS.wapi_request('DELETE', object_type = network_ref)

    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    sleep(60)


"""
 Copyright (c) Infoblox Inc., 2016

 Modle Name  : ib_preparation
 Description : This module is used for Prepration

 Author   : Vindya V K
 History  : 02/24/2021 (Created)
 Reviewer : Shekhar and Manoj
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

"""
IPAM REPORTS PREPARATION:
1. IPAMv4 Device Networks
2. IPAMv4 Network Usage Statistics
3. IPAMv4 Network Usage Trend
4. IPAMv4 Top Utilized networks
5. DHCPv4 Top Utilized networks
"""

def ipam_reports():
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
    
    #############################################################################################################
    for i in range(10):
       fin=os.popen("sudo /import/tools/qa/tools/dras/dras  -n 80 -i "+config.grid_vip+" -x l=165.0.0.0")
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
    
    #############################################################################################################
    for i in range(5):
       fin=os.popen("sudo /import/tools/qa/tools/dras/dras  -n 80 -i "+config.grid_vip+" -x l=165.0.0.0")
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
    
    #############################################################################################################

    for i in range(1):
       fin=os.popen("sudo /import/tools/qa/tools/dras/dras  -n 40 -i "+config.grid_vip+" -x l=165.0.0.0")
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
    
    print("Wait for some time for the reports to get generated...")
#    sleep(700)  # Sleep time not enough
#    sleep(300)


"""
DCVM REPORTS PREPARATION:
1. DNS Domain Query Trend
2. DNS Domains Queried by Client
3. DNS Query Rate by Member
4. DNS Top Clients by Query Type
5. DNS Top Clients Querying MX Records
"""

def DCVM_reports():
    logger.info("Add Auth Zone 'source.com' with Grid master as Member assignment")
    zone = {"fqdn": "source.com", "grid_primary": [{"name": config.grid_fqdn}]}
    zone_response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(zone))
    zone_get = ib_NIOS.wapi_request('GET', object_type="zone_auth")
    zone_ref = json.loads(zone_get)[0]['_ref']


    logger.info("Add A record 10.35.175.5 under source.com")
    A_record = {"name":"a_record.source.com","ipv4addr":"10.35.175.5"}
    A_record_response = ib_NIOS.wapi_request('POST', object_type="record:a", fields=json.dumps(A_record))
    A_record_get = ib_NIOS.wapi_request('GET', object_type="record:a")
    A_record_ref = json.loads(A_record_get)[0]['_ref']


    logger.info("Add AAAA record 1008:0000:0000:3564:2945:2947:0028:0001 under source.com")
    AAAA_record = {"name":"aaaa_record.source.com","ipv6addr":"1008:0000:0000:3564:2945:2947:0028:0001"}
    AAAA_record_response = ib_NIOS.wapi_request('POST', object_type="record:aaaa", fields=json.dumps(AAAA_record))
    AAAA_record_get = ib_NIOS.wapi_request('GET', object_type="record:aaaa")
    AAAA_record_ref = json.loads(AAAA_record_get)[0]['_ref']


    logger.info("Add MX record under source.com")
    MX_record = {"name":"mx_record.source.com","mail_exchanger":"source.com","preference":10}
    MX_record_response = ib_NIOS.wapi_request('POST', object_type="record:mx", fields=json.dumps(MX_record))
    MX_record_get = ib_NIOS.wapi_request('GET', object_type="record:mx")
    MX_record_ref = json.loads(MX_record_get)[0]['_ref']


    # Restart Services

    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    sleep(60)


    # Perform multiple dig queries with client_ip1

    cmd = os.system("for i in {1..5};do dig @"+config.grid_vip+" a_record.source.com in a -b 0.0.0.0;done")
    print(cmd)

    cmd = os.system("for i in {1..5};do dig @"+config.grid_vip+" aaaa_record.source.com in aaaa -b 0.0.0.0;done")
    print(cmd)

    cmd = os.system("for i in {1..5};do dig @"+config.grid_vip+" mx_record.source.com in mx -b 0.0.0.0;done")
    print(cmd)


    # Perform multiple dig queies with cliend_ip2
    cmd = os.system("for i in {1..5};do dig @"+config.grid_vip+" a_record.source.com in a -b ::;done")
    print(cmd)

    cmd = os.system("for i in {1..5};do dig @"+config.grid_vip+" aaaa_record.source.com in aaaa -b ::;done")
    print(cmd)

    cmd = os.system("for i in {1..5};do dig @"+config.grid_vip+" mx_record.source.com in mx -b ::;done")
    print(cmd)


    # wait for few minutes for the reports to get generated
    sleep(60)


"""
1. IPAM Prediction Dashboard Preparation
2. IP Address usage report Preparation (midnight)
3. DHCP LPS usage report Preparation (midnight)
"""

def ipam_Pred_and_IP_DHCP_usage_report():

    # Enable DHCP ipv6 interface on master
    
    
    print("\n============================================\n")
    print("Enable DHCP ipv6 interface on master")
    print("\n============================================\n")


    get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties?_return_fields=enable_dhcpv6_service", grid_vip=config.grid_vip)
#    print(get_ref)
    res = json.loads(get_ref)
    for i in res:
        if config.grid_fqdn in i['_ref']:
            data = {"enable_dhcpv6_service": True}
            response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
#            print(response)
            get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties?_return_fields=enable_dhcpv6_service", grid_vip=config.grid_vip)
            print(get_ref)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    print("Failure: Enable DHCP ipv6 interface on master")
                    assert False
                break
            else:
                print("Success: Enable DHCP ipv6 interface on master")
                assert True
                break
        else:
            continue
            
        sleep(30)

    

    # Add ipv4 Network

    logger.info("Add Network '10.0.0.0/8' with Grid master as Member assignment")
    network1 = {"network":"10.0.0.0/8","network_view":"default","members":[{"name":config.grid_fqdn,"_struct": "dhcpmember"}],"options":[{"name": "dhcp-lease-time","value": "74390400"}]}
    network1_response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(network1))
    network1_get = ib_NIOS.wapi_request('GET', object_type="network?network=10.0.0.0/8")
    network1_ref = json.loads(network1_get)[0]['_ref']
    print(network1_ref)


    # Add ipv6 Network

    logger.info("Add ipv6 Network '2001:550:40a:2500::/64' with Grid master as Member assignment")
    network2 = {"network": "2001:550:40a:2500::/64","network_view":"default","members":[{"name":config.grid_fqdn,"_struct": "dhcpmember"}],"options":[{"name": "dhcp-lease-time","value": "74390400"}]}
    network2_response = ib_NIOS.wapi_request('POST', object_type="ipv6network", fields=json.dumps(network2))
    network2_get = ib_NIOS.wapi_request('GET', object_type="ipv6network")
    network2_ref = json.loads(network2_get)[0]['_ref']
    print(network2_ref)



    # Add range in 10.0.0.0/8

    logger.info("Add Range '10.0.0.1 - 10.0.0.200' in '10.0.0.0/8' with Grid master as Member assignment")
    range = {"network":"10.0.0.0/8","network_view":"default","member":{"_struct": "dhcpmember","name":config.grid_fqdn},"start_addr":"10.0.0.1","end_addr":"10.0.0.200"}
    range_response = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(range))
    print(range_response)

    # Add range in 2001:550:40a:2500::/64

    logger.info("Add Range '2001:550:40a:2500::1111 - 2001:550:40a:2500::5555' in '2001:550:40a:2500::/64' with Grid master as Member assignment")
    range = {"network":"2001:550:40a:2500::/64","network_view":"default","member":{"_struct": "dhcpmember","name":config.grid_fqdn},"start_addr":"2001:550:40a:2500::1111","end_addr":"2001:550:40a:2500::5555"}
    range_response = ib_NIOS.wapi_request('POST', object_type="ipv6range", fields=json.dumps(range))
    print(range_response)


    # Restart Services

    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    sleep(60)



    # Requesting 10 Leases

    cmd1 = os.system("sudo /import/tools/qa/tools/dras/dras  -n 10 -i "+config.grid_vip+" -x l=165.0.0.0")
    print(cmd1)

    cmd2 = os.system("sudo /import/tools/qa/tools/dras6/dras6  -n 10 -i "+config.master_v6ip+" -A")
    print(cmd2)
    
    print("Wait for few minutes for the report to be generated...")
    #    sleep(300)
    print("----5 minutes remaining----")
    sleep(120)
    print("----3 minutes remaining----")
    sleep(120)
    print("----1 minutes remaining----")
    sleep(60)
    print("----0 minutes remaining----")
    
    # IP address usage and DHCP LPS usage reports update midnight


"""
INVENTORY REPORTS:
1. Network inventory
2. VLAN Inventory
3. VLAN Conflict reports preparation
"""
def display_msg(x):
    logger.info(x)
    print("\n"+x)

def Network_VLAN_inventory_reports():

    logger.info("Create Vlan View")
    data = {"name":"VLAN_view","start_vlan_id":100,"end_vlan_id":200}
    post_ref=ib_NIOS.wapi_request('POST',object_type ="vlanview", fields=json.dumps(data))
    print(post_ref)
    ref=json.loads(post_ref)
    res=ib_NIOS.wapi_request('GET' ,object_type=ref)
    res_json=json.loads(res)
    res_json.pop("_ref")
    assert res_json== data
    display_msg("=="*50)
    display_msg("TEST 1 COMPLETED")



    get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview")
    res = json.loads(get_ref)
    for i in res:
        if i["name"]=="VLAN_view":
            ref=i["_ref"]
    data = {"vlan_view":ref,"name": "VLAN_range1","start_vlan_id":151,"end_vlan_id":155,"vlan_name_prefix":"","comment":"test comment"}
    post_ref = ib_NIOS.wapi_request('POST',object_type="vlanrange",  fields=json.dumps(data))
    ref=json.loads(post_ref)
    res=ib_NIOS.wapi_request('GET' ,object_type=ref)
    print res
    res_json=json.loads(res)
    assert  data["name"]==res_json["name"] and data["start_vlan_id"]==res_json["start_vlan_id"]  and data["end_vlan_id"]==res_json["end_vlan_id"]
    display_msg("=="*50)
    display_msg("TEST 2 COMPLETED")



    get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview")
    res = json.loads(get_ref)
    for i in res:
        if i["name"]=="VLAN_view":
            ref=i["_ref"]
    data = {"parent":ref,"name": "VLAN_id1","id":159,"reserved":True,"contact":"879220","department":"ng","description":"descn"}
    post_ref = ib_NIOS.wapi_request('POST',object_type="vlan",  fields=json.dumps(data))
    ref=json.loads(post_ref)
    res=ib_NIOS.wapi_request('GET' ,object_type=ref)
    print res
    res_json=json.loads(res)
    assert  data["name"]==res_json["name"] and data["id"]==res_json["id"]
    display_msg("=="*50)
    display_msg("TEST 3 COMPLETED")



    get_ref = ib_NIOS.wapi_request('GET', object_type="vlanrange")
    res = json.loads(get_ref)
    for i in res:
        if i["name"]=="VLAN_range1":
            ref= i["_ref"]
    data = {"parent":ref,"name": "VLAN_id2","id":154,"reserved":True,"contact":"879220","department":"ng","description":"descn"}
    post_ref = ib_NIOS.wapi_request('POST',object_type="vlan",  fields=json.dumps(data))
    ref=json.loads(post_ref)
    res=ib_NIOS.wapi_request('GET' ,object_type=ref)
    print res
    res_json=json.loads(res)
    assert  data["name"]==res_json["name"] and data["id"]==res_json["id"]
    display_msg("=="*50)
    display_msg("TEST 4 COMPLETED")



    get_ref = ib_NIOS.wapi_request('GET', object_type="vlan")
    res = json.loads(get_ref)
    for i in res:
        if i["name"]=="VLAN_id1":
            ref= i["_ref"]
    print ref
    data =  {"network_view":"default","network":"61.0.0.0/24","vlans":[{"vlan":ref}] }
    response = ib_NIOS.wapi_request('POST',object_type="network",fields=json.dumps(data))
    read  = re.search(r'201',response)
    for read in  response:
        assert True
    display_msg("=="*50)
    display_msg("TEST 5 COMPLETED")



    get_ref = ib_NIOS.wapi_request('GET', object_type="vlan")
    res = json.loads(get_ref)
    for i in res:
        if i["name"]=="VLAN_id1":
            ref= i["_ref"]
    print ref
    data =  {"network_view":"default","network":"2620:10A:6000:2500::/64","vlans":[{"vlan":ref}] }
    response = ib_NIOS.wapi_request('POST',object_type="ipv6network",fields=json.dumps(data))
    read  = re.search(r'201',response)
    for read in  response:
        assert True
    display_msg("=="*50)
    display_msg("TEST 6 COMPLETED")


    get_ref = ib_NIOS.wapi_request('GET', object_type="vlan")
    res = json.loads(get_ref)
    for i in res:
        if i["name"]=="VLAN_id2":
            ref= i["_ref"]
    print ref
    data =  {"network_view":"default","network":"62.0.0.0/24","vlans":[{"vlan":ref}] }
    response = ib_NIOS.wapi_request('POST',object_type="network",fields=json.dumps(data))
    read  = re.search(r'201',response)
    for read in  response:
        assert True
    display_msg("=="*50)
    display_msg("TEST 7 COMPLETED")



    
"""
FLEX GRID REPORTS:
1. Managed DDI features enabled (midnight)
2. DNS Object Count Trend for FLEX Grid License (midnight)
3. DNS Effective Peak Usage Trend for Flex Grid License (midnight)
4. Flex Grid licencing features enabled
5. DNS QPS Usage report (sending 10000 dig queries from master ip)
"""

def flex_grid_reports():
    # Editing Grid DNS properties - enabling recurssion

    print("\n============================================\n")
    print("Stop DHCP Service on Flex member")
    print("\n============================================\n")


    get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties?_return_fields=enable_dhcp", grid_vip=config.grid_vip)
    res = json.loads(get_ref)
    for i in res:
        if config.grid_member1_fqdn in i['_ref']:
            data = {"enable_dhcp": False}
            response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties?_return_fields=enable_dhcp", grid_vip=config.grid_vip)
            print(get_ref)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    print("Failure: Stop DHCP Service on Member")
                    assert False
                break
            else:
                print("Success: Stop DHCP Service on Member")
                assert True
                break
        
        else:
            continue
        
        sleep(30)


    print("\n============================================\n")
    print("DNS Start Service on Flex member")
    print("\n============================================\n")


    get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns?_return_fields=enable_dns", grid_vip=config.grid_vip)
    res = json.loads(get_ref)
    for i in res:
        if config.grid_member1_fqdn in i['_ref']:
            data = {"enable_dns": True}
            response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns?_return_fields=enable_dns", grid_vip=config.grid_vip)
            print(get_ref)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    print("Failure: DNS Start Services on Member")
                    assert False
                break
            else:
                print("Success: DNS Start Services on Member")
                assert True
                break
        
        else:
            continue
        
        sleep(40)



    # Starting DNS Cache acceleration service on Member

    print("\n============================================\n")
    print("Start DCA Service on Flex member")
    print("\n============================================\n")


    get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns?_return_fields=enable_dns_cache_acceleration", grid_vip=config.grid_vip)
    res = json.loads(get_ref)
    for i in res:
        if config.grid_member1_fqdn in i['_ref']:
            data = {"enable_dns_cache_acceleration": True}
            response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns?_return_fields=enable_dns_cache_acceleration", grid_vip=config.grid_vip)
            print(get_ref)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    print("Failure: Start DCA service on Member")
                    assert False
                break
            else:
                print("Success: Start DCA service on Member")
                assert True
                break
        else:
            continue
            
        sleep(40)



    # Starting Threat protection service on Member
    print("\n============================================\n")
    print("Start TP Service on Flex member")
    print("\n============================================\n")


    get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection?_return_fields=enable_service", grid_vip=config.grid_vip)
    res = json.loads(get_ref)
    for i in res:
        if config.grid_member1_fqdn in i['_ref']:
            data = {"enable_service": True}
            response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection?_return_fields=enable_service", grid_vip=config.grid_vip)
            print(get_ref)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    print("Failure: Start TP service on Member")
                    assert False
                break
            else:
                print("Success: Start TP service on Member")
                assert True
                break
        else:
            continue
        
        sleep(40)


    # Restart Services

    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    sleep(30)


    logger.info("Enabling recursion")
    grid_get = ib_NIOS.wapi_request('GET',object_type="grid:dns")
    logger.info(grid_get)
    grid_ref = json.loads(grid_get)[0]['_ref']
    print(grid_ref)

    grid={"allow_recursive_query": True}
    grid_response = ib_NIOS.wapi_request('PUT',ref=grid_ref,fields=json.dumps(grid),grid_vip=config.grid_vip)
    print(grid_response)

    # Creating Auth Zone and Records


    logger.info("Add Auth Zone 'flex.com' with Grid master as Member assignment")
    zone = {"fqdn": "flex.com", "grid_primary": [{"name":config.grid_fqdn}]}
    zone_response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(zone))
    print(zone_response)
    zone_get = ib_NIOS.wapi_request('GET', object_type="zone_auth")
    zone_ref = json.loads(zone_get)[0]['_ref']


    logger.info("Add A record 10.35.175.5 under flex.com")
    A_record = {"name":"a_record.flex.com","ipv4addr":"10.35.175.5"}
    A_record_response = ib_NIOS.wapi_request('POST', object_type="record:a", fields=json.dumps(A_record))
    print(A_record_response)
    A_record_get = ib_NIOS.wapi_request('GET', object_type="record:a")
    A_record_ref = json.loads(A_record_get)[0]['_ref']



    logger.info("Add MX record under flex.com")
    mx_record={"name": "mx_record.flex.com","mail_exchanger": "flex.com","preference": 10,"view": "default"}
    mx_response = ib_NIOS.wapi_request('POST', object_type="record:mx",fields=json.dumps(mx_record))
    print(mx_response)
    mx_record_get = ib_NIOS.wapi_request('GET', object_type="record:mx")
    mx_record_ref = json.loads(mx_record_get)[0]['_ref']



    logger.info("Add HINFO record under flex.com")
    data={"name": "hinfo_record.flex.com","record_type": "hinfo","subfield_values": [{"field_type": "P","field_value": "\"INTEL\" \"INTEL\"","include_length": "NONE"}],"view": "default"}
    response = ib_NIOS.wapi_request('POST', object_type="record:unknown",fields=json.dumps(data))
    print(response)



    # Restart Services

    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    sleep(60)


    # Perform multiple dig queries with flex member
    cmd = os.system("for i in {1..10000};do dig @"+config.grid_member1_vip+" a_record.flex.com in a;done")
    print(cmd)

    cmd = os.system("for i in {1..10000};do dig @"+config.grid_member1_vip+" mx_record.flex.com in mx;done")
    print(cmd)

    cmd = os.system("for i in {1..10000};do dig @"+config.grid_member1_vip+" hinfo_record.flex.com in unknown;done")
    print(cmd)


    print("Preparstion for Flex Member reports completed!!!")
    # wait for few MIDNIGHT for the reports to get generated

    print("Dig query for DNS QPS Usage report...")
    cmd = os.system("for i in {1..10000};do dig @"+config.grid_vip+" a_record.flex.com in a;done")
    print(cmd)

#    sleep(3600)




"""
DISCOVERY MEMBER REPORTS:
1. Device Components
2. Device Interface Inventory
3. Device Inventory
4. IPAMv4 Device Networks
5. IP Address Inventory
"""



"""
Report: Discovery
Author: Manimaran
"""

def discovery():
    #Network View
    network_view = {"name":"discovery_view"}
    response = ib_NIOS.wapi_request('POST', object_type="networkview", fields=json.dumps(network_view))

    papi.enable_discovery_service(config.grid_vip,config.grid_member2_fqdn)
    sleep(180)
    # Add Network
    network_data = {"network":"10.40.16.0/24","network_view":"discovery_view"}
    response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(network_data))
    print(response)

    # Get Network for Enabling Discovery
    grid =  ib_NIOS.wapi_request('GET', object_type="network?network=10.40.16.0/24")
    ref = json.loads(grid)[0]['_ref']

    # Enable Grid Discovery Properties using following script
    rc=subprocess.call(['perl','ib_data/Discovery/discovery_preparation.pl',config.grid_vip,config.grid_member2_fqdn])

    # Enable Discovery in Network 10.40.16.0/24
    data = {"enable_discovery":True,"discovery_member":config.grid_member2_fqdn}
    enable_network_discovery = ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
    
    
    
    
def discovery_member_reports():

    # Starting discovery service on Member
        
    print("\n============================================\n")
    print("Start Discovery Service on Disovery member")
    print("\n============================================\n")


    get_ref = ib_NIOS.wapi_request('GET', object_type="discovery:memberproperties", grid_vip=config.grid_vip)
    res = json.loads(get_ref)
    for i in res:
        if "discovery.member" in i['_ref']:
            data = {"enable_service": True}
            response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            get_ref = ib_NIOS.wapi_request('GET', object_type="discovery:memberproperties?_return_fields=enable_service", grid_vip=config.grid_vip)
            print(get_ref)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    print("Failure: Start Discovery service on Member")
                    assert False
                    
            else:
                print("Success: Start Discovery service on Member")
                assert True
            break
        else:
            continue
        
        sleep(300)


    logger.info("Logging into discovery member as 'root'")
    child = pexpect.spawn("ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@"+config.grid_member2_vip,  maxread=4000)
    try:
    
        child.expect('.*#',timeout=100)
        print(child.sendline("cd /infoblox/netmri/bin"))

        child.expect('.*#',timeout=100)
        child.sendline("./discovery_network_device_inventory")

        child.expect('.*#',timeout=100)
        child.sendline("./discovery_switch_port_capacity")

        child.expect('.*#',timeout=100)
        child.sendline("./discovery_vpn_info")

        child.expect('.*#',timeout=100)
        child.sendline("./discovery_device_components")

        child.expect('.*#',timeout=100)
        child.sendline("exit")

        print("Wait for few minutes for the report to be generated...")
        #    sleep(300)

    except Exception as e:
        print(e)
        child.close()
        assert False


    finally:
        child.close()
        
        
        
def discovery_backup():

    logger.info("Logging into discovery member as 'root'")
    child = pexpect.spawn("ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@"+config.grid_member2_vip,  maxread=4000)
    try:
    
        child.expect('.*#',timeout=100)
        print(child.sendline("cd /infoblox/netmri/bin"))

        child.expect('.*#',timeout=100)
        child.sendline("./discovery_network_device_inventory")

        child.expect('.*#',timeout=100)
        child.sendline("./discovery_switch_port_capacity")

        child.expect('.*#',timeout=100)
        child.sendline("./discovery_vpn_info")

        child.expect('.*#',timeout=100)
        child.sendline("./discovery_device_components")

        child.expect('.*#',timeout=100)
        child.sendline("exit")

        print("Wait for few minutes for the report to be generated...")
        #    sleep(300)

    except Exception as e:
        print(e)
        child.close()
        assert False


    finally:
        child.close()
        
        

"""
VM Address history
"""

def VM_address_History():

    logger.info("Creating a super User for cloud_api_only Group")
    get_ref = ib_NIOS.wapi_request('GET',object_type="admingroup?name=cloud-api-only")
    logger.info(get_ref)
    ref1 = json.loads(get_ref)[0]['_ref']
    print(ref1)

    data={"superuser":True}
    response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
    print(response)


    
    user={"name":"User","password":"user@123","admin_groups":["cloud-api-only"]}
    get_ref = ib_NIOS.wapi_request('POST',object_type="adminuser", fields=json.dumps(user))
    if (get_ref[0] == 400):
        print("Duplicate object \'user\' of type \'adminuser\' already exists in the database")
        assert True
    else:
        print("User \'User\' has been created")
    

# Creating a Network using new credentials

    logger.info("Add Network '2.0.0.0/24' with Grid master as Member assignment")
    network1 = {"network":"2.0.0.0/24","network_view":"default","members":[{"name":config.grid_fqdn,"_struct": "dhcpmember"}],"options":[{"name": "dhcp-lease-time","value": "74390400"}]}
    network1_response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(network1), user="User", password="user@123")
    print("> ",network1_response)
    network1_get = ib_NIOS.wapi_request('GET', object_type="network?network=2.0.0.0/24", user="User", password="user@123")
    print(">> ",network1_get)
    network1_ref = json.loads(network1_get)[0]['_ref']
    print(network1_ref)


# Creating fixed address using new credentials

    logger.info("Add fixed address '2.0.0.9'")
    fixed_add = {"ipv4addr": "2.0.0.9", "network_view": "default","mac":"15:86:32:12:00:96","extattrs": { "Tenant ID":{"value": "395"} ,"CMP Type":{"value":"vm216ctest"} ,"VM ID":{"value":"361"},"Cloud API Owned":{"value":"True"}}}
    fixed_add_response = ib_NIOS.wapi_request('POST', object_type="fixedaddress", fields=json.dumps(fixed_add), user="User", password="user@123")
    fixed_add_get = ib_NIOS.wapi_request('GET', object_type="fixedaddress", user="User", password="user@123")
    fixed_add_ref = json.loads(fixed_add_get)[0]['_ref']
    print(fixed_add_ref)

#  Creating a zone using new credentials

    logger.info("Add zone 'zone.com'")
    zone = {"fqdn": "zone.com", "view": "default", "grid_primary": [{"name": config.grid_fqdn}]}
    zone_response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(zone), user="User", password="user@123")
    zone_get = ib_NIOS.wapi_request('GET', object_type="zone_auth", user="User", password="user@123")
    zone_ref = json.loads(zone_get)[0]['_ref']
    print(zone_ref)

# Creating A record using new credentials

    logger.info("Add A record 'record.zone.com'")
    record = {"view":"default","name":"record.zone.com","ipv4addr":"2.2.2.9","extattrs": { "Tenant ID":{"value": "375"} ,"CMP Type":{"value":"vm218ctest"} ,"VM ID":{"value":"567"},"Cloud API Owned":{"value":"True"}}}
    record_response = ib_NIOS.wapi_request('POST', object_type="record:a", fields=json.dumps(record), user="User", password="user@123")
    record_get = ib_NIOS.wapi_request('GET', object_type="record:a", user="User", password="user@123")
    record_ref = json.loads(record_get)[0]['_ref']
    print(record_ref)

    
    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    sleep(60)

    print("Wait for few minutes for the report to be generated...")
#    sleep(300)


"""
FireEye Alerts Reports

"""

def fireEye_alerts_report():

    # Creating DNS response policy zone

    logger.info("Add zone_rp 'test.com'")
    rpz = {"fqdn": "test.com","grid_primary": [{"name": config.grid_fqdn}], "rpz_type": "FIREEYE","fireeye_rule_mapping": {"apt_override": "NOOVERRIDE"}}
    rpz_response = ib_NIOS.wapi_request('POST', object_type="zone_rp", fields=json.dumps(rpz),grid_vip=config.grid_vip)
    print(">>>",rpz_response)
    rpz_get = ib_NIOS.wapi_request('GET', object_type="zone_rp")
    print(">>",rpz_get)
    rpz_ref = json.loads(rpz_get)[0]['_ref']
    print(rpz_ref)

    # Restart Services

    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    sleep(30)



    logger.info("Making fire-eye Group as Superuser")
    get_ref = ib_NIOS.wapi_request('GET',object_type="admingroup?name=fireeye-group")
    logger.info(get_ref)
    #ref1 = json.loads(get_ref)[4]['_ref']
    ref1 = json.loads(get_ref)[0]['_ref']
    print(ref1)

    data={"superuser":True}
    response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
    print(response)



    user={"name":"user","password":"user@123","admin_groups":["fireeye-group"]}
    get_ref = ib_NIOS.wapi_request('POST',object_type="adminuser", fields=json.dumps(user))
    if (get_ref[0] == 400):
        print("Duplicate object \'user\' of type \'adminuser\' already exists in the database")
        assert True
    else:
        print("User \'user\' has been created")


    # Editing Grid DNS properties - adding forwarder and enabling recurssion

    logger.info("Adding Forwarder and enabling recursion")
    grid_get = ib_NIOS.wapi_request('GET',object_type="grid:dns")
    logger.info(get_ref)
    grid_ref = json.loads(grid_get)[0]['_ref']
    print(grid_ref)

    grid={"allow_recursive_query": True,"forwarders": ["10.39.16.160"]}
    grid_response = ib_NIOS.wapi_request('PUT',ref=grid_ref,fields=json.dumps(grid),grid_vip=config.grid_vip)
    print(grid_response)


    # Restart Services

    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    sleep(30)

    # Execute ./run_alert_tests.sh

    cmd = os.system("chmod 777 run_alert_tests.sh")
    cmd = os.system("./run_alert_tests.sh")
    print(cmd)



    logger.info ("Wait 5 minutes for reports to get update")
    sleep(150)


"""
Device Advisor Report
"""

def device_advisor():

    logger.info("Logging into discovery member as 'admin'")
    child = pexpect.spawn("ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@"+config.grid_member2_vip,  maxread=4000)
    try:
    
        child.expect("password:")
        child.sendline("infoblox")
        child.expect("Infoblox >")

        child.sendline('set static_route add 18.0.0.0/8 10.36.0.1')
        
        child.expect("Infoblox >",timeout=100)
        child.sendline("exit")
        
    except Exception as e:
        print(e)
        child.close()
        assert False


    finally:
        child.close()
        

    logger.info("Enabling advisor Application")
    get_ref = ib_NIOS.wapi_request('GET',object_type="discovery:gridproperties?_return_fields=enable_advisor")
    logger.info(get_ref)
    ref1 = json.loads(get_ref)[0]['_ref']
    print(ref1)

    enable_advisor = {"enable_advisor":True}
    advisor = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(enable_advisor),grid_vip=config.grid_vip)
    print(advisor)
    
    get_ref = ib_NIOS.wapi_request('GET',object_type="discovery:gridproperties?_return_fields=enable_advisor")
    logger.info(get_ref)


    # Advisor setting : address, auth_token, execution_hour, execution_interval, min_severity,  network_interface_type, port

    logger.info("Updating Advisor setting")
    get_ref2 = ib_NIOS.wapi_request('GET',object_type="discovery:gridproperties?_return_fields=advisor_settings")
    logger.info(get_ref2)
    ref2 = json.loads(get_ref2)[0]['_ref']
    print(ref2)

    advisor_settings = {"advisor_settings":{"address": "18.204.145.112", "auth_token": "blBheHQxSlN3NXdtZFIhOlNKcGtlNlNDVHkyJSE=", "auth_type": "TOKEN", "execution_hour": 9, "execution_interval": 86400, "min_severity": "0.0", "network_interface_type": "MGMT", "port": 8888}}
    settings = ib_NIOS.wapi_request('PUT',ref=ref2,fields=json.dumps(advisor_settings),grid_vip=config.grid_vip)
    print(settings)


    logger.info("Logging into discovery member as 'root'")
    child = pexpect.spawn("ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@"+config.grid_member2_vip,  maxread=4000)
    try:
    
        child.expect('.*#',timeout=100)
        print(child.sendline("cd /infoblox/netmri/bin/"))

        child.expect('.*#',timeout=100)
        child.sendline("python device_advisor_reporter")

        child.expect('.*#',timeout=100)
        child.sendline("exit")

        print("Wait for 5 minutes for the report to be generated...")
        
        print("----5 minutes remaining----")
        sleep(120)
        print("----3 minutes remaining----")
        sleep(120)
        print("----1 minutes remaining----")
        sleep(60)
        print("----0 minutes remaining----")
        
    except Exception as e:
        print(e)
        child.close()
        assert False


    finally:
        child.close()
        


"""
Restart Services on Grid
"""
def restart_services_on_grid():

    # Restart Services

    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    sleep(80)


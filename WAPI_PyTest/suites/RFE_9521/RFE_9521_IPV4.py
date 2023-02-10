import re
import config
import pytest
import unittest
import logging
import subprocess
import os
import json
import config
import ib_utils.ib_NIOS as ib_NIOS
from time import sleep
import commands
import json, ast
import requests
import time
import pexpect
import getpass
import sys

logging.basicConfig(filename='ref_IPV4.log', filemode='w', level=logging.DEBUG)

def create_group(name,roles):
    logging.info("Creating group")
    group_info={"name":name,"access_method": ["GUI","API"],"roles": [roles]}
    group_ref=ib_NIOS.wapi_request('POST',object_type='admingroup',field=json.dumps(group_info))
    logging.info(group_ref)
    return group_ref

def create_user(name,password,admin_group):
    logging.info("Creating user")
    user_info={"name": name,"password": password,"admin_groups": admin_group}
    user_ref=ib_NIOS.wapi_request('POST',object_type='adminuser',field=json.dumps(user_info))
    logging.info(user_ref)
    return user_ref


def create_network(network,network_view):
    logging.info("Creating network")
    nw_info={"network": network,"network_view": network_view}
    nw_ref=ib_NIOS.wapi_request('POST',object_type='network',fields=json.dumps(nw_info))
    logging.info(nw_ref)
    return nw_ref

def create_network_container(network,network_view):
    logging.info("Creating network")
    nw_info={"network": network,"network_view": network_view}
    nw_ref=ib_NIOS.wapi_request('POST',object_type='networkcontainer',fields=json.dumps(nw_info))
    logging.info(nw_ref)
    return nw_ref



def create_host(name,ipv4addr):
    logging.info("Creating host")
    host_info={"name": name,"network_view": "default","configure_for_dns": False,"ipv4addrs": [{"configure_for_dhcp": False,"ipv4addr": ipv4addr}]}
    host_ref=ib_NIOS.wapi_request('POST',object_type='record:host',fields=json.dumps(host_info))
    logging.info(host_ref)
    return host_ref


def permission(group,permission,object_ref):
    logging.info("Assigning permission")
    print "Assigning permissions"
    perm_info={"group": group,"permission": permission,"object": object_ref}
    perm_ref=ib_NIOS.wapi_request('POST',object_type='permission',fields=json.dumps(perm_info))
    logging.info(perm_ref)
    return perm_ref



print "----------------------Starting initial grid configuration----------------------"
print "\n\n"

logging.info ("Creating group1")
group1={"name": "group1","access_method": ["GUI","API"],"roles": []}
group1_ref=ib_NIOS.wapi_request('POST',object_type='admingroup',fields=json.dumps(group1))
logging.info(group1_ref)
logging.info ("Creating user1")
user1={"name": "user1","password": "infoblox","admin_groups": ["group1"]}
user1_ref=ib_NIOS.wapi_request('POST',object_type='adminuser',fields=json.dumps(user1))
logging.info (user1_ref)
print "###Group1 and User1 creation successfull###"
time.sleep(3)

logging.info ("Creating group2")
group2={"name": "group2","access_method": ["GUI","API"],"roles": ["DHCP Admin"]}
group2_ref=ib_NIOS.wapi_request('POST',object_type='admingroup',fields=json.dumps(group2))
logging.info (group2_ref)
logging.info ("Creating user2")
user2={"name": "user2","password": "infoblox","admin_groups": ["group2"]}
user2_ref=ib_NIOS.wapi_request('POST',object_type='adminuser',fields=json.dumps(user2))
logging.info (user2_ref)
print "###Group2 and User2 creation successfull###"
time.sleep(3)

logging.info ("Creating group3")
group3={"name": "group3","access_method": ["GUI","API"],"roles": ["DNS Admin"]}
group3_ref=ib_NIOS.wapi_request('POST',object_type='admingroup',fields=json.dumps(group3))
logging.info (group3_ref)
logging.info ("Creating user3")
user3={"name": "user3","password": "infoblox","admin_groups": ["group3"]}
user3_ref=ib_NIOS.wapi_request('POST',object_type='adminuser',fields=json.dumps(user3))
logging.info (user3_ref)
print "###group3 and user3 creation successfull###"
time.sleep(3)


logging.info("Creating network 90.0.0.0/8")
network_90_8_ref=create_network("90.0.0.0/8","default")
print "90.0.0.0/8 created"
time.sleep(3)

logging.info("Creating network 10.20.0.0/18")
network_10_18_ref=create_network("10.20.0.0/18","default")
print "10.20.0.0/18 created"
time.sleep(3)

logging.info("Creating network 10.20.0.0/16")
network_10_16_ref=create_network_container("10.20.0.0/16","default")
print "10.20.0.0/16 created"
print network_10_16_ref
time.sleep(3)


logging.info("Creating network 10.0.0.0/8")
network_10_8_ref=create_network_container("10.0.0.0/8","default")
print "10.0.0.0/8 created"
time.sleep(3)


logging.info("Creating range 10.20.0.1-10.20.0.100")
range_info={"network": "10.20.0.0/18","network_view": "default","start_addr": "10.20.0.1","end_addr": "10.20.0.100"}
range_ref=ib_NIOS.wapi_request('POST',object_type='range',fields=json.dumps(range_info))
logging.info(range_ref)
print "Range 10.20.0.1-10.20.0.100 created"
time.sleep(3)

logging.info("Creating host1")
host1_ref=create_host("host1","10.20.0.1")
print "Host1 created"
time.sleep(3)

logging.info("Creating host2")
host2_ref=create_host("host2","10.20.0.150")
print "Host2 created"
time.sleep(3)

logging.info ("Creating group4")
group4={"name": "group4","access_method": ["GUI","API"],"roles": []}
group4_ref=ib_NIOS.wapi_request('POST',object_type='admingroup',fields=json.dumps(group4))
logging.info (group4_ref)
logging.info ("Creating user4")
user4={"name": "user4","password": "infoblox","admin_groups": ["group4"]}
user4_ref=ib_NIOS.wapi_request('POST',object_type='adminuser',fields=json.dumps(user4))
logging.info (user4_ref)
print "###group4 and user4 creation successfull###"
time.sleep(3)


logging.info("Providing range object permission to group4")
perm_range=permission("group4","WRITE",range_ref)
time.sleep(3)

logging.info("Write permission for network container 10.0.0.0/8")
perm_8=permission("group4","WRITE",network_10_8_ref)
time.sleep(3)

logging.info("Write permission for network container 10.20.0.0/16")
perm_16=permission("group4","WRITE",network_10_16_ref)
time.sleep(3)

logging.info("Write permission for network container 10.20.0.0/18")
perm_18=permission("group4","WRITE",network_10_18_ref)
time.sleep(3)

logging.info("Global write permission for zone")
perm_zone_info={"group": "group4","permission": "WRITE","resource_type": "ZONE"}
perm_zone_ref=ib_NIOS.wapi_request('POST',object_type='permission',fields=json.dumps(perm_zone_info))
logging.info(perm_zone_ref)
time.sleep(3)




class Network(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test001_query_host_user1(self):
        logging.info("Starting testcase 1")
        logging.info("GET host object with user1")
        t1_ref=ib_NIOS.wapi_request('GET',object_type='record:host',user='user1',password='infoblox')
        logging.info("Logging recieved reference")
        logging.info(t1_ref)
        assert t1_ref=='[]'
        logging.info("Testcase 1 successfull")
        time.sleep(5)


    @pytest.mark.run(order=2)
    def test002_query_host_user2(self):
        logging.info("Starting testcase 2")
        logging.info("GET host object with user2")
        t2_ref=ib_NIOS.wapi_request('GET',object_type='record:host',user='user2',password='infoblox')
        logging.info("Logging recieved reference")
        logging.info(t2_ref)
        t2_json=json.loads(t2_ref)
        logging.info(t2_json)
        assert t2_json[0]['name']=="host1"
        assert t2_json[0]['ipv4addrs'][0]['host']=='host1'
        assert t2_json[0]['ipv4addrs'][0]['ipv4addr']=='10.20.0.1'
        assert t2_json[1]['name']=="host2"
        assert t2_json[1]['ipv4addrs'][0]['host']=='host2'
        assert t2_json[1]['ipv4addrs'][0]['ipv4addr']=='10.20.0.150'
        time.sleep(5)


    @pytest.mark.run(order=3)
    def test003_query_host_user3(self):
        logging.info("Starting testcase 3")
        logging.info("GET host object with user3")
        t3_ref=ib_NIOS.wapi_request('GET',object_type='record:host',user='user3',password='infoblox')
        logging.info("Logging recieved reference")
        logging.info(t3_ref)
        assert t3_ref=='[]'
        logging.info("Testcase 3 successfull")
        time.sleep(5)

    @pytest.mark.run(order=4)
    def test004_query_host_user4(self):
        logging.info("Starting testcase 4")
        logging.info("GET host object with user4")
        t4_ref=ib_NIOS.wapi_request('GET',object_type='record:host',user='user4',password='infoblox')
        logging.info("Logging recieved reference")
        logging.info(t4_ref)
        t4_json=json.loads(t4_ref)
        logging.info(t4_json)
        assert t4_json[0]['name']=="host1"
        assert t4_json[0]['ipv4addrs'][0]['host']=='host1'
        assert t4_json[0]['ipv4addrs'][0]['ipv4addr']=='10.20.0.1'
        assert t4_json[1]['name']=="host2"
        assert t4_json[1]['ipv4addrs'][0]['host']=='host2'
        assert t4_json[1]['ipv4addrs'][0]['ipv4addr']=='10.20.0.150'
        logging.info("Testcase 4 execution succesfull")
        time.sleep(5)


    @pytest.mark.run(order=5)
    def test005_permission_change_1(self):
        logging.info("Starting testcase 5")
        logging.info("Logging as admin and changing the permissions of 10.20.0.0/16,10.20.0.0/18, 10.20.0.1-100 to DENY")
        data={"permission":"DENY"}
        logging.info(perm_16)
        perm_change_1=ib_NIOS.wapi_request('PUT', ref=perm_16.strip('\"'), fields=json.dumps(data), user='admin', password='infoblox')
        perm_change_2=ib_NIOS.wapi_request('PUT', ref=perm_18.strip('\"'), fields=json.dumps(data), user='admin', password='infoblox')
        perm_change_3=ib_NIOS.wapi_request('PUT', ref=perm_range.strip('\"'), fields=json.dumps(data), user='admin', password='infoblox')
        logging.info("Permissions changed successfully")
        logging.info("Querying record host with user4")
        t5_ref=ib_NIOS.wapi_request('GET',object_type='record:host',user='user4',password='infoblox')
        logging.info(t5_ref)
        assert t5_ref=='[]'
        logging.info("Testcase 5 execution successfull")
        time.sleep(5)


    @pytest.mark.run(order=6)
    def test006_permission_change_2(self):
        logging.info("Starting testcase 6")
        logging.info("Logging as admin and changing the permission of 10.20.0.0/16 to Read only")
        data={"permission":"READ"}
        perm_change_1=ib_NIOS.wapi_request('PUT', ref=perm_16.strip('\"'), fields=json.dumps(data), user='admin', password='infoblox')
        logging.info("Permissions changed successfully")
        logging.info("Querying host record with user4")
        t6_ref=ib_NIOS.wapi_request('GET',object_type='record:host',user='user4',password='infoblox')
        logging.info(t6_ref)
        assert t6_ref=='[]'
        logging.info("Testcase 6 execution succesfull")
        time.sleep(5)


    @pytest.mark.run(order=7)
    def test007_permission_change_3(self):
        logging.info("Starting testcase 7")
        logging.info("Logging as admin and changing the permission of 10.20.0.0/18 to Read only")
        data={"permission":"READ"}
        perm_change_1=ib_NIOS.wapi_request('PUT', ref=perm_18.strip('\"'), fields=json.dumps(data), user='admin', password='infoblox')
        logging.info("Permissions changed successfully")
        logging.info("Querying host record with user4")
        t7_ref=ib_NIOS.wapi_request('GET',object_type='record:host',user='user4',password='infoblox')
        logging.info(t7_ref)
        t7_json=json.loads(t7_ref)
        logging.info(t7_json)
        assert t7_json[0]['name']=="host1"
        assert t7_json[0]['ipv4addrs'][0]['host']=='host1'
        assert t7_json[0]['ipv4addrs'][0]['ipv4addr']=='10.20.0.1'
        assert t7_json[1]['name']=="host2"
        assert t7_json[1]['ipv4addrs'][0]['host']=='host2'
        assert t7_json[1]['ipv4addrs'][0]['ipv4addr']=='10.20.0.150'
        logging.info("Testcase 7 execution succesfull")
        time.sleep(5)


    @pytest.mark.run(order=8)
    def test008_permission_change_4(self):
        logging.info("Starting testcase 8")
        logging.info("Logging as admin and changing the permission of 10.20.0.1-100 to Read only")
        data={"permission":"READ"}
        perm_change_1=ib_NIOS.wapi_request('PUT', ref=perm_range.strip('\"'), fields=json.dumps(data), user='admin', password='infoblox')
        logging.info("Permissions changed successfully")
        logging.info("Querying host record with user4")
        t8_ref=ib_NIOS.wapi_request('GET',object_type='record:host',user='user4',password='infoblox')
        logging.info(t8_ref)
        t8_json=json.loads(t8_ref)
        logging.info(t8_json)
        assert t8_json[0]['name']=="host1"
        assert t8_json[0]['ipv4addrs'][0]['host']=='host1'
        assert t8_json[0]['ipv4addrs'][0]['ipv4addr']=='10.20.0.1'
        assert t8_json[1]['name']=="host2"
        assert t8_json[1]['ipv4addrs'][0]['host']=='host2'
        assert t8_json[1]['ipv4addrs'][0]['ipv4addr']=='10.20.0.150'
        logging.info("Testcase 8 execution succesfull")
        time.sleep(5)


    @pytest.mark.run(order=9)
    def test009_permission_change_5(self):
        logging.info("Starting testcase 9")
        logging.info("Logging as admin and changing the permission of 10.0.0.0/8 to Read only")
        data={"permission":"READ"}
        perm_change_1=ib_NIOS.wapi_request('PUT', ref=perm_8.strip('\"'), fields=json.dumps(data), user='admin', password='infoblox')
        logging.info("Permissions changed successfully")
        logging.info("Querying host record with user4")
        t9_ref=ib_NIOS.wapi_request('GET',object_type='record:host',user='user4',password='infoblox')
        logging.info(t9_ref)
        t9_json=json.loads(t9_ref)
        logging.info(t9_json)
        assert t9_json[0]['name']=="host1"
        assert t9_json[0]['ipv4addrs'][0]['host']=='host1'
        assert t9_json[0]['ipv4addrs'][0]['ipv4addr']=='10.20.0.1'
        assert t9_json[1]['name']=="host2"
        assert t9_json[1]['ipv4addrs'][0]['host']=='host2'
        assert t9_json[1]['ipv4addrs'][0]['ipv4addr']=='10.20.0.150'
        logging.info("Testcase 9 execution succesfull")
        time.sleep(5)

    @pytest.mark.run(order=10)
    def test010_permission_change_6(self):
        logging.info("Starting testcase 10")
        logging.info("Logging as admin and changing the permission of 10.20.0.1-100 to Write")
        data={"permission":"WRITE"}
        perm_change_1=ib_NIOS.wapi_request('PUT', ref=perm_range.strip('\"'), fields=json.dumps(data), user='admin', password='infoblox')
        logging.info("Permissions changed successfully")
        logging.info("Querying host record with user4")
        t10_ref=ib_NIOS.wapi_request('GET',object_type='record:host',user='user4',password='infoblox')
        logging.info(t10_ref)
        t10_json=json.loads(t10_ref)
        logging.info(t10_json)
        assert t10_json[0]['name']=="host1"
        assert t10_json[0]['ipv4addrs'][0]['host']=='host1'
        assert t10_json[0]['ipv4addrs'][0]['ipv4addr']=='10.20.0.1'
        assert t10_json[1]['name']=="host2"
        assert t10_json[1]['ipv4addrs'][0]['host']=='host2'
        assert t10_json[1]['ipv4addrs'][0]['ipv4addr']=='10.20.0.150'
        logging.info("Testcase 10 execution succesfull")
        time.sleep(5)


    @pytest.mark.run(order=11)
    def test011_permission_change_7(self):
        logging.info("Starting testcase 11")
        logging.info("Logging as admin and changing the permission of 10.20.0.1-100 to Read only")
        data={"permission":"READ"}
        perm_change_1=ib_NIOS.wapi_request('PUT', ref=perm_range.strip('\"'), fields=json.dumps(data), user='admin', password='infoblox')
        logging.info("Permissions changed successfully")
        logging.info("Querying host record with user4")
        t11_ref=ib_NIOS.wapi_request('GET',object_type='record:host',user='user4',password='infoblox')
        logging.info(t11_ref)
        t11_json=json.loads(t11_ref)
        logging.info(t11_json)
        assert t11_json[0]['name']=="host1"
        assert t11_json[0]['ipv4addrs'][0]['host']=='host1'
        assert t11_json[0]['ipv4addrs'][0]['ipv4addr']=='10.20.0.1'
        assert t11_json[1]['name']=="host2"
        assert t11_json[1]['ipv4addrs'][0]['host']=='host2'
        assert t11_json[1]['ipv4addrs'][0]['ipv4addr']=='10.20.0.150'
        logging.info("Testcase 11 execution succesfull")
        time.sleep(5)


    @pytest.mark.run(order=12)
    def test012_permission_change_8(self):
        logging.info("Starting testcase 12")
        logging.info("Logging as admin and changing the permission of 10.20.0.0/18 to RW and 10.20.0.1-100 to Deny")
        data1={"permission":"WRITE"}
        data2={"permission":"DENY"}
        perm_change_1=ib_NIOS.wapi_request('PUT', ref=perm_18.strip('\"'), fields=json.dumps(data1), user='admin', password='infoblox')
        perm_change_2=ib_NIOS.wapi_request('PUT', ref=perm_range.strip('\"'), fields=json.dumps(data2), user='admin', password='infoblox')
        logging.info("Permissions changed successfully")
        logging.info("Querying host record with user4")
        t12_ref=ib_NIOS.wapi_request('GET',object_type='record:host',user='user4',password='infoblox')
        logging.info(t12_ref)
        t12_json=json.loads(t12_ref)
        logging.info(t12_json)
        assert t12_json[0]['name']=="host1"
        assert t12_json[0]['ipv4addrs'][0]['host']=='host1'
        assert t12_json[0]['ipv4addrs'][0]['ipv4addr']=='10.20.0.1'
        assert t12_json[1]['name']=="host2"
        assert t12_json[1]['ipv4addrs'][0]['host']=='host2'
        assert t12_json[1]['ipv4addrs'][0]['ipv4addr']=='10.20.0.150'
        logging.info("Testcase 12 execution succesfull")
        time.sleep(5)


    @pytest.mark.run(order=13)
    def test013_permission_change_9(self):
        logging.info("Starting testcase 13")
        logging.info("Logging as admin and changing the permission of 10.20.0.0/18 to deny and 10.20.0.1-100 to Denyand 10.20.0.0/16 to RW")
        data1={"permission":"WRITE"}
        data2={"permission":"DENY"}
        perm_change_1=ib_NIOS.wapi_request('PUT', ref=perm_18.strip('\"'), fields=json.dumps(data2), user='admin', password='infoblox')
        perm_change_2=ib_NIOS.wapi_request('PUT', ref=perm_range.strip('\"'), fields=json.dumps(data2), user='admin', password='infoblox')
        perm_change_3=ib_NIOS.wapi_request('PUT', ref=perm_16.strip('\"'), fields=json.dumps(data1), user='admin', password='infoblox')
        logging.info("Permissions changed successfully")
        logging.info("Querying host record with user4")
        t13_ref=ib_NIOS.wapi_request('GET',object_type='record:host',user='user4',password='infoblox')
        assert t13_ref=='[]'
        logging.info("Testcase 13 execution successfull")
        time.sleep(5)


    @pytest.mark.run(order=14)
    def test014_permission_change_10(self):
        logging.info("Starting testcase 14")
        logging.info("Logging as admin and changing the permission of 10.20.0.0/18 to deny and 10.20.0.1-100 to Deny 10.20.0.0/16 to DEny and 10.0.0.0/8 to RW")
        data1={"permission":"WRITE"}
        data2={"permission":"DENY"}
        perm_change_1=ib_NIOS.wapi_request('PUT', ref=perm_18.strip('\"'), fields=json.dumps(data2), user='admin', password='infoblox')
        perm_change_2=ib_NIOS.wapi_request('PUT', ref=perm_range.strip('\"'), fields=json.dumps(data2), user='admin', password='infoblox')
        perm_change_3=ib_NIOS.wapi_request('PUT', ref=perm_16.strip('\"'), fields=json.dumps(data2), user='admin', password='infoblox')
        perm_change_4=ib_NIOS.wapi_request('PUT', ref=perm_8.strip('\"'), fields=json.dumps(data1), user='admin', password='infoblox')
        logging.info("Permissions changed successfully")
        logging.info("Querying host record with user4")
        t14_ref=ib_NIOS.wapi_request('GET',object_type='record:host',user='user4',password='infoblox')
        assert t14_ref=='[]'
        logging.info("Testcase 14 execution successfull")
        time.sleep(5)


    @pytest.mark.run(order=15)
    def test015_nios_60674(self):
        logging.info("Starting validation of NIOS-60674")
        logging.info("Adding global permission for ALL HOSTS with RO permission")
        logging.info("Global read permission for hosts")
        perm_host_info={"group": "group4","permission": "DENY","resource_type": "HOST"}
        perm_host_ref=ib_NIOS.wapi_request('POST',object_type='permission',fields=json.dumps(perm_host_info))
        logging.info(perm_host_ref)
        time.sleep(3)
        logging.info("Scenario 1 permission DENY for network and host")
        comment={"comment": "Testcomment"}
        ea={"extattrs": { "Site": { "value": "bdc"}}}
        try:
            put_comment=ib_NIOS.wapi_request('PUT',ref=host1_ref.strip('\"'), fields=json.dumps(comment),user='user4', password='infobox')
        except Exception as error:
            logging.info("Unable to add comment")
        else:
            logging.info("Comment added succesfully")
            raise Exception("Comment addition was succesfull even though it doesnt have permission")

        try:
            put_ea=ib_NIOS.wapi_request('PUT',ref=host1_ref.strip('\"'), fields=json.dumps(ea),user='user4', password='infobox')
        except Exception as error:
            logging.info("Unable to add EA")
        else:
            logging.info("EA added succesfully")
            raise Exception("EA addition was succesfull even though it doesnt have permission")

        
        logging.info("Scenario 2 permission RO for network and host")
        data1={"permission":"READ"}
        data2={"permission":"WRITE"}
        perm_change_1=ib_NIOS.wapi_request('PUT', ref=perm_18.strip('\"'), fields=json.dumps(data1), user='admin', password='infoblox')
        perm_change_2=ib_NIOS.wapi_request('PUT', ref=perm_host_ref.strip('\"'), fields=json.dumps(data1), user='admin', password='infoblox')

        try:
            put_comment=ib_NIOS.wapi_request('PUT',ref=host1_ref.strip('\"'), fields=json.dumps(comment),user='user4', password='infobox')
        except Exception as error:
            logging.info("Unable to add comment")
        else:
            logging.info("Comment added succesfully")
            raise Exception("Comment addition was succesfull even though it doesnt have permission")

        try:
            put_ea=ib_NIOS.wapi_request('PUT',ref=host1_ref.strip('\"'), fields=json.dumps(ea),user='user4', password='infobox')
        except Exception as error:
            logging.info("Unable to add EA")
        else:
            logging.info("EA added succesfully")
            raise Exception("EA addition was succesfull even though it doesnt have permission")


        logging.info("Scenario 3 permission RW for network and host")
        perm_change_1=ib_NIOS.wapi_request('PUT', ref=perm_18.strip('\"'), fields=json.dumps(data2), user='admin', password='infoblox')
        perm_change_2=ib_NIOS.wapi_request('PUT', ref=perm_host_ref.strip('\"'), fields=json.dumps(data2), user='admin', password='infoblox')

        try:
            put_comment=ib_NIOS.wapi_request('PUT',ref=host1_ref.strip('\"'), fields=json.dumps(comment),user='user4', password='infoblox')
        except Exception as error:
            logging.info("Unable to add comment")
            raise Exception("Comment addition was unsuccesfull even though it has permission")
        else:
            logging.info("Comment added succesfully")

        try:
            put_ea=ib_NIOS.wapi_request('PUT',ref=host1_ref.strip('\"'), fields=json.dumps(ea),user='user4', password='infoblox')
        except Exception as error:
            logging.info("Unable to add EA")
            raise Exception("EA addition was unsuccesfull even though it has permission")
        else:
            logging.info("EA added succesfully")

        
        time.sleep(5)

























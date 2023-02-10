#!/usr/bin/env python
__author__ = "Chetan Kumar PG"
__email__  = "cpg@infoblox.com"

import re
import config
import pytest
import unittest
import logging
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS

### Global variables ###
container1_perm = None
container2_perm = None
network_perm = None
range_perm = None

def display_msg(x):
    logging.info(x)
    print(x)

class RFE_9521(unittest.TestCase):
    
    @pytest.mark.run(order=1)
    def test_001_set_up(self):
        global container1_perm, container2_perm, network_perm, range_perm
        display_msg("=="*94)
        display_msg("Create user groups and add IPV4/IPV6 objects as admin user")
        
        display_msg("Create group5")
        group5_data = {"name": "group5","access_method": ["GUI","API"], "roles":[]}
        response = ib_NIOS.wapi_request('POST',object_type="admingroup",fields=json.dumps(group5_data))
        display_msg(response)

        display_msg("Create user5 in group5")
        user5_data = {"name": "user5","password": "infoblox","admin_groups": ["group5"]}
        response = ib_NIOS.wapi_request('POST',object_type="adminuser",fields=json.dumps(user5_data))
        display_msg(response)

        display_msg("Create group6")
        group6_data = {"name": "group6","access_method": ["GUI","API"],"roles": ["DHCP Admin"]}
        response = ib_NIOS.wapi_request('POST',object_type="admingroup",fields=json.dumps(group6_data))
        display_msg(response)

        display_msg("Create user6 in group6")
        user6_data = {"name": "user6","password": "infoblox","admin_groups": ["group6"]}
        response = ib_NIOS.wapi_request('POST',object_type="adminuser",fields=json.dumps(user6_data))
        display_msg(response)

        display_msg("Create group7")
        group7_data = {"name": "group7","access_method": ["GUI","API"],"roles": ["DNS Admin"]}
        response = ib_NIOS.wapi_request('POST',object_type="admingroup",fields=json.dumps(group7_data))
        display_msg(response)
        
        display_msg("Create user7 in group7")
        user7_data = {"name": "user7","password": "infoblox","admin_groups": ["group7"]}
        response = ib_NIOS.wapi_request('POST',object_type="adminuser",fields=json.dumps(user7_data))
        display_msg(response)
        
        display_msg("Create group8")
        group8_data = {"name": "group8","access_method": ["GUI","API"],"roles": []}
        response = ib_NIOS.wapi_request('POST',object_type="admingroup",fields=json.dumps(group8_data))
        display_msg(response)

        display_msg("Create user8 in group8")
        user8_data = {"name": "user8","password": "infoblox","admin_groups": ["group8"]}
        response = ib_NIOS.wapi_request('POST',object_type="adminuser",fields=json.dumps(user8_data))
        display_msg(response)

        display_msg("Create Global Permission as 'All Zones' for group8")
        data = {"group":"group8","resource_type":"ZONE","permission":"WRITE"}
        response = ib_NIOS.wapi_request('POST',object_type="permission",fields=json.dumps(data))
        display_msg(response)
        
        display_msg("Create IPV6 Network Containers")
        data = [{"method":"POST","object":"ipv6networkcontainer","data":{"network":"1234::/32"}},{"method":"POST","object":"ipv6networkcontainer","data":{"network":"1234::/64"}}]
        response = ib_NIOS.wapi_request('POST',object_type="request",fields=json.dumps(data))
        display_msg(response)
        
        display_msg("Create IPV6 Networks")
        data = [{"method":"POST","object":"ipv6network","data":{"network":"1234::/72"}},{"method":"POST","object":"ipv6network","data":{"network":"2222::/64"}}]
        response = ib_NIOS.wapi_request('POST',object_type="request",fields=json.dumps(data))
        display_msg(response)

        display_msg("Create IPV6 Network Range")
        data = [{"method":"POST","object":"ipv6range","data":{"start_addr":"1234::1", "end_addr":"1234::150", "network":"1234::/72"}}]
        response = ib_NIOS.wapi_request('POST',object_type="request",fields=json.dumps(data))
        display_msg(response)

        display_msg("Create IPV6 Host Objects")
        data = {"ipv6addrs":[{"ipv6addr":"1234::1"}],"name":"ipv6testobj.com","configure_for_dns":False}
        response = ib_NIOS.wapi_request('POST',object_type="record:host",fields=json.dumps(data))
        display_msg(response)
        
        data = {"ipv6addrs":[{"ipv6addr":"1234::150"}],"name":"ipv6testobj1.com","configure_for_dns":False}
        response = ib_NIOS.wapi_request('POST',object_type="record:host",fields=json.dumps(data))
        display_msg(response)
        
        # Getting IPV6 objects ref
        ref_container = ib_NIOS.wapi_request('GET',object_type="ipv6networkcontainer")
        container_ref1 = json.loads(ref_container)[0]['_ref']
        container_ref2 = json.loads(ref_container)[1]['_ref']
        ref_network = ib_NIOS.wapi_request('GET',object_type="ipv6network")
        network_ref = json.loads(ref_network)[0]['_ref']
        ref_range = ib_NIOS.wapi_request('GET',object_type="ipv6range")
        range_ref = json.loads(ref_range)[0]['_ref']

        display_msg("Create IPV6 Object permission for group8")
        data = [{"method":"POST","object":"permission","data":{"group":"group8","object":container_ref1,"permission":"WRITE"}},
                {"method":"POST","object":"permission","data":{"group":"group8","object":container_ref2,"permission":"WRITE"}},
                {"method":"POST","object":"permission","data":{"group":"group8","object":network_ref,"permission":"WRITE"}}, 
                {"method":"POST","object":"permission","data":{"group":"group8","object":range_ref,"permission":"WRITE"}}]
        response = ib_NIOS.wapi_request('POST',object_type="request",fields=json.dumps(data))
        res = json.loads(response)
        container1_perm = res[0]
        container2_perm = res[1]
        network_perm = res[2]
        range_perm = res[3]
        display_msg(response)
        
        display_msg("Test Case 1 Execution Completed")

    @pytest.mark.run(order=2)
    def test_002_get_host_record_from_user6(self):
        display_msg("=="*94)
        display_msg("GET Host Record Object by logging in using user6 credentials")
        get_ref = ib_NIOS.wapi_request("GET",object_type="record:host_ipv6addr", user="user6", password="infoblox")
        res = json.loads(get_ref)
        for obj in res:
            obj.pop("_ref")
        display_msg(res)
        for obj in res:
            assert obj['ipv6addr']=='1234::1' or obj['ipv6addr']=='1234::150' and obj['configure_for_dhcp']==False
        display_msg("TestCase 002 completed succesfully")

    @pytest.mark.run(order=3)
    def test_003_get_host_record_from_user8(self):
        display_msg("=="*94)
        display_msg("GET Host Record Object by logging in using user8 credentials")
        get_ref = ib_NIOS.wapi_request("GET",object_type="record:host_ipv6addr", user="user8", password="infoblox")
        res = json.loads(get_ref)
        for obj in res:
            obj.pop("_ref")
        display_msg(res)
        for obj in res:
            assert obj['ipv6addr']=='1234::1' or obj['ipv6addr']=='1234::150' and obj['configure_for_dhcp']==False
        display_msg("TestCase 003 completed succesfully")

    @pytest.mark.run(order=4)
    def test_004_Create_host_record_in_other_network_and_get_host_record_from_user8(self):
        global container1_perm, container2_perm, network_perm, range_perm
        display_msg("=="*94)
        display_msg("Create IPV6 host record in 2222::/64 network and GET Host Record Object by logging in using user8 credentials")
        display_msg("Creating host record in 2222::/64 network")
        data = {"ipv6addrs":[{"ipv6addr":"2222::11"}],"name":"ipv6testobj_1.com","configure_for_dns":False}
        response = ib_NIOS.wapi_request('POST',object_type="record:host",fields=json.dumps(data))
        display_msg(response)
        display_msg("GET Host Record Object by logging in using user8 credentials")
        get_ref = ib_NIOS.wapi_request("GET",object_type="record:host_ipv6addr", user="user8", password="infoblox")
        res = json.loads(get_ref)
        for obj in res:
            obj.pop("_ref")
        display_msg(res)
        for obj in res:
            assert obj['ipv6addr']=='1234::1' or obj['ipv6addr']=='1234::150' and obj['configure_for_dhcp']==False
        display_msg("TestCase 004 completed succesfully")

    @pytest.mark.run(order=5)
    def test_005_Modify_object_permissions_and_get_host_record_from_user8(self):
        global container1_perm, container2_perm, network_perm, range_perm
        display_msg("=="*94)
        display_msg("Modify Object permissions and GET Host Record Object by logging in using user8 credentials")
        display_msg("Modifying IPV6 Object permission for group8")
        container2_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=container2_perm, fields=json.dumps({'permission':'DENY'})))
        network_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=network_perm, fields=json.dumps({'permission':'DENY'})))
        range_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=range_perm, fields=json.dumps({'permission':'DENY'})))
        display_msg(str(container2_perm)+'\n'+str(network_perm)+'\n'+str(range_perm))
        display_msg("GET Host Record Object by logging in using user8 credentials")
        get_ref = ib_NIOS.wapi_request("GET",object_type="record:host_ipv6addr", user="user8", password="infoblox")
        if get_ref=='[]':
          assert True
        else:
          assert False
        display_msg("TestCase 005 completed succesfully")

    @pytest.mark.run(order=6)
    def test_006_Modify_object_permissions_and_get_host_record_from_user8(self):
        global container1_perm, container2_perm, network_perm, range_perm
        display_msg("=="*94)
        display_msg("Modify Object permissions and GET Host Record Object by logging in using user8 credentials")
        display_msg("Modifying IPV6 Object permission for group8")
        container2_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=container2_perm, fields=json.dumps({'permission':'READ'})))
        display_msg(container2_perm)
        display_msg("GET Host Record Object by logging in using user8 credentials")
        get_ref = ib_NIOS.wapi_request("GET",object_type="record:host_ipv6addr", user="user8", password="infoblox")
        if get_ref=='[]':
          assert True
        else:
          assert False
        display_msg("TestCase 006 completed succesfully")

    @pytest.mark.run(order=7)
    def test_007_Modify_object_permissions_and_get_host_record_from_user8(self):
        global container1_perm, container2_perm, network_perm, range_perm
        display_msg("=="*94)
        display_msg("Modify Object permissions and GET Host Record Object by logging in using user8 credentials")
        display_msg("Modifying IPV6 Object permission for group8")
        network_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=network_perm, fields=json.dumps({'permission':'READ'})))
        display_msg(network_perm)
        display_msg("GET Host Record Object by logging in using user8 credentials")
        get_ref = ib_NIOS.wapi_request("GET",object_type="record:host_ipv6addr", user="user8", password="infoblox")
        res = json.loads(get_ref)
        for obj in res:
            obj.pop("_ref")
        display_msg(res)
        for obj in res:
            assert obj['ipv6addr']=='1234::1' or obj['ipv6addr']=='1234::150' and obj['configure_for_dhcp']==False
        display_msg("TestCase 007 completed succesfully")

    @pytest.mark.run(order=8)
    def test_008_Modify_object_permissions_and_get_host_record_from_user8(self):
        global container1_perm, container2_perm, network_perm, range_perm
        display_msg("=="*94)
        display_msg("Modify Object permissions and GET Host Record Object by logging in using user8 credentials")
        display_msg("Modifying IPV6 Object permission for group8")
        range_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=range_perm, fields=json.dumps({'permission':'READ'})))
        display_msg(range_perm)
        display_msg("GET Host Record Object by logging in using user8 credentials")
        get_ref = ib_NIOS.wapi_request("GET",object_type="record:host_ipv6addr", user="user8", password="infoblox")
        res = json.loads(get_ref)
        for obj in res:
            obj.pop("_ref")
        display_msg(res)
        for obj in res:
            assert obj['ipv6addr']=='1234::1' or obj['ipv6addr']=='1234::150' and obj['configure_for_dhcp']==False
        display_msg("TestCase 008 completed succesfully")

    @pytest.mark.run(order=9)
    def test_009_Modify_object_permissions_and_get_host_record_from_user8(self):
        global container1_perm, container2_perm, network_perm, range_perm
        display_msg("=="*94)
        display_msg("Modify Object permissions and GET Host Record Object by logging in using user8 credentials")
        display_msg("Modifying IPV6 Object permission for group8")
        container1_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=container1_perm, fields=json.dumps({'permission':'READ'})))
        display_msg(container1_perm)
        display_msg("GET Host Record Object by logging in using user8 credentials")
        get_ref = ib_NIOS.wapi_request("GET",object_type="record:host_ipv6addr", user="user8", password="infoblox")
        res = json.loads(get_ref)
        for obj in res:
            obj.pop("_ref")
        display_msg(res)
        for obj in res:
            assert obj['ipv6addr']=='1234::1' or obj['ipv6addr']=='1234::150' and obj['configure_for_dhcp']==False
        display_msg("TestCase 009 completed succesfully")

    @pytest.mark.run(order=10)
    def test_010_Modify_object_permissions_and_get_host_record_from_user8(self):
        global container1_perm, container2_perm, network_perm, range_perm
        display_msg("=="*94)
        display_msg("Modify Object permissions and GET Host Record Object by logging in using user8 credentials")
        display_msg("Modifying IPV6 Object permission for group8")
        container1_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=container1_perm, fields=json.dumps({'permission':'DENY'})))
        container2_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=container2_perm, fields=json.dumps({'permission':'DENY'})))
        network_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=network_perm, fields=json.dumps({'permission':'DENY'})))
        range_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=range_perm, fields=json.dumps({'permission':'WRITE'})))
        display_msg(str(container1_perm)+'\n'+str(container2_perm)+'\n'+str(network_perm)+'\n'+str(range_perm))
        display_msg("GET Host Record Object by logging in using user8 credentials")
        get_ref = ib_NIOS.wapi_request("GET",object_type="record:host_ipv6addr", user="user8", password="infoblox")
        if get_ref=='[]':
          assert True
        else:
          assert False
        display_msg("TestCase 010 completed succesfully")

    @pytest.mark.run(order=11)
    def test_011_Modify_object_permissions_and_get_host_record_from_user8(self):
        global container1_perm, container2_perm, network_perm, range_perm
        display_msg("=="*94)
        display_msg("Modify Object permissions and GET Host Record Object by logging in using user8 credentials")
        display_msg("Modifying IPV6 Object permission for group8")
        range_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=range_perm, fields=json.dumps({'permission':'READ'})))
        display_msg(range_perm)
        display_msg("GET Host Record Object by logging in using user8 credentials")
        get_ref = ib_NIOS.wapi_request("GET",object_type="record:host_ipv6addr", user="user8", password="infoblox")
        if get_ref=='[]':
          assert True
        else:
          assert False
        display_msg("TestCase 011 completed succesfully")

    @pytest.mark.run(order=12)
    def test_012_Modify_object_permissions_and_get_host_record_from_user8(self):
        global container1_perm, container2_perm, network_perm, range_perm
        display_msg("=="*94)
        display_msg("Modify Object permissions and GET Host Record Object by logging in using user8 credentials")
        display_msg("Modifying IPV6 Object permission for group8")
        network_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=network_perm, fields=json.dumps({'permission':'WRITE'})))
        range_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=range_perm, fields=json.dumps({'permission':'DENY'})))
        display_msg(str(network_perm)+'\n'+str(range_perm))
        display_msg("GET Host Record Object by logging in using user8 credentials")
        get_ref = ib_NIOS.wapi_request("GET",object_type="record:host_ipv6addr", user="user8", password="infoblox")
        res = json.loads(get_ref)
        for obj in res:
            obj.pop("_ref")
        display_msg(res)
        for obj in res:
            assert obj['ipv6addr']=='1234::1' or obj['ipv6addr']=='1234::150' and obj['configure_for_dhcp']==False
        display_msg("TestCase 012 completed succesfully")

    @pytest.mark.run(order=13)
    def test_013_Modify_object_permissions_and_get_host_record_from_user8(self):
        global container1_perm, container2_perm, network_perm, range_perm
        display_msg("=="*94)
        display_msg("Modify Object permissions and GET Host Record Object by logging in using user8 credentials")
        display_msg("Modifying IPV6 Object permission for group8")
        container2_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=container2_perm, fields=json.dumps({'permission':'WRITE'})))
        network_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=network_perm, fields=json.dumps({'permission':'DENY'})))
        display_msg(str(container2_perm)+'\n'+str(network_perm))
        display_msg("GET Host Record Object by logging in using user8 credentials")
        get_ref = ib_NIOS.wapi_request("GET",object_type="record:host_ipv6addr", user="user8", password="infoblox")
        if get_ref=='[]':
          assert True
        else:
          assert False
        display_msg("TestCase 013 completed succesfully")

    @pytest.mark.run(order=14)
    def test_014_Modify_object_permissions_and_get_host_record_from_user8(self):
        global container1_perm, container2_perm, network_perm, range_perm
        display_msg("=="*94)
        display_msg("Modify Object permissions and GET Host Record Object by logging in using user8 credentials")
        display_msg("Modifying IPV6 Object permission for group8")
        container1_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=container1_perm, fields=json.dumps({'permission':'WRITE'})))
        container2_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=container2_perm, fields=json.dumps({'permission':'DENY'})))
        display_msg(str(container1_perm)+'\n'+str(container2_perm))
        display_msg("GET Host Record Object by logging in using user8 credentials")
        get_ref = ib_NIOS.wapi_request("GET",object_type="record:host_ipv6addr", user="user8", password="infoblox")
        if get_ref=='[]':
          assert True
        else:
          assert False
        display_msg("TestCase 014 completed succesfully")

    @pytest.mark.run(order=15)
    def test_015_Modify_object_permissions_and_get_host_record_from_user8(self):
        global container1_perm, container2_perm, network_perm, range_perm
        display_msg("=="*94)
        display_msg("Modify Object permissions and GET Host Record Object by logging in using user8 credentials")
        display_msg("Modifying IPV6 Object permission for group8")
        container2_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=container2_perm, fields=json.dumps({'permission':'READ'})))
        network_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=network_perm, fields=json.dumps({'permission':'READ'})))
        display_msg(str(container2_perm)+'\n'+str(network_perm)+'\n'+str(range_perm))
        display_msg("GET Host Record Object by logging in using user8 credentials")
        get_ref = ib_NIOS.wapi_request("GET",object_type="record:host_ipv6addr", user="user8", password="infoblox")
        res = json.loads(get_ref)
        for obj in res:
            obj.pop("_ref")
        display_msg(res)
        for obj in res:
            assert obj['ipv6addr']=='1234::1' or obj['ipv6addr']=='1234::150' and obj['configure_for_dhcp']==False
        display_msg("TestCase 015 completed succesfully")

    @pytest.mark.run(order=16)
    def test_016_Modify_object_permissions_and_get_host_record_from_user8(self):
        global container1_perm, container2_perm, network_perm, range_perm
        display_msg("=="*94)
        display_msg("Modify Object permissions and GET Host Record Object by logging in using user8 credentials")
        display_msg("Modifying IPV6 Object permission for group8")
        range_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=range_perm, fields=json.dumps({'permission':'READ'})))
        display_msg(range_perm)
        display_msg("GET Host Record Object by logging in using user8 credentials")
        get_ref = ib_NIOS.wapi_request("GET",object_type="record:host_ipv6addr", user="user8", password="infoblox")
        res = json.loads(get_ref)
        for obj in res:
            obj.pop("_ref")
        display_msg(res)
        for obj in res:
            assert obj['ipv6addr']=='1234::1' or obj['ipv6addr']=='1234::150' and obj['configure_for_dhcp']==False
        display_msg("TestCase 016 completed succesfully")

    @pytest.mark.run(order=17)
    def test_017_Modify_object_permissions_and_get_host_record_from_user8(self):
        global container1_perm, container2_perm, network_perm, range_perm
        display_msg("=="*94)
        display_msg("Modify Object permissions and GET Host Record Object by logging in using user8 credentials")
        display_msg("Modifying IPV6 Object permission for group8")
        container1_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=container1_perm, fields=json.dumps({'permission':'READ'})))
        display_msg(container1_perm)
        display_msg("GET Host Record Object by logging in using user8 credentials")
        get_ref = ib_NIOS.wapi_request("GET",object_type="record:host_ipv6addr", user="user8", password="infoblox")
        res = json.loads(get_ref)
        for obj in res:
            obj.pop("_ref")
        display_msg(res)
        for obj in res:
            assert obj['ipv6addr']=='1234::1' or obj['ipv6addr']=='1234::150' and obj['configure_for_dhcp']==False
        display_msg("TestCase 017 completed succesfully")

    @pytest.mark.run(order=18)
    def test_018_Modify_object_permissions_and_get_host_record_from_user8(self):
        global container1_perm, container2_perm, network_perm, range_perm
        display_msg("=="*94)
        display_msg("Modify Object permissions and GET Host Record Object by logging in using user8 credentials")
        display_msg("Modifying IPV6 Object permission for group8")
        container1_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=container1_perm, fields=json.dumps({'permission':'DENY'})))
        container2_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=container2_perm, fields=json.dumps({'permission':'DENY'})))
        network_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=network_perm, fields=json.dumps({'permission':'DENY'})))
        range_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=range_perm, fields=json.dumps({'permission':'WRITE'})))
        display_msg(str(container1_perm)+'\n'+str(container2_perm)+'\n'+str(network_perm)+'\n'+str(range_perm))
        display_msg("GET Host Record Object by logging in using user8 credentials")
        get_ref = ib_NIOS.wapi_request("GET",object_type="record:host_ipv6addr", user="user8", password="infoblox")
        if get_ref=='[]':
          assert True
        else:
          assert False
        display_msg("TestCase 018 completed succesfully")

    @pytest.mark.run(order=19)
    def test_019_Modify_object_permissions_and_get_host_record_from_user8(self):
        global container1_perm, container2_perm, network_perm, range_perm
        display_msg("=="*94)
        display_msg("Modify Object permissions and GET Host Record Object by logging in using user8 credentials")
        display_msg("Modifying IPV6 Object permission for group8")
        range_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=range_perm, fields=json.dumps({'permission':'READ'})))
        display_msg(range_perm)
        display_msg("GET Host Record Object by logging in using user8 credentials")
        get_ref = ib_NIOS.wapi_request("GET",object_type="record:host_ipv6addr", user="user8", password="infoblox")
        if get_ref=='[]':
          assert True
        else:
          assert False
        display_msg("TestCase 019 completed succesfully")

    @pytest.mark.run(order=20)
    def test_020_Modify_object_permissions_and_get_host_record_from_user8(self):
        global container1_perm, container2_perm, network_perm, range_perm
        display_msg("=="*94)
        display_msg("Modify Object permissions and GET Host Record Object by logging in using user8 credentials")
        network_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=network_perm, fields=json.dumps({'permission':'WRITE'})))
        range_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=range_perm, fields=json.dumps({'permission':'DENY'})))
        display_msg(str(network_perm)+'\n'+str(range_perm))
        display_msg("GET Host Record Object by logging in using user8 credentials")
        get_ref = ib_NIOS.wapi_request("GET",object_type="record:host_ipv6addr", user="user8", password="infoblox")
        res = json.loads(get_ref)
        for obj in res:
            obj.pop("_ref")
        display_msg(res)
        for obj in res:
            assert obj['ipv6addr']=='1234::1' or obj['ipv6addr']=='1234::150' and obj['configure_for_dhcp']==False
        display_msg("TestCase 020 completed succesfully")

    @pytest.mark.run(order=21)
    def test_021_Modify_object_permissions_and_get_host_record_from_user8(self):
        global container1_perm, container2_perm, network_perm, range_perm
        display_msg("=="*94)
        display_msg("Modify Object permissions and GET Host Record Object by logging in using user8 credentials")
        display_msg("Modifying IPV6 Object permission for group8")
        container2_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=container2_perm, fields=json.dumps({'permission':'WRITE'})))
        network_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=network_perm, fields=json.dumps({'permission':'DENY'})))
        display_msg(str(container2_perm)+'\n'+str(network_perm))
        display_msg("GET Host Record Object by logging in using user8 credentials")
        get_ref = ib_NIOS.wapi_request("GET",object_type="record:host_ipv6addr", user="user8", password="infoblox")
        if get_ref=='[]':
          assert True
        else:
          assert False
        display_msg("TestCase 021 completed succesfully")

    @pytest.mark.run(order=22)
    def test_022_Modify_object_permissions_and_get_host_record_from_user8(self):
        global container1_perm, container2_perm, network_perm, range_perm
        display_msg("=="*94)
        display_msg("Modify Object permissions and GET Host Record Object by logging in using user8 credentials")
        display_msg("Modifying IPV6 Object permission for group8")
        container1_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=container1_perm, fields=json.dumps({'permission':'WRITE'})))
        container2_perm = json.loads(ib_NIOS.wapi_request('PUT', ref=container2_perm, fields=json.dumps({'permission':'DENY'})))
        display_msg(str(container1_perm)+'\n'+str(container2_perm))
        display_msg("GET Host Record Object by logging in using user8 credentials")
        get_ref = ib_NIOS.wapi_request("GET",object_type="record:host_ipv6addr", user="user8", password="infoblox")
        if get_ref=='[]':
          assert True
        else:
          assert False
        display_msg("TestCase 022 completed succesfully")

    @pytest.mark.run(order=23)
    def test_023_get_host_record_from_user6(self):
        display_msg("=="*94)
        display_msg("GET Host Record Object by logging in using user5 credentials")
        get_ref = ib_NIOS.wapi_request("GET",object_type="record:host_ipv6addr", user="user5", password="infoblox")
        if get_ref=='[]':
          assert True
        else:
          assert False
        display_msg("TestCase 023 completed succesfully")
    
    @pytest.mark.run(order=-1)
    def test_cleanup(self):
        display_msg("=="*45+"*Clean-up*"+"=="*44)
        get_ref = ib_NIOS.wapi_request('GET',object_type="adminuser")
        for ref in json.loads(get_ref):
            if 'user' in ref['name']:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])
        
        get_ref = ib_NIOS.wapi_request('GET',object_type="admingroup")
        for ref in json.loads(get_ref):
            if 'group' in ref['name']:
                ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])
        
        get_ref = ib_NIOS.wapi_request('GET',object_type="ipv6network")
        for ref in json.loads(get_ref):
            ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])
        
        get_ref = ib_NIOS.wapi_request('GET',object_type="ipv6networkcontainer")
        for ref in json.loads(get_ref):
            ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])
        
        get_ref = ib_NIOS.wapi_request('GET',object_type="ipv6range")
        for ref in json.loads(get_ref):
            ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])
        
        display_msg("Clean-up process completed succesfully")
    
    
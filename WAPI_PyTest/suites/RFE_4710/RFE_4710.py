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
import sys

def display_msg(x):
    logging.info(x)
    print("\n"+x)

def generate_token_from_file(filepath, filename):
    dir_name = filepath
    base_filename = filename
    filename = os.path.join(dir_name, base_filename)
    data = {"filename": base_filename}
    create_file = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=uploadinit")
    logging.info(create_file)
    res = json.loads(create_file)
    token = json.loads(create_file)['token']
    url = json.loads(create_file)['url']
    print create_file
    print res
    print token
    print url
    os.system('curl -k1 -u admin:infoblox -F name=%s -F filedata=@%s %s' % (filename, filename, url))
    filename = "/" + filename
    return token


def get_object_reference(object_type, data):
    object_type1 = object_type
    data = data
    get_ref = ib_NIOS.wapi_request('GET', object_type=object_type1, fields=json.dumps(data))
    logging.info(get_ref)
    res = json.loads(get_ref)
    ref = json.loads(get_ref)[0]['_ref']
    print res
    print ref
    return ref


class  Network(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_001_create_vlan_View(self):      
        logging.info("Create Vlan View")        
        data = {"name":"VLAN_view","start_vlan_id":100,"end_vlan_id":200}
        post_ref=ib_NIOS.wapi_request('POST',object_type ="vlanview", fields=json.dumps(data))
        ref=json.loads(post_ref)
        res=ib_NIOS.wapi_request('GET' ,object_type=ref)
        res_json=json.loads(res)
        res_json.pop("_ref")
        assert res_json== data
        display_msg("=="*50)
        display_msg("TEST 1 COMPLETED")

        
    @pytest.mark.run(order=2)
    def test_002_create_Vlan_range_under_vlan_view(self):
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


    @pytest.mark.run(order=3)
    def test_003_create_Vlan_id_under_vlan_view(self):
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


    @pytest.mark.run(order=4)
    def test_004_create_Vlan_id_under_vlan_range(self):
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


    @pytest.mark.run(order=5)
    def test_005_create_ipv4_Network_assign_vlan_id_added_under_vlanview(self):
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


    @pytest.mark.run(order=6)
    def test_006_create_ipv6_Network_assign_vlan_id_added_under_vlanview(self):
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



    @pytest.mark.run(order=7)
    def test_007_create_ipv4_Network_assign_vlan_id_added_under_vlanrange(self):
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
    

    @pytest.mark.run(order=8)
    def test_008_create_ipv6_Network_assign_vlan_id_added_under_vlanrange(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlan")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="VLAN_id2":
                ref= i["_ref"]
        print ref
        data =  {"network_view":"default","network":"2222:10A:6000:2500::/64","vlans":[{"vlan":ref}] }
        response = ib_NIOS.wapi_request('POST',object_type="ipv6network",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 8 COMPLETED")


    @pytest.mark.run(order=9)
    def test_009_create_vlan_View_with_pre_create_option(self):
        logging.info("Create Vlan View")
        data ={"name":"VLAN_view2","start_vlan_id":1,"end_vlan_id":20,"vlan_name_prefix":"vlan@123","pre_create_vlan":True}
        response=ib_NIOS.wapi_request('POST',object_type ="vlanview", fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 09 COMPLETED")


    @pytest.mark.run(order=10)
    def test_010_create_ipv4_Network_assign_vlan_id_using_nextavailablevlan(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="VLAN_view2":
                ref= i["_ref"]
        print ref
        data =  {"network_view":"default","network":"63.0.0.0/24","vlans":[{"vlan":"func:nextavailablevlan:"+ref}]}
        response = ib_NIOS.wapi_request('POST',object_type="network",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 10 COMPLETED")


    @pytest.mark.run(order=11)
    def test_011_create_ipv6_Network_assign_vlan_id_using_nextavailablevlan(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="VLAN_view2":
                ref= i["_ref"]
        print ref
        data =  {"network_view":"default","network":"3333:10A:6000:2500::/64","vlans":[{"vlan":"func:nextavailablevlan:"+ref}]}
        response = ib_NIOS.wapi_request('POST',object_type="ipv6network",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 11 COMPLETED")

        
    @pytest.mark.run(order=12)
    def test_012_create_vlan_View(self):
        logging.info("Create Vlan View")
        data = {"name":"VLAN_view3","start_vlan_id":1,"end_vlan_id":20}
        response=ib_NIOS.wapi_request('POST',object_type ="vlanview", fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 12 COMPLETED")

                             
                             
    @pytest.mark.run(order=13)
    def test_013_create_Vlan_range_under_vlan_view(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="VLAN_view3":
                ref=i["_ref"]
        data = {"vlan_view":ref,"name": "VLAN_range3","start_vlan_id":1,"end_vlan_id":10,"vlan_name_prefix":"test123","pre_create_vlan":True,"comment":"test comment"}
        post_ref = ib_NIOS.wapi_request('POST',object_type="vlanrange",  fields=json.dumps(data))
        ref=json.loads(post_ref)
        res=ib_NIOS.wapi_request('GET' ,object_type=ref)
        print res
        res_json=json.loads(res)
        assert  data["name"]==res_json["name"] and data["start_vlan_id"]==res_json["start_vlan_id"]  and data["end_vlan_id"]==res_json["end_vlan_id"]                
        display_msg("=="*50)
        display_msg("TEST 13 COMPLETED")
                             
                             
    @pytest.mark.run(order=14)
    def test_014_create_Vlan_id_under_vlan_view_using_nextavailable_function(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanrange")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="VLAN_range3":
                ref=i["_ref"]
        '''data = {"parent":ref,"name": "VLAN_id1","id":"func:nextavailablevlanid:"+ref,"name":"vlan","reserved":true,"contact":"879220","department":"ng","description":"descn"}
        '''
        data={"network_view":"default","network":"64.0.0.0/24","vlans":[{"vlan":"func:nextavailablevlan:"+ref}]}
        response = ib_NIOS.wapi_request('POST',object_type="network",  fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 14 COMPLETED")
                             
                             
                             
    @pytest.mark.run(order=15)
    def test_015_create_Vlan_id_under_vlan_view_nextavailable_function(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanrange")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="VLAN_range3":
                ref=i["_ref"]
        '''data = {"parent":ref,"name": "VLAN_id1","id":"func:nextavailablevlanid:"+ref,"name":"vlan","reserved":true,"contact":"879220","department":"ng","description":"descn"}
        '''
        data={"network_view":"default","network":"21::/64","vlans":[{"vlan":"func:nextavailablevlan:"+ref}]}
        response = ib_NIOS.wapi_request('POST',object_type="ipv6network",  fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 15 COMPLETED")


                             
                             
    @pytest.mark.run(order=16)
    def test_016_create_vlan_View(self):
        logging.info("Create Vlan View")
        data = {"name":"VLAN_view4","start_vlan_id":1,"end_vlan_id":20}
        post_ref=ib_NIOS.wapi_request('POST',object_type ="vlanview", fields=json.dumps(data))
        ref=json.loads(post_ref)
        res=ib_NIOS.wapi_request('GET' ,object_type=ref)
        res_json=json.loads(res)
        res_json.pop("_ref")
        assert res_json== data
        display_msg("=="*50)
        display_msg("TEST 16 COMPLETED")

                             
    @pytest.mark.run(order=17)
    def test_017_create_Vlan_id_under_vlan_range(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="VLAN_view4":
                ref= i["_ref"]
        data = {"parent":ref,"name": "VLAN_id1","id":"func:nextavailablevlanid:"+ref,"name":"vlan","reserved":True,"contact":"879220","department":"ng","description":"descn"}
        response = ib_NIOS.wapi_request('POST',object_type="vlan",  fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 17 COMPLETED")


                             
                             
    @pytest.mark.run(order=18)
    def test_018_create_Vlan_range_under_vlan_view(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="VLAN_view4":
                ref=i["_ref"]
        data = {"vlan_view":ref,"name": "VLAN_range4","start_vlan_id":5,"end_vlan_id":10,"comment":"test comment"}
        post_ref = ib_NIOS.wapi_request('POST',object_type="vlanrange",  fields=json.dumps(data))
        ref=json.loads(post_ref)
        res=ib_NIOS.wapi_request('GET' ,object_type=ref)
        print res
        res_json=json.loads(res)
        assert  data["name"]==res_json["name"] and data["start_vlan_id"]==res_json["start_vlan_id"]  and data["end_vlan_id"]==res_json["end_vlan_id"]
        display_msg("=="*50)
        display_msg("TEST 18 COMPLETED")
                             
                             
                             
    @pytest.mark.run(order=19)
    def test_019_create_Vlan_id_under_vlan_range(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanrange")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="VLAN_range4":
                ref= i["_ref"]
        data = {"parent":ref,"name": "VLAN_id2","id":"func:nextavailablevlanid:"+ref,"name":"vlan","reserved":True,"contact":"879220","department":"ng","description":"descn"}
        response= ib_NIOS.wapi_request('POST',object_type="vlan",  fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 19 COMPLETED")

    @pytest.mark.run(order=20)
    def test_020_Negative_create_vlan_View_without_passing_the_name(self):
        logging.info("Create Vlan View")
        data = {"name":"","start_vlan_id":1,"end_vlan_id":20}
        status, response = ib_NIOS.wapi_request('POST',object_type="vlanview",fields=json.dumps(data), grid_vip=config.grid_vip)
        display_msg(response)
        assert re.search(r"Required value missing", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 20 COMPLETED")
                             
                             
    @pytest.mark.run(order=21)
    def test_021_Negative_create_vlan_View_with_start_value_as_zero(self):
        logging.info("Create Vlan View")
        data = {"name":"view","start_vlan_id":0,"end_vlan_id":20}
        status, response = ib_NIOS.wapi_request('POST',object_type="vlanview",fields=json.dumps(data), grid_vip=config.grid_vip)
        display_msg(response)
        assert re.search(r"The 'Start VLAN ID' field must contain a value from 1 to 4094", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 21 COMPLETED")


    @pytest.mark.run(order=22)
    def test_022_Negative_create_vlan_View_with_start_value_as_4096(self):
        logging.info("Create Vlan View")
        data = {"name":"view","start_vlan_id":4096,"end_vlan_id":5000}
        status, response = ib_NIOS.wapi_request('POST',object_type="vlanview",fields=json.dumps(data), grid_vip=config.grid_vip)
        display_msg(response)
        assert re.search(r"The 'Start VLAN ID' field must contain a value from 1 to 4094", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 22 COMPLETED")


    @pytest.mark.run(order=23)
    def test_023_Negative_create_vlan_View_with_End_Start_value_as_zero(self):
        logging.info("Create Vlan View")
        data = {"name":"view","start_vlan_id":22,"end_vlan_id":0}
        status, response = ib_NIOS.wapi_request('POST',object_type="vlanview",fields=json.dumps(data), grid_vip=config.grid_vip)
        display_msg(response)
        assert re.search(r"The start VLAN ID of 22 must not be greater than the end VLAN ID of 0", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 23 COMPLETED")

    @pytest.mark.run(order=24)
    def test_024_Negative_create_vlan_View_with_End_Start_value_as_4096(self):
        logging.info("Create Vlan View")
        data = {"name":"view","start_vlan_id":22,"end_vlan_id":4096}
        status, response = ib_NIOS.wapi_request('POST',object_type="vlanview",fields=json.dumps(data), grid_vip=config.grid_vip)
        display_msg(response)
        assert re.search(r"The 'End VLAN ID' field must contain a value from 1 to 4094", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 24 COMPLETED")

    @pytest.mark.run(order=25)
    def test_025_Negative_create_Vlan_range_under_vlan_view_without_passing_Name(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="VLAN_view4":
                ref=i["_ref"]
        data = {"vlan_view":ref,"name":"","start_vlan_id":15,"end_vlan_id":20,"comment":"test comment"}
        status, response = ib_NIOS.wapi_request('POST',object_type="vlanrange",  fields=json.dumps(data))
        display_msg(response)
        assert re.search(r"'Required value missing'", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 25 COMPLETED")

    @pytest.mark.run(order=26)
    def test_026_Negative_create_Vlan_range_under_vlan_view_with_outofrange_value(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="VLAN_view4":
                ref=i["_ref"]
        data = {"vlan_view":ref,"name":"range4","start_vlan_id":22,"end_vlan_id":25,"comment":"test comment"}
        status, response = ib_NIOS.wapi_request('POST',object_type="vlanrange",  fields=json.dumps(data))
        display_msg(response)
        assert re.search(r"The VLAN range is not within the selected VLAN view with IDs from 1...20", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 26 COMPLETED")


    @pytest.mark.run(order=27)
    def test_027_Negative_create_Vlan_range_under_vlan_view_with_startvalid_value_is_more(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="VLAN_view4":
                ref=i["_ref"]
        data = {"vlan_view":ref,"name":"","start_vlan_id":21,"end_vlan_id":20,"comment":"test comment"}
        status, response = ib_NIOS.wapi_request('POST',object_type="vlanrange",  fields=json.dumps(data))
        display_msg(response)
        assert re.search(r"The start VLAN ID of 21 must not be greater than the end VLAN ID of 20", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 27 COMPLETED")

    

    @pytest.mark.run(order=28)
    def test_028_create_custom_network_view(self):
        display_msg("Create custom network  View")
        data = {"name": "custom_network"}
        response = ib_NIOS.wapi_request('POST',object_type="networkview",fields=json.dumps(data), grid_vip=config.grid_vip)
        response1 = json.loads(response)
        display_msg(response)
        get_ref=ib_NIOS.wapi_request('GET', object_type="networkview")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="custom_network":
                ref=i["_ref"]
        assert  response1==ref
        display_msg("=="*50)
        display_msg("TEST 28 COMPLETED")

    @pytest.mark.run(order=29)
    def test_029_create_ipv4_Network_under_custom_Network_View_assign_vlan_id_using_nextavailablevlan(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="VLAN_view2":
                ref= i["_ref"]
        print ref
        data =  {"network_view":"custom_network","network":"27.0.0.0/24","vlans":[{"vlan":"func:nextavailablevlan:"+ref}]}
        response = ib_NIOS.wapi_request('POST',object_type="network",fields=json.dumps(data))
        display_msg("=="*50)
        display_msg("TEST 29 COMPLETED")

    @pytest.mark.run(order=30)
    def test_030_create_ipv6_Network_under_custom_Network_View_assign_vlan_id_using_nextavailablevlan(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="VLAN_view2":
                ref= i["_ref"]
        print ref
        data =  {"network_view":"custom_network","network":"28:10A:6000:3000::/64","vlans":[{"vlan":"func:nextavailablevlan:"+ref}]}
        response = ib_NIOS.wapi_request('POST',object_type="ipv6network",fields=json.dumps(data))
        display_msg("=="*50)
        display_msg("TEST 30 COMPLETED")





    @pytest.mark.run(order=31)
    def test_031_create_ipv4_Network_assign_multiple_vlan_id_using_nextavailablevlan(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="VLAN_view2":
                ref= i["_ref"]
        print ref
        data =  {"network_view":"custom_network","network":"29.0.0.0/24","vlans":[{"vlan":"func:nextavailablevlan:"+ref},{"vlan":"func:nextavailablevlan:"+ref},{"vlan":"func:nextavailablevlan:"+ref}]}
        response = ib_NIOS.wapi_request('POST',object_type="network",fields=json.dumps(data))

        for i in res:
            if i["name"]=="VLAN_view4":
                ref=i["_ref"]
        data = {"parent":ref,"name": "","id":8,"reserved":True}
        status, response = ib_NIOS.wapi_request('POST',object_type="vlan",  fields=json.dumps(data))
        display_msg(response)
        assert re.search(r"'Required value missing'", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 31 COMPLETED")

    @pytest.mark.run(order=32)
    def test_032_Negative_create_Vlan_id_under_vlan_view_without_passing_Name(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="VLAN_view4":
                ref=i["_ref"]
        data = {"parent":ref,"name": "","id":8,"reserved":True}
        status, response = ib_NIOS.wapi_request('POST',object_type="vlan",  fields=json.dumps(data))
        display_msg(response)
        assert re.search(r"'Required value missing'", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 32 COMPLETED")

                         
    @pytest.mark.run(order=33)
    def test_033_Negative_create_Vlan_id_under_vlan_view_with_duplicate_id(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="VLAN_view4":
                ref=i["_ref"]
        data = {"parent":ref,"name": "test","id":1,"reserved":True}
        status, response = ib_NIOS.wapi_request('POST',object_type="vlan",  fields=json.dumps(data))
        display_msg(response)
        assert re.search(r"Duplicate object 'test' with ID 1 of type 'VLAN' already exists in the database", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 33 COMPLETED")

                             
    @pytest.mark.run(order=34)
    def test_034_Negative_create_Vlan_id_under_vlan_view_outside_the_vlanview_range(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="VLAN_view4":
                ref=i["_ref"]
        data = {"parent":ref,"name": "test","id":21,"reserved":True}
        status, response = ib_NIOS.wapi_request('POST',object_type="vlan",  fields=json.dumps(data))
        display_msg(response)
        assert re.search(r"The VLAN is not within the selected VLAN view with IDs from 1...20", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 34 COMPLETED")



    @pytest.mark.run(order=35)
    def test_035_Negative_create_Vlan_id_under_vlan_range_without_passing_Name(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanrange")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="VLAN_range4":
                ref=i["_ref"]
        data = {"parent":ref,"name": "","id":8,"reserved":True}
        status, response = ib_NIOS.wapi_request('POST',object_type="vlan",  fields=json.dumps(data))
        display_msg(response)
        assert re.search(r"'Required value missing'", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 35 COMPLETED ")



    @pytest.mark.run(order=36)
    def test_036_Negative_create_Vlan_id_under_vlan_range_with_duplicate_id(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanrange")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="VLAN_range4":
                ref=i["_ref"]
        data = {"parent":ref,"name": "test","id":5,"reserved":True}
        status, response = ib_NIOS.wapi_request('POST',object_type="vlan",  fields=json.dumps(data))
        display_msg(response)
        assert re.search(r"Duplicate object 'test' with ID 5 of type 'VLAN' already exists in the database", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 36 COMPLETED")

    @pytest.mark.run(order=37)
    def test_037_Negative_create_Vlan_id_under_vlan_range_outside_the_vlanview_range(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanrange")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="VLAN_range4":
                ref=i["_ref"]
        data = {"parent":ref,"name": "test","id":21,"reserved":True}
        status, response = ib_NIOS.wapi_request('POST',object_type="vlan",  fields=json.dumps(data))
        display_msg(response)
        assert re.search(r"The VLAN is not within the selected VLAN range with IDs from", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 37 COMPLETED")

    @pytest.mark.run(order=38)
    def test_038_create_vlan_id_under_default_view_with_reserved_as_true(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="default":
                ref=i["_ref"]
        data = {"parent":ref,"name": "test1","id":1,"reserved":True}
        post_ref = ib_NIOS.wapi_request('POST',object_type="vlan",  fields=json.dumps(data))
        ref=json.loads(post_ref)
        res=ib_NIOS.wapi_request('GET' ,object_type=ref)
        print res
        res_json=json.loads(res)
        assert  data["name"]==res_json["name"] and data["id"]==res_json["id"]
        display_msg("=="*50)
        display_msg("TEST 3 COMPLETED")

    @pytest.mark.run(order=39)
    def test_039_Negative_create_network_under_default_vlan_view_where_only_one_reserved_vlan_id_available(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="default":
                ref=i["_ref"]
        data =  {"network_view":"default","network":"39.0.0.0/24","vlans":[{"vlan":"func:nextavailablevlan:"+ref}]}
        status,response = ib_NIOS.wapi_request('POST',object_type="network",fields=json.dumps(data))
        display_msg(response)
        assert re.search(r"Cannot find 1 next available VLANs in this VLAN view", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 39 COMPLETED")

    @pytest.mark.run(order=40)
    def test_040_create_vlan_id_under_default_view_with_reserved_as_false(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="default":
                ref=i["_ref"]
        data = {"parent":ref,"name": "test2","id":2}
        post_ref = ib_NIOS.wapi_request('POST',object_type="vlan",  fields=json.dumps(data))
        ref=json.loads(post_ref)
        res=ib_NIOS.wapi_request('GET' ,object_type=ref)
        print res
        res_json=json.loads(res)
        assert  data["name"]==res_json["name"] and data["id"]==res_json["id"]
        display_msg("=="*50)
        display_msg("TEST 40 COMPLETED")

    @pytest.mark.run(order=41)
    def test_041__delete_vlan_id_as_reserved_from_vlan_view(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlan")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="test1":
                ref= i["_ref"]
        print ref
        logging.info("Deleting the vlan id from vlan view as reserved")
        response = ib_NIOS.wapi_request('DELETE', object_type=ref, grid_vip=config.grid_vip)
        display_msg(response)
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 19 COMPLETED")

    @pytest.mark.run(order=42)
    def test_042__delete_vlan_id_as_unassigned_from_vlan_view(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlan")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="test2":
                ref= i["_ref"]
        print ref
        logging.info("Deleting the vlan id from vlan view as unassigned")
        response = ib_NIOS.wapi_request('DELETE', object_type=ref, grid_vip=config.grid_vip)
        display_msg(response)
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 19 COMPLETED")


    @pytest.mark.run(order=43)
    def test_043__delete_ipv4_Network_which_is_having_assign_vlan_id_from_vlan_view(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="network")
        res = json.loads(get_ref)
        for i in res:
            if i["network"]=="61.0.0.0/24":
                ref= i["_ref"]
        print ref
        logging.info("Deleting the IPv4 network which is having assigned vlan id from vlan view")
        status, response = ib_NIOS.wapi_request('DELETE', object_type=ref, grid_vip=config.grid_vip)
        display_msg(response)
        assert re.search(r"Cannot delete the '61.0.0.0/24' network because it has VLANs assigned to it", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 40 COMPLETED") 


    @pytest.mark.run(order=44)
    def test_044_Negative_delete_ipv6_Network_which_is_having_assign_vlan_id_from_vlan_view(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6network")
        res = json.loads(get_ref)
        for i in res:
            if i["network"]=="2620:10a:6000:2500::/64":
                ref= i["_ref"]
        print ref

        logging.info("Deleting the IPv6 network which is having assigned vlan id from vlan view")
        status, response = ib_NIOS.wapi_request('DELETE', object_type=ref, grid_vip=config.grid_vip)
        display_msg(response)
        assert re.search(r"Cannot delete the '2620:10a:6000:2500::/64' network because it has VLANs assigned to it", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 41 COMPLETED")



    @pytest.mark.run(order=45)
    def test_045_Negative_delete_vlan_View_which_is_having_assign_vlan_id(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="VLAN_view":
                ref= i["_ref"]
        print ref
        logging.info("Deleting the IPv4 network which is having assigned vlan id and delete the vlan view")
        status, response = ib_NIOS.wapi_request('DELETE', object_type=ref, grid_vip=config.grid_vip)
        display_msg(response)
        assert re.search(r"Cannot delete 'VLAN_id1' VLAN in the 'VLAN_view' VLAN view as it is currently assigned to an IPAM object", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 42 COMPLETED")


    @pytest.mark.run(order=46)
    def test_046_Negative_delete_ipv4_Network_which_is_having_assign_vlan_id_from_vlan_range(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="network")
        res = json.loads(get_ref)
        for i in res:
            if i["network"]=="62.0.0.0/24":
                ref= i["_ref"]
        print ref
        logging.info("Deleting the IPv4 network which is having assigned vlan id from vlan range")
        status, response = ib_NIOS.wapi_request('DELETE', object_type=ref, grid_vip=config.grid_vip)
        display_msg(response)
        assert re.search(r"Cannot delete the '62.0.0.0/24' network because it has VLANs assigned to it", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 43 COMPLETED")



    @pytest.mark.run(order=47)
    def test_047_delete_ipv6_Network_which_is_having_assign_vlan_id_from_vlan_range(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6network")
        res = json.loads(get_ref)
        for i in res:
            if i["network"]=="2222:10a:6000:2500::/64":
                ref= i["_ref"]
        print ref

        logging.info("Deleting the IPv6 network which is having assigned vlan id from vlan range")
        status, response = ib_NIOS.wapi_request('DELETE', object_type=ref, grid_vip=config.grid_vip)
        display_msg(response)
        assert re.search(r"Cannot delete the '2222:10a:6000:2500::/64' network because it has VLANs assigned to it", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 44 COMPLETED")


    @pytest.mark.run(order=48)
    def test_048_Negative_delete_vlanid_under_vlanview_which_is_assign_to_network(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlan")
        res = json.loads(get_ref)
        for i in res:
            if i["id"]==159:
                ref= i["_ref"]
        print ref

        logging.info("Deleting vlanid under vlan view assigned to network")
        status, response = ib_NIOS.wapi_request('DELETE', object_type=ref, grid_vip=config.grid_vip)
        display_msg(response)
        assert re.search(r"Cannot delete 'VLAN_id1' VLAN in the 'VLAN_view' VLAN view as it is currently assigned to an IPAM object", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 45 COMPLETED")


    @pytest.mark.run(order=49)
    def test_049_Negative_delete_vlanid_under_vlan_range_which_is_assign_to_network(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlan")
        res = json.loads(get_ref)
        for i in res:
            if i["id"]==154:
                ref= i["_ref"]
        print ref

        logging.info("Deleting vlanid under vlan range assigned to network")
        status, response = ib_NIOS.wapi_request('DELETE', object_type=ref, grid_vip=config.grid_vip)
        display_msg(response)
        assert re.search(r"Cannot delete 'VLAN_id2' VLAN from 'VLAN_range1' VLAN range in the 'VLAN_view' VLAN view as it is currently assigned to an IPAM object", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 46 COMPLETED")
    
    @pytest.mark.run(order=50)
    def test_050_validate_create_vlans__with_pre_create_option(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlan?name=vlan@1230001")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="vlan@1230001":
                ref=i["_ref"]
                assert True
            else:
                assert False
        display_msg("=="*50)
        display_msg("TEST 50 COMPLETED")


    @pytest.mark.run(order=51)
    def test_051_create_Vlan_id_under_vlan_view(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="VLAN_view2":
                ref=i["_ref"]
        data = {"parent":ref,"name": "test_vlan1","id":1,"reserved":True,"contact":"879220","department":"ng","description":"descn"}
        status,response = ib_NIOS.wapi_request('POST',object_type="vlan",  fields=json.dumps(data))
        display_msg(response)
        assert re.search(r"Duplicate object \'test_vlan1\' with ID 1 of type \'VLAN\' already exists in the database", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 51 COMPLETED")


    @pytest.mark.run(order=52)
    def test_052_create_ipv4_Networkcontainer_assign_vlan_id_added_under_vlanview(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlan")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="VLAN_id1":
                ref= i["_ref"]
        print ref
        data =  {"network_view":"default","network":"61.0.0.0/8","vlans":[{"vlan":ref}] }
        status,response = ib_NIOS.wapi_request('POST',object_type="networkcontainer",fields=json.dumps(data))
        read  = re.search(r'Unknown argument/field',response)
        for read in  response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 52 COMPLETED")
    
    @pytest.mark.run(order=53)
    def test_053_Create_admin_group(self):
        logging.info("Create A new admin group")
        data = {"name": "group_vlan"}
        response = ib_NIOS.wapi_request('POST', object_type="admingroup", fields=json.dumps(data))
        print response
        logging.info(response)
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        logging.info("Test Case 53 Execution Completed")

    @pytest.mark.run(order=54)
    def test_054_Create_admin_user(self):
        logging.info("Create A new admin user")
        data = {"admin_groups": ["group_vlan"],"comment": "test_vlan","name": "user_vlan","password":"infoblox"}
        response = ib_NIOS.wapi_request('POST', object_type="adminuser", fields=json.dumps(data))
        print response
        logging.info(response)
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        logging.info("Test Case 54 Execution Completed")
    

    @pytest.mark.run(order=55)
    def test_055_Create_admin_group_permission_as_deny_for_VLAN_View(self):
        display_msg("Create A new admin group")
        data = {"group":"group_vlan","permission":"DENY","resource_type":"VLAN_VIEW"}
        response = ib_NIOS.wapi_request('POST', object_type="permission", fields=json.dumps(data))
        display_msg(response)
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        display_msg("Test Case 55 Execution Completed")

    @pytest.mark.run(order=56)
    def test_056_Negative_Get_operation_to_read_resource_record_vlan_with_deny_permission(self):
        logging.info("Get_operation_to_read_resource_record_vlan")
        response1 = ib_NIOS.wapi_request('GET', object_type="vlanview",user="user_vlan",password="infoblox")
        print response1
        logging.info(response1)
        assert  re.search(r"\[\]",response1)
        logging.info("Test Case 56 Execution Completed")
        logging.info("============================")

    @pytest.mark.run(order=57)
    def test_057_Create_New_vlan_view_with_deny_permission(self):
        logging.info("Create_New_vlan_view_with_deny_permission")
        data = {"name":"VLAN_view_te_st","start_vlan_id":100,"end_vlan_id":200}
        status,response = ib_NIOS.wapi_request('POST', object_type="vlanview", fields=json.dumps(data),user="user_vlan",password="infoblox")
        print response
        logging.info(response)
        assert status == 400 and re.search(r"You need to have Write permission for the VLAN view to add a new object of this type",response)
        logging.info("Test Case 57 Execution Completed")
    
    @pytest.mark.run(order=58)
    def test_058_Delete_permission_for_vlan_view(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="permission", params="?group=group_vlan")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[0]['_ref']
        print ref
        logging.info("Deleting the permission for vlan view")
        get_status = ib_NIOS.wapi_request('DELETE', object_type=ref)
        print get_status
        logging.info(get_status)
        read = re.search(r'200',get_status)
        for read in get_status:
            assert True
        logging.info("Test Case 58 Execution Completed")

    @pytest.mark.run(order=59)
    def test_059_Create_read_only_permission_for_vlan_view(self):
        logging.info("Create_permission_read_for_vlan_view")
        data = {"group":"group_vlan","permission":"READ","resource_type":"VLAN_VIEW"}
        response = ib_NIOS.wapi_request('POST', object_type="permission", fields=json.dumps(data))
        print response
        logging.info(response)
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        logging.info("Test Case 59 Execution Completed")

    @pytest.mark.run(order=60)
    def test_060_Get_operation_to_read_vlan_with_read_permission(self):
        logging.info("Get_operation_to_read_vlan_view")
        response1 = ib_NIOS.wapi_request('GET', object_type="vlanview", params="?name=default", user="user_vlan",password="infoblox")
        print response1
        logging.info(response1)
        assert  re.search(r"vlanview",response1)
        logging.info("Test Case 60 Execution Completed")
        logging.info("============================")

    @pytest.mark.run(order=61)
    def test_061_Create_New_vlan_view_with_READ_permission(self):
        logging.info("Create_New_vlan_view_with_deny_permission")
        data = {"name":"VLAN_view_te_st","start_vlan_id":100,"end_vlan_id":200}
        status,response = ib_NIOS.wapi_request('POST', object_type="vlanview", fields=json.dumps(data),user="user_vlan",password="infoblox")
        print response
        logging.info(response)
        assert status == 400 and re.search(r"You need to have Write permission for the VLAN view to add a new object of this type",response)
        logging.info("Test Case 61 Execution Completed")

    @pytest.mark.run(order=62)
    def test_062_Modify_permission_for_vlan_view_from_read_to_write(self):
        data = {"group": "group_vlan"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="permission", fields=json.dumps(data))
        logging.info(get_ref)
        res1 = json.loads(get_ref)
        ref = json.loads(get_ref)[-1]['_ref']
        print ref
        logging.info("Modify_permission_for_vlan_view_from_read_to_write")
        data = {"permission": "WRITE"}
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
        print response
        logging.info(response)
        read  = re.search(r'200',response)
        for read in  response:
            assert True
        logging.info("Test Case 62 Execution Completed")
        logging.info("============================")

    @pytest.mark.run(order=63)
    def test_063_create_vlanview_with_write_permission(self):
        data = {"name":"VLAN_view_permission","start_vlan_id":100,"end_vlan_id":200}
        response=ib_NIOS.wapi_request('POST',object_type ="vlanview", user="user_vlan",password="infoblox",fields=json.dumps(data))
        display_msg(response)
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        display_msg("Test Case 63 Execution Completed")


    @pytest.mark.run(order=64)
    def test_064_Create_admin_group_permission_as_deny_for_vlanrange(self):
        data = {"group":"group_vlan","permission":"DENY","resource_type":"VLAN_RANGE"}
        response = ib_NIOS.wapi_request('POST', object_type="permission", fields=json.dumps(data))
        display_msg(response)
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        display_msg("Test Case 64 Execution Completed")

    @pytest.mark.run(order=65)
    def test_065_Get_operation_to_read_vlanrange_with_deny_permission_negative(self):
        logging.info("Get_operation_to_read_vlanrange")
        response1 = ib_NIOS.wapi_request('GET', object_type="vlanrange",user="user_vlan",password="infoblox")
        print response1
        logging.info(response1)
        assert  re.search(r"\[\]",response1)
        logging.info("Test Case 102 Execution Completed")
        logging.info("============================")

    @pytest.mark.run(order=66)
    def test_066_Create_New_vlanrange_with_deny_permission(self):
        logging.info("Create_New_vlanrange_with_deny_permission")
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="VLAN_view_permission":
                ref=i["_ref"]
        data = {"vlan_view":ref,"name": "VLAN_range_permission","start_vlan_id":101,"end_vlan_id":155,"comment":"test comment"}
        status,response = ib_NIOS.wapi_request('POST',object_type="vlanrange",  fields=json.dumps(data),user="user_vlan",password="infoblox")
        display_msg(response)
        assert re.search(r"You need to have Write permission for the VLAN range to add a new object of this type",response)
        logging.info("Test Case 66 Execution Completed")


            
    @pytest.mark.run(order=67)
    def test_067_Delete_permission_for_vlanrange(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="permission", params="?group=group_vlan")
        logging.info(get_ref)
        res = json.loads(get_ref)
        for temp in res:
            if temp["resource_type"]=="VLAN_RANGE":
                ref=temp["_ref"]
        print ref
        logging.info("Deleting the permission for vlan range")
        get_status = ib_NIOS.wapi_request('DELETE', object_type=ref)
        print get_status
        logging.info(get_status)
        read = re.search(r'200',get_status)
        for read in get_status:
            assert True
        logging.info("Test Case 67 Execution Completed")

    @pytest.mark.run(order=68)
    def test_068_Create_permission_read_for_vlanrange(self):
        logging.info("Create_permission_read_for_vlanrange")
        data = {"group":"group_vlan","permission":"READ","resource_type":"VLAN_RANGE"}
        response = ib_NIOS.wapi_request('POST', object_type="permission", fields=json.dumps(data))
        print response
        logging.info(response)
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        logging.info("Test Case 68 Execution Completed")

    @pytest.mark.run(order=69)
    def test_069_Get_operation_to_read_vlan_with_read_permission(self):
        logging.info("Get_operation_to_read_vlan")
        response1 = ib_NIOS.wapi_request('GET', object_type="vlanrange", params="?name=VLAN_range3", user="user_vlan",password="infoblox")
        print response1
        logging.info(response1)
        assert  re.search(r"vlanrange",response1)
        logging.info("Test Case 69 Execution Completed")
        logging.info("============================")

    @pytest.mark.run(order=70)
    def test_070_Create_New_vlan_range_with_READ_permission(self):
        logging.info("Create_New_vlan_view_with_READ_permission")
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="VLAN_view_permission":
                ref=i["_ref"]
        data = {"vlan_view":ref,"name": "VLAN_range_permission","start_vlan_id":101,"end_vlan_id":155,"comment":"test comment"}
        status,response = ib_NIOS.wapi_request('POST',object_type="vlanrange",  fields=json.dumps(data),user="user_vlan",password="infoblox")
        print response
        logging.info(response)
        assert status == 400 and re.search(r"You need to have Write permission for the VLAN range to add a new object of this type",response)
        logging.info("Test Case 70 Execution Completed")

    @pytest.mark.run(order=71)
    def test_071_Modify_permission_for_vlan_range_from_read_to_write(self):
        data = {"group": "group_vlan","resource_type":"VLAN_RANGE"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="permission", fields=json.dumps(data))
        logging.info(get_ref)
        res1 = json.loads(get_ref)
        ref = json.loads(get_ref)[0]['_ref']
        print ref
        logging.info("Modify_permission_for_vlan_range_from_read_to_write")
        data = {"permission": "WRITE","resource_type":"VLAN_RANGE"}
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
        print response
        logging.info(response)
        read  = re.search(r'200',response)
        for read in  response:
            assert True
        logging.info("Test Case 71 Execution Completed")
        logging.info("============================")

    @pytest.mark.run(order=72)
    def test_072_create_vlanrange_with_write_permission(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="VLAN_view_permission":
                ref=i["_ref"]
        data = {"vlan_view":ref,"name": "VLAN_range_permission","start_vlan_id":101,"end_vlan_id":155,"comment":"test comment"}
        response = ib_NIOS.wapi_request('POST',object_type="vlanrange",  fields=json.dumps(data),user="user_vlan",password="infoblox")
        display_msg(response)
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        display_msg("Test Case 72 Execution Completed")

    @pytest.mark.run(order=73)
    def test_073_Create_admin_group_permission_as_deny_for_vlanobject(self):
        data = {"group": "group_vlan", "permission": "DENY", "resource_type": "VLAN_OBJECTS"}
        response = ib_NIOS.wapi_request('POST', object_type="permission", fields=json.dumps(data))
        display_msg(response)
        read = re.search(r'201', response)
        for read in response:
            assert True
        display_msg("Test Case 73 Execution Completed")

    @pytest.mark.run(order=74)
    def test_074_Negative_Get_operation_to_read_vlanobject_with_deny_permission(self):
        logging.info("Get_operation_to_read_vlanrange")
        response1 = ib_NIOS.wapi_request('GET', object_type="vlan", user="user_vlan", password="infoblox")
        print response1
        logging.info(response1)
        assert re.search(r"\[\]", response1)
        logging.info("Test Case 74 Execution Completed")
        logging.info("============================")

    @pytest.mark.run(order=75)
    def test_075_Create_New_vlanobject_with_deny_permission(self):
        logging.info("Create_New_vlanrange_with_deny_permission")
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview")
        res = json.loads(get_ref)
        for i in res:
            if i["name"] == "VLAN_view":
                ref = i["_ref"]
        data = {"parent": ref, "name": "VLAN_id1", "id": 199, "reserved": True}
        status,post_ref = ib_NIOS.wapi_request('POST', object_type="vlan",user="user_vlan", password="infoblox", fields=json.dumps(data))
        assert re.search(r"You need to have Write permission for the VLAN object to add a new object of this type.",post_ref)
        logging.info("Test Case 75 Execution Completed")

    @pytest.mark.run(order=76)
    def test_076_Delete_permission_for_vlanrange(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="permission", params="?group=group_vlan")
        logging.info(get_ref)
        res = json.loads(get_ref)
        for temp in res:
            if temp["resource_type"]=="VLAN_OBJECTS":
                ref=temp["_ref"]
        print ref
        logging.info("Deleting the permission for vlan objects")
        get_status = ib_NIOS.wapi_request('DELETE', object_type=ref)
        print get_status
        logging.info(get_status)
        read = re.search(r'200', get_status)
        for read in get_status:
            assert True
        logging.info("Test Case 76 Execution Completed")

    @pytest.mark.run(order=77)
    def test_077_Create_read_only_permission_for_vlan_objects(self):
        logging.info("Create_permission_read_for_vlanrange")
        data = {"group": "group_vlan", "permission": "READ", "resource_type": "VLAN_OBJECTS"}
        response = ib_NIOS.wapi_request('POST', object_type="permission", fields=json.dumps(data))
        print response
        logging.info(response)
        read = re.search(r'201', response)
        for read in response:
            assert True
        logging.info("Test Case 77 Execution Completed")

    @pytest.mark.run(order=78)
    def test_078_Get_operation_for_vlan_objects_with_read_permission(self):
        logging.info("Get_operation_to_read_vlan")
        response1 = ib_NIOS.wapi_request('GET', object_type="vlan", params="?name=VLAN_id1", user="user_vlan",
                                         password="infoblox")
        print response1
        logging.info(response1)
        assert re.search(r"VLAN_id1", response1)
        logging.info("Test Case 78 Execution Completed")
        logging.info("============================")

    @pytest.mark.run(order=79)
    def test_079_Negative_Create_New_vlanid_with_READ_permission(self):
        logging.info("Create_New_vlan_view_with_READ_permission")
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview")
        res = json.loads(get_ref)
        for i in res:
            if i["name"] == "VLAN_view":
                ref = i["_ref"]
        data = {"parent": ref, "name": "VLAN_id1", "id": 159, "reserved": True, "contact": "879220", "department": "ng",
                "description": "descn"}
        status, post_ref= ib_NIOS.wapi_request('POST', object_type="vlan", fields=json.dumps(data),user="user_vlan", password="infoblox")
        assert re.search(r"You need to have Write permission for the VLAN object to add a new object of this type.",post_ref)
        logging.info("Test Case 79 Execution Completed")

    @pytest.mark.run(order=80)
    def test_080_Modify_permission_for_vlan_objects_from_read_to_write(self):
        data = {"group": "group_vlan", "resource_type": "VLAN_OBJECTS"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="permission", fields=json.dumps(data))
        logging.info(get_ref)
        res1 = json.loads(get_ref)
        ref = json.loads(get_ref)[0]['_ref']
        print ref
        logging.info("Modify_permission_for_vlan_objects_from_read_to_write")
        data = {"permission": "WRITE", "resource_type": "VLAN_OBJECTS"}
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
        print response
        logging.info(response)
        read = re.search(r'200', response)
        for read in response:
            assert True
        logging.info("Test Case 80 Execution Completed")
        logging.info("============================")

    @pytest.mark.run(order=81)
    def test_081_create_vlan_objects_write_permission(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview")
        res = json.loads(get_ref)
        for i in res:
            if i["name"] == "VLAN_view":
                ref = i["_ref"]
        data = {"parent": ref, "name": "VLAN_id1", "id": 199, "reserved": True, "contact": "879220", "department": "ng","description": "descn"}
        response= ib_NIOS.wapi_request('POST', object_type="vlan", fields=json.dumps(data),user="user_vlan", password="infoblox")
        read = re.search(r'201', response)
        for read in response:
            assert True
        display_msg("Test Case 81 Execution Completed")


    @pytest.mark.run(order=82)
    def test_082_CSV_import_and_validate_for_VLAN_view(self):
            logging.info("Upload vlan view file")
            dir_name = "csv/"
            base_filename = "csv_import_vlanview.csv"
            token =generate_token_from_file(dir_name, base_filename)
            #data = {"token": token, "overwrite": True}
            print "========================="
            print token
            print "========================="
            data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"OVERRIDE"}
            response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),
                                                                    params="?_function=csv_import")
            sleep(30)
            logging.info(response)
            print response
            read = re.search(r'201', response)
            data = {"objtype": "vlanview", "search_string": "csv_import"}
            get_ref = ib_NIOS.wapi_request('GET', object_type="search", fields=json.dumps(data))
            res_json = json.loads(get_ref)
            print res_json
            assert data["search_string"] == res_json[0]["name"]
            for read in response:
                assert True
            logging.info("Test Case 82 Execution Completed")
            logging.info("============================")


    @pytest.mark.run(order=83)
    def test_083_CSV_import_and_validate_for_VLAN_range_vlanid_under_vlan_view(self):
            logging.info("Upload vlan view file")
            dir_name = "csv/"
            base_filename = "csv_import_vlanrange_id.csv"
            token =generate_token_from_file(dir_name, base_filename)
            #data = {"token": token, "overwrite": True}
            print "========================="
            print token
            print "========================="
            data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"OVERRIDE"}
            response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),
                                            params="?_function=csv_import")
            sleep(30)
            logging.info(response)
            print response
            read = re.search(r'201', response)
            for read in response:
                assert True
            data = {"objtype": "vlanrange", "search_string": "csv_range"}
            get_ref = ib_NIOS.wapi_request('GET', object_type="search", fields=json.dumps(data))
            res_json = json.loads(get_ref)
            print res_json
            assert data["search_string"] == res_json[0]["name"]
            logging.info("Test Case 83 Execution Completed")
            logging.info("============================")

    @pytest.mark.run(order=84)
    def test_084_CSV_import_and_validate_for_vlanid_under_vlan_range(self):
            logging.info("Upload vlan view file")
            dir_name = "csv/"
            base_filename = "csv_import_id_under_range.csv"
            token =generate_token_from_file(dir_name, base_filename)
            #data = {"token": token, "overwrite": True}
            print "========================="
            print token
            print "========================="
            data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"OVERRIDE"}
            response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),
                                            params="?_function=csv_import")
            sleep(30)
            logging.info(response)
            print response
            read = re.search(r'201', response)
            for read in response:
                assert True
            data = {"objtype": "vlan", "search_string": "csv_vlan_id"}
            get_ref = ib_NIOS.wapi_request('GET', object_type="search", fields=json.dumps(data))
            res_json = json.loads(get_ref)
            print res_json
            assert data["search_string"] == res_json[0]["name"]
            logging.info("Test Case 84 Execution Completed")
            logging.info("============================")

    @pytest.mark.run(order=85)
    def test_085_add_vlanview_with_overlapping(self):
        logging.info("Create Vlan View")
        data = {"name": "VLAN_view_overlapping", "start_vlan_id": 1, "end_vlan_id": 100,"allow_range_overlapping":True}
        response = ib_NIOS.wapi_request('POST', object_type="vlanview", fields=json.dumps(data))
        logging.info(response)
        print response
        read = re.search(r'201', response)
        for read in response:
            assert True
        display_msg("==" * 50)
        display_msg("TEST 85 COMPLETED")

    @pytest.mark.run(order=86)
    def test_086_create_Vlan_range_under_vlan_view(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview")
        res = json.loads(get_ref)
        for i in res:
            if i["name"] == "VLAN_view_overlapping":
                ref = i["_ref"]
        data = {"vlan_view": ref, "name": "VLAN_range_override1", "start_vlan_id": 1, "end_vlan_id": 50,
                "vlan_name_prefix": "", "comment": "test comment"}
        post_ref = ib_NIOS.wapi_request('POST', object_type="vlanrange", fields=json.dumps(data))
        ref = json.loads(post_ref)
        res = ib_NIOS.wapi_request('GET', object_type=ref)
        print res
        res_json = json.loads(res)
        assert data["name"] == res_json["name"] and data["start_vlan_id"] == res_json["start_vlan_id"] and data[
            "end_vlan_id"] == res_json["end_vlan_id"]
        display_msg("==" * 50)
        display_msg("TEST 86 COMPLETED")

    @pytest.mark.run(order=87)
    def test_087_create_overlapping_Vlan_range_under_vlan_view(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview")
        res = json.loads(get_ref)
        for i in res:
            if i["name"] == "VLAN_view_overlapping":
                ref = i["_ref"]
        data = {"vlan_view": ref, "name": "VLAN_range_override2", "start_vlan_id": 1, "end_vlan_id": 60,
                "vlan_name_prefix": "", "comment": "test comment"}
        post_ref = ib_NIOS.wapi_request('POST', object_type="vlanrange", fields=json.dumps(data))
        ref = json.loads(post_ref)
        res = ib_NIOS.wapi_request('GET', object_type=ref)
        print res
        res_json = json.loads(res)
        assert data["name"] == res_json["name"] and data["start_vlan_id"] == res_json["start_vlan_id"] and data[
            "end_vlan_id"] == res_json["end_vlan_id"]
        display_msg("==" * 50)
        display_msg("TEST 87 COMPLETED")

    @pytest.mark.run(order=88)
    def test_088_Negative_create_overlapping_Vlan_range_under_vlan_view(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview")
        res = json.loads(get_ref)
        for i in res:
            if i["name"]=="VLAN_view":
                ref=i["_ref"]
        data = {"vlan_view":ref,"name": "VLAN_range2","start_vlan_id":150,"end_vlan_id":200,"vlan_name_prefix":"","comment":"test comment"}
        status,post_ref = ib_NIOS.wapi_request('POST',object_type="vlanrange",  fields=json.dumps(data))
        assert re.search(r"Cannot create VLAN range 'VLAN_range2' with IDs 150...200 because it will overlap the VLAN range ", post_ref)
        display_msg("=="*50)
        display_msg("TEST 88 COMPLETED")
    
    @pytest.mark.run(order=89)
    def test_089_search_vlan_view_using_global_search(self):
        data={"objtype":"vlanview","search_string":"VLAN_view"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="search",fields=json.dumps(data) )
        res_json = json.loads(get_ref)
        print res_json
        assert  data["search_string"]==res_json[0]["name"]
        display_msg("==" * 50)
        display_msg("TEST 89 COMPLETED")

    @pytest.mark.run(order=90)
    def test_090_search_vlan_range_using_global_search(self):
        data={"objtype":"vlanrange","search_string":"VLAN_range3"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="search",fields=json.dumps(data) )
        res_json = json.loads(get_ref)
        print res_json
        assert  data["search_string"]==res_json[0]["name"]
        display_msg("==" * 50)
        display_msg("TEST 90 COMPLETED")

    @pytest.mark.run(order=91)
    def test_091_search_vlan_id_using_global_search(self):
        data={"objtype":"vlan","search_string":"VLAN_id1"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="search",fields=json.dumps(data) )
        res_json = json.loads(get_ref)
        print res_json
        assert  data["search_string"]==res_json[0]["name"]
        display_msg("==" * 50)
        display_msg("TEST 91 COMPLETED")

    @pytest.mark.run(order=92)
    def test_092_modify_vlan_id_range_of_vlan_view(self):
        data={"objtype":"vlanview","search_string":"VLAN_view_overlapping"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="search",fields=json.dumps(data) )
        res_json = json.loads(get_ref)
        print res_json
        ref=res_json[0]["_ref"]
        data = {"start_vlan_id":1,"end_vlan_id":200}
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
        print response
        logging.info(response)
        read  = re.search(r'200',response)
        for read in  response:
            assert True
        display_msg("==" * 50)
        display_msg("TEST 92 COMPLETED")

    @pytest.mark.run(order=93)
    def test_093_modify_vlan_range_id_values(self):
        data = {"objtype": "vlanview", "search_string": "VLAN_view_overlapping"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="search", fields=json.dumps(data))
        res_json = json.loads(get_ref)
        print res_json
        ref = res_json[0]["_ref"]
        data = {"objtype": "vlanrange", "search_string": "VLAN_range_override2"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="search", fields=json.dumps(data))
        res_json = json.loads(get_ref)
        print res_json
        res1 = res_json[0]["_ref"]
        data = {"vlan_view": ref, "start_vlan_id": 1, "end_vlan_id": 80}
        response = ib_NIOS.wapi_request('PUT', ref=res1, fields=json.dumps(data))
        print response
        logging.info(response)
        read = re.search(r'200', response)
        for read in response:
            assert True
        display_msg("==" * 50)

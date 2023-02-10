#Standalone 1415 with IPV6 Config
#grid_ipv6_ip need to be added in config
#config grid with only lan ipv4 and ipv6
import re
import config
import pytest
import unittest
import logging
import subprocess
import os
import json
import ib_utils.ib_NIOS as ib_NIOS
import commands
import json, ast
import requests
from time import sleep as sleep
import pexpect
import paramiko
import time
import sys
import socket
from paramiko import client
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv
from ib_utils.start_bird import Start_bird_process as bird

host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)

def restart_the_grid():
    logging.info("Restaring the grid")
    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data))
    sleep(30)
    print("Restrting the grid")


def show_BGP_data():
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show bgp config')
        child.expect('.')
        child.sendline('\n')
        child.expect('Infoblox >')
        output= child.before
        child.sendline('exit')
        return output


class Network(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_001_add_BGP_configuration(self):
        directory=os.getcwd()
        bird("bird6",["bgp"],directory+"/arun.json")
        logging.info("Add BGP config")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        print (ref1)
        data = {"bgp_as": [{"as": 221,"holddown": 16,"keepalive": 4,"link_detect": False,"neighbors": [{"authentication_mode": "NONE","enable_bfd": False,"interface": "LAN_HA","multihop": False,"multihop_ttl": 255,"neighbor_ip":host_ip,"remote_as": 331}]}]}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
        sleep(20)
        logging.info(response)
        print (response)
        sleep(20)
        print("BGP is enabled on the member")


    @pytest.mark.run(order=2)
    def test_002_add_Anycast_configuration(self):
        logging.info("getting member properties")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member")
        logging.info(get_ref)
        print get_ref
        res = json.loads(get_ref)
        print res
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"additional_ip_list":[{"anycast": True,"enable_bgp": True,"enable_ospf": False,"interface": "LOOPBACK","ipv6_network_setting": {"cidr_prefix":128,"enabled":True,"virtual_ip":"2:2:2::3"}}]}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        print response
        sleep(150)
        print("Anycast is enabled on the Grid member")

    @pytest.mark.run(order=3)
    def test_003_enable_mgmt_port_for_dns(self):
        ref=ib_NIOS.wapi_request('GET', object_type="member:dns")
        ref=json.loads(ref)[0]['_ref']
        data={"use_lan_ipv6_port":True}
        ref1=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
        logging.info (ref1)

    @pytest.mark.run(order=4)
    def test_004_add_Anycast_ip_in_member(self):
        logging.info("getting member properties")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        logging.info(get_ref)
        print get_ref
        res = json.loads(get_ref)
        print res
        ref1 = json.loads(get_ref)[0]['_ref']
        #data={"additional_ip_list_struct":[{"ip_address":"2:2:2::3"}],"use_mgmt_port":True,"use_mgmt_ipv6_port":True,"use_lan_ipv6_port":True}
        data={"additional_ip_list_struct":[{"ip_address":"2:2:2::3"}]}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
        restart_the_grid()
        sleep(50)
        print("Anycast ip is added on the Grid member")

    @pytest.mark.run(order=5)
    def test_005_Start_DNS_Service(self):
        logging.info("Start DNS Service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        logging.info(get_ref)
        res = json.loads(get_ref)
        for ref in res:
            ref1 = ref["_ref"]
            logging.info("Modify a enable_dns")
            data = {"enable_dns": True}
            response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
            print response
            sleep(20)
            logging.info(response)
            read  = re.search(r'200',response)
            for read in  response:
                assert True
        logging.info("Test Case 4 Execution Completed")

    @pytest.mark.run(order=6)
    def test_006_Validate_DNS_service_Enabled(self):
        logging.info("Validate DNs Service is enabled")
        get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns")
        logging.info(get_tacacsplus)
        res = json.loads(get_tacacsplus)
        print res
        for i in res:
            print i
            logging.info("found")
            assert i["enable_dns"] == True
        logging.info("Test Case 5 Execution Completed")
        logging.info("============================")


    @pytest.mark.run(order=7)
    def test_007_validate_BGP_data(self):
        time.sleep(20)
        data=show_BGP_data()
        result=re.search("No BGP network exists",data)
        if result!=None:
            assert False
        else:
            result=re.search(".*ipv6 prefix-list DEFAULT seq 5 permit ::/0.*",data)
            if (result != None):
                assert True
                print ("Test case 6 passed")
            else:
                assert False
                print ("Test case 6 failed")
   
    @pytest.mark.run(order=4)
    def test_008_Remove_Anycast_ip_in_member(self):
        logging.info("Cleaning up the added Anycast IP")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        logging.info(get_ref)
        print get_ref
        res = json.loads(get_ref)
        print res
        ref1 = json.loads(get_ref)[0]['_ref']
        data={"additional_ip_list_struct":[]}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
        print response
        print("Anycast ip is removed on the Grid member")

    @pytest.mark.run(order=2)
    def test_009_remove_Anycast_configuration(self):
        logging.info("Remove Anycast configuratpn")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"additional_ip_list":[]}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        print response
        sleep(150)
        print("Anycast is enabled on the Grid member")

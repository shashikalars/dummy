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

global host_ip
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

class SSH:
    client=None

    def __init__(self,address):
        logging.info ("connecting to server \n : ", address)
        self.client=client.SSHClient()
        self.client.set_missing_host_key_policy(client.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        self.client.connect(address, username='root', pkey = mykey)

    def send_command(self,command):
        if(self.client):
            stdin, stdout, stderr = self.client.exec_command(command)
            result=stdout.read()
            return result

def kill_process(command):
    connection=SSH(str(config.grid_vip))
    check_pid="pidof "+command 
    print (check_pid)
    check_pid=connection.send_command(check_pid)
    print (check_pid)
    command1="kill -9 "+check_pid
    check_pid=connection.send_command(command1)
    print (check_pid)


def show_BGP_data():
    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
    child.logfile=sys.stdout
    child.expect('password:')
    child.sendline('infoblox')
    child.expect('Infoblox >')
    child.sendline('show bgp neighbor')
    child.expect('>')
    output= child.before
    child.sendline('exit')
    return output


class Network(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_001_start_bird(self):
        directory=os.getcwd()
        bird("bird",["bgp"],directory+"/arun.json")
    

    @pytest.mark.run(order=2)
    def test_002_add_BGP_configuration(self):
        logging.info("Add BGP config")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        print (ref1)
        data = {"bgp_as": [{"as": 221,"holddown": 16,"keepalive": 4,"link_detect": False,"neighbors": [{"authentication_mode": "NONE","enable_bfd": False,"interface": "LAN_HA","multihop": False,"multihop_ttl": 255,"neighbor_ip": host_ip,"remote_as": 331}]}]}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
        if type(response)!=tuple:
            print("Anycast ip is added on the Grid member")
            assert True
            sleep(50)
        else:
            assert False


    @pytest.mark.run(order=1)
    def test_003_add_Anycast_configuration(self):
        logging.info("getting member properties")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
        logging.info(get_ref)
        print (get_ref)
        res = json.loads(get_ref)
        print (res)
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"additional_ip_list":[{"anycast": True,"enable_bgp": True,"enable_ospf": False,"interface": "LOOPBACK","ipv4_network_setting": {"address": "1.1.1.2","dscp": 0,"primary": False,"subnet_mask": "255.255.255.255","use_dscp": False}}]}

        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        print response
        if type(response)!=tuple:
            print("Anycast ip is added on the Grid member")
            assert True
            sleep(300)
        else:
            assert False

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
        data={"additional_ip_list_struct":[{"ip_address":"1.1.1.2"}]}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
        print response
        sleep(30)
        print("Anycast ip is added on the Grid member")

    @pytest.mark.run(order=5)
    def test_005_Start_DNS_Service(self):
        restart_the_grid()
        logging.info("Start DNS Service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        logging.info(get_ref)
        res = json.loads(get_ref)
        for ref in res:
            ref1 = ref["_ref"]
            logging.info("Modify a enable_dns")
            data = {"enable_dns": True}
            response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
            sleep(20)
            logging.info(response)
            read  = re.search(r'200',response)
            for read in  response:
                assert True
        logging.info("Test Case 5 Execution Completed")

    @pytest.mark.run(order=6)
    def test_006_Validate_DNS_service_Enabled(self):
        logging.info("Validate DNs Service is enabled")
        get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns")
        logging.info(get_tacacsplus)
        res = json.loads(get_tacacsplus)
        for i in res:
            logging.info("found")
            assert i["enable_dns"] == True
        logging.info("Test Case 6 Execution Completed")
        logging.info("============================")


    @pytest.mark.run(order=7)
    def test_007_validate_BGP_data(self):
        time.sleep(20)
        data=show_BGP_data()
        result=re.search("No BGP network exists",data)
        if result!=None:
            assert False
        else:
            get_ref = ib_NIOS.wapi_request('GET', object_type="member?_return_fields=bgp_as", grid_vip=config.grid_vip)
            get_ref=json.loads(get_ref)
            local=get_ref[0]["bgp_as"][0]["as"]
            remote=get_ref[0]["bgp_as"][0]["neighbors"][0]["remote_as"]

            result=re.search("BGP neighbor is "+str(host_ip)+", remote AS "+str(remote)+", local AS "+str(local),data)
            if (result != None):
                assert True
                print ("Test case 7 passed")
            else:
                assert False
                print ("Test case 7 failed")

    @pytest.mark.run(order=8)
    def test_008_start_Infoblox_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        #log("start","/infoblox/var/infoblox",config.grid_vip)
        logging.info("test case 8  passed")
    
    @pytest.mark.run(order=9)
    def test_009_forced_restart_dns(self):
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        data={"restart_option":"FORCE_RESTART","service_option":"DNS"}
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data))
        time.sleep(120)
        print ("Restarting the grid forcefully ")


    @pytest.mark.run(order=10)
    def test_010_stop_Infoblox_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        #log("start","/infoblox/var/infoblox",config.grid_vip)
        logging.info("test case 10  passed")
    
    @pytest.mark.run(order=11)
    def test_011_validate_Infoblox_Messages(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="Starting bgpd process..."#Domain Name White List update completed in var/log/messages
        #LookFor="Arun|Kumar"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        if logs==None:
            logging.info("Test Case 11 Execution Completed")
            assert True
        else:
            logging.info("Test Case 11 Execution failed")
            assert False
    

    @pytest.mark.run(order=12)
    def test_012_start_Infoblox_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("test case 12  passed")
    
    @pytest.mark.run(order=13)
    def test_013_restart_dns(self):
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        data={"restart_option":"RESTART_IF_NEEDED","service_option":"DNS"}
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data))
        time.sleep(120)
        print ("Restarting the grid forcefully ")


    @pytest.mark.run(order=14)
    def test_014_stop_Infoblox_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("test case 14  passed")

    @pytest.mark.run(order=15)
    def test_015_validate_Infoblox_Messages(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="Starting bgpd process..."#Domain Name White List update completed in var/log/messages
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        if logs==None:
            logging.info("Test Case 15 Execution Completed")
            assert True
        else:
            logging.info("Test Case 15 Execution failed")
            assert False

    @pytest.mark.run(order=16)
    def test_016_start_Infoblox_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("test case 16  passed")
    
    @pytest.mark.run(order=17)
    def test_017_kill_named_process(self):
        kill_process("named")
        sleep(30)

    @pytest.mark.run(order=18)
    def test_018_stop_Infoblox_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("test case 18  passed")
    
    @pytest.mark.run(order=19)
    def test_019_validate_Infoblox_Messages(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="Starting bgpd process..."#Domain Name White List update completed in var/log/messages
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        if logs!=None:
            logging.info("Test Case 19 Execution Completed")
            assert True
        else:
            logging.info("Test Case 19 Execution failed")
            assert False

    @pytest.mark.run(order=20)
    def test_020_start_Infoblox_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("test case 20  passed")
    
    @pytest.mark.run(order=21)
    def test_021_kill_zebra_process(self):
        kill_process("zebra")
        sleep(120)
    
    @pytest.mark.run(order=22)
    def test_022_stop_Infoblox_Messages_logs(self):
        logging.info("Starting Infoblox Messages Logs")
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("test case 22  passed")

    @pytest.mark.run(order=23)
    def test_023_validate_Infoblox_Messages(self):
        logging.info("Validating Infoblox Messages Logs")
        LookFor="Starting bgpd process..."#Domain Name White List update completed in var/log/messages
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        if logs!=None:
            logging.info("Test Case 23 Execution Completed")
            assert True
        else:
            logging.info("Test Case 23 Execution failed")
            assert False

    @pytest.mark.run(order=4)
    def test_024_Remove_Anycast_ip_in_member(self):
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
    def test_025_add_Anycast_configuration(self):
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

    







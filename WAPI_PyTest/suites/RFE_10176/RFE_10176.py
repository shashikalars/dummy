#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
# Grid Set up required:                                                     #
#  1. SA grid + HA + Flex                                                   #
#  2. Licenses : Grid,DNS,RPZ license,DCA,DTC                               #
#############################################################################
import os
import re
import config
import pytest
import unittest
import logging
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import shlex
from time import sleep
from subprocess import Popen, PIPE
import pexpect
import paramiko
from scapy import *
from scapy.utils import RawPcapReader
from scapy.all import *
import shutil
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv
#from ib_utils.Bgp_and_OSPF_new import Start_bird_process,get_user_input

logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="RFE_10176.log" ,level=logging.DEBUG,filemode='w')


def remove():
    data="rm /home/"+config.client_username+"/.ssh/known_hosts"
    ret_code = os.system(data)
    if ret_code == 0:
        print("Cleared known hosts file")
    else:
        print("Couldnt clear known hosts file")

def set_cli_anycast_restart_on(ip_address=config.grid_vip):
    remove()
    print("\n============================================\n")
    print("setting restart anycast with dns restart on")
    print("\n============================================\n")
    try:
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+ip_address)
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')

        child.sendline('set restart_anycast_with_dns_restart on')

        child.expect('>')
        child.sendline('show restart_anycast_with_dns_restart')
        child.expect('>')

        if 'restart_anycast_with_dns_restart is set to "on"' in child.before:
            child.close()
            assert True
        else:
            raise(Exception)

    except Exception as e:
        child.close()
        print("Failure")
        print (e)
        assert False




def set_cli_anycast_restart_off(ip_address=config.grid_vip):
    remove()
    print("\n============================================\n")
    print("setting restart_anycast_with_dns_restart off")
    print("\n============================================\n")
    try:
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+ip_address)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set restart_anycast_with_dns_restart off')
        child.expect('>')
        child.sendline('show restart_anycast_with_dns_restart')
        child.expect('>')

        if 'restart_anycast_with_dns_restart is set to "off"' in child.before:
            child.close()
            assert True
        else:
            raise(Exception)

    except Exception as e:
        child.close()
        print("Failure")
        print (e)
        assert False

def check_able_to_login_appliances(ip_address=config.grid_vip):
    remove()
    for i in range(5):
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+ip_address)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')

            child.sendline('show version')

            child.expect('>')

            if 'Version :' in child.before:
                child.close()
                print("\n************Appliances is Working************\n ")
                sleep(60)
                assert True
                break
            else:

                raise(Exception)

        except Exception as e:
            child.close()
            print(e)
            sleep(20)
            continue
            print("Failure")

            assert False

def check_able_to_login_appliances_ha(ip):
    remove()
    for i in range(5):
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+ip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')

            child.sendline('show version')

            child.expect('>')

            if 'Version :' in child.before:
                child.close()
                print("\n************Appliances is Working************\n ")
                sleep(60)
                assert True
                break
            else:

                raise(Exception)

        except Exception as e:
            child.close()
            print(e)
            sleep(20)
            continue
            print("Failure")
            assert False


def get_ha_active_passive():
    remove()
    try:
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.HA_ip1)
        child.expect('#')
        child.sendline('cat /infoblox/var/ha_status.txt')
        child.expect('#')
        a = child.before
        if 'Active' in a:
            child.close()
            return config.HA_ip1,config.HA_ip2
        elif 'Passive' in child.before:
            child.close()
            return config.HA_ip2,config.HA_ip1
        else:
            child.close()
            raise Exception("Couldnt find the HA status")
    except Exception as e:
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.HA_ip2)
            child.expect('#')
            child.sendline('cat /infoblox/var/ha_status.txt')
            child.expect('#')
            a = child.before
            if 'Active' in a:
                child.close()
                return config.HA_ip1,config.HA_ip2
            elif 'Passive' in child.before:
                child.close()
                return config.HA_ip2,config.HA_ip1
            else:
                child.close()
                raise Exception("Couldnt find the HA status")
        except Exception as e:
            print e
            print("Unable to login to both HA node and passive node")
            assert False

def fetch_process_ID1(ip_address=config.grid_vip):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(ip_address, username='root', pkey = mykey)
    data="pgrep named\n"
    stdin, stdout, stderr = client.exec_command(data)
    stdout=stdout.read()
    print("process ID 1:"+str(stdout))
    pid1=stdout
    #if len(pid1)!= 0:
        #pid1 = int(pid1)

    # for i in range(5):
        # if stdout =='':
            # print("DNS does not started")
            # sleep(10)
            # data="pgrep named\n"
            # stdin, stdout, stderr = client.exec_command(data)
            # stdout=stdout.read()
            # print("process PID *******:"+str(stdout))
            # pid1=stdout
            # continue
        # else:
            # pass

    return pid1,client

def fetch_process_ID2(pid1,client):
    #Reduce sleep time
    for i in range(5):
        #print(i)
        data="pgrep named\n"
        stdout = None
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()

        pid2=stdout
        #if len(pid2)!=0:
            #pid2 = int(pid2)
        #print(pid2)
        #print("-------")
        if pid1 == pid2:
            sleep(20)
            continue
        else:
            print("procces ID 2:"+str(stdout))
            sleep(30)
            client.close()
        break

def dns_restart_services():
    print("\n============================================\n")
    print("DNS Restart Services")
    print("\n============================================\n")

    pid1,client = fetch_process_ID1(config.grid_vip)

    grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
    ref = json.loads(grid)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)

    fetch_process_ID2(pid1,client)
    print("got two different P_ID")

def dns_restart_services_normally():
    print("\n============================================\n")
    print("DNS Restart Services Normally")
    print("\n============================================\n")

    pid1,client = fetch_process_ID1(config.grid_vip)
    if pid1 =='':
        client.close()
        pid1,client = fetch_process_ID1(config.grid_vip)

    grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
    ref = json.loads(grid)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"RESTART_IF_NEEDED","service_option": "ALL"}
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)

    fetch_process_ID2(pid1,client)


def dns_start_services(fqdn=config.grid_fqdn):
    print("\n============================================\n")
    print("DNS Start Services")
    print("\n============================================\n")

    pid1,client = fetch_process_ID1(config.grid_vip)

    get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
    print(get_ref)
    res = json.loads(get_ref)
    for i in res:
        if i["host_name"] == fqdn:
            data = {"enable_dns": True}
            response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)
            print(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    print("Failure: DNS Start Services")
                    assert False
            else:
                print("Success: DNS Start Services")
                assert True

    fetch_process_ID2(pid1,client)


def dns_stop_services(fqdn=config.grid_fqdn):
    print("\n============================================\n")
    print("DNS stop Services")
    print("\n============================================\n")

    pid1,client = fetch_process_ID1(config.grid_vip)

    get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
    print(get_ref)
    res = json.loads(get_ref)
    for i in res:
        if i["host_name"] == fqdn:
            data = {"enable_dns": False}
            response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)
            print(type(response),response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    print("Failure: DNS stop Services")
                    assert False
            else:
                print("Success: DNS stop Services")
                assert True
    fetch_process_ID2(pid1,client)

def ospf_ipv4_configuration():
    print("\n============================================\n")
    print("Configuring OSFP IPV4 for member")
    print("\n============================================\n")
    sleep(30)
    check_able_to_login_appliances(config.grid_vip)
    get_ref = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=additional_ip_list')
    print(get_ref)
    for ref in json.loads(get_ref):

        data={"ospf_list": [ {
                    "area_id": "0.0.0.12",
                    "area_type": "STANDARD",
                    "authentication_type": "NONE",
                    "auto_calc_cost_enabled": True,
                    "cost": 1,
                    "dead_interval": 40,
                    "enable_bfd": False,
                    "hello_interval": 10,
                    "interface": "LAN_HA",
                    "is_ipv4": True,
                    "key_id": 1,
                    "retransmit_interval": 5,
                    "transmit_delay": 1
                }
            ]}
        response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)
        print(type(response),response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Configure OSPF ipv4 for advertising")
                assert False
        else:
            print("Success: Configure OSPF ipv4 for advertising")
            assert True



def anycast_ipv4_configuration():
    print("\n============================================\n")
    print("Configuring ipv4 Anycast IP for member")
    print("\n============================================\n")

    get_ref = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=additional_ip_list')
    #print(get_ref)
    for ref in json.loads(get_ref):
        data={"additional_ip_list": [
            {
                "anycast": True,
                "enable_bgp": False,
                "enable_ospf": True,
                "interface": "LOOPBACK",
                "ipv4_network_setting": {
                    "address": "1.3.3.3",
                    "dscp": 0,
                    "primary": False,
                    "subnet_mask": "255.255.255.255",
                    "use_dscp": False
                }
            }
        ]}
        response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: configure Anycast IP")
                assert False
        else:
            print("Success: configure Anycast IP")
            sleep(90)
            check_able_to_login_appliances(config.grid_vip)
    get_ref = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=additional_ip_list')
    print(get_ref)
    check_able_to_login_appliances(config.grid_vip)
    print("\n============================================\n")
    print("Configure IPV4 anycast IP for member DNS")
    print("\n============================================\n")
    sleep(60)
    check_able_to_login_appliances(config.grid_vip)

    get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=additional_ip_list_struct')
    print(get_ref)

    for ref in json.loads(get_ref):

        data={"additional_ip_list_struct": [{
                "ip_address": "1.3.3.3"
            }]}
        response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
        print(response)

        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Configure IPV4 anycast IP for member DNS")
                assert False
        else:
            print("Success: Configure IPV4 anycast IP for member DNS")
            assert True



def ospf_ipv6_configuration():
    print("\n============================================\n")
    print("create OSFP IVP4 & IPV6 for member ")
    print("\n============================================\n")

    get_ref = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=additional_ip_list')
    print(get_ref)
    for ref in json.loads(get_ref):

        data={"ospf_list": [
            {
                "area_id": "0.0.0.12",
                "area_type": "STANDARD",
                "authentication_type": "NONE",
                "auto_calc_cost_enabled": True,
                "cost": 1,
                "dead_interval": 40,
                "enable_bfd": False,
                "hello_interval": 10,
                "interface": "LAN_HA",
                "is_ipv4": True,
                "key_id": 1,
                "retransmit_interval": 5,
                "transmit_delay": 1
            },
            {
                "area_id": "0.0.0.12",
                "area_type": "STANDARD",
                "authentication_type": "NONE",
                "auto_calc_cost_enabled": True,
                "cost": 1,
                "dead_interval": 40,
                "enable_bfd": False,
                "hello_interval": 10,
                "interface": "LAN_HA",
                "is_ipv4": False,
                "key_id": 1,
                "retransmit_interval": 5,
                "transmit_delay": 1
            }
        ]}

        response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)

        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Configure OSPF ipv6 for advertising")
                assert False
        else:
            print("Success: Configure OSPF ipv6 for advertising")
            assert True

def anycast_ipv6_configuration():

    print("\n============================================\n")
    print("Configuring IVP4 & IPV6 Anycast IP for member")
    print("\n============================================\n")

    get_ref = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=additional_ip_list')
    print(get_ref)
    for ref in json.loads(get_ref):
        data={"config_addr_type": "BOTH",
        "additional_ip_list": [
            {
                "anycast": True,
                "enable_bgp": False,
                "enable_ospf": True,
                "interface": "LOOPBACK",
                "ipv4_network_setting": {
                    "address": "1.3.3.3",
                    "dscp": 0,
                    "primary": False,
                    "subnet_mask": "255.255.255.255",
                    "use_dscp": False
                }
            },
            {
                "anycast": True,
                "enable_bgp": False,
                "enable_ospf": True,
                "interface": "LOOPBACK",
                "ipv6_network_setting": {
                    "cidr_prefix": 128,
                    "dscp": 0,
                    "enabled": True,
                    "primary": False,
                    "use_dscp": False,
                    "virtual_ip": "3333::3331"
                }
            }
        ]}

        response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
        print(response)

        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Anycast configuration")
                assert False
        else:
            print("Success: Anycast configuration")
            sleep(90)
            check_able_to_login_appliances(config.grid_vip)

    sleep(30)
    check_able_to_login_appliances(config.grid_vip)
    sleep(30)
    print("\n============================================\n")
    print("Configure IVP4 & IPV6 anycast IP for DNS")
    print("\n============================================\n")

    get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=additional_ip_list_struct')

    print(get_ref)
    for ref in json.loads(get_ref):
        print(ref['_ref'])
        data={"use_lan_ipv6_port":True,
        "additional_ip_list_struct": [
            {
                "ip_address": "1.3.3.3"
            },
            {
                "ip_address": "3333::3331"
            }
        ]}
        response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
        print(response)

        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Configure IPV6 anycast IP for member DNS")
                assert False
        else:
            print("Success: Configure IPV6 anycast IP for member DNS")
            assert True


def bgp_configuration():
    # sleep(30)
    # check_able_to_login_appliances(config.grid_vip)
    print("\n============================================\n")
    print("Create BGP for member")
    print("\n============================================\n")

    get_ref = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=bgp_as')
    print(get_ref)
    for ref in json.loads(get_ref):

        data={"bgp_as": [
            {
                "as": 12,
                "holddown": 16,
                "keepalive": 4,
                "link_detect": False,
                "neighbors": [
                    {
                        "authentication_mode": "NONE",
                        "enable_bfd": False,
                        "interface": "LAN_HA",
                        "multihop": False,
                        "multihop_ttl": 255,
                        "neighbor_ip": config.anycast_client,
                        "remote_as": 12
                    }
                ]
            }
        ]}
        response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Configure BGP for advertising")
                assert False
        else:
            print("Success: Configure BGP for advertising")
            assert True

def anycast_bgp_ipv4_configuration():
    print("\n============================================\n")
    print("Configuring IPV4 BGP for advertising")
    print("\n============================================\n")
    sleep(30)
    check_able_to_login_appliances(config.grid_vip)
    get_ref = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=additional_ip_list')
    print(get_ref)
    for ref in json.loads(get_ref):
        data={"additional_ip_list": [
            {
                "anycast": True,
                "enable_bgp": True,
                "enable_ospf": True,
                "interface": "LOOPBACK",
                "ipv4_network_setting": {
                    "address": "1.3.3.3",
                    "dscp": 0,
                    "primary": False,
                    "subnet_mask": "255.255.255.255",
                    "use_dscp": False
                }
            },
            {
                "anycast": True,
                "enable_bgp": False,
                "enable_ospf": True,
                "interface": "LOOPBACK",
                "ipv6_network_setting": {
                    "cidr_prefix": 128,
                    "dscp": 0,
                    "enabled": True,
                    "primary": False,
                    "use_dscp": False,
                    "virtual_ip": "3333::3331"
                }
            }
        ]}
        response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Configure IPV4 BGP for advertising")
                assert False
        else:
            print("Success: Configure IPV4 BGP for advertisingn")
            sleep(90)
            check_able_to_login_appliances(config.grid_vip)


def anycast_bgp_ipv6_configuration():
    print("\n============================================\n")
    print("Configuring IPV4 and IPV6 BGP for member")
    print("\n============================================\n")
    #check_able_to_login_appliances(config.grid_vip)
    get_ref = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=additional_ip_list')
    print(get_ref)
    for ref in json.loads(get_ref):
        data={"additional_ip_list": [
            {
                "anycast": True,
                "enable_bgp": True,
                "enable_ospf": True,
                "interface": "LOOPBACK",
                "ipv4_network_setting": {
                    "address": "1.3.3.3",
                    "dscp": 0,
                    "primary": False,
                    "subnet_mask": "255.255.255.255",
                    "use_dscp": False
                }
            },
            {
                "anycast": True,
                "enable_bgp": True,
                "enable_ospf": True,
                "interface": "LOOPBACK",
                "ipv6_network_setting": {
                    "cidr_prefix": 128,
                    "dscp": 0,
                    "enabled": True,
                    "primary": False,
                    "use_dscp": False,
                    "virtual_ip": "3333::3331"
                }
            }
        ]}
        response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Configure IPV6 BGP for advertising")
                assert False
        else:
            print("Success: Configure IPV6 BGP for advertising")
            sleep(90)
            check_able_to_login_appliances(config.grid_vip)



def abnormally_kill_named(ip=config.grid_vip):
    print("\n============================================\n")
    print("Abnormally Kill named process")
    print("\n============================================\n")
    remove()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(ip, username='root', pkey = mykey)
    data="killall named"
    stdin, stdout, stderr = client.exec_command(data)
    stdout=stdout.read()
    print("=========Killall=========")
    print(stdout)


def subscriber_start_services(fqdn=config.grid_fqdn):
    print("\n============================================\n")
    print("Subscriber START Services")
    print("\n============================================\n")

    get_ref = ib_NIOS.wapi_request('GET', object_type="member:parentalcontrol")
    print(get_ref)
    res = json.loads(get_ref)
    for i in res:
        if fqdn in i['_ref']:
            data = {"enable_service": True}
            response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
            print(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    print("Failure: Subscriber Start Services")
                    assert False
            else:
                print("Success: Subscriber Start Services")
                assert True
    dns_restart_services()


def subscriber_stop_services(fqdn=config.grid_fqdn):
    print("\n============================================\n")
    print("Subscriber STOP Services")
    print("\n============================================\n")


    get_ref = ib_NIOS.wapi_request('GET', object_type="member:parentalcontrol")
    print(get_ref)
    res = json.loads(get_ref)
    for i in res:
        if fqdn in i['_ref']:
            data = {"enable_service": False}
            response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
            print(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    print("Failure: Subscriber stop Services")
                    assert False
            else:
                print("Success: Subscriber stop Services")
                assert True
    dns_restart_services()


def check_process_response_when_SS_start(ip=config.grid_vip):
    print("\n============================================\n")
    print("Checking process response when Subscriber service is start")
    print("\n============================================\n")
    remove()
    flag_bgp=False
    flag_osfp=False
    flag_zebra=False

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(ip, username='root', pkey = mykey)
    data="pgrep bgp\n"
    stdin, stdout, stderr = client.exec_command(data)
    stdout=stdout.read()
    print("************************")
    print(len(stdout),stdout)
    print("************************")
    if len(stdout)==0:
        flag_bgp=True
        client.close()
    remove()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(ip, username='root', pkey = mykey)
    data="pgrep ospf\n"
    stdin, stdout, stderr = client.exec_command(data)
    stdout=stdout.read()
    print("************************")
    print(len(stdout),stdout)
    print("************************")

    if len(stdout)==0:
        flag_osfp=True
        client.close()
    remove()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(ip, username='root', pkey = mykey)
    data="pgrep zebra\n"
    stdin, stdout, stderr = client.exec_command(data)
    stdout=stdout.read()
    print("************************")
    print(len(stdout),stdout)
    print("************************")

    if len(stdout)==0:
        flag_zebra=True
        client.close()
    print(flag_bgp,flag_osfp,flag_zebra)
    if flag_bgp==True and flag_osfp==True and flag_zebra==True:
        assert True
    else:
        assert False


def check_process_ID_when_SS_start(ip=config.grid_vip):
    print("\n============================================\n")
    print("Checking process ID is present when Subscriber service is start")
    print("\n============================================\n")

    flag_bgp=True
    flag_osfp=True
    flag_zebra=True
    remove()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(ip, username='root', pkey = mykey)
    data="pgrep bgp\n"
    stdin, stdout, stderr = client.exec_command(data)
    stdout=stdout.read()
    print(len(stdout))

    if len(stdout)==0:
        flag_bgp=False
        client.close()
    remove()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(ip, username='root', pkey = mykey)
    data="pgrep ospf\n"
    stdin, stdout, stderr = client.exec_command(data)
    stdout=stdout.read()
    print(stdout)

    if len(stdout)==0:
        flag_osfp=False
        client.close()
    remove()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(ip, username='root', pkey = mykey)
    data="pgrep zebra\n"
    stdin, stdout, stderr = client.exec_command(data)
    stdout=stdout.read()
    print(stdout)

    if len(stdout)==0:
        flag_zebra=False
        client.close()

    print(flag_bgp,flag_osfp,flag_zebra)
    if flag_bgp==True and flag_osfp==True and flag_zebra==True:
        assert True
    else:
        assert False

def reboot(ip=config.grid_vip):
    print("\n============================================\n")
    print("Reboot the appliance")
    print("\n============================================\n")
    remove()
    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+ip)
    child.logfile=sys.stdout
    child.expect('password:')
    child.sendline('infoblox')
    child.expect('Infoblox >')
    child.sendline('reboot')
    child.expect('y or n')
    child.sendline('y')
    sleep(60)

def set_recursive_query_true_for_restart_pending_changes(fqdn=config.grid_fqdn):
    print("\n============================================\n")
    print("Set allow_recursive_query to True for DNS services Restart normally")
    print("\n============================================\n")

    get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=additional_ip_list_struct')
    print(get_ref)
    for ref in json.loads(get_ref):
        if fqdn in ref['_ref']:
            data={"allow_recursive_query":True}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)
            print(response)

            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    print("Failure: Set allow_recursive_query to True for DNS services Restart normally")
                    assert False
                else:
                    print("Success: Set allow_recursive_query to True for DNS services Restart normally")
                    assert True


def set_recursive_query_false_for_restart_pending_changes(fqdn=config.grid_fqdn):
    print("\n============================================\n")
    print("Set allow_recursive_query to False for DNS services Restart normally")
    print("\n============================================\n")

    get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=additional_ip_list_struct')
    print(get_ref)
    for ref in json.loads(get_ref):
        if fqdn in ref['_ref']:
            data={"allow_recursive_query":False}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)
            print(response)

            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    print("Failure: Set allow_recursive_query to False for DNS services Restart normally")
                    assert False
                else:
                    print("Success: Set allow_recursive_query to False for DNS services Restart normally")
                    assert True


def configure_and_enable_threat_protection(ip=config.grid_vip,fqdn=config.grid_fqdn):
    '''print ("------Adding DNS resolver------")
    grid_ref = ib_NIOS.wapi_request('GET', object_type='grid')
    print(grid_ref)
    data = {"dns_resolver_setting":{"resolvers":["10.102.3.10"]}}
    for ref in json.loads(get_ref):
        response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Adding DNS Resolver")
                assert False
    print ("------DNS resolver added successfully------")'''
    print("------Enabling automatic download of ruleset------")
    logging.info("Enable automatic download")
    get_ref = ib_NIOS.wapi_request('GET', object_type="grid:threatprotection",grid_vip=ip)
    print(get_ref)
    for ref in json.loads(get_ref):
        if ref["grid_name"]== 'Infoblox':
            ref1 = ref['_ref']
            response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps({"enable_auto_download": True}),grid_vip=config.grid_vip)
            print(response)
            if type(response) == tuple:
                print("Failure: Enable automatic download in threat protection service")
                assert False
            dns_restart_services()
            print("sleep 30 seconds for threat protection rules to download")
            sleep(30)
    print("-"*6+"Enabling Threat protection service"+"-"*6)
    logging.info("Enable the threat protection service")
    get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
    print(get_ref)
    for ref in json.loads(get_ref):
        ref1 = json.loads(get_ref)[0]['_ref']
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps({"enable_service": True}),grid_vip=ip)
        print(response)
        if type(response) == tuple:
            print("Failure: Enable threat protection service")
            assert False
    sleep(360)
    check_able_to_login_appliances(config.grid_vip)

def enable_dca(ip=config.grid_vip,fqdn=config.grid_fqdn):
    get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns',grid_vip=ip)
    print(get_ref)
    for ref in json.loads(get_ref):
        if ref["host_name"]== fqdn:
            data = {"enable_dns_cache_acceleration": True}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)
            print(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401 or response[0]==401 or response[0]==404:
                    print("Failure: Enable_dns_cache_acceleration")
                    assert False
            else:
                print("Success: Enable_dns_cache_acceleration")
                assert True
    sleep(360)



class RFE_10176(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_001_set_anycast_restart_behavior_to_ON(self):
        print("##################################################################################################")
        print("#######Test cases to verify that no anycast logs are present before configuring the anycast#######")
        print("##################################################################################################")
        set_cli_anycast_restart_on(config.grid_vip)

    @pytest.mark.run(order=2)
    def test_002_Restart_DNS_Normally_and_verify_no_anycast_logs_are_present_in_anycast_restart_on_behavior(self):
        print("\n====================================")
        print("\n Restart DNS services normally")
        print("\n====================================")

        set_recursive_query_true_for_restart_pending_changes(config.grid_fqdn)

        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_restart_services_normally()
        sleep(40)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*Stopping ospfd process.*",".*Stopping ospf6d process.*",".*Stopping bgpd process.*",".*Stopping zebra process.*",".*Starting zebra process.*",".*Starting bgpd process.*",".*Starting ospfd process.*",".*Starting ospf6d process.*"]


        LookFor_sys=[".*notice Zebra.*starting.*",".*notice OSPFd.*starting.*",".*ospf6d.*notice OSPF6d .*starts.*"]

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1

        print(flag_info,flag_sys)

        if flag_info==0 and flag_sys==0:
            assert True
        else:
            assert False


    @pytest.mark.run(order=3)
    def test_003_Restart_DNS_Forcefully_and_verify_no_anycast_logs_are_present_in_anycast_restart_on_behavior(self):
        print("\n====================================")
        print("\n Restart DNS services FORCE_RESTART")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_restart_services()
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*Stopping ospfd process.*",".*Stopping ospf6d process.*",".*Stopping bgpd process.*",".*Stopping zebra process.*",".*Starting zebra process.*",".*Starting bgpd process.*",".*Starting ospfd process.*",".*Starting ospf6d process.*"]


        LookFor_sys=[".*info no longer listening on 3333::3331.*",".*notice Zebra.*starting.*",".*notice OSPFd.*starting.*",".*ospf6d.*notice OSPF6d .*starts.*"]

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1

        print(flag_info,flag_sys)

        if flag_info==0 and flag_sys==0:
            assert True
        else:
            assert False


    @pytest.mark.run(order=4)
    def test_004_Stop_DNS_service_and_verify_no_anycast_logs_are_present_in_anycast_restart_ON_behavior(self):

        print("\n====================================")
        print("\n Stop DNS services")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_stop_services(config.grid_fqdn)
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*Stopping ospfd process.*",".*Stopping ospf6d process.*",".*Stopping bgpd process.*",".*Stopping zebra process.*"]


        LookFor_sys=[".*info no longer listening on 3333::3331.*"]

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==0 and flag_sys==0:
            assert True
        else:
            assert False


    @pytest.mark.run(order=5)
    def test_005_Start_DNS_service_and_verify_no_anycast_logs_are_present_in_anycast_restart_ON_behavior(self):
        print("\n====================================")
        print("\n Start DNS services ")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_start_services(config.grid_fqdn)
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*Starting zebra process.*",".*Starting bgpd process.*",".*Starting ospfd process.*",".*Starting ospf6d process.*"]


        LookFor_sys=[".*notice Zebra.*starting.*",".*notice BGPd.*starting.*bgp.*",".*notice OSPFd.*starting.*"]
        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==0 and flag_sys==0:
            assert True
        else:
            assert False

    @pytest.mark.run(order=6)
    def test_006_set_anycast_restart_behavior_to_off(self):
        set_cli_anycast_restart_off(config.grid_vip)


    @pytest.mark.run(order=7)
    def test_007_Restart_DNS_Service_normally_and_verify_no_anycast_logs_are_present_in_anycast_restart_OFF_behavior(self):
        print("\n====================================")
        print("\n Restart DNS services normally")
        print("\n====================================")

        set_recursive_query_false_for_restart_pending_changes(config.grid_fqdn)

        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_restart_services_normally()
        sleep(30)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*Stopping ospfd process.*",".*Stopping ospf6d process.*",".*Stopping bgpd process.*",".*Stopping zebra process.*",".*Starting zebra process.*",".*Starting bgpd process.*",".*Starting ospfd process.*",".*Starting ospf6d process.*"]


        LookFor_sys=[".*info no longer listening on 3333::3331.*",".*notice Zebra.*starting.*",".*notice OSPFd.*starting.*",".*ospf6d.*notice OSPF6d .*starts.*"]

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1

        print(flag_info,flag_sys)

        if flag_info==0 and flag_sys==0:
            assert True
        else:
            assert False



    @pytest.mark.run(order=8)
    def test_008_Restart_DNS_Service_forcefully_and_verify_no_anycast_logs_are_present_in_anycast_restart_OFF_behavior(self):
        print("\n====================================")
        print("\n Restart DNS services FORCE_RESTART")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_restart_services()
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*Stopping ospfd process.*",".*Stopping ospf6d process.*",".*Stopping bgpd process.*",".*Stopping zebra process.*",".*Starting zebra process.*",".*Starting bgpd process.*",".*Starting ospfd process.*",".*Starting ospf6d process.*"]


        LookFor_sys=[".*info no longer listening on 3333::3331.*",".*notice Zebra.*starting.*",".*notice OSPFd.*starting.*",".*ospf6d.*notice OSPF6d .*starts.*"]

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1

        print(flag_info,flag_sys)

        if flag_info==0 and flag_sys==0:
            assert True
        else:
            assert False




    @pytest.mark.run(order=9)
    def test_009_Stop_DNS_service_and_verify_no_anycast_logs_are_present_in_anycast_restart_OFF_behavior(self):
        print("\n====================================")
        print("\n Stop DNS services ")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_stop_services(config.grid_fqdn)
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)

        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*Stopping ospfd process.*",".*Stopping ospf6d process.*",".*Stopping bgpd process.*",".*Stopping zebra process.*"]


        LookFor_sys=[".*info no longer listening on 3333::3331.*"]

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==0 and flag_sys==0:
            assert True
        else:
            assert False



    @pytest.mark.run(order=10)
    def test_010_Start_DNS_service_and_verify_no_anycast_logs_are_present_in_anycast_restart_OFF_behavior(self):
        print("\n====================================")
        print("\n Start DNS services normally")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_start_services(config.grid_fqdn)
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*Starting zebra process.*",".*Starting bgpd process.*",".*Starting ospfd process.*",".*Starting ospf6d process.*"]


        LookFor_sys=[".*notice Zebra.*starting.*",".*notice BGPd.*starting.*bgp.*",".*notice OSPFd.*starting.*"]
        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==0 and flag_sys==0:
            assert True
        else:
            assert False

    @pytest.mark.run(order=11)
    def test_011_configure_ospf_ipv4(self):
        ospf_ipv4_configuration()
        sleep(30)
        dns_restart_services()

    @pytest.mark.run(order=12)
    def test_012_anycast_ipv4_configuration(self):
        anycast_ipv4_configuration()
        dns_restart_services()
        sleep(120)


    @pytest.mark.run(order=13)
    def test_013_set_anycast_restart_behavior_to_ON(self):
        set_cli_anycast_restart_on(config.grid_vip)
        sleep(10)

    @pytest.mark.run(order=14)
    def test_014_Restart_DNS_service_normally_and_check_for_anycast_logs_ospf_ipv4(self):
        print("\n====================================")
        print("\nRestart DNS normally")
        print("\n====================================")
        set_recursive_query_true_for_restart_pending_changes(config.grid_fqdn)
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_restart_services_normally()
        sleep(30)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*Stopping ospfd process.*",".*Stopping zebra process.*",".*Starting zebra process.*",".*Starting ospfd process.*"]

        LookFor_sys=[".*info shutting down.*",".*notice exiting.*",".*notice starting BIND.*(Supported Preview Version).*",".*notice running on.*",".*info all zones loaded.*",".*notice running.*",".*notice Zebra.*starting.*vty@2601.*",".*notice OSPFd.*starting.*vty@2604.*"]
        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            #logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1


        for look in LookFor_sys:
            print(look)
            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1

        print(flag_info,flag_sys)

        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False




    @pytest.mark.run(order=15)
    def test_015_Restart_DNS_service_forcefully_and_check_for_anycast_logs_ospf_ipv4(self):
        print("\n====================================")
        print("\nRestart DNS FORCE RESTART")
        print("\n====================================")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_restart_services()
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*Stopping ospfd process.*",".*Stopping zebra process.*",".*Starting zebra process.*",".*Starting ospfd process.*"]


        LookFor_sys=[".*info shutting down.*",".*notice exiting.*",".*notice starting BIND.*(Supported Preview Version).*",".*notice running on.*",".*info all zones loaded.*",".*notice running.*",".*notice Zebra.*starting.*vty@2601.*",".*notice OSPFd.*starting.*vty@2604.*"]


        #LookFor_sys=".*ospfd[.*].*notice Termi.*"
        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            #logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1


        for look in LookFor_sys:
            print(look)
            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1

        print(flag_info,flag_sys)

        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False



    @pytest.mark.run(order=16)
    def test_016_Stop_DNS_Service_and_check_for_anycast_logs_ospf_ipv4(self):
        print("\n====================================")
        print("\nStop DNS services")
        print("\n====================================")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_stop_services(config.grid_fqdn)
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*stopping named services.*",".*Stopping ospfd process.*",".*Stopping zebra process.*"]


        LookFor_sys=[".*info shutting down.*",".*notice stopping command channel on.*",".*info no longer listening on.*",".*info no longer listening on "+config.grid_vip+".*",".*notice exiting.*"]
        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False


    @pytest.mark.run(order=17)
    def test_017_Start_DNS_Service_and_check_for_anycast_logs_ospf_ipv4(self):
        print("\n====================================")
        print("\nStart DNS services")
        print("\n====================================")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_start_services(config.grid_fqdn)
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*killall named.*",".*Starting zebra process.*",".*Starting ospfd process.*"]


        LookFor_sys=[".*notice starting BIND.*(Supported Preview Version).*",".*notice running on.*",".*info managed-keys-zone.*loaded serial.*",".*info all zones loaded.*",".*notice running.*",".*notice Zebra.*starting.*vty@2601.*",".*notice OSPFd.*starting: vty@2604.*"]
        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False

    @pytest.mark.run(order=18)
    def test_018_Perform_killall_operation_and_verify_the_logs_for_anycast_restart_behavior_ON(self):
        print("\n====================================")
        print("\n Killall named process")
        print("\n====================================")
        log("start","/infoblox/var/infoblox.log",config.grid_member3_vip)
        log("start","/var/log/syslog",config.grid_member3_vip)
        sleep(10)
        abnormally_kill_named(config.grid_member3_vip)
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_member3_vip)
        log("stop","/var/log/syslog",config.grid_member3_vip)

        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_member3_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member3_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")

        #LookFor_info=[".*DNS not suppress splunk restart.*"]
        LookFor_sys=[".*info shutting down.*",".*info no longer listening.*"]
        #flag_info=0
        flag_sys=0

        # for look in LookFor_info:
            # print(look)
            # logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            # print(logs)
            # if logs:
                # flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member3_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1

        print(flag_sys)
        if flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False


    @pytest.mark.run(order=19)
    def test_019_set_anycast_restart_behavior_to_OFF(self):
        set_cli_anycast_restart_off(config.grid_vip)


    @pytest.mark.run(order=20)
    def test_020_Restart_DNS_normally_and_check_for_anycast_logs_ospf_ipv4(self):
        set_recursive_query_false_for_restart_pending_changes(config.grid_fqdn)
        print("\n====================================")
        print("\n Restart DNS services Normally")
        print("\n====================================")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_restart_services_normally()
        sleep(30)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info_not=[".*Stopping ospfd process.*",".*Stopping zebra process.*",".*Starting zebra process.*",".*Starting ospfd process.*"]


        LookFor_sys_not=[".*notice Zebra.*starting.*vty@2601.*",".*notice OSPFd.*starting.*vty@2604.*"]

        LookFor_info=[]

        LookFor_sys=[".*info shutting down.*",".*notice stopping command channel on.*",".*info no longer listening on.*",".*info no longer listening on "+config.grid_vip+".*",".*notice exiting.*",".*notice starting BIND.*(Supported Preview Version).*",".*notice running on.*",".*info all zones loaded.*",".*notice running.*"]
        flag_info_not=1
        flag_sys_not=1

        for look in LookFor_info_not:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info_not=0

        for look in LookFor_sys_not:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys_not=0

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1

        print(flag_info_not,flag_sys_not,flag_info,flag_sys)
        if flag_info_not==1 and flag_sys_not==1 and flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False

    @pytest.mark.run(order=21)
    def test_021_Restart_DNS_forcefully_and_check_for_anycast_logs_ospf_ipv4(self):
        print("\n====================================")
        print("\n Restart DNS services FORCE_RESTART")
        print("\n====================================")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_restart_services()
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info_not=[".*Stopping ospfd process.*",".*Stopping zebra process.*",".*Starting zebra process.*",".*Starting ospfd process.*"]


        LookFor_sys_not=[".*notice Zebra.*starting.*vty@2601.*",".*notice OSPFd.*starting.*vty@2604.*"]

        LookFor_info=[]

        LookFor_sys=[".*info shutting down.*",".*notice stopping command channel on.*",".*info no longer listening on.*",".*info no longer listening on "+config.grid_vip+".*",".*notice exiting.*",".*notice starting BIND.*(Supported Preview Version).*",".*notice running on.*",".*info all zones loaded.*",".*notice running.*"]
        flag_info_not=1
        flag_sys_not=1

        for look in LookFor_info_not:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info_not=0

        for look in LookFor_sys_not:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys_not=0

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1

        print(flag_info_not,flag_sys_not,flag_info,flag_sys)
        if flag_info_not==1 and flag_sys_not==1 and flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False

    @pytest.mark.run(order=22)
    def test_022_Stop_DNS_service_and_check_for_anycast_logs_ospf_ipv4(self):
        print("\n====================================")
        print("\n Stop DNS services")
        print("\n====================================")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(20)
        dns_stop_services(config.grid_fqdn)
        sleep(120)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)

        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*stopping named services.*",".*Stopping ospfd process.*",".*Stopping zebra process.*"]

        LookFor_sys=[".*info shutting down.*",".*notice stopping command channel on.*",".*info no longer listening on.*",".*info no longer listening on "+config.grid_vip+".*",".*notice exiting.*"]

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False

    @pytest.mark.run(order=23)
    def test_023_Start_DNS_service_and_check_for_anycast_logs_ospf_ipv4(self):
        print("\n====================================")
        print("\n Start DNS services")
        print("\n====================================")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_start_services(config.grid_fqdn)
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")

        LookFor_info=[".*killall named.*",".*Starting zebra process.*",".*Starting ospfd process.*"]

        LookFor_sys=[".*notice starting BIND.*(Supported Preview Version).*",".*notice running on.*",".*info all zones loaded.*",".*notice running.*",".*notice Zebra.*starting.*vty@2601.*",".*notice OSPFd.*starting.*vty@2604.*"]

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1


        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1

        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False

    @pytest.mark.run(order=24)
    def test_024_Perform_operation_killall_and_check_for_anycast_logs_ospf_ipv4(self):
        print("\n====================================")
        print("\n Killall named process")
        print("\n====================================")
        log("start","/infoblox/var/infoblox.log",config.grid_member3_vip)
        log("start","/var/log/syslog",config.grid_member3_vip)
        sleep(10)
        abnormally_kill_named(config.grid_member3_vip)
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_member3_vip)
        log("stop","/var/log/syslog",config.grid_member3_vip)

        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_member3_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member3_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")

        #LookFor_info=[".*DNS not suppress splunk restart.*"]
        LookFor_sys=[".*info shutting down.*",".*info no longer listening.*"]
        #flag_info=0
        flag_sys=0

        # for look in LookFor_info:
            # print(look)
            # logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            # print(logs)
            # if logs:
                # flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member3_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1

        print(flag_sys)
        if flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False

    @pytest.mark.run(order=25)
    def test_025_ospf_ipv6_configuration(self):
        check_able_to_login_appliances(config.grid_vip)
        ospf_ipv6_configuration()
        sleep(30)

    @pytest.mark.run(order=26)
    def test_026_anycast_ipv6_configuration(self):
        sleep(30)
        check_able_to_login_appliances(config.grid_vip)
        anycast_ipv6_configuration()
        sleep(120)
        dns_restart_services()

    @pytest.mark.run(order=27)
    def test_027_set_anycst_restart_behavior_to_ON(self):
        set_cli_anycast_restart_on(config.grid_vip)

    @pytest.mark.run(order=28)
    def test_028_Restart_DNS_normally_and_check_for_anycast_logs_ospf_ipv6(self):
        print("\n====================================")
        print("\n Restart DNS services normally")
        print("\n====================================")
        set_recursive_query_true_for_restart_pending_changes(config.grid_fqdn)

        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_restart_services_normally()
        sleep(30)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*Stopping ospf6d process.*",".*Stopping zebra process.*",".*Starting zebra process.*",".*Starting ospf6d process.*"]


        LookFor_sys=[".*info shutting down.*",".*notice stopping command channel on.*",".*notice exiting.*",".*notice stopping command channel on.*",".*info no longer listening on 3333::3331.*",".*info no longer listening on.*"+config.grid_ipv6+".*",".*notice exiting.*",".*notice starting BIND.*(Supported Preview Version).*",".*notice running on Linux .*",".*info listening on IPv6 interface eth1.*"+config.grid_ipv6+".*",".*info all zones loaded.*",".*notice running.*",".*notice Zebra.*starting.*",".*ospf6d.*notice OSPF6d.*starts.*"]
        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False


    @pytest.mark.run(order=29)
    def test_029_Restart_DNS_forcefully_and_check_for_anycast_logs_ospf_ipv6(self):
        check_able_to_login_appliances(config.grid_vip)
        print("\n====================================")
        print("\n Restart DNS service FORCE_RESTART")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_restart_services()
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*Stopping ospf6d process.*",".*Stopping zebra process.*",".*Starting zebra process.*",".*Starting ospf6d process.*"]


        LookFor_sys=[".*info shutting down.*",".*notice stopping command channel on.*",".*notice exiting.*",".*notice stopping command channel on.*",".*info no longer listening on 3333::3331.*",".*info no longer listening on.*"+config.grid_ipv6+".*",".*notice exiting.*",".*notice starting BIND.*(Supported Preview Version).*",".*notice running on Linux .*",".*info listening on IPv6 interface eth1.*"+config.grid_ipv6+".*",".*info all zones loaded.*",".*notice running.*",".*notice Zebra.*starting.*",".*ospf6d.*notice OSPF6d.*starts.*"]
        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False

    @pytest.mark.run(order=30)
    def test_030_Stop_DNS_service_and_check_for_anycast_logs_ospf_ipv6(self):
        print("\n====================================")
        print("\n Stop DNS service ")
        print("\n====================================")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_stop_services(config.grid_fqdn)
        sleep(30)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)

        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")

        LookFor_info=[".*Stopping ospf6d process.*",".*Stopping zebra process.*"]


        LookFor_sys=[".*info shutting down.*",".*notice stopping command channel on.*",".*info no longer listening on 3333::3331.*",".*info no longer listening on.*"+config.grid_ipv6+".*",".*notice exiting.*"]
        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False


    @pytest.mark.run(order=31)
    def test_031_Start_DNS_service_and_check_for_anycast_logs_ospf_ipv6(self):
        print("\n====================================")
        print("\n Start DNS service ")
        print("\n====================================")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_start_services(config.grid_fqdn)
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*killall named.*",".*Starting zebra process.*",".*Starting ospf6d process.*"]


        LookFor_sys=[".*notice starting BIND.*(Supported Preview Version).*",".*notice running on Linux.*",".*info listening on IPv6 interface eth1.*"+config.grid_ipv6+".*",".*notice command channel listening on.*",".*info all zones loaded.*",".*notice running.*",".*notice Zebra.*starting.*",".*ospf6d.*notice OSPF6d.*starts.*"]
        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False

    @pytest.mark.run(order=32)
    def test_032_set_anycast_restart_behavior_to_OFF(self):
        set_cli_anycast_restart_off(config.grid_vip)

    @pytest.mark.run(order=34)
    def test_033_Restart_DNS_normally_and_check_for_anycast_logs_ospf_ipv6(self):

        print("\n====================================")
        print("\n Restart DNS services normally")
        print("\n====================================")

        set_recursive_query_false_for_restart_pending_changes(config.grid_fqdn)
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_restart_services_normally()
        sleep(30)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info_not=[".*Stopping ospf6d process.*",".*Stopping zebra process.*",".*Starting zebra process.*",".*Starting ospf6d process.*"]


        LookFor_sys_not=[".*notice Zebra.*starting.*",".*ospf6d.*notice OSPF6d.*starts.*"]

        LookFor_info=[]

        LookFor_sys=[".*info shutting down.*",".*notice stopping command channel on.*",".*info no longer listening on "+config.grid_vip+".*",".*info no longer listening on 3333::3331.*",".*info no longer listening on.*",".*info no longer listening on.*"+config.grid_ipv6+".*",".*notice exiting.*",".*notice starting BIND.*(Supported Preview Version).*",".*notice running on Linux.*",".*info listening on IPv4 interface eth1, "+config.grid_vip+".*",".*notice fd.*receive buffer set to.*",".*info all zones loaded.*",".*notice running.*"]
        flag_info_not=1
        flag_sys_not=1

        for look in LookFor_info_not:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info_not=0

        for look in LookFor_sys_not:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys_not=0

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info_not,flag_sys_not,flag_info,flag_sys)

        if flag_info_not==1 and flag_sys_not==1 and flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False

    @pytest.mark.run(order=34)
    def test_034_Restart_DNS_forcefully_and_check_for_anycast_logs_ospf_ipv6(self):
        print("\n====================================")
        print("\n Restart DNS services FORCE_RESTART")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_restart_services()
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info_not=[".*Stopping ospf6d process.*",".*Stopping zebra process.*",".*Starting zebra process.*",".*Starting ospf6d process.*"]


        LookFor_sys_not=[".*notice Zebra.*starting.*",".*ospf6d.*notice OSPF6d.*starts.*"]

        LookFor_info=[]

        LookFor_sys=[".*info shutting down.*",".*notice stopping command channel on.*",".*info no longer listening on "+config.grid_vip+".*",".*info no longer listening on 3333::3331.*",".*info no longer listening on ::1.*",".*info no longer listening on.*"+config.grid_ipv6+".*",".*notice exiting.*",".*notice starting BIND.*(Supported Preview Version).*",".*notice running on Linux.*",".*info listening on IPv4 interface eth1, "+config.grid_vip+".*",".*notice fd.*receive buffer set to.*",".*info all zones loaded.*",".*notice running.*"]
        flag_info_not=1
        flag_sys_not=1

        for look in LookFor_info_not:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info_not=0

        for look in LookFor_sys_not:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys_not=0

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info_not,flag_sys_not,flag_info,flag_sys)
        if flag_info_not==1 and flag_sys_not==1 and flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False




    @pytest.mark.run(order=35)
    def test_035_Stop_DNS_and_check_for_anycast_logs_ospf_ipv6(self):

        print("\n====================================")
        print("\n Stop DNS services ")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(20)
        dns_stop_services(config.grid_fqdn)
        sleep(80)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)

        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*stopping named services.*",".*Stopping ospf6d process.*",".*Stopping zebra process.*"]

        LookFor_sys=[".*info shutting down.*",".*notice stopping command channel on.*",".*info no longer listening on 3333::3331.*",".*info no longer listening on ::1.*",".*info no longer listening on.*"+config.grid_ipv6+".*",".*notice exiting.*"]

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False

    @pytest.mark.run(order=36)
    def test_036_Start_DNS_and_check_for_anycast_logs_ospf_ipv6(self):

        print("\n====================================")
        print("\n Start DNS services")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_start_services(config.grid_fqdn)
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")

        LookFor_info=[".*killall named.*",".*Starting zebra process.*",".*Starting ospf6d process.*"]

        LookFor_sys=[".*notice starting BIND.*(Supported Preview Version).*",".*notice running on Linux.*",".*info listening on IPv6 interface eth1.*"+config.grid_ipv6+".*",".*info all zones loaded.*",".*notice running.*",".*notice Zebra.*starting.*",".*ospf6d.*notice OSPF6d.*starts.*"]


        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False



    @pytest.mark.run(order=37)
    def test_037_select_bgp_for_advertising(self):
        bgp_configuration()
        sleep(60)

    @pytest.mark.run(order=38)
    def test_038_anycast_ipv4_configuration_enable_BGP(self):
        anycast_bgp_ipv4_configuration()
        sleep(60)

    @pytest.mark.run(order=39)
    def test_039_set_anycast_restart_behavior_to_ON(self):
        set_cli_anycast_restart_on(config.grid_vip)

    @pytest.mark.run(order=40)
    def test_040_Restart_DNS_normally_and_check_for_anycast_logs_bgp_ipv4(self):
        print("\n====================================")
        print("\n Restart DNS services normally")
        print("\n====================================")

        set_recursive_query_true_for_restart_pending_changes(config.grid_fqdn)
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_restart_services_normally()
        sleep(30)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*Stopping bgpd process.*",".*Stopping zebra process.*",".*Starting zebra process.*",".*Starting bgpd process.*"]


        LookFor_sys=[".*info shutting down.*",".*notice stopping command channel on.*",".*info no longer listening on "+config.grid_vip+".*",".*notice exiting.*",".*notice starting BIND.*(Supported Preview Version).*",".*notice running on Linux.*",".*info listening on IPv4 interface lo,.*",".*info listening on IPv4 interface eth1, "+config.grid_vip+".*",".*info all zones loaded.*",".*notice running.*",".*notice Zebra.*starting.*",".*bgpd.*notice BGPd.*starting.*"]
        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1

        print(flag_info,flag_sys)

        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False


    @pytest.mark.run(order=41)
    def test_041_Restart_DNS_forcefully_and_check_for_anycast_logs_bgp_ipv4(self):
        print("\n====================================")
        print("\n Restart DNS services FORCE_RESTART")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_restart_services()
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*Stopping bgpd process.*",".*Stopping zebra process.*",".*Starting zebra process.*",".*Starting bgpd process.*"]


        LookFor_sys=[".*info shutting down.*",".*notice stopping command channel on.*",".*info no longer listening on "+config.grid_vip+".*",".*notice exiting.*",".*notice starting BIND.*(Supported Preview Version).*",".*notice running on Linux.*",".*info listening on IPv4 interface lo,.*",".*info listening on IPv4 interface eth1, "+config.grid_vip+".*",".*info all zones loaded.*",".*notice running.*",".*notice Zebra.*starting.*",".*bgpd.*notice BGPd.*starting.*"]

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1

        print(flag_info,flag_sys)

        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False


    @pytest.mark.run(order=42)
    def test_042_Stop_DNS_and_check_for_anycast_logs_bgp_ipv4(self):

        print("\n====================================")
        print("\n Stop DNS services")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_stop_services(config.grid_fqdn)
        sleep(30)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*stopping named services.*",".*Stopping bgpd process.*",".*/infoblox/one/bin/anycast_control).*topping zebra process.*"]


        LookFor_sys=[".*info shutting down.*",".*notice stopping command channel on.*",".*info no longer listening on "+config.grid_vip+".*",".*notice exiting.*"]
        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False


    @pytest.mark.run(order=43)
    def test_043_Start_DNS_and_check_for_anycast_logs_bgp_ipv4(self):
        print("\n====================================")
        print("\n Start DNS services ")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_start_services(config.grid_fqdn)
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*killall named.*",".*Starting zebra process.*",".*Starting bgpd process.*"]


        LookFor_sys=[".*notice starting BIND.*(Supported Preview Version).*",".*notice running on Linux.*",".*info listening on IPv4 interface lo.*",".*nfo listening on IPv4 interface lo:1, 1.3.3.3.*",".*info listening on IPv4 interface eth1, "+config.grid_vip+".*",".*info all zones loaded.*",".*notice running.*",".*notice Zebra.*starting.*",".*notice BGPd.*starting.*bgp.*"]
        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False

    @pytest.mark.run(order=44)
    def test_044_set_anycast_restart_behavior_to_OFF(self):
        set_cli_anycast_restart_off(config.grid_vip)


    @pytest.mark.run(order=45)
    def test_045_Restart_DNS_normally_and_check_for_anycast_logs_bgp_ipv4(self):
        print("\n====================================")
        print("\n Restart DNS services normally")
        print("\n====================================")

        set_recursive_query_false_for_restart_pending_changes(config.grid_fqdn)

        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_restart_services_normally()
        sleep(30)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info_not=[".*Stopping bgpd process.*",".*Stopping zebra process.*",".*Starting zebra process.*",".*Starting bgpd process.*"]


        LookFor_sys_not=[".*notice Zebra.*starting.*",".*bgpd.*notice BGPd.*starting.*"]

        LookFor_info=[]


        LookFor_sys=[".*info shutting down.*",".*notice stopping command channel on.*",".*info no longer listening on.*",".*info no longer listening on "+config.grid_vip+".*",".*notice exiting.*",".*notice starting BIND.*(Supported Preview Version).*",".*notice running on Linux.*",".*info listening on IPv4 interface eth1, "+config.grid_vip+".*",".*info all zones loaded.*",".*notice running.*"]


        flag_info_not=1
        flag_sys_not=1

        for look in LookFor_info_not:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info_not=0

        for look in LookFor_sys_not:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys_not=0

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info_not,flag_sys_not,flag_info,flag_sys)
        if flag_info_not==1 and flag_sys_not==1 and flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False


    @pytest.mark.run(order=46)
    def test_046_Restart_DNS_forcefully_and_check_for_anycast_logs_bgp_ipv4(self):
        print("\n====================================")
        print("\n Restart DNS services FORCE_RESTART")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_restart_services()
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info_not=[".*Stopping bgpd process.*",".*Stopping zebra process.*",".*Starting zebra process.*",".*Starting bgpd process.*"]


        LookFor_sys_not=[".*notice Zebra.*starting.*",".*bgpd.*notice BGPd.*starting.*"]

        LookFor_info=[]


        LookFor_sys=[".*info shutting down.*",".*notice stopping command channel on.*",".*info no longer listening on.*",".*info no longer listening on "+config.grid_vip+".*",".*notice exiting.*",".*notice starting BIND.*(Supported Preview Version).*",".*notice running on Linux.*",".*info listening on IPv4 interface eth1, "+config.grid_vip+".*",".*info all zones loaded.*",".*notice running.*"]


        flag_info_not=1
        flag_sys_not=1

        for look in LookFor_info_not:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info_not=0

        for look in LookFor_sys_not:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys_not=0

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info_not,flag_sys_not,flag_info,flag_sys)
        if flag_info_not==1 and flag_sys_not==1 and flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False




    @pytest.mark.run(order=47)
    def test_047_Stop_DNS_and_check_for_anycast_logs_bgp_ipv4(self):
        print("\n====================================")
        print("\n Stop DNS services ")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_stop_services(config.grid_fqdn)
        sleep(80)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")

        LookFor_info=[".*stopping named services.*",".*Stopping bgpd process.*",".*Stopping zebra process.*"]

        LookFor_sys=[".*info shutting down.*",".*notice stopping command.*",".*info no longer listening on.*",".*info no longer listening on "+config.grid_vip+".*",".*notice exiting.*"]

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1

        print(flag_info,flag_sys)

        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False

    @pytest.mark.run(order=48)
    def test_048_Start_DNS_and_check_for_anycast_logs_bgp_ipv4(self):
        print("\n====================================")
        print("\n Start DNS services normally")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_start_services(config.grid_fqdn)
        sleep(120)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*/infoblox/dns/bin/named_control.*killall named.*",".*/infoblox/dns/bin/named_control.*DNS not suppress splunk restart.*",".*Starting zebra process.*",".*Starting bgpd process.*"]

        LookFor_sys=[".*notice starting BIND.*(Supported Preview Version).*",".*notice running on Linux.*",".*info listening on IPv4 interface lo.*",".*info listening on IPv4 interface eth1.*"+config.grid_vip+".*",".*info all zones loaded.*",".*notice running.*",".*notice Zebra.*starting.*",".*notice BGPd.*starting.*bgp.*"]


        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False


    @pytest.mark.run(order=49)
    def test_049_anycast_ipv6_configuration_enable_BGP(self):
        anycast_bgp_ipv6_configuration()
        dns_restart_services()

    @pytest.mark.run(order=50)
    def test_050_set_anycast_restart_behavior_to_ON(self):
        set_cli_anycast_restart_on(config.grid_vip)


    @pytest.mark.run(order=51)
    def test_051_Restart_DNS_normally_and_check_for_anycast_logs_bgp_ipv6(self):
        print("\n====================================")
        print("\n Restart DNS services normally")
        print("\n====================================")

        set_recursive_query_true_for_restart_pending_changes(config.grid_fqdn)


        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_restart_services_normally()
        sleep(30)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*Stopping bgpd process.*",".*Stopping zebra process.*",".*Starting zebra process.*",".*Starting bgpd process.*"]


        LookFor_sys=[".*info shutting down.*",".*notice stopping command channel on.*",".*info no longer listening on 3333::3331.*",".*info no longer listening on "+config.grid_ipv6+".*",".*notice exiting.*",".*notice starting BIND.*(Supported Preview Version).*",".*notice running on Linux.*",".*info listening on IPv6 interface eth1.*"+config.grid_ipv6+".*",".*info all zones loaded.*",".*notice running on Linux.*",".*notice Zebra.*starting.*",".*bgpd.*notice BGPd.*starting.*"]


        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        sleep(10)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False



    @pytest.mark.run(order=52)
    def test_052_Restart_DNS_forcefully_and_check_for_anycast_logs_bgp_ipv6(self):
        print("\n====================================")
        print("\n Restart DNS services FORCE_RESTART")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_restart_services()
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*Stopping bgpd process.*",".*Stopping zebra process.*",".*Starting zebra process.*",".*Starting bgpd process.*"]


        LookFor_sys=[".*info shutting down.*",".*notice stopping command channel on.*",".*info no longer listening on 3333::3331.*",".*info no longer listening on "+config.grid_ipv6+".*",".*notice exiting.*",".*notice starting BIND.*(Supported Preview Version).*",".*notice running on Linux.*",".*info listening on IPv6 interface eth1.*"+config.grid_ipv6+".*",".*info all zones loaded.*",".*notice running on Linux.*",".*notice Zebra.*starting.*",".*bgpd.*notice BGPd.*starting.*"]

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False


    @pytest.mark.run(order=53)
    def test_053_Stop_DNS_and_check_for_anycast_logs_bgp_ipv6(self):
        print("\n====================================")
        print("\n Stop DNS services ")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_stop_services(config.grid_fqdn)
        sleep(30)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*stopping named services.*",".*Stopping bgpd process.*",".*/infoblox/one/bin/anycast_control).*topping zebra process.*"]


        LookFor_sys=[".*info shutting down.*",".*notice stopping command channel on.*",".*info no longer listening on 3333::3331.*",".*info no longer listening on "+config.grid_ipv6+".*",".*notice exiting.*"]

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False


    @pytest.mark.run(order=54)
    def test_054_Start_DNS_and_check_for_anycast_logs_bgp_ipv6(self):
        print("\n====================================")
        print("\n Start DNS services ")
        print("\n====================================")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_start_services(config.grid_fqdn)
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*killall named.*",".*Starting zebra process.*",".*Starting bgpd process.*",
        ]


        LookFor_sys=[".*notice starting BIND.*(Supported Preview Version).*",".*notice running on Linux.*",".*info listening on IPv4 interface lo.*",".*info listening on IPv6 interface eth1.*"+config.grid_ipv6+".*",".*info all zones loaded.*",".*notice running.*",".*notice Zebra.*starting.*",".*notice BGPd.*starting.*bgp.*"]

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False

    @pytest.mark.run(order=55)
    def test_055_set_anycast_restart_behavior_to_OFF(self):
        set_cli_anycast_restart_off(config.grid_vip)

    @pytest.mark.run(order=56)
    def test_056_Restart_DNS_normally_and_check_for_anycast_logs_bgp_ipv6(self):
        print("\n====================================")
        print("\n Restart DNS services normally")
        print("\n====================================")

        set_recursive_query_false_for_restart_pending_changes(config.grid_fqdn)

        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_restart_services_normally()
        sleep(30)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info_not=[".*Stopping bgpd process.*",".*Stopping zebra process.*",".*Starting zebra process.*",".*Starting bgpd process.*"]


        LookFor_sys_not=[".*notice Zebra.*starting.*",".*bgpd.*notice BGPd.*starting.*"]

        LookFor_info=[]

        LookFor_sys=[".*info shutting down.*",".*notice stopping command channel on.*",".*info no longer listening on.*",".*info no longer listening on 3333::3331.*",".*info no longer listening on "+config.grid_ipv6+".*",".*notice exiting.*",".*notice starting BIND.*(Supported Preview Version).*",".*notice running on Linux.*",".*info listening on IPv6 interface eth1.*"+config.grid_ipv6+".*",".*info all zones loaded.*",".*notice running.*"]


        flag_info_not=1
        flag_sys_not=1

        for look in LookFor_info_not:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info_not=0

        for look in LookFor_sys_not:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys_not=0

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info_not,flag_sys_not,flag_info,flag_sys)
        if flag_info_not==1 and flag_sys_not==1 and flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False


    @pytest.mark.run(order=57)
    def test_057_Restart_DNS_forcefully_and_check_for_anycast_logs_bgp_ipv6(self):
        print("\n====================================")
        print("\n Restart DNS services FORCE_RESTART")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_restart_services()
        sleep(120)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)

        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info_not=[".*Stopping bgpd process.*",".*Stopping zebra process.*",".*Starting zebra process.*",".*Starting bgpd process.*"]


        LookFor_sys_not=[".*notice Zebra.*starting.*",".*bgpd.*notice BGPd.*starting.*"]

        LookFor_info=[]

        LookFor_sys=[".*info shutting down.*",".*notice stopping command channel on.*",".*info no longer listening on.*",".*info no longer listening on 3333::3331.*",".*info no longer listening on "+config.grid_ipv6+".*",".*notice exiting.*",".*notice starting BIND.*(Supported Preview Version).*",".*notice running on Linux.*",".*info listening on IPv6 interface eth1.*"+config.grid_ipv6+".*",".*info all zones loaded.*",".*notice running.*"]


        flag_info_not=1
        flag_sys_not=1

        for look in LookFor_info_not:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info_not=0

        for look in LookFor_sys_not:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys_not=0

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info_not,flag_sys_not,flag_info,flag_sys)
        if flag_info_not==1 and flag_sys_not==1 and flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False

    @pytest.mark.run(order=58)
    def test_058_Stop_DNS_and_check_for_anycast_logs_bgp_ipv6(self):
        print("\n====================================")
        print("\n Stop DNS services ")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_stop_services(config.grid_fqdn)
        sleep(40)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)

        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*stopping named services.*",".*Stopping bgpd process.*",".*Stopping zebra process.*"]

        LookFor_sys=[".*info shutting down.*",".*notice stopping command.*",".*info no longer listening on.*",".*info no longer listening on 3333::3331.*",".*info no longer listening on "+config.grid_ipv6+".*",".*notice exiting.*"]

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False

    @pytest.mark.run(order=59)
    def test_059_Start_DNS_and_check_for_anycast_logs_bgp_ipv6(self):
        print("\n====================================")
        print("\n Start DNS services ")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        dns_start_services(config.grid_fqdn)
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")

        LookFor_info=[".*killall named.*",".*Starting zebra process.*",".*Starting bgpd process.*",
        ".*Enabled firewall BGP.*"]


        LookFor_sys=[".*notice starting BIND.*(Supported Preview Version).*",".*notice running on Linux.*",".*info listening on IPv4 interface lo.*",".*info listening on IPv6 interface eth1.*"+config.grid_ipv6+".*",".*info all zones loaded.*",".*notice running.*",".*notice Zebra.*starting.*",".*notice BGPd.*starting.*bgp.*"]

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False

    @pytest.mark.run(order=60)
    def test_060_parental_control_and_subscriber_service_configuration_setup(self):
        set_cli_anycast_restart_on(config.grid_vip)
        print("\n====================================")
        print("\n Subscriber configuration setup ")
        print("\n====================================")

        """
        setup method: Used for configuring pre-required configs.
        """

        '''Add DNS Resolver'''
        print("Add DNS Resolver 10.102.3.10 ")
        grid_ref = ib_NIOS.wapi_request('GET', object_type='grid')
        data = {"dns_resolver_setting":{"resolvers":["10.102.3.10"]}}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(grid_ref)[0]['_ref'], fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Adding DNS Resolver")
                assert False

        '''Add DNS Forwarder'''
        print("Add DNS forwarder : 10.102.3.10 ")
        grid_dns_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns')
        data = {"forwarders":["10.102.3.10"]}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(grid_dns_ref)[0]['_ref'], fields=json.dumps(data))
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Adding DNS Forwarder")
                assert False


        '''Enable logging for queries, responses, rpz'''
        print("Enable logging for queries, responses, rpz")
        data = {"logging_categories":{"log_queries":True, "log_responses":True, "log_rpz":True}}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(grid_dns_ref)[0]['_ref'], fields=json.dumps(data))
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Enabling logging for queries, responses, rpz")
                assert False


        ''' Add Subscriber Site'''
        print("Add Subscriber Site")
        data={"name": "rfe_10176_subscbr",
              "maximum_subscribers": 1000000,
              "members": [{"name": config.grid_member2_fqdn}],
              "nas_gateways": [{"ip_address": "10.35.120.10","shared_secret": "test","name": "rfe_10176_nas","send_ack": True}]}
        subs_site = ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscribersite",fields=json.dumps(data))
        print(subs_site)
        if type(subs_site) == tuple:
            if subs_site[0]==400 or subs_site[0]==401:
                print("Failure: Adding subscriber site")
                assert False

        # print("Restart services")
        # grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        # ref = json.loads(grid)[0]['_ref']
        # data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        # restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices", fields=json.dumps(data))
        # sleep(60)

        ''' Enable Parental Control'''
        print("Enable Parental Control")
        get_ref = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriber")
        print(get_ref)
        data={"enable_parental_control": True,
              "cat_acctname":"infoblox_sdk",
              "cat_password":"LinWmRRDX0q",
              "category_url":"https://dl.zvelo.com/",
              "proxy_url":"http://10.196.9.113:8001",
              "proxy_username":"client",
              "proxy_password":"infoblox",
              "pc_zone_name":"rfe_10176.zone.com",
              "cat_update_frequency":24}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]["_ref"],fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Enabling parental control")
                assert False
        #sleep(30)

        # print("Restart services")
        # grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        # ref = json.loads(grid)[0]['_ref']
        # data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        # restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices", fields=json.dumps(data))
        # sleep(60)

        print("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(60)

    @pytest.mark.run(order=61)
    def test_061_Subscriber_service_scenario1_verify_anycast_stops_in_interim_state(self):
        print('################# SCENARIO 1 ##################')
        print('Set anycast restart behavior to ON, start subscriber service(goes to interim state), change anycast restart behavior to OFF, stop subscriber service')
        print('###############################################')
        sleep(80)
        check_able_to_login_appliances(config.grid_member2_vip)
        print("\n==========================================")
        print("change anycast behaviour in interim state scenario_1")
        print("\n==========================================")
        log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
        log("start","/var/log/syslog",config.grid_member2_vip)
        sleep(40)
        set_cli_anycast_restart_on(config.grid_vip)

        subscriber_start_services(config.grid_member2_fqdn)

        #dns_restart_services()
        sleep(80)

        check_process_response_when_SS_start(config.grid_member2_vip)

        set_cli_anycast_restart_off(config.grid_vip)

        subscriber_stop_services(config.grid_member2_fqdn)


        #dns_restart_services()
        sleep(80)

        check_process_ID_when_SS_start(config.grid_member2_vip)

        sleep(60)
        log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
        log("stop","/var/log/syslog",config.grid_member2_vip)

        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_member2_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member2_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*Stopping ospfd process.*",".*Stopping ospf6d process.*",".*Stopping zebra process.*",".*Starting bgpd process.*",".*Starting ospfd process.*",".*Starting ospf6d process.*"]

        LookFor_INFO_SS=[".*Sending state change trap for.*"+config.grid_member2_vip+".*imc_servers.*Subscriber Collection Service is inactive.*from 138 to 136.*",".*Sending state change trap for.*"+config.grid_member2_vip+".*imc_servers.*Subscriber Collection Service failed.*from 136 to 134.*",".*Sending state change trap for.*"+config.grid_member2_vip+".*imc_servers.*Initial Subscriber Collection service interim Interval.*from 134 to 138",".*Subscriber Collection Service is working.*from 138 to 133"]

        LookFor_sys=[".*info shutting down.*",".*notice exiting.*",".*notice starting BIND.*Supported Preview Version.*",".*notice running on Linux.*",".*info all zones loaded.*",".*notice running.*",".*notice Zebra.*starting.*",".*bgpd.*notice BGPd.*starting.*, bgp.*",".*notice OSPFd.*starting.*",".*ospf6d.*notice OSPF6d.*starts.*"]

        #LookFor_SYS_SS=[".*Initial Subscriber Collection service interim Interval state change from 136 to 138.*",".*Subscriber Collection Service failed state change from 136 to 134.*",".*Initial Subscriber Collection service interim Interval state change from 134 to 138.*"]

        flag_info=0
        flag_sys=0
        flag_ss_info=False
        flag_ss_sys=False

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1

        for look in LookFor_INFO_SS:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_ss_info=True

        # for look in LookFor_SYS_SS:
            # print(look)
            # logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            # print(logs)
            # if logs:
                # flag_ss_sys=True


        print(flag_info,flag_sys,flag_ss_info)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys) and flag_ss_info==True:
            assert True
        else:
            assert False
    @pytest.mark.run(order=62)
    def test_062_Subscriber_service_scenario2_verify_anycast_stops_in_interim_state(self):
        print('################# SCENARIO 2 ##################')
        print('Set anycast restart behavior to OFF, start subscriber service(goes to interim state), change anycast restart behavior to ON, stop subscriber service')
        print('###############################################')

        print("\n==========================================")
        print("change anycast behaviour in interim state scenario_2")
        print("\n==========================================")
        check_able_to_login_appliances(config.grid_member2_vip)
        log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
        log("start","/var/log/syslog",config.grid_member2_vip)
        sleep(30)
        set_cli_anycast_restart_off(config.grid_vip)


        subscriber_start_services(config.grid_member2_fqdn)

        #dns_start_services(config.grid_fqdn)
        sleep(80)

        check_process_response_when_SS_start(config.grid_member2_vip)

        set_cli_anycast_restart_on(config.grid_vip)

        subscriber_stop_services(config.grid_member2_fqdn)


        #dns_restart_services()
        sleep(80)

        check_process_ID_when_SS_start(config.grid_member2_vip)
        sleep(60)
        log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
        log("stop","/var/log/syslog",config.grid_member2_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_member2_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member2_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*Stopping ospfd process.*",".*Stopping ospf6d process.*",".*Stopping bgpd process.*",".*Stopping zebra process.*",".*Starting zebra process.*",".*Starting bgpd process.*",".*Starting ospfd process.*",".*Starting ospf6d process.*"]

        LookFor_INFO_SS=[".*Sending state change trap for.*"+config.grid_member2_vip+".*imc_servers.*Subscriber Collection Service is inactive.*from 138 to 136.*",".*Sending state change trap for.*"+config.grid_member2_vip+".*imc_servers.*Subscriber Collection Service failed.*from 136 to 134.*",".*Sending state change trap for.*"+config.grid_member2_vip+".*imc_servers.*Initial Subscriber Collection service interim Interval.*from 134 to 138"]

        LookFor_sys=[".*info shutting down.*",".*notice exiting.*",".*notice starting BIND.*(Supported Preview Version).*",".*notice running on.*",".*notice running.*",".*notice starting BIND.*(Supported Preview Version).*",".*notice running on Linux.*",".*notice running.*",".*notice Zebra.*starting.*",".*bgpd.*notice BGPd.*starting.*",".*notice OSPFd.*starting.*",".*ospf6d.*notice OSPF6d.*starts.*"]

        #LookFor_SYS_SS=[".*infoblox.localdomain monitor.*err Type.*IMC, State.*Yellow, Event.*Initial Subscriber Collection service interim Interval state change from 136 to 138.*",".*infoblox.localdomain monitor.*alert Type.*IMC, State.*Red, Event.*Subscriber Collection Service failed state change from 136 to 134.*",".*infoblox.localdomain monitor.*err Type.*IMC, State.*Yellow, Event.*Initial Subscriber Collection service interim Interval state change from 134 to 138.*"]

        flag_info=0
        flag_sys=0
        flag_ss_info=False
        flag_ss_sys=False

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1


        for look in LookFor_INFO_SS:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_ss_info=True

        # for look in LookFor_SYS_SS:
            # print(look)
            # logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            # print(logs)
            # if logs:
                # flag_ss_sys=True


        print(flag_info,flag_sys,flag_ss_info)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys) and flag_ss_info==True:
            assert True
        else:
            assert False

    @pytest.mark.run(order=63)
    def test_063_Subscriber_service_scenario3_verify_anycast_stops_in_interim_state(self):
        print('################# SCENARIO 3 ##################')
        print('Set anycast restart behavior to ON, start subscriber service(goes to interim state), stop subscriber service')
        print('###############################################')

        print("\n==========================================")
        print("change anycast behaviour in interim state scenario_3")
        print("\n==========================================")
        log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
        log("start","/var/log/syslog",config.grid_member2_vip)
        sleep(30)
        set_cli_anycast_restart_on(config.grid_vip)


        subscriber_start_services(config.grid_member2_fqdn)

        #dns_start_services(config.grid_fqdn)
        sleep(80)

        check_process_response_when_SS_start(config.grid_member2_vip)


        subscriber_stop_services(config.grid_member2_fqdn)
        sleep(80)

        #dns_restart_services()
        check_process_ID_when_SS_start(config.grid_member2_vip)
        sleep(40)
        log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
        log("stop","/var/log/syslog",config.grid_member2_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_member2_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member2_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")

        LookFor_info=[".*Stopping ospfd process.*",".*Stopping ospf6d process.*",".*Stopping zebra process.*",".*Starting bgpd process.*",".*Starting ospfd process.*",".*Starting ospf6d process.*"]

        LookFor_INFO_SS=[".*Sending state change trap for.*"+config.grid_member2_vip+".*imc_servers.*Subscriber Collection Service is inactive.*from 138 to 136.*",".*Sending state change trap for.*"+config.grid_member2_vip+".*imc_servers.*Subscriber Collection Service failed.*from 136 to 134.*",".*Sending state change trap for.*"+config.grid_member2_vip+".*imc_servers.*Initial Subscriber Collection service interim Interval.*from 134 to 138",".*Subscriber Collection Service is working.*from 138 to 133"]

        LookFor_sys=[".*info ospfTrapIfStateChange trap sent.*1.3.3.3 now Down.*",".*notice exiting.*",".*notice starting BIND.*(Supported Preview Version).*",".*notice running on Linux.*",".*info all zones loaded.*",".*notice running.*",".*notice Zebra.*starting.*",".*bgpd.*notice BGPd.*starting.*, bgp.*",".*notice OSPFd.*starting.*",".*ospf6d.*notice OSPF6d.*starts.*"]

        #LookFor_SYS_SS=[".*Initial Subscriber Collection service interim Interval state change from 136 to 138.*",".*Subscriber Collection Service failed state change from 136 to 134.*",".*Initial Subscriber Collection service interim Interval state change from 134 to 138.*"]

        flag_info=0
        flag_sys=0
        flag_ss_info=False
        flag_ss_sys=False

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1

        for look in LookFor_INFO_SS:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_ss_info=True

        # for look in LookFor_SYS_SS:
            # print(look)
            # logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            # print(logs)
            # if logs:
                # flag_ss_sys=True


        print(flag_info,flag_sys,flag_ss_info)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys) and flag_ss_info==True:
            assert True
        else:
            assert False

    @pytest.mark.run(order=64)
    def test_064_Subscriber_service_scenario4_verify_anycast_stops_in_interim_state(self):
        print('################# SCENARIO 4 ##################')
        print('Set anycast restart behavior to OFF, start subscriber service(goes to interim state), stop subscriber service')
        print('###############################################')

        print("\n==========================================")
        print("change anycast behaviour in interim state scenario_4")
        print("\n==========================================")

        log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
        log("start","/var/log/syslog",config.grid_member2_vip)
        sleep(30)
        set_cli_anycast_restart_off(config.grid_vip)


        subscriber_start_services(config.grid_member2_fqdn)

        #dns_start_services(config.grid_fqdn)
        sleep(80)

        check_process_response_when_SS_start(config.grid_member2_vip)


        subscriber_stop_services(config.grid_member2_fqdn)

        #dns_restart_services()
        sleep(80)

        check_process_ID_when_SS_start(config.grid_member2_vip)
        sleep(60)
        log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
        log("stop","/var/log/syslog",config.grid_member2_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_member2_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member2_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")

        LookFor_info=[".*Stopping ospfd process.*",".*Stopping ospf6d process.*",".*Stopping bgpd process.*",".*Stopping zebra process.*",".*/infoblox/one/bin/anycast_control.*Starting zebra process.*",".*Starting bgpd process.*",".*Starting ospfd process.*",".*Starting ospf6d process.*"]

        LookFor_INFO_SS=[".*Sending state change trap for.*"+config.grid_member2_vip+".*imc_servers.*Subscriber Collection Service is inactive.*from 138 to 136.*",".*Sending state change trap for.*"+config.grid_member2_vip+".*imc_servers.*Subscriber Collection Service failed.*from 136 to 134.*",".*Sending state change trap for.*"+config.grid_member2_vip+".*imc_servers.*Initial Subscriber Collection service interim Interval.*from 134 to 138"]

        LookFor_sys=[".*bgpd.*notice Terminating on signal.*",".*notice exiting.*",".*notice starting BIND.*(Supported Preview Version).*",".*notice running on.*",".*notice running.*",".*notice starting BIND.*(Supported Preview Version).*",".*notice running on Linux.*",".*notice running.*",".*notice Zebra.*starting.*",".*bgpd.*notice BGPd.*starting.*",".*notice OSPFd.*starting.*",".*ospf6d.*notice OSPF6d.*starts.*"]

        #LookFor_SYS_SS=[".*Initial Subscriber Collection service interim Interval state change from 136 to 138.*",".*Subscriber Collection Service failed state change from 136 to 134.*",".*Initial Subscriber Collection service interim Interval state change from 134 to 138.*"]

        flag_info=0
        flag_sys=0
        flag_ss_info=False
        flag_ss_sys=False

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1

        for look in LookFor_INFO_SS:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_ss_info=True

        # for look in LookFor_SYS_SS:
            # print(look)
            # logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            # print(logs)
            # if logs:
                # flag_ss_sys=True


        print(flag_info,flag_sys,flag_ss_info)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys) and flag_ss_info==True:
            assert True
        else:
            assert False


    @pytest.mark.run(order=65)
    def test_065_Change_the_interim_time_of_subscriber_service_and_change_the_subscriber_state_to_green(self):

        get_ref = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriber")
        print(get_ref)
        data={"enable_parental_control": False,
              "cat_acctname":"infoblox_sdk",
              "cat_password":"LinWmRRDX0q",
              "category_url":"https://dl.zvelo.com/",
              "proxy_url":"http://10.196.9.113:8001",
              "proxy_username":"client",
              "proxy_password":"infoblox",
              "pc_zone_name":"rfe_10176.zone.com",
              "cat_update_frequency":24}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]["_ref"],fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Disabled parental control")
                assert False
        sleep(30)

        print("\n==========================================")
        print("Setting interim time to 2 minute")
        print("\n==========================================")

        get_ref = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriber")
        print(get_ref)
        data={"interim_accounting_interval":2}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]["_ref"],fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Setting interim time")
                assert False


        dns_restart_services()

        set_recursive_query_true_for_restart_pending_changes(config.grid_member2_fqdn)

        log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
        sleep(10)
        subscriber_start_services(config.grid_member2_fqdn)

        sleep(180)
        check_able_to_login_appliances(config.grid_vip)

        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
        print("\n********************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_member2_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n********************************************************")

        #look=".*Sending state change trap for.*"+config.grid_vip+".*- imc_servers (Subscriber Collection Service is working) from 138 to 133.*"
        look=".*Subscriber Collection Service is working.*from 138 to 133.*"

        logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member2_vip)

        print(logs)
        if logs:
            print("Subscriber is working.......!")
            assert True
        else:
            print("Subscriber is NOT working.......!")
            assert False

        LookFor_info=[".*Starting zebra process.*",".*Starting bgpd process.*",".*Starting ospfd process.*",".*Starting ospf6d process.*"]

        flag_info=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        print(flag_info)

        if flag_info==len(LookFor_info):
            assert True
        else:
            assert False


    @pytest.mark.run(order=66)
    def test_066_Restart_DNS_normally_with_Subscriber_service_enabled_and_anycast_restart_behavior_ON(self):
        sleep(60)
        check_able_to_login_appliances(config.grid_member2_vip)
        print("\n==========================================")
        print("Restart DNS services normally")
        print("\n==========================================")

        set_cli_anycast_restart_on(config.grid_vip)

        log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
        log("start","/var/log/syslog",config.grid_member2_vip)
        sleep(20)
        check_process_ID_when_SS_start(config.grid_member2_vip)
        sleep(40)
        dns_restart_services_normally()
        sleep(40)

        log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
        log("stop","/var/log/syslog",config.grid_member2_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_member2_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member2_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*Stopping ospfd process.*",".*Stopping ospf6d process.*",".*Stopping bgpd process.*",".*Stopping zebra process.*",".*Starting zebra process.*",".*Starting bgpd process.*",".*Starting ospfd process.*",".*Starting ospf6d process.*"]


        LookFor_sys=[".*info shutting down.*",".*info no longer listening on.*"+config.grid_member2_vip+".*",".*info no longer listening on 3333::3331.*",".*info no longer listening on.*"+config.grid_member2_ipv6+".*",".*notice exiting.*",".*notice starting BIND.*",".*notice running on Linux.*",".*info listening on IPv4 interface eth1.*"+config.grid_member2_vip+".*",".*info listening on IPv6 interface eth1.*"+config.grid_member2_ipv6+".*",".*info all zones loaded.*",".*notice running.*",".*notice Zebra.*starting.*",".*notice OSPFd.*starting.*",".*ospf6d.*notice OSPF6d .*starts.*"]

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)

        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            print("Did not request for restart")


    @pytest.mark.run(order=67)
    def test_067_Restart_DNS_forcefully_with_Subscriber_service_enabled_and_anycast_restart_behavior_ON(self):
        print("\n==========================================")
        print("Restart DNS services forcefully")
        print("\n==========================================")

        log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
        log("start","/var/log/syslog",config.grid_member2_vip)
        sleep(10)
        dns_restart_services()
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
        log("stop","/var/log/syslog",config.grid_member2_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_member2_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member2_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*Stopping ospfd process.*",".*Stopping ospf6d process.*",".*Stopping bgpd process.*",".*Stopping zebra process.*",".*Starting zebra process.*",".*Starting bgpd process.*",".*Starting ospfd process.*",".*Starting ospf6d process.*"]


        LookFor_sys=[".*info shutting down.*",".*info no longer listening on.*"+config.grid_member2_vip+".*",".*info no longer listening on 3333::3331.*",".*info no longer listening on.*"+config.grid_member2_ipv6+".*",".*notice exiting.*",".*notice starting BIND.*",".*notice running on Linux.*",".*info listening on IPv4 interface eth1.*"+config.grid_member2_vip+".*",".*info listening on IPv6 interface eth1.*"+config.grid_member2_ipv6+".*",".*info all zones loaded.*",".*notice running.*",".*notice Zebra.*starting.*",".*notice OSPFd.*starting.*",".*ospf6d.*notice OSPF6d .*starts.*"]
        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False

    @pytest.mark.run(order=68)
    def test_068_Stop_DNS_with_Subscriber_service_enabled_and_anycast_restart_behavior_ON(self):
        print("\n==========================================")
        print("Stop DNS service")
        print("\n==========================================")

        log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
        log("start","/var/log/syslog",config.grid_member2_vip)
        sleep(10)
        dns_stop_services(config.grid_member2_fqdn)
        sleep(30)
        log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
        log("stop","/var/log/syslog",config.grid_member2_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_member2_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member2_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*stopping named services.*",".*Stopping ospfd process.*",".*Stopping ospf6d process.*",".*Stopping bgpd process.*",".*Stopping zebra process.*"]


        LookFor_sys=[".*info shutting down.*",".*info no longer listening on.*"+config.grid_member2_vip+".*",".*info no longer listening on 3333::3331.*",".*info no longer listening on.*"+config.grid_member2_ipv6+".*",".*notice exiting.*"]
        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False


    @pytest.mark.run(order=69)
    def test_069_Start_DNS_with_Subscriber_service_enabled_and_anycast_restart_behavior_ON(self):
        print("\n==========================================")
        print("Start DNS services ")
        print("\n==========================================")
        log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
        log("start","/var/log/syslog",config.grid_member2_vip)
        sleep(10)
        dns_start_services(config.grid_member2_fqdn)
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
        log("stop","/var/log/syslog",config.grid_member2_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_member2_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member2_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*Starting zebra process.*",".*Starting bgpd process.*",".*Starting ospfd process.*",".*Starting ospf6d process.*"]


        LookFor_sys=[".*notice starting BIND.*",".*notice running on Linux.*",".*info listening on IPv4 interface eth1.*"+config.grid_member2_vip+".*",".*info listening on IPv6 interface eth1.*"+config.grid_member2_ipv6+".*",".*info all zones loaded.*",".*notice running.*",".*notice Zebra.*starting.*",".*notice BGPd.*starting.*bgp.*",".*notice OSPFd.*starting.*"]
        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False



    @pytest.mark.run(order=71)
    def test_070_Restart_DNS_normally_with_Subscriber_service_enabled_and_anycast_restart_behavior_OFF(self):
        print("\n==========================================")
        print("Restart DNS services normally")
        print("\n==========================================")

        set_cli_anycast_restart_off(config.grid_vip)

        set_recursive_query_false_for_restart_pending_changes(config.grid_member2_fqdn)

        log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
        log("start","/var/log/syslog",config.grid_member2_vip)
        sleep(10)
        dns_restart_services_normally()
        sleep(40)
        log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
        log("stop","/var/log/syslog",config.grid_member2_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_member2_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member2_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info_not=[".*Stopping ospfd process.*",".*Stopping ospf6d process.*",".*Stopping bgpd process.*",".*Stopping zebra process.*",".*Starting zebra process.*",".*Starting bgpd process.*",".*Starting ospfd process.*",".*Starting ospf6d process.*"]


        LookFor_sys_not=[".*ospf6d.*notice OSPF6d .*starts.*"]



        LookFor_info=[]

        LookFor_sys=[".*info shutting down.*",".*notice stopping command channel on.*",".*info no longer listening on.*",".*info no longer listening on 3333::3331.*",".*info no longer listening on "+config.grid_member2_ipv6+".*",".*notice exiting.*",".*notice starting BIND.*(Supported Preview Version).*",".*notice running on Linux.*",".*info listening on IPv6 interface eth1, "+config.grid_member2_ipv6+".*",".*info all zones loaded.*",".*notice running.*"]

        flag_info_not=1
        flag_sys_not=1

        for look in LookFor_info_not:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_info_not=0

        for look in LookFor_sys_not:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_sys_not=0

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info_not,flag_sys_not,flag_info,flag_sys)
        if flag_info_not==1 and flag_sys_not==1 and flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False

    @pytest.mark.run(order=71)
    def test_071_Restart_DNS_forcefullyy_with_Subscriber_service_enabled_and_anycast_restart_behavior_OFF(self):
        print("\n==========================================")
        print("Restart DNS services forcefully")
        print("\n==========================================")

        log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
        log("start","/var/log/syslog",config.grid_member2_vip)
        sleep(10)
        dns_restart_services()
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
        log("stop","/var/log/syslog",config.grid_member2_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_member2_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member2_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info_not=[".*Stopping ospfd process.*",".*Stopping ospf6d process.*",".*Stopping bgpd process.*",".*Stopping zebra process.*",".*Starting zebra process.*",".*Starting bgpd process.*",".*Starting ospfd process.*",".*Starting ospf6d process.*"]


        LookFor_sys_not=[".*ospf6d.*notice OSPF6d .*starts.*"]



        LookFor_info=[]

        LookFor_sys=[".*info shutting down.*",".*notice stopping command channel on.*",".*info no longer listening on.*",".*info no longer listening on 3333::3331.*",".*info no longer listening on "+config.grid_member2_ipv6+".*",".*notice exiting.*",".*notice starting BIND.*(Supported Preview Version).*",".*notice running on Linux.*",".*info listening on IPv6 interface lo.*, 3333::3331.*",".*info listening on IPv6 interface eth1, "+config.grid_member2_ipv6+".*",".*info all zones loaded.*",".*notice running.*"]


        flag_info_not=1
        flag_sys_not=1

        for look in LookFor_info_not:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_info_not=0

        for look in LookFor_sys_not:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_sys_not=0

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info_not,flag_sys_not,flag_info,flag_sys)
        if flag_info_not==1 and flag_sys_not==1 and flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False




    @pytest.mark.run(order=72)
    def test_072_Stop_DNS_with_Subscriber_service_enabled_and_anycast_restart_behavior_OFF(self):
        print("\n==========================================")
        print("Stop DNS services ")
        print("\n==========================================")

        log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
        log("start","/var/log/syslog",config.grid_member2_vip)
        sleep(10)
        dns_stop_services(config.grid_member2_fqdn)

        sleep(60)
        log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
        log("stop","/var/log/syslog",config.grid_member2_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_member2_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member2_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")

        LookFor_info=[".*stopping named services.*",".*Stopping bgpd process.*",".*Stopping zebra process.*"]

        LookFor_sys=[".*info shutting down.*",".*notice stopping command.*",".*info no longer listening on.*",".*info no longer listening on 3333::3331.*",".*info no longer listening on "+config.grid_member2_ipv6+".*",".*notice exiting.*"]

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False

    @pytest.mark.run(order=73)
    def test_073_Start_DNS_with_Subscriber_service_enabled_and_anycast_restart_behavior_OFF(self):
        print("\n==========================================")
        print("Start DNS services ")
        print("\n==========================================")

        log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
        log("start","/var/log/syslog",config.grid_member2_vip)
        sleep(10)
        dns_start_services(config.grid_member2_fqdn)
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
        log("stop","/var/log/syslog",config.grid_member2_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_member2_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member2_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")

        LookFor_info=[".*Starting zebra process.*",".*Starting bgpd process.*"]

        LookFor_sys=[".*notice starting BIND.*(Supported Preview Version).*",".*notice running on Linux.*",".*info listening on IPv4 interface lo.*",".*info listening on IPv6 interface lo.*, 3333::3331.*",".*info listening on IPv6 interface eth1.*"+config.grid_member2_ipv6+".*",".*info all zones loaded.*",".*notice running.*",".*notice Zebra.*starting.*",".*notice BGPd.*starting.*bgp.*"]


        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member2_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            subscriber_stop_services(config.grid_member2_fqdn)
            zone=ib_NIOS.wapi_request('GET',object_type='zone_auth')
            print(zone)
            zone_ref=json.loads(zone)
            for ref in zone_ref:
                if ref["fqdn"]=="rfe_10176.zone.com":
                    ref_del=ref['_ref']
                    del_zone=ib_NIOS.wapi_request('DELETE',ref=ref_del)
                    print(del_zone)
                    dns_restart_services()
            assert True
        else:
            assert False

    @pytest.mark.run(order=74)
    def test_074_Verify_audit_log_when_the_anycast_restart_behavior_is_set_to_ON(self):
        check_able_to_login_appliances(config.grid_member2_vip)
        print("\n====================================")
        print("\n Checking Audit in ON behavior")
        print("\n====================================")
        check_able_to_login_appliances(config.grid_vip)
        log("start","/infoblox/var/audit.log",config.grid_vip)
        set_cli_anycast_restart_on(config.grid_vip)
        sleep(20)
        log("stop","/infoblox/var/audit.log",config.grid_vip)
        print("\n********************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_audit.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n********************************************************")
        LookFor_audit=[".*admin.*Called.*set_restart_anycast_with_dns_restart.*enable_anycast_restart.*true from false.*"]
        flag_audit=0

        for look in LookFor_audit:
            print(look)
            logs=logv(look,"/infoblox/var/audit.log",config.grid_vip)
            print(logs)
            if logs:
                flag_audit=flag_audit+1


        print(flag_audit)
        if flag_audit==len(LookFor_audit):
            assert True
        else:
            assert False

    @pytest.mark.run(order=75)
    def test_075_Verify_audit_log_when_the_anycast_restart_behavior_is_set_to_OFF(self):
        check_able_to_login_appliances(config.grid_vip)
        print("\n====================================")
        print("\n Checking Audit in OFF behavior")
        print("\n====================================")
        check_able_to_login_appliances(config.grid_vip)
        log("start","/infoblox/var/audit.log",config.grid_vip)
        set_cli_anycast_restart_off(config.grid_vip)
        sleep(20)
        log("stop","/infoblox/var/audit.log",config.grid_vip)
        print("\n********************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey=mykey)
        data="cat /tmp/"+config.grid_vip+"_infoblox_var_audit.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n********************************************************")
        LookFor_audit=[".*admin.*Called.*set_restart_anycast_with_dns_restart.*enable_anycast_restart.*false from true.*"]
        flag_audit=0

        for look in LookFor_audit:
            print(look)
            logs=logv(look,"/infoblox/var/audit.log",config.grid_vip)
            print(logs)
            if logs:
                flag_audit=flag_audit+1


        print(flag_audit)
        if flag_audit==len(LookFor_audit):
            assert True
        else:
            assert False

    @pytest.mark.run(order=76)
    def test_076_add_a_DTC_Server1(self):
        logging.info("Creating zone abc.com")
        data={"fqdn":"abc.com","view":"default","grid_primary":[{"name": config.grid_member3_fqdn,"stealth": False}]}
        zone_ref=ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data))
        logging.info(zone_ref)
        print(zone_ref)
        if bool(re.match("\"zone_auth*.",str(zone_ref))):
            logging.info("abc.com created succesfully")
            logging.info("Restart services")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            sleep(20)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            sleep(20)

        else:
            raise Exception("abc.com creation unsuccessful")
        logging.info("Creating dtc server1")
        data={"host": config.grid_vip,"monitors": [{"host": config.grid_vip,"monitor": "dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"}],"name": "server1"}
        server1_ref=ib_NIOS.wapi_request('POST',object_type='dtc:server',fields=json.dumps(data))
        logging.info(server1_ref)
        print(server1_ref)
        if bool(re.match("\"dtc:server*.",str(server1_ref))):
            logging.info("dtc server1 created succesfully")
        else:
            raise Exception("dtc server1 creation unsuccessful")


    @pytest.mark.run(order=77)
    def test_077_add_a_DTC_Server2(self):
        logging.info("Creating dtc server2")
        data={"host": config.grid_member1_vip,"monitors": [{"host": config.grid_member1_vip,"monitor": "dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"}],"name": "server2"}
        server2_ref=ib_NIOS.wapi_request('POST',object_type='dtc:server',fields=json.dumps(data))
        logging.info(server2_ref)
        print(server2_ref)
        if bool(re.match("\"dtc:server*.",str(server2_ref))):
            logging.info("dtc server2 created succesfully")
        else:
            raise Exception("dtc server2 creation unsuccessful")

    @pytest.mark.run(order=78)
    def test_078_add_a_DTC_pool(self):
        logging.info("Creating dtc pool")
        server=ib_NIOS.wapi_request('GET',object_type='dtc:server')
        server1=json.loads(server)[0]['_ref']
        server2=json.loads(server)[1]['_ref']
        data={"name": "pool","lb_preferred_method": "ROUND_ROBIN","monitors": ["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"],"servers": [{"ratio": 1,"server": server1},{"ratio": 1,"server": server2}]}
        pool_ref=ib_NIOS.wapi_request('POST',object_type='dtc:pool',fields=json.dumps(data))
        logging.info(pool_ref)
        print(pool_ref)
        if bool(re.match("\"dtc:pool*.",str(pool_ref))):
            logging.info("pool created succesfully")
        else:
            raise Exception("pool creation unsuccessful")



    @pytest.mark.run(order=79)
    def test_079_add_a_DTC_lbdn(self):
        logging.info("Creating lbdn")
        zone=ib_NIOS.wapi_request('GET',object_type='zone_auth')
        zone_ref=json.loads(zone)[0]['_ref']
        pool=ib_NIOS.wapi_request('GET',object_type='dtc:pool')
        pool_ref=json.loads(pool)[0]['_ref']
        data={"name": "lbdn1","lb_method": "ROUND_ROBIN","patterns": ["b2.abc.com"],"auth_zones": [zone_ref],"pools": [{"pool": pool_ref,"ratio": 1}]}
        lbdn_ref=ib_NIOS.wapi_request('POST',object_type='dtc:lbdn',fields=json.dumps(data))
        logging.info(lbdn_ref)
        print(lbdn_ref)
        if bool(re.match("\"dtc:lbdn*.",str(lbdn_ref))):
            logging.info("lbdn created succesfully")
            logging.info("Restart services")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
            ref = json.loads(grid)[0]['_ref']
            data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
            sleep(20)
        else:
            raise Exception("lbdn creation unsuccessful")


    '''@pytest.mark.run(order=80)
    def test_080_assign_servers_to_pool_monitor(self):
        print("Assign_servers_to_pool_monitor")
        get_ref = ib_NIOS.wapi_request('GET', object_type="dtc:monitor:http",grid_vip=config.grid_member3_vip)
        monitor=""
        for ref in json.loads(get_ref):
            if not'https' in ref['_ref']:
                monitor=ref['_ref']

        get_ref_mem = ib_NIOS.wapi_request('GET', object_type="member",grid_vip=config.grid_member3_vip)

        memb=[]
        ind=1
        for ref in json.loads(get_ref_mem):
            if config.grid_member3_fqdn in ref['_ref']:
                memb.append(config.grid_member3_fqdn)
            # if config.grid_member2_fqdn in ref['_ref']:
                # memb.append(config.grid_member2_fqdn)

        get_ref_pool = ib_NIOS.wapi_request('GET', object_type="dtc:pool",grid_vip=config.grid_member3_vip)
        print(get_ref_pool)
        print(memb)
        for ref in json.loads(get_ref_pool):
            if 'pool_p' in ref['_ref']:
                get_ref = ib_NIOS.wapi_request('GET', object_type=ref['_ref']+"?_return_fields=consolidated_monitors")
                data = {"consolidated_monitors": [{"availability": "ALL","members": memb,"monitor": monitor}]}

                # data = {"consolidated_monitors": [{"availability": "ALL","full_health_communication": True,"members": [config.grid_member1_fqdn,config.grid_member2_fqdn],"monitor":"dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"}]}
                response = ib_NIOS.wapi_request('PUT',ref=ref['_ref'], fields=json.dumps(data))
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: Assign_servers_to_pool_monitor")
                        assert False
                    else:
                        print("Success: Assign_servers_to_pool_monitor")
                        assert True
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)'''


    @pytest.mark.run(order=81)
    def test_081_set_anycast_restart_behavior_to_ON(self):
        set_cli_anycast_restart_on(config.grid_vip)

    @pytest.mark.run(order=82)
    def test_082_Restart_DNS_normally_with_DTC_and_anycast_restart_behavior_set_to_ON(self):
        print("\n====================================")
        print("\n Restart DNS services normally")
        print("\n====================================")

        set_recursive_query_true_for_restart_pending_changes(config.grid_member3_fqdn)

        log("start","/infoblox/var/infoblox.log",config.grid_member3_vip)
        log("start","/var/log/syslog",config.grid_member3_vip)

        dns_restart_services_normally()
        log("stop","/infoblox/var/infoblox.log",config.grid_member3_vip)
        log("stop","/var/log/syslog",config.grid_member3_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, password='infoblox')
        data="cat /tmp/"+config.grid_member3_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member3_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*/infoblox/one/bin/anycast_control).*Stopping ospfd process.*",".*/infoblox/one/bin/anycast_control).*Stopping ospf6d process.*",".*/infoblox/one/bin/anycast_control).*Stopping bgpd process.*",".*/infoblox/one/bin/anycast_control).*Stopping zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting bgpd process.*",".*/infoblox/one/bin/anycast_control).*Starting ospfd process.*",".*/infoblox/one/bin/anycast_control).*Starting ospf6d process.*"]


        LookFor_sys=[".*named.*info shutting down.*",".*named.*notice exiting.*",".*named.*notice starting BIND.*",".*named.*notice running on Linux.*",".*named.*info all zones loaded.*",".*named.*notice running.*",".*zebra.*notice Zebra.*starting.*",".*ospfd.*notice OSPFd.*starting.*",".*ospf6d.*notice OSPF6d .*starts.*"]


        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member3_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member3_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1

        print(flag_info,flag_sys)

        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False


    @pytest.mark.run(order=83)
    def test_083_Restart_DNS_forcefully_with_DTC_and_anycast_restart_behavior_set_to_ON(self):
        print("\n====================================")
        print("\n Restart DNS services FORCE_RESTART")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_member3_vip)
        log("start","/var/log/syslog",config.grid_member3_vip)

        dns_restart_services()
        log("stop","/infoblox/var/infoblox.log",config.grid_member3_vip)
        log("stop","/var/log/syslog",config.grid_member3_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, password = 'infoblox')
        data="cat /tmp/"+config.grid_member3_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member3_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*/infoblox/one/bin/anycast_control).*Stopping ospfd process.*",".*/infoblox/one/bin/anycast_control).*Stopping ospf6d process.*",".*/infoblox/one/bin/anycast_control).*Stopping bgpd process.*",".*/infoblox/one/bin/anycast_control).*Stopping zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting bgpd process.*",".*/infoblox/one/bin/anycast_control).*Starting ospfd process.*",".*/infoblox/one/bin/anycast_control).*Starting ospf6d process.*"]


        LookFor_sys=[".*named.*info shutting down.*",".*named.*notice exiting.*",".*named.*notice starting BIND.*",".*named.*notice running on Linux.*",".*named.*info all zones loaded.*",".*named.*notice running.*",".*zebra.*notice Zebra.*starting.*",".*ospfd.*notice OSPFd.*starting.*",".*ospf6d.*notice OSPF6d .*starts.*"]


        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member3_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member3_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1

        print(flag_info,flag_sys)

        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False


    @pytest.mark.run(order=84)
    def test_084_Stop_DNS_with_DTC_and_anycast_restart_behavior_set_to_ON(self):

        print("\n====================================")
        print("\n Stop DNS services")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_member3_vip)
        log("start","/var/log/syslog",config.grid_member3_vip)

        dns_stop_services(config.grid_member3_fqdn)
        log("stop","/infoblox/var/infoblox.log",config.grid_member3_vip)
        log("stop","/var/log/syslog",config.grid_member3_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, password = 'infoblox')
        data="cat /tmp/"+config.grid_member3_vip+"_vip_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member3_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*/infoblox/dns/bin/stop_dns_service).*stopping named services.*",".*/infoblox/one/bin/anycast_control).*Stopping ospfd process.*",".*/infoblox/one/bin/anycast_control).*Stopping ospf6d process.*",".*/infoblox/one/bin/anycast_control).*Stopping bgpd process.*",".*/infoblox/one/bin/firewall).*Disabled firewall BGP.*",".*/infoblox/one/bin/anycast_control).*Stopping zebra process.*"]


        LookFor_sys=[".*named.*info shutting down.*",".*named.*notice exiting.*"]

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member3_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member3_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False


    @pytest.mark.run(order=85)
    def test_085_Start_DNS_with_DTC_and_anycast_restart_behavior_set_to_ON(self):
        print("\n====================================")
        print("\n Start DNS services ")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_member3_vip)
        log("start","/var/log/syslog",config.grid_member3_vip)

        dns_start_services(config.grid_member3_fqdn)
        log("stop","/infoblox/var/infoblox.log",config.grid_member3_vip)
        log("stop","/var/log/syslog",config.grid_member3_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, password = 'infoblox')
        data="cat /tmp/"+config.grid_member3_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member3_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*/infoblox/one/bin/anycast_control).*Starting zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting bgpd process.*",".*/infoblox/one/bin/anycast_control).*Starting ospfd process.*",".*/infoblox/one/bin/anycast_control).*Starting ospf6d process.*"]


        LookFor_sys=[".*named.*notice starting BIND.*",".*named.*notice running on Linux.*",".*named.*info all zones loaded.*",".*named.*notice running.*",".*zebra.*notice Zebra.*starting.*",".*bgpd.*notice BGPd.*starting.*bgp.*",".*ospfd.*notice OSPFd.*starting.*"]

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member3_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member3_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False

    @pytest.mark.run(order=86)
    def test_086_set_anycast_restart_behavior_to_OFF(self):
        set_cli_anycast_restart_off(config.grid_vip)


    @pytest.mark.run(order=87)
    def test_087_Restart_DNS_normally_with_DTC_and_anycast_restart_behavior_set_to_OFF(self):
        print("\n====================================")
        print("\n Restart DNS services normally")
        print("\n====================================")

        set_recursive_query_false_for_restart_pending_changes(config.grid_member3_fqdn)

        log("start","/infoblox/var/infoblox.log",config.grid_member3_vip)
        log("start","/var/log/syslog",config.grid_member3_vip)

        dns_restart_services_normally()
        log("stop","/infoblox/var/infoblox.log",config.grid_member3_vip)
        log("stop","/var/log/syslog",config.grid_member3_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, password = 'infoblox')
        data="cat /tmp/"+config.grid_member3_vip+"_vip_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member3_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info_not=[".*/infoblox/one/bin/anycast_control).*Stopping ospfd process.*",".*/infoblox/one/bin/anycast_control).*Stopping ospf6d process.*",".*/infoblox/one/bin/anycast_control).*Stopping bgpd process.*",".*/infoblox/one/bin/anycast_control).*Stopping zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting bgpd process.*",".*/infoblox/one/bin/anycast_control).*Starting ospfd process.*",".*/infoblox/one/bin/anycast_control).*Starting ospf6d process.*"]


        LookFor_sys_not=[".*zebra.*notice client.*disconnected.*ospf routes removed from the rib.*",".*ospfd.*notice Terminating on signal.*",".*ospfd.*info ospfTrapIfStateChange trap sent.*"+config.grid_vip+".*now Down.*",".*ospfd.*info ospfTrapIfStateChange trap sent: 1.3.3.3 now Down.*",".*ospfd.*info ospfTrapIfStateChange trap sent.*"+config.grid_vip+".*now DROther.*",".*ospf6d.*notice OSPF6d .*starts.*",".*zebra.*notice client.*says hello and bids fair to announce only ospf6 routes.*"]



        LookFor_info=[]

        LookFor_sys=[".*named.*info shutting down.*",".*named.*notice exiting.*",".*named.*notice starting BIND.*(Supported Preview Version).*",".*named.*notice running on Linux.*",".*named.*info all zones loaded.*",".*named.*notice running.*"]


        flag_info_not=1
        flag_sys_not=1

        for look in LookFor_info_not:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member3_vip)
            print(logs)
            if logs:
                flag_info_not=0

        for look in LookFor_sys_not:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member3_vip)
            print(logs)
            if logs:
                flag_sys_not=0

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member3_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member3_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info_not,flag_sys_not,flag_info,flag_sys)
        if flag_info_not==1 and flag_sys_not==1 and flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False



    @pytest.mark.run(order=88)
    def test_088_Restart_DNS_forcefully_with_DTC_and_anycast_restart_behavior_set_to_OFF(self):
        print("\n====================================")
        print("\n Restart DNS services FORCE_RESTART")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_member3_vip)
        log("start","/var/log/syslog",config.grid_member3_vip)

        dns_restart_services()
        log("stop","/infoblox/var/infoblox.log",config.grid_member3_vip)
        log("stop","/var/log/syslog",config.grid_member3_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, password = 'infoblox')
        data="cat /tmp/"+config.grid_member3_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member3_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info_not=[".*/infoblox/one/bin/anycast_control).*Stopping ospfd process.*",".*/infoblox/one/bin/anycast_control).*Stopping ospf6d process.*",".*/infoblox/one/bin/anycast_control).*Stopping bgpd process.*",".*/infoblox/one/bin/firewall).*Disabled firewall BGP.*",".*/infoblox/one/bin/anycast_control).*Stopping zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting bgpd process.*",".*/infoblox/one/bin/firewall).*Enabled firewall BGP.*",".*/infoblox/one/bin/anycast_control).*Starting ospfd process.*",".*/infoblox/one/bin/anycast_control).*Starting ospf6d process.*"]


        LookFor_sys_not=[".*zebra.*notice client.*disconnected.*ospf routes removed from the rib.*",".*ospfd.*notice Terminating on signal.*",".*ospfd.*info ospfTrapIfStateChange trap sent.*"+config.grid_vip+".*now Down.*",".*ospfd.*info ospfTrapIfStateChange trap sent: 1.3.3.3 now Down.*",".*ospfd.*info ospfTrapIfStateChange trap sent.*"+config.grid_vip+".*now DROther.*",".*ospf6d.*notice OSPF6d .*starts.*",".*zebra.*notice client.*says hello and bids fair to announce only ospf6 routes.*"]



        LookFor_info=[]

        LookFor_sys=[".*named.*info shutting down.*",".*named.*notice exiting.*",".*named.*notice starting BIND.*(Supported Preview Version).*",".*named.*notice running on Linux.*",".*named.*info all zones loaded.*",".*named.*notice running.*"]


        flag_info_not=1
        flag_sys_not=1

        for look in LookFor_info_not:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member3_vip)
            print(logs)
            if logs:
                flag_info_not=0

        for look in LookFor_sys_not:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member3_vip)
            print(logs)
            if logs:
                flag_sys_not=0

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member3_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member3_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info_not,flag_sys_not,flag_info,flag_sys)
        if flag_info_not==1 and flag_sys_not==1 and flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False



    @pytest.mark.run(order=89)
    def test_089_Stop_DNS_with_DTC_and_anycast_restart_behavior_set_to_OFF(self):
        print("\n====================================")
        print("\n Stop DNS services ")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_member3_vip)
        log("start","/var/log/syslog",config.grid_member3_vip)

        dns_stop_services(config.grid_member3_fqdn)
        sleep(40)
        log("stop","/infoblox/var/infoblox.log",config.grid_member3_vip)
        log("stop","/var/log/syslog",config.grid_member3_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, password = 'infoblox')
        data="cat /tmp/"+config.grid_member3_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member3_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")

        LookFor_info=[".*/infoblox/dns/bin/stop_dns_service).*stopping named services.*",".*/infoblox/one/bin/anycast_control).*Stopping bgpd process.*",".*/infoblox/one/bin/anycast_control).*Stopping zebra process.*"]

        LookFor_sys=[".*named.*info shutting down.*",".*named.*notice exiting.*"]

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member3_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member3_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1

        print(flag_info,flag_sys)

        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False

    @pytest.mark.run(order=90)
    def test_090_Start_DNS_with_DTC_and_anycast_restart_behavior_set_to_OFF(self):
        print("\n====================================")
        print("\n Start DNS services normally")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_member3_vip)
        log("start","/var/log/syslog",config.grid_member3_vip)

        dns_start_services(config.grid_member3_fqdn)
        sleep(30)
        log("stop","/infoblox/var/infoblox.log",config.grid_member3_vip)
        log("stop","/var/log/syslog",config.grid_member3_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, password = 'infoblox')
        data="cat /tmp/"+config.grid_member3_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member3_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*/infoblox/one/bin/anycast_control).*Starting zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting bgpd process.*",".*/infoblox/one/bin/anycast_control).*Starting ospfd process.*",".*/infoblox/one/bin/anycast_control).*Starting ospf6d process.*"]


        LookFor_sys=[".*named.*notice starting BIND.*",".*named.*notice running on Linux.*",".*named.*info all zones loaded.*",".*named.*notice running.*",".*zebra.*notice Zebra.*starting.*",".*bgpd.*notice BGPd.*starting.*bgp.*",".*ospfd.*notice OSPFd.*starting.*"]

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member3_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member3_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            zone=ib_NIOS.wapi_request('GET',object_type='zone_auth')
            print(zone)
            zone_ref=json.loads(zone)
            for ref in zone_ref:
                if ref["fqdn"]=="abc.com":
                    ref_del=ref['_ref']
                    del_zone=ib_NIOS.wapi_request('DELETE',ref=ref_del)
                    print(del_zone)
                    dns_restart_services()

            assert True
        else:
            assert False

    @pytest.mark.run(order=91)
    def test_091_enable_DCA_and_threat_protection_on_IB_FLEX(self):
        enable_dca(config.grid_vip,config.grid_member4_fqdn1)
        check_able_to_login_appliances(config.grid_member4_vip)
        configure_and_enable_threat_protection(config.grid_vip)
        check_able_to_login_appliances(config.grid_member4_vip)



    @pytest.mark.run(order=92)
    def test_092_Restart_DNS_normally_with_DCA_and_ADP_enabled_with_anycast_restart_behavior_ON(self):
        print("\n====================================")
        print("\n Restart DNS services normally")
        print("\n====================================")
        set_cli_anycast_restart_on(config.grid_vip)
        set_recursive_query_true_for_restart_pending_changes(config.grid_member4_fqdn1)

        log("start","/infoblox/var/infoblox.log",config.grid_member4_vip)
        log("start","/var/log/syslog",config.grid_member4_vip)
        sleep(10)
        dns_restart_services_normally()
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_member4_vip)
        log("stop","/var/log/syslog",config.grid_member4_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey = mykey)
        data="cat /tmp/"+config.grid_member4_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member4_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*/infoblox/one/bin/anycast_control).*Stopping ospfd process.*",".*/infoblox/one/bin/anycast_control).*Stopping ospf6d process.*",".*/infoblox/one/bin/anycast_control).*Stopping bgpd process.*",".*/infoblox/one/bin/anycast_control).*Stopping zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting bgpd process.*",".*/infoblox/one/bin/anycast_control).*Starting ospfd process.*",".*/infoblox/one/bin/anycast_control).*Starting ospf6d process.*"]


        LookFor_sys=[".*named.*info shutting down.*",".*named.*notice exiting.*",".*named.*notice starting BIND.*",".*named.*notice running on Linux.*",".*named.*info all zones loaded.*",".*named.*notice running.*",".*zebra.*notice Zebra.*starting.*",".*ospfd.*notice OSPFd.*starting.*",".*ospf6d.*notice OSPF6d .*starts.*",]


        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member4_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member4_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1

        print(flag_info,flag_sys)

        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False


    @pytest.mark.run(order=93)
    def test_093_Restart_DNS_forcefully_with_DCA_and_ADP_enabled_with_anycast_restart_behavior_ON(self):

        print("\n====================================")
        print("\n Restart DNS services FORCE_RESTART")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_member4_vip)
        log("start","/var/log/syslog",config.grid_member4_vip)
        sleep(10)
        check_able_to_login_appliances(config.grid_vip)
        dns_restart_services()
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_member4_vip)
        log("stop","/var/log/syslog",config.grid_member4_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey = mykey)
        data="cat /tmp/"+config.grid_member4_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member4_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*/infoblox/one/bin/anycast_control).*Stopping ospfd process.*",".*/infoblox/one/bin/anycast_control).*Stopping ospf6d process.*",".*/infoblox/one/bin/anycast_control).*Stopping bgpd process.*",".*/infoblox/one/bin/anycast_control).*Stopping zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting bgpd process.*",".*/infoblox/one/bin/anycast_control).*Starting ospfd process.*",".*/infoblox/one/bin/anycast_control).*Starting ospf6d process.*"]


        LookFor_sys=[".*named.*info shutting down.*",".*named.*notice exiting.*",".*named.*notice starting BIND.*",".*named.*notice running on Linux.*",".*named.*info all zones loaded.*",".*named.*notice running.*",".*zebra.*notice Zebra.*starting.*",".*ospfd.*notice OSPFd.*starting.*",".*ospf6d.*notice OSPF6d .*starts.*"]


        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member4_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member4_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1

        print(flag_info,flag_sys)

        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False


    @pytest.mark.run(order=94)
    def test_094_Stop_DNS_with_DCA_and_ADP_enabled_with_anycast_restart_behavior_ON(self):

        print("\n====================================")
        print("\n Stop DNS services")
        print("\n====================================")

        print("---Starting log capture----")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_member4_vip, username='root', pkey = mykey)
        data = 'tail -f /var/log/syslog > '+config.grid_member4_vip+'_var_log_messages.log 2>&1 &'
        print data
        stdin, stdout, stderr = client.exec_command(data)
        stdout1=stdout.readlines()
        #print "---stdout1----"
        #print(stdout1)
        count =0
        try:
            if len(stdout1)==0:
                count += 1
            else:
                raise Exception("Unable to start capture of the syslog")
        except Exception as e:
            print("Capture of syslog failed")
        data = 'tail -f /infoblox/var/infoblox.log > '+config.grid_member4_vip+'_infoblox_log_messages.log 2>&1 &'
        print data
        stdin, stdout, stderr = client.exec_command(data)
        stdout2=stdout.readlines()
        #print "---stdout2----"
        #print(stdout2)
        #print type(stdout2)
        try:
            if len(stdout2)==0:
                count += 1
            else:
                raise Exception("Unable to start capture of the infoblox log")
        except Exception as e:
            print("Capture of syslog failed")
            assert False
        if count != 2:
            assert False

        client.close()

        dns_stop_services(config.grid_member4_fqdn1)
        sleep(300)
        check_able_to_login_appliances(config.grid_member4_vip)

        sleep(60)
        cwd = os.getcwd()
        c = pexpect.spawn('scp -r root@'+config.grid_member4_vip+':/root/'+config.grid_member4_vip+'_infoblox_log_messages.log .')
        c.expect('$')
        output = c.read()
        print(output)
        c.close()
        if '100%' not in output:
            print "SCP failed"
            assert False

        c = pexpect.spawn('scp -r root@'+config.grid_member4_vip+':/root/'+config.grid_member4_vip+'_var_log_messages.log .')
        c.expect('$')
        output = c.read()
        c.close()
        if '100%' not in output:
            print "SCP failed"
            assert False

        print("-------------------------------------------syslog----------------------------------------")
        f = open(config.grid_member4_vip+'_var_log_messages.log','r')
        for line in f:
            print(line)
        f.close()
        print("\n")
        print("-----------------------------------------------infoblox.log------------------------------")
        f = open(config.grid_member4_vip+'_infoblox_log_messages.log','r')
        for line in f:
            print(line)
        f.close()
        print("\n")
        print("-------------------------log captuure ends-----------------------------------------------")



        LookFor_info=[".*/infoblox/dns/bin/stop_dns_service).*stopping named services.*",".*/infoblox/one/bin/anycast_control).*Stopping ospfd process.*",".*/infoblox/one/bin/anycast_control).*Stopping ospf6d process.*",".*/infoblox/one/bin/anycast_control).*Stopping bgpd process.*",".*/infoblox/one/bin/anycast_control).*Stopping zebra process.*"]


        LookFor_sys=[".*named.*notice exiting.*"]

        flag_fastpath_terminate=True



        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            #logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            command = "grep -ai '"+look+"' "+config.grid_member4_vip+"_infoblox_log_messages.log"
            #logs = subprocess.check_output(command,shell=True)
            #print(logs)
            #if logs:
                #flag_info=flag_info+1
            try:
                logs = subprocess.check_output(command,shell=True,stderr=subprocess.STDOUT)
                print(logs)
                if logs:
                    flag_info=flag_info+1
                    flag_fastpath_terminate=False
            except subprocess.CalledProcessError as e:
                logs = None
                print(logs)

        for look in LookFor_sys:
            print(look)
            #logs=logv(look,"/var/log/syslog",config.grid_vip)
            command = "grep -ai '"+look+"' "+config.grid_member4_vip+"_var_log_messages.log"

            try:
                logs = subprocess.check_output(command,shell=True,stderr=subprocess.STDOUT)
                print(logs)
                if logs:
                    flag_sys=flag_sys+1
                    flag_fastpath_terminate=False
            except subprocess.CalledProcessError as e:
                logs = None
                print(logs)

        if flag_fastpath_terminate==True:
            print("DCA terminated before named could terminate, hence no logs for named and anycast will be seen")
        elif (flag_info!=len(LookFor_info) or flag_sys!=len(LookFor_sys)):
            print("DCA terminated before named could terminate, hence no logs for named and anycast will be seen")
        else:
            print(flag_info,flag_sys)
            if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
                assert True
            else:
                assert False


    @pytest.mark.run(order=95)
    def test_095_Start_DNS_with_DCA_and_ADP_enabled_with_anycast_restart_behavior_ON(self):
        print("\n====================================")
        print("\n Start DNS services ")
        print("\n====================================")

        check_able_to_login_appliances(config.grid_member4_vip)

        log("start","/infoblox/var/infoblox.log",config.grid_member4_vip)
        log("start","/var/log/syslog",config.grid_member4_vip)
        sleep(10)
        dns_start_services(config.grid_member4_fqdn1)
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_member4_vip)
        log("stop","/var/log/syslog",config.grid_member4_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey = mykey)
        data="cat /tmp/"+config.grid_member4_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member4_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*/infoblox/one/bin/anycast_control).*Starting zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting bgpd process.*",".*/infoblox/one/bin/anycast_control).*Starting ospfd process.*",".*/infoblox/one/bin/anycast_control).*Starting ospf6d process.*"]


        LookFor_sys=[".*named.*notice starting BIND.*",".*named.*notice running on Linux.*",".*named.*info all zones loaded.*",".*named.*notice running.*",".*zebra.*notice Zebra.*starting.*",".*notice BGPd.*starting.*bgp.*",".*ospfd.*notice OSPFd.*starting.*"]
        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member4_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member4_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False

    @pytest.mark.run(order=96)
    def test_096_Enable_DCA_and_ADP_and_set_anycast_restart_behavior_to_OFF(self):
        enable_dca(config.grid_vip,config.grid_member4_fqdn1)
        check_able_to_login_appliances(config.grid_member4_vip)
        set_cli_anycast_restart_off(config.grid_vip)


    @pytest.mark.run(order=97)
    def test_097_Restart_DNS_normally_with_DCA_and_ADP_enabled_with_anycast_restart_behavior_OFF(self):
        print("\n====================================")
        print("\n Restart DNS services normally")
        print("\n====================================")

        set_recursive_query_false_for_restart_pending_changes(config.grid_member4_fqdn1)

        log("start","/infoblox/var/infoblox.log",config.grid_member4_vip)
        log("start","/var/log/syslog",config.grid_member4_vip)
        sleep(10)
        dns_restart_services_normally()
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_member4_vip)
        log("stop","/var/log/syslog",config.grid_member4_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey = mykey)
        data="cat /tmp/"+config.grid_member4_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member4_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info_not=[".*/infoblox/one/bin/anycast_control).*Stopping ospfd process.*",".*/infoblox/one/bin/anycast_control).*Stopping ospf6d process.*",".*/infoblox/one/bin/anycast_control).*Stopping bgpd process.*",".*/infoblox/one/bin/anycast_control).*Stopping zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting bgpd process.*",".*/infoblox/one/bin/anycast_control).*Starting ospfd process.*",".*/infoblox/one/bin/anycast_control).*Starting ospf6d process.*"]


        LookFor_sys_not=[".*ospfd.*info ospfTrapIfStateChange trap sent: 1.3.3.3 now Down.*",".*ospf6d.*notice OSPF6d .*starts.*"]



        LookFor_info=[]

        LookFor_sys=[".*named.*info shutting down.*",".*named.*notice exiting.*",".*named.*notice starting BIND.*(Supported Preview Version).*",".*named.*notice running on Linux.*",".*named.*info all zones loaded.*",".*named.*notice running.*"]


        flag_info_not=1
        flag_sys_not=1

        for look in LookFor_info_not:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member4_vip)
            print(logs)
            if logs:
                flag_info_not=0

        for look in LookFor_sys_not:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member4_vip)
            print(logs)
            if logs:
                flag_sys_not=0

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member4_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member4_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info_not,flag_sys_not,flag_info,flag_sys)
        if flag_info_not==1 and flag_sys_not==1 and flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False


    @pytest.mark.run(order=98)
    def test_098_Restart_DNS_forcefully_with_DCA_and_ADP_enabled_with_anycast_restart_behavior_OFF(self):
        print("\n====================================")
        print("\n Restart DNS services FORCE_RESTART")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_member4_vip)
        log("start","/var/log/syslog",config.grid_member4_vip)
        sleep(10)
        dns_restart_services()
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_member4_vip)
        log("stop","/var/log/syslog",config.grid_member4_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey = mykey)
        data="cat /tmp/"+config.grid_member4_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member4_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info_not=[".*/infoblox/one/bin/anycast_control).*Stopping ospfd process.*",".*/infoblox/one/bin/anycast_control).*Stopping ospf6d process.*",".*/infoblox/one/bin/anycast_control).*Stopping bgpd process.*",".*/infoblox/one/bin/firewall).*Disabled firewall BGP.*",".*/infoblox/one/bin/anycast_control).*Stopping zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting bgpd process.*",".*/infoblox/one/bin/firewall).*Enabled firewall BGP.*",".*/infoblox/one/bin/anycast_control).*Starting ospfd process.*",".*/infoblox/one/bin/anycast_control).*Starting ospf6d process.*"]


        LookFor_sys_not=[".*zebra.*notice client.*disconnected.*ospf routes removed from the rib.*",".*ospfd.*notice Terminating on signal.*",".*ospfd.*info ospfTrapIfStateChange trap sent.*"+config.grid_vip+".*now Down.*",".*ospfd.*info ospfTrapIfStateChange trap sent: 1.3.3.3 now Down.*",".*ospfd.*info ospfTrapIfStateChange trap sent.*"+config.grid_vip+".*now DROther.*",".*ospf6d.*notice OSPF6d .*starts.*",".*zebra.*notice client.*says hello and bids fair to announce only ospf6 routes.*"]



        LookFor_info=[]

        LookFor_sys=[".*named.*info shutting down.*",".*named.*info no longer listening on.*",".*named.*notice exiting.*",".*named.*notice starting BIND.*(Supported Preview Version).*",".*named.*notice running on Linux.*",".*named.*info all zones loaded.*",".*named.*notice running.*"]


        flag_info_not=1
        flag_sys_not=1

        for look in LookFor_info_not:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member4_vip)
            print(logs)
            if logs:
                flag_info_not=0

        for look in LookFor_sys_not:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member4_vip)
            print(logs)
            if logs:
                flag_sys_not=0

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member4_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member4_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info_not,flag_sys_not,flag_info,flag_sys)
        if flag_info_not==1 and flag_sys_not==1 and flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False




    @pytest.mark.run(order=99)
    def test_099_Stop_DNS_with_DCA_and_ADP_enabled_with_anycast_restart_behavior_OFF(self):
        print("\n====================================")
        print("\n Stop DNS services ")
        print("\n====================================")


        print("---Starting log capture----")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_member4_vip, username='root', pkey = mykey)
        data = 'tail -f /var/log/syslog > '+config.grid_member4_vip+'_var_log_messages.log 2>&1 &'
        print data
        stdin, stdout, stderr = client.exec_command(data)
        stdout1=stdout.readlines()
        #print "---stdout1----"
        #print(stdout1)
        count =0
        try:
            if len(stdout1)==0:
                count += 1
            else:
                raise Exception("Unable to start capture of the syslog")
        except Exception as e:
            print("Capture of syslog failed")
        data = 'tail -f /infoblox/var/infoblox.log > '+config.grid_member4_vip+'_infoblox_log_messages.log 2>&1 &'
        print data
        stdin, stdout, stderr = client.exec_command(data)
        stdout2=stdout.readlines()
        #print "---stdout2----"
        #print(stdout2)
        #print type(stdout2)
        try:
            if len(stdout2)==0:
                count += 1
            else:
                raise Exception("Unable to start capture of the infoblox log")
        except Exception as e:
            print("Capture of syslog failed")
            assert False
        if count != 2:
            assert False

        client.close()

        dns_stop_services(config.grid_member4_fqdn1)
        sleep(300)
        check_able_to_login_appliances(config.grid_member4_vip)
        sleep(60)
        cwd = os.getcwd()
        c = pexpect.spawn('scp -r root@'+config.grid_member4_vip+':/root/'+config.grid_member4_vip+'_infoblox_log_messages.log .')
        c.expect('$')
        output = c.read()
        c.close()
        if '100%' not in output:
            print "SCP failed"
            assert False

        c = pexpect.spawn('scp -r root@'+config.grid_member4_vip+':/root/'+config.grid_member4_vip+'_var_log_messages.log .')
        c.expect('$')
        output = c.read()
        c.close()
        if '100%' not in output:
            print "SCP failed"
            assert False

        print("-------------------------------------------syslog----------------------------------------")
        f = open(config.grid_member4_vip+'_var_log_messages.log','r')
        for line in f:
            print(line)
        f.close()
        print("\n")
        print("-----------------------------------------------infoblox.log------------------------------")
        f = open(config.grid_member4_vip+'_infoblox_log_messages.log','r')
        for line in f:
            print(line)
        f.close()
        print("\n")
        print("-------------------------log captuure ends-----------------------------------------------")

        LookFor_info=[".*/infoblox/dns/bin/stop_dns_service).*stopping named services.*"]

        LookFor_sys=[".*named.*info shutting down.*"]

        flag_info=0
        flag_sys=0

        flag_fastpath_terminate=True

        for look in LookFor_info:
            print(look)
            #logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            command = "grep -ai '"+look+"' "+config.grid_member4_vip+"_infoblox_log_messages.log"
            try:
                logs = subprocess.check_output(command,shell=True,stderr=subprocess.STDOUT)
                print(logs)
                if logs:
                    flag_info=flag_info+1
                    flag_fastpath_terminate=False
            except subprocess.CalledProcessError as e:
                logs = None
                print(logs)

        for look in LookFor_sys:
            print(look)
            #logs=logv(look,"/var/log/syslog",config.grid_vip)
            command = "grep -ai '"+look+"' "+config.grid_member4_vip+"_var_log_messages.log"
            try:
                logs = subprocess.check_output(command,shell=True,stderr=subprocess.STDOUT)
                print(logs)
                if logs:
                    flag_sys=flag_sys+1
                    flag_fastpath_terminate=False
            except subprocess.CalledProcessError as e:
                logs = None
                print(logs)

        print(flag_info,flag_sys)
        if flag_fastpath_terminate==True:
            print("DCA terminated before named could terminate, hence no logs for named and anycast will be seen")
        elif (flag_info!=len(LookFor_info) or flag_sys!=len(LookFor_sys)):
            print("DCA terminated before named could terminate, hence no logs for named and anycast will be seen")
        else:
            if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
                assert True
            else:
                assert False

    @pytest.mark.run(order=100)
    def test_100_Start_DNS_with_DCA_and_ADP_enabled_with_anycast_restart_behavior_OFF(self):
        print("\n====================================")
        print("\n Start DNS services normally")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_member4_vip)
        log("start","/var/log/syslog",config.grid_member4_vip)
        sleep(10)
        dns_start_services(config.grid_member4_fqdn1)
        sleep(30)
        log("stop","/infoblox/var/infoblox.log",config.grid_member4_vip)
        log("stop","/var/log/syslog",config.grid_member4_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey = mykey)
        data="cat /tmp/"+config.grid_member4_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member4_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*/infoblox/one/bin/anycast_control).*Starting zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting bgpd process.*",".*/infoblox/one/bin/anycast_control).*Starting ospfd process.*",".*/infoblox/one/bin/anycast_control).*Starting ospf6d process.*"]


        LookFor_sys=[".*named.*notice starting BIND.*",".*named.*notice running on Linux.*",".*named.*info all zones loaded.*",".*named.*notice running.*",".*zebra.*notice Zebra.*starting.*",".*bgpd.*notice BGPd.*starting.*bgp.*",".*ospfd.*notice OSPFd.*starting.*"]



        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member4_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member4_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False

    @pytest.mark.run(order=101)
    def test_101_Enable_DCA_and_change_DNS_resolver_type_to_unbound_on_IB_FLEX(self):
        print("Unbound case, hence skipping")
        '''enable_dca(config.grid_vip,config.grid_member4_fqdn1)
        check_able_to_login_appliances(config.grid_vip)
        sleep(60)
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=recursive_resolver', grid_vip=config.grid_vip)
        print("\n")
        for ref in json.loads(get_ref):
            if config.grid_member4_fqdn1 in ref['_ref']:
                data={"recursive_resolver":"UNBOUND"}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401 or response[0]==404:
                        print("Failure: set to recursive resolver")
                        assert False
                    else:
                        print("Success: set to recursive resolver")
                        #assert True
        dns_restart_services()'''


    @pytest.mark.run(order=102)
    def test_102_set_anycast_restart_behavior_to_ON(self):
        print("Unbound case, hence skipping")
        '''set_cli_anycast_restart_on(config.grid_vip)
        sleep(30)'''

    @pytest.mark.run(order=103)
    def test_103_Restart_DNS_normally_with_DCA_and_ADP_enabled_with_anycast_restart_behavior_ON_and_DNS_resolver_UNBOUND(self):
        print("Unbound case, hence skipping")
        '''print("\n====================================")
        print("\n Restart DNS services normally")
        print("\n====================================")

        set_recursive_query_true_for_restart_pending_changes(config.grid_member4_fqdn1)

        log("start","/infoblox/var/infoblox.log",config.grid_member4_vip)
        log("start","/var/log/syslog",config.grid_member4_vip)
        sleep(10)
        dns_restart_services_normally()
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_member4_vip)
        log("stop","/var/log/syslog",config.grid_member4_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey = mykey)
        data="cat /tmp/"+config.grid_member4_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member4_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*/infoblox/one/bin/anycast_control).*Stopping ospfd process.*",".*/infoblox/one/bin/anycast_control).*Stopping bgpd process.*",".*/infoblox/one/bin/anycast_control).*Stopping zebra process.*",".*/infoblox/dns/bin/unbound_control).*starting unbound.*",".*/infoblox/one/bin/anycast_control).*Starting zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting bgpd process.*",".*/infoblox/one/bin/anycast_control).*Starting ospfd process.*"]


        LookFor_sys=[".*unbound.*info.*info.*service stopped.*",".*unbound.*notice.*notice.*init module.*validator.*",".*unbound.*notice.*notice.*init module.*iterator.*",".*unbound.*info.*info.*start of service.*",".*zebra.*notice Zebra.*starting.*",".*bgpd.*notice BGPd.*starting.*bgp.*"]



        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member4_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member4_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1

        print(flag_info,flag_sys)

        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False'''


    @pytest.mark.run(order=104)
    def test_104_Restart_DNS_forcefully_with_DCA_and_ADP_enabled_with_anycast_restart_behavior_ON_and_DNS_resolver_UNBOUND(self):
        print("Unbound case, hence skipping")
        '''sleep(20)
        print("\n====================================")
        print("\n Restart DNS services FORCE_RESTART")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_member4_vip)
        log("start","/var/log/syslog",config.grid_member4_vip)
        sleep(10)
        dns_restart_services()
        sleep(30)
        log("stop","/infoblox/var/infoblox.log",config.grid_member4_vip)
        log("stop","/var/log/syslog",config.grid_member4_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey = mykey)
        data="cat /tmp/"+config.grid_member4_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member4_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*/infoblox/one/bin/anycast_control).*Stopping ospfd process.*",".*/infoblox/one/bin/anycast_control).*Stopping bgpd process.*",".*/infoblox/one/bin/anycast_control).*Stopping zebra process.*",".*/infoblox/dns/bin/unbound_control).*starting unbound.*",".*/infoblox/one/bin/anycast_control).*Starting zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting bgpd process.*",".*/infoblox/one/bin/anycast_control).*Starting ospfd process.*"]


        LookFor_sys=[".*unbound.*info.*info.*service stopped.*",".*unbound.*notice.*notice.*init module.*validator.*",".*unbound.*notice.*notice.*init module.*iterator.*",".*unbound.*info.*info.*start of service.*",".*zebra.*notice Zebra.*starting.*",".*bgpd.*notice BGPd.*starting.*bgp.*",".*ospfd.*notice OSPFd.*starting.*"]


        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member4_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member4_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1

        print(flag_info,flag_sys)

        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False'''


    @pytest.mark.run(order=105)
    def test_105_Stop_DNS_with_DCA_and_ADP_enabled_with_anycast_restart_behavior_ON_and_DNS_resolver_UNBOUND(self):
        print("Unbound case, hence skipping")
        '''print("\n====================================")
        print("\n Stop DNS services")
        print("\n====================================")


        print("---Starting log capture----")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_member4_vip, username='root', pkey = mykey)
        data = 'tail -f /var/log/syslog > '+config.grid_member4_vip+'_var_log_messages.log 2>&1 &'
        print data
        stdin, stdout, stderr = client.exec_command(data)
        stdout1=stdout.readlines()
        #print "---stdout1----"
        #print(stdout1)
        count =0
        try:
            if len(stdout1)==0:
                count += 1
            else:
                raise Exception("Unable to start capture of the syslog")
        except Exception as e:
            print("Capture of syslog failed")
        data = 'tail -f /infoblox/var/infoblox.log > '+config.grid_member4_vip+'_infoblox_log_messages.log 2>&1 &'
        print data
        stdin, stdout, stderr = client.exec_command(data)
        stdout2=stdout.readlines()
        #print "---stdout2----"
        #print(stdout2)
        #print type(stdout2)
        try:
            if len(stdout2)==0:
                count += 1
            else:
                raise Exception("Unable to start capture of the infoblox log")
        except Exception as e:
            print("Capture of syslog failed")
            assert False
        if count != 2:
            assert False

        client.close()
        #check_able_to_login_appliances(config.grid_vip)
        dns_stop_services(config.grid_member4_fqdn1)
        sleep(180)
        check_able_to_login_appliances(config.grid_member4_vip)
        sleep(60)
        cwd = os.getcwd()
        c = pexpect.spawn('scp -r root@'+config.grid_member4_vip+':/root/'+config.grid_member4_vip+'_infoblox_log_messages.log .')
        c.expect('$')
        output = c.read()
        c.close()
        if '100%' not in output:
            print "SCP failed"
            assert False

        c = pexpect.spawn('scp -r root@'+config.grid_member4_vip+':/root/'+config.grid_member4_vip+'_var_log_messages.log .')
        c.expect('$')
        output = c.read()
        c.close()
        if '100%' not in output:
            print "SCP failed"
            assert False

        print("-------------------------------------------syslog----------------------------------------")
        f = open(config.grid_member4_vip+'_var_log_messages.log','r')
        for line in f:
            print(line)
        f.close()
        print("\n")
        print("-----------------------------------------------infoblox.log------------------------------")
        f = open(config.grid_member4_vip+'_infoblox_log_messages.log','r')
        for line in f:
            print(line)
        f.close()
        print("\n")
        print("-------------------------log captuure ends-----------------------------------------------")

        LookFor_info=[".*/infoblox/dns/bin/stop_dns_service).*stopping unbound services.*",".*/infoblox/one/bin/anycast_control).*Stopping ospfd process.*",".*/infoblox/one/bin/anycast_control).*Stopping bgpd process.*",".*/infoblox/one/bin/anycast_control).*Stopping zebra process.*",".*/infoblox/dns/bin/unbound_control).*Sending SIGTERM to unbound process.*"]


        LookFor_sys=[".*unbound.*info.*info.*service stopped.*"]

        flag_info=0
        flag_sys=0
        flag_fastpath_terminate=True

        for look in LookFor_info:
            print(look)
            #logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            command = "grep -ai '"+look+"' "+config.grid_member4_vip+"_infoblox_log_messages.log"
            try:
                logs = subprocess.check_output(command,shell=True,stderr=subprocess.STDOUT)
                print(logs)
                if logs:
                    flag_info=flag_info+1
                    flag_fastpath_terminate=False
            except subprocess.CalledProcessError as e:
                logs = None
                print(logs)

        for look in LookFor_sys:
            print(look)
            #logs=logv(look,"/var/log/syslog",config.grid_vip)
            command = "grep -ai '"+look+"' "+config.grid_member4_vip+"_var_log_messages.log"
            try:
                logs = subprocess.check_output(command,shell=True,stderr=subprocess.STDOUT)
                print(logs)
                if logs:
                    flag_sys=flag_sys+1
                    flag_fastpath_terminate=False
            except subprocess.CalledProcessError as e:
                logs = None
                print(logs)
        if flag_fastpath_terminate==True:
            print("DCA terminated before named could terminate, hence no logs for named and anycast will be seen")
        elif (flag_info!=len(LookFor_info) or flag_sys!=len(LookFor_sys)):
            print("DCA terminated before named could terminate, hence no logs for named and anycast will be seen")
        else:
            print(flag_info,flag_sys)
            if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
                assert True
            else:
                assert False'''


    @pytest.mark.run(order=106)
    def test_106_Start_DNS_with_DCA_and_ADP_enabled_with_anycast_restart_behavior_ON_and_DNS_resolver_UNBOUND(self):
        print("Unbound case, hence skipping")
        '''print("\n====================================")
        print("\n Start DNS services ")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_member4_vip)
        log("start","/var/log/syslog",config.grid_member4_vip)
        sleep(10)
        dns_start_services(config.grid_member4_fqdn1)
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_member4_vip)
        log("stop","/var/log/syslog",config.grid_member4_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey = mykey)
        data="cat /tmp/"+config.grid_member4_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member4_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info=[".*/infoblox/dns/bin/unbound_control).*starting unbound.*",".*/infoblox/one/bin/anycast_control).*Starting zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting bgpd process.*",".*/infoblox/one/bin/anycast_control).*Starting ospfd process.*"]


        LookFor_sys=[".*unbound.*notice.*notice.*init module.*validator.*",".*unbound.*notice.*notice.*init module.*iterator.*",".*unbound.*info.*info.*start of service.*",".*zebra.*notice Zebra.*starting.*",".*bgpd.*notice BGPd.*starting.*",".*ospfd.*notice OSPFd.*starting.*"]

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member4_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member4_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False'''

    @pytest.mark.run(order=107)
    def test_107_Enable_DCA_and_set_anycast_restart_behavior_to_OFF(self):
        print("Unbound case, hence skipping")
        '''check_able_to_login_appliances(config.grid_vip)
        enable_dca(config.grid_vip,config.grid_member4_fqdn1)
        check_able_to_login_appliances(config.grid_vip)
        sleep(30)
        set_cli_anycast_restart_off(config.grid_vip)'''


    @pytest.mark.run(order=108)
    def test_108_Restart_DNS_normally_with_DCA_and_ADP_enabled_with_anycast_restart_behavior_OFF_and_DNS_resolver_UNBOUND(self):
        print("Unbound case, hence skipping")
        '''print("\n====================================")
        print("\n Restart DNS services normally")
        print("\n====================================")

        set_recursive_query_false_for_restart_pending_changes(config.grid_member4_fqdn1)

        log("start","/infoblox/var/infoblox.log",config.grid_member4_vip)
        log("start","/var/log/syslog",config.grid_member4_vip)
        sleep(10)
        dns_restart_services_normally()
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_member4_vip)
        log("stop","/var/log/syslog",config.grid_member4_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey = mykey)
        data="cat /tmp/"+config.grid_member4_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member4_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info_not=[".*/infoblox/one/bin/anycast_control).*Stopping ospfd process.*",".*/infoblox/one/bin/anycast_control).*Stopping bgpd process.*",".*/infoblox/one/bin/anycast_control).*Stopping zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting bgpd process.*",".*/infoblox/one/bin/anycast_control).*Starting ospfd process.*"]


        LookFor_sys_not=[".*unbound.*info.*info.*service stopped.*",".*unbound.*notice.*notice.*init module.*validator.*",".*unbound.*notice.*notice.*init module.*iterator.*",".*unbound.*info.*info.*start of service.*",".*zebra.*notice Zebra.*starting.*",".*bgpd.*notice BGPd.*starting.*bgp.*",".*ospfd.*notice OSPFd.*starting.*"]



        LookFor_info=[".*/infoblox/dns/bin/unbound_control).*starting unbound.*"]


        LookFor_sys=[".*unbound.*info.*info.*service stopped.*",".*unbound.*notice.*notice.*init module.*validator.*",".*unbound.*notice.*notice.*init module.*iterator.*",".*unbound.*info.*info.*start of service.*"]


        flag_info_not=1
        flag_sys_not=1

        for look in LookFor_info_not:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member4_vip)
            print(logs)
            if logs:
                flag_info_not=0

        for look in LookFor_sys_not:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member4_vip)
            print(logs)
            if logs:
                flag_sys_not=0

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member4_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member4_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False'''


    @pytest.mark.run(order=109)
    def test_109_Restart_DNS_forcefully_with_DCA_and_ADP_enabled_with_anycast_restart_behavior_OFF_and_DNS_resolver_UNBOUND(self):
        print("Unbound case, hence skipping")
        '''print("\n====================================")
        print("\n Restart DNS services FORCE_RESTART")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_member4_vip)
        log("start","/var/log/syslog",config.grid_member4_vip)
        sleep(10)
        dns_restart_services()
        sleep(20)
        log("stop","/infoblox/var/infoblox.log",config.grid_member4_vip)
        log("stop","/var/log/syslog",config.grid_member4_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey = mykey)
        data="cat /tmp/"+config.grid_member4_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member4_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
        LookFor_info_not=[".*/infoblox/one/bin/anycast_control).*Stopping ospfd process.*",".*/infoblox/one/bin/anycast_control).*Stopping bgpd process.*",".*/infoblox/one/bin/anycast_control).*Stopping zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting bgpd process.*",".*/infoblox/one/bin/anycast_control).*Starting ospfd process.*"]


        LookFor_sys_not=[".*ospfd.*info ospfTrapIfStateChange trap sent: 1.3.3.3 now Down.*",".*unbound.*info.*info.*service stopped.*",".*unbound.*notice.*notice.*init module.*validator.*",".*unbound.*notice.*notice.*init module.*iterator.*",".*unbound.*info.*info.*start of service.*",".*zebra.*notice Zebra.*starting.*",".*bgpd.*notice BGPd.*starting.*bgp.*",".*ospfd.*notice OSPFd.*starting.*"]



        LookFor_info=[".*/infoblox/dns/bin/unbound_control).*starting unbound.*"]


        LookFor_sys=[".*unbound.*info.*info.*service stopped.*",".*unbound.*notice.*notice.*init module.*validator.*",".*unbound.*notice.*notice.*init module.*iterator.*",".*unbound.*info.*info.*start of service.*"]


        flag_info_not=1
        flag_sys_not=1

        for look in LookFor_info_not:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member4_vip)
            print(logs)
            if logs:
                flag_info_not=0

        for look in LookFor_sys_not:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member4_vip)
            print(logs)
            if logs:
                flag_sys_not=0

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member4_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member4_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False'''

    @pytest.mark.run(order=110)
    def test_110_Stop_DNS_with_DCA_and_ADP_enabled_with_anycast_restart_behavior_OFF_and_DNS_resolver_UNBOUND(self):
        print("Unbound case, hence skipping")
        '''print("\n====================================")
        print("\n Stop DNS services ")
        print("\n====================================")


        print("---Starting log capture----")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_member4_vip, username='root', pkey = mykey)
        data = 'tail -f /var/log/syslog > '+config.grid_member4_vip+'_var_log_messages.log 2>&1 &'
        print data
        stdin, stdout, stderr = client.exec_command(data)
        stdout1=stdout.readlines()
        #print "---stdout1----"
        #print(stdout1)
        count =0
        try:
            if len(stdout1)==0:
                count += 1
            else:
                raise Exception("Unable to start capture of the syslog")
        except Exception as e:
            print("Capture of syslog failed")
        data = 'tail -f /infoblox/var/infoblox.log > '+config.grid_member4_vip+'_infoblox_log_messages.log 2>&1 &'
        print data
        stdin, stdout, stderr = client.exec_command(data)
        stdout2=stdout.readlines()
        #print "---stdout2----"
        #print(stdout2)
        #print type(stdout2)
        try:
            if len(stdout2)==0:
                count += 1
            else:
                raise Exception("Unable to start capture of the infoblox log")
        except Exception as e:
            print("Capture of syslog failed")
            assert False
        if count != 2:
            assert False

        client.close()

        dns_stop_services(config.grid_member4_fqdn1)
        sleep(180)
        check_able_to_login_appliances(config.grid_member4_vip)
        sleep(60)
        cwd = os.getcwd()
        c = pexpect.spawn('scp -r root@'+config.grid_member4_vip+':/root/'+config.grid_member4_vip+'_infoblox_log_messages.log .')
        c.expect('$')
        output = c.read()
        c.close()
        if '100%' not in output:
            print "SCP failed"
            assert False

        c = pexpect.spawn('scp -r root@'+config.grid_member4_vip+':/root/'+config.grid_member4_vip+'_var_log_messages.log .')
        c.expect('$')
        output = c.read()
        c.close()
        if '100%' not in output:
            print "SCP failed"
            assert False

        print("-------------------------------------------syslog----------------------------------------")
        f = open(config.grid_member4_vip+'_var_log_messages.log','r')
        for line in f:
            print(line)
        f.close()
        print("\n")
        print("-----------------------------------------------infoblox.log------------------------------")
        f = open(config.grid_member4_vip+'_infoblox_log_messages.log','r')
        for line in f:
            print(line)
        f.close()
        print("\n")
        print("-------------------------log captuure ends-----------------------------------------------")

        LookFor_info=[".*/infoblox/dns/bin/stop_dns_service).*stopping unbound services.*"]

        LookFor_sys=[".*unbound.*info.*info.*service stopped.*"]

        flag_info=0
        flag_sys=0
        flag_fastpath_terminate=True

        for look in LookFor_info:
            print(look)
            #logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            command = "grep -ai '"+look+"' "+config.grid_member4_vip+"_infoblox_log_messages.log"
            try:
                logs = subprocess.check_output(command,shell=True,stderr=subprocess.STDOUT)
                print(logs)
                if logs:
                    flag_info=flag_info+1
                    flag_fastpath_terminate=False
            except subprocess.CalledProcessError as e:
                logs = None
                print(logs)

        for look in LookFor_sys:
            print(look)
            #logs=logv(look,"/var/log/syslog",config.grid_vip)
            command = "grep -ai '"+look+"' "+config.grid_member4_vip+"_var_log_messages.log"
            try:
                logs = subprocess.check_output(command,shell=True,stderr=subprocess.STDOUT)
                print(logs)
                if logs:
                    flag_sys=flag_sys+1
                    flag_fastpath_terminate=False
            except subprocess.CalledProcessError as e:
                logs = None
                print(logs)

        print(flag_info,flag_sys)
        if flag_fastpath_terminate==True:
            print("DCA terminated before named could terminate, hence no logs for named and anycast will be seen")
        elif (flag_info!=len(LookFor_info) or flag_sys!=len(LookFor_sys)):
            print("DCA terminated before named could terminate, hence no logs for named and anycast will be seen")
        else:
            if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
                assert True
            else:
                assert False'''


    @pytest.mark.run(order=111)
    def test_111_Start_DNS_with_DCA_and_ADP_enabled_with_anycast_restart_behavior_OFF_and_DNS_resolver_UNBOUND(self):
        print("Unbound case, hence skipping")
        '''print("\n====================================")
        print("\n Start DNS services normally")
        print("\n====================================")

        log("start","/infoblox/var/infoblox.log",config.grid_member4_vip)
        log("start","/var/log/syslog",config.grid_member4_vip)
        sleep(10)
        dns_start_services(config.grid_member4_fqdn1)
        sleep(30)
        log("stop","/infoblox/var/infoblox.log",config.grid_member4_vip)
        log("stop","/var/log/syslog",config.grid_member4_vip)
        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey = mykey)
        data="cat /tmp/"+config.grid_member4_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member4_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")

        LookFor_info=[".*/infoblox/dns/bin/unbound_control).*starting unbound.*",".*/infoblox/one/bin/anycast_control).*Starting zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting bgpd process.*",".*/infoblox/one/bin/anycast_control).*Starting ospfd process.*"]

        LookFor_sys=[".*unbound.*notice.*notice.*init module.*validator.*",".*unbound.*notice.*notice.*init module.*iterator.*",".*unbound.*info.*info.*start of service.*",".*zebra.*notice Zebra.*starting.*",".*bgpd.*notice BGPd.*starting.*",".*ospfd.*notice OSPFd.*starting.*"]

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member4_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member4_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False'''

    @pytest.mark.run(order=112)
    def test_112_change_DNS_resolver_to_BIND_and_disable_DCA(self):
        '''get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=recursive_resolver')
        print("\n")
        for ref in json.loads(get_ref):
            if config.grid_member4_fqdn1 in ref['_ref']:
                data={"recursive_resolver":"BIND"}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401 or response[0]==404:
                        print("Failure: set to recursive resolver")
                        assert False
                else:
                    print("Success: set to recursive resolver")'''

        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns',grid_vip=config.grid_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            if ref["host_name"]== config.grid_member4_fqdn1:
                data = {"enable_dns_cache_acceleration": False}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401 or response[0]==401 or response[0]==404:
                        print("Failure: Enable_dns_cache_acceleration")
                        assert False
                else:
                    print("Success: Disable_dns_cache_acceleration")
                    assert True
                    sleep(240)

    @pytest.mark.run(order=113)
    def test_113_create_Auth_Zone(self):
        print("\n============================================\n")
        print("Create a new Auth Zone")
        print("\n============================================\n")

        dns_start_services(config.grid_fqdn)

        data = {"fqdn": "ref_10176.com","grid_primary": [{"name": config.grid_member_fqdn,"stealth":False}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)

        if type(response) == tuple:
            if response[0]==400 or response[0]==401 or response[0]==401 or response[0]==404:
                print("Failure: Create a new Auth Zone")
                assert False
            else:
                print("Success: Create a new Auth Zone")
                assert True

        print("\n============================================\n")
        print("Creating A records for ref_10176.com zone")
        print("\n============================================\n")

        for i in range(10):
            data = {"ipv4addr": "13.0.0."+str(i+1),
                    "view":"default",
                    "name": "A_rec"+str(i)+".ref_10176.com"}
            response = ib_NIOS.wapi_request('POST',object_type="record:a",fields=json.dumps(data),grid_vip=config.grid_vip)
            print(response)
            if type(response) == tuple:
                print("Failure: Create A record in ref_10176.com zone")
                assert False
            else:
                print("Success: Create A record in ref_10176.com zone")
                assert True

        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(60)

    @pytest.mark.run(order=114)
    def test_114_modify_bird_conf_file_and_start_bird_process_for_both_ospf_and_bgp(self):
        cwd = os.getcwd()
        '''a = os.system('cp -rf /import/qaddi/adityag/bird.conf '+cwd)
        if a != 0:
            raise Exception("Couldnt copy the bird conf file")
        print("File copied")'''
        #print config.grid_vip
        fin = open("bird.conf","rt")
        data = fin.read()
        #data = data.replace('neighbor .* as 12','neighbour '+grid_vip+' as 12')
        data = re.sub('neighbor .* as 12','neighbor '+config.grid_vip+' as 12',data)
        fin.close()
        fin = open("bird.conf", "wt")
        fin.write(data)
        fin.close()
        print("ip replaced")
        child = pexpect.spawn("scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bird.conf root@"+config.anycast_client+":/usr/local/etc/",timeout=300)
        child.expect("password:",timeout=300)
        child.sendline("infoblox")
        child.expect("$",timeout=300)
        output = child.read()
        if '100%' in output:
            child.close()
        else:
            child.close()
            raise Exception("Couldnt copy modfified bird conf file to client")
        print("scp successfull")
        child =  pexpect.spawn("ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@"+config.anycast_client,timeout=300)
        child.expect("password:",timeout=300)
        child.sendline("infoblox")
        child.expect("#",timeout=300)
        child.sendline("bird -c /usr/local/etc/bird.conf")
        child.expect("#",timeout=300)
        if "bird: I found another BIRD running" in child.before:
            child.sendline("bird_pid=$(pidof bird)")
            child.expect("#",timeout=300)
            child.sendline("kill -9 $bird_pid")
            child.expect("#",timeout=300)
            child.sendline("bird -c /usr/local/etc/bird.conf")
            child.expect("#",timeout=300)
            child.close()
        else:
            child.close()


    @pytest.mark.run(order=115)
    def test_115_validate_the_anycast_client_details_in_the_grid(self):
        sleep(60)
        child =  pexpect.spawn("ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null admin@"+config.grid_vip)
        child.expect("password: ")
        child.sendline("infoblox")
        child.expect("Infoblox > ")
        sleep(10)
        child.sendline("show bgp summary")
        sleep(5)
        child.expect("Infoblox > ")
        output = child.before
        print(output)
        if config.anycast_client in output:
            print("BGP verified")
            child.close()
        else:
            print("Couldnt find any bgp route for anycast")
            child.close()
            assert False

        child =  pexpect.spawn("ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null admin@"+config.grid_vip)
        child.expect("password: ")
        child.sendline("infoblox")
        child.expect("Infoblox > ")
        sleep(10)
        child.sendline("show ospf database")
        sleep(5)
        #print(child.before)
        #child.read()
        child.expect("Infoblox > ")
        output = child.before
        #child.close()
        print(output)
        if config.anycast_client in output:
            print("OSPF verified")
            child.close()
        else:
            print("Couldnt find any ospf route for anycast")
            child.close()
            assert False


    @pytest.mark.run(order=116)
    def test_116_perform_dig_cmd_for_anycast_member(self):
        print("Turn off DNS service on other members, so that adjacency is created only with the master grid")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        print(get_ref)
        res = json.loads(get_ref)
        for i in res:
            if i["host_name"] != config.grid_fqdn:
                data = {"enable_dns": False}
                response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)
                print(type(response),response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: DNS stop Services")
                        assert False
                else:
                    print("Success: DNS stop Services for "+i["host_name"])
                    assert True
        sleep(300)
        print("Query though anycast member")
        sleep(30)
        child =  pexpect.spawn("ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@"+config.anycast_client,timeout=300)
        child.expect("password:",timeout=300)
        child.sendline("infoblox")
        child.expect("#",timeout=300)
        child.sendline("dig @"+config.anycast_ip+" A_rec1.ref_10176.com in a")
        child.expect("#",timeout=300)
        output = child.before
        print(output)
        if  '13.0.0.2' in output:
            print("Dig query successfull")
            print("Turn on DNS service on other members")
            get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
            res = json.loads(get_ref)
            for i in res:
                if i["host_name"] != config.grid_vip:
                    data = {"enable_dns": True}
                    response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)
                    print(type(response),response)
                    if type(response) == tuple:
                        if response[0]==400 or response[0]==401:
                            print("Failure: DNS start Services")
                            assert False
                    else:
                        print("Success: DNS start Services for "+i["host_name"])
                        assert True
            sleep(240)
            assert True
        else:
            print("Dig query unsuccessfull")
            print("Turn on DNS service on other members")
            get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
            res = json.loads(get_ref)
            for i in res:
                if i["host_name"] != config.grid_vip:
                    data = {"enable_dns": True}
                    response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)
                    print(type(response),response)
                    if type(response) == tuple:
                        if response[0]==400 or response[0]==401:
                            print("Failure: DNS stop Services")
                            assert False
                    else:
                        print("Success: DNS stop Services for "+i["host_name"])
                        assert True
            sleep(240)
            assert False

    @pytest.mark.run(order=117)
    def test_117_Set_anycast_restart_behavior_to_ON_and_Perform_HA_pair_failover(self):
        active,passive = get_ha_active_passive()
        print(active,passive)
        check_able_to_login_appliances(config.grid_vip)
        set_cli_anycast_restart_on(config.grid_vip)


        flag_bgp=True
        flag_ospf=True
        flag_zebra=True
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(active, username='root', pkey = mykey)
        # data="yes\n"
        #stdin, stdout, stderr = client.exec_command(data)
        data="pgrep bgp\n"
        stdin, stdout, stderr = client.exec_command(data)
        a=stdout.readlines()
        #stdout=stdout.read()
        #print("----read--")
        #print(stdout)
        #print(type(stdout))
        #print("---readlines---")
        #print(a)
        #print(type(a))
        #print(len(stdout))

        if len(a)==0:
            flag_bgp=False
            client.close()
        else:
            client.close()

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(active, username='root', pkey = mykey)
        data="pgrep ospf\n"
        stdin, stdout, stderr = client.exec_command(data)
        a=stdout.readlines()
        #stdout=stdout.read()
        #print("----read--")
        #print(stdout)
        #print("---readlines---")
        #print(a)
        #print(len(stdout))

        if len(a)==0:
            flag_ospf=False
            client.close()
        else:
            client.close()



        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(active, username='root', pkey = mykey)
        data="pgrep zebra\n"
        stdin, stdout, stderr = client.exec_command(data)
        a=stdout.readlines()
        #stdout=stdout.read()
        #print(len(stdout))
        #print("----read--")
        #print(stdout)
        #print("---readlines---")
        #print(a)

        if len(a)==0:
            flag_zebra=False
            client.close()
        else:
            client.close()


        print(flag_bgp,flag_ospf,flag_zebra)
        if flag_bgp==True and flag_ospf==True and flag_zebra==True:
            assert True
        else:
            assert False

        #check_able_to_login_appliances(config.grid_vip)
        reboot(config.grid_member1_vip)
        sleep(700)


        check_able_to_login_appliances_ha(passive)
        check_able_to_login_appliances_ha(active)

        flag_bgp=False
        flag_ospf=False
        flag_zebra=False

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(active, username='root', pkey = mykey)
        data="pgrep bgp\n"
        stdin, stdout, stderr = client.exec_command(data)
        a=stdout.readlines()


        if len(a)==0:
            flag_bgp=True
            client.close()

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(active, username='root', pkey = mykey)
        data="pgrep ospf\n"
        stdin, stdout, stderr = client.exec_command(data)
        a=stdout.readlines()


        if len(a)==0:
            flag_ospf=True
            client.close()

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(active, username='root', pkey = mykey)
        data="pgrep zebra\n"
        stdin, stdout, stderr = client.exec_command(data)
        a=stdout.readlines()


        if len(a)==0:
            flag_zebra=True
            client.close()

        print(flag_bgp,flag_ospf,flag_zebra)
        if flag_bgp==True and flag_ospf==True and flag_zebra==True:
            assert True
        else:
            assert False


        flag_bgp=True
        flag_ospf=True
        flag_zebra=True
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(passive, username='root', pkey = mykey)
        # data="yes\n"
        #stdin, stdout, stderr = client.exec_command(data)
        data="pgrep bgp\n"
        stdin, stdout, stderr = client.exec_command(data)
        a=stdout.readlines()


        if len(a)==0:
            flag_bgp=False
            client.close()

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(passive, username='root', pkey = mykey)
        data="pgrep ospf\n"
        stdin, stdout, stderr = client.exec_command(data)
        a=stdout.readlines()


        if len(a)==0:
            flag_ospf=False
            client.close()


        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(passive, username='root', pkey = mykey)
        data="pgrep zebra\n"
        stdin, stdout, stderr = client.exec_command(data)
        a=stdout.readlines()

        if len(a)==0:
            flag_zebra=False
            client.close()

        print(flag_bgp,flag_ospf,flag_zebra)
        if flag_bgp==True and flag_ospf==True and flag_zebra==True:
            sleep(60)
            assert True
        else:
            sleep(60)
            assert False




    @pytest.mark.run(order=118)
    def test_118_Restart_DNS_normally_on_new_active_node_with_anycast_restart_behavior_ON(self):

        set_recursive_query_true_for_restart_pending_changes(config.grid_member1_fqdn)

        log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
        log("start","/var/log/syslog",config.grid_member1_vip)

        dns_restart_services_normally()
        log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
        log("stop","/var/log/syslog",config.grid_member1_vip)

        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        #print(mykey)
        client.connect(config.client_ip, username=config.client_username, pkey = mykey)
        data="cat /tmp/"+config.grid_member1_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member1_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")


        LookFor_info=[".*infoblox/one/bin/anycast_control).*Stopping ospfd process.*",".*infoblox/one/bin/anycast_control).*Stopping zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting ospfd process.*"]


        LookFor_sys=[".*named.*info shutting down.*",".*named.*notice exiting.*",".*named.*notice starting BIND.*(Supported Preview Version).*",".*named.*notice running on.*",".*named.*info all zones loaded.*",".*named.*notice running.*",".*zebra.*notice Zebra.*starting.*vty@2601.*",".*ospfd.*notice OSPFd.*starting.*vty@2604.*"]

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member1_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1


        for look in LookFor_sys:
            print(look)
            logs=logv(look,"/var/log/syslog",config.grid_member1_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1

        print(flag_info,flag_sys)

        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            sleep(60)
            assert True
        else:
            sleep(60)
            assert False


    @pytest.mark.run(order=119)
    def test_119_Restart_DNS_forcefully_on_new_active_node_with_anycast_restart_behavior_ON(self):

        log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
        log("start","/var/log/syslog",config.grid_member1_vip)

        dns_restart_services()
        log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
        log("stop","/var/log/syslog",config.grid_member1_vip)

        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey = mykey)
        data="cat /tmp/"+config.grid_member1_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member1_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")


        LookFor_info=[".*infoblox/one/bin/anycast_control).*Stopping ospfd process.*",".*infoblox/one/bin/anycast_control).*Stopping zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting ospfd process.*"]


        LookFor_sys=[".*named.*info shutting down.*",".*named.*notice exiting.*",".*named.*notice starting BIND.*(Supported Preview Version).*",".*named.*notice running on.*",".*named.*info all zones loaded.*",".*named.*notice running.*",".*zebra.*notice Zebra.*starting.*vty@2601.*",".*ospfd.*notice OSPFd.*starting.*vty@2604.*"]

        flag_info=0
        flag_sys=0

        #LookFor_sys=".*ospfd[.*].*notice Termi.*"

        for look in LookFor_info:
            print(look)
            #logs=logv(look,"/infoblox/var/infoblox.log",config.grid_vip)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member1_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1


        for look in LookFor_sys:
            print(look)
            logs=logv(look,"/var/log/syslog",config.grid_member1_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1

        print(flag_info,flag_sys)

        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False



    @pytest.mark.run(order=120)
    def test_120_Stop_DNS_on_new_active_node_with_anycast_restart_behavior_ON(self):
        log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
        log("start","/var/log/syslog",config.grid_member1_vip)

        dns_stop_services(config.grid_member1_fqdn)
        log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
        log("stop","/var/log/syslog",config.grid_member1_vip)

        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey = mykey)
        data="cat /tmp/"+config.grid_member1_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member1_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")


        LookFor_info=[".*/infoblox/dns/bin/stop_dns_service).*stopping named services.*",".*/infoblox/one/bin/anycast_control).*Stopping ospfd process.*",".*/infoblox/one/bin/anycast_control.*Stopping zebra process.*"]


        LookFor_sys=[".*named.*info shutting down.*",".*named.*notice exiting.*"]
        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member1_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member1_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False


    @pytest.mark.run(order=121)
    def test_121_Start_DNS_on_new_active_node_with_anycast_restart_behavior_ON(self):

        log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
        log("start","/var/log/syslog",config.grid_member1_vip)

        dns_start_services(config.grid_member1_fqdn)
        log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
        log("stop","/var/log/syslog",config.grid_member1_vip)

        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey = mykey)
        data="cat /tmp/"+config.grid_member1_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member1_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")


        LookFor_info=[".*/infoblox/one/bin/anycast_control).*Starting zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting ospfd process.*"]


        LookFor_sys=[".*named.*notice starting BIND.*(Supported Preview Version).*",".*named.*notice running on.*",".*named.*info all zones loaded.*",".*named.*notice running.*",".*zebra.*notice Zebra.*starting.*vty@2601.*",".*ospfd.*notice OSPFd.*starting: vty@2604.*"]
        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member1_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member1_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False


    @pytest.mark.run(order=122)
    def test_122_set_anycast_restart_behavior_to_OFF(self):
        check_able_to_login_appliances(config.grid_vip)
        print("setting restart_anycast_with_dns_restart off")
        set_cli_anycast_restart_off(config.grid_vip)


    @pytest.mark.run(order=123)
    def test_123_Perform_HA_pair_failover(self):

        active,passive = get_ha_active_passive()
        check_able_to_login_appliances(config.grid_vip)
        set_cli_anycast_restart_off(config.grid_vip)


        flag_bgp=True
        flag_ospf=True
        flag_zebra=True
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(active, username='root', pkey = mykey)
        # data="yes\n"
        #stdin, stdout, stderr = client.exec_command(data)
        data="pgrep bgp\n"
        stdin, stdout, stderr = client.exec_command(data)
        a=stdout.readlines()
        #stdout=stdout.read()
        #print("----read--")
        #print(stdout)
        #print(type(stdout))
        #print("---readlines---")
        #print(a)
        #print(type(a))
        #print(len(stdout))

        if len(a)==0:
            flag_bgp=False
            client.close()
        else:
            client.close()

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(active, username='root', pkey = mykey)
        data="pgrep ospf\n"
        stdin, stdout, stderr = client.exec_command(data)
        a=stdout.readlines()

        if len(a)==0:
            flag_ospf=False
            client.close()
        else:
            client.close()



        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(active, username='root', pkey = mykey)
        data="pgrep zebra\n"
        stdin, stdout, stderr = client.exec_command(data)
        a=stdout.readlines()

        if len(a)==0:
            flag_zebra=False
            client.close()
        else:
            client.close()


        print(flag_bgp,flag_ospf,flag_zebra)
        if flag_bgp==True and flag_ospf==True and flag_zebra==True:
            assert True
        else:
            assert False

        #check_able_to_login_appliances(config.grid_vip)
        reboot(config.grid_member1_vip)
        sleep(700)
        check_able_to_login_appliances_ha(passive)
        check_able_to_login_appliances_ha(active)

        flag_bgp=False
        flag_ospf=False
        flag_zebra=False

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(active, username='root', pkey = mykey)
        data="pgrep bgp\n"
        stdin, stdout, stderr = client.exec_command(data)
        a=stdout.readlines()


        if len(a)==0:
            flag_bgp=True
            client.close()

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(active, username='root', pkey = mykey)
        data="pgrep ospf\n"
        stdin, stdout, stderr = client.exec_command(data)
        a=stdout.readlines()


        if len(a)==0:
            flag_ospf=True
            client.close()

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(active, username='root', pkey = mykey)
        data="pgrep zebra\n"
        stdin, stdout, stderr = client.exec_command(data)
        a=stdout.readlines()


        if len(a)==0:
            flag_zebra=True
            client.close()

        print(flag_bgp,flag_ospf,flag_zebra)
        if flag_bgp==True and flag_ospf==True and flag_zebra==True:
            assert True
        else:
            assert False


        flag_bgp=True
        flag_ospf=True
        flag_zebra=True
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(passive, username='root', pkey = mykey)
        # data="yes\n"
        #stdin, stdout, stderr = client.exec_command(data)
        data="pgrep bgp\n"
        stdin, stdout, stderr = client.exec_command(data)
        a=stdout.readlines()


        if len(a)==0:
            flag_bgp=False
            client.close()

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(passive, username='root', pkey = mykey)
        data="pgrep ospf\n"
        stdin, stdout, stderr = client.exec_command(data)
        a=stdout.readlines()


        if len(a)==0:
            flag_ospf=False
            client.close()


        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(passive, username='root', pkey = mykey)
        data="pgrep zebra\n"
        stdin, stdout, stderr = client.exec_command(data)
        a=stdout.readlines()

        if len(a)==0:
            flag_zebra=False
            client.close()

        print(flag_bgp,flag_ospf,flag_zebra)
        if flag_bgp==True and flag_ospf==True and flag_zebra==True:
            assert True
        else:
            assert False




    @pytest.mark.run(order=124)
    def test_124_Restart_DNS_normally_on_new_active_node_with_anycast_restart_behavior_OFF(self):

        set_recursive_query_false_for_restart_pending_changes(config.grid_member1_fqdn)

        log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
        log("start","/var/log/syslog",config.grid_member1_vip)

        dns_restart_services_normally()
        log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
        log("stop","/var/log/syslog",config.grid_member1_vip)


        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey = mykey)
        data="cat /tmp/"+config.grid_member1_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member1_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")


        LookFor_info_not=[".*infoblox/one/bin/anycast_control).*Stopping ospfd process.*",".*infoblox/one/bin/anycast_control).*Stopping zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting ospfd process.*"]


        LookFor_sys_not=[".*ospfd.*notice Terminating on signal.*",".*ospfd.*info ospfTrapIfStateChange trap sent.*"+config.grid_member1_vip+" now Down.*",".*ospfd.*info ospfTrapIfStateChange trap sent: 1.3.3.3 now Down.*",".*zebra.*notice client.*disconnected.*ospf routes removed from the rib.*",".*zebra.*notice Terminating on signal.*",".*zebra.*info IRDP.*Received shutdown notification.*",".*zebra.*notice Zebra.*starting.*vty@2601.*",".*ospfd.*notice OSPFd.*starting.*vty@2604.*",".*zebra.*notice client.*says hello and bids fair to announce only ospf routes.*","ospfd.*info ospfTrapIfStateChange trap sent.*"+config.grid_member1_vip+" now DROther"]

        LookFor_info=[]

        LookFor_sys=[".*named.*info shutting down.*",".* named.*notice exiting.*",".*named.*notice starting BIND.*(Supported Preview Version).*",".*named.*notice running on.*",".*named.*info all zones loaded.*",".*named.*notice running.*"]
        flag_info_not=1
        flag_sys_not=1

        for look in LookFor_info_not:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member1_vip)
            print(logs)
            if logs:
                flag_info_not=0

        for look in LookFor_sys_not:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member1_vip)
            print(logs)
            if logs:
                flag_sys_not=0

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member1_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member1_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1

        print(flag_info_not,flag_sys_not,flag_info,flag_sys)
        if flag_info_not==1 and flag_sys_not==1 and flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False




    @pytest.mark.run(order=125)
    def test_125_Restart_DNS_forcefully_on_new_active_node_with_anycast_restart_behavior_OFF(self):
        log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
        log("start","/var/log/syslog",config.grid_member1_vip)

        dns_restart_services()
        log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
        log("stop","/var/log/syslog",config.grid_member1_vip)

        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey = mykey)
        data="cat /tmp/"+config.grid_member1_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member1_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")


        LookFor_info_not=[".*infoblox/one/bin/anycast_control).*Stopping ospfd process.*",".*infoblox/one/bin/anycast_control).*Stopping zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting ospfd process.*"]


        LookFor_sys_not=[".*ospfd.*notice Terminating on signal.*",".*ospfd.*info ospfTrapIfStateChange trap sent.*"+config.grid_member1_vip+" now Down.*",".*ospfd.*info ospfTrapIfStateChange trap sent: 1.3.3.3 now Down.*",".*zebra.*notice client.*disconnected.*ospf routes removed from the rib.*",".*zebra.*notice Terminating on signal.*",".*zebra.*info IRDP.*Received shutdown notification.*",".*zebra.*notice Zebra.*starting.*vty@2601.*",".*ospfd.*notice OSPFd.*starting.*vty@2604.*",".*zebra.*notice client.*says hello and bids fair to announce only ospf routes.*","ospfd.*info ospfTrapIfStateChange trap sent.*"+config.grid_member1_vip+" now DROther"]

        LookFor_info=[]

        LookFor_sys=[".*named.*info shutting down.*",".* named.*notice exiting.*",".*named.*notice starting BIND.*(Supported Preview Version).*",".*named.*notice running on.*",".*named.*info all zones loaded.*",".*named.*notice running.*"]
        flag_info_not=1
        flag_sys_not=1

        for look in LookFor_info_not:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member1_vip)
            print(logs)
            if logs:
                flag_info_not=0

        for look in LookFor_sys_not:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member1_vip)
            print(logs)
            if logs:
                flag_sys_not=0

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member1_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member1_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1

        print(flag_info_not,flag_sys_not,flag_info,flag_sys)
        if flag_info_not==1 and flag_sys_not==1 and flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False

    @pytest.mark.run(order=126)
    def test_126_Stop_DNS_on_new_active_node_with_anycast_restart_behavior_OFF(self):
        log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
        log("start","/var/log/syslog",config.grid_member1_vip)

        dns_stop_services(config.grid_member1_fqdn)
        sleep(80)
        log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
        log("stop","/var/log/syslog",config.grid_member1_vip)

        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey = mykey)
        data="cat /tmp/"+config.grid_member1_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member1_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")



        LookFor_info=[".*/infoblox/dns/bin/stop_dns_service).*stopping named services.*",".*/infoblox/one/bin/anycast_control).*Stopping ospfd process.*",".*/infoblox/one/bin/anycast_control).*Stopping zebra process.*"]

        LookFor_sys=[".*named.*info shutting down.*",".*named.*notice exiting.*"]

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member1_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member1_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1
        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False

    @pytest.mark.run(order=127)
    def test_127_Start_DNS_on_new_active_node_with_anycast_restart_behavior_OFF(self):
        log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
        log("start","/var/log/syslog",config.grid_member1_vip)

        dns_start_services(config.grid_member1_fqdn)
        log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
        log("stop","/var/log/syslog",config.grid_member1_vip)

        print("\n******************************infoblox_var_infoblox.log******************************************************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey = mykey)
        data="cat /tmp/"+config.grid_member1_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member1_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")



        LookFor_info=[".*/infoblox/one/bin/anycast_control).*Starting zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting ospfd process.*"]

        LookFor_sys=[".*named.*notice starting BIND.*(Supported Preview Version).*",".*named.*info all zones loaded.*",".*named.*notice running.*",".*zebra.*notice Zebra.*starting.*vty@2601.*",".*ospfd.*notice OSPFd.*starting.*vty@2604.*"]

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member1_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1


        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member1_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1

        print(flag_info,flag_sys)
        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False

    pytest.mark.run(order=128)
    def test_128_Set_HA_pair_as_GMC_and_check_if_able_to_set_anycast_restart_behavior_ON(self):

        get_ref = ib_NIOS.wapi_request('GET', object_type="member?_return_fields=master_candidate")
        print(get_ref)

        for ref in json.loads(get_ref):
            if config.grid_member1_fqdn in ref['_ref']:
                data = {"master_candidate": True}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: Can't set master candidate to true for member")
                        assert False
                else:
                    print("Success: set master candidate to true for member")
                    assert True
        remove()
        sleep(300)
        check_able_to_login_appliances(config.grid_member1_vip)
        print("\n============================================\n")
        print("setting restart anycast with dns restart on")
        print("\n============================================\n")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')

            child.sendline('set restart_anycast_with_dns_restart on')

            child.expect('>')
            output = child.before
            if 'ERROR: This setting may only be changed on the active MASTER' in child.before:
                child.close()
                assert True
            else:
                child.close()
                raise Exception("Able to set cli command in master candidate")
        except Exception as e:
            assert False


    @pytest.mark.run(order=129)
    def test_129_GMC_grid_master_candidate_HA_pair_check_if_able_to_set_anycast_restart_behavior_OFF(self):

        check_able_to_login_appliances(config.grid_vip)
        remove()
        print("\n============================================\n")
        print("setting restart anycast with dns restart off")
        print("\n============================================\n")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')

            child.sendline('set restart_anycast_with_dns_restart off')

            child.expect('>')
            output = child.before
            if 'ERROR: This setting may only be changed on the active MASTER' in child.before:
                child.close()
                assert True
            else:
                child.close
                raise Exception("Able to set cli command in master candidate")
        except Exception as e:
            assert False

    @pytest.mark.run(order=130)
    def test_130_Promote_GMC_candidate_HA_pair_as_master(self):
        #for db synchronization
        sleep(240)
        remove()
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set promote_master')
        child.expect(': ')
        child.sendline('n')
        child.expect(': ')
        child.sendline('y')
        child.expect(': ')
        child.sendline('y')
        sleep(10)
        print(child.before)
        child.close()
        sleep(600)
        check_able_to_login_appliances(config.grid_vip)
        check_able_to_login_appliances(config.grid_member1_vip)
        
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show network')
        child.expect('Infoblox >')
        print(child.before)
        child.close()

        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show network')
        child.expect('Infoblox >')
        output = child.before
        print(output)
        if 'Master of Infoblox Grid' in output:
            print("Grid master promotion successfull")
            assert True
        else:
            print("Grid master promotion failed")
            assert False



    @pytest.mark.run(order=131)
    def test_131_Verify_anycast_cli_on_behavior_on_new_promoted_master(self):
        remove()
        print("\n============================================\n")
        print("setting restart anycast with dns restart on")
        print("\n============================================\n")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')

            child.sendline('set restart_anycast_with_dns_restart on')

            child.expect('>')
            child.sendline('show restart_anycast_with_dns_restart')
            child.expect('>')

            if 'restart_anycast_with_dns_restart is set to "on"' in child.before:
                child.close()
                assert True
            else:
                raise(Exception)

        except Exception as e:
            child.close()
            print("Failure")
            print (e)
            assert False

    @pytest.mark.run(order=132)
    def test_132_Verify_anycast_cli_off_behavior_on_new_promoted_master(self):
        remove()
        print("\n============================================\n")
        print("setting restart anycast with dns restart off")
        print("\n============================================\n")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')

            child.sendline('set restart_anycast_with_dns_restart off')

            child.expect('>')
            child.sendline('show restart_anycast_with_dns_restart')
            child.expect('>')

            if 'restart_anycast_with_dns_restart is set to "off"' in child.before:
                child.close()
                assert True
            else:
                raise(Exception)

        except Exception as e:
            child.close()
            print("Failure")
            print (e)
            assert False




    @pytest.mark.run(order=133)
    def test_133_Mark_old_master_as_GMC_and_promote_as_master(self):
        check_able_to_login_appliances(config.grid_vip)
        sleep(40)
        get_ref = ib_NIOS.wapi_request('GET', object_type="member?_return_fields=master_candidate",grid_vip=config.grid_member1_vip)
        print(get_ref)

        for ref in json.loads(get_ref):
            if config.grid_fqdn in ref['_ref']:
                data = {"master_candidate": True}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data),grid_vip=config.grid_member1_vip)
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: Can't set master candidate to true for member")
                        assert False
                    else:
                        print("Success: Set master candidate to true for member")
                        #sleep(180)
                        assert True
        #sleep for db syncronization
        #sleep(240)
        remove()
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set promote_master')
        child.expect(': ')
        child.sendline('n')
        child.expect(': ')
        child.sendline('y')
        child.expect(': ')
        child.sendline('y')
        print(child.before)
        sleep(10)
        child.close()
        sleep(600)
        check_able_to_login_appliances(config.grid_vip)

        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show network')
        child.expect('Infoblox >')
        print(child.before)
        child.close()
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show network')
        child.expect('Infoblox >')
        output = child.before
        print(output)
        if 'Master of Infoblox Grid' in output:
            print("Grid master promotion successfull")
            assert True
        else:
            print("Grid master promotion failed")
            assert False

    @pytest.mark.run(order=134)
    def test_134_Move_the_binary_named_file_to_a_different_name_and_perform_DNS_restart(self):
        print("\n====================================")
        print("\n Restart DNS services normally")
        print("\n====================================")
        check_able_to_login_appliances(config.grid_vip)
        set_cli_anycast_restart_on(config.grid_vip)

        log("start","/infoblox/var/infoblox.log",config.grid_member3_vip)
        log("start","/var/log/syslog",config.grid_member3_vip)
        sleep(30)
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member3_vip)
        try:
            child.expect('#')
            child.sendline('mount -o remount,rw /')
            child.expect('#')
            child.sendline('cp /usr/sbin/named /usr/sbin/named-orig')
            child.expect('#')
            #child.sendline('ls -ltr /usr/sbin/named')
            child.sendline('mv /usr/sbin/named /usr/sbin/named-bak')
            #child.sendline('ls -ltr /usr/sbin/named')
	    child.expect('#')
	    print(child.before)
            child.close()
            assert True

        except Exception as e:
            child.close()
            print("Failure: Can't moved back-named")
            print (e)
            assert False


        dns_restart_services()
        sleep(60)
        log("stop","/infoblox/var/infoblox.log",config.grid_member3_vip)
        log("stop","/var/log/syslog",config.grid_member3_vip)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey = mykey)
        data="cat /tmp/"+config.grid_member3_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
	stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member3_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")


        LookFor_info=[".*/infoblox/one/bin/anycast_control).*Stopping ospfd process.*",".*/infoblox/one/bin/anycast_control).*Stopping ospf6d process.*",".*/infoblox/one/bin/anycast_control).*Stopping bgpd process.*",".*/infoblox/one/bin/anycast_control).*Stopping zebra process.*"]


        LookFor_sys=[".*named.*info shutting down.*",".*named.*info no longer listening on.*"+config.grid_member3_vip+".*",".*named.*info no longer listening on.*"+config.grid_member3_ipv6+".*",".*named.*notice exiting.*"]
        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member3_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member3_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1

        print(flag_info,flag_sys)

        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False
    @pytest.mark.run(order=135)
    def test_135_Restore_the_binary_named_file_to_a_original_name_and_perform_DNS_restart(self):

        log("start","/infoblox/var/infoblox.log",config.grid_member3_vip)
        log("start","/var/log/syslog",config.grid_member3_vip)
        sleep(30)
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member3_vip)
        try:
            child.logfile=sys.stdout
            child.expect('#')
            child.sendline('mv /usr/sbin/named-bak /usr/sbin/named')
            child.expect('#')
	    print(child.before)
            child.close()
            assert True

        except Exception as e:
            child.close()
            print("Failure: Can't move back-named")
            print (e)
            assert False


        dns_restart_services()
        sleep(40)
        log("stop","/infoblox/var/infoblox.log",config.grid_member3_vip)
        log("stop","/var/log/syslog",config.grid_member3_vip)

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.client_ip, username=config.client_username, pkey = mykey)
        data="cat /tmp/"+config.grid_member3_vip+"_infoblox_var_infoblox.log\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        print("\n**************************var_log_messages*****************************************************************")
        data="cat /tmp/"+config.grid_member3_vip+"_var_log_messages\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        client.close()
        print("\n*******************************END logs************************************************************")
	LookFor_info=[".*/infoblox/one/bin/anycast_control).*Starting zebra process.*",".*/infoblox/one/bin/anycast_control).*Starting bgpd process.*",".*/infoblox/one/bin/anycast_control).*Starting ospfd process.*",".*/infoblox/one/bin/anycast_control).*Starting ospf6d process.*"]


        LookFor_sys=[".*named.*notice starting BIND.*",".*named.*notice running on Linux.*",".*named.*info listening on IPv4 interface eth1.*"+config.grid_member3_vip+".*",".*named.*info listening on IPv6 interface eth1.*"+config.grid_member3_ipv6+".*",".*named.*info all zones loaded.*",".*named.*notice running.*",".*zebra.*notice Zebra.*starting.*",".*bgpd.*notice BGPd.*starting.*",".*ospfd.*notice OSPFd.*starting.*",".*ospf6d.*notice OSPF6d.*starts.*"]

        flag_info=0
        flag_sys=0

        for look in LookFor_info:
            print(look)
            logs=logv(look,"/infoblox/var/infoblox.log",config.grid_member3_vip)
            print(logs)
            if logs:
                flag_info=flag_info+1

        for look in LookFor_sys:
            print(look)

            logs=logv(look,"/var/log/syslog",config.grid_member3_vip)
            print(logs)
            if logs:
                flag_sys=flag_sys+1

        print(flag_info,flag_sys)

        if flag_info==len(LookFor_info) and flag_sys==len(LookFor_sys):
            assert True
        else:
            assert False

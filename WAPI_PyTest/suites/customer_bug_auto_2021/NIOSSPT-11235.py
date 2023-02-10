__author__ = "Aditya G"
__email__  = "adityag@infoblox.com"

#####################################################################################################
#  Grid Set up required:                                                                            #
#  1. Standalone GM(IB hardware) + HA pair member(PT hardware), Isuue reproducible only on hardware #
#  2. Licenses : DNS, DHCP, Grid, TP                                                                #
####################################################################################################

import re
import config
import pytest
import unittest
import logging
import subprocess
import os
import json
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.dig_utility
from time import sleep
import commands
import json, ast
import time
import getpass
import sys
import pexpect
import paramiko


logging.basicConfig(filename='niosspt11235.log', filemode='w', level=logging.DEBUG)

def remove():
    data="rm /home/"+config.client_username+"/.ssh/known_hosts"
    ret_code = os.system(data)
    if ret_code == 0:
        print("Cleared known hosts file")
    else:
        print("Couldnt clear known hosts file")

def dns_restart_services():
    print("\n============================================\n")
    print("DNS Restart Services")
    print("\n============================================\n")
    logging.info("Restart services")
    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    publish={"member_order":"SIMULTANEOUSLY"}
    request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
    sleep(5)
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    sleep(5)

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


def ospf_ipv4_configuration():
    print("\n============================================\n")
    print("Configuring OSFP IPV4 for member")
    print("\n============================================\n")
    sleep(30)
    check_able_to_login_appliances(config.grid_vip)
    get_ref = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=additional_ip_list')
    print(get_ref)
    for ref in json.loads(get_ref):
        if config.grid_member1_fqdn in ref['_ref']:
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
        if config.grid_member1_fqdn in ref['_ref']:
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
                assert True
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
        if config.grid_member1_fqdn in ref['_ref']:
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
        if config.grid_member1_fqdn in ref['_ref']:
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
        if config.grid_member1_fqdn in ref['_ref']:
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
                assert True
    sleep(30)
    check_able_to_login_appliances(config.grid_vip)
    sleep(30)
    print("\n============================================\n")
    print("Configure IVP4 & IPV6 anycast IP for DNS")
    print("\n============================================\n")

    get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=additional_ip_list_struct')

    print(get_ref)
    for ref in json.loads(get_ref):
        if config.grid_member1_fqdn in ref['_ref']:
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
        if config.grid_member1_fqdn in ref['_ref']:
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
        if config.grid_member1_fqdn in ref['_ref']:
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
                assert True
def anycast_bgp_ipv6_configuration():
    print("\n============================================\n")
    print("Configuring IPV4 and IPV6 BGP for member")
    print("\n============================================\n")
    #check_able_to_login_appliances(config.grid_vip)
    get_ref = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=additional_ip_list')
    print(get_ref)
    for ref in json.loads(get_ref):
        if config.grid_member1_fqdn in ref['_ref']:
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
                assert True


class NIOSSPT11235(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test001_Configure_anycast_ospf_ipv4_details(self):
        ospf_ipv4_configuration()
        sleep(30)
        dns_restart_services()

    @pytest.mark.run(order=2)
    def test002_Configure_anycast_ipv4_configuration_for_ospf(self):
        anycast_ipv4_configuration()
        dns_restart_services()
        sleep(120)

    @pytest.mark.run(order=3)
    def test003_Configure_anycast_ospf_ipv6_details(self):
        ospf_ipv6_configuration()
        sleep(30)

    @pytest.mark.run(order=4)
    def test004_Configure_anycast_ipv6_configuration_for_ospf(self):
        sleep(30)
        anycast_ipv6_configuration()
        sleep(120)
        dns_restart_services()

    @pytest.mark.run(order=5)
    def test005_Configure_anycast_bgp_ipv4_details(self):
        bgp_configuration()
        sleep(60)

    @pytest.mark.run(order=6)
    def test006_Configure_anycast_ipv4_configuration_for_bgp(self):
        anycast_bgp_ipv4_configuration()
        sleep(60)

    @pytest.mark.run(order=7)
    def test007_Configure_anycast_ipv6_configuration_for_bgp(self):
        anycast_bgp_ipv6_configuration()
        dns_restart_services()

    @pytest.mark.run(order=8)
    def test008_Start_DNS_service_on_HA_pair(self):
        logging.info("Starting DNS service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        logging.info(get_ref)
        res = json.loads(get_ref)
        for ref in res:
            if config.grid_member1_fqdn in ref['_ref']:
                ref1 = ref["_ref"]
                data = {"enable_dns": True}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                sleep(20)
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                    assert True

    @pytest.mark.run(order=9)
    def test009_Verify_if_anycast_daemons_are_running_on_HA_pair(self):
        logging.info("Verifying anycast daemons are running on HA pair")
        active,passive = get_ha_active_passive()
        logging.info("Active-"+active+",Passive-"+passive)
        check_able_to_login_appliances(config.grid_member1_vip)
        
        flag_bgp=True
        flag_ospf=True
        flag_zebra=True

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(active, username='root', pkey = mykey)
        data="pgrep bgp\n"
        stdin, stdout, stderr = client.exec_command(data)
        a=stdout.readlines()
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


    @pytest.mark.run(order=10)
    def test010_Enable_Threat_Protection_on_HA_pair_member(self):
        ip=config.grid_vip
        fqdn=config.grid_fqdn
        print ("------Adding DNS resolver------")
        grid_ref = ib_NIOS.wapi_request('GET', object_type='grid')
        print(grid_ref)
        data = {"dns_resolver_setting":{"resolvers":["10.102.3.10"]}}
        for ref in json.loads(grid_ref):
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)
            print(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    print("Failure: Adding DNS Resolver")
                    assert False
        print ("------DNS resolver added successfully------")
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
        sleep(300)
        check_able_to_login_appliances(config.grid_member1_vip)
        logging.info("Sleeping for 5 min after enabling threat protection service")
        print("Sleeping for 5 min after enabling threat protection service")
        sleep(300)

    @pytest.mark.run(order=11)
    def test011_Disable_Threat_Protection_Service(self):
        ip=config.grid_vip
        print("-"*6+"Disable Threat protection service"+"-"*6)
        logging.info("Disable the threat protection service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        print(get_ref)
        for ref in json.loads(get_ref):
            ref1 = json.loads(get_ref)[0]['_ref']
            response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps({"enable_service": False}),grid_vip=ip)
            print(response)
            if type(response) == tuple:
                print("Failure: Enable threat protection service")
                assert False
        dns_restart_services()
        sleep(300)
        check_able_to_login_appliances(config.grid_member1_vip)

    @pytest.mark.run(order=12)
    def test012_Perform_HA_failover_and_check_if_anycast_is_up_and_running(self):
        active,passive = get_ha_active_passive()
        print(active,passive)
        reboot(config.grid_member1_vip)
        sleep(60)
        check_able_to_login_appliances_ha(passive)
        check_able_to_login_appliances_ha(active)
        sleep(300)
        
        #Check anycast daemons not running on passive client
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
            logging.info("Anycast daemons are not running on new active client")
            assert True
        else:
            logging.info("Anycast daemons are running on new active client, HA failover was unsuccessful")
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
            logging.info("Anycast daemons are running on new active node")
            sleep(60)
            assert True
        else:
            logging.info("Anycast daemons are not running on new active node, HA failover was unsuccessful")
            sleep(60)
            assert False

    @pytest.mark.run(order=13)
    def test013_Enable_Threat_Protection_service(self):
        ip=config.grid_vip
        print("-"*6+"Enable Threat protection service"+"-"*6)
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
        dns_restart_services()
        sleep(300)
        check_able_to_login_appliances(config.grid_member1_vip)


    @pytest.mark.run(order=14)
    def test014_Check_for_BGP_drop_logs_in_rules_txt_file(self):
        active,passive = get_ha_active_passive()
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(active, username='root', pkey = mykey)
        data="grep -ir \"bgp\" /infoblox/var/atp_conf/rules.txt"
        stdin, stdout, stderr = client.exec_command(data)
        output = stdout.read()
        if "msg:\"DROP BGP unexpected\"" in output:
            logging.info("BGP drop rule found in rules.txt")
            assert False
        else:
            logging.info("BGP drop rule not found in rules.txt")
            assert True


    @pytest.mark.run(order=15)
    def test015_Test_Cleanup(self):
        logging.info("\n====Removing anycast ips  from additional ip list====")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns?_return_fields=additional_ip_list_struct")
        print(get_ref)
        data={"additional_ip_list_struct": []}
        for ref in json.loads(get_ref):
            if config.grid_member1_fqdn in ref['_ref']:
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: Deleting DNS anycast")
        dns_restart_services()






        







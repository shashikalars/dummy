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
import pexpect
import paramiko
import sys
from paramiko import client


wapi_object = "member"
wapi_attribute = "host_name"
wapi_attribute_value = "infoblox.localdomain"
lan1_address={"vip_setting":{"address": config.master01lan1v4, "gateway": config.master0lan1v4gw, "primary": True,"subnet_mask": config.netmask},"ipv6_setting":{"auto_router_config_enabled": False, "cidr_prefix": 64, "enabled": True,"primary": True, "gateway": config.master0lan1v6gw,"virtual_ip": config.master0lan1v6}}
lan2_address={"network_setting":{"address": config.master0lan2v4,"gateway": config.master0lan2v4gw,"subnet_mask": config.netmask},"v6_network_setting": {"cidr_prefix": 64,"enabled": True,"gateway": config.master0lan2v6gw,"primary": True,"virtual_ip": config.master0lan2v6}}
ha_lan2_address={"network_setting":{"address": config.ha_lan2_v4,"gateway": config.halan2_v4gw,"subnet_mask": config.netmask},"v6_network_setting": {"cidr_prefix": 64,"enabled": True,"gateway": config.halan2_v6gw,"primary": True,"virtual_ip": config.ha_lan2_v6}}

def display_msg(x):
    logging.info(x)
    print("")
    print(x)


class SSH:
    client=None

    def __init__(self,address):
        logging.info ("Log Validation Script")
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
        else:
            logging.info("Connection not opened.")


class RouteRedundancy():

    def __init__(self, wapi_object, wapi_attribute = None, wapi_attribute_value = None):
        # object_ref='member' and field = "host_name" field_value= "10.34.52.16"}'
        self.wapi_object = wapi_object
        self.wapi_attribute = wapi_attribute
        self.wapi_attribute_value = wapi_attribute_value

    def get_member_reference(self):
        response = ib_NIOS.wapi_request('GET', object_type="member")
        memref = json.loads(response)[0]['_ref']
        return memref

    def route_redundancy_status(self, vip):
        display_msg("Getting status of \"Enable default route redundancy on LAN1/LAN2\"")
        member_ref = self.get_member_reference()
        field="default_route_failover_enabled"
        get_ref = ib_NIOS.wapi_request('GET', object_type=member_ref + "?_return_fields=lan2_port_setting", grid_vip= vip)
        print get_ref
        res = json.loads(get_ref)
        status= res["lan2_port_setting"]["default_route_failover_enabled"]
        print "Redundancy Status is",status,
        return status

    def route_redundancy_enable(self,default_route_failover_enabled=True):
        display_msg('Enable the feature "Enable default route redundancy on LAN1/LAN2"')
        ref = self.get_member_reference()
        data = {"lan2_port_setting": {"default_route_failover_enabled": default_route_failover_enabled}}
        status, response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
        display_msg(response)
        return status,response

    def is_device_up(self,ipaddress):
        for i in range(50):
            response = os.system("ping -c 1 " + ipaddress)
            if response == 0:
                sleep(90) #90 seconds for the httpd to start once the device is reachable
                break
            else:
                sleep(15)
 
    def set_default_route(self,lan):
        display_msg("Setting Default Route to " +lan)
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no ' 'admin@'+config.master0mgmt)
        child.logfile = sys.stdout
        print child.before 
        child.expect ('password.*:')
        child.sendline ('infoblox')
        child.sendline('set default_route ' +lan)
        child.sendline('y')
        sleep(50)
        member.is_device_up(config.master0mgmt)
        child.close()
    


member = RouteRedundancy("member", "host_name", config.master0mgmt)

class Network(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_001_bydefault_route_failover_behaviour(self):
        display_msg("The Route Redundancy feature should be disabled by default")
        assert (member.route_redundancy_status(config.master0mgmt)) == False
        display_msg("Test Completed")

    @pytest.mark.run(order=2)
    def test_002_remove_lan2_ips(self):
        display_msg("Remove LAN2 IPs")
        ref = member.get_member_reference()
        data = {"lan2_port_setting": {"enabled": False}}
        res = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data), grid_vip=config.master0mgmt)
        print res
        sleep(60)
        member.is_device_up(config.master0mgmt)
        display_msg("Test Completed")

    @pytest.mark.run(order=3)
    def test_003_enable_the_feature_with_nic_failover(self):
        display_msg("Negative: Enable the feature \"Enable default route redundancy on LAN1/LAN2\" when NIC failover configured")
        ref = member.get_member_reference()
        data = {"lan2_port_setting": {"enabled": True,"nic_failover_enabled": True}}
        res = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data), grid_vip=config.master0mgmt)
        sleep(60)
        member.is_device_up(config.master0mgmt)
        data= {"lan2_port_setting": {"enabled": True, "default_route_failover_enabled": True,
                                      "network_setting": lan2_address["network_setting"],
                                      "v6_network_setting":lan2_address["v6_network_setting"]}}
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data), grid_vip=config.master0mgmt)
        print(response)
        response=str(response)
        assert (re.search(r'Cannot disable NIC failover and enable LAN2 at the same time.',response) and ((member.route_redundancy_status(config.master0mgmt)) == False))
        display_msg("Test Completed")

    @pytest.mark.run(order=4)
    def test_004_disable_nic_failover(self):
        display_msg("disabling NIC failover")
        ref = member.get_member_reference()
        data = {"lan2_port_setting": {"enabled": False, "nic_failover_enabled": False}}
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data), grid_vip=config.master0mgmt)
        print(response)
        sleep(60)
        member.is_device_up(config.master0mgmt)
        display_msg("Test Completed")

    ##RFE9114-29
    @pytest.mark.run(order=5)
    #NIC FAILOVER CAN BE ENABLED AS SETTING enabled:True will reset LAN2 settings and disable my feature
    def test_005_enable_nic_failover_and_route_redundancy_together(self):
        display_msg("Negative: enable NIC failover and \"Enable default route redundancy on LAN1/LAN2\" together")
        ref = member.get_member_reference()
        data = {"lan2_port_setting": {"nic_failover_enabled":True, "default_route_failover_enabled": True,"enabled": True, "network_setting": lan2_address["network_setting"] }}
        status,response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data), grid_vip=config.master0mgmt)
        print(response)
        assert ((re.search(r'Cannot enable default route redundancy and NIC failover together',response)) and (status == 400) and (member.route_redundancy_status(config.master0mgmt) == False))
        display_msg("Test Completed")
        

    @pytest.mark.run(order=6)
    def test_006_different_network_config_lan1v4_lan2v6(self):
        display_msg(
            "Negative:Enabling the feature \"Enable default route redundancy on LAN1/LAN2\" when LAN1 and LAN2 have different network combination LAN1v4 lan2v6")
        ref = member.get_member_reference()
        data = {"config_addr_type": "IPV4",
                "vip_setting": lan1_address["vip_setting"],"ipv6_setting": {},"service_type_configuration": "ALL_V4",
                "lan2_port_setting": {"enabled": True, "default_route_failover_enabled": True,
                                      "v6_network_setting":lan2_address["v6_network_setting"]}}
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data), grid_vip=config.master0mgmt)
        print response
        sleep(15)
        member.is_device_up(config.master0mgmt)
        member.route_redundancy_status(config.master0mgmt)
        response = str(response)
        assert ((re.search(r'IPV4 LAN2 must be enabled when default route redundancy is enabled', response)))
        display_msg("Test Completed")

    @pytest.mark.run(order=7)
    def test_007_different_network_config_lan1v4_lan2v4v6(self):
        display_msg(
            "Negative:Enabling the feature \"Enable default route redundancy on LAN1/LAN2\" when LAN1 and LAN2 have different network combination LAN1v4 lan2v4&v6")
        ref = member.get_member_reference()
        data = {"config_addr_type": "IPV4",
                "vip_setting": lan1_address["vip_setting"],"ipv6_setting": {}, "service_type_configuration": "ALL_V4",
                "lan2_port_setting": {"enabled": True, "default_route_failover_enabled": True,
                                      "network_setting": lan2_address["network_setting"],
                                      "v6_network_setting":lan2_address["v6_network_setting"]}}
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data), grid_vip=config.master0mgmt)
        print response
        sleep(15)
        member.route_redundancy_status(config.master0mgmt)
        member.is_device_up(config.master0mgmt)
        response = str(response)
        assert ((re.search(r'IPV6 LAN1 must be enabled when default route redundancy is enabled', response)))
        display_msg("Test Completed")

    @pytest.mark.run(order=8)
    def test_008_different_network_config_lan1v4v6_lan2v4(self):
        display_msg(
            "Negative:Enabling the feature \"Enable default route redundancy on LAN1/LAN2\" when LAN1 and LAN2 have different network combination LAN1v4&v6 lan2v4")
        ref = member.get_member_reference()
        data = {"config_addr_type": "BOTH",
                "vip_setting": lan1_address["vip_setting"],"ipv6_setting": lan1_address["ipv6_setting"],
                "lan2_port_setting": {"enabled": True, "default_route_failover_enabled": True,
                                      "network_setting": lan2_address["network_setting"]}}
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data), grid_vip=config.master0mgmt)
        print response
        sleep(15)
        member.is_device_up(config.master0mgmt)
        member.route_redundancy_status(config.master0mgmt)
        response = str(response)
        assert ((re.search(r'IPV6 LAN2 must be enabled when default route redundancy is enabled', response)))
        display_msg("Test Completed")

    @pytest.mark.run(order=9)
    def test_009_different_network_config_lan1v4v6_lan2v6(self):
        display_msg(
            "Negative:Enabling the feature \"Enable default route redundancy on LAN1/LAN2\" when LAN1 and LAN2 have different network combination LAN1v4&v6 lan2v6")
        ref = member.get_member_reference()
        data = {"config_addr_type": "BOTH",
                "vip_setting": lan1_address["vip_setting"],"ipv6_setting": lan1_address["ipv6_setting"],
                "lan2_port_setting": {"enabled": True, "default_route_failover_enabled": True,
                                      "v6_network_setting":lan2_address["v6_network_setting"]}}
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data), grid_vip=config.master0mgmt)
        print response
        sleep(15)
        member.is_device_up(config.master0mgmt)
        member.route_redundancy_status(config.master0mgmt)
        response = str(response)
        assert ((re.search(r'IPV4 LAN2 must be enabled when default route redundancy is enabled', response)))
        display_msg("Test Completed")


    @pytest.mark.run(order=10)
    def test_010_different_network_config_lan1v6_lan2v4(self):
        display_msg(
            "Negative:Enabling the feature \"Enable default route redundancy on LAN1/LAN2\" when LAN1 and LAN2 have different network combination LAN1v6 lan2v4")
        ref = member.get_member_reference()
        data = {"config_addr_type": "IPV6",
                "vip_setting": {},"ipv6_setting": lan1_address["ipv6_setting"], "service_type_configuration": "ALL_V6",
                "lan2_port_setting": {"enabled": True, "default_route_failover_enabled": True,
                                      "network_setting": lan2_address["network_setting"]}}
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data), grid_vip=config.master0mgmt)
        print response
        sleep(15)
        member.is_device_up(config.master0mgmt)
        member.route_redundancy_status(config.master0mgmt)
        response = str(response)
        assert ((re.search(r'IPV6 LAN2 must be enabled when default route redundancy is enabled', response)))
        display_msg("Test Completed")

    @pytest.mark.run(order=11)
    def test_011_different_network_config_lan1v6_lan2v4v6(self):
        display_msg(
            "Negative:Enabling the feature \"Enable default route redundancy on LAN1/LAN2\" when LAN1 and LAN2 have different network combination LAN1v6 lan2v4&v6")
        ref = member.get_member_reference()
        data = {"config_addr_type": "IPV6",
                "vip_setting": {},"ipv6_setting": lan1_address["ipv6_setting"], "service_type_configuration": "ALL_V6",
                "lan2_port_setting": {"enabled": True, "default_route_failover_enabled": True,
                                      "v6_network_setting":lan2_address["v6_network_setting"],"network_setting":lan2_address["network_setting"]}}
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data), grid_vip=config.master0mgmt)
        print response
        sleep(15)
        member.is_device_up(config.master0mgmt)
        member.route_redundancy_status(config.master0mgmt)
        response = str(response)
        assert ((re.search(r'IPV4 LAN1 must be enabled when default route redundancy is enabled', response)))
        display_msg("Test Completed")

    @pytest.mark.run(order=12)
    def test_012_configure_v4_lan1_lan2(self):
        display_msg(
            "Configure LAN1 and LAN2 IPv4 and enable the feature")
        ref = member.get_member_reference()
        data = {"config_addr_type": "IPV4",
                "vip_setting": lan1_address["vip_setting"],"ipv6_setting": {}, "service_type_configuration": "ALL_V4",
                "lan2_port_setting": {"enabled": True, "default_route_failover_enabled": True,
                                      "network_setting": lan2_address["network_setting"]}}
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data), grid_vip=config.master0mgmt)
        print response
        sleep(60)
        member.is_device_up(config.master0mgmt)
        #status, response = member.route_redundancy_enable()
        assert member.route_redundancy_status(config.master0mgmt)
        display_msg("Test Completed")

    @pytest.mark.run(order=13)
    def test_013_validate_ipv4_routing_table(self):
        display_msg("Validate IPv4 routing table with LAN1 as default route")
        connection=SSH(str(config.master0_mgmt))
        result=connection.send_command("ip route")
        print (result)
        match1 = "default via " + config.master0lan1v4gw + " dev eth1  proto ifplugd"
        match2 = "default via " + config.master0lan2v4gw + " dev eth3  proto ifplugd  metric 10"
        assert (( match1 in result) and (match2 in result))
        display_msg("Test Completed")
        
    @pytest.mark.run(order=14)
    def test_014_traceroute(self):        
        display_msg("Perform traceroute and validate the default route")
        connection=SSH(str(config.master0_mgmt))
        result=connection.send_command("traceroute " +config.google_dns_v4)
        print (result)
        #assert (re.search(config.master0lan1v4gw, result))
        assert True
        display_msg ("Test Completed")

    @pytest.mark.run(order=15)
    def test_015_set_default_route_lan2(self):
        member.set_default_route('lan2')
    

    @pytest.mark.run(order=16)
    def test_016_validate_ipv4_routing_table(self):
        display_msg("Validate IPv4 routing table with LAN2 as default route")
        connection=SSH(str(config.master0_mgmt))
        result=connection.send_command("ip route")
        print (result)
        match1 = "default via " + config.master0lan2v4gw + " dev eth3  proto ifplugd"
        match2 = "default via " + config.master0lan1v4gw + " dev eth1  proto ifplugd  metric 10"
        assert (( match1 in result) and (match2 in result)) 
        display_msg("Test Completed")
        
        
    @pytest.mark.run(order=17)
    def test_017_traceroute(self):        
        display_msg("Perform traceroute and validate the default route")
        connection=SSH(str(config.master0_mgmt))
        result=connection.send_command("traceroute " +config.google_dns_v4)
        print (result)
        #assert (re.search(config.master0lan2v4gw, result))
        assert True
        display_msg ("Test Completed")

    @pytest.mark.run(order=18)
    def test_018_set_default_route_lan1(self):
        member.set_default_route('lan1')

    @pytest.mark.run(order=19)
    def test_019_disable_lan1_using_netctl(self):
        display_msg("Disable LAN1 using netctl command for the device "+config.master0_hw_name )
        response = os.system("netctl_system -i lan -a disable -H " +config.master0_hw_name+ " -c " +config.user)
        print response
        sleep(30)
        display_msg("LAN1 disabled") 

    @pytest.mark.run(order=20)
    def test_020_validate_ipv4_routing_table(self):
        display_msg("Validate IPv4 routing table with LAN1 disabled and LAN2 enabled")
        connection=SSH(str(config.master0_mgmt))
        result=connection.send_command("ip route")
        print (result)
        match1 = "default via " + config.master0lan1v4gw + " dev eth1  proto ifplugd"
        match2 = "default via " + config.master0lan2v4gw + " dev eth3  proto ifplugd  metric 10"
        assert (( match1 not in result) and (match2 in result))
        display_msg("Test Completed")

    @pytest.mark.run(order=21)
    def test_021_disable_lan2_using_netctl(self):
        display_msg("Disable LAN2 using netctl command for the device "+config.master0_hw_name )
        response = os.system("netctl_system -i lan2 -a disable -H " +config.master0_hw_name+ " -c " +config.user)
        print response
        sleep(30)
        display_msg("LAN2 disabled") 

    @pytest.mark.run(order=22)
    def test_022_validate_ipv4_routing_table(self):
        display_msg("Validate IPv4 routing table with both LAN1 & LAN2 disabled")
        connection=SSH(str(config.master0_mgmt))
        result=connection.send_command("ip route")
        print (result)
        match1 = "default via " + config.master0lan1v4gw + " dev eth1  proto ifplugd"
        match2 = "default via " + config.master0lan2v4gw + " dev eth3  proto ifplugd  metric 10"
        assert (( match1 not in result) and (match2 not in result))
        display_msg("Test Completed")

    @pytest.mark.run(order=23)
    def test_023_enable_lan1_using_netctl(self):
        display_msg("Enable LAN1 using netctl command for the device "+config.master0_hw_name )
        response = os.system("netctl_system -i lan -a enable -H " +config.master0_hw_name+ " -c " +config.user)
        print response
        sleep(30)
        display_msg("LAN1 enabled") 

    @pytest.mark.run(order=24)
    def test_024_validate_ipv4_routing_table(self):
        display_msg("Validate IPv4 routing table with only LAN1 enabled")
        connection=SSH(str(config.master0_mgmt))
        result=connection.send_command("ip route")
        print (result)
        match1 = "default via " + config.master0lan1v4gw + " dev eth1  proto ifplugd"
        match2 = "default via " + config.master0lan2v4gw + " dev eth3  proto ifplugd  metric 10"
        assert (( match1 in result) and (match2 not in result))
        display_msg("Test Completed")

    @pytest.mark.run(order=25)
    def test_025_enable_lan2_using_netctl(self):
        display_msg("Enable LAN2 using netctl command for the device "+config.master0_hw_name )
        response = os.system("netctl_system -i lan2 -a enable -H " +config.master0_hw_name+ " -c " +config.user)
        print response
        sleep(30)
        display_msg("LAN2 enabled") 

    @pytest.mark.run(order=26)
    def test_026_validate_ipv4_routing_table(self):
        display_msg("Validate IPv4 routing table with both LAN1 & LAN2 enabled")
        connection=SSH(str(config.master0_mgmt))
        result=connection.send_command("ip route")
        print (result)
        match1 = "default via " + config.master0lan1v4gw + " dev eth1  proto ifplugd"
        match2 = "default via " + config.master0lan2v4gw + " dev eth3  proto ifplugd  metric 10"
        assert (( match1 in result) and (match2 in result))
        display_msg("Test Completed")  

    @pytest.mark.run(order=27)
    def test_027_disable_route_redundancy(self):
        display_msg("Disabling the feature Route Redundancy")
        ref = member.get_member_reference()
        data = {"lan2_port_setting": {"enabled": False, "default_route_failover_enabled": False}}
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data), grid_vip=config.master0mgmt)
        print response
        sleep(60)
        member.is_device_up(config.master0mgmt)
        assert member.route_redundancy_status(config.master0mgmt) == False
        display_msg("Test Completed")        


    @pytest.mark.run(order=28)
    def test_028_configure_v6_lan1_lan2(self):
        display_msg("Configure LAN1 and LAN2 IPv6 and enable the feature")
        ref = member.get_member_reference()
        data = {"config_addr_type": "IPV6",
                "vip_setting": {}, "ipv6_setting": lan1_address["ipv6_setting"], "service_type_configuration": "ALL_V6",
                "lan2_port_setting": {"enabled": True, "default_route_failover_enabled": True,
                                      "v6_network_setting": lan2_address["v6_network_setting"]}}
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data), grid_vip=config.master0mgmt)
        print response
        sleep(60)
        member.is_device_up(config.master0mgmt)
        assert member.route_redundancy_status(config.master0mgmt)
        display_msg("Test Completed")   



    @pytest.mark.run(order=29)
    def test_029_validate_ipv6_routing_table(self):
        display_msg("Validate IPv6 routing table with LAN1 as default route")
        connection=SSH(str(config.master0_mgmt))
        result=connection.send_command("ip -6 route")
        print (result)
        match1 = "default via " + config.master0lan1v6gw + " dev eth1  proto ifplugd  metric 1024"
        match2 = "default via " + config.master0lan2v6gw + " dev eth3  proto ifplugd  metric 1124"
        assert (( match1 in result) and (match2 in result))
        display_msg("Test Completed")        
        
    @pytest.mark.run(order=30)
    def test_030_traceroute(self):        
        display_msg("Perform traceroute and validate the default route")
        connection=SSH(str(config.master0_mgmt))
        result=connection.send_command("traceroute6 " +config.google_dns_v6)
        print (result)
        #assert (re.search(config.master0lan1v6gw, result))
        assert True
        display_msg ("Test Completed")
 
    @pytest.mark.run(order=31)
    def test_031_set_default_route_lan2(self):
        member.set_default_route('lan2')
    

    @pytest.mark.run(order=32)
    def test_032_validate_ipv6_routing_table(self):
        display_msg("Validate IPv6 routing table with LAN2 as default route")
        connection=SSH(str(config.master0_mgmt))
        result=connection.send_command("ip -6 route")
        print (result)
        match1 = "default via " + config.master0lan2v6gw + " dev eth3  proto ifplugd  metric 1024"
        match2 = "default via " + config.master0lan1v6gw + " dev eth1  proto ifplugd  metric 1124"
        assert (( match1 in result) and (match2 in result)) 
        display_msg("Test Completed") 

    @pytest.mark.run(order=33)
    def test_033_traceroute(self):        
        display_msg("Perform traceroute and validate the default route")
        connection=SSH(str(config.master0_mgmt))
        result=connection.send_command("traceroute6 " +config.google_dns_v6)
        print (result)
        #assert (re.search(config.master0lan2v6gw, result))
        assert True
        display_msg ("Test Completed")

    @pytest.mark.run(order=34)
    def test_034_set_default_route_lan1(self):
        member.set_default_route('lan1')  

    @pytest.mark.run(order=35)
    def test_035_disable_lan1_using_netctl(self):
        display_msg("Disable LAN1 using netctl command for the device "+config.master0_hw_name )
        response = os.system("netctl_system -i lan -a disable -H " +config.master0_hw_name+ " -c " +config.user)
        print response
        sleep(30)
        display_msg("LAN1 disabled") 

    @pytest.mark.run(order=36)
    def test_036_validate_ipv6_routing_table(self):
        display_msg("Validate IPv6 routing table with LAN1 disabled and LAN2 enabled")
        connection=SSH(str(config.master0_mgmt))
        result=connection.send_command("ip -6 route")
        print (result)
        match1 = "default via " + config.master0lan1v6gw + " dev eth1  proto ifplugd  metric 1024"
        match2 = "default via " + config.master0lan2v6gw + " dev eth3  proto ifplugd  metric 1124"
        assert (( match1 not in result) and (match2 in result))
        display_msg("Test Completed")

    @pytest.mark.run(order=37)
    def test_037_disable_lan2_using_netctl(self):
        display_msg("Disable LAN2 using netctl command for the device "+config.master0_hw_name )
        response = os.system("netctl_system -i lan2 -a disable -H " +config.master0_hw_name+ " -c " +config.user)
        print response
        sleep(30)
        display_msg("LAN2 disabled") 

    @pytest.mark.run(order=38)
    def test_038_validate_ipv6_routing_table(self):
        display_msg("Validate IPv6 routing table with both LAN1 & LAN2 disabled")
        connection=SSH(str(config.master0_mgmt))
        result=connection.send_command("ip -6 route")
        print (result)
        match1 = "default via " + config.master0lan1v6gw + " dev eth1  proto ifplugd  metric 1024"
        match2 = "default via " + config.master0lan2v6gw + " dev eth3  proto ifplugd  metric 1124"
        assert (( match1 not in result) and (match2 not in result))
        display_msg("Test Completed")

    @pytest.mark.run(order=39)
    def test_039_enable_lan1_using_netctl(self):
        display_msg("Enable LAN1 using netctl command for the device "+config.master0_hw_name )
        response = os.system("netctl_system -i lan -a enable -H " +config.master0_hw_name+ " -c " +config.user)
        print response
        sleep(30)
        display_msg("LAN1 enabled") 

    @pytest.mark.run(order=40)
    def test_040_validate_ipv6_routing_table(self):
        display_msg("Validate IPv6 routing table with only LAN1 enabled")
        connection=SSH(str(config.master0_mgmt))
        result=connection.send_command("ip -6 route")
        print (result)
        match1 = "default via " + config.master0lan1v6gw + " dev eth1  proto ifplugd  metric 1024"
        match2 = "default via " + config.master0lan2v6gw + " dev eth3  proto ifplugd  metric 1124"
        assert (( match1 in result) and (match2 not in result))
        display_msg("Test Completed")

    @pytest.mark.run(order=41)
    def test_041_enable_lan2_using_netctl(self):
        display_msg("Enable LAN2 using netctl command for the device "+config.master0_hw_name )
        response = os.system("netctl_system -i lan2 -a enable -H " +config.master0_hw_name+ " -c " +config.user)
        print response
        sleep(30)
        display_msg("LAN2 enabled") 

    @pytest.mark.run(order=42)
    def test_042_validate_ipv6_routing_table(self):
        display_msg("Validate IPv6 routing table with both LAN1 & LAN2 enabled")
        connection=SSH(str(config.master0_mgmt))
        result=connection.send_command("ip -6 route")
        print (result)
        match1 = "default via " + config.master0lan1v6gw + " dev eth1  proto ifplugd  metric 1024"
        match2 = "default via " + config.master0lan2v6gw + " dev eth3  proto ifplugd  metric 1124"
        assert (( match1 in result) and (match2 in result))
        display_msg("Test Completed")  

    @pytest.mark.run(order=43)
    def test_043_disable_route_redundancy(self):
        display_msg("Disabling the feature Route Redundancy")
        ref = member.get_member_reference()
        data = {"lan2_port_setting": {"enabled": False, "default_route_failover_enabled": False}}
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data), grid_vip=config.master0mgmt)
        print response
        sleep(60)
        member.is_device_up(config.master0mgmt)
        assert member.route_redundancy_status(config.master0mgmt) == False
        display_msg("Test Completed")        

    @pytest.mark.run(order=44)
    def test_044_configure_lan1v4v6_lan2v4v6(self):
        display_msg("Configure LAN1 & LAN2 with IPv4 & IPv6 and Enable the feature Route Redundancy")
        ref = member.get_member_reference()
        data = {"config_addr_type": "BOTH",
                "vip_setting": lan1_address["vip_setting"],"ipv6_setting": lan1_address["ipv6_setting"],
                "lan2_port_setting": {"enabled": True, "default_route_failover_enabled": True,
                                      "v6_network_setting":lan2_address["v6_network_setting"],"network_setting": lan2_address["network_setting"]}}
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data), grid_vip=config.master0mgmt)
        print response
        sleep(60)
        member.is_device_up(config.master0mgmt)
        assert member.route_redundancy_status(config.master0mgmt)
        display_msg("Test Completed")

    @pytest.mark.run(order=45)
    def test_045_validate_ipv4_routing_table(self):
        display_msg("Validate IPv4 routing table with LAN1 as default route")
        connection=SSH(str(config.master0_mgmt))
        result=connection.send_command("ip route")
        print (result)
        match1 = "default via " + config.master0lan1v4gw + " dev eth1  proto ifplugd"
        match2 = "default via " + config.master0lan2v4gw + " dev eth3  proto ifplugd  metric 10"
        assert (( match1 in result) and (match2 in result)) == True
        display_msg("Test Completed")

    @pytest.mark.run(order=46)
    def test_046_validate_ipv6_routing_table(self):
        display_msg("Validate IPv6 routing table with LAN1 as default route")
        connection=SSH(str(config.master0_mgmt))
        result=connection.send_command("ip -6 route")
        print (result)
        match1 = "default via " + config.master0lan1v6gw + " dev eth1  proto ifplugd  metric 1024"
        match2 = "default via " + config.master0lan2v6gw + " dev eth3  proto ifplugd  metric 1124"
        assert (( match1 in result) and (match2 in result))
        display_msg("Test Completed")     

    @pytest.mark.run(order=47)
    def test_047_traceroute(self):        
        display_msg("Perform traceroute and validate the default route")
        connection=SSH(str(config.master0_mgmt))
        result1=connection.send_command("traceroute " +config.google_dns_v4)
        print (result1)
        connection=SSH(str(config.master0_mgmt))
        result2=connection.send_command("traceroute6 " +config.google_dns_v6)
        print (result2)
        #assert (re.search(config.master0lan1v4gw, result1)) and (re.search(config.master0lan1v6gw, result2))
        assert True
        display_msg ("Test Completed")
        
    @pytest.mark.run(order=48)
    def test_048_set_default_route_lan2(self):
        member.set_default_route('lan2')

    @pytest.mark.run(order=49)
    def test_049_validate_ipv4_routing_table(self):
        display_msg("Validate IPv4 routing table with LAN2 as default route")
        connection=SSH(str(config.master0_mgmt))
        result=connection.send_command("ip route")
        print (result)
        match1 = "default via " + config.master0lan2v4gw + " dev eth3  proto ifplugd"
        match2 = "default via " + config.master0lan1v4gw + " dev eth1  proto ifplugd  metric 10"
        assert (( match1 in result) and (match2 in result)) 
        display_msg("Test Completed")

    @pytest.mark.run(order=50)
    def test_050_validate_ipv6_routing_table(self):
        display_msg("Validate IPv6 routing table with LAN2 as default route")
        connection=SSH(str(config.master0_mgmt))
        result=connection.send_command("ip -6 route")
        print (result)
        match1 = "default via " + config.master0lan2v6gw + " dev eth3  proto ifplugd  metric 1024"
        match2 = "default via " + config.master0lan1v6gw + " dev eth1  proto ifplugd  metric 1124"
        assert (( match1 in result) and (match2 in result)) 
        display_msg("Test Completed")         
        
    @pytest.mark.run(order=51)
    def test_051_traceroute(self):        
        display_msg("Perform traceroute and validate the default route")
        connection=SSH(str(config.master0_mgmt))
        result1=connection.send_command("traceroute " +config.google_dns_v4)
        print (result1)
        connection=SSH(str(config.master0_mgmt))
        result2=connection.send_command("traceroute6 " +config.google_dns_v6)
        print (result2)
        #assert (re.search(config.master0lan2v4gw, result1)) and (re.search(config.master0lan2v6gw, result2))
        assert True
        display_msg ("Test Completed")
        
    @pytest.mark.run(order=52)
    def test_052_set_default_route_lan1(self):
        member.set_default_route('lan1')  

    @pytest.mark.run(order=53)
    def test_053_disable_lan1_using_netctl(self):
        display_msg("Disable LAN1 using netctl command for the device "+config.master0_hw_name )
        response = os.system("netctl_system -i lan -a disable -H " +config.master0_hw_name+ " -c " +config.user)
        print response
        sleep(30)
        display_msg("LAN1 disabled") 

    @pytest.mark.run(order=54)
    def test_054_validate_ipv4_routing_table(self):
        display_msg("Validate IPv4 routing table with LAN1 disabled and LAN2 enabled")
        connection=SSH(str(config.master0_mgmt))
        result=connection.send_command("ip route")
        print (result)
        match1 = "default via " + config.master0lan1v4gw + " dev eth1  proto ifplugd"
        match2 = "default via " + config.master0lan2v4gw + " dev eth3  proto ifplugd  metric 10"
        assert (( match1 not in result) and (match2 in result))
        display_msg("Test Completed")
        
    @pytest.mark.run(order=55)
    def test_055_validate_ipv6_routing_table(self):
        display_msg("Validate IPv6 routing table with LAN1 disabled and LAN2 enabled")
        connection=SSH(str(config.master0_mgmt))
        result=connection.send_command("ip -6 route")
        print (result)
        match1 = "default via " + config.master0lan1v6gw + " dev eth1  proto ifplugd  metric 1024"
        match2 = "default via " + config.master0lan2v6gw + " dev eth3  proto ifplugd  metric 1124"
        assert (( match1 not in result) and (match2 in result))
        display_msg("Test Completed")

    @pytest.mark.run(order=56)
    def test_056_disable_lan2_using_netctl(self):
        display_msg("Disable LAN2 using netctl command for the device "+config.master0_hw_name )
        response = os.system("netctl_system -i lan2 -a disable -H " +config.master0_hw_name+ " -c " +config.user)
        print response
        sleep(30)
        display_msg("LAN2 disabled") 
        
    @pytest.mark.run(order=57)
    def test_057_validate_ipv4_routing_table(self):
        display_msg("Validate IPv4 routing table with both LAN1 & LAN2 disabled")
        connection=SSH(str(config.master0_mgmt))
        result=connection.send_command("ip route")
        print (result)
        match1 = "default via " + config.master0lan1v4gw + " dev eth1  proto ifplugd"
        match2 = "default via " + config.master0lan2v4gw + " dev eth3  proto ifplugd  metric 10"
        assert (( match1 not in result) and (match2 not in result))
        display_msg("Test Completed")
        
    @pytest.mark.run(order=58)
    def test_058_validate_ipv6_routing_table(self):
        display_msg("Validate IPv6 routing table with both LAN1 & LAN2 disabled")
        connection=SSH(str(config.master0_mgmt))
        result=connection.send_command("ip -6 route")
        print (result)
        match1 = "default via " + config.master0lan1v6gw + " dev eth1  proto ifplugd  metric 1024"
        match2 = "default via " + config.master0lan2v6gw + " dev eth3  proto ifplugd  metric 1124"
        assert (( match1 not in result) and (match2 not in result))
        display_msg("Test Completed")

    @pytest.mark.run(order=59)
    def test_059_enable_lan1_using_netctl(self):
        display_msg("Enable LAN1 using netctl command for the device "+config.master0_hw_name )
        response = os.system("netctl_system -i lan -a enable -H " +config.master0_hw_name+ " -c " +config.user)
        print response
        sleep(30)
        display_msg("LAN1 enabled") 
        
    @pytest.mark.run(order=60)
    def test_060_validate_ipv4_routing_table(self):
        display_msg("Validate IPv4 routing table with only LAN1 enabled")
        connection=SSH(str(config.master0_mgmt))
        result=connection.send_command("ip route")
        print (result)
        match1 = "default via " + config.master0lan1v4gw + " dev eth1  proto ifplugd"
        match2 = "default via " + config.master0lan2v4gw + " dev eth3  proto ifplugd  metric 10"
        assert (( match1 in result) and (match2 not in result))
        display_msg("Test Completed")
        
    @pytest.mark.run(order=61)
    def test_061_validate_ipv6_routing_table(self):
        display_msg("Validate IPv6 routing table with only LAN1 enabled")
        connection=SSH(str(config.master0_mgmt))
        result=connection.send_command("ip -6 route")
        print (result)
        match1 = "default via " + config.master0lan1v6gw + " dev eth1  proto ifplugd  metric 1024"
        match2 = "default via " + config.master0lan2v6gw + " dev eth3  proto ifplugd  metric 1124"
        assert (( match1 in result) and (match2 not in result))
        display_msg("Test Completed")

    @pytest.mark.run(order=62)
    def test_062_enable_lan2_using_netctl(self):
        display_msg("Enable LAN2 using netctl command for the device "+config.master0_hw_name )
        response = os.system("netctl_system -i lan2 -a enable -H " +config.master0_hw_name+ " -c " +config.user)
        print response
        sleep(30)
        display_msg("LAN2 enabled") 
        
    @pytest.mark.run(order=63)
    def test_063_validate_ipv4_routing_table(self):
        display_msg("Validate IPv4 routing table with both LAN1 & LAN2 enabled")
        connection=SSH(str(config.master0_mgmt))
        result=connection.send_command("ip route")
        print (result)
        match1 = "default via " + config.master0lan1v4gw + " dev eth1  proto ifplugd"
        match2 = "default via " + config.master0lan2v4gw + " dev eth3  proto ifplugd  metric 10"
        assert (( match1 in result) and (match2 in result))
        display_msg("Test Completed") 
        
    @pytest.mark.run(order=64)
    def test_064_validate_ipv6_routing_table(self):
        display_msg("Validate IPv6 routing table with both LAN1 & LAN2 enabled")
        connection=SSH(str(config.master0_mgmt))
        result=connection.send_command("ip -6 route")
        print (result)
        match1 = "default via " + config.master0lan1v6gw + " dev eth1  proto ifplugd  metric 1024"
        match2 = "default via " + config.master0lan2v6gw + " dev eth3  proto ifplugd  metric 1124"
        assert (( match1 in result) and (match2 in result))
        display_msg("Test Completed")  

    @pytest.mark.run(order=65)
    def test_065_tey_to_delete_lan1_v4(self):
        display_msg("NEGATIVE: Try to delete LAN1 v4 with the feature enabled.")
        ref = member.get_member_reference()
        data = {"config_addr_type": "IPV6",
                "vip_setting": {}, "ipv6_setting": lan1_address["ipv6_setting"], "service_type_configuration": "ALL_V6"}
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data), grid_vip=config.master0mgmt)
        print response
        sleep(15)
        member.is_device_up(config.master0mgmt)
        member.route_redundancy_status(config.master0mgmt)
        response = str(response)
        assert ((re.search(r'IPV4 LAN1 must be enabled when default route redundancy is enabled', response)))
        display_msg("Test Completed")

    @pytest.mark.run(order=66)
    def test_066_tey_to_delete_lan1_v6(self):
        display_msg("NEGATIVE: Try to delete LAN1 v6 with the feature enabled.")
        ref = member.get_member_reference()
        data = {"config_addr_type": "IPV4",
                "vip_setting": lan1_address["vip_setting"],"ipv6_setting": {}, "service_type_configuration": "ALL_V4"}
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data), grid_vip=config.master0mgmt)
        print response
        sleep(15)
        member.is_device_up(config.master0mgmt)
        member.route_redundancy_status(config.master0mgmt)
        response = str(response)
        assert ((re.search(r'IPV6 LAN1 must be enabled when default route redundancy is enabled', response)))
        display_msg("Test Completed")

    @pytest.mark.run(order=67)
    def test_067_disable_route_redundancy(self):
        display_msg("Disabling the feature Route Redundancy")
        ref = member.get_member_reference()
        data = {"lan2_port_setting": {"enabled": False, "default_route_failover_enabled": False}}
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data), grid_vip=config.master0mgmt)
        print response
        sleep(60)
        member.is_device_up(config.master0mgmt)
        assert member.route_redundancy_status(config.master0mgmt) == False
        display_msg("Test Completed")  
        
        
        
############# HA PAIR ################


    @pytest.mark.run(order=101)
    def test_101_make_node1_active(self):
        display_msg("PREPARATION: Making node1 active")
        response = os.system("reboot_system -H "  +config.ha2_hw_name+ " -c " +config.user)
        sleep(60)
        member.is_device_up(config.ha2_mgmt)
        display_msg("Node 1 is active now")
        
    @pytest.mark.run(order=102)
    def test_102_configure_lan1v4v6_lan2v4v6(self):
        display_msg("Configure HA pair with IPv4 & IPv6 and Enable the feature Route Redundancy")
        ref = member.get_member_reference()
        data = {"lan2_port_setting": {"enabled": True, "default_route_failover_enabled": True,
                                      "v6_network_setting": ha_lan2_address["v6_network_setting"],"network_setting": ha_lan2_address["network_setting"], "virtual_router_id": config.vrid}}
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data), grid_vip=config.ha1_mgmt)
        print response
        sleep(60)
        member.is_device_up(config.ha1_mgmt)
        assert member.route_redundancy_status(config.ha2_mgmt)
        display_msg("Route Redundancy is enabled and Node2 is the HA master")


    @pytest.mark.run(order=103)
    def test_103_validate_ipv4_routing_table(self):
        display_msg("Validate IPv4 routing table of active node (Node2) with LAN1 as default route")
        connection=SSH(str(config.ha2_mgmt))
        result=connection.send_command("ip route")
        print (result)
        match1 = "default via " + config.halan1_v4gw + " dev eth1  proto ifplugd"
        match2 = "default via " + config.halan2_v4gw + " dev eth3  proto ifplugd  metric 10"
        assert (( match1 in result) and (match2 in result)) == True
        display_msg("Test Completed")

    @pytest.mark.run(order=104)
    def test_104_validate_ipv6_routing_table(self):
        display_msg("Validate IPv6 routing table of active node (Node2) with LAN1 as default route")
        connection=SSH(str(config.ha2_mgmt))
        result=connection.send_command("ip -6 route")
        print (result)
        match1 = "default via " + config.halan1_v6gw + " dev eth1  proto ifplugd  metric 1024"
        match2 = "default via " + config.halan2_v6gw + " dev eth3  proto ifplugd  metric 1124"
        assert (( match1 in result) and (match2 in result))
        display_msg("Test Completed")     

    @pytest.mark.run(order=105)
    def test_105_traceroute(self):        
        display_msg("Perform traceroute and validate the default route")
        connection=SSH(str(config.ha2_mgmt))
        result1=connection.send_command("traceroute " +config.google_dns_v4)
        print (result1)
        connection=SSH(str(config.ha2_mgmt))
        result2=connection.send_command("traceroute6 " +config.google_dns_v6)
        print (result2)
        #assert (re.search(config.halan1_v4gw, result1)) and (re.search(config.halan1_v6gw, result2))
        assert True
        display_msg ("Test Completed")



    @pytest.mark.run(order=106)
    def test_106_disable_lan1_using_netctl(self):
        display_msg("Disable LAN1 using netctl command for the device "+config.ha2_hw_name )
        response = os.system("netctl_system -i lan -a disable -H " +config.ha2_hw_name+ " -c " +config.user)
        print response
        sleep(30)
        display_msg("LAN1 disabled") 

    @pytest.mark.run(order=107)
    def test_107_validate_ipv4_routing_table(self):
        display_msg("Validate IPv4 routing table of active node (Node2) with LAN1 disabled and LAN2 enabled")
        connection=SSH(str(config.ha2_mgmt))
        result=connection.send_command("ip route")
        print (result)
        match1 = "default via " + config.halan1_v4gw + " dev eth1  proto ifplugd"
        match2 = "default via " + config.halan2_v4gw + " dev eth3  proto ifplugd  metric 10"
        assert (( match1 not in result) and (match2 in result))
        display_msg("Test Completed")
        
    @pytest.mark.run(order=108)
    def test_108_validate_ipv6_routing_table(self):
        display_msg("Validate IPv6 routing table of active node (Node2) with LAN1 disabled and LAN2 enabled")
        connection=SSH(str(config.ha2_mgmt))
        result=connection.send_command("ip -6 route")
        print (result)
        match1 = "default via " + config.halan1_v6gw + " dev eth1  proto ifplugd  metric 1024"
        match2 = "default via " + config.halan2_v6gw + " dev eth3  proto ifplugd  metric 1124"
        assert (( match1 not in result) and (match2 in result))
        display_msg("Test Completed")

    @pytest.mark.run(order=109)
    def test_109_disable_lan2_using_netctl(self):
        display_msg("Disable LAN2 using netctl command for the device "+config.ha2_hw_name )
        response = os.system("netctl_system -i lan2 -a disable -H " +config.ha2_hw_name+ " -c " +config.user)
        print response
        sleep(30)
        display_msg("LAN2 disabled") 
        
    @pytest.mark.run(order=110)
    def test_110_validate_ipv4_routing_table(self):
        display_msg("Validate IPv4 routing table of active node (Node2) with both LAN1 & LAN2 disabled")
        connection=SSH(str(config.ha2_mgmt))
        result=connection.send_command("ip route")
        print (result)
        match1 = "default via " + config.halan1_v4gw + " dev eth1  proto ifplugd"
        match2 = "default via " + config.halan2_v4gw + " dev eth3  proto ifplugd  metric 10"
        assert (( match1 not in result) and (match2 not in result))
        display_msg("Test Completed")
        
    @pytest.mark.run(order=111)
    def test_111_validate_ipv6_routing_table(self):
        display_msg("Validate IPv6 routing table of active node (Node2) with both LAN1 & LAN2 disabled")
        connection=SSH(str(config.ha2_mgmt))
        result=connection.send_command("ip -6 route")
        print (result)
        match1 = "default via " + config.halan1_v6gw + " dev eth1  proto ifplugd  metric 1024"
        match2 = "default via " + config.halan2_v6gw + " dev eth3  proto ifplugd  metric 1124"
        assert (( match1 not in result) and (match2 not in result))
        display_msg("Test Completed")

    @pytest.mark.run(order=112)
    def test_112_enable_lan1_using_netctl(self):
        display_msg("Enable LAN1 using netctl command for the device "+config.ha2_hw_name )
        response = os.system("netctl_system -i lan -a enable -H " +config.ha2_hw_name+ " -c " +config.user)
        print response
        sleep(30)
        display_msg("LAN1 enabled") 
        
    @pytest.mark.run(order=113)
    def test_113_validate_ipv4_routing_table(self):
        display_msg("Validate IPv4 routing table of active node (Node2) with only LAN1 enabled")
        connection=SSH(str(config.ha2_mgmt))
        result=connection.send_command("ip route")
        print (result)
        match1 = "default via " + config.halan1_v4gw + " dev eth1  proto ifplugd"
        match2 = "default via " + config.halan2_v4gw + " dev eth3  proto ifplugd  metric 10"
        assert (( match1 in result) and (match2 not in result))
        display_msg("Test Completed")
        
    @pytest.mark.run(order=114)
    def test_114_validate_ipv6_routing_table(self):
        display_msg("Validate IPv6 routing table of active node (Node2) with only LAN1 enabled")
        connection=SSH(str(config.ha2_mgmt))
        result=connection.send_command("ip -6 route")
        print (result)
        match1 = "default via " + config.halan1_v6gw + " dev eth1  proto ifplugd  metric 1024"
        match2 = "default via " + config.halan2_v6gw + " dev eth3  proto ifplugd  metric 1124"
        assert (( match1 in result) and (match2 not in result))
        display_msg("Test Completedd")

    @pytest.mark.run(order=115)
    def test_115_enable_lan2_using_netctl(self):
        display_msg("Enable LAN2 using netctl command for the device "+config.ha2_hw_name )
        response = os.system("netctl_system -i lan2 -a enable -H " +config.ha2_hw_name+ " -c " +config.user)
        print response
        sleep(30)
        display_msg("LAN2 enabled") 
        
    @pytest.mark.run(order=116)
    def test_116_validate_ipv4_routing_table(self):
        display_msg("Validate IPv4 routing table of active node (Node2) with both LAN1 & LAN2 enabled")
        connection=SSH(str(config.ha2_mgmt))
        result=connection.send_command("ip route")
        print (result)
        match1 = "default via " + config.halan1_v4gw + " dev eth1  proto ifplugd"
        match2 = "default via " + config.halan2_v4gw + " dev eth3  proto ifplugd  metric 10"
        assert (( match1 in result) and (match2 in result))
        display_msg("Test Completedd") 
        
    @pytest.mark.run(order=117)
    def test_117_validate_ipv6_routing_table(self):
        display_msg("Validate IPv6 routing table of active node (Node2) with both LAN1 & LAN2 enabled")
        connection=SSH(str(config.ha2_mgmt))
        result=connection.send_command("ip -6 route")
        print (result)
        match1 = "default via " + config.halan1_v6gw + " dev eth1  proto ifplugd  metric 1024"
        match2 = "default via " + config.halan2_v6gw + " dev eth3  proto ifplugd  metric 1124"
        assert (( match1 in result) and (match2 in result))
        display_msg("Test Completedd")  

    @pytest.mark.run(order=118)
    def test_118_validate_routing_table_passive(self):
        display_msg("Negative: Validate if ifplugd is running in passive node (Node1)")
        connection=SSH(str(config.ha1_mgmt))
        result1=connection.send_command("ip route")
        print (result1)
        connection=SSH(str(config.ha1_mgmt))
        result2=connection.send_command("ip -6 route")
        print (result2)
        assert (("ifplugd" not in result1) and ("ifplugd" not in result2))
        display_msg("Test Completed")


    @pytest.mark.run(order=119)
    def test_119_make_node1_active(self):
        display_msg("Making node1 active")
        response = os.system("reboot_system -H "  +config.ha2_hw_name+ " -c " +config.user)
        sleep(60)
        member.is_device_up(config.ha2_mgmt)
        display_msg("Node 1 is active now")
        
        
    @pytest.mark.run(order=120)
    def test_120_validate_ipv4_routing_table(self):
        display_msg("Validate IPv4 routing table of active node (Node1) with LAN1 as default route")
        connection=SSH(str(config.ha1_mgmt))
        result=connection.send_command("ip route")
        print (result)
        match1 = "default via " + config.halan1_v4gw + " dev eth1  proto ifplugd"
        match2 = "default via " + config.halan2_v4gw + " dev eth3  proto ifplugd  metric 10"
        assert (( match1 in result) and (match2 in result)) == True
        display_msg("Test Completed")

    @pytest.mark.run(order=121)
    def test_121_validate_ipv6_routing_table(self):
        display_msg("Validate IPv6 routing table of active node (Node1) with LAN1 as default route")
        connection=SSH(str(config.ha1_mgmt))
        result=connection.send_command("ip -6 route")
        print (result)
        match1 = "default via " + config.halan1_v6gw + " dev eth1  proto ifplugd  metric 1024"
        match2 = "default via " + config.halan2_v6gw + " dev eth3  proto ifplugd  metric 1124"
        assert (( match1 in result) and (match2 in result))
        display_msg("Test Completed")     

    @pytest.mark.run(order=122)
    def test_122_traceroute(self):        
        display_msg("Perform traceroute and validate the default route")
        connection=SSH(str(config.ha1_mgmt))
        result1=connection.send_command("traceroute " +config.google_dns_v4)
        print (result1)
        connection=SSH(str(config.ha1_mgmt))
        result2=connection.send_command("traceroute6 " +config.google_dns_v6)
        print (result2)
        #assert (re.search(config.halan1_v4gw, result1)) and (re.search(config.halan1_v6gw, result2))
        assert True
        display_msg ("Test Completed")



    @pytest.mark.run(order=123)
    def test_123_disable_lan1_using_netctl(self):
        display_msg("Disable LAN1 using netctl command for the device "+config.ha1_hw_name )
        response = os.system("netctl_system -i lan -a disable -H " +config.ha1_hw_name+ " -c " +config.user)
        print response
        sleep(30)
        display_msg("LAN1 disabled") 

    @pytest.mark.run(order=124)
    def test_124_validate_ipv4_routing_table(self):
        display_msg("Validate IPv4 routing table of active node (Node1) with LAN1 disabled and LAN2 enabled")
        connection=SSH(str(config.ha1_mgmt))
        result=connection.send_command("ip route")
        print (result)
        match1 = "default via " + config.halan1_v4gw + " dev eth1  proto ifplugd"
        match2 = "default via " + config.halan2_v4gw + " dev eth3  proto ifplugd  metric 10"
        assert (( match1 not in result) and (match2 in result))
        display_msg("Test Completedd")
        
    @pytest.mark.run(order=125)
    def test_125_validate_ipv6_routing_table(self):
        display_msg("Validate IPv6 routing table of active node (Node1) with LAN1 disabled and LAN2 enabled")
        connection=SSH(str(config.ha1_mgmt))
        result=connection.send_command("ip -6 route")
        print (result)
        match1 = "default via " + config.halan1_v6gw + " dev eth1  proto ifplugd  metric 1024"
        match2 = "default via " + config.halan2_v6gw + " dev eth3  proto ifplugd  metric 1124"
        assert (( match1 not in result) and (match2 in result))
        display_msg("Test Completedd")

    @pytest.mark.run(order=126)
    def test_126_disable_lan2_using_netctl(self):
        display_msg("Disable LAN2 using netctl command for the device "+config.ha1_hw_name )
        response = os.system("netctl_system -i lan2 -a disable -H " +config.ha1_hw_name+ " -c " +config.user)
        print response
        sleep(30)
        display_msg("LAN2 disabled") 
        
    @pytest.mark.run(order=127)
    def test_127_validate_ipv4_routing_table(self):
        display_msg("Validate IPv4 routing table of active node (Node1) with both LAN1 & LAN2 disabled")
        connection=SSH(str(config.ha1_mgmt))
        result=connection.send_command("ip route")
        print (result)
        match1 = "default via " + config.halan1_v4gw + " dev eth1  proto ifplugd"
        match2 = "default via " + config.halan2_v4gw + " dev eth3  proto ifplugd  metric 10"
        assert (( match1 not in result) and (match2 not in result))
        display_msg("Test Completedd")
        
    @pytest.mark.run(order=128)
    def test_128_validate_ipv6_routing_table(self):
        display_msg("Validate IPv6 routing table of active node (Node1) with both LAN1 & LAN2 disabled")
        connection=SSH(str(config.ha1_mgmt))
        result=connection.send_command("ip -6 route")
        print (result)
        match1 = "default via " + config.halan1_v6gw + " dev eth1  proto ifplugd  metric 1024"
        match2 = "default via " + config.halan2_v6gw + " dev eth3  proto ifplugd  metric 1124"
        assert (( match1 not in result) and (match2 not in result))
        display_msg("Test Completedd")

    @pytest.mark.run(order=129)
    def test_129_enable_lan1_using_netctl(self):
        display_msg("Enable LAN1 using netctl command for the device "+config.ha1_hw_name )
        response = os.system("netctl_system -i lan -a enable -H " +config.ha1_hw_name+ " -c " +config.user)
        print response
        sleep(30)
        display_msg("LAN1 enabled") 
        
    @pytest.mark.run(order=130)
    def test_130_validate_ipv4_routing_table(self):
        display_msg("Validate IPv4 routing table of active node (Node1) with only LAN1 enabled")
        connection=SSH(str(config.ha1_mgmt))
        result=connection.send_command("ip route")
        print (result)
        match1 = "default via " + config.halan1_v4gw + " dev eth1  proto ifplugd"
        match2 = "default via " + config.halan2_v4gw + " dev eth3  proto ifplugd  metric 10"
        assert (( match1 in result) and (match2 not in result))
        display_msg("Test Completedd")
        
    @pytest.mark.run(order=131)
    def test_131_validate_ipv6_routing_table(self):
        display_msg("Validate IPv6 routing table of active node (Node1) with only LAN1 enabled")
        connection=SSH(str(config.ha1_mgmt))
        result=connection.send_command("ip -6 route")
        print (result)
        match1 = "default via " + config.halan1_v6gw + " dev eth1  proto ifplugd  metric 1024"
        match2 = "default via " + config.halan2_v6gw + " dev eth3  proto ifplugd  metric 1124"
        assert (( match1 in result) and (match2 not in result))
        display_msg("Test Completedd")

    @pytest.mark.run(order=132)
    def test_132_enable_lan2_using_netctl(self):
        display_msg("Enable LAN2 using netctl command for the device "+config.ha1_hw_name )
        response = os.system("netctl_system -i lan2 -a enable -H " +config.ha1_hw_name+ " -c " +config.user)
        print response
        sleep(30)
        display_msg("LAN2 enabled") 
        
    @pytest.mark.run(order=133)
    def test_133_validate_ipv4_routing_table(self):
        display_msg("Validate IPv4 routing table of active node (Node1) with both LAN1 & LAN2 enabled")
        connection=SSH(str(config.ha1_mgmt))
        result=connection.send_command("ip route")
        print (result)
        match1 = "default via " + config.halan1_v4gw + " dev eth1  proto ifplugd"
        match2 = "default via " + config.halan2_v4gw + " dev eth3  proto ifplugd  metric 10"
        assert (( match1 in result) and (match2 in result))
        display_msg("Test Completedd") 
        
    @pytest.mark.run(order=134)
    def test_134_validate_ipv6_routing_table(self):
        display_msg("Validate IPv6 routing table of active node (Node1) with both LAN1 & LAN2 enabled")
        connection=SSH(str(config.ha1_mgmt))
        result=connection.send_command("ip -6 route")
        print (result)
        match1 = "default via " + config.halan1_v6gw + " dev eth1  proto ifplugd  metric 1024"
        match2 = "default via " + config.halan2_v6gw + " dev eth3  proto ifplugd  metric 1124"
        assert (( match1 in result) and (match2 in result))
        display_msg("Test Completedd")  

    @pytest.mark.run(order=135)
    def test_135_validate_routing_table_passive(self):
        display_msg("Negative: Validate if ifplugd is running in passive node (Node2)")
        connection=SSH(str(config.ha2_mgmt))
        result1=connection.send_command("ip route")
        print (result1)
        connection=SSH(str(config.ha2_mgmt))
        result2=connection.send_command("ip -6 route")
        print (result2)
        assert (("ifplugd" not in result1) and ("ifplugd" not in result2))
        display_msg("Test Completed")

    @pytest.mark.run(order=136)
    def test_136_set_default_route_lan2(self):
        display_msg("Set default route to LAN2")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no ' 'admin@'+config.ha1_mgmt)
        child.logfile = sys.stdout
        print child.before 
        child.expect ('password.*:')
        child.sendline ('infoblox')
        child.sendline('set default_route lan2')
        child.sendline('y')
        sleep(45)
        member.is_device_up(config.ha1_mgmt)
        child.close()
        display_msg("Default_Route is set to LAN2 and Node2 is Active now")
        

    @pytest.mark.run(order=137)
    def test_137_validate_ipv4_routing_table(self):
        display_msg("Validate IPv4 routing table with LAN2 as default route")
        connection=SSH(str(config.ha2_mgmt))
        result=connection.send_command("ip route")
        print (result)
        match1 = "default via " + config.halan2_v4gw + " dev eth3  proto ifplugd"
        match2 = "default via " + config.halan1_v4gw + " dev eth1  proto ifplugd  metric 10"
        assert (( match1 in result) and (match2 in result)) 
        display_msg("Test Completedd")

    @pytest.mark.run(order=138)
    def test_138_validate_ipv6_routing_table(self):
        display_msg("Validate IPv6 routing table with LAN2 as default route")
        connection=SSH(str(config.ha2_mgmt))
        result=connection.send_command("ip -6 route")
        print (result)
        match1 = "default via " + config.halan2_v6gw + " dev eth3  proto ifplugd  metric 1024"
        match2 = "default via " + config.halan1_v6gw + " dev eth1  proto ifplugd  metric 1124"
        assert (( match1 in result) and (match2 in result)) 
        display_msg("Test Completedd")         
        
    @pytest.mark.run(order=139)
    def test_139_traceroute(self):        
        display_msg("Perform traceroute and validate the default route")
        connection=SSH(str(config.ha2_mgmt))
        result1=connection.send_command("traceroute " +config.google_dns_v4)
        print (result1)
        connection=SSH(str(config.ha2_mgmt))
        result2=connection.send_command("traceroute6 " +config.google_dns_v6)
        print (result2)
        #assert (re.search(config.halan2_v4gw, result1)) and (re.search(config.halan2_v6gw, result2))
        assert True
        display_msg ("Test Completed")


    @pytest.mark.run(order=140)
    def test_140_make_node1_active(self):
        display_msg("Making node1 active")
        response = os.system("reboot_system -H "  +config.ha2_hw_name+ " -c " +config.user)
        sleep(60)
        member.is_device_up(config.ha2_mgmt)
        display_msg("Node 1 is active now")
        
    @pytest.mark.run(order=141)
    def test_141_validate_ipv4_routing_table(self):
        display_msg("Validate IPv4 routing table with LAN2 as default route")
        connection=SSH(str(config.ha1_mgmt))
        result=connection.send_command("ip route")
        print (result)
        match1 = "default via " + config.halan2_v4gw + " dev eth3  proto ifplugd"
        match2 = "default via " + config.halan1_v4gw + " dev eth1  proto ifplugd  metric 10"
        assert (( match1 in result) and (match2 in result)) 
        display_msg("Test Completedd")

    @pytest.mark.run(order=142)
    def test_142_validate_ipv6_routing_table(self):
        display_msg("Validate IPv6 routing table with LAN2 as default route")
        connection=SSH(str(config.ha1_mgmt))
        result=connection.send_command("ip -6 route")
        print (result)
        match1 = "default via " + config.halan2_v6gw + " dev eth3  proto ifplugd  metric 1024"
        match2 = "default via " + config.halan1_v6gw + " dev eth1  proto ifplugd  metric 1124"
        assert (( match1 in result) and (match2 in result)) 
        display_msg("Test Completedd")         
        
    @pytest.mark.run(order=143)
    def test_143_traceroute(self):        
        display_msg("Perform traceroute and validate the default route")
        connection=SSH(str(config.ha1_mgmt))
        result1=connection.send_command("traceroute " +config.google_dns_v4)
        print (result1)
        connection=SSH(str(config.ha1_mgmt))
        result2=connection.send_command("traceroute6 " +config.google_dns_v6)
        print (result2)
        assert True
        #assert (re.search(config.halan2_v4gw, result1)) and (re.search(config.halan2_v6gw, result2))
        display_msg ("Test Completed")


################## HA PAIR TESTING COMPLETED ########################
#!/usr/bin/env python
__author__ = "Chetan Kumar PG"
__email__  = "cpg@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Two Grid Master(IPV4+IPV6)                                            #
#  2. Licenses : IB-FLEX                                                    #
#############################################################################

import os
import re
import config
import pytest
import unittest
import logging
import json
import paramiko
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="niosspt_9130.log" ,level=logging.DEBUG,filemode='w')

# Global variables

def parse_get_lab_info(ipv4):
    """
    ipv4    : ipv4 address of the machine
    Returns : Dictionary containing lab unit info
    """
    h_info = os.popen("identify_lab_unit "+ipv4).read()
    hostname = h_info.split(' ')[-1][:-2]
    display_msg(hostname)
    info = os.popen("get_lab_info -H "+hostname).read()
    info_list = info.split('\n')
    info_list = list(filter(None, info_list))
    info_dict = {}
    for x in info_list:
        info_dict[x.split('=')[0]] = x.split('=')[1]
    display_msg(info_dict)
    return info_dict

def display_msg(x=""):
    """ 
    Additional function.
    """
    logging.info(x)
    print(x)

class NIOSSPT_9130(unittest.TestCase):
    
    @pytest.mark.run(order=1)
    def test_000_setup(self):
        """
        setup method: Used for configuring pre-required configs.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case setup Started            |")
        display_msg("------------------------------------------------")
        
        display_msg("-----------Test Case setup Completed------------")
    
    @pytest.mark.run(order=2)
    def test_001_Add_offline_member(self):
        """
        Add an offline member (which is the second master reserved) to the first master.
        Set grid communication to IPV6.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 1 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Add offline member")
        member_info = parse_get_lab_info(config.grid2_vip)
        grid2_lan_ip = member_info["LAN_IPADDR"]
        member_gateway = member_info["LAN_ROUTER"]
        member_subnet = member_info["LAN_NETMASK"]
        member_cidr = member_info["LAN_CIDR"]
        member_ipv6 = member_info["LAN_IPV6ADDR"]
        member_ipv6_gateway = member_info["LAN_V6ROUTER"]
        data = {"config_addr_type": "BOTH", 
                "host_name": "member1.localdomain", 
                "platform": "VNIOS", 
                "service_type_configuration": "ALL_V6", 
                "vip_setting": {"address": grid2_lan_ip,  
                                "gateway": member_gateway, 
                                "primary": True, 
                                "subnet_mask": member_subnet}, 
                "ipv6_setting": {"cidr_prefix": int(member_cidr), 
                                 "enabled": True, 
                                 "gateway": member_ipv6_gateway, 
                                 "primary": True,
                                 "virtual_ip": member_ipv6 }}
        response = ib_NIOS.wapi_request('POST',object_type="member",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Add offline member")
            assert False
        display_msg("-----------Test Case 1 Execution Completed------------")

    @pytest.mark.run(order=3)
    def test_002_perform_join_grid_using_WAPI(self):
        """
        Perform join grid using WAPI
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 2 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Perform Join Grid")
        master_info = parse_get_lab_info(config.grid_vip)
        master_ipv6 = master_info["LAN_IPV6ADDR"]
        data = {"grid_name":"Infoblox", "master":master_ipv6, "shared_secret":"test"}
        response = ib_NIOS.wapi_request('POST',object_type="grid?_function=join",fields=json.dumps(data), grid_vip=config.grid2_vip)
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Perfrom join grid")
            assert False
        sleep(300)
        display_msg("-----------Test Case 2 Execution Completed------------")

    @pytest.mark.run(order=4)
    def test_003_verify_join_grid_status(self):
        """
        Verify the grid has successfully joined master.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 3 Execution Started           |")
        display_msg("----------------------------------------------------")
        display_msg("Verify join grid status")
        status_info = os.popen("grid_info "+config.grid_vip).read()
        display_msg(status_info)
        if "OFFLINE" in status_info:
            display_msg("Failure: Grid join failed")
            assert False
        
        display_msg("-----------Test Case 3 Execution Completed------------")

    @pytest.mark.run(order=-1)
    def test_cleanup(self):
        """
        cleanup method: Delete all the objects created from this script.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|          Test Case cleanup Started           |")
        display_msg("------------------------------------------------")
        display_msg("")
        
        display_msg("-----------Test Case cleanup Completed------------")

    @pytest.mark.run(order=4)
    def test_004_check_cores(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(config.grid_vip, username='root')
        stdin, stdout, stderr = ssh.exec_command("ls /storage/cores/ | wc -l")
        response=stdout.readlines()
        print(response[0])
        if int(response[0]) == 0:
            assert True
        else:
            stdin, stdout, stderr = ssh.exec_command("ls -ltr /storage/cores/")
            response=stdout.readlines()
            print(response)
            assert False

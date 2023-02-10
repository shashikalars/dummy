#!/usr/bin/env python
__author__ = "Shivasai Bandaru"
__email__  = "sbandaru@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master + Grid Member                                                                 #
#  2. Licenses : DNS, DHCP, Grid                                                       #
########################################################################################

import os
import re
import pexpect
import paramiko
import config
import pytest
import unittest
import logging
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="niosspt_10848.log" ,level=logging.DEBUG,filemode='w')



def display_msg(x=""):
    """ 
    Additional function.
    """
    logging.info(x)
    print(x)

class NIOSSPT_11064(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_setup(self):
        """
        Enable snmp configurations, traps and queries
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|			 Test Case setup Started			|")
        display_msg("------------------------------------------------")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting')
        print(get_ref)
        get_ref = json.loads(get_ref)[0]['_ref']
        data={"snmp_setting":{"queries_enable":True,"queries_community_string":"public","trap_receivers":[{"address": config.client_ip}],"traps_community_string":"public","traps_enable":True}}
        response = ib_NIOS.wapi_request('PUT', ref=get_ref, fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            assert False
        else:
            assert True


    @pytest.mark.run(order=2)
    def test_001_enable_all_snmp_notifications(self):
        """
        Enable all snmp notifications
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|			Test Case 1 Execution Started			|")
        display_msg("----------------------------------------------------")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=trap_notifications')
        print(get_ref)
        get_ref = json.loads(get_ref)[0]['_ref']
        data={"trap_notifications": [{"enable_trap": True,"trap_type": "AnalyticsRPZ"}, {"enable_trap": True,"trap_type": "AutomatedTrafficCapture"}, {"enable_trap": True,"trap_type": "BFD"}, {"enable_trap": True,"trap_type": "BGP"}, {"enable_trap": True,"trap_type": "Backup"}, {"enable_trap": True,"trap_type": "Bloxtools"}, {"enable_trap": True,"trap_type": "CPU"}, {"enable_trap": True,"trap_type": "CaptivePortal"}, {"enable_trap": True,"trap_type": "CiscoISEServer"}, {"enable_trap": True,"trap_type": "Clear"}, {"enable_trap": True,"trap_type": "CloudAPI"}, {"enable_trap": True,"trap_type": "Cluster"}, {"enable_trap": True,"trap_type": "Controld"}, {"enable_trap": True,"trap_type": "DHCP"}, {"enable_trap": True,"trap_type": "DNS"}, {"enable_trap": True,"trap_type": "DNSAttack"}, {"enable_trap": True,"trap_type": "DNSIntegrityCheck"}, {"enable_trap": True,"trap_type": "DNSIntegrityCheckConnection"}, {"enable_trap": True,"trap_type": "Database"}, {"enable_trap": True,"trap_type": "DisconnectedGrid"}, {"enable_trap": True,"trap_type": "Discovery"}, {"enable_trap": True,"trap_type": "DiscoveryConflict"}, {"enable_trap": True,"trap_type": "DiscoveryUnmanaged"}, {"enable_trap": True,"trap_type": "Disk"}, {"enable_trap": True,"trap_type": "DuplicateIP"}, {"enable_trap": True,"trap_type": "ENAT"}, {"enable_trap": True,"trap_type": "FDUsage"}, {"enable_trap": True,"trap_type": "FTP"}, {"enable_trap": True,"trap_type": "Fan"}, {"enable_trap": True,"trap_type": "HA"}, {"enable_trap": True,"trap_type": "HSM"}, {"enable_trap": True,"trap_type": "HTTP"}, {"enable_trap": True,"trap_type": "IFMAP"}, {"enable_trap": True,"trap_type": "IMC"}, {"enable_trap": True,"trap_type": "IPAMUtilization"}, {"enable_trap": True,"trap_type": "IPMIDevice"}, {"enable_trap": True,"trap_type": "LCD"}, {"enable_trap": True,"trap_type": "LDAPServers"}, {"enable_trap": True,"trap_type": "License"}, {"enable_trap": True,"trap_type": "Login"}, {"enable_trap": True,"trap_type": "MGM"}, {"enable_trap": True,"trap_type": "MSServer"}, {"enable_trap": True,"trap_type": "Memory"}, {"enable_trap": True,"trap_type": "NTP"}, {"enable_trap": True,"trap_type": "Network"}, {"enable_trap": True,"trap_type": "OCSPResponders"}, {"enable_trap": True,"trap_type": "OSPF"}, {"enable_trap": True,"trap_type": "OSPF6"}, {"enable_trap": True,"trap_type": "Outbound"}, {"enable_trap": True,"trap_type": "PowerSupply"}, {"enable_trap": True,"trap_type": "RAID"}, {"enable_trap": True,"trap_type": "RIRSWIP"}, {"enable_trap": True,"trap_type": "RPZHitRate"}, {"enable_trap": True,"trap_type": "RecursiveClients"}, {"enable_trap": True,"trap_type": "Reporting"}, {"enable_trap": True,"trap_type": "RootFS"}, {"enable_trap": True,"trap_type": "SNMP"}, {"enable_trap": True,"trap_type": "SSH"}, {"enable_trap": True,"trap_type": "SerialConsole"}, {"enable_trap": True,"trap_type": "SwapUsage"}, {"enable_trap": True,"trap_type": "Syslog"}, {"enable_trap": True,"trap_type": "System"}, {"enable_trap": True,"trap_type": "TFTP"}, {"enable_trap": True,"trap_type": "Taxii"}, {"enable_trap": True,"trap_type": "ThreatAnalytics"}, {"enable_trap": True,"trap_type": "ThreatProtection"}] }
        response = ib_NIOS.wapi_request('PUT', ref=get_ref, fields=json.dumps(data))
        print(response)
        grid =	ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        sleep(20)
        if type(response) == tuple:
            assert False
        else:
            assert True
            display_msg("-----------Test Case 1 Execution Completed------------")
    
    @pytest.mark.run(order=3)
    def test_002_start_ntp_service_and_add_ntpserver(self):
        """
        Start Ntp service and add external ntp servers
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|		Test Case 2 Execution Started	    	|")
        display_msg("----------------------------------------------------")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=ntp_setting')
        get_ref = json.loads(get_ref)[0]['_ref']
        data={"ntp_setting":{"enable_ntp": True,"ntp_servers": [{"address": "10.36.198.7","burst": True,"preferred": True}]}}
        response = ib_NIOS.wapi_request('PUT', ref=get_ref, fields=json.dumps(data))
        print(response)
        get_ref = ib_NIOS.wapi_request('GET', object_type="member?_return_fields=ntp_setting", grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            data={"ntp_setting":{"enable_ntp": True,"ntp_servers": [{"address": "10.36.198.7","burst": True,"preferred": True}]}}
            response = ib_NIOS.wapi_request('PUT',ref=ref['_ref'],fields=json.dumps(data), grid_vip=config.grid_vip)
            display_msg("-----------Test Case 2 Execution Completed------------")
            assert True

    @pytest.mark.run(order=4)
    def test_003_collect_ntp_trap_receivers_data_and_promote_meber_master(self):
        """
        Start collecting trap receivers data and perform GMC pormotion
        """
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.client_ip)
        try:
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('#')
            child.sendline('snmptrapd udp6:162,udp:162 -f -C -c /etc/snmp/snmptrapd.conf -Le &> trap_data.txt \n')
            get_ref = ib_NIOS.wapi_request('GET', object_type="member?_return_fields=master_candidate")
            print(get_ref)
            for ref in json.loads(get_ref):
                if config.grid_member1_fqdn in ref['_ref']:
                    data = {"master_candidate": True}
                    response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
                    print(response)
                    assert True

        except Exception as e:
            print(e)
            assert False

    @pytest.mark.run(order=5)
    def test_004_promote_member_to_master(self):
        display_msg("----------------------------------------------------")
        display_msg("|	         Test Case 4 Execution Started	        |")
        display_msg("----------------------------------------------------")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        try:
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set promote_master')
            child.expect('y or n')
            child.sendline('y')
            child.expect('Default: 30s')
            child.sendline('\n')
            child.expect('y or n')
            child.sendline('y\n')
            child.expect('y or n')
            child.sendline('y\n')
            child.expect('y or n')
            child.sendline('y\n')
            sleep(120)
            assert True

        except Exception as e:
            print(e)
            assert False

    @pytest.mark.run(order=6)
    def test_005_check_traps_in_receiver(self):
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 5 Execution Started            |")
        display_msg("----------------------------------------------------")
        child = pexpect.spawn('ssh root@'+config.client_ip)
        try:
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('#')
            count = os.system(""" cat /root/trap_data.txt |grep "The NTP service is out of synchronization" | wc -l """)
            print(count)
            count1 =  os.system(""" cat /root/trap_data.txt |grep "The NTP service resumed synchronization" | wc -l """)
            print(count1)
            if count > 0 and count1 > 0 :
                assert True
            else:
                assert False
        except Exception as e:
            print(e)
            assert False

    @pytest.mark.run(order=7)
    def test_clean_up(self):
        """
        reverting changes, making GMC master as member and cleaning ntp changes
        """
        get_ref = ib_NIOS.wapi_request('GET', object_type="member?_return_fields=ntp_setting", grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            data= {"ntp_setting":{"enable_external_ntp_servers": False,"enable_ntp": False,"exclude_grid_master_ntp_server": False}}
            response = ib_NIOS.wapi_request('PUT',ref=ref['_ref'],fields=json.dumps(data), grid_vip=config.grid_vip)
            print(response)
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_master_vip)
        try:
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set promote_master')
            child.expect('y or n')
            child.sendline('y')
            child.expect('Default: 30s')
            child.sendline('\n')
            child.expect('y or n')
            child.sendline('y\n')
            child.expect('y or n')
            child.sendline('y\n')
            child.expect('y or n')
            child.sendline('y\n')
            sleep(120)
            assert True
        except Exception as e:
            print(e)
            assert False


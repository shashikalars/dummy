#!/usr/bin/env python
__author__ = "Chetan Kumar PG"
__email__  = "cpg@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Grid Master                                                           #
#  2. Licenses : DNS, Grid, NIOS, DTC                                       #
#  3. Enable DNS services                                                   #
#############################################################################

import os
import re
import sys
import config
import pytest
import unittest
import logging
import json
import shlex
import pexpect
import paramiko
from time import sleep
from scp import SCPClient
from subprocess import Popen, PIPE
import ib_utils.ib_NIOS as ib_NIOS
from ib_utils.log_capture import log_action as log
from ib_utils.log_validation import log_validation as logv
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="niosspt_12323.log" ,level=logging.DEBUG,filemode='w')

def display_msg(x=""):
    """ 
    Additional function.
    """
    logging.info(x)
    print(x)

def is_grid_alive(grid=config.grid_vip):
    """
    Checks whether the grid is reachable
    """
    ping = os.popen("ping -c 2 "+grid).read()
    display_msg(ping)
    if "0 received" in ping:
        return False
    else:
        return True

def remove_known_hosts_file():
    """
    Removes known_hosts file.
    This is to avoid host key expiration issues.
    """
    cmd = "rm -rf /home/"+config.client_username+"/.ssh/known_hosts"
    ret_code = os.system(cmd)
    if ret_code == 0:
        display_msg("Cleared known hosts file")
    else:
        display_msg("Couldnt clear known hosts file")

def restart_services(grid=config.grid_vip, service=['ALL']):
    """
    Restart Services
    """
    display_msg()
    display_msg("+----------------------------------------------+")
    display_msg("|           Restart Services                   |")
    display_msg("+----------------------------------------------+")
    get_ref =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=grid)
    ref = json.loads(get_ref)[0]['_ref']
    data= {"mode" : "SIMULTANEOUS","restart_option":"FORCE_RESTART","services": service}
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices", fields=json.dumps(data),grid_vip=grid)
    if restart != '{}':
        display_msg(restart)
        display_msg("FAIL: Restart services failed, Please debug above error message for root cause")
        assert False
    sleep(20)

class NIOSSPT_12323(unittest.TestCase):
    
    @pytest.mark.run(order=1)
    def test_001_Enable_logging_for_DTC_load_balancing_and_DTC_health_monitor(self):
        """
        Enable logging for DTC load balancing and DTC health monitor.
        """
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Test Case 1 Started            |")
        display_msg("+------------------------------------------+")
        
        display_msg("Enable logging for DTC load balancing and DTC health monitor")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns')
        grid_dns_ref = json.loads(get_ref)[0]['_ref']
        display_msg(get_ref)
        
        data = {"logging_categories":{"log_dtc_gslb": True, "log_dtc_health": True}}
        response = ib_NIOS.wapi_request('PUT', ref=grid_dns_ref, fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("FAIL: Failed to enable logging for DTC load balancing and DTC health monitor")
            assert False
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns?_return_fields=logging_categories')
        display_msg(get_ref)
        if 'log_dtc_health": true' in get_ref and 'log_dtc_gslb": true' in get_ref:
            display_msg("PASS: Successfully enabled logging for DTC load balancing and DTC health monitor")
        else:
            display_msg("FAIL: Failed to enable logging for DTC load balancing and DTC health monitor")
            assert False

        display_msg("---------Test Case 1 Execution Completed----------")

    @pytest.mark.run(order=2)
    def test_002_add_auth_zone(self):
        """
        Add an authoritative zone.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 2 Started                |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Add an authoritative zone niosspt_12323.com")
        data = {"fqdn": "niosspt_12323.com",
                "view":"default",
                "grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("FAIL: Create Authorative FMZ")
            assert False
        display_msg("PASS: Authoritative zone niosspt_12323.com is added")
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth?fqdn=niosspt_12323.com")
        display_msg(get_ref)
        if 'niosspt_12323.com' in get_ref:
            display_msg("PASS: Zone niosspt_12323.com found")
        else:
            display_msg("FAIL: Zone niosspt_12323.com not found")
            assert False
        
        display_msg("---------Test Case 2 Execution Completed----------")

    @pytest.mark.run(order=3)
    def test_003_create_DTC_servers(self):
        """
        Create DTC servers.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 3 Started                |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Create DTC servers")
        data = {"name": "server1", "host":"8.8.8.8"}
        response = ib_NIOS.wapi_request('POST',object_type="dtc:server",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("FAIL: Creation of DTC server failed")
            assert False
        display_msg("PASS: Successfully created DTC server")
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref = ib_NIOS.wapi_request('GET',object_type="dtc:server")
        display_msg(get_ref)
        if 'server1' in get_ref:
            display_msg("PASS: DTC server 'server1' found")
        else:
            display_msg("FAIL: DTC server 'server1' not found")
            assert False
        
        display_msg("---------Test Case 3 Execution Completed----------")

    @pytest.mark.run(order=4)
    def test_004_create_pool_with_icmp_health_monitor(self):
        """
        Create Pool with ICPM Health monitor.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 4 Started                |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Create Pool with ICPM Health monitor")
        get_ref = ib_NIOS.wapi_request('GET',object_type="dtc:server?name=server1")
        display_msg(get_ref)
        data = {"lb_preferred_method": "ROUND_ROBIN",
                "name": "pool1",
                "servers": [{"ratio": 1,
                             "server": json.loads(get_ref)[0]['_ref']}],
                             "monitors": ["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"]}
        response = ib_NIOS.wapi_request('POST',object_type="dtc:pool",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("FAIL: Creation of Pool failed")
            assert False
        display_msg("PASS: Successfully created Pool")
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref = ib_NIOS.wapi_request('GET',object_type="dtc:pool")
        display_msg(get_ref)
        if 'pool1' in get_ref:
            display_msg("PASS: DTC Pool 'pool1' found")
        else:
            display_msg("FAIL: DTC Pool 'pool1' not found")
            assert False
        
        display_msg("---------Test Case 4 Execution Completed----------")

    @pytest.mark.run(order=5)
    def test_005_create_lbdn(self):
        """
        Create LBDN.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 5 Started                |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Create LBDN")
        get_ref = ib_NIOS.wapi_request('GET',object_type="dtc:pool?name=pool1")
        display_msg(get_ref)
        get_ref2 = ib_NIOS.wapi_request('GET',object_type="zone_auth?fqdn=niosspt_12323.com")
        display_msg(get_ref2)
        data = {"lb_method": "ROUND_ROBIN",
                "name": "lbdn1",
                "pools": [{"pool": json.loads(get_ref)[0]['_ref'],"ratio": 1}],
                "auth_zones": [json.loads(get_ref2)[0]['_ref']],
                "patterns": ["niosspt_12323.com"]}
        response = ib_NIOS.wapi_request('POST',object_type="dtc:lbdn",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("FAIL: Creation of LBDN failed")
            assert False
        display_msg("PASS: Successfully created LBDN")
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref = ib_NIOS.wapi_request('GET',object_type="dtc:lbdn")
        display_msg(get_ref)
        if 'lbdn1' in get_ref:
            display_msg("PASS: DTC Pool 'lbdn1' found")
        else:
            display_msg("FAIL: DTC Pool 'lbdn1' not found")
            assert False
        
        display_msg("---------Test Case 5 Execution Completed----------")

    @pytest.mark.run(order=6)
    def test_006_Set_logging_facility_to_DAEMON(self):
        """
        Set logging facility DAEMON.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 6 Started                |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Set logging facility to DAEMON")
        get_ref = ib_NIOS.wapi_request("GET", object_type="grid:dns?_return_fields=syslog_facility")
        display_msg(get_ref)
        
        response = ib_NIOS.wapi_request("PUT", ref=json.loads(get_ref)[0]["_ref"], fields=json.dumps({"syslog_facility":"DAEMON"}))
        display_msg(response)
        if type(response) == tuple:
            display_msg(response)
            display_msg("FAIL: Failed to set logging facility")
            assert False
        display_msg("PASS: Successfully set logging facility")
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        dns_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns?_return_fields=syslog_facility')
        display_msg(dns_ref)
        if 'DAEMON' in dns_ref:
            display_msg("PASS: Successfully validated syslog facility")
        else:
            display_msg("FAIL: Failed to validate syslog facility")
            assert False
        
        display_msg("---------Test Case 6 Execution Completed---------")

    @pytest.mark.run(order=6)
    def test_006_Start_syslog_capture(self):
        """
        Start capturing syslog.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 6 Started                |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Start capturing syslog")
        log("start","/var/log/syslog",config.grid_vip)
        
        display_msg("---------Test Case 6 Execution Completed----------")

    @pytest.mark.run(order=7)
    def test_007_Start_DNS_service(self):
        """
        Start DNS service on all members if not already started.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 7 Started                |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Check if DNS service is already enabled")
        dns_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=enable_dns')
        display_msg(dns_ref)
        if 'false' in dns_ref:
            display_msg("Enable DNS service")
            get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns')
            display_msg(get_ref)
            response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps({"enable_dns":True}))
            if type(response) == tuple:
                display_msg(response)
                display_msg("FAIL: Enable DNS Service")
                assert False
            display_msg("PASS: DNS Service enabled")
            sleep(60)
        
            # Validation
            display_msg()
            display_msg("+------------------------------------------+")
            display_msg("|           Validation                     |")
            display_msg("+------------------------------------------+")
            dns_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=enable_dns')
            display_msg(dns_ref)
            if 'true' in dns_ref:
                display_msg("PASS: DNS service vaidation")
            else:
                display_msg("FAIL: DNS service vaidation")
                assert False
        else:
            restart_services()
            sleep(60)
        
        display_msg("---------Test Case 7 Execution Completed----------")
    
    @pytest.mark.run(order=8)
    def test_008_Stop_syslog_capture(self):
        """
        Stop capturing syslog.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 8 Started                |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Stop capturing syslog")
        log("stop","/var/log/syslog",config.grid_vip)
        
        display_msg("---------Test Case 8 Execution Completed----------")

    @pytest.mark.run(order=9)
    def test_009_Validate_syslog(self):
        """
        Validate captured syslog.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 9 Started                |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Validate captured syslog")
        display_msg(os.popen("cat /tmp/"+config.grid_vip+"_var_log_messages.log").read())
        logv(".*user.*idns_healthd.*","/var/log/syslog",config.grid_vip)
        
        display_msg("---------Test Case 9 Execution Completed----------")

    @pytest.mark.run(order=10)
    def test_010_Modify_logging_facility_to_LOCAL6(self):
        """
        Change logging facility from DAEMON to LOCAL6.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 10 Started               |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Change logging facility from DAEMON to LOCAL6")
        get_ref = ib_NIOS.wapi_request("GET", object_type="grid:dns?_return_fields=syslog_facility")
        display_msg(get_ref)
        
        response = ib_NIOS.wapi_request("PUT", ref=json.loads(get_ref)[0]["_ref"], fields=json.dumps({"syslog_facility":"LOCAL6"}))
        display_msg(response)
        if type(response) == tuple:
            display_msg(response)
            display_msg("FAIL: Failed to modify logging facility")
            assert False
        display_msg("PASS: Successfully modified logging facility")
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        dns_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns?_return_fields=syslog_facility')
        display_msg(dns_ref)
        if 'LOCAL6' in dns_ref:
            display_msg("PASS: Successfully validated syslog facility")
        else:
            display_msg("FAIL: Failed to validate syslog facility")
            assert False
        
        display_msg("---------Test Case 10 Execution Completed--------")

    @pytest.mark.run(order=11)
    def test_011_Start_syslog_capture(self):
        """
        Start capturing syslog.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 11 Started               |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Start capturing syslog")
        log("start","/var/log/syslog",config.grid_vip)
        restart_services()
        sleep(60)
        
        display_msg("---------Test Case 11 Execution Completed---------")

    @pytest.mark.run(order=12)
    def test_012_Stop_syslog_capture(self):
        """
        Stop capturing syslog.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 12 Started               |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Stop capturing syslog")
        log("stop","/var/log/syslog",config.grid_vip)
        
        display_msg("---------Test Case 12 Execution Completed---------")

    @pytest.mark.run(order=13)
    def test_013_Validate_syslog(self):
        """
        Validate captured syslog.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 13 Started               |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Validate captured syslog")
        display_msg(os.popen("cat /tmp/"+config.grid_vip+"_var_log_messages.log").read())
        logv(".*mail.*idns_healthd.*","/var/log/syslog",config.grid_vip)
        
        display_msg("---------Test Case 13 Execution Completed---------")

    @pytest.mark.run(order=14)
    def test_014_Modify_logging_facility_to_DAEMON(self):
        """
        Change logging facility from LOCAL6 to LOCAL0.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 14 Started               |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Change logging facility from LOCAL6 to LOCAL0")
        get_ref = ib_NIOS.wapi_request("GET", object_type="grid:dns?_return_fields=syslog_facility")
        display_msg(get_ref)
        
        response = ib_NIOS.wapi_request("PUT", ref=json.loads(get_ref)[0]["_ref"], fields=json.dumps({"syslog_facility":"LOCAL0"}))
        display_msg(response)
        if type(response) == tuple:
            display_msg(response)
            display_msg("FAIL: Failed to modify logging facility")
            assert False
        display_msg("PASS: Successfully modified logging facility")
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        dns_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns?_return_fields=syslog_facility')
        display_msg(dns_ref)
        if 'LOCAL0' in dns_ref:
            display_msg("PASS: Successfully validated syslog facility")
        else:
            display_msg("FAIL: Failed to validate syslog facility")
            assert False
        
        display_msg("---------Test Case 14 Execution Completed--------")

    @pytest.mark.run(order=15)
    def test_015_Start_syslog_capture(self):
        """
        Start capturing syslog.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 15 Started               |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Start capturing syslog")
        log("start","/var/log/syslog",config.grid_vip)
        restart_services()
        sleep(60)
        
        display_msg("---------Test Case 15 Execution Completed---------")

    @pytest.mark.run(order=16)
    def test_016_Stop_syslog_capture(self):
        """
        Stop capturing syslog.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 16 Started               |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Stop capturing syslog")
        log("stop","/var/log/syslog",config.grid_vip)
        
        display_msg("---------Test Case 16 Execution Completed---------")

    @pytest.mark.run(order=17)
    def test_017_Validate_syslog(self):
        """
        Validate captured syslog.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 17 Started               |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Validate captured syslog")
        display_msg(os.popen("cat /tmp/"+config.grid_vip+"_var_log_messages.log").read())
        logv(".*mail.*idns_healthd.*","/var/log/syslog",config.grid_vip)
        
        display_msg("---------Test Case 17 Execution Completed---------")
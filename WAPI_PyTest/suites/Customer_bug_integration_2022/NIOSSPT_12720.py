#!/usr/bin/env python
__author__ = "Chetan Kumar PG"
__email__  = "cpg@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Grid Master                                                           #
#  2. Licenses : DNS, Grid, NIOS, RPZ                                       #
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
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="niosspt_12720.log" ,level=logging.DEBUG,filemode='w')

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

class NIOSSPT_12720(unittest.TestCase):
    
    @pytest.mark.run(order=1)
    def test_001_Start_DNS_service(self):
        """
        Start DNS service on all members.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 1 Started                |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Enable DNS service")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns')
        display_msg(get_ref)
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps({"enable_dns":True}))
        if type(response) == tuple:
            display_msg(response)
            display_msg("FAIL: Enable DNS Service")
            assert False
        display_msg("PASS: DNS Service enabled")
        sleep(30)
        
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
        
        display_msg("---------Test Case 1 Execution Completed----------")

    @pytest.mark.run(order=2)
    def test_002_Add_DNS_forwarder_and_enable_recursion(self):
        """
        Add DNS forwarder : 10.39.16.160
        Enable recursive queries.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 2 Started                |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Add DNS forwarder and enable recursive queries")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns')
        display_msg(get_ref)
        
        data = {"forwarders":["10.39.16.160"], "allow_recursive_query":True}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data))
        if type(response) == tuple:
            display_msg(response)
            display_msg("FAIL: Grid DNS properties not updated")
            assert False
        display_msg("PASS: Grid DNS Properties updated")
        restart_services()
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        dns_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns?_return_fields=forwarders,allow_recursive_query')
        display_msg(dns_ref)
        if 'true' in dns_ref and '10.39.16.160' in dns_ref:
            display_msg("PASS: Grid DNS Properties validation")
        else:
            display_msg("FAIL: Grid DNS Properties validation failed")
            assert False
        
        display_msg("---------Test Case 2 Execution Completed----------")

    @pytest.mark.run(order=3)
    def test_003_add_response_policy_zone_blacklist(self):
        """
        Add a Response Policy Zone 'blacklist'.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 3 Started                |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Add a Response Policy Zone 'blacklist'")
        data = {"fqdn": "blacklist",
                "grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_rp",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("FAIL: Create Response Policy Zone")
            assert False
        display_msg("PASS: Response Policy Zone blacklist is added")
        
        restart_services()
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref = ib_NIOS.wapi_request('GET',object_type="zone_rp?fqdn=blacklist")
        display_msg(get_ref)
        if 'blacklist' in get_ref:
            display_msg("PASS: Response Policy Zone blacklist found")
        else:
            display_msg("FAIL: Response Policy Zone blacklist not found")
            assert False
        
        display_msg("---------Test Case 3 Execution Completed----------")

    @pytest.mark.run(order=4)
    def test_004_add_block_domain_name_rule_under_blacklist_rpz(self):
        """
        Add Block Domain Name (No Data) Rule under blacklist RPZ.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 4 Started                |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Add Block Domain Name (No Data) Rule under blacklist RPZ")
        data = {"canonical": "*", 
                "name": "www.google.com.blacklist", 
                "rp_zone": "blacklist"}
        response = ib_NIOS.wapi_request('POST',object_type="record:rpz:cname",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("FAIL: Add Block Domain Name (No Data) Rule")
            assert False
        display_msg("PASS: Block Domain Name (No Data) Rule is added")
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref = ib_NIOS.wapi_request('GET',object_type="record:rpz:cname?name=www.google.com.blacklist")
        display_msg(get_ref)
        if 'www.google.com.blacklist' in get_ref:
            display_msg("PASS: Block Domain Name (No Data) Rule found")
        else:
            display_msg("FAIL: Block Domain Name (No Data) Rule not found")
            assert False
        
        display_msg("Sleep for 60 seconds for rpz reload")
        sleep(60)
        
        display_msg("---------Test Case 4 Execution Completed----------")

    @pytest.mark.run(order=5)
    def test_005_Validate_dig_query_output(self):
        """
        Send dig query for www.google.com and validate that ANSER SECTION is present in the output
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 5 Started                |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Send dig query for www.google.com")
        output = os.popen("dig @"+config.grid_vip+" www.google.com").read()
        display_msg(output)
        output = output.split('\n')
        answer = False
        pattern = False
        for line in output:
            if answer:
                match = re.match("blacklist.\s+\d+\s+IN\s+SOA", line)
                if match:
                    pattern = True
                    break
            if 'ADDITIONAL SECTION' in line:
                answer = True
        if not answer or not pattern:
            display_msg("Failure: Query output validation failed.")
            assert False
        display_msg("PASS: RPZ rule matched with blacklist rpz.")
        
        display_msg("---------Test Case 5 Execution Completed----------")

    @pytest.mark.run(order=6)
    def test_006_add_response_policy_zone_nxdomain(self):
        """
        Add a Response Policy Zone 'nxdomain'.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 6 Started                |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Add a Response Policy Zone 'nxdomain'")
        data = {"fqdn": "nxdomain",
                "grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_rp",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("FAIL: Create Response Policy Zone")
            assert False
        display_msg("PASS: Response Policy Zone nxdomain is added")
        
        restart_services()
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref = ib_NIOS.wapi_request('GET',object_type="zone_rp?fqdn=nxdomain")
        display_msg(get_ref)
        if 'nxdomain' in get_ref:
            display_msg("PASS: Response Policy Zone nxdomain found")
        else:
            display_msg("FAIL: Response Policy Zone nxdomain not found")
            assert False
        
        display_msg("---------Test Case 6 Execution Completed----------")

    @pytest.mark.run(order=7)
    def test_007_add_block_domain_name_rule_under_nxdomain_rpz(self):
        """
        Add Block Domain Name (No Such Domain) Rule under nxdomain RPZ.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 7 Started                |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Add Block Domain Name (No Such Domain) Rule under nxdomain RPZ")
        data = {"canonical": "", 
                "name": "www.google.com.nxdomain", 
                "rp_zone": "nxdomain"}
        response = ib_NIOS.wapi_request('POST',object_type="record:rpz:cname",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("FAIL: Add Block Domain Name (No Such Domain) Rule")
            assert False
        display_msg("PASS: Block Domain Name (No Such Domain) Rule is added")
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref = ib_NIOS.wapi_request('GET',object_type="record:rpz:cname?name=www.google.com.nxdomain")
        display_msg(get_ref)
        if 'www.google.com.nxdomain' in get_ref:
            display_msg("PASS: Block Domain Name (No Such Domain) Rule found")
        else:
            display_msg("FAIL: Block Domain Name (No Such Domain) Rule not found")
            assert False
        
        display_msg("Sleep for 60 seconds for rpz reload")
        sleep(60)
        
        display_msg("---------Test Case 7 Execution Completed----------")

    @pytest.mark.run(order=8)
    def test_008_Validate_dig_query_output(self):
        """
        Send dig query for www.google.com and validate that ANSER SECTION is present in the output
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 8 Started                |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Send dig query for www.google.com")
        output = os.popen("dig @"+config.grid_vip+" www.google.com").read()
        display_msg(output)
        output = output.split('\n')
        answer = False
        pattern = False
        for line in output:
            if answer:
                match = re.match("nxdomain.\s+\d+\s+IN\s+SOA", line)
                if match:
                    pattern = True
                    break
            if 'ADDITIONAL SECTION' in line:
                answer = True
        if not answer or not pattern:
            display_msg("Failure: Query output validation failed")
            assert False
        display_msg("PASS: RPZ rule matched with nxdomain rpz.")
        
        display_msg("---------Test Case 8 Execution Completed----------")

    @pytest.mark.run(order=9)
    def test_009_add_response_policy_zone_whitelist(self):
        """
        Add a Response Policy Zone 'whitelist'.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 9 Started                |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Add a Response Policy Zone 'whitelist'")
        data = {"fqdn": "whitelist",
                "grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_rp",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("FAIL: Create Response Policy Zone")
            assert False
        display_msg("PASS: Response Policy Zone whitelist is added")
        
        restart_services()
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref = ib_NIOS.wapi_request('GET',object_type="zone_rp?fqdn=whitelist")
        display_msg(get_ref)
        if 'whitelist' in get_ref:
            display_msg("PASS: Response Policy Zone whitelist found")
        else:
            display_msg("FAIL: Response Policy Zone whitelist not found")
            assert False
        
        display_msg("---------Test Case 9 Execution Completed----------")

    @pytest.mark.run(order=10)
    def test_010_add_passthru_domain_name_rule_under_whitelist_rpz(self):
        """
        Add passthru Domain Name Rule under whitelist RPZ.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 10 Started               |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Add passthru Domain Name Rule under whitelist RPZ")
        data = {"canonical": "www.google.com", 
                "name": "www.google.com.whitelist", 
                "rp_zone": "whitelist"}
        response = ib_NIOS.wapi_request('POST',object_type="record:rpz:cname",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("FAIL: Add passthru Domain Name Rule")
            assert False
        display_msg("PASS: passthru Domain Name Rule is added")
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref = ib_NIOS.wapi_request('GET',object_type="record:rpz:cname?name=www.google.com.whitelist")
        display_msg(get_ref)
        if 'www.google.com.whitelist' in get_ref:
            display_msg("PASS: passthru Domain Name Rule found")
        else:
            display_msg("FAIL: passthru Domain Name Rule not found")
            assert False
        
        display_msg("Sleep for 60 seconds for rpz reload")
        sleep(60)
        
        display_msg("---------Test Case 10 Execution Completed---------")

    @pytest.mark.run(order=11)
    def test_011_Validate_rpz_priority_for_all_the_zones(self):
        """
        Validate Response Policy Zones have below priority numbers:
        whitelist  - 0
        nxdomain   - 1
        blacklist  - 2
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 11 Started               |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Validate rpz priority for all the zones")
        response = ib_NIOS.wapi_request("GET", object_type="zone_rp?_return_fields=fqdn,rpz_priority")
        display_msg(response)
        if type(response) == tuple or response == '[]':
            display_msg("FAIL: Failed to fetch response policy zones")
            assert False
        rpz_zones = json.loads(response)
        for zone in rpz_zones:
            if zone['fqdn'] == 'whitelist':
                if not zone['rpz_priority'] == 0:
                    display_msg("FAIL: whitelist rp zone doesn't have priority as 0")
                    assert False
            elif zone['fqdn'] == 'nxdomain':
                if not zone['rpz_priority'] == 1:
                    display_msg("FAIL: nxdomain rp zone doesn't have priority as 1")
                    assert False
            elif zone['fqdn'] == 'blacklist':
                if not zone['rpz_priority'] == 2:
                    display_msg("FAIL: blacklist rp zone doesn't have priority as 2")
                    assert False
        
        display_msg("---------Test Case 11 Execution Completed---------")

    @pytest.mark.run(order=12)
    def test_012_Validate_dig_query_output(self):
        """
        Send dig query for www.google.com and validate that ANSER SECTION is present in the output
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 12 Started               |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Send dig query for www.google.com")
        output = os.popen("dig @"+config.grid_vip+" www.google.com").read()
        display_msg(output)
        output = output.split('\n')
        answer = False
        pattern = False
        for line in output:
            if answer:
                match = re.match("www.google.com.\s+\d+\s+IN\s+A", line)
                if match:
                    pattern = True
                    break
            if 'ANSWER SECTION' in line:
                answer = True
        if not answer or not pattern:
            display_msg("Failure: Query output validation failed")
            assert False
        display_msg("PASS: RPZ rule matched with whitelist rpz, hence the ANSWER SECTION in dig output")
        
        display_msg("---------Test Case 12 Execution Completed---------")
    
    @pytest.mark.run(order=13)
    def test_013_Delete_nxdomain_reponse_policy_zone(self):
        """
        Delete the nxdomain Response Policy Zone.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 13 Started               |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Delete the nxdomain Response Policy Zone")
        rpz_ref = ib_NIOS.wapi_request('GET',object_type="zone_rp?fqdn=nxdomain")
        display_msg(rpz_ref)
        if 'nxdomain' not in rpz_ref:
            display_msg("No RPZ zone found with name 'nxdomain'")
            assert False
        response = ib_NIOS.wapi_request('DELETE', ref=json.loads(rpz_ref)[0]['_ref'])
        restart_services()
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref = ib_NIOS.wapi_request('GET',object_type="zone_rp")
        display_msg(get_ref)
        if 'nxdomain' not in get_ref:
            display_msg("PASS: Successfully deleted nxdomain RPZ zone")
        else:
            display_msg("FAIL: Failed to delete nxdomain RPZ zone")
            assert False
        
        display_msg("---------Test Case 13 Execution Completed---------")

    @pytest.mark.run(order=14)
    def test_014_Validate_dig_query_output(self):
        """
        Send dig query for www.google.com and validate that ANSER SECTION is present in the output
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 14 Started               |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Send dig query for www.google.com")
        output = os.popen("dig @"+config.grid_vip+" www.google.com").read()
        display_msg(output)
        output = output.split('\n')
        answer = False
        pattern = False
        for line in output:
            if answer:
                match = re.match("www.google.com.\s+\d+\s+IN\s+A", line)
                if match:
                    pattern = True
                    break
            if 'ANSWER SECTION' in line:
                answer = True
        if not answer or not pattern:
            display_msg("Failure: Query output validation failed")
            assert False
        display_msg("PASS: RPZ rule matched with whitelist rpz, hence the ANSWER SECTION in dig output")
        
        display_msg("---------Test Case 14 Execution Completed---------")

    @pytest.mark.run(order=-1)
    def test_cleanup(self):
        """
        Clear all the data.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test cleanup Started               |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Delete all RPZ zones")
        rpz_ref = ib_NIOS.wapi_request('GET',object_type="zone_rp")
        display_msg(rpz_ref)
        for zone in json.loads(rpz_ref):
            response = ib_NIOS.wapi_request('DELETE', ref=zone['_ref'])
        restart_services()
        
        display_msg("Delete forwarder and disable recursive queries")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns')
        display_msg(get_ref)
        
        data = {"forwarders":[], "allow_recursive_query":False}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data))
        if type(response) == tuple:
            display_msg(response)
            display_msg("FAIL: Grid DNS properties not updated")
            assert False
        display_msg("PASS: Grid DNS Properties updated")
        restart_services()
        
        display_msg("---------Test Case cleanup Execution Completed---------")

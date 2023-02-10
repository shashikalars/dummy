#!/usr/bin/env python
__author__ = "Shivasai"
__email__  = "sbandaru@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master + Grid Member                                                        #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415), Threat Analytics, RPZ ,Echo-system  #
########################################################################################

import os
import re
import config
import pytest
import unittest
import logging
import subprocess
import json
from time import sleep
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv
import ib_utils.ib_NIOS as ib_NIOS
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="niosspt_9130.log" ,level=logging.DEBUG,filemode='w')

# Global variables
global master_ref
global member_ref
global zone_ref 
def display_msg(x=""):
    """ 
    Additional function.
    """
    logging.info(x)
    print(x)

class NIOSSPT_8982(unittest.TestCase):
    
    @pytest.mark.run(order=1)
    def test_000_setup(self):
        """
        setup method: Used for configuring pre-required configs.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case setup Started            |")
        display_msg("------------------------------------------------")
        global master_ref,member_ref
        get_ref = ib_NIOS.wapi_request('GET',object_type="member")
        display_msg(get_ref)
        ref = json.loads(get_ref)
        master_ref = ref[0]["_ref"]
        member_ref = ref[1]["_ref"]
        print(member_ref)
        pass

    @pytest.mark.run(order=2)
    def test_001_Change_member_hostname(self):
        """
        Member hostname should not allow special characters
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 1 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        print(member_ref)
        response = ib_NIOS.wapi_request('PUT',ref=member_ref,fields=json.dumps({"host_name": "member1@.in.com"}))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                if "Host name contains forbidden characters" in response[1]:
                    print("Host name contains forbidden")
                    assert True
            else:
                assert False
        print("'@' not allowing in the Host name")

        
    @pytest.mark.run(order=3)
    def test_002_Create_RPZ_Zone(self):
        """
         Configure Global forwarder,allow recursion, rpz logging
         Create RPZ zone and add the zone to add blaclisted domains in threat analytics
         
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 2 Execution Started           |")
        display_msg("----------------------------------------------------")
        global master_ref,member_ref
        display_msg("Configuring forwarder")
        response = ib_NIOS.wapi_request('GET', object_type="grid:dns")
        response=json.loads(response)
        print(response)
        dns_ref = response[0]['_ref']
        response = ib_NIOS.wapi_request('PUT',object_type=dns_ref ,fields=json.dumps({"forwarders": ["10.39.16.160"],"allow_recursive_query": True,"logging_categories":{"log_queries": True,"log_resolver": True,"log_responses": True}}))
        print(response)
        data = {"fqdn": "NIOSSPT_8982.com",
                "view":"default",
                "grid_primary": [
                    {
                        "name": config.grid_fqdn, 
                        "stealth": False
                    }
                ]
                }
        global zone
        zone = ib_NIOS.wapi_request('POST',object_type="zone_rp",fields=json.dumps(data))
        zone=json.loads(zone)
        print(zone)
        response1 = ib_NIOS.wapi_request('GET',object_type="grid:threatanalytics")
        response1=json.loads(response1)
        print(response1)
        TA = response1[0]['_ref']
        response = ib_NIOS.wapi_request('PUT',object_type=TA ,fields=json.dumps({"dns_tunnel_black_list_rpz_zones":[zone]}))
        print(response)
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                assert False
            else:
                assert True

    @pytest.mark.run(order=4)
    def test_003_Enable_Threat_Analytics_service(self):
        """
        Enable threat analytics service
        """
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatanalytics", grid_vip=config.grid_vip)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"enable_service": True}
        output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
        print(output)
        print("Successfully started threat analytics service")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(45)
        if type(output) == tuple:
            if response[0]==400 or response[0]==401:
                assert False
            else:
                assert True

    @pytest.mark.run(order=5)
    def test_004_Check_Domain(self):
        """
         Create tunneling and check if the domain is blacklisted in rpz
         
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 3 Execution Started           |")
        display_msg("----------------------------------------------------")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        record = "bugsszz.com"
        a=1
        for i in range(1,7):
            dig_cmd = 'dig @'+config.grid_vip+' '+'226L01TTL-0.'+str(a)+'.'+"bugsszz.com"+str(' IN ')+str(' TXT')
            os.system(dig_cmd)
        display_msg("check if reference  got added in rpz blacklist")
        sleep(45)
        response1 = ib_NIOS.wapi_request('GET',object_type="record:rpz:cname")
        response1=json.loads(response1)
        print(response1)
        LookFor="DNS Tunneling detected"
        sleep(15)
        log("stop","/var/log/syslog",config.grid_vip)
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        sleep(10)
        #log("stop","/var/log/syslog",config.grid_vip)
        print(logs)
        if logs == None:
            assert False

        if response1 == []:
            assert False
        else:
            for i in range (len(response1)):     
                if record in response1[i]['name']:
                    print(response1[i]['name'])
                    assert True
                    return
                else:
                    assert False
                    

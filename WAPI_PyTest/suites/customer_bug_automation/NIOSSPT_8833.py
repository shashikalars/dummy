#!/usr/bin/env python
__author__ = "Shivasai"
__email__  = "sbandaru@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master + Grid Member                                                        #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415), Echo-system  Licenses               #
########################################################################################

import os
import re
import config
import pytest
import unittest
import logging
import subprocess
import commands
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv

#import ib_utils.outbound5_dns_zone111 as import_zone
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="niosspt_9130.log" ,level=logging.DEBUG,filemode='w')

# Global variables
master_ref = None
member_ref = None
zone_ref = None
def display_msg(x=""):
    """ 
    Additional function.
    """
    logging.info(x)
    print(x)

class NIOSSPT_8833(unittest.TestCase):
    
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
        logging.info("Start DHCP Service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties")
        logging.info(get_ref)
        res = json.loads(get_ref)
        for i in res:
            logging.info("Modify a enable_dhcp")
            data = {"enable_dhcp": True}
            response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
            print response
        

        logging.info(response)
        read  = re.search(r'200',response)
        for read in  response:
            assert True
        print("Setup done")

        pass

    @pytest.mark.run(order=2)
    def test_001_Add_DHCP_ipv4_network(self):
        """
         Add '@' in the member hostname 
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 1 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        print(member_ref)
        response = ib_NIOS.wapi_request('POST',object_type="network",fields=json.dumps({"network": "20.0.0.0/8","network_view": "default"}))
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                assert False
            else:
                assert True
        print("Added 20.0.0.0/8 network in DHCP")

        
    @pytest.mark.run(order=3)
    def test_002_Upload_REST_API_Session_Template(self):
        logging.info("Upload REST API Version5 Session Template")
        dir_name="/import/qaddi/shivasai/template"
        base_filename="Version5_REST_API_Session_Template.json"
        token = common_util.generate_token_from_file(dir_name,base_filename)
        data = {"token": token,"overwrite": True}
        response = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=restapi_template_import")
        logging.info(response)
        print response
        logging.info(response)
        res = json.loads(response)
        string = {"overall_status": "SUCCESS","error_message": ""}
        if res == string:
            assert True
        else:
            assert False
        print("Test Case 2 Execution Completed")
	
    @pytest.mark.run(order=4)
    def test_003_Upload_DNS_Records_Event_Template(self):
        logging.info("Upload DNS RECORDS Version5 Event Template")
        dir_name="/import/qaddi/shivasai/template"
        base_filename="Version6_REST_EVENT_Tunnel.json"
        token = common_util.generate_token_from_file(dir_name,base_filename)
        data = {"token": token,"overwrite":True}
        response = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=restapi_template_import")
        logging.info(response)
        print response
        logging.info(response)
        res = json.loads(response)
        string = {"overall_status": "SUCCESS","error_message": ""}
        if res == string:
            assert True
        else:
            assert False
        print("Test Case 3 Execution Completed")

    @pytest.mark.run(order=5)
    def test_004_Validate_Template_Upload(self):
        logging.info("Validating template upload")
        get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rest:template")
        logging.info(get_temp)
        print get_temp
        print("Test Case 4 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=6)
    def test_005_Add_REST_API_endpoint(self):
        logging.info("Add REST API endpoint")
        data = {"name": "rest_api_endpoint1", "uri": "https://"+config.grid_master_vip,"outbound_member_type": "GM","username": "admin","password": "infoblox","wapi_user_name": "admin", "wapi_user_password": "infoblox","template_instance": {"template": "Version5_REST_API_Session_Template"},"server_cert_validation": "NO_VALIDATION","log_level": "DEBUG"}
        response = ib_NIOS.wapi_request('POST', object_type="notification:rest:endpoint", fields=json.dumps(data))
        res=json.loads(response)
        logging.info(response)
        sleep(10)
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        print("Test Case 5 Execution Completed")

    @pytest.mark.run(order=7)
    def test_006_Validating_REST_API_endpoint(self):
        logging.info("Validating REST API endpoint")
        data = {"name": "rest_api_endpoint1"}
        get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rest:endpoint")
        logging.info(get_temp)
        res=json.loads(get_temp)
        print res
        print("Test Case 6 Execution Completed")
        sleep(5)
        
    @pytest.mark.run(order=8)
    def test_007_Add_DHCP_HOST_ADDRESS_IPV4_Notification_Rule(self):
        logging.info("Adding Notification rule with zone type as Authoritative")
        object_type="notification:rest:endpoint"
        data={"name":"rest_api_endpoint1"}
        get_ref = common_util.get_object_reference(object_type,data)
        print "========================="
        print get_ref
        data = {"name": "host_notify1","notification_action": "RESTAPI_TEMPLATE_INSTANCE", "notification_target": get_ref,"template_instance": {"template": "event_tunnel_ipv4"},"event_type": "DB_CHANGE_DNS_HOST_ADDRESS_IPV4","expression_list": [{"op": "AND", "op1_type": "LIST"}, {"op": "CONTAINED_IN", "op1": "NETWORK", "op1_type": "FIELD", "op2": "20.0.0.0/8", "op2_type": "STRING"}, {"op": "ENDLIST"}]}
        response = ib_NIOS.wapi_request('POST', object_type="notification:rule", fields=json.dumps(data))
        res=json.loads(response)
        logging.info(response)
        sleep(25)
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        print("Test Case 7 Execution Completed")
        
    @pytest.mark.run(order=9)
    def test_008_create_zone(self):
        logging.info("Adding Notification rule with zone type as Authoritative")       
        
        data={"fqdn":"niosspt111_1883.com",
             "grid_primary": [{"name": config.grid_fqdn, "stealth": False}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data))
        print(response)
        logging.info(response)
        zoneref=response
        zoneref = json.loads(zoneref)
        print(zoneref)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(5)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")

        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        sleep(30)
        host_info={"name": "vj8.com","network_view": "default","configure_for_dns": False,"ipv4addrs": [{"configure_for_dhcp": False,"ipv4addr": "20.0.0.175"}]}
        host_ref=ib_NIOS.wapi_request('POST',object_type='record:host',fields=json.dumps(host_info))
        logging.info(host_ref)
        sleep(50)
        LookFor="unpack requires a string argument of length 4"
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)

        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        print(logs)
        if logs == None:
            assert False
        else:
            assert True
        print("Test Case 08 Execution Completed")
        
    @pytest.mark.run(order=10)
    def test_009_create_zone(self):
        logging.info("Adding Notification rule with zone type as Authoritative") 
        log("start","/infoblox/var/outbound/log/worker_0.log",config.grid_vip)
        sleep(10)
        host_info={"name": "vj3.com","network_view": "default","configure_for_dns": False,"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "20.0.0.74","mac": "aa:4a:bc:11:02:34"}]}
        host_ref=ib_NIOS.wapi_request('POST',object_type='record:host',fields=json.dumps(host_info))
        logging.info(host_ref)
        print (host_ref)
        sleep(30)
        log("stop","/infoblox/var/outbound/log/worker_0.log",config.grid_vip)
        LookFor="The template was executed successfully"
        log("stop","/infoblox/var/outbound/log/worker_0.log",config.grid_vip)
        logs=logv(LookFor,"/infoblox/var/outbound/log/worker_0.log",config.grid_vip)
        print(logs)
        if logs == None:
            assert False
        else:
            assert True
        print("Test Case 9 Execution Completed")

        






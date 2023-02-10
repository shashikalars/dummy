#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
# Grid Set up required:                                                     #
#  1. Grid                                                                  #
#  2. Licenses : Grid,NIOS                                                  #
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
from config import username 
   
class NIOS_81464(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_create_admin_group_with_testing_DENY(self):
       
        print("Create a non-super users testing_DENY  group")
        data={"name": "testing_DENY","comment":"group for Limited-Access User","superuser":False}
        response = ib_NIOS.wapi_request('POST',object_type="admingroup",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:
                print("Success: Create a Limited-Access users group ")
                assert True
            else:
                print("Failure: Create a Limited-Access user group")
                assert False
                

    @pytest.mark.run(order=2)
    def test_001_create_testing_DENY_non_super_user(self):
        print("Create a non super user")
        data={"admin_groups": ["testing_DENY"],"name": "testing","password":"infoblox"}
        
        response = ib_NIOS.wapi_request('POST',object_type="adminuser",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:
                print("Success: Create a Local user")
                assert True
            else:
                print("Failure: Create a Local user ")
                assert False

    @pytest.mark.run(order=3)
    def test_002_add_Deny_permission_to_the_limited_access_group(self):
        get_ref = ib_NIOS.wapi_request('GET',object_type="permission?_return_fields=resource_type")
        li=['ZONE','GRID_DNS_PROPERTIES','VIEW','SHARED_RECORD_GROUP','MEMBER','MSSERVER','KERBEROS_KEY','NETWORK_VIEW','DHCP_MAC_FILTER','TEMPLATE','IPV6_TEMPLATE','DHCP_LEASE_HISTORY','IPV6_DHCP_LEASE_HISTORY','DHCP_FINGERPRINT','GRID_FILE_DIST_PROPERTIES','SUPER_HOST','VLAN_VIEW','VLAN_RANGE','VLAN_OBJECTS','NETWORK','IPV6_NETWORK','GRID_DHCP_PROPERTIES','CA_CERTIFICATE','OCSP_SERVICE','HOST','IDNS_LBDN','IDNS_LBDN_RECORD','IDNS_POOL','IDNS_MONITOR','IDNS_SERVER','IDNS_TOPOLOGY','IDNS_CERTIFICATE','IDNS_GEO_IP','CSV_IMPORT_TASK','SAML_AUTH_SERVICE','RESPONSE_POLICY_RULE','TXT','IPV6_HOST_ADDRESS','HOST_ADDRESS','RESPONSE_POLICY_ZONE','RECLAMATION','Unknown','SRV','NAPTR','SHARED_MX','TLSA','DNS64_SYNTHESIS_GROUP','CNAME','PTR','MX','RULESET','BULKHOST','DNAME','SHARED_CNAME','SHARED_TXT','ALIAS','SHARED_SRV']

        for resource in li:
            #if 'testing_DENY' in ref['_ref']:
            data={"group": "testing_DENY","permission": "DENY","resource_type":resource}
            response = ib_NIOS.wapi_request('POST',object_type="permission",fields=json.dumps(data))
            print(response)
            if type(response) == tuple:
                if response[0]==200:
                    print(response)
                    assert True
                else:
                    assert False
        
        print("\nSucessfully added deny permission to the limited access group")


    @pytest.mark.run(order=4)
    def test_003_check_super_user_is_un_checked_and_allowed_interfaces_only_API_selected(self):
        
        print("check super user is un-checked and allowed interfaces only GUI selected")
        get_ref = ib_NIOS.wapi_request('GET',object_type="admingroup?_return_fields=access_method,superuser")
        #print(get_ref)
        for ref in json.loads(get_ref):
            if 'testing_DENY' in ref['_ref']:
                print(ref)
                print(ref['superuser'])
                if 'API' in ref['access_method'] and 'GUI' in ref['access_method'] and 'CLI' not in ref['access_method']:
                    print("Success: API is selected in access method")
                    assert True
                else:
                    assert False
                if ref['superuser']==False:
                    print("\nSuccess: un-checked superuser")
                    assert True
                else:
                    assert False

        
        
    @pytest.mark.run(order=5)
    def test_004_try_to_create_a_zone_login_as_local_user(self):
        print("Change username and password for login as local user")
        data =json.dumps({"fqdn":"test_deny.com","view":"default","grid_primary": [{"stealth": False,"name":config.grid_fqdn}]})   
        curl_cmd="curl -k -u testing:infoblox -H \"Content-Type: application/json\" -X POST https://"+config.grid_vip+"/wapi/v"+config.wapi_version+"/zone_auth -d "+"'"+data+"'"
        print(curl_cmd)

        response = os.popen(curl_cmd).read()
        print(response)

        if 'Write permission for zone' in response:
            print("Success:Write permission for zone")
            assert True
        else:
            assert False
               
    @pytest.mark.run(order=6)
    def test_005_allow_all_interfaces_and_all_show_commands(self):
        
        get_ref = ib_NIOS.wapi_request('GET',object_type="admingroup?name=testing_DENY")
        res = json.loads(get_ref)
        ref1=res[0]['_ref']
        print(ref1)
        data={"admin_show_commands":{"show_admin_group_acl":True,"show_arp":True,"show_bfd":True,"show_bgp":True,"show_capacity":True,"show_clusterd_info":True,"show_config":True,"show_cpu":True,"show_date":True,"show_debug":True,"show_delete_tasks_interval":True,"show_disk":True,"show_file":True,"show_hardware_type":True,"show_hwid":True,"show_ibtrap":True,"show_lcd":True,"show_lcd_info":True,"show_lcd_settings":True,"show_log":True,"show_logfiles":True,"show_memory":True,"show_ntp":True,"show_scheduled":True,"show_snmp":True,"show_status":True,"show_tech_support":True,"show_temperature":True,"show_thresholdtrap":True,"show_upgrade_history":True,"show_uptime":True,
"show_version":True},"access_method": ["GUI","API","CLI"]}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)

        print(response)
        if type(response) == tuple:
            if response[0]==200:
                print("Success: Enable all admin_show_commands and access_method ")
                assert True
            else:
                print("Failure: Enable all admin_show_commands and access_method ")
                assert False
  
                
    @pytest.mark.run(order=7)
    def test_006_try_to_create_a_zone_after_login_as_local_user(self):   
        
        data =json.dumps({"fqdn":"test_deny.com","view":"default","grid_primary": [{"stealth": False,"name":config.grid_fqdn}]})   
        curl_cmd="curl -k -u testing:infoblox -H \"Content-Type: application/json\" -X POST https://"+config.grid_vip+"/wapi/v"+config.wapi_version+"/zone_auth -d "+"'"+data+"'"
        print(curl_cmd)

        response = os.popen(curl_cmd).read()
        print(response)

        if 'Write permission for zone' in response:
            print("Success:Write permission for zone")
            assert True
        else:
            assert False 
                
    @pytest.mark.run(order=8)
    def test_007_create_admin_group_with_testing_RO(self):
       
        print("Create a non-super users testing_RO  group")
        data={"name": "testing_RO","comment":"group for Limited-Access User","superuser":False}
        response = ib_NIOS.wapi_request('POST',object_type="admingroup",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:
                print("Success: Create a Limited-Access users group ")
                assert True
            else:
                print("Failure: Create a Limited-Access user group")
                assert False
                

    @pytest.mark.run(order=9)
    def test_008_create_testing_DENY_non_super_user(self):
        print("Create a non super user")
        data={"admin_groups": ["testing_RO"],"name": "testing1","password":"infoblox"}
        
        response = ib_NIOS.wapi_request('POST',object_type="adminuser",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:
                print("Success: Create a Local user for RO")
                assert True
            else:
                print("Failure: Create a Local user for RO")
                assert False

    @pytest.mark.run(order=10)
    def test_009_add_READ_permission_to_the_limited_access_group(self):
        
        li=['ZONE','GRID_DNS_PROPERTIES','VIEW','SHARED_RECORD_GROUP','MEMBER','MSSERVER','KERBEROS_KEY','NETWORK_VIEW','DHCP_MAC_FILTER','TEMPLATE','IPV6_TEMPLATE','DHCP_LEASE_HISTORY','IPV6_DHCP_LEASE_HISTORY','DHCP_FINGERPRINT','GRID_FILE_DIST_PROPERTIES','SUPER_HOST','VLAN_VIEW','VLAN_RANGE','VLAN_OBJECTS','NETWORK','IPV6_NETWORK','GRID_DHCP_PROPERTIES','CA_CERTIFICATE','OCSP_SERVICE','HOST','IDNS_LBDN','IDNS_LBDN_RECORD','IDNS_POOL','IDNS_MONITOR','IDNS_SERVER','IDNS_TOPOLOGY','IDNS_CERTIFICATE','IDNS_GEO_IP','CSV_IMPORT_TASK','SAML_AUTH_SERVICE','RESPONSE_POLICY_RULE','TXT','IPV6_HOST_ADDRESS','HOST_ADDRESS','RESPONSE_POLICY_ZONE','RECLAMATION','Unknown','SRV','NAPTR','SHARED_MX','TLSA','DNS64_SYNTHESIS_GROUP','CNAME','PTR','MX','RULESET','BULKHOST','DNAME','SHARED_CNAME','SHARED_TXT','ALIAS','SHARED_SRV']
        for resource in li:
            #if 'testing_RO' in ref['_ref']:
            
            data={"group": "testing_RO","permission": "READ","resource_type":resource}
            response = ib_NIOS.wapi_request('POST',object_type="permission",fields=json.dumps(data))
            print(response)
            if type(response) == tuple:
                if response[0]==200:
                    print(response)
                    assert True
                else:
                    assert False     
        print("Sucessfully added READ permission to the limited access group")

    @pytest.mark.run(order=11)
    def test_010_check_super_user_is_un_checked_and_allowed_interfaces_only_API_selected(self):
        print("check super user is un-checked and allowed interfaces only GUI selected")
        get_ref = ib_NIOS.wapi_request('GET',object_type="admingroup?_return_fields=access_method,superuser")
        #print(get_ref)
        for ref in json.loads(get_ref):
            if 'testing_RO' in ref['_ref']:
                print(ref)
                print(ref['superuser'])
                if 'API' in ref['access_method'] and 'GUI' in ref['access_method'] and 'CLI' not in ref['access_method']:
                    print("Success: API is selected in access method")
                    assert True
                else:
                    assert False
                if ref['superuser']==False:
                    print("\nSuccess: un-checked superuser")
                    assert True
                else:
                    assert False

               
    @pytest.mark.run(order=12)
    def test_011_try_to_create_a_zone_login_as_local_user_RO(self):  
        
        print("Add the Authoritative zone test_ro.com in grid through local-user") 
        
        data =json.dumps({"fqdn":"test_ro.com","view":"default","grid_primary": [{"stealth": False,"name":config.grid_fqdn}]})   
        curl_cmd="curl -k -u testing:infoblox -H \"Content-Type: application/json\" -X POST https://"+config.grid_vip+"/wapi/v"+config.wapi_version+"/zone_auth -d "+"'"+data+"'"
        print(curl_cmd)

        response = os.popen(curl_cmd).read()
        print(response)

        if 'Write permission for zone' in response:
            print("Success:Write permission for zone")
            assert True
        else:
            assert False
        
    @pytest.mark.run(order=13)
    def test_012_allow_all_interfaces_and_all_show_commands_RO(self):
       
        get_ref = ib_NIOS.wapi_request('GET',object_type="admingroup?name=testing_RO")
        res = json.loads(get_ref)
        ref1=res[0]['_ref']
        print(ref1)
        data={"admin_show_commands":{"show_admin_group_acl":True,"show_arp":True,"show_bfd":True,"show_bgp":True,"show_capacity":True,"show_clusterd_info":True,"show_config":True,"show_cpu":True,"show_date":True,"show_debug":True,"show_delete_tasks_interval":True,"show_disk":True,"show_file":True,"show_hardware_type":True,"show_hwid":True,"show_ibtrap":True,"show_lcd":True,"show_lcd_info":True,"show_lcd_settings":True,"show_log":True,"show_logfiles":True,"show_memory":True,"show_ntp":True,"show_scheduled":True,"show_snmp":True,"show_status":True,"show_tech_support":True,"show_temperature":True,"show_thresholdtrap":True,"show_upgrade_history":True,"show_uptime":True,
"show_version":True},"access_method": ["GUI","API","CLI"]}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)

        print(response)
        if type(response) == tuple:
            if response[0]==200:
                print("Success: Enable all admin_show_commands and access_method ")
                assert True
            else:
                print("Failure: Enable all admin_show_commands and access_method ")
                assert False
  
                
    @pytest.mark.run(order=14)
    def test_013_try_to_create_a_zone_after_login_as_local_user_RO(self):   
        data =json.dumps({"fqdn":"test_ro.com","view":"default","grid_primary": [{"stealth": False,"name":config.grid_fqdn}]})   
        curl_cmd="curl -k -u testing:infoblox -H \"Content-Type: application/json\" -X POST https://"+config.grid_vip+"/wapi/v"+config.wapi_version+"/zone_auth -d "+"'"+data+"'"
        print(curl_cmd)

        response = os.popen(curl_cmd).read()
        print(response)

        if 'Write permission for zone' in response:
            print("Success:Write permission for zone")
            assert True
        else:
            assert False
        
                
                
    @pytest.mark.run(order=15)
    def test_014_cleanup(self):
        get_reff = ib_NIOS.wapi_request('GET', object_type="adminuser")
        #print(get_reff)
        for ref in json.loads(get_reff):
            if 'testing' in ref['_ref'] or 'testing1' in ref['_ref']:
                response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
                print(response)  
                if type(response) == tuple:           
                    if response[0]==200:     
                        assert True
                    else:
                        assert False
                           
        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup", grid_vip=config.grid_vip)

        for ref in json.loads(get_ref):
            if 'testing_DENY' in ref["_ref"] or 'testing_RO' in ref["_ref"]:
                response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
                print(response)  
                if type(response) == tuple:           
                    if response[0]==200:     
                        assert True
                    else:
                        assert False
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)

        for ref in json.loads(get_ref):
            if 'test_deny.com' in ref["_ref"] or 'test_ro.com' in ref["_ref"]:
                response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
                print(response)  
                if type(response) == tuple:           
                    if response[0]==200:     
                        assert True
                    else:
                        assert False
                        
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(5)
       






########################################################################
#                                                                      #
# Copyright (c) Infoblox Inc., 2019                                    #
#                                                                      #
########################################################################
#
# File: NIOSSPT-9150-DNS64_RPZ_NODATA_not_working.py
#
# Description:
#     This Script is written to verfiy customer BUG : NIOSSPT-9150-DNS64 RPZ NODATA not working.
#     Adding a zone under DNS, and adding RPZ Zone with No-domain rule,when customer tries to ping the record after enabling DNS64 in 
#     grid properties,dig was failing but CEF logs were captured under var/log/messages.To Verify this situation after FIX,this script is used.
# Input Options:
#	  before running this script utilities which are imported must be installed and common utilities must be copied.
#__author__ = "Rajeev Patil"
#__email__  = "rpatil@infoblox.com"
#
######################################################################################################################
#  Grid Set up required:                                                                                             #
#  1. Grid Master                                                                    #
#  2. Licenses : DNS, DHCP, Grid, RPZ,NIOS (IB-V1415)						#
######################################################################################################################
#	  			
#  Output:
#    0: Test success
#    1: Test failed
#
########################################################################


import re
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
import requests
import time
import pexpect
import getpass
import sys
import config
from ib_utils.dig_all_records import dig
#from nsupdate_util import nsupdate_add
#import log_validation as logv
#from ib_utils.log_capture import log_action as log
#from ib_utils.log_validation import log_validation as logv
import pdb
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv


auth_zone={"fqdn": "source.com","allow_query": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}],"allow_update": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}]}
rpz_data={"fqdn": "local.com","grid_primary":[{"name": config.grid_fqdn,"stealth":False}]}

def restart_services():
    """
    Restart Services
    """
    print("Restart services")
    grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
    ref = json.loads(grid)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices", fields=json.dumps(data),grid_vip=config.grid_vip)
    sleep(10)


class Network(unittest.TestCase):
     @pytest.mark.run(order=1)
     def test_01_add_auth_zone(self):
          print("Creating auth Zone to add different records for bug verification purpose")
          #pdb.set_trace()
          response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(auth_zone))
          if (response[0]==400):
               print ("Zone already exists,try with other data[Don't get confused with Pytest Passed status]")
          else:
               print ("Zone added and response looks like : ",response)
               res = json.loads(response)
               time.sleep(30)
               print ("reference of zone added ",res)
               data = {"grid_primary": [{"name": config.grid_fqdn,"stealth":False}]}
               print ("Trying to Associate ZONE with Primary GRID")
               response = ib_NIOS.wapi_request('PUT',ref=res,fields=json.dumps(data))
               response=json.loads(response)
               print ("Restart services")
               print ("Associated Zone with Primary GRID and reference looks like :",response)
               grid =  ib_NIOS.wapi_request('GET', object_type="grid")
               ref = json.loads(grid)[0]['_ref']
               publish={"member_order":"SIMULTANEOUSLY"}
               request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
               time.sleep(1)
               request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
               restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
               time.sleep(1)
               print ("Restarting grid here now ")
               logging.info("Fetching reference values for Zones")
               get_reference = ib_NIOS.wapi_request('GET',object_type="zone_auth?fqdn=source.com")
               get_reference = json.loads(get_reference)
               if (get_reference[0]['_ref']==response):
                    print ("Test Case 1 Execution Completed")
                    assert True
               else:
                    assert False
                    print ("Test Case 1 Execution Failed")
                    
          

     @pytest.mark.run(order=2)
     def test_02_start_dns(self):
          member_ref=ib_NIOS.wapi_request('GET',object_type="member:dns")
          print (member_ref)
          member_ref=json.loads(member_ref)
          print (member_ref)
          print ("__________________________________")
          dns_ref=member_ref[0]['_ref']
          condition=ib_NIOS.wapi_request('GET',object_type=dns_ref+"?_return_fields=enable_dns")
          print (condition)
          data={"enable_dns": True}
          enable_dns_ref = ib_NIOS.wapi_request('PUT', ref=dns_ref, fields=json.dumps(data))
          print (enable_dns_ref)
          print ("*************************************")
          com=json.loads(enable_dns_ref)+"?_return_fields=enable_dns"
          print (com)
          new_member_ref=ib_NIOS.wapi_request('GET',object_type=com)
          print (new_member_ref)
          print ("####################################")
          print (condition)
          print ("++++++++++++++++++++++++++++++++")
          new_member_ref=json.loads(new_member_ref)
          print (new_member_ref)
          if (data['enable_dns']==new_member_ref['enable_dns']):
               assert True
               print ("DNS service enabled")
               print ("Test case 2 passed")
          else:
               assert False
               print ("Test case 2 failed")
               print ("Not enabled")

     @pytest.mark.run(order=3)
     def test_03_add_a_record(self):
         print ("Creating A Record for added Zone")
         data={"name": "a."+auth_zone['fqdn'],"ipv4addr":"12.12.12.12","comment":"Adding arec","view":"default"}
         response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data))
	 print(response)
         if (response[0]!=400):
             print ("Added A Record with Reference value :",json.loads(response))
             time.sleep(1)
             read  = re.search(r'201',response)
             for read in response:
                 assert True
             print("A Record is created Successfully")
         else:
             assert False
         


     @pytest.mark.run(order=4)
     def test_04_enabling_DNS_recursion(self):
         print ("Enabling DNS on both ipv4, ipv6")
         data={"use_lan_ipv6_port": True,"use_lan_port": True}
         member_ref=ib_NIOS.wapi_request('GET',object_type="member:dns")
         member_reference=json.loads(member_ref)[0]['_ref']
         response = ib_NIOS.wapi_request('PUT', ref=member_reference,fields=json.dumps(data))
         time.sleep(30)
         publish={"member_order":"SIMULTANEOUSLY"}
         request_publish = ib_NIOS.wapi_request('POST', object_type = member_reference + "?_function=publish_changes",fields=json.dumps(publish))
         time.sleep(10)
         request_restart = ib_NIOS.wapi_request('POST', object_type = member_reference + "?_function=requestrestartservicestatus")
         restart = ib_NIOS.wapi_request('POST', object_type = member_reference + "?_function=restartservices")
         time.sleep(10)
         new_data_ref=ib_NIOS.wapi_request('GET',member_reference+"?_return_fields=use_lan_ipv6_port,use_lan_port")
         new_data_ref=json.loads(new_data_ref)
         new_data_ref.pop('_ref')
         print ("Updated data after PUT command ",new_data_ref)
         if (new_data_ref==data):
             assert True
             print ("DNS Interfaces on IPV4 and IPV6 enabled")
             print ("Test case 4 passed")
         else:
             assert False 
             print ("DNS Interfaces on IPV4 and IPV6 Failed to enable check Manually for further instructions")
             print ("Test case 4 Failed")
             
         
     @pytest.mark.run(order=5)
     def test_05_enabling_DNS_recursion(self):
         print ("Enabling DNS on both Recursion and RPZ-logging")
         grid_ref=ib_NIOS.wapi_request('GET',object_type="grid:dns")
	 #pdb.set_trace()
	 sleep(30)
         grid_ref=json.loads(grid_ref)
         grid_dns_ref=grid_ref[0]['_ref']
         fields=grid_dns_ref+"?_return_fields=allow_query,allow_update,forwarders,logging_categories,allow_recursive_query"
         grid_fields_data=ib_NIOS.wapi_request('GET',object_type=fields)
         print ("before editing grid : dns properties",grid_fields_data)
	 grid_fields_data='"allow_recursive_query": true'
         data={"allow_query": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}],"allow_recursive_query": True,"allow_update": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}],"forwarders": [],"logging_categories": {"log_client": False,"log_config": False,"log_database": False,"log_dnssec": False,"log_dtc_gslb": False,"log_dtc_health": False,"log_general": False,"log_lame_servers": False,"log_network": False,"log_notify": False,"log_queries": True,"log_query_rewrite": False,"log_rate_limit": False,"log_resolver": False,"log_responses": False,"log_rpz": True,"log_security": False,"log_update": False,"log_update_security": False,"log_xfer_in": False,"log_xfer_out": False}}
         condition=ib_NIOS.wapi_request('PUT', ref=grid_dns_ref, fields=json.dumps(data))
         print (condition)
         publish={"member_order":"SIMULTANEOUSLY"}
         request_publish = ib_NIOS.wapi_request('POST', object_type = grid_dns_ref + "?_function=publish_changes",fields=json.dumps(publish))
         time.sleep(10)
	 restart_services()
	 '''
         request_restart = ib_NIOS.wapi_request('POST', object_type = grid_dns_ref + "?_function=requestrestartservicestatus")
         restart = ib_NIOS.wapi_request('POST', object_type = grid_dns_ref + "?_function=restartservices")
         time.sleep(10)
	 '''
         new_fields=grid_dns_ref+"?_return_fields=allow_recursive_query"
         new_grid_fields_data=ib_NIOS.wapi_request('GET',object_type=new_fields)
	 new_grid_fields_data=new_grid_fields_data.split('\n')
	 new_grid_fields_data=new_grid_fields_data[3]
         if (grid_fields_data == new_grid_fields_data):
               assert False
               print (" Test case 5 failed, Modified GRID DNS Properties ")
         else:
               assert True
               print ("Test case 5 passed , Modify GRID_DNS Properties ")
         
        
     @pytest.mark.run(order=6)
     def test_06_add_rpz_zone(self):
         get_ref=ib_NIOS.wapi_request('POST', object_type="zone_rp",fields=json.dumps(rpz_data))
	 print(get_ref)
         print("adding RPZ zone ")
         #pdb.set_trace()
         if (get_ref[0]!=400):
             grid =  ib_NIOS.wapi_request('GET', object_type="grid")
             ref = json.loads(grid)[0]['_ref']
             publish={"member_order":"SIMULTANEOUSLY"}
             request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
	     print(request_publish)
             time.sleep(10)
             request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
	     print(request_restart)
             restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
             time.sleep(20)
             print ("Restarting the grid ")
             response=ib_NIOS.wapi_request('GET', object_type="zone_rp")
	     print(response)
             response1=json.loads(response)
             print ("::::::::::::::::::::",response1)
             if (response1[0]["fqdn"]==rpz_data["fqdn"]):
                 print("Test case passed as RPZ zone is added")
                 assert True
             else:
                 print("Test case failed as RPZ zone is not added")
               
         else:
             assert False 
             print("Test case failed as RPZ zone is not added")


     @pytest.mark.run(order=7)
     def test_07_adding_nodomain_rule_to_rpz_zone(self):
         data={"canonical": "","comment": "check","disable": False,"extattrs": {},"name":"a."+str(auth_zone['fqdn'])+"."+str(rpz_data['fqdn']),"rp_zone": str(rpz_data['fqdn']),"use_ttl": False,"view": "default"}
         print ("|||||||||||||||||||||||||||||||||||||||||",data)
         get_ref=ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
         print ("Rule added with reference :",get_ref)
         new_get_ref=ib_NIOS.wapi_request('GET', object_type="record:rpz:cname")
         new_get_ref=json.loads(new_get_ref)
         reference=new_get_ref[0]['_ref']
         new_data=ib_NIOS.wapi_request('GET', object_type=reference+"?_return_fields=canonical,comment,disable,extattrs,name,rp_zone,ttl,use_ttl,view")
         new_data=json.loads(new_data)
         new_data.pop('_ref')
         print ("updated data after POST command : ",new_data)
         if (new_data == data):
             assert True
             print ("Test case 07 passed , no-domain rule added successfully")
         else:
             assert False
             print ("Test case 07 failed , no-domain rule not added successfully")
         

     @pytest.mark.run(order=8)
     def test_08_query_with_ipv4_and_ipv6(self):
                  
         grid_ref=ib_NIOS.wapi_request('GET',object_type="member:dns")
         grid_ref=json.loads(grid_ref)
         grid_dns_ref=grid_ref[0]['_ref']
         fields=grid_dns_ref+"?_return_fields=ipv4addr,ipv6addr"
         grid_fields_data=ib_NIOS.wapi_request('GET',object_type=fields)
         grid_fields_data=json.loads(grid_fields_data)
         grid_fields_data.pop('_ref')
         ipv4_address=grid_fields_data['ipv4addr']
	 #pdb.set_trace()
         ipv6_address=grid_fields_data['ipv6addr']
         sleep(30)
         log("start","/var/log/syslog",config.grid_vip)
         print ("querying with either ipv4, ipv6 address with zone name. RPZ CEF logged but NXDomain responses are seen as expected")
         try:
             record_list=['a']
             for i in record_list:
                 LookFor='.* status: NXDOMAIN .*'+str(i)+'.'+auth_zone['fqdn']+'.*IN.*'+str(i)+'.*'
                 logging.info ("$$$$$$$$$$$$$$$$$$$",LookFor)
                 #pdb.set_trace()
                 #result_ipv4 = os.system('dig @'+config.grid_vip+' a.source.com a')
                 result_ipv4=os.popen("for i in {1..3}; do dig @"+config.grid_vip+" a.source.com a; sleep 2 ; done")
                 print result_ipv4
                 time.sleep(20)
                 LookFor='.* status: NXDOMAIN .*'+str(i)+'.'+auth_zone['fqdn']+'.*IN.*'+str(i)+'.*'
                 NoneType = type(None)
                 if  isinstance(result_ipv4, NoneType):
                      assert False
         except ValueError:
             logging.info ("Dig failed")
         sleep(30)
         log("stop","/var/log/syslog",config.grid_vip)
         #sleep(30)
         
         #pdb.set_trace()
         #LookFor = 'CEF:0|Infoblox|NIOS|'
	 LookFor =".*named.*info CEF.*"
         log_validation=logv(LookFor,"/var/log/syslog",config.grid_vip)  #here for log validation , we have not used assert because if pattern/LookFor string is not found in the logs,then it fails which is managed by log_validity utility.
         print('look for is',LookFor)
         print(log_validation)
         print("---------------------------")
         if log_validation:
             assert True
         else:
            assert False
         time.sleep(5)

     @pytest.mark.run(order=9)
     def test_09_enabling_dns64_with_default_group(self):
         print ("Enabling DNS64 with Default Group ")
         dns_ref=ib_NIOS.wapi_request('GET',object_type="grid:dns")
         dns_ref=json.loads(dns_ref)
         dns_ref=dns_ref[0]['_ref']
         data={"dns64_groups": ["default"],"enable_dns64": True}
         response = ib_NIOS.wapi_request('PUT',ref=dns_ref,fields=json.dumps(data))
         response=json.loads(response)
         time.sleep(4)
         print ("Restart services")
         print ("Associated Zone with Primary GRID and reference looks like :",response)
         grid =  ib_NIOS.wapi_request('GET', object_type="grid")
         ref = json.loads(grid)[0]['_ref']
         publish={"member_order":"SIMULTANEOUSLY"}
         request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
         time.sleep(10)
         request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
         restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
         time.sleep(10)
         new_data= ib_NIOS.wapi_request('GET', object_type=dns_ref+"?_return_fields=enable_dns64,dns64_groups")
         print ("new data is here :",new_data)
         new_data=json.loads(new_data)
         new_data.pop('_ref')
         if (new_data == data):
             assert True
             print ("DNS64 Enabled successfully")
             print ("Test case 9 passed")
         else:
             assert False
             print ("DNS64 Enabling Failed")
             print ("Test case 9 Failed")




     @pytest.mark.run(order=10)
     def test_10_query_with_ipv4_and_ipv6(self):
         grid_ref=ib_NIOS.wapi_request('GET',object_type="member:dns")
         grid_ref=json.loads(grid_ref)
         grid_dns_ref=grid_ref[0]['_ref']
         fields=grid_dns_ref+"?_return_fields=ipv4addr,ipv6addr"
         grid_fields_data=ib_NIOS.wapi_request('GET',object_type=fields)
         grid_fields_data=json.loads(grid_fields_data)
         grid_fields_data.pop('_ref')
         #ipv4_address=grid_fields_data['ipv4addr']
         #ipv6_address=grid_fields_data['ipv6addr']
         #pdb.set_trace()
         log("start","/var/log/syslog",config.grid_vip)
         print ("querying with either ipv4, ipv6 address with zone name. RPZ CEF logged but NXDomain responses are seen as expected")
         try:
             record_list=['a']
             for i in record_list:
                 LookFor='.* status: NXDOMAIN .*'+str(i)+'.'+auth_zone['fqdn']+'.*IN.*'+str(i)+'.*'
                 print ("$$$$$$$$$$$$$$$$$$$",LookFor)
                 #dig({"fqdn":"test.com"},"a",("hinfo.test.com. * IN *   "))
                 result_ipv4 = os.system('dig @'+config.grid_vip +' '+'a.source.com a')
                 #result_ipv4=os.system("dig @10.35.171.10 a.source.com a")
                 #result_ipv4=dig(i,rpz_data,i.lower(),LookFor,ipv4_address)
		 print result_ipv4
                 #dig(i,auth_zone,i.lower(),LookFor,ipv4_address)
                 #time.sleep(60)
                 LookFor='.* status: NXDOMAIN .*'+str(i)+'.'+auth_zone['fqdn']+'.*IN.*'+str(i)+'.*'
                 #result_ipv6=dig(i,rpz_data,i.lower(),LookFor,ipv6_address)
                 #print ("type here : " ,type(result_ipv4))
		 #print result_ipv6
                 #print ("type here : " , result_ipv6)
                 NoneType = type(None)
                 if  isinstance(result_ipv4, NoneType) :
                      print ("error")
         except ValueError:
             logging.info ("Dig failed")
         log("stop","/var/log/syslog",config.grid_vip)
         #LookFor='.*info CEF:0|Infoblox|NIOS|.*'
         LookFor = 'info CEF:0|Infoblox|NIOS|'
         #out1=str(config.grid_vip+'_var_log_messages.log')
         #print(out1)
         #textfile=open('/tmp/'+out1,'r')
         #log_validation=textfile.read()
         #textfile.close()
         #print('logs are given below',log_validation)
         log_validation=logv(LookFor,"/var/log/syslog",config.grid_vip)  #here for log validation , we have not used assert because if pattern/LookFor string is not found in the logs,then it fails which is managed by log_validity utility.
         #check=re.search('sneha',log_validation)
         print('look for is',LookFor)
         print(log_validation)
         print("--------------------------------")
         if log_validation:
             assert True
         else:
            assert False
         #print(check)
         #print (type(check))
         #print (check)
         #time.sleep(5)
     
     '''
     @pytest.mark.run(order=11)
     def test_11_clean_up(self):
         logging.info("cleaning up zones and rpz added")
	     #zone=ib_NIOS.wapi_request('GET',object_type='zone_auth',grid_vip= config.grid_vip)
         get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth")
	     
         for zone1_ref in json.loads(get_ref):
             response = ib_NIOS.wapi_request('DELETE', zone1_ref['_ref'],grid_vip= config.grid_vip)
	 #restart_services
	     rpz_zone=ib_NIOS.wapi_request('GET',object_type='zone_rp',grid_vip= config.grid_vip)
	     print(rpz_zone)
	     rpz_ref=json.loads(rpz_zone)[0]['_ref']
	     del_rpz=ib_NIOS.wapi_request('DELETE',ref=rpz_ref)
	     print(del_rpz)
	
	
     '''

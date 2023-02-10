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
import requests
import time
#import pexpect
#from log_capture import log_action as log
#from log_validation import log_validation as logv 

class Network(unittest.TestCase):
      @pytest.mark.run(order=1)
      def test_001_create_IPv4_network(self):
          logging.info("Create an ipv4 network in default network view")
          data = {"network": "10.0.0.0/24","network_view": "default","members":[{"_struct": "dhcpmember","ipv4addr":config.grid_vip}]}
          response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data), grid_vip=config.grid_vip)
          print(response)
          print("Created the ipv4network 10.0.0.0/24 in default view")
          logging.info("Created the ipv4network 10.0.0.0/24 in default view")
          logging.info("Restart DHCP Services")
          grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
          ref = json.loads(grid)[0]['_ref']
          data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
          request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
          sleep(20) #wait for 20 secs for the member to get started
          response = ib_NIOS.wapi_request('GET', object_type="network",grid_vip=config.grid_vip)
          print(response)
          if ("10.0.0.0/24" in response):
                assert True
          else:
                assert False
          print("Test Case 1 Execution Completed")

      @pytest.mark.run(order=2)
      def test_002_create_IPv4_Range(self):
           logging.info("Create an IPv4 range in network")
           data = {"network":"10.0.0.0/24","start_addr":"10.0.0.10","end_addr":"10.0.0.100","network_view": "default","member": {"_struct": "dhcpmember","ipv4addr": config.grid_vip,"name": config.grid_fqdn}}
           response = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(data), grid_vip=config.grid_vip)
           print (response)
           print("Created the ipv4 prefix range with bits 24  in default view")
           logging.info("Created the ipv4 prefix range with bits 24  in default view")
           logging.info("Restart DHCP Services")
           grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
           ref = json.loads(grid)[0]['_ref']
           data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
           request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
           sleep(20) #wait for 20 secs for the member to get started
           response = ib_NIOS.wapi_request('GET', object_type="range", grid_vip=config.grid_vip)
           response=eval(response)
           print(response)
           if (response[0].get('start_addr') == "10.0.0.10" and response[0].get('end_addr') == "10.0.0.100"):
                   assert True
           else:
                   assert False
           print("Test Case 2 Execution Completed") 	    

      @pytest.mark.run(order=3)
      def test_003_validating_the_inherited_values_of_lease_scavenge_time_at_grid_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of lease_scavenge_time with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"lease_scavenge_time": 86400}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=lease_scavenge_time",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['lease_scavenge_time']
          if (response['inherited']== True and response['value']== 86400 and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 3 Execution Completed")



      @pytest.mark.run(order=4)
      def test_004_validating_the_inherited_values_of_authority_at_grid_dhcpproperties_network(self):
          logging.info("validating the inherited values of authority with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"authority": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=authority",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['authority']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 4 Execution Completed")

      @pytest.mark.run(order=5)
      def test_005_validating_the_inherited_values_of_ignore_dhcp_optionlist_at_grid_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of ignore_dhcp_option_list with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ignore_dhcp_option_list_request": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=ignore_dhcp_option_list_request",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ignore_dhcp_option_list_request']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 5 Execution Completed")


      @pytest.mark.run(order=6)
      def test_006_validating_the_inherited_values_of_enable_ddns_at_grid_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of enable_ddns with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"enable_ddns": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=enable_ddns",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['enable_ddns']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 6 Execution Completed")

      @pytest.mark.run(order=7)
      def test_007_validating_the_inherited_values_of_ddns_domainname_at_grid_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of ddns_domainname with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_domainname": "www.infoblox.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=ddns_domainname",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_domainname']
          if (response['inherited']== True and response['value']== "www.infoblox.com" and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 7 Execution Completed")


      @pytest.mark.run(order=8)
      def test_008_validating_the_inherited_values_of_ddns_ttl_at_grid_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of ddns_ttl with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_ttl": 100}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=ddns_ttl",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_ttl']
          if (response['inherited']== True and response['value']== 100 and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 8 Execution Completed")


      @pytest.mark.run(order=9)
      def test_009_validating_the_inherited_values_of_ddns_generate_hostname_at_grid_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of ddns_generate_hostname with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_generate_hostname": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=ddns_generate_hostname",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_generate_hostname']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 9 Executuion Completed")

      @pytest.mark.run(order=10)
      def test_010_validating_the_inherited_values_of_ddns_fixed_address_at_grid_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of ddns_update_fixed_address with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_update_fixed_addresses": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=ddns_update_fixed_addresses",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_update_fixed_addresses']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 10 Executuion Completed")

      @pytest.mark.run(order=11)
      def test_011_validating_the_inherited_values_of_ddns_use_option81_at_grid_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of ddns_use_option81 with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_use_option81": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=ddns_use_option81",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_use_option81']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 11 Executuion Completed")


      @pytest.mark.run(order=12)
      def test_012_validating_the_inherited_values_of_update_dns_on_lease_renewal_at_grid_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of update_dns_on_lease_renewal with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"update_dns_on_lease_renewal": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=update_dns_on_lease_renewal",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['update_dns_on_lease_renewal']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 12 Executuion Completed")

      @pytest.mark.run(order=13)
      def test_013_validating_the_inherited_values_of_enable_dhcp_thresholds_at_grid_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of enable_dhcp_thresholds with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"enable_dhcp_thresholds": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=enable_dhcp_thresholds",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['enable_dhcp_thresholds']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 13 Executuion Completed")

      @pytest.mark.run(order=14)
      def test_014_validating_the_inherited_values_of_pxe_lease_time_at_grid_dhcpproperties_with_network(self):
          #logging.info("validating the inherited values of pxe_lease_time with network")
          #get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          #res = json.loads(get_ref)
          #ref1 = json.loads(get_ref)[0]['_ref']
          #data = {"pxe_lease_time": 43200}
          #output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          logging.info("Through perl script giving pxe_lease_time value at grid")
          pxe_value = 'perl pxe_lease_time_script_for_grid_14.pl {}'.format(config.grid_vip)
          pxe_value1 = os.system(pxe_value)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=pxe_lease_time",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['pxe_lease_time']
          if (response['inherited']== True and response['value']== 43200 and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 14 Execution Completed")


      @pytest.mark.run(order=15)
      def test_015_validating_the_inherited_values_of_deny_bootp_at_grid_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of deny_bootp with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"deny_bootp": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=deny_bootp",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['deny_bootp']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 15 Executuion Completed")


      @pytest.mark.run(order=16)
      def test_016_validating_the_inherited_values_of_bootfile_at_grid_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of bootfile with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"bootfile": "100"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=bootfile",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['bootfile']
          if (response['inherited']== True and response['value']== "100" and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 16 Execution Completed") 

      @pytest.mark.run(order=17)
      def test_017_validating_the_inherited_values_of_nextserver_at_grid_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of nextserver with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"nextserver": "www.infoblox.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=nextserver",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['nextserver']
          if (response['inherited']== True and response['value']== "www.infoblox.com" and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 17 Execution Completed") 


      @pytest.mark.run(order=18)
      def test_018_validating_the_inherited_values_of_bootserver_at_grid_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of bootserver with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"bootserver": "www.infoblox.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=bootserver",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['bootserver']
          if (response['inherited']== True and response['value']== "www.infoblox.com" and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 18 Execution Completed")

      @pytest.mark.run(order=19)
      def test_019_validating_the_inherited_values_of_enable_dhcp_thresholds_at_grid_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of enable_dhcp_thresholds with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"enable_dhcp_thresholds": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=enable_dhcp_thresholds",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['enable_dhcp_thresholds']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 19 Executuion Completed")

      @pytest.mark.run(order=20)
      def test_020_validating_the_inherited_values_of_email_list_at_grid_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of email_list with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"email_setting": {"address": "pkondisetty@infoblox.com","enabled": True,"from_address": "ashetty@infoblox.com","relay_enabled": False}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=email_list",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['email_list']
          if (response['inherited']== True and response['value']== ["pkondisetty@infoblox.com"] and response['multisource']== False and "grid/" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 20 Executuion Completed")


      @pytest.mark.run(order=21)
      def test_021_validating_the_inherited_values_of_logic_filter_rules_at_grid_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of logic_filter_rules with network")
          data = {"name": "prasad"}
          response = ib_NIOS.wapi_request('POST', object_type="filtermac", fields=json.dumps(data), grid_vip=config.grid_vip)
          print(response)
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"logic_filter_rules":[{"filter": "prasad","type": "MAC"}]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response1 = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=logic_filter_rules",grid_vip=config.grid_vip)
          print(response1)
          response1=json.loads(response1)
          response1=response1[0]['logic_filter_rules']
          if (response1['inherited']== True and response1['multisource']== False and response1['value']== [{"filter": "prasad","type": "MAC"}] and "grid:dhcpproperties" in response1['source']):
                  assert True
          else:
                  assert False
          print("Test Case 21 Executuion Completed")


      @pytest.mark.run(order=22)
      def test_022_validating_the_inherited_values_of_enable_ifmap_publishing_at_grid_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of enable_ifmap_publishing with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"enable_ifmap_publishing": False}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=enable_ifmap_publishing",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['enable_ifmap_publishing']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 22 Executuion Completed")


      @pytest.mark.run(order=23)
      def test_023_validating_the_inherited_values_of_ipam_trap_settings_at_grid_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of ipam_trap_settings with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"trap_notifications": [{"enable_email": True,"enable_trap": True,"trap_type": "AnalyticsRPZ"},{"enable_email": True,"enable_trap": True,"trap_type": "AutomatedTrafficCapture"},{"enable_email": True,"enable_trap": True,"trap_type": "BFD"},{"enable_email": True,"enable_trap": True,"trap_type": "BGP"},{"enable_email": True,"enable_trap": True,"trap_type": "Backup"},{"enable_email": True,"enable_trap": True,"trap_type": "Bloxtools"},{"enable_email": True,"enable_trap": True,"trap_type": "CPU"},{"enable_email": True,"enable_trap": True,"trap_type": "CaptivePortal"},{"enable_email": True,"enable_trap": True,"trap_type": "CiscoISEServer"},{"enable_email": True,"enable_trap": True,"trap_type": "Clear"},{"enable_email": True,"enable_trap": True,"trap_type": "CloudAPI"},{"enable_email": True,"enable_trap": True,"trap_type": "Cluster"},{"enable_email": True,"enable_trap": True,"trap_type": "Controld"},{"enable_email": True,"enable_trap": True,"trap_type": "DHCP"},{"enable_email": True,"enable_trap": True,"trap_type": "DNS"},{"enable_email": True,"enable_trap": True,"trap_type": "DNSAttack"},{"enable_email": True,"enable_trap": True,"trap_type": "DNSIntegrityCheck"},{"enable_email": True,"enable_trap": True,"trap_type": "DNSIntegrityCheckConnection"},{"enable_email": True,"enable_trap": True,"trap_type": "Database"},{"enable_email": True,"enable_trap": True,"trap_type": "DisconnectedGrid"},{"enable_email": True,"enable_trap": True,"trap_type": "Discovery"},{"enable_email": True,"enable_trap": True,"trap_type": "DiscoveryConflict"},{"enable_email": True,"enable_trap": True,"trap_type": "DiscoveryUnmanaged"},{"enable_email": True,"enable_trap": True,"trap_type": "Disk"},{"enable_email": True,"enable_trap": True,"trap_type": "DuplicateIP"},{"enable_email": True,"enable_trap": True,"trap_type": "ENAT"},{"enable_email": True,"enable_trap": True,"trap_type": "FDUsage"},{"enable_email": True,"enable_trap": True,"trap_type": "FTP"},{"enable_email": True,"enable_trap": True,"trap_type": "Fan"},{"enable_email": True,"enable_trap": True,"trap_type": "HA"},{"enable_email": True,"enable_trap": True,"trap_type": "HSM"},{"enable_email": True,"enable_trap": True,"trap_type": "HTTP"},{"enable_email": True,"enable_trap": True,"trap_type": "IFMAP"},{"enable_email": True,"enable_trap": True,"trap_type": "IMC"},{"enable_email": True,"enable_trap": True,"trap_type": "IPAMUtilization"},{"enable_email": True,"enable_trap": True,"trap_type": "IPMIDevice"},{"enable_email": True,"enable_trap": True,"trap_type": "LCD"},{"enable_email": True,"enable_trap": True,"trap_type": "LDAPServers"},{"enable_email": True,"enable_trap": True,"trap_type": "License"},{"enable_email": True,"enable_trap": True,"trap_type": "Login"},{"enable_email": True,"enable_trap": True,"trap_type": "MGM"},{"enable_email": True,"enable_trap": True,"trap_type": "MSServer"},{"enable_email": True,"enable_trap": True,"trap_type": "Memory"},{"enable_email": True,"enable_trap": True,"trap_type": "NTP"},{"enable_email": True,"enable_trap": True,"trap_type": "Network"},{"enable_email": True,"enable_trap": True,"trap_type": "OCSPResponders"},{"enable_email": True,"enable_trap": True,"trap_type": "OSPF"},{"enable_email": True,"enable_trap": True,"trap_type": "OSPF6"},{"enable_email": True,"enable_trap": True,"trap_type": "Outbound"},{"enable_email": True,"enable_trap": True,"trap_type": "PowerSupply"},{"enable_email": True,"enable_trap": True,"trap_type": "RAID"},{"enable_email": True,"enable_trap": True,"trap_type": "RIRSWIP"},{"enable_email": True,"enable_trap": True,"trap_type": "RPZHitRate"},{"enable_email": True,"enable_trap": True,"trap_type": "RecursiveClients"},{"enable_email": True,"enable_trap": True,"trap_type": "Reporting"},{"enable_email": True,"enable_trap": True,"trap_type": "RootFS"},{"enable_email": True,"enable_trap": True,"trap_type": "SNMP"},{"enable_email": True,"enable_trap": True,"trap_type": "SSH"},{"enable_email": True,"enable_trap": True,"trap_type": "SerialConsole"},{"enable_email": True,"enable_trap": True,"trap_type": "SwapUsage"},{"enable_email": True,"enable_trap": True,"trap_type": "Syslog"},{"enable_email": True,"enable_trap": True,"trap_type": "System"},{"enable_email": True,"enable_trap": True,"trap_type": "TFTP"},{"enable_email": True,"enable_trap": True,"trap_type": "Taxii"},{"enable_email": True,"enable_trap": True,"trap_type": "ThreatAnalytics"},{"enable_email": True,"enable_trap": True,"trap_type": "ThreatProtection"}]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=ipam_trap_settings",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ipam_trap_settings']
          if (response['inherited']== True and response['value']== {"enable_email_warnings": True,"enable_snmp_warnings": True} and response['multisource']== False and "grid/" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 23 Executuion Completed")

      @pytest.mark.run(order=24)
      def test_024_validating_the_inherited_values_of_high_water_mark_and_high_water_mark_reset_at_grid_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of high_water_mark,high_water_mark_reset with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"high_water_mark": 100,"high_water_mark_reset": 90}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=high_water_mark,high_water_mark_reset",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response1=response[0]['high_water_mark']
          response2=response[0]['high_water_mark_reset']
          if (response1['inherited']== True and response1['value']== 100 and response1['multisource']== False and "grid:dhcpproperties" in response1['source']):
                  assert True
          elif (response2['inherited']== True and response2['value']== 90 and response2['multisource']== False and "grid:dhcpproperties" in response2['source']):
                assert True
          else:
                assert False
          print("Test Case 24 Executuion Completed")
      
      @pytest.mark.run(order=25)
      def test_025_validating_the_inherited_values_of_email_list_at_grid_with_network(self):
          logging.info("validating the inherited values of email_list with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"email_setting": {"address": "ashetty@infoblox.com","enabled": True,"from_address": "pkondisetty@infoblox.com","relay_enabled": False}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=email_list",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['email_list']
          if (response['inherited']== True and response['value']== ["ashetty@infoblox.com"] and response['multisource']== False and "grid/" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 25 Executuion Completed")

      @pytest.mark.run(order=26)
      def test_026_validating_the_inherited_values_of_ignore_mac_addresses_at_grid_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of ignore_mac_addresses with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ignore_id": "MACADDR","ignore_mac_addresses": ["11:22:33:44:55:66"]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=ignore_mac_addresses",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ignore_mac_addresses']
          if (response['inherited']== True and response['value']== ["11:22:33:44:55:66"] and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 26 Executuion Completed")


      @pytest.mark.run(order=27)
      def test_027_validating_the_inherited_values_of_lease_scavenge_time_at_grid_dhcpproperties_with_range(self):
          logging.info("validating the inherited values of lease_scavenge_time with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"lease_scavenge_time": 172800}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=lease_scavenge_time",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
  	#print(response)
          response=response[0]['lease_scavenge_time']
  	#print(response)
          if (response['inherited']== True and response['value']== 172800 and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 27 Execution Completed")

      @pytest.mark.run(order=28)
      def test_028_validating_the_inherited_values_of_ignore_dhcp_option_list_request_at_grid_dhcpproperties_with_range(self):
          logging.info("validating the inherited values of ignore_dhcp_option_list_request with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ignore_dhcp_option_list_request": False}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=ignore_dhcp_option_list_request",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ignore_dhcp_option_list_request']
          if (response['inherited']== True and response['value']== False and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 28 Execution Completed")


      @pytest.mark.run(order=29)
      def test_029_validating_the_inherited_values_of_enable_ddns_at_grid_dhcpproperties_with_range(self):
          logging.info("validating the inherited values of enable_ddns with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"enable_ddns": False}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=enable_ddns",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['enable_ddns']
          if (response['inherited']== True and response['value']== False and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 29 Execution Completed")


      @pytest.mark.run(order=30)
      def test_030_validating_the_inherited_values_of_ddns_domainname_at_grid_dhcpproperties_with_range(self):
          logging.info("validating the inherited values of ddns_domainname with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_domainname": "www.range.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=ddns_domainname",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_domainname']
          if (response['inherited']== True and response['value']== "www.range.com" and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 30 Execution Completed")


      @pytest.mark.run(order=31)
      def test_031_validating_the_inherited_values_of_ddns_generate_hostname_at_grid_hcpproperties_with_range(self):
          logging.info("validating the inherited values of ddns_generate_hostname with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_generate_hostname": False}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=ddns_generate_hostname",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_generate_hostname']
          if (response['inherited']== True and response['value']== False and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 31 Executuion Completed")


      @pytest.mark.run(order=32)
      def test_032_validating_the_inherited_values_of_update_dns_on_lease_renewal_at_grid_dhcpproperties_with_range(self):
          logging.info("validating the inherited values of update_dns_on_lease_renewal with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"update_dns_on_lease_renewal": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=update_dns_on_lease_renewal",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['update_dns_on_lease_renewal']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 32 Executuion Completed")


      @pytest.mark.run(order=33)
      def test_033_validating_the_inherited_values_of_pxe_lease_time_at_grid_dhcpproperties_with_range(self):
          logging.info("validating the inherited values of pxe_lease_time with range")
          #get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          #res = json.loads(get_ref)
          #ref1 = json.loads(get_ref)[0]['_ref']
          #data = {"pxe_lease_time": 43200}
          #output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          logging.info("Through perl script giving pxe_lease_time value at grid")
          pxe_value = 'perl pxe_lease_time_script_for_grid_33.pl {}'.format(config.grid_vip)
          pxe_value1 = os.system(pxe_value)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=pxe_lease_time",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['pxe_lease_time']
          if (response['inherited']== True and response['value']== 43200 and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 33 Execution Completed")


      @pytest.mark.run(order=34)
      def test_034_validating_the_inherited_values_of_deny_bootp_at_grid_dhcpproperties_with_range(self):
          logging.info("validating the inherited values of deny_bootp with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"deny_bootp": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=deny_bootp",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['deny_bootp']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 34 Executuion Completed")


      @pytest.mark.run(order=35)
      def test_035_validating_the_inherited_values_of_bootfile_at_grid_dhcpproperties_with_range(self):
          logging.info("validating the inherited values of bootfile with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"bootfile": "1000"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=bootfile",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['bootfile']
          if (response['inherited']== True and response['value']== "1000" and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 35 Execution Completed")


      @pytest.mark.run(order=36)
      def test_036_validating_the_inherited_values_of_nextserver_at_grid_dhcpproperties_with_range(self):
          logging.info("validating the inherited values of nextserver with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"nextserver": "www.infoblox.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=nextserver",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['nextserver']
          if (response['inherited']== True and response['value']== "www.infoblox.com" and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 36 Execution Completed")


      @pytest.mark.run(order=37)
      def test_037_validating_the_inherited_values_of_boot_server_at_grid_dhcpproperties_with_range(self):
          logging.info("validating the inherited values of bootserver with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"bootserver": "www.prasad.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=bootserver",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['bootserver']
          if (response['inherited']== True and response['value']== "www.prasad.com" and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 37 Execution Completed")


      @pytest.mark.run(order=38)
      def test_038_validating_the_inherited_values_of_enable_dhcp_thresholds_at_grid_dhcpproperties_with_range(self):
          logging.info("validating the inherited values of enable_dhcp_thresholds with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"enable_dhcp_thresholds": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=enable_dhcp_thresholds",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['enable_dhcp_thresholds']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 38 Executuion Completed")


      @pytest.mark.run(order=39)
      def test_039_validating_the_inherited_values_of_email_list_at_grid_dhcpproperties_with_range(self):
          logging.info("validating the inherited values of email_list with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"email_setting": {"address": "prasad@infoblox.com","enabled": True,"from_address": "ajith@infoblox.com","relay_enabled": False}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=email_list",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['email_list']
          if (response['inherited']== True and response['value']== ["prasad@infoblox.com"] and response['multisource']== False and "grid/" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 39 Executuion Completed")



      @pytest.mark.run(order=40)
      def test_040_validating_the_inherited_values_of_logic_filter_rules_at_grid_dhcpproperties_with_range(self):
          logging.info("validating the inherited values of logic_filter_rules with range")
          data = {"name": "prasad123"}
          response = ib_NIOS.wapi_request('POST', object_type="filtermac", fields=json.dumps(data), grid_vip=config.grid_vip)
          print(response)
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"logic_filter_rules":[{"filter": "prasad123","type": "MAC"}]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response1 = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=logic_filter_rules",grid_vip=config.grid_vip)
          print(response1)
          response1=json.loads(response1)
          response1=response1[0]['logic_filter_rules']
          if (response1['inherited']== True and response1['multisource']== False and response1['value']== [{"filter": "prasad123","type": "MAC"}] and "grid:dhcpproperties" in response1['source']):
                  assert True
          else:
                  assert False
          print("Test Case 40 Executuion Completed")
                               
                                               
      @pytest.mark.run(order=41)
      def test_041_validating_the_inherited_values_of_ignore_mac_addresses_at_grid_dhcpproperties_with_range(self):
          logging.info("validating the inherited values of ignore_mac_addresses with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ignore_id": "MACADDR","ignore_mac_addresses": ["11:22:33:66:55:44"]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=ignore_mac_addresses",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ignore_mac_addresses']
          if (response['inherited']== True and response['value']== ["11:22:33:66:55:44"] and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 41 Executuion Completed")                             
                                   
                                   
      @pytest.mark.run(order=42)
      def test_042_create_ipv4_fixed_address(self):
          logging.info("Create an ipv4 fixedaddress")
          data = {"ipv4addr":"10.0.0.1","mac":"aa:bb:cc:11:22:33"}
          response = ib_NIOS.wapi_request('POST', object_type="fixedaddress", fields=json.dumps(data), grid_vip=config.grid_vip)
          print(response)
          response1 = ib_NIOS.wapi_request('GET', object_type="fixedaddress", grid_vip=config.grid_vip)
          print(response1)
          response=eval(response1)
          if (response[0].get('ipv4addr') == "10.0.0.1"):
                assert True
          else:
                assert False
          print("Test Case 42 Execution Completed")                             
                                      
                                          
      @pytest.mark.run(order=43)
      def test_043_validating_the_inherited_values_of_enable_ddns_at_grid_dhcpproperties_with_fixedaddress(self):
          logging.info("validating the inherited values of enable_ddns with fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"enable_ddns": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=enable_ddns",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['enable_ddns']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 43 Execution Completed")

      @pytest.mark.run(order=44)
      def test_044_validating_the_inherited_values_of_ddns_domainname_at_grid_dhcpproperties_with_fixedaddress(self):
          logging.info("validating the inherited values of ddns_domainname with fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_domainname": "www.fixedaddress.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=ddns_domainname",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_domainname']
          if (response['inherited']== True and response['value']== "www.fixedaddress.com" and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 44 Execution Completed")

                                       
      @pytest.mark.run(order=45)
      def test_045_validating_the_inherited_values_of_pxe_lease_time_at_grid_dhcpproperties_with_fixedaddress(self):
          logging.info("validating the inherited values of pxe_lease_time with fixedaddress")
          #get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          #res = json.loads(get_ref)
          #ref1 = json.loads(get_ref)[0]['_ref']
          #data = {"pxe_lease_time": 86400}
          #output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          logging.info("Through perl script giving pxe_lease_time value at grid")
          pxe_value = 'perl pxe_lease_time_script_for_grid_045.pl {}'.format(config.grid_vip)
          pxe_value1 = os.system(pxe_value)
          response = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=pxe_lease_time",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['pxe_lease_time']
          if (response['inherited']== True and response['value']== 86400 and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 45 Execution Completed")                               
                             
                                 
      @pytest.mark.run(order=46)
      def test_046_validating_the_inherited_values_of_deny_bootp_at_grid_dhcpproperties_with_fixedaddress(self):
          logging.info("validating the inherited values of deny_bootp with fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"deny_bootp": False}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=deny_bootp",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['deny_bootp']
          if (response['inherited']== True and response['value']== False and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 46 Executuion Completed")

      @pytest.mark.run(order=47)
      def test_047_validating_the_inherited_values_of_bootfile_at_grid_dhcpproperties_with_fixedaddress(self):
          logging.info("validating the inherited values of bootfile with fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"bootfile": "10000"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=bootfile",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['bootfile']
          if (response['inherited']== True and response['value']== "10000" and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 47 Execution Completed")

      @pytest.mark.run(order=48)
      def test_048_validating_the_inherited_values_of_nextserver_at_grid_dhcpproperties_with_fixedaddress(self):
          logging.info("validating the inherited values of nextserver with fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"nextserver": "www.infoblox1.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=nextserver",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['nextserver']
          if (response['inherited']== True and response['value']== "www.infoblox1.com" and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 48 Execution Completed")

      @pytest.mark.run(order=49)
      def test_049_validating_the_inherited_values_of_bootserver_at_grid_dhcpproperties_with_fixedaddress(self):
          logging.info("validating the inherited values of bootserver with fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"bootserver": "www.prasad1.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=bootserver",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['bootserver']
          if (response['inherited']== True and response['value']== "www.prasad1.com" and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 49 Execution Completed")


      @pytest.mark.run(order=50)
      def test_050_validating_the_inherited_values_of_logic_filter_rules_at_grid_dhcpproperties_with_fixedaddress(self):
          logging.info("validating the inherited values of logic_filter_rules with fixedaddress")
          data = {"name": "prasad12345"}
          response = ib_NIOS.wapi_request('POST', object_type="filtermac", fields=json.dumps(data), grid_vip=config.grid_vip)
          print(response)
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"logic_filter_rules":[{"filter": "prasad12345","type": "MAC"}]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response1 = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=logic_filter_rules",grid_vip=config.grid_vip)
          print(response1)
          response1=json.loads(response1)
          response1=response1[0]['logic_filter_rules']
          if (response1['inherited']== True and response1['multisource']== False and response1['value']== [{"filter": "prasad12345","type": "MAC"}] and "grid:dhcpproperties" in response1['source']):
                  assert True
          else:
                  assert False
          print("Test Case 50 Executuion Completed")                         
                                      
                  
      @pytest.mark.run(order=51)
      def test_051_validating_the_inherited_values_of_lease_scavenge_time_at_member_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of lease_scavenge_time with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"lease_scavenge_time": 86400}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=lease_scavenge_time",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['lease_scavenge_time']
          if (response['inherited']== True and response['value']== 86400 and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 51 Execution Completed")

  
      @pytest.mark.run(order=52)
      def test_052_validating_the_inherited_values_of_authority_at_member_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of authority with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"authority": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=authority",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['authority']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 52 Execution Completed")

      @pytest.mark.run(order=53)
      def test_053_validating_the_inherited_values_of_ignore_dhcp_option_list_at_member_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of ignore_dhcp_option_list with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ignore_dhcp_option_list_request": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=ignore_dhcp_option_list_request",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ignore_dhcp_option_list_request']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 53 Execution Completed")


      @pytest.mark.run(order=54)
      def test_054_validating_the_inherited_values_of_enable_ddns_at_member_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of enable_ddns with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"enable_ddns": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=enable_ddns",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['enable_ddns']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 54 Execution Completed")

      @pytest.mark.run(order=55)
      def test_055_validating_the_inherited_values_of_ddns_domainname_at_member_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of ddns_domainname with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_domainname": "www.infoblox.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=ddns_domainname",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_domainname']
          if (response['inherited']== True and response['value']== "www.infoblox.com" and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 55 Execution Completed")


      @pytest.mark.run(order=56)
      def test_056_validating_the_inherited_values_of_ddns_ttl_at_member_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of ddns_ttl with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_ttl": 500}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=ddns_ttl",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_ttl']
          if (response['inherited']== True and response['value']== 500 and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 56 Execution Completed")                            
                                         

      @pytest.mark.run(order=57)
      def test_057_validating_the_inherited_values_of_ddns_generate_hostname_at_member_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of ddns_generate_hostname with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_generate_hostname": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=ddns_generate_hostname",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_generate_hostname']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 57 Executuion Completed")

      @pytest.mark.run(order=58)
      def test_058_validating_the_inherited_values_of_ddns_update_fixed_addresses_at_member_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of ddns_update_fixed_addresses with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_update_fixed_addresses": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=ddns_update_fixed_addresses",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_update_fixed_addresses']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 58 Executuion Completed")

      @pytest.mark.run(order=59)
      def test_059_validating_the_inherited_values_of_ddns_use_option81_at_member_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of ddns_use_option81 with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_use_option81": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=ddns_use_option81",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_use_option81']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 59 Executuion Completed")

      @pytest.mark.run(order=60)
      def test_060_validating_the_inherited_values_of_update_dns_on_lease_renewal_at_member_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of update_dns_on_lease_renewal with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"update_dns_on_lease_renewal": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=update_dns_on_lease_renewal",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['update_dns_on_lease_renewal']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "member:dhcpproperties" in response['source']):
                 assert True
          else:
                 assert False
          print("Test Case 60 Executuion Completed")

      @pytest.mark.run(order=61)
      def test_061_validating_the_inherited_values_of_enable_dhcp_thresholds_at_member_dhcpproperties_with_network(self):
           logging.info("validating the inherited values of enable_dhcp_thresholds with network")
           get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
           res = json.loads(get_ref)
           ref1 = json.loads(get_ref)[0]['_ref']
           data = {"enable_dhcp_thresholds": True}
           output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
           response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=enable_dhcp_thresholds",grid_vip=config.grid_vip)
           print(response)
           response=json.loads(response)
           response=response[0]['enable_dhcp_thresholds']
           if (response['inherited']== True and response['value']== True and response['multisource']== False and "member:dhcpproperties" in response['source']):
                assert True
           else:
                assert False
           print("Test Case 61 Executuion Completed")

      @pytest.mark.run(order=62)
      def test_062_validating_the_inherited_values_of_pxe_lease_time_at_member_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of pxe_lease_time with network")
          #get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          #res = json.loads(get_ref)
          #ref1 = json.loads(get_ref)[0]['_ref']
          #data = {"pxe_lease_time": 43200}
          #output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          logging.info("Through perl script giving pxe_lease_time value at grid")
          pxe_value = 'perl pxe_lease_time_script_for_member_62.pl {}'.format(config.grid_vip)
          pxe_value1 = os.system(pxe_value)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=pxe_lease_time",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['pxe_lease_time']
          if (response['inherited']== True and response['value']== 43200 and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 62 Execution Completed")


      @pytest.mark.run(order=63)
      def test_063_validating_the_inherited_values_of_deny_bootp_at_member_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of deny_bootp with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"deny_bootp": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=deny_bootp",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['deny_bootp']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 63 Executuion Completed")


      @pytest.mark.run(order=64)
      def test_064_validating_the_inherited_values_of_bootfile_at_member_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of bootfile with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"bootfile": "100"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=bootfile",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['bootfile']
          if (response['inherited']== True and response['value']== "100" and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 64 Execution Completed")

      @pytest.mark.run(order=65)
      def test_065_validating_the_inherited_values_of_nextserver_at_member_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of nextserver with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"nextserver": "www.infoblox.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=nextserver",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['nextserver']
          if (response['inherited']== True and response['value']== "www.infoblox.com" and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 65 Execution Completed")

      @pytest.mark.run(order=66)
      def test_066_validating_the_inherited_values_of_bootserver_at_member_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of bootserver with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"bootserver": "www.infoblox.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=bootserver",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['bootserver']
          if (response['inherited']== True and response['value']== "www.infoblox.com" and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 66 Execution Completed")

      @pytest.mark.run(order=67)
      def test_067_validating_the_inherited_values_of_enable_dhcp_thresholds_at_member_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of enable_dhcp_thresholds with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"enable_dhcp_thresholds": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=enable_dhcp_thresholds",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['enable_dhcp_thresholds']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 67 Executuion Completed")

      @pytest.mark.run(order=68)
      def test_068_validating_the_inherited_values_of_email_list_at_member_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of email_list with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"email_list": ["prasad@gmail.com"]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=email_list",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['email_list']
          if (response['inherited']== True and response['value']== ["prasad@gmail.com"] and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 68 Executuion Completed")


      @pytest.mark.run(order=69)
      def test_069_validating_the_inherited_values_of_logic_filter_rules_at_member_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of logic_filter_rules with network")
          data = {"name": "prasad"}
          response = ib_NIOS.wapi_request('POST', object_type="filtermac", fields=json.dumps(data), grid_vip=config.grid_vip)
          print(response)
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"logic_filter_rules":[{"filter": "prasad","type": "MAC"}]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response1 = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=logic_filter_rules",grid_vip=config.grid_vip)
          print(response1)
          response1=json.loads(response1)
          response1=response1[0]['logic_filter_rules']
          if (response1['inherited']== True and response1['multisource']== False and response1['value']== [{"filter": "prasad","type": "MAC"}] and "member:dhcpproperties" in response1['source']):
                  assert True
          else:
                  assert False
          print("Test Case 69 Executuion Completed")


      @pytest.mark.run(order=70)
      def test_070_validating_the_inherited_values_of_lease_high_water_mark_and_high_water_mark_reset_at_member_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of high_water_mark and high_water_mark_reset with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"high_water_mark": 97,"high_water_mark_reset": 91}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=high_water_mark,high_water_mark_reset",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response1=response[0]['high_water_mark']
          response2=response[0]['high_water_mark_reset']
          if (response1['inherited']== True and response1['value']== 97 and response1['multisource']== False and "grid:dhcpproperties" in response1['source']):
                  assert True
          elif (response2['inherited']== True and response2['value']== 91 and response2['multisource']== False and "member:dhcpproperties" in response2['source']):
                  assert True
          else:
                  assert False
          print("Test Case 70 Executuion Completed")


      @pytest.mark.run(order=71)
      def test_071_validating_the_inherited_values_of_ignore_mac_addresses_at_member_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of ignore_mac_addresses with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ignore_id": "MACADDR","ignore_mac_addresses": ["66:55:44:33:22:11"]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=ignore_mac_addresses",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ignore_mac_addresses']
          if (response['inherited']== True and response['value']== ["66:55:44:33:22:11"] and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 71 Executuion Completed")


      @pytest.mark.run(order=72)
      def test_072_validating_the_inherited_values_of_lease_scavenge_time_at_member_dhcpproperties_with_range(self):
          logging.info("validating the inherited values of lease_scavenge with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"lease_scavenge_time": 259200}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=lease_scavenge_time",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['lease_scavenge_time']
          if (response['inherited']== True and response['value']== 259200 and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 72 Execution Completed")

      @pytest.mark.run(order=73)
      def test_073_validating_the_inherited_values_of_ignore_dhcp_option_list_at_member_dhcpproperties_with_range(self):
          logging.info("validating the inherited values of ignore_dhcp_option_list with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ignore_dhcp_option_list_request": False}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=ignore_dhcp_option_list_request",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ignore_dhcp_option_list_request']
          if (response['inherited']== True and response['value']== False and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 73 Execution Completed")

      @pytest.mark.run(order=74)
      def test_074_validating_the_inherited_values_of_enable_ddns_at_member_dhcpproperties_with_range(self):
          logging.info("validating the inherited values of enable_ddns with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"enable_ddns": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=enable_ddns",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['enable_ddns']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 74 Execution Completed")


      @pytest.mark.run(order=75)
      def test_075_validating_the_inherited_values_of_ddns_domainname_at_member_dhcpproperties_with_range(self):
          logging.info("validating the inherited values of ddns_domainname with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_domainname": "www.domain.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=ddns_domainname",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_domainname']
          if (response['inherited']== True and response['value']== "www.domain.com" and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 75 Execution Completed")


      @pytest.mark.run(order=76)
      def test_076_validating_the_inherited_values_of_ddns_generate_hostname_at_member_dhcpproperties_with_range(self):
          logging.info("validating the inherited values of ddns_generate_hostname with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_generate_hostname": False}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=ddns_generate_hostname",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_generate_hostname']
          if (response['inherited']== True and response['value']== False and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 76 Executuion Completed")


      @pytest.mark.run(order=77)
      def test_077_validating_the_inherited_values_of_update_dns_lease_renewal_at_member_dhcpproperties_with_range(self):
          logging.info("validating the inherited values of update_dns_lease_renewal with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"update_dns_on_lease_renewal": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=update_dns_on_lease_renewal",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['update_dns_on_lease_renewal']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 77 Executuion Completed")


      @pytest.mark.run(order=78)
      def test_078_validating_the_inherited_values_of_pxe_lease_time_at_member_dhcpproperties_with_range(self):
          logging.info("validating the inherited values of pxe_lease_time with range")
          #get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          #res = json.loads(get_ref)
          #ref1 = json.loads(get_ref)[0]['_ref']
          #data = {"pxe_lease_time": 129600}
          #output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          logging.info("Through perl script giving pxe_lease_time value at grid")
          pxe_value = 'perl pxe_lease_time_script_for_member_78.pl {}'.format(config.grid_vip)
          pxe_value1 = os.system(pxe_value)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=pxe_lease_time",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['pxe_lease_time']
          if (response['inherited']== True and response['value']== 129600 and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 78 Execution Completed")


      @pytest.mark.run(order=79)
      def test_079_validating_the_inherited_values_of_deny_bootp_at_member_dhcpproperties_with_range(self):
          logging.info("validating the inherited values of deny_bootp with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"deny_bootp": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=deny_bootp",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['deny_bootp']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 79 Executuion Completed")


      @pytest.mark.run(order=80)
      def test_080_validating_the_inherited_values_of_bootfile_at_member_dhcpproperties_with_range(self):
          logging.info("validating the inherited values of bootfile with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"bootfile": "50"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=bootfile",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['bootfile']
          if (response['inherited']== True and response['value']== "50" and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 80 Execution Completed")


      @pytest.mark.run(order=81)
      def test_081_validating_the_inherited_values_of_nextserver_at_member_dhcpproperties_with_range(self):
          logging.info("validating the inherited values of nextserver with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"nextserver": "www.dns.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=nextserver",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['nextserver']
          if (response['inherited']== True and response['value']== "www.dns.com" and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 81 Execution Completed")


      @pytest.mark.run(order=82)
      def test_082_validating_the_inherited_values_of_bootserver_at_member_dhcpproperties_with_range(self):
          logging.info("validating the inherited values of bootserver with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"bootserver": "www.bootserver.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=bootserver",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['bootserver']
          if (response['inherited']== True and response['value']== "www.bootserver.com" and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 82 Execution Completed")


      @pytest.mark.run(order=83)
      def test_083_validating_the_inherited_values_of_enable_dhcp_thresholds_at_member_dhcpproperties_with_range(self):
          logging.info("validating the inherited values of enable_dhcp_thresholds with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"enable_dhcp_thresholds": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=enable_dhcp_thresholds",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['enable_dhcp_thresholds']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 83 Executuion Completed")


      @pytest.mark.run(order=84)
      def test_084_validating_the_inherited_values_of_email_list_at_member_dhcpproperties_with_range(self):
          logging.info("validating the inherited values of email_list with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"email_list": ["email@gmail.com"]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=email_list",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['email_list']
          if (response['inherited']== True and response['value']== ["email@gmail.com"] and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 84 Executuion Completed")


      @pytest.mark.run(order=85)
      def test_085_validating_the_inherited_values_of_logic_filter_rules_at_member_dhcpproperties_with_range(self):
          logging.info("validating the inherited values of logic_filter_rules with range")
          data = {"name": "filter123"}
          response = ib_NIOS.wapi_request('POST', object_type="filtermac", fields=json.dumps(data), grid_vip=config.grid_vip)
          print(response)
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"logic_filter_rules":[{"filter": "filter123","type": "MAC"}]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response1 = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=logic_filter_rules",grid_vip=config.grid_vip)
          print(response1)
          response1=json.loads(response1)
          response1=response1[0]['logic_filter_rules']
          if (response1['inherited']== True and response1['multisource']== False and response1['value']== [{"filter": "filter123","type": "MAC"}] and "member:dhcpproperties" in response1['source']):
                  assert True
          else:
                  assert False
          print("Test Case 85 Executuion Completed")


      @pytest.mark.run(order=86)
      def test_086_validating_the_inherited_values_of_ignore_mac_addresses_at_member_dhcpproperties_with_range(self):
          logging.info("validating the inherited values of ignore_mac_addresses with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ignore_id": "MACADDR","ignore_mac_addresses": ["99:88:77:66:55:44"]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=ignore_mac_addresses",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ignore_mac_addresses']
          if (response['inherited']== True and response['value']== ["99:88:77:66:55:44"] and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 86 Executuion Completed")


      @pytest.mark.run(order=87)
      def test_087_validating_the_inherited_values_of_enable_ddns_at_member_dhcpproperties_with_fixedaddress(self):
          logging.info("validating the inherited values of enable_ddns with fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"enable_ddns": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=enable_ddns",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['enable_ddns']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 87 Execution Completed")

      @pytest.mark.run(order=88)
      def test_088_validating_the_inherited_values_of_ddns_domainname_at_member_dhcpproperties_with_fixedaddress(self):
          logging.info("validating the inherited values of ddns_domainname with fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_domainname": "www.host.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=ddns_domainname",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_domainname']
          if (response['inherited']== True and response['value']== "www.host.com" and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 88 Execution Completed")


      @pytest.mark.run(order=89)
      def test_089_validating_the_inherited_values_of_pxe_lease_time_at_member_dhcpproperties_with_fixedaddress(self):
          logging.info("validating the inherited values of pxe_lease_time with fixedaddress")
          #get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          #res = json.loads(get_ref)
          #ref1 = json.loads(get_ref)[0]['_ref']
          #data = {"pxe_lease_time": 172800}
          #output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          logging.info("Through perl script giving pxe_lease_time value at grid")
          pxe_value = 'perl pxe_lease_time_script_for_member_89.pl {}'.format(config.grid_vip)
          pxe_value1 = os.system(pxe_value)
          response = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=pxe_lease_time",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['pxe_lease_time']
          if (response['inherited']== True and response['value']== 172800 and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 89 Execution Completed")

  
      @pytest.mark.run(order=90)
      def test_090_validating_the_inherited_values_of_deny_bootp_at_member_dhcpproperties_with_fixedaddress(self):
          logging.info("validating the inherited values of deny_bootp with fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"deny_bootp": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=deny_bootp",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['deny_bootp']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 90 Executuion Completed")

      @pytest.mark.run(order=91)
      def test_091_validating_the_inherited_values_of_bootfile_at_member_dhcpproperties_with_fixedaddress(self):
          logging.info("validating the inherited values of bootfile with fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"bootfile": "550"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=bootfile",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['bootfile']
          if (response['inherited']== True and response['value']== "550" and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 91 Execution Completed")

      @pytest.mark.run(order=92)
      def test_092_validating_the_inherited_values_of_nextserver_at_member_dhcpproperties_with_fixedaddress(self):
          logging.info("validating the inherited values of nextserver with fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"nextserver": "www.nxt.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=nextserver",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['nextserver']
          if (response['inherited']== True and response['value']== "www.nxt.com" and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 92 Execution Completed")


      @pytest.mark.run(order=93)
      def test_093_validating_the_inherited_values_of_bootserver_at_member_dhcpproperties_with_fixedaddress(self):
          logging.info("validating the inherited values of bootserver with fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"bootserver": "www.bt.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=bootserver",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['bootserver']
          if (response['inherited']== True and response['value']== "www.bt.com" and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 93 Execution Completed")


      @pytest.mark.run(order=94)
      def test_094_validating_the_inherited_values_of_logic_filter_rules_at_member_dhcpproperties_with_fixedaddress(self):
          logging.info("validating the inherited values of logic_filter_rules with fixedaddress")
          data = {"name": "mac123"}
          response = ib_NIOS.wapi_request('POST', object_type="filtermac", fields=json.dumps(data), grid_vip=config.grid_vip)
          print(response)
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"logic_filter_rules":[{"filter": "mac123","type": "MAC"}]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response1 = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=logic_filter_rules",grid_vip=config.grid_vip)
          print(response1)
          response1=json.loads(response1)
          response1=response1[0]['logic_filter_rules']
          if (response1['inherited']== True and response1['multisource']== False and response1['value']== [{"filter": "mac123","type": "MAC"}] and "member:dhcpproperties" in response1['source']):
                  assert True
          else:
                  assert False
          print("Test Case 94 Executuion Completed")
                                         
                              
      @pytest.mark.run(order=95)
      def test_095_create_IPv4_network(self):
          logging.info("Create an networkcontainer in default network view")
          data = {"network": "10.0.0.0/8","network_view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="networkcontainer",fields=json.dumps(data), grid_vip=config.grid_vip)
          print(response)
          response1= ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          print(response1)
          response=eval(response1)
          if (response[0].get('network') == "10.0.0.0/8"):
                assert True
          else:
                assert False
          print("Created the ipv4network 10.0.0.0/8 in default view")                           
                                       
                                             
                    
      @pytest.mark.run(order=96)
      def test_096_validating_the_inherited_values_of_lease_scavenge_time_at_networkcontainer_with_network(self):
          logging.info("validating the inherited values of lease_scavenge_time with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"lease_scavenge_time": 432000}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=lease_scavenge_time",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['lease_scavenge_time']
          if (response['inherited']== True and response['value']== 432000 and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 96 Execution Completed")         
                             
                                 
      @pytest.mark.run(order=97)
      def test_097_validating_the_inherited_values_of_authority_at_networkcontainer_with_network(self):
          logging.info("validating the inherited values of authority with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"authority": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=authority",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['authority']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 97 Execution Completed")

      @pytest.mark.run(order=98)
      def test_098_validating_the_inherited_values_of_ignore_dhcp_option_list_at_networkcontainer_with_network(self):
          logging.info("validating the inherited values of dhcp_option_list with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ignore_dhcp_option_list_request": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=ignore_dhcp_option_list_request",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ignore_dhcp_option_list_request']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 98 Execution Completed")

      @pytest.mark.run(order=99)
      def test_099_validating_the_inherited_values_of_enable_ddns_at_networkcontainer_with_network(self):
          logging.info("validating the inherited values of enable_ddns with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"enable_ddns": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=enable_ddns",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['enable_ddns']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 99 Execution Completed")

      @pytest.mark.run(order=100)
      def test_100_validating_the_inherited_values_of_ddns_domainname_at_networkcontainer_with_network(self):
          logging.info("validating the inherited values of ddns_domainname with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_domainname": "www.network_container.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=ddns_domainname",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_domainname']
          if (response['inherited']== True and response['value']== "www.network_container.com" and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 100 Execution Completed")

      @pytest.mark.run(order=101)
      def test_101_validating_the_inherited_values_of_ddns_ttl_at_networkcontainer_with_network(self):
          logging.info("validating the inherited values of ddns_ttl with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_ttl": 700}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=ddns_ttl",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_ttl']
          if (response['inherited']== True and response['value']== 700 and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 101 Execution Completed")


      @pytest.mark.run(order=102)
      def test_102_validating_the_inherited_values_of_ddns_generate_hostname_at_networkcontainer_with_network(self):
          logging.info("validating the inherited values of ddns_generate_hostname with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_generate_hostname": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=ddns_generate_hostname",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_generate_hostname']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 102 Executuion Completed")

      @pytest.mark.run(order=103)
      def test_103_validating_the_inherited_values_of_ddns_update_fixed_addresses_at_networkcontainer_with_network(self):
          logging.info("validating the inherited values of ddns_update_fixed_addresses with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_update_fixed_addresses": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=ddns_update_fixed_addresses",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_update_fixed_addresses']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 103 Executuion Completed")

      @pytest.mark.run(order=104)
      def test_104_validating_the_inherited_values_of_ddns_use_option81_at_networkcontainer_with_network(self):
          logging.info("validating the inherited values of ddns_use_option81 with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_use_option81": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=ddns_use_option81",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_use_option81']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 104 Executuion Completed")

      @pytest.mark.run(order=105)
      def test_105_validating_the_inherited_values_of_update_dns_on_lease_renewal_at_networkcontainer_with_network(self):
          logging.info("validating the inherited values of update_dns_on_lease_renewal with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"update_dns_on_lease_renewal": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=update_dns_on_lease_renewal",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['update_dns_on_lease_renewal']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 105 Executuion Completed")

      @pytest.mark.run(order=106)
      def test_106_validating_the_inherited_values_of_enable_dhcp_thresholds_at_networkcontainer_with_network(self):
          logging.info("validating the inherited values of enable_dhcp_thresholds with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"enable_dhcp_thresholds": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=enable_dhcp_thresholds",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['enable_dhcp_thresholds']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 106 Executuion Completed")

      @pytest.mark.run(order=107)
      def test_107_validating_the_inherited_values_of_pxe_lease_time_at_networkcontainer_with_network(self):
          logging.info("validating the inherited values of pxe_lease_time with network")
          #get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          #res = json.loads(get_ref)
          #ref1 = json.loads(get_ref)[0]['_ref']
          #data = {"pxe_lease_time": 432000}
          #output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          logging.info("Through perl script giving pxe_lease_time value at grid")
          pxe_value = 'perl pxe_lease_time_script_for_network_container_107.pl {}'.format(config.grid_vip)
          pxe_value1 = os.system(pxe_value)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=pxe_lease_time",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['pxe_lease_time']
          if (response['inherited']== True and response['value']== 432000 and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 107 Execution Completed")


      @pytest.mark.run(order=108)
      def test_108_validating_the_inherited_values_of_deny_bootp_at_networkcontainer_with_network(self):
          logging.info("validating the inherited values of deny_bootp with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"deny_bootp": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=deny_bootp",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['deny_bootp']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 108 Executuion Completed")


      @pytest.mark.run(order=109)
      def test_109_validating_the_inherited_values_of_bootfile_at_networkcontainer_with_network(self):
          logging.info("validating the inherited values of bootfile with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"bootfile": "300"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=bootfile",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['bootfile']
          if (response['inherited']== True and response['value']== "300" and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 109 Execution Completed")

      @pytest.mark.run(order=110)
      def test_110_validating_the_inherited_values_of_nextserver_at_networkcontainer_with_network(self):
          logging.info("validating the inherited values of nextserver with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"nextserver": "www.server_container.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=nextserver",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['nextserver']
          if (response['inherited']== True and response['value']== "www.server_container.com" and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 110 Execution Completed")


      @pytest.mark.run(order=111)
      def test_111_validating_the_inherited_values_of_bootserver_at_networkcontainer_with_network(self):
          logging.info("validating the inherited values of bootserver with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"bootserver": "www.server_container.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=bootserver",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['bootserver']
          if (response['inherited']== True and response['value']== "www.server_container.com" and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 111 Execution Completed")

      @pytest.mark.run(order=112)
      def test_112_validating_the_inherited_values_of_enable_dhcp_thresholds_at_networkcontainer_with_network(self):
          logging.info("validating the inherited values of enable_dhcp_thresholds with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"enable_dhcp_thresholds": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=enable_dhcp_thresholds",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['enable_dhcp_thresholds']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 112 Executuion Completed")

      @pytest.mark.run(order=113)
      def test_113_validating_the_inherited_values_of_email_list_at_networkcontainer_with_network(self):
          logging.info("validating the inherited values of email_list with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"email_list": ["gmail@gmail.com"]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=email_list",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['email_list']
          if (response['inherited']== True and response['value']== ["gmail@gmail.com"] and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 113 Executuion Completed")


      @pytest.mark.run(order=114)
      def test_114_validating_the_inherited_values_of_logic_filter_rules_at_networkcontainer_with_network(self):
          logging.info("validating the inherited values of logic_filter_rules with network")
          data = {"name": "container"}
          response = ib_NIOS.wapi_request('POST', object_type="filtermac", fields=json.dumps(data), grid_vip=config.grid_vip)
          print(response)
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"logic_filter_rules":[{"filter": "container","type": "MAC"}]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response1 = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=logic_filter_rules",grid_vip=config.grid_vip)
          print(response1)
          response1=json.loads(response1)
          response1=response1[0]['logic_filter_rules']
          if (response1['inherited']== True and response1['multisource']== False and response1['value']== [{"filter": "container","type": "MAC"}] and "networkcontainer" in response1['source']):
                  assert True
          else:
                  assert False
          print("Test Case 114 Executuion Completed")



      @pytest.mark.run(order=115)
      def test_115_validating_the_inherited_values_of_high_water_mark_and_high_water_mark_reset_at_networkcontainer_with_network(self):
          logging.info("validating the inherited values of high_water_mark and high_water_mark_reset with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"high_water_mark": 94,"high_water_mark_reset": 93}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=high_water_mark,high_water_mark_reset",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response1=response[0]['high_water_mark']
          response2=response[0]['high_water_mark_reset']
          if (response1['inherited']== True and response1['value']== 94 and response1['multisource']== False and "networkcontainer" in response1['source']):
                  assert True
          elif (response2['inherited']== True and response2['value']== 93 and response2['multisource']== False and "networkcontainer" in response2['source']):
                  assert True
          else:
                  assert False
          print("Test Case 115 Executuion Completed")


      @pytest.mark.run(order=116)
      def test_116_validating_the_inherited_values_of_ignore_mac_addresses_at_networkcontainer_with_network(self):
          logging.info("validating the inherited values of ignore_mac_addresses with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ignore_id": "MACADDR","ignore_mac_addresses": ["2a:2b:2c:2d:2e:2f"]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=ignore_mac_addresses",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ignore_mac_addresses']
          if (response['inherited']== True and response['value']== ["2a:2b:2c:2d:2e:2f"] and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 116 Executuion Completed")


      @pytest.mark.run(order=117)
      def test_117_validating_the_inherited_values_of_lease_scavenge_time_at_networkcontainer_with_range(self):
          logging.info("validating the inherited values of lease_scavenge_time with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"lease_scavenge_time": 432000}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=lease_scavenge_time",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['lease_scavenge_time']
          if (response['inherited']== True and response['value']== 432000 and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 117 Execution Completed")

      @pytest.mark.run(order=118)
      def test_118_validating_the_inherited_values_of_ignore_dhcp_option_list_request_at_networkcontainer_with_range(self):
          logging.info("validating the inherited values of ignore_dhcp_option_list_request with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ignore_dhcp_option_list_request": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=ignore_dhcp_option_list_request",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ignore_dhcp_option_list_request']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 118 Execution Completed")

      @pytest.mark.run(order=119)
      def test_119_validating_the_inherited_values_of_enable_ddns_at_networkcontainer_with_range(self):
          logging.info("validating the inherited values of enable_ddns with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"enable_ddns": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=enable_ddns",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['enable_ddns']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 119 Execution Completed")


      @pytest.mark.run(order=120)
      def test_120_validating_the_inherited_values_of_ddns_domainname_at_networkcontainer_with_range(self):
          logging.info("validating the inherited values of ddns_domainname with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_domainname": "www.grid_container.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=ddns_domainname",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_domainname']
          if (response['inherited']== True and response['value']== "www.grid_container.com" and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 120 Execution Completed")


      @pytest.mark.run(order=121)
      def test_121_validating_the_inherited_values_of_ddns_generate_hostname_at_networkcontainer_with_range(self):
          logging.info("validating the inherited values of ddns_generate_hostname with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_generate_hostname": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=ddns_generate_hostname",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_generate_hostname']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 121 Executuion Completed")


      @pytest.mark.run(order=122)
      def test_122_validating_the_inherited_values_of_update_dns_on_lease_renewal_at_networkcontainer_with_range(self):
          logging.info("validating the inherited values of update_dns_on_lease_renewal with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"update_dns_on_lease_renewal": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=update_dns_on_lease_renewal",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['update_dns_on_lease_renewal']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 122 Executuion Completed")



      @pytest.mark.run(order=123)
      def test_123_validating_the_inherited_values_of_pxe_lease_time_at_networkcontainer_with_range(self):
          logging.info("validating the inherited values of pxe_lease_time with range")
          #get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          #res = json.loads(get_ref)
          #ref1 = json.loads(get_ref)[0]['_ref']
          #data = {"pxe_lease_time": 432000}
          #output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          logging.info("Through perl script giving pxe_lease_time value at grid")
          pxe_value = 'perl pxe_lease_time_script_for_network_container_123.pl {}'.format(config.grid_vip)
          pxe_value1 = os.system(pxe_value)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=pxe_lease_time",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['pxe_lease_time']
          if (response['inherited']== True and response['value']== 432000 and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 123 Execution Completed")


      @pytest.mark.run(order=124)
      def test_124_validating_the_inherited_values_of_deny_bootp_at_networkcontainer_with_range(self):
          logging.info("validating the inherited values of deny_bootp with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"deny_bootp": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=deny_bootp",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['deny_bootp']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 124 Executuion Completed")


      @pytest.mark.run(order=125)
      def test_125_validating_the_inherited_values_of_bootfile_at_networkcontainer_with_range(self):
          logging.info("validating the inherited values of bootfile with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"bootfile": "101"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=bootfile",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['bootfile']
          if (response['inherited']== True and response['value']== "101" and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 125 Execution Completed")


      @pytest.mark.run(order=126)
      def test_126_validating_the_inherited_values_of_nextserver_at_networkcontainer_with_range(self):
          logging.info("validating the inherited values of nextserver with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"nextserver": "www.dns_infoblox_container.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=nextserver",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['nextserver']
          if (response['inherited']== True and response['value']== "www.dns_infoblox_container.com" and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 126 Execution Completed")


      @pytest.mark.run(order=127)
      def test_127_validating_the_inherited_values_of_bootserver_at_networkcontainer_with_range(self):
          logging.info("validating the inherited values of bootserver with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"bootserver": "www.bootserver_infoblox_container.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=bootserver",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['bootserver']
          if (response['inherited']== True and response['value']== "www.bootserver_infoblox_container.com" and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 127ecution Completed")


      @pytest.mark.run(order=128)
      def test_128_validating_the_inherited_values_of_enable_dhcp_thresholds_at_networkcontainer_with_range(self):
          logging.info("validating the inherited values of enable_dhcp_thresholds with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"enable_dhcp_thresholds": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=enable_dhcp_thresholds",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['enable_dhcp_thresholds']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 128 Executuion Completed")


      @pytest.mark.run(order=129)
      def test_129_validating_the_inherited_values_of_email_list_at_networkcontainer_with_range(self):
          logging.info("validating the inherited values of email_list with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"email_list": ["email_container@gmail.com"]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=email_list",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['email_list']
          if (response['inherited']== True and response['value']== ["email_container@gmail.com"] and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 129 Executuion Completed")



      @pytest.mark.run(order=130)
      def test_130_validating_the_inherited_values_of_logic_filter_rules_at_networkcontainer_with_range(self):
          logging.info("validating the inherited values of logic_filter_rules with range")
          data = {"name": "infoblox_container"}
          response = ib_NIOS.wapi_request('POST', object_type="filtermac", fields=json.dumps(data), grid_vip=config.grid_vip)
          print(response)
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"logic_filter_rules":[{"filter": "infoblox_container","type": "MAC"}]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response1 = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=logic_filter_rules",grid_vip=config.grid_vip)
          print(response1)
          response1=json.loads(response1)
          response1=response1[0]['logic_filter_rules']
          if (response1['inherited']== True and response1['multisource']== False and response1['value']== [{"filter": "infoblox_container","type": "MAC"}] and "networkcontainer" in response1['source']):
                  assert True
          else:
                  assert False
          print("Test Case 130 Executuion Completed")



      @pytest.mark.run(order=131)
      def test_131_validating_the_inherited_values_of_ignore_mac_addresses_at_networkcontainer_with_range(self):
          logging.info("validating the inherited values of ignore_mac_addresses with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ignore_id": "MACADDR","ignore_mac_addresses": ["22:33:99:88:44:77"]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=ignore_mac_addresses",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ignore_mac_addresses']
          if (response['inherited']== True and response['value']== ["22:33:99:88:44:77"] and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 131 Executuion Completed")


      @pytest.mark.run(order=132)
      def test_132_validating_the_inherited_values_of_enable_ddns_at_networkcontainer_with_fixedaddress(self):
          logging.info("validating the inherited values of enable_ddns with fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"enable_ddns": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=enable_ddns",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['enable_ddns']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 132 Execution Completed")

      @pytest.mark.run(order=133)
      def test_133_validating_the_inherited_values_of_ddns_domainname_at_networkcontainer_with_fixedaddress(self):
          logging.info("validating the inherited values of ddns_domainname with fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_domainname": "www.host_info_blox_container.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=ddns_domainname",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_domainname']
          if (response['inherited']== True and response['value']== "www.host_info_blox_container.com" and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 133 Execution Completed")


      @pytest.mark.run(order=134)
      def test_134_validating_the_inherited_values_of_pxe_lease_time_at_networkcontainer_with_fixedaddress(self):
          logging.info("validating the inherited values of pxe_lease_time with fixedaddress")
          #get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          #res = json.loads(get_ref)
          #ref1 = json.loads(get_ref)[0]['_ref']
          #data = {"pxe_lease_time": 432000}
          #output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          logging.info("Through perl script giving pxe_lease_time value at grid")
          pxe_value = 'perl pxe_lease_time_script_for_network_container_134.pl {}'.format(config.grid_vip)
          pxe_value1 = os.system(pxe_value)
          response = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=pxe_lease_time",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['pxe_lease_time']
          if (response['inherited']== True and response['value']== 432000 and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 134 Execution Completed")


      @pytest.mark.run(order=135)
      def test_135_validating_the_inherited_values_of_deny_bootp_at_networkcontainer_with_fixedaddress(self):
          logging.info("validating the inherited values of deny_bootp with fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"deny_bootp": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=deny_bootp",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['deny_bootp']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 135 Executuion Completed")

      @pytest.mark.run(order=136)
      def test_136_validating_the_inherited_values_of_bootfile_at_networkcontainer_with_fixedaddress(self):
          logging.info("validating the inherited values of bootfile with fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"bootfile": "91"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=bootfile",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['bootfile']
          if (response['inherited']== True and response['value']== "91" and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 136 Execution Completed")

      @pytest.mark.run(order=137)
      def test_137_validating_the_inherited_values_of_nextserver_at_networkcontainer_with_fixedaddress(self):
          logging.info("validating the inherited values of nextserver with fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"nextserver": "www.nxt_infoblox_container.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=nextserver",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['nextserver']
          if (response['inherited']== True and response['value']== "www.nxt_infoblox_container.com" and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 137 Execution Completed")                   
                              

      @pytest.mark.run(order=138)
      def test_138_validating_the_inherited_values_of_bootserver_at_networkcontainer_with_fixedaddress(self):
          logging.info("validating the inherited values of bootserver with fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"bootserver": "www.bt_infoblox_container.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=bootserver",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['bootserver']
          if (response['inherited']== True and response['value']== "www.bt_infoblox_container.com" and response['multisource']== False and "networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 138 Execution Completed")


      @pytest.mark.run(order=139)
      def test_139_validating_the_inherited_values_of_logic_filter_rules_at_networkcontainer_with_fixedaddress(self):
          logging.info("validating the inherited values of logic_filter_rules with fixedaddress")
          data = {"name": "container"}
          response = ib_NIOS.wapi_request('POST', object_type="filtermac", fields=json.dumps(data), grid_vip=config.grid_vip)
          print(response)
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"logic_filter_rules":[{"filter": "container","type": "MAC"}]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response1 = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=logic_filter_rules",grid_vip=config.grid_vip)
          print(response1)
          response1=json.loads(response1)
          response1=response1[0]['logic_filter_rules']
          if (response1['inherited']== True and response1['multisource']== False and response1['value']== [{"filter": "container","type": "MAC"}] and "networkcontainer" in response1['source']):
                  assert True
          else:
                  assert False
          print("Test Case 139 Executuion Completed")
                          
                                      
      @pytest.mark.run(order=140)
      def test_140_validating_the_inherited_values_of_lease_scavenge_time_at_networklevel_with_network(self):
          logging.info("validating the inherited values of lease_scavenge_time with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"lease_scavenge_time": 864000}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=lease_scavenge_time",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['lease_scavenge_time']
          if (response['inherited']== False and response['value']== 864000 and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 140 Execution Completed")



      @pytest.mark.run(order=141)
      def test_141_validating_the_inherited_values_of_authority_at_networklevel_with_network(self):
          logging.info("validating the inherited values of authority with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"authority": False}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=authority",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['authority']
          if (response['inherited']== False and response['value']== False and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 141 Execution Completed")

      @pytest.mark.run(order=142)
      def test_142_validating_the_inherited_values_of_ignore_dhcp_option_list_request_at_networklevel_with_network(self):
          logging.info("validating the inherited values of ignore_dhcp_option_list_request with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ignore_dhcp_option_list_request": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=ignore_dhcp_option_list_request",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ignore_dhcp_option_list_request']
          if (response['inherited']== False and response['value']== True and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 142 Execution Completed")


      @pytest.mark.run(order=143)
      def test_143_validating_the_inherited_values_of_enable_ddns_at_networklevel_with_network(self):
          logging.info("validating the inherited values of enable_ddns with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"enable_ddns": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=enable_ddns",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['enable_ddns']
          if (response['inherited']== False and response['value']== True and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 143 Execution Completed")                    
                            
                          

      @pytest.mark.run(order=144)
      def test_144_validating_the_inherited_values_of_ddns_domainname_at_networklevel_with_network(self):
          logging.info("validating the inherited values of ddns_domainname with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_domainname": "www.network.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=ddns_domainname",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_domainname']
          if (response['inherited']== False and response['value']== "www.network.com" and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 144 Execution Completed")


      @pytest.mark.run(order=145)
      def test_145_validating_the_inherited_values_of_ddns_ttl_at_networklevel_with_network(self):
          logging.info("validating the inherited values of ddns_ttl with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_ttl": 600}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=ddns_ttl",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_ttl']
          if (response['inherited']== False and response['value']== 600 and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 145 Execution Completed")


      @pytest.mark.run(order=146)
      def test_146_validating_the_inherited_values_of_ddns_generate_hostname_at_networklevel_with_network(self):
          logging.info("validating the inherited values of ddns_generate_hostname with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_generate_hostname": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=ddns_generate_hostname",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_generate_hostname']
          if (response['inherited']== False and response['value']== True and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 146 Executuion Completed")

      @pytest.mark.run(order=147)
      def test_147_validating_the_inherited_values_of_ddns_update_fixed_addresses_at_networklevel_with_network(self):
          logging.info("validating the inherited values of ddns_update_fixed_addresses with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_update_fixed_addresses": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=ddns_update_fixed_addresses",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_update_fixed_addresses']
          if (response['inherited']== False and response['value']== True and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 147 Executuion Completed")


      @pytest.mark.run(order=148)
      def test_148_validating_the_inherited_values_of_ddns_use_option81_at_networklevel_with_network(self):
          logging.info("validating the inherited values of ddns_use_option81 with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_use_option81": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=ddns_use_option81",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_use_option81']
          if (response['inherited']== False and response['value']== True and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 148 Executuion Completed")


      @pytest.mark.run(order=149)
      def test_149_validating_the_inherited_values_of_update_dns_on_lease_renewal_at_networklevel_with_network(self):
          logging.info("validating the inherited values of update_dns_on_lease_renewal with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"update_dns_on_lease_renewal": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=update_dns_on_lease_renewal",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['update_dns_on_lease_renewal']
          if (response['inherited']== False and response['value']== True and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 149 Executuion Completed")

      @pytest.mark.run(order=150)
      def test_150_validating_the_inherited_values_of_enable_dhcp_thresholds_at_networklevel_with_network(self):
          logging.info("validating the inherited values of enable_dhcp_thresholds with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"enable_dhcp_thresholds": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=enable_dhcp_thresholds",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['enable_dhcp_thresholds']
          if (response['inherited']== False and response['value']== True and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 150 Executuion Completed")

      @pytest.mark.run(order=151)
      def test_151_validating_the_inherited_values_of_pxe_lease_time_at_networklevel_with_network(self):
          logging.info("validating the inherited values of pxe_lease_time with network")
          #get_ref = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
          #res = json.loads(get_ref)
          #ref1 = json.loads(get_ref)[0]['_ref']
          #data = {"pxe_lease_time": 129600}
          #output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          logging.info("Through perl script giving pxe_lease_time value at grid")
          pxe_value = 'perl pxe_lease_time_script_for_network_151.pl {}'.format(config.grid_vip)
          pxe_value1 = os.system(pxe_value)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=pxe_lease_time",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['pxe_lease_time']
          if (response['inherited']== False and response['value']== 129600 and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 151 Execution Completed")



      @pytest.mark.run(order=152)
      def test_152_validating_the_inherited_values_of_deny_bootp_at_networklevel_with_network(self):
          logging.info("validating the inherited values of deny_bootp with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"deny_bootp": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=deny_bootp",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['deny_bootp']
          if (response['inherited']== False and response['value']== True and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 152 Executuion Completed")


      @pytest.mark.run(order=153)
      def test_153_validating_the_inherited_values_of_bootfile_at_networklevel_with_network(self):
          logging.info("validating the inherited values of bootfile with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"bootfile": "200"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=bootfile",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['bootfile']
          if (response['inherited']== False and response['value']== "200" and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 153 Execution Completed")

      @pytest.mark.run(order=154)
      def test_154_validating_the_inherited_values_of_nextserver_at_networklevel_with_network(self):
          logging.info("validating the inherited values of nextserver with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"nextserver": "www.server.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=nextserver",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['nextserver']
          if (response['inherited']== False and response['value']== "www.server.com" and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 154 Execution Completed")


      @pytest.mark.run(order=155)
      def test_155_validating_the_inherited_values_of_bootserver_at_networklevel_with_network(self):
          logging.info("validating the inherited values of bootserver with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"bootserver": "www.server1.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=bootserver",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['bootserver']
          if (response['inherited']== False and response['value']== "www.server1.com" and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 155 Execution Completed")


      @pytest.mark.run(order=156)
      def test_156_validating_the_inherited_values_of_enable_dhcp_thresholds_at_networklevel_with_network(self):
          logging.info("validating the inherited values of enable_dhcp_thresholds with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"enable_dhcp_thresholds": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=enable_dhcp_thresholds",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['enable_dhcp_thresholds']
          if (response['inherited']== False and response['value']== True and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 156 Executuion Completed")

      @pytest.mark.run(order=157)
      def test_157_validating_the_inherited_values_of_email_list_at_networklevel_with_network(self):
          logging.info("validating the inherited values of email_list with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"email_list": ["mail@gmail.com"]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=email_list",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['email_list']
          if (response['inherited']== False and response['value']== ["mail@gmail.com"] and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 157 Executuion Completed")


      @pytest.mark.run(order=158)
      def test_158_validating_the_inherited_values_of_logic_filter_rules_at_networklevel_with_network(self):
          logging.info("validating the inherited values of logic_filter_rules with network")
          data = {"name": "DNS"}
          response = ib_NIOS.wapi_request('POST', object_type="filtermac", fields=json.dumps(data), grid_vip=config.grid_vip)
          print(response)
          get_ref = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"logic_filter_rules":[{"filter": "DNS","type": "MAC"}]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response1 = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=logic_filter_rules",grid_vip=config.grid_vip)
          print(response1)
          response1=json.loads(response1)
          response1=response1[0]['logic_filter_rules']
          if (response1['inherited']== False and response1['multisource']== False and response1['value']== [{"filter": "DNS","type": "MAC"}] and "" in response1['source']):
                  assert True
          else:
                  assert False
          print("Test Case 158 Executuion Completed")


      @pytest.mark.run(order=159)
      def test_159_validating_the_inherited_values_of_high_water_mark_and_high_water_mark_reset_at_networklevel_with_network(self):
          logging.info("validating the inherited values of high_water_mark and high_water_mark_reset with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"high_water_mark": 93,"high_water_mark_reset": 92}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=high_water_mark,high_water_mark_reset",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response1=response[0]['high_water_mark']
          response2=response[0]['high_water_mark_reset']
          if (response1['inherited']== False and response1['value']== 93 and response1['multisource']== False and "" in response1['source']):
                  assert True
          elif (response2['inherited']== False and response2['value']== 92 and response2['multisource']== False and "" in response2['source']):
                  assert True
          else:
                  assert False
          print("Test Case 159 Executuion Completed")


      @pytest.mark.run(order=160)
      def test_160_validating_the_inherited_values_of_ignore_mac_addresses_at_networklevel_with_network(self):
          logging.info("validating the inherited values of ignore_mac_addresses with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ignore_id": "MACADDR","ignore_mac_addresses": ["1a:1b:1c:1d:1e:1f"]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=ignore_mac_addresses",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ignore_mac_addresses']
          if (response['inherited']== False and response['value']== ["1a:1b:1c:1d:1e:1f"] and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 160 Executuion Completed")


      @pytest.mark.run(order=161)
      def test_161_validating_the_inherited_values_of_lease_scavenge_time_at_rangelevel_with_range(self):
          logging.info("validating the inherited values of lease_scavenge_time with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="range", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"lease_scavenge_time": 345600}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=lease_scavenge_time",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['lease_scavenge_time']
          if (response['inherited']== False and response['value']== 345600 and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 161 Execution Completed")

      @pytest.mark.run(order=162)
      def test_162_validating_the_inherited_values_of_ignore_dhcp_option_list_request__at_rangelevel_with_range(self):
          logging.info("validating the inherited values of ignore_dhcp_option_list_request with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="range", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ignore_dhcp_option_list_request": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=ignore_dhcp_option_list_request",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ignore_dhcp_option_list_request']
          if (response['inherited']== False and response['value']== True and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 162 Execution Completed")


      @pytest.mark.run(order=163)
      def test_163_validating_the_inherited_values_of_enable_ddns_at_rangelevel_with_range(self):
          logging.info("validating the inherited values of enable_ddns with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="range", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"enable_ddns": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=enable_ddns",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['enable_ddns']
          if (response['inherited']== False and response['value']== True and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 163 Execution Completed")



      @pytest.mark.run(order=164)
      def test_164_validating_the_inherited_values_of_ddns_domainname_at_rangelevel_with_range(self):
          logging.info("validating the inherited values of ddns_domainname with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="range", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_domainname": "www.grid.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=ddns_domainname",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_domainname']
          if (response['inherited']== False and response['value']== "www.grid.com" and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 164 Execution Completed")


      @pytest.mark.run(order=165)
      def test_165_validating_the_inherited_values_of_ddns_generate_hostname_at_rangelevel_with_range(self):
          logging.info("validating the inherited values of ddns_generate_hostname with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="range", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_generate_hostname": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=ddns_generate_hostname",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_generate_hostname']
          if (response['inherited']== False and response['value']== True and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 165 Executuion Completed")


      @pytest.mark.run(order=166)
      def test_166_validating_the_inherited_values_of_update_dns_on_lease_renewal_at_rangelevel_with_range(self):
          logging.info("validating the inherited values of update_dns_on_lease_renewal with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="range", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"update_dns_on_lease_renewal": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=update_dns_on_lease_renewal",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['update_dns_on_lease_renewal']
          if (response['inherited']== False and response['value']== True and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 166 Executuion Completed")


      @pytest.mark.run(order=167)
      def test_167_validating_the_inherited_values_of_pxe_lease_time_at_rangelevel_with_range(self):
          logging.info("validating the inherited values of pxe_lease_time with range")
          #get_ref = ib_NIOS.wapi_request('GET', object_type="range", grid_vip=config.grid_vip)
          #res = json.loads(get_ref)
          #ref1 = json.loads(get_ref)[0]['_ref']
          #data = {"pxe_lease_time": 108000}
          #output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          logging.info("Through perl script giving pxe_lease_time value at grid")
          pxe_value = 'perl pxe_lease_time_script_for_range_167.pl {}'.format(config.grid_vip)
          pxe_value1 = os.system(pxe_value)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=pxe_lease_time",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['pxe_lease_time']
          if (response['inherited']== False and response['value']== 108000 and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 167 Execution Completed")


      @pytest.mark.run(order=168)
      def test_168_validating_the_inherited_values_of_deny_bootp_at_rangelevel_with_range(self):
          logging.info("validating the inherited values of deny_bootp with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="range", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"deny_bootp": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=deny_bootp",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['deny_bootp']
          if (response['inherited']== False and response['value']== True and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 168 Executuion Completed")


      @pytest.mark.run(order=169)
      def test_169_validating_the_inherited_values_of_bootfile_at_rangelevel_with_range(self):
          logging.info("validating the inherited values of bootfile with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="range", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"bootfile": "75"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=bootfile",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['bootfile']
          if (response['inherited']== False and response['value']== "75" and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 169 Execution Completed")


      @pytest.mark.run(order=170)
      def test_170_validating_the_inherited_values_of_nextserver_at_rangelevel_with_range(self):
          logging.info("validating the inherited values of nextserver with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="range", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"nextserver": "www.dns_infoblox.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=nextserver",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['nextserver']
          if (response['inherited']== False and response['value']== "www.dns_infoblox.com" and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 170 Execution Completed")


      @pytest.mark.run(order=171)
      def test_171_validating_the_inherited_values_of_bootserver_at_rangelevel_with_range(self):
          logging.info("validating the inherited values of bootserver with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="range", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"bootserver": "www.bootserver_infoblox.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=bootserver",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['bootserver']
          if (response['inherited']== False and response['value']== "www.bootserver_infoblox.com" and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 171 Execution Completed")


      @pytest.mark.run(order=172)
      def test_172_validating_the_inherited_values_of_enable_dhcp_thresholds_at_rangelevel_with_range(self):
          logging.info("validating the inherited values of enable_dhcp_thresholds with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="range", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"enable_dhcp_thresholds": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=enable_dhcp_thresholds",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['enable_dhcp_thresholds']
          if (response['inherited']== False and response['value']== True and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 172 Executuion Completed")


      @pytest.mark.run(order=173)
      def test_173_validating_the_inherited_values_of_email_list_at_rangelevel_with_range(self):
          logging.info("validating the inherited values of email_list with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="range", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"email_list": ["email_infoblox@gmail.com"]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=email_list",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['email_list']
          if (response['inherited']== False and response['value']== ["email_infoblox@gmail.com"] and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 173 Executuion Completed")



      @pytest.mark.run(order=174)
      def test_174_validating_the_inherited_values_of_logic_filter_rules_at_rangelevel_with_range(self):
          logging.info("validating the inherited values of logic_filter_rules with range")
          data = {"name": "infoblox"}
          response = ib_NIOS.wapi_request('POST', object_type="filtermac", fields=json.dumps(data), grid_vip=config.grid_vip)
          print(response)
          get_ref = ib_NIOS.wapi_request('GET', object_type="range", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"logic_filter_rules":[{"filter": "infoblox","type": "MAC"}]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response1 = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=logic_filter_rules",grid_vip=config.grid_vip)
          print(response1)
          response1=json.loads(response1)
          response1=response1[0]['logic_filter_rules']
          if (response1['inherited']== False and response1['multisource']== False and response1['value']== [{"filter": "infoblox","type": "MAC"}] and "" in response1['source']):
                  assert True
          else:
                  assert False
          print("Test Case 174 Executuion Completed")


      @pytest.mark.run(order=175)
      def test_175_validating_the_inherited_values_of_ignore_mac_addresses_at_rangelevel_with_range(self):
          logging.info("validating the inherited values of ignore_mac_addresses with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="range", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ignore_id": "MACADDR","ignore_mac_addresses": ["11:99:22:88:33:77"]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=ignore_mac_addresses",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ignore_mac_addresses']
          if (response['inherited']== False and response['value']== ["11:99:22:88:33:77"] and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 175 Executuion Completed")



      @pytest.mark.run(order=176)
      def test_176_validating_the_inherited_values_of_enable_ddns_at_fixedaddresslevel_with_fixedaddress(self):
          logging.info("validating the inherited values of enable_ddns with fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="fixedaddress", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"enable_ddns": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=enable_ddns",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['enable_ddns']
          if (response['inherited']== False and response['value']== True and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 176 Execution Completed")

      @pytest.mark.run(order=177)
      def test_177_validating_the_inherited_values_of_ddns_domainname_at_fixedaddresslevel_with_fixedaddress(self):
          logging.info("validating the inherited values of ddns_domainname with fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="fixedaddress", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_domainname": "www.host_info_blox.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=ddns_domainname",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_domainname']
          if (response['inherited']== False and response['value']== "www.host_info_blox.com" and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 177 Execution Completed")


      @pytest.mark.run(order=178)
      def test_178_validating_the_inherited_values_of_pxe_lease_time_at_fixedaddresslevel_with_fixedaddress(self):
          logging.info("validating the inherited values of pxe_lease_time with fixedaddress")
          #get_ref = ib_NIOS.wapi_request('GET', object_type="fixedaddress", grid_vip=config.grid_vip)
          #res = json.loads(get_ref)
          #ref1 = json.loads(get_ref)[0]['_ref']
          #data = {"pxe_lease_time": 90000}
          #output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          logging.info("Through perl script giving pxe_lease_time value at grid")
          pxe_value = 'perl pxe_lease_time_script_for_fixedaddr_178.pl {}'.format(config.grid_vip)
          pxe_value1 = os.system(pxe_value)
          response = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=pxe_lease_time",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['pxe_lease_time']
          if (response['inherited']== False and response['value']== 90000 and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 178 Execution Completed")


      @pytest.mark.run(order=179)
      def test_179_validating_the_inherited_values_of_deny_bootp_at_fixedaddresslevel_with_fixedaddress(self):
          logging.info("validating the inherited values of deny_bootp with fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="fixedaddress", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"deny_bootp": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=deny_bootp",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['deny_bootp']
          if (response['inherited']== False and response['value']== True and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 179 Executuion Completed")


      
      @pytest.mark.run(order=180)
      def test_180_validating_the_inherited_values_of_bootfile_at_fixedaddresslevel_with_fixedaddress(self):
          logging.info("validating the inherited values of bootfile with fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="fixedaddress", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"bootfile": "90"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=bootfile",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['bootfile']
          if (response['inherited']== False and response['value']== "90" and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 180 Execution Completed")

      @pytest.mark.run(order=181)
      def test_181_validating_the_inherited_values_of_nextserver_at_fixedaddresslevel_with_fixedaddress(self):
          logging.info("validating the inherited values of nextserver with fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="fixedaddress", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"nextserver": "www.nxt_infoblox.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=nextserver",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['nextserver']
          if (response['inherited']== False and response['value']== "www.nxt_infoblox.com" and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 181 Execution Completed")

      @pytest.mark.run(order=182)
      def test_182_validating_the_inherited_values_of_bootserver_at_fixedaddresslevel_with_fixedaddress(self):
          logging.info("validating the inherited values of bootserver with fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="fixedaddress", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"bootserver": "www.bt_infoblox.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=bootserver",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['bootserver']
          if (response['inherited']== False and response['value']== "www.bt_infoblox.com" and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 182 Execution Completed")


      @pytest.mark.run(order=183)
      def test_183_validating_the_inherited_values_of_logic_filter_rules_at_fixedaddresslevel_with_fixedaddress(self):
          logging.info("validating the inherited values of logic_filter_rules with fixedaddress")
          data = {"name": "infoblox123"}
          response = ib_NIOS.wapi_request('POST', object_type="filtermac", fields=json.dumps(data), grid_vip=config.grid_vip)
          print(response)
          get_ref = ib_NIOS.wapi_request('GET', object_type="fixedaddress", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"logic_filter_rules":[{"filter": "infoblox123","type": "MAC"}]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response1 = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=logic_filter_rules",grid_vip=config.grid_vip)
          print(response1)
          response1=json.loads(response1)
          response1=response1[0]['logic_filter_rules']
          if (response1['inherited']== False and response1['multisource']== False and response1['value']== [{"filter": "infoblox123","type": "MAC"}] and "" in response1['source']):
                  assert True
          else:
                  assert False
          print("Test Case 183 Executuion Completed")

      @pytest.mark.run(order=184)
      def test_184_create_IPv6_network(self):
          logging.info("Create an ipv6 network in default network view")
          data = {"network":"fd81:12be:2c71:5d14::/64","network_view": "default","members":[{"_struct": "dhcpmember","ipv4addr":config.grid_vip}]}
          response = ib_NIOS.wapi_request('POST', object_type="ipv6network", fields=json.dumps(data), grid_vip=config.grid_vip)
          print(response)
          print("Created the ipv6network fd81:12be:2c71:5d14::/64 in default view")
          logging.info("Restart DHCP Services")
          grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
          ref = json.loads(grid)[0]['_ref']
          data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
          request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
          sleep(20) #wait for 20 secs for the member to get started
          response1 = ib_NIOS.wapi_request('GET', object_type="ipv6network", grid_vip=config.grid_vip)
          response=eval(response1)
          if (response[0].get('network') == "fd81:12be:2c71:5d14::/64"):
          	assert True
          else:
          	assert False
          print("Test Case 184 Execution Completed")

      @pytest.mark.run(order=185)
      def test_185_create_IPv6_Range(self):
          logging.info("Create an IPv6 range in defaultnetwork view")
          data = {"end_addr": "fd81:12be:2c71:5d14::10","network": "fd81:12be:2c71:5d14::/64","network_view": "default","start_addr": "fd81:12be:2c71:5d14::1"}
          response = ib_NIOS.wapi_request('POST', object_type="ipv6range", fields=json.dumps(data), grid_vip=config.grid_vip)
          print (response)
          print("Created the ipv6 prefix range with bits 64  in default view")
          logging.info("Restart DHCP Services")
          grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
          ref = json.loads(grid)[0]['_ref']
          data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
          request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
          sleep(20) #wait for 20 secs for the member to get started
          response1 = ib_NIOS.wapi_request('GET', object_type="ipv6range", grid_vip=config.grid_vip)
          response=eval(response1)
          if (response[0].get('start_addr') == "fd81:12be:2c71:5d14::1" and response[0].get('end_addr') == "fd81:12be:2c71:5d14::10"):
          	assert True
          else:
          	assert False
          print("Test Case 185 Execution Completed")

      @pytest.mark.run(order=186)
      def test_186_validating_the_inherited_values_of_valid_lifetime_at_grid_dhcpproperties_with_ipv6network(self):
          logging.info("validating the inherited values of valid_lifetime with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"use_valid_lifetime": False}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          sleep(7)
          print(output)
          get_ref1 = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res1 = json.loads(get_ref1)
          ref2 = json.loads(get_ref1)[0]['_ref']
          data1 = {"valid_lifetime": 90000}
          output1 = ib_NIOS.wapi_request('PUT',ref=ref2,fields=json.dumps(data1),grid_vip=config.grid_vip)
          sleep(10)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=valid_lifetime",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['valid_lifetime']
          if (response['inherited']== True and response['value']== 90000 and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 186 Execution Completed")

      @pytest.mark.run(order=187)
      def test_187_validating_the_inherited_values_of_preferred_lifetime_at_grid_dhcpproperties_with_ipv6network(self):
          logging.info("validating the inherited values of preferred_lifetime  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"preferred_lifetime": 150}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=preferred_lifetime",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['preferred_lifetime']
          if (response['inherited']== True and response['value']== 150 and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 187 Execution Completed")

      @pytest.mark.run(order=188)
      def test_188_validating_the_inherited_values_of_domain_name_at_grid_dhcpproperties_with_ipv6network(self):
          logging.info("validating the inherited values of domain_name  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ipv6_domain_name": "www.domain.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=domain_name",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['domain_name']
          if (response['inherited']== True and response['value']== "www.domain.com" and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 188 Execution Completed")


      @pytest.mark.run(order=189)
      def test_189_validating_the_inherited_values_of_domain_name_servers_at_grid_dhcpproperties_with_ipv6network(self):
          logging.info("validating the inherited values of domain_name_servers  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ipv6_domain_name_servers": ["fd81:12be:2c71:5d14::13"]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=domain_name_servers",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['domain_name_servers']
          if (response['inherited']== True and response['value']== ["fd81:12be:2c71:5d14::13"] and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 189 Execution Completed")

      @pytest.mark.run(order=190)
      def test_190_validating_the_inherited_values_of_enable_ddns_at_grid_dhcpproperties_with_ipv6network(self):
          logging.info("validating the inherited values of enable_ddns  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ipv6_enable_ddns": False}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=enable_ddns",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['enable_ddns']
          if (response['inherited']== True and response['value']== False and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 190 Execution Completed")

      @pytest.mark.run(order=191)
      def test_191_validating_the_inherited_values_of_ddns_domainname_at_grid_dhcpproperties_with_ipv6network(self):
          logging.info("validating the inherited values of ddns_domainname  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ipv6_ddns_domainname": "www.infoblox.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=ddns_domainname",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_domainname']
          if (response['inherited']== True and response['value']== "www.infoblox.com" and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 191 Execution Completed")


      @pytest.mark.run(order=192)
      def test_192_validating_the_inherited_values_of_ddns_ttl_at_grid_dhcpproperties_with_ipv6network(self):
          logging.info("validating the inherited values of ddns_ttl  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ipv6_ddns_ttl": 100}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=ddns_ttl",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_ttl']
          if (response['inherited']== True and response['value']== 100 and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 192 Execution Completed")


      @pytest.mark.run(order=193)
      def test_193_validating_the_inherited_values_of_ddns_generate_hostname_at_grid_dhcpproperties_with_ipv6network(self):
          logging.info("validating the inherited values of ddns_generate_hostname  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ipv6_generate_hostname": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=ddns_generate_hostname",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_generate_hostname']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 193 Executuion Completed")

      @pytest.mark.run(order=194)
      def test_194_validating_the_inherited_values_of_ddns_enable_option_fqdn_at_grid_dhcpproperties_with_ipv6network(self):
          logging.info("validating the inherited values of ddns_enable_option_fqdn  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ipv6_ddns_enable_option_fqdn": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=ddns_enable_option_fqdn",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_enable_option_fqdn']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 194 Executuion Completed")

      @pytest.mark.run(order=195)
      def test_195_validating_the_inherited_values_of_update_dns_on_lease_renewal_at_grid_dhcpproperties_with_ipv6network(self):
          logging.info("validating the inherited values of update_dns_on_lease_renewal  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ipv6_update_dns_on_lease_renewal": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=update_dns_on_lease_renewal",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['update_dns_on_lease_renewal']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 195 Executuion Completed")


      @pytest.mark.run(order=196)
      def test_196_create_ipv6fixedaddress(self):
          logging.info("Create an ipv6 fixedaddress in default network view")
          data = {"duid": "11:22:33:bb:cc:aa","ipv6addr": "fd81:12be:2c71:5d14::11","network_view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="ipv6fixedaddress", fields=json.dumps(data), grid_vip=config.grid_vip)
          print(response)
          response1 = ib_NIOS.wapi_request('GET', object_type="ipv6fixedaddress", grid_vip=config.grid_vip)
          print(response1)
          response=eval(response1)
          if (response[0].get('ipv6addr') == "fd81:12be:2c71:5d14::11" and response[0].get('duid') == "11:22:33:bb:cc:aa"):
          	assert True
          else:
          	assert False
          print("Test Case 196 Execution Completed")


      @pytest.mark.run(order=197)
      def test_197_validating_the_inherited_values_of_valid_lifetime_at_grid_dhcpproperties_with_ipv6fixedaddress(self):
          logging.info("validating the inherited values of valid_lifetime  with ipv6fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"valid_lifetime": 200}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6fixedaddress",params="?_inheritance=True&_return_fields=valid_lifetime",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['valid_lifetime']
          if (response['inherited']== True and response['value']== 200 and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 197 Execution Completed")

      @pytest.mark.run(order=198)
      def test_198_validating_the_inherited_values_of_preferred_lifetime_at_grid_dhcpproperties_with_ipv6fixedaddress(self):
          logging.info("validating the inherited values of preferred_lifetime  with ipv6fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"preferred_lifetime": 160}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6fixedaddress",params="?_inheritance=True&_return_fields=preferred_lifetime",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['preferred_lifetime']
          if (response['inherited']== True and response['value']== 160 and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 198 Execution Completed")

      @pytest.mark.run(order=199)
      def test_199_validating_the_inherited_values_of_domain_name_at_grid_dhcpproperties_with_ipv6fixedaddress(self):
          logging.info("validating the inherited values of domain_name with ipv6fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ipv6_domain_name": "www.domainname.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6fixedaddress",params="?_inheritance=True&_return_fields=domain_name",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['domain_name']
          if (response['inherited']== True and response['value']== "www.domainname.com" and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 199 Execution Completed")


      @pytest.mark.run(order=200)
      def test_200_validating_the_inherited_values_of_domain_name_servers_at_grid_dhcpproperties_with_ipv6fixedaddress(self):
          logging.info("validating the inherited values of domain_name  with ipv6fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ipv6_domain_name_servers": ["fd81:12be:2c71:5d14::14"]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6fixedaddress",params="?_inheritance=True&_return_fields=domain_name_servers",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['domain_name_servers']
          if (response['inherited']== True and response['value']== ["fd81:12be:2c71:5d14::14"] and response['multisource']== False and "grid:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 200 Execution Completed")


      @pytest.mark.run(order=201)
      def test_201_validating_the_inherited_values_of_valid_lifetime_at_member_dhcpproperties_with_ipv6network(self):
          logging.info("validating the inherited values of valid_lifetime  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"valid_lifetime": 200}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=valid_lifetime",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['valid_lifetime']
          if (response['inherited']== True and response['value']== 200 and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 201 Execution Completed")



      @pytest.mark.run(order=202)
      def test_202_validating_the_inherited_values_of_preferred_lifetime_at_member_dhcpproperties_with_ipv6network(self):
          logging.info("validating the inherited values of preferred_lifetime  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"preferred_lifetime": 101}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=preferred_lifetime",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['preferred_lifetime']
          if (response['inherited']== True and response['value']== 101 and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 202 Execution Completed")

      @pytest.mark.run(order=203)
      def test_203_validating_the_inherited_values_of_domain_name_at_member_dhcpproperties_with_ipv6network(self):
          logging.info("validating the inherited values of domain_name  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ipv6_domain_name": "www.domainmember.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=domain_name",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['domain_name']
          if (response['inherited']== True and response['value']== "www.domainmember.com" and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 203 Execution Completed")

      @pytest.mark.run(order=204)
      def test_204_validating_the_inherited_values_of_domain_name_servers_at_member_dhcpproperties_with_ipv6network(self):
          logging.info("validating the inherited values of domain_name_servers  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ipv6_domain_name_servers": ["fd81:12be:2c71:5d14::14"]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=domain_name_servers",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['domain_name_servers']
          if (response['inherited']== True and response['value']== ["fd81:12be:2c71:5d14::14"] and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 204 Execution Completed")

      @pytest.mark.run(order=205)
      def test_205_validating_the_inherited_values_of_enable_ddns_at_member_dhcpproperties_with_ipv6network(self):
          logging.info("validating the inherited values of enable_ddns  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ipv6_enable_ddns": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=enable_ddns",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['enable_ddns']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 205 Execution Completed")

      @pytest.mark.run(order=206)
      def test_206_validating_the_inherited_values_of_ddns_domainname_at_member_dhcpproperties_with_ipv6network(self):
          logging.info("validating the inherited values of ddns_domainname  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ipv6_ddns_domainname": "www.infobloxmember.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=ddns_domainname",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_domainname']
          if (response['inherited']== True and response['value']== "www.infobloxmember.com" and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 206 Execution Completed")


      @pytest.mark.run(order=207)
      def test_207_validating_the_inherited_values_of_ddns_ttl_at_member_dhcpproperties_with_ipv6network(self):
          logging.info("validating the inherited values of ddns_ttl  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ipv6_ddns_ttl": 102}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=ddns_ttl",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_ttl']
          if (response['inherited']== True and response['value']== 102 and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 207 Execution Completed")

      @pytest.mark.run(order=208)
      def test_208_validating_the_inherited_values_of_ddns_generate_hostname_at_member_dhcpproperties_with_ipv6network(self):
          logging.info("validating the inherited values of ddns_generate_hostname  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ipv6_generate_hostname": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=ddns_generate_hostname",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_generate_hostname']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 208 Executuion Completed")

      @pytest.mark.run(order=209)
      def test_209_validating_the_inherited_values_of_ddns_enable_option_fqdn_at_member_dhcpproperties_with_ipv6network(self):
          logging.info("validating the inherited values of ddns_enable_option_fqdn  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ipv6_ddns_enable_option_fqdn": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=ddns_enable_option_fqdn",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_enable_option_fqdn']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 209 Executuion Completed")


      @pytest.mark.run(order=210)
      def test_210_validating_the_inherited_values_of_update_dns_on_lease_renewal_at_member_dhcpproperties_with_ipv6network(self):
          logging.info("validating the inherited values of update_dns_on_lease_renewal  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ipv6_update_dns_on_lease_renewal": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=update_dns_on_lease_renewal",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['update_dns_on_lease_renewal']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 210 Executuion Completed")

      @pytest.mark.run(order=211)
      def test_211_validating_the_inherited_values_of_valid_lifetime_at_member_dhcpproperties_with_ipv6fixedaddress(self):
          logging.info("validating the inherited values of valid_lifetime  with ipv6fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"valid_lifetime": 201}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6fixedaddress",params="?_inheritance=True&_return_fields=valid_lifetime",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['valid_lifetime']
          if (response['inherited']== True and response['value']== 201 and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 211 Execution Completed")

      @pytest.mark.run(order=212)
      def test_212_validating_the_inherited_values_of_preferred_lifetime_at_member_dhcpproperties_with_ipv6fixedaddress(self):
          logging.info("validating the inherited values of preferred_lifetime  with ipv6fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"preferred_lifetime": 161}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6fixedaddress",params="?_inheritance=True&_return_fields=preferred_lifetime",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['preferred_lifetime']
          if (response['inherited']== True and response['value']== 161 and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 212 Execution Completed")


      @pytest.mark.run(order=213)
      def test_213_validating_the_inherited_values_of_domain_name_at_member_dhcpproperties_with_ipv6fixedaddress(self):
          logging.info("validating the inherited values of domain_name  with ipv6fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ipv6_domain_name": "www.domainnamemember.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6fixedaddress",params="?_inheritance=True&_return_fields=domain_name",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['domain_name']
          if (response['inherited']== True and response['value']== "www.domainnamemember.com" and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 213 Execution Completed")


      @pytest.mark.run(order=214)
      def test_214_validating_the_inherited_values_of_domain_name_servers_at_member_dhcpproperties_with_ipv6fixedaddress(self):
          logging.info("validating the inherited values of domain_name_servers  with ipv6fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ipv6_domain_name_servers": ["fd81:12be:2c71:5d14::16"]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6fixedaddress",params="?_inheritance=True&_return_fields=domain_name_servers",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['domain_name_servers']
          if (response['inherited']== True and response['value']== ["fd81:12be:2c71:5d14::16"] and response['multisource']== False and "member:dhcpproperties" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 214 Execution Completed")


      @pytest.mark.run(order=215)
      def test_215_create_IPv6networkcontainer(self):
          logging.info("Create an ipv6 network container in  default network view")
          data = {"network": "fd81:12be:2c71:5d14::/62","network_view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="ipv6networkcontainer",fields=json.dumps(data), grid_vip=config.grid_vip)
          print(response)
          response1 = ib_NIOS.wapi_request('GET', object_type="ipv6networkcontainer", grid_vip=config.grid_vip)
          print(response1)
          response=eval(response1)
          if (response[0].get('network') == "fd81:12be:2c71:5d14::/62"):
          	assert True
          else:
          	assert False
          logging.info("Created the ipv6networkcontainer fd81:12be:2c71:5d14::/62 in default view")
          print("Test Case 215 Execution Completed") 

      @pytest.mark.run(order=216)
      def test_216_validating_the_inherited_values_of_valid_lifetime_at_ipv6networkcontainer_with_ipv6network(self):
          logging.info("validating the inherited values of valid_lifetime  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print(ref1)
          data = {"valid_lifetime": 100000}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=valid_lifetime",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['valid_lifetime']
          if (response['inherited']== True and response['value']== 100000 and response['multisource']== False and "ipv6networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 216 Execution Completed")



      @pytest.mark.run(order=217)
      def test_217_validating_the_inherited_values_of_preferred_lifetime_at_ipv6networkcontainer_with_ipv6network(self):
          logging.info("validating the inherited values of preferred_lifetime  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"preferred_lifetime": 1000}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=preferred_lifetime",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['preferred_lifetime']
          if (response['inherited']== True and response['value']== 1000 and response['multisource']== False and "ipv6networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 217 Execution Completed")


      @pytest.mark.run(order=218)
      def test_218_validating_the_inherited_values_of_domain_name_servers_at_ipv6networkcontainer_with_ipv6network(self):
          logging.info("validating the inherited values of domain_name_servers  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"domain_name_servers": ["fd81:12be:2c71:5d14::18"]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=domain_name_servers",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['domain_name_servers']
          if (response['inherited']== True and response['value']== ["fd81:12be:2c71:5d14::18"] and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 218 Execution Completed")

      @pytest.mark.run(order=219)
      def test_219_validating_the_inherited_values_of_enable_ddns_at_ipv6networkcontainer_with_ipv6network(self):
          logging.info("validating the inherited values of enable_ddns  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"enable_ddns": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=enable_ddns",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['enable_ddns']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "ipv6networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 219 Execution Completed")

      @pytest.mark.run(order=220)
      def test_220_validating_the_inherited_values_of_ddns_domainname_at_ipv6networkcontainer_with_ipv6network(self):
          logging.info("validating the inherited values of ddns_domainname  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_domainname": "www.networkcontainer.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=ddns_domainname",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_domainname']
          if (response['inherited']== True and response['value']== "www.networkcontainer.com" and response['multisource']== False and "ipv6networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 220 Execution Completed")


      @pytest.mark.run(order=221)
      def test_221_validating_the_inherited_values_of_ddns_ttl_at_ipv6networkcontainer_with_ipv6network(self):
          logging.info("validating the inherited values of ddns_ttl  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_ttl": 104}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=ddns_ttl",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_ttl']
          if (response['inherited']== True and response['value']== 104 and response['multisource']== False and "ipv6networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 221 Execution Completed")


      @pytest.mark.run(order=222)
      def test_222_validating_the_inherited_values_of_ddns_generate_hostname_at_ipv6networkcontainer_with_ipv6network(self):
          logging.info("validating the inherited values of ddns_generate_hostname  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_generate_hostname": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=ddns_generate_hostname",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_generate_hostname']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "ipv6networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 222 Executuion Completed")

      @pytest.mark.run(order=223)
      def test_223_validating_the_inherited_values_of_ddns_enable_option_fqdn_at_ipv6networkcontainer_with_ipv6network(self):
          logging.info("validating the inherited values of ddns_enable_option_fqdn  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_enable_option_fqdn": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=ddns_enable_option_fqdn",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_enable_option_fqdn']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "ipv6networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 223 Executuion Completed")

      @pytest.mark.run(order=224)
      def test_224_validating_the_inherited_values_of_update_dns_on_lease_renewal_at_ipv6networkcontainer_with_ipv6network(self):
          logging.info("validating the inherited values of update_dns_on_lease_renewal  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"update_dns_on_lease_renewal": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=update_dns_on_lease_renewal",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['update_dns_on_lease_renewal']
          if (response['inherited']== True and response['value']== True and response['multisource']== False and "ipv6networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 224 Executuion Completed")

      @pytest.mark.run(order=225)
      def test_225_validating_the_inherited_values_of_valid_lifetime_at_ipv6networkcontainer_with_ipv6fixedaddress(self):
          logging.info("validating the inherited values of valid_lifetime  with ipv6fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"valid_lifetime": 1002}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6fixedaddress",params="?_inheritance=True&_return_fields=valid_lifetime",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['valid_lifetime']
          if (response['inherited']== True and response['value']== 1002 and response['multisource']== False and "ipv6networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 225 Execution Completed")

      @pytest.mark.run(order=226)
      def test_226_validating_the_inherited_values_of_preferred_lifetime_at_ipv6networkcontainer_with_ipv6fixedaddress(self):
          logging.info("validating the inherited values of preferred_lifetime  with ipv6fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"preferred_lifetime": 1001}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6fixedaddress",params="?_inheritance=True&_return_fields=preferred_lifetime",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['preferred_lifetime']
          if (response['inherited']== True and response['value']== 1001 and response['multisource']== False and "ipv6networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 226 Execution Completed")




      @pytest.mark.run(order=227)
      def test_227_validating_the_inherited_values_of_domain_name_servers_at_ipv6networkcontainer_with_ipv6fixedaddress(self):
          logging.info("validating the inherited values of domain_name_servers  with ipv6fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"domain_name_servers": ["fd81:12be:2c71:5d14::19"]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6fixedaddress",params="?_inheritance=True&_return_fields=domain_name_servers",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['domain_name_servers']
          if (response['inherited']== True  and response['value']== ["fd81:12be:2c71:5d14::19"] and response['multisource']== False and "ipv6networkcontainer" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 227 Execution Completed")


      @pytest.mark.run(order=228)
      def test_228_validating_the_inherited_values_of_valid_lifetime_at_ipv6networklevel_with_ipv6network(self):
          logging.info("validating the inherited values of valid_lifetime  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"valid_lifetime": 199}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=valid_lifetime",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['valid_lifetime']
          if (response['inherited']== False and response['value']== 199 and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 228 Execution Completed")



      @pytest.mark.run(order=229)
      def test_229_validating_the_inherited_values_of_preferred_lifetime_at_ipv6networklevel_with_ipv6network(self):
          logging.info("validating the inherited values of preferred_lifetime  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"preferred_lifetime": 102}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=preferred_lifetime",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['preferred_lifetime']
          if (response['inherited']== False and response['value']== 102 and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 229 Execution Completed")

      @pytest.mark.run(order=230)
      def test_230_validating_the_inherited_values_of_domain_name_at_ipv6networklevel_with_ipv6network(self):
          logging.info("validating the inherited values of domain_name with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"domain_name": "www.networkdomain.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=domain_name",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['domain_name']
          if (response['inherited']== False and response['value']== "www.networkdomain.com" and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 230 Execution Completed")


      @pytest.mark.run(order=231)
      def test_231_validating_the_inherited_values_of_domain_name_servers_at_ipv6networklevel_with_ipv6network(self):
          logging.info("validating the inherited values of domain_name_servers  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"domain_name_servers": ["fd81:12be:2c71:5d14::17"]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=domain_name_servers",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['domain_name_servers']
          if (response['inherited']== False and response['value']== ["fd81:12be:2c71:5d14::17"] and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 231 Execution Completed")


      @pytest.mark.run(order=232)
      def test_232_validating_the_inherited_values_of_enable_ddns_at_ipv6networklevel_with_ipv6network(self):
          logging.info("validating the inherited values of enable_ddns  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"enable_ddns": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=enable_ddns",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['enable_ddns']
          if (response['inherited']== False and response['value']== True and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 232 Execution Completed")

      @pytest.mark.run(order=233)
      def test_233_validating_the_inherited_values_of_ddns_domainname_at_ipv6networklevel_with_ipv6network(self):
          logging.info("validating the inherited values of ddns_domainname  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_domainname": "www.network.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=ddns_domainname",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_domainname']
          if (response['inherited']== False and response['value']== "www.network.com" and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 233 Execution Completed")


      @pytest.mark.run(order=234)
      def test_234_validating_the_inherited_values_of_ddns_ttl_at_ipv6networklevel_with_ipv6network(self):
          logging.info("validating the inherited values of ddns_ttl  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_ttl": 103}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=ddns_ttl",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_ttl']
          if (response['inherited']== False and response['value']== 103 and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 234 Execution Completed")


      @pytest.mark.run(order=235)
      def test_235_validating_the_inherited_values_of_ddns_generate_hostname_at_ipv6networklevel_with_ipv6network(self):
          logging.info("validating the inherited values od ddns_generate_hostname  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_generate_hostname": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=ddns_generate_hostname",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_generate_hostname']
          if (response['inherited']== False and response['value']== True and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 235 Executuion Completed")


      @pytest.mark.run(order=236)
      def test_236_validating_the_inherited_values_of_ddns_enable_option_fqdn_at_ipv6networklevel_with_ipv6network(self):
          logging.info("validating the inherited values of ddns_enable_option_fqdn  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ddns_enable_option_fqdn": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=ddns_enable_option_fqdn",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['ddns_enable_option_fqdn']
          if (response['inherited']== False and response['value']== True and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 236 Executuion Completed")


      @pytest.mark.run(order=237)
      def test_237_validating_the_inherited_values_of_update_dns_on_lease_renewal_at_ipv6networklevel_with_ipv6network(self):
          logging.info("validating the inherited values of update_dns_on_lease_renewal  with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"update_dns_on_lease_renewal": True}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=update_dns_on_lease_renewal",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['update_dns_on_lease_renewal']
          if (response['inherited']== False and response['value']== True and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 237 Executuion Completed")

      @pytest.mark.run(order=238)
      def test_238_validating_the_inherited_values_of_valid_lifetime_at_ipv6fixedaddresslevel_with_ipv6fixedaddress(self):
          logging.info("validating the inherited values of valid_lifetime  with ipv6fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6fixedaddress", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"valid_lifetime": 202}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6fixedaddress",params="?_inheritance=True&_return_fields=valid_lifetime",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['valid_lifetime']
          if (response['inherited']== False and response['value']== 202 and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 238 Execution Completed")

      @pytest.mark.run(order=239)
      def test_239_validating_the_inherited_values_of_preferred_lifetime_at_ipv6fixedaddresslevel_with_ipv6fixedaddress(self):
          logging.info("validating the inherited values of preferred_lifetime  with ipv6fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6fixedaddress", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"preferred_lifetime": 162}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6fixedaddress",params="?_inheritance=True&_return_fields=preferred_lifetime",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['preferred_lifetime']
          if (response['inherited']== False and response['value']== 162 and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 239 Execution Completed")


      @pytest.mark.run(order=240)
      def test_240_validating_the_inherited_values_of_domain_name_at_ipv6fixedaddresslevel_with_ipv6fixedaddress(self):
          logging.info("validating the inherited values of domain_name  with ipv6fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6fixedaddress", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"domain_name": "www.domainnetwork.com"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6fixedaddress",params="?_inheritance=True&_return_fields=domain_name",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['domain_name']
          if (response['inherited']== False and response['value']== "www.domainnetwork.com" and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 240 Execution Completed")

      @pytest.mark.run(order=241)
      def test_241_validating_the_inherited_values_of_domain_name_servers_at_ipv6fixedaddresslevel_with_ipv6fixedaddress(self):
          logging.info("validating the inherited values of domain_name_servers  with ipv6fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6fixedaddress", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"domain_name_servers": ["fd81:12be:2c71:5d14::17"]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6fixedaddress",params="?_inheritance=True&_return_fields=domain_name_servers",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['domain_name_servers']
          if (response['inherited']== False  and response['value']== ["fd81:12be:2c71:5d14::17"] and response['multisource']== False and "" in response['source']):
                  assert True
          else:
                  assert False
          print("Test Case 241 Execution Completed")


      @pytest.mark.run(order=242)
      def test_242_validating_the_inherited_values_of_ipv4_custom_dhcpoptions_at_grid_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of ipv4_custom_dhcpoptions with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"options": [{"name": "host-name","num": 12,"value": "stringer","vendor_class": "DHCP"}]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          sleep(5)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=options",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['options']
          #print(response)
          if (response[0]['inherited']== True and "grid:dhcpproperties" in response[0]['source'] and response[0]['values'][0]['num']== 12 and response[0]['values'][0]['value']=="stringer" and response[0]['values'][0]['name']=="host-name"):
                  assert True
          else:
                  assert False
          print("Test Case 242 Execution Completed")

      @pytest.mark.run(order=243)
      def test_243_validating_the_inherited_values_of_ipv4_custom_dhcpoptions_at_grid_dhcpproperties_with_range(self):
          logging.info("validating the inherited values of ipv4_custom_dhcpoptions with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"options": [{"name": "merit-dump","num": 14,"value": "text","vendor_class": "DHCP"}]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          sleep(5)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=options",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['options']
          #print(response)
          if (response[0]['inherited']== True and "grid:dhcpproperties" in response[0]['source'] and response[0]['values'][0]['num']== 14 and response[0]['values'][0]['value']== "text" and response[0]['values'][0]['name']== "merit-dump"):
                  assert True
          else:
                  assert False
          print("Test Case 243 Execution Completed")


      @pytest.mark.run(order=244)
      def test_244_validating_the_inherited_values_of_ipv4_custom_dhcpoptions_at_grid_dhcpproperties_with_fixedaddress(self):
          logging.info("validating the inherited values of ipv4_custom_dhcpoptions with fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"options": [{"name": "root-path","num": 17,"value": "fixedtext","vendor_class": "DHCP"}]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          sleep(5)
          response = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=options",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['options']
          #print(response)
          if (response[0]['inherited']== True and "grid:dhcpproperties" in response[0]['source'] and response[0]['values'][0]['num']== 17and response[0]['values'][0]['value']=="fixedtext" and response[0]['values'][0]['name']=="root-path"):
                  assert True
          else:
                  assert False
          print("Test Case 244 Execution Completed")


      @pytest.mark.run(order=245)
      def test_245_validating_the_inherited_values_of_ipv4_custom_dhcpoptions_at_member_dhcpproperties_with_network(self):
          logging.info("validating the inherited values of ipv4_custom_dhcpoptions with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"options": [{"name": "host-name","num": 12,"value": "stringer","vendor_class": "DHCP"}]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          sleep(5)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=options",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['options']
          #print(response)
          if (response[0]['inherited']== True and "member:dhcpproperties" in response[0]['source'] and response[0]['values'][0]['num']== 12 and response[0]['values'][0]['value']=="stringer" and response[0]['values'][0]['name']=="host-name"):
                  assert True
          else:
                  assert False
          print("Test Case 245 Execution Completed")

      @pytest.mark.run(order=246)
      def test_246_validating_the_inherited_values_of_ipv4_custom_dhcpoptions_at_member_dhcpproperties_with_range(self):
          logging.info("validating the inherited values of ipv4_custom_dhcpoptions with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"options": [{"name": "merit-dump","num": 14,"value": "text","vendor_class": "DHCP"}]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          sleep(5)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=options",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['options']
          #print(response)
          #if (response[0]['inherited']== True and member:dhcpproperties" in response[0]['source'] and response[0]['values'][0]['num']== 14 and response[0]['values'][0]['value']== "text" and response[0]['values'][0]['name']== "merit-dump"):
                  #assert True
         # else:
          #        assert False
          print("Test Case 246 Execution Completed")

      @pytest.mark.run(order=247)
      def test_247_validating_the_inherited_values_of_ipv4_custom_dhcpoptions_at_member_dhcpproperties_with_fixedaddress(self):
          logging.info("validating the inherited values of ipv4_custom_dhcpoptions with fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"options": [{"name": "root-path","num": 17,"value": "fixedtext","vendor_class": "DHCP"}]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          sleep(5)
          response = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=options",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['options']
          #print(response)
          if (response[0]['inherited']== True and "member:dhcpproperties" in response[0]['source'] and response[0]['values'][0]['num']== 17and response[0]['values'][0]['value']=="fixedtext" and response[0]['values'][0]['name']=="root-path"):
                  assert True
          else:
                  assert False
          print("Test Case 247 Execution Completed")


      @pytest.mark.run(order=248)
      def test_248_validating_the_inherited_values_of_ipv4_custom_dhcpoptions_at_networkcontainer_with_network(self):
          logging.info("validating the inherited values of ipv4_custom_dhcpoptions with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"options": [{"name": "host-name","num": 12,"value": "stringer","vendor_class": "DHCP"}]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          sleep(5)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=options",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['options'][2]
          if (response['inherited']== True and "networkcontainer" in response['source'] and response['values'][0]['num']== 12 and response['values'][0]['value']=="stringer" and response['values'][0]['name']=="host-name"):
                 assert True
          else:
                 assert False
          print("Test Case 248 Execution Completed")



      @pytest.mark.run(order=249)
      def test_249_validating_the_inherited_values_of_ipv4_custom_dhcpoptions_at_networklevel_with_network(self):
          logging.info("validating the inherited values of ipv4_custom_dhcpoptions with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"options": [{"name": "host-name","num": 12,"value": "stringer","vendor_class": "DHCP"}]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          sleep(5)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=options",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['options'][0]
          if (response['inherited']== False and "" in response['source'] and response['values'][0]['num']== 12 and response['values'][0]['value']=="stringer" and response['values'][0]['name']=="host-name"):
                  assert True
          else:
                  assert False
          print("Test Case 249 Execution Completed")

      @pytest.mark.run(order=250)
      def test_250_validating_the_inherited_values_of_ipv4_custom_dhcpoptions_at_rangelevel_with_range(self):
          logging.info("validating the inherited values of ipv4_custom_dhcpoptions with range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="range", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"options": [{"name": "merit-dump","num": 14,"value": "text","vendor_class": "DHCP"}]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          sleep(5)
          response = ib_NIOS.wapi_request('GET',object_type="range",params="?_inheritance=True&_return_fields=options",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['options'][0]
          #print(response)
          if (response['inherited']== False and "" in response['source'] and response['values'][0]['num']== 14 and response['values'][0]['value']=="text" and response['values'][0]['name']=="merit-dump"):
                  assert True
          else:
                  assert False
          print("Test Case 250 Execution Completed")

      @pytest.mark.run(order=251)
      def test_251_validating_the_inherited_values_of_ipv4_custom_dhcpoptions_at_fixedaddresslevel_with_fixedaddress(self):
          logging.info("validating the inherited values of ipv4_custom_dhcpoptions with fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="fixedaddress", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"options": [{"name": "root-path","num": 17,"value": "fixedtext","vendor_class": "DHCP"}]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          sleep(5)
          response = ib_NIOS.wapi_request('GET',object_type="fixedaddress",params="?_inheritance=True&_return_fields=options",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['options']
          #print(response)
          if (response[0]['inherited']== False and "" in response[0]['source'] and response[0]['values'][0]['num']== 17and response[0]['values'][0]['value']=="fixedtext" and response[0]['values'][0]['name']=="root-path"):
                  assert True
          else:
                  assert False
          print("Test Case 251 Execution Completed")


      @pytest.mark.run(order=252)
      def test_252_validating_the_inherited_values_of_ipv6_custom_dhcpoptions_at_grid_dhcpproperties_with_ipv6network(self):
          logging.info("validating the inherited values of ipv6_custom_dhcpoptions with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ipv6_options": [{"name": "dhcp6.fqdn","num": 39,"value": "stringer","vendor_class": "DHCPv6"}]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          sleep(5)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=options",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['options']
          #print(response)
          if (response[1]['inherited']== True and "grid:dhcpproperties" in response[1]['source'] and response[1]['values'][0]['num']== 39 and response[1]['values'][0]['value']=="stringer" and response[1]['values'][0]['name']=="dhcp6.fqdn"):
                  assert True
          else:
                  assert False
          print("Test Case 252 Execution Completed")


      @pytest.mark.run(order=253)
      def test_253_validating_the_inherited_values_of_ipv6_custom_dhcpoptions_at_grid_dhcpproperties_with_ipv6fixedaddress(self):
          logging.info("validating the inherited values of ipv6_custom_dhcpoptions with ipv6fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ipv6_options": [{"name": "dhcp6.bcms-server-d","num": 33,"value": "\"www.infoblox.com\"","vendor_class": "DHCPv6"}]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          sleep(5)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6fixedaddress",params="?_inheritance=True&_return_fields=options",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['options']
          #print(response)
          if (response[1]['inherited']== True and "grid:dhcpproperties" in response[1]['source'] and response[1]['values'][0]['num']== 33 and response[1]['values'][0]['value']=="\"www.infoblox.com\"" and response[1]['values'][0]['name']=="dhcp6.bcms-server-d"):
                  assert True
          else:
                  assert False
          print("Test Case 253 Execution Completed")


      @pytest.mark.run(order=254)
      def test_254_validating_the_inherited_values_of_ipv6_custom_dhcpoptions_at_member_dhcpproperties_with_ipv6network(self):
          logging.info("validating the inherited values of ipv6_custom_dhcpoptions with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ipv6_options": [{"name": "dhcp6.fqdn","num": 39,"value": "stringer","vendor_class": "DHCPv6"}]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          sleep(5)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=options",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['options']
          #print(response)
          if (response[1]['inherited']== True and "member:dhcpproperties" in response[1]['source'] and response[1]['values'][0]['num']== 39 and response[1]['values'][0]['value']=="stringer" and response[1]['values'][0]['name']=="dhcp6.fqdn"):
                  assert True
          else:
                  assert False
          print("Test Case 254 Execution Completed")


      @pytest.mark.run(order=255)
      def test_255_validating_the_inherited_values_of_ipv6_custom_dhcpoptions_at_member_dhcpproperties_with_ipv6fixedaddress(self):
          logging.info("validating the inherited values of ipv6_custom_dhcpoptions with ipv6fixedaddress")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"ipv6_options": [{"name": "dhcp6.bcms-server-d","num": 33,"value": "\"www.infoblox.com\"","vendor_class": "DHCPv6"}]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          sleep(5)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6fixedaddress",params="?_inheritance=True&_return_fields=options",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['options']
          #print(response)
          if (response[1]['inherited']== True and "member:dhcpproperties" in response[1]['source'] and response[1]['values'][0]['num']== 33 and response[1]['values'][0]['value']=="\"www.infoblox.com\"" and response[1]['values'][0]['name']=="dhcp6.bcms-server-d"):
                  assert True
          else:
                  assert False
          print("Test Case 255 Execution Completed")

      @pytest.mark.run(order=256)
      def test_256_validating_the_inherited_values_of_ipv6_custom_dhcpoptions_at_ipv6networkcontainer_with_ipv6network(self):
          logging.info("validating the inherited values of ipv6_custom_dhcpoptions with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6networkcontainer", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"options": [{"name": "dhcp6.fqdn","num": 39,"value": "stringer","vendor_class": "DHCPv6"}]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          sleep(5)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=options",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['options'][2]
          #print(response)
          if (response['inherited']== True and "ipv6networkcontainer" in response['source'] and response['values'][0]['num']== 39 and response['values'][0]['value']=="stringer" and response['values'][0]['name']=="dhcp6.fqdn"):
                  assert True
          else:
                  assert False
          print("Test Case 256 Execution Completed")


      @pytest.mark.run(order=257)
      def test_257_validating_the_inherited_values_of_ipv6_custom_dhcpoptions_at_ipv6networklevel_with_ipv6network(self):
          logging.info("validating the inherited values of ipv6_custom_dhcpoptions with ipv6network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6network", grid_vip=config.grid_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"options": [{"name": "dhcp6.rapid-commit","num": 14,"value": "true","vendor_class": "DHCPv6"}]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          sleep(5)
          response = ib_NIOS.wapi_request('GET',object_type="ipv6network",params="?_inheritance=True&_return_fields=options",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['options'][0]
          #print(response)
          if (response['inherited']== False and "" in response['source'] and response['values'][0]['num']== 14 and response['values'][0]['value']== "true" and response['values'][0]['name']=="dhcp6.rapid-commit"):
                  assert True
          else:
                  assert False
          print("Test Case 257 Execution Completed")

      @pytest.mark.run(order=258)
      def test_258_member_assignment_to_the_ipv4network(self):
          logging.info("assigning member to the ipv4network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"members":[{"_struct": "dhcpmember","ipv4addr":config.grid_vip},{"_struct": "dhcpmember","ipv4addr":config.grid_member1_vip}]}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          print("Test Case 258 Execution Completed")

      @pytest.mark.run(order=259)
      def test_259_validating_the_multisource_inherited_values_of_enable_ddns_at_grid_dhcpproperties_with_network(self):
          logging.info("validating the multisource inherited values of enable_ddns with network")
          get_ref = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"use_enable_ddns": False}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          get_ref1 = ib_NIOS.wapi_request('GET', object_type="networkcontainer", grid_vip=config.grid_vip)
          res1 = json.loads(get_ref1)
          ref2 = json.loads(get_ref1)[0]['_ref']
          data1 = {"use_enable_ddns": False}
          output1 = ib_NIOS.wapi_request('PUT',ref=ref2,fields=json.dumps(data1),grid_vip=config.grid_vip)
          get_ref2 = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
          res2 = json.loads(get_ref2)
          ref3 = json.loads(get_ref2)[0]['_ref']
          data2 = {"enable_ddns": True}
          output2 = ib_NIOS.wapi_request('PUT',ref=ref3,fields=json.dumps(data2),grid_vip=config.grid_vip)
          response = ib_NIOS.wapi_request('GET',object_type="network",params="?_inheritance=True&_return_fields=enable_ddns",grid_vip=config.grid_vip)
          print(response)
          response=json.loads(response)
          response=response[0]['enable_ddns']
          if (response['inherited']== True and response['multisource']== True and "member:dhcpproperties" in response['values'][0]['source'] and "grid:dhcpproperties" in response['values'][1]['source']):
                  assert True
          else:
                  assert False
          print("Test Case 259 Execution Completed")




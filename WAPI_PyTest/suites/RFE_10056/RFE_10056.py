import re
import pexpect
import sys
import config
import pytest
import unittest
import logging
import os
import os.path
from os.path import join
import subprocess
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util

class Network(unittest.TestCase):

####################################################################################################################################################################
############ Associating EA at default network view and checking the child(dnsview,zone,records) inheritance states. ###############################################
############ Result: At all child levels inheritance state should show as "Inherit" and value should get from default network view  ################################
####################################################################################################################################################################

#######################################################################################################
#### Note: Since WAPI has limitation, we are removing the configuration to test other scenarios #####
#######################################################################################################


      @pytest.mark.run(order=1)
      def test_001_Add_and_Validate_Extensible_Attribute_with_enable_inheritance(self):
          logging.info("adding and validating extensible attribute")
          data = {"default_value": "100","name": "infoblox","type": "STRING"}
          response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=default_value,name",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "infoblox"','"default_value": "100"']
          for i in result:
	      if i in output:
                  assert True
              else:
                  assert False
          print(result)
          print("Test Case 01 Executuion Completed")

      @pytest.mark.run(order=2)
      def test_002_Associate_and_Validate_EA_at_networkview(self):
          logging.info("associating created EA at networkview")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkview", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print(ref1)
          data = {"extattrs": {"infoblox": {"value": "100"}}}
          view = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(view)
          output = ib_NIOS.wapi_request('GET',object_type="networkview",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = 'extattrs:infoblox:value:100'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 02 Executuion Completed")

      @pytest.mark.run(order=3)
      def test_003_Modify_descendants_action(self):
          logging.info("modifying descendant actions to get EA to child objects")
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"descendants_action": {"option_with_ea": "INHERIT","option_without_ea": "INHERIT"},"flags": "I"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",ref=ref1,params="?_inheritance=True&_return_fields=flags",grid_vip=config.grid_vip)
          print(get_ref)
          result = '"flags": "I"'
          if result in get_ref:
               assert True
          else:
               assert False
          print(result)
          print("Test Case 03 Executuion Completed")

      @pytest.mark.run(order=4)
      def test_004_Validate_EA_inheritance_at_dns_view(self):
          logging.info("validating EA inheritance at dns view")
          get_ref = ib_NIOS.wapi_request('GET',object_type="view",grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',object_type="view",ref=ref1,params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
   	  #print(output)
          result = ['extattrs:infoblox:inheritance_source::networkview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 04 Executuion Completed")
    

      @pytest.mark.run(order=5)
      def test_005_Add_and_Validate_Authority_zone(self):
          logging.info("adding authority zone")
          data = {"fqdn": "test.com","view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print(ref1)
          result = 'test.com'
          if result in ref1:
               assert True
               print("Authority zone has created")
          else:
               assert False
          print(result)
          print("Test Case 05 Executuion Completed")
      
      @pytest.mark.run(order=6)
      def test_006_Validate_EA_Inheritance_at_authority_zone(self):
          logging.info("validating EA inheritance at zone level")
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          print(output)
          result = ['extattrs:infoblox:inheritance_source::networkview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 06 Executuion Completed")
      
      @pytest.mark.run(order=7)
      def test_007_Add_and_Validate_A_record(self):
          logging.info("adding and validating A record")
          data = {"ipv4addr": "10.0.0.2","name": "a.test.com","view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          output = ib_NIOS.wapi_request('GET',object_type="record:a",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "a.test.com"','"ipv4addr": "10.0.0.2"']
          for i in result:
            if i in output:
                  assert True
            else:
                  assert False
          print(result)
          print("Test Case 07 Executuion Completed")
    

      @pytest.mark.run(order=8)
      def test_008_Validate_EA_inheritance_at_A_record(self):
          logging.info("validating EA inheritance at record level(A record)")
          output = ib_NIOS.wapi_request('GET',object_type="record:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox:inheritance_source::networkview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 08 Executuion Completed")


      @pytest.mark.run(order=9)
      def test_009_Add_and_validate_AAAA_record(self):
          logging.info("adding and validating AAAA record")
          data = {"ipv6addr": "2620:10a:6000:2400::2","name": "aaaa.test.com","view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="record:aaaa",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          get_ref = ib_NIOS.wapi_request('GET',object_type="record:aaaa",grid_vip=config.grid_vip)
          print(get_ref)
          result = ['"ipv6addr": "2620:10a:6000:2400::2"','"name": "aaaa.test.com"','"view": "default"']
          for i in result:
            if i in get_ref:
               assert True
            else:
               assert False
          print(result)
          print("Test Case 09 Executuion Completed")

      @pytest.mark.run(order=10)
      def test_010_Validate_EA_inheritance__at_AAAA_record(self):
          logging.info("validating EA inheritance at record level(AAAA record)")
          output = ib_NIOS.wapi_request('GET',object_type="record:aaaa",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox:inheritance_source::networkview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 10 Executuion Completed")

      @pytest.mark.run(order=11)
      def test_011_Add_and_Validate_alias_record(self):
          logging.info("adding and validating alias record")
          data = {"name": "alias.test.com","target_name": "www.infoblox.com","target_type": "A","view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="record:alias",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          output = ib_NIOS.wapi_request('GET',object_type="record:alias",grid_vip=config.grid_vip)
          print(output)
          result =['"name": "alias.test.com"','"target_name": "www.infoblox.com"','"target_type": "A"','"view": "default"']
          for i in result:
            if i in output:
                  assert True
            else:
                  assert False
          print(result)
          print("Test Case 11 Executuion Completed")


      @pytest.mark.run(order=12)
      def test_012_Validate_EA_inheritance_at_alias_record(self):
          logging.info("validating EA inheritance at alias record")
          output = ib_NIOS.wapi_request('GET',object_type="record:alias",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox:inheritance_source::networkview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 12 Executuion Completed")


      @pytest.mark.run(order=13)
      def test_013_Add_and_Validate_CNAME_record(self):
          logging.info("add and validate CNAME record")
          data = {"canonical": "test.com","name": "caa.test.com","view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="record:cname",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          output = ib_NIOS.wapi_request('GET',object_type="record:cname",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "caa.test.com"','"canonical": "test.com"','"view": "default"']
          for i in result:
            if i in output:
                  assert True
            else:
                  assert False
          print(result)
          print("Test Case 13 Executuion Completed")


      @pytest.mark.run(order=14)
      def test_014_Validate_EA_inheritance_at_cname_record(self):
          logging.info("validating EA inheritance at cname record")
          output = ib_NIOS.wapi_request('GET',object_type="record:cname",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox:inheritance_source::networkview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 14 Executuion Completed")

      @pytest.mark.run(order=15)
      def test_015_Add_and_Validate_dname_record(self):
          logging.info("adding and validating dname record")
          data = {"name": "dname.test.com","target": "www.infoblox.com","view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="record:dname",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          output = ib_NIOS.wapi_request('GET',object_type="record:dname",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "dname.test.com"','"target": "www.infoblox.com"','"view": "default"']
          for i in result:
            if i in output:
                  assert True
            else:
                  assert False
          print(result)
          print("Test Case 15 Executuion Completed")

      @pytest.mark.run(order=16)
      def test_016_Validate_EA_inheritance_at_dname_record(self):
          logging.info("validating EA inheritance at dname record ")
          output = ib_NIOS.wapi_request('GET',object_type="record:dname",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox:inheritance_source::networkview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 16 Executuion Completed")


      @pytest.mark.run(order=17)
      def test_017_Add_and_Validate_mx_record(self):
          logging.info("adding and validating mx record")
          data = {"mail_exchanger": "test.com","name": "mx.test.com","preference": 10,"view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="record:mx",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          output = ib_NIOS.wapi_request('GET',object_type="record:mx",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "mx.test.com"','"mail_exchanger": "test.com"','"view": "default"','"preference": 10']
          for i in result:
            if i in output:
                  assert True
            else:
                  assert False
          print(result)
          print("Test Case 17 Executuion Completed")


      @pytest.mark.run(order=18)
      def test_018_Validate_EA_inheritance_at_mx_record(self):
          logging.info("validating EA inheritance at mx record")
          output = ib_NIOS.wapi_request('GET',object_type="record:mx",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox:inheritance_source::networkview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 18 Executuion Completed")


      @pytest.mark.run(order=19)
      def test_019_Add_and_Validate_naptr_record(self):
          logging.info("adding and validating naptr record")
          data = {"name": "naptr.test.com","order": 10,"preference": 10,"regexp": "","replacement": ".","services": "http+E2U","view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="record:naptr",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          output = ib_NIOS.wapi_request('GET',object_type="record:naptr",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "naptr.test.com"','"order": 10','"preference": 10','"regexp": ""','"replacement": "."','"services": "http+E2U"','"view": "default"']
          for i in result:
            if i in output:
                  assert True
            else:
                  assert False
          print(result)
          print("Test Case 19 Executuion Completed")

      @pytest.mark.run(order=20)
      def test_020_Validate_EA_inheritance_at_naptr_record(self):
          logging.info("validating EA inheritance at naptr record")
          output = ib_NIOS.wapi_request('GET',object_type="record:naptr",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          result = ['extattrs:infoblox:inheritance_source::networkview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 20 Executuion Completed")

      @pytest.mark.run(order=21)
      def test_021_Add_and_Validate_ptr_record(self):
          logging.info("adding and validating ptr record")
          data = {"ptrdname": "www.infoblox.com","name": "ptr.test.com","view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="record:ptr",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          output = ib_NIOS.wapi_request('GET',object_type="record:ptr",params="?_inheritance=True&_return_fields=name,ptrdname",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "ptr.test.com"','"ptrdname": "www.infoblox.com"']
          for i in result:
            if i in output:
                  assert True
            else:
                  assert False
          print(result)
          sleep(03)
          print("Test Case 21 Executuion Completed")

      @pytest.mark.run(order=22)
      def test_022_Validate_EA_inheritance_at_ptr_record(self):
          logging.info("validating EA inheritance at ptr record")
          output = ib_NIOS.wapi_request('GET',object_type="record:ptr",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result =['ptr.test.com/default,extattrs:infoblox:inheritance_source::networkview','value:100']
          for i in result: 
            if i in output:
                assert True
            else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 22 Executuion Completed")

      @pytest.mark.run(order=23)
      def test_023_Add_and_Validate_srv_record(self):
          logging.info("adding and validating srv record")
          data = {"name": "srv.test.com","port": 22,"priority": 0,"target": "test.com","view": "default","weight": 0}
          response = ib_NIOS.wapi_request('POST', object_type="record:srv",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          output = ib_NIOS.wapi_request('GET',object_type="record:srv",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "srv.test.com"','"port": 22','"priority": 0','"target": "test.com"','"view": "default"','"weight": 0']
          for i in result:
            if i in output:
                  assert True
            else:
                  assert False
          print(result)
          sleep(03)
          print("Test Case 23 Executuion Completed")

      @pytest.mark.run(order=24)
      def test_024_Validate_EA_inheritance_at_srv_record(self):
          logging.info("validating EA inheritance at srv record") 
          output = ib_NIOS.wapi_request('GET',object_type="record:srv",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          result = ['extattrs:infoblox:inheritance_source::networkview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
   	  sleep(03)
          print("Test Case 24 Executuion Completed")

      @pytest.mark.run(order=25)
      def test_025_Add_and_Validate_tlsa_record(self):
          logging.info("adding and validating tsla record")
	  data={"certificate_data": "1A1B","certificate_usage": 0,"matched_type": 0,"name": "_443._tcp.tlsa.test.com","selector": 0,"view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="record:tlsa",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          output = ib_NIOS.wapi_request('GET',object_type="record:tlsa",params="?_inheritance=True&_return_fields=name,certificate_data,view,certificate_data,certificate_usage,selector",grid_vip=config.grid_vip)
          print(output)
          result = ['"certificate_data": "1A1B"','"name": "_443._tcp.tlsa.test.com"','"view": "default"','"certificate_usage": 0','"selector": 0']
          for i in result:
            if i in output:
                  assert True
            else:
                  assert False
          print(result)
          sleep(03)
          print("Test Case 25 Executuion Completed")

      @pytest.mark.run(order=26)
      def test_026_Validate_EA_inheritance_at_tsla_record(self):
          logging.info("validating EA inheritance at tsla record")
          output = ib_NIOS.wapi_request('GET',object_type="record:tlsa",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox:inheritance_source::networkview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 26 Executuion Completed")

      @pytest.mark.run(order=27)
      def test_027_Add_and_Validate_txt_record(self):
          logging.info("adding and validating txt record")
          data = {"name": "txt.test.com","text": "textdata","view": "default"}
          response = ib_NIOS.wapi_request('POST',object_type="record:txt",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          output = ib_NIOS.wapi_request('GET',object_type="record:txt",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "txt.test.com"','"text": "textdata"','"view": "default"']
          for i in result:
            if i in output:
                  assert True
            else:
                  assert False
          print(result)
          sleep(03)
          print("Test Case 27 Executuion Completed")

      @pytest.mark.run(order=28)
      def test_028_Validate_EA_inheritance_at_txt_record(self):
          logging.info("validating EA inheritance at txt record")
          output = ib_NIOS.wapi_request('GET',object_type="record:txt",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox:inheritance_source::networkview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 28 Executuion Completed")

      @pytest.mark.run(order=29)
      def test_029_Add_and_Validate_unknown_record(self):
          logging.info("adding and validating unknown record")
          data = {"name": "unknown.test.com","record_type": "TYPE123","subfield_values": [],"view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="record:unknown",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          output = ib_NIOS.wapi_request('GET',object_type="record:unknown",grid_vip=config.grid_vip)
          print(output)
          result = 'unknown.test.com'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          sleep(03)
          print("Test Case 29 Executuion Completed")

      @pytest.mark.run(order=30)
      def test_030_Validate_EA_inheritance_at_unknown_record(self):
          logging.info("validating EA inheritance at unknown record")
          output = ib_NIOS.wapi_request('GET',object_type="record:unknown",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          result = ['extattrs:infoblox:inheritance_source::networkview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 30 Executuion Completed")

####################################################################################################################################################################
###################### Overriding EA at default DNS view and checking the child(zone,records) inheritance states. ##################################################
################ Result: At all child levels inheritance state should show as "Inherit" and value should get from default DNS view  ################################
####################################################################################################################################################################


      @pytest.mark.run(order=31)
      def test_031_Override_and_Validate_EA_value_at_dns_view(self):
          logging.info("overriding and validating EA value at dns view")
          output = ib_NIOS.wapi_request('GET',object_type="view",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          #print(output)
          get_ref = ib_NIOS.wapi_request('GET', object_type="view", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox": {"value": "1000"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          #print(output)
          output = ib_NIOS.wapi_request('GET',object_type="view",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          print(output)
          result = 'extattrs:infoblox:value:1000'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          sleep(03)
          print("Test Case 31 Executuion Completed")


      @pytest.mark.run(order=32)
      def test_032_Validate_EA_inheritance_at_authority_zone(self):
          logging.info("validating EA inheritance at authority zone")   
          get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ["extattrs:infoblox:inheritance_source::view","value:1000"]
          for i in result:
          	if i in output:
                	assert True
          	else:
                	assert False
          print(result)
          sleep(03)
          print("Test Case 32 Executuion Completed")

      @pytest.mark.run(order=33)
      def test_033_VAlidate_EA_inheritance_at_A_record(self):
          logging.info("validating EA inheritance at A record")
          output = ib_NIOS.wapi_request('GET',object_type="record:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ["extattrs:infoblox:inheritance_source::view","value:1000"]
          for i in result:
             if i in output:
                assert True
             else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 33 Executuion Completed")
   
     
      @pytest.mark.run(order=34)
      def test_034_Validate_EA_inheritance_at_AAAA_record(self):
          logging.info("validating EA inheritance at AAAA record")
          output = ib_NIOS.wapi_request('GET',object_type="record:aaaa",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ["extattrs:infoblox:inheritance_source::view","value:1000"]
          for i in result:
             if i in output:
                assert True
             else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 34 Executuion Completed")

      @pytest.mark.run(order=35)
      def test_035_Validate_EA_inheritance_at_alias_record(self):
          logging.info("validating EA inheritance at alias record")
          output = ib_NIOS.wapi_request('GET',object_type="record:alias",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          result = ["extattrs:infoblox:inheritance_source::view","value:1000"]
          for i in result:
             if i in output:
                assert True
             else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 35 Executuion Completed")

      @pytest.mark.run(order=36)
      def test_036_Validate_EA_inheritance_at_cname_record(self):
          logging.info("validating EA inheritance at cname record")
          output = ib_NIOS.wapi_request('GET',object_type="record:cname",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          result = ["extattrs:infoblox:inheritance_source::view","value:1000"]
          for i in result:
             if i in output:
                assert True
             else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 36 Executuion Completed")

      @pytest.mark.run(order=37)
      def test_037_Validate_EA_inheritance_at_dname_record(self):
          logging.info("validating EA inheritance at dname record")
          output = ib_NIOS.wapi_request('GET',object_type="record:dname",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          result = ["extattrs:infoblox:inheritance_source::view","value:1000"]
          for i in result:
             if i in output:
                assert True
             else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 37 Executuion Completed")


      @pytest.mark.run(order=38)
      def test_038_Validate_EA_inheritance_at_mx_record(self):
          logging.info("validating EA inheritance at mx record")
          output = ib_NIOS.wapi_request('GET',object_type="record:mx",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          result = ["extattrs:infoblox:inheritance_source::view","value:1000"]
          for i in result:
             if i in output:
                assert True
             else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 38 Executuion Completed")
   
      @pytest.mark.run(order=39)
      def test_039_Validate_EA_inheritance_at_naptr_record(self):
          logging.info("validating EA inheritance at naptr record")
          output = ib_NIOS.wapi_request('GET',object_type="record:naptr",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          result = ["extattrs:infoblox:inheritance_source::view","value:1000"]
          for i in result:
             if i in output:
                assert True
             else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 39 Executuion Completed")

      @pytest.mark.run(order=40)
      def test_040_Validate_EA_inheritance_at_ptr_record(self):
          logging.info("validating EA inheritance at ptr record")
          output = ib_NIOS.wapi_request('GET',object_type="record:ptr",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          result = ["extattrs:infoblox:inheritance_source::view","value:1000"]
          for i in result:
             if i in output:
                assert True
             else:
                assert False
          print(result)      
          sleep(03)    
          print("Test Case 40 Executuion Completed")

      @pytest.mark.run(order=41)
      def test_041_Validate_EA_inheritance_at_srv_record(self):
          logging.info("validating EA inheritance at srv record")
          output = ib_NIOS.wapi_request('GET',object_type="record:srv",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          result = ["extattrs:infoblox:inheritance_source::view","value:1000"]
          for i in result:
             if i in output:
                assert True
             else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 41 Executuion Completed")

      @pytest.mark.run(order=42)
      def test_042_Validate_EA_inheritance_at_tlsa_record(self):
          logging.info("validating EA inheritance at tsla record")
          output = ib_NIOS.wapi_request('GET',object_type="record:tlsa",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          result = ["extattrs:infoblox:inheritance_source::view","value:1000"]
          for i in result:
             if i in output:
                assert True
             else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 42 Executuion Completed")

      @pytest.mark.run(order=43)
      def test_043_Validate_EA_inheritance_at_txt_record(self):
          logging.info("validating EA inheritance at txt record")
          output = ib_NIOS.wapi_request('GET',object_type="record:txt",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          result = ["extattrs:infoblox:inheritance_source::view","value:1000"]
          for i in result:
             if i in output:
                assert True
             else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 43 Executuion Completed")

      @pytest.mark.run(order=44)
      def test_044_Validate_EA_inheritance_at_unknown_record(self):
          logging.info("validating EA inheritance at unknown record")
          output = ib_NIOS.wapi_request('GET',object_type="record:unknown",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          result = ["extattrs:infoblox:inheritance_source::view","value:1000"]
          for i in result:
             if i in output:
                assert True
             else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 44 Executuion Completed")



####################################################################################################################################################################
################################# Overriding EA at ZONE and checking the child(records) inheritance states. ########################################################
###################### Result: At all child levels inheritance state should show as "Inherit" and value should get from "ZONE"  ####################################
####################################################################################################################################################################

      @pytest.mark.run(order=45)
      def test_045_Override_and_validate_EA_value_at_authority_zone(self):
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox": {"value": "zone"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          #print(output)
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = "extattrs:infoblox:value:zone"
          if result in output:
                assert True
          else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 45 Executuion Completed")


      @pytest.mark.run(order=46)
      def test_046_Validate_EA_inheritance_at_A_record(self):
          logging.info("validating EA inheritance at A record")
          output = ib_NIOS.wapi_request('GET',object_type="record:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ["extattrs:infoblox:inheritance_source::zone_auth","value:zone"]
          for i in result:
             if i in output:
                assert True
             else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 46 Executuion Completed")

      @pytest.mark.run(order=47)
      def test_047_Validate_EA_inheritance_at_AAAA_record(self):
          logging.info("validating EA inheritance at AAAA record ")
          output = ib_NIOS.wapi_request('GET',object_type="record:aaaa",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ["extattrs:infoblox:inheritance_source::zone_auth","value:zone"]
          for i in result:
             if i in output:
                assert True
             else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 47 Executuion Completed")

      @pytest.mark.run(order=48)
      def test_048_Validate_EA_inheritance_at_alias_record(self):
          logging.info("validating EA inheritance at alias record ")
          output = ib_NIOS.wapi_request('GET',object_type="record:alias",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          result = ["extattrs:infoblox:inheritance_source::zone_auth","value:zone"]
          for i in result:
             if i in output:
                assert True
             else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 48 Executuion Completed")

      @pytest.mark.run(order=49)
      def test_049_Validate_EA_inheritance_at_cname_record(self):
          logging.info("validating EA inheritance at cname record ")
          output = ib_NIOS.wapi_request('GET',object_type="record:cname",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          result = ["extattrs:infoblox:inheritance_source::zone_auth","value:zone"]
          for i in result:
             if i in output:
                assert True
             else:
                assert False
          print(result)
 	  sleep(03)
          print("Test Case 49 Executuion Completed")

      @pytest.mark.run(order=50)
      def test_050_Validate_EA_inheritance_at_dname_record(self):
          logging.info("validating EA inheritance at dname record ")
          output = ib_NIOS.wapi_request('GET',object_type="record:dname",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          result = ["extattrs:infoblox:inheritance_source::zone_auth","value:zone"]
          for i in result:
             if i in output:
                assert True
             else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 50 Executuion Completed")

      @pytest.mark.run(order=51)
      def test_051_Validate_EA_inheritance_at_mx_record(self):
          logging.info("validating EA inheritance at mx record ")
          output = ib_NIOS.wapi_request('GET',object_type="record:mx",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          result = ["extattrs:infoblox:inheritance_source::zone_auth","value:zone"]
          for i in result:
             if i in output:
                assert True
             else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 51 Executuion Completed")

      @pytest.mark.run(order=52)
      def test_052_Validate_EA_inheritance_at_naptr_record(self):
          logging.info("validating EA inheritance at naptr record ")
          output = ib_NIOS.wapi_request('GET',object_type="record:naptr",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          result = ["extattrs:infoblox:inheritance_source::zone_auth","value:zone"]
          for i in result:
             if i in output:
                assert True
             else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 52 Executuion Completed")

      @pytest.mark.run(order=53)
      def test_053_Validate_EA_inheritance_at_ptr_record(self):
          logging.info("validating EA inheritance at ptr record ")
          output = ib_NIOS.wapi_request('GET',object_type="record:ptr",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          result = ["extattrs:infoblox:inheritance_source::zone_auth","value:zone"]
          for i in result:
             if i in output:
                assert True
             else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 53 Executuion Completed")

      @pytest.mark.run(order=54)
      def test_054_Validate_EA_inheritance_at_srv_record(self):
          logging.info("validating EA inheritance at srv record ")
          output = ib_NIOS.wapi_request('GET',object_type="record:srv",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          result = ["extattrs:infoblox:inheritance_source::zone_auth","value:zone"]
          for i in result:
             if i in output:
                assert True
             else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 54 Executuion Completed")


      @pytest.mark.run(order=55)
      def test_055_Validate_EA_inheritance_at_tsla_record(self):
          logging.info("validating EA inheritance at tsla record ")
          output = ib_NIOS.wapi_request('GET',object_type="record:tlsa",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          result = ["extattrs:infoblox:inheritance_source::zone_auth","value:zone"]
          for i in result:
             if i in output:
                assert True
             else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 55 Executuion Completed")

      @pytest.mark.run(order=56)
      def test_056_Validate_EA_inheritance_at_txt_record(self):
          logging.info("validating EA inheritance at txt record ")
          output = ib_NIOS.wapi_request('GET',object_type="record:txt",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          result = ["extattrs:infoblox:inheritance_source::zone_auth","value:zone"]
          for i in result:
             if i in output:
                assert True
             else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 56 Executuion Completed")

      @pytest.mark.run(order=57)
      def test_057_Validate_EA_inheritance_at_unknown_record(self):
          logging.info("validating EA inheritance at unknown record ")
          output = ib_NIOS.wapi_request('GET',object_type="record:unknown",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          result = ["extattrs:infoblox:inheritance_source::zone_auth","value:zone"]
          for i in result:
             if i in output:
                assert True
             else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 57 Executuion Completed")


####################################################################################################################################################################
############################################## Overriding EA at Records and checking the inheritance states. #######################################################
###################### Result: At records level inheritance state should show as "Overridden" and value should show current value ##################################
####################################################################################################################################################################


      @pytest.mark.run(order=58)
      def test_058_Override_and_Validate_EA_value_at_authority_zone(self):
          logging.info("overriding and validating EA inheritance value at zone level")
          get_ref = ib_NIOS.wapi_request('GET', object_type="record:a", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"extattrs": {"infoblox": {"value": "record"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          output = ib_NIOS.wapi_request('GET',object_type="record:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          result = "extattrs:infoblox:value:record"
          if result in output:
                assert True
          else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 58 Executuion Completed")


      @pytest.mark.run(order=59)
      def test_059_Override_and_Validate_EA_inheritance_value_at_record_level(self):
          logging.info("overriding and validating EA inheritance value at record level")
          get_ref = ib_NIOS.wapi_request('GET', object_type="record:aaaa", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"extattrs": {"infoblox": {"value": "record"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          output = ib_NIOS.wapi_request('GET',object_type="record:aaaa",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          result = "extattrs:infoblox:value:record"
          if result in output:
                assert True
          else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 59 Executuion Completed")

####################################################################################################################################################
########################################## removing the configuration to test other scenario #####################################################
####################################################################################################################################################

      @pytest.mark.run(order=60)
      def test_060_Delete_and_Validate_Extensible_attribute(self):
          logging.info("deleting and validating  exetensible attribute to test other scenarios")
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          result = '"name": "infoblox"'
          if result in output:
             assert False
          else:
             assert True
          print(result)
          sleep(03)
          print("Test Case 60 Executuion Completed")


###################################################################################################################################################################
############## Associating EA at default dns view  and checking at parent(networkview) level.(Result : At networkview level value should be empty #################
###################################################################################################################################################################

      @pytest.mark.run(order=61)
      def test_061_Add_and_Validate_Extensible_Attribute_with_enable_inheritance(self):
          logging.info("adding and validating extensible attribute")
          data = {"default_value": "100","name": "infoblox","type": "STRING"}
          response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=default_value,name",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "infoblox"','"default_value": "100"']
          for i in result:
              if i in output:
                  assert True
              else:
                  assert False
          print(result)
          sleep(03)
          print("Test Case 61 Executuion Completed")

      @pytest.mark.run(order=62)
      def test_062_Associate_and_Validate_EA_at_dns_view(self):
          logging.info("associating created EA at dns view ")
          output = ib_NIOS.wapi_request('GET',object_type="view",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          get_ref = ib_NIOS.wapi_request('GET', object_type="view", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox": {"value": "100"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          output = ib_NIOS.wapi_request('GET',object_type="view",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"value": "100"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          sleep(03)
          print("Test Case 62 Executuion Completed")

      @pytest.mark.run(order=63)
      def test_063_Modify_descendants_action(self):
          logging.info("modifying descendant actions to get EA to child objects")
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"descendants_action": {"option_with_ea": "INHERIT","option_without_ea": "INHERIT"},"flags": "I"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",ref=ref1,params="?_inheritance=True&_return_fields=flags",grid_vip=config.grid_vip)
          print(get_ref)
          result = '"flags": "I"'
          if result in get_ref:
               assert True
          else:
               assert False
          print(result)
          sleep(03)
          print("Test Case 63 Executuion Completed")

      @pytest.mark.run(order=64)
      def test_064_Validate_EA_inheritance_at_network_view(self):
          logging.info("validating EA inheritance at network view")
          output = ib_NIOS.wapi_request('GET',object_type="networkview",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"extattrs": {}'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          sleep(03)
          print("Test Case 64 Executuion Completed")

####################################################################################################################################################
########################################## removing the configuration to test other scenario #####################################################
####################################################################################################################################################

      @pytest.mark.run(order=65)
      def test_065_Delete_and_Validate_Extensible_attribute(self):
          logging.info("deleting and validating  extensible attribute to test other scenarios")
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          result = '"name": "infoblox"'
          if result in output:
             assert False
          else:
             assert True
          print(result)
          sleep(03)
          print("Test Case 65 Executuion Completed")

########################################################################################################################################################################
############## Associating EA at zone level  and checking at parent(networkview,dnsview) level.(Result : At networkview & dnsview level value should be empty ##########
########################################################################################################################################################################

      @pytest.mark.run(order=66)
      def test_066_Add_and_Validate_Extensible_Attribute_with_enable_inheritance(self):
          logging.info("adding and validating extensible attribute")
          data = {"default_value": "100","name": "infoblox","type": "STRING"}
          response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=default_value,name",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "infoblox"','"default_value": "100"']
          for i in result:
              if i in output:
                  assert True
              else:
                  assert False
          print(result)
          sleep(03)
          print("Test Case 66 Executuion Completed")

      @pytest.mark.run(order=67)
      def test_067_Associate_and_Validate_EA_at_authority_zone(self):
          logging.info("associating EA at authority zone")
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox": {"value": "100"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"value": "100"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          sleep(03)
          print("Test Case 67 Executuion Completed")

      @pytest.mark.run(order=68)
      def test_068_Modify_descendants_action(self):
          logging.info("modifying descendant actions to get EA to child objects")
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"descendants_action": {"option_with_ea": "INHERIT","option_without_ea": "INHERIT"},"flags": "I"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",ref=ref1,params="?_inheritance=True&_return_fields=flags",grid_vip=config.grid_vip)
          print(get_ref)
          result = '"flags": "I"'
          if result in get_ref:
               assert True
          else:
               assert False
          print(result)
          sleep(03)
          print("Test Case 68 Executuion Completed")


      @pytest.mark.run(order=69)
      def test_069_Validate_EA_inheritance_at_dns_view(self):
          logging.info("validating EA inheritance at dns view")
          output = ib_NIOS.wapi_request('GET',object_type='view',params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"extattrs": {}'
          if result in output:
                assert True
          else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 69 Executuion Completed")

      @pytest.mark.run(order=70)
      def test_070_Validate_EA_inheritance_at_network_view(self):
          logging.info("validating EA inheritance at network view")
          output = ib_NIOS.wapi_request('GET',object_type="networkview",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"extattrs": {}'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          sleep(03)
          print("Test Case 70 Executuion Completed")

####################################################################################################################################################
########################################## removing the configuration to test other scenario #####################################################
####################################################################################################################################################

      @pytest.mark.run(order=71)
      def test_071_Delete_and_Validate_Extensible_attribute(self):
          logging.info("deleting and validating  extensible attribute to test other scenarios")
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          result = '"name": "infoblox"'
          if result in output:
             assert False
          else:
             assert True
          print(result)
          sleep(03)
          print("Test Case 71 Executuion Completed")


###############################################################################################################################################################################
############## Associating EA at record level and checking at parent(networkview,dnsview,zone) level.(Result : At networkview & dnsview,zone level value should be empty ######
###############################################################################################################################################################################

      @pytest.mark.run(order=72)
      def test_072_Add_and_Validate_Extensible_Attribute_with_enable_inheritance(self):
          logging.info("adding and validating extensible attribute")
          data = {"default_value": "100","name": "infoblox","type": "STRING"}
          response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=default_value,name",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "infoblox"','"default_value": "100"']
          for i in result:
              if i in output:
                  assert True
              else:
                  assert False
          print(result)
          sleep(03)
          print("Test Case 72 Executuion Completed")

      @pytest.mark.run(order=73)
      def test_073_Add_A_record(self):
          logging.info("adding and validating extensible attribute")
          get_ref = ib_NIOS.wapi_request('GET',object_type="record:a",grid_vip=config.grid_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print(ref1)
          output=ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          data = {"ipv4addr": "10.0.0.2","name": "a.test.com","view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          output = ib_NIOS.wapi_request('GET',object_type="record:a",grid_vip=config.grid_vip)
          print(output)
          result = '"name": "a.test.com"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          sleep(03)
          print("Test Case 73 Executuion Completed")

      @pytest.mark.run(order=74)
      def test_074_Associate_and_Validate_EA_at_A_record(self):
          logging.info("associating EA at A record")
          output = ib_NIOS.wapi_request('GET',object_type="record:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          get_ref = ib_NIOS.wapi_request('GET', object_type="record:a", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox": {"value": "100"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          output = ib_NIOS.wapi_request('GET',object_type="record:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"value": "100"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          sleep(03)
          print("Test Case 74 Executuion Completed")


      @pytest.mark.run(order=75)
      def test_075_Modify_descendants_action(self):
          logging.info("modifying descendants action to get EA to child objects")
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"descendants_action": {"option_with_ea": "INHERIT","option_without_ea": "INHERIT"},"flags": "I"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",ref=ref1,params="?_inheritance=True&_return_fields=flags",grid_vip=config.grid_vip)
          print(get_ref)
          result = '"flags": "I"'
          if result in get_ref:
               assert True
          else:
               assert False
          print(result)
          sleep(03)
          print("Test Case 75 Executuion Completed")

      @pytest.mark.run(order=76)
      def test_076_validate_EA_inheritance_at_A_record(self):
          logging.info("validating EA inheritance at A record")
          output = ib_NIOS.wapi_request('GET',object_type="record:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = 'extattrs:infoblox:value:100'
          if result in output:
                  assert True
          else:
                  assert False
          print(result) 
          sleep(03)
          print("Test Case 76 Executuion Completed")


      @pytest.mark.run(order=77)
      def test_077_Add_and_Validate_cname_record(self):
          logging.info("adding and validating cname record") 
          #data = {"canonical": "test.com","name": "caa.test.com","view": "default"}
          #response = ib_NIOS.wapi_request('POST', object_type="record:cname",fields=json.dumps(data),grid_vip=config.grid_vip)
          #print(response)
          output = ib_NIOS.wapi_request('GET',object_type="record:cname",grid_vip=config.grid_vip)
          print(output)
          result = '"name": "caa.test.com"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          sleep(03)
          print("Test Case 77 Executuion Completed")

      @pytest.mark.run(order=78)
      def test_078_Associate_and_Validate_EA_at_cname_record(self):
          logging.info("associating EA at cname record")
          output = ib_NIOS.wapi_request('GET',object_type="record:cname",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          get_ref = ib_NIOS.wapi_request('GET', object_type="record:cname", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox": {"value": "100"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          output = ib_NIOS.wapi_request('GET',object_type="record:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"value": "100"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          sleep(03)
          print("Test Case 78 Executuion Completed")


      @pytest.mark.run(order=79)
      def test_079_Validate_EA_inheritance_at_cname_record(self):
          logging.info("validating EA inheritance at cname record")
          output = ib_NIOS.wapi_request('GET',object_type="record:cname",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          print(output)
          result = 'extattrs:infoblox:value:100'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          sleep(03)
          print("Test Case 79 Executuion Completed")

      @pytest.mark.run(order=80)
      def test_080_Validate_EA_inheritance_at_authority_zone(self):
          logging.info("validating EA inheritance at authority zone")
          output = ib_NIOS.wapi_request('GET',object_type='zone_auth',params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"extattrs": {}'
          if result in output:
                assert True
          else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 80 Executuion Completed")


      @pytest.mark.run(order=81)
      def test_081_Validate_EA_inheritance_at_dns_view(self):
          logging.info("validating EA inheritance at dns view")
          output = ib_NIOS.wapi_request('GET',object_type='view',params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"extattrs": {}'
          if result in output:
                assert True
          else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 81 Executuion Completed")

      @pytest.mark.run(order=82)
      def test_082_Validate_EA_inheritance_at_network_view(self):
          logging.info("validating EA inheritance at network view")
          output = ib_NIOS.wapi_request('GET',object_type="networkview",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"extattrs": {}'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          sleep(03)
          print("Test Case 82 Executuion Completed")

####################################################################################################################################################
########################################## removing the configuration to test other scenario #####################################################
####################################################################################################################################################

      @pytest.mark.run(order=83)
      def test_083_Delete_and_Validate_Authority_zone(self):
          logging.info("deleting and validating  authority zone")
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[0]['_ref']
          #print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          print(output)
          if 'test.com' in output:
             assert False
          else:
             assert True
          sleep(03)
          print("Test Case 83 Executuion Completed")

      @pytest.mark.run(order=84)
      def test_084_Delete_and_Validate_Extensible_attribute(self):
          logging.info("deleting and validating  extensible attri bute to test other scenarios")
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          result = '"name": "infoblox"'
          if result in output:
             assert False
          else:
             assert True
          sleep(03)
          print("Test Case 84 Executuion Completed")

############################################################################################################################
####################Testing option_with_ea : retain, EA that already exists on a descendant#################################
############################################################################################################################

      @pytest.mark.run(order=85)
      def test_085_Add_and_Validate_Extensible_Attribute_with_enable_inheritance(self):
          logging.info("adding and validating extensible attribute")
          data = {"default_value": "100","name": "infoblox","type": "STRING"}
          response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=default_value,name",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "infoblox"','"default_value": "100"']
          for i in result:
              if i in output:
                  assert True
              else:
                  assert False
          print(result)
          sleep(03)
          print("Test Case 85 Executuion Completed")

      @pytest.mark.run(order=86)
      def test_086_Add_and_Validate_authority_zone(self):
          logging.info("adding and validating authority zone")
          data = {"fqdn": "test.com","view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print(ref1)
          result = 'test.com'
          if result in ref1:
               assert True
               print("Authority zone has created")
          else:
               assert False
          print(result)
          sleep(03)
          print("Test Case 86 Executuion Completed")

      @pytest.mark.run(order=87)
      def test_087_Add_and_Validate_A_record(self):
          logging.info("adding and validating A record")
          data = {"ipv4addr": "10.0.0.2","name": "a.test.com","view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          output = ib_NIOS.wapi_request('GET',object_type="record:a",grid_vip=config.grid_vip)
          print(output)
          result = '"name": "a.test.com"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          sleep(03)
          print("Test Case 87 Executuion Completed")

      @pytest.mark.run(order=88)
      def test_088_Associate_and_Validate_EA_at_cname_record(self):
          logging.info("associating EA at cname record")
          get_ref = ib_NIOS.wapi_request('GET', object_type="record:a", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox": {"value": "100"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          output = ib_NIOS.wapi_request('GET',object_type="record:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"value": "100"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          sleep(03)
          print("Test Case 88 Executuion Completed")

      @pytest.mark.run(order=89)
      def test_089_Associate_and_Validate_EA_at_authority_zone(self):
          logging.info("associating EA at authority zone")
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox": {"value": "100"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"value": "100"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          sleep(03)
          print("Test Case 89 Executuion Completed")

      @pytest.mark.run(order=90)
      def test_090_Modify_descendants_action(self):
          logging.info("modifying descendants action to get EA to child objects")
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"descendants_action": {"option_with_ea": "RETAIN","option_without_ea": "INHERIT"},"flags": "I"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",ref=ref1,params="?_inheritance=True&_return_fields=flags",grid_vip=config.grid_vip)
          print(get_ref)
          result = '"flags": "I"'
          if result in get_ref:
               assert True
          else:
               assert False
          print(result)
          print("Test Case 90 Executuion Completed")

      @pytest.mark.run(order=91)
      def test_091_Validate_EA_inheritance_at_A_record(self):
          logging.info("validating EA inheritance at A record")
          output = ib_NIOS.wapi_request('GET',object_type="record:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = "extattrs:infoblox:value:100"
          if result in output:
                assert True
          else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 91 Executuion Completed")

##########################################################################################################################
###############################removing the configuration to test other scenario########################################
##########################################################################################################################

      @pytest.mark.run(order=92)
      def test_092_Delete_and_Validate_Authority_zone(self):
          logging.info("deleting and validating  authority zone")
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[0]['_ref']
          #print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          print(output)
          if 'test.com' in output:
             assert False
          else:
             assert True
          print("Test Case 92 Executuion Completed")

      @pytest.mark.run(order=93)
      def test_093_Delete_and_Validate_Extensible_attribute(self):
          logging.info("deleting and validating  extensible attribute to test other scenarios")
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          if '"name": "infoblox"' in output:
             assert False
          else:
             assert True
          print("Test Case 93 Executuion Completed")

#########################################################################################################################################################
##Testing option_with_ea : CONVERT,EA that already exists on a descendant with same values on child and parent.Child will inherit the value from parent##
#########################################################################################################################################################



      @pytest.mark.run(order=94)
      def test_094_Add_and_Validate_Extensible_Attribute_with_enable_inheritance(self):
          logging.info("adding and validating extensible attribute")
          data = {"default_value": "100","name": "infoblox","type": "STRING"}
          response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=default_value,name",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "infoblox"','"default_value": "100"']
          for i in result:
              if i in output:
                  assert True
              else:
                  assert False
          print(result)
          print("Test Case 94 Executuion Completed")

      @pytest.mark.run(order=95)
      def test_095_Add_and_Validate_authority_zone(self):
          logging.info("adding and validating authority zone")
          data = {"fqdn": "test.com","view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print(ref1)
          result = 'test.com'
          if result in ref1:
               assert True
               print("Authority zone has created")
          else:
               assert False
          print("Test Case 95 Executuion Completed")

      @pytest.mark.run(order=96)
      def test_096_Add_A_record(self):
          logging.info("adding A record")
          data = {"ipv4addr": "10.0.0.2","name": "a.test.com","view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="record:a",grid_vip=config.grid_vip)
          print(output)
          result = '"name": "a.test.com"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 96 Executuion Completed")

      @pytest.mark.run(order=97)
      def test_097_Associate_and_Validate_EA_at_A_record(self):
          logging.info("associating EA at A record")
          get_ref = ib_NIOS.wapi_request('GET', object_type="record:a", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox": {"value": "100"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="record:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"value": "100"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 97 Executuion Completed")

      @pytest.mark.run(order=98)
      def test_098_Associate_and_Validate_EA_at_authority_zone(self):
          logging.info("associating EA at authority zone")
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox": {"value": "100"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"value": "100"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 98 Executuion Completed")

      @pytest.mark.run(order=99)
      def test_099_Modify_descendants_action(self):
          logging.info("modifying descendants action to get EA to child objects")
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"descendants_action": {"option_with_ea": "CONVERT","option_without_ea": "NOT_INHERIT"},"flags": "I"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",ref=ref1,params="?_inheritance=True&_return_fields=flags",grid_vip=config.grid_vip)
          print(get_ref)
          result = '"flags": "I"'
          if result in get_ref:
               assert True
          else:
               assert False
          print(result)
          print("Test Case 99 Executuion Completed")

      @pytest.mark.run(order=100)
      def test_100_Validate_EA_inheritance_at_A_record(self):
          logging.info("validating EA inheritance at A record")
          output = ib_NIOS.wapi_request('GET',object_type="record:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ["inheritance_source::zone_auth","value:100"]
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 100 Executuion Completed")


##########################################################################################################################
############################### removing the configuration to test other scenario ######################################
##########################################################################################################################


      @pytest.mark.run(order=101)
      def test_101_Delete_and_Validate_Authority_zone(self):
          logging.info("deleting and validating  authority zone")
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[0]['_ref']
          #print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          if 'test.com' in output:
             assert False
          else:
             assert True
          print("Test Case 101 Executuion Completed")

      @pytest.mark.run(order=102)
      def test_102_Delete_and_Validate_Extensible_attribute(self):
          logging.info("deleting and validating  extensible attribute to test other scenarios")
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          #print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          #print(output)
          if '"name": "infoblox"' in output:
             assert False
          else:
             assert True
          print("Test Case 102 Executuion Completed")


##################################################################################################################################################################
## Testing option_with_ea : CONVERT,EA that already exists on a descendant with different values on child and parent.Child will Overriden the value from parent ##
##################################################################################################################################################################

      @pytest.mark.run(order=103)
      def test_103_Add_and_Validate_Extensible_Attribute_with_enable_inheritance(self):
          logging.info("adding and validating extensible attribute")
          data = {"default_value": "100","name": "infoblox","type": "STRING"}
          response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=default_value,name",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "infoblox"','"default_value": "100"']
          for i in result:
              if i in output:
                  assert True
              else:
                  assert False
          print(result)
          print("Test Case 103 Executuion Completed")

      @pytest.mark.run(order=104)
      def test_104_Create_Authority_zone(self):
          logging.info("creating authority zone")
          data = {"fqdn": "test.com","view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print(ref1)
          result = 'test.com'
          if result in ref1:
               assert True
               print("Authority zone has created")
          else:
               assert False
          print("Test Case 104 Executuion Completed")

      @pytest.mark.run(order=105)
      def test_105_Add_A_record(self):
          logging.info("adding A record")
          data = {"ipv4addr": "10.0.0.2","name": "a.test.com","view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="record:a",grid_vip=config.grid_vip)
          print(output)
          result = '"name": "a.test.com"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 105 Executuion Completed")

      @pytest.mark.run(order=106)
      def test_106_Associate_and_Validate_EA_at_A_record(self):
          logging.info("associating EA at A record")
          get_ref = ib_NIOS.wapi_request('GET', object_type="record:a", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox": {"value": "200"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          output = ib_NIOS.wapi_request('GET',object_type="record:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"value": "200"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 106 Executuion Completed")

      @pytest.mark.run(order=107)
      def test_107_Associate_and_Validate_EA_at_authority_zone(self):
          logging.info("associating created EA at authority zone")
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox": {"value": "100"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"value": "100"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 107 Executuion Completed")

      @pytest.mark.run(order=108)
      def test_108_Modify_descendants_action(self):
          logging.info("modifying descendant actions to get EA to child objects")
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"descendants_action": {"option_with_ea": "CONVERT","option_without_ea": "NOT_INHERIT"},"flags": "I"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",ref=ref1,params="?_inheritance=True&_return_fields=flags",grid_vip=config.grid_vip)
          print(get_ref)
          result = '"flags": "I"'
          if result in get_ref:
               assert True
          else:
               assert False
          print(result)
          print("Test Case 108 Executuion Completed")


      @pytest.mark.run(order=109)
      def test_109_Validate_EA_inheritance_at_A_record(self):
          logging.info("validating EA inheritance at A record")
          output = ib_NIOS.wapi_request('GET',object_type="record:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = "extattrs:infoblox:value:200"
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 109 Executuion Completed")


##########################################################################################################################
############################## removing the configuration to test other scenario #######################################
##########################################################################################################################

      @pytest.mark.run(order=110)
      def test_110_Delete_and_Validate_Authority_zone(self):
          logging.info("deleting and validating  authority zone")
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[0]['_ref']
          #print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          print(output)
          if 'test.com' in output:
             assert False
          else:
             assert True
          print("Test Case 110 Executuion Completed")

      @pytest.mark.run(order=111)
      def test_111_Delete_and_Validate_Extensible_attribute(self):
          logging.info("deleting and validating  extensible attribute to test other scenarions")
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          #print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          #print(output)
          if '"name": "infoblox"' in output:
             assert False
          else:
             assert True
          print("Test Case 111 Executuion Completed")


###########################################################################################################################################################
## Testing option_with_ea : Inherit,EA that already exists on a descendant with same values on child and parent.Child will inherit the value from parent ##
###########################################################################################################################################################

      @pytest.mark.run(order=112)
      def test_112_Add_and_Validate_Extensible_Attribute_with_enable_inheritance(self):
          logging.info("adding and validating extensible attribute")
          data = {"default_value": "100","name": "infoblox","type": "STRING"}
          response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=default_value,name",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "infoblox"','"default_value": "100"']
          for i in result:
              if i in output:
                  assert True
              else:
                  assert False
          print(result)
          print("Test Case 112 Executuion Completed")

      @pytest.mark.run(order=113)
      def test_113_Create_authority_zone(self):
          logging.info("creating authority zone")
          data = {"fqdn": "test.com","view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print(ref1)
          result = 'test.com'
          if result in ref1:
               assert True
               print("Authority zone has created")
          else:
               assert False
          print("Test Case 113 Executuion Completed")

      @pytest.mark.run(order=114)
      def test_114_Add_A_record(self):
          logging.info("adding A record")
          data = {"ipv4addr": "10.0.0.2","name": "a.test.com","view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="record:a",grid_vip=config.grid_vip)
          print(output)
          result = '"name": "a.test.com"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 114 Executuion Completed")

      @pytest.mark.run(order=115)
      def test_115_Associate_and_Validate_EA_at_A_record(self):
          logging.info("associating EA at A record")
          get_ref = ib_NIOS.wapi_request('GET', object_type="record:a", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox": {"value": "100"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="record:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"value": "100"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 115 Executuion Completed")

      @pytest.mark.run(order=116)
      def test_116_Associate_and_Validate_EA_at_authority_zone(self):
          logging.info("associating EA at authority zone")
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox": {"value": "100"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"value": "100"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 116 Executuion Completed")

      @pytest.mark.run(order=117)
      def test_117_Modify_descendants_action(self):
          logging.info("modifying descendants action to get EA to child objects")
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"descendants_action": {"option_with_ea": "INHERIT","option_without_ea": "NOT_INHERIT"},"flags": "I"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",ref=ref1,params="?_inheritance=True&_return_fields=flags",grid_vip=config.grid_vip)
          print(get_ref)
          result = '"flags": "I"'
          if result in get_ref:
               assert True
          else:
               assert False
          print(result)
          print("Test Case 117 Executuion Completed")

      @pytest.mark.run(order=118)
      def test_118_Validate_EA_inheritance_at_A_record(self):
          output = ib_NIOS.wapi_request('GET',object_type="record:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ["inheritance_source::zone_auth","value:100"]
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 118 Executuion Completed")


##########################################################################################################################
############################## removing the configuration to test other scenario #######################################
##########################################################################################################################


      @pytest.mark.run(order=119)
      def test_119_Delete_and_Validate_Authority_zone(self):
          logging.info("deleting and validating  authority zone")
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[0]['_ref']
          #print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          print(output)
          if 'test.com' in output:
             assert False
          else:
             assert True
          print("Test Case 119 Executuion Completed")

      @pytest.mark.run(order=120)
      def test_120_Delete_and_Validate_Extensible_attribute(self):
          logging.info("deleting and validating  extensible attribute to test other scenarios")
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          #print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          #print(output)
          if '"name": "infoblox"' in output:
             assert False
          else:
             assert True
          print("Test Case 120 Executuion Completed")


################################################################################################################################################################
## Testing option_with_ea : Inherit,EA that already exists on a descendant with different values on child and parent.Child will inherit the value from parent ##
################################################################################################################################################################

      @pytest.mark.run(order=121)
      def test_121_Add_and_Validate_Extensible_Attribute_with_enable_inheritance(self):
          logging.info("adding and validating extensible attribute")
          data = {"default_value": "100","name": "infoblox","type": "STRING"}
          response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=default_value,name",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "infoblox"','"default_value": "100"']
          for i in result:
              if i in output:
                  assert True
              else:
                  assert False
          print(result)
          print("Test Case 121 Executuion Completed")

      @pytest.mark.run(order=122)
      def test_122_Create_authority_zone(self):
          logging.info("creating authority zone")
          data = {"fqdn": "test.com","view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print(ref1)
          result = 'test.com'
          if result in ref1:
               assert True
               print("Authority zone has created")
          else:
               assert False
          print("Test Case 122 Executuion Completed")

      @pytest.mark.run(order=123)
      def test_123_Add_A_record(self):
          logging.info("adding A record")
          data = {"ipv4addr": "10.0.0.2","name": "a.test.com","view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="record:a",grid_vip=config.grid_vip)
          print(output)
          result = '"name": "a.test.com"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 123 Executuion Completed")

      @pytest.mark.run(order=124)
      def test_124_Associate_and_Validate_EA_at_A_record(self):
          logging.info("associating EA at A record")
          get_ref = ib_NIOS.wapi_request('GET', object_type="record:a", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox": {"value": "200"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="record:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"value": "200"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 124 Executuion Completed")

      @pytest.mark.run(order=125)
      def test_125_Associate_and_Validate_EA_at_authority_zone(self):
          logging.info("associating EA at authority zone")
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox": {"value": "100"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"value": "100"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 125 Executuion Completed")

      @pytest.mark.run(order=126)
      def test_126_Modify_descendants_action(self):
          logging.info("modifying descendant actions to get EA to child objects")
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"descendants_action": {"option_with_ea": "INHERIT","option_without_ea": "NOT_INHERIT"},"flags": "I"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",ref=ref1,params="?_inheritance=True&_return_fields=flags",grid_vip=config.grid_vip)
          print(get_ref)
          result = '"flags": "I"'
          if result in get_ref:
               assert True
          else:
               assert False
          print(result)
          print("Test Case 126 Executuion Completed")

      @pytest.mark.run(order=127)
      def test_127_Validate_EA_inheritance_at_A_record(self):
          logging.info("validating EA inheritance at A record")
          output = ib_NIOS.wapi_request('GET',object_type="record:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ["inheritance_source::zone_auth","value:100"]
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 127 Executuion Completed")


##########################################################################################################################
############################## removing the configuration to test other scenario #######################################
##########################################################################################################################

      @pytest.mark.run(order=128)
      def test_128_Delete_and_Validate_Authority_zone(self):
          logging.info("deleting and validating  authority zone")
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[0]['_ref']
          #print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          print(output)
          if 'test.com' in output:
             assert False
          else:
             assert True
          print("Test Case 128 Executuion Completed")

      @pytest.mark.run(order=129)
      def test_129_Delete_and_Validate_Extensible_attribute(self):
          logging.info("deleting and validating  extensible attribute to test other scenarios")
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          #print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          #print(output)
          if '"name": "infoblox"' in output:
             assert False
          else:
             assert True
          print("Test Case 129 Executuion Completed")



##############################################################################################################################################################
################# Testing option_without_ea : Not_Inherit,EA that does not exists on a descendant. Child will inherit the value from parent ##################
##############################################################################################################################################################

      @pytest.mark.run(order=130)
      def test_130_Add_and_Validate_Extensible_Attribute_with_enable_inheritance(self):
          logging.info("adding and validating extensible attribute")
          data = {"default_value": "100","name": "infoblox","type": "STRING"}
          response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=default_value,name",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "infoblox"','"default_value": "100"']
          for i in result:
              if i in output:
                  assert True
              else:
                  assert False
          print(result)
          print("Test Case 130 Executuion Completed")

      @pytest.mark.run(order=131)
      def test_131_Create_Authority_zone(self):
          logging.info("creating authority zone")
          data = {"fqdn": "test.com","view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print(ref1)
          result = 'test.com'
          if result in ref1:
               assert True
               print("Authority zone has created")
          else:
               assert False
          print("Test Case 131 Executuion Completed")

      @pytest.mark.run(order=132)
      def test_132_Add_and_Validate_A_record(self):
          logging.info("adding and validating A record")
          data = {"ipv4addr": "10.0.0.2","name": "a.test.com","view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="record:a",grid_vip=config.grid_vip)
          print(output)
          result = '"name": "a.test.com"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 132 Executuion Completed")

      @pytest.mark.run(order=133)
      def test_133_Associate_and_Validate_EA_at_authority_zone(self):
          logging.info("associating EA at authority zone")
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox": {"value": "100"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"value": "100"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 133 Executuion Completed")

      @pytest.mark.run(order=134)
      def test_134_Modify_descendants_action(self):
          logging.info("modifying descendant actions to GET EA to child objects")
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"descendants_action": {"option_without_ea": "NOT_INHERIT"},"flags": "I"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",ref=ref1,params="?_inheritance=True&_return_fields=flags",grid_vip=config.grid_vip)
          print(get_ref)
          result = '"flags": "I"'
          if result in get_ref:
               assert True
          else:
               assert False
          print(result)
          print("Test Case 134 Executuion Completed")

      @pytest.mark.run(order=135)
      def test_135_Validate_EA_inheritance_at_A_record(self):
          logging.info("validating EA inheritance at A record")
          output = ib_NIOS.wapi_request('GET',object_type="record:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"extattrs": {}'
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 135 Executuion Completed")


##########################################################################################################################
############################## removing the configuration to test other scenario #######################################
##########################################################################################################################

      @pytest.mark.run(order=136)
      def test_136_Delete_and_Validate_Authority_zone(self):
          logging.info("deleting and validating  authority zone")
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[0]['_ref']
          #print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          print(output)
          if 'test.com' in output:
             assert False
          else:
             assert True
          print("Test Case 136 Executuion Completed")

      @pytest.mark.run(order=137)
      def test_137_Delete_and_Validate_Extensible_attribute(self):
          logging.info("deleting and validating  extensible attribute")
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          #print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          #print(output)
          if '"name": "infoblox"' in output:
             assert False
          else:
             assert True
          print("Test Case 137 Executuion Completed")



##############################################################################################################################################################
################# Testing option_without_ea : Inherit,EA that does not exists on a descendant. Child will inherit the value from parent ######################
##############################################################################################################################################################

      @pytest.mark.run(order=138)
      def test_138_Add_and_Validate_Extensible_Attribute_with_enable_inheritance(self):
          logging.info("adding and validating extensible attribute")
          data = {"default_value": "100","name": "infoblox","type": "STRING"}
          response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=default_value,name",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "infoblox"','"default_value": "100"']
          for i in result:
              if i in output:
                  assert True
              else:
                  assert False
          print(result)
          print("Test Case 138 Executuion Completed")

      @pytest.mark.run(order=139)
      def test_139_Create_authority_zone(self):
          logging.info("creating authority zone")
          data = {"fqdn": "test.com","view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)     
          sleep(03)
          get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print(ref1)
          result = 'test.com'
          if result in ref1:
               assert True
               print("Authority zone has created")
          else:
               assert False
          print("Test Case 139 Executuion Completed")

      @pytest.mark.run(order=140)
      def test_140_Add_A_record(self):
          logging.info("adding A record")
          data = {"ipv4addr": "10.0.0.2","name": "a.test.com","view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="record:a",grid_vip=config.grid_vip)
          print(output)
          result = '"name": "a.test.com"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 140 Executuion Completed")

      @pytest.mark.run(order=141)
      def test_141_Associate_and_Validate_EA_at_authority_zone(self):
          logging.info("associating EA at authority zone")
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox": {"value": "100"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"value": "100"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 141 Executuion Completed")

      @pytest.mark.run(order=142)
      def test_142_Modify_descendants_action(self):
          logging.info("modifying descendant action to get EA to child objects")
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"descendants_action": {"option_without_ea": "INHERIT"},"flags": "I"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",ref=ref1,params="?_inheritance=True&_return_fields=flags",grid_vip=config.grid_vip)
          print(get_ref)
          result = '"flags": "I"'
          if result in get_ref:
               assert True
          else:
               assert False
          print(result)
          print("Test Case 142 Executuion Completed")

      @pytest.mark.run(order=143)
      def test_143_Validate_EA_inheritance_at_A_record(self):
          logging.info("validating EA inheritance at A record")
          output = ib_NIOS.wapi_request('GET',object_type="record:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ["inheritance_source::zone_auth","value:100"]
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 143 Executuion Completed")


##########################################################################################################################
############################## removing the configuration to test other scenario #######################################
##########################################################################################################################

      @pytest.mark.run(order=144)
      def test_144_Delete_and_Validate_Authority_zone(self):
          logging.info("deleting and validating  authority zone")
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[0]['_ref']
          #print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          print(output)
          if 'test.com' in output:
             assert False
          else:
             assert True
          print("Test Case 144 Executuion Completed")

      @pytest.mark.run(order=145)
      def test_145_Delete_and_Validate_Extensible_attribute(self):
          logging.info("deleting and validating  extensible attribute")
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          #print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          #print(output)
          if '"name": "infoblox"' in output:
             assert False
          else:
             assert True
          print("Test Case 145 Executuion Completed")


######################################################################################################################
############# Scenario : When parent is Not inherited child should not get the inheritance value #####################
######################################################################################################################

      @pytest.mark.run(order=146)
      def test_146_Add_and_Validate_Extensible_Attribute_with_enable_inheritance(self):
          logging.info("adding and validating extensible attribute")
          data = {"default_value": "100","name": "infoblox","type": "STRING"}
          response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=default_value,name",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "infoblox"','"default_value": "100"']
          for i in result:
              if i in output:
                  assert True
              else:
                  assert False
          print(result)
          print("Test Case 146 Executuion Completed")

      @pytest.mark.run(order=147)
      def test_147_Create_authority_zone(self):
          logging.info("creating authority zone")
          data = {"fqdn": "test.com","view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print(ref1)
          result = 'test.com'
          if result in ref1:
               assert True
               print("Authority zone has created")
          else:
               assert False
          print("Test Case 147 Executuion Completed")

      @pytest.mark.run(order=148)
      def test_148_Associate_and_Validate_EA_at_dns_view(self):
          logging.info("associating EA at dns view")
          output = ib_NIOS.wapi_request('GET',object_type="view",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          get_ref = ib_NIOS.wapi_request('GET', object_type="view", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox": {"value": "100"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          output = ib_NIOS.wapi_request('GET',object_type="view",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"value": "100"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 148 Executuion Completed")

      @pytest.mark.run(order=149)
      def test_149_Modify_descendants_action(self):
          logging.info("modifying descendant actions to get EA to child objects")
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"descendants_action": {"option_without_ea": "NOT_INHERIT"},"flags": "I"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",ref=ref1,params="?_inheritance=True&_return_fields=flags",grid_vip=config.grid_vip)
          print(get_ref)
          result = '"flags": "I"'
          if result in get_ref:
               assert True
          else:
               assert False
          print(result)
          print("Test Case 149 Executuion Completed")

      @pytest.mark.run(order=150)
      def test_150_Add_and_Validate_A_record(self):
          logging.info("adding and validating A record")
          data = {"ipv4addr": "10.0.0.2","name": "a.test.com","view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="record:a",grid_vip=config.grid_vip)
          print(output)
          result = '"name": "a.test.com"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 150 Executuion Completed")

      @pytest.mark.run(order=151)
      def test_151_Add_and_Validate_cname_record(self):
          logging.info("adding and validating cname record")
          data = {"canonical": "test.com","name": "caa.test.com","view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="record:cname",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="record:cname",grid_vip=config.grid_vip)
          print(output)
          result = '"name": "caa.test.com"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 151 Executuion Completed")

      @pytest.mark.run(order=152)
      def test_152_Validate_EA_inheritance_at_A_record(self):
          logging.info("validating EA inheritance at A record")
          output = ib_NIOS.wapi_request('GET',object_type="record:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"extattrs": {}'
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 152 Executuion Completed")


      @pytest.mark.run(order=153)
      def test_153_Validate_EA_inheritance_at_CNAME_record(self):
          logging.info("validating EA inheritance at CNAME record")
          output = ib_NIOS.wapi_request('GET',object_type="record:cname",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"extattrs": {}'
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 153 Executuion Completed")

##########################################################################################################################
############################### removing the configuration to test other scenario ######################################
##########################################################################################################################

      @pytest.mark.run(order=154)
      def test_154_Delete_and_Validate_Authority_zone(self):
          logging.info("deleting and validating  authority zone")
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[0]['_ref']
          #print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          print(output)
          if 'test.com' in output:
             assert False
          else:
             assert True
          print("Test Case 154 Executuion Completed")

      @pytest.mark.run(order=155)
      def test_155_Delete_and_Validate_Extensible_attribute(self):
          logging.info("deleting and validating  extensible attribute to get EA to child objects")
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          #print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          #print(output)
          if '"name": "infoblox"' in output:
             assert False
          else:
             assert True
          print("Test Case 155 Executuion Completed")


################################################################################
############################### Vlan Scenarions Started ########################
################################################################################


###############################################################################################################################################
#### Associating EA at vlanview and checking at child(vlanrange,vlan) level. (Result : Child should inherit the value from vlanview ###########
###############################################################################################################################################

      @pytest.mark.run(order=156)
      def test_156_Add_and_Validate_Extensible_attribute(self):
          logging.info("adding and validating extensible attribute")
          data = {"default_value": "100","name": "infoblox","type": "STRING"}
          response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=default_value,name",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "infoblox"','"default_value": "100"']
          for i in result:
              if i in output:
                  assert True
              else:
                  assert False
          print(result)
          print("Test Case 156 Executuion Completed")

      @pytest.mark.run(order=157)
      def test_157_Create_and_Validate_vlan_range(self):
          logging.info("creating and validating vlan range")
          get_ref = ib_NIOS.wapi_request('GET',object_type="vlanview",grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          res = eval(json.dumps(res))
          #print(res)
          ref1=(res)[0]['_ref']
          print(ref1)
          data = {"end_vlan_id": 5,"name": "range","start_vlan_id": 1,"vlan_view": ref1}
          response = ib_NIOS.wapi_request('POST', object_type="vlanrange",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          get_ref = ib_NIOS.wapi_request('GET',object_type="vlanrange",grid_vip=config.grid_vip)
          #res = json.loads(get_ref)
          #ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          result = ['"end_vlan_id": 5','"start_vlan_id": 1','"name": "range"']
          for i in result:
            if i in get_ref:
               assert True
            else:
               assert False
          print(result)
          print("Test Case 157 Executuion Completed")

      @pytest.mark.run(order=158)
      def test_158_Create_and_Validating_static_vlan(self):
          logging.info("creating and validating static vlan")
          get_ref = ib_NIOS.wapi_request('GET',object_type="vlanview",grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          res = eval(json.dumps(res))
          #print(res)
          ref1=(res)[0]['_ref']
          print(ref1)
          data = {"id": 6,"name": "staticvlan","parent": ref1}
          response = ib_NIOS.wapi_request('POST', object_type="vlan",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          get_ref = ib_NIOS.wapi_request('GET',object_type="vlan",grid_vip=config.grid_vip)
          #res = json.loads(get_ref)
          #ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          result = ['"id": 6','"name": "staticvlan"']
          for i in result:
            if i in get_ref:
               assert True
            else:
               assert False
          print(result)
          print("Test Case 158 Executuion Completed")


      @pytest.mark.run(order=159)
      def test_159_Associate_and_Validate_EA_at_vlan_view(self):
          logging.info("associating EA at vlan view")
          get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox": {"value": "100"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="vlanview",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"value": "100"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 159 Executuion Completed")

      @pytest.mark.run(order=160)
      def test_160_Modify_descendants_action(self):
          logging.info("modifying descendant actions to get EA to to child objects")
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"descendants_action": {"option_without_ea": "INHERIT"},"flags": "I"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",ref=ref1,params="?_inheritance=True&_return_fields=flags",grid_vip=config.grid_vip)
          print(get_ref)
          result = '"flags": "I"'
          if result in get_ref:
               assert True
          else:
               assert False
          print(result)
          print("Test Case 160 Executuion Completed")

      @pytest.mark.run(order=161)
      def test_161_Validading_EA_inheritance_at_vlan_range(self):
          logging.info("validating EA inheritance at vlan range")
          output = ib_NIOS.wapi_request('GET',object_type="vlanrange",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          print(output)
          result = ['inheritance_source::vlanview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 161 Executuion Completed")

      @pytest.mark.run(order=162)
      def test_162_Validate_EA_inheritance_at_static_vlan(self):
          logging.info("validating EA inheritance at static vlan")
          output = ib_NIOS.wapi_request('GET',object_type="vlan",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['inheritance_source::vlanview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 162 Executuion Completed")


####################################################################################################################################################
########################################## removing the configuration to test other scenario #####################################################
####################################################################################################################################################

      @pytest.mark.run(order=163)
      def test_163_Delete_and_Validate_Extensible_attribute(self):
          logging.info("deleting and validating  extensible attribute to test other scenarios")
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          #print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          #print(output)
          result = '"name": "infoblox"'
          if result in output:
             assert False
          else:
             assert True
          print(result)
          print("Test Case 163 Executuion Completed")


###################################################################################################################################################################
#### Associating EA at vlanrange and checking at parent(vlanview) and at vlan level.(Result : valanview and vlan should not inherit the value from vlanview ######
###################################################################################################################################################################


      @pytest.mark.run(order=164)
      def test_164_Add_and_Validate_Extensible_attribute(self):
          logging.info("adding and validating extensible attribute")
          data = {"default_value": "100","name": "infoblox","type": "STRING"}
          response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=default_value,name",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "infoblox"','"default_value": "100"']
          for i in result:
              if i in output:
                  assert True
              else:
                  assert False
          print(result)
          print("Test Case 164 Executuion Completed")

      @pytest.mark.run(order=165)
      def test_165_Associate_and_Validate_EA_at_vlan_range(self):
          logging.info("associating Ea at vlan range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="vlanrange", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox": {"value": "100"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="vlanrange",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"value": "100"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 165 Executuion Completed")

      @pytest.mark.run(order=166)
      def test_166_Modify_descendants_actions(self):
          logging.info("modifying descendant actions to get EA to child objects")
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"descendants_action": {"option_with_ea": "INHERIT","option_without_ea": "INHERIT"},"flags": "I"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",ref=ref1,params="?_inheritance=True&_return_fields=flags",grid_vip=config.grid_vip)
          print(get_ref)
          result = '"flags": "I"'
          if result in get_ref:
               assert True
          else:
               assert False
          print(result)
          print("Test Case 166 Executuion Completed")

      @pytest.mark.run(order=167)
      def test_167_Validate_EA_inheritance_at_vlan_view(self):
          logging.info("validating EA inheritance at vlan view")
          output = ib_NIOS.wapi_request('GET',object_type="vlanview",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"extattrs": {}'
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 167 Executuion Completed")


      @pytest.mark.run(order=168)
      def test_168_Validate_EA_inheritance_at_static_vlan(self):
          logging.info("validating EA inheritance at static vlan")
          output = ib_NIOS.wapi_request('GET',object_type="vlan",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"extattrs": {}'
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 168 Executuion Completed")


####################################################################################################################################################
########################################## removing the configuration to test other scenario #####################################################
####################################################################################################################################################

      @pytest.mark.run(order=169)
      def test_169_Delete_and_Validate_Extensible_attribute(self):
          logging.info("deleting and validating  extensible attribute")
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          #print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          #print(output)
          result = '"name": "infoblox"'
          if result in output:
             assert False
          else:
             assert True
          print(result)
          print("Test Case 169 Executuion Completed")

##################################################################################################################################################################
#### Associating EA at vlan and checking at parent(vlanview) and at vlanrange level.(Result : valanview and vlanrange should not inherit the value from vlan #####
##################################################################################################################################################################


      @pytest.mark.run(order=170)
      def test_170_Add_and_Validate_Extensible_attribute(self):
          logging.info("adding and validating extensible attribute")
          data = {"default_value": "100","name": "infoblox","type": "STRING"}
          response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=default_value,name",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "infoblox"','"default_value": "100"']
          for i in result:
              if i in output:
                  assert True
              else:
                  assert False
          print(result)
          print("Test Case 170 Executuion Completed")

      @pytest.mark.run(order=171)
      def test_171_Associating_EA_at_vlan(self):
          logging.info("associate EA at static vlan")
          get_ref = ib_NIOS.wapi_request('GET', object_type="vlan", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox": {"value": "100"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="vlan",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"value": "100"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 171 Executuion Completed")

      @pytest.mark.run(order=172)
      def test_172_Modify_descendants_action(self):
          logging.info("modifying descendant actions to get EA to child objects")
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"descendants_action": {"option_with_ea": "INHERIT","option_without_ea": "INHERIT"},"flags": "I"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",ref=ref1,params="?_inheritance=True&_return_fields=flags",grid_vip=config.grid_vip)
          print(get_ref)
          result = '"flags": "I"'
          if result in get_ref:
               assert True
          else:
               assert False
          print(result)
          print("Test Case 172 Executuion Completed")

      @pytest.mark.run(order=173)
      def test_173_Validate_EA_inheritance_at_vlanview(self):
          output = ib_NIOS.wapi_request('GET',object_type="vlanview",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"extattrs": {}'
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 173 Executuion Completed")

      @pytest.mark.run(order=174)
      def test_174_Validate_EA_inheritance_at_vlan_range(self):
          logging.info("validating EA inheritance at vlan range")
          output = ib_NIOS.wapi_request('GET',object_type="vlanrange",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"extattrs": {}'
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 174 Executuion Completed")



####################################################################################################################################################
########################################## removing the configuration to test other scenario #####################################################
####################################################################################################################################################

      @pytest.mark.run(order=175)
      def test_175_Delete_and_Validate_Extensible_attribute(self):
          logging.info("deleting and validating  extensible attribute to test other scenarios")
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          #print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          #print(output)
          result = '"name": "infoblox"'
          if result in output:
             assert False
          else:
             assert True
          print(result)
          print("Test Case 175 Executuion Completed")


####################################################################################################################################################
##### Checking the option_with_ea : retain,EA that already exists on a descendant. Result: at child inheritance state should show as Override ######
####################################################################################################################################################

      @pytest.mark.run(order=176)
      def test_176_Add_and_Validate_Extensible_Attribute_with_enable_inheritance(self):
          logging.info("adding and validating extensible attribute")
          data = {"default_value": "100","name": "infoblox","type": "STRING"}
          response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=default_value,name",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "infoblox"','"default_value": "100"']
          for i in result:
              if i in output:
                  assert True
              else:
                  assert False
          print(result)
          print("Test Case 176 Executuion Completed")

      @pytest.mark.run(order=177)
      def test_177_Associate_and_Validate_EA_at_vlan_range(self):
          logging.info("associating created EA at vlan range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="vlanrange", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox": {"value": "100"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="vlanrange",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"value": "100"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 177 Executuion Completed")

      @pytest.mark.run(order=178)
      def test_178_Associate_and_Validate_EA_at_vlan_view(self):
          logging.info("associate EA at vlan view")
          get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox": {"value": "100"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="vlanview",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"value": "100"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 178 Executuion Completed")

      @pytest.mark.run(order=179)
      def test_179_Modify_descendants_action(self):
          logging.info("modifying descendant actions to get EA to child objects")
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"descendants_action": {"option_with_ea": "RETAIN","option_without_ea": "NOT_INHERIT"},"flags": "I"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",ref=ref1,params="?_inheritance=True&_return_fields=flags",grid_vip=config.grid_vip)
          print(get_ref)
          result = '"flags": "I"'
          if result in get_ref:
               assert True
          else:
               assert False
          print(result)
          print("Test Case 179 Executuion Completed")

      @pytest.mark.run(order=180)
      def test_180_Validate_EA_inheritance_at_vlan_range(self):
          logging.info("validating EA inheritance at vlan range")
          output = ib_NIOS.wapi_request('GET',object_type="vlanrange",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = 'extattrs:infoblox:value:100'
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 180 Executuion Completed")



####################################################################################################################################################
########################################## removing the configuration to test other scenario #####################################################
####################################################################################################################################################

      @pytest.mark.run(order=181)
      def test_181_Delete_and_Validate_Extensible_attribute(self):
          logging.info("deleting and validating  extensible attribute to test other scenarios")
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          #print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          #print(output)
          result = '"name": "infoblox"'
          if result in output:
             assert False
          else:
             assert True
          print(result)
          print("Test Case 181 Executuion Completed")


###################################################################################################################################################################
## When values are same checking the option_with_ea : convert,EA that already exists on a descendant. Result: at child inheritance state should show as Inherit ###
###################################################################################################################################################################

      @pytest.mark.run(order=182)
      def test_182_Add_and_Validate_Extensible_Attribute_with_enable_inheritance(self):
          logging.info("adding and validating extensible attribute")
          data = {"default_value": "100","name": "infoblox","type": "STRING"}
          response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=default_value,name",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "infoblox"','"default_value": "100"']
          for i in result:
              if i in output:
                  assert True
              else:
                  assert False
          print(result)
          print("Test Case 182 Executuion Completed")

      @pytest.mark.run(order=183)
      def test_183_Associate_and_Validate_EA_at_vlan_range(self):
          logging.info("associating EA at vlan range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="vlanrange", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox": {"value": "100"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="vlanrange",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"value": "100"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 183 Executuion Completed")

      @pytest.mark.run(order=184)
      def test_184_Associate_and_Validate_EA_at_vlan_view(self):
          logging.info("associating EA at vlan view")
          get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox": {"value": "100"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="vlanview",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"value": "100"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 184 Executuion Completed")

      @pytest.mark.run(order=185)
      def test_185_Modify_descendants_action(self):
          logging.info("modifying descendant actions to get EA to child objects")
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"descendants_action": {"option_with_ea": "CONVERT","option_without_ea": "NOT_INHERIT"},"flags": "I"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",ref=ref1,params="?_inheritance=True&_return_fields=flags",grid_vip=config.grid_vip)
          print(get_ref)
          result = '"flags": "I"'
          if result in get_ref:
               assert True
          else:
               assert False
          print(result)
          print("Test Case 185 Executuion Completed")


      @pytest.mark.run(order=186)
      def test_186_Validate_EA_inheritance_at_vlan_range(self):
          logging.info("validating EA inheritance at vlan range")
          output = ib_NIOS.wapi_request('GET',object_type="vlanrange",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox:inheritance_source::vlanview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 186 Executuion Completed")


####################################################################################################################################################
########################################## removing the configuration to test other scenario #####################################################
####################################################################################################################################################

      @pytest.mark.run(order=187)
      def test_187_Delete_and_Validate_Extensible_attribute(self):
          logging.info("deleting and validating  extensible attribute")
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          #print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          #print(output)
          result = '"name": "infoblox"'
          if result in output:
             assert False
          else:
             assert True
          print(result)
          print("Test Case 187 Executuion Completed")

#########################################################################################################################################################################
## When values are different checking the option_with_ea : convert,EA that already exists on a descendant. Result: at child inheritance state should show as Override ###
#########################################################################################################################################################################

      @pytest.mark.run(order=188)
      def test_188_Add_and_Validate_Extensible_attribute(self):
          logging.info("adding and validating extensible attribute")
          data = {"default_value": "100","name": "infoblox","type": "STRING"}
          response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=default_value,name",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "infoblox"','"default_value": "100"']
          for i in result:
              if i in output:
                  assert True
              else:
                  assert False
          print(result)
          print("Test Case 188 Executuion Completed")

      @pytest.mark.run(order=189)
      def test_189_Associate_and_Validate_EA_at_vlan_range(self):
          logging.info("associating EA at vlan range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="vlanrange", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox": {"value": "200"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="vlanrange",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"value": "200"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 189 Executuion Completed")

      @pytest.mark.run(order=190)
      def test_190_Associate_and_Validate_EA_at_vlan_view(self):
          logging.info("associating EA at vlan view")
          get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox": {"value": "100"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="vlanview",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"value": "100"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 190 Executuion Completed")

      @pytest.mark.run(order=191)
      def test_191_Modify_descendants_action(self):
          logging.info("modifying descendant actions")
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"descendants_action": {"option_with_ea": "CONVERT","option_without_ea": "NOT_INHERIT"},"flags": "I"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",ref=ref1,params="?_inheritance=True&_return_fields=flags",grid_vip=config.grid_vip)
          print(get_ref)
          result = '"flags": "I"'
          if result in get_ref:
               assert True
          else:
               assert False
          print(result)
          print("Test Case 191 Executuion Completed")


      @pytest.mark.run(order=192)
      def test_192_Validate_EA_Inheritance_at_vlan_range(self):
          logging.info("validating EA inheritance at vlan range")
          output = ib_NIOS.wapi_request('GET',object_type="vlanrange",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = 'extattrs:infoblox:value:200'
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 192 Executuion Completed")

####################################################################################################################################################
########################################## removing the configuration to test other scenario #####################################################
####################################################################################################################################################

      @pytest.mark.run(order=193)
      def test_193_Delete_and_Validate_Extensible_attribute(self):
          logging.info("deleting and validating  extensible attribute")
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          #print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          #print(output)
          result = '"name": "infoblox"'
          if result in output:
             assert False
          else:
             assert True
          print(result)
          print("Test Case 193 Executuion Completed")

#################################################################################################################################################################
#### Checking the option_without_ea : NOT_INHERIT,EA that does not exists on a descendant. Result: at child the inheritance state should show as NOT_INHERIT ####
#################################################################################################################################################################

      @pytest.mark.run(order=194)
      def test_194_Add_and_Validate_Extensible_attribute(self):
          logging.info("adding and validating extensible attribute")
          data = {"default_value": "100","name": "infoblox","type": "STRING"}
          response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=default_value,name",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "infoblox"','"default_value": "100"']
          for i in result:
              if i in output:
                  assert True
              else:
                  assert False
          print(result)
          print("Test Case 194 Executuion Completed")


      @pytest.mark.run(order=195)
      def test_195_Associate_and_Validate_EA_at_vlan_view(self):
          logging.info("associating and validating EA at vlan view")
          get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox": {"value": "100"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="vlanview",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"value": "100"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 195 Executuion Completed")

      @pytest.mark.run(order=196)
      def test_196_Modify_descendants_action(self):
          logging.info("modifying descendat actions")
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"descendants_action": {"option_with_ea": "INHERIT","option_without_ea": "NOT_INHERIT"},"flags": "I"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",ref=ref1,params="?_inheritance=True&_return_fields=flags",grid_vip=config.grid_vip)
          print(get_ref)
          result = '"flags": "I"'
          if result in get_ref:
               assert True
          else:
               assert False
          print(result)
          print("Test Case 196 Executuion Completed")


      @pytest.mark.run(order=197)
      def test_197_Validate_EA_inheritance_at_vlan_range(self):
          logging.info("validatig EA inheritance at vlan range")
          output = ib_NIOS.wapi_request('GET',object_type="vlanrange",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"extattrs": {}'
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 197 Executuion Completed")


####################################################################################################################################################
########################################## removing the configuration to test other scenario #####################################################
####################################################################################################################################################

      @pytest.mark.run(order=198)
      def test_198_Delete_and_Validate_Extensible_attribute(self):
          logging.info("deleting and validating  and validating EA")
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          #print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          #print(output)
          result = '"name": "infoblox"'
          if result in output:
             assert False
          else:
             assert True
          print(result)
          print("Test Case 198 Executuion Completed")

####################################################################################################################################################
###################################### Custom network view scenarions for DNS objects  #############################################################
####################################################################################################################################################


################################################################################################
################### Checking the Inheritance Scenarions ########################################
################################################################################################


      @pytest.mark.run(order=199)
      def test_199_Add_and_Validate_network_view(self):
          logging.info("adding and validating network view")
          data = {"name": "custom"}
          response = ib_NIOS.wapi_request('POST', object_type="networkview",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="networkview",grid_vip=config.grid_vip)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = 'is_default:false,name:custom'
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 199 Executuion Completed")

      @pytest.mark.run(order=200)
      def test_200_Add_and_Validate_Extensible_attribute(self):
          logging.info("adding and validating extensible attribute")
          data = {"default_value": "100","name": "infoblox","type": "STRING"}
          response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=default_value,name",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "infoblox"','"default_value": "100"']
          for i in result:
              if i in output:
                  assert True
              else:
                  assert False
          print(result)
          print("Test Case 200 Executuion Completed")


      @pytest.mark.run(order=201)
      def test_201_Associate_and_Validate_EA_at_custom_network_view(self):
          logging.info("addinga nd validating EA at custom network view")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkview", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"extattrs": {"infoblox": {"value": "100"}}}
          view = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(view)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="networkview",ref=ref1,params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          print(output)
          result = ['extattrs:infoblox:value:100','networkview','custom/false']
          for i in result:
            if i in output:
                  assert True
            else:
                  assert False
          print(result)
          print("Test Case 201 Executuion Completed")

      @pytest.mark.run(order=202)
      def test_202_Modify_descendants_action(self):
          logging.info("modifying descendant actions")
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"descendants_action": {"option_with_ea": "INHERIT","option_without_ea": "INHERIT"},"flags": "I"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",ref=ref1,params="?_inheritance=True&_return_fields=flags",grid_vip=config.grid_vip)
          print(get_ref)
          result = '"flags": "I"'
          if result in get_ref:
               assert True
          else:
               assert False
          print(result)
          print("Test Case 202 Executuion Completed")

      @pytest.mark.run(order=203)
      def test_203_Validate_EA_inheritance_at_custom_dns_view(self):
          logging.info("validating EA inheritance at custom dns view")
          get_ref = ib_NIOS.wapi_request('GET',object_type="view",grid_vip=config.grid_vip)
          #print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',object_type="view",ref=ref1,params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = "inheritance_source::networkview"
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 203 Executuion Completed")


      @pytest.mark.run(order=204)
      def test_204_Create_and_Validate_authority_zone_in_custom_network_view(self):
          logging.info("creating and validating authority zone in custom network view")
          data = {"fqdn": "test.com","view": "default.custom"}
          response = ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          print(get_ref)
          result = ['"fqdn": "test.com"','"view": "default.custom"']
          for i in result:
            if i in get_ref:
               assert True
            else:
               assert False
          print(result)
          print("Test Case 204 Executuion Completed")

      @pytest.mark.run(order=205)
      def test_205_Validate_EA_inheritance_at_authority_zone_under_custom_networkview(self):
          logging.info("validating EA inheritance at authority zone in custom networkview")
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          result = "inheritance_source::networkview"
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 205 Executuion Completed")

      @pytest.mark.run(order=206)
      def test_206_Add_and_Validate_A_record_in_custom_networkview(self):
          logging.info("adding and validating A record in custom networkview")
          data = {"ipv4addr": "10.0.0.2","name": "a.test.com","view": "default.custom"}
          response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="record:a",grid_vip=config.grid_vip)
          print(output)
          result = '"name": "a.test.com"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 206 Executuion Completed")

      @pytest.mark.run(order=207)
      def test_207_Validate_EA_inheritance__at_A_record_in_custom_networkview(self):
          logging.info("validating EA inheritance at A record in custom networkview")
          output = ib_NIOS.wapi_request('GET',object_type="record:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          result = "inheritance_source::networkview"
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 207 Executuion Completed")


      @pytest.mark.run(order=208)
      def test_208_Add_and_Validate_cname_record_in_custom_networkview(self):
          logging.info("adding and validating cname record in custom networkview")
          data = {"canonical": "test.com","name": "caa.test.com","view": "default.custom"}
          response = ib_NIOS.wapi_request('POST', object_type="record:cname",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="record:cname",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "caa.test.com"','"canonical": "test.com"','"view": "default.custom"']
          for i in result:
            if i in output:
                  assert True
            else:
                  assert False
          print(result)
          print("Test Case 208 Executuion Completed")


      @pytest.mark.run(order=209)
      def test_209_Validate_EA_inheritance_at_cname_record_in_custom_networkview(self):
          logging.info("validating EA inheritance at cname record in custom networkview")
          output = ib_NIOS.wapi_request('GET',object_type="record:cname",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = "inheritance_source::networkview"
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 209 Executuion Completed")


########################################################################################################
#####################  Checking the Override scenarions under custom networkview #######################
########################################################################################################


      @pytest.mark.run(order=210)
      def test_210_Associate_and_Validate_EA_at_A_record_in_custom_networkview(self):
          logging.info("associating and validating EA at A record in custom networkview")
          get_ref = ib_NIOS.wapi_request('GET', object_type="record:a", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"extattrs": {"infoblox": {"value": "200"}}}
          view = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(view)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="record:a",ref=ref1,params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = 'extattrs:infoblox:value:200'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 210 Executuion Completed")

      @pytest.mark.run(order=211)
      def test_211_Associate_and_Validate_EA_at_CNAME_record_in_custom_networkview(self):
          logging.info("associating and validating EA at cname record in custom networkview")
          get_ref = ib_NIOS.wapi_request('GET', object_type="record:cname", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"extattrs": {"infoblox": {"value": "200"}}}
          view = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(view)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="record:cname",ref=ref1,params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = 'extattrs:infoblox:value:200'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 211 Executuion Completed")



##########################################################################################################################
############################ removing the custom network view & EA to test other scenario ################################
##########################################################################################################################



      @pytest.mark.run(order=212)
      def test_212_Delete_and_Validate_Extensible_attribute(self):
          logging.info("deleting and validating  and validating extensible attribute")
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          #print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          #print(output)
          result = '"name": "infoblox"'
          if result in output:
             assert False
          else:
             assert True
          print(result)
          print("Test Case 212 Executuion Completed")


      @pytest.mark.run(order=213)
      def test_213_Delete_and_Validate_custom_networkview(self):
          logging.info("deleting and validating  and validating custom networkview")
          output = ib_NIOS.wapi_request('GET',object_type="networkview",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          #print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="networkview",grid_vip=config.grid_vip)
          print(output)
          result = '"name": "custom"'
          if result in output:
             assert False
          else:
             assert True
          print(result)
          print("Test Case 213 Executuion Completed")

      @pytest.mark.run(order=214)
      def test_214_Delete_and_Validate_vlanrange(self):
          logging.info("deleting and validating  and validate vlanrange")
          output = ib_NIOS.wapi_request('GET',object_type="vlanrange",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[0]['_ref']
          #print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="vlanrange",grid_vip=config.grid_vip)
          #print(output)
          result = '"name": "range"'
          if result in output:
             assert False
          else:
             assert True
          print(result)
          print("Test Case 214 Executuion Completed")

      @pytest.mark.run(order=215)
      def test_215_Delete_and_Validate_vlan(self):
          logging.info("deleting and validating a nd validating vlan ")
          output = ib_NIOS.wapi_request('GET',object_type="vlan",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[0]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="vlan",grid_vip=config.grid_vip)
          #print(output)
          result = '"name": "staticvlan"'
          if result in output:
             assert False
          else:
             assert True
          print(result)
          print("Test Case 215 Executuion Completed")

###########################################################################################################
############################### Multiple EA Scenarios #####################################################
###########################################################################################################

###########################################################################################################################################
###################################### Adding Three EA's (infoblox1,infoblox2,infoblox3) ##################################################
###########################################################################################################################################



      @pytest.mark.run(order=216)
      def test_216_Add_and_Validate_Extensible_attribute(self):
          logging.info("adding and validating extensible attribute")
          data = {"default_value": "100","name": "infoblox1","type": "STRING"}
          response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=default_value,name",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "infoblox1"','"default_value": "100"']
          for i in result:
              if i in output:
                  assert True
              else:
                  assert False
          print(result)
          print("Test Case 216 Executuion Completed")

      @pytest.mark.run(order=217)
      def test_217_Add_and_Validate_Extensible_attribute(self):
          logging.info("adding and validating extensible attribute")
          data = {"default_value": "200","name": "infoblox2","type": "STRING"}
          response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=default_value,name",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "infoblox2"','"default_value": "200"']
          for i in result:
              if i in output:
                  assert True
              else:
                  assert False
          print(result)
          print("Test Case 217 Executuion Completed")

      @pytest.mark.run(order=218)
      def test_218_Add_and_Validate_Extensible_attribute(self):
          logging.info("adding and validating extensible attribute")
          data = {"default_value": "300","name": "infoblox3","type": "STRING"}
          response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=default_value,name",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "infoblox3"','"default_value": "300"']
          for i in result:
              if i in output:
                  assert True
              else:
                  assert False
          print(result)
          print("Test Case 216 Executuion Completed")

      @pytest.mark.run(order=219)
      def test_219_Associate_and_Validate_EA_at_networkview(self):
          logging.info("associating EA to networkview")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkview", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print(ref1)
          data = {"extattrs": {"infoblox1": {"value": "100"},"infoblox2": {"value": "200"},"infoblox3": {"value": "300"}}}
          view = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(view)
          print("Test Case 219 Executuion Completed")

      @pytest.mark.run(order=220)
      def test_220_Validate_aasociation_of_multiple_EAs_at_networkview(self):
          logging.info("validating association of multiple EA's at networkview")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkview", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',object_type="networkview",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = 'extattrs:infoblox1:value:100,infoblox2:value:200,infoblox3:value:300'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 220 Executuion Completed")

      @pytest.mark.run(order=221)
      def test_221_Modify_descendants_action(self):
          logging.info("modifying descendant actions")
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"descendants_action": {"option_with_ea": "INHERIT","option_without_ea": "INHERIT"},"flags": "I"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",ref=ref1,params="?_inheritance=True&_return_fields=flags",grid_vip=config.grid_vip)
          print(get_ref)
          result = '"flags": "I"'
          if result in get_ref:
               assert True
          else:
               assert False
          print(result)
          print("Test Case 221 Executuion Completed")

      @pytest.mark.run(order=222)
      def test_222_Modify_descendants_action(self):
          logging.info("modifying descendant actions")
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-2]['_ref']
          print(ref1)
          data = {"descendants_action": {"option_with_ea": "INHERIT","option_without_ea": "INHERIT"},"flags": "I"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",ref=ref1,params="?_inheritance=True&_return_fields=flags",grid_vip=config.grid_vip)
          print(get_ref)
          result = '"flags": "I"'
          if result in get_ref:
               assert True
          else:
               assert False
          print(result)
          print("Test Case 222 Executuion Completed")

      @pytest.mark.run(order=223)
      def test_223_Modify_descendants_action(self):
          logging.info("modifying descendant actions")
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-3]['_ref']
          print(ref1)
          data = {"descendants_action": {"option_with_ea": "INHERIT","option_without_ea": "INHERIT"},"flags": "I"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",ref=ref1,params="?_inheritance=True&_return_fields=flags",grid_vip=config.grid_vip)
          print(get_ref)
          result = '"flags": "I"'
          if result in get_ref:
               assert True
          else:
               assert False
          print(result)
          print("Test Case 223 Executuion Completed")

      @pytest.mark.run(order=224)
      def test_224_Validate_EA_inheritance_at_dns_view(self):
          logging.info("validating EA inheritance at dns view")
          get_ref = ib_NIOS.wapi_request('GET',object_type="view",grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print(ref1)
          #output = ib_NIOS.wapi_request('GET',object_type="view",ref=ref1,params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox1:inheritance_source::networkview,value:100,infoblox2:inheritance_source::networkview,value:200,infoblox3:inheritance_source::networkview,value:300']
          for i in result: 
            if i in result:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 224 Executuion Completed")

      @pytest.mark.run(order=225)
      def test_225_Create_authority_zone(self):
          logging.info("creating authority zone")
          data = {"fqdn": "test.com","view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print(ref1)
          result = 'test.com'
          if result in ref1:
               assert True
          else:
               assert False
          print(result)
          print("Test Case 225 Executuion Completed")

      @pytest.mark.run(order=226)
      def test_226_Override_EA_value_at_authority_zone(self):
          logging.info("overriding EA value at authority zone")
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"extattrs": {"infoblox1": {"value": "400"},"infoblox2": {"value": "500"},"infoblox3": {"value": "300"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          result = ['extattrs:infoblox1:value:400,infoblox2:value:500,infoblox3:inheritance_source::networkview','value:300']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 226 Executuion Completed")

      @pytest.mark.run(order=227)
      def test_227_Associate_and_Validate_EA_at_vlanview(self):
          logging.info("associating EA to vlan view")
          get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print(ref1)
          data = {"extattrs": {"infoblox1": {"value": "100"},"infoblox2": {"value": "200"},"infoblox3": {"value": "300"}}}
          view = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(view)
          print("Test Case 227 Executuion Completed")

      @pytest.mark.run(order=228)
      def test_228_Validate_multiple_EA_associations_at_vlanview(self):
          logging.info("validating multiple EA assciations at vlan view")
          get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview",grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',object_type="vlanview",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = 'extattrs:infoblox1:value:100,infoblox2:value:200,infoblox3:value:300'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 228 Executuion Completed")

      @pytest.mark.run(order=229)
      def test_229_Create_and_Validate_vlanrange(self):
          logging.info("creating and validating vlan range")
          get_ref = ib_NIOS.wapi_request('GET',object_type="vlanview",grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          res = eval(json.dumps(res))
          #print(res)
          ref1=(res)[0]['_ref']
          print(ref1)
          data = {"end_vlan_id": 5,"name": "range","start_vlan_id": 1,"vlan_view": ref1}
          response = ib_NIOS.wapi_request('POST', object_type="vlanrange",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          get_ref = ib_NIOS.wapi_request('GET',object_type="vlanrange",grid_vip=config.grid_vip)
          result = ['"end_vlan_id": 5','"start_vlan_id": 1','"name": "range"']
          for i in result:
            if i in get_ref:
               assert True
            else:
               assert False
          print(result)
          print("Test Case 229 Executuion Completed")

      @pytest.mark.run(order=230)
      def test_230_Validate_EA_inheritance_at_vlanrange(self):
          logging.info("validating EA inheritance at vlan range")
          output = ib_NIOS.wapi_request('GET',object_type="vlanrange",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox1:inheritance_source::vlanview','value:100','infoblox2:inheritance_source::vlanview','value:200,infoblox3:inheritance_source::vlanview','value:300']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 230 Executuion Completed")

      @pytest.mark.run(order=231)
      def test_231_Create_static_vlan(self):
          logging.info("creating static vlan")
          get_ref = ib_NIOS.wapi_request('GET',object_type="vlanview",grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          res = eval(json.dumps(res))
          #print(res)
          ref1=(res)[0]['_ref']
          print(ref1)
          data = {"id": 6,"name": "staticvlan","parent": ref1}
          response = ib_NIOS.wapi_request('POST', object_type="vlan",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          get_ref = ib_NIOS.wapi_request('GET',object_type="vlan",grid_vip=config.grid_vip)
          result = ['"id": 6','"name": "staticvlan"']
          for i in result:
            if i in get_ref:
               assert True
            else:
               assert False
          print(result)
          print("Test Case 231 Executuion Completed")

      @pytest.mark.run(order=232)
      def test_232_Validate_EA_inheritance_at_vlanrange(self):
          logging.info("validating EA inheritance at vlan range")
          output = ib_NIOS.wapi_request('GET',object_type="vlan",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox1:inheritance_source::vlanview','value:100','infoblox2:inheritance_source::vlanview','value:200,infoblox3:inheritance_source::vlanview','value:300']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 232 Executuion Completed")

##########################################################################################################################
############################ removing the custom network view & EA to test other scenario ################################
##########################################################################################################################

      @pytest.mark.run(order=233)
      def test_233_Delete_and_Validate_Extensible_attribute(self):
          logging.info("deleting and validating  extensible attribute")
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          #print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          ref2 = json.loads(output)[-2]['_ref']
          print(ref2)
          ref3 = json.loads(output)[-3]['_ref']
          print(ref3)
          output1 = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output1)
          output2 = ib_NIOS.wapi_request('DELETE',ref=ref2,grid_vip=config.grid_vip)
          print(output2)
          output3 = ib_NIOS.wapi_request('DELETE',ref=ref3,grid_vip=config.grid_vip)
          print(output3)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          #print(output)
          result = ['infoblox1','infoblox2','infoblox3']
          for i in result:
            if i in output:
             assert False
            else:
             assert True
          print(result)
          print("Test Case 233 Executuion Completed")


############################################################################################################
################################## EA with multiple values scenarios #######################################
############################################################################################################


      @pytest.mark.run(order=234)
      def test_234_Add_and_Validate_Extensible_Attribute_with_enable_inheritance(self):
          logging.info("adding and validating extensible attribute")
          data = {"default_value": "100","name": "infoblox1","type": "STRING","flags": "IV"}
          response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=default_value,name,flags",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "infoblox1"','"default_value": "100"','"flags": "IV"']
          for i in result:
              if i in output:
                  assert True
              else:
                  assert False
          print(result)
          print("Test Case 234 Executuion Completed")


      @pytest.mark.run(order=235)
      def test_235_Associate_and_Validate_EA_at_networkview(self):
          logging.info("associating EA at network view")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkview", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"extattrs": {"infoblox1": {"value": ["100","200"]}}}
          view = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(view)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="networkview",ref=ref1,params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          print(output)
          result = 'extattrs:infoblox1:value:[100,200]'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 235 Executuion Completed")

      @pytest.mark.run(order=236)
      def test_236_Modify_descendants_action(self):
          logging.info("modifying descendant actions")
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"descendants_action": {"option_with_ea": "INHERIT","option_without_ea": "INHERIT"}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",ref=ref1,params="?_inheritance=True&_return_fields=flags",grid_vip=config.grid_vip)
          print(get_ref)
          print("Test Case 236 Executuion Completed")

      @pytest.mark.run(order=237)
      def test_237_Add_and_Validate_custom_dns_view(self):
          logging.info("adding custom dns view")
          data = {"name": "custom"}
          response = ib_NIOS.wapi_request('POST', object_type="view",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="view",grid_vip=config.grid_vip)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          print(output)
          result = 'is_default:false,name:custom'
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 237 Executuion Completed")

      @pytest.mark.run(order=238)
      def test_238_Validate_EA_inheritance_at_custom_dns_view(self):
          logging.info("validating EA inheritance at custom dns view")
          get_ref = ib_NIOS.wapi_request('GET', object_type="view", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',object_type="view",ref=ref1,params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          print(output)
          result = ['extattrs:infoblox1:inheritance_source::networkview','value:[100,200]']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 238 Executuion Completed")

      @pytest.mark.run(order=239)
      def test_239_Create_authority_zone(self):
          logging.info("creating authority zone")
          data = {"fqdn": "custom.com","view": "custom"}
          response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          print(get_ref)
          result = 'custom.com'
          if result in get_ref:
               assert True
          else:
               assert False
          print(result)
          print("Test Case 239 Executuion Completed")

      @pytest.mark.run(order=240)
      def test_240_Override_extensible_attribute_value_at_authority_zone(self):
          logging.info("overriding extensible attribute value at authority zone")
          get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"extattrs": {"infoblox1": {"value": ["300","400"]}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:,:zone_auth','extattrs:infoblox1:value:[300,400]']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 240 Executuion Completed")

      @pytest.mark.run(order=241)
      def test_241_Associate_and_Validate_EA_at_vlanview(self):
          logging.info("associating EA at vlan view")
          get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox1": {"value": ["100","200"]}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="vlanview",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = 'extattrs:infoblox1:value:[100,200]'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 241 Executuion Completed")

      @pytest.mark.run(order=242)
      def test_242_Add_and_Validate_vlanrange(self):
          logging.info("adding and validating vlan range")
          get_ref = ib_NIOS.wapi_request('GET',object_type="vlanview",grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          res = eval(json.dumps(res))
          #print(res)
          ref1=(res)[0]['_ref']
          print(ref1)
          data = {"end_vlan_id": 10,"name": "range2","start_vlan_id": 6,"vlan_view": ref1}
          response = ib_NIOS.wapi_request('POST', object_type="vlanrange",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          get_ref = ib_NIOS.wapi_request('GET',object_type="vlanrange",grid_vip=config.grid_vip)
          print(get_ref)
          result = ['"end_vlan_id": 10','"start_vlan_id": 6','"name": "range2"']
          for i in result:
            if i in get_ref:
               assert True
            else:
               assert False
          print(result)
          print("Test Case 242 Executuion Completed")

      @pytest.mark.run(order=243)
      def test_243_Validat_EA_inheritance_and_value_at_vlanrange(self):
          logging.info("validating EA inheritance and value at vlan range")
          get_ref = ib_NIOS.wapi_request('GET', object_type="vlanrange", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,object_type="vlanrange",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox1:inheritance_source::vlanview','value:[100,200]']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 243 Executuion Completed")

####################################################################################################################################################
########################################## removing the configuration to test other scenario #####################################################
####################################################################################################################################################

      @pytest.mark.run(order=244)
      def test_244_Delete_and_Validate_Extensible_attribute(self):
          logging.info("deleting and validating  extensible attribute")
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          result = '"name": "infoblox1"'
          if result in output:
             assert False
          else:
             assert True
          print(result)
          sleep(03)
          print("Test Case 244 Executuion Completed")

      @pytest.mark.run(order=245)
      def test_245_Delete_and_Validate_custom_dnsview(self):
          logging.info("deleting and validating  custom dns view")
          output = ib_NIOS.wapi_request('GET',object_type="view",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          output = ib_NIOS.wapi_request('GET',object_type="view",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          result = '"name": "custom"'
          if result in output:
             assert False
          else:
             assert True
          print(result)
          sleep(03)
          print("Test Case 245 Executuion Completed")


########################################################################################################
##############################  EA deleted scenarios ###################################################
########################################################################################################

      @pytest.mark.run(order=246)
      def test_246_Add_and_Validate_Extensible_attribute_with_enable_inheritance(self):
          logging.info("adding and validating extensible attribute")
          data = {"default_value": "100","name": "infoblox","type": "STRING"}
          response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=default_value,name",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "infoblox"','"default_value": "100"']
          for i in result:
              if i in output:
                  assert True
              else:
                  assert False
          print(result)
          print("Test Case 246 Executuion Completed")

      @pytest.mark.run(order=247)
      def test_247_Associate_and_Validate_EA_at_networkview(self):
          logging.info("associating EA at network view")
          output = ib_NIOS.wapi_request('GET',object_type="networkview",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"extattrs": {}'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkview", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print(ref1)
          data = {"extattrs": {"infoblox": {"value": "100"}}}
          view = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(view)
          output = ib_NIOS.wapi_request('GET',object_type="networkview",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"value": "100"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 247 Executuion Completed")

      @pytest.mark.run(order=248)
      def test_248_Modify_and_Validate_descendants_action(self):
          logging.info("modifying descendant actions")
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"descendants_action": {"option_with_ea": "INHERIT","option_without_ea": "INHERIT"},"flags": "I"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",ref=ref1,params="?_inheritance=True&_return_fields=flags",grid_vip=config.grid_vip)
          print(get_ref)
          result = '"flags": "I"'
          if result in get_ref:
               assert True
          else:
               assert False
          print(result)
          print("Test Case 248 Executuion Completed")

      @pytest.mark.run(order=249)
      def test_249_Validate_EA_inheritance_at_dns_view(self):
          logging.info("validating EA inheritance at dns view")
          get_ref = ib_NIOS.wapi_request('GET',object_type="view",grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = "inheritance_source::networkview"
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 249 Executuion Completed")

      @pytest.mark.run(order=250)
      def test_250_Add_and_Validate_authority_zone(self):
          logging.info("adding and validating authority zone")
          #data = {"fqdn": "test.com","view": "default"}
          #response = ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data),grid_vip=config.grid_vip)
          #print(response)
          get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print(ref1)
          result = 'test.com'
          if result in ref1:
               assert True
          else:
               assert False
          print(result)
          print("Test Case 250 Executuion Completed")

      @pytest.mark.run(order=251)
      def test_251_Validate_EA_inheritance_at_authority_zone(self):
          logging.info("validating EA inheritance at authority zone")
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          result = "inheritance_source::networkview"
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 251 Executuion Completed")

      @pytest.mark.run(order=252)
      def test_252_Add_and_validate_A_record(self):
          logging.info("adding and validating A record")
          data = {"ipv4addr": "10.0.0.2","name": "a.test.com","view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          output = ib_NIOS.wapi_request('GET',object_type="record:a",grid_vip=config.grid_vip)
          print(output)
          result = '"name": "a.test.com"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 252 Executuion Completed")

      @pytest.mark.run(order=253)
      def test_253_Validate_EA_inheritance_at_A_record(self):
          logging.info("validating EA inheritance at A record")
          output = ib_NIOS.wapi_request('GET',object_type="record:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = "inheritance_source::networkview"
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 253 Executuion Completed")

      @pytest.mark.run(order=254)
      def test_254_Associate_and_Validate_EA_at_vlan_view(self):
          logging.info("associating EA at vlan view")
          get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox": {"value": "100"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="vlanview",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"value": "100"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 254 Executuion Completed")

      @pytest.mark.run(order=255)
      def test_255_Add_and_Validate_static_vlan(self):
          logging.info("adding and validating static vlan")
          get_ref = ib_NIOS.wapi_request('GET',object_type="vlanview",grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          res = eval(json.dumps(res))
          #print(res)
          ref1=(res)[0]['_ref']
          print(ref1)
          data = {"id": 11,"name": "vlan","parent": ref1}
          response = ib_NIOS.wapi_request('POST', object_type="vlan",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          get_ref = ib_NIOS.wapi_request('GET',object_type="vlan",grid_vip=config.grid_vip)
          #res = json.loads(get_ref)
          #ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          result = ['"id": 11','"name": "vlan"']
          for i in result:
            if i in get_ref:
               assert True
            else:
               assert False
          print(result)
          print("Test Case 255 Executuion Completed")

      @pytest.mark.run(order=256)
      def test_256_Validate_EA_inheritance_at_static_vlan(self):
          logging.info("validating EA inheritance at static vlan")
          output = ib_NIOS.wapi_request('GET',object_type="vlan",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['inheritance_source::vlanview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 256 Executuion Completed")

      @pytest.mark.run(order=257)
      def test_257_Delete_and_Validate_Extensible_attribute(self):
          logging.info("deleting and validating  and validating extensible attribute")
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('DELETE',ref=ref1,grid_vip=config.grid_vip)
          print(output)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          result = '"name": "infoblox"'
          if result in output:
             assert False
          else:
             assert True
          print(result)
          sleep(03)
          print("Test Case 257 Executuion Completed")

      @pytest.mark.run(order=258)
      def test_258_Validate_EA_inheritance_at_dns_view(self):
          logging.info("validating EA inheritance at dns view")
          get_ref = ib_NIOS.wapi_request('GET',object_type="view",grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"extattrs": {}'
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 258 Executuion Completed")

      @pytest.mark.run(order=259)
      def test_259_Validate_EA_inheritance_at_authority_zone(self):
          logging.info("validating EA inheritance at authority zone")
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"extattrs": {}'
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 259 Executuion Completed")

      @pytest.mark.run(order=260)
      def test_260_Validate_EA_inheritance_at_A_record(self):
          logging.info("validating EA inheritance at A record")
          output = ib_NIOS.wapi_request('GET',object_type="record:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"extattrs": {}'
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 260 Executuion Completed")

      @pytest.mark.run(order=261)
      def test_261_Validate_EA_inheritance_at_static_vlan(self):
          logging.info("validating EA inheritance at static vlan")
          output = ib_NIOS.wapi_request('GET',object_type="vlan",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"extattrs": {}'
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 261 Executuion Completed")

##############################################################################################
################################ Negative Scenarios ##########################################
##############################################################################################

####################################################################################################################
### Checking the inheritance state of DNS view, Zone, Record, vlanrane and vlan without enabling the "Inheritance"##
############################################################################################################

      @pytest.mark.run(order=262)
      def test_262_Add_and_Validate_Extensible_attribute(self):
          logging.info("adding and validating extensible attribute")
          data = {"default_value": "100","name": "infoblox","type": "STRING"}
          response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=default_value,name",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "infoblox"','"default_value": "100"']
          for i in result:
              if i in output:
                  assert True
              else:
                  assert False
          print(result)
          print("Test Case 262 Executuion Completed")

      @pytest.mark.run(order=263)
      def test_263_Associate_and_Validate_EA_at_networkview(self):
          logging.info("associating EA at network view")
          output = ib_NIOS.wapi_request('GET',object_type="networkview",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"extattrs": {}'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkview", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox": {"value": "100"}}}
          view = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          #print(view)
          output = ib_NIOS.wapi_request('GET',object_type="networkview",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          print(output)
          result = 'extattrs:infoblox:value:100'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 263 Executuion Completed")

      @pytest.mark.run(order=264)
      def test_264_Validate_EA_inheritance_at_dns_view(self):
          logging.info("validating EA inheritance at dns view")
          get_ref = ib_NIOS.wapi_request('GET',object_type="view",grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print(ref1)
          #output = ib_NIOS.wapi_request('GET',object_type="view",ref=ref1,params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"extattrs": {}'
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 264 Executuion Completed")

      @pytest.mark.run(order=265)
      def test_265_Validate_EA_inheritance_at_authority_zone(self):
          logging.info("validating EA inheritance at authority zone")
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"extattrs": {}'
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 265 Executuion Completed")

      @pytest.mark.run(order=266)
      def test_266_Validate_EA_inheritance_at_A_record(self):
          logging.info("validating EA inheritance at A record")
          output = ib_NIOS.wapi_request('GET',object_type="record:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"extattrs": {}'
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 266 Executuion Completed")

      @pytest.mark.run(order=267)
      def test_267_Associate_and_Validate_EA_at_vlanview(self):
          logging.info("associating and validating EA at vlan view")
          get_ref = ib_NIOS.wapi_request('GET', object_type="vlanview", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          #print(ref1)
          data = {"extattrs": {"infoblox": {"value": "100"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="vlanview",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = 'extattrs:infoblox:value:100'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 267 Executuion Completed")

      @pytest.mark.run(order=268)
      def test_268_Validate_EA_inheritance_at_vlanrange(self):
          logging.info("validating EA inheritance at vlan range")
          output = ib_NIOS.wapi_request('GET',object_type="vlanrange",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"extattrs": {}'
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 268 Executuion Completed")

      @pytest.mark.run(order=269)
      def test_269_Validate_EA_inheritance_at_static_vlan(self):
          logging.info("validating EA inheritance at static vlan")
          output = ib_NIOS.wapi_request('GET',object_type="vlan",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"extattrs": {}'
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 269 Executuion Completed")

#################################################################################################################
################################## Negative Scenarios on custom networkview #####################################
#################################################################################################################


      @pytest.mark.run(order=270)
      def test_270_Add_and_Validate_network_view(self):
          logging.info("adding and validating network view")
          data = {"name": "custom"}
          response = ib_NIOS.wapi_request('POST', object_type="networkview",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="networkview",grid_vip=config.grid_vip)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = 'is_default:false,name:custom'
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 270 Executuion Completed")

      @pytest.mark.run(order=271)
      def test_271_Associate_and_Validate_EA_at_custom_network_view(self):
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkview", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"extattrs": {"infoblox": {"value": "100"}}}
          view = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(view)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="networkview",ref=ref1,params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          print(output)
          result = ['extattrs:infoblox:value:100','networkview','custom/false']
          for i in result:
            if i in output:
                  assert True
            else:
                  assert False
          print(result)
          print("Test Case 271 Executuion Completed")

      @pytest.mark.run(order=272)
      def test_272_Validate_EA_inheritance_at_custom_dns_view(self):
          logging.info("validating EA inheritance at custom dns view")
          get_ref = ib_NIOS.wapi_request('GET',object_type="view",grid_vip=config.grid_vip)
          #print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',object_type="view",ref=ref1,params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"extattrs": {}'
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 272 Executuion Completed")


      @pytest.mark.run(order=273)
      def test_273_Add_and_Validate_authority_zone_in_custom_network_view(self):
          logging.info("adding and validating authority zone in custom network view")
          data = {"fqdn": "test.com","view": "default.custom"}
          response = ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
          print(get_ref)
          result = ['"fqdn": "test.com"','"view": "default.custom"']
          for i in result:
            if i in get_ref:
               assert True
            else:
               assert False
          print(result)
          print("Test Case 273 Executuion Completed")

      @pytest.mark.run(order=274)
      def test_274_Validate_EA_inheritance_at_authority_zone_in_custom_networkview(self):
          logging.info("validating EA inheritance at authority zone in custom network view")
          output = ib_NIOS.wapi_request('GET',object_type="zone_auth",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"extattrs": {}'
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 274 Executuion Completed")

      @pytest.mark.run(order=275)
      def test_275_Add_and_Validate_A_record_in_custom_networkview(self):
          logging.info("adding and validating A record in custom network view")
          data = {"ipv4addr": "10.0.0.2","name": "a.test.com","view": "default.custom"}
          response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="record:a",grid_vip=config.grid_vip)
          print(output)
          result = '"name": "a.test.com"'
          if result in output:
                  assert True
          else:
                  assert False
          print(result) 
          print("Test Case 275 Executuion Completed")

      @pytest.mark.run(order=276)
      def test_276_Validate_EA_inheritance_at_A_record_in_custom_networkview(self):
          logging.info("validating EA inheritance at A record in custom network view")
          output = ib_NIOS.wapi_request('GET',object_type="record:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          result = '"extattrs": {}'
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 276 Executuion Completed")



#####################################################################################################################################
########################################## RPZ SCENARIOS in Default DNS view ########################################################
#####################################################################################################################################


      @pytest.mark.run(order=277)
      def test_277_Add_and_Validate_Extensible_Attribute_with_enable_inheritance(self):
          logging.info("adding and validating extensible attribute")
          data = {"default_value": "100","name": "infoblox_rpz","type": "STRING"}
          response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=default_value,name",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "infoblox_rpz"','"default_value": "100"']
          for i in result:
              if i in output:
                  assert True
              else:
                  assert False
          print(result)
          print("Test Case 277 Executuion Completed")

      @pytest.mark.run(order=278)
      def test_278_Associate_and_Validate_EA_at_networkview(self):
          logging.info("associating created EA at networkview")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkview", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print(ref1)
          data = {"extattrs": {"infoblox_rpz": {"value": "100"}}}
          view = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(view)
          output = ib_NIOS.wapi_request('GET',object_type="networkview",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = 'extattrs:infoblox_rpz:value:100'
          if result in output:
                  assert True
          else:
                  assert False
          print(result)
          print("Test Case 278 Executuion Completed")

      @pytest.mark.run(order=279)
      def test_279_Modify_descendants_action(self):
          logging.info("modifying descendant actions to get EA to child objects")
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"descendants_action": {"option_with_ea": "INHERIT","option_without_ea": "INHERIT"},"flags": "I"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",ref=ref1,params="?_inheritance=True&_return_fields=flags",grid_vip=config.grid_vip)
          print(get_ref)
          result = '"flags": "I"'
          if result in get_ref:
               assert True
          else:
               assert False
          print(result)
          print("Test Case 279 Executuion Completed")


      @pytest.mark.run(order=280)
      def test_280_Create_response_policy_zone_in_default_dns_view(self):
          logging.info("creating response policy zone in default dns view")
          fqdn=config.grid_vip.split('.')
          fqdn='ib-'+str(fqdn[0])+'-'+str(fqdn[1])+'-'+str(fqdn[2])+'-'+str(fqdn[3])+'.infoblox.com'
          data = {"fqdn": "rpz.com","grid_primary": [{"name": fqdn,"stealth": False}],"view": "default"}
          response = ib_NIOS.wapi_request('POST', object_type="zone_rp", fields=json.dumps(data), grid_vip=config.grid_vip)
          print(response)
          print("Test Case 280 Executuion Completed")
   

      @pytest.mark.run(order=281)
      def test_281_Validate_created_response_policy_zone_in_default_dns_view(self):
          logging.info("validating created response policy zone in default dns view")
          get_ref = ib_NIOS.wapi_request('GET',object_type="zone_rp",grid_vip=config.grid_vip)
          print(get_ref)
          result = ['"fqdn": "rpz.com"','"view": "default"']
          for i in result:
            if i in get_ref:
               assert True
            else:
               assert False
          print(result)
          print("Test Case 281 Executuion Completed")

      @pytest.mark.run(order=282)
      def test_282_Validate_EA_inheritance_at_response_policy_zone_in_default_dns_view(self):
          logging.info("validating EA inheritance at response policy zone in default dns view")
          output = ib_NIOS.wapi_request('GET',object_type="zone_rp",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox_rpz:inheritance_source::networkview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 282 Executuion Completed")

      @pytest.mark.run(order=283)
      def test_283_Create_Substitute_A_record_rule_in_default_dns_view(self):
          logging.info("creating substitute A record rule in default dns view")
          fqdn=config.grid_vip.split('.')
          fqdn='ib-'+str(fqdn[0])+'-'+str(fqdn[1])+'-'+str(fqdn[2])+'-'+str(fqdn[3])+'.infoblox.com'
          data = {"ipv4addr": "90.90.90.9","name": "a.rpz.com","view": "default","rp_zone": "rpz.com"}
          response = ib_NIOS.wapi_request('POST', object_type="record:rpz:a", fields=json.dumps(data), grid_vip=config.grid_vip)
          print(response)
          print("Test Case 283 Executuion Completed")
    
      @pytest.mark.run(order=284)
      def test_284_Validate_created_Substitute_A_record_rule_in_default_dns_view(self):
          logging.info("validating created substitute A record rule in default dns view")
          get_ref = ib_NIOS.wapi_request('GET',object_type="record:rpz:a",params="?_inheritance=True&_return_fields=rp_zone,ipv4addr,name,view",grid_vip=config.grid_vip)
          print(get_ref)
          result = ['"ipv4addr": "90.90.90.9"','"name": "a.rpz.com"','"rp_zone": "rpz.com"','"view": "default"']
          for i in result:
            if i in get_ref:
               assert True
            else:
               assert False
          print(result)
          print("Test Case 284 Executuion Completed")

      @pytest.mark.run(order=285)
      def test_285_Validate_EA_inheritance_at_substitute_A_record_rule_in_default_dns_view(self):
          logging.info("validating EA inheritance at substitute A record rule in default dns view")
          output = ib_NIOS.wapi_request('GET',object_type="record:rpz:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox_rpz:inheritance_source::networkview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 285 Executuion Completed")
  
      @pytest.mark.run(order=286)
      def test_286_Add_and_validate_Substitute_AAAA_record_rule_in_default_dns_view(self):
          logging.info("adding and validating substitute AAAA record rule in default dns view")
          data = {"ipv6addr": "2620:10a:6000:2400::62","name": "aaaa.rpz.com","view": "default","rp_zone": "rpz.com"}
          response = ib_NIOS.wapi_request('POST', object_type="record:rpz:aaaa",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          get_ref = ib_NIOS.wapi_request('GET',object_type="record:rpz:aaaa",params="?_inheritance=True&_return_fields=ipv6addr,name,view,rp_zone",grid_vip=config.grid_vip)
          print(get_ref)
          result = ['"ipv6addr": "2620:10a:6000:2400::62"','"name": "aaaa.rpz.com"','"rp_zone": "rpz.com"','"view": "default"']
          for i in result:
            if i in get_ref:
               assert True
            else:
               assert False
          print(result)
          print("Test Case 286 Executuion Completed")

      @pytest.mark.run(order=287)
      def test_287_Validate_EA_inheritance_at_substitute_AAAA_record_rule_in_default_dns_view(self):
          logging.info("validating EA inheritance at substitute AAAA record rule in default dns view")
          output = ib_NIOS.wapi_request('GET',object_type="record:rpz:aaaa",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox_rpz:inheritance_source::networkview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 287 Executuion Completed")

      @pytest.mark.run(order=288)
      def test_288_Add_and_validate_Substitute_MX_record_rule_in_default_dns_view(self):
          logging.info("adding and validating substitute MX record rule in default dns view")
          data = {"mail_exchanger": "rpz.com","name": "mx.rpz.com","preference": 10,"view": "default","rp_zone": "rpz.com"}
          response = ib_NIOS.wapi_request('POST', object_type="record:rpz:mx",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          get_ref = ib_NIOS.wapi_request('GET',object_type="record:rpz:mx",params="?_inheritance=True&_return_fields=mail_exchanger,name,preference,view,rp_zone",grid_vip=config.grid_vip)
          print(get_ref)
          result = ['"mail_exchanger": "rpz.com"','"name": "mx.rpz.com"','"preference": 10','"view": "default"','"rp_zone": "rpz.com"']
          for i in result:
            if i in get_ref:
               assert True
            else:
               assert False
          print(result)
          print("Test Case 288 Executuion Completed")

      @pytest.mark.run(order=289)
      def test_289_Validate_EA_inheritance_at_substitute_MX_record_rule_in_default_dns_view(self):
          logging.info("validating EA inheritance at substitute MX record rule in default dns view")
          output = ib_NIOS.wapi_request('GET',object_type="record:rpz:mx",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox_rpz:inheritance_source::networkview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 289 Executuion Completed")

      @pytest.mark.run(order=290)
      def test_290_Add_and_validate_Substitute_NAPTR_record_rule_in_default_dns_view(self):
          logging.info("adding and validating substitute NAPTR record rule in default dns view")
          data = {"name": "naptr.rpz.com","order": 10,"preference": 10,"regexp": "","replacement": ".","services": "http+E2U","view": "default","rp_zone": "rpz.com"}
          response = ib_NIOS.wapi_request('POST', object_type="record:rpz:naptr",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          get_ref = ib_NIOS.wapi_request('GET',object_type="record:rpz:naptr",params="?_inheritance=True&_return_fields=name,order,preference,regexp,replacement,services,view,rp_zone",grid_vip=config.grid_vip)
          print(get_ref)
          result = ['"name": "naptr.rpz.com"','"order": 10','"preference": 10','"regexp": ""','"replacement": "."','"services": "http+E2U"','"view": "default"','"rp_zone": "rpz.com"']
          for i in result:
            if i in get_ref:
               assert True
            else:
               assert False
          print(result)
          print("Test Case 290 Executuion Completed")

      @pytest.mark.run(order=291)
      def test_291_Validate_EA_inheritance_at_substitute_NAPTR_record_rule_in_default_dns_view(self):
          logging.info("validating EA inheritance at substitute NAPTR record rule in default dns view")
          output = ib_NIOS.wapi_request('GET',object_type="record:rpz:naptr",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox_rpz:inheritance_source::networkview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 291 Executuion Completed")

      @pytest.mark.run(order=292)
      def test_292_Add_and_validate_Substitute_TXT_record_rule_in_default_dns_view(self):
          logging.info("adding and validating substitute TXT record rule in default dns view")
          data = {"name": "txt.rpz.com","text": "testdata","view": "default","rp_zone": "rpz.com"}
          response = ib_NIOS.wapi_request('POST', object_type="record:rpz:txt",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          get_ref = ib_NIOS.wapi_request('GET',object_type="record:rpz:txt",params="?_inheritance=True&_return_fields=name,text,view,rp_zone",grid_vip=config.grid_vip)
          print(get_ref)
          result = ['"name": "txt.rpz.com"','"rp_zone": "rpz.com"','"view": "default"']
          for i in result:
            if i in get_ref:
               assert True
            else:
               assert False
          print(result)
          print("Test Case 292 Executuion Completed")

      @pytest.mark.run(order=293)
      def test_293_Validate_EA_inheritance_at_substitute_TXT_record_rule_in_default_dns_view(self):
          logging.info("validating EA inheritance at substitute TXT record rule in default dns view")
          output = ib_NIOS.wapi_request('GET',object_type="record:rpz:txt",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox_rpz:inheritance_source::networkview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 293 Executuion Completed")

      @pytest.mark.run(order=294)
      def test_294_Add_and_validate_Substitute_PTR_record_rule_in_default_dns_view(self):
          logging.info("adding and validating substitute PTR record rule in default dns view")
          data = {"ptrdname": "www.infoblox.com","view": "default","rp_zone": "rpz.com","ipv4addr": "10.35.0.8"}
          response = ib_NIOS.wapi_request('POST', object_type="record:rpz:ptr",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          get_ref = ib_NIOS.wapi_request('GET',object_type="record:rpz:ptr",params="?_inheritance=True&_return_fields=name,rp_zone,rp_zone,view,ipv4addr",grid_vip=config.grid_vip)
          print(get_ref)
          result = ['"ipv4addr": "10.35.0.8"','"name": "8.0.35.10.in-addr.arpa.rpz.com"','"rp_zone": "rpz.com"','"view": "default"']
          for i in result:
            if i in get_ref:
               assert True
            else:
               assert False
          print(result)
          print("Test Case 294 Executuion Completed")

      @pytest.mark.run(order=295)
      def test_295_Validate_EA_inheritance_at_substitute_PTR_record_rule_in_default_dns_view(self):
          logging.info("validating EA inheritance at substitute PTR record rule in default dns view")
          output = ib_NIOS.wapi_request('GET',object_type="record:rpz:ptr",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox_rpz:inheritance_source::networkview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 295 Executuion Completed")


      @pytest.mark.run(order=296)
      def test_296_Add_and_validate_Substitute_SRV_record_rule_in_default_dns_view(self):
          logging.info("adding and validating substitute SRV record rule in default dns view")
          data = {"name": "srv.rpz.com","port": 22,"priority": 0,"target": "rpz.com","view": "default","weight": 0,"rp_zone": "rpz.com"}
          response = ib_NIOS.wapi_request('POST', object_type="record:rpz:srv",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          get_ref = ib_NIOS.wapi_request('GET',object_type="record:rpz:srv",params="?_inheritance=True&_return_fields=name,port,priority,target,view,weight,rp_zone",grid_vip=config.grid_vip)
          print(get_ref)
          result = ['"name": "srv.rpz.com"','"port": 22','"priority": 0','"target": "rpz.com"','"view": "default"','"weight": 0','"rp_zone": "rpz.com"']
          for i in result:
            if i in get_ref:
               assert True
            else:
               assert False
          print(result)
          print("Test Case 296 Executuion Completed")

      @pytest.mark.run(order=297)
      def test_297_Validate_EA_inheritance_at_substitute_PTR_record_rule_in_default_dns_view(self):
          logging.info("validating EA inheritance at substitute PTR record rule in default dns view")
          output = ib_NIOS.wapi_request('GET',object_type="record:rpz:srv",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox_rpz:inheritance_source::networkview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 297 Executuion Completed")


      @pytest.mark.run(order=298)
      def test_298_Add_and_validate_Substitute_IPv4_Address_Rule_in_default_dns_view(self):
          logging.info("adding and validating substitute IPv4 address rule in default dns view")
          data = {"ipv4addr": "10.35.0.98","name": "10.35.0.99.rpz.com","view": "default","rp_zone": "rpz.com"}
          response = ib_NIOS.wapi_request('POST', object_type="record:rpz:a:ipaddress",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          get_ref = ib_NIOS.wapi_request('GET',object_type="record:rpz:a:ipaddress",params="?_inheritance=True&_return_fields=name,ipv4addr,view,rp_zone",grid_vip=config.grid_vip)
          print(get_ref)
          result = ['"ipv4addr": "10.35.0.98"','"name": "10.35.0.99.rpz.com"','"view": "default"','"rp_zone": "rpz.com"']
          for i in result:
            if i in get_ref:
               assert True
            else:
               assert False
          print(result)
          print("Test Case 298 Executuion Completed")

      @pytest.mark.run(order=299)
      def test_299_Validate_EA_inheritance_at_Substitute_IPv4_Address_rule_in_default_dns_view(self):
          logging.info("validating EA inheritance at substitute IPv4 Address rule in default dns view")
          output = ib_NIOS.wapi_request('GET',object_type="record:rpz:a:ipaddress",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox_rpz:inheritance_source::networkview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 299 Executuion Completed")

      @pytest.mark.run(order=300)
      def test_300_Add_and_validate_Substitute_IPv6_Address_Rule_in_default_dns_view(self):
          logging.info("adding and validating substitute IPv6 address rule in default dns view")
          data = {"ipv6addr": "2620:10a:6000:2400::3","name": "2620:10a:6000:2400::62.rpz.com","view": "default","rp_zone": "rpz.com"}
          response = ib_NIOS.wapi_request('POST', object_type="record:rpz:aaaa:ipaddress",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          get_ref = ib_NIOS.wapi_request('GET',object_type="record:rpz:aaaa:ipaddress",params="?_inheritance=True&_return_fields=ipv6addr,name,view,rp_zone",grid_vip=config.grid_vip)
          print(get_ref)
          result = ['"ipv6addr": "2620:10a:6000:2400::3"','"name": "2620:10a:6000:2400::62.rpz.com"','"view": "default"','"rp_zone": "rpz.com"']
          for i in result:
            if i in get_ref:
               assert True
            else:
               assert False
          print(result)
          print("Test Case 300 Executuion Completed")

      @pytest.mark.run(order=301)
      def test_301_Validate_EA_inheritance_at_Substitute_IPv4_Address_rule_in_default_dns_view(self):
          logging.info("validating EA inheritance at substitute IPv4 Address rule in default dns view")
          output = ib_NIOS.wapi_request('GET',object_type="record:rpz:aaaa:ipaddress",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox_rpz:inheritance_source::networkview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 301 Executuion Completed")

      @pytest.mark.run(order=302)
      def test_302_Add_and_validate_at_Passthru_domain_name_rule_in_default_dns_view(self):
          logging.info("adding and validating at Passthru rule in default dns view")
          data = {"canonical": "pass","name": "pass.rpz.com","view": "default","rp_zone": "rpz.com"}
          response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          get_ref = ib_NIOS.wapi_request('GET',object_type="record:rpz:cname",params="?_inheritance=True&_return_fields=canonical,name,view,rp_zone",grid_vip=config.grid_vip)
          print(get_ref)
          result = ['"canonical": "pass"','"name": "pass.rpz.com"','"view": "default"','"rp_zone": "rpz.com"']
          for i in result:
            if i in get_ref:
               assert True
            else:
               assert False
          print(result)
          print("Test Case 302 Executuion Completed")

      @pytest.mark.run(order=303)
      def test_303_Validate_EA_inheritance_at_Passthru_domain_name_rule_in_default_dns_view(self):
          logging.info("validating EA inheritance at substitute IPv4 Address rule in default dns view")
          output = ib_NIOS.wapi_request('GET',object_type="record:rpz:cname",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox_rpz:inheritance_source::networkview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 303 Executuion Completed")


      @pytest.mark.run(order=304)
      def test_304_Add_and_validate_at_block_domain_name_rule_in_default_dns_view(self):
          logging.info("adding and validating at Passthru rule in default dns view")
          data = {"canonical": "*","name": "block_domain.rpz.com","view": "default","rp_zone": "rpz.com"}
          response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          get_ref = ib_NIOS.wapi_request('GET',object_type="record:rpz:cname",params="?_inheritance=True&_return_fields=canonical,name,view",grid_vip=config.grid_vip)
          print(get_ref)
          result = ['"canonical": "*"','"name": "pass.rpz.com"','"view": "default"']
          for i in result:
            if i in get_ref:
               assert True
            else:
               assert False
          print(result)
          print("Test Case 304 Executuion Completed")

      @pytest.mark.run(order=305)
      def test_305_Validate_EA_inheritance_at_block_domain_name_rule_in_default_dns_view(self):
          logging.info("validating EA inheritance at substitute IPv4 Address rule in default dns view")
          get_ref = ib_NIOS.wapi_request('GET',object_type="record:rpz:cname",grid_vip=config.grid_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,object_type="record:rpz:cname",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox_rpz:inheritance_source::networkview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 305 Executuion Completed")


#################################################################################
#################### Override EA value at DNS view ##############################
#################################################################################


      @pytest.mark.run(order=306)
      def test_306_Override_and_Validate_EA_value_at_default_dns_view(self):
          logging.info("overriding and validating EA value at dns view")
          #output = ib_NIOS.wapi_request('GET',object_type="view",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          #print(output)
          get_ref = ib_NIOS.wapi_request('GET', object_type="view", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print(ref1)
          data = {"extattrs": {"infoblox_rpz": {"value": "2000"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          output = ib_NIOS.wapi_request('GET',object_type="zone_rp",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ["extattrs:infoblox_rpz:inheritance_source::view","value:2000"]
          for i in result:
             if i in output:
                assert True
             else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 306 Executuion Completed")



      @pytest.mark.run(order=307)
      def test_307_Validate_EA_inheritance_at_substitute_A_record_rule_in_default_dns_view(self):
          logging.info("validating EA inheritance at substitute A record rule in default dns view")
          output = ib_NIOS.wapi_request('GET',object_type="record:rpz:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox_rpz:inheritance_source::view',"value:2000"]
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 307 Executuion Completed")



      @pytest.mark.run(order=308)
      def test_308_Validate_EA_inheritance_at_substitute_AAAA_record_rule_in_default_dns_view(self):
          logging.info("validating EA inheritance at substitute AAAA record rule in default dns view")
          output = ib_NIOS.wapi_request('GET',object_type="record:rpz:aaaa",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox_rpz:inheritance_source::view','value:2000']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 308 Executuion Completed")

      @pytest.mark.run(order=309)
      def test_309_Validate_EA_inheritance_at_Substitute_IPv4_Address_rule_in_default_dns_view(self):
          logging.info("validating EA inheritance at substitute IPv4 Address rule in default dns view")
          output = ib_NIOS.wapi_request('GET',object_type="record:rpz:a:ipaddress",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox_rpz:inheritance_source::view','value:2000']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 309 Executuion Completed")

      @pytest.mark.run(order=310)
      def test_310_Validate_EA_inheritance_at_Substitute_IPv6_Address_rule_in_default_dns_view(self):
          logging.info("validating EA inheritance at substitute IPv4 Address rule in default dns view")
          output = ib_NIOS.wapi_request('GET',object_type="record:rpz:aaaa:ipaddress",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox_rpz:inheritance_source::view','value:2000']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 310 Executuion Completed")


      @pytest.mark.run(order=311)
      def test_311_Validate_EA_inheritance_at_Passthru_rule_in_default_dns_view(self):
          logging.info("validating EA inheritance at substitute IPv4 Address rule in default dns view")
          output = ib_NIOS.wapi_request('GET',object_type="record:rpz:cname",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox_rpz:inheritance_source::view','value:2000']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 311 Executuion Completed")


      @pytest.mark.run(order=312)
      def test_312_Validate_EA_inheritance_at_Passthru_rule_in_default_dns_view(self):
          logging.info("validating EA inheritance at substitute IPv4 Address rule in default dns view")
          get_ref = ib_NIOS.wapi_request('GET',object_type="record:rpz:cname",grid_vip=config.grid_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,object_type="record:rpz:cname",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox_rpz:inheritance_source::view','value:2000']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 312 Executuion Completed")



#################################################################################################
#################### Override EA value at Response Policy Zone ##################################
#################################################################################################


      @pytest.mark.run(order=313)
      def test_313_Override_and_Validate_EA_value_at_default_dns_view(self):
          logging.info("overriding and validating EA value at dns view")
          get_ref = ib_NIOS.wapi_request('GET', object_type="zone_rp", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print(ref1)
          data = {"extattrs": {"infoblox_rpz": {"value": "3000"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          output = ib_NIOS.wapi_request('GET',object_type="zone_rp",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = "extattrs:infoblox_rpz:value:3000"
          if result in output:
                assert True
          else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 313 Executuion Completed")


      @pytest.mark.run(order=314)
      def test_314_Validate_EA_inheritance_at_substitute_A_record_rule_in_default_dns_view(self):
          logging.info("validating EA inheritance at substitute A record rule in default dns view")
          output = ib_NIOS.wapi_request('GET',object_type="record:rpz:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          print(output)
          result = ['extattrs:infoblox_rpz:inheritance_source::zone_rp',"value:3000"]
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 314 Executuion Completed")

      @pytest.mark.run(order=315)
      def test_315_Validate_EA_inheritance_at_substitute_AAAA_record_rule_in_default_dns_view(self):
          logging.info("validating EA inheritance at substitute AAAA record rule in default dns view")
          output = ib_NIOS.wapi_request('GET',object_type="record:rpz:aaaa",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox_rpz:inheritance_source::zone_rp','value:3000']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 315 Executuion Completed")

      @pytest.mark.run(order=316)
      def test_316_Validate_EA_inheritance_at_Substitute_IPv4_Address_rule_in_default_dns_view(self):
          logging.info("validating EA inheritance at substitute IPv4 Address rule in default dns view")
          output = ib_NIOS.wapi_request('GET',object_type="record:rpz:a:ipaddress",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox_rpz:inheritance_source::zone_rp','value:3000']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 316 Executuion Completed")

      @pytest.mark.run(order=317)
      def test_317_Validate_EA_inheritance_at_Substitute_IPv6_Address_rule_in_default_dns_view(self):
          logging.info("validating EA inheritance at substitute IPv4 Address rule in default dns view")
          output = ib_NIOS.wapi_request('GET',object_type="record:rpz:aaaa:ipaddress",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox_rpz:inheritance_source::zone_rp','value:3000']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 317 Executuion Completed")

      @pytest.mark.run(order=318)
      def test_318_Validate_EA_inheritance_at_Passthru_rule_in_default_dns_view(self):
          logging.info("validating EA inheritance at substitute IPv4 Address rule in default dns view")
          output = ib_NIOS.wapi_request('GET',object_type="record:rpz:cname",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox_rpz:inheritance_source::zone_rp','value:3000']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 318 Executuion Completed")


      @pytest.mark.run(order=319)
      def test_319_Validate_EA_inheritance_at_Passthru_rule_in_default_dns_view(self):
          logging.info("validating EA inheritance at substitute IPv4 Address rule in default dns view")
          get_ref = ib_NIOS.wapi_request('GET',object_type="record:rpz:cname",grid_vip=config.grid_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,object_type="record:rpz:cname",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox_rpz:inheritance_source::zone_rp','value:3000']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 319 Executuion Completed")

################################################################################################
###################### Override EA at RPZ record level #########################################
################################################################################################



      @pytest.mark.run(order=320)
      def test_320_Override_and_Validate_EA_value_at_RPZ_Record_A(self):
          logging.info("overriding and validating EA value at dns view")
          get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:a", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print(ref1)
          data = {"extattrs": {"infoblox_rpz": {"value": "4000"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          output = ib_NIOS.wapi_request('GET',object_type="record:rpz:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = "extattrs:infoblox_rpz:value:4000"
          if result in output:
                assert True
          else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 320 Executuion Completed")

      @pytest.mark.run(order=321)
      def test_321_Override_and_Validate_EA_value_at_RPZ_Record_AAAA(self):
          logging.info("overriding and validating EA value at RPZ Record A")
          get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:aaaa", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print(ref1)
          data = {"extattrs": {"infoblox_rpz": {"value": "4000"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          output = ib_NIOS.wapi_request('GET',object_type="record:rpz:aaaa",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = "extattrs:infoblox_rpz:value:4000"
          if result in output:
                assert True
          else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 321 Executuion Completed")



######################################################################################
################## RPZ Scenarios in custom DNS view ##################################
######################################################################################


      @pytest.mark.run(order=322)
      def test_322_Add_and_Validate_custom_dns_view(self):
          logging.info("adding custom dns view")
          data = {"name": "custom"}
          response = ib_NIOS.wapi_request('POST', object_type="view",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="view",grid_vip=config.grid_vip)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          print(output)
          result = 'is_default:false,name:custom'
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 322 Executuion Completed")

      @pytest.mark.run(order=323)
      def test_323_Validate_EA_inheritance_at_custom_dns_view(self):
          logging.info("validating EA inheritance at custom dns view")
          get_ref = ib_NIOS.wapi_request('GET', object_type="view", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',object_type="view",ref=ref1,params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox_rpz:inheritance_source::networkview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 323 Executuion Completed")

      @pytest.mark.run(order=324)
      def test_324_Create_response_policy_zone_in_custom_dns_view(self):
          logging.info("creating response policy zone in custom dns view")
          fqdn=config.grid_vip.split('.')
          fqdn='ib-'+str(fqdn[0])+'-'+str(fqdn[1])+'-'+str(fqdn[2])+'-'+str(fqdn[3])+'.infoblox.com'
          data = {"fqdn": "infoblox.com","grid_primary": [{"name": fqdn,"stealth": False}],"view": "custom"}
          response = ib_NIOS.wapi_request('POST', object_type="zone_rp", fields=json.dumps(data), grid_vip=config.grid_vip)
          print(response)
          print("Test Case 324 Executuion Completed")

      @pytest.mark.run(order=325)
      def test_325_Validate_EA_inheritance_at_custom_dns_view(self):
          logging.info("validating EA inheritance at custom dns view")
          get_ref = ib_NIOS.wapi_request('GET', object_type="zone_rp")
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',object_type="view",ref=ref1,params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox_rpz:inheritance_source::networkview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 325 Executuion Completed")


      @pytest.mark.run(order=326)
      def test_326_Create_Substitute_A_record_rule_in_custom_dns_view(self):
          logging.info("creating substitute A record rule in custom dns view")
          fqdn=config.grid_vip.split('.')
          fqdn='ib-'+str(fqdn[0])+'-'+str(fqdn[1])+'-'+str(fqdn[2])+'-'+str(fqdn[3])+'.infoblox.com'
          data = {"ipv4addr": "10.90.90.9","name": "a.infoblox.com","view": "custom","rp_zone": "infoblox.com"}
          response = ib_NIOS.wapi_request('POST', object_type="record:rpz:a", fields=json.dumps(data), grid_vip=config.grid_vip)
          print(response)
          print("Test Case 326 Executuion Completed")

      @pytest.mark.run(order=327)
      def test_327_Validate_created_Substitute_A_record_rule_in_custom_dns_view(self):
          logging.info("validating created substitute A record rule in custom dns view")
          get_ref = ib_NIOS.wapi_request('GET',object_type="record:rpz:a",params="?_inheritance=True&_return_fields=rp_zone,ipv4addr,name,view",grid_vip=config.grid_vip)
          print(get_ref)
          result = ['"ipv4addr": "10.90.90.9"','"name": "a.infoblox.com"','"rp_zone": "infoblox.com"','"view": "custom"']
          for i in result:
            if i in get_ref:
               assert True
            else:
               assert False
          print(result)
          print("Test Case 327 Executuion Completed")

      @pytest.mark.run(order=328)
      def test_328_Validate_EA_inheritance_at_substitute_A_record_rule_in_custom_dns_view(self):
          logging.info("validating EA inheritance at substitute A record rule in custom dns view")
          get_ref = ib_NIOS.wapi_request('GET',object_type="record:rpz:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(get_ref)
          output = get_ref
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          print(output)
          result = ['extattrs:infoblox_rpz:inheritance_source::networkview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 328 Executuion Completed")

      @pytest.mark.run(order=329)
      def test_329_Add_and_validate_at_Passthru_domain_name_rule_in_custom_dns_view(self):
          logging.info("adding and validating at Passthru rule in default dns view")
          data = {"canonical": "pass","name": "pass.infoblox.com","view": "custom","rp_zone": "infoblox.com"}
          response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          get_ref = ib_NIOS.wapi_request('GET',object_type="record:rpz:cname",params="?_inheritance=True&_return_fields=canonical,name,view",grid_vip=config.grid_vip)
          print(get_ref)
          result = ['"canonical": "pass"','"name": "pass.infoblox.com"','"view": "custom"']
          for i in result:
            if i in get_ref:
               assert True
            else:
               assert False
          print(result)
          print("Test Case 329 Executuion Completed")

      @pytest.mark.run(order=330)
      def test_330_Validate_EA_inheritance_at_Passthru_domain_name_rule_in_custom_dns_view(self):
          logging.info("validating EA inheritance at passthru rule in custom dns view")
          get_ref = ib_NIOS.wapi_request('GET',object_type="record:rpz:cname",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(get_ref)
          output = get_ref
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox_rpz:inheritance_source::networkview','value:100']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 330 Executuion Completed")

      @pytest.mark.run(order=331)
      def test_331_Override_and_Validate_EA_value_at_response_policy_zone_in_custom_dns_view(self):
          logging.info("overriding and validating EA value at dns view")
          #output = ib_NIOS.wapi_request('GET',object_type="view",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          #print(output)
          get_ref = ib_NIOS.wapi_request('GET', object_type="view", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"extattrs": {"infoblox_rpz": {"value": "5000"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          output = ib_NIOS.wapi_request('GET',object_type="zone_rp",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ["extattrs:infoblox_rpz:inheritance_source::view","value:5000"]
          for i in result:
             if i in output:
                assert True
             else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 331 Executuion Completed")

      @pytest.mark.run(order=332)
      def test_332_Validate_EA_inheritance_at_substitute_A_record_rule_in_custom_dns_view(self):
          logging.info("validating EA inheritance at substitute A record rule in custom dns view")
          get_ref = ib_NIOS.wapi_request('GET',object_type="record:rpz:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(get_ref)
          output = get_ref
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox_rpz:inheritance_source::view','value:5000']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 332 Executuion Completed")


      @pytest.mark.run(order=333)
      def test_333_Validate_EA_inheritance_at_Passthru_domain_name_rule_in_custom_dns_view(self):
          logging.info("validating EA inheritance at substitute A record rule in custom dns view")
          get_ref = ib_NIOS.wapi_request('GET',object_type="record:rpz:cname",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(get_ref)
          output = get_ref
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox_rpz:inheritance_source::view','value:5000']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 333 Executuion Completed")

      @pytest.mark.run(order=334)
      def test_334_Override_and_Validate_EA_value_at_response_policy_zone_in_custom_dns_view(self):
          logging.info("overriding and validating EA value at response policy zone in custom dns view")
          get_ref = ib_NIOS.wapi_request('GET', object_type="zone_rp", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"extattrs": {"infoblox_rpz": {"value": "6000"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          output = ib_NIOS.wapi_request('GET',object_type="zone_rp",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = "extattrs:infoblox_rpz:value:6000"
          if result in output:
                assert True
          else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 334 Executuion Completed")

      @pytest.mark.run(order=335)
      def test_335_Validate_EA_inheritance_at_Substitute_A_record_rule_in_custom_dns_view(self):
          logging.info("validating EA inheritance at substitute A record rule in custom dns view")
          get_ref = ib_NIOS.wapi_request('GET',object_type="record:rpz:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(get_ref)
          output = get_ref
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox_rpz:inheritance_source::zone_rp','value:6000']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 335 Executuion Completed")

      @pytest.mark.run(order=336)
      def test_336_Validate_EA_inheritance_at_Passthru_domain_name_rule_in_custom_dns_view(self):
          logging.info("validating EA inheritance at passthru domain name rule in custom dns view")
          get_ref = ib_NIOS.wapi_request('GET',object_type="record:rpz:cname",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(get_ref)
          output = get_ref
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ['extattrs:infoblox_rpz:inheritance_source::zone_rp','value:6000']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 336 Executuion Completed")

      @pytest.mark.run(order=337)
      def test_337_Override_and_Validate_EA_value_at_RPZ_Record_A_in_custom_dns_view(self):
          logging.info("overriding and validating EA value at RPZ record A in custom dns view")
          get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:a", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"extattrs": {"infoblox_rpz": {"value": "7000"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          output = ib_NIOS.wapi_request('GET',object_type="record:rpz:a",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = "extattrs:infoblox_rpz:value:7000"
          if result in output:
                assert True
          else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 337 Executuion Completed")

###############################################################################################################
############################ RPZ Scenarios in custom network view #############################################
###############################################################################################################


      @pytest.mark.run(order=338)
      def test_338_Add_and_Validate_network_view(self):
          logging.info("adding and validating network view")
          data = {"name": "custom1"}
          response = ib_NIOS.wapi_request('POST', object_type="networkview",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="networkview",grid_vip=config.grid_vip)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = 'is_default:false,name:custom1'
          if result in output:
                assert True
          else:
                assert False
          print(result)
          print("Test Case 338 Executuion Completed")

      @pytest.mark.run(order=339)
      def test_339_Add_and_Validate_Extensible_attribute(self):
          logging.info("adding and validating extensible attribute")
          data = {"default_value": "200","name": "local","type": "STRING"}
          response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef",fields=json.dumps(data),grid_vip=config.grid_vip)
          print(response)
          output = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(output)
          res = json.loads(output)
          ref1 = json.loads(output)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=default_value,name",grid_vip=config.grid_vip)
          print(output)
          result = ['"name": "local"','"default_value": "200"']
          for i in result:
              if i in output:
                  assert True
              else:
                  assert False
          print(result)
          print("Test Case 339 Executuion Completed")


      @pytest.mark.run(order=340)
      def test_340_Associate_and_Validate_EA_at_custom_network_view(self):
          logging.info("addinga and validating EA at custom network view")
          get_ref = ib_NIOS.wapi_request('GET', object_type="networkview", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"extattrs": {"local": {"value": "200"}}}
          view = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(view)
          sleep(03)
          output = ib_NIOS.wapi_request('GET',object_type="networkview",ref=ref1,params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          print(output)
          result = ['extattrs:local:value:200','networkview','custom1/false']
          for i in result:
            if i in output:
                  assert True
            else:
                  assert False
          print(result)
          print("Test Case 340 Executuion Completed")

      @pytest.mark.run(order=341)
      def test_341_Modify_descendants_action(self):
          logging.info("modifying descendant actions")
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",params="?_inheritance=True&_return_fields=name",grid_vip=config.grid_vip)
          print(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"descendants_action": {"option_with_ea": "INHERIT","option_without_ea": "INHERIT"},"flags": "I"}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          #print(output)
          sleep(03)
          get_ref = ib_NIOS.wapi_request('GET',object_type="extensibleattributedef",ref=ref1,params="?_inheritance=True&_return_fields=flags,name",grid_vip=config.grid_vip)
          print(get_ref)
          result = ['"flags": "I"','"name": "local"']
          for i in result:
           if i in get_ref:
               assert True
           else:
                assert False
          print(result)
          print("Test Case 341 Executuion Completed")


      @pytest.mark.run(order=342)
      def test_342_Create_response_policy_zone_in_custom_network_view(self):
          logging.info("creating response policy zone in custom dns view")
          fqdn=config.grid_vip.split('.')
          fqdn='ib-'+str(fqdn[0])+'-'+str(fqdn[1])+'-'+str(fqdn[2])+'-'+str(fqdn[3])+'.infoblox.com'
          data = {"fqdn": "infoblox1.com","grid_primary": [{"name": fqdn,"stealth": False}],"view": "default.custom1"}
          response = ib_NIOS.wapi_request('POST', object_type="zone_rp", fields=json.dumps(data), grid_vip=config.grid_vip)
          print(response)
          print("Test Case 342 Executuion Completed")

      @pytest.mark.run(order=343)
      def test_343_Validate_EA_inheritance_at_dns_view(self):
          logging.info("validating EA inheritance at dns view")
          get_ref = ib_NIOS.wapi_request('GET',object_type="view",grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          output = ib_NIOS.wapi_request('GET',object_type="view",ref=ref1,params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          output = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          print(output)
          result = ['extattrs:local:inheritance_source::networkview','value:200']
          for i in result:
            if i in output:
                assert True
            else:
                assert False
          print(result)
          print("Test Case 343 Executuion Completed")

      @pytest.mark.run(order=344)
      def test_344_Override_and_Validate_EA_value_at_custom_default_dns_view_in_custom_network_view(self):
          logging.info("overriding and validating EA value at dns view")
          #output = ib_NIOS.wapi_request('GET',object_type="view",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          #print(output)
          get_ref = ib_NIOS.wapi_request('GET', object_type="view", grid_vip=config.grid_vip)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[-1]['_ref']
          print(ref1)
          data = {"extattrs": {"local": {"value": "8000"}}}
          output = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
          print(output)
          output = ib_NIOS.wapi_request('GET',object_type="zone_rp",params="?_inheritance=True&_return_fields=extattrs",grid_vip=config.grid_vip)
          print(output)
          output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
          #print(output)
          result = ["extattrs:local:inheritance_source::view","value:8000"]
          for i in result:
             if i in output:
                assert True
             else:
                assert False
          print(result)
          sleep(03)
          print("Test Case 344 Executuion Completed")





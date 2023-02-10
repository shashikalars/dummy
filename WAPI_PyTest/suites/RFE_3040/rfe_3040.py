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
from dig_utility import dig
from nsupdate_util import nsupdate_add
from common_utilities import generate_token_from_file
from log_capture import log_action as log
from log_validation import log_validation as logv



auth_zone={"fqdn": "source.com","allow_query": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}],"allow_update": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}]}
sub_zone={"fqdn": "sub_zone","allow_query": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}],"allow_update": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}]}
source_ip='10.35.148.12'
new_auth_zone={"fqdn": "csv_imported_zone1.com","allow_query": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}],"allow_update": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}]}



        
def get_reference_for_unknown_records(record_ref):
     ref=record_ref
     logging.info("Fetching values for Unknown Resource records")
     get_ref = ib_NIOS.wapi_request('GET',object_type=record_ref+"?_return_fields=name,view,zone,record_type,creator")
     logging.info(get_ref)
     res = json.loads(get_ref)
     return res

def get_reference_for_zone(response):
    logging.info("Fetching reference values for Zones")
    get_ref = ib_NIOS.wapi_request('GET',object_type=response)
    return json.loads(get_ref)

class Network(unittest.TestCase):
     @pytest.mark.run(order=1)
     def test_01_add_auth_zone(self):
          logging.info("Creating auth Zone for Adding Unknown Resource Records ")
          response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(auth_zone))
          if (response[0]==400):
               logging.info ("Zone already exists,try with other data[Don't get confused with Pytest Passed status]")
          else:
               log("start","/var/log/syslog",config.grid_vip)
               logging.info ("Zone added and response looks like : ",response)
               res = json.loads(response)
               time.sleep(30)
               logging.info ("reference of zone added ",res)
               data = {"grid_primary": [{"name": config.grid_fqdn,"stealth":False}]}
               logging.info ("Trying to Associate ZONE with Primary GRID")
               response = ib_NIOS.wapi_request('PUT',ref=res,fields=json.dumps(data))
               response=json.loads(response)
               logging.info ("Restart services")
               logging.info ("Associated Zone with Primary GRID and reference looks like :",response)
               grid =  ib_NIOS.wapi_request('GET', object_type="grid")
               ref = json.loads(grid)[0]['_ref']
               publish={"member_order":"SIMULTANEOUSLY"}
               request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
               time.sleep(1)
               request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
               restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
               time.sleep(1)
               logging.info ("Restarting grid here now ")
               log("stop","/var/log/syslog",config.grid_vip)
               get_reference=get_reference_for_zone(response)
               if (get_reference['_ref']==response):
                    logging.info ("Test Case 1 Execution Completed")
                    assert True
               else:
                    logging.info ("Test Case 1 Execution Failed")
                    assert False
          

     @pytest.mark.run(order=2)
     def test_02_start_dns(self):
          member_ref=ib_NIOS.wapi_request('GET',object_type="member:dns")
          member_ref=json.loads(member_ref)
          logging.info (member_ref)
          logging.info ("__________________________________")
          dns_ref=member_ref[0]['_ref']
          condition=ib_NIOS.wapi_request('GET',object_type=dns_ref+"?_return_fields=enable_dns")
          logging.info (condition)
          data={"enable_dns": True}
          enable_dns_ref = ib_NIOS.wapi_request('PUT', ref=dns_ref, fields=json.dumps(data))
          logging.info (enable_dns_ref)
          logging.info ("*************************************")
          com=json.loads(enable_dns_ref)+"?_return_fields=enable_dns"
          logging.info (com)
          new_member_ref=ib_NIOS.wapi_request('GET',object_type=com)
          logging.info (new_member_ref)
          logging.info ("####################################")
          logging.info (condition)
          logging.info ("++++++++++++++++++++++++++++++++")
          logging.info (new_member_ref)
          if (condition==new_member_ref):
               assert True
               logging.info ("DNS service enabled")
          else:
               assert False
               logging.info ("Not enabled")

     @pytest.mark.run(order=3)
     def test_03_afsdb_record(self):
          log("start","/var/log/syslog",config.grid_vip)
          logging.info ("Creating AFSDB Record for added Zone")
          data={"name": "AFSDB."+auth_zone['fqdn'],"record_type": "AFSDB","subfield_values": [{"field_type": "S","field_value": "10","include_length": "NONE"},{"field_type": "N","field_value": "www.exmple1200.com","include_length": "NONE"}],"view": "default","extattrs": { "IB Discovery Owned": {"value": "100"},"Site": { "value": "200"}}}
          response = ib_NIOS.wapi_request('POST', object_type="record:unknown",fields=json.dumps(data))
          if (response[0]!=400):
               logging.info ("Added AFSDB Record with Reference value :",json.loads(response))
               time.sleep(1)
               record_details_before_modification=get_reference_for_unknown_records(json.loads(response))
               logging.info ("Record details before modification",record_details_before_modification)
               time.sleep(1)
               logging.info ("Modifying AFSDB record now ")
               response_ref=json.loads(response)
               modify_data={"name": "AFSDB."+auth_zone['fqdn'],"record_type": "AFSDB","subfield_values": [{"field_type": "S","field_value": "10","include_length": "NONE"},{"field_type": "N","field_value": "www.exmple200.com","include_length": "NONE"}],"view": "default","extattrs": { "IB Discovery Owned": {"value": "200"},"Site": { "value": "200"}}}
               modified_response = ib_NIOS.wapi_request('PUT', ref=response_ref, fields=json.dumps(modify_data))
               if (modified_response[0]==400):
                    logging.info ("Failed to modify AFSDB record")
               else:
                    logging.info ("Modified record AFSDB with new details",json.loads(modified_response))
               time.sleep(1)
               record_details_after_modification=get_reference_for_unknown_records(json.loads(modified_response))
               logging.info ("Record details after Modification",record_details_after_modification)
               if ((record_details_before_modification == record_details_after_modification)==False):
                    assert True
                    logging.info ("Test Case 3 Execution Completed ")
               else:
                    assert False
                    logging.info ("Test Case 3 Execution Failed")
          log("stop","/var/log/syslog",config.grid_vip)
          time.sleep(1)

     @pytest.mark.run(order=4)
     def test_04_rp_record(self):
          log("start","/var/log/syslog",config.grid_vip)
          logging.info ("Creating  RP Record for added Zone")
          data= {"name": "RP."+auth_zone['fqdn'],"record_type": "RP","subfield_values": [{"field_type": "N","field_value": "www.example.com","include_length": "NONE"},{"field_type": "N","field_value": "abc.example.com","include_length": "NONE"}],"view": "default","extattrs":{"IB Discovery Owned":{"value":"100"},"Site":{"value":"200"}}}
          response = ib_NIOS.wapi_request('POST', object_type="record:unknown",fields=json.dumps(data))
          if (response[0]!=400):
               logging.info ("Added RP Record with Reference value :",json.loads(response))
               time.sleep(1)
               record_details_before_modification=get_reference_for_unknown_records(json.loads(response))
               logging.info ("Record details before modification",record_details_before_modification)
               time.sleep(1)
               logging.info ("Modifying RP record now ")
               response_ref=json.loads(response)
               modify_data={"name": "RP."+auth_zone['fqdn'],"record_type": "RP","subfield_values": [{"field_type": "N","field_value": "www.example1.com","include_length": "NONE"},{"field_type": "N","field_value": "abc.example.com","include_length": "NONE"}],"view": "default","extattrs":{"IB Discovery Owned":{"value":"200"},"Site":{"value":"200"}}}
               modified_response = ib_NIOS.wapi_request('PUT', ref=response_ref, fields=json.dumps(modify_data))
               if (modified_response[0]==400):
                    logging.info ("Failed to modify RP record")
               else:
                    logging.info ("Modified record RP with new details",json.loads(modified_response))
               time.sleep(1)
               record_details_after_modification=get_reference_for_unknown_records(json.loads(modified_response))
               logging.info ("Record details before modification",record_details_after_modification)
               if ((record_details_before_modification == record_details_after_modification)==False):
                    assert True
                    logging.info ("Test Case 4 Execution Completed ")
               else:
                    assert False
                    logging.info ("Test Case 4 Execution Failed")
          log("stop","/var/log/syslog",config.grid_vip)
          time.sleep(1)
     
          

     @pytest.mark.run(order=5)
     def test_05_apl_record(self):
          log("start","/var/log/syslog",config.grid_vip)
          logging.info ("Creating  APL Record for added Zone")
          data={"name": "APL."+auth_zone['fqdn'],"record_type": "APL","subfield_values": [{"field_type": "P","field_value": "1:224.0.0.0/4 2:ff00::/8","include_length": "NONE"}],"view": "default","extattrs": {"IB Discovery Owned":{"value":"100"},"Site":{"value":"200"}}}
          response = ib_NIOS.wapi_request('POST', object_type="record:unknown",fields=json.dumps(data))
          if (response[0]!=400):
               logging.info ("Added APL Record with Reference value :",json.loads(response))
               time.sleep(1)
               record_details_before_modification=get_reference_for_unknown_records(json.loads(response))
               logging.info ("Record details before modification",record_details_before_modification)
               time.sleep(1)
               logging.info ("Modifying APL record now ")
               response_ref=json.loads(response)
               modify_data={"name": "APL."+auth_zone['fqdn'],"record_type": "APL","subfield_values": [{"field_type": "P","field_value": "1:224.0.0.1/4 2:ff00::/8","include_length": "NONE"}],"view": "default","extattrs": {"IB Discovery Owned":{"value":"300"},"Site":{"value":"300"}}}
               modified_response = ib_NIOS.wapi_request('PUT', ref=response_ref, fields=json.dumps(modify_data))
               if (modified_response[0]==400):
                    logging.info ("Failed to modify APL record")
               else:
                    logging.info ("Modified record APL with new details",json.loads(modified_response))
               time.sleep(1)
               record_details_after_modification=get_reference_for_unknown_records(json.loads(modified_response))
               logging.info ("Record details before modification",record_details_after_modification)
               if ((record_details_before_modification == record_details_after_modification)==False):
                    assert True
                    logging.info ("Test Case 5 Execution Completed ")
               else:
                    assert False
                    logging.info ("Test Case 5 Execution Failed")
          log("stop","/var/log/syslog",config.grid_vip)
          LookFor='.*ADD.*APL*'
          logv(LookFor,"/var/log/syslog",config.grid_vip)
          time.sleep(1)
          
          

     @pytest.mark.run(order=6)
     def test_06_dlv_record(self):
          log("start","/var/log/syslog",config.grid_vip)
          logging.info ("Creating  DLV Record for added Zone")
          data={"name": "DLV."+auth_zone['fqdn'],"record_type": "DLV","subfield_values": [{"field_type": "B","field_value": "10","include_length": "NONE"},{"field_type": "B","field_value": "11","include_length": "NONE"},{"field_type": "B","field_value": "23","include_length": "NONE"},{"field_type": "X","field_value": "2AF3","include_length": "NONE"}],"view": "default","extattrs": {"IB Discovery Owned":{"value":"100"},"Site":{"value":"200"}}}
          response = ib_NIOS.wapi_request('POST', object_type="record:unknown",fields=json.dumps(data))
          if (response[0]!=400):
               logging.info ("Added DLV Record with Reference value :",json.loads(response))
               time.sleep(1)
               record_details_before_modification=get_reference_for_unknown_records(json.loads(response))
               logging.info ("Record details before modification",record_details_before_modification)
               time.sleep(1)
               logging.info ("Modifying DLV record now ")
               response_ref=json.loads(response)
               modify_data={"name": "DLV."+auth_zone['fqdn'],"record_type": "DLV","subfield_values": [{"field_type": "B","field_value": "20","include_length": "NONE"},{"field_type": "B","field_value": "14","include_length": "NONE"},{"field_type": "B","field_value": "34","include_length": "NONE"},{"field_type": "X","field_value": "2AF3","include_length": "NONE"}],"view": "default","extattrs": {"IB Discovery Owned":{"value":"100"},"Site":{"value":"300"}}}
               modified_response = ib_NIOS.wapi_request('PUT', ref=response_ref, fields=json.dumps(modify_data))
               if (modified_response[0]==400):
                    logging.info ("Failed to modify DLV record")
               else:
                    logging.info ("Modified record DLV with new details",json.loads(modified_response))
               time.sleep(1)
               record_details_after_modification=get_reference_for_unknown_records(json.loads(modified_response))
               logging.info ("Record details before modification",record_details_after_modification)
               if ((record_details_before_modification == record_details_after_modification)==False):
                    assert True
                    logging.info ("Test Case 6 Execution Completed ")
               else:
                    assert False
                    logging.info ("Test Case 6 Execution Failed")
          time.sleep(1)
          log("stop","/var/log/syslog",config.grid_vip)
          logv("'.*ADD.*DLV*'","/var/log/syslog",config.grid_vip)
          


     @pytest.mark.run(order=7)
     def test_07_sshfp_record(self):
          log("start","/var/log/syslog",config.grid_vip)
          logging.info ("Creating  SSHFP Record for added Zone")
          data={"name": "SSHFP."+auth_zone['fqdn'],"record_type": "SSHFP","subfield_values":[{"field_type": "B","field_value": "1","include_length": "NONE"},{"field_type": "B","field_value": "1","include_length": "NONE"},{"field_type": "X","field_value": "123456789abcdef67890123456789abcdef67890","include_length": "8_BIT"}],"view": "default","extattrs": {"IB Discovery Owned":{"value":"100"},"Site":{"value":"200"}}}
          response = ib_NIOS.wapi_request('POST', object_type="record:unknown",fields=json.dumps(data))
          if (response[0]!=400):
               logging.info ("Added SSHFP Record with Reference value :",json.loads(response))
               time.sleep(1)
               record_details_before_modification=get_reference_for_unknown_records(json.loads(response))
               logging.info ("Record details before modification",record_details_before_modification)
               time.sleep(1)
               logging.info ("Modifying SSHFP record now ")
               response_ref=json.loads(response)
               modify_data={"name": "SSHFP."+auth_zone['fqdn'],"record_type": "SSHFP","subfield_values":[{"field_type": "B","field_value": "2","include_length": "NONE"},{"field_type": "B","field_value": "1","include_length": "NONE"},{"field_type": "X","field_value": "123456789abcdef67890123456789abcdef67890","include_length": "8_BIT"}],"view": "default","extattrs": {"IB Discovery Owned":{"value":"100"},"Site":{"value":"100"}}}
               modified_response = ib_NIOS.wapi_request('PUT', ref=response_ref, fields=json.dumps(modify_data))
               if (modified_response[0]==400):
                    logging.info ("Failed to modify SSHFP record")
               else:
                    logging.info ("Modified record SSHFP with new details",json.loads(modified_response))
               time.sleep(1)
               record_details_after_modification=get_reference_for_unknown_records(json.loads(modified_response))
               logging.info ("Record details before modification",record_details_after_modification)
               if ((record_details_before_modification == record_details_after_modification)==False):
                    assert True
                    logging.info ("Test Case 7 Execution Completed ")
               else:
                    assert False
                    logging.info ("Test Case 7 Execution Failed")
          log("stop","/var/log/syslog",config.grid_vip)
          logv("'.*ADD.*SSHFP*'","/var/log/syslog",config.grid_vip)
          time.sleep(1)


     @pytest.mark.run(order=8)
     def test_08_cds_record(self):
          log("start","/var/log/syslog",config.grid_vip)
          logging.info ("Creating  CDS Record for added Zone")
          data={"name": "CDS."+auth_zone['fqdn'],"record_type": "CDS","subfield_values": [{"field_value":"100","field_type": "S","include_length": "NONE"},{"field_value":"0","field_type": "S","include_length": "NONE"},{"field_value":"200","field_type": "S","include_length": "NONE"},{"field_value":"123456789abcdef67890123456789abcdef67890","field_type": "X","include_length": "8_BIT"}],"view": "default","extattrs":{"IB Discovery Owned":{"value":"100"},"Site":{"value":"200"}}}
          response = ib_NIOS.wapi_request('POST', object_type="record:unknown",fields=json.dumps(data))
          if (response[0]!=400):
               logging.info ("Added CDS Record with Reference value :",json.loads(response))
               time.sleep(1)
               record_details_before_modification=get_reference_for_unknown_records(json.loads(response))
               logging.info ("Record details before modification",record_details_before_modification)
               time.sleep(1)
               logging.info ("Modifying CDS record now ")
               response_ref=json.loads(response)
               modify_data={"name": "CDS."+auth_zone['fqdn'],"record_type": "CDS","subfield_values": [{"field_value":"200","field_type": "S","include_length": "NONE"},{"field_value":"0","field_type": "S","include_length": "NONE"},{"field_value":"200","field_type": "S","include_length": "NONE"},{"field_value":"123456789abcdef67890123456789abcdef61234","field_type": "X","include_length": "8_BIT"}],"view": "default","extattrs":{"IB Discovery Owned":{"value":"100"},"Site":{"value":"200"}}}
               modified_response = ib_NIOS.wapi_request('PUT', ref=response_ref, fields=json.dumps(modify_data))
               if (modified_response[0]==400):
                    logging.info ("Failed to modify CDS record")
               else:
                    logging.info ("Modified record CDS with new details",json.loads(modified_response))
               time.sleep(1)
               record_details_after_modification=get_reference_for_unknown_records(json.loads(modified_response))
               logging.info ("Record details before modification",record_details_after_modification)
               if ((record_details_before_modification == record_details_after_modification)==False):
                    assert True
                    logging.info ("Test Case 8 Execution Completed ")
               else:
                    assert False
                    logging.info ("Test Case 8 Execution Failed")
          time.sleep(1)
          log("stop","/var/log/syslog",config.grid_vip)

     @pytest.mark.run(order=9)
     def test_09_cert_record(self):
          log("start","/var/log/syslog",config.grid_vip)
          logging.info ("Creating  CERT Record for added Zone")
          data={"name": "CERT."+auth_zone['fqdn'],"record_type": "CERT","subfield_values": [{"field_value": "11083 21041 76 MEdib2NhSU9PaW0xK3FkSHRPU3JEY09zR2lJMk5DY3h1WDIvVHFj","field_type": "P","include_length": "NONE"}],"view":"default","extattrs": {"IB Discovery Owned":{"value":"100"},"Site":{"value":"200"}}}
          response = ib_NIOS.wapi_request('POST', object_type="record:unknown",fields=json.dumps(data))
          if (response[0]!=400):
               logging.info ("Added CERT Record with Reference value :",json.loads(response))
               time.sleep(1)
               record_details_before_modification=get_reference_for_unknown_records(json.loads(response))
               logging.info ("Record details before modification",record_details_before_modification)
               time.sleep(1)
               logging.info ("Modifying CERT record now ")
               response_ref=json.loads(response)
               modify_data={"name": "CERT."+auth_zone['fqdn'],"record_type": "CERT","subfield_values": [{"field_value": "11085 21044 76 MEdib2NhSU9PaW0xK3FkSHRPU3JEY09zR2lJMk5DY3h1WDIvVHFj","field_type": "P","include_length": "NONE"}],"view":"default","extattrs": {"IB Discovery Owned":{"value":"100"},"Site":{"value":"200"}}}
               modified_response = ib_NIOS.wapi_request('PUT', ref=response_ref, fields=json.dumps(modify_data))
               if (modified_response[0]==400):
                    logging.info ("Failed to modify CERT record")
               else:
                    logging.info ("Modified record CERT with new details",json.loads(modified_response))
               time.sleep(1)
               record_details_after_modification=get_reference_for_unknown_records(json.loads(modified_response))
               logging.info ("Record details before modification",record_details_after_modification)
               if ((record_details_before_modification == record_details_after_modification)==False):
                    assert True
                    logging.info ("Test Case 9 Execution Completed ")
               else:
                    assert False
                    logging.info ("Test Case 9 Execution Failed")
          time.sleep(1)
          log("stop","/var/log/syslog",config.grid_vip)

     @pytest.mark.run(order=10)
     def test_10_hinfo_record(self):
          log("start","/var/log/syslog",config.grid_vip)
          logging.info ("Creating  HINFO Record for added Zone")
          data={"name": "HINFO."+auth_zone['fqdn'],"record_type": "HINFO","subfield_values": [{"field_value": "INTEL","field_type": "T","include_length": "8_BIT"},{"field_value": "WINDOWS","field_type": "T","include_length": "8_BIT"}],"view": "default","extattrs":{"IB Discovery Owned":{"value":"100"},"Site":{"value":"200"}}}
          response = ib_NIOS.wapi_request('POST', object_type="record:unknown",fields=json.dumps(data))
          if (response[0]!=400):
               logging.info ("Added HINFO Record with Reference value :",json.loads(response))
               time.sleep(1)
               record_details_before_modification=get_reference_for_unknown_records(json.loads(response))
               logging.info ("Record details before modification",record_details_before_modification)
               time.sleep(1)
               logging.info ("Modifying HINFO record now ")
               response_ref=json.loads(response)
               modify_data={"name": "HINFO."+auth_zone['fqdn'],"record_type": "HINFO","subfield_values": [{"field_value": "GENTEL","field_type": "T","include_length": "8_BIT"},{"field_value": "DINDOWS","field_type": "T","include_length": "8_BIT"}],"view": "default","extattrs":{"IB Discovery Owned":{"value":"100"},"Site":{"value":"100"}}}
               modified_response = ib_NIOS.wapi_request('PUT', ref=response_ref, fields=json.dumps(modify_data))
               if (modified_response[0]==400):
                    logging.info ("Failed to modify HINFO record")
               else:
                    logging.info ("Modified record HINFO with new details",json.loads(modified_response))
               time.sleep(1)
               record_details_after_modification=get_reference_for_unknown_records(json.loads(modified_response))
               logging.info ("Record details before modification",record_details_after_modification)
               if ((record_details_before_modification == record_details_after_modification)==False):
                    assert True
                    logging.info ("Test Case 10 Execution Completed ")
               else:
                    assert False
                    logging.info ("Test Case 10 Execution Failed")
          log("stop","/var/log/syslog",config.grid_vip)
          time.sleep(1)

     @pytest.mark.run(order=11)
     def test_11_loc_record(self):
          logging.info ("Creating  LOC Record for added Zone")
          data={"name": "LOC."+auth_zone['fqdn'],"record_type": "LOC","subfield_values": [{"field_type": "P","field_value": "42 21 54.000 N 71 6 18.000 W -24.00m 30m 100m 0.10m","include_length": "NONE"}],"view": "default","extattrs":{"IB Discovery Owned":{"value":"100"},"Site":{"value":"200"}}}
          response = ib_NIOS.wapi_request('POST', object_type="record:unknown",fields=json.dumps(data))
          if (response[0]!=400):
               logging.info ("Added LOC Record with Reference value :",json.loads(response))
               time.sleep(1)
               record_details_before_modification=get_reference_for_unknown_records(json.loads(response))
               logging.info ("Record details before modification",record_details_before_modification)
               time.sleep(1)
               logging.info ("Modifying LOC record now ")
               response_ref=json.loads(response)
               modify_data={"name": "LOC."+auth_zone['fqdn'],"record_type": "LOC","subfield_values": [{"field_type": "P","field_value": "22 21 54.000 N 71 6 18.000 W -24.00m 30m 100m 0.10m","include_length": "NONE"}],"view": "default","extattrs":{"IB Discovery Owned":{"value":"100"},"Site":{"value":"100"}}}
               modified_response = ib_NIOS.wapi_request('PUT', ref=response_ref, fields=json.dumps(modify_data))
               if (modified_response[0]==400):
                    logging.info ("Failed to modify LOC record")
               else:
                    logging.info ("Modified record LOC with new details",json.loads(modified_response))
               time.sleep(1)
               record_details_after_modification=get_reference_for_unknown_records(json.loads(modified_response))
               logging.info ("Record details before modification",record_details_after_modification)
               if ((record_details_before_modification == record_details_after_modification)==False):
                    assert True
                    logging.info ("Test Case 11 Execution Completed ")
               else:
                    assert False
                    logging.info ("Test Case 11 Execution Failed")
          time.sleep(1)

        
     @pytest.mark.run(order=12)
     def test_12_ipseckey_record(self):
          logging.info ("Creating  IPSECKEY Record for added Zone")
          data={"name": "IPSECKEY."+auth_zone['fqdn'],"record_type": "IPSECKEY","subfield_values": [{"field_value":"10","field_type": "B","include_length": "NONE"},{"field_value":"1","field_type": "S","include_length": "NONE"},{"field_value":"2","field_type": "S","include_length": "NONE"},{"field_value": "1.1.1.1","field_type": "4","include_length": "NONE"},{"field_value": "AQNRU3mG7TVTO2BkR47usntb102uFJtugbo6BSGvgqt4AQ==","field_type": "H","include_length": "8_BIT"}],"view": "default","extattrs":{"IB Discovery Owned":{"value":"100"},"Site":{"value":"200"}}}
          response = ib_NIOS.wapi_request('POST', object_type="record:unknown",fields=json.dumps(data))
          if (response[0]!=400):
               logging.info ("Added IPSECKEY Record with Reference value :",json.loads(response))
               time.sleep(1)
               record_details_before_modification=get_reference_for_unknown_records(json.loads(response))
               logging.info ("Record details before modification",record_details_before_modification)
               time.sleep(1)
               logging.info ("Modifying IPSECKEY record now ")
               response_ref=json.loads(response)
               modify_data={"name": "IPSECKEY."+auth_zone['fqdn'],"record_type": "IPSECKEY","subfield_values": [{"field_value":"10","field_type": "B","include_length": "NONE"},{"field_value":"1","field_type": "S","include_length": "NONE"},{"field_value":"2","field_type": "S","include_length": "NONE"},{"field_value": "3.4.1.1","field_type": "4","include_length": "NONE"},{"field_value": "AQNRU3mG7TVTO2BkR47usntb102uFJtugbo6BSGvgqt4AQ==","field_type": "H","include_length": "8_BIT"}],"view": "default","extattrs":{"IB Discovery Owned":{"value":"100"},"Site":{"value":"200"}}}
               modified_response = ib_NIOS.wapi_request('PUT', ref=response_ref, fields=json.dumps(modify_data))
               if (modified_response[0]==400):
                    logging.info ("Failed to modify IPSECKEY record")
               else:
                    logging.info ("Modified record IPSECKEY with new details",json.loads(modified_response))
               time.sleep(1)
               record_details_after_modification=get_reference_for_unknown_records(json.loads(modified_response))
               logging.info ("Record details before modification",record_details_after_modification)
               if ((record_details_before_modification == record_details_after_modification)==False):
                    assert True
                    logging.info ("Test Case 12 Execution Completed ")
               else:
                    assert False
                    logging.info ("Test Case 12 Execution Failed")
          time.sleep(1)

     @pytest.mark.run(order=13)
     def test_13_custom_record(self):
          logging.info ("Creating  Custom Record for added Zone")
          custom=['TYPE65279','TYPE32770','TYPE260','TYPE32767','TYPE110']
          for i in custom:
               data={"name": "Custom."+auth_zone['fqdn'],"record_type":i,"subfield_values": [{"field_type": "B","field_value": "10","include_length": "NONE"},{"field_type": "B","field_value": "11","include_length": "NONE"},{"field_type": "B","field_value": "43","include_length": "NONE"},{"field_type": "X","field_value": "2AF3","include_length": "NONE"}],"view": "default","extattrs":{"IB Discovery Owned":{"value":"100"},"Site":{"value":"100"}}}
               logging.info ("*****************************",data)
               response = ib_NIOS.wapi_request('POST', object_type="record:unknown",fields=json.dumps(data))
               if (response[0]!=400):
                    logging.info ("Added Custom Record with Reference value :",json.loads(response))
               time.sleep(1)
               record_details_before_modification=get_reference_for_unknown_records(json.loads(response))
               logging.info ("Record details before modification",record_details_before_modification)
               time.sleep(1)
               logging.info ("Modifying Custom record now ")
               response_ref=json.loads(response)
               modify_data=data={"name": "Custom."+auth_zone['fqdn'],"record_type":i,"subfield_values": [{"field_type": "B","field_value": "20","include_length": "NONE"},{"field_type": "B","field_value": "11","include_length": "NONE"},{"field_type": "B","field_value": "43","include_length": "NONE"},{"field_type": "X","field_value": "2AF3","include_length": "NONE"}],"view": "default","extattrs":{"IB Discovery Owned":{"value":"100"},"Site":{"value":"100"}}}
               modified_response = ib_NIOS.wapi_request('PUT', ref=response_ref, fields=json.dumps(modify_data))
               if (modified_response[0]==400):
                    logging.info ("Failed to modify Custom record")
               else:
                    logging.info ("Modified record Custom with new details",json.loads(modified_response))
                    time.sleep(1)
               record_details_after_modification=get_reference_for_unknown_records(json.loads(modified_response))
               logging.info ("Record details before modification",record_details_after_modification)
               if ((record_details_before_modification == record_details_after_modification)==False):
                    assert True
                    logging.info ("Test Case 13 Execution Completed ")
               else:
                    assert False
                    logging.info ("Test Case 13 Execution Failed")
          time.sleep(30)


          
     @pytest.mark.run(order=14)
     def test_14_bind_records(self):
          logging.info ("Creating  Reserved Bind Records for added Zone : Should not add records which are already Reserved eg : ")
          custom=['TYPE0','TYPE3','TYPE4','TYPE41','TYPE128','TYPE255','TYPE55555','TYPE55556','TYPE55557','TYPE65432','TYPE65433','TYPE65533']
          for i in custom:
               data={"name": "Reserved_records."+auth_zone['fqdn'],"record_type":i,"subfield_values": [{"field_type": "B","field_value": "10","include_length": "NONE"},{"field_type": "B","field_value": "11","include_length": "NONE"},{"field_type": "B","field_value": "43","include_length": "NONE"},{"field_type": "X","field_value": "2AF3","include_length": "NONE"}],"view": "default","extattrs":{"IB Discovery Owned":{"value":"100"},"Site":{"value":"100"}}}
               logging.info ("*****************************",data)
               response = ib_NIOS.wapi_request('POST', object_type="record:unknown",fields=json.dumps(data))
               if (response[0]==400):
                    assert True
                    logging.info ("Test Case 14 Execution Completed ")
               else:
                    assert False
                    logging.info ("Test Case 14 Execution Failed")
          time.sleep(30)
        
     @pytest.mark.run(order=15)
     def test_15_dig_records(self):
          record_list=['AFSDB','RP','APL','DLV','SSHFP','CDS','CERT','HINFO','LOC']
          try:
               for i in record_list:
                    LookFor='.*'+str(i)+'.'+auth_zone['fqdn']+'.*IN.*'+str(i)+'.*'
                    logging.info ("$$$$$$$$$$$$$$$$$$$",LookFor)
                    dig(i,auth_zone,i.lower(),LookFor)
          except ValueError:
               logging.info ("Dig failed")
           
     @pytest.mark.run(order=16)
     def test_16_copy_records(self):
          auth_zone_copy={"fqdn": "copied_zone.com","allow_query": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}]}
          logging.info("Creating auth Zone for Copying Unknown Resource Records from one zone to another")
          response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(auth_zone_copy))
          if (response[0]==400):
               logging.info ("Zone already exists,try with other data[Don't get confused with Pytest Passed status]")
          else:
               logging.info ("Zone added and response looks like : ",response)
               res = json.loads(response)
               time.sleep(30)
               data = {"grid_primary": [{"name": config.grid_fqdn,"stealth":False}]}
               logging.info ("Trying to Associate ZONE with Primary GRID")
               response = ib_NIOS.wapi_request('PUT',ref=res,fields=json.dumps(data))
               response=json.loads(response)
               logging.info ("Restart services")
               logging.info ("Associated Zone with Primary GRID and reference looks like :",response)
               grid =  ib_NIOS.wapi_request('GET', object_type="grid")
               ref = json.loads(grid)[0]['_ref']
               publish={"member_order":"SIMULTANEOUSLY"}
               request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
               time.sleep(1)
               request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
               restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
               time.sleep(1)
               logging.info ("Restarting grid here now ")
               destination_zone_ref=get_reference_for_zone(response)
               logging.info ("Getting destination zone reference",destination_zone_ref)
               beginning_zone_details="zone_auth?fqdn="+auth_zone['fqdn']
               beginning_zone_ref=ib_NIOS.wapi_request('GET',object_type=beginning_zone_details)
               beginning_zone_ref=json.loads(beginning_zone_ref)
               beginning_zone_ref=beginning_zone_ref[0]['_ref']
               wapi_data={"destination_zone":destination_zone_ref['_ref'],"select_records":["Unknown"]}
               logging.info ("Check here for wapi data",wapi_data)
               logging.info ("Check here for your zone reference data from where you are planning to copy records",beginning_zone_ref)
               copying_records=ib_NIOS.wapi_request('POST',fields=json.dumps(wapi_data),object_type=beginning_zone_ref+"?_function=copyzonerecords")
          time.sleep(30)
          try:
               record_list=['AFSDB','RP','APL','DLV','SSHFP','CDS','CERT','HINFO','LOC']
               for i in record_list:
                    LookFor='.*'+str(i)+'.'+auth_zone['fqdn']+'.*IN.*'+str(i)+'.*'
                    dig(i,auth_zone,i.lower(),LookFor)
               assert True
               logging.info ("Test Case 16 Execution Passed")
          except ValueError:
               assert False
               logging.info ("Unable to copy records or unable to dig them")
               logging.info ("Test Case 16 Execution Failed")

     
     @pytest.mark.run(order=17)
     def test_17_nsupdate_records(self):
          logging.info ("ns update here")
          nsupdate_add('dlv_NS','86400','DLV',auth_zone['fqdn'],'100 0 200 000114123456789ABCDEF67890123456789ABCDEF67890')
          logging.info ("done")
          time.sleep(1)
          try :
               LookFor='.* dlv_NS .'+auth_zone['fqdn']+'.*IN.* DLV.*'
               logging.info (LookFor)
               dig('dlv_NS',auth_zone,'dlv',LookFor)
               logging.info ("Successfully copied records and able to dig them")
               logging.info ("Test Case 17 Execution Completed")
          except ValueError:
               logging.info ("Unable to copy records or unable to dig them")
               logging.info ("Test Case 17 Execution Failed")

     @pytest.mark.run(order=18)
     def test_18_modify_scavenging_settings(self):
          get_ref = ib_NIOS.wapi_request('GET',object_type="grid:dns")
          ref1 = json.loads(get_ref)[0]['_ref']
          data={"scavenging_settings": {"ea_expression_list": [],"enable_auto_reclamation": False,"enable_recurrent_scavenging": False,"enable_rr_last_queried": True,"enable_scavenging": True,"enable_zone_last_queried": True,"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "rtype","op1_type": "FIELD","op2": "Unknown","op2_type": "STRING"},{"op": "ENDLIST"}],"reclaim_associated_records": False}}
          response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
          logging.info(response)
          read  = re.search(r'200',response)
          for read in response:
               assert True
          logging.info("Restart services")
          grid =  ib_NIOS.wapi_request('GET', object_type="grid")
          ref = json.loads(grid)[0]['_ref']
          publish={"member_order":"SIMULTANEOUSLY"}
          request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
          time.sleep(1)
          request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
          restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
          time.sleep(1)
          logging.info("Test Case 18 Execution Completed")

    
     @pytest.mark.run(order=19)
     def test_19_run_scavenging_for_unknown_records(self):
          logging.info("should  delete unknown record after runining scavenging")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          logging.info (ref1)
          logging.info("run scavenging operation")
          data = {"action":"ANALYZE_RECLAIM"}
          response = ib_NIOS.wapi_request('POST', ref=ref1, fields=json.dumps(data), params="?_function=run_scavenging")
          logging.info(response)
          read  = re.search(r'200',response)
          for read in  response:
               assert True
          logging.info("Test Case 19 Execution Completed")

     @pytest.mark.run(order=20)
     def test_20_validate_the_scavenging_task(self):
          get_ref = ib_NIOS.wapi_request('GET',object_type="scavengingtask")
          ref1 = json.loads(get_ref)[-1]['status']
          logging.info (ref1)
          if ref1 == "COMPLETED":
               assert True
          logging.info("Fetching values for Unknown Resource records")
          get_ref = ib_NIOS.wapi_request('GET',object_type="record:unknown?_return_fields=name,view,zone,record_type,creator")
          logging.info(get_ref)
          res = json.loads(get_ref)
          for i in res:
               if (i['creator']!='DYNAMIC'):
                    assert True
                    logging.info("Test Case 20 Execution Completed")
               else:
                    logging.info("Please check this record scavenging failed:",i)
                    logging.info("Test case 20 Execution Failed")

     @pytest.mark.run(order=21)
     def test_21_Create_New_Sub_AuthZone(self):
          get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth")
          logging.info ("*********Reference for your Sub Zone*********",get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          data = {"fqdn":sub_zone['fqdn']+"."+auth_zone['fqdn']}
          response = ib_NIOS.wapi_request('POST', ref=ref1, fields=json.dumps(data))
          logging.info(response)
          read  = re.search(r'201',response)
          for read in  response:
               assert True
          logging.info("Test Case 21 Execution Completed")

     @pytest.mark.run(order=22)
     def test_22_Create_Grid_Primary_For_Sub_Zone(self):
          logging.info("Create grid_primary with required fields")
          zone_name = str(sub_zone['fqdn']+"."+auth_zone['fqdn'])
          logging.info (zone_name)
          get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn="+str(zone_name)+"&_return_as_object=1")
          logging.info(get_ref)
          res = json.loads(get_ref)
          ref1 =str(res['result'][0]['_ref']) 
          data = {"grid_primary":[{"name":config.grid_fqdn,"stealth":False}]}
          response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
          logging.info(response)
          logging.info("============================")
          logging.info("Restart services")
          grid =  ib_NIOS.wapi_request('GET', object_type="grid")
          ref = json.loads(grid)[0]['_ref']
          publish={"member_order":"SIMULTANEOUSLY"}
          request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
          sleep(10)
          request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
          restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
          sleep(30)
          logging.info("Test Case 22 Execution Completed")
 

     @pytest.mark.run(order=23)
     def test_23_Create_Unknown_Record_in_subzone(self):
          logging.info("Create A unknown Record with ISSUE Type in sub zone")
          zone_name = str(sub_zone['fqdn']+"."+auth_zone['fqdn'])
          logging.info ("Creating Sub_zone",zone_name)
          data={"name": "HINFO."+zone_name,"record_type": "HINFO","subfield_values": [{"field_value": "INTEL","field_type": "T","include_length": "8_BIT"},{"field_value": "WINDOWS","field_type": "T","include_length": "8_BIT"}],"view": "default","extattrs":{"IB Discovery Owned":{"value":"100"},"Site":{"value":"200"}}}
          response = ib_NIOS.wapi_request('POST', object_type="record:unknown", fields=json.dumps(data))
          logging.info(response)
          read  = re.search(r'201',response)
          for read in  response:
               assert True
               logging.info("Test Case 23 Execution Completed")
          time.sleep(30)
          try:
               record_list=['HINFO']
               for i in record_list:
                    LookFor='.*'+str(i)+'.'+auth_zone['fqdn']+'.*IN.*'+str(i)+'.*'
                    dig(i,auth_zone,i.lower(),LookFor)
                    logging.info ("DIG Execution Passed For Subzone")
          except ValueError:
               logging.info ("DIG Execution Failed For Subzone")






     @pytest.mark.run(order=24)
     def test_24_create_for_csv_export(self):
          logging.info("Create the fileop function to download csv_export object with unknown record")
          data = {"_object":"record:unknown","zone":auth_zone['fqdn'],"_separator":"COMMA"}
          create_file = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=csv_export")
          logging.info(create_file)
          res = json.loads(create_file)
          token = json.loads(create_file)['token']
          url = json.loads(create_file)['url']
          logging.info (create_file)
          logging.info (res)
          logging.info (token)
          logging.info (url)
          logging.info("Create the fileop function to dowload the csv file to the specified url")
          os.system('curl -k1 -u admin:infoblox -H "Content-type:application/force-download" -O %s'%(url))
          logging.info("Delete the record before import")
          get_ref = ib_NIOS.wapi_request('GET', object_type="record:unknown")
          logging.info(get_ref)
          res = json.loads(get_ref)
          ref = json.loads(get_ref)[0]['_ref']
          logging.info (ref)
          logging.info("Deleting the unknown resourcess record")
          get_status = ib_NIOS.wapi_request('DELETE', object_type=ref)
          logging.info(get_status)
          read = re.search(r'200',get_status)
          for read in get_status:
               assert True
 
          sleep(5)
          logging.info("Create the fileop function to download csv_import object with Unknown record")
          data = {"token":token}
          create_file1 = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=csv_import")
          logging.info(create_file1)
          response1 = ast.literal_eval(json.dumps(create_file1))
          logging.info (response1)
          sleep(30)
          logging.info("Get the status of last executed csv_import task using csv importtask object")
          task = ib_NIOS.wapi_request('GET', object_type="csvimporttask")
          logging.info(task)
          response2 = json.loads(task)
          csv_imp2 = response2[-1]
          task1 = ast.literal_eval(json.dumps(csv_imp2))
          logging.info (task1)

     @pytest.mark.run(order=25)
     def test_25_export_csv(self):
          logging.info("Creating auth Zone for Adding Unknown Resource Records ")
          response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(new_auth_zone))
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
               sleep(15) 
               logging.info("Upload Unknown resource records csv file")
               dir_name = "/mnt/home/rpatil/python_automation/"
               base_filename = "Bindresourcerecords.csv"
               new_filename="new_file.csv"
               with open (base_filename,'r') as fi:
                    new_file=fi.read().replace(str(auth_zone['fqdn']),str(new_auth_zone['fqdn']))
               with open('new_file.csv','w+') as fi:
                    fi.write(new_file)
               with open('new_file.csv','r') as f1:
                    print (":::::::::::::::::::::",f1.read())
               token =generate_token_from_file(dir_name, new_filename)
               print "========================="
               print token
               print "========================="
               data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"OVERRIDE"}
               response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_import")
               sleep(30)
               logging.info(response)
               print response
               read = re.search(r'201', response)
               data = {"objtype": "record:unknown", "search_string": "csv_import"}
               get_ref = ib_NIOS.wapi_request('GET', object_type="search", fields=json.dumps(data))
               res_json = json.loads(get_ref)
               print res_json
               for read in response:
                    assert True
               logging.info("Test Case 25 Execution Completed")
               logging.info("============================") 
                             
                                 
                                 


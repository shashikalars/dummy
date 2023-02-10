"""
 Copyright (c) Infoblox Inc., 2016
 Report Name          : Audit Log
 Report Category      : Audit
 Number of Test cases: 1
 Execution time      : 302.61 seconds
 Execution Group     : Minute Group (MG)
 Description         : Audit log reports will update every 1 min. 

 Author   : Raghavendra MN
 History  : 06/02/2016 (Created)
 Reviewer : Raghavendra MN
"""
import config
import json
import os
import pytest
import pexpect
import re
import sys
import subprocess
from time import sleep
import unittest
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from logger import logger
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results

"""
TEST Steps:
      1.  Input/Preparaiton      : Adding Zones, RR's, UserGroup etc.,
      2.  Search                 : Performing Search operaion with default/custom filter
      3.  Validation             : Comparing Search results against Audit log events. 
"""

class AuditLogEvents(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        logger.info('-'*15+"START:Audit Log Events"+'-'*15)
        logger.info("Preparation for Auditlog Report")
        logger.info("Add SuperUser Group 'audit_group'")
        user_group={"name":"audit_group","superuser": False,"roles":["DNS Admin"],"superuser": False,"access_method":["GUI","API"]}
        ref_user_group = ib_NIOS.wapi_request('POST', object_type="admingroup", fields=json.dumps(user_group))
        logger.info("Add admin 'audit' under 'audit_group'")
        user = {"admin_groups":["audit_group"],"name": "audit","password":"infoblox"}
        ref_user = ib_NIOS.wapi_request('POST', object_type="adminuser", fields=json.dumps(user))

        logger.info("Add zone 'audit.com'")
        data = {"fqdn":"audit.com","view":"default","grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
        ref_admin_zone = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))

        logger.info("Add zone 'audit1.com' from 'audit' user")
        data = {"fqdn":"audit1.com","view":"default","grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
        ref_user_zone = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data),user="audit",password="infoblox")

        logger.info("Add RR's say arecord.audit.com/2.2.2.2'")
        a_record = {"name":"arecord.audit.com","ipv4addr":"2.2.2.2"}
        ref_admin_a = ib_NIOS.wapi_request('POST', object_type="record:a", fields=json.dumps(a_record))

        logger.info("Add RR's say arecord.audit1.com/2.2.2.2' from user 'audit'")
        a_record = {"name":"arecord.audit1.com","ipv4addr":"2.2.2.2"}
        ref_user_a = ib_NIOS.wapi_request('POST', object_type="record:a", fields=json.dumps(a_record),user="audit",password="infoblox")

        logger.info("Modify RR's")
        get_a_record = ib_NIOS.wapi_request('GET', object_type="record:a?name=arecord.audit.com")
        ref_a_record = json.loads(get_a_record)[0]['_ref']
        data_modify = {"name":"arecord_modified.audit.com"}
        response = ib_NIOS.wapi_request('PUT', object_type=ref_a_record,fields=json.dumps(data_modify))

        get_a_record = ib_NIOS.wapi_request('GET', object_type="record:a?name=arecord.audit1.com",user="audit",password="infoblox")
        ref_a_record = json.loads(get_a_record)[0]['_ref']
        data_modify = {"name":"arecord_modified.audit1.com"}
        response = ib_NIOS.wapi_request('PUT', object_type=ref_a_record,fields=json.dumps(data_modify),user="audit",password="infoblox")

        logger.info("Delete Zones") 
        del_zone_audit = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn~=audit.com")
        ref_zone_audit = json.loads(del_zone_audit)[0]['_ref']
        del_status = ib_NIOS.wapi_request('DELETE', object_type = ref_zone_audit)

        del_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn~=audit1.com")
        ref_zone = json.loads(del_zone)[0]['_ref']
        del_status = ib_NIOS.wapi_request('DELETE', object_type = ref_zone,user="audit",password="infoblox")

        logger.info("Delete Add UserGroup and AdminUser")
        del_user = ib_NIOS.wapi_request('GET', object_type="adminuser?name~=audit")
        ref = json.loads(del_user)[0]['_ref']
        del_status = ib_NIOS.wapi_request('DELETE', object_type = ref)

        del_user = ib_NIOS.wapi_request('GET', object_type="admingroup?name~=audit_group")
        ref = json.loads(del_user)[0]['_ref']
        del_status = ib_NIOS.wapi_request('DELETE', object_type = ref)
        
        logger.info("Creating input in json format")
        add_operation =[ \
        {"Admin":"audit","Action":"Created","Object Type":"A Record","Object Name":"arecord.audit1.com","Execution Status":"Normal", \
        "Message":"DnsView=default address=2.2.2.2  address=\"2.2.2.2\",fqdn=\"arecord.audit1.com\"", "Member":config.grid_fqdn }, \
        {"Admin":"admin","Action":"Created","Object Type":"A Record","Object Name":"arecord.audit.com","Execution Status":"Normal", \
        "Message":"DnsView=default address=2.2.2.2  address=\"2.2.2.2\",fqdn=\"arecord.audit.com\"", "Member":config.grid_fqdn },\
        {"Admin":"audit","Action":"Created","Object Type":"Authoritative Zone","Object Name":"audit1.com","Execution Status":"Normal", \
         "Message":"DnsView=default  fqdn=\"audit1.com\",view=DnsView:default,grid_primaries=[[grid_member=Member:"+config.grid_fqdn+",stealth=False]]", \
         "Member":config.grid_fqdn},\
        {"Admin":"admin","Action":"Created","Object Type":"Authoritative Zone","Object Name":"audit.com","Execution Status":"Normal", \
        "Message":"DnsView=default  fqdn=\"audit.com\",view=DnsView:default,grid_primaries=[[grid_member=Member:"+config.grid_fqdn+",stealth=False]]", \
        "Member":config.grid_fqdn }, \
        { "Admin":"admin", "Action":"Created", "Object Type":"Admin Member", "Object Name":"audit", "Execution Status":"Normal",\
        "Message":"groups=[AdminGroup:.audit_group],name=\"audit\",password=\"******\"", "Member":config.grid_fqdn },\
        {"Admin":"admin", "Action":"Created", "Object Type":"Admin Group", "Object Name":"audit_group", "Execution Status":"Normal", \
        "Message":"can_access_cloud_api=False,can_access_gui=True,can_access_papi=True,can_access_taxii=False,name=\"audit_group\",roles=[Role:DNS Admin],superuser=False", "Member":config.grid_fqdn } ]

        modify_operaiton = [ \
	{ "Admin":"audit","Action":"Modified", "Object Type":"A Record", "Object Name":"arecord_modified.audit1.com","Execution Status":"Normal", \
        "Message":"DnsView=default address=2.2.2.2  fqdn:\"arecord.audit1.com\"->\"arecord_modified.audit1.com\"","Member":config.grid_fqdn }, \
        { "Admin":"admin","Action":"Modified", "Object Type":"A Record", "Object Name":"arecord_modified.audit.com", "Execution Status":"Normal", \
        "Message":"DnsView=default address=2.2.2.2  fqdn:\"arecord.audit.com\"->\"arecord_modified.audit.com\"", "Member":config.grid_fqdn }]

        delete_operaiton = [ \
        {  "Admin":"admin", "Action":"Deleted", "Object Type":"Admin Group", "Object Name":"audit_group", "Execution Status":"Normal","Member":config.grid_fqdn}, \
        {  "Admin":"admin", "Action":"Deleted", "Object Type":"Admin Member","Object Name":"audit","Execution Status":"Normal","Member":config.grid_fqdn}, \
        {  "Admin":"audit", "Action":"Deleted", "Object Type":"Authoritative Zone", "Object Name":"audit1.com", "Execution Status":"Normal", \
        "Message":"DnsView=default exclude_subobj=False", "Member":config.grid_fqdn }, \
        {  "Admin":"admin", "Action":"Deleted", "Object Type":"Authoritative Zone", "Object Name":"audit.com", "Execution Status":"Normal", \
         "Message":"DnsView=default exclude_subobj=False", "Member":config.grid_fqdn } ]

        cls.test1 = add_operation +  modify_operaiton + delete_operaiton
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))

        logger.info("Wait for 10 min for report update")
        sleep(600)

    def test_1_audit_log_events_validate_add_modify_delete_events(self):
	logger.info("TestCase:"+sys._getframe().f_code.co_name)
        search_str=r'search sourcetype=ib:audit index=ib_audit | sort -_time | rename TIMESTAMP as "Timestamp", ADMIN as "Admin", ACTION as "Action", MESSAGE as "Message", host as "Member"'
        #search_str=r'search sourcetype=ib:audit index=ib_audit | sort -_time | eval MESSAGE=replace(MESSAGE, "\\\\040", " ") | eval MESSAGE=replace(MESSAGE, "\\\\042", "\"") | eval MESSAGE=replace(MESSAGE, "\\\\054", ",") | eval MESSAGE=replace(MESSAGE, "\\\\072", ":") | eval MESSAGE=replace(MESSAGE, "\\\\075", "=") | eval MESSAGE=replace(MESSAGE, "\\\\076", "&amp;gt;") | eval MESSAGE=replace(MESSAGE, "\\\\133", "\[") | eval MESSAGE=replace(MESSAGE, "\\\\134", "\\")  | eval MESSAGE=replace(MESSAGE, "\\\\135", "\]") | eval OBJECT_NAME=replace(OBJECT_NAME, "\\\\040", " ") | eval OBJECT_NAME=replace(OBJECT_NAME, "\\\\042", "\"") | eval OBJECT_NAME=replace(OBJECT_NAME, "\\\\054", ",")     | eval OBJECT_NAME=replace(OBJECT_NAME, "\\\\072", ":") | eval OBJECT_NAME=replace(OBJECT_NAME, "\\\\075", "=") | eval OBJECT_NAME=replace(OBJECT_NAME, "\\\\076", "&amp;gt;") | eval OBJECT_NAME=replace(OBJECT_NAME, "\\\\133", "\[") | eval OBJECT_NAME=replace(OBJECT_NAME, "\\\\134", "\\") | eval OBJECT_NAME=replace(OBJECT_NAME, "\\\\135", "\]") | rename TIMESTAMP as "Timestamp", ADMIN as "Admin", ACTION as "Action", OBJECT_TYPE as "Object Type", OBJECT_NAME as "Object Name", EXEC_STATUS as "Execution Status", MESSAGE as "Message", host as "Member" | table "Timestamp" "Admin" "Action" "Object Type" "Object Name" "Execution Status" "Message" "Member"'

        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        os.system(cmd)
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test1,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        print(self.test1)
        result = compare_results(self.test1,results_list)
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg

    @classmethod
    def teardown_class(cls):
        logger.info('-'*15+"END:Audit Log Events"+'-'*15)

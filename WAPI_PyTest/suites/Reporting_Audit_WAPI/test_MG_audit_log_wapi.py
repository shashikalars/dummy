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
import logging
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results

class AuditLogWAPIEvents(unittest.TestCase):
    @classmethod
    def setup_class(cls):

        get_ref = ib_NIOS.wapi_request('GET', object_type="grid?_return_fields=audit_log_format")
        logging.info(get_ref)
        ref1=json.loads(get_ref)[0]['_ref']
        data={"audit_log_format":"WAPI_DETAILED"}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))

        logging.info("Creating Super User Group & User")
        group={"name":"superuser123","superuser":True}
        get_ref_group = ib_NIOS.wapi_request('POST',object_type="admingroup", fields=json.dumps(group))
        #res_group = json.loads(get_ref_group)
        user={"name":"manoj","password":"manoj","admin_groups":["superuser123"]}
        get_ref = ib_NIOS.wapi_request('POST',object_type="adminuser", fields=json.dumps(user))
	print("###############USER CREATED################")
	
        logging.info("Creating auth Zone")
	data={"fqdn": "source.com"}
	response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
	print("################AUTH ZONE CREATED##############")	
        
	data = {"grid_primary": [{"name": config.grid_fqdn,"stealth":False}]}
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=source.com")
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
        response=json.loads(response)
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
	print("################RESTART SERVICES DONE##############")

        logging.info("Creating network")
        logging.info("Adding network 20.0.0.0/8")
        print("Adding network 20.0.0.0/8")
	net_obj = {"network": "20.0.0.0/8","network_view": "default"}
	#net_obj = {"members":[{"_struct": "dhcpmember", "ipv4addr":config.ipv4_addr,"name":config.grid_fqdn}], "network": "20.0.0.0/8", "network_view": "default"}
        network1 = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(net_obj))
        print("***************************************",network1)
        logging.info("Adding Range 20.1.0.1 - 20.9.255.255 with lease time 120")
        range_obj = {"start_addr":"20.1.0.1","end_addr":"20.9.255.254","options":[{"_struct": "dhcpoption","name":"dhcp-lease-time","num": 51,"use_option": True,"value": "120","vendor_class": "DHCP"}]}
	#range_obj = {"start_addr":"20.1.0.1","end_addr":"20.9.255.254","member":{"_struct": "dhcpmember","ipv4addr":config.ipv4_addr,"name": config.grid_fqdn}, "options":[{"_struct": "dhcpoption","name":"dhcp-lease-time","num": 51,"use_option": True,"value": "120","vendor_class": "DHCP"}]}
        range = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(range_obj))
        logging.info("Restart DHCP Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        logging.info("Wait for 30 sec.,")
        sleep(60) #wait for 30 sec, for Member Restart
	print("################NETWORK,RANGE CREATED##############")	

        logging.info("Creating input in json format")
	cls.create_network = [{"Admin":"admin","Action":"POST","Object Type":"ReservedRange","Object Name":"20.1.0.1-20.9.255.254","Input Data":"{'start_addr': '20.1.0.1', 'options': [{'num': 51, 'use_option': True, 'value': '120', 'vendor_class': 'DHCP', '_struct': 'dhcpoption', 'name': 'dhcp-lease-time'}], 'end_addr': '20.9.255.254'}"}]
	
	#cls.create_network = [{"Admin":"admin","Action":"POST","Object Type":"IPv4 Network", "Object Name":"10.0.0.0/8", "Execution Status":"Normal"}]
        logging.info(json.dumps(cls.create_network, sort_keys=True, indent=4, separators=(',', ': ')))
	print(json.dumps(cls.create_network, sort_keys=True, indent=4, separators=(',', ': ')))

    @pytest.mark.run(order=1)
    def test_001_audit_log_wapi_validate(self):

        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        print child
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set reporting_user_capabilities enable manoj')
        child.expect('  1. Delete reporting indexed data')
        child.sendline('1')
        sleep(10)
        child.expect('Infoblox >')
        output = child.before
        child.sendline('exit')
        sleep(30)
        print("\nTest Case 01 Executed Successfully")

    @pytest.mark.run(order=2)
    def test_002_audit_log_wapi_validation(self):
        logging.info("TestCase:"+sys._getframe().f_code.co_name) 
	#print("\n\n\n Sleeping for 1000 seconds")
        sleep(5)

	search_str="search sourcetype=ib:audit index=ib_audit SUB_OP=\"*\" | sort -_time | rename TIMESTAMP as \"Timestamp\", ADMIN as \"Admin\", SUB_OP as \"Action\", OBJECT_TYPE as \"Object Type\", OBJECT_NAME as \"Object Name\", EXEC_STATUS as \"Execution Status\", INDATA as \"Input Data\", host as \"Member\", RTIME as \"Response Time\", MESSAGE as \"Message\" | table \"Timestamp\" \"Admin\" \"Action\" \"Response Time\" \"URI\" \"Object Type\" \"Object Name\" \"Input Data\" \"Execution Status\" \"Member\" \"Message\""
	
	#search_str="search sourcetype=ib:audit index=ib_audit SUB_OP=\"*\" | sort -_time | eval INDATA=replace(INDATA, \"\\\\040\", \" \") | eval INDATA=replace(INDATA, \"\\\\042\", \"\\"\") | eval INDATA=replace(INDATA, \"\\\\054\", \",\") | eval INDATA=replace(INDATA, \"\\\\072\", \":\") | eval INDATA=replace(INDATA, \"\\\\075\", \"=\") | eval INDATA=replace(INDATA, \"\\\\076\", \"&amp;gt;\") | eval INDATA=replace(INDATA, \"\\\\133\", \"\[\") | eval INDATA=replace(INDATA, \"\\\\134\", \"\\\")  | eval INDATA=replace(INDATA, \"\\\\135\", \"\]\") | eval OBJECT_NAME=replace(OBJECT_NAME, \"\\\\040\", \" \") | eval OBJECT_NAME=replace(OBJECT_NAME, \"\\\\042\", \"\\"\") | eval OBJECT_NAME=replace(OBJECT_NAME, \"\\\\054\", \",\") | eval OBJECT_NAME=replace(OBJECT_NAME, \"\\\\072\", \":\") | eval OBJECT_NAME=replace(OBJECT_NAME, \"\\\\075\", \"=\") | eval OBJECT_NAME=replace(OBJECT_NAME, \"\\\\076\", \"&amp;gt;\") | eval OBJECT_NAME=replace(OBJECT_NAME, \"\\\\133\", \"\[\") | eval OBJECT_NAME=replace(OBJECT_NAME, \"\\\\134\", \"\\\") | eval OBJECT_NAME=replace(OBJECT_NAME, \"\\\\135\", \"\]\") | eval INDATA=if(INDATA=\"{}\" OR INDATA=\"[]\" OR isnull(INDATA),\"\",INDATA) | rename TIMESTAMP as \"Timestamp\", ADMIN as \"Admin\", SUB_OP as \"Action\", OBJECT_TYPE as \"Object Type\", OBJECT_NAME as \"Object Name\", EXEC_STATUS as \"Execution Status\", INDATA as \"Input Data\", host as \"Member\", RTIME as \"Response Time\", MESSAGE as \"Message\" | sort -_time | table \"Timestamp\" \"Admin\" \"Action\" \"Response Time\" \"URI\" \"Object Type\" \"Object Name\" \"Input Data\" \"Execution Status\" \"Member\" \"Message\""
	
	cmd = config.search_py + " '" + search_str + "' --output_mode=json"
	print("##############################",cmd)
        print(os.system(cmd))

        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        
        try:
            retrived_data=open(config.json_file).read()
            print(retrived_data)
           
        except Exception, e:
            logging.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']

        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.create_network,results_list)
        logging.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logging.info("compare_resutls with 'delta' value as 0")
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%",self.create_network)
        print("-------------------------------------")
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$",results_list)
        result = compare_results(self.create_network,results_list)
        print("#####################################",result)
	if result == 0:
            logging.info("Search validation result: %s (PASS)",result)
        else:
            logging.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg
         
    '''
    @pytest.mark.run(order=7)
    def test_007_Splunk_API_call_with_initial_username_and_password(self):
        logging.info("Splunk rest  API call with initial  username and password")
        import xml.etree.ElementTree as ET
        args = 'curl -k -u manoj:manoj https://' +config.grid_member5_vip +':9185/services/search/jobs/ -d search="search sourcetype=ib:audit index=ib_audit SUB_OP="*" | sort -_time"'
        result= subprocess.check_output(args,stderr=subprocess.PIPE, shell=True)
        if not "sid" in result:
            assert False, "Could not able to connect reporting server"
        data = ET.fromstring(result)
	print("***********",data)
        sid_val = ''
        for child in data:
            if child.tag == 'sid':
                sid_val = child.text
		print("@@@@@@@@@@@@@@",sid_val)
        if not sid_val:
            assert False, "sid value not found"
	
	sleep(5)
	args = 'curl -k -u manoj:manoj https://' +config.grid_member5_vip +':9185/services/search/jobs/' +sid_val +'/results --get -d output_mode=json'
	result= subprocess.check_output(args,stderr=subprocess.PIPE, shell=True)
	#print("------------------ Result ---------------",result)
	output_data = json.loads(result)
	results_list = output_data['results']
	print("#################################################",results_list)
        report_status = False
        for data in results_list:
            if data.get("SUB_OP") == "POST":
                if "source.com" in data.get("_raw"):
                    report_status = True
                    break
            continue
        assert report_status, "source.com not found and repor is not updated"
           
	print("\nTest Case 07 Executed Successfully")	
    ''' 
    @pytest.mark.run(order=8)
    def test_008_clear_data(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="network?network=20.0.0.0/8")
        logging.info(get_ref)
        ref1=json.loads(get_ref)[0]['_ref']
	response = ib_NIOS.wapi_request('DELETE',ref=ref1)
	print(response)
	get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=source.com")
        logging.info(get_ref)
        ref1=json.loads(get_ref)[0]['_ref']
        response = ib_NIOS.wapi_request('DELETE',ref=ref1)
        print(response)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(20)
        print("Restart happened successfully")
	get_ref = ib_NIOS.wapi_request('GET', object_type="adminuser?name=manoj")
        logging.info(get_ref)
        ref1=json.loads(get_ref)[0]['_ref']
        response = ib_NIOS.wapi_request('DELETE',ref=ref1)
        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup?name=superuser123")
        logging.info(get_ref)
        ref1=json.loads(get_ref)[0]['_ref']
        response = ib_NIOS.wapi_request('DELETE',ref=ref1)

	print("\nTest Case 08 Executed Successfully")

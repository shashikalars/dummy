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
import pexpect
import sys
import ib_utils.common_utilities as common_util
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv 

def clean_files(child):
    logging.info('Cleaning created files')
    child.sendline('set collect_perf_data stop')
    child.expect('Infoblox >')
    child.sendline('set collect_perf_data clean')
    child.sendline("y")	
    child.expect('Infoblox >')
    output=child.before
    print(output)
    child.sendline('exit')



class PERF_DATA(unittest.TestCase):

    
    @pytest.mark.run(order=1)
    def test_001_collection_data_dhcp_service_not_running(self):
	logging.info("Validating perf_data command when services are not running")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	child.sendline('set collect_perf_data start dhcpd')
	child.expect('Infoblox >')
	output = child.before
	if ('Please specify the running process to start' in output):
	    logging.info('Services should be running to collect perf data')
	    assert True
	else:
	    logging.info('perf data is collecting data even when services are not running')
	    assert False


    @pytest.mark.run(order=2)
    def test_002_collection_data_dns_service_not_running(self):
	logging.info("Validating perf_data command when services are not running")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	child.sendline('set collect_perf_data start named')
	child.expect('Infoblox >')
	output = child.before
	if ('Please specify the running process to start' in output):
	    logging.info('Services should be running to collect perf data')
	    assert True
	else:
	    logging.info('perf data is collecting data even when services are not running')
	    assert False

    @pytest.mark.run(order=3)
    def test_003_start_dns(self):
	logging.info('Start dns service')
	get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
	logging.info(get_ref)
	res = json.loads(get_ref)
	ref1 = json.loads(get_ref)[0]['_ref']
	data = {"enable_dns": True,"use_mgmt_port":False}
	response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
	sleep(40)
	logging.info(response)
	if response != None:
	    logging.info('DNS service started')
	    assert True
	else:
	    logging.info('DNS service not started')
	    assert False

    @pytest.mark.run(order=4)
    def test_004_Validate_DNS_service_Enabled(self):
        logging.info("Validate DNs Service is enabled")
        get_response = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns")
        logging.info(get_response)
        res = json.loads(get_response)
        logging.info(res)
        for i in res:
            logging.info("found")
            assert i["enable_dns"] == True
        logging.info("Test Case 4 Execution Completed")
   
    @pytest.mark.run(order=5)
    def test_005_start_TP_service(self):
        logging.info("start the TP service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection",grid_vip=config.grid2_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        logging.info (ref1)
        data = {"enable_service": True}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
        sleep(420)
        logging.info(response)
        logging.info("Test Case 5 Execution Completed")
 
    
    @pytest.mark.run(order=6)
    def test_006_Validate_TP_service_running(self):
        logging.info("Validate TP Service is enabled")
        response = ib_NIOS.wapi_request('GET', object_type="member:threatprotection",params="?_return_fields=enable_service",grid_vip=config.grid2_vip)
        logging.info(response)
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        logging.info("Started Threat protection services")

   
    
    @pytest.mark.run(order=7)
    def test_007_start_dhcp(self):
	logging.info('Start dhcp service')
	get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties")
	logging.info(get_ref)
	res = json.loads(get_ref)
	ref1 = json.loads(get_ref)[0]['_ref']
	logging.info("Enable DHCP service")
	data = {"enable_dhcp": True}
	response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
	sleep(40)
	logging.info(response)
	if  response != None:
	    logging.info('DHCP service started')
	    assert True
	else:
	    logging.info('DHCP service not started')
	    assert False

    @pytest.mark.run(order=8)
    def test_008_Validate_DHCP_service_Enabled(self):
        logging.info("Validate DHCP Service is enabled")
        get_response = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties",params="?_return_fields=enable_dhcp")
        logging.info(get_response)
        res = json.loads(get_response)
        logging.info(res)
        for i in res:
            logging.info("found")
            assert i["enable_dhcp"] == True
        logging.info("Test Case 10 Execution Completed")

    @pytest.mark.run(order=9)
    def test_009_Upload_REST_API_Session_Template(self):
        logging.info("Upload REST API Version5 Session Template")
        base_filename="Version5_REST_API_Session_Template.json"
	dir_name = os.getcwd()
        token = common_util.generate_token_from_file(dir_name,base_filename)
        data = {"token": token,"overwrite": True}
        response = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=restapi_template_import",grid_vip=config.grid_master_vip)
        logging.info(response)
        print response
        logging.info(response)
        res = json.loads(response)
        string = {"overall_status": "SUCCESS","error_message": ""}
        if res == string:
            assert True
        else:
            assert False
        print("Test Case 9 Execution Completed")

    @pytest.mark.run(order=10)
    def test_010_Validate_Adding_REST_API_Session_Template(self):
        logging.info("Validating Adding REST API Session Template")
        data = {"name": "Version5_REST_API_Session_Template"}
        get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rest:template",params="?_inheritance=True&_return_fields=name,template_type",grid_vip=config.grid_master_vip)
        logging.info(get_temp)
        res=json.loads(get_temp)
	res = eval(json.dumps(res))
        print(res)
	res = ''.join(map(str, res))
	output = ["'name': 'Version5_REST_API_Session_Template'","'template_type': 'REST_ENDPOINT'"]
	for values in output:
            if values in res:
                assert True
            else:
                assert False
	print(output)
        print("Test Case 10 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=11)
    def test_011_Upload_DNS_Records_Event_Template(self):
        logging.info("Upload DNS RECORDS Version5 Event Template")
        base_filename="Version5_DNS_Zone_and_Records_Action_Template.json"
	dir_name = os.getcwd()
        token = common_util.generate_token_from_file(dir_name,base_filename)
        data = {"token": token,"overwrite":True}
        response = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=restapi_template_import",grid_vip=config.grid_master_vip)
        logging.info(response)
        print response
        logging.info(response)
        res = json.loads(response)
        string = {"overall_status": "SUCCESS","error_message": ""}
        if res == string:
            assert True
        else:
            assert False
        print("Test Case 11 Execution Completed")

    @pytest.mark.run(order=12)
    def test_012_Add_REST_API_endpoint(self):
        logging.info("Add REST API endpoint")
        data = {"name": "rest_api_endpoint1", "uri": "https://"+config.grid_master_vip,"outbound_member_type": "GM","username": "admin","password": "infoblox","wapi_user_name": "admin", "wapi_user_password": "infoblox","template_instance": {"template": "Version5_REST_API_Session_Template"},"server_cert_validation": "NO_VALIDATION","log_level": "DEBUG"}
        response = ib_NIOS.wapi_request('POST', object_type="notification:rest:endpoint", fields=json.dumps(data),grid_vip=config.grid_master_vip)
        res=json.loads(response)
        logging.info(response)
        sleep(10)
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        print("Test Case 12 Execution Completed")

    @pytest.mark.run(order=13)
    def test_013_Validating_REST_API_endpoint(self):
        logging.info("Validating REST API endpoint")
	data = {"name": "rest_api_endpoint1", "uri": "https://"+config.grid_master_vip,"outbound_member_type": "GM","username": "admin","password": "infoblox","wapi_user_name": "admin", "wapi_user_password": "infoblox","template_instance": {"template": "Version5_REST_API_Session_Template"},"server_cert_validation": "NO_VALIDATION","log_level": "DEBUG"}
	get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rest:endpoint",params="?_inheritance=True&_return_fields=name,outbound_member_type,username,wapi_user_name,template_instance,server_cert_validation,log_level",grid_vip=config.grid_master_vip)
        logging.info(get_temp)
        res=json.loads(get_temp)
        res = eval(json.dumps(res))
        print(res)
	res = ''.join(map(str, res))
        output = ["'name': 'rest_api_endpoint1'","'username': 'admin'", "'wapi_user_name': 'admin'", "'log_level': 'DEBUG'", "'name': 'rest_api_endpoint1'","'outbound_member_type': 'GM'", "'server_cert_validation': 'NO_VALIDATION'", "'template_instance': {'parameters': [], 'template': 'Version5_REST_API_Session_Template'"]
        for values in output:
            if values in res:
                assert True
            else:
                assert False
        print(output)
        print("Test Case 13 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=14)
    def test_014_Add_DNS_Zone_Notification_Rule_with_Zone_Type_As_Authoritative(self):
	logging.info("Adding Notification rule with zone type as Authoritative")
        object_type="notification:rest:endpoint"
        data={"name":"rest_api_endpoint1"}
        get_ref = common_util.get_object_reference(object_type,data)
        print "========================="
        print get_ref
        data = {"name": "dns_notify1","notification_action": "RESTAPI_TEMPLATE_INSTANCE", "notification_target": get_ref,"template_instance": {"template": "Version5_DNS_Zone_and_Records_Action_Template"},"event_type": "DB_CHANGE_DNS_ZONE","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "ZONE_TYPE","op1_type": "FIELD","op2": "ZONE_TYPE_AUTHORITATIVE","op2_type": "STRING"},{"op": "ENDLIST"}]}
        response = ib_NIOS.wapi_request('POST', object_type="notification:rule", fields=json.dumps(data),grid_vip=config.grid_master_vip)
        res=json.loads(response)
        logging.info(response)
	sleep(5)
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        print("Test Case 14 Execution Completed")


    @pytest.mark.run(order=15)
    def test_015_Validate_Adding_Notification_Rule_with_zone_type_as_Authoritative(self):
        logging.info("Validating Addition of Notification rule with zone type as Authoritative")
	get_temp = ib_NIOS.wapi_request('GET', object_type="notification:rule",params="?_inheritance=True&_return_fields=name,expression_list,notification_action,notification_target,template_instance",grid_vip=config.grid_master_vip)
        logging.info(get_temp)
        res=json.loads(get_temp)
        res = eval(json.dumps(res))
        print(res)
        res = ''.join(map(str, res))
        output = ["'template_instance': {'parameters': [], 'template': 'Version5_DNS_Zone_and_Records_Action_Template'}", "'expression_list': [{'op1_type': 'LIST', 'op': 'AND'}, {'op2_type': 'STRING', 'op': 'EQ', 'op1_type': 'FIELD', 'op2': 'ZONE_TYPE_AUTHORITATIVE', 'op1': 'ZONE_TYPE'}, {'op': 'ENDLIST'}]","'notification_action': 'RESTAPI_TEMPLATE_INSTANCE'", "'name': 'dns_notify1'"]
        for values in output:
            if values in res:
                assert True
            else:
                assert False
        print(output)
        print("Test Case 15 Execution Completed")
        sleep(30)

    @pytest.mark.run(order=16)
    def test_016_Start_Discovery_Service(self):
        logging.info("Start Discovery Service")
	get_ref = ib_NIOS.wapi_request('GET', object_type="discovery:memberproperties")
        logging.info(get_ref)
        res = json.loads(get_ref)
        res = eval(json.dumps(res)) 
        print(res[1]['_ref'])
        refer=res[1]['_ref']
        print(refer)
        logging.info("start a enable_service")
        data = {"enable_service": True}
        response = ib_NIOS.wapi_request('PUT', ref=refer,fields=json.dumps(data),grid_vip=config.grid_master_vip)
        print response
        logging.info(response)
        read  = re.search(r'200',response)
        for read in  response:
            assert True
	logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish),grid_vip=config.grid_master_vip)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus",grid_vip=config.grid_master_vip)
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",grid_vip=config.grid_master_vip)
        logging.info("System Restart is done successfully")
        print("Test Case 16 Execution Completed")
	sleep(20)

    @pytest.mark.run(order=17)
    def test_017_Validate_Discovery_service_Enabled(self):
        logging.info("Validate Discovery Service is enabled")
	get_ref = ib_NIOS.wapi_request('GET', object_type="discovery:memberproperties",grid_vip=config.grid_master_vip)
        print(get_ref)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[1]['_ref']
        print(ref1)
        get_temp = ib_NIOS.wapi_request('GET',ref=ref1,object_type="discovery:memberproperties",params="?_return_fields=enable_service",grid_vip=config.grid_master_vip)
        print(get_temp)
        result='"enable_service": true'
        if result in get_temp:
            assert True
        else:
            assert False
        print(result)
        print("Test Case 17 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=18)
    def test_018_create_IPv4_network(self):
        logging.info("Create an ipv4 network default network view")
        data = {"network": "10.40.16.0/24","network_view": "default","members":[{"_struct": "dhcpmember","ipv4addr":config.grid_vip}]}
        response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data), grid_vip=config.grid_master_vip)
        print(response)
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        print("Created the ipv4network 10.40.16.0/24 in default view")
        logging.info("Restart DHCP Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_master_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_master_vip)
        print("Test Case 18 Execution Completed")


    @pytest.mark.run(order=19)
    def test_019_Validate_adding_ipv4_DHCP_network(self):
        logging.info("Validate adding ipv4 DHCP network")
        data = {"network": "10.40.16.0/24","network_view": "default"}
	get_temp = ib_NIOS.wapi_request('GET', object_type="network",params="?_inheritance=True&_return_fields=network,network_view",grid_vip=config.grid_master_vip)
        logging.info(get_temp)
        res=json.loads(get_temp)
        res = eval(json.dumps(res))
        res = ''.join(map(str, res))
        print(res)
        data= "'network': '10.40.16.0/24'"
        if data in res:
            assert True
        else:
            assert False
	print(data)
        sleep(20)

    @pytest.mark.run(order=20)
    def test_020_Enable_Discovery_Service(self):
	logging.info ("Enable discovery service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="network",grid_vip=config.grid_master_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        for i in res:
            logging.info("start a enable_service")
            data = {"network":"10.40.16.0/24","use_enable_discovery":True,"discovery_member": config.grid_member1_fqdn,"enable_discovery":True,"enable_immediate_discovery": True}
            response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data),grid_vip=config.grid_master_vip)
            print response
        logging.info(response)
        read  = re.search(r'200',response)
        for read in  response:
            assert True
	print("Test Case 20 Execution Completed")
	sleep(10)



    @pytest.mark.run(order=21)
    def test_021_validate_perf_data_default_values(self):
	logging.info("Validating default values")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	child.sendline('set collect_perf_data start named')
	child.expect('Infoblox >')
	output = child.before
	if ('10 snapshots at an interval of 30 seconds' in output):
	    logging.info('Default values are number of snapshots 10 and interval 30 ')
	    assert True
	else:
	    logging.info('Default value parameters are not met')
	    assert False
	clean_files(child)
        sleep(20)

    @pytest.mark.run(order=22)
    def test_022_validate_perf_data_for_dns(self):
	logging.info("Collecting perf data for DNS service")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	child.sendline('set collect_perf_data start named')
	child.expect('Infoblox >')
	output = child.before
	if ('Performance data collection started for the named' in output):
	    logging.info('Perf data collection for dns has started ')
	    assert True
	else:
	    logging.info('Perf data collection for DNS not started')
	    assert False
	clean_files(child)
    
    @pytest.mark.run(order=23)
    def test_023_validate_perf_data_for_dhcp(self):
	logging.info("Collecting perf data for DHCP service")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	child.sendline('set collect_perf_data start dhcpd')
	child.expect('Infoblox >')
	output = child.before
	if ('Performance data collection started for the dhcpd' in output):
	    logging.info('Perf data collection for DHCP has started ')
	    assert True
	else:
	    logging.info('Perf data collection for DHCP has not started')
	    assert False
	clean_files(child)
        sleep(20)

    @pytest.mark.run(order=24)
    def test_024_validate_perf_data_for_clusterd(self):
	logging.info("Collecting perf data for clusterd service")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	child.sendline('set collect_perf_data start clusterd')
	child.expect('Infoblox >')
	output = child.before
	if ('Performance data collection started for the clusterd' in output):
	    logging.info('Performance data collection started for clusterd with number of snapshots 10 and interval 30 ')
	    assert True
	else:
	    logging.info('Performance data collection not started')
	    assert False
	clean_files(child)

    
    @pytest.mark.run(order=25)
    def test_025_validate_perf_data_for_subscriber_collection(self):
	logging.info("Collecting perf data for subscriber collection service")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	child.sendline('set collect_perf_data start event_subscribe')
	child.expect('Infoblox >')
	output = child.before
	if ('Performance data collection started for the event_subscribe' in output):
	    logging.info('Performance data collection started for subscriber collection with number of snapshots 10 and interval 30 ')
	    assert True
	else:
	    logging.info('Performance data collection not started')
	    assert False
	clean_files(child)
    
    @pytest.mark.run(order=26)
    def test_026_validate_perf_data_for_discovery(self):
	logging.info("Collecting perf data for discovery service")
	child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('pgrep discovery')
        child.expect('#')
        PID=child.before
        PID=re.findall(r'\d+',PID)
        PID=PID[0]
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	child.sendline('set collect_perf_data start'+' '+PID)
	child.expect('Infoblox >')
	output = child.before
	if ('10 snapshots at an interval of 30 seconds' in output):
	    logging.info('Performance data collection started for Discovery service with number of snapshots 10 and interval 30 ')
	    assert True
	else:
	    logging.info('Performance data collection not started')
	    assert False
        clean_files(child)
   	sleep(20)
   
    @pytest.mark.run(order=27)
    def test_027_validate_perf_data_for_fastpath(self):
        logging.info("Collecting perf data for fastpath service")
	child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid2_vip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('pgrep fp*')
        child.expect('#')
        PID=child.before
        PID=re.findall(r'\d+',PID)
        PID=PID[0]
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid2_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	child.sendline('set collect_perf_data start'+' '+PID)
	child.expect('Infoblox >')
	output = child.before
	if ('10 snapshots at an interval of 30 seconds' in output):
	    logging.info('Performance data collection started for Fastpath with number of snapshots 10 and interval 30 ')
	    assert True
	else:
	    logging.info('Performance data collection not started')
	    assert False
        clean_files(child)
   	sleep(20)
 
    @pytest.mark.run(order=28)
    def test_028_validate_perf_data_stop_command_perf_not_running(self):
	logging.info("Validate perf data stop command")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	child.sendline('set collect_perf_data stop')
	child.expect('Infoblox >')
	output = child.before
	if ('Performance data collection not running.') in output:
	    logging.info('Perf Stop commands works when there is already collection running')
	    assert True
	else:
	    logging.info('Perf Stop command not working as expected')
	    assert False
	child.sendline('exit')
	sleep(20)

    @pytest.mark.run(order=29)
    def test_029_validate_perf_data_stop_command_perf_running(self):
	logging.info("Validate perf data stop command")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	child.sendline('set collect_perf_data start named')
	child.expect('Infoblox >')
	child.sendline('set collect_perf_data stop')
	child.expect('Infoblox >')
	output = child.before
	if ('Performance data collection stopped.') in output:
	    logging.info('Perf Stop commands works when there is already collection running')
	    assert True
	else:
	    logging.info('Perf Stop command not working as expected')
	    assert False
	child.sendline('exit')
        sleep(20)
    
    @pytest.mark.run(order=30)
    def test_030_validate_perf_data_clean_command_without_stopping_collection(self):
	logging.info("Validate perf data clean command")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	child.sendline('set collect_perf_data start named')
	child.expect('Infoblox >')
	child.sendline('set collect_perf_data clean')
	child.sendline('y')	
	child.expect('Infoblox >')
	output = child.before
	if ('Performance data collection is running') in output:
	    logging.info('Perf clean commands works when the collection is stopped')
	    assert True
	else:
	    logging.info('Perf clean command not working as expected')
	    assert False
	clean_files(child)

    
    @pytest.mark.run(order=31)
    def test_031_validate_perf_data_clean_command_after_stopping_collection(self):
	logging.info("Validate perf data clean command")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	child.sendline('set collect_perf_data start named')
	child.expect('Infoblox >')
	child.sendline('set collect_perf_data stop')
	child.expect('Infoblox >')
	child.sendline('set collect_perf_data clean')
	child.sendline('y')	
	child.expect('Infoblox >')
	output = child.before
	if ('Cleaning of performance data collection completed.') in output:
	    logging.info('Perf clean commands works when the collection is stopped')
	    assert True
	else:
	    logging.info('Perf clean command not working as expected')
	    assert False
        sleep(20)

    @pytest.mark.run(order=32)
    def test_032_validate_perf_data_for_dns_with_user_data(self):
	logging.info("Collecting perf data for DNS service")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	child.sendline('set collect_perf_data start named number_of_snapshots 10 interval 30')
	child.expect('Infoblox >')
	output = child.before
	if ('10 snapshots at an interval of 30 seconds' in output):
	    logging.info('Perf data collection for dns has started ')
	    assert True
	else:
	    logging.info('Perf data collection for DNS not started')
	    assert False
	clean_files(child)

    
    @pytest.mark.run(order=33)
    def test_033_validate_perf_data_for_dns_with_invalid_user_data(self):
	logging.info("Validating invalid interval values given by user")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	child.sendline('set collect_perf_data start named number_of_snapshots 10 interval 30000')
	child.expect('Infoblox >')
	output = child.before
	if ('interval must be between a minimum of 10 and a maximum of 180 seconds' in output):
	    logging.info('Perf data collection interval values are properly displayed ')
	    assert True
	else:
	    logging.info('Perf data collection interval values doesnot follow proper values')
	    assert False
	child.sendline('exit')

    @pytest.mark.run(order=34)
    def test_034_validate_perf_data_for_dns_with_invalid_user_data(self):
	logging.info("Validating invalid number of snapshot values given by user")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	child.sendline('set collect_perf_data start named number_of_snapshots 10000 interval 30')
	child.expect('Infoblox >')
	output = child.before
	if ('number_of_snapshots must be between a minimum of 10 and a maximum of 3000' in output):
	    logging.info('Perf data collection number of snapshot values are properly displayed ')
	    assert True
	else:
	    logging.info('Perf data collection number of snapshot values doesnot follow proper values')
	    assert False
	child.sendline('exit')
	sleep(20)

    
        
    @pytest.mark.run(order=35)
    def test_035_validate_perf_data_for_dns_check_in_logs_start_complete(self):
	logging.info("Validating perf collection in logs")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	clean_files(child)
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	log("start","/infoblox/var/infoblox.log",config.grid_vip)
	child.sendline('set collect_perf_data start named number_of_snapshots 10 interval 30')
	child.expect('Infoblox >')
	sleep(5)
	log("stop","/infoblox/var/infoblox.log",config.grid_vip)
	startdns ="starting performance data collection for named with iterations: 10 interval: 30"
	startdns=logv(startdns,'/infoblox/var/infoblox.log',config.grid_vip)
	if startdns != None:
	    logging.info(startdns)
	    assert True
	else:
	    logging.info('DNS perf collection is not getting logged in infoblox log')
	    assert False
	clean_files(child)
        sleep(20)

	

    @pytest.mark.run(order=36)
    def test_036_validate_perf_data_for_dns_check_in_logs_stop(self):
	logging.info("Validating perf collection in logs")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	log("start","/infoblox/var/infoblox.log",config.grid_vip)
	child.sendline('set collect_perf_data start named number_of_snapshots 10 interval 30')
	child.expect('Infoblox >')
	child.sendline('set collect_perf_data stop')
	child.expect('Infoblox >')
	sleep(5)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
	stopdns ="Stopping collect perf data"
	stopdns=logv(stopdns,'/infoblox/var/infoblox.log',config.grid_vip)
	if stopdns != None:
	    logging.info(stopdns)
	    assert True
	else:
	    logging.info('DNS perf collection is not getting logged in infoblox log')
	    assert False
	clean_files(child)
        sleep(20)
    
    
    @pytest.mark.run(order=37)
    def test_037_validate_perf_data_for_dns_check_in_logs_complete(self):
	logging.info("Validating perf collection in logs")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	child.sendline('set collect_perf_data start named number_of_snapshots 10 interval 30')
	child.expect('Infoblox >')
	sleep(320)
	log("start","/var/log/syslog",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_vip)
	completedns ="notice performance data collection for named completed successfully."
	completedns=logv(completedns,'/var/log/syslog',config.grid_vip)
	if completedns != None:
	    logging.info(completedns)
	    assert True
	else:
	    logging.info('DNS perf collection is not getting logged in infoblox log')
	    assert False
	clean_files(child)

    
    @pytest.mark.run(order=38)
    def test_038_validate_perf_data_command_collects_10_files(self):
	logging.info("Validating perf collection command collects only 10 files and gives error messages from 11th file")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	for i in range(10):
	    child.sendline('set collect_perf_data start named number_of_snapshots 10 interval 30')
	    child.expect('Infoblox >')
	    sleep(2)
	    child.sendline('set collect_perf_data stop')
	    child.expect('Infoblox >')
	child.sendline('set collect_perf_data start named number_of_snapshots 10 interval 30')
	child.expect('Infoblox >')
	output= child.before
	if 'Performance data collection backup file count has exceeded the maximum limit of 10 files.' in output:
	    logging.info('Performance data collection accepts only 10 files')
	    assert True
	else:
	    logging.info('Performance data collection file maximum limit count is not as expected')
	    assert False
	clean_files(child)
	    
    
    @pytest.mark.run(order=39)
    def test_039_validate_perf_data_command_collected_number_of_snapshots_files(self):
	logging.info("Validating perf collection command collects user entered number of snapshots")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
    	child.sendline('set collect_perf_data start named number_of_snapshots 10 interval 30')
        child.expect('Infoblox >')
	sleep(320)
	child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /storage/cores/')
        child.expect('#')
        child.sendline('ls')
        child.expect('#')
        output = child.before
        output=output.split('\r')
        output=output[1]
        output=output.split('\n')
        output=output[1]
        child.sendline('mkdir data')
        child.expect('#')
        child.sendline('mv' +' '+output+' '+ 'data')
        child.expect('#')
        child.sendline('cd data')
        child.expect('#')
        child.sendline('ls')
        child.expect('#')
        child.sendline('tar -xzvf' +' '+output)
        child.expect('#')
        number=child.sendline('ls | wc -l')
        if number == 11:
            logging.info('Perf collection has collected 10 snapshot as mentioned by user')
            assert True
        else:
            logging.info('Perf collection has not collected 10 snapshot as mentioned by user')
            assert False


    @pytest.mark.run(order=40)
    def test_040_validate_perf_data_default_values_in_maintenancemode(self):
	logging.info("Collecting dhcp perf data in maintenancemode")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set maintenancemode')
        child.expect('Maintenance Mode >')
	child.sendline('set collect_perf_data start dhcpd')
	child.expect('Maintenance Mode >')
	output = child.before
	if ('10 snapshots at an interval of 30 seconds' in output):
	    logging.info('Default values are number of snapshots 10 and interval 30 in maintenancemode')
	    assert True
	else:
	    logging.info('Default value parameters are not met in maintenancemode')
	    assert False
        child.sendline('set collect_perf_data stop')
        child.expect('Maintenance Mode >')
        sleep(20)

    @pytest.mark.run(order=41)
    def test_041_validate_perf_data_dns_in_maintenancemode(self):
        logging.info("Collecting dns perf data in maintenancemode")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set maintenancemode')
        child.expect('Maintenance Mode >')
        child.sendline('set collect_perf_data start named')
        child.expect('Maintenance Mode >')
        output = child.before
        if ('Performance data collection started for the named' in output):
            logging.info('Performance data collection started for named with number of snapshots 10 and interval 30 in maintenancemode')
            assert True
        else:
            logging.info('Performance data collection not worked in maintenancemode')
            assert False
        child.sendline('set collect_perf_data stop')
        child.expect('Maintenance Mode >')


    @pytest.mark.run(order=42)
    def test_042_validate_perf_data_clusterd_in_maintenancemode(self):
        logging.info("Collecting clusterd perf data in maintenancemode")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set maintenancemode')
        child.expect('Maintenance Mode >')
        child.sendline('set collect_perf_data start clusterd')
        child.expect('Maintenance Mode >')
        output = child.before
        if ('Performance data collection started for the clusterd' in output):
            logging.info('Performance data collection started for clusterd with number of snapshots 10 and interval 30 works fine in maintenancemode')
            assert True
        else:
            logging.info('Performance data collection not worked in maintenancemode')
            assert False
        child.sendline('set collect_perf_data stop')
        child.expect('Maintenance Mode >')


    @pytest.mark.run(order=43)
    def test_043_validate_perf_data_stop_in_maintenancemode(self):
        logging.info("Validating stop command of perf data in maintenancemode")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set maintenancemode')
        child.expect('Maintenance Mode >')
        child.sendline('set collect_perf_data start named')
        child.expect('Maintenance Mode >')
        child.sendline('set collect_perf_data stop')
        child.expect('Maintenance Mode >')
        output = child.before
        if ('Performance data collection stopped.' in output):
            logging.info('Perf collection stop command works fine in maintenancemode"')
            assert True
        else:
            logging.info('Perf stop command doesnot work')
            assert False

    @pytest.mark.run(order=44)
    def test_044_validate_perf_data_clean_command_in_maintenancemode(self):
        logging.info("Validating clean command of perf data in maintenancemode")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set maintenancemode')
        child.expect('Maintenance Mode >')
        child.sendline('set collect_perf_data start named')
        child.expect('Maintenance Mode >')
        child.sendline('set collect_perf_data clean')
        child.sendline('y')
        child.expect('Maintenance Mode >')
        output = child.before
        if ('Performance data collection is running. Please stop the process before proceeding with the data clean up' in output):
            logging.info('Perf collection clean command works fine in maintenancemode"')
            assert True
        else:
            logging.info('Perf clean command doesnot work')
            assert False
        sleep(20)

    @pytest.mark.run(order=45)
    def test_045_validate_perf_data_clean_command_in_maintenancemode(self):
        logging.info("Validating clean command of perf data in maintenancemode")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set maintenancemode')
        child.expect('Maintenance Mode >')
        child.sendline('set collect_perf_data start named')
        child.expect('Maintenance Mode >')
        child.sendline('set collect_perf_data stop')
        child.expect('Maintenance Mode >')
        child.sendline('set collect_perf_data clean')
        #child.expect('Do you want to proceed with the clean up? (y or n):')
        child.sendline('y')
        child.expect('Maintenance Mode >')
        output = child.before
        if ('Cleaning of performance data collection completed.' in output):
            logging.info('Perf collection clean command works fine in maintenancemode"')
            assert True
        else:
            logging.info('Perf clean command doesnot work')
            assert False

        
    @pytest.mark.run(order=46)
    def test_046_start_dns_IPv6(self):
	logging.info('Start dns service')
	get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns",grid_vip=config.grid_vip6)
	logging.info(get_ref)
	res = json.loads(get_ref)
	for i in res:
	    ref = i["_ref"]
            logging.info("Enable DNS on v6 interface service")
            data = {"use_lan_ipv6_port":True}
            response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data),grid_vip=config.grid_vip6)
            sleep(20)
	    logging.info("Enable DNS service")
            data = {"enable_dns":True}
	    response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data),grid_vip=config.grid_vip6)
	    sleep(20)
	    logging.info(response)
	    read  = re.search(r'200',response)
	if  response != None:
	    logging.info('DNS service started')
	    assert True
	else:
	    logging.info('DNS service not started')
	    assert False


    @pytest.mark.run(order=47)
    def test_047_start_dhcpv6(self):
	logging.info('Start dhcp service')
 	get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties",grid_vip=config.grid_vip6)
	logging.info(get_ref)
	res = json.loads(get_ref)
	for i in res:
	    ref = i["_ref"]
	    logging.info("Enable DHCP service")
            data = {"enable_dhcpv6_service":True}
	    response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data),grid_vip=config.grid_vip6)
	    sleep(20)
	    logging.info(response)
	read  = re.search(r'200',response)
	if response != None:
	    logging.info('DHCP service started')
	    assert True
	else:
	    logging.info('DHCP service not started')
	    assert False

    @pytest.mark.run(order=48)
    def test_048_Validate_DNS_service_Enabled(self):
        logging.info("Validate DNS Service is enabled")
        get_response = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns",grid_vip=config.grid_vip6)
        logging.info(get_response)
        res = json.loads(get_response)
        logging.info(res)
        for i in res:
            logging.info("found")
            assert i["enable_dns"] == True
        logging.info("Test Case 10 Execution Completed")


    @pytest.mark.run(order=49)
    def test_049_Validate_DHCP_service_Enabled(self):
        logging.info("Validate DHCP Service is enabled")
        get_response = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties",params="?_return_fields=enable_dhcpv6_service",grid_vip=config.grid_vip6)
        logging.info(get_response)
        res = json.loads(get_response)
        logging.info(res)
        for i in res:
            logging.info("found")
            assert i["enable_dhcpv6_service"] == True
        logging.info("Test Case 10 Execution Completed")


    @pytest.mark.run(order=50)
    def test_050_validate_perf_data_IPV6_only_for_dhcp(self):
        logging.info("Validating perf data command for IPV6 only configuration for dhcp service")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip6_1)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set collect_perf_data start dhcpdv6')
        child.expect('Infoblox >')
        output = child.before
	if ('10 snapshots at an interval of 30 seconds' in output):
	    logging.info('Perf data works fine for IPV6 only GRID with number of snapshots 10 and interval 30 ')
	    assert True
	else:
	    logging.info('Perf data doesnot work on IPV6')
	    assert False
	clean_files(child)

    @pytest.mark.run(order=51)
    def test_051_validate_perf_data_IPV6_only_for_dns(self):
        logging.info("Validating perf data command for IPV6 only configuration for dns service")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip6_1)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set collect_perf_data start named')
        child.expect('Infoblox >')
        output = child.before
        if ('10 snapshots at an interval of 30 seconds' in output):
            logging.info('Perf data works fine for IPV6 only GRID with number of snapshots 10 and interval 30 ')
            assert True
        else:
            logging.info('Perf data doesnot work on IPV6')
            assert False
	clean_files(child)


    @pytest.mark.run(order=52)
    def test_052_validate_perf_data_with_PID(self):
        logging.info("Validating perf data command using PID for named")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('pgrep named')
        child.expect('#')
        PID=child.before
        PID=re.findall(r'\d+',PID)
        PID=PID[0]
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set collect_perf_data start'+' '+PID)
        child.expect('Infoblox >')
        output = child.before
        if ('10 snapshots at an interval of 30 seconds' in output):
            logging.info('Perf data works with PID as well for DNS service ')
            assert True
        else:
            logging.info('Perf data not collecting details with PID for DNS service')
            assert False
        child.sendline('exit')

    @pytest.mark.run(order=53)
    def test_053_validate_perf_data_with_PID(self):
        logging.info("Validating perf data command using PID for DHCP")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('pgrep dhcp')
        child.expect('#')
        PID=child.before
        PID=re.findall(r'\d+',PID)
        PID=PID[0]
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	clean_files(child)
	child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set collect_perf_data start'+' '+PID)
        child.expect('Infoblox >')
        output = child.before
        if ('10 snapshots at an interval of 30 seconds' in output):
            logging.info('Perf data works with PID as well for DHCP service ')
            assert True
        else:
            logging.info('Perf data not collecting details with PID for DHCP service')
            assert False
        child.sendline('exit')

   
    @pytest.mark.run(order=54)
    def test_054_validate_perf_data_servie_stop(self):
        logging.info("Validating perf data command when service stops")
	child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('pgrep named')
        child.expect('#')
        PID=child.before
        PID=re.findall(r'\d+',PID)
        PID=PID[0]
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	clean_files(child)
	logging.info('stopping dns service')
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"enable_dns": False}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        sleep(30)
        logging.info("DNS service stopped")
	child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	log("start","/infoblox/var/infoblox.log",config.grid_master_vip)
        child.sendline('set collect_perf_data start'+' '+PID)
        child.expect('Infoblox >')
	log("stop","/infoblox/var/infoblox.log",config.grid_master_vip)
        lookfor="No process found for given PID, exiting"
        lookdns=logv(lookfor,'/infoblox/var/infoblox.log',config.grid_vip)
        if lookdns != None:
            logging.info(lookfor)
            assert True
        else:
            logging.info('DNS perf collection is not getting logged in infoblox log')
            assert False
        clean_files(child)

    
    @pytest.mark.run(order=55)
    def test_055_create_user_group(self):
        logging.info("Create a non-super-user group")
        data={"name":"test1","access_method": ["API","CLI"]}
        response = ib_NIOS.wapi_request('POST',object_type="admingroup",fields=json.dumps(data),grid_vip=config.grid_vip)
        print("#######################",response)
        logging.info(response)
        logging.info("============================")
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Group 'test1' is created")

       

    @pytest.mark.run(order=56)
    def test_056_create_nonsuperuser_user(self):
        logging.info("Create a non-super-user group")
        data = {"name":config.username1,"password":config.password1,"admin_groups": ["test1"]}
        response = ib_NIOS.wapi_request('POST',object_type="adminuser",fields=json.dumps(data))
        print("#######################",response)
        logging.info(response)
        logging.info("============================")
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Admin user 'user' is created")


    @pytest.mark.run(order=57)
    def test_057_validate_perf_data_non_super_user(self):
        logging.info("Validating perf data command doesnot work in non-super user")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no sneha@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set collect_perf_data start named')
        child.expect('Infoblox >')
        output = child.before
        if ('Error: The user does not have sufficient privileges to run this command' in output):
            logging.info('Perf data doesnot work in non-super user as its hidden command as expected ')
            assert True
        else:
            logging.info('Perf data works in non-super user')
            assert False
        child.sendline('exit')

import config
import pytest
import unittest
import logging
import subprocess
import commands
import json
import os
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import re
#import ib_utils.ib_get as ib_get
from time import sleep
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="rfe-5924.log" ,level=logging.DEBUG,filemode='w')
master_vip = config.grid_vip
client_ip = config.client_ip
client_eth1 = config.client_eth1 
client_eth2 = config.client_eth2

class RFE5924_Automation(unittest.TestCase):

    @classmethod
    def setup_class(cls):
        """ setup any state specific to the execution of the given class (which
         usually contains tests).
         """
        logging.info("SETUP METHOD")

	
        grid_dns =  ib_NIOS.wapi_request('GET', object_type="grid:dns")
        global ref
	ref = json.loads(grid_dns)[0]['_ref']
        #print ref
	'''
	data = {"forward_only": True,"forwarders": ["10.39.16.160"]}        
	response = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
        sleep(10)
 	data1 = {"allow_recursive_query":True}
	response = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data1))

        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")

        sleep(60)


 
        # Adding Forward Zone 
        fwd_zone = {"forward_to":[{"address": config.grid2_vip,"name": config.grid2_fqdn}],"fqdn": "zone.com","forwarding_servers": [{"forward_to": [],"forwarders_only": False,"name": config.grid_fqdn,"use_override_forwarders": False}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_forward", fields=json.dumps(fwd_zone))  
        
	# Adding Authoritative Zone
        zone1 = {"fqdn":"zone.com","view":"default","grid_primary": [{"name": config.grid2_fqdn,"stealth": False}]}
        print zone1
        response = ib_NIOS.wapi_request_2('POST', object_type="zone_auth", fields=json.dumps(zone1))
	
	grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request_2('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request_2('POST', object_type = ref + "?_function=restartservices")

        sleep(60)
	# Adding A Records
        record_1 = {"ipv4addr": "4.4.4.1","name": "arec.zone.com"}
        response = ib_NIOS.wapi_request_2('POST', object_type="record:a", fields=json.dumps(record_1))
 
        record_2 = {"ipv4addr": "4.4.4.2","name": "arec.zone.com"}
        response = ib_NIOS.wapi_request_2('POST', object_type="record:a", fields=json.dumps(record_2))

	record_3 = {"ipv4addr": "4.4.4.3","name": "arec.zone.com"}
        response = ib_NIOS.wapi_request_2('POST', object_type="record:a", fields=json.dumps(record_3))

	record_4 = {"ipv4addr": "4.4.4.4","name": "arec.zone.com"}
        response = ib_NIOS.wapi_request_2('POST', object_type="record:a", fields=json.dumps(record_4))

	record_5 = {"ipv4addr": "1.1.1.1","name": "arec.zone.com"}
        response = ib_NIOS.wapi_request_2('POST', object_type="record:a", fields=json.dumps(record_5))

	record_6 = {"ipv4addr": "1.1.1.2","name": "arec.zone.com"}
        response = ib_NIOS.wapi_request_2('POST', object_type="record:a", fields=json.dumps(record_6))

	record_7 = {"ipv4addr": "1.1.1.3","name": "arec.zone.com"}
        response = ib_NIOS.wapi_request_2('POST', object_type="record:a", fields=json.dumps(record_7))

	record_9 = {"ipv4addr": "1.1.1.4","name": "arec.zone.com"}
        response = ib_NIOS.wapi_request_2('POST', object_type="record:a", fields=json.dumps(record_9))
           
         
        #grid_dns =  ib_NIOS.wapi_request('GET', object_type="grid:dns")
        #ref = json.loads(grid_dns)[0]['_ref']
        #print ref
         
        sort_list = { "sortlist": [{"address": "10.34.15.185","match_list": ["1.1.1.4","1.1.1.3","1.1.1.2","1.1.1.1","4.4.4.1","4.4.4.2","4.4.4.3","4.4.4.4"]},{"address": "10.34.15.0/24","match_list": ["4.4.4.1","4.4.4.2","1.1.1.1","1.1.1.2","4.4.4.0/24","1.1.1.0/24"]},{"address": "10.36.200.11/32","match_list": ["4.4.4.1","1111::/64","4.4.4.2","1111::123","4.4.4.3","4.4.4.4","1.1.1.4","1.1.1.3","1.1.1.2","1.1.1.1"]}]}

        response = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(sort_list))    

	grid =  ib_NIOS.wapi_request('GET', object_type="grid")
	ref = json.loads(grid)[0]['_ref']
	request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
	restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")

	sleep(180)        
	'''

    '''
    @pytest.mark.run(order=1)
    def test_1_validated_a_record_responses_query_with_client_ip(self):
        logging.info('-'*30+"Test Case 1 Execution Started"+'-'*30)
        dig_cmd = 'dig @'+str(config.grid_vip)+' arec.zone.com in A -b '+client_eth2+' +short'
        out = commands.getoutput(dig_cmd) 
	input_data=['1.1.1.4', '1.1.1.3', '1.1.1.2', '1.1.1.1', '4.4.4.1', '4.4.4.2', '4.4.4.3', '4.4.4.4']
        ip_data=re.findall(r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})',out)
        ips = []
        for ip in ip_data:
            ips.append(ip)
	print ips
        print type(ips)     
        assert ips == input_data
        logging.info('-'*30+"Test Case 1 Execution Completed"+'-'*30)    
    
    @pytest.mark.run(order=2)
    def test_2_validate_a_record_responses_query_with_client_subnet(self):
        logging.info('-'*30+"Test Case 2 Execution Started"+'-'*30)  
	logging.info("Performing queries from another client with overlapping of IPv4 Network/Address and validate response based on the subnet in sortlist")
#       logging.info("Performing queries from another client, validate response based on the subnet in sortlist")
        input_data=['4.4.4.1', '4.4.4.2', '1.1.1.1', '1.1.1.2']
        dig_cmd = 'dig @'+str(config.grid_vip)+' arec.zone.com in A -b '+client_eth1+' +short'
        out = commands.getoutput(dig_cmd)
        ip_data=re.findall(r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})',out)
        result_ips = []
        for ip in ip_data:
            result_ips.append(ip)
        print result_ips 
	c=len(input_data)
	for i in range(0,c):
	    assert input_data[i] in result_ips
        logging.info('-'*30+"Test Case 2 Execution Completed"+'-'*30) 
    
    @pytest.mark.run(order=3)
    def test_3_validate_a_record_responses_query_with_another_client_ip(self):
        logging.info('-'*30+"Test Case 3 Execution Started"+'-'*30)
	logging.info("Performing queries from another client, validate response based on the subnet in sortlist")
        input_data=['4.4.4.1', '4.4.4.2', '4.4.4.3', '4.4.4.4','1.1.1.4','1.1.1.3','1.1.1.2','1.1.1.1']
        dig_cmd = 'dig @'+str(config.grid_vip)+' arec.zone.com in A -b '+client_ip+' +short'
        out = commands.getoutput(dig_cmd)
        ip_data=re.findall(r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})',out)
        result_ips = []
        for ip in ip_data:
            result_ips.append(ip)
        print result_ips
        c=len(input_data)
        for i in range(0,c):
            assert input_data[i] in result_ips

        logging.info('-'*30+"Test Case 3 Execution Completed"+'-'*30)
    
    @pytest.mark.run(order=4)
    def test_4_enable_fixed_rrset_ordering_validated_a_record_responses_query_with_client_ip(self):
        logging.info('-'*30+"Test Case 4 Execution Started"+'-'*30)
        logging.info("Enable RRSET Ordering in Grid DNS Properties")
	
        data ={"enable_fixed_rrset_order_fqdns": True,"fixed_rrset_order_fqdns": [{"fqdn": "arec.zone.com","record_type": "A"}]} 
        response = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
	grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref_grid = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref_grid + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref_grid + "?_function=restartservices")

        sleep(120)
	dig_cmd = 'dig @'+str(config.grid_vip)+' arec.zone.com in A -b '+client_eth2+' +short'
        out = commands.getoutput(dig_cmd)
	sleep(60)
        ip_data=re.findall(r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})',out)
        ips = []
        for ip in ip_data:
            ips.append(ip)
        print ips

	dig_cmd1 = 'dig @'+str(config.grid_vip)+' arec.zone.com in A -b '+client_eth2+' +short'
        out1 = commands.getoutput(dig_cmd1)
	ip_data1=re.findall(r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})',out1)
        ips1 = []
        for ip1 in ip_data1:
            ips1.append(ip1)
        print ips1
 
	assert ips == ips1

        logging.info('-'*30+"Test Case 4 Execution Started"+'-'*30)   

    
    @pytest.mark.run(order=5)
    def test_5_enable_fixed_RRSET_Ordering_validate_a_record_responses_query_with_client_subnet(self):
        logging.info('-'*30+"Test Case 5 Execution Started"+'-'*30)  
        logging.info("Modify and Validated Threat Protection Rulset- do_not_delete")
	dig_cmd = 'dig @'+str(config.grid_vip)+' arec.zone.com in A -b '+client_eth1+' +short'
        out = commands.getoutput(dig_cmd)
        ip_data=re.findall(r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})',out)
        result_ips = []
        for ip in ip_data:
            result_ips.append(ip)
        print result_ips
	sleep(10)

	dig_cmd1 = 'dig @'+str(config.grid_vip)+' arec.zone.com in A -b '+client_eth1+' +short'
        out1 = commands.getoutput(dig_cmd1)
        ip_data1=re.findall(r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})',out1)
        result_ips1 = []
        for ip1 in ip_data1:
            result_ips1.append(ip1)
        print result_ips1
	assert result_ips == result_ips1
        logging.info('-'*30+"Test Case 5 Execution Completed"+'-'*30)  


    
    @pytest.mark.run(order=6)
    def test_6_enable_fixed_RRSET_Ordering_validate_a_record_responses_query_with_another_client_ip(self):
        logging.info('-'*30+"Test Case 6 Execution Started"+'-'*30)   
	dig_cmd = 'dig @'+str(config.grid_vip)+' arec.zone.com in A -b '+client_ip+' +short'
        out = commands.getoutput(dig_cmd)
        ip_data=re.findall(r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})',out)
        result_ips = []
        for ip in ip_data:
            result_ips.append(ip)
        print result_ips

	dig_cmd1 = 'dig @'+str(config.grid_vip)+' arec.zone.com in A -b '+client_ip+' +short'
        out1 = commands.getoutput(dig_cmd1)
        ip_data1=re.findall(r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})',out1)
        result_ips1 = []
        for ip1 in ip_data1:
            result_ips1.append(ip1)
        print result_ips1
	
        assert result_ips == result_ips1

        logging.info('-'*30+"Test Case 6 Execution Completed"+'-'*30)  
    '''
    
    @pytest.mark.run(order=7)
    def test_7_get_threat_protection_ruleset_modify_validate_do_not_delete(self):
        logging.info('-'*30+"Test Case 7 Execution Started"+'-'*30) 
        logging.info("Modify and Validated Threat Protection Rulset- do_not_delete")
        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ref)
        ref1 = json.loads(get_ref)[1]['_ref']
          
        data={"do_not_delete":False}
        get_status = ib_NIOS.wapi_request('PUT', object_type = ref1,fields=json.dumps(data))

        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ref)
        ref2 = json.loads(get_ref)[1]['_ref']
         
        get_do_not_delete = ib_NIOS.wapi_request('GET', object_type = ref2+'?_return_fields=is_factory_reset_enabled,do_not_delete')
        factory = json.loads(get_do_not_delete)
        logging.info(factory)
        assert factory["do_not_delete"] == False
        logging.info('-'*30+"Test Case 7 Execution Completed"+'-'*30)  

    '''
    @pytest.mark.run(order=8)
    def test_8_get_threat_protection_ruleset_search_version(self):
        logging.info('-'*30+"Test Case 8 Execution Started"+'-'*30)  
	logging.info("Validated Threat Protection Rulset- search object for version")
        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ref)

        version_1 = json.loads(get_ref)[1]['version']
        print version_1
        search_version = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset?version~=%s"%version_1)
        ref_51 = json.loads(search_version)[0]['_ref']

        res = json.loads(search_version)
        for i in res:
            logging.info("found")
            assert i["version"] == version_1
        logging.info('-'*30+"Test Case 8 Execution Completed"+'-'*30)  

    @pytest.mark.run(order=9)
    def test_9_get_threat_protection_ruleset_search_add_type(self):
        logging.info('-'*30+"Test Case 9 Execution Started"+'-'*30)
        logging.info("Validated Threat Protection Rulset- search object for add_type")
        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ref)


        add_type_1 = json.loads(get_ref)[1]['add_type']
        print add_type_1
        search_add_type = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset?add_type=%s"%add_type_1)
        ref_51 = json.loads(search_add_type)[0]['_ref']

        res = json.loads(search_add_type)
        logging.info(res)  
        for i in res:
            logging.info("found")
            assert i["add_type"] == add_type_1
        logging.info('-'*30+"Test Case 9 Execution Completed"+'-'*30) 
 
    @pytest.mark.run(order=10)
    def test_10_get_threat_protection_ruleset_search_add_type(self):
        logging.info('-'*30+"Test Case 10 Execution Started"+'-'*30)
        logging.info("Validated Threat Protection Rulset- search object for add_type")
        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ref)


        add_type_1 = json.loads(get_ref)[1]['add_type']
        print add_type_1
        search_add_type = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset?add_type=%s"%add_type_1)
        ref_51 = json.loads(search_add_type)[0]['_ref']

        res = json.loads(search_add_type)
        for i in res:
            logging.info("found")
            assert i["add_type"] == add_type_1
        logging.info('-'*30+"Test Case 10 Execution Completed"+'-'*30) 


    '''
    @classmethod
    def teardown_class(cls):
        """ teardown any state that was previously setup with a call to
        setup_class.
        """
        logging.info("TEAR DOWN METHOD")   


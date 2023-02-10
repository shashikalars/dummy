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
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="sortlist.log" ,level=logging.DEBUG,filemode='w')
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

	member_dns =  ib_NIOS.wapi_request('GET', object_type="member:dns")
        global member_dns_ref
        member_dns_ref = json.loads(member_dns)[0]['_ref']

	dns_view =  ib_NIOS.wapi_request('GET', object_type="view")
        global dns_view_ref
        dns_view_ref = json.loads(dns_view)[0]['_ref']

	
	        	
	data = {"forward_only": True,"forwarders": ["10.39.16.160"]}        
	response = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
        sleep(10)
 	data1 = {"allow_recursive_query":True}
	response = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data1))

        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref_grid = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref_grid + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref_grid + "?_function=restartservices")

        sleep(60)

        
 
        # Adding Forward Zone 
        fwd_zone = {"forward_to":[{"address": config.grid2_vip,"name": config.grid2_fqdn}],"fqdn": "zone.com","forwarding_servers": [{"forward_to": [],"forwarders_only": False,"name": config.grid_fqdn,"use_override_forwarders": False}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_forward", fields=json.dumps(fwd_zone))  
        
	# Adding Authoritative Zone
        zone1 = {"fqdn":"zone.com","view":"default","grid_primary": [{"name": config.grid2_fqdn,"stealth": False}]}
        print zone1
        response = ib_NIOS.wapi_request_2('POST', object_type="zone_auth", fields=json.dumps(zone1))
	
	grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref_grid = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request_2('POST', object_type = ref_grid + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request_2('POST', object_type = ref_grid + "?_function=restartservices")
	

	grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref_grid = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref_grid + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref_grid + "?_function=restartservices")

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
        print response
	grid =  ib_NIOS.wapi_request('GET', object_type="grid")
	ref_grid = json.loads(grid)[0]['_ref']
	request_restart = ib_NIOS.wapi_request('POST', object_type = ref_grid + "?_function=requestrestartservicestatus")
	restart = ib_NIOS.wapi_request('POST', object_type = ref_grid + "?_function=restartservices")

	sleep(120)        
	

    
    @pytest.mark.run(order=1)
    def test_1_validated_a_record_responses_query_with_client_ip(self):
        logging.info('-'*30+"Test Case 1 Execution Started"+'-'*30)
        dig_cmd = 'dig @'+str(config.grid_vip)+' arec.zone.com in A -b '+client_eth2+' +short +noedns'
        out = commands.getoutput(dig_cmd) 
	input_data=['1.1.1.4', '1.1.1.3', '1.1.1.2', '1.1.1.1', '4.4.4.1', '4.4.4.2', '4.4.4.3', '4.4.4.4']
	logging.info(input_data)
        ip_data=re.findall(r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})',out)
        ips = []
        for ip in ip_data:
            ips.append(ip)
	print ips
        print type(ips)     
	logging.info(ips)
        assert ips == input_data
        logging.info('-'*30+"Test Case 1 Execution Completed"+'-'*30)    
    
    @pytest.mark.run(order=2)
    def test_2_validate_a_record_responses_query_with_client_subnet(self):
        logging.info('-'*30+"Test Case 2 Execution Started"+'-'*30)  
	logging.info("Performing queries from another client with overlapping of IPv4 Network/Address and validate response based on the subnet in sortlist")
#       logging.info("Performing queries from another client, validate response based on the subnet in sortlist")
        input_data=['4.4.4.1', '4.4.4.2', '1.1.1.1', '1.1.1.2']
	logging.info(input_data)
        dig_cmd = 'dig @'+str(config.grid_vip)+' arec.zone.com in A -b '+client_eth1+' +short +noedns'
        out = commands.getoutput(dig_cmd)
        ip_data=re.findall(r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})',out)
        result_ips = []
        for ip in ip_data:
            result_ips.append(ip)
        print result_ips 
	logging.info(result_ips)
	c=len(input_data)
	for i in range(0,c):
	    assert input_data[i] in result_ips
        logging.info('-'*30+"Test Case 2 Execution Completed"+'-'*30) 
    
    @pytest.mark.run(order=3)
    def test_3_validate_a_record_responses_query_with_another_client_ip(self):
        logging.info('-'*30+"Test Case 3 Execution Started"+'-'*30)
	logging.info("Performing queries from another client, validate response based on the subnet in sortlist")
        input_data=['4.4.4.1', '4.4.4.2', '4.4.4.3', '4.4.4.4','1.1.1.4','1.1.1.3','1.1.1.2','1.1.1.1']
	logging.info(input_data)
        dig_cmd = 'dig @'+str(config.grid_vip)+' arec.zone.com in A -b '+client_ip+' +short +noedns'
        out = commands.getoutput(dig_cmd)
	
        ip_data=re.findall(r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})',out)
        result_ips = []
        for ip in ip_data:
            result_ips.append(ip)
        print result_ips
	logging.info(result_ips)
        c=len(input_data)
        for i in range(0,c):
            assert input_data[i] in result_ips

        logging.info('-'*30+"Test Case 3 Execution Completed"+'-'*30)
       
    @pytest.mark.run(order=4)
    def test_4_enable_fixed_rrset_ordering_validated_a_record_responses_query_with_client_ip(self):
        logging.info('-'*30+"Test Case 4 Execution Started"+'-'*30)
        logging.info("Enable RRSET Ordering in Grid DNS Properties")
        print ref
		
        data ={"enable_fixed_rrset_order_fqdns": True,"fixed_rrset_order_fqdns": [{"fqdn": "arec.zone.com","record_type": "A"}]} 
        response = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
	logging.info(response)

	logging.info("Restart Service")
	grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref_grid = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref_grid + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref_grid + "?_function=restartservices")

        sleep(120)
	logging.info("Perform Query for 1st time")
	dig_cmd = 'dig @'+str(config.grid_vip)+' arec.zone.com in A -b '+client_eth2+' +short'
        out = commands.getoutput(dig_cmd)
	logging.info(out)
	sleep(60)
        ip_data=re.findall(r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})',out)
        ips = []
        for ip in ip_data:
            ips.append(ip)
        print ips
	logging.info(ips)
	logging.info("Perform Query for 2nd time")
	dig_cmd1 = 'dig @'+str(config.grid_vip)+' arec.zone.com in A -b '+client_eth2+' +short +noedns'
        out1 = commands.getoutput(dig_cmd1)
	logging.info(out1)
	ip_data1=re.findall(r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})',out1)
        ips1 = []
        for ip1 in ip_data1:
            ips1.append(ip1)
        print ips1
	logging.info(ips1)
 
	assert ips == ips1

        logging.info('-'*30+"Test Case 4 Execution Started"+'-'*30)   
	
    
    @pytest.mark.run(order=5)
    def test_5_enable_fixed_RRSET_Ordering_validate_a_record_responses_query_with_client_subnet(self):
        logging.info('-'*30+"Test Case 5 Execution Started"+'-'*30)  
	sleep(30)
	logging.info("enable_fixed_RRSET_Ordering_validate_a_record_responses_query_with_client_subnet")
	logging.info("Perform Query for the 1st time")
	dig_cmd = 'dig @'+str(config.grid_vip)+' arec.zone.com in A -b '+client_eth1+' +short +noedns'
        out = commands.getoutput(dig_cmd)
	logging.info(out)
        ip_data=re.findall(r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})',out)
        result_ips = []
        for ip in ip_data:
            result_ips.append(ip)
        print result_ips
	logging.info(result_ips)
	sleep(10)
	logging.info("Perform Query for the 2nd time")
	dig_cmd1 = 'dig @'+str(config.grid_vip)+' arec.zone.com in A -b '+client_eth1+' +short +noedns'
        out1 = commands.getoutput(dig_cmd1)
        ip_data1=re.findall(r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})',out1)
        result_ips1 = []
        for ip1 in ip_data1:
            result_ips1.append(ip1)
        print result_ips1
	logging.info(result_ips1)
	assert result_ips == result_ips1
        logging.info('-'*30+"Test Case 5 Execution Completed"+'-'*30)  

    
    
    @pytest.mark.run(order=6)
    def test_6_enable_fixed_RRSET_Ordering_validate_a_record_responses_query_with_another_client_ip(self):
        logging.info('-'*30+"Test Case 6 Execution Started"+'-'*30)   
	logging.info("enable_fixed_RRSET_Ordering_validate_a_record_responses_query_with_another_client_ip")
	logging.info("Perform Query for the first time")
	dig_cmd = 'dig @'+str(config.grid_vip)+' arec.zone.com in A -b '+client_ip+' +short +noedns'
        out = commands.getoutput(dig_cmd)
	logging.info(out)
        ip_data=re.findall(r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})',out)
        result_ips = []
        for ip in ip_data:
            result_ips.append(ip)
        print result_ips
	logging.info(result_ips)
	logging.info("Perform Query for the second time")
	dig_cmd1 = 'dig @'+str(config.grid_vip)+' arec.zone.com in A -b '+client_ip+' +short +noedns'
        out1 = commands.getoutput(dig_cmd1)
	logging.info(out1)
        ip_data1=re.findall(r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})',out1)
        result_ips1 = []
        for ip1 in ip_data1:
            result_ips1.append(ip1)
        print result_ips1
	logging.info(result_ips1)
	
        assert result_ips == result_ips1

        logging.info('-'*30+"Test Case 6 Execution Completed"+'-'*30)  
    
    
    @pytest.mark.run(order=7)
    def test_7_member_level_validated_a_record_responses_query_with_client_ip(self):
        logging.info('-'*30+"Test Case 7 Execution Started"+'-'*30) 
	logging.info("Member level Validated A Record Responses query with Client IP")
	logging.info("Enable Sortlist in View Level")
	sort_list = { "sortlist": [{"address": "10.34.15.185","match_list": ["1.1.1.4","1.1.1.3","1.1.1.2","1.1.1.1","4.4.4.1","4.4.4.2","4.4.4.3","4.4.4.4"]},{"address": "10.34.15.0/24","match_list": ["4.4.4.1","4.4.4.2","1.1.1.1","1.1.1.2","4.4.4.0/24","1.1.1.0/24"]},{"address": "10.36.200.11/32","match_list": ["4.4.4.1","1111::/64","4.4.4.2","1111::123","4.4.4.3","4.4.4.4","1.1.1.4","1.1.1.3","1.1.1.2","1.1.1.1"]}]}
	response = ib_NIOS.wapi_request('PUT', object_type=member_dns_ref, fields=json.dumps(sort_list))
	logging.info("Restart the service")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")

        sleep(180)
	logging.info("Perform Query for the First Time")
	dig_cmd = 'dig @'+str(config.grid_vip)+' arec.zone.com in A -b '+client_eth2+' +short +noedns'
        out = commands.getoutput(dig_cmd)
	logging.info(out)
        input_data=['1.1.1.4', '1.1.1.3', '1.1.1.2', '1.1.1.1', '4.4.4.1', '4.4.4.2', '4.4.4.3', '4.4.4.4']
	logging.info(input_data)
        ip_data=re.findall(r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})',out)
        ips = []
        for ip in ip_data:
            ips.append(ip)
        print ips
        print type(ips)
	logging.info(ips)
        assert ips == input_data
        logging.info('-'*30+"Test Case 7 Execution Completed"+'-'*30)  

    
    @pytest.mark.run(order=8)
    def test_8_member_level_validate_a_record_responses_query_with_client_subnet(self):
        logging.info('-'*30+"Test Case 8 Execution Started"+'-'*30)  
	logging.info("Performing queries from another client with overlapping of IPv4 Network/Address and validate response based on the subnet in sortlist")
        input_data=['4.4.4.1', '4.4.4.2', '1.1.1.1', '1.1.1.2']
	logging.info(input_data)
	logging.info("Perform queries with eth1")
        dig_cmd = 'dig @'+str(config.grid_vip)+' arec.zone.com in A -b '+client_eth1+' +short +noedns'
        out = commands.getoutput(dig_cmd)
	logging.info(out)
        ip_data=re.findall(r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})',out)
        result_ips = []
        for ip in ip_data:
            result_ips.append(ip)
        print result_ips
	logging.info(result_ips)
        c=len(input_data)
        for i in range(0,c):
            assert input_data[i] in result_ips
        logging.info('-'*30+"Test Case 8 Execution Completed"+'-'*30)  
   	
    @pytest.mark.run(order=9)
    def test_9_member_level_validate_a_record_responses_query_with_another_client_ip(self):
        logging.info('-'*30+"Test Case 9 Execution Started"+'-'*30)
        logging.info("Performing queries from another client, validate response based on the subnet in sortlist")
        input_data=['4.4.4.1', '4.4.4.2', '4.4.4.3', '4.4.4.4','1.1.1.4','1.1.1.3','1.1.1.2','1.1.1.1']
	logging.info(input_data)
        dig_cmd = 'dig @'+str(config.grid_vip)+' arec.zone.com in A -b '+client_ip+' +short +noedns'
        out = commands.getoutput(dig_cmd)
	logging.info(out)
        ip_data=re.findall(r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})',out)
        result_ips = []
        for ip in ip_data:
            result_ips.append(ip)
        print result_ips
        c=len(input_data)
	logging.info(result_ips)
        for i in range(0,c):
            assert input_data[i] in result_ips

	logging.info('-'*30+"Test Case 9 Execution Completed"+'-'*30) 
    

    
    @pytest.mark.run(order=10)
    def test_10_view_level_validated_a_record_responses_query_with_client_ip(self):
        logging.info('-'*30+"Test Case 10 Execution Started"+'-'*30)
	logging.info("Configuring Sortlist in  View level")
        sort_list = { "sortlist": [{"address": "10.34.15.185","match_list": ["1.1.1.4","1.1.1.3","1.1.1.2","1.1.1.1","4.4.4.1","4.4.4.2","4.4.4.3","4.4.4.4"]},{"address": "10.34.15.0/24","match_list": ["4.4.4.1","4.4.4.2","1.1.1.1","1.1.1.2","4.4.4.0/24","1.1.1.0/24"]},{"address": "10.36.200.11/32","match_list": ["4.4.4.1","1111::/64","4.4.4.2","1111::123","4.4.4.3","4.4.4.4","1.1.1.4","1.1.1.3","1.1.1.2","1.1.1.1"]}]}
        response = ib_NIOS.wapi_request('PUT', object_type=dns_view_ref, fields=json.dumps(sort_list))
	logging.info(response)
	logging.info("Restart the service")
	grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref_grid_2 = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref_grid_2 + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref_grid_2 + "?_function=restartservices")

        sleep(180)
	logging.info("Perform the query for the first time")
	dig_cmd = 'dig @'+str(config.grid_vip)+' arec.zone.com in A -b '+client_eth2+' +short +noedns'
        out = commands.getoutput(dig_cmd)
        input_data=['1.1.1.4', '1.1.1.3', '1.1.1.2', '1.1.1.1', '4.4.4.1', '4.4.4.2', '4.4.4.3', '4.4.4.4']
	logging.info(input_data)
        ip_data=re.findall(r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})',out)
        ips = []
        for ip in ip_data:
            ips.append(ip)
        print ips
        print type(ips)
	logging.info(ips)
        assert ips == input_data
	logging.info('-'*30+"Test Case 10 Execution Completed"+'-'*30) 
    
    @pytest.mark.run(order=11)
    def test_11_view_level_validated_a_record_responses_query_with_client_subnet(self):
        logging.info('-'*30+"Test Case 11 Execution Started"+'-'*30)
	logging.info("Performing queries from another client with overlapping of IPv4 Network/Address and validate response based on the subnet in sortlist")
#       logging.info("Performing queries from another client, validate response based on the subnet in sortlist")
        input_data=['4.4.4.1', '4.4.4.2', '1.1.1.1', '1.1.1.2']
	logging.info(input_data)
	logging.info("Perform queries")
        dig_cmd = 'dig @'+str(config.grid_vip)+' arec.zone.com in A -b '+client_eth1+' +short +noedns'
        out = commands.getoutput(dig_cmd)
	logging.info(dig_cmd)
        ip_data=re.findall(r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})',out)
        result_ips = []
        for ip in ip_data:
            result_ips.append(ip)
        print result_ips
	logging.info(result_ips)
        c=len(input_data)
        for i in range(0,c):
            assert input_data[i] in result_ips
    	logging.info('-'*30+"Test Case 11 Execution Completed"+'-'*30)

    @pytest.mark.run(order=12)
    def test_12_validate_a_record_responses_query_with_another_client_ip(self):
        logging.info('-'*30+"Test Case 12 Execution Started"+'-'*30)
        logging.info("Performing queries from another client, validate response based on the subnet in sortlist")
	
        input_data=['4.4.4.1', '4.4.4.2', '4.4.4.3', '4.4.4.4','1.1.1.4','1.1.1.3','1.1.1.2','1.1.1.1']
	logging.info(input_data)
	logging.info("Perform query once")
        dig_cmd = 'dig @'+str(config.grid_vip)+' arec.zone.com in A -b '+client_ip+' +short +noedns'
        out = commands.getoutput(dig_cmd)
        ip_data=re.findall(r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})',out)
        result_ips = []
        for ip in ip_data:
            result_ips.append(ip)
        print result_ips
	logging.info(result_ips)
        c=len(input_data)
        for i in range(0,c):
            assert input_data[i] in result_ips

        logging.info('-'*30+"Test Case 12 Execution Completed"+'-'*30)
    	
     
    @classmethod
    def teardown_class(cls):
        """ teardown any state that was previously setup with a call to
        setup_class.
        """
        logging.info("TEAR DOWN METHOD")   


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

class Sortlist_Automation(unittest.TestCase):

    @classmethod
    def setup_class(cls):
        """ setup any state specific to the execution of the given class (which
         usually contains tests).
         """
        logging.info("SETUP METHOD")
	
        grid_dns =  ib_NIOS.wapi_request('GET', object_type="grid:dns")
        global ref_grid_dns
        ref_grid_dns = json.loads(grid_dns)[0]['_ref']
        

	grid_security =  ib_NIOS.wapi_request('GET', object_type="grid:threatprotection")
        global ref_security
	ref_security = json.loads(grid_security)[0]['_ref']
        print ref_security
  
        '''
	data = {"enable_nat_rules": True,"nat_rules": [{"cidr": 16,"nat_ports": [{"block_size": 8,"end_port": 16,"start_port": 1}],"network": "10.36.0.0","rule_type": "NETWORK"},{"address": "10.34.15.199","nat_ports": [{"block_size": 8,"end_port": 24,"start_port": 1}],"rule_type": "ADDRESS"},{"end_address": "10.34.15.189","nat_ports": [{"block_size": 8,"end_port": 24,"start_port": 1}],"rule_type": "RANGE","start_address": "10.34.15.182"}]}
	response = ib_NIOS.wapi_request('PUT', object_type=ref_security, fields=json.dumps(data))

	'''
	data1 = {"forward_only": True,"forwarders": ["10.39.16.160"]}
        response = ib_NIOS.wapi_request('PUT', object_type=ref_grid_dns, fields=json.dumps(data1))
        sleep(10)
        data2 = {"allow_recursive_query":True}
        response = ib_NIOS.wapi_request('PUT', object_type=ref_grid_dns, fields=json.dumps(data2))

        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref_grid = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref_grid + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref_grid + "?_function=restartservices")

        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
       # sleep(120)


	
        
    '''
    @pytest.mark.run(order=1)
    def test_1_perform_query_for_fixedaddress_enabled_nat_in_grid_security_properties(self):
        logging.info('-'*30+"Test Case 1 Execution Started"+'-'*30)
	logging.info("Enabled NAT in Grid Security Properties")
	logging.info("Performing Queries with client as eth1")
        dig_cmd = 'dig @'+str(config.grid_member1_vip)+'  authors.bind A -b 10.34.15.199#14'
        out = commands.getoutput(dig_cmd)
	sleep(15)
	sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " tail -n 25 /var/log/syslog | grep -ir \"authors.*\"" '
        out1 = commands.getoutput(sys_log_validation)
        logging.info(out1)

	print out1
	assert re.search(r'.*src=10.34.15.199.*nat=1 nfpt=9 nlpt=16 fqdn=authors.bind hit_count=1',out1)

        logging.info('-'*30+"Test Case 1 Execution Completed"+'-'*30)    
     
    @pytest.mark.run(order=2)
    def test_2_perform_query_for_range_enabled_nat_in_grid_security_properties(self):
        logging.info('-'*30+"Test Case 2 Execution Started"+'-'*30)  
        logging.info("Enabled NAT in Grid Security Properties")
        logging.info("Performing Queries with client as eth2")
        dig_cmd = 'dig @'+str(config.grid_member1_vip)+'  authors.bind A -b 10.34.15.185#12'
        out = commands.getoutput(dig_cmd)
        sleep(15)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " tail -n 25 /var/log/syslog | grep -ir \"authors.*\"" '
        out1 = commands.getoutput(sys_log_validation)
        logging.info(out1)

        print out1
        assert re.search(r'.*src=10.34.15.185.*nat=1 nfpt=9 nlpt=16 fqdn=authors.bind hit_count=1',out1)


	logging.info('-'*30+"Test Case 2 Execution Completed"+'-'*30) 
     
    @pytest.mark.run(order=3)
    def test_3_perform_query_for_network_enabled_nat_in_grid_security_properties(self):
        logging.info('-'*30+"Test Case 3 Execution Started"+'-'*30)
	logging.info("Enabled NAT in Grid Security Properties")
        
        logging.info("Performing Queries with client as eth0")
        dig_cmd = 'dig @'+str(config.grid_member1_vip)+'  authors.bind A -b 10.36.200.11#12'
        out = commands.getoutput(dig_cmd)
        sleep(15)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " tail -n 25 /var/log/syslog | grep -ir \"authors.*\"" '
        out1 = commands.getoutput(sys_log_validation)
        logging.info(out1)

        print out1
        assert re.search(r'.*src=10.36.200.11.*nat=1 nfpt=9 nlpt=16 fqdn=authors.bind hit_count=1',out1)


        logging.info('-'*30+"Test Case 3 Execution Completed"+'-'*30)
    
    @pytest.mark.run(order=4)
    def test_4_perform_query_with_fixedaddress_enabled_nat_in_grid_security_properties_with_port_number_outside_the_block(self):
        logging.info('-'*30+"Test Case 4 Execution Started"+'-'*30)
	logging.info("Enabled NAT in Grid Security Properties")

        logging.info("Performing Queries with client as eth0")
        dig_cmd = 'dig @'+str(config.grid_member1_vip)+'  authors.bind A -b 10.34.15.199#29'
        out = commands.getoutput(dig_cmd)
        sleep(15)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " tail -n 25 /var/log/syslog | grep -ir \"authors.*\"" '
        out1 = commands.getoutput(sys_log_validation)
        logging.info(out1)

        print out1
        assert re.search(r'.*src=10.34.15.199.*nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1',out1)
        logging.info('-'*30+"Test Case 4 Execution Started"+'-'*30)   
	
    
    @pytest.mark.run(order=5)
    def test_5_perform_query_within_range_enabled_nat_in_grid_security_properties_with_port_number_outside_the_block(self):
        logging.info('-'*30+"Test Case 5 Execution Started"+'-'*30)  
	logging.info("Enabled NAT in Grid Security Properties")

        logging.info("Performing Queries with client as eth0")
        dig_cmd = 'dig @'+str(config.grid_member1_vip)+'  authors.bind A -b 10.34.15.185#29'
        out = commands.getoutput(dig_cmd)
        sleep(15)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " tail -n 25 /var/log/syslog | grep -ir \"authors.*\"" '
        out1 = commands.getoutput(sys_log_validation)
        logging.info(out1)

        print out1
        assert re.search(r'.*src=10.34.15.185.*nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1',out1)

        logging.info('-'*30+"Test Case 5 Execution Completed"+'-'*30)  

    
    
    @pytest.mark.run(order=6)
    def test_6_perform_query_with_network_enabled_nat_in_grid_security_properties_with_port_number_outside_the_block(self):
        logging.info('-'*30+"Test Case 6 Execution Started"+'-'*30)   
	logging.info("Enabled NAT in Grid Security Properties")

        logging.info("Performing Queries with client as eth0")
        dig_cmd = 'dig @'+str(config.grid_member1_vip)+'  authors.bind A -b 10.36.200.11#29'
        out = commands.getoutput(dig_cmd)
        sleep(15)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " tail -n 25 /var/log/syslog | grep -ir \"authors.*\"" '
        out1 = commands.getoutput(sys_log_validation)
        logging.info(out1)

        print out1
        assert re.search(r'.*src=10.36.200.11.*nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1',out1)
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

    ''' 

    @pytest.mark.run(order=1)
    def test_90_add_custom_rule_rate_limited_udp_dns_message_type(self):
        logging.info('-'*30+"Test Case 90 Execution Started"+'-'*30)
        logging.info("Get Member Threat Protection using member:threatprotection object")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[0]['_ref']

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']

        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=130481000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)
        '''
        add_custom_rule={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"PASS","log_severity":"WARNING","params":[{"name":"RECORD_TYPE","value":"A"},{"name": "EVENTS_PER_SECOND","value":"1"},{"name":"RATE_FILTER_COUNT","value":"1"},{"name":"DROP_INTERVAL","value":"5"},{"name":"RATE_ALGORITHM","value":"Rate_Limiting"}]}}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:grid:rule",fields=json.dumps(add_custom_rule))
        logging.info(response)	
        '''
        dig_cmd = 'dig @'+str(config.grid_member1_vip)+'  '
        dig_cmd = 'for i in {1..10};do dig @'+str(config.grid_member1_vip)+' udp3.com A +time=0 +retries=0 -b 10.36.200.11#14;done'
        out = commands.getoutput(dig_cmd)
        sleep(15)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " tail -n 20 /var/log/syslog | grep -ir \"udp3.com.*\"" '
        out1 = commands.getoutput(sys_log_validation)
        logging.info(out1)

        print out1
        assert re.search(r'.*src=10.36.200.11.*nat=1 nfpt=14 nlpt=14.*',out1)	
    
    @classmethod
    def teardown_class(cls):
        """ teardown any state that was previously setup with a call to
        setup_class.
        """
        logging.info("TEAR DOWN METHOD")   


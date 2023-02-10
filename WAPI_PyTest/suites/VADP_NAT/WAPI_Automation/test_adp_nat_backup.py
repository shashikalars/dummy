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
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="adpnat.log" ,level=logging.DEBUG,filemode='w')
master_vip = config.grid_vip
client_ip = config.client_ip
client_eth1 = config.client_eth1 
client_eth2 = config.client_eth2

class adpnat_Automation(unittest.TestCase):

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
	sleep(60)
        '''
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(120)
        '''

    	
    @pytest.mark.run(order=1)
    def test_1_perform_query_for_fixedaddress_without_enabling_nat_in_grid_security_properties(self):
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
        assert re.search(r'.*src=10.34.15.199.*nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1',out1)

        logging.info('-'*30+"Test Case 1 Execution Completed"+'-'*30)        
    
    
    @pytest.mark.run(order=2)
    def test_2_perform_query_for_fixedaddress_enabled_nat_in_grid_security_properties(self):
        logging.info('-'*30+"Test Case 2 Execution Started"+'-'*30)
	logging.info("Enabled NAT in Grid Security Properties")
	datas = {"enable_nat_rules": True,"nat_rules": [{"cidr": 16,"nat_ports": [{"block_size": 8,"end_port": 16,"start_port": 1}],"network": "10.36.0.0","rule_type": "NETWORK"},{"address": "10.34.15.199","nat_ports": [{"block_size": 8,"end_port": 24,"start_port": 1}],"rule_type": "ADDRESS"},{"end_address": "10.34.15.189","nat_ports": [{"block_size": 8,"end_port": 24,"start_port": 1}],"rule_type": "RANGE","start_address": "10.34.15.182"}]}
        response = ib_NIOS.wapi_request('PUT', object_type=ref_security, fields=json.dumps(datas))
       
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref_grid = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref_grid + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref_grid + "?_function=restartservices")

        grid1 =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid1)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(120)

	logging.info("Performing Queries with client as eth1")
        dig_cmd = 'dig @'+str(config.grid_member1_vip)+'  authors.bind A -b 10.34.15.199#14'
        out = commands.getoutput(dig_cmd)
	sleep(15)
	sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " tail -n 25 /var/log/syslog | grep -ir \"authors.*\"" '
        out1 = commands.getoutput(sys_log_validation)
        logging.info(out1)

	print out1
	assert re.search(r'.*src=10.34.15.199.*nat=1 nfpt=9 nlpt=16 fqdn=authors.bind hit_count=1',out1)

        logging.info('-'*30+"Test Case 2 Execution Completed"+'-'*30)    
     
    @pytest.mark.run(order=3)
    def test_3_perform_query_for_range_enabled_nat_in_grid_security_properties(self):
        logging.info('-'*30+"Test Case 3 Execution Started"+'-'*30)  
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


	logging.info('-'*30+"Test Case 3 Execution Completed"+'-'*30) 
     
    @pytest.mark.run(order=4)
    def test_4_perform_query_for_network_enabled_nat_in_grid_security_properties(self):
        logging.info('-'*30+"Test Case 4 Execution Started"+'-'*30)
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


        logging.info('-'*30+"Test Case 4 Execution Completed"+'-'*30)
    
    @pytest.mark.run(order=5)
    def test_5_perform_query_with_fixedaddress_enabled_nat_in_grid_security_properties_with_port_number_outside_the_block(self):
        logging.info('-'*30+"Test Case 5 Execution Started"+'-'*30)
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
        logging.info('-'*30+"Test Case 5 Execution Completed"+'-'*30)   
	
    
    @pytest.mark.run(order=6)
    def test_6_perform_query_within_range_enabled_nat_in_grid_security_properties_with_port_number_outside_the_block(self):
        logging.info('-'*30+"Test Case 6 Execution Started"+'-'*30)  
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

        logging.info('-'*30+"Test Case 6 Execution Completed"+'-'*30)  

    
    
    @pytest.mark.run(order=7)
    def test_7_perform_query_with_network_enabled_nat_in_grid_security_properties_with_port_number_outside_the_block(self):
        logging.info('-'*30+"Test Case 7 Execution Started"+'-'*30)   
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
        logging.info('-'*30+"Test Case 7 Execution Completed"+'-'*30)  
        
        
    @pytest.mark.run(order=8)
    def test_8_perform_query_for_fixedaddress_enabled_nat_in_member_security_properties(self):
        logging.info('-'*30+"Test Case 8 Execution Started"+'-'*30) 

	
        member_security =  ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        global ref_member_security
        ref_member_security = json.loads(member_security)[0]['_ref']
        print ref_member_security


        data12 = {"enable_nat_rules": True,"nat_rules": [{"cidr": 16,"nat_ports": [{"block_size": 8,"end_port": 40,"start_port": 1}],"network": "10.36.0.0","rule_type": "NETWORK"},{"address": "10.34.15.199","nat_ports": [{"block_size": 8,"end_port": 40,"start_port": 1}],"rule_type": "ADDRESS"},{"end_address": "10.34.15.189","nat_ports": [{"block_size": 8,"end_port": 40,"start_port": 1}],"rule_type": "RANGE","start_address": "10.34.15.182"}]}
        response = ib_NIOS.wapi_request('PUT', object_type=ref_member_security, fields=json.dumps(data12))
	grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref_grid = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref_grid + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref_grid + "?_function=restartservices")

        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(120)
	
        logging.info("Performing Queries with client as eth1")
        dig_cmd = 'dig @'+str(config.grid_member1_vip)+'  authors.bind A -b 10.34.15.199#33'
        out = commands.getoutput(dig_cmd)
        sleep(15)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " tail -n 25 /var/log/syslog | grep -ir \"authors.*\"" '
        out1 = commands.getoutput(sys_log_validation)
        logging.info(out1)

        print out1
        assert re.search(r'.*src=10.34.15.199.*nat=1 nfpt=33 nlpt=40 fqdn=authors.bind hit_count=1',out1)

	logging.info('-'*30+"Test Case 8 Execution Completed"+'-'*30)  

     
    @pytest.mark.run(order=9)
    def test_9_perform_query_for_range_enabled_nat_in_member_security_properties(self):
        logging.info('-'*30+"Test Case 9 Execution Started"+'-'*30)  
        logging.info("Enabled NAT in Member Security Properties")
        logging.info("Performing Queries with client as eth2")
        dig_cmd = 'dig @'+str(config.grid_member1_vip)+'  authors.bind A -b 10.34.15.185#33'
        out = commands.getoutput(dig_cmd)
        sleep(15)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " tail -n 25 /var/log/syslog | grep -ir \"authors.*\"" '
        out1 = commands.getoutput(sys_log_validation)
        logging.info(out1)

        print out1
        assert re.search(r'.*src=10.34.15.185.*nat=1 nfpt=33 nlpt=40 fqdn=authors.bind hit_count=1',out1)
	logging.info('-'*30+"Test Case 9 Execution Completed"+'-'*30)  
    	
    @pytest.mark.run(order=10)
    def test_10_perform_query_for_network_enabled_nat_in_member_security_properties(self):
        logging.info('-'*30+"Test Case 10 Execution Started"+'-'*30)
        logging.info("Enabled NAT in Member Security Properties")

        logging.info("Performing Queries with client as eth0")
        dig_cmd = 'dig @'+str(config.grid_member1_vip)+'  authors.bind A -b 10.36.200.11#33'
        out = commands.getoutput(dig_cmd)
        sleep(15)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " tail -n 25 /var/log/syslog | grep -ir \"authors.*\"" '
        out1 = commands.getoutput(sys_log_validation)
        logging.info(out1)

        print out1
        assert re.search(r'.*src=10.36.200.11.*nat=1 nfpt=33 nlpt=40 fqdn=authors.bind hit_count=1',out1)

	logging.info('-'*30+"Test Case 10 Execution Completed"+'-'*30) 
    

    
    @pytest.mark.run(order=11)
    def test_11_perform_query_with_fixedaddress_enabled_nat_in_member_security_properties_with_port_number_outside_the_block(self):
        logging.info('-'*30+"Test Case 11 Execution Started"+'-'*30)
        logging.info("Enabled NAT in Member Security Properties")

        logging.info("Performing Queries with client as eth0")
        dig_cmd = 'dig @'+str(config.grid_member1_vip)+'  authors.bind A -b 10.34.15.199#70'
        out = commands.getoutput(dig_cmd)
        sleep(15)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " tail -n 25 /var/log/syslog | grep -ir \"authors.*\"" '
        out1 = commands.getoutput(sys_log_validation)
        logging.info(out1)

        print out1
        assert re.search(r'.*src=10.34.15.199.*nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1',out1)  	

	logging.info('-'*30+"Test Case 11 Execution Completed"+'-'*30) 
    
    @pytest.mark.run(order=12)
    def test_12_perform_query_within_range_enabled_nat_in_member_security_properties_with_port_number_outside_the_block(self):
        logging.info('-'*30+"Test Case 12 Execution Started"+'-'*30)
    	logging.info("Enabled NAT in Member Security Properties")

        logging.info("Performing Queries with client as eth0")
        dig_cmd = 'dig @'+str(config.grid_member1_vip)+'  authors.bind A -b 10.34.15.185#70'
        out = commands.getoutput(dig_cmd)
        sleep(15)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " tail -n 25 /var/log/syslog | grep -ir \"authors.*\"" '
        out1 = commands.getoutput(sys_log_validation)
        logging.info(out1)

        print out1
        assert re.search(r'.*src=10.34.15.185.*nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1',out1)

	logging.info('-'*30+"Test Case 12 Execution Completed"+'-'*30)
    
    @pytest.mark.run(order=13)
    def test_13_perform_query_within_network_enabled_nat_in_member_security_properties_with_port_number_outside_the_block(self):
        logging.info('-'*30+"Test Case 13 Execution Started"+'-'*30)
	logging.info("Enabled NAT in Member Security Properties")

        logging.info("Performing Queries with client as eth0")
        dig_cmd = 'dig @'+str(config.grid_member1_vip)+'  authors.bind A -b 10.36.200.11#70'
        out = commands.getoutput(dig_cmd)
        sleep(15)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " tail -n 25 /var/log/syslog | grep -ir \"authors.*\"" '
        out1 = commands.getoutput(sys_log_validation)
        logging.info(out1)

        print out1
        assert re.search(r'.*src=10.36.200.11.*nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1',out1)
        logging.info('-'*30+"Test Case 13 Execution Completed"+'-'*30)
    
    @pytest.mark.run(order=14)
    def test_14_validate_cli_conf_file_for_fixed_address(self):
        logging.info('-'*30+"Test Case 14 Execution Started"+'-'*30)
        logging.info("Enabled NAT in Member Security Properties")

	logging.info("Validating Address in cli_conf.txt file")
        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " grep -ir \"10.34.15.182\-10.34.15.189\" /infoblox/var/atp_conf/cli_conf.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        logging.info(out)
        assert re.search(r'10.34.15.182-10.34.15.189',out)
	assert re.search(r'1-40',out)
        logging.info('-'*30+"Test Case 14 Execution Completed"+'-'*30) 

    @pytest.mark.run(order=15)
    def test_15_test_tcp_queries_with_nat_mappings(self):
        logging.info('-'*30+"Test Case 15 Execution Started"+'-'*30)
        logging.info("Perform TCP Queries with NAT enabled")
	dig_cmd = 'dig @'+str(config.grid_member1_vip)+' +time=1 +tcp +retries=0 google.com AFSDB -b 10.36.200.11#11'
        out = commands.getoutput(dig_cmd)
        sleep(15)

        logging.info("Validating CEF logs for TCP Queries")
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " tail -n 25 /var/log/syslog | grep -ir \"google.com.*\"" '
	out = commands.getoutput(sys_log_validation)
        print out
        assert re.search(r'.*src=10.36.200.11.*nat=1 nfpt=9 nlpt=16 fqdn=google.com hit_count=1',out)
        logging.info('-'*30+"Test Case 15 Execution Completed"+'-'*30)

    @classmethod
    def teardown_class(cls):
        """ teardown any state that was previously setup with a call to
        setup_class.
        """
        logging.info("TEAR DOWN METHOD")   


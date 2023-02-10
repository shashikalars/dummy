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
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="adpnat.log" ,level=logging.DEBUG,filemode='w')
master_vip = config.grid_vip
client_ip = config.client_ip
client_eth1 = config.client_eth1 
client_eth2 = config.client_eth2
ref_security=''
class adpnat_automation(unittest.TestCase):

    #@classmethod
    #def setup_class(cls):
    @pytest.mark.run(order=1)
    def test_000_perform_query_for_fixedaddress_without_enabling_nat_in_grid_security_properties(self):

    
        """ setup any state specific to the execution of the given class (which
         usually contains tests).
         """
        print("SETUP METHOD")
	
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

    	
    @pytest.mark.run(order=2)
    def test_001_perform_query_for_fixedaddress_without_enabling_nat_in_grid_security_properties(self):
        print('-'*30+"Test Case 1 Execution Started"+'-'*30)

        print("Performing Queries,without enabling NAT with client as eth1")
        log("start","/var/log/syslog",config.grid_member3_mgmt_vip)
        sleep(10)
        dig_cmd = 'sshpass -p '+config.password+' ssh root@'+config.client_ip+' dig @'+str(config.grid_member1_vip)+'  authors.bind A -b '+config.client_eth1+'#14'
        print(dig_cmd)
        out = commands.getoutput(dig_cmd)
        sleep(10)
        print(out)
        #sleep(15)
        #sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " tail -n 25 /var/log/syslog | grep -ir \"authors.*\"" '
        #out1 = commands.getoutput(sys_log_validation)
        #print(out1)

        #print out1
        #assert re.search(r'.*src='+config.client_eth1+'.*nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1',out1)
        log("stop","/var/log/syslog",config.grid_member3_mgmt_vip)
        lookfor = [".*src="+config.client_eth1+".*nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1"]
        for look in lookfor:
            result = logv(look, '/var/log/syslog', config.grid_member3_mgmt_vip)
            print(result)
            if not result:
                print("Failure: Validate nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1")
                assert False
        print("Success: Validate nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1")
        print('-'*30+"Test Case 1 Execution Completed"+'-'*30)        
    
        
    @pytest.mark.run(order=3)
    def test_002_enabling_nat_in_grid_security_properties_and_validating_range_fixedaddress_in_cli_conf_txtfile(self):
        print('-'*30+"Test Case 2 Execution Started"+'-'*30)
        print("Enabled NAT in Grid Security Properties")
        grid_security =  ib_NIOS.wapi_request('GET', object_type="grid:threatprotection")
        
        ref_security = json.loads(grid_security)[0]['_ref']
        print ref_security
        datas = {"enable_nat_rules": True,"nat_rules": [{"cidr": 16,"nat_ports": [{"block_size": 8,"end_port": 24,"start_port": 1}],"network": "10.38.0.0","rule_type": "NETWORK"},{"address": config.client_eth1,"nat_ports": [{"block_size": 8,"end_port": 24,"start_port": 1}],"rule_type": "ADDRESS"},{"end_address": "10.37.255.254","nat_ports": [{"block_size": 8,"end_port": 24,"start_port": 1}],"rule_type": "RANGE","start_address": "10.37.0.1"}]}
        response = ib_NIOS.wapi_request('PUT', object_type=ref_security, fields=json.dumps(datas))
        print(response)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref_grid = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref_grid + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref_grid + "?_function=restartservices")

        grid1 =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid1)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(120)
        print("Validating Address in cli_conf.txt file")
        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " cat /infoblox/var/atp_conf/cli_conf.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        print(out)
        # assert re.search(r'10.34.15.182-10.34.15.189.*1-24.*8',out)
        # assert re.search(r'10.34.15.199.*1-24.*8',out)
        # assert re.search(r'10.36.0.1-10.36.255.254.*1-24.*8',out)
        assert re.search(config.client_eth1+'-'+config.client_eth1+'.*1-24.*8',out)
        assert re.search(config.client_eth1+'.*1-24.*8',out)
        assert re.search(r'10.37.0.1-10.37.255.254.*1-24.*8',out)
        print('-'*30+"Test Case 2 Execution Completed"+'-'*30)

    @pytest.mark.run(order=4)
    def test_003_perform_query_for_fixedaddress_enabled_nat_in_grid_security_properties(self):
        print('-'*30+"Test Case 3 Execution Started"+'-'*30)
        print("Performing Queries with client as eth1")
        log("start","/var/log/syslog",config.grid_member3_mgmt_vip)
        sleep(10)
        dig_cmd = 'sshpass -p '+config.password+' ssh root@'+config.client_ip+' dig @'+str(config.grid_member1_vip)+'  authors.bind A -b '+config.client_eth1+'#14'
        print(dig_cmd)
        out = commands.getoutput(dig_cmd)
        sleep(15)
        print(out)
       
        #sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " tail -n 25 /var/log/syslog | grep -ir \"authors.*\"" '
        #out1 = commands.getoutput(sys_log_validation)
        #print(out1)

        #print out1
        #assert re.search(r'.*src='+config.client_eth1+'.*nat=1 nfpt=9 nlpt=16 fqdn=authors.bind hit_count=1',out1)
        log("stop","/var/log/syslog",config.grid_member3_mgmt_vip)
        lookfor = [".*src="+config.client_eth1+".*nat=1 nfpt=9 nlpt=16 fqdn=authors.bind hit_count=1"]
        for look in lookfor:
            result = logv(look, '/var/log/syslog', config.grid_member3_mgmt_vip)
            print(result)
            if not result:
                print("Failure: Validate nat=1 nfpt=9 nlpt=16 fqdn=authors.bind hit_count=1")
                assert False
        print("Success: Validate nat=1 nfpt=9 nlpt=16 fqdn=authors.bind hit_count=1")
        print('-'*30+"Test Case 3 Execution Completed"+'-'*30)    
     
    @pytest.mark.run(order=5)
    def test_004_perform_query_for_range_enabled_nat_in_grid_security_properties(self):
        print('-'*30+"Test Case 4 Execution Started"+'-'*30)  
        print("Enabled NAT in Grid Security Properties")
        print("Performing Queries with client as eth2")
        log("start","/var/log/syslog",config.grid_member3_mgmt_vip)
        sleep(10)
        dig_cmd = 'sshpass -p '+config.password+' ssh root@'+config.client_ip+' dig @'+str(config.grid_member1_vip)+'  authors.bind A -b '+config.client_eth1+'#12'
        out = commands.getoutput(dig_cmd)
        sleep(15)
        #sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " tail -n 25 /var/log/syslog | grep -ir \"authors.*\"" '
        #out1 = commands.getoutput(sys_log_validation)
        #print(out1)

        #print out1
        #assert re.search(r'.*src='+config.client_eth1+'.*nat=1 nfpt=9 nlpt=16 fqdn=authors.bind hit_count=1',out1)
        
        log("stop","/var/log/syslog",config.grid_member3_mgmt_vip)
        lookfor = [".*src="+config.client_eth1+".*nat=1 nfpt=9 nlpt=16 fqdn=authors.bind hit_count=1"]
        for look in lookfor:
            result = logv(look, '/var/log/syslog', config.grid_member3_mgmt_vip)
            print(result)
            if not result:
                print("Failure: Validate nat=1 nfpt=9 nlpt=16 fqdn=authors.bind hit_count=1")
                assert False
        print("Success: Validate nat=1 nfpt=9 nlpt=16 fqdn=authors.bind hit_count=1")
        print('-'*30+"Test Case 4 Execution Completed"+'-'*30) 
    
     
    @pytest.mark.run(order=6)
    def test_005_perform_query_for_network_enabled_nat_in_grid_security_properties(self):
        print('-'*30+"Test Case 5 Execution Started"+'-'*30)
        print("Enabled NAT in Grid Security Properties")
        
        print("Performing Queries with client as eth0")
        log("start","/var/log/syslog",config.grid_member3_mgmt_vip)
        sleep(10)
        
        dig_cmd = 'sshpass -p '+config.password+' ssh root@'+config.client_ip+' dig @'+str(config.grid_member1_vip)+'  authors.bind A -b '+config.client_eth1+'#12'
        out = commands.getoutput(dig_cmd)
        sleep(15)
        # sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " tail -n 25 /var/log/syslog | grep -ir \"authors.*\"" '
        # out1 = commands.getoutput(sys_log_validation)
        # print(out1)

        # print out1
        # assert re.search(r'.*src='+config.client_eth1+'.*nat=1 nfpt=9 nlpt=16 fqdn=authors.bind hit_count=1',out1)

        log("stop","/var/log/syslog",config.grid_member3_mgmt_vip)
        lookfor = [".*src="+config.client_eth1+".*nat=1 nfpt=9 nlpt=16 fqdn=authors.bind hit_count=1"]
        for look in lookfor:
            result = logv(look, '/var/log/syslog', config.grid_member3_mgmt_vip)
            print(result)
            if not result:
                print("Failure: Validate nat=1 nfpt=9 nlpt=16 fqdn=authors.bind hit_count=1")
                assert False
        print("Success: Validate nat=1 nfpt=9 nlpt=16 fqdn=authors.bind hit_count=1")
        print('-'*30+"Test Case 5 Execution Completed"+'-'*30)
    
    @pytest.mark.run(order=7)
    def test_006_performing_query_with_fixedaddress_enabled_nat_in_grid_security_properties_with_port_number_outside_the_block(self):
        print('-'*30+"Test Case 6 Execution Started"+'-'*30)
        print("Enabled NAT in Grid Security Properties")

        print("Performing Queries with client as eth0")
        log("start","/var/log/syslog",config.grid_member3_mgmt_vip)
        sleep(10)
        dig_cmd = 'sshpass -p '+config.password+' ssh root@'+config.client_ip+' dig @'+str(config.grid_member1_vip)+'  authors.bind A -b '+config.client_eth1+'#29'
        out = commands.getoutput(dig_cmd)
        sleep(15)
        # sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " tail -n 25 /var/log/syslog | grep -ir \"authors.*\"" '
        # out1 = commands.getoutput(sys_log_validation)
        # print("Validating nat=0,source and fqdn from logs ")  
        # print(out1)
       
        # print out1
        # assert re.search(r'.*src='+config.client_eth1+'.*nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1',out1)
        
        log("stop","/var/log/syslog",config.grid_member3_mgmt_vip)
        lookfor = [".*src="+config.client_eth1+".*nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1"]
        for look in lookfor:
            result = logv(look, '/var/log/syslog', config.grid_member3_mgmt_vip)
            print(result)
            if not result:
                print("Failure: Validate nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1")
                assert False
        print("Success: Validate nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1")
        print('-'*30+"Test Case 6 Execution Completed"+'-'*30)   
	
    
    @pytest.mark.run(order=8)
    def test_007_perform_query_within_range_enabled_nat_in_grid_security_properties_with_port_number_outside_the_block(self):
        print('-'*30+"Test Case 7 Execution Started"+'-'*30)  
        print("Enabled NAT in Grid Security Properties")

        print("Performing Queries with client as eth0")
        log("start","/var/log/syslog",config.grid_member3_mgmt_vip)
        sleep(10)
        dig_cmd = 'sshpass -p '+config.password+' ssh root@'+config.client_ip+' dig @'+str(config.grid_member1_vip)+'  authors.bind A -b '+config.client_eth1+'#29'
        out = commands.getoutput(dig_cmd)
        sleep(15)
        # sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " tail -n 25 /var/log/syslog | grep -ir \"authors.*\"" '
        # out1 = commands.getoutput(sys_log_validation)
        # print(out1)

        # print out1
        # assert re.search(r'.*src='+config.client_eth1+'.*nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1',out1)
        log("stop","/var/log/syslog",config.grid_member3_mgmt_vip)
        lookfor = [".*src="+config.client_eth1+".*nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1"]
        for look in lookfor:
            result = logv(look, '/var/log/syslog', config.grid_member3_mgmt_vip)
            print(result)
            if not result:
                print("Failure: Validate nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1")
                assert False
        print("Success: Validate nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1")
        print('-'*30+"Test Case 7 Execution Completed"+'-'*30)  

    
    
    @pytest.mark.run(order=9)
    def test_008_perform_query_with_network_enabled_nat_in_grid_security_properties_with_port_number_outside_the_block(self):
        print('-'*30+"Test Case 8 Execution Started"+'-'*30)   
        print("Enabled NAT in Grid Security Properties")

        print("Performing Queries with client as eth0")
        log("start","/var/log/syslog",config.grid_member3_mgmt_vip)
        sleep(10)
        dig_cmd = 'sshpass -p '+config.password+' ssh root@'+config.client_ip+' dig @'+str(config.grid_member1_vip)+'  authors.bind A -b '+config.client_eth1+'#29'
        out = commands.getoutput(dig_cmd)
        sleep(15)
        # sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " tail -n 25 /var/log/syslog | grep -ir \"authors.*\"" '
        # out1 = commands.getoutput(sys_log_validation)
        # print(out1)

        # print out1
        # assert re.search(r'.*src='+config.client_eth1+'.*nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1',out1)
        
        log("stop","/var/log/syslog",config.grid_member3_mgmt_vip)
        lookfor = [".*src="+config.client_eth1+".*nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1"]
        for look in lookfor:
            result = logv(look, '/var/log/syslog', config.grid_member3_mgmt_vip)
            print(result)
            if not result:
                print("Failure: Validate nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1")
                assert False
        print("Success: Validate nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1")
        print('-'*30+"Test Case 8 Execution Completed"+'-'*30)  
        
       
    @pytest.mark.run(order=10)
    def test_009_enabling_nat_in_member_security_properties_and_validating_cli_conf_txt_file(self):
        print('-'*30+"Test Case 9 Execution Started"+'-'*30) 
        member_security =  ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        global ref_member_security
        ref_member_security = json.loads(member_security)[0]['_ref']
        print ref_member_security

        
        
        #data12 = {"enable_nat_rules": True,"nat_rules": [{"cidr": 16,"nat_ports": [{"block_size": 8,"end_port": 40,"start_port": 1}],"network": "10.36.0.0","rule_type": "NETWORK"},{"address": "10.34.15.199","nat_ports": [{"block_size": 8,"end_port": 40,"start_port": 1}],"rule_type": "ADDRESS"},{"end_address": "10.34.15.189","nat_ports": [{"block_size": 8,"end_port": 40,"start_port": 1}],"rule_type": "RANGE","start_address": "10.34.15.182"}]}
        data12 = {"enable_nat_rules": True,"nat_rules": [{"cidr": 16,"nat_ports": [{"block_size": 8,"end_port": 40,"start_port": 1}],"network": "10.38.0.0","rule_type": "NETWORK"},{"address": config.client_eth1,"nat_ports": [{"block_size": 8,"end_port": 40,"start_port": 1}],"rule_type": "ADDRESS"},{"end_address": "10.37.255.254","nat_ports": [{"block_size": 8,"end_port": 40,"start_port": 1}],"rule_type": "RANGE","start_address": "10.37.0.1"}]}
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
        print("Validating Address in cli_conf.txt file")
        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " cat /infoblox/var/atp_conf/cli_conf.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        print(out)
        # assert re.search(r'10.34.15.182-10.34.15.189.*1-40.*8',out)
        # assert re.search(r'10.34.15.199.*1-40.*8',out)
        # assert re.search(r'10.36.0.1-10.36.255.254.*1-40.*8',out)
        
        assert re.search(config.client_eth1+'-'+config.client_eth1+'.*1-40.*8',out)
        assert re.search(config.client_eth1+'.*1-40.*8',out)
        assert re.search(r'10.37.0.1-10.37.255.254.*1-40.*8',out)     
        print('-'*30+"Test Case 9 Execution Completed"+'-'*30)

    @pytest.mark.run(order=11)
    def test_010_perform_query_for_fixedaddress_enabled_nat_in_member_security_properties(self):
        print('-'*30+"Test Case 10 Execution Started"+'-'*30)
        print("Performing Queries with client as eth1")
        log("start","/var/log/syslog",config.grid_member3_mgmt_vip)
        sleep(10)
        dig_cmd = 'sshpass -p '+config.password+' ssh root@'+config.client_ip+' dig @'+str(config.grid_member1_vip)+'  authors.bind A -b '+config.client_eth1+'#33'
        out = commands.getoutput(dig_cmd)
        sleep(15)
        # sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " tail -n 25 /var/log/syslog | grep -ir \"authors.*\"" '
        # out1 = commands.getoutput(sys_log_validation)
        # print(out1)

        # print out1
        # assert re.search(r'.*src='+config.client_eth1+'.*nat=1 nfpt=33 nlpt=40 fqdn=authors.bind hit_count=1',out1)
        log("stop","/var/log/syslog",config.grid_member3_mgmt_vip)
        lookfor = [".*src="+config.client_eth1+".*nat=1 nfpt=33 nlpt=40 fqdn=authors.bind hit_count=1"]
        for look in lookfor:
            result = logv(look, '/var/log/syslog', config.grid_member3_mgmt_vip)
            print(result)
            if not result:
                print("Failure: Validate nat=1 nfpt=33 nlpt=40 fqdn=authors.bind hit_count=1")
                assert False
        print("Success: Validate nat=1 nfpt=33 nlpt=40 fqdn=authors.bind hit_count=1")
        print('-'*30+"Test Case 10 Execution Completed"+'-'*30)  

         
    @pytest.mark.run(order=12)
    def test_011_perform_query_for_range_enabled_nat_in_member_security_properties(self):
        print('-'*30+"Test Case 11 Execution Started"+'-'*30)  
        print("Enabled NAT in Member Security Properties")
        print("Performing Queries with client as eth2")
        log("start","/var/log/syslog",config.grid_member3_mgmt_vip)
        sleep(10)
        dig_cmd = 'sshpass -p '+config.password+' ssh root@'+config.client_ip+' dig @'+str(config.grid_member1_vip)+'  authors.bind A -b '+config.client_eth1+'#33'
        out = commands.getoutput(dig_cmd)
        sleep(15)
        # sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " tail -n 25 /var/log/syslog | grep -ir \"authors.*\"" '
        # out1 = commands.getoutput(sys_log_validation)
        # print(out1)

        # print out1
        # assert re.search(r'.*src='+config.client_eth1+'.*nat=1 nfpt=33 nlpt=40 fqdn=authors.bind hit_count=1',out1)
        log("stop","/var/log/syslog",config.grid_member3_mgmt_vip)
        lookfor = [".*src="+config.client_eth1+".*nat=1 nfpt=33 nlpt=40 fqdn=authors.bind hit_count=1"]
        for look in lookfor:
            result = logv(look, '/var/log/syslog', config.grid_member3_mgmt_vip)
            print(result)
            if not result:
                print("Failure: Validate nat=1 nfpt=33 nlpt=40 fqdn=authors.bind hit_count=1")
                assert False
        print("Success: Validate nat=1 nfpt=33 nlpt=40 fqdn=authors.bind hit_count=1")
        print('-'*30+"Test Case 11 Execution Completed"+'-'*30)  
    	
    @pytest.mark.run(order=13)
    def test_012_perform_query_for_network_enabled_nat_in_member_security_properties(self):
        print('-'*30+"Test Case 12 Execution Started"+'-'*30)
        print("Enabled NAT in Member Security Properties")

        print("Performing Queries with client as eth0")
        log("start","/var/log/syslog",config.grid_member3_mgmt_vip)
        sleep(10)
        dig_cmd = 'sshpass -p '+config.password+' ssh root@'+config.client_ip+' dig @'+str(config.grid_member1_vip)+'  authors.bind A -b '+config.client_eth1+'#33'
        out = commands.getoutput(dig_cmd)
        sleep(15)
        # sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " tail -n 25 /var/log/syslog | grep -ir \"authors.*\"" '
        # out1 = commands.getoutput(sys_log_validation)
        # print(out1)

        # print out1
        # assert re.search(r'.*src='+config.client_eth1+'.*nat=1 nfpt=33 nlpt=40 fqdn=authors.bind hit_count=1',out1)
        log("stop","/var/log/syslog",config.grid_member3_mgmt_vip)
        lookfor = [".*src="+config.client_eth1+".*nat=1 nfpt=33 nlpt=40 fqdn=authors.bind hit_count=1"]
        for look in lookfor:
            result = logv(look, '/var/log/syslog', config.grid_member3_mgmt_vip)
            print(result)
            if not result:
                print("Failure: Validate nat=1 nfpt=33 nlpt=40 fqdn=authors.bind hit_count=1")
                assert False
        print("Success: Validate nat=1 nfpt=33 nlpt=40 fqdn=authors.bind hit_count=1")
        print('-'*30+"Test Case 12 Execution Completed"+'-'*30) 
    

    
    @pytest.mark.run(order=14)
    def test_013_perform_query_with_fixedaddress_enabled_nat_in_member_security_properties_with_port_number_outside_the_block(self):
        print('-'*30+"Test Case 13 Execution Started"+'-'*30)
        print("Enabled NAT in Member Security Properties")

        print("Performing Queries with client as eth0")
        log("start","/var/log/syslog",config.grid_member3_mgmt_vip)
        sleep(10)
        dig_cmd = 'sshpass -p '+config.password+' ssh root@'+config.client_ip+' dig @'+str(config.grid_member1_vip)+'  authors.bind A -b '+config.client_eth1+'#70'
        out = commands.getoutput(dig_cmd)
        sleep(15)
        # sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " tail -n 25 /var/log/syslog | grep -ir \"authors.*\"" '
        # out1 = commands.getoutput(sys_log_validation)
        # print(out1)

        # print out1
        # assert re.search(r'.*src='+config.client_eth1+'.*nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1',out1)  	
        log("stop","/var/log/syslog",config.grid_member3_mgmt_vip)
        lookfor = [".*src="+config.client_eth1+".*nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1"]
        for look in lookfor:
            result = logv(look, '/var/log/syslog', config.grid_member3_mgmt_vip)
            print(result)
            if not result:
                print("Failure: Validate nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1")
                assert False
        print("Success: Validate nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1")
        print('-'*30+"Test Case 13 Execution Completed"+'-'*30) 
    
    @pytest.mark.run(order=15)
    def test_014_perform_query_within_range_enabled_nat_in_member_security_properties_with_port_number_outside_the_block(self):
        print('-'*30+"Test Case 14 Execution Started"+'-'*30)
    	print("Enabled NAT in Member Security Properties")

        print("Performing Queries with client as eth0")
        log("start","/var/log/syslog",config.grid_member3_mgmt_vip)
        sleep(10)
        dig_cmd = 'sshpass -p '+config.password+' ssh root@'+config.client_ip+' dig @'+str(config.grid_member1_vip)+'  authors.bind A -b '+config.client_eth1+'#70'
        out = commands.getoutput(dig_cmd)
        sleep(15)
        # sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " tail -n 25 /var/log/syslog | grep -ir \"authors.*\"" '
        # out1 = commands.getoutput(sys_log_validation)
        # print(out1)

        # print out1
        # assert re.search(r'.*src='+config.client_eth1+'.*nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1',out1)
        log("stop","/var/log/syslog",config.grid_member3_mgmt_vip)
        lookfor = [".*src="+config.client_eth1+".*nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1"]
        for look in lookfor:
            result = logv(look, '/var/log/syslog', config.grid_member3_mgmt_vip)
            print(result)
            if not result:
                print("Failure: Validate nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1")
                assert False
        print("Success: Validate nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1")
        print('-'*30+"Test Case 14 Execution Completed"+'-'*30)
    
    @pytest.mark.run(order=16)
    def test_015_perform_query_within_network_enabled_nat_in_member_security_properties_with_port_number_outside_the_block(self):
        print('-'*30+"Test Case 15 Execution Started"+'-'*30)
        print("Enabled NAT in Member Security Properties")

        print("Performing Queries with client as eth0")
        log("start","/var/log/syslog",config.grid_member3_mgmt_vip)
        sleep(10)
        dig_cmd = 'sshpass -p '+config.password+' ssh root@'+config.client_ip+' dig @'+str(config.grid_member1_vip)+'  authors.bind A -b '+config.client_eth1+'#70'
        out = commands.getoutput(dig_cmd)
        sleep(15)
        # sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " tail -n 25 /var/log/syslog | grep -ir \"authors.*\"" '
        # out1 = commands.getoutput(sys_log_validation)
        # print(out1)

        # print out1
        # assert re.search(r'.*src='+config.client_eth1+'.*nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1',out1)
        log("stop","/var/log/syslog",config.grid_member3_mgmt_vip)
        lookfor = [".*src="+config.client_eth1+".*nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1"]
        for look in lookfor:
            result = logv(look, '/var/log/syslog', config.grid_member3_mgmt_vip)
            print(result)
            if not result:
                print("Failure: Validate nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1")
                assert False
        print("Success: Validate nat=0 nfpt=0 nlpt=0 fqdn=authors.bind hit_count=1")
        print('-'*30+"Test Case 15 Execution Completed"+'-'*30)
    

    @pytest.mark.run(order=17)
    def test_016_test_tcp_queries_with_nat_mappings(self):
        print('-'*30+"Test Case 16 Execution Started"+'-'*30)
        print("Perform TCP Queries with NAT enabled")
        log("start","/var/log/syslog",config.grid_member3_mgmt_vip)
        sleep(10)
        dig_cmd = 'sshpass -p '+config.password+' ssh root@'+config.client_ip+' dig @'+str(config.grid_member1_vip)+' +time=1 +tcp +retries=0 google.com AFSDB -b '+config.client_eth1+'#11'
        out = commands.getoutput(dig_cmd)
        sleep(15)

        print("Validating CEF logs for TCP Queries")
        # sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " tail -n 25 /var/log/syslog | grep -ir \"google.com.*\"" '
        # out = commands.getoutput(sys_log_validation)
        # print out
        # print(out)
        # assert re.search(r'.*src='+config.client_eth1+'.*nat=1 nfpt=9 nlpt=16 fqdn=google.com hit_count=1',out)
        log("stop","/var/log/syslog",config.grid_member3_mgmt_vip)
        lookfor = [".*src="+config.client_eth1+".*nat=1 nfpt=9 nlpt=16 fqdn=google.com hit_count=1"]
        for look in lookfor:
            result = logv(look, '/var/log/syslog', config.grid_member3_mgmt_vip)
            print(result)
            if not result:
                print("Failure: Validate nat=1 nfpt=9 nlpt=16 fqdn=google.com hit_count=1")
                assert False
        print("Success: Validate nat=1 nfpt=9 nlpt=16 fqdn=google.com hit_count=1")
        
        print('-'*30+"Test Case 16 Execution Completed"+'-'*30)
    
    @pytest.mark.run(order=18)
    def test_017_test_adp_nat_settings_with_endport_as_65535_and_performing_queries(self):
        print('-'*30+"Test Case 17 Execution Started"+'-'*30)
        member_security =  ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        global ref_member_security
        ref_member_security = json.loads(member_security)[0]['_ref']
        print ref_member_security


        #data12 = {"enable_nat_rules": True,"nat_rules": [{"cidr": 16,"nat_ports": [{"block_size": 1,"end_port": 65535,"start_port": 1}],"network": "10.36.0.0","rule_type": "NETWORK"},{"address": "10.34.15.199","nat_ports": [{"block_size": 1,"end_port": 65535,"start_port": 1}],"rule_type": "ADDRESS"},{"end_address": "10.34.15.189","nat_ports": [{"block_size": 1,"end_port": 65535,"start_port": 1}],"rule_type": "RANGE","start_address": "10.34.15.182"}]}
        data12 = {"enable_nat_rules": True,"nat_rules": [{"cidr": 16,"nat_ports": [{"block_size": 1,"end_port": 65535,"start_port": 1}],"network": "10.38.0.0","rule_type": "NETWORK"},{"address": config.client_eth1,"nat_ports": [{"block_size": 8,"end_port": 65535,"start_port": 1}],"rule_type": "ADDRESS"},{"end_address": "10.37.255.254","nat_ports": [{"block_size": 8,"end_port": 65535,"start_port": 1}],"rule_type": "RANGE","start_address": "10.37.0.1"}]}
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
        print("Validating Address in cli_conf.txt file")
        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " cat /infoblox/var/atp_conf/cli_conf.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        print(out)


        print("Performing Queries with client as eth0")
        log("start","/var/log/syslog",config.grid_member3_mgmt_vip)
        sleep(10)
        dig_cmd = 'sshpass -p '+config.password+' ssh root@'+config.client_ip+' dig @'+str(config.grid_member1_vip)+'  authors.bind A -b '+config.client_eth1+'#33'
        print(dig_cmd)
        out = commands.getoutput(dig_cmd)
        sleep(15)
        # sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " tail -n 25 /var/log/syslog | grep -ir \"authors.*\"" '
        # out1 = commands.getoutput(sys_log_validation)
        # print(out1)

        # print out1
        # assert re.search(r'.*src='+config.client_eth1+'.*nat=1 nfpt=33 nlpt=40 fqdn=authors.bind hit_count=1',out1) 
        log("stop","/var/log/syslog",config.grid_member3_mgmt_vip)
        lookfor = [".*src="+config.client_eth1+".*nat=1 nfpt=33 nlpt=40 fqdn=authors.bind hit_count=1"]
        for look in lookfor:
            result = logv(look, '/var/log/syslog', config.grid_member3_mgmt_vip)
            print(result)
            if not result:
                print("Failure: Validate nat=1 nfpt=33 nlpt=40 fqdn=authors.bind hit_count=1")
                assert False
        print("Success: Validate nat=1 nfpt=33 nlpt=40 fqdn=authors.bind hit_count=1")
        print('-'*30+"Test Case 17 Execution Completed"+'-'*30)

    @pytest.mark.run(order=19)
    def test_018_custom_rule_queries_with_enabled_nat(self):
        print('-'*30+"Test Case 18 Execution Started"+'-'*30)
        print("Get Member Threat Protection using member:threatprotection object")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        print(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[0]['_ref']

        print("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        print(get_ruleset)
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
        print(rule_temp_ref)
        
        add_custom_rule={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"PASS","log_severity":"WARNING","params":[{"name":"RECORD_TYPE","value":"A"},{"name": "EVENTS_PER_SECOND","value":"1"},{"name":"RATE_FILTER_COUNT","value":"1"},{"name":"DROP_INTERVAL","value":"5"},{"name":"RATE_ALGORITHM","value":"Rate_Limiting"}]}}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:grid:rule",fields=json.dumps(add_custom_rule))
        print(response)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(120)       
        log("start","/var/log/syslog",config.grid_member3_mgmt_vip)
        sleep(10)  
        dig_cmd = 'sshpass -p '+config.password+' ssh root@'+config.client_ip+' dig @'+str(config.grid_member1_vip)+'  '
        dig_cmd = 'sshpass -p '+config.password+' ssh root@'+config.client_ip+' "for i in {1..10};do dig @'+str(config.grid_member1_vip)+' udp3.com A +time=0 +retries=0 -b '+config.client_eth1+'#14;done"'
        print(dig_cmd)

        out = commands.getoutput(dig_cmd)
        sleep(15)
        #sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_mgmt_vip)+' " tail -n 20 /var/log/syslog | grep -ir \"udp3.com.*\"" '
        #out1 = commands.getoutput(sys_log_validation)
        #print(out1)

        #print out1
        #assert re.search(r'.*src='+config.client_eth1+'.*nat=1 nfpt=14 nlpt=14.*',out1)
        log("stop","/var/log/syslog",config.grid_member3_mgmt_vip)
        lookfor = [".*src="+config.client_eth1+".*nat=1 nfpt=9 nlpt=16 fqdn=udp3.com"]
        for look in lookfor:
            result = logv(look, '/var/log/syslog', config.grid_member3_mgmt_vip)
            print(result)
            if not result:
                print("Failure: Validate nat=1 nfpt=9 nlpt=16 fqdn=udp3.com")
                assert False
        print("Success: Validate nat=1 nfpt=9 nlpt=16 fqdn=udp3.com")
        print('-'*30+"Test Case 18 Execution Completed"+'-'*30)

'''
 
    @classmethod
    def teardown_class(cls):

        """ teardown any state that was previously setup with a call to
        setup_class.
        """
        print("TEAR DOWN METHOD")   
'''


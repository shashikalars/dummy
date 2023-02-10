import sys
#sys.path.insert(0, str(os.getenv("HOME"))+'/qa-xaas/main/api/janus/ngp/')
sys.path.insert(0,'/home/vadga-143/IB/qa/vadpga-143/FR/')
import config
import pytest
import pexpect
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
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="license.log" ,level=logging.DEBUG,filemode='w')
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv

master_vip=config.grid_vip
member_vip=config.grid_member2_vip
print member_vip


class NetworkView(unittest.TestCase):
    '''
    @classmethod
    def setup_class(cls):
        """ setup any state specific to the execution of the given class (which
         usually contains tests).
         """
        logging.info("SETUP METHOD")

    def simple_func(self,a):
        # do any process here and return the value
        # Return value is comparted(asserted) in test case method
        return(a+2)

    '''
    @pytest.mark.run(order=1)
    def test_1_vadpga_212_bug_automation(self):
        logging.info('-'*30+"Test Case 1 Execution Started"+'-'*30)
        logging.info("Validated Threat Protection Profile-Search for 'name' field")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[0]['_ref']


        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        #print ref_version_1
        ref_version_2 = json.loads(get_ruleset)[1]['version']
        print ref_version_2
        print config.grid_vip   
        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?sid=200000001&ruleset='+str(ref_version_2))
        print get_rule_temp_ref
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[0]['_ref']
        print ref_1_temp
   
         
        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)
         
        get_ref_after_disable = ib_NIOS.wapi_request('GET', object_type = rule_temp_ref+'?_return_fields=disabled')
        #print get_ref_after_disable
        custom_rule_3=json.loads(get_ref_after_disable)
        logging.info(get_ref_after_disable)
        print get_ref_after_disable
        disable_field = custom_rule_3['disabled']
        print disable_field

        data={"disabled":False,"config":{"action":"ALERT","log_severity":"WARNING","params":[{"name": "EVENTS_PER_SECOND","value":"11"},{"name":"PACKETS_PER_SECOND","value":"1"},{"name":"DROP_INTERVAL","value":"1"},{"name":"RATE_ALGORITHM","value":"Rate_Limiting"}]}}
        modify_disable_field=ib_NIOS.wapi_request('PUT',object_type=rule_temp_ref,fields=json.dumps(data))
        logging.info(modify_disable_field)
        print modify_disable_field


        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
#        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)


        execute_dnsq='dnsq -ns='+str(config.grid_member1_vip)+' -qname=NXDO.foobar -qtype=A -repeat=4 -wait=0.03'
        logs_dnsq=os.system(execute_dnsq)
        sleep(10)    
        logging.info("Validating Syslog After Performing Queries")
        sys_log_validation = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member2_vip)+' " tail -20 /var/log/syslog | grep -ir \'NXDO.foobar hit_count=1\' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        assert out1 == ''
        


    
    
    @pytest.mark.run(order=2)
    def test_2_vadpga_230_automation(self):
        logging.info('-'*30+"Test Case VADPGA-230 Bug Execution Started"+'-'*30)
        logging.info("Validated Threat Protection Profile-Search for 'name' field")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        sys_log_validation = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member2_vip)+' " cat /var/log/syslog | grep -ir \'System memory usage exceeds the critical threshold value .*\' "' 
        out1 = commands.getoutput(sys_log_validation)
        print out1
        assert out1 == ''
        
   
    @pytest.mark.run(order=3)
    def test_3_vadpga_297_automation(self):
        logging.info('-'*30+"Test Case VADPGA-297 Bug Execution Started"+'-'*30)
        logging.info("Validate by Removing MGMT Interface while TP Service Running")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member")
        res = json.loads(get_ref)
        ref_member_1 = json.loads(get_ref)[0]['_ref']
        ref_member_2 = json.loads(get_ref)[1]['_ref']
        print "=========="
        print ref_member_1
        print ref_member_2         
        remove_mgmt={"mgmt_port_setting": {"enabled":False,"security_access_enabled": False,"vpn_enabled": False}}
        status,response1 = ib_NIOS.wapi_request('PUT',object_type=ref_member_2,fields=json.dumps(remove_mgmt))
        logging.info(response1)
        print response1
        print status

        assert status == 400
  
    @pytest.mark.run(order=4)
    def test_4_vadpga_226_automation(self):
        logging.info('-'*30+"Test Case VADPGA-226 Bug Execution Started"+'-'*30)
        log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
        get_ref = ib_NIOS.wapi_request('GET', object_type="member")
        res = json.loads(get_ref)
        ref_member_1 = json.loads(get_ref)[0]['_ref']
        ref_member_2 = json.loads(get_ref)[1]['_ref']
        traffic_capture={"action":"START","interface":"LAN1","seconds_to_run":41}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref_member_2 + "?_function=capture_traffic_control",fields=json.dumps(traffic_capture))
        sleep(10)
        logging.info("Syslog Validation for Publish Changes")
        #syslog_validation = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member2_vip)+' " cat /infoblox/var/infoblox.log | grep -ir \'.*Start traffic capture on interface eth1.*\'  " '
        #out1 = commands.getoutput(syslog_validation)
        #print out1
        #print("-------------------------------")
        #logging.info(out1)
        #assert re.search(r'Start traffic capture',out1)    
        log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
        logs=logv(".*Start traffic capture.*","/infoblox/var/infoblox.log",config.grid_member2_vip)
        print(logs)
        if logs:
            assert True
        else:
            assert False

     
    '''
    @pytest.mark.run(order=5)
    def test_5_vadgpa_197(self):
        #cmd='/home/vadga-143/IB/qa/vadpga-143/FR/set_hardware_type_negative.exp ' +str(config.grid_member5_vip)
	cmd='~/API_Automation/WAPI_PyTest/suites/VADP_Bugautomation/VADPGA-143/set_hardware_type_negative.exp ' +str(config.grid_member5_vip)
        #cmd='/import/qaddi/sramanathan/IBQACI/set_hardware_type_ib_flex.exp ' +str(config.grid_member5_vip)
        out1 = commands.getoutput(cmd)  
        print out1
        assert re.search(r'IB-FLEX platform is not compatible with already installed license',out1) '''
        
    @pytest.mark.run(order=6)
    def test_6_vadpga_284_automation(self):
        logging.info('-'*30+"Test Case VADPGA-226 Bug Execution Started"+'-'*30)
        get_ref = ib_NIOS.wapi_request('GET', object_type="member")
        res = json.loads(get_ref)
        ref_member_1 = json.loads(get_ref)[0]['_ref']
        ref_member_2 = json.loads(get_ref)[1]['_ref']
        ref_member_3 = json.loads(get_ref)[2]['_ref']
         
        vpn_on_mgmt={"mgmt_port_setting":{"enabled": True,"security_access_enabled": False,"vpn_enabled":True}}
        request_mgmt = ib_NIOS.wapi_request('PUT', object_type = ref_member_3,fields=json.dumps(vpn_on_mgmt))
        sleep(120)    
        vpn_on_mgmt={"mgmt_port_setting":{"enabled": True,"security_access_enabled": False,"vpn_enabled":False}}
        request_mgmt = ib_NIOS.wapi_request('PUT', object_type = ref_member_3,fields=json.dumps(vpn_on_mgmt))
        sleep(300)
        
        ref_1 = json.loads(get_ref)[1]['_ref']
        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_member_3+'?_return_fields=node_info')
        #print get_ref_disable
        print type(get_ref_disable)
        ref_123 = json.loads(get_ref_disable)
        provisioning =ref_123['node_info']
        print provisioning[0]
         
	for i in provisioning[0]:
		if i=='service_status':
			print len(i)
			a=provisioning[0]['service_status']
			print type(a)
			print a[1]['description']
                        print a[1]['status']   
                        
                   
        #assert a[1]['description'] == "Running"
        assert a[1]['status'] == "WORKING" 
    

    @pytest.mark.run(order=7)
    def test_7_vadpga_305_automation(self):
        
        logging.info('-'*30+"Test Case VADPGA-305 Bug Execution Started"+'-'*30)
        reboot_cmd = 'reboot_system -H '+str(config.grid_member2_id)+' -a poweroff'
        os.system(reboot_cmd)
        sleep(180)
        vmspec_cmd ='vm_specs -H '+str(config.grid_member2_id)+' -M 18 -C 6'
        os.system(vmspec_cmd)
        sleep(180)
        reboot_on = 'reboot_system -H '+str(config.grid_member2_id)+' -a poweron'
        os.system(reboot_on)
        reboot_cmd = 'reboot_system -H '+str(config.grid_member2_id)+' -a poweroff'
        os.system(reboot_cmd)
        sleep(180)
        vmspec_cmd ='vm_specs -H '+str(config.grid_member2_id)+' -M 22 -C 8'
        os.system(vmspec_cmd)
        sleep(180)
        reboot_on = 'reboot_system -H '+str(config.grid_member2_id)+' -a poweron'
        os.system(reboot_on)
        sleep(180)  
        
        cmd=commands.getstatusoutput('~/API_Automation/WAPI_PyTest/suites/VADP_Bugautomation/VADPGA-143/show_hardware_type_detailed.exp ' +str(config.grid_member2_vip))
        print cmd[1]
        #assert re.search(r'TYPE3',cmd[1])
        assert re.search(r'IB-FLEX',cmd[1])
        logging.info('-'*30+"Test Case NIOSBFD-305 Execution Completed"+'-'*30)
    
    @pytest.mark.run(order=8)
    def test_8_VADPGA_296(self):
        logging.info('-'*15+"Executing VADPGA-296 Bug Automation"+'-'*15)
        logging.info("Enable TP Service")
        response = ib_NIOS.wapi_request('GET', object_type="member:threatprotection?host_name=%s"%config.grid_member1_fqdn)
        logging.info(response)
        res = json.loads(response)
        print res
        ref_1 = res[0]['_ref']
        print ref_1
             
        data={"enable_service":True}
        modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1,fields=json.dumps(data))
        logging.info(modify_disable_field)
        print modify_disable_field
        sleep(120)

        get_enable_service = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=enable_service')
        service_enable=json.loads(get_enable_service)
        logging.info(get_enable_service)
        print get_enable_service
        disable_field = service_enable['enable_service']
        print disable_field
        sleep(20)
        assert service_enable["enable_service"] == True
         
    
    @pytest.mark.run(order=9)
    def test_9_VADPGA_241(self):
        logging.info('-'*15+"Executing VADPGA-241"+'-'*15)  
        logging.info('-'*15+"Validate DB Capacity For TYPE-3"+'-'*15)
        #cmd=commands.getstatusoutput('/home/vadga-143/IB/qa/vadpga-143/FR/show_capacity_type_3.exp ' +str(config.grid_member4_vip))
        cmd=commands.getstatusoutput('~/API_Automation/WAPI_PyTest/suites/VADP_Bugautomation/VADPGA-143/show_capacity_type_3.exp ' +str(config.grid_member4_vip))
        print cmd[1]
        assert re.search(r'600000',cmd[1]) 
        #assert re.search(r'33000',cmd[1])
    

    


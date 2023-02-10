import sys
#sys.path.insert(0, str(os.getenv("HOME"))+'/qa-xaas/main/api/janus/ngp/')
sys.path.insert(0,'~/API_Automation/WAPI_PyTest/suites/BFD_Bug_Automation/')
import config
import pexpect
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
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="license.log" ,level=logging.DEBUG,filemode='w')

master_vip=config.grid_vip
member_vip=config.grid_member1_vip
print member_vip
member2_vip = config.grid_member2_vip
print member2_vip
member3_vip = config.grid_member3_vip
print member3_vip

class NetworkView(unittest.TestCase):

    @classmethod
    def setup_class(cls):
        """ setup any state specific to the execution of the given class (which
         usually contains tests).
        """
                     
        add_bfd_template={"name": "template_1","authentication_key_id":24,"authentication_type":"MD5","authentication_key":"infoblox","min_rx_interval":51,"min_tx_interval":51}
        response = ib_NIOS.wapi_request('POST',object_type="bfdtemplate",fields=json.dumps(add_bfd_template))
        logging.info("GET Reference of Member")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[2]['_ref']
        print ref  
  #     modify_bgp_anycast={"bgp_as":[{"as":1,"holddown":16,"keepalive":4,"link_detect":False,"neighbors":[{"authentication_mode":"NONE","enable_bfd":True,"interface":"LAN_HA","multihop":False,"multihop_ttl":255,"neighbor_ip":"3.3.3.3","remote_as":1},{"authentication_mode":"NONE","bfd_template":"template_1","enable_bfd":True,"interface":"LAN_HA","multihop":False,"multihop_ttl":255,"neighbor_ip":"5.5.5.5","remote_as":1}]}]}
        modify_bgp_anycast={"bgp_as":[{"as":1,"holddown":16,"keepalive":4,"link_detect":False,"neighbors":[{"authentication_mode":"NONE","enable_bfd":False,"interface":"LAN_HA","multihop":False,"multihop_ttl":255,"neighbor_ip":"10.34.15.199","remote_as":111}]}]}
        response = ib_NIOS.wapi_request('PUT',object_type=ref,fields=json.dumps(modify_bgp_anycast))
 
  #     modify_ospf_anycast={"ospf_list":[{"area_id":"2","area_type":"STANDARD","authentication_type":"NONE","auto_calc_cost_enabled": True,"cost":1,"dead_interval":40,"enable_bfd":True,"hello_interval":10,"interface":"LAN_HA","is_ipv4":True,"key_id":1,"retransmit_interval":5,"transmit_delay":1},{"area_id":"0.0.0.2","area_type": "STANDARD","authentication_type":"NONE","auto_calc_cost_enabled": True,"cost":1,"dead_interval":40,"enable_bfd":True,"hello_interval":10,"interface":"LAN_HA","is_ipv4":False,"key_id":1,"retransmit_interval":5,"transmit_delay":1}]}
        modify_ospf_anycast={"ospf_list":[{"area_id":"2","area_type":"STANDARD","authentication_type":"NONE","auto_calc_cost_enabled": True,"cost":1,"dead_interval":40,"enable_bfd":True,"hello_interval":10,"interface":"LAN_HA","is_ipv4":True,"key_id":1,"retransmit_interval":5,"transmit_delay":1},{"area_id":"0.0.0.2","area_type": "STANDARD","authentication_type":"NONE","auto_calc_cost_enabled": True,"cost":1,"dead_interval":40,"enable_bfd":False,"hello_interval":10,"interface":"LAN_HA","is_ipv4":False,"key_id":1,"retransmit_interval":5,"transmit_delay":1}]}
        response = ib_NIOS.wapi_request('PUT',object_type=ref,fields=json.dumps(modify_ospf_anycast))

        modify_additional_ip={"additional_ip_list":[{"anycast":True,"enable_bgp":False,"enable_ospf":True,"interface":"LOOPBACK","ipv6_network_setting":{"cidr_prefix":128,"dscp":0,"enabled":True,"primary":False,"use_dscp":False,"virtual_ip":"1111::1111"}},{"anycast":True,"enable_bgp":False,"enable_ospf":True,"interface":"LOOPBACK","ipv4_network_setting":{"address":"1.1.1.1","dscp":0,"primary":False,"subnet_mask":"255.255.255.255","use_dscp":False}}]} 
        response = ib_NIOS.wapi_request('PUT',object_type=ref,fields=json.dumps(modify_additional_ip))
        sleep(300)  
         
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[2]['_ref']
    
        member_additional_ip={"additional_ip_list": ["1111::1111","1.1.1.1"]}
        response = ib_NIOS.wapi_request('PUT',object_type=ref_1,fields=json.dumps(member_additional_ip))
        sleep(300)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref_grid = json.loads(grid)[0]['_ref']
   
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref_grid + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref_grid + "?_function=restartservices")
        sleep(120)
        
        logging.info("SETUP METHOD")
        

    def simple_func(self,a):
        # do any process here and return the value
        # Return value is comparted(asserted) in test case method
        return(a+2)
    
    @pytest.mark.run(order=1)
    def test_1_niosbfd_18(self):
        logging.info('-'*30+"Test Case NIOSBFD-18 Execution Started"+'-'*30)
        proc=pexpect.spawn("ssh admin@"+member3_vip+"")
        print member_vip

        try:
            print "---"
            index=proc.expect(["admin.*password:","Are you sure you want to continue connecting.*"],timeout=30)
            if index == 1:
               proc.sendline("yes")
               sleep(5)
            proc.sendline("infoblox")
            proc.expect(r"Infoblox")
            print "---Console---"
            proc.sendline("set bfd log informational")
            print "---Executed set bfd log  command ---"
            sleep(60)
            print "---Selected Yes Option---"
            ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " grep -ir \"syslog\" /infoblox/var/quagga/bfdd.conf " '
            out = commands.getoutput(ssh_cmd)
            assert re.search(r'informational',out)
        except pexpect.TIMEOUT:
            print "Error"
        logging.info('-'*30+"Test Case NIOSBFD-18 Execution Completed"+'-'*30)
    
    @pytest.mark.run(order=2)
    def test_2_niosbfd_15(self):
        logging.info('-'*30+"Test Case NIOSBFD-15 Execution Started"+'-'*30)
        cmd=commands.getstatusoutput('~/API_Automation/WAPI_PyTest/suites/BFD_Bug_Automation/show_bfd.exp ' +str(config.grid_member3_vip))
        print cmd[1]
        #assert re.search(r'Up',cmd[1])
        logging.info('-'*30+"Test Case NIOSBFD-15 Execution Completed"+'-'*30)
    

    @pytest.mark.run(order=3)
    def test_3_niosbfd_13(self):
        logging.info('-'*30+"Test Case NIOSBFD-13 Execution Started"+'-'*30)
        ssh_cmd = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " pidof named " '
        out = commands.getoutput(ssh_cmd)
        print out
        ssh_cmd1 = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " /bin/kill -9 '+str(out)+' " '  
        print ssh_cmd1
        cmd=commands.getstatusoutput(ssh_cmd1)
	print cmd
        sleep(120)
        logging.info("Validating Syslog After Performing Queries")
        sys_log_validation = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " tail -200 /var/log/syslog | grep \'notice BFDd\' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        logging.info(out1)
        assert re.search(r'notice BFDd .*starting.*',out1)
        cmd=commands.getstatusoutput('~/API_Automation/WAPI_PyTest/suites/BFD_Bug_Automation/show_bfd.exp ' +str(config.grid_member3_vip))
        print cmd[1]
        #assert re.search(r'Up',cmd[1])

    

    @pytest.mark.run(order=4)
    def test_4_niosbfd_12(self):
        logging.info('-'*30+"Test Case NIOSBFD-12 Execution Started"+'-'*30)
        ssh_cmd = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " pidof named " '
        out = commands.getoutput(ssh_cmd)
        print out
        ssh_cmd1 = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " /bin/kill -9 '+str(out)+' " '
        print ssh_cmd1
        cmd=commands.getstatusoutput(ssh_cmd1)
        print cmd
        sleep(120)
        logging.info("Validating Syslog After Performing Queries")
        sys_log_validation = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " tail -200 /var/log/syslog | grep \'notice BFDd \' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        logging.info(out1)
        assert re.search(r'notice BFDd .*starting.*',out1)
        cmd=commands.getstatusoutput('~/API_Automation/WAPI_PyTest/suites/BFD_Bug_Automation/show_bfd.exp ' +str(config.grid_member3_vip))
        print cmd[1]
        #assert re.search(r'Up',cmd[1])
        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " grep -ir \"syslog\" /infoblox/var/quagga/bfdd.conf " '
        out = commands.getoutput(ssh_cmd)
        assert re.search(r'informational',out)

    

    @pytest.mark.run(order=5)
    def test_5_niosbfd_4(self):
        logging.info('-'*30+"Test Case NIOSBFD-4 Execution Started"+'-'*30)
            
        ssh_cmd = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " pidof bfdd " '
        out = commands.getoutput(ssh_cmd)
        print out
        ssh_cmd1 = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " /bin/kill -9 '+str(out)+' " '
        print ssh_cmd1
        cmd=commands.getstatusoutput(ssh_cmd1)
        print cmd
        sleep(60)
        logging.info("Validating Syslog After Performing Queries")
        
        sys_log_validation = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " tail -200 /var/log/syslog " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        assert re.search(r'notice BFDd .*starting.*',out1) 
  

    @pytest.mark.run(order=6)
    def test_6_niosbfd_11(self):
        logging.info('-'*30+"Test Case NIOSBFD-6 Execution Started"+'-'*30)

        ssh_cmd = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " pidof bfdd " '
        out = commands.getoutput(ssh_cmd)
        print out
        ssh_cmd1 = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " /bin/kill -9 '+str(out)+' " '
        print ssh_cmd1
        cmd=commands.getstatusoutput(ssh_cmd1)
        print cmd
        sleep(30)
        logging.info("Validating Syslog After Performing Queries")

        sys_log_validation = 'ssh -o StrictHostKeyChecking=no  -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " tail -100 /var/log/syslog " '
        out1 = commands.getoutput(sys_log_validation)
 
    @pytest.mark.run(order=7)
    def test_7_niosbfd_78(self):
        logging.info('-'*30+"Test Case NIOSBFD-78 Execution Started"+'-'*30)

        ssh_cmd = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " pidof bfdd " '
        out = commands.getoutput(ssh_cmd)
        print out
        ssh_cmd1 = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " /bin/kill -9 '+str(out)+' " '
        print ssh_cmd1
        cmd=commands.getstatusoutput(ssh_cmd1)
        print cmd
        sleep(30)
        logging.info("Validating Syslog After Performing Queries")

        logging.info("Validating Syslog After Performing Queries")
        sys_log_validation = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " tail -200 /var/log/syslog " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        assert re.search(r'notice BFDd .*starting.*',out1)

    
    @pytest.mark.run(order=8)
    def test_8_niosbfd_70(self):
        logging.info('-'*30+"Test Case NIOSBFD-70 Execution Started"+'-'*30)
        logging.info("Validating Syslog After Performing Queries")
        sys_log_validation = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " tail -200 /var/log/syslog | grep -ir \'warning ospf6_rxpacket_examin\' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        assert out1 == ''
        

    @pytest.mark.run(order=9)
    def test_9_niosbfd_65(self):
        logging.info('-'*30+"Test Case NIOSBFD-65 Execution Started"+'-'*30)
        ssh_cmd = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " pidof named " '
        out = commands.getoutput(ssh_cmd)
        print out
        ssh_cmd1 = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " /bin/kill -9 '+str(out)+' " '
        print ssh_cmd1
        cmd=commands.getstatusoutput(ssh_cmd1)
        print cmd
        sleep(120)
        logging.info("Validating Syslog After Performing Queries")
        sys_log_validation = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " tail -200 /var/log/syslog | grep \'info Ouch DNS went down \' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        logging.info(out1)
        assert out1 == ''
        cmd=commands.getstatusoutput('~/API_Automation/WAPI_PyTest/suites/BFD_Bug_Automation/show_bfd.exp ' +str(config.grid_member3_vip))
        print cmd[1]
        #assert re.search(r'Up',cmd[1])

    
    @pytest.mark.run(order=10)
    def test_10_niosbfd_35(self):
        logging.info('-'*30+"Test Case NIOSBFD-35 Execution Started"+'-'*30)
        cmd=commands.getstatusoutput('~/API_Automation/WAPI_PyTest/suites/BFD_Bug_Automation/show_bfd.exp ' +str(config.grid_member3_vip))
        print cmd[1]
        #assert re.search(r'Up',cmd[1])
    

    @pytest.mark.run(order=11)
    def test_11_niosbfd_23(self):
        logging.info('-'*30+"Test Case NIOSBFD-23 Execution Started"+'-'*30)
        ssh_cmd = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " pidof bfdd " '
        out = commands.getoutput(ssh_cmd)
        print out
        ssh_cmd1 = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " /bin/kill -9 '+str(out)+' " '
        print ssh_cmd1
        cmd=commands.getstatusoutput(ssh_cmd1)
        print cmd
        sleep(60)
        logging.info("Validating Syslog After Performing Queries")
        sys_log_validation = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " tail -200 /var/log/syslog | grep \'.*An BFD daemon failure has occurred.*\' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        logging.info(out1)
        assert re.search(r'BFD daemon failure has occurred',out1)

    
    @pytest.mark.run(order=12)
    def test_12_niosbfd_24(self):
        logging.info('-'*30+"Test Case NIOSBFD-23 Execution Started"+'-'*30)
        ssh_cmd = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " pidof bfdd " '
        out = commands.getoutput(ssh_cmd)
        print out
        ssh_cmd1 = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " /bin/kill -9 '+str(out)+' " '
        print ssh_cmd1
        cmd=commands.getstatusoutput(ssh_cmd1)
        print cmd
        sleep(60)
        logging.info("Validating Syslog After Performing Queries")
        sys_log_validation = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " tail -50 /var/log/syslog | grep -ir \'.*Trap with code 4294963200 is not part of any category.*\' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        logging.info(out1)
        assert out1 == ''
    

    @pytest.mark.run(order=13)
    def test_13_niosbfd_25(self):
        logging.info('-'*30+"Test Case NIOSBFD-25 Execution Started"+'-'*30)
        proc=pexpect.spawn("ssh admin@"+member3_vip+"")
        print member_vip

        try:
            print "---"
            index=proc.expect(["admin.*password:","Are you sure you want to continue connecting.*"],timeout=30)
            if index == 1:
               proc.sendline("yes")
               sleep(5)
            proc.sendline("infoblox")
            proc.expect(r"Infoblox")
            print "---Console---"
            proc.sendline("set bfd log debugging")
            print "---Executed set bfd log  command ---"
            sleep(60)
            print "---Selected Yes Option---"
            ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " grep -ir \"syslog\" /infoblox/var/quagga/bfdd.conf " '
            out = commands.getoutput(ssh_cmd)
            assert re.search(r'debugging',out)
        except pexpect.TIMEOUT:
            print "Error"
    
    

    @pytest.mark.run(order=14)
    def test_14_niosbfd_32(self):
        logging.info('-'*30+"Test Case NIOSBFD-32 Execution Started"+'-'*30)
        ssh_cmd = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " pidof bgpd " '
        out = commands.getoutput(ssh_cmd)
        print out
        ssh_cmd1 = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " /bin/kill -9 '+str(out)+' " '
        print ssh_cmd1
        cmd=commands.getstatusoutput(ssh_cmd1)
        print cmd
        sleep(60)
        logging.info("Validating Syslog After Performing Queries")
        sys_log_validation = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " tail -1000 /var/log/syslog | grep -ir \'.*Enabled firewall BGP.*\' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        assert out1 == ''  
    

    @pytest.mark.run(order=15)
    def test_15_niosbfd_58(self):
        logging.info('-'*30+"Test Case NIOSBFD-58 Execution Started"+'-'*30)
        proc=pexpect.spawn("ssh admin@"+member3_vip+"")
        print member3_vip
        try:
            print "---"
            index=proc.expect(["admin.*password:","Are you sure you want to continue connecting.*"],timeout=30)
            if index == 1:
               proc.sendline("yes")
               sleep(5)
            proc.sendline("infoblox")
            proc.expect(r"Infoblox")
            print "---Console---"
            proc.sendline("set bfd log informational")
            print "---Executed set bfd log  command ---"
            sleep(60)
            print "---Selected Yes Option---"
            ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " grep \"syslog\" /infoblox/var/quagga/bfdd.conf " '
            out = commands.getoutput(ssh_cmd)
            audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " tail -200 /infoblox/var/audit.log | grep informational  " '
            out1 = commands.getoutput(audit_log_validation)
            print out1
            logging.info(out1)
            regex = '.*set BFD:.*Args log_level="informational"'
            assert re.search(regex,out1)
           # assert re.search(r'informational',out)
        except pexpect.TIMEOUT:
            print "Error"


    @pytest.mark.run(order=16)
    def test_16_niosbfd_34(self):
        logging.info('-'*30+"Test Case NIOSBFD-34 Execution Started"+'-'*30)
        ssh_cmd = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " pidof bfdd " '
        out = commands.getoutput(ssh_cmd)
        print out
        ssh_cmd1 = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " /bin/kill -9 '+str(out)+' " '
        print ssh_cmd1
        cmd=commands.getstatusoutput(ssh_cmd1)
        print cmd
        cmd=commands.getstatusoutput('~/API_Automation/WAPI_PyTest/suites/BFD_Bug_Automation/show_bfd.exp ' +str(config.grid_member3_vip))
        print cmd[1]
    #    assert re.search(r'BFD daemon failure has occurred',out1)
        #assert re.search(r'bfdd process is not running',cmd[1])
    
    @pytest.mark.run(order=17)
    def test_17_nios_56962(self):
        logging.info('-'*30+"Test Case NIOS-56962 Execution Started"+'-'*30)
        cmd=commands.getstatusoutput('~/API_Automation/WAPI_PyTest/suites/BFD_Bug_Automation/set_upgrade_reset_status.exp ' +str(config.grid_member3_vip))
        print cmd[1]
        assert re.search(r'Successfully reset upgrade status.*',cmd[1])
    
    @pytest.mark.run(order=18)
    def test_18_nios_57458(self):
        logging.info('-'*30+"Test Case NIOS-57458 Execution Started"+'-'*30)
        cmd=commands.getstatusoutput('~/API_Automation/WAPI_PyTest/suites/BFD_Bug_Automation/set_upgrade_reset_status.exp ' +str(config.grid_member3_vip))
        print cmd[1]
        #regex = 'Could not chdir to home directory'
    
    @pytest.mark.run(order=19)
    def test_19_niosbfd_7(self):
        logging.info('-'*30+"Test Case NIOSBFD-7 Execution Started"+'-'*30)
        ssh_cmd = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " pidof bfdd " '
        out = commands.getoutput(ssh_cmd)
        print out
        ssh_cmd1 = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " /bin/kill -9 '+str(out)+' " '
        print ssh_cmd1
        cmd=commands.getstatusoutput(ssh_cmd1)
        print cmd
        sleep(30)
        logging.info("Validating Syslog After Performing Queries")

        logging.info("Validating Syslog After Performing Queries")
        sys_log_validation = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " tail -200 /var/log/syslog " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        assert re.search(r'notice BFDd .*starting.*',out1)
    

    @pytest.mark.run(order=20)
    def test_20_niosbfd_6(self):
        logging.info('-'*30+"Test Case NIOSBFD-6 Execution Started"+'-'*30)
        ssh_cmd = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " pidof bfdd " '
        out = commands.getoutput(ssh_cmd)
        print out
        ssh_cmd1 = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " /bin/kill -9 '+str(out)+' " '
        print ssh_cmd1
        cmd=commands.getstatusoutput(ssh_cmd1)
        print cmd
        sleep(30)
        logging.info("Validating Infoblox log After Performing Queries")
        sys_log_validation = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " grep ".*set_svc_ports BFD udp:3784.*" /infoblox/var/infoblox.log " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        assert re.search(r'set_svc_ports BFD udp:3784.*',out1)

        logging.info("Validating Infoblox log After Performing Queries")

    
    @pytest.mark.run(order=21)
    def test_21_niosbfd_19(self):
        logging.info('-'*30+"Test Case NIOSBFD-19 Execution Started"+'-'*30)
        ssh_cmd = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " pidof bfdd " '
        out = commands.getoutput(ssh_cmd)
        print out
        ssh_cmd1 = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " /bin/kill -9 '+str(out)+' " '
        print ssh_cmd1
        cmd=commands.getstatusoutput(ssh_cmd1)
        print cmd
        sleep(60)
        logging.info("Validating Syslog After Performing Queries")
        sys_log_validation = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " tail -250 /var/log/syslog | grep \'.*An BFD daemon failure has occurred.*\' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        logging.info(out1)
        assert re.search(r'.*BFD daemon failure has occurred.*',out1)

    @pytest.mark.run(order=22)
    def test_22_niosbfd_14(self):
        logging.info('-'*30+"Test Case NIOSBFD-14 Execution Started"+'-'*30)
        ssh_cmd = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " pidof bfdd " '
        out = commands.getoutput(ssh_cmd)
        print out
        ssh_cmd1 = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " /bin/kill -9 '+str(out)+' " '
        print ssh_cmd1
        cmd=commands.getstatusoutput(ssh_cmd1)
        print cmd
        sleep(60)
        logging.info("Validating Syslog After Performing Queries")
        sys_log_validation = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " tail -200 /var/log/syslog | grep  \'.*An BFD daemon failure has occurred.*\' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        logging.info(out1)
        assert re.search(r'.*BFD daemon failure has occurred.*',out1)
    

    @pytest.mark.run(order=23)
    def test_23_niosbfd_79(self):
        logging.info('-'*30+"Test Case NIOSBFD-79 Execution Started"+'-'*30)
        cmd=commands.getstatusoutput('~/API_Automation/WAPI_PyTest/suites/BFD_Bug_Automation/set_ospf.exp ' +str(config.grid_member3_vip))
        print cmd[1]
        assert re.search(r'The logging level has been correctly set',cmd[1])
   
    @pytest.mark.run(order=24)
    def test_24_niosbfd_83(self):
        logging.info('-'*30+"Test Case NIOSBFD-83 Execution Started"+'-'*30)
        cmd=commands.getstatusoutput('~/API_Automation/WAPI_PyTest/suites/BFD_Bug_Automation/show_ipv6_ospf_neighbor.exp ' +str(config.grid_member3_vip))
        print cmd[1]
        #assert re.search(r'Neighbor',cmd[1])
   

    @pytest.mark.run(order=25)
    def test_25_nios_56699(self):
        logging.info('-'*30+"Test Case NIOS-56699 Execution Started"+'-'*30)
        proc=pexpect.spawn("ssh admin@"+member2_vip+"")
        print member2_vip

        try:
            print "---"
            index=proc.expect(["admin.*password:","Are you sure you want to continue connecting.*"],timeout=30)
            if index == 1:
               proc.sendline("yes")
               sleep(5)
            proc.sendline("infoblox")
            proc.expect(r"Infoblox")
            print "---Console---"
            proc.sendline("set port_mac_addr on LAN1 10.34.15.56 23:31:11:11:11:11")
            sleep(2)
            proc.expect(r".*y or n.*")
            proc.sendline("y")
            sleep(1)
            proc.expect(r".*y or n.*")
            proc.sendline("y")
            print "---Executed set bfd log  command ---"
            sleep(120)
            print "---Selected Yes Option---"
            cmd=commands.getstatusoutput('~/API_Automation/WAPI_PyTest/suites/BFD_Bug_Automation/show_interface_lan1.exp ' +str(config.grid_member2_vip))
            print cmd[1]
            assert re.search(r'23:31:11:11:11:11',cmd[1])
        except pexpect.TIMEOUT:
            print "Error"

    @pytest.mark.run(order=26)
    def test_26_niosbfd_55(self):
        logging.info('-'*30+"Test Case NIOSBFD-55 Execution Started"+'-'*30)
        logging.info("Validating Syslog After Performing Queries")
        modify_password = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " sed -i \'s/infoblox/were/g\' /infoblox/var/quagga/bfdd.conf " '
        out1 = commands.getoutput(modify_password)
        sleep(30)
        sys_log_validation = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " tail -200 /var/log/syslog " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        assert re.search(r'.*notice BFDd .*starting.*',out1)
        modify_password_1 = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " sed -i \'s/were/infoblox/g\' /infoblox/var/quagga/bfdd.conf " '
        out1 = commands.getoutput(modify_password_1)
        sleep(30)  

    @pytest.mark.run(order=27)
    def test_27_niosbfd_48(self):
        logging.info('-'*30+"Test Case NIOSBFD-48 Execution Started"+'-'*30)
        get_ref = ib_NIOS.wapi_request('GET', object_type="bfdtemplate")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[0]['_ref']

        modify_bgp_anycast={"authentication_type":"NONE"}
        response = ib_NIOS.wapi_request('PUT',object_type=ref,fields=json.dumps(modify_bgp_anycast))
        sleep(30)
        sys_log_validation = 'ssh -q -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member3_vip)+' " tail -200 /var/log/syslog " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        assert re.search(r'.*notice BFDd .*starting.*',out1)


    @pytest.mark.run(order=28)
    def test_28_nurture_774(self):
        logging.info('-'*30+"Test Case NURTURE-774 Execution Started"+'-'*30)
        add_user={"name":"remote_user","admin_groups":["admin-group"],"auth_type":"REMOTE"}
        response = ib_NIOS.wapi_request('POST',object_type="adminuser",fields=json.dumps(add_user))
        logging.info(response)

    @pytest.mark.run(order=29)
    def test_29_niosbfd_3(self):
        logging.info('-'*30+"Test Case NIOSBFD-29 Execution Started"+'-'*30)
        cmd=commands.getstatusoutput('~/API_Automation/WAPI_PyTest/suites/BFD_Bug_Automation/show_bfd.exp ' +str(config.grid_member3_vip))
        print cmd[1]
        #assert re.search(r'Up',cmd[1])

    @pytest.mark.run(order=30)
    def test_30_niosbfd_80(self):
        logging.info('-'*30+"Test Case NIOSBFD-80 Execution Started"+'-'*30)
        cmd=commands.getstatusoutput('~/API_Automation/WAPI_PyTest/suites/BFD_Bug_Automation/show_bfd.exp ' +str(config.grid_member3_vip))
        print cmd[1]
        #assert re.search(r'Up',cmd[1])

 
    @classmethod
    def teardown_class(cls):
        """ teardown any state that was previously setup with a call to
        setup_class.
        """
        logging.info("TEAR DOWN METHOD")   


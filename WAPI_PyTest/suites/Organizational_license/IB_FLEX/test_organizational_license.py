# -*- coding: utf-8 -*-
import pexpect
import config
import pytest
import unittest
import logging
import subprocess
import commands
import json
import os
from time import sleep
#import ib_utils.ib_NIOS as ib_NIOS
from ib_utils import ib_NIOS as ib_NIOS
import re
#import ib_utils.ib_get as ib_get
from time import sleep
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="license.log" ,level=logging.DEBUG,filemode='w')
master_vip=config.grid_vip
member_vip=config.grid_member1_vip
print member_vip
#proc=pexpect.spawn("ssh admin@"+member_vip+" -p 2020")

class NetworkView(unittest.TestCase):

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
    
    @pytest.mark.run(order=1)
    def test_1_perform_set_nogrid_for_adding_running_member(self):
        logging.info('-'*30+"Test Case NIOSBFD-18 Execution Started"+'-'*30)
        proc=pexpect.spawn("ssh admin@"+member_vip+"")
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
            proc.sendline("set nogrid")
            sleep(2)
            proc.expect(r".*this such an emergency?")
            proc.sendline("y")
            sleep(1)
            proc.expect(r".*y or n.*")
            proc.sendline("y")
            print "---Executed set bfd log  command ---"
            sleep(120)
            print "---Selected Yes Option---"
        except pexpect.TIMEOUT:
            print "Error"


    @pytest.mark.run(order=2)
    def test_2_delete_offline_member_from_grid(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="member")
        res = json.loads(get_ref)
        ref_member_1 = json.loads(get_ref)[0]['_ref']
        ref_member_2 = json.loads(get_ref)[1]['_ref']
        print "=========="
        print ref_member_1
        print ref_member_2
        remove_member={"host_name":config.grid_member1_fqdn}
        response1 = ib_NIOS.wapi_request('DELETE',object_type=ref_member_2,fields=json.dumps(remove_member))
        logging.info(response1)



    @pytest.mark.run(order=3)
    def test_3_add_offline_member_in_ib_flex_grid(self):
        data={"host_name":config.grid_member1_fqdn,"vip_setting":{"address": config.grid_member1_vip,"dscp":0,"gateway": "10.35.0.1","primary":True,"subnet_mask":"255.255.0.0","use_dscp": False},"platform":"VNIOS","config_addr_type":"IPV4"}
        get_status = ib_NIOS.wapi_request('POST',object_type="member",fields=json.dumps(data))
        
    @pytest.mark.run(order=4)
    def test_4_enable_ib_flex_in_preprovisioning_for_offline_member(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="member")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']  
        data={"pre_provisioning": {"hardware_info": [{"hwtype": "IB-FLEX"}],"licenses":[]}}
        get_status = ib_NIOS.wapi_request('PUT',object_type=ref_1,fields=json.dumps(data))
        get_ref = ib_NIOS.wapi_request('GET', object_type="member")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']
        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=pre_provisioning')
        print get_ref_disable
        print type(get_ref_disable)
        ref_123 = json.loads(get_ref_disable)
        print ref_123
        print type(ref_123)   
        provisioning = json.loads(get_ref_disable)['pre_provisioning']
        print provisioning
     #  print "provisioning['hardware_info']: ", provisioning['hardware_info']
        hw_in =provisioning ['hardware_info']
        print hw_in

    @pytest.mark.run(order=5)
    def test_5_install_organizational_license(self):
        logging.info('-'*15+"Installing Organizational License"+'-'*15)
        cmd1='/import/qaddi/sramanathan/IBQACI/set_license_name.exp ' +str(config.grid_member1_vip)+ ' "Add Flex Grid Activation license\"'
        rc1=os.system(cmd1)
        logging.info(rc1)
        sleep(120)



    @pytest.mark.run(order=6)
    def test_6_set_hardware_type_as_ib_flex_for_preprovisioned_offline_member(self):
        print member_vip
        proc=pexpect.spawn("ssh admin@"+member_vip+"")
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
            proc.sendline("set hardware-type IB-FLEX")
            print "---Executed set hardware-type command to IB-FLEX---"
            sleep(60)
            proc.expect(r"Do you want to proceed.*")
            proc.sendline("y")
            print "---Selected Yes Option---"
            sleep(180)
            cmd=commands.getstatusoutput('show_hw_type.exp ' +str(config.grid_member1_vip))
           # member_type_validation = re.search(r'(Member hardware type):\s+(IB-FLEX+)', cmd[1]).group(2)

        except pexpect.TIMEOUT:
            print "Error"
    
    @pytest.mark.run(order=7)
    def test_7_perform_set_membership_for_ib_flex_enabled_preprovisioned_offline_member(self):
        sys_cmd ='reboot_system -H '+str(config.grid_member3_vip)+' -a poweroff -c krishnas'
        out1 = os.system(sys_cmd)
        sleep(180)
        vm_sp = 'vm_specs -H '+str(config.grid_member3_vip)+' -M 10 -C 4 -c krishnas' 
        vm1 = os.system(vm_sp)
        sleep(180) 
        exe_sys_cmd ='reboot_system -H '+str(config.grid_member3_vip)+' -a poweron -c krishnas'
        out1 = os.system(exe_sys_cmd)  
        
        set_membership='./set_membership.exp ' +str(config.grid_member1_vip)+'  '+str(config.grid_vip)
        os.system(set_membership)
        sleep(300)
         
        cmd=commands.getstatusoutput('./show_hw_type.exp ' +str(config.grid_member1_vip))
        #member_type_validation = re.search(r'(Member hardware type):\s+(IB-FLEX+)', cmd[1]).group(2)
        assert re.search(r'.*IB-FLEX.*',cmd[1])
       
        logging.info("found")

  

    @classmethod
    def teardown_class(cls):
        """ teardown any state that was previously setup with a call to
        setup_class.
        """
        logging.info("TEAR DOWN METHOD")   


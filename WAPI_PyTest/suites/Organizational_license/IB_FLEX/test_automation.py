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
import ib_utils.ib_NIOS as ib_NIOS
import re
#import ib_utils.ib_get as ib_get
from time import sleep
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="license.log" ,level=logging.DEBUG,filemode='w')

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
    def test_validate_log_value_dns_accel_debug_cache(self):
        cmd=commands.getstatusoutput('/home/ib_flex/IB/qa/cli_automation_security/FR/show_hw_type.exp ' +str(config.grid_member1_vip))
        log_level_6 = re.search(r'(Member hardware type):\s+(IB-FLEX+)', cmd[1]).group(2)
        print log_level_6
        #if re.search(log_level_6) == "IB-FLEX" :
        #  print "Found"
        '''  
        set_membership='/home/ib_flex/IB/qa/cli_automation_security/FR/set_membership.exp ' +str(config.grid_member1_vip)+'  '+str(config.grid_vip)
        os.system(set_membership)

         
        data={"host_name":config.grid_member1_fqdn,"vip_setting":{"address": config.grid_member1_vip,"dscp":0,"gateway": "10.35.0.1","primary":True,"subnet_mask":"255.255.0.0","use_dscp": False},"platform":"VNIOS","config_addr_type":"IPV4"}
        get_status = ib_NIOS.wapi_request('POST',object_type="member",fields=json.dumps(data))
        '''
        '''  
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
         
        search = 'IB-FLEX'
        for sublist in ref_123:
            print sublist[2]
            if sublist[1] == search:
               print "Found it!", sublist
               break
        ''' 






    '''
    @pytest.mark.run(order=1)
    def test_validate_log_value_dns_accel_debug_cache(self):
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
        except pexpect.TIMEOUT:
            print "Error" 
  
    '''
    @classmethod
    def teardown_class(cls):
        """ teardown any state that was previously setup with a call to
        setup_class.
        """
        logging.info("TEAR DOWN METHOD")   


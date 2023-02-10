import sys
#sys.path.insert(0, str(os.getenv("HOME"))+'/qa-xaas/main/api/janus/ngp/')
sys.path.insert(0,'/home/vadga-143/IB/qa/vadpga-143/FR/')
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
    def test_validate_validate_sid(self):
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
    def test_2_validate_validate_sid(self):
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

        
 
    @classmethod
    def teardown_class(cls):
        """ teardown any state that was previously setup with a call to
        setup_class.
        """
        logging.info("TEAR DOWN METHOD")   


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
    def test_get_log_value_dns_accel(self):
        cmd=commands.getstatusoutput('/home/cli_automation_security/IB/qa/cli_automation_security/FR/get_default_log_level.exp ' +str(config.grid_vip))
        #print cmd[1]
        #print re.search(r'(Log level):\s+6\(Info\)', cmd[1]).group(0)
        log_level_6 = re.search(r'(Log level):\s+6\(Info\)', cmd[1]).group(0)
        print log_level_6
        if log_level_6 == re.search(r'(Log level):\s+6\(Info\)', cmd[1]).group(0):
            logging.info("found")
        #print re.search(r'(Log level):\s+(6\(Info\))', cmd[1]).group(1)
        #print re.search(r'(Log level):\s+(6\(Info\))', cmd[1]).group(2)
        #sleep(120)
    
    @pytest.mark.run(order=2)
    def test_modify_and_validate_log_value_dns_accel(self):
        cmd2=commands.getstatusoutput('/home/cli_automation_security/IB/qa/cli_automation_security/FR/modify_default_log_level.exp ' +str(config.grid_vip))
        print cmd2[1]
        cmd3=commands.getstatusoutput('/home/cli_automation_security/IB/qa/cli_automation_security/FR/get_default_log_level.exp ' +str(config.grid_vip))  
        print cmd3[1]
        log_level_7 = re.search(r'(Log level):\s+7\(Debug\)', cmd3[1]).group(0)
        print log_level_7
        if log_level_7 == re.search(r'(Log level):\s+7\(Debug\)', cmd3[1]).group(0):
            logging.info("found") 
        #print re.search(r'(Log level):\s+6\(Info\)', cmd[1]).group(0)
 
    
    @classmethod
    def teardown_class(cls):
        """ teardown any state that was previously setup with a call to
        setup_class.
        """
        logging.info("TEAR DOWN METHOD")   


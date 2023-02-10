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
    def test_validate_log_value_dns_accel_debug_cache(self):
        cmd6=commands.getstatusoutput('/home/cli_automation_security/IB/qa/cli_automation_security/FR/ib_scripts/get_dns_accl_debug.exp ' +str(config.grid_vip))
        print cmd6[1]
        cache_response = re.search(r'(Cache response traffic capture):\s+(Enabled+)', cmd6[1]).group(0)
        print cache_response
        if cache_response == re.search(r'(Cache response traffic capture):\s+(Enabled+)', cmd6[1]).group(0):
            logging.info("found")
  
    
    @classmethod
    def teardown_class(cls):
        """ teardown any state that was previously setup with a call to
        setup_class.
        """
        logging.info("TEAR DOWN METHOD")   


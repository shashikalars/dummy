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
        cmd=commands.getstatusoutput('/home/cli_automation_security/IB/qa/cli_automation_security/FR/ib_scripts/get_default_log_level.exp ' +str(config.grid_vip))
        log_level_6 = re.search(r'(Log level):\s+6\(Info\)', cmd[1]).group(0)
        #print log_level_6
        if log_level_6 == re.search(r'(Log level):\s+6\(Info\)', cmd[1]).group(0):
            logging.info("found")
    
    @pytest.mark.run(order=2)
    def test_modify_and_validate_log_value_dns_accel(self):
        cmd2=commands.getstatusoutput('/home/cli_automation_security/IB/qa/cli_automation_security/FR/ib_scripts/modify_default_log_level.exp ' +str(config.grid_vip))
        #print cmd2[1]
        cmd3=commands.getstatusoutput('/home/cli_automation_security/IB/qa/cli_automation_security/FR/ib_scripts/get_default_log_level.exp ' +str(config.grid_vip))  
        print cmd3[1]
        log_level_7 = re.search(r'(Log level):\s+7\(Debug\)', cmd3[1]).group(0)
        #print log_level_7
        if log_level_7 == re.search(r'(Log level):\s+7\(Debug\)', cmd3[1]).group(0):
            logging.info("found") 
    
    @pytest.mark.run(order=3)
    def test_validate_log_value_dns_accel_debug_global(self):
        cmd4=commands.getstatusoutput('/home/cli_automation_security/IB/qa/cli_automation_security/FR/ib_scripts/get_dns_accl_debug.exp ' +str(config.grid_vip))
        print cmd4[1]
        log_level_global = re.search(r'(Global packet rate limit):\s+(\w+)', cmd4[1]).group(0)
        print log_level_global
        if log_level_global == re.search(r'(Global packet rate limit):\s+(\w+)', cmd4[1]).group(0):
            logging.info("found")
    

    @pytest.mark.run(order=4)
    def test_validate_log_value_dns_accel_debug_ttl(self):
        cmd5=commands.getstatusoutput('/home/cli_automation_security/IB/qa/cli_automation_security/FR/ib_scripts/get_dns_accl_debug.exp ' +str(config.grid_vip))
        print cmd5[1]
        log_level_ttl = re.search(r'(Maximum TTL in seconds):\s+(\d+)', cmd5[1]).group(0)
        print log_level_ttl
        if log_level_ttl == re.search(r'(Maximum TTL in seconds):\s+(\d+)', cmd5[1]).group(0):
            logging.info("found")

    
    @pytest.mark.run(order=5)
    def test_validate_log_value_dns_accel_debug_cache(self):
        cmd6=commands.getstatusoutput('/home/cli_automation_security/IB/qa/cli_automation_security/FR/ib_scripts/get_dns_accl_debug.exp ' +str(config.grid_vip))
        print cmd6[1]
        cache_response = re.search(r'(Cache response traffic capture):\s+(Enabled+)', cmd6[1]).group(0) 
        print cache_response
        if cache_response == re.search(r'(Cache response traffic capture):\s+(Enabled+)', cmd6[1]).group(0):
            logging.info("found")
   
    @pytest.mark.run(order=6)
    def test_modify_validate_log_value_dns_accel_debug_dsr_value_off(self):
        cmd7=commands.getstatusoutput('/home/cli_automation_security/IB/qa/cli_automation_security/FR/ib_scripts/modify_dns_accl_debug_dsr_off.exp ' +str(config.grid_vip))
        print cmd7[1]
        cmd9=commands.getstatusoutput('/home/cli_automation_security/IB/qa/cli_automation_security/FR/ib_scripts/get_dns_accl_debug.exp ' +str(config.grid_vip))
        print cmd9[1]
        debug_dsr_off = re.search(r'(Direct Server Return):\s+(Disabled+)', cmd9[1]).group(0)
        print debug_dsr_off
        if debug_dsr_off == re.search(r'(Direct Server Return):\s+(Disabled+)', cmd9[1]).group(0):
            logging.info("found")

    @pytest.mark.run(order=7)
    def test_modify_validate_log_value_dns_accel_debug_dsr_value_on(self):
        cmd10=commands.getstatusoutput('/home/cli_automation_security/IB/qa/cli_automation_security/FR/ib_scripts/modify_dns_accl_debug_dsr_on.exp ' +str(config.grid_vip))
        print cmd10[1]
    #   log_level_ttl = re.search(r'(Cache response traffic capture):\s+(\w+)', cmd6[1]).group(0)
        cmd11=commands.getstatusoutput('/home/cli_automation_security/IB/qa/cli_automation_security/FR/ib_scripts/get_dns_accl_debug.exp ' +str(config.grid_vip))
        print cmd11[1]
        debug_dsr_on = re.search(r'(Direct Server Return):\s+(Enabled+)', cmd11[1]).group(0)
        print debug_dsr_on
        if debug_dsr_on == re.search(r'(Direct Server Return):\s+(Enabled+)', cmd11[1]).group(0):
            logging.info("found")
   

    @pytest.mark.run(order=8)
    def test_modify_validate_dns_accel_debug_resp_packet_off(self):
        cmd12=commands.getstatusoutput('/home/cli_automation_security/IB/qa/cli_automation_security/FR/ib_scripts/modify_dns_accl_debug_response_packet_off.exp ' +str(config.grid_vip))
        print cmd12[1]
        cmd13=commands.getstatusoutput('/home/cli_automation_security/IB/qa/cli_automation_security/FR/ib_scripts/get_dns_accl_debug.exp ' +str(config.grid_vip))
        print cmd13[1]
        debug_response_packet = re.search(r'(Cache response traffic capture):\s+(Disabled+)', cmd13[1]).group(0)
        print debug_response_packet
        if debug_response_packet == re.search(r'(Cache response traffic capture):\s+(Disabled+)', cmd13[1]).group(0):
            logging.info("found")

    @pytest.mark.run(order=9)
    def test_modify_validate_log_value_dns_accel_debug_resp_packer_on(self):
        cmd14=commands.getstatusoutput('/home/cli_automation_security/IB/qa/cli_automation_security/FR/ib_scripts/modify_dns_accl_debug_response_packet_on.exp ' +str(config.grid_vip))
        print cmd14[1]
        cmd15=commands.getstatusoutput('/home/cli_automation_security/IB/qa/cli_automation_security/FR/ib_scripts/get_dns_accl_debug.exp ' +str(config.grid_vip))
        print cmd15[1]
        debug_response_packet = re.search(r'(Cache response traffic capture):\s+(Enabled+)', cmd15[1]).group(0)
        print debug_response_packet
        if debug_response_packet == re.search(r'(Cache response traffic capture):\s+(Enabled+)', cmd15[1]).group(0):
            logging.info("found")
 





    
    @classmethod
    def teardown_class(cls):
        """ teardown any state that was previously setup with a call to
        setup_class.
        """
        logging.info("TEAR DOWN METHOD")   


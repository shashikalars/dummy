# -*- coding: utf-8 -*-
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
import sys
#import ib_utils.ib_get as ib_get
from time import sleep
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="profiling.log" ,level=logging.DEBUG,filemode='w')


class ProfilingAutomation(unittest.TestCase):

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
    def test_1_add_profile_without_inherited(self):
        logging.info("-----------Test Case 1 Execution Started------------")
         
        logging.info("Validated Threat Protection Profile-Search for 'name' field")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[0]['_ref']
        print ref_1

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        print ref_version_1 
        ''' 
        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120304000\
        &ruleset=%s"%ref_version_1)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
	#print rule_temp_ref
	'''
	get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120300500\
        &ruleset=%s"%ref_version_1)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[0]['_ref']
        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
	
	for i in xrange(1,501):
	    #print rule_temp_ref
	    name12 = "white_udp_test"+str(i)+".com"
   	    add_custom_rule={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"PASS","log_severity":"WARNING","params":[{"name":"FQDN","value":name12},{"name": "EVENTS_PER_SECOND","value":"1"}]}}
            response = ib_NIOS.wapi_request('POST',object_type="threatprotection:grid:rule",fields=json.dumps(add_custom_rule))
	    print response	
	'''
        for i in xrange(6,2000): 
	    name12 = "black_udp"+str(i)+".com" 
            add_custom_rule={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"DROP",
            "log_severity":"WARNING","params":[{"name": "EVENTS_PER_SECOND","value":"1"},{"name":"FQDN","value":name12}]}}
            response = ib_NIOS.wapi_request('POST',object_type="threatprotection:grid:rule",fields=json.dumps(add_custom_rule))
        '''

    


    @classmethod
    def teardown_class(cls):
        """ teardown any state that was previously setup with a call to
        setup_class.
        """
        logging.info("TEAR DOWN METHOD")   


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
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="rfe-5924.log" ,level=logging.DEBUG,filemode='w')


class RFE5924_Automation(unittest.TestCase):

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
    def test_1_get_threat_protection_ruleset_validate_ruleset(self):
        logging.info('-'*30+"Test Case 1 Execution Started"+'-'*30)
        logging.info("Validated Threat Protection Rulset- Version Field")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version = json.loads(get_ruleset)[0]['version'] 
        ref_version_2 = json.loads(get_ruleset)[1]['version']
        for i in res:
            logging.info("found")
            assert i["version"] == ref_version  or i["version"] == ref_version_2
        logging.info('-'*30+"Test Case 1 Execution Completed"+'-'*30)    

    @pytest.mark.run(order=2)
    def test_2_get_threat_protection_ruleset_validate_add_type(self):
        logging.info('-'*30+"Test Case 2 Execution Started"+'-'*30)  
        logging.info("Validated Threat Protection Rulset- add_type Field")
        get_add_type = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_add_type)
        res = json.loads(get_add_type)
        add_type = json.loads(get_add_type)[0]['add_type']
        add_type_2 = json.loads(get_add_type)[1]['add_type']
        for i in res:
            logging.info("found")
            assert i["add_type"] == add_type  or i["add_type"] == add_type_2
        logging.info('-'*30+"Test Case 2 Execution Completed"+'-'*30) 

    @pytest.mark.run(order=3)
    def test_3_get_threat_protection_ruleset_validate_is_factory_field(self):
        logging.info('-'*30+"Test Case 3 Execution Started"+'-'*30)
        logging.info("Validated Threat Protection Rulset- is_factory_reset_enabled field")
        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ref)
        ref = json.loads(get_ref)[1]['_ref']
        get_status = ib_NIOS.wapi_request('GET', object_type = ref+'?_return_fields=is_factory_reset_enabled,do_not_delete')
        factory = json.loads(get_status)
        assert factory["is_factory_reset_enabled"] == True
        logging.info('-'*30+"Test Case 3 Execution Completed"+'-'*30)


    @pytest.mark.run(order=4)
    def test_4_get_threat_protection_ruleset_validate_do_not_delete(self):
        logging.info('-'*30+"Test Case 4 Execution Started"+'-'*30)
        logging.info("Validated Threat Protection Rulset- do_not_delete")
        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ref)
        ref = json.loads(get_ref)[1]['_ref']
        get_status = ib_NIOS.wapi_request('GET', object_type = ref+'?_return_fields=is_factory_reset_enabled,do_not_delete')
        factory = json.loads(get_status)
        assert factory["do_not_delete"] == False
        logging.info('-'*30+"Test Case 4 Execution Started"+'-'*30)   


    @pytest.mark.run(order=5)
    def test_5_get_threat_protection_ruleset_modify_validate_do_not_delete(self):
        logging.info('-'*30+"Test Case 5 Execution Started"+'-'*30)  
        logging.info("Modify and Validated Threat Protection Rulset- do_not_delete")
        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ref)
        ref1 = json.loads(get_ref)[1]['_ref']
        data={"do_not_delete":True}
        get_status = ib_NIOS.wapi_request('PUT', object_type = ref1,fields=json.dumps(data))
        logging.info("============================")
 
        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ref)
        ref2 = json.loads(get_ref)[1]['_ref']
 
        get_do_not_delete = ib_NIOS.wapi_request('GET', object_type = ref2+'?_return_fields=is_factory_reset_enabled,do_not_delete')
        factory = json.loads(get_do_not_delete)
        assert factory["do_not_delete"] == True
        logging.info('-'*30+"Test Case 5 Execution Completed"+'-'*30)  

    @pytest.mark.run(order=6)
    def test_6_get_threat_protection_ruleset_modify_validate_comment(self):
        logging.info('-'*30+"Test Case 6 Execution Started"+'-'*30)   
        logging.info("Modify and Validated Threat Protection Rulset- comment")
        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ref)
        ref1 = json.loads(get_ref)[1]['_ref']

        data={"comment":"modified_comment"}
        get_status = ib_NIOS.wapi_request('PUT', object_type = ref1,fields=json.dumps(data))

        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ref)
        ref2 = json.loads(get_ref)[1]['_ref']

        get_do_not_delete = ib_NIOS.wapi_request('GET', object_type = ref2+'?_return_fields=is_factory_reset_enabled,do_not_delete,comment')
        factory = json.loads(get_do_not_delete)
        assert factory["comment"] == "modified_comment"
        logging.info('-'*30+"Test Case 6 Execution Completed"+'-'*30)  


    @pytest.mark.run(order=7)
    def test_7_get_threat_protection_ruleset_modify_validate_do_not_delete(self):
        logging.info('-'*30+"Test Case 7 Execution Started"+'-'*30) 
        logging.info("Modify and Validated Threat Protection Rulset- do_not_delete")
        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ref)
        ref1 = json.loads(get_ref)[1]['_ref']
          
        data={"do_not_delete":False}
        get_status = ib_NIOS.wapi_request('PUT', object_type = ref1,fields=json.dumps(data))

        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ref)
        ref2 = json.loads(get_ref)[1]['_ref']
         
        get_do_not_delete = ib_NIOS.wapi_request('GET', object_type = ref2+'?_return_fields=is_factory_reset_enabled,do_not_delete')
        factory = json.loads(get_do_not_delete)
        logging.info(factory)
        assert factory["do_not_delete"] == False
        logging.info('-'*30+"Test Case 7 Execution Completed"+'-'*30)  


    @pytest.mark.run(order=8)
    def test_8_get_threat_protection_ruleset_search_version(self):
        logging.info('-'*30+"Test Case 8 Execution Started"+'-'*30)  
	logging.info("Validated Threat Protection Rulset- search object for version")
        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ref)

        version_1 = json.loads(get_ref)[1]['version']
        print version_1
        search_version = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset?version~=%s"%version_1)
        ref_51 = json.loads(search_version)[0]['_ref']

        res = json.loads(search_version)
        for i in res:
            logging.info("found")
            assert i["version"] == version_1
        logging.info('-'*30+"Test Case 8 Execution Completed"+'-'*30)  

    @pytest.mark.run(order=9)
    def test_9_get_threat_protection_ruleset_search_add_type(self):
        logging.info('-'*30+"Test Case 9 Execution Started"+'-'*30)
        logging.info("Validated Threat Protection Rulset- search object for add_type")
        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ref)


        add_type_1 = json.loads(get_ref)[1]['add_type']
        print add_type_1
        search_add_type = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset?add_type=%s"%add_type_1)
        ref_51 = json.loads(search_add_type)[0]['_ref']

        res = json.loads(search_add_type)
        logging.info(res)  
        for i in res:
            logging.info("found")
            assert i["add_type"] == add_type_1
        logging.info('-'*30+"Test Case 9 Execution Completed"+'-'*30) 
 
    @pytest.mark.run(order=10)
    def test_10_get_threat_protection_ruleset_search_add_type(self):
        logging.info('-'*30+"Test Case 10 Execution Started"+'-'*30)
        logging.info("Validated Threat Protection Rulset- search object for add_type")
        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ref)


        add_type_1 = json.loads(get_ref)[1]['add_type']
        print add_type_1
        search_add_type = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset?add_type=%s"%add_type_1)
        ref_51 = json.loads(search_add_type)[0]['_ref']

        res = json.loads(search_add_type)
        for i in res:
            logging.info("found")
            assert i["add_type"] == add_type_1
        logging.info('-'*30+"Test Case 10 Execution Completed"+'-'*30) 

    @pytest.mark.run(order=11)
    def test_11_get_member_threat_protection_ruleset_ipv4_ipv6(self):
        logging.info('-'*30+"Test Case 11 Execution Started"+'-'*30)
        logging.info("Validated Member Threat Protection ")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[0]['_ref']  
        get_status = ib_NIOS.wapi_request('GET', object_type = ref+'?_return_fields=ipv4address')  
        factory = json.loads(get_status)
        ref_ipv4_1 = factory['ipv4address']    
        assert factory["ipv4address"] == ref_ipv4_1

        res = json.loads(get_ref)
        ref = json.loads(get_ref)[1]['_ref']
        get_status = ib_NIOS.wapi_request('GET', object_type = ref+'?_return_fields=ipv4address')
        factory = json.loads(get_status)
        ref_ipv4_2 = factory['ipv4address']
        assert factory["ipv4address"] == ref_ipv4_1 or factory["ipv4address"] == ref_ipv4_2
        logging.info('-'*30+"Test Case 11 Execution Completed"+'-'*30) 


    @pytest.mark.run(order=12)
    def test_12_get_member_threat_protection_ruleset_ipv4_ipv6(self):
        logging.info('-'*30+"Test Case 12 Execution Started"+'-'*30)  
        logging.info("Validated Member Threat Protection ")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[0]['_ref']
        get_status = ib_NIOS.wapi_request('GET', object_type = ref+'?_return_fields=ipv6address')
        factory = json.loads(get_status)
        ref_ipv4_1 = factory['ipv6address']
        assert factory["ipv6address"] == ref_ipv4_1

        res = json.loads(get_ref)
        ref = json.loads(get_ref)[1]['_ref']
        get_status = ib_NIOS.wapi_request('GET', object_type = ref+'?_return_fields=ipv6address')
        factory = json.loads(get_status)
        ref_ipv4_2 = factory['ipv6address']
        assert factory["ipv6address"] == ref_ipv4_1 or factory["ipv6address"] == ref_ipv4_2
        logging.info('-'*30+"Test Case 12 Execution Completed"+'-'*30)    
 
    @pytest.mark.run(order=13)
    def test_13_get_member_threat_protection_ruleset_version(self):
        logging.info('-'*30+"Test Case 13 Execution Started"+'-'*30)
        logging.info("Modify and Validate current ruleset field for Member Threat Protection")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[0]['_ref']
        ref1 = json.loads(get_ref)[0]['_ref']

        logging.info("Get Threat Protection Rulset- Version Field")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']

        data={"current_ruleset":ref_version}  
        get_status = ib_NIOS.wapi_request('PUT',object_type = ref,fields=json.dumps(data))
        logging.info('-'*30+"Test Case 13 Execution Completed"+'-'*30)
       
    @pytest.mark.run(order=14)
    def test_14_update_use_current_ruleset_as_false_for_ruleset(self):
        sleep(60)
        logging.info('-'*30+"Test Case 14 Execution Started"+'-'*30)  
        logging.info("Modify and Validate current ruleset field for Member Threat Protection override version")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[0]['_ref']
        ref1 = json.loads(get_ref)[0]['_ref']

        logging.info("Get Threat Protection Rulset- Version Field")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']

        data={"use_current_ruleset":False}
        get_status = ib_NIOS.wapi_request('PUT',object_type = ref,fields=json.dumps(data))
        logging.info('-'*30+"Test Case 14 Execution Started"+'-'*30)

    @pytest.mark.run(order=15)
    def test_15_get_ruleset_override_events_per_second_per_rule(self):
        logging.info('-'*30+"Test Case 15 Execution Started"+'-'*30)   
        logging.info("Modify and Validate current event per second rule and use_event_per_second_rule")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[0]['_ref']
        ref1 = json.loads(get_ref)[0]['_ref']

        logging.info("Get Threat Protection Rulset- Version Field")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)

        data={"events_per_second_per_rule": 29,"use_events_per_second_per_rule":True}
        get_status = ib_NIOS.wapi_request('PUT',object_type = ref,fields=json.dumps(data))
        logging.info('-'*30+"Test Case 15 Execution Completed"+'-'*30)  
    
    @pytest.mark.run(order=16)
    def test_16_get_member_threat_protection_ruleset_version_override(self):
        logging.info('-'*30+"Test Case 16 Execution Started"+'-'*30)
        logging.info("Modify and Validate current event per second rule and use_event_per_second_rule to inherit grid properties")
        sleep(30)  
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[0]['_ref']
        ref1 = json.loads(get_ref)[0]['_ref']

        logging.info("Get Threat Protection Rulset- Version Field")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        logging.info(res)      
        data={"use_events_per_second_per_rule":False}
        get_status = ib_NIOS.wapi_request('PUT',object_type = ref,fields=json.dumps(data))
        logging.info(get_status)
        logging.info('-'*30+"Test Case 16 Execution Started"+'-'*30) 
    
    @pytest.mark.run(order=17)
    def test_17_get_member_threat_protection_ruleset_version_override(self):
        logging.info('-'*30+"Test Case 17 Execution Started"+'-'*30)  
        logging.info("Modify and Validate current event per second rule and use_event_per_second_rule to inherit grid properties")
        sleep(30)
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[0]['_ref']
        #print ref

        ref1 = json.loads(get_ref)[0]['_ref']
        #print ref1

        data={"enable_nat_rules":True,"nat_rules":[{"address": "20.0.0.8","nat_ports": [{"block_size": 100,"end_port": 1500,"start_port": 1000}],"rule_type": "ADDRESS"}]}
        get_status = ib_NIOS.wapi_request('PUT',object_type = ref,fields=json.dumps(data))
        logging.info('-'*30+"Test Case 17 Execution Completed"+'-'*30)      
  
    @pytest.mark.run(order=18)
    def test_18_grid_threat_protection_enable_nat_address(self):
        logging.info('-'*30+"Test Case 18 Execution Started"+'-'*30)
        logging.info("Modify and Validate Enable NAT Rule under Grid Security Properties")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[0]['_ref']

        ref1 = json.loads(get_ref)[0]['_ref']

        data={"enable_nat_rules":True,"nat_rules":[{"address": "20.0.0.8","nat_ports": [{"block_size": 100,"end_port": 1500,"start_port": 1000}],"rule_type": "ADDRESS"}]}
        get_status = ib_NIOS.wapi_request('PUT',object_type = ref,fields=json.dumps(data))

        get_ref_1 = ib_NIOS.wapi_request('GET', object_type="grid:threatprotection")
        logging.info(get_ref_1)
        res1 = json.loads(get_ref_1)
        ref1 = json.loads(get_ref_1)[0]['_ref']

        get_enable_nat_rules = ib_NIOS.wapi_request('GET', object_type = ref1+'?_return_fields=enable_nat_rules,nat_rules')
        factory = json.loads(get_enable_nat_rules)
        assert factory["enable_nat_rules"] == True

        ref_ipv4_1 = factory['nat_rules']
        #print ref_ipv4_1

        flag = False
        for i in ref_ipv4_1:
            if i["rule_type"] == "ADDRESS" :
                print "FOUND"
                flag = True
                break
        assert flag == True
        logging.info('-'*30+"Test Case 18 Execution Completed"+'-'*30) 

    @pytest.mark.run(order=19)
    def test_19_grid_threat_protection_disable_nat_address(self):
        logging.info('-'*30+"Test Case 19 Execution Started"+'-'*30)
        logging.info("Modify and Validate current Enable NAT Rule for NETWORK under Grid Security Properties")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[0]['_ref']

        data={"enable_nat_rules":False}
        get_status = ib_NIOS.wapi_request('PUT',object_type = ref,fields=json.dumps(data))

        get_ref_1 = ib_NIOS.wapi_request('GET', object_type="grid:threatprotection")
        logging.info(get_ref_1)
        res1 = json.loads(get_ref_1)
        ref1 = json.loads(get_ref_1)[0]['_ref']


        get_enable_nat_rules = ib_NIOS.wapi_request('GET', object_type = ref1+'?_return_fields=enable_nat_rules')
        factory = json.loads(get_enable_nat_rules)
        assert factory["enable_nat_rules"] == False
        logging.info('-'*30+"Test Case 19 Execution Started"+'-'*30)
 
    @pytest.mark.run(order=20)
    def test_20_grid_threat_protection_enable_nat_network(self):
        sleep(30)
        logging.info('-'*30+"Test Case 20 Execution Started"+'-'*30)
        logging.info("Modify and Validate current event per second rule and use_event_per_second_rule to inherit grid properties")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[0]['_ref']

        ref1 = json.loads(get_ref)[0]['_ref']

        data={"enable_nat_rules":True,"nat_rules":[{"cidr":8,"nat_ports":[{"block_size":200,"end_port":1400,"start_port":1200}],"network":"30.0.0.0","rule_type":"NETWORK"}]}
        get_status = ib_NIOS.wapi_request('PUT',object_type = ref,fields=json.dumps(data))

        get_ref_1 = ib_NIOS.wapi_request('GET', object_type="grid:threatprotection")
        logging.info(get_ref_1)
        res1 = json.loads(get_ref_1)
        ref1 = json.loads(get_ref_1)[0]['_ref']

        get_enable_nat_rules = ib_NIOS.wapi_request('GET', object_type = ref1+'?_return_fields=enable_nat_rules,nat_rules')
        factory = json.loads(get_enable_nat_rules)
        logging.info(factory)     
        assert factory["enable_nat_rules"] == True

        ref_ipv4_1 = factory['nat_rules']

        flag = False
        for i in ref_ipv4_1:
            if i["rule_type"] == "NETWORK" :
                print "FOUND"
                flag = True
                break
        assert flag == True
        logging.info('-'*30+"Test Case 20 Execution Completed"+'-'*30) 
 


    @pytest.mark.run(order=21)
    def test_21_grid_threat_protection_disable_nat_network(self):
        sleep(30)
        logging.info('-'*30+"Test Case 21 Execution Started"+'-'*30) 
        logging.info("Modify and Validate current event per second rule and use_event_per_second_rule to inherit grid properties")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[0]['_ref']

        data={"enable_nat_rules":False}
        get_status = ib_NIOS.wapi_request('PUT',object_type = ref,fields=json.dumps(data))

        get_ref_1 = ib_NIOS.wapi_request('GET', object_type="grid:threatprotection")
        logging.info(get_ref_1)
        res1 = json.loads(get_ref_1)
        ref1 = json.loads(get_ref_1)[0]['_ref']

        
        get_enable_nat_rules = ib_NIOS.wapi_request('GET', object_type = ref1+'?_return_fields=enable_nat_rules')
        factory = json.loads(get_enable_nat_rules)
        assert factory["enable_nat_rules"] == False
        logging.info('-'*30+"Test Case 21 Execution Completed"+'-'*30)

    @pytest.mark.run(order=22)
    def test_22_grid_threat_protection_enable_nat_all(self):
        logging.info('-'*30+"Test Case 22 Execution Started"+'-'*30)
        sleep(15)
        logging.info("Modify and Validate NAT Rule with ALL for Grid Security Properties")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[0]['_ref']

        data={"enable_nat_rules":True,"nat_rules":[{"end_address":"50.0.0.250","nat_ports":[{"block_size":200,"end_port":1600,"start_port":1300},{"block_size":100,"end_port":1800,"start_port":1700}],"start_address":"50.0.0.1","rule_type":"RANGE"},{"cidr":8,"nat_ports":[{"block_size":200,"end_port":1400,"start_port":1200}],"network":"30.0.0.0","rule_type":"NETWORK"},{"address":"10.0.0.8","nat_ports":[{"block_size":100,"end_port":1500,"start_port":1000}],"rule_type":"ADDRESS"}]}
        get_status = ib_NIOS.wapi_request('PUT',object_type = ref,fields=json.dumps(data))

        get_ref_1 = ib_NIOS.wapi_request('GET', object_type="grid:threatprotection")
        logging.info(get_ref_1)
        res1 = json.loads(get_ref_1)
        ref1 = json.loads(get_ref_1)[0]['_ref']


        get_enable_nat_rules = ib_NIOS.wapi_request('GET', object_type = ref1+'?_return_fields=enable_nat_rules,nat_rules')
        factory = json.loads(get_enable_nat_rules)
        assert factory["enable_nat_rules"] == True

        ref_ipv4_1 = factory['nat_rules']
        flag = False
        for i in ref_ipv4_1:
            if i["rule_type"] == "RANGE" :
                print "FOUND"
                flag = True
                break
        assert flag == True
        logging.info('-'*30+"Test Case 22 Execution Completed"+'-'*30)  

    @pytest.mark.run(order=23)
    def test_23_grid_threat_protection_disable_nat_all(self):
        logging.info('-'*30+"Test Case 23 Execution Started"+'-'*30)
        logging.info("Modify and Validate NAT Rule with ALL for Grid Security Properties")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[0]['_ref']

        data={"enable_nat_rules":False}
        get_status = ib_NIOS.wapi_request('PUT',object_type = ref,fields=json.dumps(data))
        get_ref_1 = ib_NIOS.wapi_request('GET', object_type="grid:threatprotection")
        logging.info(get_ref_1)
        res1 = json.loads(get_ref_1)
        ref1 = json.loads(get_ref_1)[0]['_ref']


        get_enable_nat_rules = ib_NIOS.wapi_request('GET', object_type = ref1+'?_return_fields=enable_nat_rules')
        factory = json.loads(get_enable_nat_rules)
        logging.info(factory)
        assert factory["enable_nat_rules"] == False
        logging.info('-'*30+"Test Case 23 Execution Completed"+'-'*30)  

    @pytest.mark.run(order=24)
    def test_24_grid_threat_protection_disable_nat_rules_values(self):
        logging.info('-'*30+"Test Case 24 Execution Started"+'-'*30)
        logging.info("Modify and Validate Disable NAT Values  to inherit grid properties")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[0]['_ref']

        ref1 = json.loads(get_ref)[0]['_ref']

        data={"enable_nat_rules":True,"nat_rules":[]}
        get_status = ib_NIOS.wapi_request('PUT',object_type = ref,fields=json.dumps(data))

        get_enable_nat_rules = ib_NIOS.wapi_request('GET', object_type = ref1+'?_return_fields=enable_nat_rules,nat_rules')
        factory = json.loads(get_enable_nat_rules)
        assert factory["enable_nat_rules"] == True
        logging.info('-'*30+"Test Case 24 Execution Completed"+'-'*30)   
   
    @pytest.mark.run(order=25)
    def test_25_grid_threat_protection_disable_nat_rules(self):
        logging.info('-'*30+"Test Case 25 Execution Started"+'-'*30) 
        logging.info("Modify and Validate Disable NAT Values  to inherit grid properties")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[0]['_ref']

        ref1 = json.loads(get_ref)[0]['_ref']

        data={"enable_nat_rules":False,"nat_rules":[]}
        get_status = ib_NIOS.wapi_request('PUT',object_type = ref,fields=json.dumps(data))

        get_enable_nat_rules = ib_NIOS.wapi_request('GET', object_type = ref1+'?_return_fields=enable_nat_rules,nat_rules')
        factory = json.loads(get_enable_nat_rules)
        assert factory["enable_nat_rules"] == False
        logging.info('-'*30+"Test Case 25 Execution Completed"+'-'*30) 

    @pytest.mark.run(order=26)
    def test_26_member_statistics_grid(self):
        logging.info('-'*30+"Test Case 26 Execution Started"+'-'*30)  
        logging.info("Get threatprotection statistics details at Grid level")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:statistics")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_1 = json.loads(get_ruleset)[0]['_ref']

        get_version = ib_NIOS.wapi_request('GET', object_type="threatprotection:statistics"+'?_return_fields=member,stat_infos')
        factory = json.loads(get_version)
        logging.info('-'*30+"Test Case 26 Execution Started"+'-'*30) 
        #ref  = json.loads(get_version)[0]['_ref']
        #stat = json.loads(get_version)[0]['stat_infos']


    @pytest.mark.run(order=27)
    def test_27_search_member_for_statistics(self):
        logging.info('-'*30+"Test Case 27 Execution Started"+'-'*30)
        logging.info("Validated Threat Protection member Statistics for 'member' field")
        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:statistics")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[0]['_ref']
        print ref_1

        get_status = ib_NIOS.wapi_request('GET', object_type="threatprotection:statistics?member=%s"%config.grid_member1_fqdn)
        factory = json.loads(get_status)
        print factory
        assert factory[0]['member'] == config.grid_member1_fqdn
        logging.info('-'*30+"Test Case 27 Execution Completed"+'-'*30)  

    @pytest.mark.run(order=28)
    def test_28_add_custom_rule_blacklist_fqdn_lookup(self):
        logging.info('-'*30+"Test Case 28 Execution Started"+'-'*30)  
        logging.info("Validated Threat Protection Profile-Search for 'name' field")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']


        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120303000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        logging.info(rule_temp_ref)
        add_custom_rule={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"DROP",
        "log_severity":"WARNING","params":[{"name": "EVENTS_PER_SECOND","value":"1"},{"name":"FQDN","value":"black_udp.com"}]}}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:grid:rule",fields=json.dumps(add_custom_rule))
        logging.info(response)
        sleep(10)
        logging.info("Perform Publish Operation")   
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(120)
 
 

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Blacklist:black_udp.com')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
        assert custom_rule[0]["name"] == "Blacklist:black_udp.com"
        logging.info('-'*30+"Test Case 28 Execution Completed"+'-'*30)
 
    @pytest.mark.run(order=29)
    def test_29_validate_sid_in_rules_txt_file_validate_functionality_of_added_blacklist_udp_fqdn_type_rule(self):   
        logging.info('-'*30+"Test Case 29 Execution Started"+'-'*30)
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Blacklist:black_udp.com')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
        logging.info("Validate SID Value in rules.txt file")    
        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        logging.info(out)  
        assert re.search(r'sid\:'+str(sid_value)+'',out)


        dig_cmd = 'dig @'+str(config.grid_member2_vip)+' black_udp.com +time=0 +retries=0'
        os.system(dig_cmd)
           
        logging.info("Validating Syslog after performing Queries")
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " tail -200 /var/log/syslog | grep -ir \'BLACKLIST .*\' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        logging.info(out1) 
        assert re.search(r''+str(sid_value)+'|Blacklist:black_udp\.com.*cat\=\"BLACKLIST.*\"',out1)
        logging.info('-'*30+"Test Case 29 Execution Completed"+'-'*30) 
       
    @pytest.mark.run(order=30)
    def test_30_put_blacklist_udp_fqdn_type_for_custom_rule_name_negative_case(self):
        logging.info('-'*30+"Test Case 30 Execution Started"+'-'*30)
        logging.info('-'*30+"Performed Get Operation for member:threatprotection"+'-'*30)
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']


        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120303000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        logging.info(rule_temp_ref)

        data={"name":"BLACKLIST DROP"}
        status,modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1_temp,fields=json.dumps(data))
        logging.info(modify_disable_field)
        assert status == 400
        print modify_disable_field
        logging.info('-'*30+"Test Case 30 Execution Completed"+'-'*30)  

    @pytest.mark.run(order=31)
    def test_31_update_disable_field_as_true_for_blacklist_udp_fqdn(self):
        logging.info('-'*30+"Test Case 31 Execution Started"+'-'*30)
        logging.info('-'*15+"Modify Disable field for custom rule with value as true"+'-'*15)
        logging.info('-'*15+"Get ThreatProtection Grid rule for Blacklist"+'-'*15)
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name=Blacklist:black_udp.com')
        factory = json.loads(get_custom_rule)
        logging.info(factory)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2

        logging.info('-'*15+"Perform Modify operation for disable field as True"+'-'*15)    
        data={"disabled":True}
        modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_disable_field)
        print modify_disable_field

        get_ref_after_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_after_disable
        logging.info(get_ref_after_disable)
        ref_2 = json.loads(get_ref_after_disable)['disabled']
        print ref_2

        validate = json.loads(get_ref_after_disable)
        assert validate["disabled"] == ref_2
        logging.info('-'*30+"Test Case 31 Execution Completed"+'-'*30)
        sleep(10)

    @pytest.mark.run(order=32)
    def test_32_update_disable_field_as_false_for__blacklist_udp_fqdn_type(self):
        logging.info('-'*30+"Test Case 32 Execution Started"+'-'*30)
        logging.info('-'*15+"Modify Disable field for custom rule with value as true"+'-'*15)
        logging.info('-'*15+"Get Custom rule in Grid Level"+'-'*15)
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name=Blacklist:black_udp.com')
        factory = json.loads(get_custom_rule)
        logging.info(factory)  
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2

        logging.info('-'*15+"Perform Modify Operation for Disable field as False "+'-'*15)
        data={"disabled":False}
        modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_disable_field)
        print modify_disable_field
        sleep(10)
        get_ref_after_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_after_disable
        logging.info(get_ref_after_disable)
        ref_2 = json.loads(get_ref_after_disable)['disabled']
        print ref_2

        validate = json.loads(get_ref_after_disable)
        assert validate["disabled"] == ref_2
        logging.info('-'*30+"Test Case 32 Execution Completed"+'-'*30)

    
    @pytest.mark.run(order=33)
    def test_33_update_log_severity_value_and_name_in_black_udp_fqdn_lookup(self):
        logging.info('-'*30+"Test Case 33 Execution Started"+'-'*30)
        logging.info('-'*30+"Modify Log Severity and FQDN Values in Custom Rule(BlackList FQDN Lookup)"+'-'*30)
        logging.info("Get ThreatProtection Grid rule for Blacklist")
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name=Blacklist:black_udp.com')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1
        sid_value=  json.loads(get_custom_rule)[0]['sid']
        print sid_value

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2
        

        data={"config":{"action": "DROP","log_severity": "MAJOR","params": [{"name": "FQDN","value": "black_udp_modified.com"}]}}
        modify_drop_field = ib_NIOS.wapi_request('PUT',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field
        
        logging.info("Perform Publish Operation") 
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(120)  
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name=Blacklist:black_udp_modified.com')
        factory = json.loads(get_custom_rule)
        ref_modified = json.loads(get_custom_rule)[0]['_ref']
        print ref_modified

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_modified+'?_return_fields=disabled,name,config')
        print get_ref_disable

        validate = json.loads(get_ref_disable)
        print validate
        ref_ipv4_1 = validate['config']
        print ref_ipv4_1
        assert factory[0]["name"] == "Blacklist:black_udp_modified.com"
        logging.info('-'*30+"Test Case 33 Execution Started"+'-'*30)

    
    @pytest.mark.run(order=34)
    def test_34_validate_sid_in_rules_txt_file_and_validated_functionality_of_modified_blacklist_udp_fqdn_type(self):    
        logging.info('-'*30+"Test Case 34 Execution Started"+'-'*30)
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name=Blacklist:black_udp_modified.com')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1
        sid_value=  json.loads(get_custom_rule)[0]['sid']
        print sid_value 

        logging.info("Validating SID Value in rules.txt file")  
        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        logging.info(out) 
        assert re.search(r'sid\:'+str(sid_value)+'',out)

        logging.info("Perform dig command")  
        dig_cmd = 'dig @'+str(config.grid_member2_vip)+' black_udp_modified.com +time=0 +retries=0'
        os.system(dig_cmd)

        logging.info("Validate Syslog afer perform queries")  
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " tail -200 /var/log/syslog | grep -ir \'BLACKLIST .*\' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        logging.info(out1)  
        assert re.search(r''+str(sid_value)+'|Blacklist:black_udp_modified\.com.*cat\=\"BLACKLIST.*\"',out1)
        logging.info('-'*30+"Test Case 34 Execution Completed"+'-'*30)
    


    @pytest.mark.run(order=35)
    def test_35_delete_custom_rule_blacklist_udp_fqdn(self):
        logging.info('-'*30+"Test Case 35 Execution Started"+'-'*30)
        logging.info('-'*30+"Delete custom rule for Blacklist UDP FQDN lookup"'-'*30)
        logging.info('-'*15+"Get ThreatProtection Grid rule for Blacklist"'-'*15)
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name=Blacklist:black_udp_modified.com')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2


        data={"name":"Blacklist:black_udp_modified.com"}
        modify_drop_field = ib_NIOS.wapi_request('DELETE',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field
        sleep(10)   
        logging.info('-'*30+"Test Case 35 Execution Completed"+'-'*30)

    @pytest.mark.run(order=36)
    def test_36_add_custom_blacklist_tcp_fqdn(self):
        logging.info('-'*30+"Test Case 36 Execution Started"+'-'*30)
        logging.info("Validated Threat Protection Profile-Search for 'name' field")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']


        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120304000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        logging.info(rule_temp_ref)
        add_custom_rule={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"DROP","log_severity":"WARNING","params":[{"name": "EVENTS_PER_SECOND","value":"1"},{"name":"FQDN","value":"black_tcp.com"}]}}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:grid:rule",fields=json.dumps(add_custom_rule))
        logging.info(response)

        sleep(10)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)
        


        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Blacklist:black_tcp.com')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value  
        assert custom_rule[0]["name"] == "Blacklist:black_tcp.com"
        logging.info('-'*30+"Test Case 36 Execution Completed"+'-'*30)
  

    @pytest.mark.run(order=37)
    def test_37_validate_sid_in_rules_txt_file_and_validated_functionality_of_added_blacklist_tcp_fqdn_type(self): 
        logging.info('-'*30+"Test Case 37 Execution started"+'-'*30) 
        logging.info("Validating SID in rules.txt file") 
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Blacklist:black_tcp.com')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value

        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        logging.info(out)  
        assert re.search(r'sid\:'+str(sid_value)+'',out)

        logging.info("Perform Dig Command")     
        dig_cmd = 'dig @'+str(config.grid_member2_vip)+' black_tcp.com +tcp +time=0 +retries=0'
        os.system(dig_cmd)

        logging.info("Validate Syslog after Performing Queries")  
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " tail -20 /var/log/syslog | grep -ir \'BLACKLIST .*\' " '
        out1 = commands.getoutput(sys_log_validation)
        logging.info(out1)
        print out1
        assert re.search(r''+str(sid_value)+'|Blacklist:black_tcp\.com.*cat\=\"BLACKLIST.*\"',out1)
    
        logging.info('-'*30+"Test Case 37 Execution Completed"+'-'*30)


    @pytest.mark.run(order=38)
    def test_38_update_blacklist_tcp_fqdn_type_name_negative_case(self):
        logging.info('-'*30+"Test Case 38 Execution Started"+'-'*30)
        logging.info('-'*15+"Performed Get Operation for member:threatprotection"+'-'*15)
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']


        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120304000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        logging.info(rule_temp_ref)

        data={"name":"BLACKLIST DROP"}
        status,modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1_temp,fields=json.dumps(data))
        logging.info(modify_disable_field)
        assert status == 400
        print modify_disable_field
        logging.info('-'*30+"Test Case 38 Execution Completed"+'-'*30)

    @pytest.mark.run(order=39)
    def test_39_update_disable_field_false_for_custom_rule(self):
        logging.info('-'*30+"Test Case 39 Execution Started"+'-'*30)
        logging.info("Modify Disable field for custom rule with value as true")


        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Blacklist:black_tcp.com')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        custom_name = custom_rule[0]['name']
        print custom_name
        #print ref_2
        ref_1 = custom_rule[0]['_ref']
        print ref_1


        data={"disabled":False}
        modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1,fields=json.dumps(data))
        logging.info(modify_disable_field)
        print modify_disable_field

        get_custom_rule_ref = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Blacklist:black_tcp.com')
        custom_rule_2=json.loads(get_custom_rule)
        custom_ref = custom_rule[0]['_ref']
        print custom_ref


        get_ref_after_disable = ib_NIOS.wapi_request('GET', object_type = custom_ref+'?_return_fields=disabled')
        #print get_ref_after_disable
        custom_rule_3=json.loads(get_ref_after_disable)
        logging.info(get_ref_after_disable)
        print get_ref_after_disable
        disable_field = custom_rule_3['disabled']
        print disable_field

        assert custom_rule_3["disabled"] == False
        logging.info('-'*30+"Test Case 39 Execution Completed"+'-'*30)


    @pytest.mark.run(order=40)
    def test_40_update_log_severity_and_fqdn_for_blacklist_tcp_fqdn_type(self):
        logging.info('-'*30+"Test Case 40 Execution Started"+'-'*30)
        logging.info('-'*15+"Modify Log Severity and FQDN Values in Custom Rule(BlackList TCP FQDN Lookup)"+'-'*15)
        logging.info("Get ThreatProtection Grid rule for Blacklist")
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name=Blacklist:black_tcp.com')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2


        data={"config":{"action": "DROP","log_severity": "MAJOR","params": [{"name": "FQDN","value": "black_tcp_modified.com"}]}}
        modify_drop_field = ib_NIOS.wapi_request('PUT',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field

        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(30)
 

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name,config')
        print get_ref_disable

        validate = json.loads(get_ref_disable)
        print validate
        ref_ipv4_1 = validate['config']
        print ref_ipv4_1

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Blacklist:black_tcp_modified.com')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
        assert custom_rule[0]["name"] == "Blacklist:black_tcp_modified.com"
        logging.info('-'*30+"Test Case 40 Execution Completed"+'-'*30)   


    @pytest.mark.run(order=41)
    def test_41_validate_sid_in_rules_txt_file_and_validated_functionality_of_modified_blacklist_tcp_fqdn_type(self):     
        logging.info('-'*30+"Test Case 41 Execution Started"+'-'*30)
        logging.info("Validating SID in rules.txt")
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Blacklist:black_tcp_modified.com')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        logging.info(out)   
        assert re.search(r'sid\:'+str(sid_value)+'',out)

        logging.info("Perform Queries")   
        dig_cmd = 'dig @'+str(config.grid_member2_vip)+' black_tcp_modified.com +tcp +time=0 +retries=0'
        os.system(dig_cmd)

        logging.info("Validating Syslog After Performing Queries")
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " tail -200 /var/log/syslog | grep -ir \'BLACKLIST .*\' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        logging.info(out1)
        assert re.search(r''+str(sid_value)+'|Blacklist:black_tcp_modified\.com.*cat\=\"BLACKLIST.*\"',out1)

        logging.info('-'*30+"Test Case 41 Execution Completed"+'-'*30)


    @pytest.mark.run(order=42)
    def test_42_delete_custom_rule_blacklist_tcp_fqdn(self):
        logging.info('-'*30+"Test Case 42 Execution Started"+'-'*30)
        logging.info('-'*30+"Delete custom rule for Blacklist TCP FQDN lookup"'-'*30)
        logging.info('-'*15+"Get ThreatProtection Grid rule for Blacklist"'-'*15)
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name=Blacklist:black_tcp_modified.com')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2


        data={"name":"Blacklist:black_tcp_modified.com"}
        modify_drop_field = ib_NIOS.wapi_request('DELETE',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field

        logging.info('-'*30+"Test Case 42 Execution Completed"+'-'*30)
    
    @pytest.mark.run(order=43)
    def test_43_add_whitelist_tcp_fqdn(self):
        logging.info('-'*30+"Test Case 43 Execution Started"+'-'*30)
        logging.info("Validated Threat Protection Profile-Search for 'name' field")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']

        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120300000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)

        add_custom_rule={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"PASS","log_severity":"WARNING","params":[{"name":"FQDN","value":"white_test.com"},{"name": "EVENTS_PER_SECOND","value":"1"}]}}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:grid:rule",fields=json.dumps(add_custom_rule))
        logging.info(response)
        sleep(10)

        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)   


        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Whitelist:white_test.com')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value

        assert custom_rule[0]["name"] == "Whitelist:white_test.com"
        logging.info('-'*30+"Test Case 43 Execution Completed"+'-'*30)

    @pytest.mark.run(order=44)
    def test_44_validate_sid_in_rules_txt_file_and_validated_functionality_of_added_whitelist_tcp_fqdn_type(self):
        logging.info('-'*30+"Test Case 44 Execution Started"+'-'*30)    
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Whitelist:white_test.com')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value

        logging.info("Validating SID in rules.txt")   
        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        logging.info(out)
        assert re.search(r'sid\:'+str(sid_value)+'',out)

        logging.info("Performing Queries") 
        dig_cmd = 'dig @'+str(config.grid_member2_vip)+' +tcp white_test.com +time=0 +retries=0'
        os.system(dig_cmd)
        logging.info('-'*30+"Test Case 44 Execution Completed"+'-'*30)

          
    @pytest.mark.run(order=45)
    def test_45_update_whitelist_tcp_fqdn_name_negative_case(self):
        logging.info('-'*30+"Test Case 45 Execution Started"+'-'*30)
        logging.info('-'*15+"Performed Get Operation for member:threatprotection"+'-'*15)
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']


        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120300000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        logging.info(rule_temp_ref)

        data={"name":"BLACKLIST DROP"}
        status,modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1_temp,fields=json.dumps(data))
        logging.info(modify_disable_field)
        assert status == 400
        print modify_disable_field
        logging.info('-'*30+"Test Case 45 Execution Completed"+'-'*30)
    
    @pytest.mark.run(order=46)
    def test_46_update_disable_field_false_for_custom_rule(self):
        logging.info('-'*30+"Test Case 46 Execution Started"+'-'*30)
        logging.info("Modify Disable field for custom rule with value as true")

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Whitelist:white_test.com')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        custom_name = custom_rule[0]['name']
        print custom_name
        #print ref_2
        ref_1 = custom_rule[0]['_ref']
        print ref_1

        data={"disabled":False}
        modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1,fields=json.dumps(data))
        logging.info(modify_disable_field)
        print modify_disable_field

        get_custom_rule_ref = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Whitelist:white_test.com')
        custom_rule_2=json.loads(get_custom_rule)
        custom_ref = custom_rule[0]['_ref']
        print custom_ref


        get_ref_after_disable = ib_NIOS.wapi_request('GET', object_type = custom_ref+'?_return_fields=disabled')
        #print get_ref_after_disable
        custom_rule_3=json.loads(get_ref_after_disable)
        logging.info(get_ref_after_disable)
        print get_ref_after_disable
        disable_field = custom_rule_3['disabled']
        print disable_field
        sleep(10)

        assert custom_rule_3["disabled"] == False
        logging.info('-'*30+"Test Case 46 Execution Completed"+'-'*30)    
    
    @pytest.mark.run(order=47) 
    def test_47_update_log_severity_and_fqdn_for_whitelist_tcp_fqdn(self):
        logging.info('-'*30+"Test Case 47 Execution Started"+'-'*30)
        logging.info('-'*15+"Modify Log Severity and FQDN Values in Custom Rule(Whitelist TCP Domain)"+'-'*15)
        logging.info("Get ThreatProtection Grid rule for Blacklist")
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name=Whitelist:white_test.com')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2

        data={"config":{"action":"PASS","log_severity":"MAJOR","params":[{"name":"FQDN","value":"white_test_modified.com"},{"name": "EVENTS_PER_SECOND","value":"10"}]}}
        modify_drop_field = ib_NIOS.wapi_request('PUT',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        sleep(10) 
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        logging.info("Publish Triggered") 
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(30)

  
        print modify_drop_field

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name,config')
        print get_ref_disable

        validate = json.loads(get_ref_disable)
        print validate
        ref_ipv4_1 = validate['config']
        print ref_ipv4_1

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Whitelist:white_test_modified.com')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value   
        assert custom_rule[0]["name"] == "Whitelist:white_test_modified.com"
        logging.info('-'*30+"Test Case 47 Execution Completed"+'-'*30)

    @pytest.mark.run(order=48)
    def test_48_validate_sid_in_rules_txt_file_and_validated_functionality_of_modified_whitelist_tcp_fqdn_type(self):
        logging.info('-'*30+"Test Case 48 Execution Started"+'-'*30)
        logging.info("Validate Rules.txt File")
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Whitelist:white_test_modified.com')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value 
        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        logging.info(out)
        assert re.search(r'sid\:'+str(sid_value)+'',out)


        dig_cmd = 'dig @'+str(config.grid_member2_vip)+' white_test_modified.com +tcp +time=0 +retries=0'
        os.system(dig_cmd)
        logging.info('-'*30+"Test Case 48 Execution Completed"+'-'*30)

    
    @pytest.mark.run(order=49)
    def test_49_delete_custom_rule_whitelist_tcp_fqdn(self):
        logging.info('-'*30+"Test Case 49 Execution Started"+'-'*30)
        logging.info('-'*15+"Delete custom rule for Whitelist TCP Domain"'-'*15)
        logging.info('-'*15+"Get ThreatProtection Grid rule for Whitelist"'-'*15)
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name=Whitelist:white_test_modified.com')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2


        data={"name":"Whitelist:white_test_modified.com"}
        modify_drop_field = ib_NIOS.wapi_request('DELETE',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field

        logging.info('-'*30+"Test Case 49 Execution Completed"+'-'*30)


    @pytest.mark.run(order=50)
    def test_50_add_custom_rule_whitelist_udp_fqdn(self):
        logging.info('-'*30+"Test Case 50 Execution Started"+'-'*30)
        logging.info("Validated Threat Protection Profile-Search for 'name' field")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']

        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120300500\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)

        add_custom_rule={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"PASS","log_severity":"WARNING","params":[{"name":"FQDN","value":"white_udp.com"},{"name": "EVENTS_PER_SECOND","value":"1"}]}}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:grid:rule",fields=json.dumps(add_custom_rule))
        logging.info(response)
        sleep(10)
        
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)
 

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Whitelist:white_udp.com')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
        assert custom_rule[0]["name"] == "Whitelist:white_udp.com"
        logging.info('-'*30+"Test Case 50 Execution Completed"+'-'*30) 

    @pytest.mark.run(order=51)
    def test_51_validate_sid_in_rules_txt_file_and_validated_functionality_of_added_whitelist_udp_fqdn_type(self):
        logging.info("Validate the SID in Rules.txt")
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Whitelist:white_udp.com')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
        assert custom_rule[0]["name"] == "Whitelist:white_udp.com"   
        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        logging.info(out)
        assert re.search(r'sid\:'+str(sid_value)+'',out)

       
        dig_cmd = 'dig @'+str(config.grid_member2_vip)+' white_udp.com +time=0 +retries=0'
        os.system(dig_cmd)
  
        logging.info('-'*30+"Test Case 51 Execution Completed"+'-'*30)


    @pytest.mark.run(order=52)
    def test_52_put_whitelist_udp_domain_negative_case(self):
        logging.info('-'*30+"Test Case 52 Execution Started"+'-'*30)
        logging.info('-'*15+"Performed Get Operation for member:threatprotection"+'-'*15)
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']


        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']
        

        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120300500\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        logging.info(rule_temp_ref)

        data={"name":"BLACKLIST DROP"}
        status,modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1_temp,fields=json.dumps(data))
        logging.info(modify_disable_field)
        assert status == 400
        print modify_disable_field
        logging.info('-'*30+"Test Case 52 Execution Completed"+'-'*30)


    @pytest.mark.run(order=53)
    def test_53_update_disable_field_as_false_for_custom_rule(self):
        logging.info('-'*30+"Test Case 53 Execution Started"+'-'*30)
        logging.info("Modify Disable field for custom rule with value as true")

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Whitelist:white_udp.com')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        custom_name = custom_rule[0]['name']
        print custom_name
        #print ref_2
        ref_1 = custom_rule[0]['_ref']
        print ref_1

        data={"disabled":False}
        modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1,fields=json.dumps(data))
        logging.info(modify_disable_field)
        print modify_disable_field

        get_custom_rule_ref = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Whitelist:white_udp.com')
        custom_rule_2=json.loads(get_custom_rule)
        custom_ref = custom_rule[0]['_ref']
        print custom_ref


        get_ref_after_disable = ib_NIOS.wapi_request('GET', object_type = custom_ref+'?_return_fields=disabled')
        #print get_ref_after_disable
        custom_rule_3=json.loads(get_ref_after_disable)
        logging.info(get_ref_after_disable)
        print get_ref_after_disable
        disable_field = custom_rule_3['disabled']
        print disable_field
        sleep(10)

        assert custom_rule_3["disabled"] == False
        logging.info('-'*30+"Test Case 53 Execution Completed"+'-'*30)


    @pytest.mark.run(order=54)
    def test_54_update_fqdn_and_log_severity_for_whitelist_udp_domain_type(self):
        logging.info('-'*30+"Test Case 54 Execution Started"+'-'*30)
        logging.info('-'*15+"Modify Log Severity and FQDN Values in Custom Rule(Whitelist UDP Domain)"+'-'*15)
        logging.info("Get ThreatProtection Grid rule for Blacklist")
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name=Whitelist:white_udp.com')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2

        data={"config":{"action":"PASS","log_severity":"MAJOR","params":[{"name":"FQDN","value":"white_udp_modified.com"},{"name": "EVENTS_PER_SECOND","value":"2"}]}}
        modify_drop_field = ib_NIOS.wapi_request('PUT',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field
        sleep(10)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name,config')
        print get_ref_disable

        validate = json.loads(get_ref_disable)
        print validate
        ref_ipv4_1 = validate['config']
        print ref_ipv4_1

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Whitelist:white_udp_modified.com')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid'] 
        print sid_value
        assert custom_rule[0]["name"] == "Whitelist:white_udp_modified.com"
        logging.info('-'*30+"Test Case 54 Execution Completed"+'-'*30)
        

    @pytest.mark.run(order=55)
    def test_55_validate_sid_in_rules_txt_file_and_validated_functionality_of_modified_whitelist_udp_fqdn_type(self):       
        logging.info('-'*30+"Test Case 55 Execution started"+'-'*30)
        logging.info("Validating SID Values in rules.txt")
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Whitelist:white_udp_modified.com')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
 
        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        logging.info(out)
        assert re.search(r'sid\:'+str(sid_value)+'',out)

        logging.info("Performing DIG Commands") 
        dig_cmd = 'dig @'+str(config.grid_member2_vip)+' white_udp_modified.com +time=0 +retries=0'
        os.system(dig_cmd)

        logging.info('-'*30+"Test Case 55 Execution Completed"+'-'*30)

    
    @pytest.mark.run(order=56)
    def test_56_delete_custom_rule_whitelist_udp_domain(self):
        logging.info('-'*30+"Test Case 56 Execution Started"+'-'*30)
        logging.info('-'*15+"Delete custom rule for Whitelist UDP Domain"'-'*15)
        logging.info('-'*15+"Get ThreatProtection Grid rule for Whitelist"'-'*15)
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name=Whitelist:white_udp_modified.com')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2
        

        data={"name":"Whitelist:white_udp_modified.com"}
        modify_drop_field = ib_NIOS.wapi_request('DELETE',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field

        logging.info('-'*30+"Test Case 56 Execution Completed"+'-'*30)

    
    @pytest.mark.run(order=57)
    def test_57_add_custom_rule_whitelist_pass_tcp_priority_rate_limiting(self):
        logging.info('-'*30+"Test Case 57 Execution Started"+'-'*30)
        logging.info("Get Member Threat Protection using member:threatprotection object")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']

        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120102000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)

        add_custom_rule={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"PASS","log_severity":"WARNING","params":[{"name":"WHITELISTED_IP","value":"10.0.0.10"}]}}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:grid:rule",fields=json.dumps(add_custom_rule))
        logging.info(response)
        sleep(10)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)


        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Whitelist:10.0.0.10')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
        assert custom_rule[0]["name"] == "Whitelist:10.0.0.10"
        logging.info('-'*30+"Test Case 57 Execution Completed"+'-'*30)


    @pytest.mark.run(order=58)
    def test_58_validate_sid_in_rules_txt_file_and_validated_functionality_of_added_whitelist_pass_tcp_ip_prior_to_rate_limiting(self):
        logging.info('-'*30+"Test Case 58 Execution Started"+'-'*30)
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Whitelist:10.0.0.10')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value

        logging.info("Validating SID in rules.txt")         
        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        logging.info(out)
        assert re.search(r'sid\:'+str(sid_value)+'',out)

        logging.info('-'*30+"Test Case 58 Execution Completed"+'-'*30)


    @pytest.mark.run(order=59)
    def test_59_update_whitelist_pass_tcp_priority_rate_limiting_negative_case(self):
        logging.info('-'*30+"Test Case 59 Execution Started"+'-'*30)
        logging.info('-'*15+"Performed Get Operation for member:threatprotection"+'-'*15)
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']


        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120102000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        logging.info(rule_temp_ref)

        data={"name":"BLACKLIST DROP"}
        status,modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1_temp,fields=json.dumps(data))
        logging.info(modify_disable_field)
        assert status == 400
        print modify_disable_field
        logging.info('-'*30+"Test Case 59 Execution Completed"+'-'*30)
    
    @pytest.mark.run(order=59)
    def test_59_update_disable_field_false_for_whitelist_pass_tcp_ip_prior_to_rate_limiting(self):
        logging.info('-'*15+"Test Case 59 Execution Started"+'-'*30)
        logging.info("Modify Disable field for custom rule with value as true")

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Whitelist:10.0.0.10')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        custom_name = custom_rule[0]['name']
        print custom_name
        #print ref_2
        ref_1 = custom_rule[0]['_ref']
        print ref_1

        data={"disabled":False}
        modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1,fields=json.dumps(data))
        logging.info(modify_disable_field)
        print modify_disable_field

        get_custom_rule_ref = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Whitelist:10.0.0.10')
        custom_rule_2=json.loads(get_custom_rule)
        custom_ref = custom_rule[0]['_ref']
        print custom_ref


        get_ref_after_disable = ib_NIOS.wapi_request('GET', object_type = custom_ref+'?_return_fields=disabled')
        #print get_ref_after_disable
        custom_rule_3=json.loads(get_ref_after_disable)
        logging.info(get_ref_after_disable)
        print get_ref_after_disable
        disable_field = custom_rule_3['disabled']
        print disable_field
        sleep(10)

        assert custom_rule_3["disabled"] == False
        logging.info('-'*30+"Test Case 59 Execution Completed"+'-'*30)


    
    @pytest.mark.run(order=60)
    def test_60_put_whitelist_pass_tcp_ip_priority_rate_limiting(self):
        logging.info('-'*30+"Test Case 60 Execution Started"+'-'*30)
        logging.info('-'*15+"Modify Log Severity and FQDN Values in Custom Rule(Whitelist Pass TCP Priority Rate Limiting)"+'-'*15)
        logging.info("Get ThreatProtection Grid rule for Whitelist")
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name=Whitelist:10.0.0.10')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120102000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)

        data={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"PASS","log_severity":"WARNING","params":[{"name":"WHITELISTED_IP","value":"10.0.0.20"}]}}
        modify_drop_field = ib_NIOS.wapi_request('PUT',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field

        sleep(10)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)
 
        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name,config')
        print get_ref_disable

        validate = json.loads(get_ref_disable)
        print validate
        ref_ipv4_1 = validate['config']
        print ref_ipv4_1

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Whitelist:10.0.0.20')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value

        assert custom_rule[0]["name"] == "Whitelist:10.0.0.20"
        logging.info('-'*30+"Test Case 60 Execution Completed"+'-'*30)  


    @pytest.mark.run(order=61)
    def test_61_validate_sid_in_rules_txt_and_validated_functionality_for__whitelist_pass_tcp_ip_prior_to_rate_limiting(self):
        logging.info('-'*30+"Test Case 61 Execution Started"+'-'*30)
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Whitelist:10.0.0.20')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
   
        logging.info("Validating SID in rules.txt file")
        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        logging.info(out)    
        assert re.search(r'sid\:'+str(sid_value)+'',out)
        logging.info('-'*30+"Test Case 61 Execution Completed"+'-'*30)


    @pytest.mark.run(order=62)
    def test_62_delete_custom_rule_whitelist_pass_tcp_prior_limiting(self):
        logging.info('-'*30+"Test Case 62 Execution Started"+'-'*30)
        logging.info('-'*15+"Delete custom rule for Whitelist UDP Domain"'-'*15)
        logging.info('-'*15+"Get ThreatProtection Grid rule for Whitelist"'-'*15)
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name=Whitelist:10.0.0.20')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2


        data={"name":"Whitelist:10.0.0.20"}
        modify_drop_field = ib_NIOS.wapi_request('DELETE',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field

        logging.info('-'*30+"Test Case 62 Execution Completed"+'-'*30)


    @pytest.mark.run(order=63)
    def test_63_add_custom_rule_rate_limited_tcp_fqdn_lookup(self):
        logging.info('-'*30+"Test Case 63 Execution Started"+'-'*30)
        logging.info("Get Member Threat Protection using member:threatprotection object")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']

        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120302000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)

        add_custom_rule={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"ALERT","log_severity":"WARNING","params":[{"name":"FQDN","value":"rate_tcp.com"},{"name": "EVENTS_PER_SECOND","value":"1"},{"name":"PACKETS_PER_SECOND","value":"1"},{"name":"DROP_INTERVAL","value":"5"},{"name":"RATE_ALGORITHM","value":"Blocking"}]}}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:grid:rule",fields=json.dumps(add_custom_rule))
        logging.info(response)
        #print response
        logging.info("Perform Publish Operation") 
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)
        sleep(10)

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print get_custom_rule
        print type(custom_rule)

        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value 
        assert custom_rule[0]["name"] == "Rate Limited:rate_tcp.com"
        logging.info('-'*30+"Test Case 63 Execution Completed"+'-'*30)


    @pytest.mark.run(order=64)
    def test_64_validate_sid_txt_and_functionality_for_rate_limited_tcp_fqdn_lookup(self):
        logging.info('-'*30+"Test Case 64 Execution Started"+'-'*30)
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print get_custom_rule
        print type(custom_rule)

        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value  
        sleep(120)  
        logging.info("Validating SID Value in rules.txt")
        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        assert re.search(r'sid\:'+str(sid_value)+'',out)


        dig_cmd =os.system('for i in {1..10};do dig @'+str(config.grid_member2_vip)+' rate_tcp.com +tcp +time=0 +retries=0;done')
        print dig_cmd
        logging.info(dig_cmd) 

        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " tail -200 /var/log/syslog | grep -ir \'RATE LIMITED .*\' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        assert re.search(r''+str(sid_value)+'|Rate Limited:rate_tcp\.com.*cat\=\"RATE LIMITED.*\"',out1)
   
        logging.info('-'*30+"Test Case 64 Execution Completed"+'-'*30)


    @pytest.mark.run(order=65)
    def test_65_update_type_rate_limited_tcp_fqdn_lookup_negative_case(self):
        logging.info('-'*30+"Test Case 65 Execution Started"+'-'*30)
        logging.info('-'*15+"Performed Get Operation for member:threatprotection"+'-'*15)
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']


        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120302000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        logging.info(rule_temp_ref)

        data={"name":"BLACKLIST DROP"}
        status,modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1_temp,fields=json.dumps(data))
        logging.info(modify_disable_field)
        assert status == 400
        print modify_disable_field
        logging.info('-'*30+"Test Case 65 Execution Completed"+'-'*30)

   
    @pytest.mark.run(order=66)
    def test_66_update_disable_field_false_for_custom_rule(self):
        logging.info('-'*30+"Test Case 66 Execution Started"+'-'*30)
        logging.info("Modify Disable field for custom rule with value as true")

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        custom_name = custom_rule[0]['name']
        print custom_name
        #print ref_2
        ref_1 = custom_rule[0]['_ref']
        print ref_1

        data={"disabled":False}
        modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1,fields=json.dumps(data))
        logging.info(modify_disable_field)
        print modify_disable_field

        get_custom_rule_ref = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate*')
        custom_rule_2=json.loads(get_custom_rule)
        custom_ref = custom_rule[0]['_ref']
        print custom_ref


        get_ref_after_disable = ib_NIOS.wapi_request('GET', object_type = custom_ref+'?_return_fields=disabled')
        #print get_ref_after_disable
        custom_rule_3=json.loads(get_ref_after_disable)
        logging.info(get_ref_after_disable)
        print get_ref_after_disable
        disable_field = custom_rule_3['disabled']
        print disable_field
        sleep(10)

        assert custom_rule_3["disabled"] == False
        logging.info('-'*30+"Test Case 66 Execution Completed"+'-'*30)

     
    @pytest.mark.run(order=67)
    def test_67_update_log_severity_and_fqdn_for_rate_limited_tcp_fqdn_lookup(self):
        logging.info('-'*30+"Test Case 67 Execution Started"+'-'*30)
        logging.info('-'*15+"Modify Log Severity and FQDN Values in Custom Rule(Rate Limited TCP FQDN)"+'-'*15)
        logging.info("Get ThreatProtection Grid rule for Whitelist")
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name~=Rate.*')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120302000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)

        data={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"ALERT","log_severity":"WARNING","params":[{"name":"FQDN","value":"rate_tcp_modified.com"},{"name": "EVENTS_PER_SECOND","value":"1"},{"name":"PACKETS_PER_SECOND","value":"1"},{"name":"DROP_INTERVAL","value":"5"},{"name":"RATE_ALGORITHM","value":"Blocking"}]}}
        modify_drop_field = ib_NIOS.wapi_request('PUT',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field
        sleep(10)
        
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)


        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name,config')
        print get_ref_disable

        validate = json.loads(get_ref_disable)
        print validate
        ref_ipv4_1 = validate['config']
        print ref_ipv4_1

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
        assert custom_rule[0]["name"] == "Rate Limited:rate_tcp_modified.com"
        logging.info('-'*30+"Test Case 67 Execution Completed"+'-'*30)     


    @pytest.mark.run(order=68)
    def test_68_validate_sid_in_rules_txt_file_and_validated_functionality_of_modified_rate_limited_tcp_fqdn_type(self):
        logging.info('-'*30+"Test Case 68 Execution Completed"+'-'*30)
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
        sleep(120)
        logging.info("Validating sid value in rules.txt")
        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        assert re.search(r'sid\:'+str(sid_value)+'',out)

        logging.info("Validating DROPS in syslog after performing queries")  
        dig_cmd=os.system('for i in {1..10};do dig @'+str(config.grid_member2_vip)+' rate_tcp_modified.com +tcp +time=0 +retries=0;done')
        print dig_cmd
        logging.info(dig_cmd)   
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " tail -200 /var/log/syslog | grep -ir \'RATE LIMITED .*\' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        assert re.search(r''+str(sid_value)+'|Rate Limited:rate_tcp_modified\.com.*cat\=\"RATE LIMITED.*\"',out1)

        logging.info('-'*30+"Test Case 68 Execution Completed"+'-'*30)
        


    @pytest.mark.run(order=69)
    def test_69_delete_custom_rule_rate_limited_tcp_fqdn(self):
        logging.info('-'*30+"Test Case 69 Execution Started"+'-'*30)
        logging.info('-'*15+"Delete custom rule for Rate Limited TCP FQDN"'-'*15)
        logging.info('-'*15+"Get ThreatProtection Grid rule for RATE LIMTED"'-'*15)
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name~=Rate.*')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2

        data={"name":"Rate Limited:rate_tcp_modified.com"}
        modify_drop_field = ib_NIOS.wapi_request('DELETE',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field
        logging.info('-'*30+"Test Case 69 Execution Completed"+'-'*30)


    @pytest.mark.run(order=70)
    def test_70_add_custom_rule_rate_limited_udp_fqdn_lookup(self):
        logging.info('-'*30+"Test Case 70 Execution Started"+'-'*30)
        logging.info("Get Member Threat Protection using member:threatprotection object")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']

        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120301000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)

        add_custom_rule={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"ALERT","log_severity":"WARNING","params":[{"name":"FQDN","value":"rate_udp.com"},{"name": "EVENTS_PER_SECOND","value":"1"},{"name":"PACKETS_PER_SECOND","value":"1"},{"name":"DROP_INTERVAL","value":"5"},{"name":"RATE_ALGORITHM","value":"Blocking"}]}}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:grid:rule",fields=json.dumps(add_custom_rule))
        logging.info(response)
        #print response

        sleep(10)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)
      

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print get_custom_rule
        print type(custom_rule)

        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
        assert custom_rule[0]["name"] == "Rate limited:rate_udp.com"
        logging.info('-'*30+"Test Case 70 Execution Completed"+'-'*30)

    
    @pytest.mark.run(order=71)
    def test_71_put_blacklist_udp_fqdn_type(self):
        logging.info('-'*30+"Test Case 71 Execution Started"+'-'*30)
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print get_custom_rule
        print type(custom_rule)

        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value  
        logging.info("Validate SID in rules.txt")
        sleep(30)
        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        logging.info(out)
        sleep(30)
        assert re.search(r'sid\:'+str(sid_value)+'',out)
        logging.info("Perform DIG Command")  
        dig_cmd = os.system('for i in {1..10};do dig @'+str(config.grid_member2_vip)+' rate_udp.com +time=0 +retries=0;done')
        print dig_cmd
        logging.info(dig_cmd)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " tail -200 /var/log/syslog | grep -ir \'RATE LIMITED .*\' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        logging.info(out1)
        assert re.search(r''+str(sid_value)+'|Rate Limited:rate_udp\.com.*cat\=\"RATE LIMITED.*\"',out1)   

        logging.info('-'*30+"Test Case 71 Execution Completed"+'-'*30)


    @pytest.mark.run(order=72)
    def test_72_update_rate_limited_udp_fqdn_lookup_negative_case(self):
        logging.info('-'*30+"Test Case 72 Execution Started"+'-'*30)
        logging.info('-'*15+"Performed Get Operation for member:threatprotection"+'-'*15)
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']


        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120301000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        logging.info(rule_temp_ref)

        data={"name":"BLACKLIST DROP"}
        status,modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1_temp,fields=json.dumps(data))
        logging.info(modify_disable_field)
        assert status == 400
        print modify_disable_field
        logging.info('-'*30+"Test Case 72 Execution Completed"+'-'*30)


    @pytest.mark.run(order=72)
    def test_72_update_disable_field_false_for_custom_rule(self):
        logging.info('-'*30+"Test Case 72 Execution Started"+'-'*30)
        logging.info("Modify Disable field for custom rule with value as true")

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        custom_name = custom_rule[0]['name']
        print custom_name
        #print ref_2
        ref_1 = custom_rule[0]['_ref']
        print ref_1

        data={"disabled":False}
        modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1,fields=json.dumps(data))
        logging.info(modify_disable_field)
        print modify_disable_field

        get_custom_rule_ref = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule_2=json.loads(get_custom_rule)
        custom_ref = custom_rule[0]['_ref']
        print custom_ref


        get_ref_after_disable = ib_NIOS.wapi_request('GET', object_type = custom_ref+'?_return_fields=disabled')
        #print get_ref_after_disable
        custom_rule_3=json.loads(get_ref_after_disable)
        logging.info(get_ref_after_disable)
        print get_ref_after_disable
        disable_field = custom_rule_3['disabled']
        print disable_field
        sleep(10)

        assert custom_rule_3["disabled"] == False
        logging.info('-'*30+"Test Case 72 Execution Completed"+'-'*30)

    

    @pytest.mark.run(order=73)
    def test_73_update_log_severity_and_fqdn_for_rate_limited_udp_fqdn_lookup(self):
        logging.info('-'*30+"Test Case 73 Execution Started"+'-'*30)
        logging.info('-'*15+"Modify Log Severity and FQDN Values in Custom Rul(Rate Limited UDP Fqdn Lookup)"+'-'*15)
        logging.info("Get ThreatProtection Grid rule for Whitelist")
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name~=Rate.*')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120301000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)
    
        data={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"ALERT","log_severity":"WARNING","params":[{"name":"FQDN","value":"rate_udp_modified.com"},{"name": "EVENTS_PER_SECOND","value":"1"},{"name":"PACKETS_PER_SECOND","value":"1"},{"name":"DROP_INTERVAL","value":"5"},{"name":"RATE_ALGORITHM","value":"Blocking"}]}}
        modify_drop_field = ib_NIOS.wapi_request('PUT',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field
        sleep(10)

        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name,config')
        print get_ref_disable

        validate = json.loads(get_ref_disable)
        print validate
        ref_ipv4_1 = validate['config']
        print ref_ipv4_1

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
        assert custom_rule[0]["name"] == "Rate limited:rate_udp_modified.com"
        logging.info('-'*30+"Test Case 73 Execution Completed"+'-'*30)

    @pytest.mark.run(order=74)
    def test_74_validate_sid_in_rules_txt_file_and_validated_functionality_of_modified_rate_limited_udp_fqdn_lookup(self):
        logging.info('-'*30+"Test Case 74 Execution Started"+'-'*30)
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        assert re.search(r'sid\:'+str(sid_value)+'',out)


        dig_cmd = os.system('for i in {1..10};do dig @'+str(config.grid_member2_vip)+' rate_udp_modified.com +time=0 +retries=0;done')
        print dig_cmd
        logging.info(dig_cmd)

        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " tail -200 /var/log/syslog | grep -ir \'RATE LIMITED .*\' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        assert re.search(r''+str(sid_value)+'|Rate Limited:rate_udp_modified\.com.*cat\=\"RATE LIMITED.*\"',out1)

        logging.info('-'*30+"Test Case 74 Execution Completed"+'-'*30)
   


    @pytest.mark.run(order=75)
    def test_75_delete_custom_rule_rate_limited_udp_fqdn_lookup(self):
        logging.info('-'*30+"Test Case 75 Execution Started"+'-'*30)
        logging.info('-'*15+"Delete custom rule for Rate Limited UDP FQDN Lookup"'-'*15)
        logging.info('-'*15+"Get ThreatProtection Grid rule for Whitelist"'-'*15)
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name~=Rate.*')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2


        data={"name":"Rate limited:rate_udp_modified.com"}
        modify_drop_field = ib_NIOS.wapi_request('DELETE',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field

        logging.info('-'*30+"Test Case 75 Execution Completed"+'-'*30)


    @pytest.mark.run(order=76)
    def test_76_add_custom_rule_rate_limited_tcp_ip(self):
        logging.info('-'*30+"Test Case 76 Execution Started"+'-'*30)
        logging.info("Get Member Threat Protection using member:threatprotection object")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']

        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120202000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)

        add_custom_rule={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"ALERT","log_severity":"WARNING","params":[{"name":"LIMITED_IP","value":config.client_ip},{"name": "EVENTS_PER_SECOND","value":"1"},{"name":"PACKETS_PER_SECOND","value":"5"},{"name":"DROP_INTERVAL","value":"5"},{"name":"RATE_ALGORITHM","value":"Blocking"}]}}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:grid:rule",fields=json.dumps(add_custom_rule))
        logging.info(response)
        #print response

        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")   
        sleep(90)
        
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print get_custom_rule
        print type(custom_rule)

        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value

        assert custom_rule[0]["name"] == "Rate limited:"+config.client_ip
        logging.info('-'*30+"Test Case 76 Execution Completed"+'-'*30)


    @pytest.mark.run(order=76)
    def test_76_validate_sid_in_rules_txt_file_and_validated_functionality_of_rate_limited_tcp_ip(self):
        logging.info('-'*30+"Test Case 76 Execution Started"+'-'*30)
        logging.info("Validating SID in rules.txt file")
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print get_custom_rule
        print type(custom_rule)

        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value

        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        logging.info(out)  
        assert re.search(r'sid\:'+str(sid_value)+'',out)

        logging.info("Validating Drops in SYSLOG after performing queries")   
        dig_cmd = os.system('for i in {1..10};do dig @'+str(config.grid_member2_vip)+' rate_udp_modified.com +tcp +time=0 +retries=0;done')
        print dig_cmd
        logging.info(dig_cmd)

        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " tail -200 /var/log/syslog | grep -ir \'RATE LIMITED .*\' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        logging.info(out1)
        assert re.search(r''+str(sid_value)+'|Rate Limited:'+str(config.client_ip)+'.*cat\=\"RATE LIMITED.*\"',out1)
 
        logging.info('-'*30+"Test Case 76 Execution Completed"+'-'*30)


    @pytest.mark.run(order=77)
    def test_77_put_rate_limited_tcp_ip_negative_case(self):
        logging.info('-'*30+"Test Case 77 Execution Started"+'-'*30)
        logging.info('-'*15+"Performed Get Operation for member:threatprotection"+'-'*15)
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']


        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120202000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        logging.info(rule_temp_ref)

        data={"name":"BLACKLIST DROP"}
        status,modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1_temp,fields=json.dumps(data))
        logging.info(modify_disable_field)
        assert status == 400
        print modify_disable_field
        logging.info('-'*30+"Test Case 77 Execution Completed"+'-'*30)


    @pytest.mark.run(order=78)
    def test_78_update_disable_field_false_for_custom_rule(self):
        logging.info('-'*30+"Test Case 78 Execution Started"+'-'*30)
        logging.info("Modify Disable field for custom rule with value as true")

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        custom_name = custom_rule[0]['name']
        print custom_name
        #print ref_2
        ref_1 = custom_rule[0]['_ref']
        print ref_1

        data={"disabled":False}
        modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1,fields=json.dumps(data))
        logging.info(modify_disable_field)
        print modify_disable_field

        get_custom_rule_ref = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule_2=json.loads(get_custom_rule)
        custom_ref = custom_rule[0]['_ref']
        print custom_ref


        get_ref_after_disable = ib_NIOS.wapi_request('GET', object_type = custom_ref+'?_return_fields=disabled')
        #print get_ref_after_disable
        custom_rule_3=json.loads(get_ref_after_disable)
        logging.info(get_ref_after_disable)
        print get_ref_after_disable
        disable_field = custom_rule_3['disabled']
        print disable_field
        sleep(10)

        assert custom_rule_3["disabled"] == False
        logging.info('-'*30+"Test Case 78 Execution Completed"+'-'*30)


    @pytest.mark.run(order=79)
    def test_79_update_log_severity_and_fqdn_for_rate_limited_tcp_ip(self):
        logging.info('-'*30+"Test Case 79 Execution Started"+'-'*30)
        logging.info('-'*15+"Modify Log Severity and FQDN Values in Custom Rule(Rate Limited TCP IP)"+'-'*15)
        logging.info("Get ThreatProtection Grid rule for Rate Limited")
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name~=Rate.*')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120202000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)
    
        data={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"ALERT","log_severity":"WARNING","params":[{"name":"LIMITED_IP","value":config.client_ip},{"name": "EVENTS_PER_SECOND","value":"1"},{"name":"PACKETS_PER_SECOND","value":"1"},{"name":"DROP_INTERVAL","value":"4"},{"name":"RATE_ALGORITHM","value":"Blocking"}]}}
        modify_drop_field = ib_NIOS.wapi_request('PUT',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)
        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name,config')
        print get_ref_disable

        validate = json.loads(get_ref_disable)
        print validate
        ref_ipv4_1 = validate['config']
        print ref_ipv4_1

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
#        assert custom_rule[0]["name"] == "Rate limited:10.0.0.20"
        sid_value = custom_rule[0]['sid']
        print sid_value

        assert custom_rule[0]["name"] == "Rate limited:"+config.client_ip
        logging.info('-'*30+"Test Case 79 Execution Completed"+'-'*30)


    @pytest.mark.run(order=80)
    def test_80_validate_sid_in_rules_txt_file_and_validated_functionality_of_modified_rate_limited_tcp_ip(self):
        logging.info('-'*30+"Test Case 80 Execution Started"+'-'*30)
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value

        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        assert re.search(r'sid\:'+str(sid_value)+'',out)


        dig_cmd = os.system('for i in {1..10};do dig @'+str(config.grid_member2_vip)+' rate_udp_modified.com +tcp +time=0 +retries=0;done')
        print dig_cmd
        logging.info(dig_cmd)

        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " tail -200 /var/log/syslog | grep -ir \'RATE LIMITED .*\' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        assert re.search(r''+str(sid_value)+'|Rate Limited:'+str(config.client_ip)+'.*cat\=\"RATE LIMITED.*\"',out1)

        logging.info('-'*30+"Test Case 80 Execution Completed"+'-'*30)


    @pytest.mark.run(order=81)
    def test_81_delete_custom_rule_rate_limited_tcp_ip(self):
        logging.info('-'*30+"Test Case 81 Execution Started"+'-'*30)
        logging.info('-'*15+"Delete custom rule for Rate Limited TCP IP"'-'*15)
        logging.info('-'*15+"Get ThreatProtection Grid rule for Rate Limited TCP IP"'-'*15)
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name~=Rate.*')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2


        data={"name":"Rate limited:config.client_ip"}
        modify_drop_field = ib_NIOS.wapi_request('DELETE',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field

        logging.info('-'*30+"Test Case 81 Execution Completed"+'-'*30)

    
    @pytest.mark.run(order=82)
    def test_82_add_custom_rule_rate_limited_udp_ip(self):
        logging.info('-'*30+"Test Case 82 Execution Started"+'-'*30)
        logging.info("Get Member Threat Protection using member:threatprotection object")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']

        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120201000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)

        add_custom_rule={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"ALERT","log_severity":"WARNING","params":[{"name":"LIMITED_IP","value":config.client_ip},{"name": "EVENTS_PER_SECOND","value":"1"},{"name":"PACKETS_PER_SECOND","value":"5"},{"name":"DROP_INTERVAL","value":"30"},{"name":"RATE_ALGORITHM","value":"Blocking"}]}}  
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:grid:rule",fields=json.dumps(add_custom_rule))
        logging.info(response)
        #print response
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print get_custom_rule
        print type(custom_rule)

        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
        assert custom_rule[0]["name"] == "Rate limited:"+config.client_ip
        logging.info('-'*30+"Test Case 82 Execution Completed"+'-'*30)


    @pytest.mark.run(order=83)
    def test_83_validate_sid_in_rules_txt_file_and_validated_functionality_of_modified_rate_limited_udp_ip(self):
        logging.info('-'*30+"Test Case 83 Execution Completed"+'-'*30)
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print get_custom_rule
        print type(custom_rule)

        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value

        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        assert re.search(r'sid\:'+str(sid_value)+'',out)


        dig_cmd = os.system('for i in {1..10};do dig @'+str(config.grid_member2_vip)+' rate_udp_modified.com +time=0 +retries=0;done')
        print dig_cmd
        logging.info(dig_cmd)

        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " tail -200 /var/log/syslog | grep -ir \'RATE LIMITED .*\' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        assert re.search(r''+str(sid_value)+'|Rate Limited:'+str(config.client_ip)+'.*cat\=\"RATE LIMITED.*\"',out1)
 
        logging.info('-'*30+"Test Case 83 Execution Completed"+'-'*30)
 
    @pytest.mark.run(order=84)
    def test_84_update_rate_limited_udp_ip_negative_case(self):
        logging.info('-'*30+"Test Case 84 Execution Started"+'-'*30)
        logging.info('-'*15+"Performed Get Operation for member:threatprotection"+'-'*15)
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']


        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120201000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        logging.info(rule_temp_ref)

        data={"name":"BLACKLIST DROP"}
        status,modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1_temp,fields=json.dumps(data))
        logging.info(modify_disable_field)
        assert status == 400
        print modify_disable_field
        logging.info('-'*30+"Test Case 84 Execution Completed"+'-'*30)
 
    @pytest.mark.run(order=85)
    def test_85_update_disable_field_false_for_custom_rule(self):
        logging.info('-'*30+"Test Case 85 Execution Started"+'-'*30)
        logging.info("Modify Disable field for custom rule with value as true")

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        custom_name = custom_rule[0]['name']
        print custom_name
        #print ref_2
        ref_1 = custom_rule[0]['_ref']
        print ref_1

        data={"disabled":False}
        modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1,fields=json.dumps(data))
        logging.info(modify_disable_field)
        print modify_disable_field

        get_custom_rule_ref = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule_2=json.loads(get_custom_rule)
        custom_ref = custom_rule[0]['_ref']
        print custom_ref


        get_ref_after_disable = ib_NIOS.wapi_request('GET', object_type = custom_ref+'?_return_fields=disabled')
        #print get_ref_after_disable
        custom_rule_3=json.loads(get_ref_after_disable)
        logging.info(get_ref_after_disable)
        print get_ref_after_disable
        disable_field = custom_rule_3['disabled']
        print disable_field
        sleep(10)

        assert custom_rule_3["disabled"] == False
        
        logging.info('-'*30+"Test Case 85 Execution Completed"+'-'*30)


    @pytest.mark.run(order=86)
    def test_86_update_log_severity_and_fqdn_rate_limited_udp_ip(self):
        logging.info('-'*30+"Test Case 86 Execution Started"+'-'*30)
        logging.info('-'*15+"Modify Log Severity and FQDN Values in Custom Rule(Rate Limited UDP IP)"+'-'*15)
        logging.info("Get ThreatProtection Grid rule for Whitelist")
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name~=Rate.*')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120201000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)

        data={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"ALERT","log_severity":"WARNING","params":[{"name":"LIMITED_IP","value":config.client_ip},{"name": "EVENTS_PER_SECOND","value":"1"},{"name":"PACKETS_PER_SECOND","value":"1"},{"name":"DROP_INTERVAL","value":"4"},{"name":"RATE_ALGORITHM","value":"Rate_Limiting"}]}}
        modify_drop_field = ib_NIOS.wapi_request('PUT',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field
        
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)
        
        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name,config')
        print get_ref_disable

        validate = json.loads(get_ref_disable)
        print validate
        ref_ipv4_1 = validate['config']
        print ref_ipv4_1

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        
 #      assert custom_rule[0]["name"] == "Rate limited:20.0.0.20"
        sid_value = custom_rule[0]['sid']
        print sid_value

        assert custom_rule[0]["name"] == "Rate limited:"+config.client_ip
        logging.info('-'*30+"Test Case 86 Execution Completed"+'-'*30)


    @pytest.mark.run(order=87)
    def test_87_validate_sid_in_rules_txt_file_and_validated_functionality_of_modified_blacklist_udp_fqdn_type(self):
        logging.info('-'*30+"Test Case 87 Execution Started"+'-'*30)
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2

        sid_value = custom_rule[0]['sid']
        print sid_value

        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        assert re.search(r'sid\:'+str(sid_value)+'',out)


        dig_cmd = os.system('for i in {1..10};do dig @'+str(config.grid_member2_vip)+' rate_udp_modified.com +time=0 +retries=0;done')
        print dig_cmd
        logging.info(dig_cmd)

        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " tail -200 /var/log/syslog | grep -ir \'RATE LIMITED .*\' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        assert re.search(r''+str(sid_value)+'|Rate Limited:'+str(config.client_ip)+'.*cat\=\"RATE LIMITED.*\"',out1)
    
        logging.info('-'*30+"Test Case 88 Execution Completed"+'-'*30)
 
    @pytest.mark.run(order=89)
    def test_89_delete_custom_rule_rate_limited_udp_id(self):
        logging.info('-'*30+"Test Case 89 Execution Started"+'-'*30)
        logging.info('-'*15+"Delete custom rule for Rate Limited UDP IP"'-'*15)
        logging.info('-'*15+"Get ThreatProtection Grid rule for Whitelist"'-'*15)
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name~=Rate.*')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2


        data={"name":"Rate limited:config.client_ip"}
        modify_drop_field = ib_NIOS.wapi_request('DELETE',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field

        logging.info('-'*30+"Test Case 89 Execution Completed"+'-'*30)


    @pytest.mark.run(order=90)
    def test_90_add_custom_rule_rate_limited_udp_dns_message_type(self):
        logging.info('-'*30+"Test Case 90 Execution Started"+'-'*30)
        logging.info("Get Member Threat Protection using member:threatprotection object")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
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
        logging.info(rule_temp_ref)

        add_custom_rule={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"PASS","log_severity":"WARNING","params":[{"name":"RECORD_TYPE","value":"A"},{"name": "EVENTS_PER_SECOND","value":"1"},{"name":"RATE_FILTER_COUNT","value":"1"},{"name":"DROP_INTERVAL","value":"5"},{"name":"RATE_ALGORITHM","value":"Rate_Limiting"}]}}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:grid:rule",fields=json.dumps(add_custom_rule))
        logging.info(response)
        #print response
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print get_custom_rule
        print type(custom_rule)

        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value

        assert custom_rule[0]["name"] == "Rate Limited UDP DNS Message Type: A record"
        logging.info('-'*30+"Test Case 90 Execution Completed"+'-'*30) 


    @pytest.mark.run(order=91)
    def test_91_validate_sid_in_rules_txt_file_and_validated_functionality_of_added_rate_limited_udp_dns_messagetype(self):
        logging.info('-'*30+"Test Case 91 Execution Completed"+'-'*30)
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print get_custom_rule
        print type(custom_rule)

        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        assert re.search(r'sid\:'+str(sid_value)+'',out)


        dig_cmd = os.system('for i in {1..10};do dig @'+str(config.grid_member2_vip)+' A rate_udp_modified.com +time=0 +retries=0;done')
        print dig_cmd
        logging.info(dig_cmd)

        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " tail -200 /var/log/syslog | grep -ir \'RATE LIMITED .*\' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        assert re.search(r''+str(sid_value)+'|Rate Limited .*: A record.*cat\=\"RATE LIMITED.*\"',out1)
        logging.info('-'*30+"Test Case 91 Execution Completed"+'-'*30)


    @pytest.mark.run(order=92)
    def test_92_update_rate_limited_udp_dns_messgae_type_negative_case(self):
        logging.info('-'*30+"Test Case 92 Execution Started"+'-'*30)
        logging.info('-'*15+"Performed Get Operation for member:threatprotection"+'-'*15)
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']


        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120201000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        logging.info(rule_temp_ref)

        data={"name":"BLACKLIST DROP"}
        status,modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1_temp,fields=json.dumps(data))
        logging.info(modify_disable_field)
        assert status == 400
        print modify_disable_field
        logging.info('-'*30+"Test Case 92 Execution Completed"+'-'*30)

    @pytest.mark.run(order=93)
    def test_93_update_disable_field_false_for_custom_rule(self):
        logging.info('-'*30+"Test Case 93 Execution Started"+'-'*30)
        logging.info("Modify Disable field for custom rule with value as true")

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        custom_name = custom_rule[0]['name']
        print custom_name
        #print ref_2
        ref_1 = custom_rule[0]['_ref']
        print ref_1

        data={"disabled":False}
        modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1,fields=json.dumps(data))
        logging.info(modify_disable_field)
        print modify_disable_field

        get_custom_rule_ref = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule_2=json.loads(get_custom_rule)
        custom_ref = custom_rule[0]['_ref']
        print custom_ref


        get_ref_after_disable = ib_NIOS.wapi_request('GET', object_type = custom_ref+'?_return_fields=disabled')
        #print get_ref_after_disable
        custom_rule_3=json.loads(get_ref_after_disable)
        logging.info(get_ref_after_disable)
        print get_ref_after_disable
        disable_field = custom_rule_3['disabled']
        print disable_field
        sleep(10)

        assert custom_rule_3["disabled"] == False
        logging.info('-'*30+"Test Case 93 Execution Completed"+'-'*30)


    @pytest.mark.run(order=94)
    def test_94_update_rate_limited_udp_dns_message_type_negative_case(self):
        logging.info('-'*30+"Test Case 94 Execution Started"+'-'*30)
        logging.info('-'*15+"Modify Log Severity and FQDN Values in Custom Rule(Rate Limited UDP DNS Message Type)"+'-'*15)
        logging.info("Get ThreatProtection Grid rule for Rate Limiting")
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name~=Rate.*')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
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
        logging.info(rule_temp_ref)

        data={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"PASS","log_severity":"WARNING","params":[{"name":"RECORD_TYPE","value":"CNAME"},{"name": "EVENTS_PER_SECOND","value":"1"},{"name":"RATE_FILTER_COUNT","value":"1"},{"name":"DROP_INTERVAL","value":"4"},{"name":"RATE_ALGORITHM","value":"Rate_Limiting"}]}}

        modify_drop_field = ib_NIOS.wapi_request('PUT',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field
        
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)
        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name,config')
        print get_ref_disable

        validate = json.loads(get_ref_disable)
        print validate
        ref_ipv4_1 = validate['config']
        print ref_ipv4_1

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        assert custom_rule[0]["name"] == "Rate Limited UDP DNS Message Type: CNAME record"
        sid_value = custom_rule[0]['sid']
        print sid_value
        logging.info('-'*30+"Test Case 94 Execution Completed"+'-'*30)   

    @pytest.mark.run(order=95)
    def test_95_put_validate_sid_in_rules_txt_file_and_validated_functionality_of_modified_rate_limited_udp_dns_message_type(self):
        logging.info('-'*30+"Test Case 95 Execution Completed"+'-'*30)
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value

        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        assert re.search(r'sid\:'+str(sid_value)+'',out)


        dig_cmd = os.system('for i in {1..10};do dig @'+str(config.grid_member2_vip)+' rate_udp_modified.com CNAME +time=0 +retries=0;done')
        print dig_cmd
        logging.info(dig_cmd)

        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " tail -200 /var/log/syslog | grep -ir \'RATE LIMITED .*\' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        assert re.search(r''+str(sid_value)+'|Rate Limited .*: CNAME record.*cat\=\"RATE LIMITED.*\"',out1)

        logging.info('-'*30+"Test Case 95 Execution Completed"+'-'*30)



    @pytest.mark.run(order=96)
    def test_96_delete_custom_rule_rate_limited_udp_dns_messgae_type(self):
        logging.info('-'*30+"Test Case 96 Execution Started"+'-'*30)
        logging.info('-'*15+"Delete custom rule for Rate Limited UDP DNS Message Type"'-'*15)
        logging.info('-'*15+"Get ThreatProtection Grid rule for Rate Limited"'-'*15)
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name~=Rate.*')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2


        data={"name":"Rate Limited .*: CNAME record"}
        modify_drop_field = ib_NIOS.wapi_request('DELETE',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field

        logging.info('-'*30+"Test Case 96 Execution Completed"+'-'*30)


    @pytest.mark.run(order=97)
    def test_97_add_custom_rule_rate_limited_tcp_dns_message_type(self):
        logging.info('-'*30+"Test Case 97 Execution Started"+'-'*30)
        logging.info("Get Member Threat Protection using member:threatprotection object")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']

        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=130482000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)

        add_custom_rule={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"PASS","log_severity":"WARNING","params":[{"name":"RECORD_TYPE","value":"A"},{"name": "EVENTS_PER_SECOND","value":"1"},{"name":"RATE_FILTER_COUNT","value":"1"},{"name":"DROP_INTERVAL","value":"5"},{"name":"RATE_ALGORITHM","value":"Rate_Limiting"}]}}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:grid:rule",fields=json.dumps(add_custom_rule))
        logging.info(response)
        #print response

        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)
 

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print get_custom_rule
        print type(custom_rule)

        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
        assert custom_rule[0]["name"] == "Rate Limited TCP DNS Message Type: A record"
        logging.info('-'*30+"Test Case 97 Execution Completed"+'-'*30)

    @pytest.mark.run(order=98)
    def test_98_put_validate_sid_in_rules_txt_file_and_validated_functionality_of_added_rate_limited_dns_message_type(self):    
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print get_custom_rule
        print type(custom_rule)

        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
 
        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        assert re.search(r'sid\:'+str(sid_value)+'',out)


        dig_cmd = os.system('for i in {1..10};do dig @'+str(config.grid_member2_vip)+' rate_tcp_modified.com +tcp +time=0 +retries=0;done')
        print dig_cmd
        logging.info(dig_cmd)

        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " tail -200 /var/log/syslog | grep -ir \'RATE LIMITED .*\' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        assert re.search(r''+str(sid_value)+'|Rate Limited .*: A record.*cat\=\"RATE LIMITED.*\"',out1)


        logging.info('-'*30+"Test Case 98 Execution Completed"+'-'*30)

    @pytest.mark.run(order=99)
    def test_99_update_rate_limited_tcp_dns_message_type_negative_case(self):
        logging.info('-'*30+"Test Case 99 Execution Started"+'-'*30)
        logging.info('-'*15+"Performed Get Operation for member:threatprotection"+'-'*15)
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']


        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=130482000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        logging.info(rule_temp_ref)

        data={"name":"BLACKLIST DROP"}
        status,modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1_temp,fields=json.dumps(data))
        logging.info(modify_disable_field)
        assert status == 400
        print modify_disable_field
        logging.info('-'*30+"Test Case 99 Execution Completed"+'-'*30)


    @pytest.mark.run(order=100)
    def test_100_update_disable_field_false_for_custom_rule(self):
        logging.info('-'*30+"Test Case 100 Execution Started"+'-'*30)
        logging.info("Modify Disable field for custom rule with value as true")

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        custom_name = custom_rule[0]['name']
        print custom_name
        #print ref_2
        ref_1 = custom_rule[0]['_ref']
        print ref_1

        data={"disabled":False}
        modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1,fields=json.dumps(data))
        logging.info(modify_disable_field)
        print modify_disable_field

        get_custom_rule_ref = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule_2=json.loads(get_custom_rule)
        custom_ref = custom_rule[0]['_ref']
        print custom_ref


        get_ref_after_disable = ib_NIOS.wapi_request('GET', object_type = custom_ref+'?_return_fields=disabled')
        #print get_ref_after_disable
        custom_rule_3=json.loads(get_ref_after_disable)
        logging.info(get_ref_after_disable)
        print get_ref_after_disable
        disable_field = custom_rule_3['disabled']
        print disable_field
        sleep(10)

        assert custom_rule_3["disabled"] == False
        logging.info('-'*30+"Test Case 100 Execution Completed"+'-'*30)


    @pytest.mark.run(order=101)
    def test_101_update_logging_severity_and_type_for_rate_limited_tcp_dns_message_type(self):
        logging.info('-'*30+"Test Case 101 Execution Started"+'-'*30)
        logging.info('-'*15+"Modify Log Severity and FQDN Values in Custom Rule(Ratelimited TCP DNS Message Type)"+'-'*15)
        logging.info("Get ThreatProtection Grid rule for Whitelist")
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name~=Rate.*')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=130482000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)


        data={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"PASS","log_severity":"WARNING","params":[{"name":"RECORD_TYPE","value":"CNAME"},{"name": "EVENTS_PER_SECOND","value":"1"},{"name":"RATE_FILTER_COUNT","value":"1"},{"name":"DROP_INTERVAL","value":"5"},{"name":"RATE_ALGORITHM","value":"Rate_Limiting"}]}}
        
        modify_drop_field = ib_NIOS.wapi_request('PUT',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field

        sleep(10)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)
        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name,config')
        print get_ref_disable

        validate = json.loads(get_ref_disable)
        print validate
        ref_ipv4_1 = validate['config']
        print ref_ipv4_1

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        assert custom_rule[0]["name"] == "Rate Limited TCP DNS Message Type: CNAME record"
        sid_value = custom_rule[0]['sid']
        print sid_value
        logging.info('-'*30+"Test Case 101 Execution Completed"+'-'*30)
       
    @pytest.mark.run(order=102)
    def test_102_update_rate_limited_tcp_dns_message_type(self):
        logging.info('-'*30+"Test Case 102 Execution Completed"+'-'*30)
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
  
        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        assert re.search(r'sid\:'+str(sid_value)+'',out)


        dig_cmd = os.system('for i in {1..10};do dig @'+str(config.grid_member2_vip)+' rate_tcp_modified.com +tcp +time=0 +retries=0;done')
        print dig_cmd
        logging.info(dig_cmd)

        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " tail -200 /var/log/syslog | grep -ir \'RATE LIMITED .*\' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        assert re.search(r''+str(sid_value)+'|Rate Limited .*: CNAME record.*cat\=\"RATE LIMITED.*\"',out1)
     
        logging.info('-'*30+"Test Case 102 Execution Completed"+'-'*30)


    @pytest.mark.run(order=103)
    def test_103_delete_custom_rule_rate_limited_tcp_dns_message_type(self):
        logging.info('-'*30+"Test Case 103 Execution Started"+'-'*30)
        logging.info('-'*15+"Delete custom rule for Rate Limited TCP DNS Message Type"'-'*15)
        logging.info('-'*15+"Get ThreatProtection Grid rule for Rate Limited"'-'*15)
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name~=Rate.*')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2


        data={"name":"Rate Limited .*: CNAME record"}
        modify_drop_field = ib_NIOS.wapi_request('DELETE',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field
        logging.info('-'*30+"Test Case 103 Execution Completed"+'-'*30)

    @pytest.mark.run(order=104)
    def test_104_add_custom_rule_pass_udp_dns_message_type(self):
        logging.info('-'*30+"Test Case 104 Execution Started"+'-'*30)
        logging.info("Get Member Threat Protection using member:threatprotection object")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']

        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=130483000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)

        add_custom_rule={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"PASS","log_severity":"WARNING","params":[{"name":"RECORD_TYPE","value":"A"}]}}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:grid:rule",fields=json.dumps(add_custom_rule))
        logging.info(response)
        #print response
        
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Pass%20UDP%20DNS%20Message%20Type')
        custom_rule=json.loads(get_custom_rule)
        print get_custom_rule
        print type(custom_rule)

        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value

        assert custom_rule[0]["name"] == "Pass UDP DNS Message Type: A record"
        logging.info('-'*30+"Test Case 104 Execution Completed"+'-'*30)

   
    @pytest.mark.run(order=105)
    def test_105_validate_sid_in_rules_txt_file_and_validated_functionality_of_added_pass_udp_dns_message_type(self):    
        logging.info('-'*30+"Test Case 105 Execution Completed"+'-'*30)
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Pass%20UDP%20DNS%20Message%20Type')
        custom_rule=json.loads(get_custom_rule)
        print get_custom_rule
        print type(custom_rule)

        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value

        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        assert re.search(r'sid\:'+str(sid_value)+'',out)
        logging.info('-'*30+"Test Case 105 Execution Completed"+'-'*30)



    @pytest.mark.run(order=106)
    def test_106_update_pass_udp_dns_message_type_negative_case(self):
        logging.info('-'*30+"Test Case 106 Execution Started"+'-'*30)
        logging.info('-'*15+"Performed Get Operation for member:threatprotection"+'-'*15)
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']


        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=130483000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        logging.info(rule_temp_ref)

        data={"name":"BLACKLIST DROP"}
        status,modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1_temp,fields=json.dumps(data))
        logging.info(modify_disable_field)
        assert status == 400
        print modify_disable_field
        logging.info('-'*30+"Test Case 106 Execution Completed"+'-'*30)


    @pytest.mark.run(order=107)
    def test_107_update_disable_field_false_for_custom_rule(self):
        logging.info('-'*30+"Test Case 107 Execution Started"+'-'*30)
        logging.info("Modify Disable field for custom rule with value as true")

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Pass%20UDP%20DNS%20Message%20Type')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        custom_name = custom_rule[0]['name']
        print custom_name
        #print ref_2
        ref_1 = custom_rule[0]['_ref']
        print ref_1

        data={"disabled":False}
        modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1,fields=json.dumps(data))
        logging.info(modify_disable_field)
        print modify_disable_field

        get_custom_rule_ref = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Pass*')
        custom_rule_2=json.loads(get_custom_rule)
        custom_ref = custom_rule[0]['_ref']
        print custom_ref


        get_ref_after_disable = ib_NIOS.wapi_request('GET', object_type = custom_ref+'?_return_fields=disabled')
        #print get_ref_after_disable
        custom_rule_3=json.loads(get_ref_after_disable)
        logging.info(get_ref_after_disable)
        print get_ref_after_disable
        disable_field = custom_rule_3['disabled']
        print disable_field
        sleep(10)

        assert custom_rule_3["disabled"] == False
        logging.info('-'*30+"Test Case 107 Execution Completed"+'-'*30)


    @pytest.mark.run(order=108)
    def test_108_update_log_severity_and_type_for_pass_udp_dns_message_type(self):
        logging.info('-'*30+"Test Case 108 Execution Started"+'-'*30)
        logging.info('-'*15+"Modify Log Severity and FQDN Values in Custom Rule(Pass UDP DNS Message Type)"+'-'*15)
        logging.info("Get ThreatProtection Grid rule for Whitelist")
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name~=Pass%20UDP%20DNS%20Message%20Type')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=130483000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)


        data={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"PASS","log_severity":"WARNING","params":[{"name":"RECORD_TYPE","value":"CNAME"}]}}
        modify_drop_field = ib_NIOS.wapi_request('PUT',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field

        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)


        sleep(10)
        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name,config')
        print get_ref_disable

        validate = json.loads(get_ref_disable)
        print validate
        ref_ipv4_1 = validate['config']
        print ref_ipv4_1

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Pass%20UDP%20DNS%20Message%20Type')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        assert custom_rule[0]["name"] == "Pass UDP DNS Message Type: CNAME record"
        logging.info('-'*30+"Test Case 108 Execution Completed"+'-'*30)

    @pytest.mark.run(order=109)
    def test_109_validate_sid_in_rules_txt_file_and_validated_functionality_of_modified_pass_udp_dns_message_type(self):
        logging.info('-'*30+"Test Case 109 Execution Completed"+'-'*30)
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Pass%20UDP%20DNS%20Message%20Type')
        custom_rule=json.loads(get_custom_rule)
        print get_custom_rule
        print type(custom_rule)

        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value

        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        assert re.search(r'sid\:'+str(sid_value)+'',out)
        logging.info('-'*30+"Test Case 109 Execution Completed"+'-'*30)



    @pytest.mark.run(order=110)
    def test_110_delete_custom_rule_pass_udp_dns_message_type(self):
        logging.info('-'*30+"Test Case 110 Execution Started"+'-'*30)
        logging.info('-'*15+"Delete custom rule for Pass UDP DNS Message Type"'-'*15)
        logging.info('-'*15+"Get ThreatProtection Grid rule for Pass"'-'*15)
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name~=Pass%20UDP%20DNS%20Message%20Type')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2


        data={"name":"Pass UDP .*: CNAME record"}
        modify_drop_field = ib_NIOS.wapi_request('DELETE',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field

        logging.info('-'*30+"Test Case 110 Execution Completed"+'-'*30)



    @pytest.mark.run(order=111)
    def test_111_add_custom_rule_pass_tcp_dns_message_type(self):
        logging.info('-'*30+"Test Case 111 Execution Started"+'-'*30)
        logging.info("Get Member Threat Protection using member:threatprotection object")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']

        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=130484000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)

        add_custom_rule={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"PASS","log_severity":"WARNING","params":[{"name":"RECORD_TYPE","value":"A"}]}}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:grid:rule",fields=json.dumps(add_custom_rule))
        logging.info(response)
        #print response
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)


        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Pass%20TCP%20DNS%20Message%20Type')
        custom_rule=json.loads(get_custom_rule)
        print get_custom_rule
        print type(custom_rule)

        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
        assert custom_rule[0]["name"] == "Pass TCP DNS Message Type: A record"

        logging.info('-'*30+"Test Case 111 Execution Completed"+'-'*30)


    @pytest.mark.run(order=112)
    def test_112_validate_sid_in_rules_txt_file_and_validated_functionality_of_added_pass_tcp_dns_message_type(self):    
        logging.info('-'*30+"Test Case 112 Execution Started"+'-'*30)
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Pass%20TCP%20DNS%20Message%20Type')
        custom_rule=json.loads(get_custom_rule)
        print get_custom_rule
        print type(custom_rule)

        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
 
        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        assert re.search(r'sid\:'+str(sid_value)+'',out)

        logging.info('-'*30+"Test Case 112 Execution Completed"+'-'*30)



    @pytest.mark.run(order=113)
    def test_113_update_pass_tcp_dns_message_type_negative_case(self):
        logging.info('-'*30+"Test Case 113 Execution Started"+'-'*30)
        logging.info('-'*15+"Performed Get Operation for member:threatprotection"+'-'*15)
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']


        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=130484000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        logging.info(rule_temp_ref)

        data={"name":"BLACKLIST DROP"}
        status,modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1_temp,fields=json.dumps(data))
        logging.info(modify_disable_field)
        assert status == 400
        print modify_disable_field
        logging.info('-'*30+"Test Case 113 Execution Completed"+'-'*30)
   

    @pytest.mark.run(order=114)
    def test_114_update_disable_field_false_for_custom_rule(self):
        logging.info('-'*30+"Test Case 114 Execution Started"+'-'*30)
        logging.info("Modify Disable field for custom rule with value as true")

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Pass%20TCP%20DNS%20Message%20Type')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        custom_name = custom_rule[0]['name']
        print custom_name
        #print ref_2
        ref_1 = custom_rule[0]['_ref']
        print ref_1

        data={"disabled":True}
        modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1,fields=json.dumps(data))
        logging.info(modify_disable_field)
        print modify_disable_field

        get_custom_rule_ref = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Pass*')
        custom_rule_2=json.loads(get_custom_rule)
        custom_ref = custom_rule[0]['_ref']
        print custom_ref


        get_ref_after_disable = ib_NIOS.wapi_request('GET', object_type = custom_ref+'?_return_fields=disabled')
        #print get_ref_after_disable
        custom_rule_3=json.loads(get_ref_after_disable)
        logging.info(get_ref_after_disable)
        print get_ref_after_disable
        disable_field = custom_rule_3['disabled']
        print disable_field
        sleep(10)

        assert custom_rule_3["disabled"] == True
        logging.info('-'*30+"Test Case 114 Execution Completed"+'-'*30)


    @pytest.mark.run(order=115)
    def test_115_update_log_severity_and_type_for_pass_tcp_dns_message_type(self):
        logging.info('-'*30+"Test Case 115 Execution Started"+'-'*30)
        logging.info('-'*15+"Modify Log Severity and FQDN Values in Custom Rule(PASS TCP DNS Message Types)"+'-'*15)
        logging.info("Get ThreatProtection Grid rule for Whitelist")
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name~=Pass%20TCP%20DNS%20Message%20Type')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=130484000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)


        data={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"PASS","log_severity":"WARNING","params":[{"name":"RECORD_TYPE","value":"CNAME"}]}}

        modify_drop_field = ib_NIOS.wapi_request('PUT',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field
            
        sleep(10)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)
        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name,config')
        print get_ref_disable

        validate = json.loads(get_ref_disable)
        print validate
        ref_ipv4_1 = validate['config']
        print ref_ipv4_1

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Pass%20TCP%20DNS%20Message%20Type')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
        assert custom_rule[0]["name"] == "Pass TCP DNS Message Type: CNAME record"
        logging.info('-'*30+"Test Case 115 Execution Completed"+'-'*30)


    @pytest.mark.run(order=116)
    def test_116_validate_sid_in_rules_txt_file_and_validated_functionality_of_added_pass_tcp_dns_message_type(self):
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Pass%20TCP%20DNS%20Message%20Type')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        assert re.search(r'sid\:'+str(sid_value)+'',out)
        assert custom_rule[0]["name"] == "Pass TCP DNS Message Type: CNAME record"
        logging.info('-'*30+"Test Case 116 Execution Completed"+'-'*30)
  
    @pytest.mark.run(order=117)
    def test_117_delete_custom_rule_pass_tcp_dns_message_type(self):
        logging.info('-'*30+"Test Case 117 Execution Started"+'-'*30)
        logging.info('-'*15+"Delete custom rule for Pass TCP DNS Message Type"'-'*15)
        logging.info('-'*15+"Get ThreatProtection Grid rule for Pass"'-'*15)
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name~=Pass%20TCP%20DNS%20Message%20Type')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2


        data={"name":"Pass TCP .*: CNAME record"}
        modify_drop_field = ib_NIOS.wapi_request('DELETE',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field

        logging.info('-'*30+"Test Case 117 Execution Completed"+'-'*30)

    @pytest.mark.run(order=118)
    def test_118_add_custom_rule_blacklist_udp_fqdn_lookup_dns_message_type(self):
        logging.info('-'*30+"Test Case 118 Execution Started"+'-'*30)
        logging.info("Get Member Threat Protection using member:threatprotection object")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']

        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120305000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)

        add_custom_rule={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"DROP","log_severity":"WARNING","params":[{"name":"RECORD_TYPE","value":"A"},{"name": "EVENTS_PER_SECOND","value":"1"},{"name":"FQDN","value":"black_udp_dns.com"}]}}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:grid:rule",fields=json.dumps(add_custom_rule))
        logging.info(response)
        #print response
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)  



        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Blacklist')
        custom_rule=json.loads(get_custom_rule)
        print get_custom_rule
        print type(custom_rule)

        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
        assert custom_rule[0]["name"] == "Blacklist UDP DNS Message type: A record for black_udp_dns.com"
        logging.info('-'*30+"Test Case 118 Execution Completed"+'-'*30)


    @pytest.mark.run(order=119)
    def test_119_update_blacklist_udp_fqdn_lookup_dns_message_type_negative_case(self):         
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Blacklist')
        custom_rule=json.loads(get_custom_rule)
        print get_custom_rule
        print type(custom_rule)

        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value

        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        assert re.search(r'sid\:'+str(sid_value)+'',out)


        dig_cmd = os.system('for i in {1..10};do dig @'+str(config.grid_member2_vip)+' black_udp_dns.com A +time=0 +retries=0;done')
        print dig_cmd
        logging.info(dig_cmd)

        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " tail -200 /var/log/syslog | grep -ir \'BLACKLIST UDP .*\' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        assert re.search(r''+str(sid_value)+'|Blacklist UDP .*: A record for black_udp_dns.com.*cat\=\"BLACKLIST UDP.*\"',out1)

        logging.info('-'*30+"Test Case 119 Execution Completed"+'-'*30)


    @pytest.mark.run(order=120)
    def test_120_update_blacklist_udp_fqdn_lookup_negative_case(self):
        logging.info('-'*30+"Test Case 120 Execution Started"+'-'*30)
        logging.info('-'*15+"Performed Get Operation for member:threatprotection"+'-'*15)
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']


        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120305000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        logging.info(rule_temp_ref)

        data={"name":"BLACKLIST DROP"}
        status,modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1_temp,fields=json.dumps(data))
        logging.info(modify_disable_field)
        assert status == 400
        print modify_disable_field
        logging.info('-'*30+"Test Case 120 Execution Completed"+'-'*30)


    @pytest.mark.run(order=121)
    def test_121_update_disable_field_false_for_custom_rule(self):
        logging.info('-'*30+"Test Case 121 Execution Started"+'-'*30)
        logging.info("Modify Disable field for custom rule with value as true")

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~:=BLACKLIST*')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule

        custom_name = custom_rule[0]['name']
        print custom_name
        #print ref_2
        ref_1 = custom_rule[0]['_ref']

        print ref_1


        data={"disabled":False}
        modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1,fields=json.dumps(data))
        logging.info(modify_disable_field)
        print modify_disable_field

        get_custom_rule_ref = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=BLACKLIST')
        custom_rule_2=json.loads(get_custom_rule)
        custom_ref = custom_rule[0]['_ref']
        print custom_ref

        get_ref_after_disable = ib_NIOS.wapi_request('GET', object_type = custom_ref+'?_return_fields=disabled')
        #print get_ref_after_disable
        custom_rule_3=json.loads(get_ref_after_disable)
        logging.info(get_ref_after_disable)
        print get_ref_after_disable
        disable_field = custom_rule_3['disabled']
        print disable_field
        sleep(10)
        assert custom_rule_3["disabled"] == False
        logging.info('-'*30+"Test Case 120 Execution Completed"+'-'*30)  



    @pytest.mark.run(order=121)
    def test_121_put_blacklist_udp_fqdn_lookup_dns_message_type(self):
        logging.info('-'*30+"Test Case 121 Execution Started"+'-'*30)
        logging.info('-'*15+"Modify Log Severity and FQDN Values in Custom Rule(Blacklist UDP FQDN lookup DNS Message Type)"+'-'*15)
        logging.info("Get ThreatProtection Grid rule for Whitelist")
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name~:=BLACKLIST*')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120305000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)

        data={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"DROP","log_severity":"WARNING","params":[{"name":"RECORD_TYPE","value":"CNAME"},{"name": "EVENTS_PER_SECOND","value":"1"},{"name":"FQDN","value":"black_udp_dns_modified.com"}]}}
       
        modify_drop_field = ib_NIOS.wapi_request('PUT',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field
        
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)
   
        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name,config')
        print get_ref_disable

        validate = json.loads(get_ref_disable)
        print validate
        ref_ipv4_1 = validate['config']
        print ref_ipv4_1

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~:=BLACKLIST')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        
        sid_value = custom_rule[0]['sid']
        print sid_value
        assert custom_rule[0]["name"] == "Blacklist UDP DNS Message type: CNAME record for black_udp_dns_modified.com"
        logging.info('-'*30+"Test Case 121 Execution Completed"+'-'*30)


    @pytest.mark.run(order=122)
    def test_122_validate_sid_in_rules_txt_file_and_validated_functionality_of_modified_blacklist_udp_fqdn_lookup_dns_message_type(self):
        logging.info('-'*30+"Test Case 122 Execution Started"+'-'*30)
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~:=BLACKLIST')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        assert re.search(r'sid\:'+str(sid_value)+'',out)


        dig_cmd = os.system('for i in {1..10};do dig @'+str(config.grid_member2_vip)+' black_udp_dns_modified.com cname +time=0 +retries=0;done')
        print dig_cmd
        logging.info(dig_cmd)

        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " tail -200 /var/log/syslog | grep -ir \'BLACKLIST UDP .*\' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        assert re.search(r''+str(sid_value)+'|Blacklist UDP .*: CNAME record.*cat\=\"BLACKLIST UDP.*\"',out1)

        logging.info('-'*30+"Test Case 122 Execution Completed"+'-'*30)
  
    
    @pytest.mark.run(order=123)
    def test_123_delete_custom_rule_blacklist_udp_fqdn_lookup_dns_message_type(self):
        logging.info('-'*30+"Test Case 123 Execution Started"+'-'*30)
        logging.info('-'*15+"Delete custom rule for Blacklist UDP DNS Message Type"'-'*15)
        logging.info('-'*15+"Get ThreatProtection Grid rule for Pass"'-'*15)
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name~:=BLACKLIST*')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2


        data={"name":"Blacklist UDP .*: CNAME record for black_udp_dns_modified.com"}
        modify_drop_field = ib_NIOS.wapi_request('DELETE',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field

        logging.info('-'*30+"Test Case 124 Execution Completed"+'-'*30)


    @pytest.mark.run(order=124)
    def test_124_add_custom_rule_blacklist_tcp_fqdn_lookup_dns_message_type(self):
        logging.info('-'*30+"Test Case 124 Execution Started"+'-'*30)
        logging.info("Get Member Threat Protection using member:threatprotection object")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']

        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120306000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)

        add_custom_rule={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"DROP","log_severity":"WARNING","params":[{"name":"RECORD_TYPE","value":"A"},{"name": "EVENTS_PER_SECOND","value":"1"},{"name":"FQDN","value":"black_tcp_dns.com"}]}}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:grid:rule",fields=json.dumps(add_custom_rule))
        logging.info(response)
        #print response
        sleep(10)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)


        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Blacklist')
        custom_rule=json.loads(get_custom_rule)
        print get_custom_rule
        print type(custom_rule)

        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
        assert custom_rule[0]["name"] == "Blacklist TCP DNS Message type: A record for black_tcp_dns.com"
        logging.info('-'*30+"Test Case 124 Execution Completed"+'-'*30)

    @pytest.mark.run(order=125)
    def test_125_validate_sid_in_rules_txt_file_and_validated_functionality_of_added_blacklist_tcp_dns_message_type(self):
        logging.info('-'*30+"Test Case 125 Execution Completed"+'-'*30)
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Blacklist')
        custom_rule=json.loads(get_custom_rule)
        print get_custom_rule
        print type(custom_rule)

        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value  
        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        assert re.search(r'sid\:'+str(sid_value)+'',out)


        dig_cmd = os.system('for i in {1..10};do dig @'+str(config.grid_member2_vip)+' black_tcp_dns.com +tcp +time=0 +retries=0;done')
        print dig_cmd
        logging.info(dig_cmd)

        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " tail -200 /var/log/syslog | grep -ir \'BLACKLIST TCP .*\' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        assert re.search(r''+str(sid_value)+'|Blacklist TCP .*: A record for black_tcp_dns.com.*cat\=\"BLACKLIST TCP.*\"',out1)
        logging.info('-'*30+"Test Case 125 Execution Completed"+'-'*30)
  

    @pytest.mark.run(order=126)
    def test_126_update_blacklist_tcp_fqdn_lookup_dns_message_type_negative_case(self):
        logging.info('-'*30+"Test Case 126 Execution Started"+'-'*30)
        logging.info('-'*15+"Performed Get Operation for member:threatprotection"+'-'*15)
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']


        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120306000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        logging.info(rule_temp_ref)

        data={"name":"BLACKLIST DROP"}
        status,modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1_temp,fields=json.dumps(data))
        logging.info(modify_disable_field)
        assert status == 400
        print modify_disable_field
        logging.info('-'*30+"Test Case 126 Execution Completed"+'-'*30)


    @pytest.mark.run(order=127)
    def test_127_update_blacklist_tcp_fqdn_lookup_dns_message_type_custom_rule(self):
        logging.info('-'*30+"Test Case 127 Execution Started"+'-'*30)
        logging.info("Modify Disable field for custom rule with value as true")

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~:=BLACKLIST*')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule

        custom_name = custom_rule[0]['name']
        print custom_name
        #print ref_2
        ref_1 = custom_rule[0]['_ref']

        print ref_1


        data={"disabled":False}
        modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1,fields=json.dumps(data))
        logging.info(modify_disable_field)
        print modify_disable_field

        get_custom_rule_ref = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=BLACKLIST')
        custom_rule_2=json.loads(get_custom_rule)
        custom_ref = custom_rule[0]['_ref']
        print custom_ref


        get_ref_after_disable = ib_NIOS.wapi_request('GET', object_type = custom_ref+'?_return_fields=disabled')
        #print get_ref_after_disable
        custom_rule_3=json.loads(get_ref_after_disable)
        logging.info(get_ref_after_disable)
        print get_ref_after_disable
        disable_field = custom_rule_3['disabled']
        print disable_field
        sleep(10)

        assert custom_rule_3["disabled"] == False
        logging.info('-'*30+"Test Case 127 Execution Completed"+'-'*30)


    @pytest.mark.run(order=128)
    def test_128_update_log_severity_and_fqdn_for_blacklist_tcp_fqdn_lookup_dns_message_type(self):
        logging.info('-'*30+"Test Case 128 Execution Started"+'-'*30)
        logging.info('-'*15+"Modify Log Severity and FQDN Values in Custom Rule(Blacklist TCP DNS Message Type)"+'-'*15)
        logging.info("Get ThreatProtection Grid rule for Blacklist")
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name~:=BLACKLIST*')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120306000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)
   
        data={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"DROP","log_severity":"WARNING","params":[{"name":"RECORD_TYPE","value":"CNAME"},{"name": "EVENTS_PER_SECOND","value":"1"},{"name":"FQDN","value":"black_tcp_dns_modified.com"}]}}
 
 
        modify_drop_field = ib_NIOS.wapi_request('PUT',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field
        sleep(10)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name,config')
        print get_ref_disable

        validate = json.loads(get_ref_disable)
        print validate
        ref_ipv4_1 = validate['config']
        print ref_ipv4_1

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~:=BLACKLIST')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
        assert custom_rule[0]["name"] == "Blacklist TCP DNS Message type: CNAME record for black_tcp_dns_modified.com"
        logging.info('-'*30+"Test Case 128 Execution Completed"+'-'*30)


    @pytest.mark.run(order=129)
    def test_129_validate_sid_in_rules_txt_file_and_validated_functionality_of_modified_blacklist_tcp_fqdn_lookup_dns_message_type(self):
        logging.info('-'*30+"Test Case 129 Execution Completed"+'-'*30)
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~:=BLACKLIST')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value

        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        assert re.search(r'sid\:'+str(sid_value)+'',out)


        dig_cmd = os.system('for i in {1..10};do dig @'+str(config.grid_member2_vip)+' black_tcp_dns_modified.com +tcp +time=0 +retries=0;done')
        print dig_cmd
        logging.info(dig_cmd)

        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " tail -200 /var/log/syslog | grep -ir \'BLACKLIST TCP .*\' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        assert re.search(r''+str(sid_value)+'|BLACKLIST TCP .*: A record for black_udp_dns_modified.com.*cat\=\"BLACKLIST TCP.*\"',out1)

#        assert custom_rule[0]["name"] == "Blacklist TCP DNS Message type: CNAME record for black_tcp_dns_modified.com"
        logging.info('-'*30+"Test Case 129 Execution Completed"+'-'*30)



    @pytest.mark.run(order=130)
    def test_130_delete_custom_rule_blacklist_tcp_fqdn_lookup_dns_message_type(self):
        logging.info('-'*30+"Test Case 130 Execution Started"+'-'*30)
        logging.info('-'*15+"Delete custom rule for Pass TCP DNS Message Type"'-'*15)
        logging.info('-'*15+"Get ThreatProtection Grid rule for Pass"'-'*15)
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name~:=BLACKLIST*')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2


        data={"name":"Blacklist TCP .*: CNAME record for black_tcp_dns_modified.com"}
        modify_drop_field = ib_NIOS.wapi_request('DELETE',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field
        logging.info('-'*30+"Test Case 130 Execution Completed"+'-'*30)


    @pytest.mark.run(order=131)
    def test_131_add_custom_rule_whitelist_pass_udp_prior_rate_limiting(self):
        logging.info('-'*30+"Test Case 131 Execution Started"+'-'*30)
        logging.info("Get Member Threat Protection using member:threatprotection object")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']

        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120101000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)

        add_custom_rule={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"PASS","log_severity":"WARNING","params":[{"name":"WHITELISTED_IP","value":"20.0.0.10"}]}}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:grid:rule",fields=json.dumps(add_custom_rule))
        logging.info(response)
        #print response

        sleep(10)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Whitelist:20.0.0.10')
        custom_rule=json.loads(get_custom_rule)

        print get_custom_rule
        print type(custom_rule)

        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']   
        print sid_value
        assert custom_rule[0]["name"] == "Whitelist:20.0.0.10"
        logging.info('-'*30+"Test Case 131 Execution Completed"+'-'*30)

    @pytest.mark.run(order=132)
    def test_132_validate_sid_in_rules_txt_file_and_validated_functionality_of_added_whitelist_pass_tcp_ip_prior_to_rate_limiting(self):
        logging.info('-'*30+"Test Case 132 Execution Completed"+'-'*30) 
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Whitelist:20.0.0.10')
        custom_rule=json.loads(get_custom_rule)

        print get_custom_rule
        print type(custom_rule)

        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        assert re.search(r'sid\:'+str(sid_value)+'',out)

        logging.info('-'*30+"Test Case 132 Execution Completed"+'-'*30)


    @pytest.mark.run(order=133)
    def test_133_update_whitelist_pass_udp_prior_limiting_negative_case(self):
        logging.info('-'*30+"Test Case 133 Execution Started"+'-'*30)
        logging.info('-'*15+"Performed Get Operation for member:threatprotection"+'-'*15)
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']


        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120101000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        logging.info(rule_temp_ref)

        data={"name":"BLACKLIST DROP"}
        status,modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1_temp,fields=json.dumps(data))
        logging.info(modify_disable_field)
        assert status == 400
        print modify_disable_field
        logging.info('-'*30+"Test Case 133 Execution Completed"+'-'*30)
    
     
    @pytest.mark.run(order=134)
    def test_134_update_disable_field_false_for_custom_rule(self):
        logging.info('-'*30+"Test Case 134 Execution Started"+'-'*30)
        logging.info("Modify Disable field for custom rule with value as true")

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Whitelist:20.0.0.10')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule

        custom_name = custom_rule[0]['name']
        print custom_name
        #print ref_2
        ref_1 = custom_rule[0]['_ref']

        print ref_1


        data={"disabled":False}
        modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1,fields=json.dumps(data))
        logging.info(modify_disable_field)
        print modify_disable_field

        get_custom_rule_ref = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Whitelist:20.0.0.10')
        custom_rule_2=json.loads(get_custom_rule)
        custom_ref = custom_rule[0]['_ref']
        print custom_ref


        get_ref_after_disable = ib_NIOS.wapi_request('GET', object_type = custom_ref+'?_return_fields=disabled')
        #print get_ref_after_disable
        custom_rule_3=json.loads(get_ref_after_disable)
        logging.info(get_ref_after_disable)
        print get_ref_after_disable
        disable_field = custom_rule_3['disabled']
        print disable_field
        sleep(10)

        assert custom_rule_3["disabled"] == False
        logging.info('-'*30+"Test Case 134 Execution Completed"+'-'*30)

        
    @pytest.mark.run(order=135)
    def test_135_update_log_severity_and_type_for_whitelist_pass_udp_prior_limiting(self):
        logging.info('-'*30+"Test Case 135 Execution Started"+'-'*30)
        logging.info('-'*15+"Modify Log Severity and FQDN Values in Custom Rule(Whitelist TCP Domain)"+'-'*15)
        logging.info("Get ThreatProtection Grid rule for Whitelist")
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name=Whitelist:20.0.0.10')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120101000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)

        data={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"PASS","log_severity":"WARNING","params":[{"name":"WHITELISTED_IP","value":"20.0.0.20"}]}}
        modify_drop_field = ib_NIOS.wapi_request('PUT',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field

        sleep(10)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)   
        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name,config')
        print get_ref_disable

        validate = json.loads(get_ref_disable)
        print validate
        ref_ipv4_1 = validate['config']
        print ref_ipv4_1

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Whitelist:20.0.0.20')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
        assert custom_rule[0]["name"] == "Whitelist:20.0.0.20"
        logging.info('-'*30+"Test Case 135 Execution Completed"+'-'*30)

    @pytest.mark.run(order=136)
    def test_136_update_blacklist_udp_fqdn_lookup_dns_message_type(self):
        logging.info('-'*30+"Test Case 136 Execution Started"+'-'*30)
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Whitelist:20.0.0.20')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value

        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        assert re.search(r'sid\:'+str(sid_value)+'',out)
 
        logging.info('-'*30+"Test Case 136 Execution Completed"+'-'*30)

    @pytest.mark.run(order=137)
    def test_137_delete_custom_rule_whitelist_pass_udp_ip_prior_limiting(self):
        logging.info('-'*30+"Test Case 137 Execution Started"+'-'*30)
        logging.info('-'*15+"Delete custom rule for Whitelist Pass UDP IP Prior Limiting"'-'*15)
        logging.info('-'*15+"Get ThreatProtection Grid rule for Pass"'-'*15)
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name=Whitelist:20.0.0.20')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2


        data={"name":"Whitelist:20.0.0.20"}
        modify_drop_field = ib_NIOS.wapi_request('DELETE',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field

        logging.info('-'*30+"Test Case 137 Execution Completed"+'-'*30)


    @pytest.mark.run(order=138)
    def test_138_add_custom_rule_blacklist_drop_udp_ip_prior_to_rate_limiting(self):
        logging.info('-'*30+"Test Case 138 Execution Started"+'-'*30)
        logging.info("Get Member Threat Protection using member:threatprotection object")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']

        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120103000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)

        add_custom_rule={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"DROP","log_severity":"WARNING","params":[{"name": "EVENTS_PER_SECOND","value":"1"},{"name": "BLACKLISTED_IP","value":config.client_ip}]}}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:grid:rule",fields=json.dumps(add_custom_rule))
        logging.info(response)
        #print response
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)
  
        sleep(10)

   #    get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Blacklist:11.0.0.1')
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Blacklist:'+config.client_ip)   
        custom_rule=json.loads(get_custom_rule)
        print get_custom_rule
        print type(custom_rule)

        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
        assert custom_rule[0]["name"] == "Blacklist:"+config.client_ip
        logging.info('-'*30+"Test Case 138 Execution Completed"+'-'*30)

    @pytest.mark.run(order=139)
    def test_139_validate_sid_in_rules_txt_file_and_validated_functionality_of_added_blacklist_drop_ip_prior_to_rate_limiting(self):
        logging.info('-'*30+"Test Case 139 Execution Completed"+'-'*30)
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Blacklist:'+config.client_ip)
        custom_rule=json.loads(get_custom_rule)
        print get_custom_rule
        print type(custom_rule)

        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value

        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        assert re.search(r'sid\:'+str(sid_value)+'',out)
            

        dig_cmd = os.system('for i in {1..10};do dig @'+str(config.grid_member2_vip)+' rate_udp_modified.com +time=0 +retries=0;done')
        print dig_cmd
        logging.info(dig_cmd)

        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " tail -200 /var/log/syslog | grep -ir \'BLACKLIST DROP .*\' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        assert re.search(r''+str(sid_value)+'|Blacklist:'+str(config.client_ip)+'.*cat\=\"BLACKLIST DROP.*\"',out1)
  

        logging.info('-'*30+"Test Case 139 Execution Completed"+'-'*30)


    @pytest.mark.run(order=140)
    def test_140_update_blacklist_drop_udp_ip_prior_to_rate_limiting_negative_case(self):
        logging.info('-'*30+"Test Case 140 Execution Started"+'-'*30)
        logging.info('-'*15+"Performed Get Operation for member:threatprotection"+'-'*15)
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']


        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120103000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        logging.info(rule_temp_ref)

        data={"name":"BLACKLIST DROP"}
        status,modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1_temp,fields=json.dumps(data))
        logging.info(modify_disable_field)
        assert status == 400
        print modify_disable_field
        logging.info('-'*30+"Test Case 140 Execution Completed"+'-'*30)


    @pytest.mark.run(order=141)
    def test_141_update_disable_field_false_for_custom_rule(self):
        logging.info('-'*30+"Test Case 141 Execution Started"+'-'*30)
        logging.info("Modify Disable field for custom rule with value as true")

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Blacklist:'+config.client_ip)
        custom_rule=json.loads(get_custom_rule)
        print custom_rule

        custom_name = custom_rule[0]['name']
        print custom_name
        #print ref_2
        ref_1 = custom_rule[0]['_ref']
        print ref_1

        data={"disabled":False}
        modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1,fields=json.dumps(data))
        logging.info(modify_disable_field)
        print modify_disable_field

        get_custom_rule_ref = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Blacklist:'+config.client_ip)
        custom_rule_2=json.loads(get_custom_rule)
        custom_ref = custom_rule[0]['_ref']
        print custom_ref

        get_ref_after_disable = ib_NIOS.wapi_request('GET', object_type = custom_ref+'?_return_fields=disabled')
        #print get_ref_after_disable
        custom_rule_3=json.loads(get_ref_after_disable)
        logging.info(get_ref_after_disable)
        print get_ref_after_disable
        disable_field = custom_rule_3['disabled']
        print disable_field
        sleep(10)

        assert custom_rule_3["disabled"] == False
        logging.info('-'*30+"Test Case 141 Execution Completed"+'-'*30)
   

    @pytest.mark.run(order=142)
    def test_142_update_blacklist_drop_udp_ip_prior_to_rate_limiting(self):
        logging.info('-'*30+"Test Case 142 Execution Started"+'-'*30)
        logging.info('-'*15+"Modify Log Severity and FQDN Values in Custom Rule(Blacklist DROP UDP)"+'-'*15)
        logging.info("Get ThreatProtection Grid rule for Whitelist")
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name=Blacklist:'+config.client_ip)
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120103000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)

        data={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"DROP","log_severity":"WARNING","params":[{"name": "EVENTS_PER_SECOND","value":"2"},{"name": "BLACKLISTED_IP","value":config.client_ip}]}}

        modify_drop_field = ib_NIOS.wapi_request('PUT',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field

        sleep(10)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)  
        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name,config')
        print get_ref_disable

        validate = json.loads(get_ref_disable)
        print validate
        ref_ipv4_1 = validate['config']
        print ref_ipv4_1

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Blacklist:'+config.client_ip)
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value

        assert custom_rule[0]["name"] == "Blacklist:"+config.client_ip
        logging.info('-'*30+"Test Case 142 Execution Completed"+'-'*30) 

    @pytest.mark.run(order=143)
    def test_143_validate_sid_in_rules_txt_file_and_validated_functionality_of_added_blacklist_drop_udp_ip_prior_to_rate_limiting(self):
        logging.info('-'*30+"Test Case 143 Execution Completed"+'-'*30)
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Blacklist:'+config.client_ip)
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        assert re.search(r'sid\:'+str(sid_value)+'',out)


        dig_cmd = os.system('for i in {1..10};do dig @'+str(config.grid_member2_vip)+' rate_udp_modified.com +time=0 +retries=0;done')
        print dig_cmd
        logging.info(dig_cmd)

        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " tail -200 /var/log/syslog | grep -ir \'BLACKLIST DROP .*\' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        assert re.search(r''+str(sid_value)+'|Blacklist:'+str(config.client_ip)+'.*cat\=\"BLACKLIST DROP.*\"',out1)
        logging.info('-'*30+"Test Case 143 Execution Completed"+'-'*30)
  
    @pytest.mark.run(order=144)
    def test_144_delete_custom_rule_blacklist_udp_ip_prior_to_rate_limiting(self):
        logging.info('-'*30+"Test Case 144 Execution Started"+'-'*30)
        logging.info('-'*15+"Delete custom rule for Blacklist UDP IP Prior to Rate Limiting"'-'*15)
        logging.info('-'*15+"Get ThreatProtection Grid rule for Pass"'-'*15)
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name=Blacklist:'+config.client_ip)
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2


        data={"name":"Blacklist:+config.client_ip"}
        modify_drop_field = ib_NIOS.wapi_request('DELETE',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field

        logging.info('-'*30+"Test Case 144 Execution Completed"+'-'*30)


    @pytest.mark.run(order=145)
    def test_145_add_custom_rule_blacklist_drop_tcp_ip_prior_to_rate_limiting(self):
        logging.info('-'*30+"Test Case 145 Execution Started"+'-'*30)
        logging.info("Get Member Threat Protection using member:threatprotection object")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']

        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120104000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)

        add_custom_rule={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"DROP","log_severity":"WARNING","params":[{"name": "EVENTS_PER_SECOND","value":"1"},{"name": "BLACKLISTED_IP","value":config.client_ip}]}}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:grid:rule",fields=json.dumps(add_custom_rule))
        logging.info(response)
        #print response
        sleep(10)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90) 
        
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Blacklist:'+config.client_ip)
        custom_rule=json.loads(get_custom_rule)
        print get_custom_rule
        print type(custom_rule)

        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value

        assert custom_rule[0]["name"] == "Blacklist:"+config.client_ip
        logging.info('-'*30+"Test Case 145 Execution Completed"+'-'*30)

    @pytest.mark.run(order=146)
    def test_146_validate_sid_in_rules_txt_file_and_validated_functionality_of_added_blacklist_udp_drop_prior_to_rate_limiting(self):
        logging.info('-'*30+"Test Case 146 Execution Completed"+'-'*30)   
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Blacklist:'+config.client_ip)
        custom_rule=json.loads(get_custom_rule)
        print get_custom_rule
        print type(custom_rule)

        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        assert re.search(r'sid\:'+str(sid_value)+'',out)
        dig_cmd = os.system('for i in {1..10};do dig @'+str(config.grid_member2_vip)+' rate_udp_modified.com +tcp +time=0 +retries=0;done')
        print dig_cmd
        logging.info(dig_cmd)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " tail -200 /var/log/syslog | grep -ir \'BLACKLIST DROP .*\' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        assert re.search(r''+str(sid_value)+'|Blacklist:'+str(config.client_ip)+'.*cat\=\"BLACKLIST DROP.*\"',out1)
 

        logging.info('-'*30+"Test Case 146 Execution Completed"+'-'*30)

    @pytest.mark.run(order=147)
    def test_147_update_blacklist_drop_tcp_ip_prior_to_rate_limiting_negative_case(self):
        logging.info('-'*30+"Test Case 147 Execution Started"+'-'*30)
        logging.info('-'*15+"Performed Get Operation for member:threatprotection"+'-'*15)
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']


        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120104000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        logging.info(rule_temp_ref)

        data={"name":"BLACKLIST DROP"}
        status,modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1_temp,fields=json.dumps(data))
        logging.info(modify_disable_field)
        assert status == 400
        print modify_disable_field
        logging.info('-'*30+"Test Case 147 Execution Completed"+'-'*30)


    @pytest.mark.run(order=148)
    def test_148_update_disable_field_false_for_custom_rule(self):
        logging.info('-'*30+"Test Case 148 Execution Started"+'-'*30)
        logging.info("Modify Disable field for custom rule with value as true")

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Blacklist:'+config.client_ip)
        custom_rule=json.loads(get_custom_rule)
        print custom_rule

        custom_name = custom_rule[0]['name']
        print custom_name
        #print ref_2
        ref_1 = custom_rule[0]['_ref']
        print ref_1

        data={"disabled":False}
        modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_1,fields=json.dumps(data))
        logging.info(modify_disable_field)
        print modify_disable_field

        get_custom_rule_ref = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Blacklist:'+config.client_ip)
        custom_rule_2=json.loads(get_custom_rule)
        custom_ref = custom_rule[0]['_ref']
        print custom_ref

        get_ref_after_disable = ib_NIOS.wapi_request('GET', object_type = custom_ref+'?_return_fields=disabled')
        #print get_ref_after_disable
        custom_rule_3=json.loads(get_ref_after_disable)
        logging.info(get_ref_after_disable)
        print get_ref_after_disable
        disable_field = custom_rule_3['disabled']
        print disable_field
        sleep(10)

        assert custom_rule_3["disabled"] == False
        logging.info('-'*30+"Test Case 148 Execution Completed"+'-'*30)


    @pytest.mark.run(order=149)
    def test_149_update_log_severity_and_type_blacklist_drop_tcp_ip_prior_to_rate_limiting(self):
        logging.info('-'*30+"Test Case 149 Execution Started"+'-'*30)
        logging.info('-'*15+"Modify Log Severity and FQDN Values in Custom Rule(Blacklist DROP UDP IP Prior to Rate Limiting)"+'-'*15)
        logging.info("Get ThreatProtection Grid rule for Whitelist")
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name=Blacklist:'+config.client_ip)
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120104000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)

        data={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"DROP","log_severity":"WARNING","params":[{"name": "EVENTS_PER_SECOND","value":"2"},{"name": "BLACKLISTED_IP","value":config.client_ip}]}}

        modify_drop_field = ib_NIOS.wapi_request('PUT',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field

        sleep(10)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name,config')
        print get_ref_disable

        validate = json.loads(get_ref_disable)
        print validate
        ref_ipv4_1 = validate['config']
        print ref_ipv4_1
        logging.info('-'*30+"Test Case 149 Execution Completed"+'-'*30)  
        

    @pytest.mark.run(order=150)
    def test_150_put_validate_sid_in_rules_txt_file_and_validated_functionality_of_blacklist_drop_tcp_ip_prior_to_rate_limiting(self):
        logging.info('-'*30+"Test Case 150 Execution Completed"+'-'*30) 
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Blacklist:'+config.client_ip)
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value

        ssh_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " grep -ir '+str(sid_value)+' /infoblox/var/atp_conf/rules.txt " '
        out = commands.getoutput(ssh_cmd)
        print out
        assert re.search(r'sid\:'+str(sid_value)+'',out)


        dig_cmd = os.system('for i in {1..10};do dig @'+str(config.grid_member2_vip)+' rate_udp_modified.com +tcp +time=0 +retries=0;done')
        print dig_cmd
        logging.info(dig_cmd)

        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member4_mgmt_vip)+' " tail -200 /var/log/syslog | grep -ir \'BLACKLIST DROP .*\' " '
        out1 = commands.getoutput(sys_log_validation)
        print out1
        assert re.search(r''+str(sid_value)+'|Blacklist:'+str(config.client_ip)+'.*cat\=\"BLACKLIST DROP.*\"',out1)
 
        
        logging.info('-'*30+"Test Case 150 Execution Completed"+'-'*30)


    @pytest.mark.run(order=151)
    def test_151_delete_custom_rule_blacklist_drop_tcp_prior_to_rate_limiting(self):
        logging.info('-'*30+"Test Case 151 Execution Started"+'-'*30)
        logging.info('-'*15+"Delete custom rule for Blacklist DROP UDP IP Prior to Rate Limiting"'-'*15)
        logging.info('-'*15+"Get ThreatProtection Grid rule for Pass"'-'*15)
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name=Blacklist:'+config.client_ip)
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2


        data={"name":"Blacklist:+config.client_ip"}
        modify_drop_field = ib_NIOS.wapi_request('DELETE',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field

        logging.info('-'*30+"Test Case 151 Execution Completed"+'-'*30)

    @pytest.mark.run(order=152)
    def test_152_update_rule_template_negative_case(self):
        logging.info('-'*30+"Test Case 152 Execution Started"+'-'*30)
        logging.info('-'*15+"Put Operation for Rule Template Negative Case"+'-'*15)
        logging.info("Get Member Threat Protection using member:threatprotection object")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']
        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']
        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120306000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)

        add_custom_rule={"name":"BLACKLIST DROP"}
        status,response = ib_NIOS.wapi_request('PUT',object_type=ref_1_temp,fields=json.dumps(add_custom_rule))
        logging.info(response)
        print response
        assert status == 400
        logging.info('-'*30+"Test Case 152 Execution Started"+'-'*30)


    @pytest.mark.run(order=153)
    def test_153_add_rule_category_in_custom_rule_negative_case(self):
        logging.info('-'*30+"Test Case 153 Execution Started"+'-'*30)
        logging.info("Get Member Threat Protection using member:threatprotection object")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']
        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']

        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120306000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)

        add_custom_rule={"name":"BLACKLIST DROP"}
        status,response = ib_NIOS.wapi_request('DELETE',object_type=ref_1_temp,fields=json.dumps(add_custom_rule))
        logging.info(response)
        print response
        assert status == 400
        logging.info('-'*30+"Test Case 153 Execution Completed"+'-'*30)



    @pytest.mark.run(order=154)
    def test_154_delete_rule_category_negative_case(self):
        logging.info('-'*30+"Test Case 154 Execution Started"+'-'*30)
        logging.info("Get Member Threat Protection using member:threatprotection object")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']

        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120306000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)

        add_custom_rule={"name":"BLACKLIST DROP"}
        status,response = ib_NIOS.wapi_request('DELETE',object_type=ref_1_temp,fields=json.dumps(add_custom_rule))
        logging.info(response)
        print response
        assert status == 400

        logging.info('-'*30+"Test Case 154 Execution Completed"+'-'*30)


    @pytest.mark.run(order=155)
    def test_155_add_rule_category_in_custom_rule_negative_case(self):
        logging.info('-'*30+"Test Case 155 Execution Started"+'-'*30)
        logging.info("Get Member Threat Protection using member:threatprotection object")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']

        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120104000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        logging.info(rule_temp_ref)

        add_custom_rule={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"DROP","log_severity":"WARNING","params":[{"name": "EVENTS_PER_SECOND","value":"1"},{"name": "BLACKLISTED_IP","value": "21.0.0.1"}]}}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:grid:rule",fields=json.dumps(add_custom_rule))
        logging.info(response)
        sleep(10)
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Blacklist:21.0.0.1')
        custom_rule=json.loads(get_custom_rule)
        ref_2 = custom_rule[0]['_ref']
        

        response1 = json.loads(ib_NIOS.wapi_request('GET',object_type=ref_2+'?_return_fields=category'))
        logging.info(response1)
        ref_category = response1["category"]
        print ref_category

        add_custom_rule={"name":"BLACKLIST DROP"}
        status,response = ib_NIOS.wapi_request('POST',object_type=ref_category,fields=json.dumps(add_custom_rule))
        logging.info(response)
        print response
        assert status == 400

        logging.info('-'*30+"Test Case 155 Execution Completed"+'-'*30)



    @pytest.mark.run(order=156)
    def test_156_put_operation_rule_category_in_custom_rule_negative_case(self):
        logging.info('-'*30+"Test Case 156 Execution Started"+'-'*30)
        logging.info("Get Member Threat Protection using member:threatprotection object")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']

        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120104000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        logging.info(rule_temp_ref)

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Blacklist:21.0.0.1')
        custom_rule=json.loads(get_custom_rule)
        ref_2 = custom_rule[0]['_ref']

        response1 = json.loads(ib_NIOS.wapi_request('GET',object_type=ref_2+'?_return_fields=category'))
        logging.info(response1)
        ref_category = response1["category"]
        print ref_category

        add_custom_rule={"name":"BLACKLIST DROP"}
        status,response = ib_NIOS.wapi_request('PUT',object_type=ref_category,fields=json.dumps(add_custom_rule))
        logging.info(response)
 
        print response
        assert status == 400

        logging.info('-'*30+"Test Case 156 Execution Completed"+'-'*30)
    

    @pytest.mark.run(order=157)
    def test_157_delete_rule_category_in_custom_rule_negative_case(self):
        logging.info('-'*30+"Test Case 157 Execution Started"+'-'*30)
        logging.info("Get Member Threat Protection using member:threatprotection object")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']

        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120104000\
        &ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[1]['_ref']

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        logging.info(rule_temp_ref)

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Blacklist:21.0.0.1')
        custom_rule=json.loads(get_custom_rule)
        ref_2 = custom_rule[0]['_ref']

        response1 = json.loads(ib_NIOS.wapi_request('GET',object_type=ref_2+'?_return_fields=category'))
        logging.info(response1)
        ref_category = response1["category"]
        print ref_category

        add_custom_rule={"name":"BLACKLIST DROP"}
        status,response = ib_NIOS.wapi_request('DELETE',object_type=ref_category,fields=json.dumps(add_custom_rule))
        logging.info(response)
    
        print response
        assert status == 400

        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name=Blacklist:21.0.0.1')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2


        data={"name":"Blacklist:21.0.0.1"}
        modify_drop_field = ib_NIOS.wapi_request('DELETE',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)


        logging.info('-'*30+"Test Case 157 Execution Completed"+'-'*30)


    @pytest.mark.run(order=158)
    def test_158_publish_changes_with_sequential(self):
        logging.info('-'*30+"Test Case 158 Execution Started"+'-'*30)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SEQUENTIALLY","sequential_delay":15}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(30)
        logging.info("Audit Log Validation") 
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -200 /infoblox/var/audit.log | grep -ir PublishChanges  " '
        out1 = commands.getoutput(audit_log_validation)
        print out1
        logging.info(out1)
        assert re.search(r'PublishChanges\:.*Args service_option\=\"ALL\"\,sequential_delay\=15\,member_order\=\"SEQUENTIALLY\"',out1)
        logging.info('-'*30+"Test Case 158 Execution Completed"+'-'*30)


    @pytest.mark.run(order=159)
    def test_159_publish_changes_with_service_changes_as_atp_squentially(self):
        logging.info('-'*30+"Test Case 159 Execution Started"+'-'*30)

        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SEQUENTIALLY","sequential_delay":15,"services":"ATP"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(20)
        logging.info("Audit log Validation") 
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -200 /infoblox/var/audit.log | grep -ir PublishChanges  " '
        out1 = commands.getoutput(audit_log_validation)
        print out1
        logging.info(out1)
        assert re.search(r'PublishChanges\:.*Args service_option\=\"ATP\"\,sequential_delay\=15\,member_order\=\"SEQUENTIALLY\"',out1) 
        logging.info('-'*30+"Test Case 159 Execution Completed"+'-'*30)


    @pytest.mark.run(order=160)
    def test_160_publish_changes_with_simultaneous(self):
        logging.info('-'*30+"Test Case 160 Execution Started"+'-'*30)

        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(20)
        logging.info("Audit Log Validation for Publish Changes")
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -200 /infoblox/var/audit.log | grep -ir PublishChanges  " '
        out1 = commands.getoutput(audit_log_validation)
        print out1
        logging.info(out1)   
        assert re.search(r'PublishChanges\:.*Args service_option\=\"ALL\"\,sequential_delay\=0\,member_order\=\"SIMULTANEOUSLY\"',out1)
        logging.info('-'*30+"Test Case 160 Execution Completed"+'-'*30)


    @pytest.mark.run(order=161)
    def test_161_publish_changes_with_simultaneous_for_member_level(self):
        logging.info('-'*30+"Test Case 161 Execution Started"+'-'*30)

        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY","member":config.grid_fqdn}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(20)
        logging.info("Audit Log Validation for Publish Changes")
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -200 /infoblox/var/audit.log | grep -ir PublishChanges  " '
        out1 = commands.getoutput(audit_log_validation)
        print out1
        logging.info(out1)
        regex = 'PublishChanges:.*Args service_option="ALL",grid_member=Member:'+str(config.grid_fqdn)
        assert re.search(regex,out1) 
        logging.info('-'*30+"Test Case 161 Execution Completed"+'-'*30)


    @classmethod
    def teardown_class(cls):
        """ teardown any state that was previously setup with a call to
        setup_class.
        """
        logging.info("TEAR DOWN METHOD")   


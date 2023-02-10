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
        logging.info("Adding Profiles with Inherited Ruleset")
        add_profile={"name":"profile_mani_mdu_1"} 
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:profile",fields=json.dumps(add_profile))
        logging.info(response)
        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:profile")
        logging.info(get_ref)
        res = json.loads(get_ref)
        #print res 
        get_profile_name_1 = json.loads(get_ref)[0]['name']
        print get_profile_name_1

        for i in res:
            logging.info("found")
            assert i["name"] == get_profile_name_1
        logging.info("-----------Test Case 1 Execution Completed------------")  
        
    

    
    @pytest.mark.run(order=2)
    def test_2_add_profile_with_inherited(self):
        logging.info("-----------Test Case 2 Execution Started------------") 
        logging.info("Adding Profiles with Inherited Ruleset")

        logging.info("Get Ruleset Version for adding profile for overridden operation")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        logging.info("============================")
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        print ref_version_1
        ref_version_2 = json.loads(get_ruleset)[1]['version']
        print ref_version_2


        add_profile={"name":"profile_mani_mdu_2","current_ruleset":ref_version_2}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:profile",fields=json.dumps(add_profile))
        logging.info(response)
        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:profile")
        logging.info(get_ref)
        res1 = json.loads(get_ref)
        print res1

        get_profile_name_2 = json.loads(get_ref)[0]['name']
        print get_profile_name_2

        get_profile_name_1 = json.loads(get_ref)[1]['name']
        print get_profile_name_1
        # Edited

        logging.info("-----------Test Case 2 Execution Completed------------")

    @pytest.mark.run(order=3)
    def test_3_associate_member_for_profile(self):
        logging.info("Associated Member for Profiles")
        logging.info("-----------Test Case 3 Execution Started------------")
        logging.info("Get Ruleset Version for adding profile for overridden operation")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:profile")
        logging.info(get_ruleset)
        logging.info("============================")
        res = json.loads(get_ruleset)
        ref_1 = json.loads(get_ruleset)[0]['_ref']
        print ref_1
        ref_2 = json.loads(get_ruleset)[1]['_ref']
        print ref_2

        print config.grid_member1_fqdn
        print "---"
        data={"members":[config.grid_member1_fqdn]}
        get_status = ib_NIOS.wapi_request('PUT',object_type=ref_1,fields=json.dumps(data))
        print get_status
        logging.info(get_status)
        # Edited

        logging.info("-----------Test Case 3 Execution Completed------------")  

    @pytest.mark.run(order=4)
    def test_4_disable_multiple_dns_tcp_request_for_profile_as_true(self):
        logging.info("Modify use_disable_multiple_dns_tcp_request as true")
        logging.info("-----------Test Case 4 Execution Started------------")  

        logging.info("Modify and Validate use_disable_multiple_dns_tcp_request in Profile Editor")
        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:profile")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[0]['_ref']

        data={"use_disable_multiple_dns_tcp_request":True}
        get_status = ib_NIOS.wapi_request('PUT',object_type=ref,fields=json.dumps(data))
        logging.info(get_status)
        print get_status


        get_ref_1 = ib_NIOS.wapi_request('GET', object_type="threatprotection:profile")
        logging.info(get_ref_1)
        res1 = json.loads(get_ref_1)
        ref1 = json.loads(get_ref_1)[0]['_ref']


        get_multiple_request = ib_NIOS.wapi_request('GET', object_type = ref1+'?_return_fields=use_disable_multiple_dns_tcp_request')
        logging.info("============================")
        factory = json.loads(get_multiple_request)
        logging.info(factory)
        assert factory["use_disable_multiple_dns_tcp_request"] == True
        logging.info("-----------Test Case 4 Execution Completed------------")   

    @pytest.mark.run(order=5)
    def test_5_disable_multiple_dns_tcp_request_for_profile_as_false(self):
        logging.info("-----------Test Case 5 Execution Started------------")
        logging.info("Modify use_disable_multiple_dns_tcp_request as false")

        logging.info("Modify and Validate use_disable_multiple_dns_tcp_request")
        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:profile")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[0]['_ref']

        data={"use_disable_multiple_dns_tcp_request":False}
        get_status = ib_NIOS.wapi_request('PUT',object_type=ref,fields=json.dumps(data))
        print get_status


        get_ref_1 = ib_NIOS.wapi_request('GET', object_type="threatprotection:profile")
        logging.info(get_ref_1)
        res1 = json.loads(get_ref_1)
        ref1 = json.loads(get_ref_1)[0]['_ref']


        get_multiple_request = ib_NIOS.wapi_request('GET', object_type = ref1+'?_return_fields=use_disable_multiple_dns_tcp_request')
        logging.info("============================")
        factory = json.loads(get_multiple_request)
        logging.info(factory) 
        assert factory["use_disable_multiple_dns_tcp_request"] == False
        logging.info("-----------Test Case 5 Execution Completed------------") 
   

    @pytest.mark.run(order=6)
    def test_6_modify_events_per_second_per_rule_true(self):
        logging.info("-----------Test Case 6 Execution Started------------")   
        logging.info("Modify events_per_second_per_rule in threatprotection:profile")


        logging.info("Modify and Validate events_per_second_per_rule in threatprotection:profile")
        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:profile")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[0]['_ref']

        data={"events_per_second_per_rule":24,"use_events_per_second_per_rule":True}
        get_status = ib_NIOS.wapi_request('PUT',object_type=ref,fields=json.dumps(data))
        print get_status


        get_ref_1 = ib_NIOS.wapi_request('GET', object_type="threatprotection:profile")
        logging.info(get_ref_1)
        res1 = json.loads(get_ref_1)
        ref1 = json.loads(get_ref_1)[0]['_ref']


        get_multiple_request = ib_NIOS.wapi_request('GET', object_type = ref1+'?_return_fields=events_per_second_per_rule')
        logging.info("============================")
        factory = json.loads(get_multiple_request)
        logging.info(factory)
        assert factory["events_per_second_per_rule"] == 24
        logging.info("-----------Test Case 6 Execution Completed------------")  


    @pytest.mark.run(order=7)
    def test_7_modify_per_second_per_rule_false(self):
        logging.info("-----------Test Case 7 Execution Started------------")
        logging.info("Modify events_per_second_per_rule set to false")


        logging.info("Modify and Validate events_per_second_per_rule in threatprotection:profile")
        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:profile")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[0]['_ref']

        data={"use_events_per_second_per_rule":False}
        get_status = ib_NIOS.wapi_request('PUT',object_type=ref,fields=json.dumps(data))
        print get_status


        get_ref_1 = ib_NIOS.wapi_request('GET', object_type="threatprotection:profile")
        logging.info(get_ref_1)
        res1 = json.loads(get_ref_1)
        ref1 = json.loads(get_ref_1)[0]['_ref']


        get_multiple_request = ib_NIOS.wapi_request('GET', object_type = ref1+'?_return_fields=events_per_second_per_rule,use_events_per_second_per_rule')
        factory = json.loads(get_multiple_request)
        assert factory["use_events_per_second_per_rule"] == False
        logging.info(factory) 
        logging.info("-----------Test Case 7 Execution Completed------------")  

    
    @pytest.mark.run(order=8)
    def test_8_modify_overridden_ruleset(self):
        logging.info("-----------Test Case 8 Execution Started------------")
        logging.info("Modify Inherited to Overridden Ruleset")

        logging.info("Get Ruleset version to perform overridden ")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:profile")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_1 = json.loads(get_ruleset)[0]['_ref']
        print ref_1
        ref_2 = json.loads(get_ruleset)[1]['_ref']
        print ref_2

        get_version = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_version)
        res = json.loads(get_version)
        ref_version_1 = json.loads(get_version)[0]['version']
        print ref_version_1
        ref_version_2 = json.loads(get_version)[1]['version']
        print ref_version_2



        data={"current_ruleset":ref_version_2}
        get_status = ib_NIOS.wapi_request('PUT',object_type=ref_2,fields=json.dumps(data))
        print get_status
        logging.info(get_status)

        get_version = ib_NIOS.wapi_request('GET', object_type = ref_2+'?_return_fields=current_ruleset')
        factory = json.loads(get_version)
        logging.info(factory)   
        assert factory["current_ruleset"] == ref_version_2
        logging.info("-----------Test Case 8 Execution Completed------------")   

    @pytest.mark.run(order=9)
    def test_9_modify_overridden_ruleset_false(self):
        logging.info("-----------Test Case 9 Execution Started------------")
        logging.info("Modify Inherited to Overridden Ruleset as false")

        logging.info("Get Ruleset version to perform overridden ")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:profile")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_1 = json.loads(get_ruleset)[0]['_ref']
        print ref_1
        ref_2 = json.loads(get_ruleset)[1]['_ref']
        print ref_2

        data={"use_current_ruleset":False}
        get_status = ib_NIOS.wapi_request('PUT',object_type=ref_2,fields=json.dumps(data))
        print get_status

        get_version = ib_NIOS.wapi_request('GET', object_type = ref_2+'?_return_fields=use_current_ruleset')
        factory = json.loads(get_version)
        logging.info(factory)
        assert factory["use_current_ruleset"] == False
        logging.info("-----------Test Case 9 Execution Completed------------")
 
    
    @pytest.mark.run(order=10)
    def test_10_search_name_for_profile(self):
        logging.info("-----------Test Case 10 Execution Started------------")  
        logging.info("Validated Threat Protection Profile-Search for 'name' field")
        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:profile")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']

        get_status = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=current_ruleset,name')
        logging.info(get_status)
        current_ruleset_1 = json.loads(get_status)['current_ruleset']
        print current_ruleset_1


        search_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:profile?current_ruleset=%s"%current_ruleset_1)
        ref_51 = json.loads(search_ruleset)[0]['_ref']

        get_versi = ib_NIOS.wapi_request('GET', object_type = ref_51+'?_return_fields=current_ruleset')
        res1 = json.loads(get_versi)
        val_version = res1['current_ruleset']
        print val_version
        logging.info(val_version)
        assert res1["current_ruleset"] == current_ruleset_1
        logging.info("-----------Test Case 10 Execution Completed------------")  
   

    @pytest.mark.run(order=11)
    def test_11_delete_profile_for_name(self):
        logging.info("-----------Test Case 11 Execution Started------------") 
        logging.info("Adding Profiles with Inherited Ruleset")
        add_profile_3={"name":"profile_mani_mdu_3"}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:profile",fields=json.dumps(add_profile_3))


        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:profile")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[2]['_ref']
        print ref


        data ={"name": "profile_mani_mdu_3"}
        get_status = ib_NIOS.wapi_request('DELETE', object_type=ref,fields=json.dumps(data))
        print get_status
        logging.info(get_status)
        # Need to validate the deleted status
         
        logging.info("-----------Test Case 11 Execution Completed------------")


    @pytest.mark.run(order=12)
    def test_12_delete_profile_using_comment_field(self):
        logging.info("-----------Test Case 12 Execution Started------------")
        logging.info("Adding Profiles with Inherited Ruleset")
        add_profile_4={"name":"profile_mani_mdu_4","comment":"modified_comment"}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:profile",fields=json.dumps(add_profile_4))


        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:profile")
        logging.info(get_ref)

        res = json.loads(get_ref)
        ref = json.loads(get_ref)[2]['_ref']
        print ref
        get_status = ib_NIOS.wapi_request('GET', object_type = ref+'?_return_fields=comment,name')
        logging.info("============================")
        factory = json.loads(get_status)


        data ={"comment": "modified_comment"}
        get_status = ib_NIOS.wapi_request('DELETE', object_type=ref,fields=json.dumps(data))
        # Need to validate the deleted status
        logging.info("-----------Test Case 12 Execution Completed------------") 

    @pytest.mark.run(order=13)
    def test_13_adding_cloned_profile_using_source_profile(self):
        logging.info("-----------Test Case 13 Execution Started------------")
        logging.info("Adding Cloned Profile")

        add_profile_5={"name":"profile_mani_mdu_5","source_profile":"profile_mani_mdu_1"}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:profile",fields=json.dumps(add_profile_5))

        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:profile")
        logging.info(get_ref)
        res = json.loads(get_ref)
        get_profile_name_1 = json.loads(get_ref)[2]['name']
        logging.info(get_profile_name_1)
        print get_profile_name_1

        search_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:profile")
        res1 = json.loads(search_ruleset)
        print search_ruleset
        # Edited
  
        logging.info(res1) 
        logging.info("-----------Test Case 13 Execution Completed------------")  

    @pytest.mark.run(order=14)
    def test_14_added_profile_using_source_member(self):
        logging.info("-----------Test Case 14 Execution Started------------")  
        logging.info("Added profile using source_member")

        add_profile_5={"name":"profile_mani_mdu_6","source_member":config.grid_member2_fqdn}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:profile",fields=json.dumps(add_profile_5))
        print response
        logging.info(response)  
        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:profile")
        logging.info(get_ref)
        print get_ref
        res = json.loads(get_ref)
        get_profile_name_1 = json.loads(get_ref)[2]['name']
        # Edited

        logging.info("-----------Test Case 14 Execution Completed------------")   
     
    @pytest.mark.run(order=15)
    def test_15_search_name_for_profile(self):
        logging.info("-----------Test Case 15 Execution Started------------")
        logging.info("Delete Cloned Profile")
        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:profile")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[2]['_ref']
        print ref
        logging.info(ref)  

        ref_2 = json.loads(get_ref)[3]['_ref']
        print ref_2
        logging.info(ref_2)
    
           
        data ={"name":"profile_mani_mdu_5"}
        get_status = ib_NIOS.wapi_request('DELETE', object_type=ref,fields=json.dumps(data))

        data_delete ={"name": "profile_mani_mdu_6"}
        get_status = ib_NIOS.wapi_request('DELETE', object_type=ref_2,fields=json.dumps(data_delete))
        # Need to validate using assert 
        logging.info("-----------Test Case 15 Execution Completed------------")  
         

    
    @pytest.mark.run(order=16)
    def test_16_validate_profile_name_get_operation(self):
        logging.info("-----------Test Case 16 Execution Started------------")
        logging.info("GET Operation for member:threatprotection object")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[0]['_ref']
        print ref
        logging.info(ref)

        get_versi = ib_NIOS.wapi_request('GET', object_type = ref+'?_return_fields=profile,hardware_type,hardware_model')
        res1 = json.loads(get_versi)
        print res1
        logging.info(res1) 
        profile_name = res1['profile']
        print profile_name
        logging.info(profile_name)
        assert res1["profile"] == profile_name
        logging.info("-----------Test Case 16 Execution Completed------------")

    @pytest.mark.run(order=17)
    def test_17_validate_hardware_model_get_operation(self):
        logging.info("-----------Test Case 17 Execution Started------------") 
        logging.info("GET Operation for member:threatprotection object")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[0]['_ref']
        print ref

        get_hw_type = ib_NIOS.wapi_request('GET', object_type = ref+'?_return_fields=profile,hardware_type,hardware_model')
        res1 = json.loads(get_hw_type)
        print res1
        logging.info(res1)  
        hw_name = res1['hardware_model']
        print hw_name
        logging.info(hw_name)
        assert res1["hardware_model"] == hw_name
        logging.info("-----------Test Case 17 Execution Completed------------")


    @pytest.mark.run(order=18)
    def test_18_update_another_profile_in_member_1(self):
        logging.info("-----------Test Case 18 Execution Started------------") 
        logging.info("GET Operation for member:threatprotection object")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[0]['_ref']
        print ref
        logging.info(ref)
        logging.info("Update profile_mani_mdu_1 to profile_mani_mdu_2 in Member 1")
        data={"profile":"profile_mani_mdu_2"}
        get_status = ib_NIOS.wapi_request('PUT',object_type=ref,fields=json.dumps(data))
        print get_status


        get_versi = ib_NIOS.wapi_request('GET', object_type = ref+'?_return_fields=profile,hardware_type,hardware_model')
        res1 = json.loads(get_versi)
        print res1
        logging.info(res1)
        profile_name = res1['profile']
        print profile_name
        logging.info(profile_name)
        assert res1["profile"] == profile_name
        sleep(30)
        logging.info("-----------Test Case 18 Execution Completed------------")  


    @pytest.mark.run(order=19)
    def test_19_update_another_profile_in_member_1(self):
        logging.info("-----------Test Case 19 Execution Started------------")
        logging.info("GET Operation for member:threatprotection object")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[0]['_ref']
        print ref
        logging.info(ref)
        logging.info("Update profile_mani_mdu_1 to profile_mani_mdu_2 in Member 1")
        data={"profile":"profile_mani_mdu_1"}
        get_status = ib_NIOS.wapi_request('PUT',object_type=ref,fields=json.dumps(data))
        print get_status
        logging.info(get_status)  


        get_versi = ib_NIOS.wapi_request('GET', object_type = ref+'?_return_fields=profile,hardware_type,hardware_model')
        res1 = json.loads(get_versi)
        print res1
        profile_name = res1['profile']
        print profile_name
        logging.info(profile_name)
        assert res1["profile"] == profile_name
        logging.info("-----------Test Case 19 Execution Completed------------")  

    @pytest.mark.run(order=20)
    def test_20_search_hw_model_for_member_threatprotection(self):
        logging.info("-----------Test Case 20 Execution Started------------")
        logging.info("Validated Threat Protection Profile-Search for 'name' field")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']

        get_status = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=hardware_model')
        current_hw_model = json.loads(get_status)['hardware_model']
        print current_hw_model
        logging.info(current_hw_model)


        search_hw_model = ib_NIOS.wapi_request('GET', object_type="member:threatprotection?hardware_model=%s"%current_hw_model)
        ref_51 = json.loads(search_hw_model)[0]['_ref']
        logging.info(search_hw_model)
  
        get_hw_model = ib_NIOS.wapi_request('GET', object_type = ref_51+'?_return_fields=hardware_model')
        res1 = json.loads(get_hw_model)
        logging.info(res1)

        val_version = res1['hardware_model']
        print val_version
        logging.info(val_version)
        
        assert res1["hardware_model"] == current_hw_model
        logging.info("-----------Test Case 20 Execution Completed------------")  

    @pytest.mark.run(order=21)
    def test_21_search_hw_type_for_hw_type(self):
        logging.info("-----------Test Case 21 Execution Started------------") 
        logging.info("Validated Threat Protection Profile-Search for 'name' field")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[1]['_ref']

        get_status = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=hardware_type')
        current_hw_type = json.loads(get_status)['hardware_type']
        print current_hw_type
        logging.info(current_hw_type)


        search_hw_model = ib_NIOS.wapi_request('GET', object_type="member:threatprotection?hardware_type=%s"%current_hw_type)
        ref_51 = json.loads(search_hw_model)[0]['_ref']

        get_hw_type = ib_NIOS.wapi_request('GET', object_type = ref_51+'?_return_fields=hardware_type')
        res1 = json.loads(get_hw_type)
        logging.info(res1)
        val_version = res1['hardware_type']
        print val_version
        logging.info(res1) 
        assert res1["hardware_type"] == current_hw_type
        logging.info("-----------Test Case 21 Execution Completed------------")  


    @pytest.mark.run(order=22)
    def test_22_update_disable_field_true_for_custom_rule(self):
        logging.info("-----------Test Case 22 Execution Started------------")
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
        add_custom_rule={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"DROP","log_severity":"WARNING","params":[{"name": "EVENTS_PER_SECOND","value":"1"},{"name":"FQDN","value":"mani_mdu.com"}]}}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:grid:rule",fields=json.dumps(add_custom_rule))
        logging.info(response)
        logging.info("-----------Test Case 22 Execution Completed------------")  
    
    @pytest.mark.run(order=23)
    def test_23_update_disable_field_false_for_custom_rule(self):
        logging.info("-----------Test Case 23 Execution Started------------")
        logging.info("Modify Disable field for custom rule with value as true")
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:profile:rule?profile=profile_mani_mdu_1&rule=Blacklist:mani_mdu.com')
        factory = json.loads(get_custom_rule)
        print factory
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disable,profile,rule')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2


        data={"disable":True}
        modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_disable_field) 
        print modify_disable_field

        get_ref_after_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disable,profile,rule')
        print get_ref_after_disable
        logging.info(get_ref_after_disable)
        ref_2 = json.loads(get_ref_after_disable)['disable']
        print ref_2

        validate = json.loads(get_ref_after_disable)
        assert validate["disable"] == ref_2
        logging.info("-----------Test Case 23 Execution Completed------------")
    

    @pytest.mark.run(order=24)
    def test_24_update_disable_field_false_for_custom_rule(self):
        logging.info("-----------Test Case 24 Execution Started------------")   
        logging.info("Modify Disable field for custom rule with value as true")
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:profile:rule?profile=profile_mani_mdu_1&rule=Blacklist:mani_mdu.com')
        factory = json.loads(get_custom_rule)
        print factory
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disable,profile,rule')
        print get_ref_disable
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2


        data={"disable":False}
        modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref_2,fields=json.dumps(data))
        print modify_disable_field

        get_ref_after_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disable,profile,rule')
        print get_ref_after_disable
        ref_2 = json.loads(get_ref_after_disable)['disable']
        print ref_2

        validate = json.loads(get_ref_after_disable)
        assert validate["disable"] == ref_2
        logging.info("-----------Test Case 24 Execution Completed------------")   


    @pytest.mark.run(order=25)
    def test_25_addd_duplicate_profile_negative_case(self):
        logging.info("-----------Test Case 25 Execution Started------------")
        logging.info("Adding Duplicate Profile")
        add_profile={"name":"profile_1"}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:profile",fields=json.dumps(add_profile))
        logging.info(response)

        #print response
        #print status

        add_duplicate_profile={"name":"profile_1"}
        status,response1 = ib_NIOS.wapi_request('POST',object_type="threatprotection:profile",fields=json.dumps(add_duplicate_profile))
        logging.info(response)
        sleep(10)
        print response
        print status

        assert status == 400
        logging.info("-----------Test Case 25 Execution Completed------------")

    @pytest.mark.run(order=26)
    def test_25_add_profile_with_more_than_256_characters_negative_case(self):
        logging.info("-----------Test Case 26 Execution Started------------")
        logging.info("Adding Profile with more than 64 Characters")
        add_profile={"name":"profile_11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111"}
        status,response = ib_NIOS.wapi_request('POST',object_type="threatprotection:profile",fields=json.dumps(add_profile))
        logging.info(response)
        print response
        print status
        assert status == 400
        logging.info("-----------Test Case 26 Execution Started------------")
    
    @pytest.mark.run(order=27)
    def test_27_add_profile_with_idn_characters(self):
        logging.info("-----------Test Case 27 Execution Started------------")
        logging.info("Adding Profile with name as IDN Characters")
        add_profile={"name":"今天"}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:profile",fields=json.dumps(add_profile))
        logging.info(response)
        print response
        # Edited 
        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:profile")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[3]['_ref']
        print ref
        logging.info(ref)

        logging.info("-----------Test Case 27 Execution Completed------------")


    @pytest.mark.run(order=28)
    def test_28_add_profile_with_same_name_after_delete_operation(self):
        logging.info("-----------Test Case 28 Execution Started------------")
        logging.info("GET the ThreatProtection Profile Rule")

        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:profile")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[2]['_ref']
        print ref

        logging.info("Deleting the Profile profile_1")
        data ={"name": "profile_1"}
        get_status = ib_NIOS.wapi_request('DELETE', object_type=ref,fields=json.dumps(data))
        print get_status
        logging.info(get_status)
        sleep(10)
        logging.info("Adding the Profile profile_1 after Deleting the Profile profile_1")
        add_profile_3={"name":"profile_1"}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:profile",fields=json.dumps(add_profile_3))

        logging.info("-----------Test Case 28 Execution Completed------------")

    @pytest.mark.run(order=29)
    def test_29_modify_rulesets_for_the_added_profile(self):

        logging.info("-----------Test Case 29 Execution Started------------")
        logging.info("GET the ThreatProtection Profile Rule")

        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:profile")
        logging.info(get_ref)
        factory = json.loads(get_ref)
        print factory
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[3]['_ref']
        name = json.loads(get_ref)[3]['name']


        get_version = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_version)
        res = json.loads(get_version)
        ref_version_1 = json.loads(get_version)[0]['version']
        print ref_version_1
        ref_version_2 = json.loads(get_version)[1]['version']
       # print ref_version_2


        data={"current_ruleset":ref_version_1}
        get_status = ib_NIOS.wapi_request('PUT',object_type=ref,fields=json.dumps(data))
        print get_status
        logging.info(get_status)


        get_version = ib_NIOS.wapi_request('GET', object_type = ref+'?_return_fields=current_ruleset')
        factory = json.loads(get_version)
        logging.info(factory)
        assert factory["current_ruleset"] == ref_version_1
        logging.info("-----------Test Case 29 Execution Completed------------")

    @pytest.mark.run(order=30)
    def test_30_added_comments_with_idn_characters_for_the_added_profile(self):

        logging.info("-----------Test Case 30 Execution Started------------")
        logging.info("GET the ThreatProtection Profile Rule")

        get_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:profile")
        logging.info(get_ref)
        factory = json.loads(get_ref)
        print factory
        res = json.loads(get_ref)
        ref = json.loads(get_ref)[3]['_ref']
        name = json.loads(get_ref)[3]['name']


        get_version = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_version)


        data={"comment":"今天"}
        get_status = ib_NIOS.wapi_request('PUT',object_type=ref,fields=json.dumps(data))
        print get_status
        logging.info(get_status)
        logging.info("-----------Test Case 30 Execution Completed------------")
        get_ref_21 = ib_NIOS.wapi_request('GET', object_type="threatprotection:profile")
        logging.info(get_ref_21)
        factory = json.loads(get_ref_21)
        print factory
        res = json.loads(get_ref_21)
        ref21 = json.loads(get_ref_21)[3]['_ref']


        get_comment = ib_NIOS.wapi_request('GET', object_type = ref21+'?_return_fields=comment')
        factory = json.loads(get_comment)
        logging.info(factory)


    @classmethod
    def teardown_class(cls):
        """ teardown any state that was previously setup with a call to
        setup_class.
        """
        logging.info("TEAR DOWN METHOD")   


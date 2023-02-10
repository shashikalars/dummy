import re
import config
import pytest
import unittest
import logging
import subprocess
import os
import json
import ib_utils.ib_NIOS as ib_NIOS
from time import sleep
import commands
import json, ast
import time
import sys
import pexpect
from ib_utils.log_capture import log_action as log
from ib_utils.log_validation import log_validation as logv

def nsupdate_add(name,ttl,record_type,zone,record_data):
    child = pexpect.spawn ('ssh -o StrictHostKeyChecking=no test2@10.36.201.11')
    child.logfile=sys.stdout
    child.expect (':')
    child.sendline ('infoblox')
    child.expect ('$')
    #child.sendline('ls -ltr')
    child.sendline ('nsupdate')
    child.expect ('>')
    child.sendline ('server '+config.grid_vip)
    child.expect ('>')
    child.sendline (('update add '+ ' '+str(name)+'.'+str(zone)+' '+str(ttl)+' '+str(record_type)+' '+str(record_data)))
    child.expect ('>')
    child.sendline ('send')
    child.expect ('>')


auth_zone={"fqdn": "source.com","allow_query": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}],"allow_update": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}]}
sub_zone={"fqdn": "sub_zone","allow_query": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}],"allow_update": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}]}

def get_reference_for_unknown_records(record_ref):
     ref=record_ref
     logging.info("Fetching values for Unknown Resource records")
     get_ref = ib_NIOS.wapi_request('GET',object_type=record_ref+"?_return_fields=name,view,zone,record_type,creator")
     logging.info(get_ref)
     res = json.loads(get_ref)
     return res

def validate_CLI(username,password,role_list):
    try:    
	child = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+username+'@'+config.grid_vip)
        child.expect ('password.*:')
        child.sendline (password)
        child.expect ('Infoblox >',timeout=60)
        
        for key,value in role_list.iteritems():
            print (key,value)
            child.sendline(key)
            child.expect(value)
            assert True

    except Exception as e:
        print(e)
        assert False

    finally:
        child.sendline("exit")
        child.close()
        os.system("/import/tools/lab/bin/reset_console -H "+config.vmid)
        sleep(20)
        
class NIOSSPT_10291(unittest.TestCase):
#logging.basicConfig(filename='example.log', filemode='w', level=logging.DEBUG)
    
        @pytest.mark.run(order=1)
        def test_001_start_dns(self):
            member_ref=ib_NIOS.wapi_request('GET',object_type="member:dns")
            member_ref=json.loads(member_ref)
            logging.info (member_ref)
            logging.info ("__________________________________")
            dns_ref=member_ref[0]['_ref']
            condition=ib_NIOS.wapi_request('GET',object_type=dns_ref+"?_return_fields=enable_dns")
            logging.info (condition)
            data={"enable_dns": True}
            enable_dns_ref = ib_NIOS.wapi_request('PUT', ref=dns_ref, fields=json.dumps(data))
            logging.info (enable_dns_ref)
            logging.info ("*************************************")
            com=json.loads(enable_dns_ref)+"?_return_fields=enable_dns"
            logging.info (com)
            new_member_ref=ib_NIOS.wapi_request('GET',object_type=com)
            logging.info (new_member_ref)
            logging.info ("####################################")
            logging.info (condition)
            logging.info ("++++++++++++++++++++++++++++++++")
            logging.info (new_member_ref)
            if (condition==new_member_ref):
               assert True
               logging.info ("DNS service enabled")
            else:
               assert False
               logging.info ("Not enabled")
 
         
        @pytest.mark.run(order=2)
        def test_002_Add_Authoritative_zone(self):
            logging.info("Create Auth Zone")
            grid_member=config.grid_fqdn
            response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(auth_zone))
            print response
            read  = re.search(r'201',response)
            for read in  response:
                assert True
            logging.info("zone is created")
            logging.info("Create grid_primary with required fields")
            get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth")
            logging.info(get_ref)
            res = json.loads(get_ref)
            ref1 = json.loads(get_ref)[0]['_ref']
            print ref1

            data = {"grid_primary": [{"name": config.grid_fqdn,"stealth":False}]}
            response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
            logging.info(response)
            logging.info("============================")
            print response    

            logging.info("Restart services")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            print("System Restart is done successfully")
            sleep(30)
        
        
        
        @pytest.mark.run(order=3)
        def test_003_lock_zone(self):
            logging.info("Create grid_primary with required fields")
            get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth")
            logging.info(get_ref)
            res = json.loads(get_ref)
            ref1 = json.loads(get_ref)[0]['_ref']
            print ref1

            data = {"locked":True}
            response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
            logging.info(response)
            print response
            read  = re.search(r'201',response)
            for read in  response:
                assert True
            logging.info("zone locked successfully")
            print response
        
        @pytest.mark.run(order=4)
        def test_004_add_a_record_in_zone(self):
            logging.info("Create A record")
            data={"name":"arec1.source.com","ipv4addr":"2.2.2.2","view": "default","creator":"DYNAMIC"}
            response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data))
            print(response)
            if (response[0]!=400):
               assert True
               print ("Added A record")
            else:
               print ("A record already exists")
            logging.info("Test Case 4 Execution Completed")


        
        @pytest.mark.run(order=5)
        def test_005_modify_scavenging_settings(self):
            get_ref = ib_NIOS.wapi_request('GET',object_type="grid:dns")
            ref1 = json.loads(get_ref)[0]['_ref']
            data={"scavenging_settings": {"ea_expression_list": [],"enable_auto_reclamation": False,"enable_recurrent_scavenging": False,"enable_rr_last_queried": True,"enable_scavenging": True,"enable_zone_last_queried": True,"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "rtype","op1_type": "FIELD","op2": "A","op2_type": "STRING"},{"op": "ENDLIST"}],"reclaim_associated_records": False}}
            response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
            logging.info(response)
            read  = re.search(r'200',response)
            for read in response:
                assert True
            logging.info("Restart services")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            time.sleep(10)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            time.sleep(30)
            logging.info("Test Case 5 Execution Completed") 

        @pytest.mark.run(order=6)
        def test_006_run_scavenging_for_grid_A_records(self):
            logging.info("should  delete unknown record after runining scavenging")
            get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
            res = json.loads(get_ref)
            ref1 = json.loads(get_ref)[0]['_ref']
            logging.info (ref1)
            logging.info("run scavenging operation")
            data = {"action":"ANALYZE_RECLAIM"}
            response = ib_NIOS.wapi_request('POST', ref=ref1, fields=json.dumps(data), params="?_function=run_scavenging")
            logging.info(response)
            read  = re.search(r'200',response)
            for read in  response:
                assert True
            logging.info("Test Case 6 Execution Completed")
 
 
        @pytest.mark.run(order=7)
        def test_007_validate_the_scavenging_task(self):
            get_ref = ib_NIOS.wapi_request('GET',object_type="scavengingtask")
            logging.info("Fetching values for A Resource records")
            ref1 = json.loads(get_ref)
            get_ref = ib_NIOS.wapi_request('GET',object_type="record:a?_return_fields=name")
            logging.info(get_ref)
            res = json.loads(get_ref)
            print res
            for i in res:
                if(i['name'] in res):
                    assert False
                    print ("Zone is locked and hence scanvenging task cannot be run")
            logging.info("Test case 7 Execution Failed")        
                    
                    
        @pytest.mark.run(order=8)
        def test_008_modify_settings_to_unlock_zone(self):
            logging.info("Create grid_primary with required fields")
            get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth")
            logging.info(get_ref)
            res = json.loads(get_ref)
            ref1 = json.loads(get_ref)[0]['_ref']
            print ref1
            data ={"operation": "UNLOCK"}
            #response = ib_NIOS.wapi_request('POST', ref=ref1,fields=json.dumps(data))
            response = ib_NIOS.wapi_request('POST', object_type=ref1,params="?_function=lock_unlock_zone",fields=json.dumps(data))
            print response
            if type(response) == tuple:
               if response[0]==400 or response[0]==401:
                  logging.info("Failed to unlock")
                  assert False
                  print("Test Case 8 Execution Completed")
            sleep(90) 

        @pytest.mark.run(order=9)
        def test_009_run_scavenging_for_a_records(self):
            logging.info("should  delete unknown record after runining scavenging")
            get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
            res = json.loads(get_ref)
            ref1 = json.loads(get_ref)[0]['_ref']
            logging.info (ref1)
            logging.info("run scavenging operation")
            data = {"action":"ANALYZE_RECLAIM"}
            response = ib_NIOS.wapi_request('POST', ref=ref1, fields=json.dumps(data), params="?_function=run_scavenging")
            logging.info(response)
            read  = re.search(r'200',response)
            for read in  response:
                assert True
            sleep(30)
            logging.info("Test Case 09 Execution Completed")

 
        @pytest.mark.run(order=10)
        def test_010_validate_the_scavenging_task(self):
            get_ref = ib_NIOS.wapi_request('GET',object_type="scavengingtask")
            ref1 = json.loads(get_ref)[-1]['status']
            logging.info (ref1)
            if ref1 == "COMPLETED":
               assert True
            logging.info("Fetching values for Unknown Resource records")
            get_ref = ib_NIOS.wapi_request('GET',object_type="record:a?_return_fields=name")
            logging.info(get_ref)
            res = json.loads(get_ref)
            for i in res:
                if(i['name']=="arec1.source.com"):
                    assert False
                    print i
                    logging.info("Please check this record scavenging failed:",i)
                    logging.info("Test case 11 Execution Failed")
                else:
                    assert True
            logging.info("Test Case 10 Execution Completed")

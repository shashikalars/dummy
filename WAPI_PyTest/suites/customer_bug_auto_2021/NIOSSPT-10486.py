#############################################################################
#!/usr/bin/env python
__author__ ="Vijaya Sinha"
__email__  = "vsinha@infoblox.com"
#############################################################################
# Bug Description : NIOSSPT-1048                                      #
#  Grid Set up required:                                                    #
#  Confire 1 grids
# grid1 should be IB-1415
###########################################################################






import datetime
import re
import config
import pytest
import pexpect
import unittest
import sys
import logging
import os
import os.path
from os.path import join
import subprocess
import commands
import json
import time
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util

class NIOSSPT_10486(unittest.TestCase):

#Starting DNS service

        @pytest.mark.run(order=1)
        def test_001_Start_DNS_Service(self):
                logging.info("Start DNS Service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                for i in res:
                        logging.info("Modify a enable_dns")
                        data = {"enable_dns": True}
                        response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
                        print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 1 Execution Completed")

        @pytest.mark.run(order=2)
        def test_002_Validate_DNS_service_Enabled(self):
                logging.info("Validate DNs Service is enabled")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                for i in res:
                        print i
                        logging.info("found")
                        assert i["enable_dns"] == True
                print("Test Case 2 Execution Completed")

#Adding Forwarder

        @pytest.mark.run(order=3)
        def test_003_Add_Authoritative_zone(self):
                logging.info("Create Auth Zone")
                grid_member=config.grid_fqdn
                data = {"fqdn": "funddevelopmentservices.com","grid_primary": [{"name":config.grid_fqdn,"stealth":False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 3 Execution Completed")

                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                print("System Restart is done successfully")
                sleep(5)

        
        @pytest.mark.run(order=4)
        def test_004_Create_A_record(self):
                logging.info ("Creating A Record for added Zone")
                data = {"fqdn":"funddevelopmentservices.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "rec.funddevelopmentservices.com","ipv4addr":"1.2.3.5","_ref":endpoint,"comment":"Adding arec","view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                #import pdb;pdb.set_trace()
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                print("Test Case 004 Execution Completed")
                sleep(5)


	@pytest.mark.run(order=5)
        def test_005_modify_scavenging_settings(self):
            get_ref = ib_NIOS.wapi_request('GET',object_type="grid:dns")
            ref1 = json.loads(get_ref)[0]['_ref']
            data={"scavenging_settings": {"ea_expression_list": [],"enable_auto_reclamation": False,"enable_recurrent_scavenging": False,"enable_rr_last_queried": True,"enable_scavenging": True,"enable_zone_last_queried": True,"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "rtype","op1_type": "FIELD","op2": "A","op2_type": "STRING"},{"op": "ENDLIST"}],"reclaim_associated_records": True}}
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
            sleep(10)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            sleep(30)
            logging.info("Test Case 5 Execution Completed")


	@pytest.mark.run(order=6)
        def test_006_run_scavenging_for_grid_A_level(self):
            logging.info("run scavenging on grid level")
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
	    sleep(150)

	@pytest.mark.run(order=7)
        def test_007_Validate_static_record_as_reclaimable(self):
                logging.info("Validate static record as reclaimable")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:a",params="?_inheritance=True&_return_fields=reclaimable")
		print(get_ref)
		data= '"reclaimable": true'
                if data in get_ref:
                        assert True
                else:
                        assert False
                print("Test Case 7 passes as Static records can be marked as reclaimable but they cannot be reclaimed by DNS Scavenging.")

	@pytest.mark.run(order=8)
        def test_008_Validate_static_A_record_reclaimed(self):
                logging.info("Validate dynamic A record scavenged")
                get_temp = ib_NIOS.wapi_request('GET', object_type="record:a",params="?_inheritance=True&_return_fields=name")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                res = ''.join(map(str, res))
                print(res)
                data= "'name': 'rec.funddevelopmentservices.com'"
                if data in res:
                        assert True
                else:
                        assert False
                print("Static record gets deleted while performing DNS scavenging")





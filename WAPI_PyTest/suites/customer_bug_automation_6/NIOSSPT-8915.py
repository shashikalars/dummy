#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Vijaya Sinha"
__email__  = "vsinha@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Grid Master 1                                                         #
#  2. Licenses : DNS(enabled),Grid,RPZ,Threat Protection
#  3. Grid Master 2
#  4. Licenses : DNS(enabled),RPZ
#############################################################################

import re
import pdb
import config
import pytest
import unittest
import logging
import os
import commands
import os.path
from os.path import join
import subprocess
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as comm_util
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv


class Outbound(unittest.TestCase):

#Starting DNS service on 1st grid

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

#Enable	Threat Protection in grid 1			
    
    @pytest.mark.run(order=3)
    def test_003_Start_ThreatProtection_Service(self):
        logging.info("Start ThreatProtection Service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        for i in res:
            logging.info("Modify threat protection service")
            data = {"enable_service": True}
            response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data),grid_vip= config.grid_vip)
            print response

        logging.info(response)
        read  = re.search(r'200',response)
        for read in  response:
            assert True
        print("Test Case 3 Execution Completed")
        sleep(100)

    @pytest.mark.run(order=4)
    def test_004_Validate_ThreatProtection_Enabled(self):
        logging.info("Validate ThreatProtection is enabled")
        get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:threatprotection",params="?_return_fields=enable_service")
        logging.info(get_tacacsplus)
        res = json.loads(get_tacacsplus)
        print res
        for i in res:
            print i
            logging.info("found")
            assert i["enable_service"] == True
        print("Test Case 4 Execution Completed")
            
#Adding Forwarder in Grid 1

    @pytest.mark.run(order=5)
    def test_005_Update_Forwarders(self):
        logging.info("Update Forwarders")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        print ref1

        logging.info("Modify Grid DNS Properties")
        data = {"allow_recursive_query": True,"forwarders": [config.dns_forwarder],"logging_categories": {"log_queries": True,"log_responses": True,"log_rpz": True}}
        response = ib_NIOS.wapi_request('PUT',ref= ref1,fields=json.dumps(data))
        print response
        logging.info(response)
        read  = re.search(r'200',response)
        for read in  response:
                assert True
        print("Test Case 5 Execution Completed")
            
            
#Starting DNS service on Grid 2				

    @pytest.mark.run(order=6)
    def test_006_Start_DNS_Service(self):
        logging.info("Start DNS Service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns",grid_vip= config.grid2_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        print(res)
        for i in res:
            logging.info("Modify a enable_dns")
            data = {"enable_dns": True}
            response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data),grid_vip= config.grid2_vip)
            print response

        logging.info(response)
        read  = re.search(r'200',response)
        for read in  response:
                assert True
        print("Test Case 6 Execution Completed")

    @pytest.mark.run(order=7)
    def test_007_Validate_DNS_service_Enabled(self):
        logging.info("Validate DNs Service is enabled")
        get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns",grid_vip= config.grid2_vip)
        logging.info(get_tacacsplus)
        res = json.loads(get_tacacsplus)
        print res
        for i in res:
            print i
            logging.info("found")
            assert i["enable_dns"] == True
        print("Test Case 7 Execution Completed")
        
#Adding Forwarder in Grid 2

    @pytest.mark.run(order=8)
    def test_008_Update_Forwarders(self):
        logging.info("Update Forwarders")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns",grid_vip= config.grid2_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        print ref1

        logging.info("Modify Grid DNS Properties")
        data = {"allow_recursive_query": True,"forwarders": [config.dns_forwarder],"logging_categories": {"log_queries": True,"log_responses": True,"log_rpz": True},"allow_transfer":[{"_struct": "addressac","address": "Any","permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('PUT',ref= ref1,fields=json.dumps(data),grid_vip= config.grid2_vip)
        print response
        logging.info(response)
        read  = re.search(r'200',response)
        for read in  response:
            assert True
        print("Test Case 8 Execution Completed")

    @pytest.mark.run(order=9)
    def test_009_Validate_Forwarders(self):
        logging.info("Validate forwarders are added")
        get_forwarder = ib_NIOS.wapi_request('GET', object_type="grid:dns",params="?_return_fields=forwarders")
        logging.info(get_forwarder)
        res = json.loads(get_forwarder)
        print res
        for i in res:
            print i
            logging.info("found")
            assert i["forwarders"] == [config.dns_forwarder]
        print("Test Case 9 Execution Completed")

##Add secondary zone in Grid 

    @pytest.mark.run(order=10)
    def test_010_Add_Authoritative_zone_in_2nd_grid(self):
        logging.info("Add Authoritative zone in 2nd grid")
        data = {"fqdn" : "s1.com","grid_primary": [{"name": config.grid2_fqdn,"stealth": False}],"external_secondaries":[{"address": config.grid_vip ,"name": "yy.com","use_tsig_key_name": False,"stealth":False}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data),grid_vip= config.grid2_vip)
        print(response)
        res=json.loads(response)
        logging.info(response)
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        print("Test Case 010 Execution Completed")
        sleep(20)

        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid2_vip)
        print(grid)
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish),grid_vip=config.grid2_vip)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus",grid_vip=config.grid2_vip)
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",grid_vip=config.grid2_vip)
        print("System Restart is done successfully")
        sleep(10)

    @pytest.mark.run(order=11)
    def test_011_Validate_Authoritative_zone_in_2nd_grid(self):
        logging.info("Validate Authoritative_zone_in_2nd_grid")
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",params="?_return_fields=fqdn",grid_vip= config.grid2_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        print res
        flag = False
        for i in res:
            print i
            if i["fqdn"] == "s1.com":
                flag = True
        assert flag
        print("Test Case 11 Execution Completed")


    @pytest.mark.run(order=12)
    def test_012_Create_A_record(self):
        logging.info ("Creating A Record for added Zone")
        data={"name": "arec.s1.com","ipv4addr":"1.2.3.4","comment":"Adding arec","view":"default"}
        response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data),grid_vip= config.grid2_vip)
        print ("---------------------------------------------------",json.loads(response))
        read  = re.search(r'201',response)
        for read in response:
            assert True
        logging.info("A Record is created Successfully")
        sleep(20)

    @pytest.mark.run(order=13)
    def test_013_Validate_A_record(self):
        logging.info("Validate A record")
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:a",params="?_return_fields=name",grid_vip= config.grid2_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        print res
        flag = False
        for i in res:
            print i
            if i["name"] == "arec.s1.com":
                flag = True
        assert flag
        print("Test Case 13 Execution Completed")

    @pytest.mark.run(order=14)
    def test_014_Add_secondary_zone_in_1st_grid(self):
        logging.info("Add  secondary zone in 1st grid")
        data = {"fqdn" : "s1.com","external_primaries": [{"address": config.grid2_vip,"name": "ee.com","stealth": False,"use_tsig_key_name": False}],"use_external_primary" : True,"grid_secondaries":[{"enable_preferred_primaries": False,"grid_replicate": False,"lead": False,"name": config.grid_fqdn,"preferred_primaries": [],"stealth": False}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
        res=json.loads(response)
        logging.info(response)
        read  = re.search(r'201',response)
        for read in  response:
                assert True
        print("Test Case 14 Execution Completed")
        sleep(20)

        logging.info("Restart services")

        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        print("System Restart is done successfully")
        sleep(10)
        print("Test Case 14 Execution Completed")


    @pytest.mark.run(order=15)
    def test_015_Validate_DNS_Record_Gets_added_After_zone_transfer(self):
        logging.info("Validate DNS record is added after zone transfer")
        data = {"name": "arec.sec1.com"}
        get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="record:a",fields=json.dumps(data),grid_vip=config.grid2_vip)
        print(get_tacacsplus)
        res = json.loads(get_tacacsplus)
        print(res)
        print("Test Case 15 Execution Completed")

    @pytest.mark.run(order=16)
    def test_016_Add_RPZ_Feed_zone(self):
        logging.info("Create RPZ Feed Zone")
        grid_member=config.grid_fqdn
        data = {"fqdn":"base.rpz.infoblox.local","rpz_type": "FEED","external_primaries": [{"address": "10.34.1.130","name": "external.com","stealth": False}],"grid_secondaries": [{"enable_preferred_primaries": False,"grid_replicate": False,"lead": False,"name":config.grid_fqdn}],"rpz_type": "FEED","use_external_primary": True}
        response = ib_NIOS.wapi_request('POST', object_type="zone_rp", fields=json.dumps(data))
        res=json.loads(response)
        logging.info(response)
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        logging.info("Test Case 16 Execution Completed")

        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        logging.info("DNS service restarted")
        sleep(30)


    @pytest.mark.run(order=17)
    def test_017_validate_logs_after_sending_dig_query(self):
        logging.info("validating var logs after sending dig query")
        log("start","/var/log/syslog",config.grid2_vip)
        sleep(10)
        dig_cmd = 'dig @'+config.grid2_vip+' '+'s1.com'+str(' axfr')
        print(dig_cmd)
        dig_cmd1 = os.system(dig_cmd)
        sleep(30)
        log("stop","/var/log/syslog",config.grid2_vip)
        logs=logv("err CEF:0|Infoblox|NIOS Threat","/var/log/syslog",config.grid2_vip)
        print(logs)
	if re.search(r'err CEF:0|Infoblox|NIOS Threat',logs):
		assert False
	else:
		assert True
        print("Test Case 17 Execution Completed")


	logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid2_vip)
        print(grid)
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish),grid_vip=config.grid2_vip)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus",grid_vip=config.grid2_vip)
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",grid_vip=config.grid2_vip)
        print("System Restart is done successfully")
        sleep(10)
	logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
        print(grid)
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish),grid_vip=config.grid_vip)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus",grid_vip=config.grid_vip)
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",grid_vip=config.grid_vip)
        print("System Restart is done successfully")
        sleep(10)



    @pytest.mark.run(order=18)
    def test_018_cleanup(self):
        logging.info("Starting cleanup")
	#pdb.set_trace()
        zone=ib_NIOS.wapi_request('GET',object_type='zone_auth',params="?fqdn=s1.com",grid_vip= config.grid2_vip)
	print(zone)
        zone_ref=json.loads(zone)[0]['_ref']
        del_zone=ib_NIOS.wapi_request('DELETE',ref=zone_ref,grid_vip= config.grid2_vip)
	logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid2_vip)
        print(grid)
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish),grid_vip=config.grid2_vip)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus",grid_vip=config.grid2_vip)
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",grid_vip=config.grid2_vip)
        print("System Restart is done successfully")
        sleep(10)


    @pytest.mark.run(order=19)
    def test_019_cleanup1(self):
	#pdb.set_trace()
	zone1=ib_NIOS.wapi_request('GET',object_type='zone_auth',params="?fqdn=s1.com",grid_vip= config.grid_vip)
        print(zone1)
        zone1_ref=json.loads(zone1)[0]['_ref']
        del_zone1=ib_NIOS.wapi_request('DELETE',ref=zone1_ref)
	print(del_zone1)
        rpz_zone=ib_NIOS.wapi_request('GET',object_type="zone_rp",params="?fqdn=base.rpz.infoblox.local",grid_vip= config.grid_vip)
	print(rpz_zone)
        rpz_zone_ref=json.loads(rpz_zone)[0]['_ref']
        del_rpz_zone=ib_NIOS.wapi_request('DELETE',ref=rpz_zone_ref)

	logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
        print(grid)
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish),grid_vip=config.grid_vip)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus",grid_vip=config.grid_vip)
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",grid_vip=config.grid_vip)
        print("System Restart is done successfully")
        sleep(10)

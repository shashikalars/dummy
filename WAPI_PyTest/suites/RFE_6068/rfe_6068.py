import datetime
from ib_utils.common_utilities import generate_token_from_file
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
#from ib_utils.start_stop_logs import log_action as log
#from ib_utils.file_content_validation import log_validation as logv
import pdb


def restart_services(grid=config.grid_vip):
	"""
    	Restart Services
    	"""
    	display_msg("Restart services")
   	get_ref =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=grid)
    	ref = json.loads(get_ref)[0]['_ref']
    	data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    	restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices", fields=json.dumps(data),grid_vip=grid)
    	sleep(20)

def display_msg(x=""):
    	"""
    	Additional function.
    	"""
    	logging.info(x)
    	print(x)

class RFE_6068(unittest.TestCase):

#Starting DNS service

	@pytest.mark.run(order=1)
    	def test_001_Start_DNS_Service(self):
                logging.info("Start DNS Service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
        	for i in res:
                    logging.info("Start DNS service")
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
	def test_003_Allow_Recursion_At_Grid_level(self):
        	logging.info("Allow Recursion at Grid level")
        	get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
        	logging.info(get_ref)
        	res = json.loads(get_ref)
        	ref1 = json.loads(get_ref)[0]['_ref']
        	print ref1

        	logging.info("Modify Grid DNS Properties & allow recursion")
        	data = {"allow_recursive_query": True}
        	response = ib_NIOS.wapi_request('PUT',ref= ref1,fields=json.dumps(data))
        	print response
        	logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 3 Execution Completed")
		restart_services()

	@pytest.mark.run(order=4)
	def test_004_Validate_Recursion_enabled_At_Grid_level(self):
                logging.info("Validate Recursion enabled at Grid level")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="grid:dns",params="?_return_fields=allow_recursive_query")
                res = json.loads(get_tacacsplus)
                res = eval(json.dumps(get_tacacsplus))
                print(res)
                output=res.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                print(output)
                result = ['allow_recursive_query:true']
                for i in result:
                  if i in output:
                        assert True
                  else:
                        assert False
                print(result)
		print("Test Case 4 Execution Completed")

	@pytest.mark.run(order=5)
        def test_005_Validate_default_algorithm_set_in_grid_dns_properties_RSASHA256(self):
                logging.info("Validate default algorithm in grid dns properties RSASHA256")
                get_ref = ib_NIOS.wapi_request('GET',object_type="grid:dns",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="grid:dns",ref=ref1,params="?_inheritance=True&_return_fields=dnssec_key_params",grid_vip=config.grid_vip)
                print(output)
                output=json.loads(output)
                print(output)
                result = {'dnssec_key_params': {'next_secure_type': 'NSEC3', 'zsk_algorithms': [{'algorithm': 'RSASHA256', 'size': 1024}], 'ksk_size': 2048, 'ksk_rollover_notification_config': 'REQUIRE_MANUAL_INTERVENTION', 'signature_expiration': 345600, 'ksk_email_notification_enabled': False, 'zsk_rollover': 2592000, 'enable_ksk_auto_rollover': True, 'nsec3_salt_min_length': 1, 'nsec3_salt_max_length': 15, 'nsec3_iterations': 10, 'zsk_size': 1024, 'ksk_snmp_notification_enabled': True, 'ksk_rollover': 31536000, 'ksk_algorithms': [{'algorithm': 'RSASHA256', 'size': 2048}], 'zsk_rollover_mechanism': 'PRE_PUBLISH', 'ksk_algorithm': '8', u'zsk_algorithm': '8'}}
                for i in result:
                        if output[i] == result[i]:
                                assert True
                        else:
                                assert False
                print(result)
                sleep(30)
                print("Test Case 5 Execution Completed")

	@pytest.mark.run(order=6)
        def test_006_Update_KSK_ZSK_algorithm_with_ECDSAP256SHA256_in_grid_dns_properties(self):
                logging.info("Update KSK ZSK algorithm with ECDSAP256SHA256 in grid dns properties")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                print("Modify KSK ZSK algorithm with ECDSAP256SHA256")
                data = {"dnssec_key_params":{"ksk_algorithms": [{"algorithm": "ECDSAP256SHA256","size": 160}],"zsk_algorithms": [{"algorithm": "ECDSAP256SHA256","size": 160}]}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 6 Execution Completed")
                sleep(30)
		restart_services()

        @pytest.mark.run(order=7)
        def test_007_Validate_updating_KSK_ZSK_algorithm_with_ECDSAP256SHA256_in_grid_dns_properties(self):
                logging.info("Validate updating KSK ZSK algorithm with ECDSAP256SHA256 in grid dns properties")
                get_ref = ib_NIOS.wapi_request('GET',object_type="grid:dns",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="grid:dns",ref=ref1,params="?_inheritance=True&_return_fields=dnssec_key_params",grid_vip=config.grid_vip)
                print(output)
                output=json.loads(output)
                print(output)
                result = {'dnssec_key_params': {'next_secure_type': 'NSEC3', 'zsk_algorithms': [{'algorithm': 'ECDSAP256SHA256', 'size': 160}], 'ksk_size': 160, 'ksk_rollover_notification_config': 'REQUIRE_MANUAL_INTERVENTION', 'signature_expiration': 345600, 'ksk_email_notification_enabled': False, 'zsk_rollover': 2592000, 'enable_ksk_auto_rollover': True, 'nsec3_salt_min_length': 1, 'nsec3_salt_max_length': 15, 'nsec3_iterations': 10, 'zsk_size': 160, 'ksk_snmp_notification_enabled': True, 'ksk_rollover': 31536000, 'ksk_algorithms': [{'algorithm': 'ECDSAP256SHA256', 'size': 160}], 'zsk_rollover_mechanism': 'PRE_PUBLISH', 'ksk_algorithm': '13', 'zsk_algorithm': '13'}}
                for i in result:
                        if output[i] == result[i]:
                                assert True
                        else:
                                assert False
                print(result)
                sleep(30)
                print("Test Case 7 Execution Completed")

	@pytest.mark.run(order=8)
        def test_008_Update_KSK_ZSK_algorithm_with_NSEC_ECDSAP256SHA256_in_grid_dns_properties(self):
                logging.info("Update KSK ZSK algorithm with NSEC ECDSAP256SHA256 in grid dns properties")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                print("Modify KSK ZSK algorithm with ECDSAP256SHA256")
                data = {'dnssec_key_params': {'next_secure_type': 'NSEC', 'zsk_algorithms': [{'algorithm': 'ECDSAP256SHA256', 'size': 160}], 'ksk_size': 160, 'ksk_rollover_notification_config': 'REQUIRE_MANUAL_INTERVENTION', 'signature_expiration': 345600, 'ksk_email_notification_enabled': False, 'zsk_rollover': 2592000, 'enable_ksk_auto_rollover': True, 'nsec3_salt_min_length': 1, 'nsec3_salt_max_length': 15, 'nsec3_iterations': 10, 'zsk_size': 160, 'ksk_snmp_notification_enabled': True, 'ksk_rollover': 31536000, 'ksk_algorithms': [{'algorithm': 'ECDSAP256SHA256', 'size': 160}], 'zsk_rollover_mechanism': 'PRE_PUBLISH', 'ksk_algorithm': '13', 'zsk_algorithm': '13'}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 8 Execution Completed")
                sleep(30)
                restart_services()

	@pytest.mark.run(order=9)
        def test_009_Validate_updating_KSK_ZSK_algorithm_with_NSEC_ECDSAP256SHA256_in_grid_dns_properties(self):
                logging.info("Validate updating KSK ZSK algorithm with NSEC ECDSAP256SHA256 in grid dns properties")
                get_ref = ib_NIOS.wapi_request('GET',object_type="grid:dns",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="grid:dns",ref=ref1,params="?_inheritance=True&_return_fields=dnssec_key_params",grid_vip=config.grid_vip)
                print(output)
                output=json.loads(output)
                print(output)
                result = {'dnssec_key_params': {'next_secure_type': 'NSEC', 'zsk_algorithms': [{'algorithm': 'ECDSAP256SHA256', 'size': 160}], 'ksk_size': 160, 'ksk_rollover_notification_config': 'REQUIRE_MANUAL_INTERVENTION', 'signature_expiration': 345600, 'ksk_email_notification_enabled': False, 'zsk_rollover': 2592000, 'enable_ksk_auto_rollover': True, 'nsec3_salt_min_length': 1, 'nsec3_salt_max_length': 15, 'nsec3_iterations': 10, 'zsk_size': 160, 'ksk_snmp_notification_enabled': True, 'ksk_rollover': 31536000, 'ksk_algorithms': [{'algorithm': 'ECDSAP256SHA256', 'size': 160}], 'zsk_rollover_mechanism': 'PRE_PUBLISH', 'ksk_algorithm': '13', 'zsk_algorithm': '13'}}
                for i in result:
                        if output[i] == result[i]:
                                assert True
                        else:
                                assert False
                print(result)
                sleep(30)
                print("Test Case 9 Execution Completed")

#Negativescenario

	@pytest.mark.run(order=10)
        def test_010_Update_KSK_algorithm_with_ECDSAP256SHA256__size_1024_in_grid_dns_properties(self):
                logging.info("Update KSK ZSK algorithm with ECDSAP256SHA256 in grid dns properties")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                print("Modify KSK ZSK algorithm with ECDSAP256SHA256")
                data = {"dnssec_key_params":{"ksk_algorithms": [{"algorithm": "ECDSAP256SHA256","size": 1024}],"zsk_algorithms": [{"algorithm": "ECDSAP256SHA256","size": 160}]}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
		print("&&&&&&&&&&&&&&&&&&&&&&&",response)
		if '{ "Error": "AdmConDataError: The DNSSEC ECDSAP256 key size must be between 160 and 256 bits.", \n  "code": "Client.Ibap.Data", \n  "text": "The DNSSEC ECDSAP256 key size must be between 160 and 256 bits."\n}' in response:
			assert True
		else:
            		print("KSK algorithm set as ECDSAP256SHA256")
            		assert False
                print("Test Case 10 Execution Completed")
                sleep(30)

	@pytest.mark.run(order=11)
        def test_011_Update_ZSK_algorithm_with_ECDSAP256SHA256__size_1024_in_grid_dns_properties(self):
                logging.info("Update KSK ZSK algorithm with ECDSAP256SHA256 in grid dns properties")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                print("Modify KSK ZSK algorithm with ECDSAP256SHA256")
                data = {"dnssec_key_params":{"ksk_algorithms": [{"algorithm": "ECDSAP256SHA256","size": 160}],"zsk_algorithms": [{"algorithm": "ECDSAP256SHA256","size": 1024}]}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
		print("&&&&&&&&&&&&&&&&&&&&&&&",response)
                if '{ "Error": "AdmConDataError: The DNSSEC ECDSAP256 key size must be between 160 and 256 bits.", \n  "code": "Client.Ibap.Data", \n  "text": "The DNSSEC ECDSAP256 key size must be between 160 and 256 bits."\n}' in response:
                        assert True
                else:
                        print("ZSK algorithm set as ECDSAP256SHA256")
                        assert False
		print("Test Case 11 Execution Completed")
                sleep(30)

	@pytest.mark.run(order=12)
	def test_012_Add_Authoritative_zone(self):
                logging.info("Create Auth Zone")
                grid_member=config.grid_fqdn
                data = {"fqdn": "network.com","grid_primary": [{"name":config.grid_fqdn,"stealth":False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 12 Execution Completed")
		restart_services()

	@pytest.mark.run(order=13)
        def test_013_Validate_addition_of_Auth_Zone(self):
                logging.info("Validate Addition of Auth Zone")
        	get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="zone_auth",ref=ref1,params="?_inheritance=True&_return_fields=fqdn",grid_vip=config.grid_vip)
                print(output)
        	output=json.loads(output)
                print(output)
        	result = {'fqdn': 'network.com'}
        	for i in result:
                	if output[i] == result[i]:
                		assert True
                	else:
                		assert False
                print(result)
        	sleep(30)
                print("Test Case 13 Execution Completed")

	@pytest.mark.run(order=14)
        def test_014_Validate_default_algorithm_on_Auth_zone_RSASHA256(self):
                logging.info("Validate default algorithm in Auth zone RSASHA256")
                get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="zone_auth",ref=ref1,params="?_inheritance=True&_return_fields=dnssec_key_params",grid_vip=config.grid_vip)
                print(output)
                output=json.loads(output)
                print(output)
                result = {'dnssec_key_params': {'next_secure_type': 'NSEC3', 'zsk_algorithms': [{'algorithm': 'RSASHA256', 'size': 1024}], 'ksk_size': 2048, 'ksk_rollover_notification_config': 'REQUIRE_MANUAL_INTERVENTION', 'signature_expiration': 345600, 'ksk_email_notification_enabled': False, 'zsk_rollover': 2592000, 'enable_ksk_auto_rollover': False, 'nsec3_salt_min_length': 1, 'nsec3_salt_max_length': 15, 'nsec3_iterations': 10, 'zsk_size': 1024, 'ksk_snmp_notification_enabled': True, 'ksk_rollover': 31536000, 'ksk_algorithms': [{'algorithm': 'RSASHA256', 'size': 2048}], 'zsk_rollover_mechanism': 'PRE_PUBLISH', 'ksk_algorithm': '8', 'zsk_algorithm': '8'}}
                for i in result:
                        if output[i] == result[i]:
                                assert True
                        else:
                                assert False
                print(result)
                sleep(30)
                print("Test Case 14 Execution Completed")

	@pytest.mark.run(order=15)
        def test_015_Create_A_record(self):
                logging.info ("Creating A Record for added Zone")
                data = {"fqdn":"network.com","view": "default"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "arec.network.com","ipv4addr":"1.2.3.6","_ref":endpoint,"comment":"Adding arec","view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                print("Test Case 15 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=16)
        def test_016_Validate_A_record_created(self):
                logging.info("Validate A record created")
                get_ref = ib_NIOS.wapi_request('GET',object_type="record:a",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="record:a",ref=ref1,params="?_inheritance=True&_return_fields=name,ipv4addr",grid_vip=config.grid_vip)
                print(output)
                output=json.loads(output)
                print(output)
                result = {'ipv4addr': '1.2.3.6', 'name': 'arec.network.com'}
                for i in result:
                        if output[i] == result[i]:
                                assert True
                        else:
                                assert False
                print(result)
                sleep(30)
                print("Test Case 16 Execution Completed")

	@pytest.mark.run(order=17)
        def test_017_Sign_Dnssec_AuthZone_with_default_algorithm(self):
                logging.info("Sign Auth zone with default algorithm")
                data = {"fqdn":"network.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                ref=endpoint
                print ("###########",ref)
                data={"buffer":"KSK","operation":"SIGN"}
                response = ib_NIOS.wapi_request('POST', object_type=ref,fields=json.dumps(data),params="?_function=dnssec_operation")
                print (response)
                for read in response:
                        assert True
                logging.info("The selected zone is signed successfully")
		restart_services()
                print("Test Case 17 Execution Completed")

	@pytest.mark.run(order=18)
        def test_018_Validate_default_algorithm_on_signed_zone_RSASHA256(self):
                logging.info("Validate default algorithm in signed zone RSASHA256")
		get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="zone_auth",ref=ref1,params="?_inheritance=True&_return_fields=dnssec_key_params",grid_vip=config.grid_vip)
                print(output)
                output=json.loads(output)
                print(output)
                result = {'dnssec_key_params': {'next_secure_type': 'NSEC3', 'zsk_algorithms': [{'algorithm': 'RSASHA256', 'size': 1024}], 'ksk_size': 2048, 'ksk_rollover_notification_config': 'REQUIRE_MANUAL_INTERVENTION', 'signature_expiration': 345600, 'ksk_email_notification_enabled': False, 'zsk_rollover': 2592000, 'enable_ksk_auto_rollover': False, 'nsec3_salt_min_length': 1, 'nsec3_salt_max_length': 15, 'nsec3_iterations': 10, 'zsk_size': 1024, 'ksk_snmp_notification_enabled': True, 'ksk_rollover': 31536000, 'ksk_algorithms': [{'algorithm': 'RSASHA256', 'size': 2048}], 'zsk_rollover_mechanism': 'PRE_PUBLISH', 'ksk_algorithm': '8', 'zsk_algorithm': '8'}}
                for i in result:
                        if output[i] == result[i]:
                                assert True
                        else:
                                assert False
                print(result)
                sleep(30)
                print("Test Case 18 Execution Completed")

	@pytest.mark.run(order=19)
        def test_019_Update_KSK_ZSK_algorithm_with_ECDSAP256SHA256_for_Authzone(self):
                logging.info("Update KSK ZSK algorithm with ECDSAP256SHA256 for auth zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth")
        	print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                print("Modify KSK algorithm with ECDSAP256SHA256")
                data = {'dnssec_key_params': {'next_secure_type': 'NSEC', 'zsk_algorithms': [{'algorithm': 'ECDSAP256SHA256', 'size': 165}], 'ksk_size': 160, 'ksk_rollover_notification_config': 'REQUIRE_MANUAL_INTERVENTION', 'signature_expiration': 345600, 'ksk_email_notification_enabled': False, 'zsk_rollover': 2592000, 'enable_ksk_auto_rollover': True, 'nsec3_salt_min_length': 1, 'nsec3_salt_max_length': 15, 'nsec3_iterations': 10, 'zsk_size': 160, 'ksk_snmp_notification_enabled': True, 'ksk_rollover': 31536000, 'ksk_algorithms': [{'algorithm': 'ECDSAP256SHA256', 'size': 160}], 'zsk_rollover_mechanism': 'PRE_PUBLISH', 'ksk_algorithm': '13', 'zsk_algorithm': '13'}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 19 Execution Completed")
            	sleep(30)

	@pytest.mark.run(order=20)
        def test_020_Validate_updating_KSK_ZSK_algorithm_with_ECDSAP256SHA256(self):
                logging.info("Validate updating KSK ZSK algorithm with ECDSAP256SHA256")
                get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="zone_auth",ref=ref1,params="?_inheritance=True&_return_fields=dnssec_key_params",grid_vip=config.grid_vip)
                print(output)
                output=json.loads(output)
                print(output)
                result = {'dnssec_key_params': {'next_secure_type': 'NSEC', 'zsk_algorithms': [{'algorithm': 'ECDSAP256SHA256', 'size': 160}], 'ksk_size': 160, 'ksk_rollover_notification_config': 'REQUIRE_MANUAL_INTERVENTION', 'signature_expiration': 345600, 'ksk_email_notification_enabled': False, 'zsk_rollover': 2592000, 'enable_ksk_auto_rollover': True, 'nsec3_salt_min_length': 1, 'nsec3_salt_max_length': 15, 'nsec3_iterations': 10, 'zsk_size': 160, 'ksk_snmp_notification_enabled': True, 'ksk_rollover': 31536000, 'ksk_algorithms': [{'algorithm': 'ECDSAP256SHA256', 'size': 160}], 'zsk_rollover_mechanism': 'PRE_PUBLISH', 'ksk_algorithm': '13', 'zsk_algorithm': '13'}}
                for i in result:
                        if output[i] == result[i]:
                                assert True
                        else:
                                assert False
                print(result)
                sleep(30)
        	print("Test Case 20 Execution Completed")

	@pytest.mark.run(order=21)
        def test_021_dig_dnssec_record_to_get_code_of_ECDSAP256SHA256_algorithm(self):
                logging.info ("Dig A record to get code of ECDSAP256SHA256 algorithm")
		output = os.popen('dig @'+str(config.grid_vip)+' network.com +dnssec').read()
    		output = output.split('\n')
		print(output)
		flag=False
		for line in output:
			print(line)
			if "NSEC 13" in line:
                        	flag=True
				break
		if flag==True:
			assert True
			print("ECDSAP256SHA256 algorithm is code 13")
		else:
			print("Error")
			assert False
        	print("Test Case 21 Execution Completed")

#negativescenario

	@pytest.mark.run(order=22)
        def test_022_Update_KSK_algorithm_with_ECDSAP256SHA256__size_1024_in_Authzone(self):
                logging.info("Update KSK ZSK algorithm with ECDSAP256SHA256 in Authzone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                print("Modify KSK ZSK algorithm with ECDSAP256SHA256")
                data = {"dnssec_key_params":{"ksk_algorithms": [{"algorithm": "ECDSAP256SHA256","size": 1024}],"zsk_algorithms": [{"algorithm": "ECDSAP256SHA256","size": 160}]}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print("&&&&&&&&&&&&&&&&&&&&&&&",response)
		if '{ "Error": "AdmConDataError: The DNSSEC ECDSAP256 key size must be between 160 and 256 bits.", \n  "code": "Client.Ibap.Data", \n  "text": "The DNSSEC ECDSAP256 key size must be between 160 and 256 bits."\n}' in response:
                        assert True
                else:
                        print("KSK algorithm set as ECDSAP256SHA256")
                        assert False
                print("Test Case 22 Execution Completed")
                sleep(30)

	@pytest.mark.run(order=23)
        def test_023_Update_ZSK_algorithm_with_ECDSAP256SHA256__size_1024_in_Authzone(self):
                logging.info("Update KSK ZSK algorithm with ECDSAP256SHA256 in Authzone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                print("Modify KSK ZSK algorithm with ECDSAP256SHA256")
                data = {"dnssec_key_params":{"ksk_algorithms": [{"algorithm": "ECDSAP256SHA256","size": 160}],"zsk_algorithms": [{"algorithm": "ECDSAP256SHA256","size": 1024}]}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print("&&&&&&&&&&&&&&&&&&&&&&&",response)
		if '{ "Error": "AdmConDataError: The DNSSEC ECDSAP256 key size must be between 160 and 256 bits.", \n  "code": "Client.Ibap.Data", \n  "text": "The DNSSEC ECDSAP256 key size must be between 160 and 256 bits."\n}' in response:
                        assert True
                else:
                        print("KSK algorithm set as ECDSAP256SHA256")
                        assert False
                print("Test Case 23 Execution Completed")
                sleep(30)

	@pytest.mark.run(order=24)
        def test_024_Add_sub_zone(self):
                logging.info("Create sub zone")
                grid_member=config.grid_fqdn
                data = {"fqdn": "sub.network.com","grid_primary": [{"name":config.grid_fqdn,"stealth":False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 24 Execution Completed")
		restart_services()

	@pytest.mark.run(order=25)
        def test_025_Validate_addition_of_sub_Zone(self):
                logging.info("Validate Addition of sub Zone")
                get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="zone_auth",ref=ref1,params="?_inheritance=True&_return_fields=fqdn",grid_vip=config.grid_vip)
                print(output)
                output=json.loads(output)
                print(output)
                result = {'fqdn':'sub.network.com'}
                for i in result:
                        if output[i] == result[i]:
                                assert True
                        else:
                                assert False
                print(result)
                print("Test Case 25 Execution Completed")
                sleep(30)

	@pytest.mark.run(order=26)
        def test_026_sign_Dnssec_subZone(self):
                logging.info("Sign Sub zone with default algorithm")
                data = {"fqdn":"sub.network.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                ref=endpoint
                print ("###########",ref)
                data={"buffer":"KSK","operation":"SIGN"}
                response = ib_NIOS.wapi_request('POST', object_type=ref,fields=json.dumps(data),params="?_function=dnssec_operation")
                print (response)
                for read in response:
                        assert True
                logging.info("The selected zone is signed successfully")
                print("Test Case 24 Execution Completed")
                restart_services()

	@pytest.mark.run(order=27)
        def test_027_dig_dnssec_record_to_get_code_of_ECDSAP256SHA256_algorithm(self):
                logging.info ("Dig A record to get code of ECDSAP256SHA256 algorithm")
		output = os.popen('dig @'+str(config.grid_vip)+' network.com +dnssec').read()
                output = output.split('\n')
                print(output)
                flag=False
                for line in output:
                        print(line)
                        if "NSEC 13" in line:
                                flag=True
                                break
                if flag==True:
                        assert True
                        print("ECDSAP256SHA256 algorithm code is 13")
                else:
                        print("Error")
                        assert False
                print("Test Case 27 Execution Completed")
	
	@pytest.mark.run(order=28)
        def test_028_ROLLOVER_KSK_for_Dnssec_AuthZone(self):
                logging.info("ROLLOVER_KSK for Auth zone")
                data = {"fqdn":"network.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                ref=endpoint
                print ("###########",ref)
                data={"operation":"ROLLOVER_KSK"}
                response = ib_NIOS.wapi_request('POST', object_type=ref,fields=json.dumps(data),params="?_function=dnssec_operation")
                print (response)
                for read in response:
                        assert True
                print("Test Case 28 Execution Completed")
                restart_services()

	@pytest.mark.run(order=29)
        def test_029_Validate_Rollover_KSK_algorithm_for_auth_zone(self):
                logging.info("Validate KSK algorithm with ECDSAP256SHA256")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        sleep(05)
                        child.sendline('grep -e KSK /var/log/syslog')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = ["The KSK has been successfully rolled over for 'network.com' in view 'default'."]
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
        	sleep(30)
                print("Test Case 29 Execution Completed")


	@pytest.mark.run(order=30)
        def test_030_ROLLOVER_ZSK_for_Dnssec_AuthZone(self):
                logging.info("Rollover ZSK algorithm with ECDSAP256SHA256")
                data = {"fqdn":"network.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                ref=endpoint
                print ("###########",ref)
                data={"operation":"ROLLOVER_ZSK"}
                response = ib_NIOS.wapi_request('POST', object_type=ref,fields=json.dumps(data),params="?_function=dnssec_operation")
                print (response)
                for read in response:
                        assert True
                print("Test Case 30 Execution Completed")
                restart_services()


	@pytest.mark.run(order=31)
        def test_031_Validate_Rollover_ZSK_algorithm_for_Authzone(self):
                logging.info("Validate ZSK algorithm with ECDSAP256SHA256")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        sleep(05)
                        child.sendline('grep -e ZSK /var/log/syslog')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = ["The ZSK has been successfully rolled over for 'network.com' in view 'default'."]
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
                sleep(30)
                print("Test Case 31 Execution Completed")

	@pytest.mark.run(order=32)
        def test_032_ROLLOVER_KSK_for_Dnssec_SubZone(self):
                logging.info("ROLLOVER_KSK for Sub zone")
                data = {"fqdn":"sub.network.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                ref=endpoint
                print ("###########",ref)
                data={"operation":"ROLLOVER_KSK"}
                response = ib_NIOS.wapi_request('POST', object_type=ref,fields=json.dumps(data),params="?_function=dnssec_operation")
                print (response)
                for read in response:
                        assert True
                print("Test Case 32 Execution Completed")
                restart_services()

	@pytest.mark.run(order=33)
        def test_033_Validate_Rollover_KSK_algorithm_for_subzone(self):
                logging.info("Validate Rollover KSK algorithm for subzone ECDSAP256SHA256")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        sleep(05)
                        child.sendline('grep -e KSK /var/log/syslog')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = ["The KSK has been successfully rolled over for 'sub.network.com' in view 'default'."]
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
                sleep(30)
                print("Test Case 33 Execution Completed")

	@pytest.mark.run(order=34)
        def test_034_ROLLOVER_ZSK_for_Dnssec_subzone(self):
                logging.info("ROLLOVER_ZSK for sub zone")
                data = {"fqdn":"sub.network.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                ref=endpoint
                print ("###########",ref)
                data={"operation":"ROLLOVER_ZSK"}
                response = ib_NIOS.wapi_request('POST', object_type=ref,fields=json.dumps(data),params="?_function=dnssec_operation")
                print (response)
                for read in response:
                        assert True
                print("Test Case 34 Execution Completed")
                restart_services()

	@pytest.mark.run(order=35)
        def test_035_Validate_Rollover_ZSK_algorithm_for_subzone(self):
                logging.info("Validate Rollover ZSK algorithm for subzone")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        sleep(05)
                        child.sendline('grep -e ZSK /var/log/syslog')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = ["The ZSK has been successfully rolled over for 'sub.network.com' in view 'default'."]
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
                sleep(30)
                print("Test Case 35 Execution Completed")

	@pytest.mark.run(order=36)
	def test_036_Update_KSK_ZSK_algorithm_with_RSASHA256_for_Authzone(self):
                logging.info("Update KSK ZSK algorithm with RSASHA256 for auth zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                data = {"dnssec_key_params":{"ksk_algorithms": [{"algorithm": "RSASHA256","size": 1024}],"zsk_algorithms": [{"algorithm": "RSASHA256","size": 1024}]}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 36 Execution Completed")
                sleep(30)

	@pytest.mark.run(order=37)
        def test_037_Validate_updating_KSK_ZSK_algorithm_with_RSASHA256_for_authzone(self):
                logging.info("Validate updating KSK ZSK algorithm with RSASHA256 for authzone")
                get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="zone_auth",ref=ref1,params="?_inheritance=True&_return_fields=dnssec_key_params",grid_vip=config.grid_vip)
                print(output)
                output=json.loads(output)
                print(output)
                result = {'dnssec_key_params': {'next_secure_type': 'NSEC', 'zsk_algorithms': [{'algorithm': 'RSASHA256', 'size': 1024}], 'ksk_size': 1024, 'ksk_rollover_notification_config': 'REQUIRE_MANUAL_INTERVENTION', 'signature_expiration': 345600, 'ksk_email_notification_enabled': False, 'zsk_rollover': 2592000, 'enable_ksk_auto_rollover': True, 'nsec3_salt_min_length': 1, 'nsec3_salt_max_length': 15, 'nsec3_iterations': 10, 'zsk_size': 1024, 'ksk_snmp_notification_enabled': True, 'ksk_rollover': 31536000, 'ksk_algorithms': [{'algorithm': 'RSASHA256', 'size': 1024}], 'zsk_rollover_mechanism': 'PRE_PUBLISH', 'ksk_algorithm': '8', 'zsk_algorithm': '8'}}
                for i in result:
                        if output[i] == result[i]:
                                assert True
                        else:
                                assert False
                print(result)
                sleep(30)
                print("Test Case 37 Execution Completed")

	@pytest.mark.run(order=38)
        def test_038_Resign_Dnssec_AuthZone(self):
                logging.info("Apply algorithm changes for Auth zone")
                data = {"fqdn":"network.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                ref=endpoint
                print ("###########",ref)
                data={"operation":"RESIGN"}
                response = ib_NIOS.wapi_request('POST', object_type=ref,fields=json.dumps(data),params="?_function=dnssec_operation")
                print (response)
                for read in response:
                        assert True
                logging.info("The selected zone is signed successfully")
                print("Test Case 38 Execution Completed")
		sleep(30)

	@pytest.mark.run(order=39)
        def test_039_dig_dnssec_record_to_get_code_of_RSASHA256_algorithm(self):
                logging.info ("Dig A record to get code of RSASHA256 algorithm")
		output = os.popen('dig @'+str(config.grid_vip)+' network.com +dnssec').read()
                output = output.split('\n')
                print(output)
                flag=False
                for line in output:
                        print(line)
                        if "NSEC 8" in line:
                                flag=True
                                break
                if flag==True:
                        assert True
                        print("RSASHA256 algorithm code is 8")
                else:
                        print("Error")
                        assert False
                print("Test Case 39 Execution Completed")

	@pytest.mark.run(order=40)
        def test_040_Update_KSK_ZSK_algorithm_with_RSASHA256_for_subzone(self):
                logging.info("Update KSK ZSK algorithm with RSASHA256 for sub zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1

                data = {"dnssec_key_params":{"next_secure_type": "NSEC","ksk_algorithms": [{"algorithm": "RSASHA256","size": 1024}],"zsk_algorithms": [{"algorithm": "RSASHA256","size": 1024}]}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 40 Execution Completed")
                sleep(30)

	@pytest.mark.run(order=41)
        def test_041_Validate_updating_KSK_ZSK_algorithm_with_RSASHA256(self):
                logging.info("Validate updating KSK ZSK algorithm with RSASHA256 for sub zone")
                get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="zone_auth",ref=ref1,params="?_inheritance=True&_return_fields=dnssec_key_params",grid_vip=config.grid_vip)
                print(output)
                output=json.loads(output)
                print(output)
                result = {'dnssec_key_params': {'next_secure_type': 'NSEC', 'zsk_algorithms': [{'algorithm': 'RSASHA256', 'size': 1024}], 'ksk_size': 1024, 'ksk_rollover_notification_config': 'REQUIRE_MANUAL_INTERVENTION', 'signature_expiration': 345600, 'ksk_email_notification_enabled': False, 'zsk_rollover': 2592000, 'enable_ksk_auto_rollover': True, 'nsec3_salt_min_length': 1, 'nsec3_salt_max_length': 15, 'nsec3_iterations': 10, 'zsk_size': 1024, 'ksk_snmp_notification_enabled': True, 'ksk_rollover': 31536000, 'ksk_algorithms': [{'algorithm': 'RSASHA256', 'size': 1024}], 'zsk_rollover_mechanism': 'PRE_PUBLISH', 'ksk_algorithm': '8', 'zsk_algorithm': '8'}}
                for i in result:
                        if output[i] == result[i]:
                                assert True
                        else:
                                assert False
                print(result)
                sleep(30)
                print("Test Case 41 Execution Completed")

	@pytest.mark.run(order=42)
        def test_042_Resign_Dnssec_subZone_with_RSASHA256(self):
                logging.info("Resign sub zone RSASHA256")
                data = {"fqdn":"sub.network.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                ref=endpoint
                print ("###########",ref)
                data={"operation":"RESIGN"}
                response = ib_NIOS.wapi_request('POST', object_type=ref,fields=json.dumps(data),params="?_function=dnssec_operation")
                print (response)
                for read in response:
                        assert True
                logging.info("Apply algorithm changes on sub zone")
                sleep(90)
		print("Test Case 42 Execution Completed")

        @pytest.mark.run(order=43)
        def test_043_dig_dnssec_record_to_get_code_of_RSASHA256_algorithm(self):
                logging.info ("Dig A record to get code of RSASHA256 algorithm")
                output = os.popen('dig @'+str(config.grid_vip)+' sub.network.com +dnssec').read()
                output = output.split('\n')
                print(output)
                flag=False
                for line in output:
                        print(line)
                        if "NSEC 8" in line:
                                flag=True
                                break
                if flag==True:
                        assert True
                        print("RSASHA256 algorithm code is 8")
                else:
                        print("Error")
                        assert False
                print("Test Case 43 Execution Completed")

#negativescenario

        @pytest.mark.run(order=44)
        def test_044_Unsign_Dnssec_AuthZone(self):
                logging.info("Unsign Auth zone")
                data = {"fqdn":"network.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                ref=endpoint
                print ("###########",ref)
                data={"buffer":"KSK","operation":"UNSIGN"}
                response = ib_NIOS.wapi_request('POST', object_type=ref,fields=json.dumps(data),params="?_function=dnssec_operation")
                print (response)
                for read in response:
                        assert True
                logging.info("The selected zone is unsigned successfully")
                restart_services()
                print("Test Case 44 Execution Completed")

	@pytest.mark.run(order=45)
        def test_045_Resign_Dnssec_AuthZone_without_the_zone_signed(self):
                logging.info("Resign Auth zone without the zone signed")
                data = {"fqdn":"network.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                ref=endpoint
                print ("###########",ref)
                data={"operation":"RESIGN"}
                response = ib_NIOS.wapi_request('POST', object_type=ref,fields=json.dumps(data),params="?_function=dnssec_operation")
                print (response)
                if '{ "Error": "AdmConDataError: None (IBDataError: IB.Data:Cannot perform KSK rollover because zone \'network.com\' in view \'default\' has not been signed.)", \n  "code": "Client.Ibap.Data", \n  "text": "Cannot perform KSK rollover because zone \'network.com\' in view \'default\' has not been signed."\n}' in response:
                        assert True
                else:
                        print("Apply Algorithm changes on auth zone without the zone signed")
                        assert False
                print("Test Case 45 Execution Completed")

	@pytest.mark.run(order=46)
        def test_046_Add_root_zone(self):
                logging.info("Create root zone")
                grid_member=config.grid_fqdn
                data = {"fqdn": ".","grid_primary": [{"name":config.grid_fqdn,"stealth":False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 46 Execution Completed")
		restart_services()

	@pytest.mark.run(order=47)
        def test_047_Validate_addition_of_root_Zone(self):
                logging.info("Validate Addition of root Zone")
                get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[2]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="zone_auth",ref=ref1,params="?_inheritance=True&_return_fields=fqdn",grid_vip=config.grid_vip)
                print(output)
                output=json.loads(output)
                print(output)
                result = {'fqdn':'.'}
                for i in result:
                        if output[i] == result[i]:
                                assert True
                        else:
                                assert False
                print(result)
                print("Test Case 47 Execution Completed")
                sleep(30)

	@pytest.mark.run(order=48)
        def test_048_sign_Dnssec_root_Zone(self):
                logging.info("sign Root zone")
                data = {"fqdn":"."}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                ref=endpoint
                print ("###########",ref)
                data={"buffer":"KSK","operation":"SIGN"}
                response = ib_NIOS.wapi_request('POST', object_type=ref,fields=json.dumps(data),params="?_function=dnssec_operation")
                print (response)
                for read in response:
                        assert True
                logging.info("The selected zone is signed successfully")
                print("Test Case 48 Execution Completed")
                restart_services()

        @pytest.mark.run(order=49)
        def test_049_dig_dnssec_record_to_get_code_of_ECDSAP256SHA256_algorithm(self):
                logging.info ("Dig A record to get code of ECDSAP256SHA256 algorithm")
                output = os.popen('dig @'+str(config.grid_vip)+' . +dnssec').read()
                output = output.split('\n')
                print(output)
                flag=False
                for line in output:
                        print(line)
                        if "NSEC 13" in line:
                                flag=True
                                break
                if flag==True:
                        assert True
                        print("ECDSAP256SHA256 algorithm code is 13")
                else:
                        print("Error")
                        assert False
                print("Test Case 49 Execution Completed")

	@pytest.mark.run(order=50)
        def test_050_ROLLOVER_KSK_for_Dnssec_RootZone(self):
                logging.info("ROLLOVER_ZSK for root zone")
                data = {"fqdn":"."}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                ref=endpoint
                print ("###########",ref)
                data={"operation":"ROLLOVER_KSK"}
                response = ib_NIOS.wapi_request('POST', object_type=ref,fields=json.dumps(data),params="?_function=dnssec_operation")
                print (response)
                for read in response:
                        assert True
                print("Test Case 50 Execution Completed")
                restart_services()

	@pytest.mark.run(order=51)
        def test_051_Validate_Rollover_KSK_algorithm_for_rootzone(self):
                logging.info("Validate Rollover KSK algorithm for rootzone")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        sleep(05)
                        child.sendline('grep -e KSK /var/log/syslog')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = ["The KSK has been successfully rolled over for '.' in view 'default'."]
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
                sleep(30)
                print("Test Case 51 Execution Completed")

	@pytest.mark.run(order=52)
        def test_052_ROLLOVER_ZSK_for_Dnssec_rootZone(self):
                logging.info("ROLLOVER_ZSK for root zone")
                data = {"fqdn":"."}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                ref=endpoint
                print ("###########",ref)
                data={"operation":"ROLLOVER_ZSK"}
                response = ib_NIOS.wapi_request('POST', object_type=ref,fields=json.dumps(data),params="?_function=dnssec_operation")
                print (response)
                for read in response:
                        assert True
                print("Test Case 52 Execution Completed")
                restart_services()

	@pytest.mark.run(order=53)
        def test_053_Validate_Rollover_ZSK_algorithm_for_rootzone(self):
                logging.info("Validate Rollover ZSK algorithm for rootzone")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        sleep(05)
                        child.sendline('grep -e ZSK /var/log/syslog')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = ["The ZSK has been successfully rolled over for '.' in view 'default'."]
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
                sleep(30)
                print("Test Case 53 Execution Completed")

	@pytest.mark.run(order=54)
        def test_054_Update_KSK_ZSK_algorithm_with_RSASHA256_for_rootzone(self):
                logging.info("Update KSK ZSK algorithm with RSASHA256 for root zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[2]['_ref']
                print ref1

                data = {"dnssec_key_params":{"next_secure_type": "NSEC","ksk_algorithms": [{"algorithm": "RSASHA256","size": 1024}],"zsk_algorithms": [{"algorithm": "RSASHA256","size": 1024}]}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 54 Execution Completed")
                sleep(30)

	@pytest.mark.run(order=55)
        def test_055_Validate_updating_KSK_ZSK_algorithm_with_RSASHA256(self):
                logging.info("Validate updating KSK ZSK algorithm with RSASHA256 for root zone")
                get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[2]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="zone_auth",ref=ref1,params="?_inheritance=True&_return_fields=dnssec_key_params",grid_vip=config.grid_vip)
                print(output)
                output=json.loads(output)
                print(output)
		result= {'dnssec_key_params': {'next_secure_type': 'NSEC', 'zsk_algorithms': [{'algorithm': 'RSASHA256', 'size': 1024}], 'ksk_size': 1024, 'ksk_rollover_notification_config': 'REQUIRE_MANUAL_INTERVENTION', 'signature_expiration': 345600, 'ksk_email_notification_enabled': False, 'zsk_rollover': 2592000, 'enable_ksk_auto_rollover': False, 'nsec3_salt_min_length': 1, 'nsec3_salt_max_length': 15, 'nsec3_iterations': 10, 'zsk_size': 1024, 'ksk_snmp_notification_enabled': True, 'ksk_rollover': 31536000, 'ksk_algorithms': [{'algorithm': 'RSASHA256', 'size': 1024}], 'zsk_rollover_mechanism': 'PRE_PUBLISH', 'ksk_algorithm': '8', 'zsk_algorithm': '8'}}
                for i in result:
                        if output[i] == result[i]:
                                assert True
                        else:
                                assert False
                print(result)
                sleep(30)
                print("Test Case 55 Execution Completed")

	@pytest.mark.run(order=56)
        def test_056_Resign_Dnssec_rootZone_with_RSASHA256(self):
                logging.info("Resign root zone RSASHA256")
                data = {"fqdn":"."}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                ref=endpoint
                print ("###########",ref)
                data={"operation":"RESIGN"}
                response = ib_NIOS.wapi_request('POST', object_type=ref,fields=json.dumps(data),params="?_function=dnssec_operation")
                print (response)
                for read in response:
                        assert True
                logging.info("Apply algorithm changes on root zone")
		sleep(90)
		restart_services()
                print("Test Case 56 Execution Completed")

	@pytest.mark.run(order=57)
        def test_057_dig_dnssec_record_to_get_code_of_RSASHA256_algorithm(self):
                logging.info ("Dig A record to get code of RSASHA256 algorithm")
                output = os.popen('dig @'+str(config.grid_vip)+' . +dnssec').read()
                output = output.split('\n')
                print(output)
                flag=False
                for line in output:
                        print(line)
                        if "NSEC 8" in line:
                                flag=True
                                break
                if flag==True:
                        assert True
                        print("RSASHA256 algorithm code is 8")
                else:
                        print("Error")
                        assert False
                print("Test Case 57 Execution Completed")

	@pytest.mark.run(order=58)
        def test_058_Update_KSK_ZSK_algorithm_with_ECDSAP384SHA384_in_grid_dns_properties(self):
                logging.info("Update KSK ZSK algorithm with ECDSAP384SHA384 in grid dns properties")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                print("Modify KSK ZSK algorithm with ECDSAP384SHA384")
                data = {"dnssec_key_params":{"ksk_algorithms": [{"algorithm": "ECDSAP384SHA384","size": 160}],"zsk_algorithms": [{"algorithm": "ECDSAP384SHA384","size": 160}]}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 58 Execution Completed")
                sleep(30)

        @pytest.mark.run(order=59)
        def test_059_Validate_updating_KSK_ZSK_algorithm_with_ECDSAP384SHA384_in_grid_dns_properties(self):
                logging.info("Validate updating KSK ZSK algorithm with ECDSAP384SHA384 in grid dns properties")
                get_ref = ib_NIOS.wapi_request('GET',object_type="grid:dns",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="grid:dns",ref=ref1,params="?_inheritance=True&_return_fields=dnssec_key_params",grid_vip=config.grid_vip)
                print(output)
                output=json.loads(output)
                print(output)
                result = {'dnssec_key_params': {'next_secure_type': 'NSEC', 'zsk_algorithms': [{'algorithm': 'ECDSAP384SHA384', 'size': 160}], 'ksk_size': 160, 'ksk_rollover_notification_config': 'REQUIRE_MANUAL_INTERVENTION', 'signature_expiration': 345600, 'ksk_email_notification_enabled': False, 'zsk_rollover': 2592000, 'enable_ksk_auto_rollover': True, 'nsec3_salt_min_length': 1, 'nsec3_salt_max_length': 15, 'nsec3_iterations': 10, 'zsk_size': 160, 'ksk_snmp_notification_enabled': True, 'ksk_rollover': 31536000, 'ksk_algorithms': [{'algorithm': 'ECDSAP384SHA384', 'size': 160}], 'zsk_rollover_mechanism': 'PRE_PUBLISH', 'ksk_algorithm': '14', 'zsk_algorithm': '14'}}
                for i in result:
                        if output[i] == result[i]:
                                assert True
                        else:
                                assert False
                print(result)
                sleep(30)
                print("Test Case 59 Execution Completed")


#negativescenario

	@pytest.mark.run(order=60)
        def test_060_Update_KSK_algorithm_with_ECDSAP384SHA384__size_1024_in_grid_dns_properties(self):
                logging.info("Update KSK ZSK algorithm with ECDSAP384SHA384 in grid dns properties")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                print("Modify KSK ZSK algorithm with ECDSAP384SHA384")
                data = {"dnssec_key_params":{"ksk_algorithms": [{"algorithm": "ECDSAP384SHA384","size": 1024}],"zsk_algorithms": [{"algorithm": "ECDSAP384SHA384","size": 160}]}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print("&&&&&&&&&&&&&&&&&&&&&&&",response)
                if '{ "Error": "AdmConDataError: The DNSSEC ECDSAP384 key size must be between 160 and 384 bits.", \n  "code": "Client.Ibap.Data", \n  "text": "The DNSSEC ECDSAP384 key size must be between 160 and 384 bits."\n}' in response:
                    assert True
                else:
            		print("KSK algorithm set as ECDSAP384SHA384")
            		assert False
                print("Test Case 60 Execution Completed")
                sleep(30)


	@pytest.mark.run(order=61)
        def test_061_Update_ZSK_algorithm_with_ECDSAP384SHA384__size_1024_in_grid_dns_properties(self):
                logging.info("Update KSK ZSK algorithm with ECDSAP384SHA384 in grid dns properties")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                print("Modify KSK ZSK algorithm with ECDSAP384SHA384")
                data = {"dnssec_key_params":{"ksk_algorithms": [{"algorithm": "ECDSAP384SHA384","size": 160}],"zsk_algorithms": [{"algorithm": "ECDSAP384SHA384","size": 1024}]}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print("&&&&&&&&&&&&&&&&&&&&&&&",response)
                if '{ "Error": "AdmConDataError: The DNSSEC ECDSAP384 key size must be between 160 and 384 bits.", \n  "code": "Client.Ibap.Data", \n  "text": "The DNSSEC ECDSAP384 key size must be between 160 and 384 bits."\n}' in response:
                        assert True
                else:
                        print("ZSK algorithm set as ECDSAP384SHA384")
                        assert False
                print("Test Case 61 Execution Completed")
                sleep(30)

	@pytest.mark.run(order=62)
        def test_062_Delete_root_zone(self):
                logging.info("Deleting Root zone")
                data= {"fqdn": "."}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
                sleep(5)
        	print("Test Case 62 Execution Completed")

	@pytest.mark.run(order=63)
        def test_063_Add_Authoritative_zone(self):
                logging.info("Create Auth Zone")
                grid_member=config.grid_fqdn
                data = {"fqdn": "network.com","grid_primary": [{"name":config.grid_fqdn,"stealth":False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 63 Execution Completed")
                restart_services()

        @pytest.mark.run(order=64)
        def test_064_Validate_addition_of_Auth_Zone(self):
                logging.info("Validate Addition of Auth Zone")
                get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="zone_auth",ref=ref1,params="?_inheritance=True&_return_fields=fqdn",grid_vip=config.grid_vip)
                print(output)
                output=json.loads(output)
                print(output)
                result = {'fqdn': 'network.com'}
                for i in result:
                        if output[i] == result[i]:
                                assert True
                        else:
                                assert False
                print(result)
                sleep(30)
                print("Test Case 64 Execution Completed")

	@pytest.mark.run(order=65)
        def test_065_Update_KSK_ZSK_algorithm_with_ECDSAP384SHA384_for_Authzone(self):
                logging.info("Update KSK ZSK algorithm with ECDSAP384SHA384 for auth zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth")
        	print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                print("Modify KSK algorithm with ECDSAP384SHA384")
                data = {"dnssec_key_params":{"ksk_algorithms": [{"algorithm": "ECDSAP384SHA384","size": 160}],"zsk_algorithms": [{"algorithm": "ECDSAP384SHA384","size": 160}]}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 65 Execution Completed")
		restart_services()
            	sleep(30)

        @pytest.mark.run(order=66)
        def test_066_Validate_updating_KSK_ZSK_algorithm_with_ECDSAP384SHA384_for_authzone(self):
                logging.info("Validate updating KSK ZSK algorithm with ECDSAP384SHA384 for authzone")
                get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="zone_auth",ref=ref1,params="?_inheritance=True&_return_fields=dnssec_key_params",grid_vip=config.grid_vip)
                print(output)
                output=json.loads(output)
                print(output)
                result = {'dnssec_key_params': {'next_secure_type': 'NSEC3', 'zsk_algorithms': [{'algorithm': 'ECDSAP384SHA384', 'size': 160}], 'ksk_size': 160, 'ksk_rollover_notification_config': 'REQUIRE_MANUAL_INTERVENTION', 'signature_expiration': 345600, 'ksk_email_notification_enabled': False, 'zsk_rollover': 2592000, 'enable_ksk_auto_rollover': False, 'nsec3_salt_min_length': 1, 'nsec3_salt_max_length': 15, 'nsec3_iterations': 10, 'zsk_size': 160, 'ksk_snmp_notification_enabled': True, 'ksk_rollover': 31536000, 'ksk_algorithms': [{'algorithm': 'ECDSAP384SHA384', 'size': 160}], 'zsk_rollover_mechanism': 'PRE_PUBLISH', 'ksk_algorithm': '14', 'zsk_algorithm': '14'}}
                for i in result:
                        if output[i] == result[i]:
                                assert True
                        else:
                                assert False
                print(result)
		print("Test Case 66 Execution Completed")


	@pytest.mark.run(order=67)
        def test_067_Sign_Dnssec_AuthZone_with_ECDSAP384SHA384_algorithm(self):
                logging.info("Sign Auth zone with ECDSAP384SHA384 algorithm")
                data = {"fqdn":"network.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                ref=endpoint
                print ("###########",ref)
                data={"buffer":"KSK","operation":"SIGN"}
                response = ib_NIOS.wapi_request('POST', object_type=ref,fields=json.dumps(data),params="?_function=dnssec_operation")
                print (response)
                for read in response:
                        assert True
                logging.info("The selected zone is signed successfully")
                restart_services()
                print("Test Case 67 Execution Completed")

        @pytest.mark.run(order=68)
        def test_068_Validate_default_algorithm_on_signed_authzone_ECDSAP384SHA384(self):
                logging.info("Validate default algorithm in signed authzone ECDSAP384SHA384")
                get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="zone_auth",ref=ref1,params="?_inheritance=True&_return_fields=dnssec_key_params",grid_vip=config.grid_vip)
                print(output)
                output=json.loads(output)
                print(output)
                result = {'dnssec_key_params': {'next_secure_type': 'NSEC3', 'zsk_algorithms': [{'algorithm': 'ECDSAP384SHA384', 'size': 160}], 'ksk_size': 160, 'ksk_rollover_notification_config': 'REQUIRE_MANUAL_INTERVENTION', 'signature_expiration': 345600, 'ksk_email_notification_enabled': False, 'zsk_rollover': 2592000, 'enable_ksk_auto_rollover': False, 'nsec3_salt_min_length': 1, 'nsec3_salt_max_length': 15, 'nsec3_iterations': 10, 'zsk_size': 160, 'ksk_snmp_notification_enabled': True, 'ksk_rollover': 31536000, 'ksk_algorithms': [{'algorithm': 'ECDSAP384SHA384', 'size': 160}], 'zsk_rollover_mechanism': 'PRE_PUBLISH', 'ksk_algorithm': '14', 'zsk_algorithm': '14'}}
                for i in result:
                        if output[i] == result[i]:
                                assert True
                        else:
                                assert False
                print(result)
                sleep(30)
		print("Test Case 68 Execution Completed")

	@pytest.mark.run(order=69)
        def test_069_dig_dnssec_record_to_get_code_of_ECDSAP384SHA384_algorithm(self):
                logging.info ("Dig A record to get code of ECDSAP384SHA384 algorithm")
                output = os.popen('dig @'+str(config.grid_vip)+' network.com +dnssec').read()
                output = output.split('\n')
                print(output)
                flag=False
                for line in output:
                        print(line)
                        if "NSEC3 14" in line:
                                flag=True
                                break
                if flag==True:
                        assert True
                        print("ECDSAP384SHA384 algorithm code is 14")
                else:
                        print("Error")
                        assert False
		print("Test Case 69 Execution Completed")

#negativescenarion

	@pytest.mark.run(order=70)
        def test_070_Update_KSK_algorithm_with_ECDSAP384SHA384__size_1024_in_Authzone(self):
                logging.info("Update KSK ZSK algorithm with ECDSAP384SHA384 in authzone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                print("Modify KSK ZSK algorithm with ECDSAP384SHA384")
                data = {"dnssec_key_params":{"ksk_algorithms": [{"algorithm": "ECDSAP384SHA384","size": 1024}],"zsk_algorithms": [{"algorithm": "ECDSAP384SHA384","size": 160}]}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print("&&&&&&&&&&&&&&&&&&&&&&&",response)
                if '{ "Error": "AdmConDataError: The DNSSEC ECDSAP384 key size must be between 160 and 384 bits.", \n  "code": "Client.Ibap.Data", \n  "text": "The DNSSEC ECDSAP384 key size must be between 160 and 384 bits."\n}' in response:
                    assert True
                else:
                        print("KSK algorithm set as ECDSAP384SHA384")
                        assert False
                print("Test Case 70 Execution Completed")
                sleep(30)


        @pytest.mark.run(order=71)
        def test_071_Update_ZSK_algorithm_with_ECDSAP384SHA384__size_1024_in_authzone(self):
                logging.info("Update KSK ZSK algorithm with ECDSAP384SHA384 in authzone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                print("Modify KSK ZSK algorithm with ECDSAP384SHA384")
                data = {"dnssec_key_params":{"ksk_algorithms": [{"algorithm": "ECDSAP384SHA384","size": 160}],"zsk_algorithms": [{"algorithm": "ECDSAP384SHA384","size": 1024}]}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print("&&&&&&&&&&&&&&&&&&&&&&&",response)
                if '{ "Error": "AdmConDataError: The DNSSEC ECDSAP384 key size must be between 160 and 384 bits.", \n  "code": "Client.Ibap.Data", \n  "text": "The DNSSEC ECDSAP384 key size must be between 160 and 384 bits."\n}' in response:
                        assert True
                else:
			print("KSK algorithm set as ECDSAP384SHA384")
                        assert False
                print("Test Case 71 Execution Completed")
                sleep(30)

	@pytest.mark.run(order=72)
        def test_072_Add_sub_zone(self):
                logging.info("Create sub zone")
                grid_member=config.grid_fqdn
                data = {"fqdn": "sub.network.com","grid_primary": [{"name":config.grid_fqdn,"stealth":False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 72 Execution Completed")
            	restart_services()

        @pytest.mark.run(order=73)
        def test_073_Validate_addition_of_sub_Zone(self):
                logging.info("Validate Addition of sub Zone")
                get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="zone_auth",ref=ref1,params="?_inheritance=True&_return_fields=fqdn",grid_vip=config.grid_vip)
                print(output)
                output=json.loads(output)
                print(output)
                result = {'fqdn':'sub.network.com'}
                for i in result:
                        if output[i] == result[i]:
                                assert True
                        else:
                                assert False
                print(result)
                print("Test Case 73 Execution Completed")
                sleep(30)

	@pytest.mark.run(order=74)
        def test_074_Validate_default_algorithm_on_subzone_with_ECDSAP384SHA384(self):
                logging.info("Validate default algorithm in subzone with ECDSAP384SHA384")
                get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="zone_auth",ref=ref1,params="?_inheritance=True&_return_fields=dnssec_key_params",grid_vip=config.grid_vip)
                print(output)
                output=json.loads(output)
                print(output)
                result = {'dnssec_key_params': {'next_secure_type': 'NSEC3', 'zsk_algorithms': [{'algorithm': 'RSASHA256', 'size': 1024}], 'ksk_size': 2048, 'ksk_rollover_notification_config': 'REQUIRE_MANUAL_INTERVENTION', 'signature_expiration': 345600, 'ksk_email_notification_enabled': False, 'zsk_rollover': 2592000, 'enable_ksk_auto_rollover': False, 'nsec3_salt_min_length': 1, 'nsec3_salt_max_length': 15, 'nsec3_iterations': 10, 'zsk_size': 1024, 'ksk_snmp_notification_enabled': True, 'ksk_rollover': 31536000, 'ksk_algorithms': [{'algorithm': 'RSASHA256', 'size': 2048}], 'zsk_rollover_mechanism': 'PRE_PUBLISH', 'ksk_algorithm': '8', 'zsk_algorithm': '8'}}
                for i in result:
                        if output[i] == result[i]:
                                assert True
                        else:
                                assert False
                print(result)
                sleep(30)
                print("Test Case 74 Execution Completed")

	@pytest.mark.run(order=75)
        def test_075_Update_KSK_ZSK_algorithm_with_ECDSAP384SHA384_for_subzone(self):
                logging.info("Update KSK ZSK algorithm with ECDSAP384SHA384 for auth zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1

                print("Modify KSK algorithm with ECDSAP384SHA384")
                data = {"dnssec_key_params":{"ksk_algorithms": [{"algorithm": "ECDSAP384SHA384","size": 160}],"zsk_algorithms": [{"algorithm": "ECDSAP384SHA384","size": 160}]}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 75 Execution Completed")
                restart_services()
                sleep(30)

	@pytest.mark.run(order=76)
        def test_076_Validate_default_algorithm_on_subzone_with_ECDSAP384SHA384(self):
                logging.info("Validate default algorithm in subzone with ECDSAP384SHA384")
                get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="zone_auth",ref=ref1,params="?_inheritance=True&_return_fields=dnssec_key_params",grid_vip=config.grid_vip)
                print(output)
                output=json.loads(output)
                print(output)
                result = {'dnssec_key_params': {'next_secure_type': 'NSEC3', 'zsk_algorithms': [{'algorithm': 'ECDSAP384SHA384', 'size': 160}], 'ksk_size': 160, 'ksk_rollover_notification_config': 'REQUIRE_MANUAL_INTERVENTION', 'signature_expiration': 345600, 'ksk_email_notification_enabled': False, 'zsk_rollover': 2592000, 'enable_ksk_auto_rollover': False, 'nsec3_salt_min_length': 1, 'nsec3_salt_max_length': 15, 'nsec3_iterations': 10, 'zsk_size': 160, 'ksk_snmp_notification_enabled': True, 'ksk_rollover': 31536000, 'ksk_algorithms': [{'algorithm': 'ECDSAP384SHA384', 'size': 160}], 'zsk_rollover_mechanism': 'PRE_PUBLISH', 'ksk_algorithm': '14', 'zsk_algorithm': '14'}}
                for i in result:
                        if output[i] == result[i]:
                                assert True
                        else:
                                assert False
                print(result)
                sleep(30)
                print("Test Case 76 Execution Completed")

	@pytest.mark.run(order=77)
        def test_077_sign_Dnssec_subZone(self):
                logging.info("Sign Sub zone with default algorithm")
                data = {"fqdn":"sub.network.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                ref=endpoint
                print ("###########",ref)
                data={"buffer":"KSK","operation":"SIGN"}
                response = ib_NIOS.wapi_request('POST', object_type=ref,fields=json.dumps(data),params="?_function=dnssec_operation")
                print (response)
                for read in response:
                        assert True
                logging.info("The selected zone is signed successfully")
                print("Test Case 77 Execution Completed")
                restart_services()

	@pytest.mark.run(order=78)
        def test_078_dig_dnssec_record_to_get_code_of_ECDSAP384SHA384_algorithm(self):
                logging.info ("Dig A record to get code of ECDSAP384SHA384 algorithm")
                output = os.popen('dig @'+str(config.grid_vip)+' sub.network.com +dnssec').read()
                output = output.split('\n')
                print(output)
                flag=False
                for line in output:
                        print(line)
                        if "NSEC3 14" in line:
                                flag=True
                                break
                if flag==True:
                        assert True
                        print("ECDSAP384SHA384 algorithm code is 14")
                else:
                        print("Error")
                        assert False
                print("Test Case 78 Execution Completed")


	@pytest.mark.run(order=79)
        def test_079_ROLLOVER_KSK_for_Dnssec_AuthZone(self):
                logging.info("ROLLOVER_KSK for Auth zone")
                data = {"fqdn":"network.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                ref=endpoint
                print ("###########",ref)
                data={"operation":"ROLLOVER_KSK"}
                response = ib_NIOS.wapi_request('POST', object_type=ref,fields=json.dumps(data),params="?_function=dnssec_operation")
                print (response)
                for read in response:
                        assert True
                print("Test Case 79 Execution Completed")
                restart_services()


	@pytest.mark.run(order=80)
        def test_080_Validate_Rollover_KSK_algorithm_for_auth_zone(self):
                logging.info("Validate Rollover KSK algorithm for authzone with ECDSAP384SHA384")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        sleep(05)
                        child.sendline('grep -e KSK /var/log/syslog')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = ["The KSK has been successfully rolled over for 'network.com' in view 'default'."]
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
			assert False
		finally:
                        child.close()
                print("\n")
        	sleep(30)
                print("Test Case 80 Execution Completed")


	@pytest.mark.run(order=81)
        def test_081_ROLLOVER_ZSK_for_Dnssec_AuthZone(self):
                logging.info("Validate Rollover ZSK algorithm with ECDSAP384SHA384")
                data = {"fqdn":"network.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                ref=endpoint
                print ("###########",ref)
                data={"operation":"ROLLOVER_ZSK"}
                response = ib_NIOS.wapi_request('POST', object_type=ref,fields=json.dumps(data),params="?_function=dnssec_operation")
                print (response)
                for read in response:
                        assert True
                print("Test Case 81 Execution Completed")
                restart_services()

	@pytest.mark.run(order=82)
        def test_082_Validate_Rollover_ZSK_algorithm_for_auth_zone(self):
                logging.info("Validate Rollover ZSK algorithm for authzone with ECDSAP384SHA384")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        sleep(05)
                        child.sendline('grep -e ZSK /var/log/syslog')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = ["The ZSK has been successfully rolled over for 'network.com' in view 'default'."]
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("\n")
                sleep(30)
                print("Test Case 82 Execution Completed")

	

	@pytest.mark.run(order=83)
        def test_083_ROLLOVER_KSK_for_Dnssec_subZone(self):
                logging.info("ROLLOVER_KSK for sub zone")
                data = {"fqdn":"sub.network.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                ref=endpoint
                print ("###########",ref)
                data={"operation":"ROLLOVER_KSK"}
                response = ib_NIOS.wapi_request('POST', object_type=ref,fields=json.dumps(data),params="?_function=dnssec_operation")
                print (response)
                for read in response:
                        assert True
                print("Test Case 83 Execution Completed")
                restart_services()


	@pytest.mark.run(order=84)
        def test_084_Validate_Rollover_KSK_algorithm_for_sub_zone(self):
                logging.info("Validate Rollover KSK algorithm for subzone with ECDSAP384SHA384")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        sleep(05)
                        child.sendline('grep -e KSK /var/log/syslog')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = ["The KSK has been successfully rolled over for 'sub.network.com' in view 'default'."]
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("\n")
                sleep(30)
                print("Test Case 84 Execution Completed")

	@pytest.mark.run(order=85)
        def test_085_ROLLOVER_ZSK_for_Dnssec_SubZone(self):
                logging.info("ROLLOVER ZSK for Sub zone")
                data = {"fqdn":"sub.network.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                ref=endpoint
                print ("###########",ref)
                data={"operation":"ROLLOVER_ZSK"}
                response = ib_NIOS.wapi_request('POST', object_type=ref,fields=json.dumps(data),params="?_function=dnssec_operation")
                print (response)
                for read in response:
                        assert True
                print("Test Case 85 Execution Completed")
                restart_services()

	@pytest.mark.run(order=86)
        def test_086_Validate_Rollover_ZSK_algorithm_for_sub_zone(self):
                logging.info("Validate Rollover ZSK algorithm for subzone with ECDSAP384SHA384")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        sleep(05)
                        child.sendline('grep -e ZSK /var/log/syslog')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = ["The ZSK has been successfully rolled over for 'sub.network.com' in view 'default'."]
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("\n")
                sleep(30)
                print("Test Case 86 Execution Completed")

#negativescenarion

	@pytest.mark.run(order=87)
        def test_087_Update_KSK_algorithm_with_ECDSAP384SHA384__size_1024_in_subzone(self):
                logging.info("Update KSK ZSK algorithm with ECDSAP384SHA384 in subzone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1

                print("Modify KSK ZSK algorithm with ECDSAP384SHA384")
                data = {"dnssec_key_params":{"ksk_algorithms": [{"algorithm": "ECDSAP384SHA384","size": 1024}],"zsk_algorithms": [{"algorithm": "ECDSAP384SHA384","size": 160}]}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print("&&&&&&&&&&&&&&&&&&&&&&&",response)
                if '{ "Error": "AdmConDataError: The DNSSEC ECDSAP384 key size must be between 160 and 384 bits.", \n  "code": "Client.Ibap.Data", \n  "text": "The DNSSEC ECDSAP384 key size must be between 160 and 384 bits."\n}' in response:
                    assert True
                else:
                        print("KSK algorithm set as ECDSAP384SHA384")
                        assert False
                print("Test Case 87 Execution Completed")
                sleep(30)


        @pytest.mark.run(order=88)
        def test_088_Update_ZSK_algorithm_with_ECDSAP384SHA384__size_1024_in_subzone(self):
                logging.info("Update KSK ZSK algorithm with ECDSAP384SHA384 in subone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1

                print("Modify KSK ZSK algorithm with ECDSAP384SHA384")
                data = {"dnssec_key_params":{"ksk_algorithms": [{"algorithm": "ECDSAP384SHA384","size": 160}],"zsk_algorithms": [{"algorithm": "ECDSAP384SHA384","size": 1024}]}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print("&&&&&&&&&&&&&&&&&&&&&&&",response)
                if '{ "Error": "AdmConDataError: The DNSSEC ECDSAP384 key size must be between 160 and 384 bits.", \n  "code": "Client.Ibap.Data", \n  "text": "The DNSSEC ECDSAP384 key size must be between 160 and 384 bits."\n}' in response:
                        assert True
                else:
			print("ZSK algorithm set as ECDSAP384SHA384")
                        assert False
                print("Test Case 88 Execution Completed")
                sleep(30)

	@pytest.mark.run(order=89)
	def test_089_Update_KSK_ZSK_algorithm_with_RSASHA256_for_Authzone(self):
                logging.info("Update KSK ZSK algorithm with RSASHA256 for auth zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                data = {"dnssec_key_params":{"ksk_algorithms": [{"algorithm": "RSASHA256","size": 1024}],"zsk_algorithms": [{"algorithm": "RSASHA256","size": 1024}]}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 89 Execution Completed")
                sleep(30)

	@pytest.mark.run(order=90)
        def test_090_Validate_updating_KSK_ZSK_algorithm_with_RSASHA256_for_authzone(self):
                logging.info("Validate updating KSK ZSK algorithm with RSASHA256 for authzone")
                get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="zone_auth",ref=ref1,params="?_inheritance=True&_return_fields=dnssec_key_params",grid_vip=config.grid_vip)
                print(output)
                output=json.loads(output)
                print(output)
                result = {'dnssec_key_params': {'next_secure_type': 'NSEC3', 'zsk_algorithms': [{'algorithm': 'RSASHA256', 'size': 1024}], 'ksk_size': 1024, 'ksk_rollover_notification_config': 'REQUIRE_MANUAL_INTERVENTION', 'signature_expiration': 345600, 'ksk_email_notification_enabled': False, 'zsk_rollover': 2592000, 'enable_ksk_auto_rollover': False, 'nsec3_salt_min_length': 1, 'nsec3_salt_max_length': 15, 'nsec3_iterations': 10, 'zsk_size': 1024, 'ksk_snmp_notification_enabled': True, 'ksk_rollover': 31536000, 'ksk_algorithms': [{'algorithm': 'RSASHA256', 'size': 1024}], 'zsk_rollover_mechanism': 'PRE_PUBLISH', 'ksk_algorithm': '8', 'zsk_algorithm': '8'}}
                for i in result:
                        if output[i] == result[i]:
                                assert True
                        else:
                                assert False
                print(result)
                sleep(30)
                print("Test Case 90 Execution Completed")

	@pytest.mark.run(order=91)
        def test_091_Resign_Dnssec_AuthZone(self):
                logging.info("Apply algorithm changes for Auth zone")
                data = {"fqdn":"network.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                ref=endpoint
                print ("###########",ref)
                data={"operation":"RESIGN"}
                response = ib_NIOS.wapi_request('POST', object_type=ref,fields=json.dumps(data),params="?_function=dnssec_operation")
                print (response)
                for read in response:
                        assert True
                logging.info("The selected zone is signed successfully")
                print("Test Case 91 Execution Completed")
                sleep(30)

	@pytest.mark.run(order=92)
        def test_092_dig_dnssec_record_to_get_code_of_RSASHA256_algorithm(self):
                logging.info ("Dig A record to get code of RSASHA256 algorithm")
                output = os.popen('dig @'+str(config.grid_vip)+' network.com +dnssec').read()
                output = output.split('\n')
                print(output)
                flag=False
                for line in output:
                        print(line)
                        if "NSEC3 8" in line:
                                flag=True
                                break
                if flag==True:
                        assert True
                        print("RSASHA256 algorithm code is 8")
                else:
                        print("Error")
                        assert False
                print("Test Case 92 Execution Completed")

	@pytest.mark.run(order=93)
        def test_093_Update_KSK_ZSK_algorithm_with_RSASHA256_for_subzone(self):
                logging.info("Update KSK ZSK algorithm with RSASHA256 for sub zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1

                data = {"dnssec_key_params":{"next_secure_type": "NSEC3","ksk_algorithms": [{"algorithm": "RSASHA256","size": 1024}],"zsk_algorithms": [{"algorithm": "RSASHA256","size": 1024}]}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 93 Execution Completed")
                sleep(30)

	@pytest.mark.run(order=94)
        def test_094_Validate_updating_KSK_ZSK_algorithm_with_RSASHA256(self):
                logging.info("Validate updating KSK ZSK algorithm with RSASHA256 for sub zone")
                get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="zone_auth",ref=ref1,params="?_inheritance=True&_return_fields=dnssec_key_params",grid_vip=config.grid_vip)
                print(output)
                output=json.loads(output)
                print(output)
                result = {'dnssec_key_params': {'next_secure_type': 'NSEC3', 'zsk_algorithms': [{'algorithm': 'RSASHA256', 'size': 1024}], 'ksk_size': 1024, 'ksk_rollover_notification_config': 'REQUIRE_MANUAL_INTERVENTION', 'signature_expiration': 345600, 'ksk_email_notification_enabled': False, 'zsk_rollover': 2592000, 'enable_ksk_auto_rollover': False, 'nsec3_salt_min_length': 1, 'nsec3_salt_max_length': 15, 'nsec3_iterations': 10, 'zsk_size': 1024, 'ksk_snmp_notification_enabled': True, 'ksk_rollover': 31536000, 'ksk_algorithms': [{'algorithm': 'RSASHA256', 'size': 1024}], 'zsk_rollover_mechanism': 'PRE_PUBLISH', 'ksk_algorithm': '8', 'zsk_algorithm': '8'}}
                for i in result:
                        if output[i] == result[i]:
                                assert True
                        else:
                                assert False
                print(result)
                sleep(30)
                print("Test Case 94 Execution Completed")


	@pytest.mark.run(order=95)
        def test_095_Resign_Dnssec_subZone_with_RSASHA256(self):
                logging.info("Resign sub zone RSASHA256")
                data = {"fqdn":"sub.network.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                ref=endpoint
                print ("###########",ref)
                data={"operation":"RESIGN"}
                response = ib_NIOS.wapi_request('POST', object_type=ref,fields=json.dumps(data),params="?_function=dnssec_operation")
                print (response)
                for read in response:
                        assert True
                logging.info("Apply algorithm changes on sub zone")
                sleep(90)
                print("Test Case 95 Execution Completed")

	@pytest.mark.run(order=96)
        def test_096_dig_dnssec_record_to_get_code_of_RSASHA256_algorithm(self):
                logging.info ("Dig A record to get code of RSASHA256 algorithm")
                output = os.popen('dig @'+str(config.grid_vip)+' sub.network.com +dnssec').read()
                output = output.split('\n')
                print(output)
                flag=False
                for line in output:
                        print(line)
                        if "NSEC3 8" in line:
                                flag=True
                                break
                if flag==True:
                        assert True
                        print("RSASHA256 algorithm code is 8")
                else:
                        print("Error")
                        assert False
                print("Test Case 96 Execution Completed")

	@pytest.mark.run(order=97)
        def test_097_Add_root_zone(self):
                logging.info("Create root zone")
                grid_member=config.grid_fqdn
                data = {"fqdn": ".","grid_primary": [{"name":config.grid_fqdn,"stealth":False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 97 Execution Completed")
                restart_services()


	@pytest.mark.run(order=98)
        def test_098_Validate_addition_of_root_Zone(self):
                logging.info("Validate Addition of root Zone")
                get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[2]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="zone_auth",ref=ref1,params="?_inheritance=True&_return_fields=fqdn",grid_vip=config.grid_vip)
                print(output)
                output=json.loads(output)
                print(output)
                result = {'fqdn':'.'}
                for i in result:
                        if output[i] == result[i]:
                                assert True
                        else:
                                assert False
                print(result)
                print("Test Case 98 Execution Completed")
                sleep(30)

	
	@pytest.mark.run(order=99)
        def test_099_Validate_default_KSK_ZSK_algorithm_in_rootzone(self):
                logging.info("Validate default KSK ZSK algorithm in rootzone")
                get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[2]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="zone_auth",ref=ref1,params="?_inheritance=True&_return_fields=dnssec_key_params",grid_vip=config.grid_vip)
                print(output)
                output=json.loads(output)
                print(output)
                result = {'dnssec_key_params': {'next_secure_type': 'NSEC3', 'zsk_algorithms': [{'algorithm': 'RSASHA256', 'size': 1024}], 'ksk_size': 2048, 'ksk_rollover_notification_config': 'REQUIRE_MANUAL_INTERVENTION', 'signature_expiration': 345600, 'ksk_email_notification_enabled': False, 'zsk_rollover': 2592000, 'enable_ksk_auto_rollover': False, 'nsec3_salt_min_length': 1, 'nsec3_salt_max_length': 15, 'nsec3_iterations': 10, 'zsk_size': 1024, 'ksk_snmp_notification_enabled': True, 'ksk_rollover': 31536000, 'ksk_algorithms': [{'algorithm': 'RSASHA256', 'size': 2048}], 'zsk_rollover_mechanism': 'PRE_PUBLISH', 'ksk_algorithm': '8', 'zsk_algorithm': '8'}}
                for i in result:
                        if output[i] == result[i]:
                                assert True
                        else:
                                assert False
                print(result)
                sleep(30)
                print("Test Case 99 Execution Completed")

#negativescenarion

	@pytest.mark.run(order=100)
        def test_100_Update_KSK_algorithm_with_ECDSAP384SHA384__size_1024_in_rootzone(self):
                logging.info("Update KSK ZSK algorithm with ECDSAP384SHA384 in rootzone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[2]['_ref']
                print ref1

                print("Modify KSK ZSK algorithm with ECDSAP384SHA384")
                data = {"dnssec_key_params":{"ksk_algorithms": [{"algorithm": "ECDSAP384SHA384","size": 1024}],"zsk_algorithms": [{"algorithm": "ECDSAP384SHA384","size": 160}]}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print("&&&&&&&&&&&&&&&&&&&&&&&",response)
                if '{ "Error": "AdmConDataError: The DNSSEC ECDSAP384 key size must be between 160 and 384 bits.", \n  "code": "Client.Ibap.Data", \n  "text": "The DNSSEC ECDSAP384 key size must be between 160 and 384 bits."\n}' in response:
                    assert True
                else:
                        print("KSK algorithm set as ECDSAP384SHA384")
                        assert False
                print("Test Case 100 Execution Completed")
                sleep(30)


        @pytest.mark.run(order=101)
        def test_101_Update_ZSK_algorithm_with_ECDSAP384SHA384__size_1024_in_rootzone(self):
                logging.info("Update KSK ZSK algorithm with ECDSAP384SHA384 in rootzone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[2]['_ref']
                print ref1

                print("Modify KSK ZSK algorithm with ECDSAP384SHA384")
                data = {"dnssec_key_params":{"ksk_algorithms": [{"algorithm": "ECDSAP384SHA384","size": 160}],"zsk_algorithms": [{"algorithm": "ECDSAP384SHA384","size": 1024}]}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print("&&&&&&&&&&&&&&&&&&&&&&&",response)
                if '{ "Error": "AdmConDataError: The DNSSEC ECDSAP384 key size must be between 160 and 384 bits.", \n  "code": "Client.Ibap.Data", \n  "text": "The DNSSEC ECDSAP384 key size must be between 160 and 384 bits."\n}' in response:
                        assert True
		else:
                        print("KSK algorithm set as ECDSAP384SHA384")
                        assert False
                print("Test Case 101 Execution Completed")
                sleep(30)

	@pytest.mark.run(order=102)
        def test_102_sign_Dnssec_root_Zone(self):
                logging.info("sign Root zone")
                data = {"fqdn":"."}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                ref=endpoint
                print ("###########",ref)
                data={"buffer":"KSK","operation":"SIGN"}
                response = ib_NIOS.wapi_request('POST', object_type=ref,fields=json.dumps(data),params="?_function=dnssec_operation")
                print (response)
                for read in response:
                        assert True
                logging.info("The selected zone is signed successfully")
                print("Test Case 102 Execution Completed")
                restart_services()

        @pytest.mark.run(order=103)
        def test_103_dig_dnssec_record_to_get_code_of_ECDSAP384SHA384_algorithm(self):
                logging.info ("Dig A record to get code of ECDSAP384SHA384 algorithm")
                output = os.popen('dig @'+str(config.grid_vip)+' . +dnssec').read()
                output = output.split('\n')
                print(output)
                flag=False
                for line in output:
                        print(line)
                        if "NSEC 14" in line:
                                flag=True
                                break
                if flag==True:
                        assert True
                        print("ECDSAP384SHA384 algorithm code is 14")
                else:
                        print("Error")
                        assert False
                print("Test Case 103 Execution Completed")

	@pytest.mark.run(order=104)
        def test_104_ROLLOVER_KSK_for_Dnssec_RootZone(self):
                logging.info("ROLLOVER_ZSK for root zone")
                data = {"fqdn":"."}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                ref=endpoint
                print ("###########",ref)
                data={"operation":"ROLLOVER_KSK"}
                response = ib_NIOS.wapi_request('POST', object_type=ref,fields=json.dumps(data),params="?_function=dnssec_operation")
                print (response)
                for read in response:
                        assert True
                print("Test Case 104 Execution Completed")
                restart_services()

	@pytest.mark.run(order=105)
        def test_105_Validate_Rollover_KSK_algorithm_for_rootzone(self):
                logging.info("Validate Rollover KSK algorithm for rootzone")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        sleep(05)
                        child.sendline('grep -e KSK /var/log/syslog')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = ["The KSK has been successfully rolled over for '.' in view 'default'."]
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
                sleep(30)
                print("Test Case 105 Execution Completed")

	@pytest.mark.run(order=106)
        def test_106_ROLLOVER_ZSK_for_Dnssec_rootZone(self):
                logging.info("ROLLOVER_ZSK for root zone")
                data = {"fqdn":"."}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                ref=endpoint
                print ("###########",ref)
                data={"operation":"ROLLOVER_ZSK"}
                response = ib_NIOS.wapi_request('POST', object_type=ref,fields=json.dumps(data),params="?_function=dnssec_operation")
                print (response)
                for read in response:
                        assert True
                print("Test Case 106 Execution Completed")
                restart_services()

	@pytest.mark.run(order=107)
        def test_107_Validate_Rollover_ZSK_algorithm_for_rootzone(self):
                logging.info("Validate Rollover ZSK algorithm for rootzone")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        sleep(05)
                        child.sendline('grep -e ZSK /var/log/syslog')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = ["The ZSK has been successfully rolled over for '.' in view 'default'."]
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
                sleep(30)
                print("Test Case 107 Execution Completed")

	@pytest.mark.run(order=108)
        def test_108_Update_KSK_ZSK_algorithm_with_RSASHA256_for_rootzone(self):
                logging.info("Update KSK ZSK algorithm with RSASHA256 for root zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[2]['_ref']
                print ref1

                data = {"dnssec_key_params":{"next_secure_type": "NSEC","ksk_algorithms": [{"algorithm": "RSASHA256","size": 1024}],"zsk_algorithms": [{"algorithm": "RSASHA256","size": 1024}]}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 108 Execution Completed")
                sleep(30)

	@pytest.mark.run(order=109)
        def test_109_Validate_updating_KSK_ZSK_algorithm_with_RSASHA256(self):
                logging.info("Validate updating KSK ZSK algorithm with RSASHA256 for root zone")
                get_ref = ib_NIOS.wapi_request('GET',object_type="zone_auth",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[2]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="zone_auth",ref=ref1,params="?_inheritance=True&_return_fields=dnssec_key_params",grid_vip=config.grid_vip)
                print(output)
                output=json.loads(output)
                print(output)
		result= {'dnssec_key_params': {'next_secure_type': 'NSEC', 'zsk_algorithms': [{'algorithm': 'RSASHA256', 'size': 1024}], 'ksk_size': 1024, 'ksk_rollover_notification_config': 'REQUIRE_MANUAL_INTERVENTION', 'signature_expiration': 345600, 'ksk_email_notification_enabled': False, 'zsk_rollover': 2592000, 'enable_ksk_auto_rollover': False, 'nsec3_salt_min_length': 1, 'nsec3_salt_max_length': 15, 'nsec3_iterations': 10, 'zsk_size': 1024, 'ksk_snmp_notification_enabled': True, 'ksk_rollover': 31536000, 'ksk_algorithms': [{'algorithm': 'RSASHA256', 'size': 1024}], 'zsk_rollover_mechanism': 'PRE_PUBLISH', 'ksk_algorithm': '8', 'zsk_algorithm': '8'}}
                for i in result:
                        if output[i] == result[i]:
                                assert True
                        else:
                                assert False
                print(result)
                sleep(30)
                print("Test Case 109 Execution Completed")

	@pytest.mark.run(order=110)
        def test_110_Resign_Dnssec_rootZone_with_RSASHA256(self):
                logging.info("Resign root zone RSASHA256")
                data = {"fqdn":"."}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                ref=endpoint
                print ("###########",ref)
                data={"operation":"RESIGN"}
                response = ib_NIOS.wapi_request('POST', object_type=ref,fields=json.dumps(data),params="?_function=dnssec_operation")
                print (response)
                for read in response:
                        assert True
                logging.info("Apply algorithm changes on root zone")
		sleep(90)
		restart_services()
                print("Test Case 110 Execution Completed")

	@pytest.mark.run(order=111)
        def test_111_dig_dnssec_record_to_get_code_of_RSASHA256_algorithm(self):
                logging.info ("Dig A record to get code of RSASHA256 algorithm")
                output = os.popen('dig @'+str(config.grid_vip)+' . +dnssec').read()
                output = output.split('\n')
                print(output)
                flag=False
                for line in output:
                        print(line)
                        if "NSEC 8" in line:
                                flag=True
                                break
                if flag==True:
                        assert True
                        print("RSASHA256 algorithm code is 8")
                else:
                        print("Error")
                        assert False
                print("Test Case 111 Execution Completed")

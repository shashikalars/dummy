import re
import config
import pytest
import unittest
import logging
import subprocess
import os
import json
import ib_utils.ib_NIOS as ib_NIOS
import commands
import json, ast
import requests
import time
import pexpect

class Network(unittest.TestCase):
        @pytest.mark.run(order=1)
        def test_1_add_client_ip_mac_options_enable(self):
                logging.info("Grid DNS Properties: Enable the option - Add client IP and MAC address to outgoing recursive queries")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                data = {"add_client_ip_mac_options":True}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                logging.info("============================")
                print response
		read  = re.search(r'200',response)
                for read in  response:
                        assert True


				
	@pytest.mark.run(order=2)	
	def test_1_copy_client_ip_mac_options_enable(self):
                logging.info("Grid DNS Properties: Enable the option - Carryover client IP and MAC options to outgoing recursive queries")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                data = {"copy_client_ip_mac_options":True}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                logging.info("============================")
                print response
                read  = re.search(r'200',response)
                for read in  response:
                        assert True

        @pytest.mark.run(order=3)
        def test_1_add_client_ip_mac_options_enable_member_dns(self):
                logging.info("Member DNS Properties: Enable the option - Add client IP and MAC address to outgoing recursive queries")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                data = {"add_client_ip_mac_options":True}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                logging.info("============================")
                print response
                read  = re.search(r'200',response)
                for read in  response:
                        assert True





        @pytest.mark.run(order=4)
        def test_1_copy_client_ip_mac_options_enable_member_dns(self):
                logging.info("Member DNS Properties: Enable the option - Carryover client IP and MAC options to outgoing recursive queries")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                data = {"copy_client_ip_mac_options":True}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                logging.info("============================")
                print response
                read  = re.search(r'200',response)
                for read in  response:
                        assert True




        @pytest.mark.run(order=5)
        def test_1_add_client_ip_mac_options_disable(self):
                logging.info("Grid DNS Properties: Disable the option - Add client IP and MAC address to outgoing recursive queries")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                data = {"add_client_ip_mac_options":False}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                logging.info("============================")
                print response
                read  = re.search(r'200',response)
                for read in  response:
                        assert True





        @pytest.mark.run(order=6)
        def test_1_copy_client_ip_mac_options_disable(self):
                logging.info("Grid DNS Properties: Disable the option - Carryover client IP and MAC options to outgoing recursive queries")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                data = {"copy_client_ip_mac_options":False}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                logging.info("============================")
                print response
                read  = re.search(r'200',response)
                for read in  response:
                        assert True


				
        @pytest.mark.run(order=7)
        def test_1_add_client_ip_mac_options_disable_member_dns(self):
                logging.info("Member DNS Properties: Disable the option - Add client IP and MAC address to outgoing recursive queries")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                data = {"add_client_ip_mac_options":False}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                logging.info("============================")
                print response
                read  = re.search(r'200',response)
                for read in  response:
                        assert True




        @pytest.mark.run(order=8)
        def test_1_copy_client_ip_mac_options_disable_member_dns(self):
                logging.info("Member DNS Properties: Disable the option - Carryover client IP and MAC options to outgoing recursive queries")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                data = {"copy_client_ip_mac_options":False}
		
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                logging.info("============================")
                print response
                read  = re.search(r'200',response)
                for read in  response:
                        assert True





        @pytest.mark.run(order=9)
        def test_1_add_client_ip_mac_options_disable_when_ATC_enabled(self):
                logging.info("Member DNS Properties: Disable the option - Add client IP and MAC address to outgoing recursive queries - when forwarding to ActiveTrust Cloud is enabled on member ")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                data = {"add_client_ip_mac_options":True,"copy_client_ip_mac_options":True,"atc_fwd_access_key":"3f498c266d03354f058aeb44729bf6d2","atc_fwd_enable": True,"atc_fwd_resolver_address": "10.0.2.35","atc_fwd_forward_first": False}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                logging.info("============================")
                print response
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
				
		data = {"add_client_ip_mac_options":False}
		response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
		response = str(response)
                logging.info("============================")
                print response
                if re.search(r'400',response):
			assert True
		else:
			assert False

        @pytest.mark.run(order=10)
        def test_1_add_client_ip_mac_options_disable_when_ATC_disabled(self):
                logging.info("Member DNS Properties: Disable the option - Add client IP and MAC address to outgoing recursive queries - when forwarding to ActiveTrust Cloud is disabled on member ")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
				
	        data = {"add_client_ip_mac_options":False,"atc_fwd_enable": False}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
		response = str(response)
                logging.info("============================")
                print response
                read  = re.search(r'200',response)
                for read in  response:
                        assert True





	
				


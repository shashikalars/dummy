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

global ref1,ref2,ref3,ref4,ref5,ref6

class Network(unittest.TestCase):
        @pytest.mark.run(order=1)
        def test_101_Create_New_AuthZone(self):
                logging.info("Create A new Zone")
                data = {"fqdn": "zone.com"}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Zone zone.com created")
				
	@pytest.mark.run(order=2)
	def test_102_Create_IPv4_network_reverse_mapping_zone(self):
                logging.info("Create an ipv4 network and it's reverse mapping zone")
                data = {"network": "10.0.0.0/8","auto_create_reversezone":True}
                response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Created the network 10.0.0.0/8 and 10.in-addr.arpa zone")

        @pytest.mark.run(order=3)
        def test_103_Create_IPv6_network_reverse_mapping_zone(self):
                logging.info("Create an ipv6 network and it's reverse mapping zone")
                data = {"network": "1234::/64","auto_create_reversezone":True}
                response = ib_NIOS.wapi_request('POST', object_type="ipv6network", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Created the ipv6network 1234::/64 and reverse mapping zone")

		
	@pytest.mark.run(order=4)
        def test_104_Create_A_AAAA_PTR_HOST_for_AuthZone(self):
                logging.info("Create A,AAAA,PTR,HOST record for the zone zone.com")
                data = {"ipv4addr":"10.0.0.250","name":"arec1.zone.com"}
                response = ib_NIOS.wapi_request('POST', object_type="record:a", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("A record created for the zone zone.com")
				
		data = {"ipv6addr":"1234::1","name":"aaaarec1.zone.com"}
		response = ib_NIOS.wapi_request('POST', object_type="record:aaaa", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("AAAA record created for the zone zone.com")

                data = {"name":"ptrrec1.zone.com","ptrdname":"ptr.test.com"}
                response = ib_NIOS.wapi_request('POST', object_type="record:ptr", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("PTR record created for the zone zone.com")

				
		data ={"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "10.0.0.1","mac": "11:11:11:11:11:15"}], "name": "host.zone.com","view": "default"} 
		response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Host record created for the zone zone.com and network 10.0.0.0/8")
				
				
				
	@pytest.mark.run(order=5)
       	def test_105_Create_HOST_Fixedaddress_for_network(self):
                logging.info("Create Fixedaddress for the network 10.0.0.0/8")
                data = {"ipv4addr":"10.0.0.20","name":"fixed_address1","mac":"11:11:11:11:11:11","network":"10.0.0.0/8"}
                response = ib_NIOS.wapi_request('POST', object_type="fixedaddress", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Fixedaddress created for the network 10.0.0.0/8")	


        @pytest.mark.run(order=6)
        def test_106_Create_HOST_Fixedaddress_for_ipv6_network(self):
                logging.info("Create Fixedaddress for the ipv6 network 1234::/64")
                data = {"ipv6addr":"1234::1","name":"fixed_address1","duid":"11:11","network":"1234::/64"}
                response = ib_NIOS.wapi_request('POST', object_type="ipv6fixedaddress", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Fixedaddress created for the ipv6network 1234::/64")


	@pytest.mark.run(order=7)
        def test_107_create_superhost_with_dns_and_dhcp_objects(self):
                logging.info("Create super host")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:a", grid_vip=config.grid_vip)
                ref1 = json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:aaaa", grid_vip=config.grid_vip)
                ref2= json.loads(get_ref)[0]['_ref']	
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:ptr",grid_vip=config.grid_vip)
                ref3= json.loads(get_ref)[3]['_ref']	
		get_ref = ib_NIOS.wapi_request('GET', object_type="record:host", grid_vip=config.grid_vip)
                ref4= json.loads(get_ref)[0]['_ref']
		get_ref = ib_NIOS.wapi_request('GET', object_type="fixedaddress", grid_vip=config.grid_vip)
                ref5= json.loads(get_ref)[0]['_ref']
		get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6fixedaddress", grid_vip=config.grid_vip)
                ref6= json.loads(get_ref)[0]['_ref']

                data = {"dns_associated_objects" : [ref1,ref2,ref3,ref4],"dhcp_associated_objects":[ref5,ref6],"name": "SUPERHOST1"}
		response = ib_NIOS.wapi_request('POST', object_type="superhost", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Created the superhost")	

        @pytest.mark.run(order=8)
        def test_108_negative_create_superhost_with_dns_and_dhcp_objects(self):
                logging.info("Create super host")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:a", grid_vip=config.grid_vip)
                ref1 = json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:aaaa", grid_vip=config.grid_vip)
                ref2= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:ptr",grid_vip=config.grid_vip)
                ref3= json.loads(get_ref)[3]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:host", grid_vip=config.grid_vip)
                ref4= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="fixedaddress", grid_vip=config.grid_vip)
                ref5= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6fixedaddress", grid_vip=config.grid_vip)
                ref6= json.loads(get_ref)[0]['_ref']

                data = {"dns_associated_objects" : [ref1,ref2,ref3,ref4],"dhcp_associated_objects":[ref5,ref6],"name": "SUPERHOST2"}
                response = ib_NIOS.wapi_request('POST', object_type="superhost", fields=json.dumps(data), grid_vip=config.grid_vip)
		print response
                logging.info(response)
                assert response[0] == 400, "expect error message as : super host record is already associated with another super host"
                logging.info("Cannot create the superhost when DNS or DHCP records are associated to other superhost")

				
        @pytest.mark.run(order=9)
        def test_109_disable_superhost(self):
                get_ref = ib_NIOS.wapi_request('GET', object_type="superhost", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']

                get_ref = ib_NIOS.wapi_request('GET', object_type="record:a", grid_vip=config.grid_vip)
                ref1 = json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:aaaa", grid_vip=config.grid_vip)
                ref2= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:ptr",grid_vip=config.grid_vip)
                ref3= json.loads(get_ref)[3]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:host", grid_vip=config.grid_vip)
                ref4= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="fixedaddress", grid_vip=config.grid_vip)
                ref5= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6fixedaddress", grid_vip=config.grid_vip)
                ref6= json.loads(get_ref)[0]['_ref']


                logging.info("Modify a superhost")
                data = {"dns_associated_objects" : [ref1,ref2,ref3,ref4],"dhcp_associated_objects":[ref5,ref6],"name": "SUPERHOST1","disabled":True}
                response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True


        @pytest.mark.run(order=10)
        def test_201_get_superhostchild(self):

 	        response = ib_NIOS.wapi_request('GET', object_type="superhostchild",params="?parent=SUPERHOST1", grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("GET superhostchild object")
		
        @pytest.mark.run(order=11)
        def test_202_delete_superhost(self):

                get_ref = ib_NIOS.wapi_request('GET', object_type="superhost", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']


                logging.info("Delete a superhost")
                response = ib_NIOS.wapi_request('DELETE', ref=ref1, grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True	
		logging.info("DELETED the superhost SUPERHOST1")


        @pytest.mark.run(order=12)
        def test_203_create_superhost_with_only_dns_objects(self):
                logging.info("Create super host with only DNS objects")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:a", grid_vip=config.grid_vip)
                ref1 = json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:aaaa", grid_vip=config.grid_vip)
                ref2= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:ptr",grid_vip=config.grid_vip)
                ref3= json.loads(get_ref)[3]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:host", grid_vip=config.grid_vip)
                ref4= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="fixedaddress", grid_vip=config.grid_vip)
                ref5= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6fixedaddress", grid_vip=config.grid_vip)
                ref6= json.loads(get_ref)[0]['_ref']

                data = {"dns_associated_objects" : [ref1,ref2,ref3,ref4],"dhcp_associated_objects":[],"name": "SUPERHOST1"}
                response = ib_NIOS.wapi_request('POST', object_type="superhost", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Created the superhost with only DNS objects")

        @pytest.mark.run(order=13)
        def test_204_create_superhost_with_only_dhcp_objects(self):
                logging.info("Create super host with only DHCP objects")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:a", grid_vip=config.grid_vip)
                ref1 = json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:aaaa", grid_vip=config.grid_vip)
                ref2= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:ptr",grid_vip=config.grid_vip)
                ref3= json.loads(get_ref)[3]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:host", grid_vip=config.grid_vip)
                ref4= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="fixedaddress", grid_vip=config.grid_vip)
                ref5= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6fixedaddress", grid_vip=config.grid_vip)
                ref6= json.loads(get_ref)[0]['_ref']

                data = {"dns_associated_objects" : [],"dhcp_associated_objects":[ref5,ref6],"name": "SUPERHOST2"}
                response = ib_NIOS.wapi_request('POST', object_type="superhost", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Created the superhost with only DHCP objects")


        @pytest.mark.run(order=14)
        def test_205_create_superhost_with_no_dns_dhcp_objects(self):
                logging.info("Create super host with no DNS and DHCP objects")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:a", grid_vip=config.grid_vip)
                ref1 = json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:aaaa", grid_vip=config.grid_vip)
                ref2= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:ptr",grid_vip=config.grid_vip)
                ref3= json.loads(get_ref)[3]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:host", grid_vip=config.grid_vip)
                ref4= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="fixedaddress", grid_vip=config.grid_vip)
                ref5= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6fixedaddress", grid_vip=config.grid_vip)
                ref6= json.loads(get_ref)[0]['_ref']

                data = {"dns_associated_objects" : [],"dhcp_associated_objects":[],"name": "SUPERHOST3"}
                response = ib_NIOS.wapi_request('POST', object_type="superhost", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Created the superhost with no DNS and DHCP objects")

        @pytest.mark.run(order=15)
        def test_206_delete_superhost1(self):

                get_ref = ib_NIOS.wapi_request('GET', object_type="superhost",params="?name=SUPERHOST1", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']


                logging.info("Delete a superhost")
                response = ib_NIOS.wapi_request('DELETE', ref=ref1, grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True

        @pytest.mark.run(order=16)
        def test_207_delete_superhost2(self):

                get_ref = ib_NIOS.wapi_request('GET', object_type="superhost",params="?name=SUPERHOST2", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']


                logging.info("Delete a superhost")
                response = ib_NIOS.wapi_request('DELETE', ref=ref1, grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True


        @pytest.mark.run(order=17)
        def test_208_update_superhost(self):
                get_ref = ib_NIOS.wapi_request('GET', object_type="superhost",params="?name=SUPERHOST3", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']

                get_ref = ib_NIOS.wapi_request('GET', object_type="record:a", grid_vip=config.grid_vip)
                ref1 = json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:aaaa", grid_vip=config.grid_vip)
                ref2= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:ptr",grid_vip=config.grid_vip)
                ref3= json.loads(get_ref)[3]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:host", grid_vip=config.grid_vip)
                ref4= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="fixedaddress", grid_vip=config.grid_vip)
                ref5= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6fixedaddress", grid_vip=config.grid_vip)
                ref6= json.loads(get_ref)[0]['_ref']


                logging.info("Modify a superhost")
                data = {"dns_associated_objects" : [ref1,ref2,ref3,ref4],"dhcp_associated_objects":[ref5,ref6],"name": "SUPERHOST3","disabled":True}
                response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True

        @pytest.mark.run(order=18)
        def test_209_delete_superhost3(self):

                get_ref = ib_NIOS.wapi_request('GET', object_type="superhost",params="?name=SUPERHOST3", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']


                logging.info("Delete a superhost")
                response = ib_NIOS.wapi_request('DELETE', ref=ref1, grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True

        @pytest.mark.run(order=19)
        def test_301_Create_networkview(self):
                logging.info("Create networkview")
                data = {"name": "net_view1"}
                response = ib_NIOS.wapi_request('POST', object_type="networkview", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Network View net_view1 created")

        @pytest.mark.run(order=20)
        def test_302_custom_network_view_Create_New_AuthZone(self):
                logging.info("Create A new Zone in custom networkview")
                data = {"fqdn": "zone.com","view": "default.net_view1"}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Zone zone.com created in network view net_view1")
				
	@pytest.mark.run(order=21)
	def test_303_custom_network_view_Create_IPv4_network_reverse_mapping_zone(self):
                logging.info("Create an ipv4 network and it's reverse mapping zone in custom networkview")
                data = {"network": "10.0.0.0/8","auto_create_reversezone":True,"network_view": "net_view1"}
                response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Created the network 10.0.0.0/8 and 10.in-addr.arpa zone in custom networkview")

        @pytest.mark.run(order=22)
        def test_304_custom_network_view_Create_IPv6_network_reverse_mapping_zone(self):
                logging.info("Create an ipv6 network and it's reverse mapping zone in custom networkview")
                data = {"network": "1234::/64","auto_create_reversezone":True,"network_view": "net_view1"}
                response = ib_NIOS.wapi_request('POST', object_type="ipv6network", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Created the ipv6network 1234::/64 and reverse mapping zone in custom networkview")

		
	@pytest.mark.run(order=23)
        def test_305_custom_network_view_Create_A_AAAA_PTR_HOST_for_AuthZone(self):
                logging.info("Create A,AAAA,PTR,HOST record for the zone zone.com in custom networkview")
                data = {"ipv4addr":"10.0.0.250","name":"arec1.zone.com","view": "default.net_view1"}
                response = ib_NIOS.wapi_request('POST', object_type="record:a", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("A record created for the zone zone.com in custom networkview")
				
		data = {"ipv6addr":"1234::1","name":"aaaarec1.zone.com","view": "default.net_view1"}
		response = ib_NIOS.wapi_request('POST', object_type="record:aaaa", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("AAAA record created for the zone zone.com in custom networkview")

                data = {"name":"ptrrec1.zone.com","ptrdname":"ptr.test.com","view": "default.net_view1"}
                response = ib_NIOS.wapi_request('POST', object_type="record:ptr", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("PTR record created for the zone zone.com in custom networkview")

				
		data ={"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "10.0.0.1","mac": "11:11:11:11:11:15"}], "name": "host.zone.com","view": "default.net_view1"} 
		response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Host record created for the zone zone.com and network 10.0.0.0/8 in custom networkview")
				
				
				
	@pytest.mark.run(order=24)
       	def test_306_custom_network_view_Create_HOST_Fixedaddress_for_network(self):
                logging.info("Create Fixedaddress for the network 10.0.0.0/8 in custom networkview")
                data = {"ipv4addr":"10.0.0.20","name":"fixed_address1","mac":"11:11:11:11:11:11","network":"10.0.0.0/8","network_view": "net_view1"}
                response = ib_NIOS.wapi_request('POST', object_type="fixedaddress", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Fixedaddress created for the network 10.0.0.0/8 in custom networkview")	


        @pytest.mark.run(order=25)
        def test_307_custom_network_view_Create_HOST_Fixedaddress_for_ipv6_network(self):
                logging.info("Create Fixedaddress for the ipv6 network 1234::/64 in custom networkview")
                data = {"ipv6addr":"1234::1","name":"fixed_address1","duid":"11:11","network":"1234::/64","network_view": "net_view1"}
                response = ib_NIOS.wapi_request('POST', object_type="ipv6fixedaddress", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Fixedaddress created for the ipv6network 1234::/64 in custom networkview")


	@pytest.mark.run(order=26)
        def test_308_custom_network_view_create_superhost_with_dns_and_dhcp_objects(self):
                logging.info("Create super host with DNS and DHCP records associated from custom network view")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:a",params="?view=default.net_view1", grid_vip=config.grid_vip)
                ref1 = json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:aaaa",params="?view=default.net_view1", grid_vip=config.grid_vip)
                ref2= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:ptr",params="?view=default.net_view1",grid_vip=config.grid_vip)
                ref3= json.loads(get_ref)[2]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:host",params="?view=default.net_view1", grid_vip=config.grid_vip)
                ref4= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="fixedaddress",params="?network_view=net_view1", grid_vip=config.grid_vip)
                ref5= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6fixedaddress",params="?network_view=net_view1", grid_vip=config.grid_vip)
                ref6= json.loads(get_ref)[0]['_ref']


                data = {"dns_associated_objects" : [ref1,ref2,ref3,ref4],"dhcp_associated_objects":[ref5,ref6],"name": "SUPERHOST1"}
		print data
		response = ib_NIOS.wapi_request('POST', object_type="superhost", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Created the superhost with DNS and DHCP records associated from custom network view")	

        @pytest.mark.run(order=27)
        def test_309_custom_network_view_negative_create_superhost_with_dns_and_dhcp_objects(self):
                logging.info("Create super host with DNS and DHCP records associated from custom network view")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:a",params="?view=default.net_view1", grid_vip=config.grid_vip)
                ref1 = json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:aaaa",params="?view=default.net_view1", grid_vip=config.grid_vip)
                ref2= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:ptr",params="?view=default.net_view1",grid_vip=config.grid_vip)
                ref3= json.loads(get_ref)[2]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:host",params="?view=default.net_view1", grid_vip=config.grid_vip)
                ref4= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="fixedaddress",params="?network_view=net_view1", grid_vip=config.grid_vip)
                ref5= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6fixedaddress",params="?network_view=net_view1", grid_vip=config.grid_vip)
                ref6= json.loads(get_ref)[0]['_ref']

                data = {"dns_associated_objects" : [ref1,ref2,ref3,ref4],"dhcp_associated_objects":[ref5,ref6],"name": "SUPERHOST2"}
                response = ib_NIOS.wapi_request('POST', object_type="superhost", fields=json.dumps(data), grid_vip=config.grid_vip)
		print response
                logging.info(response)
                assert response[0] == 400, "expect error message as : super host record is already associated with another super host"
                logging.info("Cannot create the superhost when DNS or DHCP records are associated to other superhost")

				
        @pytest.mark.run(order=28)
        def test_401_custom_network_view_disable_superhost(self):
                get_ref = ib_NIOS.wapi_request('GET', object_type="superhost", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']


                get_ref = ib_NIOS.wapi_request('GET', object_type="record:a",params="?view=default.net_view1", grid_vip=config.grid_vip)
                ref1 = json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:aaaa",params="?view=default.net_view1", grid_vip=config.grid_vip)
                ref2= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:ptr",params="?view=default.net_view1",grid_vip=config.grid_vip)
                ref3= json.loads(get_ref)[2]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:host",params="?view=default.net_view1", grid_vip=config.grid_vip)
                ref4= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="fixedaddress",params="?network_view=net_view1", grid_vip=config.grid_vip)
                ref5= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6fixedaddress",params="?network_view=net_view1", grid_vip=config.grid_vip)
                ref6= json.loads(get_ref)[0]['_ref']

                logging.info("Modify a superhost")
                data = {"dns_associated_objects" : [ref1,ref2,ref3,ref4],"dhcp_associated_objects":[ref5,ref6],"name": "SUPERHOST1","disabled":True}
                response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True


        @pytest.mark.run(order=29)
        def test_402_custom_network_view_get_superhostchild(self):

 	        response = ib_NIOS.wapi_request('GET', object_type="superhostchild",params="?parent=SUPERHOST1", grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("GET superhostchild object")
		
        @pytest.mark.run(order=30)
        def test_403_custom_network_view_delete_superhost(self):

                get_ref = ib_NIOS.wapi_request('GET', object_type="superhost", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']


                logging.info("Delete a superhost")
                response = ib_NIOS.wapi_request('DELETE', ref=ref1, grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True	
		logging.info("DELETED the superhost SUPERHOST1")


        @pytest.mark.run(order=31)
        def test_404_custom_network_view_create_superhost_with_only_dns_objects(self):
                logging.info("Create super host with only DNS objects from custom networkview")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:a",params="?view=default.net_view1", grid_vip=config.grid_vip)
                ref1 = json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:aaaa",params="?view=default.net_view1", grid_vip=config.grid_vip)
                ref2= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:ptr",params="?view=default.net_view1",grid_vip=config.grid_vip)
                ref3= json.loads(get_ref)[2]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:host",params="?view=default.net_view1", grid_vip=config.grid_vip)
                ref4= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="fixedaddress",params="?network_view=net_view1", grid_vip=config.grid_vip)
                ref5= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6fixedaddress",params="?network_view=net_view1", grid_vip=config.grid_vip)
                ref6= json.loads(get_ref)[0]['_ref']

                data = {"dns_associated_objects" : [ref1,ref2,ref3,ref4],"dhcp_associated_objects":[],"name": "SUPERHOST1"}
                response = ib_NIOS.wapi_request('POST', object_type="superhost", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Created the superhost with only DNS objects")

        @pytest.mark.run(order=32)
        def test_405_custom_network_view_create_superhost_with_only_dhcp_objects(self):
                logging.info("Create super host with only DHCP objects from custom network view")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:a",params="?view=default.net_view1", grid_vip=config.grid_vip)
                ref1 = json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:aaaa",params="?view=default.net_view1", grid_vip=config.grid_vip)
                ref2= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:ptr",params="?view=default.net_view1",grid_vip=config.grid_vip)
                ref3= json.loads(get_ref)[2]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:host",params="?view=default.net_view1", grid_vip=config.grid_vip)
                ref4= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="fixedaddress",params="?network_view=net_view1", grid_vip=config.grid_vip)
                ref5= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6fixedaddress",params="?network_view=net_view1", grid_vip=config.grid_vip)
                ref6= json.loads(get_ref)[0]['_ref']

                data = {"dns_associated_objects" : [],"dhcp_associated_objects":[ref5,ref6],"name": "SUPERHOST2"}
                response = ib_NIOS.wapi_request('POST', object_type="superhost", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Created the superhost with only DHCP objects")


        @pytest.mark.run(order=33)
        def test_406_custom_network_view_create_superhost_with_no_dns_dhcp_objects(self):
                logging.info("Create super host with no DNS and DHCP objects")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:a",params="?view=default.net_view1", grid_vip=config.grid_vip)
                ref1 = json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:aaaa",params="?view=default.net_view1", grid_vip=config.grid_vip)
                ref2= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:ptr",params="?view=default.net_view1",grid_vip=config.grid_vip)
                ref3= json.loads(get_ref)[2]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:host",params="?view=default.net_view1", grid_vip=config.grid_vip)
                ref4= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="fixedaddress",params="?network_view=net_view1", grid_vip=config.grid_vip)
                ref5= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6fixedaddress",params="?network_view=net_view1", grid_vip=config.grid_vip)
                ref6= json.loads(get_ref)[0]['_ref']

                data = {"dns_associated_objects" : [],"dhcp_associated_objects":[],"name": "SUPERHOST3"}
                response = ib_NIOS.wapi_request('POST', object_type="superhost", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Created the superhost with no DNS and DHCP objects")

        @pytest.mark.run(order=34)
        def test_407_custom_network_view_delete_superhost1(self):

                get_ref = ib_NIOS.wapi_request('GET', object_type="superhost",params="?name=SUPERHOST1", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']


                logging.info("Delete a superhost")
                response = ib_NIOS.wapi_request('DELETE', ref=ref1, grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True

        @pytest.mark.run(order=35)
        def test_408_custom_network_view_delete_superhost2(self):

                get_ref = ib_NIOS.wapi_request('GET', object_type="superhost",params="?name=SUPERHOST2", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']


                logging.info("Delete a superhost")
                response = ib_NIOS.wapi_request('DELETE', ref=ref1, grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True


        @pytest.mark.run(order=36)
        def test_409_custom_network_view_update_superhost(self):
                get_ref = ib_NIOS.wapi_request('GET', object_type="superhost",params="?name=SUPERHOST3", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']

                get_ref = ib_NIOS.wapi_request('GET', object_type="record:a",params="?view=default.net_view1", grid_vip=config.grid_vip)
                ref1 = json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:aaaa",params="?view=default.net_view1", grid_vip=config.grid_vip)
                ref2= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:ptr",params="?view=default.net_view1",grid_vip=config.grid_vip)
                ref3= json.loads(get_ref)[2]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:host",params="?view=default.net_view1", grid_vip=config.grid_vip)
                ref4= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="fixedaddress",params="?network_view=net_view1", grid_vip=config.grid_vip)
                ref5= json.loads(get_ref)[0]['_ref']
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6fixedaddress",params="?network_view=net_view1", grid_vip=config.grid_vip)
                ref6= json.loads(get_ref)[0]['_ref']

                logging.info("Modify a superhost with DNS/DHCP records from the custom view")
                data = {"dns_associated_objects" : [ref1,ref2,ref3,ref4],"dhcp_associated_objects":[ref5,ref6],"name": "SUPERHOST3","disabled":True}
                response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True

        @pytest.mark.run(order=37)
        def test_501_custom_network_view_delete_superhost3(self):

                get_ref = ib_NIOS.wapi_request('GET', object_type="superhost",params="?name=SUPERHOST3", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']


                logging.info("Delete a superhost")
                response = ib_NIOS.wapi_request('DELETE', ref=ref1, grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True



				
				
	
				
				
	

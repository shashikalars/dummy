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
#from paramiko import client
#from log_capture import log_action as log
#from log_validation import log_validation as logv
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as comm_util

global ref1,ref2,ref3,ref4,ref5,ref6

class Network(unittest.TestCase):
	@pytest.mark.run(order=0)
        def test_100_add_dns_view(self):
            data={"name": "net_view1","comment":"Adding network view"}
            response=ib_NIOS.wapi_request('POST', object_type="networkview",fields=json.dumps(data))
            logging.info(response)
            read  = re.search(r'201',response)
            for read in  response:
                   assert True
	    logging.info("Network View created")

        @pytest.mark.run(order=1)
        def test_101_Create_New_AuthZone(self):
                logging.info("Create A new Zone")
                data = {"fqdn": "zone.com"}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
		data = {"fqdn": "zone.com","view": "default.net_view1"}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Zone zone.com created")
				
	@pytest.mark.run(order=2)
	def test_102_Create_IPv4_network_reverse_mapping_zone(self):		
                logging.info("Create an ipv4 network and it's reverse mapping zone")
                data = {"network": "9.0.0.0/8","auto_create_reversezone":False}
                response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                data = {"network": "10.0.0.0/16","auto_create_reversezone":False}
                response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                data = {"network": "20.0.0.0/8","auto_create_reversezone":False}
                response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
		data = {"network": "9.0.0.0/8","auto_create_reversezone":False,"network_view": "net_view1"}
                response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
		data = {"network": "10.0.0.0/16","auto_create_reversezone":False,"network_view": "net_view1"}
                response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                
		data = {"network": "20.0.0.0/8","auto_create_reversezone":False,"network_view": "net_view1"}
                response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
		logging.info("Created an ipv4 network and it's reverse mapping zone")
		
        @pytest.mark.run(order=3)
        def test_103_Create_IPv6_network_reverse_mapping_zone(self):
                logging.info("Create an ipv6 network and it's reverse mapping zone")
		data = {"network": "1231::/64","auto_create_reversezone":True}
                response = ib_NIOS.wapi_request('POST', object_type="ipv6network", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True

                data = {"network": "1234::/64","auto_create_reversezone":True}
                response = ib_NIOS.wapi_request('POST', object_type="ipv6network", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
		data = {"network": "2345::/64","auto_create_reversezone":True}
                response = ib_NIOS.wapi_request('POST', object_type="ipv6network", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
		
		data = {"network": "1231::/64","auto_create_reversezone":True,"network_view": "net_view1"}
                response = ib_NIOS.wapi_request('POST', object_type="ipv6network", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True

		data = {"network": "1234::/64","auto_create_reversezone":True,"network_view": "net_view1"}
                response = ib_NIOS.wapi_request('POST', object_type="ipv6network", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True

                data = {"network": "2345::/64","auto_create_reversezone":True,"network_view": "net_view1"}
                response = ib_NIOS.wapi_request('POST', object_type="ipv6network", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Created ipv6 network and it's reverse mapping zone")

		
	@pytest.mark.run(order=4)
        def test_104_Create_IPV4_network_hosts(self):
		data ={"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "9.0.0.1","mac": "11:11:11:11:11:19"}], "name": "host9.zone.com","view": "default","extattrs": {"Site": {"value": "100"}},"comment":"host1"}
                response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Host record created for the zone zone.com and network 9.0.0.0/8")
	
		data ={"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "10.0.0.1","mac": "11:11:11:11:11:11"}], "name": "host1.zone.com","view": "default","extattrs": {"Site": {"value": "100"}},"comment":"host1"} 
		response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
		logging.info("Host record created for the zone zone.com and network 10.0.0.0/16")

		data ={"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "10.0.0.3","mac": "11:11:11:11:11:13"}], "name": "host3.zone.com","view": "default","extattrs": {"Site": {"value": "100"}},"comment":"host3"}
                response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Host record created for the zone zone.com and network 10.0.0.0/16")
		
		data ={"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "10.0.0.5","mac": "11:11:11:11:11:15"}], "name": "host5.zone.com","view": "default","extattrs": {"Site": {"value": "500"}}}
                response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Host record created for the zone zone.com and network 10.0.0.0/16")

		data ={"ipv4addrs": [{"configure_for_dhcp": False,"ipv4addr": "10.0.0.7","mac": "11:11:11:11:11:17"}], "name": "host7.zone.com","view": "default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Host record created for the zone zone.com and network 10.0.0.0/16")		
		
		data ={"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "9.0.0.1","mac": "11:11:11:11:11:19"}], "name": "host9.zone.com","view": "default.net_view1","extattrs": {"Site": {"value": "100"}},"comment":"host1"}
                response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Host record created for the zone zone.com and network 9.0.0.0/8")

		data ={"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "10.0.0.1","mac": "11:11:11:11:11:11"}], "name": "host1.zone.com","view": "default.net_view1","extattrs": {"Site": {"value": "100"}},"comment":"host1"}
                response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Host record created for the zone zone.com and network 10.0.0.0/16")

                data ={"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "10.0.0.3","mac": "11:11:11:11:11:13"}], "name": "host3.zone.com","view": "default.net_view1","extattrs": {"Site": {"value": "100"}},"comment":"host3"}
                response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Host record created for the zone zone.com and network 10.0.0.0/16")

                data ={"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "10.0.0.5","mac": "11:11:11:11:11:15"}], "name": "host5.zone.com","view": "default.net_view1","extattrs": {"Site": {"value": "500"}}}
                response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Host record created for the zone zone.com and network 10.0.0.0/16")		
		
		data ={"ipv4addrs": [{"configure_for_dhcp": False,"ipv4addr": "10.0.0.7","mac": "11:11:11:11:11:17"}], "name": "host7.zone.com","view": "default.net_view1"}
                response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Host record created for the zone zone.com and network 10.0.0.0/16")

	@pytest.mark.run(order=5)
	def test_105_get_network_HOST_records_for_network(self):
	    response = ib_NIOS.wapi_request('GET',object_type="record:host?network=10.0.0.0/16")
	    response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
	    response=response.split(',')
	    logging.info(response)
	    if ((response[4]!='"ipv4addr":"9.0.0.1"' and response[4]=='"ipv4addr":"10.0.0.1"') and response[7]=='"view":"default"' and response[12]=='"ipv4addr":"10.0.0.3"' and response[15]=='"view":"default"'and response[20]=='"ipv4addr":"10.0.0.5"' and response[23]=='"view":"default"' and response[28]=='"ipv4addr":"10.0.0.7"' and response[31]=='"view":"default"' and response[36]=='"ipv4addr":"10.0.0.1"' and response[39]=='"view":"default.net_view1"' and response[44]=='"ipv4addr":"10.0.0.3"' and response[47]=='"view":"default.net_view1"' and response[52]=='"ipv4addr":"10.0.0.5"' and response[55]=='"view":"default.net_view1"' and response[60]=='"ipv4addr":"10.0.0.7"' and response[63]=='"view":"default.net_view1"'):
		    assert True
	    else:
	            assert False
	    logging.info("Network_HOST_records_for_10.0.0.0/8_network")
	    
	@pytest.mark.run(order=6)
        def test_106_get_network_HOST_records_for_Site_100(self):
            response = ib_NIOS.wapi_request('GET',object_type="record:host?*Site=100&network=10.0.0.0/16")
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
	    response=response.split(',')      
	    logging.info(response)      
	    if ((response[4]!='"ipv4addr":"9.0.0.1"' and response[4]=='"ipv4addr":"10.0.0.1"') and response[3]=='"host":"host1.zone.com"' and response[7]=='"view":"default"' and response[11]=='"host":"host3.zone.com"' and response[12]=='"ipv4addr":"10.0.0.3"' and response[15]=='"view":"default"' and response[19]=='"host":"host1.zone.com"' and response[20]=='"ipv4addr":"10.0.0.1"' and response[23]=='"view":"default.net_view1"' and response[27]=='"host":"host3.zone.com"' and response[28]=='"ipv4addr":"10.0.0.3"' and response[31]=='"view":"default.net_view1"'):

	    	    assert True
            else:
                    assert False
	    logging.info("Network_HOST_records_for_Site_100")

	@pytest.mark.run(order=7)
        def test_107_get_network_HOST_records_using_host_name(self):
            response = ib_NIOS.wapi_request('GET',object_type="record:host",params="?name=host3.zone.com&_return_fields=ipv4addrs")
	    response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
	    response=response.split(',')
	    logging.info(response)
            if (response[3]=='"host":"host3.zone.com"' and response[4]=='"ipv4addr":"10.0.0.3"' and response[9]=='"host":"host3.zone.com"' and response[10]=='"ipv4addr":"10.0.0.3"'):

                    assert True
            else:
                    assert False
            logging.info("Network_HOST_records_using_host_name")

	@pytest.mark.run(order=8)
        def test_108_get_network_HOST_records_using_Site_host_name(self):
	    response = ib_NIOS.wapi_request('GET',object_type="record:host",params="?*Site=100&name=host1.zone.com")
	    logging.info(response)
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
	    if ((response[4]!='"ipv4addr":"9.0.0.1"' and response[4]=='"ipv4addr":"10.0.0.1"') and response[3]=='"host":"host1.zone.com"' and response[7]=='"view":"default"' and response[11]=='"host":"host1.zone.com"' and response[12]=='"ipv4addr":"10.0.0.1"' and response[15]=='"view":"default.net_view1"'):
 
                    assert True
            else:
                    assert False
            logging.info("Network_HOST_records_using_Site_host_name")

	@pytest.mark.run(order=9)
        def test_109_get_network_HOST_records_using_host_name(self):
            response = ib_NIOS.wapi_request('GET',object_type="record:host?name=host1.zone.com")
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
	    if ((response[4]!='"ipv4addr":"9.0.0.1"' and response[4]=='"ipv4addr":"10.0.0.1"') and response[3]=='"host":"host1.zone.com"' and response[7]=='"view":"default.net_view1"' and response[11]=='"host":"host1.zone.com"' and response[12]=='"ipv4addr":"10.0.0.1"' and response[15]=='"view":"default"'):
		    assert True
            else:
                    assert False
            logging.info("Network_HOST_records_using_host_name")

	@pytest.mark.run(order=10)
        def test_110_get_network_HOST_records_using_Site_comment(self):
            response = ib_NIOS.wapi_request('GET',object_type="record:host",params="?*Site=100&comment~=host1&network=10.0.0.0/16")
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
	    if ((response[3]!='"host":"host9.zone.com"' and response[3]=='"host":"host1.zone.com"') and response[4]=='"ipv4addr":"10.0.0.1"' and response[7]=='"view":"default"' and response[11]=='"host":"host1.zone.com"' and response[12]=='"ipv4addr":"10.0.0.1"' and response[15]=='"view":"default.net_view1"'):
                    assert True
            else:
                    assert False
            logging.info("Network_HOST_records_using_Site_comment")
	
	@pytest.mark.run(order=11)
        def test_111_Create_HOST_Fixedaddress_for_IPV6_network(self):
	    data ={"ipv6addrs": [{"configure_for_dhcp": True,"ipv6addr": "1231::1","duid": "12:11"}], "name": "host01.zone.com","view": "default","extattrs": {"Site": {"value": "100"}},"comment":"host11"}
            response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
            logging.info(response)
            read  = re.search(r'201',response)
            for read in  response:
                     assert True

	    data ={"ipv6addrs": [{"configure_for_dhcp": True,"ipv6addr": "1234::1","duid": "12:34"}], "name": "host11.zone.com","view": "default","extattrs": {"Site": {"value": "100"}},"comment":"host11"}
            response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
            logging.info(response)
            read  = re.search(r'201',response)
            for read in  response:
                     assert True

	    data ={"ipv6addrs": [{"configure_for_dhcp": True,"ipv6addr": "1234::3","duid": "12:33"}], "name": "host13.zone.com","view": "default","extattrs": {"Site": {"value": "100"}},"comment":"host13"}
            response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
            logging.info(response)
            read  = re.search(r'201',response)
            for read in  response:
                     assert True

	    data ={"ipv6addrs": [{"configure_for_dhcp": False,"ipv6addr": "1234::5","duid": "12:55"}], "name": "host15.zone.com","view": "default"}
            response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
            logging.info(response)
            read  = re.search(r'201',response)
            for read in  response:
                     assert True

  	    data ={"ipv6addrs": [{"configure_for_dhcp": True,"ipv6addr": "1234::7","duid": "12:77"}], "name": "host17.zone.com","view": "default","extattrs": {"Site": {"value": "700"}}}
            response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
            logging.info(response)
            read  = re.search(r'201',response)
            for read in  response:
                     assert True

	    data ={"ipv6addrs": [{"configure_for_dhcp": True,"ipv6addr": "1231::1","duid": "12:11"}], "name": "host01.zone.com","view": "default.net_view1","extattrs": {"Site": {"value": "100"}},"comment":"host11"}
            response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
            logging.info(response)
            read  = re.search(r'201',response)
            for read in  response:
                     assert True

	    data ={"ipv6addrs": [{"configure_for_dhcp": True,"ipv6addr": "1234::1","duid": "12:34"}], "name": "host11.zone.com","view": "default.net_view1","extattrs": {"Site": {"value": "100"}},"comment":"host11"}
            response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
            logging.info(response)
            read  = re.search(r'201',response)
            for read in  response:
                     assert True

            data ={"ipv6addrs": [{"configure_for_dhcp": True,"ipv6addr": "1234::3","duid": "12:33"}], "name": "host13.zone.com","view": "default.net_view1","extattrs": {"Site": {"value": "100"}},"comment":"host13"}
            response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
            logging.info(response)
            read  = re.search(r'201',response)
            for read in  response:
                     assert True

            data ={"ipv6addrs": [{"configure_for_dhcp": False,"ipv6addr": "1234::5","duid": "12:55"}], "name": "host15.zone.com","view": "default.net_view1"}
            response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
            logging.info(response)
            read  = re.search(r'201',response)
            for read in  response:
                     assert True

	    data ={"ipv6addrs": [{"configure_for_dhcp": True,"ipv6addr": "1234::7","duid": "12:77"}], "name": "host17.zone.com","view": "default.net_view1","extattrs": {"Site": {"value": "100"}}}
            response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
            logging.info(response)
            read  = re.search(r'201',response)
            for read in  response:
                     assert True
            logging.info("Host record created for the zone zone.com and network 1234::1/64")

	@pytest.mark.run(order=12)
        def test_112_get_network_HOST_records_for_ipv6_network(self):
            response = ib_NIOS.wapi_request('GET',object_type="record:host?network=1234::/64")
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
	    if((response[5]!='"ipv6addr":"1231::1"' and response[5]=='"ipv6addr":"1234::1"') and response[4]=='"host":"host11.zone.com"' and response[7]=='"view":"default"' and response[12]=='"host":"host13.zone.com"' and response[13]=='"ipv6addr":"1234::3"' and response[15]=='"view":"default"' and response[20]=='"host":"host15.zone.com"' and response[21]=='"ipv6addr":"1234::5"' and response[23]=='"view":"default"' and response[28]=='"host":"host17.zone.com"' and response[29]=='"ipv6addr":"1234::7"' and response[31]=='"view":"default"' and response[36]=='"host":"host11.zone.com"' and response[37]=='"ipv6addr":"1234::1"'and response[39]=='"view":"default.net_view1"' and response[44]=='"host":"host13.zone.com"' and response[45]=='"ipv6addr":"1234::3"' and response[47]=='"view":"default.net_view1"' and response[52]=='"host":"host15.zone.com"' and response[53]=='"ipv6addr":"1234::5"' and response[55]=='"view":"default.net_view1"' and response[60]=='"host":"host17.zone.com"' and response[61]=='"ipv6addr":"1234::7"' and response[63]=='"view":"default.net_view1"'):
		    assert True
            else:
                    assert False
            logging.info("Network_HOST_records_for_1234::/64_network")
	
	@pytest.mark.run(order=13)
        def test_113_get_network_HOST_records_for_network_Site(self):
            response = ib_NIOS.wapi_request('GET',object_type="record:host?*Site=100&network=1234::/64")
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
	    if((response[5]!='"ipv6addr":"1231::1"' and response[5]=='"ipv6addr":"1234::1"') and response[4]=='"host":"host11.zone.com"' and response[7]=='"view":"default"' and response[12]=='"host":"host13.zone.com"' and response[13]=='"ipv6addr":"1234::3"' and response[15]=='"view":"default"' and response[20]=='"host":"host11.zone.com"' and response[21]=='"ipv6addr":"1234::1"'and response[23]=='"view":"default.net_view1"' and response[28]=='"host":"host13.zone.com"' and response[29]=='"ipv6addr":"1234::3"' and response[31]=='"view":"default.net_view1"'):
		    assert True
            else:
                    assert False
            logging.info("Network_HOST_records_for_1234::/64_network_Site")

	@pytest.mark.run(order=14)
        def test_114_get_network_HOST_records_using_host_name(self):
	    response = ib_NIOS.wapi_request('GET',object_type="record:host",params="?name=host15.zone.com&_return_fields=ipv6addrs")
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
	    if ((response[5]!='"ipv6addr":"1234::1"' and response[5]=='"ipv6addr":"1234::5"') and response[4]=='"host":"host15.zone.com"' and response[10]=='"host":"host15.zone.com"' and response[11]=='"ipv6addr":"1234::5"'):
		    assert True
            else:
                    assert False
            logging.info("Network_HOST_records_using_host_name")

	@pytest.mark.run(order=15)
        def test_115_get_network_HOST_records_using_Site_host_name(self):
            response = ib_NIOS.wapi_request('GET',object_type="record:host",params="?*Site=100&name=host13.zone.com")
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
	    if((response[5]!='"ipv6addr":"1234::1"' and response[5]=='"ipv6addr":"1234::3"') and response[4]=='"host":"host13.zone.com"' and response[7]=='"view":"default"' and response[12]=='"host":"host13.zone.com"' and response[13]=='"ipv6addr":"1234::3"' and response[15]=='"view":"default.net_view1"'):
	    	    assert True
            else:
                    assert False
            logging.info("Network_HOST_records_using_Site_host_name_Site")

	@pytest.mark.run(order=16)
        def test_116_get_network_HOST_records_using_Site_host_name(self):
            response = ib_NIOS.wapi_request('GET',object_type="record:host?name=host13.zone.com")
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
	    if((response[5]!='"ipv6addr":"1234::1"' and response[5]=='"ipv6addr":"1234::3"') and response[4]=='"host":"host13.zone.com"' and response[7]=='"view":"default.net_view1"' and response[12]=='"host":"host13.zone.com"' and response[13]=='"ipv6addr":"1234::3"' and response[15]=='"view":"default"'):
                    assert True
            else:
                    assert False
            logging.info("Network_HOST_records_using_Site_host_name")
	
	@pytest.mark.run(order=17)
        def test_117_get_network_HOST_records_using_Site_comment(self):
            response = ib_NIOS.wapi_request('GET',object_type="record:host",params="?*Site=100&comment~=host13")
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
            if((response[5]!='"ipv6addr":"1234::1"' and response[5]=='"ipv6addr":"1234::3"') and response[4]=='"host":"host13.zone.com"' and response[7]=='"view":"default"' and response[12]=='"host":"host13.zone.com"' and response[13]=='"ipv6addr":"1234::3"' and response[15]=='"view":"default.net_view1"'):
                    assert True
            else:
                    assert False
            logging.info("Network_HOST_records_using_Site_comment")

	@pytest.mark.run(order=18)
        def test_118_get_network_HOST_records_IPV4_using_configure_for_dhcp(self):
            response = ib_NIOS.wapi_request('GET',object_type="record:host_ipv4addr",params="?_return_fields=configure_for_dhcp,ipv4addr")
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
	    if (response[1]=='"configure_for_dhcp":true' and response[2]=='"ipv4addr":"9.0.0.1"' and response[4]=='"configure_for_dhcp":true' and response[5]=='"ipv4addr":"10.0.0.1"' and response[7]=='"configure_for_dhcp":true' and response[8]=='"ipv4addr":"10.0.0.3"' and response[10]=='"configure_for_dhcp":true' and response[11]=='"ipv4addr":"10.0.0.5"' and response[13]=='"configure_for_dhcp":false' and response[14]=='"ipv4addr":"10.0.0.7"' and response[16]=='"configure_for_dhcp":true' and response[17]=='"ipv4addr":"9.0.0.1"' and response[19]=='"configure_for_dhcp":true' and response[20]=='"ipv4addr":"10.0.0.1"' and response[22]=='"configure_for_dhcp":true' and response[23]=='"ipv4addr":"10.0.0.3"' and response[25]=='"configure_for_dhcp":true' and response[26]=='"ipv4addr":"10.0.0.5"' and response[28]=='"configure_for_dhcp":false' and response[29]=='"ipv4addr":"10.0.0.7"'):
		    assert True
            else:
                    assert False
            logging.info("Network_HOST_records_using_configure_for_dhcp_ipv4")

	@pytest.mark.run(order=19)
        def test_119_get_network_HOST_records_IPV6_using_configure_for_dhcp(self):
            response = ib_NIOS.wapi_request('GET',object_type="record:host_ipv6addr",params="?_return_fields=configure_for_dhcp,ipv6addr")
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
	    if (response[1]=='"configure_for_dhcp":true' and response[2]=='"ipv6addr":"1231::1"' and response[4]=='"configure_for_dhcp":true' and response[5]=='"ipv6addr":"1234::1"' and response[7]=='"configure_for_dhcp":true' and response[8]=='"ipv6addr":"1234::3"' and response[10]=='"configure_for_dhcp":false' and response[11]=='"ipv6addr":"1234::5"' and response[13]=='"configure_for_dhcp":true' and response[14]=='"ipv6addr":"1234::7"' and response[16]=='"configure_for_dhcp":true' and response[17]=='"ipv6addr":"1231::1"' and response[19]=='"configure_for_dhcp":true' and response[20]=='"ipv6addr":"1234::1"' and response[22]=='"configure_for_dhcp":true' and response[23]=='"ipv6addr":"1234::3"'and response[25]=='"configure_for_dhcp":false' and response[26]=='"ipv6addr":"1234::5"' and response[28]=='"configure_for_dhcp":true' and response[29]=='"ipv6addr":"1234::7"'):
		    assert True
            else:
                    assert False
            logging.info("Network_HOST_records_using_configure_for_dhcp_ipv6")

	@pytest.mark.run(order=20)
        def test_120_get_host_records_using_filter(self):
            response = ib_NIOS.wapi_request('GET',object_type="record:host?ipv4addr>=10.0.0.4")
            response=response.replace('\n','').replace(' ','').replace('}','').replace(']','').replace('[','').replace('{','')
            response=response.split(',')
            logging.info(response)
            if ((response[6]=='"name":"host5.zone.com"' and response[7]=='"view":"default"') and (response[14]=='"name":"host7.zone.com"' and response[15]=='"view":"default"') and (response[22]=='"name":"host5.zone.com"' and response[23]=='"view":"default.net_view1"') and (response[30]=='"name":"host7.zone.com"' and response[31]=='"view":"default.net_view1"')):
                    assert True
            else:
                    assert False
            logging.info("Network_HOST_records using filter ipv4addr>=10.0.0.4")



	@pytest.mark.run(order=21)
        def test_121_get_host_records_with_extattr(self):
            response = ib_NIOS.wapi_request('GET',object_type="record:host?_return_fields=extattrs")
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
            if ((response[1]=='"extattrs":"Site":"value":"100"') and (response[3]=='"extattrs":"Site":"value":"100"') and (response[5]=='"extattrs":"Site":"value":"100"') and (response[7]=='"extattrs":"Site":"value":"500"') and (response[9]=='"extattrs":') and (response[11]=='"extattrs":"Site":"value":"100"') and (response[13]=='"extattrs":"Site":"value":"100"') and (response[15]=='"extattrs":"Site":"value":"100"') and (response[17]=='"extattrs":"Site":"value":"500"') and (response[19]=='"extattrs":') and (response[21]=='"extattrs":"Site":"value":"100"') and (response[23]=='"extattrs":"Site":"value":"100"') and (response[25]=='"extattrs":"Site":"value":"100"') and (response[27]=='"extattrs":') and (response[29]=='"extattrs":"Site":"value":"700"') and (response[31]=='"extattrs":"Site":"value":"100"')):
                    assert True
            else:
                    assert False
            logging.info("Display IPv4 and IPv6 network_HOST_records with extensible attributes")

	@pytest.mark.run(order=22)
        def test_122_get_invalid_host_records(self):
            logging.info("Negative: Display network_HOST_records that are not present")
            response = ib_NIOS.wapi_request('GET',object_type="search?address=11.0.0.1")
            logging.info(response)
            if (response=='[]'):
                    assert True
            else:
                    assert False
            
	@pytest.mark.run(order=23)
        def test_123_get_invalid_host_records_ipv6(self):
            logging.info("Negative: Display IPv6 network_HOST_records that are not present")
            response = ib_NIOS.wapi_request('GET',object_type="search?address=2606::1")
            logging.info(response)
            if (response=='[]'):
                    assert True
            else:
                    assert False

	@pytest.mark.run(order=24)
        def test_124_get_host_records_using_search(self):
            logging.info("Display network_HOST_records with the IP 10.0.0.3")
            response = ib_NIOS.wapi_request('GET',object_type="search?address=10.0.0.3")
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response) 
            if ((response[4]=='"ipv4addr":"10.0.0.3"') and (response[6]=='"name":"host3.zone.com"') and (response[15]=='"ipv4addr":"10.0.0.3"') and (response[17]=='"name":"host3.zone.com"')):
                    assert True
            else:
                    assert False
   
	@pytest.mark.run(order=25)
        def test_125_get_host_records_using_search(self):
            logging.info("Display network_HOST_records with IPs <= 10.0.0.3 and with comments")
            response = ib_NIOS.wapi_request('GET',object_type="ipv4address?network=10.0.0.0&ip_address<=10.0.0.2&_return_fields=comment&_max_results=100")
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
            response=response.split(',')
            logging.info(response)
            if ((response[1]=='"comment":""') and (response[3]=='"comment":"host1"') and (response[5]=='"comment":""')):
                    assert True
            else:
                    assert False
   
	@pytest.mark.run(order=26)
        def test_126_get_host_records_using_search_string(self):
            logging.info("Display network_HOST_records using search string 100")
            response = ib_NIOS.wapi_request('GET',object_type="search?search_string=100")
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
            response=response.split(',')
            logging.info(response)
            if ((response[9]=='"name":"host01.zone.com"') and (response[10]=='"view":"default.net_view1"') and (response[17]=='"name":"host1.zone.com"') and (response[18]=='"view":"default.net_view1"') and (response[25]=='"name":"host11.zone.com"') and (response[26]=='"view":"default.net_view1"') and (response[33]=='"name":"host13.zone.com"') and (response[34]=='"view":"default.net_view1"') and (response[65]=='"name":"host01.zone.com"') and (response[66]=='"view":"default"') and (response[73]=='"name":"host1.zone.com"') and (response[74]=='"view":"default"')):
                    assert True
            else:
                    assert False

	@pytest.mark.run(order=27)
        def test_127_get_v6_host_records_using_filter(self):
            logging.info("Display IPv6 network_HOST_records using filter ipv6addr>=1234:4")
            response = ib_NIOS.wapi_request('GET',object_type="record:host?ipv6addr>=1234::4")
            response=response.replace('\n','').replace(' ','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
            if ((response[6]=='"name":"host15.zone.com"' and response[7]=='"view":"default"') and (response[14]=='"name":"host17.zone.com"' and response[15]=='"view":"default"') and (response[22]=='"name":"host15.zone.com"' and response[23]=='"view":"default.net_view1"') and (response[30]=='"name":"host17.zone.com"' and response[31]=='"view":"default.net_view1"')):
                    assert True
            else:
                    assert False
          
        @pytest.mark.run(order=28)
        def test_128_get_v6_host_records_using_search(self):
            logging.info("Display IPv6 network_HOST_records with the IP 1234::3")
            response = ib_NIOS.wapi_request('GET',object_type="search?address=1234::3")
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
            if ((response[6]=='"name":"host13.zone.com"') and (response[7]=='"view":"default"') and (response[17]=='"name":"host13.zone.com"') and (response[18]=='"view":"default.net_view1"')):
                    assert True
            else:
                    assert False

        @pytest.mark.run(order=29)
        def test_129_get_host_records_using_search(self):
            logging.info("Display network_HOST_records with IPs <= 1234::3 and with comments")
            response = ib_NIOS.wapi_request('GET',object_type="ipv6address?network=1234::&ip_address<=1234::3&_return_fields=comment&_max_results=100")
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
            response=response.split(',')
            logging.info(response)
            if ((response[1]=='"comment":"host11"') and (response[3]=='"comment":"host13"')):
                     assert True
            else:
                     assert False
  
	@pytest.mark.run(order=30)
        def test_130_creating_non_super_user(self):

            try:
                group1={"name":"non","superuser":False}
                get_ref_group1 = ib_NIOS.wapi_request('POST',object_type="admingroup", fields=json.dumps(group1))
                logging.info(get_ref_group1)
                res_group1 = json.loads(get_ref_group1)
            except Exception as error:
                logging.info ("abcd {}".format(error))

            try:
                user1={"name":"non","password":"infoblox","admin_groups":["non"]}
                get_ref1 = ib_NIOS.wapi_request('POST',object_type="adminuser", fields=json.dumps(user1))
                logging.info(get_ref1)
                res1 = json.loads(get_ref1)
                logging.info (res1)
            except Exception as error:
                logging.info ("abcd {}".format(error))
	
	@pytest.mark.run(order=32)
	def test_132_enable_API_to_admingroups(self):
            logging.info("To Get reference for admingroups")
            get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup")
            logging.info(get_ref)
            res = json.loads(get_ref)
            ref1 = json.loads(get_ref)[4]['_ref']
            data1={"name": "non","access_method":["GUI","API"]}
            response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data1), grid_vip=config.grid_vip)
	
        @pytest.mark.run(order=33)
        def test_133_get_network_HOST_records_for_network(self):
            logging.info("display network_HOST_records_for_10.0.0.0/16_network")
            response = ib_NIOS.wapi_request('GET',object_type="record:host?network=10.0.0.0/16",user='non',password='infoblox')
            logging.info(response)
	    if (response=='[]'):
                    assert True
            else:
                    assert False
	
        @pytest.mark.run(order=34)
        def test_134_enable_API_to_admingroup(self):
	    data = {"group":"non","resource_type":"HOST","permission":"WRITE"}
	    response = ib_NIOS.wapi_request('POST',object_type="permission",fields=json.dumps(data))
	    logging.info(response)
            data = {"group":"non","resource_type":"NETWORK","permission":"WRITE"}
            response = ib_NIOS.wapi_request('POST',object_type="permission",fields=json.dumps(data))
            logging.info(response)
            data = {"group":"non","resource_type":"IPV6_NETWORK","permission":"WRITE"}
            response = ib_NIOS.wapi_request('POST',object_type="permission",fields=json.dumps(data))
            logging.info(response)

	@pytest.mark.run(order=35)
        def test_135_get_network_HOST_records_for_network(self):
            logging.info("display network_HOST_records_for_10.0.0.0/16_network")
	    response = ib_NIOS.wapi_request('GET',object_type="record:host?network=10.0.0.0/16",user='non',password='infoblox')
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
            if ((response[4]!='"ipv4addr":"9.0.0.1"' and response[4]=='"ipv4addr":"10.0.0.1"') and response[7]=='"view":"default"' and response[12]=='"ipv4addr":"10.0.0.3"' and response[15]=='"view":"default"'and response[20]=='"ipv4addr":"10.0.0.5"' and response[23]=='"view":"default"' and response[28]=='"ipv4addr":"10.0.0.7"' and response[31]=='"view":"default"' and response[36]=='"ipv4addr":"10.0.0.1"' and response[39]=='"view":"default.net_view1"' and response[44]=='"ipv4addr":"10.0.0.3"' and response[47]=='"view":"default.net_view1"' and response[52]=='"ipv4addr":"10.0.0.5"' and response[55]=='"view":"default.net_view1"' and response[60]=='"ipv4addr":"10.0.0.7"' and response[63]=='"view":"default.net_view1"'):
		    assert True
	    else:
	            assert False
	
	@pytest.mark.run(order=36)
        def test_136_get_network_HOST_records_for_Site_100(self):
            logging.info("display network_HOST_records_for_Site_100")
            response = ib_NIOS.wapi_request('GET',object_type="record:host?*Site=100&network=10.0.0.0/16",user='non',password='infoblox')
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
            if ((response[4]!='"ipv4addr":"9.0.0.1"' and response[4]=='"ipv4addr":"10.0.0.1"') and response[3]=='"host":"host1.zone.com"' and response[7]=='"view":"default"' and response[11]=='"host":"host3.zone.com"' and response[12]=='"ipv4addr":"10.0.0.3"' and response[15]=='"view":"default"' and response[19]=='"host":"host1.zone.com"' and response[20]=='"ipv4addr":"10.0.0.1"' and response[23]=='"view":"default.net_view1"' and response[27]=='"host":"host3.zone.com"' and response[28]=='"ipv4addr":"10.0.0.3"' and response[31]=='"view":"default.net_view1"'):

                    assert True
            else:
                    assert False

        @pytest.mark.run(order=37)
        def test_137_get_network_HOST_records_using_host_name(self):
            logging.info("display network_HOST_records_using_host_name")
            response = ib_NIOS.wapi_request('GET',object_type="record:host",params="?name=host3.zone.com&_return_fields=ipv4addrs",user='non',password='infoblox')
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
            if (response[3]=='"host":"host3.zone.com"' and response[4]=='"ipv4addr":"10.0.0.3"' and response[9]=='"host":"host3.zone.com"' and response[10]=='"ipv4addr":"10.0.0.3"'):

                    assert True
	    else:
                    assert False

        @pytest.mark.run(order=38)
        def test_138_get_network_HOST_records_using_Site_host_name(self):
            logging.info("display network_HOST_records_using_Site_host_name")
            response = ib_NIOS.wapi_request('GET',object_type="record:host",params="?*Site=100&name=host1.zone.com",user='non',password='infoblox')
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
            if ((response[4]!='"ipv4addr":"9.0.0.1"' and response[4]=='"ipv4addr":"10.0.0.1"') and response[3]=='"host":"host1.zone.com"' and response[7]=='"view":"default"' and response[11]=='"host":"host1.zone.com"' and response[12]=='"ipv4addr":"10.0.0.1"' and response[15]=='"view":"default.net_view1"'):

                    assert True
            else:
                    assert False

	@pytest.mark.run(order=39)
        def test_139_get_network_HOST_records_using_host_name(self):
            logging.info("display network_HOST_records_using_host_name")
            response = ib_NIOS.wapi_request('GET',object_type="record:host?name=host1.zone.com",user='non',password='infoblox')
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
            if ((response[4]!='"ipv4addr":"9.0.0.1"' and response[4]=='"ipv4addr":"10.0.0.1"') and response[3]=='"host":"host1.zone.com"' and response[7]=='"view":"default.net_view1"' and response[11]=='"host":"host1.zone.com"' and response[12]=='"ipv4addr":"10.0.0.1"' and response[15]=='"view":"default"'):
                    assert True
            else:
                    assert False
           
        @pytest.mark.run(order=40)
        def test_140_get_network_HOST_records_using_Site_comment(self):
            logging.info("display network_HOST_records_using_Site_comment")
            response = ib_NIOS.wapi_request('GET',object_type="record:host",params="?*Site=100&comment~=host1&network=10.0.0.0/16",user='non',password='infoblox')
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
            if ((response[3]!='"host":"host9.zone.com"' and response[3]=='"host":"host1.zone.com"') and response[4]=='"ipv4addr":"10.0.0.1"' and response[7]=='"view":"default"' and response[11]=='"host":"host1.zone.com"' and response[12]=='"ipv4addr":"10.0.0.1"' and response[15]=='"view":"default.net_view1"'):
                    assert True
            else:
                    assert False

	@pytest.mark.run(order=41)
        def test_141_get_network_HOST_records_for_ipv6_network(self):
            logging.info("display network_HOST_records_for_1234::/64_network")
            response = ib_NIOS.wapi_request('GET',object_type="record:host?network=1234::/64",user='non',password='infoblox')
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
            if((response[5]!='"ipv6addr":"1231::1"' and response[5]=='"ipv6addr":"1234::1"') and response[4]=='"host":"host11.zone.com"' and response[7]=='"view":"default"' and response[12]=='"host":"host13.zone.com"' and response[13]=='"ipv6addr":"1234::3"' and response[15]=='"view":"default"' and response[20]=='"host":"host15.zone.com"' and response[21]=='"ipv6addr":"1234::5"' and response[23]=='"view":"default"' and response[28]=='"host":"host17.zone.com"' and response[29]=='"ipv6addr":"1234::7"' and response[31]=='"view":"default"' and response[36]=='"host":"host11.zone.com"' and response[37]=='"ipv6addr":"1234::1"'and response[39]=='"view":"default.net_view1"' and response[44]=='"host":"host13.zone.com"' and response[45]=='"ipv6addr":"1234::3"' and response[47]=='"view":"default.net_view1"' and response[52]=='"host":"host15.zone.com"' and response[53]=='"ipv6addr":"1234::5"' and response[55]=='"view":"default.net_view1"' and response[60]=='"host":"host17.zone.com"' and response[61]=='"ipv6addr":"1234::7"' and response[63]=='"view":"default.net_view1"'):
                    assert True
            else:
                    assert False

        @pytest.mark.run(order=42)
        def test_142_get_network_HOST_records_for_network_Site(self):
            logging.info("display network_HOST_records_for_1234::/64_network_Site")
            response = ib_NIOS.wapi_request('GET',object_type="record:host?*Site=100&network=1234::/64",user='non',password='infoblox')
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
	    if((response[5]!='"ipv6addr":"1231::1"' and response[5]=='"ipv6addr":"1234::1"') and response[4]=='"host":"host11.zone.com"' and response[7]=='"view":"default"' and response[12]=='"host":"host13.zone.com"' and response[13]=='"ipv6addr":"1234::3"' and response[15]=='"view":"default"' and response[20]=='"host":"host11.zone.com"' and response[21]=='"ipv6addr":"1234::1"'and response[23]=='"view":"default.net_view1"' and response[28]=='"host":"host13.zone.com"' and response[29]=='"ipv6addr":"1234::3"' and response[31]=='"view":"default.net_view1"'):
                    assert True
            else:
                    assert False

        @pytest.mark.run(order=43)
        def test_143_get_network_HOST_records_using_host_name(self):
            logging.info("display network_HOST_records_using_host_name")
            response = ib_NIOS.wapi_request('GET',object_type="record:host",params="?name=host15.zone.com&_return_fields=ipv6addrs",user='non',password='infoblox')
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
            if ((response[5]!='"ipv6addr":"1234::1"' and response[5]=='"ipv6addr":"1234::5"') and response[4]=='"host":"host15.zone.com"' and response[10]=='"host":"host15.zone.com"' and response[11]=='"ipv6addr":"1234::5"'):
                    assert True
            else:
                    assert False
           
        @pytest.mark.run(order=44)
        def test_144_get_network_HOST_records_using_Site_host_name_Site(self):
            logging.info("display network_HOST_records_using_Site_host_name_Site")
            response = ib_NIOS.wapi_request('GET',object_type="record:host",params="?*Site=100&name=host13.zone.com",user='non',password='infoblox')
            print(response)
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
	    logging.info(response)
            if((response[5]!='"ipv6addr":"1234::1"' and response[5]=='"ipv6addr":"1234::3"') and response[4]=='"host":"host13.zone.com"' and response[7]=='"view":"default"' and response[12]=='"host":"host13.zone.com"' and response[13]=='"ipv6addr":"1234::3"' and response[15]=='"view":"default.net_view1"'):
                    assert True
            else:
                    assert False
            
        @pytest.mark.run(order=45)
        def test_145_get_network_HOST_records_using_Site_host_name(self):
            logging.info("display network_HOST_records_using_Site_host_name")
            response = ib_NIOS.wapi_request('GET',object_type="record:host?name=host13.zone.com",user='non',password='infoblox')
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
            if((response[5]!='"ipv6addr":"1234::1"' and response[5]=='"ipv6addr":"1234::3"') and response[4]=='"host":"host13.zone.com"' and response[7]=='"view":"default.net_view1"' and response[12]=='"host":"host13.zone.com"' and response[13]=='"ipv6addr":"1234::3"' and response[15]=='"view":"default"'):
                    assert True
            else:
                    assert False
          
	@pytest.mark.run(order=46)
        def test_146_get_network_HOST_records_using_Site_comment(self):
            logging.info("display network_HOST_records_using_Site_comment")
            response = ib_NIOS.wapi_request('GET',object_type="record:host",params="?*Site=100&comment~=host13",user='non',password='infoblox')
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
            if((response[5]!='"ipv6addr":"1234::1"' and response[5]=='"ipv6addr":"1234::3"') and response[4]=='"host":"host13.zone.com"' and response[7]=='"view":"default"' and response[12]=='"host":"host13.zone.com"' and response[13]=='"ipv6addr":"1234::3"' and response[15]=='"view":"default.net_view1"'):
                    assert True
            else:
                    assert False
     
        @pytest.mark.run(order=47)
        def test_147_get_network_HOST_records_using_configure_for_dhcp(self):
            logging.info("display network_HOST_records_using_configure_for_dhcp")
            response = ib_NIOS.wapi_request('GET',object_type="record:host_ipv4addr",params="?_return_fields=configure_for_dhcp,ipv4addr",user='non',password='infoblox')
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
            if (response[1]=='"configure_for_dhcp":true' and response[2]=='"ipv4addr":"9.0.0.1"' and response[4]=='"configure_for_dhcp":true' and response[5]=='"ipv4addr":"10.0.0.1"' and response[7]=='"configure_for_dhcp":true' and response[8]=='"ipv4addr":"10.0.0.3"' and response[10]=='"configure_for_dhcp":true' and response[11]=='"ipv4addr":"10.0.0.5"' and response[13]=='"configure_for_dhcp":false' and response[14]=='"ipv4addr":"10.0.0.7"' and response[16]=='"configure_for_dhcp":true' and response[17]=='"ipv4addr":"9.0.0.1"' and response[19]=='"configure_for_dhcp":true' and response[20]=='"ipv4addr":"10.0.0.1"' and response[22]=='"configure_for_dhcp":true' and response[23]=='"ipv4addr":"10.0.0.3"' and response[25]=='"configure_for_dhcp":true' and response[26]=='"ipv4addr":"10.0.0.5"' and response[28]=='"configure_for_dhcp":false' and response[29]=='"ipv4addr":"10.0.0.7"'):
	            assert True
            else:
                    assert False

        @pytest.mark.run(order=48)
        def test_148_get_network_HOST_records_using_configure_for_dhcp(self):
            logging.info("display network_HOST_records_using_configure_for_dhcp")
            response = ib_NIOS.wapi_request('GET',object_type="record:host_ipv6addr",params="?_return_fields=configure_for_dhcp,ipv6addr",user='non',password='infoblox')
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
            if (response[1]=='"configure_for_dhcp":true' and response[2]=='"ipv6addr":"1231::1"' and response[4]=='"configure_for_dhcp":true' and response[5]=='"ipv6addr":"1234::1"' and response[7]=='"configure_for_dhcp":true' and response[8]=='"ipv6addr":"1234::3"' and response[10]=='"configure_for_dhcp":false' and response[11]=='"ipv6addr":"1234::5"' and response[13]=='"configure_for_dhcp":true' and response[14]=='"ipv6addr":"1234::7"' and response[16]=='"configure_for_dhcp":true' and response[17]=='"ipv6addr":"1231::1"' and response[19]=='"configure_for_dhcp":true' and response[20]=='"ipv6addr":"1234::1"' and response[22]=='"configure_for_dhcp":true' and response[23]=='"ipv6addr":"1234::3"'and response[25]=='"configure_for_dhcp":false' and response[26]=='"ipv6addr":"1234::5"' and response[28]=='"configure_for_dhcp":true' and response[29]=='"ipv6addr":"1234::7"'):
                    assert True
            else:
                    assert False
           
	@pytest.mark.run(order=49)
        def test_149_get_host_records_using_filter(self):
            logging.info("Display network_HOST_records using filter ipv4addr>=10.0.0.4")
            response = ib_NIOS.wapi_request('GET',user='non',password='infoblox',object_type="record:host?ipv4addr>=10.0.0.4")
            response=response.replace('\n','').replace(' ','').replace('}','').replace(']','').replace('[','').replace('{','')
            response=response.split(',')
            logging.info(response)
            if ((response[6]=='"name":"host5.zone.com"' and response[7]=='"view":"default"') and (response[14]=='"name":"host7.zone.com"' and response[15]=='"view":"default"') and (response[22]=='"name":"host5.zone.com"' and response[23]=='"view":"default.net_view1"') and (response[30]=='"name":"host7.zone.com"' and response[31]=='"view":"default.net_view1"')):
                    assert True
            else:
                    assert False

	@pytest.mark.run(order=50)
        def test_150_get_host_records_with_extattr(self):
            logging.info("Display IPv4 and IPv6 network_HOST_records with extensible attributes")
            response = ib_NIOS.wapi_request('GET',user='non',password='infoblox',object_type="record:host?_return_fields=extattrs")
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
            if ((response[1]=='"extattrs":"Site":"value":"100"') and (response[3]=='"extattrs":"Site":"value":"100"') and (response[5]=='"extattrs":"Site":"value":"100"') and (response[7]=='"extattrs":"Site":"value":"500"') and (response[9]=='"extattrs":') and (response[11]=='"extattrs":"Site":"value":"100"') and (response[13]=='"extattrs":"Site":"value":"100"') and (response[15]=='"extattrs":"Site":"value":"100"') and (response[17]=='"extattrs":"Site":"value":"500"') and (response[19]=='"extattrs":') and (response[21]=='"extattrs":"Site":"value":"100"') and (response[23]=='"extattrs":"Site":"value":"100"') and (response[25]=='"extattrs":"Site":"value":"100"') and (response[27]=='"extattrs":') and (response[29]=='"extattrs":"Site":"value":"700"') and (response[31]=='"extattrs":"Site":"value":"100"')):
                    assert True
            else:
                    assert False
           
	@pytest.mark.run(order=51)
        def test_151_get_invalid_host_records(self):
            logging.info("Negative: Display network_HOST_records that are not present")
            response = ib_NIOS.wapi_request('GET',user='non',password='infoblox',object_type="search?address=11.0.0.1")
            logging.info(response)
            if (response=='[]'):
                    assert True
            else:
                    assert False

	@pytest.mark.run(order=52)
        def test_152_get_invalid_host_records_ipv6(self):
            logging.info("Negative: Display IPv6 network_HOST_records that are not present")
            response = ib_NIOS.wapi_request('GET',user='non',password='infoblox',object_type="search?address=2606::1")
            logging.info(response)
            if (response=='[]'):
                    assert True
            else:
                    assert False

	@pytest.mark.run(order=53)
        def test_153_get_host_records_using_search(self):
            logging.info("Display network_HOST_records with the IP 10.0.0.3")
            response = ib_NIOS.wapi_request('GET',user='non',password='infoblox',object_type="search?address=10.0.0.3")
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
            if ((response[4]=='"ipv4addr":"10.0.0.3"') and (response[6]=='"name":"host3.zone.com"') and (response[15]=='"ipv4addr":"10.0.0.3"') and (response[17]=='"name":"host3.zone.com"')):
                    assert True
            else:
                    assert False
        
	@pytest.mark.run(order=54)
        def test_154_get_host_records_using_search(self):
            logging.info("Display network_HOST_records with IPs <= 10.0.0.3 and with comments")
            response = ib_NIOS.wapi_request('GET',user='non',password='infoblox',object_type="ipv4address?network=10.0.0.0&ip_address<=10.0.0.2&_return_fields=comment&_max_results=100")
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
            response=response.split(',')
            logging.info(response)
            if ((response[1]=='"comment":""') and (response[3]=='"comment":"host1"') and (response[5]=='"comment":""')):
                    assert True
            else:
                    assert False

	@pytest.mark.run(order=55)
        def test_155_get_host_records_using_search_string(self):
            logging.info("Display network_HOST_records using search string 100")
            response = ib_NIOS.wapi_request('GET',user='non',password='infoblox',object_type="search?search_string=100")
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
            response=response.split(',')
            logging.info(response)
            if ((response[6]=='"name":"host01.zone.com"') and (response[7]=='"view":"default.net_view1"') and (response[14]=='"name":"host1.zone.com"') and (response[15]=='"view":"default.net_view1"') and (response[22]=='"name":"host11.zone.com"') and (response[23]=='"view":"default.net_view1"') and (response[30]=='"name":"host13.zone.com"') and (response[31]=='"view":"default.net_view1"') and (response[62]=='"name":"host01.zone.com"') and (response[63]=='"view":"default"') and (response[70]=='"name":"host1.zone.com"') and (response[71]=='"view":"default"')):
                    assert True
            else:
                    assert False
            
	@pytest.mark.run(order=56)
        def test_156_get_v6_host_records_using_filter(self):
            logging.info("Display IPv6 network_HOST_records using filter ipv6addr>=1234:4")
            response = ib_NIOS.wapi_request('GET',user='non',password='infoblox',object_type="record:host?ipv6addr>=1234::4")
            response=response.replace('\n','').replace(' ','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
            if ((response[6]=='"name":"host15.zone.com"' and response[7]=='"view":"default"') and (response[14]=='"name":"host17.zone.com"' and response[15]=='"view":"default"') and (response[22]=='"name":"host15.zone.com"' and response[23]=='"view":"default.net_view1"') and (response[30]=='"name":"host17.zone.com"' and response[31]=='"view":"default.net_view1"')):
                    assert True
            else:
                    assert False
          
        @pytest.mark.run(order=57)
        def test_157_get_v6_host_records_using_search(self):
            logging.info("Display IPv6 network_HOST_records with the IP 1234::3")
            response = ib_NIOS.wapi_request('GET',user='non',password='infoblox',object_type="search?address=1234::3")
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
            if ((response[6]=='"name":"host13.zone.com"') and (response[7]=='"view":"default"') and (response[17]=='"name":"host13.zone.com"') and (response[18]=='"view":"default.net_view1"')):
                    assert True
            else:
                    assert False
           
        @pytest.mark.run(order=58)
        def test_158_get_host_records_using_search(self):
            logging.info("Display network_HOST_records with IPs <= 1234::3 and with comments")
            response = ib_NIOS.wapi_request('GET',user='non',password='infoblox',object_type="ipv6address?network=1234::&ip_address<=1234::3&_return_fields=comment&_max_results=100")
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','').replace('[','')
            response=response.split(',')
            logging.info(response)
            if ((response[1]=='"comment":"host11"') and (response[3]=='"comment":"host13"')):
                     assert True
            else:
                     assert False
         
        @pytest.mark.run(order=59)
        def test_159_get_network_HOST_records_using_configure_for_dhcp(self):
            logging.info("display network_HOST_records_using_configure_for_dhcp")
            response = ib_NIOS.wapi_request('GET',object_type="search?mac_address=11:11:11:11:11:15")
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
            if(response[5]=='"mac":"11:11:11:11:11:15"' and response[7]== '"view":"default"' and  response[13]=='"mac":"11:11:11:11:11:15"' and response[15]=='"view":"default.net_view1"'):
                    assert True
            else:
                    assert False
          
        @pytest.mark.run(order=60)
        def test_160_get_network_HOST_records_using_configure_for_dhcp(self):
            logging.info("display network_HOST_records_using_configure_for_dhcp")
            response = ib_NIOS.wapi_request('GET',object_type="search?mac_address=11:11:11:11:11:15",user='non',password='infoblox')
            response=response.replace('\n','').replace(' ','').replace('{','').replace('}','').replace(']','')
            response=response.split(',')
            logging.info(response)
            if(response[5]=='"mac":"11:11:11:11:11:15"' and response[7]== '"view":"default"' and  response[13]=='"mac":"11:11:11:11:11:15"' and response[15]=='"view":"default.net_view1"'):
                    assert True
            else:
                    assert False

	@pytest.mark.run(order=61)
        def test_161_get_host_records_using_filter(self):
            print("Display network_HOST_records using filter ipv4addr<=10.0.0.4")
            response = ib_NIOS.wapi_request('GET',object_type="record:host?ipv4addr<=10.0.0.4")
            print(response)
            response=response.replace('\n','').replace(' ','').replace('}','').replace(']','').replace('[','').replace('{','')
            response=response.split(',')
            print ("################################",(response))
            print(type(response))
            print (response[6],response[7],response[14],response[15],response[22],response[23],response[30],response[31])
            if ((response[6]=='"name":"host1.zone.com"' and response[7]=='"view":"default"') and (response[14]=='"name":"host3.zone.com"' and response[15]=='"view":"default"') and (response[22]=='"name":"host1.zone.com"' and response[23]=='"view":"default.net_view1"') and (response[30]=='"name":"host3.zone.com"' and response[31]=='"view":"default.net_view1"')):
                assert True
            else:
                assert False
            print("completed")


        @pytest.mark.run(order=62)
        def test_162_get_v6_host_records_using_filter(self):
            print("Display IPv6 network_HOST_records using filter ipv6addr<=1234:4")
            response = ib_NIOS.wapi_request('GET',user='non',password='infoblox',object_type="record:host?ipv6addr<=1234::4")
            print(response)
            response=response.replace('\n','').replace(' ','').replace('}','').replace(']','')
            response=response.split(',')
            print ("################################",(response))
            print(type(response))
            print (response[6],response[7],response[14],response[15],response[22],response[23],response[30],response[31],response[38],response[39],response[46],response[47])
            if ((response[6]=='"name":"host01.zone.com"' and response[7]=='"view":"default"') and (response[14]=='"name":"host11.zone.com"' and response[15]=='"view":"default"') and (response[22]=='"name":"host13.zone.com"' and response[23]=='"view":"default"') and (response[30]=='"name":"host01.zone.com"' and response[31]=='"view":"default.net_view1"') and (response[38]=='"name":"host11.zone.com"' and response[39]=='"view":"default.net_view1"') and (response[46]=='"name":"host13.zone.com"' and response[47]=='"view":"default.net_view1"')):
                assert True
            else:
                assert False
            print("completed")
      
	@pytest.mark.run(order=63)
        def test_163_Create_IPV4_network_additional_hosts(self):
                data ={"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "10.0.0.16","mac": "11:11:11:11:11:16"}], "name": "host16.zone.com","view": "default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Host record created for the zone zone.com and network 10.0.0.0/8")

                data ={"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "10.0.0.99","mac": "11:11:11:11:10:99"}], "name": "host99.zone.com","view": "default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Host record created for the zone zone.com and network 10.0.0.0/16")

                data ={"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "10.0.0.199","mac": "11:11:11:11:11:99"}], "name": "host199.zone.com","view": "default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Host record created for the zone zone.com and network 10.0.0.0/16")

                data ={"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "10.0.0.254","mac": "11:11:11:11:12:54"}], "name": "host254.zone.com","view": "default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Host record created for the zone zone.com and network 10.0.0.0/16")

		data ={"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "10.0.0.16","mac": "11:11:11:11:11:16"}], "name": "host16.zone.com","view": "default.net_view1"}
                response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Host record created for the zone zone.com and network 10.0.0.0/8")

                data ={"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "10.0.0.99","mac": "11:11:11:11:10:99"}], "name": "host99.zone.com","view": "default.net_view1"}
                response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Host record created for the zone zone.com and network 10.0.0.0/16")

                data ={"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "10.0.0.199","mac": "11:11:11:11:11:99"}], "name": "host199.zone.com","view": "default.net_view1"}
                response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Host record created for the zone zone.com and network 10.0.0.0/16")

                data ={"ipv4addrs": [{"configure_for_dhcp": True,"ipv4addr": "10.0.0.254","mac": "11:11:11:11:12:54"}], "name": "host254.zone.com","view": "default.net_view1"}
                response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Host record created for the zone zone.com and network 10.0.0.0/16")

	@pytest.mark.run(order=64)
        def test_164_get_host_records_using_filter(self):
            response = ib_NIOS.wapi_request('GET',object_type="record:host?ipv4addr>=10.0.0.7")
            response=response.replace('\n','').replace(' ','').replace('}','').replace(']','').replace('[','').replace('{','')
            response=response.split(',')
            logging.info(response)
            if ((response[3]=='"name":"host7.zone.com"' and response[7]=='"view":"default"') and (response[11]=='"name":"host16.zone.com"' and response[15]=='"view":"default"') and (response[19]=='"name":"host99.zone.com"' and response[23]=='"view":"default"') and (response[27]=='"name":"host199.zone.com"' and response[31]=='"view":"default"')and (response[35]=='"name":"host254.zone.com"' and response[39]=='"view":"default"') and (response[43]=='"name":"host7.zone.com"' and response[47]=='"view":"default.net_view1"') and (response[51]=='"name":"host16.zone.com"' and response[55]=='"view":"default.net_view1"') and (response[59]=='"name":"host99.zone.com"' and response[63]=='"view":"default.net_view1"') and (response[67]=='"name":"host199.zone.com"' and response[71]=='"view":"default.net_view1"')and (response[75]=='"name":"host254.zone.com"' and response[79]=='"view":"default.net_view1"')):
                    assert True
            else:
                    assert False
            logging.info("Network_HOST_records using filter ipv4addr>=10.0.0.7")

	@pytest.mark.run(order=65)
        def test_165_get_host_records_using_filter_non_superuser(self):
            response = ib_NIOS.wapi_request('GET',object_type="record:host?ipv4addr>=10.0.0.7",user='non',password='infoblox')
            response=response.replace('\n','').replace(' ','').replace('}','').replace(']','').replace('[','').replace('{','')
            response=response.split(',')
            logging.info(response)
            if ((response[3]=='"name":"host7.zone.com"' and response[7]=='"view":"default"') and (response[11]=='"name":"host16.zone.com"' and response[15]=='"view":"default"') and (response[19]=='"name":"host99.zone.com"' and response[23]=='"view":"default"') and (response[27]=='"name":"host199.zone.com"' and response[31]=='"view":"default"')and (response[35]=='"name":"host254.zone.com"' and response[39]=='"view":"default"') and (response[43]=='"name":"host7.zone.com"' and response[47]=='"view":"default.net_view1"') and (response[51]=='"name":"host16.zone.com"' and response[55]=='"view":"default.net_view1"') and (response[59]=='"name":"host99.zone.com"' and response[63]=='"view":"default.net_view1"') and (response[67]=='"name":"host199.zone.com"' and response[71]=='"view":"default.net_view1"')and (response[75]=='"name":"host254.zone.com"' and response[79]=='"view":"default.net_view1"')):
                    assert True
            else:
                    assert False
            logging.info("Network_HOST_records using filter ipv4addr>=10.0.0.7") 

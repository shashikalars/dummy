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

class RFE_9401(unittest.TestCase):

#Starting DHCP service

	@pytest.mark.run(order=1)
        def test_001_Start_DHCP_IPv4_Service(self):
		logging.info("start the ipv4 DHCP service")
		get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties")
		print(get_ref)
                res = json.loads(get_ref)
                for i in res:
                        print("Enabling DHCP IPV4 service")
                        data = {"enable_dhcp": True}
                        response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
                        print response

                read  = re.search(r'200',response)
                for read in  response:
                        assert True
		sleep(30)
		print("Test Case 1 Execution Completed")

	@pytest.mark.run(order=2)
        def test_002_start_DHCP_IPv6_service(self):
                logging.info("start the ipv6 service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties")
                print(get_ref)
                res = json.loads(get_ref)
		for i in res:
                        print("Enabling DHCP IPV6 service")
                        data = {"enable_dhcpv6_service": True}
                        response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
                        print response

                read  = re.search(r'200',response)
                for read in  response:
                        assert True
		sleep(30)
		print("Test Case 2 Execution Completed")

	@pytest.mark.run(order=3)
        def test_003_Validate_DHCP_service_Enabled_for_both_IPv4_and_IPv6(self):
                logging.info("Validate DHCP Service is enabled for both IPv4 & IPv6")
                res= ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties",params="?_return_fields=enable_dhcp,enable_dhcpv6_service")
                res= str(res)
                output=res.replace(' ','').replace("'",'')
                print(output)
		result = ['"enable_dhcp":true','"enable_dhcpv6_service":true']
		for i in result:
		    if i in output:
                        assert True
            	    else:
                	assert False
          	print(result)
		sleep(30)
                print("Test Case 3 Execution Completed")
	
	@pytest.mark.run(order=4)
        def test_004_Add_IPv6_Option_filter_with_multiple_match_rules_and_option_lists(self):
            logging.info("Add IPv6 Option Filter with multiple match rules and option lists")
            data={"name":"IPv6_option_filter","comment":"vsinha123","expression": "(hardware=01:01:23:45:67:89:ab AND option dhcp6.fqdn!=\"test.com\")","option_list": [{"name": "dhcp6.vendor-class","num":16,"value": "Infoblox","vendor_class": "DHCPv6"},{"name": "dhcp6.fqdn","num": 39,"value": "true","vendor_class": "DHCPv6"},{"name": "dhcp6.name-servers","num":23,"value":"21::1,22::2","vendor_class": "DHCPv6"},{"name": "dhcp6.sip-servers-addresses","num":22,"value":"21::1,22::2","vendor_class": "DHCPv6"},{"name": "dhcp6.sntp-servers","num":31,"value":"21::1,22::2","vendor_class": "DHCPv6"},{"name": "dhcp6.bcms-server-a","num":34,"value":"21::1,22::2","vendor_class": "DHCPv6"},{"name": "dhcp6.bcms-server-d","num":33,"value":"\"test.com\",\"zone.com\"","vendor_class": "DHCPv6"},{"name": "dhcp6.info-refresh-time","num":32,"value":"444444444","vendor_class": "DHCPv6"},{"name": "dhcp6.nisp-domain-name","num":30,"value":"\"test.com\"","vendor_class": "DHCPv6"},{"name": "dhcp6.nis-domain-name","num":29,"value":"\"test.com\"","vendor_class": "DHCPv6"},{"name": "dhcp6.nisp-servers","num":28,"value":"22::2","vendor_class": "DHCPv6"},{"name": "dhcp6.nis-servers","num":27,"value":"22::2","vendor_class": "DHCPv6"},{"name": "dhcp6.domain-search","num":24,"value":"\"test.com\"","vendor_class": "DHCPv6"},{"name": "dhcp6.sip-servers-names","num":21,"value":"\"test.com\"","vendor_class": "DHCPv6"}]}
            response = ib_NIOS.wapi_request('POST', object_type="ipv6filteroption",fields=json.dumps(data))
            res=response
            res = json.loads(res)
            print(res)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    assert False
	    sleep(30)
            print("Test Case 4 Execution Completed")	

	@pytest.mark.run(order=5)
        def test_005_Validate_Addition_of_IPv6_Option_filter(self):
		logging.info("Validate Addition of IPv6 Option filter")
		get_ref = ib_NIOS.wapi_request('GET',object_type="ipv6filteroption",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                output = ib_NIOS.wapi_request('GET',object_type="ipv6filteroption",ref=ref1,params="?_inheritance=True&_return_fields=name,expression,lease_time,option_list",grid_vip=config.grid_vip)
                output=json.loads(output)
		result= {'option_list': [{'vendor_class': 'DHCPv6', 'num': 32, 'name': 'dhcp6.info-refresh-time', 'value': '444444444'}, {'vendor_class': 'DHCPv6', 'num': 21, 'name': 'dhcp6.sip-servers-names', 'value': '"test.com"'}, {'vendor_class': 'DHCPv6', 'num': 24, 'name': 'dhcp6.domain-search', 'value': '"test.com"'}, {'vendor_class': 'DHCPv6', 'num': 16, 'name': 'dhcp6.vendor-class', 'value': 'Infoblox'}, {'vendor_class': 'DHCPv6', 'num': 33, 'name': 'dhcp6.bcms-server-d', 'value': '"test.com","zone.com"'}, {'vendor_class': 'DHCPv6', 'num': 29, 'name': 'dhcp6.nis-domain-name', 'value': '"test.com"'}, {'vendor_class': 'DHCPv6', 'num': 27, 'name': 'dhcp6.nis-servers', 'value': '22::2'}, {'vendor_class': 'DHCPv6', 'num': 23, 'name': 'dhcp6.name-servers', 'value': '21::1,22::2'}, {'vendor_class': 'DHCPv6', 'num': 30, 'name': 'dhcp6.nisp-domain-name', 'value': '"test.com"'}, {'vendor_class': 'DHCPv6', 'num': 34, 'name': 'dhcp6.bcms-server-a', 'value': '21::1,22::2'}, {'vendor_class': 'DHCPv6', 'num': 31, 'name': 'dhcp6.sntp-servers', 'value': '21::1,22::2'}, {'vendor_class': 'DHCPv6', 'num': 28, 'name': 'dhcp6.nisp-servers', 'value': '22::2'}, {'vendor_class': 'DHCPv6', 'num': 39, 'name': 'dhcp6.fqdn', 'value': 'true'}, {'vendor_class': 'DHCPv6', 'num': 22, 'name': 'dhcp6.sip-servers-addresses', 'value': '21::1,22::2'}], 'expression': '(hardware=01:01:23:45:67:89:ab AND option dhcp6.fqdn!="test.com")', 'name': 'IPv6_option_filter'}
                for i in result:
                    if output[i] == result[i]:
                        assert True
                    else:
                        assert False
                print(result)
		sleep(30)
		print("Test Case 5 Execution Completed")
	
	@pytest.mark.run(order=6)
        def test_006_Update_IPv6_Option_Filter_modifying_option_list(self):
                logging.info("Update IPv6 Option Filter modifying option list")
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6filteroption")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"option_list": [{"name": "dhcp6.vendor-class","num":16,"value": "Infoblox","vendor_class": "DHCPv6"},{"name": "dhcp6.fqdn","num": 39,"value": "true","vendor_class": "DHCPv6"},{"name": "dhcp6.name-servers","num":23,"value":"21::1,22::2","vendor_class": "DHCPv6"},{"name": "dhcp6.sip-servers-addresses","num":22,"value":"21::1,22::2","vendor_class": "DHCPv6"},{"name": "dhcp6.sntp-servers","num":31,"value":"21::1,22::2","vendor_class": "DHCPv6"},{"name": "dhcp6.bcms-server-a","num":34,"value":"21::1,22::2","vendor_class": "DHCPv6"},{"name": "dhcp6.bcms-server-d","num":33,"value":"\"test.com\",\"zone.com\"","vendor_class": "DHCPv6"},{"name": "dhcp6.info-refresh-time","num":32,"value":"444444444","vendor_class": "DHCPv6"},{"name": "dhcp6.nisp-domain-name","num":30,"value":"\"test.com\"","vendor_class": "DHCPv6"},{"name": "dhcp6.nis-domain-name","num":29,"value":"\"test.com\"","vendor_class": "DHCPv6"},{"name": "dhcp6.nisp-servers","num":28,"value":"22::2","vendor_class": "DHCPv6"},{"name": "dhcp6.nis-servers","num":27,"value":"22::2","vendor_class": "DHCPv6"},{"name": "dhcp6.domain-search","num":24,"value":"\"test.com\"","vendor_class": "DHCPv6"},{"name": "dhcp6.sip-servers-names","num":21,"value":"\"test111.com\"","vendor_class": "DHCPv6"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 6 Execution Completed")
                sleep(30)
	
	@pytest.mark.run(order=7)
        def test_007_Validate_updation_of_IPv6_Option_filter_modifying_option_list(self):
                logging.info("Validate updation of IPv6 Option filter modifying option list")
		get_ref = ib_NIOS.wapi_request('GET',object_type="ipv6filteroption",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="ipv6filteroption",ref=ref1,params="?_inheritance=True&_return_fields=option_list",grid_vip=config.grid_vip)
                output=json.loads(output)
                print(output)
		result= {'option_list': [{'vendor_class': 'DHCPv6', 'num': 32, 'name': 'dhcp6.info-refresh-time', 'value': '444444444'}, {'vendor_class': 'DHCPv6', 'num': 21, 'name': 'dhcp6.sip-servers-names', 'value': '"test111.com"'}, {'vendor_class': 'DHCPv6', 'num': 24, 'name': 'dhcp6.domain-search', 'value': '"test.com"'}, {'vendor_class': 'DHCPv6', 'num': 16, 'name': 'dhcp6.vendor-class', 'value': 'Infoblox'}, {'vendor_class': 'DHCPv6', 'num': 33, 'name': 'dhcp6.bcms-server-d', 'value': '"test.com","zone.com"'}, {'vendor_class': 'DHCPv6', 'num': 29, 'name': 'dhcp6.nis-domain-name', 'value': '"test.com"'}, {'vendor_class': 'DHCPv6', 'num': 27, 'name': 'dhcp6.nis-servers', 'value': '22::2'}, {'vendor_class': 'DHCPv6', 'num': 23, 'name': 'dhcp6.name-servers', 'value': '21::1,22::2'}, {'vendor_class': 'DHCPv6', 'num': 30, 'name': 'dhcp6.nisp-domain-name', 'value': '"test.com"'}, {'vendor_class': 'DHCPv6', 'num': 34, 'name': 'dhcp6.bcms-server-a', 'value': '21::1,22::2'}, {'vendor_class': 'DHCPv6', 'num': 31, 'name': 'dhcp6.sntp-servers', 'value': '21::1,22::2'}, {'vendor_class': 'DHCPv6', 'num': 28, 'name': 'dhcp6.nisp-servers', 'value': '22::2'}, {'vendor_class': 'DHCPv6', 'num': 39, 'name': 'dhcp6.fqdn', 'value': 'true'}, {'vendor_class': 'DHCPv6', 'num': 22, 'name': 'dhcp6.sip-servers-addresses', 'value': '21::1,22::2'}]}
                for i in result:
                    if output[i] == result[i]:
                        assert True
                    else:
                        assert False
                print(result)
		sleep(30)
                print("Test Case 07 Execution Completed")

	@pytest.mark.run(order=8)
        def test_008_Delete_IPv6_Option_Filter(self):
                logging.info("deleting IPv6 OPtion Filter")
		data = {"name":"IPv6_option_filter"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6filteroption",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
		print(ref)
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
                sleep(30)
		print("Test Case 8 Execution Completed")

	@pytest.mark.run(order=9)
        def test_009_Validate_deletion_of_IPv6_Option_filter(self):
                logging.info("Validate deletion of IPv6 Option filter")
                get_temp = ib_NIOS.wapi_request('GET', "ipv6filteroption?name=IPv6_option_filter_9401&_return_fields=expression,name,option_list&_return_as_object=1")
                print(get_temp)
                get_temp = get_temp.replace("\n","").replace(" ","")
                print('my get_temp is',get_temp)
		data=['name=IPv6_option_filter']
                for i in data:
                        if i in get_temp:
                                assert False
                        else:
                                assert True
		sleep(30)
                print("Test Case 9 Execution Completed")

	@pytest.mark.run(order=10)
        def test_010_Add_IPv6_Option_filter_for_functionality_testing(self):
               logging.info("Add IPv6 Option Filter for functionality testing")
               data={"name":"IPv6_option_filter","comment":"vsinha123","lease_time": 20,"expression": "(option dhcp6.fqdn=\"test\")","apply_as_class": True}
               response = ib_NIOS.wapi_request('POST', object_type="ipv6filteroption",fields=json.dumps(data))
               print(response)
               res=response
               res= json.loads(res)
               print(res)
               sleep(100)
               if type(response) == tuple:
                   	if response[0]==400 or response[0]==401:
				assert False
			print("Test Case 10 Execution Completed")

	@pytest.mark.run(order=11)
        def test_011_Validate_addition_of_IPv6_Option_filter(self):
                logging.info("Validate Addition of IPv6 Option filter")
		get_ref = ib_NIOS.wapi_request('GET',object_type="ipv6filteroption",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="ipv6filteroption",ref=ref1,params="?_inheritance=True&_return_fields=name,expression,lease_time",grid_vip=config.grid_vip)
                print(output)
		output=json.loads(output)
                print(output)
		result = {'name':'IPv6_option_filter','expression':'(option dhcp6.fqdn="test")','lease_time': 20}
		for i in result:
    		    if output[i] == result[i]:
        		assert True
    		    else:
        		assert False
                print(result)		
		sleep(100)
                print("Test Case 11 Execution Completed")

	@pytest.mark.run(order=12)
        def test_012_create_IPv6_network(self):
                logging.info("Creatiing an ipv6 network with members assignment")
                global ipv6_network
                ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
                print(ipv6_network)
                ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
                print(ipv6_network)
                data = {"network": ipv6_network+"::/64","network_view": "default","members": [{"ipv4addr":config.grid_vip,"name":config.grid_fqdn}]}
                print(data)
                response = ib_NIOS.wapi_request('POST', object_type="ipv6network", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                sleep(30)
                print("Test Case 12 Execution Completed")

	@pytest.mark.run(order=13)
	def test_013_Validate_added_IPv6_network(self):
		logging.info("validate Creatiing an ipv6 network with members assignment")
		global ipv6_network
		get_ref = ib_NIOS.wapi_request('GET',object_type="ipv6network",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="ipv6network",ref=ref1,params="?_inheritance=True&_return_fields=network",grid_vip=config.grid_vip)
                print(output)
		output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                print("output",output)
        	result = ['network:'+ipv6_network+'::/64']
        	print(result)
		for i in result:
                    if i in output:
                        assert True
                    else:
                        assert False
                print(result)
                sleep(30)
                print("Test Case 13 Execution Completed")

	@pytest.mark.run(order=14)
        def test_014_Update_IPv6_Network_with_IPv6_logic_filter(self):
                logging.info("Update IPv6 network with IPv6 Option Filter")
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6network")
		print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                print("Modify IPv6 Network with IPv6 Option Filter")
                data = {"logic_filter_rules":[{"filter": "IPv6_option_filter","type": "Option"}],"use_logic_filter_rules": True}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 14 Execution Completed")
        	sleep(30)

	@pytest.mark.run(order=15)
        def test_015_Validate_updating_ipv6_DHCP_network_with_IPv6_logic_filter(self):
                logging.info("Validate updating ipv6 DHCP network with IPv6 logic filter")
                get_temp = ib_NIOS.wapi_request('GET', object_type="ipv6network",params="?_inheritance=True&_return_fields=logic_filter_rules,use_logic_filter_rules")
                print(get_temp)
                get_temp = get_temp.replace("\n","").replace(" ","")
		data=['"logic_filter_rules":{"inherited":false,"multisource":false,"source":"","value":[{"filter":"IPv6_option_filter","type":"Option"}]},"use_logic_filter_rules":true']
                print('my get_temp is',get_temp)
                for i in data:
                        if i in get_temp:
                                assert True
                        else:
                                assert False
                sleep(60)
		print("Test Case 15 Execution Completed")

	@pytest.mark.run(order=16)
        def test_016_create_IPv6_range_in_IPv6_network(self):
                logging.info("Create IPv6 range in IPv6 network")
		global ipv6_network
		ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
		print(ipv6_network)
                ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
                print(ipv6_network)
		data ={"address_type":"ADDRESS","network":ipv6_network+"::/64","start_addr":ipv6_network+"::2","end_addr":ipv6_network+"::200","network_view": "default","member":{"_struct":"dhcpmember","ipv4addr":config.grid_vip,"name":config.grid_fqdn}}
                response = ib_NIOS.wapi_request('POST', object_type="ipv6range", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
		sleep(30)
                print("Test Case 16 Execution Completed")

	@pytest.mark.run(order=17)
        def test_017_Validate_adding_ipv6_range_in_IPv6_network(self):
                logging.info("Validate adding IPv6 range in IPv6 network")
		global ipv6_network
                get_ref = ib_NIOS.wapi_request('GET',object_type="ipv6range",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="ipv6range",ref=ref1,params="?_inheritance=True&_return_fields=start_addr,end_addr",grid_vip=config.grid_vip)
                print(output)
                output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                print("output",output)
                result = ['start_addr:'+ipv6_network+'::2','end_addr:'+ipv6_network+'::200']
                print(result)
                for i in result:
                    if i in output:
                        assert True
                    else:
                        assert False
                print(result)
                sleep(100)
                print("Test Case 17 Execution Completed")
	
	@pytest.mark.run(order=18)
	def test_018_Update_IPv6_range_with_IPv6_Option_filter_permission_to_allow_lease(self):
                logging.info("Update IPv6 range with IPv6 Option Filter permission to allow lease")
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6range")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                print("Modify IPv6 range with IPv6 Option Filter")
                data = {"use_logic_filter_rules": True,"logic_filter_rules":[{"filter": "IPv6_option_filter","type": "Option"}],"option_filter_rules":[{"filter": "IPv6_option_filter","permission": "Allow"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                print(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
		sleep(30)
                print("Test Case 18 Execution Completed")

        @pytest.mark.run(order=19)
        def test_019_Validate_updating_ipv6_DHCP_range_IPv6_Option_filter_permission_to_allow_lease(self):
                logging.info("Validate updating ipv6 DHCP range with IPv6 Option Filter permission to allow lease")
		get_temp = ib_NIOS.wapi_request('GET', object_type="ipv6range",params="?_inheritance=True&_return_fields=use_logic_filter_rules,logic_filter_rules,option_filter_rules")
                print(get_temp)
                get_temp = get_temp.replace("\n","").replace(" ","")
                data=['"logic_filter_rules":{"inherited":false,"multisource":false,"source":"","value":[{"filter":"IPv6_option_filter","type":"Option"}]},"option_filter_rules":[{"filter":"IPv6_option_filter","permission":"Allow"}],"use_logic_filter_rules":true}]']
                print('my get_temp is',get_temp)
                for i in data:
                        if i in get_temp:
                                assert True
                        else:
                                assert False
                sleep(100)
                print("Test Case 19 Execution Completed")
                print(data)
		print("Restart DHCP services to reflect changes")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(150)
                print("Service restarted successfully")

	@pytest.mark.run(order=20)
        def test_020_Add_IPv4_NAC_filter_for_functionality_testing(self):
               logging.info("Add IPv4 NAC Filter for functionality testing")
               data={"name":"IPv4_filter_NAC","comment":"vsinha123","lease_time": 20}
               response = ib_NIOS.wapi_request('POST', object_type="filternac",fields=json.dumps(data))
               print(response)
               res=response
               res = json.loads(res)
               print(res)
               if type(response) == tuple:
                        if response[0]==400 or response[0]==401:
                                assert False
                        print("Test Case 20 Execution Completed")

        @pytest.mark.run(order=21)
        def test_021_Validate_addition_of_IPv4_NAC_filter(self):
                logging.info("Validate Addition of IPv4 NAC filter")
                get_temp = ib_NIOS.wapi_request('GET', "filternac?name=IPv4_filter_NAC&_return_fields=name")
                print(get_temp)
                get_temp = get_temp.replace("\n","").replace(" ","")
		data= ['"name":"IPv4_filter_NAC"']
                print('my get_temp is',get_temp)
                for i in data:
                        if i in get_temp:
                                assert True
                        else:
                                assert False
		sleep(30)
                print("Test Case 21 Execution Completed")

	@pytest.mark.run(order=22)
        def test_022_Negartive_Scenario_Update_IPv6_Network_with_IPv4_NAC_filter(self):
                logging.info("Update IPv6 network with IPv6 NAC Filter")
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6network")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                print("Modify IPv6 Network with IPv6 NAC Filter")
		data = {"logic_filter_rules":[{"filter": "IPv4_filter_NAC","type": "NAC"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print('my response is',response)
		data= '"Error": "AdmConDataError: None (IBDataConflictError: IB.Data.Conflict:Cannot associate an IPv4 DHCP option filter with IPv6Network.)", \n  "code": "Client.Ibap.Data.Conflict", \n  "text": "Cannot associate an IPv4 DHCP option filter with IPv6Network."\n'
		if response[0]==400 or response[0]==401:
                                assert True
                print("Test Case 22 Execution Completed")
                sleep(200)

	@pytest.mark.run(order=23)
        def test_023_requesting_ipv6_lease_with_IPv6_option_filter(self):
		global ipv6_network
                print("Perform dras command with correct option")
		ping_cmd= 'ping6 -c 3 '+str(config.grid_vip6)
        	print ping_cmd
        	result_ping= os.system(ping_cmd)
		dras_cmd ='sudo /import/tools/qa/tools/dras6/dras6 -i'+str(config.grid_vip6)+' '+'-n 1 -a 02:02:02:01:01:01 -A -O 39:74657374'
                dras_cmd1 = os.system(dras_cmd)
                sleep(30)
                print("Test Case 23 Execution Completed")

	@pytest.mark.run(order=24)
        def test_024_validate_syslog_with_IP_leased_for_correct_IPv6_option_filter(self):
                logging.info("validate syslog with IP leased for correct IPv6 option filter")
		try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
            		sleep(05)
                        child.sendline('grep -e 02:02:02:01:01:01 /var/log/syslog')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = ['02:02:02:01:01:01']
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
        	print("Test Case 24 Execution Completed")

	@pytest.mark.run(order=25)
        def test_025_Update_IPv6_range_with_IPv6_Option_filter_permission_to_Deny_lease(self):
                logging.info("Update IPv6 range with IPv6 Option Filter permission to deny lease")
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6range")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                print("Modify IPv6 range with IPv6 Option Filter")
                data = {"option_filter_rules":[{"filter": "IPv6_option_filter","permission": "Deny"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
		sleep(30)
                print("Test Case 25 Execution Completed")

	@pytest.mark.run(order=26)
        def test_026_Validate_updating_ipv6_DHCP_range_IPv6_Option_filter_permission_to_deny_lease(self):
                logging.info("Validate updating ipv6 DHCP range with IPv6 Option Filter permission to allow lease")
                get_temp = ib_NIOS.wapi_request('GET', object_type="ipv6range",params="?_inheritance=True&_return_fields=option_filter_rules")
                print(get_temp)
                get_temp = get_temp.replace("\n","").replace(" ","")
                data=['"option_filter_rules":[{"filter":"IPv6_option_filter","permission":"Deny"}]']
                print('my get_temp is',get_temp)
                for i in data:
                        if i in get_temp:
                                assert True
                        else:
                                assert False
                print("Test Case 26 Execution Completed")
                print(data)
                sleep(30)
                print("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(150)
                print("Service restarted successfully")

	@pytest.mark.run(order=27)
        def test_027_requesting_ipv6_lease_with_IPv6_option_filter_permission_to_deny_lease(self):
                logging.info("Perform dras")
		global ipv6_network
                dras_cmd ='sudo /import/tools/qa/tools/dras6/dras6 -i'+str(config.grid_vip6)+' '+'-n 1 -a 02:02:02:02:03:03 -A -O 39:74657374'
                dras_cmd1 = os.system(dras_cmd)
                sleep(30)
                print("Test Case 27 Execution Completed")

	@pytest.mark.run(order=28)
        def test_028_validate_syslog_with_IP_leased_for_Deny_lease(self):
                logging.info("validate syslog with IP leased for Deny lease")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        sleep(05)
                        child.sendline('grep -e 02:02:02:02:03:03 /var/log/syslog')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = ['no permitted ranges with available leases']
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
                print("Test Case 28 Execution Completed")

	@pytest.mark.run(order=29)
        def test_029_create_IPv6_prefix_range_in_IPv6_network(self):
                logging.info("Create IPv6 prefix range in IPv6 network")
                global ipv6_network
                ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
                print(ipv6_network)
                ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
                print(ipv6_network)
                data ={"address_type":"PREFIX","network":ipv6_network+"::/64","ipv6_start_prefix":ipv6_network+"::","ipv6_end_prefix":ipv6_network+"::","ipv6_prefix_bits": 64,"network_view": "default","member":{"_struct":"dhcpmember","ipv6addr":config.grid_vip6,"ipv4addr":config.grid_vip,"name":config.grid_fqdn}}
                response = ib_NIOS.wapi_request('POST', object_type="ipv6range", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
		sleep(30)
                print("Test Case 29 Execution Completed")

        @pytest.mark.run(order=30)
        def test_030_Validate_adding_ipv6_prefix_range_in_IPv6_network(self):
                logging.info("Validate adding IPv6 prefix range in IPv6 network")
                global ipv6_network
                get_ref = ib_NIOS.wapi_request('GET',object_type="ipv6range",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="ipv6range",ref=ref1,params="?_inheritance=True&_return_fields=network,ipv6_end_prefix,ipv6_start_prefix",grid_vip=config.grid_vip)
                print(output)
                output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                print("output",output)
		#ipv6_network = '2001:550:40a:2500'
                result = ['network:'+ipv6_network+'::/64','ipv6_start_prefix:'+ipv6_network+'::','ipv6_end_prefix:'+ipv6_network+'::']
                print(result)
                for i in result:
                    if i in output:
                        assert True
                    else:
                        assert False
                print(result)
                sleep(30)
		print("Test Case 30 Execution Completed")

	@pytest.mark.run(order=31)
        def test_031_Update_IPv6_prefix_range_with_IPv6_Option_filter(self):
                logging.info("Update IPv6 prefix range with IPv6 Option Filter")
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6range")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1

                print("Modify IPv6 prefix range with IPv6 Option Filter")
                data = {"logic_filter_rules":[{"filter": "IPv6_option_filter","type": "Option"}],"option_filter_rules":[{"filter": "IPv6_option_filter","permission": "Allow"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                print(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
		grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(30)
                print("Test Case 31 Execution Completed")

        @pytest.mark.run(order=32)
        def test_032_Validate_updating_ipv6_DHCP_prefix_range(self):
                logging.info("Validate updating ipv6 DHCP prefix range")
		get_ref = ib_NIOS.wapi_request('GET',object_type="ipv6range",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="ipv6range",ref=ref1,params="?_inheritance=True&_return_fields=logic_filter_rules,option_filter_rules",grid_vip=config.grid_vip)
                print(output)
                output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                print("output",output)
                result = ['logic_filter_rules:inherited:false,multisource:false,source:,value:[filter:IPv6_option_filter,type:Option],option_filter_rules:[filter:IPv6_option_filter,permission:Allow]']
                print(result)
                for i in result:
                    if i in output:
                        assert True
                    else:
                        assert False
                print(result)
                print("Test Case 32 Execution Completed")
                sleep(30)
	
	@pytest.mark.run(order=33)
        def test_033_create_IPv6_fixed_address_in_IPv6_network(self):
                logging.info("Create IPv6 fixed address in IPv6 network")
		global ipv6_network
                ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
                print(ipv6_network)
                ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
                print(ipv6_network)
                data ={"address_type":"ADDRESS","network":ipv6_network+"::/64","duid": "00:02:00:01:02:03:04:05:07:a0","ipv6addr": ipv6_network+"::3","network_view": "default"}
                response = ib_NIOS.wapi_request('POST', object_type="ipv6fixedaddress", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
		sleep(30)
                print("Test Case 33 Execution Completed")


	@pytest.mark.run(order=34)
        def test_034_Validate_adding_ipv6_fixedaddress(self):
                logging.info("Validate adding ipv6 fixed address")
                get_temp = ib_NIOS.wapi_request('GET', object_type="ipv6fixedaddress")
                print(get_temp)
                ref1 = json.loads(get_temp)[0]['_ref']
                get_temp = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=ipv6addr")
                print(get_temp)
                get_temp = get_temp.replace("\n","").replace(" ","")
		#ipv6_network= '2001:550:40a:2500'
		data = ['"ipv6addr":"'+ipv6_network+'::3"']
                print('my get_temp is',get_temp)
                for i in data:
                        if i in get_temp:
                                assert True
                        else:
                                assert False
                print("Test Case 34 Execution Completed")
                print(data)
                sleep(30)


	@pytest.mark.run(order=35)
	def test_035_Update_IPv6_fixedaddress_with_IPv6_Option_filter(self):
                logging.info("Update IPv6 fixed address with IPv6 Option Filter")
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6fixedaddress")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                print("Modify IPv6 fixed address with IPv6 Option Filter")
                data = {"logic_filter_rules":[{"filter": "IPv6_option_filter","type": "Option"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
		print("Restart DHCP services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(30)
                print("Test Case 35 Execution Completed")

        @pytest.mark.run(order=36)
        def test_036_Validate_updating_ipv6_DHCP_fixed_address_with_IPv6_option_filter(self):
                logging.info("Validate updating ipv6 DHCP fixed address with IPv6 option filter")
		get_ref = ib_NIOS.wapi_request('GET',object_type="ipv6fixedaddress",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="ipv6fixedaddress",ref=ref1,params="?_inheritance=True&_return_fields=logic_filter_rules",grid_vip=config.grid_vip)
                print(output)
                output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                print("output",output)
                result = ['logic_filter_rules:inherited:false,multisource:false,source:,value:[filter:IPv6_option_filter,type:Option]']
                print(result)
                for i in result:
                    if i in output:
                        assert True
                    else:
                        assert False
                print(result)
		sleep(50)
                print("Test Case 36 Execution Completed")

        @pytest.mark.run(order=37)
        def test_037_requesting_ipv6_lease_with_fixedaddress(self):
                logging.info("Perform dras command")
		global ipv6_network
		#ipv6_network= '2001:550:40a:2500'
		print("Request lease using Ipv6 option filter with fixed address")
		dras_cmd ='sudo /import/tools/qa/tools/dras6/dras6 -i'+str(config.grid_vip6)+' '+'-n 1 -a 02:02:02:02:04:04 -A -c'+ipv6_network+'::3 -n 1 -O 39:74657374'
                dras_cmd1 = os.system(dras_cmd)
                sleep(30)
                print("Test Case 37 Execution Completed")

        @pytest.mark.run(order=38)
        def test_038_validate_syslog_with_IP_leased_for_Ipv6_fixed_address(self):
                logging.info("validate syslog with IP leased for IPv6 fixed address")
		global ipv6_network
		#ipv6_network= '2001:550:40a:2500'
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        sleep(05)
                        child.sendline('grep -e '+ipv6_network+'::3 /var/log/syslog')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = ['Relay-forward message']
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
                print("Test Case 38 Execution Completed")

	@pytest.mark.run(order=39)
	def test_039_Adding_IPv6_Network_Template(self):
                logging.info("Add IPv6 Network Template")
                data = {"name": "v6_network","members": [{"ipv4addr": config.grid_vip,"ipv6addr": config.grid_vip6,"name": config.grid_fqdn}],"cidr": 64,"logic_filter_rules":[{"filter":"IPv6_option_filter","type":"Option"}]}
                response= ib_NIOS.wapi_request('POST',object_type="ipv6networktemplate",fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print(response)
		sleep(100)
                print("Test Case 39 Execution Completed")

	@pytest.mark.run(order=40)
	def test_040_Validating_IPv6_Network_Template(self):
                logging.info("validating ipv6 Network template")
		get_ref = ib_NIOS.wapi_request('GET',object_type="ipv6networktemplate",grid_vip=config.grid_vip)
		res = json.loads(get_ref)
		ref1 = json.loads(get_ref)[0]['_ref']
		print(ref1)
		output = ib_NIOS.wapi_request('GET',object_type="ipv6networktemplate",ref=ref1,params="?_return_fields=name,logic_filter_rules",grid_vip=config.grid_vip)
		print(output)
          	output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
		print(output)
		result = ['logic_filter_rules:[filter:IPv6_option_filter,type:Option]','name:v6_network']
		for i in result:
		    if i in output:
                        assert True
            	    else:
                	assert False
          	print(result)
		sleep(30)
                print("\nTest Case 40 Execution Completed")

	@pytest.mark.run(order=41)
	def test_041_Adding_IPv6_Range_Template(self):
                logging.info("adding IPv6 range template")
                data = {"name": "v6_range","member":{"_struct":"dhcpmember","ipv4addr":config.grid_vip,"name":config.grid_fqdn},"number_of_addresses": 20,"offset": 6,"server_association_type":"MEMBER","option_filter_rules": [{"filter": "IPv6_option_filter","permission": "Allow"}],"logic_filter_rules":[{"filter": "IPv6_option_filter","type": "Option"}]}
                response = ib_NIOS.wapi_request('POST',object_type="ipv6rangetemplate",fields=json.dumps(data),grid_vip=config.grid_vip)
                print response
                print(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print(response)
		sleep(100)
		print("Test Case 41 Execution Completed")

	@pytest.mark.run(order=42)
	def test_042_Validating_IPv6_Range_Template(self):
                logging.info("validating ipv6 range template")
		get_ref = ib_NIOS.wapi_request('GET',object_type="ipv6rangetemplate",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="ipv6rangetemplate",ref=ref1,params="?_inheritance=True&_return_fields=name,logic_filter_rules",grid_vip=config.grid_vip)
                output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                print(output)
                result = ['logic_filter_rules:[filter:IPv6_option_filter,type:Option]','name:v6_range']
                for i in result:
                    if i in output:
                        assert True
                    else:
                        assert False
                print(result)
		sleep(30)
                print("\nTest Case 42 Execution Completed")

	@pytest.mark.run(order=43)
        def test_043_Adding_IPv6_Fixed_Address_Template(self):
                logging.info("adding fixed address template")
                data = {"name": "v6_fixed_address","number_of_addresses": 10,"offset": 5,"logic_filter_rules":[{"filter": "IPv6_option_filter","type": "Option"}]}
                response = ib_NIOS.wapi_request('POST',object_type="ipv6fixedaddresstemplate",fields=json.dumps(data),grid_vip=config.grid_vip)
                print response
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print(response)
		sleep(100)
		print("Test Case 43 Execution Completed")

        @pytest.mark.run(order=44)
        def test_044_Validating_IPv6_fixed_address_Template(self):
                logging.info("validating ipv6 fixed address template")
		get_ref = ib_NIOS.wapi_request('GET',object_type="ipv6fixedaddresstemplate",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="ipv6fixedaddresstemplate",ref=ref1,params="?_inheritance=True&_return_fields=name,logic_filter_rules",grid_vip=config.grid_vip)
                print(output)
                output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                print(output)
                result = ['logic_filter_rules:[filter:IPv6_option_filter,type:Option]','name:v6_fixed_address']
                for i in result:
                    if i in output:
                        assert True
                    else:
                        assert False
                print(result)
		sleep(30)
                print("\nTest Case 44 Execution Completed")

	
	@pytest.mark.run(order=45)
        def test_045_create_IPv6_network_with_template(self):
                logging.info("Create an ipv6 network in default network view with IPv6 network template")
                data = {"network": "23::/64","network_view": "default","template" : "v6_network"}
                response = ib_NIOS.wapi_request('POST', object_type="ipv6network", fields=json.dumps(data), grid_vip=config.grid_vip)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print(response)
                sleep(100)
                print("Test Case 45 Execution Completed")
#NIOS-80082

        @pytest.mark.run(order=46)
        def test_046_Validate_adding_ipv6_DHCP_network_with_template(self):
                logging.info("Validate adding ipv6 DHCP network with template")
                get_ref = ib_NIOS.wapi_request('GET',object_type="ipv6network",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                output = ib_NIOS.wapi_request('GET',object_type="ipv6network",ref=ref1,params="?_inheritance=True&_return_fields=network,logic_filter_rules",grid_vip=config.grid_vip)
                output=json.loads(output)
                print(output)
                result={'logic_filter_rules':[{'filter':'IPv6_option_filter','type':'Option'}], 'network': '23::/64'}
                if output["logic_filter_rules"] == result["logic_filter_rules"]:
                        assert False
                else:
                        assert True
                print(result)
                print("Test Case 46 Execution Completed")

	@pytest.mark.run(order=47)
        def test_047_create_IPv6_range_in_IPv6_network_with_IPv6_range_template(self):
                logging.info("Create IPv6 range in IPv6 network with IPv6 range template")
                data ={"address_type":"ADDRESS","network":"23::/64","start_addr":"23::2","end_addr":"23::200","network_view": "default","template": "v6_range"}
                response = ib_NIOS.wapi_request('POST', object_type="ipv6range", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                print(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
		sleep(100)
                print("Test Case 47 Execution Completed")

        @pytest.mark.run(order=48)
	def test_048_Validate_adding_IPv6_range_in_IPv6_network_with_IPv6_range_template(self):
                logging.info("Validate adding IPv6 range in IPv6 network with IPv6 range template")
                get_ref = ib_NIOS.wapi_request('GET',object_type="ipv6range",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[-1]['_ref']
                output = ib_NIOS.wapi_request('GET',object_type="ipv6range",ref=ref1,params="?_inheritance=True&_return_fields=start_addr,end_addr,logic_filter_rules",grid_vip=config.grid_vip)
                output=json.loads(output)
                print(output)
                result={'start_addr': '23::2','end_addr': '23::200','logic_filter_rules':[{'filter':'IPv6_option_filter','type':'Option'}]}
                if output["logic_filter_rules"] == result["logic_filter_rules"]:
                        assert False
                else:
                        assert True
                print(result)
                print("Test Case 48 Execution Completed")
                sleep(30)

	@pytest.mark.run(order=49)
        def test_049_create_IPv6_fixed_address_with_fixed_address_template(self):
                logging.info("Create IPv6 fixed address with fixed address template")
                data ={"address_type":"ADDRESS","network":"23::/64","duid": "00:02:00:01:02:03:04:05:07:a3","ipv6addr": "23::4","network_view": "default","template": "v6_fixed_address"}
                response = ib_NIOS.wapi_request('POST', object_type="ipv6fixedaddress", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                print(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Created the ipv6 fixed address in default view")
                print("Test Case 49 Execution Completed")
		sleep(60)


        @pytest.mark.run(order=50)
        def test_050_Validate_adding_ipv6_fixedaddress_with_fixed_address_template(self):
                logging.info("Validate adding ipv6 fixed address with fixed address template")
                get_ref = ib_NIOS.wapi_request('GET',object_type="ipv6fixedaddress",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                output = ib_NIOS.wapi_request('GET',object_type="ipv6fixedaddress",ref=ref1,params="?_inheritance=True&_return_fields=ipv6addr,logic_filter_rules",grid_vip=config.grid_vip)
                output=json.loads(output)
                print(output)
                result={'logic_filter_rules':[{'filter':'IPv6_option_filter','type':'Option'}],'ipv6addr':'23::4'}
                if output["logic_filter_rules"] == result["logic_filter_rules"]:
                        assert False
                else:
                        assert True
                print(result)
                print("Test Case 50 Execution Completed")

	@pytest.mark.run(order=51)
	def test_051_Add_ipv6_option_filter_at_grid_level(self):
                logging.info("adding IPv6 option filter at grid level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                data = {"logic_filter_rules":[{"filter": "IPv6_option_filter","type": "Option"}]}
                response1 = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response1)
                sleep(60)
                print("\nTest Case 51 Execution Completed")

	@pytest.mark.run(order=52)
	def test_052_Validate_added_ipv6_IPv6_option_filter_at_grid_level(self):
                logging.info("validating added ipv6 option filter at grid level")
                get_temp = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties",params="?_inheritance=True&_return_fields=logic_filter_rules")
                get_temp = get_temp.replace("\n","").replace(" ","")
                data=['"logic_filter_rules":[{"filter":"IPv6_option_filter","type":"Option"}]']
                print('my get_temp is',get_temp)
                for i in data:
                        if i in get_temp:
                                assert True
                        else:
                                assert False
                sleep(30)
                print("Test Case 52 Execution Completed")

	@pytest.mark.run(order=53)
        def test_053_Add_ipv6_option_filter_at_member_level(self):
                logging.info("adding IPv6 option filter at member level")
		get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties")
                print(get_ref)
                res = json.loads(get_ref)
                for i in res:
                        data = {"logic_filter_rules":[{"filter": "IPv6_option_filter","type": "Option"}]}
                        response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
                        print response

                read  = re.search(r'200',response)
                for read in  response:
                        assert True
		sleep(150)
                print("\nTest Case 53 Execution Completed")

        @pytest.mark.run(order=54)
        def test_054_Validate_added_ipv6_IPv6_option_filter_at_member_level(self):
                logging.info("validating added ipv6 option filter at grid level")
		get_temp = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties",params="?_inheritance=True&_return_fields=logic_filter_rules")
                get_temp = get_temp.replace("\n","").replace(" ","")
                data=['"logic_filter_rules":[{"filter":"IPv6_option_filter","type":"Option"}]}]']
                print('my get_temp is',get_temp)
                for i in data:
                        if i in get_temp:
                                assert True
                        else:
                                assert False
                sleep(60)
                print("Test Case 54 Execution Completed")

	@pytest.mark.run(order=55)
	def test_055_create_second_IPv6_network_to_add_shared_network(self):
                logging.info("create second IPv6 network to add shared network")
                data = {"network": "22::/64","network_view": "default","members": [{"_struct": "dhcpmember","ipv4addr":config.grid_vip,"name":config.grid_fqdn}]}
                response = ib_NIOS.wapi_request('POST', object_type="ipv6network", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                read  = re.search(r'201',response)
                for read in  response:
                         assert True
                print("Restart DHCP Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(100)
		print("Test Case 55 Execution Completed")


	@pytest.mark.run(order=56)
        def test_056_adding_both_ipv6_DHCP_network_to_add_shared_network_with_csv_import(self):
                logging.info("Adding both ipv6 DHCP network to add shared network_with_csv_import")
                dir_name = os.getcwd()
                base_filename = "Allsharednetworks.csv"
                token = generate_token_from_file(dir_name,base_filename)
                data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"OVERRIDE"}
                response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_import")
                response=json.loads(response)
                sleep(30)
                get_ref=ib_NIOS.wapi_request('GET', object_type="csvimporttask ")
                get_ref=json.loads(get_ref)
                for ref in get_ref:
                   if response["csv_import_task"]["import_id"]==ref["import_id"]:
                       print ref["lines_failed"]
                       if ref["lines_failed"]>0:
                           data={"import_id":ref["import_id"]}
                           response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_error_log")
                           response=json.loads(response)
                           response=response["url"].split("/")
                           print response[4]
                           print response[5]
                           connection=SSH(str(config.grid_vip))
                           command1='cat /tmp/http_direct_file_io/'+response[4]+'/'+response[5]+'| egrep -i \"Insertion\"'
                           print (command1)
                           result=connection.send_command(command1)
                           print (result)
                print("File Uploaded Successfully")
                print("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(100)
		print("Test Case 56 Execution Completed")

	@pytest.mark.run(order=57)
        def test_057_Validate_adding_ipv6_DHCP_shared_network(self):
                logging.info("Validate adding IPv6 DHCP shared network")
                get_temp = ib_NIOS.wapi_request('GET', object_type="ipv6sharednetwork",params="?_inheritance=True&_return_fields=name")
                print(get_temp)
                get_temp = get_temp.replace("\n","").replace(" ","")
                data=['"name":"shared_network"']
                print('my get_temp is',get_temp)
                for i in data:
                        if i in get_temp:
                                assert True
                        else:
                                assert False
                sleep(70)
                print("Test Case 57 Execution Completed")
                print(data)

	@pytest.mark.run(order=58)
        def test_058_Update_IPv6_shared_Network_with_IPv6_Option_filter(self):
                logging.info("Update IPv6 shared network with IPv6 Option Filter")
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6sharednetwork")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                print("Modify IPv6 shared Network with IPv6 Option Filter")
                data = {"logic_filter_rules":[{"filter": "IPv6_option_filter","type": "Option"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 58 Execution Completed")
                sleep(100)

	@pytest.mark.run(order=59)
        def test_059_Validate_addition_of_IPv6_Option_filter_in_shared_network(self):
                logging.info("Validate addition of IPv6 option filter in shared network")
		get_ref = ib_NIOS.wapi_request('GET',object_type="ipv6sharednetwork",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="ipv6sharednetwork",ref=ref1,params="?_inheritance=True&_return_fields=logic_filter_rules",grid_vip=config.grid_vip)
                print(output)
                output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                print(output)
                result = ['logic_filter_rules:[filter:IPv6_option_filter,type:Option]']
                for i in result:
                    if i in output:
                        assert True
                    else:
                        assert False
                print(result)
		sleep(100)
                print("Test Case 59 Execution Completed")

	@pytest.mark.run(order=60)
        def test_060_Update_IPv6_range_with_IPv6_Option_filter_permission_to_Allow_lease(self):
                logging.info("Update IPv6 range with IPv6 Option Filter permission to deny lease")
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6range")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                print("Modify IPv6 range with IPv6 Option Filter")
                data = {"option_filter_rules":[{"filter": "IPv6_option_filter","permission": "Allow"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                print(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
		sleep(30)
		print("Test Case 60 Execution Completed")

	@pytest.mark.run(order=61)
        def test_061_Validate_updating_ipv6_DHCP_range_IPv6_Option_filter_permission_to_allow_lease(self):
                logging.info("Validate updating ipv6 DHCP range with IPv6 Option Filter permission to allow lease")
                get_temp = ib_NIOS.wapi_request('GET', object_type="ipv6range",params="?_inheritance=True&_return_fields=logic_filter_rules,option_filter_rules")
                print(get_temp)
                get_temp = get_temp.replace("\n","").replace(" ","")
                data=['"option_filter_rules":[{"filter":"IPv6_option_filter","permission":"Allow"}]']
                print('my get_temp is',get_temp)
                for i in data:
                        if i in get_temp:
                                assert True
                        else:
                                assert False
                print("Test Case 61 Execution Completed")
                print("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(30)
                print("Service restarted successfully")

	@pytest.mark.run(order=62)
        def test_062_requesting_ipv6_lease_with_permission_to_allow_lease_in_shared_network(self):
                logging.info("Perform dras command")
                dras_cmd ='sudo /import/tools/qa/tools/dras6/dras6 -i'+str(config.grid_vip6)+' '+'-n 1 -a 02:02:02:02:05:05 -A -O 39:74657374'
                dras_cmd1 = os.system(dras_cmd)
                sleep(30)
                print("Test Case 62 Execution Completed")
				
	@pytest.mark.run(order=63)
        def test_063_validate_syslog_with_IP_leased_from_shared_network_when_one_network_is_without_range(self):
                logging.info("validate syslog with IP leased from shared network when one network is without range")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        sleep(05)
                        child.sendline('grep -e 02:02:02:02:05:05 /var/log/syslog')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = ['02:02:02:02:05:05']
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
                print("Test Case 63 Execution Completed")

	@pytest.mark.run(order=64)
        def test_064_Update_IPv6_Option_filter_with_multiple_match_rules(self):
                logging.info("Update IPv6 option filter with multiple match rules")
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6filteroption")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print("Modify IPv6 Option Filter with multiple match rules")
                data = {"expression": "(option dhcp6.fqdn=\"test\" AND option dhcp6.vendor-class=\"mac\")"}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                print(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 64 Execution Completed")
                sleep(30)

	@pytest.mark.run(order=65)
        def test_065_Validate_updation_IPv6_Option_filter_with_multiple_match_rules(self):
                logging.info("Validate updation of IPv6 option filter with multiple match rules")
                get_ref = ib_NIOS.wapi_request('GET',object_type="ipv6filteroption",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="ipv6filteroption",ref=ref1,params="?_inheritance=True&_return_fields=expression",grid_vip=config.grid_vip)
                print(output)
                output=json.loads(output)
                print(output)
                result = {'expression':'(option dhcp6.fqdn="test" AND option dhcp6.vendor-class="mac")'}
                for i in result:
                    if output[i] == result[i]:
                        assert True
                    else:
                        assert False
                print(result)
                print("Test Case 65 Execution Completed")
		print("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(30)
                print("System Restart is done successfully")

	@pytest.mark.run(order=66)
        def test_066_requesting_ipv6_lease_with_multiple_option_filters(self):
                logging.info("Perform dras command")
                dras_cmd ='sudo /import/tools/qa/tools/dras6/dras6 -i'+str(config.grid_vip6)+' '+'-n 1 -A -O 39:74657374 -O 16:6d6163'
                dras_cmd1 = os.system(dras_cmd)
                sleep(30)
                print("Test Case 66 Execution Completed")

	@pytest.mark.run(order=67)
        def test_067_validate_syslog_with_IP_leased_with_multiple_IPv6_option_filter(self):
                logging.info("validate syslog with IP leased with multiple IPv6 option filter")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        sleep(05)
                        child.sendline('grep -e fqdn /var/log/syslog')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = ['err Unable to convert dhcp6.fqdn domain name to printable form']
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
		sleep(60)
                print("Test Case 67 Execution Completed")

	@pytest.mark.run(order=68)
        def test_068_Add_IPv6_network_container_with_IPv6_option_filter(self):
               logging.info("Add IPv6 network container with IPv6 option filter")
               data={"network": "25::/64","network_view": "default","logic_filter_rules":[{"filter": "IPv6_option_filter","type": "Option"}]}
               response = ib_NIOS.wapi_request('POST', object_type="ipv6networkcontainer",fields=json.dumps(data))
               print(response)
               res=response
               res = json.loads(res)
               print(res)
               if type(response) == tuple:
                        if response[0]==400 or response[0]==401:
                                assert False
                        print("Test Casie 68 Execution Completed")

        @pytest.mark.run(order=69)
        def test_069_Validate_addition_of_IPv6_network_container_with_IPv6_option_filter(self):
                logging.info("Validate Addition of IPv6 network container with IPv6 option filter")
                data={'"network"': '"25::/64"','"network_view"': '"default"','"logic_filter_rules"':'[{"filter": "IPv6_option_filter","type": "Option"}]'}
		get_temp=ib_NIOS.wapi_request('GET', object_type="ipv6networkcontainer",params="?_inheritance=True&_return_fields=network,network_view,logic_filter_rules")
                print(get_temp)
                get_temp = get_temp.replace("\n","").replace(" ","")
                print('my get_temp is',get_temp)
                for i in data:
                        if i in get_temp:
                                assert True
                        else:
                                assert False
                sleep(70)
                print("Test Case 69 Execution Completed")

	@pytest.mark.run(order=70)
	def test_070_import_csv_file_with_bulk_IPv6_option_filter(self):
		logging.info("Import CSV file with bulk IPv6 option filter")
		dir_name = os.getcwd()
		base_filename = "Allfilters.csv"
		token = generate_token_from_file(dir_name,base_filename)
		data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"OVERRIDE"}
		response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_import")
		response=json.loads(response)
		sleep(30)
		get_ref=ib_NIOS.wapi_request('GET', object_type="csvimporttask ")
		get_ref=json.loads(get_ref)
		for ref in get_ref:
                   if response["csv_import_task"]["import_id"]==ref["import_id"]:
                       print ref["lines_failed"]
                       if ref["lines_failed"]>0:
                           data={"import_id":ref["import_id"]}
                           response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_error_log")
                           response=json.loads(response)
                           response=response["url"].split("/")
                           print response[4]
                           print response[5]
                           connection=SSH(str(config.grid_vip))
                           command1='cat /tmp/http_direct_file_io/'+response[4]+'/'+response[5]+'| egrep -i \"Insertion\"'
                           print (command1)
                           result=connection.send_command(command1)
                           print (result)
		print("File Uploaded Successfully")
		print("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(100)
		print("Test case 70 completed")

	@pytest.mark.run(order=71)
        def test_071_Validate_addition_of_IPv6_Option_filter_getting_added_in_csv_import(self):
                logging.info("Validate Addition of IPv6 Option filter getting added in csv import")
                get_ref = ib_NIOS.wapi_request('GET',object_type="ipv6filteroption",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[3]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="ipv6filteroption",ref=ref1,params="?_inheritance=True&_return_fields=name,expression,lease_time",grid_vip=config.grid_vip)
                print(output)
                output=json.loads(output)
                print(output)
                result = {'name':'IPv6_filter1'}
                for i in result:
                    if output[i] == result[i]:
                        assert True
                    else:
                        assert False
                print(result)
		sleep(70)
		print("Test case 71 completed")
	
	@pytest.mark.run(order=72)
        def test_072_Add_IPv6_Option_filter_with_apply_as_class_unchecked(self):
               logging.info("Add IPv6 Option Filter with apply as class unchecked")
               data={"name":"IPv6_option_filter_01","comment":"vsinha123","lease_time": 20,"expression": "(option dhcp6.fqdn=\"zone\")","apply_as_class": False}
               response = ib_NIOS.wapi_request('POST', object_type="ipv6filteroption",fields=json.dumps(data))
               print(response)
               res=response
               res = json.loads(res)
               print(res)
               if type(response) == tuple:
                        if response[0]==400 or response[0]==401:
                                assert False
                        print("Test Case 72 Execution Completed")

        @pytest.mark.run(order=73)
        def test_073_Validate_addition_of_IPv6_Option_filter_with_apply_as_class_unchecked(self):
                logging.info("Validate Addition of IPv6 Option filter with apply as class unchecked")
                get_temp = ib_NIOS.wapi_request('GET', "ipv6filteroption?name=IPv6_option_filter_01&_return_fields=expression,name,comment,lease_time,apply_as_class")
                print(get_temp)
                get_temp = get_temp.replace("\n","").replace(" ","")
                print('my get_temp is',get_temp)
		data= ['"apply_as_class":false','"comment":"vsinha123"','"expression":"(optiondhcp6.fqdn=\\"zone\\")"','"lease_time":20','"name":"IPv6_option_filter_01']
                for i in data:
                        if i in get_temp:
                                assert True
                        else:
                                assert False
		sleep(30)
                print("Test Case 73 Execution Completed")

	@pytest.mark.run(order=74)
        def test_074_Negative_scenario_Update_IPv6_range_with_IPv6_Option_filter_with_apply_as_class_unchecked(self):
                logging.info("Update IPv6 range with IPv6 Option Filter with apply as class unchecked")
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6range")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                print("Modify IPv6 range with IPv6 Option Filter")
                data = {"logic_filter_rules":[{"filter": "IPv6_option_filter_01","type": "Option"}],"option_filter_rules":[{"filter": "IPv6_option_filter_01","permission": "Allow"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print(response)
		if type(response) == tuple:
                        if response[0]==400 or response[0]==401:
                                assert True
		print("Test Case 74 Execution Completed")

	@pytest.mark.run(order=75)
        def test_075_Add_custom_IPv6_DHCP_option_space(self):
               logging.info("Add custom IPv6 DHCP Option space")
               data={"name": "v6_space","enterprise_number":22}
               response = ib_NIOS.wapi_request('POST', object_type="ipv6dhcpoptionspace",fields=json.dumps(data))
               print(response)
               res=response
               res = json.loads(res)
               if type(response) == tuple:
                        if response[0]==400 or response[0]==401:
                                assert False
                        print("Test Case 75 Execution Completed")

        @pytest.mark.run(order=76)
        def test_076_Validate_addition_of_custom_IPv6_DHCP_option_space(self):
                logging.info("Validate Addition of custom IPv6 option space")
                get_temp = ib_NIOS.wapi_request('GET', "ipv6dhcpoptionspace?name=v6_space&_return_fields=name,enterprise_number")
                print(get_temp)
                get_temp = get_temp.replace("\n","").replace(" ","")
                print('my get_temp is',get_temp)
		data={'"enterprise_number":22,"name":"v6_space"}]'}
                for i in data:
                        if i in get_temp:
                                assert True
                        else:
                                assert False
                print("Test Case 76 Execution Completed")

	@pytest.mark.run(order=77)
        def test_077_Update_custom_IPv6_DHCP_option_space_with_option_definition(self):
               logging.info("update custom IPv6 DHCP Option space with option definition")
               data={"name":"fqdn","code":9,"space":"v6_space","type":"string"}
               response = ib_NIOS.wapi_request('POST', object_type="ipv6dhcpoptiondefinition",fields=json.dumps(data))
               print(response)
               res=response
               res = json.loads(res)
               print(res)
               if type(response) == tuple:
                        if response[0]==400 or response[0]==401:
                                assert False
                        print("Test Case 77 Execution Completed")

        @pytest.mark.run(order=78)
        def test_078_Validate_Updation_of_custom_IPv6_DHCP_option_space_with_option_definition(self):
                logging.info("Validate updation of custom IPv6 DHCP Option space with option definition")
                get_temp = ib_NIOS.wapi_request('GET', "ipv6dhcpoptiondefinition?name=fqdn&_return_fields=name,code,space,type")
                print(get_temp)
                get_temp = get_temp.replace("\n","").replace(" ","")
                print('my get_temp is',get_temp)
		data=['"code":9,"name":"fqdn","space":"v6_space","type":"string"}]']
                for i in data:
                        if i in get_temp:
                                assert True
                        else:
                                assert False
                print("Test Case 78 Execution Completed")

	@pytest.mark.run(order=79)
        def test_079_update_IPv6_Option_filter_with_IPv6_option_space(self):
                logging.info("Add IPv6 Option Filter with IPv6 option space")
		get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6filteroption")
                print(get_ref)
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                print("Modify IPv6 Option Filter with option space")
                data = {"name":"IPv6_option_filter","comment":"vsinha123","lease_time": 20,"expression": "(option dhcp6.fqdn=\"test\")","apply_as_class": True,"option_space": "v6_space","option_list": [{"name": "fqdn","num": 9,"value": "test","vendor_class": "v6_space"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
		sleep(30)
		print("Test Case 79 Execution Completed")

        @pytest.mark.run(order=80)
        def test_080_Validate_updation_of_IPv6_Option_filter_with_IPv6_option_space(self):
                logging.info("Validate updation of IPv6 Option filter with IPv6 option space")
                get_temp = ib_NIOS.wapi_request('GET', object_type="ipv6filteroption")
                print(get_temp)
                ref1 = json.loads(get_temp)[0]['_ref']
                get_temp = ib_NIOS.wapi_request('GET',ref=ref1,params="?_inheritance=True&_return_fields=name,option_list,option_space")
                print(get_temp)
                get_temp = get_temp.replace("\n","").replace(" ","")
                print('my get_temp is',get_temp)
		data = ['"name":"IPv6_option_filter","option_list":[{"name":"fqdn","num":9,"value":"test","vendor_class":"v6_space"}],"option_space":"v6_space"}']
                for i in data:
                        if i in get_temp:
                                assert True
                        else:
                                assert False
                print("Test Case 80 Execution Completed")
                print(data)
                sleep(5)

#NIOS-80073

	@pytest.mark.run(order=81)
        def test_081_Add_Extensible_Attribute_restrict_to_IPv6optionFilter(self):
               logging.info("Add Extensible Attribute restricts to IPv6OptionFilter")
               data={"name": "location","type": "STRING","allowed_object_types": ["IPv6OptionFilter"]}
               response = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef",fields=json.dumps(data))
               print(response)
               res=response
               res = json.loads(res)
               print(res)
               if type(response) == tuple:
                        if response[0]==400 or response[0]==401:
                                assert False
                        print("Test Case 81 Execution Completed")

        @pytest.mark.run(order=82)
        def test_082_Validate_addition_of_IPv6_Option_filter_in_restricted_EA(self):
                logging.info("Validate Addition of IPv6 Option filter in restricted EA")
                get_temp = ib_NIOS.wapi_request('GET', "extensibleattributedef?name=location&_return_fields=name,type,allowed_object_types")
                print(get_temp)
                get_temp = get_temp.replace("\n","").replace(" ","")
                print('my get_temp is',get_temp)
		data=['"allowed_object_types":["IPv6OptionFilter"],"name":"location","type":"STRING"}]']
                for i in data:
                        if i in get_temp:
                                assert True
                        else:
                                assert False
		print("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(80)
                print("System Restart is done successfully")
                print("Test Case 80 Execution Completed")

	@pytest.mark.run(order=83)
        def test_083_import_csv_file_with_bulk_IPv6_option_filter_with_restricted_EA(self):
                logging.info("Import CSV file with bulk IPv6 option filter with restricted EA")
		dir_name = os.getcwd()
    		base_filename = "Allfilters_EA.csv"
                token = generate_token_from_file(dir_name,base_filename)
                data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"OVERRIDE"}
                response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_import")
                response=json.loads(response)
                sleep(30)
                get_ref=ib_NIOS.wapi_request('GET', object_type="csvimporttask ")
                get_ref=json.loads(get_ref)
                for ref in get_ref:
                   if response["csv_import_task"]["import_id"]==ref["import_id"]:
                       print ref["lines_failed"]
                       if ref["lines_failed"]>0:
                           data={"import_id":ref["import_id"]}
                           response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_error_log")
                           response=json.loads(response)
                           response=response["url"].split("/")
                           print response[4]
                           print response[5]
                           connection=SSH(str(config.grid_vip))
                           command1='cat /tmp/http_direct_file_io/'+response[4]+'/'+response[5]+'| egrep -i \"Insertion\"'
                           print (command1)
                           result=connection.send_command(command1)
                           print (result)
                print("File Uploaded Successfully")
                print("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(100)
                print("Test case 83 completed")

	@pytest.mark.run(order=84)
        def test_084_Validate_addition_of_IPv6_Option_filter_getting_added_with_restricted_EA(self):
                logging.info("Validate Addition of IPv6 Option filter getting added with restricted EA")
		output = ib_NIOS.wapi_request('GET', "ipv6filteroption?name=rfe111&_return_fields=extattrs")
		print(output)
		output = output.replace("\n","").replace(" ","")
		print(output)
                result = ['"extattrs":{"location":{"value":"Bangalore"}}']
                for i in result:
                        if i in output:
                                assert True
                        else:
                                assert False
                sleep(60)
                print("Test case 84 completed")

	@pytest.mark.run(order=85)
	def test_085_import_csv_file_with_global_csv_export(self):
                logging.info("Import CSV file with global csv export")
                dir_name = os.getcwd()
                base_filename = "global_csv_import.csv"
                token = generate_token_from_file(dir_name,base_filename)
                data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"OVERRIDE"}
                response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_import")
                response=json.loads(response)
                sleep(30)
                get_ref=ib_NIOS.wapi_request('GET', object_type="csvimporttask ")
                get_ref=json.loads(get_ref)
                for ref in get_ref:
                   if response["csv_import_task"]["import_id"]==ref["import_id"]:
                       print ref["lines_failed"]
                       if ref["lines_failed"]>0:
                           data={"import_id":ref["import_id"]}
                           response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_error_log")
                           response=json.loads(response)
                           response=response["url"].split("/")
                           print response[4]
                           print response[5]
                           connection=SSH(str(config.grid_vip))
                           command1='cat /tmp/http_direct_file_io/'+response[4]+'/'+response[5]+'| egrep -i \"Insertion\"'
                           print (command1)
                           result=connection.send_command(command1)
                           print (result)
                print("File Uploaded Successfully")
                print("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(100)
                print("Test case 85 completed")

	@pytest.mark.run(order=86)
        def test_086_Validate_addition_of_IPv6_Option_filter_getting_added_in_global_csv_import(self):
                logging.info("Validate Addition of IPv6 Option filter getting added in global csv import")
                get_ref = ib_NIOS.wapi_request('GET',object_type="ipv6filteroption",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[10]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="ipv6filteroption",ref=ref1,params="?_inheritance=True&_return_fields=name,expression,lease_time",grid_vip=config.grid_vip)
                print(output)
                output=json.loads(output)
                print(output)
                result = {'name':'IPv6_filter001'}
                for i in result:
                    if output[i] == result[i]:
                        assert True
                    else:
                        assert False
                print(result)
		sleep(70)
		print("Test case 86 completed")

	@pytest.mark.run(order=87)
	def test_087_Validating_IPv6_optionfilter_reflected_in_DHCP_config_file(self):
                logging.info("validating IPv6 option filter reflected in DHCP config file")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cd /infoblox/var/dhcpdv6_conf')
                child.expect('#')
                child.sendline('cat dhcpdv6.conf')
                sleep(03)
                child.expect('#')
                child.sendline('exit')
                output=child.read()
                output=output.replace('\n','').replace(' ','').replace('[','').replace(']','').replace('\r','').replace('\t','')
                #print(output)
                value = 'IPv6_option_filter'
                if value in output:
                   assert True
                else:
                   assert False
                print("\n")
                print(value)
		sleep(30)
                print("\nTest Case 87 Executed Successfully")

	@pytest.mark.run(order=88)
        def test_088_Negative_scenario_update_IPv6_Option_filter_with_IPv4_option_space(self):
                logging.info("Add IPv6 Option Filter with IPv4 option space")
                get_ref = ib_NIOS.wapi_request('GET', object_type="ipv6filteroption")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
		print(ref1)
                print("Modify IPv6 Option Filter with option space")
                data = {"name":"IPv6_option_filter","comment":"vsinha123","lease_time": 20,"expression": "(option dhcp6.fqdn=\"test\")","apply_as_class": True,"option_space": "DHCP"}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print('my response is',response)
                data= '"Error": "AdmConDataError: None (IBDataConflictError: IB.Data.Conflict:DHCP option filter \'IPv6_option_filter\' is using an...IPv6_option_filter\' is using an incorrect IPv4/IPv6 option space type. IPv4/IPv6 option space should be of the string data type"\n'
                if response[0]==400 or response[0]==401:
                                assert True
                print("Test Case 88 Execution Completed")

	@pytest.mark.run(order=89)
        def test_089_Add_IPv4_Option_filter_for_functionality_testing(self):
               logging.info("Add IPv4 Option Filter for functionality testing")
               data={"name":"IPv4_option_filter","comment":"vsinha123","lease_time": 30,"expression": "(option fqdn=\"test\")","apply_as_class": True}
               response = ib_NIOS.wapi_request('POST', object_type="filteroption",fields=json.dumps(data))
               print(response)
               res=response
               res= json.loads(res)
               print(res)
               if type(response) == tuple:
                        if response[0]==400 or response[0]==401:
                                assert False
                        print("Test Case 89 Execution Completed")

        @pytest.mark.run(order=90)
        def test_090_Validate_addition_of_IPv4_Option_filter(self):
                logging.info("Validate Addition of IPv4 Option filter")
                get_ref = ib_NIOS.wapi_request('GET',object_type="filteroption",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="filteroption",ref=ref1,params="?_inheritance=True&_return_fields=name,expression,lease_time",grid_vip=config.grid_vip)
                print(output)
                output=json.loads(output)
                print(output)
                result = {'name':'IPv4_option_filter','expression':'(option fqdn=\"test\")','lease_time': 30}
                for i in result:
                    if output[i] == result[i]:
                        assert True
                    else:
                        assert False
                print(result)
                print("Test Case 90 Execution Completed")

	@pytest.mark.run(order=91)
        def test_091_create_IPv4_network(self):
                logging.info("create IPv4 network")
                data = {"network": "10.0.0.0/24","network_view": "default","members": [{"_struct": "dhcpmember","ipv4addr":config.grid_vip,"name":config.grid_fqdn}]}
                response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                read  = re.search(r'201',response)
                for read in  response:
                         assert True
                print("Test Case 91 Execution Completed")

	@pytest.mark.run(order=92)
        def test_092_Validate_addition_of_IPv4_network(self):
                logging.info("Validate addition of IPv4 network")
		get_ref = ib_NIOS.wapi_request('GET',object_type="network",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="network",ref=ref1,params="?_inheritance=True&_return_fields=network",grid_vip=config.grid_vip)
                print(output)
                output=json.loads(output)
                print(output)
                result = {'network':'10.0.0.0/24'}
                for i in result:
                    if output[i] == result[i]:
                        assert True
                    else:
                        assert False
                print(result)
                print("Test Case 92 Execution Completed")

	@pytest.mark.run(order=93)
        def test_093_create_IPv4_range_in_IPv4_network(self):
                logging.info("Create IPv4 range in IPv4 network")
                data ={"network":"10.0.0.0/24","start_addr":"10.0.0.2","end_addr":"10.0.0.200","network_view": "default","member":{"_struct":"dhcpmember","ipv4addr":config.grid_vip,"name":config.grid_fqdn}}
                response = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                print(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
		sleep(30)
                print("Test Case 93 Execution Completed")		

	@pytest.mark.run(order=94)
        def test_094_Validate_adding_ipv4_range_in_IPv4_network(self):
                logging.info("Validate adding IPv4 range in IPv4 network")
                get_ref = ib_NIOS.wapi_request('GET',object_type="range",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="range",ref=ref1,params="?_inheritance=True&_return_fields=start_addr,end_addr",grid_vip=config.grid_vip)
                print(output)
                output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                print("output",output)
                result = ['start_addr:10.0.0.2','end_addr:10.0.0.200']
                print(result)
                for i in result:
                    if i in output:
                        assert True
                    else:
                        assert False
                print(result)
		sleep(30)
		print("Test Case 94 Execution Completed")

        @pytest.mark.run(order=95)
	def test_095_Update_IPv4_range_with_IPv4_Option_filter_permission_to_allow_lease(self):
                logging.info("Update IPv6 range with IPv6 Option Filter permission to allow lease")
                get_ref = ib_NIOS.wapi_request('GET', object_type="range")
                print(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                print("Modify IPv6 range with IPv6 Option Filter")
                data = {"use_logic_filter_rules": True,"logic_filter_rules":[{"filter": "IPv4_option_filter","type": "Option"}],"option_filter_rules":[{"filter": "IPv4_option_filter","permission": "Allow"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
		sleep(50)
                print("Test Case 95 Execution Completed")

	@pytest.mark.run(order=96)
	def test_096_Validate_adding_ipv4_option_filter_in_IPv4_range(self):
                logging.info("Validate adding IPv4 option filter in IPv4 range")
                get_ref = ib_NIOS.wapi_request('GET',object_type="range",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="range",ref=ref1,params="?_inheritance=True&_return_fields=logic_filter_rules,option_filter_rules",grid_vip=config.grid_vip)
                print(output)
                output=output.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                print("output",output)
                result = ['logic_filter_rules:inherited:false,multisource:false,source:,value:[filter:IPv4_option_filter,type:Option],option_filter_rules:[filter:IPv4_option_filter,permission:Allow]']
                print(result)
                for i in result:
                    if i in output:
                        assert True
                    else:
                        assert False
                print(result)
		sleep(30)
		print("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(100)
                print("Test Case 96 Execution Completed")

	@pytest.mark.run(order=97)
        def test_097_requesting_ipv4_lease_with_Ignore_prefix_length(self):
                logging.info("Perform dras command")
                dras_cmd ='sudo /import/tools/qa/tools/dras/dras -i'+str(config.grid_vip)+' '+'-n 1 -x l=10.0.0.0 -O 81:74657374'
                dras_cmd1 = os.system(dras_cmd)
                sleep(30)
                print("Test Case 97 Execution Completed")
				
	@pytest.mark.run(order=98)
        def test_098_validate_syslog_with_IP_leased_for_IPv4_option_filter(self):
                logging.info("validate syslog with IP leased for IPv4 option filter")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        sleep(05)
                        child.sendline('grep -e fancy bits /var/log/syslog')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = ['fancy bits in fqdn option']
                        for i in data:
                                if i in output:
                                        assert False
                                        print(i)
                                else:
                                        assert True
                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
		sleep(100)
                print("Test Case 98 Execution Completed")

	@pytest.mark.run(order=99)
        def test_099_Add_second_ipv6_option_filter_at_member_level(self):
                logging.info("adding second IPv6 option filter at member level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties")
                print(get_ref)
                res = json.loads(get_ref)
                for i in res:
                        data = {"logic_filter_rules":[{"filter": "IPv6_option_filter","type": "Option"},{"filter":"IPv6_filter001","type": "Option"}]}
                        response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
                        print response

                read  = re.search(r'200',response)
                for read in  response:
                        assert True
		print("Restart DHCP services to reflect changes")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(100)
                print("\nTest Case 99 Execution Completed")

        @pytest.mark.run(order=100)
        def test_100_Validate_added_ipv6_IPv6_option_filter_at_member_level(self):
                logging.info("validating added ipv6 option filter at grid level")
                get_temp = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties",params="?_inheritance=True&_return_fields=logic_filter_rules")
                get_temp = get_temp.replace("\n","").replace(" ","")
                data=['"logic_filter_rules":[{"filter":"IPv6_option_filter","type":"Option"},{"filter":"IPv6_filter001","type":"Option"}]']
                print('my get_temp is',get_temp)
                for i in data:
                        if i in get_temp:
                                assert True
                        else:
                                assert False
                sleep(60)
                print("Test Case 100 Execution Completed")


	@pytest.mark.run(order=101)
        def test_101_create_non_super_user(self):
            logging.info("Creating non-super user to test functionality")
            data={"admin_groups":["saml-group"],"name": "user1","password":"infoblox"}
            response = ib_NIOS.wapi_request('POST', object_type="adminuser",fields=json.dumps(data))
            print(response)
            res=response
            res = json.loads(res)
            print(res)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    assert False
                print("Test Case 100 Execution Completed")
		print("Restart DHCP services to reflect changes")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(30)
                print("Test case 101 Execution Completed")
	

	@pytest.mark.run(order=102)
        def test_102_Add_IPv6_Option_filter_for_functionality_testing_through_a_non_superuser(self):
            	logging.info("Add IPv6 Option Filter for functionality testing through a non-superuser")
            	data={"name":"IPv6_option_filter_03","comment":"vsinha123","lease_time": 20,"apply_as_class": True}
            	response = ib_NIOS.wapi_request('POST', object_type="ipv6filteroption",fields=json.dumps(data),user='user1',password='infoblox')
                print('my response is',response)
                if response[0]==400 or response[0]==401:
                                assert True
	    	print("Test Case 102 Execution Completed")

	@pytest.mark.run(order=103)
        def test_103_requesting_ipv6_lease_with_prefixrange(self):
                logging.info("Perform dras command")
                global ipv6_network
		ipv6_network = '2001:550:40a:2500'
                dras_cmd ='sudo /import/tools/qa/tools/dras6/dras6 -i'+str(config.grid_vip6)+' '+'-n 1 -a 02:02:02:02:07:07 -A -c '+str(ipv6_network)+'"::" -n 1 -O 39:74657374 -b  '+str(ipv6_network)+'"::/64"'
                dras_cmd1 = os.system(dras_cmd)
                sleep(30)
                print("Test Case 103 Execution Completed")

        @pytest.mark.run(order=104)
        def test_104_validate_syslog_with_IP_leased_for_Ipv6_prefix_range(self):
                logging.info("validate syslog with IP leased for IPv6 prefix range")
                global ipv6_network
                #ipv6_network= '2001:550:40a:2500'
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        sleep(05)
                        child.sendline('grep -e 02:02:02:02:07:07 /var/log/syslog')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = ['02:02:02:02:07:07']
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
                print("Test Case 104 Execution Completed")



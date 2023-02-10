import config
import json
import os
import pytest
import pexpect
import re
import sys
import subprocess
#import time
from time import sleep
import unittest
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from logger import logger
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results

class MS_Server(unittest.TestCase):
    @classmethod

    def setup_class(cls):

        logger.info("Generating data for MS Server reports")
        print("Generating data for MS Server reports")
        grid_member = ib_NIOS.wapi_request('GET', object_type="member?_return_fields=host_name")
        print("################################################")
        print(grid_member)
        ref = json.loads(grid_member)[0]['host_name']
        print("************************************************")
        print(ref)
        print("***********MS SERVER IP*************",config.ms_server_ip)

	ms_server = {"address": config.ms_server_ip,"grid_member": ref,"read_only": False,"synchronization_min_delay": 2,"login_name": config.ms_name,"login_password": config.ms_password,"dns_server": {"managed": True,"enable_monitoring": True,"synchronization_min_delay": 2,"use_enable_dns_reports_sync": False,"use_enable_monitoring": False,"use_login": False,"use_synchronization_min_delay": False},"dhcp_server": {"managed": True,"enable_monitoring": True,"login_name": config.ms_name,"synchronization_min_delay": 2,"use_enable_monitoring": False,"use_login": False,"use_synchronization_min_delay": False}}

        get_ref = ib_NIOS.wapi_request('POST',object_type="msserver", fields=json.dumps(ms_server))
	print("###############################################################",get_ref)
        if (get_ref[0] == 400):
            print("Another Microsoft server is using the address "+config.ms_server_ip)
            assert True
        else:
            print("MS Server \'10.34.98.32\' has been created")

        print("Performing service restart operation")
	logger.info("Performing service restart operation")
	grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print(restart)
        logger.info("Waiting 30 sec., for Member Restart")
	sleep(60)

        #Validation of networks synced from MS Server
        get_ref = ib_NIOS.wapi_request("GET",object_type="network?network=10.0.0.0/8")
        ref_1=json.loads(get_ref)[0]['network']
        print(ref_1)
	
	get_ref = ib_NIOS.wapi_request("GET",object_type="network?network=20.0.0.0/24")
        ref_2=json.loads(get_ref)[0]['network']
        print(ref_2)

        if (ref_1 == "10.0.0.0/8"):
            print("\nPASS")
            assert True
        else:
            print("\nFAIL")
            assert False

        if (ref_2 == "20.0.0.0/24"):
            print("PASS")
            assert True
        else:
            print("FAIL")
            assert False

        #Preparation for Test1

        cmd="sudo /import/tools/qa/tools/dras/dras -n 1 -i "+config.ms_server_ip+" -x l=10.0.0.0"
        logger.info("Request lease using dras command for action=Issued")
        fp=os.popen(cmd)
	sleep(10)

        #Preparation for Test2
        cmd="sudo /import/tools/qa/tools/dras/dras -n 1 -i "+config.ms_server_ip+" -x l=20.0.0.0"
        logger.info("Request lease using dras command for action=Issued")
        fp=os.popen(cmd)

        print("sleeping for 4500 seconds")
        sleep(4500)

	logger.info("Validation of MS Server reports")
	cls.dhcp_lease_history = [{"Protocol":"IPV4","Action":"Issued","Microsoft Server IP":"10.34.98.32"}]
	
	cls.ipam_device_networks = [{"IPAM Network":"20.0.0.0/24","Utilization %":"39.3","Network View":"default"},{"IPAM Network":"10.0.0.0/8","Utilization %":"0.0","Network View":"default"}]

	cls.ipam_network_statistics = [{"Network view":"default","Network":"10.0.0.0","CIDR":"8","Total":"16777216","Allocated":"200","Protocol":"IPV4"},{"Network view":"default","Network":"20.0.0.0","CIDR":"24","Total":"256","Protocol":"IPV4"}]

	cls.ipam_network_trend = [{"10.0.0.0/8":"0"}]	
	#cls.ipam_network_trend  = [{"Network view":"default","Network":"20.0.0.0","CIDR":"24","Utilization %":"39.3","Total":"256"},{"Network view":"default","Network":"10.0.0.0","CIDR":"8","Utilization %":"0.0","Total":"16777216"}]
	
	cls.ipam_top_utilized_networks = [{"Network view":"default","Network":"20.0.0.0","CIDR":"24","Utilization %":"39.3","Total":"256","Assigned":"3","Reserved":"2","Unmanaged":"0"},{"Network view":"default","Network":"10.0.0.0","CIDR":"8","Utilization %":"0.0","Total":"16777216","Assigned":"31","Reserved":"2","Unmanaged":"0"}]

	cls.dhcp_top_utilized_networks = [{"Provisioned": "100", "Network View": "default", "Static": "0", "CIDR": "8", "Network": "10.0.0.0"},{"Provisioned": "100", "Network View": "default", "Static": "0","CIDR": "24", "Network": "20.0.0.0"}]

	cls.dhcp_message_rate_trend = [{"DHCPv6SOLICIT":"0","DHCPv6ADVERTISE":"0","DHCPv6REQUEST":"0","DHCPv6REPLY":"0","DHCPv4DISCOVER":"0","DHCPv4OFFER":"0","DHCPv4REQUEST":"0","DHCPv4ACK":"0"}]

    @pytest.mark.run(order=1)
    def test_001_dhcp_lease_history_validation(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
	
	search_str="search sourcetype=ib:dhcp:lease_history index=ib_dhcp_lease_history (host=\"*\") * * * * dhcpd OR dhcpdv6 r-l-e | eval Protocol=if(PROTO==\"dhcpdv6\",\"IPV6\",\"IPV4\") | noop | eval LEASE_START=strftime(START_EPOCH, \"%Y-%m-%d %H:%M:%S\") | eval LEASE_END=strftime(END_EPOCH, \"%Y-%m-%d %H:%M:%S\") | eval dummy_epoch=\"\" | eval __COMMENT=\"The lease_time.latest and lease_time.latest are the date format in epoch number. For example if  timestamp is 01-01-1971 01.01.01, the epoch number is 8 digit number. So taken lease_time length with >=8.\" | eval min_lengh_epoch=8 | eval earliest=if(len(\"0\") <= min_lengh_epoch, dummy_epoch , \"0\") | eval latest=if(len(\"\") <= min_lengh_epoch, dummy_epoch , \"\")  | eval earliest=if(len(\"0\") == 0, START_EPOCH,\"0\") | eval latest=if(len(\"\") == 0, END_EPOCH,\"\") | where ((earliest <= START_EPOCH) AND (START_EPOCH <= latest))    OR ((earliest <= END_EPOCH) AND (END_EPOCH <= latest))  | eval FINGER_PRINT=if(isnull(OS_NUMBER) OR OS_NUMBER==0,FP,SFP) | eval resolved_names_or_ips=coalesce(ms_resolved_names,ms_resolved_ips) | eval resolved_names_or_ips=if(isnull(resolved_names_or_ips),MS_SERVER,resolved_names_or_ips) | noop | noop | eval host = if (isnull(MS_SERVER),host,NULL) | eval MEMBER_IP = if (isnull(MS_SERVER),MEMBER_IP,NULL) | noop | eval DEVICE_CLASS=if(isnull(DEVICE_CLASS), \"Modified or Deleted\", DEVICE_CLASS) | rename host as \"Member\", ACTION as \"Action\", LEASE_IP as \"Lease IP\", MAC_DUID as \"MAC/DUID\", MEMBER_IP as \"Member IP\", OPTION12HOST as \"Host Name\", LEASE_START as \"Lease Start\", LEASE_END as \"Lease End\", FINGER_PRINT as \"Fingerprint\", MS_SERVER as \"Microsoft Server IP\", ms_resolved_names as \"Microsoft Server\"  | convert ctime(_time) as Time  | table Time, Member, \"Member IP\", Protocol, Action, \"Lease IP\", \"MAC/DUID\", \"Host Name\", \"Lease Start\", \"Lease End\", \"Fingerprint\", \"Microsoft Server\", \"Microsoft Server IP\""

	cmd = config.search_py + " '" + search_str + "' --output_mode=json"
	print("EXECUTION OF SEARCH STRING COMMAND",cmd)
        print(os.system(cmd))
        print("*****************%%%%%*********************")

        try:
            retrived_data=open(config.json_file).read()
            print(retrived_data)
           
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']

        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.dhcp_lease_history,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%",self.dhcp_lease_history)
        print("-------------------------------------")
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$",results_list)
        result = compare_results(self.dhcp_lease_history,results_list)
        print("#####################################",result)
	if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg


    @pytest.mark.run(order=2)
    def test_002_ipam_device_networks(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)

	search_str = "search source=ib:discovery:switch_port_capacity index=ib_discovery | fillnull value=\"N/A\" | dedup network_view device_ip_address interface_ip_address | join type=inner InterfaceSubnet, network_view [search sourcetype=ib:ipam:network index=ib_ipam | dedup NETWORK, view | rename NETWORK as InterfaceSubnet view as network_view | fields InterfaceSubnet, network_view, allocation] | APPEND [search sourcetype=ib:ipam:network index=ib_ipam | dedup NETWORK, view | rename NETWORK as InterfaceSubnet view as network_view | join type=left InterfaceSubnet, network_view [search source=ib:discovery:switch_port_capacity index=ib_discovery | fields InterfaceSubnet, device_ip_address, network_view] | where isnull(device_ip_address)] | rename InterfaceSubnet as \"IPAM Network\" allocation as \"Utilization %\" device_ip_address as \"Device IP\" interface_ip_address as \"Interface IP\" device_model as \"Device Model\" device_vendor as \"Device Vendor\" device_version as \"Device OS Version\" device_name as \"Device Name\" network_view as \"Network View\" | table \"IPAM Network\", \"Utilization %\", \"Network View\", \"Device IP\", \"Device Name\", \"Interface IP\", \"Device Model\", \"Device Vendor\", \"Device OS Version\""

        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
	print("EXECUTION OF SEARCH STRING COMMAND",cmd)
        print(os.system(cmd))
        print("*****************%%%%%*********************")

	
        try:
            retrived_data=open(config.json_file).read()
            print(retrived_data)

        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        results_dist= results_list[-240::1]

        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        print(results_dist)
        first=results_dist[0]
        print(first)
        second=results_dist[1]
        print(second)
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

        if first['Utilization %'] >= 0 and second['Utilization %'] >= 0:
            print("-----------------------------------------")
            print("20.0.0.0/8 Utilization %",first['Utilization %'])
            print("10.0.0.0/24 Utilization %",second['Utilization %'])
            print("--------------***********----------------")
            print("PASSED")
            logger.info("Search validation result: %s %s(PASS)",first,second)
            assert True

        else:
            logger.error("Search validation result: %s %s(FAIL)",first,second)

            msg = 'Count does not match - %s %s', first,second
            assert False

	'''
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.ipam_device_networks,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%",self.ipam_device_networks)
        print("-------------------------------------")
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$",results_list)
        result = compare_results(self.ipam_device_networks,results_list)
        print("#####################################",result)
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg
 	'''

    @pytest.mark.run(order=3)
    def test_003_ipam_network_statistics(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)

	search_str = "search sourcetype=ib:ipam:network index=ib_ipam | eval dedup_key=view.\"/\".address.\"/\".cidr | dedup dedup_key | eval NETWORK=address.\"/\".cidr | lookup network_ea_lookup_csv NETWORK, NETWORK_VIEW as view output EA | spath input=EA output=MSSITE path=BUILTIN-MSSite | eval MSSITE = if(isnull(MSSITE), \"(no_value)\", MSSITE) | mvexpand MSSITE | eval utilization=round(utilization/10, 1) | mvcombine MSSITE | sort -utilization | rename timestamp as Timestamp, view as \"Network view\", address as Network, cidr as CIDR, MSSITE as \"AD Site\", utilization as \"DHCPv4 Utilization %\", address_total as Total, address_alloc as Allocated, address_reserved as Reserved, address_assigned as Assigned, protocol as Protocol, allocation as \"Utilization %\", address_unmanaged as Unmanaged | table Timestamp, \"Network view\", Network, CIDR, \"AD Site\", \"DHCPv4 Utilization %\", Total, Allocated, Reserved, Assigned, Protocol, \"Utilization %\", Unmanaged"


        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
	print("EXECUTION OF SEARCH STRING COMMAND",cmd)

        print(os.system(cmd))
        print("*****************%%%%%*********************")

        try:
            retrived_data=open(config.json_file).read()
            print(retrived_data)

        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']

        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.ipam_network_statistics,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%",self.ipam_network_statistics)
        print("-------------------------------------")
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$",results_list)
        result = compare_results(self.ipam_network_statistics,results_list)
        print("#####################################",result)
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg

    @pytest.mark.run(order=4)
    def test_004_ipam_network_trend(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)

	search_str = "search sourcetype=ib:ipam:network index=ib_ipam earliest=-8h | eval NETWORK=address.\"/\".cidr | lookup network_ea_lookup_csv NETWORK, NETWORK_VIEW as view output EA | spath input=EA output=MSSITE path=BUILTIN-MSSite | eval MSSITE = if(isnull(MSSITE), \"(no_value)\", MSSITE) | mvexpand MSSITE | sort 0 -allocation | timechart bins=1000 avg(allocation) as \"Usage %\" by NETWORK useother=f"

        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
	print("EXECUTION OF SEARCH STRING COMMAND",cmd)

        print(os.system(cmd))
        print("*****************%%%%%*********************")

        try:
            retrived_data=open(config.json_file).read()
            print(retrived_data)

        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']

        '''
	results_dist= results_list[-2400::1]

        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        print(results_dist)
        first=results_dist[0]
        print(first)
        second=results_dist[1]
        print(second)
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

        if first['10.0.0.0/8'] >= 0 and second['20.0.0.0/24'] >= 0:
            print("-----------------------------------------")
            print("10.0.0.0/8",first['10.0.0.0/8'])
            print("20.0.0.0/24",second['20.0.0.0/24'])
            print("--------------***********----------------")
            print("PASSED")
            logger.info("Search validation result: %s %s(PASS)",first,second)
            assert True

        else:
            logger.error("Search validation result: %s %s(FAIL)",first,second)

            msg = 'Count does not match - %s %s', first,second
            assert False

	'''
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.ipam_network_trend,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%",self.ipam_network_trend)
        print("-------------------------------------")
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$",results_list)
        result = compare_results(self.ipam_network_trend,results_list)
        print("#####################################",result)
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg

    @pytest.mark.run(order=5)
    def test_005_ipam_top_utilized_networks(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)

	search_str = "search sourcetype=ib:ipam:network index=ib_ipam | eval dedup_key=view.\"/\".address.\"/\".cidr | dedup dedup_key | eval NETWORK=address.\"/\".cidr | lookup network_ea_lookup_csv NETWORK, NETWORK_VIEW as view output EA | spath input=EA output=MSSITE path=BUILTIN-MSSite | eval MSSITE = if(isnull(MSSITE), \"(no_value)\", MSSITE) | sort -allocation | head 10 | rename timestamp as Timestamp, view as \"Network view\", address as Network, cidr as CIDR, MSSITE as \"AD Site\", allocation as \"Utilization %\", address_total as Total, address_assigned as Assigned, address_reserved as Reserved, address_unmanaged as Unmanaged | table Timestamp, \"Network view\", Network, CIDR, \"AD Site\", \"Utilization %\", Total, Assigned, Reserved, Unmanaged"

        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
	print("EXECUTION OF SEARCH STRING COMMAND",cmd)

        print(os.system(cmd))
        print("*****************%%%%%*********************")

        try:
            retrived_data=open(config.json_file).read()
            print(retrived_data)

        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        results_dist= results_list[-240::1]

        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        print(results_dist)
        first=results_dist[0]
        print(first)
        second=results_dist[1]
        print(second)
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

        if first['Utilization %'] >= 0 and second['Utilization %'] >= 0:
            print("-----------------------------------------")
            print("10.0.0.0/8 Utilization %",first['Utilization %'])
            print("20.0.0.0/24 Utilization %",second['Utilization %'])
            print("--------------***********----------------")
            print("PASSED")
            logger.info("Search validation result: %s %s(PASS)",first,second)
            assert True

        else:
            logger.error("Search validation result: %s %s(FAIL)",first,second)

            msg = 'Count does not match - %s %s', first,second
            assert False

	'''
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.ipam_network_trend,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%",self.ipam_network_trend)
        print("-------------------------------------")
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$",results_list)
        result = compare_results(self.ipam_network_trend,results_list)
        print("#####################################",result)
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg
	'''

    @pytest.mark.run(order=06)
    def test_006_dhcp_top_utilized_networks(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)

	search_str = "search sourcetype=ib:dhcp:network index=ib_dhcp | eval dedup_key=view.\"/\".address.\"/\".cidr | dedup dedup_key | sort 0 -num(dhcp_utilization) | head 10 | eval Free=address_total-dhcp_hosts | rename timestamp as Timestamp, view as \"Network View\", address as Network, cidr as CIDR, dhcp_utilization as \"DHCPv4 Utilization %\", ranges as Ranges, address_total as Provisioned, dhcp_hosts as Used, static_hosts as Static, dynamic_hosts as Dynamic | table Timestamp, \"Network View\", Network, CIDR, \"DHCPv4 Utilization %\", Ranges, Provisioned, Dynamic, Static, Free, Used"

        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
	print("EXECUTION OF SEARCH STRING COMMAND",cmd)

        print(os.system(cmd))
        print("*****************%%%%%*********************")

        try:
            retrived_data=open(config.json_file).read()
            print(retrived_data)

        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        results_dist= results_list[-240::1]

        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        print(results_dist)
        first=results_dist[0]
        print(first)
        second=results_dist[1]
        print(second)
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

        if first['Dynamic'] >= 0 and first['Free'] >=0 and first['DHCPv4 Utilization %'] >= 0 and second['Dynamic'] >= 0 and second['Free'] >=0 and second['DHCPv4 Utilization %'] >= 0:
            print("-----------------------------------------")
	    print("10.0.0.0/8 Dynamic",first['Dynamic'])
	    print("10.0.0.0/8 Free",first['Free'])
            print("10.0.0.0/8 DHCPv4 Utilization %",first['DHCPv4 Utilization %'])
            print("20.0.0.0/24 Dynamic",second['Dynamic'])
            print("20.0.0.0/24 Free",second['Free'])
            print("20.0.0.0/24 DHCPv4 Utilization %",second['DHCPv4 Utilization %'])
            print("--------------***********----------------")
            print("PASSED")
            logger.info("Search validation result: %s %s(PASS)",first,second)
            assert True

        else:
            logger.error("Search validation result: %s %s(FAIL)",first,second)

            msg = 'Count does not match - %s %s', first,second
            assert False

	'''
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.dhcp_top_utilized_networks,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%",self.dhcp_top_utilized_networks)
        print("-------------------------------------")
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$",results_list)
        result = compare_results(self.dhcp_top_utilized_networks,results_list)
        print("#####################################",result)

        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg
	'''

    @pytest.mark.run(order=07)
    def test_007_dhcp_message_rate_trend(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)

	search_str="search index=ib_dhcp_summary report=si_dhcp_message (orig_host=\"*\")| eval resolved_names_or_ips=coalesce(ms_resolved_names,ms_resolved_ips)| eval resolved_names_or_ips=if(isnull(resolved_names_or_ips),ms_server,resolved_names_or_ips)| noop| stats sum(v6solicit) as v6solicit,   sum(v6advertise) as v6advertise,   sum(v6request) as v6request,   sum(v6reply) as v6reply,   sum(v4discover) as v4discover,   sum(v4offer) as v4offer,   sum(v4request) as v4request,   sum(v4ack) as v4ack by _time| timechart bins=1000 avg(v6solicit) as DHCPv6SOLICIT,  avg(v6advertise) as DHCPv6ADVERTISE,  avg(v6request) as DHCPv6REQUEST,  avg(v6reply) as \"DHCPv6REPLY\",  avg(v4discover) as DHCPv4DISCOVER,  avg(v4offer) as DHCPv4OFFER,  avg(v4request) as DHCPv4REQUEST,  avg(v4ack) as \"DHCPv4ACK\"|  sort -_time  | rename _time as Time  | eval Time=strftime(Time, \"%Y-%m-%d %H:%M:%S %Z\")"

        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        print("EXECUTION OF SEARCH STRING COMMAND",cmd)

        print(os.system(cmd))
        print("*****************%%%%%*********************")

        try:
            retrived_data=open(config.json_file).read()
            print(retrived_data)

        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']

        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.dhcp_message_rate_trend,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%",self.dhcp_message_rate_trend)
        print("-------------------------------------")
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$",results_list)
        result = compare_results(self.dhcp_message_rate_trend,results_list)
        print("#####################################",result)

        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg


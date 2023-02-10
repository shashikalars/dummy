"""
 Copyright (c) Infoblox Inc., 2016

 ReportName          : DNS Query Rate By Query Type
 ReportCategory      : DNS Query
 Number of Test cases: 1
 Execution time      : 361.09 seconds
 Execution Group     : Minute Group (MG)
 Description         : DNS 'Query Rate by Query Type' report update every 1 min.

 Author   : Vindya V K
 History  : 02/24/2021 (Created)
 Reviewer : Shekhar and Manoj
"""

import config
import json
import os
import pytest
import pexpect
import re
import sys
import subprocess
from time import sleep
import time
import unittest
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from logger import logger
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results

"""
TEST Steps:
      1.  Input/Preparaiton      : Adding Networks, Shared addresses, fixed address, Range and reservations
      2.  Search                 : Search with Default Filter
      3.  Validation             : Validating Search result against input data
"""

# Preparation steps - Creating the required networks

class IPAMv4NetworkUsageStatistics(unittest.TestCase):
    @classmethod
    def setup_class(cls):

        logger.info("Add Network '10.0.0.0/8' with Grid master as Member assignment")
        network1 = {"network":"10.0.0.0/8","network_view":"default","members":[{"name":config.grid_fqdn,"_struct": "dhcpmember"}],"options":[{"name": "dhcp-lease-time","value": "74390400"}]}
        network1_response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(network1))
        network1_get = ib_NIOS.wapi_request('GET', object_type="network?network=10.0.0.0/8")
        network1_ref = json.loads(network1_get)[0]['_ref']


        logger.info("Add Network '165.0.0.0/8' with Grid master as Member assignment")
        network2 = {"network":"165.0.0.0/8","network_view":"default","members":[{"name":config.grid_fqdn,"_struct": "dhcpmember"}],"options":[{"name": "dhcp-lease-time","value": "74390400"}],}
        network2_response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(network2))
        network2_get = ib_NIOS.wapi_request('GET', object_type="network?network=165.0.0.0/8")
        network2_ref = json.loads(network2_get)[0]['_ref']


        logger.info("Add Range '165.0.0.1-165.10.10.255' in '165.0.0.0/8' with Grid master as Member assignment")
        range1 = {"network":"165.0.0.0/8","network_view":"default","member":{"_struct": "dhcpmember","name":config.grid_fqdn},"start_addr":"165.0.0.1","end_addr":"165.10.10.255"}
        range1_response = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(range1))


        logger.info("Add 10 fixed address in '165.0.0.0/8'")
        for i in range(10):
           fix_addr = {"network":"165.0.0.0/8","network_view":"default","ipv4addr":"165.0.30."+str(i),"mac":"00:00:00:00:00:"+str(i)}
           fix_response = ib_NIOS.wapi_request('POST', object_type="fixedaddress", fields=json.dumps(fix_addr))

        logger.info("Add 10 Reservation in '165.0.0.0/8'")
        for i in range(10):
           reserve = {"network":"165.0.0.0/8","network_view":"default","ipv4addr":"165.0.30.1"+str(i),"match_client":"RESERVED"}
           reserve_response = ib_NIOS.wapi_request('POST', object_type="fixedaddress", fields=json.dumps(reserve))

        logger.info("Add shared Network '165.0.0.0/8', 10.0.0.0/8 ")
        shared_network = {"name":"shared_ipv4","networks":[{"_ref":str(network1_ref)},{"_ref":str(network2_ref)}]}
        shared_network_response = ib_NIOS.wapi_request('POST', object_type="sharednetwork", fields=json.dumps(shared_network))

        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(60)
        #############################################################################################################
        for i in range(10):
           fin=os.popen("sudo /import/tools/qa/tools/dras/dras  -n 200 -i "+config.grid_vip)
           logger.info(''.join(fin.readlines()))
           sleep(10)

        logger.info("Add Network '166.10.0.0/16' with Grid master as Member assignment")
        network3 = {"network":"166.10.0.0/16","network_view":"default","members":[{"name":config.grid_fqdn,"_struct": "dhcpmember"}],"options":[{"name": "dhcp-lease-time","value": "74390400"}]}
        network3_response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(network3))
        network3_get = ib_NIOS.wapi_request('GET', object_type="network?network=166.10.0.0/16")
        network3_ref = json.loads(network3_get)[0]['_ref']


        logger.info("Add Range '166.10.0.1-166.10.5.255' in '166.10.0.0/16' with Grid master as Member assignment")
        range1 = {"network":"166.10.0.0/16","network_view":"default","member":{"_struct": "dhcpmember","name":config.grid_fqdn},"start_addr":"166.10.0.1","end_addr":"166.10.5.255"}
        range1_response = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(range1))

        logger.info("Add 10 fixed address in '166.10.0.0/16'")
        for i in range(7):
           fix_addr = {"network":"166.10.0.0/16","network_view":"default","ipv4addr":"166.10.20."+str(i),"mac":"00:00:00:00:10:"+str(i)}
           fix_response = ib_NIOS.wapi_request('POST', object_type="fixedaddress", fields=json.dumps(fix_addr))

        logger.info("Add 10 Reservation in '166.10.0.0/16'")
        for i in range(7):
           reserve = {"network":"166.10.0.0/16","network_view":"default","ipv4addr":"166.10.20.1"+str(i),"match_client":"RESERVED"}
           reserve_response = ib_NIOS.wapi_request('POST', object_type="fixedaddress", fields=json.dumps(reserve))

        logger.info("Modifiy shared Network '166.10.0.0/16', 10.0.0.0/8 ")
        shared_network_get = ib_NIOS.wapi_request('GET', object_type="sharednetwork?name=shared_ipv4")
        shared_network_ref = json.loads(shared_network_get)[0]['_ref']
        shared_network = {"networks":[{"_ref":str(network1_ref)},{"_ref":str(network3_ref)}]}
        shared_network_response = ib_NIOS.wapi_request('PUT', object_type=shared_network_ref, fields=json.dumps(shared_network))

        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(60)
        #############################################################################################################
        for i in range(5):
           fin=os.popen("sudo /import/tools/qa/tools/dras/dras  -n 200 -i"+config.grid_vip)
           logger.info(''.join(fin.readlines()))
           sleep(10)


        logger.info("Add Network '167.1.1.0/24' with Grid master as Member assignment")
        network4 = {"network":"167.1.1.0/24","network_view":"default","members":[{"name":config.grid_fqdn,"_struct": "dhcpmember"}],"options":[{"name": "dhcp-lease-time","value": "74390400"}]}
        network4_response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(network4))
        network4_get = ib_NIOS.wapi_request('GET', object_type="network?network=167.1.1.0/24")
        network4_ref = json.loads(network4_get)[0]['_ref']

        logger.info("Add Range '167.1.1.100-167.1.1.254' in '167.1.1.0/24' with Grid master as Member assignment")
        range3 = {"network":"167.1.1.0/24","network_view":"default","member":{"_struct": "dhcpmember","name":config.grid_fqdn},"start_addr":"167.1.1.100","end_addr":"167.1.1.254"}
        range3_response = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(range3))

        logger.info("Add 10 fixed address in '167.1.1.0/24'")
        for i in range(5):
           fix_addr = {"network":"167.1.1.0/24","network_view":"default","ipv4addr":"167.1.1."+str(i+1),"mac":"00:00:00:00:20:"+str(i)}
           fix_response = ib_NIOS.wapi_request('POST', object_type="fixedaddress", fields=json.dumps(fix_addr))

        logger.info("Add 10 Reservation in '167.1.1.0/24'")
        for i in range(5):
           reserve = {"network":"167.1.1.0/24","network_view":"default","ipv4addr":"167.1.1.2"+str(i),"match_client":"RESERVED"}
           reserve_response = ib_NIOS.wapi_request('POST', object_type="fixedaddress", fields=json.dumps(reserve))

        logger.info("Modifiy shared Network '167.1.1.0/24', 10.0.0.0/8 ")
        shared_network_get = ib_NIOS.wapi_request('GET', object_type="sharednetwork?name=shared_ipv4")
        shared_network_ref = json.loads(shared_network_get)[0]['_ref']
        shared_network = {"networks":[{"_ref":str(network1_ref)},{"_ref":str(network4_ref)}]}
        shared_network_response = ib_NIOS.wapi_request('PUT', object_type=shared_network_ref, fields=json.dumps(shared_network))

        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(60)
        #############################################################################################################

        for i in range(1):
           fin=os.popen("sudo /import/tools/qa/tools/dras/dras  -n 128 -i"+config.grid_vip)
           logger.info(''.join(fin.readlines()))
           sleep(10)

        logger.info("Removed shared Network")
        shared_network_get = ib_NIOS.wapi_request('GET', object_type="sharednetwork?name=shared_ipv4")
        shared_network_ref = json.loads(shared_network_get)[0]['_ref']
        shared_network_del_status = ib_NIOS.wapi_request('DELETE', object_type = shared_network_ref)

        logger.info("Remove 10.0.0.0/8 network")
        network_get = ib_NIOS.wapi_request('GET', object_type="network?network=10.0.0.0/8")
        network_ref = json.loads(network_get)[0]['_ref']
        network_del_status = ib_NIOS.wapi_request('DELETE', object_type = network_ref)

        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(60)
        
        sleep(700)

# Expected Values

# IPAMv4 DEVICE NETWORKS

        #cls.test1=[{"Network":"167.1.1.0","CIDR":"24","Utilization %":"64.9","Total":"256","Assigned":"165" }, {"Network":"165.0.0.0","CIDR":"8","Utilization %":"3.9","Total":"16777216","Assigned":"9853"},{"Network":"166.10.0.0","CIDR":"16","Utilization %":"2.3","Total":"65536","Assigned":"1549"},{"Network":"10.0.0.0","CIDR":"8","Utilization %":"0.0","Total":"16777216","Assigned":"0"}]
        cls.test1 = [{"IPAM Network":"167.1.1.0/24","Utilization %":"64.9"},{"IPAM Network":"166.10.0.0/16","Utilization %":"2.3"},{"IPAM Network":"165.0.0.0/8","Utilization %":"3.9"}]
        logger.info ("Input Json Data for IPAMv4 Device Networks report validation")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))

        logger.info ("Wait 10 minutes for reports to get updated")
        #        time.sleep(700)

        # IPAMv4 NETWORK USAGE STATISTICS

        cls.test2=[{"Network":"167.1.1.0","CIDR":"24","DHCPv4 Utilization %":"6.0","Total":"256","Allocated":"165","Reserved":"2","Assigned":"10","Protocol":"IPV4","Utilization %":"64.9"},{"Network":"166.10.0.0","CIDR":"16","DHCPv4 Utilization %":"0.9","Total":"65536","Allocated":"1549","Reserved":"2","Assigned":"14","Protocol":"IPV4","Utilization %":"2.3"},{"Network":"165.0.0.0","CIDR":"8","DHCPv4 Utilization %":"0.0","Total":"16777216","Allocated":"658175","Reserved":"2","Assigned":"20","Protocol":"IPV4","Utilization %":"3.9"}]
        logger.info ("Input Json Data for IPAMv4 Network Usage Statistics report validation")
        logger.info(json.dumps(cls.test2, sort_keys=True, indent=4, separators=(',', ': ')))

        logger.info ("Wait 10 minutes for reports to get update")
        # time.sleep(700)

        # IPAMv4 NETWORK USAGE TREND

        cls.test3=[{"165.0.0.0/8":"3.9","166.10.0.0/16":"2.3","167.1.1.0/24":"64.9","_span":"300"}]
        logger.info ("Input Json Data for IPAMv4 Network Usage Trend report validation")
        logger.info(json.dumps(cls.test3, sort_keys=True, indent=4, separators=(',', ': ')))

        logger.info ("Wait 10 minutes for reports to get update")
        # time.sleep(700)


        # IPAMv4 TOP UTILISED NETWORKS

        cls.test4=[{"Network":"167.1.1.0","CIDR":"24","Utilization %":"64.9","Total":"256","Assigned":"10","Reserved":"2"},{"Network":"165.0.0.0","CIDR":"8","Utilization %":"3.9","Total":"16777216","Assigned":"20","Reserved":"2"},{"Network":"166.10.0.0","CIDR":"16","Utilization %":"2.3","Total":"65536","Assigned":"14","Reserved":"2"}]
        logger.info ("Input Json Data for IPAMv4 Top Utilised Networks report validation")
        logger.info(json.dumps(cls.test4, sort_keys=True, indent=4, separators=(',', ': ')))

        logger.info ("Wait 10 minutes for reports to get update")
        # time.sleep(700)


        # DHCPv4 TOP UTILISED NETWORKS

        cls.test5=[{"Network":"167.1.1.0","CIDR":"24","DHCPv4 Utilization %":"6.0","Ranges":"1","Provisioned":"165","Dynamic":"0","Static":"10","Free":"155","Used":"10"},{"Network":"166.10.0.0","CIDR":"16","DHCPv4 Utilization %":"0.9","Ranges":"1","Provisioned":"1549","Dynamic":"0","Static":"14","Free":"1535","Used":"14"},{"Network":"165.0.0.0","CIDR":"8","DHCPv4 Utilization %":"0.0","Ranges":"1","Provisioned":"658175","Dynamic":"0","Static":"20","Free":"658155","Used":"20"}]
        logger.info ("Input Json Data for DHCPv4 Top Utilized networks report validation")
        logger.info(json.dumps(cls.test5, sort_keys=True, indent=4, separators=(',', ': ')))

        logger.info ("Wait 10 minutes for reports to get update")
        # time.sleep(700)


    @pytest.mark.run(order=1)
    def test_1(self):
#        import pdb;pdb.set_trace()

        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search source=ib:discovery:switch_port_capacity index=ib_discovery | fillnull value=\"N/A\" | dedup network_view device_ip_address interface_ip_address | join type=inner InterfaceSubnet, network_view [search sourcetype=ib:ipam:network index=ib_ipam | dedup NETWORK, view | rename NETWORK as InterfaceSubnet view as network_view | fields InterfaceSubnet, network_view, allocation] | APPEND [search sourcetype=ib:ipam:network index=ib_ipam | dedup NETWORK, view | rename NETWORK as InterfaceSubnet view as network_view | join type=left InterfaceSubnet, network_view [search source=ib:discovery:switch_port_capacity index=ib_discovery | fields InterfaceSubnet, device_ip_address, network_view] | where isnull(device_ip_address)] | rename InterfaceSubnet as \"IPAM Network\" allocation as \"Utilization %\" device_ip_address as \"Device IP\" interface_ip_address as \"Interface IP\" device_model as \"Device Model\" device_vendor as \"Device Vendor\" device_version as \"Device OS Version\" device_name as \"Device Name\" network_view as \"Network View\" | table \"IPAM Network\", \"Utilization %\", \"Network View\", \"Device IP\", \"Device Name\", \"Interface IP\", \"Device Model\", \"Device Vendor\", \"Device OS Version\""
        print(search_str)
        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        logger.info (cmd)

        print(os.system(cmd))
        print("-------------%%%----------")
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operation failed, Please check Grid Configuration")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        results_dist= results_list[-240::1]
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test1,results_dist)
        logger.info("compare_results with 'delta=1'")
        result = compare_results(self.test1,results_list,1)
        print(result)
        logger.info("-----------------------------------------------------")
        logger.info(self.test1)
        logger.info(len(self.test1))
        logger.info("--------------------shashhhhhhhh-------------------")
        logger.info(results_list)
        logger.info(len(results_list))
        logger.info("-----------------------------------------------------")

        if result == 0:
            print("PASSED")
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg


    @pytest.mark.run(order=2)
    def test_2(self):
#        import pdb;pdb.set_trace()

        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search sourcetype=ib:ipam:network index=ib_ipam | eval dedup_key=view.\"/\".address.\"/\".cidr | dedup dedup_key | eval NETWORK=address.\"/\".cidr | lookup network_ea_lookup_csv NETWORK, NETWORK_VIEW as view output EA | spath input=EA output=MSSITE path=BUILTIN-MSSite | eval MSSITE = if(isnull(MSSITE), \"(no_value)\", MSSITE) | mvexpand MSSITE | eval utilization=round(utilization/10, 1) | mvcombine MSSITE | sort -utilization | rename timestamp as Timestamp, view as \"Network view\", address as Network, cidr as CIDR, MSSITE as \"AD Site\", utilization as \"DHCPv4 Utilization %\", address_total as Total, address_alloc as Allocated, address_reserved as Reserved, address_assigned as Assigned, protocol as Protocol, allocation as \"Utilization %\", address_unmanaged as Unmanaged | table Timestamp, \"Network view\", Network, CIDR, \"AD Site\", \"DHCPv4 Utilization %\", Total, Allocated, Reserved, Assigned, Protocol, \"Utilization %\", Unmanaged"
        print(search_str)
        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        logger.info (cmd)

        print(os.system(cmd))
        print("-------------%%%----------")
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operation failed, Please check Grid Configuration")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        results_dist= results_list[-240::1]
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test2,results_dist)
        logger.info("compare_results with 'delta=1'")
        result = compare_results(self.test2,results_list,1)
        print(result)
        logger.info("-----------------------------------------------------")
        logger.info(self.test2)
        logger.info(len(self.test2))
        logger.info("--------------------shashhhhhhhh-------------------")
        logger.info(results_list)
        logger.info(len(results_list))
        logger.info("-----------------------------------------------------")

        if result == 0:
            print("PASSED")
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg


    @pytest.mark.run(order=3)
    def test_3(self):
#        import pdb;pdb.set_trace()

        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search sourcetype=ib:ipam:network index=ib_ipam | eval NETWORK=address.\"/\".cidr | lookup network_ea_lookup_csv NETWORK, NETWORK_VIEW as view output EA | spath input=EA output=MSSITE path=BUILTIN-MSSite | eval MSSITE = if(isnull(MSSITE), \"(no_value)\", MSSITE) | mvexpand MSSITE | sort -allocation | timechart bins=1000 avg(allocation) as \"Usage %\" by NETWORK useother=f"
        print(search_str)
        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        logger.info (cmd)

        print(os.system(cmd))
        print("-------------%%%----------")
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operation failed, Please check Grid Configuration")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        results_dist= results_list[-240::1]
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test3,results_dist)
        logger.info("compare_results with 'delta=1'")
        result = compare_results(self.test3,results_list,1)
        print(result)
        logger.info("-----------------------------------------------------")
        logger.info(self.test3)
        logger.info(len(self.test3))
        logger.info("--------------------shashhhhhhhh-------------------")
        logger.info(results_list)
        logger.info(len(results_list))
        logger.info("-----------------------------------------------------")

        if result == 0:
            print("PASSED")
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg


    @pytest.mark.run(order=4)
    def test_4(self):
#        import pdb;pdb.set_trace()

        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search sourcetype=ib:ipam:network index=ib_ipam | eval dedup_key=view.\"/\".address.\"/\".cidr | dedup dedup_key | eval NETWORK=address.\"/\".cidr | lookup network_ea_lookup_csv NETWORK, NETWORK_VIEW as view output EA | spath input=EA output=MSSITE path=BUILTIN-MSSite | eval MSSITE = if(isnull(MSSITE), \"(no_value)\", MSSITE) | sort -allocation | head 10 | rename timestamp as Timestamp, view as \"Network view\", address as Network, cidr as CIDR, MSSITE as \"AD Site\", allocation as \"Utilization %\", address_total as Total, address_assigned as Assigned, address_reserved as Reserved, address_unmanaged as Unmanaged | table Timestamp, \"Network view\", Network, CIDR, \"AD Site\", \"Utilization %\", Total, Assigned, Reserved, Unmanaged"
        print(search_str)
        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        logger.info (cmd)

        print(os.system(cmd))
        print("-------------%%%----------")
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operation failed, Please check Grid Configuration")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        results_dist= results_list[-240::1]
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test4,results_dist)
        logger.info("compare_results with 'delta=1'")
        result = compare_results(self.test4,results_list,1)
        print(result)
        logger.info("-----------------------------------------------------")
        logger.info(self.test4)
        logger.info(len(self.test4))
        logger.info("--------------------shashhhhhhhh-------------------")
        logger.info(results_list)
        logger.info(len(results_list))
        logger.info("-----------------------------------------------------")

        if result == 0:
            print("PASSED")
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg


    @pytest.mark.run(order=5)
    def test_5(self):
#        import pdb;pdb.set_trace()

        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search sourcetype=ib:dhcp:network index=ib_dhcp | eval dedup_key=view.\"/\".address.\"/\".cidr | dedup dedup_key | sort 0 -num(dhcp_utilization) | head 10 | eval Free=address_total-dhcp_hosts | rename timestamp as Timestamp, view as \"Network View\", address as Network, cidr as CIDR, dhcp_utilization as \"DHCPv4 Utilization %\", ranges as Ranges, address_total as Provisioned, dhcp_hosts as Used, static_hosts as Static, dynamic_hosts as Dynamic | table Timestamp, \"Network View\", Network, CIDR, \"DHCPv4 Utilization %\", Ranges, Provisioned, Dynamic, Static, Free, Used"
        print(search_str)
        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        logger.info (cmd)

        print(os.system(cmd))
        print("-------------%%%----------")
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operation failed, Please check Grid Configuration")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        results_dist= results_list[-240::1]
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test5,results_dist)
        logger.info("compare_results with 'delta=1'")
        result = compare_results(self.test5,results_list,1)
        print(result)
        logger.info("-----------------------------------------------------")
        logger.info(self.test5)
        logger.info(len(self.test5))
        logger.info("--------------------shashhhhhhhh-------------------")
        logger.info(results_list)
        logger.info(len(results_list))
        logger.info("-----------------------------------------------------")

        if result == 0:
            print("PASSED")
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg


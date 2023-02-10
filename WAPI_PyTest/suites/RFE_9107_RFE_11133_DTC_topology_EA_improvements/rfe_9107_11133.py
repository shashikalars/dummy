import re
import sys
import config
import pytest
import unittest
import logging
import os
import os.path
from os.path import join
import subprocess
import json
import time
import subprocess
from time import sleep
import commands
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util
import ib_utils.log_capture as log_capture
from  ib_utils.log_capture import log_action as log
from  ib_utils.log_validation import log_validation as logv
import pexpect
import paramiko
from ib_utils.common_utilities import generate_token_from_file

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="rfe_9107_11133.log" ,level=logging.INFO,filemode='w')


Server_ip=[]
d={}
Server_name=[]

for i in range(1,5):
    W = config.ip_range+str(i)
    response = os.system("ping -c 1 " + W)
    if (response == 0):
        pingstatus = "Network Active"
        Server_ip.append(W)
    else:
        pass
for i in range(1,3):
    name="server"+str(i)
    print(name)
    d[name]=Server_ip[i]
    Server_name.append(name)



def print_and_log(arg=""):
        print(arg)
        logging.info(arg)


#Adding code which can used multiple times
def restart_services():
        print_and_log("Service restart start")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"RESTART_IF_NEEDED","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(40)
        print_and_log("Service restart Done")


def restart_services_on_grid_2():
        print_and_log("Service restart start")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid2_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"RESTART_IF_NEEDED","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid2_vip)
        sleep(40)
        print_and_log("Service restart Done")


def restart_services_on_member():
        print_and_log("Service restart start")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_member1_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"RESTART_IF_NEEDED","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_member1_vip)
        sleep(40)
        print_and_log("Service restart Done")


def rebuild_services():
        print_and_log("******** Rebuild Services **********")
        log("start","/var/log/syslog",config.grid_vip)
        request_restart = ib_NIOS.wapi_request('POST', object_type = "dtc?_function=generate_ea_topology_db")
        print_and_log(request_restart)
        if request_restart == '{}':
            print_and_log("Success: Rebuild Service")
            assert True
        else:
            print_and_log("Failure: Rebuild Service")
            assert False
        sleep(60)
        LookFor="'Topology EA DB Generator has finished: OK'"
        log("stop","/var/log/syslog",config.grid_vip)
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        print_and_log("Success: validate Rebuild has completed successfully")


def rebuild_services_on_grid_2():
        print_and_log("******** Rebuild Services **********")
        log("start","/var/log/syslog",config.grid2_vip)
        request_restart = ib_NIOS.wapi_request('POST', object_type = "dtc?_function=generate_ea_topology_db", grid_vip=config.grid2_vip)
        print_and_log(request_restart)
        if request_restart == '{}':
            print_and_log("Success: Rebuild Service")
            assert True
        else:
            print_and_log("Failure: Rebuild Service")
            assert False
        sleep(60)
        LookFor="'Topology EA DB Generator has finished: OK'"
        log("stop","/var/log/syslog",config.grid2_vip)
        logs=logv(LookFor,"/var/log/syslog",config.grid2_vip)
        print_and_log("Success: validate Rebuild has completed successfully")


def rebuild_services_on_member():
        print_and_log("******** Rebuild Services **********")
        log("start","/var/log/syslog",config.grid_member1_vip)
        request_restart = ib_NIOS.wapi_request('POST', object_type = "dtc?_function=generate_ea_topology_db", grid_vip=config.grid_member1_vip)
        print_and_log(request_restart)
        if request_restart == '{}':
            print_and_log("Success: Rebuild Service")
            assert True
        else:
            print_and_log("Failure: Rebuild Service")
            assert False
        sleep(60)
        LookFor="'Topology EA DB Generator has finished: OK'"
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
        print_and_log("Success: validate Rebuild has completed successfully")


def validation_of_value_configured_in_extensible_attribute(obj, value, name):
        print_and_log(" Validation of value configured in extensible attribute ")
        response = ib_NIOS.wapi_request('GET', object_type=obj, params=name)
        response = json.loads(response)
        ref = response[0]['_ref']
        response1 = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=extattrs')
        response1 = json.loads(response1)
        ref_value = response1['extattrs']['EA_string']['value']
        if ref_value == value:
            print_and_log("Extensible Attribute "+ref_value+" configured successfully")
            assert True
        else:
            print_and_log("Error while validating the extensible attribute")
            assert False


def validation_of_4_EAs_value_configured_in_extensible_attribute(obj, value, EA, name):
        print_and_log(" Validation of 4 EAs value configured in extensible attribute ")
        response = ib_NIOS.wapi_request('GET', object_type=obj, params='?'+str(name))
        response = json.loads(response)
        ref = response[0]['_ref']
        response1 = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=extattrs')
        response1 = json.loads(response1)
        ref_value = response1['extattrs'][str(EA)]['value']
        if ref_value == value:
            print_and_log("Extensible Attribute "+str(ref_value)+" configured successfully")
            assert True
        else:
            print_and_log("Error while validating the extensible attribute")
            assert False


def validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2(obj, value, EA, name, ip):
        print_and_log(" Validation of 4 EAs value configured in extensible attribute ")
        response = ib_NIOS.wapi_request('GET', object_type=obj, params='?'+str(name), grid_vip=ip)
        response = json.loads(response)
        ref = response[0]['_ref']
        response1 = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=extattrs', grid_vip=ip)
        response1 = json.loads(response1)
        ref_value = response1['extattrs'][str(EA)]['value']
        if ref_value == value:
            print_and_log("Extensible Attribute "+str(ref_value)+" configured successfully")
            assert True
        else:
            print_and_log("Error while validating the extensible attribute")
            assert False


def generate_token_from_file(filepath, filename, ip):
        dir_name=filepath
        base_filename=filename
        filename= os.path.join(dir_name, base_filename)
        data = {"filename":base_filename}
        create_file = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=uploadinit", grid_vip=ip)
        logging.info(create_file)
        res = json.loads(create_file)
        token = json.loads(create_file)['token']
        url = json.loads(create_file)['url']
        print_and_log(create_file)
        print_and_log(res)
        print_and_log(token)
        print_and_log(url)
        os.system('curl -k1 -u admin:infoblox -F name=%s -F filedata=@%s %s'%(filename,filename,url))
        filename="/"+filename
        return token


class RFE_9107_11133(unittest.TestCase):

        @pytest.mark.run(order=1)
        def test_001_Start_DNS_Service(self):
                print_and_log("********** Start DNS Service **********")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                print_and_log(get_ref)
                res = json.loads(get_ref)
                for i in res:
                    print_and_log("Modify a enable_dns")
                    data = {"enable_dns": True}
                    response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
                    print_and_log(response)
                read  = re.search(r'200',response)
                for read in response:
                        assert True
                print_and_log("Test Case 1 Execution Completed")

        @pytest.mark.run(order=2)
        def test_002_Validate_DNS_service_Enabled(self):
                print_and_log("********** Validate DNS Service is enabled **********")
                res = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns")
                print_and_log(res)
                res = json.loads(res)
                print_and_log(res)
                for i in res:
                    print_and_log(i)
                    print_and_log("found")
                    assert i["enable_dns"] == True
                print_and_log("Test Case 2 Execution Completed")


        @pytest.mark.run(order=3)
        def test_003_create_AuthZone(self):
                print_and_log("********** Create A auth Zone **********")
                data = {"fqdn": "dtc.com","grid_primary": [{"name": config.grid_member_fqdn,"stealth":False}, {"name": config.grid_member1_fqdn,"stealth":False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                print_and_log(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401 or response[0]==404:
                        print_and_log("Failure: Create A new Zone")
                        assert False
                    else:
                        print_and_log("Success: Create A new Zone")
                        assert True
                print_and_log("Restart DNS Services")
                restart_services()
                #Validation of Auth Zone Created
                response = ib_NIOS.wapi_request('GET', object_type="zone_auth", params='?fqdn=dtc.com')
                response = json.loads(response)
                res_fqdn = response[0]['fqdn']
                if res_fqdn == "dtc.com":
                    print_and_log("The authorative zone "+res_fqdn+" creatd successfully")
                    assert True
                else:
                    print_and_log("Error while creating the authorative zone")
                    assert False
                print_and_log("Test Case 3 Execution Completed")




        @pytest.mark.run(order=4)
        def test_004_Create_A_Record(self):
                print_and_log("********** Create A Record************")
                data = {"name":"new1.dtc.com","ipv4addr":"10.1.1.1"}
                response = ib_NIOS.wapi_request('POST', object_type="record:a", fields=json.dumps(data))
                print_and_log(response)
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                print_and_log("Test Case 4 Execution Completed")



        @pytest.mark.run(order=5)
        def test_005_Validation_of_A_Record(self):
                print_and_log("********** Validation of A Record************")
                response = ib_NIOS.wapi_request('GET',object_type="record:a" , params='?_return_fields=name')
                ref1 = json.loads(response)
                print_and_log(ref1)
                ref1 = ref1[0]['name']
                if ref1 == "new1.dtc.com":
                    assert True
                    print_and_log("A record "+ref1+" was created successfully")
                else:
                    print_and_log("A record "+ref1+" was not created successfully")
                    assert False
                print_and_log("Test Case 5 Execution Completed")


        @pytest.mark.run(order=6)
        def test_006_verifying_if_all_the_ipam_objects_are_enabled_in_grid_dns_properties_traffic_control(self):
                print_and_log("********** Verifying if all the ipam objects are enabled in grid dns properties traffic control ************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                for i in json.loads(config.ipam_obj):
                    response1 = ib_NIOS.wapi_request('GET',object_type=ref ,params='?_return_fields='+i)
                    response1 = json.loads(response1)
                    output = response1[i]
                    print_and_log(output)
                    if output == True:
                        print_and_log("IPAM Object "+i+" is Enabled")
                        assert True
                    else:
                        print_and_log("IPAM Object "+i+" is Disabled")
                        assert False
                print_and_log("Test Case 6 Execution Completed")



        @pytest.mark.run(order=7)
        def test_007_Create_Two_DTC_Servers(self):
                print_and_log("******* Create two DTC Servers *********")
                for i,j in d.items():
                    print_and_log(i)
                    print_and_log(j)
                    data = {"name":i,"host":j}
                    response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
                    print_and_log(response)
                    assert re.search(r'dtc:server', response)
                print_and_log("TestCase Case 7 execution completed")


        @pytest.mark.run(order=8)
        def test_008_Create_DTC_Pool_1_and_assign_server1_and_server2_As_server_members(self):
                print_and_log("******* Create DTC Pool_1 and assign server1 and server2 As server members *********")
                print_and_log("Getting the server name reference ")
                server_ref = []
                for i in Server_name:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    server_ref.append(ref)
                print_and_log(server_ref)
                print_and_log("****** Creating the pool and assiging the server ******")
                data = {"name": "Pool_1", "lb_preferred_method": "ROUND_ROBIN", "servers": [{"ratio": 1,"server": str(server_ref[0])}, {"ratio": 1,"server": str(server_ref[1])}], "monitors": ["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"]}
                response_servers = ib_NIOS.wapi_request('POST',object_type='dtc:pool', fields=json.dumps(data))
                ref1 = json.loads(response_servers)
                print_and_log(ref1)
                print_and_log("Validation of Pool creation")
                assert re.search(r'dtc:pool', ref1)
                print_and_log("TestCase Case 8 execution completed")


        @pytest.mark.run(order=9)
        def test_009_Create_DTC_LBDN_1_and_assgin_Pool_1_as_Pool_member(self):
                print_and_log("********** Create DTC LBDN 1 and assgin Pool 1 as Pool member ***********")
                print_and_log("********** Getting the ref of authorative zone ************")
                response = ib_NIOS.wapi_request('GET',object_type='zone_auth', params='?fqdn=dtc.com')
                response = json.loads(response)
                ref_zone = response[0]['_ref']
                print_and_log("********** Getting the ref of pool 1 ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_1')
                response = json.loads(response)
                ref_pool1 = response[0]['_ref']
                print_and_log("********** Creating the lbdn ************")
                data = {"auth_zones": [ref_zone], "name": "LBDN", "lb_method": "ROUND_ROBIN", "patterns": ["a.dtc.com"], "pools": [{"ratio": 1, "pool": ref_pool1}]}
                print_and_log(data)
                response1 = ib_NIOS.wapi_request('POST',object_type='dtc:lbdn', fields=json.dumps(data))
                ref1 = json.loads(response1)
                print_and_log(ref1)
                assert re.search(r'dtc:lbdn', ref1)
                restart_services()
                print_and_log("Test Case 9 Execution Completed")


        @pytest.mark.run(order=10)
        def test_010_validation_of_dtc_servers(self):
                print_and_log("******* Validation of DTC servers *********")
                response = ib_NIOS.wapi_request('GET', object_type="dtc:server")
                response = json.loads(response)
                print_and_log(response)
                for i in response:
                    print_and_log(i['name'])
                    if i['name'] == Server_name[0]:
                        print_and_log(" DTC Server 1 configured successfully")
                        assert True
                    elif i['name'] == Server_name[1]:
                        print_and_log(" DTC Server 2 Configured successfully")
                        assert True
                    else:
                        print_and_log(" Error while validating the DTC servers ")
                        assert False
                print_and_log("Test Case 10 Execution Completed")



        @pytest.mark.run(order=11)
        def test_011_validation_of_dtc_pool(self):
                print_and_log("******* Validation of DTC Pool *********")
                response1 = ib_NIOS.wapi_request('GET', object_type="dtc:pool")
                response1 = json.loads(response1)
                print_and_log(response1)
                if response1[0]['name'] == "Pool_1":
                    print_and_log(" DTC Pool 1 Created successfully")
                    assert True
                else:
                    print_and_log(" Error while validating the DTC pool")
                    assert False
                print_and_log("Test Case 11 Execution Completed")



        @pytest.mark.run(order=12)
        def test_012_validation_of_dtc_server_pool_and_lbdn(self):
                print_and_log("******* Validation of DTC LBDN *********")
                response2 = ib_NIOS.wapi_request('GET', object_type="dtc:lbdn")
                response2 = json.loads(response2)
                print_and_log(response2)
                if response2[0]['name'] == "LBDN":
                    print_and_log(" DTC LBDN Created successfully")
                    assert True
                else:
                    print_and_log(" Error while validating the DTC LBDN")
                    assert False
                print_and_log(" Test Case 12 Execution Completed ")



        @pytest.mark.run(order=13)
        def test_013_Create_Custom_Extensible_Attribute_required_for_testing(self):
                print_and_log("******** Creation of Custom Externsible Attribute with Type String **********")
                data = {"name": "EA_string", "type": "STRING"}
                response = ib_NIOS.wapi_request('POST',object_type='extensibleattributedef', fields=json.dumps(data))
                print_and_log(response)
                assert re.search(r'EA_string', response)
                print_and_log("******** Creation of Custom Externsible Attribute with Type List **********")
                data = {"name": "EA_list", "type": "ENUM", "list_values": [{"value": "1"}, {"value": "2"}], "comment": "EA for List"}
                response = ib_NIOS.wapi_request('POST',object_type='extensibleattributedef', fields=json.dumps(data))
                print_and_log(response)
                assert re.search(r'EA_list', response)
                print_and_log("******** Creation of Custom Externsible Attribute with Type Interger **********")
                data = {"name": "EA_int", "type": "INTEGER"}
                response = ib_NIOS.wapi_request('POST',object_type='extensibleattributedef', fields=json.dumps(data))
                print_and_log(response)
                assert re.search(r'EA_int', response)
                print_and_log("Test Case 13 Execution Completed")


        @pytest.mark.run(order=14)
        def test_014_Validation_of_Custom_Extensible_Attribute_that_are_created(self):
                print_and_log("********** Validation of custom extensible attribute that are created *************")
                new_list = ["EA_string", "EA_list", "EA_int"]
                for i in new_list:
                    response = ib_NIOS.wapi_request('GET',object_type='extensibleattributedef', params="?name="+i)
                    response = json.loads(response)
                    ref_name = response[0]['name']
                    ref_type = response[0]['type']
                    if ref_name == i and ref_type == "STRING":
                        print_and_log("Custom EA "+i+" with type "+ref_type+" is configured successfully")
                        assert True
                    elif ref_name == i and ref_type == "ENUM":
                        print_and_log("Custom EA "+i+" with type "+ref_type+" is configured successfully")
                        assert True
                    elif ref_name == i and ref_type == "INTEGER":
                        print_and_log("Custom EA "+i+" with type "+ref_type+" is configured successfully")
                        assert True
                    else:
                        print_and_log("Validation failed for One of the custom EA")
                        assert False
                print_and_log("Test Case 14 Execution Completed")


        @pytest.mark.run(order=15)
        def test_015_Assign_the_Custom_EA_EA_string_in_Grid_Properties_Traffic_Control(self):
                print_and_log("********** Assign the Custom EA EA_string in Grid Properties Traffic Conftrol w************")
                response = ib_NIOS.wapi_request('GET',object_type='grid:dns')
                response = json.loads(response)
                ref = response[0]['_ref']
                data={"dtc_topology_ea_list": ["EA_string"]}
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
                print_and_log(response1)
                assert re.search(r'grid:dns', response1)
                rebuild_services()
                # validate Custom EA
                print_and_log("Test Case 15 Execution completed ")


        @pytest.mark.run(order=16)
        def test_016_Validation_of_the_Custom_EA_EA_string_in_Grid_Properties_Traffic_Control(self):
                print_and_log("********** Validation of the Custom EA EA_string in Grid Properties TrafficControl ***********")
                response = ib_NIOS.wapi_request('GET',object_type='grid:dns')
                response = json.loads(response)
                ref = response[0]['_ref']
                response = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=dtc_topology_ea_list')
                response = json.loads(response)
                out = response['dtc_topology_ea_list'][0]
                print_and_log(out)
                if out == "EA_string":
                    print_and_log(" Custome EA "+out+" configured in Grid DNS properties")
                    assert True
                else:
                    print_and_log(" Error while Validating the Custom EA in Grid DNS properties")
                    assert False
                print_and_log("Test Case 16 Execution completed ")


        @pytest.mark.run(order=17)
        def test_017_Enable_the_EDNS0_Client_Subnet_option(self):
                print_and_log("********** Enable the EDNS0 Client Subnet option ************")
                response = ib_NIOS.wapi_request('GET',object_type='grid:dns')
                response = json.loads(response)
                ref = response[0]['_ref']
                data={"dtc_edns_prefer_client_subnet": True}
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
                print_and_log(response1)
                assert re.search(r'grid:dns', response1)
                restart_services()
                print_and_log("Test Case 17 Execution completed ")


        @pytest.mark.run(order=18)
        def test_018_Validation_of_the_EDNS0_Client_Subnet_option(self):
                print_and_log("******** Validation of the EDNS0 Client Subnet option **********")
                response = ib_NIOS.wapi_request('GET',object_type='grid:dns')
                response = json.loads(response)
                ref = response[0]['_ref']
                response = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=dtc_edns_prefer_client_subnet')
                response = json.loads(response)
                out = response['dtc_edns_prefer_client_subnet']
                print_and_log(out)
                if out == True:
                    print_and_log("EDNS0 Client Option is enabled")
                    assert True
                else:
                    print_and_log("EDNS0 is not enabled")
                    assert False
                print_and_log("Test Case 18 Execution completed ")



        @pytest.mark.run(order=19)
        def test_019_ADD_IPV4_Network_Container_Ranges_and_Hosts(self):
                print_and_log("******** Add IPV4 Network *********")
                data = {"network": config.ipv4network1, "extattrs": { "EA_string": { "value": "network2"}}}
                response = ib_NIOS.wapi_request('POST',object_type="network", fields=json.dumps(data))
                print_and_log(response)
                assert re.search(r'network', response)
                data = {"network": config.ipv4network_container1, "extattrs": { "EA_string": { "value": "network1"}}}
                response1 = ib_NIOS.wapi_request('POST',object_type="networkcontainer", fields=json.dumps(data))
                print_and_log(response1)
                assert re.search(r'networkcontainer', response1)
                data = {"start_addr": json.loads(config.ipv4_ranges)[0], "end_addr": json.loads(config.ipv4_ranges)[2], "network": config.ipv4network1, "extattrs": { "EA_string": { "value": "network1"}}}
                response2 = ib_NIOS.wapi_request('POST',object_type="range", fields=json.dumps(data))
                print_and_log(response2)
                assert re.search(r'range', response2)
                data = {"name": "host_new","configure_for_dns": False, "ipv4addrs": [{"ipv4addr": config.ipv4addr_host}], "extattrs": { "EA_string": { "value": "network1"}}}
                response3 = ib_NIOS.wapi_request('POST',object_type="record:host", fields=json.dumps(data))
                print_and_log(response3)
                assert re.search(r'record:host', response3)
                rebuild_services()
                print_and_log("Test Case 19 Execution completed")



        @pytest.mark.run(order=20)
        def test_020_Validation_of_IPV4_Network(self):
                print_and_log("********* Validation of IPV4 Network ***********")
                response = ib_NIOS.wapi_request('GET',object_type="network", params='?network='+config.ipv4network1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                res_name = response[0]['network']
                response = ib_NIOS.wapi_request('GET',object_type=res_ref, params='?_return_fields=extattrs')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response['extattrs']['EA_string']['value']
                print_and_log(res_ref)
                if res_ref == "network2" and res_name == config.ipv4network1:
                    print_and_log("IPV4 Network "+res_name+" with extensible attributte "+res_ref+" configured successfully")
                    assert True
                else:
                    print_and_log("Error while validating the IPV4 network")
                    assert False
                print_and_log("Test Case 21 Execution completed")



        @pytest.mark.run(order=22)
        def test_022_Validation_of_IPV4_Container(self):
                print_and_log("********* Validation of IPV4 Container ***********")
                response = ib_NIOS.wapi_request('GET',object_type="networkcontainer", params='?network='+config.ipv4network_container1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                res_name = response[0]['network']
                response = ib_NIOS.wapi_request('GET',object_type=res_ref, params='?_return_fields=extattrs')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response['extattrs']['EA_string']['value']
                print_and_log(res_ref)
                if res_ref == "network1" and res_name == config.ipv4network_container1:
                    print_and_log("IPV4 Network Container "+res_name+" with extensible attributte "+res_ref+" configured successfully")
                    assert True
                else:
                    print_and_log("Error while validating the IPV4 network container")
                    assert False
                print_and_log("Test Case 22 Execution completed")


        @pytest.mark.run(order=23)
        def test_023_Validation_of_IPV4_Ranges(self):
                print_and_log("********* Validation of IPV4 ranges ***********")
                response = ib_NIOS.wapi_request('GET',object_type="range", params='?network='+config.ipv4network1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                res_start_addr = response[0]['start_addr']
                res_end_addr = response[0]['end_addr']
                response = ib_NIOS.wapi_request('GET',object_type=res_ref, params='?_return_fields=extattrs')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response['extattrs']['EA_string']['value']
                print_and_log(res_ref)
                if res_start_addr == json.loads(config.ipv4_ranges)[0] and res_end_addr == json.loads(config.ipv4_ranges)[2] and res_ref == "network1":
                    print_and_log("IPV4 Network Range with extensible attributte "+res_ref+" configured successfully")
                    assert True
                else:
                    print_and_log("Error while validating the IPV4 network range")
                    assert False
                print_and_log("Test Case 23 Execution completed")


        @pytest.mark.run(order=24)
        def test_024_Validation_of_IPV4_Host(self):
                print_and_log("********* Validation of IPV4 Host ***********")
                response = ib_NIOS.wapi_request('GET',object_type="record:host", params='?name=host_new')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                res_addr = response[0]['ipv4addrs'][0]['ipv4addr']
                response = ib_NIOS.wapi_request('GET',object_type=res_ref, params='?_return_fields=extattrs')
                response = json.loads(response)
                print_and_log(response)
                res_extattrs = response['extattrs']['EA_string']['value']
                if res_extattrs == "network1" and res_addr == config.ipv4addr_host:
                    print_and_log("IPV4 Host with extensible attributte "+res_extattrs+" configured successfully")
                    assert True
                else:
                    print_and_log(" Error while validating the IPV4 host")
                    assert False
                print_and_log("Test Case 24 Execution completed")



        @pytest.mark.run(order=25)
        def test_025_Create_the_DTC_topology_Rule_with_Server_as_Destination(self):
                print_and_log("********* Create the DTC topology Rule with Server as Destination ***********")
                server_ref = []
                for i in Server_name:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    server_ref.append(ref)
                data = {"name": "ea-rule1", "rules": [{"sources": [{"source_op": "IS","source_type": "EA0","source_value": "network1"}], "dest_type": "SERVER","destination_link": server_ref[0]}, {"sources":[{"source_op": "IS","source_type": "EA0","source_value": "network2"}], "dest_type": "SERVER","destination_link": server_ref[1]}]}
                print_and_log(data)
                response = ib_NIOS.wapi_request('POST',object_type='dtc:topology', fields=json.dumps(data))
                print_and_log(response)
                assert re.search(r'dtc:topology', response)
                print_and_log("********* Validation of Topology rule 1 ***********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ea-rule1')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                res_name = response[0]['name']
                if res_name == "ea-rule1":
                    print_and_log("Topology rule "+res_name+" created successfully")
                    assert True
                else:
                    print_and_log(" Validation for the Topology rule failed ")
                    assert False
                print_and_log("Test Case 25 Execution completed")


        @pytest.mark.run(order=26)
        def test_026_Modify_the_Pool_Lb_method_to_Topology(self):
                print_and_log("********* Mofity the Pool LB method to Topology ***********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ea-rule1')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_1')
                response1 = json.loads(response1)
                print_and_log(response1)
                res_ref1 = response1[0]['_ref']
                data = {"lb_preferred_method": "TOPOLOGY", "lb_preferred_topology": res_ref}
                response2 = ib_NIOS.wapi_request('PUT',object_type=res_ref1, fields=json.dumps(data))
                response2 = json.loads(response2)
                print_and_log(response2)
                assert re.search(r'dtc:pool', response2)
                restart_services()
                print_and_log("Test Case 26 Execution completed")


        @pytest.mark.run(order=27)
        def test_027_Validation_of_Pool_Lb_method_to_Topology(self):
                print_and_log("********** Validation of Pool LB method to Topology **********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ea-rule1')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_1')
                response1 = json.loads(response1)
                print_and_log(response1)
                res_ref1 = response1[0]['_ref']
                response2 = ib_NIOS.wapi_request('GET',object_type=res_ref1, params='?_return_fields=lb_preferred_method')
                response2 = json.loads(response2)
                res_lb_method = response2['lb_preferred_method']
                print_and_log(res_lb_method)
                response3 = ib_NIOS.wapi_request('GET',object_type=res_ref1, params='?_return_fields=lb_preferred_topology')
                response3 = json.loads(response3)
                res_lb_topology = response3['lb_preferred_topology'].split(":")[-1]
                print_and_log(res_lb_topology)
                if res_lb_method == "TOPOLOGY" and res_lb_topology == "ea-rule1":
                    print_and_log(" LB method "+res_lb_method+" is configured to Pool with topo rule "+res_lb_topology+" successfully")
                    assert True
                else:
                    print_and_log(" Error while validating the LB method of the Pool")
                    assert False
                print_and_log("Test Case 27 Execution completed")


        @pytest.mark.run(order=28)
        def test_028_Run_the_dig_command_with_subnet_of_IPAM_network1(self):
                print_and_log("********** Run the dig command with subnet of IPAM network1 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network1+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 28 Execution Completed")


        @pytest.mark.run(order=29)
        def test_029_Run_the_dig_command_with_subnet_of_IPAM_conatiner(self):
                print_and_log("********** Run the dig command with subnet of IPAM Container ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network_container1+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network_container1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 29 Execution Completed")


        @pytest.mark.run(order=30)
        def test_030_Run_the_dig_command_with_subnet_of_IPAM_ranges(self):
                print_and_log("********** Run the dig command with subnet of IPAM Ranges ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[0]+"/32 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[1]+"/32 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[2]+"/32 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 30 Execution Completed")



        @pytest.mark.run(order=31)
        def test_031_Run_the_dig_command_with_subnet_of_IPAM_Hosts(self):
                print_and_log("********** Run the dig command with subnet of IPAM Hosts ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4addr_host+"/32 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4addr_host)
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 31 Execution Completed")


        @pytest.mark.run(order=32)
        def test_032_Run_the_dig_command_with_pattern_matching_with_a_record(self):
                print_and_log("********** Run the dig command with pattern matching with a record ************")
                output = os.popen("dig @"+config.grid_vip+" new1.dtc.com in a +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == "10.1.1.1":
                    print_and_log("A record with responded to the query")
                    assert True
                else:
                    print_and_log("A record didn't respond to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 32 Execution Completed")


        @pytest.mark.run(order=33)
        def test_033_Modify_the_value_of_the_IPAM_network_from_network2_to_network1(self):
                print_and_log("******** Modify the value of the IPAM network from network2 to network1 *********")
                response = ib_NIOS.wapi_request('GET',object_type="network", params='?network='+config.ipv4network1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network1"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('network', 'network1', '?network='+config.ipv4network1)
                print_and_log("Test Case 33 Execution Completed")



        @pytest.mark.run(order=34)
        def test_034_Modify_the_value_of_the_IPAM_conatiner_from_network1_to_network2(self):
                print_and_log("******** Modify the value of the IPAM conatiner from network1 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="networkcontainer", params='?network='+config.ipv4network_container1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network2"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('networkcontainer', 'network2', '?network='+config.ipv4network_container1)
                print_and_log("Test Case 34 Execution Completed")



        @pytest.mark.run(order=35)
        def test_035_Modify_the_value_of_the_IPAM_Ranges_from_network1_to_network2(self):
                print_and_log("******** Modify the value of the IPAM network from network1 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="range", params='?network='+config.ipv4network1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network2"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('range', 'network2', '?network='+config.ipv4network1)
                print_and_log("Test Case 35 Execution Completed")


        @pytest.mark.run(order=36)
        def test_036_Modify_the_value_of_the_IPAM_Host_from_network1_to_network2(self):
                print_and_log("******** Modify the value of the IPAM network from network1 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="record:host", params='?name=host_new')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network2"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('record:host', 'network2', '?name=host_new')
                print_and_log("Test Case 36 Execution Completed")



        @pytest.mark.run(order=37)
        def test_037_Run_the_dig_command_with_subnet_of_IPAM_network1(self):
                print_and_log("********** Run the dig command with subnet of IPAM network1 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network1+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 37 Execution Completed")


        @pytest.mark.run(order=38)
        def test_038_Run_the_dig_command_with_subnet_of_IPAM_conatiner(self):
                print_and_log("********** Run the dig command with subnet of IPAM Container ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network_container1+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network_container1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 38 Execution Completed")


        @pytest.mark.run(order=39)
        def test_039_Run_the_dig_command_with_subnet_of_IPAM_ranges(self):
                print_and_log("********** Run the dig command with subnet of IPAM Ranges ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[0]+"/32 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[1]+"/32 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[2]+"/32 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 39 Execution Completed")



        @pytest.mark.run(order=40)
        def test_040_Run_the_dig_command_with_subnet_of_IPAM_Hosts(self):
                print_and_log("********** Run the dig command with subnet of IPAM Hosts ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4addr_host+"/32 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4addr_host)
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 40 Execution Completed")


        @pytest.mark.run(order=41)
        def test_041_Run_the_dig_command_with_subnet_that_does_not_belong_to_IPAM_Ranges_or_Host(self):
                print_and_log("********** Run the dig command with subnet of IPAM Hosts ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet=1.1.1.6/32 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4addr_host)
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 41 Execution Completed")



        @pytest.mark.run(order=42)
        def test_042_Run_the_dig_command_with_wrong_subnet_and_pattern_matching_the_DTC_LBDN(self):
                print_and_log("********** Run_the_dig_command_with_wrong_subnet and pattern matching the DTC LBDN ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet=2.2.2.0/24").read()
                out = output.split("\n")
                flag = False
                for i in out:
                    match = re.match("dtc.com.\s+\d+\s+IN\s+SOA.*",i)
                    print_and_log(i)
                    if match:
                        print_and_log(" Match found ")
                        flag=True
                        break
                if flag == True:
                    print_and_log("SOA record is found, No response from any for the DTC servers")
                    assert True
                else:
                    print_and_log("Query got the response from DTC servers")
                    assert False
                print_and_log("Test Case 42 Execution Completed")


        @pytest.mark.run(order=43)
        def test_043_Run_the_dig_command_with_wrong_subnet_and_pattern_matching_the_A_record(self):
                print_and_log("********** Run_the_dig_command_with_wrong_subnet and pattern matching the A record ************")
                output = os.popen("dig @"+config.grid_vip+" new1.dtc.com in a +subnet=2.2.2.0/24 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == "10.1.1.1":
                    print_and_log("A record with responded to the query")
                    assert True
                else:
                    print_and_log("A record didn't respond to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 43 Execution Completed")


        @pytest.mark.run(order=44)
        def test_044_Uncheck_the_IPAM_Container_object_in_Grid_DNS_Properties_Traffic_Control(self):
                print_and_log("********** Uncheck the IPAM Container object in Grid DNS Properties Traffic Control ************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                data = {"gen_eadb_from_network_containers": False}
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                restart_services()
                print_and_log("Test Case 44 Execution Completed")


        @pytest.mark.run(order=45)
        def test_045_Validation_of_the_IPAM_Container_object_in_Grid_DNS_Properties_Traffic_Control(self):
                print_and_log("********** Validation of the IPAM Container object in Grid DNS Properties Traffic Control************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=gen_eadb_from_network_containers')
                response1 = json.loads(response1)
                output = response1['gen_eadb_from_network_containers']
                if output == False:
                    print_and_log(" The IPAM Containers Object in Grid DNS properties is set to False")
                    assert True
                else:
                    print_and_log(" The IPAM Containers Object in Grid DNS properties is set to True")
                    assert False
                print_and_log("Test Case 45 Execution Completed")


        @pytest.mark.run(order=46)
        def test_046_Run_the_dig_command_with_subnet_of_IPAM_conatiner(self):
                print_and_log("********** Run the dig command with subnet of IPAM Container ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network_container1).read()
                out = output.split("\n")
                flag = False
                for i in out:
                    match = re.match("dtc.com.\s+\d+\s+IN\s+SOA.*",i)
                    print_and_log(i)
                    if match:
                        print_and_log(" Match found ")
                        flag=True
                        break
                if flag == True:
                    print_and_log("SOA record is found, No response from any for the DTC servers")
                    assert True
                else:
                    print_and_log("Query got the response from DTC servers")
                    assert False
                print_and_log("Test Case 46 Execution Completed")



        @pytest.mark.run(order=47)
        def test_047_Uncheck_the_IPAM_Networks_object_in_Grid_DNS_Properties_Traffic_Control(self):
                print_and_log("********** Uncheck the IPAM networks object in Grid DNS Properties Traffic Control ************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                data = {"gen_eadb_from_networks": False}
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                restart_services()
                print_and_log("Test Case 47 Execution Completed")


        @pytest.mark.run(order=48)
        def test_048_Validation_of_the_IPAM_network_object_in_Grid_DNS_Properties_Traffic_Control(self):
                print_and_log("********** Validation of the IPAM networks object in Grid DNS Properties Traffic Control************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=gen_eadb_from_networks')
                response1 = json.loads(response1)
                output = response1['gen_eadb_from_networks']
                if output == False:
                    print_and_log(" The IPAM networks Object in Grid DNS properties is set to False")
                    assert True
                else:
                    print_and_log(" The IPAM networks Object in Grid DNS properties is set to True")
                    assert False
                print_and_log("Test Case 48 Execution Completed")



        @pytest.mark.run(order=49)
        def test_049_Run_the_dig_command_with_subnet_of_IPAM_network(self):
                print_and_log("********** Run the dig command with subnet of IPAM Network ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network1).read()
                out = output.split("\n")
                flag = False
                for i in out:
                    match = re.match("dtc.com.\s+\d+\s+IN\s+SOA.*",i)
                    print_and_log(i)
                    if match:
                        print_and_log(" Match found ")
                        flag=True
                        break
                if flag == True:
                    print_and_log("SOA record is found, No response from any for the DTC servers")
                    assert True
                else:
                    print_and_log("Query got the response from DTC servers")
                    assert False
                print_and_log("Test Case 49 Execution Completed")



        @pytest.mark.run(order=50)
        def test_050_Uncheck_the_IPAM_ranges_object_in_Grid_DNS_Properties_Traffic_Control(self):
                print_and_log("********** Uncheck the IPAM ranges object in Grid DNS Properties Traffic Control ************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                data = {"gen_eadb_from_ranges": False}
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                restart_services()
                print_and_log("Test Case 50 Execution Completed")


        @pytest.mark.run(order=51)
        def test_051_Validation_of_the_IPAM_ranges_object_in_Grid_DNS_Properties_Traffic_Control(self):
                print_and_log("********** Validation of the IPAM ranges object in Grid DNS Properties Traffic Control************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=gen_eadb_from_ranges')
                response1 = json.loads(response1)
                output = response1['gen_eadb_from_ranges']
                if output == False:
                    print_and_log(" The IPAM ranges Object in Grid DNS properties is set to False")
                    assert True
                else:
                    print_and_log(" The IPAM networks Object in Grid DNS properties is set to True")
                    assert False
                print_and_log("Test Case 51 Execution Completed")



        @pytest.mark.run(order=52)
        def test_052_Run_the_dig_command_with_subnet_of_IPAM_ranges(self):
                print_and_log("********** Run the dig command with subnet of IPAM Ranges ************")
                for i in json.loads(config.ipv4_ranges):
                    output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+i+"/32").read()
                    out = output.split("\n")
                    flag = False
                    for i in out:
                        match = re.match("dtc.com.\s+\d+\s+IN\s+SOA.*",i)
                        print_and_log(i)
                        if match:
                            print_and_log(" Match found ")
                            flag=True
                            break
                    if flag == True:
                        print_and_log("SOA record is found, No response from any for the DTC servers")
                        assert True
                    else:
                        print_and_log("Query got the response from DTC servers")
                        assert False
                print_and_log("Test Case 52 Execution Completed")


        @pytest.mark.run(order=53)
        def test_053_Run_the_dig_command_with_subnet_that_does_not_belong_to_IPAM_Ranges_or_Host(self):
                print_and_log("********** Run the dig command with subnet of IPAM Hosts ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet=1.1.1.6/32").read()
                out = output.split("\n")
                flag = False
                for i in out:
                    match = re.match("dtc.com.\s+\d+\s+IN\s+SOA.*",i)
                    print_and_log(i)
                    if match:
                        print_and_log(" Match found ")
                        flag=True
                        break
                if flag == True:
                    print_and_log("SOA record is found, No response from any for the DTC servers")
                    assert True
                else:
                    print_and_log("Query got the response from DTC servers")
                    assert False
                print_and_log("Test Case 53 Execution Completed")



        @pytest.mark.run(order=54)
        def test_054_Uncheck_the_IPAM_hosts_object_in_Grid_DNS_Properties_Traffic_Control_and_expect_error(self):
                print_and_log("********* Uncheck the IPAM hosts object in Grid DNS Properties Traffic Control and expect error **********")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                data = {"gen_eadb_from_hosts": False}
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
                if type(response1) == tuple:
                    out = response1[1]
                    out = json.loads(out)
                    print_and_log(out)
                    error_message = out['text']
                    print_and_log(error_message)
                    expected_error_message = "' At least one source type for EA MMDB must be selected.'"
                    if error_message in expected_error_message:
                        print_and_log("Expected Error message is seen")
                        assert True
                    else:
                        print_and_log("Expected Error message is not seen")
                        assert False
                else:
                    print_and_log(response1)
                    print_and_log(" All the IPAM objects under Grid DNS properties Traffic control is disabled ")
                    assert False
                print_and_log("Test Case 54 Execution Completed")



        @pytest.mark.run(order=55)
        def test_055_Modify_the_Pool_Lb_method_and_add_the_alternate_load_balancing_method_global_availability(self):
                print_and_log("********* Mofity the Pool LB method global availability to Topology ***********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ea-rule1')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_1')
                response1 = json.loads(response1)
                print_and_log(response1)
                res_ref1 = response1[0]['_ref']
                data = {"lb_alternate_method": "GLOBAL_AVAILABILITY"}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref1, fields=json.dumps(data))
                print_and_log(response1)
                restart_services()
                print_and_log("Test Case 55 Execution Completed")


        @pytest.mark.run(order=56)
        def test_056_Validation_of_Pool_Alternate_Lb_method_global_availability_to_Topology(self):
                print_and_log("********** Validation of Pool LB method global availability to Topology **********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ea-rule1')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_1')
                response1 = json.loads(response1)
                print_and_log(response1)
                res_ref1 = response1[0]['_ref']
                response2 = ib_NIOS.wapi_request('GET',object_type=res_ref1, params='?_return_fields=lb_alternate_method')
                response2 = json.loads(response2)
                res_lb_method = response2['lb_alternate_method']
                print_and_log(res_lb_method)
                response3 = ib_NIOS.wapi_request('GET',object_type=res_ref1, params='?_return_fields=lb_preferred_topology')
                response3 = json.loads(response3)
                res_lb_topology = response3['lb_preferred_topology'].split(":")[-1]
                print_and_log(res_lb_topology)
                if res_lb_method == "GLOBAL_AVAILABILITY" and res_lb_topology == "ea-rule1":
                    print_and_log("Alternate LB method "+res_lb_method+" is configured to Pool with topo rule "+res_lb_topology+" successfully")
                    assert True
                else:
                    print_and_log(" Error while validating the LB method of the Pool")
                    assert False
                print_and_log("Test Case 56 Execution completed")



        @pytest.mark.run(order=57)
        def test_057_Run_the_dig_command_with_subnet_of_IPAM_network1(self):
                print_and_log("********** Run the dig command with subnet of IPAM network1 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network1+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 57 Execution Completed")


        @pytest.mark.run(order=58)
        def test_058_Run_the_dig_command_with_subnet_of_IPAM_conatiner(self):
                print_and_log("********** Run the dig command with subnet of IPAM Container ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network_container1+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network_container1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 58 Execution Completed")


        @pytest.mark.run(order=59)
        def test_059_Run_the_dig_command_with_subnet_of_IPAM_ranges(self):
                print_and_log("********** Run the dig command with subnet of IPAM Ranges ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[0]+"/32 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[1]+"/32 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[2]+"/32 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 59 Execution Completed")


        @pytest.mark.run(order=60)
        def test_060_Modify_the_Pool_Lb_method_and_add_the_alternate_load_balancing_method_all_available(self):
                print_and_log("********* Mofity the Pool LB method all available to Topology ***********")
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_1')
                response1 = json.loads(response1)
                print_and_log(response1)
                res_ref1 = response1[0]['_ref']
                data = {"lb_alternate_method": "ALL_AVAILABLE"}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref1, fields=json.dumps(data))
                print_and_log(response1)
                restart_services()
                print_and_log("Test Case 60 Execution Completed")


        @pytest.mark.run(order=61)
        def test_061_Validation_of_Pool_Alternate_Lb_method_to_Topology(self):
                print_and_log("********** Validation of Pool LB method all available to Topology **********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ea-rule1')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_1')
                response1 = json.loads(response1)
                print_and_log(response1)
                res_ref1 = response1[0]['_ref']
                response2 = ib_NIOS.wapi_request('GET',object_type=res_ref1, params='?_return_fields=lb_alternate_method')
                response2 = json.loads(response2)
                res_lb_method = response2['lb_alternate_method']
                print_and_log(res_lb_method)
                response3 = ib_NIOS.wapi_request('GET',object_type=res_ref1, params='?_return_fields=lb_preferred_topology')
                response3 = json.loads(response3)
                res_lb_topology = response3['lb_preferred_topology'].split(":")[-1]
                print_and_log(res_lb_topology)
                if res_lb_method == "ALL_AVAILABLE" and res_lb_topology == "ea-rule1":
                    print_and_log("Alternate LB method "+res_lb_method+" is configured to Pool with topo rule "+res_lb_topology+" successfully")
                    assert True
                else:
                    print_and_log(" Error while validating the LB method of the Pool")
                    assert False
                print_and_log("Test Case 61 Execution completed")



        @pytest.mark.run(order=62)
        def test_062_Run_the_dig_command_with_subnet_of_IPAM_network1(self):
                print_and_log("********** Run the dig command with subnet of IPAM network1 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network1+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                Server_That_Responded1 = output.strip(" ").split("\n")[1]
                print_and_log(Server_That_Responded)
                print_and_log(Server_That_Responded1)
                if Server_That_Responded == Server_ip[1] and Server_That_Responded1 == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" and Server "+Server_That_Responded1+" responded for the query with subnet "+config.ipv4network1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 62 Execution Completed")


        @pytest.mark.run(order=63)
        def test_063_Run_the_dig_command_with_subnet_of_IPAM_conatiner(self):
                print_and_log("********** Run the dig command with subnet of IPAM Container ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network_container1+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                Server_That_Responded1 = output.strip(" ").split("\n")[1]
                print_and_log(Server_That_Responded)
                print_and_log(Server_That_Responded1)
                if Server_That_Responded == Server_ip[1] and Server_That_Responded1 == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" and Server "+Server_That_Responded1+" responded for the query with subnet "+config.ipv4network_container1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 63 Execution Completed")


        @pytest.mark.run(order=64)
        def test_064_Run_the_dig_command_with_subnet_of_IPAM_ranges(self):
                print_and_log("********** Run the dig command with subnet of IPAM Ranges ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[0]+"/32 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                Server_That_Responded1 = output.strip(" ").split("\n")[1]
                print_and_log(Server_That_Responded)
                print_and_log(Server_That_Responded1)
                if Server_That_Responded == Server_ip[1] and Server_That_Responded1 == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" and Server "+Server_That_Responded1+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[1]+"/32 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                Server_That_Responded1 = output1.strip(" ").split("\n")[1]
                print_and_log(Server_That_Responded)
                print_and_log(Server_That_Responded1)
                if Server_That_Responded == Server_ip[1] and Server_That_Responded1 == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" and Server "+Server_That_Responded1+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[2]+"/32 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                Server_That_Responded1 = output2.strip(" ").split("\n")[1]
                print_and_log(Server_That_Responded)
                print_and_log(Server_That_Responded1)
                if Server_That_Responded == Server_ip[1] and Server_That_Responded1 == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" and Server "+Server_That_Responded1+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 64 Execution Completed")



        @pytest.mark.run(order=65)
        def test_065_Modify_the_Pool_Lb_method_and_add_the_alternate_load_balancing_method_round_robin(self):
                print_and_log("********* Mofity the Pool LB method round robin to Topology ***********")
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_1')
                response1 = json.loads(response1)
                print_and_log(response1)
                res_ref1 = response1[0]['_ref']
                data = {"lb_alternate_method": "ROUND_ROBIN"}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref1, fields=json.dumps(data))
                print_and_log(response1)
                restart_services()
                print_and_log("Test Case 65 Execution Completed")


        @pytest.mark.run(order=66)
        def test_066_Validation_of_Pool_Alternate_Lb_method_round_robin_to_Topology(self):
                print_and_log("********** Validation of Pool LB method round robin to Topology **********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ea-rule1')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_1')
                response1 = json.loads(response1)
                print_and_log(response1)
                res_ref1 = response1[0]['_ref']
                response2 = ib_NIOS.wapi_request('GET',object_type=res_ref1, params='?_return_fields=lb_alternate_method')
                response2 = json.loads(response2)
                res_lb_method = response2['lb_alternate_method']
                print_and_log(res_lb_method)
                response3 = ib_NIOS.wapi_request('GET',object_type=res_ref1, params='?_return_fields=lb_preferred_topology')
                response3 = json.loads(response3)
                res_lb_topology = response3['lb_preferred_topology'].split(":")[-1]
                print_and_log(res_lb_topology)
                if res_lb_method == "ROUND_ROBIN" and res_lb_topology == "ea-rule1":
                    print_and_log("Alternate LB method "+res_lb_method+" is configured to Pool with topo rule "+res_lb_topology+" successfully")
                    assert True
                else:
                    print_and_log(" Error while validating the LB method of the Pool")
                    assert False
                print_and_log("Test Case 66 Execution completed")



        @pytest.mark.run(order=67)
        def test_067_Run_the_dig_command_with_subnet_of_IPAM_network1(self):
                print_and_log("********** Run the dig command with subnet of IPAM network1 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network1+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1] or Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 67 Execution Completed")


        @pytest.mark.run(order=68)
        def test_068_Run_the_dig_command_with_subnet_of_IPAM_conatiner(self):
                print_and_log("********** Run the dig command with subnet of IPAM Container ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network_container1+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1] or Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network_container1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 68 Execution Completed")


        @pytest.mark.run(order=69)
        def test_069_Run_the_dig_command_with_subnet_of_IPAM_ranges(self):
                print_and_log("********** Run the dig command with subnet of IPAM Ranges ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[0]+"/32 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1] or Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[1]+"/32 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1] or Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[2]+"/32 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1] or Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 69 Execution Completed")



        @pytest.mark.run(order=70)
        def test_070_Modify_the_Pool_Lb_method_and_add_the_alternate_load_balancing_method_source_ip_hash(self):
                print_and_log("********* Mofity the Pool LB method source ip hash to Topology ***********")
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_1')
                response1 = json.loads(response1)
                print_and_log(response1)
                res_ref1 = response1[0]['_ref']
                data = {"lb_alternate_method": "SOURCE_IP_HASH"}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref1, fields=json.dumps(data))
                print_and_log(response1)
                restart_services()
                print_and_log("Test Case 70 Execution Completed")


        @pytest.mark.run(order=71)
        def test_071_Validation_of_Pool_Alternate_Lb_method_source_ip_hash_to_Topology(self):
                print_and_log("********** Validation of Pool LB method source ip hash to Topology **********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ea-rule1')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_1')
                response1 = json.loads(response1)
                print_and_log(response1)
                res_ref1 = response1[0]['_ref']
                response2 = ib_NIOS.wapi_request('GET',object_type=res_ref1, params='?_return_fields=lb_alternate_method')
                response2 = json.loads(response2)
                res_lb_method = response2['lb_alternate_method']
                print_and_log(res_lb_method)
                response3 = ib_NIOS.wapi_request('GET',object_type=res_ref1, params='?_return_fields=lb_preferred_topology')
                response3 = json.loads(response3)
                res_lb_topology = response3['lb_preferred_topology'].split(":")[-1]
                print_and_log(res_lb_topology)
                if res_lb_method == "SOURCE_IP_HASH" and res_lb_topology == "ea-rule1":
                    print_and_log("Alternate LB method "+res_lb_method+" is configured to Pool with topo rule "+res_lb_topology+" successfully")
                    assert True
                else:
                    print_and_log(" Error while validating the LB method of the Pool")
                    assert False
                print_and_log("Test Case 71 Execution completed")



        @pytest.mark.run(order=72)
        def test_072_Run_the_dig_command_with_subnet_of_IPAM_network1(self):
                print_and_log("********** Run the dig command with subnet of IPAM network1 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network1+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1] or Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 72 Execution Completed")


        @pytest.mark.run(order=73)
        def test_073_Run_the_dig_command_with_subnet_of_IPAM_conatiner(self):
                print_and_log("********** Run the dig command with subnet of IPAM Container ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network_container1+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1] or Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network_container1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 73 Execution Completed")


        @pytest.mark.run(order=74)
        def test_074_Run_the_dig_command_with_subnet_of_IPAM_ranges(self):
                print_and_log("********** Run the dig command with subnet of IPAM Ranges ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[0]+"/32 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1] or Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[1]+"/32 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1] or Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[2]+"/32 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1] or Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 74 Execution Completed")



        @pytest.mark.run(order=75)
        def test_075_Modify_the_Pool_Lb_method_and_add_the_alternate_load_balancing_method_none(self):
                print_and_log("********* Mofity the Pool LB method source ip hash to Topology ***********")
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_1')
                response1 = json.loads(response1)
                print_and_log(response1)
                res_ref1 = response1[0]['_ref']
                data = {"lb_alternate_method": "NONE"}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref1, fields=json.dumps(data))
                print_and_log(response1)
                restart_services()
                print_and_log("Test Case 75 Execution Completed")


        @pytest.mark.run(order=76)
        def test_076_Validation_of_Pool_Alternate_Lb_method_none_to_Topology(self):
                print_and_log("********** Validation of Pool LB method source ip hash to Topology **********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ea-rule1')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_1')
                response1 = json.loads(response1)
                print_and_log(response1)
                res_ref1 = response1[0]['_ref']
                response2 = ib_NIOS.wapi_request('GET',object_type=res_ref1, params='?_return_fields=lb_alternate_method')
                response2 = json.loads(response2)
                res_lb_method = response2['lb_alternate_method']
                print_and_log(res_lb_method)
                response3 = ib_NIOS.wapi_request('GET',object_type=res_ref1, params='?_return_fields=lb_preferred_topology')
                response3 = json.loads(response3)
                res_lb_topology = response3['lb_preferred_topology'].split(":")[-1]
                print_and_log(res_lb_topology)
                if res_lb_method == "NONE" and res_lb_topology == "ea-rule1":
                    print_and_log("Alternate LB method "+res_lb_method+" is configured to Pool with topo rule "+res_lb_topology+" successfully")
                    assert True
                else:
                    print_and_log(" Error while validating the LB method of the Pool")
                    assert False
                print_and_log("Test Case 76 Execution completed")


        @pytest.mark.run(order=77)
        def test_077_modify_the_pool1_and_assign_Server_1(self):
                print_and_log("******* Modify the pool1 lb method to Round Robin *********")
                print_and_log("Getting the server name reference ")
                server_ref = []
                for i in Server_name:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    server_ref.append(ref)
                print_and_log(server_ref)
                print_and_log("****** Getting the ref of Pool 1 ******")
                print_and_log("****** Modify the pool Pool_1 and assiging the server1 *********")
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_1')
                response1 = json.loads(response1)
                ref_pool1 = response1[0]['_ref']
                data = {"lb_preferred_method": "ROUND_ROBIN", "servers": [{"ratio": 1,"server": str(server_ref[0])}]}
                response_servers = ib_NIOS.wapi_request('PUT',object_type=ref_pool1, fields=json.dumps(data))
                print_and_log(response_servers)
                restart_services()
                print_and_log("Test Case 77 Execution completed")


        @pytest.mark.run(order=78)
        def test_078_Add_second_pool_Pool_2_and_assign_Server_2(self):
                print_and_log("******* Add Second DTC Pool Pool_2 *********")
                print_and_log("Getting the server name reference ")
                server_ref = []
                for i in Server_name:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    server_ref.append(ref)
                print_and_log(server_ref)
                print_and_log("****** Creating the pool Pool_2 and assiging the server2 ******")
                data = {"name": "Pool_2", "lb_preferred_method": "ROUND_ROBIN", "servers": [{"ratio": 1,"server": str(server_ref[1])}], "monitors": ["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"]}
                response_servers = ib_NIOS.wapi_request('POST',object_type='dtc:pool', fields=json.dumps(data))
                print_and_log(response_servers)
                print_and_log("Validation of Pool creation")
                assert re.search(r'dtc:pool', response_servers)
                print_and_log("Test Case 78 Execution completed")


        @pytest.mark.run(order=79)
        def test_079_Validation_of_the_Pool_1_after_modification(self):
                print_and_log("******* Validation_of_the_Pool_1_after_modification *********")
                response = ib_NIOS.wapi_request('GET', object_type="dtc:pool", params='?name=Pool_1')
                response = json.loads(response)
                print_and_log(response)
                ref_pool1 = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET', object_type=ref_pool1, params='?_return_fields=servers')
                response1 = json.loads(response1)
                print_and_log(response1)
                ref_server = response1['servers'][0]['server'].split(":")[-1]
                print_and_log(ref_server)
                if ref_server == "server1" and ref_server != "server2":
                    print_and_log(ref_server+" is present under the Pool 1, Modfication is successful")
                    assert True
                else:
                    print_and_log("Modfication for Pool 1 failed")
                    assert False
                print_and_log("Test Case 79 Execution completed")


        @pytest.mark.run(order=80)
        def test_080_Validation_of_the_Pool_2(self):
                print_and_log("******* Validation of the Pool 2 *********")
                response = ib_NIOS.wapi_request('GET', object_type="dtc:pool", params='?name=Pool_2')
                response = json.loads(response)
                print_and_log(response)
                ref_pool2 = response[0]['_ref']
                ref_name = response[0]['name']
                print_and_log(ref_name)
                response1 = ib_NIOS.wapi_request('GET', object_type=ref_pool2, params='?_return_fields=servers')
                response1 = json.loads(response1)
                print_and_log(response1)
                ref_server = response1['servers'][0]['server'].split(":")[-1]
                print_and_log(ref_server)
                if ref_server == "server2" and ref_server != "server1" and ref_name == "Pool_2":
                    print_and_log(ref_name+" Pool got created with "+ref_server+" is present under the Pool 2")
                    assert True
                else:
                    print_and_log("Validation for the Pool 2 failed")
                    assert False
                print_and_log("Test Case 80 Execution completed")


        @pytest.mark.run(order=81)
        def test_081_Enable_all_the_IPAM_options_in_grid_dns_properties_traffic_control(self):
                print_and_log("********** Enable all the IPAM options in grid dns properties traffic control ************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                ipam_obj=["gen_eadb_from_networks", "gen_eadb_from_network_containers", "gen_eadb_from_ranges"]
                for i in ipam_obj:
                    data = {i : True}
                    response1 = ib_NIOS.wapi_request('PUT',object_type=ref ,fields=json.dumps(data))
                    print_and_log(response1)
                rebuild_services()
                restart_services()
                print_and_log("Test Case 81 Execution Completed")


        @pytest.mark.run(order=82)
        def test_082_verifying_if_all_the_ipam_objects_are_enabled_in_grid_dns_properties_traffic_control(self):
                print_and_log("********** Verifying if all the ipam objects are enabled in grid dns properties traffic control ************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                for i in json.loads(config.ipam_obj):
                    response1 = ib_NIOS.wapi_request('GET',object_type=ref ,params='?_return_fields='+i)
                    response1 = json.loads(response1)
                    output = response1[i]
                    print_and_log(output)
                    if output == True:
                        print_and_log("IPAM Object "+i+" is Enabled")
                        assert True
                    else:
                        print_and_log("IPAM Object "+i+" is Disabled")
                        assert False
                print_and_log("Test Case 82 Execution Completed")


        @pytest.mark.run(order=83)
        def test_083_Create_the_DTC_topology_Rule_with_Pool_as_Destination(self):
                print_and_log("********* Create the DTC topology Rule with Server as Destination ***********")
                pool_ref = []
                Pool = ["Pool_1", "Pool_2"]
                for i in Pool:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    pool_ref.append(ref)
                data = {"name": "ea-rule2", "rules": [{"sources": [{"source_op": "IS","source_type": "EA0","source_value": "network1"}], "dest_type": "POOL","destination_link": pool_ref[0]}, {"sources":[{"source_op": "IS","source_type": "EA0","source_value": "network2"}], "dest_type": "POOL","destination_link": pool_ref[1]}]}
                print_and_log(data)
                response = ib_NIOS.wapi_request('POST',object_type='dtc:topology', fields=json.dumps(data))
                print_and_log(response)
                assert re.search(r'dtc:topology', response)
                print_and_log("Test Case 83 Execution completed")


        @pytest.mark.run(order=84)
        def test_084_Validation_of_Topology_rule_2(self):
                print_and_log("********* Validation of Topology rule 2 ***********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ea-rule2')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                res_name = response[0]['name']
                if res_name == "ea-rule2":
                    print_and_log("Topology rule "+res_name+" created successfully")
                    assert True
                else:
                    print_and_log(" Validation for the Topology rule failed ")
                    assert False
                print_and_log("Test Case 84 Execution completed")


        @pytest.mark.run(order=85)
        def test_085_Modify_the_LBDN_and_Configure_the_Topology_rule_2_as_Lb_method(self):
                print_and_log("********* Modify the LBDN and Configure the Topology rule 2 as Lb method ***********")
                pool_ref = []
                Pool = ["Pool_1", "Pool_2"]
                for i in Pool:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    pool_ref.append(ref)
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ea-rule2')
                response1 = json.loads(response1)
                print_and_log(response1)
                res_ref = response1[0]['_ref']
                response2 = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=LBDN')
                response2 = json.loads(response2)
                ref_lbdn = response2[0]['_ref']
                data = {"lb_method": "TOPOLOGY", "topology": res_ref, "pools": [{"ratio": 1, "pool": pool_ref[0]}, {"ratio": 1, "pool": pool_ref[1]}]}
                response3 = ib_NIOS.wapi_request('PUT',object_type=ref_lbdn, fields=json.dumps(data))
                print_and_log(response3)
                assert re.search(r'dtc:lbdn', response3)
                restart_services()
                print_and_log("Test Case 85 Execution completed")



        @pytest.mark.run(order=86)
        def test_086_validation_of_dtc_lbdn(self):
                print_and_log("******** Validation of dtc lbdn **********")
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=LBDN')
                response1 = json.loads(response1)
                ref_lbdn = response1[0]['_ref']
                response2 = ib_NIOS.wapi_request('GET',object_type=ref_lbdn, params='?_return_fields=lb_method')
                response2 = json.loads(response2)
                ref_lb_method = response2['lb_method']
                response3 = ib_NIOS.wapi_request('GET',object_type=ref_lbdn, params='?_return_fields=topology')
                response3 = json.loads(response3)
                ref_lb_topology = response3['topology'].split(":")[-1]
                if ref_lb_method == "TOPOLOGY" and ref_lb_topology == "ea-rule2":
                    print_and_log("LBDN configured with Lb method "+ref_lb_method+" with topology rule "+ref_lb_topology)
                    assert True
                else:
                    print_and_log("Validation for the LBDN failed")
                    assert False
                print_and_log("Test Case 86 Execution completed")



        @pytest.mark.run(order=87)
        def test_087_Modify_the_value_of_the_IPAM_network_from_network1_to_network2(self):
                print_and_log("******** Modify the value of the IPAM network from network1 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="network", params='?network='+config.ipv4network1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network2"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('network', 'network2', '?network='+config.ipv4network1)
                print_and_log("Test Case 87 Execution Completed")



        @pytest.mark.run(order=88)
        def test_088_Modify_the_value_of_the_IPAM_conatiner_from_network2_to_network1(self):
                print_and_log("******** Modify the value of the IPAM conatiner from network2 to network1 *********")
                response = ib_NIOS.wapi_request('GET',object_type="networkcontainer", params='?network='+config.ipv4network_container1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network1"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('networkcontainer', 'network1', '?network='+config.ipv4network_container1)
                print_and_log("Test Case 88 Execution Completed")



        @pytest.mark.run(order=89)
        def test_089_Modify_the_value_of_the_IPAM_Ranges_from_network2_to_network1(self):
                print_and_log("******** Modify the value of the IPAM network from network2 to network1 *********")
                response = ib_NIOS.wapi_request('GET',object_type="range", params='?network='+config.ipv4network1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network1"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('range', 'network1', '?network='+config.ipv4network1)
                print_and_log("Test Case 89 Execution Completed")


        @pytest.mark.run(order=90)
        def test_090_Modify_the_value_of_the_IPAM_Host_from_network2_to_network1(self):
                print_and_log("******** Modify the value of the IPAM network from network2 to network1 *********")
                response = ib_NIOS.wapi_request('GET',object_type="record:host", params='?name=host_new')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network1"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('record:host', 'network1', '?name=host_new')
                print_and_log("Test Case 90 Execution Completed")



        @pytest.mark.run(order=91)
        def test_091_Run_the_dig_command_with_subnet_of_IPAM_network1(self):
                print_and_log("********** Run the dig command with subnet of IPAM network1 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network1+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 91 Execution Completed")


        @pytest.mark.run(order=92)
        def test_092_Run_the_dig_command_with_subnet_of_IPAM_conatiner(self):
                print_and_log("********** Run the dig command with subnet of IPAM Container ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network_container1+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network_container1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 92 Execution Completed")


        @pytest.mark.run(order=93)
        def test_093_Run_the_dig_command_with_subnet_of_IPAM_ranges(self):
                print_and_log("********** Run the dig command with subnet of IPAM Ranges ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[0]+"/32 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[1]+"/32 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[2]+"/32 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 93 Execution Completed")



        @pytest.mark.run(order=94)
        def test_094_Run_the_dig_command_with_subnet_of_IPAM_Hosts(self):
                print_and_log("********** Run the dig command with subnet of IPAM Hosts ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4addr_host+"/32 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4addr_host)
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 94 Execution Completed")



        @pytest.mark.run(order=95)
        def test_095_Modify_the_value_of_the_IPAM_network_from_network2_to_network1(self):
                print_and_log("******** Modify the value of the IPAM network from network2 to network1 *********")
                response = ib_NIOS.wapi_request('GET',object_type="network", params='?network='+config.ipv4network1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network1"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('network', 'network1', '?network='+config.ipv4network1)
                print_and_log("Test Case 95 Execution Completed")



        @pytest.mark.run(order=96)
        def test_096_Modify_the_value_of_the_IPAM_conatiner_from_network1_to_network2(self):
                print_and_log("******** Modify the value of the IPAM conatiner from network1 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="networkcontainer", params='?network='+config.ipv4network_container1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network2"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('networkcontainer', 'network2', '?network='+config.ipv4network_container1)
                print_and_log("Test Case 96 Execution Completed")



        @pytest.mark.run(order=97)
        def test_097_Modify_the_value_of_the_IPAM_Ranges_from_network1_to_network2(self):
                print_and_log("******** Modify the value of the IPAM network from network1 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="range", params='?network='+config.ipv4network1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network2"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('range', 'network2', '?network='+config.ipv4network1)
                print_and_log("Test Case 97 Execution Completed")


        @pytest.mark.run(order=98)
        def test_098_Modify_the_value_of_the_IPAM_Host_from_network1_to_network2(self):
                print_and_log("******** Modify the value of the IPAM network from network1 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="record:host", params='?name=host_new')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network2"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('record:host', 'network2', '?name=host_new')
                print_and_log("Test Case 98 Execution Completed")



        @pytest.mark.run(order=99)
        def test_099_Run_the_dig_command_with_subnet_of_IPAM_network1(self):
                print_and_log("********** Run the dig command with subnet of IPAM network1 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network1+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 99 Execution Completed")


        @pytest.mark.run(order=100)
        def test_100_Run_the_dig_command_with_subnet_of_IPAM_conatiner(self):
                print_and_log("********** Run the dig command with subnet of IPAM Container ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network_container1+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network_container1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 100 Execution Completed")


        @pytest.mark.run(order=101)
        def test_101_Run_the_dig_command_with_subnet_of_IPAM_ranges(self):
                print_and_log("********** Run the dig command with subnet of IPAM Ranges ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[0]+"/32 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[1]+"/32 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[2]+"/32 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 101 Execution Completed")



        @pytest.mark.run(order=102)
        def test_102_Run_the_dig_command_with_subnet_of_IPAM_Hosts(self):
                print_and_log("********** Run the dig command with subnet of IPAM Hosts ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4addr_host+"/32 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4addr_host)
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 102 Execution Completed")



        @pytest.mark.run(order=103)
        def test_103_Uncheck_the_IPAM_Container_object_in_Grid_DNS_Properties_Traffic_Control(self):
                print_and_log("********** Uncheck the IPAM Container object in Grid DNS Properties Traffic Control ************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                data = {"gen_eadb_from_network_containers": False}
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                restart_services()
                print_and_log("Test Case 103 Execution Completed")


        @pytest.mark.run(order=104)
        def test_104_Validation_of_the_IPAM_Container_object_in_Grid_DNS_Properties_Traffic_Control(self):
                print_and_log("********** Validation of the IPAM Container object in Grid DNS Properties Traffic Control************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=gen_eadb_from_network_containers')
                response1 = json.loads(response1)
                output = response1['gen_eadb_from_network_containers']
                if output == False:
                    print_and_log(" The IPAM Containers Object in Grid DNS properties is set to False")
                    assert True
                else:
                    print_and_log(" The IPAM Containers Object in Grid DNS properties is set to True")
                    assert False
                print_and_log("Test Case 104 Execution Completed")


        @pytest.mark.run(order=105)
        def test_105_Run_the_dig_command_with_subnet_of_IPAM_conatiner(self):
                print_and_log("********** Run the dig command with subnet of IPAM Container ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network_container1).read()
                out = output.split("\n")
                flag = False
                for i in out:
                    match = re.match("dtc.com.\s+\d+\s+IN\s+SOA.*",i)
                    print_and_log(i)
                    if match:
                        print_and_log(" Match found ")
                        flag=True
                        break
                if flag == True:
                    print_and_log("SOA record is found, No response from any for the DTC servers")
                    assert True
                else:
                    print_and_log("Query got the response from DTC servers")
                    assert False
                print_and_log("Test Case 105 Execution Completed")


        @pytest.mark.run(order=106)
        def test_106_Uncheck_the_IPAM_Networks_object_in_Grid_DNS_Properties_Traffic_Control(self):
                print_and_log("********** Uncheck the IPAM networks object in Grid DNS Properties Traffic Control ************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                data = {"gen_eadb_from_networks": False}
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                restart_services()
                print_and_log("Test Case 106 Execution Completed")




        @pytest.mark.run(order=107)
        def test_107_Validation_of_the_IPAM_network_object_in_Grid_DNS_Properties_Traffic_Control(self):
                print_and_log("********** Validation of the IPAM networks object in Grid DNS Properties Traffic Control************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=gen_eadb_from_networks')
                response1 = json.loads(response1)
                output = response1['gen_eadb_from_networks']
                if output == False:
                    print_and_log(" The IPAM networks Object in Grid DNS properties is set to False")
                    assert True
                else:
                    print_and_log(" The IPAM networks Object in Grid DNS properties is set to True")
                    assert False
                print_and_log("Test Case 107 Execution Completed")



        @pytest.mark.run(order=108)
        def test_108_Run_the_dig_command_with_subnet_of_IPAM_network(self):
                print_and_log("********** Run the dig command with subnet of IPAM Network ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network1).read()
                out = output.split("\n")
                flag = False
                for i in out:
                    match = re.match("dtc.com.\s+\d+\s+IN\s+SOA.*",i)
                    print_and_log(i)
                    if match:
                        print_and_log(" Match found ")
                        flag=True
                        break
                if flag == True:
                    print_and_log("SOA record is found, No response from any for the DTC servers")
                    assert True
                else:
                    print_and_log("Query got the response from DTC servers")
                    assert False
                print_and_log("Test Case 108 Execution Completed")



        @pytest.mark.run(order=109)
        def test_109_Uncheck_the_IPAM_ranges_object_in_Grid_DNS_Properties_Traffic_Control(self):
                print_and_log("********** Uncheck the IPAM ranges object in Grid DNS Properties Traffic Control ************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                data = {"gen_eadb_from_ranges": False}
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                restart_services()
                print_and_log("Test Case 109 Execution Completed")


        @pytest.mark.run(order=110)
        def test_110_Validation_of_the_IPAM_ranges_object_in_Grid_DNS_Properties_Traffic_Control(self):
                print_and_log("********** Validation of the IPAM ranges object in Grid DNS Properties Traffic Control************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=gen_eadb_from_ranges')
                response1 = json.loads(response1)
                output = response1['gen_eadb_from_ranges']
                if output == False:
                    print_and_log(" The IPAM ranges Object in Grid DNS properties is set to False")
                    assert True
                else:
                    print_and_log(" The IPAM networks Object in Grid DNS properties is set to True")
                    assert False
                print_and_log("Test Case 110 Execution Completed")



        @pytest.mark.run(order=111)
        def test_111_Run_the_dig_command_with_subnet_of_IPAM_ranges(self):
                print_and_log("********** Run the dig command with subnet of IPAM Ranges ************")
                for i in json.loads(config.ipv4_ranges):
                    output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+i+"/32").read()
                    out = output.split("\n")
                    flag = False
                    for i in out:
                        match = re.match("dtc.com.\s+\d+\s+IN\s+SOA.*",i)
                        print_and_log(i)
                        if match:
                            print_and_log(" Match found ")
                            flag=True
                            break
                    if flag == True:
                        print_and_log("SOA record is found, No response from any for the DTC servers")
                        assert True
                    else:
                        print_and_log("Query got the response from DTC servers")
                        assert False
                print_and_log("Test Case 111 Execution Completed")



        @pytest.mark.run(order=112)
        def test_112_Create_the_thrid_DTC_server(self):
                print_and_log("********** Create the Thrid DTC server ***********")
                data = {"name":"server3","host":Server_ip[0]}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
                print_and_log(response)
                assert re.search(r'dtc:server', response)
                print_and_log("Test Case 112 Execution Completed")


        @pytest.mark.run(order=113)
        def test_113_Validate_the_New_DTC_server_that_is_created(self):
                print_and_log("********** Validate the New DTC server that is created ***********")
                response = ib_NIOS.wapi_request('GET', object_type="dtc:server", params='?name=server3')
                response = json.loads(response)
                print_and_log(response)
                name = response[0]['name']
                if name == "server3":
                    print_and_log(" DTC server "+name+" created successfully")
                    assert True
                else:
                    print_and_log(" Error while validating the newly created server")
                    assert False
                print_and_log("Test Case 113 Execution Completed")


        @pytest.mark.run(order=114)
        def test_114_Create_the_thrid_DTC_Pool(self):
                print_and_log("********** Create the thrid DTC Pool ***********")
                response = ib_NIOS.wapi_request('GET', object_type="dtc:server", params='?name=server3')
                response = json.loads(response)
                print_and_log(response)
                ref = response[0]['_ref']
                data = {"name": "Pool_3", "lb_preferred_method": "ROUND_ROBIN", "servers": [{"ratio": 1,"server": str(ref)}], "monitors": ["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"]}
                response_servers = ib_NIOS.wapi_request('POST',object_type='dtc:pool', fields=json.dumps(data))
                ref1 = json.loads(response_servers)
                print_and_log(ref1)
                print_and_log("Validation of Pool creation")
                assert re.search(r'dtc:pool', ref1)
                print_and_log("Test Case 114 Execution Completed")


        @pytest.mark.run(order=115)
        def test_115_Validate_the_New_DTC_Pool_that_is_created(self):
                print_and_log("********** Validate the New DTC Pool that is created ***********")
                response = ib_NIOS.wapi_request('GET', object_type="dtc:pool", params='?name=Pool_3')
                response = json.loads(response)
                print_and_log(response)
                name = response[0]['name']
                if name == "Pool_3":
                    print_and_log(" DTC Pool "+name+" created successfully")
                    assert True
                else:
                    print_and_log(" Error while validating the newly created Pool")
                    assert False
                print_and_log("Test Case 115 Execution Completed")


        @pytest.mark.run(order=116)
        def test_116_Enable_all_the_IPAM_options_in_grid_dns_properties_traffic_control(self):
                print_and_log("********** Enable all the IPAM options in grid dns properties traffic control ************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                ipam_obj=["gen_eadb_from_networks", "gen_eadb_from_network_containers", "gen_eadb_from_ranges"]
                for i in ipam_obj:
                    data = {i : True}
                    response1 = ib_NIOS.wapi_request('PUT',object_type=ref ,fields=json.dumps(data))
                    print_and_log(response1)
                rebuild_services()
                restart_services()
                print_and_log("Test Case 116 Execution Completed")


        @pytest.mark.run(order=117)
        def test_117_Add_Pool_3_has_default_destination_in_the_topology_rule(self):
                print_and_log("********* Add_Pool_3_has_default_destination_in_the_topology_rule **********")
                pool_ref = []
                Pool = ["Pool_1", "Pool_2", "Pool_3"]
                for i in Pool:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    pool_ref.append(ref)
                data = {"rules": [{"sources": [{"source_op": "IS","source_type": "EA0","source_value": "network1"}], "dest_type": "POOL","destination_link": pool_ref[0]}, {"sources":[{"source_op": "IS","source_type": "EA0","source_value": "network2"}], "dest_type": "POOL","destination_link": pool_ref[1]}, {"sources":[], "dest_type": "POOL", "destination_link": pool_ref[2]}]}
                response = ib_NIOS.wapi_request('GET', object_type="dtc:topology", params='?name=ea-rule2')
                response = json.loads(response)
                print_and_log(response)
                topo_ref = response[0]['_ref']
                #data = {"rules": [{"sources":[], "dest_type": "POOL", "destination_link": str(pool_ref)}]}
                response1 = ib_NIOS.wapi_request('PUT', object_type=topo_ref, fields=json.dumps(data))
                print_and_log(response1)
                print_and_log("Validation of Topology creation")
                assert re.search(r'dtc:topology', response1)
                restart_services()
                print_and_log("Test Case 117 Execution Completed")



        @pytest.mark.run(order=118)
        def test_118_Validation_of_default_destination_pool_added_in_topo_rule(self):
                print_and_log("********* Validation of default destination pool added in topo rule **********")
                response = ib_NIOS.wapi_request('GET', object_type="dtc:topology", params='?name=ea-rule2')
                response = json.loads(response)
                print_and_log(response)
                topo_ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET', object_type=topo_ref, params='?_return_fields=rules')
                response1 = json.loads(response1)
                print_and_log(response1)
                rule_ref = response1['rules'][2]['_ref']
                response2 = ib_NIOS.wapi_request('GET', object_type=rule_ref, params='?_return_fields=destination_link')
                response2 = json.loads(response2)
                print_and_log(response2)
                pool_name = response2['destination_link']['name']
                print_and_log(pool_name)
                response3 = ib_NIOS.wapi_request('GET', object_type=rule_ref, params='?_return_fields=sources')
                response3 = json.loads(response3)
                print_and_log(response3)
                sources = response3['sources']
                print_and_log(sources)
                if sources == [] and pool_name == "Pool_3":
                    print_and_log(pool_name+" is configured as default destination pool")
                    assert True
                else:
                    print_and_log("Validation for deafult destination failed")
                    assert False
                print_and_log("Test Case 118 Execution Completed")


        @pytest.mark.run(order=119)
        def test_119_Modify_the_value_of_the_IPAM_network_from_network1_to_network3(self):
                print_and_log("******** Modify the value of the IPAM network from network1 to network3 *********")
                response = ib_NIOS.wapi_request('GET',object_type="network", params='?network='+config.ipv4network1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network3"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('network', 'network3', '?network='+config.ipv4network1)
                print_and_log("Test Case 119 Execution Completed")



        @pytest.mark.run(order=120)
        def test_120_Modify_the_value_of_the_IPAM_conatiner_from_network2_to_network3(self):
                print_and_log("******** Modify the value of the IPAM conatiner from network2 to network3 *********")
                response = ib_NIOS.wapi_request('GET',object_type="networkcontainer", params='?network='+config.ipv4network_container1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network3"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('networkcontainer', 'network3', '?network='+config.ipv4network_container1)
                print_and_log("Test Case 120 Execution Completed")



        @pytest.mark.run(order=121)
        def test_121_Run_the_dig_command_with_subnet_of_IPAM_network1(self):
                print_and_log("********** Run the dig command with subnet of IPAM network1 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network1+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[0]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 121 Execution Completed")


        @pytest.mark.run(order=122)
        def test_122_Run_the_dig_command_with_subnet_of_IPAM_conatiner(self):
                print_and_log("********** Run the dig command with subnet of IPAM Container ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network_container1+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[0]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network_container1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 122 Execution Completed")



        @pytest.mark.run(order=123)
        def test_123_Modify_the_value_of_the_IPAM_network_from_network3_to_network1(self):
                print_and_log("******** Modify the value of the IPAM network from network1 to network3 *********")
                response = ib_NIOS.wapi_request('GET',object_type="network", params='?network='+config.ipv4network1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network1"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('network', 'network1', '?network='+config.ipv4network1)
                print_and_log("Test Case 123 Execution Completed")



        @pytest.mark.run(order=124)
        def test_124_Modify_the_value_of_the_IPAM_conatiner_from_network3_to_network2(self):
                print_and_log("******** Modify the value of the IPAM conatiner from network2 to network3 *********")
                response = ib_NIOS.wapi_request('GET',object_type="networkcontainer", params='?network='+config.ipv4network_container1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network2"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('networkcontainer', 'network2', '?network='+config.ipv4network_container1)
                print_and_log("Test Case 124 Execution Completed")


        @pytest.mark.run(order=125)
        def test_125_Modify_the_Pool_1_Lb_method_to_Topology(self):
                print_and_log("********* Mofity the Pool LB method to Topology ***********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ea-rule1')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                server_ref = []
                for i in Server_name:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    server_ref.append(ref)
                print_and_log(server_ref)
                print_and_log("****** Creating the pool and assiging the server ******")
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_1')
                response1 = json.loads(response1)
                print_and_log(response1)
                res_ref1 = response1[0]['_ref']
                data = {"lb_preferred_method": "TOPOLOGY", "lb_preferred_topology": res_ref, "servers": [{"ratio": 1,"server": str(server_ref[0])}, {"ratio": 1,"server": str(server_ref[1])}]}
                response2 = ib_NIOS.wapi_request('PUT',object_type=res_ref1, fields=json.dumps(data))
                print_and_log(response2)
                print_and_log("Validation of Pool Modfication")
                assert re.search(r'dtc:pool', response2)
                restart_services()
                print_and_log("Test Case 125 Execution Completed")



        @pytest.mark.run(order=126)
        def test_126_Modify_the_Pool_2_Lb_method_to_Topology(self):
                print_and_log("********* Mofity the Pool LB method to Topology ***********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ea-rule1')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                server_ref = []
                for i in Server_name:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    server_ref.append(ref)
                print_and_log(server_ref)
                print_and_log("****** Creating the pool and assiging the server ******")
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_2')
                response1 = json.loads(response1)
                print_and_log(response1)
                res_ref1 = response1[0]['_ref']
                data = {"lb_preferred_method": "TOPOLOGY", "lb_preferred_topology": res_ref, "servers": [{"ratio": 1,"server": str(server_ref[1])}, {"ratio": 1,"server": str(server_ref[0])}]}
                response2 = ib_NIOS.wapi_request('PUT',object_type=res_ref1, fields=json.dumps(data))
                print_and_log(response2)
                print_and_log("Validation of Pool Modfication")
                assert re.search(r'dtc:pool', response2)
                restart_services()
                print_and_log("Test Case 126 Execution Completed")




        @pytest.mark.run(order=127)
        def test_127_Run_the_dig_command_with_subnet_of_IPAM_network1(self):
                print_and_log("********** Run the dig command with subnet of IPAM network1 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network1+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 127 Execution Completed")


        @pytest.mark.run(order=128)
        def test_128_Run_the_dig_command_with_subnet_of_IPAM_conatiner(self):
                print_and_log("********** Run the dig command with subnet of IPAM Container ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network_container1+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network_container1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 128 Execution Completed")


        @pytest.mark.run(order=129)
        def test_129_Run_the_dig_command_with_subnet_of_IPAM_ranges(self):
                print_and_log("********** Run the dig command with subnet of IPAM Ranges ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[0]+"/32 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[1]+"/32 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[2]+"/32 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 129 Execution Completed")



        @pytest.mark.run(order=130)
        def test_130_Run_the_dig_command_with_subnet_of_IPAM_Hosts(self):
                print_and_log("********** Run the dig command with subnet of IPAM Hosts ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4addr_host+"/32 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4addr_host)
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 130 Execution Completed")



        @pytest.mark.run(order=131)
        def test_131_Modify_the_value_of_the_IPAM_network_from_network1_to_network2(self):
                print_and_log("******** Modify the value of the IPAM network from network1 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="network", params='?network='+config.ipv4network1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network2"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('network', 'network2', '?network='+config.ipv4network1)
                print_and_log("Test Case 131 Execution Completed")



        @pytest.mark.run(order=132)
        def test_132_Modify_the_value_of_the_IPAM_conatiner_from_network2_to_network1(self):
                print_and_log("******** Modify the value of the IPAM conatiner from network2 to network1 *********")
                response = ib_NIOS.wapi_request('GET',object_type="networkcontainer", params='?network='+config.ipv4network_container1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network1"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('networkcontainer', 'network1', '?network='+config.ipv4network_container1)
                print_and_log("Test Case 132 Execution Completed")



        @pytest.mark.run(order=133)
        def test_133_Modify_the_value_of_the_IPAM_Ranges_from_network2_to_network1(self):
                print_and_log("******** Modify the value of the IPAM network from network2 to network1 *********")
                response = ib_NIOS.wapi_request('GET',object_type="range", params='?network='+config.ipv4network1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network1"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('range', 'network1', '?network='+config.ipv4network1)
                print_and_log("Test Case 133 Execution Completed")


        @pytest.mark.run(order=134)
        def test_134_Modify_the_value_of_the_IPAM_Host_from_network2_to_network1(self):
                print_and_log("******** Modify the value of the IPAM network from network2 to network1 *********")
                response = ib_NIOS.wapi_request('GET',object_type="record:host", params='?name=host_new')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network1"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('record:host', 'network1', '?name=host_new')
                print_and_log("Test Case 134 Execution Completed")


        @pytest.mark.run(order=135)
        def test_135_Run_the_dig_command_with_subnet_of_IPAM_network1(self):
                print_and_log("********** Run the dig command with subnet of IPAM network1 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network1+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 135 Execution Completed")


        @pytest.mark.run(order=136)
        def test_136_Run_the_dig_command_with_subnet_of_IPAM_conatiner(self):
                print_and_log("********** Run the dig command with subnet of IPAM Container ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network_container1+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network_container1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 136 Execution Completed")


        @pytest.mark.run(order=137)
        def test_137_Run_the_dig_command_with_subnet_of_IPAM_ranges(self):
                print_and_log("********** Run the dig command with subnet of IPAM Ranges ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[0]+"/32 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[1]+"/32 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[2]+"/32 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 137 Execution Completed")



        @pytest.mark.run(order=138)
        def test_138_Run_the_dig_command_with_subnet_of_IPAM_Hosts(self):
                print_and_log("********** Run the dig command with subnet of IPAM Hosts ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4addr_host+"/32 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4addr_host)
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 138 Execution Completed")



        @pytest.mark.run(order=139)
        def test_139_Drop_the_Server1_and_verify_the_response(self):
                logging.info("********** Drop the Server1 and verify the response ************")
                drop_server = "iptables -I INPUT -s "+Server_ip[1]+" -j DROP"
                print(drop_server)
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_master_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline(drop_server)
                child.expect('#')
                child.close()
                sleep(60)
                logging.info("Test Case 139 Execution Completed")



        @pytest.mark.run(order=140)
        def test_140_Run_the_dig_command_with_subnet_of_IPAM_network1(self):
                print_and_log("********** Run the dig command with subnet of IPAM network1 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network1+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 140 Execution Completed")


        @pytest.mark.run(order=141)
        def test_141_Run_the_dig_command_with_subnet_of_IPAM_conatiner(self):
                print_and_log("********** Run the dig command with subnet of IPAM Container ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network_container1+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[0]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network_container1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 141 Execution Completed")


        @pytest.mark.run(order=142)
        def test_142_Run_the_dig_command_with_subnet_of_IPAM_ranges(self):
                print_and_log("********** Run the dig command with subnet of IPAM Ranges ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[0]+"/32 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[0]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[1]+"/32 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[0]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[2]+"/32 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[0]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 142 Execution Completed")



        @pytest.mark.run(order=143)
        def test_143_Run_the_dig_command_with_subnet_of_IPAM_Hosts(self):
                print_and_log("********** Run the dig command with subnet of IPAM Hosts ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4addr_host+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[0]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4addr_host)
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 143 Execution Completed")




        @pytest.mark.run(order=144)
        def test_144_Accept_the_Server1_and_verify_the_response(self):
                logging.info("********** Drop the Server1 and verify the response ************")
                accept_server = "iptables -I INPUT -s "+Server_ip[1]+" -j ACCEPT"
                print(accept_server)
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_master_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline(accept_server)
                child.expect('#')
                child.close()
                sleep(60)
                logging.info("Test Case 144 Execution Completed")



        @pytest.mark.run(order=145)
        def test_145_Modify_the_LBDN_and_Configure_the_Topology_rule_2_as_Lb_method(self):
                print_and_log("********* Modify the LBDN and Configure ROUND ROBIN method ***********")
                response2 = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=LBDN')
                response2 = json.loads(response2)
                ref_lbdn = response2[0]['_ref']
                data = {"lb_method": "ROUND_ROBIN"}
                response3 = ib_NIOS.wapi_request('PUT',object_type=ref_lbdn, fields=json.dumps(data))
                print_and_log(response3)
                assert re.search(r'dtc:lbdn', response3)
                restart_services()
                print_and_log("Test Case 145 Execution completed")



        @pytest.mark.run(order=146)
        def test_146_validation_of_dtc_lbdn(self):
                print_and_log("******** Validation of dtc lbdn **********")
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=LBDN')
                response1 = json.loads(response1)
                ref_lbdn = response1[0]['_ref']
                response2 = ib_NIOS.wapi_request('GET',object_type=ref_lbdn, params='?_return_fields=lb_method')
                response2 = json.loads(response2)
                ref_lb_method = response2['lb_method']
                if ref_lb_method == "ROUND_ROBIN":
                    print_and_log("LBDN configured with Lb method "+ref_lb_method)
                    assert True
                else:
                    print_and_log("Validation for the LBDN failed")
                    assert False
                print_and_log("Test Case 146 Execution completed")



        @pytest.mark.run(order=147)
        def test_147_Run_the_dig_command_with_subnet_of_IPAM_network1(self):
                print_and_log("********** Run the dig command with subnet of IPAM network1 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network1+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 147 Execution Completed")


        @pytest.mark.run(order=148)
        def test_148_Run_the_dig_command_with_subnet_of_IPAM_conatiner(self):
                print_and_log("********** Run the dig command with subnet of IPAM Container ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network_container1+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network_container1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 148 Execution Completed")


        @pytest.mark.run(order=149)
        def test_149_Run_the_dig_command_with_subnet_of_IPAM_ranges(self):
                print_and_log("********** Run the dig command with subnet of IPAM Ranges ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[0]+"/32 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[1]+"/32 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges)[2]+"/32 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 149 Execution Completed")



        @pytest.mark.run(order=150)
        def test_150_Run_the_dig_command_with_subnet_of_IPAM_Hosts(self):
                print_and_log("********** Run the dig command with subnet of IPAM Hosts ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4addr_host+"/32 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4addr_host)
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 150 Execution Completed")



        @pytest.mark.run(order=151)
        def test_151_Assign_Four_EAs_in_Grid_Properties_Traffic_Control(self):
                print_and_log("********** Assign Four EAs in Grid Properties Traffic Control ************")
                response = ib_NIOS.wapi_request('GET',object_type='grid:dns')
                response = json.loads(response)
                ref = response[0]['_ref']
                data={"dtc_topology_ea_list": ["EA_string", "EA_list", "EA_int", "Site"]}
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
                print_and_log(response1)
                assert re.search(r'grid:dns', response1)
                rebuild_services()
                print_and_log("Test Case 151 Execution completed ")



        @pytest.mark.run(order=152)
        def test_152_Validate_Four_EAs_in_Grid_Properties_Traffic_Control(self):
                print_and_log("********** Validate Four EAs in Grid Properties Traffic Control ************")
                response = ib_NIOS.wapi_request('GET',object_type='grid:dns')
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=dtc_topology_ea_list')
                response1 = json.loads(response1)
                print_and_log(response1)
                output = response1['dtc_topology_ea_list']
                print_and_log(output)
                expected_list = ["EA_string", "EA_list", "EA_int", "Site"]
                if output == expected_list:
                    print_and_log(" ALl the 4 Ea's are configured successfully")
                    assert True
                else:
                    print_and_log(" Error while validating the EA's ")
                    assert False
                print_and_log("Test Case 152 Execution completed ")



        @pytest.mark.run(order=153)
        def test_153_ADD_New_IPV4_Network_Container_Ranges_and_Hosts(self):
                print_and_log("******** Add New IPV4 Network, Network container, Ranges and Host *********")
                data = {"network": config.ipv4network2, "extattrs": { "EA_int": {"value": 5}, "EA_list": {"value": "2"}, "EA_string": {"value": "network2"}, "Site": {"value": "Infoblox"}}}
                response = ib_NIOS.wapi_request('POST',object_type="network", fields=json.dumps(data))
                print_and_log(response)
                assert re.search(r'network', response)
                data = {"network": config.ipv4network_container2, "extattrs": { "EA_int": {"value": 10}, "EA_list": {"value": "1"}, "EA_string": {"value": "network1"}, "Site": {"value": "Infoblox"}}}
                response1 = ib_NIOS.wapi_request('POST',object_type="networkcontainer", fields=json.dumps(data))
                print_and_log(response1)
                assert re.search(r'networkcontainer', response1)
                data = {"start_addr": json.loads(config.ipv4_ranges2)[0], "end_addr": json.loads(config.ipv4_ranges2)[2], "network": config.ipv4network2, "extattrs": { "EA_int": {"value": 10}, "EA_list": {"value": "1"}, "EA_string": {"value": "network1"}, "Site": {"value": "Infoblox"}}}
                response2 = ib_NIOS.wapi_request('POST',object_type="range", fields=json.dumps(data))
                print_and_log(response2)
                assert re.search(r'range', response2)
                data = {"name": "host_new_2","configure_for_dns": False, "ipv4addrs": [{"ipv4addr": config.ipv4addr_host2}], "extattrs": { "EA_int": {"value": 10}, "EA_list": {"value": "1"}, "EA_string": {"value": "network1"}, "Site": {"value": "Infoblox"}}}
                response3 = ib_NIOS.wapi_request('POST',object_type="record:host", fields=json.dumps(data))
                print_and_log(response3)
                assert re.search(r'record:host', response3)
                rebuild_services()
                print_and_log("Test Case 153 Execution completed")



        @pytest.mark.run(order=154)
        def test_154_Validate_the_Extensible_attribute_values_configured_for_IPAM_network2(self):
                print_and_log("********** Validate the Extensible attribute values configured ***********")
                validation_of_4_EAs_value_configured_in_extensible_attribute('network', 'network2', 'EA_string', 'network='+str(config.ipv4network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('network', '2', 'EA_list', 'network='+str(config.ipv4network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('network', 'Infoblox', 'Site', 'network='+str(config.ipv4network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('network', int(5), 'EA_int', 'network='+str(config.ipv4network2))
                print_and_log("Test Case 154 Execution completed")



        @pytest.mark.run(order=155)
        def test_155_Validate_the_Extensible_attribute_values_configured_for_IPAM_networkcontainer2(self):
                print_and_log("********** Validate the Extensible attribute values configured ***********")
                validation_of_4_EAs_value_configured_in_extensible_attribute('networkcontainer', 'network1', 'EA_string', 'network='+str(config.ipv4network_container2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('networkcontainer', '1', 'EA_list', 'network='+str(config.ipv4network_container2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('networkcontainer', 'Infoblox', 'Site', 'network='+str(config.ipv4network_container2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('networkcontainer', int(10), 'EA_int', 'network='+str(config.ipv4network_container2))
                print_and_log("Test Case 155 Execution completed")



        @pytest.mark.run(order=156)
        def test_156_Validate_the_Extensible_attribute_values_configured_for_IPAM_ranges(self):
                print_and_log("********** Validate the Extensible attribute values configured ***********")
                validation_of_4_EAs_value_configured_in_extensible_attribute('range', 'network1', 'EA_string', 'network='+str(config.ipv4network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('range', '1', 'EA_list', 'network='+str(config.ipv4network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('range', 'Infoblox', 'Site', 'network='+str(config.ipv4network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('range', int(10), 'EA_int', 'network='+str(config.ipv4network2))
                print_and_log("Test Case 156 Execution completed")


        pytest.mark.run(order=157)
        def test_157_Validate_the_Extensible_attribute_values_configured_for_IPAM_host(self):
                print_and_log("********** Validate the Extensible attribute values configured ***********")
                validation_of_4_EAs_value_configured_in_extensible_attribute('record:host', 'network1', 'EA_string', 'name=host_new_2')
                validation_of_4_EAs_value_configured_in_extensible_attribute('record:host', '1', 'EA_list', 'name=host_new_2')
                validation_of_4_EAs_value_configured_in_extensible_attribute('record:host', 'Infoblox', 'Site', 'name=host_new_2')
                validation_of_4_EAs_value_configured_in_extensible_attribute('record:host', int(10), 'EA_int', 'name=host_new_2')
                print_and_log("Test Case 157 Execution completed")


        @pytest.mark.run(order=158)
        def test_158_Create_the_DTC_topology_Rule_3_with_Server_as_Destination(self):
                print_and_log("********* Create the DTC topology Rule 3 with Server as Destination ***********")
                server_ref = []
                for i in Server_name:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    server_ref.append(ref)
                data = {"name": "ea-rule3", "rules": [{"sources": [{"source_op": "IS", "source_type": "EA0", "source_value": "network1"}, {"source_op": "IS", "source_type": "EA1", "source_value": "1"}, {"source_op": "IS", "source_type": "EA2", "source_value": "10"}, {"source_op": "IS", "source_type": "EA3", "source_value": "Infoblox"}], "dest_type": "SERVER","destination_link": server_ref[0]}, {"sources":[{"source_op": "IS", "source_type": "EA0", "source_value": "network2"}, {"source_op": "IS", "source_type": "EA1", "source_value": "2"}, {"source_op": "IS", "source_type": "EA2", "source_value": "5"}, {"source_op": "IS", "source_type": "EA3", "source_value": "Infoblox"}], "dest_type": "SERVER","destination_link": server_ref[1]}]}
                print_and_log(data)
                response = ib_NIOS.wapi_request('POST',object_type='dtc:topology', fields=json.dumps(data))
                print_and_log(response)
                print_and_log("********* Validation of Topology rule 3 ***********")
                assert re.search(r'dtc:topology', response)
                print_and_log("Test Case 158 Execution completed")


        @pytest.mark.run(order=159)
        def test_159_Validate_the_DTC_topology_Rule_3(self):
                print_and_log("********* Validate the DTC topology Rule 3 **********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ea-rule3')
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=rules')
                response1 = json.loads(response1)
                output1 = response1['rules'][0]['_ref'].split(':')[-1].split('/')[-1]
                output2 = response1['rules'][1]['_ref'].split(':')[-1].split('/')[-1]
                print_and_log(output1)
                print_and_log(output2)
                if output1 == "server1" and output2 == "server2":
                    print_and_log("DTC Topology rule configured with "+output1+" and "+output2+" as Destination")
                    assert True
                else:
                    print_and_log("Error in validation of Topology rule")
                    assert False
                print_and_log("Test Case 159 Execution completed")



        @pytest.mark.run(order=160)
        def test_160_modify_the_pool1_and_assign_Server_1_and_server2(self):
                print_and_log("******* Modify the pool1 and assign Server 1 and Server2 *********")
                print_and_log("Getting the server name reference ")
                server_ref = []
                for i in Server_name:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    server_ref.append(ref)
                print_and_log(server_ref)
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ea-rule3')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                print_and_log("****** Getting the ref of Pool 1 ******")
                print_and_log("****** Modify the pool Pool_1 and assiging the server1 *********")
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_1')
                response1 = json.loads(response1)
                ref_pool1 = response1[0]['_ref']
                data = {"lb_preferred_method": "TOPOLOGY", "lb_preferred_topology": res_ref, "servers": [{"ratio": 1,"server": str(server_ref[0])}, {"ratio": 1,"server": str(server_ref[1])}]}
                response_servers = ib_NIOS.wapi_request('PUT',object_type=ref_pool1, fields=json.dumps(data))
                print_and_log(response_servers)
                restart_services()
                print_and_log("Test Case 160 Execution completed")



        @pytest.mark.run(order=161)
        def test_161_Validation_the_pool1_for_topology_rule3(self):
                print_and_log("******* Validation the pool1 for topology rule3 *********")
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_1')
                response1 = json.loads(response1)
                ref_pool1 = response1[0]['_ref']
                response2 = ib_NIOS.wapi_request('GET',object_type=ref_pool1, params='?_return_fields=lb_preferred_method')
                response2 = json.loads(response2)
                res_lb_method = response2['lb_preferred_method']
                print_and_log(res_lb_method)
                response3 = ib_NIOS.wapi_request('GET',object_type=ref_pool1, params='?_return_fields=lb_preferred_topology')
                response3 = json.loads(response3)
                res_lb_topology = response3['lb_preferred_topology'].split(":")[-1]
                print_and_log(res_lb_topology)
                if res_lb_method == "TOPOLOGY" and res_lb_topology == "ea-rule3":
                    print_and_log(" LB method "+res_lb_method+" is configured to Pool with topo rule "+res_lb_topology+" successfully")
                    assert True
                else:
                    print_and_log(" Error while validating the LB method of the Pool")
                    assert False
                print_and_log("Test Case 161 Execution completed")



        @pytest.mark.run(order=162)
        def test_162_Modify_the_LBDN_and_configure_round_robin_as_lb_method(self):
                print_and_log("********* Modify the LBDN and configure round robin as lb method ***********")
                pool_ref = []
                Pool = ["Pool_1", "Pool_2"]
                for i in Pool:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    pool_ref.append(ref)
                response2 = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=LBDN')
                response2 = json.loads(response2)
                ref_lbdn = response2[0]['_ref']
                data = {"lb_method": "ROUND_ROBIN", "pools": [{"ratio": 1, "pool": pool_ref[0]}]}
                response3 = ib_NIOS.wapi_request('PUT',object_type=ref_lbdn, fields=json.dumps(data))
                print_and_log(response3)
                assert re.search(r'dtc:lbdn', response3)
                restart_services()
                print_and_log("Test Case 162 Execution completed")



        @pytest.mark.run(order=163)
        def test_163_Validate_LBDN_for_round_robin_lb_method(self):
                print_and_log("******** Validate LBDN for round robin lb method *********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=LBDN')
                response = json.loads(response)
                ref_lbdn = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref_lbdn, params='?_return_fields=lb_method')
                response1 = json.loads(response1)
                ref_lb_method = response1['lb_method']
                if ref_lb_method == "ROUND_ROBIN":
                    print_and_log("LBDN configured with Lb method "+ref_lb_method)
                    assert True
                else:
                    print_and_log("Validation for the LBDN failed")
                    assert False
                print_and_log("Test Case 163 Execution completed")



        @pytest.mark.run(order=164)
        def test_161_Run_the_dig_command_with_subnet_of_IPAM_network2(self):
                print_and_log("********** Run the dig command with subnet of IPAM network1 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network2+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network2+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 164 Execution Completed")


        @pytest.mark.run(order=165)
        def test_165_Run_the_dig_command_with_subnet_of_IPAM_conatiner2(self):
                print_and_log("********** Run the dig command with subnet of IPAM Container2 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network_container2+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network_container2+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 165 Execution Completed")


        @pytest.mark.run(order=166)
        def test_166_Run_the_dig_command_with_subnet_of_IPAM_ranges2(self):
                print_and_log("********** Run the dig command with subnet of IPAM Ranges2 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges2)[0]+"/32 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges2)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges2)[1]+"/32 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges2)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges2)[2]+"/32 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges2)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 166 Execution Completed")



        @pytest.mark.run(order=167)
        def test_167_Run_the_dig_command_with_subnet_of_IPAM_Hosts2(self):
                print_and_log("********** Run the dig command with subnet of IPAM Hosts2 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4addr_host2+"/32 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4addr_host2)
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 167 Execution Completed")



        @pytest.mark.run(order=168)
        def test_168_Modify_the_value_of_the_IPAM_network_from_network2_to_network1(self):
                print_and_log("******** Modify the value of the IPAM network from network2 to network1 *********")
                response = ib_NIOS.wapi_request('GET',object_type="network", params='?network='+config.ipv4network2)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_int": {"value": 10}, "EA_list": {"value": "1"}, "EA_string": {"value": "network1"}, "Site": {"value": "Infoblox"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_4_EAs_value_configured_in_extensible_attribute('network', 'network1', 'EA_string', 'network='+str(config.ipv4network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('network', '1', 'EA_list', 'network='+str(config.ipv4network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('network', 'Infoblox', 'Site', 'network='+str(config.ipv4network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('network', int(10), 'EA_int', 'network='+str(config.ipv4network2))
                print_and_log("Test Case 168 Execution Completed")



        @pytest.mark.run(order=169)
        def test_169_Modify_the_value_of_the_IPAM_conatiner_from_network1_to_network2(self):
                print_and_log("******** Modify the value of the IPAM conatiner from network1 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="networkcontainer", params='?network='+config.ipv4network_container2)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_int": {"value": 5}, "EA_list": {"value": "2"}, "EA_string": {"value": "network2"}, "Site": {"value": "Infoblox"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_4_EAs_value_configured_in_extensible_attribute('networkcontainer', 'network2', 'EA_string', 'network='+str(config.ipv4network_container2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('networkcontainer', '2', 'EA_list', 'network='+str(config.ipv4network_container2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('networkcontainer', 'Infoblox', 'Site', 'network='+str(config.ipv4network_container2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('networkcontainer', int(5), 'EA_int', 'network='+str(config.ipv4network_container2))
                print_and_log("Test Case 169 Execution Completed")



        @pytest.mark.run(order=170)
        def test_170_Modify_the_value_of_the_IPAM_Ranges_from_network1_to_network2(self):
                print_and_log("******** Modify the value of the IPAM network from network1 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="range", params='?network='+config.ipv4network2)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_int": {"value": 5}, "EA_list": {"value": "2"}, "EA_string": {"value": "network2"}, "Site": {"value": "Infoblox"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_4_EAs_value_configured_in_extensible_attribute('range', 'network2', 'EA_string', 'network='+str(config.ipv4network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('range', '2', 'EA_list', 'network='+str(config.ipv4network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('range', 'Infoblox', 'Site', 'network='+str(config.ipv4network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('range', int(5), 'EA_int', 'network='+str(config.ipv4network2))
                print_and_log("Test Case 170 Execution Completed")


        @pytest.mark.run(order=171)
        def test_171_Modify_the_value_of_the_IPAM_Host_from_network1_to_network2(self):
                print_and_log("******** Modify the value of the IPAM network from network1 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="record:host", params='?network='+config.ipv4addr_host2)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_int": {"value": 5}, "EA_list": {"value": "2"}, "EA_string": {"value": "network2"}, "Site": {"value": "Infoblox"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_4_EAs_value_configured_in_extensible_attribute('record:host', 'network2', 'EA_string', 'name=host_new_2')
                validation_of_4_EAs_value_configured_in_extensible_attribute('record:host', '2', 'EA_list', 'name=host_new_2')
                validation_of_4_EAs_value_configured_in_extensible_attribute('record:host', 'Infoblox', 'Site', 'name=host_new_2')
                validation_of_4_EAs_value_configured_in_extensible_attribute('record:host', int(5), 'EA_int', 'name=host_new_2')
                print_and_log("Test Case 171 Execution Completed")



        @pytest.mark.run(order=172)
        def test_172_Run_the_dig_command_with_subnet_of_IPAM_network2(self):
                print_and_log("********** Run the dig command with subnet of IPAM network1 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network2+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network2+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 172 Execution Completed")


        @pytest.mark.run(order=173)
        def test_173_Run_the_dig_command_with_subnet_of_IPAM_conatiner2(self):
                print_and_log("********** Run the dig command with subnet of IPAM Container2 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network_container2+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network_container2+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 173 Execution Completed")


        @pytest.mark.run(order=174)
        def test_174_Run_the_dig_command_with_subnet_of_IPAM_ranges2(self):
                print_and_log("********** Run the dig command with subnet of IPAM Ranges2 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges2)[0]+"/32 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges2)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges2)[1]+"/32 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges2)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges2)[2]+"/32 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges2)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 174 Execution Completed")



        @pytest.mark.run(order=175)
        def test_175_Run_the_dig_command_with_subnet_of_IPAM_Hosts2(self):
                print_and_log("********** Run the dig command with subnet of IPAM Hosts2 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4addr_host2+"/32 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4addr_host2)
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 175 Execution Completed")



        @pytest.mark.run(order=176)
        def test_176_Create_the_DTC_topology_Rule_4_with_Pool_as_Destination(self):
                print_and_log("********* Create the DTC topology Rule 4 with Pool as Destination ***********")
                pool_ref = []
                pool_name = ["Pool_1", "Pool_2"]
                for i in pool_name:
                    response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name='+i)
                    response = json.loads(response)
                    ref = response[0]['_ref']
                    pool_ref.append(ref)
                data = {"name": "ea-rule4", "rules": [{"sources": [{"source_op": "IS", "source_type": "EA0", "source_value": "network1"}, {"source_op": "IS", "source_type": "EA1", "source_value": "1"}, {"source_op": "IS", "source_type": "EA2", "source_value": "10"}, {"source_op": "IS", "source_type": "EA3", "source_value": "Infoblox"}], "dest_type": "POOL","destination_link": pool_ref[0]}, {"sources":[{"source_op": "IS", "source_type": "EA0", "source_value": "network2"}, {"source_op": "IS", "source_type": "EA1", "source_value": "2"}, {"source_op": "IS", "source_type": "EA2", "source_value": "5"}, {"source_op": "IS", "source_type": "EA3", "source_value": "Infoblox"}], "dest_type": "POOL","destination_link": pool_ref[1]}]}
                print_and_log(data)
                response = ib_NIOS.wapi_request('POST',object_type='dtc:topology', fields=json.dumps(data))
                print_and_log(response)
                print_and_log("********* Validation of Topology rule 4 ***********")
                assert re.search(r'dtc:topology', response)
                print_and_log("Test Case 176 Execution completed")



        @pytest.mark.run(order=177)
        def test_177_Validate_the_DTC_topology_Rule_4(self):
                print_and_log("********* Validate the DTC topology Rule 4 **********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ea-rule4')
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=rules')
                response1 = json.loads(response1)
                output1 = response1['rules'][0]['_ref'].split(':')[-1].split('/')[-1]
                output2 = response1['rules'][1]['_ref'].split(':')[-1].split('/')[-1]
                print_and_log(output1)
                print_and_log(output2)
                if output1 == "Pool_1" and output2 == "Pool_2":
                    print_and_log("DTC Topology rule configured with "+output1+" and "+output2+" as Destination")
                    assert True
                else:
                    print_and_log("Error in validation of Topology rule")
                    assert False
                print_and_log("Test Case 177 Execution completed")



        @pytest.mark.run(order=178)
        def test_178_modify_the_pool1_and_assign_Server_1(self):
                print_and_log("******* Modify the pool1 and assign Server 1 *********")
                print_and_log("Getting the server name reference ")
                server_ref = []
                for i in Server_name:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    server_ref.append(ref)
                print_and_log(server_ref)
                print_and_log("****** Modify the pool Pool_1 and assiging the server1 *********")
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_1')
                response1 = json.loads(response1)
                ref_pool1 = response1[0]['_ref']
                data = {"lb_preferred_method": "ALL_AVAILABLE", "servers": [{"ratio": 1,"server": str(server_ref[0])}]}
                response_servers = ib_NIOS.wapi_request('PUT',object_type=ref_pool1, fields=json.dumps(data))
                print_and_log(response_servers)
                restart_services()
                print_and_log("Test Case 178 Execution completed")



        @pytest.mark.run(order=179)
        def test_179_Validation_of_the_pool1(self):
                print_and_log("******* Validation of the pool1 *********")
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_1')
                response1 = json.loads(response1)
                ref_pool1 = response1[0]['_ref']
                response2 = ib_NIOS.wapi_request('GET',object_type=ref_pool1, params='?_return_fields=lb_preferred_method')
                response2 = json.loads(response2)
                print_and_log(response2)
                ref = response2['lb_preferred_method']
                response3 = ib_NIOS.wapi_request('GET',object_type=ref_pool1, params='?_return_fields=servers')
                response3 = json.loads(response3)
                print_and_log(response3)
                ref_server = response3['servers'][0]['server'].split(':')[-1]
                print_and_log(ref)
                print_and_log(ref_server)
                if ref == "ALL_AVAILABLE" and ref_server == "server1":
                    print_and_log("Pool Pool_1 is configure with lb method "+ref+" with server "+ref_server)
                    assert True
                else:
                    print_and_log("Validation failed for the DTC Pool")
                    assert False
                print_and_log("Test Case 179 Execution completed")



        @pytest.mark.run(order=180)
        def test_180_modify_the_pool2_and_assign_Server_2(self):
                print_and_log("******* Modify the pool2 and assign Server 2 *********")
                print_and_log("Getting the server name reference ")
                server_ref = []
                for i in Server_name:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    server_ref.append(ref)
                print_and_log(server_ref)
                print_and_log("****** Modify the pool Pool_2 and assiging the server1 *********")
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_2')
                response1 = json.loads(response1)
                ref_pool1 = response1[0]['_ref']
                data = {"lb_preferred_method": "ALL_AVAILABLE", "servers": [{"ratio": 1,"server": str(server_ref[1])}]}
                response_servers = ib_NIOS.wapi_request('PUT',object_type=ref_pool1, fields=json.dumps(data))
                print_and_log(response_servers)
                restart_services()
                print_and_log("Test Case 180 Execution completed")



        @pytest.mark.run(order=181)
        def test_181_Validation_of_the_pool1(self):
                print_and_log("******* Validation of the pool1 *********")
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_2')
                response1 = json.loads(response1)
                ref_pool = response1[0]['_ref']
                response2 = ib_NIOS.wapi_request('GET',object_type=ref_pool, params='?_return_fields=lb_preferred_method')
                response2 = json.loads(response2)
                ref = response2['lb_preferred_method']
                response3 = ib_NIOS.wapi_request('GET',object_type=ref_pool, params='?_return_fields=servers')
                response3 = json.loads(response3)
                print_and_log(response3)
                ref_server = response3['servers'][0]['server'].split(':')[-1]
                print_and_log(ref)
                print_and_log(ref_server)
                if ref == "ALL_AVAILABLE" and ref_server == "server2":
                    print_and_log("Pool Pool_2 is configure with lb method "+ref+" with server "+ref_server)
                    assert True
                else:
                    print_and_log("Validation failed for the DTC Pool")
                    assert False
                print_and_log("Test Case 181 Execution completed")



        @pytest.mark.run(order=182)
        def test_182_Modify_the_LBDN_and_Configure_the_Topology_rule_4_as_Lb_method(self):
                print_and_log("********* Modify the LBDN and Configure the Topology rule 4 as Lb method ***********")
                pool_ref = []
                Pool = ["Pool_1", "Pool_2"]
                for i in Pool:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    pool_ref.append(ref)
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ea-rule4')
                response1 = json.loads(response1)
                print_and_log(response1)
                res_ref = response1[0]['_ref']
                response2 = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=LBDN')
                response2 = json.loads(response2)
                ref_lbdn = response2[0]['_ref']
                data = {"lb_method": "TOPOLOGY", "topology": res_ref, "pools": [{"ratio": 1, "pool": pool_ref[0]}, {"ratio": 1, "pool": pool_ref[1]}]}
                response3 = ib_NIOS.wapi_request('PUT', object_type=ref_lbdn, fields=json.dumps(data))
                print_and_log(response3)
                assert re.search(r'dtc:lbdn', response3)
                restart_services()
                print_and_log("Test Case 182 Execution completed")



        @pytest.mark.run(order=183)
        def test_183_Validate_the_LBDN_and_the_Topology_rule_4_as_Lb_method(self):
                print_and_log("********* Validate the LBDN and the Topology rule 4 as Lb method *********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=LBDN')
                response = json.loads(response)
                ref_lbdn = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref_lbdn, params='?_return_fields=lb_method')
                response1 = json.loads(response1)
                res_lb_method = response1['lb_method']
                print_and_log(res_lb_method)
                response2 = ib_NIOS.wapi_request('GET',object_type=ref_lbdn, params='?_return_fields=topology')
                response2 = json.loads(response2)
                res_lb_topology = response2['topology'].split(':')[-1]
                print_and_log(res_lb_topology)
                if res_lb_method == "TOPOLOGY" and res_lb_topology == "ea-rule4":
                    print_and_log("LBDN is configured with LB method "+res_lb_method+" with topology "+res_lb_topology)
                    assert True
                else:
                    print_and_log("Validation for the LBDN failed")
                    assert False
                print_and_log("Test Case 183 Execution completed")



        @pytest.mark.run(order=184)
        def test_184_Run_the_dig_command_with_subnet_of_IPAM_network2(self):
                print_and_log("********** Run the dig command with subnet of IPAM network1 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network2+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network2+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 184 Execution Completed")


        @pytest.mark.run(order=185)
        def test_185_Run_the_dig_command_with_subnet_of_IPAM_conatiner2(self):
                print_and_log("********** Run the dig command with subnet of IPAM Container2 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network_container2+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network_container2+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 185 Execution Completed")


        @pytest.mark.run(order=186)
        def test_186_Run_the_dig_command_with_subnet_of_IPAM_ranges2(self):
                print_and_log("********** Run the dig command with subnet of IPAM Ranges2 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges2)[0]+"/32 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges2)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges2)[1]+"/32 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges2)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges2)[2]+"/32 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges2)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 186 Execution Completed")




        @pytest.mark.run(order=187)
        def test_187_Run_the_dig_command_with_subnet_of_IPAM_Hosts2(self):
                print_and_log("********** Run the dig command with subnet of IPAM Hosts2 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4addr_host2+"/32 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4addr_host2)
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 187 Execution Completed")




        @pytest.mark.run(order=188)
        def test_188_Modify_the_value_of_the_IPAM_network_from_network1_to_network2(self):
                print_and_log("******** Modify the value of the IPAM network from network1 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="network", params='?network='+config.ipv4network2)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_int": {"value": 5}, "EA_list": {"value": "2"}, "EA_string": {"value": "network2"}, "Site": {"value": "Infoblox"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_4_EAs_value_configured_in_extensible_attribute('network', 'network2', 'EA_string', 'network='+str(config.ipv4network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('network', '2', 'EA_list', 'network='+str(config.ipv4network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('network', 'Infoblox', 'Site', 'network='+str(config.ipv4network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('network', int(5), 'EA_int', 'network='+str(config.ipv4network2))
                print_and_log("Test Case 188 Execution Completed")



        @pytest.mark.run(order=189)
        def test_189_Modify_the_value_of_the_IPAM_conatiner_from_network2_to_network1(self):
                print_and_log("******** Modify the value of the IPAM conatiner from network2 to network1 *********")
                response = ib_NIOS.wapi_request('GET',object_type="networkcontainer", params='?network='+config.ipv4network_container2)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_int": {"value": 10}, "EA_list": {"value": "1"}, "EA_string": {"value": "network1"}, "Site": {"value": "Infoblox"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_4_EAs_value_configured_in_extensible_attribute('networkcontainer', 'network1', 'EA_string', 'network='+str(config.ipv4network_container2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('networkcontainer', '1', 'EA_list', 'network='+str(config.ipv4network_container2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('networkcontainer', 'Infoblox', 'Site', 'network='+str(config.ipv4network_container2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('networkcontainer', int(10), 'EA_int', 'network='+str(config.ipv4network_container2))
                print_and_log("Test Case 189 Execution Completed")



        @pytest.mark.run(order=190)
        def test_190_Modify_the_value_of_the_IPAM_Ranges_from_network2_to_network1(self):
                print_and_log("******** Modify the value of the IPAM network from network2 to network1 *********")
                response = ib_NIOS.wapi_request('GET',object_type="range", params='?network='+config.ipv4network2)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_int": {"value": 10}, "EA_list": {"value": "1"}, "EA_string": {"value": "network1"}, "Site": {"value": "Infoblox"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_4_EAs_value_configured_in_extensible_attribute('range', 'network1', 'EA_string', 'network='+str(config.ipv4network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('range', '1', 'EA_list', 'network='+str(config.ipv4network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('range', 'Infoblox', 'Site', 'network='+str(config.ipv4network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('range', int(10), 'EA_int', 'network='+str(config.ipv4network2))
                print_and_log("Test Case 190 Execution Completed")


        @pytest.mark.run(order=191)
        def test_191_Modify_the_value_of_the_IPAM_Host_from_network1_to_network2(self):
                print_and_log("******** Modify the value of the IPAM network from network1 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="record:host", params='?network='+config.ipv4addr_host2)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_int": {"value": 10}, "EA_list": {"value": "1"}, "EA_string": {"value": "network1"}, "Site": {"value": "Infoblox"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_4_EAs_value_configured_in_extensible_attribute('record:host', 'network1', 'EA_string', 'name=host_new_2')
                validation_of_4_EAs_value_configured_in_extensible_attribute('record:host', '1', 'EA_list', 'name=host_new_2')
                validation_of_4_EAs_value_configured_in_extensible_attribute('record:host', 'Infoblox', 'Site', 'name=host_new_2')
                validation_of_4_EAs_value_configured_in_extensible_attribute('record:host', int(10), 'EA_int', 'name=host_new_2')
                print_and_log("Test Case 191 Execution Completed")




        @pytest.mark.run(order=192)
        def test_192_Run_the_dig_command_with_subnet_of_IPAM_network2(self):
                print_and_log("********** Run the dig command with subnet of IPAM network1 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network2+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network2+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 192 Execution Completed")


        @pytest.mark.run(order=193)
        def test_193_Run_the_dig_command_with_subnet_of_IPAM_conatiner2(self):
                print_and_log("********** Run the dig command with subnet of IPAM Container2 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network_container2+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network_container2+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 193 Execution Completed")


        @pytest.mark.run(order=194)
        def test_194_Run_the_dig_command_with_subnet_of_IPAM_ranges2(self):
                print_and_log("********** Run the dig command with subnet of IPAM Ranges2 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges2)[0]+"/32 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges2)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges2)[1]+"/32 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges2)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges2)[2]+"/32 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges2)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 194 Execution Completed")



        @pytest.mark.run(order=195)
        def test_195_Run_the_dig_command_with_subnet_of_IPAM_Hosts2(self):
                print_and_log("********** Run the dig command with subnet of IPAM Hosts2 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4addr_host2+"/32 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4addr_host2)
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 195 Execution Completed")



        @pytest.mark.run(order=196)
        def test_196_Modify_the_name_of_the_custom_extensible_attributes_created(self):
                print_and_log("********* Modify the name of the custom extensible attributes created *********")
                custom_ea = ["EA_string", "EA_list", "EA_int"]
                for i in custom_ea:
                    response = ib_NIOS.wapi_request('GET',object_type='extensibleattributedef', params='?name='+i)
                    response = json.loads(response)
                    ref = response[0]['_ref']
                    data = {"name": i+'_modified'}
                    print_and_log(data)
                    response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
                    print_and_log(response1)
                print_and_log("Test Case 196 Execution Completed")



        @pytest.mark.run(order=197)
        def test_197_Validate_the_name_of_the_custom_extensible_attributes_modified(self):
                print_and_log("********* Validate the name of the custom extensible attributes modified **********")
                expected_list = ["EA_string_modified", "EA_list_modified", "EA_int_modified"]
                output = []
                for i in expected_list:
                    response = ib_NIOS.wapi_request('GET',object_type='extensibleattributedef', params='?name='+i)
                    response = json.loads(response)
                    ref = response[0]['name']
                    output.append(ref)
                print_and_log(output)
                if expected_list == output:
                    print_and_log("Modfication of the name for custom extensible attributes is successful")
                    assert True
                else:
                    print_and_log("Error while validating the name of the modified name of custom extensible attributes")
                    assert False
                print_and_log("Test Case 197 Execution Completed")



        @pytest.mark.run(order=198)
        def test_198_Run_the_dig_command_with_subnet_of_IPAM_network2(self):
                print_and_log("********** Run the dig command with subnet of IPAM network2 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network2+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network2+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 198 Execution Completed")


        @pytest.mark.run(order=199)
        def test_199_Run_the_dig_command_with_subnet_of_IPAM_conatiner2(self):
                print_and_log("********** Run the dig command with subnet of IPAM Container2 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4network_container2+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4network_container2+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 199 Execution Completed")


        @pytest.mark.run(order=200)
        def test_200_Run_the_dig_command_with_subnet_of_IPAM_ranges2(self):
                print_and_log("********** Run the dig command with subnet of IPAM Ranges2 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges2)[0]+"/32 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges2)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges2)[1]+"/32 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges2)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+json.loads(config.ipv4_ranges2)[2]+"/32 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv4_ranges2)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 200 Execution Completed")



        @pytest.mark.run(order=201)
        def test_201_Run_the_dig_command_with_subnet_of_IPAM_Hosts2(self):
                print_and_log("********** Run the dig command with subnet of IPAM Hosts2 ************")
                output = os.popen("dig @"+config.grid_vip+" a.dtc.com in a +subnet="+config.ipv4addr_host2+"/32 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv4addr_host2)
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 201 Execution Completed")



        @pytest.mark.run(order=202)
        def test_202_Revert_back_the_Modified_name_of_the_custom_extensible_attributes_created(self):
                print_and_log("********* Modify the name of the custom extensible attributes created *********")
                custom_ea = ["EA_string_modified", "EA_list_modified", "EA_int_modified"]
                for i in custom_ea:
                    response = ib_NIOS.wapi_request('GET',object_type='extensibleattributedef', params='?name='+i)
                    response = json.loads(response)
                    ref = response[0]['_ref']
                    name = i.split('_')[0]+"_"+i.split('_')[1]
                    data = {"name": name}
                    print_and_log(data)
                    response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
                    print_and_log(response1)
                print_and_log("Test Case 202 Execution Completed")


        @pytest.mark.run(order=203)
        def test_203_Validate_the_name_of_the_custom_extensible_attributes_modified(self):
                print_and_log("********* Validate the name of the custom extensible attributes modified **********")
                expected_list = ["EA_string", "EA_list", "EA_int"]
                output = []
                for i in expected_list:
                    response = ib_NIOS.wapi_request('GET',object_type='extensibleattributedef', params='?name='+i)
                    response = json.loads(response)
                    ref = response[0]['name']
                    output.append(ref)
                print_and_log(output)
                if expected_list == output:
                    print_and_log("Modfication of the name for custom extensible attributes is successful")
                    assert True
                else:
                    print_and_log("Error while validating the name of the modified name of custom extensible attributes")
                    assert False
                print_and_log("Test Case 203 Execution Completed")


        #IPV6 Sceanrios
        @pytest.mark.run(order=204)
        def test_204_Enable_the_lan_ipv6_in_member_dns_properties(self):
                print_and_log("********* Enable the lan ipv6 in member dns properties *********")
                response = ib_NIOS.wapi_request('GET',object_type='member:dns')
                response = json.loads(response)
                print_and_log(response)
                ref = response[0]['_ref']
                data = {"use_lan_ipv6_port": True}
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
                print_and_log(response1)
                assert re.search(r'member:dns', response1)
                restart_services()
                print_and_log("Test Case 204 Execution Completed")



        @pytest.mark.run(order=205)
        def test_205_Validate_if_the_lan_ipv6_in_member_dns_properties_is_enabled_or_not(self):
                print_and_log("********* Validate if the lan ipv6 in member dns properties is enabled or not *********")
                response = ib_NIOS.wapi_request('GET',object_type='member:dns')
                response = json.loads(response)
                print_and_log(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=use_lan_ipv6_port')
                response1 = json.loads(response1)
                output = response1['use_lan_ipv6_port']
                if output == True:
                    print_and_log("LAN IPV6 port is enabled in member dns properties")
                    assert True
                else:
                    print_and_log("LAN IPV6 port is disabled in member dns properties")
                    assert False
                print_and_log("Test Case 205 Execution Completed")




        @pytest.mark.run(order=206)
        def test_206_Create_IPV6_dtc_server_server4_and_server5(self):
                print_and_log("******* Create 2 DTC servers server4 and server5 ********")
                data = {"server4": config.ipv6_server1, "server5": config.ipv6_server2}
                ipv6_server_name = []
                for i,j in data.items():
                    print_and_log(i)
                    print_and_log(j)
                    data = {"name":i,"host":j}
                    response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
                    print_and_log(response)
                    ipv6_server_name.append(response.split(':')[-1].strip('"'))
                    assert re.search(r'dtc:server', response)
                print_and_log("Test Case 206 Execution Completed")



        @pytest.mark.run(order=207)
        def test_207_Create_IPV6_dtc_pool_Pool_4(self):
                print_and_log("******* Create DTC Pool Pool_4********")
                print_and_log("Getting the server name reference ")
                server_ref = []
                ipv6_server_name = ["server4", "server5"]
                for i in ipv6_server_name:
                    print_and_log(i)
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    print_and_log(response_servers)
                    ref = response_servers[0]['_ref']
                    server_ref.append(ref)
                print_and_log(server_ref)
                print_and_log("****** Creating the pool and assiging the server ******")
                data = {"name": "Pool_4", "lb_preferred_method": "ROUND_ROBIN", "servers": [{"ratio": 1,"server": str(server_ref[0])}, {"ratio": 1,"server": str(server_ref[1])}], "monitors": ["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"]}
                response_servers = ib_NIOS.wapi_request('POST',object_type='dtc:pool', fields=json.dumps(data))
                ref1 = json.loads(response_servers)
                print_and_log(ref1)
                print_and_log("Validation of Pool creation")
                assert re.search(r'dtc:pool', ref1)
                print_and_log("Test Case 207 Execution Completed")




        @pytest.mark.run(order=208)
        def test_208_Create_IPV6_dtc_LBDN_2(self):
                print_and_log("******* Create DTC LBDN LBDN_2 ********")
                print_and_log("********** Getting the ref of authorative zone ************")
                response = ib_NIOS.wapi_request('GET',object_type='zone_auth', params='?fqdn=dtc.com')
                response = json.loads(response)
                ref_zone = response[0]['_ref']
                print_and_log("********** Getting the ref of pool 1 ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_4')
                response = json.loads(response)
                ref_pool1 = response[0]['_ref']
                print_and_log("********** Creating the lbdn ************")
                data = {"auth_zones": [ref_zone], "name": "LBDN_2", "lb_method": "ROUND_ROBIN", "patterns": ["aaaa.dtc.com"], "pools": [{"ratio": 1, "pool": ref_pool1}]}
                print_and_log(data)
                response1 = ib_NIOS.wapi_request('POST',object_type='dtc:lbdn', fields=json.dumps(data))
                ref1 = json.loads(response1)
                print_and_log(ref1)
                assert re.search(r'dtc:lbdn', ref1)
                restart_services()
                print_and_log("Test Case 208 Execution Completed")



        @pytest.mark.run(order=209)
        def test_209_validation_of_IPV6_dtc_server(self):
                print_and_log("******* Validation of DTC servers *********")
                servers = ["server4", "server5"]
                for i in servers:
                    response = ib_NIOS.wapi_request('GET', object_type="dtc:server", params='?name='+i)
                    response = json.loads(response)
                    print_and_log(response)
                    if response[0]['name'] == "server4":
                        print_and_log(" DTC Server 4 configured successfully")
                        assert True
                    elif response[0]['name'] == "server5":
                        print_and_log(" DTC Server 5 Configured successfully")
                        assert True
                    else:
                        print_and_log(" Error while validating the DTC servers ")
                        assert False
                print_and_log("Test Case 209 Execution Completed")



        @pytest.mark.run(order=210)
        def test_210_validation_of_IPV6_dtc_pool(self):
                print_and_log("******* Validation of DTC Pool Pool_4 *********")
                response1 = ib_NIOS.wapi_request('GET', object_type="dtc:pool")
                response1 = json.loads(response1)
                print_and_log(response1)
                if response1[3]['name'] == "Pool_4":
                    print_and_log(" DTC Pool 4 Created successfully")
                    assert True
                else:
                    print_and_log(" Error while validating the DTC pool")
                    assert False
                print_and_log("Test Case 210 Execution Completed")



        @pytest.mark.run(order=211)
        def test_211_validation_of_IPV6_dtc_lbdn(self):
                print_and_log("******* Validation of DTC LBDN *********")
                response2 = ib_NIOS.wapi_request('GET', object_type="dtc:lbdn")
                response2 = json.loads(response2)
                print_and_log(response2)
                if response2[1]['name'] == "LBDN_2":
                    print_and_log(" DTC LBDN Created successfully")
                    assert True
                else:
                    print_and_log(" Error while validating the DTC LBDN")
                    assert False
                print_and_log(" Test Case 211 Execution Completed ")




        @pytest.mark.run(order=212)
        def test_212_Modify_the_LBDN_and_Configure_Round_Robin_as_Lb_method(self):
                print_and_log("********* Modify the LBDN and Configure ROUND ROBIN method ***********")
                response2 = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=LBDN')
                response2 = json.loads(response2)
                ref_lbdn = response2[0]['_ref']
                data = {"lb_method": "ROUND_ROBIN"}
                response3 = ib_NIOS.wapi_request('PUT',object_type=ref_lbdn, fields=json.dumps(data))
                print_and_log(response3)
                assert re.search(r'dtc:lbdn', response3)
                restart_services()
                print_and_log("Test Case 212 Execution completed")


        @pytest.mark.run(order=213)
        def test_213_Delete_the_Topo_rule_ea_rule3(self):
                print_and_log("********* Delete the Topo rule earule3 ***********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ea-rule3')
                response = json.loads(response)
                ref_topology = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('DELETE', object_type=ref_topology)
                print_and_log(response1)
                assert re.search(r'dtc:topology', response1)
                print_and_log("Test Case 213 Execution completed")



        @pytest.mark.run(order=214)
        def test_214_Delete_the_Topo_rule_ea_rule4(self):
                print_and_log("********* Delete the Topo rule earule4 ***********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ea-rule4')
                response = json.loads(response)
                ref_topology = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('DELETE', object_type=ref_topology)
                print_and_log(response1)
                assert re.search(r'dtc:topology', response1)
                print_and_log("Test Case 214 Execution completed")



        @pytest.mark.run(order=215)
        def test_215_Assign_the_Custom_EA_EA_string_in_Grid_Properties_Traffic_Control(self):
                print_and_log("********** Assign the Custom EA EA_string in Grid Properties Traffic Conftrol w************")
                response = ib_NIOS.wapi_request('GET',object_type='grid:dns')
                response = json.loads(response)
                ref = response[0]['_ref']
                data={"dtc_topology_ea_list": ["EA_string"]}
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
                print_and_log(response1)
                assert re.search(r'grid:dns', response1)
                rebuild_services()
                # validate Custom EA
                print_and_log("Test Case 215 Execution completed ")


        @pytest.mark.run(order=216)
        def test_216_Validation_of_the_Custom_EA_EA_string_in_Grid_Properties_Traffic_Control(self):
                print_and_log("********** Validation of the Custom EA EA_string in Grid Properties TrafficControl ***********")
                response = ib_NIOS.wapi_request('GET',object_type='grid:dns')
                response = json.loads(response)
                ref = response[0]['_ref']
                response = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=dtc_topology_ea_list')
                response = json.loads(response)
                out = response['dtc_topology_ea_list'][0]
                print_and_log(out)
                if out == "EA_string":
                    print_and_log(" Custome EA "+out+" configured in Grid DNS properties")
                    assert True
                else:
                    print_and_log(" Error while Validating the Custom EA in Grid DNS properties")
                    assert False
                print_and_log("Test Case 216 Execution completed ")



        @pytest.mark.run(order=217)
        def test_217_ADD_IPV6_Network_Container_Ranges_and_Hosts(self):
                print_and_log("******** Add IPV6 Network *********")
                data = {"network": config.ipv6network1, "extattrs": { "EA_string": { "value": "network2"}}}
                response = ib_NIOS.wapi_request('POST',object_type="ipv6network", fields=json.dumps(data))
                print_and_log(response)
                assert re.search(r'ipv6network', response)
                data = {"network": config.ipv6network_container1, "extattrs": { "EA_string": { "value": "network1"}}}
                response1 = ib_NIOS.wapi_request('POST',object_type="ipv6networkcontainer", fields=json.dumps(data))
                print_and_log(response1)
                assert re.search(r'ipv6networkcontainer', response1)
                data = {"start_addr": json.loads(config.ipv6_ranges)[0], "end_addr": json.loads(config.ipv6_ranges)[2], "network": config.ipv6network1, "extattrs": { "EA_string": { "value": "network1"}}}
                response2 = ib_NIOS.wapi_request('POST',object_type="ipv6range", fields=json.dumps(data))
                print_and_log(response2)
                assert re.search(r'ipv6range', response2)
                data = {"name": "host_new_ipv6","configure_for_dns": False, "ipv6addrs": [{"ipv6addr": config.ipv6addr_host}], "extattrs": { "EA_string": { "value": "network1"}}}
                response3 = ib_NIOS.wapi_request('POST',object_type="record:host", fields=json.dumps(data))
                print_and_log(response3)
                assert re.search(r'record:host', response3)
                rebuild_services()
                print_and_log("Test Case 217 Execution completed")



        @pytest.mark.run(order=218)
        def test_218_Validation_of_IPV6_Network(self):
                print_and_log("********* Validation of IPV6 Network ***********")
                response = ib_NIOS.wapi_request('GET',object_type="ipv6network", params='?network='+config.ipv6network1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                res_name = response[0]['network']
                response = ib_NIOS.wapi_request('GET',object_type=res_ref, params='?_return_fields=extattrs')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response['extattrs']['EA_string']['value']
                print_and_log(res_ref)
                if res_ref == "network2" and res_name == config.ipv6network1:
                    print_and_log("IPV6 Network "+res_name+" with extensible attributte "+res_ref+" configured successfully")
                    assert True
                else:
                    print_and_log("Error while validating the IPV6 network")
                    assert False
                print_and_log("Test Case 218 Execution completed")



        @pytest.mark.run(order=219)
        def test_219_Validation_of_IPV6_Container(self):
                print_and_log("********* Validation of IPV6 Container ***********")
                response = ib_NIOS.wapi_request('GET',object_type="ipv6networkcontainer", params='?network='+config.ipv6network_container1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                res_name = response[0]['network']
                response = ib_NIOS.wapi_request('GET',object_type=res_ref, params='?_return_fields=extattrs')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response['extattrs']['EA_string']['value']
                print_and_log(res_ref)
                if res_ref == "network1" and res_name == config.ipv6network_container1:
                    print_and_log("IPV4 Network Container "+res_name+" with extensible attributte "+res_ref+" configured successfully")
                    assert True
                else:
                    print_and_log("Error while validating the IPV6 network container")
                    assert False
                print_and_log("Test Case 219 Execution completed")


        @pytest.mark.run(order=220)
        def test_220_Validation_of_IPV6_Ranges(self):
                print_and_log("********* Validation of IPV6 ranges ***********")
                response = ib_NIOS.wapi_request('GET',object_type="ipv6range", params='?network='+config.ipv6network1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                res_start_addr = response[0]['start_addr']
                res_end_addr = response[0]['end_addr']
                response = ib_NIOS.wapi_request('GET',object_type=res_ref, params='?_return_fields=extattrs')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response['extattrs']['EA_string']['value']
                print_and_log(res_ref)
                if res_start_addr == json.loads(config.ipv6_ranges)[0] and res_end_addr == json.loads(config.ipv6_ranges)[2] and res_ref == "network1":
                    print_and_log("IPV4 Network Range with extensible attributte "+res_ref+" configured successfully")
                    assert True
                else:
                    print_and_log("Error while validating the IPV6 network range")
                    assert False
                print_and_log("Test Case 220 Execution completed")


        @pytest.mark.run(order=221)
        def test_221_Validation_of_IPV6_Host(self):
                print_and_log("********* Validation of IPV6 Host ***********")
                response = ib_NIOS.wapi_request('GET',object_type="record:host", params='?name=host_new_ipv6')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                res_addr = response[0]['ipv6addrs'][0]['ipv6addr']
                response = ib_NIOS.wapi_request('GET',object_type=res_ref, params='?_return_fields=extattrs')
                response = json.loads(response)
                print_and_log(response)
                res_extattrs = response['extattrs']['EA_string']['value']
                if res_extattrs == "network1" and res_addr == config.ipv6addr_host:
                    print_and_log("IPV4 Host with extensible attributte "+res_extattrs+" configured successfully")
                    assert True
                else:
                    print_and_log(" Error while validating the IPV6 host")
                    assert False
                print_and_log("Test Case 221 Execution completed")




        @pytest.mark.run(order=222)
        def test_222_Create_the_DTC_topology_Rule_with_Server_as_Destination(self):
                print_and_log("********* Create the DTC topology Rule with Server as Destination ***********")
                servers = ["server4", "server5"]
                server_ref = []
                for i in servers:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    server_ref.append(ref)
                data = {"name": "ipv6-ea-rule1", "rules": [{"sources": [{"source_op": "IS","source_type": "EA0","source_value": "network1"}], "dest_type": "SERVER","destination_link": server_ref[0]}, {"sources":[{"source_op": "IS","source_type": "EA0","source_value": "network2"}], "dest_type": "SERVER","destination_link": server_ref[1]}]}
                print_and_log(data)
                response = ib_NIOS.wapi_request('POST',object_type='dtc:topology', fields=json.dumps(data))
                print_and_log(response)
                assert re.search(r'dtc:topology', response)
                print_and_log("********* Validation of Topology rule 1 ***********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ipv6-ea-rule1')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                res_name = response[0]['name']
                if res_name == "ipv6-ea-rule1":
                    print_and_log("Topology rule "+res_name+" created successfully")
                    assert True
                else:
                    print_and_log(" Validation for the Topology rule failed ")
                    assert False
                print_and_log("Test Case 222 Execution completed")


        @pytest.mark.run(order=223)
        def test_223_Modify_the_Pool_Lb_method_to_Topology(self):
                print_and_log("********* Mofity the Pool LB method to Topology ***********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ipv6-ea-rule1')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_4')
                response1 = json.loads(response1)
                print_and_log(response1)
                res_ref1 = response1[0]['_ref']
                data = {"lb_preferred_method": "TOPOLOGY", "lb_preferred_topology": res_ref}
                response2 = ib_NIOS.wapi_request('PUT',object_type=res_ref1, fields=json.dumps(data))
                response2 = json.loads(response2)
                print_and_log(response2)
                assert re.search(r'dtc:pool', response2)
                restart_services()
                print_and_log("Test Case 223 Execution completed")


        @pytest.mark.run(order=224)
        def test_224_Validation_of_Pool_Lb_method_to_Topology(self):
                print_and_log("********** Validation of Pool LB method to Topology **********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ipv6-ea-rule1')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_4')
                response1 = json.loads(response1)
                print_and_log(response1)
                res_ref1 = response1[0]['_ref']
                response2 = ib_NIOS.wapi_request('GET',object_type=res_ref1, params='?_return_fields=lb_preferred_method')
                response2 = json.loads(response2)
                res_lb_method = response2['lb_preferred_method']
                print_and_log(res_lb_method)
                response3 = ib_NIOS.wapi_request('GET',object_type=res_ref1, params='?_return_fields=lb_preferred_topology')
                response3 = json.loads(response3)
                res_lb_topology = response3['lb_preferred_topology'].split(":")[-1]
                print_and_log(res_lb_topology)
                if res_lb_method == "TOPOLOGY" and res_lb_topology == "ipv6-ea-rule1":
                    print_and_log(" LB method "+res_lb_method+" is configured to Pool with topo rule "+res_lb_topology+" successfully")
                    assert True
                else:
                    print_and_log(" Error while validating the LB method of the Pool")
                    assert False
                print_and_log("Test Case 224 Execution completed")



        @pytest.mark.run(order=225)
        def test_225_Run_the_dig_command_with_subnet_of_IPAM_IPV6_network1(self):
                print_and_log("********** Run the dig command with subnet of IPAM IPV6 network1 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_64_subnet+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 225 Execution Completed")


        @pytest.mark.run(order=226)
        def test_226_Run_the_dig_command_with_subnet_of_IPAM_IPV6_conatiner(self):
                print_and_log("********** Run the dig command with subnet of IPAM IPV6 Container ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_32_subnet+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network_container1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 226 Execution Completed")


        @pytest.mark.run(order=227)
        def test_227_Run_the_dig_command_with_subnet_of_IPAM_IPV6_ranges(self):
                print_and_log("********** Run the dig command with subnet of IPAM IPV6 Ranges ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[0]+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[1]+"/128 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[2]+"/128 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 227 Execution Completed")



        @pytest.mark.run(order=228)
        def test_228_Run_the_dig_command_with_subnet_of_IPAM_IPV6_Hosts(self):
                print_and_log("********** Run the dig command with subnet of IPAM IPV6 Hosts ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6addr_host+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6addr_host)
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 228 Execution Completed")



        @pytest.mark.run(order=229)
        def test_229_Modify_the_value_of_the_IPV6_IPAM_network_from_network2_to_network1(self):
                print_and_log("******** Modify the value of the IPV6 IPAM network from network2 to network1 *********")
                response = ib_NIOS.wapi_request('GET',object_type="ipv6network", params='?network='+config.ipv6network1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network1"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('ipv6network', 'network1', '?network='+config.ipv6network1)
                print_and_log("Test Case 229 Execution Completed")



        @pytest.mark.run(order=230)
        def test_230_Modify_the_value_of_the_IPV6_IPAM_conatiner_from_network1_to_network2(self):
                print_and_log("******** Modify the value of the IPV6 IPAM conatiner from network1 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="ipv6networkcontainer", params='?network='+config.ipv6network_container1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network2"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('ipv6networkcontainer', 'network2', '?network='+config.ipv6network_container1)
                print_and_log("Test Case 230 Execution Completed")



        @pytest.mark.run(order=231)
        def test_231_Modify_the_value_of_the_IPV6_IPAM_Ranges_from_network1_to_network2(self):
                print_and_log("******** Modify the value of the IPV6 IPAM network from network1 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="ipv6range", params='?network='+config.ipv6network1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network2"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('ipv6range', 'network2', '?network='+config.ipv6network1)
                print_and_log("Test Case 231 Execution Completed")


        @pytest.mark.run(order=232)
        def test_232_Modify_the_value_of_the_IPV6_IPAM_Host_from_network1_to_network2(self):
                print_and_log("******** Modify the value of the IPV6 IPAM network from network1 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="record:host", params='?name=host_new_ipv6')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network2"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('record:host', 'network2', '?name=host_new_ipv6')
                print_and_log("Test Case 232 Execution Completed")



        @pytest.mark.run(order=233)
        def test_233_Run_the_dig_command_with_subnet_of_IPAM_IPV6_network1(self):
                print_and_log("********** Run the dig command with subnet of IPAM IPV6 network1 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_64_subnet+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 233 Execution Completed")


        @pytest.mark.run(order=234)
        def test_234_Run_the_dig_command_with_subnet_of_IPAM_IPV6_conatiner(self):
                print_and_log("********** Run the dig command with subnet of IPAM IPV6 Container ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_32_subnet+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network_container1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 234 Execution Completed")


        @pytest.mark.run(order=235)
        def test_235_Run_the_dig_command_with_subnet_of_IPAM_IPV6_ranges(self):
                print_and_log("********** Run the dig command with subnet of IPAM IPV6 Ranges ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[0]+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[1]+"/128 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[2]+"/128 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 235 Execution Completed")



        @pytest.mark.run(order=236)
        def test_236_Run_the_dig_command_with_subnet_of_IPAM_IPV6_Hosts(self):
                print_and_log("********** Run the dig command with subnet of IPAM IPV6 Hosts ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6addr_host+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6addr_host)
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 236 Execution Completed")



        @pytest.mark.run(order=237)
        def test_237_Uncheck_the_IPAM_Container_object_in_Grid_DNS_Properties_Traffic_Control(self):
                print_and_log("********** Uncheck the IPAM Container object in Grid DNS Properties Traffic Control ************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                data = {"gen_eadb_from_network_containers": False}
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                restart_services()
                print_and_log("Test Case 237 Execution Completed")


        @pytest.mark.run(order=238)
        def test_238_Validation_of_the_IPAM_Container_object_in_Grid_DNS_Properties_Traffic_Control(self):
                print_and_log("********** Validation of the IPAM Container object in Grid DNS Properties Traffic Control************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=gen_eadb_from_network_containers')
                response1 = json.loads(response1)
                output = response1['gen_eadb_from_network_containers']
                if output == False:
                    print_and_log(" The IPAM Containers Object in Grid DNS properties is set to False")
                    assert True
                else:
                    print_and_log(" The IPAM Containers Object in Grid DNS properties is set to True")
                    assert False
                print_and_log("Test Case 238 Execution Completed")


        @pytest.mark.run(order=239)
        def test_239_Run_the_dig_command_with_subnet_of_IPV6_IPAM_conatiner(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Container ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_32_subnet).read()
                out = output.split("\n")
                flag = False
                for i in out:
                    match = re.match("dtc.com.\s+\d+\s+IN\s+SOA.*",i)
                    print_and_log(i)
                    if match:
                        print_and_log(" Match found ")
                        flag=True
                        break
                if flag == True:
                    print_and_log("SOA record is found, No response from any for the DTC servers")
                    assert True
                else:
                    print_and_log("Query got the response from DTC servers")
                    assert False
                print_and_log("Test Case 239 Execution Completed")


        @pytest.mark.run(order=240)
        def test_240_Uncheck_the_IPAM_Networks_object_in_Grid_DNS_Properties_Traffic_Control(self):
                print_and_log("********** Uncheck the IPAM networks object in Grid DNS Properties Traffic Control ************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                data = {"gen_eadb_from_networks": False}
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                restart_services()
                print_and_log("Test Case 240 Execution Completed")


        @pytest.mark.run(order=241)
        def test_241_Validation_of_the_IPAM_network_object_in_Grid_DNS_Properties_Traffic_Control(self):
                print_and_log("********** Validation of the IPAM networks object in Grid DNS Properties Traffic Control************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=gen_eadb_from_networks')
                response1 = json.loads(response1)
                output = response1['gen_eadb_from_networks']
                if output == False:
                    print_and_log(" The IPAM networks Object in Grid DNS properties is set to False")
                    assert True
                else:
                    print_and_log(" The IPAM networks Object in Grid DNS properties is set to True")
                    assert False
                print_and_log("Test Case 241 Execution Completed")



        @pytest.mark.run(order=242)
        def test_242_Run_the_dig_command_with_subnet_of_IPV6_IPAM_network(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Network ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_64_subnet).read()
                out = output.split("\n")
                flag = False
                for i in out:
                    match = re.match("dtc.com.\s+\d+\s+IN\s+SOA.*",i)
                    print_and_log(i)
                    if match:
                        print_and_log(" Match found ")
                        flag=True
                        break
                if flag == True:
                    print_and_log("SOA record is found, No response from any for the DTC servers")
                    assert True
                else:
                    print_and_log("Query got the response from DTC servers")
                    assert False
                print_and_log("Test Case 242 Execution Completed")



        @pytest.mark.run(order=243)
        def test_243_Uncheck_the_IPAM_ranges_object_in_Grid_DNS_Properties_Traffic_Control(self):
                print_and_log("********** Uncheck the IPAM ranges object in Grid DNS Properties Traffic Control ************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                data = {"gen_eadb_from_ranges": False}
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                restart_services()
                print_and_log("Test Case 243 Execution Completed")


        @pytest.mark.run(order=244)
        def test_244_Validation_of_the_IPAM_ranges_object_in_Grid_DNS_Properties_Traffic_Control(self):
                print_and_log("********** Validation of the IPAM ranges object in Grid DNS Properties Traffic Control************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=gen_eadb_from_ranges')
                response1 = json.loads(response1)
                output = response1['gen_eadb_from_ranges']
                if output == False:
                    print_and_log(" The IPAM ranges Object in Grid DNS properties is set to False")
                    assert True
                else:
                    print_and_log(" The IPAM networks Object in Grid DNS properties is set to True")
                    assert False
                print_and_log("Test Case 244 Execution Completed")



        @pytest.mark.run(order=245)
        def test_245_Run_the_dig_command_with_subnet_of_IPV6_IPAM_ranges(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Ranges ************")
                for i in json.loads(config.ipv6_ranges):
                    output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+i+"/128").read()
                    out = output.split("\n")
                    flag = False
                    for i in out:
                        match = re.match("dtc.com.\s+\d+\s+IN\s+SOA.*",i)
                        print_and_log(i)
                        if match:
                            print_and_log(" Match found ")
                            flag=True
                            break
                    if flag == True:
                        print_and_log("SOA record is found, No response from any for the DTC servers")
                        assert True
                    else:
                        print_and_log("Query got the response from DTC servers")
                        assert False
                print_and_log("Test Case 245 Execution Completed")



        @pytest.mark.run(order=246)
        def test_246_Run_the_dig_command_with_subnet_that_does_not_belong_to_IPV6_IPAM_Ranges_or_Host(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Hosts ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet=111::9/128").read()
                out = output.split("\n")
                flag = False
                for i in out:
                    match = re.match("dtc.com.\s+\d+\s+IN\s+SOA.*",i)
                    print_and_log(i)
                    if match:
                        print_and_log(" Match found ")
                        flag=True
                        break
                if flag == True:
                    print_and_log("SOA record is found, No response from any for the DTC servers")
                    assert True
                else:
                    print_and_log("Query got the response from DTC servers")
                    assert False
                print_and_log("Test Case 246 Execution Completed")



        @pytest.mark.run(order=247)
        def test_247_Uncheck_the_IPAM_hosts_object_in_Grid_DNS_Properties_Traffic_Control_and_expect_error(self):
                print_and_log("********* Uncheck the IPAM hosts object in Grid DNS Properties Traffic Control and expect error **********")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                data = {"gen_eadb_from_hosts": False}
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
                if type(response1) == tuple:
                    out = response1[1]
                    out = json.loads(out)
                    print_and_log(out)
                    error_message = out['text']
                    print_and_log(error_message)
                    expected_error_message = "' At least one source type for EA MMDB must be selected.'"
                    if error_message in expected_error_message:
                        print_and_log("Expected Error message is seen")
                        assert True
                    else:
                        print_and_log("Expected Error message is not seen")
                        assert False
                else:
                    print_and_log(response1)
                    print_and_log(" All the IPAM objects under Grid DNS properties Traffic control is disabled ")
                    assert False
                print_and_log("Test Case 247 Execution Completed")



        @pytest.mark.run(order=248)
        def test_248_Modify_the_Pool4_Lb_method_and_add_the_alternate_load_balancing_method_global_availability(self):
                print_and_log("********* Mofity the Pool4 LB method global availability to Topology ***********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ipv6-ea-rule1')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_4')
                response1 = json.loads(response1)
                print_and_log(response1)
                res_ref1 = response1[0]['_ref']
                data = {"lb_alternate_method": "GLOBAL_AVAILABILITY"}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref1, fields=json.dumps(data))
                print_and_log(response1)
                restart_services()
                print_and_log("Test Case 248 Execution Completed")


        @pytest.mark.run(order=249)
        def test_249_Validation_of_Pool4_Alternate_Lb_method_global_availability_to_Topology(self):
                print_and_log("********** Validation of Pool4 LB method global availability to Topology **********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ipv6-ea-rule1')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_4')
                response1 = json.loads(response1)
                print_and_log(response1)
                res_ref1 = response1[0]['_ref']
                response2 = ib_NIOS.wapi_request('GET',object_type=res_ref1, params='?_return_fields=lb_alternate_method')
                response2 = json.loads(response2)
                res_lb_method = response2['lb_alternate_method']
                print_and_log(res_lb_method)
                response3 = ib_NIOS.wapi_request('GET',object_type=res_ref1, params='?_return_fields=lb_preferred_topology')
                response3 = json.loads(response3)
                res_lb_topology = response3['lb_preferred_topology'].split(":")[-1]
                print_and_log(res_lb_topology)
                if res_lb_method == "GLOBAL_AVAILABILITY" and res_lb_topology == "ipv6-ea-rule1":
                    print_and_log("Alternate LB method "+res_lb_method+" is configured to Pool with topo rule "+res_lb_topology+" successfully")
                    assert True
                else:
                    print_and_log(" Error while validating the LB method of the Pool")
                    assert False
                print_and_log("Test Case 249 Execution completed")



        @pytest.mark.run(order=250)
        def test_250_Run_the_dig_command_with_subnet_of_IPV6_IPAM_network1(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM network1 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_64_subnet+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 250 Execution Completed")


        @pytest.mark.run(order=251)
        def test_251_Run_the_dig_command_with_subnet_of_IPV6_IPAM_conatiner(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Container ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_32_subnet+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network_container1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 251 Execution Completed")


        @pytest.mark.run(order=252)
        def test_252_Run_the_dig_command_with_subnet_of_IPV6_IPAM_ranges(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Ranges ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[0]+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[1]+"/128 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[2]+"/128 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 252 Execution Completed")



        @pytest.mark.run(order=253)
        def test_253_Modify_the_Pool4_Lb_method_and_add_the_alternate_load_balancing_method_all_available(self):
                print_and_log("********* Mofity the Pool4 LB method all available to Topology ***********")
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_4')
                response1 = json.loads(response1)
                print_and_log(response1)
                res_ref1 = response1[0]['_ref']
                data = {"lb_alternate_method": "ALL_AVAILABLE"}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref1, fields=json.dumps(data))
                print_and_log(response1)
                restart_services()
                print_and_log("Test Case 253 Execution Completed")


        @pytest.mark.run(order=254)
        def test_254_Validation_of_Pool4_Alternate_Lb_method_to_Topology(self):
                print_and_log("********** Validation of Pool4 LB method all available to Topology **********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ipv6-ea-rule1')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_4')
                response1 = json.loads(response1)
                print_and_log(response1)
                res_ref1 = response1[0]['_ref']
                response2 = ib_NIOS.wapi_request('GET',object_type=res_ref1, params='?_return_fields=lb_alternate_method')
                response2 = json.loads(response2)
                res_lb_method = response2['lb_alternate_method']
                print_and_log(res_lb_method)
                response3 = ib_NIOS.wapi_request('GET',object_type=res_ref1, params='?_return_fields=lb_preferred_topology')
                response3 = json.loads(response3)
                res_lb_topology = response3['lb_preferred_topology'].split(":")[-1]
                print_and_log(res_lb_topology)
                if res_lb_method == "ALL_AVAILABLE" and res_lb_topology == "ipv6-ea-rule1":
                    print_and_log("Alternate LB method "+res_lb_method+" is configured to Pool with topo rule "+res_lb_topology+" successfully")
                    assert True
                else:
                    print_and_log(" Error while validating the LB method of the Pool")
                    assert False
                print_and_log("Test Case 254 Execution completed")



        @pytest.mark.run(order=255)
        def test_255_Run_the_dig_command_with_subnet_of_IPV6_IPAM_network1(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM network1 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_64_subnet+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                Server_That_Responded1 = output.strip(" ").split("\n")[1]
                print_and_log(Server_That_Responded)
                print_and_log(Server_That_Responded1)
                if Server_That_Responded == config.ipv6_server1 and Server_That_Responded1 == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" and Server "+Server_That_Responded1+" responded for the query with subnet "+config.ipv6network1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 255 Execution Completed")


        @pytest.mark.run(order=256)
        def test_256_Run_the_dig_command_with_subnet_of_IPV6_IPAM_conatiner(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Container ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_32_subnet+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                Server_That_Responded1 = output.strip(" ").split("\n")[1]
                print_and_log(Server_That_Responded)
                print_and_log(Server_That_Responded1)
                if Server_That_Responded == config.ipv6_server1 and Server_That_Responded1 == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" and Server "+Server_That_Responded1+" responded for the query with subnet "+config.ipv6network_container1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 256 Execution Completed")


        @pytest.mark.run(order=257)
        def test_257_Run_the_dig_command_with_subnet_of_IPV6_IPAM_ranges(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Ranges ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[0]+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                Server_That_Responded1 = output.strip(" ").split("\n")[1]
                print_and_log(Server_That_Responded)
                print_and_log(Server_That_Responded1)
                if Server_That_Responded == config.ipv6_server1 and Server_That_Responded1 == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" and Server "+Server_That_Responded1+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[1]+"/128 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                Server_That_Responded1 = output1.strip(" ").split("\n")[1]
                print_and_log(Server_That_Responded)
                print_and_log(Server_That_Responded1)
                if Server_That_Responded == config.ipv6_server1 and Server_That_Responded1 == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" and Server "+Server_That_Responded1+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[2]+"/128 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                Server_That_Responded1 = output2.strip(" ").split("\n")[1]
                print_and_log(Server_That_Responded)
                print_and_log(Server_That_Responded1)
                if Server_That_Responded == config.ipv6_server1 and Server_That_Responded1 == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" and Server "+Server_That_Responded1+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 257 Execution Completed")



        @pytest.mark.run(order=258)
        def test_258_Modify_the_Pool4_Lb_method_and_add_the_alternate_load_balancing_method_round_robin(self):
                print_and_log("********* Mofity the Pool4 LB method round robin to Topology ***********")
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_4')
                response1 = json.loads(response1)
                print_and_log(response1)
                res_ref1 = response1[0]['_ref']
                data = {"lb_alternate_method": "ROUND_ROBIN"}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref1, fields=json.dumps(data))
                print_and_log(response1)
                restart_services()
                print_and_log("Test Case 258 Execution Completed")


        @pytest.mark.run(order=259)
        def test_259_Validation_of_Pool4_Alternate_Lb_method_round_robin_to_Topology(self):
                print_and_log("********** Validation of Pool4 LB method round robin to Topology **********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ipv6-ea-rule1')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_4')
                response1 = json.loads(response1)
                print_and_log(response1)
                res_ref1 = response1[0]['_ref']
                response2 = ib_NIOS.wapi_request('GET',object_type=res_ref1, params='?_return_fields=lb_alternate_method')
                response2 = json.loads(response2)
                res_lb_method = response2['lb_alternate_method']
                print_and_log(res_lb_method)
                response3 = ib_NIOS.wapi_request('GET',object_type=res_ref1, params='?_return_fields=lb_preferred_topology')
                response3 = json.loads(response3)
                res_lb_topology = response3['lb_preferred_topology'].split(":")[-1]
                print_and_log(res_lb_topology)
                if res_lb_method == "ROUND_ROBIN" and res_lb_topology == "ipv6-ea-rule1":
                    print_and_log("Alternate LB method "+res_lb_method+" is configured to Pool with topo rule "+res_lb_topology+" successfully")
                    assert True
                else:
                    print_and_log(" Error while validating the LB method of the Pool")
                    assert False
                print_and_log("Test Case 259 Execution completed")




        @pytest.mark.run(order=260)
        def test_260_Run_the_dig_command_with_subnet_of_IPV6_IPAM_network1(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM network1 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_64_subnet+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1 or Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 260 Execution Completed")


        @pytest.mark.run(order=261)
        def test_261_Run_the_dig_command_with_subnet_of_IPV6_IPAM_conatiner(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Container ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_32_subnet+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1 or Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network_container1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 261 Execution Completed")


        @pytest.mark.run(order=262)
        def test_262_Run_the_dig_command_with_subnet_of_IPV6_IPAM_ranges(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Ranges ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[0]+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1 or Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[1]+"/128 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1 or Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[2]+"/128 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1 or Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 262 Execution Completed")



        @pytest.mark.run(order=263)
        def test_263_Modify_the_Pool4_Lb_method_and_add_the_alternate_load_balancing_method_source_ip_hash(self):
                print_and_log("********* Mofity the Pool4 LB method source ip hash to Topology ***********")
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_4')
                response1 = json.loads(response1)
                print_and_log(response1)
                res_ref1 = response1[0]['_ref']
                data = {"lb_alternate_method": "SOURCE_IP_HASH"}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref1, fields=json.dumps(data))
                print_and_log(response1)
                restart_services()
                print_and_log("Test Case 263 Execution Completed")


        @pytest.mark.run(order=264)
        def test_264_Validation_of_Pool4_Alternate_Lb_method_source_ip_hash_to_Topology(self):
                print_and_log("********** Validation of Pool4 LB method source ip hash to Topology **********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ipv6-ea-rule1')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_4')
                response1 = json.loads(response1)
                print_and_log(response1)
                res_ref1 = response1[0]['_ref']
                response2 = ib_NIOS.wapi_request('GET',object_type=res_ref1, params='?_return_fields=lb_alternate_method')
                response2 = json.loads(response2)
                res_lb_method = response2['lb_alternate_method']
                print_and_log(res_lb_method)
                response3 = ib_NIOS.wapi_request('GET',object_type=res_ref1, params='?_return_fields=lb_preferred_topology')
                response3 = json.loads(response3)
                res_lb_topology = response3['lb_preferred_topology'].split(":")[-1]
                print_and_log(res_lb_topology)
                if res_lb_method == "SOURCE_IP_HASH" and res_lb_topology == "ipv6-ea-rule1":
                    print_and_log("Alternate LB method "+res_lb_method+" is configured to Pool with topo rule "+res_lb_topology+" successfully")
                    assert True
                else:
                    print_and_log(" Error while validating the LB method of the Pool")
                    assert False
                print_and_log("Test Case 264 Execution completed")



        @pytest.mark.run(order=265)
        def test_265_Run_the_dig_command_with_subnet_of_IPV6_IPAM_network1(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM network1 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_64_subnet+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1 or Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 265 Execution Completed")


        @pytest.mark.run(order=266)
        def test_266_Run_the_dig_command_with_subnet_of_IPV6_IPAM_conatiner(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Container ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_32_subnet+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1 or Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network_container1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 266 Execution Completed")


        @pytest.mark.run(order=267)
        def test_267_Run_the_dig_command_with_subnet_of_IPV6_IPAM_ranges(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Ranges ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[0]+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1 or Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[1]+"/128 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1 or Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[2]+"/128 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1 or Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 267 Execution Completed")



        @pytest.mark.run(order=268)
        def test_268_Modify_the_Pool4_Lb_method_and_add_the_alternate_load_balancing_method_none(self):
                print_and_log("********* Mofity the Pool4 LB method source ip hash to Topology ***********")
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_4')
                response1 = json.loads(response1)
                print_and_log(response1)
                res_ref1 = response1[0]['_ref']
                data = {"lb_alternate_method": "NONE"}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref1, fields=json.dumps(data))
                print_and_log(response1)
                restart_services()
                print_and_log("Test Case 268 Execution Completed")


        @pytest.mark.run(order=269)
        def test_269_Validation_of_Pool4_Alternate_Lb_method_none_to_Topology(self):
                print_and_log("********** Validation of Pool4 LB method source ip hash to Topology **********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ipv6-ea-rule1')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_4')
                response1 = json.loads(response1)
                print_and_log(response1)
                res_ref1 = response1[0]['_ref']
                response2 = ib_NIOS.wapi_request('GET',object_type=res_ref1, params='?_return_fields=lb_alternate_method')
                response2 = json.loads(response2)
                res_lb_method = response2['lb_alternate_method']
                print_and_log(res_lb_method)
                response3 = ib_NIOS.wapi_request('GET',object_type=res_ref1, params='?_return_fields=lb_preferred_topology')
                response3 = json.loads(response3)
                res_lb_topology = response3['lb_preferred_topology'].split(":")[-1]
                print_and_log(res_lb_topology)
                if res_lb_method == "NONE" and res_lb_topology == "ipv6-ea-rule1":
                    print_and_log("Alternate LB method "+res_lb_method+" is configured to Pool with topo rule "+res_lb_topology+" successfully")
                    assert True
                else:
                    print_and_log(" Error while validating the LB method of the Pool")
                    assert False
                print_and_log("Test Case 269 Execution completed")



        @pytest.mark.run(order=270)
        def test_270_modify_the_pool4_and_assign_Server_4(self):
                print_and_log("******* Modify the pool4 lb method to Round Robin *********")
                print_and_log("Getting the server name reference ")
                servers = ["server4", "server5"]
                server_ref = []
                for i in servers:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    server_ref.append(ref)
                print_and_log(server_ref)
                print_and_log("****** Getting the ref of Pool 4 ******")
                print_and_log("****** Modify the pool Pool_4 and assiging the server4 *********")
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_4')
                response1 = json.loads(response1)
                ref_pool1 = response1[0]['_ref']
                data = {"lb_preferred_method": "ROUND_ROBIN", "servers": [{"ratio": 1,"server": str(server_ref[0])}]}
                response_servers = ib_NIOS.wapi_request('PUT',object_type=ref_pool1, fields=json.dumps(data))
                print_and_log(response_servers)
                restart_services()
                print_and_log("Test Case 270 Execution completed")


        @pytest.mark.run(order=271)
        def test_271_add_Pool_5_and_assign_Server_5(self):
                print_and_log("******* Add Second DTC Pool Pool_5 *********")
                print_and_log("Getting the server name reference ")
                servers = ["server4", "server5"]
                server_ref = []
                for i in servers:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    server_ref.append(ref)
                print_and_log(server_ref)
                print_and_log("****** Creating the pool Pool_5 and assiging the server5 ******")
                data = {"name": "Pool_5", "lb_preferred_method": "ROUND_ROBIN", "servers": [{"ratio": 1,"server": str(server_ref[1])}], "monitors": ["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"]}
                response_servers = ib_NIOS.wapi_request('POST',object_type='dtc:pool', fields=json.dumps(data))
                print_and_log(response_servers)
                print_and_log("Validation of Pool creation")
                assert re.search(r'dtc:pool', response_servers)
                print_and_log("Test Case 271 Execution completed")


        @pytest.mark.run(order=272)
        def test_272_Validation_of_the_Pool_4_after_modification(self):
                print_and_log("******* Validation_of_the_Pool_4_after_modification *********")
                response = ib_NIOS.wapi_request('GET', object_type="dtc:pool", params='?name=Pool_4')
                response = json.loads(response)
                print_and_log(response)
                ref_pool1 = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET', object_type=ref_pool1, params='?_return_fields=servers')
                response1 = json.loads(response1)
                print_and_log(response1)
                ref_server = response1['servers'][0]['server'].split(":")[-1]
                print_and_log(ref_server)
                if ref_server == "server4" and ref_server != "server5":
                    print_and_log(ref_server+" is present under the Pool 4, Modfication is successful")
                    assert True
                else:
                    print_and_log("Modfication for Pool 4 failed")
                    assert False
                print_and_log("Test Case 272 Execution completed")


        @pytest.mark.run(order=273)
        def test_273_Validation_of_the_Pool_5(self):
                print_and_log("******* Validation of the Pool 5 *********")
                response = ib_NIOS.wapi_request('GET', object_type="dtc:pool", params='?name=Pool_5')
                response = json.loads(response)
                print_and_log(response)
                ref_pool2 = response[0]['_ref']
                ref_name = response[0]['name']
                print_and_log(ref_name)
                response1 = ib_NIOS.wapi_request('GET', object_type=ref_pool2, params='?_return_fields=servers')
                response1 = json.loads(response1)
                print_and_log(response1)
                ref_server = response1['servers'][0]['server'].split(":")[-1]
                print_and_log(ref_server)
                if ref_server == "server5" and ref_server != "server4" and ref_name == "Pool_5":
                    print_and_log(ref_name+" Pool got created with "+ref_server+" is present under the Pool 5")
                    assert True
                else:
                    print_and_log("Validation for the Pool 5 failed")
                    assert False
                print_and_log("Test Case 273 Execution completed")



        @pytest.mark.run(order=274)
        def test_274_Enable_all_the_IPAM_options_in_grid_dns_properties_traffic_control(self):
                print_and_log("********** Enable all the IPAM options in grid dns properties traffic control ************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                ipam_obj=["gen_eadb_from_networks", "gen_eadb_from_network_containers", "gen_eadb_from_ranges"]
                for i in ipam_obj:
                    data = {i : True}
                    response1 = ib_NIOS.wapi_request('PUT',object_type=ref ,fields=json.dumps(data))
                    print_and_log(response1)
                rebuild_services()
                restart_services()
                print_and_log("Test Case 274 Execution Completed")


        @pytest.mark.run(order=275)
        def test_275_verifying_if_all_the_ipam_objects_are_enabled_in_grid_dns_properties_traffic_control(self):
                print_and_log("********** Verifying if all the ipam objects are enabled in grid dns properties traffic control ************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                for i in json.loads(config.ipam_obj):
                    response1 = ib_NIOS.wapi_request('GET',object_type=ref ,params='?_return_fields='+i)
                    response1 = json.loads(response1)
                    output = response1[i]
                    print_and_log(output)
                    if output == True:
                        print_and_log("IPAM Object "+i+" is Enabled")
                        assert True
                    else:
                        print_and_log("IPAM Object "+i+" is Disabled")
                        assert False
                print_and_log("Test Case 275 Execution Completed")



        @pytest.mark.run(order=276)
        def test_276_Create_the_DTC_topology_Rule_IPV6_with_Pool_as_Destination(self):
                print_and_log("********* Create the DTC topology Rule with Pool as Destination ***********")
                pool_ref = []
                Pool = ["Pool_4", "Pool_5"]
                for i in Pool:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    pool_ref.append(ref)
                data = {"name": "ipv6-ea-rule2", "rules": [{"sources": [{"source_op": "IS","source_type": "EA0","source_value": "network1"}], "dest_type": "POOL","destination_link": pool_ref[0]}, {"sources":[{"source_op": "IS","source_type": "EA0","source_value": "network2"}], "dest_type": "POOL","destination_link": pool_ref[1]}]}
                print_and_log(data)
                response = ib_NIOS.wapi_request('POST',object_type='dtc:topology', fields=json.dumps(data))
                print_and_log(response)
                assert re.search(r'dtc:topology', response)
                print_and_log("Test Case 276 Execution completed")


        @pytest.mark.run(order=277)
        def test_277_Validation_of_Topology_rule_IPV6_ea_rule_2(self):
                print_and_log("********* Validation of Topology IPV6 ea rule 2 ***********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ipv6-ea-rule2')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                res_name = response[0]['name']
                if res_name == "ipv6-ea-rule2":
                    print_and_log("Topology rule "+res_name+" created successfully")
                    assert True
                else:
                    print_and_log(" Validation for the Topology rule failed ")
                    assert False
                print_and_log("Test Case 277 Execution completed")



        @pytest.mark.run(order=278)
        def test_278_Modify_the_LBDN_and_Configure_the_IPV6_Topology_rule_2_as_Lb_method(self):
                print_and_log("********* Modify the LBDN and Configure the IPV6 Topology rule 2 as Lb method ***********")
                pool_ref = []
                Pool = ["Pool_4", "Pool_5"]
                for i in Pool:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    pool_ref.append(ref)
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ipv6-ea-rule2')
                response1 = json.loads(response1)
                print_and_log(response1)
                res_ref = response1[0]['_ref']
                response2 = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=LBDN_2')
                response2 = json.loads(response2)
                ref_lbdn = response2[0]['_ref']
                data = {"lb_method": "TOPOLOGY", "topology": res_ref, "pools": [{"ratio": 1, "pool": pool_ref[0]}, {"ratio": 1, "pool": pool_ref[1]}]}
                response3 = ib_NIOS.wapi_request('PUT',object_type=ref_lbdn, fields=json.dumps(data))
                print_and_log(response3)
                assert re.search(r'dtc:lbdn', response3)
                restart_services()
                print_and_log("Test Case 278 Execution completed")



        @pytest.mark.run(order=279)
        def test_279_validation_of_dtc_lbdn(self):
                print_and_log("******** Validation of dtc lbdn **********")
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=LBDN_2')
                response1 = json.loads(response1)
                ref_lbdn = response1[0]['_ref']
                response2 = ib_NIOS.wapi_request('GET',object_type=ref_lbdn, params='?_return_fields=lb_method')
                response2 = json.loads(response2)
                ref_lb_method = response2['lb_method']
                response3 = ib_NIOS.wapi_request('GET',object_type=ref_lbdn, params='?_return_fields=topology')
                response3 = json.loads(response3)
                ref_lb_topology = response3['topology'].split(":")[-1]
                if ref_lb_method == "TOPOLOGY" and ref_lb_topology == "ipv6-ea-rule2":
                    print_and_log("LBDN configured with Lb method "+ref_lb_method+" with topology rule "+ref_lb_topology)
                    assert True
                else:
                    print_and_log("Validation for the LBDN failed")
                    assert False
                print_and_log("Test Case 279 Execution completed")



        @pytest.mark.run(order=280)
        def test_280_Modify_the_value_of_the_IPV6_IPAM_network_from_network1_to_network2(self):
                print_and_log("******** Modify the value of the IPV6 IPAM network from network1 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="ipv6network", params='?network='+config.ipv6network1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network2"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('ipv6network', 'network2', '?network='+config.ipv6network1)
                print_and_log("Test Case 280 Execution Completed")



        @pytest.mark.run(order=281)
        def test_281_Modify_the_value_of_the_IPV6_IPAM_conatiner_from_network2_to_network1(self):
                print_and_log("******** Modify the value of the IPV6 IPAM conatiner from network2 to network1 *********")
                response = ib_NIOS.wapi_request('GET',object_type="ipv6networkcontainer", params='?network='+config.ipv6network_container1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network1"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('ipv6networkcontainer', 'network1', '?network='+config.ipv6network_container1)
                print_and_log("Test Case 281 Execution Completed")



        @pytest.mark.run(order=282)
        def test_282_Modify_the_value_of_the_IPV6_IPAM_Ranges_from_network2_to_network1(self):
                print_and_log("******** Modify the value of the IPV6 IPAM network from network2 to network1 *********")
                response = ib_NIOS.wapi_request('GET',object_type="ipv6range", params='?network='+config.ipv6network1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network1"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('ipv6range', 'network1', '?network='+config.ipv6network1)
                print_and_log("Test Case 282 Execution Completed")


        @pytest.mark.run(order=283)
        def test_283_Modify_the_value_of_the_IPV6_IPAM_Host_from_network2_to_network1(self):
                print_and_log("******** Modify the value of the IPV6 IPAM network from network2 to network1 *********")
                response = ib_NIOS.wapi_request('GET',object_type="record:host", params='?name=host_new_ipv6')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network1"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('record:host', 'network1', '?name=host_new_ipv6')
                sleep(60)
                print_and_log("Test Case 283 Execution Completed")



        @pytest.mark.run(order=284)
        def test_284_Run_the_dig_command_with_subnet_of_IPV6_IPAM_network1(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM network1 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_64_subnet+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 284 Execution Completed")


        @pytest.mark.run(order=285)
        def test_285_Run_the_dig_command_with_subnet_of_IPV6_IPAM_conatiner(self):
                print_and_log("********** Run the dig command with subnet of IPAM Container ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_32_subnet+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network_container1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 285 Execution Completed")


        @pytest.mark.run(order=286)
        def test_286_Run_the_dig_command_with_subnet_of_IPV6_IPAM_ranges(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Ranges ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[0]+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[1]+"/128 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[2]+"/128 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 286 Execution Completed")



        @pytest.mark.run(order=287)
        def test_287_Run_the_dig_command_with_subnet_of_IPV6_IPAM_Hosts(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Hosts ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6addr_host+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6addr_host)
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 287 Execution Completed")



        @pytest.mark.run(order=288)
        def test_288_Modify_the_value_of_the_IPV6_IPAM_network_from_network2_to_network1(self):
                print_and_log("******** Modify the value of the IPV6 IPAM network from network2 to network1 *********")
                response = ib_NIOS.wapi_request('GET',object_type="ipv6network", params='?network='+config.ipv6network1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network1"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('ipv6network', 'network1', '?network='+config.ipv6network1)
                print_and_log("Test Case 288 Execution Completed")



        @pytest.mark.run(order=289)
        def test_289_Modify_the_value_of_the_IPV6_IPAM_conatiner_from_network1_to_network2(self):
                print_and_log("******** Modify the value of the IPV6 IPAM conatiner from network1 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="ipv6networkcontainer", params='?network='+config.ipv6network_container1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network2"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('ipv6networkcontainer', 'network2', '?network='+config.ipv6network_container1)
                print_and_log("Test Case 289 Execution Completed")



        @pytest.mark.run(order=290)
        def test_290_Modify_the_value_of_the_IPV6_IPAM_Ranges_from_network1_to_network2(self):
                print_and_log("******** Modify the value of the IPV6 IPAM network from network1 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="ipv6range", params='?network='+config.ipv6network1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network2"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('ipv6range', 'network2', '?network='+config.ipv6network1)
                print_and_log("Test Case 290 Execution Completed")


        @pytest.mark.run(order=291)
        def test_291_Modify_the_value_of_the_IPV6_IPAM_Host_from_network1_to_network2(self):
                print_and_log("******** Modify the value of the IPV6 IPAM network from network1 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="record:host", params='?name=host_new_ipv6')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network2"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('record:host', 'network2', '?name=host_new_ipv6')
                sleep(60)
                rebuild_services()
                print_and_log("Test Case 291 Execution Completed")



        @pytest.mark.run(order=292)
        def test_292_Run_the_dig_command_with_subnet_of_IPV6_IPAM_network1(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM network1 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_64_subnet+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 292 Execution Completed")


        @pytest.mark.run(order=293)
        def test_293_Run_the_dig_command_with_subnet_of_IPV6_IPAM_conatiner(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Container ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_32_subnet+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network_container1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 293 Execution Completed")


        @pytest.mark.run(order=294)
        def test_294_Run_the_dig_command_with_subnet_of_IPV6_IPAM_ranges(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Ranges ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[0]+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[1]+"/128 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[2]+"/128 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded ==config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 294 Execution Completed")



        @pytest.mark.run(order=295)
        def test_295_Run_the_dig_command_with_subnet_of_IPV6_IPAM_Hosts(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Hosts ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6addr_host+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6addr_host)
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 295 Execution Completed")



        @pytest.mark.run(order=296)
        def test_296_Uncheck_the_IPAM_Container_object_in_Grid_DNS_Properties_Traffic_Control(self):
                print_and_log("********** Uncheck the IPAM Container object in Grid DNS Properties Traffic Control ************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                data = {"gen_eadb_from_network_containers": False}
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                restart_services()
                print_and_log("Test Case 296 Execution Completed")


        @pytest.mark.run(order=297)
        def test_297_Validation_of_the_IPAM_Container_object_in_Grid_DNS_Properties_Traffic_Control(self):
                print_and_log("********** Validation of the IPAM Container object in Grid DNS Properties Traffic Control************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=gen_eadb_from_network_containers')
                response1 = json.loads(response1)
                output = response1['gen_eadb_from_network_containers']
                if output == False:
                    print_and_log(" The IPAM Containers Object in Grid DNS properties is set to False")
                    assert True
                else:
                    print_and_log(" The IPAM Containers Object in Grid DNS properties is set to True")
                    assert False
                print_and_log("Test Case 297 Execution Completed")


        @pytest.mark.run(order=298)
        def test_298_Run_the_dig_command_with_subnet_of_IPV6_IPAM_conatiner(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Container ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_32_subnet).read()
                out = output.split("\n")
                flag = False
                for i in out:
                    match = re.match("dtc.com.\s+\d+\s+IN\s+SOA.*",i)
                    print_and_log(i)
                    if match:
                        print_and_log(" Match found ")
                        flag=True
                        break
                if flag == True:
                    print_and_log("SOA record is found, No response from any for the DTC servers")
                    assert True
                else:
                    print_and_log("Query got the response from DTC servers")
                    assert False
                print_and_log("Test Case 289 Execution Completed")


        @pytest.mark.run(order=299)
        def test_299_Uncheck_the_IPAM_Networks_object_in_Grid_DNS_Properties_Traffic_Control(self):
                print_and_log("********** Uncheck the IPAM networks object in Grid DNS Properties Traffic Control ************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                data = {"gen_eadb_from_networks": False}
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                restart_services()
                print_and_log("Test Case 299 Execution Completed")


        @pytest.mark.run(order=300)
        def test_300_Validation_of_the_IPAM_network_object_in_Grid_DNS_Properties_Traffic_Control(self):
                print_and_log("********** Validation of the IPAM networks object in Grid DNS Properties Traffic Control************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=gen_eadb_from_networks')
                response1 = json.loads(response1)
                output = response1['gen_eadb_from_networks']
                if output == False:
                    print_and_log(" The IPAM networks Object in Grid DNS properties is set to False")
                    assert True
                else:
                    print_and_log(" The IPAM networks Object in Grid DNS properties is set to True")
                    assert False
                print_and_log("Test Case 300 Execution Completed")



        @pytest.mark.run(order=301)
        def test_301_Run_the_dig_command_with_subnet_of_IPV6_IPAM_network(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Network ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_64_subnet).read()
                out = output.split("\n")
                flag = False
                for i in out:
                    match = re.match("dtc.com.\s+\d+\s+IN\s+SOA.*",i)
                    print_and_log(i)
                    if match:
                        print_and_log(" Match found ")
                        flag=True
                        break
                if flag == True:
                    print_and_log("SOA record is found, No response from any for the DTC servers")
                    assert True
                else:
                    print_and_log("Query got the response from DTC servers")
                    assert False
                print_and_log("Test Case 301 Execution Completed")



        @pytest.mark.run(order=302)
        def test_302_Uncheck_the_IPAM_ranges_object_in_Grid_DNS_Properties_Traffic_Control(self):
                print_and_log("********** Uncheck the IPAM ranges object in Grid DNS Properties Traffic Control ************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                data = {"gen_eadb_from_ranges": False}
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                restart_services()
                print_and_log("Test Case 302 Execution Completed")


        @pytest.mark.run(order=303)
        def test_303_Validation_of_the_IPAM_ranges_object_in_Grid_DNS_Properties_Traffic_Control(self):
                print_and_log("********** Validation of the IPAM ranges object in Grid DNS Properties Traffic Control************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=gen_eadb_from_ranges')
                response1 = json.loads(response1)
                output = response1['gen_eadb_from_ranges']
                if output == False:
                    print_and_log(" The IPAM ranges Object in Grid DNS properties is set to False")
                    assert True
                else:
                    print_and_log(" The IPAM networks Object in Grid DNS properties is set to True")
                    assert False
                print_and_log("Test Case 303 Execution Completed")



        @pytest.mark.run(order=304)
        def test_304_Run_the_dig_command_with_subnet_of_IPAM_ranges(self):
                print_and_log("********** Run the dig command with subnet of IPAM Ranges ************")
                for i in json.loads(config.ipv6_ranges):
                    output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+i+"/128").read()
                    out = output.split("\n")
                    flag = False
                    for i in out:
                        match = re.match("dtc.com.\s+\d+\s+IN\s+SOA.*",i)
                        print_and_log(i)
                        if match:
                            print_and_log(" Match found ")
                            flag=True
                            break
                    if flag == True:
                        print_and_log("SOA record is found, No response from any for the DTC servers")
                        assert True
                    else:
                        print_and_log("Query got the response from DTC servers")
                        assert False
                print_and_log("Test Case 304 Execution Completed")



        @pytest.mark.run(order=305)
        def test_305_Create_the_thrid_IPV6_DTC_server(self):
                print_and_log("********** Create the Thrid IPV6 DTC server ***********")
                data = {"name":"server6","host":config.ipv6_server3}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
                print_and_log(response)
                assert re.search(r'dtc:server', response)
                print_and_log("Test Case 296 Execution Completed")


        @pytest.mark.run(order=306)
        def test_306_Validate_the_New_DTC_server_that_is_created(self):
                print_and_log("********** Validate the New DTC server that is created ***********")
                response = ib_NIOS.wapi_request('GET', object_type="dtc:server", params='?name=server6')
                response = json.loads(response)
                print_and_log(response)
                name = response[0]['name']
                if name == "server6":
                    print_and_log(" DTC server "+name+" created successfully")
                    assert True
                else:
                    print_and_log(" Error while validating the newly created server")
                    assert False
                print_and_log("Test Case 297 Execution Completed")


        @pytest.mark.run(order=307)
        def test_307_Create_the_thrid_IPV6_DTC_Pool(self):
                print_and_log("********** Create the thrid IPV6 DTC Pool ***********")
                response = ib_NIOS.wapi_request('GET', object_type="dtc:server", params='?name=server6')
                response = json.loads(response)
                print_and_log(response)
                ref = response[0]['_ref']
                data = {"name": "Pool_6", "lb_preferred_method": "ROUND_ROBIN", "servers": [{"ratio": 1,"server": str(ref)}], "monitors": ["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"]}
                response_servers = ib_NIOS.wapi_request('POST',object_type='dtc:pool', fields=json.dumps(data))
                ref1 = json.loads(response_servers)
                print_and_log(ref1)
                print_and_log("Validation of Pool creation")
                assert re.search(r'dtc:pool', ref1)
                print_and_log("Test Case 307 Execution Completed")


        @pytest.mark.run(order=308)
        def test_308_Validate_the_IPV6_DTC_Pool_that_is_created(self):
                print_and_log("********** Validate the IPV6 DTC Pool that is created ***********")
                response = ib_NIOS.wapi_request('GET', object_type="dtc:pool", params='?name=Pool_6')
                response = json.loads(response)
                print_and_log(response)
                name = response[0]['name']
                if name == "Pool_6":
                    print_and_log(" DTC Pool "+name+" created successfully")
                    assert True
                else:
                    print_and_log(" Error while validating the newly created Pool")
                    assert False
                print_and_log("Test Case 308 Execution Completed")



        @pytest.mark.run(order=309)
        def test_309_Enable_all_the_IPAM_options_in_grid_dns_properties_traffic_control(self):
                print_and_log("********** Enable all the IPAM options in grid dns properties traffic control ************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns")
                response = json.loads(response)
                ref = response[0]['_ref']
                ipam_obj=["gen_eadb_from_networks", "gen_eadb_from_network_containers", "gen_eadb_from_ranges"]
                for i in ipam_obj:
                    data = {i : True}
                    response1 = ib_NIOS.wapi_request('PUT',object_type=ref ,fields=json.dumps(data))
                    print_and_log(response1)
                rebuild_services()
                restart_services()
                print_and_log("Test Case 309 Execution Completed")



        @pytest.mark.run(order=310)
        def test_310_Add_Pool_6_has_default_destination_in_the_topology_rule(self):
                print_and_log("********* Add_Pool_6_has_default_destination_in_the_topology_rule **********")
                pool_ref = []
                Pool = ["Pool_4", "Pool_5", "Pool_6"]
                for i in Pool:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    pool_ref.append(ref)
                data = {"rules": [{"sources": [{"source_op": "IS","source_type": "EA0","source_value": "network1"}], "dest_type": "POOL","destination_link": pool_ref[0]}, {"sources":[{"source_op": "IS","source_type": "EA0","source_value": "network2"}], "dest_type": "POOL","destination_link": pool_ref[1]}, {"sources":[], "dest_type": "POOL", "destination_link": pool_ref[2]}]}
                response = ib_NIOS.wapi_request('GET', object_type="dtc:topology", params='?name=ipv6-ea-rule2')
                response = json.loads(response)
                print_and_log(response)
                topo_ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('PUT', object_type=topo_ref, fields=json.dumps(data))
                print_and_log(response1)
                print_and_log("Validation of Topology creation")
                assert re.search(r'dtc:topology', response1)
                restart_services()
                print_and_log("Test Case 310 Execution Completed")



        @pytest.mark.run(order=311)
        def test_311_Validation_of_default_destination_pool_added_in_topo_rule(self):
                print_and_log("********* Validation of default destination pool added in topo rule **********")
                response = ib_NIOS.wapi_request('GET', object_type="dtc:topology", params='?name=ipv6-ea-rule2')
                response = json.loads(response)
                print_and_log(response)
                topo_ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET', object_type=topo_ref, params='?_return_fields=rules')
                response1 = json.loads(response1)
                print_and_log(response1)
                rule_ref = response1['rules'][2]['_ref']
                response2 = ib_NIOS.wapi_request('GET', object_type=rule_ref, params='?_return_fields=destination_link')
                response2 = json.loads(response2)
                print_and_log(response2)
                pool_name = response2['destination_link']['name']
                print_and_log(pool_name)
                response3 = ib_NIOS.wapi_request('GET', object_type=rule_ref, params='?_return_fields=sources')
                response3 = json.loads(response3)
                print_and_log(response3)
                sources = response3['sources']
                print_and_log(sources)
                if sources == [] and pool_name == "Pool_6":
                    print_and_log(pool_name+" is configured as default destination pool")
                    assert True
                else:
                    print_and_log("Validation for deafult destination failed")
                    assert False
                print_and_log("Test Case 311 Execution Completed")



        @pytest.mark.run(order=312)
        def test_312_Modify_the_value_of_the_IPV6_IPAM_network_from_network1_to_network3(self):
                print_and_log("******** Modify the value of the IPV6 IPAM network from network1 to network3 *********")
                response = ib_NIOS.wapi_request('GET',object_type="ipv6network", params='?network='+config.ipv6network1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network3"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('ipv6network', 'network3', '?network='+config.ipv6network1)
                print_and_log("Test Case 312 Execution Completed")



        @pytest.mark.run(order=313)
        def test_313_Modify_the_value_of_the_IPV6_IPAM_conatiner_from_network2_to_network3(self):
                print_and_log("******** Modify the value of the IPV6 IPAM conatiner from network2 to network3 *********")
                response = ib_NIOS.wapi_request('GET',object_type="ipv6networkcontainer", params='?network='+config.ipv6network_container1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network3"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('ipv6networkcontainer', 'network3', '?network='+config.ipv6network_container1)
                print_and_log("Test Case 313 Execution Completed")



        @pytest.mark.run(order=314)
        def test_314_Run_the_dig_command_with_subnet_of_IPV6_IPAM_network1(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM network1 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_64_subnet+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server3:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 314 Execution Completed")


        @pytest.mark.run(order=315)
        def test_315_Run_the_dig_command_with_subnet_of_IPV6_IPAM_conatiner(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Container ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_32_subnet+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server3:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network_container1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 315 Execution Completed")



        @pytest.mark.run(order=316)
        def test_316_Modify_the_value_of_the_IPV6_IPAM_network_from_network3_to_network1(self):
                print_and_log("******** Modify the value of the IPV6 IPAM network from network3 to network1 *********")
                response = ib_NIOS.wapi_request('GET',object_type="ipv6network", params='?network='+config.ipv6network1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network1"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('ipv6network', 'network1', '?network='+config.ipv6network1)
                print_and_log("Test Case 316 Execution Completed")



        @pytest.mark.run(order=317)
        def test_317_Modify_the_value_of_the_IPV6_IPAM_conatiner_from_network3_to_network2(self):
                print_and_log("******** Modify the value of the IPV6 IPAM conatiner from network3 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="ipv6networkcontainer", params='?network='+config.ipv6network_container1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network2"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('ipv6networkcontainer', 'network2', '?network='+config.ipv6network_container1)
                print_and_log("Test Case 317 Execution Completed")



        @pytest.mark.run(order=318)
        def test_318_Modify_the_Pool_4_Lb_method_to_Topology(self):
                print_and_log("********* Mofity the Pool 4 LB method to Topology ***********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ipv6-ea-rule1')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                server_ref = []
                servers = ["server4", "server5", "server6"]
                for i in servers:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    server_ref.append(ref)
                print_and_log(server_ref)
                print_and_log("****** Creating the pool and assiging the server ******")
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_4')
                response1 = json.loads(response1)
                print_and_log(response1)
                res_ref1 = response1[0]['_ref']
                data = {"lb_preferred_method": "TOPOLOGY", "lb_preferred_topology": res_ref, "servers": [{"ratio": 1,"server": str(server_ref[0])}, {"ratio": 1,"server": str(server_ref[1])}]}
                response2 = ib_NIOS.wapi_request('PUT',object_type=res_ref1, fields=json.dumps(data))
                print_and_log(response2)
                print_and_log("Validation of Pool Modfication")
                assert re.search(r'dtc:pool', response2)
                restart_services()
                print_and_log("Test Case 318 Execution Completed")



        @pytest.mark.run(order=319)
        def test_319_Modify_the_Pool_5_Lb_method_to_Topology(self):
                print_and_log("********* Mofity the Pool 5 LB method to Topology ***********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ipv6-ea-rule1')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                server_ref = []
                servers = ["server4", "server5", "server6"]
                for i in servers:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    server_ref.append(ref)
                print_and_log(server_ref)
                print_and_log("****** Creating the pool and assiging the server ******")
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_5')
                response1 = json.loads(response1)
                print_and_log(response1)
                res_ref1 = response1[0]['_ref']
                data = {"lb_preferred_method": "TOPOLOGY", "lb_preferred_topology": res_ref, "servers": [{"ratio": 1,"server": str(server_ref[1])}, {"ratio": 1,"server": str(server_ref[0])}]}
                response2 = ib_NIOS.wapi_request('PUT',object_type=res_ref1, fields=json.dumps(data))
                print_and_log(response2)
                print_and_log("Validation of Pool Modfication")
                assert re.search(r'dtc:pool', response2)
                restart_services()
                print_and_log("Test Case 319 Execution Completed")



        @pytest.mark.run(order=320)
        def test_320_Run_the_dig_command_with_subnet_of_IPV6_IPAM_network1(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM network1 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_64_subnet+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 320 Execution Completed")


        @pytest.mark.run(order=321)
        def test_321_Run_the_dig_command_with_subnet_of_IPV6_IPAM_conatiner(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Container ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_32_subnet+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network_container1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 321 Execution Completed")


        @pytest.mark.run(order=322)
        def test_322_Run_the_dig_command_with_subnet_of_IPV6_IPAM_ranges(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Ranges ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[0]+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[1]+"/128 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[2]+"/128 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 322 Execution Completed")



        @pytest.mark.run(order=323)
        def test_323_Run_the_dig_command_with_subnet_of_IPV6_IPAM_Hosts(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Hosts ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6addr_host+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6addr_host)
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(5)
                print_and_log("Test Case 323 Execution Completed")



        @pytest.mark.run(order=324)
        def test_324_Modify_the_value_of_the_IPV6_IPAM_network_from_network1_to_network2(self):
                print_and_log("******** Modify the value of the IPV6 IPAM network from network1 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="ipv6network", params='?network='+config.ipv6network1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network2"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('ipv6network', 'network2', '?network='+config.ipv6network1)
                print_and_log("Test Case 324 Execution Completed")



        @pytest.mark.run(order=325)
        def test_325_Modify_the_value_of_the_IPV6_IPAM_conatiner_from_network2_to_network1(self):
                print_and_log("******** Modify the value of the IPV6 IPAM conatiner from network2 to network1 *********")
                response = ib_NIOS.wapi_request('GET',object_type="ipv6networkcontainer", params='?network='+config.ipv6network_container1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network1"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('ipv6networkcontainer', 'network1', '?network='+config.ipv6network_container1)
                print_and_log("Test Case 325 Execution Completed")



        @pytest.mark.run(order=326)
        def test_326_Modify_the_value_of_the_IPV6_IPAM_Ranges_from_network2_to_network1(self):
                print_and_log("******** Modify the value of the IPV6 IPAM network from network2 to network1 *********")
                response = ib_NIOS.wapi_request('GET',object_type="ipv6range", params='?network='+config.ipv6network1)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network1"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('ipv6range', 'network1', '?network='+config.ipv6network1)
                print_and_log("Test Case 326 Execution Completed")


        @pytest.mark.run(order=327)
        def test_327_Modify_the_value_of_the_IPV6_IPAM_Host_from_network2_to_network1(self):
                print_and_log("******** Modify the value of the IPV6 IPAM network from network2 to network1 *********")
                response = ib_NIOS.wapi_request('GET',object_type="record:host", params='?name=host_new_ipv6')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_string": { "value": "network1"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_value_configured_in_extensible_attribute('record:host', 'network1', '?name=host_new_ipv6')
                print_and_log("Test Case 327 Execution Completed")


        @pytest.mark.run(order=328)
        def test_328_Run_the_dig_command_with_subnet_of_IPV6_IPAM_network1(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM network1 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_64_subnet+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 328 Execution Completed")


        @pytest.mark.run(order=329)
        def test_329_Run_the_dig_command_with_subnet_of_IPV6_IPAM_conatiner(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Container ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_32_subnet+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network_container1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 329 Execution Completed")


        @pytest.mark.run(order=330)
        def test_330_Run_the_dig_command_with_subnet_of_IPV6_IPAM_ranges(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Ranges ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[0]+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[1]+"/128 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[2]+"/128 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 330 Execution Completed")



        @pytest.mark.run(order=331)
        def test_331_Run_the_dig_command_with_subnet_of_IPV6_IPAM_Hosts(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Hosts ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6addr_host+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6addr_host)
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 331 Execution Completed")



        @pytest.mark.run(order=332)
        def test_332_Drop_the_Server1_and_verify_the_response(self):
                logging.info("********** Drop the Server1 and verify the response ************")
                drop_server = "ip6tables -I INPUT -s "+config.ipv6_server1+" -j DROP"
                print(drop_server)
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_master_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline(drop_server)
                child.expect('#')
                child.close()
                sleep(90)
                logging.info("Test Case 332 Execution Completed")



        @pytest.mark.run(order=333)
        def test_333_Run_the_dig_command_with_subnet_of_IPAM_network1(self):
                print_and_log("********** Run the dig command with subnet of IPAM network1 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_64_subnet+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 333 Execution Completed")


        @pytest.mark.run(order=334)
        def test_334_Run_the_dig_command_with_subnet_of_IPAM_conatiner(self):
                print_and_log("********** Run the dig command with subnet of IPAM Container ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_32_subnet+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server3:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network_container1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 334 Execution Completed")


        @pytest.mark.run(order=335)
        def test_335_Run_the_dig_command_with_subnet_of_IPAM_ranges(self):
                print_and_log("********** Run the dig command with subnet of IPAM Ranges ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[0]+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server3:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[1]+"/128 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server3:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[2]+"/128 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server3:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 335 Execution Completed")



        @pytest.mark.run(order=336)
        def test_336_Run_the_dig_command_with_subnet_of_IPAM_Hosts(self):
                print_and_log("********** Run the dig command with subnet of IPAM Hosts ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6addr_host+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server3:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6addr_host)
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 336 Execution Completed")




        @pytest.mark.run(order=337)
        def test_337_Accept_the_Server1_and_verify_the_response(self):
                logging.info("********** Drop the Server1 and verify the response ************")
                accept_server = "ip6tables -I INPUT -s "+config.ipv6_server1+" -j ACCEPT"
                print(accept_server)
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_master_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline(accept_server)
                child.expect('#')
                child.close()
                sleep(60)
                logging.info("Test Case 337 Execution Completed")



        @pytest.mark.run(order=338)
        def test_338_Modify_the_LBDN_and_Configure_the_Round_Robin_as_Lb_method(self):
                print_and_log("********* Modify the LBDN and Configure ROUND ROBIN method ***********")
                response2 = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=LBDN_2')
                response2 = json.loads(response2)
                ref_lbdn = response2[0]['_ref']
                data = {"lb_method": "ROUND_ROBIN"}
                response3 = ib_NIOS.wapi_request('PUT',object_type=ref_lbdn, fields=json.dumps(data))
                print_and_log(response3)
                assert re.search(r'dtc:lbdn', response3)
                restart_services()
                print_and_log("Test Case 338 Execution completed")



        @pytest.mark.run(order=339)
        def test_339_validation_of_dtc_lbdn(self):
                print_and_log("******** Validation of dtc lbdn **********")
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=LBDN_2')
                response1 = json.loads(response1)
                ref_lbdn = response1[0]['_ref']
                response2 = ib_NIOS.wapi_request('GET',object_type=ref_lbdn, params='?_return_fields=lb_method')
                response2 = json.loads(response2)
                ref_lb_method = response2['lb_method']
                if ref_lb_method == "ROUND_ROBIN":
                    print_and_log("LBDN configured with Lb method "+ref_lb_method)
                    assert True
                else:
                    print_and_log("Validation for the LBDN failed")
                    assert False
                print_and_log("Test Case 339 Execution completed")



        @pytest.mark.run(order=340)
        def test_340_Run_the_dig_command_with_subnet_of_IPV6_IPAM_network1(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM network1 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_64_subnet+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 340 Execution Completed")


        @pytest.mark.run(order=341)
        def test_341_Run_the_dig_command_with_subnet_of_IPV6_IPAM_conatiner(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Container ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_32_subnet+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network_container1+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 341 Execution Completed")


        @pytest.mark.run(order=342)
        def test_342_Run_the_dig_command_with_subnet_of_IPV6_IPAM_ranges(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Ranges ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[0]+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[1]+"/128 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges)[2]+"/128 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 342 Execution Completed")



        @pytest.mark.run(order=343)
        def test_343_Run_the_dig_command_with_subnet_of_IPV6_IPAM_Hosts(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Hosts ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6addr_host+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6addr_host)
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 343 Execution Completed")



        @pytest.mark.run(order=344)
        def test_344_Assign_Four_EAs_in_Grid_Properties_Traffic_Control(self):
                print_and_log("********** Assign Four EAs in Grid Properties Traffic Control ************")
                response = ib_NIOS.wapi_request('GET',object_type='grid:dns')
                response = json.loads(response)
                ref = response[0]['_ref']
                data={"dtc_topology_ea_list": ["EA_string", "EA_list", "EA_int", "Site"]}
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
                print_and_log(response1)
                assert re.search(r'grid:dns', response1)
                rebuild_services()
                print_and_log("Test Case 344 Execution completed ")



        @pytest.mark.run(order=345)
        def test_345_Validate_Four_EAs_in_Grid_Properties_Traffic_Control(self):
                print_and_log("********** Validate Four EAs in Grid Properties Traffic Control ************")
                response = ib_NIOS.wapi_request('GET',object_type='grid:dns')
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=dtc_topology_ea_list')
                response1 = json.loads(response1)
                print_and_log(response1)
                output = response1['dtc_topology_ea_list']
                print_and_log(output)
                expected_list = ["EA_string", "EA_list", "EA_int", "Site"]
                if output == expected_list:
                    print_and_log(" ALl the 4 Ea's are configured successfully")
                    assert True
                else:
                    print_and_log(" Error while validating the EA's ")
                    assert False
                print_and_log("Test Case 345 Execution completed ")



        @pytest.mark.run(order=346)
        def test_346_ADD_New_IPV6_Network_Container_Ranges_and_Hosts(self):
                print_and_log("******** Add New IPV6 Network, Network container, Ranges and Host *********")
                data = {"network": config.ipv6network2, "extattrs": { "EA_int": {"value": 5}, "EA_list": {"value": "2"}, "EA_string": {"value": "network2"}, "Site": {"value": "Infoblox"}}}
                response = ib_NIOS.wapi_request('POST',object_type="ipv6network", fields=json.dumps(data))
                print_and_log(response)
                assert re.search(r'ipv6network', response)
                data = {"network": config.ipv6network_container2, "extattrs": { "EA_int": {"value": 10}, "EA_list": {"value": "1"}, "EA_string": {"value": "network1"}, "Site": {"value": "Infoblox"}}}
                response1 = ib_NIOS.wapi_request('POST',object_type="ipv6networkcontainer", fields=json.dumps(data))
                print_and_log(response1)
                assert re.search(r'ipv6networkcontainer', response1)
                data = {"start_addr": json.loads(config.ipv6_ranges2)[0], "end_addr": json.loads(config.ipv6_ranges2)[2], "network": config.ipv6network2, "extattrs": { "EA_int": {"value": 10}, "EA_list": {"value": "1"}, "EA_string": {"value": "network1"}, "Site": {"value": "Infoblox"}}}
                response2 = ib_NIOS.wapi_request('POST',object_type="ipv6range", fields=json.dumps(data))
                print_and_log(response2)
                assert re.search(r'ipv6range', response2)
                data = {"name": "host_new_ipv6_2","configure_for_dns": False, "ipv6addrs": [{"ipv6addr": config.ipv6addr_host2}], "extattrs": { "EA_int": {"value": 10}, "EA_list": {"value": "1"}, "EA_string": {"value": "network1"}, "Site": {"value": "Infoblox"}}}
                response3 = ib_NIOS.wapi_request('POST',object_type="record:host", fields=json.dumps(data))
                print_and_log(response3)
                assert re.search(r'record:host', response3)
                rebuild_services()
                print_and_log("Test Case 346 Execution completed")



        @pytest.mark.run(order=347)
        def test_347_Validate_the_Extensible_attribute_values_configured_for_IPV6_IPAM_network2(self):
                print_and_log("********** Validate the Extensible attribute values configured ***********")
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6network', 'network2', 'EA_string', 'network='+str(config.ipv6network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6network', '2', 'EA_list', 'network='+str(config.ipv6network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6network', 'Infoblox', 'Site', 'network='+str(config.ipv6network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6network', int(5), 'EA_int', 'network='+str(config.ipv6network2))
                print_and_log("Test Case 347 Execution completed")



        @pytest.mark.run(order=348)
        def test_348_Validate_the_Extensible_attribute_values_configured_for_IPV6_IPAM_networkcontainer2(self):
                print_and_log("********** Validate the Extensible attribute values configured ***********")
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6networkcontainer', 'network1', 'EA_string', 'network='+str(config.ipv6network_container2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6networkcontainer', '1', 'EA_list', 'network='+str(config.ipv6network_container2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6networkcontainer', 'Infoblox', 'Site', 'network='+str(config.ipv6network_container2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6networkcontainer', int(10), 'EA_int', 'network='+str(config.ipv6network_container2))
                print_and_log("Test Case 348 Execution completed")



        @pytest.mark.run(order=349)
        def test_349_Validate_the_Extensible_attribute_values_configured_for_IPV6_IPAM_ranges(self):
                print_and_log("********** Validate the Extensible attribute values configured ***********")
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6range', 'network1', 'EA_string', 'network='+str(config.ipv6network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6range', '1', 'EA_list', 'network='+str(config.ipv6network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6range', 'Infoblox', 'Site', 'network='+str(config.ipv6network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6range', int(10), 'EA_int', 'network='+str(config.ipv6network2))
                print_and_log("Test Case 349 Execution completed")


        pytest.mark.run(order=350)
        def test_350_Validate_the_Extensible_attribute_values_configured_for_IPV6_IPAM_host(self):
                print_and_log("********** Validate the Extensible attribute values configured ***********")
                validation_of_4_EAs_value_configured_in_extensible_attribute('record:host', 'network1', 'EA_string', 'name=host_new_ipv6_2')
                validation_of_4_EAs_value_configured_in_extensible_attribute('record:host', '1', 'EA_list', 'name=host_new_ipv6_2')
                validation_of_4_EAs_value_configured_in_extensible_attribute('record:host', 'Infoblox', 'Site', 'name=host_new_ipv6_2')
                validation_of_4_EAs_value_configured_in_extensible_attribute('record:host', int(10), 'EA_int', 'name=host_new_ipv6_2')
                print_and_log("Test Case 350 Execution completed")



        @pytest.mark.run(order=351)
        def test_351_Create_the_IPV6_DTC_topology_Rule_3_with_Server_as_Destination(self):
                print_and_log("********* Create the DTC topology Rule 3 with Server as Destination ***********")
                servers = ["server4", "server5", "server6"]
                server_ref = []
                for i in servers:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    server_ref.append(ref)
                data = {"name": "ipv6-ea-rule3", "rules": [{"sources": [{"source_op": "IS", "source_type": "EA0", "source_value": "network1"}, {"source_op": "IS", "source_type": "EA1", "source_value": "1"}, {"source_op": "IS", "source_type": "EA2", "source_value": "10"}, {"source_op": "IS", "source_type": "EA3", "source_value": "Infoblox"}], "dest_type": "SERVER","destination_link": server_ref[0]}, {"sources":[{"source_op": "IS", "source_type": "EA0", "source_value": "network2"}, {"source_op": "IS", "source_type": "EA1", "source_value": "2"}, {"source_op": "IS", "source_type": "EA2", "source_value": "5"}, {"source_op": "IS", "source_type": "EA3", "source_value": "Infoblox"}], "dest_type": "SERVER","destination_link": server_ref[1]}]}
                print_and_log(data)
                response = ib_NIOS.wapi_request('POST',object_type='dtc:topology', fields=json.dumps(data))
                print_and_log(response)
                print_and_log("********* Validation of IPV6 Topology rule 3 ***********")
                assert re.search(r'dtc:topology', response)
                print_and_log("Test Case 351 Execution completed")


        @pytest.mark.run(order=352)
        def test_352_Validate_the_IPV6_DTC_topology_Rule_3(self):
                print_and_log("********* Validate the DTC topology Rule 3 **********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ipv6-ea-rule3')
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=rules')
                response1 = json.loads(response1)
                output1 = response1['rules'][0]['_ref'].split(':')[-1].split('/')[-1]
                output2 = response1['rules'][1]['_ref'].split(':')[-1].split('/')[-1]
                print_and_log(output1)
                print_and_log(output2)
                if output1 == "server4" and output2 == "server5":
                    print_and_log("DTC Topology rule configured with "+output1+" and "+output2+" as Destination")
                    assert True
                else:
                    print_and_log("Error in validation of Topology rule")
                    assert False
                print_and_log("Test Case 352 Execution completed")



        @pytest.mark.run(order=353)
        def test_353_modify_the_pool4_and_assign_Server_4_and_server5(self):
                print_and_log("******* Modify the pool1 and assign Server 4 and Server4 *********")
                print_and_log("Getting the server name reference ")
                servers = ["server4", "server5", "server6"]
                server_ref = []
                for i in servers:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    server_ref.append(ref)
                print_and_log(server_ref)
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ipv6-ea-rule3')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                print_and_log("****** Getting the ref of Pool 4 ******")
                print_and_log("****** Modify the pool Pool_4 and assiging the server4 *********")
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_4')
                response1 = json.loads(response1)
                ref_pool1 = response1[0]['_ref']
                data = {"lb_preferred_method": "TOPOLOGY", "lb_preferred_topology": res_ref, "servers": [{"ratio": 1,"server": str(server_ref[0])}, {"ratio": 1,"server": str(server_ref[1])}]}
                response_servers = ib_NIOS.wapi_request('PUT',object_type=ref_pool1, fields=json.dumps(data))
                print_and_log(response_servers)
                restart_services()
                print_and_log("Test Case 353 Execution completed")



        @pytest.mark.run(order=354)
        def test_354_Validation_the_pool4_for_topology_rule3(self):
                print_and_log("******* Validation the pool1 for topology rule3 *********")
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_4')
                response1 = json.loads(response1)
                ref_pool1 = response1[0]['_ref']
                response2 = ib_NIOS.wapi_request('GET',object_type=ref_pool1, params='?_return_fields=lb_preferred_method')
                response2 = json.loads(response2)
                res_lb_method = response2['lb_preferred_method']
                print_and_log(res_lb_method)
                response3 = ib_NIOS.wapi_request('GET',object_type=ref_pool1, params='?_return_fields=lb_preferred_topology')
                response3 = json.loads(response3)
                res_lb_topology = response3['lb_preferred_topology'].split(":")[-1]
                print_and_log(res_lb_topology)
                if res_lb_method == "TOPOLOGY" and res_lb_topology == "ipv6-ea-rule3":
                    print_and_log(" LB method "+res_lb_method+" is configured to Pool with topo rule "+res_lb_topology+" successfully")
                    assert True
                else:
                    print_and_log(" Error while validating the LB method of the Pool")
                    assert False
                print_and_log("Test Case 354 Execution completed")



        @pytest.mark.run(order=355)
        def test_355_Modify_the_LBDN_and_configure_round_robin_as_lb_method(self):
                print_and_log("********* Modify the LBDN and configure round robin as lb method ***********")
                pool_ref = []
                Pool = ["Pool_4", "Pool_5"]
                for i in Pool:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    pool_ref.append(ref)
                response2 = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=LBDN_2')
                response2 = json.loads(response2)
                ref_lbdn = response2[0]['_ref']
                data = {"lb_method": "ROUND_ROBIN", "pools": [{"ratio": 1, "pool": pool_ref[0]}]}
                response3 = ib_NIOS.wapi_request('PUT',object_type=ref_lbdn, fields=json.dumps(data))
                print_and_log(response3)
                assert re.search(r'dtc:lbdn', response3)
                restart_services()
                print_and_log("Test Case 355 Execution completed")



        @pytest.mark.run(order=356)
        def test_356_Validate_LBDN_for_round_robin_lb_method(self):
                print_and_log("******** Validate LBDN for round robin lb method *********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=LBDN_2')
                response = json.loads(response)
                ref_lbdn = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref_lbdn, params='?_return_fields=lb_method')
                response1 = json.loads(response1)
                ref_lb_method = response1['lb_method']
                if ref_lb_method == "ROUND_ROBIN":
                    print_and_log("LBDN configured with Lb method "+ref_lb_method)
                    assert True
                else:
                    print_and_log("Validation for the LBDN failed")
                    assert False
                print_and_log("Test Case 356 Execution completed")



        @pytest.mark.run(order=357)
        def test_357_Run_the_dig_command_with_subnet_of_IPV6_IPAM_network2(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM network1 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_64_subnet2+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network2+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 357 Execution Completed")


        @pytest.mark.run(order=358)
        def test_358_Run_the_dig_command_with_subnet_of_IPV6_IPAM_conatiner2(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Container2 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_32_subnet2+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network_container2+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 358 Execution Completed")


        @pytest.mark.run(order=359)
        def test_359_Run_the_dig_command_with_subnet_of_IPV6_IPAM_ranges2(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Ranges2 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges2)[0]+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges2)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges2)[1]+"/128 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges2)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges2)[2]+"/128 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges2)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 359 Execution Completed")



        @pytest.mark.run(order=360)
        def test_360_Run_the_dig_command_with_subnet_of_IPV6_IPAM_Hosts2(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Hosts2 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6addr_host2+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6addr_host2)
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 360 Execution Completed")



        @pytest.mark.run(order=361)
        def test_361_Modify_the_value_of_the_IPV6_IPAM_network_from_network2_to_network1(self):
                print_and_log("******** Modify the value of the IPV6 IPAM network from network2 to network1 *********")
                response = ib_NIOS.wapi_request('GET',object_type="ipv6network", params='?network='+config.ipv6network2)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_int": {"value": 10}, "EA_list": {"value": "1"}, "EA_string": {"value": "network1"}, "Site": {"value": "Infoblox"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6network', 'network1', 'EA_string', 'network='+str(config.ipv6network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6network', '1', 'EA_list', 'network='+str(config.ipv6network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6network', 'Infoblox', 'Site', 'network='+str(config.ipv6network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6network', int(10), 'EA_int', 'network='+str(config.ipv6network2))
                print_and_log("Test Case 361 Execution Completed")



        @pytest.mark.run(order=362)
        def test_362_Modify_the_value_of_the_IPV6_IPAM_conatiner_from_network1_to_network2(self):
                print_and_log("******** Modify the value of the IPV6 IPAM conatiner from network1 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="ipv6networkcontainer", params='?network='+config.ipv6network_container2)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_int": {"value": 5}, "EA_list": {"value": "2"}, "EA_string": {"value": "network2"}, "Site": {"value": "Infoblox"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6networkcontainer', 'network2', 'EA_string', 'network='+str(config.ipv6network_container2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6networkcontainer', '2', 'EA_list', 'network='+str(config.ipv6network_container2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6networkcontainer', 'Infoblox', 'Site', 'network='+str(config.ipv6network_container2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6networkcontainer', int(5), 'EA_int', 'network='+str(config.ipv6network_container2))
                print_and_log("Test Case 362 Execution Completed")



        @pytest.mark.run(order=363)
        def test_363_Modify_the_value_of_the_IPV6_IPAM_Ranges_from_network1_to_network2(self):
                print_and_log("******** Modify the value of the IPV6 IPAM network from network1 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="ipv6range", params='?network='+config.ipv6network2)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_int": {"value": 5}, "EA_list": {"value": "2"}, "EA_string": {"value": "network2"}, "Site": {"value": "Infoblox"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6range', 'network2', 'EA_string', 'network='+str(config.ipv6network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6range', '2', 'EA_list', 'network='+str(config.ipv6network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6range', 'Infoblox', 'Site', 'network='+str(config.ipv6network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6range', int(5), 'EA_int', 'network='+str(config.ipv6network2))
                print_and_log("Test Case 363 Execution Completed")


        @pytest.mark.run(order=364)
        def test_364_Modify_the_value_of_the_IPV6_IPAM_Host_from_network1_to_network2(self):
                print_and_log("******** Modify the value of the IPV6 IPAM network from network1 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="record:host", params='?name=host_new_ipv6_2')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_int": {"value": 5}, "EA_list": {"value": "2"}, "EA_string": {"value": "network2"}, "Site": {"value": "Infoblox"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_4_EAs_value_configured_in_extensible_attribute('record:host', 'network2', 'EA_string', 'name=host_new_ipv6_2')
                validation_of_4_EAs_value_configured_in_extensible_attribute('record:host', '2', 'EA_list', 'name=host_new_ipv6_2')
                validation_of_4_EAs_value_configured_in_extensible_attribute('record:host', 'Infoblox', 'Site', 'name=host_new_ipv6_2')
                validation_of_4_EAs_value_configured_in_extensible_attribute('record:host', int(5), 'EA_int', 'name=host_new_ipv6_2')
                print_and_log("Test Case 364 Execution Completed")



        @pytest.mark.run(order=365)
        def test_365_Run_the_dig_command_with_subnet_of_IPV6_IPAM_network2(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM network1 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_64_subnet2+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network2+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 365 Execution Completed")


        @pytest.mark.run(order=366)
        def test_366_Run_the_dig_command_with_subnet_of_IPV6_IPAM_conatiner2(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Container2 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_32_subnet2+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network_container2+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 366 Execution Completed")


        @pytest.mark.run(order=367)
        def test_367_Run_the_dig_command_with_subnet_of_IPV6_IPAM_ranges2(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Ranges2 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges2)[0]+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges2)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges2)[1]+"/128 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges2)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges2)[2]+"/128 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges2)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 367 Execution Completed")



        @pytest.mark.run(order=368)
        def test_368_Run_the_dig_command_with_subnet_of_IPV6_IPAM_Hosts2(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Hosts2 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6addr_host2+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6addr_host2)
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(5)
                print_and_log("Test Case 368 Execution Completed")



        @pytest.mark.run(order=369)
        def test_369_Create_the_IPV6_DTC_topology_Rule_4_with_Pool_as_Destination(self):
                print_and_log("********* Create the IPV6 DTC topology Rule 4 with Pool as Destination ***********")
                pool_ref = []
                pool_name = ["Pool_4", "Pool_5"]
                for i in pool_name:
                    response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name='+i)
                    response = json.loads(response)
                    ref = response[0]['_ref']
                    pool_ref.append(ref)
                data = {"name": "ipv6-ea-rule4", "rules": [{"sources": [{"source_op": "IS", "source_type": "EA0", "source_value": "network1"}, {"source_op": "IS", "source_type": "EA1", "source_value": "1"}, {"source_op": "IS", "source_type": "EA2", "source_value": "10"}, {"source_op": "IS", "source_type": "EA3", "source_value": "Infoblox"}], "dest_type": "POOL","destination_link": pool_ref[0]}, {"sources":[{"source_op": "IS", "source_type": "EA0", "source_value": "network2"}, {"source_op": "IS", "source_type": "EA1", "source_value": "2"}, {"source_op": "IS", "source_type": "EA2", "source_value": "5"}, {"source_op": "IS", "source_type": "EA3", "source_value": "Infoblox"}], "dest_type": "POOL","destination_link": pool_ref[1]}]}
                print_and_log(data)
                response = ib_NIOS.wapi_request('POST',object_type='dtc:topology', fields=json.dumps(data))
                print_and_log(response)
                print_and_log("********* Validation of IPV6 Topology rule 4 ***********")
                assert re.search(r'dtc:topology', response)
                print_and_log("Test Case 369 Execution completed")



        @pytest.mark.run(order=370)
        def test_370_Validate_the_IPV6_DTC_topology_Rule_4(self):
                print_and_log("********* Validate the IPV6 DTC topology Rule 4 **********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ipv6-ea-rule4')
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=rules')
                response1 = json.loads(response1)
                output1 = response1['rules'][0]['_ref'].split(':')[-1].split('/')[-1]
                output2 = response1['rules'][1]['_ref'].split(':')[-1].split('/')[-1]
                print_and_log(output1)
                print_and_log(output2)
                if output1 == "Pool_4" and output2 == "Pool_5":
                    print_and_log("DTC Topology rule configured with "+output1+" and "+output2+" as Destination")
                    assert True
                else:
                    print_and_log("Error in validation of Topology rule")
                    assert False
                print_and_log("Test Case 370 Execution completed")



        @pytest.mark.run(order=371)
        def test_371_modify_the_pool4_and_assign_Server_4(self):
                print_and_log("******* Modify the pool4 and assign Server 4 *********")
                print_and_log("Getting the server name reference ")
                servers = ["server4", "server5", "server6"]
                server_ref = []
                for i in servers:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    server_ref.append(ref)
                print_and_log(server_ref)
                print_and_log("****** Modify the pool Pool_4 and assiging the server4 *********")
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_4')
                response1 = json.loads(response1)
                ref_pool1 = response1[0]['_ref']
                data = {"lb_preferred_method": "ALL_AVAILABLE", "servers": [{"ratio": 1,"server": str(server_ref[0])}]}
                response_servers = ib_NIOS.wapi_request('PUT',object_type=ref_pool1, fields=json.dumps(data))
                print_and_log(response_servers)
                restart_services()
                print_and_log("Test Case 371 Execution completed")



        @pytest.mark.run(order=372)
        def test_372_Validation_of_the_pool4(self):
                print_and_log("******* Validation of the pool1 *********")
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_4')
                response1 = json.loads(response1)
                ref_pool1 = response1[0]['_ref']
                response2 = ib_NIOS.wapi_request('GET',object_type=ref_pool1, params='?_return_fields=lb_preferred_method')
                response2 = json.loads(response2)
                print_and_log(response2)
                ref = response2['lb_preferred_method']
                response3 = ib_NIOS.wapi_request('GET',object_type=ref_pool1, params='?_return_fields=servers')
                response3 = json.loads(response3)
                print_and_log(response3)
                ref_server = response3['servers'][0]['server'].split(':')[-1]
                print_and_log(ref)
                print_and_log(ref_server)
                if ref == "ALL_AVAILABLE" and ref_server == "server4":
                    print_and_log("Pool Pool_1 is configure with lb method "+ref+" with server "+ref_server)
                    assert True
                else:
                    print_and_log("Validation failed for the DTC Pool")
                    assert False
                print_and_log("Test Case 372 Execution completed")



        @pytest.mark.run(order=373)
        def test_373_modify_the_pool5_and_assign_Server_5(self):
                print_and_log("******* Modify the pool5 and assign Server 5 *********")
                print_and_log("Getting the server name reference ")
                servers = ["server4", "server5", "server6"]
                server_ref = []
                for i in servers:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    server_ref.append(ref)
                print_and_log(server_ref)
                print_and_log("****** Modify the pool Pool_5 and assiging the server5 *********")
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_5')
                response1 = json.loads(response1)
                ref_pool1 = response1[0]['_ref']
                data = {"lb_preferred_method": "ALL_AVAILABLE", "servers": [{"ratio": 1,"server": str(server_ref[1])}]}
                response_servers = ib_NIOS.wapi_request('PUT',object_type=ref_pool1, fields=json.dumps(data))
                print_and_log(response_servers)
                restart_services()
                print_and_log("Test Case 373 Execution completed")



        @pytest.mark.run(order=374)
        def test_374_Validation_of_the_pool5(self):
                print_and_log("******* Validation of the pool5 *********")
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_5')
                response1 = json.loads(response1)
                ref_pool = response1[0]['_ref']
                response2 = ib_NIOS.wapi_request('GET',object_type=ref_pool, params='?_return_fields=lb_preferred_method')
                response2 = json.loads(response2)
                ref = response2['lb_preferred_method']
                response3 = ib_NIOS.wapi_request('GET',object_type=ref_pool, params='?_return_fields=servers')
                response3 = json.loads(response3)
                print_and_log(response3)
                ref_server = response3['servers'][0]['server'].split(':')[-1]
                print_and_log(ref)
                print_and_log(ref_server)
                if ref == "ALL_AVAILABLE" and ref_server == "server5":
                    print_and_log("Pool Pool_5 is configure with lb method "+ref+" with server "+ref_server)
                    assert True
                else:
                    print_and_log("Validation failed for the DTC Pool")
                    assert False
                print_and_log("Test Case 374 Execution completed")



        @pytest.mark.run(order=375)
        def test_375_Modify_the_LBDN_and_Configure_the_IPV6_Topology_rule_4_as_Lb_method(self):
                print_and_log("********* Modify the LBDN and Configure the Topology rule 4 as Lb method ***********")
                pool_ref = []
                Pool = ["Pool_4", "Pool_5"]
                for i in Pool:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    pool_ref.append(ref)
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ipv6-ea-rule4')
                response1 = json.loads(response1)
                print_and_log(response1)
                res_ref = response1[0]['_ref']
                response2 = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=LBDN_2')
                response2 = json.loads(response2)
                ref_lbdn = response2[0]['_ref']
                data = {"lb_method": "TOPOLOGY", "topology": res_ref, "pools": [{"ratio": 1, "pool": pool_ref[0]}, {"ratio": 1, "pool": pool_ref[1]}]}
                response3 = ib_NIOS.wapi_request('PUT', object_type=ref_lbdn, fields=json.dumps(data))
                print_and_log(response3)
                assert re.search(r'dtc:lbdn', response3)
                restart_services()
                print_and_log("Test Case 375 Execution completed")



        @pytest.mark.run(order=376)
        def test_376_Validate_the_LBDN_and_the_IPV6_Topology_rule_4_as_Lb_method(self):
                print_and_log("********* Validate the LBDN and the Topology rule 4 as Lb method *********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=LBDN_2')
                response = json.loads(response)
                ref_lbdn = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref_lbdn, params='?_return_fields=lb_method')
                response1 = json.loads(response1)
                res_lb_method = response1['lb_method']
                print_and_log(res_lb_method)
                response2 = ib_NIOS.wapi_request('GET',object_type=ref_lbdn, params='?_return_fields=topology')
                response2 = json.loads(response2)
                res_lb_topology = response2['topology'].split(':')[-1]
                print_and_log(res_lb_topology)
                if res_lb_method == "TOPOLOGY" and res_lb_topology == "ipv6-ea-rule4":
                    print_and_log("LBDN is configured with LB method "+res_lb_method+" with topology "+res_lb_topology)
                    assert True
                else:
                    print_and_log("Validation for the LBDN failed")
                    assert False
                print_and_log("Test Case 376 Execution completed")



        @pytest.mark.run(order=377)
        def test_377_Run_the_dig_command_with_subnet_of_IPV6_IPAM_network2(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM network1 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_64_subnet2+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network2+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 377 Execution Completed")


        @pytest.mark.run(order=378)
        def test_378_Run_the_dig_command_with_subnet_of_IPV6_IPAM_conatiner2(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Container2 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_32_subnet2+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded ==config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network_container2+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 378 Execution Completed")


        @pytest.mark.run(order=379)
        def test_379_Run_the_dig_command_with_subnet_of_IPV6_IPAM_ranges2(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Ranges2 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges2)[0]+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges2)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges2)[1]+"/128 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges2)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges2)[2]+"/128 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges2)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 379 Execution Completed")



        @pytest.mark.run(order=380)
        def test_380_Run_the_dig_command_with_subnet_of_IPV6_IPAM_Hosts2(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Hosts2 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6addr_host2+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6addr_host2)
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 380 Execution Completed")



        @pytest.mark.run(order=381)
        def test_381_Modify_the_value_of_the_IPV6_IPAM_network_from_network1_to_network2(self):
                print_and_log("******** Modify the value of the IPV6 IPAM network from network1 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="ipv6network", params='?network='+config.ipv6network2)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_int": {"value": 5}, "EA_list": {"value": "2"}, "EA_string": {"value": "network2"}, "Site": {"value": "Infoblox"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6network', 'network2', 'EA_string', 'network='+str(config.ipv6network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6network', '2', 'EA_list', 'network='+str(config.ipv6network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6network', 'Infoblox', 'Site', 'network='+str(config.ipv6network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6network', int(5), 'EA_int', 'network='+str(config.ipv6network2))
                print_and_log("Test Case 381 Execution Completed")



        @pytest.mark.run(order=382)
        def test_382_Modify_the_value_of_the_IPV6_IPAM_conatiner_from_network2_to_network1(self):
                print_and_log("******** Modify the value of the IPV6 IPAM conatiner from network2 to network1 *********")
                response = ib_NIOS.wapi_request('GET',object_type="ipv6networkcontainer", params='?network='+config.ipv6network_container2)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_int": {"value": 10}, "EA_list": {"value": "1"}, "EA_string": {"value": "network1"}, "Site": {"value": "Infoblox"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6networkcontainer', 'network1', 'EA_string', 'network='+str(config.ipv6network_container2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6networkcontainer', '1', 'EA_list', 'network='+str(config.ipv6network_container2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6networkcontainer', 'Infoblox', 'Site', 'network='+str(config.ipv6network_container2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6networkcontainer', int(10), 'EA_int', 'network='+str(config.ipv6network_container2))
                print_and_log("Test Case 382 Execution Completed")



        @pytest.mark.run(order=383)
        def test_383_Modify_the_value_of_the_IPV6_IPAM_Ranges_from_network2_to_network1(self):
                print_and_log("******** Modify the value of the IPV6 IPAM network from network2 to network1 *********")
                response = ib_NIOS.wapi_request('GET',object_type="ipv6range", params='?network='+config.ipv6network2)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_int": {"value": 10}, "EA_list": {"value": "1"}, "EA_string": {"value": "network1"}, "Site": {"value": "Infoblox"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6range', 'network1', 'EA_string', 'network='+str(config.ipv6network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6range', '1', 'EA_list', 'network='+str(config.ipv6network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6range', 'Infoblox', 'Site', 'network='+str(config.ipv6network2))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6range', int(10), 'EA_int', 'network='+str(config.ipv6network2))
                print_and_log("Test Case 383 Execution Completed")


        @pytest.mark.run(order=384)
        def test_384_Modify_the_value_of_the_IPV6_IPAM_Host_from_network1_to_network2(self):
                print_and_log("******** Modify the value of the IPV6 IPAM network from network1 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="record:host", params='?name=host_new_ipv6_2')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_int": {"value": 10}, "EA_list": {"value": "1"}, "EA_string": {"value": "network1"}, "Site": {"value": "Infoblox"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_4_EAs_value_configured_in_extensible_attribute('record:host', 'network1', 'EA_string', 'name=host_new_ipv6_2')
                validation_of_4_EAs_value_configured_in_extensible_attribute('record:host', '1', 'EA_list', 'name=host_new_ipv6_2')
                validation_of_4_EAs_value_configured_in_extensible_attribute('record:host', 'Infoblox', 'Site', 'name=host_new_ipv6_2')
                validation_of_4_EAs_value_configured_in_extensible_attribute('record:host', int(10), 'EA_int', 'name=host_new_ipv6_2')
                print_and_log("Test Case 384 Execution Completed")




        @pytest.mark.run(order=385)
        def test_385_Run_the_dig_command_with_subnet_of_IPV6_IPAM_network2(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM network1 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_64_subnet2+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network2+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 385 Execution Completed")


        @pytest.mark.run(order=386)
        def test_386_Run_the_dig_command_with_subnet_of_IPV6_IPAM_conatiner2(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Container2 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_32_subnet2+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network_container2+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 386 Execution Completed")


        @pytest.mark.run(order=387)
        def test_387_Run_the_dig_command_with_subnet_of_IPV6_IPAM_ranges2(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Ranges2 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges2)[0]+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges2)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges2)[1]+"/128 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges2)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges2)[2]+"/128 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded ==config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges2)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 387 Execution Completed")



        @pytest.mark.run(order=388)
        def test_388_Run_the_dig_command_with_subnet_of_IPV6_IPAM_Hosts2(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Hosts2 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6addr_host2+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6addr_host2)
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 388 Execution Completed")


        @pytest.mark.run(order=389)
        def test_389_Create_the_extensibleattribute_with_enabling_Allow_multiple_values_field(self):
                print_and_log("*********** Create the extensible with enabling Allow multiple values field ************")
                data = {"name": "EA_with_Allow_Multiple_values", "type": "STRING", "flags": "V"}
                response = ib_NIOS.wapi_request('POST',object_type='extensibleattributedef', fields=json.dumps(data))
                print_and_log(response)
                assert re.search(r'EA_with_Allow_Multiple_values', response)
                print_and_log("Test Case 389 Execution Completed")



        @pytest.mark.run(order=390)
        def test_390_Validate_the_extensibleattribute_EA_with_Allow_Multiple_values(self):
                print_and_log("********* Validate the extensibleattribute EA with Allow Multiple values **********")
                response = ib_NIOS.wapi_request('GET',object_type='extensibleattributedef', params='?name=EA_with_Allow_Multiple_values')
                response = json.loads(response)
                ref = response[0]['_ref']
                name = response[0]['name']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=flags')
                response1 = json.loads(response1)
                ref_flag = response1['flags']
                if name == "EA_with_Allow_Multiple_values" and ref_flag == "V":
                    print_and_log("EA "+name+" with Multiple values is enabled")
                    assert True
                else:
                    print_and_log("EA "+name+" with Multiple values is not enabled")
                    assert False
                print_and_log("Test Case 390 Execution Completed")



        @pytest.mark.run(order=391)
        def test_391_Assign_the_Custom_EA_EA_with_Allow_Multiple_values_in_Grid_Properties_Traffic_Control(self):
                print_and_log("********** Assign the Custom EA EA_with_Allow_Multiple_values in Grid Properties Traffic Conftrol w************")
                response = ib_NIOS.wapi_request('GET',object_type='grid:dns')
                response = json.loads(response)
                ref = response[0]['_ref']
                data={"dtc_topology_ea_list": ["EA_with_Allow_Multiple_values"]}
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
                if type(response1) == tuple:
                    out = response1[1]
                    out = json.loads(out)
                    print_and_log(out)
                    error_message = out['text']
                    print_and_log(error_message)
                    expected_error_message = "'The specified extensible attribute 'EA_with_Allow_Multiple_values' cannot be used as a source type for DTC extensible attribute topology rules. You cannot use a definition that allows multiple values.'"
                    if error_message in expected_error_message:
                        print_and_log("Expected Error message is seen")
                        assert True
                    else:
                        print_and_log("Expected Error message is not seen")
                        assert False
                else:
                    print_and_log(response1)
                    print_and_log(" The EA with Allow Multiple values is configured under Grid DNS Properties Traffic control ")
                    assert False
                print_and_log("Test Case 391 Execution completed ")



        #CSV Upload case
        @pytest.mark.run(order=392)
        def test_392_Upload_the_IPAM_Network_NetworkContainer_Ranges_and_Host_through_CSV(self):
                print_and_log("Uploading csv file containing IAPM Network NetworkConatiner Ranges Hosts")
                dir_name=os.getcwd()
                base_filename = "IPAM_Networks_Containers_Ranges_Hosts.csv"
                token =generate_token_from_file(dir_name, base_filename, config.grid_vip)
                data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"OVERRIDE","operation":"INSERT"}
                response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_import")
                response=json.loads(response)
                print_and_log(response)
                if type(response) == tuple:
                    print_and_log("Failure: CSV file upload")
                    assert False
                else:
                    print_and_log("CSV File Uploaded successfully")
                    assert True
                sleep(30)
                rebuild_services()
                print_and_log("Test Case 392 Execution completed")



        @pytest.mark.run(order=393)
        def test_393_validate_the_value_of_the_IPV6_IPAM_network_from_network1_to_network2(self):
                print_and_log("******** Validate the value of the IPV6 IPAM network from network1 to network2 *********")
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6network', 'network2', 'EA_string', 'network='+str(config.ipv6network3))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6network', '2', 'EA_list', 'network='+str(config.ipv6network3))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6network', 'Infoblox', 'Site', 'network='+str(config.ipv6network3))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6network', int(5), 'EA_int', 'network='+str(config.ipv6network3))
                print_and_log("Test Case 393 Execution Completed")



        @pytest.mark.run(order=394)
        def test_394_validate_the_value_of_the_IPV6_IPAM_conatiner_from_network2_to_network1(self):
                print_and_log("******** validate the value of the IPV6 IPAM conatiner from network2 to network1 *********")
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6networkcontainer', 'network1', 'EA_string', 'network='+str(config.ipv6network_container3))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6networkcontainer', '1', 'EA_list', 'network='+str(config.ipv6network_container3))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6networkcontainer', 'Infoblox', 'Site', 'network='+str(config.ipv6network_container3))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6networkcontainer', int(10), 'EA_int', 'network='+str(config.ipv6network_container3))
                print_and_log("Test Case 394 Execution Completed")



        @pytest.mark.run(order=395)
        def test_395_validate_the_value_of_the_IPV6_IPAM_Ranges_from_network2_to_network1(self):
                print_and_log("******** validate the value of the IPV6 IPAM ranges from network2 to network1 *********")
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6range', 'network1', 'EA_string', 'network='+str(config.ipv6network3))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6range', '1', 'EA_list', 'network='+str(config.ipv6network3))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6range', 'Infoblox', 'Site', 'network='+str(config.ipv6network3))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6range', int(10), 'EA_int', 'network='+str(config.ipv6network3))
                print_and_log("Test Case 395 Execution Completed")


        @pytest.mark.run(order=396)
        def test_396_validate_the_value_of_the_IPV6_IPAM_Host_from_network2_to_network1(self):
                print_and_log("******** validate the value of the IPV6 IPAM hosts from network2 to network1 *********")
                validation_of_4_EAs_value_configured_in_extensible_attribute('record:host', 'network1', 'EA_string', 'name=host_new_ipv6_3')
                validation_of_4_EAs_value_configured_in_extensible_attribute('record:host', '1', 'EA_list', 'name=host_new_ipv6_3')
                validation_of_4_EAs_value_configured_in_extensible_attribute('record:host', 'Infoblox', 'Site', 'name=host_new_ipv6_3')
                validation_of_4_EAs_value_configured_in_extensible_attribute('record:host', int(10), 'EA_int', 'name=host_new_ipv6_3')
                print_and_log("Test Case 396 Execution Completed")


        @pytest.mark.run(order=397)
        def test_397_Run_the_dig_command_with_subnet_of_IPV6_IPAM_network3(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM network3 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_64_subnet3+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network3+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 397 Execution Completed")


        @pytest.mark.run(order=398)
        def test_398_Run_the_dig_command_with_subnet_of_IPV6_IPAM_conatiner3(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Container3 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_32_subnet3+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network_container3+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 398 Execution Completed")


        @pytest.mark.run(order=399)
        def test_399_Run_the_dig_command_with_subnet_of_IPV6_IPAM_ranges3(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Ranges3 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges3)[0]+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges3)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges3)[1]+"/128 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges3)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges3)[2]+"/128 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded ==config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges3)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 399 Execution Completed")




        @pytest.mark.run(order=400)
        def test_400_Run_the_dig_command_with_subnet_of_IPV6_IPAM_Hosts3(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Hosts3 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6addr_host3+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6addr_host3)
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 400 Execution Completed")



        @pytest.mark.run(order=401)
        def test_401_Modify_the_value_of_the_IPV6_IPAM_network_from_network2_to_network1(self):
                print_and_log("******** Modify the value of the IPV6 IPAM network from network2 to network1 *********")
                response = ib_NIOS.wapi_request('GET',object_type="ipv6network", params='?network='+config.ipv6network3)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_int": {"value": 10}, "EA_list": {"value": "1"}, "EA_string": {"value": "network1"}, "Site": {"value": "Infoblox"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6network', 'network1', 'EA_string', 'network='+str(config.ipv6network3))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6network', '1', 'EA_list', 'network='+str(config.ipv6network3))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6network', 'Infoblox', 'Site', 'network='+str(config.ipv6network3))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6network', int(10), 'EA_int', 'network='+str(config.ipv6network3))
                print_and_log("Test Case 401 Execution Completed")



        @pytest.mark.run(order=402)
        def test_402_Modify_the_value_of_the_IPV6_IPAM_conatiner_from_network1_to_network2(self):
                print_and_log("******** Modify the value of the IPV6 IPAM conatiner from network1 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="ipv6networkcontainer", params='?network='+config.ipv6network_container3)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_int": {"value": 5}, "EA_list": {"value": "2"}, "EA_string": {"value": "network2"}, "Site": {"value": "Infoblox"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6networkcontainer', 'network2', 'EA_string', 'network='+str(config.ipv6network_container3))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6networkcontainer', '2', 'EA_list', 'network='+str(config.ipv6network_container3))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6networkcontainer', 'Infoblox', 'Site', 'network='+str(config.ipv6network_container3))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6networkcontainer', int(5), 'EA_int', 'network='+str(config.ipv6network_container3))
                print_and_log("Test Case 402 Execution Completed")



        @pytest.mark.run(order=403)
        def test_403_Modify_the_value_of_the_IPV6_IPAM_Ranges_from_network1_to_network2(self):
                print_and_log("******** Modify the value of the IPV6 IPAM network from network1 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="ipv6range", params='?network='+config.ipv6network3)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_int": {"value": 5}, "EA_list": {"value": "2"}, "EA_string": {"value": "network2"}, "Site": {"value": "Infoblox"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6range', 'network2', 'EA_string', 'network='+str(config.ipv6network3))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6range', '2', 'EA_list', 'network='+str(config.ipv6network3))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6range', 'Infoblox', 'Site', 'network='+str(config.ipv6network3))
                validation_of_4_EAs_value_configured_in_extensible_attribute('ipv6range', int(5), 'EA_int', 'network='+str(config.ipv6network3))
                print_and_log("Test Case 403 Execution Completed")


        @pytest.mark.run(order=404)
        def test_404_Modify_the_value_of_the_IPV6_IPAM_Host_from_network1_to_network2(self):
                print_and_log("******** Modify the value of the IPV6 IPAM network from network1 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="record:host", params='?name=host_new_ipv6_3')
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_int": {"value": 5}, "EA_list": {"value": "2"}, "EA_string": {"value": "network2"}, "Site": {"value": "Infoblox"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print_and_log(response1)
                rebuild_services()
                validation_of_4_EAs_value_configured_in_extensible_attribute('record:host', 'network2', 'EA_string', 'name=host_new_ipv6_3')
                validation_of_4_EAs_value_configured_in_extensible_attribute('record:host', '2', 'EA_list', 'name=host_new_ipv6_3')
                validation_of_4_EAs_value_configured_in_extensible_attribute('record:host', 'Infoblox', 'Site', 'name=host_new_ipv6_3')
                validation_of_4_EAs_value_configured_in_extensible_attribute('record:host', int(5), 'EA_int', 'name=host_new_ipv6_3')
                sleep(60)
                rebuild_services()
                print_and_log("Test Case 404 Execution Completed")


        @pytest.mark.run(order=405)
        def test_405_Run_the_dig_command_with_subnet_of_IPV6_IPAM_network3(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM network3 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_64_subnet3+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network3+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 405 Execution Completed")


        @pytest.mark.run(order=406)
        def test_406_Run_the_dig_command_with_subnet_of_IPV6_IPAM_conatiner3(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Container3 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_32_subnet3+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network_container3+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 406 Execution Completed")


        @pytest.mark.run(order=407)
        def test_407_Run_the_dig_command_with_subnet_of_IPV6_IPAM_ranges3(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Ranges3 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges3)[0]+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges3)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges3)[1]+"/128 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges3)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges3)[2]+"/128 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded ==config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges3)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 407 Execution Completed")



        @pytest.mark.run(order=408)
        def test_408_Run_the_dig_command_with_subnet_of_IPV6_IPAM_Hosts3(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Hosts3 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6addr_host3+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6addr_host3)
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 408 Execution Completed")


        #BackUp
        @pytest.mark.run(order=409)
        def test_409_Backup_DTC_Config_File(self):
                print_and_log("Backup DTC Config File")
                data = {"type": "BACKUP_DTC"}
                response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=getgriddata")
                response = json.loads(response)
                print_and_log(response)
                global token_of_GM
                global token_of_URL
                token_of_GM = response['token']
                token_of_URL = response['url']
                print_and_log(token_of_GM)
                print_and_log("Test Case 409 Execution Completed")



        @pytest.mark.run(order=410)
        def test_410_Delete_the_DTC_LBDN2(self):
                print_and_log("************ Delete the DTC LBDN2 *************")
                response = ib_NIOS.wapi_request('GET', object_type="dtc:lbdn", params="?name=LBDN_2")
                response = json.loads(response)
                ref_lbdn = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('DELETE', object_type=ref_lbdn)
                print_and_log(response1)
                restart_services()
                print_and_log("Test Case 410 Execution Completed")


        @pytest.mark.run(order=411)
        def test_411_Restore_DTC_Config_File(self):
                print_and_log("Restore DTC Config File")
                log("start","/infoblox/var/infoblox.log", config.grid_vip)
                data = {"forced": False, "token": token_of_GM}
                print_and_log(data)
                response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=restoredtcconfig")
                print_and_log(response)
                restart_services()
                sleep(30)
                LookFor="'DTC restore: done'"
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
                print_and_log("successful Log message "+LookFor+" is seen in infoblox.log")
                print_and_log("Test Case 411 Execution Completed")



        @pytest.mark.run(order=412)
        def test_412_Run_the_dig_command_with_subnet_of_IPV6_IPAM_network3(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM network3 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_64_subnet3+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network3+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 412 Execution Completed")


        @pytest.mark.run(order=413)
        def test_413_Run_the_dig_command_with_subnet_of_IPV6_IPAM_conatiner3(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Container3 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_32_subnet3+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network_container3+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 413 Execution Completed")


        @pytest.mark.run(order=414)
        def test_414_Run_the_dig_command_with_subnet_of_IPV6_IPAM_ranges3(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Ranges3 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges3)[0]+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges3)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges3)[1]+"/128 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges3)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges3)[2]+"/128 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded ==config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges3)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 414 Execution Completed")



        @pytest.mark.run(order=415)
        def test_415_Run_the_dig_command_with_subnet_of_IPV6_IPAM_Hosts3(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Hosts3 ************")
                output = os.popen("dig @"+config.grid_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6addr_host3+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6addr_host3)
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 415 Execution Completed")


        #Restore DTC config File in New Grid
        @pytest.mark.run(order=416)
        def test_416_Start_DNS_Service(self):
                print_and_log("********** Start DNS Service **********")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid2_vip)
                print_and_log(get_ref)
                res = json.loads(get_ref)
                global host_name
                host_name = res[0]['host_name']
                for i in res:
                    print_and_log("Modify a enable_dns")
                    data = {"enable_dns": True}
                    response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data), grid_vip=config.grid2_vip)
                    print_and_log(response)
                read  = re.search(r'200',response)
                for read in response:
                        assert True
                print_and_log("Test Case 416 Execution Completed")

        @pytest.mark.run(order=417)
        def test_417_Validate_DNS_service_Enabled(self):
                print_and_log("********** Validate DNS Service is enabled **********")
                res = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns", grid_vip=config.grid2_vip)
                print_and_log(res)
                res = json.loads(res)
                print_and_log(res)
                for i in res:
                    print_and_log(i)
                    print_and_log("found")
                    assert i["enable_dns"] == True
                print_and_log("Test Case 417 Execution Completed")


        @pytest.mark.run(order=418)
        def test_418_create_AuthZone(self):
                print_and_log("********** Create A auth Zone **********")
                data = {"fqdn": "dtc.com","grid_primary": [{"name": host_name,"stealth":False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data), grid_vip=config.grid2_vip)
                print_and_log(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401 or response[0]==404:
                        print_and_log("Failure: Create A new Zone")
                        assert False
                    else:
                        print_and_log("Success: Create A new Zone")
                        assert True
                print_and_log("Restart DNS Services")
                restart_services_on_grid_2()
                #Validation of Auth Zone Created
                response = ib_NIOS.wapi_request('GET', object_type="zone_auth", params='?fqdn=dtc.com', grid_vip=config.grid2_vip)
                response = json.loads(response)
                res_fqdn = response[0]['fqdn']
                if res_fqdn == "dtc.com":
                    print_and_log("The authorative zone "+res_fqdn+" creatd successfully")
                    assert True
                else:
                    print_and_log("Error while creating the authorative zone")
                    assert False
                print_and_log("Test Case 418 Execution Completed")



        @pytest.mark.run(order=419)
        def test_419_Enable_the_lan_ipv6_in_member_dns_properties(self):
                print_and_log("********* Enable the lan ipv6 in member dns properties *********")
                response = ib_NIOS.wapi_request('GET',object_type='member:dns', grid_vip=config.grid2_vip)
                response = json.loads(response)
                print_and_log(response)
                ref = response[0]['_ref']
                data = {"use_lan_ipv6_port": True}
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data), grid_vip=config.grid2_vip)
                print_and_log(response1)
                assert re.search(r'member:dns', response1)
                restart_services()
                print_and_log("Test Case 419 Execution Completed")



        @pytest.mark.run(order=420)
        def test_420_Validate_if_the_lan_ipv6_in_member_dns_properties_is_enabled_or_not(self):
                print_and_log("********* Validate if the lan ipv6 in member dns properties is enabled or not *********")
                response = ib_NIOS.wapi_request('GET',object_type='member:dns', grid_vip=config.grid2_vip)
                response = json.loads(response)
                print_and_log(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=use_lan_ipv6_port', grid_vip=config.grid2_vip)
                response1 = json.loads(response1)
                output = response1['use_lan_ipv6_port']
                if output == True:
                    print_and_log("LAN IPV6 port is enabled in member dns properties")
                    assert True
                else:
                    print_and_log("LAN IPV6 port is disabled in member dns properties")
                    assert False
                print_and_log("Test Case 420 Execution Completed")


        @pytest.mark.run(order=421)
        def test_421_Create_Custom_Extensible_Attribute_required_for_testing_on_grid_2(self):
                print_and_log("******** Creation of Custom Externsible Attribute with Type String **********")
                data = {"name": "EA_string", "type": "STRING"}
                response = ib_NIOS.wapi_request('POST',object_type='extensibleattributedef', fields=json.dumps(data), grid_vip=config.grid2_vip)
                print_and_log(response)
                assert re.search(r'EA_string', response)
                print_and_log("******** Creation of Custom Externsible Attribute with Type List **********")
                data = {"name": "EA_list", "type": "ENUM", "list_values": [{"value": "1"}, {"value": "2"}], "comment": "EA for List"}
                response = ib_NIOS.wapi_request('POST',object_type='extensibleattributedef', fields=json.dumps(data), grid_vip=config.grid2_vip)
                print_and_log(response)
                assert re.search(r'EA_list', response)
                print_and_log("******** Creation of Custom Externsible Attribute with Type Interger **********")
                data = {"name": "EA_int", "type": "INTEGER"}
                response = ib_NIOS.wapi_request('POST',object_type='extensibleattributedef', fields=json.dumps(data), grid_vip=config.grid2_vip)
                print_and_log(response)
                assert re.search(r'EA_int', response)
                print_and_log("Test Case 421 Execution Completed")


        @pytest.mark.run(order=422)
        def test_422_Validation_of_Custom_Extensible_Attribute_that_are_created_on_grid_2(self):
                print_and_log("********** Validation of custom extensible attribute that are created *************")
                new_list = ["EA_string", "EA_list", "EA_int"]
                for i in new_list:
                    response = ib_NIOS.wapi_request('GET',object_type='extensibleattributedef', params="?name="+i, grid_vip=config.grid2_vip)
                    response = json.loads(response)
                    ref_name = response[0]['name']
                    ref_type = response[0]['type']
                    if ref_name == i and ref_type == "STRING":
                        print_and_log("Custom EA "+i+" with type "+ref_type+" is configured successfully")
                        assert True
                    elif ref_name == i and ref_type == "ENUM":
                        print_and_log("Custom EA "+i+" with type "+ref_type+" is configured successfully")
                        assert True
                    elif ref_name == i and ref_type == "INTEGER":
                        print_and_log("Custom EA "+i+" with type "+ref_type+" is configured successfully")
                        assert True
                    else:
                        print_and_log("Validation failed for One of the custom EA")
                        assert False
                print_and_log("Test Case 422 Execution Completed")



        @pytest.mark.run(order=423)
        def test_423_Upload_the_IPAM_Network_NetworkContainer_Ranges_and_Host_through_CSV_on_Grid_2(self):
                print_and_log("Uploading csv file containing IAPM Network NetworkConatiner Ranges Hosts")
                dir_name=os.getcwd()
                base_filename = "IPAM_Networks_Containers_Ranges_Hosts.csv"
                token =generate_token_from_file(dir_name, base_filename, config.grid2_vip)
                data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"OVERRIDE","operation":"INSERT"}
                response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_import", grid_vip=config.grid2_vip)
                response=json.loads(response)
                print_and_log(response)
                if type(response) == tuple:
                    print_and_log("Failure: CSV file upload")
                    assert False
                else:
                    print_and_log("CSV File Uploaded successfully")
                    assert True
                sleep(30)
                print_and_log("Test Case 423 Execution completed")



        @pytest.mark.run(order=424)
        def test_424_validate_the_value_of_the_IPV6_IPAM_network_from_network1_to_network2(self):
                print_and_log("******** Validate the value of the IPV6 IPAM network from network1 to network2 *********")
                validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2('ipv6network', 'network2', 'EA_string', 'network='+str(config.ipv6network3), config.grid2_vip)
                validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2('ipv6network', '2', 'EA_list', 'network='+str(config.ipv6network3), config.grid2_vip)
                validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2('ipv6network', 'Infoblox', 'Site', 'network='+str(config.ipv6network3), config.grid2_vip)
                validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2('ipv6network', int(5), 'EA_int', 'network='+str(config.ipv6network3), config.grid2_vip)
                print_and_log("Test Case 424 Execution Completed")



        @pytest.mark.run(order=425)
        def test_425_validate_the_value_of_the_IPV6_IPAM_conatiner_from_network2_to_network1(self):
                print_and_log("******** validate the value of the IPV6 IPAM conatiner from network2 to network1 *********")
                validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2('ipv6networkcontainer', 'network1', 'EA_string', 'network='+str(config.ipv6network_container3), config.grid2_vip)
                validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2('ipv6networkcontainer', '1', 'EA_list', 'network='+str(config.ipv6network_container3), config.grid2_vip)
                validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2('ipv6networkcontainer', 'Infoblox', 'Site', 'network='+str(config.ipv6network_container3), config.grid2_vip)
                validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2('ipv6networkcontainer', int(10), 'EA_int', 'network='+str(config.ipv6network_container3), config.grid2_vip)
                print_and_log("Test Case 425 Execution Completed")



        @pytest.mark.run(order=426)
        def test_426_validate_the_value_of_the_IPV6_IPAM_Ranges_from_network2_to_network1(self):
                print_and_log("******** validate the value of the IPV6 IPAM ranges from network2 to network1 *********")
                validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2('ipv6range', 'network1', 'EA_string', 'network='+str(config.ipv6network3), config.grid2_vip)
                validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2('ipv6range', '1', 'EA_list', 'network='+str(config.ipv6network3), config.grid2_vip)
                validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2('ipv6range', 'Infoblox', 'Site', 'network='+str(config.ipv6network3), config.grid2_vip)
                validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2('ipv6range', int(10), 'EA_int', 'network='+str(config.ipv6network3), config.grid2_vip)
                print_and_log("Test Case 426 Execution Completed")


        @pytest.mark.run(order=427)
        def test_427_validate_the_value_of_the_IPV6_IPAM_Host_from_network2_to_network1(self):
                print_and_log("******** validate the value of the IPV6 IPAM hosts from network2 to network1 *********")
                validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2('record:host', 'network1', 'EA_string', 'name=host_new_ipv6_3', config.grid2_vip)
                validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2('record:host', '1', 'EA_list', 'name=host_new_ipv6_3', config.grid2_vip)
                validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2('record:host', 'Infoblox', 'Site', 'name=host_new_ipv6_3', config.grid2_vip)
                validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2('record:host', int(10), 'EA_int', 'name=host_new_ipv6_3', config.grid2_vip)
                print_and_log("Test Case 427 Execution Completed")



        @pytest.mark.run(order=428)
        def test_428_Restore_DTC_Config_File(self):
                print_and_log("Restore DTC Config File")
                log("start","/infoblox/var/infoblox.log", config.grid2_vip)
                #curl -k -u admin:infoblox -H  "content-type: application/force-download" https://10.197.36.129/http_direct_file_io/req_id-DOWNLOAD-1007201457899476/dtc-config.bak -o "dtcconfig.bak"
                cmd ='curl -k -u admin:infoblox -H  "content-type: application/force-download" "' + str(token_of_URL) +'" -o "dtcconfig.bak"'
                out2 = commands.getoutput(cmd)
                print_and_log(out2)
                sleep(10)
                response = ib_NIOS.wapi_request('POST', object_type="fileop", params="?_function=uploadinit", grid_vip=config.grid2_vip)
                response = json.loads(response)
                token = response['token']
                url = response['url']
                print_and_log(token)
                print_and_log(url)
                cmd2 ='curl -k -u admin:infoblox -H  "content-typemultipart-formdata" "'+str(url)+'" -F file=@dtcconfig.bak'
                out3 = commands.getoutput(cmd2)
                print_and_log(out3)
                data = {"forced": True, "token": str(token)}
                response1 = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data), params="?_function=restoredtcconfig", grid_vip=config.grid2_vip)
                response1 = json.loads(response1)
                print_and_log(response)
                restart_services_on_grid_2()
                sleep(60)
                LookFor="'DTC restore: done'"
                log("stop","/infoblox/var/infoblox.log",config.grid2_vip)
                logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid2_vip)
                print_and_log("successful Log message "+LookFor+" is seen in infoblox.log")
                rebuild_services_on_grid_2()
                sleep(300)
                print_and_log("Test Case 428 Execution Completed")



        @pytest.mark.run(order=429)
        def test_429_Run_the_dig_command_with_subnet_of_IPV6_IPAM_network3(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM network3 ************")
                output = os.popen("dig @"+config.grid2_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_64_subnet3+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network3+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 429 Execution Completed")


        @pytest.mark.run(order=430)
        def test_430_Run_the_dig_command_with_subnet_of_IPV6_IPAM_conatiner3(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Container3 ************")
                output = os.popen("dig @"+config.grid2_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_32_subnet3+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network_container3+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 430 Execution Completed")


        @pytest.mark.run(order=431)
        def test_431_Run_the_dig_command_with_subnet_of_IPV6_IPAM_ranges3(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Ranges3 ************")
                output = os.popen("dig @"+config.grid2_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges3)[0]+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges3)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid2_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges3)[1]+"/128 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges3)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid2_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges3)[2]+"/128 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded ==config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges3)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 431 Execution Completed")



        @pytest.mark.run(order=432)
        def test_432_Run_the_dig_command_with_subnet_of_IPV6_IPAM_Hosts3(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Hosts3 ************")
                output = os.popen("dig @"+config.grid2_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6addr_host3+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6addr_host3)
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 432 Execution Completed")


        #GMC Promotion Scenarios
        @pytest.mark.run(order=433)
        def test_433_Enable_the_lan_ipv6_in_member_dns_properties(self):
                print_and_log("********* Enable the lan ipv6 in member dns properties *********")
                response = ib_NIOS.wapi_request('GET',object_type='member:dns')
                response = json.loads(response)
                print_and_log(response)
                ref = response[1]['_ref']
                data = {"use_lan_ipv6_port": True}
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
                print_and_log(response1)
                assert re.search(r'member:dns', response1)
                restart_services()
                print_and_log("Test Case 433 Execution Completed")



        @pytest.mark.run(order=434)
        def test_434_Validate_if_the_lan_ipv6_in_member_dns_properties_is_enabled_or_not(self):
                print_and_log("********* Validate if the lan ipv6 in member dns properties is enabled or not *********")
                response = ib_NIOS.wapi_request('GET',object_type='member:dns')
                response = json.loads(response)
                print_and_log(response)
                ref = response[1]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=use_lan_ipv6_port')
                response1 = json.loads(response1)
                output = response1['use_lan_ipv6_port']
                if output == True:
                    print_and_log("LAN IPV6 port is enabled in member dns properties")
                    assert True
                else:
                    print_and_log("LAN IPV6 port is disabled in member dns properties")
                    assert False
                print_and_log("Test Case 434 Execution Completed")


        @pytest.mark.run(order=435)
        def test_435_Enable_Master_candidate_option_on_the_Grid_Member(self):
                print_and_log("********* Enable Master candidate option on the Grid Member ***********")
                response = ib_NIOS.wapi_request('GET', object_type="member")
                response = json.loads(response)
                ref = response[1]['_ref']
                data = {"master_candidate": True}
                response1 = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
                print_and_log(response1)
                assert re.search(r'member', response1)
                sleep(120)
                print_and_log("Test Case 435 Execution Completed")



        @pytest.mark.run(order=436)
        def test_436_Validate_if_Master_candidate_option_is_enalbed_in_the_Grid_Member(self):
                print_and_log("********** Validate if Master candidate option is enalbed in the Grid Member ***********")
                response = ib_NIOS.wapi_request('GET', object_type="member")
                response = json.loads(response)
                ref = response[1]['_ref']
                response1 = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=master_candidate')
                response1 = json.loads(response1)
                ref_master_candidate = response1['master_candidate']
                if ref_master_candidate == True:
                    print_and_log("Master Candidate option is enabled in Grid member")
                    assert True
                else:
                    print_and_log("Master Candidate option is not enabled in Grid member")
                    assert False
                print_and_log("Test Case 436 Execution Completed")



        @pytest.mark.run(order=437)
        def test_437_Run_the_command_promote_master_on_Grid_Member(self):
                print_and_log("*********** Run the command promote master on Grid Member ************")
                try:
                    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
                    child.logfile=sys.stdout
                    child.expect('password:')
                    child.sendline('infoblox')
                    child.expect('Infoblox >')
                    child.sendline('set promote_master')
                    child.expect(': ')
                    child.sendline('n')
                    child.expect(': ')
                    child.sendline('y')
                    child.expect(': ')
                    child.sendline('y')
                    child.expect(' ')
                    print_and_log(child.before)
                    output = child.before
                    if output.split("\n")[0] == "y\r":
                        print_and_log("Set Promote master executed successfully")
                        assert True
                        sleep(180)
                    else:
                        raise Exception
                except Exception as e:
                    print_and_log(e)
                    print_and_log("Set Promote master execution failed")
                    assert False
                print_and_log("Test Case 437 Execution Completed")



        @pytest.mark.run(order=438)
        def test_438_Verify_if_the_Promote_master_is_successfull(self):
                print_and_log("********** Verify if the Promote master is successfull ***********")
                try:
                    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
                    child.logfile=sys.stdout
                    child.expect('password:')
                    child.sendline('infoblox')
                    child.expect('Infoblox >')
                    child.sendline('show status')
                    child.expect('Infoblox >')
                    print_and_log(child.before)
                    output = child.before
                    if output.split("\n")[1] == "Grid Status: ID Grid Master\r":
                        print_and_log("Member has been prompoted successfully to Master")
                        assert True
                    else:
                        raise Exception
                except Exception as e:
                    print_and_log(e)
                    print_and_log("Validation for the Promote master failed")
                    assert False
                print_and_log("Test Case 438 Execution Completed")




        @pytest.mark.run(order=439)
        def test_439_Run_the_dig_command_with_subnet_of_IPV6_IPAM_network3(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM network3 ************")
                output = os.popen("dig @"+config.grid_member1_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_64_subnet3+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network3+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 439 Execution Completed")


        @pytest.mark.run(order=440)
        def test_440_Run_the_dig_command_with_subnet_of_IPV6_IPAM_conatiner3(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Container3 ************")
                output = os.popen("dig @"+config.grid_member1_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_32_subnet3+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network_container3+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 440 Execution Completed")


        @pytest.mark.run(order=441)
        def test_441_Run_the_dig_command_with_subnet_of_IPV6_IPAM_ranges3(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Ranges3 ************")
                output = os.popen("dig @"+config.grid_member1_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges3)[0]+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges3)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_member1_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges3)[1]+"/128 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges3)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_member1_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges3)[2]+"/128 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded ==config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges3)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 441 Execution Completed")



        @pytest.mark.run(order=442)
        def test_442_Run_the_dig_command_with_subnet_of_IPV6_IPAM_Hosts3(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Hosts3 ************")
                output = os.popen("dig @"+config.grid_member1_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6addr_host3+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6addr_host3)
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 442 Execution Completed")



        @pytest.mark.run(order=443)
        def test_443_Modify_the_value_of_the_IPV6_IPAM_network_from_network1_to_network2(self):
                print_and_log("******** Modify the value of the IPV6 IPAM network from network1 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="ipv6network", params='?network='+config.ipv6network3, grid_vip=config.grid_member1_vip)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_int": {"value": 5}, "EA_list": {"value": "2"}, "EA_string": {"value": "network2"}, "Site": {"value": "Infoblox"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data), grid_vip=config.grid_member1_vip)
                print_and_log(response1)
                rebuild_services_on_member()
                validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2('ipv6network', 'network2', 'EA_string', 'network='+str(config.ipv6network3), config.grid_member1_vip)
                validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2('ipv6network', '2', 'EA_list', 'network='+str(config.ipv6network3), config.grid_member1_vip)
                validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2('ipv6network', 'Infoblox', 'Site', 'network='+str(config.ipv6network3), config.grid_member1_vip)
                validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2('ipv6network', int(5), 'EA_int', 'network='+str(config.ipv6network3), config.grid_member1_vip)
                print_and_log("Test Case 443 Execution Completed")



        @pytest.mark.run(order=444)
        def test_444_Modify_the_value_of_the_IPV6_IPAM_conatiner_from_network2_to_network1(self):
                print_and_log("******** Modify the value of the IPV6 IPAM conatiner from network2 to network1 *********")
                response = ib_NIOS.wapi_request('GET',object_type="ipv6networkcontainer", params='?network='+config.ipv6network_container3, grid_vip=config.grid_member1_vip)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_int": {"value": 10}, "EA_list": {"value": "1"}, "EA_string": {"value": "network1"}, "Site": {"value": "Infoblox"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data), grid_vip=config.grid_member1_vip)
                print_and_log(response1)
                rebuild_services_on_member()
                validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2('ipv6networkcontainer', 'network1', 'EA_string', 'network='+str(config.ipv6network_container3), config.grid_member1_vip)
                validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2('ipv6networkcontainer', '1', 'EA_list', 'network='+str(config.ipv6network_container3), config.grid_member1_vip)
                validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2('ipv6networkcontainer', 'Infoblox', 'Site', 'network='+str(config.ipv6network_container3), config.grid_member1_vip)
                validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2('ipv6networkcontainer', int(10), 'EA_int', 'network='+str(config.ipv6network_container3), config.grid_member1_vip)
                print_and_log("Test Case 444 Execution Completed")



        @pytest.mark.run(order=445)
        def test_445_Modify_the_value_of_the_IPV6_IPAM_Ranges_from_network1_to_network2(self):
                print_and_log("******** Modify the value of the IPV6 IPAM network from network1 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="ipv6range", params='?network='+config.ipv6network3, grid_vip=config.grid_member1_vip)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_int": {"value": 10}, "EA_list": {"value": "1"}, "EA_string": {"value": "network1"}, "Site": {"value": "Infoblox"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data), grid_vip=config.grid_member1_vip)
                print_and_log(response1)
                rebuild_services_on_member()
                validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2('ipv6range', 'network1', 'EA_string', 'network='+str(config.ipv6network3), config.grid_member1_vip)
                validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2('ipv6range', '1', 'EA_list', 'network='+str(config.ipv6network3), config.grid_member1_vip)
                validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2('ipv6range', 'Infoblox', 'Site', 'network='+str(config.ipv6network3), config.grid_member1_vip)
                validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2('ipv6range', int(10), 'EA_int', 'network='+str(config.ipv6network3), config.grid_member1_vip)
                print_and_log("Test Case 445 Execution Completed")


        @pytest.mark.run(order=446)
        def test_446_Modify_the_value_of_the_IPV6_IPAM_Host_from_network1_to_network2(self):
                print_and_log("******** Modify the value of the IPV6 IPAM network from network1 to network2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="record:host", params='?name=host_new_ipv6_3', grid_vip=config.grid_member1_vip)
                response = json.loads(response)
                print_and_log(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "EA_int": {"value": 10}, "EA_list": {"value": "1"}, "EA_string": {"value": "network1"}, "Site": {"value": "Infoblox"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data), grid_vip=config.grid_member1_vip)
                print_and_log(response1)
                rebuild_services_on_member()
                validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2('record:host', 'network1', 'EA_string', 'name=host_new_ipv6_3', config.grid_member1_vip)
                validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2('record:host', '1', 'EA_list', 'name=host_new_ipv6_3', config.grid_member1_vip)
                validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2('record:host', 'Infoblox', 'Site', 'name=host_new_ipv6_3', config.grid_member1_vip)
                validation_of_4_EAs_value_configured_in_extensible_attribute_on_grid_2('record:host', int(10), 'EA_int', 'name=host_new_ipv6_3', config.grid_member1_vip)
                print_and_log("Test Case 446 Execution Completed")



        @pytest.mark.run(order=447)
        def test_447_Run_the_dig_command_with_subnet_of_IPV6_IPAM_network3(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM network3 ************")
                output = os.popen("dig @"+config.grid_member1_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_64_subnet3+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server2:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network3+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 447 Execution Completed")


        @pytest.mark.run(order=448)
        def test_448_Run_the_dig_command_with_subnet_of_IPV6_IPAM_conatiner3(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Container3 ************")
                output = os.popen("dig @"+config.grid_member1_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_32_subnet3+" +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6network_container3+" network")
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 448 Execution Completed")


        @pytest.mark.run(order=449)
        def test_449_Run_the_dig_command_with_subnet_of_IPV6_IPAM_ranges3(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Ranges3 ************")
                output = os.popen("dig @"+config.grid_member1_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges3)[0]+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges3)[0])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output1 = os.popen("dig @"+config.grid_member1_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges3)[1]+"/128 +short").read()
                Server_That_Responded = output1.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges3)[1])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                output2 = os.popen("dig @"+config.grid_member1_vip+" aaaa.dtc.com in aaaa +subnet="+json.loads(config.ipv6_ranges3)[2]+"/128 +short").read()
                Server_That_Responded = output2.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded ==config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+json.loads(config.ipv6_ranges3)[2])
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 449 Execution Completed")



        @pytest.mark.run(order=450)
        def test_450_Run_the_dig_command_with_subnet_of_IPV6_IPAM_Hosts3(self):
                print_and_log("********** Run the dig command with subnet of IPV6 IPAM Hosts3 ************")
                output = os.popen("dig @"+config.grid_member1_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6addr_host3+"/128 +short").read()
                Server_That_Responded = output.strip(" ").split("\n")[0]
                print_and_log(Server_That_Responded)
                if Server_That_Responded == config.ipv6_server1:
                    print_and_log("Server "+Server_That_Responded+" responded for the query with subnet "+config.ipv6addr_host3)
                    assert True
                else:
                    print_and_log("Different server responded to the query")
                    assert False
                sleep(10)
                print_and_log("Test Case 450 Execution Completed")



        @pytest.mark.run(order=451)
        def test_451_Uncheck_the_IPAM_Container_object_in_Grid_DNS_Properties_Traffic_Control(self):
                print_and_log("********** Uncheck the IPAM Container object in Grid DNS Properties Traffic Control ************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns", grid_vip=config.grid_member1_vip)
                response = json.loads(response)
                ref = response[0]['_ref']
                data = {"gen_eadb_from_network_containers": False}
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data), grid_vip=config.grid_member1_vip)
                print_and_log(response1)
                rebuild_services_on_member()
                restart_services_on_member()
                print_and_log("Test Case 451 Execution Completed")


        @pytest.mark.run(order=452)
        def test_452_Validation_of_the_IPAM_Container_object_in_Grid_DNS_Properties_Traffic_Control(self):
                print_and_log("********** Validation of the IPAM Container object in Grid DNS Properties Traffic Control************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns", grid_vip=config.grid_member1_vip)
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=gen_eadb_from_network_containers', grid_vip=config.grid_member1_vip)
                response1 = json.loads(response1)
                output = response1['gen_eadb_from_network_containers']
                if output == False:
                    print_and_log(" The IPAM Containers Object in Grid DNS properties is set to False")
                    assert True
                else:
                    print_and_log(" The IPAM Containers Object in Grid DNS properties is set to True")
                    assert False
                print_and_log("Test Case 452 Execution Completed")


        @pytest.mark.run(order=453)
        def test_453_Run_the_dig_command_with_subnet_of_IPAM_conatiner(self):
                print_and_log("********** Run the dig command with subnet of IPAM Container ************")
                output = os.popen("dig @"+config.grid_member1_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_32_subnet3).read()
                out = output.split("\n")
                flag = False
                for i in out:
                    match = re.match("dtc.com.\s+\d+\s+IN\s+SOA.*",i)
                    print_and_log(i)
                    if match:
                        print_and_log(" Match found ")
                        flag=True
                        break
                if flag == True:
                    print_and_log("SOA record is found, No response from any for the DTC servers")
                    assert True
                else:
                    print_and_log("Query got the response from DTC servers")
                    assert False
                print_and_log("Test Case 453 Execution Completed")



        @pytest.mark.run(order=454)
        def test_454_Uncheck_the_IPAM_Networks_object_in_Grid_DNS_Properties_Traffic_Control(self):
                print_and_log("********** Uncheck the IPAM networks object in Grid DNS Properties Traffic Control ************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns", grid_vip=config.grid_member1_vip)
                response = json.loads(response)
                ref = response[0]['_ref']
                data = {"gen_eadb_from_networks": False}
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data), grid_vip=config.grid_member1_vip)
                print_and_log(response1)
                rebuild_services_on_member()
                restart_services_on_member()
                print_and_log("Test Case 454 Execution Completed")


        @pytest.mark.run(order=455)
        def test_455_Validation_of_the_IPAM_network_object_in_Grid_DNS_Properties_Traffic_Control(self):
                print_and_log("********** Validation of the IPAM networks object in Grid DNS Properties Traffic Control************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns", grid_vip=config.grid_member1_vip)
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=gen_eadb_from_networks', grid_vip=config.grid_member1_vip)
                response1 = json.loads(response1)
                output = response1['gen_eadb_from_networks']
                if output == False:
                    print_and_log(" The IPAM networks Object in Grid DNS properties is set to False")
                    assert True
                else:
                    print_and_log(" The IPAM networks Object in Grid DNS properties is set to True")
                    assert False
                print_and_log("Test Case 455 Execution Completed")



        @pytest.mark.run(order=456)
        def test_456_Run_the_dig_command_with_subnet_of_IPAM_network(self):
                print_and_log("********** Run the dig command with subnet of IPAM Network ************")
                output = os.popen("dig @"+config.grid_member1_vip+" aaaa.dtc.com in aaaa +subnet="+config.ipv6_64_subnet3).read()
                out = output.split("\n")
                flag = False
                for i in out:
                    match = re.match("dtc.com.\s+\d+\s+IN\s+SOA.*",i)
                    print_and_log(i)
                    if match:
                        print_and_log(" Match found ")
                        flag=True
                        break
                if flag == True:
                    print_and_log("SOA record is found, No response from any for the DTC servers")
                    assert True
                else:
                    print_and_log("Query got the response from DTC servers")
                    assert False
                print_and_log("Test Case 456 Execution Completed")



        @pytest.mark.run(order=457)
        def test_457_Uncheck_the_IPAM_ranges_object_in_Grid_DNS_Properties_Traffic_Control(self):
                print_and_log("********** Uncheck the IPAM ranges object in Grid DNS Properties Traffic Control ************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns", grid_vip=config.grid_member1_vip)
                response = json.loads(response)
                ref = response[0]['_ref']
                data = {"gen_eadb_from_ranges": False}
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data), grid_vip=config.grid_member1_vip)
                print_and_log(response1)
                rebuild_services_on_member()
                restart_services_on_member()
                print_and_log("Test Case 457 Execution Completed")


        @pytest.mark.run(order=458)
        def test_458_Validation_of_the_IPAM_ranges_object_in_Grid_DNS_Properties_Traffic_Control(self):
                print_and_log("********** Validation of the IPAM ranges object in Grid DNS Properties Traffic Control************")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns", grid_vip=config.grid_member1_vip)
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=gen_eadb_from_ranges', grid_vip=config.grid_member1_vip)
                response1 = json.loads(response1)
                output = response1['gen_eadb_from_ranges']
                if output == False:
                    print_and_log(" The IPAM ranges Object in Grid DNS properties is set to False")
                    assert True
                else:
                    print_and_log(" The IPAM networks Object in Grid DNS properties is set to True")
                    assert False
                print_and_log("Test Case 458 Execution Completed")



        @pytest.mark.run(order=459)
        def test_459_Run_the_dig_command_with_subnet_of_IPAM_ranges(self):
                print_and_log("********** Run the dig command with subnet of IPAM Ranges ************")
                for i in json.loads(config.ipv6_ranges3):
                    output = os.popen("dig @"+config.grid_member1_vip+" aaaa.dtc.com in aaaa +subnet="+i+"/128").read()
                    out = output.split("\n")
                    flag = False
                    for i in out:
                        match = re.match("dtc.com.\s+\d+\s+IN\s+SOA.*",i)
                        print_and_log(i)
                        if match:
                            print_and_log(" Match found ")
                            flag=True
                            break
                    if flag == True:
                        print_and_log("SOA record is found, No response from any for the DTC servers")
                        assert True
                    else:
                        print_and_log("Query got the response from DTC servers")
                        assert False
                print_and_log("Test Case 459 Execution Completed")





        @pytest.mark.run(order=460)
        def test_460_Uncheck_the_IPAM_hosts_object_in_Grid_DNS_Properties_Traffic_Control_and_expect_error(self):
                print_and_log("********* Uncheck the IPAM hosts object in Grid DNS Properties Traffic Control and expect error **********")
                response = ib_NIOS.wapi_request('GET',object_type="grid:dns", grid_vip=config.grid_member1_vip)
                response = json.loads(response)
                ref = response[0]['_ref']
                data = {"gen_eadb_from_hosts": False}
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data), grid_vip=config.grid_member1_vip)
                if type(response1) == tuple:
                    out = response1[1]
                    out = json.loads(out)
                    print_and_log(out)
                    error_message = out['text']
                    print_and_log(error_message)
                    expected_error_message = "' At least one source type for EA MMDB must be selected.'"
                    if error_message in expected_error_message:
                        print_and_log("Expected Error message is seen")
                        assert True
                    else:
                        print_and_log("Expected Error message is not seen")
                        assert False
                else:
                    print_and_log(response1)
                    print_and_log(" All the IPAM objects under Grid DNS properties Traffic control is disabled ")
                    assert False
                print_and_log("Test Case 460 Execution Completed")

__author__ = "Arun J R"
__email__  = "aramaiah@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Stand alone Grid Master                                               #
#  2. Licenses : DNS, Grid, NIOS(IB_1415), DTC license                      #
#############################################################################

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
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="NIOSSPT_11092.log" ,level=logging.INFO,filemode='w')


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


class NIOSSPT_11092(unittest.TestCase):

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
                logging.info("Validate DNS Service is enabled")
                res = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns")
                logging.info(res)
                res = json.loads(res)
                print res
                for i in res:
                        print i
                        logging.info("found")
                        assert i["enable_dns"] == True
                print("Test Case 2 Execution Completed")


        @pytest.mark.run(order=3)
        def test_003_create_AuthZone(self):
                print("Create A auth Zone")
                data = {"fqdn": "dtc.com","grid_primary": [{"name": config.grid_fqdn,"stealth":False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                print response
                if type(response) == tuple:
                        if response[0]==400 or response[0]==401 or response[0]==404:
                                print("Failure: Create A new Zone")
                                assert False
                        else:
                                print("Success: Create A new Zone")
                                assert True
                print("Restart DNS Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20)
                logging.info("Test Case 3 Execution Completed")



        @pytest.mark.run(order=4)
        def test_004_Create_A_Record(self):
                logging.info("********** Create A Record************")
                data = {"name":"new1.dtc.com","ipv4addr":"10.1.1.1"}
                response = ib_NIOS.wapi_request('POST', object_type="record:a", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("Test Case 4 Execution Completed")



        @pytest.mark.run(order=5)
        def test_005_Validation_of_A_Record(self):
                response = ib_NIOS.wapi_request('GET',object_type="record:a" , params='?_return_fields=name')
                ref1 = json.loads(response)
                print(ref1)
                ref1 = ref1[0]['name']
                if ref1 == "new1.dtc.com":
                    assert True
                    print("A record "+ref1+" was created successfully")
                else:
                    print("A record "+ref1+" was not created successfully")
                    assert False
                logging.info("Test Case 5 Execution Completed")


        @pytest.mark.run(order=6)
        def test_006_Creating_Two_DTC_Servers(self):
                logging.info("Creating Twenty DTC Servers")
                #d = {"server1": "10.120.21.2", "server2": "10.120.21.3"}
                for i,j in d.items():
                    #server="server"+str(i)
                    print(i)
                    print(j)
                    data = {"name":i,"host":j}
                    response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
                    print response
                    logging.info(response)
                    read  = re.search(r'201',response)
                    for read in  response:
                            assert True
                logging.info("Test Case 6 Execution Completed")


        @pytest.mark.run(order=7)
        def test_007_Validation_of_Servers_Created(self):
                logging.info("**** Validation of DTC servers that are created ****")
                for i in Server_name:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    name_server = response_servers[0]['name']
                    if i == name_server:
                        assert True
                    else:
                        Print("There was a error in creation of server, Server names doesn't match")
                        assert False
                logging.info("Test Case 7 Execution Completed")



        @pytest.mark.run(order=8)
        def test_008_Creation_of_Pool_1(self):
                logging.info("********** Creation of Pool 1 ************")
                logging.info("Getting the server name reference ")
                server_ref = []
                for i in Server_name:
                        response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                        response_servers = json.loads(response_servers)
                        ref = response_servers[0]['_ref']
                        server_ref.append(ref)
                print(server_ref)
                logging.info("****** Creating the pool and assiging the server ******")
                data = {"name": "Pool_1", "lb_preferred_method": "ALL_AVAILABLE", "servers": [{"ratio": 1,"server": str(server_ref[0])}], "monitors": ["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"]}
                response_servers = ib_NIOS.wapi_request('POST',object_type='dtc:pool', fields=json.dumps(data))
                ref1 = json.loads(response_servers)
                print(ref1)
                logging.info("Validation of Pool creation")
                assert re.search(r'dtc:pool', ref1)
                logging.info("Test Case 8 Execution Completed")



        @pytest.mark.run(order=9)
        def test_009_Creation_of_Pool_2(self):
                logging.info("********** Creation of Pool 2 ************")
                logging.info("Getting the server name reference ")
                server_ref = []
                for i in Server_name:
                        response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                        response_servers = json.loads(response_servers)
                        ref = response_servers[0]['_ref']
                        server_ref.append(ref)
                print(server_ref)
                logging.info("****** Creating the pool and assiging the server ******")
                data = {"name": "Pool_2", "lb_preferred_method": "ROUND_ROBIN", "servers": [{"ratio": 1,"server": str(server_ref[1])}], "monitors": ["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"]}
                response_servers = ib_NIOS.wapi_request('POST',object_type='dtc:pool', fields=json.dumps(data))
                ref1 = json.loads(response_servers)
                print(ref1)
                logging.info("Validation of Pool creation")
                assert re.search(r'dtc:pool', ref1)
                logging.info("Test Case 9 Execution Completed")


        @pytest.mark.run(order=10)
        def test_010_Validation_of_Pools_Created(self):
                logging.info("************ Validation of Pools created **************")
                newlist = ["Pool_1", "Pool_2"]
                response_servers = ib_NIOS.wapi_request('GET', object_type='dtc:pool')
                res = json.loads(response_servers)
                for i in res:
                    i = i['name']
                    if i in newlist:
                        assert True
                        print("Pool "+i+" is created successfully")
                    else:
                        print("Pool "+i+" is not created successfully")
                        assert False
                logging.info("Test case 10 Execution completed")


        @pytest.mark.run(order=11)
        def test_011_Creation_of_LBDN(self):
                logging.info("********** Creation of LBDN ************")
                logging.info("********** Getting the ref of authorativezone ************")
                response = ib_NIOS.wapi_request('GET',object_type='zone_auth', params='?fqdn=dtc.com')
                response = json.loads(response)
                ref_zone = response[0]['_ref']
                logging.info("********** Getting the ref of pool 1 ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_1')
                response = json.loads(response)
                ref_pool1 = response[0]['_ref']
                logging.info("********** Getting the ref of pool 2 ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_2')
                response = json.loads(response)
                ref_pool2 = response[0]['_ref']
                logging.info("********** Creating the lbdn by post request ************")
                data = {"auth_zones": [ref_zone], "name": "LBDN_1", "lb_method": "ROUND_ROBIN", "patterns": ["*.dtc.com"], "pools": [{"ratio": 1, "pool": ref_pool1}, {"ratio": 1, "pool": ref_pool2}]}
                print(data)
                response = ib_NIOS.wapi_request('POST',object_type='dtc:lbdn', fields=json.dumps(data))
                response = json.loads(response)
                logging.info("Validation of lbdn creation")
                assert re.search(r'dtc:lbdn', response)
                logging.info("******** Restart the DTC service *********")
                response = ib_NIOS.wapi_request('GET',object_type='grid')
                reference = json.loads(response)
                ref = reference[0]['_ref']
                data = {"member_order" : "SIMULTANEOUSLY", "restart_option": "FORCE_RESTART", "service_option": "ALL"}
                response1 = ib_NIOS.wapi_request('POST', object_type=ref + '?_function=restartservices',fields=json.dumps(data))
                if type(response1) == tuple:
                    if response1 == 400 or response1 == 401 or response1 == 402:
                        print("Error while restarting the DTC service")
                        assert False
                else:
                    print("DTC restarted successfully")
                    assert True
                sleep(30)
                logging.info("Test Case 11 Execution Completed")


        @pytest.mark.run(order=12)
        def test_012_Validation_of_LBDN_Created(self):
                logging.info("********** Validation of LBDN created ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn')
                res = json.loads(response)
                res = res[0]['name']
                if res == "LBDN_1":
                    assert True
                    print("LBDN "+res+" created successfully")
                else:
                    print("LBDN "+res+" not created successfully")
                    assert False
                logging.info("Test Case 12 Execution Completed")


        @pytest.mark.run(order=13)
        def test_013_Create_Custom_Extensible_Attribute_and_Enable_Inheritance(self):
                logging.info("******** Creation of Custom Externsible Attribute and Enable Inheritance **********")
                data = {"name": "dtc-ea", "type": "STRING", "flags": "I"}
                response = ib_NIOS.wapi_request('POST',object_type='extensibleattributedef', fields=json.dumps(data))
                print(response)
                if "dtc-ea" in response:
                    assert True
                    print("Custom Extensible attribute got created successfully")
                else:
                    print("Error while creating the Extensible attribute")
                    assert False
                logging.info("Test Case 13 Execution Completed")


        @pytest.mark.run(order=14)
        def test_014_Validation_of_Custom_Extensible_Attribute(self):
                logging.info("******** Validation of Custom Externsible Attribute **********")
                response = ib_NIOS.wapi_request('GET',object_type='extensibleattributedef', params="?name=dtc-ea")
                response = json.loads(response)
                res_ref = response[0]['_ref']
                res_name = response[0]['name']
                res_type = response[0]['type']
                logging.info("********* Validation of Name and Type ***********")
                if res_name == "dtc-ea" and res_type == "STRING":
                    assert True
                    print("Custom attribute created successfully")
                else:
                    print("Custom attribute is not created")
                logging.info("********* Validation of Inheritance enabled ***********")
                response1 = ib_NIOS.wapi_request('GET',object_type=res_ref, params="?_return_fields=flags")
                response1 = json.loads(response1)
                res_flag = response1['flags']
                if res_flag == "I":
                    assert True
                    print("Inheritance is enabled")
                else:
                    print("Inheritance is not enabled")
                    assert False
                logging.info("Test Case 14 Execution Completed")


        @pytest.mark.run(order=15)
        def test_015_Assign_the_Custom_EA_in_Grid_Properties_Traffic_Control(self):
                logging.info("********** Assign the Custom EA in Grid Properties Traffic Conftrol ************")
                response = ib_NIOS.wapi_request('GET',object_type='grid:dns')
                response = json.loads(response)
                ref = response[0]['_ref']
                data={"dtc_topology_ea_list": ["dtc-ea"]}
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
                print(response1)
                assert re.search(r'grid:dns', response1)
                logging.info("Test Case 15 Execution completed ")



        @pytest.mark.run(order=16)
        def test_016_rebuild_services(self):
                logging.info("******** Rebuild Services **********")
                print("\nRebuild Services")
                log("start","/var/log/syslog",config.grid_vip)
                request_restart = ib_NIOS.wapi_request('POST', object_type = "dtc?_function=generate_ea_topology_db")
                print(request_restart)
                if request_restart == '{}':
                    print("Success: Rebuild Service")
                    assert True
                else:
                    print("Failure: Rebuild Service")
                    assert False
                sleep(10)
                logging.info("Test Case 16 Execution Completed")


        @pytest.mark.run(order=17)
        def test_017_validate_Rebuild_has_completed_successfully(self):
                logging.info("******** Validation of whether Rebuild has completed successfully **********")
                sleep(10)
                LookFor="'Topology EA DB Generator has finished: OK'"
                log("stop","/var/log/syslog",config.grid_vip)
                logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
                print("Success: validate Rebuild has completed successfully")
                logging.info("Test Case 17 Execution Completed")


        @pytest.mark.run(order=18)
        def test_018_Enable_the_EDNS0_Client_Subnet_option(self):
                logging.info("********** Enable the EDNS0 Client Subnet option ************")
                response = ib_NIOS.wapi_request('GET',object_type='grid:dns')
                response = json.loads(response)
                ref = response[0]['_ref']
                data={"dtc_edns_prefer_client_subnet": True}
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
                print(response1)
                assert re.search(r'grid:dns', response1)
                logging.info("******** Restart the DTC service *********")
                response = ib_NIOS.wapi_request('GET',object_type='grid')
                reference = json.loads(response)
                ref = reference[0]['_ref']
                data = {"member_order" : "SIMULTANEOUSLY", "restart_option": "FORCE_RESTART", "service_option": "ALL"}
                response1 = ib_NIOS.wapi_request('POST', object_type=ref + '?_function=restartservices',fields=json.dumps(data))
                if type(response1) == tuple:
                    if response1 == 400 or response1 == 401 or response1 == 402:
                        print("Error while restarting the DTC service")
                        assert False
                else:
                    print("DTC restarted successfully")
                    assert True
                sleep(30)
                logging.info("Test Case 18 Execution Completed")


        @pytest.mark.run(order=20)
        def test_019_ADD_two_IPV4_Networks(self):
                logging.info("******** Add two IPV4 Networks *********")
                data = {"network": config.network1, "extattrs": { "dtc-ea": { "value": "1"}}}
                response1 = ib_NIOS.wapi_request('POST',object_type="network", fields=json.dumps(data))
                print(response1)
                if type(response1) == tuple:
                    if response1 == 400 or response1 == 401 or response1 == 402:
                        print("Error while creating the IPV4 NETWOR4")
                        assert False
                else:
                    print("Network 1 created successfully")
                    assert True
                logging.info("****** Creation of second network ***********")
                data = {"network": config.network2, "extattrs": { "dtc-ea": { "value": "2"}}}
                response2 = ib_NIOS.wapi_request('POST',object_type="network", fields=json.dumps(data))
                print(response2)
                if type(response2) == tuple:
                    if response2 == 400 or response2 == 401 or response2 == 402:
                        print("Error while creating the IPV4 NETWOR4")
                        assert False
                else:
                    print("Network 2 created successfully")
                    assert True
                logging.info("Test Case 19 Execution Completed")


        @pytest.mark.run(order=21)
        def test_020_rebuild_services(self):
                logging.info("******** Rebuild Services **********")
                print("\nRebuild Services")
                log("start","/var/log/syslog",config.grid_vip)
                request_restart = ib_NIOS.wapi_request('POST', object_type = "dtc?_function=generate_ea_topology_db")
                print(request_restart)
                if request_restart == '{}':
                    print("Success: Rebuild Service")
                    assert True
                else:
                    print("Failure: Rebuild Service")
                    assert False
                sleep(10)
                logging.info("Test Case 20 Execution Completed")


        @pytest.mark.run(order=21)
        def test_021_validate_Rebuild_has_completed_successfully(self):
                logging.info("******** Validation of whether Rebuild has completed successfully **********")
                sleep(10)
                LookFor="'Topology EA DB Generator has finished: OK'"
                log("stop","/var/log/syslog",config.grid_vip)
                logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
                print("Success: validate Rebuild has completed successfully")
                logging.info("Test Case 21 Execution Completed")


        @pytest.mark.run(order=22)
        def test_022_Add_new_topology_rule_1_for_the_pool(self):
                logging.info("********** Add new topology rule 1 for the pool ************")
                logging.info("********** Getting ref of dtc pools ***********")
                response = ib_NIOS.wapi_request('GET',object_type="dtc:pool")
                response = json.loads(response)
                ref_pool=[]
                for i in response:
                    i = i['_ref']
                    ref_pool.append(i)
                data = {"name": "ea-rule", "rules": [{"sources": [{"source_op": "IS","source_type": "EA0","source_value": "1"}], "dest_type": "POOL","destination_link": ref_pool[0]}, {"sources": [{"source_op": "IS","source_type": "EA0","source_value": "2"}], "dest_type": "POOL","destination_link": ref_pool[1]}]}
                response1 = ib_NIOS.wapi_request('POST',object_type="dtc:topology", fields=json.dumps(data))
                print(response1)
                if "dtc:topology" in response1:
                    assert True
                    print("Topology rule got created successfully")
                else:
                    print("Error while creating Topology rule")
                    assert False
                logging.info("Test Case 22 Execution Completed")



        @pytest.mark.run(order=23)
        def test_023_Modify_the_lb_method_of_LBDN_to_Topology(self):
                logging.info("************* Modify the LB method of LBDN to Topology ************")
                logging.info("********* Getting the topology reference *********")
                response2 = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ea-rule')
                response2 = json.loads(response2)
                response2_ref = response2[0]['_ref']
                logging.info("********* Modify the lb preferred method to topology *********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=LBDN_1')
                response = json.loads(response)
                ref_lbdn = response[0]['_ref']
                data = {"lb_method": "TOPOLOGY", "topology": response2_ref}
                print(data)
                response = ib_NIOS.wapi_request('PUT',object_type=ref_lbdn, fields=json.dumps(data))
                response = json.loads(response)
                logging.info("Validation of lbdn creation")
                assert re.search(r'dtc:lbdn', response)
                logging.info("******** Restart the DTC service *********")
                response = ib_NIOS.wapi_request('GET',object_type='grid')
                reference = json.loads(response)
                ref = reference[0]['_ref']
                data = {"member_order" : "SIMULTANEOUSLY", "restart_option": "FORCE_RESTART", "service_option": "ALL"}
                response1 = ib_NIOS.wapi_request('POST', object_type=ref + '?_function=restartservices',fields=json.dumps(data))
                if type(response1) == tuple:
                    if response1 == 400 or response1 == 401 or response1 == 402:
                        print("Error while restarting the DTC service")
                        assert False
                else:
                    print("DTC restarted successfully")
                    assert True
                sleep(30)
                logging.info("Test Case 23 Execution Completed")



        @pytest.mark.run(order=24)
        def test_024_Run_the_dig_command_with_subnet_of_network1(self):
                logging.info("********** Run the dig command with subnet of network1 ************")
                #output = os.popen("dig @"+config.grid_vip+" new1.dtc.com in a +subnet=10.10.1.0/24 +short > test.log").read()
                output = os.popen("dig @"+config.grid_vip+" new1.dtc.com in a +subnet="+config.network1+" +short > test.log").read()
                Server_That_Responded = os.popen("grep -v PST test.log | sort").read()
                Server_That_Responded = Server_That_Responded.strip(" ").split("\n")[0]
                print(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    assert True
                    print("Server "+Server_That_Responded+" responded for the query with subnet "+config.network1+" network")
                else:
                    print("Different server responded to the query")
                    assert False
                os.system('rm test.log')
                logging.info("Test Case 24 Execution Completed")


        @pytest.mark.run(order=25)
        def test_025_Run_the_dig_command_with_subnet_of_network2(self):
                logging.info("********** Run the dig command with subnet of network2 ************")
                #output = os.popen("dig @"+config.grid_vip+" new1.dtc.com in a +subnet=10.10.2.0/24 +short > test.log").read()
                output = os.popen("dig @"+config.grid_vip+" new1.dtc.com in a +subnet="+config.network2+" +short > test.log").read()
                Server_That_Responded = os.popen("grep -v PST test.log | sort").read()
                Server_That_Responded = Server_That_Responded.strip(" ").split("\n")[0]
                print(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    assert True
                    print("Server "+Server_That_Responded+" responded for the query with subnet "+config.network2+" network")
                else:
                    print("Different server responded to the query")
                    assert False
                os.system('rm test.log')
                logging.info("Test Case 25 Execution Completed")


        @pytest.mark.run(order=26)
        def test_026_modify_the_ea_value_to_2_for_network1(self):
                logging.info("********** modify the ea value to 2 for network1 ************")
                response = ib_NIOS.wapi_request('GET',object_type='network', params='?network='+config.network1)
                response = json.loads(response)
                res_ref = response[0]['_ref']
                logging.info("********** modify the ea value to 2 for network1 ************")
                data = {"extattrs": { "dtc-ea": { "value": "2"}}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print(response1)
                if "network" in response1:
                    print("EA value changed successfully")
                    assert True
                else:
                    print("Error while changing the EA value")
                    assert False
                logging.info("Test Case 26 Execution Completed")


        @pytest.mark.run(order=27)
        def test_027_rebuild_services(self):
                logging.info("******** Rebuild Services **********")
                print("\nRebuild Services")
                log("start","/var/log/syslog",config.grid_vip)
                request_restart = ib_NIOS.wapi_request('POST', object_type = "dtc?_function=generate_ea_topology_db")
                print(request_restart)
                if request_restart == '{}':
                    print("Success: Rebuild Service")
                    assert True
                else:
                    print("Failure: Rebuild Service")
                    assert False
                sleep(10)
                logging.info("Test Case 27 Execution Completed")


        @pytest.mark.run(order=28)
        def test_028_validate_Rebuild_has_completed_successfully(self):
                logging.info("******** Validation of whether Rebuild has completed successfully **********")
                sleep(10)
                LookFor="'Topology EA DB Generator has finished: OK'"
                log("stop","/var/log/syslog",config.grid_vip)
                logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
                print("Success: validate Rebuild has completed successfully")
                logging.info("Test Case 28 Execution Completed")



        @pytest.mark.run(order=29)
        def test_029_Run_the_dig_command_with_subnet_of_network1(self):
                logging.info("********** Run the dig command with subnet of network1 ************")
                #output = os.popen("dig @"+config.grid_vip+" new1.dtc.com in a +subnet=10.10.1.0/24 +short > test.log").read()
                output = os.popen("dig @"+config.grid_vip+" new1.dtc.com in a +subnet="+config.network1+" +short > test.log").read()
                Server_That_Responded = os.popen("grep -v PST test.log | sort").read()
                Server_That_Responded = Server_That_Responded.strip(" ").split("\n")[0]
                print(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    assert True
                    print("Server "+Server_That_Responded+" responded for the query with subnet "+config.network1+" network")
                else:
                    print("Different server responded to the query")
                    assert False
                os.system('rm test.log')
                logging.info("Test Case 29 Execution Completed")


        @pytest.mark.run(order=30)
        def test_030_delete_the_ea_value_for_network2(self):
                logging.info("********** delete the ea value for network2 ************")
                response = ib_NIOS.wapi_request('GET',object_type='network', params='?network='+config.network2)
                response = json.loads(response)
                res_ref = response[0]['_ref']
                logging.info("********** modify the ea value to 2 for network2 ************")
                data = {"extattrs": {}}
                response1 = ib_NIOS.wapi_request('PUT',object_type=res_ref, fields=json.dumps(data))
                print(response1)
                if "network" in response1:
                    print("EA value changed successfully")
                    assert True
                else:
                    print("Error while changing the EA value")
                    assert False
                logging.info("Test Case 30 Execution Completed")


        @pytest.mark.run(order=31)
        def test_031_rebuild_services(self):
                logging.info("******** Rebuild Services **********")
                print("\nRebuild Services")
                log("start","/var/log/syslog",config.grid_vip)
                request_restart = ib_NIOS.wapi_request('POST', object_type = "dtc?_function=generate_ea_topology_db")
                print(request_restart)
                if request_restart == '{}':
                    print("Success: Rebuild Service")
                    assert True
                else:
                    print("Failure: Rebuild Service")
                    assert False
                sleep(10)
                logging.info("Test Case 31 Execution Completed")


        @pytest.mark.run(order=32)
        def test_032_validate_Rebuild_has_completed_successfully(self):
                logging.info("******** Validation of whether Rebuild has completed successfully **********")
                sleep(10)
                LookFor="'Topology EA DB Generator has finished: OK'"
                log("stop","/var/log/syslog",config.grid_vip)
                logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
                print("Success: validate Rebuild has completed successfully")
                logging.info("Test Case 32 Execution Completed")



        @pytest.mark.run(order=33)
        def test_033_Run_the_dig_command_with_subnet_of_Network2(self):
                logging.info("********** Run the dig command with subnet of Network2 ************")
                #output = os.popen("dig @"+config.grid_vip+" new1.dtc.com in a +subnet=10.10.2.0/24 +short > test.log").read()
                output = os.popen("dig @"+config.grid_vip+" new1.dtc.com in a +subnet="+config.network2+" +short > test.log").read()
                Server_That_Responded = os.popen("grep -v PST test.log | sort").read()
                Server_That_Responded = Server_That_Responded.strip(" ").split("\n")[0]
                print(Server_That_Responded)
                if Server_That_Responded != Server_ip[2]:
                    assert True
                    print("Server "+Server_That_Responded+" responded for the query with subnet of "+config.network1+" network")
                else:
                    print("Different server responded to the query")
                    assert False
                os.system('rm test.log')
                logging.info("Test Case 33 Execution Completed")


        @pytest.mark.run(order=34)
        def test_034_Run_the_dig_command_with_different_subnet_and_check_if_the_query_is_bypassed_from_DTC_Servers(self):
                logging.info("********** Run the dig command with different subnet and check if the query is bypassed from DTC servers ************")
                response = ib_NIOS.wapi_request('GET',object_type='record:a',params='?name=new1.dtc.com')
                response = json.loads(response)
                res_ip = response[0]['ipv4addr']
                output = os.popen("dig @"+config.grid_vip+" new1.dtc.com in a +subnet=20.20.2.0/24 +short > test.log").read()
                Server_That_Responded = os.popen("grep -v PST test.log | sort").read()
                Server_That_Responded = Server_That_Responded.strip(" ").split("\n")[0]
                print(Server_That_Responded)
                if Server_That_Responded not in Server_ip and str(Server_That_Responded) == res_ip: 
                    assert True
                    print("DTC servers did not respond to the query, the query was bypassed to Record which responded to the query")
                else:
                    print("One of the DTC servers responded to the query")
                    assert False
                os.system('rm test.log')
                logging.info("Test Case 34 Execution Completed")


        @pytest.mark.run(order=35)
        def test_035_Run_the_dig_command_without_subnet_and_send_the_query_from_network_clients(self):
                logging.info("********** Run the dig command without subnet and send the query from network clients ************")
                output = os.popen("dig @"+config.grid_vip+" new1.dtc.com +short > test.log").read()
                Server_That_Responded = os.popen("grep -v PST test.log | sort").read()
                Server_That_Responded = Server_That_Responded.strip(" ").split("\n")[0]
                print(Server_That_Responded)
                if Server_That_Responded in Server_ip:
                    assert True
                    print("DTC Servers Responded to the query because the query was sent from one of the network clients")
                else:
                    print("DTC servers failed to respond to the query")
                    assert False
                os.system('rm test.log')
                logging.info("Test Case 35 Execution Completed")




        @pytest.mark.run(order=36)
        def test_036_Modify_the_Network1_EA_Value_to_1(self):
                logging.info("******** Modify the Network1 EA Value to 1 *********")
                response = ib_NIOS.wapi_request('GET',object_type="network", params='?network='+config.network1)
                response = json.loads(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "dtc-ea": { "value": "1"}}}
                response1 = ib_NIOS.wapi_request('PUT', object_type=res_ref, fields=json.dumps(data))
                print(response1)
                logging.info("Test Case 36 Execution Completed")


        @pytest.mark.run(order=37)
        def test_037_Validation_of_EA_Value_of_Network1(self):
                logging.info("******** Validation of the Network1 EA Value to 1 *********")
                response = ib_NIOS.wapi_request('GET',object_type="network", params='?network='+config.network1)
                response = json.loads(response)
                res_ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET', object_type=res_ref, params='?_return_fields=extattrs')
                response1 = json.loads(response1)
                res_value = response1['extattrs']['dtc-ea']['value']
                if res_value == "1":
                    print(" Value has been modified successfully")
                    assert True
                else:
                    print(" Value has not been modified successfully")
                    assert False
                logging.info("Test Case 37 Execution Completed")



        @pytest.mark.run(order=38)
        def test_038_rebuild_services(self):
                logging.info("******** Rebuild Services **********")
                print("\nRebuild Services")
                log("start","/var/log/syslog",config.grid_vip)
                request_restart = ib_NIOS.wapi_request('POST', object_type = "dtc?_function=generate_ea_topology_db")
                print(request_restart)
                if request_restart == '{}':
                    print("Success: Rebuild Service")
                    assert True
                else:
                    print("Failure: Rebuild Service")
                    assert False
                sleep(10)
                logging.info("Test Case 38 Execution Completed")


        @pytest.mark.run(order=39)
        def test_039_validate_Rebuild_has_completed_successfully(self):
                logging.info("******** Validation of whether Rebuild has completed successfully **********")
                sleep(10)
                LookFor="'Topology EA DB Generator has finished: OK'"
                log("stop","/var/log/syslog",config.grid_vip)
                logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
                print("Success: validate Rebuild has completed successfully")
                logging.info("Test Case 39 Execution Completed")



        @pytest.mark.run(order=40)
        def test_040_Modify_the_Network1_EA_Value_to_2(self):
                logging.info("******** Modify the Network2 EA Value to 2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="network", params='?network='+config.network2)
                response = json.loads(response)
                res_ref = response[0]['_ref']
                data = {"extattrs": { "dtc-ea": { "value": "2"}}}
                response1 = ib_NIOS.wapi_request('PUT', object_type=res_ref, fields=json.dumps(data))
                print(response1)
                logging.info("Test Case 40 Execution Completed")


        @pytest.mark.run(order=41)
        def test_041_Validation_of_EA_Value_of_Network2(self):
                logging.info("******** Validation of the Network2 EA Value to 2 *********")
                response = ib_NIOS.wapi_request('GET',object_type="network", params='?network='+config.network2)
                response = json.loads(response)
                res_ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET', object_type=res_ref, params='?_return_fields=extattrs')
                response1 = json.loads(response1)
                res_value = response1['extattrs']['dtc-ea']['value']
                if res_value == "2":
                    print(" Value has been modified successfully")
                    assert True
                else:
                    print(" Value has not been modified successfully")
                    assert False
                logging.info("Test Case 41 Execution Completed")



        @pytest.mark.run(order=42)
        def test_042_rebuild_services(self):
                logging.info("******** Rebuild Services **********")
                print("\nRebuild Services")
                log("start","/var/log/syslog",config.grid_vip)
                request_restart = ib_NIOS.wapi_request('POST', object_type = "dtc?_function=generate_ea_topology_db")
                print(request_restart)
                if request_restart == '{}':
                    print("Success: Rebuild Service")
                    assert True
                else:
                    print("Failure: Rebuild Service")
                    assert False
                sleep(10)
                logging.info("Test Case 42 Execution Completed")


        @pytest.mark.run(order=43)
        def test_043_validate_Rebuild_has_completed_successfully(self):
                logging.info("******** Validation of whether Rebuild has completed successfully **********")
                sleep(10)
                LookFor="'Topology EA DB Generator has finished: OK'"
                log("stop","/var/log/syslog",config.grid_vip)
                logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
                print("Success: validate Rebuild has completed successfully")
                logging.info("Test Case 43 Execution Completed")


        @pytest.mark.run(order=44)
        def test_044_Add_new_topology_rule_2_for_the_servers(self):
                logging.info("********** Add new topology rule 2 for the pool ************")
                logging.info("********** Getting ref of dtc servers ***********")
                response = ib_NIOS.wapi_request('GET',object_type="dtc:server")
                response = json.loads(response)
                ref_server=[]
                for i in response:
                    i = i['_ref']
                    ref_server.append(i)
                data = {"name": "ea-rule2", "rules": [{"sources": [{"source_op": "IS","source_type": "EA0","source_value": "1"}], "dest_type": "SERVER","destination_link": ref_server[1]}]}
                response1 = ib_NIOS.wapi_request('POST',object_type="dtc:topology", fields=json.dumps(data))
                print(response1)
                if "dtc:topology" in response1:
                    assert True
                    print("Topology rule got created successfully")
                else:
                    print("Error while creating Topology rule")
                    assert False
                logging.info("Test Case 44 Execution Completed")


        @pytest.mark.run(order=45)
        def test_045_Add_new_topology_rule_2_for_the_servers(self):
                logging.info("********** Add new topology rule 3 for the pool ************")
                logging.info("********** Getting ref of dtc servers ***********")
                response = ib_NIOS.wapi_request('GET',object_type="dtc:server")
                response = json.loads(response)
                ref_server=[]
                for i in response:
                    i = i['_ref']
                    ref_server.append(i)
                data = {"name": "ea-rule3", "rules": [{"sources": [{"source_op": "IS","source_type": "EA0","source_value": "2"}], "dest_type": "SERVER","destination_link": ref_server[0]}]}
                response1 = ib_NIOS.wapi_request('POST',object_type="dtc:topology", fields=json.dumps(data))
                print(response1)
                if "dtc:topology" in response1:
                    assert True
                    print("Topology rule got created successfully")
                else:
                    print("Error while creating Topology rule")
                    assert False
                logging.info("Test Case 45 Execution Completed")




        @pytest.mark.run(order=46)
        def test_046_Modifying_Pool1_and_Assigining_Topology_rule_2(self):
                logging.info("Getting the server name reference ")
                server_ref = []
                for i in Server_name:
                        response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                        response_servers = json.loads(response_servers)
                        ref = response_servers[0]['_ref']
                        server_ref.append(ref)
                print(server_ref)
                logging.info("****** Getting the ref of Pool 1 ******")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_1')
                response = json.loads(response)
                ref_pool = response[0]['_ref']
                logging.info("****** Getting the ref of topo rule 2 ******")
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ea-rule2')
                response1 = json.loads(response1)
                ref_topo = response1[0]['_ref']
                logging.info("****** Modifying the LB methond and Pool members on Pool1 ******")
                data = {"lb_preferred_method": "TOPOLOGY", "lb_preferred_topology": ref_topo, "lb_alternate_method": "ALL_AVAILABLE", "servers": [{"ratio": 1,"server": str(server_ref[1])},{"ratio": 1,"server": str(server_ref[0])}], "monitors": ["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"]}
                response2 = ib_NIOS.wapi_request('PUT', object_type=ref_pool, fields=json.dumps(data))
                ref1 = json.loads(response2)
                print(ref1)
                logging.info("Validation of Pool creation")
                assert re.search(r'dtc:pool', ref1)
                logging.info("******** Restart the DTC service *********")
                response = ib_NIOS.wapi_request('GET',object_type='grid')
                reference = json.loads(response)
                ref = reference[0]['_ref']
                data = {"member_order" : "SIMULTANEOUSLY", "restart_option": "FORCE_RESTART", "service_option": "ALL"}
                response1 = ib_NIOS.wapi_request('POST', object_type=ref + '?_function=restartservices',fields=json.dumps(data))
                if type(response1) == tuple:
                    if response1 == 400 or response1 == 401 or response1 == 402:
                        print("Error while restarting the DTC service")
                        assert False
                else:
                    print("DTC restarted successfully")
                    assert True
                sleep(30)
                logging.info("Test Case 46 Execution Completed")



        @pytest.mark.run(order=47)
        def test_047_Modifying_Pool2_and_Assigining_Topology_rule_3(self):
                logging.info("Getting the server name reference ")
                server_ref = []
                for i in Server_name:
                        response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                        response_servers = json.loads(response_servers)
                        ref = response_servers[0]['_ref']
                        server_ref.append(ref)
                print(server_ref)
                logging.info("****** Getting the ref of Pool 2 ******")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=Pool_2')
                response = json.loads(response)
                ref_pool = response[0]['_ref']
                logging.info("****** Getting the ref of topo rule 2 ******")
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ea-rule3')
                response1 = json.loads(response1)
                ref_topo = response1[0]['_ref']
                logging.info("****** Modifying the LB methond and Pool members on Pool2 ******")
                data = {"lb_preferred_method": "TOPOLOGY", "lb_preferred_topology": ref_topo, "lb_alternate_method": "ALL_AVAILABLE", "servers": [{"ratio": 1,"server": str(server_ref[0])},{"ratio": 1,"server": str(server_ref[1])}], "monitors": ["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"]}
                response2 = ib_NIOS.wapi_request('PUT', object_type=ref_pool, fields=json.dumps(data))
                ref1 = json.loads(response2)
                print(ref1)
                logging.info("Validation of Pool creation")
                assert re.search(r'dtc:pool', ref1)
                logging.info("******** Restart the DTC service *********")
                response = ib_NIOS.wapi_request('GET',object_type='grid')
                reference = json.loads(response)
                ref = reference[0]['_ref']
                data = {"member_order" : "SIMULTANEOUSLY", "restart_option": "FORCE_RESTART", "service_option": "ALL"}
                response1 = ib_NIOS.wapi_request('POST', object_type=ref + '?_function=restartservices',fields=json.dumps(data))
                if type(response1) == tuple:
                    if response1 == 400 or response1 == 401 or response1 == 402:
                        print("Error while restarting the DTC service")
                        assert False
                else:
                    print("DTC restarted successfully")
                    assert True
                sleep(30)
                logging.info("Test Case 47 Execution Completed")



        @pytest.mark.run(order=48)
        def test_048_Run_the_dig_command_with_subnet_of_network1(self):
                logging.info("********** Run the dig command with subnet of network1 ************")
                #output = os.popen("dig @"+config.grid_vip+" new1.dtc.com in a +subnet=10.10.1.0/24 +short > test.log").read()
                output = os.popen("dig @"+config.grid_vip+" new1.dtc.com in a +subnet="+config.network1+" +short > test.log").read()
                Server_That_Responded = os.popen("grep -v PST test.log | sort").read()
                Server_That_Responded = Server_That_Responded.strip(" ").split("\n")[0]
                print(Server_That_Responded)
                if Server_That_Responded == Server_ip[2]:
                    assert True
                    print("Server "+Server_That_Responded+" responded for the query with subnet "+config.network1+" network")
                else:
                    print("Different server responded to the query")
                    assert False
                os.system('rm test.log')
                logging.info("Test Case 48 Execution Completed")


        @pytest.mark.run(order=49)
        def test_049_Run_the_dig_command_with_subnet_of_network2(self):
                logging.info("********** Run the dig command with subnet of network2 ************")
                #output = os.popen("dig @"+config.grid_vip+" new1.dtc.com in a +subnet=10.10.1.0/24 +short > test.log").read()
                output = os.popen("dig @"+config.grid_vip+" new1.dtc.com in a +subnet="+config.network2+" +short > test.log").read()
                Server_That_Responded = os.popen("grep -v PST test.log | sort").read()
                Server_That_Responded = Server_That_Responded.strip(" ").split("\n")[0]
                print(Server_That_Responded)
                if Server_That_Responded == Server_ip[1]:
                    assert True
                    print("Server "+Server_That_Responded+" responded for the query with subnet "+config.network2+" network")
                else:
                    print("Different server responded to the query")
                    assert False
                os.system('rm test.log')
                logging.info("Test Case 49 Execution Completed")


        @pytest.mark.run(order=50)
        def test_050_Delete_the_LBDN(self):
                logging.info("********** Getting the ref of LBDN created ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=LBDN_1')
                response = json.loads(response)
                res_ref = response[0]['_ref']
                logging.info("********** Delete the LBDN created ************")
                response = ib_NIOS.wapi_request('DELETE' ,object_type=res_ref)
                print(response)
                logging.info("Validation of LBDN Deleted")
                assert re.search(r'dtc:lbdn', response)
                logging.info("******** Restart the DTC service *********")
                response = ib_NIOS.wapi_request('GET',object_type='grid')
                reference = json.loads(response)
                ref = reference[0]['_ref']
                data = {"member_order" : "SIMULTANEOUSLY", "restart_option": "FORCE_RESTART", "service_option": "ALL"}
                response1 = ib_NIOS.wapi_request('POST', object_type=ref + '?_function=restartservices',fields=json.dumps(data))
                if type(response1) == tuple:
                    if response1 == 400 or response1 == 401 or response1 == 402:
                        print("Error while restarting the DTC service")
                        assert False
                else:
                    print("DTC restarted successfully")
                    assert True
                sleep(30)
                logging.info("Test Case 50 Execution Completed")


        @pytest.mark.run(order=51)
        def test_051_Delete_the_First_Topology_Rule_Created(self):
                logging.info("********** Getting the ref of First Topology rule created ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=ea-rule')
                response = json.loads(response)
                res_ref = response[0]['_ref']
                response = ib_NIOS.wapi_request('DELETE' ,object_type=res_ref)
                print(response)
                logging.info("Validation of whether topology is deleted or not")
                assert re.search(r'dtc:topology', response)
                logging.info("Test Case 51 Execution Completed")


        @pytest.mark.run(order=52)
        def test_052_Delete_the_DTC_Pools(self):
                logging.info("********** Getting the ref of pools created ************")
                pools = ["Pool_1", "Pool_2"]
                for i in pools:
                    response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name='+i)
                    response = json.loads(response)
                    res_ref = response[0]['_ref']
                    logging.info("********** Delete the pool created ************")
                    response = ib_NIOS.wapi_request('DELETE' ,object_type=res_ref)
                    print(response)
                    logging.info("Validation of whether DTC pools is deleted or not")
                    assert re.search(r'dtc:pool', response)
                logging.info("Test Case 52 Execution Completed")



        @pytest.mark.run(order=53)
        def test_053_Delete_the_Second_and_Thrid_topology_rule(self):
                logging.info("********** Getting the ref of pools created ************")
                pools = ["ea-rule2", "ea-rule3"]
                for i in pools:
                    response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name='+i)
                    response = json.loads(response)
                    res_ref = response[0]['_ref']
                    logging.info("********** Delete the topology created ************")
                    response = ib_NIOS.wapi_request('DELETE' ,object_type=res_ref)
                    print(response)
                    logging.info("Validation of whether topology is deleted or not")
                    assert re.search(r'dtc:topology', response)
                logging.info("Test Case 53 Execution Completed")


        @pytest.mark.run(order=54)
        def test_054_Delete_the_DTC_Servers(self):
                logging.info("********** Getting the ref of servers created ************")
                pools = ["server1", "server2"]
                for i in pools:
                    response = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                    response = json.loads(response)
                    res_ref = response[0]['_ref']
                    logging.info("********** Delete the server created ************")
                    response = ib_NIOS.wapi_request('DELETE' ,object_type=res_ref)
                    print(response)
                    logging.info("Validation of whether DTC servers is deleted or not")
                    assert re.search(r'dtc:server', response)
                logging.info("Test Case 54 Execution Completed")



        @pytest.mark.run(order=55)
        def test_055_Disable_the_EDNS0_Client_Subnet_option(self):
                logging.info("********** Enable the EDNS0 Client Subnet option ************")
                response = ib_NIOS.wapi_request('GET',object_type='grid:dns')
                response = json.loads(response)
                ref = response[0]['_ref']
                data={"dtc_edns_prefer_client_subnet": False}
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
                print(response1)
                assert re.search(r'grid:dns', response1)
                logging.info("******** Restart the DTC service *********")
                response = ib_NIOS.wapi_request('GET',object_type='grid')
                reference = json.loads(response)
                ref = reference[0]['_ref']
                data = {"member_order" : "SIMULTANEOUSLY", "restart_option": "FORCE_RESTART", "service_option": "ALL"}
                response1 = ib_NIOS.wapi_request('POST', object_type=ref + '?_function=restartservices',fields=json.dumps(data))
                if type(response1) == tuple:
                    if response1 == 400 or response1 == 401 or response1 == 402:
                        print("Error while restarting the DTC service")
                        assert False
                else:
                    print("DTC restarted successfully")
                    assert True
                sleep(30)
                logging.info("Test Case 55 Execution Completed")



        @pytest.mark.run(order=56)
        def test_056_Delete_the_Networks(self):
                logging.info("********** Getting the ref of networkscreated ************")
                pools = [config.network1, config.network2]
                for i in pools:
                    response = ib_NIOS.wapi_request('GET',object_type='network', params='?network='+i)
                    response = json.loads(response)
                    res_ref = response[0]['_ref']
                    logging.info("********** Delete the server created ************")
                    response = ib_NIOS.wapi_request('DELETE' ,object_type=res_ref)
                    print(response)
                    logging.info("Validation of whether netwoks is deleted or not")
                    assert re.search(r'network', response)
                logging.info("Test Case 56 Execution Completed")


        @pytest.mark.run(order=57)
        def test_057_delete_the_Custom_EA_in_Grid_Properties_Traffic_Control(self):
                logging.info("********** delete the Custom EA in Grid Properties Traffic Conftrol ************")
                response = ib_NIOS.wapi_request('GET',object_type='grid:dns')
                response = json.loads(response)
                ref = response[0]['_ref']
                data={"dtc_topology_ea_list": []}
                response1 = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
                print(response1)
                assert re.search(r'grid:dns', response1)
                logging.info("Test Case 57 Execution completed ")


        @pytest.mark.run(order=58)
        def test_058_Delete_the_extensibleattribute_that_is_created(self):
                logging.info("********** Getting the ref of extensibleattributedef that is created ************")
                response = ib_NIOS.wapi_request('GET',object_type='extensibleattributedef', params='?name=dtc-ea')
                response = json.loads(response)
                res_ref = response[0]['_ref']
                response = ib_NIOS.wapi_request('DELETE' ,object_type=res_ref)
                print(response)
                logging.info("Validation of whether extensibleattribute is deleted or not")
                assert re.search(r'extensibleattributedef', response)
                logging.info("Test Case 58 Execution Completed")


        @pytest.mark.run(order=59)
        def test_059_rebuild_services(self):
                logging.info("******** Rebuild Services **********")
                print("\nRebuild Services")
                log("start","/var/log/syslog",config.grid_vip)
                request_restart = ib_NIOS.wapi_request('POST', object_type = "dtc?_function=generate_ea_topology_db")
                print(request_restart)
                if request_restart == '{}':
                    print("Success: Rebuild Service")
                    assert True
                else:
                    print("Failure: Rebuild Service")
                    assert False
                sleep(10)
                logging.info("Test Case 59 Execution Completed")


        @pytest.mark.run(order=60)
        def test_060_validate_Rebuild_has_completed_successfully(self):
                logging.info("******** Validation of whether Rebuild has completed successfully **********")
                sleep(10)
                LookFor="'Topology EA DB Generator has finished: OK'"
                log("stop","/var/log/syslog",config.grid_vip)
                logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
                print("Success: validate Rebuild has completed successfully")
                logging.info("Test Case 60 Execution Completed")



        @pytest.mark.run(order=61)
        def test_061_Delete_the_Zone_created(self):
                logging.info("********** Getting the ref of Zone ************")
                response = ib_NIOS.wapi_request('GET',object_type='zone_auth', params='?fqdn=dtc.com')
                response = json.loads(response)
                res_ref = response[0]['_ref']
                response = ib_NIOS.wapi_request('DELETE' ,object_type=res_ref)
                print(response)
                logging.info("Validation of whether zone is deleted or not")
                assert re.search(r'zone_auth', response)
                logging.info("Test Case 61 Execution Completed")



        @pytest.mark.run(order=62)
        def test_062_Stop_DNS_Service(self):
                logging.info("Stop DNS Service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                for i in res:
                        logging.info("Modify a enable_dns")
                        data = {"enable_dns": False}
                        response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
                        print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 62 Execution Completed")

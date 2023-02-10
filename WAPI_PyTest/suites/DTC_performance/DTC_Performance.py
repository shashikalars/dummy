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
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="DTC_performance.log" ,level=logging.INFO,filemode='w')

Server_ip=[]
d={}
Server_name=[]
a_record_name=[]
Vm_ip=[]
for i in range(1,50):
    W = config.ip_range+str(i)
    response = os.system("ping -c 1 " + W)
    if (response == 0):
        pingstatus = "Network Active"
        Server_ip.append(W)
    else:
        pass
for i in range(0,20):
    name="server"+str(i)
    print(name)
    d[name]=Server_ip[i]
    Server_name.append(name)

for i,j in d.items():
    a_name = str(i)+".dtc.com"
    a_record_name.append(a_name)

for i in range(1,50):
    W = config.ip_range+str(i)
    response = os.system("ping -c 1 " + W)
    if (response == 0):
        pingstatus = "Network Active"
        Server_ip.append(W)
    else:
        pass

for i in range(2,50):
    W = config.Vm_ip_range+str(i)
    response = os.system("ping -c 1 " + W)
    if (response == 0):
        pingstatus = "Network Active"
        Vm_ip.append(W)
    else:
        pass

print(Vm_ip)

class Rfe_6827(unittest.TestCase):

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
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                for i in res:
                        print i
                        logging.info("found")
                        assert i["enable_dns"] == True
                print("Test Case 2 Execution Completed")


        @pytest.mark.run(order=2)
        def test_003_create_AuthZone(self):
                print("Create A auth Zone")
                data = {"fqdn": "dtc.com","grid_primary": [{"name": config.grid_member_fqdn,"stealth":False}, {"name": config.grid_member1_fqdn,"stealth":False}, {"name": config.grid_member2_fqdn,"stealth":False}]}
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

        @pytest.mark.run(order=4)
        def test_004_Validate_AuthZone(self):
                logging.info("Validate the  Zone")
                response =  ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=dtc.com", grid_vip=config.grid_vip)
                print response
                if ('"fqdn": "dtc.com"' in response):
                    assert True
                else:
                    assert False
                logging.info("Test Case 4 Execution Completed")

        @pytest.mark.run(order=5)
        def test_005_Creating_Twenty_DTC_Servers(self):
                logging.info("Creating Twenty DTC Servers")
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
                logging.info("Test Case 5 Execution Completed")

        @pytest.mark.run(order=6)
        def test_006_Validation_of_Servers_Created(self):
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
                logging.info("Test Case 6 Execution Completed")

        @pytest.mark.run(order=7)
        def test_007_Creating_a_Pool_with_Twenty_Servers(self):
                logging.info("********** Adding one DTC server to Pool ************")
                logging.info("Getting the server name reference ")
                server_ref = []
                for i in Server_name:
                        response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                        response_servers = json.loads(response_servers)
                        ref = response_servers[0]['_ref']
                        server_ref.append(ref)
                print(server_ref)
                logging.info("****** Creating the pool and assiging the server ******")
                data = {"name": "DTC_Sample_pool", "lb_preferred_method": "ROUND_ROBIN", "servers": [{"ratio": 4,"server": str(server_ref[0])}], "monitors": ["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"]}
                response_servers = ib_NIOS.wapi_request('POST',object_type='dtc:pool', fields=json.dumps(data))
                ref1 = json.loads(response_servers)
                print(ref1)
                logging.info("Validation of Pool creation")
                assert re.search(r'dtc:pool', ref1)
                All_the_Server=[]
                server_dict={}
                for i in server_ref:
                        server_dict['ratio']=1
                        server_dict['server']=i
                        All_the_Server.append(server_dict)
                        server_dict={}
                data = {"name": "DTC_Sample_pool", "lb_preferred_method": "ROUND_ROBIN", "servers": All_the_Server, "monitors": ["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"]}
                response = ib_NIOS.wapi_request('PUT',object_type=ref1, fields=json.dumps(data))
                response = json.loads(response)
                logging.info("Validation of Pool creation")
                assert re.search(r'dtc:pool', response)
                logging.info("All the Servers are added to pool")
                logging.info("Test Case 7 Execution Completed")

        @pytest.mark.run(order=8)
        def test_008_Validation_of_DTC_Pool_of_20_servers(self):
                logging.info("********** Validating all 20 servers in pool ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                ref = json.loads(response)
                ref1 = ref[0]['_ref']
                ref2 = ref[0]['name']
                print(ref1)
                print(ref2)
                response = ib_NIOS.wapi_request('GET',object_type=ref1 , params='?_return_fields=servers')
                print(response)
                ref1 = json.loads(response)
                new_list = []
                for i in ref1['servers']:
                        a = i['server'].split(":")[-1]
                        new_list.append(a)
                if new_list == Server_name:
                        assert True
                        print("Validation of all servers are done, all servers match")
                else:
                        print("Validation of all servers failed, all servers do not match")
                        assert False
                logging.info("Validating the Pool that is created")
                if ref2 == "DTC_Sample_pool":
                    assert True
                    print("DTC Pool has been created successfully")
                else:
                    print("Pool creation was not successfull")
                    assert False
                logging.info("Test Case 8 Execution Completed")


        @pytest.mark.run(order=9)
        def test_009_Creation_of_LBDN(self):
                logging.info("********** Creation of LBDN ************")
                logging.info("********** Getting the ref of authorativezone ************")
                response = ib_NIOS.wapi_request('GET',object_type='zone_auth', params='?fqdn=dtc.com')
                response = json.loads(response)
                ref_zone = response[0]['_ref']
                logging.info("********** Getting the ref of pool ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref_pool = response[0]['_ref']
                logging.info("********** Creating the lbdn by post request ************")
                data = {"auth_zones": [ref_zone], "name": "DTC_LBDN", "lb_method": "ROUND_ROBIN", "patterns": ["*.dtc.com"], "pools": [{"ratio": 1, "pool": ref_pool}]}
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
                logging.info("Test Case 9 Execution Completed")
        
        @pytest.mark.run(order=10)
        def test_010_Modify_the_pool_lb_method_to_all_available(self):
                logging.info("********** Modifying the pool lb method to all available ************")
                logging.info("********** Getting the server name reference ***********")
                server_ref = []
                for i in Server_name:
                        response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                        response_servers = json.loads(response_servers)
                        ref = response_servers[0]['_ref']
                        server_ref.append(ref)
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                ref1 = json.loads(response)
                ref1 = ref1[0]['_ref']
                All_the_Server=[]
                server_dict={}
                for i in server_ref:
                        server_dict['ratio']=1
                        server_dict['server']=i
                        All_the_Server.append(server_dict)
                        server_dict={}
                logging.info("********** Changing the pool lb method to all available ***********")
                data = {"lb_preferred_method": "ALL_AVAILABLE"}
                print(data)
                response = ib_NIOS.wapi_request('PUT',object_type=ref1, fields=json.dumps(data))
                response = json.loads(response)
                print(response) 
                logging.info("Validation of Pool creation")
                assert re.search(r'dtc:pool', response)
                logging.info("All the Servers are added to pool")
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
                logging.info("Test Case 10 Execution Completed")

        @pytest.mark.run(order=11)
        def test_011_Validation_of_changes_from_round_robin_to_all_available(self):
                logging.info("********** Validation of changes from round robin to all available ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=lb_preferred_method')
                response1 = json.loads(response1)
                print(response1)
                ref1 = response1['lb_preferred_method']
                if ref1 == "ALL_AVAILABLE":
                        assert True
                        print("Modified changes are reflecting")
                else:
                        print("Modified changes are not reflecting")
                        assert False
                logging.info("Test Case 11 Execution Completed")

        
        @pytest.mark.run(order=12)
        def test_012_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                print(output1)
                new_ip=Server_ip[:20]
                for i in new_ip:
                        if ("5000" in output1) and (i in output1):
                                assert True
                                print("5000 queries are seen in %s" % (i))
                        else:
                                print("queries doesn't match in %s server" % (i))
                                assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 12 Execution Completed")


        @pytest.mark.run(order=13)
        def test_013_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                print(output1)
                new_ip=Server_ip[:20]
                for i in new_ip:
                        if ("5000" in output1) and (i in output1):
                                assert True
                                print("5000 queries are seen in %s" % (i))
                        else:
                                print("queries doesn't match in %s server" % (i))
                                assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 13 Execution Completed")

        @pytest.mark.run(order=14)
        def test_014_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                print(output1)
                new_ip=Server_ip[:20]
                for i in new_ip:
                        if ("5000" in output1) and (i in output1):
                                assert True   
                                print("5000 queries are seen in %s" % (i))
                        else:
                                print("queries doesn't match in %s server" % (i))
                                assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 14 Execution Completed")

        @pytest.mark.run(order=15)
        def test_015_Drop_each_server_from_grid_master_and_members(self):
                logging.info("********** Drop each server from grid master and members ************")
                new_list = [config.grid_master_vip, config.grid_member1_vip, config.grid_member2_vip]
                for i in Server_ip[:3]:
                        for j in new_list:
                                #print("Logging in to %s" % (j))
                                drop_server = "iptables -I INPUT -s "+i+" -j DROP"
                                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+j)
                                child.logfile=sys.stdout
                                child.expect('#')
                                child.sendline(drop_server)
                                child.expect('#')
                                child.close()
                                sleep(60)
                logging.info("Test Case 15 Execution Completed")


        @pytest.mark.run(order=16)
        def test_016_Run_the_dig_command_with_5k_queries_on_grid_master_verify_severs_are_dropped(self):
                logging.info("********** Run the dig command with 5k queries on grid master and verify servers are dropped ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                print(output1)
                new_ip=Server_ip[3:20]
                dropped_servers=Server_ip[:3]
                logging.info("Validation of dropped servers in queries")
                Server_responded = output1.split("\n")
                Server_responded=list(filter(None, Server_responded))
                No_of_queries=[]
                for i in Server_responded:
                    a = i.strip(" ").split(" ")[1]
                    No_of_queries.append(a)
                for j in dropped_servers:
                    if (j not in No_of_queries):
                        assert True
                        print("Server "+j+" is not seen in the queries")
                    else:
                        print("Server "+j+" dropped failed and it is responding to the query")
                        assert False
                logging.info("Validation of query output")
                for i in new_ip:
                    if ("5000" in output1) and (i in output1):
                        assert True
                        print("5000 queries are seen in %s" % (i))
                    else:
                        print("queries doesn't match in %s server or %s Server Dropped failed" % (i, i))
                        assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 16 Execution Completed")


        @pytest.mark.run(order=17)
        def test_017_Run_the_dig_command_with_5k_queries_on_grid_member_1_verify_severs_are_dropped(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 and verify servers are dropped ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                print(output1)
                new_ip=Server_ip[3:20]
                dropped_servers=Server_ip[:3]
                logging.info("Validation of dropped servers in queries")
                Server_responded = output1.split("\n")
                Server_responded=list(filter(None, Server_responded))
                No_of_queries=[]
                for i in Server_responded:
                    a = i.strip(" ").split(" ")[1]
                    No_of_queries.append(a)
                for j in dropped_servers:
                    if (j not in No_of_queries):
                        assert True
                        print("Server "+j+" is not seen in the queries")
                    else:
                        print("Server "+j+" dropped failed and it is responding to the query")
                        assert False
                logging.info("Validation of query output")
                for i in new_ip:
                    if ("5000" in output1) and (i in output1):
                        assert True
                        print("5000 queries are seen in %s" % (i))
                    else:
                        print("queries doesn't match in %s server or %s Server Dropped failed" % (i, i))
                        assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 17 Execution Completed")


        @pytest.mark.run(order=18)
        def test_018_Run_the_dig_command_with_5k_queries_on_grid_member_2_verify_severs_are_dropped(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 and verify servers are dropped ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                print(output1)
                new_ip=Server_ip[3:20]
                dropped_servers=Server_ip[:3]
                logging.info("Validation of dropped servers in queries")
                Server_responded = output1.split("\n")
                Server_responded=list(filter(None, Server_responded))
                No_of_queries=[]
                for i in Server_responded:
                    a = i.strip(" ").split(" ")[1]
                    No_of_queries.append(a)
                for j in dropped_servers:
                    if (j not in No_of_queries):
                        assert True
                        print("Server "+j+" is not seen in the queries")
                    else:
                        print("Server "+j+" dropped failed and it is responding to the query")
                        assert False
                logging.info("Validation of query output")
                for i in new_ip:
                    if ("5000" in output1) and (i in output1):
                        assert True
                        print("5000 queries are seen in %s" % (i))
                    else:
                        print("queries doesn't match in %s server or %s Server Dropped failed" % (i, i))
                        assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 18 Execution Completed")

        @pytest.mark.run(order=19)
        def test_019_Accept_the_dropped_servers_from_grid_master_and_members(self):
                logging.info("********** Accept the dropped servers from grid master and members ************")
                new_list = [config.grid_master_vip, config.grid_member1_vip, config.grid_member2_vip]
                for i in Server_ip[:3]:
                        for j in new_list:
                                add_server = "iptables -I INPUT -s "+i+" -j ACCEPT"
                                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+j)
                                child.logfile=sys.stdout
                                child.expect('#')
                                child.sendline(add_server)
                                child.expect('#')
                                child.close()
                                sleep(60)
                logging.info("Test Case 19 Execution Completed")

        @pytest.mark.run(order=20)
        def test_020_Modify_the_pool_lb_method_to_ratio_dynamic(self):
                logging.info("********** Modifying the pool to lb method to ratio dynamic ************")
                logging.info("Getting the server name reference ")
                server_ref = []
                for i in Server_name:
                        response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                        response_servers = json.loads(response_servers)
                        ref = response_servers[0]['_ref']
                        server_ref.append(ref)
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                ref1 = json.loads(response)
                ref1 = ref1[0]['_ref']
                All_the_Server=[]
                server_dict={}
                for i in server_ref:
                        server_dict['ratio']=1
                        server_dict['server']=i
                        All_the_Server.append(server_dict)
                        server_dict={}
                data = {"lb_preferred_method": "DYNAMIC_RATIO", "lb_dynamic_ratio_preferred": {"method": "ROUND_TRIP_DELAY", "monitor": "dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp", "monitor_weighing": "RATIO"}}
                print(data)
                response = ib_NIOS.wapi_request('PUT',object_type=ref1, fields=json.dumps(data))
                response = json.loads(response)
                print(response)
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
                logging.info("Test Case 20 Execution Completed")

        @pytest.mark.run(order=21)
        def test_021_Validation_of_lb_method_to_ratio_dynamic(self):
                logging.info("********** Validation of lb method to ratio dynamic ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=lb_preferred_method')
                response1 = json.loads(response1)
                print(response1)
                ref1 = response1['lb_preferred_method']
                if ref1 == "DYNAMIC_RATIO":
                        assert True
                        print("Modified changes are reflecting")
                else:
                        print("Modified changes are not reflecting")
                        assert False
                logging.info("Test Case 21 Execution Completed")


        @pytest.mark.run(order=22)
        def test_022_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                print(output1)
                new_ip=Server_ip[:20]
                total_expected_queries=int(5000)
                logging.info("Checking total number of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                for i in queries:
                    i = i.strip(" ").split(" ")[0]
                    No_of_queries.append(int(i))
                No_of_queries=list(filter(None, No_of_queries))
                print(No_of_queries)
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("Verifying if all the servers received the query or not")
                for i in new_ip:
                        if (i in output1):
                                if (re.findall(r'\b2\d{2}\b', output1)) or (re.findall(r'\b3\d{2}\b', output1)):
                                       assert True
                                       print("Pattern match for number of queries are seen in server %s" % (i))
                                else:
                                       print("Patterns doesn't match for the queries in %s server" % (i))
                                       assert False
                        else:
                                print("Server %s doesn't match for the query sent" % (i))
                                assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 22 Execution Completed")


        @pytest.mark.run(order=23)
        def test_023_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                print(output1)
                new_ip=Server_ip[:20]
                total_expected_queries=int(5000)
                logging.info("Checking total number of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                for i in queries:
                    i = i.strip(" ").split(" ")[0]
                    No_of_queries.append(int(i))
                No_of_queries=list(filter(None, No_of_queries))
                print(No_of_queries)
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("Verifying if all the servers received the query or not")
                for i in new_ip:
                        if (i in output1):
                                if (re.findall(r'\b2\d{2}\b', output1)) or (re.findall(r'\b3\d{2}\b', output1)):
                                       assert True
                                       print("Pattern match for number of queries are seen in server %s" % (i))
                                else:
                                       print("Patterns doesn't match for the queries in %s server" % (i))
                                       assert False
                        else:
                                print("Server %s doesn't match for the query sent" % (i))
                                assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 23 Execution Completed")

        @pytest.mark.run(order=24)
        def test_024_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                print(output1)
                new_ip=Server_ip[:20]
                total_expected_queries=int(5000)
                logging.info("Checking total number of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                for i in queries:
                    i = i.strip(" ").split(" ")[0]
                    No_of_queries.append(int(i))
                No_of_queries=list(filter(None, No_of_queries))
                print(No_of_queries)
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("Verifying if all the servers received the query or not")
                for i in new_ip:
                        if (i in output1):
                                if (re.findall(r'\b2\d{2}\b', output1)) or (re.findall(r'\b3\d{2}\b', output1)):
                                       assert True
                                       print("Pattern match for number of queries are seen in server %s" % (i))
                                else:
                                       print("Patterns doesn't match for the queries in %s server" % (i))
                                       assert False
                        else:
                                print("Server %s doesn't match for the query sent" % (i))
                                assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 24 Execution Completed")
        

        @pytest.mark.run(order=25)
        def test_025_Modify_the_pool_lb_method_to_global_availabilty(self):
                logging.info("********** Modifying the pool to lb method to global availabilty ************")
                logging.info("Getting the server name reference ")
                server_ref = []
                for i in Server_name:
                        response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                        response_servers = json.loads(response_servers)
                        ref = response_servers[0]['_ref']
                        server_ref.append(ref)
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                ref1 = json.loads(response)
                ref1 = ref1[0]['_ref']
                All_the_Server=[]
                server_dict={}
                for i in server_ref:
                        server_dict['ratio']=1
                        server_dict['server']=i
                        All_the_Server.append(server_dict)
                        server_dict={}
                data = {"name": "DTC_Sample_pool", "lb_preferred_method": "GLOBAL_AVAILABILITY", "servers": All_the_Server, "monitors": ["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"]}
                print(data)
                response = ib_NIOS.wapi_request('PUT',object_type=ref1, fields=json.dumps(data))
                response = json.loads(response)
                print(response)
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
                logging.info("Test Case 25 Execution Completed")

        @pytest.mark.run(order=26)
        def test_026_Validation_of_lb_method_to_global_availabilty(self):
                logging.info("********** Validation of lb method to global availabilty ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=lb_preferred_method')
                response1 = json.loads(response1)
                print(response1)
                ref1 = response1['lb_preferred_method']
                if ref1 == "GLOBAL_AVAILABILITY":
                        assert True
                        print("Modified changes are reflecting")
                else:
                        print("Modified changes are not reflecting")
                        assert False
                logging.info("Test Case 26 Execution Completed")


        @pytest.mark.run(order=27)
        def test_027_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                print(output1)
                new_ip=Server_ip[:20]
                if ("5000" in output1) and (new_ip[0] in output1):
                        assert True
                        print("5000 queries are seen in %s server" % (new_ip[0]))
                else:
                        print("queries doesn't match in %s server" % (new_ip[0]))
                        assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 27 Execution Completed")


        @pytest.mark.run(order=28)
        def test_028_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                print(output1)
                new_ip=Server_ip[:20]
                if ("5000" in output1) and (new_ip[0] in output1):
                        assert True
                        print("5000 queries are seen in %s server" % (new_ip[0]))
                else:
                        print("queries doesn't match in %s server" % (new_ip[0]))
                        assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 28 Execution Completed")


        @pytest.mark.run(order=29)
        def test_029_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                print(output1)
                new_ip=Server_ip[:20]
                if ("5000" in output1) and (new_ip[0] in output1):
                        assert True
                        print("5000 queries are seen in %s server" % (new_ip[0]))
                else:
                        print("queries doesn't match in %s server" % (new_ip[0]))
                        assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 29 Execution Completed")


        @pytest.mark.run(order=30)
        def test_030_drop_one_server_from_grid_master_and_members(self):
                logging.info("********** Drop one server from the grid master and members ************")
                new_list = [config.grid_master_vip, config.grid_member1_vip, config.grid_member2_vip]
                for i in Server_ip[:1]:
                        for j in new_list:
                                add_server = "iptables -I INPUT -s "+i+" -j DROP"
                                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+j)
                                child.logfile=sys.stdout
                                child.expect('#')
                                child.sendline(add_server)
                                child.expect('#')
                                child.close()
                                sleep(60)
                logging.info("Test Case 30 Execution Completed")


        @pytest.mark.run(order=31)
        def test_031_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                if ("5000" in output1) and (new_ip[1] in output1):
                        assert True
                        print("5000 queries are seen in %s server" % (new_ip[1]))
                else:
                        print("queries doesn't match in %s server" % (new_ip[1]))
                        assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 31 Execution Completed")


        @pytest.mark.run(order=32)
        def test_032_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                if ("5000" in output1) and (new_ip[1] in output1):
                        assert True
                        print("5000 queries are seen in %s server" % (new_ip[1]))
                else:
                        print("queries doesn't match in %s server" % (new_ip[1]))
                        assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 32 Execution Completed")


        @pytest.mark.run(order=33)
        def test_033_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                if ("5000" in output1) and (new_ip[1] in output1):
                        assert True
                        print("5000 queries are seen in %s server" % (new_ip[1]))
                else:
                        print("queries doesn't match in %s server" % (new_ip[1]))
                        assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 33 Execution Completed")

        @pytest.mark.run(order=34)
        def test_034_Add_one_server_which_was_dropped_from_grid_master_and_members(self):
                logging.info("********** Add one server which was dropped from the grid master and members ************")
                new_list = [config.grid_master_vip, config.grid_member1_vip, config.grid_member2_vip]
                for i in Server_ip[:1]:
                        for j in new_list:
                                add_server = "iptables -I INPUT -s "+i+" -j ACCEPT"
                                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+j)
                                child.logfile=sys.stdout
                                child.expect('#')
                                child.sendline(add_server)
                                child.expect('#')
                                child.close()
                                sleep(60)
                logging.info("Test Case 34 Execution Completed")
 

        @pytest.mark.run(order=35)
        def test_035_Modify_the_pool_lb_method_to_ratio_fixed(self):
                logging.info("********** Modifying the pool to lb method to ratio fixed ************")
                logging.info("Getting the server name reference ")
                server_ref = []
                for i in Server_name:
                        response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                        response_servers = json.loads(response_servers)
                        ref = response_servers[0]['_ref']
                        server_ref.append(ref)
                #print(server_ref)
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                ref1 = json.loads(response)
                ref1 = ref1[0]['_ref']
                All_the_Server=[]
                server_dict={}
                for i in server_ref:
                        server_dict['ratio']=1
                        server_dict['server']=i
                        All_the_Server.append(server_dict)
                        server_dict={}
                #print(server_dict)
                logging.info("********** Updating new ratio values for few servers in All_the_Server list ************")
                count = 0
                for i in All_the_Server:
                    if count > 3:
                        break
                    if "server0" in i['server']:
                        i['ratio'] = 6
                    if "server1" in i['server']:
                        i['ratio'] = 5
                    if "server2" in i['server']:
                        i['ratio'] = 3
                    if "server3" in i['server']:
                        i['ratio'] = 2
                    count = count+1
                print(All_the_Server)
                data = {"name": "DTC_Sample_pool", "lb_preferred_method": "RATIO", "servers": All_the_Server[:4], "monitors": ["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"]}
                print(data)
                response = ib_NIOS.wapi_request('PUT',object_type=ref1, fields=json.dumps(data))
                response = json.loads(response)
                print(response)
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
                logging.info("Test Case 35 Execution Completed")


        @pytest.mark.run(order=36)
        def test_036_Validation_of_lb_method_to_ratio_fixed(self):
                logging.info("********** Validation of lb method to ratio fixed ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=lb_preferred_method')
                response1 = json.loads(response1)
                print(response1)
                ref1 = response1['lb_preferred_method']
                if ref1 == "RATIO":
                        assert True
                        print("Modified changes are reflecting")
                else:
                        print("Modified changes are not reflecting")
                        assert False
                logging.info("Test Case 36 Execution Completed")


        @pytest.mark.run(order=37)
        def test_037_Validation_of_ratio_values_that_are_updated(self):
                logging.info("********** Validation of ratio values changes ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=servers')
                response1 = json.loads(response1)
                response1 = response1['servers']
                print(response1)
                count = 0
                for i in response1:
                    if count > 3:
                        break
                    if i['ratio'] == int(6):
                        assert True
                        print("Ratio updated for first server succesfully")
                    elif i['ratio'] == int(5):
                        assert True
                        print("Ratio updated for second server succesfully")
                    elif i['ratio'] == int(3):
                        assert True
                        print("Ratio updated for third server succesfully")
                    elif i['ratio'] == int(2):
                        assert True
                        print("Ratio updated for fourth server succesfully")
                    else:
                        assert False
                        print("Ratio updation failed for one of the servers")
                    count = count+1
                logging.info("Test Case 37 Execution Completed")


        @pytest.mark.run(order=38)
        def test_038_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:4]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                for i in queries:
                    i = i.strip(" ").split(" ")[0]
                    No_of_queries.append(int(i))
                No_of_queries=list(filter(None, No_of_queries))
                print(No_of_queries)
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("*********** Validating how much queries each server received ***********")
                output2 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc > test.log").read()
                with open(r"test.log",'r') as file:
                     for i in file:
                         i=i.strip().split(" ")
                         if((int(i[0]) < 2000) and (i[1]==new_ip[0])):
                             assert True
                             print("Server %s received correct number of queries" % new_ip[0])
                         elif((int(i[0]) < 1700) and (i[1]==new_ip[1])):
                             assert True
                             print("Server %s received correct number of queries" % new_ip[1])
                         elif((int(i[0]) < 1000) and (i[1]==new_ip[2])):
                             assert True
                             print("Server %s received correct number of queries" % new_ip[2])
                         elif((int(i[0]) < 800) and (i[1]==new_ip[3])):
                             assert True
                             print("Server %s received correct number of queries" % new_ip[3])
                         else:
                             print("One of the server didn't receive correct number of queries")
                             assert False
                os.system('rm test.log')
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 38 Execution Completed")


        @pytest.mark.run(order=39)
        def test_039_Run_the_dig_command_with_5k_queries_on_grid_member1(self):
                logging.info("********** Run the dig command with 5k queries on grid member1 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:4]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                for i in queries:
                    i = i.strip(" ").split(" ")[0]
                    No_of_queries.append(int(i))
                No_of_queries=list(filter(None, No_of_queries))
                print(No_of_queries)
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                if Sum_of_queries == total_expected_queries:
                      assert True   
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("*********** Validating how much queries each server received ***********")
                output2 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc > test.log").read()
                with open(r"test.log",'r') as file:
                     for i in file:
                         i=i.strip().split(" ")
                         if((int(i[0]) < 2000) and (i[1]==new_ip[0])):
                             assert True
                             print("Server %s received correct number of queries" % new_ip[0])
                         elif((int(i[0]) < 1700) and (i[1]==new_ip[1])):
                             assert True
                             print("Server %s received correct number of queries" % new_ip[1])
                         elif((int(i[0]) < 1000) and (i[1]==new_ip[2])):
                             assert True
                             print("Server %s received correct number of queries" % new_ip[2])
                         elif((int(i[0]) < 800) and (i[1]==new_ip[3])):
                             assert True
                             print("Server %s received correct number of queries" % new_ip[3])
                         else:
                             print("One of the server didn't receive correct number of queries")
                             assert False
                os.system('rm test.log')
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 39 Execution Completed")


        @pytest.mark.run(order=40)
        def test_040_Run_the_dig_command_with_5k_queries_on_grid_member2(self):
                logging.info("********** Run the dig command with 5k queries on grid member2 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                for i in queries:
                    i = i.strip(" ").split(" ")[0]
                    No_of_queries.append(int(i))
                No_of_queries=list(filter(None, No_of_queries))
                print(No_of_queries)
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                if Sum_of_queries == total_expected_queries:
                      assert True   
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("*********** Validating how much queries each server received ***********")
                output2 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc > test.log").read()
                with open(r"test.log",'r') as file:
                     for i in file:
                         i=i.strip().split(" ")
                         if((int(i[0]) < 2000) and (i[1]==new_ip[0])):
                             assert True
                             print("Server %s received correct number of queries" % new_ip[0])
                         elif((int(i[0]) < 1700) and (i[1]==new_ip[1])):
                             assert True
                             print("Server %s received correct number of queries" % new_ip[1])
                         elif((int(i[0]) < 1000) and (i[1]==new_ip[2])):
                             assert True
                             print("Server %s received correct number of queries" % new_ip[2])
                         elif((int(i[0]) < 800) and (i[1]==new_ip[3])):
                             assert True
                             print("Server %s received correct number of queries" % new_ip[3])
                         else:
                             print("One of the server didn't receive correct number of queries")
                             assert False
                os.system('rm test.log')
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 40 Execution Completed")



        @pytest.mark.run(order=41)
        def test_041_Add_new_topology_rule_for_the_pool(self):
                logging.info("********** Add new topology rule for the pool ************")
                logging.info("Getting the server name reference ")
                server_ref = []
                for i in Server_name:
                        response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                        response_servers = json.loads(response_servers)
                        ref = response_servers[0]['_ref']
                        server_ref.append(ref)
                data = {"name": "DTC_Sample_Topology", "rules": [{"sources": [{"source_op": "IS","source_type": "SUBNET","source_value": "10.0.0.0/8"}], "dest_type": "SERVER","destination_link": server_ref[0]}]}
                response = ib_NIOS.wapi_request('POST',object_type='dtc:topology', fields=json.dumps(data))
                print(response)
                assert re.search(r'dtc:topology', response)
                logging.info("Test Case 41 Execution Completed")

        @pytest.mark.run(order=42)
        def test_042_Validation_of_topology_rule_created(self):
                logging.info("********** Validation of topology rule created ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=DTC_Sample_Topology')
                print(response)
                response = json.loads(response)
                print(response)
                response = response[0]['name']
                if response == "DTC_Sample_Topology":
                    assert True
                    print("DTC topology created successfully")
                else:
                    print("DTC topology is not created")
                    assert False
                logging.info("Test Case 42 Execution Completed")


        @pytest.mark.run(order=43)
        def test_043_Add_All_the_20_servers_back(self):
                logging.info("********** Add all the 20 servers back ************")
                server_ref = []
                for i in Server_name:
                        response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                        response_servers = json.loads(response_servers)
                        ref = response_servers[0]['_ref']
                        server_ref.append(ref)
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                ref1 = json.loads(response)
                ref1 = ref1[0]['_ref']
                All_the_Server=[]
                server_dict={}
                for i in server_ref:
                        server_dict['ratio']=1
                        server_dict['server']=i
                        All_the_Server.append(server_dict)
                        server_dict={}
                data = {"servers": All_the_Server}
                print(data)
                response = ib_NIOS.wapi_request('PUT',object_type=ref1, fields=json.dumps(data))
                response = json.loads(response)
                print(response)
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
                logging.info("Test Case 43 Execution Completed")

        @pytest.mark.run(order=44)
        def test_044_Modify_the_lb_prefered_method_to_source_ip_hash(self):
                logging.info("********** Modify the lb prefered method to source ip hash ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                ref1 = json.loads(response)
                ref1 = ref1[0]['_ref']
                data = {"lb_preferred_method": "SOURCE_IP_HASH"}
                response = ib_NIOS.wapi_request('PUT',object_type=ref1, fields=json.dumps(data))
                response = json.loads(response)
                print(response)
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
                logging.info("Test Case 44 Execution Completed")


        @pytest.mark.run(order=45)
        def test_045_Validation_of_lb_prefered_method_to_source_ip_hash(self):
                logging.info("********** Validation of lb prefered method to source ip hash ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                print(response)
                response = json.loads(response)
                print(response)
                ref = response[0]['_ref']
                response = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=lb_preferred_method')
                response = json.loads(response)
                ref1 = response['lb_preferred_method']
                if ref1 == "SOURCE_IP_HASH":
                    assert True
                    print("LB Preferred method modified to Source IP hash")
                else:
                    print("LB Preferred method modification to Source IP hash failed")
                    assert False
                logging.info("Test Case 45 Execution Completed")


        @pytest.mark.run(order=46)
        def test_046_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                queries = output1.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                global Server_That_Responded_First
                Server_That_Responded_First=queries[0].strip(" ").split(" ")[1]
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded_First)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded_First)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 46 Execution Completed")


        @pytest.mark.run(order=47)
        def test_047_Run_the_dig_command_with_5k_queries_on_grid_member1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                queries = output1.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                global Server_That_Responded_First
                Server_That_Responded_First=queries[0].strip(" ").split(" ")[1]
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded_First)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded_First)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 46 Execution Completed")

        
        @pytest.mark.run(order=48)
        def test_048_Run_the_dig_command_with_5k_queries_on_grid_member2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                queries = output1.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                global Server_That_Responded_First
                Server_That_Responded_First=queries[0].strip(" ").split(" ")[1]
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded_First)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded_First)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 48 Execution Completed")


        @pytest.mark.run(order=49)
        def test_049_Drop_the_responded_server_from_the_grid_master(self):
                logging.info("********** Drop the responded server from the grid master ************")
                global Server_That_Responded_First
                print("Dropping the server %s on master grid" % Server_That_Responded_First)
                drop_server = "iptables -I INPUT -s "+Server_That_Responded_First+" -j DROP"
                print(drop_server)
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_master_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline(drop_server)
                child.expect('#')
                child.close()
                sleep(60)
                logging.info("Test Case 49 Execution Completed")


        @pytest.mark.run(order=50)
        def test_050_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                queries = output1.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                global Server_That_Responded_First
                Server_That_Responded_After_Drop=queries[0].strip(" ").split(" ")[1]
                logging.info("********** Validation of servers whether different server responded since the server responded last is down in grid master ************")
                if Server_That_Responded_First != Server_That_Responded_After_Drop:
                    assert True
                    print("Server %s Responded to query since first responded server is down on grid master" % Server_That_Responded_After_Drop)
                else:
                    print("Server %s didn't drop on the master grid hence getting query on the same" % Server_That_Responded_First)
                    assert False
                logging.info("Validation of number of count of queries")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded_After_Drop)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded_After_Drop)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 50 Execution Completed")


        @pytest.mark.run(order=51)
        def test_051_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                queries = output1.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                global Server_That_Responded_First
                Server_That_Responded_After_Drop=queries[0].strip(" ").split(" ")[1]
                logging.info("********** Validation of servers whether different server responded since the server responded last is down in grid master ************")
                if Server_That_Responded_First == Server_That_Responded_After_Drop:
                    assert True
                    print("Server %s Responded to query" % Server_That_Responded_After_Drop)
                else:
                    print("Server %s didn't respond to the query" % Server_That_Responded_After_Drop)
                    assert False
                logging.info("Validation of number of count of queries")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded_After_Drop)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded_After_Drop)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 51 Execution Completed")


        @pytest.mark.run(order=52)
        def test_052_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                queries = output1.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                global Server_That_Responded_First
                Server_That_Responded_After_Drop=queries[0].strip(" ").split(" ")[1]
                logging.info("********** Validation of servers whether different server responded since the server responded last is down in grid master ************")
                if Server_That_Responded_First == Server_That_Responded_After_Drop:
                    assert True
                    print("Server %s Responded to query" % Server_That_Responded_After_Drop)
                else:
                    print("Server %s didn't respond to the query" % Server_That_Responded_After_Drop)
                    assert False
                logging.info("Validation of number of count of queries")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded_After_Drop)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded_After_Drop)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 52 Execution Completed")


        @pytest.mark.run(order=53)
        def test_053_Accept_the_server_which_was_removed_from_the_grid_master(self):
                logging.info("********** Accept the server which was removed from the grid master ************")
                global Server_That_Responded_First
                print("Adding the server %s on master grid" % Server_That_Responded_First)
                add_server = "iptables -I INPUT -s "+Server_That_Responded_First+" -j ACCEPT"
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_master_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline(add_server)
                child.expect('#')
                child.close()
                sleep(60)
                logging.info("Test Case 53 Execution Completed")


        @pytest.mark.run(order=54)
        def test_054_Enable_Auto_Consolidated_Monitors_in_the_pool(self):
                logging.info("********* Enabling Auto Consolidated Monitors in the pool *********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref = response[0]['_ref']
                data={"auto_consolidated_monitors": True}
                response1 = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
                print(response1)
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
                logging.info("Test Case 54 Execution Completed")


        @pytest.mark.run(order=55)
        def test_055_Validation_of_Auto_Consolidated_Monitors_in_the_pool(self):
                logging.info("********** Validation of Auto consolidated monitors in the pool ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                print(response)
                response = json.loads(response)
                print(response)
                ref = response[0]['_ref']
                response = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=auto_consolidated_monitors')
                response = json.loads(response)
                ref1 = response['auto_consolidated_monitors']
                if ref1 == True:
                    assert True
                    print("Auto consolidated montiors has been enabled")
                else:
                    print("Auto consolidated montiors has not been enabled")
                    assert False
                logging.info("Test Case 55 Execution Completed")


        @pytest.mark.run(order=56)
        def test_056_Validation_of_whether_master_and_members_are_part_of_consolidated_monitors_after_enabling_Auto_Consolidated_Monitors(self):
                logging.info("********** Validation of whether master and members are part of consolidated monitors after enabling auto consolidated monitors ************")
                list_of_master_and_members=[config.grid_member_fqdn, config.grid_member1_fqdn, config.grid_member2_fqdn]
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=consolidated_monitors')
                response1 = json.loads(response1)
                response1 = response1['consolidated_monitors'][0]['members']
                print(response1)
                if list_of_master_and_members == response1:
                    assert True
                    print("All the Master and members are present in consolidated monitors")
                else:
                    print("All the Master and members are not present in consolidated monitors")
                    assert False
                logging.info("Test Case 56 Execution Completed")


        @pytest.mark.run(order=57)
        def test_057_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                global Server_That_Responded_For_Master
                Server_That_Responded_For_Master=queries[0].strip(" ").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded_For_Master)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded_For_Master)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 57 Execution Completed")


        @pytest.mark.run(order=58)
        def test_058_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid memeber 1 ************")
                output_member1 = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1_member1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                queries = output1_member1.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                global Server_That_Responded_For_Member_1
                Server_That_Responded_For_Member_1=queries[0].strip(" ").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded_For_Member_1)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded_For_Member_1)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 58 Execution Completed")


        @pytest.mark.run(order=59)
        def test_059_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid memeber 2 ************")
                output_member2 = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1_member2 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                queries = output1_member2.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                global Server_That_Responded_For_Member_2
                Server_That_Responded_For_Member_2=queries[0].strip(" ").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded_For_Member_2)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded_For_Member_2)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 59 Execution Completed")


        @pytest.mark.run(order=60)
        def test_060_Validation_for_the_Server_responded_for_queries_sent_to_master_and_members(self):
                logging.info("********** Validation for the server responded for queries sent to master and members ************")
                global Server_That_Responded_For_Master
                global Server_That_Responded_For_Member_1
                global Server_That_Responded_For_Member_2
                new_list=[Server_That_Responded_For_Member_1, Server_That_Responded_For_Member_2]
                for i in new_list:
                    if i == Server_That_Responded_For_Master:
                        assert True
                        print("Same Server responded for all master and members")
                    else:
                        print("Different Server responded for all master and members")
                        assert False
                logging.info("Test Case 60 Execution Completed")


        @pytest.mark.run(order=61)
        def test_061_Disable_Auto_Consolidated_Monitors_in_the_pool(self):
                logging.info("********* Enabling Auto Consolidated Monitors in the pool *********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref = response[0]['_ref']
                data={"auto_consolidated_monitors": False}
                response1 = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
                print(response1)
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
                logging.info("Test Case 61 Execution Completed")

        
        @pytest.mark.run(order=62)
        def test_062_Mofify_the_pool_lb_method_to_round_robin(self):
                logging.info("********* Modify the pool lb method to round robin *********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref = response[0]['_ref']
                data={"lb_preferred_method": "ROUND_ROBIN"}
                response1 = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
                print(response1)
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
                logging.info("Test Case 62 Execution Completed")


        @pytest.mark.run(order=63)
        def test_063_Validation_of_pool_lb_method_to_round_robin(self):
                logging.info("********** Validation of Auto consolidated monitors in the pool ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref = response[0]['_ref']
                response = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=lb_preferred_method')
                response = json.loads(response)
                ref1 = response['lb_preferred_method']
                print(ref1)
                if ref1 == "ROUND_ROBIN":
                        assert True
                        print("Modified changes are reflecting")
                else:
                        print("Modified changes are not reflecting")
                        assert False
                logging.info("Test Case 63 Execution Completed")


        @pytest.mark.run(order=64)
        def test_064_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                for i in queries:
                    a = i.strip(" ").split(" ")[0]
                    No_of_queries.append(int(a))
                print(No_of_queries)
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                logging.info("******** Validating total no of queries *********")
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("******** Validating whether each server receieved same count *********")
                for i in No_of_queries:
                    if i == 250:
                        assert True
                        print("Each server received the equal no of count %s" % i)
                    else:
                        print("Each server didn't receice the equal no of count")
                        assert False
                logging.info("******** Validating whether all the servers responded or not *********")
                for i in new_ip:
                    if (i in output1):
                        assert True
                        print("Server %s responded to the query" % i)
                    else:
                        print("Server %s didn't respond to the query" % i)
                        assert False
                logging.info("Test Case 64 Execution Completed")


        @pytest.mark.run(order=65)
        def test_065_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                for i in queries:
                    a = i.strip(" ").split(" ")[0]
                    No_of_queries.append(int(a))
                print(No_of_queries)
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                logging.info("******** Validating total no of queries *********")
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      assert False
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                logging.info("******** Validating whether each server receieved same count *********")
                for i in No_of_queries:
                    if i == 250:
                        assert True
                        print("Each server received the equal no of count %s" % i)
                    else:
                        print("Each server didn't receice the equal no of count")
                        assert False
                logging.info("******** Validating whether all the servers responded or not *********")
                for i in new_ip:
                    if (i in output1):
                        assert True
                        print("Server %s responded to the query" % i)
                    else:
                        print("Server %s didn't respond to the query" % i)
                        assert False
                logging.info("Test Case 65 Execution Completed")


        @pytest.mark.run(order=66)
        def test_066_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                for i in queries:
                    a = i.strip(" ").split(" ")[0]
                    No_of_queries.append(int(a))
                print(No_of_queries)
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                logging.info("******** Validating total no of queries *********")
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:      
                      assert False
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                logging.info("******** Validating whether each server receieved same count *********")
                for i in No_of_queries:
                    if i == 250:
                        assert True     
                        print("Each server received the equal no of count %s" % i)
                    else:
                        print("Each server didn't receice the equal no of count")
                        assert False
                logging.info("******** Validating whether all the servers responded or not *********")
                for i in new_ip:
                    if (i in output1):
                        assert True
                        print("Server %s responded to the query" % i)
                    else:
                        print("Server %s didn't respond to the query" % i)
                        assert False
                logging.info("Test Case 66 Execution Completed")


        @pytest.mark.run(order=67)
        def test_067_Modify_Consolidated_Monitors_in_the_pool_to_ANY_and_add_master_and_member_1(self):
                logging.info("********* Modify consolidated monitors in the pool to ANY and add master and member 1 *********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref = response[0]['_ref']
                data={"consolidated_monitors": [{"availability": "ANY", "full_health_communication": True, "members": [config.grid_member_fqdn, config.grid_member1_fqdn],"monitor": "dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"}]}
                response1 = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
                print(response1)
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
                logging.info("Test Case 67 Execution Completed")


        @pytest.mark.run(order=68)
        def test_068_Validation_of_whether_master_and_member1_are_part_of_consolidated_monitors_also_if_availability_is_set_to_ANY(self):
                logging.info("********** Validation of whether master and member1 are part of consolidated monitors and also if availabity is set to ANY ************")
                list_of_master_and_members=[config.grid_member_fqdn, config.grid_member1_fqdn]
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=consolidated_monitors')
                response1 = json.loads(response1)
                response_members = response1['consolidated_monitors'][0]['members']
                print(response_members)
                logging.info("******* Validation of master and member1 in consolidated monitors ********")
                if list_of_master_and_members == response_members:
                    assert True
                    print("Master and member1 are present in consolidated monitors")
                else:
                    print("Master and member1 are not present in consolidated monitors")
                    assert False
                logging.info("******* Validation if availability is set to ANY ********")
                response2 = response1['consolidated_monitors'][0]['availability']
                if response2 == "ANY":
                    assert True
                    print("Availability is set to %s" % response2)
                else:
                    print("Availability is not set to %s" % response2)
                    assert False
                logging.info("Test Case 68 Execution Completed")


        @pytest.mark.run(order=69)
        def test_069_Drop_ALL_the_servers_from_the_grid_member1(self):
                logging.info("********** Drop All the servers from the grid member1 ************")
                new_ip=Server_ip[:20]
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
                for i in new_ip:
                    drop_server = "iptables -I INPUT -s "+i+" -j DROP"
                    #print(drop_server)
                    child.logfile=sys.stdout
                    child.expect('#')
                    child.sendline(drop_server)
                    child.sendline('\n')
                    child.expect('#')
                    sleep(30)
                child.close()
                sleep(30)
                logging.info("Test Case 69 Execution Completed")


        @pytest.mark.run(order=70)
        def test_070_Validate_the_health_status_of_each_server_in_master_after_dropping_server_in_member1(self):
                logging.info("******** Validate the health status of each server in master after dropping server in member1 *********")
                logging.info("Getting the server name reference ")
                server_ref = []
                for i in Server_name:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    server_ref.append(ref)
                for i in server_ref:
                    response = ib_NIOS.wapi_request('GET',object_type=i, params='?_return_fields=health')
                    response = json.loads(response)
                    status = response['health']['availability']
                    if status == "GREEN":
                        assert True
                        print("Health status of Server %s is in GREEN state" % i)
                    else:
                        print("Health status of Server %s is in RED status" % i)
                        assert False
                logging.info("Test Case 70 Execution Completed")



        @pytest.mark.run(order=71)
        def test_071_Modify_Consolidated_Monitors_in_the_pool_to_ALL_and_having_only_master_and_member1(self):
                logging.info("********* Modify consolidated monitors in the pool to ALL and having only master and member 1 *********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref = response[0]['_ref']
                data={"consolidated_monitors": [{"availability": "ALL", "full_health_communication": True, "members": [config.grid_member_fqdn, config.grid_member1_fqdn],"monitor": "dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"}]}
                response1 = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
                print(response1)
                assert re.search(r'dtc:pool', response1)
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
                logging.info("Test Case 71 Execution Completed")


        @pytest.mark.run(order=72)
        def test_072_Validation_of_consolidated_monitors_if_availability_is_set_to_ALL(self):
                logging.info("********** Validation of consolidated monitors if availability is set to ALL ************")
                list_of_master_and_members=[config.grid_member_fqdn, config.grid_member1_fqdn]
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=consolidated_monitors')
                response1 = json.loads(response1)
                logging.info("******* Validation if availability is set to ANY ********")
                response2 = response1['consolidated_monitors'][0]['availability']
                if response2 == "ALL":
                    assert True
                    print("Availability is set to %s" % response2)
                else:
                    print("Availability is not set to %s" % response2)
                    assert False
                sleep(60)
                logging.info("Test Case 72 Execution Completed")


        @pytest.mark.run(order=73)
        def test_073_Validate_the_health_status_of_each_server_in_master_after_setting_availability_to_ALL(self):
                logging.info("******** Validate the health status of each server in master after setting availability to ALL *********")
                logging.info("Getting the server name reference ")
                server_ref = []
                for i in Server_name:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    server_ref.append(ref)
                logging.info("******* Validation if HEALTH status is RED********")
                for i in server_ref:
                    response = ib_NIOS.wapi_request('GET',object_type=i, params='?_return_fields=health')
                    response = json.loads(response)
                    status = response['health']['availability']
                    if status == "RED":
                        assert True
                        print("Health status of Server %s is in RED state" % i)
                    else:
                        print("Health status of Server %s is in GREEN status" % i)
                        assert False
                logging.info("Test Case 73 Execution Completed")


        @pytest.mark.run(order=74)
        def test_074_Modify_Consolidated_Monitors_in_the_pool_to_ALL_having_master_member1_and_member2(self):
                logging.info("********* Modify consolidated monitors in the pool to ALL having master member1 and member2 *********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref = response[0]['_ref']
                data={"consolidated_monitors": [{"availability": "ALL", "full_health_communication": True, "members": [config.grid_member_fqdn, config.grid_member1_fqdn, config.grid_member2_fqdn],"monitor": "dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"}]}
                response1 = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
                print(response1)
                assert (re.search(r'dtc:pool', response1))
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
                logging.info("Test Case 74 Execution Completed")


        @pytest.mark.run(order=75)
        def test_075_Add_ALL_the_servers_from_the_grid_member1(self):
                logging.info("********** Add All the servers from the grid member1 ************")
                new_ip=Server_ip[:20]
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
                for i in new_ip:
                    drop_server = "iptables -I INPUT -s "+i+" -j ACCEPT"
                    #print(drop_server)
                    child.logfile=sys.stdout
                    child.expect('#')
                    child.sendline(drop_server)
                    child.sendline('\n')
                    child.expect('#')
                    sleep(30)
                child.close()
                sleep(30)
                logging.info("Test Case 75 Execution Completed")


        @pytest.mark.run(order=76)
        def test_076_Validation_of_topology_rule_subnet_and_server_added(self):
                logging.info("********** Validation of topology rule subnet and server added ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=DTC_Sample_Topology')
                response = json.loads(response)
                response_name = response[0]['name']
                response_ref = response[0]['_ref']
                logging.info("******* Validation of DTC topology name **********")
                if response_name == "DTC_Sample_Topology":
                    assert True
                    print("DTC Topolgy %s Created sucessfully" % response_name)
                else:
                    print("DTC Topolgy %s is not created" % response_name)
                    assert False
                logging.info("******* Validation of rule configured **********")
                response1 = ib_NIOS.wapi_request('GET',object_type=response_ref, params='?_return_fields=rules')
                response1 = json.loads(response1)
                rule_ref = response1['rules'][0]['_ref']
                if "server0" in rule_ref:
                    assert True
                    print("DTC topology rule created successfully")
                else:
                    print("DTC topology rule creation failed")
                    assert False
                logging.info("******* Validation of subnet configured **********")
                response2 = ib_NIOS.wapi_request('GET',object_type=rule_ref, params='?_return_fields=sources')
                response2 = json.loads(response2)
                source_op = response2['sources'][0]['source_op']
                source_value = response2['sources'][0]['source_value']
                if (source_op == "IS") and (source_value == "10.0.0.0/8"):
                    assert True
                    print("Subnet value is updated")
                else:
                    print("Subnet value is not updated")
                    assert False
                logging.info("Test Case 76 Execution Completed")


        @pytest.mark.run(order=77)
        def test_077_Modify_the_lb_preferred_method_to_topology(self):
                logging.info("********* Getting the topology reference *********")
                response2 = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=DTC_Sample_Topology')
                response2 = json.loads(response2)
                response2_ref = response2[0]['_ref']
                logging.info("********* Modify the lb preferred method to topology *********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref = response[0]['_ref']
                data = {"lb_preferred_method": "TOPOLOGY", "lb_preferred_topology": response2_ref, "lb_alternate_method": "SOURCE_IP_HASH"}
                response1 = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
                print(response1)
                assert (re.search(r'dtc:pool', response1))
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
                logging.info("Test Case 77 Execution Completed")


        @pytest.mark.run(order=78)
        def test_078_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip(" ").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded == new_ip[0]:
                    assert True
                    print("Configured server %s responded to the query" % Server_That_Responded)
                else:
                    print("Different server responded to the query")
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 78 Execution Completed")


        @pytest.mark.run(order=79)
        def test_079_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip(" ").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded == new_ip[0]:
                    assert True
                    print("Configured server %s responded to the query" % Server_That_Responded)
                else:
                    print("Different server responded to the query")
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 79 Execution Completed")


        @pytest.mark.run(order=80)
        def test_080_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip(" ").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded == new_ip[0]:
                    assert True
                    print("Configured server %s responded to the query" % Server_That_Responded)
                else:
                    print("Different server responded to the query")
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 80 Execution Completed")


        @pytest.mark.run(order=81)
        def test_081_Enable_the_EDNS0_Client_Subnet_option(self):
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
                logging.info("Test Case 81 Execution Completed")


        @pytest.mark.run(order=82)
        def test_082_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com in a +subnet=20.10.2.0/24 +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip(" ").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded != new_ip[0]:
                    assert True
                    print("Configured server %s responded to the query" % Server_That_Responded)
                else:
                    print("Different server responded to the query")
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 82 Execution Completed")


        @pytest.mark.run(order=83)
        def test_083_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com in a +subnet=20.10.2.0/24 +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip(" ").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded != new_ip[0]:
                    assert True
                    print("Configured server %s responded to the query" % Server_That_Responded)
                else:
                    print("Different server responded to the query")
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 83 Execution Completed")


        @pytest.mark.run(order=84)
        def test_084_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com in a +subnet=20.10.2.0/24 +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip(" ").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded != new_ip[0]:
                    assert True
                    print("Configured server %s responded to the query" % Server_That_Responded)
                else:
                    print("Different server responded to the query")
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 84 Execution Completed")


        @pytest.mark.run(order=85)
        def test_085_Disable_the_EDNS0_Client_Subnet_option(self):
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
                logging.info("Test Case 85 Execution Completed") 


        @pytest.mark.run(order=86)
        def test_086_Modify_topology_rule_source_op_to_IS_NOT(self):
                logging.info("********** Add new topology rule for the pool ************")
                logging.info("Getting the server name reference ")
                server_ref = []
                for i in Server_name:
                        response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                        response_servers = json.loads(response_servers)
                        ref = response_servers[0]['_ref']
                        server_ref.append(ref)
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=DTC_Sample_Topology')
                response1 = json.loads(response1)
                response1 = response1[0]['_ref']
                data = {"rules": [{"sources": [{"source_op": "IS_NOT","source_type": "SUBNET","source_value": "10.0.0.0/8"}], "dest_type": "SERVER","destination_link": server_ref[0]}]}
                response = ib_NIOS.wapi_request('PUT',object_type=response1, fields=json.dumps(data))
                print(response)
                assert re.search(r'dtc:topology', response)
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
                logging.info("Test Case 86 Execution Completed")


        @pytest.mark.run(order=87)
        def test_087_Validation_of_topology_rule_for_source_op_IS_NOT(self):
                logging.info("********** Validation of soruce op whether IS_NOT is updated or not ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=DTC_Sample_Topology')
                response = json.loads(response)
                response_name = response[0]['name']
                response_ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=response_ref, params='?_return_fields=rules')
                response1 = json.loads(response1)
                rule_ref = response1['rules'][0]['_ref']
                logging.info("******* Validation of source_op **********")
                response2 = ib_NIOS.wapi_request('GET',object_type=rule_ref, params='?_return_fields=sources')
                response2 = json.loads(response2)
                source_op = response2['sources'][0]['source_op']
                source_value = response2['sources'][0]['source_value']
                if (source_op == "IS_NOT") and (source_value == "10.0.0.0/8"):
                    assert True
                    print("source_op value is updated")
                else:
                    print("source_op is not updated")
                    assert False
                logging.info("Test Case 87 Execution Completed")


        @pytest.mark.run(order=88)
        def test_088_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip(" ").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded != new_ip[0]:
                    assert True
                    print("Different server %s responded to the query" % Server_That_Responded)
                else:
                    print("Same server responded to the query")
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 88 Execution Completed")


        @pytest.mark.run(order=89)
        def test_089_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip(" ").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded != new_ip[0]:
                    assert True
                    print("Different server %s responded to the query" % Server_That_Responded)
                else:
                    print("Same server responded to the query")
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 89 Execution Completed")


        @pytest.mark.run(order=90)
        def test_090_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip(" ").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded != new_ip[0]:
                    assert True
                    print("Different server %s responded to the query" % Server_That_Responded)
                else:
                    print("Same server responded to the query")
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 85 Execution Completed")


        @pytest.mark.run(order=91)
        def test_091_Add_the_default_destination_server_to_topology_rule(self):
                logging.info("********** Adding new default destination server to the topology rule ************")
                logging.info("Getting the server name reference ")
                server_ref = []
                for i in Server_name:
                        response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                        response_servers = json.loads(response_servers)
                        ref = response_servers[0]['_ref']
                        server_ref.append(ref)
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=DTC_Sample_Topology')
                response1 = json.loads(response1)
                response1 = response1[0]['_ref']
                data = {"rules": [{"sources": [{"source_op": "IS_NOT","source_type": "SUBNET","source_value": "10.0.0.0/8"}], "dest_type": "SERVER","destination_link": server_ref[0]}, {"sources":[],"dest_type": "SERVER","destination_link": server_ref[1]}]}
                response = ib_NIOS.wapi_request('PUT',object_type=response1, fields=json.dumps(data))
                print(response)
                assert re.search(r'dtc:topology', response)
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
                logging.info("Test Case 91 Execution Completed")

     
        @pytest.mark.run(order=92)
        def test_092_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip(" ").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded == new_ip[1]:
                    assert True
                    print("Default destination server %s responded to the query" % Server_That_Responded)
                else:
                    print("Default destination server %s didn't responde to the query" % Server_That_Responded)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 92 Execution Completed")


        @pytest.mark.run(order=93)
        def test_093_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip(" ").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded == new_ip[1]:
                    assert True
                    print("Default destination server %s responded to the query" % Server_That_Responded)
                else:
                    print("Default destination server %s didn't responde to the query" % Server_That_Responded)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 93 Execution Completed")


        @pytest.mark.run(order=94)
        def test_094_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip(" ").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded == new_ip[1]:
                    assert True
                    print("Default destination server %s responded to the query" % Server_That_Responded)
                else:
                    print("Default destination server %s didn't responde to the query" % Server_That_Responded)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 94 Execution Completed") 


        @pytest.mark.run(order=95)
        def test_095_Create_second_pool_and_assign_two_servers(self):
                logging.info("Getting the server name reference")
                server_ref = []
                for i in Server_name:
                        response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                        response_servers = json.loads(response_servers)
                        ref = response_servers[0]['_ref']
                        server_ref.append(ref)
                logging.info("***** Creating the pool and assiging the server ******")
                data = {"name": "DTC_Sample_pool_2", "lb_preferred_method": "RATIO", "servers": [{"ratio": 1,"server": str(server_ref[0])}, {"ratio": 1,"server": str(server_ref[1])}], "monitors": ["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"]}
                response_servers = ib_NIOS.wapi_request('POST',object_type='dtc:pool', fields=json.dumps(data))
                ref1 = json.loads(response_servers)
                print(ref1)
                logging.info("Validation of Pool creation")
                assert re.search(r'dtc:pool', ref1)
                logging.info("DTC Pool 2 has been created successfully")
                logging.info("Test Case 95 Execution Completed")


        @pytest.mark.run(order=96)
        def test_096_Validation_of_second_pool_creation(self):
                logging.info("Getting the server name reference")
                server_ref = []
                for i in Server_name:
                        response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                        response_servers = json.loads(response_servers)
                        ref = response_servers[0]['_ref']
                        server_ref.append(ref)
                logging.info("Validation of second pool")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool_2')
                response = json.loads(response)
                response_ref = response[0]['_ref']
                response_name = response[0]['name']
                if response_name == "DTC_Sample_pool_2":
                    assert True
                    print("%s pool created successfully" % response_name)
                else:
                    print("%s pool not created successfully" % response_name)
                    assert False
                logging.info("Validation of servers added in the pool")
                response1 = ib_NIOS.wapi_request('GET',object_type=response_ref, params='?_return_fields=servers')
                response1 = json.loads(response1)
                response1_server1 = response1['servers'][0]['server']
                response1_server2 = response1['servers'][1]['server']
                if (response1_server1 == server_ref[0]) and (response1_server2 == server_ref[1]):
                    assert True
                    print("Both the servers are added successfully")
                else:
                    print("Server validation failed for the new pool created")
                    assert False
                logging.info("Validation of pool LB method")
                response2 = ib_NIOS.wapi_request('GET',object_type=response_ref, params='?_return_fields=lb_preferred_method')
                response2 = json.loads(response2)
                response2 = response2['lb_preferred_method']
                if response2 == "RATIO":
                    assert True
                    print("LB method updated successfully")
                else:
                    print(" LB method not updated successfully")
                    assert False
                logging.info("Test Case 96 Execution Completed")


        @pytest.mark.run(order=97)
        def test_097_Modify_the_pool_1_lb_method_to_global_availabilty(self):
                logging.info("********** Modifying the pool to lb method to global availabilty ************")
                logging.info("Getting the server name reference ")
                server_ref = []
                for i in Server_name:
                        response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                        response_servers = json.loads(response_servers)
                        ref = response_servers[0]['_ref']
                        server_ref.append(ref)
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                ref1 = json.loads(response)
                ref1 = ref1[0]['_ref']
                data = {"name": "DTC_Sample_pool", "lb_preferred_method": "GLOBAL_AVAILABILITY", "servers": [{"ratio": 1,"server": str(server_ref[2])}, {"ratio": 1,"server": str(server_ref[3])}]}
                print(data)
                response = ib_NIOS.wapi_request('PUT',object_type=ref1, fields=json.dumps(data))
                response = json.loads(response)
                print(response)
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
                logging.info("Test Case 97 Execution Completed")


        @pytest.mark.run(order=98)
        def test_098_Validation_of_pool1_changes_to_global_availability(self):
                logging.info("Getting the server name reference ")
                server_ref = []
                for i in Server_name:
                        response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                        response_servers = json.loads(response_servers)
                        ref = response_servers[0]['_ref']
                        server_ref.append(ref)
                logging.info("Validation of pool one")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                response_ref = response[0]['_ref']
                logging.info("Validation of servers added in the pool1")
                response1 = ib_NIOS.wapi_request('GET',object_type=response_ref, params='?_return_fields=servers')
                response1 = json.loads(response1)
                response1_server1 = response1['servers'][0]['server']
                response1_server2 = response1['servers'][1]['server']
                if (response1_server1 == server_ref[2]) and (response1_server2 == server_ref[3]):
                    assert True
                    print("Both the servers are added successfully")
                else:
                    print("Server validation failed for the new pool created")
                    assert False
                logging.info("Validation of pool LB method")
                response2 = ib_NIOS.wapi_request('GET',object_type=response_ref, params='?_return_fields=lb_preferred_method')
                response2 = json.loads(response2)
                response2 = response2['lb_preferred_method']
                if response2 == "GLOBAL_AVAILABILITY":
                    assert True
                    print("LB method updated successfully")
                else:
                    print(" LB method not updated successfully")
                    assert False
                logging.info("Test Case 98 Execution Completed")


        @pytest.mark.run(order=99)
        def test_099_Modify_the_lbdn_and_add_second_pool(self):
                logging.info("********** Creation of LBDN ************")
                logging.info("********** Getting the ref of pool ************")
                pool_list = ["DTC_Sample_pool", "DTC_Sample_pool_2"]
                pool_ref=[]
                for i in pool_list:
                     response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name='+i)
                     response = json.loads(response)
                     ref_pool = response[0]['_ref']
                     pool_ref.append(ref_pool)
                logging.info("********** Getting the ref of LBDN ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=DTC_LBDN')
                response = json.loads(response)
                ref_lbdn = response[0]['_ref']
                logging.info("**********  Adding the second pool in the LBDN ************")
                data = {"lb_method": "ROUND_ROBIN", "pools": [{"ratio": 1, "pool": pool_ref[0]}, {"ratio": 1, "pool": pool_ref[1]}]}
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
                logging.info("Test Case 99 Execution Completed")



        @pytest.mark.run(order=100)
        def test_100_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                Servers=[]
                for i in queries:
                    a = i.strip(" ").split(" ")[0]
                    b = i.strip(" ").split(" ")[1]
                    No_of_queries.append(int(a))
                    Servers.append(b)
                No_of_queries=list(filter(None, No_of_queries))
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("*********** Validating how many queries pool 2 received***********")
                if (sum(No_of_queries[:2]) == int(2500)) and (Servers[:2] == new_ip[:2]):
                    assert True
                    print("Pool 2 Responded with Fixed Ratio method using %s and %s servers " % (Servers[0], Servers[1]))
                else:
                    print("%s and %s servers from Pool 2 failed to respond with fixed ratio method")
                    assert False
                logging.info("*********** Validating how many queries pool 1 received***********")
                if ((No_of_queries[2]) == int(2500)) and (Servers[2] == new_ip[2]):
                    assert True
                    print("Pool 1 Responded with GLOBAL AVAILABILITY method using %s server " % Servers[2])
                else:
                    print("%s server from pool 1 failed to respond with GLOBAL AVAILABILITY method" % Servers[2])
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 100 Execution Completed")


        @pytest.mark.run(order=101)
        def test_101_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                Servers=[]
                for i in queries:
                    a = i.strip(" ").split(" ")[0]
                    b = i.strip(" ").split(" ")[1]
                    No_of_queries.append(int(a))
                    Servers.append(b)
                No_of_queries=list(filter(None, No_of_queries))
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("*********** Validating how many queries pool 2 received***********")
                if (sum(No_of_queries[:2]) == int(2500)) and (Servers[:2] == new_ip[:2]):
                    assert True
                    print("Pool 2 Responded with Fixed Ratio method using %s and %s servers " % (Servers[0], Servers[1]))
                else:
                    print("%s and %s servers from Pool 2 failed to respond with fixed ratio method")
                    assert False
                logging.info("*********** Validating how many queries pool 1 received***********")
                if ((No_of_queries[2]) == int(2500)) and (Servers[2] == new_ip[2]):
                    assert True
                    print("Pool 1 Responded with GLOBAL AVAILABILITY method using %s server " % Servers[2])
                else:
                    print("%s server from pool 1 failed to respond with GLOBAL AVAILABILITY method" % Servers[2])
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 101 Execution Completed")


        @pytest.mark.run(order=102)
        def test_102_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                Servers=[]
                for i in queries:
                    a = i.strip(" ").split(" ")[0]
                    b = i.strip(" ").split(" ")[1]
                    No_of_queries.append(int(a))
                    Servers.append(b)
                No_of_queries=list(filter(None, No_of_queries))
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("*********** Validating how many queries pool 2 received***********")
                if (sum(No_of_queries[:2]) == int(2500)) and (Servers[:2] == new_ip[:2]):
                    assert True
                    print("Pool 2 Responded with Fixed Ratio method using %s and %s servers " % (Servers[0], Servers[1]))
                else:
                    print("%s and %s servers from Pool 2 failed to respond with fixed ratio method")
                    assert False
                logging.info("*********** Validating how many queries pool 1 received***********")
                if ((No_of_queries[2]) == int(2500)) and (Servers[2] == new_ip[2]):
                    assert True
                    print("Pool 1 Responded with GLOBAL AVAILABILITY method using %s server " % Servers[2])
                else:
                    print("%s server from pool 1 failed to respond with GLOBAL AVAILABILITY method" % Servers[2])
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 102 Execution Completed")


        @pytest.mark.run(order=103)
        def test_103_Modify_the_lb_method_of_LBDN_to_Global_Availability(self):
                logging.info("************* Modify the LB method of LBDN to Global Availability ************") 
                logging.info("********** Getting the ref of LBDN ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=DTC_LBDN')
                response = json.loads(response)
                ref_lbdn = response[0]['_ref']
                logging.info("**********  Modify the LB method of LBDN to Global Availability ************")
                data = {"lb_method": "GLOBAL_AVAILABILITY"}
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
                logging.info("Test Case 103 Execution Completed")



        @pytest.mark.run(order=104)
        def test_104_Validation_of_the_lb_method_of_LBDN_to_Global_Availability(self):
                logging.info("********** Getting the ref of LBDN ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=DTC_LBDN')
                response = json.loads(response)
                ref_lbdn = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref_lbdn, params='?_return_fields=lb_method')
                response1 = json.loads(response1)
                res_lb_method = response1['lb_method']
                if res_lb_method == "GLOBAL_AVAILABILITY":
                    assert True
                    print("Modified changes to %s are reflecting" % res_lb_method)
                else:
                    print("Modified changes to %s are NOT reflecting" % res_lb_method)
                    assert False
                logging.info("Test Case 104 Execution Completed")


        @pytest.mark.run(order=105)
        def test_105_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                Queries_Responded = queries[0].strip(" ").split(" ")[0]
                Server_that_responded = queries[0].strip(" ").split(" ")[1]
                logging.info("*********** Validating Total number of queries ~***********")
                if int(Queries_Responded) == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Queries_Responded)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("*********** Validating how many queries pool 1 received***********")
                if (int(Queries_Responded) == int(5000)) and (Server_that_responded == new_ip[2]):
                    assert True
                    print("Pool 1 Responded with GLOBAL AVAILABILITY method using %s server " % Server_that_responded)
                else:
                    print("%s server from pool 1 failed to respond with GLOBAL AVAILABILITY method" % Server_that_responded)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 105 Execution Completed")


        @pytest.mark.run(order=106)
        def test_106_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                Queries_Responded = queries[0].strip(" ").split(" ")[0]
                Server_that_responded = queries[0].strip(" ").split(" ")[1]
                logging.info("*********** Validating Total number of queries ~***********")
                if int(Queries_Responded) == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Queries_Responded)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("*********** Validating how many queries pool 1 received***********")
                if (int(Queries_Responded) == int(5000)) and (Server_that_responded == new_ip[2]):
                    assert True
                    print("Pool 1 Responded with GLOBAL AVAILABILITY method using %s server " % Server_that_responded)
                else:
                    print("%s server from pool 1 failed to respond with GLOBAL AVAILABILITY method" % Server_that_responded)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 106 Execution Completed")


        @pytest.mark.run(order=107)
        def test_107_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                Queries_Responded = queries[0].strip(" ").split(" ")[0]
                Server_that_responded = queries[0].strip(" ").split(" ")[1]
                logging.info("*********** Validating Total number of queries ~***********")
                if int(Queries_Responded) == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Queries_Responded)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("*********** Validating how many queries pool 1 received***********")
                if (int(Queries_Responded) == int(5000)) and (Server_that_responded == new_ip[2]):
                    assert True
                    print("Pool 1 Responded with GLOBAL AVAILABILITY method using %s server " % Server_that_responded)
                else:
                    print("%s server from pool 1 failed to respond with GLOBAL AVAILABILITY method" % Server_that_responded)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 107 Execution Completed")


        @pytest.mark.run(order=108)
        def test_108_Modify_the_lb_method_of_LBDN_to_Fixed_Ratio(self):
                logging.info("************* Modify the LB method of LBDN to Fixed Ratio ************")
                logging.info("********** Getting the ref of LBDN ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=DTC_LBDN')
                response = json.loads(response)
                ref_lbdn = response[0]['_ref']
                logging.info("**********  Modify the LB method of LBDN to Fixed Ratio ************")
                data = {"lb_method": "RATIO"}
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
                logging.info("Test Case 108 Execution Completed")



        @pytest.mark.run(order=109)
        def test_109_Validation_of_the_lb_method_of_LBDN_to_Fixed_Ratio(self):
                logging.info("********** Getting the ref of LBDN ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=DTC_LBDN')
                response = json.loads(response)
                ref_lbdn = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref_lbdn, params='?_return_fields=lb_method')
                response1 = json.loads(response1)
                res_lb_method = response1['lb_method']
                if res_lb_method == "RATIO":
                    assert True
                    print("Modified changes to %s are reflecting" % res_lb_method)
                else:
                    print("Modified changes to %s are NOT reflecting" % res_lb_method)
                    assert False
                logging.info("Test Case 109 Execution Completed")


        @pytest.mark.run(order=110)
        def test_110_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                print(new_ip)
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                Servers=[]
                for i in queries:
                    a = i.strip(" ").split(" ")[0]
                    b = i.strip(" ").split(" ")[1]
                    No_of_queries.append(int(a))
                    Servers.append(b)
                No_of_queries=list(filter(None, No_of_queries))
                Sum_of_queries=sum(No_of_queries)
                print(No_of_queries)
                print(Servers)
                print(Sum_of_queries)
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("*********** Validating how many queries each pool received***********")
                for i in Servers:
                     if (No_of_queries[0] < int(1400)) and (i == new_ip[0]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[0], i))
                     elif (No_of_queries[1] < int(1400)) and (i == new_ip[1]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[1], i))
                     elif (No_of_queries[2] < int(2600)) and (i == new_ip[2]):
                         assert True
                         print("Pool 1 responded to %s queries using the server %s" % (No_of_queries[2], i))
                     else:
                         print("Validation for the queries in Fixed ratio method failed")
                         assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 110 Execution Completed")



        @pytest.mark.run(order=111)
        def test_111_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                Servers=[]
                for i in queries:
                    a = i.strip(" ").split(" ")[0]
                    b = i.strip(" ").split(" ")[1]
                    No_of_queries.append(int(a))
                    Servers.append(b)
                No_of_queries=list(filter(None, No_of_queries))
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("*********** Validating how many queries each pool received***********")
                for i in Servers:
                     if (No_of_queries[0] < int(1400)) and (i == new_ip[0]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[0], i))
                     elif (No_of_queries[1] < int(1400)) and (i == new_ip[1]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[1], i))
                     elif (No_of_queries[2] < int(2600)) and (i == new_ip[2]):
                         assert True
                         print("Pool 1 responded to %s queries using the server %s" % (No_of_queries[2], i))
                     else:
                         print("Validation for the queries in Fixed ratio method failed")
                         assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 111 Execution Completed")


        @pytest.mark.run(order=112)
        def test_112_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                Servers=[]
                for i in queries:
                    a = i.strip(" ").split(" ")[0]
                    b = i.strip(" ").split(" ")[1]
                    No_of_queries.append(int(a))
                    Servers.append(b)
                No_of_queries=list(filter(None, No_of_queries))
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("*********** Validating how many queries each pool received***********")
                for i in Servers:
                     if (No_of_queries[0] < int(1400)) and (i == new_ip[0]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[0], i))
                     elif (No_of_queries[1] < int(1400)) and (i == new_ip[1]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[1], i))
                     elif (No_of_queries[2] < int(2600)) and (i == new_ip[2]):
                         assert True
                         print("Pool 1 responded to %s queries using the server %s" % (No_of_queries[2], i))
                     else:
                         print("Validation for the queries in Fixed ratio method failed")
                         assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 112 Execution Completed")


        @pytest.mark.run(order=113)
        def test_113_Modify_the_lb_method_of_LBDN_to_Source_IP_Hash(self):
                logging.info("************* Modify the LB method of LBDN to Source IP Hash ************")
                logging.info("********** Getting the ref of LBDN ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=DTC_LBDN')
                response = json.loads(response)
                ref_lbdn = response[0]['_ref']
                logging.info("**********  Modify the LB method of LBDN to Fixed Ratio ************")
                data = {"lb_method": "SOURCE_IP_HASH"}
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
                logging.info("Test Case 113 Execution Completed")



        @pytest.mark.run(order=114)
        def test_114_Validation_Source_IP_Hash_lb_method_in_LBDN(self):
                logging.info("********** Getting the ref of LBDN ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=DTC_LBDN')
                response = json.loads(response)
                ref_lbdn = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref_lbdn, params='?_return_fields=lb_method')
                response1 = json.loads(response1)
                res_lb_method = response1['lb_method']
                if res_lb_method == "SOURCE_IP_HASH":
                    assert True
                    print("Modified changes to %s are reflecting" % res_lb_method)
                else:
                    print("Modified changes to %s are NOT reflecting" % res_lb_method)
                    assert False
                logging.info("Test Case 114 Execution Completed")


        @pytest.mark.run(order=115)
        def test_115_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                Servers=[]
                for i in queries:
                    a = i.strip(" ").split(" ")[0]
                    b = i.strip(" ").split(" ")[1]
                    No_of_queries.append(int(a))
                    Servers.append(b)
                No_of_queries=list(filter(None, No_of_queries))
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                print(Servers)
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("*********** Validating how many queries each pool received***********")
                for i in Servers:
                     if (No_of_queries[0] < int(2600)) and (i == new_ip[0]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[0], i))
                     elif (No_of_queries[1] < int(2600)) and (i == new_ip[1]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[1], i))
                     elif (No_of_queries[0] < int(2600)) and (i == new_ip[2]):
                         assert True
                         print("Pool 1 responded to %s queries using the server %s" % (No_of_queries[0], i))
                     elif (No_of_queries[1] < int(2600)) and (i == new_ip[3]):
                         assert True
                         print("Pool 1 responded to %s queries using the server %s" % (No_of_queries[1], i))
                     else:
                         print("Validation failed for Source IP hash method, since pool 2 servers didn't respons to the query")
                         assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 115 Execution Completed")


        @pytest.mark.run(order=116)
        def test_116_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                Servers=[]
                for i in queries:
                    a = i.strip(" ").split(" ")[0]
                    b = i.strip(" ").split(" ")[1]
                    No_of_queries.append(int(a))
                    Servers.append(b)
                No_of_queries=list(filter(None, No_of_queries))
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                print(Servers)
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("*********** Validating how many queries each pool received***********")
                for i in Servers:
                     if (No_of_queries[0] < int(2600)) and (i == new_ip[0]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[0], i))
                     elif (No_of_queries[1] < int(2600)) and (i == new_ip[1]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[1], i))
                     elif (No_of_queries[0] < int(2600)) and (i == new_ip[2]):
                         assert True
                         print("Pool 1 responded to %s queries using the server %s" % (No_of_queries[0], i))
                     elif (No_of_queries[1] < int(2600)) and (i == new_ip[3]):
                         assert True
                         print("Pool 1 responded to %s queries using the server %s" % (No_of_queries[1], i))
                     else:
                         print("Validation failed for Source IP hash method, since pool 2 servers didn't respons to the query")
                         assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 116 Execution Completed")


        @pytest.mark.run(order=117)
        def test_117_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                Servers=[]
                for i in queries:
                    a = i.strip(" ").split(" ")[0]
                    b = i.strip(" ").split(" ")[1]
                    No_of_queries.append(int(a))
                    Servers.append(b)
                No_of_queries=list(filter(None, No_of_queries))
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                print(Servers)
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("*********** Validating how many queries each pool received***********")
                for i in Servers:
                     if (No_of_queries[0] < int(2600)) and (i == new_ip[0]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[0], i))
                     elif (No_of_queries[1] < int(2600)) and (i == new_ip[1]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[1], i))
                     elif (No_of_queries[0] < int(2600)) and (i == new_ip[2]):
                         assert True
                         print("Pool 1 responded to %s queries using the server %s" % (No_of_queries[0], i))
                     elif (No_of_queries[1] < int(2600)) and (i == new_ip[3]):
                         assert True
                         print("Pool 1 responded to %s queries using the server %s" % (No_of_queries[1], i))
                     else:
                         print("Validation failed for Source IP hash method, since pool 2 servers didn't respons to the query")
                         assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 117 Execution Completed")


        @pytest.mark.run(order=118)
        def test_118_create_new_topo_rule2_with_destination_as_pool1(self):
                logging.info("********** Adding new topology rule2 wih destination as pool 1 ************")
                logging.info("Getting the Pool name reference")
                Pool_name=["DTC_Sample_pool","DTC_Sample_pool_2"]
                Pool_ref = []
                for i in Pool_name:
                        response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name='+i)
                        response_servers = json.loads(response_servers)
                        ref = response_servers[0]['_ref']
                        Pool_ref.append(ref)
                data = {"name": "DTC_Sample_Topology_2", "rules": [{"sources": [{"source_op": "IS","source_type": "SUBNET","source_value": "10.0.0.0/8"}], "dest_type": "POOL","destination_link": Pool_ref[0]}]}
                response = ib_NIOS.wapi_request('POST',object_type='dtc:topology', fields=json.dumps(data))
                print(response)
                assert re.search(r'dtc:topology', response)
                logging.info("Test Case 118 Execution Completed")


        @pytest.mark.run(order=119)
        def test_119_Validation_of_topology_rule2_subnet_and_server_added(self):
                logging.info("********** Validation of topology rule2 subnet and server added ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=DTC_Sample_Topology_2')
                response = json.loads(response)
                response_name = response[0]['name']
                response_ref = response[0]['_ref']
                logging.info("******* Validation of DTC topology name **********")
                if response_name == "DTC_Sample_Topology_2":
                    assert True
                    print("DTC Topolgy %s Created sucessfully" % response_name)
                else:
                    print("DTC Topolgy %s is not created" % response_name)
                    assert False
                logging.info("******* Validation of rule configured **********")
                response1 = ib_NIOS.wapi_request('GET',object_type=response_ref, params='?_return_fields=rules')
                response1 = json.loads(response1)
                rule_ref = response1['rules'][0]['_ref']
                response2 = ib_NIOS.wapi_request('GET',object_type=rule_ref, params='?_return_fields=dest_type')
                response2 = json.loads(response2)
                response2 = response2['dest_type']
                if response2 == "POOL":
                   assert True
                   print("The dest_type for the topology rule 2 is %s" % response2)
                else:
                   print("The dest_type for the topology rule 2 is not %s" % response2)
                   assert False
                response3 = ib_NIOS.wapi_request('GET',object_type=rule_ref, params='?_return_fields=destination_link')
                response3 = json.loads(response3)
                response3 = response3['destination_link']['name']
                if response3 == "DTC_Sample_pool":
                   assert True
                   print("The pool configured under topology rule 2 is %s" % response3)
                else:
                   print("The pool configured under topology rule 2 is not %s" % response3)
                   assert False
                logging.info("Test Case 119 Execution Completed")


        @pytest.mark.run(order=120)
        def test_120_Modify_the_lb_method_of_LBDN_to_Topology(self):
                logging.info("************* Modify the LB method of LBDN to Topology ************")
                logging.info("********* Getting the topology reference *********")
                response2 = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=DTC_Sample_Topology_2')
                response2 = json.loads(response2)
                response2_ref = response2[0]['_ref']
                logging.info("********* Modify the lb preferred method to topology *********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=DTC_LBDN')
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
                logging.info("Test Case 120 Execution Completed")



        @pytest.mark.run(order=121)
        def test_121_Validation_of_the_lb_method_of_LBDN_to_Topology(self):
                logging.info("********** Getting the ref of LBDN ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=DTC_LBDN')
                response = json.loads(response)
                ref_lbdn = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref_lbdn, params='?_return_fields=lb_method')
                response1 = json.loads(response1)
                res_lb_method = response1['lb_method']
                if res_lb_method == "TOPOLOGY":
                    assert True
                    print("Modified changes to %s are reflecting" % res_lb_method)
                else:
                    print("Modified changes to %s are NOT reflecting" % res_lb_method)
                    assert False
                logging.info("Test Case 121 Execution Completed")


        @pytest.mark.run(order=122)
        def test_122_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip(" ").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded == new_ip[2]:
                    assert True
                    print("Configured Pool 1 responded with server %s for the queries" % Server_That_Responded)
                else:
                    print("Configured Pool 1 did not respond with server %s for the queries" % Server_That_Responded)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 122 Execution Completed")


        @pytest.mark.run(order=123)
        def test_123_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip(" ").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded == new_ip[2]:
                    assert True
                    print("Configured Pool 1 responded with server %s for the queries" % Server_That_Responded)
                else:
                    print("Configured Pool 1 did not respond with server %s for the queries" % Server_That_Responded)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 123 Execution Completed")


        @pytest.mark.run(order=124)
        def test_124_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip(" ").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded == new_ip[2]:
                    assert True
                    print("Configured Pool 1 responded with server %s for the queries" % Server_That_Responded)
                else:
                    print("Configured Pool 1 did not respond with server %s for the queries" % Server_That_Responded)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 124 Execution Completed")



        @pytest.mark.run(order=125)
        def test_125_Add_the_default_destination_pool_to_topology_rule(self):
                logging.info("********** Adding default destination pool to the topology rule ************")
                logging.info("Getting the Pool name reference")
                Pool_name=["DTC_Sample_pool","DTC_Sample_pool_2"]
                Pool_ref = []
                for i in Pool_name:
                        response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name='+i)
                        response_servers = json.loads(response_servers)
                        print(response_servers)
                        ref = response_servers[0]['_ref']
                        Pool_ref.append(ref)
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=DTC_Sample_Topology_2')
                response1 = json.loads(response1)
                response1 = response1[0]['_ref']
                data = {"name": "DTC_Sample_Topology_2", "rules": [{"sources": [{"source_op": "IS","source_type": "SUBNET","source_value": "10.0.0.0/8"}], "dest_type": "POOL","destination_link": Pool_ref[0]}, {"sources":[], "dest_type": "POOL", "destination_link": Pool_ref[1]}]}
                response = ib_NIOS.wapi_request('PUT',object_type=response1, fields=json.dumps(data))
                print(response)
                assert re.search(r'dtc:topology', response)
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
                logging.info("Test Case 125 Execution Completed")


        @pytest.mark.run(order=126)
        def test_126_Enable_the_DTC_In_Grid_DNS_Properties(self):
                logging.info("********** Enable the DTC in Grid DNS Properties ************")
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
                logging.info("Test Case 126 Execution Completed")


        @pytest.mark.run(order=127)
        def test_127_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("************ Run the dig command with 5k queries on grid master *************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com in a +subnet=20.10.2.0/24 +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                Servers=[]
                for i in queries:
                    a = i.strip(" ").split(" ")[0]
                    b = i.strip(" ").split(" ")[1]
                    No_of_queries.append(int(a))
                    Servers.append(b)
                No_of_queries=list(filter(None, No_of_queries))
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      assert False
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                logging.info("*********** Validating how many queries each pool received***********")
                for i in Servers:
                     if (No_of_queries[0] < int(2600)) and (i == new_ip[0]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[0], i))
                     elif (No_of_queries[1] < int(2600)) and (i == new_ip[1]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[1], i))
                     else:
                         print("Validation failed for topology method, since pool 2 servers didn't respond to the query")
                         assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 127 Execution Completed")

       
        @pytest.mark.run(order=128)
        def test_128_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("************ Run the dig command with 5k queries on grid member 1 *************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com in a +subnet=20.10.2.0/24 +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                Servers=[]
                for i in queries:
                    a = i.strip(" ").split(" ")[0]
                    b = i.strip(" ").split(" ")[1]
                    No_of_queries.append(int(a))
                    Servers.append(b)
                No_of_queries=list(filter(None, No_of_queries))
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      assert False
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                logging.info("*********** Validating how many queries each pool received***********")
                for i in Servers:
                     if (No_of_queries[0] < int(2600)) and (i == new_ip[0]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[0], i))
                     elif (No_of_queries[1] < int(2600)) and (i == new_ip[1]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[1], i))
                     else:
                         print("Validation failed for topology method, since pool 2 servers didn't respond to the query")
                         assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 128 Execution Completed")


        @pytest.mark.run(order=129)
        def test_129_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("************ Run the dig command with 5k queries on grid member 2 *************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com in a +subnet=20.10.2.0/24 +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                Servers=[]
                for i in queries:
                    a = i.strip(" ").split(" ")[0]
                    b = i.strip(" ").split(" ")[1]
                    No_of_queries.append(int(a))
                    Servers.append(b)
                No_of_queries=list(filter(None, No_of_queries))
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      assert False
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                logging.info("*********** Validating how many queries each pool received***********")
                for i in Servers:
                     if (No_of_queries[0] < int(2600)) and (i == new_ip[0]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[0], i))
                     elif (No_of_queries[1] < int(2600)) and (i == new_ip[1]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[1], i))
                     else:
                         print("Validation failed for topology method, since pool 2 servers didn't respond to the query")
                         assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 129 Execution Completed")

        @pytest.mark.run(order=130)
        def test_130_Remove_the_default_destination_pool_in_topology_rule_2_and_modify_the_source_op_to_IS_NOT(self):
                logging.info("********** Remove the default destination pool in topology rule 2 and modify the source op to IS NOT ************")
                logging.info("Getting the Pool name reference")
                Pool_name=["DTC_Sample_pool","DTC_Sample_pool_2"]
                Pool_ref = []
                for i in Pool_name:
                        response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name='+i)
                        response_servers = json.loads(response_servers)
                        print(response_servers)
                        ref = response_servers[0]['_ref']
                        Pool_ref.append(ref)
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=DTC_Sample_Topology_2')
                response1 = json.loads(response1)
                response1 = response1[0]['_ref']
                data = {"name": "DTC_Sample_Topology_2", "rules": [{"sources": [{"source_op": "IS_NOT","source_type": "SUBNET","source_value": "10.0.0.0/8"}], "dest_type": "POOL","destination_link": Pool_ref[0]}]}
                response = ib_NIOS.wapi_request('PUT',object_type=response1, fields=json.dumps(data))
                print(response)
                assert re.search(r'dtc:topology', response)
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
                logging.info("Test Case 130 Execution Completed")


        @pytest.mark.run(order=131)
        def test_131_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com in a +subnet=20.10.2.0/24 +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip(" ").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded == new_ip[2]:
                    assert True
                    print("Configured Pool 1 responded with server %s for the queries" % Server_That_Responded)
                else:
                    print("Configured Pool 1 did not respond with server %s for the queries" % Server_That_Responded)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 131 Execution Completed")


        @pytest.mark.run(order=132)
        def test_132_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com in a +subnet=20.10.2.0/24 +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip(" ").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded == new_ip[2]:
                    assert True
                    print("Configured Pool 1 responded with server %s for the queries" % Server_That_Responded)
                else:
                    print("Configured Pool 1 did not respond with server %s for the queries" % Server_That_Responded)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 132 Execution Completed")



        @pytest.mark.run(order=133)
        def test_133_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com in a +subnet=20.10.2.0/24 +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_ip=Server_ip[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip(" ").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded == new_ip[2]:
                    assert True
                    print("Configured Pool 1 responded with server %s for the queries" % Server_That_Responded)
                else:
                    print("Configured Pool 1 did not respond with server %s for the queries" % Server_That_Responded)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 133 Execution Completed")


        @pytest.mark.run(order=134)
        def test_134_Disable_the_DTC_In_Grid_DNS_Properties(self):
                logging.info("********** Enable the DTC in Grid DNS Properties ************")
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
                logging.info("Test Case 134 Execution Completed")


        @pytest.mark.run(order=135)
        def test_135_Modify_the_lb_method_of_LBDN_to_Round_Robin(self):
                logging.info("********* Modify the lb preferred method to Round Robin *********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=DTC_LBDN')
                response = json.loads(response)
                ref_lbdn = response[0]['_ref']
                data = {"lb_method": "ROUND_ROBIN"}
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
                logging.info("Test Case 135 Execution Completed")



        @pytest.mark.run(order=136)
        def test_136_Validation_of_the_lb_method_of_LBDN_to_Round_Robin(self):
                logging.info("****** Validation of the lb method of LBDN to Round Robin *******")
                logging.info("********** Getting the ref of LBDN ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=DTC_LBDN')
                response = json.loads(response)
                ref_lbdn = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref_lbdn, params='?_return_fields=lb_method')
                response1 = json.loads(response1)
                res_lb_method = response1['lb_method']
                if res_lb_method == "ROUND_ROBIN":
                    assert True
                    print("Modified changes to %s are reflecting" % res_lb_method)
                else:
                    print("Modified changes to %s are NOT reflecting" % res_lb_method)
                    assert False
                logging.info("Test Case 136 Execution Completed")



        @pytest.mark.run(order=137)
        def test_137_Check_if_any_cores_generated_in_master_and_member(self):
                logging.info("********** Check if any cores generated in master and members ************")
                ip = [config.grid_master_vip, config.grid_member1_vip, config.grid_member2_vip]
                for i in ip:
                    print("Logging in to device "+i)
                    dir_path = 'cd /storage/cores/'
                    client = paramiko.SSHClient()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
                    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
                    client.connect(i, username='root', pkey = mykey)
                    stdin, stdout, stderr = client.exec_command('ls /storage/cores/ | wc -l')
                    output = stdout.read()
                    output = output.split("\n")
                    if output[0] == "0":
                        assert True
                        print("There are no cores files generated")
                    else:
                        print("Core files are generated while running the performance cases")
                        assert False
                    print("Logging out of device "+i)
                logging.info("Test Case 137 Execution Completed")



        @pytest.mark.run(order=138)
        def test_138_Modify_the_lbdn_to_remove_second_pool(self):
                logging.info("********** Getting the ref of pool ************")
                pool_list = ["DTC_Sample_pool", "DTC_Sample_pool_2"]
                pool_ref=[]
                for i in pool_list:
                     response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name='+i)
                     response = json.loads(response)
                     ref_pool = response[0]['_ref']
                     pool_ref.append(ref_pool)
                logging.info("********** Getting the ref of LBDN ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=DTC_LBDN')
                response = json.loads(response)
                ref_lbdn = response[0]['_ref']
                logging.info("**********  Reverting the lbdn pools to pool1 instead of pool2 ************")
                data = {"lb_method": "ROUND_ROBIN", "pools": [{"ratio": 1, "pool": pool_ref[0]}]}
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
                logging.info("Test Case 138 Execution Completed")


        @pytest.mark.run(order=139)
        def test_139_Modify_the_Pool_1_and_add_all_twenty_servers(self):
                logging.info("Getting the server name reference ")
                server_ref = []
                for i in Server_name:
                        response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                        response_servers = json.loads(response_servers)
                        ref = response_servers[0]['_ref']
                        server_ref.append(ref)
                print(server_ref)
                logging.info("****** Getting the pool ref ******")
                response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                ref1 = json.loads(response_servers)
                ref1 = ref1[0]['_ref']
                print(ref1)
                logging.info("************ Adding all twenty servers ***********")
                All_the_Server=[]
                server_dict={}
                for i in server_ref:
                        server_dict['ratio']=1
                        server_dict['server']=i
                        All_the_Server.append(server_dict)
                        server_dict={}
                data = {"servers": All_the_Server}
                response = ib_NIOS.wapi_request('PUT',object_type=ref1, fields=json.dumps(data))
                response = json.loads(response)
                logging.info("Validation of Pool creation")
                assert re.search(r'dtc:pool', response)
                logging.info("All the Servers are added to pool")
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
                logging.info("Test Case 139 Execution Completed")


        @pytest.mark.run(order=140)
        def test_140_Validation_of_DTC_Pool_of_20_servers(self):
                logging.info("********** Validating all 20 servers in pool ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                ref1 = json.loads(response)
                ref1 = ref1[0]['_ref']
                print(ref1)
                response = ib_NIOS.wapi_request('GET',object_type=ref1 , params='?_return_fields=servers')
                print(response)
                ref1 = json.loads(response)
                new_list = []
                for i in ref1['servers']:
                        a = i['server'].split(":")[-1]
                        new_list.append(a)
                if new_list == Server_name:
                        assert True
                        print("Validation of all servers are done, all servers match")
                else:
                        print("Validation of all servers failed, all servers do not match")
                        assert False
                logging.info("Test Case 140 Execution Completed")



        @pytest.mark.run(order=141)
        def test_141_Create_Twenty_A_Records(self):
                logging.info("********** Create Twenty A Records ************")
                for i,j in d.items():
                    a_name = str(i)+".dtc.com"
                    print(a_name)
                    data = {"name":a_name,"ipv4addr":j}
                    response = ib_NIOS.wapi_request('POST', object_type="record:a", fields=json.dumps(data))
                    print response
                    logging.info(response)
                    read  = re.search(r'201',response)
                    for read in  response:
                            assert True
                logging.info("Test Case 141 Execution Completed")


        @pytest.mark.run(order=142)
        def test_142_Validation_of_Twenty_A_Records(self):
                logging.info("********* Validating the Twenty A Records **********")
                response = ib_NIOS.wapi_request('GET',object_type="record:a" , params='?_return_fields=name')
                #print(response)
                ref1 = json.loads(response)
                print(ref1)
                new_list = []
                for i in ref1:
                    new_list.append(i['name'])
                        
                if new_list == a_record_name:
                    assert True
                    print("All the Twenty A records are created")
                else:
                    print("All Twenty records are not created")
                    assert False
                logging.info("Test Case 142 Execution Completed")


        @pytest.mark.run(order=143)
        def test_143_get_the_VM_hostname_for_DTC_sever_with_hostname_scenarios(self):
                logging.info("********* Get the VM hostname for DTC sever with hostname scenarios *********")
                global Server_Domain_name
                Server_Domain_name=[]
                for i in Vm_ip:
                    print("Logging in to device "+i)
                    client = client = paramiko.SSHClient()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    try:
                        client.connect(i, username='root', password = 'infoblox')
                        stdin, stdout, stderr = client.exec_command('hostname')
                        output = stdout.read()
                        output1 = output.decode('ascii').split(".")[0]
                        print(output1)
                        Server_Domain_name.append(output1.strip("\n"))
                        print("Logging out of device "+i)
                    except Exception as e:
                        print(e)
                        continue
                    finally:
                        client.close()
                Server_Domain_name=Server_Domain_name[:20]
                print(Server_Domain_name)
                logging.info("Test Case 143 Execution Completed")


        @pytest.mark.run(order=144)
        def test_144_Modify_the_DTC_Server_IPs_to_Domain_Name(self):
                logging.info("********* Modify the DTC Server IPs to Domain Name **********")
                logging.info("********* Getting the server ref ***********")
                for n,i in enumerate(Server_name):
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    data = {"host": Server_Domain_name[n]}
                    response = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
                    assert re.search(r'dtc:server', response)
                    print("%s pool updated successfully" % (Server_Domain_name[n]))
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
                logging.info("Test Case 144 Execution Completed")


        @pytest.mark.run(order=145)
        def test_145_adding_dns_resolver_ip_and_domain_name(self):
                logging.info("********** Adding the resolver ip and domain name **********")
                response = ib_NIOS.wapi_request('GET',object_type='grid')
                reference = json.loads(response)
                ref = reference[0]['_ref']
                data={"dns_resolver_setting": {"resolvers": [config.resolver_ip], "search_domains": [config.resolver_domain_name]}}
                response1 = ib_NIOS.wapi_request('PUT', object_type=ref ,fields=json.dumps(data))
                assert re.search(r'grid', response1)
                logging.info("Test Case 145 Execution Completed")



        @pytest.mark.run(order=146)
        def test_146_Validating_the_modification_of_the_DTC_Server_IPs_to_Domain_Name(self):
                logging.info("********* Validating the modification of the DTC Server IP's to Domain name")
                server_ref = []
                for i in Server_name:
                        response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                        response_servers = json.loads(response_servers)
                        ref = response_servers[0]['_ref']
                        server_ref.append(ref)
                print(server_ref)
                for n,i in enumerate(server_ref):
                    response_servers = ib_NIOS.wapi_request('GET',object_type=i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers['host']
                    if ref == Server_Domain_name[n]:
                        assert True
                        print("%s domain name updated successfully" % ref)
                    else:
                        print("%s domain name not updated successfully" % ref)
                        assert False
                logging.info("Test Case 146 Execution Completed")


        @pytest.mark.run(order=147)
        def test_147_Modify_the_pool_lb_method_to_dynamic_ratio(self):
                logging.info("********** Modifying the pool lb method to dynamic ratio ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                ref1 = json.loads(response)
                ref1 = ref1[0]['_ref']
                print(ref1)
                logging.info("********** Changing the pool lb method to all available ***********")
                data = {"lb_preferred_method": "DYNAMIC_RATIO", "lb_dynamic_ratio_preferred": {"method": "ROUND_TRIP_DELAY", "monitor": "dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp", "monitor_weighing": "RATIO"}}
                print(data)
                response = ib_NIOS.wapi_request('PUT',object_type=ref1, fields=json.dumps(data))
                response = json.loads(response)
                print(response) 
                logging.info("Validation of Pool creation")
                assert re.search(r'dtc:pool', response)
                logging.info("All the Servers are added to pool")
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
                logging.info("Test Case 147 Execution Completed")


        @pytest.mark.run(order=148)
        def test_148_Validation_of_changes_from_Global_availabilty_to_dynamic_ratio(self):
                logging.info("********** Validation of changes to dynamic ratio ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=lb_preferred_method')
                response1 = json.loads(response1)
                print(response1)
                ref1 = response1['lb_preferred_method']
                if ref1 == "DYNAMIC_RATIO":
                        assert True
                        print("Modified changes are reflecting")
                else:
                        print("Modified changes are not reflecting")
                        assert False
                sleep(30)
                logging.info("Test Case 148 Execution Completed")


        @pytest.mark.run(order=149)
        def test_149_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                total_expected_queries=int(5000)
                for i in new_name:
                        if (i in output1):
                                if (re.findall(r'\b2\d{2}\b', output1)) or (re.findall(r'\b3\d{2}\b', output1)):
                                       assert True
                                       print("Pattern match for number of queries are seen in server %s" % (i))
                                else:
                                       print("Patterns doesn't match for the queries in %s server" % (i))
                                       assert False
                        else:
                                print("Server %s doesn't match for the query sent" % (i))
                                assert False
                logging.info("Checking total number of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                for i in queries:
                    i = i.strip(" ").split(" ")[0]
                    No_of_queries.append(int(i))
                No_of_queries=list(filter(None, No_of_queries))
                print(No_of_queries)
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 149 Execution Completed")


        @pytest.mark.run(order=150)
        def test_150_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                total_expected_queries=int(5000)
                for i in new_name:
                        if (i in output1):
                                if (re.findall(r'\b2\d{2}\b', output1)) or (re.findall(r'\b3\d{2}\b', output1)):
                                       assert True
                                       print("Pattern match for number of queries are seen in server %s" % (i))
                                else:
                                       print("Patterns doesn't match for the queries in %s server" % (i))
                                       assert False
                        else:
                                print("Server %s doesn't match for the query sent" % (i))
                                assert False
                logging.info("Checking total number of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                for i in queries:
                    i = i.strip(" ").split(" ")[0]
                    No_of_queries.append(int(i))
                No_of_queries=list(filter(None, No_of_queries))
                print(No_of_queries)
                Sum_of_queries=sum(No_of_queries)
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 150 Execution Completed")

        @pytest.mark.run(order=151)
        def test_151_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                total_expected_queries=int(5000)
                for i in new_name:
                        if (i in output1):
                                if (re.findall(r'\b2\d{2}\b', output1)) or (re.findall(r'\b3\d{2}\b', output1)):
                                       assert True
                                       print("Pattern match for number of queries are seen in server %s" % (i))
                                else:
                                       print("Patterns doesn't match for the queries in %s server" % (i))
                                       assert False
                        else:
                                print("Server %s doesn't match for the query sent" % (i))
                                assert False
                logging.info("Checking total number of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                for i in queries:
                    i = i.strip(" ").split(" ")[0]
                    No_of_queries.append(int(i))
                No_of_queries=list(filter(None, No_of_queries))
                print(No_of_queries)
                Sum_of_queries=sum(No_of_queries)
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 151 Execution Completed")



        @pytest.mark.skip(order=152)
        def test_152_Modify_the_pool_lb_method_to_all_available(self):
                logging.info("********** Modifying the pool lb method to all available ************")
                logging.info("********** Getting the server name reference ***********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                ref1 = json.loads(response)
                ref1 = ref1[0]['_ref']
                logging.info("********** Changing the pool lb method to all available ***********")
                data = {"lb_preferred_method": "ALL_AVAILABLE"}
                print(data)
                response = ib_NIOS.wapi_request('PUT',object_type=ref1, fields=json.dumps(data))
                response = json.loads(response)
                print(response) 
                logging.info("Validation of Pool creation")
                assert re.search(r'dtc:pool', response)
                logging.info("All the Servers are added to pool")
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
                logging.info("Test Case 152 Execution Completed")

        @pytest.mark.skip(order=153)
        def test_153_Validation_of_changes_from_round_robin_to_all_available(self):
                logging.info("********** Validation of changes from round robin to all available ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=lb_preferred_method')
                response1 = json.loads(response1)
                print(response1)
                ref1 = response1['lb_preferred_method']
                if ref1 == "ALL_AVAILABLE":
                        assert True
                        print("Modified changes are reflecting")
                else:
                        print("Modified changes are not reflecting")
                        assert False
                logging.info("Test Case 153 Execution Completed")

        
        @pytest.mark.skip(order=154)
        def test_154_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                for i in new_name:
                        if ("5000" in output1) and (i in output1):
                                assert True
                                print("5000 queries are seen in %s" % (i))
                        else:
                                print("queries doesn't match in %s server" % (i))
                                assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 154 Execution Completed")


        @pytest.mark.skip(order=155)
        def test_155_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                for i in new_name:
                        if ("5000" in output1) and (i in output1):
                                assert True
                                print("5000 queries are seen in %s" % (i))
                        else:
                                print("queries doesn't match in %s server" % (i))
                                assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 155 Execution Completed")

        @pytest.mark.skip(order=156)
        def test_156_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                for i in new_name:
                        if ("5000" in output1) and (i in output1):
                                assert True   
                                print("5000 queries are seen in %s" % (i))
                        else:
                                print("queries doesn't match in %s server" % (i))
                                assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 156 Execution Completed")

        @pytest.mark.skip(order=157)
        def test_157_Drop_each_server_from_grid_master_and_members(self):
                logging.info("********** Drop each server from grid master and members ************")
                new_list = [config.grid_master_vip, config.grid_member1_vip, config.grid_member2_vip]
                for i in Server_name[:3]:
                        for j in new_list:
                                #print("Logging in to %s" % (j))
                                drop_server = "iptables -I INPUT -s "+i+" -j DROP"
                                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+j)
                                child.logfile=sys.stdout
                                child.expect('#')
                                child.sendline(drop_server)
                                child.expect('#')
                                sleep(60)
                logging.info("Test Case 157 Execution Completed")


        @pytest.mark.skip(order=158)
        def test_158_Run_the_dig_command_with_5k_queries_on_grid_master_verify_severs_are_dropped(self):
                logging.info("********** Run the dig command with 5k queries on grid master and verify servers are dropped ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                for i in new_name:
                        if ("5000" in output1) and (i in output1):
                                assert True
                                print("5000 queries are seen in %s" % (i))
                        else:
                                print("queries doesn't match in %s server or %s Server Dropped failed" % (i, i))
                                assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 158 Execution Completed")


        @pytest.mark.skip(order=159)
        def test_159_Run_the_dig_command_with_5k_queries_on_grid_member_1_verify_severs_are_dropped(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 and verify servers are dropped ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                for i in new_name:
                        if ("5000" in output1) and (i in output1):
                                assert True
                                print("5000 queries are seen in %s" % (i))
                        else:
                                print("queries doesn't match in %s server or %s Server Dropped failed" % (i, i))
                                assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 159 Execution Completed")


        @pytest.mark.skip(order=160)
        def test_160_Run_the_dig_command_with_5k_queries_on_grid_member_2_verify_severs_are_dropped(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 and verify servers are dropped ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                for i in new_name:
                        if ("5000" in output1) and (i in output1):
                                assert True
                                print("5000 queries are seen in %s" % (i))
                        else:
                                print("queries doesn't match in %s server or %s Server Dropped failed" % (i, i))
                                assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 160 Execution Completed")

        @pytest.mark.skip(order=161)
        def test_161_Add_the_dropped_servers_from_grid_master_and_members(self):
                logging.info("********** Add the dropped servers from grid master and members ************")
                new_list = [config.grid_master_vip, config.grid_member1_vip, config.grid_member2_vip]
                for i in Server_Domain_name[:3]:
                        for j in new_list:
                                add_server = "iptables -I INPUT -s "+i+" -j ACCEPT"
                                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+j)
                                child.logfile=sys.stdout
                                child.expect('#')
                                child.sendline(add_server)
                                child.expect('#')
                                sleep(60)
                logging.info("Test Case 161 Execution Completed")



        @pytest.mark.run(order=162)
        def test_162_Modify_the_pool_lb_method_to_global_availabilty(self):
                logging.info("********** Modifying the pool to lb method to global availabilty ************")
                logging.info("Getting the server name reference ")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                ref1 = json.loads(response)
                ref1 = ref1[0]['_ref']
                data = {"lb_preferred_method": "GLOBAL_AVAILABILITY"}
                print(data)
                response = ib_NIOS.wapi_request('PUT',object_type=ref1, fields=json.dumps(data))
                response = json.loads(response)
                print(response)
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
                logging.info("Test Case 162 Execution Completed")



        @pytest.mark.run(order=163)
        def test_163_Validation_of_changes_from_round_robin_to_global_availabilty(self):
                logging.info("********** Validation of changes from round robin to global availabilty ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=lb_preferred_method')
                response1 = json.loads(response1)
                print(response1)
                ref1 = response1['lb_preferred_method']
                if ref1 == "GLOBAL_AVAILABILITY":
                        assert True
                        print("Modified changes are reflecting")
                else:
                        print("Modified changes are not reflecting")
                        assert False
                logging.info("Test Case 163 Execution Completed")


        @pytest.mark.run(order=164)
        def test_164_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                if ("5000" in output1) and (new_name[0] in output1):
                        assert True
                        print("5000 queries are seen in %s server" % (new_name[0]))
                else:
                        print("queries doesn't match in %s server" % (new_name[0]))
                        assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 164 Execution Completed")


        @pytest.mark.run(order=165)
        def test_165_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                if ("5000" in output1) and (new_name[0] in output1):
                        assert True
                        print("5000 queries are seen in %s server" % (new_name[0]))
                else:
                        print("queries doesn't match in %s server" % (new_name[0]))
                        assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 165 Execution Completed")


        @pytest.mark.run(order=166)
        def test_166_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                if ("5000" in output1) and (new_name[0] in output1):
                        assert True
                        print("5000 queries are seen in %s server" % (new_name[0]))
                else:
                        print("queries doesn't match in %s server" % (new_name[0]))
                        assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 166 Execution Completed")


        @pytest.mark.run(order=167)
        def test_167_drop_one_server_from_grid_master_and_members(self):
                logging.info("********** Drop one server from the grid master and members ************")
                new_list = [config.grid_master_vip, config.grid_member1_vip, config.grid_member2_vip]
                for i in Server_Domain_name[:1]:
                        for j in new_list:
                                add_server = "iptables -I INPUT -s "+i+" -j DROP"
                                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+j)
                                child.logfile=sys.stdout
                                child.expect('#')
                                child.sendline(add_server)
                                child.expect('#')
                                child.close()
                                sleep(60)
                logging.info("Test Case 167 Execution Completed")


        @pytest.mark.run(order=168)
        def test_168_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                if ("5000" in output1) and (new_name[1] in output1):
                        assert True
                        print("5000 queries are seen in %s server" % (new_name[1]))
                else:
                        print("queries doesn't match in %s server" % (new_name[1]))
                        assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 168 Execution Completed")


        @pytest.mark.run(order=169)
        def test_169_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                if ("5000" in output1) and (new_name[1] in output1):
                        assert True
                        print("5000 queries are seen in %s server" % (new_name[1]))
                else:
                        print("queries doesn't match in %s server" % (new_name[1]))
                        assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 169 Execution Completed")


        @pytest.mark.run(order=170)
        def test_170_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                if ("5000" in output1) and (new_name[1] in output1):
                        assert True
                        print("5000 queries are seen in %s server" % (new_name[1]))
                else:
                        print("queries doesn't match in %s server" % (new_name[1]))
                        assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 170 Execution Completed")

        @pytest.mark.run(order=171)
        def test_171_Add_one_server_which_was_dropped_from_grid_master_and_members(self):
                logging.info("********** Add one server which was dropped from the grid master and members ************")
                new_list = [config.grid_master_vip, config.grid_member1_vip, config.grid_member2_vip]
                for i in Server_Domain_name[:1]:
                        for j in new_list:
                                add_server = "iptables -I INPUT -s "+i+" -j ACCEPT"
                                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+j)
                                child.logfile=sys.stdout
                                child.expect('#')
                                child.sendline(add_server)
                                child.expect('#')
                                child.close()
                                sleep(60)
                logging.info("Test Case 171 Execution Completed")


        @pytest.mark.run(order=172)
        def test_172_Modify_the_pool_lb_method_to_ratio_fixed(self):
                logging.info("********** Modifying the pool to lb method to ratio fixed ************")
                logging.info("Getting the server name reference ")
                server_ref = []
                for i in Server_name:
                        response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                        response_servers = json.loads(response_servers)
                        ref = response_servers[0]['_ref']
                        server_ref.append(ref)
                #print(server_ref)
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                ref1 = json.loads(response)
                ref1 = ref1[0]['_ref']
                All_the_Server=[]
                server_dict={}
                for i in server_ref:
                        server_dict['ratio']=1
                        server_dict['server']=i
                        All_the_Server.append(server_dict)
                        server_dict={}
                #print(server_dict)
                logging.info("********** Updating new ratio values for few servers in All_the_Server list ************")
                count = 0
                for i in All_the_Server:
                    if count > 3:
                        break
                    if "server0" in i['server']:
                        i['ratio'] = 6
                    if "server1" in i['server']:
                        i['ratio'] = 5
                    if "server2" in i['server']:
                        i['ratio'] = 3
                    if "server3" in i['server']:
                        i['ratio'] = 2
                    count = count+1
                print(All_the_Server)
                data = {"lb_preferred_method": "RATIO", "servers": All_the_Server[:4]}
                print(data)
                response = ib_NIOS.wapi_request('PUT',object_type=ref1, fields=json.dumps(data))
                response = json.loads(response)
                print(response)
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
                logging.info("Test Case 172 Execution Completed")


        @pytest.mark.run(order=173)
        def test_173_Validation_of_changes_from_round_robin_to_ratio_fixed(self):
                logging.info("********** Validation of changes from round robin to ratio fixed ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=lb_preferred_method')
                response1 = json.loads(response1)
                print(response1)
                ref1 = response1['lb_preferred_method']
                if ref1 == "RATIO":
                        assert True
                        print("Modified changes are reflecting")
                else:
                        print("Modified changes are not reflecting")
                        assert False
                logging.info("Test Case 173 Execution Completed")


        @pytest.mark.run(order=174)
        def test_174_Validation_of_ratio_changes(self):
                logging.info("********** Validation of ratio values changes ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=servers')
                response1 = json.loads(response1)
                response1 = response1['servers']
                print(response1)
                count = 0
                for i in response1:
                    if count > 3:
                        break
                    if i['ratio'] == int(6):
                        assert True
                        print("Ratio updated for first server succesfully")
                    elif i['ratio'] == int(5):
                        assert True
                        print("Ratio updated for second server succesfully")
                    elif i['ratio'] == int(3):
                        assert True
                        print("Ratio updated for third server succesfully")
                    elif i['ratio'] == int(2):
                        assert True
                        print("Ratio updated for fourth server succesfully")
                    else:
                        assert False
                        print("Ratio updation failed for one of the servers")
                    count = count+1
                logging.info("Test Case 174 Execution Completed")


        @pytest.mark.run(order=175)
        def test_175_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:4]
                print(new_name)
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                for i in queries:
                    i = i.strip().split(" ")[0]
                    No_of_queries.append(int(i))
                No_of_queries=list(filter(None, No_of_queries))
                print(No_of_queries)
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("*********** Validating how much queries each server received ***********")
                output2 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc > test.log").read()
                with open(r"test.log",'r') as file:
                     for i in file:
                         i=i.strip().strip(".").split(" ")
                         if((int(i[0]) < 2000) and (i[1]==new_name[0])):
                             assert True
                             print("Server %s received correct number of queries" % new_name[0])
                         elif((int(i[0]) < 1700) and (i[1]==new_name[1])):
                             assert True
                             print("Server %s received correct number of queries" % new_name[1])
                         elif((int(i[0]) < 1000) and (i[1]==new_name[2])):
                             assert True
                             print("Server %s received correct number of queries" % new_name[2])
                         elif((int(i[0]) < 800) and (i[1]==new_name[3])):
                             assert True
                             print("Server %s received correct number of queries" % new_name[3])
                         else:
                             print("One of the server didn't receive correct number of queries")
                             assert False
                os.system('rm test.log')
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 175 Execution Completed")


        @pytest.mark.run(order=176)
        def test_176_Run_the_dig_command_with_5k_queries_on_grid_member1(self):
                logging.info("********** Run the dig command with 5k queries on grid member1 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:4]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                for i in queries:
                    i = i.strip(" ").split(" ")[0]
                    No_of_queries.append(int(i))
                No_of_queries=list(filter(None, No_of_queries))
                print(No_of_queries)
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                if Sum_of_queries == total_expected_queries:
                      assert True   
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("*********** Validating how much queries each server received ***********")
                output2 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc > test.log").read()
                with open(r"test.log",'r') as file:
                     for i in file:
                         i=i.strip().strip(".").split(" ")
                         if((int(i[0]) < 2000) and (i[1]==new_name[0])):
                             assert True
                             print("Server %s received correct number of queries" % new_name[0])
                         elif((int(i[0]) < 1700) and (i[1]==new_name[1])):
                             assert True
                             print("Server %s received correct number of queries" % new_name[1])
                         elif((int(i[0]) < 1000) and (i[1]==new_name[2])):
                             assert True
                             print("Server %s received correct number of queries" % new_name[2])
                         elif((int(i[0]) < 800) and (i[1]==new_name[3])):
                             assert True
                             print("Server %s received correct number of queries" % new_name[3])
                         else:
                             print("One of the server didn't receive correct number of queries")
                             assert False
                os.system('rm test.log')
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 176 Execution Completed")


        @pytest.mark.run(order=177)
        def test_177_Run_the_dig_command_with_5k_queries_on_grid_member2(self):
                logging.info("********** Run the dig command with 5k queries on grid member2 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:4]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                for i in queries:
                    i = i.strip(" ").split(" ")[0]
                    No_of_queries.append(int(i))
                No_of_queries=list(filter(None, No_of_queries))
                print(No_of_queries)
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                if Sum_of_queries == total_expected_queries:
                      assert True   
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("*********** Validating how much queries each server received ***********")
                output2 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc > test.log").read()
                with open(r"test.log",'r') as file:
                     for i in file:
                         i=i.strip().strip(".").split(" ")
                         if((int(i[0]) < 2000) and (i[1]==new_name[0])):
                             assert True
                             print("Server %s received correct number of queries" % new_name[0])
                         elif((int(i[0]) < 1700) and (i[1]==new_name[1])):
                             assert True
                             print("Server %s received correct number of queries" % new_name[1])
                         elif((int(i[0]) < 1000) and (i[1]==new_name[2])):
                             assert True
                             print("Server %s received correct number of queries" % new_name[2])
                         elif((int(i[0]) < 800) and (i[1]==new_name[3])):
                             assert True
                             print("Server %s received correct number of queries" % new_name[3])
                         else:
                             print("One of the server didn't receive correct number of queries")
                             assert False
                os.system('rm test.log')
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 177 Execution Completed")



        @pytest.mark.run(order=178)
        def test_178_Add_All_the_20_servers_back(self):
                logging.info("********** Add all the 20 servers back ************")
                server_ref = []
                for i in Server_name:
                        response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                        response_servers = json.loads(response_servers)
                        ref = response_servers[0]['_ref']
                        server_ref.append(ref)
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                ref1 = json.loads(response)
                ref1 = ref1[0]['_ref']
                All_the_Server=[]
                server_dict={}
                for i in server_ref:
                        server_dict['ratio']=1
                        server_dict['server']=i
                        All_the_Server.append(server_dict)
                        server_dict={}
                data = {"servers": All_the_Server}
                print(data)
                response = ib_NIOS.wapi_request('PUT',object_type=ref1, fields=json.dumps(data))
                response = json.loads(response)
                print(response)
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
                logging.info("Test Case 178 Execution Completed")

        @pytest.mark.run(order=179)
        def test_179_Modify_the_lb_prefered_method_to_source_ip_hash(self):
                logging.info("********** Modify the lb prefered method to source ip hash ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                ref1 = json.loads(response)
                ref1 = ref1[0]['_ref']
                data = {"lb_preferred_method": "SOURCE_IP_HASH", "consolidated_monitors":[]}
                response = ib_NIOS.wapi_request('PUT',object_type=ref1, fields=json.dumps(data))
                response = json.loads(response)
                print(response)
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
                logging.info("Test Case 179 Execution Completed")


        @pytest.mark.run(order=180)
        def test_180_Validation_of_lb_prefered_method_to_source_ip_hash(self):
                logging.info("********** Validation of lb prefered method to source ip hash ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                print(response)
                response = json.loads(response)
                print(response)
                ref = response[0]['_ref']
                response = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=lb_preferred_method')
                response = json.loads(response)
                ref1 = response['lb_preferred_method']
                if ref1 == "SOURCE_IP_HASH":
                    assert True
                    print("LB Preferred method modified to Source IP hash")
                else:
                    print("LB Preferred method modification to Source IP hash failed")
                    assert False
                logging.info("Test Case 180 Execution Completed")


        @pytest.mark.run(order=181)
        def test_181_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                queries = output1.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                #global Server_That_Responded_First
                Server_That_Responded_First=queries[0].strip().strip(".").split(" ")[1]
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded_First)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded_First)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 181 Execution Completed")


        @pytest.mark.run(order=182)
        def test_182_Run_the_dig_command_with_5k_queries_on_grid_member1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                queries = output1.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                #global Server_That_Responded_First
                Server_That_Responded_First=queries[0].strip().strip(".").split(" ")[1]
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded_First)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded_First)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 182 Execution Completed")

        
        @pytest.mark.run(order=183)
        def test_183_Run_the_dig_command_with_5k_queries_on_grid_member2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                print(output1)
                queries = output1.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                global Server_That_Responded_First
                Server_That_Responded_First=queries[0].strip().strip(".").split(" ")[1]
                print("Server that responded before drop "+Server_That_Responded_First)
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded_First)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded_First)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 183 Execution Completed")


        @pytest.mark.run(order=184)
        def test_184_Drop_the_responded_server_from_the_grid_master(self):
                logging.info("********** Drop the responded server from the grid master ************")
                global Server_That_Responded_First
                print("Dropping the server %s on master grid" % Server_That_Responded_First)
                drop_server = "iptables -I INPUT -s "+Server_That_Responded_First+" -j DROP"
                #print(drop_server)
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_master_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline(drop_server)
                child.expect('#')
                child.close()
                sleep(60)
                logging.info("Test Case 184 Execution Completed")


        @pytest.mark.run(order=185)
        def test_185_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                print(output1)
                queries = output1.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                global Server_That_Responded_First
                Server_That_Responded_After_Drop=queries[0].strip().strip(".").split(" ")[1]
                print("Server that responded before after "+Server_That_Responded_After_Drop)
                logging.info("********** Validation of servers whether different server responded since the server responded last is down in grid master ************")
                if Server_That_Responded_First != Server_That_Responded_After_Drop:
                    assert True
                    print("Server %s Responded to query since first responded server is down on grid master" % Server_That_Responded_After_Drop)
                else:
                    print("Server %s didn't drop on the master grid hence getting query on the same" % Server_That_Responded_First)
                    assert False
                logging.info("Validation of number of count of queries")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded_After_Drop)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded_After_Drop)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 185 Execution Completed")


        @pytest.mark.run(order=186)
        def test_186_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                print(output1)
                queries = output1.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                global Server_That_Responded_First
                Server_That_Responded_After_Drop=queries[0].strip().strip(".").split(" ")[1]
                print("Server that responded before after "+Server_That_Responded_After_Drop)
                logging.info("********** Validation of servers whether different server responded since the server responded last is down in grid master ************")
                if Server_That_Responded_First == Server_That_Responded_After_Drop:
                    assert True
                    print("Server %s Responded to query" % Server_That_Responded_After_Drop)
                else:
                    print("Server %s didn't respond to the query" % Server_That_Responded_First)
                    assert False
                logging.info("Validation of number of count of queries")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded_After_Drop)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded_After_Drop)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 186 Execution Completed")


        @pytest.mark.run(order=187)
        def test_187_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                print(output1)
                queries = output1.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                global Server_That_Responded_First
                Server_That_Responded_After_Drop=queries[0].strip().strip(".").split(" ")[1]
                print("Server that responded before after "+Server_That_Responded_After_Drop)
                logging.info("********** Validation of servers whether different server responded since the server responded last is down in grid master ************")
                if Server_That_Responded_First == Server_That_Responded_After_Drop:
                    assert True
                    print("Server %s Responded to query" % Server_That_Responded_After_Drop)
                else:
                    print("Server %s didn't respond to the query" % Server_That_Responded_First)
                    assert False
                logging.info("Validation of number of count of queries")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded_After_Drop)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded_After_Drop)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 187 Execution Completed")


        @pytest.mark.run(order=188)
        def test_188_Add_the_server_which_was_removed_from_the_grid_master(self):
                logging.info("********** Add the server which was removed from the grid master ************")
                global Server_That_Responded_First
                print("Adding the server %s on master grid" % Server_That_Responded_First)
                add_server = "iptables -I INPUT -s "+Server_That_Responded_First+" -j ACCEPT"
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_master_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline(add_server)
                child.expect('#')
                child.close()
                sleep(60)
                logging.info("Test Case 188 Execution Completed")


        @pytest.mark.run(order=189)
        def test_189_Enable_Auto_Consolidated_Monitors_in_the_pool(self):
                logging.info("********* Enabling Auto Consolidated Monitors in the pool *********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref = response[0]['_ref']
                data={"auto_consolidated_monitors": True}
                response1 = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
                print(response1)
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
                logging.info("Test Case 189 Execution Completed")


        @pytest.mark.run(order=190)
        def test_190_Validation_of_Auto_Consolidated_Monitors_in_the_pool(self):
                logging.info("********** Validation of Auto consolidated monitors in the pool ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                print(response)
                response = json.loads(response)
                print(response)
                ref = response[0]['_ref']
                response = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=auto_consolidated_monitors')
                response = json.loads(response)
                ref1 = response['auto_consolidated_monitors']
                if ref1 == True:
                    assert True
                    print("Auto consolidated montiors has been enabled")
                else:
                    print("Auto consolidated montiors has not been enabled")
                    assert False
                logging.info("Test Case 190 Execution Completed")


        @pytest.mark.run(order=191)
        def test_191_Validation_of_whether_master_and_members_are_part_of_consolidated_monitors_after_enabling_Auto_Consolidated_Monitors(self):
                logging.info("********** Validation of whether master and members are part of consolidated monitors after enabling auto consolidated monitors ************")
                list_of_master_and_members=[config.grid_member_fqdn, config.grid_member1_fqdn, config.grid_member2_fqdn]
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=consolidated_monitors')
                response1 = json.loads(response1)
                response1 = response1['consolidated_monitors'][0]['members']
                print(response1)
                if list_of_master_and_members == response1:
                    assert True
                    print("All the Master and members are present in consolidated monitors")
                else:
                    print("All the Master and members are not present in consolidated monitors")
                    assert False
                logging.info("Test Case 191 Execution Completed")


        @pytest.mark.run(order=192)
        def test_192_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                global Server_That_Responded_For_Master
                Server_That_Responded_For_Master=queries[0].strip().strip(".").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded_For_Master)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded_For_Master)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 192 Execution Completed")


        @pytest.mark.run(order=193)
        def test_193_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid memeber 1 ************")
                output_member1 = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1_member1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                queries = output1_member1.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                global Server_That_Responded_For_Member_1
                Server_That_Responded_For_Member_1=queries[0].strip().strip(".").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded_For_Member_1)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded_For_Member_1)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 193 Execution Completed")


        @pytest.mark.run(order=194)
        def test_194_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid memeber 2 ************")
                output_member2 = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1_member2 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                queries = output1_member2.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                global Server_That_Responded_For_Member_2
                Server_That_Responded_For_Member_2=queries[0].strip().strip(".").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded_For_Member_2)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded_For_Member_2)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 194 Execution Completed")


        @pytest.mark.run(order=195)
        def test_195_Validation_for_the_Server_responded_for_queries_sent_to_master_and_members(self):
                logging.info("********** Validation for the server responded for queries sent to master and members ************")
                global Server_That_Responded_For_Master
                global Server_That_Responded_For_Member_1
                global Server_That_Responded_For_Member_2
                new_list=[Server_That_Responded_For_Member_1, Server_That_Responded_For_Member_1]
                for i in new_list:
                    if i == Server_That_Responded_For_Master:
                        assert True
                        print("Same Server responded for all master and members")
                    else:
                        print("Different Server responded for all master and members")
                        assert False
                logging.info("Test Case 195 Execution Completed")


        @pytest.mark.run(order=196)
        def test_196_Disable_Auto_Consolidated_Monitors_in_the_pool(self):
                logging.info("********* Disabling Auto Consolidated Monitors in the pool *********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref = response[0]['_ref']
                data={"auto_consolidated_monitors": False}
                response1 = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
                print(response1)
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
                logging.info("Test Case 196 Execution Completed")

        
        @pytest.mark.run(order=197)
        def test_197_Mofify_the_pool_lb_method_to_round_robin(self):
                logging.info("********* Modify the pool lb method to round robin *********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref = response[0]['_ref']
                data={"lb_preferred_method": "ROUND_ROBIN"}
                response1 = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
                print(response1)
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
                logging.info("Test Case 197 Execution Completed")


        @pytest.mark.run(order=198)
        def test_198_Validation_of_lb_method_to_round_robin(self):
                logging.info("********** Validation of Auto consolidated monitors in the pool ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref = response[0]['_ref']
                response = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=lb_preferred_method')
                response = json.loads(response)
                ref1 = response['lb_preferred_method']
                print(ref1)
                if ref1 == "ROUND_ROBIN":
                        assert True
                        print("Modified changes are reflecting")
                else:
                        print("Modified changes are not reflecting")
                        assert False
                logging.info("Test Case 198 Execution Completed")


        @pytest.mark.run(order=199)
        def test_199_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                for i in queries:
                    a = i.strip(" ").split(" ")[0]
                    No_of_queries.append(int(a))
                print(No_of_queries)
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                logging.info("******** Validating total no of queries *********")
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("******** Validating whether each server receieved same count *********")
                for i in No_of_queries:
                    if i == 250:
                        assert True
                        print("Each server received the equal no of count %s" % i)
                    else:
                        print("Each server didn't receice the equal no of count")
                        assert False
                logging.info("******** Validating whether all the servers responded or not *********")
                for i in new_name:
                    if (i in output1):
                        assert True
                        print("Server %s responded to the query" % i)
                    else:
                        print("Server %s didn't respond to the query" % i)
                        assert False
                logging.info("Test Case 199 Execution Completed")


        @pytest.mark.run(order=200)
        def test_200_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                for i in queries:
                    a = i.strip(" ").split(" ")[0]
                    No_of_queries.append(int(a))
                print(No_of_queries)
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                logging.info("******** Validating total no of queries *********")
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      assert False
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                logging.info("******** Validating whether each server receieved same count *********")
                for i in No_of_queries:
                    if i == 250:
                        assert True
                        print("Each server received the equal no of count %s" % i)
                    else:
                        print("Each server didn't receice the equal no of count")
                        assert False
                logging.info("******** Validating whether all the servers responded or not *********")
                for i in new_name:
                    if (i in output1):
                        assert True
                        print("Server %s responded to the query" % i)
                    else:
                        print("Server %s didn't respond to the query" % i)
                        assert False
                logging.info("Test Case 200 Execution Completed")


        @pytest.mark.run(order=201)
        def test_201_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                for i in queries:
                    a = i.strip(" ").split(" ")[0]
                    No_of_queries.append(int(a))
                print(No_of_queries)
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                logging.info("******** Validating total no of queries *********")
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:      
                      assert False
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                logging.info("******** Validating whether each server receieved same count *********")
                for i in No_of_queries:
                    if i == 250:
                        assert True     
                        print("Each server received the equal no of count %s" % i)
                    else:
                        print("Each server didn't receice the equal no of count")
                        assert False
                logging.info("******** Validating whether all the servers responded or not *********")
                for i in new_name:
                    if (i in output1):
                        assert True
                        print("Server %s responded to the query" % i)
                    else:
                        print("Server %s didn't respond to the query" % i)
                        assert False
                logging.info("Test Case 201 Execution Completed")


        @pytest.mark.run(order=202)
        def test_202_Modify_Consolidated_Monitors_in_the_pool_to_ANY_and_add_master_and_member_1(self):
                logging.info("********* Modify consolidated monitors in the pool to ANY and add master and member 1 *********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref = response[0]['_ref']
                data={"consolidated_monitors": [{"availability": "ANY", "full_health_communication": True, "members": [config.grid_member_fqdn, config.grid_member1_fqdn],"monitor": "dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"}]}
                response1 = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
                print(response1)
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
                logging.info("Test Case 202 Execution Completed")


        @pytest.mark.run(order=203)
        def test_203_Validation_of_whether_master_and_member1_are_part_of_consolidated_monitors_also_if_availability_is_set_to_ANY(self):
                logging.info("********** Validation of whether master and member1 are part of consolidated monitors and also if availabity is set to ANY ************")
                list_of_master_and_members=[config.grid_member_fqdn, config.grid_member1_fqdn]
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=consolidated_monitors')
                response1 = json.loads(response1)
                response_members = response1['consolidated_monitors'][0]['members']
                print(response_members)
                logging.info("******* Validation of master and member1 in consolidated monitors ********")
                if list_of_master_and_members == response_members:
                    assert True
                    print("Master and member1 are present in consolidated monitors")
                else:
                    print("Master and member1 are not present in consolidated monitors")
                    assert False
                logging.info("******* Validation if availability is set to ANY ********")
                response2 = response1['consolidated_monitors'][0]['availability']
                if response2 == "ANY":
                    assert True
                    print("Availability is set to %s" % response2)
                else:
                    print("Availability is not set to %s" % response2)
                    assert False
                logging.info("Test Case 203 Execution Completed")


        @pytest.mark.run(order=204)
        def test_204_Drop_ALL_the_servers_from_the_grid_member1(self):
                logging.info("********** Drop All the servers from the grid member1 ************")
                new_name=Server_Domain_name[:20]
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
                for i in new_name:
                    drop_server = "iptables -I INPUT -s "+i+" -j DROP"
                    #print(drop_server)
                    child.logfile=sys.stdout
                    child.expect('#')
                    child.sendline(drop_server)
                    child.sendline('\n')
                    child.expect('#')
                    sleep(30)
                child.close()
                sleep(60)
                logging.info("Test Case 204 Execution Completed")


        @pytest.mark.run(order=205)
        def test_205_Validate_the_health_status_of_each_server_in_master_after_dropping_server_in_member1(self):
                logging.info("******** Validate the health status of each server in master after dropping server in member1 *********")
                logging.info("Getting the server name reference ")
                server_ref = []
                for i in Server_name:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    server_ref.append(ref)
                for i in server_ref:
                    response = ib_NIOS.wapi_request('GET',object_type=i, params='?_return_fields=health')
                    response = json.loads(response)
                    status = response['health']['availability']
                    if status == "GREEN":
                        assert True
                        print("Health status of Server %s is in GREEN state" % i)
                    else:
                        print("Health status of Server %s is in RED status" % i)
                        assert False
                logging.info("Test Case 205 Execution Completed")



        @pytest.mark.run(order=206)
        def test_206_Modify_Consolidated_Monitors_in_the_pool_to_ALL(self):
                logging.info("********* Modify consolidated monitors in the pool to ALL *********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref = response[0]['_ref']
                data={"consolidated_monitors": [{"availability": "ALL", "full_health_communication": True, "members": [config.grid_member_fqdn, config.grid_member1_fqdn],"monitor": "dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"}]}
                response1 = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
                print(response1)
                assert re.search(r'dtc:pool', response1)
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
                logging.info("Test Case 206 Execution Completed")


        @pytest.mark.run(order=207)
        def test_207_Validation_of_consolidated_monitors_if_availability_is_set_to_ALL(self):
                logging.info("********** Validation of consolidated monitors if availability is set to ALL ************")
                list_of_master_and_members=[config.grid_member_fqdn, config.grid_member1_fqdn]
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref, params='?_return_fields=consolidated_monitors')
                response1 = json.loads(response1)
                logging.info("******* Validation if availability is set to ANY ********")
                response2 = response1['consolidated_monitors'][0]['availability']
                if response2 == "ALL":
                    assert True
                    print("Availability is set to %s" % response2)
                else:
                    print("Availability is not set to %s" % response2)
                    assert False
                sleep(60)
                logging.info("Test Case 207 Execution Completed")


        @pytest.mark.run(order=208)
        def test_208_Validate_the_health_status_of_each_server_in_master_after_setting_availability_to_ALL(self):
                logging.info("******** Validate the health status of each server in master after setting availability to ALL *********")
                logging.info("Getting the server name reference ")
                server_ref = []
                for i in Server_name:
                    response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                    response_servers = json.loads(response_servers)
                    ref = response_servers[0]['_ref']
                    server_ref.append(ref)
                logging.info("******* Validation if HEALTH status is RED********")
                for i in server_ref:
                    response = ib_NIOS.wapi_request('GET',object_type=i, params='?_return_fields=health')
                    response = json.loads(response)
                    status = response['health']['availability']
                    if status == "RED":
                        assert True
                        print("Health status of Server %s is in RED state" % i)
                    else:
                        print("Health status of Server %s is in GREEN status" % i)
                        assert False
                logging.info("Test Case 208 Execution Completed")


        @pytest.mark.run(order=209)
        def test_209_Modify_Consolidated_Monitors_in_the_pool_to_ALL(self):
                logging.info("********* Modify consolidated monitors in the pool to ALL *********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref = response[0]['_ref']
                data={"consolidated_monitors": [{"availability": "ALL", "full_health_communication": True, "members": [config.grid_member_fqdn, config.grid_member1_fqdn, config.grid_member2_fqdn],"monitor": "dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"}]}
                response1 = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
                print(response1)
                assert (re.search(r'dtc:pool', response1))
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
                logging.info("Test Case 209 Execution Completed")


        @pytest.mark.run(order=210)
        def test_210_Add_ALL_the_servers_from_the_grid_member1(self):
                logging.info("********** Add All the servers from the grid member1 ************")
                new_name=Server_Domain_name[:20]
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
                for i in new_name:
                    accept_server = "iptables -I INPUT -s "+i+" -j ACCEPT"
                    #print(drop_server)
                    child.logfile=sys.stdout
                    child.expect('#')
                    child.sendline(accept_server)
                    child.sendline('\n')
                    child.expect('#')
                    sleep(30)
                child.close()
                sleep(60)
                logging.info("Test Case 210 Execution Completed")


        @pytest.mark.run(order=211)
        def test_211_Modify_the_lb_preferred_method_to_topology(self):
                logging.info("********* Getting the topology reference *********")
                response2 = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=DTC_Sample_Topology')
                response2 = json.loads(response2)
                response2_ref = response2[0]['_ref']
                logging.info("********* Modify the lb preferred method to topology *********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                ref = response[0]['_ref']
                data = {"lb_preferred_method": "TOPOLOGY", "lb_preferred_topology": response2_ref, "lb_alternate_method": "SOURCE_IP_HASH"}
                response1 = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
                print(response1)
                assert (re.search(r'dtc:pool', response1))
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
                logging.info("Test Case 211 Execution Completed")


        @pytest.mark.run(order=212)
        def test_212_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                print(output1_master)
                new_name=Server_Domain_name[:20]
                print(new_name)
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip().strip(".").split(" ")[1]
                print("The server that responded "+Server_That_Responded)
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded == new_name[0]:
                    assert True
                    print("Configured server %s responded to the query" % Server_That_Responded)
                else:
                    print("Different server responded to the query")
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 212 Execution Completed")


        @pytest.mark.run(order=213)
        def test_213_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                print(output1_master)
                new_name=Server_Domain_name[:20]
                print(new_name)
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip().strip(".").split(" ")[1]
                print("The server that responded "+Server_That_Responded)
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded == new_name[0]:
                    assert True
                    print("Configured server %s responded to the query" % Server_That_Responded)
                else:
                    print("Different server responded to the query")
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 213 Execution Completed")


        @pytest.mark.run(order=214)
        def test_214_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                print(output1_master)
                new_name=Server_Domain_name[:20]
                print(new_name)
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip().strip(".").split(" ")[1]
                print("The server that responded "+Server_That_Responded)
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded == new_name[0]:
                    assert True
                    print("Configured server %s responded to the query" % Server_That_Responded)
                else:
                    print("Different server responded to the query")
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 214 Execution Completed")


        @pytest.mark.run(order=215)
        def test_215_Enable_the_EDNS0_Client_Subnet_option(self):
                logging.info("********** Enable the DTC in Grid DNS Properties ************")
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
                logging.info("Test Case 215 Execution Completed")


        @pytest.mark.run(order=216)
        def test_216_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com in a +subnet=20.10.2.0/24 +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip().strip(".").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded != new_name[0]:
                    assert True
                    print("Configured server %s responded to the query" % Server_That_Responded)
                else:
                    print("Different server responded to the query")
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 216 Execution Completed")


        @pytest.mark.run(order=217)
        def test_217_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com in a +subnet=20.10.2.0/24 +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip().strip(".").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded != new_name[0]:
                    assert True
                    print("Configured server %s responded to the query" % Server_That_Responded)
                else:
                    print("Different server responded to the query")
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 217 Execution Completed")


        @pytest.mark.run(order=218)
        def test_218_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com in a +subnet=20.10.2.0/24 +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip().strip(".").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded != new_name[0]:
                    assert True
                    print("Configured server %s responded to the query" % Server_That_Responded)
                else:
                    print("Different server responded to the query")
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 218 Execution Completed")


        @pytest.mark.run(order=219)
        def test_219_Disable_the_EDNS0_Client_Subnet_option(self):
                logging.info("********** Enable the DTC in Grid DNS Properties ************")
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
                logging.info("Test Case 219 Execution Completed") 


        @pytest.mark.run(order=220)
        def test_220_Modify_topology_rule_source_op_to_IS_NOT(self):
                logging.info("********** Add new topology rule for the pool ************")
                logging.info("Getting the server name reference ")
                server_ref = []
                for i in Server_name:
                        response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                        response_servers = json.loads(response_servers)
                        ref = response_servers[0]['_ref']
                        server_ref.append(ref)
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=DTC_Sample_Topology')
                response1 = json.loads(response1)
                response1 = response1[0]['_ref']
                data = {"rules": [{"sources": [{"source_op": "IS_NOT","source_type": "SUBNET","source_value": "10.0.0.0/8"}], "dest_type": "SERVER","destination_link": server_ref[0]}]}
                response = ib_NIOS.wapi_request('PUT',object_type=response1, fields=json.dumps(data))
                print(response)
                assert re.search(r'dtc:topology', response)
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
                logging.info("Test Case 220 Execution Completed")


        @pytest.mark.run(order=221)
        def test_221_Validation_of_topology_rule_for_source_op_IS_NOT(self):
                logging.info("********** Validation of soruce op whether IS_NOT is updated or not ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=DTC_Sample_Topology')
                response = json.loads(response)
                response_name = response[0]['name']
                response_ref = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=response_ref, params='?_return_fields=rules')
                response1 = json.loads(response1)
                rule_ref = response1['rules'][0]['_ref']
                logging.info("******* Validation of source_op **********")
                response2 = ib_NIOS.wapi_request('GET',object_type=rule_ref, params='?_return_fields=sources')
                response2 = json.loads(response2)
                source_op = response2['sources'][0]['source_op']
                source_value = response2['sources'][0]['source_value']
                if (source_op == "IS_NOT") and (source_value == "10.0.0.0/8"):
                    assert True
                    print("source_op value is updated")
                else:
                    print("source_op is not updated")
                    assert False
                logging.info("Test Case 221 Execution Completed")


        @pytest.mark.run(order=222)
        def test_222_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip().strip(".").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded != new_name[0]:
                    assert True
                    print("Different server %s responded to the query" % Server_That_Responded)
                else:
                    print("Same server responded to the query")
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 222 Execution Completed")


        @pytest.mark.run(order=223)
        def test_223_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip().strip(".").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded != new_name[0]:
                    assert True
                    print("Different server %s responded to the query" % Server_That_Responded)
                else:
                    print("Same server responded to the query")
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 223 Execution Completed")


        @pytest.mark.run(order=224)
        def test_224_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip().strip(".").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded != new_name[0]:
                    assert True
                    print("Different server %s responded to the query" % Server_That_Responded)
                else:
                    print("Same server responded to the query")
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 224 Execution Completed")


        @pytest.mark.run(order=225)
        def test_225_Add_the_default_destination_server_to_topology_rule(self):
                logging.info("********** Adding new default destination server to the topology rule ************")
                logging.info("Getting the server name reference ")
                server_ref = []
                for i in Server_name:
                        response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                        response_servers = json.loads(response_servers)
                        ref = response_servers[0]['_ref']
                        server_ref.append(ref)
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=DTC_Sample_Topology')
                response1 = json.loads(response1)
                response1 = response1[0]['_ref']
                data = {"rules": [{"sources": [{"source_op": "IS_NOT","source_type": "SUBNET","source_value": "10.0.0.0/8"}], "dest_type": "SERVER","destination_link": server_ref[0]}, {"sources":[],"dest_type": "SERVER","destination_link": server_ref[1]}]}
                response = ib_NIOS.wapi_request('PUT',object_type=response1, fields=json.dumps(data))
                print(response)
                assert re.search(r'dtc:topology', response)
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
                logging.info("Test Case 225 Execution Completed")

     
        @pytest.mark.run(order=226)
        def test_226_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip().strip(".").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded == new_name[1]:
                    assert True
                    print("Default destination server %s responded to the query" % Server_That_Responded)
                else:
                    print("Default destination server %s didn't responde to the query" % Server_That_Responded)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 226 Execution Completed")


        @pytest.mark.run(order=227)
        def test_227_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip().strip(".").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded == new_name[1]:
                    assert True
                    print("Default destination server %s responded to the query" % Server_That_Responded)
                else:
                    print("Default destination server %s didn't responde to the query" % Server_That_Responded)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 227 Execution Completed")


        @pytest.mark.run(order=228)
        def test_228_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip().strip(".").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded == new_name[1]:
                    assert True
                    print("Default destination server %s responded to the query" % Server_That_Responded)
                else:
                    print("Default destination server %s didn't responde to the query" % Server_That_Responded)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 228 Execution Completed")


        @pytest.mark.run(order=229)
        def test_229_Modify_the_pool_1_lb_method_to_global_availabilty(self):
                logging.info("********** Modifying the pool to lb method to global availabilty ************")
                logging.info("Getting the server name reference ")
                server_ref = []
                for i in Server_name:
                        response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                        response_servers = json.loads(response_servers)
                        ref = response_servers[0]['_ref']
                        server_ref.append(ref)
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                ref1 = json.loads(response)
                ref1 = ref1[0]['_ref']
                data = {"lb_preferred_method": "GLOBAL_AVAILABILITY", "servers": [{"ratio": 1,"server": str(server_ref[2])}, {"ratio": 1,"server": str(server_ref[3])}]}
                print(data)
                response = ib_NIOS.wapi_request('PUT',object_type=ref1, fields=json.dumps(data))
                response = json.loads(response)
                print(response)
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
                logging.info("Test Case 229 Execution Completed")

        @pytest.mark.run(order=230)
        def test_230_Validation_of_second_pool_creation(self):
                logging.info("Getting the server name reference ")
                server_ref = []
                for i in Server_name:
                        response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                        response_servers = json.loads(response_servers)
                        ref = response_servers[0]['_ref']
                        server_ref.append(ref)
                logging.info("Validation of second pool")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool_2')
                response = json.loads(response)
                response_ref = response[0]['_ref']
                response_name = response[0]['name']
                if response_name == "DTC_Sample_pool_2":
                    assert True
                    print("%s pool created successfully" % response_name)
                else:
                    print("%s pool not created successfully" % response_name)
                    assert False
                logging.info("Validation of servers added in the pool")
                response1 = ib_NIOS.wapi_request('GET',object_type=response_ref, params='?_return_fields=servers')
                response1 = json.loads(response1)
                response1_server1 = response1['servers'][0]['server']
                response1_server2 = response1['servers'][1]['server']
                if (response1_server1 == server_ref[0]) and (response1_server2 == server_ref[1]):
                    assert True
                    print("Both the servers are added successfully")
                else:
                    print("Server validation failed for the new pool created")
                    assert False
                logging.info("Validation of pool LB method")
                response2 = ib_NIOS.wapi_request('GET',object_type=response_ref, params='?_return_fields=lb_preferred_method')
                response2 = json.loads(response2)
                response2 = response2['lb_preferred_method']
                if response2 == "RATIO":
                    assert True
                    print("LB method updated successfully")
                else:
                    print(" LB method not updated successfully")
                    assert False
                logging.info("Test Case 230 Execution Completed")


        @pytest.mark.run(order=231)
        def test_231_Validation_of_pool_one_lb_method(self):
                logging.info("Getting the server name reference ")
                server_ref = []
                for i in Server_name:
                        response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:server', params='?name='+i)
                        response_servers = json.loads(response_servers)
                        ref = response_servers[0]['_ref']
                        server_ref.append(ref)
                logging.info("Validation of second pool")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name=DTC_Sample_pool')
                response = json.loads(response)
                response_ref = response[0]['_ref']
                logging.info("Validation of servers added in the pool")
                response1 = ib_NIOS.wapi_request('GET',object_type=response_ref, params='?_return_fields=servers')
                response1 = json.loads(response1)
                response1_server1 = response1['servers'][0]['server']
                response1_server2 = response1['servers'][1]['server']
                if (response1_server1 == server_ref[2]) and (response1_server2 == server_ref[3]):
                    assert True
                    print("Both the servers are added successfully")
                else:
                    print("Server validation failed for the new pool created")
                    assert False
                logging.info("Validation of pool LB method")
                response2 = ib_NIOS.wapi_request('GET',object_type=response_ref, params='?_return_fields=lb_preferred_method')
                response2 = json.loads(response2)
                response2 = response2['lb_preferred_method']
                if response2 == "GLOBAL_AVAILABILITY":
                    assert True
                    print("LB method updated successfully")
                else:
                    print(" LB method not updated successfully")
                    assert False
                logging.info("Test Case 231 Execution Completed")


        @pytest.mark.run(order=232)
        def test_232_Modify_the_lbdn_and_add_second_pool(self):
                logging.info("********** Creation of LBDN ************")
                logging.info("********** Getting the ref of pool ************")
                pool_list = ["DTC_Sample_pool", "DTC_Sample_pool_2"]
                pool_ref=[]
                for i in pool_list:
                     response = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name='+i)
                     response = json.loads(response)
                     ref_pool = response[0]['_ref']
                     pool_ref.append(ref_pool)
                logging.info("********** Getting the ref of LBDN ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=DTC_LBDN')
                response = json.loads(response)
                ref_lbdn = response[0]['_ref']
                logging.info("**********  Adding the second pool in the LBDN ************")
                data = {"lb_method": "ROUND_ROBIN", "pools": [{"ratio": 1, "pool": pool_ref[0]}, {"ratio": 1, "pool": pool_ref[1]}]}
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
                logging.info("Test Case 232 Execution Completed")


        @pytest.mark.run(order=233)
        def test_233_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                print(output1)
                new_name=Server_Domain_name[:20]
                print(new_name)
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                Servers=[]
                for i in queries:
                    a = i.strip(" ").split(" ")[0]
                    b = i.strip().strip(".").split(" ")[1]
                    print(b)
                    No_of_queries.append(int(a))
                    Servers.append(b)
                No_of_queries=list(filter(None, No_of_queries))
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("*********** Validating how many queries pool 2 received***********")
                if (sum(No_of_queries[:2]) == int(2500)):
                    assert True
                    print("Pool 2 responded for total 2500 queries with fixed ration method")
                else:
                    print("Pool 2 didn't responded for total 2500 queries with fixed ration method")
                    assert False                    
                logging.info("****** Validation of servers in which queries are recieved ********")
                for i in Servers[:2]:
                    if i in new_name[:2]:
                        assert True
                        print("Pool 2 Responded with Fixed Ratio method using "+i+" server")
                    else:
                        print("Pool 2 didn't Responded with Fixed Ratio method using "+i+" server")
                        assert False
                logging.info("*********** Validating how many queries pool 1 received***********")
                if ((No_of_queries[2]) == int(2500)) and (Servers[2] == new_name[2]):
                    assert True
                    print("Pool 1 Responded with GLOBAL AVAILABILITY method using %s server " % Servers[2])
                else:
                    print("%s server from pool 1 failed to respond with GLOBAL AVAILABILITY method" % Servers[2])
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 233 Execution Completed")


        @pytest.mark.run(order=234)
        def test_234_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                print(new_name)
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                Servers=[]
                for i in queries:
                    a = i.strip(" ").split(" ")[0]
                    b = i.strip().strip(".").split(" ")[1]
                    print(b)
                    No_of_queries.append(int(a))
                    Servers.append(b)
                No_of_queries=list(filter(None, No_of_queries))
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("*********** Validating how many queries pool 2 received***********")
                if (sum(No_of_queries[:2]) == int(2500)):
                    assert True
                    print("Pool 2 responded for total 2500 queries with fixed ration method")
                else:
                    print("Pool 2 didn't responded for total 2500 queries with fixed ration method")
                    assert False                    
                logging.info("****** Validation of servers in which queries are recieved ********")
                for i in Servers[:2]:
                    if i in new_name[:2]:
                        assert True
                        print("Pool 2 Responded with Fixed Ratio method using "+i+" server")
                    else:
                        print("Pool 2 didn't Responded with Fixed Ratio method using "+i+" server")
                        assert False
                logging.info("*********** Validating how many queries pool 1 received***********")
                if ((No_of_queries[2]) == int(2500)) and (Servers[2] == new_name[2]):
                    assert True
                    print("Pool 1 Responded with GLOBAL AVAILABILITY method using %s server " % Servers[2])
                else:
                    print("%s server from pool 1 failed to respond with GLOBAL AVAILABILITY method" % Servers[2])
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 234 Execution Completed")


        @pytest.mark.run(order=235)
        def test_235_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                print(new_name)
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                Servers=[]
                for i in queries:
                    a = i.strip(" ").split(" ")[0]
                    b = i.strip().strip(".").split(" ")[1]
                    print(b)
                    No_of_queries.append(int(a))
                    Servers.append(b)
                No_of_queries=list(filter(None, No_of_queries))
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("*********** Validating how many queries pool 2 received***********")
                if (sum(No_of_queries[:2]) == int(2500)):
                    assert True
                    print("Pool 2 responded for total 2500 queries with fixed ration method")
                else:
                    print("Pool 2 didn't responded for total 2500 queries with fixed ration method")
                    assert False                    
                logging.info("****** Validation of servers in which queries are recieved ********")
                for i in Servers[:2]:
                    if i in new_name[:2]:
                        assert True
                        print("Pool 2 Responded with Fixed Ratio method using "+i+" server")
                    else:
                        print("Pool 2 didn't Responded with Fixed Ratio method using "+i+" server")
                        assert False
                logging.info("*********** Validating how many queries pool 1 received***********")
                if ((No_of_queries[2]) == int(2500)) and (Servers[2] == new_name[2]):
                    assert True
                    print("Pool 1 Responded with GLOBAL AVAILABILITY method using %s server " % Servers[2])
                else:
                    print("%s server from pool 1 failed to respond with GLOBAL AVAILABILITY method" % Servers[2])
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 235 Execution Completed")


        @pytest.mark.run(order=236)
        def test_236_Modify_the_lb_method_of_LBDN_to_Global_Availability(self):
                logging.info("************* Modify the LB method of LBDN to Global Availability ************") 
                logging.info("********** Getting the ref of LBDN ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=DTC_LBDN')
                response = json.loads(response)
                ref_lbdn = response[0]['_ref']
                logging.info("**********  Modify the LB method of LBDN to Global Availability ************")
                data = {"lb_method": "GLOBAL_AVAILABILITY"}
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
                logging.info("Test Case 236 Execution Completed")



        @pytest.mark.run(order=237)
        def test_237_Validation_of_the_lb_method_of_LBDN_to_Global_Availability(self):
                logging.info("********** Getting the ref of LBDN ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=DTC_LBDN')
                response = json.loads(response)
                ref_lbdn = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref_lbdn, params='?_return_fields=lb_method')
                response1 = json.loads(response1)
                res_lb_method = response1['lb_method']
                if res_lb_method == "GLOBAL_AVAILABILITY":
                    assert True
                    print("Modified changes to %s are reflecting" % res_lb_method)
                else:
                    print("Modified changes to %s are NOT reflecting" % res_lb_method)
                    assert False
                logging.info("Test Case 237 Execution Completed")


        @pytest.mark.run(order=238)
        def test_238_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                Queries_Responded = queries[0].strip(" ").split(" ")[0]
                Server_that_responded = queries[0].strip().strip(".").split(" ")[1]
                logging.info("*********** Validating Total number of queries ~***********")
                if int(Queries_Responded) == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Queries_Responded)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("*********** Validating how many queries pool 1 received***********")
                if (int(Queries_Responded) == int(5000)) and (Server_that_responded == new_name[2]):
                    assert True
                    print("Pool 1 Responded with GLOBAL AVAILABILITY method using %s server " % Server_that_responded)
                else:
                    print("%s server from pool 1 failed to respond with GLOBAL AVAILABILITY method" % Server_that_responded)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 238 Execution Completed")


        @pytest.mark.run(order=239)
        def test_239_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                Queries_Responded = queries[0].strip(" ").split(" ")[0]
                Server_that_responded = queries[0].strip().strip(".").split(" ")[1]
                logging.info("*********** Validating Total number of queries ~***********")
                if int(Queries_Responded) == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Queries_Responded)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("*********** Validating how many queries pool 1 received***********")
                if (int(Queries_Responded) == int(5000)) and (Server_that_responded == new_name[2]):
                    assert True
                    print("Pool 1 Responded with GLOBAL AVAILABILITY method using %s server " % Server_that_responded)
                else:
                    print("%s server from pool 1 failed to respond with GLOBAL AVAILABILITY method" % Server_that_responded)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 239 Execution Completed")


        @pytest.mark.run(order=240)
        def test_240_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                Queries_Responded = queries[0].strip(" ").split(" ")[0]
                Server_that_responded = queries[0].strip().strip(".").split(" ")[1]
                logging.info("*********** Validating Total number of queries ~***********")
                if int(Queries_Responded) == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Queries_Responded)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("*********** Validating how many queries pool 1 received***********")
                if (int(Queries_Responded) == int(5000)) and (Server_that_responded == new_name[2]):
                    assert True
                    print("Pool 1 Responded with GLOBAL AVAILABILITY method using %s server " % Server_that_responded)
                else:
                    print("%s server from pool 1 failed to respond with GLOBAL AVAILABILITY method" % Server_that_responded)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 240 Execution Completed")


        @pytest.mark.run(order=241)
        def test_241_Modify_the_lb_method_of_LBDN_to_Fixed_Ratio(self):
                logging.info("************* Modify the LB method of LBDN to Fixed Ratio ************")
                logging.info("********** Getting the ref of LBDN ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=DTC_LBDN')
                response = json.loads(response)
                ref_lbdn = response[0]['_ref']
                logging.info("**********  Modify the LB method of LBDN to Fixed Ratio ************")
                data = {"lb_method": "RATIO"}
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
                logging.info("Test Case 241 Execution Completed")



        @pytest.mark.run(order=242)
        def test_242_Validation_of_the_lb_method_of_LBDN_to_Fixed_Ratio(self):
                logging.info("********** Getting the ref of LBDN ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=DTC_LBDN')
                response = json.loads(response)
                ref_lbdn = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref_lbdn, params='?_return_fields=lb_method')
                response1 = json.loads(response1)
                res_lb_method = response1['lb_method']
                if res_lb_method == "RATIO":
                    assert True
                    print("Modified changes to %s are reflecting" % res_lb_method)
                else:
                    print("Modified changes to %s are NOT reflecting" % res_lb_method)
                    assert False
                logging.info("Test Case 242 Execution Completed")


        @pytest.mark.run(order=243)
        def test_243_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                Servers=[]
                for i in queries:
                    a = i.strip(" ").split(" ")[0]
                    b = i.strip().strip(".").split(" ")[1]
                    No_of_queries.append(int(a))
                    Servers.append(b)
                No_of_queries=list(filter(None, No_of_queries))
                Sum_of_queries=sum(No_of_queries)
                print(No_of_queries)
                print(Servers)
                print(Sum_of_queries)
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("*********** Validating how many queries each pool received***********")
                for i in Servers:
                     if (No_of_queries[0] < int(1400)) and (i == new_name[0]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[0], i))
                     elif (No_of_queries[1] < int(1400)) and (i == new_name[1]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[1], i))
                     elif (No_of_queries[2] < int(2600)) and (i == new_name[2]):
                         assert True
                         print("Pool 1 responded to %s queries using the server %s" % (No_of_queries[2], i))
                     else:
                         print("Validation for the queries in Fixed ratio method failed")
                         assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 243 Execution Completed")



        @pytest.mark.run(order=244)
        def test_244_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                Servers=[]
                for i in queries:
                    a = i.strip(" ").split(" ")[0]
                    b = i.strip().strip(".").split(" ")[1]
                    No_of_queries.append(int(a))
                    Servers.append(b)
                No_of_queries=list(filter(None, No_of_queries))
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("*********** Validating how many queries each pool received***********")
                for i in Servers:
                     if (No_of_queries[0] < int(1400)) and (i == new_name[0]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[0], i))
                     elif (No_of_queries[1] < int(1400)) and (i == new_name[1]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[1], i))
                     elif (No_of_queries[2] < int(2600)) and (i == new_name[2]):
                         assert True
                         print("Pool 1 responded to %s queries using the server %s" % (No_of_queries[2], i))
                     else:
                         print("Validation for the queries in Fixed ratio method failed")
                         assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 244 Execution Completed")


        @pytest.mark.run(order=245)
        def test_245_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                Servers=[]
                for i in queries:
                    a = i.strip(" ").split(" ")[0]
                    b = i.strip().strip(".").split(" ")[1]
                    No_of_queries.append(int(a))
                    Servers.append(b)
                No_of_queries=list(filter(None, No_of_queries))
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("*********** Validating how many queries each pool received***********")
                for i in Servers:
                     if (No_of_queries[0] < int(1400)) and (i == new_name[0]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[0], i))
                     elif (No_of_queries[1] < int(1400)) and (i == new_name[1]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[1], i))
                     elif (No_of_queries[2] < int(2600)) and (i == new_name[2]):
                         assert True
                         print("Pool 1 responded to %s queries using the server %s" % (No_of_queries[2], i))
                     else:
                         print("Validation for the queries in Fixed ratio method failed")
                         assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 245 Execution Completed")


        @pytest.mark.run(order=246)
        def test_246_Modify_the_lb_method_of_LBDN_to_Source_IP_Hash(self):
                logging.info("************* Modify the LB method of LBDN to Source IP Hash ************")
                logging.info("********** Getting the ref of LBDN ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=DTC_LBDN')
                response = json.loads(response)
                ref_lbdn = response[0]['_ref']
                logging.info("**********  Modify the LB method of LBDN to Fixed Ratio ************")
                data = {"lb_method": "SOURCE_IP_HASH"}
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
                logging.info("Test Case 246 Execution Completed")



        @pytest.mark.run(order=247)
        def test_247_Validation_of_the_lb_method_of_LBDN_to_Source_IP_Hash(self):
                logging.info("********** Getting the ref of LBDN ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=DTC_LBDN')
                response = json.loads(response)
                ref_lbdn = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref_lbdn, params='?_return_fields=lb_method')
                response1 = json.loads(response1)
                res_lb_method = response1['lb_method']
                if res_lb_method == "SOURCE_IP_HASH":
                    assert True
                    print("Modified changes to %s are reflecting" % res_lb_method)
                else:
                    print("Modified changes to %s are NOT reflecting" % res_lb_method)
                    assert False
                logging.info("Test Case 247 Execution Completed")


        @pytest.mark.run(order=248)
        def test_248_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                print(output1)
                new_name=Server_Domain_name[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                Servers=[]
                for i in queries:
                    a = i.strip(" ").split(" ")[0]
                    b = i.strip().strip(".").split(" ")[1]
                    No_of_queries.append(int(a))
                    Servers.append(b)
                No_of_queries=list(filter(None, No_of_queries))
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                print(Servers)
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("*********** Validating how many queries each pool received***********")
                for i in Servers:
                     if (No_of_queries[0] < int(2600)) and (i == new_name[0]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[0], i))
                     elif (No_of_queries[1] < int(2600)) and (i == new_name[1]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[1], i))
                     else:
                         print("Validation failed for Source IP hash method, since pool 2 servers didn't respons to the query")
                         assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 248 Execution Completed")


        @pytest.mark.run(order=249)
        def test_249_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                Servers=[]
                for i in queries:
                    a = i.strip(" ").split(" ")[0]
                    b = i.strip().strip(".").split(" ")[1]
                    No_of_queries.append(int(a))
                    Servers.append(b)
                No_of_queries=list(filter(None, No_of_queries))
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("*********** Validating how many queries each pool received***********")
                for i in Servers:
                     if (No_of_queries[0] < int(2600)) and (i == new_name[0]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[0], i))
                     elif (No_of_queries[1] < int(2600)) and (i == new_name[1]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[1], i))
                     else:
                         print("Validation failed for Source IP hash method, since pool 2 servers didn't respons to the query")
                         assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 249 Execution Completed")


        @pytest.mark.run(order=250)
        def test_250_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                Servers=[]
                for i in queries:
                    a = i.strip(" ").split(" ")[0]
                    b = i.strip().strip(".").split(" ")[1]
                    No_of_queries.append(int(a))
                    Servers.append(b)
                No_of_queries=list(filter(None, No_of_queries))
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                      assert False
                logging.info("*********** Validating how many queries each pool received***********")
                for i in Servers:
                     if (No_of_queries[0] < int(2600)) and (i == new_name[0]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[0], i))
                     elif (No_of_queries[1] < int(2600)) and (i == new_name[1]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[1], i))
                     else:
                         print("Validation failed for Source IP hash method, since pool 2 servers didn't respons to the query")
                         assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 250 Execution Completed")


        @pytest.mark.run(order=251)
        def test_251_modify_new_topo_rule_with_destination_as_pool1(self):
                logging.info("********** Adding new topology rule wih destination as pool 1 ************")
                logging.info("Getting the Pool name reference")
                Pool_name=["DTC_Sample_pool","DTC_Sample_pool_2"]
                Pool_ref = []
                for i in Pool_name:
                        response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name='+i)
                        response_servers = json.loads(response_servers)
                        ref = response_servers[0]['_ref']
                        Pool_ref.append(ref)
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=DTC_Sample_Topology_2')
                response = json.loads(response)
                ref = response[0]['_ref']
                data = {"name": "DTC_Sample_Topology_2", "rules": [{"sources": [{"source_op": "IS","source_type": "SUBNET","source_value": "10.0.0.0/8"}], "dest_type": "POOL","destination_link": Pool_ref[0]}]}
                response = ib_NIOS.wapi_request('PUT',object_type=ref, fields=json.dumps(data))
                print(response)
                assert re.search(r'dtc:topology', response)
                logging.info("Test Case 251 Execution Completed")


        @pytest.mark.run(order=252)
        def test_252_Validation_of_topology_rule_subnet_and_server_added(self):
                logging.info("********** Validation of topology rule subnet and server added ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=DTC_Sample_Topology_2')
                response = json.loads(response)
                response_name = response[0]['name']
                response_ref = response[0]['_ref']
                logging.info("******* Validation of DTC topology name **********")
                if response_name == "DTC_Sample_Topology_2":
                    assert True
                    print("DTC Topolgy %s Created sucessfully" % response_name)
                else:
                    print("DTC Topolgy %s is not created" % response_name)
                    assert False
                logging.info("******* Validation of rule configured **********")
                response1 = ib_NIOS.wapi_request('GET',object_type=response_ref, params='?_return_fields=rules')
                response1 = json.loads(response1)
                rule_ref = response1['rules'][0]['_ref']
                response2 = ib_NIOS.wapi_request('GET',object_type=rule_ref, params='?_return_fields=dest_type')
                response2 = json.loads(response2)
                response2 = response2['dest_type']
                if response2 == "POOL":
                   assert True
                   print("The dest_type for the topology rule is %s" % response2)
                else:
                   print("The dest_type for the topology rule is not %s" % response2)
                   assert False
                response3 = ib_NIOS.wapi_request('GET',object_type=rule_ref, params='?_return_fields=destination_link')
                response3 = json.loads(response3)
                response3 = response3['destination_link']['name']
                if response3 == "DTC_Sample_pool":
                   assert True
                   print("The pool configured under topology rule is %s" % response3)
                else:
                   print("The pool configured under topology rule is not %s" % response3)
                   assert False
                logging.info("Test Case 252 Execution Completed")


        @pytest.mark.run(order=253)
        def test_253_Modify_the_lb_method_of_LBDN_to_Topology(self):
                logging.info("************* Modify the LB method of LBDN to Topology ************")
                logging.info("********* Getting the topology reference *********")
                response2 = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=DTC_Sample_Topology_2')
                response2 = json.loads(response2)
                response2_ref = response2[0]['_ref']
                logging.info("********* Modify the lb preferred method to topology *********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=DTC_LBDN')
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
                logging.info("Test Case 253 Execution Completed")



        @pytest.mark.run(order=254)
        def test_254_Validation_of_the_lb_method_of_LBDN_to_Topology(self):
                logging.info("********** Getting the ref of LBDN ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=DTC_LBDN')
                response = json.loads(response)
                ref_lbdn = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref_lbdn, params='?_return_fields=lb_method')
                response1 = json.loads(response1)
                res_lb_method = response1['lb_method']
                if res_lb_method == "TOPOLOGY":
                    assert True
                    print("Modified changes to %s are reflecting" % res_lb_method)
                else:
                    print("Modified changes to %s are NOT reflecting" % res_lb_method)
                    assert False
                logging.info("Test Case 254 Execution Completed")


        @pytest.mark.run(order=255)
        def test_255_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip().strip(".").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded == new_name[2]:
                    assert True
                    print("Configured Pool 1 responded with server %s for the queries" % Server_That_Responded)
                else:
                    print("Configured Pool 1 did not respond with server %s for the queries" % Server_That_Responded)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 255 Execution Completed")


        @pytest.mark.run(order=256)
        def test_256_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip().strip(".").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded == new_name[2]:
                    assert True
                    print("Configured Pool 1 responded with server %s for the queries" % Server_That_Responded)
                else:
                    print("Configured Pool 1 did not respond with server %s for the queries" % Server_That_Responded)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 256 Execution Completed")


        @pytest.mark.run(order=257)
        def test_257_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip().strip(".").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded == new_name[2]:
                    assert True
                    print("Configured Pool 1 responded with server %s for the queries" % Server_That_Responded)
                else:
                    print("Configured Pool 1 did not respond with server %s for the queries" % Server_That_Responded)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 257 Execution Completed")


        @pytest.mark.run(order=258)
        def test_258_Add_the_default_destination_pool_to_topology_rule(self):
                logging.info("********** Adding default destination pool to the topology rule ************")
                logging.info("Getting the Pool name reference")
                Pool_name=["DTC_Sample_pool","DTC_Sample_pool_2"]
                Pool_ref = []
                for i in Pool_name:
                        response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name='+i)
                        response_servers = json.loads(response_servers)
                        print(response_servers)
                        ref = response_servers[0]['_ref']
                        Pool_ref.append(ref)
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=DTC_Sample_Topology_2')
                response1 = json.loads(response1)
                response1 = response1[0]['_ref']
                data = {"name": "DTC_Sample_Topology_2", "rules": [{"sources": [{"source_op": "IS","source_type": "SUBNET","source_value": "10.0.0.0/8"}], "dest_type": "POOL","destination_link": Pool_ref[0]}, {"sources":[], "dest_type": "POOL", "destination_link": Pool_ref[1]}]}
                response = ib_NIOS.wapi_request('PUT',object_type=response1, fields=json.dumps(data))
                print(response)
                assert re.search(r'dtc:topology', response)
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
                logging.info("Test Case 258 Execution Completed")


        @pytest.mark.run(order=259)
        def test_259_Enable_the_DTC_In_Grid_DNS_Properties(self):
                logging.info("********** Enable the DTC in Grid DNS Properties ************")
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
                logging.info("Test Case 259 Execution Completed")


        @pytest.mark.run(order=260)
        def test_260_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("************ Run the dig command with 5k queries on grid master *************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com in a +subnet=20.10.2.0/24 +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                Servers=[]
                for i in queries:
                    a = i.strip(" ").split(" ")[0]
                    b = i.strip().strip(".").split(" ")[1]
                    No_of_queries.append(int(a))
                    Servers.append(b)
                No_of_queries=list(filter(None, No_of_queries))
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      assert False
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                logging.info("*********** Validating how many queries each pool received***********")
                for i in Servers:
                     if (No_of_queries[0] < int(2600)) and (i == new_name[0]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[0], i))
                     elif (No_of_queries[1] < int(2600)) and (i == new_name[1]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[1], i))
                     else:
                         print("Validation failed for topology method, since pool 2 servers didn't respond to the query")
                         assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 260 Execution Completed")

       
        @pytest.mark.run(order=261)
        def test_261_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("************ Run the dig command with 5k queries on grid member 1 *************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com in a +subnet=20.10.2.0/24 +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                Servers=[]
                for i in queries:
                    a = i.strip(" ").split(" ")[0]
                    b = i.strip().strip(".").split(" ")[1]
                    No_of_queries.append(int(a))
                    Servers.append(b)
                No_of_queries=list(filter(None, No_of_queries))
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      assert False
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                logging.info("*********** Validating how many queries each pool received***********")
                for i in Servers:
                     if (No_of_queries[0] < int(2600)) and (i == new_name[0]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[0], i))
                     elif (No_of_queries[1] < int(2600)) and (i == new_name[1]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[1], i))
                     else:
                         print("Validation failed for topology method, since pool 2 servers didn't respond to the query")
                         assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 261 Execution Completed")


        @pytest.mark.run(order=262)
        def test_262_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("************ Run the dig command with 5k queries on grid member 2 *************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com in a +subnet=20.10.2.0/24 +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                queries=list(filter(None, queries))
                No_of_queries=[]
                Servers=[]
                for i in queries:
                    a = i.strip(" ").split(" ")[0]
                    b = i.strip().strip(".").split(" ")[1]
                    No_of_queries.append(int(a))
                    Servers.append(b)
                No_of_queries=list(filter(None, No_of_queries))
                Sum_of_queries=sum(No_of_queries)
                print(Sum_of_queries)
                if Sum_of_queries == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % Sum_of_queries)
                else:
                      assert False
                      print("Total number of queries dosen't match %s " % Sum_of_queries)
                logging.info("*********** Validating how many queries each pool received***********")
                for i in Servers:
                     if (No_of_queries[0] < int(2600)) and (i == new_name[0]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[0], i))
                     elif (No_of_queries[1] < int(2600)) and (i == new_name[1]):
                         assert True
                         print("Pool 2 responded to %s queries using the server %s" % (No_of_queries[1], i))
                     else:
                         print("Validation failed for topology method, since pool 2 servers didn't respond to the query")
                         assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 262 Execution Completed")

        @pytest.mark.run(order=263)
        def test_263_Remove_the_default_destination_pool_in_topology_rule_2_and_modify_the_source_op_to_IS_NOT(self):
                logging.info("********** Remove the default destination pool in topology rule 2 and modify the source op to IS NOT ************")
                logging.info("Getting the Pool name reference")
                Pool_name=["DTC_Sample_pool","DTC_Sample_pool_2"]
                Pool_ref = []
                for i in Pool_name:
                        response_servers = ib_NIOS.wapi_request('GET',object_type='dtc:pool', params='?name='+i)
                        response_servers = json.loads(response_servers)
                        print(response_servers)
                        ref = response_servers[0]['_ref']
                        Pool_ref.append(ref)
                response1 = ib_NIOS.wapi_request('GET',object_type='dtc:topology', params='?name=DTC_Sample_Topology_2')
                response1 = json.loads(response1)
                response1 = response1[0]['_ref']
                data = {"name": "DTC_Sample_Topology_2", "rules": [{"sources": [{"source_op": "IS_NOT","source_type": "SUBNET","source_value": "10.0.0.0/8"}], "dest_type": "POOL","destination_link": Pool_ref[0]}]}
                response = ib_NIOS.wapi_request('PUT',object_type=response1, fields=json.dumps(data))
                print(response)
                assert re.search(r'dtc:topology', response)
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
                logging.info("Test Case 263 Execution Completed")


        @pytest.mark.run(order=264)
        def test_264_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com in a +subnet=20.10.2.0/24 +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip().strip(".").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded == new_name[2]:
                    assert True
                    print("Configured Pool 1 responded with server %s for the queries" % Server_That_Responded)
                else:
                    print("Configured Pool 1 did not respond with server %s for the queries" % Server_That_Responded)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 264 Execution Completed")


        @pytest.mark.run(order=265)
        def test_265_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com in a +subnet=20.10.2.0/24 +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip().strip(".").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded == new_name[2]:
                    assert True
                    print("Configured Pool 1 responded with server %s for the queries" % Server_That_Responded)
                else:
                    print("Configured Pool 1 did not respond with server %s for the queries" % Server_That_Responded)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 265 Execution Completed")



        @pytest.mark.run(order=266)
        def test_266_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output_master = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com in a +subnet=20.10.2.0/24 +short; done >DTC_26_1.log").read()
                output1_master = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                queries = output1_master.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip().strip(".").split(" ")[1]
                logging.info("********** Validation of number of queries *********")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded)
                    assert False
                logging.info("********** Validation of server that responded *********")
                if Server_That_Responded == new_name[2]:
                    assert True
                    print("Configured Pool 1 responded with server %s for the queries" % Server_That_Responded)
                else:
                    print("Configured Pool 1 did not respond with server %s for the queries" % Server_That_Responded)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 266 Execution Completed")


        @pytest.mark.run(order=267)
        def test_267_Disable_the_DTC_In_Grid_DNS_Properties(self):
                logging.info("********** Enable the DTC in Grid DNS Properties ************")
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
                logging.info("Test Case 267 Execution Completed")


        @pytest.mark.run(order=268)
        def test_268_Modify_the_lb_method_of_LBDN_to_Round_Robin(self):
                logging.info("********* Modify the lb preferred method to Round Robin *********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=DTC_LBDN')
                response = json.loads(response)
                ref_lbdn = response[0]['_ref']
                data = {"lb_method": "ROUND_ROBIN"}
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
                logging.info("Test Case 268 Execution Completed")



        @pytest.mark.run(order=269)
        def test_269_Validation_of_the_lb_method_of_LBDN_to_Round_Robin(self):
                logging.info("********** Getting the ref of LBDN ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=DTC_LBDN')
                response = json.loads(response)
                ref_lbdn = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref_lbdn, params='?_return_fields=lb_method')
                response1 = json.loads(response1)
                res_lb_method = response1['lb_method']
                if res_lb_method == "ROUND_ROBIN":
                    assert True
                    print("Modified changes to %s are reflecting" % res_lb_method)
                else:
                    print("Modified changes to %s are NOT reflecting" % res_lb_method)
                    assert False
                logging.info("Test Case 269 Execution Completed")



        @pytest.mark.run(order=270)
        def test_270_Modify_the_lb_method_of_LBDN_to_SOURCE_IP_HASH(self):
                logging.info("********* Modify the lb preferred method of LBDN to Source ip hash  *********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=DTC_LBDN')
                response = json.loads(response)
                ref_lbdn = response[0]['_ref']
                data = {"lb_method": "SOURCE_IP_HASH"}
                print(data)
                response = ib_NIOS.wapi_request('PUT',object_type=ref_lbdn, fields=json.dumps(data))
                response = json.loads(response)
                logging.info("Validation of lbdn creation")
                assert re.search(r'dtc:lbdn', response)
                logging.info("********* Modify the lb preferred method of pool to Source ip hash  *********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool')
                response = json.loads(response)
                pool_ref=[]
                for i in response:
                    i = i['_ref']
                    pool_ref.append(i)
                print(pool_ref)
                for i in pool_ref:
                    data = {"lb_preferred_method": "SOURCE_IP_HASH"}
                    print(data)
                    response2 = ib_NIOS.wapi_request('PUT', object_type=i, fields=json.dumps(data))
                    response2 = json.loads(response2)
                    assert re.search(r'dtc:pool', response2)
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
                logging.info("Test Case 270 Execution Completed")


        @pytest.mark.run(order=271)
        def test_271_Validation_of_the_lb_method_of_LBDN_to_Source_IP_Hash_and_auto_consolidated_monitors(self):
                logging.info("********** Getting the ref of LBDN ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=DTC_LBDN')
                response = json.loads(response)
                ref_lbdn = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref_lbdn, params='?_return_fields=lb_method')
                response1 = json.loads(response1)
                res_lb_method = response1['lb_method']
                logging.info("Validation of LB method")
                if res_lb_method == "SOURCE_IP_HASH":
                    assert True
                    print("Modified changes to %s are reflecting" % res_lb_method)
                else:
                    print("Modified changes to %s are NOT reflecting" % res_lb_method)
                    assert False
                logging.info("Validation of lb method in pools")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool')
                response = json.loads(response)
                pool_ref=[]
                for i in response:
                    i = i['_ref']
                    pool_ref.append(i)
                for i in pool_ref:
                    response2 = ib_NIOS.wapi_request('GET',object_type=i, params='?_return_fields=lb_preferred_method')
                    response2 = json.loads(response2)
                    res = response2['lb_preferred_method']
                    if res == "SOURCE_IP_HASH":
                        assert True
                        print("Modified changes to %s are reflecting" % res_lb_method)
                    else:
                        print("Modified changes to %s are NOT reflecting" % res_lb_method)
                        assert False
                logging.info("Test Case 271 Execution Completed")



        @pytest.mark.run(order=272)
        def test_272_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("************ Run the dig command with 5k queries on grid master *************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip().strip(".").split(" ")[1]
                if int(No_of_queries) == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % No_of_queries)
                else:
                      assert False
                      print("Total number of queries dosen't match %s " % No_of_queries)
                logging.info("*********** Validating which server reeceived the query ***********")
                if Server_That_Responded in new_name[:4]:
                    print("Server "+Server_That_Responded+" responded to the query")
                    assert True
                else:
                    print("Different "+Server_That_Responded+" responded to the query")
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 272 Execution Completed")


        @pytest.mark.run(order=273)
        def test_273_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("************ Run the dig command with 5k queries on grid member1 *************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                Server_That_Responded=queries[0].strip().strip(".").split(" ")[1]
                if int(No_of_queries) == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % No_of_queries)
                else:
                      assert False
                      print("Total number of queries dosen't match %s " % No_of_queries)
                logging.info("*********** Validating which server reeceived the query ***********")
                if Server_That_Responded in new_name[:4]:
                    print("Server "+Server_That_Responded+" responded to the query")
                    assert True
                else:
                    print("Different "+Server_That_Responded+" responded to the query")
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 273 Execution Completed")


        @pytest.mark.run(order=274)
        def test_274_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("************ Run the dig command with 5k queries on grid member2 *************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                new_name=Server_Domain_name[:20]
                total_expected_queries=int(5000)
                logging.info("Validating total no of queries")
                queries = output1.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                global Server_That_Responded_First
                Server_That_Responded_First = queries[0].strip().strip(".").split(" ")[1]
                if int(No_of_queries) == total_expected_queries:
                      assert True
                      print("Total number of queries from all the servers are %s " % No_of_queries)
                else:
                      assert False
                      print("Total number of queries dosen't match %s " % No_of_queries)
                logging.info("*********** Validating which server reeceived the query ***********")
                if Server_That_Responded_First in new_name[:4]:
                    print("Server "+Server_That_Responded_First+" responded to the query")
                    assert True
                else:
                    print("Different "+Server_That_Responded_First+" responded to the query")
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 274 Execution Completed")


        @pytest.mark.run(order=275)
        def test_275_Drop_the_responded_server_from_the_grid_master(self):
                logging.info("********** Drop the responded server from the grid master ************")
                global Server_That_Responded_First
                print("Dropping the server %s on master grid" % Server_That_Responded_First)
                drop_server = "iptables -I INPUT -s "+Server_That_Responded_First+" -j DROP"
                #print(drop_server)
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_master_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline(drop_server)
                child.expect('#')
                child.close()
                sleep(60)
                logging.info("Test Case 275 Execution Completed")


        @pytest.mark.run(order=276)
        def test_276_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                print(output1)
                queries = output1.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                global Server_That_Responded_First
                Server_That_Responded_After_Drop=queries[0].strip().strip(".").split(" ")[1]
                print("Server that responded before after "+Server_That_Responded_After_Drop)
                logging.info("********** Validation of servers whether different server responded since the server responded last is down in grid master ************")
                if Server_That_Responded_First != Server_That_Responded_After_Drop:
                    assert True
                    print("Server %s Responded to query since first responded server is down on grid master" % Server_That_Responded_After_Drop)
                else:
                    print("Server %s didn't drop on the master grid hence getting query on the same" % Server_That_Responded_First)
                    assert False
                logging.info("Validation of number of count of queries")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded_After_Drop)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded_After_Drop)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 276 Execution Completed")


        @pytest.mark.run(order=277)
        def test_277_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                print(output1)
                queries = output1.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                global Server_That_Responded_First
                Server_That_Responded_After_Drop=queries[0].strip().strip(".").split(" ")[1]
                print("Server that responded before after "+Server_That_Responded_After_Drop)
                logging.info("********** Validation of servers whether different server responded since the server responded last is down in grid master ************")
                if Server_That_Responded_First == Server_That_Responded_After_Drop:
                    assert True
                    print("Server %s Responded to query" % Server_That_Responded_After_Drop)
                else:
                    print("Server %s didn't respond to the query" % Server_That_Responded_First)
                    assert False
                logging.info("Validation of number of count of queries")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded_After_Drop)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded_After_Drop)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 277 Execution Completed")


        @pytest.mark.run(order=278)
        def test_278_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                print(output1)
                queries = output1.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                global Server_That_Responded_First
                Server_That_Responded_After_Drop=queries[0].strip().strip(".").split(" ")[1]
                print("Server that responded before after "+Server_That_Responded_After_Drop)
                logging.info("********** Validation of servers whether different server responded since the server responded last is down in grid master ************")
                if Server_That_Responded_First == Server_That_Responded_After_Drop:
                    assert True
                    print("Server %s Responded to query" % Server_That_Responded_After_Drop)
                else:
                    print("Server %s didn't respond to the query" % Server_That_Responded_First)
                    assert False
                logging.info("Validation of number of count of queries")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded_After_Drop)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded_After_Drop)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 278 Execution Completed")



        @pytest.mark.run(order=279)
        def test_279_ENABLE_AUTO_CONSOLIDATED_MONITORS_in_LBDN(self):
                logging.info("********* Enable Auto consolidated montiors in LBDN *********")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=DTC_LBDN')
                response = json.loads(response)
                ref_lbdn = response[0]['_ref']
                data = {"auto_consolidated_monitors": True}
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
                logging.info("Test Case 279 Execution Completed")


        @pytest.mark.run(order=280)
        def test_280_Validation_of_the_lb_method_of_LBDN_to_Source_IP_Hash_and_auto_consolidated_monitors(self):
                logging.info("********** Getting the ref of LBDN ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:lbdn', params='?name=DTC_LBDN')
                response = json.loads(response)
                ref_lbdn = response[0]['_ref']
                response1 = ib_NIOS.wapi_request('GET',object_type=ref_lbdn, params='?_return_fields=auto_consolidated_monitors')
                response1 = json.loads(response1)
                res_lb_method = response1['auto_consolidated_monitors']
                logging.info("Validation of LB method")
                if res_lb_method == True:
                    assert True
                    print("Modified changes to %s are reflecting" % res_lb_method)
                else:
                    print("Modified changes to %s are NOT reflecting" % res_lb_method)
                    assert False
                logging.info("Validation of auto consolidated monitors")
                response2 = ib_NIOS.wapi_request('GET',object_type=ref_lbdn, params='?_return_fields=auto_consolidated_monitors')
                response2 = json.loads(response2)
                res = response2['auto_consolidated_monitors']
                if res == True:
                    print("Auto consolidated monitors is enbaled")
                    assert True
                else:
                    print("Auto consolidated monitors is Disabled")
                    assert False
                logging.info("Test Case 280 Execution Completed")


        @pytest.mark.run(order=281)
        def test_281_Run_the_dig_command_with_5k_queries_on_grid_master(self):
                logging.info("********** Run the dig command with 5k queries on grid master ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_master_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                print(output1)
                queries = output1.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                global Server_That_Responded_First
                Server_That_Responded_After_Drop=queries[0].strip().strip(".").split(" ")[1]
                print("Server that responded before after "+Server_That_Responded_After_Drop)
                logging.info("********** Validation of servers whether different server responded since the server responded last is down in grid master ************")
                if Server_That_Responded_First != Server_That_Responded_After_Drop:
                    assert True
                    print("Server %s Responded to query" % Server_That_Responded_After_Drop)
                else:
                    print("Server %s didn't respond to the query" % Server_That_Responded_First)
                    assert False
                logging.info("Validation of number of count of queries")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded_After_Drop)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded_After_Drop)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 281 Execution Completed")


        @pytest.mark.run(order=282)
        def test_282_Run_the_dig_command_with_5k_queries_on_grid_member_1(self):
                logging.info("********** Run the dig command with 5k queries on grid member 1 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member1_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                print(output1)
                queries = output1.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                global Server_That_Responded_First
                Server_That_Responded_After_Drop=queries[0].strip().strip(".").split(" ")[1]
                print("Server that responded before after "+Server_That_Responded_After_Drop)
                logging.info("********** Validation of servers whether different server responded since the server responded last is down in grid master ************")
                if Server_That_Responded_First != Server_That_Responded_After_Drop:
                    assert True
                    print("Server %s Responded to query" % Server_That_Responded_After_Drop)
                else:
                    print("Server %s didn't respond to the query" % Server_That_Responded_First)
                    assert False
                logging.info("Validation of number of count of queries")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded_After_Drop)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded_After_Drop)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 282 Execution Completed")


        @pytest.mark.run(order=283)
        def test_283_Run_the_dig_command_with_5k_queries_on_grid_member_2(self):
                logging.info("********** Run the dig command with 5k queries on grid member 2 ************")
                output = os.popen("for i in {1..5000}; do dig @"+config.grid_member2_vip+" a.dtc.com +short; done >DTC_26_1.log").read()
                output1 = os.popen("grep -v PST DTC_26_1.log | sort | uniq -dc").read()
                print(output1)
                queries = output1.split("\n")
                No_of_queries=queries[0].strip(" ").split(" ")[0]
                global Server_That_Responded_First
                Server_That_Responded_After_Drop=queries[0].strip().strip(".").split(" ")[1]
                print("Server that responded before after "+Server_That_Responded_After_Drop)
                logging.info("********** Validation of servers whether different server responded since the server responded last is down in grid master ************")
                if Server_That_Responded_First != Server_That_Responded_After_Drop:
                    assert True
                    print("Server %s Responded to query" % Server_That_Responded_After_Drop)
                else:
                    print("Server %s didn't respond to the query" % Server_That_Responded_First)
                    assert False
                logging.info("Validation of number of count of queries")
                if No_of_queries == "5000":
                    assert True
                    print("Expected number of queries are seen on %s" % Server_That_Responded_After_Drop)
                else:
                    print("Expected number of queries are not seen on %s" % Server_That_Responded_After_Drop)
                    assert False
                os.system('rm DTC_26_1.log')
                logging.info("Test Case 283 Execution Completed")


        @pytest.mark.run(order=284)
        def test_284_Try_Disbaling_the_auto_consolidated_monitors_in_pool_and_expect_error(self):
                logging.info("********** Try Disbaling the auto consolidated monitors in pool and expect error ************")
                response = ib_NIOS.wapi_request('GET',object_type='dtc:pool')
                response = json.loads(response)
                pool_ref=[]
                for i in response:
                    i = i['_ref']
                    pool_ref.append(i)
                for i in pool_ref:
                    data = {"auto_consolidated_monitors": False}
                    response2 = ib_NIOS.wapi_request('PUT',object_type=i, fields=json.dumps(data))
                    print(response2)
                    expected_error = "Cannot manually disable the Auto Consolidated Monitor option on the DTC pool \'"+i.split(":")[-1]+"\' because it inherited from linked LBDN \'DTC_LBDN\'"
                    if type(response2) == tuple:
                        if expected_error in response2[1]:
                            print("Expected Error "+expected_error+"seen")
                            assert True
                        else:
                            assert False
                            print("Expected Error "+expected_error+"is not seen")
                logging.info("Test Case 284 Execution Completed")


        @pytest.mark.run(order=285)
        def test_285_Check_if_any_cores_generated_in_master_and_member(self):
                logging.info("********** Check if any cores generated in master and members ************")
                ip = [config.grid_master_vip, config.grid_member1_vip, config.grid_member2_vip]
                for i in ip:
                    print("Logging in to device "+i)
                    dir_path = 'cd /storage/cores/'
                    client = paramiko.SSHClient()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
                    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
                    client.connect(i, username='root', pkey = mykey)
                    stdin, stdout, stderr = client.exec_command('ls /storage/cores/ | wc -l')
                    output = stdout.read()
                    output = output.split("\n")
                    if output[0] == "0":
                        assert True
                        print("There are no cores files generated")
                    else:
                        print("Core files are generated while running the performance cases")
                        assert False
                    print("Logging out of device "+i)
                logging.info("Test Case 285 Execution Completed")
